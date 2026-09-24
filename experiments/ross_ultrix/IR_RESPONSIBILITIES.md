# IR_RESPONSIBILITIES.md — what the Ross Ultrix plugin tier does, as input to a cross-vendor IR

ROADMAP.md item R34. Sources read in full: `findings/17-how-a-human-writes-one.md`;
`samples/Custom Module/plugin_ross_ultrix.py` (78 lines); `samples/Custom
Module/mod_ross_matrix_RossTalk_v1_1_0_0.py` (273 lines); `samples/Custom
Module/mod_ross_matrix_tsl_3_1_v1_1_0_0.py` (288 lines); `tools/wire_table.py`
(1045 lines); `findings/04-crestron-interop-verdict.md` lines 84–104;
`findings/05-samsung-cross-vendor.md` (in full). `samples/Custom
Module/tools.py` (7,644 lines) was targeted-read, not read cover to cover:
the docstring/changelog (lines 1–134), the `__InterfaceWrapper` class and its
six transport subclasses (1002–1669) in full, and grep hits for
`Subscribe`/`Poll`/`Connect` across the rest of the file to confirm nothing
relevant was missed outside that range. `experiments/ross_ultrix/` itself
holds no copies of `plugin_ross_ultrix.py` or `tools.py` — those files live
only under `samples/Custom Module/`; this document cites them there.

Two extraction gaps below (§b.10, §b.11) were found by actually re-running
`tools/wire_table.py dump` against both hand-written modules on 2026-09-23,
not by reading finding 17 — finding 17 §4 reports command *counts* (5 and 2)
without checking template/response fidelity, and both counts are correct as
far as they go.

## (a) What each layer of the plugin tier is responsible for

The "plugin tier" spans four files with distinct jobs. None of them is a
`.pkp`; all are ControlScript `.py`.

### 1. Transport
- **Which physical/network protocol, and its parameters.** Each device
  module defines its own duplicate set of transport subclasses
  (`SerialClass`, `SerialOverEthernetClass`, `EthernetClass`) wrapping
  `extronlib.interface.SerialInterface`/`EthernetClientInterface`
  (`mod_ross_matrix_RossTalk_v1_1_0_0.py:206-273`); the TSL 3.1 module keeps
  only the Ethernet one, defaulted to port 5727
  (`mod_ross_matrix_tsl_3_1_v1_1_0_0.py:265-287`, default at line 267).
  `tools.py` provides a second, general implementation of the same six
  transport kinds (Serial, SerialOverEthernet, Ethernet, Dante, SSH, SPI) as
  `Create_Device` methods on six wrapper classes
  (`samples/Custom Module/tools.py:1577-1669`).
- **Connect/disconnect lifecycle and auto-reconnect.** `tools.py`'s
  `__InterfaceWrapper` runs a 10-second timer that calls `Connect()` again
  whenever the interface isn't connected and connection was previously
  requested (`tools.py:1131-1132`, `1147-1152`). On top of that, the plugin
  tier adds its own connect-ordering policy: `plugin_ross_ultrix.py:70-78`
  staggers the three device instances' initial `Connect()` calls 0.1s apart
  via three separate `Wait(0.1)` closures, rather than connecting all three
  at once.
- **Model-variant dispatch.** Both device modules and `tools.py` share an
  identical "if this device type declares named model subclasses, invoke the
  matching one" pattern (`mod_ross_matrix_RossTalk_v1_1_0_0.py:212-217`;
  `tools.py:1057-1063`) — unused by Ross (`self.Models = {}` stays empty,
  `mod_ross_matrix_RossTalk_v1_1_0_0.py:20`) but present as scaffolding in
  every module built from the template.
- **Rate limiting / synchronous send.** `tools.py`'s `__InterfaceWrapper`
  supports an optional command pacer (a timer draining a queue,
  `tools.py:1003`, `1021-1023`, `1071-1080`, `1244-1248`) and a synchronous
  `SendAndWait(commandstring, timeout=0.5, **args)` (`tools.py:1254-1266`).
  Neither Ross device module opts into either — they only call
  `self.Send(commandstring)` from `__SetHelper`
  (`mod_ross_matrix_RossTalk_v1_1_0_0.py:61-63`) — but the capability is part
  of the transport tier's contract for any module that plugs into it.

### 2. Framing
- Each device module's "RECOMMENDED not to modify" block defines
  `__ReceiveData`, which is supposed to accumulate a byte buffer, run every
  registered regex from `AddMatchString` against it, trim matched spans, and
  cap the buffer at `__maxBufferSize` (10,000 bytes) when nothing matches
  (`mod_ross_matrix_tsl_3_1_v1_1_0_0.py:236-258`, which is the version that
  actually runs this logic).
- **The RossTalk module's copy of this same function is dead code.**
  `mod_ross_matrix_RossTalk_v1_1_0_0.py:176-179`:
  ```
  def __ReceiveData(self, interface, data):
      # Handle incoming data
      self.OnConnected()
      return
      self.__receiveBuffer += data
      ...
  ```
  The bare `return` on line 179 means every line below it — the buffer
  accumulation, the `AddMatchString` regex loop, the buffer cap — never
  executes. RossTalk also registers zero `AddMatchString` patterns (grep of
  the file finds none), so this is consistent, not merely unreachable: the
  module was written to do no incoming framing/parsing at all. Receiving any
  byte from the device only calls `OnConnected()`.
- `tools.py`'s `__fn_device_init` wires a device module's `ReceiveData`
  (if present) into its own receive-buffer callback list
  (`tools.py:1054-1055`), so framing responsibility formally belongs to the
  device module, with `tools.py` only forwarding raw interface bytes to it
  and logging them (`tools.py:1103-1117`).

### 3. Command table
- Each device module declares a `self.Commands` dict: command name →
  `{'Parameters': [...], 'Status': {}}`
  (`mod_ross_matrix_RossTalk_v1_1_0_0.py:23-29`;
  `mod_ross_matrix_tsl_3_1_v1_1_0_0.py:99-102`).
- `Set<Command>` methods build the wire string, e.g.
  `'CC {}{:02}\x0d\x0a'.format(int(qualifier['Bank']),int(value))`
  (`mod_ross_matrix_RossTalk_v1_1_0_0.py:57`) and hand it to `__SetHelper`
  (`61-63`), which just calls `self.Send`.
- **Parameter shaping that never reaches a `Commands` dict lives one layer
  up, in the plugin.** `plugin_ross_ultrix.py:45-54`'s `setMatrixTieCommand`
  converts a UI-level `sw_type` string (`'Video'` / `'Audio'` /
  `'Audio/Vdeo'` — note the typo, line 51) into a `Levels` wire parameter via
  three hardcoded `if` branches, and applies a fixed `output = int(output)+53`
  offset before calling `self.dev.Set('MatrixTieCommand', ...)`
  (line 53-54). None of this arithmetic or string-matching is visible from
  the device module alone.

### 4. Parsing / feedback decode
- TSL 3.1's `__MatchOutputTieStatus` (`mod_ross_matrix_tsl_3_1_v1_1_0_0.py:112-120`)
  decodes an 18-byte frame (2-byte output id + 16-byte input name) matched by
  the regex `rb'([\x81-\x90][\x00])(.{16})'` (line 105): it converts the
  2-byte id to an output number, then looks the 16-byte name up by *position*
  in a hardcoded 130-plus-entry `__input_names` list
  (`mod_ross_matrix_tsl_3_1_v1_1_0_0.py:22-97`) to get a numeric UI value.
- RossTalk performs no feedback decode at all (see Framing above) — its only
  status is `ConnectionStatus`, driven by `OnConnected`/`OnDisconnected`, not
  by anything read off the wire.

### 5. State / feedback storage and dispatch
- The shared "RECOMMENDED not to modify" block in both device modules
  implements a `Commands[cmd]['Status']` nested dict keyed by qualifier
  parameters, a `Subscription` dict of callbacks, `WriteStatus` (writes and
  fires `NewStatus` only when the value actually changed,
  `mod_ross_matrix_RossTalk_v1_1_0_0.py:153-159`), `ReadStatus`, and
  `NewStatus` (fires **one** subscribed callback per command/qualifier slot —
  `Method['callback'] = callback`, `RossTalk:116-117`, overwriting any prior
  subscriber).
- `tools.py` reimplements the identical bookkeeping independently as
  `__ModuleSubscribeWrapper` (`tools.py:1521-1575`), except callbacks are
  stored as a **list** (`Method['callback'].append(callback)`,
  `tools.py:1566`), so multiple subscribers can share one slot. When a module
  is wrapped, `__fn_device_init` monkey-patches this version directly over
  the device module's own `SubscribeStatus`
  (`tools.py:1047-1048: self.device.SubscribeStatus =
  self.__subscriber.SubscribeStatus`), so in the wrapped configuration the
  device module's own single-callback implementation
  (`RossTalk:96-119`) never runs.

### 6. Polling
- Neither Ross device module defines a single `Update<Command>` method
  (`has_update_method` is `False` for all 7 commands across both files —
  confirmed by running `tools/wire_table.py dump` on both, see §b). There is
  no polling loop anywhere in the plugin tier for this device: all feedback
  is either unsolicited (TSL's binary push) or synthesized from the
  connection event (`ConnectionStatus`).
- `tools.py` does implement polling machinery elsewhere in the file for
  other wrapper classes (e.g. a `_Timer(5, self.__create_polling_timer())`
  pattern at `tools.py:5185-5186`, `5653-5655`) — outside the
  `__InterfaceWrapper` range read in full for this document, and not used by
  the Ross plugin.

### 7. Orchestration (the plugin's own job, per its docstring)
- `plugin_ross_ultrix.py:12-13` states its purpose: *"providing a
  translation layer between the main program and hardware module... Logic
  defined in this class should be only device specific from program
  generic."*
- It holds **three live device-module instances** for one physical device
  and hard-routes commands between them: `self.dev` (RossTalk, primary —
  `MatrixTieCommand`, `SalvoRecall`), `self.dev2` (TSL 3.1, feedback-only —
  `OutputTieStatus`), `self.dev3` (a second RossTalk instance — `LoadSet`,
  `CustomControl`) (`plugin_ross_ultrix.py:23-25`, `45-60`).
- It relays `dev`'s and `dev2`'s events up to the parent program
  (`self.p.event_switch_ConnectionStatus`, `self.p.event_switch_OutputTieStatus`,
  lines 28-43) and deliberately **suppresses** the analogous `dev2`/`dev3`
  connection-status events (`pass#...`, lines 34 and 38) rather than
  forwarding them — a connection-status aggregation policy that exists only
  at this layer.

### 8. Error handling / logging (host framework, not device-specific)
- `tools.py`'s replacement `Set`/`Update`/`NewStatus` wrappers
  (`tools.py:1166-1242`) and its own `Set`/`Update`/`ReadStatus`/
  `SubscribeStatus` (`1293-1346`) each catch and log exceptions via
  `DebugPrint.Print` and `_ProgramLog`, and report them to a telnet debug
  server (`class __InterfaceWrapper(DebugServer)`, `tools.py:1002`, and the
  print/log helpers at `1082-1101`). This is cross-cutting infrastructure,
  not something either Ross device module implements for itself — their own
  `Error`/`Discard` methods just `print()`
  (`mod_ross_matrix_RossTalk_v1_1_0_0.py:219-224`).
- Per finding 17 §5, the rest of `tools.py` (not re-read in full for this
  document) provides NVRAM JSON persistence with log rotation
  (`findings/17-how-a-human-writes-one.md:100`, citing `tools.py:161-590`)
  and the debug telnet server itself (`findings/17-how-a-human-writes-one.md:101`,
  citing `tools.py:644-1000`).

## (b) Responsibilities an IR would need to carry, mapped against `tools/wire_table.py`

**Already represented** in `tools/wire_table.py`'s normalised table
(`CommandRecord`/`Template`/`Response`, `tools/wire_table.py:507-567`):

1. Command names and declared parameter lists — from `self.Commands`
   (`tools/wire_table.py:795-817`, confirmed extracting `MatrixTieCommand`,
   `SalvoRecall`, `LoadSet`, `CustomControl`, `ConnectionStatus` from
   RossTalk and `ConnectionStatus`, `OutputTieStatus` from TSL 3.1).
2. Outgoing command-string templates with substitution slots, resolved
   symbolically from `Set<Command>` bodies (`tools/wire_table.py:670-728`).
   Confirmed correct for `SalvoRecall` (`'GPI {}\r\n'`), `LoadSet`
   (`'LOADSET {}\r\n'`), `CustomControl` (`'CC {}{}\r\n'`).
3. `has_set_method`/`has_update_method` existence flags
   (`tools/wire_table.py:533`, `541`) — correctly report `has_update_method:
   false` everywhere in both Ross modules, matching §a.6.
4. Response regex patterns from `AddMatchString`, when spelled
   `re.compile(...)` (an `ast.Attribute` call) — `tools/wire_table.py:731-780`.
5. Value maps sourced from a literal `ValueStateValues`-style dict on the
   Set side, or inverted from a Match handler's reverse map
   (`tools/wire_table.py:853-919`).
6. An opaque-marker count for anything the resolver can't statically pin
   down (`tools/wire_table.py:64-65`, `120-123`, etc.) — the honesty gauge
   finding 17 already relies on.

**Not represented** — each checked against the actual code, not assumed:

7. **Transport tier** (§a.1) — protocol kind, host/port/baud, auto-reconnect
   cadence, connect staggering. `extract_table` never inspects
   `Create_Device`, `__init__`'s interface args, the transport subclasses, or
   `plugin_ross_ultrix.py`'s `subscribe()` at all; its walk is limited to the
   `Commands` dict, `Set*`/`Update*` methods, and `AddMatchString` calls
   (`tools/wire_table.py:790-819`).
8. **Multi-instance/multi-module orchestration** (§a.7) — the plugin's
   3-instance, per-command routing is invisible in principle, because
   `extract_table` reads one source file and takes the file's *first*
   `ast.ClassDef` as "the" device (`tools/wire_table.py:593-597`,
   `790-793`). It has no model of "this logical device is really two
   protocol modules plus a routing plugin."
9. **Business-rule parameter shaping above the device module** (§a.3) —
   `plugin_ross_ultrix.py:47-53`'s `sw_type`→`Levels` mapping and the
   `output+53` offset happen in a file `wire_table.py` never reads (it is
   only ever pointed at a device module), so this transform is absent from
   any wire table built from the device module alone, with no marker that
   anything was skipped.
10. **Framing liveness** — `wire_table.py` records only the regex *pattern*
    text from `AddMatchString`; it has no way to notice that RossTalk's
    `__ReceiveData` returns before ever consulting the match-string dict
    (§a.2). More directly, TSL 3.1's response regex is **not extracted at
    all**: re-running `tools/wire_table.py dump` on
    `mod_ross_matrix_tsl_3_1_v1_1_0_0.py` returns
    `"match_strings_total": 0` (checked 2026-09-23). Root cause:
    `tools/wire_table.py:752-753` requires the `AddMatchString` pattern
    argument to be an `ast.Attribute` call (`re.compile(...)`), but TSL 3.1
    imports the bare name (`from re import compile, search`,
    `mod_ross_matrix_tsl_3_1_v1_1_0_0.py:2`) and calls `compile(rb'...')`
    directly (line 105) — an `ast.Name`, not `ast.Attribute` — so the check
    never matches. The entire response layer for `OutputTieStatus`,
    including the 130-entry `__input_names` decode table, is silently
    invisible to the oracle for this file. This is a translator-oracle gap
    found while producing this document, distinct from finding 17's claim
    (which only checked command *names*, not response fidelity).
11. **Conditional/branching command templates** — RossTalk's
    `SetMatrixTieCommand` (`mod_ross_matrix_RossTalk_v1_1_0_0.py:33-42`)
    builds `CmdString` inside an `if`/`else`. Re-running the dump on this
    file (checked 2026-09-23) shows `MatrixTieCommand`'s `set_templates`
    resolves to the single opaque slot `"OPAQUE:CmdString"` (`opaque: 1`)
    rather than either of the two real wire templates
    (`'XPT D:{} S:{} I:99 L:{}\x0d\x0a'` / `'XPT D:{} S:{} I:99\x0d\x0a'`).
    Root cause: `_find_helper_calls_in_method`'s branch walker
    (`tools/wire_table.py:630-637`) recurses into an `If`'s body/orelse with
    a *copy* of the environment and never merges the branch-local
    assignment back into the env used by the `__SetHelper` call that occurs
    after the `if`/`else` at the same level — so by the time the helper call
    is reached, `CmdString` isn't bound in the env the resolver sees. A
    second, real extraction gap found by exercising the tool on this file.
12. **State-store/pub-sub mechanics** (§a.5) — `WriteStatus`'s
    change-detection, and the single-callback-per-slot template versus
    `tools.py`'s list-based fan-out that actually wins at runtime once a
    module is wrapped — `wire_table.py` never reads `WriteStatus`/
    `NewStatus`/`Subscription` bodies.
13. **Polling cadence** (§a.6) — even where `Update<Command>` methods do
    exist elsewhere in this codebase, `wire_table.py`'s schema has no field
    for a polling interval or timer; `has_update_method` is presence-only.
14. **Error handling / retry / logging** (§a.8) — no concept in
    `CommandRecord`/`Template`/`Response` at all.
15. **Command pacing / synchronous send-and-wait / timeout values**
    (`tools.py:1254-1266`) — no field in the schema for send timing or
    synchronization semantics.

## (c) What the plugin tier does that neither format's model, as described in findings 04/05, is shown to express

- **Concurrent multi-instance command-splitting for one logical device.**
  `plugin_ross_ultrix.py` runs three simultaneous connections/module
  instances against what is, physically, one Ross Ultrix router, and
  hard-routes different commands to different instances (§a.7). Finding 05
  establishes that a `.pkp` **can** carry two protocol scripts for one
  device — the Samsung package holds both a serial driver and an
  Extron2.HTTPDriver-based ethernet driver as separate `StreamResourceAsset`
  objects (`findings/05-samsung-cross-vendor.md:52-56`) — but that is
  documented as an alternate-transport choice ("one device is genuinely N
  drivers, not one driver with N transport bindings," line 66-67), not as
  running multiple instances concurrently and splitting command traffic
  between them the way the Ross plugin does. Neither `findings/04` nor
  `findings/05` addresses this concurrent-instance shape directly — see open
  question in (d).
- **Arbitrary imperative business logic above the wire layer** —
  `plugin_ross_ultrix.py:47-53`'s string-matching and unit-offset arithmetic
  — is *not* a gap finding 04 is silent on. It is exactly the case finding 04
  already has an answer for: "Hand-written Extron code outside the
  `### BEGIN/END AUTO GENERATION` markers is the escape hatch: carry it in
  the IR as an opaque flagged node that the Crestron emitter reports as
  manual work, never silently dropped"
  (`findings/04-crestron-interop-verdict.md:102-104`). So this is expressible
  under the recommended hub-and-spoke design, but only as an *opaque*
  carried node, not as structured IR content — Crestron's rule-engine DSL
  (`findings/05-samsung-cross-vendor.md:79-98`, "Templates" +
  "Transformations" + "Rules") is data-driven and would need the same
  branches re-expressed as its own transform vocabulary to become structured
  rather than opaque, and nothing read for this document shows that
  vocabulary can express arbitrary Python control flow.

## (d) Open questions

1. Does Extron's `.pkp` model, or Crestron's `DriverDefinition`
   (`findings/04-crestron-interop-verdict.md:87-93`: "templates +
   transformations outgoing, decoder tree incoming, typed state controllers
   with polling policy, transport block, connector list"), support one
   logical device driven by more than one simultaneously-connected instance
   of the same or a different protocol module, with commands hard-routed
   between instances? Not checked in this session; findings 04 and 05 don't
   address it, and no `.pkp` or Crestron JSON file was opened while
   producing this document to check directly.
2. Would fixing the two `wire_table.py` gaps found here (§b.10's bare
   `compile()` miss, §b.11's if/else env-merge miss) change finding 17's
   headline command-overlap numbers, or only the fidelity of the templates
   already counted? Not measured — both gaps were found incidentally while
   re-running the tool for this document, not by design.
3. `tools.py`'s `__ModuleSubscribeWrapper` (`tools.py:1521-1575`) silently
   supersedes the device module's own single-callback `SubscribeStatus`
   (`mod_ross_matrix_RossTalk_v1_1_0_0.py:96-119`) whenever a module is
   wrapped via `__fn_device_init` (`tools.py:1047-1048`). Is the unwrapped,
   single-callback version ever what actually runs on the processor for this
   project, or is it always dead code once `tools.py` wraps it? Not
   verifiable from the four files read here — would need the higher-level
   `main_switch` program that isn't part of this sample set (it is only
   imported under `TYPE_CHECKING` in `plugin_ross_ultrix.py:1-3`).
4. Is RossTalk's dead `__ReceiveData` (§a.2,
   `mod_ross_matrix_RossTalk_v1_1_0_0.py:176-179`) a leftover bug from
   copying the newer template and then disabling it, or deliberate because
   RossTalk genuinely has no unsolicited feedback on this device and only
   TSL 3.1 is meant to carry status? Not established from the code alone —
   finding 17 §2 already notes the two modules were spliced from two
   different template vintages but doesn't address why RossTalk's copy of
   the newer template is switched off rather than removed.
5. None of the four plugin-tier files was ever executed against a real or
   simulated Ross Ultrix (finding 17's own "What this does NOT show" section,
   `findings/17-how-a-human-writes-one.md:149,154`, and unchanged by
   anything read for this document) — so every responsibility above is a
   *static-code* claim, not a confirmed runtime behavior.
