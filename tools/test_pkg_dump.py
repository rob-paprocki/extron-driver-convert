#!/usr/bin/env python3
"""
test_pkg_dump.py - tests for pkg_dump.py, the Crestron .pkg extractor.

No pytest is installed in this environment, so these are plain test_*
functions collected and run by the __main__ block at the bottom (asserts
only, no fixtures). The same functions are pytest-collectible if pytest
ever is available (pytest looks for test_* functions in test_*.py files).

Run: python3 tools/test_pkg_dump.py
"""
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkg_dump  # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAMSUNG_DIR = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "Crestron")
SAMSUNG_SERIAL = os.path.join(SAMSUNG_DIR, "Serial", "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_Serial.pkg")
SAMSUNG_IP = os.path.join(SAMSUNG_DIR, "IP", "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg")
SAMSUNG_IR = os.path.join(SAMSUNG_DIR, "IR", "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IR.pkg")

BEYOND_I20 = os.path.join(
    REPO_ROOT, "samples", "Crestron 1 Beyond IV-CAM-i12_i20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg",
)
BEYOND_P20 = os.path.join(
    REPO_ROOT, "samples", "Crestron 1 Beyond IV-CAM-p12_p20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg",
)

ALL_PKGS = [SAMSUNG_SERIAL, SAMSUNG_IP, SAMSUNG_IR, BEYOND_I20, BEYOND_P20]


def _require_samples():
    missing = [p for p in ALL_PKGS if not os.path.isfile(p)]
    assert not missing, "missing sample .pkg files: %r" % missing


# --------------------------------------------------------------------------
# PE / CLI metadata primitives
# --------------------------------------------------------------------------

def test_pe_parse_finds_cli_header_samsung_serial():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_SERIAL, ".dll")
    pe = pkg_dump.PEImage(dll_bytes)
    cor20 = pe.cor20_header()
    assert cor20["resources_rva"] != 0
    assert cor20["resources_size"] == 46168  # 4-byte length prefix + 46164 payload


def test_pe_rva_to_offset_roundtrips_through_sections():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_SERIAL, ".dll")
    pe = pkg_dump.PEImage(dll_bytes)
    for section in pe.sections:
        off = pe.rva_to_offset(section["virtual_address"])
        assert off == section["pointer_to_raw_data"]


def test_pe_rejects_non_pe_bytes():
    try:
        pkg_dump.PEImage(b"not a PE file at all")
        assert False, "expected PEImage to raise on garbage input"
    except pkg_dump.PEFormatError:
        pass


# --------------------------------------------------------------------------
# ManifestResource extraction, byte-exact regression assertions
# --------------------------------------------------------------------------

def _read_member(pkg_path, suffix):
    with zipfile.ZipFile(pkg_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(suffix)]
        assert len(names) == 1, "expected exactly one %s member in %s, got %r" % (suffix, pkg_path, names)
        return z.read(names[0])


def test_samsung_serial_resource_is_exactly_46164_bytes():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_SERIAL, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    assert result.method == "cli-metadata", result.notes
    assert len(result.raw_bytes) == 46164, len(result.raw_bytes)


def test_samsung_ip_resource_is_exactly_80889_bytes():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_IP, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    assert result.method == "cli-metadata", result.notes
    assert len(result.raw_bytes) == 80889, len(result.raw_bytes)


def test_samsung_serial_resource_has_bom_and_valid_json():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_SERIAL, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    assert result.raw_bytes[:3] == b"\xef\xbb\xbf"
    assert isinstance(result.definition, dict)
    assert "SchemaVersion" in result.definition


def test_samsung_ip_driver_definition_sections_present():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_IP, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    d = result.definition
    for key in ("SchemaVersion", "GeneralInformation", "Transports", "Commands",
                "Responses", "Conditions", "Transformations", "Rules", "Controllers"):
        assert key in d, "missing section %r in %r" % (key, sorted(d.keys()))


def test_beyond_i20_resource_extracted_via_metadata_not_fallback():
    _require_samples()
    dll_bytes = _read_member(BEYOND_I20, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    assert result.method == "cli-metadata", result.notes
    assert result.raw_bytes[:1] == b"{"  # no BOM in this one
    assert result.definition["SchemaVersion"]


def test_beyond_p20_resource_extracted_via_metadata_not_fallback():
    _require_samples()
    dll_bytes = _read_member(BEYOND_P20, ".dll")
    result = pkg_dump.extract_driver_definition(dll_bytes)
    assert result.method == "cli-metadata", result.notes
    assert result.raw_bytes[:1] == b"{"
    assert result.definition["SchemaVersion"]


def test_beyond_i20_schema_marker_offset_matches_known_value():
    # Established by direct inspection: '"SchemaVersion"' literal string is at
    # file offset 22981 in this DLL. Our resource payload must start exactly
    # one byte before that (the opening brace).
    _require_samples()
    dll_bytes = _read_member(BEYOND_I20, ".dll")
    marker = dll_bytes.find(b'"SchemaVersion"')
    assert marker == 22981
    result = pkg_dump.extract_driver_definition(dll_bytes)
    start = dll_bytes.find(result.raw_bytes)
    assert start != -1
    assert start + 1 == marker


# --------------------------------------------------------------------------
# Fallback brace-matched scan
# --------------------------------------------------------------------------

def test_fallback_scan_used_when_metadata_parse_fails():
    _require_samples()
    dll_bytes = _read_member(SAMSUNG_SERIAL, ".dll")
    # Corrupt the CLI header's COM data-directory RVA so metadata parsing breaks,
    # forcing the brace-matched fallback.
    pe = pkg_dump.PEImage(dll_bytes)
    corrupted = bytearray(dll_bytes)
    dd_off = pe.com_descriptor_directory_offset()
    corrupted[dd_off:dd_off + 4] = (0xFFFFFFF0).to_bytes(4, "little")
    result = pkg_dump.extract_driver_definition(bytes(corrupted))
    assert result.method == "brace-scan"
    assert any("fallback" in n.lower() or "brace" in n.lower() for n in result.notes), result.notes
    assert result.definition["SchemaVersion"]


def test_fallback_scan_finds_schema_version_directly():
    data = b'noise noise {"SchemaVersion": "1.0", "Nested": {"a": 1}} trailing junk'
    found = pkg_dump.brace_match_scan(data, b'"SchemaVersion"')
    assert found == b'{"SchemaVersion": "1.0", "Nested": {"a": 1}}'
    json.loads(found)  # must be valid JSON


def test_brace_match_scan_handles_braces_inside_strings():
    data = b'{"SchemaVersion": "1.0", "weird": "a{b}c", "n": {"x": 1}}'
    found = pkg_dump.brace_match_scan(data, b'"SchemaVersion"')
    parsed = json.loads(found)
    assert parsed["weird"] == "a{b}c"
    assert parsed["n"]["x"] == 1


# --------------------------------------------------------------------------
# Whole-package processing
# --------------------------------------------------------------------------

def test_process_pkg_samsung_serial_end_to_end():
    _require_samples()
    doc = pkg_dump.process_pkg(SAMSUNG_SERIAL)
    assert doc["package"] == os.path.basename(SAMSUNG_SERIAL)
    assert doc["manifest"]["driverId"]
    assert doc["driver_definition"] is not None
    assert doc["driver_definition"]["SchemaVersion"]
    assert doc["resource"]["size"] == 46164
    names = {m["name"] for m in doc["members"]}
    assert any(n.endswith(".dat") for n in names)
    assert any(n.endswith(".dll") for n in names)


def test_process_pkg_ir_has_no_dll_and_notes_it():
    _require_samples()
    doc = pkg_dump.process_pkg(SAMSUNG_IR)
    assert doc["driver_definition"] is None
    assert doc["manifest"] is not None
    ir_members = [m["name"] for m in doc["members"] if m["name"].lower().endswith(".ir")]
    assert len(ir_members) == 1
    assert any(".ir" in n for n in doc["notes"])
    assert any("no dll" in n.lower() or "no .dll" in n.lower() for n in doc["notes"])


def test_process_pkg_beyond_i20_end_to_end():
    _require_samples()
    doc = pkg_dump.process_pkg(BEYOND_I20)
    assert doc["driver_definition"]["SchemaVersion"]
    assert doc["resource"]["size"] == 116874
    assert doc["resource"]["method"] == "cli-metadata"


def test_process_pkg_beyond_p20_end_to_end():
    _require_samples()
    doc = pkg_dump.process_pkg(BEYOND_P20)
    assert doc["driver_definition"]["SchemaVersion"]
    assert doc["resource"]["size"] == 109648
    assert doc["resource"]["method"] == "cli-metadata"


def test_process_directory_of_pkgs():
    _require_samples()
    docs = pkg_dump.process_path(SAMSUNG_DIR)
    assert len(docs) == 3
    packages = {d["package"] for d in docs}
    assert packages == {
        "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_Serial.pkg",
        "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg",
        "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IR.pkg",
    }


def test_summary_line_format():
    _require_samples()
    doc = pkg_dump.process_pkg(SAMSUNG_SERIAL)
    line = pkg_dump.summary_line(doc)
    assert doc["package"] in line
    assert "members=" in line
    assert "resource_size=46164" in line
    assert "driver_sections=" in line


def test_summary_line_for_ir_package_has_no_resource_size():
    _require_samples()
    doc = pkg_dump.process_pkg(SAMSUNG_IR)
    line = pkg_dump.summary_line(doc)
    assert doc["package"] in line
    assert "no-dll" in line or "resource_size=0" in line


# --------------------------------------------------------------------------
# Failing loudly
# --------------------------------------------------------------------------

def test_process_pkg_raises_on_missing_dat():
    import io
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        bad_path = os.path.join(td, "bad.pkg")
        with zipfile.ZipFile(bad_path, "w") as z:
            z.writestr("bad.dll", b"not really a dll")
        try:
            pkg_dump.process_pkg(bad_path)
            assert False, "expected process_pkg to fail loudly on a .pkg with no .dat"
        except pkg_dump.PkgFormatError:
            pass


def test_process_pkg_raises_on_multiple_dlls():
    import tempfile

    with tempfile.TemporaryDirectory() as td:
        bad_path = os.path.join(td, "bad2.pkg")
        with zipfile.ZipFile(bad_path, "w") as z:
            z.writestr("bad2.dat", json.dumps({"driverID": "x"}))
            z.writestr("bad2.dll", b"one")
            z.writestr("extra.dll", b"two")
        try:
            pkg_dump.process_pkg(bad_path)
            assert False, "expected process_pkg to fail loudly on a .pkg with two .dll members"
        except pkg_dump.PkgFormatError:
            pass


def test_extract_driver_definition_raises_when_all_methods_fail():
    junk = b"MZ" + b"\x00" * 500  # looks vaguely PE-ish but has no valid headers
    try:
        pkg_dump.extract_driver_definition(junk)
        assert False, "expected extract_driver_definition to raise when nothing works"
    except pkg_dump.DriverExtractionError:
        pass


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
