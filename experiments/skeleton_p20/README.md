# skeleton_p20 — the IV-CAM-P12/P20 variant (ROADMAP R24)

Same shape as `experiments/skeleton_i20/` (finding 13), applied to Crestron's
1 Beyond IV-CAM-P12/P20 driver instead of the I12/I20 one, requested at the
project's outset. Nothing under `experiments/skeleton_i20/` was edited; every
i20 file this package reuses is imported as a library (see each script's
module docstring for exactly which pieces).

## What was built

| Stage | Script | Output | What it does |
|---|---|---|---|
| Resolve | `resolve_p20.py` | `p20_wire_table.txt` | Imports `skeleton_i20/resolve_visca.py` unmodified, points it at Crestron's P20 `.pkg`, writes the flattened Template chain: 77 commands, 3 literal, 74 parameterised, **0 unresolved**. |
| Diff | `diff_wire_tables.py` | `i20_p20_diff.txt` | Compares that table against `skeleton_i20/i20_wire_table.txt`, command by command. |
| Build 1 (.pkp script) | `build_p20.py` | `out/1bynd_19_20101_v1_0_0.pkp` | Derives the embedded driver from the same Extron donor (`1bynd_19_4743`, PTZ-IP12/IP20) build_i20.py uses; renames the two models to IV-CAM-P12/IV-CAM-P20. |
| Build 2 (.pkp graph) | `build_p20_assets.py` | `out/1bynd_19_20102_v1_0_0.pkp` | Adds the `DriverCommandAsset` graph nodes GC actually renders (mirrors `skeleton_i20/build_i20_assets.py`'s two-stage pipeline: script text first, then the graph objects the script's Commands table promises). **This is the deliverable .pkp.** |
| Build 3 (ControlScript) | `build_p20_cs.py` | `out/onebynd_camera_IV_CAM_P20_v1_0_0_0.py` | The standalone ControlScript module, same wire bytes, ControlScript's `SetX`/`UpdateX` host contract. |
| Tests | `test_p20_wire.py` | — | 69 checks, wire bytes against Crestron's own resolved P20 templates. **69 passed, 0 failed.** |

Run in order: `resolve_p20.py` → `diff_wire_tables.py` → `build_p20.py` →
`build_p20_assets.py` → `build_p20_cs.py` → `test_p20_wire.py`. Each script's
own module docstring says exactly which i20 file it imports and which pieces
of it are called verbatim versus cut/recombined — that reuse is the point of
this package, not an implementation detail, so it is documented at the point
of use rather than only here.

## The I20/P20 diff

Full data in `i20_p20_diff.txt` (`diff_wire_tables.py`'s output, regenerated
from both models' own compiled SchemaVersion 2.0 definitions — not from
documentation and not from either build script).

**I20-only (8 of I20's 82 commands), all reserved-VISCA-preset recalls,
absent from P20's own driver AND from `reference/crestron-visca/
Reserved-Presets.md`, which never names a P model anywhere in its 0–108
table** (the only two rows that aren't I-series-scoped are "95 OSD Menu
Toggle — All cameras" and "99 Reboot — All cameras", both already shared):

```
GetTrackingFraming, StartTrackingFraming, StopTrackingFraming   (presets 80/81)
GetGroupTracking, EnableGroupTracking, EnablePresenterTracking  (presets 82/83)
GetTrackingFramingProfile, SetTrackingFramingProfile            (presets 105-108)
```
(`EnableGroupTracking`/`EnablePresenterTracking` are I20's `TrackingMode`;
`TrackingShot`/`PresetZone`, built in i20 from documentation rather than from
Crestron's own driver, are equally absent from P20's driver and equally
unscoped to any P model in Reserved-Presets.md, so they are excluded here on
the same evidence.)

**P20-only (3 of P20's 77 commands)** — CAM_MountMode, the Stand/Ceiling mount
switch:

```
GetInverted   {Header} 09 04 A4 FF
SetInverted   {Header} 01 04 A4 {Inverted} FF
EnablePrivacyInverted   (a third Privacy variant; left unimplemented — see below)
```
`COMMANDS.md:225-226,287-288` documents this explicitly: *"CAM_MountMode ...
IV-CAM-P12 and IV-CAM-P20 only. Stand = `8x 01 04 A4 02 FF`. Ceiling = `8x 01
04 A4 03 FF`."* Confirmed independently in P20's own compiled driver: its
`MapInvertedToHex` transform maps `true → 0x03, false → 0x02` — Ceiling/Stand,
the same two values, from a second, unrelated source (the driver's IL-free
declarative JSON, not the documentation page).

**Shared (74 of P20's 77 commands): byte-for-byte identical templates on both
models, with zero exceptions** — `Shared, DIFFERENT templates (0)` in
`i20_p20_diff.txt`. Every command either driver implements that the other also
declares resolves to the exact same byte string on both. This is the finding
that made reuse possible: there was no case where "P20's version of the same
command" needed different bytes.

### The three "known differences to check" from the task, resolved

1. **Lightbar geometry (P-series: four segments of 4 = 16 lights; I-series:
   two outer of 4 + two inner of 3 = 14 lights,**
   `VISCA-Lightbar-Commands.md`**).** Checked by extracting
   `MapIndicatorLightToLedBar` (the Crestron transform that packs Width/Colour/
   Brightness into the four wire bytes) from *both* compiled drivers and
   diffing them: **byte-for-byte identical**, all 24 map entries. The
   4-byte wire format does not encode segment count at all — it is the same
   packing rule regardless of physical geometry. `IndicatorLight` is reused
   from `build_i20.py` completely unchanged; only the resulting physical
   pattern differs between the two lightbars, not any byte this driver sends.

2. **"P20 uses a 4-nibble assemble where I20 uses 2" (finding 08).** Checked
   by extracting every `Responses`/`Rules` entry that calls
   `ViscaAssemble2LowerNibbles` or `ViscaAssemble4LowerNibbles` from both
   compiled drivers. Result: **both models use `ViscaAssemble4LowerNibbles`
   identically** for ExposureCompensation, FocusPosition, ZoomPosition,
   PanTiltPosition and PtzSuperOperation replies — already what
   `build_i20.py`'s generic `_Nibbles(value, count)`/`_FromNibbles` implement
   (they take a nibble *count* as a parameter; nothing about them is
   4-specific). I20 has exactly **one** extra transform beyond that shared
   set: `ViscaAssemble2LowerNibbles`, used by exactly one response,
   `ViscaTrackingFramingProfileInquiryResponse` — i.e. `TrackingFramingProfile`,
   a command P20 does not have at all (bucket 1 above). So finding 08's "P20
   instead calls a 4-nibble variant" describes P20 lacking I20's one
   *extra*, 2-nibble-specific response, not P20 needing new code: the shared
   4-nibble helper already in `build_i20.py` covers every P20 command that
   needs nibble assembly. **No new nibble-handling code was required.**

3. **"I-series tracking/switching presets may not apply."** Confirmed --
   see bucket 1 above: `Reserved-Presets.md`'s full 0-108 table never names a
   P model, P20's own compiled driver declares none of these commands, and
   Crestron's own P20/P12 spec sheets (`P20Specs.md`, `IV-CAM-P20-
   Specifications.md`) contain no "Camera Processing / Intelligent Video
   Functions" section at all — unlike I12Specs.md/IV-CAM-I20-Specifications.md,
   which both have one. **Reported as "not found by method X" across three
   independent sources (reserved-preset table, P20's own driver, P20's own
   spec sheet), not assumed.**

### One difference the diff did NOT find, worth recording explicitly

Unlike the I12/I20 case (`I12_VS_I20.md`), **no command in the harvested
documentation or in either compiled driver is scoped to P20 but not P12, or
vice versa.** `COMMANDS.md`'s CAM_MountMode row names *both* P models
explicitly on the same line ("IV-CAM-P12 and IV-CAM-P20 only"), and
Crestron's own P20 package manifest lists
`"supportedModels":["IV-CAM-P20","IV-CAM-P12"]` with no per-command gate
anywhere else in the harvest. So `build_p20_assets.py` gives both models the
identical 38-command list — no `_trim_model`-style split, and its `verify_p20`
asserts exactly that (both model lists must equal the whole pool, the
opposite assertion from i20's `I20_ONLY` check).

## Provenance discipline

Every command implemented here is one of:

- **Present in P20's own compiled SchemaVersion 2.0 driver** (`p20_wire_table.txt`)
  — the strongest source, used wherever available (all of bucket 3 above, plus
  MountMode, Menu, Identify, Reboot, and every "parity" command).
- **Present in `reference/crestron-visca/COMMANDS.md`** with an explicit
  per-model note, used to corroborate or to supply a value table
  (CAM_MountMode's Stand=0x02/Ceiling=0x03; the lightbar packing rule).
- **Left out, with the reason recorded**, when the only source is I-series
  documentation or the i20 build's own hand-composed additions with no P20
  counterpart in either compiled driver: `EnablePrivacyInverted`/`Privacy`
  (driver behaviour, not a camera command — the same reasoning `build_i20.py`
  already gives for `Privacy`/`DisablePrivacy`), `PtzSuperOperation`/
  `FieldOfView`/press-and-hold-menu (undocumented op codes or IL-only
  polynomials, same as i20).

No command here was carried over from the i20 driver "by analogy" — every one
either resolves directly from P20's own package or cites a COMMANDS.md row
that names a P model. Where i20 and P20 happen to agree byte-for-byte (bucket
"Shared" above), that agreement is *measured*, not assumed, and the reused
code (`build_i20.patch_zoom`, the nibble helpers, `_SharedInquiry`, the
lightbar packing) is reused because the diff confirmed it applies unchanged —
not the other way around.

**Focus Position range.** Crestron's P20 package declares it in the same two
rules as the I20's — `FeedbackForZoomAndFocusRanges20` (`ModelIsP20OrI20`)
12224–17114 and `...12` (`ModelIsP12OrI12`) 15084–20664 — so the P-series
ranges equal the I-series'. The asset offers the union, 12224–20664, which the
reused script method already enforces. (The first build offered 0–65535 on the
belief that no P-series range was declared; the P20 package's own rules say
otherwise.)

## Verification

- **`tools/pkp_validate.py`**: both `out/1bynd_19_20101_v1_0_0.pkp` (script
  only) and `out/1bynd_19_20102_v1_0_0.pkp` (script + graph, the deliverable)
  report `Valid`, 0 issues.
- **Extron's own loader** (`experiments/gcp_harness/Load-Package.ps1
  -Deserialize -Commands`, 32-bit PowerShell, `BinaryFormatter.Deserialize`
  through the real `Extron.Configuration.*` assemblies — not our own model of
  the format, per STATUS.md's methodology note #4): `1bynd_19_20102_v1_0_0.pkp`
  deserializes OK and lists **38 `DriverCommandAsset` objects on both
  IV-CAM-P12 and IV-CAM-P20**, matching what the graph builder reports. Command
  list, value enums and per-parameter names all read back correctly — e.g.
  `MountMode ... Value[Ceiling/Stand]`, `DeviceModel ...
  Value[IV-CAM-I20/IV-CAM-I12/IV-CAM-P20/IV-CAM-P12/Unknown]`.
- **`test_p20_wire.py`**: 69/69 passed — driver loads without error; every SET
  command (shared and MountMode) emits the exact bytes Crestron's own P20
  driver declares; UPDATE commands emit the right inquiries and parse the
  documented replies (including a rejected undocumented MountMode reply byte,
  never guessed at); the zoom-speed fix is present and Extron's untouched
  commands are untouched; the eight removed I-series commands are provably
  unreachable (`hasattr` false, not just absent from a table); the lightbar
  and "parity" blocks are confirmed byte-identical to i20's; both `.pkp`
  stages round-trip byte-identically; the ControlScript module carries
  MountMode and not the removed commands.

### What is UNVERIFIED

Same standing gap as finding 13/`skeleton_i20`, not narrowed by this package:

- **Never run against a real IV-CAM-P12 or IV-CAM-P20.** Every command here is
  a transcription of Crestron's declarative spec for this model, checked
  byte-for-byte offline against it and against Extron's own deserializer — no
  reply has ever come from an actual camera, so status feedback in particular
  (`MountMode`'s Stand/Ceiling reply values, the model-code table, the speed
  maxima) is provisional in the same sense `skeleton_i20`'s is.
  `skeleton_i20/PROTOCOL.md`'s loopback rig (a PC playing the camera) has not
  been pointed at this driver; that is the cheapest next step, mirroring how
  i20 got its first wire-level confirmation before any real hardware was
  involved.
- **Never opened in Global Configurator's UI itself** (only through the
  scripted deserializer) — GC's own command-surface rendering, per finding 15,
  is exactly the thing the loader check stands in for but does not fully
  replace; a screenshot-level confirmation (finding 18's own bar) has not been
  done for this package.
- **The Focus Position range gap above** is a documentation gap, not a code
  bug, but it means that field's *bounds* (not its wire format) are unverified
  for this model specifically.
- **`EnablePrivacyInverted` and `PtzSuperOperation`/`FieldOfView`** remain
  unimplemented, for the same reasons `Privacy` and those same three commands
  are unimplemented in the i20 driver (see "Provenance discipline" above) —
  not oversights, but the same documented scope boundary carried over because
  the evidence for excluding them did not change between models.

## Files

```
resolve_p20.py          resolve Crestron's P20 driver -> p20_wire_table.txt
p20_wire_table.txt       77 commands, 3 literal, 74 parameterised, 0 unresolved
diff_wire_tables.py      i20_wire_table.txt vs p20_wire_table.txt -> i20_p20_diff.txt
i20_p20_diff.txt         8 I20-only / 3 P20-only / 74 shared-identical / 0 shared-different
build_p20.py             .pkp stage 1: embedded script (imports build_i20)
build_p20_assets.py      .pkp stage 2: DriverCommandAsset graph (imports build_i20_assets)
build_p20_cs.py          standalone ControlScript module (imports build_i20_cs)
test_p20_wire.py         69 wire-level checks against Crestron's own P20 templates
out/
  1bynd_19_20101_v1_0_0.pkp                script only, 38 commands promised, 14 in the graph
  1bynd_19_20102_v1_0_0.pkp                THE DELIVERABLE - script + graph, 38/38, model v1.0
  driver_p20.py                            the derived .pkp-embedded script, for inspection
  onebynd_camera_IV_CAM_P20_v1_0_0_0.py    the standalone ControlScript module
```
