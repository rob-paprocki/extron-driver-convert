Source: https://docs.crestron.com/en-us/9440/Content/Topics/NextGenCameras/Configuration/Add-Cameras.htm

# Add Cameras

Use the following procedures to add Crestron 1 Beyond cameras to the Crestron 1 Beyond Camera Manager 2 software.

note: Before adding cameras to the Crestron 1 Beyond Camera Manager 2 software, ensure that the software is first installed onto the computer. For more information on installing the Crestron 1 Beyond Camera Manager 2 software, refer to [Install Camera Manager Software](1 Beyond Camera Manager System Installation.htm)

*   To access the camera manager main menu, refer to [Access the Main Menu](#Access).
    
*   To add a new camera, refer to [Add a New Camera](#NewCamera).
    
*   To add a camera that has been used in the software previously, refer to [Add a Configured Camera](#ExistingCamera).
    
*   To add a camera manually with its network information, refer to [Manually Add a Camera](#Manual).
    
*   To delete a camera from the camera list, refer to [Delete Camera](#Delete).
    
*   To delete all cameras from the camera list, refer to [Delete All Cameras](#Deleteall).
    
*   To identify which cameras are associated with entries in the camera list, refer to [Identify Cameras](#Identify).
    

## Access the Main Menu

Open the Crestron 1 Beyond Camera Manager 2 software either by selecting the desktop icon, or by navigating to the directory of the local computer where the software was installed.

Desktop Icon

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/C1BCM-Desktop-Icon.jpg)

The following screen is displayed when the software opens.

Camera Manager

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/CamManagerMainMenu.png)

The camera list is located on the left side of the user interface.

Camera List

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CameraList.png)

## Add a New Camera

To add a new camera to the camera list:

1.  Select **\+ Add Camera** in the top left of the user interface.
    
    + Add Camera
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/AddCamera.png)
    
    The **ADD CAMERA** window is displayed.
    
    Add Camera Window
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/Add Camera Blank.png)
    
2.  Select **Search Network** to search for cameras on the network. The desired camera must on the same network as the computer running the software. Cameras appear in the camera list with their IP address, MAC address, model, device name and firmware version.
    
    Search Network
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/SearchNetwork.png)
    
3.  Select the desired camera in the camera list, then select **Add Camera** in the bottom right of the **ADD CAMERA** window.
    
    Add Camera  
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/AddFromCameraList.png)
    
    TIP: Use the filter text field to narrow network search results for cameras. Input a parameter (IP address, camera model, MAC address) of the desired camera into the field. The search results will show all cameras that match the input parameters.
    
    Filter Text Field
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/NetworkSearch.png)
    
    When the camera connects to the host computer, the **Initial Setup** window is displayed.
    
    Initial Setup
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/Add Camera Initial Setup.png)  
    
    note: A prompt is shown displaying "Unable to add camera. Please check network parameters". if the camera is unable to connect to the host computer.  Verify that the camera's network parameters are correct under the **ADD CAMERA** banner.
    
    Network Parameters
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CameraParameters.png)
    
4.  Enter a password for the camera into the **New Password** and **Confirm Password** fields, then select **Apply**.
    
    Password Entry
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CreatePassword.png)
    
    note: The password entered for the camera also applies to RTSP and ONVIF connections for the camera.
    
5.  Select **Add Camera**.
    

The camera is now available in the camera list.

Camera List

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CameraAdded.png)

## Add a Configured Camera

To add a camera that was previously configured in Crestron 1 Beyond Camera Manager 2 but is not currently displayed in the camera list:

1.  Select **\+ Add Camera** in the top left of the user interface.
    
    \+ Add Camera
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/AddCamera.png)
    
    The **ADD CAMERA** window is displayed.
    
    Add Camera Window
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/Add Camera Blank.png)
    
2.  Select **Search Network** to search for cameras on the network. The desired camera must on the same network as the computer using the software.
    
    Search Network
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/SearchNetwork.png)
    
    TIP: Use the filter text field to narrow network search results for cameras. Input a parameter (IP address, camera model, MAC address) of the desired camera into the field. The search results show all cameras that match the input parameters.
    
    Filter Text Field
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/NetworkSearch.png)
    
3.  Cameras appear in the camera list with their IP address, MAC address, model, device name and firmware version. Select the desired camera in the camera list, then input the password of the camera into the **Password** text field.
    
    Password Text Field  
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/AddExistingCamera.png)
    
4.  Select **Add Camera** in the bottom right of the **ADD CAMERA** window.
    
    Add Camera Window
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/AddFromCameraList.png)
    
    Note: The software shows a prompt indicating that the camera could not connect if the password for the camera is incorrect.
    

The camera is now available in the camera list.

Camera list

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CameraAdded.png)

## Manually Add a Camera

A camera can be added manually to the camera list by entering its network parameters within the **ADD CAMERA** menu.

To add a camera to the camera list manually:

1.  Enter the camera's network information (**IP Address**, **App Port**, and **Password** if applicable) into the text fields below the **ADD CAMERA** banner.
    
    Network Parameters
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/CameraParameters.png)
    
2.  Select **Add Camera** in the bottom right of the **ADD CAMERA** window.
    
    Add Camera
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Add Camera/AddFromCameraList.png)
    

The camera is now added to the camera list.

### Edit IP

The **Edit IP** button in the **ADD CAMERA** window allows for the selected camera to have its IP settings changed. Select a camera in the camera list, then select **Edit IP** to open the **Edit IP Settings** window.

Edit IP Settings

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/EditIP-DCHP.png)

By default, cameras are set to DCHP. Select **Static IP** under the IP Type header to enter network settings manually.

Edit Static IP

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/EditIP-StaticIP.png)

Select **Save Settings** to confirm network changes to the camera.

## Delete Camera

To delete a camera from the camera list:

1.  Select **Delete** on the desired camera in the camera list.
    
    Delete Camera
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/DeleteCamera.png)
    
    A window prompt is displayed stating "The following action will delete the camera. Are you sure you want to proceed?".
    
    Window Prompt
    
    ![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Camera List Delete.png)
    
2.  Select **Ok**.
    

The camera is now deleted from the software. To add the camera back to the software, refer to [Add a Configured Camera](#ExistingCamera).

## Delete All Cameras

To delete all cameras from the camera list, right click on the camera list. Then, select either **Clear All Cameras** to remove all cameras from the camera list, or select **Clear Offline Cameras** to remove just inactive cameras from the camera list.

Clear All Cameras

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/Clear-All-Cameras.png)

The cameras are now deleted from the software. To add cameras back to the software, refer to [Add a Configured Camera](#ExistingCamera).

## Identify Cameras

Once cameras are added to the software, they can be identified by having their light bar flash for 10 seconds. To have the respective camera's light bar flash, select the eyeball symbol on the top left of the desired camera in the camera list.

Identify Camera

![](../../../Resources/Images/1BCameraManager/Camera Manager Screenshots/EyeballCameraList.png)
