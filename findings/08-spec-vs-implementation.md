# CORRECTION (2026-09-07) — READ THIS FIRST

**The headline claim below was wrong.** `Wake` **is** documented, at
`.../API-Reference/Wake-API.htm`. So are `AutoSwitchStatus`, `StartAutoSwitch`,
`OutputStatus`, `RecordStatus`, `RoomConfigStatus`, `GetLayouts`, `LayoutStatus`
and `GetRoomConfigs` — nine pages the harvest never found.

**Root cause.** The harvest enumerated pages by keyword search and declared
"convergence" when a second sweep of 68 terms surfaced nothing new. That is an
absence of evidence treated as evidence of absence. The URL pattern is plainly
`<EndpointName>-API.htm`; probing it directly finds the pages immediately. It was
never tried. The unverified conclusion was then repeated in a finding, a commit
message and three replies before the repo owner caught it.

**Corrected measurement (second pass).** The first correction was *also* short,
because it assumed a uniform `<Name>-API.htm` filename. Two more pages exist under
different conventions, both found by the repo owner:

- `StopAutoSwitch.htm` — **no `-API` suffix**
- `ChangeRoomConfig-API.htm` — **filename shortened**, documents the
  `ChangeRoomConfiguration` endpoint

Final tally across all 32 endpoints Extron actually calls:

| | count |
|---|---|
| documented with a dedicated page | **29** |
| no dedicated page | **3** |

The three are `StartISORecord`, `StopISORecord` and `ISORecordStatus` — the entire
ISO-record family, and nothing else. Probed under 11 name variants against both
URL patterns: no page exists. `ISORecordStatus` does appear in `GetAllStatus`'s
example body (`api_call_3`, with a real response shape), so it is documented by
example but not by page.

**That pattern reads as deprecation, not omission** — the owner's read, and the
evidence supports it. Crestron demonstrably *does* remove retired calls and record
it ("Removed support for depreciated CallPlugin API call"), so a whole feature
family with no pages is more likely retired than overlooked. Extron's driver, whose
own revision history spans 2019–2026, still implements it.

**What this changes.**
- The "five endpoints with no trace at all" list was wrong: `Wake`,
  `StartAutoSwitch`, `StopAutoSwitch` and `ChangeRoomConfiguration` are all
  documented.
- The "five sub-APIs visible only inside `GetAllStatus`'s example body" claim was
  wrong for four of the five — `AutoSwitchStatus`, `OutputStatus`, `RecordStatus`
  and `RoomConfigStatus` all have first-class pages. Only `ISORecordStatus` does not.
- Doc-driven generation therefore looks **better** than reported below, not worse.

**What survives.** A much smaller delta — 3 of 32, all ISO-record, plausibly
deprecated — and the pattern it illustrates
is intact, because it never rested on this case. Samsung's shared undocumented
firmware-bug workaround and the 1 Beyond cameras' undocumented `c2` command family
were both established from driver bytes, not from failing to find a doc page.

The replacement example I reached for — "`StartAutoSwitch` documented,
`StopAutoSwitch` not" — **was also wrong**, for the same reason: I inferred a
filename convention from a sample and treated it as exhaustive. Two corrections,
two variants of the same mistake.

**Methodological lesson, which is the durable part:** a claim needs positive
evidence, and *"I searched and found nothing" is a statement about a search, not
about a document.*

This was got wrong twice in a row, each time by a different flavour of the same
error:
1. keyword-search enumeration, with "two sweeps found nothing new" mistaken for
   convergence;
2. URL-pattern enumeration, with a convention inferred from a sample and assumed
   exhaustive.

The reliable method is an index the site itself publishes, or exhaustive
verification of each negative before it becomes an argument. Where neither is
available, a negative should be reported as *"not found by method X"*, never as
*"does not exist"*. Every claim in this repo that rests on an absence should be
read with that caveat.

---

# Finding 08 — could you generate a driver from the vendor's API docs?

**Mostly not — documentation is necessary but not sufficient, and we can now
say by exactly how much.** *(First written as a flat "No." The header's
correction narrows it: 29 of the 32 endpoints Extron's driver actually calls
turn out to have their own documentation page, not the ~69% first counted —
see "Extron implements 22 of the 32 documented endpoints" below. What
survives is 3 genuinely undocumented endpoints, the whole ISO-record family,
plus the wrong parameter types.)*

The Automate VX API is publicly documented, and we hold three implementations that
demonstrably work against the real device. That makes this the only case in the
project where implementations can be measured against ground truth rather than
against each other. 40 pages harvested to `reference/automate-vx-api/`, 32
endpoints tabulated in `ENDPOINTS.md`.

**24 confirmed, 6 overstated, 5 refuted** — the refutations are folded in below.

## Extron implements 22 of the 32 documented endpoints (69%)

*(This counts against the endpoint list as first tabulated, which the
Wake/StartAutoSwitch/StopAutoSwitch harvest gap did not touch — none of those
three were in this "documented" list either way, so the 10-ignored /
2-genuine-gap breakdown below is unaffected. The number that the header's
correction actually moves is the different question below: of the 32
endpoints Extron's driver calls, how many are documented — corrected from
~69% to 29/32, 91%.)*

The 10 it ignores are mostly defensible: `CopyFiles`, `GetCameras`, `GetScenarios`,
`ImportCameraPresets`, `RecordingSpaceAvail`, `Restart` are installer-time or
maintenance actions a room-control driver has no business calling; `GetAllStatus`
and `Macro` are batch wrappers redundant with the per-feature calls Extron already
makes individually.

Two are genuine capability gaps: **`GetActiveTalkers`** and **`ShotStatus`**.
Extron's driver cannot report which microphone is actively talking, nor the
combined shot/current-layout/previous-layout state the device exposes.

## But Extron calls 11 things the endpoint table does not list

This is the part that answers the question.

**Five are sub-APIs that appear only inside `GetAllStatus`'s example response
body** — `AutoSwitchStatus`, `OutputStatus`, `ISORecordStatus`, `RecordStatus`,
`RoomConfigStatus`. They are real and Extron calls them as first-class commands.
A generator reading the endpoint documentation would never promote a name out of
an example JSON blob into a pollable command.

**Five more have no trace in the documentation at all:**

```
StartAutoSwitch   StopAutoSwitch   StartISORecord   StopISORecord   Wake
```

*(A sixth candidate, `ChangeRoomConfiguration`, was initially reported as
undocumented; a verifier found it does appear once, in a cURL example on the
Macro API page. Corrected.)*

*(Corrected by the header, second pass: `StartAutoSwitch`, `StopAutoSwitch`
and `Wake` are all documented too — found by probing `<Name>-API.htm` and,
for `StopAutoSwitch`, the no-`-API`-suffix variant. Only `StartISORecord` and
`StopISORecord` survive as genuinely undocumented, the ISO-record family.)*

**`Sleep` is documented. `Wake` is not.** *(Corrected: `Wake` **is**
documented, at `.../API-Reference/Wake-API.htm` — first written as
undocumented from a harvest that hadn't tried that URL directly. See the
header.)* A driver generated from the docs could put the device to sleep and
never wake it up — first thought to be the whole finding in miniature; the
surviving miniature is the ISO-record family, undocumented for a plausible
reason (deprecation) rather than a missed harvest.

## And the types are wrong

Several parameters the spec types as JSON integers are sent by the working driver
as JSON **strings** — `GoToScenario.id`, `StartPT.ptDir`, `StartZ.zDir`. Extron's
driver interoperates with the real device, so where they disagree, the driver is
right and the document is wrong.

## What this means for the project

A doc-driven generator would produce something that looks complete and is not: it
would get the auth flow right, get ~69% of the surface right (first count;
corrected below to 29 of 32 endpoints actually documented, 91%), silently omit
two endpoints a real driver needs (`StartISORecord`, `StopISORecord` — first
counted as five, before the header's correction found `Wake`,
`StartAutoSwitch` and `StopAutoSwitch` documented after all), never discover
one more hidden in an example (`ISORecordStatus` — first counted as five,
before `AutoSwitchStatus`, `OutputStatus`, `RecordStatus` and
`RoomConfigStatus` turned out to have first-class pages of their own), and
emit three parameters with wrong JSON types.

**This is the same lesson the Samsung case taught, from the opposite direction.**
There, two vendors independently encoded the same *undocumented firmware bug*
(`0D 00 00 02` for power-on). Here, one vendor's driver encodes five endpoints the
manufacturer never wrote down. Both say the same thing:

> **A shipped driver records what the device actually does. Documentation records
> what someone intended it to do. The delta is exactly the value a driver carries.**

So the project's centre of gravity should stay on **converting real drivers**, with
documentation as a *cross-check and enrichment source* — good for parameter ranges,
descriptions, and spotting unimplemented capability — never as the primary input.

## The IL-only residue is bounded and reusable — the good answer

Finding 07 left open whether the compiled-code residue in Crestron V2 drivers is a
small fixed set or unbounded per-device code. **It is bounded.**

`IV-CAM-P20` is the same engine as `I20`: 33 TypeDefs / 76 MethodDefs (vs 36 / 84),
same `ReflectedAttributeDriverEntity` base, same `Crestron.DeviceDrivers.EntityModel`
and `.SDK` at **26.0.26.0**, same 11-section SchemaVersion 2.0 JSON, same
self-signed-not-strong-named signing.

Its Rules reference **39 distinct Transformation names; 27 are declared** in the
JSON. Of the 12 undeclared, only **5 have driver-local IL** — `FormatRomVersion`,
`ParseDecimal`, `ZoomLevelToPosition`, `ZoomPositionToLevel`, `ApplyZoomPositionStep`
— plus `OverridePolynomial`, an override hook never called by literal name. The
remaining undeclared names are supplied by the SDK framework itself.

I20 has that **same six-type family plus exactly one extra**:
`ViscaAssemble2LowerNibbles`. P20 instead calls a 4-nibble variant and a separate
nibble-extraction helper.

> **So the residue is a small, reusable, per-vendor set — not per-device custom
> code.** A converter can implement these transformations once, name them, and
> handle the long tail by failing loudly with an exact list. That makes the V2
> Entity Model form substantially more tractable than "some behaviour is compiled"
> first suggested.

## Correction to finding 07

Finding 07 described the `.cmc`'s 308 named-signal blocks as internal wiring
distinct from the join surface. **Refuted.** 286 of the 308 (92.9%) are
byte-for-byte identical to real join names — zero join names are missing from the
signal set. The signal declarations *are* the join surface. The rest of finding
07's `.cmc` conclusion (no wire strings, logic delegated to an unshipped `.csp`)
stands.
