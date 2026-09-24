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
import collections
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


def find_protocol_assets(objs, model):
    """Every concrete ProtocolAsset* dict declared under `model`, in wrapper
    discovery order.

    findings/06 established "a DriverModelAsset owns exactly one ProtocolAsset
    child" and the original `find_protocol_asset` (singular, below) assumed
    it structurally: `unwrap_generic_wrapper` requires a wrapper's child
    collection to hold exactly one item, returning None otherwise. That
    assumption is false for a package where one model is wired for more than
    one physical connection -- evidenced directly by this repo's own
    `samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp`:
    both its models' single `AssetBase\\`1[[IProtocolAsset]]` wrapper holds
    TWO concrete children (an EthernetProtocolAsset AND a
    SerialProtocolAsset -- an IP/serial-selectable camera), not one. Against
    that shape the old function silently returned None, which is one
    confirmed, reproduced cause of ROADMAP R17's "3,455 of 8,027 models
    resolve to no protocol asset" finding (experiments/protocol_assets/
    SURVEY.md) despite no package lacking one. This function does not share
    the single-child assumption: it walks every wrapper's children, however
    many, drilling through any further nested generic wrapper, and returns
    every concrete node whose class ends in "ProtocolAsset". A model that
    genuinely declares none returns []."""
    out = []
    for wrapper in child_collection_items(objs, model):
        if not (isinstance(wrapper, dict) and wrapper.get("class", "").startswith(
                "Extron.Configuration.Core.Assets.AssetBase`1[[")):
            continue
        for kid in child_collection_items(objs, wrapper):
            concrete = kid
            if isinstance(concrete, dict) and concrete.get("class", "").startswith(
                    "Extron.Configuration.Core.Assets.AssetBase`1[["):
                concrete = unwrap_generic_wrapper(objs, concrete)
            if isinstance(concrete, dict) and concrete.get("class", "").endswith("ProtocolAsset"):
                out.append(concrete)
    return out


def find_protocol_asset(objs, model):
    """Back-compat single-asset accessor: the first concrete protocol asset
    declared under `model` (see find_protocol_assets), or None if the model
    declares none at all. Existing single-protocol-per-model callers (most
    of the corpus) see no change; a model declaring more than one asset now
    resolves to its first one instead of silently None."""
    assets = find_protocol_assets(objs, model)
    return assets[0] if assets else None


def enum_value(objs, ref):
    """Follow one $ref to an NRBF enum instance (a ClassWithId/
    ClassWithMembersAndTypes wrapping a single 'value__' member) and return
    its int, or None if the field is absent, null, or not an enum shape.
    Same method experiments/protocol_assets/survey.py uses to read
    `_compatibility`."""
    obj = deref(objs, ref)
    if isinstance(obj, dict) and "members" in obj and "value__" in obj.get("members", {}):
        return obj["members"]["value__"]
    return None


# Extron.Configuration.Contracts.Enumeration.ProtocolCompatibilityFlags, read by
# .NET reflection against the installed Extron.Configuration.Contracts.dll
# (experiments/protocol_assets/SURVEY.md, `Load-Package.ps1 -Protocol`,
# 15.45.0.0, 2026-09-23) -- ground truth, not inferred from port numbers or
# script content. The 4 mapped here are the compatibility values the corpus
# ever pairs with a real, nonzero socket endpoint (SURVEY.md's `_compatibility`
# table); 1024 (Ethernet_Dante) and 2048 (Ethernet_RoomScheduling) are
# deliberately absent -- both are always _port=0 corpus-wide, read there as an
# auxiliary-feature flag rather than this asset's own wire transport.
ETHERNET_COMPATIBILITY_PROTOCOL = {
    16: "TCP",    # Ethernet_Telnet
    32: "UDP",    # Ethernet_UDP
    64: "HTTP",   # Ethernet_HTTP (the http dialect's own HTTPDriver detection
                  # already covers this case end to end; kept here only so
                  # this table is a complete, honest record of what the enum
                  # values mean, not because EthernetClass/SSHClass emit it)
    512: "SSH",   # Ethernet_SSH
}
ETHERNET_COMPATIBILITY_NAME = {
    16: "Ethernet_Telnet", 32: "Ethernet_UDP", 64: "Ethernet_HTTP",
    512: "Ethernet_SSH", 1024: "Ethernet_Dante", 2048: "Ethernet_RoomScheduling",
}


def ethernet_protocol_info(objs, asset):
    """For a concrete EthernetProtocolAsset dict (see find_protocol_assets),
    read `_port` and `_compatibility` and resolve them to
    (protocol_string_or_None, port_or_None, compatibility_int_or_None).
    protocol_string is None when `_compatibility` is absent/unrecognised, or
    is one of the two "no real endpoint" flags (1024/2048 -- see
    ETHERNET_COMPATIBILITY_PROTOCOL). Returns None outright if `asset` is not
    an EthernetProtocolAsset at all."""
    if not (isinstance(asset, dict) and asset.get("class", "").endswith("EthernetProtocolAsset")):
        return None
    m = asset.get("members", {})
    port = m.get("_port")
    compat = enum_value(objs, m.get("_compatibility"))
    return ETHERNET_COMPATIBILITY_PROTOCOL.get(compat), port, compat


class ModelInfo:
    def __init__(self, name, script_file_name, script_class_name, protocol_class,
                 protocol_classes=None, ethernet_info=None):
        self.name = name
        self.script_file_name = script_file_name
        self.script_class_name = script_class_name
        self.protocol_class = protocol_class          # first declared asset's class, or None (back-compat)
        # every declared asset's class (see find_protocol_assets); a caller that only
        # passes protocol_class (the common case, and every pre-R17 call site) gets a
        # single-item list built from it rather than losing that evidence to [].
        self.protocol_classes = protocol_classes if protocol_classes is not None else (
            [protocol_class] if protocol_class else [])
        # (protocol_string_or_None, port_or_None, compatibility_int_or_None) from
        # the model's own EthernetProtocolAsset (see ethernet_protocol_info), or
        # None if it declares no EthernetProtocolAsset at all.
        self.ethernet_info = ethernet_info

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
        protos = find_protocol_assets(objs, v)
        proto_classes = [p.get("class") for p in protos if isinstance(p, dict) and p.get("class")]
        proto_class = proto_classes[0] if proto_classes else None
        eth_info = None
        for p in protos:
            info_tuple = ethernet_protocol_info(objs, p)
            if info_tuple is not None:
                eth_info = info_tuple
                break
        if not isinstance(sfn, str):
            continue
        info = ModelInfo(name, sfn, scn, proto_class, protocol_classes=proto_classes,
                          ethernet_info=eth_info)
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

    def __init__(self, model_class_to_name, current_method_name, residuals, commands=None):
        self.model_class_to_name = model_class_to_name
        self.current_method_name = current_method_name
        self.residuals = residuals
        self.commands = commands or {}

    # -- statement-level rules (return None/[] to drop, a list to splice) --

    def visit_If(self, node):
        self.generic_visit(node)

        # if self.__SafeToSet('X'): <body incl. real call> -- the Emulated
        # pre-write that used to sit in this body is stripped generically by
        # visit_Expr's call-shape rule (self.generic_visit(node) above has
        # already run over node.body by this point), regardless of guard
        # shape; nothing left to do here but unwrap the now-trivial guard.
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
            return node.body

        # if self.__SafeToSet('X') and <cond>: <body> [else: <body>] -- the
        # BoolOp form of the same guard (e.g. Automate VX's
        # 'if self.__SafeToSet(X) and value in ValueStateValues:'). __SafeToSet
        # is a trivial `return True` stub (GC_ONLY_DROP_METHOD_NAMES), so its
        # conjunct is always dropped; what happens to the *rest* of the test
        # is decided by whether GC's own if/else already has an orelse --
        # confirmed by diffing all 5 shipped Automate VX Set* methods that use
        # this shape: SetAutoSwitch/SetISORecording (GC has NO else) drop the
        # whole guard and call unconditionally; SetOutput/SetRecord/SetStream
        # (GC already has 'else: self.Discard(...)') keep 'if <cond>: ...
        # else: ...' with only the __SafeToSet(...) conjunct removed. This is
        # a syntactic signal already present in the GC source, not a guess.
        if (isinstance(node.test, ast.BoolOp) and isinstance(node.test.op, ast.And)
                and any(_call_attr(v) == "__SafeToSet" for v in node.test.values)):
            remaining = [v for v in node.test.values if _call_attr(v) != "__SafeToSet"]
            new_body = node.body  # Emulated pre-write already stripped by visit_Expr, if present
            if not node.orelse:
                if remaining:
                    self.residuals.add(
                        "gc-safetoset-boolop-guard-dropped",
                        "%s: 'if self.__SafeToSet(...) and %s:' had no else clause in GC's "
                        "source, matching Automate VX's shipped SetAutoSwitch/SetISORecording "
                        "shape -- the whole guard (not just __SafeToSet) is dropped, body "
                        "called unconditionally" % (self.current_method_name, ast.unparse(node.test)))
                return new_body
            new_test = remaining[0] if len(remaining) == 1 else ast.BoolOp(op=ast.And(), values=remaining)
            self.residuals.add(
                "gc-safetoset-boolop-guard-simplified",
                "%s: dropped the always-true self.__SafeToSet(...) conjunct from 'if ... and ...:', "
                "keeping the remaining condition and GC's own else clause (matches Automate VX's "
                "shipped SetOutput/SetRecord/SetStream shape)" % self.current_method_name)
            new_if = ast.If(test=new_test, body=new_body, orelse=node.orelse)
            ast.copy_location(new_if, node)
            return new_if

        # if ctime - self.lastXUpdate > 4: <body> [else: self.Discard(...)]
        # -- GC's query throttle. Every write of self.last* is dropped below
        # (gc-scratch-timer-dropped), so the guard was left reading an
        # attribute nothing sets: an AttributeError on every such Update,
        # found by executing DSC's generated module (ROADMAP R13). Extron's
        # shipped DSC keeps only the body. Rewritten only in that exact shape
        # - a single comparison, with no else or a lone Discard - because any
        # other else (avr's sequence reset) is real logic; those stay, and
        # find_unassigned_self_attributes reports them.
        if (isinstance(node.test, ast.Compare) and _reads_self_last(node.test)
                and (not node.orelse or (len(node.orelse) == 1
                                         and isinstance(node.orelse[0], ast.Expr)
                                         and _call_attr(node.orelse[0].value) == "Discard"))):
            self.residuals.add(
                "gc-throttle-guard-dropped",
                "%s: dropped GC's query throttle 'if %s:' and its Discard, keeping the body "
                "(the self.last* timer it reads is dropped; matches Extron's shipped DSC)"
                % (self.current_method_name, ast.unparse(node.test)))
            return node.body

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
            # self.lastXUpdate[channel] = ctime: the same timer, kept per
            # qualifier. Its dict's initialisation is dropped with the rest,
            # so the store raised AttributeError (18 of the 314 packages).
            if isinstance(tgt, ast.Subscript) and _reads_self_last(tgt.value) \
                    and isinstance(tgt.value, ast.Attribute):
                self.residuals.add("gc-scratch-timer-dropped",
                                    "%s: dropped self.%s[...] (GC-only staleness/throttle timer)"
                                    % (self.current_method_name, tgt.value.attr))
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
            # self.Write<X>(<args>, 'Emulated') -- GC's dual-status pre-write
            # bookkeeping call, wherever it appears in a method body. The
            # invariant is the CALL SHAPE, not the guard it happens to sit
            # inside: every shipped module (DSC/DTP3/Samsung/Automate
            # VX/Clock Audio/Biamp -- confirmed by grepping all six for
            # 'Emulated' and for any per-command def Write<X>/Read<X>, both
            # zero hits) defines only the generic WriteStatus/ReadStatus, so
            # a call to the per-command Write<X> wrapper (already deleted
            # elsewhere as pure boilerplate -- see the wrapper-drop rules)
            # is always dangling if it survives. The old rule only stripped
            # this inside an 'if self.__SafeToSet(...):' body; Biamp's Tesira
            # generator never emits __SafeToSet at all and gates the same
            # bookkeeping call on plain parameter validation instead (e.g.
            # 'if 1 <= int(chnl) <= 24 and value in state:'), and DTP3's own
            # SetMatrixIONameString/SetMatrixIONumberSelect do the identical
            # thing with a length check -- so gating this rule on the
            # __SafeToSet guard shape was itself a second special case.
            # Excludes WriteStatus/WriteStatusHelper/WriteDeviceResponseStatus
            # (handled by their own rules above/elsewhere) and, by requiring
            # the literal 'Emulated' last argument, never fires on a
            # 'Live' (or contextless) Write<X> call -- that's the B1
            # Write<X>(...,'Live') -> WriteStatus(...) rewrite rule's job --
            # nor on a Read<X>(..., 'Emulated') call, which reads GC-only
            # scratch state and has its return value consumed (a different
            # construct entirely; left as a reported residual, never guessed
            # at).
            if (attr and attr.startswith("Write")
                    and attr not in ("WriteStatus", "WriteStatusHelper", "WriteDeviceResponseStatus")
                    and _has_emulated_context(node.value)):
                self.residuals.add(
                    "gc-dual-status-emulated-prewrite-dropped",
                    "%s: dropped Emulated pre-write %s(...)" %
                    (self.current_method_name, attr))
                return None
            # self.StartQueryDelayTimer(...) -- GC BaseDriver's own
            # query-throttle bookkeeping, no ControlScript equivalent no
            # matter which method calls it. __SetHelper/__UpdateHelper get
            # their own fixed-template replacement (see
            # gc-sethelper-updatehelper-fixed-template) which already drops
            # this; this rule catches the same call appearing anywhere else
            # (evidenced by DTP3's _cmd_SetMatrixIONameStatus, an internal
            # query-composition helper that isn't itself __SetHelper/
            # __UpdateHelper).
            if attr == "StartQueryDelayTimer":
                self.residuals.add("gc-query-throttle-dropped",
                                    "%s: dropped self.StartQueryDelayTimer(...) call (GC-only "
                                    "query-throttle bookkeeping, no ControlScript target)"
                                    % self.current_method_name)
                return None
        return node

    # -- expression-level rules --

    def visit_Attribute(self, node):
        self.generic_visit(node)
        # self._cmd_X read as a value, not called: nec's __init__ builds a
        # dispatch table {'DeviceStatus': self._cmd_UpdateDeviceStatus}. The
        # def is renamed (_cmd_ stripped) and visit_Call renames calls, but a
        # reference was left on the old name - an AttributeError while the
        # class was still being constructed (found by executing it, R13).
        if (node.attr.startswith("_cmd_") and isinstance(node.value, ast.Name)
                and node.value.id == "self" and isinstance(node.ctx, ast.Load)):
            return ast.copy_location(
                ast.Attribute(value=node.value, attr=node.attr[len("_cmd_"):], ctx=node.ctx),
                node)
        return node

    def visit_Call(self, node):
        self.generic_visit(node)

        attr = _call_attr(node)

        # self.Send(data, pacing=0.1): GC's BaseDriver paces queued sends;
        # extronlib's Send takes data alone (and SendAndWait only delimiter
        # keywords), so the call raised TypeError - DTP3's
        # RefreshMatrixIONames, found by executing it (R13). Extron's shipped
        # DTP3 sends without it. 5 of the 314 packages pass pacing.
        if attr in ("Send", "SendAndWait") and isinstance(node.func.value, ast.Name) \
                and node.func.value.id == "self" \
                and any(k.arg == "pacing" for k in node.keywords):
            self.residuals.add(
                "gc-send-pacing-dropped",
                "%s: dropped pacing= from self.%s(...) - a GC BaseDriver option extronlib "
                "does not take; any delay the device needs between these sends is lost"
                % (self.current_method_name, attr))
            node.keywords = [k for k in node.keywords if k.arg != "pacing"]

        # self.DriverCmd('Name', a, b, ...) -> self.Name(a, b, ...)
        if attr == "DriverCmd" and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str):
            name = node.args[0].value
            return ast.Call(
                func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                    attr=name, ctx=ast.Load()),
                args=list(node.args[1:]), keywords=node.keywords)

        # self._cmd_X(...) / self._cmd_SetX(...) / self._cmd_UpdateX(...) --
        # a *direct* call-by-old-name to a def that gets the same "_cmd_"
        # prefix stripped wherever it is defined (see the rename rules in
        # `analyse()`). Only the DriverCmd('X', ...) call form was rewritten
        # here before; a direct self._cmd_X(...) call site (evidenced by
        # DTP3's __MatchQik -> self._cmd_UpdateAllMatrixTie(...)) was left
        # pointing at a name that no longer exists once the def is renamed.
        # Stripping the literal "_cmd_" prefix is equivalent to the rename
        # table used for defs (same regex family), so this needs no lookup.
        if (attr and attr.startswith("_cmd_") and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "self"):
            new_attr = attr[len("_cmd_"):]
            return ast.Call(
                func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                    attr=new_attr, ctx=ast.Load()),
                args=node.args, keywords=node.keywords)

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

        # self.Read<X>(qualifier, 'Live') -> self.ReadStatus('<X>', qualifier)
        # -- the read-side symmetric counterpart of the Write<X> rule above.
        # Evidenced by shipped DTP3: self.ReadOutputTieStatus({...}, 'Live')
        # (a cross-command call to a Read wrapper deleted as a pure
        # status-accessor -- see _is_write_read_wrapper) becomes
        # self.ReadStatus('OutputTieStatus', {...}). Gated on the literal
        # 'Live' context (same shape the Write rule requires) AND on <X>
        # still being a live command: this is deliberately NOT the same as
        # "any Read<X> call", because MatrixIONameString/MatrixIONumberSelect
        # are called with an 'Emulated' context and are themselves commands
        # Extron folded/eliminated (Category B2, no ControlScript Set/Update
        # survives for them) -- rewriting those would silently read an
        # always-empty status instead of the honest AttributeError this
        # tool's whole-module dangling-call check exists to surface.
        if (attr and attr.startswith("Read") and attr not in ("ReadStatus", "ReadStatusHelper")
                and len(node.args) == 2 and _const_eq(node.args[1], "Live")):
            x = attr[len("Read"):]
            if x in self.commands:
                qualifier_arg = node.args[0]
                return ast.Call(
                    func=ast.Attribute(value=ast.Name(id="self", ctx=ast.Load()),
                                        attr="ReadStatus", ctx=ast.Load()),
                    args=[ast.Constant(value=x), qualifier_arg], keywords=[])

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


def transform_method(func, model_class_to_name, residuals, new_name=None, commands=None):
    """Apply strip-docstring + GenericBodyRewriter to a copy of `func`,
    optionally renaming it. Returns the new FunctionDef."""
    func = copy.deepcopy(func)
    strip_docstring(func)
    name_for_messages = new_name or func.name
    rewriter = GenericBodyRewriter(model_class_to_name, name_for_messages, residuals, commands=commands)
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
    # Python's own method decorators change how a method is called, so dropping
    # them is a runtime bug neither the wire table nor the resolvability checks
    # can see: ktek's DM8000 calls self.__check_instance_tag(tag) on a
    # @staticmethod, which without the decorator receives self as the tag.
    # The corpus uses only staticmethod (23 methods in 15 packages) and property
    # (1); anything else is not evidenced, so it is reported, not kept.
    kept = []
    for d in func.decorator_list:
        if _is_builtin_method_decorator(d):
            kept.append(d)
        else:
            residuals.add("method-decorator-dropped",
                          "%s: dropped decorator @%s (not one of Python's own method "
                          "decorators; no rule maps it)" % (name_for_messages, ast.unparse(d)))
    func.decorator_list = kept
    ast.fix_missing_locations(func)
    return func


def _reads_self_last(node):
    """True if the expression reads a self.last* attribute - GC's scratch
    timers, every write of which the translation drops."""
    return any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
               and n.value.id == "self" and n.attr.startswith("last")
               for n in ast.walk(node))


def _helper_calls_needing_more(method_defs, name):
    """{name} if any method calls self.<name>(...) with more than the fixed
    template's four arguments (or any keyword argument), else an empty set."""
    for f in method_defs:
        for n in ast.walk(f):
            if isinstance(n, ast.Call) and _call_attr(n) == name \
                    and (len(n.args) > 4 or n.keywords
                         or any(isinstance(x, ast.Starred) for x in n.args)):
                return {name}
    return set()


def _extra_helper_params(func):
    """The parameters a GC __SetHelper/__UpdateHelper declares beyond
    (self, command, commandstring, value, qualifier), as source text with
    their defaults: ['queryDisallowTime=0']."""
    a = func.args
    pos = a.posonlyargs + a.args
    first_default = len(pos) - len(a.defaults)
    out = []
    for i, p in enumerate(pos[5:], start=5):
        out.append(p.arg if i < first_default
                   else "%s=%s" % (p.arg, ast.unparse(a.defaults[i - first_default])))
    if a.vararg:
        out.append("*" + a.vararg.arg)
    elif a.kwonlyargs:
        out.append("*")
    for p, d in zip(a.kwonlyargs, a.kw_defaults):
        out.append(p.arg if d is None else "%s=%s" % (p.arg, ast.unparse(d)))
    if a.kwarg:
        out.append("**" + a.kwarg.arg)
    return out


def _is_builtin_method_decorator(d):
    """staticmethod / classmethod / property, or a property's .setter /
    .getter / .deleter."""
    if isinstance(d, ast.Name):
        return d.id in ("staticmethod", "classmethod", "property")
    return isinstance(d, ast.Attribute) and d.attr in ("setter", "getter", "deleter")


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
        self.onconnected_extra_stmts = []    # genuine device-state statements from GC's OnConnected
        self.ondisconnected_extra_stmts = [] # genuine device-state statements from GC's OnDisconnected
        self.needs_fixed_set_update_helper = False  # __SetHelper/__UpdateHelper replaced by fixed template
        self.http_helper_sig = None    # ('url_kw', 'data_kw') detection aid, unused for now
        self.needs_dual_transport_mixin = False  # model(s) declare both Serial and Ethernet (R17)
        self.needs_emulated_scratch_store = False  # a kept Read<X>/Write<X> wrapper needs self._emulated_status
        # R16: (protocol_string_or_None, port_or_None, compatibility_int_or_None) for the
        # EthernetClass/SSHClass mixin, or None if no model carries an EthernetProtocolAsset.
        self.ethernet_info = None
        # The source's own module-level imports, except the GC framework's
        # (Extron2.*), as source text: carried into the generated module so the
        # names they bind - pack, time, a bare `compile` from re - still resolve.
        self.carried_imports = []
        # The source's other top-level statements (helper classes, constants,
        # functions), as (after_driver_class, stmt), in source order. emit()
        # carries only the ones the generated module reads - see
        # _module_definitions_needed().
        self.module_stmts = []
        # name -> source text of the Extron/Extron2 import that binds it
        # (never carried), and the names bound only inside a top-level if/try
        # block (a platform gate, never carried): both explain a NameError
        # residual rather than resolve it.
        self.gc_import_names = {}
        self.conditional_names = set()
        # (lineno, source) of each __init__ local assignment an AddMatchString
        # call reads, e.g. `du_talk_status_regex = br'...'`; the registrations
        # are regenerated, so their locals must be too.
        self.addmatchstring_prelude = []
        self.addmatchstring_linenos = []
        # The driver class's own non-method statements (ktek's
        # `unwanted_chars = compile(...).search`, read as a later method's
        # default argument), carried to the top of DeviceClass.
        self.class_attr_stmts = []
        # __SetHelper / __UpdateHelper -> the source's parameters beyond
        # (command, commandstring, value, qualifier), kept in the fixed
        # template's signature.
        self.helper_extra_params = {}
        # Which SIS session flags the source itself sets, and the handshake
        # strings it sends ('w3cv\r' on some drivers, 'w3cv\r\n' on others).
        self.uses_echo = False
        self.uses_verbose = False
        self.sis_literals = {}


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


class UntranslatableDriver(Exception):
    """The embedded script is not in a shape this translator understands.

    Raised instead of degrading, because a driver emitted with a partial or
    empty command table looks plausible and controls nothing -- the worst
    failure mode available to this tool.
    """


def _parse_commands_dict(init_func):
    """Return the literal self.Commands dict, or raise UntranslatableDriver.

    Never returns None: an absent or dynamically-built Commands dict is a
    translation failure, not an empty driver.
    """
    found_assignment = False
    for stmt in ast.walk(init_func):
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 \
                and _is_self_attr(stmt.targets[0], "Commands"):
            found_assignment = True
            if isinstance(stmt.value, ast.Dict):
                try:
                    return ast.literal_eval(stmt.value)
                except ValueError as exc:
                    raise UntranslatableDriver(
                        "self.Commands is a dict literal but contains "
                        "non-literal entries: %s" % exc) from exc
    if found_assignment:
        raise UntranslatableDriver(
            "self.Commands is assigned but is not a literal dict "
            "(built dynamically?); the command table cannot be recovered "
            "statically")
    raise UntranslatableDriver(
        "no self.Commands assignment found in the driver __init__")


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


def _make_emulated_scratch_wrapper(name, wrapped, kind):
    """Build the kept, evidence-backed replacement body for a Write<X>/Read<X>
    wrapper over a Live=False/Emulated=True command that is still referenced
    from elsewhere (see the gc-emulated-wrapper-kept-as-scratch-store
    residual). A private per-module dict, keyed by command name, standing in
    for GC's own dropped WriteStatusHelper/ReadStatusHelper -- never
    ControlScript's WriteStatus/ReadStatus (the externally-visible Live
    store, the wrong target for a value GC itself never published)."""
    if kind == "Write":
        src = ("def %s(self, value, qualifier, context):\n"
               "    self._emulated_status[%r] = value\n" % (name, wrapped))
    else:
        src = ("def %s(self, qualifier, context):\n"
               "    return self._emulated_status.get(%r)\n" % (name, wrapped))
    new_func = ast.parse(src).body[0]
    ast.fix_missing_locations(new_func)
    return new_func


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

    # Module-level imports. The emitted header has always been a fixed list,
    # so a name the driver imported for itself was simply not there: pack in
    # every VISCA driver, time in others - a NameError on the processor that
    # neither the wire table nor the dangling self.X() check can see. Worse,
    # `from re import compile` was dropped while the calls stayed, so they
    # reached the builtin compile() instead of re.compile() and registered no
    # response pattern at all (found by ROADMAP R36). Carry every top-level
    # import except the GC runtime's own packages (Extron, Extron2), which do
    # not exist under ControlScript - extronlib replaces them, and carrying
    # them would trade a NameError for an ImportError. Anything imported
    # conditionally is reported, not guessed.
    subclasses = _find_subclasses(tree, cls.name)
    a.subclass_names = [s.name for s in subclasses]
    after_driver = False
    for node in tree.body:
        if node is cls:
            after_driver = True
            continue
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = ([al.name for al in node.names] if isinstance(node, ast.Import)
                    else [node.module or ""])
            if any(m.split(".")[0] in ("Extron", "Extron2") for m in mods):
                for al in node.names:
                    bound = al.asname or (al.name.split(".")[0]
                                          if isinstance(node, ast.Import) else al.name)
                    a.gc_import_names[bound] = ast.unparse(node)
                continue
            a.carried_imports.append(ast.unparse(node))
        elif isinstance(node, (ast.Try, ast.If)):
            a.conditional_names.update(_names_bound_by(node))
            if any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(node)):
                a.residuals.add("conditional-module-import-not-carried",
                                "a module-level import sits inside a %s block and was not "
                                "carried into the generated module" % type(node).__name__)
        elif isinstance(node, ast.ClassDef) and node in subclasses:
            continue
        elif isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
            continue  # a module or section docstring
        else:
            # Helper classes (Scroller, Directory), constants (a WebSocket
            # driver's FIN / OPCODE), module functions (_mask): plain Python the
            # driver's methods call. They were dropped wholesale, so every such
            # read became a NameError on the processor. Kept here; emit()
            # carries the ones the generated module actually reads.
            a.module_stmts.append((after_driver, node))
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

    # protocol family, used to pick the mixin template. Union of every
    # declared asset across every model (find_protocol_assets, R17): a model
    # can declare more than one (e.g. an IP/serial-selectable camera), and
    # using only the first-seen asset per model (the old `protocol_class`)
    # silently lost evidence of the others.
    proto_classes = {c for m in models for c in m.protocol_classes if c}
    for m in models:
        if not m.protocol_classes:
            a.residuals.add(
                "model-has-no-protocol-asset",
                "%s: no ProtocolAsset (Ethernet/Serial/CEC/...) found under this "
                "DriverModelAsset at all -- not a lookup failure (find_protocol_assets "
                "walked every declared child), a genuine absence in the package. This "
                "model's transport cannot be determined from its own graph; any "
                "dialect below was inferred from its SIBLING models or the script's own "
                "content instead." % (m.name or m.script_class_name or "<unnamed model>"))
    eth_infos = [m.ethernet_info for m in models if m.ethernet_info is not None]
    if eth_infos:
        a.ethernet_info = eth_infos[0]
        distinct = {t for t in eth_infos}
        if len(distinct) > 1:
            a.residuals.add(
                "model-ethernet-settings-differ",
                "this job's models declare different EthernetProtocolAsset "
                "(protocol, port, compatibility) tuples (%s); the first model's "
                "(%r) was used for the emitted EthernetClass/SSHClass -- verify "
                "by hand for any other model in self.Models"
                % (sorted(str(t) for t in distinct), a.ethernet_info))

    both_serial_and_ethernet = (
        not is_http
        and any(p and p.endswith("SerialProtocolAsset") for p in proto_classes)
        and any(p and p.endswith("EthernetProtocolAsset") for p in proto_classes))
    a.needs_dual_transport_mixin = both_serial_and_ethernet
    if both_serial_and_ethernet:
        # 1 Beyond PTZ-IP12/IP20 shape: one model, one embedded script, but
        # the script is wired for EITHER a direct IP connection or a direct
        # serial connection (an EnumParamAsset alongside the two protocol
        # assets almost certainly selects which). GC's BaseDriver abstracts
        # the transport behind self.Send()/self.ConnectionType, so the SAME
        # command logic below is not itself transport-specific -- only
        # __init__'s wiring class is. ControlScript already has precedent
        # for shipping more than one wiring class from one module (the
        # 'serial' dialect's SerialClass + SerialOverEthernetClass, below);
        # emit BOTH the ethernet and serial wiring classes here on the same
        # principle, rather than picking one per the old elif precedence and
        # silently dropping evidence of the other.
        a.residuals.add(
            "model-declares-multiple-transports",
            "declares both a SerialProtocolAsset and an EthernetProtocolAsset "
            "(%s); both EthernetClass/SSHClass and SerialClass/SerialOverEthernetClass "
            "wiring classes are emitted below so neither connection option is silently "
            "dropped, but this is evidenced only by the 1 Beyond PTZ-IP12/IP20 donor -- "
            "verify by hand that the shared command logic is genuinely transport-agnostic "
            "for any other package this fires on" % sorted(proto_classes))
    if is_http:
        a.dialect = "http"
    elif any(p and p.endswith("SerialProtocolAsset") for p in proto_classes):
        a.dialect = "serial"
    elif any(p and p.endswith("EthernetProtocolAsset") for p in proto_classes):
        # "SIS" is Extron's own protocol, not a synonym for Ethernet. Only use the
        # SIS handshake template when the package itself demonstrably speaks SIS.
        if _source_speaks_sis(source):
            a.dialect = "sis_ethernet"
        else:
            a.dialect = "ethernet"
            a.residuals.add("connection-handshake-not-translated",
                             "Ethernet device with no SIS handshake in its own script. The "
                             "Extron SIS echo/verbose handshake was NOT emitted (it would be "
                             "fabricated wire content for this device). If this device needs a "
                             "session-setup exchange, it must be added by hand.")
    else:
        a.dialect = "ethernet"
        a.residuals.add("dialect-transport-not-evidenced",
                         "no ProtocolAsset class matched a known transport; defaulted to plain "
                         "ethernet with no handshake rather than assuming SIS")

    # model_class_to_name: scriptClassName -> DriverModelAsset display name
    model_class_to_name = {}
    for m in models:
        if m.script_class_name:
            model_class_to_name[m.script_class_name] = m.name
    a.model_class_to_name = model_class_to_name

    init_func = next((s for s in cls.body if isinstance(s, ast.FunctionDef) and s.name == "__init__"), None)
    if init_func is None:
        raise ValueError("driver class has no __init__")

    raw_commands = _parse_commands_dict(init_func)
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
            # 'Live': False / 'Emulated': True together mark a GC command
            # with no ControlScript dual-status "Live" store at all -- an
            # Emulated-only scratch value. Evidenced identically across two
            # independent packages/dialects (DTP3's MatrixIONameString/
            # MatrixIONumberSelect, Samsung ethernet's MultiviewString) to
            # be exactly the commands Extron's shipped modules restructure
            # or drop entirely (see gc-emulated-only-command-wrapper-dropped
            # below); default True/False respectively so an absent key
            # (most commands) never matches this pattern.
            "live": bool(spec.get("Live", True)),
            "emulated": bool(spec.get("Emulated", False)),
        }
        a.command_order.append(name)

    matchstring_calls = _collect_addmatchstrings(init_func)
    for call in matchstring_calls:
        a.addmatchstring_srcs.append("self.AddMatchString(%s)" %
                                      ", ".join(ast.unparse(arg) for arg in call.args))
        a.addmatchstring_linenos.append(call.lineno)

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

    # The registrations are regenerated from their calls alone, so a local the
    # source assigned beside them was lost: ATUC50's
    # `du_talk_status_regex = br'...'` then `compile(du_talk_status_regex)` - a
    # NameError in __init__, before the module does anything. Extron's shipped
    # ATUC50 module keeps the assignment directly above its registration.
    # Carry each such local assignment (and the locals it reads in turn), in
    # source order among the calls, unless it already travels with __init__.
    local_assigns = {}
    for node in ast.walk(init_func):
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) for t in node.targets):
            for t in node.targets:
                local_assigns.setdefault(t.id, []).append(node)
    carried_init = {id(n) for s in a.init_extra_stmts for n in ast.walk(s)}
    prelude = {}
    todo = [(n.id, call.lineno) for call in matchstring_calls
            for n in ast.walk(call) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)]
    while todo:
        name, before_line = todo.pop()
        earlier = [s for s in local_assigns.get(name, ()) if s.lineno < before_line]
        if not earlier:
            continue
        stmt = earlier[-1]  # the assignment in force at the reading line
        if id(stmt) in carried_init or id(stmt) in prelude:
            continue
        prelude[id(stmt)] = stmt
        todo.extend((n.id, stmt.lineno) for n in ast.walk(stmt.value)
                    if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load))
    a.addmatchstring_prelude = sorted((s.lineno, ast.unparse(s)) for s in prelude.values())

    # class-body statements that are not methods: only methods were read, so
    # these were dropped, and a default argument reading one raised NameError
    # when the class was defined - the whole module failed to import. Three in
    # the corpus, all simple assignments; carried first so every def sees them.
    for s in cls.body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)) or _is_docstring_stmt(s):
            continue
        a.class_attr_stmts.append(s)
    if a.class_attr_stmts:
        a.residuals.add("driver-class-attribute-carried",
                        "carried %d class-body statement(s) of %s to the top of DeviceClass: %s"
                        % (len(a.class_attr_stmts), cls.name,
                           "; ".join(ast.unparse(s).splitlines()[0][:80] for s in a.class_attr_stmts)))

    # The SIS session flags the source sets and the handshake strings it sends,
    # its own __SetHelper's first - see FIXED_SET_UPDATE_HELPER_SIS_VERBOSE_ONLY.
    helper = next((s for s in cls.body if isinstance(s, ast.FunctionDef)
                   and s.name == "__SetHelper"), None)
    for n in list(ast.walk(helper) if helper else []) + list(ast.walk(cls)):
        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                and n.value.id == "self" and isinstance(n.ctx, ast.Store):
            if n.attr == "EchoDisabled":
                a.uses_echo = True
            elif n.attr == "VerboseDisabled":
                a.uses_verbose = True
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            for key in ("w3cv", "w0echo"):
                if key not in a.sis_literals and re.fullmatch(key + r"[\r\n]+", n.value):
                    a.sis_literals[key] = n.value

    # methods
    method_defs = [s for s in cls.body if isinstance(s, ast.FunctionDef) and s.name != "__init__"]
    # R37: names called as self.<name>(...) from a DIFFERENT method's body than
    # <name>'s own definition, computed once from the raw (pre-transform) source
    # so a later per-method deletion decision (_is_write_read_wrapper, below)
    # can tell whether deleting a wrapper would orphan a live caller. Evidenced
    # by the Samsung ethernet job: MultiviewCommand's Set body assigns
    # `mode = self.ReadMultiviewString(qualifier, 'Emulated')`, a value-context
    # call the generic Emulated-pre-write-statement-drop rule does not touch
    # (that rule only deletes a *standalone* Expr statement), so the call
    # itself survives translation even though _is_write_read_wrapper's
    # structural check says ReadMultiviewString's definition should be deleted
    # -- an AttributeError at runtime with nothing to catch it beforehand.
    _referenced_elsewhere = set()
    for _caller in method_defs:
        for _node in ast.walk(_caller):
            if (isinstance(_node, ast.Call) and isinstance(_node.func, ast.Attribute)
                    and isinstance(_node.func.value, ast.Name) and _node.func.value.id == "self"
                    and _node.func.attr != _caller.name):
                _referenced_elsewhere.add(_node.func.attr)
    # ...and names read as values, not called - yama's __init__ builds a
    # dispatch table {'FaderLevel': self.WriteFaderLevel, ...}. Deleting the
    # wrapper left that reference dangling, and the class failed while being
    # constructed (found by executing it, R13; 3 of the 24 generated modules
    # that could not be constructed).
    _referenced_as_value = set()
    for _caller in method_defs + [init_func]:
        _call_funcs = {id(n.func) for n in ast.walk(_caller) if isinstance(n, ast.Call)}
        for _node in ast.walk(_caller):
            if (isinstance(_node, ast.Attribute) and isinstance(_node.value, ast.Name)
                    and _node.value.id == "self" and isinstance(_node.ctx, ast.Load)
                    and id(_node) not in _call_funcs and _node.attr != _caller.name):
                _referenced_as_value.add(_node.attr)
    _referenced_elsewhere |= _referenced_as_value
    for func in method_defs:
        name = func.name
        _dropped_cmd_match = re.match(r"^(?:_cmd_Set|_cmd_Update|__Match|Write|Read)([A-Za-z0-9]+)$", name)
        if _dropped_cmd_match and _dropped_cmd_match.group(1) in ALWAYS_DROPPED_COMMAND_NAMES:
            continue  # residual already recorded once, above, for the command itself
        if name in ("__SetHelper", "__UpdateHelper") and a.dialect in ("sis_ethernet", "serial", "ethernet"):
            # GC's own __SetHelper/__UpdateHelper are dialect-fixed
            # boilerplate, not a per-driver transform of the GC body: diffing
            # shipped DSC and DTP3 (sis_ethernet) shows their __SetHelper/
            # __UpdateHelper are byte-identical modulo blank lines, and
            # Samsung's shipped serial module has its own (simpler, no
            # Echo/Verbose branches) fixed body -- always fixed, never
            # derived. Carrying the GC body through generically (as any
            # other method) leaked GC BaseDriver runtime API
            # (QueryDelayTimerIsRunning/StartQueryDelayTimer, and Samsung's
            # GC-only ReadPower power-gate) that no shipped module defines or
            # calls. Only sis_ethernet and serial are evidenced this way;
            # the http dialect has no oracle for this shape (Automate VX's
            # own __SetHelper/__UpdateHelper carry genuine per-driver HTTP
            # logic that already survives translation with no dangling
            # calls, and Samsung's HTTP/"ethernet" job has no shipped
            # HTTP-dialect module to compare against) and is left untouched.
            a.needs_fixed_set_update_helper = True
            a.residuals.add(
                "gc-sethelper-updatehelper-fixed-template",
                "%s: replaced GC's body with the fixed, evidence-backed %s-dialect boilerplate "
                "instead of transforming it, dropping GC BaseDriver runtime API "
                "(QueryDelayTimerIsRunning/StartQueryDelayTimer/ReadPower-power-gate) with no "
                "ControlScript equivalent" % (name, a.dialect))
            # The body is fixed, the signature is not: ktek's DM8000 declares
            # __SetHelper(..., qualifier, queryDisallowTime=0) and passes it,
            # so the four-parameter template raised TypeError on those
            # commands - 1,143 call sites in 192 of finding 14's 314 packages,
            # found by executing a module (R13); no static check looked at
            # argument counts. Extron's shipped modules keep the parameter
            # (and ignore it) where calls pass it - 36 in the 09/06/2026
            # shipment - and drop it where none do (DSC, DTP3), so it is
            # carried only when some call passes more than the four.
            extra = _extra_helper_params(func)
            if extra and name in _helper_calls_needing_more(method_defs, name):
                a.helper_extra_params[name] = extra
                a.residuals.add(
                    "helper-signature-carried",
                    "%s: kept the source's extra parameter(s) %s in the fixed template's "
                    "signature, accepted and ignored, as Extron's shipped modules with this "
                    "signature do" % (name, ", ".join(extra)))
            continue
        if name in ("OnConnected", "OnDisconnected"):
            # emit() always supplies its own fixed-template OnConnected/
            # OnDisconnected (see onconnected-ondisconnected-synthesized).
            # GC's own definitions must never be carried through as ordinary
            # methods: before this branch existed they landed in
            # a.leftover_methods like any other method, so the class ended up
            # with the same def twice; Python keeps only the last, so the
            # first (GC-derived) copy -- the one containing
            # self.__ResetLiveStatus(), a def dropped elsewhere as GC-only --
            # was silent, unreachable dead code carrying a dangling call.
            # Genuine device-state resets in the GC body (evidenced by
            # shipped DTP3's matrix_tie_status/matrix_io_names resets and
            # shipped Automate VX's Token/Authenticated resets + the
            # OnConnected TokenRequest kickoff, all of which the shipped
            # modules keep) are not GC-only boilerplate and are carried
            # through into the synthesized template at emit() time instead.
            transformed = transform_method(func, model_class_to_name, a.residuals, new_name=name,
                                            commands=a.commands)
            extra = []
            for stmt in transformed.body:
                if isinstance(stmt, ast.Pass):
                    continue
                if (isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call)
                        and _call_attr(stmt.value) == "__ResetLiveStatus"):
                    a.residuals.add(
                        "gc-dual-status-no-target",
                        "%s: dropped self.__ResetLiveStatus() call (GC dual-status construct "
                        "with no ControlScript target)" % name)
                    continue
                if (isinstance(stmt, ast.Assign) and len(stmt.targets) == 1
                        and isinstance(stmt.targets[0], ast.Attribute)
                        and stmt.targets[0].attr in ("EchoDisabled", "VerboseDisabled")):
                    a.residuals.add(
                        "gc-echo-verbose-toggle-superseded",
                        "%s: dropped self.%s assignment; the synthesized OnDisconnected already "
                        "sets both Echo/VerboseDisabled when has_verbose_echo is detected"
                        % (name, stmt.targets[0].attr))
                    continue
                extra.append(stmt)
            if name == "OnConnected":
                a.onconnected_extra_stmts = extra
            else:
                a.ondisconnected_extra_stmts = extra
            if extra:
                a.residuals.add(
                    "gc-onconnected-ondisconnected-extra-state-carried",
                    "%s: carried %d genuine device-state statement(s) from GC's definition into "
                    "the synthesized OnConnected/OnDisconnected template" % (name, len(extra)))
            else:
                a.residuals.add(
                    "gc-onconnected-ondisconnected-superseded",
                    "%s: GC's own definition contained only boilerplate already covered by the "
                    "synthesized fixed template; dropped entirely (emit() always supplies its own "
                    "OnConnected/OnDisconnected -- see onconnected-ondisconnected-synthesized)" % name)
            continue
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
            wrapped = name[len("Write"):] if name.startswith("Write") else name[len("Read"):]
            spec = a.commands.get(wrapped, {})
            if spec.get("live") is False and spec.get("emulated") is True:
                if name in _referenced_elsewhere:
                    # R37: this wrapper's structural shape says "delete" (it
                    # only calls WriteStatusHelper/ReadStatusHelper, GC dual-
                    # status machinery with no ControlScript target), but
                    # another retained method's body still calls it in a
                    # VALUE context (`mode = self.ReadMultiviewString(...)`),
                    # which the Emulated-pre-write-statement-drop rule does
                    # not strip (that rule only deletes a bare Expr
                    # statement). Deleting the definition anyway would leave
                    # that call dangling -- AttributeError at runtime, no
                    # residual to explain it beforehand. Keep it instead,
                    # backed by a private per-module scratch dict
                    # (self._emulated_status) rather than GC's own
                    # WriteStatusHelper/ReadStatusHelper (still dropped, no
                    # ControlScript target) and rather than ControlScript's
                    # WriteStatus/ReadStatus (the externally-visible Live
                    # store -- wrong target: Live=False means GC never
                    # published this as device status, so routing it through
                    # WriteStatus/ReadStatus would silently expose a
                    # never-live value via NewStatus()/SubscribeStatus()).
                    kind = "Write" if name.startswith("Write") else "Read"
                    new_func = _make_emulated_scratch_wrapper(name, wrapped, kind)
                    a.methods[name] = new_func
                    a.method_order.append((("~emulated_wrapper", wrapped, 0 if kind == "Write" else 1), name))
                    a.needs_emulated_scratch_store = True
                    a.residuals.add(
                        "gc-emulated-wrapper-kept-as-scratch-store",
                        "%s: command %r is Live=False/Emulated=True and is called from another "
                        "retained method's body; kept (instead of deleted) as a private "
                        "self._emulated_status[%r] accessor so that call resolves instead of "
                        "raising AttributeError. This is NOT GC's own WriteStatusHelper/"
                        "ReadStatusHelper (Mutex/ExtronTime dual-status machinery, still dropped "
                        "elsewhere, no ControlScript target) and does NOT use ControlScript's "
                        "WriteStatus/ReadStatus (Live=False means GC never published this as "
                        "device status; the externally-visible Live store is the wrong target). "
                        "If the matching %s<X> wrapper's own call site was itself dropped as a "
                        "standalone Emulated pre-write elsewhere (see "
                        "gc-dual-status-emulated-prewrite-dropped), this value is never written "
                        "and always reads back the scratch default (None) -- verify by hand."
                        % (name, wrapped, wrapped, "Write" if kind == "Read" else "Read"))
                    continue
                # Evidenced identically across two independent packages/
                # dialects (DTP3's MatrixIONameString/MatrixIONumberSelect,
                # Samsung ethernet's MultiviewString): a command with
                # Live=False/Emulated=True in the .pkp has no ControlScript
                # dual-status "Live" store at all. Any OTHER command's body
                # still calling this wrapper is therefore calling a
                # deleted method with no safe automatic replacement -- the
                # B1 Read<X>->ReadStatus rule deliberately does not fire
                # here (it's gated on a literal 'Live' context; this
                # wrapper is only ever called with 'Emulated'), so the call
                # site surfaces as dangling-self-call. Confirmed in DTP3
                # v1.2.0.0: Extron folded MatrixIONameString/
                # MatrixIONumberSelect entirely into MatrixIONameCommand's
                # Number/Name qualifiers rather than keeping a Read/Write
                # pair -- verify the equivalent restructuring by hand for
                # any caller flagged here rather than bridging to
                # ReadStatus/WriteStatus, which would silently return/store
                # an always-empty status instead.
                a.residuals.add(
                    "gc-emulated-only-command-wrapper-dropped",
                    "dropped %s: command %r is Live=False/Emulated=True (no ControlScript "
                    "dual-status store); if anything else in this module still calls %s(...), "
                    "that call will surface as dangling-self-call below and needs a hand-verified "
                    "restructuring, not an automatic ReadStatus/WriteStatus bridge" % (name, wrapped, name))
            elif name.startswith("Write") and name in _referenced_as_value:
                # An ordinary (Live) command's Write<X> held as a value (a
                # dispatch table) and called later with a context. Calls
                # are already rewritten by two rules - 'Live' becomes
                # WriteStatus, an 'Emulated' pre-write is dropped - so the
                # kept wrapper is exactly those two rules, applied at call
                # time instead of at translation time.
                new_func = ast.parse(
                    "def %s(self, value, qualifier, context):\n"
                    "    if context == 'Live':\n"
                    "        self.WriteStatus(%r, value, qualifier)\n" % (name, wrapped)).body[0]
                ast.fix_missing_locations(new_func)
                a.methods[name] = new_func
                a.method_order.append((("~live_wrapper", wrapped, 0), name))
                a.residuals.add(
                    "gc-write-wrapper-kept-for-value-reference",
                    "%s: referenced as a value (not called) elsewhere, so kept, forwarding a "
                    "'Live' write to WriteStatus(%r, ...) and dropping an 'Emulated' one - the "
                    "same two rules applied to direct calls" % (name, wrapped))
                continue
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

        transformed = transform_method(func, model_class_to_name, a.residuals, new_name=new_name,
                                        commands=a.commands)

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

# __SetHelper/__UpdateHelper -- fixed, dialect-keyed boilerplate (see the
# gc-sethelper-updatehelper-fixed-template residual in analyse() for the
# evidence). sis_ethernet: byte-identical (modulo blank lines) between
# shipped DSC (extr_scaler_DSC_12G_HD_A_v1_0_0_0.py:995-1032) and shipped
# DTP3 (extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py:1074-1109).
FIXED_SET_UPDATE_HELPER_SIS_ETHERNET = '''
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\\r\\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\\r\\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\\r\\n')
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\\r\\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)
'''

# sis_ethernet for a driver with the verbose handshake and no echo handshake:
# the source never sets self.EchoDisabled, so the template above read an
# attribute nothing assigns - an AttributeError on every Set and Update in 8 of
# finding 14's 314 packages (found by R13's attribute check). Evidenced by
# Extron's shipped modules for three of them (AXI 22 AT D Plus, AXI02AT,
# IPL T CR48): the same template with the echo branches removed.
FIXED_SET_UPDATE_HELPER_SIS_VERBOSE_ONLY = '''
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\\r\\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\\r\\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)
'''

# serial: evidenced by shipped Samsung
# (smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py:219-236) -- simpler, no
# Echo/Verbose branches; only one oracle exists for this dialect (same
# generalisation risk already flagged by serial-over-ethernet-mixin-
# generalised for MIXIN_SERIAL).
FIXED_SET_UPDATE_HELPER_SERIAL = '''
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
'''

# Plain (non-SIS) Ethernet. Derived from the SIS template by REMOVING the
# Extron-specific echo/verbose handshake rather than by inventing a replacement:
# a third-party device's own handshake is not knowable from the package, so it is
# omitted and reported as a residual for a human to supply. Emitting Extron's
# handshake to a Biamp or Clock Audio device -- which is what this code did before
# -- is fabricated wire content.
FIXED_SET_UPDATE_HELPER_ETHERNET_PLAIN = '''
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)
'''

# Plain (non-SIS) Ethernet transport. Shape copied from the only plain-ethernet
# oracle, Clock Audio's shipped EthernetClass
# (clau_dsp_CDT100_v1_0_3_0.py:419-441). `Protocol`/`ServicePort` default to
# whatever ROADMAP R16 could read off the package's own EthernetProtocolAsset
# (`_port` + `_compatibility`, see ethernet_protocol_info / emit()'s
# ethernet-connection-settings-* residuals) -- the NEUTRAL extronlib defaults
# ('TCP', 0) below are the fallback used only when that data is genuinely
# absent or unmapped (see ETHERNET_COMPATIBILITY_PROTOCOL), never a
# fabricated per-device guess.
def _mixin_ethernet_text(protocol="TCP", port=0):
    return ('''

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol=%r, ServicePort=%r, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\\r\\n')

    def Discard(self, message):
        self.Error([message])
''') % (protocol, port)

FIXED_SET_UPDATE_HELPER = {
    "sis_ethernet": FIXED_SET_UPDATE_HELPER_SIS_ETHERNET,
    "serial": FIXED_SET_UPDATE_HELPER_SERIAL,
    "ethernet": FIXED_SET_UPDATE_HELPER_ETHERNET_PLAIN,
}

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

# R16 deliberately does NOT thread the resolved `_port` into SSHClass's
# ServicePort default, unlike EthernetClass below. Evidence: BOTH shipped
# sis_ethernet oracles -- DSC (extr_scaler_DSC_12G_HD_A_v1_0_0_0.py:1218) and
# DTP3 (extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py:1315) -- leave
# `ServicePort=0` even though their own packages' real `_port` is 22023
# (confirmed directly: both resolve to _compatibility=Ethernet_SSH(512),
# _port=22023 via ethernet_protocol_info). extronlib's own
# EthernetClientInterface(Protocol='SSH', ServicePort=0) auto-selects the
# standard SSH port, so 0 is Extron's own intentional, oracle-matching
# value here, not an unresolved gap -- writing 22023 in would DIVERGE from
# both oracles, not fix anything. No residual: this was never the
# ethernet-connection-settings-not-recoverable defect (that residual only
# ever fired for the 'ethernet' dialect's EthernetClass, never sis_ethernet).
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
    calls = list(zip(a.addmatchstring_linenos, a.addmatchstring_srcs)) \
        if len(a.addmatchstring_linenos) == len(a.addmatchstring_srcs) \
        else [(0, s) for s in a.addmatchstring_srcs]
    # the carried locals sort before any call on a later line; a stable sort
    # keeps the calls' own order where lines tie (or are unknown)
    for _, src in sorted(a.addmatchstring_prelude + calls, key=lambda ls: ls[0]):
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


def _ethernet_settings_unresolved_reason(a):
    """Why R16's EthernetClass/SSHClass Protocol/ServicePort resolution would
    fall back to the neutral extronlib defaults, or None when a.ethernet_info
    carries a genuinely usable (protocol, port) pair. A precise, evidence-keyed
    reason for every case SURVEY.md's corpus-wide _compatibility read found,
    not a single generic "not recoverable" message."""
    info = a.ethernet_info
    if info is None:
        return "no EthernetProtocolAsset was found for any model in this job"
    protocol, port, compat = info
    if compat is None:
        return "the package's own _compatibility field is absent or unreadable"
    if compat in (1024, 2048):
        return ("_compatibility=%d (%s) is an auxiliary-feature flag with no real socket "
                "endpoint -- always _port=0 corpus-wide per SURVEY.md, not a distinct wire "
                "transport" % (compat, ETHERNET_COMPATIBILITY_NAME.get(compat, compat)))
    if compat == 64:
        return ("_compatibility=64 (Ethernet_HTTP) is handled end to end by the http "
                "dialect's own HTTPDriver detection; EthernetClass/SSHClass never carry it")
    if protocol is None:
        return "_compatibility=%r has no known EthernetClass/SSHClass protocol mapping" % (compat,)
    if port is None:
        return "the package's own _port field is null"
    return None


def _resolve_ethernet_class_defaults(a, secondary=False):
    """(Protocol, ServicePort) for EthernetClass (TCP/UDP dialects). Falls
    back to the neutral extronlib defaults ('TCP', 0) and records
    ethernet-connection-settings-not-recoverable with a precise reason when
    the package's own EthernetProtocolAsset data can't supply them."""
    reason = _ethernet_settings_unresolved_reason(a)
    info = a.ethernet_info
    if reason is None and info[0] in ("TCP", "UDP"):
        return info[0], info[1]
    if reason is None:  # info[0] == "SSH": right data, wrong mixin class
        reason = ("_compatibility=512 (Ethernet_SSH) resolves to SSHClass for this model, "
                   "not EthernetClass")
    a.residuals.add(
        "ethernet-connection-settings-not-recoverable",
        "%sEthernetClass emitted with the neutral extronlib defaults (Protocol='TCP', "
        "ServicePort=0): %s. Note the shipped Biamp module uses SSHClass and the shipped "
        "Clock Audio module uses Protocol='UDP', ServicePort=49494 -- the correct choice "
        "is per-device and is not inferable beyond what the package's own _port/"
        "_compatibility can supply." % ("secondary " if secondary else "", reason))
    return "TCP", 0


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
    for line in a.carried_imports:
        if line not in header_lines:
            header_lines.append(line)

    body = []
    body.append("class DeviceClass:")
    for stmt in a.class_attr_stmts:
        body.append(_reindent(ast.unparse(stmt), 4))
    if a.class_attr_stmts:
        body.append("")
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

    if a.needs_emulated_scratch_store:
        body.append("        self._emulated_status = {}")

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

    if a.needs_fixed_set_update_helper:
        template = FIXED_SET_UPDATE_HELPER[a.dialect]
        if a.dialect == "sis_ethernet" and not a.uses_echo:
            template = FIXED_SET_UPDATE_HELPER_SIS_VERBOSE_ONLY
            a.residuals.add(
                "sis-verbose-only-template",
                "the source sets VerboseDisabled but never EchoDisabled, so the SIS template "
                "without the echo handshake is used (Extron's shipped AXI 22 AT D Plus, "
                "AXI02AT and IPL T CR48 modules have this shape)")
        helpers = template.rstrip("\n")
        if a.dialect == "sis_ethernet":
            for key, default in (("w3cv", "'w3cv\\r\\n'"), ("w0echo", "'w0echo\\r\\n'")):
                found = a.sis_literals.get(key)
                if found and repr(found) != default and default in helpers:
                    helpers = helpers.replace(default, repr(found))
                    a.residuals.add(
                        "sis-handshake-literal-from-source",
                        "the template's %s is replaced by the source's own %s (the "
                        "terminator differs between drivers)" % (default, repr(found)))
        for helper, extra in a.helper_extra_params.items():
            fixed = "def %s(self, command, commandstring, value, qualifier):" % helper
            assert fixed in helpers, (helper, a.dialect)
            helpers = helpers.replace(fixed, "def %s(self, command, commandstring, value, "
                                             "qualifier, %s):" % (helper, ", ".join(extra)))
        body.append(helpers)
        body.append("")

    # OnConnected / OnDisconnected -- the fixed template, plus whatever
    # genuine device-state statements survived from GC's own definitions
    # (see the OnConnected/OnDisconnected branch in analyse(): boilerplate
    # like self.__ResetLiveStatus() and the Echo/VerboseDisabled toggle
    # below are GC-only or already covered here and were dropped there).
    body.append("    def OnConnected(self):")
    body.append("        self.connectionFlag = True")
    body.append("        self.WriteStatus('ConnectionStatus', 'Connected')")
    body.append("        self.counter = 0")
    for stmt in a.onconnected_extra_stmts:
        body.append(_reindent(ast.unparse(stmt), 8))
    body.append("")
    body.append("    def OnDisconnected(self):")
    body.append("        self.WriteStatus('ConnectionStatus', 'Disconnected')")
    body.append("        self.connectionFlag = False")
    for stmt in a.ondisconnected_extra_stmts:
        body.append(_reindent(ast.unparse(stmt), 8))
    if a.has_verbose_echo or a.uses_verbose:
        # Reset only the session flags the source uses: a verbose-only
        # driver's shipped OnDisconnected resets VerboseDisabled alone.
        body.append("")
        if a.has_verbose_echo or a.uses_echo:
            body.append("        self.EchoDisabled = True")
        body.append("        self.VerboseDisabled = True")
    if a.onconnected_extra_stmts or a.ondisconnected_extra_stmts:
        a.residuals.add("onconnected-ondisconnected-synthesized",
                         "OnConnected/OnDisconnected are the fixed template with GC's own genuine "
                         "device-state statements carried through (see "
                         "gc-onconnected-ondisconnected-extra-state-carried); any *other* "
                         "device-specific reset a hand-authored shipped module might add there was "
                         "not derived (not part of the wire-string acceptance surface)")
    else:
        a.residuals.add("onconnected-ondisconnected-synthesized",
                         "OnConnected/OnDisconnected are the minimal fixed template; any device-specific "
                         "state reset a hand-authored shipped module might add there was not derived "
                         "(not part of the wire-string acceptance surface)")
    body.append("")

    for stub_src in model_stub_srcs:
        body.append(_reindent(stub_src, 4))
        body.append("")

    body.append(FIXED_TAIL.rstrip("\n"))
    if a.dialect in ("sis_ethernet", "serial", "ethernet"):
        body.append(FIXED_STREAM_TAIL_EXTRA.rstrip("\n"))

    if a.dialect == "sis_ethernet":
        body.append(MIXIN_SSH.rstrip("\n"))
    elif a.dialect == "ethernet":
        protocol, port = _resolve_ethernet_class_defaults(a)
        body.append(_mixin_ethernet_text(protocol, port).rstrip("\n"))
    elif a.dialect == "serial":
        body.append(MIXIN_SERIAL.rstrip("\n"))
        a.residuals.add("serial-over-ethernet-mixin-generalised",
                         "SerialOverEthernetClass is only evidenced by the single Samsung oracle; "
                         "emitting it for every 'serial' dialect job is a generalisation, not "
                         "independently confirmed")
    elif a.dialect == "http":
        body.append(MIXIN_HTTP.rstrip("\n"))

    # R17: a model can declare BOTH a Serial and an Ethernet protocol asset
    # (see needs_dual_transport_mixin above) -- emit the OTHER transport's
    # wiring class(es) too, alongside whichever one the elif chain above
    # picked as primary (__SetHelper/__UpdateHelper stay keyed to the
    # primary dialect; GC's own Send()/ConnectionType abstraction is what
    # makes one shared command body usable from either).
    if a.needs_dual_transport_mixin:
        if a.dialect == "serial":
            if _source_speaks_sis(job.source):
                body.append(MIXIN_SSH.rstrip("\n"))
            else:
                protocol, port = _resolve_ethernet_class_defaults(a, secondary=True)
                body.append(_mixin_ethernet_text(protocol, port).rstrip("\n"))
        elif a.dialect in ("sis_ethernet", "ethernet"):
            body.append(MIXIN_SERIAL.rstrip("\n"))
            a.residuals.add("serial-over-ethernet-mixin-generalised",
                             "secondary SerialClass/SerialOverEthernetClass (this model also "
                             "declares a SerialProtocolAsset) emitted alongside the primary "
                             "%s wiring class." % a.dialect)

    text = "\n".join(header_lines) + "\n\n" + "\n".join(body) + "\n"
    before, after = _module_definitions_needed(text, a)
    if before or after:
        a.residuals.add(
            "module-level-definition-carried",
            "carried the source's top-level %s verbatim: the generated module reads them"
            % ", ".join(sorted(set().union(*(_module_stmt_binds(s) for s in before + after)))))
        pre = "".join(ast.unparse(s) + "\n\n" for s in before)
        post = "".join("\n\n" + ast.unparse(s) for s in after)
        text = ("\n".join(header_lines) + "\n\n" + pre + "\n".join(body) + post + "\n")
    return text


# ==========================================================================
# TOP LEVEL
# ==========================================================================

EXTRONLIB_PROVIDED = frozenset([
    # Public methods of the extronlib interface classes that ControlScript transport
    # classes actually inherit from -- SerialInterface, EthernetClientInterface,
    # EthernetServerInterface(Ex), IRInterface, RelayInterface, SPInterface. A module may
    # call these on self without defining them.
    #
    # Source: the official ControlScript VS Code extension (extronlib API stubs,
    # versions 3.13.39 / 3.12.5 / 1.11.1xi), not inference. Deliberately scoped to the
    # transport bases rather than all 140 public extronlib methods: a wider list would
    # silence real dangling references, which is the failure this check exists to catch.
    #
    # Note: HTTPClass inherits from DeviceClass only, with no extronlib interface base,
    # so for the http dialect this list is broader than strictly correct.
    "Baud",
    "CharDelay",
    "Clients",
    "Connect",
    "Connected",
    "Credentials",
    "Data",
    "Disconnect",
    "Disconnected",
    "File",
    "FlowControl",
    "Host",
    "Hostname",
    "IPAddress",
    "IPPort",
    "Initialize",
    "Interface",
    "MaxClients",
    "Mode",
    "Offline",
    "Online",
    "Parity",
    "PlayContinuous",
    "PlayCount",
    "PlayTime",
    "Port",
    "Protocol",
    "Pulse",
    "ReceiveData",
    "SSLWrap",
    "Send",
    "SendAndWait",
    "ServicePort",
    "SetBufferSize",
    "SetState",
    "StartKeepAlive",
    "StartListen",
    "State",
    "Stop",
    "StopKeepAlive",
    "StopListen",
    "Toggle",
])


def _source_speaks_sis(src_text):
    """True when the embedded GC script itself uses the Extron SIS session
    handshake. Evidence-based: the strings must be present in the package."""
    return "w0echo" in (src_text or "") or "w3cv" in (src_text or "")


def _has_emulated_context(call):
    """True when a call passes the GC 'Emulated' status context, positionally or
    by keyword.

    Keying only on the last POSITIONAL argument was a real boundary: a generator
    emitting context='Emulated' would leave the pre-write call in place while its
    target definition was still deleted -- the same dangling-reference bug this
    rule exists to prevent, reintroduced silently. No package among the six uses
    the keyword form; this closes it before a seventh does.
    """
    if call.args and _const_eq(call.args[-1], "Emulated"):
        return True
    return any(_const_eq(kw.value, "Emulated") for kw in (call.keywords or []))


def find_invented_wire_strings(module_source, origin_source):
    """Return literal strings the generated module sends that do NOT occur in the
    package it came from.

    A converter must never author wire content. The sis_ethernet helper template
    was injecting Extron's own 'w0echo' / 'w3cv' SIS handshake into Biamp and
    Clock Audio modules -- devices that do not speak SIS -- because the template
    was lifted from an Extron device and keyed only on "is it Ethernet". The
    per-command wire table could not see it: it extracts command templates, not
    helper bodies.
    """
    # Compare parsed constant to parsed constant. Comparing a parsed value against
    # the origin's raw TEXT would mis-fire on every escape sequence: the AST value
    # of 'REAL\\r' is REAL + CR, which does not occur literally in the source text.
    origin_literals = set()
    for node in ast.walk(ast.parse(origin_source)):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            origin_literals.add(node.value)

    invented = []
    for node in ast.walk(ast.parse(module_source)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in ("Send", "SendAndWait"):
            continue
        for arg in node.args:
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.strip():
                if arg.value not in origin_literals \
                        and not any(arg.value in lit for lit in origin_literals):
                    invented.append(arg.value)
    return sorted(set(invented))


def find_dangling_self_calls(module_source):
    """Return sorted names called as self.<name>(...) but never defined in the module.

    A wrapper deleted by the Read/Write-wrapper rule is normally a self-contained
    status accessor, but it can also be called cross-command from another Set body
    to compose that command's payload. Deleting it then leaves a reference that
    raises AttributeError at runtime -- on a control processor, not here. This is
    a whole-class check rather than a special case, so it catches any rule that
    removes something still in use.

    Scoped to the classes the translator generates - DeviceClass and the
    transport classes that derive from it - because only those are rewritten.
    The source's own helper classes, carried verbatim when the module reads
    them, call callables held in attributes (`self.entry_function(...)`) and
    methods inherited from outside the module (a urllib handler's
    `self.http_error_401(...)`); no rewrite rule touched them, so whatever they
    call, they called in the source too. A module with no DeviceClass is
    checked whole, as before.
    """
    tree = ast.parse(module_source)
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    generated = [c for c in classes if c.name == "DeviceClass" or any(
        isinstance(b, ast.Name) and b.id == "DeviceClass" for b in c.bases)]
    scopes = generated or [tree]
    defined = {node.name for scope in scopes for node in ast.walk(scope)
               if isinstance(node, ast.FunctionDef)}
    defined |= EXTRONLIB_PROVIDED
    called = set()
    for node in (n for scope in scopes for n in ast.walk(scope)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "self":
            called.add(node.func.attr)
    return sorted(called - defined)


# Attributes the extronlib interface constructors set on the instance, from the
# ControlScript extension's stubs (EthernetClientInterface, SerialInterface).
INTERFACE_ATTRIBUTES = frozenset([
    "Hostname", "IPAddress", "IPPort", "Protocol", "ServicePort", "Credentials",
    "Host", "Port", "Baud", "Data", "Parity", "Stop", "FlowControl", "CharDelay", "Mode",
])


def _generated_classes(tree):
    classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
    return [c for c in classes if c.name == "DeviceClass" or any(
        isinstance(b, ast.Name) and b.id == "DeviceClass" for b in c.bases)]


def _self_attributes_assigned(nodes):
    """Names assigned as self.<name> (any store, setattr with a literal) or
    bound in a class body, anywhere under the given nodes."""
    out = set()
    for root in nodes:
        if isinstance(root, ast.ClassDef):
            for s in root.body:
                for t in (s.targets if isinstance(s, ast.Assign) else
                          [s.target] if isinstance(s, (ast.AnnAssign, ast.AugAssign)) else []):
                    if isinstance(t, ast.Name):
                        out.add(t.id)
        for n in ast.walk(root):
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) \
                    and n.value.id == "self" and isinstance(n.ctx, (ast.Store, ast.Del)):
                out.add(n.attr)
            elif isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "setattr" and len(n.args) >= 2 \
                    and isinstance(n.args[1], ast.Constant):
                out.add(n.args[1].value)
    return out


def find_unassigned_self_attributes(module_source):
    """Return sorted names read as self.<name> (not called) in the generated
    classes that nothing assigns there and no base class provides.

    The attribute-read companion of find_dangling_self_calls, found necessary
    by executing generated modules (ROADMAP R13): DSC's UpdateLogoAvailability
    read the GC throttle timer self.lastLogoAvailabilityUpdate, whose every
    write the translation drops; ktek's login read self.deviceUsername, set
    only in GC's dropped configs[...] parsing. Neither is a call, so the
    dangling-call check could not see them. Scoped like that check to
    DeviceClass and the classes derived from it."""
    tree = ast.parse(module_source)
    generated = _generated_classes(tree)
    if not generated:
        return []
    assigned = _self_attributes_assigned(generated)
    methods = {n.name for c in generated for n in ast.walk(c) if isinstance(n, ast.FunctionDef)}
    call_funcs = {id(n.func) for c in generated for n in ast.walk(c) if isinstance(n, ast.Call)}
    read = {n.attr for c in generated for n in ast.walk(c)
            if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name)
            and n.value.id == "self" and isinstance(n.ctx, ast.Load) and id(n) not in call_funcs}
    known = assigned | methods | EXTRONLIB_PROVIDED | INTERFACE_ATTRIBUTES
    return sorted(a for a in read
                  if a not in known and not (a.startswith("__") and a.endswith("__")))


def _accepts_call(func, call):
    """Could `func` (a method definition) bind this `self.<name>(...)` call?"""
    a = func.args
    static = any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in func.decorator_list)
    pos = [p.arg for p in a.posonlyargs + a.args]
    if not static and pos:
        pos = pos[1:]                                 # self (or cls)
    n_pos = len(call.args)
    if n_pos > len(pos) and a.vararg is None:
        return False
    keywords = {k.arg for k in call.keywords}
    first_default = len(pos) - len(a.defaults)
    for i, name in enumerate(pos):
        if i < n_pos:
            if name in keywords:
                return False                          # given twice
        elif i < first_default and name not in keywords:
            return False                              # required, not given
    kwonly = {p.arg: d for p, d in zip(a.kwonlyargs, a.kw_defaults)}
    if any(d is None and name not in keywords for name, d in kwonly.items()):
        return False
    allowed = set(pos[n_pos:]) | set(kwonly)
    return a.kwarg is not None or keywords <= allowed


def find_call_arity_mismatches(module_source):
    """Return sorted (method, arguments given) for self.<method>(...) calls in
    the generated classes that no definition of <method> there can accept.

    Found necessary by executing generated modules (ROADMAP R13): GC's
    __SetHelper takes a fifth argument, queryDisallowTime, that the fixed
    four-parameter template did not, so 1,143 calls in 192 of finding 14's
    314 packages would have raised TypeError - every name resolved, so no
    other check could see it. Calls with *args or **kwargs are skipped."""
    tree = ast.parse(module_source)
    generated = _generated_classes(tree)
    defs = collections.defaultdict(list)
    for c in generated:
        for n in c.body:
            if isinstance(n, ast.FunctionDef):
                defs[n.name].append(n)
    out = set()
    for c in generated:
        for n in ast.walk(c):
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                    and isinstance(n.func.value, ast.Name) and n.func.value.id == "self"):
                continue
            if any(isinstance(x, ast.Starred) for x in n.args) \
                    or any(k.arg is None for k in n.keywords):
                continue
            funcs = defs.get(n.func.attr)
            if funcs:
                if not any(_accepts_call(f, n) for f in funcs):
                    out.add((n.func.attr, len(n.args) + len(n.keywords)))
            elif n.func.attr in EXTRONLIB_CALL_SIGNATURES:
                lo, hi, keywords = EXTRONLIB_CALL_SIGNATURES[n.func.attr]
                if not lo <= len(n.args) <= hi or any(k.arg not in keywords for k in n.keywords):
                    out.add((n.func.attr, len(n.args) + len(n.keywords)))
    return sorted(out)


# The interface methods generated modules call most, as the ControlScript
# extension's stubs declare them: (min positional, max positional, keywords).
EXTRONLIB_CALL_SIGNATURES = {
    "Send": (1, 1, frozenset()),
    "SendAndWait": (2, 2, frozenset(["deliLen", "deliTag", "deliRex"])),
}


def find_unresolved_globals(module_source):
    """Return sorted names read as bare globals that nothing in the module binds.

    The companion of find_dangling_self_calls for module scope: a name the
    module neither defines, imports, assigns nor gets from builtins raises
    NameError when the line runs. Scope-insensitive on purpose - a name bound
    anywhere counts as bound - so this under-reports rather than over-reports.
    """
    import builtins
    tree = ast.parse(module_source)
    bound = set(dir(builtins))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            args = node.args
            for arg in args.posonlyargs + args.args + args.kwonlyargs:
                bound.add(arg.arg)
            for arg in (args.vararg, args.kwarg):
                if arg is not None:
                    bound.add(arg.arg)
        elif isinstance(node, ast.Import):
            bound.update((al.asname or al.name).split(".")[0] for al in node.names)
        elif isinstance(node, ast.ImportFrom):
            bound.update(al.asname or al.name for al in node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            bound.add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            bound.add(node.name)
    read = {node.id for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)}
    return sorted(read - bound)


def _names_bound_by(stmt):
    """Names a module-level statement binds: its def/class name, the Name
    targets of an assignment (tuples unpacked), a for loop's target, anything
    an import inside it binds. Walks the whole statement, so for an if/try block
    it is every name bound in any branch."""
    out = set()
    for node in ast.walk(stmt):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            out.add(node.id)
        elif isinstance(node, ast.Import):
            out.update((al.asname or al.name).split(".")[0] for al in node.names)
        elif isinstance(node, ast.ImportFrom):
            out.update(al.asname or al.name for al in node.names)
    return out


def _module_stmt_binds(stmt):
    """What a carried top-level statement provides, for the demand closure: a
    def/class its name, an assignment its Name targets, and any statement the
    names whose items or attributes it stores into (`EXP_TABLE[i] = ...` in a
    top-level for loop provides EXP_TABLE's contents). A for loop's own target
    is deliberately not included: a method-local `i` must never pull in a
    module-level `for i in ...`."""
    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {stmt.name}
    out = set()
    if isinstance(stmt, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
        targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
        for t in targets:
            for n in ast.walk(t):
                if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store):
                    out.add(n.id)
    for n in ast.walk(stmt):
        if isinstance(n, (ast.Subscript, ast.Attribute)) and isinstance(n.ctx, ast.Store):
            base = n.value
            while isinstance(base, (ast.Subscript, ast.Attribute)):
                base = base.value
            if isinstance(base, ast.Name):
                out.add(base.id)
    return out


def _module_definitions_needed(text, a):
    """The source's top-level statements the generated module reads, closed
    over what they read in turn, as (before, after) lists in source order -
    before and after the driver class, where the source put them.

    Demand-driven on purpose: nearly every script defines `class
    ExtronTime(float)` after its driver class, for GC's dual-status machinery
    that the translation drops, and carrying it everywhere would be noise. A
    statement that would rebind a name the generated module already defines at
    top level (DeviceClass, a transport class) is refused, with a residual."""
    tree = ast.parse(text)
    defined = {n.name for n in tree.body if isinstance(n, ast.ClassDef)}
    wanted = set(find_unresolved_globals(text))
    carried = set()
    todo = list(wanted)
    seen = set()
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        for i, (_, stmt) in enumerate(a.module_stmts):
            if i in carried or name not in _module_stmt_binds(stmt):
                continue
            clash = _names_bound_by(stmt) & defined
            if clash:
                a.residuals.add(
                    "module-level-definition-not-carried",
                    "the source's top-level %s would rebind %s, which the generated module "
                    "already defines; not carried" % (type(stmt).__name__, sorted(clash)))
                continue
            carried.add(i)
            todo.extend(find_unresolved_globals(ast.unparse(stmt)))
    before = [s for i, (after, s) in enumerate(a.module_stmts) if i in carried and not after]
    after = [s for i, (after, s) in enumerate(a.module_stmts) if i in carried and after]
    return before, after


def _unresolved_origin(name, a, source_unresolved):
    """Why a name the generated module reads is unbound - for the residual."""
    if name in source_unresolved:
        return ("it is unbound in the embedded script too: a defect in the package "
                "itself, carried faithfully")
    if name in a.gc_import_names:
        return ("the source binds it only by the GC runtime import `%s`, which does not "
                "exist under ControlScript; no rule maps its call sites"
                % a.gc_import_names[name])
    if name in a.conditional_names:
        return ("the source binds it only inside a top-level if/try block (a platform "
                "gate), which is not carried")
    return "the source binds it in a scope the translation dropped"


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
    for name in find_dangling_self_calls(text):
        residuals.add("dangling-self-call",
                      "generated module calls self.%s(...) but never defines it; a rewrite rule "
                      "removed a method that is still referenced. Calling it would raise "
                      "AttributeError at runtime." % name)
    for name, given in find_call_arity_mismatches(text):
        residuals.add("call-arity-mismatch",
                      "generated module calls self.%s(...) with %d argument(s), which no "
                      "definition of it accepts; the call would raise TypeError at runtime."
                      % (name, given))
    unassigned = find_unassigned_self_attributes(text)
    if unassigned:
        try:
            src_tree = ast.parse(job.source)
            src_cls, _ = _find_driver_class(src_tree)
            source_assigns = _self_attributes_assigned([src_cls])
        except (SyntaxError, ValueError):
            source_assigns = set()
        for name in unassigned:
            why = ("the source assigns it in code the translation dropped"
                   if name in source_assigns else
                   "the source never assigns it either (GC's runtime may; ControlScript's does not)")
            residuals.add("unassigned-self-attribute",
                          "generated module reads self.%s, which nothing in the generated "
                          "classes assigns; the line that reads it would raise AttributeError "
                          "at runtime. Why: %s." % (name, why))
    unresolved = find_unresolved_globals(text)
    source_unresolved = set()
    if unresolved:
        try:
            source_unresolved = set(find_unresolved_globals(job.source))
        except SyntaxError:
            pass
    for name in unresolved:
        residuals.add("unresolved-global-name",
                      "generated module reads %s as a global that nothing binds; the line "
                      "that reads it would raise NameError at runtime. Why: %s."
                      % (name, _unresolved_origin(name, a, source_unresolved)))
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
