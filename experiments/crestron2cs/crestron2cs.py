#!/usr/bin/env python3
"""
crestron2cs.py -- EXPERIMENT q1b-crestron-to-controlscript.

Translates a Crestron "LegacyWrappers" JSON-engine .pkg driver (a fully
declarative rule-engine DSL -- Templates, Transformations, Rules, Responses)
into an Extron ControlScript module, in the GC-runtime `Extron2.HTTPDriver`
dialect (the dialect the Samsung QNxxLS03DAFXZA .pkp's own ethernet embedded
script uses -- see samples/.../pkp/smsg_10_6738_v1_0_0.pkp,
"smsg_10_6738_ethernet.py"). That dialect is chosen deliberately: it is the
dialect wire_table.py resolves with the least ambiguity (self.__SetHelper /
self.__UpdateHelper with an explicit `data = {...}` dict literal), and it is
literally what a from-scratch Extron author would write for this same wire
protocol, which makes the diff meaningful.

ALGORITHM (bottom-up template resolution, per findings/05):
  1. Every Commands[] entry is either a leaf ("Text"/"WakeOnLan") or a
     "Template" that points at a base command via Info.CommandName and
     supplies Values overrides for the base's `{token}` slots.
  2. Resolve bottom-up: fully resolve the base FIRST, then substitute this
     level's Values into the base's already-resolved text. Anything not
     overridden bubbles up unresolved -- these become the terminal wire
     slots (AccessToken, _CommandId_, Channel, ...).
  3. `{{` / `}}` are literal-brace escapes (collapse to one brace) and must
     never be confused with a `{name}` substitution token -- see
     `_collapse_doubled_braces` for the exact rule, self-consistency-tested
     by requiring every fully-substituted (dummy-filled) template to parse
     as valid JSON.
  4. Transformations declared ANYWHERE in a command's CommandName ancestor
     chain apply to it (a Transformation on an intermediate base, e.g.
     SetAntennaTemplate, still applies to every child that inherits it).
  5. This translator is deliberately literal to CRESTRON's OWN naming and
     value domains (e.g. boolean maps keyed 'true'/'false', not Extron's
     'On'/'Off') -- it does NOT peek at Extron's shipped script to inflate
     the eventual wire-table match count. Any resemblance to Extron's code
     is because the underlying protocol actually is the same, which is
     exactly the thing being measured.

Fails loudly (raises CrestronTemplateError, or records a SkippedCommand with
a reason) rather than guessing, per project rules.

Usage:
    python3 crestron2cs.py <path-to.pkg> -o <output.py> [--report report.json]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field

_HERE = os.path.dirname(os.path.abspath(__file__))
_TOOLS_DIR = os.path.normpath(os.path.join(_HERE, "..", "..", "tools"))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

import pkg_dump  # noqa: E402


class CrestronTemplateError(Exception):
    """Raised when a Commands[] entry cannot be resolved without guessing."""


# ---------------------------------------------------------------------------
# Step 1: template-text resolution (bottom-up substitution)
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"\{(\w+)\}")
# A single combined, left-to-right, non-overlapping scan: at every `{`/`}`
# position, prefer a genuine `{identifier}` substitution token (leave it
# untouched -- it is resolved by a later pass) over collapsing a literal
# `{{`/`}}` escape pair. This is NOT the same as two independent
# str.replace("{{", ...) / str.replace("}}", ...) passes: those are
# ambiguous when a token's own closing `}` sits directly against a literal
# object-closing `}` (e.g. RpcRequest's "...{params}},\"id\"..." -- the
# `}` that ends the `{params}` token is immediately followed by the LITERAL
# `}` that closes the "params" JSON object; a naive `.replace("}}", "}")`
# corrupts the token itself). Regex alternation tries `\{(\w+)\}` first at
# each starting position, so it always claims a real token before `{{`/`}}`
# get a chance to (mis)match across a token boundary.
_BRACE_SCAN_RE = re.compile(r"\{(\w+)\}|\{\{|\}\}")


def _collapse_doubled_braces(text: str) -> str:
    def _sub(m):
        if m.group(1) is not None:
            return m.group(0)  # a real token -- leave for the next pass
        return "{" if m.group(0) == "{{" else "}"

    return _BRACE_SCAN_RE.sub(_sub, text)


class TemplateIndex:
    """Indexes a Crestron driver_definition dict for resolution."""

    def __init__(self, dd: dict):
        self.dd = dd
        self.commands_by_name = {c["Name"]: c for c in dd.get("Commands", [])}
        self.transformations_by_name = {t["Name"]: t for t in dd.get("Transformations", [])}
        self.controllers_by_name = {c["Name"]: c for c in dd.get("Controllers", [])}
        self.rules = dd.get("Rules", [])
        self.responses_by_name = {r["Name"]: r for r in dd.get("Responses", [])}
        self.command_id_names = {"_%s_" % c["Name"] for c in dd.get("CommandIds", [])}
        self.user_attr_names = {
            "_%s_" % u["Name"] for u in dd.get("UserAttributes", []) if u.get("Type") == "Custom"
        }
        self._text_memo: dict[str, str] = {}

    # -- bottom-up template text resolution --------------------------------
    def resolve_text(self, name: str, _stack=None) -> str:
        if name in self._text_memo:
            return self._text_memo[name]
        if _stack is None:
            _stack = []
        if name in _stack:
            raise CrestronTemplateError(
                "Commands[%r]: CommandName cycle: %s" % (name, " -> ".join(_stack + [name]))
            )
        cmd = self.commands_by_name.get(name)
        if cmd is None:
            raise CrestronTemplateError("no Commands[] entry named %r" % name)
        ctype = cmd.get("Type")
        if ctype == "Text":
            info = cmd.get("Info")
            if not isinstance(info, dict) or "Content" not in info:
                raise CrestronTemplateError("Commands[%r]: Text entry missing Info.Content" % name)
            text = _collapse_doubled_braces(info["Content"])
        elif ctype == "Template":
            info = cmd.get("Info")  # strictly case-sensitive: a lowercase
            # 'info' (as SetVideoConfiguration actually has -- a real bug in
            # Crestron's own JSON, cite: Commands[] entry "SetVideoConfiguration")
            # is NOT recognised, matching what any case-sensitive JSON-schema
            # consumer of this manifest would do. Fail loudly, don't guess.
            if not isinstance(info, dict) or "CommandName" not in info:
                raise CrestronTemplateError(
                    "Commands[%r]: Template entry has no (correctly-cased) Info.CommandName "
                    "-- keys present: %r" % (name, sorted(cmd.keys()))
                )
            base_name = info["CommandName"]
            base_text = self.resolve_text(base_name, _stack + [name])
            values = info.get("Values", {})

            def _sub(m):
                key = m.group(1)
                return values[key] if key in values else m.group(0)

            text = _TOKEN_RE.sub(_sub, base_text)
        elif ctype == "WakeOnLan":
            raise CrestronTemplateError("Commands[%r]: WakeOnLan is not a JSON template" % name)
        else:
            raise CrestronTemplateError("Commands[%r]: unsupported Type %r" % (name, ctype))
        self._text_memo[name] = text
        return text

    def chain_transformations(self, name: str) -> list[dict]:
        """All Transformations declared anywhere in name's CommandName
        ancestor chain (a Transformation on an intermediate base still
        applies to every descendant that inherits the base's slot)."""
        out = []
        cur = name
        seen = set()
        while cur is not None and cur not in seen:
            seen.add(cur)
            cmd = self.commands_by_name.get(cur)
            if cmd is None:
                break
            out.extend(cmd.get("Transformations", []))
            info = cmd.get("Info") if isinstance(cmd.get("Info"), dict) else None
            cur = info.get("CommandName") if info else None
        return out


# ---------------------------------------------------------------------------
# Step 2: parse the fully-substituted text into a slot-aware JSON tree
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Slot:
    name: str
    quoted: bool  # True: token appeared as the WHOLE content of a JSON string
    # False: token appeared as a bare (unquoted) JSON value position


_BARE_SLOT_RE = re.compile(r'(?<!")\{(\w+)\}(?!")')
_QUOTED_SLOT_RE = re.compile(r'^\{(\w+)\}$')


def parse_json_with_slots(text: str):
    """Parse `text` (JSON with possible bare-`{name}` slots in value
    position, and quoted-`"{name}"` slots in string position) into a plain
    Python structure whose leaves are `Slot` instances where a token was
    found. Delegates all *structural* parsing to `json.loads` -- bare slots
    are protected first (turned into valid-but-recognisable JSON strings),
    everything else is standard JSON, so this only special-cases exactly
    the two token shapes actually used in the samples (never partial/mixed
    with literal text in the same string -- verified by direct inspection
    of every Content/Values string in the Samsung Crestron IP package)."""

    def _protect(m):
        return json.dumps("\x00BARE:%s\x00" % m.group(1))

    protected = _BARE_SLOT_RE.sub(_protect, text)
    try:
        obj = json.loads(protected)
    except json.JSONDecodeError as e:
        raise CrestronTemplateError("resolved template is not valid JSON: %r (%s)" % (text, e))

    def walk(node):
        if isinstance(node, dict):
            return {k: walk(v) for k, v in node.items()}
        if isinstance(node, list):
            return [walk(v) for v in node]
        if isinstance(node, str):
            if node.startswith("\x00BARE:") and node.endswith("\x00"):
                return Slot(node[6:-1], quoted=False)
            m = _QUOTED_SLOT_RE.match(node)
            if m:
                return Slot(m.group(1), quoted=True)
            return node
        return node

    return walk(obj)


# ---------------------------------------------------------------------------
# Step 3: resolve each Slot to a Python source expression
# ---------------------------------------------------------------------------

@dataclass
class SlotResolution:
    pyexpr: str
    value_map: dict | None = None  # if this slot renders as ValueStateValues[...]
    map_var_name: str | None = None


def resolve_slot(idx: TemplateIndex, top_name: str, primary_value_name: str | None,
                  transforms_by_output: dict[str, dict], slot: Slot) -> SlotResolution:
    name = slot.name

    xform = transforms_by_output.get(name)
    if xform is not None:
        tdef = idx.transformations_by_name.get(xform["Transformation"])
        if tdef is None:
            raise CrestronTemplateError(
                "%s: Transformation %r referenced but not defined" % (top_name, xform["Transformation"])
            )
        source_token = xform.get("Input", "")
        m = _QUOTED_SLOT_RE.match(source_token) or _BARE_SLOT_RE.match(source_token)
        source_name = m.group(1) if m else source_token.strip("{}")
        source_pyexpr = "value" if source_name == primary_value_name else "self.%s" % source_name

        ttype = tdef.get("Type")
        if ttype == "Map":
            mapping = tdef.get("Info", {}).get("Map", {})
            varname = "%sValueStateValues" % name
            return SlotResolution(
                pyexpr="%s[%s]" % (varname, source_pyexpr),
                value_map=mapping,
                map_var_name=varname,
            )
        if ttype == "Format":
            fmt = tdef.get("Info", {}).get("FormatString", "{0}")
            return SlotResolution(pyexpr="'%s'.format(%s)" % (fmt, source_pyexpr))
        raise CrestronTemplateError(
            "%s: unsupported Transformation Type %r (%s)" % (top_name, ttype, xform["Transformation"])
        )

    if name in idx.command_id_names:
        return SlotResolution(pyexpr="self._commandId")

    if name in idx.user_attr_names:
        return SlotResolution(pyexpr="self.%s" % name.strip("_"))

    if name == primary_value_name:
        return SlotResolution(pyexpr="str(value)" if slot.quoted else "value")

    # generic fallback: a reference to some OTHER controller's persisted
    # state (this is how AccessToken resolves -- it is not a transform
    # output, not a system name, and not this command's own bound value,
    # so it falls through to "read the persistent controller state named
    # AccessToken", exactly matching Extron's self.AccessToken).
    return SlotResolution(pyexpr="self.%s" % name)


# ---------------------------------------------------------------------------
# Step 4: render a slot-tree as Python source (a dict literal)
# ---------------------------------------------------------------------------

def render_pynode(node, idx: TemplateIndex, top_name: str, primary_value_name: str | None,
                   transforms_by_output: dict[str, dict], collected_maps: dict, indent: int = 0) -> str:
    pad = "    " * indent
    inner_pad = "    " * (indent + 1)
    if isinstance(node, dict):
        if not node:
            return "{}"
        lines = ["{"]
        for k, v in node.items():
            rendered = render_pynode(v, idx, top_name, primary_value_name, transforms_by_output,
                                      collected_maps, indent + 1)
            lines.append("%s%r: %s," % (inner_pad, k, rendered))
        lines.append(pad + "}")
        return "\n".join(lines)
    if isinstance(node, list):
        parts = [render_pynode(v, idx, top_name, primary_value_name, transforms_by_output,
                                collected_maps, indent) for v in node]
        return "[%s]" % ", ".join(parts)
    if isinstance(node, Slot):
        res = resolve_slot(idx, top_name, primary_value_name, transforms_by_output, node)
        if res.value_map is not None:
            collected_maps[res.map_var_name] = res.value_map
        return res.pyexpr
    return repr(node)


# ---------------------------------------------------------------------------
# Step 5: capability classification (mechanical, from Crestron's own naming)
# ---------------------------------------------------------------------------

INFRA_EXCLUDE = {"RpcRequest", "RpcPollRequest", "SetAntennaTemplate", "RemoteKey"}
# GetPower2 is a documented internal retry duplicate of GetPower used only
# inside the UseWOLForPowerOn CommandSequence -- not independently invocable
# by any Rule/Controller, so it is not a standalone capability.
SKIP_STANDALONE = {"GetPower2"}
# WakeOnLan is not a JSON command at all (see resolve_text) -- it is folded
# into SetPower's generated body directly (see emit_module), matching the
# UseWOLForPowerOn Rule (CommandSequence: WakeOnLan x6, SetPower, GetPower2, GetPower).
WAKE_ON_LAN_NAME = "WakeOnLan"
# The only Get<->Set naming exception in the manifest (cited): the poll for
# the "VideoInput" capability is named GetReportedVideoInput, not
# GetVideoInput, because Crestron models "requested" vs "reported" input
# separately (Rule UpdateDisplayedVideoInputFeedback copies one into the other).
GET_TO_CAPABILITY_ALIASES = {"GetReportedVideoInput": "VideoInput"}


@dataclass
class Capability:
    name: str
    set_command: str | None
    update_command: str | None
    kind: str  # 'stateful' | 'fire'


def classify_capabilities(idx: TemplateIndex) -> tuple[list[Capability], list[dict]]:
    names = [n for n in idx.commands_by_name if n not in INFRA_EXCLUDE
             and n not in SKIP_STANDALONE and n != WAKE_ON_LAN_NAME]
    name_set = set(names)

    capability_for_get = dict(GET_TO_CAPABILITY_ALIASES)
    consumed_gets = set(GET_TO_CAPABILITY_ALIASES)
    for n in names:
        if n.startswith("Get") and ("Set" + n[3:]) in name_set:
            capability_for_get[n] = n[3:]
            consumed_gets.add(n)

    caps = []
    seen_capability_names = set()
    for n in names:
        if n in consumed_gets:
            continue
        if n.startswith("Set"):
            cap_name = n[3:]
            get_name = None
            for g, target in capability_for_get.items():
                if target == cap_name:
                    get_name = g
                    break
            # "stateful" only if a real Get<X> counterpart exists to poll
            # it back; a bare Set-prefixed entry with no poll (SetTvInput,
            # SetMediaService, SetPictureModeStandard, ...) is exactly as
            # much a one-shot fire command as a RemoteKey descendant is --
            # it just happens to share Crestron's Set-naming convention.
            kind = "stateful" if get_name else "fire"
            caps.append(Capability(cap_name, n, get_name, kind))
            seen_capability_names.add(cap_name)
        else:
            caps.append(Capability(n, n, None, "fire"))
    return caps, []


# ---------------------------------------------------------------------------
# Step 6: emit the ControlScript (GC-runtime HTTPDriver-dialect) module
# ---------------------------------------------------------------------------

def primary_value_name_for(idx: TemplateIndex, cap: Capability) -> str | None:
    cmd = idx.commands_by_name[cap.set_command]
    states_set = cmd.get("StatesSet")
    if states_set:
        return states_set[0]
    if cap.kind == "stateful":
        return cap.name
    return None


def _canonicalise_single_map_name(body_src: str, maps: dict) -> tuple[str, dict]:
    """When a body has exactly one value-map slot, rename its local
    variable to the bare `ValueStateValues` -- the universal convention
    used across every Extron ControlScript sample in this project (not
    something private to this one device's shipped script). This is
    needed for a fair wire_table comparison: wire_table's value_map
    extraction heuristic specifically looks for a local var named
    `ValueStateValues` (see wire_table.py's `primary_map` selection in
    extract_table) -- a per-command-prefixed name like
    `PowerValueStateValues` is functionally identical Python but defeats
    that heuristic. With >1 map in one body (e.g. SetAntennaTemplate's
    ConvertedAntenna + ConvertedSource) the prefixed names are kept to
    avoid a variable-name collision."""
    if len(maps) != 1:
        return body_src, maps
    (old_name, mapping), = maps.items()
    new_body = re.sub(r"\b%s\b" % re.escape(old_name), "ValueStateValues", body_src)
    return new_body, {"ValueStateValues": mapping}


def build_set_body(idx: TemplateIndex, cap: Capability, generation_report: list):
    top = cap.set_command
    text = idx.resolve_text(top)
    tree = parse_json_with_slots(text)
    primary = primary_value_name_for(idx, cap)
    transforms = idx.chain_transformations(top)
    by_output = {t["Output"]: t for t in transforms}
    maps: dict = {}
    body_src = render_pynode(tree, idx, top, primary, by_output, maps, indent=3)
    body_src, maps = _canonicalise_single_map_name(body_src, maps)
    return body_src, maps, primary


def build_update_body(idx: TemplateIndex, cap: Capability):
    top = cap.update_command
    text = idx.resolve_text(top)
    tree = parse_json_with_slots(text)
    transforms = idx.chain_transformations(top)
    by_output = {t["Output"]: t for t in transforms}
    maps: dict = {}
    body_src = render_pynode(tree, idx, top, None, by_output, maps, indent=3)
    body_src, maps = _canonicalise_single_map_name(body_src, maps)
    return body_src, maps


def find_response_decode(idx: TemplateIndex, get_command_name: str):
    """Flatten the Responses decoder graph for a given outstanding command
    name into a flat {ResultStateName: (json_path, transformation_or_None)}
    map. Handles CommandResponseNameMatch entries whose Match is a single
    name or a '|'-alternation (e.g. TVStatesCommandDecoder), and chases
    'Json' nodes with a Select (following Next for nested/chained Json
    nodes like GetResult -> GetTvStates / GetVideoConfigurationResponse)."""
    matches = []
    for r in idx.dd.get("Responses", []):
        if r.get("Type") != "CommandResponseNameMatch":
            continue
        match = r.get("Match", "")
        if get_command_name in match.split("|"):
            matches.append(r)
    if not matches:
        return {}

    result = {}

    def walk(node_name, prefix, depth=0):
        if depth > 10:
            return
        node = idx.responses_by_name.get(node_name)
        if node is None:
            return
        select = node.get("Select")
        is_json = node.get("Type") == "Json"
        if isinstance(select, dict) and is_json:
            xforms = {t["Output"]: t["Transformation"] for t in node.get("Transformations", [])}
            for state_name, path in select.items():
                full_path = ".".join(prefix + [path]) if prefix and "." not in path else path
                result[state_name] = (full_path, xforms.get(state_name))
            new_prefix = prefix
        elif is_json and isinstance(node.get("Match"), str):
            # a pure scope-narrowing node (e.g. GetResult: Match="result",
            # no Select of its own) -- its children's Select paths are
            # relative to this key.
            new_prefix = prefix + [node["Match"]]
        else:
            new_prefix = prefix
        for nxt in node.get("Next", []):
            walk(nxt, new_prefix, depth + 1)

    for m in matches:
        for nxt in m.get("Next", []):
            walk(nxt, [])
    return result


HEADER = '''"""
%(class_name)s (EXPERIMENT-GENERATED, Crestron -> ControlScript translation)

Mechanically translated by crestron2cs.py (experiments/crestron2cs) from the
Crestron LegacyWrappers JSON-engine driver at:
    %(source_pkg)s

This is a measurement artifact for project question 1b: "can a Crestron IP
driver be turned into an Extron ControlScript module?" -- NOT a hand-tuned,
production-quality driver. Every command below is derived mechanically from
Crestron's own Commands[]/Transformations[]/Controllers[] naming and value
domains (booleans keyed 'true'/'false', not Extron's 'On'/'Off') -- it does
NOT copy Extron's own shipped ethernet script's naming or value choices.
See experiments/crestron2cs/ for the resolver and the wire-table diff against
that shipped script.

DRIVER STYLE
    Ethernet - HTTP Driver (GC-runtime Extron2.HTTPDriver dialect)
COMMAND STRUCTURE
    JSON-RPC 2.0 over HTTPS, port 1516, createAccessToken handshake.
"""
from Extron2.HTTPDriver import HTTPDriver
import socket
import struct
import urllib.error
import urllib.request
import json


class %(class_name)s(HTTPDriver):

    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
%(commands_dict)s
        }
        self.AccessToken = None
        self.authenticated = False
        self._commandId = 1
'''

FOOTER = '''
    # ------------------------------------------------------------------
    # Infrastructure (not itself part of the measured wire content)
    # ------------------------------------------------------------------

    def __CheckResponseForErrors(self, sourceCmdName, response):
        try:
            res = json.loads(response.read().decode())
            if 'error' in res:
                self.Error(['{0}: {1}'.format(sourceCmdName, res['error']['message'])])
                return ''
            return res
        except Exception:
            self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])

    def __NextCommandId(self):
        # Crestron's CommandIds[] declares a MonotonicIntegerId, Min=1 Max=127,
        # Rollover=None -- modelled faithfully here. (Extron's own shipped
        # ethernet script hardcodes 'id': 1 for every request instead --
        # see extron_ethernet_source.py; a genuine, if likely inconsequential
        # per JSON-RPC's spec, protocol-detail difference.)
        current = self._commandId
        self._commandId = current + 1 if current < 127 else 1
        return current

    def __SetHelper(self, command, value, qualifier, data=None):
        data['id'] = self.__NextCommandId()
        url = self.RootURL.replace('http', 'https')
        payload = json.dumps(data).encode()
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        my_request = urllib.request.Request(url, data=payload, headers=headers, method='POST')
        try:
            res = self.Opener.open(my_request, timeout=8)
        except urllib.error.HTTPError as err:
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception:
            res = ''
        else:
            res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, data=None):
        return self.__SetHelper(command, value, qualifier, data)

    def _sendWakeOnLan(self, mac_address):
        """Crestron's WakeOnLan Command (Info.MacAddress = '{_MacAddress_}')
        -- a UDP magic packet, sent 6x by Rule UseWOLForPowerOn before every
        SetPower('true'). Extron's shipped ethernet script has NO equivalent
        anywhere (grep for 'MacAddress'/'WakeOnLan' in
        extron_ethernet_source.py returns nothing): Extron relies solely on
        the IP-remote/createAccessToken handshake to power the display on.
        """
        mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
        packet = b'\\xff' * 6 + mac_bytes * 16
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, ('255.255.255.255', 9))
        sock.close()
'''


def emit_module(idx: TemplateIndex, class_name: str, source_pkg: str):
    caps, _ = classify_capabilities(idx)
    generation_report = {"emitted": [], "skipped": []}

    commands_dict_lines = []
    body_chunks = []

    for cap in sorted(caps, key=lambda c: c.name):
        try:
            set_body, set_maps, primary = build_set_body(idx, cap, generation_report)
        except CrestronTemplateError as e:
            generation_report["skipped"].append({"name": cap.name, "reason": str(e)})
            continue

        update_body = None
        update_maps = {}
        response_decode = {}
        if cap.update_command:
            try:
                update_body, update_maps = build_update_body(idx, cap)
                response_decode = find_response_decode(idx, cap.update_command)
            except CrestronTemplateError as e:
                generation_report["skipped"].append(
                    {"name": cap.name + " (Update)", "reason": str(e)}
                )

        commands_dict_lines.append(
            "            %r: {'Set': True, 'Update': %s, 'Status': {}}," % (
                cap.name, bool(update_body)
            )
        )

        lines = []
        lines.append("    # Crestron Commands[%r] (%s)" % (cap.set_command, cap.kind))
        lines.append("    def _cmd_Set%s(self, value, qualifier):" % cap.name)
        # NOTE: each ValueStateValues map MUST be a local dict-literal
        # assignment (matching Extron's own idiom exactly), not a class
        # attribute referenced via self.<x> -- wire_table.py's mapslot
        # detection (_resolve_subscript) only recognises `Name[key]` where
        # `Name` is bound, in THIS method's own local env, directly to an
        # `ast.Dict` literal node. A `self.`-attribute indirection resolves
        # to a bare ('slot', ...) instead and the whole subscript expression
        # becomes an opaque marker -- confirmed by direct experiment (see
        # experiments/crestron2cs/test_crestron2cs.py::test_no_spurious_opaque).
        for varname, mapping in set_maps.items():
            lines.append("        %s = %r" % (varname, mapping))
        lines.append("        data = %s" % set_body)
        if cap.name == "Power":
            lines.append(
                "        if value in ('true', True) and self.AccessToken:\n"
                "            for _i in range(6):\n"
                "                self._sendWakeOnLan(self.MacAddress)"
            )
        lines.append("        self.__SetHelper(%r, value, qualifier, data)" % cap.name)
        lines.append("")

        if update_body is not None:
            lines.append("    def _cmd_Update%s(self, value, qualifier):" % cap.name)
            for varname, mapping in update_maps.items():
                lines.append("        %s = %r" % (varname, mapping))
            lines.append("        data = %s" % update_body)
            lines.append("        res = self.__UpdateHelper(%r, value, qualifier, data)" % cap.name)
            if response_decode:
                lines.append("        if res:")
                lines.append("            try:")
                for state_name, (path, xform) in response_decode.items():
                    accessor = "res"
                    for part in path.split("."):
                        accessor += "[%r]" % part
                    if xform:
                        tdef = idx.transformations_by_name.get(xform, {})
                        mapping = tdef.get("Info", {}).get("Map", {})
                        lines.append(
                            "                %s = %r[str(%s)]" % (state_name, mapping, accessor)
                        )
                    else:
                        lines.append("                %s = %s" % (state_name, accessor))
                lines.append("            except (KeyError, IndexError, AttributeError):")
                lines.append(
                    "                self.Error(['%s: Invalid/unexpected response'])" % cap.name
                )
            lines.append("")

        body_chunks.append("\n".join(lines))
        generation_report["emitted"].append(
            {"capability": cap.name, "set_command": cap.set_command,
             "update_command": cap.update_command, "kind": cap.kind}
        )

    module_src = HEADER % {
        "class_name": class_name,
        "source_pkg": source_pkg,
        "commands_dict": "\n".join(commands_dict_lines),
    }
    module_src += "\n\n".join(body_chunks)
    module_src += FOOTER
    return module_src, generation_report


def translate_pkg(pkg_path: str, class_name: str = "CrestronDerived"):
    doc = pkg_dump.process_pkg(pkg_path)
    dd = doc["driver_definition"]
    if dd is None:
        raise CrestronTemplateError("%s: no driver_definition (no .dll?)" % pkg_path)
    idx = TemplateIndex(dd)
    return emit_module(idx, class_name, pkg_path)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pkg", help="path to a Crestron .pkg")
    ap.add_argument("-o", "--output", required=True, help="output .py path")
    ap.add_argument("--report", help="optional generation-report .json path")
    ap.add_argument("--class-name", default="CrestronDerived")
    args = ap.parse_args(argv)

    module_src, report = translate_pkg(args.pkg, args.class_name)
    with open(args.output, "w") as f:
        f.write(module_src)
    print("wrote %s (%d capabilities emitted, %d skipped)" % (
        args.output, len(report["emitted"]), len(report["skipped"])
    ))
    if args.report:
        with open(args.report, "w") as f:
            json.dump(report, f, indent=2)
    return 0


if __name__ == "__main__":
    sys.exit(main())
