# 23 - Spike final state: protocol complete, endpoint I/O blocked

## Final verdict

The master-side proprietary-peer protocol is fully specified and
empirically validated. Driving endpoint I/O (RMC ComPort, IR, Relay)
over that single socket is NOT achievable with the chassis's OEM
default program loaded, confirmed empirically across every reasonable
hypothesis.

## What we have (permanently valuable)

- Full byte-level protocol spec: handshake, framing, heartbeat,
  DATA/EXT_LEN, auth (evidence/19).
- Full nested-container Cresnet payload encoding spec (evidence/20).
- Working Python master client `cip_master_v1.py` - 244 lines,
  tested live against this chassis, speaks the protocol end-to-end.
- Map of 29 permanent chassis IPTable entries at specific CIDs
  (evidence/22-cid-sweep-and-slot-response-capture.log).
- Chassis-side firmware architecture understood: Windows CE XIP ROM
  running the same managed PROTO_* assemblies as the CP4N master
  (evidence/22).
- Server-side dispatcher logic reverse-engineered: the chassis
  always calls `FindRegisteredMasterNode(cid, 2, ...)` with filter
  type 2; no alternate role-elevation path exists for peer clients
  (evidence/23-master-of-record-registration.md).

## What empirically did not work (comprehensively tested)

- 420 ComPort StringInput writes to RMC[101].ComPort[1]
  across 7 representative CIDs x 2 leaf types (serial-15, serial-34)
  x 30 join numbers. Zero PING loopback echoes.
- All 29 slot-dispatch CIDs give fingerprint-identical responses
  split into just 2 groups. No "unique DmMd endpoint dispatcher"
  CID distinguishes itself from the fingerprint data.
- CP4N client sends BYTE-IDENTICAL ALTERNATE_CONNECT to what our
  client sends (fork-23 analysis of SimplSharpPro.dll). No
  additional post-handshake role-elevation message exists.

## Final architectural interpretation

The chassis's OEM default program on `DM-MD-CPU3-RPS` firmware
`v1.8001.*` publishes WebUI-level state (input/output labels, menu
items, byte-counter) via a dynamically-allocated CGway at IPID 1,
and exposes 29 permanent slot-status reporter services at specific
CIDs. It does NOT dispatch slot-addressed writes to the actual
DM-link endpoint stack regardless of the handshake variant used.

That DM-link dispatch role is reserved for a Crestron master
processor (CP3-series or CP4-series) that connects to the chassis
with specific state established during its SIMPL# Pro boot
sequence - state we have not been able to replicate from static
analysis of its managed assemblies. The CP4N master emits
byte-identical frames to what we emit, suggesting the role
differentiation is chassis-side state that gets created by
operator-level actions (loading a SIMPL# Pro program on the master
CP4N) that we cannot trigger from outside.

## What this means for deployment

- The committed shipping design (branch `crestron-dm-bridge`,
  unified `.pkp` driver: CTP :41795 authenticated for routing +
  CIP IPID 1 masquerade for routing feedback) is unchanged and
  remains the correct shipping answer.
- One-socket operation for routing alone can be achieved today via
  pure-CIP (IPID 1 masquerade works, we proved this long ago).
- One-socket operation that INCLUDES endpoint I/O remains blocked
  on either (a) a physical CP4N on the LAN that we can pcap
  during legitimate chassis registration, or (b) a vendor-level
  understanding of the chassis's internal IPTable state the OEM
  firmware creates when CP4N registration begins.

## Permanently open follow-up (if a CP4N becomes available)

A single 10-second pcap of a real CP4N connecting to this
chassis would reveal exactly what distinguishes a legitimate
master-of-record session from our peer session. That pcap
would complete the spike. Without it, static analysis of the
managed decompile has reached its ceiling: the client code is
byte-identical, meaning the difference must be in chassis state
that gets established by vendor-specific registration not visible
in the managed layer.

## Deprecation notes

- Finding 21's "load a user SIMPL program on the chassis" path is
  withdrawn. The chassis is not a programmable processor; user
  programs load on CP3/CP4-series master processors, not on the
  chassis itself. Finding 21's `pGatewayLinkObject` null-check
  interpretation also had the direction wrong (that gate is in
  CP4N master code, not chassis acceptor code), noted inline.
- Finding 17's "endpoint-side peering blocked by topology" stands
  as correct for that specific test.

## Artifacts added in this session

- `evidence/22-chassis-firmware-extract.md` - CP3 .cos format study
- `evidence/22-chassis-state-tree-dump.log` - 582-payload capture
  from CGway (pre-reset)
- `evidence/22-cid-sweep-and-slot-response-capture.log` - DestCID
  sweep + fingerprint results
- `evidence/23-master-of-record-registration.md` - deep RE of
  what distinguishes CP4N role vs our role (answer: nothing on
  the client side, everything is chassis state)
- `evidence/23-live-sweep-NEGATIVE.log` - final write sweep summary
- `evidence/23-spike-final-state.md` - this file
