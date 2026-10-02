# Q-SYS: what converting drivers to and from it would take

*2026-10-01. Scoping only: nothing is built yet. Read-only surveys of the owner's Q-SYS Designer
10.5 install and plugin library, QSC's online developer documentation, and four same-device
pairs against Extron's own modules, then an independent critic who re-checked the claims and
corrected two of the pairings. Everything below is static reading unless it says otherwise; no
plugin, Core or device was run.*

## 0. In short

- **A Q-SYS plugin is a plain-text Lua file** (`.qplug`) with a fixed shape: a `PluginInfo`
  table, design-time functions that declare properties, controls and layout, and a runtime
  section that opens a TCP, UDP or serial connection, sends command strings, parses replies and
  writes status into controls. That shape maps onto Extron's ControlScript `DeviceClass`
  closely enough to convert command tables in both directions (§3).
- **Only some plugins are readable.** Of the 97 plugin files in the owner's library, 25 are plain
  `.qplug`; 72 are `.qplugx`/`.qplugx2`, which QSC's own file-type labels call "Encrypted
  Plugin". Those are off limits and were not opened. Designer also ships 28 plain Attero Tech
  plugins.
- **Same-device pairs exist, and the first one scored well.** Clock Audio CDT100: all 9 commands
  Extron's module sends are among the 21 the Q-SYS plugin sends, byte for byte; the replies
  differ, and the manual sides with Q-SYS in three places. Three more pairs are found but not
  scored yet: Barco ClickShare CX, Samsung MDC displays and the Extron SMP 351 (§2).
- **Controlling a Q-SYS Core from Extron is already done by Extron**:
  `qsc_dsp_Q_Sys_Core_Series_v1_15_1_0.py` speaks QSC's ECP text protocol. QSC also documents a
  JSON-RPC protocol (QRC, TCP 1710). That is a different job from converting device drivers;
  the owner wants it, as a separate job (§6, decision D-Q4).
- **What is missing before any building:** a reader that turns a Lua plugin into this project's
  wire table, and a way to run a generated plugin (Designer's emulator, on this PC). The four
  owner decisions are made (§6, 2026-10-01): Q-SYS → Extron first.

## 1. What a Q-SYS plugin is

| part | what it holds | Extron counterpart |
|---|---|---|
| `PluginInfo` (Name, Version, Id, Manufacturer, Model, ...) | identity | module file name and header |
| `GetProperties` / `RectifyProperties` | design-time settings: model, connection type, poll rate | constructor arguments, `Models` |
| `GetControls` | the public surface: buttons, knobs, text, indicators; `Count` makes arrays | `Commands` names and qualifiers |
| `GetControlLayout`, `GetPages`, graphics | the panel the user sees in Designer | **none**: Extron's UI lives in the main program |
| runtime, under `if Controls then` | `TcpSocket` / `UdpSocket` / `SerialPorts` / `HttpClient`, timers, send and parse | `Set*` / `Update*`, `AddMatchString` handlers, the transport classes |

Facts that matter for a converter:
- **Strings are built imperatively**, not from a table: a verb plus arguments plus CR (Clock
  Audio), verb fragments plus a class prefix (PJLink), or binary frames with a checksum (Samsung
  MDC). Replies are parsed with Lua patterns in if/else chains, not a regex table.
- **Each plugin does its own pacing and polling** (queues, stop-and-wait, health and reconnect
  timers). Extron modules leave polling to the caller. That logic has no direct home in a
  generated Extron module and becomes host-script code or is recorded as opaque.
- **The control objects are the state store.** Whether a script write to a control fires that
  control's own handler is not documented (it matters for echo suppression; to test).
- **Signatures.** 19 of the 27 plain plugins in the library start with a "BEGIN DIGITAL
  SIGNATURE" Lua comment; 8 do not, which suggests unsigned plugins load. Whether Designer
  rejects an edited signed file is untested.

## 2. Same-device pairs

| device | Q-SYS plugin (plain) | Extron module | state |
|---|---|---|---|
| Clock Audio CDT100 | `ClockAudioCDT100.qplug` (v3.6, MK1-MK3) | `clau_dsp_CDT100_v1_0_3_0.py` (MK I/II family, finding 10) | **scored**, below |
| Barco ClickShare CX-20/30/50 | `BarcoClickShareCX.qplug` | `barc_cs_CX_x0_Series_v1_1_4_0.py`, `barc_cs_CX_50_Gen2_v1_0_0_0.py` | found, same `/v2/` API on 4003; not scored |
| Samsung MDC displays | `SamsungCommercialDisplay.qplug` | the `smsg_display_QM*` family, e.g. `smsg_display_QMxxR_v1_1_4_0.py` | found, same 0xAA frames and command bytes; not scored |
| Extron SMP 351 | `ExtronSMP351.qplug` (QSC-written, Telnet 23) | `extr_sm_SMP_300_Series_v1_19_20_0.py` | found; not scored |

**Clock Audio CDT100, the one pair scored.** Both use UDP to port 49494 and CR-terminated text
verbs. Of 14 functions both implement, 9 send identical bytes (`SASIP`, `SARMC`, `GARMC`,
`PP`, `QUERY`, `SCH32`, `GCH32`, `LOAD 0`, `SAVE 0`); the Extron module's 9 verbs are a strict
subset of the plugin's 21. The differences are in replies: Extron's regexes expect `0|1` where
the MK3 manual prints `ON`/`OFF` for `QUERY`, never match `ACK SARMC`, and accept `BSTATUS` for
B1-B4 where the manual defines B1-B12. Q-SYS covers MK2/MK3 commands Extron has no source for.
**Verdict:** command strings carry across mechanically in both directions; reply parsing does
only after the manual adjudicates; polling and connection behaviour is hand work. This repeats
finding 10's Clock Audio result from a third implementation.

**A pairing lesson, again.** The first Barco attempt paired the CX plugin with Extron's
CSM/CSC/CSE module (`barc_sp_ClickShare_Series`) and found zero shared commands; the right
Extron module for the CX series speaks the same API. The first Samsung search looked for "sams"
and "mdc" in file names and missed Extron's `smsg_` prefix. Finding 10 made the same mistake
with Clock Audio. **Pairs must be chosen by declared model list and protocol, and checked,
before any score is quoted.**

## 3. How the two models map

Near-direct: a control's event handler is a `Set`; a poll plus its parse branch is an `Update`
plus a match handler; writing a control is `WriteStatus`; a `Count` array is a qualifier (1-based
index against string values); the plugin's Status indicator is `ConnectionStatus`;
`TcpSocket`/`UdpSocket`/`SerialPorts` are Extron's interface classes; the Model property is the
`Models` dict.

Lossy, needing design or an explicit "opaque" record:
1. **Layout and pages** have no Extron counterpart. Q-SYS → Extron drops them; Extron → Q-SYS
   must invent a control surface and a layout, and nothing can judge layout quality automatically.
2. **Reply parsing** is a Lua if/else chain, and one reply can update many controls; each branch
   becomes an Extron regex and handler.
3. **Polling, queues, timeouts, reconnects, authentication handshakes** (PJLink's MD5 login,
   wake-on-LAN, receive-port selection) live inside the plugin.
4. **Multi-qualifier commands** flatten differently (per-colour control arrays against
   `Channel`/`Color` qualifiers, "Global" controls against qualifier `All`).

## 4. Tooling: what exists, what would have to be built

Installed: Q-SYS Designer 10.5 (build 10.5.0-2609.007), a .NET app. No help files, no plugin
compiler or packager. It registers `.qplug`, `.qplugx` and `.qplugx2` as separate file types,
ships seven plain Lua libraries (one GPLv3) and 28 plain Attero Tech plugins, and has a built-in
emulator (F6) that runs plugin logic on the PC without a Core. QSC documents the plugin API online
(`help.qsys.com/DeveloperHelp`). No scripting licence is needed on Cores running 10.0 or later.

| needed | exists? | note |
|---|---|---|
| A Lua plugin → wire table reader, the Q-SYS side of `tools/wire_table.py` | **no** | standard-library Python can tokenise Lua well enough to find the send and parse sites; the target is the same normalised table (command, template, reply pattern, value map, opaque count) |
| Score the four pairs | no | needs the reader |
| Run a generated plugin | **Designer F6**, on this PC | GUI-bound, one design at a time, **no serial in emulation**, TCP works on a chosen NIC; a machine-bound step for `ENVIRONMENT.md`, not the portable suite |
| Run a plugin headless | no | no documented command-line emulator; a community evaluation script runs only the design-time functions and needs a Lua interpreter, which the repo's standard-library rule excludes |
| `.qsys` design files | not parsed | they start with the .NET BinaryFormatter header this repo already parses for `.pkp`; a lead, untested |

## 5. Unknowns that need a test or a direct read

- Whether a script write to a control fires its event handler (echo suppression depends on it).
- Whether an unsigned or edited `.qplug` loads in Designer 10.5 (one harmless hand-made test file).
- Timer repeat default, several lines per `TcpSocket` Data event, the Core's Lua version, where
  `rapidjson` comes from, how a serial pin binds to a port.
- Licence: no Designer EULA was found on disk or online; QSC says nothing about reading or
  converting third-party plugins; each plain plugin is under its author's terms. Treat it as open,
  as the Crestron question already is.

## 6. Decisions (the owner, 2026-10-01)

| id | decision | recommendation | **decided** |
|---|---|---|---|
| D-Q1 | **Which direction first.** Extron → Q-SYS (generate `.qplug` from an Extron module) or Q-SYS → Extron (translate a plugin into ControlScript). | **Extron → Q-SYS.** Extron's corpus has about 2,200 ControlScript modules; only 25 Q-SYS plugins are readable. Generating from Extron reaches far more devices, and the four pairs become the oracle that checks the output, the way finding 14 used Extron's own pairs. | **Q-SYS → Extron first**, against the recommendation. Extron → Q-SYS follows. |
| D-Q2 | **Provenance for Q-SYS material.** `.qplug`, `.qplugx`, `.qplugx2`, `.nupkg` and `.qsys` are vendor files: add `.gitignore` rules and manifest lines before any is copied near the repo. Sealed formats are never opened. May generated plugins derived from vendor modules be tracked, as was decided for generated Extron modules on 2026-09-24? | add the rules first; tracking generated plugins is the owner's call | **Generated plugins may be tracked.** The vendor rules still come first. |
| D-Q3 | **Lua at test time.** The portable suite is standard-library only. Executing generated Lua offline needs a Lua interpreter (excluded) or Designer's emulator (this PC only). | keep the suite stdlib-only (wire-table checks); run F6 emulation as a machine-bound acceptance step | **Designer's emulator**, as recommended; no Lua interpreter in the repo. |
| D-Q4 | **Q-SYS as a device**: an Extron or Crestron driver for a Core over QRC (JSON-RPC, TCP 1710). Extron's existing module uses the older ECP protocol. | out of scope unless the owner needs it; it is a separate, well-documented job | **Yes, as a separate job** (ROADMAP R49). |

## 7. First steps, as decided

Q-SYS → Extron first, so the output is a ControlScript module, which the existing exec harness
can run offline; Designer's emulator is needed only once the Extron → Q-SYS direction starts.

1. Add the `.gitignore` rules and manifest lines for Q-SYS vendor files (D-Q2), then write the
   Lua reader (stdlib) and its tests against the 25 plain plugins: every send site and reply
   branch found, or counted as opaque (ROADMAP R46).
2. Score the three unscored pairs, model family checked first (finding 10's rule) (R47).
3. Pilot one device Q-SYS → Extron. Clock Audio CDT100 is the natural first: smallest surface,
   already scored, and finding 10 already holds the manual-based adjudication. Translate the
   plugin into a ControlScript module, compare its wire table with both QSC's plugin and
   Extron's module, and run it in `experiments/exec_harness/` (R48).
4. Then Extron → Q-SYS: load a generated plugin in Designer, emulate it against a stand-in
   device on the PC, and compare its wire table with QSC's own plugin.

## Sources

Owner's install and library: `C:/Program Files/QSC/Q-SYS Designer 10.5/`,
`Documents/QSC/Q-Sys Designer/` (96 Asset Manager packages, 16 sample designs). QSC developer
documentation: Building a plugin, Reserved Functions, Plugin Encryption Tool, TcpSocket,
SerialPorts, Emulate Mode, QRC Overview and Commands, What's New in Q-SYS 10.0
(help.qsys.com). Extron modules: corpus snapshot `extron-gs-modules/09062026` (vendor material,
listed in `vendor-files.manifest.tsv`). No plugin or module text is copied here.
