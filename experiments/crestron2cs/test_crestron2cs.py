#!/usr/bin/env python3
"""Tests for crestron2cs.py (experiment q1b). Run: python3 -m unittest -v
(from this directory)."""
import ast
import json
import os
import re
import sys
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.normpath(os.path.join(_HERE, "..", "..", "tools")))

import crestron2cs as c2c  # noqa: E402
import pkg_dump  # noqa: E402
from wire_table import extract_table  # noqa: E402

PKG_PATH = os.path.normpath(os.path.join(
    _HERE, "..", "..", "samples", "Samsung QNxxLS03DAFXZA", "Crestron", "IP",
    "FlatPanelDisplay_Samsung_QN43LS03DAFXZA_IP.pkg"))

# The two Crestron SDK V2 (Entity Model) 1 Beyond camera drivers -- findings/07
# and findings/08's "IL-only residue" packages. Same engine, one model apart.
I20_PKG_PATH = os.path.normpath(os.path.join(
    _HERE, "..", "..", "samples", "Crestron 1 Beyond IV-CAM-i12_i20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg"))
P20_PKG_PATH = os.path.normpath(os.path.join(
    _HERE, "..", "..", "samples", "Crestron 1 Beyond IV-CAM-p12_p20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg"))


class TestBraceCollapse(unittest.TestCase):
    def test_leaves_a_real_token_untouched(self):
        self.assertEqual(c2c._collapse_doubled_braces("{method}"), "{method}")

    def test_collapses_leading_and_trailing_doubled_braces(self):
        self.assertEqual(c2c._collapse_doubled_braces("{{x}}"), "{x}")

    def test_does_not_eat_a_tokens_own_closing_brace(self):
        # The exact bug found & fixed during development: a naive
        # str.replace("}}", "}") corrupts "...{params}},..." by treating
        # the token's own closing brace + the literal object-closing brace
        # as one doubled pair, destroying the token.
        raw = '{{"a":{"b": 1, {params}},"c":1}}'
        collapsed = c2c._collapse_doubled_braces(raw)
        self.assertEqual(collapsed, '{"a":{"b": 1, {params}},"c":1}')
        # and it must be valid once {params} itself is substituted away with
        # an additional-key splice (exactly how RpcRequest's own {params}
        # token is used by every Set command that inherits it)
        substituted = collapsed.replace("{params}", '"x":1')
        json.loads(substituted)  # must not raise

    def test_real_rpcrequest_content_resolves_to_valid_json_shape(self):
        raw = ('{{"method":"{method}","params":{"AccessToken": "{AccessToken}", '
               '{params}},"id":{_CommandId_},"jsonrpc":"2.0"}}')
        collapsed = c2c._collapse_doubled_braces(raw)
        # fill every slot with a JSON-legal dummy, respecting whether the
        # token sits in a quoted-string position ("{method}") or a bare
        # value position ({_CommandId_}) -- exactly the distinction
        # parse_json_with_slots itself makes.
        filled = (collapsed
                  .replace('"{method}"', '"m"')
                  .replace('"{AccessToken}"', '"tok"')
                  .replace("{params}", '"x": 1')
                  .replace("{_CommandId_}", "1"))
        obj = json.loads(filled)
        self.assertEqual(obj["params"]["x"], 1)
        self.assertEqual(obj["id"], 1)


class TestSlotParsing(unittest.TestCase):
    def test_bare_slot_vs_quoted_slot(self):
        tree = c2c.parse_json_with_slots('{"id":{_CommandId_},"v":"{Volume}","m":"lit"}')
        self.assertEqual(tree["id"], c2c.Slot("_CommandId_", quoted=False))
        self.assertEqual(tree["v"], c2c.Slot("Volume", quoted=True))
        self.assertEqual(tree["m"], "lit")

    def test_rejects_genuinely_malformed_json(self):
        with self.assertRaises(c2c.CrestronTemplateError):
            c2c.parse_json_with_slots("{not json at all")


class TestTemplateIndexOnRealPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        doc = pkg_dump.process_pkg(PKG_PATH)
        cls.dd = doc["driver_definition"]
        cls.idx = c2c.TemplateIndex(cls.dd)

    def test_setvolume_resolves_bottom_up_through_rpcrequest(self):
        text = self.idx.resolve_text("SetVolume")
        obj = c2c.parse_json_with_slots(text)
        self.assertEqual(obj["method"], "directVolumeControl")
        self.assertEqual(obj["params"]["volume"], c2c.Slot("Volume", quoted=True))
        self.assertEqual(obj["params"]["AccessToken"], c2c.Slot("AccessToken", quoted=True))

    def test_setdigitalairantenna_inherits_grandparent_transformations(self):
        # SetDigitalAirAntenna -> SetAntennaTemplate -> RpcRequest. The two
        # Map transforms (antenna name / source) live on SetAntennaTemplate,
        # not on SetDigitalAirAntenna itself.
        transforms = self.idx.chain_transformations("SetDigitalAirAntenna")
        names = {t["Transformation"] for t in transforms}
        self.assertIn("MapInputsToAntennaName", names)
        self.assertIn("MapInputsToSourceName", names)

    def test_lowercase_info_bug_is_reported_not_guessed(self):
        with self.assertRaises(c2c.CrestronTemplateError) as ctx:
            self.idx.resolve_text("SetVideoConfiguration")
        self.assertIn("CommandName", str(ctx.exception))

    def test_every_resolvable_top_level_command_is_valid_json_when_slots_filled(self):
        """Self-consistency oracle: whatever the real (unknown) escaping
        rule inside Crestron's own interpreter is, the text it hands to a
        JSON serializer at runtime obviously has to be valid JSON once
        every slot is filled. This is checked across ALL 76 non-broken
        Commands[] entries, not just the ones examined by hand."""
        checked = 0
        # Pure template BASES (RpcRequest et al) are never resolved
        # standalone in the real generator -- their `{params}`-style slots
        # are only ever valid once a CHILD splices a "key":value fragment
        # in, which is exactly what chain resolution does. Excluded here
        # for the same reason crestron2cs.py itself never emits them as
        # top-level capabilities (see INFRA_EXCLUDE).
        for name, cmd in self.idx.commands_by_name.items():
            if name in c2c.INFRA_EXCLUDE or name == c2c.WAKE_ON_LAN_NAME:
                continue
            if cmd.get("Type") not in ("Text", "Template"):
                continue
            try:
                text = self.idx.resolve_text(name)
            except c2c.CrestronTemplateError:
                continue  # the one documented lowercase-'info' bug
            # quoted-position tokens ("{Name}") -> "x"; bare tokens ({Name}
            # directly in value position, e.g. "id":{_CommandId_}) -> 1
            dummy = re.sub(r'"\{(\w+)\}"', '"x"', text)
            dummy = c2c._TOKEN_RE.sub("1", dummy)
            json.loads(dummy)  # must not raise
            checked += 1
        self.assertGreaterEqual(checked, 70)


class TestFullGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module_src, cls.report = c2c.translate_pkg(PKG_PATH)

    def test_compiles(self):
        ast.parse(self.module_src)

    def test_only_documented_skip(self):
        self.assertEqual(len(self.report["skipped"]), 1)
        self.assertIn("SetVideoConfiguration", self.report["skipped"][0]["reason"])

    def test_wire_table_extracts_every_emitted_capability_with_zero_opaque(self):
        table = extract_table(self.module_src, "generated.py")
        self.assertEqual(len(table.commands), len(self.report["emitted"]))
        self.assertEqual(table.stats["opaque_markers"], 0)

    def test_power_and_volume_match_extron_shipped_script_by_name(self):
        # The two names that happen to coincide between the mechanical
        # Crestron-side translation and Extron's own editorial naming --
        # everything else is compared by protocol content, not name, in
        # compare_semantic.py.
        ext_path = os.path.join(_HERE, "out", "extron_ethernet_source.py")
        if not os.path.exists(ext_path):
            self.skipTest("extron_ethernet_source.py not extracted yet")
        from wire_table import diff_tables
        gen_table = extract_table(self.module_src, "generated.py")
        ext_table = extract_table(open(ext_path).read(), "extron.py")
        d = diff_tables(gen_table, ext_table)
        self.assertIn("Power", d["shared"])
        self.assertIn("Volume", d["shared"])
        # both commands' set request uses the identical method + param keys
        for name in ("Power", "Volume"):
            self.assertNotIn("parameters", d["differences"].get(name, {}))


class TestUndeclaredTransformations(unittest.TestCase):
    """Package-level diagnostic (ROADMAP R31): every Transformation name a
    driver references anywhere minus what it declares in Transformations[]
    -- the IL-only residue findings/07 and findings/08 describe for
    Crestron V2 Entity Model drivers. Checked against both findings'
    packages plus the one JSON LegacyWrappers package the translator has
    actually run on (Samsung), to confirm the scan finds nothing there."""

    def test_samsung_json_legacywrappers_has_zero_undeclared(self):
        # Regression check: a fully-declarative JSON-engine driver (no
        # compiled IL residue at all) must report nothing undeclared.
        doc = pkg_dump.process_pkg(PKG_PATH)
        idx = c2c.TemplateIndex(doc["driver_definition"])
        report = idx.undeclared_transformations()
        self.assertEqual(report.undeclared, [])
        self.assertEqual(report.referenced, sorted(report.referenced))
        self.assertGreater(len(report.referenced), 0)

    def test_p20_matches_finding_08_exactly(self):
        # findings/08: "Its Rules reference 39 distinct Transformation
        # names; 27 are declared... Of the 12 undeclared, only 5 have
        # driver-local IL -- FormatRomVersion, ParseDecimal,
        # ZoomLevelToPosition, ZoomPositionToLevel, ApplyZoomPositionStep
        # -- plus OverridePolynomial... The remaining undeclared names are
        # supplied by the SDK framework itself."
        # (OverridePolynomial is an override hook "never called by literal
        # name" -- findings/08 found it via IL disassembly, not JSON text,
        # so it cannot appear in a referenced-name scan and is correctly
        # absent from this package-level pass's output.)
        if not os.path.exists(P20_PKG_PATH):
            self.skipTest("P20 sample package not present")
        doc = pkg_dump.process_pkg(P20_PKG_PATH)
        idx = c2c.TemplateIndex(doc["driver_definition"])
        report = idx.undeclared_transformations()
        self.assertEqual(len(report.referenced), 39)
        self.assertEqual(len(report.declared), 27)
        self.assertEqual(len(report.undeclared), 12)
        self.assertEqual(report.undeclared, [
            "ApplyZoomPositionStep", "Divide", "FormatRomVersion", "Identity",
            "ParseDecimal", "Product", "Subtract", "Sum",
            "ViscaAssemble4LowerNibbles", "ViscaExtractNibbles",
            "ZoomLevelToPosition", "ZoomPositionToLevel",
        ])
        # findings/08's "5 driver-local + OverridePolynomial" family, minus
        # OverridePolynomial (IL-only, never named in the JSON -- see above):
        driver_local = {
            "FormatRomVersion", "ParseDecimal", "ZoomLevelToPosition",
            "ZoomPositionToLevel", "ApplyZoomPositionStep",
        }
        self.assertTrue(driver_local.issubset(set(report.undeclared)))

    def test_i20_does_not_match_findings_07s_six_undercount(self):
        # findings/07 lists exactly six names it says "the JSON's own
        # Rules invoke" with no declarative definition: FormatRomVersion,
        # ParseDecimal, ViscaAssemble2LowerNibbles, ZoomLevelToPosition,
        # ZoomPositionToLevel, ApplyZoomPositionStep. That is finding/07's
        # phase-1 pass; it turns out to be an UNDERCOUNT (see the module
        # docstring on TemplateIndex.undeclared_transformations and the
        # summary this test file's docstring points to): it only surveyed
        # the driver-local-IL family, and missed the SDK-framework-supplied
        # names (Identity/Sum/Subtract/Product/Divide) and the OTHER Visca
        # nibble-transform names that findings/08's own P20 methodology --
        # applied identically here -- also finds referenced in I20's own
        # Responses[] decoders. Applying findings/08's exact method (whole
        # document, not just Rules[]) to I20 reproduces the SAME total
        # referenced-name count as P20 (39, same shared engine) and gives
        # 13 undeclared, not 6 -- one more than P20's 12, because I20's
        # JSON additionally names ViscaAssemble2LowerNibbles (I20's own
        # nibble-assembly variant) alongside the ViscaAssemble4LowerNibbles/
        # ViscaExtractNibbles pair P20 also references.
        if not os.path.exists(I20_PKG_PATH):
            self.skipTest("I20 sample package not present")
        doc = pkg_dump.process_pkg(I20_PKG_PATH)
        idx = c2c.TemplateIndex(doc["driver_definition"])
        report = idx.undeclared_transformations()
        self.assertEqual(len(report.referenced), 39)
        self.assertEqual(len(report.declared), 26)
        self.assertEqual(len(report.undeclared), 13)
        self.assertNotEqual(len(report.undeclared), 6)
        expected = {
            "ApplyZoomPositionStep", "Divide", "FormatRomVersion", "Identity",
            "ParseDecimal", "Product", "Subtract", "Sum",
            "ViscaAssemble2LowerNibbles", "ViscaAssemble4LowerNibbles",
            "ViscaExtractNibbles", "ZoomLevelToPosition", "ZoomPositionToLevel",
        }
        self.assertEqual(set(report.undeclared), expected)
        # findings/07's own six ARE all present (it wasn't wrong about
        # those six -- it just didn't find the rest):
        findings_07_six = {
            "FormatRomVersion", "ParseDecimal", "ViscaAssemble2LowerNibbles",
            "ZoomLevelToPosition", "ZoomPositionToLevel", "ApplyZoomPositionStep",
        }
        self.assertTrue(findings_07_six.issubset(expected))

    def test_find_undeclared_transformations_entry_point(self):
        # The module-level convenience wrapper (loads the .pkg itself, for
        # the --list-il-only CLI path) agrees with the TemplateIndex method.
        report = c2c.find_undeclared_transformations(PKG_PATH)
        self.assertEqual(report.undeclared, [])

    def test_never_raises_on_undeclared_names(self):
        # This is a diagnostic pass, not a translation step: an undeclared
        # Transformation is exactly the thing it reports, never something
        # it raises CrestronTemplateError over (unlike resolve_slot, which
        # DOES raise when translating a command that needs one).
        if not os.path.exists(I20_PKG_PATH):
            self.skipTest("I20 sample package not present")
        try:
            c2c.find_undeclared_transformations(I20_PKG_PATH)
        except c2c.CrestronTemplateError:
            self.fail("undeclared_transformations() must not raise for a "
                      "driver that merely has undeclared names")


if __name__ == "__main__":
    unittest.main()
