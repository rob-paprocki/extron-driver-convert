# Automate VX: three-way verification (Extron GC and ControlScript, Crestron module and native IP ID, API docs)

Date: 2026-09-24. All three extractions arrived; none was null. I re-read the sources wherever an extraction was unclear, and three of my checks changed the picture: (1) the documentation site publishes its own table of contents, (2) the GC package declares the parameter types, and (3) the Automate VX 6.4.1.8 release notes. Each is covered below.

*Produced 2026-09-24 by a multi-agent pass: three independent extractions, then one comparison
(this report), then an adversarial verifier that re-checked every discrepancy against the files and
live pages. It confirmed all 37. By hand afterwards: X14, X19, X24 and X25 re-read at the cited
lines, and the site TOC re-counted (48 API pages, index built 2026-05-26), all as stated.*

*Extraction [0] is Extron's two drivers, [1] Crestron's SIMPL module plus the native IP ID
research, [2] the live documentation. `gc:N` is a line of `1bynd_42_4279.embedded.py`
(`surfaces.py extract`); `cs:N` a line of the ControlScript module; `cmc:N` a line of the
`.cmc`.*

## 1. Summary

**How much is documented.** The site's own TOC is `Data/HelpSystem.xml` → `Data/Tocs/Manual_TOC_Automate_API_Chunk0.js`, built 2026-05-26. It lists **48 API pages**. The repo harvest has 43. Extraction [2] reported that no TOC exists, but it probed the wrong filename (`Data/Tocs/0.js`).

- **5 pages exist on the site but in neither the harvest nor extraction [2]:** `PauseRecord`, `ExportCameraPresets`, `HealthStatus` (page `Health-Status-API.htm`), `StorageSpaceAvail` and `CloseWirecast`. All five return 200 live.
- **`GetActiveTalkers`** is live and linked from What's New, but it is not in the TOC.
- **Total: 49 documented calls.**
- **4 names the drivers use have no page.** These are `StartISORecord`, `StopISORecord`, `ISORecordStatus` and `CopyStatus`. None is in the TOC. Six ISO name variants all return 404. `ISORecordStatus` and `CopyStatus` appear only inside `GetAllStatus`'s example.

**Extron GC (1bynd_42_4279 v1.0.11) and ControlScript (v1.0.11.0) have identical wire surfaces.**
- Both call the same 33 URIs, a byte-identical set (checked by `sort -u` and `diff`). That is 30 documented calls plus the 3 undocumented ISO calls.
- The 30 documented URIs match the documented base URI exactly, including case.
- Method, headers and the empty-body convention all match the docs. Every call is a POST with `Content-Type: application/json`. Get-token sends `Authorization: base64(user:pass)` and later calls send `Authorization: <token>`.
- All 6 body key names (`id`, `address`, `cam`, `pre`, `ptDir`, `zDir`) match the docs, as do the enumerations (ptDir 0–7 mapping, zDir 0/1, layout A–Z) and the ranges (1–99, 1–255).
- Response field names match the dedicated pages: `token`, `results`, `roomConfigs[0].id`, `scenario.id`, `address`.
- **Coverage is 30 of 49 documented calls.**

**Crestron SIMPL module (1Beyond Automate_VX v1.2).** All network logic sits behind `1Beyond Automate_VX_v1.2.csp`: §8 found it in the installed device database, a SIMPL+ wrapper over a compiled SIMPL# library. **§10 decompiles that library**, so its requests are now read too: 42 URIs, with the bodies, value types, headers and session handling. The bullets below are the join-level view that came first.
- By join name, it covers 36 of the 49 documented calls plus the 4 undocumented names.
- On the face of its joins and help sheet, its value ranges lag the current API: cameras 1–8, layouts A–Y, scenarios 1–10. §8 revises this from the source: only A–Y is a real limit, set by the wrapper's 25 layout joins.
- Its default transport is HTTP (`Request_Type` defaults to 0 = HTTP on port 3579). Crestron's 6.4.1.8 release notes say new installations no longer support that legacy mode.

**Native IP ID** applies only to Automate VX2 hardware. It needs Automate VX ≥ 6.2.2.27 and a SIMPL device database ≥ 200.355.002.00, and the unit registers the control system through its IP Table (IP ID, port 41794, optional SSL).
- **The join map was not found.** I checked the VX2 manual's published TOC (22 topics, none a join map or SIMPL topic) and ran a WebSearch.
- Only two functions have indirect evidence: scenario recall and active talkers.
- First-generation hardware gets no native path; the 6.2.1.18 release notes say "Use Crestron Module for control".

### The discrepancies that matter most
1. **X19, fails on device (per the vendor release note; not measured on a unit).** The Crestron module defaults to HTTP on 3579. Release note [AVX-2994] (6.4.1.8) says the API defaults to HTTPS and "New installations do not support legacy mode". Setting `Request_Type`=HTTPS and `Port`=4443 fixes it.
2. **X25, fails on device.** The ControlScript sheet (page 4) documents `Set('Scenario', None, {'ID': 'String'})`. The v1.0.11.0 code runs `if 1 <= value:` (cs:300), which raises `TypeError` for `None` or any string. The GC sheet documents it correctly.
3. **X14, unknown, possibly fails on device.** The `RoomConfigStatus` page documents a list, `roomConfigs:[{id,name}]`. `GetAllStatus`'s example of the same sub-call shows an object, `roomConfig:{id,name}`. Both Extron drivers read `res['roomConfigs'][0]['id']` (gc:595, cs:293). If the device returns the singular object, Room Configuration feedback never updates.
4. **X12a–d, unknown (H6). JSON value types are wider than H6 lists.**
   - The docs' prose says Integer for 14 fields, but every Body-JSON and cURL example quotes them as strings. The docs contradict themselves.
   - Extron sends **10 of them as strings**: `GoToScenario.id` and `ptDir`/`zDir` (the three H6 names), plus `ChangeRoomConfiguration.id`, `ForceChangeRoomConfig.id`, `ManualSwitchCamera.address` and `cam`/`pre` for both preset calls.
   - Extron sends **`cam` as a number** in StartPT, StopPT, StartZ and StopZ.
   - For GC this is now settled offline from the package: those fields are `EnumParamAsset` with string states `'1'…'N'`, while PanTilt/Zoom `Camera` and `Scenario` are `DecimalParamAsset`.
5. **X07, unknown. The ISO-record family is undocumented today but is not an invention.**
   - Extron's GC script cites "Pg 26 & 28" and "Pg 30" of "Automate API - 2023-12-28.pdf" for it (gc:335, 350), so an earlier edition of the API document covered it.
   - Release note [AVX-2735] (6.4.0.49) shows ISO recording is still a product feature.
   - Nothing yet shows the API calls still work.
6. **X02, X03, X04, X05: capability gaps.**
   - **Extron (both drivers):** no `PauseRecord`, no layout status or name lists, no room-config or scenario name lists.
   - **All three drivers:** no `GetActiveTalkers`, no `ShotStatus`, no `HealthStatus`.
   - **Crestron:** no `SaveCameraPreset`.
7. **X10.** The Crestron module wires `CallPlugin` with 3 arguments; the doc page has 2. The changelog says support was removed in 6.4.1, yet the page is still in the TOC.

### Corrections this pass makes to the inputs and to repo claims
- **Extraction [2]:** a TOC does exist, and it lists 48 pages rather than the 44 that extraction counted. Finding 08's own lesson ("use an index the site publishes") applies here, and the index was there.
- **Extraction [0]:**
  - GC value types are not opaque. The package declares them (§5).
  - GC does have a `ConnectionStatus` command in the package. Per the GC sheet (page 5) it is driven by `/api/RecordStatus`.
  - ControlScript never calls `WriteDeviceResponseStatus`; only GC does (gc:927–939).
  - `ISORecordStatus`'s response shape is attested by `GetAllStatus` api_call_3. It is not "inferred by analogy".
- **Extraction [1]:**
  - The quoted request bodies it lists come from the Extron driver. The Crestron module's value types were opaque at this stage; §10 reads them from the library.
  - `CopyFiles`, `RecordingSpaceAvail` and `PauseRecord` are documented, so the Copy, Storage and Pause joins do map to documented calls by name.
  - All 10 PTZ joins go through the Debounce symbol (SmC=50, 10 in / 10 out, 0.5 s, cmc:2073–2105), not 7 of 8.
  - `Camera_Count` cannot come from `CameraStatus`, which returns only `address`. Its source is opaque.
- **Finding 08:155 ("driver right, doc wrong").** The doc is internally inconsistent, not simply wrong: its examples agree with the driver's strings. The string-typed set is also 10 fields, not 3.

## 2. Matrix (one row per call, union of all sources)

Legend:
- **Y**: implemented; the wire string is in the source.
- **J**: a join exists; the wire bytes are opaque (the `.csp` is absent).
- **?**: opaque.
- **—**: not implemented. For Extron this is not found by a full read of the script. For Crestron it is not found among the module's 263 input/output cues.
- **Docs**: *undated* means no changelog entry names the call. *TOC-only* means the page is in the site TOC but not in the harvest.
- **Native** applies to VX2 hardware only. When this table was made the join map had not been found, so cells are **?** unless the release notes give indirect evidence. §9 now fills this column from the device database.

| # | Call (URI) | Docs (firmware) | GC | CS | Crestron module | Native IP ID |
|---|---|---|---|---|---|---|
| 1 | get-token (`/get-token`) | Y, initial 2022-08-15; URI corrected 2023-01-05 | Y | Y | J `Login`/`PersistentLogin` | n/a (IP table) |
| 2 | StartAutoSwitch | Y undated | Y | Y | J | ? |
| 3 | StopAutoSwitch (page `StopAutoSwitch.htm`) | Y undated | Y | Y | J | ? |
| 4 | AutoSwitchStatus | Y undated | Y | Y | J | ? |
| 5 | StartRecord | Y undated | Y | Y | J | ? |
| 6 | StopRecord | Y undated | Y | Y | J | ? |
| 7 | **PauseRecord** | Y undated, **TOC-only** | — | — | J `Pause_Recording` | ? |
| 8 | RecordStatus | Y undated | Y | Y | J (+`Recording_State` 0/1/2) | ? |
| 9 | StartISORecord | **no page** (404) | Y | Y | J | ? |
| 10 | StopISORecord | **no page** (404) | Y | Y | J | ? |
| 11 | ISORecordStatus | **no page**; `GetAllStatus` example only | Y | Y | J | ? |
| 12 | StartStream | Y undated | Y | Y | J | ? |
| 13 | StopStream | Y undated | Y | Y | J | ? |
| 14 | StreamStatus | Y undated | Y | Y | J | ? |
| 15 | StartOutput | Y undated | Y | Y | J | ? |
| 16 | StopOutput | Y undated | Y | Y | J | ? |
| 17 | OutputStatus | Y undated | Y | Y | J | ? |
| 18 | Sleep | Y undated | Y | Y | J | ? |
| 19 | Wake | Y undated | Y | Y | J | ? |
| 20 | ManualSwitchCamera | Y; 1–255 since 2023-12-28 | Y | Y | J (1–8) | ? |
| 21 | CameraStatus | Y; 1–255 note | Y | Y | J | ? |
| 22 | GoHome | Y undated | Y | Y | J | ? |
| 23 | CallCameraPreset | Y; 1–255 | Y | Y | J live/selected (1–8) | ? |
| 24 | SaveCameraPreset | Y 5.8 (2023-01-09) | Y | Y | — | ? |
| 25 | ImportCameraPresets | Y undated | — | — | — | ? |
| 26 | **ExportCameraPresets** | Y undated, **TOC-only** | — | — | — | ? |
| 27 | StartPT | Y 5.8 | Y | Y | J (8 directions) | ? |
| 28 | StopPT | Y 5.8 | Y | Y | J (stop-on-release inferred) | ? |
| 29 | StartZ | Y 5.8 | Y | Y | J | ? |
| 30 | StopZ | Y 5.8 | Y | Y | J | ? |
| 31 | GetCameras | Y; "updated" 5.8 | — | — | ? (`Camera_Count` output only) | ? |
| 32 | ChangeLayout | Y undated (A–Z) | Y A–Z | Y A–Z | J A–Y | ? |
| 33 | LayoutStatus | Y undated | — | — | J `Get_Current_Layout` | ? |
| 34 | GetLayouts | Y undated | — | — | J `Get_Layouts` | ? |
| 35 | ChangeRoomConfiguration (page `ChangeRoomConfig-API.htm`) | Y undated | Y | Y | J | ? |
| 36 | ForceChangeRoomConfig | Y undated | Y | Y | J (sheet describes a client-side sequence; endpoint opaque) | ? |
| 37 | RoomConfigStatus | Y undated | Y | Y | J | ? |
| 38 | GetRoomConfigs | Y undated | — | — | J | ? |
| 39 | GoToScenario | Y 5.8 | Y | Y | J (1–10) | inferred ([AVX-2194..2196]) |
| 40 | ScenarioStatus | Y 5.8 | Y | Y | ? (`Current_Scenario` output, no input join) | ? |
| 41 | GetScenarios | Y 5.8 | — | — | J | ? |
| 42 | ShotStatus | Y 5.8 | — | — | — | ? |
| 43 | GetActiveTalkers | Y 6.3 (2024-08-15); live, not in TOC | — | — | — | inferred (6.3.0.29 "Requires DB v200.365.004") |
| 44 | CopyFiles | Y undated | — | — | J (all 3 parameter names match) | ? |
| 45 | CopyStatus | **no page**; `GetAllStatus` example only | — | — | J `Get_Copy_Files_Status` | ? |
| 46 | RecordingSpaceAvail | Y undated | — | — | J `Get_Storage_Space_Available` | ? |
| 47 | **StorageSpaceAvail** | Y undated, **TOC-only** | — | — | ? | ? |
| 48 | GetAllStatus | Y 5.8 | — | — | ? (sheet: login "will poll… current status") | ? |
| 49 | Macro | Y 5.8 | — | — | — | ? |
| 50 | Restart | Y 5.8 | — | — | — | ? |
| 51 | **HealthStatus** (page `Health-Status-API.htm`) | Y undated, **TOC-only** | — | — | — | ? |
| 52 | **CloseWirecast** | Y undated, **TOC-only** | — | — | — | ? |
| 53 | CallPlugin | page in TOC; support removed 6.4.1 (2025-05-09) | — | — | J (3 slots, 3 arguments) | ? |

Totals against the 49 documented calls: **GC 30, CS 30, Crestron 36 (J) plus 4 opaque (?), native: 2 inferred, the rest opaque.**

**Update (§10).** The decompiled library replaces the Crestron column's J and ? with what it sends. It posts to 42 URIs: **38 of the 49 documented calls** plus the four names with no page (rows 9–11 and 45). Every J row is a Y. Of the ? rows, 31 GetCameras and 40 ScenarioStatus are Y, and 47 StorageSpaceAvail and 48 GetAllStatus are —: neither build requests them. Rows 27–30 go out as `/api/StartPt`, `/api/StopPt`, `/api/StartZ` and `/api/StopZ` (X36).

## 3. Request and response comparison (every call at least one driver implements)

**Common to all Extron calls.** Every call goes to `https://host:4443/` + URI (gc:867/913, cs:29) as a POST with `Content-Type: application/json`.
- Status calls and no-body commands send no body; Python sends `Content-Length: 0`, the same as the docs' `--data ""`.
- A reply counts as an error only if `status == 'Error'`, in which case the driver reads `err`.
- Only `TypeError` is caught, so a non-JSON reply, or an `Error` reply without an `err` key, raises out of the handler (gc:842–855, cs:409–418).

**Command calls with a body**

| Call | Docs (prose type; example) | GC sends | CS sends (per its sheet) | Crestron |
|---|---|---|---|---|
| GoToScenario | `id` Integer; example `"1"` | `{"id": str(value)}`; value is Decimal ≥1 (gc:625–628) | `{"id": str(value)}`; value must be numeric (cs:300) | `Recall_Scenario` analog. **§10: `{"id":3}`, a number**, no upper bound |
| ChangeRoomConfiguration / ForceChangeRoomConfig | `id` Integer 1–99; example `"16"` | `{"id":"5"}`, a string (Enum states `'1'…'99'`) | string per sheet (`'1'`–`'99'`); an int if the caller passes one | analog. **§10: `{"id":5}`, a number**; Change refuses above 99 or while AutoSwitch runs |
| ManualSwitchCamera | `address` Integer 1–255; example `"4"` (the Macro example uses `2`) | string (Enum `'1'…'255'`) | string per sheet | analog. **§10: `{"address":"4","id":0}`**: a string, plus an `id` of 0 on every call; ≤255 |
| CallCameraPreset / SaveCameraPreset | `cam`, `pre` Integer 1–255; example `"4"`,`"47"` | strings (Enum) | strings per sheet | Call only: `Call_Live_`/`Call_Selected_Camera_Preset`. **§10: `{"cam":"1","pre":"4"}`, strings** |
| StartPT | `cam` Integer 1–255, `ptDir` Integer 0–7; examples quoted | `{"cam": <number>, "ptDir": "0".."7"}` (gc:476–500) | same (cs:216–240) | 8 direction joins through Debounce. **§10: `/api/StartPt` `{"cam":1,"ptDir":5,"zDir":0}`, all numbers** |
| StopPT / StopZ | `cam` Integer; example `"1"` | `{"cam": <number>}` | same | release of the direction join (inferred). **§10: `/api/StopPt`, `/api/StopZ` `{"cam":1,"ptDir":0,"zDir":0}`** |
| StartZ | `cam`, `zDir` 0=In / 1=Out | `{"cam": <number>, "zDir": "0"/"1"}` | same | `Camera_Zoom_In`/`Out`. **§10: `{"cam":1,"ptDir":0,"zDir":1}`, all numbers** |
| ChangeLayout | `id` **String** A–Z | `{"id":"A".."Z"}`; matches the docs | same | A–Y only (joins). **§10: `{"id":"A"}`…`"Z"`**; the library takes 1–26 |
| CopyFiles | `destination`, `logDestination` String, `deleteSource` Boolean | — | — | `Copy_Files_Destination$`, `Copy_Log_Destination$`, `Delete_Source_File` (analog 0/1). **§10: `{"destination":"…","logDestination":"…","deleteSource":false}`** |
| CallPlugin | `name`, `arg1`, `arg2` String | — | — | `Plugin_<n>_Name$` + `Plugin_Arg1$`/`2$`/`3$` (3 arguments). **§10: `{"name":"…","arg1":"…","arg2":"…","arg3":"…"}`** |

No-body commands match the docs in both Extron drivers, and the Crestron module has joins for them: Start/Stop AutoSwitch, Record, Stream, Output and ISO, plus Sleep, Wake and GoHome. GC additionally writes an optimistic "Emulated" status before sending; ControlScript does not. `PauseRecord` is documented with no body; only Crestron wires it.

**Status calls**

| Call | Docs response | Extron parse | Crestron output |
|---|---|---|---|
| AutoSwitch / Record / Stream / Output / ISORecordStatus | `results` true/false (ISO: `GetAllStatus` api_call_3 only) | `results` maps to On/Off or Start/Stop; also accepts `'true'`/`'false'`; matches the docs | `*_Started_FB` / `*_Stopped_FB`; Record also has `Recording_State` 0/1/2 and `Pause_Enabled_FB`, and no documented field carries "paused" |
| RoomConfigStatus | page: `roomConfigs:[{"id":"[1-99]",...}]`; `GetAllStatus`: `roomConfig:{"id":1}` | `str(res['roomConfigs'][0]['id'])`; catches KeyError, IndexError, AttributeError | `Change_Room_Config_FB` |
| ScenarioStatus | `scenario:{"id":[value] (unquoted), "name"}` | `str(res['scenario']['id'])`; catches **ValueError, IndexError, AttributeError only**; KeyError and TypeError escape (gc:650, cs:318) | `Current_Scenario`; source opaque |
| CameraStatus | page: `"address":"[value]"`; `GetAllStatus`: `"address":1, "addresses":[1]` | `int(value)` range check, then writes the **raw** value (gc:771–773, cs:374–376) | `Manual_Switch_Camera_FB` |
| get-token | `{"status":"OK","token":[token]}`; error `"Incorrect Username or Password"` | stores `res['token']`; if the key is missing, retries immediately with no limit | `Login_FB` |
| LayoutStatus, GetLayouts, GetRoomConfigs, GetScenarios, RecordingSpaceAvail, CopyStatus | documented (CopyStatus by example only) | not called | `Change_Layout_<x>_FB`, the name lists, `Storage_Space_*_GB`, `Copy_Files_In_Progress` |

## 4. Discrepancies

| ID | Category | Severity | Summary |
|---|---|---|---|
| X01 | docs-internal | cosmetic | The site's TOC lists 48 pages. The harvest has 43; 5 are TOC-only (PauseRecord, ExportCameraPresets, HealthStatus, StorageSpaceAvail, CloseWirecast). GetActiveTalkers is live but not in the TOC. Coverage numbers in the repo are low by 5 or 6. |
| X02 | documented-unimplemented | functional-gap | PauseRecord is documented. GC and CS omit it; Crestron has `Pause_Recording` (wire opaque). |
| X03 | documented-unimplemented | functional-gap | GetActiveTalkers and ShotStatus are in no driver. The VX2 native symbol probably has active talkers. |
| X04 | documented-unimplemented | functional-gap | Extron has no layout feedback (LayoutStatus) and no name lists (GetLayouts, GetRoomConfigs, GetScenarios); Crestron has all four. |
| X05 | documented-unimplemented | functional-gap | Crestron has no SaveCameraPreset join; both Extron drivers have it. |
| X06 | documented-unimplemented | functional-gap | HealthStatus, StorageSpaceAvail, RecordingSpaceAvail, CopyFiles, Import/ExportCameraPresets, GetCameras, GetAllStatus, Macro, Restart and CloseWirecast are absent from Extron. Crestron has only the Copy and Storage ones. |
| X07 | sends-undocumented | unknown | Both Extron drivers and Crestron use StartISORecord, StopISORecord and ISORecordStatus. None has a page (not in the TOC; 404 for 6 name variants). ISORecordStatus appears in the GetAllStatus example. Extron cites pages 26, 28 and 30 of a 2023-12-28 PDF for them. The feature still existed in 6.4.0 [AVX-2735]. |
| X08 | sends-undocumented | unknown | Crestron's `Get_Copy_Files_Status` implies CopyStatus, which is attested only in GetAllStatus's example (`copy_underway`). |
| X09 | sends-undocumented | unknown | Crestron's `Recording_State`=2 (Paused) and `Pause_Enabled_FB` need a pause state and a pause-enabled flag that no documented response carries. |
| X10 | value-domain-mismatch | unknown | Crestron's CallPlugin passes 3 arguments; the page defines 2. Support was removed in 6.4.1 by both the changelog and [AVX-2996], but the page is still in the TOC. |
| X12a | value-domain-mismatch | unknown | GoToScenario `id`: Extron sends `str(value)`; the docs' prose says Integer (H6). |
| X12b | value-domain-mismatch | unknown | StartPT and StartZ: `ptDir`/`zDir` are strings but `cam` is a number in the same body; the docs' prose says Integer for both (H6). |
| X12c | value-domain-mismatch | unknown | ChangeRoomConfiguration and ForceChangeRoomConfig `id`, ManualSwitchCamera `address`, and Call/SaveCameraPreset `cam` and `pre` are strings in GC (package Enum) and in CS (per its sheet); the docs' prose says Integer. `cam` is a string here but a number in PT/Z. |
| X12d | docs-internal | cosmetic | The prose says Integer for 14 fields while every example quotes them. The Macro example is unquoted (`"address": 2`). Several examples are malformed. |
| X13 | value-domain-mismatch | unknown | GC's Decimal parameters (Scenario; PanTilt and Zoom `Camera`) have an opaque runtime type. A float would put `"3.0"` or `1.0` on the wire; `decimal.Decimal` would make `json.dumps` raise. |
| X14 | docs-internal | unknown | RoomConfigStatus is a list on its page and a singular object in GetAllStatus. Both Extron drivers index `roomConfigs[0]`. |
| X15 | docs-internal | unknown | LayoutStatus is a list on its page and an object in GetAllStatus. This affects Crestron's `Get_Current_Layout`. |
| X16 | value-domain-mismatch | unknown | CameraStatus `address` is a string on its page and an int (plus `addresses[]`) in GetAllStatus. Extron writes the raw value into an Enum `'1'…'255'` status (GC) or a string-documented status (CS). |
| X17 | value-domain-mismatch | unknown | Both Extron ScenarioStatus handlers let KeyError and TypeError escape when `scenario` is missing or null. |
| X18 | value-domain-mismatch | cosmetic | StopPT and StopZ document a lowercase `"error"` with a `message` key. Extron checks for `'Error'`/`err`, so those failures pass silently; an `Error` reply without `err` raises. |
| X19 | extron-vs-crestron | fails-on-device | The Crestron default is HTTP on 3579 (`Request_Type` DV=0d); Extron uses HTTPS on 4443. Per [AVX-2994], new 6.4.1.8+ installations do not support legacy mode. |
| X20 | extron-vs-crestron | functional-gap | Camera range: Crestron 1–8; docs and Extron 1–255. |
| X21 | extron-vs-crestron | functional-gap | Layouts: Crestron A–Y (25 joins); docs and Extron A–Z. |
| X22 | extron-vs-crestron | functional-gap | Scenarios: Crestron 1–10 (recall and names); docs have no maximum; GC minimum 1, no maximum. |
| X23 | extron-vs-crestron | unknown | Force room config: the Crestron sheet describes a client-side stop/change/restart sequence, while Extron calls `api/ForceChangeRoomConfig`. |
| X24 | extron-vs-crestron | unknown | Re-login: Crestron retries 5 times, then waits 5 minutes, then stops. Extron re-logs in on every connect and retries a missing token immediately with no limit; in CS that retry is direct recursion (cs:73). |
| X25 | gc-vs-controlscript | fails-on-device | The CS sheet's `Set('Scenario', None, {'ID':'String'})` raises TypeError (cs:300). The stale `'Parameters':['ID']` is at cs:47. GC is correct. |
| X26 | gc-vs-controlscript | functional-gap | An unauthenticated Set: CS re-requests a token (cs:458–460); GC only discards the command (gc:903–904). |
| X27 | gc-vs-controlscript | cosmetic | ConnectionStatus: GC derives it from RecordStatus via the base class (HTTPError still counts as 'Good'); CS uses a 15-miss watchdog over every Update. |
| X28 | gc-vs-controlscript | cosmetic | GC writes optimistic Emulated status for 7 commands; CS writes none. GC's Scenario Emulated value (Decimal) never equals its Live value (str). |
| X29 | gc-vs-controlscript | cosmetic | Only GC has the SSL-off platform gate and CommandPacing. ResponseTimeout is unused in both; the real timeout is a literal 10 s. |
| X30 | gc-vs-controlscript | unknown | GC builds its URL with `RootURL.replace('http','https',1)`. A base URL that is already `https://` would become `httpss://`. |
| X31 | docs-internal | cosmetic | Currency notes disagree: 6.4.1.8 vs 6.02 vs changelog 6.4.2. The release note history dates 6.4.0.49 as 2024-03-19, after 6.3.0.34 (2024-11-07) in the list. |
| X32 | docs-internal | cosmetic | Scheme and port history: HTTPS references were "corrected" to HTTP in 2022, then everything moved to 4443 in 2025. The Make-API-Calls example still uses `http://`. The release notes still mention "4443 or 3579". |
| X33 | docs-internal | cosmetic | Page and GetAllStatus examples disagree: message text, GetCameras entry shape (`{id,name,ip}` vs `{id,model}`), quoted vs int GB values. HealthStatus uses `"status":"Healthy"`. GetActiveTalkers `talkers` is the string `"[5,]"`. OutputStatus and StopOutput document no error. |
| X34 | docs-internal | unknown | [AVX-2995/2997] applied permissions to API commands; the permission-error shape is undocumented. Extron keeps `Authenticated` after an HTTP error. |
| X35 | docs-internal | cosmetic | GoToScenario's success example documents `cameras:[[1-8]]` while camera IDs go to 255. |

Full evidence (file:line and URL) for each is in `discrepancies.json`, with the verifier's verdict.

## 5. Details worth knowing

**GC parameter types, read from the package.** `surfaces.py params` runs `tools/pkp_asset.CommandGraph` over `samples/Automate VX/pkp/1bynd_42_4279_v1_0_11.pkp`, and `test_surfaces.py` pins the result.
- **Enum (string states):** RoomConfiguration and ForceRoomConfiguration (`'1'…'99'`); CameraPresetRecall and CameraPresetSave `Camera` and `Value` (`'1'…'255'`); SwitchCamera (`'1'…'255'`); Layout (`'A'…'Z'`).
- **Decimal:** PanTilt and Zoom `Camera` (min 1, max 255); Scenario `Value` (min 1, **no maximum**).
- The package also carries a `ConnectionStatus` command (Connected/Disconnected).
- That Enum values arrive at the script as the state strings is consistent with the script's `int(value)` casts; live test LT17 confirms it on a processor.

**The ISO-record family.** Removal from the docs is not proof the API is deprecated.
- The site TOC (built 2026-05-26) has no ISO page. I probed 6 URL variants on 2026-09-24 and all returned 404.
- Extron's GC comments cite pages 26, 28 and 30 of "Automate API - 2023-12-28.pdf", so the family was documented in that edition. That PDF is not in the repo.
- Release notes: "[AVX-2735] ISO recording and Enable Pause are now mutually exclusive" (6.4.0.49), so ISO recording is still a product feature.
- This adds to ROADMAP R33, which found nothing either way.

**Pause.** `PauseRecord` is documented (no body; success "Record Paused Successfully"). No `ResumeRecord` page was found: 16 pause and resume variants were probed. Release note [AVX-2844] mentions resuming a paused recording, and the documented `RecordStatus` has no field for the paused state.

**Native IP ID in more detail.**
- "Added native symbol support for VX2. Requires DB version 200.355.002.00" (release notes page 11, 6.2.2.27).
- "No native symbol support in this release. Use Crestron Module for control." (page 12, 6.2.1.18).
- The IP Table page gives the IP ID, port 41794 by default, and an optional SSL setting with username and password.
- The release notes show a join model: [AVX-2238] "update all control system joins", [AVX-2902] "VX2 symbol no longer allows values above the max support (99)", [AVX-2194..2196] scenario calls via the "VX2 hardware definition", and [AVX-2809] multiple control systems.
- The VX2 spec page lists only "System Control: REST API".
- The join names and numbers were **not found** by the VX2 manual's published TOC or by WebSearch. The Crestron device database (SIMPL Windows) is the likely holder.
- Neither Extron driver speaks CIP. An Extron controller could not use this path without a CIP client. The same limit bears on the second goal of driving a DM-MD32x32 through an Extron processor.

**Robustness (both Extron drivers, identical).**
- A missing token retries forever. In ControlScript the retry is recursion (cs:73), so a device that keeps answering 200 without a token would end in `RecursionError`.
- `__CheckResponseForErrors` catches only `TypeError`.
- ScenarioStatus does not catch `KeyError`.
- The ControlScript `Scenario` qualifier is stale.

## 6. Method
- **Sources read in full:** the GC embedded script (1,166 lines; `surfaces.py extract` writes it to `1bynd_42_4279.embedded.py`, git-ignored), the ControlScript module (640 lines), both Extron sheets, and the Crestron sheet.
- **Crestron module:** the `.cmc` cue list and the Debounce and Dp blocks.
- **Docs:** harvested pages under `reference/automate-vx-api/`, plus live pages. I spot-checked GoToScenario, RoomConfigStatus, CameraStatus, GetAllStatus and CallPlugin, and fetched the 5 TOC-only pages new.
- **Site index:** `Data/HelpSystem.xml` and the TOC chunk.
- **Name probe:** 96 names × 2 URL shapes. Results are in `probe_results.txt`; `surfaces.py probe` repeats it.
- **Release notes:** https://www.crestron.com/release_notes/automate_vx_6.4.1.8_release_notes.pdf.
- **VX2 manual:** the IP Table and spec pages at docs.crestron.com/en-us/9488 and its TOC.
- **URI sets:** GC and CS compared with `sort -u` and `diff` (33 each, identical).
- `surfaces.py` repeats every offline measurement and the live TOC comparison; `test_surfaces.py` pins the offline ones.
- **Evidence shorthand:** `gc:N` is the extracted GC script, `cs:N` is `samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py`, `cmc:N` is `samples/Automate VX/Crestron Module/1Beyond Automate_VX_v1.2.cmc`, and doc pages are `reference/automate-vx-api/API-Reference/<Name>-API.md` or `https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/API-Reference/<Page>.htm`.
- **Limits:**
  - The Crestron wire format is read from the decompiled library (§10), not observed on a wire.
  - The TOC is the site's own index but may still omit live pages; GetActiveTalkers shows that it does.
  - No live unit was reached.

## 7. Live tests
See `LIVE_TESTS.md`. Each test names the discrepancy it settles. Tests marked disruptive (Restart, SaveCameraPreset, CloseWirecast, ExportCameraPresets) should run only on a unit where that is acceptable. LT17 needs a processor and a PC, not an Automate VX.

## 8. The Crestron module's source, from the installed device database (second pass, 2026-09-24)

The owner pointed at the Crestron device database installed on the workstation
(`<CRESDB>` = `C:\Program Files (x86)\Crestron\Cresdb`). `crestron_module.py` reads it;
`test_surfaces.py` pins what follows.

**Where the logic is.**
- `<CRESDB>/Modules/` holds the module in three versions, `1Beyond Automate_VX_v1.0/1.1/1.2.cmc`.
- `<CRESDB>/Modules/crssplus.dat` is a ZIP of SIMPL+ sources: 3,526 entries, none encrypted. It holds `1Beyond Automate_VX_v1.x.csp` and `.csh` for each version, and two SIMPL# libraries, `Automate_VX.clz` (3-Series) and `Automate_Vx_4Series.clz`. The v1.2 files and both libraries are dated 2026-03-23.
- Two sibling stores, `crsprtct.dat` and `CrsNoImp.dat`, have encrypted entries. They were not opened.

**The `.csp` is plain SIMPL+ source, and it is only a wrapper.**
- It declares the 102 signals the `.cmc` shows.
- Every command input calls a method on the library's `AutomateVx` class (`AutomateVx4Series` on a 4-Series processor).
- It contains no URL, no URI and no request body.
- The wire bytes are therefore built in the compiled library. This pass did not read them; §10 does. *Correction:* this line first said that decompiling a `.clz` is what Crestron's development-tools licence bars. That was wrong. The clause finding 04 records is in the licence for Crestron's development *tools*, and no term covering this distributed library was found (§10, licence note).
- The 3-Series library carries its own XML documentation, which is readable and names and describes each method. The 4-Series library ships a `.pdb` instead, which was not read.

**What the source settles**

| ID | Before | Now |
|---|---|---|
| X19 | HTTP default, from the `.cmc` parameter cue | **Confirmed at source:** `Request_Type` defaults to 0, and `main()` sets `Automate.IsHttps = Request_Type`. If the `Port` analog is 0, the library's own default port applies (§10: 3579 for HTTP, 4443 for HTTPS). |
| X20 | Crestron cameras 1–8 | **The wrapper does not cap cameras.** `CameraCount 8` appears only in commented-out code, and `Manual_Switch_Camera` forwards any analog value. The 1–8 figure is the help sheet's. §10: the library allows up to 255, except the live-preset call, which still stops at 8. |
| X21 | Layouts A–Y | **The limit is the wrapper's.** `LayoutCount 25` gives 25 layout joins, while the library documents `ChangeLayout` as "Valid Values A-Z". Z is unreachable only because there is no join for it. |
| X22 | Scenarios 1–10 | **Recall is not capped.** `Recall_Scenario` forwards any value; `ScenarioCount 10` bounds only the name outputs. |
| X23 | Force room config: a client-side sequence per the sheet | **One library call.** The library documents it as stopping autoswitching and forcing the change, which is consistent with the documented `ForceChangeRoomConfig` API. §10: it is one request, `POST /api/ForceChangeRoomConfig`. |
| X24 | Re-login | **The library caches a token per device IP in a file on the processor.** 1.5 s after an IP address arrives it checks for a stored token, and logs in (credentials Base64-encoded) only if none is found. `PersistentLogin` is new in v1.2. |
| X09 | `Recording_State` 2 (paused) | The state arrives from the library as a (status, state) pair. §10: it reads `record_state` and `pause_enabled` from the RecordStatus reply, two fields no documented response carries, and sets "paused" itself after a successful PauseRecord. |
| X10 | `CallPlugin` with 3 arguments | **Confirmed at source:** three argument properties. |

**New from the library's documentation.** `ChangeRoomConfig`, `ManualSwitchCamera` and `SetCameraPreset` are documented to raise an error while AutoSwitch is enabled. Neither Extron driver treats that case specially: it sends the request and reports the device's error. LT16 checks it.

**Versions.** v1.1 added the room-configuration name outputs (up to 99); v1.2 added `PersistentLogin`. Nothing else changed in the wrapper.

**What stayed opaque at this pass** (the requests themselves: URIs, body keys and value types, plus the default port, error handling and polling cadence) is read from the decompiled library in §10.

## 9. Native IP ID: the IV-SAM-VX2 symbol, from the installed device database (second pass, 2026-09-24)

The VX2's native control surface is the SIMPL device `IV-SAM-VX2` in `<CRESDB>/Programming/iodev.tio`
(Code 19868) and `symlib.tio`. It has a main symbol (Code 20126, 39 named joins) and eight child
symbols: System, Layouts, Room Configs, Config Names, Camera Names, Scenarios, Scenario Names and
Advanced Settings. **In all, 276 named joins.** An older `IV-SAM-VX2 (Deprecated)` set sits beside
it. `experiments/dm_md/crestron_symbols.py` reads these files, and `test_crestron_symbols.py` pins
the numbers below.

(D = digital, A = analog, S = serial; i = input, o = output.)

*Corrected 2026-09-24 (third pass).* This table first counted each bare `[~UNUSED~]` cue in the
symbol as a join. It is a spacer between groups and takes no number, so every join after one was
too high (by up to 3 here). The rule was established on the DM-MD switcher's symbol against
Crestron's compiled library (`experiments/dm_md/DECOMPILE.md` §3). Here it is applied to the VX2
symbol, whose own control code was not decompiled.

| API call(s) | Native join(s) |
|---|---|
| Wake, Sleep | Di1 `Wake`, Di2 `Sleep` |
| Start/Stop AutoSwitch, AutoSwitchStatus | Di4–6 start/stop/toggle; Do4 `Autoswitch_F`, Do34 `Autoswitch_Starting_F` |
| Start/Stop Output, OutputStatus | Di7–9; Do7 `Output_F` |
| Start/Stop/Pause Record, RecordStatus | Ai31 `Recording` / Ao31 `Recording_F`. It is an analog, so its values are not in the symbol. |
| Start/Stop Stream, StreamStatus | Ai32 `Streaming` / Ao32 `Streaming_F` (analog, as above) |
| ManualSwitchCamera | Di10 `Manual_Switch_Camera` with Ai23 `Camera_Select` |
| StartPT/StopPT, StartZ/StopZ | Di11–18 (eight directions, in the same order as the documented `ptDir` 0–7), Di19–20 zoom in/out |
| CallCameraPreset, SaveCameraPreset | Di21 `Recall_Camera_Preset`, Di22 `Save_Camera_Preset`, Ai24 `Camera_Preset` (camera from Ai23) |
| ChangeLayout, LayoutStatus, GetLayouts | Ai28 `Layout` / Ao28 `Layout_F`; Layouts child: `Layout_Count` and `Layout_A_Name_F`–`Layout_Y_Name_F` (25 names) |
| ChangeRoomConfiguration, RoomConfigStatus, GetRoomConfigs | Ai29 / Ao29; Config Names child: `Room_Config_Count` and 99 names |
| GoToScenario, ScenarioStatus, GetScenarios | Ai30 / Ao30; Scenario Names child: `Scenario_Count` and 99 names |
| GetActiveTalkers | Ao26–27 `Active_Talker_1_F`, `Active_Talker_2_F` |
| HealthStatus, Restart, storage | System child: `Health_Status_F`, Di1 `Reboot`, `Total_Storage`, `Available_Storage` |
| CopyFiles, CopyStatus | Advanced Settings child: `Copy_Files`, `Delete_Files_After_Copy`, `Copy_Files_Location`, `Log_Destination`, `Copy_Files_Success_F` |
| GetCameras | Camera Names child: `Camera_Count` only, no names |
| (none) | Advanced Settings `PTZ_Correction`, which no API page documents; `Error_Message_F` (So33) |
| Not native | ISO recording, GoHome, CameraStatus (no active-camera feedback), ShotStatus, Macro, CallPlugin, Import/ExportCameraPresets, ForceChangeRoomConfig, CloseWirecast |

**Findings**
- **The native symbol is the richest of the three control surfaces.** It is the only one with active talkers and health status. It also has Save preset, which the SIMPL module lacks, and the name lists and storage, which Extron lacks.
- **Its layout names stop at Y,** as in the SIMPL module.
- **ISO recording is absent here too,** which fits the ISO calls' missing documentation (X07).
- **Using it needs a Crestron control system.** The VX2 registers to one over CIP. For an Extron processor it is the same barrier as the DM-MD's native path (`experiments/dm_md/DESIGN.md` §1.4), so the REST API remains the practical route. The native join map fills the matrix's **Native IP ID** column, which reads `?` in §2.

**The two demo programs in Downloads** (`intelligent_switching_microphone_integration_demo_v5`, `1_beyond_multi-cam_demo_v1.2`) use neither the VX2 symbol nor any DigitalMedia device.
- The first drives 1 Beyond cameras through a compiled SIMPL# library (`ISMIv2`, class `OneBeyondCamera`, addressed by IP and a camera ID of 1–5).
- The second is a VISCA-over-IP module for 1 Beyond cameras, built from plain SIMPL+ helpers. It is an independent source of VISCA strings for the i20 driver to be checked against (ROADMAP R45).

## 10. The Crestron library's requests, decompiled (third pass, 2026-09-24)

The owner decided the module's SIMPL# library may be decompiled for interoperability, and ran the
decompiler; I read its output. `experiments/crestron_decompile/decompile.py` repeats the run. This
section **supersedes §8's "stays opaque"** and corrects §8's licence line (note at the end).

**Inputs.** Both builds come from `<CRESDB>/Modules/crssplus.dat`, dated 2026-03-23.

| assembly | package | SHA-256 |
|---|---|---|
| `Automate_VX.dll` (3-Series) | `Automate_VX.clz` | `ac6bbcfda23e1be4463bed93aa3145da1e243305c1a3e0157a2850c4185ecdf2` |
| `Automate_Vx_4Series.dll` | `Automate_Vx_4Series.clz` | `a7ad416a65dc967d224da90079e7898d1602509fa49641860e2f1b4fd079b55f` |

**Method.**
- ILSpy's `ilspycmd` 11.1.0.9782 decompiled each build to C#, and disassembled each to IL.
- The C# view could not decode the `[JsonProperty]` arguments, because they carry an enum from Crestron's own Newtonsoft build. The JSON key names therefore come from the attribute blobs in the IL.
- `lib:<file>:<line>` cites the decompiled 3-Series project. The 4-Series build was compared by URI set, model classes, JSON keys and HTTP client: the 11 model classes are identical, the API keys match in name, order and null handling, and the only difference is how the token-file class is laid out.
- This section describes formats. It does not reproduce the library's source.

### 10.1 Transport (settles X19)
- **Base URL.** `https://<ip>:<port>` when `IsHttps` is 1, `http://<ip>:<port>` when it is 0. The port is the `Port` parameter when that is above 0, else **4443 for HTTPS and 3579 for HTTP** (lib:AutomateVx.cs:970–996; the same values are the `AutomateConstants` fields, which the compiler inlined). At the module's defaults, then, the library posts to `http://<ip>:3579` — X19, confirmed end to end.
- **Method and headers.** Every call is a POST: Crestron's request type 1 on the 3-Series build (the enum is defined outside the library, INF), `HttpMethod.Post` on the 4-Series. `Content-Type` is `application/json`. An empty body goes out with `Content-Length: 0` (lib:Https.cs:87–104). Bodies are compact JSON written by Newtonsoft.
- **TLS.** Both builds switch certificate checking off, so the unit's self-signed certificate is accepted: `HostVerification`/`PeerVerification = false` on the 3-Series (lib:Https.cs:31–38), a no-check `CertificatePolicy` on the 4-Series.
- **Clients.** The 3-Series client sets `KeepAlive` false, `User-Agent: crestron` and `Accept: application/json`. The 4-Series one is .NET `HttpClient`, with `Connection: close` and a 3-hour timeout.
- **Replies.**
  - HTTP 200 is parsed, 400 with a body is read for `err`, and 401 means "Unauthorized" (lib:Https.cs:220–265).
  - Inside a 200, only `status == "Error"` counts as an error — the same capital-E test as Extron's, so X18's lowercase `error` passes silently here too.

### 10.2 Authentication and session (settles X24; adds X37)
- **Login.** `/get-token` goes out with an empty body and `Base64(user:pass)` in `Authorization`.
- **Token cache.** The returned `token` is stored in `<app root>/user/1Beyond/AutomateVX.txt` on the processor, keyed by base URL. A stored token is reused without calling `/get-token` (lib:AutomateVx.cs:275–323).
- **The header's form depends on build and scheme (X37).**
  - The 3-Series HTTPS client sends `Authorization: Basic <value>`, for the credential and for the token alike (lib:Https.cs:94).
  - The 3-Series HTTP client and the 4-Series client send the bare value (lib:Http.cs:79), as Extron and the docs do.
- **Losing the session.**
  - On HTTP 401, or on the 4-Series client's synthetic code 666 (any transport exception), the library marks itself logged out (lib:AutomateVx.cs:1395–1424).
  - A 401's "Unauthorized" is mapped to "Incorrect Username or Password…", and that text deletes the cached token (lib:ErrorHandling.cs:44; lib:AutomateVx.cs:1436–1449). The next login therefore fetches a fresh token rather than replaying the old one.
  - With `PersistentLogin` set: up to 5 immediate re-logins, then a 5-minute wait. At most two 5-minute waits happen. Each one resets the counter, so each can be followed by another burst of up to 5 immediate re-logins.
- **Polling.**
  - After login it reads 15 statuses, 200 ms apart, once: AutoSwitch, Record, ISO, Stream and Output; the layout list and current layout; the room-config list and current configuration; the camera; Record again; recording space; copy status; cameras; scenarios (lib:AutomateVx.cs:1079–1110).
  - After a *fresh* token it also polls `CameraStatus` every 60 s as a keep-alive (lib:TimedEvents.cs). A token reused from the file does not start that clock (lib:AutomateVx.cs:290–300 against 1215–1231), so after a processor restart with a cached token there is no periodic poll.

### 10.3 Requests
**URIs.** Both builds post to the same 42 URIs (identical sets): `/get-token` and 41 under `/api/`. That is 38 of the 49 documented calls plus the four names with no page: `StartISORecord`, `StopISORecord`, `ISORecordStatus` and `CopyStatus`. Neither build requests `SaveCameraPreset`, `Import`/`ExportCameraPresets`, `ShotStatus`, `GetActiveTalkers`, `StorageSpaceAvail`, `GetAllStatus`, `Macro`, `Restart`, `HealthStatus` or `CloseWirecast`.

**Bodies.**
- Newtonsoft writes properties in declaration order.
- Every request and response key carries `NullValueHandling.Ignore`, so a null string is left out.
- An integer is never null, so it is always written, even by a call that does not set it. That is where X38's extra keys come from.

| call (URI as sent) | Crestron library sends | Extron sends | same? |
|---|---|---|---|
| GoToScenario | `{"id":3}` | `{"id":"3"}` | **no**: type (X12a) |
| ChangeRoomConfiguration, ForceChangeRoomConfig | `{"id":5}` | `{"id":"5"}` | **no**: type (X12c) |
| `StartPt` | `{"cam":1,"ptDir":5,"zDir":0}` | `StartPT` `{"cam":1,"ptDir":"5"}` | **no**: URI case (X36), `ptDir` type (X12b), extra `zDir` (X38) |
| `StopPt` | `{"cam":1,"ptDir":0,"zDir":0}` | `StopPT` `{"cam":1}` | **no**: URI case, extra keys |
| StartZ | `{"cam":1,"ptDir":0,"zDir":1}` | `{"cam":1,"zDir":"1"}` | **no**: `zDir` type, extra `ptDir` |
| StopZ | `{"cam":1,"ptDir":0,"zDir":0}` | `{"cam":1}` | **no**: extra keys |
| ManualSwitchCamera | `{"address":"4","id":0}` | `{"address":"4"}` | **no**: extra `id` (X38) |
| CallCameraPreset | `{"cam":"1","pre":"4"}` | `{"cam":"1","pre":"4"}` | yes |
| ChangeLayout | `{"id":"A"}` | `{"id":"A"}` | yes |
| CopyFiles | `{"destination":"…","logDestination":"…","deleteSource":false}` | not sent | — |
| CallPlugin | `{"name":"…","arg1":"…","arg2":"…","arg3":"…"}` | not sent | 3 arguments (X10) |
| every other call | empty body | empty body | yes |

(lib:AutomateVx.cs:489–548, 579–615, 617–700, 702–729.)

**Key names agree with Extron's and the docs'**, in the same case: `id`, `address`, `cam`, `pre`, `ptDir`, `zDir`, `destination`, `logDestination`, `deleteSource`, `name` and `arg1`–`arg3`.

**What the disagreements mean.** Two vendors' production drivers disagree on the JSON type of `GoToScenario.id`, the room-configuration `id`, `ptDir` and `zDir`; on the case of `StartPT`/`StopPT`; and on whether unused keys are sent.
- If both drivers work against the same firmware, the device parses those fields leniently, matches URIs case-insensitively and ignores extra keys. That is **inference, not measurement**: either driver could be broken on some firmware.
- One case needs watching: Crestron's zoom calls carry `"ptDir":0`, and 0 is Up.
- The docs' own split (X12d) lines up exactly: Crestron follows the prose (Integer), Extron follows the examples (quoted).
- LT2–LT4 and the new LT18–LT20 decide it on a unit.

### 10.4 Responses (settles X09, X15 and Crestron's side of X14)
- **One flat model** is read for every reply except GoToScenario's. Its keys, from the IL, in declaration order: `status`, `token`, `err`, `message`, `results`, `address` (int), `layout`, `roomConfig`, `pause_enabled`, `record_state`, `copy_underway`, `layouts`, `roomConfigs`, `available_gigabytes`, `total_gigabytes`, `return_code`, `std_out`, `std_err`, `cameras`, `scenarios`, `scenario`. A layout, room configuration or scenario is `{id,name}`; a camera is `{address,id,model,ip}`.
- **RoomConfigStatus (X14).** Crestron reads `roomConfig`, a single object: the `GetAllStatus` shape. Extron reads `roomConfigs[0]`: the page's list. The two drivers expect different shapes, so unless the device sends both, one of them never gets room-configuration feedback from this call (lib:RequestParsing.cs:384–393). After a Change or Force, Crestron also takes the current configuration from the first number in the reply's `message` (regex `\d+`, lines 349–383), which depends on message text no page defines.
- **LayoutStatus (X15).** Crestron reads `layout` as a single object (lines 329–341). The page documents a list. A list would fail to deserialize, and the library would log a JSON parsing error.
- **RecordStatus (X09).** Crestron reads `results`, `record_state` (0 stopped, 1 recording, 2 paused) and `pause_enabled` (lines 267–278). No documented response carries the last two. A successful PauseRecord also sets state 2 locally.
- **CopyStatus (X08)** reads `copy_underway`, as in `GetAllStatus`'s example.
- **GoToScenario (X35)** is read as `{status, message, cameras}`, with `cameras` a flat list of integers rather than the page's nested `[[1-8]]` (lines 88–99).
- **CameraStatus (X16)** reads `address` as an int. Json.NET's default conversion should accept `4` or `"4"`, so either documented form probably works for Crestron (inferred from the library's behaviour, not run).

### 10.5 Limits and guards
- **ChangeLayout** takes 1–26 and maps it to A–Z, with an error above 26. The wrapper's 25 joins are the only reason Z is unreachable (X21).
- **ManualSwitchCamera and CallCameraPreset** accept a camera and a preset up to 255. The "live" preset call, which uses the current camera, still refuses a camera above 8. All three guards report one shared message that still says "(1-8)", so a rejected camera 256 is reported with the wrong range (X20).
- **ChangeRoomConfiguration** refuses a configuration above 99. It reports that with the AutoSwitch error (code 4), and never uses its own out-of-range code 23 — a library defect. ForceChangeRoomConfig has no bound.
- **AutoSwitch guard.** Change room configuration, manual camera switch and preset recall refuse to send while AutoSwitch is on (errors 4–6). That is the case LT16 checks.
- **Login guard.** Most calls check that the library is logged in before sending. These do not: GoToScenario, the four pan/tilt/zoom calls, the live preset call, GetCameras, GetScenarios and ScenarioStatus. GetCameras and GetScenarios are part of the post-login status burst.
- **ForceChangeRoomConfig is a single POST** (X23): there is no client-side stop/change/restart sequence.

### 10.6 Licence note (corrects §8)
§8 said that decompiling a `.clz` is what Crestron's development-tools licence bars. That was wrong.
- The clause finding 04 records (§4.2(c), on reverse engineering and decompilation) is in Crestron's *Software Development Tools* licence, which governs the tools: SIMPL Windows and Toolbox.
- The only licence text this repo has read is that one. I found no term that governs this distributed module library and bars decompiling it.
- The owner, who works for a Crestron dealer/partner organisation, made the call to decompile it for interoperability.
- ROADMAP D2 still carries the licence question, and no legal conclusion is drawn here.
