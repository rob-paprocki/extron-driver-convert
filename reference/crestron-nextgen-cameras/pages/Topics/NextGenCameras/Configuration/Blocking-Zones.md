Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Blocking-Zones.htm

# Blocking Zones

Set **Blocking Zones** within the **Tracking Zone** to prevent unwanted objects from triggering the camera’s facial detection. **Blocking Zones** are indicated in the video frame as red boxes.

note: **Blocking Zones** are set per camera's mode. When the camera switches its intelligent function, the **Blocking Zones** set for that specific camera mode apply. Ensure that **Blocking Zones** are set for all desired camera modes. For more information on changing the camera's mode, refer to [Change the Camera Mode](Change-the-Camera-Mode.htm).

To draw a **Blocking Zone**:

1.  Select one of the options underneath the **Blocking Zones** header. When an option is selected, the cursor moves into the video frame.
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/BlockingZones.png)
    
    **Blocking Zones B1** through **B4** are for blocking displays, windows, and projection screens.
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/B1toB4DisplayBlocking.png)
    
    **Blocking Zones B5** through **B8** are for blocking participants.
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/B5toB8PersonBlocking.png)
    
2.  Press and hold the cursor over the location in the video frame where the **Blocking Zone** should begin. Then, drag the cursor to draw the **Blocking Zone**.
    
    Note the following guidelines when configuring **Blocking Zones**.
    
    *   **Blocking Zones** are only active within the **Tracking Zone**.
        
    *   Ensure that there is space on the edges of the **Tracking Zone** for a presenter to enter. Covering an edge of the **Tracking Zone** with a **Blocking Zone** causes the presenter to be not tracked.
        
    *   There is no padding around the edges of **Blocking Zones**, they behave precisely as they are drawn.
        
    *   **Blocking Zones B1 - B4**: Displays must be turned off and participants are required to be out of the camera's FOV when drawing the **Blocking Zone**.
        
    *   **Blocking Zones B5 - B8**: Do not block an entire section of the **Tracking Zone**. This could cause the camera to lose the presenter if they remain in the blocked area for too long.
        
    
3.  Release the cursor to finish the **Blocking Zone**. Refer to the images below for an examples.
    
    In this example, the Blocking Zone is placed on the left side of the Tracking Zone (green box) over the door. This prevents people entering or leaving the room from triggering the camera's facial detection. For more information about drawing a Tracking Zone, refer to [Set the Tracking Zone](Set-the-Tracking-Zone.htm).
    
    Participant Blocking Zone
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings (i12 Group)/Tracking Zones (Presenter).png)
    
    In this example, there are two Blocking Zones (red boxes) over the displays within the Tracking Zone (green box). These Blocking Zones prevent the displays from triggering the camera's facial detection, while still allowing the camera to detect motion in the area underneath the displays.
    
    There is also a Preset Zone (blue box) on the right side of the Tracking Zone, which switches the camera to a predefined camera shot after someone enters the zone. For more information about drawing a Preset Zone, refer to [Preset Zones](Preset-Zones.htm).
    
    Display Blocking Zone
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/Tracking Zones.png)
    
4.  Once the **Blocking Zones** are set, select **Save Settings**.
    
    note: Tracking must be restarted for **Blocking Zones** to operate properly after configuring.
    

The **Blocking Zones** are now configured to ignore the defined areas.
