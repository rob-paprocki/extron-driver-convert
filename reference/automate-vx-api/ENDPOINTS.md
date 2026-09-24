# Automate VX API — Endpoint Reference

Source: Crestron SDK documentation, `https://sdkcon78221.crestron.com/sdk/Automate-VX-API/Content/Topics/Automate-API/Home.htm` and its 32 API-Reference sub-pages (see `API-Reference/*.md`). Current as of the 6.4.1.8 firmware release per the Home page; the API-Reference index page itself states it is current as of firmware 6.02, so the two headline version numbers are inconsistent in the source (both cited verbatim, not reconciled by this document).

Global facts, true for every endpoint below unless noted:
- **Base URL**: `https://[Server URL]:4443` — port 4443 is used for all calls (`Whats-New/Whats-New.htm`: "Updated all topics to change the API calls to reflect port 4443 in the base URLs," July 1, 2025).
- **Auth**: every endpoint except `Get-Token` requires an `Authorization` header carrying the bearer token obtained from `Get-Token` (`Quick-Start/Authentication.md`). `Get-Token` itself requires an `Authorization` header of its own: base64(`username:password`), default `YWRtaW46MWJleW9uZA==` = `admin:1beyond` (`API-Reference/Get-Token-API.md`).
- **Content-Type**: `application/json` for both request and response on every endpoint.
- **HTTP Method**: POST for every documented endpoint — there are no GET, PUT, or DELETE calls anywhere in this API.
- **Base URI prefix**: all endpoints are under `/api/...` except `Get-Token`, which is at the root (`/get-token`), per an explicit note on that page.
- Tokens do not expire but are bound to the client's source IP; a new token is required if the server's IP changes (`Quick-Start/Authentication.md`).

## Endpoint table

| Endpoint | HTTP Method | Base URI | Auth | Request Parameters | Response Shape (success) | Description |
|---|---|---|---|---|---|---|
| Get-Token | POST | `/get-token` | `Authorization: base64(user:pass)` header (no token yet) | None (empty body) | `{"status":"OK","token":[token]}` | Obtains the auth token required by every other call. |
| AutoSwitchStatus | POST | `/api/AutoSwitchStatus` | Bearer token | none | `{"status":"OK","results":true|false,"message":"AutoSwitching in Progress"|"No AutoSwitching in Progress"}` | Reports whether AutoSwitching is in progress. |
| CallCameraPreset | POST | `/api/CallCameraPreset` | Bearer token | `cam` (int, 1–255, required), `pre` (int, 1–255, required) | `{"status":"OK","message":"Successfully called preset [value] for camera [value]"}` | Switches a camera output to a saved preset. |
| CameraStatus | POST | `/api/CameraStatus` | Bearer token | none | `{"status":"OK","message":"Live camera address queried successfully","address":"[value]"}` | Retrieves the active camera shot's address. |
| ChangeLayout | POST | `/api/ChangeLayout` | Bearer token | `id` (string, body JSON, required; valid A–Z) | `{"status":"OK","message":"Changed to Layout [A-Z]"}` or `"Already on Layout [A-Z]"` | Changes the active output layout. |
| ChangeRoomConfiguration | POST | `/api/ChangeRoomConfiguration` | Bearer token | `id` (int, body JSON, required; valid 1–99) | `{"status":"OK","message":"Changed to Room Configuration [1-99]"}` or `"Already on Room Configuration [1-99]"` | Changes the active room configuration. |
| CopyFiles | POST | `/api/CopyFiles` | Bearer token | `destination` (string, required), `logDestination` (string, required — blank disables logging), `deleteSource` (bool, required) | `{"status":"OK","message":"Successfully backed up information"}` | Copies recorded files from `D:\Recordings` to an external destination. |
| ForceChangeRoomConfig | POST | `/api/ForceChangeRoomConfig` | Bearer token | `id` (int, 1–99, required) | `{"status":"OK","message":"Changed to Room Configuration [1-99]"}` or `"Already on Room Configuration [1-99]"` | Forces a room-configuration change even while AutoSwitching is active (AutoSwitching is paused then resumed). |
| GetActiveTalkers | POST | `/api/GetActiveTalkers` | Bearer token | none | `{"status":"OK","talkers":"[...]","defaultShot":0|1}` | Returns which virtual mic position(s) have an active speaker; up to 2 for conversation/side-by-side mode. |
| GetAllStatus | POST | `/api/GetAllStatus` | Bearer token | none | `{"status":"OK","api_call_0":{...}, ... "api_call_12":{...}}` — 13 nested sub-responses, each `{"request_api","response_code","response_body"}` (`response_body` is a string the client must deserialize) | Aggregates the status of all system functions (switching, recording, streaming, layout, room config, cameras, disk space, copy) into one call. **Reveals 8 sub-APIs with no standalone documentation page** — see "Undocumented sub-APIs" below. *(2026-09-23: 7 of the 9 names actually listed there now have their own page — see the dated correction at the head of that section; only `ISORecordStatus` and `CopyStatus` remain without one.)* |
| GetCameras | POST | `/api/GetCameras` | Bearer token | none | `{"status":"OK","message":"cameras loaded successfully","cameras":[{"id","name","ip"}]}` | Lists configured camera models in the current room configuration. |
| GetLayouts | POST | `/api/GetLayouts` | Bearer token | none | `{"status":"OK","message":"Layouts loaded successfully","layouts":[{"id","name"}]}` | Lists all layouts stored on the system. |
| GetRoomConfigs | POST | `/api/GetRoomConfigs` | Bearer token | none | `{"status":"OK","message":"Room configs loaded successfully","roomConfigs":[{"id","name"}]}` | Lists all room configurations stored on the system. |
| GetScenarios | POST | `/api/GetScenarios` | Bearer token | none | `{"status":"OK","message":"Scenarios loaded successfully","scenarios":[{"id","name"}]}` | Lists all scenarios' names and IDs. |
| GoHome | POST | `/api/GoHome` | Bearer token | none | `{"status":"OK","message":"Successfully called Home Shot and preset"}` | Switches to the home shot preset. |
| GoToScenario | POST | `/api/GoToScenario` | Bearer token | `id` (int, required) | `{"status":"OK","message":"Successfully called scenario [value]","cameras":[[1-8]]}` | Calls a scenario by ID, changing the active shot. |
| ImportCameraPresets | POST | `/api/ImportCameraPresets` | Bearer token | none | `{"status":"OK","message":"Camera presets imported successfully"}` | Imports all camera presets to configured cameras. |
| LayoutStatus | POST | `/api/LayoutStatus` | Bearer token | none | `{"status":"OK","message":"Current layout queried successfully","layout":[{"id","name"}]}` | Returns the currently active layout. |
| Macro | POST | `/api/Macro` | Bearer token | `requests` (array, required) of `{"api": string, "body": string}` objects, each naming another API call and its body params | `{"status":"OK","message":"Finished running requests","responses":[{"request_api","response_code","response_body"},...]}` | Batches a sequence of other API calls into one request. |
| ManualSwitchCamera | POST | `/api/ManualSwitchCamera` | Bearer token | `address` (int, 1–255, required) | `{"status":"OK","message":"Successfully switched shot to [value]"}` | Manually switches to a specific camera output. |
| OutputStatus | POST | `/api/OutputStatus` | Bearer token | none | `{"status":"OK","results":true|false,"message":"Output in Progress"|"No Output in Progress"}` | Reports whether live output is in progress. |
| RecordingSpaceAvail | POST | `/api/RecordingSpaceAvail` | Bearer token | none | `{"status":"OK","message":"Available recording storage queried successfully","available_gigabytes":"[value]","total_gigabytes":"[value]"}` | Reports available recording disk space (rounded down to whole GB). |
| RecordStatus | POST | `/api/RecordStatus` | Bearer token | none | `{"status":"OK","results":true|false,"message":"Record in Progress"|"No Record in Progress"}` | Reports whether recording is in progress. |
| Restart | POST | `/api/Restart` | Bearer token | none | `{"status":"OK","message":"Restart command initiated"}` | Restarts the Automate VX system. |
| RoomConfigStatus | POST | `/api/RoomConfigStatus` | Bearer token | none | `{"status":"OK","message":"Current room configuration queried successfully","roomConfigs":[{"id","name"}]}` | Returns the currently active room configuration. |
| SaveCameraPreset | POST | `/api/SaveCameraPreset` | Bearer token | `cam` (int, 1–255, required), `pre` (int, 1–255, required) | `{"status":"OK","message":"Successfully saved preset [value] for camera [value]"}` | Saves the current shot as a preset for a camera output. |
| ScenarioStatus | POST | `/api/ScenarioStatus` | Bearer token | none | `{"status":"OK","message":"Successfully read selected scenario","scenario":{"id","name"}}` | Returns the currently active scenario. |
| ShotStatus | POST | `/api/ShotStatus` | Bearer token | none | `{"status":"OK","message":"Shot status queried successfully.","shotname":-1,"layout":"A","storedLayout":"A","cam1":1,"cam2":-1}` | Returns the active camera/scenario shot plus current and previous (side-by-side) layout. |
| Sleep | POST | `/api/Sleep` | Bearer token | none | `{"status":"OK","message":"VX went to sleep successfully"}` | Turns off all system functions and calls a sleep camera preset. |
| StartAutoSwitch | POST | `/api/StartAutoSwitch` | Bearer token | none | `{"status":"OK","message":"AutoSwitching Started Successfully"}` | Starts the AutoSwitching functionality. |
| StartOutput | POST | `/api/StartOutput` | Bearer token | none | `{"status":"OK","message":"Started Output"}` or `"Output is in progress"` | Starts live output over a configured interface. |
| StartPT | POST | `/api/StartPT` | Bearer token | `cam` (int, 1–255, required), `ptDir` (int 0–7, required: 0=Up,1=Up-Right,2=Right,3=Down-Right,4=Down,5=Down-Left,6=Left,7=Up-Left) | `{"status":"OK","message":"Successfully called started movement for camera [value]"}` | Starts continuous pan/tilt movement on a camera. |
| StartRecord | POST | `/api/StartRecord` | Bearer token | none | `{"status":"OK","message":"Record Started Successfully"}` | Starts recording. |
| StartStream | POST | `/api/StartStream` | Bearer token | none | `{"status":"OK","message":"Stream Started Successfully"}` | Starts streaming (requires stream settings pre-configured on the device). |
| StartZ | POST | `/api/StartZ` | Bearer token | `cam` (int, 1–255, required), `zDir` (int 0–1, required: 0=Zoom In, 1=Zoom Out) | `{"status":"OK","message":"[message]"}` | Starts continuous zoom movement on a camera. |
| StopAutoSwitch | POST | `/api/StopAutoSwitch` | Bearer token | none | `{"status":"OK","message":"AutoSwitching Stopped Successfully"}` | Stops the AutoSwitching functionality. |
| StopOutput | POST | `/api/StopOutput` | Bearer token | none | `{"status":"OK","message":"Output Stopped"}` or `"No output in progress"` | Stops live output. |
| StopPT | POST | `/api/StopPT` | Bearer token | `cam` (int, 1–255, required) | `{"status":"OK","message":"Successfully called stop camera [value]"}` | Stops pan/tilt movement on a camera. |
| StopRecord | POST | `/api/StopRecord` | Bearer token | none | `{"status":"OK","message":"Record Stopped Successfully"}` | Stops recording. |
| StopStream | POST | `/api/StopStream` | Bearer token | none | `{"status":"OK","message":"Stream Stopped Successfully"}` | Stops streaming. |
| StopZ | POST | `/api/StopZ` | Bearer token | `cam` (int, 1–255, required) | `{"status":"OK","message":"Successfully called stop camera [value]"}` | Stops zoom movement on a camera. |
| StreamStatus | POST | `/api/StreamStatus` | Bearer token | none | `{"status":"OK","results":true|false,"message":"Stream in Progress"|"No Stream in Progress"}` | Reports whether streaming is active (requires stream settings pre-configured). |
| Wake | POST | `/api/Wake` | Bearer token | none | `{"status":"OK","message":"VX woke up successfully"}` | Wakes the system from a sleep state and turns on optional Automate VX functions. |

That is **32 documented endpoints** (the table above has exactly 32 rows, `Get-Token` included), matching the "32 identical endpoint strings" observed shared verbatim between the Extron ControlScript module and the Extron .pkp (findings/07).

*(2026-09-23: 11 more pages were fetched after this was written — finding 08's second correction (`ChangeRoomConfiguration`, `StopAutoSwitch`) and ROADMAP R32 (`AutoSwitchStatus`, `GetLayouts`, `GetRoomConfigs`, `LayoutStatus`, `OutputStatus`, `RecordStatus`, `RoomConfigStatus`, `StartAutoSwitch`, `Wake`) — so the table above now has 43 rows. The "32 identical endpoint strings" match with findings/07 is about what Extron's driver calls, not about how many pages exist on Crestron's site; it is not re-measured here.)*

## Error shape

Every endpoint that documents an error case returns one of two shapes, inconsistently capitalized across pages (cited verbatim, not normalized):
- `{"status": "Error", "err": "[Reason for error]"}` — the majority pattern (e.g. ChangeLayout, ForceChangeRoomConfig, CallCameraPreset, CameraStatus, GetActiveTalkers, GetCameras, ManualSwitchCamera, RecordingSpaceAvail, Sleep).
- `{"status": "error", "message": "..."}` — lowercase `status`, `message` instead of `err`, used only by StopPT and StopZ (`API-Reference/StopPT-API.md`, `API-Reference/StopZ-API.md`).
- `Get-Token` uses `{"status": "Error", "err": "Incorrect Username or Password"}`.
- `StopOutput` documents no error case at all on its page.
- `GetScenarios` uses a fixed error string `"Failed to read available scenarios"` rather than a generic `[Reason for error]` placeholder.
- `GoToScenario` uses `"Could not find scenario: [value]"`.
- `Restart` uses `"Could not restart. [Reason for error]"`.
- `SaveCameraPreset` uses `"Camera preset [value] is invalid"`.
- `StartPT`/`StartZ` use `"Could not move camera [value]"`.
- `StartRecord`/`StopRecord` use `"Failed to Start Recording"` / `"Failed to Stop Recording"`.
- `StartStream`/`StopStream` use `"Failed to Start Streaming"` / `"Failed to Stop Streaming"`.
- `StreamStatus` uses `"Failed to Fetch Stream Status"`.

## Undocumented sub-APIs (found only inside GetAllStatus's response, no standalone page)

*(2026-09-23 correction: this section's own list below has 9 names, not the 8 the prose says — that mismatch is in the original text and is left as written. Of those 9, 7 have since gotten a standalone page — added in commit ad9899e (`ChangeRoomConfiguration`, `StopAutoSwitch`; the latter isn't one of the 9 below, so read that commit as adding pages for names outside this list too) and commit aa75c40 (`AutoSwitchStatus`, `GetLayouts`, `GetRoomConfigs`, `LayoutStatus`, `OutputStatus`, `RecordStatus`, `RoomConfigStatus`). Checked directly against the files now under `API-Reference/`: only `ISORecordStatus` and `CopyStatus`, of the 9 listed, still have no page. The "confirmed by repeated `brightdata search` queries" claim below was accurate for the search method used on 2026-09-07 — it was not a claim that no page could ever exist, and it did not hold once a different harvest (`WebFetch`, R32) tried the URLs directly on 2026-09-23. Original text follows unedited.)*

`GetAllStatus`'s example response body (`API-Reference/GetAllStatus-API.md`) names 13 internal "request_api" calls it aggregates. Of those, 5 correspond to endpoints documented above (StreamStatus, RecordingSpaceAvail, GetCameras, CameraStatus — matched by name) and 8 do **not** have their own page anywhere on the site (confirmed by repeated `brightdata search` queries for each name, all returning zero hits under `site:sdkcon78221.crestron.com`):

- `AutoSwitchStatus`
- `OutputStatus`
- `ISORecordStatus`
- `RecordStatus`
- `CopyStatus`
- `GetLayouts`
- `LayoutStatus`
- `GetRoomConfigs`
- `RoomConfigStatus`

These are real, live server-side calls (their example JSON responses are shown verbatim inside `GetAllStatus-API.md`) but are **not independently documented** — no dedicated page, no syntax/parameter section of their own. Treat them as attested-but-undocumented: usable for coverage comparison against the three implementations (they may appear as internal strings in the Extron/Crestron drivers even though this Crestron doc site never gives them a page), but do not expect a params/response contract beyond what's embedded in the `GetAllStatus` example.

## Deprecated / removed

- **CallPlugin** — mentioned only in `Whats-New/Whats-New.htm` (May 9, 2025 entry): "Removed support for depreciated CallPlugin API call." No API-Reference page exists for it (confirmed absent from the current 32; likely removed prior to firmware 6.4.1). Do not treat as a current endpoint, but its historical existence is relevant if either Extron implementation or the Crestron SIMPL+ module still references it.
