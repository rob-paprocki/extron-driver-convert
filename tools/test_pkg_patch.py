#!/usr/bin/env python3
"""
test_pkg_patch.py - tests for pkg_patch.py, the strategy-A Crestron .pkg
resource patcher.

No pytest is installed in this environment: plain test_* functions,
asserts only, collected and run by the __main__ block, matching
test_pkg_dump.py's style.

Every edit-shape test re-parses its result with pkg_dump's real ECMA-335
metadata walk (never by re-checking the bytes this module itself wrote) so
that patch bugs pkg_dump would independently catch actually get caught.

Run: python3 tools/test_pkg_patch.py
"""
import json
import os
import struct
import sys
import tempfile
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkg_dump as pd    # noqa: E402
import pkg_patch as pp   # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAMSUNG_SERIAL = os.path.join(
    REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "Crestron", "Serial",
    "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_Serial.pkg")

# The one literal field every variant test mutates: a plain ASCII string
# value ("LS Series") with no quotes/backslashes, so replacing it with
# another same-shape ASCII string of a chosen length keeps the JSON valid
# without needing to reproduce the original file's exact json.dumps style.
NEEDLE = b'"Description": "LS Series"'


def _require_sample():
    assert os.path.isfile(SAMSUNG_SERIAL), "missing sample file: %r" % SAMSUNG_SERIAL


def _read_dll(pkg_path):
    with zipfile.ZipFile(pkg_path) as z:
        names = [n for n in z.namelist() if n.lower().endswith(".dll")]
        assert len(names) == 1
        return z.read(names[0])


def _variant_raw(original_raw_bytes, new_description_value):
    """original_raw_bytes includes the BOM and the exact original byte
    layout; returns a new raw payload (same BOM-ness) with only the
    Description field's value swapped in, so length changes are exactly
    controlled and everything else -- including formatting -- is
    untouched."""
    assert original_raw_bytes.count(NEEDLE) == 1
    new_field = ('"Description": "%s"' % new_description_value).encode("utf-8")
    return original_raw_bytes.replace(NEEDLE, new_field)


# --------------------------------------------------------------------------
# Fixtures (module-level, computed once)
# --------------------------------------------------------------------------

def _dll_and_raw():
    _require_sample()
    dll = _read_dll(SAMSUNG_SERIAL)
    result = pd.extract_driver_definition(dll)
    assert result.method == "cli-metadata"
    return dll, result.raw_bytes


# --------------------------------------------------------------------------
# Edit shapes, each verified by re-parsing with pkg_dump
# --------------------------------------------------------------------------

def test_identity_roundtrip_is_byte_identical():
    dll, raw = _dll_and_raw()
    patched, result = pp.patch_resource_bytes(dll, raw, bom=None)
    assert result.method == "same-size"
    assert result.growth == 0
    assert patched == dll, "patching with the DLL's own current JSON must be a no-op"

    doc = pd.extract_driver_definition(patched)
    assert doc.definition == pd.extract_driver_definition(dll).definition


def test_same_length_edit():
    dll, raw = _dll_and_raw()
    variant = _variant_raw(raw, "LS Seriez")  # 9 chars, same as "LS Series"
    assert len(variant) == len(raw)

    patched, result = pp.patch_resource_bytes(dll, variant, bom=None)
    assert result.method == "same-size"
    assert result.growth == 0
    assert len(patched) == len(dll)

    doc = pd.extract_driver_definition(patched)
    assert doc.definition["GeneralInformation"]["Description"] == "LS Seriez"
    # everything else in the definition is untouched
    orig_doc = pd.extract_driver_definition(dll).definition
    orig_doc["GeneralInformation"]["Description"] = "LS Seriez"
    assert doc.definition == orig_doc

    # full PE re-parse succeeds and COR20 header is internally consistent
    pe = pd.PEImage(patched)
    cor20 = pe.cor20_header()
    assert cor20["resources_size"] == len(variant) + 4


def test_shorter_edit():
    dll, raw = _dll_and_raw()
    variant = _variant_raw(raw, "LS")
    assert len(variant) < len(raw)
    shrink_amount = len(raw) - len(variant)

    patched, result = pp.patch_resource_bytes(dll, variant, bom=None)
    assert result.method == "shrink"
    assert result.growth == -shrink_amount
    assert len(patched) == len(dll), "shrink must pad in place, not shorten the file"

    doc = pd.extract_driver_definition(patched)
    assert doc.definition["GeneralInformation"]["Description"] == "LS"

    pe = pd.PEImage(patched)
    cor20 = pe.cor20_header()
    assert cor20["resources_size"] == len(variant) + 4
    # nothing after the resource moved: metadata RVA is untouched
    orig_cor20 = pd.PEImage(dll).cor20_header()
    assert cor20["metadata_rva"] == orig_cor20["metadata_rva"]


def test_growing_edit_within_slack():
    dll, raw = _dll_and_raw()
    long_value = "LS Series " + ("X" * 500)
    variant = _variant_raw(raw, long_value)
    growth = len(variant) - len(raw)
    assert growth > 0

    patched, result = pp.patch_resource_bytes(dll, variant, bom=None)
    assert result.method == "growth"
    assert result.growth == growth
    assert result.slack is not None and result.slack >= growth
    assert len(patched) == len(dll), "in-slack growth must not change the file length"

    # The actual relocation shift is `growth` rounded up to a 4-byte boundary
    # (see pkg_patch's growth-path comment): the CLI metadata root must stay
    # 4-byte aligned relative to its own start, which pkg_dump's stream-name
    # padding depends on. That shift, not the raw JSON growth, is what every
    # relocated RVA below actually moved by.
    shift = growth + ((-growth) % 4)
    assert shift % 4 == 0 and 0 <= shift - growth < 4

    # 1. pkg_dump's own walk finds the grown resource and the right JSON
    doc = pd.extract_driver_definition(patched)
    assert doc.method == "cli-metadata"
    assert doc.definition["GeneralInformation"]["Description"] == long_value

    # 2. the CLI metadata root itself still parses (BSJB signature etc.)
    pe = pd.PEImage(patched)
    cor20 = pe.cor20_header()
    orig_cor20 = pd.PEImage(dll).cor20_header()
    assert cor20["metadata_rva"] == orig_cor20["metadata_rva"] + shift
    assert cor20["resources_size"] == len(variant) + 4
    streams = pe.metadata_root(cor20["metadata_rva"], cor20["metadata_size"])
    assert "#~" in streams and "#Strings" in streams

    # 3. the Import Directory this module had to relocate still decodes:
    #    walk it completely independently of pkg_patch's own internals,
    #    using only the (now-shifted) data directory entry.
    imp_rva, imp_size, _ = pp.data_directory(pe, pp.IMAGE_DIRECTORY_ENTRY_IMPORT)
    orig_imp_rva, _, _ = pp.data_directory(pd.PEImage(dll), pp.IMAGE_DIRECTORY_ENTRY_IMPORT)
    assert imp_rva == orig_imp_rva + shift
    imp_off = pe.rva_to_offset(imp_rva)
    oft, _tds, _fc, name_rva, fit = struct.unpack_from("<IIIII", patched, imp_off)
    name_off = pe.rva_to_offset(name_rva)
    dll_name = patched[name_off:patched.index(b"\x00", name_off)].decode("ascii")
    assert dll_name == "mscoree.dll"

    ilt_off = pe.rva_to_offset(oft)
    hint_name_rva = struct.unpack_from("<I", patched, ilt_off)[0]
    hn_off = pe.rva_to_offset(hint_name_rva)
    func_name = patched[hn_off + 2:patched.index(b"\x00", hn_off + 2)].decode("ascii")
    assert func_name == "_CorDllMain"

    # 4. the IAT entry (outside the moved block) was updated to match
    iat_off = pe.rva_to_offset(fit)
    iat_entry = struct.unpack_from("<I", patched, iat_off)[0]
    assert iat_entry == hint_name_rva


def test_growth_beyond_slack_is_refused_not_guessed():
    dll, raw = _dll_and_raw()
    huge_value = "LS Series " + ("X" * 5000)
    variant = _variant_raw(raw, huge_value)
    try:
        pp.patch_resource_bytes(dll, variant, bom=None)
        assert False, "expected PatchNotSupportedError for growth past the section's slack"
    except pp.PatchNotSupportedError as e:
        assert "slack" in str(e)


# --------------------------------------------------------------------------
# Authenticode: detect + report, never re-sign
# --------------------------------------------------------------------------

def test_signature_is_detected_and_reported():
    dll, raw = _dll_and_raw()
    pe = pd.PEImage(dll)
    sig = pp.signature_info(pe)
    assert sig["present"] is True
    assert sig["size"] > 0
    assert sig["ends_at_eof"] is True

    _patched, result = pp.patch_resource_bytes(dll, raw, bom=None)
    assert result.signature["present"] is True
    assert any("Authenticode" in n and "does NOT re-sign" in n for n in result.notes)


def test_strip_signature_removes_it_without_resigning():
    dll, raw = _dll_and_raw()
    stripped, note = pp._strip_authenticode(dll)  # noqa: SLF001 (module-internal, tested directly)
    assert "stripped" in note
    assert len(stripped) < len(dll)

    pe = pd.PEImage(stripped)
    sig = pp.signature_info(pe)
    assert sig["present"] is False

    # stripping alone must not touch the resource: the JSON still round-trips
    doc = pd.extract_driver_definition(stripped)
    assert doc.definition == pd.extract_driver_definition(dll).definition


def test_strip_signature_on_already_unsigned_is_a_noop():
    dll, _raw = _dll_and_raw()
    once, _ = pp._strip_authenticode(dll)  # noqa: SLF001
    twice, note = pp._strip_authenticode(once)  # noqa: SLF001
    assert twice == once
    assert "nothing to strip" in note


# --------------------------------------------------------------------------
# .pkg (ZIP) level: other members untouched, whole file re-parses
# --------------------------------------------------------------------------

def test_patch_pkg_preserves_other_members_and_reparses():
    _require_sample()
    dll = _read_dll(SAMSUNG_SERIAL)
    raw = pd.extract_driver_definition(dll).raw_bytes

    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "patched.pkg")
        result = pp.patch_pkg(SAMSUNG_SERIAL, raw, out_path)
        assert result.method == "same-size"

        with zipfile.ZipFile(SAMSUNG_SERIAL) as zin, zipfile.ZipFile(out_path) as zout:
            assert zin.namelist() == zout.namelist()
            for name in zin.namelist():
                assert zin.read(name) == zout.read(name), \
                    "member %r changed by an identity patch_pkg" % name

        # the whole output re-parses cleanly through pkg_dump's own entry point
        doc = pd.process_pkg(out_path)
        orig_doc = pd.process_pkg(SAMSUNG_SERIAL)
        assert doc["driver_definition"] == orig_doc["driver_definition"]
        assert doc["resource"]["method"] == "cli-metadata"


def test_patch_pkg_growing_edit_end_to_end_via_json_dict():
    """The --json-file path: a plain dict, not exact original bytes. Confirms
    growth works through the full patch_pkg/zip path too, and that pkg_dump
    reads back the (reformatted, but semantically identical plus one field
    changed) definition correctly."""
    _require_sample()
    orig_doc = pd.process_pkg(SAMSUNG_SERIAL)
    new_definition = json.loads(json.dumps(orig_doc["driver_definition"]))
    new_definition["GeneralInformation"]["Description"] = "LS Series " + ("Y" * 400)

    with tempfile.TemporaryDirectory() as td:
        out_path = os.path.join(td, "grown.pkg")
        result = pp.patch_pkg(SAMSUNG_SERIAL, new_definition, out_path)
        assert result.method in ("growth", "shrink", "same-size")  # reformatting can shrink too

        doc = pd.process_pkg(out_path)
        assert doc["driver_definition"]["GeneralInformation"]["Description"] == \
            new_definition["GeneralInformation"]["Description"]


# --------------------------------------------------------------------------
# Failing loudly
# --------------------------------------------------------------------------

def test_locate_resource_raises_on_non_pe_bytes():
    junk = b"not a PE file at all"
    try:
        pp.locate_single_embedded_resource(junk)
        assert False, "expected a PE/metadata parse error on non-PE bytes"
    except (pd.PEFormatError, pd.MetadataParseError):
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
