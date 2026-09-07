Source: https://tesira-software-help.biamp.com/assets/TOC/System_Control/Tesira_Text_Protocol/TTP_Syntax.htm

Tesira Software Help

Click here to see this page in full context

# TTP Syntax

The Services Code defines a instruction and function for a DSP block to perform. The Attribute Code defines the portion of the DSP block to be controlled such as a fader level. Each element of the command instruction is delimited by a single space. The commands are case sensitive and upper and lower case characters are used.

## Instance Tag

The Instance Tag is case sensitive and is the unique name of a software object used in a Tesira project. The Instance Tag can be found when disconnected from the System in the DSP Properties tab of the Properties docking menu. This defaults to the object code when compiled but can be customized by the user. The Tesira compiler will also check for duplicate Instance Tags. Instance tags can be defined within speech marks. If instance tags have no spaces they do not require speech marks. Instance tags can be numerical and contain spaces. Any Customized Instance tags that contain spaces must be defined within speech marks. Duplicate instance tags are not allowed. If duplicates are created a dialog will appear allowing editing of the tags.

Note: The following Instance Tag characters are illegal: / &

### Available Instance Tags

A Session command can be used to get a listing of available Instance Tags. Any devices that have an incomplete audio path will not be listed.

#### Example

SESSION get aliases

+OK "list":["123" "AudioMeter1" "AudioMeter2" "AudioMeter3" "DEVICE" "Input1" "Mixer1" "Mute1" "Level1" "Output1"]

#### Example - Using an Instance Tag Called Level1

Level1 get level 1

+OK "value":0.000000

#### Example - Instance tags can contain spaces enclosed in speech marks

"my level 2" get level 1

+OK "value":-10.000000

Missing speech marks will return an error:

my level 2 get level 1

-ERR address not found: {"deviceId":0 "classCode":0 "instanceNum":0}

#### Example - Instance Tags may be Numerical

123 get level 1

+OK "value":-10.000000

## Command

The Command field specifies what is to be done with the DSP processing block Attribute. Tesira Text Protocol supports different Attribute commands as listed below. These are case sensitive and the availability of the command would depend on the DSP object Attribute Code. The following table shows the Commands which only apply to Attribute Codes. An Attribute Code may not support all of them, but it will support at least one.

## Attribute

The attribute Code defines the portion of the DSP Processing block to be controlled such as a fader level, crosspoint mute, etc.

## Service

The Services Code defines a instruction and function for a Hardware item to perform or a system wide command such as recalling a Preset. Any Service Code commands do not use Attribute Commands such as get, set, etc. Instead they use their own commands such as recallPreset or dial.

## Index

Attribute Codes use Index fields to refer to inputs, outputs, or cross attribute of a DSP Block. Due to the different types of DSP blocks, some attributes will not require and Index so no value should be used. Some DSP blocks require a single index such as a level control. Some DSP blocks require 2 indexes such as a matrix mixer. The first index would be the Input or Row and the second index would be the Output or Column.

For a Crossover, Index band is indexed by number from high to low, so in a four-way crossover high=1, mid high=2, low mid =3 and low=4. filter is indexed by number. 1 is the high cutoff frequency for each band while 2 is the low.

#### Example - Index values can be Encased in Double Quotes

Mixer1 set crosspoint 1 1 true +OK Mixer1 set crosspoint "1""1" true +OK

When a subscription command is configured a unique custom name can be used in the second Index of the command line. This is used as the identifier for the subscribed item.

Some Service Codes use index fields to define the hardware channel that is being controlled. For example, a Dialer Block will require the line and Call appearance indexes to be specified.

## Value

Value determines what a DSP block is being set to, incremented by, or decremented by. The interface definition tables define which type of value the string will need in order to execute the TTP string.

A TTP value will depend on the attribute being controlled. It can be:

* A number

* A string (in double quotes)

* A Boolean (true or false)

* null

| Required Action | Value Example | Description |

| Turn On | true | Refers to the 'on' state of a processing object component with two states such as a crosspoint, mute or similar. |

| Turn Off | false | Refers to the 'off' state of a processing object component with two states such as a crosspoint, mute or similar. |

| Adjust Level (set, increment, decrement) | 1.0 -1.0 -15 etc... | A numerical decimal value used to represent the new state. For a 'set' command this will move the value to the specified level. For an increment it will adjust the value from the current value by the specified amount. |

| State | BUTTERWORTH | A text string can be used to represent a value such as a filter type |

| Preset | 1001 | An Integer that is the required state. |

## Special Addresses

### Device

The local unit currently connected. See Device for a full listing of commands.

| Instance Tag | Command | Attribute Code | Index | Line_Feed |

| DEVICE | get | ipStatus | interface | LF |

### Session

The current RS-232, Telnet or SSH text session. See Session for a full listing of commands.

| Instance Tag | Command | Attribute Code | Value | Line_Feed |

| SESSION | set | Verbose | false | LF |
