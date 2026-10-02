# An improved Automate VX ControlScript module (v1.1)

*2026-10-01. `out/onebynd_sm_Automate_VX_Series_v1_1_0_0.py`, derived from Extron's own
`onebynd_sm_Automate_VX_Series_v1_0_11_0.py` by `build_avx_cs.py`. Not yet run on a processor or
against an Automate VX. Reviewed by three independent reviewers; their findings are applied.*

## What it is

Extron's module with a provenance header, ten named fixes (E2-E11) and six additions (A1-A6),
each marked `[E#]` or `[A#]` in the output. Everything else is Extron's code, unchanged. It is
used exactly as Extron's help sheet describes, plus the new commands below.

**Same requests as Extron's.** Once logged in, each of 26 calls with valid values (every Set and
the On/Off polls) sends exactly the requests Extron's module sends; `test_avx_cs.py` diffs them.
The deliberate differences are E2 (a whole float such as `3.0` now sends `"3"`; fractions are
discarded), E6-E8 (how a login is obtained and repeated) and A1 (the new Pause value).

## The fixes

Each defect was reproduced by running Extron's module offline (the exec_harness extronlib
stand-in against a loopback server); each has a test that fails on Extron's module and passes on
this one, and leaving any one edit out of the build makes a test fail.

| | defect in v1.0.11.0 | what a user would see (reproduced offline) | fix |
|---|---|---|---|
| E2 | `Set('Scenario', None, {'ID': '3'})`, the help sheet's own form, raised `TypeError`; so did any string. A fractional number was sent as-is (`"2.5"`) | scenario buttons threw into the program | the ID comes from the qualifier or the value; anything that is not a whole number (fractions, infinity, True/False, `'3.0'`) is discarded |
| E3 | room-configuration feedback read only the list reply; the docs also show a single object (X14) | feedback never updated, an error line every poll; a null list threw | accept both shapes |
| E4 | scenario feedback let `KeyError`/`TypeError` escape | an exception on every poll if the unit answers oddly | caught and logged |
| E5 | a non-JSON, status-less or truncated reply raised; a device error's reason was never printed | tracebacks instead of log lines; "Error:" with no reason | caught; the reason is printed |
| E6 | a login reply without a token asked again at once, with no limit (X24) | hundreds of logins in one burst on every poll (487 under Python 3.14 here; the limit is the interpreter's recursion depth) | one attempt per call, the next call retries; a null or empty token is refused |
| E7 | a rejected token (401) was only logged, and later calls kept using it | a control-only program kept failing with a 401 log line; a polling one recovered only after 16 polls | log in again and repeat that request once; if a fresh token is refused too, the request is not permitted, the login is kept and other polls carry on |
| E8 | the first Set after start-up, or after the module declared Disconnected (which clears the token), was thrown away (X26) | the first button press did nothing | log in, then send it |
| E9 | a unit that was off, or refused the login, from start-up never set Connection Status | `ReadStatus('ConnectionStatus')` stayed `None` | failed logins count toward Disconnected (the sheet's 15 queries) |
| E10 | camera feedback kept the reply's type, an int on one documented shape (X16), and a bad value raised | `ReadStatus('SwitchCamera') == '4'` was never true on that shape | always a string `'1'`-`'255'`, as the help sheet says; non-integers are logged, out-of-range values dropped as before. A program that compared with an int must compare with a string |
| E11 | five On/Off parsers let `TypeError` escape on a malformed `results` | an exception instead of a log line | caught and logged |

Left as Extron wrote it: the first **poll** after start-up still only logs in (the next poll
sends; no button press is lost).

**Known limit of E7.** If a unit's 401 carried a non-Basic `WWW-Authenticate` header, Python's
Basic-auth handler would turn it into a different error before E7 sees it, and the old token
would be kept (as in Extron's module). LT14 should record the 401's headers.

## The additions (documented calls only)

| command | request | status written |
|---|---|---|
| `Set('Record', 'Pause')` | `POST api/PauseRecord`, no body | |
| `Update('Layout')` | `api/LayoutStatus` | `'A'`-`'Z'`; list or object reply |
| `Update('ActiveTalker', {'Talker': '1'})`, `Update('DefaultShot')` | `api/GetActiveTalkers` (firmware 6.3+) | mic position as a string, or `'None'`; `'On'`/`'Off'`. One call fills all three: poll one of them |
| `Update('RecordingSpace', {'Type': 'Available'})` | `api/RecordingSpaceAvail` | whole GB, `Total` then `Available` |
| `Update('HealthStatus')` | `api/HealthStatus` | the top-level status, e.g. `'Healthy'` |
| `Update('LayoutName')`, `Update('RoomConfigurationName')`, `Update('ScenarioName')`, `Update('CameraModel')` / `Update('CameraCount')` | `api/GetLayouts`, `GetRoomConfigs`, `GetScenarios`, `GetCameras` | one entry per qualifier (`Layout`, `RoomConfiguration`, `Scenario`, `Camera`); an entry that leaves the list is blanked; `CameraCount` is written after the models |

- **Qualifier values are strings** (`{'Camera': '1'}`, `{'Layout': 'A'}`), as in Extron's camera
  preset commands. Extron's own PanTilt and Zoom take an int Camera; these do not.
- **`CameraModel` holds the camera's model name**: the API's `name` field is documented as
  "[model name]", and `GetAllStatus` calls it `model`.
- **When to poll:** active talkers every few seconds if a program uses them; storage and health
  every few minutes; `CameraModel`/`CameraCount` on connect and after any room-configuration
  change (the list is per room configuration); the other name lists on connect and after any
  edit on the unit.
- Every reply is parsed completely before anything is written, so a subscriber's callback sees
  a consistent set, and an error inside a callback is not reported as a bad reply.

**Left out on purpose:** `ShotStatus` (one example, with field meanings and types undocumented;
LT11), pause and record-state feedback (the keys are not documented; LT10), `GetAllStatus`,
`StorageSpaceAvail`, `Macro`, `CallPlugin` (support removed in 6.4.1), and the disruptive calls
(`CopyFiles`, `Restart`, `ImportCameraPresets`, `ExportCameraPresets`, `CloseWirecast`).

## What is not proven

Nothing here has touched a unit. The live tests in `LIVE_TESTS.md` settle what remains: LT0
(token type, E6), LT5 and LT7 (room-configuration and layout reply shapes), LT6 (camera address
type, E10), LT8 (scenario status edge, E4), LT10 (pause and resume), LT11 (active-talker
types), LT12 (the error key and status capitalisation, E5), LT14 (what invalidates a token, and
the 401's headers, E7), LT15 (health, storage and cameras). **No live test covers the
`GetLayouts`, `GetRoomConfigs` or `GetScenarios` replies yet**; those parsers rest on the
documented shapes only. The module also needs a first run on a processor, which needs Extron's
ControlScript Deployment Utility and a certified account (ROADMAP H1L Path A).

## Reproduce

```
python experiments/automate_vx_threeway/build_avx_cs.py      # needs Extron's module (vendor, untracked)
python -u experiments/automate_vx_threeway/test_avx_cs.py      # 22 tests; 2 skip without Extron's module
```
