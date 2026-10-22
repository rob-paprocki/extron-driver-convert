# Crestron DM-MD8X8-CPU3-RPS XPanel masquerade - PLAN

Experiment to let an Extron IPL Pro drive an existing Crestron
DM-MD8X8-CPU3-RPS chassis + its DM endpoints by registering as a CIP peer
that behaves like the chassis stock OEM XPanel.

Status: Phase 1 complete on the read side; route write-side is next.

## Update 2026-10-09

- Chassis moved to **192.168.6.14** (programmed IP in SIMPL is still 172.16.0.104 — see `S3002` in the cache dump; the live IP changed via static override or DHCP).
- Dev laptop at **192.168.6.114/24** reaches it on both 22 and 41794.
- `cip_proof_of_connect.py --host 192.168.6.14 --ipid 1 --hold 10` ran end-to-end: handshake, registration, 320-join initial cache (74 D, 17 A, 229 S), end-of-query ack, heartbeat, clean shutdown. Full capture in `evidence/05-cip-signal-cache-dump.txt`; structural analysis in `evidence/06-oem-discovered-joinmap.md`.
- **The OEM default program's join numbering is not the Pepperdash scheme.** Routing is NOT on `A101..A108`. The chassis publishes a serial-heavy map centered on `S900..S979` (inputs), `S1200..S1295` (outputs), `S3xxx` (system), `S4xxx` (command dispatch + endpoint firmware roll), `S5xxx` / `S7xxx` (front-panel labels). The actual route-feedback joins were not captured because initial-state only sends non-zero values and nothing was being driven. Phase 2 drives one route via SSH `DMROUTE` and diffs the capture to pin those joins.
- IP table slot caveat: `ADDS` creates a `CGway` entry, which the chassis refuses CIP registration against (`ff ff 02 = IPID not defined`). `ADDPEER` adds a Master-list Gway but requires a program restart. The only live `Gway` slot is IPID 1 (the OEM-defined XPanel slot). We use IPID 1 opportunistically — fine while the human XPanel is OFFLINE (which is the live state; the OEM default binds IPID 1 to 127.0.0.1 as a placeholder).

## Context (verified 2026-10-07/08)

- Chassis DM-MD8X8-CPU3-RPS fw v1.8001.5769.27432 (Oct 18 2024) @ 172.16.0.104 (now 192.168.6.14).
- Dev laptop reaches chassis on Ethernet 2 = 172.16.0.102/16 (now 192.168.6.114/24).
- SSH console: admin / blank password + Enter past terms. Paramiko works.
- No user SIMPL program loaded - live behavior is the chassis OEM firmware
  program at slot 0 (reachable as /cwsprogram0/ on CWS).
- IP table has one row: CIP_ID=1, Gway, 127.0.0.1, OFFLINE - the slot the stock
  XPanel is wired to. The .c3p XPanel confirms it uses IPID=1 targeting
  172.16.0.104:41794 plain CIP (SSL off).
- CIP_IDs 2 through FE are free.
- Only pass-through endpoint attached: DM-RMC-4K-SCALER-C at output 101. Also
  6.1 (DM-TX-4K-100-C-1G) and 8.1 (DM-TX-201-C) are input TXes.

Raw: evidence/01-chassis-fingerprint.md, evidence/02-xpanel-config.md,
evidence/03-oem-joins-report.md, evidence/04-cip-protocol-report.md,
evidence/05-cip-signal-cache-dump.txt, evidence/06-oem-discovered-joinmap.md.

## Confirmed facts

### CIP wire protocol
Established by four independent OSS implementations cross-cited with
rdriscoll reference server. Full detail in PROTOCOL.md. **End-to-end
exercised against the live chassis 2026-10-09**: see `evidence/05`.

- Transport: TCP 41794 (plain, no SSL on this chassis).
- Framing: [type:1][length:2 BE][payload].
- Handshake:
  1. Chassis sends 0F 00 01 02 on TCP accept (program-ready).
  2. Client replies 14-byte registration:
     01 00 0B 00 00 00 00 00 <ipid> 40 FF FF F1 01.
  3. Chassis acks 02 00 04 00 00 00 1F on success
     (or 02 00 03 FF FF 02 if the IPID is not defined).
  4. Client sends update request 05 00 05 00 00 02 03 00.
  5. Chassis streams initial signal cache (0x05 + 0x12 frames).
  6. Chassis terminates with 05 00 05 00 00 02 03 1C (end-of-query).
  7. Client acks 05 00 05 00 00 02 03 1D, then begins 15-s heartbeat
     0D 00 02 00 00.

### SIMPL# Pro class
Crestron.SimplSharpPro.DM.DmMd8x8Cpu3rps for our chassis. Constructor
new DmMd8x8Cpu3rps(ipid, Global.ControlSystem). Confirmed in Pepperdash
DmChassisController.cs case statement.

### Join map (OEM default program — authoritative for this chassis)

See `evidence/06-oem-discovered-joinmap.md`. The Pepperdash joins
(`A101..A108` video, `A301..A308` audio) **do not apply** to the live
default program; they stay in the repo as the fallback target if a
user-authored EISC bridge is ever installed on this chassis.

OEM clusters discovered 2026-10-09:

- Inputs: `S900..S979`, stride 10. Row columns: `S*0`=number, `S*1`=name+card, `S*6`=HDCP, `S*9`=sync.
- Outputs: `S1200..S1295`, stride 12. Row columns: `S*0`=number, `S*1`=name, `S*2`=card, `S*6`=HDCP, `S*9`=sync, `S*11`=endpoint FW.
- System: `S3000..S3023` (power, IP, subnet, gateway, MAC, hostname).
- Endpoints: `S4010..S4019` (live firmware inventory row-per-endpoint).
- Front-panel labels: `S5000..S5015` (inputs), `S7000..S7031` (outputs), HTML-colored.
- Command result: `S4019` = 'Command completed.'
- Routing readback: not yet pinned (zero-valued at capture; needs Phase 2 drive-and-diff).

### Caveats
1. CPU3 removed per-card management from SIMPL. The chassis uses DMTool, not
   the SIMPL program, for input/output card config. Our bridge can route and
   read feedback, but not edit card bindings.
2. The Pepperdash join map was for an EISC bridge in a USER program; the OEM
   default program on this chassis uses the discovered map above (evidence/06).
   Three ways we considered to confirm, done or deferred:
   (a) ✅ passive CIP registration against IPID 1 + initial-cache dump — DONE 2026-10-09.
   (b) pktmon capture while the stock XPanel is driven live — deferred (not needed; CIP dump is cleaner).
   (c) decompile the .c3p SWFs with JPEXS/FFDec — deferred.
3. Concurrent registration on the same IPID: NOT confirmed on this firmware.
   The OEM default binds IPID 1 to 127.0.0.1 (placeholder), so the slot is
   effectively unused and our masquerade works. Behavior under a live human
   XPanel is unverified and may evict one side.
4. digitalmedia_3.04.16.puf is NOT our chassis firmware - targets non-CPU3
   DM-MDs. Nothing to mine there.

## Workstreams

### Phase 1 - CIP baseline bring-up ✅ DONE 2026-10-09

Script: cip_proof_of_connect.py.

1. ✅ Open TCP to 192.168.6.14:41794 from 192.168.6.114.
2. ✅ Accept the 0F 00 01 02 program-ready frame.
3. ✅ Send registration for a chosen IPID (default 3; --ipid 1 reuses the stock
   XPanel slot).
4. ✅ Confirm success 02 ... 1F.
5. ✅ Send update request 05 00 05 00 00 02 03 00.
6. ✅ Receive and decode initial signal cache; log every join + value (320 joins).
7. ✅ End-of-query ack + first heartbeat.
8. ✅ Hold the connection 10 s to prove feedback flows, then clean shutdown.

Pass/fail: ✅ 320 joins observed in initial cache (74 D, 17 A, 229 S), end-of-query acknowledged, clean shutdown.

### Phase 2 - Drive-and-diff to pin routing joins (next)

Open a long-held CIP capture (`--hold 60`). From a second SSH shell, issue
`DMROUTE` (or whatever the actual DM route console command is on this fw —
check `HELP DMROUTE` first) to send input 1 to output 1, then input 2 to
output 1, etc. Diff each resulting cache delta against the baseline from
Phase 1. Routing-feedback analog(s) and any digital edge triggers will fall
out of the diff.

Also drive a route by *writing* a digital/analog from the CIP side (one of
the D1013..D1020 or D1313..D1320 clusters, which look like matrix buttons)
and verify the chassis actually routes. If none of those work, fall back
to writing the serial `S4000` (the command-queue slot) with a text command
like `ROUTE 1 1`. One of these paths is almost certainly how the stock
XPanel drives routing.

Deliverable: `evidence/07-routing-join-pin.md` with the proven write path.

### Phase 3 - CIP client in extronlib

Pure extronlib Python (no third-party). Reuse the state machine from the
Phase 1 script, adapt to EthernetClientInterface.ReceiveData callbacks instead
of raw sockets. Pieces: cip_client.py, cip_state.py, joins.py, driver.py.

### Phase 4 - Package as .pkp

Use existing project tooling (tools/pkp_build.py, tools/pkp_asset.py,
tools/pkp_validate.py). Pick a donor similar in shape (a Samsung LFD or similar
text-TCP driver). Expose command surface:

- ROUTE_AV in,out / ROUTE_V in,out / ROUTE_A in,out / BREAK out
- STATUS (passive)
- EP101_COM_SEND / EP101_CEC_SEND / EP101_IR_SEND / EP101_DISPLAY_POWER
  (contingent on Phase 2 confirming endpoint joins exist in the OEM program;
  otherwise we add them with a tiny SIMPL# Pro helper).

### Phase 5 - Finding writeup

findings/19-crestron-dm-md-bridge.md.

## Non-goals / risks

- Not writing a universal CIP library. Just enough to drive this chassis.
- If OEM joins differ from Pepperdash more than slightly, we re-pin from the
  pktmon capture - expect a day of label-and-verify.
- If the OEM program exposes no endpoint joins at all (purely matrix), we
  write a small SIMPL# Pro add-on. Research confirmed DmMd8x8Cpu3rps + the
  DmRmc* endpoint classes are the right stack for that fallback.
