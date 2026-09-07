# Finding 07 — the 1 Beyond drivers, and what a SIMPL macro really is

Phase 1 of the unattended session. **40 confirmed, 4 overstated, 2 refuted.**
(`oneb-p20-dll` returned a placeholder stub and is being re-run.)

## The 1 Beyond camera driver is NOT a JSON shell — but the gap is *named*

This is the answer to the biggest open question, and it is neither the good case
nor the bad case.

`Camera_Crestron-1-Beyond_IV-CAM-I20_IP.dll` is a full **Crestron SDK V2 (Entity
Model)** assembly: **36 TypeDefs, 84 MethodDefs, 79 Fields**, 133 MemberRefs,
referencing `Crestron.DeviceDrivers.EntityModel` and `Crestron.DeviceDrivers.SDK`
**v26.0.26.0** — not `LegacyWrappers`. Samsung's was 2 TypeDefs and *one*
MethodDef.

Its type `.DriverEntity` extends `ReflectedAttributeDriverEntity` and `.EntryPoint`
extends `DriverAssemblyEntryPoint`; the metadata carries `[EntityCommand]`,
`[EntityProperty]`, `[EntityDataType]` and `[ImplementationProvider]` attributes.
So Crestron ships **at least three driver forms in production**: the LegacyWrappers
JSON engine (Samsung), V2 Entity Model (1 Beyond), and V1 RAD.

The embedded JSON is large and still does most of the work — **116,874 bytes,
`SchemaVersion 2.0`**, with 82 Commands, 31 Responses, 54 Conditions, 26
Transformations, 70 Rules, 73 Controllers.

**But six Transformations that the JSON's own Rules invoke have no declarative
definition:**

```
FormatRomVersion        ParseDecimal            ViscaAssemble2LowerNibbles
ZoomLevelToPosition     ZoomPositionToLevel     ApplyZoomPositionStep
```

Their behaviour exists only as ~5.9 KB of compiled IL in matching Factory classes
registered via `[ImplementationProviderAttribute]` — binary protocol assembly
(these cameras speak **VISCA**), table interpolation, and an async scene/camera-view
state machine with timeouts.

### Why this is the best available form of bad news

The JSON **names** what it cannot express. A converter does not have to guess
whether it got everything — it can enumerate every `Transformation` referenced by
`Rules`, subtract those defined in the `Transformations` array, and report the
difference exactly.

> **Design rule:** the extractor must resolve referenced-vs-defined transformations
> and fail loudly with the list of IL-only names. Partial extraction that looks
> complete is the failure mode to design against.

So "Crestron in" is: **fully recoverable for LegacyWrappers drivers; recoverable
with a precisely-known residue for V2 drivers.** Both are far better than
"decompile everything".

## A `.cmc` is an I/O contract with a dangling pointer

Finding 04 ruled the SIMPL family out as "program logic, not a driver". That
ruling is **correct, and it understated the case.**

The Automate VX macro is a Crestron Macro container holding: one Symbol interface
(263 inputs, 263 outputs, 1 parameter), 308 named signal declarations, and a
wiring graph over just **three** placed sub-symbols — an argument pass-through, a
stock Debounce block for 10 joystick inputs, and a **bare-name reference to an
external SIMPL+ module, `1Beyond Automate_VX_v1.2.csp`, which is not embedded and
was not shipped with the sample.**

**Zero literal serial/TCP command strings, hex escapes, or quoted payloads appear
anywhere in the 59,033 bytes.** The only quoted text is a `HTTP`/`HTTPS` dropdown
label.

This matches Crestron's documented distribution model: the `.cmc`/`.umc` is the
wiring and interface shell; the protocol logic lives in a companion `.usp`/`.csp`
shipped alongside. **It is not merely unreachable logic — it is an I/O contract
plus a pointer to logic that is absent.**

## Automate VX: convergence confirmed on one axis, blocked on the other

Not the Samsung result, and the distinction matters.

- **Extron vs Extron: converges heavily.** The ControlScript module and the
  `.pkp`-embedded script share **32 identical endpoint strings, verbatim**. But
  these are two Extron in-house rewrites of the same Extron-authored driver
  against the same documented API — so this is consistency, not independent
  corroboration.
- **Extron vs Crestron: untestable, not refuted.** The `.cmc` contains none of
  those wire strings because it contains no wire strings at all. The artifact
  needed for the comparison — the `.csp` — is missing.

What *is* confirmed is **semantic parity at the command level**: every Extron
capability (AutoSwitch, CameraPresetRecall, PanTilt/Zoom, Layout A–Z,
RoomConfiguration, Scenario, Sleep/Wake, ISORecording, Record, Stream,
SwitchCamera, HomeShotPreset/GoHome, credentials, IP/Port, HTTP-vs-HTTPS) has a
same-named join in the macro — **except `CameraPresetSave`, which has no join at
all.**

So the Samsung claim stands unweakened but also ungeneralised: it holds where two
vendors independently encode a wire protocol, and this sample could not test that.

## `tools/pkg_dump.py` — built and verified

The Crestron counterpart to `pkp_dump.py`. Verified independently, not taken on
the agent's word:

```
$ python3 tools/test_pkg_dump.py
23 passed, 0 failed, 23 total
```

No hardcoded offsets. It walks DOS/COFF/optional headers to the data directory,
reads the CLI header via directory entry 14, resolves Metadata and Resources RVAs
through the section table, parses the `BSJB` root, and implements a real ECMA-335
`#~` tables-stream reader — column and coded-index definitions for all 45 standard
tables — to walk `ManifestResource` and read the 4-byte length-prefixed payload.
A brace-matched `"SchemaVersion"` scan exists as a fallback and records itself in
`notes`; **it was never needed on real samples.** If both paths fail it raises
rather than returning partial data.

All five packages extract via `method=cli-metadata`:

| package | members | resource | sections |
|---|---|---|---|
| 1 Beyond IV-CAM-I20 IP | 2 | 116,874 | 11 |
| 1 Beyond IV-CAM-P20 IP | 2 | 109,648 | 11 |
| Samsung Serial | 2 | 46,164 | 13 |
| Samsung IP | 2 | 80,889 | 14 |
| Samsung IR | 3 | no DLL | — |

**The two schemas differ.** 1 Beyond (SchemaVersion 2.0) has `ConfigurationSteps`
and `DriverController`; Samsung has `UserAttributes`, `SupportedFeatures`,
`CommandIds` and `InputOutput`. Same rule-engine shape, different section sets —
the cross-vendor mapping must handle both.
