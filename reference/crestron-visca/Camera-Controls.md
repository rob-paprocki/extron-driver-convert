Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Camera-Controls.htm

# Camera Controls

Crestron 1 Beyond camera shots can be manually configured with the Crestron 1 Beyond Camera Manager 2 software. These controls are located at the bottom of the user interface.

Camera Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/CameraSettings.png)

## PTZ Controls

**PTZ Controls** allow for manual pan, tilt, zoom, iris, and focus controls of the PTZ camera.

PTZ Controls

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/PTZControls.png)

*   Navigation Pad: Use the left and right buttons to pan the camera, and the up and down buttons to tilt the camera. The four corners on the navigation pad simultaneously pan and tilt the PTZ camera in the respective direction. The center button returns the camera to its center position.
    
*   **\- Zoom +**: Use the **+** and **\-** buttons to zoom the PTZ camera shot in or out.
    
*   **\- Focus +**: Use the **+** and **-** buttons to increase and decrease the PTZ camera lens focus.
    
*   **AF**: Use to auto focus the PTZ camera lens.
    
    NOTE: Auto focus is only available when presenter tracking is disabled. When presenter tracking is enabled, the camera automatically focuses the camera lens. For more information about Presenter Tracking, refer to [Presenter Tracking Settings](Presenter-Tracking-Settings.htm).
    

## Presets

Presets are used to switch to specific camera shots when the preset is called. Presets must be **Set** before they can be called. Refer to the following information on setting and calling presets.

note: There are reserved camera presets that cannot be overwritten. For more information, refer to [Reserved Presets](Reserved-Presets.htm).

Presets Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Presets.png)

Open the **Presets** drop-down menu by selecting the down arrow to display all camera presets. Select the desired preset to set it as the active preset. The **Call**, **Set**, and **Clear** controls will be applied to the active preset.

NOTE: **Preset 0** and **Preset 1** are reserved as the **Home Shot** and **Tracking Shot**. For more information, refer to [Tracking Menu](Intelligent-Settings.htm#TrackingSettings).

*   **Set**: Sets the current camera shot for the active preset. When **Call** is selected, the camera feed switches to the camera shot that was configured with **Set**. Selecting **Set** will override the previous camera shot associated with the preset.
    
    TIP: Use the PTZ Controls to manually create a camera shot for the preset. For more information, refer to [PTZ Controls](#PTZControls).
    
*   **Call**: Switch the camera shot to the preset. If the preset has not been set first, **Call** does not switch the camera shot.
    
*   **Clear**: Delete the camera shot set to the preset. The preset is now empty and can be **Set** for another camera shot if desired.
    

## Tracking

**note**: The **Tracking** settings are only available for the IV‑CAM‑I12, IV‑CAM‑I20, and IV‑CAM‑I12D‑B cameras.

The **Tracking** settings enable or disable the camera's intelligent functions (Group Framing and Presenter Tracking), display the current intelligent function status, and enable or disable debug mode for the camera.

Tracking Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking.png)

*   **Tracking** color bar: This shows the intelligent function status of the camera.
    
    *   Green indicates that the intelligent function is enabled.
        
        ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/TrackingIndicator.png)
        
    *   Gray indicates that the intelligent function is disabled.
        
        ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/TrackingIndicatoroff.png)
        
*   Play/Pause button: This enables or disables presenter tracking on the camera.
    
*   In-Frame button: This enables or disables debug mode. Debug mode shows the following depending on the camera's mode:
    
    *   Presenter tracking: Debug mode shows a box around faces in the camera shot. Green boxes indicate participants, and red boxes indicate active presenters.
        
    *   Speaker Tracking: Debug mode shows a green Direction of Audio (DoA) bar in the reference camera's video feed. When no audio is detected, the DoA bar rests on the left side of the camera feed. When audio is detected, the DoA bar moves over the speaking participant.
        
    
    The circle next to the button indicates the status of Debug mode.
    
    *   Grey circle: Debug mode is off.
        
    *   White circle: Debug mode is on.
        

In-Frame Button

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/TrackingDebug.png)
