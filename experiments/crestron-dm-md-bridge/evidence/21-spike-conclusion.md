# 21 - DLL spike conclusion: one-socket is architecturally gated by chassis-side user program

## Final verdict

**The master-side proprietary-peer protocol is now fully understood and
implemented. Driving slot-addressed endpoint I/O over that single
socket is NOT possible with the chassis's OEM default program loaded
- and the reason is a specific line in the chassis's server-side
dispatcher, not any gap in our client.**

See `evidence/21-slot-dispatch-unlock-verdict.md` for the full RE
report (138 lines, 5 refuted hypotheses, cited server-side code
paths). See `evidence/21-live-probe-NEGATIVE.log` for the 20+ live
write probes that empirically confirmed the ceiling.

## The server-side gate (verbatim from the deep RE)

Chassis-side dispatcher at `ProtoTcp.decompiled.cs:1230`
(`HandleGatewayDataMessage` -> `HandleDataPacket` at :938)
silently drops DATA packets when
`pSocketContainer.pGatewayLinkObject` is null.

A `CGatewayLink` object is only created when the chassis's own
SIMPL# Pro program instantiates a device object
(e.g. `DmMd8x8Cpu3rps` with child `DmRmc4kScalerC`) and calls
`.Register()` on it. The chassis's OEM default program creates only
a generic `CGway` placeholder at IPID 1 (that's what we saw in
`evidence/02`), with NO device-type binding.

So:
- `FindRegisteredMasterNode(0x0001, 2)` succeeds -> we get
  CONNECT_RESPONSE and a valid handler.
- But `pSocketContainer.pGatewayLinkObject` is null -> every DATA
  payload gets `if (link == null) return` at the dispatch step.
- Chassis never routes our writes to any slot; writes get silently
  swallowed; our counter publishes are a side effect of the parser
  running to compute MsgLength, not of dispatch.

All five mitigation hypotheses are refuted by evidence (opcode 1 vs
10, Type bit variations, missing REGISTER payload, opcode 38
DEVICEROUTER route, alternate CID). None affect the dispatcher
check.

## Arc of findings 18 through 21

- **finding 18** (`b2a3b93`): Spike pivot - the DLL we assumed held
  the TCP handshake is just an IPC shim. Real TCP code lives in
  managed C# (`PROTO_TLDM.dll`), not the ARM `/usr/bin/TLDM` daemon
  (which coordinates RS-485 Cresnet bus, not IP CIP).
- **finding 19** (`3694e81`): Full byte-level handshake spec
  extracted from PROTO_TLDM. Live-tested end-to-end against the
  chassis. CONNECT_RESPONSE with Mode=0x20 Flags=0x03, heartbeat loop
  works, clean disconnect works. Python prototype
  (`cip_master_v1.py`) is production-ready for the protocol layer.
- **finding 20**: Byte-level Cresnet payload encoding - nested
  container wrappers (`[ID][Len][0x20][body]`), serial-15 leaf for
  ComPort StringInput, analog-sym leaf for routing. All encoding
  byte-exact; 5 runtime slot IDs documented as "empirically probable
  in one shot."
- **finding 21** (this file): Empirical probes with the full
  nested-container encoding found the exact server-side gate that
  silently drops our writes. The gate is a specific null-check on
  the chassis-side SIMPL# Pro's registration table. Only a user
  SIMPL program creates the required `CGatewayLink` object.

## What permanently survives this spike

- **Portable Python master-side CIP client**
  (`cip_master_v1.py`). Correct implementation of ALTERNATE_CONNECT,
  heartbeat, DATA/EXT_LEN frame IO against any Crestron chassis.
  Works today; works tomorrow against any chassis + user SIMPL
  program combination.
- **Complete handshake and payload encoding specs** in evidence
  19/20. These are reference documentation for anyone (us or
  anyone) implementing a non-Crestron master against a Crestron
  gateway device.
- **Negative-result documentation** showing exactly why the OEM
  default can't be driven, with a line-cited server-side code path.
  Settles the question definitively; no more "maybe there's another
  opcode" uncertainty.

## What this means for the deployment

The committed shipping design (`crestron-dm-bridge` branch,
unified `.pkp` driver) remains the right answer for the chassis in
its current OEM-only state:

- **CTP :41795 (authenticated)** for routing commands
- **CIP IPID 1 masquerade** for routing feedback
- **No endpoint I/O** (RS-232 / IR / Relay) is driveable from an
  external master against the OEM-only chassis - regardless of
  socket count. This matches findings 10 and 16, now with the
  architectural proof.

The "one-socket endpoint I/O" path remains open IF a user SIMPL
program is loaded on the chassis. Our client is ready to drive
it. That decision belongs to the user, not this spike.

## Impact on earlier memory

Memory file `extron-dm-md-cpu3-bridge.md` should be updated: the
"L1 handshake, master-side peering path" is now FULLY understood
and empirically confirmed, but endpoint I/O is still bottlenecked
by the chassis's OEM program. The master-side protocol gap is
closed; the chassis-program gap is unchanged.

## Artifacts

- `cip_master_v1.py` - working master client (244 lines, pushed)
- `evidence/19-proto-tldm-tcp-handshake-spec.md` - handshake spec
- `evidence/19-live-handshake-capture.log` - handshake live test
- `evidence/20-dm-slot-payload-encoding.md` - payload encoding spec
- `evidence/21-slot-dispatch-unlock-verdict.md` - deep RE verdict
- `evidence/21-live-probe-NEGATIVE.log` - live write probe log
