     Advanced Camera Settings | IV-CAM Series Manual              

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

# Advanced Camera Settings

This section contains information on the Crestron 1 Beyond camera advanced settings. These are used to change the protocol, network, user, and firmware update settings.

To access the **Advanced Settings** menu, select **Settings** on the desired camera in the camera list.

Settings Select

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/AdvancedSettingsSelect.png)

The **Advanced Settings** menu is displayed.

Advanced Settings Menu

![](../../../Resources/Images/Camera_Manager_8-26-25/ADV_Protocol_82625.png)

## Protocol Settings

The **Protocol** settings are displayed by default when the **Advanced Settings** menu is opened. **Protocol** settings include streaming options for camera output and control settings for interacting with control devices.

Select the **Save Settings** button in the bottom right of the **Advanced Settings** window to save any changes made.

Protocol Tab

![](../../../Resources/Images/Camera_Manager_8-26-25/ADV_Protocol_82625.png)

The following **Protocol** settings are available.

### Streaming

**Streaming** settings are used to adjust the properties of the native IP video streams that are encoded and transmitted by the camera.

Streaming Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Advanced Settings/StreamingSettings.png)

The following **Streaming** settings are available.

*   **Stream Type**: Select the camera stream to be configured.
*   **Resolution**: Select the desired stream resolution independently of the camera's operating resolution.
    
*   **Bitrate Type**: Select whether the video will be encoded with **CBR** (constant) or **VBR** (variable) bit rate. Selecting **VBR** causes reduced stream bit rate during static shots with little movement. The bit rate increases as motion increases.
    
*   **Max Bitrate**: Set the maximum bit rate of the video stream. The default value of **6000** Mbps should be retained for most setups.
    
*   **Frame Rate**: Select the stream's frame rate.
    
*   **Key Frame Interval**: Enter the number of frames that must occur before a keyframe is sent in a video stream.
    
*   **Encoding Type**: Select whether the video stream will use **H.264** or **H.265** encoding.
    
*   **Encode Profile**: Select whether the video stream will use a **low**, **base**, or **high-profile** encoding type.
    

### Control Settings

The **Control** settings are used to set a secondary connection to the camera from a control device.

Control Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Advanced Settings/ControlSettings.png)

The following **Control** settings are available.

*   **Enable** and **Disable**: Select **Enable** or **Disable** to turn the secondary connections on or off.
    
*   **Protocol Type**: Select the communication protocol for the secondary connection.
    
*   **Device Mode**: Select either **Server** or **Client** to determine the role for the camera when using a secondary connection.
    
*   **Server IP Address**: Enter the IP address for the secondary connection device. The default value of **0.0.0.0** should be retained for most setups.
    
*   **Control Port**: Enter the port number into the **Control Port** text field for the secondary connection. The default value of **5500** should be retained for most setups.
    

#### Control Settings (IV-CAM-I12D-B Only)

The following **Control** settings are available only with the IV-CAM-I12D-B.

Control Settings (IV-CAM-I12D-B Only)

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/ADVControl.png)

*   **VISCA Passthrough Port**: Enter the port number into the **VISCA Passthrough Port** text field for the VISCA connection. The default value of **5500** should be retained for most setups.
    
*   **VISCA over IP Port**: Enter the port number into the **VISCA over Port** text field for the network VISCA connection. The default value of **52381** should be retained for most setups. This protocol use standard VISCA commands preceded by an 8‑byte hedaer.
    
*   **Audio Reference IP**: Enter the IP address of the audio device's AES67 stream to have the camera ignore the incoming audio during Speaker Tracking. Alternatively, this configuration can be achieved via the **AUDIO REF** port of the camera without requiring an Audio Reference IP. For more information about the **AUDIO REF** port, refer to [Connect the IV-CAM-I12D-B Camera](../Installation/Connect-the-IV-CAM-I12D-B-Camera.htm).
    
*   **Audio Reference Port**: Enter the port number into the **Audio Reference Port** text field for the AES67 connection.
    

### Other Settings

The following miscellaneous settings are available.

Other Settings

![](../../../Resources/Images/NextGenCameras_3_18/Protocol_DownloadLogs_sidepane.png)

*   **Reboot** : Select to restart the camera.
    
*   **Reset** : Select to restore all settings on the camera back to the factory default.
    
    Caution: Performing a factory restore returns all settings to their default values and removes any static IP addresses for the camera. For more information on setting a static IP address, refer to [Set a Static IP Address](Set-a-Static-IP-Address.htm).
    
*   **Reboot All Cameras**: Select to restart all cameras available in the camera list.
    
*   **Download Logs**: Select to download log files for the camera onto the computer operating Camera Manager.
    

## Network Settings

The **Network** settings contain the camera's network settings for the camera's video streams, time settings, and autoupdate settings. Select the **Save Settings** button in the bottom right of the **Advanced Settings** window to save any changes made.

To access the **Network** settings, select the **Network** tab on the top of the **Advanced Settings** menu.

Network Menu

![](../../../Resources/Images/Camera_Manager_8-26-25/ADV_Network-82625.png)

The following **Network** settings are available.

*   **IP Type**: Select whether the camera connects to the network over a static IP address or dynamically over a **DHCP** IP address. If set to **Static IP**, configure the following options:
    
    *   **IP Address**: Enter a static IP address for the camera.
        
    *   **Mask**: Enter a static subnet mask address for the camera.
        
    *   **Gateway**: Enter a static address for the default gateway router.
        
    *   **DNS 1**: Enter a static primary DNS (Domain Name Server) lookup address.
        
    *   **DNS 2**: Enter a static secondary DNS (Domain Name Server) lookup address.
        
*   **RTSP Port**: Enter a port that will be used for the camera's RTSP video-over-IP streams. For more information about accessing the RTSP streams, refer to [Accessing the RTSP Streams](#Accessing).
    
    note: Only RTSP values of 554 and the range of 3479–7999 are supported.
    
*   **App Port**: Enter a port that will be used for communication between the Crestron 1 Beyond Camera Manager 2 software and the camera.  
    
    NOTE: The **App Port** value should not be changed unless instructed to do so by [Crestron True Blue Support](https://www.crestron.com/Support "https://www.crestron.com/Support").
    
*   **NTP**: Select **Enable** to use Network Time Protocol and sync the camera's clock with the network's time. Select **Disable** to not use NTP.
    
*   **NTP Server**: If **NTP** is enabled, enter the network server into the **NTP Server** text field that NTP will use to obtain the date and time.
    
*   **Time Zone Offset**: Use the **Time Zone Offset** drop-down menu to select the camera's time zone.
    
*   **Auto-Update**: Select **Enable** to allow the camera to perform automatic updates. Select **Disable** to not allow the camera to perform automatic updates. If **Auto-Update** is enabled, configure the following options:
    
    **note**: It is not recommended to use the Camera Manager's **Auto-Update** tool if the camera is used with a Crestron Flex or Automate VX solution. These systems perform automatic updates for the camera via their own methods.
    
    *   **Manifest URL**: Enter the URL that the camera will pull the automatic updates from.
        
        NOTE: Do not change the **Manifest URL** value unless instructed by [Crestron's True Blue Support](https://www.crestron.com/Support "https://www.crestron.com/Support").
        
    *   **Auto-Update Time**: Select the desired time for the cameras to perform automatic updates.
        

### Accessing the RTSP Streams

The following credentials are required to access the camera's RTSP stream:

*   **Username**: admin
    
*   **Password**: The password set for the camera in camera manager. For more information about changing a camera's password, refer to [User Settings](#User).
    

#### RTSP Stream URL

A URL is required to access the RTSP stream of the camera. The URL for the camera's RTSP stream adheres to the following structure: **rtsp://cameraIPaddress:rtspportnumber/x.encodingtype**. Observe the following about the RTSP stream URL:

**note**: Special characters in a RTSP URL must be escaped by encoding characters into URL escape codes.

*   **cameraIPaddress** is the camera's IP address designated within camera manager. For information about the camera's IP address, refer to [Network Settings](#Network).
    
*   **rtspportnumber** is the RSTP port designated for the camera. For more information about the RTSP port, refer to [Network Settings](#Network).
    
*   **x.encodingtype** is the encoding type used for the camera, as well as the camera feed being accessed. For more information about the encoding type, refer to [Streaming](#Streaming).  
    
    Refer to the following information to select which camera feed is used for the RTSP stream:
    
    *   **x** = 1: Access the camera's main PTZ feed.
        
    *   **x** = 2: Access the camera's reference camera feed.
        
    
    For IV-CAM-I12D-B cameras:
    
    *   **x** = 1: Access the camera's PTZ 1 feed.
        
    *   **x** = 2: Access the camera's main PTZ 2 feed.
        
    *   **x** = 3: Access the camera's reference camera feed.
        
    
    For more information on camera streams, refer to [Accessing Camera Feeds](Access-Camera-Feeds.htm).
    
    note: If the credentials for the camera's RTSP stream are required in the stream URL, then the URL can be written as **rtsp://admin:\[camerapassword\]@\[cameraIPaddress\]:rtspportnumber/x.encodingtype**
    

Refer to the following example of a valid RTSP stream URL: **rtsp://10.10.120.145:554/1.h264**.

*   The camera's IP address is **10.10.120.145**.
    
*   The camera's RTSP port is **554**.
    
*   The camera feed accessed is the main PTZ camera's feed (x = **1**).
    
*   The encoding type used is **h.264**.
    

## Upgrade Settings

The **Upgrade** settings are used to perform manual firmware updates, display the current camera version, and display the upgrade status during a firmware update.

To access the **Upgrade** menu, select **Upgrade** on the top right of the **Advanced Settings** menu.

Upgrade Menu

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Advanced Settings/Upgrade.png)

For information on performing a firmware update for the camera, refer to [Update Firmware](Update-Firmware.htm).

## User Settings

The **User** settings show the name of the camera and provides password management. To access the **User** settings, select the **User** tab on the top right of the **Advanced Settings** menu.

User Tab

![](../../../Resources/Images/Camera_Manager_8-26-25/ADV_User_82625.png)

The following **User** settings are available.

*   **Device Name**: Set the name of the current camera. The name displayed in the Device Name text field is also the NDI stream name of the camera.
    
    note: If the **Device Name** is changed, the camera requires a restart before the new **Device Name** appears in NDI streams. For more information on how to restart a camera, refer to [Other Settings](#Other).
    
*   Change Password: To change the camera's password, perform the following steps.
    
    1.  Enter the current password of the camera in the **Old Password** text field.
        
    2.  Enter the desired new password in the **New Password** text field.
        
    3.  Enter the same new password in the **Confirm Password** text field.
        
    4.  Select **Save Settings** to change the password of the camera.
        
        The camera's password has been updated.
        

## NDI Settings

The NDI settings allow you to enable or disable the camera’s NDI output, edit the group and stream names, and configure connections to Discovery and Multicast Servers.

note: NDI settings should not be changed for Automate VX configurations unless instructed to do so by Crestron True Blue Support.

NDI Settings

![](../../../Resources/Images/Camera_Manager_8-26-25/ADV_NDI_82625.png)

Select **Enable** to turn on the NDI output or select **Disable** to turn it off. To configure the other NDI settings, refer to [NDI's documentation](https://docs.ndi.video/all/getting-started/white-paper "https://docs.ndi.video/all/getting-started/white-paper").

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [Advanced Camera Settings](#AdvancedCameraSettings)

*   [Protocol Settings](#ProtocolSettings)

*   [Streaming](#Streaming)
*   [Control Settings](#ControlSettings)
*   [Other Settings](#OtherSettings)

*   [Network Settings](#NetworkSettings)

*   [Accessing the RTSP Streams](#AccessingtheRTSPStreams)

*   [Upgrade Setti