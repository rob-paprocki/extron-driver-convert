Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Security.htm

Tesira Software Help

Click here to see this page in full context

# TTP Security

Establishing an SSH connection to the TTP server requires login credentials by definition.

In a protected Tesira system, the same password access levels apply to all connections to the Tesira Text Protocol (TTP) Server. Please review the System Security settings that can be configured on the Tesira Servers.

Opening a Telnet or SSH session to a Tesira Server results in a login prompt. Valid credentials must be provided to access the system in any way. One must be logged in as controller or higher level to make any changes to the system, while an observer can only query the system for levels and other current parameters.

In an unprotected system, the username and password are ‘default’ and ‘default’ respectively. In a protected system, the credentials configured in the system must be provided, excepting that the "default" user is downgraded to a system access level of "observer".

RS-232 Serial connections to the TTP servers also require authentication in protected systems. Making the serial connection and sending a line feed will reveal the login prompt.

If a system has security enabled the RS-232 will not require authentication until the connection is fully terminated using a 'exit' command. There will then be a requirement to authenticate at the next log on.

Once logged in to the TTP server via RS-232, this user has access until a 'exit' command is sent, even if the serial connection is removed and restored.
