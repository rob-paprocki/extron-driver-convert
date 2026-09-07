Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Visual-Cue-Intelligent-Switching-Config.htm

# Visual Cue Intelligent Switching Configuration

Visual Cue Intelligent Switching utilizes a host camera (IV-CAM-I12 set to Group Framing or IV‑CAM‑I12D‑B) and up to four other Crestron intelligent cameras (IV-CAM-I12 and IV-CAM-I20) serving as Presenter Tracking cameras.

Camera switching in this configuration occurs based on visual cues:

*   If a participant enters the Tracking Zone of one of the Presenter Tracking cameras, the video output switches to that camera.
    
    *   If there are participants in two or more cameras' Tracking Zones, the higher numbered camera takes priority in the output. The order of camera priority is as follows (highest priority to lowest): camera 2, camera 3, camera 4, camera 5.
        
*   If there are no participants in any Tracking Zones associated with Presenter Tracking cameras, the camera output switches to the host camera (IV-CAM-I12 set to Group Framing or IV‑CAM‑I12D‑B).
    

To activate Visual Cue Intelligent Switching:

note: Additional Presenter Tracking and Group Framing settings require configuration for **Intelligent Switching** to operate properly. For more information on Presenter Tracking and Group Framing settings, refer to [Tracking Settings](Tracking-Settings.htm).

1.  Select **Tracking** on the host camera in the camera list to access the **Tracking** menu.
    
    Tracking Button
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/AccessTrackingSettings.png)
    
    The Tracking Menu is displayed.
    
    Tracking Menu
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings (i12 Group)/TrackingSettingsi12.png)
    
2.  Select the **Tracking Settings** tab to access the **Tracking Settings**.
    
    Select Tracking Settings
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/SelectTrackingSettings.png)
    
    The **Tracking Settings** menu is displayed. The **Multi-Cam Tracking** settings are located at the bottom of the **Tracking Settings** menu.
    
    Tracking Settings
    
    ![](../../../Resources/Images/Camera_Manager_8-26-25/TrackingSettings_MultiCam_82625.png)
    
3.  Enable **Multi-Cam Tracking** by selecting **On**.
    
    Multi-Camera Tracking Settings
    
    ![](../../../Resources/Images/Camera_Manager_8-26-25/TrackingSettings_MultiCam_Zoomedin_82625.png)
    
4.  (IV-CAM-I12D-B in Speaker Tracking mode Only) Select **Speaker Priority** to have the speaker tracking camera shots take priority on the camera output.
    
    Speaker Priority
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/SpeakerPriority.png)
    
5.  In the **Cam 2 IP** text field, enter the IP address of the Presenter Tracking camera (IV-CAM-I12 camera set to Presenter Tracking mode or an IV-CAM-I20 camera). For more information on setting an IP address for a camera, refer to [Set a Static IP Address](Set-a-Static-IP-Address.htm).
    
    note: The light indicator next to the IP address text field displays the camera connection status. A white light indicates that the camera is connected and operational. If the light is black, the camera is either disconnected or not operational.
    
6.  If more than two cameras are used in the Intelligent Switching configuration, enter the additional cameras' IP addresses into their respective Cam IP text field. Refer to the following table for camera IP assignment logic:
    
     
    
    Camera Number (Order of Priority)
    
    Camera IP Address Assignment
    
    Camera 2
    
    Cam IP 2
    
    Camera 3
    
    Cam IP 3
    
    Camera 4
    
    Cam IP 4
    
    Camera 5
    
    Cam IP 5
    
7.  Select the **Optimize Settings for Multi-Camera** button.
    
8.  Select the **Save Settings** button to save the configuration.
    

Visual Cue Intelligent Switching is now configured.
