Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Installation/Connect-the-IV-CAM-I12D-B-Camera.htm

# Connect the IV-CAM-I12D-B Camera

Refer to the following sections for more information on the required and optional camera connections.

## Camera Ports

Route all necessary cables to the IV‑CAM‑I12D‑B as described in the installation instructions for the included mounting accessory (refer to [IV-CAM-I12D-B Installation](IV-CAM-I12D-B-Mounting.htm)). Then, make all connections to the rear of the camera as shown in the following image.

![](../../../Resources/Images/Hawk 2/iv-cam-i12d-b Connect-01.png)

## Network Connection

A network connection enables easy configuration and control from any computer connected to the same network, and access to the camera’s IP video streams. Use a CAT5e (or greater) cable to connect the camera to the network or directly to the host computer used for configuration. The camera by default is set to DCHP.

## Audio Reference

Audio coming from in room speakers can be sent to the IV‑CAM‑I12D‑B to prevent unwanted camera switching. Failure to send in room audio to the camera causes poor camera performance during meetings.

Use either the 3-Pin balanced audio port (**AUDIO REF**) or input the IP address of the audio device into the camera's settings to send reference audio to the camera. For more information about connecting to the audio device via camera manager, refer to [Control Settings](../Configuration/Advanced-Settings.htm#Control).

## DC Power

Power the IV-CAM-I12D-B camera using the included 24VDC power supply. The camera cannot operate properly with less than 24VDC power. Since voltage drops over distance, the included power adapter is not sufficient if the power source is greater than 10 ft (3 m) from the camera.

Caution: Providing too little or too much power can damage the camera. Ensure 24V is supplied to the camera.

## Video Output

The IV‑CAM‑I12D‑B has multiple video output options, and all video outputs are available simultaneously. Refer to the following sections for information regarding video outputs.

tip: When the IV‑CAM‑I12D‑B is connected via HDMI for video output, the IP address of the camera is shown momentarily on the video output display when the camera is powered on.

note: Picture-in-Picture in the camera output is unavailable at resolutions at and below 360p.

### USB 3.0/2.0

Connect the camera to a computer using the included USB-C® to USB-A cable. It will be detected by your operating system and become selectable in all applications supporting USB cameras.

### HDMI

The camera can be connected with an HDMI® cable to a conferencing codec or capture device via the rear HDMI port on the camera.

## Serial Control

The IV-CAM Series camera supports serial control over RS-485 and RS-232. The serial connection is for sending remote commands to the camera using the VISCA, PELCO\_D, or PELCO\_P protocols from a control system. In most cases, serial cabling is optional because control of the camera is done through a network connection.

If serial control is required, it is recommended to use RS-485. RS-485 can support cable lengths of up to 4,000 ft while RS-232 is limited to cable distances of 50 ft. Also, RS-485 can support up to 32 controller devices while RS-232 only supports one.

22 or 24 AWG twisted pair cable is recommended for serial control. Depending on specific building fire codes, cables may need to be plenum rated.

To wire serial control, use the terminal block (included) with a serial cable. Then, connect the ends of the cable into the camera and the control device being used.
