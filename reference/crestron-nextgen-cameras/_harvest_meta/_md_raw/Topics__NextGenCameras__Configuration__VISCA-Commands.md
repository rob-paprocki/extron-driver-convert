     | IV-CAM Series Manual               

[Skip To Main Content](#)

Account

Settings

* * *

Logout

[](http://www.crestron.com)

*   placeholder

Account

Settings

* * *

Logout

Filter:

*   All Files

Submit Search

# VISCA Commands

Crestron 1 Beyond cameras can be controlled using the VISCA protocol through either a serial (RS‑232 / RS‑485) or TCP connection. By default, the port for TCP control is set to 5500. For serial communication, make sure the baud rate of the controller is set to 9600 bps. Below is a comprehensive list of VISCA commands that can be used to control the cameras.

note: Cameras cannot use any VISCA commands if they are in Privacy Mode. Send the wake command to the camera before sending any other VISCA commands to the camera.

## Call Camera Preset

To call a reserved preset, convert the camera preset value to hexadecimal. Then, call the following command:

  

Command

Command Packet

Comments

Call Camera Preset

8x 01 04 3F 02 yy FF

Call reserved preset, camera addr x.  
yy = hexadecimal value of camera preset.  

For more information on reserved presets, refer to [Reserved Presets](Reserved-Presets.htm).

## ACK / Completion Messages

  

Command

Command Message

Comments

ACK

z0 4y FF  
(y:Socket No.)

Returned when the command is accepted.

Completion

z0 5y FF  
(y:Socket No.)

Returned when the command has been executed.

## Error Messages

  

Command

Command Message

Comments

Syntax Error

z0 6y 02 FF

Returned when the command format is different or when a command with illegal command parameters is accepted.

Command Buffer Full

z0 6y 03 FF

Indicates that two sockets are already being used (executing two commands) and the command could not be accepted when received.

Command Canceled

z0 6y 04 FF  
(y:Socket No.)

Returned when a command which is being executed in a socket specified by the cancel command is canceled. The completion message for the command is not returned.

No Socket

z0 6y 05 FF  
(y:Socket No.)

Returned when no command is executed in a socket specified by the cancel command, or when an invalid socket number is specified.

Command Not Executable

z0 6y 41 FF  
(y:Execution command Socket No. Inquiry command:0)

Returned when a command cannot be executed due to current conditions. For example, when commands controlling the focus manually are received during auto focus.

z = Device address + 8

## Commands

   

Command Set

Command

Command Packet

Comments

AddressSet

Broadcast

88 30 01 FF

Address setting

IF\_Clear

Broadcast

88 01 00 01 FF

I/F Clear

Command Cancel

 

8x 2p FF

p: Socket No. (=1 or 2)

CAM\_Power

On

8x 01 04 00 02 FF

Power On/Off

Off

8x 01 04 00 03 FF

CAM\_Zoom

Stop

8x 01 04 07 00 FF

 

Tele(Standard)

8x 01 04 07 02 FF

Wide(Standard)

8x 01 04 07 03 FF

Tele(Variable)

8x 01 04 07 2p FF

p: 0(Low)to 7 (High)

Wide(Variable)

8x 01 04 07 3p FF

Direct

8x 01 04 47 0p 0q 0r 0s FF

p,q,r,s: Zoom Position

Absolute Position

8x 01 04 47 0t 0p 01 04 0s FF

t:speed 0 - 7; p,q,r,s: Zoom Position

CAM\_Focus

Stop

8x 01 04 08 00 FF

 

Far(Standard)

8x 01 04 08 02 FF

Near(Standard)

8x 01 04 08 03 FF

Far(Variable)

8x 01 04 08 2p FF

p: 0 (Low) to 7 (High)

Near(Variable)

8x 01 04 08 3p FF

Direct

8x 01 04 48 0p 0q 0r 0s FF

p,q,r,s: Focus Position

Auto Focus

8x 01 04 38 02 FF

AF On/Off

Manual Focus

8x 01 04 38 03 FF

Auto/Manual

8x 01 04 38 10 FF

One Push Trigger

8x 01 04 18 01 FF

One Push AF Trigger

CAM\_ZoomFocus

Direct

8x 01 04 47 0p 0q 0r 0s 0t 0u 0v 0w FF

p,q,r,s: Zoom Position t,u,v,w: Focus Position

CAM\_WB

Auto

8x 01 04 35 00 FF

Normal Auto

Indoor

8x 01 04 35 01 FF

Indoor Mode

Outdoor

8x 01 04 35 02 FF

Outdoor Mode

One Push WB

8x 01 04 35 03 FF

One Push WB Mode

Manual

8x 01 04 35 05 FF

Manual Control Mode

One Push Trigger

8x 01 04 10 05 FF

One Push WB Trigger

CAM\_RGain

Reset

8x 01 04 03 00 FF

Manual Control of R Gain

Up

8x 01 04 03 02 FF

Down

8x 01 04 03 03 FF

Direct

8x 01 04 43 00 00 0p 0q FF

p,q: R Gain

CAM\_BGain

Reset

8x 01 04 04 00 FF

Manual Control of B Gain

Up

8x 01 04 04 02 FF

Down

8x 01 04 04 03 FF

Direct

8x 01 04 44 00 00 0p 0q FF

p,q: B Gain

CAM\_AE

Full Auto

8x 01 04 39 00 FF

Automatic Exposure mode

Manual

8x 01 04 39 03 FF

Manual Control mode

Shutter Priority

8x 01 04 39 0A FF

Shutter Priority Automatic Exposure mode

Iris Priority

8x 01 04 39 0B FF

Iris Priority Automatic Exposure mode

Bright

8x 01 04 39 0D FF

Bright Mode (Manual control)

CAM\_Shutter

Reset

8x 01 04 0A 00 FF

Shutter Setting

Up

8x 01 04 0A 02 FF

Down

8x 01 04 0A 03 FF

Direct

8x 01 04 4A 00 00 0p 0q FF

p,q: Shutter Position

CAM\_Iris

Reset

8x 01 04 0B 00 FF

Iris Setting

Up

8x 01 04 0B 02 FF

Down

8x 01 04 0B 03 FF

Direct

8x 01 04 4B 00 00 0p 0q FF

p,q: Iris Position

CAM\_Gain

Reset

8x 01 04 0C 00 FF

Gain Setting

Up

8x 01 04 0C 02 FF

Down

8x 01 04 0C 03 FF

Direct

8x 01 04 4C 00 00 0p 0q FF

p,q: Gain Position

CAM\_Bright

Reset

8x 01 04 0D 00 FF

Bright Setting

Up

8x 01 04 0D 02 FF

Down

8x 01 04 0D 03 FF

Direct

8x 01 04 4D 00 00 0p 0q FF

p,q: Bright Position

CAM\_ExpComp

On

8x 01 04 3E 02 FF

Exposure Compensation On/Off

Off

8x 01 04 3E 03 FF

Reset

8x 01 04 0E 00 FF

Exposure Compensation Amount Setting

Up

8x 01 04 0E 02 FF

Down

8x 01 04 0E 03 FF

Direct

8x 01 04 4E 00 00 0p 0q FF

p,q: ExpComp Position

CAM\_Backlight

On

8x 01 04 33 02 FF

Back Light Compensation ON/OFF

Off

8x 01 04 33 03 FF

CAM\_Memory

Reset

8x 01 04 3F 00 pp FF

pp: Memory Number (=0 to 255)  
Corresponds to 0 to 255 on the Remote.

Set

8x 01 04 3F 01 pp FF

Recall

8x 01 04 3F 02 pp FF

Freeze

Freeze On

8x 01 04 62 02 FF

Freeze On Immediately

Freeze Off

8x 01 04 62 03 FF

Freeze Off Immediately

Preset Freeze On

8x 01 04 62 22 FF

Freeze On When Running Preset

Preset Freeze Off

8x 01 04 62 23 FF

Freeze Off When Running Preset

IR\_Receive

On

8x 01 06 08 02 FF

IR receiver On/Off

Off

8x 01 06 08 03 FF

Pan‐tiltDrive

Up

8x 01 06 01 VV WW 03 01 FF

VV: Pan speed 0 x01 (low speed) to 0 x18  
(high speed)

Down

8x 01 06 01 VV WW 03 02 FF

Left

8x 01 06 01 VV WW 01 03 FF

Right

8x 01 06 01 VV WW 02 03 FF

WW: Tilt Speed 0 x 01 (low speed) to 0 x14  
(high speed)

Up Left

8x 01 06 01 VV WW 01 01 FF

Up Right

8x 01 06 01 VV WW 02 01 FF

Down Left

8x 01 06 01 VV WW 01 02 FF

YYYY: pan absolute position: 1 angle=14.4;

Down Right

8x 01 06 01 VV WW 02 02 FF

Stop

8x 01 06 01 VV WW 03 03 FF

ZZZZ: tilt absolute position: 1 angle=14.4;

Absolute Position

8x 01 06 02 VV WW  
0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF

vv indicates pan speed: 1-0x18  
ww indicates tilt speed: 1-0x14

Relative Position

8x 01 06 03 VV WW  
0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF

 

Home

8x 01 06 04 FF

 

PTZ Correction

8x 01 06 05 FF

Resets the PTZ head position

Pan‐tiltLimitSet

Limit Set

8x 01 06 07 00 0W  
0Y 0Y 0Y 0Y 0Z 0Z 0Z 0Z FF

W: 1 Up Right 0: Down Left  
YYYY: Pan Limit Position  
ZZZZ: Tilt Position

CAM\_MountMode  

note: IV-CAM-P12 and IV-CAM-P20 only.

Stand

8x 01 04 A4 02 FF

Inverted video and PTZ control off

Ceiling

8x 01 04 A4 03 FF

Inverted video and PTZ control on

## Inquiry Commands

   

Inquiry Command

Command Packet

Inquiry Packet

Comments

CAM\_PowerInq

8x 09 04 00 FF

y0 50 02 FF

On

y0 50 03 FF

Off (Standby)

y0 50 04 FF

Internal power circuit error

CAM\_ZoomPosInq

8x 09 04 47 FF

y0 50 0p 0q 0r 0s FF

p,q,r,s: Zoom Position

CAM\_FocusModeInq

8x 09 04 38 FF

y0 50 02 FF

Auto Focus

y0 50 03 FF

Manual Focus

CAM\_FocusPosInq

8x 09 04 48 FF

y0 50 0p 0q 0r 0s FF

p,q,r,s: Focus Position

CAM\_WBModeInq

8x 09 04 35 FF

y0 50 00 FF

Auto

y0 50 01 FF

In Door

y0 50 02 FF

Out Door

y0 50 03 FF

One Push WB

y0 50 05 FF

Manual

CAM\_RGainInq

8x 09 04 43 FF

y0 50 00 00 0p 0q FF

p,q: R Gain

CAM\_BGainInq

8x 09 04 44 FF

y0 50 00 00 0p 0q FF

p,q: B Gain

CAM\_AEModeInq

8x 09 04 39 FF

y0 50 00 FF

Full Auto

y0 50 03 FF

Manual

y0 50 0A FF

Shutter Priority

y0 50 0B FF

Iris Priority

y0 50 0D FF

Bright

CAM\_ShutterPosInq

8x 09 04 4A FF

y0 50 00 00 0p 0q FF

p,q: Shutter Position

CAM\_IrisPosInq

8x 09 04 4B FF

y0 50 00 00 0p 0q FF

p,q: Iris Position

CAM\_GainPosInq

8x 09 04 4C FF

y0 50 00 00 0p 0q FF

p,q: Gain Position

CAM\_BrightPosInq

8x 09 04 4D FF

y0 50 00 00 0p 0q FF

p,q: Bright Position

CAM\_ExpCompModeInq

8x 09 04 3E FF

y0 50 02 FF

On

y0 50 03 FF

Off

CAM\_ExpCompPosInq

8x 09 04 4E FF

y0 50 00 00 0p 0q FF

p,q: ExpComp Position

CAM\_BacklightModeInq

8x 09 04 33 FF

y0 50 02 FF

On

y0 50 03 FF

Off

CAM\_MemoryInq

8x 09 04 3F FF

y0 50 0p FF

p: Memory number last operated.

CAM\_VersionInq

8x 09 00 02 FF

y0 50 00 01

mn pq rs tu vw FF

m,n,p,q: Model Code

r,s,t,u: ROM version

v,w: Socket Number

VideoSystemInq

8x 09 06 23 FF

y0 50 00 FF

 

1920 x1080i/60

60 Hz system

y0 50 01 FF

 

1920 x1080p/30

60 Hz system

y0 50 02 FF

 

1280 x720p/60

60 Hz system

y0 50 03 FF

 

1280 x720p/30

60 Hz system

y0 50 07 FF

 

1920 x1080p/60

60 Hz system

y0 50 08 FF

 

1920 x1080i/50

50 Hz system

y0 50 09 FF

 

1920 x1080p/25

50 Hz system

y0 50 0A FF

 

1280 x720p/50

50 Hz system

y0 50 0B FF

 

1280 x 720p/25

50 Hz system

y0 50 0F FF

 

1920 x1080p/50

50 Hz system

IR\_Receive

8x 09 06 08 FF

y0 50 02 FF

On

y0 50 03 FF

Off

Pan‐tiltMaxSpeedI

8x 09 06 11 FF

y0 50 ww zz FF

ww = Pan Max Speed zz = Tilt Max Speed

Pan‐tiltPosInq

8x 09 06 12 FF

y0 50 0w 0w 0w 0w

0z 0z 0z 0z FF

wwww = Pan Position zzzz = Tilt Position

Pan‐tiltModeInq

8x 09 06 10 FF

y0 50 pq rs FF

p,q,r,s: Pan/Tilt Status

CAM\_TrackingInq

8x 09 08 01 FF

y0 50 02 FF

Checks if tracking is active

y0 50 03 FF

Checks if tracking is paused

CAM\_MountModeInq

8x 09 04 A4 FF

y0 50 02 FF

Stand

8x 09 04 A4 FF

y0 50 03 FF

Ceiling

### Zoom Ratio / Position (CAM\_Zoom)

(CAM\_Zoom Direct – p,q,r,s Zoom Position)

12x Zoom

 

Optical Zoom Ratio

Optical Zoom Ratio

1x

0000

2x

1982

3x

24E2

4x

2BC9

5x

3099

6x

343D

7x

3724

8x

3988

9x

3B8B

10x

3D43

11x

3EBB

12x

4000

20x Zoom

 

Optical Zoom Ratio

Optical Zoom Ratio

1x

0000

2x

1851

3x

22BE

4x

28F6

5x

2D45

6x

3086

7x

3320

8x

3549

9x

371E

10x

38B3

11x

3A12

12x

3B42

13x

3C47

14x

3D25

15x

3DDF

16x

3E7B

17x

3EFB

18x

3F64

19x

3FBA

20x

4000

### Exposure Comp (CAM\_ExpComp)

(CAM\_ExpComp Direct – p,q ExpComp Position)

  

0E

+7

0000

0D

+6

1851

0C

+5

22BE

0B

+4

28F6

0A

+3

2D45

09

+2

3086

08

+1

3320

07

0

3549

06

\-1

371E

05

\-2

38B3

04

\-3

3A12

03

\-4

3B42

02

\-5

3C47

02

\-6

3D25

00

\-7

4000

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [VISCA Commands](#VISCACommands)

*   [Call Camera Preset](#CallCameraPreset)
*   [ACK / Completion Messages](#ACKCompletionMessages)
*   [Error Messages](#ErrorMessages)
*   [Commands](#Commands)
*   [Inquiry Commands](#InquiryCommands)

*   [Zoom Ratio / Position (CAM\_Zoom)](#ZoomRatioPositionCAMZoom)
*   [Exposure Co