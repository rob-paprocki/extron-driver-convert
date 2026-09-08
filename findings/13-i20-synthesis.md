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

The transport agrees too, and more interestingly than a matching value would
suggest. Both vendors name **TCP port 5500** — Crestron in its driver
(`{"Name": "TcpTransport", "Type": "Tcp", "Info": {"Port": 5500}}`, identical on
i20 and p20) and in its VISCA documentation ("By default, the port for TCP
control is set to 5500"); Extron in its driver header ("Manufacturer confirmed
ethernet control uses UDP port 5500").

Note what each says about the *protocol*. Both initially documented UDP, and
Extron's revision `1_0_1` corrected it — "Changed ethernet to TCP based on
testing. DR# 62249". Crestron ships TCP. So the two vendors did not merely
arrive at the same answer; **they made and corrected the same mistake**, which
is the finding-05 pattern applied to a transport rather than a command.

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
- substitution of a **different length** works in both directions (37,201 → 68,285
  bytes, and a 50 KB growth test). Confirms nrbf_write.py's claim that NRBF
  carries no absolute-offset pointers, which its own tests did not exercise
- re-parsing the output shows **exactly one object changed**, and it is the
  script's content array

The 1 Beyond camera donor is also **1,426 objects** against the Automate VX's
43,030 — a graph small enough that from-scratch synthesis (open item 4) becomes
a tractable next step rather than an aspiration.

## 4b. The `.pkp` pins the transport, and often locks it

A `.pkp` does not leave the connection to the installer. `EthernetProtocolAsset`
carries the address, the port, the ethernet type, and a flag saying whether the
field may be edited in Global Configurator at all:

```
_port              5500
_canEditPort       False            <- greyed out in GC
_protocolSubType   EthernetTypeEnum = 0
_address           192.168.254.254
```

**The transport is carried by `ProtocolCompatibilityFlags`, not by
`EthernetTypeEnum`.** `_protocolSubType` is `0` in *every* package in
`samples/` — including one that is definitively UDP — so it encodes something
else and cannot be read as TCP-vs-UDP.

*(An earlier revision of this finding claimed `EthernetTypeEnum 0 = TCP`,
"measured". It was not: the survey behind it stopped at the first ethernet
asset per package and never looked at a UDP device. The claim was consistent
with every sample precisely because the field is constant. A constant field
agreeing with a hypothesis is not evidence for it — recorded here because
STATUS.md's methodology notes exist for exactly this error.)*

`_compatibility` does discriminate:

| flag | packages | protocol |
|---|---|---|
| **16** | both 1 Beyond cameras, port 5500 | **TCP** |
| **32** | both ClockAudio, port 49494 | **UDP** |
| 64 | Automate VX (4443), Samsung (1516) | **not determined** |
| 512 | Extron (22023), Biamp Tesira (22) | **not determined** |

The ClockAudio evidence is direct rather than inferred: its supported model is
named `CDT 100-UDP`, and its driver header carries "UDP port number is based on
the information provided by the…" plus a revision note "Added comm sheet notes
regarding UDP connection."

A second, corroborating marker: **`_udpOutputPort` is non-zero only on the UDP
packages**, where it mirrors `_port` (49494). Every TCP package leaves it `0`.

`64` and `512` are left as *not determined* rather than guessed. Both cover
devices that are certainly TCP (HTTPS on 4443, SSH on 22), so the field is
plainly finer-grained than a two-way transport switch — but no sample here
settles what it distinguishes.

Ports and lock state across the sample set:

| package | port | `_canEditPort` |
|---|---|---|
| `1bynd_19_4743` PTZ-IP12/20 (our donor) | 5500 | **False** |
| `1bynd_19_4741` AutoTracker3 | 5500 | True |
| `1bynd_42_4279` Automate VX | 4443 | True |
| `clau_25_5940` | 49494 | **False** |
| `clau_25_1777` | 49494 | True |
| `extr_17_17677`, `extr_15_17578` | 22023 | **False** |
| `smsg_10_6738` | 1516 | **False** |
| `biam_25_150` Tesira | 22 | **False** |

Extron is not consistent even within one vendor's cameras - the two 1 Beyond
packages differ. Two consequences:

1. **Our derived package inherits TCP 5500 locked**, which is correct for the
   i20 (Crestron declares the same), so nothing needs changing. That is luck
   rather than design, and a donor with the wrong port would have required
   editing `_port` - a one-line change with `pkp_build.py`, but only if someone
   thought to look.
2. **A from-scratch emitter must construct this asset**, not just the script.
   The transport is package metadata; the embedded Python never mentions a port.

The ControlScript form has the opposite property: the port is a constructor
argument (`EthernetClass(ip, 5500)`), so it is the integrator's to set and
nothing is locked.

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
