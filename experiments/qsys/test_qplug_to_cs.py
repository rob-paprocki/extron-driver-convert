#!/usr/bin/env python3
"""
test_qplug_to_cs.py - tests for bridge_ir and qplug_to_cs.

Pattern matches test_qplug_wire.py: assert-based, stdlib only, run as
`python -u experiments/qsys/test_qplug_to_cs.py`.

Vendor-input tests (the Clock Audio pair, the RDL BTN plugin, the full plain
library stress-run) skip gracefully when the file is not present on disk.
"""
from __future__ import annotations

import ast
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from bridge_ir import (
    BridgedCommand,
    BridgedModule,
    BridgedResponse,
    BridgedTemplate,
    _derive_name,
    _first_token,
    _is_update,
    _merge_sg_pairs,
    _name_from_label,
    from_qwire,
)
from qplug_to_cs import (
    _bytes_literal_to_pysrc,
    _emit_cmd_expr,
    _lua_pattern_to_py,
    _py_identifier,
    _rename_colliding,
    _text_literal_to_pysrc,
    emit,
)
from qplug_wire import extract
import wire_table


VENDOR_FILES = {
    "cdt100_qplug": "samples/qsys/library/ClockAudio_CDT100.3.6.0/ClockAudioCDT100.qplug",
    "cdt100_extron": "corpus/extron-gs-modules/09062026/clau_dsp_CDT100_v1_0_3_0.py",
    "rdl_btn_qplug": "samples/qsys/plugins/RDL-BTN-Series-1.1.3-Plugin.qplug",
    "atero_bt_extron": "corpus/extron-gs-modules/09062026/atero_dsp_unBT2A_v1_0_0_0.py",
    "qsys_library_dir": "samples/qsys/library",
    "qsys_plugins_dir": "samples/qsys/plugins",
}


def _vendor(key: str) -> str | None:
    p = os.path.join(ROOT, VENDOR_FILES[key])
    return p if os.path.exists(p) else None


# ---------------------------------------------------------------------------
# bridge_ir pure-function tests
# ---------------------------------------------------------------------------

def test_py_identifier_folds_hostile_input():
    """A command name becomes a valid Python identifier regardless of what
    the plugin gave us."""
    assert _py_identifier("ARMC") == "ARMC"
    assert _py_identifier("BTConnect") == "BTConnect"
    assert _py_identifier("1CLSS") == "_1CLSS", "digit prefix -> underscore"
    assert _py_identifier("%1CLSS") == "_1CLSS", "'%' folds the same as digit prefix"
    assert _py_identifier("") == "Anon", "empty becomes Anon"
    # Can round-trip through ast.parse as an attribute
    for raw in ("foo", "foo bar", "SA 0.1", "", "{}%1 ?\\r"):
        py = _py_identifier(raw)
        src = "class X:\n    def Set%s(self): pass\n" % py
        ast.parse(src)


def test_first_token_pulls_wire_verbs():
    assert _first_token("SARMC {}\r") == "SARMC"
    assert _first_token("GARMC\r") == "ARMC"[:0] + "GARMC"
    assert _first_token("ACK BTS {}\r") == "ACK"
    assert _first_token("43 42 01") == "CB"
    assert _first_token("43 4D 01 10") == "CM"
    assert _first_token("51 44 53 FF") == "QD"
    assert _first_token("53 42 01 FF") == "SB"


def test_name_from_label_matches_eventhandler_shape():
    assert _name_from_label("Controls.BTConnect.EventHandler") == "BTConnect"
    assert _name_from_label("BTConnect.EventHandler") == "BTConnect"
    assert _name_from_label("ARM.EventHandler") == "ARM"
    assert _name_from_label("Controls[].EventHandler") == "", "array labels are opaque"
    assert _name_from_label("phantom[].EventHandler") == ""
    assert _name_from_label("PollCommands") == "", "non-handler labels do not match"
    assert _name_from_label("") == ""


def test_derive_name_prefers_label_over_wire_token():
    """Byte-level commands get useful names via the plugin control label."""
    bt_wire = BridgedTemplate(kind="bytes", canonical="43 42 01",
                              label="Controls.BTConnect.EventHandler")
    assert _derive_name(bt_wire) == "BTConnect"
    bt_no_label = BridgedTemplate(kind="bytes", canonical="43 42 01", label="")
    assert _derive_name(bt_no_label) == "CB", "wire-prefix fallback"


def test_is_update_recognises_polling_labels():
    assert _is_update(BridgedTemplate(kind="text", canonical="QC\r", label="PollCommands"))
    assert _is_update(BridgedTemplate(kind="text", canonical="QC\r", label="queryDevice"))
    assert _is_update(BridgedTemplate(kind="text", canonical="QC\r", label="InitCommands"))
    assert not _is_update(BridgedTemplate(kind="text", canonical="SARMC {}\r",
                                          label="ARM.EventHandler"))


def test_merge_sg_pairs_folds_matched_tails():
    commands = {
        "SARMC": BridgedCommand(name="SARMC",
            set_templates=[BridgedTemplate(kind="text", canonical="SARMC {}\r", label="")]),
        "GARMC": BridgedCommand(name="GARMC",
            update_templates=[BridgedTemplate(kind="text", canonical="GARMC\r", label="")]),
        "LOAD":  BridgedCommand(name="LOAD",  # no pair
            set_templates=[BridgedTemplate(kind="text", canonical="LOAD 0\r", label="")]),
    }
    merged = _merge_sg_pairs(commands)
    assert set(merged) == {"ARMC", "LOAD"}, merged.keys()
    assert len(merged["ARMC"].set_templates) == 1
    assert len(merged["ARMC"].update_templates) == 1


def test_merge_sg_pairs_leaves_singletons_alone():
    """'SAVE' with no 'GAVE' twin stays named 'SAVE'. Nothing merges silently."""
    commands = {
        "SAVE": BridgedCommand(name="SAVE",
            set_templates=[BridgedTemplate(kind="text", canonical="SAVE 0\r", label="")]),
    }
    merged = _merge_sg_pairs(commands)
    assert set(merged) == {"SAVE"}


# ---------------------------------------------------------------------------
# qplug_to_cs pure-function tests
# ---------------------------------------------------------------------------

def test_text_literal_escapes_control_bytes():
    assert _text_literal_to_pysrc("SARMC {}\r") == r"'SARMC {}\r'"
    assert _text_literal_to_pysrc("line1\nline2") == r"'line1\nline2'"


def test_bytes_literal_prefers_printable_ascii():
    """A bytes-wire template emits a bytes literal with printable chars where
    possible and \\xNN for everything else. 'CM 01 10' -> b'CM\\x01\\x10'."""
    assert _bytes_literal_to_pysrc("43 4D 01 10") == r"b'CM\x01\x10'"
    assert _bytes_literal_to_pysrc("53 42 01 FF") == r"b'SB\x01\xFF'"
    assert _bytes_literal_to_pysrc("43 42 0B ??") == r"b'CB\x0B\x00'", \
        "?? slot bytes become \\x00 placeholders"


def test_emit_cmd_expr_handles_slot_counts():
    """Zero slots is a bare literal; one slot formats value; two or more
    slots pulls earlier slots from qualifier."""
    zero = BridgedTemplate(kind="text", canonical="GARMC\r", label="")
    one = BridgedTemplate(kind="text", canonical="SARMC {}\r", label="",
                          slots=["slot:ctl.Value"])
    two = BridgedTemplate(kind="text", canonical="PP {} {}\r", label="",
                          slots=["slot:numloop:i", "slot:ctl.Value"])
    expr, uses, n = _emit_cmd_expr(zero, "value")
    assert not uses and n == 0 and expr == r"'GARMC\r'"
    expr, uses, n = _emit_cmd_expr(one, "value")
    assert uses and n == 1 and expr == r"'SARMC {}\r'.format(value)"
    expr, uses, n = _emit_cmd_expr(two, "value")
    assert uses and n == 2
    assert "qualifier.get('Slot1', '')" in expr and expr.endswith(", value)")


def test_lua_pattern_to_py_covers_the_classes_we_see():
    assert _lua_pattern_to_py("%d") == r"\d"
    assert _lua_pattern_to_py("%a+") == "[A-Za-z]+"
    assert _lua_pattern_to_py("%w+") == r"\w+"
    assert _lua_pattern_to_py("B(%d+)=(%d)") == r"B(\d+)=(\d)"
    assert _lua_pattern_to_py("CH(%d) (%d+) (%d+) (%d+)") == r"CH(\d) (\d+) (\d+) (\d+)"
    # Lua's '-' means non-greedy *; a bare space stays literal
    assert _lua_pattern_to_py(".-") == r".*?"


def test_rename_colliding_disambiguates_folded_names():
    """Two IR commands whose names fold to the same Python identifier (via
    _py_identifier) must get distinct method names in the emitted module."""
    m = BridgedModule(plugin={}, transports=["tcp"], commands={
        "%1CLSS": BridgedCommand(name="%1CLSS",
            set_templates=[BridgedTemplate(kind="text", canonical="%1CLSS?\r", label="")]),
        "{}%1CLSS ?\r": BridgedCommand(name="{}%1CLSS ?\r",
            set_templates=[BridgedTemplate(kind="text", canonical="{}%1CLSS ?\r", label="")]),
    })
    m2 = _rename_colliding(m)
    pys = sorted({_py_identifier(n) for n in m2.commands})
    assert len(pys) == len(m2.commands), "collision not resolved: %r" % pys


# ---------------------------------------------------------------------------
# AST invariants on the EMITTED module
# ---------------------------------------------------------------------------

def _emit_from_qplug(path):
    with open(path, "r", encoding="utf-8") as f:
        src = f.read()
    return emit(from_qwire(extract(src, path)))


def _parse(src):
    try:
        return ast.parse(src)
    except SyntaxError as e:
        raise AssertionError("emitted module failed to parse: %s" % e)


def _method_names(cls: ast.ClassDef):
    return [m.name for m in cls.body if isinstance(m, ast.FunctionDef)]


def test_minimal_bridgedmodule_emits_a_valid_class():
    """Nothing-but-plugin-info -> an empty-but-loadable DeviceClass."""
    bm = BridgedModule(plugin={"Manufacturer": "Acme", "Name": "Widget", "Version": "1.0"},
                       transports=["tcp"])
    src = emit(bm)
    tree = _parse(src)
    cls_names = sorted(n.name for n in tree.body if isinstance(n, ast.ClassDef))
    assert cls_names == ["DeviceClass", "EthernetClass"], cls_names


def test_default_transport_falls_back_to_tcp_ethernet():
    bm = BridgedModule(plugin={"Manufacturer": "", "Name": ""}, transports=[])
    src = emit(bm)
    assert "class EthernetClass(EthernetClientInterface" in src


def test_serial_transport_emits_both_classes():
    bm = BridgedModule(plugin={"Manufacturer": "", "Name": ""}, transports=["serial", "tcp"])
    src = emit(bm)
    assert "class SerialClass(SerialInterface" in src
    assert "class EthernetClass(EthernetClientInterface" in src


def test_emitted_commands_have_no_duplicate_method_names_across_library():
    lib = _vendor("qsys_library_dir")
    if not lib:
        return "SKIP"
    files = sorted(f for root, _, fs in os.walk(lib) for f in
                   [os.path.join(root, x) for x in fs] if f.endswith(".qplug"))
    assert files, "library found but no .qplug files"
    for p in files:
        src = _emit_from_qplug(p)
        tree = _parse(src)
        for c in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
            methods = _method_names(c)
            dupes = sorted(set(m for m in methods if methods.count(m) > 1))
            assert not dupes, "duplicate methods in %s: %s" % (os.path.basename(p), dupes)


def test_rdl_btn_emits_without_duplicates():
    p = _vendor("rdl_btn_qplug")
    if not p:
        return "SKIP"
    src = _emit_from_qplug(p)
    tree = _parse(src)
    for c in [n for n in tree.body if isinstance(n, ast.ClassDef)]:
        methods = _method_names(c)
        dupes = sorted(set(m for m in methods if methods.count(m) > 1))
        assert not dupes, "RDL BTN duplicate methods: %s" % dupes


# ---------------------------------------------------------------------------
# Wire-table equivalence tests (the acceptance criterion)
# ---------------------------------------------------------------------------

def test_cdt100_generated_matches_plugin_wire_bytes():
    """Every text/bytes template in the generated module appears in the plugin's
    wire table. This is the acceptance criterion for Direction A."""
    plugin_p = _vendor("cdt100_qplug")
    if not plugin_p:
        return "SKIP"
    gen = _emit_from_qplug(plugin_p)
    # Extract the generated module's wire table via tools/wire_table.py
    gen_wt = wire_table.extract_table(gen, filename="<generated>")
    gen_templates = set()
    for rec in gen_wt.commands.values():
        for t in rec.set_templates:
            gen_templates.add(t.canonical)
        for t in rec.update_templates:
            gen_templates.add(t.canonical)
    assert gen_templates, "generated wire table had no templates"

    with open(plugin_p, "r", encoding="utf-8") as f:
        plugin_src = f.read()
    plug_wt = extract(plugin_src, plugin_p)
    plug_templates = {t.canonical for t in plug_wt.templates()}
    # Set subset
    missing = gen_templates - plug_templates
    assert not missing, (
        "generated templates not found in plugin:\n  %s" % "\n  ".join(sorted(missing)))


def test_rdl_btn_generated_matches_plugin_wire_bytes():
    plugin_p = _vendor("rdl_btn_qplug")
    if not plugin_p:
        return "SKIP"
    gen = _emit_from_qplug(plugin_p)
    gen_wt = wire_table.extract_table(gen, filename="<generated>")
    gen_templates = set()
    for rec in gen_wt.commands.values():
        for t in rec.set_templates:
            gen_templates.add(t.canonical)
        for t in rec.update_templates:
            gen_templates.add(t.canonical)
    assert gen_templates, "RDL BTN emitted no templates"

    with open(plugin_p, "r", encoding="utf-8") as f:
        plugin_src = f.read()
    plug_wt = extract(plugin_src, plugin_p)
    plug_templates = {t.canonical for t in plug_wt.templates()}
    missing = gen_templates - plug_templates
    assert not missing, "RDL BTN missing in plugin: %s" % sorted(missing)


def test_match_handlers_decode_reply_parameters_not_stub_ok():
    """A simple prefix pattern like 'GARMC' is a command-name probe, not a
    full reply pattern. The emitter augments it with `\\s*(.*?)\\r?\\n?$`
    so match.group(1) captures the reply parameter. The handler decodes
    that group as the status value instead of hard-coding 'OK'. Measured
    on 2026-10-26: the CDT100 pilot has 14 of 16 patterns in the simple-
    prefix shape and all 14 handlers now decode the real reply bytes."""
    plugin_p = _vendor("cdt100_qplug")
    if not plugin_p:
        return "SKIP"
    gen_src = _emit_from_qplug(plugin_p)
    # Count: for each __Match function, does the body write 'OK' or does
    # it write match.group(1).decode() ?
    tree = ast.parse(gen_src)
    cls = next(n for n in ast.walk(tree)
               if isinstance(n, ast.ClassDef) and n.name == "DeviceClass")
    stub_handlers = []
    decoded_handlers = []
    for fn in [n for n in cls.body if isinstance(n, ast.FunctionDef)]:
        # dunder-mangled: `__MatchXxx` -> `_DeviceClass__MatchXxx` after
        # class body eval; here we're reading the source AST so names
        # survive as `_DeviceClass__MatchXxx` only after exec. Read the
        # raw AST name.
        if not fn.name.startswith("_DeviceClass__Match") and not fn.name.startswith("__Match"):
            continue
        body_src = ast.unparse(fn)
        if "value = 'OK'" in body_src:
            stub_handlers.append(fn.name)
        elif "match.group(1)" in body_src or "match.group(0)" in body_src:
            decoded_handlers.append(fn.name)
    assert decoded_handlers, (
        "No __Match handlers decode reply bytes; the emitter regressed to "
        "stub-only outputs. stub=%r decoded=%r" % (stub_handlers, decoded_handlers))
    # 14+ decoded on the CDT100 pilot per the 2026-10-26 measurement.
    assert len(decoded_handlers) >= 10, (
        "Expected at least 10 decoded __Match handlers on the CDT100 pilot; "
        "got %d. decoded=%r stub=%r" %
        (len(decoded_handlers), decoded_handlers, stub_handlers))


def test_multi_slot_set_methods_do_not_raise_on_qualifier_none():
    """Multi-slot SetXxx bodies call `qualifier.get('Slot1')...` and raise
    AttributeError if the caller passes qualifier=None. Finding 14 shape:
    wire-correct, resolves cleanly, static checks pass, raises at runtime.
    exec_harness caught this on 5 of the generated CDT100 commands on
    2026-10-25; the emitter now inserts `if qualifier is None: qualifier = {}`
    at the top of any multi-slot body. Lock the invariant in."""
    plugin_p = _vendor("cdt100_qplug")
    if not plugin_p:
        return "SKIP"
    gen_src = _emit_from_qplug(plugin_p)
    # Load the generated module as a namespace, then invoke every SetXxx
    # method with qualifier=None. The method only needs to not raise
    # AttributeError BEFORE reaching __SetHelper (which hits a stubbed
    # extronlib if we had one; here we patch SetHelper to a no-op so the
    # test isolates the pre-helper qualifier logic).
    # The generated module imports `extronlib`. Install exec_harness's stub
    # into sys.modules first so the import resolves without a real extronlib.
    sys.path.insert(0, os.path.join(ROOT, "experiments", "exec_harness"))
    import extronlib_stub
    extronlib_stub.install()
    try:
        ns = {}
        exec(compile(gen_src, "<generated-cdt100>", "exec"),
             {"__name__": "__generated__"}, ns)
    finally:
        extronlib_stub.uninstall()
    # Replace extronlib-dependent helpers with no-ops.
    cls = ns["DeviceClass"]
    cls._DeviceClass__SetHelper = lambda self, cmd, cs, v, q: None
    cls._DeviceClass__UpdateHelper = lambda self, cmd, cs, v, q: None
    instance = cls.__new__(cls)
    offenders = []
    for name in dir(instance):
        if not name.startswith("Set") or name in ("Set",):
            continue
        try:
            getattr(instance, name)("probe", None)
        except AttributeError as e:
            offenders.append((name, str(e)))
        except Exception:
            # Other exceptions (TypeError, ValueError on int()) are allowed:
            # the regression target is AttributeError from None.get, not every
            # runtime path.
            pass
    assert not offenders, (
        "Multi-slot Set methods raised AttributeError on qualifier=None:\n  "
        + "\n  ".join("%s: %s" % o for o in offenders))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    # bridge_ir pure
    test_py_identifier_folds_hostile_input,
    test_first_token_pulls_wire_verbs,
    test_name_from_label_matches_eventhandler_shape,
    test_derive_name_prefers_label_over_wire_token,
    test_is_update_recognises_polling_labels,
    test_merge_sg_pairs_folds_matched_tails,
    test_merge_sg_pairs_leaves_singletons_alone,
    # qplug_to_cs pure
    test_text_literal_escapes_control_bytes,
    test_bytes_literal_prefers_printable_ascii,
    test_emit_cmd_expr_handles_slot_counts,
    test_lua_pattern_to_py_covers_the_classes_we_see,
    test_rename_colliding_disambiguates_folded_names,
    # Emitted module AST
    test_minimal_bridgedmodule_emits_a_valid_class,
    test_default_transport_falls_back_to_tcp_ethernet,
    test_serial_transport_emits_both_classes,
    test_emitted_commands_have_no_duplicate_method_names_across_library,
    test_rdl_btn_emits_without_duplicates,
    # Acceptance
    test_cdt100_generated_matches_plugin_wire_bytes,
    test_rdl_btn_generated_matches_plugin_wire_bytes,
    # Reply decoding
    test_match_handlers_decode_reply_parameters_not_stub_ok,
    # Runtime regression
    test_multi_slot_set_methods_do_not_raise_on_qualifier_none,
]


def main():
    passed = failed = skipped = 0
    for fn in TESTS:
        try:
            result = fn()
            if result == "SKIP":
                print("SKIP %s - vendor input absent" % fn.__name__)
                skipped += 1
            else:
                print("PASS %s" % fn.__name__)
                passed += 1
        except AssertionError as e:
            failed += 1
            print("FAIL %s - %r" % (fn.__name__, e))
        except Exception:
            failed += 1
            print("FAIL %s - exception:" % fn.__name__)
            traceback.print_exc()
    total = passed + failed + skipped
    print("%d passed, %d failed, %d skipped, %d total" % (passed, failed, skipped, total))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
