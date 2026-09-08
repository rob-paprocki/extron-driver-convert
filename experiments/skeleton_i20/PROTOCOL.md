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
| `1bynd_19_20022_v1_0_0.pkp` | embedded driver → the i20 command set (37,201 → 54,845 bytes) | **script substitution**: does a rewritten, *longer* driver load and run? |
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
| 5 | Tracking Framing → Stop | auto-framing disengages | `81 01 04 3F 02 51 FF` |
| 6 | Presenter Tracking → Enable | presenter mode | `81 01 04 3F 02 53 FF` |
| 7 | Group Tracking → Enable | group mode | `81 01 04 3F 02 52 FF` |
| 8 | Zoom Position 6666, speed 3 | zooms to a repeatable point | `81 01 04 47 03 01 0A 02 0B FF` |
| 9 | Freeze Frame On / Off | image freezes / resumes | `81 01 04 62 02 FF` / `03` |

Step 3 is worth its own attention: it is the one place this driver
**deliberately differs** from Extron's shipping behaviour. Their driver
computes the zoom speed and then transmits a constant instead, so zoom always
ran at speed 0. If step 3 visibly zooms faster than Extron's own PTZ-IP driver
does, that defect is confirmed on hardware.

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
- **Status feedback is the weakest part.** Crestron declares the inquiry
  *requests*; it does not fully declare the *reply* layouts. Those are parsed on
  the same pattern Extron uses for the equivalent PTZ-IP replies, which is an
  assumption, not a measurement. Expect polled status to be where this breaks
  first.
- **Catalogue acceptance is not a working driver.** Finding 12 got a generated
  package listed in Driver Manager; that proves nothing about gates 2–5. Please
  don't stop at "it showed up".
