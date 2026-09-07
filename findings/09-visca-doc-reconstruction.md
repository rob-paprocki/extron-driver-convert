# Finding 09 — can documentation close a known compiled-code gap?

**Partly, and the boundary is sharp enough to design around.**

The experiment: six Transformations in Crestron's 1 Beyond camera drivers exist
only as compiled IL. Could Crestron's own VISCA documentation reconstruct them
*without* decompiling — which the SDK licence bars anyway?

**32 confirmed, 4 overstated, 1 refuted, 1 uncertain.**

## The calibration result — do this first, always

The 26 *declared* transformations have their definitions visible in the driver
JSON, so they are a control group with known answers. Scoring the documentation
against them, before trusting it on the six unknowns:

| | count |
|---|---|
| FULLY PREDICTABLE | 12 |
| PARTIALLY | 5 |
| NOT PREDICTABLE | 9 |

**46% strict, 56% weighted.** The documentation earns *real but conditional*
trust — and the failure pattern is the useful part:

- ✅ **Protocol-level conventions it gets right**, byte for byte: on/off `0x02`/`0x03`,
  focus/pan/tilt direction codes, exposure-mode codes, the zoom-speed 0–7 nibble
  range, pan/tilt speed ranges, the `1 angle = 14.4` constant, `CAM_MountMode`
  Stand/Ceiling, reserved-preset-to-hex, tracking-profile presets 105–108.
- ❌ **Device-specific curves and proprietary codes it gets wrong or omits
  entirely**: the zoom-position-to-field-of-view polynomial, the model-code table,
  autofocus sub-modes.

> **The single most useful signal:** `ZoomPositionToFieldOfView` and
> `FieldOfViewToZoomPosition` — the closest *documented* analogues to the
> undeclared zoom family — both scored NOT PREDICTABLE. The calibration predicted
> the reconstruction would fail on exactly the transformations it did fail on.

## The calibration also caught the documentation being wrong

`MapIndicatorLightToLedBar` is declared, so its answer is visible. The driver
sends `0x00` for every "off" lightbar segment. The documented Lightbar table
requires an off segment to **retain its colour's 2-bit code** — `0x01` red,
`0x03` yellow. The driver only agrees with the doc for green, whose off-code
happens to be `0x00`.

By this project's standing principle — a shipped driver records what the hardware
does, documentation records intent — the driver is the better evidence. Either
way: **documentation is not an oracle, even where it looks authoritative.**

## Reconstruction verdicts

| transformation | verdict |
|---|---|
| `ViscaAssemble2LowerNibbles` | **CONFIDENT** — algorithm derived and numerically verified |
| `ParseDecimal` | **CONFIDENT** |
| `ApplyZoomPositionStep` | PLAUSIBLE — role pinned by JSON, internal rule under-determined |
| `FormatRomVersion` | PLAUSIBLE — same |
| `ZoomLevelToPosition` | PLAUSIBLE for 1×–20× · **FAILED** for digital 20×–320× |
| `ZoomPositionToLevel` | PLAUSIBLE for 1×–20× · **FAILED** for digital 20×–320× |

The optical range was recoverable by interpolating the documentation's own 20×
Zoom Ratio table (position 0–16384). The digital range (position 16384–31424) is
documented nowhere.

**One finding materially reduces the damage:** `ZoomLevelToPosition`'s output
above 20× is *provably dead code* — Rule 21 always overrides it with a literal
`16384`. That was established from the driver's own control flow, not guessed. So
only `ZoomPositionToLevel`'s digital-range gap is functionally live, and it feeds
device-polled feedback rather than outbound commands.

## An important tension between two dimensions, unresolved rather than smoothed

The reconstruction dimension rates `ViscaAssemble2LowerNibbles` CONFIDENT. The
delta dimension found it is invoked **only against an undocumented `c2 09 06/07`
"custom inquiry" register block with zero coverage anywhere in the 16-page doc
set** — so the hoped-for "fill the hole" outcome there is *untestable*, not
confirmed.

Both can be true: you can confidently know **how** it packs nibbles while having
no documentation for **what** it is packing. Recorded as-is; do not collapse it.

The documentation also never narrates the nibble-packing rule in prose at all —
it expresses it only typographically (`0p 0q 0r 0s`). The one page with a worked
prose example, Lightbar, uses a *different* 2-bit sub-field scheme, making it a
negative control rather than a template.

## The doc-vs-driver delta reproduces — a third time

Both camera drivers carry a large **undocumented vendor-extension command
family** — autofocus behaviour and sensitivity, auto-software-update, group
tracking, tracking-framing-profile, `Identify` — riding on the same VISCA `c2`
envelope Crestron's docs reserve for "Intelligent Switching", at disjoint
sub-opcodes. A second, silent extension family layered on a documented one.

That is now three independent confirmations of the same pattern:

1. **Samsung** — two vendors encoded the same *undocumented firmware bug*.
2. **Automate VX** — Extron calls five endpoints with no doc trace, incl. `Wake`.
3. **1 Beyond** — a whole undocumented command family, plus a documented table
   the driver contradicts.

## What a converter should therefore do

Not "consult the docs" and not "give up". Specifically:

1. **Enumerate** referenced-minus-defined transformations from the JSON — the gap
   is always exactly knowable.
2. **Special-case the protocol-level ones.** They are a small reusable per-vendor
   set and the documentation reconstructs them reliably.
3. **Fail loudly on device-specific curves.** Do not interpolate a polynomial from
   a doc table and ship it as if it were the vendor's.
4. **Check whether the gap is live.** The dead-code discovery turned one of six
   holes into a non-issue; that analysis is cheap and worth doing every time.

Documentation is a real input. It is not a substitute for the artifact, and the
calibration step is what tells you which is which — **run it every time, on the
declared set, before trusting a doc on the undeclared one.**

*(The full NextGen Cameras doc set is being harvested separately; if it carries
the digital-zoom position range, the two FAILED verdicts may improve.)*
