# TLDM/Cresnet managed-side harvest - report

## SUMMARY (lead with the architectural conclusion)

**The managed decompile does NOT contain the chassis TCP handshake, and
TLDMInterfaceDLL.dll is NOT the binary that owns the TCP socket.**

Evidence:

1. Across all decompiled/*.cs files, the ONLY DllImport targeting
   TLDMInterfaceDLL.dll is a single nullary sync-primitive at
   SimplSharpPro_exe.cs:176006:

       DllImport("TLDMInterfaceDLL.dll")
       public static extern bool SendSyncOnCresnetMessageToTLDM();

2. All approximately 30 other call sites touch native code through a wrapper class
   TLDMManagedToNativeInterface whose methods include SendMessageToTLDM,
   SendMessageToTLDMEx, ReceiveMessageFromTLDM, SendTLDMAppInitDoneToTLDM,
   SendTLDMAppUnInitDoneToTLDM, SendTLDMAppUnRegisterMessage,
   ExitTLDMAppReceiveThread, SetMaxExLenMessageSize,
   SendAppSuspendedMessageToTLDM, SendAppResumedMessageToTLDM. That class
   is REFERENCED everywhere but DEFINED NOWHERE in decompiled/*.cs. It
   lives in another Crestron assembly not in this tree.

3. There is no `new TcpClient`, `new Socket(AddressFamily...)`,
   `BeginConnect`, or `new IPEndPoint` with port 41794 anywhere in the
   managed decompile. SimplSharpPro.exe never opens a TCP socket itself.

4. The packet structs flowing through the TLDM interface are explicitly
   named TLDM_FROM_APP_EO4S_IPC_* - "EO4S IPC", i.e., inter-process
   communication to a local daemon, NOT on-wire frames. The 1044-byte
   cresnetPacket byte array inside is the actual Cresnet payload; the
   16-byte EO4S IPC header around it (length, type, fromRoomHash,
   toRoomHash) is only for app-to-daemon routing.

**Interpretation**: on Crestron Linux_CS, SimplSharpPro.exe talks to a
local TLDM daemon over IPC. The daemon owns the TCP socket to the
chassis / network. The handshake we need (master registering with
chassis on port 41794) is implemented IN THE TLDM DAEMON, which is a
separate native binary not in this decompile.

**Impact on the spike plan**: ripping TLDMInterfaceDLL.dll apart in
Ghidra is unlikely to produce the handshake bytes - it will show us how
the shim marshals IPC packet structs to a daemon, not how the daemon
negotiates with the chassis. Reconsider plan options:

- **Option A (easier)**: get the TLDM daemon binary from a real Crestron
  3-series or 4-series processor (look for files named something like
  tldm, tldmd, csomn, or similar under /usr/bin / /opt), and
  disassemble THAT.
- **Option B (easier still)**: boot SimplSharpPro.exe under Mono on a
  Linux VM pointed at the chassis, with tcpdump capturing port 41794.
  The handshake is observed live rather than reconstructed from assembly.
  Note: on Crestron hardware the daemon is a separate process; running
  SimplSharpPro.exe standalone on a non-Crestron Linux is likely to
  immediately fail because TLDMInterfaceDLL.dll will try to open an IPC
  endpoint to a daemon that is not running. Needs a stub daemon or a
  Crestron processor image.
- **Option C (hard)**: full RE of the daemon binary once obtained.

### Secondary findings (useful either way)

- The managed side knows exactly WHICH packet types flow. The IPC
  header deviceSendPacketMessageType takes values 9, 17, 28, 30, 36,
  41, 43, 44, 46, and more. REGISTER type is 28; UNREGISTER is 30;
  43 and 41 are EXTENDED_LENGTH_CRESNET and short CRESNET packet
  dispatches; 44 is startup; 46 is remove-rooms; 9 and 17 are
  Ethernet/Cresnet normal-send variants.
- The IPC packet struct carries deviceParentType which takes values
  from eTLDMDeviceParentType enum:
     1 = DEVICE_PARENT_TOP_LEVEL_SLOT
     2 = DEVICE_PARENT_CRESNET_TYPE
     3 = DEVICE_PARENT_ETHERNET_TYPE
     4 = DEVICE_PARENT_GATEWAY_TYPE
     5 = DEVICE_PARENT_ANY  (debug)
     6 = DEVICE_PARENT_TYPE_UNKNOWN
- TLDM_SEND_MSG_TYPE_* codes (from doc comments only):
     0 = NORMAL_INIT
     1 = UPDATE_INIT
     2 = NORMAL_SEND
     3 = FORCE_SEND
     + SEND_TO_MYSELF (value unknown; sends to internal queue, not TLDM)
- The receive thread (TLDMRcvThreadFunction, approx :179877) blocks on
  ReceiveMessageFromTLDM(array, maxSize, out length, out type) and
  dispatches by type. No TCP recv call anywhere.

### Concrete unknowns that only the DAEMON can tell us

1. The TCP connect sequence to chassis:41794.
2. The first master-sent frame (opcode/length/body) - the "I am a
   proprietary device peer" announcement.
3. The chassis register-ACK frame layout and the field the master uses
   to confirm success.
4. The heartbeat cadence and payload (L4 keepalive).
5. The on-wire framing - is there a session MAC / crypto layer? (unlikely
   given earlier IPID-1 masquerade with no crypto worked, but confirm).

None of these are visible in the decompile. They all live in the
TLDM daemon.

## FULL EXTRACTS

### 1. The ONLY TLDMInterfaceDLL.dll [DllImport]

File: SimplSharpPro_exe.cs lines 176006-176007 (inside class
SimplSharpProManager):

    [DllImport("TLDMInterfaceDLL.dll")]
    public static extern bool SendSyncOnCresnetMessageToTLDM();

Nullary, bool return, no CharSet, no CallingConvention. It is a sync
primitive, not a packet send. The actual send paths go through
TLDMManagedToNativeInterface.* methods, which are declared in a
separate Crestron assembly.

### 2. Complete list of [DllImport] attributes in decompiled/

- ProgrammingInterfaces.cs:321:
  [DllImport("AppWatchdogInterfaceDLL.dll", EntryPoint = "AppWatchdogRegisterAuxiliaryProcess")]
  private static extern uint b(uint, uint);
- ProgrammingInterfaces.cs:324:
  [DllImport("AppWatchdogInterfaceDLL.dll", EntryPoint = "AppWatchdogUnRegisterAuxiliaryProcess")]
  private static extern uint a(uint, uint);
- InternalFunctions.cs:3299:
  [DllImport("libProductNameUtil.so")]
  private static extern bool GetDeviceInfo(ref uint, ref uint);
- InternalFunctions.cs:4285:
  [DllImport("JsonDb")]
  private static extern int JsonDbSetConnection(IntPtr, int);
- SimplSharpPro_exe.cs:164903:
  [DllImport("libUtilities.so")]
  private static extern uint CalcCRC32FromWStringUsingLower(IntPtr);
- SimplSharpPro_exe.cs:176006:
  TLDMInterfaceDLL.dll (above).

Mixed .dll / .so names tell us this build runs on Linux_CS with the
runtime loader mapping both suffixes.

### 3. TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT (the register struct)

File: SimplSharpPro_exe.cs:167437-167793 (internal struct, no explicit
[StructLayout] - so sequential, pack=default).

Field order (as laid out in managed memory, which marshals 1:1 to native):

    uint   singleDeviceRegisterMessageLength
    uint   singleDeviceRegisterMessageType          # e.g. 28 for register
    uint   singleDeviceOrSlotId
    uint   singleDeviceSymbolCode
    eTLDMDeviceParentType  singleDeviceParentType   # (4 = GATEWAY)
    uint   singleDeviceRegistrationFlags
    uint   singleDeviceTypeForPlugInSlots
    TLDM_DEVICE_REG_PARAM_TYPE_ENUM  singleDeviceRegParamType
    fixed uint  singleDeviceRegSpecificData[8]
    fixed byte  singleDeviceRegIPAddressForEthernetDevices[200]
    fixed byte  singleDeviceRegDeviceFriendlyName[100]
    fixed byte  singleDeviceRegDeviceProductName[100]

Total size: 8*4 (header) + 8*4 (specific data) + 200 + 100 + 100 = 464 bytes.

Concrete populated instance (SimplSharpPro_exe.cs:10868,
SendDeviceRegisterUnregisterForRFDevices):

    singleDeviceRegisterMessageType = 28u          # register opcode
    singleDeviceRegisterMessageLength = 64u        # ONLY 64, not 464
    singleDeviceOrSlotId = CrestronControlSystem.RFSlot
    singleDeviceSymbolCode = 0u
    singleDeviceRegParamType = (TLDM_DEVICE_REG_PARAM_TYPE_ENUM)1
    singleDeviceParentType = DEVICE_PARENT_GATEWAY_TYPE  (= 4)
    *singleDeviceRegSpecificData = IDToRegisterUnregister   # first uint
    singleDeviceRegistrationFlags = 2u

Note the 64-byte Length: only header + 8*4 specific-data = 64 bytes get
sent; the IP/name buffers populated only for ethernet-device registrations.

### 4. TLDM_SINGLE_DEVICE_UNREGISTER_MESSAGE_STRUCT

File: SimplSharpPro_exe.cs:168109-168375:

    uint   singleDeviceUnRegisterMessageLength
    uint   singleDeviceUnRegisterMessageType         # e.g. 30
    uint   singleDeviceOrSlotId
    eTLDMDeviceParentType  singleDeviceParentType
    TLDM_DEVICE_REG_PARAM_TYPE_ENUM  singleDeviceUnRegisterParmType
    uint   singleDevicePortIdToUnreg

Concrete usage (:10843): length=24u, type=30u, parent=GATEWAY,
regParamType=(enum)6, portId=IDToRegisterUnregister. 24 bytes = 6*4.

### 5. TLDM_SINGLE_DEVICE_REGISTER_RESPONSE_MESSAGE_STRUCT

File: SimplSharpPro_exe.cs:167797-168105:

    uint   _singleDeviceRegisterResponseMessageLength
    uint   _singleDeviceRegisterResponseMessageType
    uint   _singleDeviceOrSlotId
    eTLDMDeviceParentType  _singleDeviceParentType
    TLDM_RESPONSE_STATUS_ENUM  _singleDeviceRegisterResponse
    TLDM_DEVICE_REG_PARAM_TYPE_ENUM  _singleDeviceRegParamType
    uint   _singleDeviceRegSpecificData

7 fields of 4 bytes each = 28 bytes.

### 6. The IPC packet structs (app to TLDM daemon)

File: SimplSharpPro_exe.cs:15107-15145

    internal static class TLDM_INTERFACE_Constants_EX {
      public const int TLDM_FROM_APP_EO4S_IPC_STARTUP_STRUCT_HEADER_LENGTH = 12;
      public const int TLDM_FROM_APP_EO4S_IPC_PACKET_STRUCT_HEADER_LENGTH = 16;
    }

    internal struct TLDM_FROM_APP_EO4S_IPC_PACKET_STRUCT {
      public uint deviceSendPacketMessageLength;
      public uint deviceSendPacketMessageType;
      public uint roomNameFromHash;
      public uint roomNameToHash;
      [MarshalAs(UnmanagedType.ByValArray, SizeConst = 1044)]
      public unsafe fixed byte cresnetPacket[1044];
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    internal struct TLDM_FROM_APP_EO4S_IPC_STARTUP_STRUCT {
      public uint deviceSendPacketMessageLength;
      public uint deviceSendPacketMessageType;
      public uint roomNameHash;
      [MarshalAs(UnmanagedType.ByValArray, SizeConst = 1)]
      public unsafe fixed uint roomNameHashList[1];
    }

The 1044-byte cresnetPacket byte array is where the actual
on-wire Cresnet payload goes (finding 12 L3 bytes). The 16 bytes
around it are app-to-daemon IPC routing, invisible on the wire.

### 7. Message-type literals observed

- 9  : used widely as deviceSendPacketMessageType on CRESNET packets
       (:109694, :115962, :116176, :229307, :229642) - "normal send"
- 17 : used on EXTENDED_LENGTH_CRESNET packets (:116728, :116954,
       :229184, :229538) - "normal extended send"
- 28 : REGISTER (:10870, :79172)
- 30 : UNREGISTER (:10846, :81962)
- 36 : used widely as deviceSendPacketMessageType on CRESNET packets -
       likely update-send variant (:115949, :115979, :116163, :116193, :116474)
- 41 : BuildAndSendIPCPacket default type for TLDM_FROM_APP_CRESNET_PACKET_STRUCT
       (:117179) - short Cresnet IPC packet
- 43 : BuildAndSendLongIPCPacket type for extended-length (:117142) -
       long Cresnet IPC packet
- 44 : BuildAndSendIPCStartupPacket (:117097) - startup
- 46 : BuildAndSendIPCRemoveRoomsPacket (:117071) - remove rooms

### 8. The caller sites of SendMessageToTLDM / SendMessageToTLDMEx

All in SimplSharpPro_exe.cs. Representative:

- :10890 SendMessageToTLDM (register, nullary bool) - followed by
  controlSystem.WaitForTldmResponse(timeout) which blocks for a
  response (:10921). This is the sync register path.
- :10903 SendMessageToTLDM (unregister).
- :78978 SendMessageToTLDM - ethernet device register.
- :109620, :109633, :109664 SendMessageToTLDMEx (ExtendedLen) for
  rack initialization finished - the deviceParentType is set
  successively to GATEWAY (4), CRESNET (2), ETHERNET (3) and
  TOP_LEVEL_SLOT (1); the master finished-rack-init message is sent
  across each transport (BuildAndSendFinishedWithRackInitialization at :109605).

The pattern: managed code allocates a struct ON THE STACK, populates
fields, takes a struct pointer as IntPtr, and calls the native wrapper
with that pointer plus the struct MessageLength field. The native layer
copies those bytes into whatever IPC transport (Unix socket, shared
memory, named pipe) talks to the TLDM daemon.

### 9. The TLDM receive thread

Function TLDMRcvThreadFunction (approx line 179877). Allocates a
byte[iMaxSystemMessageSize] buffer and loops on:

    flag2 = TLDMManagedToNativeInterface.ReceiveMessageFromTLDM(
      array, iMaxSystemMessageSize, ref msgLength, ref msgType);

Then dispatches by msgType through a huge switch. Case 80 logs
"APP{nn} received {type} msg from TLDM on {localTime}" (:179787),
confirming each inbound message carries a type field matching the
outbound opcode space.

Heartbeat: no explicit timer named heartbeat / keepalive in managed
code. If a periodic frame flows app to TLDM daemon it is driven by the
daemon own timer; the managed app only wraps request/response pairs.
If a periodic frame flows daemon to chassis on the wire, it is 100% in
the daemon native code and not visible from here.

### 10. Explicit TCP code paths in managed code

None. Zero new-TcpClient, zero new-Socket, zero new-IPEndPoint with any
Cresnet port in SimplSharpPro.exe. The only chassis-port-related
artifacts are projector-side XML doc comments in CrestronConnected.cs
(:17526, :25572) describing server-side listen, not client connect.

## Spike plan - concrete recommendation

Given the architectural reality (daemon owns the socket), the fastest
path forward is to AVOID the DLL disassembly spike entirely and instead:

1. Procure a Crestron processor binary image (3-series or 4-series
   firmware tarball, or an actual device filesystem dump). Extract the
   TLDM daemon binary. OR
2. Spin up SimplSharpPro.exe under Mono on a Linux VM targeting
   chassis 192.168.6.14, with tcpdump capturing port 41794. Likely
   blocked by missing daemon dependency on non-Crestron Linux. OR
3. If a real Crestron master processor is ever on the LAN with the
   chassis for any reason, mirror its port and pcap for the few seconds
   it takes to establish a session.

In any case: the DLL disassembly spike as originally scoped against
TLDMInterfaceDLL.dll is pointed at the wrong binary. The handshake
lives in the TLDM daemon.
