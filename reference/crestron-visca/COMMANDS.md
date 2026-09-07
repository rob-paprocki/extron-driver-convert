Source (primary): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Commands.htm
Source (lightbar): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Lightbar-Commands.htm
Source (intelligent switching): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/VISCA-Intelligent-Switching-Commands.htm
Source (reserved presets): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Reserved-Presets.htm
Source (P20 specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/P20Specs.htm
Source (I20 specs): https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Specifications/I20Specs.htm

This file tabulates every VISCA command documented on Crestron's "IV-CAM Series Manual" doc
set (doc area 9440) for the 1 Beyond IV-CAM cameras. Byte sequences are copied VERBATIM from
the source pages (including the doc's own placeholder-letter conventions); nothing here is
inferred or filled in from outside knowledge of the VISCA standard.

## 0. Framing conventions used by this documentation (verbatim)

- Transport: "Crestron 1 Beyond cameras can be controlled using the VISCA protocol through
  either a serial (RS-232 / RS-485) or TCP connection. By default, the port for TCP control is
  set to 5500. For serial communication, make sure the baud rate of the controller is set to
  9600 bps."
- Privacy Mode gate: "Cameras cannot use any VISCA commands if they are in Privacy Mode. Send
  the wake command to the camera before sending any other VISCA commands to the camera." (Note:
  the doc never actually tabulates a "wake" command anywhere on this page — see Gaps, below.)
- Command header placeholder: commands are written with a leading byte `8x`, where `x` is the
  camera address (not spelled out numerically on this page beyond that convention).
  `88 ...` is used literally for the two broadcast commands (AddressSet, IF_Clear).
  `8x c1 ...` / `8x c2 ...` are used for lightbar / intelligent-switching commands respectively.
- Reply header placeholder: replies are written with a leading byte `y0` or `z0`. The doc
  states explicitly: **"z = Device address + 8"** (given directly under the Error Messages
  table). `y` is used the same way in the Inquiry Commands table (i.e. `y0` = reply header for
  device address `x`, matching `z0`).
- Terminator: every command and reply ends in `FF`.
- Parameter placeholders inside a packet are lower-case letters (`p`, `q`, `r`, `s`, `t`, `u`,
  `v`, `w`, `y`, `z` — reused across rows/commands, meaning differs per command, defined in the
  Comments column each time) or upper-case pairs (`VV`, `WW`, `Y`, `Z` for pan/tilt).

## 1. Multi-nibble parameter encoding — THE CRUX

The documentation expresses multi-byte numeric parameters (zoom position, focus position, gain,
shutter, iris, bright, exposure-compensation, pan/tilt position) as a run of bytes each written
`0p` / `0q` / `0r` / `0s` (etc.) — i.e. every byte in the parameter is documented with a literal
leading `0` nibble, one significant (low) nibble per byte, MSB-first left-to-right in the byte
sequence as printed. Examples, verbatim from the Commands table:

- `CAM_Zoom Direct`: `8x 01 04 47 0p 0q 0r 0s FF` — "p,q,r,s: Zoom Position"
- `CAM_Focus Direct`: `8x 01 04 48 0p 0q 0r 0s FF` — "p,q,r,s: Focus Position"
- `CAM_ZoomFocus Direct`: `8x 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF` — "p,q,r,s: Zoom Position
  t,u,v,w: Focus Position"
- `CAM_RGain Direct`: `8x 01 04 43 00 00 0p 0q FF` — "p,q: R Gain"
- `CAM_BGain Direct`: `8x 01 04 44 00 00 0p 0q FF` — "p,q: B Gain"
- `CAM_Shutter Direct`: `8x 01 04 4A 00 00 0p 0q FF` — "p,q: Shutter Position"
- `CAM_Iris Direct`: `8x 01 04 4B 00 00 0p 0q FF` — "p,q: Iris Position"
- `CAM_Gain Direct`: `8x 01 04 4C 00 00 0p 0q FF` — "p,q: Gain Position"
- `CAM_Bright Direct`: `8x 01 04 4D 00 00 0p 0q FF` — "p,q: Bright Position"
- `CAM_ExpComp Direct`: `8x 01 04 4E 00 00 0p 0q FF` — "p,q: ExpComp Position"
- `Pan-tiltDrive Absolute Position`: `8x 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF`
- `Pan-tiltDrive Relative Position`: `8x 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF`
- `Pan-tiltLimitSet`: `8x 01 06 07 00 0W 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF`
- Inquiry replies mirror the same convention, e.g. `CAM_ZoomPosInq` reply
  `y0 50 0p 0q 0r 0s FF` ("p,q,r,s: Zoom Position"), `Pan-tiltPosInq` reply
  `y0 50 0w 0w 0w 0w 0z 0z 0z 0z FF` ("wwww = Pan Position zzzz = Tilt Position").

The doc does **not** spell out in prose, on the VISCA-Commands page itself, that this means
"16-bit value split into four nibbles, each right-justified into its own byte with a zero high
nibble" — that description is the reader's inference from the repeated `0p 0q 0r 0s` shorthand.
It gives the pattern typographically (one placeholder letter per byte, always prefixed `0`) but
does not narrate the packing/unpacking algorithm in words anywhere on this page.

### The one place nibble packing IS narrated step-by-step: the Lightbar page

The VISCA Lightbar Commands page is the only page in this doc set that walks through nibble
construction as explicit prose plus a fully worked numeric example (see
`VISCA-Lightbar-Commands.md` for the full page). Summary, verbatim:

- Command format: **`8x c1 ** ** ** ** ff`** where each `**` is a brightness+color byte for one
  of the four lightbar segments.
- Step-by-step procedure given by the doc:
  1. "The binary value string created should have 16 digits separated into four 4 digit
     segments" (i.e. one 4-bit nibble per lightbar segment... but then doubled — see below).
  2. "Each 4 digit segment of the binary value string must be individually converted into
     hexadecimal values. Each binary value string should result in two hexadecimal characters."
  3. Place each two-character hex value in sequence, single space between them.
  4. Slot into `8x c1 ** ** ** ** ff`.
- Worked example (bright green, half-width / two inner segments only), verbatim table:
  - Binary Value: `0000 1100 1100 0000`
  - Hexadecimal Code: `00 0C 0C 00`
  - VISCA Command: `8x c1 00 0C 0C 00 ff`
  - Doc's own explanation: "The 0000 binary value correlates with 00 (OFF) and 00 (Green)." /
    "The 1100 binary value correlates with 11 (Bright) and 00 (Green)." — i.e. each byte here is
    itself two packed 2-bit fields (brightness sub-nibble, color sub-nibble), not a single 4-bit
    VISCA data nibble; this command's byte values are NOT restricted to the low-nibble-only
    (`0x0`-`0xF` treated as "0-15" flat scale) convention used by zoom/focus/pan-tilt above — it
    is its own bespoke bit-packing, unrelated to the standard VISCA "4 significant bits per byte"
    multi-byte-value idiom. This is a useful negative control: the doc clearly distinguishes two
    different byte-packing schemes across two different command families, on two different pages.

### Where the multi-nibble VALUE convention is spelled out in words, elsewhere in this doc

No page in this set states in prose, generically, "a 16-bit VISCA value is transmitted as four
bytes, each carrying 4 significant bits in its low nibble, MSB first" as a named rule of the
protocol. The convention is only demonstrable by pattern-matching the repeated `0p 0q 0r 0s`
placeholder style across every multi-byte parameter in the Commands/Inquiry tables (Section 1
above), plus the worked Zoom Ratio/Position table in Section 4, which supplies concrete
before/after hex values for specific zoom ratios and therefore lets a reader reverse-engineer
the packing by example even without a stated formula.

## 2. ACK / Completion Messages

| Command | Command Message | Comments |
|---|---|---|
| ACK | `z0 4y FF` (y: Socket No.) | Returned when the command is accepted. |
| Completion | `z0 5y FF` (y: Socket No.) | Returned when the command has been executed. |

## 3. Error Messages

| Command | Command Message | Comments |
|---|---|---|
| Syntax Error | `z0 6y 02 FF` | Returned when the command format is different or when a command with illegal command parameters is accepted. |
| Command Buffer Full | `z0 6y 03 FF` | Indicates that two sockets are already being used (executing two commands) and the command could not be accepted when received. |
| Command Canceled | `z0 6y 04 FF` (y: Socket No.) | Returned when a command which is being executed in a socket specified by the cancel command is canceled. The completion message for the command is not returned. |
| No Socket | `z0 6y 05 FF` (y: Socket No.) | Returned when no command is executed in a socket specified by the cancel command, or when an invalid socket number is specified. |
| Command Not Executable | `z0 6y 41 FF` (y: Execution command Socket No. Inquiry command: 0) | Returned when a command cannot be executed due to current conditions. For example, when commands controlling the focus manually are received during auto focus. |

`z = Device address + 8` (stated directly beneath this table in the source).

## 4. Commands

### Call Camera Preset (standalone, own section on the page)

| Command | Command Packet | Comments |
|---|---|---|
| Call Camera Preset | `8x 01 04 3F 02 yy FF` | Call reserved preset, camera addr x. yy = hexadecimal value of camera preset. (Convert the decimal preset number to hex first.) See `Reserved-Presets.md`. |

### Main Commands table

| Command Set | Sub-command | Command Packet | Comments |
|---|---|---|---|
| AddressSet | Broadcast | `88 30 01 FF` | Address setting |
| IF_Clear | Broadcast | `88 01 00 01 FF` | I/F Clear |
| Command Cancel | — | `8x 2p FF` | p: Socket No. (=1 or 2) |
| CAM_Power | On | `8x 01 04 00 02 FF` | Power On/Off |
| CAM_Power | Off | `8x 01 04 00 03 FF` | |
| CAM_Zoom | Stop | `8x 01 04 07 00 FF` | |
| CAM_Zoom | Tele (Standard) | `8x 01 04 07 02 FF` | |
| CAM_Zoom | Wide (Standard) | `8x 01 04 07 03 FF` | |
| CAM_Zoom | Tele (Variable) | `8x 01 04 07 2p FF` | p: 0 (Low) to 7 (High) |
| CAM_Zoom | Wide (Variable) | `8x 01 04 07 3p FF` | p: 0 (Low) to 7 (High) (inferred shared with Tele row above; doc gives the range once) |
| CAM_Zoom | Direct | `8x 01 04 47 0p 0q 0r 0s FF` | p,q,r,s: Zoom Position |
| CAM_Zoom | Absolute Position | `8x 01 04 47 0t 0p 01 04 0s FF` | t: speed 0-7; p,q,r,s: Zoom Position (packet as printed in source — see Gaps note below, this row's fixed bytes `01 04` sit where `0q 0r` would otherwise be, and the doc does not explain the discrepancy) |
| CAM_Focus | Stop | `8x 01 04 08 00 FF` | |
| CAM_Focus | Far (Standard) | `8x 01 04 08 02 FF` | |
| CAM_Focus | Near (Standard) | `8x 01 04 08 03 FF` | |
| CAM_Focus | Far (Variable) | `8x 01 04 08 2p FF` | p: 0 (Low) to 7 (High) |
| CAM_Focus | Near (Variable) | `8x 01 04 08 3p FF` | |
| CAM_Focus | Direct | `8x 01 04 48 0p 0q 0r 0s FF` | p,q,r,s: Focus Position |
| CAM_Focus | Auto Focus | `8x 01 04 38 02 FF` | AF On/Off |
| CAM_Focus | Manual Focus | `8x 01 04 38 03 FF` | |
| CAM_Focus | Auto/Manual | `8x 01 04 38 10 FF` | |
| CAM_Focus | One Push Trigger | `8x 01 04 18 01 FF` | One Push AF Trigger |
| CAM_ZoomFocus | Direct | `8x 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF` | p,q,r,s: Zoom Position; t,u,v,w: Focus Position |
| CAM_WB | Auto | `8x 01 04 35 00 FF` | Normal Auto |
| CAM_WB | Indoor | `8x 01 04 35 01 FF` | Indoor Mode |
| CAM_WB | Outdoor | `8x 01 04 35 02 FF` | Outdoor Mode |
| CAM_WB | One Push WB | `8x 01 04 35 03 FF` | One Push WB Mode |
| CAM_WB | Manual | `8x 01 04 35 05 FF` | Manual Control Mode |
| CAM_WB | One Push Trigger | `8x 01 04 10 05 FF` | One Push WB Trigger |
| CAM_RGain | Reset | `8x 01 04 03 00 FF` | Manual Control of R Gain |
| CAM_RGain | Up | `8x 01 04 03 02 FF` | |
| CAM_RGain | Down | `8x 01 04 03 03 FF` | |
| CAM_RGain | Direct | `8x 01 04 43 00 00 0p 0q FF` | p,q: R Gain |
| CAM_BGain | Reset | `8x 01 04 04 00 FF` | Manual Control of B Gain |
| CAM_BGain | Up | `8x 01 04 04 02 FF` | |
| CAM_BGain | Down | `8x 01 04 04 03 FF` | |
| CAM_BGain | Direct | `8x 01 04 44 00 00 0p 0q FF` | p,q: B Gain |
| CAM_AE | Full Auto | `8x 01 04 39 00 FF` | Automatic Exposure mode |
| CAM_AE | Manual | `8x 01 04 39 03 FF` | Manual Control mode |
| CAM_AE | Shutter Priority | `8x 01 04 39 0A FF` | Shutter Priority Automatic Exposure mode |
| CAM_AE | Iris Priority | `8x 01 04 39 0B FF` | Iris Priority Automatic Exposure mode |
| CAM_AE | Bright | `8x 01 04 39 0D FF` | Bright Mode (Manual control) |
| CAM_Shutter | Reset | `8x 01 04 0A 00 FF` | Shutter Setting |
| CAM_Shutter | Up | `8x 01 04 0A 02 FF` | |
| CAM_Shutter | Down | `8x 01 04 0A 03 FF` | |
| CAM_Shutter | Direct | `8x 01 04 4A 00 00 0p 0q FF` | p,q: Shutter Position |
| CAM_Iris | Reset | `8x 01 04 0B 00 FF` | Iris Setting |
| CAM_Iris | Up | `8x 01 04 0B 02 FF` | |
| CAM_Iris | Down | `8x 01 04 0B 03 FF` | |
| CAM_Iris | Direct | `8x 01 04 4B 00 00 0p 0q FF` | p,q: Iris Position |
| CAM_Gain | Reset | `8x 01 04 0C 00 FF` | Gain Setting |
| CAM_Gain | Up | `8x 01 04 0C 02 FF` | |
| CAM_Gain | Down | `8x 01 04 0C 03 FF` | |
| CAM_Gain | Direct | `8x 01 04 4C 00 00 0p 0q FF` | p,q: Gain Position |
| CAM_Bright | Reset | `8x 01 04 0D 00 FF` | Bright Setting |
| CAM_Bright | Up | `8x 01 04 0D 02 FF` | |
| CAM_Bright | Down | `8x 01 04 0D 03 FF` | |
| CAM_Bright | Direct | `8x 01 04 4D 00 00 0p 0q FF` | p,q: Bright Position |
| CAM_ExpComp | On | `8x 01 04 3E 02 FF` | Exposure Compensation On/Off |
| CAM_ExpComp | Off | `8x 01 04 3E 03 FF` | |
| CAM_ExpComp | Reset | `8x 01 04 0E 00 FF` | Exposure Compensation Amount Setting |
| CAM_ExpComp | Up | `8x 01 04 0E 02 FF` | |
| CAM_ExpComp | Down | `8x 01 04 0E 03 FF` | |
| CAM_ExpComp | Direct | `8x 01 04 4E 00 00 0p 0q FF` | p,q: ExpComp Position |
| CAM_Backlight | On | `8x 01 04 33 02 FF` | Back Light Compensation ON/OFF |
| CAM_Backlight | Off | `8x 01 04 33 03 FF` | |
| CAM_Memory | Reset | `8x 01 04 3F 00 pp FF` | pp: Memory Number (=0 to 255). Corresponds to 0 to 255 on the Remote. |
| CAM_Memory | Set | `8x 01 04 3F 01 pp FF` | |
| CAM_Memory | Recall | `8x 01 04 3F 02 pp FF` | |
| Freeze | Freeze On | `8x 01 04 62 02 FF` | Freeze On Immediately |
| Freeze | Freeze Off | `8x 01 04 62 03 FF` | Freeze Off Immediately |
| Freeze | Preset Freeze On | `8x 01 04 62 22 FF` | Freeze On When Running Preset |
| Freeze | Preset Freeze Off | `8x 01 04 62 23 FF` | Freeze Off When Running Preset |
| IR_Receive | On | `8x 01 06 08 02 FF` | IR receiver On/Off |
| IR_Receive | Off | `8x 01 06 08 03 FF` | |
| Pan-tiltDrive | Up | `8x 01 06 01 VV WW 03 01 FF` | VV: Pan speed 0x01 (low) to 0x18 (high) |
| Pan-tiltDrive | Down | `8x 01 06 01 VV WW 03 02 FF` | |
| Pan-tiltDrive | Left | `8x 01 06 01 VV WW 01 03 FF` | |
| Pan-tiltDrive | Right | `8x 01 06 01 VV WW 02 03 FF` | WW: Tilt speed 0x01 (low) to 0x14 (high) |
| Pan-tiltDrive | Up Left | `8x 01 06 01 VV WW 01 01 FF` | |
| Pan-tiltDrive | Up Right | `8x 01 06 01 VV WW 02 01 FF` | |
| Pan-tiltDrive | Down Left | `8x 01 06 01 VV WW 01 02 FF` | YYYY: pan absolute position: 1 angle = 14.4 (doc's note, attached to this row) |
| Pan-tiltDrive | Down Right | `8x 01 06 01 VV WW 02 02 FF` | ZZZZ: tilt absolute position: 1 angle = 14.4 (doc's note, attached to this row) |
| Pan-tiltDrive | Stop | `8x 01 06 01 VV WW 03 03 FF` | |
| Pan-tiltDrive | Absolute Position | `8x 01 06 02 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF` | VV: pan speed 1-0x18; WW: tilt speed 1-0x14 |
| Pan-tiltDrive | Relative Position | `8x 01 06 03 VV WW 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF` | |
| Pan-tiltDrive | Home | `8x 01 06 04 FF` | |
| Pan-tiltDrive | PTZ Correction | `8x 01 06 05 FF` | Resets the PTZ head position |
| Pan-tiltLimitSet | Limit Set | `8x 01 06 07 00 0W 0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF` | W: 1 Up Right, 0: Down Left; YYYY: Pan Limit Position; ZZZZ: Tilt Position |
| CAM_MountMode | Stand | `8x 01 04 A4 02 FF` | Inverted video and PTZ control off. **Note: IV-CAM-P12 and IV-CAM-P20 only.** |
| CAM_MountMode | Ceiling | `8x 01 04 A4 03 FF` | Inverted video and PTZ control on. **Note: IV-CAM-P12 and IV-CAM-P20 only.** |

Notes copied verbatim on the "1 angle = 14.4" fragments: the source table places these two
fragments as the Comments-column text for the "Down Left" and "Down Right" rows respectively,
immediately to the right of the Stop-adjacent rows — this reads as a table-formatting artifact
in the source (the note plainly belongs to the Absolute/Relative Position rows below, which are
the ones that actually carry `YYYY`/`ZZZZ` parameters) rather than a claim about Down-Left/
Down-Right specifically. Reported as seen, byte-for-byte, with this caveat rather than silently
"fixed."

## 5. Inquiry Commands

| Inquiry Command | Command Packet | Inquiry Packet | Comments |
|---|---|---|---|
| CAM_PowerInq | `8x 09 04 00 FF` | `y0 50 02 FF` | On |
| CAM_PowerInq | | `y0 50 03 FF` | Off (Standby) |
| CAM_PowerInq | | `y0 50 04 FF` | Internal power circuit error |
| CAM_ZoomPosInq | `8x 09 04 47 FF` | `y0 50 0p 0q 0r 0s FF` | p,q,r,s: Zoom Position |
| CAM_FocusModeInq | `8x 09 04 38 FF` | `y0 50 02 FF` | Auto Focus |
| CAM_FocusModeInq | | `y0 50 03 FF` | Manual Focus |
| CAM_FocusPosInq | `8x 09 04 48 FF` | `y0 50 0p 0q 0r 0s FF` | p,q,r,s: Focus Position |
| CAM_WBModeInq | `8x 09 04 35 FF` | `y0 50 00 FF` | Auto |
| CAM_WBModeInq | | `y0 50 01 FF` | In Door |
| CAM_WBModeInq | | `y0 50 02 FF` | Out Door |
| CAM_WBModeInq | | `y0 50 03 FF` | One Push WB |
| CAM_WBModeInq | | `y0 50 05 FF` | Manual |
| CAM_RGainInq | `8x 09 04 43 FF` | `y0 50 00 00 0p 0q FF` | p,q: R Gain |
| CAM_BGainInq | `8x 09 04 44 FF` | `y0 50 00 00 0p 0q FF` | p,q: B Gain |
| CAM_AEModeInq | `8x 09 04 39 FF` | `y0 50 00 FF` | Full Auto |
| CAM_AEModeInq | | `y0 50 03 FF` | Manual |
| CAM_AEModeInq | | `y0 50 0A FF` | Shutter Priority |
| CAM_AEModeInq | | `y0 50 0B FF` | Iris Priority |
| CAM_AEModeInq | | `y0 50 0D FF` | Bright |
| CAM_ShutterPosInq | `8x 09 04 4A FF` | `y0 50 00 00 0p 0q FF` | p,q: Shutter Position |
| CAM_IrisPosInq | `8x 09 04 4B FF` | `y0 50 00 00 0p 0q FF` | p,q: Iris Position |
| CAM_GainPosInq | `8x 09 04 4C FF` | `y0 50 00 00 0p 0q FF` | p,q: Gain Position |
| CAM_BrightPosInq | `8x 09 04 4D FF` | `y0 50 00 00 0p 0q FF` | p,q: Bright Position |
| CAM_ExpCompModeInq | `8x 09 04 3E FF` | `y0 50 02 FF` | On |
| CAM_ExpCompModeInq | | `y0 50 03 FF` | Off |
| CAM_ExpCompPosInq | `8x 09 04 4E FF` | `y0 50 00 00 0p 0q FF` | p,q: ExpComp Position |
| CAM_BacklightModeInq | `8x 09 04 33 FF` | `y0 50 02 FF` | On |
| CAM_BacklightModeInq | | `y0 50 03 FF` | Off |
| CAM_MemoryInq | `8x 09 04 3F FF` | `y0 50 0p FF` | p: Memory number last operated |
| CAM_VersionInq | `8x 09 00 02 FF` | `y0 50 00 01 mn pq rs tu vw FF` | m,n,p,q: Model Code; r,s,t,u: ROM version; v,w: Socket Number |
| VideoSystemInq | `8x 09 06 23 FF` | `y0 50 00 FF` | 1920x1080i/60, 60 Hz system |
| VideoSystemInq | | `y0 50 01 FF` | 1920x1080p/30, 60 Hz system |
| VideoSystemInq | | `y0 50 02 FF` | 1280x720p/60, 60 Hz system |
| VideoSystemInq | | `y0 50 03 FF` | 1280x720p/30, 60 Hz system |
| VideoSystemInq | | `y0 50 07 FF` | 1920x1080p/60, 60 Hz system |
| VideoSystemInq | | `y0 50 08 FF` | 1920x1080i/50, 50 Hz system |
| VideoSystemInq | | `y0 50 09 FF` | 1920x1080p/25, 50 Hz system |
| VideoSystemInq | | `y0 50 0A FF` | 1280x720p/50, 50 Hz system |
| VideoSystemInq | | `y0 50 0B FF` | 1280x720p/25, 50 Hz system |
| VideoSystemInq | | `y0 50 0F FF` | 1920x1080p/50, 50 Hz system |
| IR_ReceiveInq | `8x 09 06 08 FF` | `y0 50 02 FF` | On |
| IR_ReceiveInq | | `y0 50 03 FF` | Off |
| Pan-tiltMaxSpeedInq | `8x 09 06 11 FF` | `y0 50 ww zz FF` | ww = Pan Max Speed; zz = Tilt Max Speed |
| Pan-tiltPosInq | `8x 09 06 12 FF` | `y0 50 0w 0w 0w 0w 0z 0z 0z 0z FF` | wwww = Pan Position; zzzz = Tilt Position |
| Pan-tiltModeInq | `8x 09 06 10 FF` | `y0 50 pq rs FF` | p,q,r,s: Pan/Tilt Status |
| CAM_TrackingInq | `8x 09 08 01 FF` | `y0 50 02 FF` | Checks if tracking is active |
| CAM_TrackingInq | | `y0 50 03 FF` | Checks if tracking is paused |
| CAM_MountModeInq | `8x 09 04 A4 FF` | `y0 50 02 FF` | Stand |
| CAM_MountModeInq | `8x 09 04 A4 FF` | `y0 50 03 FF` | Ceiling |

(The source table literally repeats the `8x 09 04 A4 FF` command packet on both CAM_MountModeInq
rows rather than leaving it blank the second time, unlike every other multi-reply inquiry above —
reproduced faithfully.)

## 6. Zoom Ratio / Position (CAM_Zoom)

Heading in source: "Zoom Ratio / Position (CAM_Zoom) — (CAM_Zoom Direct – p,q,r,s Zoom Position)".
Two tables are given, one per lens variant, mapping optical zoom ratio to the 4-nibble zoom
position value used in `CAM_Zoom Direct` / `CAM_ZoomFocus Direct` / `CAM_ZoomPosInq`. **Both the
P20 and I20 spec pages list a 20x optical zoom lens** (`IV-CAM-P20-Specifications.md`,
`IV-CAM-I20-Specifications.md`), so the "20x Zoom" column below is the one that applies to the
two cameras in scope for this experiment; the "12x Zoom" table is left in verbatim because the
source presents both without saying which camera model uses which — see Gaps.

### 12x Zoom

| Optical Zoom Ratio | Zoom Position (hex) |
|---|---|
| 1x | 0000 |
| 2x | 1982 |
| 3x | 24E2 |
| 4x | 2BC9 |
| 5x | 3099 |
| 6x | 343D |
| 7x | 3724 |
| 8x | 3988 |
| 9x | 3B8B |
| 10x | 3D43 |
| 11x | 3EBB |
| 12x | 4000 |

### 20x Zoom

| Optical Zoom Ratio | Zoom Position (hex) |
|---|---|
| 1x | 0000 |
| 2x | 1851 |
| 3x | 22BE |
| 4x | 28F6 |
| 5x | 2D45 |
| 6x | 3086 |
| 7x | 3320 |
| 8x | 3549 |
| 9x | 371E |
| 10x | 38B3 |
| 11x | 3A12 |
| 12x | 3B42 |
| 13x | 3C47 |
| 14x | 3D25 |
| 15x | 3DDF |
| 16x | 3E7B |
| 17x | 3EFB |
| 18x | 3F64 |
| 19x | 3FBA |
| 20x | 4000 |

Observations (derived, not stated by the doc):
- Both tables run from hex `0000` (1x / no zoom) to hex `4000` (max optical zoom), i.e. the
  4-nibble zoom-position value spans a fixed 0x0000-0x4000 range regardless of the lens' optical
  ratio ceiling — the doc does not state this as a rule, it is only visible by comparing the two
  tables' endpoints.
  - `0x4000` = 16384 decimal.
- The mapping from ratio to position is non-linear (bigger jumps at low zoom ratios, smaller
  jumps as ratio increases) in both tables — consistent with a lens whose focal-length-to-motor-
  step curve is non-linear, but the doc supplies only the lookup table, not a formula.
- Each 4-hex-digit value here is exactly the four `p,q,r,s` nibbles from `CAM_Zoom Direct`
  concatenated in order (e.g. 20x Zoom "4x" = `28F6` corresponds to packet bytes
  `08 0F 06`... — no: see the worked check immediately below).

**Worked check against the CAM_Zoom Direct nibble convention (Section 1):** the Zoom Position
tables here give a plain 4-hex-digit value (e.g. `28F6`), but `CAM_Zoom Direct`'s packet is
`8x 01 04 47 0p 0q 0r 0s FF` — four SEPARATE bytes, each of which per the doc's own convention
carries one significant nibble prefixed with `0`. Splitting `28F6` into its four hex digits and
prefixing each with `0` gives the on-wire bytes `02 08 0F 06`. The doc does not spell out this
translation step anywhere on the VISCA-Commands page or in the Zoom Ratio/Position table's own
text — a reader has to combine the two tables/sections to derive it. This is exactly the kind of
"nibble-packing rule that must be inferred, not read directly" the experiment is testing for.

## 7. Exposure Comp (CAM_ExpComp)

Heading in source: "Exposure Comp (CAM_ExpComp) — (CAM_ExpComp Direct – p,q ExpComp Position)".

| ExpComp Position (hex, 1 byte as printed) | Compensation (EV) | Full 4-nibble value (hex, as printed) |
|---|---|---|
| 0E | +7 | 0000 |
| 0D | +6 | 1851 |
| 0C | +5 | 22BE |
| 0B | +4 | 28F6 |
| 0A | +3 | 2D45 |
| 09 | +2 | 3086 |
| 08 | +1 | 3320 |
| 07 | 0 | 3549 |
| 06 | -1 | 371E |
| 05 | -2 | 38B3 |
| 04 | -3 | 3A12 |
| 03 | -4 | 3B42 |
| 02 | -5 | 3C47 |
| 02 | -6 | 3D25 |
| 00 | -7 | 4000 |

Reproduced exactly as printed, including the apparent inconsistency: `CAM_ExpComp Direct`'s
packet (`8x 01 04 4E 00 00 0p 0q FF`) only carries a 2-nibble (`p,q`) parameter, matching this
table's first column — but the table's third column reuses the SAME 4-nibble hex values as the
20x Zoom Ratio table above, verbatim (`0000`, `1851`, `22BE`, `28F6`, `2D45`, `3086`, `3320`,
`3549`, `371E`, `38B3`, `3A12`, `3B42`, `3C47`, `3D25`, `4000`), one entry short (15 rows here vs
20 in the zoom table) and with a duplicated `-5`/`-6` row both showing `02`. This third column
looks like a copy/paste leftover from the Zoom Ratio table rather than a genuine ExpComp value
— flagged, not silently corrected, because it directly bears on how much to trust this doc set's
internal consistency. The first two columns (hex code / EV step) are internally coherent (14
steps in the header's own hex code column, -7 to +7 minus one, since 02 repeats) and match the
2-nibble `p,q` shape the command packet actually declares.

## 8. VISCA Lightbar Commands

Full page: `VISCA-Lightbar-Commands.md`. Command format: **`8x c1 ** ** ** ** ff`** (4 payload
bytes, one per lightbar segment; transport is VISCA over the same serial/TCP connection as the
main command set). Status-driven lightbar colors (fixed, not user-settable):

| Lightbar Color | Camera Status | VISCA Command |
|---|---|---|
| Full green | Intelligent camera function ON | `8x c1 0C 0C 0C 0C ff` |
| Half green | Camera output ON | `8x c1 00 0C 0C 00 ff` |
| Full yellow | Firmware update in progress | `8x c1 0F 0F 0F 0F ff` |
| Half red | Privacy Mode ON (camera output OFF) | `8x c1 01 0D 0D 01 ff` |

Common (user-settable) combinations — width x color x brightness:

| Width | Color | Brightness | VISCA Command |
|---|---|---|---|
| None | None | None | `8x c1 00 00 00 00 ff` |
| Full | Green | Bright | `8x c1 0C 0C 0C 0C ff` |
| Full | Green | Medium | `8x c1 08 08 08 08 ff` |
| Full | Green | Dim | `8x c1 04 04 04 04 ff` |
| Full | Yellow | Bright | `8x c1 0F 0F 0F 0F ff` |
| Full | Yellow | Medium | `8x c1 0B 0B 0B 0B ff` |
| Full | Yellow | Dim | `8x c1 07 07 07 07 ff` |
| Full | Red | Bright | `8x c1 0D 0D 0D 0D ff` |
| Full | Red | Medium | `8x c1 09 09 09 09 ff` |
| Full | Red | Dim | `8x c1 05 05 05 05 ff` |
| Half | Green | Bright | `8x c1 00 0C 0C 00 ff` |
| Half | Green | Medium | `8x c1 00 08 08 00 ff` |
| Half | Green | Dim | `8x c1 00 04 04 00 ff` |
| Half | Yellow | Bright | `8x c1 03 0F 0F 03 ff` |
| Half | Yellow | Medium | `8x c1 03 0B 0B 03 ff` |
| Half | Yellow | Dim | `8x c1 03 07 07 03 ff` |
| Half | Red | Bright | `8x c1 01 0D 0D 01 ff` |
| Half | Red | Medium | `8x c1 01 09 09 01 ff` |
| Half | Red | Dim | `8x c1 01 05 05 01 ff` |

Segment geometry (verbatim): "IV-CAM-P12 and IV-CAM-P20 series cameras: The lightbar contains
four lightbar segments with 4 lights each, totaling 16 lights." / "IV-CAM-I12-B and IV-CAM-I20
series cameras: The lightbar contains two outer segments with 4 lights each and two inner
segments with 3 lights each, totaling 14 lights." — **directly names both P20 and I20.**

Bespoke bit-packing for custom colors (see Section 1 for the doc's own worked example): each
payload byte = 2-bit brightness field (`00` off, `01` dim, `10` medium, `11` bright) packed with
a 2-bit color field (`00` green, `01` red, `11` yellow — note `10` is unused/undefined in the
doc) into one 4-bit-per-byte-pair binary string, then that binary is converted to hex per byte.

## 9. VISCA Intelligent Switching Commands

Full page: `VISCA-Intelligent-Switching-Commands.md`. Transport: "controlled using the VISCA
protocol through a TCP connection" (serial not mentioned for this command family, unlike the
main and lightbar sets). Placeholder key given by the doc:

| Placeholder Letter | Definition |
|---|---|
| X | Camera Address |
| Z | Camera ID (2, 3, 4, 5) |
| W | IP Address (each W represents one digit of the IP address in hexadecimal) |

| Command | Command Packet | Ack Response | Comments |
|---|---|---|---|
| Set Camera (IP Address) | `8x c2 01 09 0Z 0W 0W 0W 0W 0W 0W 0W 0W ff` | `Y0 41 FF` `Y0 51 FF` | Sets the camera IP to be used for Intelligent Switching |
| Get Camera | `8x c2 09 09 0Z ff` | `Y0 50 0Z 0W 0W 0W 0W 0W 0W 0W 0W ff` | Returns the camera IP used for Intelligent Switching |
| Clear All Cameras Set | `8x c2 01 0A 00 ff` | `Y0 41 FF` `Y0 51 FF` | Clears all cameras set for Intelligent Switching |
| Call Camera Output (1/2/3/4/5) | `8x c2 01 08 0Z ff` | `Y0 41 FF` `Y0 51 FF` | Calls the camera output during Intelligent Switching |
| Resume Intelligent Switching | `8x c2 01 08 00 ff` | `Y0 41 FF` `Y0 51 FF` | Resumes Intelligent Switching |
| Pause Intelligent Switching | `8x c2 01 0B 00 ff` | `Y0 41 FF` `Y0 51 FF` | Pauses Intelligent Switching |
| Get Output | `8x C2 09 08 FF` | see below | Returns the camera output |
| Check Connection Status (2/3/4/5) | `8x c2 09 0d 0Z ff` | Disconnect: `Y0 50 00 00 FF`; Connect: `Y0 50 00 01 FF` | Returns the connection status of the camera and Intelligent Switching |

`Get Output` reply detail (verbatim, camera IDs 1-5):
- Intelligent Switching On: Camera 1 `Y0 50 01 01 FF`; Camera 2 `Y0 50 01 02 FF`; Camera 3
  `Y0 50 01 03 FF`; Camera 4 `Y0 50 01 04 FF`; Camera 5 `Y0 50 01 05 FF`.
- Intelligent Switching Off: Camera 1 `Y0 50 00 01 FF`; Camera 2 `Y0 50 00 02 FF`; Camera 3
  `Y0 50 00 03 FF`; Camera 4 `Y0 50 00 04 FF`; Camera 5 `Y0 50 00 05 FF`.

Note the placeholder-letter mismatch preserved verbatim: the key table defines `Z` (upper-case)
as the Camera ID, but every command packet in the list below it writes the nibble-form as `0Z`
uniformly, while the ack/reply header uses `Y0` (upper-case Y) whereas the rest of this document
set's replies use lower-case `y0` — reported as printed, not normalized.

## 10. Reserved Presets (VISCA path: Call Camera Preset, Section 4 above)

See `Reserved-Presets.md` for the full table. Highlights relevant to VISCA preset-calling
(`8x 01 04 3F 02 yy FF`) and model scope:

| Preset | Function | Cameras (verbatim) |
|---|---|---|
| 0 | Home Shot | IV-CAM-I12, IV-CAM-I20, and IV-CAM-I12D-B |
| 1 | Tracking Shot | IV-CAM-I12, IV-CAM-I20, and IV-CAM-I12D-B |
| 80 | Start Tracking | IV-CAM-I12, IV-CAM-I20, and IV-CAM-I12D-B |
| 81 | Pause Tracking | IV-CAM-I12, IV-CAM-I20, and IV-CAM-I12D-B |
| 82 | Start Group Tracking | IV-CAM-I20 |
| 83 | Pause Group Tracking | IV-CAM-I20 |
| 95 | OSD Menu Toggle | All cameras |
| 99 | Reboot | All cameras |
| 101-104 | Preset Zone 1-4 | IV-CAM-I20 |
| 105-108 | Tracking Profile 1-4 | IV-CAM-I20 |

(Presets 84-89 are I12/I12D-only and out of scope for I20/P20; omitted here, present in full in
`Reserved-Presets.md`.) **No P20-specific reserved presets are listed anywhere on this page** —
P20 gets only the generic ones (95 OSD Toggle, 99 Reboot) plus whatever plain numbered presets
(0-255 via `CAM_Memory`/`Call Camera Preset`) a user sets themselves; see Gaps.

## 11. Zoom / pan-tilt facts drawn from the Specifications pages (cross-reference, not VISCA-Commands page itself)

From `IV-CAM-P20-Specifications.md` and `IV-CAM-I20-Specifications.md` (both pages, identical
figures unless noted):
- Optical Zoom: 20x (both). Focal Length: F=5.2-94mm (both).
- Field of View: P20 "Horizontal: 56.45°" (one FOV, since P20 has a single PTZ lens). I20 gives
  two: "Field of View (PTZ): Horizontal: 56.45°" and "Field of View (Reference): Horizontal: 104°
  (changes based on camera mode)" — the I20 has both a PTZ lens and a separate wide-angle
  reference camera used for tracking; P20 does not.
- Pan/Tilt Angle: "Pan: -130° — 130°, Tilt: -30° — 90°" (both).
- Pan/Tilt Speed: "Pan: 0.2° — 90°/s, Tilt: 0.2° — 70°/s" (both).
- Presets: "Up to 256 configurable presets" (both) — matches `CAM_Memory`'s `pp` byte range (0
  to 255) exactly.
- Control Protocol: "VISCA/TCP, VISCA/UDP, PELCO-D, PELCO-P, ONVIF" (both) — note VISCA/UDP is
  listed here even though the VISCA-Commands page's prose only mentions "serial (RS-232/RS-485)
  or TCP" as the two transports; UDP is not mentioned anywhere in the VISCA-Commands,
  VISCA-Lightbar-Commands, or VISCA-Intelligent-Switching-Commands pages. Flagged as a gap.
- Serial: "RS-232, RS-485" (both), matching the VISCA-Commands page's transport prose exactly.

This lets us sanity-check the doc's own "1 angle = 14.4" fragment attached to the Pan-tiltDrive
table (Section 4): the spec page's Pan range is -130° to 130° (260° total). If the `YYYY`
absolute-position nibble value's unit really is "1 unit = 1/14.4 degree" as the fragment implies
(reading "1 angle=14.4" as "1 degree = 14.4 position units"), then 260° would span roughly
260 x 14.4 ≈ 3744 position units — well within a 4-nibble (0-65535) range, and also comfortably
inside the signed range needed for a value centered near mid-scale. This is presented as an
arithmetic sanity check only; the doc does not state a zero point or sign convention for `YYYY`/
`ZZZZ` anywhere, so the check does not by itself confirm the formula, only that it is not
obviously impossible.

## Gaps / things this documentation does NOT give us

1. No "Wake" VISCA command byte sequence anywhere in this doc set, despite the VISCA-Commands
   page's own note ("Send the wake command to the camera before sending any other VISCA
   commands") — confirms the earlier findings/08 pattern (Wake undocumented while Sleep-like
   behavior — here Privacy Mode toggling — is at least named) generalizes to this camera family
   too, on the DOCUMENTATION side; we have not checked the driver JSON for a corresponding
   declared Wake transformation/command in this pass.
2. `CAM_Zoom Absolute Position`'s packet (`8x 01 04 47 0t 0p 01 04 0s FF`) does not fit the
   4-nibble-parameter pattern used everywhere else — two of its middle bytes are literal `01 04`
   rather than `0q 0r`, and the doc gives no separate explanation for why an "Absolute Position"
   zoom command needs a speed nibble `t` plus only two free position nibbles `p`/`s` instead of
   four. Left as printed; not resolved.
3. The Exposure Comp table's third column duplicating the 20x Zoom table's values (Section 7) is
   unexplained and looks like a documentation authoring error, not a deliberate cross-reference.
4. VISCA/UDP is named on both spec pages as a supported control protocol but never appears in
   the VISCA-Commands, VISCA-Lightbar-Commands, or VISCA-Intelligent-Switching-Commands pages'
   own transport prose (which only ever say "serial ... or TCP", or "TCP" alone for Intelligent
   Switching).
5. No page in this doc set gives a byte-level definition, table, or worked example specifically
   for `ViscaAssemble2LowerNibbles` (the I20-only undeclared transformation named in the task
   brief) by that name or an equivalent generic description of "assemble two 4-bit nibbles into
   one byte" as a distinct, named operation — the nibble-assembly behavior can only be inferred
   from the pattern in Section 1 and the worked Lightbar example, not read off a dedicated
   explanation.
6. No dedicated "P20 reserved presets" list — Reserved-Presets.md's table names cameras
   individually per row and P20 never appears; whether P20 has additional reserved presets is
   simply unaddressed, not stated as "P20 has none."
7. `Pan-tiltMaxSpeedInq`'s reply is documented as one byte per axis (`ww`, `zz`) while the max
   speeds referenced in Pan-tiltDrive rows are given as ranges up to `0x18` (pan) / `0x14` (tilt)
   — consistent, but the doc never explicitly cross-references the two.
