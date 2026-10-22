# DM slot-addressed Cresnet payload encoding - spec

## TL;DR for parent

- The on-wire LEAF-level encoding for `ComPort[N].StringInput = "HI\r"` is
  **confirmed byte-exact** from the clean SimplSharpPro.dll decompile at
  `BuildCresnetSerial_Internal_15h_or_34h` (line 46792 of the .NET
  Standard variant). Format: `[DeviceID][Length][0x15][Join_hi][Join_lo][Flags][StringBytes][optional 0x0D]`.
- The CONTAINER (wrapper) encoding for the hierarchy is confirmed from
  `AddEncapsulationToPacket` body and `InsertID` at line 58919. Each
  container level: `[ID][Length][TypeByte][body]` where TypeByte is one
  of `0x20/0x35/0x41/0x42` depending on short/long length and 1/4-byte ID.
- **No separate "slot-register" wire message is required** before
  writing. Session ownership is established by ALTERNATE_CONNECT only
  (finding 19). The IPC register path (opcode 28 in TLDM_FROM_APP_* IPC
  structs) is master-local; when WE are the master, that step is
  bypassed and DATA frames can flow directly.
- **Specific DM-MD slot IDs still need empirical probing.** The chassis
  will reveal them in response to an Update Request. The protocol
  machinery is nailed; the exact hierarchy IDs for your specific
  chassis+endpoint pair are reads-worth-of-work, not spec-worth-of-work.

**Ready-to-paste byte sequence template** for `cip_master_v1.py` once
the slot IDs are known:

    # Target: chassis slot ID = CHASSIS_SLOT, output slot ID = OUT_SLOT,
    #         RMC device ID = RMC_ID, ComPort StringInput join = JOIN
    body_in = b"HI\r"                                       # ASCII payload
    leaf  = bytes([RMC_ID])                                 # device ID (1 byte)
    leaf += bytes([3 + 1 + 2 + 1 + len(body_in)])           # length byte
    leaf += bytes([0x15, (JOIN>>8) & 0xFF, JOIN & 0xFF])    # type + join
    leaf += bytes([0x00])                                   # flags: ASCII, no CR append, no encrypt
    leaf += body_in                                         # payload
    mid   = bytes([OUT_SLOT, len(leaf) + 1, 0x20]) + leaf   # inner container
    outer = bytes([CHASSIS_SLOT, len(mid) + 1, 0x20]) + mid # outer container
    cresnet = outer                                         # pCresnetPacket[1:...]
    master.send_data(cresnet)

## 1. Container wrapper encoding

Source: `SimplSharpPro_exe.cs:114730-114772` docblock plus the
`AddEncapsulationToPacket` body at :114775 (dotfuscated with
control-flow obfuscation) and the cleaner `BuildCresnetSerial_Internal_15h_or_34h`
plus `InsertID` in `SimplSharpPro.dll` decompile.

Each container wrapper on the wire:

    [ID : 1 byte or 4 bytes BE]
    [Length : 1 byte for short, 2 bytes BE for long]
    [TypeByte : 1 byte]
    [body : Length-1 bytes OR Length-2 bytes]

The `TypeByte` and `Length` width is correlated:

| TypeByte | Name                   | ID width | Length width | Used when                       |
|---------:|------------------------|---------:|-------------:|---------------------------------|
| 0x20     | e_PktContainer         | 1 byte   | 1 byte       | Normal short container, ID<=255 |
| 0x35     | e_PktContainerLong     | 1 byte   | 2 bytes BE   | Body > 253 bytes                |
| 0x41     | e_PktContainer32bID    | 4 bytes BE | 1 byte     | ID > 255                        |
| 0x42     | e_PktContainerLong32bID| 4 bytes BE | 2 bytes BE  | Body > 253 AND ID > 255         |
| 0x38/0x39| e_PktComplexJoin{Long} | 1/4 bytes| 1/2 bytes    | Smart objects (not needed here) |

Length counts bytes AFTER the Length field itself (i.e. starting at
TypeByte, inclusive, through the end of body).

### Finding-12 worked example re-verified

Given hierarchy `[outer ID=3][mid ID=4][leaf ID=2]` and leaf
`[0x14][Join=7][Value=25]` (analog symmetric):

    [03][0B][20] [04][08][20] [02][05][14][00][07][00][19]
    outer ID=3, Length=0x0B (= 11 bytes = type + 10 inner body bytes)
    mid   ID=4, Length=0x08 (=  8 bytes = type +  7 inner body bytes)
    leaf  ID=2, Length=0x05 (=  5 bytes = 0x14 + join_hi + join_lo + val_hi + val_lo)

Enum values confirmed in `SimplSharpPro.dll:32078` (CresnetTypes):

- `PKT_TYPE_CRESNET_DIGITAL          = 0`
- `PKT_TYPE_CRESNET_ANALOG           = 1`  (short analog; wire byte 0x01)
- `PKT_TYPE_CRESNET_ANALOG_SYMMETRIC = 20` (= 0x14; what finding 12 showed)
- `PKT_TYPE_CRESNET_SERIAL_15        = 21` (= 0x15; what ComPort uses)
- `PKT_TYPE_CRESNET_SERIAL_34        = 52` (= 0x34; long serial)
- `PKT_TYPE_CRESNET_SERIAL_12        = 18` (= 0x12; legacy serial)

## 2. ComPort[N].StringInput leaf encoding (0x15)

Source: `BuildCresnetSerial_Internal_15h_or_34h` at `SimplSharpPro.dll:46792-47200`
of the clean decompile. Write sequence inside the function
(switch case numbers from the dispatcher):

1. (`case 0`) `InsertID(buffer, IdWidth, deviceId, EncapsulationSize)` writes
   the leaf-device ID at `offset = EncapsulationSize`. Returns new offset.
   IdWidth is 1 for IDs <= 255, 4 for IDs > 255.
2. `num6 = num5++` saves the offset for the Length byte, then advances
   past it (length filled in later).
3. (`case 23`) If `LongPacket`: `num5++` advances past a 2nd length byte
   (long packets have 2-byte BE length).
4. (`case 33`) Writes three bytes:
   - `PacketType` = 0x15 for serial-15h, 0x34 for long serial-34h
   - `(Join >> 8) & 0xFF`
   - `Join & 0xFF`
5. (`case 24`) Writes one Flags byte:
   `(byte)outboundEncoding | TextAppendModeFlags | (sendAsEncrypted ? 32 : 0)`
   - `outboundEncoding`: 0 = ASCII, 4 = UTF16 (eStringEncodingFlags)
   - `TextAppendModeFlags`: a bitmask set by caller for append-vs-replace semantics
     (eOutboundTextModes). For a one-shot "set string" write, typically 0.
   - Add 32 if `sendAsEncrypted`.
6. (`case 5` -> `case 42` optionally) If `InsertCarriageReturn`, write `0x0D`.
7. (`case 22/31/47/13/16`) Loop writing the actual string bytes
   (character-remap optional).
8. (`case 14 -> IL_05fe -> case 45`) Write LENGTH BACK at offset `num6`:
   - Short packet: `buffer[num6] = (byte)(num5 - num6 - 1)` i.e. count of
     bytes from the byte after Length through end-of-body.
   - Long packet: `buffer[num6..num6+1] = (num5 - num6 - 2) BE`.

**Resulting leaf bytes for a short-packet serial-15h write**:

    [DeviceID : 1 byte]
    [Length   : 1 byte]       (= 1 + 2 + 1 + N + optional-CR = 4 + len(payload))
    [0x15]
    [Join_hi]
    [Join_lo]
    [Flags]                   (0x00 for ASCII, no append flag, no encrypt)
    [Payload bytes : N]       (string characters)
    [0x0D]                    (if InsertCarriageReturn, optional)

Caveats:
- `Value.Length` cannot exceed what fits in a 258-byte buffer at
  BuildAndSendSingleStringParameter level (:49651 check `num5 <= 258`).
  Longer strings use `BuildAndSendCresnetSerial_Internal_34h` with
  the 0x34 TypeByte and 2-byte length.
- The chassis treats this leaf as "assign this serial signal of this
  device to this value" - exactly the ComPort.StringInput semantics.
- `BuildAndSendSingleStringParameter` (line 49582) is for device
  configuration parameters, NOT for ComPort signals - note it uses
  TypeByte 28 (0x1C) and a different flags byte (5). Don't confuse
  these paths.

## 3. Routing (MatrixCrosspoint) leaf encoding

Confirmed indirectly: switcher routing in Crestron SIMPL# Pro is driven
by writing a UShortInputSig named `VideoOut` on each output's slot.
Semantically, `switcher.Outputs[N].VideoOut.UShortValue = M` routes
input M to output N. The underlying encoding is a plain analog signal
write at a specific join number inside the output slot.

The leaf bytes are therefore analog (symmetric):

    [DeviceID : 1 byte]   = the output's slot ID in the chassis's
                            device-space
    [Length   : 1 byte]   = 5
    [0x14]                = PKT_TYPE_CRESNET_ANALOG_SYMMETRIC
    [Join_hi]             = VideoOut sig join hi byte
    [Join_lo]             = VideoOut sig join lo byte
    [Value_hi]            = input number hi byte (0 for 1-8)
    [Value_lo]            = input number lo byte

Wrapped in container(s) addressing the chassis + output path.

The specific `VideoOut` join number for a DM-MD8X8-CPU3 output is NOT
directly extractable from DM.cs by grep because the sig is injected via
`_txVideoOut = txVideoOut` at line 200206 and the actual join index is
set at a wiring call site I couldn't locate without a full data-flow
trace. Empirical probing will reveal it.

## 4. Slot addressing conventions - what the chassis's hierarchy looks like

Based on `DmMd8x8Cpu3rps` class at `DM.cs:173158` and the
`Ethernet_DM_MD8x8_CPU3_with_RPS` inner class:

- Chassis is registered to the master as an EthernetDevice with
  `DeviceRegistrationFlags = 9` and `DeviceRegistrationMethod = 6`.
  Its parent-type on the gateway channel is **GATEWAY (= 4)** per
  finding 18's harvest of `singleDeviceParentType`.
- The chassis has:
  - 8 inputs: child StartID=1, EndID=8
  - 5 "slot-33..37" cards (control registers / aux slots)
  - 8 outputs: NumberOfOutputs=8, each a slot that can have an
    EndpointReceiverBase device attached
- `((Switch)this).NumberOfInputs = 8` and `.NumberOfOutputs = 8`
- Signal size on chassis: 120 digital in, 232 digital out, 84 analog
  in/out, 28 serial in/out
- Example from a DM.cs doc comment (line 139323):
  `_dmRmc4kScalar = new DmRmc4kScalerC(0x06, switcher.Outputs[24]);`
  The `0x06` is the RMC's own ID within the output slot (a
  per-endpoint handle, typically a small integer); the `Outputs[24]`
  is the output card's index.

So the hierarchy for our DM-RMC-4K-SCALER-C at output 101 of a
DM-MD8X8-CPU3-RPS looks approximately like:

- Outer wrapper: `ID = chassis-top-level-slot-id (gateway slot)`, type 0x20
  - Middle wrapper: `ID = output-slot-id (1..8 or possibly 101..108)`, type 0x20
    - Leaf: `ID = RMC's internal ID`, type 0x15 for ComPort or 0x14 for routing

The **top-level chassis slot ID is NOT the IPID**. The IPID is just the
session-identity in the gateway handshake (we picked 0x0001). The slot
IDs inside the Cresnet-over-TCP container tree are chassis-specific
numbers assigned by the chassis's own program.

**IDs needed and how to find them empirically** (one query frame reveals them):

Send a chassis-level **Update Request** - a Cresnet control packet with
`PKT_TYPE_CRESNET_CONTROL = 3` and subtype
`PKT_TYPE_CRESNET_CONTROL_SUBTYPE_UPDATE_REQUEST_VARIANT = 4`. The
chassis will reply by dumping its registered device/slot/join tree over
opcode-5 DATA frames. The hierarchy IDs appear directly in those
container wrappers.

The exact wire bytes to send:

    cresnet = bytes([
        0x01,            # top-level device ID (speculation; try 1 first)
        0x02,            # length
        0x03,            # 0x03 = PKT_TYPE_CRESNET_CONTROL
        0x04,            # 0x04 = UPDATE_REQUEST_VARIANT subtype
    ])
    master.send_data(cresnet)

If the chassis ignores or NAKs, iterate the top-level ID (0x01, 0x80,
chassis IPID, etc.). Each response (if any) is a snapshot of the device
hierarchy, from which the ComPort join number and output slot IDs can
be read.

## 5. Device-of-record / ownership on-wire

Finding 18 showed the IPC-level `TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT`
with opcode 28 (REGISTER) and parent-type GATEWAY. **That is master-local
IPC, not an on-wire message to the chassis.** The managed app registers
devices with the LOCAL daemon so the daemon knows which app owns which
slot. The daemon's TCP channel to the chassis handles slot addressing
purely via the Cresnet container hierarchy.

Confirmed by:
- `TLDMManagedToNativeInterface.SendMessageToTLDM()` carries the register
  struct, hands it to the daemon via `TLDMInterfaceDLL.dll` (symlink to
  `libTLDMSYMPROCInterfaceLogos.so`), which is a LOCAL IPC endpoint.
- The daemon owns the TCP socket to the chassis (`PROTO_TLDM.dll`
  implements it in managed code, loaded by `SimplSharpPro.exe`).
- The chassis-side wire protocol has no DEVICE_REGISTER opcode in the
  EGatewayMessageTypes enum (finding 19). The only opcodes are
  2/3/4/5/10/11/12/13/14/15/18/38/39.
- Slot addressing on the wire is entirely via the container-tree ID
  nesting inside opcode-5 DATA frames.

**Conclusion**: For us (acting as the master), ALTERNATE_CONNECT
establishes the session with our CID, and we can send opcode-5 DATA
frames with slot-addressed Cresnet payloads immediately. No separate
on-wire registration step is required for the chassis to accept them.

The chassis might reject writes to slots that are already owned by
another registered master (if any), or might overlay them. In our setup
the chassis's own DM-link control plane is the de-facto master for the
endpoints - we may step on its toes with writes. Reads/queries are safer
first probes.

## 6. Suggested next experiment (empirical bridging)

Add to `cip_master_v1.py` after the handshake succeeds:

    # 1. Fire an update request to see what the chassis exposes
    master.send_data(bytes([0x01, 0x02, 0x03, 0x04]))

    # 2. Hold the session for 30s with verbose RX logging; expect
    #    opcode-5 DATA frames back containing the device tree

The RX frames will reveal: chassis top-level slot ID, output slot IDs,
RMC's device ID, join numbers for VideoOut and ComPort StringInput.

Once those are known, the ComPort loopback write becomes:

    cresnet_payload = bytes([
        CHASSIS_ID, container_len, 0x20,
        OUT_SLOT_ID, inner_len, 0x20,
        RMC_ID, leaf_len, 0x15, (JOIN>>8)&0xFF, JOIN&0xFF, 0x00,
    ]) + b"HI\r"
    master.send_data(cresnet_payload)

Watch the DM-RMC's loopback TX->RX feedback appear in a DATA frame rx.

## 7. Known unknowns (none blocking - all probe-able)

1. Exact `CHASSIS_ID` (top-level device ID in Cresnet space, not IPID)
2. Exact `OUT_SLOT_ID` for output 101 (likely 1 for Outputs[1] or 101
   for the engraved port label - need to see which the chassis publishes)
3. Exact `RMC_ID` (the per-endpoint internal ID; the DM.cs doc example
   used 0x06 as a sample constructor arg)
4. Exact `JOIN` number for ComPort[1].StringInput inside the DM-RMC-4K-SCALER-C
   signal space (grep for "txDeviceComPortStringInput" in the clean DM
   decompile shows signal counts of 28 serial in/out joins total; the
   StringInput join is one specific number within those)
5. Exact `JOIN` number for VideoOut inside the output slot

All five are empirically answerable by sending the Update Request and
parsing the RX. None require more static reading.

## 8. File:line citations

| What                                | File                                                 | Line        |
|-------------------------------------|------------------------------------------------------|-------------|
| ePacketType enum                    | SimplSharpPro_exe.cs                                 | 95556       |
| CresnetTypes enum                   | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 32078       |
| AddEncapsulationToPacket (dotfusc.) | SimplSharpPro_exe.cs                                 | 114775      |
| Container writes (dotfusc.)         | SimplSharpPro_exe.cs                                 | 114775-115700 |
| InsertID (clean)                    | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 58919       |
| BuildAndSendCresnetSerial_15h       | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 46792       |
| BuildCresnetSerial_Internal_15h_or_34h | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs  | 46985       |
| BuildAndSendSingleAnalog            | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 44872       |
| BuildAndSendSingleStringParameter   | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 49582       |
| DmMd8x8Cpu3rps class                | DM.cs                                                | 173158      |
| DmRmc4kScalerC class                | DM.cs                                                | 139401      |
| InitializeSigsDmRmc4kScalerC        | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 440262      |
| DeviceRegister IPC struct usage     | SimplSharpPro_dotnet/SimplSharpPro.decompiled.cs     | 102637      |
| EGatewayMessageTypes (wire opcodes) | ProtoEngine_dotnet/ProtoEngine.decompiled.cs         | 2062        |
| TCPGatewayClient                    | ProtoTcp_dotnet/ProtoTcp.decompiled.cs               | 7720        |
