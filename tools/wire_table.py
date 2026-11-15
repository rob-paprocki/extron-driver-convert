#!/usr/bin/env python3
"""
wire_table.py - the acceptance ORACLE for the .pkp -> ControlScript translator.

Extracts, from a Python driver source file (either dialect: a shipped
ControlScript module -- `class DeviceClass`, `self.Commands`, `AddMatchString`,
`Set*`/`Update*` methods -- or a Global-Configurator embedded script --
`Extron2.BaseDriver`/`Extron2.HTTPDriver`, `_cmd_Set*`/`_cmd_Update*`, the same
`AddMatchString` idiom) a normalised WIRE TABLE: for every command, its
parameter list, the command-string template(s) it builds, the response
regex pattern(s) it matches, and any value maps.

Uses `ast`, never regex-on-source, to find the `Commands` dict literal, the
`AddMatchString` calls, and the per-command method bodies. Command strings are
resolved symbolically (a tiny constant-propagation interpreter over the
method's AST) to a canonical template string with '{}' marking a
substitution slot -- e.g. 'w1*{}ASPR\\r' for text/SIS protocols, or a
space-separated hex byte template with '??' slots for binary protocols
(struct.pack / a self.<helper>() byte-builder). Anything not statically
resolvable is recorded as an OPAQUE marker rather than guessed, and counted,
since that count bounds how much this oracle can see.

Also exposes `diff_tables(a, b)`: commands only in A, only in B, and for
shared commands, any difference in template/regex/value-map/parameter-list.

Run as a script for a human-readable dump or diff:
    python3 wire_table.py dump <driver.py>
    python3 wire_table.py diff <driver_a.py> <driver_b.py>
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections.abc import Hashable
from dataclasses import dataclass, field, asdict
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Small resolved-value representation.
#
# A "Val" is a tuple whose first element is a tag:
#   ('lit', value)              -- a fully known Python literal (str/bytes/int/...)
#   ('slot', description)       -- a per-call substitution slot we expect
#                                   (usually a function parameter, or a
#                                   qualifier[...] lookup): contributes '{}'/'??'
#   ('mapslot', mapname, mapping, keyexpr)
#                                -- a dict[...] lookup where the dict resolved
#                                   to a literal dict: contributes '{}'/'??'
#                                   AND records the mapping.
#   ('format', base_val, args)  -- str.format(*args) on base_val
#   ('concat', [vals])          -- string/bytes concatenation (BinOp Add, or
#                                   an f-string's parts)
#   ('bytespack', fmt, [vals])  -- struct.pack(fmt, *vals)
#   ('checksum', description)   -- a detected checksum-byte idiom
#                                   (e.g. two's-complement: ~sum(...) & 0xFF)
#   ('dict', {key: val})        -- a JSON-style request-body dict (HTTP dialect)
#   ('opaque', source)          -- could not resolve; counted.
# ---------------------------------------------------------------------------

OPAQUE = "opaque"
_VAL_TAGS = {"lit", "slot", "mapslot", "format", "concat", "bytespack", "checksum", "dict", OPAQUE}


class Resolver:
    """Symbolic, best-effort resolver for command-string-building expressions.

    Not a real interpreter: it does a simple, order-preserving walk of a
    function's statements building a name->AST-node environment (branches
    are walked independently so each `if`/`else` arm gets its own template),
    then resolves an expression against that environment. Anything it
    doesn't recognise becomes an ('opaque', <source>) leaf and increments
    `opaque_count` -- callers should treat that count as the honesty gauge.
    """

    def __init__(self, class_methods: dict[str, ast.FunctionDef]):
        self.class_methods = class_methods
        self.opaque_count = 0
        self.notes: list[str] = []
        self._method_env_cache: dict[str, dict[str, ast.AST]] = {}

    # -- environment building -------------------------------------------
    @staticmethod
    def build_env(stmts: list[ast.stmt], base_env: Optional[dict] = None) -> dict[str, ast.AST]:
        env = dict(base_env or {})

        def walk(stmt_list, into):
            for stmt in stmt_list:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                        and isinstance(stmt.targets[0], ast.Name):
                    into[stmt.targets[0].id] = stmt.value
                elif isinstance(stmt, ast.If):
                    walk(stmt.body, into)
                    walk(stmt.orelse, into)
                elif isinstance(stmt, (ast.For, ast.While)):
                    walk(stmt.body, into)
                    walk(stmt.orelse, into)
                elif isinstance(stmt, ast.Try):
                    walk(stmt.body, into)
                    for h in stmt.handlers:
                        walk(h.body, into)
                    walk(stmt.orelse, into)
                    walk(stmt.finalbody, into)
                elif isinstance(stmt, ast.With):
                    walk(stmt.body, into)

        walk(stmts, env)
        return env

    def method_env(self, func: ast.FunctionDef) -> dict[str, ast.AST]:
        key = func.name
        if key not in self._method_env_cache:
            self._method_env_cache[key] = self.build_env(func.body)
        return self._method_env_cache[key]

    # -- the resolver proper ----------------------------------------------
    def resolve(self, node, env, params, depth=0):
        if depth > 25:
            self.opaque_count += 1
            return (OPAQUE, "<max-depth>")

        # Detect the two's-complement checksum idiom before generic dispatch:
        # bytes([(~sum(X) & 0xFF) + 1])  or  (~sum(X) & 0xFF) + 1
        if self._looks_like_checksum(node):
            desc = ast.unparse(node)
            self.notes.append("checksum idiom (two's complement of a byte sum): %s" % desc)
            return ("checksum", "twos_complement")

        if isinstance(node, ast.Constant):
            return ("lit", node.value)

        if isinstance(node, ast.Name):
            # `env` wins over `params`: when inlining a helper method (e.g.
            # Samsung's self.build()), the helper's own formal parameter
            # names are substituted into `env` and may coincide textually
            # with the *caller's* parameter names ('value', 'qualifier')
            # without meaning the same thing -- e.g. self.build(0xF0, 0x01,
            # 0x00, 0x00) binds build's formal 'value' to a literal 0, not
            # to the caller's 'value' argument. Checking env first resolves
            # that correctly; params is only consulted once no local/
            # substituted binding shadows the name.
            if node.id in env:
                bound = env[node.id]
                # A helper-call inline substitution stores an *already
                # resolved* Val (resolved against the CALLER's env/params,
                # before the callee's own same-named formal parameters could
                # shadow it) rather than a raw AST node -- see _inline_call.
                if isinstance(bound, tuple) and bound and bound[0] in _VAL_TAGS:
                    return bound
                return self.resolve(bound, env, params, depth + 1)
            if node.id in params:
                return ("slot", node.id)
            self.opaque_count += 1
            return (OPAQUE, node.id)

        if isinstance(node, ast.Attribute):
            # self.RootURL, self.Host.DeviceAlias, etc: a structural
            # reference to fixed (but not visible-here) driver state.
            return ("slot", ast.unparse(node))

        if isinstance(node, ast.Subscript):
            return self._resolve_subscript(node, env, params, depth)

        if isinstance(node, ast.Call):
            return self._resolve_call(node, env, params, depth)

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self.resolve(node.left, env, params, depth + 1)
            right = self.resolve(node.right, env, params, depth + 1)
            return ("concat", [left, right])

        if isinstance(node, ast.JoinedStr):
            parts = []
            for v in node.values:
                if isinstance(v, ast.Constant):
                    parts.append(("lit", v.value))
                elif isinstance(v, ast.FormattedValue):
                    parts.append(self.resolve(v.value, env, params, depth + 1))
            return ("concat", parts)

        if isinstance(node, ast.Dict):
            d = {}
            for k, v in zip(node.keys, node.values):
                try:
                    key = ast.literal_eval(k)
                except Exception:
                    key = ast.unparse(k) if k is not None else "**"
                d[key] = self.resolve(v, env, params, depth + 1)
            return ("dict", d)

        if isinstance(node, ast.List) or isinstance(node, ast.Tuple):
            return ("concat", [self.resolve(e, env, params, depth + 1) for e in node.elts])

        # last resort: try a pure literal evaluation
        try:
            return ("lit", ast.literal_eval(node))
        except Exception:
            self.opaque_count += 1
            return (OPAQUE, ast.unparse(node))

    def _looks_like_checksum(self, node) -> bool:
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Invert):
            operand = node.operand
            if isinstance(operand, ast.Call) and isinstance(operand.func, ast.Name) \
                    and operand.func.id == "sum":
                return True
        # (~sum(x) & 0xFF) + 1  -- the UnaryOp is nested inside BinOps; walk down
        if isinstance(node, ast.BinOp):
            for child in ast.walk(node):
                if isinstance(child, ast.UnaryOp) and isinstance(child.op, ast.Invert):
                    operand = child.operand
                    if isinstance(operand, ast.Call) and isinstance(operand.func, ast.Name) \
                            and operand.func.id == "sum":
                        return True
        return False

    def _resolve_subscript(self, node, env, params, depth):
        base = node.value
        key_node = node.slice
        # Python <3.9 wraps the slice in an ast.Index; 3.9+ doesn't.
        if isinstance(key_node, ast.Index):  # pragma: no cover (old Python)
            key_node = key_node.value

        # dict[literal-key] where dict resolves (directly, or via env) to a
        # Dict literal: this is THE value-map idiom this codebase uses.
        base_dict_node = None
        base_name = None
        if isinstance(base, ast.Name):
            base_name = base.id
            candidate = env.get(base.id)
            if isinstance(candidate, ast.Dict):
                base_dict_node = candidate
        elif isinstance(base, ast.Dict):
            base_dict_node = base
            base_name = "<inline>"

        if base_dict_node is not None:
            mapping = self._literal_dict(base_dict_node)
            if mapping is not None:
                key_desc = ast.unparse(key_node)
                return ("mapslot", base_name, mapping, key_desc)

        # qualifier['Field'] / value-ish subscript on a function parameter
        if isinstance(base, ast.Name) and base.id in params:
            try:
                key_lit = ast.literal_eval(key_node)
                return ("slot", "%s[%r]" % (base.id, key_lit))
            except Exception:
                pass

        # A second subscript on a map lookup, e.g. `ValueStateValues[value][0]`
        # where ValueStateValues maps to a tuple/list (a multi-byte wire
        # value picked apart by index): project the mapping through the
        # literal index rather than giving up.
        base_val = self.resolve(base, env, params, depth + 1)
        if base_val[0] == "mapslot":
            _, name, mapping, key_desc = base_val
            try:
                idx = ast.literal_eval(key_node)
                projected = {k: (v[idx] if isinstance(v, (tuple, list)) else v)
                             for k, v in mapping.items()}
                return ("mapslot", "%s[%r]" % (name, idx), projected, key_desc)
            except Exception:
                pass

        try:
            return ("lit", ast.literal_eval(node))
        except Exception:
            self.opaque_count += 1
            return (OPAQUE, ast.unparse(node))

    @staticmethod
    def _literal_dict(dict_node: ast.Dict) -> Optional[dict]:
        out = {}
        for k, v in zip(dict_node.keys, dict_node.values):
            try:
                key = ast.literal_eval(k)
                val = ast.literal_eval(v)
            except Exception:
                return None
            out[key] = val
        return out

    def _resolve_call(self, node, env, params, depth):
        func = node.func
        fname = ast.unparse(func)

        # transparent no-op-ish casts: int(x), str(x), float(x)
        if isinstance(func, ast.Name) and func.id in ("int", "str", "float", "bytes") and node.args:
            return self.resolve(node.args[0], env, params, depth + 1)

        # struct.pack('fmt', ...) / pack('fmt', ...)
        if (isinstance(func, ast.Name) and func.id == "pack") or fname == "struct.pack":
            fmt_val = None
            if node.args:
                try:
                    fmt_val = ast.literal_eval(node.args[0])
                except Exception:
                    fmt_val = None
            parts = [self.resolve(a, env, params, depth + 1) for a in node.args[1:]]
            return ("bytespack", fmt_val, parts)

        # '<template>'.format(...)
        if isinstance(func, ast.Attribute) and func.attr == "format":
            base = self.resolve(func.value, env, params, depth + 1)
            args = [self.resolve(a, env, params, depth + 1) for a in node.args]
            return ("format", base, args)

        # json.dumps({...}) -- keep the dict, drop the encode-to-bytes wrapper
        if fname in ("json.dumps",) and node.args:
            return self.resolve(node.args[0], env, params, depth + 1)

        # self.<method>(...): inline single-return helper methods one level
        # deep (this is what self.build(...) is, in the Samsung driver).
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) \
                and func.value.id == "self":
            method_name = func.attr.lstrip("_")
            method = self._find_method(method_name)
            if method is not None:
                return self._inline_call(method, node.args, node.keywords, env, params, depth)
            self.opaque_count += 1
            return (OPAQUE, fname)

        self.opaque_count += 1
        return (OPAQUE, fname)

    def _find_method(self, stripped_name: str) -> Optional[ast.FunctionDef]:
        for name, func in self.class_methods.items():
            if name.lstrip("_") == stripped_name:
                return func
        return None

    def _inline_call(self, method: ast.FunctionDef, call_args, call_keywords,
                      caller_env, caller_params, depth):
        if depth > 10:
            self.opaque_count += 1
            return (OPAQUE, "<max-inline-depth:%s>" % method.name)

        # Resolve each argument expression EAGERLY, against the CALLER's
        # env/params, before it's substituted into the callee's scope. This
        # matters whenever the callee's formal parameter name collides with
        # a name meaningful in the caller (e.g. Samsung's
        # `def build(self, cmd1, cmd2, cmd3, value)` called as
        # `self.build(0x01, 0x00, 0x00, int(value))` from a method whose own
        # parameter is ALSO called 'value'): substituting the raw, unresolved
        # AST node would let the callee's same-named formal re-shadow it on
        # the next lookup and recurse forever. Substituting an already-
        # resolved Val sidesteps that entirely.
        formal = [a.arg for a in method.args.args if a.arg != "self"]
        resolved_args = [self.resolve(a, caller_env, caller_params, depth + 1) for a in call_args]
        resolved_kwargs = {kw.arg: self.resolve(kw.value, caller_env, caller_params, depth + 1)
                            for kw in call_keywords if kw.arg}

        method_env = dict(self.method_env(method))
        for i, formal_name in enumerate(formal):
            if i < len(resolved_args):
                method_env[formal_name] = resolved_args[i]
        method_env.update(resolved_kwargs)

        ret = self._find_return(method.body)
        if ret is None or ret.value is None:
            self.opaque_count += 1
            return (OPAQUE, "<no-return:%s>" % method.name)
        return self.resolve(ret.value, method_env, caller_params, depth + 1)

    @staticmethod
    def _find_return(stmts):
        """Find 'the' return statement for a helper method being inlined,
        walking statements in source order.

        A `Try`'s `except` handlers are deliberately never consulted here.
        A handler's `return` only executes on the path where the try body
        raised -- something this best-effort, non-executing walk cannot
        know happened -- so treating it as *the* return would be a guess
        the opaque-marker convention elsewhere in this module forbids.
        Only the try's own normal-path substructure (`body`, then `orelse`,
        then `finalbody` -- covered by the same generic attr walk used for
        `if`/`for`/`while`, since `Try` carries all three) is searched. If
        none of those has a return, the whole `Try` contributes nothing and
        the walk moves on to the next sibling statement, same as any other
        statement with no return inside it. That was the bug: the old code
        dove into a Try's handlers *before* checking a later sibling
        statement in the same block, so a handler's return could shadow the
        normal-path return that actually runs (findings/19 section 2, the
        Samsung ReadStatusHelper case)."""
        for stmt in stmts:
            if isinstance(stmt, ast.Return):
                return stmt
            for attr in ("body", "orelse", "finalbody"):
                sub = getattr(stmt, attr, None)
                if sub:
                    found = Resolver._find_return(sub)
                    if found is not None:
                        return found
        return None


# ---------------------------------------------------------------------------
# Rendering a resolved Val tree to a canonical template string.
# ---------------------------------------------------------------------------

def infer_kind(val) -> str:
    tag = val[0]
    if tag == "dict":
        return "dict"
    if tag in ("bytespack", "checksum"):
        return "bytes"
    if tag == "lit" and isinstance(val[1], (bytes, bytearray)):
        return "bytes"
    if tag == "concat":
        for c in val[1]:
            k = infer_kind(c)
            if k != "text":
                return k
        return "text"
    if tag == "format":
        for c in [val[1]] + val[2]:
            k = infer_kind(c)
            if k not in ("text",):
                return k
        return "text"
    return "text"


def render(val, kind: str) -> str:
    tag = val[0]
    if tag == "lit":
        v = val[1]
        if kind == "bytes":
            if isinstance(v, (bytes, bytearray)):
                return " ".join("%02X" % b for b in v)
            if isinstance(v, int):
                return "%02X" % (v & 0xFF)
            return str(v)
        return str(v)
    if tag in ("slot", "mapslot", "opaque"):
        return "??" if kind == "bytes" else "{}"
    if tag == "checksum":
        return "CHK"
    if tag == "format":
        _, base, args = val
        base_str = base[1] if base[0] == "lit" and isinstance(base[1], str) else "{}"
        parts = re.split(r"\{[^{}]*\}", base_str)
        pieces = []
        for i, p in enumerate(parts):
            pieces.append(p)
            if i < len(args):
                pieces.append(render(args[i], "text"))
        return "".join(pieces)
    if tag == "concat":
        joiner = " " if kind == "bytes" else ""
        return joiner.join(render(v, kind) for v in val[1])
    if tag == "bytespack":
        _, fmt, parts = val
        return " ".join(render(p, "bytes") for p in parts)
    if tag == "dict":
        _, d = val
        items = ", ".join("%r: %s" % (k, render(v, "text")) for k, v in d.items())
        return "{%s}" % items
    return "<?>"


def collect_slots(val, out: list):
    """Walk a resolved Val tree collecting the source description of every
    plain ('slot', ...) and ('opaque', ...) leaf -- i.e. every substitution
    whose *content* isn't already captured by a value-map. This is what
    catches a residual like DSC's UpdateLogoAssignment: both dialects render
    the same shape ('wA{}LOGO\\r') but one dialect's slot is fed by
    `qualifier['Logo']` and the other's by the bare `value` parameter --
    same wire shape, different actual wire content."""
    tag = val[0]
    if tag == "slot":
        out.append(val[1])
    elif tag == "opaque":
        out.append("OPAQUE:%s" % val[1])
    elif tag == "format":
        collect_slots(val[1], out)
        for a in val[2]:
            collect_slots(a, out)
    elif tag == "concat":
        for v in val[1]:
            collect_slots(v, out)
    elif tag == "bytespack":
        for v in val[2]:
            collect_slots(v, out)
    elif tag == "dict":
        for v in val[1].values():
            collect_slots(v, out)


def collect_value_maps(val, out_maps: dict):
    """Walk a resolved Val tree collecting every ('mapslot', name, mapping, key) seen."""
    tag = val[0]
    if tag == "mapslot":
        _, name, mapping, _key = val
        if name not in out_maps:
            out_maps[name] = mapping
    elif tag == "format":
        collect_value_maps(val[1], out_maps)
        for a in val[2]:
            collect_value_maps(a, out_maps)
    elif tag == "concat":
        for v in val[1]:
            collect_value_maps(v, out_maps)
    elif tag == "bytespack":
        for v in val[2]:
            collect_value_maps(v, out_maps)
    elif tag == "dict":
        for v in val[1].values():
            collect_value_maps(v, out_maps)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Template:
    kind: str                 # 'text' | 'bytes' | 'dict' | 'http'
    canonical: str
    source: str                # the un-parsed Python source of the resolved expr
    value_maps: dict = field(default_factory=dict)   # {varname: {user: wire}}
    slots: list = field(default_factory=list)         # non-map slot sources, e.g. "qualifier['Logo']"
    opaque: int = 0
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class Response:
    pattern: str               # regex pattern, as text (bytes decoded latin-1 if needed)
    is_bytes: bool
    tag: Any                   # the third AddMatchString arg, if a literal; else None
    handler: str

    def to_dict(self):
        return asdict(self)


@dataclass
class CommandRecord:
    name: str
    parameters: list = field(default_factory=list)
    set_templates: list = field(default_factory=list)     # list[Template]
    update_templates: list = field(default_factory=list)  # list[Template]
    responses: list = field(default_factory=list)          # list[Response]
    value_map: dict = field(default_factory=dict)          # canonical user->wire map
    has_set_method: bool = False
    has_update_method: bool = False

    def to_dict(self):
        return {
            "name": self.name,
            "parameters": self.parameters,
            "set_templates": [t.to_dict() for t in self.set_templates],
            "update_templates": [t.to_dict() for t in self.update_templates],
            "responses": [r.to_dict() for r in self.responses],
            "value_map": self.value_map,
            "has_set_method": self.has_set_method,
            "has_update_method": self.has_update_method,
        }


@dataclass
class WireTable:
    commands: dict            # name -> CommandRecord
    stats: dict
    unmapped_responses: list  # AddMatchString entries whose handler maps to no command

    def to_dict(self):
        return {
            "commands": {k: v.to_dict() for k, v in self.commands.items()},
            "stats": self.stats,
            "unmapped_responses": self.unmapped_responses,
        }


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

_HELPER_SUFFIXES = ("SetHelper", "UpdateHelper")


def _is_helper_call(node: ast.AST) -> Optional[str]:
    """Return 'set'/'update' if node is a call to self.__SetHelper/__UpdateHelper."""
    if not isinstance(node, ast.Call):
        return None
    func = node.func
    if not (isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
            and func.value.id == "self"):
        return None
    attr = func.attr.lstrip("_")
    if attr == "SetHelper":
        return "set"
    if attr == "UpdateHelper":
        return "update"
    return None


def _find_main_class(tree: ast.Module) -> ast.ClassDef:
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node
    raise ValueError("no class definition found in module")


def _collect_class_methods(cls: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    return {n.name: n for n in cls.body if isinstance(n, ast.FunctionDef)}


def _find_commands_dict(cls: ast.ClassDef) -> Optional[ast.Dict]:
    for func in cls.body:
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute) and target.attr == "Commands":
                        if isinstance(node.value, ast.Dict):
                            return node.value
    return None


def _env_sig(env: dict) -> tuple:
    """A structural signature for an env dict, for deduplicating branch
    worlds that ended up identical (same names bound to the same source
    expression) -- e.g. an if/else that doesn't touch the variable a later
    call actually uses, or assigns it the same literal on both arms."""
    return tuple(sorted((k, ast.dump(v)) for k, v in env.items()))


def _dedup_envs(envs: list) -> list:
    seen = set()
    out = []
    for e in envs:
        sig = _env_sig(e)
        if sig in seen:
            continue
        seen.add(sig)
        out.append(e)
    return out


# Cap on live branch worlds, purely as a safety net against pathological
# nesting in a method this walker hasn't been run against; every real sample
# module in this repo stays in the single digits.
_MAX_BRANCH_WORLDS = 64


def _find_helper_calls_in_method(func: ast.FunctionDef, resolver: Resolver):
    """Yield (kind, call_node, env) for every __SetHelper/__UpdateHelper call
    in `func`, each with the name->AST env visible at that call site.

    This threads a *list* of live envs ("worlds") through the statement
    sequence, one per branch alternative still reachable at that point,
    rather than a single env copied-and-discarded per branch. An if/else
    that assigns the SAME variable differently in each arm splits the
    world in two, and -- unlike a single-env walk that starts a fresh copy
    per branch and throws it away when the branch ends -- both worlds
    survive past the `if` and are still live for a helper call that comes
    AFTER it, each carrying its own arm's binding. That is what lets a
    command string assigned in both arms of an if/else and sent after it
    (RossTalk's SetMatrixTieCommand) resolve to two templates -- one per
    arm -- instead of the merge silently getting dropped and the call
    resolving the variable as opaque. Worlds that end up structurally
    identical (`_dedup_envs`) collapse back into one, so a branch that
    doesn't affect the eventual command string doesn't fork it for no
    reason, and a `return`/`raise`/`break`/`continue` terminates whichever
    world reached it, so an early-return guard clause doesn't leave behind
    a bogus duplicate world downstream of the value it never let execute."""
    results = []

    def branch_envs(stmts, envs):
        for stmt in stmts:
            if not envs:
                break
            if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                    and isinstance(stmt.targets[0], ast.Name):
                name = stmt.targets[0].id
                for env in envs:
                    # The value is evaluated before the name is bound, so a
                    # helper call inside it - `res = self.__UpdateHelper(...)`,
                    # the usual Update shape - is recorded with the env as it
                    # stood before this statement.
                    for node in ast.walk(stmt.value):
                        kind = _is_helper_call(node)
                        if kind:
                            results.append((kind, node, dict(env)))
                    env[name] = stmt.value
                continue
            if isinstance(stmt, ast.If):
                for env in envs:
                    for node in ast.walk(stmt.test):
                        kind = _is_helper_call(node)
                        if kind:
                            results.append((kind, node, dict(env)))
                body_envs = branch_envs(stmt.body, [dict(e) for e in envs])
                orelse_envs = branch_envs(stmt.orelse, [dict(e) for e in envs]) \
                    if stmt.orelse else [dict(e) for e in envs]
                envs = _dedup_envs(body_envs + orelse_envs)[:_MAX_BRANCH_WORLDS]
                continue
            if isinstance(stmt, (ast.For, ast.While)):
                if isinstance(stmt, ast.While):
                    for env in envs:
                        for node in ast.walk(stmt.test):
                            kind = _is_helper_call(node)
                            if kind:
                                results.append((kind, node, dict(env)))
                # A loop body may run zero or more times: the "didn't run"
                # world (the incoming envs, unchanged) and the "ran >=1
                # times" world (envs after one pass of the body) are both
                # live afterward.
                body_envs = branch_envs(stmt.body, [dict(e) for e in envs])
                after_envs = _dedup_envs(body_envs + [dict(e) for e in envs])[:_MAX_BRANCH_WORLDS]
                envs = branch_envs(stmt.orelse, after_envs) if stmt.orelse else after_envs
                continue
            if isinstance(stmt, ast.Try):
                # Normal path: body, then orelse (only reached if body
                # didn't raise/return), then finalbody (always). Each
                # handler is an alternate world starting from the envs
                # BEFORE the try, since an exception can interrupt the
                # body at any point; finalbody still applies to those too.
                normal_envs = branch_envs(stmt.body, [dict(e) for e in envs])
                if stmt.orelse:
                    normal_envs = branch_envs(stmt.orelse, normal_envs)
                handler_envs = []
                for h in stmt.handlers:
                    handler_envs += branch_envs(h.body, [dict(e) for e in envs])
                merged = _dedup_envs(normal_envs + handler_envs)[:_MAX_BRANCH_WORLDS]
                envs = branch_envs(stmt.finalbody, merged) if stmt.finalbody else merged
                continue
            if isinstance(stmt, ast.With):
                envs = branch_envs(stmt.body, envs)
                continue
            if isinstance(stmt, (ast.Return, ast.Raise, ast.Continue, ast.Break)):
                for env in envs:
                    for node in ast.walk(stmt):
                        kind = _is_helper_call(node)
                        if kind:
                            results.append((kind, node, dict(env)))
                envs = []
                continue
            for env in envs:
                for node in ast.walk(stmt):
                    kind = _is_helper_call(node)
                    if kind:
                        results.append((kind, node, dict(env)))
        return envs

    branch_envs(func.body, [{}])
    return results


def _param_names(func: ast.FunctionDef) -> set:
    return {a.arg for a in func.args.args if a.arg != "self"}


def _extract_template_from_helper_call(call: ast.Call, env: dict, params: set,
                                        resolver: Resolver) -> Optional[Template]:
    args = call.args
    keywords = {kw.arg: kw.value for kw in call.keywords if kw.arg}

    if len(args) < 2:
        return None

    second = args[1]
    is_http_dialect = isinstance(second, ast.Name) and second.id in params and second.id == "value"

    if is_http_dialect:
        url_node = keywords.get("url")
        if url_node is None and len(args) > 3:
            url_node = args[3]
        data_node = keywords.get("data")
        if data_node is None and len(args) > 4:
            data_node = args[4]

        templates = []
        if url_node is not None:
            val = resolver.resolve(url_node, env, params)
            kind = infer_kind(val)
            maps = {}
            collect_value_maps(val, maps)
            templates.append(("url", val, kind, maps))
        if data_node is not None:
            val = resolver.resolve(data_node, env, params)
            maps = {}
            collect_value_maps(val, maps)
            templates.append(("body", val, "dict", maps))

        if not templates:
            return None
        # Combine url + body into one Template record (both matter for the wire).
        pieces = []
        all_maps = {}
        all_slots = []
        for label, val, kind, maps in templates:
            pieces.append("%s=%s" % (label, render(val, kind)))
            all_maps.update(maps)
            collect_slots(val, all_slots)
        canonical = " ".join(pieces)
        return Template(kind="http", canonical=canonical,
                         source=ast.unparse(call),
                         value_maps=all_maps,
                         slots=all_slots,
                         opaque=0)

    # SIS/text/bytes dialect: args[1] is the command-string expression.
    val = resolver.resolve(args[1], env, params)
    kind = infer_kind(val)
    canonical = render(val, kind)
    maps = {}
    collect_value_maps(val, maps)
    slots = []
    collect_slots(val, slots)
    return Template(kind=kind, canonical=canonical, source=ast.unparse(args[1]),
                     value_maps=maps, slots=slots, opaque=0)


def _collect_re_compile_aliases(tree: ast.Module) -> set:
    """Return the set of bare names bound to `re.compile` by a module-level
    `from re import compile` (optionally `as X`), e.g. `{'compile'}` for
    `from re import compile` or `{'_rc'}` for `from re import compile as _rc`.

    Only names actually imported from the `re` module qualify: a same-named
    local function or a `compile` bound some other way is never treated as
    `re.compile` -- that would be guessing, not resolving. `re.compile(...)`
    and `<alias>.compile(...)` (e.g. `import re as r`) are recognised
    separately, as any Attribute call named `compile`, and don't need this."""
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == "re":
            for alias in node.names:
                if alias.name == "compile":
                    names.add(alias.asname or alias.name)
    return names


def _collect_add_match_strings(cls: ast.ClassDef, re_compile_names: Optional[set] = None):
    """Return list of dict(pattern, is_bytes, handler, tag) for every
    self.AddMatchString(re.compile(pattern), self.<handler>, tag) call.

    The pattern-compiling call is recognised either as `<expr>.compile(...)`
    (`re.compile`, or `<alias>.compile` for `import re as <alias>`) or as a
    bare name call whose name is in `re_compile_names` (`from re import
    compile[ as <alias>]`)."""
    re_compile_names = re_compile_names or set()
    out = []
    for func in cls.body:
        if not isinstance(func, ast.FunctionDef):
            continue
        for node in ast.walk(func):
            if not isinstance(node, ast.Call):
                continue
            fn = node.func
            if not (isinstance(fn, ast.Attribute) and fn.attr == "AddMatchString"):
                continue
            if len(node.args) < 2:
                continue
            pattern_arg = node.args[0]
            handler_arg = node.args[1]
            tag_arg = node.args[2] if len(node.args) > 2 else None

            pattern = None
            is_bytes = False
            is_compile_call = False
            if isinstance(pattern_arg, ast.Call) and pattern_arg.args:
                pfn = pattern_arg.func
                if isinstance(pfn, ast.Attribute) and pfn.attr == "compile":
                    is_compile_call = True
                elif isinstance(pfn, ast.Name) and pfn.id in re_compile_names:
                    is_compile_call = True
            if is_compile_call:
                try:
                    raw = ast.literal_eval(pattern_arg.args[0])
                    if isinstance(raw, bytes):
                        is_bytes = True
                        pattern = raw.decode("latin-1")
                    else:
                        pattern = raw
                except Exception:
                    pattern = None

            handler = None
            if isinstance(handler_arg, ast.Attribute):
                handler = handler_arg.attr
            elif isinstance(handler_arg, ast.Name):
                handler = handler_arg.id

            tag = None
            if tag_arg is not None:
                try:
                    tag = ast.literal_eval(tag_arg)
                except Exception:
                    tag = ast.unparse(tag_arg)

            if pattern is None or handler is None:
                continue
            out.append({"pattern": pattern, "is_bytes": is_bytes, "handler": handler, "tag": tag})
    return out


def _method_for_command(methods: dict[str, ast.FunctionDef], prefix: str, name: str):
    for candidate in ("%s%s" % (prefix, name), "_cmd_%s%s" % (prefix, name)):
        if candidate in methods:
            return methods[candidate]
    return None


def extract_table(source: str, filename: str = "<string>") -> WireTable:
    tree = ast.parse(source, filename=filename)
    cls = _find_main_class(tree)
    methods = _collect_class_methods(cls)

    commands_dict_node = _find_commands_dict(cls)
    command_names: list[str] = []
    parameters: dict[str, list[str]] = {}
    if commands_dict_node is not None:
        for k, v in zip(commands_dict_node.keys, commands_dict_node.values):
            try:
                name = ast.literal_eval(k)
            except Exception:
                continue
            command_names.append(name)
            params = []
            if isinstance(v, ast.Dict):
                for pk, pv in zip(v.keys, v.values):
                    try:
                        pkey = ast.literal_eval(pk)
                    except Exception:
                        continue
                    if pkey == "Parameters" and isinstance(pv, ast.List):
                        try:
                            params = [ast.literal_eval(e) for e in pv.elts]
                        except Exception:
                            params = []
            parameters[name] = params

    re_compile_names = _collect_re_compile_aliases(tree)
    match_strings = _collect_add_match_strings(cls, re_compile_names)

    resolver = Resolver(methods)
    records: dict[str, CommandRecord] = {}

    for name in command_names:
        rec = CommandRecord(name=name, parameters=parameters.get(name, []))

        set_method = _method_for_command(methods, "Set", name)
        if set_method is not None:
            rec.has_set_method = True
            fparams = _param_names(set_method)
            for kind, call, env in _find_helper_calls_in_method(set_method, resolver):
                if kind != "set":
                    continue
                tmpl = _extract_template_from_helper_call(call, env, fparams, resolver)
                if tmpl is not None:
                    tmpl.opaque = resolver.opaque_count
                    rec.set_templates.append(tmpl)

        update_method = _method_for_command(methods, "Update", name)
        if update_method is not None:
            rec.has_update_method = True
            fparams = _param_names(update_method)
            for kind, call, env in _find_helper_calls_in_method(update_method, resolver):
                if kind != "update":
                    continue
                tmpl = _extract_template_from_helper_call(call, env, fparams, resolver)
                if tmpl is not None:
                    tmpl.opaque = resolver.opaque_count
                    rec.update_templates.append(tmpl)

        records[name] = rec

    # value maps: prefer the Set-direction 'ValueStateValues' map (user->wire).
    # Fall back to inverting a Match-handler's reverse map (wire->user), and
    # otherwise to whatever map appeared first (Update, other var names).
    match_by_handler_suffix: dict[str, list[dict]] = {}
    for entry in match_strings:
        match_by_handler_suffix.setdefault(entry["handler"], []).append(entry)

    unmapped_responses = []
    responses_by_command: dict[str, list[Response]] = {}
    for entry in match_strings:
        handler = entry["handler"]
        stripped = handler.lstrip("_")
        mapped_name = None
        if stripped.startswith("Match"):
            candidate = stripped[len("Match"):]
            if candidate in records:
                mapped_name = candidate
        if mapped_name is None:
            unmapped_responses.append(entry)
            continue
        responses_by_command.setdefault(mapped_name, []).append(
            Response(pattern=entry["pattern"], is_bytes=entry["is_bytes"],
                     tag=entry["tag"], handler=handler))

    for name, rec in records.items():
        rec.responses = responses_by_command.get(name, [])

        primary_map = {}
        for tmpl in rec.set_templates:
            if "ValueStateValues" in tmpl.value_maps:
                primary_map = tmpl.value_maps["ValueStateValues"]
                break
        if not primary_map:
            # try inverting a reverse map found in the Match handler
            match_method = None
            for mname, mfunc in methods.items():
                if mname.lstrip("_") == "Match" + name:
                    match_method = mfunc
                    break
            if match_method is not None:
                menv = resolver.build_env(match_method.body)
                if "ValueStateValues" in menv and isinstance(menv["ValueStateValues"], ast.Dict):
                    reverse = Resolver._literal_dict(menv["ValueStateValues"])
                    if reverse:
                        # A Match handler's ValueStateValues is normally a
                        # flat wire-value -> human-name map, invertible into
                        # the user->wire map this fallback wants. But it is
                        # sometimes a *qualifier-keyed table* of per-input
                        # state maps instead (e.g. one map per HDMI/USB
                        # source), where the dict's values are themselves
                        # dicts. That shape can't be inverted into a single
                        # scalar map without guessing which sub-map's keys
                        # apply here, and a naive `{v: k ...}` inversion
                        # crashes on the unhashable dict value besides.
                        # Per the opaque-marker convention: leave it
                        # unresolved and counted, never guessed.
                        if all(isinstance(v, Hashable) for v in reverse.values()):
                            primary_map = {v: k for k, v in reverse.items()}
                        else:
                            resolver.opaque_count += 1
        if not primary_map:
            for tmpl in rec.update_templates:
                if tmpl.value_maps:
                    first_key = next(iter(tmpl.value_maps))
                    primary_map = tmpl.value_maps[first_key]
                    break
        rec.value_map = primary_map

    total_opaque = resolver.opaque_count

    stats = {
        "commands_found": len(records),
        "commands_with_set_method": sum(1 for r in records.values() if r.has_set_method),
        "commands_with_update_method": sum(1 for r in records.values() if r.has_update_method),
        "set_templates_resolved": sum(len(r.set_templates) for r in records.values()),
        "update_templates_resolved": sum(len(r.update_templates) for r in records.values()),
        "match_strings_total": len(match_strings),
        "match_strings_mapped": sum(len(v) for v in responses_by_command.values()),
        "match_strings_unmapped": len(unmapped_responses),
        "opaque_markers": total_opaque,
    }

    return WireTable(commands=records, stats=stats, unmapped_responses=unmapped_responses)


# ---------------------------------------------------------------------------
# Diff
# ---------------------------------------------------------------------------

def diff_tables(a: WireTable, b: WireTable) -> dict:
    a_names = set(a.commands)
    b_names = set(b.commands)
    only_a = sorted(a_names - b_names)
    only_b = sorted(b_names - a_names)
    shared = sorted(a_names & b_names)

    differences = {}
    for name in shared:
        ra, rb = a.commands[name], b.commands[name]
        diffs = {}

        pa, pb = sorted(ra.parameters), sorted(rb.parameters)
        if pa != pb:
            diffs["parameters"] = {"a": pa, "b": pb}

        sa = sorted(t.canonical for t in ra.set_templates)
        sb = sorted(t.canonical for t in rb.set_templates)
        if sa != sb:
            diffs["set_templates"] = {"a": sa, "b": sb}

        ua = sorted(t.canonical for t in ra.update_templates)
        ub = sorted(t.canonical for t in rb.update_templates)
        if ua != ub:
            diffs["update_templates"] = {"a": ua, "b": ub}

        # Same shape, different wire content: e.g. both sides render
        # 'wA{}LOGO\r' but one feeds the slot from qualifier['Logo'] and the
        # other from the bare value parameter. Catches this even when the
        # canonical *shape* strings above already matched.
        ssa = sorted(s for t in ra.set_templates for s in t.slots)
        ssb = sorted(s for t in rb.set_templates for s in t.slots)
        if sa == sb and ssa != ssb:
            diffs["set_template_slot_sources"] = {"a": ssa, "b": ssb}

        usa = sorted(s for t in ra.update_templates for s in t.slots)
        usb = sorted(s for t in rb.update_templates for s in t.slots)
        if ua == ub and usa != usb:
            diffs["update_template_slot_sources"] = {"a": usa, "b": usb}

        respa = sorted(r.pattern for r in ra.responses)
        respb = sorted(r.pattern for r in rb.responses)
        if respa != respb:
            diffs["responses"] = {"a": respa, "b": respb}

        if ra.value_map != rb.value_map:
            diffs["value_map"] = {"a": ra.value_map, "b": rb.value_map}

        if diffs:
            differences[name] = diffs

    return {
        "only_in_a": only_a,
        "only_in_b": only_b,
        "shared": shared,
        "differences": differences,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    dump_p = sub.add_parser("dump", help="extract and print a wire table as JSON")
    dump_p.add_argument("driver_py")
    dump_p.add_argument("-o", "--output")

    diff_p = sub.add_parser("diff", help="diff two driver files' wire tables")
    diff_p.add_argument("driver_a")
    diff_p.add_argument("driver_b")
    diff_p.add_argument("-o", "--output")

    args = ap.parse_args(argv)

    if args.cmd == "dump":
        with open(args.driver_py, encoding="utf-8") as f:
            src = f.read()
        table = extract_table(src, args.driver_py)
        out = json.dumps(table.to_dict(), indent=2, default=str)
    else:
        with open(args.driver_a, encoding="utf-8") as f:
            src_a = f.read()
        with open(args.driver_b, encoding="utf-8") as f:
            src_b = f.read()
        ta = extract_table(src_a, args.driver_a)
        tb = extract_table(src_b, args.driver_b)
        out = json.dumps(diff_tables(ta, tb), indent=2, default=str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print("wrote %s" % args.output)
    else:
        print(out)


if __name__ == "__main__":
    main()
