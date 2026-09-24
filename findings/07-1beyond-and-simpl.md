# Finding 07 — the 1 Beyond drivers, and what a SIMPL macro really is

**Carries a correction, 2026-09-23** — see "Correction, 2026-09-23" below the
`.cmc`/dangling-pointer section: with real `.usp` source in hand for two
vendors, the `.usp` turns out to be a second dispatcher, not where the
protocol lives, and the "untestable" verdict on Extron-vs-Crestron wire
convergence is now tested. Read the correction alongside the original text,
not instead of it.

Phase 1 of the unattended session. **40 confirmed, 4 overstated, 2 refuted.**
(`oneb-p20-dll` returned a placeholder stub and is being re-run.) *(Re-run
completed — see finding 08 "The IL-only residue is bounded and reusable":
IV-CAM-P20 is the same engine as I20, sharing the same driver-local IL family
(`FormatRomVersion`, `ParseDecimal`, `ZoomLevelToPosition`,
`ZoomPositionToLevel`, `ApplyZoomPositionStep`, `OverridePolynomial`); where
I20 adds `ViscaAssemble2LowerNibbles`, P20 instead calls a 4-nibble variant
and a separate nibble-extraction helper.)*

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

*(Recounted 2026-09-23 with a whole-document scan — Commands, Responses and
Rules, the method that reproduces finding 08's P20 figures exactly
(`crestron2cs.py --list-il-only`, ROADMAP R31): the I20 references **39**
Transformation names, declares **26**, leaves **13** undeclared. The six above
are all among them; the other seven are the SDK's generic `Identity`, `Sum`,
`Subtract`, `Product` and `Divide`, and the nibble helpers
`ViscaAssemble4LowerNibbles` and `ViscaExtractNibbles`, which the I20's
Responses name as well. So the six are the driver-local family, not the whole
undeclared set.)*

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

### Correction, 2026-09-23 — the `.usp` is a dispatcher, not the logic

Source: `tools/out/verdicts/heldout_synthesis.md` §4 ("The SIMPL answer —
correcting finding 07"), written once real `.usp` source was in hand for two
vendors (Clock Audio, Biamp).

**The first half of the claim above is confirmed and now generalises; the
second half is wrong.** The companion module is *not* where the protocol
lives. Every `.usp` in both suites is itself a second dispatcher:
`Clock Audio Device v3.4.1.usp:80` declares
`#USER_SIMPLSHARP_LIBRARY "Clock Audio"` and calls `device.SetLedState(...)`;
`Biamp Tesira Comm v3.3.usp:52` declares
`#USER_SIMPLSHARP_LIBRARY "BiampTesiraLib3"` and calls `tesira.Connect()`.
Neither contains a single literal wire token. The real chain is
`.umc → .usp → compiled SimplSharp .NET assembly`, so this finding's
structural claim should read: *a Crestron module is an I/O contract plus a
pointer to logic in a compiled assembly, and the `.usp` is part of the
contract, not the logic.*

**The "untestable, not refuted" verdict below is now testable, and it was
tested. Wire strings are fully recoverable** from the assembly's ECMA-335
`#US` heap — `BiampTesiraLib3.clz` is a ZIP containing `BiampTesiraLib3.dll`;
`Clock Audio.dll` sits uncompressed under `SPlsWork/`. Finding 05's
two-vendor convergence result reproduces, but not uniformly:

- **Clock Audio: yes, strongly.** 19 of the 20 command tokens Extron's 1777
  driver uses appear in Clock Audio's own SimplSharp library (the one miss is
  `ON`, a value, not a verb). Response formats are structurally identical
  modulo named-vs-anonymous capture groups.
- **Biamp: partially — convergence at the grammar level, not byte level.**
  Both sides speak the same Tesira Text Protocol grammar (`DEVICE get
  version\n`, `SESSION set verbose true`, `(set|get|subscribe)`), but two
  systematic divergences hold throughout: Biamp's library always quotes the
  instance tag where Extron never does, and Biamp terminates with bare `\n`
  where Extron mostly uses `\r\n`. *(Measured 2026-09-23, and narrower than
  the synthesis says: on the **send** side Extron's shipped Tesira module ends
  all 73 of its command templates in bare `\n` and none in `\r\n`; its 44
  `\r\n` literals are reply patterns. So both vendors send `\n`, and the one
  exception, `DeviceFaultList` in the `.pkp`, is an artifact — finding 11,
  `experiments/tesira_terminator/RESULT.md`.)*

So cross-vendor corroboration is strong enough to *adjudicate* a disputed
string (see finding 11), and not strong enough to *generate* one — Samsung's
verbatim-string convergence is not the general case; Clock Audio reproduces it
at the token/format level, Biamp only at the grammar level.

## Automate VX: convergence confirmed on one axis, blocked on the other

Not the Samsung result, and the distinction matters.

- **Extron vs Extron: converges heavily.** The ControlScript module and the
  `.pkp`-embedded script share **32 identical endpoint strings, verbatim**. But
  these are two Extron in-house rewrites of the same Extron-authored driver
  against the same documented API — so this is consistency, not independent
  corroboration.
- **Extron vs Crestron: untestable, not refuted.** The `.cmc` contains none of
  those wire strings because it contains no wire strings at all. The artifact
  needed for the comparison — the `.csp` — is missing. *(Correction,
  2026-09-23: this is no longer untestable — see the correction section
  above. With the compiled SimplSharp assembly in hand for Clock Audio and
  Biamp, the comparison was made, and it converges at the token level for one
  vendor and the grammar level for the other.)*

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
