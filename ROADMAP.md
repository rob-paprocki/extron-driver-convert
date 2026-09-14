# Roadmap

*Written 2026-09-11 from a deduplicated backlog. Every status claim below was re-checked against the working tree that day, then corrected for the commits that landed while it was being written. Effort: **S** is under half a day, **M** is 1–3 days, **L** is a week or more.*

All four conversion directions work offline, and 576 standard-library tests pass. The i20 driver exists in two forms:
- **`.pkp`:** `1bynd_19_20024`, 34 commands. It loads through Extron's own `LoadFromFile`, and GCP renders every command (finding 18 §8, checked by driving GCP over UI Automation).
- **ControlScript module:** 32 commands, identical wire bytes.

**"Done" today means verified offline, plus Extron's loader and the GCP editor.** Nothing has run on a processor, and no socket has ever been opened to a camera. The next milestone is a camera that moves under an Extron processor. The GCP licence is not a deadline: it renews for 30 days whenever GCP starts online and checks in with Extron (§6). The first hardware step needs no camera at all: a processor driving the driver at a PC (H1L).

**The 2026-09 pack-up is done and closed.** Everything a retired workstation held is either in this repo or, where it carries account or licence data, in the git-ignored `private/`. All 195 project source files were matched byte-for-byte and the 6,354 corpus files SHA-256 verified. `notes/2026-09-pack-up.md` records what moved where; it is history and needs nothing further.

---

## 1. Needs the user's hardware

Cheapest failure first. Each session should capture **raw reply bytes**, because a single capture fixes a parser. R3 fixed QUICKSTART and PROTOCOL on 2026-09-13; every call they give a tester now runs against the module (`experiments/skeleton_i20/doc_calls.py`).

| ID | What | Blocked by | Exact steps | What to look for | Evidence | Effort |
|---|---|---|---|---|---|---|
| H0 | Save a GCP project, then run **compile-only Build** (no camera needed) | a licensed GCP install | **Prepared 2026-09-13:** `20024` installed in a GC library and catalogued on the first launch (`DataFile.dat` +5,716 bytes, as on 09-10); what remains is steps 1–4, by hand.<br>**Save by hand, never over UIA:** Save As renamed a repo folder last time. **Set a dummy address first:** the Add Controller dialog comes pre-filled with the real processor's address and credentials, so replace it with a non-routable one before anything else.<br>1. New Project (Pro): IPCP Pro 255Q xi.<br>2. Ethernet Port 1 → `1 Beyond IV-CAM-I20 v1.2` (TCP 5500, `1bynd_19_20024`).<br>3. Save As a full path in an empty folder; keep the `.gcpro` under `evidence/` or `experiments/skeleton_i20/`.<br>4. Build. | Any build error, verbatim. No network contact during Build. | `experiments/gcp_harness/README.md` traps 4–5; STATUS item 4; offer at transcript a721b700 ~L4764, never answered | S |
| H1 | **Processor only, no camera:** import the modules | any Extron processor | 1. Put `experiments/skeleton_i20/out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py` in a ControlScript project on an xi unit (Python 3.11) and, if one is available, a non-xi unit (3.5).<br>2. Do the same with one clean generated module: Samsung serial, 9/9 wire match, 0 dangling.<br>3. Instantiate each with a dummy IP. | `SyntaxError` on 3.5: the only 3.5 check today is an f-string lint. `NameError`: finding 13 §5 shows embedded drivers call runtime-injected globals such as `ExtronTime`. `AttributeError`. | findings 14 and 17 "No module was executed"; build_i20 f-string lint only | S |
| H1L | **Processor loopback, no camera:** the processor drives the i20 driver at a PC, which records and decodes every frame | any Extron processor, and a PC on its network | Follow `experiments/loopback/README.md`: static address and a TCP 5500 firewall rule on the PC; `visca_listener.py --reply ack`; deploy `controlscript/main.py` (Path A); repeat against `--reply full`; then the H0 project pointed at the PC (Path B). | `--summarize`: every T3 string, in order, and no UNKNOWN frame. The processor log's `loopback: read` lines for the edge polls. Whether polls survive `--reply full`. The Python version line. | `experiments/loopback/`; covers H1, and H4 minus the camera | S |
| H2 | **ControlScript Path A against an i20** | processor + i20 | 1. `EthernetClass(ip, 5500)`.<br>2. Run the `main.py` from QUICKSTART. | QUICKSTART's three answers: does it move; does `Update('TrackingFraming')` return Start/Stop correctly; what does preset 83 do. | `QUICKSTART.md` "What to report back"; STATUS row "untested on hardware" | S |
| H3 | **Wire captures**, in the same session as H2 | processor + i20 | Send each probe in the table below and log request and reply. | — | PROTOCOL T3 / T3b / "Known limits"; findings 09, 13; STATUS item 6 | M |
| H4 | **`.pkp` Build → Upload → Control** | GCP licence + processor + i20 | 1. Open the H0 project and restore the real controller address.<br>2. Build, then Upload.<br>3. Run PROTOCOL T3 steps 1–16 against **20024**, not 20023.<br>4. In GC, set edge values on `ZoomPosition`, `PanTiltAngle` and `IndicatorLight`, and capture what is sent (e.g. `81 01 06 02 … FF`). | Build errors. Steps 5/7 feedback. Whether GC delivers `qualifier['Pan']` / `['Tilt']` to the script. Whether the rendered ranges (−2448..2448, −1296..1296) match the camera's real limits. | STATUS items 4–5; finding 18 "does NOT show" (widgets, PanTiltAngle shape) | M |
| H5 | Samsung QN display | Samsung QNxxLS03DAFXZA | 1. Send ChannelStep both ways: Extron `0x03` family vs Crestron `0D 00 00 12/10`.<br>2. Load `experiments/missing_ethernet/smsg_10_6738_ethernet.generated.py`; drive power and volume. | Which ChannelStep encoding the panel honours — the one known cross-vendor wire divergence. | finding 05:102-104; experiments/missing_ethernet | S |
| H6 | Automate VX | an Automate VX | 1. Send `GoToScenario.id`, `StartPT.ptDir` and `StartZ.zDir` as int and as string.<br>2. Call `GetActiveTalkers` and `ShotStatus`. | "Driver right, doc wrong" is inferred from "Extron's driver works", not measured. | finding 08:102-104, 131-135 | S |
| H7 | Biamp Tesira terminator (only if R19's offline check is inconclusive) | a Tesira | Send `DEVICE get activeFaultList` ending `\r\n`, then ending `\n`. | Which one the device answers. | finding 11:51 | S |
| H8 | Load a resource-swapped Crestron `.pkg` | 4-Series processor or VC-4; dealer agreement; D2 | Rebuild the patcher first (R29). Upload the patched Samsung Serial `.pkg` with Toolbox File Manager. | Does it instantiate? No signature gate was found on paper; the Authenticode signature is self-signed. | STATUS item 1; findings 04:84-85, 06:8-28 | M |

**H3 probe list** (send, then capture):

| probe | send | expect or decide | settles |
|---|---|---|---|
| tracking poll | `81 09 08 01 FF` after Start and after Stop | `90 50 02 FF` / `90 50 03 FF` | TrackingFraming parser (documented, never observed) |
| zoom position | `81 09 04 47 FF`, stepping through optical **and digital** zoom | nibble layout; reply vs. displayed ratio for 16384–31424 | ZoomPosition parser; finding 09's FAILED digital `ZoomPositionToLevel` |
| pan/tilt | `81 09 06 12 FF`, including at a negative pan and tilt | nibble layout, and whether negatives come back as two's complement (the parser assumes so since 2026-09-13) | `PanAngleStatus` / `TiltAngleStatus` (one shared inquiry) |
| camera output | `81 C2 09 08 FF` | documented after all, on the Intelligent Switching page: `y0 50 0S 0Z FF` (S switching, Z camera). The parser read S until 2026-09-13; confirm Z on the camera | CameraOutput parser |
| c2 custom inquiries | `{Header} c2 09 06 FF`, `{Header} c2 09 07 FF` | any stable reply | lets GroupTracking / TrackingProfile poll (2 of the 12 emulated commands) |
| zoom speed | `81 01 04 07 25 FF` from the derived driver, then Extron's stock PTZ-IP driver | derived zooms faster | Extron's speed-0 defect ([PATCH E2]); so far seen only in source |
| preset 83 (T3b) | `81 01 04 3F 02 52 FF`, then `… 53 FF` | group tracking pauses (docs) **or** presenter framing engages (Crestron driver); record the firmware version | control label |
| lightbar | `81 C1 0D 0D 0D 0D FF`, `81 C1 00 04 04 00 FF`, `81 C1 00 00 00 00 FF`; half-width both ways (`03 0F 0F 03` vs `00 0F 0F 00`) | segments light as intended | 0xC1 payload; the off-segment conflict (the i20 build follows the doc, finding 09 prefers the driver) |
| zoom absolute | `81 01 04 47 03 01 0A 02 0B FF` (T3 step 8) | repeatable stop | Crestron's driver template vs the doc's different packet (`reference/crestron-visca/COMMANDS.md:543-547`) |
| version / step | version inquiry; zoom-step commands | reply bytes | `FormatRomVersion`, `ApplyZoomPositionStep` (both PLAUSIBLE) |
| Wake | send commands with no Wake first | do they work? | the VISCA page says send Wake first; no Wake byte is known |

---

## 2. Can be done from the repo, no hardware

Ordered by value. **Blocked by: nothing, unless noted.**

### 2A. Finish the hand-off (do first)

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R3 | ~~**Fix the tester-facing docs.**~~ **Done 2026-09-13.** Every call QUICKSTART and PROTOCOL give a tester was run against the module with `extronlib` stubbed (`doc_calls.py`), which found more than this row had listed: `Focus`, `Zoom Stop` and `PanTilt Home` raise `TypeError` without their speed qualifier; `PanTiltAngle` as documented is silently discarded; `Update()` works on 12 commands, not 11 (and not the 13 this row claimed); `ReadStatus()` after a `Set` echoes the value sent, so the feedback check could not fail; and T3 step 8 paired value 6666 with the bytes of 6699 (`0x1A2B`). PROTOCOL now leads with 20024, retires the ladder, and quotes 86 + 57 checks. | Stops the first hardware session failing on documentation errors. | — | `experiments/skeleton_i20/QUICKSTART.md`, `PROTOCOL.md` | S |
| R4 | **STATUS / README / CLAUDE.md consistency.**<br>STATUS: row 10 is still "(pending write-up)"; its source, `tools/out/verdicts/three_questions_synthesis.md`, was recovered on 2026-09-11 (D9). The Answers row says "17 added" while item 6 says 19 (15 + 19 = 34). "4 staged `.pkp`" should name 20024. pkp_dump's "all 4 packages" should be 9. "~84%" is 27/32, but finding 08's final tally is 29/32.<br>README:27: "about 84%".<br>~~CLAUDE.md: "graph assembled from scratch" out of date, and "Closed by finding 12" miscredited~~ — **both corrected.**<br>findings/README.md: its list stops at 12. | These are the hand-off entry points, and each contradicts itself. | One pass over the remaining files. Re-measure the docs-only figure (R32) rather than assuming 29/32. | STATUS.md:12,14,16,32,46,109 | S |
| R5 | **Stale text inside findings.**<br>00: 16 unticked boxes.<br>02:75, 03:40/90, 04:6/46, 05:124, 07:4: still say "re-run" or "under verification".<br>08: the body still says Wake is undocumented, "22 of 32 (69%)" and "No".<br>09:99: repeats the retracted Wake claim; 09:120 says the zoom harvest is pending, but `ZOOM.md` §4 found no digital range.<br>15: "80085 is undecoded", "ladder is unrun" (both superseded by 16).<br>18: line 190 says 32 commands and the first "does NOT show" bullet says GC has not rendered them (superseded by §8 / 34); "PanTiltAngle shape is a guess" is partly superseded by 86c5acb.<br>Code comments: `build_i20_assets.py` docstring says 31 / 17; `pkp_build.py:11` cites "STATUS open item 4", which is now a different item; `pkp_validate.py` gap (1) says the repo does not ship `ExtronDH.dat`, but `validator_differential/ilres/` now holds it. | A reader who skips headers gets the wrong answer, and the open work looks larger than it is. | Add a one-line "resolved by finding NN" pointer beside each; rewrite finding 08's body inline. | grep results as cited | S |
| R6 | **Results that no finding records.**<br>Finding 10 resolution: the Clock Audio 5940 mis-pairing, 82.7% agreement vs 100% fidelity-to-source, and the `SRBG` typo (in no finding).<br>Finding 07 correction: the `.usp` is a dispatcher; the logic lives in a SimplSharp DLL whose wire strings are readable from its `#US` heap.<br>The three-questions experiments (crestron2cs, missing_ethernet, docs_only) have no finding — but their synthesis is recovered (`tools/out/verdicts/three_questions_synthesis.md`), so finding 10 can now be written from it.<br>missing_ethernet's `MultiviewCommand` slot residual is unexplained.<br>`experiments/docs_only/REPORT.md`, cited by `generator.py:23` for the protocol-integrity disclosure, is missing.<br>The Tesira speed-dial double-quoting bug (`ttp_validation.md`) is not in finding 11.<br>86c5acb's three contract bugs appear only in the commit message. | The claims exist only in `tools/out/verdicts/` or commit text. | Write the finding 10 / 07 sections from `heldout_synthesis.md` §1, §4–§6 first. | `heldout_synthesis.md`; grep | M |
| R7 | **Remove the tracked temp directory** `experiments/skeleton_i20/out/.ptmp3A0FB0/` | A glob over `out/` could copy it into Driver3. | `git rm -r`, add `.ptmp*/` to `.gitignore`, then check that `pkp_build` cleans its temp file on failure. | `git ls-files` | S |

### 2B. Make the measurements reproducible and trustworthy

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R8 | **Decide whether finding 14's join rule is the right one.** Reproduction is now settled. On 2026-09-11 the committed `build_index.py` — first substring match, then `break`, whatever the vendor — could not reproduce its own committed output under any module order: rebuilding from `corpus/` gave 312, 311 or 310 packages instead of 314 (`evidence/test-logs/oracle_repro_*.log`). The committed output matches a *first vendor-consistent match* rule exactly (314 packages, 352 pairs), so `build_index.py` now implements that rule and `test_build_index.py` pins it, including that which packages pair no longer depends on order. Still open: the rule takes the first same-vendor substring hit, so it can pick the wrong model within one vendor (the Clock Audio 5940 class). | 80.9% rests on this join. | Try "same vendor, longest match"; diff the pair set against today's 352 and inspect every pair that changes. | `build_index.py` `match_models`; `experiments/oracle_pairs/test_build_index.py` | S |
| R9 | **Post-fix validator differential, run anywhere.** Extron's verdicts are already captured (`real_all.txt`), so only mutants and new packages need Extron's DLL. | STATUS and finding 16 still quote the pre-fix 1,900 / 1,919. After the fixes, only the disagreeing cases were re-checked. | Rewrite the paths in `all_pkp.txt` to `corpus/extron-driver3/`, re-run `runpy.py`, diff against `real_all.txt`, and classify each of the 19 disagreements. | `validator_differential/README.md` | S |
| R10 | **Wire `guidtable.tsv` into `pkp_validate`** as an optional `--guid-table` (4,775 GUID → SHA-256 rows, already extracted) | Turns pre-13.x `80086` predictions into measurements. | Load TSV → `{guid: bytes.fromhex(d)}`, re-run finding 16 §5c's three GUID-dependent packages, rewrite docstring gaps (1)/(2). Keep the TSV out of git until D1. | `guidtable.tsv` header; `pkp_validate.py:81-83` | S |
| R11 | **Fix the two silent compare failures:** `extr_31_1685` (MediaPort 200), `extr_31_6096` (MediaPort 300), `TypeError: unhashable type: 'dict'` | This is why 314 becomes 312: the same silent-exclusion shape as finding 14's harness bugs. | Run `wire_table.diff_tables` on the pair, write a failing test, fix it, re-score. | `scorecard.json:4359, 4619` | S |
| R12 | **Attribute finding 14's differences.**<br>Split version skew from mistranslation (930 differing, 292 only-in-shipped).<br>Triage the 292.<br>Test the presumption that broken modules score higher (146 dangling calls, 77 packages, 23 with perfect tables).<br>Slice the scorecard by the fitted-rule residuals `gc-safetoset-boolop-guard-*` and `serial-over-ethernet-mixin-generalised`. | 80.9% currently mixes library skew with translator error. Two rules are fitted on one sample each. | Add a version-match column (package `vX_Y_Z` vs module `vX_Y_Z_W`) to `build_index.py`; bucket `only_in_b`. | finding 14 "does NOT show" and §3; `heldout_synthesis.md:39` | M |
| R13 | **Offline execution harness.** Use extronlib stubs from the vsix (`corpus/vendor-tooling/controlscript-1x13x0-6.vsix`; the unpacked copy in `tools/out/vsix` is git-ignored). Import every generated module, call Set/Update with sample and adversarial values (spaces, quotes, empty), and capture `Send`. Include `ross_ultrix_generated_by_pkp2cs.py`. | All translator evidence so far is static. Value-dependent bugs such as the Tesira double-quoting are invisible to `wire_table`. | Stub `extronlib`, then run it over the six scorecard pairs. | findings 14 and 17 "No module was executed"; `ross_ultrix/README.md` "Not done" | M |
| R14 | **Score the two 1 Beyond camera oracle pairs** (`samples/1 Beyond Cameras/PTZ-IP12_IP20`, `AutoTracker3`) | A device class the translator has never seen. Proposed twice, never run. | `pkp2cs` on both; `diff_tables` against the shipped `onebynd_camera_*.py`. | `1bynd_19` has 0 hits in `pair_index.json` and `scorecard.json` | S |
| R15 | **Corpus-wide sweep for the untested paths.**<br>Round-trip all 1,854 packages through the NRBF writer (Primitive-typed String path).<br>Look for a package with no `Manifest` child (validator gap 4).<br>Look for Emulated pre-writes embedded inside a larger expression.<br>AST-scan the embedded scripts for runtime-injected globals beyond `ExtronTime`.<br>Record the newest Python syntax Extron's embedded scripts use. | Each path raises rather than guessing, but none has met real data. | Loop `pkp_build.PackageBuilder` over `corpus/extron-driver3/*.pkp` in round-trip-only mode; count errors by cause. | `nrbf_write.py:192-205, 291`; `pkp_validate` gap (4); `pkp2cs.py:405-412`; finding 13 §5 | M |

### 2C. Translator (`pkp2cs`) correctness

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R16 | **Read the port and protocol from `EthernetProtocolAsset`** (`_port`, `_compatibility`, `_udpOutputPort`) instead of emitting `TCP` / port 0 | The residual "not recoverable from the package" fires in 178 packages (57%), yet finding 13 §4b shows the package carries these fields. No tool reads `_compatibility` today. | First survey `_compatibility` against `_port` across the corpus to pin down 64 and 512 (currently "not determined"). Then emit defaults for 16 (TCP) / 32 (UDP) and keep the residual only for the rest. | `pkp2cs.py:1636-1642`; finding 13:163-174 | M |
| R17 | **One residual per model whose protocol asset resolves to `None`, and one transport per declared asset** | 20 of Biamp's 23 models resolve to nothing, silently. Serial wins over Ethernet. CDT 100-UDP gets a TCP class. | Add the per-model residual with a test on `biam_25_150`, then emit the transports. | `heldout_synthesis.md` §2 #4, §6 #4; `pkp2cs.py:95` | M |
| R18 | **Extend the oracle:**<br>- a transport-class / connection-settings column<br>- helper-body coverage<br>- attribution of the shared `__MatchAllSubscribe` dispatcher (6 of Biamp's 11 "differences")<br>- a TTP spec-conformance check built from `reference/biamp-ttp/SYNTAX.md`<br>- a manufacturer-adjudication column<br>- held-out rows in the STATUS scorecard: Clock Audio 1777 7/7, Biamp 69/74, 5940 and Samsung ethernet "unscored" | A metric that cannot see invented wire strings or transports is how 85% hid SIS injection. | Add the transport column to `score.py` first. | `heldout_synthesis.md` §6 #3, #5, #6; finding 11; STATUS scorecard lists only 4 in-sample pairs | L |
| R19 | **Settle the Tesira `DeviceFaultList` terminator offline** | Only command out of 140+ templates using `\r\n`; the spec cannot decide it. | Pull the `#US` heap strings from `samples/Tesira/Crestron/*/BiampTesiraLib3.clz` and grep for `activeFaultList`. | finding 11:51; `.clz` present | S |

### 2D. i20 driver completeness

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R20 | **Check Crestron's I20 driver for reply rules** for `GetGroupTracking` / `GetTrackingFramingProfile`, plus `GetExposureCompensation`, `GetFocusPosition`, `GetAutoPrivacyMode`, `GetDeviceInformation`, `GetAutoSoftwareUpdate`, `GetPanTiltSpeedMax` | STATUS item 6 says the device publishes nothing for 12 commands, but Crestron's driver declares these inquiries and the derived driver never sends them. | `pkg_dump` the I20 `.pkg` and search the Responses/Rules. Stage Update methods ready for H3's capture. | `i20_wire_table.txt:78, 81` | S |
| R21 | **Check the IV-CAM-I12 model entry** | `build_i20.py:938` advertises the I12 too, but every addition was built from I20 docs (lightbar geometry; 12x vs 20x zoom). | Diff I12 vs I20 in Crestron's i12_i20 JSON and the lightbar docs. Document equivalence, or drop I12 from 20024. | finding 18 §8 Driver Manager row; `ZOOM.md` | S |
| R22 | **Shared VISCA transformations module:**<br>- move the nibble helpers out of the builders<br>- add `ParseDecimal` (rated CONFIDENT)<br>- add a `ZoomRatio` command backed only by `ZOOM.md`'s discrete 12x / 20x tables, raising on values off the table | The drivers expose only raw 0–16384. Interpolation is undocumented and must not be guessed. | Port `reference/crestron-nextgen-cameras/zoom-reconstruction/zoom_reference.py` with a test for every table row. | findings 08:176-180, 09; `ZOOM.md` §6 | M |
| R23 | **Parity with Crestron's i20 driver:** privacy, exposure compensation, focus position and mode, AutoFocus behaviour, AutoSoftwareUpdate, GetDeviceInformation, the PressAndHold / Release menu, SetFieldOfView, SetPtzSuperOperation, the discrete speed setters, GetPanTiltSpeedMax | The user asked for full parity with both back ends; the module has 32 commands. | Diff Crestron's command names against both emitters' `Commands` tables. Every new `.pkp` command must pass `build_i20_assets.py`'s agreement check. | transcript a721b700 ~L2638 | L |
| R24 | **p12/p20 variant.** Asked for at the outset; only the i20 was built. | A generalisation test as well as a deliverable. | Run `resolve_visca.py` on the P20 `.pkg` (in `samples/`). The P20 spec is in `reference/crestron-visca/`; note the 4×4 lightbar and the 4-nibble assemble. | transcript 2141be6e L252; no p20 builder exists | L |

### 2E. `.pkp` synthesis generality (final gate is `Load-Package.ps1` on a workstation)

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R25 | **Decode the `DriverAttributeEnum` bits** (values seen: 3, 19, 35, 51, 59) | Added commands copied their bits from donors. A from-scratch emitter needs to know what each bit means. | Read the enum names from `Extron.Configuration.Drivers.dll` metadata (the ECMA-335 walker in `pkg_dump` is portable). Cross-tabulate against `_attributes` across the corpus. | finding 18 "does NOT show" | S |
| R26 | **Edit kinds GC has not yet accepted:** a changed `_port` / `_compatibility`, and changed parse / response assets | Only command-table edits have been shown to survive GC. | Build two mutants of the donor and run each through `pkp_validate`, `Load-Package.ps1 -Deserialize`, and the port GCP displays. | findings 12 and 13 §4b | M |
| R27 | **Cross-package cloning:** `pana_19_5702`'s `PanTiltAbsolutePosition` into the i20 donor, importing the class records, positive object ids only | Every clone so far stays inside one package family. | `pkp_asset` clone, then `Load-Package.ps1`. | finding 18 "does NOT show", §6 | L |
| R28 | **A graph assembled from scratch:** one model, one command, and an `EthernetProtocolAsset` built from nothing | The last structural unknown for a general `.py` → `.pkp` emitter. | Gate the result through `pkp_validate` → `Load-Package.ps1 -Deserialize` → `gc_catalogue`. | findings 16:145-147, 13 §4b; `pkp_build.py:11` | L |
| R29 | **Commit the strategy-A `.pkg` resource patcher** (`tools/pkg_patch.py`). Finding 06's patch at offset `0x1068` ran only in `/tmp`. Growth past 1,653 bytes, the rename cascade and re-signing were never built. | H8 has nothing to load without it. | Reuse `pkg_dump`'s metadata walk; test against the Samsung Serial DLL. | finding 06:8-28; no patch tool in `tools/` | M |
| R30 | **An optional test that uses Extron's own loader:** a stdlib test that shells out to `Load-Package.ps1` / `harness.exe` when present and skips otherwise | The two bugs only Extron's code could see were caught by hand. Offered, never answered. | Wrap `Load-Package.ps1 -Path out/*.pkp` behind a platform / existence check. | transcript a721b700 ~L2091 | M |

### 2F. Crestron side and desk research

| ID | What | Why it matters | First concrete step | Evidence | Effort |
|---|---|---|---|---|---|
| R31 | **A package-level V2 pass in crestron2cs** listing every IL-only transformation (I20: 6; P20: 12 undeclared of 39) | Today it raises on the first one only (`crestron2cs.py:247`), and it has only ever run on Samsung. | Take referenced names minus declared transformations, and check the result against the lists in findings 07 and 08. | finding 07:47-49 | S |
| R32 | **Re-measure docs-only generation.** Fetch the 11 missing Automate VX pages; `API-Reference` has 35 files and `endpoint_crossref.txt:77, 88, 135` still marks Wake as a gap. Re-run `analyze_endpoints.py`. Fix the generator's dict-to-scalar status writes and its missing double JSON decode. | The "~84%" cannot be reproduced from the repo. | Fetch the URLs named in finding 08's header. | finding 08 header; transcript 22114bf1 L889, L960 | M |
| R33 | **Desk research:**<br>- Automate VX ISO-record deprecation (release notes)<br>- which toolchain strategy B needs (VS2008 / .NET CF?)<br>- how Control4 / Savant driver houses ship across vendors<br>- GC Plus vs Pro<br>Report each as found or "not found by method X". | Each is an unverified claim or an unanswered question. | One search each. | findings 08:36-41, 06:44, 00:13; 22114bf1 L202 | S |
| R34 | **Read the Ross Ultrix plugin tier** (`plugin_ross_ultrix.py`, `tools.py`'s `__InterfaceWrapper`) as input to an IR | The only practitioner example of the IR idea. `tools.py` was mapped, not read. | Write down the responsibilities an IR would need to carry. | finding 17 "does NOT show" | M |
| R35 | **Extron → Crestron Samsung JSON regeneration test** (no emitter exists; `DriverDefinition` appears only in the `pkg_dump` reader) | An offline acceptance test for the Crestron emitter. | **Blocked by D2**, per STATUS item 2 ("ask before building an emitter"). | finding 04:106-108 | M |

---

## 3. Needs a decision or credentials from the user

| ID | Decision | Why it matters | What unblocks it | Evidence | Effort |
|---|---|---|---|---|---|
| D1 | **Binaries and vendor resources in git — decided by the owner's instruction, reversible only by a history rewrite.** `experiments/validator_differential/` (four compiled `.exe`, ~130 mutant `.pkp`, `guidtable.tsv`, `ilres/ExtronDH.dat` — a resource of a licensed assembly) and `evidence/` (catalogue snapshots, `Work.zip`) were committed in `6eb1118` under "pack everything up … get it set up in the git repo … i mean everything". | If any of it should not be in history, a `.gitignore` no longer helps. | Confirm, or ask for `git filter-repo` on named paths. | `du`; `git status` | S |
| D2 | **Licensing.** Crestron: the user said "I work for a Crestron dealer/partner org, so I presume I'm okay". Confirm the agreement covers cross-vendor tooling, then update STATUS item 2. Extron: nothing records whether a modified Extron `.pkp` (20024 is `1bynd_19_4743` with its script replaced) may be deployed at another site. | Gates R35 and H8, and the i20 deliverable itself. | The org's agreement or counsel; the Extron Insider / GC EULA clauses. | STATUS item 2; finding 04:165-192; transcript 2141be6e L252 | S |
| D3 | **Log in to `drivers.crestron.io`** (user-driven browser, no bulk crawl) | Catalogue coverage has only 2–3 data points. The same session can fetch Automate VX's missing `.csp` and any switcher `.pkg` (D5). | Pull a stratified sample of 15–30 `.pkg`, then `tools/pkg_dump.py <dir> --summary`. | STATUS item 3; finding 07:61-65, 85-87 | M |
| D4 | **Scratch-accessor policy:** attempt the `qualifier['Number']` / `['Name']` rewrite, or keep failing loudly | 5 residuals in-sample, but 146 calls in 77 packages at scale (≈25% of modules would raise). | Yes or no; if yes, derive the rule from the shipped DTP3 module, test-first. | STATUS scorecard note; finding 14 §3 | L if yes |
| D5 | **Which Crestron first-party switchers** to target | Named as the user's main interest, alongside 1 Beyond. There are no samples. | Drop the `.pkg` files into `samples/`; classify them with `pkg_dump`. | transcript 2141be6e L252 | L |
| D6 | **Build the hub-and-spoke IR?** | Recommended (finding 04:87-104) and justified (STATUS), but it does not exist. Decides whether R35 is worth doing. | Go / no-go. If go, start from `resolve_visca.py` plus `DriverDefinition` sections. | findings 04–06; no IR module in the repo | L |
| D7 | ~~**GCP licence: what is the real term?**~~ **Resolved 2026-09-13, by the owner:** the licence renews for 30 days each time GCP starts while online and can check in with Extron's servers. That is why the status bar read "Expires in 30 Days" on 09-07, 09-09, 09-10 and 09-13, and why the ~2026-10-07 date was never real. | A licensed GCP is the gate for H0, H4 and the render check. | Start GCP online at least once a month. | §6 | — |
| D8 | **Report defects to Extron?**<br>- zoom speed 0 in `1bynd_19_4743` and AutoTracker3<br>- the `SRBG` typo in `clau_25_5940`<br>- `LogoAssignment` in DSC 12G-HD<br>- Tesira speed-dial quoting<br>- **the `.eir` filename check that skips hashing** (security-relevant; private disclosure) | Nothing in the repo promises it; listed so it is decided rather than forgotten. | Yes or no, recorded in STATUS. | findings 13 §3, 16 §5b; `pkp_validate.py` gap (2) | S |
| D9 | **Mostly resolved: the synthesis documents.** `.gitignore`'s `tools/out/` rule kept every verdict out of git. Fixed, and the saved results of all 14 workflow runs from the first session plus finding 10's `three_questions_synthesis.md` were recovered and committed under `tools/out/verdicts/` (`6eb1118`). | Some claims can't be checked, e.g. finding 09's "1 uncertain". | Map each finding (02, 04–09) to the run it was written from (`tools/out/verdicts/workflows/22114bf1/`); mark any with no surviving source. | `.gitignore` provenance note | S |
| D10 | **Sample provenance.** `notes/sample-provenance.md` has one "(pending)" row. | Findings are meant to cite where each sample came from. | Claude fills in versions with `pkp_dump` / `pkg_dump`; the user supplies each source. | `samples/README.md:12-13` | S |
| D11 | **A Clock Audio MK3 ControlScript module.** The GS shipment holds only `clau_dsp_CDT100_v1_0_3_0.py` (the 1777 module). | Without one, `clau_25_5940` stays unscored. | Extron Insider or Clock Audio. | `heldout_synthesis.md` §6 #7 | S |
| D13 | **Claude session transcripts in git?** They are in the git-ignored `private/claude/` (this project's) and at `Z:\.claude\projects\` (the first session). Copying the first session's transcripts into the repo was refused by the permission classifier, and was not routed around. | They hold full tool output, account details and lab IPs — and the reasoning behind several findings. | The owner's call. |  | S |
| D12 | **Install commit-identity pinning** (the per-folder gitconfig with `includeIf`, the credential helper, and `identity-guard.sh`) | Git needs `user.name`/`user.email` and cannot always auto-detect them, so a fresh checkout refuses to commit until identity is set by hand. | User action, then a dry-run commit and push. | `ENVIRONMENT.md` troubleshooting | S |

---

## 4. Deferred by the user

| Item | What was said | State now | When it returns, first step | Evidence |
|---|---|---|---|---|
| **IR** | "we'll deal with IR another day" | Ambiguous: it followed a discussion of `.eir`, but IR is also this project's term for the intermediate representation (D6). No parser exists for `.eir` (26 in corpus) or Crestron `.ir`; `pkp2cs` has no IR or relay dialect. | Ask which IR was meant. If infrared: run `pkp_dump` over the 26 `.eir` files and the Samsung `.ir` member, then write a finding. | transcript a721b700 ~L2559; findings 03:14, 07:126 |
| **Extron → Crestron direction** | "I don't have a VC4 or any Crestron processor to hand"; the main interest is Crestron gear driven by Extron processors | Deprioritised. | H8, R29, R35 | transcript 2141be6e L252 |
| **Crestron catalogue sampling** | Offered repeatedly; user redirected to the i20 | Not done. | D3 | 22114bf1 L1120, L1513; 2141be6e L246 |
| **Offers never answered** | Compile-only GCP Build; the validator as an optional test | Not done. | H0, R30 | a721b700 ~L4764, ~L2091 |
| **ControlScript framework doc** | "I'm also attaching the Controlscript framework doc"; the attachment never arrived | The vsix apidocs cover part of it. | Ask whether it is still needed. | 22114bf1 L1088, L1108 |

---

## 5. Open research questions and unmeasured claims

| Claim or question | Current basis | Settled by |
|---|---|---|
| An outsider-built or resource-swapped `.pkg` loads on 4-Series | Documentation only | H8 |
| Share of Crestron's catalogue that is JSON-engine vs V2 vs V1 RAD | N = 2–3 | D3 |
| Two vendors converge on **undocumented** protocols | Shown only for Samsung (published protocol) and i20 (partly documented) | D3 sample plus a `wire_table` diff |
| Automate VX: Extron vs Crestron | Untestable without the `.csp` | D3 |
| Docs-only generation reaches ~84% | Stale (27/32); finding 08 says 29/32 | R32 |
| ISO-record APIs are deprecated | The owner's reading | R33 |
| String-typed Automate VX parameters are right | Inferred from "Extron's driver works" | H6 |
| ChannelStep: which encoding the Samsung panel honours | Two conflicting implementations | H5 |
| Finding 09: `FormatRomVersion`, `ApplyZoomPositionStep` PLAUSIBLE; digital zoom FAILED; one claim "uncertain", unnamed | Documentation reconstruction | H3, D9 |
| Lightbar off-segment encoding | Doc vs driver conflict | H3 |
| Preset 83 label | Doc vs driver conflict | H3 (T3b) |
| Extron's zoom-speed-0 defect | Static reading only | H3 |
| CameraOutput, ZoomPosition and PanTilt reply layouts | Inferred | H3 |
| 12 of 19 added commands cannot be polled | Checked against documentation only; Crestron declares c2 09 06/07 | R20, H3 |
| I12 behaves like the I20 | Assumed | R21 |
| The emitters are Python 3.5-safe | f-string lint only | H1, R15 |
| Globals the runtime injects beyond `ExtronTime` | Only one identified | R15, H1 |
| `_compatibility` 64 / 512 meaning | "Not determined" | R16 |
| `DriverAttributeEnum` bits | Copied from donors | R25 |
| GUID table coverage; whether GC loads it before `Validate`; `ComputeHash(Stream)` callers outside one assembly; non-`byte[]` and no-Manifest paths | Read from IL, never observed | R10, R15, a Windows-box caller scan |
| Broken modules score higher because scratch accessors compose payloads | "Presumably" | R12 |
| How much of the 930 / 292 differences is version skew | Unknown | R12 |
| `__SafeToSet`-BoolOp else rule; SerialOverEthernet mixin | Fitted on one sample each | R12 |
| Tesira `DeviceFaultList` terminator | Unresolved by the spec | R19, H7 |
| The plugin tier generalises to a cross-vendor IR | One integrator, one device | R34 |
| GC Plus and Pro packages differ | Only Pro was examined | R33 |
| Strategy B needs VS2008 / .NET CF | Verifier marked UNCERTAIN | R33 |
| GCP licence expiry | Settled (D7): a rolling 30 days, renewed whenever GCP starts online | §6 |

---

## 6. Clocks and machine-bound constraints

### Clocks

| Clock | What is known | Action | Effort |
|---|---|---|---|
| **GCP Pro licence** | **A rolling 30 days, renewed each time GCP starts while online and checks in with Extron's servers** (the owner, 2026-09-13). That is why the status bar has read "Expires in 30 Days" on every day it was checked. | Start GCP online at least once a month; a workstation kept offline for 30 days loses it. | S |

### What needs a licensed GCP install

Everything else on a workstation — the loader, the validator, the IL scans —
needs only the Extron DLLs and 32-bit PowerShell, which are not licence-gated.
`ENVIRONMENT.md` has the full capability table. Only these two need the licence:

| Capability | Used by |
|---|---|
| GCP render check over UI Automation — 12 verified steps live in `experiments/gcp_harness/scratch/`, **not yet consolidated into one script**. Worth making `Render-Package.ps1`, restoring the catalogue backup on exit (M). | every new package: R23, R24, R26–R28 |
| GCP Build and Upload (Upload also needs a processor) | H0, H4 |

Everything in `tools/`, the corpus reproductions, and all of 2B–2D except the
final loader gates run anywhere Python 3 does.

### Standing constraint

Nothing in this project has run on a processor, and no socket has ever been
opened to a camera. Treat "renders correctly in the editor" as one gate short of
working, the same way the wire table was one gate short of a runnable module.
---

*Produced by workflow `wf_61d1161c-2c8` (script in `tools/out/verdicts/workflows/`): five readers over the findings, code and three session transcripts, two independent sweeps of the C: drive, a completeness critic, and a synthesis pass that re-checked each claim against the tree. Corrected afterwards for commits that landed while it ran.*
