Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Set-the-Tracking-Zone.htm

# Set the Tracking Zone

Note: Tracking Zones are only available for the IV-CAM-I20 and IV-CAM-I12 when set to **Presenter** mode. For more information on switching a camera's mode, refer to [Change the Camera Mode](Change-the-Camera-Mode.htm)

The camera uses Visual AI to detect faces in the Tracking Zone of its wide-angle lens, then tracks the presenter within the Tracking Zone. The Tracking Zone is indicated in the video frame as a green box.

NOTE: The camera does not save settings automatically. Make sure to save frequently during the setup process.

To draw a **Tracking Zone**:

1.  Select **Set Tracking Zone** in the top left of the **Tracking Zones** menu. When selected, the cursor moves into the video frame.
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/SelectSetTrackingZone.png)
    
2.  Press and hold the cursor over the location in the video frame where the **Tracking Zone** should begin. Then, drag the cursor to create the **Tracking Zone**.
    
    Note the following guidelines when configuring **Tracking Zones**.
    
    *   Set the **Tracking Zone** to contain the entire area where a presenter will move around. Draw the **Tracking Zone** so it fills a presenter's head and torso. Tracking is more effective when zones are narrow and defined.
        
    *   Leave room on the left and right of the zones to allow the presenter to leave the zone and another presenter to enter.
        
    *   If the front row of audience seats covers some of the presentation area, do not include it in the **Tracking Zone**. Instead, draw it so that at least the torso and/or head of the presenter will be the only moving subjects in the Tracking Zone.
        
    
3.  Release the cursor to finish the Tracking Zone. Refer to the image below for an example, the **Tracking Zone** is indicated as a green box.
    
    note: The red box in the image below is the **Blocking Zone** for this configuration. For more information about drawing a **Blocking Zone**, refer to [Blocking Zones](Blocking-Zones.htm).
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings (i12 Group)/Tracking Zones (Presenter).png)
    
4.  Once the **Tracking Zone** is set, select **Save Settings**.
    

The **Tracking Zone** is now configured to track the presenter.

NOTE: When no presenter is detected or tracked, the camera will revert to the **Home Shot** (**Preset 0**). For more information on the **Home Shot** (**Preset 0**), refer to [Camera Controls](Camera-Controls.htm#SetHomeShot).
