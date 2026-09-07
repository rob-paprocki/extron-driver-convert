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

**Corrected measurement** — every one of the 32 endpoints Extron actually calls,
probed directly:

| | count |
|---|---|
| documented | **27** |
| not documented | **5** |

Not documented: `StopAutoSwitch`, `StartISORecord`, `StopISORecord`,
`ISORecordStatus`, and `ChangeRoomConfiguration` (which appears only inside a
cURL example on the Macro page).

**What this changes.**
- The "five endpoints with no trace at all" list was wrong: `Wake` and
  `StartAutoSwitch` are documented.
- The "five sub-APIs visible only inside `GetAllStatus`'s example body" claim was
  wrong for four of the five — `AutoSwitchStatus`, `OutputStatus`, `RecordStatus`
  and `RoomConfigStatus` all have first-class pages. Only `ISORecordStatus` does not.
- Doc-driven generation therefore looks **better** than reported below, not worse.

**What survives.** A real delta remains — 5 of 32 — and the pattern it illustrates
is intact, because it never rested on this case. Samsung's shared undocumented
firmware-bug workaround and the 1 Beyond cameras' undocumented `c2` command family
were both established from driver bytes, not from failing to find a doc page.

There is even a better instance of the exact asymmetry the original argument
wanted: **`StartAutoSwitch` is documented and `StopAutoSwitch` is not.** The
argument was sound; the evidence chosen for it was not.

**Methodological lesson, which is the durable part:** this project's standing rule
is that a claim needs positive evidence. "I searched and found nothing" is not
positive evidence about a document's contents — it is a statement about a search.
Enumerating a doc site by keyword search is unsound; enumerate by URL pattern, or
by an index the site itself publishes, and verify a negative before building on it.

---

# Finding 08 — could you generate a driver from the vendor's API docs?

**No. Documentation is necessary but not sufficient — and we can now say by exactly
how much.**

The Automate VX API is publicly documented, and we hold three implementations that
demonstrably work against the real device. That makes this the only case in the
project where implementations can be measured against ground truth rather than
against each other. 40 pages harvested to `reference/automate-vx-api/`, 32
endpoints tabulated in `ENDPOINTS.md`.

**24 confirmed, 6 overstated, 5 refuted** — the refutations are folded in below.

## Extron implements 22 of the 32 documented endpoints (69%)

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

**`Sleep` is documented. `Wake` is not.** A driver generated from the docs could
put the device to sleep and never wake it up. That single pair is the whole
finding in miniature.

## And the types are wrong

Several parameters the spec types as JSON integers are sent by the working driver
as JSON **strings** — `GoToScenario.id`, `StartPT.ptDir`, `StartZ.zDir`. Extron's
driver interoperates with the real device, so where they disagree, the driver is
right and the document is wrong.

## What this means for the project

A doc-driven generator would produce something that looks complete and is not: it
would get the auth flow right, get ~69% of the surface right, silently omit five
endpoints a real driver needs, never discover five more hidden in an example, and
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
