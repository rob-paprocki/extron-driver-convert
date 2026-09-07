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


if __name__ == "__main__":
    unittest.main()
