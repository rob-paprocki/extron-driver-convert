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

## What this does NOT show

- **Nothing has run on hardware.** No i20 was available to this repo. The wire
  bytes are verified against Crestron's spec offline (39 checks in
  `experiments/skeleton_i20/test_i20_wire.py`), never observed on a wire.
- **Status feedback is the weakest claim.** Crestron declares the inquiry
  *requests*; the *reply* layouts are not fully declared. They are parsed on the
  pattern Extron uses for equivalent PTZ-IP replies — an assumption, not a
  measurement, and the likeliest thing to be wrong.
- **Catalogue acceptance is still not a working driver.** Finding 12's caveat
  stands unchanged: gates 2–5 (place, build, upload, control) remain untested by
  this project. `experiments/skeleton_i20/PROTOCOL.md` is the instrument for
  measuring them.
