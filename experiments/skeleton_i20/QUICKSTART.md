# Quickstart — get the i20 moving

Two deliverables, two paths. **The ControlScript one is faster** — no catalogue
rebuild, no Driver Manager, no GC at all.

*Every call on this page was run against the module with `extronlib` stubbed
out (`doc_calls.py`, 2026-09-13), and the bytes it sent were checked against the
tables here and in `PROTOCOL.md`. That proves each call is well-formed. It does
not prove a camera answers it.*

---

## Path A — ControlScript (fastest)

**File:** `out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py`

1. Copy it into your ControlScript project alongside `main.py`.
2. In `main.py`:

```python
from onebynd_camera_IV_CAM_I20_v1_0_0_0 import EthernetClass

cam = EthernetClass('192.168.1.50', 5500)     # TCP 5500
cam.Connect()

cam.Set('Power', 'On')
cam.Set('Preset', 1, {'Action': 'Recall'})
cam.Set('Zoom', 'Tele', {'Speed': 5})

# The i20-specific commands
cam.Set('TrackingFraming', 'Start')
cam.Set('TrackingProfile', 2)
cam.Set('IndicatorLight', 'Full', {'Color': 'Red', 'Brightness': 'Bright'})
cam.Set('CameraOutput', 2)

# Feedback: poll, then read what the camera reported
cam.Update('TrackingFraming')
print(cam.ReadStatus('TrackingFraming'))       # 'Start' or 'Stop' -- see below

# Or subscribe
cam.SubscribeStatus('TrackingFraming', None,
                    lambda cmd, val, q: print('tracking is now', val))
```

3. Build and upload as normal.

**Port: TCP 5500.** Not a guess — three sources in this repo agree, and two of
them are independent vendors:

| source | says |
|---|---|
| Crestron's driver definition, i20 **and** p20 | `"Type": "Tcp", "Info": {"Port": 5500}` |
| Crestron's VISCA documentation | "By default, the port for TCP control is set to 5500" |
| Extron's own driver header | "Manufacturer confirmed ethernet control uses UDP port 5500" |

Both vendors also converged on the same correction: each first documented UDP,
and Extron's revision `1_0_1` changed it to TCP "based on testing" (DR# 62249).
If a camera has been reconfigured, its web UI is the authority — but the default
is settled. Serial is 9600 bps.

### Every command

Bold rows are the 19 i20 additions; the rest are Extron's original commands.

**A qualifier marked *required* is read unconditionally.** Leave it out and the
call raises `TypeError` — even for values such as `Stop` or `Home` that do not
use it — or, where the table says so, is discarded with only an `Invalid
Command` line in the program log.

| command | value | qualifier | `Update()` |
|---|---|---|---|
| `Power` | `On`, `Off` | — | yes |
| `Preset` | 0–254, as an `int` (`'1'` raises). The module accepts 255, but that value is VISCA's `FF` terminator, so the camera sees a truncated frame | *required* `{'Action': 'Reset'/'Save'/'Recall'}` | — |
| `PanTilt` | `Up`, `Down`, `Left`, `Right`, `Up Left`, `Up Right`, `Down Left`, `Down Right`, `Stop`, `Home`, `Reset` | *required* `{'Pan Speed': 1–24, 'Tilt Speed': 1–20}` | — |
| **`PanTiltAngle`** | **ignored — pass `None`** | ***required* `{'Pan Speed': 1–24, 'Tilt Speed': 1–20, 'Pan': int, 'Tilt': int}`; a missing key is discarded** | **— (use the two below)** |
| **`PanAngleStatus`, `TiltAngleStatus`** | **feedback only** | **—** | **yes — both send one shared inquiry** |
| **`PanTiltHome`** | **any** | **—** | **—** |
| `Zoom` | `Tele`, `Wide`, `Stop` | *required* `{'Speed': 0–7}` | — |
| **`ZoomPosition`** | **0–16384** | ***required* `{'Speed': 0–7}`; if missing, discarded** | **yes** |
| `Focus` | `Far`, `Near`, `Stop` | *required* `{'Speed': 0–7}` | — |
| `AutoFocus`, `Backlight` | `On`, `Off` | — | yes |
| `Iris`, `Gain`, `Shutter` | `Up`, `Down`, `Reset` | — | — |
| `WhiteBalance` | `Auto`, `Indoor`, `Outdoor`, `One Push`, `Manual`, `One Push Trigger` | — | yes |
| `AutoExposure` | `Full Auto`, `Manual`, `Shutter Priority`, `Iris Priority`, `Bright` | — | yes |
| `ConnectionStatus` | feedback only — written by the module as polls succeed or time out | — | — |
| **`TrackingFraming`** | **`Start`, `Stop`** | **—** | **yes** |
| **`GroupTracking`** | **`Enable`** | **—** | **—** |
| **`PresenterTracking`** | **`Enable`** | **—** | **—** |
| **`TrackingProfile`** | **1–4** | **—** | **—** |
| **`TrackingShot`** | **`Home`, `Tracking`** | **—** | **—** |
| **`PresetZone`** | **1–4** | **—** | **—** |
| **`IndicatorLight`** | **`None`, `Half`, `Full`** | **`{'Color': 'Green'/'Red'/'Yellow', 'Brightness': 'Off'/'Dim'/'Medium'/'Bright'}`; not needed for `None`** | **—** |
| **`CameraOutput`** | **0–5 (0 = resume switching)** | **—** | **yes** |
| **`IntelligentSwitching`** | **`Resume`, `Pause`** | **—** | **—** |
| **`CameraConnectionStatus`** | **feedback only** | ***required* `{'Camera': 2–5}` — `cam.Update('CameraConnectionStatus', {'Camera': 2})`; if missing, discarded** | **yes** |
| **`FreezeFrame`** | **`On`, `Off`** | **—** | **yes** |
| **`Menu`, `Identify`, `Reboot`** | **any** | **—** | **—** |

`Update()` works on exactly the **12** marked *yes*. Calling it on anything
else — `PanTiltAngle` and `ConnectionStatus` included — raises `AttributeError`.

**`ReadStatus()` straight after a `Set` proves nothing.** For `TrackingFraming`,
`GroupTracking`, `PresenterTracking`, `TrackingProfile`, `ZoomPosition`,
`PanTiltAngle`, `FreezeFrame`, `IndicatorLight`, `CameraOutput` and
`IntelligentSwitching`, `Set` writes the value it *sent* into the status without
waiting for the camera. Only a poll whose reply parses overwrites it; a timeout
or an unexpected reply leaves the value from the `Set` in place.

---

## Path B — Global Configurator

**File:** `out/1bynd_19_20024_v1_0_0.pkp` — **the only one to install.** It lists
in Driver Manager as *1 Beyond / IV-CAM-I20 / 1.2* and renders all 34 commands
(finding 18 §8). The other four `.pkp` in `out/`, `20020`–`20023`, are the staged
packages from the first hardware round, kept as its record; `20023` renders only
15 commands. Follow `PROTOCOL.md`, which starts with a catalogue backup.

Use this path when you want the driver available to GC projects generally, or
to take the synthesised package through Build, Upload and control — the gates it
has not yet passed. For simply making a camera move, Path A is less ceremony.

---

## What to report back

Whichever path, these three answers are worth more than everything else:

1. **Does it move?** Any command, any response.
2. **Does the tracking poll follow the camera?** Change tracking from the camera
   side — its web UI or remote, not this module — then
   `Update('TrackingFraming')`. A poll that follows the camera is a pass; one
   that echoes the last `Set` is not evidence (see the `ReadStatus()` note under
   *Every command*). Polling is the weakest part of this driver: the request bytes are
   documented, but every reply layout the parsers expect comes from
   documentation, never from a camera.
3. **Preset 83.** Start group tracking (`GroupTracking`/`Enable`), then send
   `PresenterTracking`/`Enable`. Does group tracking *stop*, or does presenter
   framing *engage*? Crestron's driver and Crestron's docs disagree, and this
   settles it. See `PROTOCOL.md` §T3b.

If something fails, the raw bytes are worth more than a description — every
command's expected wire string is in `PROTOCOL.md` and
`i20_wire_table.txt`.
