# 09 — PoE power cycle on both DM endpoints: TX cycle captured, RMC cycle gap

**Date:** 2026-10-10
**Capture:** `evidence/09-poe-cycle-capture.log` (1556 lines)
**Stimuli:** two sequential PoE off/on cycles via SSH to Netgear M4250 at `192.168.6.209`:
- Port `0/8` (DM-RMC-4K-SCALER-C @ 101.1): OFF 16:55:50 → ON 16:55:55 (5.0 s off)
- Port `0/7` (DM-TX-4K-100-C-1G @ 6.1):     OFF 16:56:55 → ON 16:57:00 (5.0 s off)

**Both endpoints had TX↔RX externally shorted on their RS-232 ports** (user-provided loopback).

## Headline

**Still no endpoint-COM traffic on CIP.** 229/229 serials, 74/74 digitals, 17/17 analogs — identical to the evidence/05 baseline set. No ASCII in any serial frame that could be a boot banner. The OEM default program does not bridge endpoint RS-232 TX/RX over CIP, even under a true hard power cycle.

## Two value transitions did show up

1. **`A5010: 2 → 1 → 2`** at `[16:56:35] 2`, `[16:56:55] 1`, `[16:57:06] 2`
   - A5010 is the Input-6 color-state analog (panel-label cluster: 2 = white/online, 1 = grey/offline).
   - Timing: `16:56:55` is PoE OFF on port 0/7 (TX). `16:57:00` is PoE ON. `16:57:06` is 6 s later — within the TX endpoint's enumeration delay.
   - **The OEM bridges endpoint online/offline state for an INPUT endpoint via an ANALOG, not a digital.** Novel: the structural analysis in evidence/06 assumed online state was captured in the per-input-row serial at `S909` ('Offline' / 'Online'). It turns out the real-time edge event is `A5010`, with the serial updating later as a side effect.

2. **`D1800: 1 → 0`** at `[16:56:47]`
   - Unknown semantic. Timing is 52 s after RMC PoE-on (and 48 s after capture connected). Could be the RMC-online indicator finally reporting, or an unrelated event. Only one transition direction observed.

## What we missed

The capture subprocess took ~66 s between orchestrator Popen and first CIP log line — probably Python startup + chassis-side TCP state lingering from Capture 1. By the time the client connected at 16:56:32, the RMC had already been powered back on for 37 s. **The RMC's off → on transition is not in this capture.** A pre-connected retake fills the gap.

## 0x38 smart-object frames (unchanged)

Same set as Capture 1: SOs `0x01`, `0x05`, `0x06`, `0x0D`, `0x10`, `0x11`, `0x12` publishing updates. Payload shape consistent — list-of-joins in little-endian pairs (`aa 0f ab 0f ...` = joins 4010, 4011, ...). No endpoint-IO smart objects.

## Loopback outcome (both endpoints)

Zero bytes made it onto CIP from either loopback. Two hypotheses remain live:

- **H1 (most likely):** The OEM never calls `.Register()` on either endpoint's ComPort, so the UARTs stay in high-Z. The loopback carries nothing because nothing drives TX.
- **H2:** The endpoints do emit boot banners, but on an internal console UART, not the external pass-through port.

Both still lead to the same conclusion: the OEM default program does not expose endpoint RS-232 via CIP.

## Verdict update

`needs-simpl-add-on`, confidence raised from ~98% → **~99%**. The retake + Phase D CIP-writes probe would move it to 99.5%+.

## Next

- **Capture 3 (retake):** connect CIP first, then cycle RMC via port 0/8. Fills the data gap.
- **Phase D:** CIP writes to candidate serial-input joins S4000/S4001/S4003/S4100 with safe query strings. Catches the "OEM has a text-command interface we haven't noticed" scenario.
