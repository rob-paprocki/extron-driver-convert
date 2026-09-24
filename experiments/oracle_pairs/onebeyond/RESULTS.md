# ROADMAP R14 — the two 1 Beyond oracle pairs, scored

**Status: measured**, this session, with `score_onebeyond.py` in this directory.
Method: `tools/pkp2cs.py` translation → `tools/wire_table.py` `diff_tables` (the
wire-string acceptance oracle, per `STATUS.md`) → residual-reason accounting →
`pkp2cs.find_dangling_self_calls` (the runtime-resolvability check), exactly as
`experiments/oracle_pairs/score.py` runs it for finding 14, applied directly to
two explicit pairs read from `samples/` rather than to a corpus-built index.
Neither `score.py`, `tools/pkp2cs.py` nor `tools/wire_table.py` was modified.

## Why these two never appear in `out/pair_index.json` / `scorecard.json`

`experiments/oracle_pairs/build_index.py` joins `corpus/extron-driver3`
against `corpus/extron-gs-modules` by model name. Checked directly against the
committed corpus snapshot in this session:

- `corpus/extron-driver3` contains exactly **one** `1bynd_19*` package —
  `1bynd_19_20024_v1_0_0.pkp` — and its `DriverModelAsset` names are
  `IV-CAM-I12` / `IV-CAM-I20` (parsed with `pkp_dump.PkpParser`, same method
  `build_index.py` uses). That is the i12/i20 donor package findings 13/14
  discuss, not either package asked for here.
- Neither `1bynd_19_4743_v1_0_1.pkp` nor `1bynd_19_4741_v1_0_1.pkp` is present
  anywhere under `corpus/extron-driver3` (checked by filename).
- The **shipped modules** for both *are* in the corpus, and are byte-identical
  (SHA-256, `samples/` copy vs `corpus/extron-gs-modules/09062026/` copy):
  - `onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py`:
    `f23531d0b7353c9c7343934e2ad9e87efb9b1769c6c8421ec9e0ab791dd6cd2d`
  - `onebynd_camera_AutoTracker_3_v1_0_1_1.py`:
    `0d12dafbd808f02b5832f7589df70e51b94c36e0f2155034fcb71c5a56cde11a`

So `build_index.py`'s model-name join (`PTZ-IP12` → normalises to a substring
of `onebyndcameraptzip12ip20v1000`; `AutoTracker 3` likewise) would very likely
have matched these two, had the `.pkp` side been present. **This is a corpus
acquisition gap** ("not found by method X": these two `.pkp` files are absent
from the committed `corpus/extron-driver3` snapshot), not a failure of the
join algorithm and not a claim that Extron never shipped them — `samples/`
itself is the counter-evidence that they exist. Reported per
`experiments/oracle_pairs/onebeyond/score_onebeyond.py`'s docstring and this
file; `pair_index.json`/`scorecard.json` were not edited (out of scope).

No `wire_table.py` "unhashable type: 'dict'" TypeError was hit in this run
(`score_onebeyond.py` carries a name-only-diff fallback for it regardless, in
case a concurrent fix to that file was mid-flight when this ran — it was not
exercised).

## Per-pair results

### PTZ-IP12_IP20 (`1bynd_19_4743_v1_0_1.pkp` ↔ `onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py`)

This `.pkp` is also **the donor of the i20 package** (`experiments/skeleton_i20/`,
per finding 13).

| | |
|---|---|
| shipped commands | 13 |
| generated commands | 13 |
| shared | 13 |
| **wire-matching** | **13 / 13 (100%)** |
| differing | **0** |
| only in generated | 0 |
| only in shipped | 0 |
| residual entries | 30 |
| dangling `self.X()` references | **0** |

Shared/matched command set: `AutoExposure, AutoFocus, Backlight,
ConnectionStatus, Focus, Gain, Iris, PanTilt, Power, Preset, Shutter,
WhiteBalance, Zoom`. No differences to classify (version skew / translator
error / Extron editorial / other) — the table is a perfect wire-shape match,
zero rows in `diff_tables()["differences"]`.

Residuals by reason (all "documented, deliberate rewrite" categories from
finding 14's taxonomy — none are `dangling-self-call`):

| reason | count |
|---|---|
| `gc-dual-status-no-target` | 10 |
| `gc-config-parsing-dropped` | 6 |
| `gc-dual-status-emulated-prewrite-dropped` | 5 |
| `gc-sethelper-updatehelper-fixed-template` | 2 |
| `gc-onconnected-ondisconnected-superseded` | 2 |
| `extron-editorial-omission` | 2 |
| `model-declares-multiple-transports` | 1 |
| `onconnected-ondisconnected-synthesized` | 1 |
| `serial-over-ethernet-mixin-generalised` | 1 |
| **total** | **30** |

### AutoTracker3 (`1bynd_19_4741_v1_0_1.pkp` ↔ `onebynd_camera_AutoTracker_3_v1_0_1_1.py`)

| | |
|---|---|
| shipped commands | 16 |
| generated commands | 16 |
| shared | 16 |
| **wire-matching** | **16 / 16 (100%)** |
| differing | **0** |
| only in generated | 0 |
| only in shipped | 0 |
| residual entries | 29 |
| dangling `self.X()` references | **0** |

Shared/matched command set: `AutoExposure, AutoTracking, Backlight,
ConnectionStatus, Focus, FocusMode, Home, Iris, PanTilt, PanTiltReset, Power,
PresetRecall, PresetReset, PresetSave, Shutter, Zoom`. Also a perfect wire-shape
match; no differences to classify.

Residuals by reason:

| reason | count |
|---|---|
| `gc-dual-status-no-target` | 10 |
| `gc-config-parsing-dropped` | 6 |
| `gc-dual-status-emulated-prewrite-dropped` | 4 |
| `gc-sethelper-updatehelper-fixed-template` | 2 |
| `gc-onconnected-ondisconnected-superseded` | 2 |
| `extron-editorial-omission` | 2 |
| `model-declares-multiple-transports` | 1 |
| `onconnected-ondisconnected-synthesized` | 1 |
| `serial-over-ethernet-mixin-generalised` | 1 |
| **total** | **29** |

*(2026-09-23, re-run after ROADMAP R16/R17: both packages declare a Serial
and an Ethernet protocol asset, which the translator now finds and emits
both wiring classes for, so `dialect-transport-not-evidenced` and
`ethernet-connection-settings-not-recoverable` became
`model-declares-multiple-transports` and `serial-over-ethernet-mixin-generalised`
in both tables. The wire results and residual totals are unchanged.)*

*(2026-09-23, later, after ROADMAP R13's runtime checks: both packages gain
two residuals, totals 32 and 31. `helper-signature-carried`: their GC
`__SetHelper` takes `queryDisallowTime=0.1` and calls pass it, so the fixed
template now keeps the parameter; before, those calls would have raised
`TypeError`. `unassigned-self-attribute`: both generated modules read
`self.DeviceID`, the VISCA camera address, which only GC's dropped
`configs[...]` parsing sets. **As translated, neither module would run: the
first command to read `DeviceID` raises `AttributeError`.** A perfect wire
table and zero dangling calls did not show it (ROADMAP R41).)*

Both pairs land exactly where finding 14's aggregate result predicts for a
"clean" package: zero missing/extra commands, zero dangling calls, and a
residual profile drawn entirely from the same nine documented, non-fault
categories finding 14 already catalogued at scale (no new reason strings
appeared). Two more data points for the **138/312 "perfect table" packages**
bucket in finding 14 §2, now including a hardware family closer to the i20
work than anything in finding 14's original run (whose scorer skipped these
two for the corpus-coverage reason above).

## The zoom speed-0 defect (finding 13 §3) — does the scoring see it?

**No — `Zoom` scores as a perfect wire-table match in both pairs, exactly like
every other shared command** (`zoom_in_shared: true, zoom_in_differing: false,
zoom_diff_detail: null` for both, in `results.json`).

Why: finding 13 §3 describes a bug in **Extron's shipped module** — `SetZoom`
computes `speed` (direction + the qualifier's Zoom Speed, 0–7) but then packs
`ValueStateValues[value]` (the bare direction byte) into the wire command,
discarding `speed`. This scoring run confirms **`tools/pkp2cs.py`'s generic
translator (`translate_pkp`, exercised here and by `score.py`) reproduces that
same defect rather than fixing it** — the generated `SetZoom` in this run is
line-for-line the same logic as shipped (`speed += ValueStateValues[value]`
computed and then discarded; `ZoomCmdString = pack('>6B', ..., 
ValueStateValues[value], ...)`, `speed` unused), differing only in cosmetic
hex-vs-decimal literal formatting (`0x20` vs `32`, same value). Confirmed by
reading the generated module this run wrote to `<tmp>/onebeyond_gen/`
(not committed — see script docstring) against
`samples/1 Beyond Cameras/PTZ-IP12_IP20/Controlscript/onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py`
lines 319–338.

The `[PATCH E2]` fix finding 13 §3 refers to is **not** part of
`tools/pkp2cs.py`'s generic pipeline — it is a hand-applied patch specific to
the i20 synthesis project, in `experiments/skeleton_i20/build_i20.py` (search
`ZOOM_GOOD` / `[PATCH E2]`), applied on top of / instead of the generic
translator's output when that project builds `driver_i20.py`. Running plain
`pkp2cs.translate_pkp()` against the donor `.pkp` — what this scoring exercise
and `score.py` both do — does not apply it.

Two independent reasons the scoring oracle can't surface this defect even in
principle, both already on record in `STATUS.md`/`CLAUDE.md`:

1. **The defect is present identically on both sides being compared.**
   `wire_table.diff_tables` compares the *generated* module's wire shape
   against the *shipped* module's wire shape. When both sides emit the exact
   same packed-byte expression (`ValueStateValues[value]`, `speed` unused),
   there is nothing for a structural diff to find — a bug shared by donor and
   derivative is invisible to a donor-vs-derivative diff by construction.
2. **The oracle is wire-string structure, not runtime correctness.**
   `wire_table.py` extracts the AST shape of the `pack()` call and its slot
   sources; it does not evaluate what byte value `speed` vs
   `ValueStateValues[value]` produces on real hardware. Per `CLAUDE.md` item 2
   ("acceptance is the wire-string table... wire correctness is necessary but
   not sufficient") and finding 13 §3 itself, this class of bug — same shape,
   wrong runtime value — was never something this oracle claims to catch;
   catching it needs the camera hardware test in finding 13's protocol, which
   is exactly the class of item this R14 run was told to skip.

## Files

- `score_onebeyond.py` — the script (repo-relative paths only; generated
  modules go to a temp directory, not this repo).
- `results.json` — this run's full structured output (per-pair status,
  residual detail, diff detail, dangling-call list, the zoom-speed check).
- This file.

No vendor file under `samples/` or `corpus/` was modified or copied into the
repo; the only new files are the two above and this one.
