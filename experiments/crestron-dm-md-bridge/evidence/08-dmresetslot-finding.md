# 08 — DMRESETSLOT 101 forces chassis re-sync, exposes no endpoint-COM joins

**Date:** 2026-10-10
**Capture:** `evidence/08-dmresetslot-101-capture.log` (1704 lines)
**Stimulus:** SSH `DMRESETSLOT 101` fired at `16:26:59`, 20 s into a 180 s CIP capture against chassis `192.168.6.14` as IPID 1 with `--log-all-frames`.
**Hardware setup:** DM-RMC-4K-SCALER-C at output `101.1` with its RS-232 port TX↔RX externally shorted (user-provided loopback). Chassis in OEM default program (no user SIMPL loaded).

## Headline

**No new endpoint-IO joins. No ASCII boot banner. No COM-shaped traffic.** The chassis sees the endpoint drop and come back (`S4016` firmware-roll row for the RMC is re-pushed at 16:27:01), but its CIP surface stays within the already-known OEM join set: outputs `S1200–1295`, system `S3xxx`, labels `S5xxx`/`S7xxx`, firmware roll `S4010–4019`, smart-object events `0x38`.

## Pre vs post-trigger counts

| | pre (0:00–0:20) | post (0:20–3:00) |
|---|---|---|
| frames | 184 | 476 |
| op=0x05 (digital/analog/admin) | 92 | 23 |
| op=0x12 (serial) | 92 | 441 |
| digital updates | 73 | 2 |
| analog updates | 17 | 0 |
| serial updates | 92 | 149 |
| op=0x0E (periodic chassis frames, 15–16 s interval) | 0 | 12 |

The post-trigger surge is a full OEM-state re-publish — 137 of 149 post-trigger serial updates are joins we already saw in the initial-cache dump (evidence/05), being pushed again. No value changed.

Only one truly new digital join appeared: `D1800 = 0`. Doesn't fit any obvious endpoint-IO pattern; worth a note, not a lead.

## Smart-object events observed

The chassis also published a flurry of `0x38`-marker frames post-trigger — undocumented in evidence/06, now partially decoded:

```
00 00 LL 38 00 00 00 SO_ID <SO-specific payload>
```

Smart objects seen: `0x01` (top-level menu), `0x05`, `0x06` (input/output pickers), `0x0D` (single-input picker), `0x10`, `0x11`, `0x12` (EDID dropdowns per the earlier research). The ~65-byte payloads list joins in little-endian pairs — e.g. `aa 0f ab 0f ac 0f ...` = joins 4010, 4011, 4012, ... (the firmware-roll table ranges).

**None of the SOs enumerate endpoint-IO joins.** The SO menu is still `{Inputs, Outputs, Ethernet, System Overview, Password, Naming, System}` — no COM/IR/Relay tab.

## Why the loopback didn't help here

Three possible reasons the TX↔RX loopback on the DM-RMC's RS-232 produced no observable CIP traffic:

1. **UART never powered.** The OEM default program does not call `.Register()` on the endpoint's ComPort, so the RMC's UART stays in high-Z. Loopback carries nothing because nothing drives TX. This is the hypothesis the SIMPL# research backed.
2. **No boot banner on the pass-through port.** Even if the UART is enabled, the RMC may print its boot banner on a separate internal console UART, not on the external DB9 pass-through — in which case replug or hard reset would still produce no bytes on the pass-through TX.
3. **`DMRESETSLOT` is a soft reset.** The command resets the chassis's output card controller, not the attached endpoint — the RMC may not actually have power-cycled. A hard PoDM/PoE cycle would decisively test this (Capture 2 below).

(1) and (2) both still land at "OEM doesn't bridge endpoint COM via CIP". (3) is the only way DMRESETSLOT could give a false negative; Capture 2 closes that door.

## Open: Capture 2 — true PoE power cycle

Next: cut PoE on the switch port feeding the output endpoint (hard power cycle), re-capture with `--log-all-frames`, diff against Capture 1. If still no COM-shaped traffic appears, verdict is confirmed to ≥99%.

Secondary probe during the same window: HDMI HPD toggle at the RMC's output. Catches any HDMI-feedback bridging that the OEM might offer.

## Verdict (unchanged)

`needs-simpl-add-on` — the OEM default program on this DM-MD8X8-CPU3-RPS does not expose endpoint RS-232 / IR / Relay joins on CIP. Confidence raised from 95% to **~98%** by Capture 1; pending Capture 2 for 99%.
