Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/On-Screen-Display(OSD)-Menu.htm

# On-Screen Display (OSD)

Crestron 1 Beyond cameras have an integrated On-Screen Display (OSD) menu where camera settings can be changed. To access the OSD menu, select **Menu** on the desired camera in the camera list.

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/SelectMenu.png)

The OSD menu is then displayed overlaid on the camera’s video feed.

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Menu/OSD Menu Controls.png)

Alternatively, the OSD menu can be accessed with the [IV-CAMA-REMOTE](https://crestron.com/model/6513217 "https://crestron.com/model/6513217") Crestron 1 Beyond IR Camera Remote. To access the OSD menu with the IR camera remote, press **Menu** on the remote.

## Menu Navigation

Use the navigation pad to navigate through the OSD menu. Select **Enter** to open a sub menu and select **Back** to exit the sub menu. Use the navigation pad to move up and down through the menus, and left and right to scroll through menu options. Refer to the table below for information on navigating through the OSD sub menus.

OSD Menu Options

   

Option

Sub Menu Options

Setting Range

Setting Description

Video

Sharpness

0 - 11

Adjust video sharpening.

Brightness

0 - 14

Adjust video brightness.

Contrast

0 - 14

Adjust video contrast.

Gamma

0 - 4

Adjust video gamma correction.

2DNR

0 - 7

2D Noise Reduction level.

3DNR

0 - 7

3D Noise Reduction level.

DRC

0 - 5

Dynamic Range Compression level.

Mirror

Off/On

Mirrors camera output.

Invert

Off/On

Inverts the PTZ camera video feed.

note: Only IV‑CAM‑P12 and IV‑CAM‑P20 cameras can be inverted.

Video Format

1080p30/29.97/25/60/59.94/50,  
720p60/59.94/50/

Adjust camera video output format.

note: SDI and HDMI video outputs only.

Exposure

Mode

Auto

Automatically adjust exposure.

Manual

Manually adjust exposure.

Shutter PRI

Shutter priority mode.

Iris PRI

Iris priority mode.

Bright

Brightness priority mode.

Anti-Flicker

OFF/50Hz /60Hz

Reduces flicker induced by 25p and 30p frame rates.

BLC

Off/On

Turn Back Light Compensation On or Off.

EXP Comp

Off/On

Turn exposure compensation On or Off.

\-7 - 7

Adjust the exposure compensation of the camera.

Gain

0 - 14

Adjust the gain of the camera.

Shutter

1/60 - 1/10000

Adjust the shutter speed of the camera.

Iris

F1.6 - F14, Close

Adjust the aperture of the camera.

REF Brightness

0 - 14

Adjust the reference camera's video brightness.

Color

Mode

Auto

Fully automatic white balance.

Manual

Fully manual white balance adjustment.

One Push

Trigger a one time white balance adjustment.

Static

Preset white balance adjustments

Profile

Cloudy

Static Color Mode presets.

Daylight

Fluorescent

Tungsten

Custom

R-Gain

0 - 16

Adjust the red color channel balance.

G-Gain

0 - 16

Adjust the green color channel balance.

B-Gain

0 - 16

Adjust the blue color channel balance.

WB Sens

Low/Medium/High

Adjust white balance sensitivity.

Saturation

0 - 14

Increase or decrease color saturation.

Hue

0 - 14

Increase or decrease video hue.

PTZ

Speed

1 - 7

Adjust the speed of camera movement.

AF Sens

Low/Medium/High

Adjusts the AutoFocus sensitivity

AF Area

Global/Center/Face  

note: Face AF Area is only available with p-series cameras.

Set the Auto-Focus area to be used:

*   **Global** uses the full PTZ image provided.
    
*   **Center** focuses from the center of lens first.
    
*   **Face** prioritizes faces within the scene.
    

PTZ Trig AF

Off/On

Auto-focus after moving the camera.

Preset Freeze

Off/On

Turn Preset Freeze On or Off.

Auto Privacy

Off/On

Turn automatic Privacy Mode On or Off

Home Shot

Off/On

Enables Preset 0 (Home Shot) to be called upon camera wake action  

Digital Zoom

Off/On

Turn Digital Zoom On or Off.

Limit

x1 - x16

Adjust the Digital Zoom limit.

Calibrate

Confirm

When selected, the camera will perform focus calibration. Refer to [Focus Calibration](#Focus) for more information about focus calibration.

System

Address

1 - 7

Choose the camera address for serial and IP communication.

Protocol

VISCA

Choose the protocol for serial and IP communication.

PELCO-D

PELCO-P

Baudrate

2400 - 38400

Set the baud rate for the serial port.

Disable LED

Off/On

Turn the camera LED On or Off.

Group Track

Off/On

Turn Group Tracking On or Off.

note: IV-CAM-I20 only.

Track Mode

Presenter/Group

Set the IV-CAM-I12 to Presenter Track or Group Frame.

IR

Off/On

Turn the IR receiver On or Off.

note: IV-CAM-I12 only.

IR Address

1/2/3

Set the IR address for the camera.

MJPEG Only

Off/On

Turn MJPEG Only mode On or Off.

TIP: When MJPEG Only mode is enabled, the camera only outputs video in a MJPEG format via USB. This provides compatibility with video conferencing platforms or video adapters that do not support Intelligent Switching due to an incompatible format.

Room Size

Large

Set the size of the room the camera is used in.

**Large** room size is intended for presenter tracking up to 35 ft from the camera.  

Extra Large

**Extra Large** room size is intended for presenter tracking 35 to 55 ft from the camera.

note: IV-CAM-I20 only.

Show Preset#

Off/On

Turn the Preset number On or Off on the video feed.

FW Version

n/a

Displays the camera firmware version.

Reset OSD

Confirm

Select Confirm to reset OSD menu settings to the factory default.

Network

Mode

Static IP

Set the camera IP connection method.

DCHP

IP

n/a

Displays the camera's IP address.

Subnet

n/a

Displays the camera's subnet mask address.

Gateway

n/a

Displays the camera's static gateway address.

DNS 1

n/a

Displays the camera's static primary DNS lookup address.

DNS 2

n/a

Displays the camera's static secondary DNS lookup address.

### IV-CAM-I12D-B Menu Navigation

The IV-CAM-I12D-B camera contains different values and options compared to the other IV-CAM Series cameras. Refer to the table below for information on navigating through the OSD sub menus.

IV-CAM-I12D-B OSD Menu Options

   

Option

Sub Menu Options

Setting Range

Setting Description

  Video

Lens

PTZ/Reference

Selects either the PTZ cameras or Reference camera for settings.

Sharpness

0 - 11

Adjust video sharpening.

Brightness

0 - 14

Adjust video brightness.

Contrast

0 - 14

Adjust video contrast.

Gamma

0 - 4

Adjust video gamma correction.

2DNR

0 - 7

2D Noise Reduction level.

3DNR

0 - 7

3D Noise Reduction level.

DRC

0 - 5

Dynamic Range Compression level.

Mirror

Off/On

Mirrors camera output.

Video Format

4Kp25/29.97/30  
1080p30/29.97/25/60/59.94/50,  
720p60/59.94/50/

Adjust camera video output format.

note: HDMI video outputs only.

Distort Correct

Off/On

Turn the Reference Camera Distortion Correction On or Off.

  Exposure

Lens

PTZ/Reference

Selects either the PTZ cameras or Reference camera for settings.

Mode

Auto

Automatically adjust exposure.

Manual

Manually adjust exposure.

Shutter PRI

Shutter priority mode.

Aperture PRI

Aperture priority mode.

Bright

Brightness priority mode.

Anti-Flicker

OFF/50Hz /60Hz

Reduces flicker induced by 25p and 30p frame rates.

BLC

Off/On

Turn Back Light Compensation On or Off.

EXP Comp

Off/On

Turn exposure compensation On or Off.

\-7 - 7

Adjust the exposure compensation of the camera.

Gain

0 - 14

Adjust the gain of the camera.

Shutter

1/60 - 1/10000

Adjust the shutter speed of the camera.

Iris

F1.6 - F14, Close

Adjust the aperture of the camera.

REF Brightness

0 - 14

Adjust the reference camera's video brightness.

  Color

Lens

PTZ/Reference

Selects either the PTZ cameras or Reference camera for settings.

Mode

Auto

Fully automatic white balance.

Manual

Fully manual white balance adjustment.

One Push

Trigger a one time white balance adjustment.

Static

Preset white balance adjustments

Auto-R

Automatically adjust white balance to match the Reference Camera

Profile

Cloudy

Static Color Mode presets.

Daylight

Fluorescent

Tungsten

Custom

R-Gain

0 - 16

Adjust the red color channel balance.

G-Gain

0 - 16

Adjust the green color channel balance.

B-Gain

0 - 16

Adjust the blue color channel balance.

WB Sens

Low/Medium/High

Adjust white balance sensitivity.

Saturation

0 - 14

Increase or decrease color saturation.

Hue

0 - 14

Increase or decrease video hue.

PTZ

Speed

1 - 7

Adjust the speed of camera movement.

AF Sens

Low/Medium/High

Adjusts the AutoFocus sensitivity

AF Area

Global/Center/Face/Foreground  

Set the Auto-Focus area to be used:

*   **Global** uses the full PTZ image provided.
    
*   **Center** focuses from the center of lens first.
    
*   **Face** prioritizes faces within the scene.
    
*   **Foreground** prioritizes objects nearest to the camera
    

PTZ Trig AF

Off/On

Auto-focus after moving the camera.

Preset Freeze

Off/On

Turn Preset Freeze On or Off.

Auto Privacy

Off/On

Turn automatic Privacy Mode On or Off

Home Shot

Off/On

Enables Preset 0 (Home Shot) to be called upon camera wake action  

Digital Zoom

Off/On

Turn Digital Zoom On or Off.

Calibrate

Confirm

When selected, the camera will perform focus calibration. Refer to [Focus Calibration](#Focus) for more information about focus calibration.

System

Address

1 - 3

Choose the camera address for serial and IP communication.

Protocol

VISCA

Choose the protocol for serial and IP communication.

PELCO-D

PELCO-P

Baudrate

2400 - 38400

Set the baud rate for the serial port.

Disable LED

Off/On

Turn the camera LED On or Off.

Layout

Standard/PiP

Switches between a full-screen (Standard) and picture and picture (PiP) camera shot layouts.

IR

Off/On

Turn the IR receiver On or Off.

IR Address

1/2/3

Set the IR address for the camera.

MJPEG Only

Off/On

Turn MJPEG Only mode On or Off.

TIP: When MJPEG Only mode is enabled, the camera only outputs video in a MJPEG format via USB. This provides compatibility with video conferencing platforms or video adapters that do not support Multi-Camera Switching due to an incompatible format.

Show Preset#

Off/On

Turn the Preset number On or Off on the video feed.

FW Version

n/a

Displays the camera firmware version.

Reset OSD

Confirm

Select Confirm to reset OSD menu settings to the factory default.

Network

Mode

Static IP

Set the camera IP connection method.

DCHP

IP

n/a

Displays the camera's IP address.

Subnet

n/a

Displays the camera's subnet mask address.

Gateway

n/a

Displays the camera's static gateway address.

DNS 1

n/a

Displays the camera's static primary DNS lookup address.

DNS 2

n/a

Displays the camera's static secondary DNS lookup address.

### Focus Calibration

Focus calibration should be performed when the camera appears to be off focus at various zoom levels. Complete the following procedure to calibrate the focus of the PTZ camera:

1.  At the bottom of the user interface, use the **PTZ Controls** to aim and zoom the camera's PTZ lens at the farthest object in the room.
    
2.  Select the **Menu** button to open the OSD menu.
    
3.  Select the **PTZ** option within the OSD menu.
    
4.  Select the **Calibration** option.
    

The camera performs the focus calibration for the PTZ lens. The focus calibration process may take up to 3 minutes to be complete.

note: Ensure that no objects or people move in front of the camera during this process.
