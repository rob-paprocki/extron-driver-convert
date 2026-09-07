Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Presenter-Tracking-Settings.htm

# Presenter Tracking Settings

note: Presenter Tracking settings are only available for the IV-CAM-I20 and IV-CAM-I12 set to **Presenter** mode. For more information on switching a camera's mode, refer to [Change the Camera Mode](Change-the-Camera-Mode.htm)

Refer to the following sections for information on the available Presenter Tracking settings.

Presenter Tracking Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Tracking Settings i20/Tracking Settings.png)

## Auto-Tilt

When enabled, the camera will tilt up or down once locked onto a presenter.

## Auto Zoom

When enabled, the camera will automatically zoom in or out as the tracked subject moves closer to or away from the camera.

## Outside Zone

When enabled, the camera keeps tracking a presenter that it has locked onto as they exit the **Tracking Zone** but remain in the wide-angle reference camera's FOV (field of view). For more information about Tracking Zones, refer to [Set the Tracking Zone](Set-the-Tracking-Zone.htm).

## Group Track

note: Group Tracking is only available for the IV-CAM-I20.

When enabled, the camera fits all participants into the frame and tracks the presenters within the **Tracking Zone**. When disabled, the camera only tracks one presenter at a time. For more information about Tracking Zones, refer to [Set the Tracking Zone](Set-the-Tracking-Zone.htm).

## Track Sensitivity

Use the slider to determine how sensitive the wide-angle camera detection is within the tracking zone. Lower this setting if the camera gets distracted by lighting changes or shadows.

## Target Lost Time

Use the slider to determine how long the camera waits before returning to the **Target Lost Action** once the participant leaves the **Tracking Zone**. For more information about Tracking Zones, refer to [Set the Tracking Zone](Set-the-Tracking-Zone.htm).

## Zoom Limit

Use the slider to determine the maximum amount of zoom applied when the tracked presenter moves further into the background.

## Pan Speed

Use the slider to adjust the speed of pan movement during tracking. Increase **Pan Speed** if presenters tend to be more active.

## Target Lost Action

Determines whether the camera returns to the **Home Shot (Preset 0)**, **Tracking Shot (Preset 1)**, or stays at its current position when no presenter is being tracked. For more information on setting the **Home Shot (Preset 0)** and **Tracking Shot (Preset 1)**, refer to [Set the Tracking Shots](Set-the-Tracking-Shots.htm).

## Power On State

Determines whether Presenter Tracking is enabled or disabled when the camera is powered on.
