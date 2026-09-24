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
| 2026-09-14 | `20024` | **binding a test panel in GC found two asset gaps.** A label's Text Feedback offered nothing for Zoom Position, Pan/Tilt Angle Status or Camera Output, and Camera Connection Status offered no way to choose the camera. Cause: every decimal was cloned from Preset's Value, whose `ParamAssetBase+_conditionTypes` is 0 (it is only ever sent) and whose `_attributes` is 15 (a Value, not a qualifier). Extron's own feedback values carry 3 (Set+Update) or 1 (Update-only), and qualifiers 13 (`pana_19_5702`, `7th_29_17052`). Rebuilt with both set, and `build_i20_assets.verify` now refuses a feedback command without them. `LoadFromFile` accepts it with the same 34 commands, and GC re-catalogued it into the library on the next start (`gc_catalogue.py --has`, 1,880 packages) | this page |
| 2026-09-14 | `20025` | **still no conditions** for those four in GC. One more member differed from Extron's: `ParamAssetBase+_validOperators` was 1 (set only). Extron's is the condition operators on an Update-only Value (`PanPositionStatus`: 282001408) and action \| condition on a Set+Update one (`ZoomPosition`: 282001415). Set the same way and checked by `verify`; against `pana_19_5702` the Pan/Tilt Values now differ only in range. Written as a **new file and version, `1bynd_19_20025` / v1.3**, because a GC project that already holds 20024 v1.2 keeps that build. `LoadFromFile` accepts it, 34 commands per model. 20024 is kept unchanged | this page |
| 2026-09-14 | `20025` | **Build and Upload passed; the driver runs on a processor.** A GC Pro project (IPCP Pro 360, TLP Pro 725M, *IV-CAM-I20 v1.3* addressed to a PC) built and uploaded. The processor connected to `experiments/loopback/visca_listener.py --reply full` and polls Power, TrackingFraming, AutoExposure, WhiteBalance, AutoFocus, Backlight and FreezeFrame about every 3 s with the documented inquiry bytes, each answered. Not polled: ZoomPosition, the angle statuses, CameraOutput, CameraConnectionStatus. Capture `experiments/loopback/captures/2026-09-14-gc-panel-run.tsv` | `experiments/loopback/` |
| 2026-09-14 | `20025` | **Control from the TLP Pro 725M panel, 30 of 30.** Every button on `experiments/loopback/panel/` pressed through Extron Control for Web: all 30 frames reached the PC as the expected VISCA bytes, in order (Power, Auto Tracking, all five Auto Exposure and six White Balance values including One Push Trigger, Auto Focus, Backlight, Freeze Frame, Camera Output 1–5). The seven polled statuses moved their lit button within one poll (~3 s). **Open:** the processor polls exactly the statuses bound to button feedback and never the numeric ones or CameraOutput, so the Zoom, Pan, Tilt and Camera Output readouts stay `--`. The driver script has no poll list, so what is polled is the GC-built program's choice | same capture |
| 2026-09-15 | `20025` | **The numeric statuses are never asked for.** Toolbelt's live trace on the processor, with Program messages on, shows only the seven enum polls every 3 s and no errors, so the GC-built program does not call Update on ZoomPosition, Pan/TiltAngleStatus, CameraOutput or CameraConnectionStatus; the driver is not failing them. Ruled out: bindings (all bound), `PollingInterval` (3 s on CameraOutput and PanAngleStatus, as on Backlight and `pana_19_5702`), the script's `self.Commands` flags (identical to `pana_19_5702` PanPositionStatus / ZoomPosition, which has no polling of its own). **Lead:** every enum status GC polls came from the donor's enums; every decimal status it skips was built from Preset's DecimalParamAsset, which is the donor's older serialization (`Extron.Configuration` 1.1.24.402, no `_bEnableCustomMinMax`) where `pana_19_5702` is 13.26.0.15. The donor has no decimal status of its own to copy | Toolbelt trace |
| 2026-09-15 | `20026` | **Cause found: polling was disabled on every status we added.** GC shows those commands as not polled. Its compiler polls a command only if `CommandAssetExtensions.HasPollingValue` holds: the command's `PollingInterval` parameter exists, has `ParamAttributeFlags.Enabled`, and has a value (`Extron.Configuration.Core`, read with ildasm). Every polled command carries attributes 13 (Enabled) and 3 s, as do `pana_19_5702` ZoomPosition and PanPositionStatus; ZoomPosition, CameraOutput, Pan/TiltAngleStatus and CameraConnectionStatus carried 12, cloned from Preset, Zoom and ConnectionStatus, which are never polled (the last two also 1 s). Rebuilt as **`1bynd_19_20026` / v1.4** with Enabled set and 3 s; `verify` now refuses a live status GC would not poll. `LoadFromFile` accepts it, 34 commands per model. Also decoded from the DLL: `DriverAttributeEnum` 1 ConfigurationVisible, 2 RuntimeVisible, 4 Alias, 8 RequiredPollingCommand, 16 EmulatedStatus, 32 LiveStatus, 64 WriteProtected; `DriverConditionTypeFlags` 1 Live, 2 Emulation; `ParamAttributeFlags` 1 Enabled, 2 ValueType, 4 ConfigurationVisible, 8 RuntimeVisible | this page |
| 2026-09-17 | `20026` | **v1.4 polls on hardware.** The processor reconnected at 17:09:50 running v1.4 and ran 802 clean 3 s cycles — 8,823 inquiries, 8,823 replies, nothing undecoded — carrying the four that were never asked for before: `81 09 04 47 FF` ZoomPosition, `81 09 06 12 FF` **twice** (Pan and Tilt are separate commands sharing one inquiry) and `81 C2 09 08 FF` CameraOutput. So enabling `PollingInterval` was the whole fix for those | capture, untracked: lab addresses |
| 2026-09-17 | `20026` | **Which commands GC polls, read out of the compiler.** CameraConnectionStatus is still never polled, and the package is not why: it carries attributes 35 with `PollingInterval` 13 at 3 s, exactly like the four that now work. `SystemCompiler._BuildPollingDriver` assembles a driver's poll list from three sources: query command **instances** in the project's logic; command instances used by the panel module; and, independent of the project, every command whose `DriverAttributeEnum` has `RequiredPollingCommand` (8), whose qualifier comes from `RenderDriverRequiredCommandQualifier` and whose interval falls back Value → DefaultValue → Interval. The first two gate on the same `PollingInterval` Enabled bit and build the qualifier from the **binding's** parameter values (`RenderPollingCommandInstance` walks `InstanceParams`), so **a qualified status nothing binds has no qualifier to poll with and is not polled at all.** Power is the only i20 command carrying bit 8, which is why one Power inquiry arrives alone at connect, 3 s ahead of the first full cycle. **So: `HasPollingValue` is necessary, not sufficient — the project must also bind the status.** | `Extron.Configuration.Core`, ildasm |
| 2026-09-18 | `20026` | **Both directions checked from the panel, and the last gap was a binding, not the package.** Device → panel: with the camera changed only from the listener's console, Zoom Position, Pan Angle, Tilt Angle and Camera Output tracked it exactly (8000 / 1000 / -500 / 4) within a poll, and Auto Tracking and Freeze Frame moved their lit button. **These four readouts were `--` on every build before v1.4.** Panel → device: eight presses, eight exact frames — `81 01 04 39 03 FF`, `81 01 04 35 01 FF`, `81 01 04 38 03 FF`, `81 01 04 33 02 FF`, `81 C2 01 08 03 FF`, `81 01 04 3F 02 51 FF`, `81 01 04 62 03 FF`, `81 C2 01 08 01 FF` — each reflected back on the panel at the next poll. **The four Cam 2–5 labels are bound to the device's `ConnectionStatus`, not `CameraConnectionStatus`:** disconnecting two cameras at the console moved nothing, and stopping the listener flipped all four to Disconnected in lockstep with the device label at top right. That is the whole reason `81 C2 09 0D FF` is never sent — rebind them and it will be | `experiments/loopback/panel/` |
| 2026-09-18 | `20026` | **Rebound, and it polls — the compiler rule confirmed by prediction.** With the four labels bound to *Camera* Connection Status, the rebuilt program sends **four** inquiries per 3 s cycle, one per bound qualifier: `81 C2 09 0D 02 FF`, `03`, `04`, `05`. The qualifier is the binding's own, exactly as `RenderPollingCommandInstance` reads it from `InstanceParams`. Each label then tracked its own camera independently — connecting 2 while disconnecting 3 moved those two and left 4 and 5 alone. **Every status on the page now works in both directions, and no package change was needed.** | capture `2026-09-18T010954.tsv` |
| 2026-09-18 | `20027` | **The command surface tidied, now that it is known to work.** Three changes, none of them to a byte the camera sees. (1) `GroupTracking` and `PresenterTracking` were one value each — GC could latch either on and release neither, and the emulated status could never go back. They are one setting on the camera, so they are now one command, **Tracking Mode**, valued Group (0x52) or Presenter (0x53). The value names are the reading *both* sources support, so the contested byte stays contested and T3b still settles it. (2) **Camera Output is 1–5**, not 0–5: value 0 was byte-for-byte `IntelligentSwitching Resume`, so two commands sent one frame and a capture could not tell them apart. (3) The two position statuses **share one query**, rate limited the way `pana_19_5702` rate limits its own, so a bound Pan and a bound Tilt cost one `81 09 06 12 FF` per cycle rather than two; a failed query caches nothing. Tracking Mode carries attributes 19 with condition type 2 on its Value — Extron's own shape for a Set-only command with emulated feedback (`UserDefinedString`), so GC offers it to a button but never polls a command the script cannot answer. `LoadFromFile` accepts it: **33 commands** per model, `Tracking Mode Value[Group/Presenter]`. Not yet on hardware | this page |
| 2026-09-23 | `20028` | **Parity with Crestron's I20 driver, built offline.** Twelve commands Crestron's driver has and ours did not — Exposure Compensation Mode and level (0–14), Focus Position, One Push Auto Focus, Auto Focus Behavior and Sensitivity, Auto Privacy Mode, Auto Software Update, and the statuses Device Model, ROM Version and Pan/Tilt Speed Max — each on Crestron's own template, reply rule and range (`CRESTRON_PARITY.md`). **Tracking Mode, Tracking Profile and Intelligent Switching now poll**: `c2 09 06`, `c2 09 07`, and the switching flag in the Get Output reply Camera Output already receives. Replies that carry several statuses are queried once and write them all. The **IV-CAM-I12 no longer offers** Tracking Mode, Tracking Profile or Preset Zone, whose presets are I20-only (`I12_VS_I20.md`). `LoadFromFile` and `BinaryFormatter` accept it: **45 commands, 42 on the I12**; `pkp_validate` Valid. Model version 1.6. Not yet on hardware | this page, `CRESTRON_PARITY.md` |

**Gates passed:** discovery, catalogue parse, selection, command surface,
placing the device in a project, **Build and Upload** (20025, 2026-09-14),
**control against a PC playing the camera** (`experiments/loopback/`), and
**feedback on a synthesised numeric status** (20026, 2026-09-17). `20028`
(2026-09-23) has passed Extron's loader and validator only. **Not yet
tested: a real i20.** No socket has been opened to a camera, so every reply the
driver has parsed came from the documentation. The procedure below is for that.

---

## What you have

Nine `.pkp` in `out/`, all built from Extron's own 1 Beyond PTZ-IP12/IP20
package (`1bynd_19_4743`). **Install `20028` only.** The first four are the
staged round from 2026-09-08. They are kept because each changes exactly one
thing relative to the one above it, so they can still isolate a regression.

| file | changes vs. the one above | gate it isolates |
|---|---|---|
| `1bynd_19_20020_v1_0_0.pkp` | nothing but the filename — the same 321,697-byte NRBF stream as Extron's driver (the gzip wrapper is re-compressed, so the file's own hash differs) | **discovery**: does GC index a file whose name disagrees with its internal id? (yes) |
| `1bynd_19_20021_v1_0_0.pkp` | model strings → `IV-CAM-I12` / `IV-CAM-I20` | **metadata**: does a renamed model survive the catalogue rebuild? (yes) |
| `1bynd_19_20022_v1_0_0.pkp` | embedded driver → the i20 command set (37,201 → 98,990 bytes as of v1.6; rebuilt with each version), digest refreshed | **script substitution and integrity** |
| `1bynd_19_20023_v1_0_0.pkp` | both of the above | **selection** — lists as *IV-CAM-I12 v1.1* |
| `1bynd_19_20024_v1_0_0.pkp` | 19 command assets cloned from the donor's own and added to the graph (15 → 34); model version 1.2 | **command surface — the deliverable** |
| `1bynd_19_20025_v1_0_0.pkp` | the added statuses' Values carry `_conditionTypes` and `_validOperators`; model version 1.3 | **feedback GC will bind** — a label can compare against them |
| `1bynd_19_20026_v1_0_0.pkp` | those statuses' `PollingInterval` carries `Enabled` at 3 s; model version 1.4 | **feedback GC will poll** — the readouts follow the device |
| `1bynd_19_20027_v1_0_0.pkp` | one Tracking Mode command replaces two enable-only ones; Camera Output 1-5; the two position statuses share one query; model version 1.5 | **the command surface as a surface** — nothing that can be switched on but not off, and no two commands sending one frame |
| `1bynd_19_20028_v1_0_0.pkp` | twelve parity commands (33 → 45); Tracking Mode, Tracking Profile and Intelligent Switching polled; the IV-CAM-I12 model's own list drops the three I20-only commands (42); model version 1.6 | **per-model command lists** — does GC show the I12 the shorter list Extron's loader reads? |

All nine keep the internal identity string `1bynd_19_4743`. T0 established that
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

## Install 20028

*(The built packages are not in the repository since 2026-09-24 — each is a
modified Extron package. Build `20028` locally with
`python experiments/skeleton_i20/build_i20_assets.py`, which needs Extron's donor
package in `samples/` (`vendor-files.manifest.tsv`); the owner's checkout already
has it.)*

1. Close GC completely.
2. Copy `out/1bynd_19_20028_v1_0_0.pkp` into the driver library. If an earlier
   build is installed too, Driver Manager lists the same models more than once;
   the one you want is version **1.6**. A project already using an older build
   keeps it: swap the device to *IV-CAM-I20 v1.6* and rebind.
3. Start GC. Wait for "Organizing Driver Manager…" to finish.
4. Confirm it was catalogued, either way:
   - `python3 tools/gc_catalogue.py <DRIVER_LIB>/DriverLookup.dat --has 1bynd_19_20028` exits 0;
   - Driver Manager → search `IV-CAM` → *1 Beyond / IV-CAM-I20 / 1.6 / Camera*.
5. **New in 1.6, worth a look:** place *IV-CAM-I12 v1.6* on a spare port and
   check its command list lacks Tracking Mode, Tracking Profile and Preset Zone.
   Extron's loader already reads 42 commands for it and 45 for the I20; this
   is whether GC's editor shows the same.

```
DataFile.dat size:        ________  (delta from baseline: ________; 20024 added 5,716)
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

1. **Place** — *passed for 20024 (finding 18 §8) and since*, but do it in your
   own project: add the processor, open Ethernet Port 1, and assign
   *1 Beyond IV-CAM-I20 v1.6*. The port shows TCP 5500, greyed out.
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
