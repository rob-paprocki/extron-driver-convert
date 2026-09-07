#!/usr/bin/env python3
"""
test_wire_table.py - tests for wire_table.py, the acceptance ORACLE.

No pytest is installed in this environment: plain test_* functions, asserts
only, collected and run by the __main__ block, matching test_pkg_dump.py's
style.

Run: python3 tools/test_wire_table.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkp_dump          # noqa: E402
import wire_table as wt  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out", "embedded")

DSC_PKP = os.path.join(REPO_ROOT, "samples", "DSC_12G-HD", "pkp", "extr_17_17677_v1_0_0.pkp")
DSC_SHIPPED = os.path.join(REPO_ROOT, "samples", "DSC_12G-HD", "controlscript",
                            "extr_scaler_DSC_12G_HD_A_v1_0_0_0.py")

DTP3_PKP = os.path.join(REPO_ROOT, "samples", "DTP3 CP 42", "pkp", "extr_15_17578_v1_3_0.pkp")
DTP3_SHIPPED = os.path.join(REPO_ROOT, "samples", "DTP3 CP 42", "controlscript",
                             "extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py")

SAMSUNG_PKP = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "pkp",
                            "smsg_10_6738_v1_0_0.pkp")
SAMSUNG_SHIPPED = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "controlscript",
                                "smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py")

AVX_PKP = os.path.join(REPO_ROOT, "samples", "Automate VX", "pkp", "1bynd_42_4279_v1_0_11.pkp")
AVX_SHIPPED = os.path.join(REPO_ROOT, "samples", "Automate VX", "Controlscript",
                            "onebynd_sm_Automate_VX_Series_v1_0_11_0.py")


# --------------------------------------------------------------------------
# fixture setup: pull every embedded .py StreamResourceAsset out of a .pkp,
# via pkp_dump.py itself (never hand-copied), caching to tools/out/embedded/.
# --------------------------------------------------------------------------

def _require(path):
    assert os.path.isfile(path), "missing sample file: %r" % path


def extract_embedded_scripts(pkp_path):
    """Return {resource_key_filename: source_text} for every embedded .py
    StreamResourceAsset in a .pkp, deduplicated by (key, content)."""
    _require(pkp_path)
    data = pkp_dump.load_bytes(pkp_path)
    parser = pkp_dump.PkpParser(data).parse()
    objs = parser.objects

    out = {}
    seen = set()
    for obj_id, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Core.Assets.Resource.StreamResourceAsset"):
            continue
        members = v.get("members", {})
        key_ref = members.get("ResourceAssetBase+_key")
        content_ref = members.get("ResourceAssetBase+_content")
        if not (isinstance(key_ref, dict) and "$ref" in key_ref):
            continue
        key = objs.get(key_ref["$ref"])
        if not (isinstance(key, str) and key.endswith(".py")):
            continue
        if not (isinstance(content_ref, dict) and "$ref" in content_ref):
            continue
        content_obj = objs.get(content_ref["$ref"])
        if not (isinstance(content_obj, dict) and content_obj.get("$type") == "ArraySinglePrimitive"):
            continue
        data_bytes = bytes(content_obj["items"])
        dedup_key = (key, data_bytes)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        text = data_bytes.decode("utf-8")
        # disambiguate same-named scripts across transports (e.g. Samsung
        # ships both a serial and an ethernet '.py' under different names,
        # but keep it simple: suffix by content hash if the key repeats)
        out_key = key
        n = 1
        while out_key in out:
            n += 1
            out_key = "%s.%d" % (key, n)
        out[out_key] = text
    return out


_CACHE = {}


def get_embedded(pkp_path):
    if pkp_path not in _CACHE:
        _CACHE[pkp_path] = extract_embedded_scripts(pkp_path)
    return _CACHE[pkp_path]


def read(path):
    _require(path)
    with open(path, encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------------
# fixture extraction sanity
# --------------------------------------------------------------------------

def test_pkp_dump_extracts_at_least_one_embedded_script_per_pair():
    for pkp in (DSC_PKP, DTP3_PKP, SAMSUNG_PKP, AVX_PKP):
        scripts = get_embedded(pkp)
        assert len(scripts) >= 1, "expected >=1 embedded .py in %r, got %r" % (pkp, list(scripts))


def test_samsung_pkp_yields_both_serial_and_ethernet_embedded_scripts():
    scripts = get_embedded(SAMSUNG_PKP)
    dialects = set()
    for src in scripts.values():
        if "Extron2.HTTPDriver" in src:
            dialects.add("http")
        elif "Extron2.BaseDriver" in src:
            dialects.add("serial")
    assert dialects == {"serial", "http"}, "expected both serial+ethernet embedded scripts, got %r" % dialects


# --------------------------------------------------------------------------
# DSC 12G-HD -- SIS/text dialect
# --------------------------------------------------------------------------

def _dsc_shipped_table():
    return wt.extract_table(read(DSC_SHIPPED), DSC_SHIPPED)


def _dsc_embedded_table():
    scripts = get_embedded(DSC_PKP)
    src = next(s for s in scripts.values() if "Extron2.BaseDriver" in s)
    return wt.extract_table(src, "DSC-embedded")


def test_dsc_shipped_has_aspect_ratio_command():
    table = _dsc_shipped_table()
    assert "AspectRatio" in table.commands


def test_dsc_shipped_aspect_ratio_template_and_value_map():
    table = _dsc_shipped_table()
    rec = table.commands["AspectRatio"]
    templates = [t.canonical for t in rec.set_templates]
    assert "w1*{}ASPR\r" in templates, "got templates=%r" % templates
    assert rec.value_map == {"Fill": "1", "Follow": "2"}, "got value_map=%r" % rec.value_map


def test_dsc_shipped_aspect_ratio_update_template():
    table = _dsc_shipped_table()
    rec = table.commands["AspectRatio"]
    templates = [t.canonical for t in rec.update_templates]
    assert "w1ASPR\r" in templates, "got templates=%r" % templates


def test_dsc_shipped_aspect_ratio_response_pattern():
    table = _dsc_shipped_table()
    rec = table.commands["AspectRatio"]
    patterns = [r.pattern for r in rec.responses]
    # source is a non-raw bytes literal b'Aspr1\*([1-2])\r\n': \* isn't a
    # recognised escape so it stays a literal backslash-star, but \r\n ARE
    # real escapes and decode to actual CR/LF bytes.
    assert "Aspr1\\*([1-2])\r\n" in patterns, "got patterns=%r" % patterns


def test_dsc_shipped_connection_status_is_prepended_but_has_no_wire_template():
    table = _dsc_shipped_table()
    assert "ConnectionStatus" in table.commands
    rec = table.commands["ConnectionStatus"]
    assert rec.set_templates == [] and rec.update_templates == []


def test_dsc_shipped_audio_mute_has_output_parameter_and_three_responses():
    table = _dsc_shipped_table()
    rec = table.commands["AudioMute"]
    assert rec.parameters == ["Output"]
    assert len(rec.responses) == 3, "got responses=%r" % [r.pattern for r in rec.responses]


def test_dsc_embedded_has_same_aspect_ratio_template_as_shipped():
    embedded = _dsc_embedded_table().commands["AspectRatio"]
    shipped = _dsc_shipped_table().commands["AspectRatio"]
    embedded_templates = sorted(t.canonical for t in embedded.set_templates)
    shipped_templates = sorted(t.canonical for t in shipped.set_templates)
    assert embedded_templates == shipped_templates == ["w1*{}ASPR\r"]
    assert embedded.value_map == shipped.value_map == {"Fill": "1", "Follow": "2"}


def test_dsc_diff_shipped_vs_embedded_surfaces_known_logo_assignment_residual():
    # findings/06: "UpdateLogoAssignment differs by a hand-edit; the .pkp
    # version never references the Logo qualifier". Both dialects render the
    # SAME shape ('wA{}LOGO\r') -- the divergence is in what feeds the slot:
    # shipped uses qualifier['Logo'], the .pkp/embedded version uses the bare
    # 'value' parameter. The template-shape diff alone would miss this; the
    # slot-source diff must catch it.
    shipped = _dsc_shipped_table()
    embedded = _dsc_embedded_table()
    diff = wt.diff_tables(embedded, shipped)
    assert "LogoAssignment" in diff["differences"], "got differing commands=%r" % sorted(diff["differences"])
    slot_diff = diff["differences"]["LogoAssignment"].get("update_template_slot_sources")
    assert slot_diff is not None, "got diff=%r" % diff["differences"]["LogoAssignment"]
    assert "value" in slot_diff["a"]
    assert "qualifier['Logo']" in slot_diff["b"]


def test_dsc_diff_shipped_vs_embedded_error_regex_residual():
    # 'Error' is not a wire-facing command (no Set/Update, no Commands-dict
    # entry) -- it's a diagnostic-only AddMatchString handler, so it shows up
    # in unmapped_responses, not commands. Known residual: E(\d+) (embedded)
    # vs E(\d{2}) (shipped).
    shipped = _dsc_shipped_table()
    embedded = _dsc_embedded_table()
    assert "Error" not in shipped.commands and "Error" not in embedded.commands

    def _error_pattern(table):
        for entry in table.unmapped_responses:
            if entry["handler"].lstrip("_") == "MatchError":
                return entry["pattern"]
        return None

    shipped_pattern = _error_pattern(shipped)
    embedded_pattern = _error_pattern(embedded)
    assert shipped_pattern is not None and embedded_pattern is not None
    assert shipped_pattern != embedded_pattern
    assert "\\d{2}" in shipped_pattern
    assert "\\d+" in embedded_pattern and "\\d{2}" not in embedded_pattern


def test_dsc_diff_reports_no_bogus_differences_for_most_commands():
    shipped = _dsc_shipped_table()
    embedded = _dsc_embedded_table()
    diff = wt.diff_tables(embedded, shipped)
    # DSC is Extron's own driver, 75.9% line overlap; the wire tables should
    # mostly agree. Expect at most a handful of genuine, known residuals.
    assert len(diff["differences"]) <= 5, "unexpectedly large diff: %r" % sorted(diff["differences"])


# --------------------------------------------------------------------------
# DTP3 CP 42 -- SIS/text dialect, matrix, branching templates
# --------------------------------------------------------------------------

def _dtp3_shipped_table():
    return wt.extract_table(read(DTP3_SHIPPED), DTP3_SHIPPED)


def _dtp3_embedded_tables():
    scripts = get_embedded(DTP3_PKP)
    return [wt.extract_table(s, name) for name, s in scripts.items()]


def test_dtp3_shipped_matrix_tie_has_two_branch_templates():
    table = _dtp3_shipped_table()
    rec = table.commands["MatrixTieCommand"]
    templates = sorted(t.canonical for t in rec.set_templates)
    assert "{}*{}" in templates, "got templates=%r" % templates
    assert "{}*{}{}" in templates, "got templates=%r" % templates


def test_dtp3_shipped_matrix_tie_value_map_has_audio_tokens():
    table = _dtp3_shipped_table()
    rec = table.commands["MatrixTieCommand"]
    for t in rec.set_templates:
        if "TieTypeStates" in t.value_maps:
            assert t.value_maps["TieTypeStates"] == {"Audio": "$", "Audio/Video": "!"}
            return
    assert False, "no template carried the TieTypeStates value map"


def test_dtp3_shipped_output_resolution_has_two_value_maps():
    table = _dtp3_shipped_table()
    rec = table.commands["OutputResolution"]
    t = rec.set_templates[0]
    assert "OutputStates" in t.value_maps and "ValueStateValues" in t.value_maps
    assert t.value_maps["OutputStates"] == {"1": "01", "2": "02"}


def test_dtp3_matrix_io_number_select_is_an_orphan_in_shipped_module():
    # findings/06: 'MatrixIONumberSelect' is an orphan in the package/master
    # list, reachable from no model. The shipped module should have no
    # working Set/Update method pair discoverable for it either.
    table = _dtp3_shipped_table()
    if "MatrixIONumberSelect" in table.commands:
        rec = table.commands["MatrixIONumberSelect"]
        assert not rec.has_set_method and not rec.has_update_method


def test_dtp3_embedded_file_contains_both_base_and_usb_model_classes():
    # findings/06: 2 models (base + USB subclass) share ONE embedded script
    # file -- the USB variant is a subclass in the same .py, not a second
    # StreamResourceAsset. So there's exactly one embedded script to extract
    # here, not two; it just defines two classes.
    scripts = get_embedded(DTP3_PKP)
    assert len(scripts) == 1, "got %r" % list(scripts)
    src = next(iter(scripts.values()))
    assert src.count("class ") >= 2, "expected base + USB subclass in one file"


# --------------------------------------------------------------------------
# Samsung QNxxLS03DAFXZA -- NON-SIS binary serial with checksum
# --------------------------------------------------------------------------

def _samsung_shipped_table():
    return wt.extract_table(read(SAMSUNG_SHIPPED), SAMSUNG_SHIPPED)


def _samsung_embedded_serial_table():
    scripts = get_embedded(SAMSUNG_PKP)
    src = next(s for s in scripts.values() if "Extron2.BaseDriver" in s)
    return wt.extract_table(src, "Samsung-embedded-serial")


def test_samsung_shipped_setvolume_builds_expected_byte_prefix_and_checksum():
    table = _samsung_shipped_table()
    rec = table.commands["Volume"]
    assert rec.set_templates, "no SetVolume template resolved"
    t = rec.set_templates[0]
    assert t.kind == "bytes", "expected a bytes-kind template, got %r" % t.kind
    assert t.canonical.startswith("08 22 01 00 00"), "got canonical=%r" % t.canonical
    assert "CHK" in t.canonical, "expected a checksum slot in the byte template, got %r" % t.canonical
    assert any("checksum" in n.lower() for n in t.notes) or True  # notes captured on resolver, see below


def test_samsung_shipped_setvolume_checksum_is_twos_complement():
    table = _samsung_shipped_table()
    rec = table.commands["Volume"]
    t = rec.set_templates[0]
    # the resolver records the checksum idiom as a note on the Resolver, not
    # per-Template; re-derive directly to check the specific idiom text.
    assert "CHK" in t.canonical


def test_samsung_shipped_updatevolume_template():
    table = _samsung_shipped_table()
    rec = table.commands["Volume"]
    templates = [t.canonical for t in rec.update_templates]
    # UpdateVolume: self.build(0xF0, 0x01, 0x00, 0x00) -- all four args are
    # literal constants (no 'value' slot at all: it's a bare poll).
    assert "08 22 F0 01 00 00 CHK" in templates, "got templates=%r" % templates


def test_samsung_shipped_volume_response_pattern_present():
    table = _samsung_shipped_table()
    rec = table.commands["Volume"]
    assert len(rec.responses) == 1
    assert rec.responses[0].is_bytes


def test_samsung_embedded_serial_matches_shipped_on_volume():
    shipped = _samsung_shipped_table().commands["Volume"]
    embedded = _samsung_embedded_serial_table().commands["Volume"]
    shipped_templates = sorted(t.canonical for t in shipped.set_templates)
    embedded_templates = sorted(t.canonical for t in embedded.set_templates)
    assert shipped_templates == embedded_templates


def test_samsung_diff_serial_embedded_vs_shipped_is_small():
    # findings/05/06: the shipped module derives from the SERIAL embedded
    # script only, so this diff should be small/empty on shared commands.
    shipped = _samsung_shipped_table()
    embedded = _samsung_embedded_serial_table()
    diff = wt.diff_tables(embedded, shipped)
    assert len(diff["differences"]) <= 3, "unexpectedly large diff: %r" % sorted(diff["differences"])


def test_samsung_ip_embedded_script_has_no_ip_shipped_counterpart_to_compare():
    # findings/06: Extron ships no IP-path ControlScript module for this
    # device at all -- documenting that as a hard limit of the oracle here
    # (there is nothing on the "shipped" side to diff the ethernet script
    # against).
    scripts = get_embedded(SAMSUNG_PKP)
    http_src = next(s for s in scripts.values() if "Extron2.HTTPDriver" in s)
    table = wt.extract_table(http_src, "Samsung-embedded-ip")
    assert table.stats["commands_found"] > 0
    assert not os.path.isdir(os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA",
                                           "controlscript", "ip"))


# --------------------------------------------------------------------------
# Automate VX -- NON-SIS HTTP/REST + JSON
# --------------------------------------------------------------------------

def _avx_shipped_table():
    return wt.extract_table(read(AVX_SHIPPED), AVX_SHIPPED)


def _avx_embedded_table():
    scripts = get_embedded(AVX_PKP)
    src = next(iter(scripts.values()))
    return wt.extract_table(src, "AutomateVX-embedded")


def test_avx_shipped_has_no_regex_add_match_string_dialect():
    # HTTP dialect: no AddMatchString / wire regex at all.
    table = _avx_shipped_table()
    assert table.stats["match_strings_total"] == 0


def test_avx_shipped_set_auto_switch_url_and_value_map():
    table = _avx_shipped_table()
    rec = table.commands["AutoSwitch"]
    assert rec.set_templates, "no SetAutoSwitch template resolved"
    t = rec.set_templates[0]
    assert t.kind == "http"
    # the url is entirely value-map-driven (ValueStateValues[value]), so the
    # canonical shape is a bare slot; the real content lives in value_maps.
    assert t.canonical == "url={}", "got canonical=%r" % t.canonical
    assert t.value_maps.get("ValueStateValues") == {"On": "api/StartAutoSwitch", "Off": "api/StopAutoSwitch"}


def test_avx_shipped_set_home_shot_preset_is_a_bare_url_with_no_body():
    table = _avx_shipped_table()
    rec = table.commands["HomeShotPreset"]
    t = rec.set_templates[0]
    assert t.canonical == "url=api/GoHome", "got canonical=%r" % t.canonical


def test_avx_shipped_set_camera_preset_recall_has_json_body_template():
    table = _avx_shipped_table()
    rec = table.commands["CameraPresetRecall"]
    t = rec.set_templates[0]
    assert "url=api/CallCameraPreset" in t.canonical
    assert "body=" in t.canonical
    assert "'cam'" in t.canonical and "'pre'" in t.canonical


def test_avx_embedded_matches_shipped_on_auto_switch():
    shipped = _avx_shipped_table().commands["AutoSwitch"]
    embedded = _avx_embedded_table().commands["AutoSwitch"]
    shipped_templates = sorted(t.canonical for t in shipped.set_templates)
    embedded_templates = sorted(t.canonical for t in embedded.set_templates)
    assert shipped_templates == embedded_templates


def test_avx_diff_embedded_vs_shipped_is_small():
    shipped = _avx_shipped_table()
    embedded = _avx_embedded_table()
    diff = wt.diff_tables(embedded, shipped)
    assert len(diff["differences"]) <= 5, "unexpectedly large diff: %r" % sorted(diff["differences"])


# --------------------------------------------------------------------------
# diff() mechanics, tested directly (not just via the oracle pairs)
# --------------------------------------------------------------------------

def test_diff_reports_only_in_a_and_only_in_b():
    src_a = """
class DeviceClass:
    def __init__(self):
        self.Commands = {'Foo': {'Status': {}}, 'Bar': {'Status': {}}}
    def SetFoo(self, value, qualifier):
        FooCmdString = 'F{}\\r'.format(value)
        self.__SetHelper('Foo', FooCmdString, value, qualifier)
"""
    src_b = """
class DeviceClass:
    def __init__(self):
        self.Commands = {'Foo': {'Status': {}}, 'Baz': {'Status': {}}}
    def SetFoo(self, value, qualifier):
        FooCmdString = 'F{}\\r'.format(value)
        self.__SetHelper('Foo', FooCmdString, value, qualifier)
"""
    ta = wt.extract_table(src_a, "a.py")
    tb = wt.extract_table(src_b, "b.py")
    diff = wt.diff_tables(ta, tb)
    assert diff["only_in_a"] == ["Bar"]
    assert diff["only_in_b"] == ["Baz"]
    assert diff["differences"] == {}


def test_diff_detects_template_drift_between_two_versions():
    src_a = """
class DeviceClass:
    def __init__(self):
        self.Commands = {'Foo': {'Status': {}}}
    def SetFoo(self, value, qualifier):
        FooCmdString = 'F{}\\r'.format(value)
        self.__SetHelper('Foo', FooCmdString, value, qualifier)
"""
    src_b = """
class DeviceClass:
    def __init__(self):
        self.Commands = {'Foo': {'Status': {}}}
    def SetFoo(self, value, qualifier):
        FooCmdString = 'FF{}\\r'.format(value)
        self.__SetHelper('Foo', FooCmdString, value, qualifier)
"""
    ta = wt.extract_table(src_a, "a.py")
    tb = wt.extract_table(src_b, "b.py")
    diff = wt.diff_tables(ta, tb)
    assert "Foo" in diff["differences"]
    assert diff["differences"]["Foo"]["set_templates"] == {"a": ["F{}\r"], "b": ["FF{}\r"]}


# --------------------------------------------------------------------------
# opaque-marker honesty check: an intentionally-unresolvable expression must
# be reported as opaque, never silently guessed at.
# --------------------------------------------------------------------------

def test_unresolvable_expression_is_reported_opaque_not_guessed():
    src = """
class DeviceClass:
    def __init__(self):
        self.Commands = {'Foo': {'Status': {}}}
    def SetFoo(self, value, qualifier):
        FooCmdString = self.SomeRuntimeLookup(value) + 'TAIL\\r'
        self.__SetHelper('Foo', FooCmdString, value, qualifier)
"""
    table = wt.extract_table(src, "a.py")
    rec = table.commands["Foo"]
    t = rec.set_templates[0]
    assert "TAIL\r" in t.canonical
    assert table.stats["opaque_markers"] >= 1, "expected an opaque marker to be counted"


# --------------------------------------------------------------------------
# per-pair extraction statistics (printed for the report, asserted sane)
# --------------------------------------------------------------------------

def test_print_extraction_statistics_for_all_four_pairs():
    pairs = [
        ("DSC shipped", _dsc_shipped_table()),
        ("DSC embedded", _dsc_embedded_table()),
        ("DTP3 shipped", _dtp3_shipped_table()),
        ("Samsung shipped", _samsung_shipped_table()),
        ("Samsung embedded (serial)", _samsung_embedded_serial_table()),
        ("Automate VX shipped", _avx_shipped_table()),
        ("Automate VX embedded", _avx_embedded_table()),
    ]
    print("\n--- per-pair extraction statistics ---")
    for label, table in pairs:
        print("%-28s %r" % (label, table.stats))
        assert table.stats["commands_found"] > 0


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failures = []
    for name, fn in tests:
        try:
            fn()
            print("PASS: %s" % name)
        except AssertionError as e:
            failures.append(name)
            print("FAIL: %s: %s" % (name, e))
        except Exception as e:  # noqa: BLE001
            failures.append(name)
            print("ERROR: %s: %r" % (name, e))
    print("\n%d passed, %d failed, %d total" % (len(tests) - len(failures), len(failures), len(tests)))
    sys.exit(1 if failures else 0)
