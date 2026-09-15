# panel/ — a TLP Pro 725M test page for the i20 loopback

One page. Each button sends one value to the i20 driver and should light when
the driver reports that value. The labels at the bottom show the number-type
statuses. The PC plays the camera (`../visca_listener.py`), so every press shows
up there as decoded bytes.

`i20-status.json` is the spec. It was built with `extron-gdl-toolkit`, from its
Afterburn 835 seed retargeted to the TLP Pro 725M. The built `.gdl` is not
committed: it carries Extron template artwork. Rebuild it with:

    py -3.11 -m gdl.edit plan retarget.json "seeds/Afterburn 835 (Project1).gdl" retarget-plan.json
    (apply with powershell/Apply-GdlEdits.ps1, pack with gdl.container, then)
    powershell/New-GdlPanel.ps1 -Spec i20-status.json -Donor seed725.gdl -Output i20-loopback.gdl

where `retarget.json` is `{"edits":[{"op":"retarget","model":"TLP725M","scale":true}]}`.

## 1. Set up the project in GC

1. New project. Add the IPCP Pro 360 as the controller.
2. On one of its Ethernet ports, add **1 Beyond / IV-CAM-I20 v1.4**. Set its
   address to the PC. It uses port 5500.
3. Add the TLP Pro 725M under the controller.
4. **User Interfaces → Button Actions**, click **Import layout**, and pick
   `i20-loopback.gdl`.
5. In the page list, pick **i20 Status**. The file also holds the template's own
   pages. Ignore them.

## 2. Wire up the buttons

For each button: select it, drag the command onto **Button Press**, and set the
value. Then open the **Visual Feedback** tab, drag the same command there, and
set **On** to the button's value. For **Off**, pick any other value.

Tip: set up one button, then right-click → Copy, and **Paste All** onto its
neighbors. Change only the values.

| buttons | command | press value / On state |
|---|---|---|
| Power On, Off | Power | On, Off |
| Auto Tracking Start, Stop | Auto Tracking | Start, Stop |
| Auto Exposure (5) | Auto Exposure | Full Auto, Manual, Shutter Priority, Iris Priority, Bright |
| White Balance Auto … Manual (5) | White Balance | Auto, Indoor, Outdoor, One Push, Manual |
| White Balance Trigger | White Balance | One Push Trigger. Press only, no feedback |
| Auto Focus On, Off | Auto Focus | On, Off |
| Backlight On, Off | Backlight | On, Off |
| Freeze Frame On, Off | Freeze Frame | On, Off |
| Camera Output 1–5 | Camera Output | 1–5. Press only if GC offers no state to pick |

## 3. Wire up the labels

Select the label, open **Text Feedback**, and drag the status onto it.

| label | status |
|---|---|
| top right, "Connection: --" | Connection Status |
| Zoom Position | Zoom Position |
| Pan Angle | Pan Angle Status |
| Tilt Angle | Tilt Angle Status |
| Camera Output | Camera Output |
| Cam 2 … Cam 5 | Camera Connection Status, Camera 2 … 5 |

Only the big `--` labels and the `Cam` labels get feedback. The small grey ones
are captions.

These statuses need **1bynd_19_20026, IV-CAM-I20 v1.4**. The v1.2 driver
(20024) lists them but offers nothing to bind (`../../skeleton_i20/PROTOCOL.md`,
2026-09-14). In a project that already has v1.2, remove that device and add
v1.4. Zoom Position may also ask for a Speed; any value will do, because the
status ignores it.

## 4. Run it

1. On the PC, start the camera:

       python experiments/loopback/visca_listener.py --reply full

2. In GC: **Build**, then **Upload**. Write down any error exactly as shown.
3. The panel should show Connection as connected.
4. Press every button once. Each press prints a decoded line on the PC, and the
   button should light.
5. Change the "camera" from the listener window. Type a line and press Enter:
   `power off`, `freeze on`, `tracking start`, `zoom 8000`, `output 3`,
   `camera 2 connected`, or `state` to show everything. The matching button or
   label should follow.

Note what lit, what did not, and how long it took. The capture file the
listener names on exit holds every byte both ways.

## What this does not cover

Pan and Tilt have no buttons here. Their labels only change when something
moves the camera, such as the Path B macro in `../README.md`.
