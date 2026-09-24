# Quickstart — get the i20 moving

Two deliverables, two paths. **The ControlScript one is faster** — no catalogue
rebuild, no Driver Manager, no GC at all.

*Every call on this page was run against the module with `extronlib` stubbed
out (`doc_calls.py`, first 2026-09-13, again for v1.6 on 2026-09-23), and the
bytes it sent were checked against the tables here and in `PROTOCOL.md`. That
proves each call is well-formed. It does not prove a camera answers it.*

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

Bold rows are the i20 additions; the rest are Extron's original commands. Rows
marked *(v1.6)* are the parity commands added in `20028`, each one Crestron's
own template and reply rule (`CRESTRON_PARITY.md`).

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
| **`TrackingMode`** | **`Group`, `Presenter`** (I20 only) | **—** | **yes (v1.6)** |
| **`TrackingProfile`** | **1–4** (I20 only) | **—** | **yes (v1.6)** |
| **`TrackingShot`** | **`Home`, `Tracking`** | **—** | **—** |
| **`PresetZone`** | **1–4** (I20 only) | **—** | **—** |
| **`IndicatorLight`** | **`None`, `Half`, `Full`** | **`{'Color': 'Green'/'Red'/'Yellow', 'Brightness': 'Off'/'Dim'/'Medium'/'Bright'}`; not needed for `None`** | **—** |
| **`CameraOutput`** | **1–5** (Resume is `IntelligentSwitching`) | **—** | **yes — shares one inquiry with the next row** |
| **`IntelligentSwitching`** | **`Resume`, `Pause`** | **—** | **yes (v1.6)** |
| **`CameraConnectionStatus`** | **feedback only** | ***required* `{'Camera': 2–5}` — `cam.Update('CameraConnectionStatus', {'Camera': 2})`; if missing, discarded** | **yes** |
| **`FreezeFrame`** | **`On`, `Off`** | **—** | **yes** |
| **`Menu`, `Identify`, `Reboot`** | **any** | **—** | **—** |
| **`ExposureCompensationMode`** *(v1.6)* | **`On`, `Off`** | **—** | **yes** |
| **`ExposureCompensation`** *(v1.6)* | **0–14; 7 is 0 EV** (auto exposure only) | **—** | **yes** |
| **`FocusPosition`** *(v1.6)* | **12224–20664** (I20 12224–17114, I12 15084–20664; manual focus only) | **—** | **yes** |
| **`OnePushAutoFocus`** *(v1.6)* | **any** | **—** | **—** |
| **`AutoFocusBehavior`** *(v1.6)* | **`Global`, `Center`, `Face`** | **—** | **yes** |
| **`AutoFocusSensitivity`** *(v1.6)* | **1–3** | **—** | **yes** |
| **`AutoPrivacyMode`** *(v1.6)* | **`On`, `Off`** — the camera answers nothing while in privacy mode | **—** | **yes** |
| **`AutoSoftwareUpdate`** *(v1.6)* | **`On`, `Off`** | **—** | **yes** |
| **`DeviceModel`, `RomVersion`** *(v1.6)* | **feedback only**: `IV-CAM-I20`/`I12`/`P20`/`P12`/`Unknown`, and the ROM version as the raw 16-bit number | **—** | **yes — both send one shared inquiry** |
| **`PanSpeedMaxStatus`, `TiltSpeedMaxStatus`** *(v1.6)* | **feedback only** | **—** | **yes — both send one shared inquiry** |

`Update()` works on exactly the **26** marked *yes*. Calling it on anything
else — `PanTiltAngle` and `ConnectionStatus` included — raises `AttributeError`.

**`ReadStatus()` straight after a `Set` proves nothing.** For every command
above with both a value and *yes* — and for `PanTiltAngle` and
`IndicatorLight` — `Set` writes the value it *sent* into the status without
waiting for the camera. Only a poll whose reply parses overwrites it; a timeout
or an unexpected reply leaves the value from the `Set` in place.

**Not in the driver, on purpose** (Crestron's driver has them): Privacy — tilt to
the ceiling and back, which is driver behaviour, not a camera command; do it with
`PanTiltAngle`. The press-and-hold menu keys — with `Menu` open, *Select*/*Back*
are `Zoom` `Tele`/`Wide` and release is `Zoom` `Stop`, and the arrows are
`PanTilt` at speed 1. Field of view, whose conversion Crestron supplies only as
compiled code. PTZ super operation, whose operation codes are declared nowhere.

---

## Path B — Global Configurator

**File:** `out/1bynd_19_20028_v1_0_0.pkp` — **the only one to install.** It lists
in Driver Manager as *1 Beyond / IV-CAM-I20 / 1.6* (and *IV-CAM-I12 / 1.6*), with
45 commands on the I20 and 42 on the I12, which does not get the three I20-only
ones. The other `.pkp` in `out/` are earlier builds kept as the record: `20020`–
`20023` are the staged packages of the first hardware round, and `20024`–`20027`
are v1.2–v1.5. A GC project that already uses an older build keeps it until the
device is swapped to v1.6 and rebound. Follow `PROTOCOL.md`, which starts with a
catalogue backup.

Use this path when you want the driver available to GC projects generally. The
package has built, uploaded and run on an IPCP Pro 360 against a PC playing the
camera (`20025`/`20026`); a real camera is the gate left. For simply making a
camera move, Path A is less ceremony.

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
3. **Preset 83.** Start group tracking (`TrackingMode`/`Group`), then send
   `TrackingMode`/`Presenter`. Does group tracking *stop*, or does presenter
   framing *engage*? Crestron's driver and Crestron's docs disagree, and this
   settles it. See `PROTOCOL.md` §T3b. From v1.6, `Update('TrackingMode')`
   reads Crestron's own group-tracking flag back, so the answer shows in the
   status too.

Three more, cheap once a camera answers at all:

4. **Does an I20 do intelligent switching?** `Update('CameraOutput')`. Crestron's
   I20 driver has no switching commands, the I20's spec sheet does not list the
   feature, and the I12's does; the commands came from a generic documentation
   page. A syntax-error reply (`90 60 02 FF`) means the I20 lacks it.
5. **`Update('DeviceModel')` and `Update('RomVersion')`.** The model code and
   the raw ROM number, to go beside the firmware version shown in the camera's
   web UI — Crestron formats that number with code this driver cannot read.
6. **`Update('FreezeFrame')`.** Crestron's driver declares no reply rule for
   this inquiry, so this driver's parse (VISCA's `02` on / `03` off) is the one
   status reply with no Crestron source behind it.

If something fails, the raw bytes are worth more than a description — every
command's expected wire string is in `PROTOCOL.md` and
`i20_wire_table.txt`.
