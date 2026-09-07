Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Troubleshooting.htm

Tesira Software Help

Click here to see this page in full context

# TTP Troubleshooting

Brief overview of Tesira Text Protocol troubleshooting steps.

## Configuring a PC to connect to Tesira

Connecting a PC to a Tesira System to troubleshoot may be required. Using a PC allows testing of the strings and responses in real time to prove valid commands are being used. A terminal Emulator program is recommended to connect to the system. Suggested programs include TerraTerm or PuTTY.

Putty is used throughout this document in any examples given this allows connections using RS-232, Telnet or SSH.

If using Telnet or SSH, ensure these services are enabled in Device Maintenance Network Settings or via the Device TTP command.

Opening a Telnet or SSH session to a Tesira Server results in a login prompt. Valid credentials must be provided to access the system in any way. One must be logged in as controller or higher level to make any changes to the system, while an observer can only query the system for levels and other current parameters.

The SSH Login requires case sensitive User and Password authentication. In an unprotected system, the Username and Password are ‘default’ and ‘default’ respectively. In a protected system, the credentials configured in the system must be provided.

PuTTY is a free implementation of Telnet and SSH for Windows and Unix platforms, along with an xterm terminal emulator. This software can be downloaded from the following link: http://www.chiark.greenend.org.uk/~sgtatham/putty/download.html

Instructions on its use can be found here: http://www.chiark.greenend.org.uk/~sgtatham/putty/docs.html

![image](../../../images/System_Control/PuTTY_Configuration.png)

## Configuring a PC to connect to Tesira using Telnet

If you require a secure method to connect to a Tesira Server, please refer to connecting via SSH.

The use of a terminal emulation program such as PuTTY is recommended in order to establish a command session to a Tesira Server.

If the convenience of using the Windows command prompt to initiate a Telnet session is required, you can use Windows Programs and Features to enable the Telnet Client.

* To enable Telnet navigate to: Start > Control Panel > Programs & Features > Turn Windows Features on and off

* Find the entry for Telnet Client

* Select the tick box

* Select OK

* To Initiate a TELNET session with a Tesira Server:

* Select Start>programs>accessories> Command Prompt

* At the command prompt type telnet xxx.xxx.xxx.xxx (xxx.xxx.xxx.xxx is the IP address of the Tesira Server.)

![image](../../../images/System_Control/PuTTY_CommandPrompt.png)

Tesira Text Protocol will provide user feedback if a command is incorrect. The response will vary depending on the command, please review the Responses section for more details.
