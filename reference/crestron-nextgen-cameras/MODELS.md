Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Overview/IV-CAM-I12%20Features.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Overview/IV-CAM-I20%20Features.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Overview/IV-CAM-P12%20Features.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Overview/IV-CAM-P20%20Features.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Overview/IV-CAM-i12D-SpecText.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I12Specs.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P12Specs.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P20Specs.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Change-the-Camera-Mode.htm
Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Access-Camera-Feeds.htm

# MODELS — the IV-CAM lineup and what differs

## 1. The four target models at a glance

| | IV-CAM-I12 | IV-CAM-I20 | IV-CAM-P12 | IV-CAM-P20 |
|---|---|---|---|---|
| Camera design | **Dual camera**: wide-angle reference camera + PTZ camera | **Dual camera**: wide-angle reference camera + PTZ camera | Single PTZ camera only | Single PTZ camera only |
| Visual AI / auto-tracking | Yes — Group Framing, Presenter Tracking, Intelligent Switching (primary role) | Yes — Presenter Tracking, Group Tracking, Preset Zones | **No** — no visual AI, no tracking | **No** — no visual AI, no tracking |
| Optical zoom | 12x | 20x | 12x | 20x |
| Focal length | F=4.1–49.2 mm | F=5.2–94 mm | F=4.1–49.2 mm | F=5.2–94 mm |
| Field of View (PTZ), horizontal | 67.68° | 56.45° | 67.68° | 56.45° |
| Field of View (reference cam), horizontal | 104° (dual-camera only) | 104° (dual-camera only) | n/a (no reference camera) | n/a (no reference camera) |
| Iris | F1.8–F2.68 | F1.5–F3.0 | F1.8–F2.68 | F1.5–F3.0 |
| Recommended tracking range | Group Framing 5–25 ft; Presenter Tracking 15–25 ft | Presenter/Group Tracking 15–50 ft | n/a (no tracking) | n/a (no tracking) |
| Ideal room size (per docs) | medium to large spaces | large to extra large training rooms/classrooms/conference rooms | medium to large spaces (fixed, multi-area capture) | medium/large to extra large spaces (fixed, multi-area capture) |
| Intended role | tracking camera (group framing or presenter tracking) | tracking camera (presenter/group tracking, largest rooms) | fixed multi-area PTZ, Automate VX close-up camera | fixed multi-area PTZ, Automate VX close-up camera |

All four share: 1/2.8 Sony CMOS sensor, up to 1080p60 output, 3G-SDI/HDMI/USB/NDI|HX2/
ONVIF/RTSP/UVC video outputs, RJ-45 100Mbps Ethernet + RS-232/RS-485 serial,
VISCA/TCP + VISCA/UDP + PELCO-D + PELCO-P (+ ONVIF for I-series) control protocols,
PoE (802.3af Class 3, 15.4W) or 12VDC 2.5A power, and configuration exclusively via the
Windows-only "Crestron 1 Beyond Camera Manager 2" software (no browser-based web UI is
documented — see CONTROL.md).

Quoted (I20 Features, source above):
> "The IV‑CAM‑I20 has a dual camera design; the wide‑angle reference camera uses visual
> AI to direct the PTZ camera. All visual AI is built into the camera—no external
> system is needed."

Quoted (P20 Features, source above):
> "The IV‑CAM‑P20 is a high quality PTZ camera that outputs up to 1080p60 resolution
> video. The IV‑CAM‑P20 is ideal for meetings in large to extra large spaces where one
> camera needs to capture several areas of the room."
(No mention anywhere on the P20 or P12 Features/Specs pages of a second/reference
camera, visual AI, or tracking — the P-series is presented purely as a manually/
Automate-VX-driven PTZ camera.)

## 2. I12 vs I20 — same "family", different scale

- Both are dual-camera (reference + PTZ) intelligent tracking cameras.
- I12 = 12x optical zoom, medium/large rooms, tracking range 5–25 ft (Group Framing) or
  15–25 ft (Presenter Tracking); supports **Group Framing**, **Presenter Tracking**, and
  is compatible with **Intelligent Switching** and the **IV-CAMA-REMOTE** IR remote.
- I20 = 20x optical zoom, large/extra-large rooms, tracking range 15–50 ft; supports
  **Presenter Tracking**, **Group Tracking** (distinct from I12's Group Framing — group
  tracking follows multiple presenters across a larger area), and **Preset Zones**
  (Preset Zones are documented as **I20-exclusive**: "Note: Preset Zones are only
  available for the IV-CAM-I20." — Preset-Zones.htm).
- I20-exclusive "Zone Profiles" (titled "Zone Profiles" on the
  `Tracking-Profiles.htm` page): "note: This feature is only available with IV-CAM-I20
  series cameras. Zone profiles allow IV-CAM-I20 series cameras to switch between up
  to four different intelligent zone configurations." This is on top of Preset Zones
  (§ above) as a second I20-exclusive feature.
- I12 can be switched between Group Framing mode and Presenter Tracking mode
  (Change-the-Camera-Mode.htm); nothing in the docs suggests I20 has an equivalent
  mode switch — it appears to run Presenter/Group Tracking concurrently rather than as
  a selectable mode (Tracking-Settings.htm: "The Tracking Settings menu contains
  different settings depending on whether an i12, i20, or i12D camera is being
  configured").

## 3. P12 vs P20 — same "family", scaled optics, no intelligence

- Both are plain, non-tracking PTZ cameras positioned for Automate VX multi-camera
  switching setups or manual/console-driven control, with no wide-angle reference
  camera and no visual-AI features anywhere in their Features pages.
- P12 = 12x optical zoom; P20 = 20x optical zoom. Otherwise identical feature set
  (Automate VX compatible, Teams Rooms/Zoom Rooms certified, image flip / inverted
  mounting support, PoE + NDI|HX2, Camera Manager 2 configuration, Moon Gray/Bright
  White color options).
- `CAM_MountMode` (Stand/Ceiling — inverts video and PTZ control) is documented as
  "IV-CAM-P12 and IV-CAM-P20 only" in VISCA-Commands.htm, i.e. the I-series does not
  expose ceiling-mount inversion over VISCA (consistent with the I-series' dual-camera
  reference-tracking design not being intended for inverted ceiling mounting the same
  way).

## 4. Why the I20 driver has `ViscaAssemble2LowerNibbles` and the P20 driver doesn't

This is **not directly documented** anywhere in the 71-page harvest — Crestron's public
docs never name or describe `ViscaAssemble2LowerNibbles`, `ZoomLevelToPosition`, etc.
(these are internal to the compiled driver). What the docs do establish, which supports
a plausible explanation:

- **The I20 is a dual-camera device; the P20 is not.** I20 pairs a PTZ camera with a
  wide-angle reference camera whose feed is used for computer-vision tracking
  (Presenter Tracking / Group Tracking / Preset Zones), and the two camera's video
  streams and PTZ states are both exposed (`Access-Camera-Feeds.htm` describes viewing
  "Main" (PTZ) and reference feeds simultaneously; for the dual-PTZ I12D-B, `x=1`/`x=2`/
  `x=3` RTSP stream selectors address PTZ1/PTZ2/reference separately). A driver that
  needs to track/report additional per-camera or intelligent-function state (tracking
  status colors, debug mode, etc. — see `Camera-Controls.htm`'s Tracking section) has
  more nibble-packed status/control values to decode than a single-camera PTZ driver.
- **VISCA's byte format packs data as one nibble per byte** (`0p 0q 0r 0s` for a 16-bit
  Zoom Position, `pq rs` for other 2-byte fields — see VISCA-Commands.htm throughout).
  `ViscaAssemble2LowerNibbles` reads as a generic "take two VISCA bytes, each holding one
  nibble in its low 4 bits, and assemble them into a single byte/value" helper. Every
  VISCA numeric field in the spec (Zoom Position, Focus Position, Pan/Tilt Position,
  Gain, Shutter, Iris, ExpComp, ROM version, etc.) uses this same nibble-per-byte
  packing for both I20 and P20, so packing style alone doesn't explain why only I20
  needs the helper.
- The more likely differentiator is the **intelligent-function / tracking status and
  Lightbar signaling** that only I-series cameras have reason to decode: `Camera-
  Controls.htm`'s Tracking section (present only for I12/I20/I12D-B, explicitly noted
  "The Tracking settings are only available for the IV‑CAM‑I12, IV‑CAM‑I20, and
  IV‑CAM‑I12D‑B cameras") and the Lightbar color/segment commands in
  `VISCA-Lightbar-Commands.htm`, which use nibble-encoded per-segment color/brightness
  values (e.g., `8x c1 0C 0C 0C 0C ff`) that a P-series-only driver (fixed camera, no
  intelligent function to signal) would have less need to decode into higher-level
  state.
- **This is inference from the documentation, not a documented fact** — the docs do not
  say "I20 needs nibble assembly for X reason." The only *confirmed* fact (from reading
  driver metadata, not IL, per the task's constraints) is that `ViscaAssemble2LowerNibbles`
  is present in the I20 driver package and absent from the P20 driver package; the
  causal "why" above is this harvest's best-supported hypothesis given what the docs
  say differs structurally between the two cameras (dual-camera + intelligent tracking
  vs. single fixed PTZ), not a documented certainty.

## 5. Adjacent model mentioned in the doc set but not one of the four targets

- **IV-CAM-I12D-B**: a distinct model — "a pair of 4K PTZ cameras" plus a 4K reference
  camera and microphone array, for Speaker Tracking with Conversation Mode/PIP layouts.
  Not one of the four driver targets (I12/I20/P12/P20) and has no dedicated numeric
  Specs page in this harvest (only a Features-style page at
  `Overview/IV-CAM-i12D-SpecText.htm`, despite its filename). Mentioned here because it
  shares Configuration pages (Tracking-Settings, PTZ-Alignment, Access-Camera-Feeds) with
  the four target models and the docs frequently branch behavior by "i12, i20, or i12D."
- **-GV-B variants** (`IV-CAM-I12-GV-B`, `IV-CAM-I20-GV-B`, `IV-CAM-P20-GV-B`): TAA
  ("Trade Agreements Act")-compliant government-market variants of I12, I20, and P20
  respectively, with identical documented specs/features to their non-GV-B counterparts
  plus a TAA-compliance statement. Not separate optically or functionally.
