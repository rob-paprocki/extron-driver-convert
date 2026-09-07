Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/Telnet.htm

Tesira Software Help

Click here to see this page in full context

# Telnet

Please also review the Troubleshooting TTP which gives information on configuring a PC to connect to a Tesira system for testing purposes.

Telnet is configured by specifying the IP address of the Tesira Server and connecting via port 23. A maximum of 32 Telnet connections per server are supported. The ability for Tesira SERVER, SERVER I/O, Tesira Amplifiers, or TesiraFORTÉ devices to use Telnet can be enabled or disabled via a DEVICE TTP command or in the Device Maintenance Settings Network Settings dialog.

When controlling multiple Tesira units that are not part of the same TMF file, each Tesira Server unit will need to be addressed via its own Telnet Session. Commands sent via Telnet are not encrypted.

### VoIP Telnet

The option to disable Telnet connections (port 23) on the VoIP enabled FORTÉ and Server devices is available from within the VoIP Property Sheet. This is an engineering diagnostic interface only however for installations with security concerns about this port being open, it can be disabled. Also refer to the VoIP Property Sheet to disable HTTP or HTTPs access to the VoIP management webpage.

## Negotiation Required to Establish a Telnet Control Session

### Session Options

Tesira implements a Telnet server on port 23. When the request from the control system to open a session is received, the Tesira Telnet server attempts to negotiate the session’s options, following specifications described in the Telnet standard document RFC 854 as well as document RFC 855, Telnet Option Specifications.

A standard Telnet client would be able to negotiate the session options without problem, but several third party controllers do not implement a Telnet client by default. Instead, they implement control over TCP/IP using what’s commonly known as a ‘RAW’ connection. If the Control System does not respond to the Telnet session options negotiations, the session will not go ahead. As such, the control system will have to be programmed to negotiate the Telnet options with Tesira’s Telnet server. Many of the available options can be useful during a control session and indeed a programmer may choose to enable some of them, but if the desire is to continue using a ‘RAW’ connection, the simplest way to initiate a control session is for the control system to respond with a rejection to any option negotiation request from the server.

### Negotiation

The best way to understand the Telnet options negotiation procedure is by looking at the data in Hex format. Notation will be “0xFF” for Hex character FF.

The Telnet commands we are concerned with are always three bytes long. The first is the Interpret As Command (IAC) character, and it is always 0xFF. The second character is the Command and the last character is the Option being negotiated.

Commands can be:

* WILL, or 0xFB

* DO, or 0xFD

* DON’T, or 0xFE

* WON’T, or 0xFC

Negotiated options can be (but not limited to*):

* Binary Transmission, 0x00

* Echo, 0x01

* Suppress Go Ahead, 0x03

* Status, 0x05

* Terminal Type, 0x18

* There are many different Telnet options in existence; a list is maintained by IANA http://www.iana.org/assignments/telnet-options

The control system needs to react to any incoming string that begins with 0xFF, and decide whether the option is desired or not. If the intent is to control Tesira using a ‘raw’ connection, all that’s required is to always reject the option negotiation. If Tesira sends a “WILL” Command, the control system shall respond with “DON’T”, and if Tesira sends a “DO”, the response should be “WON’T”. The Option byte needs to be returned as received.

In essence, the mechanism is as follows:

| When the server sends | 0xFF | WILL |  |

| The control system responds with | 0xFF | DON'T |  |

| When the server sends | 0xFF | WILL |  |

| The control system responds with | 0xFF | DON'T |  |

### Examples

| Source | IAC | Command | Option | Notes |

| Tesira Server | 0xFF | 0xFD | 0x01 | Do Echo |

| Control System / Client | 0xFF | 0xFC | 0x01 | Won't Echo |

| Source | IAC | Command | Option | Notes |

| Tesira Server | 0xFF | 0xFB | 0x03 | Will Suppress Go Ahead |

| Control System / Client | 0xFF | 0xFE | 0x03 | Don't Suppress Go Ahead |

Once all options are negotiated, the Tesira server will send the message “Welcome to the Tesira Text Protocol Server”, preceded and followed by 0x0D and 0x0A. The control system is now free to send TTP commands.

## Other Considerations

Please note that the Tesira server will usually end any string with either 0x0D (CR character) followed by 0x0A (LF character), but as per Telnet RCF it may also use 0x0D (CR character) followed by 0x00 (NUL character). As such, the third party control system must be able to read one more character after it sees a 0x0D, which will always be either 0x0A or 0x00, and handle them appropriately.

In addition, and while in practice most of the negotiations will always take place at the beginning of a session, Telnet allows for them to happen at any point during the session.

## Example Negotiation

Below is an example session options negotiation at the beginning of a Telnet session between Tesira and a TCP Client which was programmed to reject all options offered by the server. Please note this is for illustrations purposes only and the order and quantity of options negotiated may vary depending on firmware release. Strings have been organized below for clarity; however multiple Telnet strings may arrive from the Server in one Ethernet frame. Responses can be sent one at the time, or multiple responses in a single frame.

| Source | IAC | Command | Option | Notes |

| Tesira Server | 0xFF | 0xFD | 0x18 | Do Terminal Type |

| Client | 0xFF | 0xFC | 0x18 | Won't Terminal Type |

| Tesira Server | 0xFF | 0xFD | 0x20 | Do Terminal Speed |

| Client | 0xFF | 0xFC | 0x20 | Won't Terminal Speed |

| Tesira Server | 0xFF | 0xFD | 0x23 | Display Location |

| Client | 0xFF | 0xFC | 0x23 | Won’t X Display Location |

| Tesira Server | 0xFF | 0xFD | 0x27 | Do New Environment Option |

| Client | 0xFF | 0xFC | 0x27 | Won't New Environment Option |

| Tesira Server | 0xFF | 0xFD | 0x24 | Do Environment Option |

| Client | 0xFF | 0xFC | 0x24 | Won't Environment Option |

| Tesira Server | 0xFF | 0xFB | 0x03 | Will Suppress Go Ahead |

| Client | 0xFF | 0xFE | 0x03 | Don’t Suppress Go Ahead |

| Tesira Server | 0xFF | 0xFD | 0x01 | Do Echo |

| Client | 0xFF | 0xFC | 0x01 | Won’t Echo |

| Tesira Server | 0xFF | 0xFD | 0x22 | Do Linemode |

| Client | 0xFF | 0xFC | 0x22 | Won’t Linemode |

| Tesira Server | 0xFF | 0xFD | 0x1F | Do Negotiate About Window Size |

| Client | 0xFF | 0xFC | 0x1F | Won't Negotiate About Window Size |

| Tesira Server | 0xFF | 0xFB | 0x05 | Will Status |

| Client | 0xFF | 0xFE | 0x05 | Don't Status |

| Tesira Server | 0xFF | 0xFD | 0x21 | Do Remote Flow Control |

| Client | 0xFF | 0xFC | 0x21 | Won't Remote Flow Control |

| Tesira Server | 0xFF | 0xFB | 0x01 | Will Echo |

| Client | 0xFF | 0xFE | 0x01 | Don’t Echo |

| Tesira Server | 0xFF | 0xFD | 0x06 | Do Timing Mark |

| Client | 0xFF | 0xFC | 0x06 | Won't Timing Mark |

| Tesira Server | 0xFF | 0xFD | 0x00 | Do Binary Transmission |

| Client | 0xFF | 0xFC | 0x00 | Won't Binary Transmission |

| Tesira Server | 0xFF | 0xFB | 0x03 | Will Suppress Go Ahead |

| Client | 0xFF | 0xFE | 0x03 | Don’t Suppress Go Ahead |

| Tesira Server | 0xFF | 0xFB | 0x01 | Will Echo |

| Client | 0xFF | 0xFE | 0x01 | Don’t Echo |

| Tesira Server | 0xFF | 0xFD | 0x0A |  |

| Tesira Server | 0x0D 0x0A Welcome to the Tesira Text Protocol Server 0x0D 0x0A |
