# Master-of-record registration: static analysis verdict

## TL;DR

**No byte change in the client's ALTERNATE_CONNECT unlocks a different
role.** A real CP4N and our Python client send identical bytes
(Mode=0x40, Flags=0x02, Type=0x0200|optional capability bits,
HostName=null). The chassis-side acceptor NEVER searches with any
DeviceIdType filter other than `2`, so no on-wire message distinguishes
"XPanel peer" from "master processor" via byte content.

Role selection is 100% baked into the chassis's IPTable at the chassis's
own startup. The chassis-side OEM program populates 29 permanent
entries at CIDs 0x0101+ with DeviceIdTypes in {2, 13, 14, 15, 16};
nothing we send changes that.

**What's actually different between us and a CP4N**: nothing on the wire
during the connect. The difference is PURELY `DestCID`: a CP4N connects
with the CID matching the chassis's INTERNAL "DmMd Switcher"
IPTable entry, then sends slot-addressed Cresnet payloads whose nested
container IDs reach the chassis's internal DM-link forwarder.

Our writes to CIDs 0x0101-0x010A (we tested all 9) with ComPort serial-15
leaves at joins 1-4000 produced no RMC loopback echoes because either:
  (a) None of the 9 CIDs IS the "DmMd Switcher" service entry.
  (b) The 9 IS one of them, but the join numbers for ComPort
      forwarding are in a specific small range we didn't fully cover.
  (c) The ComPort routes through a different CID group (0x0133-0x013A,
      0x0153-0x0159, or 0x0183-0x018A) that we haven't exhaustively
      tested with ComPort writes.

## Comparison table: CP4N vs our client ALTERNATE_CONNECT bytes

| Field       | CP4N emits                                | Our client emits   | Note |
|-------------|-------------------------------------------|--------------------|------|
| MsgType     | 0x0A (eALTERNATE_CONNECT)                 | 0x0A               | SAME |
| MsgLength   | 10 (no HostName)                          | 10                 | SAME |
| DestCID     | m_pGatewayClientIPTableEntry.CIP_ID       | our arg (0x0001..0x010A tested) | SAME code path on chassis side |
| PortNumber  | m_pGatewayClientIPTableEntry.PortNumber   | 0                  | CP4N uses non-zero only for DEISC |
| Mode        | iMode = 64 (0x40)                         | 0x40               | SAME |
| Flags       | iFlags = 2                                | 0x02               | SAME |
| Timeout     | 0                                         | 0                  | SAME |
| Type        | 0x0200 base \| 0xC000\|0x1000 if ExtLen \| 0x0400 if NewRCB | 0x0200             | We send BASE only - minor capability-advertisement difference |
| HostName    | null                                      | null (empty)       | SAME |

Source: `ProtoTcp.decompiled.cs:8517-8545` (SendTCPGatewayClientMessage,
case eALTERNATE_CONNECT) at
`<decompiled>/ProtoTcp_dotnet/ProtoTcp.decompiled.cs`

## The chassis-side acceptor only searches DeviceIdType=2

Three call sites of `FindRegisteredMasterNode(cid, filter, ref app)` in
`ProtoTcp.decompiled.cs` — all pass filter=2:

- `:902`  — `FindRegisteredMasterNode((ushort)pSocketContainer.DeviceId, 2, ref applicationId)`
- `:1594` — `FindRegisteredMasterNode(num2, 2, ref applicationId)`  (DEISC fallback)
- `:2425` — `FindRegisteredMasterNode(num2, 2, ref applicationId)`  (ALTERNATE_CONNECT fallback — the one we hit)

The chassis dispatcher has NO path that searches with filter=4 (GATEWAY),
or any other type. The `DEVICE_PARENT_GATEWAY_TYPE=4` enum from
finding 18 is used in a DIFFERENT subsystem (TLDM daemon registration,
not TCP accept).

## What the filter=2 search actually matches

`ProtoIptable.decompiled.cs:4380-4413`:

```csharp
public IPTableEntry FindRegisteredMasterNode(ushort CIP_ID, ushort deviceIdType, ref uint applicationId)
{
    ...
    if (CIP_ID < 255)
    {
        if (iPTableEntry.DeviceIdType == deviceIdType)   // STRICT ==2
            return iPTableEntry;
        continue;
    }
    ushort deviceIdType2 = iPTableEntry.DeviceIdType;
    if (deviceIdType2 == 2 || (uint)(deviceIdType2 - 13) <= 3u)   // 2, 13, 14, 15, 16
        return iPTableEntry;
    ...
}
```

So for CIDs ≥ 255 (our 0x0101+), the chassis accepts entries with
DeviceIdType in {2, 13, 14, 15, 16}. These are "lower-ranked EISC node"
(2), and types 13-16 which are related EISC-family codes.
Not GATEWAY.

The CHASSIS'S own OEM startup is what populates these 29 entries.
That startup is in the chassis's native code (Windows CE ROM, which
fork-22 established cannot be cleanly extracted) and is not visible
in our managed decompile. The entries exist at boot; we match them,
we don't create them.

## Post-handshake sequence (CP4N emits NOTHING unusual)

After ALTERNATE_CONNECT → CONNECT_RESPONSE, the CP4N's
`HandleEthernetGatewayClientProgramReadyResponseMessage` (ProtoTcp:8700)
+ connect-thread do NOT send any role-elevation message. Program flow:

- Program-ready status 0 or 1 → start timer, retry later
- Program-ready status 2 → if local IPTable entry has
  `DeviceIdType==21` (DEISC), send DEVICEROUTER_CONNECT_REQUEST
  (opcode 38); OTHERWISE send regular eALTERNATE_CONNECT with
  (Mode=64, Flags=2) — exactly what we do.

No `BuildAndSendRegisterGatewayDeviceMessage` or similar follow-up.
From this moment forward, the master is expected to send only:
heartbeats, DATA frames (opcode 5 for ≤255 payload, opcode 0x12
EXT_LEN for >255), and disconnect frames.

Source: `ProtoTcp.decompiled.cs:8700-8738` for ProgramReady handler;
`:8810+` for GatewayClientConnectThreadFunction (pure TCP connect
boilerplate, no post-connect state manipulation).

## HostName field: not a differentiator

Both CP4N (line 8538: `GATEWAY_ALTERNATE_CONNECT_MSG(... null)`) and
our client send HostName=null. The chassis's acceptor DOES store
HostName when provided (line 2372 `hostname = DataExtractor.ByteArrayToStr(gATEWAY_ALTERNATE_CONNECT_MSG.HostName)`),
but uses it ONLY in the DeviceRouter branch (line 2405
`DeviceMapEntry(... hostname ...)`), which activates only when
`DeviceRouterFunctionality.DeviceRouterInitialized == true` — i.e.
when a chassis-side feature is enabled. For a standalone DM-MD
chassis in OEM default, DeviceRouter is OFF, and HostName is unused.

## DeviceRouter branch is irrelevant for our scenario

The branch at `ProtoTcp.decompiled.cs:2402-2415` activates only when
`DeviceRouterFunctionality.DeviceRouterInitialized == true`. This is
a chassis-side pre-condition set by chassis configuration, not by any
bits the client sends. For a DM-MD chassis without DeviceRouter
configured, control goes to the else branch at `:2425`
(`FindRegisteredMasterNode(num2, 2, ref applicationId)`).

No bit the client sends in Mode/Flags/Type can route us into the
DeviceRouter branch — it's chassis-side state only.

## What CP4N actually does differently that works

In a real deployment, a CP4N's SIMPL# Pro program declares
`DmMd8x8Cpu3rps(ipid, this)` where `ipid` is a value the programmer
picks. The CP4N:

1. Creates a LOCAL IPTable entry at the given ipid (CP4N's address
   for the chassis in its local namespace).
2. On TCP connect, sends ALTERNATE_CONNECT with that same ipid as
   DestCID.
3. The chassis looks up that ipid in its OWN IPTable.
4. **For this to succeed, the chassis's IPTable must have an entry
   at that ipid with DeviceIdType ∈ {2, 13, 14, 15, 16}.**

Case A: `ipid < 255`. The chassis's OEM program must have populated
IPID in 1-254 range at boot with DeviceIdType=2. OEM default for
DM-MD-CPU3-RPS does NOT populate these — we confirmed by sweep that
no CID in 0x0001-0x00FE is valid post-factory-reset.

Case B: `ipid >= 255`. The chassis's 29 permanent entries at
0x0101-0x018A are the candidates. CP4N can connect to any of these.

**So real CP4N → DM-MD deployments use ipid >= 255, matching one of
the 29 chassis entries.** The SIMPL# Pro programmer picks the specific
CID that corresponds to the chassis's "DmMd Switcher" service entry.

That specific CID is NOT visible from the managed decompile because
the chassis's OEM startup code (which assigns these entries) is in
native CE ROM.

## What this means practically for the parent

- Our ALTERNATE_CONNECT handshake is correct byte-for-byte.
- The 29 chassis IPTable entries ARE the only addressable targets.
- Writing to each entry has NOT produced an RMC loopback. Reasons
  possible:
  - (highest likelihood) The 29 CIDs include slots for different
    chassis-internal services (routing matrix, FPGA module, system
    config, UI). Only ONE or a SUBSET is the "DmMd Switcher" that
    forwards to DM-link. We haven't identified which.
  - The join numbers for ComPort StringInput are in the chassis's
    private internal namespace — probably much smaller than the join
    numbers we tested (we tried 1-4000; the real join could be a
    very specific value like 7, 23, 29, or similar).
  - The payload leaf type may need to be something other than
    serial-15 (0x15) — perhaps serial-34 (0x34) which has a
    different wire format.

- **No definitive byte change exists** to switch role from
  "DeviceIdType=2 peer" to a GATEWAY master. Role is 100% chassis-
  side state.

## Recommended empirical next move for the parent

Pick CID 0x0101 (likely the chassis's main-switch entry), connect,
send the FULL CGway state-tree UpdateRequest `[0x03, 0x04]` *and*
compare the response byte-pattern against the per-CID response from
each of the other 28 CIDs. The CID whose response-pattern uniquely
differs is likely the "DmMd Switcher" entry. Then enumerate joins
systematically in the small range (1-100) for serial-type leaves of
BOTH 0x15 and 0x34. The RMC's ComPort.StringInput join is almost
certainly in that small range on that specific CID.

If none of that works, the honest answer is that we need to pcap a
real CP4N → chassis connect to see which CID it uses.

## Files cited

- `<decompiled>/ProtoTcp_dotnet/ProtoTcp.decompiled.cs` — chassis dispatcher (:902, :1594, :2425, :2402-2415, :2649) + CP4N client send (:8517-8545, :8700-8738, :8810+)
- `<decompiled>/ProtoIptable_dotnet/ProtoIptable.decompiled.cs:4380-4413` — FindRegisteredMasterNode filter semantics
- `<decompiled>/ProtoTldm_dotnet/ProtoTldm.decompiled.cs:2054-2204` — DetermineDynamicType (shows DeviceIdType values 2, 18, 19)
- `<decompiled>/SimplSharpPro_clean/SimplSharpPro.decompiled.cs:96891-96948` — GenericDevice.Register() just delegates to SIMPLDeviceImplementation (no on-wire action)
- `<decompiled>/SimplSharpPro_clean/SimplSharpPro.decompiled.cs:207600+` — Switch (DmMd container) class is control-flow obfuscated, no clear role-identifying code visible
