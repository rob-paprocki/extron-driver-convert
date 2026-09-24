# Crestron IV-CAM-I20 parity — reply rules (R20) and command-set diff (R23, first step)

Research only, no code changes. Source of truth for every byte string below is one
of:

- **READ** — present in `Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg`'s embedded
  `driver_definition` JSON (`SchemaVersion 2.0`), dumped with
  `py -3.11 -u tools/pkg_dump.py "samples/Crestron 1 Beyond IV-CAM-i12_i20/Crestron/Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg"`.
  Every "JSON path" cell below is a key path into that dump's
  `driver_definition` object.
- **DOCUMENTED** — corroborated by a harvested Crestron support page under
  `reference/crestron-visca/` or `reference/crestron-nextgen-cameras/`, cited by
  file. These pages are the *generic* VISCA reference for this camera family; not
  everything the JSON does is covered by them.
- **UNKNOWN** — genuinely not resolvable by this project. Either the behaviour
  lives only in compiled IL (findings 07/08's "IL-only residue") with no
  declarative JSON form and no documentation page, or the JSON itself has a gap
  (no `Responses` entry names the command in `CommandsProcessed`). Marked as
  such rather than guessed, per finding 13 lesson 8 and STATUS.md's methodology
  notes.

Header/device-ID convention (READ, `driver_definition.Transformations[]`, entry
`ViscaAddressToHeader`, `Type: Math, OpType: Add, Operand: 128`, comment "The
controller address is 0, so simply add 128 (0x80) to the device's VISCA
address"): `Header = 0x80 + DeviceAddress`. Matches Extron's own donor,
`self.DeviceID = 0x80 + int(value)` (finding 13 §2).

Our driver's outgoing bytes for all 82 Crestron commands are already resolved
and verified against this JSON by `experiments/skeleton_i20/resolve_visca.py`
→ `experiments/skeleton_i20/i20_wire_table.txt` (0 unresolved) and
`test_i20_wire.py`. This document does not re-derive those; it covers (a) the
**reply-parsing rules** the wire table does not carry, and (b) which of the 82
Crestron commands our two emitters implement at all.

Driver files read for Task B:
`experiments/skeleton_i20/build_i20.py` (`.pkp` emitter — `NEW_COMMANDS`,
`NEW_METHODS`) and `experiments/skeleton_i20/out/driver_i20.py` (its generated
output, which also carries Extron's unmodified donor commands), plus
`experiments/skeleton_i20/out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py` (the
ControlScript emitter's `self.Commands` table, built by `build_i20_cs.py`).
Both emitters declare the same 32 command names (31 device commands +
`UserDefinedCommand`/`UserDefinedString` pass-through, `ConnectionStatus` in
the CS module is a framework standard, not a device command).

---

## Task A — every Get\*/inquiry Crestron declares: reply rule and parse

18 of Crestron's 82 commands are inquiries (`GetX` naming, or `ViscaCustomInquiry`
templates named otherwise). For each: request bytes, the `Responses[]` entry
that names it in `CommandsProcessed`, its `Match` regex, and how the value is
parsed. Byte values in `Match` are printed as `\u00XX` (single-byte chars);
translated to hex here for readability.

| Crestron command | Request bytes | Status | Reply-match rule | Value parsing | JSON path |
|---|---|---|---|---|---|
| **GetPower** | `{Header} 09 04 00 FF` | READ | `Match`: `[90-F0] 50 [02-04] FF` | `MapBooleanToViscaOnOff` (declared Map): `0x02`→On/true, `0x03`→Off/false; `0x04` "Internal power circuit error" maps to false per an explicit comment (not a Map entry) | `Responses[]` → `ViscaPowerInquiryResponse` |
| **GetExposureCompensationMode** | `{Header} 09 04 3e FF` | READ | `[90-F0] 50 [02-03] FF` | `MapBooleanToViscaOnOff`: 0x02→On, 0x03→Off | `Responses[]` → `ViscaExposureCompensationModeInquiryResponse` |
| **GetExposureCompensation** | `{Header} 09 04 4e FF` | READ (structure) / **UNKNOWN** (assembly IL) | `[90-F0] 50 [00-0F]{4} FF` (4 nibble-bytes) | `ViscaAssemble4LowerNibbles` (referenced, **not declared** in `Transformations[]` — SDK-framework-supplied per finding 08, not driver-local IL, but its exact byte→int algorithm is still not textually specified anywhere in this JSON) → `FromBytesToUInt` (declared, `BigEndianBytesToUint`) | `Responses[]` → `ViscaExposureCompensationInquiryResponse` |
| **GetFocusPosition** | `{Header} 09 04 48 FF` | READ / DOCUMENTED (nibble shape) | `[90-F0] 50 [00-0F]{4} FF` | Same `ViscaAssemble4LowerNibbles` → `FromBytesToUInt` chain. DOCUMENTED: `reference/crestron-visca/COMMANDS.md` §5, `CAM_FocusPosInq`: reply `y0 50 0p 0q 0r 0s FF`, "p,q,r,s: Focus Position" — same 4-nibble MSB-first shape our driver's `_Nibbles`/`_FromNibbles` (build_i20.py, reimplemented rather than recovered — see finding 13 §5, quoted in the method docstring) already assumes for `ZoomPosition`/`PanTiltAngle` | `Responses[]` → `ViscaFocusPositionInquiryResponse` |
| **GetFocusMode** | `{Header} 09 04 38 FF` | READ / DOCUMENTED | `[90-F0] 50 [02-03] FF` | `MapFocusMode` (declared): 0x02→true(Auto), 0x03→false(Manual) | `Responses[]` → `ViscaFocusModeInquiryResponse`; doc: COMMANDS.md §5 `CAM_FocusModeInq`, `y0 50 02 FF`=Auto Focus, `y0 50 03 FF`=Manual Focus |
| **GetAutoFocusBehavior** | `{Header} c2 09 02 FF` (custom inquiry — I20-only, no `CAM_` op code in the generic VISCA doc) | READ | `[90-F0] 50 00 [00-01,04] FF` (single byte, allowed values 0x00/0x01/0x04) | `MapAutoFocusBehavior` (declared): 0x00→'global', 0x01→'center', 0x04→'face' | `Responses[]` → `ViscaAutoFocusBehaviorInquiryResponse` |
| **GetAutoFocusSensitivity** | `{Header} c2 09 03 FF` (custom inquiry) | READ | `[90-F0] 50 00 [01-03] FF` (single byte, 1-3) | `FromBytesToUInt` (declared) — raw integer 1-3, no Map | `Responses[]` → `ViscaAutoFocusSensitivityInquiryResponse` |
| **GetZoomPosition** | `{Header} 09 04 47 FF` | READ / DOCUMENTED (nibble shape) | `[90-F0] 50 [00-0F]{4} FF` | `ViscaAssemble4LowerNibbles` → `FromBytesToUInt`. Same reply also feeds `FieldOfView` and `ZoomPositionPollingOnly` via two extra `Identity` transforms (both raw pass-throughs, declared usage but `Identity` itself has no declared body — SDK built-in) | `Responses[]` → `ViscaZoomPositionInquiryResponse`; doc: COMMANDS.md §5 `CAM_ZoomPosInq`, `y0 50 0p 0q 0r 0s FF` |
| **GetPanTiltSpeedMax** | `{Header} 09 06 11 FF` | READ / DOCUMENTED | `[90-F0] 50 [00-FF]{2} FF` — `Select` splits byte 0 → `PanSpeedMaxHex`, byte 1 → `TiltSpeedMaxHex` (**not** the 4-nibble convention — these are raw bytes, one full byte per axis) | `FromBytesToUInt` (declared) on each byte independently → `PanSpeedMax`, `TiltSpeedMax` | `Responses[]` → `ViscaPanTiltMaxSpeedInquiryResponse`; doc: COMMANDS.md §5 `Pan-tiltMaxSpeedInq`, `y0 50 ww zz FF`, "ww = Pan Max Speed; zz = Tilt Max Speed" — confirms one-byte-per-axis, not nibble-packed |
| **GetPanTiltAngle** | `{Header} 09 06 12 FF` | READ / DOCUMENTED | `[90-F0] 50 [00-0F]{8} FF` — `Select` splits into `PanPositionNibbles` (bytes 0-3) and `TiltPositionNibbles` (bytes 4-7) | `ViscaAssemble4LowerNibbles` → `FromBytesToInt` (**signed**, `BigEndianBytesToInt` — different op than the UInt variant used for zoom/focus/exp-comp) → `PanTiltPositionToAngle` (declared `Math, Divide, Operand 14.4`) → degrees. Also has a `Next: [CheckTiltPositionIsLessThanTopBound, AlwaysMatch]` chain — see Privacy note below | `Responses[]` → `ViscaPanTiltPositionInquiryResponse`; doc: COMMANDS.md §5 `Pan-tiltPosInq`, `y0 50 0w 0w 0w 0w 0z 0z 0z 0z FF`, and §11's "1 angle = 14.4" cross-check (matches the declared `PanTiltPositionToAngle`/`PanTiltAngleToPosition` Operand exactly) |
| **GetDeviceInformation** | `{Header} 09 00 02 FF` | READ / DOCUMENTED (byte layout) / **UNKNOWN** (ROM-version format) | `[90-F0] 50 [00-FF]{6} [01-02] FF` — `Select` splits: bytes[0:2] fixed marker (doc: `00 01`), bytes[2:4]→`ModelCode`, bytes[4:6]→`RomVersion`, byte[6]∈{1,2}=Socket Number | `MapModelCodeToModel` (declared): `0x05 0x05`→"IV-CAM-I20", `0x05 0x06`→"IV-CAM-I12", `0x05 0x07`→"IV-CAM-P20", `0x05 0x08`→"IV-CAM-P12", else "Unknown". `FormatRomVersion` — **referenced, not declared, no driver-local-IL-family doc string either; genuinely UNKNOWN how the 2 raw ROM-version bytes become `DeviceFirmwareVersion`** (finding 08's 6-name I20 IL-residue list includes `FormatRomVersion` explicitly) | `Responses[]` → `ViscaVersionInquiryResponse`; doc: COMMANDS.md §5 `CAM_VersionInq`, `y0 50 00 01 mn pq rs tu vw FF`, "m,n,p,q: Model Code; r,s,t,u: ROM version; v,w: Socket Number" — byte-position match confirmed by direct offset arithmetic (both put Model Code at offset 2-3, ROM version at 4-5, Socket at 6) |
| **GetAutoSoftwareUpdate** | `{Header} c2 09 04 FF` (custom inquiry) | READ | `[90-F0] 50 00 [00-01] FF` | `MapBooleanToBinaryOnOff` (declared): 0x01→true, 0x00→false | `Responses[]` → `ViscaAutoSoftwareUpdateInquiryResponse` |
| **GetTrackingFraming** | `{Header} 09 08 01 FF` | READ / DOCUMENTED | `[90-F0] 50 [02-03] FF` | `MapBooleanToViscaOnOff`: 0x02→true(active), 0x03→false(paused) | `Responses[]` → `ViscaTrackingStatusInquiryResponse`; doc: COMMANDS.md §5 `CAM_TrackingInq`, `y0 50 02 FF`="Checks if tracking is active", `y0 50 03 FF`="...is paused" (also cited already in build_i20.py's `_cmd_UpdateTrackingFraming`) |
| **GetGroupTracking** | `{Header} c2 09 06 FF` (custom inquiry) | READ | `[90-F0] 50 00 [00-01] FF` | `MapBooleanToBinaryOnOff`→`GroupTrackingIsActive`; `InvertBoolean` (declared)→`PresenterTrackingIsActive`; then two `Identity`-with-`InputDictionary` steps build a nested `{name, supportsIsActive, isActive}` object for each mode, merged into `TrackingFramingModes` — i.e. **one boolean byte drives two derived statuses**, not two independent reads | `Responses[]` → `ViscaGroupTrackingStatusInquiryResponse` |
| **GetTrackingFramingProfile** | `{Header} c2 09 07 FF` (custom inquiry) | READ | `[90-F0] 50 (06 [09-0C]) FF` — 2 nibble-bytes, second constrained to 0x09-0x0C | `ViscaAssemble2LowerNibbles` (referenced, **not declared** — this is I20's one driver-local-IL addition beyond the shared 5-name family per finding 08/13's intro; genuinely UNKNOWN as an exact algorithm, though it is presumptively "the same 2-nibble MSB-first assembly as the 4-nibble version" — not proven) → `Preset` → `MapTrackingFramingProfileToPreset` (declared, **inverse** direction via `~{Preset}`) : preset 0x69→'trackingProfile1' ... 0x6C→'trackingProfile4' | `Responses[]` → `ViscaTrackingFramingProfileInquiryResponse` |
| **GetFreezeFrame** | `{Header} 09 04 62 FF` | READ (request only) / **UNKNOWN** (reply rule — genuinely absent) | **No `Responses[]` entry lists `GetFreezeFrame` in `CommandsProcessed`.** A reply to this inquiry falls through to the catch-all `ViscaUnknownResponse` (`Match: [00-FF]* FF`), which parses nothing. | N/A — not declared | Searched all 31 `Responses[]` entries; confirmed absent. The `FreezeFrame` **Controller** (`Controllers[]`, `PollingInterval: 4000`) carries `AckAsFeedback: true` and `RequireFeedback: true` — this is almost certainly *why* there is no dedicated response rule: Crestron's own driver treats the Set command's ACK as the feedback source, and the periodic Get inquiry's reply value is not actually consumed. Our driver (`build_i20.py` `_cmd_UpdateFreezeFrame`) invented its own parse (`res[2]`, `0x02`/`0x03`) that Crestron's JSON does not corroborate at all — it is the correct VISCA on/off convention by analogy to every other boolean inquiry on this camera, but it is **not sourced from Crestron's driver** the way the others in this table are. |
| **GetAutoPrivacyMode** | `{Header} 09 0e 24 26 FF` | READ | `[90-F0] 50 00 [00-01] FF` | `MapBooleanToBinaryOnOff`: 0x01→true, 0x00→false | `Responses[]` → `ViscaAutoPrivacyModeInquiryResponse` |

That is 17 rows with dedicated reply rules + 1 (`GetFreezeFrame`) with none = **18
Get\*/custom-inquiry commands**, matching the count of `Get`-named or
`ViscaCustomInquiry`-templated commands in the 82-command list (`GetPower`,
`GetExposureCompensationMode`, `GetExposureCompensation`, `GetExposureMode`,
`GetAutoPrivacyMode`, `GetFocusPosition`, `GetFocusMode`, `GetAutoFocusBehavior`,
`GetAutoFocusSensitivity`, `GetZoomPosition`, `GetPanTiltSpeedMax`,
`GetPanTiltAngle`, `GetDeviceInformation`, `GetFreezeFrame`,
`GetAutoSoftwareUpdate`, `GetTrackingFraming`, `GetGroupTracking`,
`GetTrackingFramingProfile`). `GetExposureMode` (row omitted above for space —
see next paragraph) is the 18th.

**GetExposureMode** (`{Header} 09 04 39 FF`): READ. `Match`:
`[90-F0] 50 [00-0F] FF` (single nibble-range byte, i.e. the full 0-15 range, not
restricted to the documented 5 values). `MapExposureMode` (declared) is applied
**inverted** (`~{ExposureMode}`) but the Map itself only has two forward entries
(`true`→0x00, `false`→0x03) plus a `Comment` field (not a Map entry) listing all
four documented values — so **only 0x00 and 0x03 round-trip through the reply
parser**; a camera reporting Shutter Priority (0x0A) or Iris Priority (0x0B) hits
`InverseDefault: "false"` and is silently reported as Manual. This is the same
asymmetry finding 13 §2 flagged from the request side ("the vendor with 16
commands is richer than the vendor with 82") reproduced on the *reply* side of
Crestron's own driver — not a gap in ours, a gap in Crestron's. `Responses[]` →
`ViscaExposureModeInquiryResponse`. DOCUMENTED: COMMANDS.md §5 `CAM_AEModeInq`
lists all 5 values (`y0 50 00/03/0A/0B/0D FF`).

### Summary: IL-only vs SDK-built-in vs driver-declared, for reply parsing

Cross-referencing every `Transformation` name used above against the 26 entries
in `driver_definition.Transformations[]` (parse script:
`ToolSearch`-independent, ad hoc, see method note at the end of this file):

| Category | Names | Status |
|---|---|---|
| Declared, fully specified | `MapBooleanToViscaOnOff`, `MapExposureMode`, `MapFocusMode`, `MapAutoFocusBehavior`, `MapBooleanToBinaryOnOff`, `InvertBoolean`, `MapModelCodeToModel`, `MapTrackingFramingProfileToPreset`, `FromBytesToUInt`, `FromBytesToInt`, `PanTiltPositionToAngle` | READ — exact byte↔value tables in the JSON itself |
| Referenced, undeclared, **driver-local IL** (finding 08's bounded 6-name I20 family) | `FormatRomVersion`, `ViscaAssemble2LowerNibbles` (I20's 6th, beyond the 5 shared with P20: `ParseDecimal`, `ZoomLevelToPosition`, `ZoomPositionToLevel`, `ApplyZoomPositionStep`, plus `OverridePolynomial` never called by literal name) | **UNKNOWN** — genuinely not recoverable without decompiling `Camera_Crestron-1-Beyond_IV-CAM-I20_IP.dll`'s IL (out of scope here; finding 07/08 did the metadata-only pass, not full IL decompilation) |
| Referenced, undeclared, **SDK-framework-supplied** (finding 08: "remaining undeclared names supplied by the SDK framework itself") | `ViscaAssemble4LowerNibbles`, `ViscaExtractNibbles`, `Identity`, `Divide`, `Sum`, `Subtract`, `Product` | DOCUMENTED (for the nibble-assembly ones) by pattern-matching against `reference/crestron-visca/COMMANDS.md` §1's repeated `0p 0q 0r 0s` convention and `ZOOM.md` §1's explicit statement that the docs never narrate the packing formula in prose — so the *shape* is documented, the *exact algorithm* is inferred, not read |

### Which of our emulated (`'Live': False`) i20-patch statuses could become Live

`build_i20.py`'s `NEW_COMMANDS` table (E3) marks these i20-added entries
`'Live': False` with `'Emulated': True` (status only ever reported as the
optimistic value written at Set time, never confirmed by a device reply):
`TrackingMode`, `TrackingProfile`, `IndicatorLight`, `IntelligentSwitching`.
Checked each against Task A/B's inquiry inventory:

| Our status (`Live: False`) | Could go live? | How |
|---|---|---|
| `TrackingMode` | **Yes** | `GetGroupTracking` (`c2 09 06`) exists in Crestron's 82 and has a full reply rule (Task A row) — we simply never added `_cmd_UpdateTrackingMode`/wired the `'Update'` flag. One boolean byte drives both `GroupTrackingIsActive` and (inverted) `PresenterTrackingIsActive`, matching our two-valued `TrackingMode` enum directly |
| `TrackingProfile` | **Yes** | `GetTrackingFramingProfile` (`c2 09 07`) exists and has a full reply rule (Task A row), via the `ViscaAssemble2LowerNibbles`-dependent 2-nibble preset byte → `MapTrackingFramingProfileToPreset`. The reply parse itself touches the one driver-local-IL name I20 adds beyond the shared 5 (`ViscaAssemble2LowerNibbles`), so "go live" would mean reimplementing that assembly the same way `build_i20.py`'s `_Nibbles`/`_FromNibbles` already reimplement the 4-nibble version (standard VISCA nibble packing, not recovered IL) |
| `IntelligentSwitching` | **Yes, and no new command needed** | We already send `GetOutput` (`c2 09 08`) for `CameraOutput` and parse its reply in `_cmd_UpdateCameraOutput`. Per `VISCA-Intelligent-Switching-Commands.md`, that reply is `Y0 50 0S 0Z FF` — `S` (byte offset 2, i.e. `res[2]`) is the Intelligent-Switching on/off flag, `Z` (offset 3, `res[3]`) is the camera number. Our code already reads `res[3]` for `CameraOutput` (correctly, per the `experiments/loopback` fix cited in `build_i20.py`) but **discards `res[2]`** — the exact byte `IntelligentSwitching`'s status needs is already arriving on every `CameraOutput` poll and is currently thrown away |
| `IndicatorLight` | **No** | Crestron's own 82 commands have no `GetIndicatorLight`/lightbar-state inquiry at all — `SetIndicatorLight` is Set-only on Crestron's side too. Cannot be made live from anything Crestron declares |

Not marked `Emulated` but worth noting for the same reason: `PresetZone`,
`TrackingShot`, `Menu`, `Identify`, `PanTiltHome`, `Reboot` are momentary
actions with `'Live': False, 'Emulated': False` — Crestron's own 82 commands
have no corresponding Get for any of them (they are one-shot preset recalls or
resets), so "live" status is not a meaningful concept for these, on either
vendor's driver.

---

## Task B (first step) — Crestron's 82 commands vs our two emitters' 32

Both `experiments/skeleton_i20/out/driver_i20.py` (`.pkp`, `self.Commands`) and
`out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py` (ControlScript, `self.Commands`)
declare the same 32 names. Verified: `grep -c "':.*'Status': {}"` structure in
both; command-name sets identical except CS's extra framework `ConnectionStatus`
entry (not device-specific — present in every ControlScript camera module).

### 82 → 32, full accounting

| Crestron command | Ours? | Our name | Note |
|---|---|---|---|
| PassThrough | — | (framework) | Raw byte passthrough; not a device feature, no Extron equivalent needed |
| ViscaPacket / ViscaCommand / ViscaInquiry / ViscaReservedCommand / ViscaCustomCommand / ViscaCustomInquiry | — | (templates) | Wire-format templates, not commands; resolved by `resolve_visca.py`, not implemented as such |
| GetPower / SetPower | ✅ | `Power` | Donor command, unmodified. `01 04 00 {OnOff} FF` — exact byte match |
| GetExposureCompensationMode / SetExposureCompensationMode | ❌ | — | **Missing.** Wire: `{Header} 09/01 04 3e [{OnOff}] FF`. READ. `OnOff`: `MapBooleanToViscaOnOff` (0x02/0x03) |
| GetExposureCompensation / SetExposureCompensation | ❌ | — | **Missing.** Set: `{Header} 01 04 4e 00 00 {Y2} {Y1} FF` (2-nibble `ViscaExtractNibbles`, range not declared in JSON — DOCUMENTED range via COMMANDS.md §7's EV table, -7..+7, byte `0x00`-`0x0E`). Get: see Task A |
| IncrementExposureCompensation / DecrementExposureCompensation | ❌ | — | **Missing.** `{Header} 01 04 0e 02/03 FF` — READ, fixed-byte, no parameters |
| GetExposureMode / SetExposureMode | ⚠️ partial | `AutoExposure` | Donor's `AutoExposure` (`01 04 39 {v} FF`) is a **superset**: 5 values (Full Auto 0x00, Manual 0x03, Shutter Priority 0x0A, Iris Priority 0x0B, Bright 0x0D) vs Crestron's own declared 2-value Map (finding 13 §2) — same op-code family, richer on our side |
| PrivacyCommand / EnablePrivacy / DisablePrivacy | ❌ | — | **Missing.** Not a boolean VISCA flag — Crestron implements privacy as `SetPanTiltAngle` at max pan/tilt speed to a fixed tilt angle (`{TiltAngle.Max}` for enable, `{TiltAngleDisablePrivacy}` for disable), reusing the `SetPanTiltAngle` wire format from Task A's `GetPanTiltAngle` row. So the "wire bytes" for this feature are identical to `SetPanTiltAngle`'s (already in `i20_wire_table.txt` line 48); READ. Status feedback is **not from an inquiry at all** — see note below |
| GetAutoPrivacyMode / SetAutoPrivacyMode | ❌ | — | **Missing.** See Task A row. `{Header} 09/01 0e 24 26 [00 {OnOff}] FF` |
| GetFocusPosition / SetFocusPosition | ❌ | — | **Missing** (absolute focus). Set: `{Header} 01 04 48 {Y4}{Y3}{Y2}{Y1} FF`, value 0-16384-ish (not declared; DOCUMENTED shape only, COMMANDS.md §5 `CAM_FocusPosInq`) |
| FocusCommand / FocusCloser / FocusFarther / FocusStop | ⚠️ partial | `Focus` | Donor's `Focus` (`01 04 08 {speed}`) supports **variable speed** 0-7 (COMMANDS.md §4 "Far(Variable)"/"Near(Variable)", `8x 01 04 08 2p/3p FF`); Crestron's own declared `FocusCommand` template uses `MapFocusDirection` which has **no speed input at all** — only the fixed-speed byte (0x02/0x03/0x00). Same op-code, ours is the richer side here, mirroring finding 13's exposure-mode asymmetry in reverse |
| GetFocusMode / SetFocusMode | ✅ | `AutoFocus` | Donor command, unmodified. `01 04 38 {v} FF`, On=0x02/Off=0x03 — exact match |
| OnePushAutoFocus | ❌ | — | **Missing.** `{Header} 01 04 18 01 FF` — READ, fixed-byte, no parameters. DOCUMENTED: COMMANDS.md §4 `CAM_Focus` "One Push Trigger" |
| GetAutoFocusBehavior / SetAutoFocusBehavior | ❌ | — | **Missing.** `{Header} c2 09/01 02 [{v}] FF`. Values (READ, `MapAutoFocusBehavior`): global=0x00, center=0x01, face=0x04 |
| GetAutoFocusSensitivity / SetAutoFocusSensitivity | ❌ | — | **Missing.** `{Header} c2 09/01 03 [{AsByte(1-3)}] FF`. Range 1-3 READ from the reply `Match`'s `[\x01-\x03]` character class (request side has no declared range — `AsByte` has none) |
| SetZoomSpeed | N/A | — | Crestron's own driver declares this as an empty no-op Text command ("must be present so Set is supported... but is never sent due to use of `StatesSet`") — not a real wire command on Crestron's side either; no gap |
| GetZoomPosition / SetZoomPosition | ✅ | `ZoomPosition` | i20-patch command (E3/E4). `01 04 47 {speed}{Y4}{Y3}{Y2}{Y1} FF` — exact match, verified in `i20_wire_table.txt` and `test_i20_wire.py` |
| SetFieldOfView | ❌ | — | **Missing.** Wire is **byte-identical to `SetZoomPosition`** (`01 04 47 {ZoomSpeedHex}{Y4}{Y3}{Y2}{Y1} FF`) — same template, different Transformation input (`{FieldOfView}` vs `{ZoomPosition}`). The FOV↔position conversion is `ZoomPositionToFieldOfView`/`FieldOfViewToZoomPosition`, **declared** `Type: Polynomial` transforms (`Min`/`Max`/`MinInput`/`MaxInput` — READ, not IL) — so unlike the `ZoomLevelToPosition` family this one IS fully declarative and could be implemented without any IL residue. `Min: 4.159363682153226°`, `Max: 67.07093698846305°` over `MinInput 0`/`MaxInput 16384` |
| ZoomCommand / ZoomIn / ZoomOut / ZoomStop | ✅ | `Zoom` | Donor command, **E2-patched** (finding 13 §3 — Extron's shipped driver discarded the speed byte; our derivation fixes it to match Crestron's single `{SpeedAndDirection}` byte exactly) |
| GetPanTiltSpeedMax | ❌ | — | **Missing.** See Task A row. `{Header} 09 06 11 FF` |
| SetPanSpeed / SetTiltSpeed | N/A | — | Same no-op pattern as `SetZoomSpeed` — Crestron's own driver never sends these either |
| GetPanTiltAngle / SetPanTiltAngle | ✅ | `PanTiltAngle` + `PanAngleStatus`/`TiltAngleStatus` | i20-patch. `06 02 {PanSpeedHex}{TiltSpeedHex}{Y4..Y1}{Z4..Z1} FF` — exact match. Split into two Extron status assets the way `pana_19_5702` does (see build_i20.py comment) |
| SetPtzSuperOperation | ❌ | — | **Missing.** `{Header} 01 15 01 {U4..U1}{PanSpeedHex}{TiltSpeedHex}{ZoomSpeedHex}{X4..X1}{Y4..Y1}{Z4..Z1} FF` — a combined pan+tilt+zoom+FOV "super operation" with its own 4-nibble operation-ID field (`{PtzSuperOperation}`, range/meaning not declared anywhere in the JSON — **UNKNOWN** what values `U1-U4` may take). Has dedicated async reply handling (`PtzSuperOperationUpdate`/`Complete`/`Ack` in `Responses[]`, RootNode-reachable) that nothing else in the 82 commands uses — a stateful multi-packet exchange, not a single request/reply |
| PanTiltDrive / PanTiltStop | ✅ | `PanTilt` | Donor command, unmodified. `06 01 {PanSpeedHex}{TiltSpeedHex}{PanDirectionHex}{TiltDirectionHex} FF` — donor's combined-direction-byte encoding decodes to the exact same two direction bytes Crestron documents separately (verified: donor's `'Up': 0x0301` packs big-endian to bytes `03,01` = pan-dir Stop(3)/tilt-dir Up(1), matching COMMANDS.md §4 `Pan-tiltDrive Up: 8x 01 06 01 VV WW 03 01 FF` exactly) |
| PanTiltReset | ✅ (dual) | `PanTilt` (`'Reset'`) **and** `PanTiltHome` | Donor's `PanTilt` already has a `'Reset': 0x05` value (`06 05 FF`) that is byte-identical to Crestron's `PanTiltReset`. The i20-patch **also** added `PanTiltHome` sending the same `06 05` bytes — so the wire is covered twice, once under the donor's pre-existing name and once under a new i20-specific name that (confusingly) matches Crestron's `PanTiltReset` op-code, not VISCA's separate `06 04` "Home" op-code (COMMANDS.md §4 `Pan-tiltDrive Home: 8x 01 06 04 FF`, distinct from `PTZ Correction: 8x 01 06 05 FF`). No functional gap, naming is muddled — `PanTiltHome` implements "PTZ Correction," not VISCA's own "Home" |
| GetDeviceInformation | ❌ | — | **Missing entirely.** No command, no method, no status field for Model or firmware version anywhere in `driver_i20.py` (0 matches for `DeviceInformation`/`FirmwareVersion`/`Model`). See Task A row for the wire bytes |
| SetIndicatorLight | ✅ | `IndicatorLight` | i20-patch (E5). `c1 {LedBar} FF` — all 19 documented lightbar strings verified byte-for-byte (finding 13 §6, `test_i20_wire.py`) |
| ResetPresetCommand / SetPresetCommand / RecallPresetCommand | ✅ | `Preset` (donor, `Action` qualifier) | `01 04 3f {action}{preset} FF`, `action` ∈ {Reset:0x00, Save:0x01, Recall:0x02} — exact match to Crestron's three separate command names, which all resolve to this one template family with the same action bytes |
| Reboot | ✅ | `Reboot` | i20-patch, reserved preset `0x63` via `_PresetOpcode` — exact match |
| GetFreezeFrame / SetFreezeFrame | ✅ (Set) / ⚠️ (Get) | `FreezeFrame` | Set: `01 04 62 {OnOff} FF`, On=0x02/Off=0x03 — exact. Get: sent (`09 04 62 FF`), but see Task A — **Crestron's own JSON has no reply rule for it either**, so our `_cmd_UpdateFreezeFrame`'s parse is unsourced-but-plausible, not verified against Crestron |
| Menu | ✅ | `Menu` | i20-patch, reserved preset `0x5F` — exact match |
| PressAndHoldSelect / PressAndHoldBack / ReleaseBackOrSelect / PressAndHoldUp / PressAndHoldDown / PressAndHoldLeft / PressAndHoldRight / ReleaseArrowKey | ❌ (all 8) | — | **Missing entirely — the "PressAndHold/Release menu" family.** These drive the camera's on-screen menu via fixed VISCA bytes reusing the `Focus` (`01 04 07 02/03/00 FF` for Select/Back/Release — note: op `04 07` is the **Zoom** op-code, not Focus's `04 08`; Crestron's driver reuses the zoom-speed-and-direction byte range 0x02/0x03/0x00 for menu Select/Back/Release, a repurposing not documented anywhere as a "menu" function) and `PanTiltDrive` (`06 01 01 01 03 01/02/01 03/02 03/03 03 FF` for arrow keys, fixed min-speed 0x01 — build_i20.py-equivalent comment "Pan and tilt speeds do not matter") op-codes. All 8 are READ, fixed-byte, zero parameters. Controllers `BackOrSelect`/`ArrowKey` (`Type: "Command"`, `ReleaseCommand`) show this is a press/release UI pattern, not a boolean toggle |
| RecallPreset / SavePreset | ✅ (via `Preset`) | `Preset` | Alternate entry points into the same `RecallPresetCommand`/`SetPresetCommand` template family (state-sourced preset number, `{RecalledPreset}`/`{sceneId}`, vs our `Preset`'s qualifier-supplied value) — same bytes, functionally covered |
| GetAutoSoftwareUpdate / SetAutoSoftwareUpdate | ❌ | — | **Missing.** `{Header} c2 09/01 04 [{OnOff}] FF`. `MapBooleanToBinaryOnOff` (0x01/0x00). Polled every 30000 ms per `Controllers[].AutoSoftwareUpdate` (the slowest poll interval in the driver) |
| Identify | ✅ | `Identify` | i20-patch. `c2 01 01 0a FF` — exact match |
| GetTrackingFraming / StartTrackingFraming / StopTrackingFraming | ✅ | `TrackingFraming` | i20-patch. Presets `0x50`/`0x51`; Get reply parsed per finding 13 §8's fix (documented `y0 50 02/03 FF`) |
| GetGroupTracking / EnableGroupTracking / EnablePresenterTracking | ⚠️ (Set only) | `TrackingMode` | Set covered (presets `0x52`/`0x53`, merged into one command at `20027` per finding 13 §7). **Get (`c2 09 06`) is missing** — `TrackingMode`'s `'Update': False` in the Commands table; no `_cmd_UpdateTrackingMode` exists |
| GetTrackingFramingProfile / SetTrackingFramingProfile | ⚠️ (Set only) | `TrackingProfile` | Set covered (presets `0x69-0x6C`, reserved-preset numbers **not** supplied by Crestron's own `SetTrackingFramingProfile` template — sourced from `reference/crestron-visca/Reserved-Presets.md` per finding 13 §6, not the JSON). **Get (`c2 09 07`) is missing** — `TrackingProfile`'s `'Update': False` |

### Counts

Counted directly off the 38 rows of the table above (each row's command count
verified to sum to 82 exactly — script-checked, not eyeballed):

| Category | Commands | Rows |
|---|---|---|
| Protocol/template plumbing, not a device feature (`PassThrough`, the 6 `Visca*` templates) | 7 | 2 |
| Crestron's own declared no-ops (`SetZoomSpeed`, `SetPanSpeed`, `SetTiltSpeed`) — no gap on either side | 3 | 2 |
| **Fully covered** (✅ rows — exact or superset wire match) | **27** | 14 |
| **Partially covered** (⚠️ rows — one direction, usually Set, covered; the other, usually Get, missing) | **13** | 5 |
| **Fully missing** (❌ rows — no command, no method, anywhere in either emitter) | **32** | 15 |
| **Total** | **82** | 38 |

The 32 fully-missing commands cluster exactly around the ROADMAP R23 list:
privacy (3 commands: `PrivacyCommand`/`EnablePrivacy`/`DisablePrivacy`) +
`AutoPrivacyMode` (2) = 5 privacy-related; exposure compensation (`Mode` 2 +
value 2 + Increment/Decrement 2 = 6); focus position (2); `OnePushAutoFocus`
(1); AutoFocus behaviour/sensitivity (4); `AutoSoftwareUpdate` (2);
`GetDeviceInformation` (1); the PressAndHold/Release menu (8);
`SetFieldOfView` (1); `SetPtzSuperOperation` (1); `GetPanTiltSpeedMax` (1) —
that is 5+6+2+1+4+2+1+8+1+1+1 = 32, exactly the fully-missing total, with no
double-counting against the 13 partially-covered commands (`GetExposureMode`
family, `FocusCommand` family, `GetFreezeFrame`, and the Get-only halves of
`GroupTracking`/`TrackingFramingProfile`).

Extron's donor also exposes **Gain, Iris, Shutter, Backlight, WhiteBalance**
(5 more commands, generic VISCA op-codes `04 0B/0C/0A/33/35` — all present in
`reference/crestron-visca/COMMANDS.md`'s generic command table) that
**Crestron's own 82-command JSON does not declare at all** for this camera —
the asymmetry runs both ways, not just "Extron is missing things."

---

## Notes flagged during this pass, not asked for directly but load-bearing

1. **Privacy status is not read from any inquiry.** `EnablePrivacy`/
   `DisablePrivacy` are pure `SetPanTiltAngle` calls (tilt to a fixed angle).
   The `Privacy` Controller (`Controllers[]`) has **no `Get` in its
   `CommandSet`** at all. Its `false` feedback is inferred as a side effect of
   `GetPanTiltAngle`'s reply, via a `Next` chain:
   `ViscaPanTiltPositionInquiryResponse` → `CheckTiltPositionIsLessThanTopBound`
   (condition `TiltPositionIsLessThanTopBound`, comparing against
   `PanTiltAngleToPosition(90)`) → `PrivacyDisabledFeedback` (unconditionally
   sets `Privacy: false`). There is **no corresponding path that sets
   `Privacy: true`** anywhere in `Responses[]` — Privacy-ON is only ever
   `Emulated`/ack-based (`AckAsFeedback: true` on the Controller), never
   confirmed live. If a synthesized driver adds Privacy, the honest design is
   the same asymmetry Crestron's own driver has, not a symmetric Get.
2. **`AutoPrivacyMode`** (the `0e 24 26` toggle) is a **separate feature** from
   `Privacy` above — it is a real boolean VISCA flag with its own dedicated
   Get/Set and its own Controller entry (`PollingInterval: 4000`). Do not
   conflate the two "privacy" names.
3. **`GetDeviceInformation`'s Controller comment is load-bearing**:
   `DeviceInformationProperties` (`Controllers[]`) carries "MUST be ordered
   last (besides Command controllers) because Ready is set based on existence
   of DeviceFirmwareVersion!" — i.e., in Crestron's own driver, device
   readiness itself gates on this inquiry succeeding at least once. Our driver
   has no equivalent readiness gate since it has no `GetDeviceInformation` at
   all.
4. **Naming convention for `CommandSet`**: most Controllers (e.g.
   `AutoPrivacyMode`, `AutoSoftwareUpdate`) declare no explicit `CommandSet` at
   all and are presumably bound by a `Get<Name>`/`Set<Name>` naming convention;
   Controllers whose Set command doesn't follow that pattern (`Privacy` →
   `EnablePrivacy`/`DisablePrivacy`; `TrackingFraming` →
   `StartTrackingFraming`/`StopTrackingFraming`) declare `CommandSet`
   explicitly. Noted because it explains why some Task A rows have an obvious
   JSON anchor and others (the convention-bound ones) don't show up under a
   `CommandSet` search.

## Method

`py -3.11 -u tools/pkg_dump.py <pkg> > dump.txt` (repo-relative paths; dump
written to the job's private tmp dir, not committed) then ad hoc Python
(`json.load` + dict/list walks) to extract `driver_definition.{Commands,
Responses, Conditions, Transformations, Rules, Controllers, DriverController}`
and cross-reference every `"Transformation": "<name>"` occurrence against the
26 entries actually declared in `Transformations[]`. No IL decompilation was
performed in this pass — the UNKNOWN markers above are exactly findings 07/08's
already-bounded residue (`FormatRomVersion`, `ParseDecimal`,
`ZoomLevelToPosition`, `ZoomPositionToLevel`, `ApplyZoomPositionStep`,
`ViscaAssemble2LowerNibbles` for I20), re-confirmed present in this specific
package's JSON, not re-derived from scratch.
