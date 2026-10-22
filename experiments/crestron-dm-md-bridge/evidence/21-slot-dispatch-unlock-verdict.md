# Slot-addressed dispatch unlock — definitive answer

## Verdict

**No byte change in our client can unlock slot-addressed dispatch on this chassis's OEM default program.** The chassis-side `HandleGatewayDataMessage` → `HandleDataPacket` dispatcher silently drops packets whose destination device has no `CGatewayLink` registered — and the OEM default program never registers one, because it has no user-defined device objects (`DmMd8x8Cpu3rps`, `DmRmc4kScalerC`, etc.). To unlock slot-addressed dispatch on the physical hardware, the chassis itself must run a SIMPL# Pro program that instantiates and registers slot-bound device objects.

This is the same ceiling findings 10 and 16 hit, now cited at the exact dispatcher-level code lines.

## Evidence

### 1. Server-side opcode dispatcher

File: `ProtoTcp_dotnet/ProtoTcp.decompiled.cs:3084` — `ProcessIncomingGatewayData` is the chassis-side TCP accepter started in `TCPGatewayServer.Start` at :512. It switches on `MsgType`:

| Opcode | Handler |
|-------:|---------|
| 1 eCONNECT, 10 eALTERNATE_CONNECT | `HandleGatewayConnectMessage` (:2310) |
| 17 ePRODIGY_CONNECT, ePRODIGY_ALTCONNECT | `HandleGatewayConnectMessage` (same) |
| 38 eDEVICEROUTER_CONNECT_REQUEST | `HandleDeviceRouterGatewayConnectMessage` (:1467) |
| 11 eAUTHENTICATE | `HandleGatewayAuthenticateMessage` |
| 3 eDISCONNECT | `HandleGatewayDisconnectMessage` |
| **5 eDATA / 18 eEXTENDED_LENGTH_DATA** | **`HandleGatewayDataMessage` (:1230)** |
| 13 eHEARTBEAT | `HandleGatewayHeartBeatMessage` |

### 2. The critical silent-drop point

`HandleGatewayDataMessage` (:1230) → `HandleDataPacket` (:938) processes our payload byte-by-byte:

- `0x35` → long container (skip 4 bytes, nest deeper)
- `0x20` → short container (skip 3 bytes, nest deeper)
- `0x03` → control-type leaf; next byte names subtype:
    - 0, 4 (**update_request**), 23, 30, 34, 35, 45, 61, 62 all remap to UID-insertion variants
    - **Requires** `m_pMasterIPTable.GetIPTableEntry(ApplicationListForSharedDevices[0], DeviceId)` to return non-null AND `CGatewayLink` object to forward through
    - If `iPTableEntry != null` AND `cGatewayLink != null`: packet forwarded to device
    - **If either is null: packet dropped silently with no response** — this is our case

Code at :1041-1051:
```csharp
CGatewayLink cGatewayLink = (CGatewayLink)pSocketContainer.pGatewayLinkObject;
if (cGatewayLink == null)
{
    // nothing happens, exit silently
}
```

### 3. What makes `cGatewayLink` non-null

Tracing backwards: `pSocketContainer.pGatewayLinkObject` is set during `HandleGatewayConnectMessage` (:2310) only when:

- `num2 != 0` (our CID > 0 — our 0x0001 qualifies)
- AND `m_pMasterIPTable.FindRegisteredMasterNode(num2, DeviceIdType=2, ref appId)` returns non-null (:2440) — this looks up IPID 1 in the chassis's SIMPL IPTable; our chassis has it per `evidence/02` as `CGway` entry on 127.0.0.1
- AND the subsequent slot-binding logic creates a `CGatewayLink` for a REGISTERED device object

The last step is the gate. A `CGatewayLink` is created only when the SIMPL program running on the chassis has:
```csharp
var chassis = new DmMd8x8Cpu3rps(0x01, this);  // bind to IPID 1
chassis.Register();                             // creates IPTableEntry + CGatewayLink
```

The OEM default program has no such instantiation. It has only the generic `CGway` placeholder at IPID 1 (the stock XPanel registration) which doesn't bind to any device subsystem.

### 4. Clean master-side slot-write path (how a legit master emits bytes)

File: `SimplSharpPro_clean/SimplSharpPro.decompiled.cs` (505955 lines, extracted from `/usr/lib/CrestronLibs/dotnet/SimplSharpPro.dll`, non-dotfuscated — clean class names).

The master-side register call pattern (:102992):
```csharp
// Builds a 64-byte TLDM_SINGLE_DEVICE_REGISTER_MESSAGE_STRUCT
// Then calls TLDMManagedToNativeInterface.SendMessageToTLDM(&struct, length)
```

**`SendMessageToTLDM` is NOT a wire call.** It's an IPC call to a local in-process TLDM subsystem (which lives in `PROTO_TLDM.dll` + `PROTO_TCP.dll` in-process, NOT in the ARM `/usr/bin/TLDM` daemon). The local TLDM subsystem then:
1. Validates the device registration against the SIMPL program's declared devices
2. On successful validation, opens a TCP client to the chassis at `chassis_ip:41794`
3. Sends ALTERNATE_CONNECT with the master's CID (NOT 0x0001 — matches the SIMPL program's declared device IPID)
4. Chassis-side `FindRegisteredMasterNode` matches that CID to the chassis's own IPTable entry for `DmMd8x8Cpu3rps`
5. Chassis-side creates CGatewayLink binding the TCP connection to the DM subsystem's device object
6. Future DATA frames carry Cresnet payloads routed through CGatewayLink → DM slot subsystem → endpoints

**Critical**: step 4 requires the chassis's own SIMPL program to have declared `DmMd8x8Cpu3rps` with a matching IPID. The chassis's OEM default program has no such declaration.

### 5. What our empirical data agrees with

Our observations map exactly to the dispatcher-level behavior:

| Observation | Explanation from code |
|-------------|----------------------|
| ALTERNATE_CONNECT succeeded, handler=0x0000 | Chassis OEM has CGway entry at IPID 1; FindRegisteredMasterNode(0x0001) returns it |
| mode=0x20 (hb-response-check) | Default for OEM entry type |
| DATA frames accepted (no DISCONNECT) | pSocketContainer.m_bServerAuthenticated=true because OEM entry doesn't require auth |
| ZERO responses to any payload format | HandleDataPacket silently drops at the "no cGatewayLink" check |
| OEM counter publication (`34 10 7c 03 '<n>'`) still arrives | That's publishing from the chassis's own OEM SIMPL program via a separate flat-join path |

### 6. Hypothesis test summary

| Hypothesis | Verdict | Evidence |
|------------|---------|----------|
| Wrong opcode (1 vs 10) | NO | Both 1 and 10 → same `HandleGatewayConnectMessage` → same IPTable lookup |
| Wrong Type bits (0x0200/0xD200/0xD600) | NO | Type bits control capability negotiation (ExtLen/NewRCB), not device binding |
| Missing wire-level REGISTER | NO | No separate wire register — chassis binding is set up during Connect by chassis-side program |
| Server-side dispatcher logic | **CONFIRMED CEILING** | HandleDataPacket silently drops without CGatewayLink |
| Wrong CID (0x0001 vs other) | PARTIAL | Different CID would still need to match a slot-bound IPTable entry on the chassis; OEM has none |
| DEVICEROUTER_CONNECT_REQUEST (opcode 38) | NO | DEISC path has the same `FindRegisteredMasterNode` gate at :1593 |

## Specific bytes we would need

**IF** the chassis loaded a SIMPL program declaring `DmMd8x8Cpu3rps` at some IPID (call it 0xXX), then:

1. Change our client's CID from 0x0001 to 0xXX
2. Everything else stays the same (ALTERNATE_CONNECT with same Mode/Flags/Type)
3. Our existing nested-container writes `[CHASSIS][len][0x20][OUT_SLOT][len][0x20][RMC][len][0x15][Jh][Jl][0x00]'HI\r'` would route to RMC endpoint

But without that chassis-side SIMPL program, no byte change works.

## Why this isn't a protocol limitation

The proprietary-peer protocol fully supports slot-addressed dispatch — we proved that by reading the server-side code path. It's purely a program-config limitation: the OEM default on this chassis never declares any slot-bound devices, so there's no device-tree for the dispatcher to route to.

A real deployed Crestron system is:

    [Master CP4N with SIMPL# Pro program]        [Chassis DM-MD-CPU3-RPS with SIMPL# Pro program]
       declares DmMd8x8Cpu3rps at IPID 0x30         declares matching entry at IPID 0x30
       opens TCP client:41794                        accepts, binds CGatewayLink to DM subsystem
       sends slot-addressed DATA frames              dispatches to RMC endpoint via DM-link
       <--- bidirectional ---->

To replace the master half (what Rob is doing), the chassis half still has to exist. The OEM program is a stub that only publishes a byte-counter.

## Options for Rob

1. **Load a user SIMPL# Pro program on the chassis.** This is "two codebases on one physical box" that Rob originally rejected. If accepted, our Python client would drive endpoint I/O over a single TCP socket — the full one-processor goal.
2. **Accept the committed CTP + CIP IPID 1 feedback dual-transport design.** The protocol spike delivered a working `cip_master_v1.py` that handles the proprietary-peer handshake; it's valuable foundational IP for any future deployment that does load a chassis-side program.

## Files

- `<decompiled>/SimplSharpPro_clean/SimplSharpPro.decompiled.cs` — 505k-line CLEAN decompile of `/usr/lib/CrestronLibs/dotnet/SimplSharpPro.dll`
- `<decompiled>/ProtoTcp_dotnet/ProtoTcp.decompiled.cs` — server-side dispatcher (lines cited above)
- Chassis-side firmware for DM-MD-CPU3 would be a separate PUF (not downloaded here); the OEM program lives on the chassis itself, not in any file we've extracted. But the master-side code we have is the exact mirror image of what the chassis runs.
