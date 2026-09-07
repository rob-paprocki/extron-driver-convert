#!/usr/bin/env python3
"""
pkp2cs.py - Extron .pkp -> ControlScript .py translator.

Pipeline
--------
1. EXTRACT  (uses pkp_dump.py as a library): parse the .pkp, pull every
   StreamResourceAsset embedded script, and read the DriverModelAsset tree
   to discover translation jobs (one per embedded script / transport).
2. ANALYSE: parse the embedded script with `ast`; locate the driver class,
   the `self.Commands` dict, `AddMatchString` calls, and the per-command
   method groups.
3. TRANSFORM: apply the rewrite rules derived from comparing embedded
   scripts to shipped ControlScript modules (see module docstring sections
   below and the project's findings/ docs).
4. EMIT: splice the transformed command block into the fixed runtime-shell
   template for the detected dialect (SIS-over-ethernet / binary-serial /
   HTTP), generate self.Models, and carry through device-specific state.
5. REPORT: a structured result with the generated module text plus a
   `residuals` list naming everything dropped or flagged, with a reason.

Python 3 standard library only.
"""
import ast
import copy
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pkp_dump  # noqa: E402


# ==========================================================================
# EXTRACT: .pkp -> translation jobs
# ==========================================================================

def deref(objs, ref):
    """Follow one {'$ref': id} indirection against the raw (unresolved)
    PkpParser.objects table. Passing through anything else unchanged."""
    if isinstance(ref, dict) and "$ref" in ref:
        return objs.get(ref["$ref"])
    return ref


def _collection_items(objs, coll):
    """coll is a raw ObservableCollection dict (members: _monitor,
    'Collection`1+items' -> a List`1 dict (members: _items, _size)) ->
    return the list's items (each still possibly a $ref)."""
    if not isinstance(coll, dict):
        return []
    lst = deref(objs, coll.get("members", {}).get("Collection`1+items"))
    if not isinstance(lst, dict):
        return []
    arr = deref(objs, lst.get("members", {}).get("_items"))
    if not isinstance(arr, dict):
        return []
    size = lst.get("members", {}).get("_size")
    items = arr.get("items", [])
    if size is not None:
        items = items[:size]
    return items


def child_collection_items(objs, asset):
    """Every AssetBase-derived node carries its children in
    `_internalChildCollection` / `AssetBase+_internalChildCollection`, an
    ObservableCollection<IAsset>. Returns the dereferenced immediate
    children (still possibly generic AssetBase`1[[...]] wrapper nodes)."""
    if not isinstance(asset, dict):
        return []
    m = asset.get("members", {})
    coll = deref(objs, m.get("_internalChildCollection") or
                 m.get("AssetBase+_internalChildCollection"))
    return [deref(objs, it) for it in _collection_items(objs, coll)]


def unwrap_generic_wrapper(objs, node, _depth=0):
    """NRBF serializes each strongly-typed child slot (IDriverCommandAsset,
    IParamAsset, IProtocolAsset, IDriverModelAsset, ...) as an intermediate
    'Extron.Configuration.Core.Assets.AssetBase`1[[I<X>Asset, ...]]' wrapper
    object whose own child collection holds exactly one concrete asset.
    Drill through those wrappers to the concrete asset."""
    if _depth > 8 or not isinstance(node, dict):
        return node
    cls = node.get("class", "")
    if cls.startswith("Extron.Configuration.Core.Assets.AssetBase`1[["):
        kids = child_collection_items(objs, node)
        if len(kids) == 1:
            return unwrap_generic_wrapper(objs, kids[0], _depth + 1)
        return None
    return node


def find_protocol_asset(objs, model):
    """A DriverModelAsset owns exactly one ProtocolAsset child (per
    findings/06). Return its concrete (unwrapped) dict, or None."""
    for wrapper in child_collection_items(objs, model):
        concrete = unwrap_generic_wrapper(objs, wrapper)
        if isinstance(concrete, dict) and concrete.get("class", "").endswith("ProtocolAsset"):
            return concrete
    return None


class ModelInfo:
    def __init__(self, name, script_file_name, script_class_name, protocol_class):
        self.name = name
        self.script_file_name = script_file_name
        self.script_class_name = script_class_name
        self.protocol_class = protocol_class

    def __repr__(self):
        return "ModelInfo(%r, %r, %r, %r)" % (
            self.name, self.script_file_name, self.script_class_name, self.protocol_class)


class TranslationJob:
    """One embedded script (== one transport) plus the DriverModelAssets
    that reference it."""
    def __init__(self, script_file_name, source, models):
        self.script_file_name = script_file_name
        self.source = source
        self.models = models  # list[ModelInfo], in DriverModelAsset discovery order

    def __repr__(self):
        return "TranslationJob(%r, models=%r)" % (self.script_file_name, self.models)


def _extract_stream_scripts(objs):
    """{key(.py filename): source text} for every StreamResourceAsset,
    deduplicated by (key, content bytes)."""
    out = {}
    seen = set()
    for v in objs.values():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Core.Assets.Resource.StreamResourceAsset"):
            continue
        members = v.get("members", {})
        key = deref(objs, members.get("ResourceAssetBase+_key"))
        if not (isinstance(key, str) and key.endswith(".py")):
            continue
        content_obj = deref(objs, members.get("ResourceAssetBase+_content"))
        if not (isinstance(content_obj, dict) and content_obj.get("$type") == "ArraySinglePrimitive"):
            continue
        data_bytes = bytes(content_obj["items"])
        dedup_key = (key, data_bytes)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        text = data_bytes.decode("utf-8")
        out_key = key
        n = 1
        while out_key in out:
            n += 1
            out_key = "%s.%d" % (key, n)
        out[out_key] = text
    return out


def discover_jobs(pkp_path):
    """EXTRACT step. Returns list[TranslationJob], one per unique embedded
    script (== one transport family), each carrying the DriverModelAssets
    that point at it (in package discovery order)."""
    data = pkp_dump.load_bytes(pkp_path)
    parser = pkp_dump.PkpParser(data).parse()
    objs = parser.objects

    scripts = _extract_stream_scripts(objs)

    models_by_script = {}
    order = []
    for oid, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Drivers.DriverModelAsset"):
            continue
        m = v.get("members", {})
        name = deref(objs, m.get("AssetBase+_name"))
        sfn = deref(objs, m.get("_scriptFileName"))
        scn = deref(objs, m.get("_scriptClassName"))
        proto = find_protocol_asset(objs, v)
        proto_class = proto.get("class") if isinstance(proto, dict) else None
        if not isinstance(sfn, str):
            continue
        info = ModelInfo(name, sfn, scn, proto_class)
        if sfn not in models_by_script:
            models_by_script[sfn] = []
            order.append(sfn)
        models_by_script[sfn].append(info)

    jobs = []
    for sfn in order:
        source = scripts.get(sfn)
        if source is None:
            # StreamResourceAsset missing for a referenced script name -- report
            # via a job with no source; caller surfaces this as a hard failure.
            source = None
        jobs.append(TranslationJob(sfn, source, models_by_script[sfn]))
    return jobs


# ==========================================================================
# ANALYSE + TRANSFORM helpers
# ==========================================================================

# 'UserDefinedCommand' / 'UserDefinedString' are a raw-passthrough command
# pair (their Set methods hand an unvalidated, hand-typed wire string
# straight to the device). They are consistently present in the .pkp's
# self.Commands dict (file-level AND every DriverModelAsset's own pruned
# per-model command list -- confirmed by direct NRBF inspection, so this is
# NOT the "orphan"/pruning issue findings/06 describes for other commands)
# yet are just as consistently absent from every shipped ControlScript
# module examined (DSC, Samsung); the DSC embedded script even carries a
# duplicated `_cmd_SetUserDefinedCommand` definition and a
# `self.__SetHelper_Sync(...)` call with no equivalent anywhere else in the
# codebase. Treated here as a confirmed, evidence-backed Extron editorial
# omission (an "own inconsistency" per the project's ACCEPTANCE PRINCIPLE),
# not something derivable from the .pkp -- dropped and reported.
ALWAYS_DROPPED_COMMAND_NAMES = {"UserDefinedCommand", "UserDefinedString"}

GC_ONLY_DROP_METHOD_NAMES = {
    "__SafeToSet", "WriteStatusHelper", "ReadStatusHelper",
    "_cmd_SetSyncEmulatedStatus", "StatusRefresh", "__ResetLiveStatus",
    "SendAndWait", "Send", "__ResponseTimeout",
}

# name-mangled forms as they'd appear if the source ever wrote them fully
# qualified (defensive; ast.parse does not mangle attribute access).


def _is_docstring_stmt(stmt):
    return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
            and isinstance(stmt.value.value, str))


def _call_attr(node):
    """If node is a Call to `self.<attr>(...)` (or `<anything>.<attr>(...)`),
    return attr, else None."""
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _is_self_attr(node, name):
    return (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
            and node.value.id == "self" and node.attr == name)


def _const_eq(node, value):
    return isinstance(node, ast.Constant) and node.value == value


class Residuals(list):
    def add(self, reason, detail=""):
        self.append({"reason": reason, "detail": detail})


class GenericBodyRewriter(ast.NodeTransformer):
    """The per-statement/per-call rewrite rules that apply uniformly to
    every surviving method body, command or helper, inside or outside the
    marker region. See module docstring / findings for the evidence behind
    each rule."""

    def __init__(self, model_class_to_name, current_method_name, residuals):
        self.model_class_to_name = model_class_to_name
        self.current_method_name = current_method_name
        self.residuals = residuals

    # -- statement-level rules (return None/[] to drop, a list to splice) --

    def visit_If(self, node):
        self.generic_visit(node)

        # if self.__SafeToSet('X'): <body incl. Emulated pre-write + real call>
        if _call_attr(node.test) == "__SafeToSet":
            if node.orelse:
                # Not observed in any oracle (the else always binds to an
                # outer 'if value in ValueStateValues:' guard, never to this
                # one) -- leave untouched rather than guess.
                self.residuals.add("unresolved-safetoset-with-else",
                                    "%s: 'if self.__SafeToSet(...):' has an else clause; "
                                    "left unrewritten (no oracle evidence for this shape)"
                                    % self.current_method_name)
                return node
            new_body = []
            for stmt in node.body:
                if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                        and isinstance(stmt.value.func, ast.Attribute)
                        and stmt.value.func.attr.startswith("Write")
                        and stmt.value.args and _const_eq(stmt.value.args[-1], "Emulated")):
                    self.residuals.add(
                        "gc-dual-status-emulated-prewrite-dropped",
                        "%s: dropped Emulated pre-write %s(...)" %
                        (self.current_method_name, stmt.value.func.attr))
                    continue
                new_body.append(stmt)
            return new_body

        # if self.RequiredTimer: self.RequiredTimer.DeleteTimer()
        if (_is_self_attr(node.test, "RequiredTimer") and not node.orelse
                and all(self._is_timer_cleanup(s) for s in node.body)):
            self.residuals.add(
                "gc-dual-status-requiredtimer-dropped",
                "%s: dropped RequiredTimer cleanup guard" % self.current_method_name)
            return []

        # if self.__SetHelper(...): <RequiredTimer/lastX bookkeeping> ->
        # bare call statement (ControlScript's helpers return nothing to
        # gate on; the guarded body is always GC dual-status timer upkeep).
        if _call_attr(node.test) in ("__SetHelper", "__UpdateHelper") and not node.orelse:
            self.residuals.add(
                "gc-dual-status-timer-body-dropped",
                "%s: flattened 'if self.%s(...):' guard, dropping its body"
                % (self.current_method_name, _call_attr(node.test)))
            return ast.Expr(value=node.test)

        return node

    def _is_timer_cleanup(self, stmt):
        return (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                and _call_attr(stmt.value) == "DeleteTimer")

    def visit_Assign(self, node):
        self.generic_visit(node)
        for tgt in node.targets:
            if _is_self_attr(tgt, "RequiredTimer"):
                self.residuals.add("gc-dual-status-requiredtimer-dropped",
                                    "%s: dropped self.RequiredTimer assignment" % self.current_method_name)
                return None
            if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) \
                    and tgt.value.id == "self" and tgt.attr.startswith("last"):
                self.residuals.add("gc-scratch-timer-dropped",
                                    "%s: dropped self.%s (GC-only staleness/throttle timer)"
                                    % (self.current_method_name, tgt.attr))
                return None
        return node

    def visit_Expr(self, node):
        self.generic_visit(node)
        if isinstance(node.value, ast.Call):
            attr = _call_attr(node.value)
            if attr == "WriteDeviceResponseStatus":
                self.residuals.add("gc-dual-status-no-target",
                                    "%s: dropped WriteDeviceResponseStatus(...) call (no ControlScript equivalent)"
                                    % self.current_method_name)
                return None
            if attr in ("WriteStatusHelper", "ReadStatusHelper"):
                self.residuals.add("gc-dual-status-no-target",
                                    "%s: dropped %s(...) call (no ControlScript equivalent)"
                                    % (self.current_method_name, attr))
                return None
        return node

    # -- expression-level rules --

    def visit_Call(self, node):
        self.generic_visit(node)

        attr = _call_attr(node)

        # self.DriverCmd('Name', a, b, ...) -> self.Name(a, b, ...)
        if attr == "DriverCmd" and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            name = node.args[0].value
            return ast.Call(
                func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                    attr=name, ctx=ast.Load()),
                args=list(node.args[1:]), keywords=node.keywords)

        # self.Write<X>(value, qualifier, 'Live') -> self.WriteStatus('<X>', value, qualifier)
        if (attr and attr.startswith("Write") and attr not in ("WriteStatus", "WriteStatusHelper",
                                                                 "WriteDeviceResponseStatus")
                and len(node.args) >= 1 and _const_eq(node.args[-1], "Live")):
            x = attr[len("Write"):]
            value_arg = node.args[0]
            qualifier_arg = node.args[1] if len(node.args) > 2 else ast.Constant(value=None)
            return ast.Call(
                func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                    attr="WriteStatus", ctx=ast.Load()),
                args=[ast.Constant(value=x), value_arg, qualifier_arg], keywords=[])

        # isinstance(self, <ScriptClassName>) -> self.ModelName == '<display name>'
        if (isinstance(node.func, ast.Name) and node.func.id == "isinstance"
                and len(node.args) == 2 and isinstance(node.args[0], ast.Name)
                and node.args[0].id == "self" and isinstance(node.args[1], ast.Name)):
            cls_name = node.args[1].id
            if cls_name in self.model_class_to_name:
                return ast.Compare(
                    left=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                        attr="ModelName", ctx=ast.Load()),
                    ops=[ast.Eq()],
                    comparators=[ast.Constant(value=self.model_class_to_name[cls_name])])
            self.residuals.add("unresolved-isinstance-model-check",
                                "%s: isinstance(self, %s) has no matching DriverModelAsset; left as-is"
                                % (self.current_method_name, cls_name))
            return node

        # self.Discard('Invalid Command') -> self.Discard('Invalid Command for <Method>')
        if attr == "Discard" and len(node.args) == 1 and _const_eq(node.args[0], "Invalid Command"):
            return ast.Call(func=node.func,
                             args=[ast.Constant(value="Invalid Command for %s" % self.current_method_name)],
                             keywords=node.keywords)

        return node


_COMPOUND_BODY_FIELDS = ("body", "orelse", "finalbody")


def _ensure_nonempty_bodies(node):
    """After statement-dropping rewrites, a compound statement's body/else/
    finally clause can end up empty, which ast.unparse cannot render (and
    real Python does not allow). Insert `pass` wherever that happened."""
    for child in ast.walk(node):
        for field in _COMPOUND_BODY_FIELDS:
            if hasattr(child, field):
                val = getattr(child, field)
                if isinstance(val, list) and len(val) == 0 and _has_other_body_context(child, field):
                    setattr(child, field, [ast.Pass()])
    return node


def _has_other_body_context(node, field):
    """Only If/For/While/Try/With/FunctionDef/ClassDef etc. truly require a
    non-empty body; an empty `orelse` on an If/For/While/Try is valid Python
    (it just means no else clause) and must be left as [] rather than
    padded with a stray `pass` branch."""
    if field == "body":
        return isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.With,
                                  ast.FunctionDef, ast.AsyncFunctionDef,
                                  ast.ClassDef, ast.AsyncFor, ast.AsyncWith))
    return False


def strip_docstring(func):
    if func.body and _is_docstring_stmt(func.body[0]):
        func.body = func.body[1:]
    if not func.body:
        func.body = [ast.Pass()]
    return func


def transform_method(func, model_class_to_name, residuals, new_name=None):
    """Apply strip-docstring + GenericBodyRewriter to a copy of `func`,
    optionally renaming it. Returns the new FunctionDef."""
    func = copy.deepcopy(func)
    strip_docstring(func)
    name_for_messages = new_name or func.name
    rewriter = GenericBodyRewriter(model_class_to_name, name_for_messages, residuals)
    new_body = []
    for s in func.body:
        result = rewriter.visit(s)
        if result is None:
            continue
        if isinstance(result, list):
            new_body.extend(x for x in result if x is not None)
        else:
            new_body.append(result)
    func.body = new_body
    if not func.body:
        func.body = [ast.Pass()]
    for s in func.body:
        _ensure_nonempty_bodies(s)
    if new_name:
        func.name = new_name
    func.decorator_list = []
    ast.fix_missing_locations(func)
    return func


def unparse_method(func, indent=4):
    src = ast.unparse(func)
    return _reindent(src, indent)


def _reindent(src, spaces):
    pad = " " * spaces
    return "\n".join((pad + line if line.strip() else "") for line in src.splitlines())


# ==========================================================================
# ANALYSE: pull the driver class apart
# ==========================================================================

CONFIG_PARSE_SELF_ATTRS = None  # (kept for readability; classification is structural, see below)


class Analysis:
    def __init__(self):
        self.dialect = None            # 'sis_ethernet' | 'serial' | 'http'
        self.base_class_name = None
        self.subclass_names = []       # additional DriverModelAsset script class names present as subclasses
        self.commands = {}             # name -> {'set':bool,'update':bool,'parameters':[...] or None}
        self.command_order = []
        self.addmatchstring_srcs = []  # source text of each 'self.AddMatchString(...)' call, in order
        self.init_extra_stmts = []     # ast statements to carry through into the emitted __init__
        self.has_verbose_echo = False
        self.methods = {}              # final_name -> ast.FunctionDef (already transformed)
        self.method_order = []         # command-group ordering hint: list of (sort_key, final_name)
        self.leftover_methods = []     # final names of methods with no recognised command group
        self.residuals = Residuals()
        self.http_helper_sig = None    # ('url_kw', 'data_kw') detection aid, unused for now


def _find_driver_class(tree):
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            if "BaseDriver" in bases or "HTTPDriver" in bases:
                return node, bases
    raise ValueError("no class deriving from BaseDriver/HTTPDriver found")


def _find_subclasses(tree, base_name):
    out = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            bases = [b.id for b in node.bases if isinstance(b, ast.Name)]
            if base_name in bases:
                out.append(node)
    return out


def _parse_commands_dict(init_func):
    for stmt in ast.walk(init_func):
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and _is_self_attr(stmt.targets[0], "Commands") and isinstance(stmt.value, ast.Dict):
            raw = ast.literal_eval(stmt.value)
            return raw
    return None


def _collect_addmatchstrings(init_func):
    calls = []
    for node in ast.walk(init_func):
        if isinstance(node, ast.Call) and _call_attr(node) == "AddMatchString":
            calls.append(node)
    return calls


def _is_config_parse_stmt(stmt):
    """True for GC-only self.Configuration/... parsing boilerplate: any
    statement that is, or is inside, a try/except touching `configs[...]`,
    the initError list, or the platform/minimumVersion SSH-interface gate."""
    src_nodes = [stmt]
    for n in ast.walk(stmt):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id == "configs":
            return True
        if isinstance(n, ast.Name) and n.id == "initError":
            return True
        if isinstance(n, ast.Name) and n.id in ("minimumVersion", "platform", "Version"):
            return True
    return False


def _is_addmatchstring_wrapper_if(stmt):
    """`if self.Unidirectional == 'False':` / `elif ...:` wrapping the
    AddMatchString registrations."""
    if not isinstance(stmt, ast.If):
        return False
    for n in ast.walk(stmt.test):
        if isinstance(n, ast.Attribute) and n.attr == "Unidirectional":
            return True
    return False


def _is_write_read_wrapper(func, commands):
    """A per-command Write<X>/Read<X> wrapper def: exists only to call
    WriteStatusHelper/ReadStatusHelper, always deleted."""
    name = func.name
    for prefix, target_attr in (("Write", "WriteStatusHelper"), ("Read", "ReadStatusHelper")):
        if name.startswith(prefix) and name not in ("WriteStatus", "ReadStatus",
                                                      "WriteStatusHelper", "ReadStatusHelper",
                                                      "WriteDeviceResponseStatus"):
            x = name[len(prefix):]
            if x in commands:
                for n in ast.walk(func):
                    if _call_attr(n) == target_attr:
                        return True
    return False


def _detect_dialect(base_class_name, bases):
    if "HTTPDriver" in bases:
        return "http"
    return None  # resolved later once we see the transport (serial vs ethernet)


def analyse(source, models):
    """ANALYSE + most of TRANSFORM. `models` is the job's list[ModelInfo]
    (used to build the isinstance -> ModelName rewrite table and to name
    the self.Models stub methods)."""
    a = Analysis()
    tree = ast.parse(source)
    cls, bases = _find_driver_class(tree)
    a.base_class_name = cls.name
    is_http = "HTTPDriver" in bases

    subclasses = _find_subclasses(tree, cls.name)
    a.subclass_names = [s.name for s in subclasses]
    for sub in subclasses:
        extra = [s for s in sub.body if not (
            isinstance(s, ast.FunctionDef) and s.name == "__init__" and
            len(s.body) == 1 and isinstance(s.body[0], ast.Expr) and
            isinstance(s.body[0].value, ast.Call) and
            isinstance(s.body[0].value.func, ast.Attribute) and s.body[0].value.func.attr == "__init__"
        )]
        if extra:
            a.residuals.add("model-subclass-has-extra-logic",
                             "%s: subclass body has content beyond super().__init__(configs); "
                             "only the ModelName stub was generated, extra logic dropped" % sub.name)

    # protocol family, used to pick the mixin template
    proto_classes = {m.protocol_class for m in models if m.protocol_class}
    if is_http:
        a.dialect = "http"
    elif any(p and p.endswith("SerialProtocolAsset") for p in proto_classes):
        a.dialect = "serial"
    elif any(p and p.endswith("EthernetProtocolAsset") for p in proto_classes):
        a.dialect = "sis_ethernet"
    else:
        a.dialect = "sis_ethernet"
        a.residuals.add("dialect-transport-not-evidenced",
                         "no ProtocolAsset class matched a known transport; defaulted to sis_ethernet")

    # model_class_to_name: scriptClassName -> DriverModelAsset display name
    model_class_to_name = {}
    for m in models:
        if m.script_class_name:
            model_class_to_name[m.script_class_name] = m.name
    a.model_class_to_name = model_class_to_name

    init_func = next((s for s in cls.body if isinstance(s, ast.FunctionDef) and s.name == "__init__"), None)
    if init_func is None:
        raise ValueError("driver class has no __init__")

    raw_commands = _parse_commands_dict(init_func) or {}
    for name, spec in raw_commands.items():
        if name in ALWAYS_DROPPED_COMMAND_NAMES:
            a.residuals.add("extron-editorial-omission",
                             "dropped command %r: consistently absent from shipped ControlScript "
                             "modules despite being present in the .pkp's file- and model-level "
                             "command registries; not derivable, treated as an Extron omission" % name)
            continue
        a.commands[name] = {
            "set": bool(spec.get("Set", False)),
            "update": bool(spec.get("Update", False)),
            "parameters": spec.get("Parameters"),
        }
        a.command_order.append(name)

    for call in _collect_addmatchstrings(init_func):
        a.addmatchstring_srcs.append("self.AddMatchString(%s)" %
                                      ", ".join(ast.unparse(arg) for arg in call.args))

    # classify top-level __init__ statements (outside the Commands assign
    # and the AddMatchString-registration if/elif block)
    for stmt in init_func.body:
        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) \
                and isinstance(stmt.value.func, ast.Attribute) and stmt.value.func.attr == "__init__" \
                and isinstance(stmt.value.func.value, ast.Call):
            continue  # super().__init__(configs)
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and _is_self_attr(stmt.targets[0], "Commands"):
            continue  # handled separately
        if _is_addmatchstring_wrapper_if(stmt):
            continue  # handled separately
        if _is_config_parse_stmt(stmt):
            a.residuals.add("gc-config-parsing-dropped",
                             "__init__: dropped GC configs[...]/initError statement: %s"
                             % ast.unparse(stmt).strip().splitlines()[0])
            continue
        if isinstance(stmt, ast.If) and isinstance(stmt.test, ast.Compare) \
                and isinstance(stmt.test.left, ast.Attribute) and stmt.test.left.attr == "InterfaceType":
            a.residuals.add("gc-platform-version-gate-dropped",
                             "__init__: dropped GC platform/minimumVersion SSHInterface gate")
            continue
        if isinstance(stmt, ast.Assign):
            dropped = False
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) \
                        and tgt.value.id == "self" and tgt.attr.startswith("last"):
                    a.residuals.add("gc-scratch-timer-dropped",
                                    "__init__: dropped self.%s (GC-only staleness/throttle timer)" % tgt.attr)
                    dropped = True
                if isinstance(tgt, ast.Attribute) and isinstance(tgt.value, ast.Name) \
                        and tgt.value.id == "self" and tgt.attr == "RequiredTimer":
                    a.residuals.add("gc-dual-status-requiredtimer-dropped",
                                    "__init__: dropped self.RequiredTimer init")
                    dropped = True
            if dropped:
                continue
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and _is_self_attr(stmt.targets[0], "EchoDisabled"):
            a.has_verbose_echo = True
        # everything else: carried through verbatim (generic transform applied at emit time)
        a.init_extra_stmts.append(stmt)

    # methods
    method_defs = [s for s in cls.body if isinstance(s, ast.FunctionDef) and s.name != "__init__"]
    for func in method_defs:
        name = func.name
        _dropped_cmd_match = re.match(r"^(?:_cmd_Set|_cmd_Update|__Match|Write|Read)([A-Za-z0-9]+)$", name)
        if _dropped_cmd_match and _dropped_cmd_match.group(1) in ALWAYS_DROPPED_COMMAND_NAMES:
            continue  # residual already recorded once, above, for the command itself
        if name in GC_ONLY_DROP_METHOD_NAMES:
            a.residuals.add("gc-dual-status-no-target",
                             "dropped %s (GC dual-status construct with no ControlScript target)" % name)
            continue
        body_src = ast.unparse(func)
        # NOTE: "ExtronTime" (bare, no trailing "(") deliberately matches the
        # isinstance(x, ExtronTime) type-check idiom used by __StatusItems, not
        # just ExtronTime(...) construction -- a prior version of this check
        # only matched "ExtronTime(" and missed that idiom, leaving
        # __StatusItems (a helper only ever called by the dropped
        # WriteStatusHelper/ReadStatusHelper) behind with a dangling reference
        # to a class (ExtronTime) that is correctly dropped elsewhere.
        if "Mutex(" in body_src or "PostNewStatusEx" in body_src or "ExtronTime" in body_src:
            a.residuals.add("gc-dual-status-no-target",
                             "dropped %s (references Mutex()/PostNewStatusEx/ExtronTime, no ControlScript target)"
                             % name)
            continue
        if _is_write_read_wrapper(func, a.commands):
            continue  # silently deleted per rewrite rules (not a residual: expected deletion)

        if name == "__MatchVerboseMode":
            new_func = ast.parse(
                "def __MatchVerboseMode(self, match, qualifier):\n"
                "    self.OnConnected()\n"
                "    self.VerboseDisabled = False\n"
            ).body[0]
            ast.fix_missing_locations(new_func)
            a.methods[name] = new_func
            a.method_order.append((("", "", 0), name))
            continue
        if name == "__MatchEchoMode":
            new_func = ast.parse(
                "def __MatchEchoMode(self, match, qualifier):\n"
                "    self.EchoDisabled = False\n"
            ).body[0]
            ast.fix_missing_locations(new_func)
            a.methods[name] = new_func
            a.method_order.append((("", "", 1), name))
            continue

        new_name = name
        sort_key = None
        m = re.match(r"^_cmd_(Set|Update)([A-Za-z0-9]+)$", name)
        if m:
            kind, x = m.groups()
            new_name = "%s%s" % (kind, x)
            sort_key = (x, "0" if kind == "Set" else "1")
        else:
            mm = re.match(r"^__Match([A-Za-z0-9]+)$", name)
            if mm and mm.group(1) in a.commands:
                sort_key = (mm.group(1), "2")
            else:
                # _cmd_<Name> for a bare (non-Set/Update) internal action, e.g.
                # Automate VX's `_cmd_TokenRequest` -- the shipped module
                # strips the `_cmd_` prefix here too (confirmed by source
                # diff), and `self.DriverCmd('TokenRequest', ...)` call sites
                # are already generically rewritten to `self.TokenRequest(...)`
                # elsewhere; without this branch the method stayed named
                # `_cmd_TokenRequest` while its callers were rewritten to call
                # `self.TokenRequest(...)`, an AttributeError at runtime.
                m3 = re.match(r"^_cmd_([A-Za-z0-9]+)$", name)
                if m3:
                    new_name = m3.group(1)

        transformed = transform_method(func, model_class_to_name, a.residuals, new_name=new_name)

        if name == "__MatchError":
            transformed.body.insert(0, ast.parse("self.counter = 0").body[0])
            ast.fix_missing_locations(transformed)
            a.methods[new_name] = transformed
            a.method_order.append((("~error", "", 0), new_name))
            continue

        a.methods[new_name] = transformed
        if sort_key:
            a.method_order.append((sort_key, new_name))
        else:
            a.leftover_methods.append(new_name)

    return a


# ==========================================================================
# EMIT
# ==========================================================================

FIXED_TAIL = '''    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)
'''

FIXED_STREAM_TAIL_EXTRA = '''
    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\\r\\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\\n Please provide a device{1} "
                   "and attempt again.\\n Ex: dvInterface.device{1} = '{1}'\\n Please "
                   "review the communication sheet.\\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')
'''

MIXIN_SSH = '''
class SSHClass(EthernetClientInterface, DeviceClass):
    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\\r\\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
'''

MIXIN_SERIAL = '''
class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\\r\\n')

    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\\r\\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
'''

MIXIN_HTTP = '''
class HTTPClass(DeviceClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None, SSLVerifyMode='Off'):
        DeviceClass.__init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.DefaultPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\\r\\n')

    def Discard(self, message):
        self.Error([message])
'''


def _fmt_commands_dict(a):
    lines = ["self.Commands = {"]
    lines.append("    'ConnectionStatus': {'Status': {}},")
    for name in a.command_order:
        spec = a.commands[name]
        if spec["parameters"]:
            lines.append("    %r: {'Parameters': %r, 'Status': {}}," % (name, spec["parameters"]))
        else:
            lines.append("    %r: {'Status': {}}," % name)
    lines.append("    }")
    return "\n".join(lines)


def _fmt_addmatchstrings(a):
    if not a.addmatchstring_srcs:
        return None
    lines = ["if self.Unidirectional == 'False':"]
    for src in a.addmatchstring_srcs:
        lines.append("    " + src)
    return "\n".join(lines)


def _ordered_final_methods(a):
    ordered = sorted(a.method_order, key=lambda kv: kv[0])
    names = [n for _, n in ordered] + a.leftover_methods
    return names


def _build_models_block(job, a):
    distinct = []
    seen = set()
    for m in job.models:
        if m.script_class_name not in seen:
            seen.add(m.script_class_name)
            distinct.append(m.script_class_name)
    if len(distinct) <= 1:
        return "self.Models = {}", []

    lines = ["self.Models = {"]
    stub_methods = []
    display_names_used = set()
    for m in job.models:
        if m.script_class_name in display_names_used:
            continue
        display_names_used.add(m.script_class_name)
        lines.append("    %r: self.%s," % (m.name, m.script_class_name))
        stub_methods.append(
            "def %s(self):\n    self.ModelName = %r\n" % (m.script_class_name, m.name))
    lines.append("    }")
    return "\n".join(lines), stub_methods


def emit(job, a):
    imports_extra = []
    header_lines = ["# Copyright 2026, Extron. All rights reserved."]
    if a.dialect == "http":
        header_lines += [
            "",
            "from extronlib.system import Wait, ProgramLog, GetUnverifiedContext",
            "import base64",
            "import urllib.error",
            "import urllib.request",
            "import json",
        ]
        init_sig = "def __init__(self, ipAddress, port, deviceUsername, devicePassword, SSLVerifyMode):"
    else:
        header_lines += [
            "",
            "from extronlib.interface import SerialInterface, EthernetClientInterface",
            "import re",
            "from extronlib.system import Wait, ProgramLog",
        ]
        init_sig = "def __init__(self):"

    body = []
    body.append("class DeviceClass:")
    body.append("    " + init_sig)
    if a.dialect == "http":
        body.append("")
        body.append("        self.Subscription = {}")
        body.append("        self.counter = 0")
        body.append("        self.connectionFlag = True")
        body.append("        self.initializationChk = True")
        body.append("        self.Debug = False")
        body.append("        self.IPAddress = ipAddress")
        body.append("        self.DefaultPort = port")
        body.append("")
        body.append("        self.Unidirectional = 'False'")
        body.append("        self.connectionCounter = 15")
        body.append("        self.DefaultResponseTimeout = 0.3")
        body.append("")
        body.append("        if SSLVerifyMode == 'Off':")
        body.append("            self._context = GetUnverifiedContext()")
        body.append("        else:")
        body.append("            self._context = None")
        body.append("")
        body.append("        self.RootURL = 'https://{0}:{1}/'.format(ipAddress, port)")
        body.append("        self.Opener = urllib.request.build_opener("
                     "urllib.request.HTTPBasicAuthHandler(), urllib.request.HTTPSHandler(context=self._context))")
        body.append("")
    else:
        body.append("")
        body.append("        self.Unidirectional = 'False'")
        body.append("        self.connectionCounter = 15")
        body.append("        self.DefaultResponseTimeout = 0.3")
        body.append("        self.Subscription = {}")
        body.append("        self.ReceiveData = self.__ReceiveData")
        body.append("        self.__receiveBuffer = b''")
        body.append("        self.__maxBufferSize = 2048")
        body.append("        self.__matchStringDict = {}")
        body.append("        self.counter = 0")
        body.append("        self.connectionFlag = True")
        body.append("        self.initializationChk = True")
        body.append("        self.Debug = False")

    models_src, model_stub_srcs = _build_models_block(job, a)
    body.append("        " + models_src)
    body.append("")
    body.append(_reindent(_fmt_commands_dict(a), 8))
    body.append("")

    # device-specific carried-through init state
    extra_ctx = Residuals()
    for stmt in a.init_extra_stmts:
        transformed = transform_method(
            ast.FunctionDef(name="__init__", args=ast.arguments(
                posonlyargs=[], args=[], vararg=None, kwonlyargs=[], kw_defaults=[],
                kwarg=None, defaults=[]), body=[stmt], decorator_list=[]),
            a.model_class_to_name, a.residuals, new_name=None)
        for s in transformed.body:
            body.append(_reindent(ast.unparse(s), 8))

    matchstrings_src = _fmt_addmatchstrings(a)
    if matchstrings_src:
        body.append("")
        body.append(_reindent(matchstrings_src, 8))

    body.append("")

    for name in _ordered_final_methods(a):
        body.append(unparse_method(a.methods[name], indent=4))
        body.append("")

    # OnConnected / OnDisconnected -- synthesized (no GC equivalent exists;
    # this is the minimal, evidence-backed universal form).
    body.append("    def OnConnected(self):")
    body.append("        self.connectionFlag = True")
    body.append("        self.WriteStatus('ConnectionStatus', 'Connected')")
    body.append("        self.counter = 0")
    body.append("")
    body.append("    def OnDisconnected(self):")
    body.append("        self.WriteStatus('ConnectionStatus', 'Disconnected')")
    body.append("        self.connectionFlag = False")
    if a.has_verbose_echo:
        body.append("")
        body.append("        self.EchoDisabled = True")
        body.append("        self.VerboseDisabled = True")
    a.residuals.add("onconnected-ondisconnected-synthesized",
                     "OnConnected/OnDisconnected are the minimal fixed template; any device-specific "
                     "state reset a hand-authored shipped module might add there was not derived "
                     "(not part of the wire-string acceptance surface)")
    body.append("")

    for stub_src in model_stub_srcs:
        body.append(_reindent(stub_src, 4))
        body.append("")

    body.append(FIXED_TAIL.rstrip("\n"))
    if a.dialect in ("sis_ethernet", "serial"):
        body.append(FIXED_STREAM_TAIL_EXTRA.rstrip("\n"))

    if a.dialect == "sis_ethernet":
        body.append(MIXIN_SSH.rstrip("\n"))
    elif a.dialect == "serial":
        body.append(MIXIN_SERIAL.rstrip("\n"))
        a.residuals.add("serial-over-ethernet-mixin-generalised",
                         "SerialOverEthernetClass is only evidenced by the single Samsung oracle; "
                         "emitting it for every 'serial' dialect job is a generalisation, not "
                         "independently confirmed")
    elif a.dialect == "http":
        body.append(MIXIN_HTTP.rstrip("\n"))

    text = "\n".join(header_lines) + "\n\n" + "\n".join(body) + "\n"
    return text


# ==========================================================================
# TOP LEVEL
# ==========================================================================

def translate_job(job):
    residuals = Residuals()
    if job.source is None:
        residuals.add("missing-embedded-script",
                       "DriverModelAsset(s) reference script %r but no matching StreamResourceAsset "
                       "was found in the package" % job.script_file_name)
        return {"script_file_name": job.script_file_name, "source": None, "residuals": residuals,
                "models": job.models}

    a = analyse(job.source, job.models)
    text = emit(job, a)
    residuals.extend(a.residuals)
    return {
        "script_file_name": job.script_file_name,
        "dialect": a.dialect,
        "source": text,
        "models": job.models,
        "commands": a.commands,
        "residuals": residuals,
    }


def translate_pkp(pkp_path):
    jobs = discover_jobs(pkp_path)
    return [translate_job(job) for job in jobs]


def main(argv=None):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pkp")
    ap.add_argument("-o", "--outdir", default=".")
    args = ap.parse_args(argv)

    results = translate_pkp(args.pkp)
    os.makedirs(args.outdir, exist_ok=True)
    for r in results:
        if r["source"] is None:
            print("SKIP %s: %s" % (r["script_file_name"], r["residuals"]), file=sys.stderr)
            continue
        out_path = os.path.join(args.outdir, r["script_file_name"])
        with open(out_path, "w") as f:
            f.write(r["source"])
        print("wrote %s (%d residuals)" % (out_path, len(r["residuals"])), file=sys.stderr)
        for res in r["residuals"]:
            print("  - [%s] %s" % (res["reason"], res["detail"]), file=sys.stderr)


if __name__ == "__main__":
    main()
