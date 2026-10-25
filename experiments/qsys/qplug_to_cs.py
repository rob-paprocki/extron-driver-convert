#!/usr/bin/env python3
"""
qplug_to_cs.py - Emit a ControlScript module from a BridgedModule.

The forward half of the Q-SYS -> Extron bridge. Takes a BridgedModule
(experiments/qsys/bridge_ir.py), produces a ControlScript module whose shape
matches the shipped vendor BT driver (corpus/.../atero_dsp_unBT2A_v1_0_0_0.py):

- a bare `class DeviceClass` carrying `self.Commands`, `self.Subscription`,
  `self.ReceiveData`, `self._ReceiveBuffer`, and `self.AddMatchString`;
- per command: `SetXxx(value, qualifier)` and/or `UpdateXxx(value, qualifier)`,
  each using `self.__SetHelper(name, cmdstring, value, qualifier)` or
  `self.__UpdateHelper(name, cmdstring, value, qualifier)`;
- per response: `__MatchXxx(match, tag)` that calls `self.WriteStatus(name, ...)`;
- the fixed helper footer (SetHelper, UpdateHelper, OnConnected, OnDisconnected,
  Set, Update, SubscribeStatus, NewStatus, ReceiveData, AddMatchString,
  CheckMatchedString) copied verbatim from atero_dsp_unBT2A;
- a `SerialOverEthernetClass` and `EthernetClass` connection mixin, selected
  by the plugin's declared transports.

What this does NOT do:

- Reply decoding is stubbed: __MatchXxx calls WriteStatus with
  match.group(1).decode() if the regex has a group, else the whole match. The
  vendor Extron module decodes with ValueStateValues maps that the Q-SYS
  plugin's Lua if/else chain does not surface. The generated handler is
  explicitly marked `# TODO: decode group -> status value` so a human can
  finish it.
- Multicast UDP receive is not reachable from extronlib.EthernetClientInterface
  (unicast only, no documented JoinMulticast). The generated module's docstring
  calls this out; outbound control works, status feedback over multicast does
  not. The user asked us to proceed under this limitation.
- Opaque templates (where the plugin builds its send string in a way the
  reader could not resolve) are dropped at the IR layer with a note. We do
  not guess.

Standard library only.
"""
from __future__ import annotations

import os
import re
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from bridge_ir import BridgedCommand, BridgedModule, BridgedResponse, BridgedTemplate  # noqa: E402


# ---------------------------------------------------------------------------
# Python-identifier derivation
# ---------------------------------------------------------------------------

_PY_IDENT_RE = re.compile(r"[^A-Za-z0-9_]")


def _py_identifier(raw: str) -> str:
    """Fold any string into a Python identifier."""
    s = _PY_IDENT_RE.sub("_", raw).strip("_")
    if not s:
        return "Anon"
    if s[0].isdigit():
        s = "_" + s
    # Capitalise the first letter so method names are PascalSet/PascalUpdate.
    return s[0].upper() + s[1:]


# ---------------------------------------------------------------------------
# Template -> Python expression
# ---------------------------------------------------------------------------

def _text_literal_to_pysrc(canonical: str) -> str:
    """Render a Python string literal from a wire-table text template.

    'SARMC {}\\r'  -> "'SARMC {}\\r'.format(value)"-ish body - the caller
    supplies the right slot source. This function returns the quoted,
    control-byte-escaped literal and nothing else.
    """
    # Python repr(str) handles \r \n \t ... but prefers " vs ' inconsistently.
    # Normalise to single quotes with escaped specials.
    escaped = (canonical
               .replace("\\", "\\\\")
               .replace("'", "\\'")
               .replace("\r", "\\r")
               .replace("\n", "\\n")
               .replace("\t", "\\t"))
    return "'" + escaped + "'"


def _bytes_literal_to_pysrc(canonical: str) -> str:
    """A bytes template rendered as a Python bytes literal.

    'CM 01 10' -> b'CM\\x01\\x10'. '?? slots' are not resolved here (that is a
    caller concern); any '??' in the canonical appears as \\x00.
    """
    parts = canonical.split(" ")
    chars = []
    for p in parts:
        if p == "??":
            chars.append("\\x00")
        else:
            try:
                b = int(p, 16)
            except ValueError:
                return "b''"
            if 0x20 <= b < 0x7F and b not in (ord("'"), ord("\\")):
                chars.append(chr(b))
            else:
                chars.append("\\x%02X" % b)
    return "b'" + "".join(chars) + "'"


def _bytes_template_to_pysrc_slotted(canonical: str, value_src: str) -> tuple[str, int]:
    """Render a bytes template that has '??' slot bytes as a runtime
    bytes-concat expression:

    'CB 0B ??' + value -> b'CB\\x0B' + bytes([int(value) & 0xFF])

    Multi-slot bytes templates get the last slot from value_src and earlier
    slots from a qualifier dict (keys 'Slot1'..'SlotN').
    Returns (python expr, slot_count).
    """
    parts = canonical.split(" ")
    pieces = []            # alternating bytes-literal pieces and slot exprs
    run = []               # pending printable/escaped chars for a literal
    slot_count = 0

    def flush_run():
        if run:
            pieces.append("b'" + "".join(run) + "'")
            run.clear()

    unknown_positions = [i for i, p in enumerate(parts) if p == "??"]
    for p in parts:
        if p == "??":
            flush_run()
            slot_count += 1
            # Pick the slot source
            if slot_count < len(unknown_positions):
                piece = "bytes([int(qualifier.get('Slot%d', 0)) & 0xFF])" % slot_count
            else:
                piece = "bytes([int(%s) & 0xFF])" % value_src
            pieces.append(piece)
        else:
            try:
                b = int(p, 16)
            except ValueError:
                return "b''", 0
            if 0x20 <= b < 0x7F and b not in (ord("'"), ord("\\")):
                run.append(chr(b))
            else:
                run.append("\\x%02X" % b)
    flush_run()
    if not pieces:
        return "b''", 0
    return " + ".join(pieces), slot_count


def _emit_cmd_expr(t: BridgedTemplate, value_src: str) -> tuple[str, bool, int]:
    """Return (python expression, uses_value, slot_count).

    - If the template has no slots, the expression is a literal; uses_value is False.
    - If one slot, the expression substitutes value_src; uses_value is True.
    - If more than one slot, the expression substitutes value_src for the last
      and takes earlier slots from a `qualifier` dict (keys 'Slot1', 'Slot2', ...).
      This is syntactically valid and honest about what is NOT known - a Lua
      plugin's loop-driven multi-slot sends do not surface a stable parameter
      naming the reader could capture. slot_count is the real placeholder count.
    """
    if t.kind == "bytes":
        if "??" in t.canonical:
            expr, n = _bytes_template_to_pysrc_slotted(t.canonical, value_src)
            return expr, n > 0, n
        lit = _bytes_literal_to_pysrc(t.canonical)
        return lit, False, 0
    lit = _text_literal_to_pysrc(t.canonical)
    placeholders = t.canonical.count("{}")
    escaped = (t.canonical.count("{{") + t.canonical.count("}}"))
    real = placeholders - escaped
    if real <= 0:
        return lit, False, 0
    if real == 1:
        return "%s.format(%s)" % (lit, value_src), True, 1
    # Multiple slots: last from value, earlier from qualifier['SlotN']
    args = []
    for i in range(real - 1):
        args.append("qualifier.get('Slot%d', '')" % (i + 1))
    args.append(value_src)
    return "%s.format(%s)" % (lit, ", ".join(args)), True, real


# ---------------------------------------------------------------------------
# Response pattern translation (Lua -> Python regex, best-effort)
# ---------------------------------------------------------------------------

# Lua pattern character classes we can map directly.
_LUA_TO_PY_CLASS = {
    "%a": "[A-Za-z]", "%A": "[^A-Za-z]",
    "%d": r"\d", "%D": r"\D",
    "%s": r"\s", "%S": r"\S",
    "%w": r"\w", "%W": r"\W",
    "%l": "[a-z]", "%L": "[^a-z]",
    "%u": "[A-Z]", "%U": "[^A-Z]",
    "%p": r"[\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]",
    "%P": r"[^\x21-\x2f\x3a-\x40\x5b-\x60\x7b-\x7e]",
    "%%": "%",
}


def _lua_pattern_to_py(pat: str) -> str:
    """Translate a Lua pattern (as used by the Q-SYS plugin) into a Python
    regex. Best-effort: `*` -> `*`, `+` -> `+`, `-` -> `*?`, `?` -> `?`,
    character classes mapped above. Returns the result with no bytes marker.
    """
    out = []
    i = 0
    while i < len(pat):
        c = pat[i]
        if c == "%" and i + 1 < len(pat):
            key = pat[i:i + 2]
            if key in _LUA_TO_PY_CLASS:
                out.append(_LUA_TO_PY_CLASS[key])
                i += 2
                continue
            # Literal escape of a punctuation char
            out.append(re.escape(pat[i + 1]))
            i += 2
            continue
        if c == "-":
            # Lua '-' is non-greedy '*', unless at start/end of a class
            out.append("*?")
            i += 1
            continue
        if c in "().|?+*^$.":
            # Lua '.' is a wildcard too, like Python's '.'; keep it passthrough.
            out.append(c)
            i += 1
            continue
        # Pass printable, benign chars through verbatim. re.escape() would
        # drop a backslash in front of e.g. ' ' which is harmless but noisy.
        if c.isalnum() or c in " \r\n\t=-/,:;!":
            out.append(c)
            i += 1
            continue
        out.append(re.escape(c))
        i += 1
    return "".join(out)


# ---------------------------------------------------------------------------
# Fixed footer (verbatim ControlScript helpers)
# ---------------------------------------------------------------------------

_FOOTER = '''
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False
            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')

    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            if qualifier:
                for Parameter in Command.get('Parameters', []):
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
            Method['callback'] = callback
            Method['qualifier'] = qualifier

    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands.setdefault(command, {'Status': {}})
        Status = Command['Status']
        if qualifier:
            for Parameter in Command.get('Parameters', []):
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return
        Status['Live'] = value

    def __ReceiveData(self, interface, data):
        self._ReceiveBuffer += data
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True
'''

_CONNECTION_CLASSES = {
    "udp": '''
class EthernetClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
''',
    "tcp": '''
class EthernetClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
''',
    "serial": '''
class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
''',
}


# ---------------------------------------------------------------------------
# Head/__init__/method emitters
# ---------------------------------------------------------------------------

def _plugin_banner(bm: BridgedModule) -> list:
    pl = bm.plugin or {}
    name = pl.get("Name") or "<unknown>"
    manuf = pl.get("Manufacturer") or "<unknown>"
    model = pl.get("Model") or ""
    version = pl.get("Version") or ""
    desc = pl.get("Description") or ""
    out = [
        '"""',
        'Generated by experiments/qsys/qplug_to_cs.py from the Q-SYS plugin:',
        '  manufacturer: %s' % manuf,
        '  name:         %s' % name,
    ]
    if model:
        out.append('  model:        %s' % model)
    if version:
        out.append('  version:      %s' % version)
    if desc:
        out.append('  description:  %s' % desc)
    out.append('')
    out.append('Transports: %s' % ", ".join(bm.transports))
    out.append('')
    if bm.notes:
        out.append('Reader notes:')
        for n in bm.notes:
            out.append('  - %s' % n)
        out.append('')
    out.append('Known gaps in the generated module:')
    out.append('  - __Match handlers decode reply groups as raw .decode(); the plugin')
    out.append('    used a Lua if/else chain to map replies into user-facing values,')
    out.append('    and that lookup was not reconstructed here. Each handler is marked')
    out.append('    with a `# TODO: decode group -> status value` comment.')
    if "udp" in bm.transports:
        out.append('  - RDL-class plugins sometimes rely on UDP multicast to receive')
        out.append('    device-pushed status (e.g. 239.254.50.0:9000). extronlib.')
        out.append('    EthernetClientInterface is unicast-only; status feedback over')
        out.append('    multicast does not work from this module as-is. Outbound control')
        out.append('    on the unicast send port is unaffected.')
    out.append('"""')
    return out


def _emit_header(bm: BridgedModule) -> str:
    imports = ["from extronlib.interface import EthernetClientInterface",
               "import re"]
    if "serial" in bm.transports:
        imports[0] = "from extronlib.interface import SerialInterface, EthernetClientInterface"
    out = _plugin_banner(bm) + imports + [""]
    return "\n".join(out) + "\n\n"


def _emit_init(bm: BridgedModule) -> str:
    cmd_names = ["ConnectionStatus"] + sorted(bm.commands.keys())
    lines = [
        "    def __init__(self):",
        "        self.Unidirectional = 'False'",
        "        self.connectionCounter = 15",
        "        self.DefaultResponseTimeout = 0.3",
        "        self._compile_list = {}",
        "        self.Subscription = {}",
        "        self.ReceiveData = self.__ReceiveData",
        "        self._ReceiveBuffer = b''",
        "        self.counter = 0",
        "        self.connectionFlag = True",
        "        self.initializationChk = True",
        "        self.Debug = False",
        "        self.Models = {}",
        "",
        "        self.Commands = {",
    ]
    for name in cmd_names:
        py = _py_identifier(name)
        lines.append("            '%s': {'Status': {}}," % py)
    lines.append("        }")
    # AddMatchString block
    responses = []
    for name, cmd in bm.commands.items():
        for resp in cmd.responses:
            responses.append((name, resp))
    if responses:
        lines.append("")
        lines.append("        if self.Unidirectional == 'False':")
        for name, resp in responses:
            py = _py_identifier(name)
            py_pat = _lua_pattern_to_py(resp.pattern)
            lines.append("            self.AddMatchString(re.compile(b'%s'), self.__Match%s, None)" %
                         (py_pat.replace("'", "\\'"), py))
    lines.append("")
    return "\n".join(lines) + "\n"


def _emit_set(cmd: BridgedCommand) -> str:
    py = _py_identifier(cmd.name)
    tmpl = cmd.set_templates[0]  # first-template-wins for the first cut
    expr, uses_value, slot_count = _emit_cmd_expr(tmpl, "value")
    lines = [
        "    def Set%s(self, value, qualifier):" % py,
        "        cmdstring = %s" % expr,
        "        self.__SetHelper('%s', cmdstring, value, qualifier)" % py,
        "",
    ]
    if slot_count > 1:
        # The body reads qualifier.get('Slot1')..['SlotN']. Caller may pass
        # qualifier=None; without this guard we raise AttributeError at runtime
        # (Finding 14: wire-correct but runtime-broken; exec_harness caught it).
        lines.insert(1, "        if qualifier is None: qualifier = {}")
        lines.insert(2, "        # TODO: this command has %d slots; earlier ones are drawn from" % slot_count)
        lines.insert(3, "        # qualifier['Slot1']..['Slot%d'], last is value. Rename these to the" % (slot_count - 1))
        lines.insert(4, "        # device's actual parameter names once you know them.")
    if len(cmd.set_templates) > 1:
        more = [t.canonical for t in cmd.set_templates[1:]]
        lines.insert(1, "        # Additional templates seen for this command (not emitted): %r" % more)
    if not uses_value and tmpl.kind == "bytes" and "??" in tmpl.canonical:
        lines.insert(2, "        # TODO: substitute slot bytes (??) with value-derived byte(s)")
    return "\n".join(lines) + "\n"


def _emit_update(cmd: BridgedCommand) -> str:
    py = _py_identifier(cmd.name)
    tmpl = cmd.update_templates[0]
    expr, _, slot_count = _emit_cmd_expr(tmpl, "value")
    lines = [
        "    def Update%s(self, value, qualifier):" % py,
        "        cmdstring = %s" % expr,
        "        self.__UpdateHelper('%s', cmdstring, value, qualifier)" % py,
        "",
    ]
    if slot_count > 1:
        # Same qualifier=None guard as _emit_set; the body reads qualifier.get.
        lines.insert(1, "        if qualifier is None: qualifier = {}")
        lines.insert(2, "        # TODO: this command has %d slots; earlier ones are drawn from" % slot_count)
        lines.insert(3, "        # qualifier['Slot1']..['Slot%d'], last is value." % (slot_count - 1))
    if len(cmd.update_templates) > 1:
        more = [t.canonical for t in cmd.update_templates[1:]]
        lines.insert(1, "        # Additional templates seen for this command (not emitted): %r" % more)
    return "\n".join(lines) + "\n"


def _emit_match(cmd: BridgedCommand, resp: BridgedResponse) -> str:
    py = _py_identifier(cmd.name)
    has_group = "(" in resp.pattern
    lines = [
        "    def __Match%s(self, match, tag):" % py,
    ]
    if has_group:
        lines.append("        # TODO: decode group -> status value (vendor plugin used a Lua if/else chain)")
        lines.append("        try:")
        lines.append("            value = match.group(1).decode()")
        lines.append("        except (IndexError, UnicodeDecodeError):")
        lines.append("            value = ''")
    else:
        lines.append("        value = 'OK'")
    lines.append("        self.WriteStatus('%s', value, None)" % py)
    lines.append("")
    return "\n".join(lines) + "\n"


def _emit_connection_classes(bm: BridgedModule) -> str:
    out = []
    chosen = []
    if "udp" in bm.transports:
        chosen.append("udp")
    elif "tcp" in bm.transports:
        chosen.append("tcp")
    if "serial" in bm.transports:
        chosen.append("serial")
    if not chosen:
        # Default to a TCP ethernet class so the file is loadable
        chosen = ["tcp"]
    for t in chosen:
        out.append(_CONNECTION_CLASSES[t])
    return "".join(out)


def _rename_colliding(module: BridgedModule) -> BridgedModule:
    """Walk the module's commands and rename any whose Python identifiers would
    collide. Non-ASCII characters, wire-token glyphs like '%' and '{', and bare
    opcode bytes all fold to '_' in _py_identifier, so e.g. '%1CLSS' and
    '{}%1CLSS ?\\r' both become '_1CLSS'. The IR picks one of them; the loser
    gets a numeric suffix in the IR itself so AddMatchString, SetXxx, UpdateXxx
    and __MatchXxx stay internally consistent. In-place.
    """
    seen: dict = {}       # python ident -> original name
    renames: dict = {}    # original name -> new name
    for name in sorted(module.commands.keys()):
        py = _py_identifier(name)
        if py not in seen:
            seen[py] = name
            continue
        # Collision: find a free suffix
        idx = 2
        while True:
            new_name = "%s_%d" % (name, idx)
            new_py = _py_identifier(new_name)
            if new_py not in seen:
                seen[new_py] = new_name
                renames[name] = new_name
                break
            idx += 1
    for old, new in renames.items():
        cmd = module.commands.pop(old)
        cmd.name = new
        module.commands[new] = cmd
    return module


def emit(module: BridgedModule) -> str:
    """Emit the ControlScript module source for a BridgedModule."""
    module = _rename_colliding(module)
    parts = [_emit_header(module), "class DeviceClass:\n", _emit_init(module)]
    emitted_matches = set()        # (command_name) - only one __MatchXxx per command
    for name in sorted(module.commands.keys()):
        cmd = module.commands[name]
        if cmd.set_templates:
            parts.append(_emit_set(cmd))
        if cmd.update_templates:
            parts.append(_emit_update(cmd))
        for resp in cmd.responses:
            key = _py_identifier(cmd.name)
            if key in emitted_matches:
                continue
            emitted_matches.add(key)
            parts.append(_emit_match(cmd, resp))
    parts.append(_FOOTER)
    parts.append(_emit_connection_classes(module))
    return "".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv=None):
    import argparse
    from qplug_wire import extract
    from bridge_ir import from_qwire

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plugin", help="path to a .qplug file")
    ap.add_argument("-o", "--output", help="write to this path (default: stdout)")
    args = ap.parse_args(argv)

    with open(args.plugin, "r", encoding="utf-8") as f:
        src = f.read()
    qwire = extract(src, args.plugin)
    bm = from_qwire(qwire)
    out = emit(bm)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    _main()
