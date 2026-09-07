# Index — Crestron 1 Beyond IV-CAM Series doc harvest (docs.crestron.com area 9440)

Harvested via Bright Data CLI (`brightdata scrape <url>`), never via WebFetch/WebSearch or a
direct request from this machine's IP, per project rules. All pages below are part of the same
doc set, titled "IV-CAM Series Manual" in the page `<title>` (visible on every page fetched),
under `https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/`.

**Scope finding, stated up front:** this doc set is NOT camera-family-generic — it explicitly
covers the exact cameras in question. `IV-CAM-P20-Specifications.md` and
`IV-CAM-I20-Specifications.md` are dedicated per-model spec pages for the IV-CAM-P20 and
IV-CAM-I20; `VISCA-Commands.md` (`CAM_MountMode`) and `VISCA-Lightbar-Commands.md` both call out
"IV-CAM-P12 and IV-CAM-P20" and "IV-CAM-I12-B and IV-CAM-I20" by name for model-specific
behavior; `Reserved-Presets.md` tabulates presets that differ specifically for IV-CAM-I20 (Group
Tracking, Preset Zones, Tracking Profiles). See `COMMANDS.md` Section 0 / footer for the full
scope discussion, including the one gap found (no P20-specific reserved-preset rows appear
anywhere in this set).

## VISCA protocol / command reference (the core deliverable)

| Page | URL |
|---|---|
| VISCA Commands (main command/inquiry tables, zoom & exposure-comp tables, error codes) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm |
| VISCA Lightbar Commands (nibble-packing worked example) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Lightbar-Commands.htm |
| VISCA Intelligent Switching Commands (multi-camera switching over VISCA/TCP) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Intelligent-Switching-Commands.htm |
| Reserved Presets (preset-number → function/model table, used by `Call Camera Preset`) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Reserved-Presets.htm |

See `COMMANDS.md` for the full tabulation drawn from all four of the above.

## Model specifications (establishes I20/P20 are in scope; zoom, pan/tilt, FOV, control-protocol facts)

| Page | URL |
|---|---|
| IV-CAM-P20 Specifications | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P20Specs.htm |
| IV-CAM-I20 Specifications | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm |

## Camera configuration / PTZ / presets / IP setup (sibling pages, UI-level not byte-level)

| Page | URL |
|---|---|
| Camera Controls (PTZ Controls, Presets Set/Call/Clear, Tracking — Camera Manager 2 UI) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Camera-Controls.htm |
| Set a Static IP Address (network/IP setup for VISCA-over-IP control) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Set-a-Static-IP-Address.htm |
| Tracking Menu (a.k.a. "Intelligent-Settings.htm"; entry point for Presenter/Group Tracking config, I20/I12 only) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Intelligent-Settings.htm |
| Presenter Tracking Settings (Auto-Tilt, Auto Zoom, Group Track — I20/I12 Presenter mode) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Presenter-Tracking-Settings.htm |
| Intelligent Switching (a.k.a. "Multi-Camera-Switching-Config.htm"; overview, up to 5 cameras) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Multi-Camera-Switching-Config.htm |
| Tracking Settings (per-camera-type intelligent-function settings menu) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Tracking-Settings.htm |
| Change the Camera Mode (Presenter Tracking ⇄ Group Framing, I12/I12D only) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Change-the-Camera-Mode.htm |
| Perform a Factory Restore (hardware RESET button procedure) | https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Perform-a-Factory-Restore.htm |

## Root / navigation pages fetched but NOT saved (content-free stubs)

These were fetched to map the doc tree but contain no information beyond a one-line summary and
a list of child-page names with no data of their own (their content is entirely subsumed by the
child pages above), so they were not written as separate files:
- `https://docs.crestron.com/en-us/9440/` (root "IV-CAM Series" landing page)
- `https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Device-Configuration.htm`
- `https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Initial-Setup.htm`
- `https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/Camera-Specifications.htm`

## Pages referenced but NOT fetched (out of budget / lower priority for this task)

Named in cross-references from the pages above but not pulled into this harvest; listed so a
follow-up pass knows where to look. None of these are VISCA byte-level protocol pages — they are
all Camera Manager 2 software UI walkthroughs:
- `Set-the-Tracking-Zone.htm`, `Set-the-Tracking-Shots.htm` (Presenter Tracking Settings sub-pages)
- `On-Screen-Display(OSD)-Menu.htm` (OSD menu, referenced for Room Size setting used by Tracking)
- `Add-Cameras.htm`, `Connect-the-Camera.htm` (Installation-section pages)
- `Presenter-Tracking-Settings.htm` sibling `Group-Framing` equivalent page (not located by name)
- `Custom-Intelligent-Switching-Configuration.htm`, `Visual-Cue-Intelligent-Switching-Configuration.htm`,
  `Intelligent-Switching-Output.htm`, `Intelligent-Switching-Design.htm` (Intelligent Switching sub-pages,
  found only via search-snippet titles, exact URLs not resolved)
- `IV-CAM-P12-Specifications.htm`, `IV-CAM-I12-Specifications.htm`, and a `Camera Accessory
  Specifications` page (sibling spec pages for the non-in-scope I12/P12 models)
