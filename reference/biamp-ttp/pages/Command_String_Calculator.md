Source: https://support.biamp.com/Tesira/Control/Tesira_command_string_calculator

# Tesira command string calculator

This tool can be used to generate command strings to control Tesira products. Fill in the
appropriate information in the prompts below to get started. All commands must be terminated
with a "line feed" character (ASCII hex value 0A).

The page body is a MindTouch article whose only static prose is the paragraph above; the
calculator itself is a client-side JS widget mounted at `<div id="calculator"></div>` in the
page HTML. Two inline `<script>` blocks (present verbatim in the fetched HTML, extracted here)
supply (1) a `blocks` data object describing every DSP/Service block type Tesira supports and
(2) the widget logic that walks the user through Block -> Attribute -> Command -> Index(es) ->
Value -> Instance Tag and assembles the final TTP string.

Raw extracted assets (verbatim from the fetched page, saved alongside this file):

* `../data/calculator_blocks.js` — the literal `var blocks = new Array(); blocks["<Name>"] = {...}`
  JS source as shipped in the page (104 `blocks[...]` assignments, some via chained/aliased
  assignment).
* `../data/calculator_blocks.json` — the same data, parsed into JSON for 92 uniquely-keyed block
  entries (1,062 attribute records total), each attribute shaped like:

  ```json
  { "commands": ["get", "set", "toggle"], "commandstring": "aecEnable",
    "description": "AEC Enabled", "indexes": ["channel"],
    "values": ["false", "true"], "valuetype": "discrete" }
  ```

  Fields seen across entries: `commands` (the verb list valid for this attribute — the same
  role as "Command" in the TTP Syntax page), `commandstring` (the Attribute Code / Service Code
  token), `description`, `indexes` (named index slots, e.g. `channel`, `input`, `output`),
  `values` (enumerated legal values for `valuetype: "discrete"`), `valuemin`/`valuemax` (for
  `valuetype: "range"`), `valuedesc` (prompt text for Service-style attributes with no fixed
  `commands`, i.e. `"commands": [""]`), and `valuetype` (`none`, `discrete`, `range`,
  `unbounded`, `date`, `freqgain`, `typeslope`, `delay`, `cmdstr`, `ipconfig`,
  `videoBandwidth`).

## Verb set found in the `blocks` data (verbatim `commandstring`/`commands` values)

Union of every string appearing in a `"commands": [...]` array across all 92 parsed block
entries: `get`, `set`, `toggle`, `increment`, `decrement`, `subscribe`, `unsubscribe`, plus
Dialer-block call-control verbs used the same way (`answer`, `dial`, `dtmf`, `end`, `flash`,
`hold`, `lconf`, `offHook`, `onHook`, `redial`, `resume`, `send`, `speedDial`), and the empty
string `""` for Service-style attributes (Device/Session services such as `recallPreset`,
`reboot`, `startAudio`) which take no get/set-style command word at all — the `commandstring`
(service name) is sent directly after the Instance Tag.

## String-assembly logic (from the widget's `calculatebutton` click handler, quoted verbatim)

```js
// Get selected values
const block = $("#selectblock").val();
const attributeNumber = parseInt($("#selectattrib").val());
const attribute = blocks[block].attributes[attributeNumber].commandstring;
const command = blocks[block].attributes[attributeNumber].commands[$("#selectcmd").val()];
...
// Build command string - MODIFIED to handle empty commands
let commandstring = instancetag;

// Only add command if it's not empty (for special device/session commands and "send")
if (command && command !== "") {
  commandstring += " " + command;
}

if (attribute) commandstring += " " + attribute;
if (index1) commandstring += " " + index1;
if (index2) commandstring += " " + index2;
if (subscriptionname) commandstring += " " + subscriptionname;
if (subscriptioninterval) commandstring += " " + subscriptioninterval;
if (value) commandstring += " " + value;
```

So the concrete assembly order is: **Instance Tag, [Command], Attribute-or-Service-code,
[Index1], [Index2], [subscription name], [subscription interval], [Value]** — each joined by a
single space, matching the `Instance_Tag Command Attribute [Index] [Value] LF` grammar stated on
the TTP Syntax / TTP Subscriptions pages, with the subscription name/interval riding in the
Index/Value slots as those pages describe.

Per-`valuetype` value formatting the widget implements (quoted verbatim):

```js
if (command === "get" || command === "toggle" || valuetype === "none") {
  if (valuetype === "ipconfig") value = "control";
} else if (command === "set" && (valuetype === "unbounded" || valuetype === "range")) {
  value = trim($("#selectnormalvalue").val());
} else if (command === "set" && valuetype === "discrete") {
  value = trim($("#selectvalue").find(":selected").text());
} else if (command === "increment" || command === "decrement") {
  value = trim($("#selectincdecvalue").val());
} else if (command === "set" && valuetype === "date") {
  value = '"' + pad($("#datehour").val()) + ":" + pad($("#dateminute").val()) + ":" +
    pad($("#datesecond").val()) + ":" + $("#datemonth").val() + ":" +
    pad($("#dateday").val()) + ":" + $("#dateyear").val() + '"';
} else if (command === "set" && valuetype === "freqgain") {
  value = '{"frequency":' + $("#freqgainfreq").val() + ' "gain":' + $("#freqgaingain").val() + '}';
} else if (command === "set" && valuetype === "typeslope") {
  value = '{"type":' + $("#typeslopetype").val() + ' "slope":' + $("#typeslopeslope").val() + '}';
} else if (command === "set" && valuetype === "delay") {
  value = '{"units":' + $("#delayunits").val() + ' "delay":' + $("#delaydelayvalue").val() + '}';
} else if (command === "set" && valuetype === "cmdstr") {
  value = '{"label":"' + $("#cmdstrlabel").val() + '" "command":"' + $("#cmdstrcommand").val() + '"}';
} else if (command === "set" && valuetype === "ipconfig") {
  if ($("#ipconfigauto").val() === "true") {
    value = 'control {"autoIPEnabled":true}';
  } else {
    value = 'control {"autoIPEnabled":false "ip":"' + $("#ipconfigip").val() +
      '" "netmask":"' + $("#ipconfigmask").val() +
      '" "gateway":"' + $("#ipconfiggateway").val() + '"}';
  }
} else if (command === "set" && valuetype === "videoBandwidth") {
  value = '{"resMax":' + $("#videoBW-resMax").val() +
    ' "frameRate":' + $("#videoBW-frameRate").val() +
    ' "compressionFactor":' + $("#videoBW-compression").val() + '}';
}
```

Token-quoting rule, the `trim()` helper (quoted verbatim — this is the calculator's own
operational definition of when a bare token must be double-quoted):

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

i.e.: a token that already looks like a JSON array (`[...]`) or object (`{...}`) is passed
through unquoted; any other token containing a space or comma gets wrapped in `"..."`; anything
else (bare numbers, bare identifiers, `true`/`false`) is left unquoted. This matches the
`SESSION get aliases` / `"my level 2" get level 1` quoting behavior documented on the TTP Syntax
page.

The page also links to two related Cornerstone articles (not fetched — out of scope for TTP
grammar, listed for completeness of what this page points to):
"Tesira DSP blocks that support subscriptions" and "Tesira device discovery methods".
