     | IV-CAM Series Manual               

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

# VISCA Intelligent Switching Commands

Intelligent Switching with Crestron 1 Beyond Cameras is controlled using the VISCA protocol through a TCP connection. For more information about Intelligent Switching and how it is configured, refer to [Intelligent Switching](Multi-Camera-Switching-Config.htm).

Below is a comprehensive list of VISCA commands that can be used to control the cameras.

## Placeholder Text Key

Refer to the following table for information about what certain placeholder letters indicate in the Intelligent Switching VISCA commands:

 

Placeholder Letter

Definition

X

Camera Address

Z

Camera ID (2, 3, 4, 5)

W

IP Address (each W represents one digit of the IP address in hexadecimal)

## Intelligent Switching Commands List

The following VISCA commands are used to configure and operate Intelligent Switching.

   

Command

Command Packet

Ack Response

Comments

Set Camera (IP Address)

8x c2 01 09 0Z 0W 0W 0W 0W 0W 0W 0W 0W ff

Y0 41 FF Y0 51 FF

Sets the camera IP to be used for Intelligent Switching

Get Camera

8x c2 09 09 0Z ff

Y0 50 0Z 0W 0W 0W 0W 0W 0W 0W 0W ff

Returns the camera IP that is used for Intelligent Switching

Clear All Cameras Set

8x c2 01 0A 00 ff

Y0 41 FF Y0 51 FF

Clears all cameras set for Intelligent Switching

Call Camera Output (1/2/3/4/5)

8x c2 01 08 0Z ff

Y0 41 FF Y0 51 FF

Calls the camera output during Intelligent Switching

Resume Intelligent Switching

8x c2 01 08 00 ff

Y0 41 FF Y0 51 FF

Resumes Intelligent Switching

Pause Intelligent Switching

8x c2 01 0B 00 ff

Y0 41 FF Y0 51 FF

Pauses Intelligent Switching

Get Output

8x C2 09 08 FF

Intelligent Switching On: 

*   Camera 1: Y0 50 01 01 FF
    
*   Camera 2: Y0 50 01 02 FF
    
*   Camera 3: Y0 50 01 03 FF
    
*   Camera 4: Y0 50 01 04 FF
    
*   Camera 5: Y0 50 01 05 FF
    

Intelligent Switching Off:

*   Camera 1: Y0 50 00 01 FF
    
*   Camera 2: Y0 50 00 02 FF
    
*   Camera 3: Y0 50 00 03 FF
    
*   Camera 4: Y0 50 00 04 FF
    
*   Camera 5: Y0 50 00 05 FF
    

Returns the camera output

Check Connection Status (2/3/4/5)

8x c2 09 0d 0Z ff

Disconnect: Y0 50 00 00 FF  
Connect: Y0 50 00 01 FF

Returns the connection status of the camera and Intelligent Switching

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [VISCA Intelligent Switching Commands](#VISCAIntelligentSwitchingCommands)

*   [Placeholder Text Key](#PlaceholderTextKey)
*   [Intelligent Switching Commands List]