Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Attribute_Tables/Service_Addresses/Session.htm

Tesira Software Help

Click here to see this page in full context

#### TTP Attribute Table | Generate command strings with: Tesira Command String Calculator

# Session

The SESSION Instance Tag is case sensitive and must be in capital letters. It is used to send session specific Attributes and Commands. This includes the response method and can be used to query the commands.

Please refer to the TTP section of the Tesira Software System Control Overview page for more details on the controlling Tesira devices using the TTP protocol.

Each element of the command instruction is delimited by one or more spaces. The commands are case sensitive and upper and lower case characters are used.

The TTP string to adjust a DSP object attribute is structured in the following order:

Instance_Tag Command Attribute [Index] [Value] LF

* Instance Tag: Is always required.

* Command: Is always required.

* Attribute: Is always required.

* [Index]: Is shown in [Brackets] and may be required depending on the Attribute being referenced. If not required it should not be defined. Depending on the Attribute, it can be made up of one or more indexes.

* [Value]: Is shown in [Brackets] and may be required depending on the Command or Attribute being referenced. If not be required it should not be defined. The Value would not normally have spaces, if it does it can be defined in "double quotes". It can also be a numerical value.

* LF: A Line feed or Carriage Return is used to define the end of the command.

For additional information on individual elements of a TTP string please review the TTP Syntax page.

| Instance Tag | Command | Attribute Code |

| SESSION | get | aliases |

#### Example

SESSION get aliases +OK "list":["123" "AudioMeter1" "AudioMeter2" "AudioMeter3" "DEVICE" "Input1" "Mixer1" "Mute1" "Level1" "Output1"]

| Attribute | Attribute Code | Command | Indexes | Value Range |

| Alias | alias | get | name |  |

| Aliases | aliases | get |  |  |

| Detailed Responses Enabled | detailedResponse | get / set / toggle |  | false, true |

| Get TTP session ID | sessionID | get |  |  |

| Enable/Disable TTP logging | ttpLoggingEnable | get / set / toggle |  | false, true |

| Verbose Output Enabled | verbose | get / set / toggle |  | false, true |

## Output Styles

A Verbose or concise response can be configured as part of the Session type.

* Verbose: +OK “time”:”12:00” “number”:”503-367-3568” “line”:”2”

* Concise: +OK ”12:00” ”503-367-3568” ”2”

#### Example

SESSION set verbose true Mute1 get numChannels +OK "value":2

SESSION set verbose false +OK

Mute1 get numChannels +OK 2

####
