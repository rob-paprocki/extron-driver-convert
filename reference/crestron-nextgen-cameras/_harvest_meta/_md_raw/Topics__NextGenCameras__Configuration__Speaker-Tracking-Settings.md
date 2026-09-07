     Speaker Tracking Settings | IV-CAM Series Manual              

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

# Speaker Tracking Settings

note: Speaker Tracking settings are only available for the IV-CAM-I12D-B when set to Speaker Tracking mode.

Refer to the following sections for information on the available Speaker Tracking settings.

Speaker Tracking Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/SpeakerTrackingSettings.png)

## Tracking Mode

Use the **Tracking Mode** drop-down menu to set the intelligent function of the camera as either **Group Framing** or **Speaker Tracking**. For more information about **Group Framing**, refer to [Group Framing Settings](Group-Framing-Settings.htm)

## Track Sensitivity

Use the slider to determine the tracking sensitivity of the wide-angle camera when detecting a speaking participant. Lower this setting if the camera is switching between speaking participants too frequently.

## Track Speed

Use the slider to adjust the speed of PTZ camera movement during tracking.

## Target Lost Time

Use the slider to determine how long the camera waits before returning to the **Target Lost Action** once no speaking participants are detected.

## Conversation Cycle

Use the slider to determine how many camera switches need to occur between two speaking participants before Conversation Mode begins. For more information about Conversation Mode, refer to [Speaker Tracking Mode](#Speaker).

## Conversation Length

Use the slider to set the length of time that Conversation Mode remains in the camera output while only one participant is actively speaking. Once the Conversation Length is exceeded, the camera shot transitions to a single shot of the last active speaking participant. For more information about Conversation Mode, refer to [Speaker Tracking Mode](#Speaker).

## Pause Delay

Use the slider to determine the amount of time before the **Standby Action** occurs. The **Pause Delay** condition can be met either through silence in front of the camera, or when active Audio Reference is sent to the camera. For more information about **Standby Action**, refer to [Standby Action](#Standby).

## Target Lost Action

Determines whether the camera returns to the **Home Shot (Preset 0)**, **Tracking Shot (Preset 1)**, or stays at its current position when no active speaking participant is heard. For more information on setting the **Home Shot (Preset 0)** and **Tracking Shot (Preset 1)**, refer to [Set the Tracking Shots](Set-the-Tracking-Shots.htm).

## Power On State

Determines whether Speaker Tracking is enabled or disabled when the camera is powered on.

## Face Offset

Select **High**, **Middle**, or **Low** to set the placement of the speaking participant's face in the camera shot.

## Frame Padding

Determines the amount of space around the speaking participant in the camera shot. Select **Tight** for a close up camera shot, or select **Wide** for a more zoomed out shot.

## Speaker Tracking Mode

Select **Single** to show only one speaking participant in the camera shot. Select **Conversation** to capture two active speaking participants within a side-by-side camrea shot.

This shot is called after the system detects another speaking participant other than the current one. Once they speak back and forth for the amount of **Conservation Cycles** set, they appear on the output in a side‑by‑side camera shot. For more information about Conversation Mode settings, refer to [Speaker Tracking Settings](#SpeakerTrack).

note: Conversation Mode is only available via the USB and HDMI outputs of the camera.

## Standby Action

The **Standby Action** occurs when the conditions for **Pause Delay** are met. For more information about Pause Delay, refer to [Pause Delay](#Pause).

Select **Group Framing** for a framed shot of all visible participants in front of the camera, **Stay** to remain on the last used camera shot, or **Reference** to show the reference camera's output.

## Additional Settings

Select the double arrow button on the bottom of the **Tracking Settings** tab to expose additional settings.

Double Arrow Button

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/SwitchIntelligentSwitching.png)

Additional Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/i12D/IntelligentSwitchingSettingsi12D.png)

The following settings are available in the additional settings menu.

### Intelligent Switching Settings

**Multi-Camera Conn**, **Speaker Priority**, and **Cam IP** settings are used for Intelligent Switching. To configure Intelligent Switching for the IV‑CAM‑I12D‑B camera, refer to [Intelligent Switching](Multi-Camera-Switching-Config.htm).

### Layout

Layout changes the Output of the camera to a video feed with different formatting. Select either of the following Layout options:

*   **Standard**: Displays a full-screen camera shot in the Output.
    
*   **PIP**: Displays a Picture-in-Picture (PIP) camera layout in the Output. A PiP layout uses the reference camera's feed in the selected corner, while showing the active PTZ camera as the full-screen video feed.
    
    Refer to the sections below for **PIP** settings.
    

#### PIP Position

The reference camera's feed in the **PIP** layout can be moved to any of the corners of the **Output**. Select **Top Left**, **Top Right**, **Bottom Left**, or **Bottom Right** to move the reference camera's feed to the respective corner of the **Output**.

#### PIP Size

The size of the reference camera's feed in the **PIP** layout can be changed. Select **Small**, **Medium**, or **Large** to adjust the size of the reference camera's feed in the **Output**.

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [Speaker Tracking Settings](#SpeakerTrackingSettings)

*   [Tracking Mode](#TrackingMode)
*   [Track Sensitivity](#TrackSensitivity)
*   [Track Speed](#TrackSpeed)
*   [Target Lost Time](#TargetLostTime)
*   [Conversation Cycle](#ConversationCycle)
*   [Conversation Length](#ConversationLength)
*   [Pause Delay](#PauseDelay)
*   [Target Lost Action](#TargetLostAction)
*   [Power On State](#PowerOnState)
*   [Face Offset](#FaceOffset)
*   [Frame Padding](#FramePadding)
*   [Speaker Tracking Mode](#SpeakerTrackingMode)
*   [Standby Action](#StandbyAction)
*   [Additional Settings](#AdditionalSettings)

*   [Intelligent Switching Settings](#IntelligentSwi