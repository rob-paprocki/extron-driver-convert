# Finding 13 — synthesising a Crestron-device driver for an Extron processor

**Status: built and verified offline; UNVERIFIED on hardware.** 2026-09-08.

This is the first finding in the **Crestron device → Extron processor**
direction. Findings 04 and 06 went the other way, and STATUS.md's open items 1
and 2 (does an outsider-built `.pkg` load; Crestron's licence position) do not
apply here: the target is Extron's free-account platform, and the Crestron-side
material is read, never emitted.

Everything below is measured except the hardware behaviour, which is
explicitly not.

## 1. The i20's headline features are reserved preset numbers

This is the result that changed the shape of the work.

The IV-CAM-i20's auto-switching and framing — the features with no counterpart
in any Extron 1 Beyond driver — are not new opcodes. Resolving Crestron's
Template chain to literals (`experiments/skeleton_i20/resolve_visca.py`) shows
they are ordinary VISCA preset recalls on reserved preset numbers:

| feature | wire |
|---|---|
| StartTrackingFraming | `81 01 04 3F 02 50 FF` |
| StopTrackingFraming | `81 01 04 3F 02 51 FF` |
| EnableGroupTracking | `81 01 04 3F 02 52 FF` |
| EnablePresenterTracking | `81 01 04 3F 02 53 FF` |
| Menu | `81 01 04 3F 02 5F FF` |
| Reboot | `81 01 04 3F 02 63 FF` |

So the protocol machinery an Extron driver needs in order to drive them is
machinery it already has. A driver that can recall a preset can start presenter
tracking. **The gap between the two vendors' camera drivers is a gap in exposed
capability, not in protocol reach.**

All 82 commands resolve with **0 unresolved** — see
`experiments/skeleton_i20/i20_wire_table.txt`.

## 2. Cross-vendor corroboration, without a Crestron processor

Finding 05 established that two vendors independently encoding the same device
produce the same bytes. That check needed both implementations *running*. Here
neither vendor's processor was available, and the check still worked, because
Extron ships its own 1 Beyond camera drivers (class 19: `1bynd_19_4743`
PTZ-IP12/IP20, `1bynd_19_4741` AutoTracker3) with both `.pkp` and ControlScript
halves.

Comparing Extron's implementation against Crestron's declarative spec:

| | Crestron (declared) | Extron (implemented) |
|---|---|---|
| exposure mode | `81 01 04 39 {mode} FF` | `pack('>6B', DeviceID, 0x01, 0x04, 0x39, v, 0xFF)` |
| mode values | comment: `Full Auto = 0x00, Manual = 0x03, Shutter Priority = 0x0a, Iris Priority = 0x0b` | `'Full Auto': 0x00, 'Manual': 0x03, 'Shutter Priority': 0x0A, 'Iris Priority': 0x0B` |
| power | `MapBooleanToViscaOnOff` → `true: 0x02, false: 0x03` | `'On': 0x02, 'Off': 0x03` |
| address | `ViscaAddressToHeader`: "add 128 (0x80)" | `self.DeviceID = 0x80 + int(value)` |

Identical bytes **and** identical value tables. This is finding 05's claim
reproduced on different hardware by a cheaper method — a spec refereeing an
implementation (finding 11's shape) rather than two implementations refereeing
each other.

One asymmetry worth recording: Crestron *documents* four exposure modes in its
own comment but its `Map` exposes only a boolean (Full Auto / Manual). Extron
exposes five, including `Bright = 0x0D`. **On this command the vendor with 16
commands is richer than the vendor with 82.** Command count is not capability.

## 3. Extron's shipped 1 Beyond drivers discard the zoom speed

`_cmd_SetZoom` in `1bynd_19_4743` computes the combined direction+speed byte and
then transmits the direction constant instead:

```python
if 0 <= speed <= 7 and value in ValueStateValues:
    if value == 'Stop':
        speed = 0x00
    else:
        speed += ValueStateValues[value]          # 0x20|speed or 0x30|speed

    ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07,
                         ValueStateValues[value],  # <-- `speed` is discarded
                         0xFF)
```

`speed` is dead. Every zoom runs at speed 0 regardless of the Zoom Speed
qualifier. The same defect is present in the standalone ControlScript module
`onebynd_camera_AutoTracker_3_v1_0_1_1.py`, so it is systematic across Extron's
1 Beyond camera drivers rather than a one-file slip.

Crestron encodes the same command as a single `{SpeedAndDirection}` byte
(`81 01 04 07 {SpeedAndDirection} FF`) and is correct.

This is the reverse of finding 10's `LogoAssignment` result, where Extron's own
bug had to be reproduced for the wire table to match. Here the bug is in the
donor we are deriving from, and the derived driver **deliberately diverges** —
recorded as `[PATCH E2]` in the generated source, and step 3 of the hardware
protocol is designed to confirm it on a real camera.

## 4. Transplant, and what it does and does not establish

`tools/pkp_build.py` builds a package by substituting content into a real donor.
It refuses to emit unless the *unmodified* donor first round-trips
byte-for-byte — we prove we understood the graph before we are allowed to change
it, and there is no bypass flag.

Measured (`tools/test_pkp_build.py`, 36 checks):

- all **9** sample packages round-trip byte-identically, including the 16 MB Tesira
- substitution of a **different length** works in both directions (37,201 → 54,845
  bytes, and a 50 KB growth test). Confirms nrbf_write.py's claim that NRBF
  carries no absolute-offset pointers, which its own tests did not exercise
- re-parsing the output shows **exactly one object changed**, and it is the
  script's content array

The 1 Beyond camera donor is also **1,426 objects** against the Automate VX's
43,030 — a graph small enough that from-scratch synthesis (open item 4) becomes
a tractable next step rather than an aspiration.

## 5. A runtime property a from-scratch emitter needs to know

The embedded driver imports only `BaseDriver`, `time` and `struct.pack`, yet
uses `ExtronTime` **7 times as a bare name**. The GC runtime populates the
module globals beyond the driver's own import list. Static analysis of these
drivers will therefore report false undefined-name errors, and a synthesised
driver may rely on the same injection.

## 6. The lightbar packing is derivable, and the docs corroborate the presets

`SetIndicatorLight` is declared by Crestron's driver as `{Header} c1 {LedBar} FF`
with `{LedBar}` opaque. The documentation supplies the packing: four payload
bytes, one per lightbar segment, each byte `(brightness << 2) | colour` with
brightness `00` off / `01` dim / `10` medium / `11` bright and colour `00` green
/ `01` red / `11` yellow (`10` undefined).

Half width keeps the two **outer** segments' colour bits while setting their
brightness to zero — which is why half-yellow is `03 0F 0F 03` and not
`00 0F 0F 00`. That single rule reproduces **all 19 command strings** printed in
the documentation, including the four fixed status colours, which turn out not
to be a separate encoding at all. `test_i20_wire.py` asserts every one.

The Reserved-Presets page also **independently corroborates finding 1 above**,
in decimal where the driver used hex: 80/81 start/pause tracking, 82 group
tracking, 95 OSD menu, 99 reboot — matching `0x50`, `0x51`, `0x52`, `0x5F`,
`0x63` exactly. Two sources, derived from different artefacts, agreeing.

It also adds presets the driver left unspecified: 0 Home Shot, 1 Tracking Shot,
101–104 Preset Zone 1–4, 105–108 Tracking Profile 1–4. Crestron's driver
declares `SetTrackingFramingProfile` as a preset recall but supplies no preset
value; the documentation is where that value lives.

## 7. Docs and implementation disagree on exactly one byte

Preset **83** (`0x53`):

| source | name |
|---|---|
| Crestron's IV-CAM-I20 driver | `EnablePresenterTracking` |
| Crestron's Reserved-Presets page | **Pause Group Tracking** |

Five of the six shared reserved presets agree exactly; this is the only one that
does not. Both readings emit the same byte, so the driver is correct either way
— what is wrong is one of the two labels, and a user pressing a control named
"Presenter Tracking" may be pausing group tracking instead.

Not resolved here, and deliberately not guessed. `PROTOCOL.md` section T3b is a
three-step sequence that settles it on hardware.

## 8. The status-feedback caveat was a real defect

Finding 13's first draft said status feedback was "provisional". It was worse
than that: `_cmd_UpdateTrackingFraming` parsed the reply as
`'Start' if res[2] else 'Stop'`, and since the documented payloads are `0x02`
and `0x03` — both truthy — it reported `Start` unconditionally. The camera could
never have reported tracking as stopped.

The reply layout *is* documented (`CAM_TrackingInq`: `y0 50 02 FF` active,
`y0 50 03 FF` paused, VISCA's usual on/off convention). It now maps explicitly
and raises on any payload the documentation does not define, rather than
defaulting.

The general lesson is the one already in STATUS.md's methodology notes, arriving
from a new direction: **a guess that scores well is worse than a recorded gap.**
This one passed every offline check the suite had, because the suite only tested
requests. It took writing the reply test to expose it.

## What this does NOT show

- **Nothing has run on hardware.** No i20 was available to this repo. The wire
  bytes are verified against Crestron's spec offline (39 checks in
  `experiments/skeleton_i20/test_i20_wire.py`), never observed on a wire.
- **Three reply layouts are still inferred.** `TrackingFraming` and
  `CameraConnectionStatus` now parse documented layouts. `CameraOutput` does not:
  the documentation says "see below" for that reply and then prints nothing.
  `ZoomPosition` and `PanTiltAngle` nibble layouts follow the general VISCA
  pattern rather than a printed one. Those three are where polling should be
  expected to break.
- **Catalogue acceptance is still not a working driver.** Finding 12's caveat
  stands unchanged: gates 2–5 (place, build, upload, control) remain untested by
  this project. `experiments/skeleton_i20/PROTOCOL.md` is the instrument for
  measuring them.
