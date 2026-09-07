Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Intelligent-Switching-Commands.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Lightbar-Commands.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Advanced-Settings.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Add-Cameras.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Access-Camera-Feeds.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Set-a-Static-IP-Address.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Intelligent-Switching-Design.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Intelligent-Switching-Connection-Requirements.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm

# CONTROL — every control surface documented for the NextGen Cameras

## 1. VISCA over IP / serial — the primary control surface

Source: VISCA-Commands.htm

> "Crestron 1 Beyond cameras can be controlled using the VISCA protocol through either
> a serial (RS‑232 / RS‑485) or TCP connection. By default, the port for TCP control is
> set to 5500. For serial communication, make sure the baud rate of the controller is
> set to 9600 bps."

- **Default VISCA/TCP control port: 5500** (configurable — Advanced-Settings.htm:
  "Control Port: Enter the port number ... The default value of 5500 should be retained
  for most setups").
- **Serial: RS-232 / RS-485 at 9600 bps.**
- Also listed in the Specs pages as supported control protocols: **VISCA/TCP,
  VISCA/UDP, PELCO-D, PELCO-P**, plus **ONVIF** for the I-series (I12Specs.htm,
  I20Specs.htm — PELCO-D/PELCO-P and VISCA/UDP are not elaborated anywhere else in the
  harvested set beyond being named in the spec table).
- **Privacy Mode gates all VISCA control**: "Cameras cannot use any VISCA commands if
  they are in Privacy Mode. Send the wake command to the camera before sending any other
  VISCA commands to the camera."
- **IV-CAM-I12D-B only** has a documented second/dedicated VISCA-over-IP path distinct
  from the passthrough control port (Advanced-Settings.htm):
  > "VISCA Passthrough Port: ... The default value of 5500 should be retained ...
  > VISCA over IP Port: ... The default value of 52381 should be retained for most
  > setups. This protocol use[s] standard VISCA commands preceded by an 8‑byte header."
  This 8-byte-header VISCA-over-IP variant (port 52381) is not documented for
  I12/I20/P12/P20 — only for I12D-B, which is not one of the four driver targets (see
  MODELS.md §5).

## 2. What the shipped I20/P20 drivers actually use of VISCA (from driver metadata, not IL)

Reading only the declarative `driver_definition` JSON (command/template names and
comments — no IL decompilation, per this harvest's constraints):

- Both the I20 and P20 driver packages open a single TCP connection on **port 5500**
  with a `ReconnectInterval` of 5000 ms, and layer VISCA packets on top of it via a
  `ViscaPacket` text-command template (comment in the driver: "VISCA Packet (3-16
  bytes) | Header|Message|Terminator|, Header = 0x80 + (SenderAddress << 4) +
  ReceiverAddress").
- Both packages define command templates named `ViscaReservedCommand` (VISCA op-code
  prefix `c1` — this is the **Lightbar** command family's op-code, per
  VISCA-Lightbar-Commands.htm), `ViscaCustomCommand` (op-code prefix `c2 01` — the
  **Intelligent Switching "set"** family's op-code, per
  VISCA-Intelligent-Switching-Commands.htm), and `ViscaCustomInquiry` (op-code prefix
  `c2 09` — the Intelligent Switching "get"/inquiry family), plus a raw `PassThrough`
  text command that sends arbitrary bytes verbatim. These names are referenced multiple
  times in the driver definition (not just declared once and left unused), meaning the
  drivers do wire up Lightbar and Intelligent Switching control at some level, on top
  of core PTZ/zoom/focus/exposure/preset VISCA commands — this is broader than "just
  PTZ," even though ZOOM.md's transformation gap (no documented
  `ZoomLevelToPosition` formula) remains the harvest's main open question.
- No occurrence of `NDI`, `Automate`, `ONVIF`, or `RTSP`-as-a-*driver-issued-command*
  was found in the driver metadata beyond an `RTSP Port` **prompt/setting** (a
  user-facing parameter the control-system operator sets so the system's own AV
  routing knows the camera's stream endpoint) and declarative **stream-routing nodes**
  (`main-stream-output-node`, `sub-stream-output-node`, `reference-stream-output-node`,
  each tagged `compatibilityIds: ["RTSP"]`). I.e., the driver **models** the existence
  of RTSP streams for routing purposes but does not itself act as an RTSP/ONVIF client
  — it never issues ONVIF requests or pulls video.

## 3. RTSP video streaming

Source: Advanced-Settings.htm ("Accessing the RTSP Streams")

- **Port**: configurable; "Only RTSP values of 554 and the range of 3479–7999 are
  supported." Default/example shown is 554.
- **Auth**: `Username: admin`; `Password:` the camera's configured password (the same
  password set in Camera Manager — see §5).
- **URL structure**: `rtsp://cameraIPaddress:rtspportnumber/x.encodingtype`, optionally
  with embedded credentials: `rtsp://admin:[camerapassword]@[cameraIPaddress]:rtspportnumber/x.encodingtype`.
- **Stream selector `x`** (verbatim):
  > "x = 1: Access the camera's main PTZ feed. x = 2: Access the camera's reference
  > camera feed. For IV-CAM-I12D-B cameras: x = 1: Access the camera's PTZ 1 feed. x =
  > 2: Access the camera's main PTZ 2 feed. x = 3: Access the camera's reference camera
  > feed."
  (P12/P20 have no reference camera, so only `x=1` applies to them; I12/I20 have `x=1`
  PTZ and `x=2` reference; I12D-B — not a target model — has three.)
- **Worked example (verbatim)**: "`rtsp://10.10.120.145:554/1.h264`. The camera's IP
  address is `10.10.120.145`. The camera's RTSP port is `554`. The camera feed accessed
  is the main PTZ camera's feed (x = 1). The encoding type used is h.264."
- Encoding type (`x.encodingtype`) is configurable per-stream (H.264/H.265) via the
  Protocol > Streaming settings (Advanced-Settings.htm).

## 4. No browser-based web interface, no REST API, no Crestron Home / XiO Cloud integration

Across all 71 harvested pages, there is:
- **No mention of a browser/HTTP web-configuration interface.** All configuration is
  performed through the **Windows-only desktop application "Crestron 1 Beyond Camera
  Manager 2"** (explicitly required — every Specs page lists "Management Client
  Software: Crestron 1 Beyond Camera Manager 2 (Windows® OS computer required)") or the
  camera's own on-screen display (OSD) menu (overlaid on the video feed, navigated via
  Camera Manager's on-screen controls or the optional IV-CAMA-REMOTE IR remote).
- **No "REST API"/"RESTful" term or endpoint appears anywhere** in the harvested set.
- **No mention of "Crestron Home" or "XiO Cloud"** anywhere in the harvested set —
  these cameras are not documented as integrating with either Crestron's residential
  Home platform or its XiO Cloud device-management service. (Camera Manager's own
  "Auto-Update" feature pulls firmware from a configurable "Manifest URL," which is the
  closest thing to a cloud-update mechanism documented, and is explicitly recommended
  against when the camera is managed by "a Crestron Flex or Automate VX solution," which
  "perform automatic updates for the camera via their own methods" instead.)
- **App Port**: a separate, distinctly-named port used only for "communication between
  the Crestron 1 Beyond Camera Manager 2 software and the camera" — i.e. Camera
  Manager's own proprietary discovery/control channel, not VISCA/RTSP/ONVIF. No default
  value is stated ("should not be changed unless instructed to do so by Crestron True
  Blue Support").

## 5. Authentication / pairing

Source: Advanced-Settings.htm ("User Settings"), Add-Cameras.htm

- Each camera has a **single password** (no separate user accounts/roles documented),
  set/changed via Camera Manager's User tab (Old Password / New Password / Confirm
  Password fields).
- **That one password gates three things at once** (verbatim, Add-Cameras.htm): "The
  password entered for the camera also applies to RTSP and ONVIF connections for the
  camera." — i.e., Camera Manager pairing, RTSP streaming, and ONVIF all share one
  camera-wide credential; RTSP's documented username is `admin` (Advanced-Settings.htm);
  ONVIF's username is not stated separately anywhere in the harvest.
- **"Pairing" a camera into Camera Manager** (Add-Cameras.htm) is simply: discover the
  camera on the network (or enter its IP manually), enter its password, and the software
  connects — "The software shows a prompt indicating that the camera could not connect
  if the password for the camera is incorrect." No certificate exchange, OAuth, or
  token-based pairing flow is documented — password-only.
- Cameras ship with **DHCP on by default**; a static IP can be set via Camera Manager
  or during the add-camera flow (Set-a-Static-IP-Address.htm).
- Factory restore (rear recessed RESET button, hold 10s) wipes the static IP, password,
  and any "camera control protocol connections" and "Automate VX connections"
  (Perform-a-Factory-Restore.htm) — implying VISCA connection/pairing state and
  Automate VX association are themselves things that can be "connected" and reset,
  though no further protocol detail on that pairing state is given.

## 6. Automate VX / Intelligent Switching — a control surface beyond plain PTZ

Source: Intelligent-Switching-Design.htm, VISCA-Intelligent-Switching-Commands.htm

- Two Intelligent Switching configurations are documented: **Visual Cue** (uses only
  Camera Manager for setup, up to 5 cameras with one I12 in Group Framing mode as the
  hub) and **Custom** (requires "the provided example module located on the respective
  camera product page and a control system" — i.e., a Crestron control-system-side
  module/program, not just Camera Manager).
- The Intelligent Switching VISCA command family (op-codes `c2 01`/`c2 09`/`c2 0A`/`c2
  0B`/`c2 08`/`c2 09 0d`, from VISCA-Intelligent-Switching-Commands.htm) lets an
  external controller **set which camera's IP feeds an output, clear/resume/pause
  switching, and query connection status** — this is a distinct command surface from
  basic per-camera PTZ/zoom VISCA, aimed at a control system orchestrating up to 5
  cameras' outputs. As noted in §2, the I20/P20 driver metadata does reference generic
  templates matching this op-code family (`ViscaCustomCommand`/`ViscaCustomInquiry`),
  so at least a generic pass-through capability for this family exists in the shipped
  drivers, even without confirming (without IL analysis) that every named Intelligent
  Switching operation has a dedicated, user-facing control.

## 7. Lightbar control — a status/indicator surface

Source: VISCA-Lightbar-Commands.htm

- The camera's front lightbar (status indicator) is itself independently controllable
  over VISCA (`c1` op-code family): width (none/half/full), color (green/yellow/red),
  and brightness (bright/medium/dim) can be set directly, overriding or matching its
  default status-reporting behavior (green=intelligent function on, half-green=output
  on, yellow=firmware update, half-red=Privacy Mode).
- Per §2, the driver metadata's `ViscaReservedCommand` template (`c1` prefix) indicates
  the shipped drivers have at least generic access to this command family, distinct
  from the Status Bar LED bargraph described in the Specs pages' "Controls and
  Indicators" section (a separate, non-VISCA-controlled physical indicator on I20/P20
  per I20Specs.htm/P20Specs.htm — "Status Bar: (1) Multisegment tricolor LED bargraph").

## 8. Summary — what a driver *could* use that the two shipped drivers don't (as far as public docs + driver metadata show)

| Surface | Documented? | Used by I20/P20 driver metadata? |
|---|---|---|
| VISCA/TCP core PTZ, zoom, focus, exposure, presets (port 5500) | Yes | Yes |
| VISCA Lightbar family (`c1`) | Yes | Yes (generic template present) |
| VISCA Intelligent Switching family (`c2 01`/`c2 09`/…) | Yes | Yes (generic template present) |
| VISCA/UDP | Yes (spec table only) | Not observed |
| PELCO-D / PELCO-P | Yes (spec table only) | Not observed |
| ONVIF | Yes (spec table + shared password) | Not observed |
| RTSP video pull | Yes (URL scheme, auth, worked example) | Modeled as a routing endpoint only; driver doesn't act as an RTSP client |
| NDI\|HX2 | Yes (spec table, Device Name = NDI stream name) | Not observed |
| Camera Manager "App Port" protocol | Yes (named, no spec published) | N/A — proprietary to Camera Manager software, not driver-relevant |
| Browser/HTTP web UI | **Not documented to exist** | N/A |
| REST API | **Not documented to exist** | N/A |
| Crestron Home / XiO Cloud integration | **Not documented to exist** | N/A |
