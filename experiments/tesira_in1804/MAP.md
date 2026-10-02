# Controlling an Extron IN1804 from a Biamp Tesira

*2026-10-01. Desk research, verified against primary sources by an independent check; nothing
here has run on a Tesira or an IN1804 yet. §7 lists what a first hardware session must settle.*

## 0. In short

**It can be done with Tesira's own blocks, no external controller.** A **Network Command
String** (NCS) block on a Tesira server-class unit opens a TCP session to the IN1804 and sends
fixed Extron SIS strings, one per logic input. On Tesira 3.15 or later the same block also
matches the switcher's replies and pulses a logic output per reply, which gives real feedback
(active input, blanked, muted). A **Serial Command String** block can do the sending over
RS-232 instead, but it reads no replies.

The IN1804 side is fully known: its command strings and reply formats come from Extron's own
ControlScript module for the series. The work is mapping, plus four things only hardware can
settle: whether the Tesira sends Extron's unterminated one-character commands, how the IN1804
greets a TCP session (password prompt, banner), whether Tesira's start-up sequence can turn on
Extron's tagged replies, and two reply forms. §6 is a paste-ready string table.

## 1. Which Tesira block

| | Network Command String | Serial Command String |
|---|---|---|
| Transport | TCP or UDP client to any IP and port | RS-232 from the unit's serial port |
| Sends | up to 32 fixed strings per block, one logic input each | same |
| Reads replies | **yes, from Tesira 3.15**: Expected Response patterns, each can pulse a logic output (250 ms) or send another string | **no** |
| Start-up exchange | **Connection Sequence**: expected string, then response string, in order, after each (re)connect | none |
| Reconnects | Auto Connect retries every 3 s | n/a |
| Runs on | Tesira server-class units: SERVER, SERVER IO, TesiraFORTE; TesiraFORTE X as well | units with an RS-232 port set to "Command String" or "Both" |

**Use the Network block.** It is the only one with feedback, and it needs no cable. The Serial
block is the fallback where the switcher is not on a network the Tesira can reach.

## 2. How the Tesira block behaves (Biamp's documentation)

- **Strings** are typed in the block's *Edit Command String* dialog. Printable text is typed as
  is; any other byte is a tilde and two hex digits: `~0D` is CR, `~0A` is LF, `~7E` a literal
  tilde. Nothing is added automatically: the block sends exactly what is typed.
- **The Serial block will not transmit a string that does not end in CR or LF** (Biamp, Serial
  Command String Block). The Network block's pages do not repeat that rule. See §4.1.
- **Triggering.** A LOW-to-HIGH transition on a string's logic input sends it. Logic inputs can
  come from Logic State blocks (which presets can set), GPIO or EX-LOGIC contact closures, Logic
  Pulse and Logic Delay blocks, and a TEC-X Control Pad button (block "Command String", attribute
  "Send", parameter = the string's number). The Tesira Text Protocol table for the block has no
  send attribute, so do not plan on firing strings over TTP.
- **Expected Response patterns** (Network block, 3.15+): case-sensitive text with the same tilde
  escapes, plus two wildcards: `?` is one printable character and `*` is zero or more, matched
  minimally. Wildcards do not span CR or LF. A pattern must not end in `*`, should start with a
  definite character, and should include the reply's terminator. Patterns are tried top to
  bottom, the first match wins, and matched bytes leave the buffer.
- **Connection.** TCP only as a client. With Auto Connect on, the block retries every 3 s. Sending
  without a connection gives Connect Error (115); an unresolvable host name gives (101). Nothing is
  documented about an idle timeout, keepalive, or Telnet option negotiation.
- **Connection Sequence** (formerly "Expected List"): pairs of expected and response strings,
  worked through in order once the connection is up, "intended for session negotiation". Biamp
  never says it answers a login prompt, and gives no example of one (§7, H-T4).

## 3. How the IN1804 talks (Extron's own module)

Read from `extr_scaler_IN1804_Series_v1_3_0_0.py`, Extron's ControlScript module for the series
(vendor material, on disk, not in this repo; `tools/wire_table.py dump` reads 34 commands from it).

- **Transports in the module:** RS-232 at 9600 8N1, no flow control; "serial over Ethernet" (raw
  TCP, port not named by the module); SSH. It handles no login prompt itself.
- **Two command shapes.** One-character SIS commands go out with **no terminator at all**:
  `2!` (input 2), `1B` (blank), `0Z` (unmute), `-20V` (volume). Longer commands start with a
  lowercase `w` and end in a bare CR: `w0AUSW` + CR. (The `w` stands in for the Esc character,
  as in Extron's other scaler modules; the module itself never sends an Esc byte. Inferred.) Three
  strings end in CR LF: `w3cv` (verbose mode), `w0echo` and the output-rate command.
- **Verbose mode 3.** Before its first command the module sends `w3cv` CR LF and waits for
  `Vrb3`. In that mode replies come back tagged: `In2 All`, `Vmt1`, `Amt0`, `Exe1`. All replies
  end in CR LF.
- **No breakaway.** `{n}!` moves audio and video together; the module has no audio-only or
  video-only select. (Absent from the module, not proven absent from the device.)
- **Auto-switch** (`w{0|1|2}AUSW`) can override a manual input select; mode 0 turns it off.
- **Errors** come back as `E` plus two digits (`E13` = invalid parameter, `E10` = invalid command).

## 4. Where the two meet

1. **Unterminated commands.** Extron sends `1!` with nothing after it. Biamp's Serial block will
   not send a string without CR or LF, and the Network block's behaviour is undocumented. So:
   on the Network block, try the strings exactly as Extron sends them; if they do not go out,
   add `~0D`. For the Serial block, add `~0D` from the start (`tesira_strings.py --serial` does).
   Whether the IN1804 ignores a trailing CR after `1!` is H-T2.
2. **Tagged replies need verbose mode 3, per session.** Send string 1 (`w3cv~0D~0A`) once after
   every connect. The clean way is a Connection Sequence keyed on a fixed piece of the switcher's
   connection banner, which only a capture can show (H-T3). Until then, fire string 1 from a
   Logic Pulse shortly after start-up and after any reconnect.
3. **Password prompt.** If the IN1804 has a password set, a TCP session starts with a prompt. A
   Connection Sequence pair (expected: the prompt; response: the password and `~0D`) is the only
   Tesira mechanism that could answer it, and Biamp does not document that use (H-T4). Without a
   password set, nothing is needed.
4. **Literal `*` in replies.** Extron's per-output replies contain `*` (`Vmt1*1`, `Amt1*0`), which
   is a wildcard in a Tesira pattern. Write it `~2A` (the table does). That a tilde escape matches
   the literal character is H-T6.
5. **Volume is a set of fixed levels.** A Tesira string is fixed text, so `-20V` is one button.
   The table gives -40, -20 and 0 (Extron's range is -100 to 0). Extron's increment form is not
   in the module and not used here.
6. **Feedback is a 250 ms pulse.** A matched reply pulses a logic output; it does not hold a
   state. To light "Input 2 selected" steadily, the four input patterns' pulses have to feed
   logic that latches the last one. Tesira's Logic Selector (3.11 and later) looks like the fit;
   Biamp gives no recipe for this, so treat the wiring as a design to test.

## 5. Feedback and polling

- Poll with a repeating **Logic Pulse** into string 7 (`!`, the input query) and, if wanted,
  strings 10 and 13 (blank and mute queries). Biamp's own TEC-X example polls this way.
- Patterns: `In1 All~0D~0A` … `In4 All~0D~0A` to four logic outputs; `Vmt1 1~0D~0A` and
  `Vmt0 0~0D~0A`; `Amt1 1~0D~0A` and `Amt0 0~0D~0A`; `E??~0D~0A` for errors.
- The same patterns fire when someone changes the switcher at its front panel, provided the
  IN1804 sends unsolicited replies in verbose mode 3 (Extron's module treats `Vmt1` and `Amt1` as
  unsolicited, which suggests it does; H-T5).
- **Signal present** (`w0LS` CR) answers `In00 a*b*c*d`, one 0 or 1 per input. Mapping that to
  lights takes one pattern per input and state, with `?` for the other positions, for example
  `In00 1~2A?~2A?~2A?~0D~0A` for "input 1 has signal". Add only what the room needs; one block
  holds 32 strings and up to 32 logic outputs.

## 6. The strings

Generated by `python experiments/tesira_in1804/tesira_strings.py` (tests: `test_tesira_strings.py`).
"Command string" goes in the block's Edit Command String dialog under the ID shown; "Expected
response" goes in the Expected Response list, each on its own logic output.

| ID | Label | Command string | Expected response | Note |
|----|---------------------------------|----------------|-------------------|--------------------------------------------------------|
| 1 | Verbose mode 3 (tagged replies) | w3cv~0D~0A | Vrb3~0D~0A | send once per connection, first |
| 2 | Auto-switch off | w0AUSW~0D | Ausw0~0D~0A | stops auto-switching overriding a manual select |
| 3 | Input 1 | 1! | In1 All~0D~0A | audio and video together; no breakaway |
| 4 | Input 2 | 2! | In2 All~0D~0A | |
| 5 | Input 3 | 3! | In3 All~0D~0A | |
| 6 | Input 4 | 4! | In4 All~0D~0A | |
| 7 | Input query | ! | | answered by the In1-In4 patterns above |
| 8 | Video blank all, on | 1B | Vmt1~0D~0A | reply form not confirmed (H-T5) |
| 9 | Video blank all, off | 0B | Vmt0~0D~0A | reply form not confirmed (H-T5) |
| 10 | Video blank query | B | Vmt1 1~0D~0A | both outputs blanked; 'Vmt0 0' = neither |
| 11 | Audio mute all, on | 1Z | Amt1~0D~0A | reply form not confirmed (H-T5) |
| 12 | Audio mute all, off | 0Z | Amt0~0D~0A | reply form not confirmed (H-T5) |
| 13 | Audio mute query | Z | Amt1 1~0D~0A | both outputs muted; 'Amt0 0' = neither |
| 14 | Front-panel lock, mode 1 | 1X | Exe1~0D~0A | Extron executive mode |
| 15 | Front-panel lock off | 0X | Exe0~0D~0A | |
| 16 | Video blank output 1A, on | 1*1B | Vmt1~2A1~0D~0A | per output: 1 = 1A, 2 = 1B |
| 17 | Video blank output 1A, off | 1*0B | Vmt1~2A0~0D~0A | |
| 18 | Signal present query | w0LS~0D | | reply 'In00 a*b*c*d', one 0/1 per input; see §5 |
| 19 | Volume -40 | -40V | | fixed levels; range -100..0 (§4) |
| 20 | Volume -20 | -20V | | |
| 21 | Volume 0 (maximum) | 0V | | |

Error replies: match `E??~0D~0A` on one logic output.

**Block settings:** Protocol TCP; Server Address the IN1804's address; Remote Port the switcher's
SIS port (H-T1); Auto Connect on. For the Serial block, run `tesira_strings.py --serial` and set
the port to 9600 baud with usage "Command String" or "Both".

## 7. What a first hardware session must settle

| id | question | how |
|---|---|---|
| H-T1 | Which TCP port the IN1804 takes SIS on, and what it sends when a session opens (banner, password prompt, any Telnet negotiation bytes) | Open the port from a PC terminal and record the first bytes |
| H-T2 | Does the NCS block send `1!` with no terminator? If not, does the IN1804 accept `1!` followed by CR? | The block's Connection Log while firing string 3 |
| H-T3 | Is verbose mode reset per session, and is there a fixed banner line a Connection Sequence can key on? | From H-T1's capture; reconnect and query |
| H-T4 | Can a Connection Sequence answer a password prompt? | Only if the switcher has a password set |
| H-T5 | What `1B` and `1Z` answer in verbose mode 3, and whether front-panel changes arrive unsolicited | Connection Log, then press the switcher's front panel |
| H-T6 | Does `~2A` in an Expected Response match a literal `*`? | Strings 16-17 |
| H-T7 | The exact volume reply (sign, zero padding), if volume feedback is wanted | Connection Log after string 20 |
| H-T8 | Serial fallback only: the switcher's RS-232 wiring against the Tesira's DCE port, and CR acceptance | The IN1804 manual, then a loop test |

## 8. Sources

Biamp (each read as raw page text; the help pages are labelled "Tesira v5.3 and earlier"):
- Using the Network Command String block — support.biamp.com/Tesira/Control/Using_the_Network_Command_String_block
- Command String (Tesira help) — tesira-help.biamp.com/Component_Objects/Audio/Controls/Command_String.htm
- Serial Command String Block — support.biamp.com/Tesira/Control/Serial_Command_String_Block
- Logic Charts — tesira-help.biamp.com/System_Design/Logic_Charts.htm
- Controlling third party devices with a TEC-X Control Pad — support.biamp.com/Tesira/Control/Controlling_third_party_devices_with_a_TEC-X_Control_Pad
- Utilizing Network Command String block with Crestron — support.biamp.com/Tesira/Control/Utilizing_Network_Command_String_block_with_Crestron
- Device Roles in a system — tesira-help.biamp.com/System_Design/Device_Roles_in_a_system.htm
- TesiraFORTE X — support.biamp.com/Tesira/Miscellaneous/TesiraFORTE_X
- Tesira network ports and protocols; Tesira release notes (3.1.0, 3.15.0, 3.17.0, 5.4.1)
- Command String Block, TTP attribute table — tesira-help.biamp.com/System_Control/Tesira_Text_Protocol/Attribute_tables/Control_Blocks/CommandString.html

Extron: `extr_scaler_IN1804_Series_v1_3_0_0.py` (corpus snapshot `extron-gs-modules/09062026`,
listed in `vendor-files.manifest.tsv`), read with `tools/wire_table.py`.

**Not found** (method: the pages above and web searches): a maximum string length; what Auto
Connect off does; any Biamp page on controlling Extron gear; the first Tesira version with the
Network block (it existed by 3.1.0, July 2017).
