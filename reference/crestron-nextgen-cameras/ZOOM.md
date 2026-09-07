Source (primary): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm
Source (specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I12Specs.htm
Source (specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm
Source (specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P12Specs.htm
Source (specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P20Specs.htm

# ZOOM — everything the NextGen Cameras documentation says about zoom

This is the highest-value digest of the harvest. **Bottom line up front: the exact
lookup table that `ZoomLevelToPosition` / `ZoomPositionToLevel` must implement is
published verbatim in the VISCA Commands page**, keyed to the two zoom-range families
(12x for I12/P12, 20x for I20/P20). See "The zoom ratio/position table" below — this
is a direct hit, not an inference.

## 1. Zoom is controlled as a 16-bit "Zoom Position" over VISCA

Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm

> "Crestron 1 Beyond cameras can be controlled using the VISCA protocol through either
> a serial (RS‑232 / RS‑485) or TCP connection. By default, the port for TCP control is
> set to 5500. For serial communication, make sure the baud rate of the controller is
> set to 9600 bps."

The `CAM_Zoom` command family (verbatim from the command table):

| Function | Command Packet | Comments |
|---|---|---|
| Stop | `8x 01 04 07 00 FF` | |
| Tele(Standard) | `8x 01 04 07 02 FF` | |
| Wide(Standard) | `8x 01 04 07 03 FF` | |
| Tele(Variable) | `8x 01 04 07 2p FF` | p: 0(Low) to 7(High) |
| Wide(Variable) | `8x 01 04 07 3p FF` | |
| **Direct** | `8x 01 04 47 0p 0q 0r 0s FF` | **p,q,r,s: Zoom Position** |
| Absolute Position | `8x 01 04 47 0t 0p 01 04 0s FF` | t:speed 0-7; p,q,r,s: Zoom Position |

And the combined zoom+focus command:

| Function | Command Packet | Comments |
|---|---|---|
| CAM_ZoomFocus Direct | `8x 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF` | p,q,r,s: Zoom Position; t,u,v,w: Focus Position |

The readback (inquiry) command:

| Inquiry Command | Command Packet | Inquiry Packet | Comments |
|---|---|---|---|
| CAM_ZoomPosInq | `8x 09 04 47 FF` | `y0 50 0p 0q 0r 0s FF` | p,q,r,s: Zoom Position |

So "Zoom Position" is a **4-nibble (16-bit) value**, transmitted as four separate
VISCA payload bytes each holding one nibble (`0p 0q 0r 0s`), exactly the shape that
would motivate a `ZoomLevelToPosition` transform: it must produce/consume that
4-nibble-packed 16-bit value. This is also almost certainly why `ViscaAssemble2LowerNibbles`
exists as a helper — assembling two hex digits (nibbles) received/sent as separate
VISCA bytes back into one byte — though the transform itself is IL and out of scope
here to decompile. Nothing in the docs additionally documents `ViscaAssemble2LowerNibbles`
by name; it is not a named VISCA/Crestron API concept in the public doc set, only an
inferable helper for exactly this nibble-per-byte VISCA encoding style.

## 2. The zoom ratio/position table (THE key data)

Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm,
under the heading "Zoom Ratio / Position (CAM_Zoom)", subheading "(CAM_Zoom Direct – p,q,r,s Zoom Position)".

Quoted verbatim (two tables on the page, one per camera zoom family):

### "12x Zoom" table (applies to IV-CAM-I12 and IV-CAM-P12 — see §3)

| Optical Zoom Ratio | Optical Zoom Ratio (hex Zoom Position) |
|---|---|
| 1x | 0000 |
| 2x | 1982 |
| 3x | 24E2 |
| 4x | 2BC9 |
| 5x | 3099 |
| 6x | 343D |
| 7x | 3724 |
| 8x | 3988 |
| 9x | 3B8B |
| 10x | 3D43 |
| 11x | 3EBB |
| 12x | 4000 |

(Note: the page's table literally has two columns both headed "Optical Zoom Ratio" —
the left column is the zoom ratio label ("1x".."12x"), the right column is the
corresponding 16-bit hex Zoom Position value. This is a documentation quirk in the
source page, not a transcription error here; both header cells read "Optical Zoom
Ratio" in the raw HTML `<th>` markup.)

### "20x Zoom" table (applies to IV-CAM-I20 and IV-CAM-P20 — see §3)

| Optical Zoom Ratio | Optical Zoom Ratio (hex Zoom Position) |
|---|---|
| 1x | 0000 |
| 2x | 1851 |
| 3x | 22BE |
| 4x | 28F6 |
| 5x | 2D45 |
| 6x | 3086 |
| 7x | 3320 |
| 8x | 3549 |
| 9x | 371E |
| 10x | 38B3 |
| 11x | 3A12 |
| 12x | 3B42 |
| 13x | 3C47 |
| 14x | 3D25 |
| 15x | 3DDF |
| 16x | 3E7B |
| 17x | 3EFB |
| 18x | 3F64 |
| 19x | 3FBA |
| 20x | 4000 |

**Reading this table:**
- Zoom Position is a 16-bit value ranging `0x0000` (widest, 1x) to `0x4000` (full
  telephoto, 12x or 20x depending on model family). `0x4000` = 16384 decimal.
- The mapping from integer zoom ratio (1x, 2x, 3x, …) to Zoom Position is **not linear**
  in the position value — e.g. for the 12x table, 1x→2x is a jump of `0x1982` (6530)
  but 11x→12x is a jump of only `0x0145` (325). The position values compress as ratio
  increases (classic lens-zoom-motor characteristic: equal position steps do not
  produce equal magnification steps; magnification is compressive near the tele end).
  A `ZoomLevelToPosition` implementation must interpolate/ use a lookup+interpolation
  across this specific table, not a linear `position = (level/max_level) * 0x4000`
  formula, if it is to reproduce Crestron's own mapping exactly. (The docs do not
  give a closed-form formula — only this discrete table. See §5.)
- The table is presented for **whole integer zoom ratios only** (1x, 2x, 3x, … up to
  12x or 20x). There is no fractional-zoom-ratio row and no stated interpolation rule
  between the listed points.

## 3. Which camera uses which table

Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I12Specs.htm — "Optical Zoom: 12x"
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P12Specs.htm — "Optical Zoom: 12x"
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm — "Optical Zoom: 20x"
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P20Specs.htm — "Optical Zoom: 20x"

| Model | Optical Zoom | Zoom table to use |
|---|---|---|
| IV-CAM-I12 | 12x | "12x Zoom" table |
| IV-CAM-P12 | 12x | "12x Zoom" table |
| IV-CAM-I20 | 20x | "20x Zoom" table |
| IV-CAM-P20 | 20x | "20x Zoom" table |

This confirms the I20 and P20 drivers should both need the **same** 20x table, and
I12/P12 the same 12x table — the VISCA-Commands page is model-family-agnostic and
just labels the two tables by max optical ratio, which lines up exactly with the
"Optical Zoom" spec field per model.

## 4. Focal length, field of view, and optical boundary — no digital zoom is documented

Source: I12Specs.htm / I20Specs.htm / P12Specs.htm / P20Specs.htm (specification tables,
"Optics" section)

| Model | Focal Length | Field of View (PTZ) | Field of View (Reference camera, I-series only) | Iris | Optical Zoom |
|---|---|---|---|---|---|
| IV-CAM-I12 | F=4.1–49.2 mm | Horizontal: 67.68° | Horizontal: 104° (changes based on camera mode) | F1.8-F2.68 | 12x |
| IV-CAM-P12 | F=4.1–49.2 mm | Horizontal: 67.68° | n/a (single camera) | F1.8-F2.68 | 12x |
| IV-CAM-I20 | F=5.2–94 mm | Horizontal: 56.45° | Horizontal: 104° (changes based on camera mode) | F1.5-F3.0 | 20x |
| IV-CAM-P20 | F=5.2–94 mm | Horizontal: 56.45° | n/a (single camera) | F1.5-F3.0 | 20x |

Quoted verbatim (I20Specs.htm):
> "Optical Zoom | 20x
> Focal Length | F=5.2–94 mm
> Field of View (PTZ) | Horizontal: 56.45°
> Field of View (Reference) | Horizontal: 104° (changes based on camera mode)"

**No digital zoom is mentioned anywhere in the harvested set.** Every "Optical Zoom"
spec field states only the optical ratio (12x or 20x); there is no "Total Zoom",
"Digital Zoom", or combined optical+digital ratio field in any of the four Specs
pages, and no other page in the 71-page set mentions digital zoom. The 16-bit Zoom
Position range (`0x0000`–`0x4000`) documented in §2 therefore appears to span the
optical range only, end to end — i.e. `0x4000` is the full optical telephoto position
(12x or 20x, matching the spec sheet's stated max optical ratio exactly), not an
optical+digital combined range. There is no documented "optical/digital boundary"
because the docs don't describe any digital zoom stage to have a boundary with.

## 5. What is NOT documented (gaps relevant to `ZoomLevelToPosition`)

- **No formula.** The docs give only the two discrete tables in §2 (12 rows for 12x,
  20 rows for 20x). There is no stated interpolation method, no polynomial/logarithmic
  formula, and no explanation of the position-value spacing pattern. Any reconstruction
  of `ZoomLevelToPosition` for non-integer zoom levels, or for intermediate `p,q,r,s`
  values not in the table, is necessarily an extrapolation beyond what Crestron
  publishes.
- **No worked example** showing a full VISCA byte sequence being sent for a specific
  zoom ratio (e.g., no "to zoom to 5x, send `8x 01 04 47 03 00 09 09 FF`" walkthrough).
  The bytes must be derived by the reader by splitting the hex Zoom Position from the
  table into four nibbles and placing each in its own `0X` byte — this splitting/packing
  behavior is demonstrated only implicitly by the command syntax (`0p 0q 0r 0s`), never
  spelled out with an example.
- **No step behavior/speed-to-position relationship** beyond the `Tele(Variable)` /
  `Wide(Variable)` commands' `p: 0(Low) to 7(High)` speed parameter and the
  `Absolute Position` command's `t:speed 0-7` field — i.e., speed (0-7) is documented,
  but not how many position units a given speed produces per unit time, nor any
  ramping/step-size behavior.
- **No mention of `ZoomLevelToPosition`, `ZoomPositionToLevel`, or `ApplyZoomPositionStep`**
  by name anywhere in the 71-page set (expected — these are Crestron driver-internal
  transformation names, not public VISCA/product documentation concepts). Their exact
  internal formula cannot be confirmed or refuted from this documentation; only the
  raw lookup table they'd need to reproduce is confirmed.
- **No zoom-ratio-to-distance/subject-size table.** Group Framing / Presenter Tracking
  pages describe "Recommended Range" (e.g., I20: 15–50 ft, from I20Specs.htm) but do not
  tie specific ranges to specific zoom ratios or Zoom Position values — tracking zoom is
  described only qualitatively (see `Group-Framing-Settings.htm`: "Zoom Limit — Use the
  slider to determine the maximum amount of zoom applied when the tracked subject moves
  further into the background" — a UI slider, not a numeric spec).

## 6. Bottom-line verdict on ZoomLevelToPosition reconstruction

**ZOOM.md contains the actual numbers needed to pin down the core lookup table** —
this was the single highest-value find of the harvest: a verbatim, camera-family-keyed
16-bit Zoom-Position-per-integer-zoom-ratio table for both the 12x (I12/P12) and 20x
(I20/P20) families, straight from Crestron's own VISCA command reference.

What it does **not** give is the interpolation/rounding rule the driver's compiled
`ZoomLevelToPosition` transform actually uses between/around these 12 or 20 discrete
points (e.g., for a UI zoom slider expressed as a continuous 0.0–1.0 or 0–100 level
rather than an integer "Nx" ratio). If the real transform only ever needs to hit these
exact integer-ratio points (e.g., preset zoom levels), this table is sufficient. If it
needs to support continuous/fractional zoom levels, the interpolation method must be
either reverse-engineered from the IL (out of scope for this experiment) or inferred/
approximated (e.g., piecewise-linear across these points) — the public documentation
does not resolve that ambiguity.
