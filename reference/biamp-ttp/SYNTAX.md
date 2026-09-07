# Tesira Text Protocol (TTP) — syntax reference

Sources for every claim below are cited inline as `pages/<File>.md` (harvested verbatim from the
URL on that file's `Source:` line) or `data/<file>` (raw/parsed data extracted from a page).
See `INDEX.md` for how the page set was enumerated.

## 1. Command grammar

Two distinct command shapes exist, both stated explicitly on the TTP Syntax page
(`pages/TTP_Syntax.md`):

**Attribute commands** (act on a DSP processing-block attribute, e.g. a fader level):

```
Instance_Tag Command Attribute [Index] [Value] LF
```

**Service commands** (act on a whole hardware item / system-wide function, e.g. recalling a
preset — no get/set-style verb at all):

```
Instance_Tag Service [Index] [Value] LF
```

Quoted directly (`pages/TTP_Subscriptions.md`, restating the general form used for
subscribe/unsubscribe too):

> **Instance_Tag Command Attribute [Index] [Value] LF**
>
> * Instance Tag: Is always required.
> * Command: Is always required.
> * Attribute: Is always required.
> * [Index]: Is shown in [Brackets] as may be required depending on the Attribute being
>   referenced. If not required it should not be defined. Depending on the Attribute, it can be
>   made up of one or more indexes.
> * [Value]: Is shown in [Brackets] as may be required depending on the Command or Attribute
>   being referenced. If not be required it should not be defined. The Value would not normally
>   have spaces, if it does it can be defined in "double quotes". It can also be a numerical
>   value.
> * **LF:** A Line feed or Carriage Return is used to define the end of the command.

And for Service commands (`pages/Device.md`):

> Instance_Tag Service [Index] [Value] LF
>
> * Instance Tag: Is always required.
> * Service: Is always required.
> * [Index]: Is shown in [Brackets] and may be required depending on the Attribute being
>   referenced. If not required it should not be defined. Depending on the Attribute, it can be
>   made up of one or more indexes.
> * [Value]: Is shown in [Brackets] and may be required depending on the Command or Attribute
>   being referenced.

Each element is delimited by (at least) a single space (`pages/TTP_Syntax.md`: "Each element of
the command instruction is delimited by a single space"; `pages/Session.md` says "one or more
spaces"). **Commands are case sensitive** and mix upper/lower case (`pages/TTP_Syntax.md`,
`pages/Device.md`): e.g. `SESSION` (all caps, a special address) vs. `get`/`set` (lowercase verbs)
vs. `aecEnable` (mixed-case attribute code). `pages/TTP_Responses.md` shows the practical effect:
`SESSION Get aliases` (capital G) fails with a parse error, and `SESSION get Aliases` (capital A)
fails because the attribute code doesn't case-match.

### Element definitions (`pages/TTP_Syntax.md`, "Instance Tag" / "Command" / "Attribute" /
"Service" / "Index" / "Value" sections)

* **Instance Tag** — "the unique name of a software object used in a Tesira project"; case
  sensitive; found in the DSP Properties tab when disconnected; defaults to the compiled object
  code but user-customizable; duplicates are rejected by the compiler. Illegal characters: `/`
  and `&`. May be numerical. May contain spaces **only** if enclosed in double quotes (unquoted
  tags with spaces fail with `-ERR address not found: ...`). Special reserved instance tags:
  `DEVICE` (the locally-connected unit) and `SESSION` (the current RS-232/Telnet/SSH text
  session) — both must be capitalized (`pages/TTP_Syntax.md`, "Special Addresses"; `pages/Session.md`;
  `pages/Device.md`).
* **Command** — "specifies what is to be done with the DSP processing block Attribute."
  Case-sensitive; availability depends on the specific Attribute Code (an attribute supports at
  least one command, not necessarily all).
* **Attribute** (Attribute Code) — "defines the portion of the DSP Processing block to be
  controlled such as a fader level, crosspoint mute, etc."
* **Service** (Service Code) — "defines a instruction and function for a Hardware item to
  perform or a system wide command such as recalling a Preset. Any Service Code commands do not
  use Attribute Commands such as get, set, etc. Instead they use their own commands such as
  recallPreset or dial." I.e. the Service Code itself *is* the verb+object in one token; there is
  no separate Command field.
* **Index** — refers to inputs/outputs/cross-points of a DSP block; 0, 1 or 2 index fields
  depending on the attribute (e.g. a level control needs one index, a matrix mixer's crosspoint
  needs two: "The first index would be the Input or Row and the second index would be the Output
  or Column"). Crossover blocks index `band` high-to-low (`1`=high, `2`=mid-high, `3`=low-mid,
  `4`=low) and `filter` by `1`=high cutoff, `2`=low cutoff. Index values may be enclosed in
  double quotes: `Mixer1 set crosspoint "1""1" true` is equivalent to
  `Mixer1 set crosspoint 1 1 true`. For a subscribe command, a second Index slot carries a
  free-form custom subscription-identifier name.
* **Value** — what an attribute is set to / incremented by / decremented by. Per
  `pages/TTP_Syntax.md`'s Value table (verbatim):

  | Required Action | Value Example | Description |
  |---|---|---|
  | Turn On | `true` | Refers to the 'on' state of a processing object component with two states such as a crosspoint, mute or similar. |
  | Turn Off | `false` | Refers to the 'off' state of a processing object component with two states such as a crosspoint, mute or similar. |
  | Adjust Level (set, increment, decrement) | `1.0` `-1.0` `-15` etc... | A numerical decimal value used to represent the new state. For a 'set' command this will move the value to the specified level. For an increment it will adjust the value from the current value by the specified amount. |
  | State | `BUTTERWORTH` | A text string can be used to represent a value such as a filter type |
  | Preset | `1001` | An Integer that is the required state. |

  Value type is one of: a number, a string (in double quotes), a Boolean (`true`/`false`), or
  `null`.

### Special addresses (`pages/TTP_Syntax.md`, `pages/Device.md`, `pages/Session.md`)

* `DEVICE` — the locally-connected unit; e.g. `DEVICE get ipStatus interface LF`.
* `SESSION` — the current RS-232/Telnet/SSH session; e.g. `SESSION set Verbose false LF`.
  `SESSION get aliases` returns the list of live Instance Tags in the system (example,
  `pages/TTP_Syntax.md`):

  ```
  SESSION get aliases
  +OK "list":["123" "AudioMeter1" "AudioMeter2" "AudioMeter3" "DEVICE" "Input1" "Mixer1" "Mute1" "Level1" "Output1"]
  ```

## 2. Full verb set

The TTP Syntax page (`pages/TTP_Syntax.md`) *describes* that a verb table exists ("Tesira Text
Protocol supports different Attribute commands as listed below... The following table shows the
Commands which only apply to Attribute Codes") but — verified against the page's own raw HTML —
**the table itself is absent from the published page** (no `<table>` and no image follow that
paragraph; confirmed by fetching the page as raw HTML and searching for both). This is a genuine
gap in Biamp's published syntax page, not a fetch/conversion artifact on this side.

The full verb set was instead recovered from two other sources that both **use** the verbs
concretely, cross-checked against each other:

**A. Attribute Table pages** (`pages/Device.md`, `pages/Session.md`) list a `Command` column per
attribute as a `/`-joined subset. Observed combinations on the Device attribute table alone:
`get`, `get / set`, `get / set / toggle`, `get / set / increment / decrement`,
`get / subscribe / unsubscribe`.

**B. The command-string-calculator's embedded data** (`data/calculator_blocks.json`, extracted
from `pages/Command_String_Calculator.md`) — the union of every string in every attribute's
`"commands": [...]` array across all 92 parsed block types:

* **Attribute-level (generic, DSP-object) verbs:** `get`, `set`, `toggle`, `increment`,
  `decrement`, `subscribe`, `unsubscribe`.
* **Dialer-block call-control verbs** (used the same syntactic slot as the generic verbs above,
  but specific to the Dialer block's attributes): `answer`, `dial`, `dtmf`, `end`, `flash`,
  `hold`, `lconf`, `offHook`, `onHook`, `redial`, `resume`, `send`, `speedDial`.
* **The empty-string verb `""`** — used by Service-style attributes/Device & Session Services
  (e.g. `recallPreset`, `recallPresetByName`, `recallPresetShowFailures`, `savePreset`,
  `savePresetByName`, `reboot`, `startAudio`, `stopAudio`, `startMedia`, `stopMedia`,
  `startPartitionAudio`/`stopPartitionAudio`, `startPartitionMedia`/`stopPartitionMedia`,
  `manualFailover`, `rebootERD`, `restoreERDToFactoryDefaults`, `syncERDFirmware`,
  `injectDanteLicenseKey`, `verifyDanteLicenseKey`, `getLocalCopyOfFile`,
  `resetWebServerCredentials`, `deleteConfigData`, `clearWorkplace`, `clearLogs`,
  `clearEventLogs`, `defaultLogConfig`, `sleep`, `wake`) — confirming the Syntax page's statement
  that "Any Service Code commands do not use Attribute Commands such as get, set, etc. Instead
  they use their own commands such as recallPreset or dial." The widget's own assembly code
  treats this explicitly: `if (command && command !== "") { commandstring += " " + command; }`
  (`pages/Command_String_Calculator.md`) — i.e. for Service attributes no separate command token
  is emitted at all; the Service Code goes straight after the Instance Tag.

`recallPreset` example from `pages/Device.md`:

```
Reboot the connected device. Result: DEVICE reboot
| Instance Tag | Service |
| DEVICE | reboot |
```

and the Device Services table (`pages/Device.md`) lists every Service Code with its parameters
verbatim, e.g. `recallPreset PresetId id`, `recallPresetByName presetName`,
`rebootERD HostnameList hostnames, HostnameList failedDevices`.

## 3. Token quoting rules

From `pages/TTP_Syntax.md`:

* Instance tags containing spaces **must** be double-quoted; unquoted, the command fails:

  ```
  "my level 2" get level 1
  +OK "value":-10.000000

  my level 2 get level 1
  -ERR address not found: {"deviceId":0 "classCode":0 "instanceNum":0}
  ```

* Index values may optionally be double-quoted even without spaces —
  `Mixer1 set crosspoint 1 1 true` and `Mixer1 set crosspoint "1""1" true` are both `+OK`.
* Values: "The Value would not normally have spaces, if it does it can be defined in 'double
  quotes'." (`pages/TTP_Subscriptions.md`)

The command-string calculator's `trim()` helper (`pages/Command_String_Calculator.md`, quoted
verbatim from the page's own JS) gives the precise, tool-authoritative version of this rule:

```js
function trim(s) {
  s = s.replace(/(^\s*)|(\s*$)/gi, "");
  // Don't add quotes around lists or JSON objects
  if (["[", "{"].indexOf(s[0]) >= 0 && ["]", "}"].indexOf(s[s.length - 1]) >= 0) {
    return s;
  }
  // Add quotes around strings with spaces or commas
  if (s.indexOf(" ") >= 0 || s.indexOf(",") >= 0) {
    s = '"' + s + '"';
  }
  return s;
}
```

I.e.: a token that already looks like a JSON array/object (`[...]`/`{...}`) is left unquoted; any
other token containing a space or comma is wrapped in `"..."`; everything else (bare numbers,
bare words, `true`/`false`) is emitted unquoted.

## 4. Line terminator

"A line feed needs to be sent after each command." (`pages/Tesira_Software_System_Control_Overview.md`)
The Subscribe/Unsubscribe grammar statements both end in an explicit `LF` token:
"**LF:** A Line feed or Carriage Return is used to define the end of the command."
(`pages/TTP_Subscriptions.md`). The Telnet page gives the low-level detail
(`pages/Telnet.md`, "Other Considerations"):

> Please note that the Tesira server will usually end any string with either 0x0D (CR character)
> followed by 0x0A (LF character), but as per Telnet RCF it may also use 0x0D (CR character)
> followed by 0x00 (NUL character). As such, the third party control system must be able to read
> one more character after it sees a 0x0D, which will always be either 0x0A or 0x00, and handle
> them appropriately.

## 5. Responses / acknowledgements, including errors

Success responses are prefixed `+OK`; error responses are prefixed `-ERR` (or a small set of
other `-`-prefixed codes, below). From `pages/Tesira_Software_System_Control_Overview.md`:

> TTP has built in error handling and the response will indicate the reason and location in the
> command where an error has been encountered. An error response will include -ERR at the
> beginning of the response. A successful response will include +OK at the beginning of the
> response.

### Verbose vs. non-verbose (concise) output

Controlled by `SESSION set verbose true|false` (a Session attribute; see `pages/Session.md`,
`detailedResponse`/`verbose` attributes with `get / set / toggle` commands and `false, true`
value range). From `pages/TTP_Responses.md`:

```
Verbose:
+OK "time":"12:00" "number":"503-367-3568" "line":"2"

Non-Verbose:
+OK "12:00" "503-367-3568" "2"
```

```
SESSION set verbose true
Mute1 get numChannels
+OK "value":2

SESSION set verbose false
+OK
Mute1 get numChannels
+OK 2
```

I.e. verbose responses wrap each returned field in a `"key":value` pair; non-verbose/concise
responses emit only the bare values, in the same order, space-separated.

### Error response table (`pages/TTP_Responses.md`, quoted verbatim from the page's HTML table)

| TTP Command String | Message | Resolution |
|---|---|---|
| *(none — success case)* | `+OK` | The command was understood and completed successfully. |
| `Session get  aliases` | `-ERR address not found: {"deviceId":0 "classCode":0 "instanceNum":0}` | The requested address is not valid due to incorrect formatting. The Address field is case sensitive. Session commands must be in capitals. Reformat the command as `SESSION get aliases`. |
| `SESSION Get aliases` | `-ERR Parse error at 8: verb was not one of the commands supported by Services` | There is a problem 8 characters into the command. The `get` command is incorrectly formatted - it has a capital 'G'. Reformat the command as `SESSION get aliases`. |
| `SESSION get Aliases` | `-ERR 'Aliases' is not supported by TextSession::Attributes` | `Aliases` is not correctly formatted. It has a capital 'A'. Reformat the command as `SESSION get aliases`. |
| `Mixer1 set inputMute 1` | `-ERR Parse error at 22: not enough parameters supplied` | The command is missing the value. Reformat the command as `Mixer1 set inputMute 1 true`. |
| `Mixer1 get inputLevel 1` | `+OK "value":0.000000` | The command was delivered and the value of the Input level is 0.0dB. |
| `Input1 get gain channel1` | `-ERR Parse error at 16: could not parse value` | `Channel1` command is invalid. The Input block channel is numerical. Reformat the command as `Input1 get gain 1`. |
| `AudioMeter2 subscribe level 3 mymeter 1000` | `! "publishToken":"mymeter" "value":-100.000000` then `+OK` | A subscribe of the meter refreshing every 1 second. |
| `MyLevel1 get level 10` | `-ERR INVALID_PARAMETER Index out of range:channelIndex min:1 max:8 received:10` | Channel 10 not available. Index indicates channels 1 to 8 available. |
| *(unspecified command)* | `-ERR WRONG_STATE` | VoIP card has received a command it cannot action (For example if the card is not connected to the Call Manager and is given a request to make a call) |
| *(unspecified command)* | `-CANNOT_DELIVER` | Typically seen on a system with multiple Server devices when connected to one Server and addressing a DSP object in another server. Would indicate a communication issue between servers. |
| *(unspecified command)* | `-GENERAL_FAILURE` | A 'catch all' error code. Can occur when referencing a Instance Tag that is not in the Tesira file. |

Types of errors enumerated in prose (`pages/TTP_Responses.md`, "TTP Feedback"):

> * Can't forward a request to a device that's not on the network
> * If an invalid address is used
> * If an invalid attribute or service for a block type (it might be valid for a different object)
> * Right address, right attribute or service, but the request doesn't make sense given the state of the target object
> * Case-and-spelling errors of various kinds

## 6. Subscription mechanism

From `pages/TTP_Subscriptions.md`:

> Subscriptions enable the updating of metering and level values to be sent to a external
> control system without the control system requesting information.
>
> Elements of a processing object can be subscribed to such as channel levels and meters. The
> Attribute tables will indicate which functions support subscription.
>
> If subscriptions are used the Tesira server may be sending back replies that were not
> individually requested from the control system (they were subscribed to). All subscribed
> objects will be preceded by a `!` "publishToken" statement [that] would indicate to the control
> system that the returned packet is from a subscription not a response to a command that was
> just sent.
>
> Subscriptions are lost when the Tesira server is rebooted or a change in configuration is sent
> to the system. Subscriptions can be revalidated by subscribing to the same block at regular
> intervals. If this is done ensure that the custom label used in Index is used in the
> re-subscription. If this label is not included it is possible to inadvertently open multiple
> subscriptions to the same call state.

### Subscribe

```
Instance Tag  Command    Attribute Code  Index  Index         Value
MyLevel1      subscribe  level           1      MyLevelName   500
```

(the two Index slots are: the attribute's own index, e.g. channel `1`; then a free-form custom
subscription name; `Value` here is the refresh interval in ms.)

Verbose subscription response format (`pages/TTP_Subscriptions.md`, quoted verbatim):

```
! "publishToken":"[CustomName]" "value":[Value]     <- first reply appends +OK
! "publishToken":"[CustomName]" "value":[Value]     <- subsequent replies
```

> The [CustomName] is used as an identifier. The identifier returned is specified in the Index
> field of the original subscribe command. This name can then be used in a parsing routine for
> the subscribed item. If no identifier is specified then empty double speech-marks ("") are
> shown in the response as a delimiter.
>
> The [Value] is the current state of the control being subscribed to. This will be formatted as
> an integer or boolean depending on the subscription attribute.

Verbose example:

```
MyLevel1 subscribe level 1 MyLevelName 500
! "publishToken":"MyLevelName" "value":-100.000000
+OK
! "publishToken":"MyLevelName" "value":-98.099998
! "publishToken":"MyLevelName" "value":-77.800003
! "publishToken":"MyLevelName" "value":-35.299999
```

Without a custom name, the publishToken is empty:

```
MyLevel1 subscribe level 1
! "publishToken":"" "value":-100.000000
+OK
! "publishToken":"" "value":-98.099998
...
```

Non-verbose subscription response format (set `SESSION set verbose false` **before**
subscribing):

```
! "[CustomName]" [Value]     <- first reply appends +OK
! "[CustomName]" [Value]     <- subsequent replies
```

Example:

```
Welcome to the Tesira Text Protocol Server...
SESSION set verbose false
+OK
MyLevel1 subscribe level 1 myLevelName 500
! "myLevelName" -40.244328
+OK
! "myLevelName" -38.992748
! "myLevelName" -41.044147
! "myLevelName" -40.063908
! "myLevelName" -38.674465
```

### Unsubscribe

Grammar (`pages/TTP_Subscriptions.md`, quoted verbatim):

> **Instance_Tag Command Attribute [Index] [Index] LF**
>
> * Instance Tag: Is always required. Is the same Instance Tag used to originally subscribe.
> * Command: Is always required. Is the same Command used to originally subscribe.
> * Attribute: Is always required. Is the same Attribute used to originally subscribe.
> * [Index]: Is required if specified as part of the Attribute. Is the same Attribute index or
>   indexes used to originally subscribe.
> * [Index]: Is required if specified as part of the original subscription. Must match the
>   custom name given in the original subscription.
> * **LF:** A Line feed or Carriage Return is used to define the end of the command.

```
Instance Tag  Command      Attribute Code  Index  Index
MyLevel1      unsubscribe  level           1      MyLevelName
```

Example round-trip:

```
MyLevel1 subscribe level 1 MyLevelName 500
! "publishToken":"MyLevelName" "value":-100.000000
+OK
! "publishToken":"MyLevelName" "value":-98.099998
...
MyLevel1 unsubscribe level 1 MyLevelName
+OK
```

**If an Index and value have been specified in the original subscribe request they must be used
in the unsubscribe request** (`pages/TTP_Subscriptions.md`), and re-subscribing at intervals to
keep a subscription alive across reboots must reuse the same custom label or risks opening
duplicate subscriptions.

## 7. Transports (context for the protocol, each independently confirmed)

* **RS-232** (`pages/RS-232.md`) — one or two ports depending on device; each port independently
  configurable for Command-String-Block output, full-duplex TTP, both, or neither, or Control
  Tunneling; baud rate one of 300/1200/2400/4800/9600/19200/38400/57600/115200; default port
  roles/baud differ per device (table given verbatim in the page); pinout given (TxD pin 2, RxD
  pin 3, rest unused); unsecured systems require no auth, secured systems require login until an
  explicit `exit`.
* **Telnet** (`pages/Telnet.md`) — port 23, max 32 connections/server, unencrypted; standard
  RFC 854/855 option negotiation (IAC=`0xFF`, commands `WILL`/`DO`/`DON'T`/`WON'T` =
  `0xFB`/`0xFD`/`0xFE`/`0xFC`); a control system wanting a raw/TCP-only session should reject
  every negotiated option (`WILL`→respond `DON'T`, `DO`→respond `WON'T`); server then sends
  `"Welcome to the Tesira Text Protocol Server"` framed by CR/LF, after which TTP commands may be
  sent.
* **SSH** (`pages/SSH.md`) — port 22, encrypted, max 80 connections/server (soft failures begin
  at 64, hard refusal at 80 — described as a DDoS mitigation); case-sensitive
  username/password; unprotected-system default `default`/no password.
* **Security** (`pages/TTP_Security.md`) — same password levels apply across all three
  transports; `controller`-or-higher required to change state, `observer` can only query;
  unprotected-system credentials `default`/`default`; on a protected system the `default` user is
  downgraded to `observer`. RS-232 in a secured system doesn't require re-auth until an explicit
  `exit` is sent, even across physical disconnect/reconnect.
