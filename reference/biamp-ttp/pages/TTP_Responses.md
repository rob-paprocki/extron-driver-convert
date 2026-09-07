Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Responses.htm

Tesira Software Help

Click here to see this page in full context

# TTP Responses

A Verbose or non-verbose response can be configured as part of the Session Command type.

Verbose:

+OK “time”:”12:00” “number”:”503-367-3568” “line”:”2”

Non-Verbose:

+OK ”12:00” ”503-367-3568” ”2”

#### Example

SESSION set verbose true

Mute1 get numChannels

+OK "value":2

SESSION set verbose false

+OK

Mute1 get numChannels

+OK 2

## TTP Feedback

Tesira Text Protocol will provide user feedback if a command is incorrect. The response will vary depending on the command. The Tesira TTP error responses for the most common types of external programming errors include:

* Can’t forward a request to a device that’s not on the network

* If an invalid address is used

* If an invalid attribute or service for a block type (it might be valid for a different object)

* Right address, right attribute or service, but the request doesn’t make sense given the state of the target object

* Case-and-spelling errors of various kinds

Please refer to the table below for some examples and details of some of the expected error responses.

| TTP Command String | Message | Resolution |

|  | +OK | The command was understood and completed successfully. |

| Session get  aliases | -ERR address not found: {"deviceId":0 "classCode":0 "instanceNum":0} | The requested address is not valid due to incorrect formatting. The Address field is case sensitive. Session commands must be in capitals. Reformat the command as SESSION get aliases. |

| SESSION Get aliases | -ERR Parse error at 8: verb was not one of the commands supported by Services | There is a problem 8 characters into the command. The get command is incorrectly formatted - it has a capital 'G'. Reformat the command as SESSION get aliases. |

| SESSION get Aliases | -ERR 'Aliases' is not supported by TextSession::Attributes | Aliases is not correctly formatted. It has a capital 'A'. Reformat the command as SESSION get aliases. |

| Mixer1 set inputMute 1 | -ERR Parse error at 22: not enough parameters supplied | The command is missing the value. Reformat the command as Mixer1 set inputMute 1 true. |

| Mixer1 get inputLevel 1 | +OK "value":0.000000 | The command was delivered and the value of the Input level is 0.0dB. |

| Input1 get gain channel1 | -ERR Parse error at 16: could not parse value | Channel1 command is invalid. The Input block channel is numerical. Reformat the command as Input1 get gain 1. |

| AudioMeter2 subscribe level 3 mymeter 1000 | ! "publishToken":"mymeter" "value":-100.000000

+OK | A subscribe of the meter refreshing every 1 second. |

| MyLevel1 get level 10 | -ERR INVALID_PARAMETER Index out of range:channelIndex min:1 max:8 received:10 | Channel 10 not available. Index indicates channels 1 to 8 available. |

|  | -ERR WRONG_STATE | VoIP card has received a command it cannot action (For example if the card is not connected to the Call Manager and is given a request to make a call) |

|  | -CANNOT_DELIVER | Typically seen on a system with multiple Server devices when connected to one Server and addressing a DSP object in another server. Would indicate a communication issue between servers. |

|  | -GENERAL_FAILURE | A 'catch all' error code. Can occur when referencing a Instance Tag that is not in the Tesira file. |
