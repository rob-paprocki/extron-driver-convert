# Q-SYS -> Extron pilot: Clock Audio, then RDL BTN

*Started 2026-10-11, auto session on the owner's say-so to work independently.
This file is the journal — decisions, iterations, measured outcomes.*

## Plan

Approach 1 from the brainstorming turn: build the smallest emitter that goes
`.qplug` -> ControlScript, warm up on Clock Audio CDT100 (R48's planned pilot,
oracle already measured at 6/8 fully-matched + 2 partials), then run the same
emitter against RDL-BTN-Series-1.1.3-Plugin.qplug (the user's target device).

Direction B (Extron NAVigator -> Q-SYS .qplug) is parked until a bench session
can answer whether NAVigator exposes SIS on a plain TCP port, or only via
SPInterface.

## Decisions adopted without checking in

| decision | choice | because |
|---|---|---|
| target dialect | bare `class DeviceClass` + EthernetClass mixin (atero_dsp_unBT2A shape) | closest shipped neighbour to the RDL BTN target; no GC runtime scaffolding needed; loadable in Pro Series projects |
| command naming | derived from the wire prefix (`SARMC`/`GARMC` -> `ARMC`) | vendor command names are editorial; wire bytes are the acceptance criterion |
| multicast UDP receive | not addressed; outbound control only | `extronlib.EthernetClientInterface` is unicast; RDL multicast feedback is a known gap, flagged in the generated module header |
| opaque slots | skipped, counted, listed | project rule — a plausible guess is worse than a recorded gap |
| test harness | assert-based runner matching test_qplug_wire.py | project convention |
| git | branch off `qsys-reader`, draft PR to main | memory: routine git pre-approved, but merging to main is the owner's call |

## Files

- `experiments/qsys/bridge_ir.py` — the thin Command/Response IR (`BridgedModule`,
  `BridgedCommand`, `BridgedTemplate`, `BridgedResponse`) and the `from_qwire(QWireTable)`
  adapter.
- `experiments/qsys/qplug_to_cs.py` — the emitter: `BridgedModule -> ControlScript source`.
- `experiments/qsys/test_qplug_to_cs.py` — the test suite.
- Generated output lives under `experiments/qsys/out/` (git-ignored).

## Runs

Measured 2026-10-11. All numbers are `qplug_wire.py compare <plugin>
<generated_module>` output: how many of the generated module's text/bytes
templates match a template in the plugin's wire table, byte-for-byte.

| plugin | emitted templates | plugin templates | exact | full | partial |
|---|---:|---:|---:|---:|---:|
| ClockAudioCDT100.qplug | 20 | 35 | **20** | 0 | 0 |
| RDL-BTN-Series-1.1.3-Plugin.qplug | 21 | 26 | **21** | 0 | 0 |
| RDL Plugin-1.10.0.qplug | 8 | 10 | **8** | 0 | 0 |

"Exact" means a generated-module template appears verbatim in the plugin's
wire table - the Extron side of the bridge speaks the device's wire bytes.
"Full" means the generated template is a specialisation of a plugin template
(same shape, slot already resolved); "partial" means some but not all strings
covered. Both pilots and the RDL general plugin land in the exact bucket for
every emitted template; nothing is "partial".

Against the vendor Extron Clock Audio module (`clau_dsp_CDT100_v1_0_3_0.py`):
- generated has 19 commands (plugin-labeled: ARM, CH32, PP, Psload, Pssave, ...)
- vendor has 7 commands (editorially-named: ARMC, LEDLightControl, LoadPreset,
  PhantomPower, SavePreset, SwitchLogicStatus, ConnectionStatus)
- shared command names: only `ConnectionStatus` (names are editorial, not
  derivable from wire). The wire-level overlap is the acceptance criterion,
  and that is 20/20.

### Known gaps surfaced on this run

1. **Multi-slot format strings pass `qualifier.get('SlotN', '')`** for earlier
   slots. The slot source is not reconstructed; the pilot ships a working
   skeleton and a TODO explaining what to replace. Clock Audio
   `SCH32 {} {}={}` and `PP {} {}` are the cases this bites.
2. **Reply-decode value maps.** The plugin's Lua if/else chain mapping replies
   like `ACK BTS 0/1/2` into friendly values ('Idle'/'Discoverable'/'Connected')
   is not reconstructed. Each `__Match` emits `value = match.group(1).decode()`
   plus a `# TODO: decode group -> status value` comment.
3. **BTNAME{<name>} braces.** The RDL BTN wire has literal `{` and `}` wrapping
   the parameter, and the reader's canonical form `'BTNAME{{}}'` is ambiguous
   about which braces are literal. The emitter passes the raw canonical as a
   Python string literal (`'BTNAME{{}}'`), which at runtime produces
   `BTNAME{{}}` - six wrong bytes. This specific case is not fixed in the pilot.
4. **Multicast UDP receive.** `extronlib.EthernetClientInterface` is unicast
   only; status feedback over `239.254.50.0:9000` does not arrive at the
   generated module. Outbound control is unaffected. The generated module's
   docstring states this.

### Test suites green on this branch

- `experiments/qsys/test_qplug_wire.py`: 14/14 pass (reader).
- `experiments/qsys/test_qplug_to_cs.py`: 19/19 pass (new, this branch).
- `tools/test_wire_table.py`: 13/13 pass + 34 skipped on vendor input.
- `tools/test_pkp2cs.py`: 58/58 pass + 32 skipped on vendor input.

### Direction B (Extron -> Q-SYS) — DTP3 CP pilot

Added 2026-10-11 after the owner pivoted to "another scaling-capable switcher
first, including RS-232 insertion for endpoints." NAVigator stays parked
(SPInterface uncertainty) and DTP3 CrossPoint takes its place: it speaks plain
TCP SIS on port 23, which is routable from a Q-SYS Core without any
proprietary channel.

**New files:**

- `experiments/qsys/cs_to_qplug.py` — the Q-SYS plugin emitter. Takes a
  `PluginSpec` (device metadata plus a few feature toggles) and produces a
  `.qplug` with `PluginInfo`, `GetProperties`, `GetControls`, `GetPages`,
  `GetControlLayout`, and the full runtime block. Three built-in specs:
  `dtp3-cp-884` (8x8), `dtp3-cp-42` (4x2), `dtp3-cp-62` (6x2). Standard
  library only.
- `experiments/qsys/test_cs_to_qplug.py` — 15 tests covering Lua-rendering
  primitives, spec sanity, structural invariants on the emitted plugin, and
  round-trip through `qplug_wire.py` to confirm the output is a parseable
  Q-SYS plugin.

**v1 scope (what the plugin actually drives):**

- Routing: `MatrixTieCommand` as three explicit tie-type variants
  (`<in>*<out>!` A+V, `<in>*<out>%` Vid-only, `<in>*<out>$` Aud-only).
  `RouteSource[o]` + `RouteType[o]` on the Q-SYS side.
- I/O labels: `MatrixIONameCommand` + `MatrixIONameStatus` wired to
  `InputName[i]`, `OutputName[o]` text controls.
- Input signal presence: `w0LS` poll, `In00 <bitmask>` parse, feeds LED
  indicators per input.
- Video mute, Global video mute, Executive mode, Preset recall — all with
  the SIS forms the ControlScript module uses.
- Per-output RS-232 insertion: a `TcpSocket` per output on
  `(IP, Serial Base Port + output_number)`. `SerialSend[o]` writes to the
  socket (and clears itself so a repeat of the same value re-fires);
  `SerialReceived[o]` accumulates whatever comes back. "Serial Base Port"
  is a user-configurable property (default 2200); the installer sets it to
  match the Extron SIS reference for the specific DTP3 unit.

**Measured round-trip of `dtp3_cp_884.qplug`:**

Parsing the emitted plugin back through `qplug_wire.py` yields:

```
transports: ['tcp']
send sites: 2            (main SIS socket + per-output serial socket)
templates: 18            (unique canonicals)
response patterns: 33    (the Lua regex table in handleLine)
opaque templates: 0      (nothing silently guessed)
```

Scoring against the vendor Extron ControlScript module
(`extr_matrix_DTP3_CrossPoint_884_Series_v1_7_00.py`, 101 Extron templates):

| result | count | what it means |
|---|---:|---|
| exact | 5 | Plugin's canonical appears byte-for-byte in the module |
| compatible | 9 | Plugin's slot shape composes with a module canonical |
| none | 87 | Module template outside v1 scope (audio mixer, HDCP, scaler details) |

The 14 matched templates cover every v1-scope command: three tie forms (both
MatrixTieCommand canonicals of the module), ExecutiveMode set + query,
VideoMute set + query, PresetRecall, plus `w{}*{}ASPR\r\n`, `w{}*{}ITYP\r\n`,
`w{}*{}RATE\r\n` which the plugin would use if the scope widened. The 87
"none" lines are the audio/HDCP work explicitly deferred to v2.

**Known gaps and risks** (documented in `cs_to_qplug.py`'s docstring):

1. No bench verification. Acceptance is round-trip through `qplug_wire.py`
   plus the subset check against the ControlScript module's wire table.
   Loading the plugin in Q-SYS Designer F6 emulation is a Windows-only
   next step.
2. The RS-232 insertion port convention (Serial Base Port + output number)
   is a reasonable default but needs to be checked against Extron's SIS
   reference for each specific DTP3 CP firmware before shipping.
3. `GetControlLayout` is a diagnostic grid, not a polished panel. Designer
   can lay out the Controls pins any way the user wants; the plugin's role
   is to supply the Controls, which it does.
4. No reply decoding for the ValueStateValues the ControlScript module
   maps (e.g. VideoMute 0/1/2 -> Off/VidMute/FullMute). The plugin surfaces
   the raw integer values from the device.
5. Only three device specs built-in (CP 884, CP 42, CP 62). Other DTP3
   CrossPoint models that share the SIS surface can be added as a one-line
   `PluginSpec(...)`.

**Direction B (NAVigator) is still deferred** — SPInterface vs plain TCP
remains unanswered without bench time.

## 2026-10-25: byte-level vendor coverage + runtime fix (R48)

Picked R48 (Q-SYS -> Extron pilot on Clock Audio CDT100) back up to measure
against the vendor module properly (STATUS methodology: wire-correctness is
necessary but not sufficient; Finding 14).

### Byte-level vendor coverage

The old scoreboard counted template subsumption against the plugin. The real
question for R48 is: does the generated module cover the vendor Extron
module's wire surface? Enumerate every concrete string the vendor module
can send (canonical templates filled with their `value_maps`); for each one,
is there a generated template whose shape covers it?

Measured 2026-10-25 against `clau_dsp_CDT100_v1_0_3_0.py`:

| metric | count |
|---|---:|
| vendor concrete strings | 55 |
| covered by generated | 37 (67.3%) |
| uncovered | 18 |

The 18 uncovered strings are all `LOAD <N>\r` and `SAVE <N>\r` for N=1..9.
The Q-SYS plugin hardcodes preset 0 (`Psload`/`Pssave` emit `LOAD 0\r` and
`SAVE 0\r` only; the plugin never exposes a preset number control). Upstream
limitation of the plugin, not an emitter bug - the plugin itself cannot
produce those bytes either.

The generated module also exposes 12 commands whose wire bytes don't appear
in the vendor module (BVERSION, CH32B, GAS, GRGB, GTS, Id, SASIP, SMKMD,
SRGB, STS, VERSION, CH32B get-form). These are plugin surface Extron's module
does not cover - a legitimate expansion of command surface, not an error.

Measurement script: scratch, enumerates per `wire_table.py dump` JSON output.

### Runtime fix: AttributeError on qualifier=None

Ran the generated CDT100 through `experiments/exec_harness/drive.py` as the
Finding 14 methodology recommends. Five commands raised at runtime:

```
CH32   set 11/11 raised  AttributeError: 'NoneType' object has no attribute 'get'
CH32B  set 11/11 raised  AttributeError: 'NoneType' object has no attribute 'get'
PP     set 11/11 raised  AttributeError: 'NoneType' object has no attribute 'get'
SRGB   set 11/11 raised  AttributeError: 'NoneType' object has no attribute 'get'
STS    set 11/11 raised  AttributeError: 'NoneType' object has no attribute 'get'
```

Cause: `qplug_to_cs._emit_set` / `_emit_update` generate multi-slot bodies
that call `qualifier.get('Slot1', '')`. When a caller passes `qualifier=None`
(as the harness does, and as the vendor module's `Set(cmd, value)` would
if the user omits a qualifier), the method dereferences None and raises.
Classic Finding 14 shape: compiles, resolves every name, scores wire-correct,
raises at runtime.

Fix in `qplug_to_cs.py`: emit `if qualifier is None: qualifier = {}` as the
first body line whenever `slot_count > 1`. Both `_emit_set` and `_emit_update`.

Verification after fix:

```
CDT100 raises: 0
RDL BTN raises: 24   (all ValueError: invalid literal for int() on adversarial
                      'On'/'Off' input to numeric commands; input-validation
                      gap, not a translator bug - exec_harness feeds every
                      Set the value map keys from the vendor module as well
                      as adversarial strings)
```

Regression test added to `test_qplug_to_cs.py`:
`test_multi_slot_set_methods_do_not_raise_on_qualifier_none` loads the
generated CDT100 against `exec_harness/extronlib_stub`, stubs the SetHelper
to a no-op, and invokes every SetXxx method with `qualifier=None`. Asserts
no AttributeError. 20/20 tests pass.

## 2026-10-26: reply decoding step 1 - capture the parameter

Second runtime pass on CDT100. Before this change, every __Match handler
in a generated module wrote `value = 'OK'` into the status - the handler
knew a reply had arrived but discarded the payload. For a status consumer
on the Q-SYS side, every event looked the same regardless of what the
device actually said.

Cause: the reader (qplug_wire) extracts response patterns from both
`string.match` sites and literal equality checks. In Clock Audio CDT100's
Lua reply parser, the per-command branches are an `elseif cmd=="GARMC"`
chain against a pre-tokenized `cmd`. The reader picks up those command
literals as response "patterns" (handler keys), so the IR carries just
the command token - "GARMC", "SMKMD" etc. - not a regex with capture
groups. The emitter saw no `(` in the pattern and fell through to the
stub branch.

Fix (bounded, no Lua AST translation):

- Add `_augment_match_pattern(py_pat)` in qplug_to_cs.py. For a simple
  prefix pattern (bare word, no regex metachars) it appends
  `\s*(.*?)\r?\n?$`, turning the AddMatchString regex into one that
  captures whatever the device sent after the command token. For patterns
  that are already real regexes (something with `(`, `|`, `.`, `%`, ...)
  the function returns them unchanged.
- Both the AddMatchString emission and `_emit_match`'s capture-group
  detection use the augmented form. The handler body now decodes
  `match.group(1).decode().strip()` as the status value for augmented
  patterns, falling back to `match.group(0).decode(errors='replace')` for
  patterns with no capture.

What this does and does not do:

- DOES: status for a `GARMC 1\r` reply is now the string `"1"` rather
  than hardcoded `"OK"`. A consumer can at least observe which raw value
  the device returned.
- DOES NOT: translate the `"1"` into `"On"` the way the vendor Extron
  module does via its ValueStateValues dict. That mapping lives in the
  Lua elseif chain's body (e.g. `ARM.Boolean = param=="1"` sets the
  boolean side of a Q-SYS Control), and extracting it needs a Lua AST
  walk the reader does not do. The generated handler now carries a block
  comment pointing a human reviewer at the right spot.

Measured on CDT100 after the fix:

- 14 of 16 AddMatchString patterns augmented (simple prefixes); 2 were
  already real regexes and left alone
- Every __Match handler now writes a decoded group instead of 'OK'
- exec_harness: 0 raises (unchanged from the previous fix)
- 21/21 tests pass (added
  `test_match_handlers_decode_reply_parameters_not_stub_ok`)

Still deferred for a later pass:

- Translating the Lua elseif body (the value mapping and the per-Control
  side-effect) into Python. Full Lua AST walk; est. several days.
- Mapping multi-field replies like PP's `PP1=X PP2=X PP3=X PP4=X ID=X`
  into a dict/qualifier shape. The vendor module's ValueStateValues
  structure is the target.
