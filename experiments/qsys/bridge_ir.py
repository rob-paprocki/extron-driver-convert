#!/usr/bin/env python3
"""
bridge_ir.py - a thin Command/Response IR between the Q-SYS reader and the
ControlScript emitter.

A Q-SYS plugin's wire table (qplug_wire.QWireTable) and an Extron module's
wire table (tools/wire_table.WireTable) are already deliberately mirror-matched
in shape, but the shared boundary isn't formalised in a single module. This
file is that boundary: dataclasses that both the emitter and the diff oracle
can consume without caring which end they came from, and `from_qwire()` which
builds one from a QWireTable.

What this does NOT do:

- It does not infer vendor-authored command names. Command names here are
  derived from the wire prefix (e.g. the plugin's SARMC/GARMC send sites both
  become a command called "ARMC"). Vendor Extron modules name commands
  editorially (e.g. the Clock Audio module names ARMC's cousins "LEDLightControl",
  "PhantomPower"), and that choice can't be reconstructed from the wire. The
  acceptance criterion is wire-byte equivalence, not name parity.

- It does not synthesise reply-handler logic. A BridgedResponse carries the
  regex pattern verbatim; the emitter is responsible for the WriteStatus call,
  with a value-map lookup if the plugin's reply parser used one.

- It does not touch opaque slots. These are counted and reported, never guessed.

Standard library only.
"""
from __future__ import annotations

import os
import re
import sys
from dataclasses import dataclass, field
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from qplug_wire import QWireTable, SendSite, Template  # noqa: E402


# ---------------------------------------------------------------------------
# The IR
# ---------------------------------------------------------------------------

@dataclass
class BridgedTemplate:
    kind: str                 # 'text' | 'bytes'
    canonical: str            # with '{}' for each slot (wire_table shape)
    typed: str = ""           # with '{#}' where the slot is numeric
    slots: list = field(default_factory=list)   # slot descriptions, for traceability
    label: str = ""           # the plugin-side label that produced this template
    opaque: int = 0           # count of opaque slots inside this template


@dataclass
class BridgedResponse:
    pattern: str              # regex pattern string (not compiled)
    is_bytes: bool            # whether to compile with b'...' in the emitted module
    handler: str              # the command name the match should feed back into
    line: int = 0             # line in the plugin, for traceability
    source_function: str = "" # the plugin's receive function


@dataclass
class BridgedCommand:
    name: str                                # 'ARMC', 'PhantomPower', ...
    parameters: list = field(default_factory=list)  # qualifier parameter names (empty for simple)
    set_templates: list = field(default_factory=list)     # list of BridgedTemplate
    update_templates: list = field(default_factory=list)  # list of BridgedTemplate
    responses: list = field(default_factory=list)          # list of BridgedResponse
    value_map: dict = field(default_factory=dict)          # user_value -> wire_value


@dataclass
class BridgedModule:
    plugin: dict                              # Name, Manufacturer, Model, Version, Author, Description
    transports: list = field(default_factory=list)  # ['udp'] / ['tcp'] / ...
    commands: dict = field(default_factory=dict)    # name -> BridgedCommand
    notes: list = field(default_factory=list)       # opaque templates, dropped sites, etc


# ---------------------------------------------------------------------------
# QWireTable -> BridgedModule
# ---------------------------------------------------------------------------

# Labels that mean "this is Update traffic, not Set traffic". Case-insensitive
# substring match on the label the reader attached to the template.
_UPDATE_LABEL_HINTS = ("poll", "init", "query", "status", "update", "subscribe")

_MIN_PAIR_TAIL = 3   # S<X>/G<X> are only merged when X is this long or more


def _first_token(canonical: str) -> str:
    """
    The first literal token of a wire template, with slots and trailing control
    bytes dropped. 'SARMC {}\\r' -> 'SARMC'; 'ACK BTS {}\\r' -> 'ACK'; '43 4D 01 10'
    (bytes) -> the first byte hex.
    """
    s = canonical.lstrip()
    # Bytes templates: first byte is the opcode (keep up to two bytes if both printable
    # letters -- 'CM', 'CB', 'QD' are the RDL verb families)
    if re.match(r"^[0-9A-F]{2}( |$)", s):
        parts = s.split(" ")
        try:
            b1 = bytes([int(parts[0], 16)]).decode("ascii")
            if len(parts) >= 2 and re.match(r"^[0-9A-F]{2}$", parts[1]):
                b2 = bytes([int(parts[1], 16)]).decode("ascii")
                if b1.isalpha() and b2.isalpha():
                    return b1 + b2
            if b1.isalpha():
                return b1
        except (UnicodeDecodeError, ValueError):
            pass
        return parts[0]
    # Text templates: pull everything up to the first space, '(', '{', or control byte
    m = re.match(r"[^\s({\r\n]+", s)
    return m.group(0) if m else s


# A label like 'Controls.BTConnect.EventHandler' or 'BTConnect.EventHandler'
# yields 'BTConnect'. 'Controls[].EventHandler' yields '' (anonymous array).
_LABEL_HANDLER_RE = re.compile(r"^(?:Controls\.)?([A-Za-z][A-Za-z0-9_]*)\.EventHandler$")


def _name_from_label(label: str) -> str:
    """Return a usable command name derived from a template label, or ''."""
    if not label:
        return ""
    m = _LABEL_HANDLER_RE.match(label)
    if m:
        return m.group(1)
    return ""


def _derive_name(template: BridgedTemplate) -> str:
    """
    Reduce a template to a command key.

    Preferred source: the plugin control name the template's EventHandler sits
    on (reader attaches labels like 'Controls.BTConnect.EventHandler'). This
    matches the vendor's own naming intent much more closely than the wire
    prefix does on byte-level protocols.

    Fallback: the first wire token. S/G pair merging in _merge_sg_pairs()
    handles the Clock-Audio-style 'SARMC'/'GARMC' case afterwards.
    """
    from_label = _name_from_label(template.label)
    if from_label:
        return from_label
    return _first_token(template.canonical)


def _merge_sg_pairs(commands: dict) -> dict:
    """
    Merge command buckets that look like Set/Get pairs sharing a verb tail,
    e.g. {'SARMC': ..., 'GARMC': ...} -> {'ARMC': merged}. Only merges when the
    tail is at least _MIN_PAIR_TAIL chars so 'SAVE'/'GAVE' don't fuse (there is
    no 'GAVE'; this check keeps 'SAVE' alone when nothing with the matching
    tail exists). An S bucket with no G twin stays as 'SAVE'; a G bucket with
    no S twin stays as 'GARMC'. Idempotent.
    """
    s_keys = {k[1:]: k for k in commands if k.startswith("S") and len(k) > _MIN_PAIR_TAIL + 1}
    g_keys = {k[1:]: k for k in commands if k.startswith("G") and len(k) > _MIN_PAIR_TAIL + 1}
    shared = set(s_keys) & set(g_keys)
    if not shared:
        return commands
    out = {k: v for k, v in commands.items() if k not in {s_keys[t] for t in shared}
                                           and k not in {g_keys[t] for t in shared}}
    for tail in sorted(shared):
        s_bucket = commands[s_keys[tail]]
        g_bucket = commands[g_keys[tail]]
        merged = BridgedCommand(name=tail)
        merged.set_templates.extend(s_bucket.set_templates + g_bucket.set_templates)
        merged.update_templates.extend(s_bucket.update_templates + g_bucket.update_templates)
        merged.responses.extend(s_bucket.responses + g_bucket.responses)
        if tail not in out:
            out[tail] = merged
        else:
            # The user already had a bucket for the bare tail (unusual): collapse.
            dst = out[tail]
            dst.set_templates.extend(merged.set_templates)
            dst.update_templates.extend(merged.update_templates)
            dst.responses.extend(merged.responses)
    return out


def _is_update(template: BridgedTemplate) -> bool:
    """Heuristic: does this template look like a Get, not a Set?"""
    low = template.label.lower()
    if any(h in low for h in _UPDATE_LABEL_HINTS):
        return True
    # Short template with no slots and no space-after-first-token: looks like a Get
    tok = _first_token(template.canonical)
    rest = template.canonical[len(tok):]
    # 'GARMC\r' - no params - likely Update
    if not template.slots and rest.rstrip("\r\n ") == "":
        # First-token prefix hints: starts with G/Q/R and the rest looks like a verb
        if tok and tok[0] in "GQR":
            return True
    return False


def _bridged_template(t: Template) -> BridgedTemplate:
    return BridgedTemplate(
        kind=t.kind,
        canonical=t.canonical,
        typed=t.typed or t.canonical,
        slots=list(t.slots or []),
        label=t.label or "",
        opaque=t.opaque or 0,
    )


def _bridged_response(resp: dict, commands: dict) -> BridgedResponse:
    """
    Build a BridgedResponse and try to attach it to a command by regex-prefix
    match (ACK, or the first literal word of the pattern that matches one of
    our derived command names).
    """
    pat = resp.get("pattern") or resp.get("equals") or ""
    is_bytes = any(ord(c) > 127 for c in pat)
    # Try to match a command by the first all-caps word that appears in the
    # pattern. 'ACK BTN ([\s\S]*)\r' -> BTN; 'ACK GARMC (0|1)\r' -> ARMC
    # First, drop an 'ACK ' prefix if present.
    probe = pat
    if probe.startswith("ACK "):
        probe = probe[4:]
    # Find the first literal token
    m = re.match(r"[^\s(\\{]+", probe)
    handler = ""
    if m:
        tok = m.group(0)
        if tok in commands:
            handler = tok
        else:
            # Try S/G-stripped form (plugin reply 'GARMC ...' -> command 'ARMC')
            for p in ("S", "G"):
                if tok.startswith(p) and len(tok) > _MIN_PAIR_TAIL + 1:
                    tail = tok[1:]
                    if tail in commands:
                        handler = tail
                        break
    return BridgedResponse(
        pattern=pat,
        is_bytes=is_bytes,
        handler=handler,
        line=resp.get("line", 0),
        source_function=resp.get("function", ""),
    )


_UNINFORMATIVE_NAMES = ("", "Anon")


def _group_sends(qwire: QWireTable) -> dict:
    """
    Group a QWireTable's templates into named command buckets.

    Keyed on the derived name; each bucket collects Set-style and Update-style
    templates separately. Templates whose derived name is uninformative (empty
    label and a shared opcode across many sites) are given a numbered name
    like 'Anon1', 'Anon2' so they do not collapse into one.
    """
    buckets: dict = {}
    anon_counter = 0
    for send in qwire.sends:
        for t in send.templates:
            if t.opaque > 0 and not t.slots:
                # Fully opaque template: nothing addressable to emit
                continue
            bt = _bridged_template(t)
            name = _derive_name(bt)
            # If the derived name has already been used AND the two templates
            # are different wire bytes, split with a numbered suffix. Same
            # bucket as another template with the same name is fine - that is
            # how we group e.g. a Set + its Update into one command.
            if name in buckets:
                existing = buckets[name]
                already_here = set((x.kind, x.canonical) for x in existing.set_templates + existing.update_templates)
                if (bt.kind, bt.canonical) not in already_here and (not name or name in _UNINFORMATIVE_NAMES):
                    anon_counter += 1
                    name = "%s%d" % (name or "Anon", anon_counter)
            cmd = buckets.setdefault(name, BridgedCommand(name=name))
            if _is_update(bt):
                cmd.update_templates.append(bt)
            else:
                cmd.set_templates.append(bt)
    return buckets


def from_qwire(qwire: QWireTable) -> BridgedModule:
    """Build a BridgedModule from a parsed Q-SYS plugin wire table."""
    plugin = dict(qwire.plugin or {})
    transports = sorted(qwire.stats.get("transports", []))
    commands = _group_sends(qwire)
    commands = _merge_sg_pairs(commands)

    # Dedupe templates in each bucket (same canonical appearing from two sites)
    for cmd in commands.values():
        seen = set()
        unique = []
        for t in cmd.set_templates:
            key = (t.kind, t.canonical)
            if key not in seen:
                seen.add(key)
                unique.append(t)
        cmd.set_templates = unique
        seen = set()
        unique = []
        for t in cmd.update_templates:
            key = (t.kind, t.canonical)
            if key not in seen:
                seen.add(key)
                unique.append(t)
        cmd.update_templates = unique

    # Attach responses, deduped by (handler, pattern) so the same equals-match
    # appearing from two if-branches in the plugin's parse function doesn't
    # become two identical AddMatchString calls (and therefore two identical
    # __MatchXxx methods, which Python would silently collapse).
    seen_resp = set()
    for resp in qwire.responses:
        br = _bridged_response(resp, commands)
        if not br.handler or br.handler not in commands:
            continue
        key = (br.handler, br.pattern)
        if key in seen_resp:
            continue
        seen_resp.add(key)
        commands[br.handler].responses.append(br)

    notes = list(qwire.notes or [])
    # Count the opaque drops so the generated module can carry a header note
    opaque_sites = sum(1 for s in qwire.sends for t in s.templates if t.opaque > 0 and not t.slots)
    if opaque_sites:
        notes.append("%d opaque send template(s) dropped (nothing addressable to emit)" % opaque_sites)

    return BridgedModule(
        plugin=plugin,
        transports=transports,
        commands=commands,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _main(argv=None):
    import argparse
    import json
    from dataclasses import asdict
    from qplug_wire import extract

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plugin", help="path to a .qplug file")
    args = ap.parse_args(argv)

    with open(args.plugin, "r", encoding="utf-8") as f:
        src = f.read()
    qwire = extract(src, args.plugin)
    bm = from_qwire(qwire)
    out = {
        "plugin": bm.plugin,
        "transports": bm.transports,
        "commands": {k: asdict(v) for k, v in bm.commands.items()},
        "notes": bm.notes,
    }
    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    _main()
