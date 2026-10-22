# 12 — The DM endpoint CIP protocol, byte-level: Cresnet-over-IP with nested-container hierarchy addressing

**Produced:** 2026-10-11 by workflow `wf_99d07615-8cc` (6 parallel readers of the decompiled Crestron.SimplSharpPro.* assemblies -> adversarial verify -> single-writer synthesis). 1.2M subagent tokens, 4h 12m.
**Status:** research-grade. The byte-level packet shapes are from reading Crestron's own compiled C# (Dotfuscator-obfuscated but readable), the control-flow citations are file:line in C:/Users/<user>/.claude/jobs/50e4735d/tmp/decompiled/*.cs (ilspycmd outputs; not committed to this repo).
**Note:** Decompiled C# is Crestron copyrighted; the findings here document the protocol for interoperability research. Raw .cs files stay in jobs/tmp, not under version control.

---

# How SIMPL# Pro drives a DM-RMC's RS-232 / IR / Relay

Short answer up front: a Crestron program never writes TCP bytes directly. The managed `.NET` code you touch (`ComPort.Send("...")`, `IROutputPort.Press(cmd)`, `Relay.Close()`) walks a three-layer stack. Only the top two layers are in the decompiled C#; the actual socket write to CIP :41794 is in a native DLL below the P/Invoke boundary. The flat-join envelope that our XPanel capture decoded is the *innermost* leaf of this stack — the real routing happens via a nested-container envelope *above* it.

---

## The three-layer stack

### L1 — Physical transport (TCP :41794 CIP session)

The managed `.NET` runtime does not own the socket. Every outbound packet is handed as an opaque struct to native `TLDMInterfaceDLL.dll` via a single P/Invoke bridge class, `Crestron.SimplSharpInternal.Tldm.TLDMManagedToNativeInterface`. The *only* `[DllImport]` wire call that survives the decompile is:

```
[DllImport("TLDMInterfaceDLL.dll")]
public static extern bool SendSyncOnCresnetMessageToTLDM();
```

**Primary citation:** `SimplSharpPro_exe.cs:176006`.

That native DLL owns the CIP TCP connection on port 41794, the outer CIP opcodes (0x01 register, 0x02 register-result, 0x05 data, 0x0D heartbeat, 0x0F program-ready), and all cert/auth negotiation if any exists (grep across the entire managed decompile for `TcpListener`, `TcpClient`, `41794`, `0xA342`, `SecureTCPServer`, `SharedSecret`, `Cert` returned **zero hits**). The managed code is purely a producer of structured bytes and a struct-pointer caller.

### L2 — Device registration (sign-on + capability advertisement)

Before any sig update can flow, each device must have told the master "I exist, here is my IPID, here is my product name, here is my capability bitfield." That handoff is a *managed-code-filled, native-code-sent* struct: `TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT`.

**Primary citation:** `SimplSharpPro_exe.cs:167437-167796`.

The managed side fills in:

- `singleDeviceOrSlotId` — the IPID
- `singleDeviceParentType` — `ETHERNET_TYPE=3` (an IPID device) or `CRESNET_TYPE=2` or `GATEWAY_TYPE=4`
- `singleDeviceRegistrationFlags` — bit 0 ports-exclusive, bit 1 device-exclusive, bits 2-9 encode the `eTypeOfEthernetDevices` sub-field (`CIP_TCP=2`, which is what a DM-RMC uses)
- UTF-16 blobs for `uniqueInstanceId^ipAddress`, friendly name, product name

The managed side then calls `TLDMManagedToNativeInterface.SendMessageToTLDM(IntPtr, uint)` and *blocks* in `WaitForTldmResponse` until the native layer reports back. The native layer is what actually frames and emits CIP opcode 0x01 register on the socket.

Important nuance: `DeviceRegistrationMethod` (the `Method=6` vs `Method=0` field you noticed in the three-constructor pattern) is a **write-only documentation tag never read anywhere in the managed code** — grep for any read returns zero. The real dispatch key is `m_eParentType` + the Flags bitfield. See `device-registration-method-6` report: setter at `SimplSharpPro_exe.cs:75848–75871` with Crestron's own docstring "Not currently used, but contains the device registration types used by logic."

### L3 — Slot-addressed sig dispatch (the nested-container envelope)

Once registered, every signal update (`BoolInputSig`, `UShortInputSig`, `StringInputSig`) is encoded as a **nested-container Cresnet payload**, not a flat `(join, value)` tuple. The outer bytes encode a hierarchy walk from the IPID down through chassis slot → sub-slot → leaf port, with each level wrapped as `[ID][Length][ContainerType=0x20][Body]`. The real-time XPanel traffic you captured only sees the innermost `[joinHi joinLo value...]` leaf because an XPanel is a single flat device with no hierarchy — a DM-RMC has four levels of hierarchy for its COM port.

**Primary citation:** `SimplSharpPro_exe.cs:114730-114772` (the AddEncapsulationToPacket docblock, containing the canonical worked example):

```
MySwampE4.Zones[2].Bass.UShortValue = 25;

HierarchyList[0]: ID=3  (Cresnet device)
HierarchyList[1]: ID=4  (sub-slot SWAMPE-4)
Device.ID: 2            (Zone 2)

Produces:  [03 0B 20 [04 08 20 [02 05 14 00 07 00 19]]]
            │  │  │   │  │  │   │  │  │  └──┬── └──┬──
            │  │  │   │  │  │   │  │  │   join 7   value 25
            │  │  │   │  │  │   │  │  type 0x14 ANALOG_SYMMETRIC
            │  │  │   │  │  │   │  len=5
            │  │  │   │  │  │   deviceID=2
            │  │  │   │  │  containerType 0x20
            │  │  │   │  len=8
            │  │  │   subSlotID=4
            │  │  containerType 0x20
            │  len=11
            outerSlotID=3
```

Every byte above 16-bit values is **big-endian**. Container type is auto-chosen per level: `0x20` for 1-byte-ID + 1-byte-length, `0x35` for long-length form, `0x41`/`0x42` for 4-byte-ID (BACnet).

---

## The call chain, step by step

Walking `rmc.ComPorts[1].Send("hello\r")` down to bytes on the wire:

| # | Method | File:line | What it does |
|---|---|---|---|
| 1 | `ComPort.Send(string)` | `SimplSharpPro_exe.cs:299021` | Assigns `TransmitString` property |
| 2 | `TransmitString` setter | `SimplSharpPro_exe.cs:295648` | `f = value; SendString(ComPortJoins.Joins[m_iID][14], f);` — looks up the TX wire-join (0 for port 0) in a static table |
| 3 | `ComPort.SendString(uint, string)` | `SimplSharpPro_exe.cs:300684` | Calls `SendSerial(join, chars, length, encoding, SingleString, 2 /* NORMAL_SEND */, e_PktUpdateRequestProcessNormally, SendAsRaw:false, sendAsEncrypted:false)` |
| 4 | `DeviceBasis.SendSerial(...)` | `SimplSharpPro_exe.cs:11173` | Checks `Registered`, `IsOnline`, `IsJoinGatedToTransmit`; under `UpdateRequestJoinProtection` lock, calls... |
| 5 | `CSSPDeviceProtocol.BuildAndSendSingleSerial(...)` | `SimplSharpPro_exe.cs:102103` | Looks up `m_iSerialTransmitType` (set to `TRILIST_TX_SERIAL_12_OR_15H` in `ComPort.cd()` at `298824`) and routes to the 0x15 builder |
| 6 | `BuildAndSendCresnetSerial_Internal_15h` | `SimplSharpPro_exe.cs:102624` | Allocates `TLDM_FROM_APP_CRESNET_PACKET_STRUCT Packet = default`, grabs `byte* pPacketBuffer`, calls... |
| 7 | `BuildCresnetSerial_Internal_15h_or_34h` | `SimplSharpPro_exe.cs:102721` | **The byte-level encoder.** Writes `[0x15][joinHi][joinLo][flagByte][payload...]` into the pinned buffer (write loop at lines 102856-102862). flagByte = `(encoding) \| (textMode) \| (sendAsEncrypted ? 0x20 : 0)` |
| 8 | `CSSPDeviceProtocol.SendPacketToTLDM(...)` | `SimplSharpPro_exe.cs:115695` | **The LOCAL/REMOTE pivot.** Four cases: (a) InterProgramCommDevice → `BuildAndSendIPCPacket`; (b) 3-series slave/proxy → in-process loopback via `HandleCresnetPacketFromSelf`; (c) `SendType==4` → same loopback; (d) **everything else (the remote-RMC path):** calls `AddEncapsulationToPacket` to prepend the hierarchy containers, sets `deviceSendPacketMessageType = 9` (FROM_APP_CRESNET_PACKET), and calls... |
| 9 | `AddEncapsulationToPacket` | `SimplSharpPro_exe.cs:114775` | Writes containers **right-to-left** from `HierarchyList`: `[outerSlotID][len][0x20][subSlotID][len][0x20][deviceID][innerLen][innerType][innerBody]` |
| 10 | `TLDMManagedToNativeInterface.SendMessageToTLDMEx(IntPtr pkt, uint len, uint timeoutMs)` | invoked at `SimplSharpPro_exe.cs:115763` | P/Invoke into native TLDM. **Beyond this line the C# ends and TLDMInterfaceDLL.dll takes over.** The native code wraps the whole payload in CIP outer framing (opcode 0x05 data + length) and writes it to the already-open TCP socket to the master. |

For a DM-RMC-4K-SCALER-C, `HierarchyList` for its ComPort looks like:

- `HierarchyList[0]`: outer IPID of the RMC (e.g. 0x50)
- `HierarchyList[1]`: Slot 1 (Rmc200CCOMSlot, ID=1)
- Device.ID: port 0 (zero-based; one-based public getter returns 1)

So `"hello\r"` on `ComPorts[1]` of IPID 0x50 lands on the wire as:

```
[50 ?? 20 [01 0E 20 [00 0B 15 00 00 00 'h' 'e' 'l' 'l' 'o' 0x0D]]]
```

**Relay1.Close()** uses the same spine but a different leaf:

- `Relay.State = true` setter at `SimplSharpPro_exe.cs:311704` → `SendDigital(MagicCueNumber - 1, true)` = `SendDigital(109, true)` (Relay1's magic cue is 110 from `DmRmcScalerC.cs:292`)
- Routes through `CSSPDeviceProtocol.BuildAndSendCresnetLongDigital_00h_Internal` at `SimplSharpPro_exe.cs:99862`
- Leaf wire bytes: `[0x03][0x00][joinLo=0x6D][joinHi=0x00]` for press, `[0x03][0x00][joinLo=0x6D][joinHi=0x80]` for release (0x80 bit on JoinHi = release)

**IR Press** skips the sig/join mechanism entirely:

- `IROutputPort.Press(driver, cmd)` at `SimplSharpPro_exe.cs:305469` calls `CSSPDeviceProtocol.BuildAndSendIRStartByUID(this, m_iID, driverCRC, functionCRC, counter, 0)` at `305541` (or `BuildAndSendIRStartCode` at `305636`)
- Leaf wire bytes: `[0x16][subtype=0x07 IR_BY_UID][driverCRC...][functionCRC...]`
- m_iID (raw zero-based port index) is in the packet, **not a join** — the parent slot resolves which port by that index

---

## Why our existing CIP capture missed this

Our XPanel-side CIP capture decoded only the **leaf** of the stack: flat `(joinType, join, value)` triples. That worked because an XPanel registers as a single flat device — its `HierarchyList` is empty, so `AddEncapsulationToPacket` writes zero container bytes and the entire packet *is* the leaf.

A DM-RMC is a four-level hierarchy. The byte sequence that actually hits Wireshark for `rmc.ComPorts[1].Send("hello\r")` is **not** `[0x15][joinHi][joinLo][flags][payload]` — it's that same leaf *wrapped in three nested 0x20 containers*, as shown above. Our decoder would see a packet starting with `0x20` (container) rather than `0x15` (serial) and fall through its switch.

Specifically, the opcode(s) you need to teach the decoder:

- **`0x20`** `PKT_TYPE_CRESNET_CONTAINER` — 1-byte ID, 1-byte length. The workhorse. ~95% of hierarchy packets use only this.
- **`0x35`** `PKT_TYPE_CRESNET_CONTAINER_35` — 1-byte ID, 2-byte big-endian length. Used when a container's payload exceeds 255 bytes.
- **`0x41`** `PKT_TYPE_CRESNET_CONTAINER_32B_ID` — 4-byte big-endian ID, 1-byte length. Used when a slot or device ID exceeds 255 (BACnet remote devices).
- **`0x42`** `PKT_TYPE_CRESNET_CONTAINER_LONG_32B_ID` — 4-byte ID, 2-byte length.
- **`0x38`** / **`0x39`** `PKT_TYPE_COMPLEX_OBJECT_CONTAINER[_LONG]` — Core-3 Smart Graphics (XPanel object UI). Not needed for RMC.
- **`0x45`** `DEVICE_GROUP_MULTICAST_PACKET` — multicast variant.

The length byte of each container counts from immediately **after** itself through the end of that container's payload, **including** the container-type byte of its first inner element. The decoder needs to be recursive: read 1 byte ID, 1 byte length (or more for long forms), peek the next byte to decide "another container (0x20/0x35/0x41/0x42) or a leaf opcode", recurse or decode-leaf, repeat.

Full inner-opcode table: `enum CresnetTypes` at `SimplSharpPro_exe.cs:496431-496856` (425 lines, 55+ entries). Key ones for RMC endpoints: `0x00` DIGITAL, `0x01`/`0x02`/`0x14` ANALOG variants, `0x03` CRESNET_CONTROL (with ~30 sub-opcodes including the end-of-query sentinels `0x1C` / `0x1D`), `0x15`/`0x34` SERIAL, `0x16` IR_DATA, `0x18` INTERNAL_CONTROL (capability flags like "supports-UTF16", "supports-type-34"), `0x3F` ESA↔IOP (versiport config, port-in-use, comspec).

One hypothesis worth noting: the "outer CIP opcodes" you reverse-engineered (`0x12` serial, `0x1C` / `0x1D` end-of-query) are **byte-identical to inner Cresnet types** `PKT_TYPE_CRESNET_SERIAL_12`, `PKT_TYPE_GENERIC_DEVICE_CONFIG`, `PKT_TYPE_CLX_LIGHTING_RCB`. It is plausible the native CIP outer framing is just `[cresnet-type-byte][len_hi][len_lo][body]` — i.e. the "outer opcode" you were decoding *is* the first byte of the Cresnet packet. The genuinely CIP-session-only opcodes are `0x0F` program-ready, `0x01` register, `0x02` register-result, `0x0D` heartbeat (none of these are in the CresnetTypes enum).

---

# Can we emulate the chassis side from Extron (or Python)?

## Layer-by-layer feasibility (verdict from the Verify stage)

| Layer | Verdict | Why |
|---|---|---|
| **L1 — Transport + handshake** | **PARTIAL** | No app-layer auth exists at the managed layer — grep for cert/secret/handshake returned zero hits, and the live RMC accepted the arbitrary peer `169.254.0.1` the moment `ADDMaster` was pointed there. **But** the four sign-on packet types (`e_PktSlaveRegister2Series`, `e_PktSlaveRegister3Series`, `e_PktEngageSlave`, `e_PktSlaveModeStatus`, enumerated at `SimplSharpPro_exe.cs:95574-95590`) fall into the default no-op branch of `ParseProcessedCresnetData` at `89909-89927`. The managed layer never parses or constructs them; the byte layout lives entirely in native `TLDMInterfaceDLL.dll`. |
| **L2 — Registration** | **PARTIAL** | We know the master→native-TLDM IPC struct (`TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT` at `SimplSharpPro_exe.cs:167437`). We know `DeviceRegistrationMethod` is write-only noise. We know Flags=9 means "ports-exclusive + CIP_TCP". But the master→slave on-wire register-ACK (CIP opcode 0x02) is in native code — the layout only comes from a pcap. The *good* news: no "is this a real Crestron processor" identity check appears anywhere in managed code. |
| **L3 — Slot-addressed sig dispatch** | **YES — fully specified** | Nested-container Cresnet payload format is documented at the byte level (`SimplSharpPro_exe.cs:114730-114772` docblock + `BuildCresnetSerial_Internal_15h_or_34h` at `102721`). All three primitive leaves we need are spec'd: serial 0x15 for ComPort TX, long-digital 0x03/0x00 for Relay close, IR_DATA 0x16 for IR pulse (keyed by raw port index, no join). Slot hierarchy for DM-RMC-4K-SCALER-C is pinned: outer IPID → Slot 1 (COM) → port 0 → serial join 0 (`ComPortJoins.Joins[0][14]=0` at `SimplSharpPro_exe.cs:300711`); Relay1=digital join 110, Relay2=160 (`DmRmcScalerC.cs:292-293`). We can hand-encode a working frame today. |
| **L4 — Steady-state completeness** | **PARTIAL** | After register, the master owes the slave at least (a) a periodic shared-info push (`TLDM_SINGLE_DEVICE_SHARED_INFORMATION_STRUCT` at `SimplSharpPro_exe.cs:168998`) and (b) heartbeat framing (your observed opcode `0x0D`). Both have payload shapes that live below the P/Invoke boundary. Capability negotiation itself is opportunistic (`PKT_TYPE_INTERNAL_CONTROL 0x18` carries feature-flag advertisements rather than a mandatory handshake). End-of-update sentinels (`0x16` END_OF_UPDATE, `0x1C` END_OF_QUERY, `0x1D` END_OF_QUERY_RESPONSE under PKT_TYPE_CRESNET_CONTROL 0x03) are documented. |

**Overall verdict: PARTIAL — not blocked, but two pcaps away from complete.**

## Risks and unknowns

**Hardest layer: L1 handshake** — specifically the master's reply to the slave's `SlaveRegister2Series` / `SlaveRegister3Series` frame. The slave emits one of these within milliseconds of the TCP SYN+ACK, and if the master doesn't echo back a well-formed register-result (CIP 0x02) with a plausible-looking payload, the slave closes the connection and retries. The ePacketType constants are the only artifacts in managed code — no builder, no parser.

**Second-hardest: heartbeat (opcode 0x0D).** If the slave times out when no heartbeat arrives, the stub listener will churn. We don't know the heartbeat interval or whether the payload needs to echo any slave-side state. The managed code never surfaces this because the native layer answers heartbeats directly.

**Where could it fail silently:**

- **Capability negotiation via `PKT_TYPE_INTERNAL_CONTROL 0x18`** has sub-opcodes like `supports-type-34` and `supports-UTF16`. If the master doesn't volunteer these, the slave may fall back to short-form packets only. For a DM-RMC that is fine (no 32KB serial strings) but worth logging.
- **The `2-Series vs 3-Series` SlaveRegister variants** suggest version negotiation. A CP4 might expect only the 3-Series frame, while a CP3 might accept both. If we emit the wrong one and the slave is strict, the handshake stalls.
- **Hidden identity data in the native layer.** The managed decompile shows no cert, no shared secret, no DllImport reveals a key-exchange call, and the live RMC accepted a bare peer — but we cannot prove by absence that TLDMInterfaceDLL doesn't do something at the native level. Only a pcap diff of a real master's register-result vs. our stub's rules this out.

What we *can* rule out: TLS/SSL (no `SecureTCPServer` references), per-device shared secrets (no key material in Register struct), SIMPL symbol-code verification (set to 0 for user-created devices), and application-layer auth gating sig dispatch (no `if (!m_bAuthenticated) return` guards in the SendXxx path).

## The one experiment to run next

**Target: 30 minutes, test bench with the already-paired DM-RMC-4K-SCALER-C and DM-MD8X8-CPU3-RPS chassis.**

**Step 1 — Capture a real sign-on.** Point the RMC's `ADDMaster` at a Windows capture host on the same subnet, running Wireshark on `tcp port 41794`. From any Crestron console with chassis access:

```
ADDMaster 1 <capture-host-ip>
REBOOT
```

Record 60 s past the `CIP_ID N Gway ONLINE 41794` line. Save as `rmc-real-master.pcap`.

**Step 2 — Stand up a stub listener.** `<repo>\experiments\crestron-dm-md-bridge\stub-master.py`:

```python
import socket
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 41794))
s.listen(1)
c, a = s.accept()
print("peer", a)
while True:
    hdr = c.recv(3)                 # [opcode][len_hi][len_lo] - framing hypothesis
    if len(hdr) < 3:
        break
    op, L = hdr[0], (hdr[1] << 8) | hdr[2]
    body = c.recv(L) if L else b""
    print("<<", hex(op), L, body.hex())
    if op == 0x01:                              # register from slave
        c.sendall(bytes([0x02, 0x00, 0x02, 0x00, 0x00]))   # minimal register-result stub; refine from pcap
```

Point the RMC's `ADDMaster` at the stub host. Watch which opcode the RMC retries after the 0x02 reply — that identifies whether the next required master-emitted frame is `0x0F` program-ready or `0x0D` heartbeat, and the pcap from step 1 gives us the exact bytes to copy.

**Step 3 — Prove L3 end-to-end.** Once the stub reaches steady state (RMC console shows `ONLINE 41794 <stub-ip>`), hand-encode and send a single ComPort-TX frame. Outer `[0x05][len_hi][len_lo]` + inner nested container:

```
[rmcIpid] [outerLen] [0x20]
    [0x01] [subLen] [0x20]           # Slot 1 = Rmc200CCOMSlot
        [0x00] [0x0B] [0x15]         # port 0, serial 0x15 leaf, body len 11
        [0x00] [0x00]                # join hi/lo = 0 (ComPortJoins.Joins[0][14])
        [0x00]                       # flags: ASCII, SingleString, not encrypted
        'T' 'E' 'S' 'T' 0x0D         # payload
```

**Pass criterion:** `TEST\r` appears on the RMC's RS-232 pin. L3 is proven end-to-end and only L4 (heartbeat / shared-info) remains before this is a complete emulation path.

**If it does not appear but TCP stays open:** the outer envelope opcode byte is wrong. Try `0x12` serial pass-through (cip-transport-wire-format `opcodesSeen` 0x12 and the collide-with-inner-type hint). Iterate.

---

# Research-to-code shopping list

If we commit to pursuing the Extron (or Python) emulator, these are the implementation items with rough line-count estimates (Python, counting non-comment-non-blank, excluding tests):

| Item | LoC | Notes |
|---|---|---|
| **TCP transport server** (`asyncio` listener on 41794, per-connection task, outer CIP framing read/write) | **~150** | `[opcode][len16_be][body]` framer plus connection state (SYN, awaiting-register, registered, closed). Mostly plumbing. |
| **Sign-on handler** (parse SlaveRegister2Series/3Series, emit register-result, EngageSlave reply) | **~200** | **Blocking on L1 pcap.** Byte layout unknown until step 1 of the experiment above. Allow 2x if the 2-Series/3-Series variants need separate code paths. |
| **Sig-update encoder/decoder** — nested-container envelope + leaf types (digital 0x03/0x00, analog 0x14, serial 0x15, IR 0x16) | **~350** | Recursive container writer/reader, 4 leaf encoders, 4 leaf decoders. The spec is complete; this is pure translation of `BuildCresnetXxx` / `AddEncapsulationToPacket` from the decompile. Container type auto-selection (0x20 vs 0x35 vs 0x41 vs 0x42) is ~30 LoC. |
| **RMC-specific join map** — slot hierarchy + ComPort TX join 0, IR raw port index 0/1, Relay1 join 110 / Relay2 join 160 for DM-RMC-4K-SCALER-C | **~80** | Dict literal plus a small resolver. Add one dict per RMC model as needed (DM-RMC-100-F, DM-RMC-150-S, DM-RMC-200-C, DM-RMC-200-S, DM-RMC-4K-SCALER-C, DM-RMC-4K-SCALER-C-DSP, DM-RMC-4KZ-SCALER-C — same relay joins across all per `manifest-and-join-registry`). |
| **ComPort RX decoder** (inbound serial 0x15 unwrap → callback with `(portIndex, bytes)`) | **~60** | Reverse of serial encoder; needs flagByte decode for ASCII vs UTF-16 and the 0x0A→`*` / 0x0B→`#` ASCII remapping. |
| **Watchdog / heartbeat** (periodic 0x0D emit, response-timeout close) | **~80** | **Partially blocking on L1 pcap** — payload shape unknown but interval is probably observable from the capture. Default: emit every 15 s, close connection on 2x missed. |
| **Reconnect / ADDMaster-swap handling** (accept new SYN, invalidate prior state, re-register) | **~100** | Mostly state-machine. The RMC drops the TCP session when its `ADDMaster` entry changes and reconnects to the new peer; we just need to not leak the old session. |
| **Shared-info / capability push** (`TLDM_SINGLE_DEVICE_SHARED_INFORMATION_STRUCT` echo at `SimplSharpPro_exe.cs:168998`, PKT_TYPE_INTERNAL_CONTROL 0x18 feature-flag emit) | **~120** | **Partially blocking on L1 pcap.** Advertising `supports-type-34` + `supports-UTF16` is a 5-byte emit each; the shared-info push structure needs byte-level confirmation. |
| **Logging + hex-dump + replay harness** | **~150** | Rip and replay from pcap for regression. Essential for iterating on L4. |
| **Integration tests** against real RMC (not counted above) | ~300 | Separate file. |

**Total: ~1,290 LoC** for a functionally complete emulator covering ComPort TX, ComPort RX, IR pulse/press/release, Relay close/open, Relay state feedback, and heartbeat. **Of that, ~400 LoC (sign-on, heartbeat, shared-info) is gated on one pcap** of a real CP3/CP4 ↔ DM-RMC handshake. The remaining ~890 LoC (transport, encoders, join map, reconnect) can be built against the decompile today without blocking on hardware access.

**One architectural note.** The L3 encoder is the natural reusable core. If we structure it as `encode_container(id, inner_bytes)` / `encode_leaf_serial(join, text, encoding)` / `encode_leaf_digital(join, press)` / `encode_leaf_ir(port_index, driver_crc, func_crc)`, the same encoder serves any DM endpoint — we only swap the join map and the hierarchy. That generality buys us DM-RMC-100-F, -150-S, -200-C, -200-S, and the Scaler family for free once DM-RMC-4K-SCALER-C works.

---

### Key file:line references (all under `C:\Users\<user>\.claude\jobs\50e4735d\tmp\decompiled\`)

- `SimplSharpPro_exe.cs:95554` — `internal class CSSPDeviceProtocol` (the serializer)
- `SimplSharpPro_exe.cs:95574-95590` — ePacketType enum including sign-on variants
- `SimplSharpPro_exe.cs:102721` — `BuildCresnetSerial_Internal_15h_or_34h` (byte-level serial encoder)
- `SimplSharpPro_exe.cs:114730-114772` — AddEncapsulationToPacket docblock with worked example
- `SimplSharpPro_exe.cs:114775` — AddEncapsulationToPacket canonical implementation
- `SimplSharpPro_exe.cs:115695` — SendPacketToTLDM LOCAL/REMOTE pivot
- `SimplSharpPro_exe.cs:167437-167796` — TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT
- `SimplSharpPro_exe.cs:176006` — the only wire-level DllImport
- `SimplSharpPro_exe.cs:300711` + `300773` — ComPortJoins.Joins[6][22] table
- `SimplSharpPro_exe.cs:311704` — Relay.State setter → SendDigital(MagicCueNumber - 1, value)
- `SimplSharpPro_exe.cs:496431-496856` — enum CresnetTypes (full inner-opcode table)
- `DmRmcScalerC.cs:292-293` — Relay1 magic 110, Relay2 magic 160 (DM-RMC-4K-SCALER-C)
- `DmRmcScalerC.cs:215-216` — Slot 1 Rmc200CCOMSlot, Slot 2 Rmc200CIRSlot
- `Rmc200CCOMSlot.cs:33` — `PortCreator.CreateComPort(0u, this, 17u, 81919u, paramParent)`
