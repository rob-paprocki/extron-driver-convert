Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/PTZ-Alignment.htm

# PTZ Alignment

To ensure the best tracking performance, perform a PTZ camera alignment in relation to the static wide-angle reference camera. When the PTZ camera is misaligned with the wide-angle reference camera, it can cause camera shots to not be centered.

To correct PTZ camera alignment in relation to the static wide-angle camera:

1.  Open the **Tracking Zones** tab.
    
2.  Select **PTZ Alignment** in the top left of the **Tracking Zones** menu.
    
    Select PTZ Alignment
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/SelectPTZAlignment.png)
    
    A window is displayed showing the PTZ's video feed and wide-angle camera's video feed overlaid with a blue crosshair.
    
    PTZ Alignment Menu
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/PTZ Alignment.png)
    
3.  Use the PTZ lens controls in the **Settings** panel to move the PTZ video feed's blue crosshair into the same position as the wide-angle feed's crosshair. For best results, place an object that can be seen in both camera feeds as a point of reference for the blue crosshairs.
    
    NOTE: There will be a slight parallax error (a displacement between the positions of the PTZ camera and wide-angle reference camera) when performing the step above. This behavior is expected.
    
4.  Once the blue crosshairs in the PTZ video feed and the wide-angle feed are aligned, select **Save Settings** to confirm the changes.
    
    note: For IV-CAM-I12D-B cameras, steps 3 and 4 need to be performed for both PTZ 1 and PTZ 2 cameras.
    
5.  Select the back arrow on the left side of the software to exit the PTZ Alignment interface.
    

## Audio Correction (IV-CAM-I12D-B Only)

To ensure the best speaker tracking performance, perform a recalibration of the spacial audio detection within the wide-angle reference camera. When the spacial audio detection is misaligned within the wide-angle reference camera, speaker tracking camera shots may not be centered.

To correct the spacial audio detection in relation to the static wide-angle camera:

1.  Open the **Tracking Zones** tab.
    
2.  Select **PTZ Alignment** in the top left of the **Tracking Zones** menu.
    
    Select PTZ Alignment
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/SelectPTZAlignment.png)
    
    A window is displayed showing the PTZ's video feed and wide-angle camera's video feed overlaid with a blue crosshair.
    
    PTZ Alignment Menu
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/AudioCorrect.png)
    
3.  Select the **Channel** drop-down menu, then navigate to **Audio Correct**. A green Direction of Audio (DoA) bar appears on the reference camera feed. The DoA bar indicates where audio is being detected within the camera feed.
    
4.  Have someone stand in front of the IV-CAM-I12D-B camera and continuously speak. The DoA bar moves to the perceived audio location within the camera feed. If the DoA bar is not aligned with the speaking participant, use the PTZ lens controls in the **Settings** panel to adjust the position of the DoA bar in the camera feed accordingly.
    
5.  Once the DoA bar in the camera feed is aligned with the speaking participant, select **Save Settings** to confirm the changes.
    
6.  Select the back arrow on the left side of the software to exit the PTZ Alignment interface.
