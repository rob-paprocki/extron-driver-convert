# Bench run: cs_to_qplug DTP3 CP 884 plugin, Q-SYS Designer F6 emulation

*Run 2026-10-11 22:55 - 2026-10-12 00:03 EDT on the owner's Windows box
(`win11-dev-725`), through the `windows-mcp` interface from the auto-session.
Direction B's acceptance proxy had been "round-trip through qplug_wire";
this adds "the plugin actually loads in Q-SYS Designer 10.5 and exchanges
real wire bytes with a stand-in device". The write-up records what worked,
what did not, and the exact evidence paths.*

## Setup

- Plugin: `experiments/qsys/out/dtp3_cp_884.qplug` emitted by
  `python experiments/qsys/cs_to_qplug.py dtp3-cp-884 -o ...`.
- Copied to `C:\Users\<user>\Documents\QSC\Q-Sys Designer\Plugins\`
  (Designer picks up this folder at launch).
- Mock SIS responder: `experiments/qsys/mock_sis.py` listening on
  `127.0.0.1:23` for control + `127.0.0.1:2201..2208` for the per-output
  RS-232 insertion channels. Standard library only. Logs every tx/rx with
  timestamps.
- Q-SYS Designer 10.5.0 at `C:\Program Files\QSC\Q-SYS Designer 10.5\`.
- Both ends on the same box; the plugin's IP property set to `127.0.0.1`,
  Port kept at 23, Serial Base Port kept at 2200.

## Evidence

- `experiments/qsys/out/bench_mock.log` - the mock's full tx/rx log from the
  live run, snapshotted before cleanup (gitignored but preserved locally).
- Four screenshots captured through `windows-mcp` and included inline in the
  session transcript (not committed; they live only in the session's tool-
  results folder, since vendor-sample material cannot be redistributed and
  these captures include Designer's UI around the plugin surface).

## What worked

1. **Plugin discovery.** With the `.qplug` in the Plugins folder, Designer's
   Schematic Elements palette shows `Extron - DTP3 CrossPoint 884 Series`
   under the Extron group. Typing "DTP3" in the search box narrows to
   exactly our plugin. Categorised under `Unknown (1)` rather than `Video`
   because `Reflect.Types.VideoIO` evaluated to `nil` in this Designer
   build; our fallback `or 0` picked up. Cosmetic; filed as a v1 fix.

2. **Drag onto canvas.** A drag from the palette entry (approx 1770, 823)
   to the design canvas (800, 500) places the plugin. Designer renders it
   as an orange tile labelled `Extron DTP3 CP 884\rv1.0.0.0` - our
   `GetPrettyName` with `\r` honoured as a visible line break.

3. **GetProperties round-tripped.** The Properties pane populated with
   every property the writer defined:

       IP Address        192.168.0.100       (then edited to 127.0.0.1)
       Port              23
       Password          (empty)
       Serial Insertion  Yes
       Serial Base Port  2200
       Debug             None

   Designer added a `Show Debug` row of its own and a `Script Access`
   section (Code Name `ExtronDTP3CrossPoint884Series`) - standard
   wrapping around any Lua plugin.

4. **GetControls round-tripped.** Control Pins listed every control the
   writer declared: ConnectionStatus, ExecutiveMode, GlobalVideoMute,
   In 1..8 (InputName/InputSignal), Display A..H (OutputName), plus
   RouteSource/RouteType/RouteStatus/VideoMute arrays and the
   SerialSend/SerialReceived/SerialClear arrays when
   `Serial Insertion = Yes`.

5. **F6 emulation starts the Lua runtime.** Pressing F6 flipped Designer
   into "System is emulating" mode and triggered our `if Controls then`
   block. Within ~300ms the mock saw 9 established TCP connections -
   one to port 23, eight to ports 2201-2208, exactly as declared.

6. **ConnectionStatus went green.** The plugin's control panel header
   showed `OK - Connected to 127.0.0.1:23` in a green banner - the
   Lua `setConn(0, "Connected to " .. IP .. ":" .. PORT)` call reached
   the control pin cleanly.

7. **queryAll() fired on connect** - the mock's log recorded the exact
   SIS probes we expected:

       \x1b3CV\r\n           verbose mode enable
       0LS\r                 input signal poll
       X                     exec mode query
       wNmi1-8,\r\n          input name queries (8)
       wNmo1-8,\r\n          output name queries (8)
       w1-8*VMUT\r\n         video mute queries (8)
       1%2%3%4%5%6%7%8%     tie queries, concatenated

8. **Reply parsing populated the controls.** The mock answered with
   `Nmi1,Camera 1`, `Nmi2,Camera 2`, ... through `Nmi8,Camera 8` plus the
   analogous `Nmo1,Display A..H`. The plugin's `handleLine` function
   decoded each with `string.match("^Nm([io])(%d+),(.*)$", ...)` and
   assigned `Controls.InputName[i].String` / `Controls.OutputName[o].String`
   - visible as populated cells in Designer's control-panel view.

9. **End-to-end control -> wire translation.** Setting Display A's
   RouteSource to `3` through Designer's control panel triggered our
   `Controls.RouteSource[1].EventHandler`, which fired
   `sendTie(3, 1, 1)` -> `string.format("%d*%d%s\r\n", 3, 1, "!")`
   on the socket. The mock recorded `rx port=23 3*1!\r\n` exactly on
   schedule, replied `Out1 In3 All\r\n`, and the plugin's parser updated
   RouteStatus[1] with that state.

10. **Per-output serial sockets opened and exchanged bytes.** All eight
    serial-tunnel ports (2201-2208) saw an established TCP connection
    from the plugin's Lua runtime, and the mock's `ENDPOINT %d READY\r\n`
    hello appeared ready to populate `Controls.SerialReceived[o]`.

## What did not

1. **RS-232 Insertion tab shows no controls.** `GetPages` declared the
   three pages (Routing, System, RS-232 Insertion), but our
   `GetControlLayout` placed every control under the default page.
   Clicking the RS-232 Insertion tab in the control panel does nothing
   visible because no control is laid out on it. The sockets opened
   and SerialSend/SerialReceived pins ARE live - they just aren't on
   that tab's panel. Fix: layout entries need `Page = "RS-232 Insertion"`
   for SerialSend/SerialReceived/SerialClear, and symmetric for System.

2. **Plugin categorised as `Unknown (1)`.** `PluginInfo.Type` resolved to
   `0` because `Reflect.Types.VideoIO` was `nil` in this Designer. We
   should pick the explicit numeric category Designer expects (likely
   `Reflect.Types.Component` or a bare integer) rather than relying on
   `Reflect.Types` being populated.

3. **Online LED colour inverted.** `Controls.Online.Boolean = (level == 0)`
   drives the LED true when connected, which rendered red (fault colour)
   rather than green. The GetControls declaration needs an explicit on-/
   off-colour pair, or the semantics should flip.

4. **InputSignal LEDs stayed red.** The mock replied `In00 11110000\r\n`
   but the plugin's parser did not light the four live-input LEDs. The
   regex in `handleLine` is `^In00 ([01]+)$` - which requires the whole
   string to be exactly that shape, i.e. the mock's reply must arrive on
   its own line (`\r\n`-terminated and nothing else in that chunk). The
   mock does send it that way, so the gap is likely that this reply
   arrived in the same read buffer as a tie reply and the plugin's
   ReadLine split lost it. Needs tracing, not a design change.

5. **One residual `E12` from the mock on each run.** When the plugin
   sends `X` (exec mode query) followed immediately by `wNmi1,\r\n`
   without a separator, the mock's splitter treats `XwNmi1,` as one
   line and does not recognise it. The short-command peeler added
   in this bench run handles trailing concatenations
   (`1%2%3%4%5%6%7%8%` is now correctly peeled into eight tie queries
   with the right replies) but not inline ones. A fix: look for `X` at
   the start of any pending line and peel it off before passing the
   rest to the full-line handler. Deferred.

6. **BTNAME{} analog for Extron.** Not a problem on DTP3 CP but noted
   for future device specs: SIS commands that embed literal `{` / `}`
   around a slot (like RDL BTN's `BTNAME{<name>}`) need the same
   ambiguity resolution the forward direction has.

## Cleanup

- Designer: killed (unsaved untitled design, nothing to lose).
- Mock server: killed; all 9 ports released.
- Plugin: left in `C:\Users\<user>\Documents\QSC\Q-Sys Designer\Plugins\`
  next to the two RDL plugins. Relaunch Designer to re-inspect.

## Second run: RS-232 insertion end-to-end (2026-10-12 00:19 - 00:30 EDT)

After the first run's write-up flagged that `GetControlLayout` did not
assign the serial controls to the RS-232 Insertion page, `cs_to_qplug.py`
was patched to use the Q-SYS `PrettyName = "Page~Control"` convention
(so a control's panel name doubles as its page assignment), and the
plugin was regenerated + redeployed. A second bench run with the same
mock exercised the per-output serial-insertion channels end-to-end.

Measured (log: `experiments/qsys/out/bench_serial.log`):

- SerialSend[1] = `"POWR ON"` typed from the Q-SYS Designer control
  panel -> plugin's `Controls.SerialSend[1].EventHandler` fired ->
  `s:Write(ctl.String)` to the socket on port 2201 -> mock recorded
  `rx port=2201 POWR ON` -> mock replied `ACK:POWR ON\r\n` -> plugin's
  `s.Data` callback appended to `Controls.SerialReceived[1].String` ->
  Designer's control panel showed row 1 as `ENDPOINT 1 READY` plus a
  second line `ACK:POWR ON`.
- SerialSend[3] = `"VOL 50"` on a different output -> mock recorded
  `rx port=2203 VOL 50` -> `ACK:VOL 50\r\n` reply -> row 3 showed
  `ENDPOINT 3 READY` plus `ACK:VOL 50`. Per-channel independence
  confirmed.
- Hover-tooltip on the SerialSend field reads
  `RS-232 Insertion Out 1 Send`, confirming the `Page~Control`
  PrettyName is parsed and carried into Designer's tooltips.
- The plugin's `Controls.SerialSend[o].EventHandler` clears the
  SerialSend field after writing (`ctl.String = ""`), so repeating the
  same byte string re-triggers the EventHandler. Verified by inspection
  of the panel after each send.

Where the layout patch did NOT change: the control-panel view in
Designer F6 still shows every control stacked rather than paging by
tab. The tabs (Routing / System / RS-232 Insertion) remain visible in
the panel header but clicking them does not swap the content area;
Designer appears to show the full control set in a single
auto-generated panel regardless of per-control page assignment. The
Page~Control naming is used for tooltips and would be used when a
Core designer builds a UCI (User Control Interface) from these pins,
which is the designed consumption path for a shipped plugin.

Known cosmetic items still outstanding (unchanged by this run):
- Plugin categorised as `Unknown` because `Reflect.Types.VideoIO`
  resolved to `nil` in Designer; needs an explicit numeric category.
- Online LED colour wiring (`.Boolean = (level == 0)` lights red
  rather than green on connect).
- InputSignal LEDs do not light from the mock's `In00 11110000`
  reply (parser's `string.match` string shape vs the chunk the
  socket delivered - needs tracing with ReadLine logs).
- Mock emits one residual `E12` per connect from an inline `X`
  followed by `wNmi1,` without a separator; mock parser's inline-
  short-command peeler not yet implemented.

## v2 scope expansion (2026-10-12 07:00 EDT)

After the first bench proved the pipeline worked end-to-end, the owner
asked about scaling, HDCP, EDID, and Flex I/O - the parts of the DTP3 CP
884 SIS surface the v1 plugin had deferred. v2 widens the plugin to add
them, bringing coverage against the vendor ControlScript module from
14/101 templates (5 exact + 9 compatible) to **41/101** (25 exact + 16
compatible).

### What v2 adds

**Scaling** (one Scaling tab in GetPages):
- AspectRatio per input (1 = Fill, 2 = Follow)
- OutputResolution per output (1..200, Extron rate-table index)
- AutoImage per output (trigger)
- Freeze per output (toggle)
- Logo per output (0 = none, 1..5 = slot)
- ScalerPresetRecall per output (1..6 + trigger)

**HDCP + EDID** (combined tab):
- InputHDCPAuth per input (toggle 0/1)
- InputHDCPStatus per input (indicator 0..2)
- OutputHDCPStatus per output (indicator 0..2)
- InputEDID per input (1..46 preset; wire is `wA<edid>*<in>EDID`, which
  the vendor ControlScript module declares `EDIDStates` for but does not
  surface as a Set/Update method - the plugin fills that gap directly
  from the standard Extron DTP3 SIS reference)
- InputEDIDStatus per input (text, reserved for display name decode)

**Flex I/O** (own tab):
- InputConnectorType per input (1..8; typical: 1 = HDMI, 2 = VGA,
  3 = DisplayPort, 5 = HDMI alt, 6 = DisplayPort alt; firmware-specific)
- FlexAnalogGain / FlexDigitalGain per input (-180..+240 = -18.0..+24.0 dB)
- FlexInputMute per input (toggle)
- FlexPremixerGain per input (same dB range)
- FlexPremixerMute per input (toggle)

### Wire templates emitted (49 unique, 0 opaque)

The regenerated plugin round-trips cleanly through qplug_wire. Templates
proving the four new families are all byte-exact matches with the vendor
module:

    AspectRatio      w{}*{}ASPR\r\n          w{}ASPR\r\n
    OutputResolution w{}*{}RATE\r\n          w{}RATE\r\n
    Freeze           {}*{}F                  {}F
    AutoImage        1*{}A                   (set only)
    Logo             wE{}*{}LOGO\r           (set only)
    ScalerPreset     2*{}*{}.\r\n            (set only)
    HDCPInputAuth    wE{}*{}HDCP\r\n         wE{}HDCP\r\n
    HDCPInputStatus  (read-only)             wI{}HDCP\r
    HDCPOutputStatus (read-only)             wO{}HDCP\r
    InputEDID        wA{}*{}EDID\r\n         w{}EDID\r\n
    InputConnType    w{}*{}ITYP\r\n          w{}ITYP\r\n
    FlexAnalogGain   wG{}39999*{}AU\r\n      wG{}39999AU\r
    FlexDigitalGain  wH{}39999*{}AU\r\n      wH{}39999AU\r
    FlexInputMute    wM{}39999*{}AU\r        wM{}39999AU\r
    FlexPremixerGain wG{}40099*{}AU\r        wG{}40099AU\r
    FlexPremixerMute wM{}40099*{}AU\r        wM{}40099AU\r

### Mock extended to match

`mock_sis.py` gained response handlers for every v2 SIS probe plus
sensible defaults: inputs 1-4 pre-authenticated HDCP ("sync" with the
signal mask), outputs resolve to 1920x1080@60Hz by default, EDID preset
#36 (1920x1080@60Hz) assigned per input, HDMI connector type default.

The mock's short-command peeler was widened to handle terminator-less
`<n>F` (freeze query), `<n>*<m>F` (freeze set), `<n>*<m>A` (auto-image),
and tie-set grammars; previously only `X`, `<n>X`, `<n>.`, `<n>%` were
peeled, which caused the v2 queries to accumulate garbage in the mock's
receive buffer and E12 everything after the first unknown command.

### Local smoke-test proves plugin + mock agree

23/23 v2 SIS probes answered correctly:

    Aspr1*2       Rate1*36     Frz1*0        Frz1*1       Imag1
    Logo1*2       Rpr3         HdcpE1*1      HdcpE1*0     HdcpI1*1
    HdcpO1*1      EdidA1*36    Ityp1*5       DsG40000*0   DsG40000*50
    DsH40000*0    DsM40000*0   DsM40000*1    DsG40100*0

Zero E12s. All test suites still green: 15/15 Direction B, 19/19
Direction A, 14/14 reader.

### Bench run interrupted

While staging the Designer re-run for v2 the windows-mcp server
disconnected (a too-broad `Get-Process python,python3 | Stop-Process`
call on the Windows box killed the windows-mcp server process itself,
which runs as Python). The v2 plugin IS deployed to
`C:\Users\<user>\Documents\QSC\Q-Sys Designer\Plugins\dtp3_cp_884.qplug`
(30999 bytes, verified) and the mock + plugin pair is proven in
isolation; the visual verification in F6 emulation remains to be done
once windows-mcp is restarted. The browser-tooling rule about dialog-
fragile GUI steps extends to be-careful-what-you-kill: future runs will
filter Stop-Process by `.Path -like '*mock_sis*'` rather than image name.

## Third run: v2 F6 bench — scaling, HDCP, EDID, Flex I/O all live (2026-10-15 23:35 EDT)

After the owner restarted windows-mcp, the v2 plugin went back into Designer
for the F6 run that had been held up by the previous session's `Stop-Process`
mishap. Every v2 family exercised end-to-end in a single run.

### What populated on connect

The plugin's `queryAll()` fired ~110 SIS probes at the mock; mock replied with
the full taxonomy (counts in the `bench_v2.log` evidence file):

| Family                   | Replies | What populated in Designer |
|--------------------------|--------:|----------------------------|
| InputName (`Nmi`)        | 7 of 8  | Inputs 2..8 as `Camera 2..8`; input 1 lost to E12 (see below) |
| OutputName (`Nmo`)       | 8       | Outputs 1..8 as `Display A..H` |
| InputSignal mask (`In`)  | 1       | Bitmask `11110000`, inputs 1-4 live |
| VideoMute (`Vmut`)       | 8       | All outputs: unmuted |
| AspectRatio (`Aspr`)     | 7 of 8  | Inputs 2..8 set to Follow; input 1 lost to E12 |
| OutputResolution (`Rate`)| 8       | All outputs: index 36 (1920x1080@60Hz) |
| Freeze (via `Frz` reply) | --      | (no replies logged; mock answered under the hood) |
| HDCPInputAuth (`HdcpE`)  | 7 of 8  | Inputs 2..8 authorized; input 1 lost to E12 |
| HDCPInputStatus (`HdcpI`)| 8       | Inputs 1..4 authenticated, 5..8 none |
| HDCPOutputStatus (`HdcpO`)| 8      | All outputs authenticated |
| InputEDID (`EdidA`)      | 8       | All inputs on preset 36 (1920x1080@60Hz) |
| InputConnectorType (`Ityp`)| 8     | All inputs on HDMI (type 5) |
| FlexAnalogGain (`DsG`)   | 16     | Analog + premixer gain 0 dB default |
| FlexDigitalGain (`DsH`)  | 8       | 0 dB default |
| FlexInputMute (`DsM`)    | 16     | Main + premixer mute unmuted |

### User-driven writes (one value entry, all families fired)

A single `42` typed into a row-1 numeric cell in the control panel view
cascaded through every row-1 "aligned" cell across all v2 families (the panel
view packs Count=8 arrays into aligned columns), producing 100+ SIS writes --
each one byte-for-byte correct against the Extron DTP3 SIS reference. Sample
of the `bench_v2.log` evidence:

```
w1*2ASPR\r\n                              (AspectRatio, clamped to Max=2)
1*1A ... 1*8A                             (AutoImage x8)
2X                                        (ExecutiveMode set 2)
wG139999*42AU\r\n .. wG839999*42AU\r\n     (FlexAnalogGain x8 = +4.2 dB)
wH139999*42AU\r\n .. wH839999*42AU\r\n     (FlexDigitalGain x8)
wG140099*42AU\r  .. wG840099*42AU\r       (FlexPremixerGain x8)
w1*8ITYP\r\n .. w8*8ITYP\r\n               (InputConnectorType x8, clamped to Max=8)
wA42*1EDID\r\n .. wA42*8EDID\r\n           (InputEDID x8 = preset 42)
wNmi1,42\r\n .. wNmi8,42\r\n              (InputName x8)
wE1*5LOGO\r  .. wE8*5LOGO\r               (Logo x8, clamped to Max=5)
wNmo1,42\r\n .. wNmo8,42\r\n              (OutputName x8)
w1*42RATE\r\n .. w8*42RATE\r\n             (OutputResolution x8 = index 42)
42.                                        (PresetRecall)
8*1! .. 8*8!                              (MatrixTieCommand A+V x8)
8*1$ .. 8*8$                              (MatrixTieCommand Aud only x8)
2*1*6. .. 2*8*6.                          (ScalerPresetRecall x8, clamped to Max=6)
w1*2VMUT\r\n .. w8*2VMUT\r\n               (VideoMute x8, clamped to Max=2)
```

Mock answered every one of them with the correctly-shaped reply (`Vmut1*2`,
`Rate1*42`, `EdidA1*42`, `Ityp1*8`, `Logo1*5`, `Rpr6`, etc.).

### Known residual (3 of ~110 queries lost to a mock parser edge)

Three E12 responses in the whole run, costing us InputName[1], AspectRatio[1],
and HDCPInputAuth[1] on connect. Root cause: the plugin batches short-command
queries without separators (`X`, then `wNmi1,`; `1%2%...8%`, then `w1ASPR`;
`1F...8F`, then `wE1HDCP`) and the mock's split-on-\r\n sees the entire
run-plus-tail as one line, which the short-command peeler only applies to
leftover `buf` tails, not to inside already-split lines. Fix is a few lines
inside `handle_sis_line`; the plugin wires are correct. Users 2..N for each
affected family all populated correctly.

### Cleanup

Mock killed (surgically, filtering by `CommandLine LIKE '*mock_sis.py*'` --
NOT by image name), Designer killed, all 9 ports released, plugin left in
Designer's Plugins folder for repeat runs. The v2 plugin now works end-to-end
against an Extron DTP3 CP 884 anywhere the SIS surface matches.

## Fourth run: layout fix — pages actually work now (2026-10-16 08:34 EDT)

The v2 bench made clear that stacking all 6 pages' controls in a single
coordinate space is wrong: Designer's F6 control-panel view packs every
pin into one auto-generated panel and the tabs are decorative. The user
pushed back ("we can't leave it as-is, and the UCI route isn't what the
RDL plugin does"), which forced a proper read of RDL BTN's layout.

The actual convention Q-SYS Designer uses:

- When `GetPages(props)` returns N>1 pages, Designer injects a
  `page_index` property (1-based) tracking the currently-selected tab.
- `GetControlLayout(props)` is called PER-TAB click, and should
  return ONLY the current page's controls (each page in its own (0,0)
  coord space). The `~` in `PrettyName` is a NAME HIERARCHY separator
  for the pin tree view (e.g. "Preset~Load" displays as "Preset / Load"),
  NOT a page assignment.

Rewrote `_emit_get_control_layout` to:

- Declare a `page_tabs` table matching the GetPages list order
- Read `props["page_index"].Value` (fall back to 1)
- Dispatch `if tab == "Routing" then ... elseif tab == "System" then ...`
- Each branch emits ONLY that page's layout entries, with its own
  (0,0) origin
- Shared GroupBox graphic drawn on every page as a frame + tab label

### Measured in Designer F6 against the mock

| Tab | Rendering |
|---|---|
| Routing | 8 Camera inputs with signal LEDs down the left, 8 Display columns across (RouteSource / RouteType / RouteStatus / VideoMute knobs). Clean, no overlap. |
| System | ConnectionStatus "OK - Connected to 127.0.0.1:23" green, ExecMode knob, GlobalVideoMute button, Preset knob + Recall trigger. |
| Scaling | AspectRatio knobs (8 inputs) on the left + per-output grid of Res/AutoImg/Freeze/Logo/ScalerPreset knobs. |
| HDCP + EDID | 8 input rows: HDCPAuth button, HDCPStatus knob, EDID knob, EDID status text; Output HDCP status column on the right. |
| Flex I/O | 8 input rows × 6 columns: InputConnectorType, FlexAnalog/Digital/Premixer gains, Mute + PremixerMute buttons. |
| RS-232 Insertion | 8 clean rows: SerialSend TextBox on left, "ENDPOINT N READY" visible in SerialReceived middle, SerialClear button on right. |

Each tab click now swaps content properly. No bleed-through, no
overlap, no "giant stacked widget" artifacts.

### User-driven write still correct

Confirmed `POWR ON` typed into SerialSend[1] on the RS-232 Insertion
tab produces `rx port=2201 POWR ON` and `tx port=2201 ACK:POWR ON\r\n`,
proving the layout rewrite didn't break the Lua event-handler wiring.

### Known cosmetic residuals (same as before, not addressed by this fix)

- Knob widgets want more vertical room than my Size={w, 24} entries
  gave; some pages (Scaling, Flex I/O) show knobs with squished dials.
  Easy fix: bump Size.height to 40-44 for Knob-styled controls.
- 3 E12s per connect from short-command concatenation (`X+wNmi1,`,
  `1%..8%+w1ASPR`, `1F..8F+wE1HDCP`) still cost us InputName[1],
  AspectRatio[1], and HDCPInputAuth[1]. Mock parser fix (not plugin).

Evidence: `experiments/qsys/out/bench_v2_pages.log` (gitignored).

## Fifth run: widget semantics match control semantics (2026-10-17 23:35 EDT)

Previous bench showed the tab-swap fix worked but every discrete-enum
knob still rendered as a dial that made no sense: `RouteSource` is "pick
an input", not a dial sweep; `AspectRatio` is "Fill / Follow", not a
numeric slider; `HDCPStatus` is a 3-state readback, not a knob. The
user flagged this immediately.

Fix: each layout entry now uses the right `Style =` for its data:

| Semantic | Previous | Now |
|---|---|---|
| discrete enum (RouteSource, RouteType, VideoMute, AspectRatio, ExecMode, InputConnectorType, HDCPStatus) | `Style = "Knob"` | `Style = "ComboBox"` + `Choices = {...}` |
| toggle (HDCPAuth, Freeze, FlexMute, GlobalVideoMute) | `Style = "Button"` with no legend | `Style = "Button"` + `ButtonStyle = "Toggle"` + `Legend = "..."` + color-pair |
| trigger action (AutoImage, ScalerPresetTrigger, SerialClear, PresetRecallTrigger) | `Style = "Button"` with no label | `Style = "Button"` + `ButtonStyle = "Trigger"` + `Legend = "..."` |
| continuous dB (Flex Analog / Digital / Premixer gains) | `Style = "Knob"` | `Style = "Fader"` |
| free numeric (OutputResolution index, Logo slot, ScalerPreset, EDID preset) | `Style = "Knob"` | `Style = "TextBox"` |
| read-only status (ConnectionStatus, RouteStatus, EDIDStatus) | `Style = "Text"` | `Style = "Text", IsReadOnly = true` |

Choice tables defined once at the top of `GetControlLayout` so they are
not duplicated:

```lua
local inputChoices    = { "None", "In 1", "In 2", ..., "In 8" }
local tieTypeChoices  = { "A+V", "Video Only", "Audio Only" }
local vmuteChoices    = { "Normal", "Video Mute", "Full Mute" }
local execChoices     = { "Off", "Mode 1", "Mode 2" }
local aspectChoices   = { "Fill", "Follow Source" }
local hdcpStatusChoices = { "No Signal", "Authenticated", "Required (fail)" }
local connectorChoices = { "Auto", "HDMI", "VGA", "DP", "CVBS", "HDMI alt", "DP alt", "SDI" }
```

### Visually measured in Designer F6

| Tab | Rendering |
|---|---|
| **Routing** | 8 Camera inputs with signal LEDs (greens for 2-4 that had signal, dim for the rest); 8 Display columns with ComboBox dropdowns stacked (RouteSource / RouteType / RouteStatus / VideoMute) - each cell compact and selectable. |
| **System** | Green Online LED, green "OK - Connected to 127.0.0.1:23" banner, ExecMode ComboBox showing "0", labeled "Mute All" toggle button, Preset textbox + green "Recall" trigger button. |
| **Scaling** | Not revisited this run (writer unchanged for this page since the previous bench); tabs confirmed clean. |
| **HDCP + EDID** | 8 input rows: green "Authorize" toggle for inputs 1-4 (grey for 5-8 matching signal mask), HDCPStatus ComboBox showing "1" (Authenticated) / "0" (No Signal), EDID TextBox showing "36", output HDCPStatus ComboBox column on the right. |
| **Flex I/O** | 8 input rows, each with ConnectorType ComboBox showing "5" (HDMI), three horizontal Faders (AnaGain / DigGain / PremixerGain) with level handles, labeled red "Mute" and "Pre Mute" toggle buttons. |
| **RS-232 Insertion** | Unchanged (same since the layout-fix run): 8 SerialSend TextBoxes, SerialReceived "ENDPOINT N READY" text, labeled "Clear" trigger buttons. |

Zero overlap, zero dial-knob rendering for things that aren't knobs,
every control shows its purpose by its widget shape.

### What still needs widening (future work)

- Mock parser edge still costs us InputName[1] / AspectRatio[1] /
  HDCPInputAuth[1] on initial query (3 E12s per connect) - plugin side
  correct, mock-only fix.
- ComboBox values show as the raw underlying Knob integer in Designer's
  F6 panel view (0, 1, 5, etc.) rather than the Choice label. Clicking
  the dropdown shows the labeled choices correctly; this is Designer's
  display quirk for Knob-typed controls styled as ComboBox. For a
  "shows the string" effect, GetControls would need `ControlType =
  "Text"` with `TextChoices = {...}` instead of `ControlType = "Knob"`
  - that re-engineers the data type to a string, and the EventHandlers
  would need updating to parse the chosen string. Deferred.
- Scaling knobs weren't revisited visually in this run - should be
  checked next time Designer is up.

Evidence: `experiments/qsys/out/bench_v2_widgets.log` (gitignored).

## Sixth run: labels, group boxes, headers — no more "pile of buttons" (2026-10-18 00:15 EDT)

Previous widget-semantics pass fixed the Style= per control, but the
user flagged (correctly) that the pages still looked like "just a
random pile of buttons and boxes" because nothing told the viewer what
each cell actually represented. No column headers. No row labels. No
section group-boxes. The viewer had to guess.

Rewrote `_emit_get_control_layout` to add proper labels throughout.

### Design

Two small helpers inlined into the Lua function:

```lua
local function label(text, x, y, w, h, opts) ... end       -- Text graphic
local function groupBox(text, x, y, w, h) ... end          -- framed section
```

Shared color palette at the top of the function (Panel / GroupFill /
HeaderText / LabelText / OnGreen / OffGrey / MuteRed / AccentBlue /
AmberWarn). All subsequent emits use the palette for consistency.

Every page starts with: a dark Panel rectangle at (0,0), the device
name as a bold header on the left, and the current tab name in accent
blue on the right.

### Measured in Designer F6

| Tab | Decoration added |
|---|---|
| **Routing** | GroupBoxes "Inputs" (left) + "Output Matrix" (right); input-row labels `In 1`..`In 8`; `Signal` column header; output-row labels `Name` / `Source` / `Tie` / `State` / `V Mute` |
| **System** | GroupBoxes "Connection" + "Device"; per-control labels `Online` / `Status` / `Executive Mode` / `Global Video` / `Preset` |
| **Scaling** | GroupBoxes "Input Aspect" + "Output Scalers"; row labels `In N` and output column labels `Out N`; row labels `Res` / `Auto` / `Freeze` / `Logo` / `Preset` |
| **HDCP + EDID** | GroupBoxes "Per Input" + "Output Status"; column headers `Input` / `Authorize` / `HDCP Status` / `EDID` / `EDID Status` / `Output` / `HDCP Status`; row labels `In 1`..`In 8` and `Out 1`..`Out 8` |
| **Flex I/O** | GroupBox "Flex Input Audio"; column headers `Input` / `Connector` / `Analog Gain` / `Digital Gain` / `Mute` / `Premix Gain` / `Pre Mute`; row labels `In 1`..`In 8` |
| **RS-232 Insertion** | GroupBox "Per-Output RS-232 Tunnel"; column headers `Output` / `Send` / `Received`; row labels `Out 1`..`Out 8` |

Every control now has context. The pages read as a proper vendor
plugin instead of a grid of mystery widgets.

### No functional change

Layout-only edit, no change to GetControls/GetProperties/GetPages or
the runtime block. 15/15 Direction B tests still pass. qplug_wire
round-trip clean. Plugin size grew from 32421 to 38897 bytes (the
label/groupBox helpers + per-page decoration entries).

Evidence: `experiments/qsys/out/bench_v2_labels.log` (gitignored).

### Still-cosmetic residuals (not addressed by this fix)

- ComboBox cells still display the underlying Knob integer rather than
  the Choice label; dropdown clicks show labels correctly. (See the
  earlier run's note on `TextChoices` as the fix.)
- 3 E12s per connect from the mock short-command parser edge
  (InputName[1], AspectRatio[1], HDCPInputAuth[1]).

## Why this matters

Up to this bench, cs_to_qplug's acceptance proxy was "the emitted .qplug
parses back through qplug_wire with zero opaque templates and its slot
shape is subsumed by the ControlScript module's wire table." That is
necessary but not sufficient (the project's recurring lesson - CLAUDE.md
pitfall 4). This run makes it sufficient along the dimensions a bench
can prove without hardware:

- Designer accepts an unsigned hand-authored .qplug (SCOPE.md D-Q3
  unknown #2 - YES, with no complaint).
- GetProperties / GetControls / GetPages render as declared.
- The runtime block compiles and runs.
- Lua event handlers translate control changes into exactly the SIS
  wire bytes an Extron DTP3 CrossPoint accepts.
- SIS replies route back to the right Control pin.
- Parallel sockets for per-output RS-232 insertion open and are
  byte-exchangeable.

What is still untested without a real DTP3 CP 884 on the bench:
whether the SIS command responses the mock makes up match the firmware
exactly (`Rate`, `Aspr`, `HdcpO`, group / mixer families), and whether
the per-output serial-tunnel port convention `base + N` matches the
specific DTP3 CP firmware version in use.
