# Hardware test protocol — synthesised i20 driver

## Where this stands (2026-09-13)

| date | package | result | source |
|---|---|---|---|
| 2026-09-08 | `20020`, `20021` | discovered, catalogued, load | finding 15, `hardware/` |
| 2026-09-08 | `20022`, `20023` | catalogued, then refused at selection: **"Invalid Driver … Error Code: 80085"** | finding 15, `hardware/80085-invalid-driver.png` |
| 2026-09-09 | — | `80085` decoded as a SHA-256 mismatch on the rewritten script. The builder now refreshes the digest, and all four packages return `Valid` from Extron's own validator. The `20030`–`20032` ladder this page once sent testers to was answered offline in seconds, so it is not needed. | finding 16 §1–§4 |
| 2026-09-09 | `20022`, `20023` | load and select in GCP — but render only the donor's **15** commands | finding 18 §1 |
| 2026-09-10 | `20024` | catalogued, listed as *IV-CAM-I20 v1.2*, assigned to Ethernet Port 1; all **34** commands render with their ranges and enum states | finding 18 §8 |
| 2026-09-13 | `20024` | installed into a second, separate GC library: catalogued on the first launch, and `DataFile.dat` grew by 5,716 bytes — the same delta as on 09-10 | this page |
| 2026-09-13 | `20024` | **rebuilt** with two reply-parser fixes (`experiments/loopback/README.md`). Extron's `LoadFromFile` accepts it, and its command surface — script names, display names, attribute bits, parameters, enum states — is identical to the build GC rendered, so only the script and its digest changed. Not yet re-catalogued in GC | this page |
| 2026-09-14 | `20024` | the rebuilt package (233,969 bytes) replaced the 09-13 build (233,820) in the GC library, with GC closed; the old package, `DataFile.dat` and `DriverLookup.dat` backed up first. GC re-catalogued it on the next start: `gc_catalogue.py --has` finds it among 1,880 packages, `DataFile.dat` came out the same size (25,116,011 bytes, as a script-only change predicts) and `DriverLookup.dat` one byte smaller | this page |
| 2026-09-14 | `20024` | **binding a test panel in GC found two asset gaps.** A label's Text Feedback offered nothing for Zoom Position, Pan/Tilt Angle Status or Camera Output, and Camera Connection Status offered no way to choose the camera. Cause: every decimal was cloned from Preset's Value, whose `ParamAssetBase+_conditionTypes` is 0 (it is only ever sent) and whose `_attributes` is 15 (a Value, not a qualifier). Extron's own feedback values carry 3 (Set+Update) or 1 (Update-only), and qualifiers 13 (`pana_19_5702`, `7th_29_17052`). Rebuilt with both set, and `build_i20_assets.verify` now refuses a feedback command without them. `LoadFromFile` accepts it with the same 34 commands; not yet re-catalogued | this page |

**Gates passed:** discovery, catalogue parse, selection, command surface, and
placing the device in a project. **Gates never tested: Build, Upload, Control.**
Nothing has run on a processor, and no socket has been opened to a camera. The
procedure below is for those three.

---

## What you have

Five `.pkp` in `out/`, all built from Extron's own 1 Beyond PTZ-IP12/IP20
package (`1bynd_19_4743`). **Install `20024` only.** The first four are the
staged round from 2026-09-08. They are kept because each changes exactly one
thing relative to the one above it, so they can still isolate a regression.

| file | changes vs. the one above | gate it isolates |
|---|---|---|
| `1bynd_19_20020_v1_0_0.pkp` | nothing but the filename — the same 321,697-byte NRBF stream as Extron's driver (the gzip wrapper is re-compressed, so the file's own hash differs) | **discovery**: does GC index a file whose name disagrees with its internal id? (yes) |
| `1bynd_19_20021_v1_0_0.pkp` | model strings → `IV-CAM-I12` / `IV-CAM-I20` | **metadata**: does a renamed model survive the catalogue rebuild? (yes) |
| `1bynd_19_20022_v1_0_0.pkp` | embedded driver → the i20 command set (37,201 → 70,574 bytes), digest refreshed | **script substitution and integrity** |
| `1bynd_19_20023_v1_0_0.pkp` | both of the above | **selection** — lists as *IV-CAM-I12 v1.1* |
| `1bynd_19_20024_v1_0_0.pkp` | 19 command assets cloned from the donor's own and added to the graph (15 → 34); model version 1.2 | **command surface — the deliverable** |

All five keep the internal identity string `1bynd_19_4743`. T0 established that
GC tolerates a filename that disagrees with it, so do not "fix" it.

---

## Before you start

**Back up the catalogue.** GC truncates `DataFile.dat` to zero and rebuilds it
on every rescan; an interrupted start leaves you with nothing. The driver
library is `C:\Users\Public\Documents\Extron\Driver3` on a default install; see
`ENVIRONMENT.md`.

```
copy "C:\Users\Public\Documents\Extron\Driver3\DataFile.dat"      %USERPROFILE%\Desktop\DataFile.dat.bak
copy "C:\Users\Public\Documents\Extron\Driver3\DriverLookup.dat"  %USERPROFILE%\Desktop\DriverLookup.dat.bak
```

Record the baseline before installing anything:

| reading | where |
|---|---|
| `DataFile.dat` size | file properties |
| `DriverLookup.dat` size | file properties |
| model count | GC → Driver Manager, the total it reports |

The rebuild runs while the splash shows "Organizing Driver Manager…". It has
taken anywhere from under a minute to four minutes. That is expected, not a hang.

---

## Install 20024

1. Close GC completely.
2. Copy `out/1bynd_19_20024_v1_0_0.pkp` into the driver library. If `20023` is
   installed too, Driver Manager lists the same models twice; the one you want
   is version **1.2**.
3. Start GC. Wait for "Organizing Driver Manager…" to finish.
4. Confirm it was catalogued, either way:
   - `python3 tools/gc_catalogue.py <DRIVER_LIB>/DriverLookup.dat --has 1bynd_19_20024` exits 0;
   - Driver Manager → search `IV-CAM` → *1 Beyond / IV-CAM-I20 / 1.2 / Camera*.

```
DataFile.dat size:        ________  (delta from baseline: ________; 5,716 expected)
DriverLookup.dat size:    ________  (delta: ________)  entries: ________
model count:              ________  (delta: ________)
appears in Driver Manager: yes / no
listed under model name:  ______________________
any GC error text:        ______________________  (verbatim, please)
```

An entry appearing in `DriverLookup.dat` but **no** growth in `DataFile.dat` is
the interesting failure: GC saw the file and declined to parse it (finding 18
§6). Record both numbers even when it works.

---

## T3 — Place, Build, Upload, Control

1. **Place** — *passed for 20024 (finding 18 §8)*, but do it in your own
   project: add the processor, open Ethernet Port 1, and assign
   *1 Beyond IV-CAM-I20 v1.2*. The port shows TCP 5500, greyed out.
2. **Save** the project to an empty folder.
3. **Build.** Check the controller address first: the Add Controller dialog can
   arrive pre-filled with a real processor's address and credentials. To build
   with no processor present, set a non-routable address such as `192.0.2.10`.
   Record any build error verbatim, and whether Build tried to reach the network.
4. **Upload** — with the real address restored, send to the processor.
5. **Control** — with an i20 on the network, in this order. The first column is
   the name GC's property editor shows; the script name follows in brackets
   where it differs.

| # | command | set | expect | wire (for a capture, if you take one) |
|---|---|---|---|---|
| 1 | Power | On | camera wakes | `81 01 04 00 02 FF` |
| 2 | Preset | Action Recall, Value 1 | camera moves | `81 01 04 3F 02 01 FF` |
| 3 | Zoom | Tele, Speed 5 | **zooms at speed 5, not speed 0** | `81 01 04 07 25 FF` |
| 4 | Auto Tracking (`TrackingFraming`) | Start | auto-framing engages | `81 01 04 3F 02 50 FF` |
| 5 | **poll Auto Tracking** | — | reports **Start** | `81 09 08 01 FF` → `90 50 02 FF` |
| 6 | Auto Tracking | Stop | auto-framing disengages | `81 01 04 3F 02 51 FF` |
| 7 | **poll Auto Tracking** | — | reports **Stop** | `81 09 08 01 FF` → `90 50 03 FF` |
| 8 | Zoom Position (`ZoomPosition`) | Value 6699, Speed 3 | zooms to a repeatable point | `81 01 04 47 03 01 0A 02 0B FF` |
| 9 | Freeze Frame (`FreezeFrame`) | On, then Off | image freezes / resumes | `81 01 04 62 02 FF` / `81 01 04 62 03 FF` |
| 10 | Indicator Light (`IndicatorLight`) | Full; Color Red; Brightness Bright | lightbar goes solid red | `81 C1 0D 0D 0D 0D FF` |
| 11 | Indicator Light | Half; Color Green; Brightness Dim | two inner segments dim green | `81 C1 00 04 04 00 FF` |
| 12 | Indicator Light | None | lightbar off | `81 C1 00 00 00 00 FF` |
| 13 | Tracking Profile (`TrackingProfile`) | 2 | profile changes | `81 01 04 3F 02 6A FF` |
| 14 | Camera Output (`CameraOutput`) | 2 | switches to camera 2 | `81 C2 01 08 02 FF` |
| 15 | Intelligent Switching (`IntelligentSwitching`) | Resume | switching resumes | `81 C2 01 08 00 FF` |
| 16 | Intelligent Switching | Pause | switching pauses | `81 C2 01 0B 00 FF` |

Every wire string above was produced by the ControlScript module from these
exact inputs (`doc_calls.py`), and both wire tests pin the same bytes for the
`.pkp` script. Step 8's value is `0x1A2B`; earlier versions of this page said
6666, which sends `81 01 04 47 03 01 0A 00 0A FF`.

**Steps 5 and 7 are the feedback test, and a matching status straight after a
Set is not a pass.** Both emitters write the value they sent into the status
before the camera replies — the `.pkp` script marks it `Emulated` — so only a
poll whose reply parses can change it. The stronger form of the test is to
change tracking from the camera side (its web UI or remote), then poll. If the
poll reports the wrong state, capture the raw reply bytes — that alone fixes it.

Step 3 deserves its own attention: it is the one place this driver
**deliberately differs** from Extron's shipping behaviour. Their driver
computes the zoom speed and then transmits a constant instead, so zoom always
ran at speed 0. If step 3 visibly zooms faster than Extron's own PTZ-IP driver
does, that defect is confirmed on hardware.

### The composed commands

Three commands were assembled from parts of the donor's own, so their shape in
GC is the part least like anything Extron ships:

| GC command | parameters GC renders | unmeasured |
|---|---|---|
| Pan Tilt Angle | Pan `(-2448) to 2448`, Tilt `(-1296) to 1296`, Pan Speed, Tilt Speed | whether GC delivers `qualifier['Pan']` / `['Tilt']` to the script; whether those ranges are the camera's real limits |
| Zoom Position | decimal Value 0–16384, decimal Speed | the reply layout of the position poll |
| Indicator Light | Value `None, Half, Full`; Color `Green, Red, Yellow`; Brightness `Off, Dim, Medium, Bright` | the off-segment encoding (§T3b's neighbour in `ROADMAP.md` H3) |

Setting edge values on these and capturing what is sent is worth doing while a
camera is on the bench.

### Transport: nothing to configure

The package pins it and Global Configurator will not let you change it:
`_port 5500`, TCP (`ProtocolCompatibilityFlags 16`), `_canEditPort: False`. That is inherited from Extron's
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

The checks named here run on a workstation in seconds; `experiments/gcp_harness/`
has `Load-Package.ps1`.

| symptom | most likely cause | next step |
|---|---|---|
| not in `DriverLookup.dat` after a rebuild | discovery: the filename, or the file is not in the library GC reads (finding 12) | check the library path GC actually uses |
| in `DriverLookup.dat`, `DataFile.dat` did not grow, absent from Driver Manager | catalogue parse: .NET's deserializer refused the stream (finding 18 §6) | `Load-Package.ps1 -Path PKG -Deserialize` names the exception |
| listed, refused at selection with `80085` | a packaged resource no longer matches its stored SHA-256 (finding 16) | `python3 tools/pkp_validate.py -v PKG` |
| selects, but shows fewer commands than expected | the asset tree is short — GC never reads the script's `Commands` (finding 18 §1) | `Load-Package.ps1 -Path PKG -Commands` |
| places but won't build | the build error text will name it | record it verbatim |
| builds, uploads, no response | transport, or the camera is not listening on TCP 5500 | confirm what the i20 listens on; capture |
| responds to Extron's commands but not the tracking ones | the reserved-preset theory is wrong for this model | capture the wire; that single result would be worth a finding |
| a poll always shows the last value set | the reply never parsed, so the status is still the emitted value | capture the raw reply bytes |

---

## Known limits of what is being tested

- **No i20 has been available to this project.** Every added command is a
  transcription of Crestron's declarative spec, verified against it byte for
  byte offline — `test_i20_wire.py` (86 checks, the `.pkp` script) and
  `test_i20_cs_wire.py` (57 checks, the ControlScript module) — but never
  observed on a wire.
- **Status feedback is better founded than it was, but still unmeasured.**
  The tracking poll parses a reply layout Crestron *documents*
  (`y0 50 02 FF` active / `y0 50 03 FF` paused) rather than one we assumed; an
  undocumented payload raises an error instead of guessing. `CameraOutput`'s
  reply turned out to be documented, on the Intelligent Switching page, as
  `y0 50 0S 0Z FF`; the parser read the wrong byte until 2026-09-13
  (`experiments/loopback/README.md`). Still inferred: the `ZoomPosition` and
  pan-tilt nibble layouts, and whether negative pan/tilt positions come back as
  two's complement. Expect those to be where polling breaks first.
- **Rendering in the editor is not a working driver.** Finding 18 took 20024 as
  far as GC's property editor with every command drawn correctly. That proves
  nothing about Build, Upload or Control. Please don't stop at "it showed up".
