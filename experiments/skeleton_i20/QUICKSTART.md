# Quickstart — get the i20 moving

Two deliverables, two paths. **The ControlScript one is faster** — no catalogue
rebuild, no Driver Manager, no GC at all.

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

# Feedback
cam.Update('TrackingFraming')
print(cam.ReadStatus('TrackingFraming'))       # 'Start' or 'Stop'

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

| command | values | qualifier |
|---|---|---|
| `Power` | On, Off | — |
| `Preset` | 0–255 | `{'Action': 'Reset'/'Save'/'Recall'}` |
| `PanTilt` | Up, Down, Left, Right, Up Left, Up Right, Down Left, Down Right, Stop, Home, Reset | `{'Pan Speed': 1–24, 'Tilt Speed': 1–20}` |
| `PanTiltAngle` | `{'Pan': int, 'Tilt': int}` | `{'Pan Speed':…, 'Tilt Speed':…}` |
| `PanTiltHome` | Reset | — |
| `Zoom` | Tele, Wide, Stop | `{'Speed': 0–7}` |
| `ZoomPosition` | 0–16384 | `{'Speed': 0–7}` |
| `Focus`, `AutoFocus`, `Iris`, `Gain`, `Shutter`, `Backlight`, `WhiteBalance`, `AutoExposure` | as Extron's original | — |
| **`TrackingFraming`** | **Start, Stop** | — |
| **`GroupTracking`** | **Enable** | — |
| **`PresenterTracking`** | **Enable** | — |
| **`TrackingProfile`** | **1–4** | — |
| **`TrackingShot`** | **Home, Tracking** | — |
| **`PresetZone`** | **1–4** | — |
| **`IndicatorLight`** | **None, Half, Full** | **`{'Color': Green/Red/Yellow, 'Brightness': Off/Dim/Medium/Bright}`** |
| **`CameraOutput`** | **0–5** (0 = resume switching) | — |
| **`IntelligentSwitching`** | **Resume, Pause** | — |
| `FreezeFrame` | On, Off | — |
| `Menu`, `Identify`, `Reboot` | any | — |

Bold rows are the i20 additions. `Update()` works on exactly these eleven: `AutoExposure`, `AutoFocus`,
`Backlight`, `Power`, `WhiteBalance` (Extron's originals) and
`TrackingFraming`, `ZoomPosition`, `PanTiltAngle`, `FreezeFrame`,
`CameraOutput`, `CameraConnectionStatus` (added). Calling `Update()` on
anything else raises `AttributeError`.

---

## Path B — Global Configurator

**Files:** the four `.pkp` in `out/`. Follow `PROTOCOL.md` — it stages them so a
failure names its own cause, and it needs a catalogue backup first.

Use this path when you want the driver available to GC projects generally, or
to answer the open research question (does GC accept a synthesised package).
For simply making a camera move, Path A is less ceremony.

---

## What to report back

Whichever path, these three answers are worth more than everything else:

1. **Does it move?** Any command, any response.
2. **Does `Update('TrackingFraming')` return the right state?** Polling is the
   weakest part of this driver — the request bytes are documented, the reply
   handling for `CameraOutput` is not.
3. **Preset 83.** Start group tracking (`GroupTracking`/`Enable`), then send
   `PresenterTracking`/`Enable`. Does group tracking *stop*, or does presenter
   framing *engage*? Crestron's driver and Crestron's docs disagree, and this
   settles it. See `PROTOCOL.md` §T3b.

If something fails, the raw bytes are worth more than a description — every
command's expected wire string is in `PROTOCOL.md` and
`i20_wire_table.txt`.
