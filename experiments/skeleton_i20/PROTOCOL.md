# Hardware test protocol — synthesised i20 driver

**What you have:** four `.pkp` packages in `out/`, built by `build_i20.py` from
Extron's own 1 Beyond PTZ-IP12/IP20 package.

**What this measures:** the five gates between a file on disk and a camera that
moves. Finding 12 reached gate 1 on a different machine; gates 2–5 have never
been tested by this project at all.

**Why it is staged:** each package changes exactly one thing relative to the
previous one, so a failure names its own cause. If you only have time for one,
run **T3** — but a T3 failure won't tell you *which* edit caused it, which is
the whole reason the other three exist.

---

## Before you start

**Back up the catalogue.** GC truncates `DataFile.dat` to zero and rebuilds it
on every rescan; an interrupted start leaves you with nothing.

```
copy "C:\Users\Public\Documents\extron\driver3\DataFile.dat"      %USERPROFILE%\Desktop\DataFile.dat.bak
copy "C:\Users\Public\Documents\extron\driver3\DriverLookup.dat"  %USERPROFILE%\Desktop\DriverLookup.dat.bak
```

Record the baseline before staging anything:

| reading | where |
|---|---|
| `DataFile.dat` size | file properties |
| `DriverLookup.dat` size | file properties |
| model count | GC → Driver Manager, the total it reports |

The rebuild takes 2–4 minutes and shows "Organizing Driver Manager…" on the
splash. That is expected, not a hang.

---

## The packages

| file | changes vs. the one above | gate it isolates |
|---|---|---|
| `1bynd_19_20020_v1_0_0.pkp` | nothing — byte-identical copy of Extron's driver, new filename | **discovery**: does GC index a file whose name disagrees with its internal id? |
| `1bynd_19_20021_v1_0_0.pkp` | model strings → `IV-CAM-I12` / `IV-CAM-I20` | **metadata**: does a renamed model survive the catalogue rebuild? |
| `1bynd_19_20022_v1_0_0.pkp` | embedded driver → the i20 command set (37,201 → 68,285 bytes) | **script substitution**: does a rewritten, *longer* driver load and run? |
| `1bynd_19_20023_v1_0_0.pkp` | both of the above | **the deliverable** |

All four keep the internal identity string `1bynd_19_4743`. That is deliberate —
T0 is the experiment that establishes whether GC tolerates the mismatch. Don't
"fix" it before running T0, or T1–T3 become uninterpretable.

---

## Procedure

Run each stage from a **fully closed** GC. Stage one package at a time.

1. Close GC completely.
2. Copy the package into `C:\Users\Public\Documents\extron\driver3\`.
3. Start GC. Wait for "Organizing Driver Manager…" to finish.
4. Record the readings below.
5. Open Driver Manager and search for the model name.

### Record per stage

```
stage:                    T0 / T1 / T2 / T3
DataFile.dat size:        ________  (delta from baseline: ________)
DriverLookup.dat size:    ________  (delta: ________)  entries: ________
model count:              ________  (delta: ________)
appears in Driver Manager: yes / no
listed under model name:  ______________________
any GC error text:        ______________________  (verbatim, please)
```

An entry appearing in `DriverLookup.dat` but **no** model added to
`DataFile.dat` is the interesting failure: it means GC saw the file and
declined to parse it. That distinction is the single most useful thing this
protocol can tell us, so please record both numbers even when it works.

---

## T3 — the part that has never been tested

Gates 2–5. Everything above only proves GC read the file.

1. **Place** — add the camera to a GC project as a device. Does it appear with
   the expected control set? Record which commands GC exposes in the UI.
2. **Build** — build the project. Any build error, verbatim.
3. **Upload** — send to the processor.
4. **Control** — with an i20 on the network, in this order:

| # | command | expect | wire (for a capture, if you take one) |
|---|---|---|---|
| 1 | Power On | camera wakes | `81 01 04 00 02 FF` |
| 2 | Preset Recall 1 | camera moves | `81 01 04 3F 02 01 FF` |
| 3 | Zoom Tele, speed 5 | **zooms at speed 5, not speed 0** | `81 01 04 07 25 FF` |
| 4 | Tracking Framing → Start | auto-framing engages | `81 01 04 3F 02 50 FF` |
| 5 | **poll Tracking Framing** | reports **Start** | `81 09 08 01 FF` → `90 50 02 FF` |
| 6 | Tracking Framing → Stop | auto-framing disengages | `81 01 04 3F 02 51 FF` |
| 7 | **poll Tracking Framing** | reports **Stop** | `81 09 08 01 FF` → `90 50 03 FF` |
| 8 | Zoom Position 6666, speed 3 | zooms to a repeatable point | `81 01 04 47 03 01 0A 02 0B FF` |
| 9 | Freeze Frame On / Off | image freezes / resumes | `81 01 04 62 02 FF` / `03` |
| 10 | Indicator Light: Full / Red / Bright | lightbar goes solid red | `81 C1 0D 0D 0D 0D FF` |
| 11 | Indicator Light: Half / Green / Dim | two inner segments dim green | `81 C1 00 04 04 00 FF` |
| 12 | Indicator Light: None | lightbar off | `81 C1 00 00 00 00 FF` |
| 13 | Tracking Profile 2 | profile changes | `81 01 04 3F 02 6A FF` |
| 14 | Camera Output → 2 | switches to camera 2 | `81 C2 01 08 02 FF` |
| 15 | Intelligent Switching → Resume | switching resumes | `81 C2 01 08 00 FF` |
| 16 | Intelligent Switching → Pause | switching pauses | `81 C2 01 0B 00 FF` |

Steps 5 and 7 are the **feedback** test. Polling is where this driver is most
likely to be wrong, because it is the one place a reply layout has to be right
rather than just a request. If the poll reports the wrong state, capture the
raw reply bytes — that alone fixes it.

Step 3 deserves its own attention: it is the one place this driver
**deliberately differs** from Extron's shipping behaviour. Their driver
computes the zoom speed and then transmits a constant instead, so zoom always
ran at speed 0. If step 3 visibly zooms faster than Extron's own PTZ-IP driver
does, that defect is confirmed on hardware.

### Transport: nothing to configure

The package pins it and Global Configurator will not let you change it:
`_port 5500`, TCP, `_canEditPort: False`. That is inherited from Extron's
PTZ-IP12/20 donor and it matches what Crestron declares for the i20, so the
greyed-out port field is the right value. If the camera has been moved off
5500, this package cannot reach it — say so and the port is a one-line rebuild.

### T3b — settling a contested byte

Crestron's driver and Crestron's documentation disagree about preset **83**
(`0x53`), and only about that one. Five other reserved presets agree exactly.

| source | what it calls preset 83 |
|---|---|
| `Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg` (their driver) | `EnablePresenterTracking` |
| Reserved-Presets documentation page | **Pause Group Tracking** |

Both readings send the same byte, so the driver works either way — only the
label on the control is at stake. This sequence settles it:

1. Group Tracking → Enable — `81 01 04 3F 02 52 FF`. Confirm group tracking is
   visibly running.
2. Presenter Tracking → Enable — `81 01 04 3F 02 53 FF`.
3. Observe.

| what happens | verdict |
|---|---|
| group tracking **stops** | the documentation is right; the control should be renamed "Pause Group Tracking" |
| camera switches to **presenter framing** | Crestron's driver is right; the label stands |
| nothing | neither, on this firmware — record the firmware version |

This is a finding-08-class question (docs versus implementation), and it is
cheap to answer while you have the camera in front of you.

---

## What a failure means

| symptom | most likely cause | next step |
|---|---|---|
| T0 not indexed | GC ties the filename to the internal id | rebuild with the identity string changed to match; this repo can do that in one line |
| T0 fine, T1 not indexed | metadata is validated against something we didn't change | dump the T1 diff — only two strings moved |
| T1 fine, T2 not indexed | the package is validated by size, hash or signature | this is the important negative; it would mean transplants are detectable |
| T2 indexed but won't place | device class or capability metadata, not the script | inspect what GC read vs. what it exposes |
| Places but won't build | the driver's declared commands don't match GC's expectations | the build error text will name it |
| Builds, uploads, no response | transport: the donor was changed from UDP 5500 to TCP in v1_0_1 | confirm what the i20 actually listens on |
| Responds to Extron's commands but not the tracking ones | the reserved-preset theory is wrong for this model | capture the wire; that single result would be worth a finding |

---

## Known limits of what is being tested

- **No i20 was available to this repo.** Every added command is a transcription
  of Crestron's declarative spec, verified against it byte-for-byte offline
  (`test_i20_wire.py`, 39 checks) — but never observed on a wire.
- **Status feedback is better founded than it was, but still unmeasured.**
  The tracking poll now parses a reply layout Crestron *documents*
  (`y0 50 02 FF` active / `y0 50 03 FF` paused) rather than one we assumed; an
  undocumented payload raises an error instead of guessing. Two replies are
  still inferred rather than documented - `CameraOutput` (the docs say "see
  below" and then print nothing) and `ZoomPosition`/`PanTiltAngle` nibble
  layouts. Expect those three to be where polling breaks first.
- **Catalogue acceptance is not a working driver.** Finding 12 got a generated
  package listed in Driver Manager; that proves nothing about gates 2–5. Please
  don't stop at "it showed up".
