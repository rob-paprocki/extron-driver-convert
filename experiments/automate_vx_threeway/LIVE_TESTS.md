# Automate VX live tests

The calls that settle what the three-way verification (`REPORT.md`) cannot settle offline.
Each names the discrepancy it settles. Run them against a unit where the disruptive ones
(Restart, SaveCameraPreset, CloseWirecast, ExportCameraPresets) are acceptable. LT17 needs the
IPCP Pro and a PC, not an Automate VX. Credentials are typed at run time: `USER:PASSWORD`
is a placeholder, never a value to commit. Record raw request and response bodies, with lab
addresses scrubbed before anything is committed.

- **LT0** setup (auth, X24/X34): curl -sk -i -X POST -H 'Content-Type: application/json' -H 'Authorization: $(printf %s 'USER:PASSWORD' | base64)' --data '' https://HOST:4443/get-token. Record the raw body and the JSON type of "token" (string, number or array). Repeat with Authorization set to base64('admin:wrong') and record the HTTP status and body (200 with {"status":"Error"} vs 401). Then set TOKEN and define avx(){ curl -sk -i -X POST -H 'Content-Type: application/json' -H "Authorization: $TOKEN" --data "$2" https://HOST:4443/api/$1; } for every test below. Record the HTTP status, headers and raw body of every call, plus the unit's Automate VX version and hardware (VXx-1B or VX2).

- **LT1** legacy transport (X19, X32): curl -s -i -X POST -H 'Content-Type: application/json' -H 'Authorization: $(printf %s 'USER:PASSWORD' | base64)' --data '' http://HOST:3579/get-token. Does plain HTTP on 3579 answer (the Crestron module's default Request_Type=HTTP)? Note whether the unit was upgraded (legacy mode on by default) or freshly installed.

- **LT2** H6 GoToScenario.id (X12a, X13): avx GoToScenario '{"id":1}'; avx ScenarioStatus ''; avx GoToScenario '{"id":"2"}'; avx ScenarioStatus ''; avx GoToScenario '{"id":"1.0"}'; avx ScenarioStatus ''; avx GoToScenario '{"id":2.0}'; avx ScenarioStatus ''. Record which forms change the scenario and the error text for the rest. The last two show what GC would send if its Decimal arrived as a float. The first form is exactly what the Crestron library sends (REPORT §10.3); the second is Extron's.

- **LT3** H6 StartPT/StartZ types (X12b): avx StartPT '{"cam":1,"ptDir":5}'; avx StopPT '{"cam":1}'; avx StartPT '{"cam":"1","ptDir":"5"}'; avx StopPT '{"cam":"1"}'; avx StartPT '{"cam":1,"ptDir":"5"}' (Extron's actual mixed form); avx StopPT '{"cam":1}'. Then avx StartZ '{"cam":1,"zDir":0}', avx StartZ '{"cam":"1","zDir":"0"}' and avx StartZ '{"cam":1,"zDir":"0"}', each followed by avx StopZ '{"cam":1}'. Observe camera motion and record each reply. Crestron's library sends neither Extron form: it sends all-number bodies with every key, to a differently cased URI. LT18 and LT20 cover that.

- **LT4** string ids beyond H6 (X12c): avx StopAutoSwitch '' first. Then avx ChangeRoomConfiguration '{"id":"2"}' vs avx ChangeRoomConfiguration '{"id":1}'; avx ForceChangeRoomConfig '{"id":"2"}' vs '{"id":1}'; avx ManualSwitchCamera '{"address":"2"}' vs '{"address":1}'; avx CallCameraPreset '{"cam":"1","pre":"1"}' vs '{"cam":1,"pre":1}'. Disruptive, scratch preset only: avx SaveCameraPreset '{"cam":"1","pre":"250"}' vs '{"cam":1,"pre":250}'. The Crestron library's own forms are ChangeRoomConfiguration and ForceChangeRoomConfig '{"id":2}' (a number), ManualSwitchCamera '{"address":"2","id":0}' and CallCameraPreset '{"cam":"1","pre":"1"}'.

- **LT5** RoomConfigStatus shape (X14): avx RoomConfigStatus ''. Record whether the body has roomConfigs (a list) or roomConfig (an object), and the JSON type of id. Compare with api_call_12 inside avx GetAllStatus ''. Crestron's library reads roomConfig and Extron reads roomConfigs[0], so this test says which vendor's room-configuration feedback works.

- **LT6** CameraStatus type (X16): avx CameraStatus ''. Record the JSON type of address and whether addresses[] is present. Compare with api_call_8 inside avx GetAllStatus ''.

- **LT7** LayoutStatus shape (X15): avx LayoutStatus ''. Record whether layout is a list or an object; compare with api_call_10 of GetAllStatus.

- **LT8** ScenarioStatus edge (X17): disruptive, avx Restart ''. Once the unit is back and before any scenario is recalled, run avx ScenarioStatus ''. Is `scenario` absent, null, or an object?

- **LT9** ISO family (X07): avx ISORecordStatus ''; avx StartISORecord ''; avx ISORecordStatus ''; avx StopISORecord ''. Record 200/OK vs 404 or {"status":"Error"} on current firmware. Repeat with 'Enable Pause' switched on in the web UI ([AVX-2735] makes ISO recording and pause mutually exclusive) and record the error text.

- **LT10** pause (X02, X09): avx StartRecord ''; avx PauseRecord ''; avx RecordStatus ''; avx GetAllStatus ''; avx PauseRecord ''; avx RecordStatus ''; avx StartRecord ''; avx RecordStatus ''; avx StopRecord ''. Record whether any response field distinguishes paused from recording (the Crestron Recording_State=2 case), and whether a second PauseRecord or a StartRecord resumes.

- **LT11** H6 talkers and shot (X03): with AutoSwitch running and someone speaking, run avx GetActiveTalkers '' and avx ShotStatus ''. Record the real JSON type of `talkers` (documented as the string "[5,]") and of `shotname`, `cam1` and `cam2`.

- **LT12** error envelope (X18): on a system with fewer than 200 cameras run avx StopPT '{"cam":200}'; avx StopZ '{"cam":200}'; avx StartPT '{"cam":200,"ptDir":0}'. Record the capitalisation of status and whether the error key is err or message.

- **LT13** CallPlugin (X10): avx CallPlugin '{"name":"nonexistent.bat","arg1":"","arg2":""}'. Record whether the result is a 404, a removed-API error, or a plugin-not-found error (support removed in 6.4.1 per the changelog).

- **LT14** token lifetime and permissions (X24, X34): after an avx Restart '' completes, reuse the old $TOKEN on avx RecordStatus ''. Is it 200 or 401/Error? Create a non-admin web user with restricted permissions, get its token through /get-token, and call avx Restart '' and avx StartRecord ''. Record the HTTP status and body of the permission error.

- **LT15** newly found pages (X01, X06): avx HealthStatus ''; avx StorageSpaceAvail '{"drives":""}'; avx RecordingSpaceAvail ''; avx GetCameras ''. Disruptive, only if acceptable: avx ExportCameraPresets ''; avx CloseWirecast ''. Confirm each exists on the unit's firmware and record its response shape.

- **LT16** force vs change while AutoSwitch runs (X23): avx StartAutoSwitch ''; avx ChangeRoomConfiguration '{"id":"1"}' (record the error text); avx ForceChangeRoomConfig '{"id":"2"}'; avx AutoSwitchStatus ''; avx RoomConfigStatus ''.

- **LT17** GC on-wire types, no Automate VX needed (X12c, X13, X16): load 1bynd_42_4279_v1_0_11 on the IPCP Pro 360 used for 20025/20026 and point it at a PC HTTPS listener on 4443. The listener answers /get-token with {"status":"OK","token":"t"} and every /api/* with {"status":"OK","results":true,"address":4,"scenario":{"id":3},"roomConfigs":[{"id":5}]}, and logs every raw request body. From GC buttons fire Scenario=3, Room Configuration=5, Force Room Configuration=5, Switch Camera=4, Camera Preset Recall (Camera 1, Value 1), Pan Tilt Up (Camera 1) and Zoom In (Camera 1). Record the exact JSON: int vs float vs quoted string, and any TypeError for Decimal. Also check whether an int `address` binds to the Switch Camera Enum feedback, and whether a str scenario id binds to the Decimal Scenario feedback.

- **LT18** pan/tilt URI case (X36): avx StartPt '{"cam":1,"ptDir":0,"zDir":0}'; avx StopPt '{"cam":1,"ptDir":0,"zDir":0}' (Crestron's exact form); then avx StartPT '{"cam":1,"ptDir":0}'; avx StopPT '{"cam":1}'. Record whether both casings move and stop the camera, or whether one returns 404.

- **LT19** Authorization scheme (X37): with $TOKEN from LT0, run curl -sk -i -X POST -H 'Content-Type: application/json' -H "Authorization: Basic $TOKEN" --data '' https://HOST:4443/api/RecordStatus, and the same with Authorization: $TOKEN. Then repeat LT0's /get-token with Authorization: Basic $(printf %s 'USER:PASSWORD' | base64). Record whether the "Basic " form is accepted (this is what the Crestron module sends from a 3-Series processor over HTTPS).

- **LT20** unused keys (X38): avx StartZ '{"cam":1,"ptDir":0,"zDir":0}', then avx StopZ '{"cam":1,"ptDir":0,"zDir":0}'. Watch whether the camera pans up (ptDir 0 is Up) as well as zooming. Then avx ManualSwitchCamera '{"address":"2","id":0}' and avx CameraStatus ''. Record whether the extra keys are ignored.
