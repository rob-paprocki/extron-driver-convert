# 18 - DLL spike pivot: handshake lives in a separate TLDM daemon

## TL;DR

The native binary we assumed held the chassis TCP handshake is NOT the
one that owns the socket. `TLDMInterfaceDLL.dll` turns out to be a thin
IPC shim; the real speaker is a TLDM daemon that only exists on
Crestron 3/4-series processor firmware. The spike pivots to procuring a
processor firmware image and disassembling the daemon from it.

## How we got here

Rob reversed the earlier decision to defer the DLL spike (see finding
17 scope correction, commit `0205f42`) and asked to complete it. Plan
was to disassemble `TLDMInterfaceDLL.dll`, extract the master-side L1
registration handshake and L4 heartbeat, implement a Python prototype,
and validate against the chassis.

The orient-first harvest of the managed decompile at
`<session tmp>/decompiled/` (full report in
`evidence/18-tldm-managed-surface-harvest.md`, 317 lines) revealed a
fundamental problem with that plan.

## What the harvest found

**Only ONE DllImport in all the decompiled C# targets `TLDMInterfaceDLL.dll`**:

    [DllImport("TLDMInterfaceDLL.dll")]
    public static extern bool SendSyncOnCresnetMessageToTLDM();

That is nullary. Returns a bool. Not a packet send - a sync primitive.

The ~30 actual send/receive sites in the decompile go through a wrapper
class `TLDMManagedToNativeInterface` with methods like
`SendMessageToTLDM`, `SendMessageToTLDMEx`, `ReceiveMessageFromTLDM`,
`SendTLDMAppInitDoneToTLDM`. That class is REFERENCED everywhere but
DEFINED NOWHERE in the decompiled tree. It lives in a separate
Crestron assembly not in the dump.

**Zero TCP code in the managed layer.** No `new TcpClient`, no
`new Socket`, no `new IPEndPoint` with 41794 anywhere in
`SimplSharpPro_exe.cs` (560k lines). `SimplSharpPro.exe` never opens a
TCP socket itself.

**The IPC packet struct name is explicit**: `TLDM_FROM_APP_EO4S_IPC_*`.
"EO4S IPC" = inter-process communication to a local daemon, not an
on-wire framing. The 16-byte IPC header (length, type, fromRoomHash,
toRoomHash) carries app-to-daemon routing fields; the daemon strips
them before sending to the chassis.

## Architecture

    SimplSharpPro.exe (managed, Mono on Linux_CS)
       |
       | IPC via TLDMInterfaceDLL.dll (thin shim, 1 nullary DllImport)
       | and TLDMManagedToNativeInterface (external assembly wrapper)
       v
    TLDM daemon (native, Crestron processor only)
       |
       | TCP :41794
       v
    chassis (DM-MD / DMPS / etc.)

The DLL I was going to disassemble sits between managed and daemon, not
between daemon and wire. Reversing it would reveal IPC marshalling (how
the shim hands packet structs across an IPC transport - Unix socket,
shared memory, named pipe), NOT the chassis handshake.

## Secondary findings worth keeping

Even though the handshake itself is not visible in the decompile, the
managed layer DOES carry significant structural intel about what the
daemon will send on the wire (the Cresnet payload portion):

### Register message struct (TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT)

Field order:

    uint   singleDeviceRegisterMessageLength
    uint   singleDeviceRegisterMessageType          # 28 = REGISTER
    uint   singleDeviceOrSlotId
    uint   singleDeviceSymbolCode
    eTLDMDeviceParentType  singleDeviceParentType   # 4 = GATEWAY
    uint   singleDeviceRegistrationFlags
    uint   singleDeviceTypeForPlugInSlots
    TLDM_DEVICE_REG_PARAM_TYPE_ENUM  singleDeviceRegParamType
    fixed uint  singleDeviceRegSpecificData[8]
    fixed byte  singleDeviceRegIPAddressForEthernetDevices[200]
    fixed byte  singleDeviceRegDeviceFriendlyName[100]
    fixed byte  singleDeviceRegDeviceProductName[100]

Declared size 464 bytes. Observed used size on RF-slot register path:
**64 bytes** (header plus 8*4 specific-data). IP/name buffers only
populated for ethernet-device registrations.

### Response struct (28 bytes = 7 uint fields)

### Unregister struct (24 bytes = 6 uint fields, type=30)

### Parent-type enum values

    1 = DEVICE_PARENT_TOP_LEVEL_SLOT
    2 = DEVICE_PARENT_CRESNET_TYPE
    3 = DEVICE_PARENT_ETHERNET_TYPE
    4 = DEVICE_PARENT_GATEWAY_TYPE
    5 = DEVICE_PARENT_ANY (debug)
    6 = DEVICE_PARENT_TYPE_UNKNOWN

### IPC packet-type opcodes (deviceSendPacketMessageType)

    9  = NORMAL send (CRESNET)
    17 = NORMAL send (EXTENDED_LENGTH_CRESNET)
    28 = REGISTER
    30 = UNREGISTER
    36 = UPDATE_SEND (CRESNET variant)
    41 = BuildAndSendIPCPacket default (short Cresnet IPC)
    43 = BuildAndSendLongIPCPacket (long Cresnet IPC)
    44 = BuildAndSendIPCStartupPacket
    46 = BuildAndSendIPCRemoveRoomsPacket

### Cresnet payload buffer

The IPC struct carries a 1044-byte `cresnetPacket` byte array. This is
where finding 12 L3 bytes live. The daemon forwards those bytes
(plus daemon-level session framing) onto the wire.

## Explicit unknowns that only the daemon reveals

1. TCP connect sequence to chassis:41794 (session open, if any).
2. The master-sent register frame as it appears on the wire -
   on-wire framing, session MAC/crypto if any.
3. The chassis register-ACK frame as it appears on the wire.
4. The heartbeat cadence and payload.
5. Whether the on-wire register payload is literally the 64-byte
   `TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT`, or whether the daemon
   re-encodes it.

## Decision and next step

Chosen path: procure a Crestron 3-series or 4-series processor firmware
image, extract the TLDM daemon binary (expected under /usr/bin/,
/opt/, or similar), disassemble that in Ghidra.

Pipeline waiting on firmware delivery:

- firmware archive --> extract Linux_CS filesystem --> find daemon
  binary (search for strings "tldm", "cresnet", "41794", opcodes 28/30)
- Ghidra project with the daemon as primary + any dependency .so files
- Reverse the TCP connect, register-frame builder, register-ACK match,
  heartbeat timer
- Document byte-level spec in finding 19
- Python prototype of proprietary-peer master client (task #3)
- End-to-end validation via DM-RMC ComPort loopback (task #4)
- If positive: collapse unified driver to single socket (task #5)

## Artifacts

- `evidence/18-tldm-managed-surface-harvest.md` - the full 317-line
  harvest report (what the managed layer tells us, what it does not,
  struct byte layouts, caller sites, enum values). Preserved
  verbatim; this is the foundation of whatever comes next.
