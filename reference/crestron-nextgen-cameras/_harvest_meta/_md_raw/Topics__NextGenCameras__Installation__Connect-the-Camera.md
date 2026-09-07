     Connect the Camera | IV-CAM Series Manual              

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

# Connect the Camera

Refer to the following sections for more information on the required and optional camera connections.

caution: To avoid damage and ensure optimal performance of the camera:

*   Check the source power before powering on the camera. IV-CAM series cameras can be powered via a 15.4 W PoE switch or with the [PW-1225DU](https://www.crestron.com/model/6513216 "https://www.crestron.com/model/6513216") 12VDC power supply (sold separately). Under or overpowering the camera will cause damage and poor performance that may not be immediately visible. If a PoE switch used, be sure the port is properly configured for 15.4 W. If using DC power and connecting to a network switch, be sure the port is not set for PoE.
    
*   Do not power the camera with PoE and a power supply at the same time. Doing so may cause it to malfunction.
    

## Camera Ports

Route all necessary cables to the camera as described in the installation instructions for the chosen mounting accessory (refer to [Install the Mounting Hardware](Install-the-Mounting-Hardware.htm)). Then, make all connections to the rear of the camera as shown in the following image.

![](../../../Resources/Images/SS-Cameras/AppDiagrams/IV-CAMConnections-01.png)

## Network Connection

A network connection enables easy configuration and control from any computer connected to the same network, and access to the camera’s IP video streams. Use a CAT5e (or greater) cable to connect the camera to the network or directly to the host computer used for configuration. The camera by default is set to DCHP.

**Note**: Use shielded CAT5e (or greater) cables when running the cable over long distances and/or if NDI is used.

## PoE Power

Crestron 1 Beyond camera support control, streaming, and power over a single Ethernet cable. If using a network switch, ensure that it is PoE certified and that it can supply 15.4 W for each connected camera. Alternatively, a PoE injector can be used to inject power between the switch and camera.

 

NOTE: To comply with the European Directive (CE), shielded CAT5e cable must be used as a minimum for PoE power.

## DC Power

Power the Crestron 1 Beyond camera using the [PW-1225DU](https://www.crestron.com/model/6513216 "https://www.crestron.com/model/6513216") 12VDC power supply (sold separately). The camera cannot operate properly with less than 12VDC power. Since voltage drops over distance, the PW-1225DU power adapter is not sufficient if the power source is greater than 10 ft (3 m) from the camera. Do not use the PW-1225DU 12VDC power supply and PoE simultaneously.

Caution: Providing too little or too much power can damage the camera. For PoE, make sure the network port is configured for 15.4 W. For DC power, be sure to supply 12V to the camera.

## Video Output

Crestron 1 Beyond cameras have multiple video output options, and all video outputs are available simultaneously. Refer to the following sections for information regarding video outputs.

tip: When cameras are connected via HDMI or 3G-SDI for video output, the IP address of the camera is shown momentarily on the video output display when the camera is powered on.

### USB 3.0

Connect the camera to a computer using a USB 3.0 cable. It will be detected by your operating system and become selectable in all applications supporting USB cameras.

### 3G-SDI

The rear of the camera has one 3G-SDI port to use with standard 3G-SDI cabling (RG-6 Coax cable, 75 Ω with BNC male connectors). Depending on specific building fire codes, cables may need to be plenum rated.

### HDMI

The camera can be connected with an HDMI® cable to a conferencing codec or capture device via the rear HDMI port on the camera.

## Serial Control

The IV-CAM Series camera supports serial control over RS-485 and RS-232. The serial connection is for sending remote commands to the camera using the VISCA, PELCO\_D, or PELCO\_P protocols from a control system. In most cases, serial cabling is optional because control of the camera is done through a network connection.

If serial control is required, it is recommended to use RS-485. RS-485 can support cable lengths of up to 4,000 ft while RS-232 is limited to cable distances of 50 ft. Also, RS- 485 can support up to 32 controller devices while RS-232 only supports one.

22 or 24 AWG twisted pair cable is recommended for serial control. Depending on specific building fire codes, cables may need to be plenum rated.

To wire serial control, use the terminal block (included) with a serial cable. Then, connect the ends of the cable into the camera and the control device being used.

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [Connect the Camera](#ConnecttheCamera)

*   [Camera Ports](#CameraPorts)
*   [Network Connection](#NetworkConnection)
*   [PoE Power](#PoEPower)
*   [DC Power](#DCPower)
*   [Video Output](#VideoOutput)

*   [USB 3.0](#USB30)
*   [3G-SDI](#3GSDI)
*   [HDMI](#HDMI)

*   [Serial 