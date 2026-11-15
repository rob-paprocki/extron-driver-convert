#!/usr/bin/env python3
"""
drive.py - execute ControlScript device modules offline and record what every
Set and Update would put on the wire (ROADMAP R13).

Every other check in this repo reads code: wire_table extracts templates,
find_dangling_self_calls and find_unresolved_globals look for names. None of
them can see a call made the wrong way - finding 14 section 7's stripped
@staticmethod compiled, resolved and scored perfectly, and raised TypeError on
every use. This runs the code.

Differential mode is the oracle: a generated module and Extron's shipped module
for the same device are loaded against the same stand-in extronlib
(extronlib_stub), constructed through the same transport class and model,
and given the same inputs. Per command and per Set/Update, each input's outcome
is compared: the bytes sent, whether the module discarded the input, and the
type of any exception that escaped. The shipped module is the reference, so an
adversarial input either side rejects is fine as long as both do.

Inputs come from both modules' own method bodies, never invented: the keys of
the value maps they look values up in, the literals they compare against, the
numeric bounds they check (each bound, and one either side of it), for the
command value and for every qualifier key they read. A few adversarial values
(empty, space, quote, None, out of range) are added to every Set. A command
whose bodies offer no candidates gets a small default set.

Not modelled, so not compared: device replies (SendAndWait returns None and no
data is fed to ReceiveData), and anything a Wait or Timer would do later.

Usage:
  python drive.py --generated GEN.py --shipped SHIP.py    differential, JSON on stdout
  python drive.py --module MOD.py                         one module: what escapes

Standard library only. Meant to run in its own process (differential.py gives
each pair one): it patches time.sleep and urllib.request globally.
"""
import argparse
import ast
import contextlib
import copy
import importlib.util
import inspect
import io
import json
import os
import sys
import textwrap
import time
import traceback
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import extronlib_stub  # noqa: E402

TRANSPORT_ORDER = ("SerialClass", "EthernetClass", "SerialOverEthernetClass",
                   "SSHClass", "HTTPClass")
ADVERSARIAL_VALUES = ["", "a b", 'a"b', None, -1, 99999]
DEFAULT_VALUES = ["On", "Off", 0, 1, "1"]
DEFAULT_QUALIFIER_VALUES = ["1", "2"]
MAX_INPUTS = 40
MAX_EXAMPLES = 2

_CURRENT_SINK = []


# --------------------------------------------------------------------------
# HTTP: modules that talk HTTP build an opener; record what they would request
# --------------------------------------------------------------------------

class _Response:
    status = 200
    code = 200
    headers = {}

    def read(self, *a):
        return b"{}"

    def getcode(self):
        return 200

    def info(self):
        return {}

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _record_http(req, data=None):
    url = getattr(req, "full_url", None) or str(req)
    body = data if data is not None else getattr(req, "data", None)
    method = req.get_method() if hasattr(req, "get_method") else ("POST" if body else "GET")
    _CURRENT_SINK.append(("HTTP", ("%s %s " % (method, url)).encode("utf-8")
                          + extronlib_stub._to_bytes(body or b"")))
    return _Response()


class _Opener:
    def open(self, req, data=None, timeout=None):
        return _record_http(req, data)

    def add_handler(self, handler):
        pass


def _patch_process():
    time.sleep = lambda *a, **k: None
    urllib.request.build_opener = lambda *a, **k: _Opener()
    urllib.request.urlopen = lambda req, data=None, *a, **k: _record_http(req, data)
    urllib.request.install_opener = lambda *a, **k: None


# --------------------------------------------------------------------------
# Loading and constructing
# --------------------------------------------------------------------------

def _where(exc_tb, path):
    """The last traceback line inside the module under test, as 'line N'."""
    line = None
    for frame, lineno in traceback.walk_tb(exc_tb):
        if os.path.abspath(frame.f_code.co_filename) == os.path.abspath(path):
            line = lineno
    return "line %d" % line if line else None


def _describe(exc, path=None):
    out = {"type": type(exc).__name__, "message": str(exc)[:240]}
    if path:
        where = _where(exc.__traceback__, path)
        if where:
            out["where"] = where
    return out


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _arg_for(cls_name, pname, model):
    low = pname.lower()
    if low == "model":
        return model
    if low == "host":
        return extronlib_stub._Placeholder()          # a ProcessorDevice
    if low in ("hostname", "ipaddress"):
        return "192.0.2.1"                            # TEST-NET-1, never routed
    if low in ("ipport", "port"):
        serial = cls_name == "SerialClass"
        return "COM1" if serial else 5000
    if low in ("deviceusername", "username"):
        return "admin"
    if low in ("devicepassword", "password"):
        return "harness"
    if low == "sslverifymode":
        return "Off"
    if low == "credentials":
        return ("admin", "harness")
    return None


def construct(module, cls_name, model):
    cls = getattr(module, cls_name)
    kwargs = {}
    for p in list(inspect.signature(cls.__init__).parameters.values())[1:]:
        if p.kind in (p.VAR_POSITIONAL, p.VAR_KEYWORD):
            continue
        value = _arg_for(cls_name, p.name, model)
        if value is None and p.default is not p.empty and p.name.lower() != "model":
            continue                                  # the module's own default
        kwargs[p.name] = value
    sink = []
    _CURRENT_SINK[:] = []
    with contextlib.redirect_stdout(io.StringIO()):
        dev = cls(**kwargs)
    if not hasattr(dev, "_harness_sent"):
        dev._harness_sent = sink                      # HTTPClass: no interface base
    dev._harness_errors = []
    dev.Error = lambda message, _d=dev: _d._harness_errors.append(str(message)[:200])
    for flag in ("EchoDisabled", "VerboseDisabled"):
        if hasattr(dev, flag):
            setattr(dev, flag, False)                 # a device that has answered the handshake
    return dev


def open_side(path, name, cls_name=None, model=None):
    """Load, pick a transport class and model, construct. Returns a dict with
    either 'dev' or 'error'."""
    side = {"module": os.path.basename(path)}
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            module = load_module(path, name)
    except Exception as e:                            # noqa: BLE001
        side["error"] = dict(_describe(e, path), stage="import")
        return side
    side["mod"] = module
    side["classes"] = [c for c in TRANSPORT_ORDER if isinstance(getattr(module, c, None), type)]
    if cls_name is None:
        cls_name = side["classes"][0] if side["classes"] else None
    if cls_name is None:
        side["error"] = {"type": "NoTransportClass", "message": "none of %s" % (TRANSPORT_ORDER,),
                         "stage": "construct"}
        return side
    side["class"] = cls_name
    try:
        dev = construct(module, cls_name, model)
    except Exception as e:                            # noqa: BLE001
        side["error"] = dict(_describe(e, path), stage="construct")
        return side
    side["dev"] = dev
    side["models"] = list(getattr(dev, "Models", {}) or {})
    return side


# --------------------------------------------------------------------------
# Inputs, from the method bodies
# --------------------------------------------------------------------------

class Candidates:
    def __init__(self):
        self.values = []
        self.quals = {}

    @staticmethod
    def _add(seq, v):
        if not any(type(v) is type(x) and v == x for x in seq):
            seq.append(v)

    def add(self, target, v):
        if isinstance(v, bool) or not isinstance(v, (str, int, float)):
            return
        if target == "value":
            self._add(self.values, v)
        else:
            self._add(self.quals.setdefault(target[1], []), v)


def _target(node):
    """('value' | ('q', key), wrapped) for `value` / `qualifier['K']`, seen
    through int() / float() / str(); None otherwise."""
    wrapped = False
    while isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
            and node.func.id in ("int", "float", "str") and node.args:
        node = node.args[0]
        wrapped = True
    if isinstance(node, ast.Name) and node.id == "value":
        return "value", wrapped
    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
            and node.value.id == "qualifier" and isinstance(node.slice, ast.Constant):
        return ("q", node.slice.value), wrapped
    return None


def scan_method(source, cands):
    tree = ast.parse(textwrap.dedent(source))
    literals = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                and isinstance(n.value, (ast.Dict, ast.List, ast.Tuple, ast.Set)):
            literals[n.targets[0].id] = n.value

    def keys_of(node):
        if isinstance(node, ast.Name):
            node = literals.get(node.id)
        if isinstance(node, ast.Dict):
            return [k.value for k in node.keys if isinstance(k, ast.Constant)]
        if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
            return [e.value for e in node.elts if isinstance(e, ast.Constant)]
        return []

    def number(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) \
                and not isinstance(node.value, bool):
            return node.value
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            inner = number(node.operand)
            return -inner if inner is not None else None
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name) \
                and isinstance(node.slice, ast.Constant):
            d = literals.get(node.value.id)
            if isinstance(d, ast.Dict):
                for k, v in zip(d.keys, d.values):
                    if isinstance(k, ast.Constant) and k.value == node.slice.value:
                        return number(v)
        return None

    def add(tw, v):
        target, wrapped = tw
        if wrapped and isinstance(v, (int, float)):
            cands.add(target, str(int(v)) if float(v).is_integer() else str(v))
        cands.add(target, v)

    for n in ast.walk(tree):
        if isinstance(n, ast.Subscript):
            tw = _target(n.slice)
            if tw:
                for k in keys_of(n.value):
                    cands.add(tw[0], k)
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "get" and n.args:
            tw = _target(n.args[0])
            if tw:
                for k in keys_of(n.func.value):
                    cands.add(tw[0], k)
        elif isinstance(n, ast.Compare):
            operands = [n.left] + list(n.comparators)
            targets = [_target(o) for o in operands]
            for i, op in enumerate(n.ops):
                left, right = operands[i], operands[i + 1]
                tl, tr = targets[i], targets[i + 1]
                if isinstance(op, (ast.In, ast.NotIn)) and tl:
                    for k in keys_of(right):
                        cands.add(tl[0], k)
                elif isinstance(op, (ast.Eq, ast.NotEq)):
                    if tl and isinstance(right, ast.Constant):
                        cands.add(tl[0], right.value)
                    if tr and isinstance(left, ast.Constant):
                        cands.add(tr[0], left.value)
                elif isinstance(op, (ast.Lt, ast.LtE, ast.Gt, ast.GtE)):
                    for tw, other in ((tl, right), (tr, left)):
                        num = number(other) if tw else None
                        if num is not None:
                            for v in (num, num - 1, num + 1):
                                add(tw, v)


def method_source(dev, name):
    fn = getattr(type(dev), name, None)
    if fn is None:
        return None
    try:
        return inspect.getsource(fn)
    except (OSError, TypeError):
        return None


def build_inputs(cands, params, kind):
    params = list(params or [])
    base = {p: (cands.quals.get(p) or DEFAULT_QUALIFIER_VALUES)[0] for p in params} or None
    inputs = []
    if kind == "set":
        values = cands.values or DEFAULT_VALUES
        for v in values[:20] + ADVERSARIAL_VALUES:
            inputs.append((v, base))
        lead = values[0]
    else:
        inputs.append((None, base))
        lead = None
    for p in params:
        for c in (cands.quals.get(p) or DEFAULT_QUALIFIER_VALUES)[1:8] + [""]:
            q = dict(base)
            q[p] = c
            inputs.append((lead, q))
    seen, out = set(), []
    for v, q in inputs:
        key = repr((type(v).__name__, v, sorted((q or {}).items(), key=repr)))
        if key not in seen:
            seen.add(key)
            out.append((v, q))
    return out[:MAX_INPUTS]


# --------------------------------------------------------------------------
# Running
# --------------------------------------------------------------------------

def run_call(side, kind, cmd, value, qualifier):
    dev = side["dev"]
    del dev._harness_sent[:]
    del dev._harness_errors[:]
    _CURRENT_SINK[:] = []
    exc = None
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            if kind == "set":
                dev.Set(cmd, copy.deepcopy(value), copy.deepcopy(qualifier))
            else:
                dev.Update(cmd, copy.deepcopy(qualifier))
    except Exception as e:                            # noqa: BLE001
        exc = _describe(e, side.get("path"))
    sent = [data.hex() for _, data in list(dev._harness_sent) + list(_CURRENT_SINK)]
    return {"sent": sent, "discarded": bool(dev._harness_errors), "exc": exc}


def _same(a, b):
    return (a["sent"] == b["sent"] and a["discarded"] == b["discarded"]
            and (a["exc"] or {}).get("type") == (b["exc"] or {}).get("type"))


def _rejected(o):
    """Nothing sent, and the input was discarded or an exception escaped."""
    return not o["sent"] and (o["discarded"] or o["exc"] is not None)


def _example(value, qualifier, gen, ship):
    return {"value": repr(value), "qualifier": repr(qualifier),
            "generated": gen, "shipped": ship}


def compare_command(gen, ship, cmd, kind):
    # Both methods of the command, on both sides: an Update rarely validates
    # its qualifier, but the Set for the same command usually does, and the
    # qualifier keys are the same.
    cands = Candidates()
    for side in (ship, gen):
        for prefix in ("Set", "Update"):
            src = method_source(side["dev"], prefix + cmd)
            if src:
                try:
                    scan_method(src, cands)
                except SyntaxError:
                    pass
    params = []
    for side in (ship, gen):
        for p in (side["dev"].Commands.get(cmd) or {}).get("Parameters") or []:
            if p not in params:
                params.append(p)
    inputs = build_inputs(cands, params, kind)
    res = {"inputs": len(inputs), "same": 0, "both_reject": 0, "gen_raises": 0,
           "ship_raises": 0, "differ": 0, "examples": {}}
    for value, qualifier in inputs:
        g = run_call(gen, kind, cmd, value, qualifier)
        s = run_call(ship, kind, cmd, value, qualifier)
        if _same(g, s):
            res["same"] += 1
            continue
        if _rejected(g) and _rejected(s):
            # One discards, the other lets a ValueError escape: both refuse
            # the input. Counted, not scored as a difference.
            bucket = "both_reject"
        elif g["exc"] and not s["exc"]:
            bucket = "gen_raises"
        elif s["exc"] and not g["exc"]:
            bucket = "ship_raises"
        else:
            bucket = "differ"
        res[bucket] += 1
        ex = res["examples"].setdefault(bucket, [])
        if len(ex) < MAX_EXAMPLES:
            ex.append(_example(value, qualifier, g, s))
    return res


def _has(side, name):
    return callable(getattr(side["dev"], name, None))


def differential(gen_path, ship_path):
    extronlib_stub.install()
    _patch_process()
    out = {"generated": os.path.basename(gen_path), "shipped": os.path.basename(ship_path)}
    ship = open_side(ship_path, "harness_shipped")
    ship["path"] = ship_path
    gen_probe = open_side(gen_path, "harness_generated_probe")
    shared = [c for c in TRANSPORT_ORDER
              if c in ship.get("classes", []) and c in gen_probe.get("classes", [])]
    cls_name = shared[0] if shared else None
    model = None
    if "dev" in ship:
        if cls_name and ship["class"] != cls_name:
            ship = dict(open_side(ship_path, "harness_shipped2", cls_name), path=ship_path)
        gen_models = gen_probe.get("models") or []
        both = [m for m in ship.get("models") or [] if m in gen_models]
        model = both[0] if both else ((ship.get("models") or [None])[0])
        if model is not None and "dev" in ship:
            ship = dict(open_side(ship_path, "harness_shipped3", ship["class"], model),
                        path=ship_path)
    gen = dict(open_side(gen_path, "harness_generated", cls_name, model), path=gen_path)
    for label, side in (("generated", gen), ("shipped", ship)):
        out[label + "_class"] = side.get("class")
        if "error" in side:
            out[label + "_error"] = side["error"]
    out["model"] = model
    if "dev" not in gen or "dev" not in ship:
        return out
    gcmds = gen["dev"].Commands
    scmds = ship["dev"].Commands
    out["commands"] = {}
    for cmd in sorted(set(gcmds) & set(scmds)):
        entry = {}
        for kind, prefix in (("set", "Set"), ("update", "Update")):
            if _has(gen, prefix + cmd) and _has(ship, prefix + cmd):
                entry[kind] = compare_command(gen, ship, cmd, kind)
        if entry:
            out["commands"][cmd] = entry
    return out


def census(path):
    """One module, no reference: which inputs make an exception escape."""
    extronlib_stub.install()
    _patch_process()
    side = dict(open_side(path, "harness_module"), path=path)
    out = {"module": os.path.basename(path), "class": side.get("class")}
    if "error" in side:
        out["error"] = side["error"]
        return out
    out["commands"] = {}
    for cmd in sorted(side["dev"].Commands):
        entry = {}
        for kind, prefix in (("set", "Set"), ("update", "Update")):
            if not _has(side, prefix + cmd):
                continue
            cands = Candidates()
            src = method_source(side["dev"], prefix + cmd)
            if src:
                scan_method(src, cands)
            params = (side["dev"].Commands.get(cmd) or {}).get("Parameters") or []
            inputs = build_inputs(cands, params, kind)
            raised = []
            for value, qualifier in inputs:
                r = run_call(side, kind, cmd, value, qualifier)
                if r["exc"]:
                    raised.append({"value": repr(value), "qualifier": repr(qualifier),
                                   "exc": r["exc"]})
            entry[kind] = {"inputs": len(inputs), "raised": len(raised), "examples": raised[:2]}
        if entry:
            out["commands"][cmd] = entry
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--generated")
    ap.add_argument("--shipped")
    ap.add_argument("--module")
    args = ap.parse_args(argv)
    if args.module:
        result = census(args.module)
    elif args.generated and args.shipped:
        result = differential(args.generated, args.shipped)
    else:
        ap.error("give --module, or --generated and --shipped")
    sys.stdout.write(json.dumps(result, default=repr))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
