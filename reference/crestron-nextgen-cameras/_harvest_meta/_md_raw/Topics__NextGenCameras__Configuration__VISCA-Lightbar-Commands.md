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

# VISCA Lightbar Commands

Crestron 1 Beyond cameras feature a lightbar that can be controlled using the VISCA protocol through either a serial (RS‑232 / RS‑485) or TCP connection. By default, the camera's lightbar displays the following colors to reflect their status:

  

Lightbar Color

Camera Status

VISCA Command

Full green

Intelligent camera function ON

8x c1 0C 0C 0C 0C ff

Half green

Camera output ON

8x c1 00 0C 0C 00 ff

Full yellow

Firmware update in progress

8x c1 0F 0F 0F 0F ff

Half red

Privacy Mode ON (camera output OFF)

8x c1 01 0D 0D 01 ff

## Common VISCA Lightbar Commands

Refer to the following table for common VISCA commands that can change the camera's lightbar to the desired color, brightness, and width.

   

Width

Color

Brightness Level

VISCA Command

None

None

None

8x c1 00 00 00 00 ff

Full

Green

Bright

8x c1 0C 0C 0C 0C ff

Full

Green

Medium

8x c1 08 08 08 08 ff

Full

Green

Dim

8x c1 04 04 04 04 ff

Full

Yellow

Bright

8x c1 0F 0F 0F 0F ff

Full

Yellow

Medium

8x c1 0B 0B 0B 0B ff

Full

Yellow

Dim

8x c1 07 07 07 07 ff

Full

Red

Bright

8x c1 0D 0D 0D 0D ff

Full

Red

Medium

8x c1 09 09 09 09 ff

Full

Red

Dim

8x c1 05 05 05 05 ff

Half

Green

Bright

8x c1 00 0C 0C 00 ff

Half

Green

Medium

8x c1 00 08 08 00 ff

Half

Green

Dim

8x c1 00 04 04 00 ff

Half

Yellow

Bright

8x c1 03 0F 0F 03 ff

Half

Yellow

Medium

8x c1 03 0B 0B 03 ff

Half

Yellow

Dim

8x c1 03 07 07 03 ff

Half

Red

Bright

8x c1 01 0D 0D 01 ff

Half

Red

Medium

8x c1 01 09 09 01 ff

Half

Red

Dim

8x c1 01 05 05 01 ff

## Customize the Lightbar

The camera's lightbar can be customized by using a VISCA command to display color and brightness on desired light segments. Refer to the following sections for more information on camera lightbar customization.

### Available Lightbar Segments

Lightbar segments are divided into four groups that each can be customized by VISCA commands. Refer to the following information for details regarding the lights available per lightbar segment:

**IV-CAM-P12 and IV-CAM-P20 series cameras**: The lightbar contains four lightbar segments with 4 lights each, totaling 16 lights.

**IV-CAM-I12-B and IV-CAM-I20 series cameras**: The lightbar contains two outer segments with 4 lights each and two inner segments with 3 lights each, totaling 14 lights.

## Create a Custom VISCA Lightbar Command

To determine the desired brightness and color codes within the VISCA command, the binary values must be translated to hexadecimal code. Refer to the following procedure to create a custom lightbar VISCA command:

**note**: This is an advanced procedure that requires the knowledge of binary values, hexadecimal code, and VISCA commands.

1.  Use the following tables to determine the binary values for the hexadecimal code. The binary value string created should have 16 digits separated into four 4 digit segments.
    
    Brightness Codes
    
     
    
    Brightness levels
    
    Binary Values
    
    OFF
    
    00
    
    Dim
    
    01
    
    Medium
    
    10
    
    Bright
    
    11
    
    Color Codes
    
     
    
    Color Options
    
    Binary Values
    
    Green
    
    00
    
    Red
    
    01
    
    Yellow
    
    11
    
2.  Convert the binary values into hexadecimal code. Each 4 digit segment of the binary value string must be individually converted into hexadecimal values. Each binary value string should result in two hexadecimal characters.
    
3.  Place each separate two character hexadecimal value in sequence with a single space between them.
    
4.  Place the hexadecimal values into the lightbar VISCA command format. The VISCA command structure is as follows (where asterisks \*\*\*\* represent the brightness and color codes in the command):
    
    **8x c1 \*\* \*\* \*\* \*\* ff**
    
5.  The VISCA command can be sent via a serial (RS‑232 / RS‑485) or TCP connection to change the camera's lightbar indicator.
    

The camera's lightbar has now been changed to display the desired brightness and color.

### VISCA Lightbar Command Example

Refer to the following table for the binary values, hexadecimal code, and the VISCA command for bright green on the two inner segments (hereafter referred to as "half-width") lightbar.

Bright Green Half-Width Lightbar Example

  

Binary Value

Hexadecimal Code

VISCA Command

0000 1100 1100 0000

00 0C 0C 00

8x c1 00 0C 0C 00 ff

The VISCA command for the lightbar to display half-width bright green is determined by the following procedure:

1.  The binary values for the bright green half-width lightbar are 0000 1100 1100 0000. Refer to the following explanation on how the binary values were determined:
    
    *   The 0000 binary value correlates with 00 (OFF) and 00 (Green).
        
    *   The 1100 binary value correlates with 11 (Bright) and 00 (Green).
        
2.  The bright green half-width lightbar binary values (0000 1100 1100 0000) are converted into hexadecimal code. Refer to the following explanation on how the hexadecimal code was determined:
    
    *   0000 converted into hexadecimal is 00.
        
    *   1100 converted into hexadecimal is 0C.
        
    
    The result for the bright green half-width lightbar hexadecimal code is 00 0C 0C 00.
    
3.  The hexadecimal code is placed into the VISCA command format (**8x c1 \*\* \*\* \*\* \*\* ff**) to give the final result of 8x c1 00 0C 0C 00 ff.
    
4.  The VISCA command for the bright green half-width lightbar (8x c1 00 0C 0C 00 ff) is sent via a serial (RS‑232 / RS‑485) or TCP connection to the camera.
    

The camera's lightbar now displays as bright green on the two inner segments.

Have feedback on this document? Contact [docfeedback@crestron.com](mailto:docfeedback@crestron.com?subject=Documentation Feedback).

©2026 Crestron Electronics, Inc.

All brand names, product names and trademarks are the property of their respective owners. Certain trademarks, registered trademarks, and trade names may be used to refer to either the entities claiming the marks and names or their products. Crestron disclaims any proprietary interest in the marks and names of others. Crestron is not responsible for errors in typography or photography. Specifications are subject to change without notice.

[Patents](https://www.crestron.com/en-us/legal/patents) | [Legal](https://www.crestron.com/en-us/legal) | [Crestron Europe Terms](https://www.crestron.com/crestroneuropeterms) | [Privacy Policy](https://www.crestron.com/legal/privacy-policy) | [Terms of Use](https://www.crestron.com/legal/website-terms-of-use) | [Support](https://community.crestron.com/)

*   [VISCA Lightbar Commands](#VISCALightbarCommands)

*   [Common VISCA Lightbar Commands](#CommonVISCALightbarCommands)
*   [Customize the Lightbar](#CustomizetheLightbar)

*   [Available Lightbar Segments](#AvailableLightbarSegments)

*   [Create a Custom VISCA Lightbar Command](#CreateaCustomVISCALightbarCom