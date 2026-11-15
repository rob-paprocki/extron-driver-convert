#!/usr/bin/env python3
"""
test_cs_to_qplug.py - tests for cs_to_qplug (Direction B: Extron -> Q-SYS).

Pattern matches test_qplug_wire.py / test_qplug_to_cs.py: assert-based,
stdlib only, run as `python -u experiments/qsys/test_cs_to_qplug.py`.

Vendor-input tests (comparing against the DTP3 ControlScript module) skip
gracefully when the file is not present on disk.
"""
from __future__ import annotations

import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from cs_to_qplug import (
    DTP3_CP_42,
    DTP3_CP_62,
    DTP3_CP_884,
    DTP3_FAMILY,
    PluginSpec,
    _lua_str,
    emit,
)
from qplug_wire import extract


VENDOR_FILES = {
    "dtp3_884": "corpus/extron-gs-modules/09062026/extr_matrix_DTP3_CrossPoint_884_Series_v1_7_00.py",
    "dtp3_42":  "corpus/extron-gs-modules/09062026/extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py",
    "dtp3_62":  "corpus/extron-gs-modules/09062026/extr_matrix_DTP3_CrossPoint_6x2_Series_v1_1_00.py",
}


def _vendor(key: str) -> str | None:
    p = os.path.join(ROOT, VENDOR_FILES[key])
    return p if os.path.exists(p) else None


# ---------------------------------------------------------------------------
# Lua rendering primitives
# ---------------------------------------------------------------------------

def test_lua_str_escapes_the_control_bytes_we_write():
    assert _lua_str("abc") == '"abc"'
    assert _lua_str("line1\r\n") == '"line1\\r\\n"'
    assert _lua_str("quote\"inside") == '"quote\\"inside"'
    assert _lua_str("back\\slash") == '"back\\\\slash"'


# ---------------------------------------------------------------------------
# Spec sanity
# ---------------------------------------------------------------------------

def test_known_specs_have_coherent_topology():
    assert DTP3_CP_884.inputs == 8 and DTP3_CP_884.outputs == 8
    assert DTP3_CP_42.inputs == 4 and DTP3_CP_42.outputs == 2
    assert DTP3_CP_62.inputs == 6 and DTP3_CP_62.outputs == 2
    # Serial insertion on by default
    assert DTP3_CP_884.serial_insertion
    # Default SIS port
    assert DTP3_CP_884.default_port == 23
    # Each has a distinct ID
    assert len({DTP3_CP_884.plugin_id, DTP3_CP_42.plugin_id, DTP3_CP_62.plugin_id}) == 3


# ---------------------------------------------------------------------------
# The emitter: structural invariants
# ---------------------------------------------------------------------------

def test_emit_produces_the_required_top_level_block():
    src = emit(DTP3_CP_884)
    # The five required Q-SYS plugin blocks
    assert "PluginInfo = {" in src
    assert "function GetProperties()" in src
    assert "function GetControls(props)" in src
    assert "function GetPages(props)" in src
    assert "function GetControlLayout(props)" in src
    assert "if Controls then" in src


def test_emit_pluginfo_fields_match_the_spec():
    spec = DTP3_CP_884
    src = emit(spec)
    assert _lua_str(spec.name) in src
    assert _lua_str(spec.plugin_id) in src
    assert _lua_str(spec.manufacturer) in src
    assert _lua_str(spec.model) in src


def test_emit_runtime_uses_the_sis_tie_grammar():
    """The main acceptance: tie commands take Extron's '<in>*<out><ch>' form,
    with ch = ! (A+V), % (Vid), $ (Aud)."""
    src = emit(DTP3_CP_884)
    assert '"!"' in src
    assert '"%"' in src
    assert '"$"' in src
    # And the format string itself
    assert "string.format(\"%d*%d%s\\r\\n\"" in src


def test_emit_runtime_opens_per_output_serial_sockets_when_enabled():
    src = emit(DTP3_CP_884)
    # Signals that per-output serial channels are wired
    assert "Serial Base Port" in src
    assert "s:Connect(IP, SPORT + o)" in src
    assert "Controls.SerialSend[o].EventHandler" in src
    assert "Controls.SerialReceived[o]" in src


def test_emit_omits_serial_controls_from_getcontrols_when_disabled():
    """serial_insertion=False drops SerialSend/SerialReceived/SerialClear from
    GetControls (which the Core instantiates); the runtime's SINS guard
    doesn't fire so those controls are never referenced at runtime either."""
    spec = PluginSpec(**{**DTP3_CP_884.__dict__, "serial_insertion": False})
    off = emit(spec)
    # Isolate the GetControls block
    gc_start = off.index("function GetControls(props)")
    gc_end   = off.index("end", gc_start)
    gc_block = off[gc_start:gc_end]
    assert "SerialSend" not in gc_block, "SerialSend declared despite serial_insertion=False"
    assert "SerialReceived" not in gc_block
    assert "SerialClear" not in gc_block
    # Properties block also drops the Serial Insertion toggle
    gp_start = off.index("function GetProperties")
    gp_end   = off.index("end", gp_start)
    gp_block = off[gp_start:gp_end]
    assert "Serial Insertion" not in gp_block
    assert "Serial Base Port" not in gp_block


def test_emit_scales_control_counts_by_topology():
    """A 4x2 plugin advertises Count=4 inputs and Count=2 outputs."""
    src_884 = emit(DTP3_CP_884)
    src_42  = emit(DTP3_CP_42)
    assert "Count = 8" in src_884, "884 should advertise Count=8 somewhere"
    assert "Count = 4" in src_42, "42 should advertise Count=4 somewhere"
    # 42 should NOT advertise Count = 8 as any per-I/O control. Skip
    # TieMatrixCell, which is INPUTS*OUTPUTS and legitimately 8 for a 4x2.
    import re
    for line in src_42.splitlines():
        if "TieMatrixCell" in line:
            continue
        m = re.search(r"Count\s*=\s*(\d+)", line)
        if m and m.group(1) == "8":
            raise AssertionError(
                "a 4x2 plugin should not have any non-matrix Count=8 declarations:\n  "
                + line.strip())


# ---------------------------------------------------------------------------
# Round-trip through qplug_wire: the emitted plugin IS a valid plugin
# ---------------------------------------------------------------------------

def _wire_table_of_emitted(spec):
    src = emit(spec)
    qt = extract(src, "<generated>")
    return qt


def test_emitted_dtp3_884_parses_without_opaque_slots():
    qt = _wire_table_of_emitted(DTP3_CP_884)
    assert qt.stats["opaque_templates"] == 0, qt.stats
    assert qt.stats["templates"] > 10
    assert "tcp" in qt.stats["transports"]


def test_emitted_dtp3_884_carries_the_three_tie_forms():
    qt = _wire_table_of_emitted(DTP3_CP_884)
    canonicals = {t.canonical for t in qt.templates()}
    assert "{}*{}!\r\n" in canonicals, "A+V tie template missing"
    assert "{}*{}%\r\n" in canonicals, "Vid-only tie template missing"
    assert "{}*{}$\r\n" in canonicals, "Aud-only tie template missing"


def test_emitted_dtp3_884_carries_the_system_commands():
    qt = _wire_table_of_emitted(DTP3_CP_884)
    canonicals = {t.canonical for t in qt.templates()}
    assert "{}X" in canonicals, "ExecutiveMode set missing"
    assert "X" in canonicals, "ExecutiveMode query missing"
    assert "{}." in canonicals, "PresetRecall missing"
    assert "w{}*{}VMUT\r\n" in canonicals, "VideoMute set missing"
    assert "w{}*VMUT\r\n" in canonicals, "VideoMute query missing"


def test_emitted_dtp3_884_names_the_io_name_commands():
    qt = _wire_table_of_emitted(DTP3_CP_884)
    canonicals = {t.canonical for t in qt.templates()}
    # Both queries and writes
    assert "wNmi{},\r\n" in canonicals
    assert "wNmo{},\r\n" in canonicals
    assert "wNmi{},{}\r\n" in canonicals
    assert "wNmo{},{}\r\n" in canonicals


def test_emitted_variants_all_round_trip():
    for spec in (DTP3_CP_884, DTP3_CP_42, DTP3_CP_62):
        qt = _wire_table_of_emitted(spec)
        assert qt.stats["opaque_templates"] == 0, (spec.model, qt.stats)
        assert qt.stats["templates"] > 10, (spec.model, qt.stats)


# ---------------------------------------------------------------------------
# Acceptance: compare the emitted plugin against the shipped Extron module
# ---------------------------------------------------------------------------

def _module_canonicals(path):
    import wire_table
    with open(path, "r", encoding="utf-8") as f:
        wt = wire_table.extract_table(f.read(), path)
    out = set()
    for rec in wt.commands.values():
        for t in rec.set_templates: out.add(t.canonical)
        for t in rec.update_templates: out.add(t.canonical)
    return out


def test_emitted_tie_forms_are_subsumed_by_the_module_forms():
    """The module's MatrixTieCommand has two canonicals:
    '{}*{}\\r\\n' and '{}*{}{}\\r\\n'. Our three explicit-char forms
    ('{}*{}!\\r\\n', '{}*{}%\\r\\n', '{}*{}$\\r\\n') are specialisations
    of the second one. We check that: for each of our three tie forms, the
    module side has at least the slot-generalised form in its wire table."""
    p = _vendor("dtp3_884")
    if not p:
        return "SKIP"
    mod = _module_canonicals(p)
    assert "{}*{}{}\r\n" in mod, "module's three-slot tie form missing"


def test_emitted_videomute_and_execmode_match_module_bytes_exactly():
    """These are the v1-scope commands we picked specifically because the
    module uses the plain SIS forms with no ladder-steering. Our emitted
    byte-exactly matches."""
    p = _vendor("dtp3_884")
    if not p:
        return "SKIP"
    mod = _module_canonicals(p)
    qt = _wire_table_of_emitted(DTP3_CP_884)
    ours = {t.canonical for t in qt.templates()}
    assert ("w{}*{}VMUT\r\n" in ours) and ("w{}*{}VMUT\r\n" in mod)
    assert ("w{}*VMUT\r\n" in ours) and ("w{}*VMUT\r\n" in mod)
    assert ("X" in ours) and ("X" in mod)
    assert ("{}." in ours) and ("{}." in mod)


def test_emitted_dtp3_family_declares_amp_controls_and_wires_them():
    """DTP3 CrossPoint family IPCP A / SA / MA 70 variants have a built-in
    amplifier. The family plugin declares AmplifierAttenuation and
    AmplifierMute controls unconditionally (Count=2) so the index space is
    stable across models; the layout and runtime scope them to HAS_AMP."""
    src = emit(DTP3_FAMILY)
    # Control declarations
    assert 'Name = "AmplifierAttenuation"' in src, "AmplifierAttenuation control missing"
    assert 'Name = "AmplifierMute"' in src, "AmplifierMute control missing"
    assert "Count = 2" in src, "Amp controls should declare Count = 2"
    # Amp tab in page_tabs
    assert '"Amp"' in src, "'Amp' tab missing from page_tabs"
    # Layout branch
    assert 'elseif tab == "Amp" then' in src, "Amp tab layout branch missing"
    # SIS wire format in EventHandler and handleLine
    assert 'wG6002' in src, "AmplifierAttenuation set wire format missing"
    assert 'wM6002' in src, "AmplifierMute set wire format missing"
    assert "6002(2[67])" in src, "Amp reply match pattern missing"
    # HAS_AMP gate referenced in the layout
    assert "if HAS_AMP then" in src, "Amp tab body does not gate on HAS_AMP"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

TESTS = [
    test_lua_str_escapes_the_control_bytes_we_write,
    test_known_specs_have_coherent_topology,
    test_emit_produces_the_required_top_level_block,
    test_emit_pluginfo_fields_match_the_spec,
    test_emit_runtime_uses_the_sis_tie_grammar,
    test_emit_runtime_opens_per_output_serial_sockets_when_enabled,
    test_emit_omits_serial_controls_from_getcontrols_when_disabled,
    test_emit_scales_control_counts_by_topology,
    test_emitted_dtp3_884_parses_without_opaque_slots,
    test_emitted_dtp3_884_carries_the_three_tie_forms,
    test_emitted_dtp3_884_carries_the_system_commands,
    test_emitted_dtp3_884_names_the_io_name_commands,
    test_emitted_variants_all_round_trip,
    test_emitted_tie_forms_are_subsumed_by_the_module_forms,
    test_emitted_videomute_and_execmode_match_module_bytes_exactly,
    test_emitted_dtp3_family_declares_amp_controls_and_wires_them,
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
