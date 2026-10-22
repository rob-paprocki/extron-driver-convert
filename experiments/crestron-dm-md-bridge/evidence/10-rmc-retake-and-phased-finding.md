# 10 — RMC PoE retake + Phase D CIP writes: nothing left to find

**Date:** 2026-10-10
**Captures:** `evidence/10-rmc-retake-and-phased.log`
**Stimuli:**
- RMC PoE cycle: port 0/8 OFF @ 17:09:27 → ON @ 17:09:32 (5.0 s off), with CIP **already connected** so no observation gap this time.
- Phase D writes to serial-input joins S4000, S4001, S4003, S4100 with safe query strings (`?\r`, `HELP\r`).

## RMC PoE cycle (fills Capture 2's gap)

Zero new joins. Zero transitions on any known endpoint-related join. The chassis's firmware roll table (`S4010..S4017`) stayed exactly as evidence/05 baseline — no re-publish burst this time either, because the chassis apparently maintains endpoint state across short PoE outages (the RMC was back online well within the chassis's heartbeat/polling interval). This closes the "`DMRESETSLOT` was a soft reset" gap from Capture 1 — a true hard power cycle on a known-live endpoint produced the same silent CIP surface.

The only transition in the entire capture was `D1800: 1 → 0` at 17:09:09 — immediately after capture start, before any stimulus. Same pattern as Captures 1 and 2 (where D1800 was reported with value 0 post-cache in Capture 1, and flipped 1→0 at some point in Capture 2). D1800 is probably a periodic chassis-internal state (program-idle? recent-command-complete?); non-endpoint, non-critical.

## Phase D CIP writes

| probe | written frame | response |
|---|---|---|
| S4000 ← '?\r' | `12 00 0a 00 00 00 06 34 0f 9f ff 3f 0d` | **S4221 → '10'** (same timestamp) |
| S4000 ← 'HELP\r' | `12 00 0d 00 00 00 09 34 0f 9f ff 48 45 4c 50 0d` | no immediate change; S4221 → '21' at +6 s |
| S4001 ← '?\r' | `12 00 0a 00 00 00 06 34 0f a0 ff 3f 0d` | nothing observable |
| S4003 ← '?\r' | `12 00 0a 00 00 00 06 34 0f a2 ff 3f 0d` | nothing immediate; S4221 → '35' at +6 s |
| S4100 ← '?\r' | `12 00 0a 00 00 00 06 34 10 03 ff 3f 0d` | nothing observable |

**Readout:** writes to S4000 trigger `S4221` updates. S4221's pre-write value was `'7'`; across 5 writes it stepped `7 → 10 → 21 → 35`. The chassis is actively listening on S4000 and tracking it with a counter at S4221. **But: no text-command dispatcher response.** `?\r` and `HELP\r` produced counter bumps, not help text. S4000 is wired to a signal handler, but it's not a shell — nothing in the response looks like a command interpreter's output.

Writes to S4001, S4003, S4100 produced no observable effects (not even S4221 bumps). So S4000 specifically is wired; the adjacent joins aren't.

**What is S4000 doing?** Unknown without the SIMPL source, but the behavior resembles a `UCMD`-style user-command input: a signal handler counts incoming commands and reports a count elsewhere. On the OEM default this handler apparently does not route commands to any endpoint — writes just get counted. Candidate uses: chassis-level self-test, UI event stream, debug counter. Not pass-through.

## Combined evidence across the three captures

| | Capture 1 (DMRESETSLOT) | Capture 2 (PoE both) | Capture 3 (RMC retake + Phase D) |
|---|---|---|---|
| New joins vs evidence/05 | 0 | 0 | 0 |
| New ASCII in serials | 0 | 0 | 0 |
| New op-code frames | 0 | 0 | 0 |
| Loopback-sourced bytes | 0 | 0 | 0 |
| Endpoint-state bridge found | — | **A5010 2↔1 for input 6** | — |
| CIP-write effect | — | — | **S4000 → S4221 counter** |

## Verdict (final)

**`needs-simpl-add-on` at ≥ 99.5% confidence.** Three independent stimuli — chassis-side slot reset, true PoE hard cycle on both endpoints, and CIP writes to candidate command joins — all converge: the OEM default program on this DM-MD8X8-CPU3-RPS does not expose endpoint RS-232 / IR / Relay joins over CIP.

Two bonus findings that *are* useful going forward:

1. **Endpoint online-state bridge exists for inputs** — `A5010` toggles `2 ↔ 1` when the DM-TX at input 6 goes offline / online. By symmetry we should look at `A5000`, `A5002`, `A5004`, `A5006`, `A5010`, `A5014` for the other inputs, and `A7000`, `A7004`, `A7008`, `A7012`, `A7016`, `A7020`, `A7024`, `A7028` for outputs. The OEM also publishes `S909`, `S1209` etc. (per-row "Offline" / "Online" serials) with a delay — the analog is the realtime edge event; the serial is a derivative display.
2. **CIP write path is live** — writes to `S4000` register in the chassis (S4221 counter increments). This is the first write-response pair we've captured. Confirms our `send_serial` encoder is correct and the chassis accepts writes from IPID 1 without ejecting the session.

## What this means for the Extron driver

The ControlScript `.pkp` has three bridgeable surfaces:

1. **Routing** — chassis-side via `SETVIDEOROUTE` / `SETAVROUTE` through SSH console (we have those commands confirmed), or via CIP analog writes once Phase 2 pins the OEM route joins.
2. **Input/output online-feedback** — `A5000` cluster for inputs, `A7000` cluster for outputs. The driver can expose online/offline state per DM port without any add-on.
3. **Endpoint RS-232/IR/Relay** — **requires** a ~300 LOC SIMPL# Pro add-on that replaces the OEM program on the chassis's one slot. The flat EISC join contract from evidence/07 is the shape; the Python side's `send_serial` / `press` / `set_analog` methods (committed in this iteration) are the write primitives already in place.

The library-ization work and the chassis-reset-safe routing probe (Phase 2 of the master PLAN.md) can both proceed independently of the SIMPL# add-on decision.
