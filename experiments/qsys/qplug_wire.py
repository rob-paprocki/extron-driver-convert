#!/usr/bin/env python3
"""
qplug_wire.py - the wire table of a Q-SYS plugin: what it sends, and what it listens for.

The Q-SYS side of tools/wire_table.py (experiments/qsys/SCOPE.md, ROADMAP R46). A plain
`.qplug` is Lua; this parses it (lua_parse.py) and finds every place it puts bytes on a
connection - `sock:Write(data)` on a TcpSocket, SerialPorts or Ssh object, `udp:Send(ip,
port, data)`, `HttpClient.Upload{...}` / `Download{...}` - then works out what `data` can be
by reading the program backwards:

- through local and global assignments, string concatenation (`..`), `string.format`,
  `string.char`, `tostring` and the `a and b or c` idiom;
- into the helper functions a value comes from (their `return`s, with this call's arguments);
- out to every call site of the function the send sits in, when the payload is one of its
  parameters, so `ToQueue("SASIP")` in a control handler reaches `sock:Send(..)` three
  functions later;
- through queue tables: what `table.insert(Q, v)` puts in comes out of `table.remove(Q)`.

Values that come from one call, or from one queued item, stay together: a command and its
argument are never paired across two different calls. What cannot be worked out - a value
built in a loop, a reply-dependent value, a control's runtime state - becomes a slot `{}`
(text) or `??` (bytes) and is counted as opaque. Nothing is guessed.

Each template is rendered the way tools/wire_table.py renders one, so the two can be
compared directly: text with `{}` for each slot, or space-separated hex bytes with `??`.
It is attributed to the function or control handler whose code holds its command literal.

    python experiments/qsys/qplug_wire.py dump PLUGIN.qplug          # JSON wire table
    python experiments/qsys/qplug_wire.py compare PLUGIN.qplug EXTRON_MODULE.py

Standard library only.
"""
import argparse
import itertools
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "..", "tools"))

from lua_parse import Node, parse, walk   # noqa: E402

MAX_ALTS = 256          # alternatives kept per expression before the rest are counted opaque
MAX_DEPTH = 14          # helper inlining plus call-site steps, per path

TRANSPORT_CTORS = {("TcpSocket", "New"): "tcp", ("UdpSocket", "New"): "udp", ("Ssh", "New"): "ssh",
                   ("WebSocket", "New"): "websocket"}
PATTERN_FUNCS = {"match", "find", "gmatch", "gsub"}


# ---- values -----------------------------------------------------------------------------------
# A value is a tuple:
#   ('lit', bytes)  ('num', int|float)  ('bool', b)  ('nil',)
#   ('slot', description)  ('opaque', reason)
#   ('concat', [values])  ('char', [values])        string.char(...) -> bytes
#   ('table', TableNode, Ctx)  ('func', FuncInfo)  ('control', name)
#   ('mapslot', description, {key: value})          a table indexed by an unknown key

@dataclass
class Alt:
    """One possible value of an expression, the choices that produced it, and its origin."""
    val: tuple
    choices: tuple = ()          # ((choice point, option), ...), sorted
    label: str = None


def _merge_choices(a, b):
    if not a:
        return b
    if not b:
        return a
    d = dict(a)
    for k, v in b:
        if d.get(k, v) != v:
            return None              # the two halves made different choices: not a real value
        d[k] = v
    return tuple(sorted(d.items(), key=repr))


def combine(alt_lists, build, cap_note):
    """Cartesian product of alternative lists, keeping only mutually consistent ones."""
    out = []
    for combo in itertools.product(*alt_lists):
        choices = ()
        ok = True
        for a in combo:
            choices = _merge_choices(choices, a.choices)
            if choices is None:
                ok = False
                break
        if not ok:
            continue
        label = next((a.label for a in combo if a.label), None)
        out.append(Alt(build([a.val for a in combo]), choices, label))
        if len(out) >= MAX_ALTS:
            cap_note.append("alternatives capped at %d" % MAX_ALTS)
            break
    return out


def lua_tostring(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return "%d.0" % v
        return "%.14g" % v
    return str(v)


# ---- program model ----------------------------------------------------------------------------
class FuncInfo:
    def __init__(self, node, parent, label):
        self.node = node
        self.parent = parent
        self.label = label
        self.params = list(node.params) if node is not None else []
        self.callsites = []          # (call node, caller FuncInfo, index of first data argument)
        self.returns = []            # Return nodes in this function's own body

    def __repr__(self):
        return "<func %s>" % self.label


class Var:
    def __init__(self, name, kind, owner):
        self.name = name
        self.kind = kind             # 'local' 'param' 'loop' 'global'
        self.owner = owner           # FuncInfo that declares it (None for globals)
        self.numeric = False         # a numeric-for counter
        self.defs = []               # (expr Node or marker tuple, FuncInfo where it is evaluated)
        self.appends = []            # table.insert / T[#T+1] = v : (expr, FuncInfo)
        self.fields = {}             # T.k = v : key -> [(expr, FuncInfo)]

    def __repr__(self):
        return "<%s %s>" % (self.kind, self.name)


class Program:
    """Every function, variable and call site of one Lua chunk."""

    def __init__(self, body):
        self.body = body
        self.globals = {}
        self.var_of = {}             # id(Name node) -> Var
        self.func_of_node = {}       # id(Function node) -> FuncInfo
        self.funcs = []
        self.callsites = []          # (call node, FuncInfo it is in)
        self.main = FuncInfo(None, None, "<chunk>")
        self.main.node = Node("Function", 0, params=[], vararg=True, body=body, name="<chunk>")
        self.funcs.append(self.main)
        self._walk_block(body, self.main, [{}])
        self._link_calls()

    # -- scopes
    def _lookup(self, name, scopes):
        for s in reversed(scopes):
            if name in s:
                return s[name]
        v = self.globals.get(name)
        if v is None:
            v = self.globals[name] = Var(name, "global", None)
        return v

    def _declare(self, name, kind, func, scopes):
        v = Var(name, kind, func)
        scopes[-1][name] = v
        return v

    # -- walking
    def _walk_block(self, body, func, scopes):
        scopes.append({})
        for st in body:
            self._walk_stat(st, func, scopes)
        scopes.pop()

    def _walk_stat(self, st, func, scopes):
        k = st.kind
        if k == "Local":
            for e in st.exprs:
                self._walk_expr(e, func, scopes, label_hint=None)
            for i, name in enumerate(st.names):
                v = self._declare(name, "local", func, scopes)
                d = self._multi_def(st.exprs, i)
                if d is not None:
                    v.defs.append((d, func))
            for i, e in enumerate(st.exprs):
                if e.kind == "Function" and i < len(st.names):
                    self.func_of_node[id(e)].label = st.names[i]
        elif k == "LocalFunc":
            v = self._declare(st.name, "local", func, scopes)
            self._walk_expr(st.func, func, scopes, label_hint=st.name)
            v.defs.append((st.func, func))
        elif k == "FuncStat":
            label = self._path(st.target) + (":" + st.method if st.method else "")
            self._walk_expr(st.func, func, scopes, label_hint=label)
            if st.method is None and st.target.kind == "Name":
                v = self._lookup(st.target.name, scopes)
                self.var_of[id(st.target)] = v
                v.defs.append((st.func, func))
            else:
                base, keys = self._split_path(st.target)
                if base is not None:
                    v = self._lookup(base, scopes)
                    key = (keys[0] if keys else None) if st.method is None else st.method
                    if st.method is not None and keys:
                        key = keys[-1] + ":" + st.method
                    v.fields.setdefault(key, []).append((st.func, func))
        elif k == "Assign":
            for e in st.exprs:
                self._walk_expr(e, func, scopes, label_hint=None)
            for i, t in enumerate(st.targets):
                d = self._multi_def(st.exprs, i)
                if t.kind == "Name":
                    v = self._lookup(t.name, scopes)
                    self.var_of[id(t)] = v
                    if d is not None:
                        v.defs.append((d, func))
                else:
                    self._walk_expr(t, func, scopes, label_hint=None)
                    base, keys = self._split_path(t)
                    if base is not None and d is not None:
                        v = self._lookup(base, scopes)
                        if len(keys) == 1 and keys[0] is not None:
                            v.fields.setdefault(keys[0], []).append((d, func))
                        elif len(keys) == 1 and self._is_append_key(t.key, base):
                            v.appends.append((d, func))
                if d is not None and getattr(d, "kind", None) == "Function":
                    self.func_of_node[id(d)].label = self._path(t)
        elif k == "CallStat":
            self._walk_expr(st.call, func, scopes, label_hint=None)
        elif k == "Do":
            self._walk_block(st.body, func, scopes)
        elif k == "While":
            self._walk_expr(st.cond, func, scopes, None)
            self._walk_block(st.body, func, scopes)
        elif k == "Repeat":
            scopes.append({})
            for s in st.body:
                self._walk_stat(s, func, scopes)
            self._walk_expr(st.cond, func, scopes, None)
            scopes.pop()
        elif k == "If":
            for cond, body in st.clauses:
                self._walk_expr(cond, func, scopes, None)
                self._walk_block(body, func, scopes)
            if st.orelse is not None:
                self._walk_block(st.orelse, func, scopes)
        elif k == "NumFor":
            for e in (st.start, st.stop, st.step):
                if e is not None:
                    self._walk_expr(e, func, scopes, None)
            scopes.append({})
            v = self._declare(st.var, "loop", func, scopes)
            v.numeric = True                     # a numeric for: always a number
            v.defs.append((("loop", st.var), func))
            self._walk_block(st.body, func, scopes)
            scopes.pop()
        elif k == "GenFor":
            for e in st.exprs:
                self._walk_expr(e, func, scopes, None)
            scopes.append({})
            for name in st.names:
                v = self._declare(name, "loop", func, scopes)
                v.defs.append((("loop", name), func))
            self._walk_block(st.body, func, scopes)
            scopes.pop()
        elif k == "Return":
            func.returns.append(st)
            for e in st.exprs:
                self._walk_expr(e, func, scopes, None)

    def _multi_def(self, exprs, i):
        if i < len(exprs):
            return exprs[i]
        if exprs and exprs[-1].kind in ("Call", "Method"):
            return ("multi", exprs[-1], i - len(exprs) + 1)
        return None

    def _walk_expr(self, e, func, scopes, label_hint):
        if e is None:
            return
        k = e.kind
        if k == "Name":
            self.var_of[id(e)] = self._lookup(e.name, scopes)
        elif k == "Function":
            label = label_hint or e.name or "<anon in %s>" % func.label
            fi = FuncInfo(e, func, label)
            self.funcs.append(fi)
            self.func_of_node[id(e)] = fi
            inner = [{}]
            for p in e.params:
                self._declare(p, "param", fi, inner)
            self._walk_block(e.body, fi, scopes + inner)
        elif k in ("Call", "Method"):
            self.callsites.append((e, func))
            if k == "Call":
                self._walk_expr(e.func, func, scopes, None)
            else:
                self._walk_expr(e.obj, func, scopes, None)
            for a in e.args:
                self._walk_expr(a, func, scopes, None)
            self._note_table_insert(e, func, scopes)
        elif k == "Table":
            for f in e.fields:
                if f.key is not None:
                    self._walk_expr(f.key, func, scopes, None)
                hint = None
                if f.key is not None and f.key.kind == "String" and f.value.kind == "Function":
                    hint = f.key.value.decode("latin-1")
                self._walk_expr(f.value, func, scopes, hint)
        else:
            for child in e.f.values():
                if isinstance(child, Node):
                    self._walk_expr(child, func, scopes, None)
                elif isinstance(child, list):
                    for c in child:
                        if isinstance(c, Node):
                            self._walk_expr(c, func, scopes, None)

    def _note_table_insert(self, call, func, scopes):
        if call.kind != "Call" or _dotted(call.func) != "table.insert" or len(call.args) < 2:
            return
        t = call.args[0]
        if t.kind == "Name":
            v = self._lookup(t.name, scopes)
            v.appends.append((call.args[-1], func))

    @staticmethod
    def _is_append_key(key, base):
        # T[#T + 1] = v
        return (key.kind == "Binop" and key.op == "+" and key.left.kind == "Unop" and key.left.op == "#"
                and key.left.operand.kind == "Name" and key.left.operand.name == base)

    @staticmethod
    def _split_path(e):
        keys = []
        while e.kind == "Index":
            keys.append(e.key.value.decode("latin-1") if e.key.kind == "String" else None)
            e = e.obj
        if e.kind != "Name":
            return None, []
        return e.name, list(reversed(keys))

    @staticmethod
    def _path(e):
        return _render_path(e)

    def _link_calls(self):
        """Attach every call site to the user functions it can reach by name."""
        by_name = {}
        for fi in self.funcs:
            if fi.node is not None and fi.label:
                by_name.setdefault(fi.label, []).append(fi)
        for call, caller in self.callsites:
            target, first = None, 0
            if call.kind == "Call":
                name = _dotted(call.func)
                if name == "pcall" and call.args:
                    name, first = _dotted(call.args[0]), 1
                elif name in ("Timer.CallAfter",):
                    continue
                target = name
            else:
                obj = _dotted(call.obj)
                target = (obj + ":" + call.name) if obj else None
            for fi in by_name.get(target, []):
                fi.callsites.append((call, caller, first))


def _dotted(e):
    """'a.b.c' for a chain of Name/Index-with-string-keys, else None."""
    parts = []
    while e is not None and e.kind == "Index" and e.key.kind == "String":
        parts.append(e.key.value.decode("latin-1"))
        e = e.obj
    if e is None or e.kind != "Name":
        return None
    parts.append(e.name)
    return ".".join(reversed(parts))


def _render_path(e):
    if e.kind == "Name":
        return e.name
    if e.kind == "Index":
        base = _render_path(e.obj)
        k = e.key
        if k.kind == "String":
            s = k.value.decode("latin-1")
            return base + "." + s if re.match(r"^[A-Za-z_]\w*$", s) else "%s[%r]" % (base, s)
        if k.kind == "Number":
            return "%s[%s]" % (base, lua_tostring(k.value))
        return base + "[]"
    if e.kind == "Paren":
        return _render_path(e.expr)
    if e.kind == "Call":
        return _render_path(e.func) + "()"
    if e.kind == "Method":
        return _render_path(e.obj) + ":" + e.name + "()"
    return "<%s>" % e.kind


# ---- evaluation --------------------------------------------------------------------------------
class Ctx:
    """One activation of a function: its parameter bindings, or None when they are open
    (unknown, so a parameter is resolved through the function's call sites)."""

    def __init__(self, func, bindings=None, outer=None, depth=0):
        self.func = func
        self.bindings = bindings
        self.outer = outer
        self.depth = depth
        self.caller_ctxs = {}        # call-site index -> caller Ctx, shared by all parameters
        self.active = set()

    def find(self, func):
        c = self
        while c is not None:
            if c.func is func:
                return c
            c = c.outer
        return None


class Evaluator:
    def __init__(self, prog):
        self.prog = prog
        self.notes = []
        self._open = {}

    def open_ctx(self, func, depth):
        """A shared open activation of `func` (and its lexical parents)."""
        if func is None:
            return None
        key = id(func)
        c = self._open.get(key)
        if c is None:
            c = Ctx(func, None, self.open_ctx(func.parent, depth), depth)
            self._open[key] = c
        return c

    def ctx_for(self, func, ctx):
        """The activation to evaluate code of `func` in, seen from `ctx`."""
        found = ctx.find(func) if ctx is not None else None
        return found if found is not None else self.open_ctx(func, ctx.depth if ctx else 0)

    def ev(self, e, ctx):
        """Alternatives (list of Alt) for expression node `e` evaluated in `ctx`."""
        if ctx.depth > MAX_DEPTH:
            return [Alt(("opaque", "depth"))]
        k = e.kind
        if k == "String":
            return [Alt(("lit", e.value))]
        if k == "Number":
            return [Alt(("num", e.value))]
        if k == "True":
            return [Alt(("bool", True))]
        if k == "False":
            return [Alt(("bool", False))]
        if k == "Nil":
            return [Alt(("nil",))]
        if k == "Paren":
            return self.ev(e.expr, ctx)
        if k == "Table":
            return [Alt(("table", e, ctx))]
        if k == "Function":
            return [Alt(("func", self.prog.func_of_node.get(id(e))))]
        if k == "Vararg":
            return [Alt(("slot", "..."))]
        if k == "Name":
            return self.ev_name(e, ctx)
        if k == "Index":
            return self.ev_index(e, ctx)
        if k == "Binop":
            return self.ev_binop(e, ctx)
        if k == "Unop":
            if e.op == "-":
                alts = self.ev(e.operand, ctx)
                return [Alt(("num", -a.val[1]), a.choices, a.label) if a.val[0] == "num"
                        else Alt(("slot", "-" + _render_path(e.operand)), a.choices, a.label) for a in alts]
            if e.op == "not":
                return [Alt(("slot", "not"))]
            return [Alt(("slot", e.op + _render_path(e.operand)))]
        if k == "Call":
            return self.ev_call(e, ctx)
        if k == "Method":
            return self.ev_method(e, ctx)
        return [Alt(("opaque", k))]

    # names
    def ev_name(self, e, ctx):
        v = self.prog.var_of.get(id(e))
        if v is None:
            return [Alt(("slot", e.name))]
        if v.kind == "param":
            return self.ev_param(v, ctx)
        if v.kind == "loop":
            return [Alt(("slot", ("numloop:" if v.numeric else "loop:") + v.name))]
        if v.kind == "global" and v.name == "Controls":
            return [Alt(("control", None))]
        if v.kind == "global" and v.name in ("Properties", "System", "Timer", "Design", "Network"):
            return [Alt(("slot", v.name))]
        if not v.defs:
            return [Alt(("slot", v.name))]
        return self.ev_var(v, ctx)

    def ev_var(self, v, ctx):
        key = (id(v), id(ctx))
        if key in ctx.active:
            return [Alt(("opaque", "recursive:" + v.name))]
        # a value accumulated in place (v = v .. x) is built in a loop: not resolvable
        for d, _f in v.defs:
            if isinstance(d, Node) and any(n.kind == "Name" and self.prog.var_of.get(id(n)) is v
                                           for n in walk(d)):
                return [Alt(("opaque", "accumulated:" + v.name))]
        ctx.active.add(key)
        try:
            out = []
            many = len(v.defs) > 1
            for i, (d, f) in enumerate(v.defs):
                c = self.ctx_for(f, ctx)
                if isinstance(d, tuple):
                    if d[0] == "multi":
                        out += [Alt(("opaque", "multiple-return"))]
                    else:
                        out += [Alt(("slot", "%s:%s" % d))]
                    continue
                for a in self.ev(d, c):
                    choices = a.choices
                    if many:
                        choices = _merge_choices(choices, ((("def", id(v), id(ctx)), i),))
                        if choices is None:
                            continue
                    out.append(Alt(a.val, choices, a.label or (f.label if f is not self.prog.main else None)
                                   if a.val[0] in ("lit", "concat", "char", "num") else a.label))
            return out[:MAX_ALTS]
        finally:
            ctx.active.discard(key)

    def ev_param(self, v, ctx):
        c = ctx.find(v.owner)
        if c is None:
            c = self.open_ctx(v.owner, ctx.depth)
        idx = v.owner.params.index(v.name)
        if c.bindings is not None:
            b = c.bindings.get(v.name)
            if b is None:
                return [Alt(("nil",))]
            expr, caller_ctx = b
            return self.ev(expr, caller_ctx)
        sites = v.owner.callsites
        if not sites:
            return [Alt(("slot", "param:" + v.name))]
        out = []
        cp = ("cs", id(c))
        for i, (call, caller, first) in enumerate(sites):
            args = call.args
            if call.kind == "Method" and v.owner.params and v.owner.params[0] == "self":
                arg_i = idx - 1
            else:
                arg_i = idx + first
            if arg_i < 0:
                out.append(Alt(("slot", "self"), ((cp, i),)))
                continue
            caller_ctx = c.caller_ctxs.get(i)
            if caller_ctx is None:
                caller_ctx = Ctx(caller, None, self.open_ctx(caller.parent, c.depth), c.depth + 1)
                c.caller_ctxs[i] = caller_ctx
            if arg_i >= len(args):
                vals = [Alt(("nil",))]
            else:
                vals = self.ev(args[arg_i], caller_ctx)
            for a in vals:
                ch = _merge_choices(a.choices, ((cp, i),))
                if ch is None:
                    continue
                label = a.label
                if label is None and a.val[0] in ("lit", "concat", "char", "num"):
                    label = caller.label if caller is not self.prog.main else None
                out.append(Alt(a.val, ch, label))
        return out[:MAX_ALTS]

    # indexing
    def ev_index(self, e, ctx):
        if e.obj.kind == "Name" and e.key.kind != "String":
            v = self.prog.var_of.get(id(e.obj))
            if v is not None and v.appends:
                return self._heap_var(v, ctx)       # Q[1] on a queue: whatever was queued
        objs = self.ev(e.obj, ctx)
        keys = self.ev(e.key, ctx)
        out = []
        for o in objs:
            for kalt in keys:
                ch = _merge_choices(o.choices, kalt.choices)
                if ch is None:
                    continue
                for a in self._index(o.val, kalt.val, e, ctx):
                    ch2 = _merge_choices(ch, a.choices)
                    if ch2 is not None:
                        out.append(Alt(a.val, ch2, a.label or o.label or kalt.label))
        return out[:MAX_ALTS]

    def _index(self, obj, key, e, ctx):
        tag = obj[0]
        if tag == "control":
            name = obj[1]
            if name is None and key[0] == "lit":
                return [Alt(("control", key[1].decode("latin-1")))]
            if name is None:
                return [Alt(("control", "?"))]
            if key[0] == "lit":
                attr = key[1].decode("latin-1")
                if attr in ("String", "Value", "Boolean", "Position", "Color", "Legend", "Choices"):
                    return [Alt(("slot", "Controls.%s.%s" % (name, attr)))]
            return [Alt(("control", name))]               # an array of controls, indexed
        if tag == "table":
            return self._index_table(obj, key)
        if tag == "lit" and key[0] == "num":
            return [Alt(("slot", "byte"))]
        return [Alt(("slot", _render_path(e)))]

    def _index_table(self, obj, key):
        _, node, tctx = obj
        if key[0] in ("lit", "num"):
            want = key[1]
            pos = 0
            for f in node.fields:
                if f.key is None:
                    pos += 1
                    if key[0] == "num" and want == pos:
                        return self.ev(f.value, tctx)
                elif f.key.kind == "String" and key[0] == "lit" and f.key.value == want:
                    return self.ev(f.value, tctx)
                elif f.key.kind == "Number" and key[0] == "num" and f.key.value == want:
                    return self.ev(f.value, tctx)
            return [Alt(("nil",))]
        # unknown key: the table is a value map
        mapping = {}
        for i, f in enumerate(node.fields):
            k = (f.key.value.decode("latin-1") if f.key is not None and f.key.kind == "String"
                 else lua_tostring(f.key.value) if f.key is not None and f.key.kind == "Number"
                 else str(i + 1) if f.key is None else None)
            if k is None:
                continue
            vals = self.ev(f.value, tctx)
            if len(vals) == 1 and vals[0].val[0] in ("lit", "num"):
                v = vals[0].val[1]
                mapping[k] = v.decode("latin-1") if isinstance(v, bytes) else lua_tostring(v)
            else:
                return [Alt(("slot", "table[?]"))]
        return [Alt(("mapslot", "table[?]", mapping))]

    # operators
    def ev_binop(self, e, ctx):
        op = e.op
        if op == "..":
            parts = self._concat_parts(e)
            lists = [self.ev(p, ctx) for p in parts]
            return combine(lists, lambda vals: ("concat", list(vals)), self.notes)
        if op == "or":
            left = e.left
            if left.kind == "Binop" and left.op == "and":
                # c and a or b: a where c holds, b where it does not
                return self._choose(self.ev(left.left, ctx), self.ev(left.right, ctx), self.ev(e.right, ctx))
            lefts = self.ev(left, ctx)
            return self._choose(lefts, None, self.ev(e.right, ctx))
        if op == "and":
            conds = self.ev(e.left, ctx)
            return self._choose(conds, self.ev(e.right, ctx), [])
        if op in ("+", "-", "*", "%", "//", "&", "|", "~", "<<", ">>", "/", "^"):
            lists = [self.ev(e.left, ctx), self.ev(e.right, ctx)]
            return combine(lists, lambda vals: _arith(op, vals[0], vals[1]), self.notes)
        return [Alt(("bool", None))]

    @staticmethod
    def _choose(conds, if_true, if_false):
        """Lua's short-circuit operators, one condition alternative at a time. `if_true` None
        means the condition's own value is the result when it holds (`x or y`)."""
        out = []
        for c in conds:
            t = truthy(c.val)
            branches = []
            if t is not False:
                branches.append([c] if if_true is None else if_true)
            if t is not True:
                branches.append(if_false)
            for branch in branches:
                for a in branch:
                    if a is c:
                        out.append(a)
                        continue
                    ch = _merge_choices(c.choices, a.choices)
                    if ch is not None:
                        out.append(Alt(a.val, ch, a.label or c.label))
        return out[:MAX_ALTS]

    @staticmethod
    def _concat_parts(e):
        if e.kind == "Binop" and e.op == "..":
            return Evaluator._concat_parts(e.left) + Evaluator._concat_parts(e.right)
        return [e]

    # calls
    def ev_call(self, e, ctx):
        name = _dotted(e.func)
        args = e.args
        if name in ("string.format",) and args:
            return self._format(args[0], args[1:], ctx)
        if name == "string.char":
            lists = [self.ev(a, ctx) for a in args]
            return combine(lists, lambda vals: ("char", list(vals)), self.notes)
        if name in ("tostring", "tonumber", "math.floor", "math.tointeger") and args:
            return self.ev(args[0], ctx)
        if name in ("string.upper", "string.lower") and args:
            return [Alt(_case(a.val, name.endswith("upper")), a.choices, a.label) for a in self.ev(args[0], ctx)]
        if name == "string.rep" and len(args) >= 2:
            return combine([self.ev(args[0], ctx), self.ev(args[1], ctx)], lambda v: _rep(v[0], v[1]), self.notes)
        if name in ("table.remove", "table.unpack", "unpack") and args:
            return self._heap(args[0], e, ctx)
        if name in ("pcall", "table.concat", "string.sub", "string.byte", "select", "type", "pairs", "ipairs"):
            return [Alt(("opaque", "call:" + name))]
        if name == "string.reverse":
            return [Alt(("opaque", "call:" + name))]
        # a user function: inline its returns with this call's arguments
        callee_alts = self.ev(e.func, ctx)
        out = []
        for ca in callee_alts:
            if ca.val[0] != "func" or ca.val[1] is None:
                out.append(Alt(("opaque", "call:%s" % (name or _render_path(e.func))), ca.choices))
                continue
            for a in self._inline(ca.val[1], args, ctx):
                ch = _merge_choices(ca.choices, a.choices)
                if ch is not None:
                    out.append(Alt(a.val, ch, a.label))
        return out[:MAX_ALTS]

    def _inline(self, fi, args, ctx, self_expr=None):
        if ctx.depth >= MAX_DEPTH:
            return [Alt(("opaque", "depth"))]
        bindings = {}
        params = list(fi.params)
        if self_expr is not None and params and params[0] == "self":
            bindings["self"] = (self_expr, ctx)
            params = params[1:]
        for i, p in enumerate(params):
            if i < len(args):
                bindings[p] = (args[i], ctx)
        callee = Ctx(fi, bindings, self.ctx_for(fi.parent, ctx) if fi.parent else None, ctx.depth + 1)
        out = []
        for r in fi.returns:
            if r.exprs:
                out += self.ev(r.exprs[0], callee)
        return (out or [Alt(("nil",))])[:MAX_ALTS]

    def ev_method(self, e, ctx):
        if e.name == "format":
            return self._format(e.obj, e.args, ctx)
        if e.name in ("upper", "lower"):
            return [Alt(_case(a.val, e.name == "upper"), a.choices, a.label) for a in self.ev(e.obj, ctx)]
        if e.name == "rep" and e.args:
            return combine([self.ev(e.obj, ctx), self.ev(e.args[0], ctx)], lambda v: _rep(v[0], v[1]), self.notes)
        obj = _dotted(e.obj)
        out = []
        for fi in self.prog.funcs:
            if obj and fi.label == obj + ":" + e.name:
                out += self._inline(fi, e.args, ctx, self_expr=e.obj)
        return out or [Alt(("opaque", "method:" + e.name))]

    def _format(self, fmt_expr, args, ctx):
        fmts = self.ev(fmt_expr, ctx)
        out = []
        for f in fmts:
            if f.val[0] != "lit":
                out.append(Alt(("opaque", "format"), f.choices, f.label))
                continue
            pieces, specs = _split_format(f.val[1])
            lists = [[Alt(("lit", pieces[0]))]]
            for i, spec in enumerate(specs):
                arg = self.ev(args[i], ctx) if i < len(args) else [Alt(("nil",))]
                lists.append([Alt(_apply_spec(spec, a.val), a.choices, a.label) for a in arg])
                lists.append([Alt(("lit", pieces[i + 1]))])
            for a in combine(lists, lambda vals: ("concat", list(vals)), self.notes):
                ch = _merge_choices(a.choices, f.choices)
                if ch is not None:
                    out.append(Alt(a.val, ch, a.label or f.label))
        return out[:MAX_ALTS]

    def _heap(self, table_expr, call, ctx):
        """Values that come out of a queue table: everything put into it."""
        if table_expr.kind != "Name":
            return [Alt(("opaque", "heap"))]
        v = self.prog.var_of.get(id(table_expr))
        if v is None or not v.appends:
            return [Alt(("opaque", "heap:" + table_expr.name))]
        return self._heap_var(v, ctx)

    def _heap_var(self, v, ctx):
        """Every value put into queue table `v`. One choice per activation, so reading
        Q[1][1] and Q[1][2] in one function gives the parts of one queued item."""
        out = []
        cp = ("heap", id(v), id(ctx))
        for i, (expr, f) in enumerate(v.appends):
            for a in self.ev(expr, self.ctx_for(f, ctx)):
                ch = _merge_choices(a.choices, ((cp, i),))
                if ch is not None:
                    out.append(Alt(a.val, ch, a.label))
        return out[:MAX_ALTS]


def truthy(v):
    """Lua truth of a value: True, False, or None when it cannot be told."""
    tag = v[0]
    if tag == "nil":
        return False
    if tag == "bool":
        return v[1]
    if tag == "opaque":
        return None
    if tag == "slot":
        # strings and numbers are always true in Lua; anything else may be nil or false
        d = str(v[1])
        if d.startswith(("loop:", "numloop:", "byte", "arith", "format:")) or d.endswith((".String", ".Value", ".Position")):
            return True
        return None
    return True


def _arith(op, a, b):
    if a[0] == "num" and b[0] == "num":
        x, y = a[1], b[1]
        try:
            r = {"+": lambda: x + y, "-": lambda: x - y, "*": lambda: x * y,
                 "%": lambda: x % y, "//": lambda: x // y, "&": lambda: int(x) & int(y),
                 "|": lambda: int(x) | int(y), "~": lambda: int(x) ^ int(y),
                 "<<": lambda: int(x) << int(y), ">>": lambda: int(x) >> int(y),
                 "/": lambda: x / y, "^": lambda: float(x) ** y}[op]()
            return ("num", r)
        except (ZeroDivisionError, OverflowError, ValueError):
            return ("slot", "arith")
    return ("slot", "arith")


def _case(v, upper):
    if v[0] == "lit":
        return ("lit", v[1].upper() if upper else v[1].lower())
    return v


def _rep(s, n):
    if s[0] == "lit" and n[0] == "num" and isinstance(n[1], int) and 0 <= n[1] <= 64:
        return ("lit", s[1] * n[1])
    return ("slot", "rep")


_FMT_SPEC = re.compile(rb"%([-+ #0]*)(\d*)(?:\.(\d+))?([diouxXeEfgGqscaA%])")


def _split_format(fmt):
    pieces, specs, pos = [], [], 0
    cur = b""
    for m in _FMT_SPEC.finditer(fmt):
        cur += fmt[pos:m.start()]
        pos = m.end()
        if m.group(4) == b"%":
            cur += b"%"
            continue
        pieces.append(cur)
        cur = b""
        specs.append(m)
    pieces.append(cur + fmt[pos:])
    return pieces, specs


def _apply_spec(m, v):
    """Format one value with a %-specification when it is a literal; else leave a slot."""
    conv = m.group(4).decode()
    if v[0] in ("num", "lit") and conv != "q":
        flags, width, prec = m.group(1).decode(), m.group(2).decode(), m.group(3)
        spec = "%" + flags + width + ("." + prec.decode() if prec else "") + conv.replace("i", "d")
        try:
            if v[0] == "num":
                x = v[1]
                if conv in "diouxXc" and isinstance(x, float) and x == int(x):
                    x = int(x)
                if conv == "c":
                    return ("lit", bytes([int(x) & 0xFF]))
                return ("lit", (spec % x).encode("latin-1"))
            if conv == "s":
                return ("lit", (spec % v[1].decode("latin-1")).encode("latin-1"))
            if conv in "dixX":
                return ("lit", (spec % int(v[1])).encode("latin-1"))
        except (TypeError, ValueError):
            pass
    if conv == "c":
        return ("char", [v])
    return v if v[0] == "slot" else ("slot", "format:" + conv)


# ---- rendering ----------------------------------------------------------------------------------
_TEXT_OK = set(range(32, 127)) | {9, 10, 13}


def flatten(val, out):
    """A value as a list of pieces: ('bytes', b) or ('slot', desc, is_opaque, kind)."""
    tag = val[0]
    if tag == "lit":
        out.append(("bytes", val[1]))
    elif tag == "num":
        out.append(("bytes", lua_tostring(val[1]).encode()))
    elif tag == "bool":
        out.append(("bytes", (b"true" if val[1] else b"false") if val[1] is not None else b"?"))
    elif tag == "concat":
        for v in val[1]:
            flatten(v, out)
    elif tag == "char":
        for v in val[1]:
            if v[0] == "num" and isinstance(v[1], (int, float)) and 0 <= v[1] <= 255 and v[1] == int(v[1]):
                out.append(("byte", int(v[1])))
            else:
                out.append(("slot", _desc(v), v[0] == "opaque", "byte"))
    elif tag == "mapslot":
        out.append(("map", val[1], val[2]))
    elif tag == "nil":
        out.append(("bytes", b""))
    else:
        out.append(("slot", _desc(val), tag == "opaque", "any"))


def _desc(v):
    return "%s:%s" % (v[0], v[1]) if len(v) > 1 and isinstance(v[1], str) else v[0]


@dataclass
class Template:
    kind: str               # 'text' | 'bytes' | 'http'
    canonical: str          # wire_table's form: {} for every slot
    label: str
    slots: list = field(default_factory=list)
    value_maps: dict = field(default_factory=dict)
    opaque: int = 0
    typed: str = ""         # the same, with {#} where the slot can only hold a number


def _numeric_slot(desc):
    d = str(desc)
    return (d.startswith(("slot:numloop:", "slot:arith", "slot:byte", "slot:format:d", "slot:format:i",
                          "slot:format:x", "slot:format:X", "slot:format:f"))
            or d.endswith((".Value", ".Position")))


def render(val, label):
    pieces = []
    flatten(val, pieces)
    is_bytes = any(p[0] == "byte" or (p[0] == "slot" and p[3] == "byte") for p in pieces) or any(
        p[0] == "bytes" and any(b not in _TEXT_OK for b in p[1]) for p in pieces)
    slots, maps, opaque = [], {}, 0
    if is_bytes:
        parts = []
        for p in pieces:
            if p[0] == "bytes":
                parts += ["%02X" % b for b in p[1]]
            elif p[0] == "byte":
                parts.append("%02X" % p[1])
            elif p[0] == "map":
                parts.append("??")
                maps[p[1]] = p[2]
            else:
                parts.append("??")
                slots.append(p[1])
                opaque += p[2]
        return Template("bytes", " ".join(parts), label, slots, maps, opaque)
    text, typed = [], []
    for p in pieces:
        if p[0] == "bytes":
            s = p[1].decode("latin-1")
            text.append(s)
            typed.append(s.replace("{", "{{"))
        elif p[0] == "map":
            text.append("{}")
            typed.append("{}")
            maps[p[1]] = p[2]
        else:
            text.append("{}")
            typed.append("{#}" if _numeric_slot(p[1]) else "{}")
            slots.append(p[1])
            opaque += p[2]
    return Template("text", "".join(text), label, slots, maps, opaque, "".join(typed))


# ---- the wire table ----------------------------------------------------------------------------
@dataclass
class SendSite:
    line: int
    transport: str
    call: str
    function: str
    templates: list


@dataclass
class QWireTable:
    plugin: dict
    sends: list
    responses: list
    stats: dict
    notes: list

    def templates(self):
        seen = {}
        for s in self.sends:
            for t in s.templates:
                seen.setdefault((t.kind, t.canonical), t)
        return list(seen.values())

    def to_dict(self):
        return {"plugin": self.plugin, "sends": [asdict(s) for s in self.sends],
                "responses": self.responses, "stats": self.stats, "notes": self.notes}


def _transports(prog):
    """Var -> transport kind, for variables assigned a socket or serial port."""
    out = {}
    for v in list(prog.globals.values()) + [prog.var_of[k] for k in prog.var_of]:
        for d, _f in v.defs:
            if not isinstance(d, Node):
                continue
            if d.kind == "Call":
                name = _dotted(d.func)
                for (a, b), kind in TRANSPORT_CTORS.items():
                    if name == a + "." + b:
                        out[id(v)] = kind
            elif d.kind == "Index" and _dotted(d.obj) == "SerialPorts":
                out[id(v)] = "serial"
    return out


def _plugin_info(prog):
    v = prog.globals.get("PluginInfo")
    info = {}
    if v is None:
        return info
    for d, _f in v.defs:
        if isinstance(d, Node) and d.kind == "Table":
            for f in d.fields:
                if f.key is not None and f.key.kind == "String" and f.value.kind in ("String", "Number"):
                    val = f.value.value
                    info[f.key.value.decode("latin-1")] = val.decode("latin-1") if isinstance(val, bytes) else val
    return info


def _receive_functions(prog, transports):
    """Functions that handle received data, and everything they call."""
    names = {v.name for v in list(prog.globals.values()) + list(prog.var_of.values()) if id(v) in transports}
    roots = set()
    for fi in prog.funcs:
        if fi.node is None:
            continue
        lab = fi.label or ""
        m = re.match(r"^(\w+)(?:\[\d+\])?\.(EventHandler|Data)$", lab)
        if m and (m.group(1) in names or m.group(1) == "SerialPorts"):
            roots.add(id(fi))
            continue
        for n in walk(fi.node.body):
            if n.kind == "Method" and n.name in ("ReadLine", "Read", "Search"):
                roots.add(id(fi))
                break
    roots = [fi for fi in prog.funcs if id(fi) in roots]
    by_label = {}
    for fi in prog.funcs:
        by_label.setdefault(fi.label, []).append(fi)
    seen, stack = set(), list(roots)
    while stack:
        fi = stack.pop()
        if id(fi) in seen:
            continue
        seen.add(id(fi))
        for n in walk(fi.node.body if fi.node is not None else []):
            if n.kind == "Call":
                for g in by_label.get(_dotted(n.func), []):
                    stack.append(g)
            if n.kind == "Function":
                g = prog.func_of_node.get(id(n))
                if g is not None:
                    stack.append(g)
    return [fi for fi in prog.funcs if id(fi) in seen]


def extract(src, filename="<plugin>"):
    tree = parse(src)
    prog = Program(tree)
    ev = Evaluator(prog)
    transports = _transports(prog)
    sends = []
    for call, func in prog.callsites:
        if call.kind == "Method" and call.name in ("Write", "Send"):
            v = prog.var_of.get(id(call.obj)) if call.obj.kind == "Name" else None
            kind = transports.get(id(v)) if v is not None else None
            if kind is None:
                if _dotted(call.obj) and _dotted(call.obj).startswith("SerialPorts"):
                    kind = "serial"
                else:
                    continue
            if call.name == "Send" and kind == "udp":
                data = call.args[2] if len(call.args) >= 3 else None
            elif call.name == "Write":
                data = call.args[0] if call.args else None
            else:
                continue
            if data is None:
                continue
            ctx = ev.open_ctx(func, 0)
            alts = ev.ev(data, ctx)
            tmpls, seen = [], set()
            for a in alts:
                if a.val[0] == "nil":
                    continue                     # writing nil sends nothing
                t = render(a.val, a.label or func.label)
                key = (t.kind, t.canonical, t.label)
                if key not in seen:
                    seen.add(key)
                    tmpls.append(t)
            sends.append(SendSite(call.line, kind, "%s:%s" % (_render_path(call.obj), call.name),
                                  func.label, tmpls))
        elif call.kind == "Call" and _dotted(call.func) in ("HttpClient.Upload", "HttpClient.Download"):
            sends.append(SendSite(call.line, "http", _dotted(call.func), func.label,
                                  _http_templates(ev, call, func)))
    responses = []
    for fi in _receive_functions(prog, transports):
        ctx = ev.open_ctx(fi, 0)
        for n in walk(fi.node.body):
            pat = None
            if n.kind == "Binop" and n.op in ("==", "~="):
                for side in (n.left, n.right):
                    if side.kind == "String" and side.value:
                        responses.append({"equals": side.value.decode("latin-1"), "line": n.line,
                                          "function": fi.label})
                continue
            if n.kind == "Method" and n.name in PATTERN_FUNCS and n.args:
                pat = n.args[0]
            elif n.kind == "Call" and _dotted(n.func) in ("string." + p for p in PATTERN_FUNCS) and len(n.args) >= 2:
                pat = n.args[1]
            if pat is None:
                continue
            for a in ev.ev(pat, ctx):
                if a.val[0] == "lit":
                    responses.append({"pattern": a.val[1].decode("latin-1"), "line": n.line, "function": fi.label})
    dedup, seen = [], set()
    for r in responses:
        key = (r.get("pattern"), r.get("equals"), r["function"])
        if key not in seen:
            seen.add(key)
            dedup.append(r)
    all_t = [t for s in sends for t in s.templates]
    stats = {"send_sites": len(sends), "templates": len({(t.kind, t.canonical) for t in all_t}),
             "opaque_templates": len({(t.kind, t.canonical) for t in all_t if t.opaque}),
             "opaque_slots": sum(t.opaque for t in all_t), "response_patterns": len(dedup),
             "transports": sorted(set(transports.values()))}
    return QWireTable(_plugin_info(prog), sends, dedup, stats, sorted(set(ev.notes)))


def _http_templates(ev, call, func):
    if not call.args or call.args[0].kind != "Table":
        return [Template("http", "{}", func.label, [], {}, 1)]
    fields = {f.key.value.decode("latin-1"): f.value for f in call.args[0].fields
              if f.key is not None and f.key.kind == "String"}
    ctx = ev.open_ctx(func, 0)
    method = [Alt(("lit", b"POST" if _dotted(call.func).endswith("Upload") else b"GET"))]
    if "Method" in fields:
        method = ev.ev(fields["Method"], ctx)
    url = ev.ev(fields["Url"], ctx) if "Url" in fields else [Alt(("slot", "url"))]
    data = ev.ev(fields["Data"], ctx) if "Data" in fields else [Alt(("nil",))]
    out, seen = [], set()
    for a in combine([method, url, data], lambda v: ("concat", [v[0], ("lit", b" "), v[1], ("lit", b" "), v[2]]),
                     ev.notes):
        t = render(a.val, a.label or func.label)
        t.kind = "http"
        t.canonical = t.canonical.rstrip()
        if (t.canonical, t.label) not in seen:
            seen.add((t.canonical, t.label))
            out.append(t)
    return out


# ---- comparison with an Extron module ------------------------------------------------------------
class Wild:
    """A slot in a tokenised template: one or more units, of any kind or digits only."""
    def __init__(self, numeric):
        self.numeric = numeric

    def allows(self, unit):
        return unit is WILD or not self.numeric or unit in "0123456789-."

    def __repr__(self):
        return "{#}" if self.numeric else "{}"


WILD = Wild(False)       # also stands for "a fresh unit no literal equals" in intersects()
NUM = Wild(True)
MAX_EXPANSIONS = 4096


def tokens(kind, canonical):
    """A template as a list of literal units (characters, or byte pairs) and Wilds.
    Text may carry {#}, a slot that holds only a number, and {{ for a literal brace."""
    if kind == "bytes":
        # wire_table writes a computed checksum byte as CHK: here it is one unknown byte
        return [WILD if p in ("??", "CHK") else p for p in canonical.split(" ") if p]
    out, i = [], 0
    while i < len(canonical):
        if canonical.startswith("{}", i):
            out.append(WILD)
            i += 2
        elif canonical.startswith("{#}", i):
            out.append(NUM)
            i += 3
        elif canonical.startswith("{{", i):
            out.append("{")
            i += 2
        else:
            out.append(canonical[i])
            i += 1
    return out


def intersects(a, b):
    """Whether two tokenised templates can produce one common string. A WILD stands for one
    or more units. Breadth-first over the product of the two patterns' automata."""
    def closure(states, pat):
        out = set(states)
        for i, inw in states:
            if inw:
                out.add((i + 1, False))
        return out

    def accept(states, pat):
        return any(i == len(pat) and not inw for i, inw in states)

    def moves(state, pat, unit):
        """States after reading `unit`; unit WILD means a unit equal to no literal."""
        i, inw = state
        res = set()
        if inw:
            if pat[i].allows(unit):
                res.add((i, True))
        elif i < len(pat):
            if isinstance(pat[i], Wild):
                if pat[i].allows(unit):
                    res.add((i, True))
            elif unit is not WILD and pat[i] == unit:
                res.add((i + 1, False))
        return res

    start = (closure({(0, False)}, a), closure({(0, False)}, b))
    seen, todo = set(), [start]
    while todo:
        sa, sb = todo.pop()
        key = (frozenset(sa), frozenset(sb))
        if key in seen:
            continue
        seen.add(key)
        if accept(sa, a) and accept(sb, b):
            return True
        units = set()
        for pat, states in ((a, sa), (b, sb)):
            for i, inw in states:
                if not inw and i < len(pat) and not isinstance(pat[i], Wild):
                    units.add(pat[i])
        units.add(WILD)                      # "any other unit"
        for u in units:
            na = set()
            for s in sa:
                na |= moves(s, a, u)
            nb = set()
            for s in sb:
                nb |= moves(s, b, u)
            if na and nb:
                todo.append((closure(na, a), closure(nb, b)))
    return False


def matches(pattern_tokens, concrete_tokens):
    return intersects(pattern_tokens, concrete_tokens)


def expand(t):
    """Every concrete string an Extron template can send, when each of its slots is a value
    map; None when some slot is free."""
    n = t.canonical.count("{}") if t.kind == "text" else t.canonical.split(" ").count("??")
    if n == 0:
        return [t.canonical]
    if t.slots or len(t.value_maps) != n or t.kind != "text":
        return None
    parts = t.canonical.split("{}")
    total = 1
    for m in t.value_maps.values():
        total *= max(1, len(m))
    if total > MAX_EXPANSIONS:
        return None
    out = []
    for combo in itertools.product(*[[str(v) for v in m.values()] for m in t.value_maps.values()]):
        out.append(parts[0] + "".join(v + parts[i + 1] for i, v in enumerate(combo)))
    return out


def http_path(canonical):
    """The resource path of an HTTP template, from either side: wire_table's
    'url=v2/x body={}' or this reader's 'GET https://{}:4003/v2/x'."""
    if canonical.startswith("url="):
        path = canonical[4:].split(" body=")[0]
    else:
        parts = canonical.split(" ", 2)
        url = parts[1] if len(parts) > 1 else ""
        url = url.split("://", 1)[-1]
        path = url.split("/", 1)[1] if "/" in url else ""
    return path.lstrip("/")


def sis_normal(c):
    """One spelling for an Extron SIS escape command. SIS accepts Esc, 'W' or 'w' as the
    escape and, after 'W', '|' as the terminator; these are different bytes for one command."""
    s = c
    if s[:1] in ("W", "w", "\x1b"):
        s = "\x1b" + s[1:]
        s = s.replace("|\r", "\r")
        if s.endswith("|"):
            s = s[:-1] + "\r"
    return s


def compare(qtable, extron_src, extron_name="<module>", sis=False):
    """How much of an Extron module's command surface the plugin sends, on the wire.

    Each Extron template is expanded through its value maps into the strings it can send,
    and each string is checked against the plugin's templates (a slot matches anything).
    A template that cannot be expanded is checked for any common string instead.
    With sis=True, text templates are compared under one SIS escape spelling (sis_normal):
    an equivalence, reported as such, never the identical-wire result."""
    import warnings
    import wire_table
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        wt = wire_table.extract_table(extron_src, extron_name)
    norm = sis_normal if sis else (lambda c: c)
    plug, typed_of = {}, {}
    for t in qtable.templates():
        c = norm(t.canonical) if t.kind == "text" else t.canonical
        plug.setdefault((t.kind, c), set()).add(t.label)
        if t.kind == "text":
            typed = norm(t.typed) if t.typed else c
            if typed_of.setdefault((t.kind, c), typed) != typed:
                typed_of[(t.kind, c)] = c          # two typings of one template: the looser
    # A template with no literal content but a line ending (a password, a pass-through of
    # whatever the user typed) would match every command: it covers nothing.
    def anchored(k, c):
        if k == "bytes":
            return any(p not in ("??", "CHK") for p in c.split(" "))
        body = (http_path(c) if k == "http" else c).replace("{}", "")
        return bool(body.strip("\r\n "))
    unanchored = sorted(c for k, c in plug if not anchored(k, c))
    plug_tokens = [(k, c, tokens("text", http_path(c)) if k == "http" else tokens(k, typed_of.get((k, c), c)))
                   for k, c in plug if anchored(k, c)]
    rows, seen = [], set()
    for name, rec in sorted(wt.commands.items()):
        for t in rec.set_templates + rec.update_templates:
            if t.kind not in ("text", "bytes", "http") or (t.kind, t.canonical) in seen:
                continue
            seen.add((t.kind, t.canonical))
            if sis and t.kind == "text":
                t = wire_table.Template(t.kind, norm(t.canonical), t.source, t.value_maps, t.slots, t.opaque)
            row = {"command": name, "kind": t.kind, "template": t.canonical}
            same_kind = [(c, tok) for k, c, tok in plug_tokens if k == t.kind]
            if t.kind == "http":
                path = http_path(t.canonical)
                exact = sorted(c for c, _tok in same_kind if http_path(c) == path)
                via = exact or sorted(c for c, tok in same_kind if intersects(tok, tokens("text", path)))
                row.update(path=path, plugin=via, result="exact" if exact else "compatible" if via else "none")
            elif (t.kind, t.canonical) in plug:
                row.update(result="exact", plugin=[t.canonical])
            else:
                concrete = expand(t)
                if concrete is not None:
                    hit, via = 0, set()
                    for s in concrete:
                        st = tokens(t.kind, s)
                        for c, tok in same_kind:
                            if intersects(tok, st):
                                hit += 1
                                via.add(c)
                                break
                    row.update(strings=len(concrete), covered=hit, plugin=sorted(via),
                               result="full" if hit == len(concrete) else "partial" if hit else "none")
                else:
                    ttok = tokens(t.kind, t.canonical)
                    via = sorted(c for c, tok in same_kind if intersects(tok, ttok))
                    row.update(result="compatible" if via else "none", plugin=via)
            rows.append(row)
    matched = {c for r in rows for c in r.get("plugin", [])}
    counts = {}
    for r in rows:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    return {
        "comparison": "SIS-equivalent (Esc/W/w escapes and the '|' terminator as one)" if sis
                      else "identical wire bytes",
        "extron_templates": len(rows),
        "plugin_templates": len(plug),
        "summary": counts,
        "rows": rows,
        "unanchored_plugin_templates": unanchored,
        "only_plugin": [{"kind": k, "template": c, "plugin_origins": sorted(o)}
                        for (k, c), o in sorted(plug.items()) if c not in matched and c not in unanchored],
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dump", help="the plugin's wire table as JSON")
    p.add_argument("plugin")
    p = sub.add_parser("compare", help="templates shared with an Extron ControlScript module")
    p.add_argument("plugin")
    p.add_argument("module")
    p.add_argument("--sis", action="store_true",
                   help="also treat SIS's escape spellings (Esc, W, w; '|') as one; reported as such")
    args = ap.parse_args(argv)
    with open(args.plugin, encoding="utf-8", errors="surrogateescape") as f:
        table = extract(f.read(), args.plugin)
    if args.cmd == "dump":
        out = table.to_dict()
    else:
        with open(args.module, encoding="utf-8") as f:
            out = compare(table, f.read(), args.module, sis=args.sis)
    print(json.dumps(out, indent=1, default=str, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
