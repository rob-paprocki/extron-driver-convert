# Finding 18 — the asset tree is the command surface, and it can be extended

**Status: measured** 2026-09-09. Two halves: a hardware observation that
settles finding 15's open question, and a tool that acts on it.

## 1. What Global Configurator actually showed

`1bynd_19_20022` and `20023` — the two packages that returned `80085` before
the digest fix in finding 16 — now **load and can be selected** in GCP. The
hash fix is confirmed on hardware, not merely against a reimplementation.

And the driver renders **15 commands**:

> Auto Exposure, Auto Focus, Backlight, Connection Status, Focus, Gain, Iris,
> Pan Tilt, Power, Preset, Shutter, User Defined Command, User Defined String,
> White Balance, Zoom

The embedded script declares **31**. The 16 missing ones — auto-tracking, the
light bar, intelligent switching, absolute position — were in the file the
whole time, as code nothing could reach.

That is finding 15's structural claim, measured. Finding 16 corrected the
*cause of the error code* (integrity, not declaration) and left this claim
standing; it was hypothesis until the screenshot. **GC builds its command
surface from `DriverCommandAsset` objects in the NRBF graph and never asks the
script what it can do.**

Three gates, and now all three are characterised:

| gate | decided by | fails as |
|---|---|---|
| discovery | filename | not listed |
| catalogue parse | package structure | not listed |
| selection | SHA-256 of packaged resources | `80085` |
| **command surface** | **the asset tree** | **silently short** |

The fourth is the dangerous one, because nothing reports it. The package is
valid, loads, and is simply less than it claims.

## 2. `_scriptName` is the seam

A `DriverCommandAsset` carries both halves of the contract:

```
AssetBase+_name                 'Backlight'      <- what GC displays
CommandAssetBase+_scriptName    'Backlight'      <- the self.Commands key
CommandAssetBase+_attributes    DriverAttributeEnum bitfield
_internalChildCollection        the parameter assets
```

So a command GC will render *and* the script will answer must exist in both
places, under names that agree. Nothing enforces that agreement — which is
exactly how a package with 15 assets and 31 script commands came to validate.

Observed attribute bitfields, from the donor's own commands:

| value | commands | GCP badges |
|---|---|---|
| 3 | Zoom, Focus, Iris, Gain, Shutter, Preset, Pan Tilt, User Defined Command | A |
| 19 | User Defined String | A C |
| 35 | Connection Status | C |
| 51 | Backlight, White Balance, Auto Exposure, Auto Focus | A C |
| 59 | Power | A C |

## 3. The walker: what was missing to add an object

`pkp_build.py` could change what a package already contained and not add to
it, because nothing knew where one object's records ended and the next began.
`tools/nrbf_graph.py` supplies that by replaying the trace with the reader's
own record grammar, giving every object id the exact span of events that
encodes it.

It is checked rather than trusted: consuming from index 0 must land exactly on
the end of the trace with every event attributed once. Across the nine sample
packages:

| package | events | objects |
|---|---|---|
| `1bynd_19_4743` | 264,239 | 1,426 |
| `1bynd_19_4741` | 280,050 | 8,021 |
| `1bynd_42_4279` | 547,611 | 43,030 |
| `clau_25_1777` | 461,541 | 1,931 |
| `clau_25_5940` | 203,401 | 2,276 |
| `extr_17_17677` | 450,061 | 8,840 |
| `extr_15_17578` | 474,851 | 9,114 |
| `smsg_10_6738` | 434,743 | 10,098 |
| `biam_25_150` | **4,464,075** | **667,970** |

Nine of nine, no drift. A grammar that were wrong would not survive 4.4 million
events.

## 4. Ownership, and the bug it prevents

A command is not a self-contained span: its parameters are defined elsewhere in
the stream, and some of what it points at is shared with all the others. So a
clone has to decide, per object, copy or share.

The rule is computed, not assumed: an object reachable from the command is
**owned** if nothing outside the subtree references it, to a fixpoint. A
Backlight command owns 58 objects and shares 5.

The shared ones are why this matters. All 15 commands point at **one** empty
string for their description. The first implementation renamed the string it
found — which would have given every command in the package the same
description. The guard caught it on the first run:

```
AssetError: CommandAssetBase+_description (string 38) is shared with other
commands; cloning it would rename them.
```

Shared strings are now repointed at a fresh object instead of rewritten, and
`test_pkp_asset.py [9]` asserts no existing description changes.

A second rule was needed, and it is the subtler one: **an object defined
*inside* a copied span must get a new id even when ownership calls it shared**,
because its original record still stands where it was. Reusing the id would put
two definitions of one object in a single stream.

## 5. Composition, because cloning alone hits a wall

Cloning whole commands can only reproduce shapes the donor already has. The
i20's `ZoomPosition` needs a decimal value beside a decimal speed qualifier;
the donor pairs a decimal speed with an **enum** value, and pairs a decimal
value with an **enum** action. Neither is the shape wanted.

So parameters are cloned and grafted individually — clone Zoom, detach its enum
value, attach a decimal cloned from Preset. Every class layout the pieces need
is already defined in the stream, so the result is still made only of Extron's
own parts.

Two array details cost real time and are worth recording:

- **.NET over-allocates.** The command arrays are capacity 16 holding 15, so
  the first added command fills a free slot and the second must grow the array.
  Both paths are exercised by `test_pkp_asset.py [6]`.
- **`ObjectNullMultiple` compresses empty slots**, so an array's event count is
  not its capacity. Editing by slot index needs the run expanded first. The
  first implementation asserted count == capacity and failed loudly on the
  parameter collections, which is how it was found.

## 6. The result

`experiments/skeleton_i20/build_i20_assets.py` produces
**`1bynd_19_20024`** — 32 commands in the graph, matching the script's 31 plus
`ConnectionStatus`.

Measured on the output:

- **all 17 i20 commands present**, script names matching `self.Commands` exactly
- **all 15 originals unchanged** — name, parameters and enum states compared
  one by one
- **`Valid`** from `pkp_validate.py`
- model version bumped to 1.2 so Driver Manager can distinguish it from 20023

`ConnectionStatus` is an asset with no `_cmd_` method. That is **Extron's own
arrangement** — the donor ships it that way, handled by the ControlScript
framework rather than the driver — and was reproduced rather than corrected.

## What this does NOT show

- **GC has not rendered these commands.** Everything above is measured on the
  file. Validation covers only the packaged resources (finding 16), so a
  structurally wrong graph still returns `Valid` — the check that matters is
  GC's UI, and that is a hardware gate. **This is the same trap as the wire
  table: necessary, not sufficient.**
- **Nothing has driven a camera.** No i20 has been reachable from this project
  at any point.
- **The parameter widgets are unverified.** Ranges, intervals and enum orders
  were set from the script's docstrings, not from anything GC has confirmed.
- **`PanTiltAngle`'s value shape is a guess.** The script documents
  `{'Pan': Decimal, 'Tilt': Decimal}`; it is modelled as two decimal
  parameters, which is the natural reading but not a measured one.
- **Attribute bitfields were copied, not decoded.** 3 / 51 / 35 were taken
  from donor commands of similar character. The individual bits are not known.
- **One package family.** Every clone here is within a single 1 Beyond camera
  package. Cross-package cloning, where class metadata would have to be
  imported too, is untried.
