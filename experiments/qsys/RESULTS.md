# Q-SYS plugins read as wire tables: the four pairs, measured

*2026-10-02. ROADMAP R46 (first version) and R47. Static reading of plain `.qplug` source
against Extron's ControlScript modules for the same devices; nothing was run on a Core,
in Designer's emulator or against a device. The owner chose Q-SYS → Extron first
(SCOPE.md §6), and this is its first step: knowing exactly what a plugin sends.*

## 0. In short

- **`lua_parse.py` parses all 27 plain plugins** in the owner's library: a full Lua 5.3
  parser, standard library only. The 72 encrypted ones stay unopened.
- **`qplug_wire.py` turns a plugin into a wire table** in `tools/wire_table.py`'s form. It
  resolves what each socket write, UDP send and HTTP request carries, back through helpers,
  call sites and queue tables, and keeps the parts of one call or one queued item together.
  Whatever it cannot resolve is a counted slot, never a guess.
- **Against Extron's modules, at the wire:**

| pair | Extron templates | identical on the wire | notes |
|---|---|---|---|
| Clock Audio CDT100 | 8 | **6 fully** (5 exact, `SCH32` 20 of 20 strings), 2 partly | the plugin loads and saves preset 0 only (1 of 10 strings each) |
| Extron SMP 351 (vs SMP 300 Series module) | 105 | 3 (2 exact, 1 full) | **11** if SIS's two escape spellings count as one (§2) |
| Barco ClickShare CX (vs both CX modules) | 12 | 2 (`system/status`, `operations/reboot`) | different endpoints, not different bytes (§3) |
| Samsung MDC (vs QMxxR module) | 20 | 0 measured | the plugin builds its frames in a loop: opaque, not yet resolvable (§4) |

## 1. How the comparison works

Each Extron template is expanded through its value maps into every concrete string it can
send (`SCH32 {} {}{}\r` → 20 strings), and each string is checked against the plugin's
templates, where a slot matches one or more characters. A slot the plugin fills from a
numeric `for` counter, arithmetic or a control's `.Value` matches digits only, so a poll
like `WM{#}AU|` cannot claim a mute command `WM4000…*1AU|`. Results per Extron template:
*exact* (same template), *full* or *partial* (how many of its strings the plugin can send),
*compatible* (no expansion possible, but some common string), *none*.

A plugin template with no literal content but its line ending (`{}\r`: a Telnet password,
a pass-through of user text) would match everything; it is listed as *unanchored* and
covers nothing.

## 2. Extron SMP 351: two spellings of one protocol

QSC's plugin writes SIS escape commands in the web form, `W…|` with an upper-case `W`
(`WBRCDR|\r`, `WY1RCDR|\r`, `WM4000{}*1AU|\r`); Extron's own module writes `w…\r`
(`wBRCDR\r`, `wY{}RCDR\r`). SIS accepts both, so on identical bytes only 3 of 105 match,
and with the two spellings treated as one (`compare --sis`, reported as an equivalence,
never as identical) 11 match: chapter marker, record, input ties, audio mutes, video mute,
streaming preset names. The other 94 are commands the plugin does not implement; it covers
a recorder's front panel, Extron's module the whole device.

## 3. Barco ClickShare CX: the same API, used differently

Both speak Barco's REST API on 4003, and two paths are identical. Elsewhere the plugin reads
collections (`v2/configuration/input-cards`, `.../video-outputs`) where Extron's module reads
items (`input-cards/{}`, `video-outputs/{}`), and the plugin never touches audio, video
mode, standby or wallpaper. Paths are compared; methods and bodies are not yet.

## 4. Samsung MDC: what is not resolved yet

The plugin builds each frame as `"\xAA" .. string.char(cmd.Command) .. string.char(ID) ..`
then appends every data byte and a checksum in a `while` loop. A value accumulated in a loop
is, by the rule above, opaque: all three send sites read `{}` (counted, 3 slots). Resolving
it needs the reader to execute a helper's body in order, unrolling loops whose bounds are
known (`cmd.Data` is a constant table at most call sites), which it does not do yet (ROADMAP
R50). Until then this pair is unmeasured, not a mismatch.

## 5. What this does NOT show

- **Nothing ran.** A matching template says both programs would put the same bytes on the
  wire for that command; it does not say either works with the device.
- **Replies are listed, not compared.** The reader collects each plugin's Lua patterns and
  literal reply keywords from its receive handlers (46 for Clock Audio, 73 for the SMP);
  Lua patterns and Extron's regular expressions are not yet compared.
- **One plugin per device.** The pairs were chosen by declared model and protocol (SCOPE.md
  §2); SMP 351 is compared with Extron's SMP 300 Series module, which covers it.
- **The reader is flow-insensitive within a function**, apart from the and/or and queue
  correlations above: two assignments to one local are both alternatives. Where that would
  over-count, the result says so (the alternative cap is logged in `notes`).

## Reproduce

```
python experiments/qsys/qplug_wire.py dump samples/qsys/library/ClockAudio_CDT100.3.6.0/ClockAudioCDT100.qplug
python experiments/qsys/qplug_wire.py compare samples/qsys/library/ClockAudio_CDT100.3.6.0/ClockAudioCDT100.qplug corpus/extron-gs-modules/09062026/clau_dsp_CDT100_v1_0_3_0.py
python experiments/qsys/qplug_wire.py compare --sis samples/qsys/library/ExtronSMP351.1.1.0/ExtronSMP351.qplug corpus/extron-gs-modules/09062026/extr_sm_SMP_300_Series_v1_19_20_0.py
python -u experiments/qsys/test_qplug_wire.py
```

The plugins are the owner's copies, untracked and pinned in `vendor-files.manifest.tsv`
(`samples/qsys/`); the Extron modules are in the corpus snapshot.
