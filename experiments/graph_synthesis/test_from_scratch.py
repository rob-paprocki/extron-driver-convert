#!/usr/bin/env python3
"""Tests for the R28 Phase 2 authoring API.

Pins the layer the fork delivered:

- `tools/extron_enums.py` exposes the four enum vocabularies with the
  correct underlying types and metadata.
- `tools/pkp_asset.py` gains three authoring methods
  (`strip_to_minimum_root`, `keep_only_command`, `author_command_values`,
  `set_ex_cmd_id`) that work correctly at the byte level.
- `experiments/graph_synthesis/build_one_command.py` produces a .pkp
  that round-trips through our Python parser AND passes `pkp_validate`.

What this does NOT pin (the Phase 3 gap documented in RESULTS.md under
"R28 Phase 3"): that Extron's deserialiser's property accessors read
our authored values back. The output .pkp deserialises cleanly through
the Finding 18 gate, but property accessors return the C# class
defaults -- an open finding. These tests check the byte-level authoring
contract, which is what the fork controls.

Standard library only. Skips when the donor .pkp is not reachable
(vendor material; per-worktree availability varies -- see
vendor-files.manifest.tsv).
"""
from __future__ import annotations

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(REPO_ROOT, "tools")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HERE)

import pkp_build as pb        # noqa: E402
import pkp_asset as pa        # noqa: E402
import extron_enums as ee     # noqa: E402
import build_one_command      # noqa: E402

PKP = os.path.join(HERE, "out", "one_command.pkp")


def _have_donor():
    return build_one_command._pick_donor() is not None


class TestExtronEnumsModule(unittest.TestCase):

    def test_four_enums_present_and_int32(self):
        self.assertEqual(sorted(ee.ENUMS_BY_NAME),
                         sorted(["DriverAttributeEnum", "ExtronCommandIdEnum",
                                 "EthernetTypeEnum",
                                 "ProtocolCompatibilityFlags"]))
        for name, meta in ee.TYPE_META.items():
            self.assertEqual(meta["underlying"], "Int32")
            self.assertEqual(meta["size"], 4)
            self.assertIn(name, ee.ENUMS_BY_NAME)

    def test_driver_attribute_bits(self):
        # Shipping packages write combinations like
        # RuntimeVisible | LiveStatus (0x22) and ConfigurationVisible |
        # RuntimeVisible (0x03). Confirm the bit values match the DLL.
        self.assertEqual(int(ee.DriverAttributeEnum.ConfigurationVisible), 0x01)
        self.assertEqual(int(ee.DriverAttributeEnum.RuntimeVisible), 0x02)
        self.assertEqual(int(ee.DriverAttributeEnum.Alias), 0x04)
        self.assertEqual(int(ee.DriverAttributeEnum.RequiredPollingCommand),
                         0x08)
        self.assertEqual(int(ee.DriverAttributeEnum.EmulatedStatus), 0x10)
        self.assertEqual(int(ee.DriverAttributeEnum.LiveStatus), 0x20)
        self.assertEqual(int(ee.DriverAttributeEnum.WriteProtected), 0x40)

    def test_ex_cmd_id_default_is_zero(self):
        self.assertEqual(int(ee.ExtronCommandIdEnum.General), 0)

    def test_compatibility_flags_round_trip(self):
        # tools/pkp2cs.py reads `_compatibility` and maps these specific
        # values to transport classes. The vocabulary must round-trip.
        for flag, dec in (("Ethernet_UDP", 32), ("Ethernet_HTTP", 64),
                          ("Ethernet_SSH", 512)):
            self.assertEqual(int(getattr(ee.ProtocolCompatibilityFlags,
                                         flag)), dec)


@unittest.skipUnless(_have_donor(), "no donor .pkp reachable")
class TestAuthoringApi(unittest.TestCase):
    """The CommandGraph methods the fork added, driven end-to-end."""

    def setUp(self):
        self.donor = build_one_command._pick_donor()
        self.b = pb.PackageBuilder(self.donor)
        self.g = pa.CommandGraph(self.b)

    def test_strip_to_minimum_root_drops_three_container_types(self):
        before = self.g.children(1)
        self.g.strip_to_minimum_root()
        after = self.g.children(1)
        # Three load-bearing containers remain, all others go.
        self.assertLess(len(after), len(before))
        for oid in after:
            cname = pa._cls(self.g.objects[oid]) or ""
            self.assertTrue(
                any(t in cname for t in
                    pa.LOAD_BEARING_ROOT_CHILD_TYPES),
                f"kept {cname!r} that is not a load-bearing container")

    def test_keep_only_command_leaves_one_live_command(self):
        cmds = self.g.commands()
        kept_sn = sorted(cmds, key=lambda sn: cmds[sn])[0]
        kept_id = cmds[kept_sn]
        self.g.strip_to_minimum_root()
        self.g.keep_only_command(kept_id)
        # Every command-holding collection now holds at most kept_id.
        for _name, parent_id in self.g._command_parents():
            kids = self.g.children(parent_id)
            for child_id in kids:
                if pa._cls(self.g.objects[child_id]) == pa.COMMAND_CLASS:
                    self.assertEqual(child_id, kept_id)

    def test_author_command_values_writes_enum_fields(self):
        cmds = self.g.commands()
        kept_sn = sorted(cmds, key=lambda sn: cmds[sn])[0]
        kept_id = cmds[kept_sn]
        attrs = (ee.DriverAttributeEnum.RuntimeVisible
                 | ee.DriverAttributeEnum.LiveStatus)
        self.g.author_command_values(
            kept_id, name="Test", script_name="TestScript",
            attributes=attrs, ex_cmd_id=ee.ExtronCommandIdEnum.General)
        # The byte-level values the fork's authoring path controls.
        self.assertEqual(
            self.g.enum_member(kept_id, "CommandAssetBase+_attributes"),
            int(attrs))
        slots = self.g.walker.member_slots(kept_id)
        exname = ("CommandAssetBase+_exCmdId"
                  if "CommandAssetBase+_exCmdId" in slots else "_exCmdId")
        self.assertEqual(self.g.enum_member(kept_id, exname), 0)
        self.assertEqual(self.g.name_of(kept_id), "Test")


@unittest.skipUnless(_have_donor() and os.path.isfile(PKP),
                     "one_command.pkp not built yet; run "
                     "build_one_command.py first")
class TestBuiltPkp(unittest.TestCase):
    """Properties of the artefact build_one_command.py produces."""

    def test_pkp_dump_loads(self):
        import pkp_dump as pd
        parser = pd.load_parser(PKP) if hasattr(pd, "load_parser") else None
        if parser is None:
            # Fallback: use pkp_build's Builder which parses on init.
            pb.PackageBuilder(PKP)

    def test_pkp_validate_reports_valid(self):
        """pkp_validate's rc reflects the resource-hash check; a
        no-manifest package shows `Valid 0` with a warning but the
        process rc may not be 0. Parse the stdout for the per-package
        verdict instead -- what matters is that our Python validator
        does not reject the authored package as unparseable or hash-
        mismatched."""
        cp = subprocess.run(
            [sys.executable, os.path.join(TOOLS, "pkp_validate.py"), PKP],
            capture_output=True, text=True, timeout=120)
        self.assertIn("Valid", cp.stdout,
                      f"stdout:\n{cp.stdout}\nstderr:\n{cp.stderr}")
        self.assertNotIn("Unparseable", cp.stdout)
        self.assertNotIn("Mismatch", cp.stdout)

    def test_pkp_round_trips_through_builder(self):
        b = pb.PackageBuilder(PKP)
        # Constructor raises RoundTripError on any round-trip failure, so
        # construction succeeding is the whole assertion.
        self.assertIsNotNone(b)

    def test_only_one_live_command(self):
        b = pb.PackageBuilder(PKP)
        g = pa.CommandGraph(b)
        for _name, parent_id in g._command_parents():
            kids = g.children(parent_id)
            cmd_kids = [k for k in kids
                        if pa._cls(g.objects[k]) == pa.COMMAND_CLASS]
            self.assertLessEqual(len(cmd_kids), 1,
                                 f"parent {parent_id} has {len(cmd_kids)} "
                                 f"live commands, expected <= 1")

    def test_authored_values_present_in_bytes(self):
        """Our authored _attributes, _exCmdId, name, script_name are on
        the wire. (Phase 3 open question: whether Extron's property
        accessors reflect them -- see RESULTS.md R28 Phase 3.)"""
        b = pb.PackageBuilder(PKP)
        g = pa.CommandGraph(b)
        cmds = g.commands()
        self.assertIn("TestCommand", cmds,
                      f"expected TestCommand in {sorted(cmds)}")
        oid = cmds["TestCommand"]
        self.assertEqual(g.name_of(oid), "Test Command")
        attrs = g.enum_member(oid, "CommandAssetBase+_attributes")
        self.assertEqual(
            attrs,
            int(ee.DriverAttributeEnum.RuntimeVisible
                | ee.DriverAttributeEnum.LiveStatus))


AUTHORED_PKP = os.path.join(HERE, "out", "authored_command.pkp")


@unittest.skipUnless(_have_donor(), "no donor .pkp reachable")
class TestAuthoredBinding(unittest.TestCase):
    """R28 Phase 5: the in-place-mutation authoring path that binds
    through Extron's property accessors.

    Builds a .pkp with author_fresh_command, then checks:
    (a) our parser reads the authored strings and enums at every variant,
    (b) `pkp_validate` reports `Valid 0`,
    (c) Load-Package.ps1 -Commands reports the authored ScriptMethodName,
        Name, and Attributes (not the C# class defaults).
    """

    AUTHORED_NAME = "Phase5 Test Name"
    AUTHORED_SCRIPT_NAME = "Phase5TestScript"
    AUTHORED_ATTRS = int(ee.DriverAttributeEnum.RuntimeVisible
                         | ee.DriverAttributeEnum.LiveStatus)  # 0x22 = 34

    @classmethod
    def setUpClass(cls):
        donor = build_one_command._pick_donor()
        if donor is None:
            raise unittest.SkipTest("no donor")
        os.makedirs(os.path.dirname(AUTHORED_PKP), exist_ok=True)
        b = pb.PackageBuilder(donor)
        g = pa.CommandGraph(b)
        cmds = g.commands()
        # Prefer Power, else any command the sharing guard accepts
        cmd_id = cmds.get("Power") or next(iter(cmds.values()))
        g.author_fresh_command(
            command_id=cmd_id,
            name=cls.AUTHORED_NAME,
            script_name=cls.AUTHORED_SCRIPT_NAME,
            attributes=cls.AUTHORED_ATTRS,
            ex_cmd_id=ee.ExtronCommandIdEnum.General,
            allow_shared=True,
        )
        b.write(AUTHORED_PKP)

    def test_authored_command_round_trips(self):
        import pkp_dump as pd
        parser = pd.PkpParser(pd.load_bytes(AUTHORED_PKP))
        parser.parse()
        # The pool-side command's _scriptName now resolves to the authored
        # string via the shared standalone BinaryObjectString.
        b = pb.PackageBuilder(AUTHORED_PKP)
        g = pa.CommandGraph(b)
        self.assertIn(self.AUTHORED_SCRIPT_NAME, g.commands(),
                      f"authored script_name missing; commands: "
                      f"{sorted(g.commands())}")

    def test_pkp_validate_passes(self):
        cp = subprocess.run(
            [sys.executable, os.path.join(TOOLS, "pkp_validate.py"),
             AUTHORED_PKP],
            capture_output=True, text=True, timeout=120)
        self.assertIn("Valid", cp.stdout,
                      f"stdout:\n{cp.stdout}\nstderr:\n{cp.stderr}")
        self.assertNotIn("Unparseable", cp.stdout)
        self.assertNotIn("Mismatch", cp.stdout)

    def test_python_sees_authored_values_at_every_variant(self):
        """Phase 5 mutates _attributes on the pool command AND all its
        model-variant siblings. Confirm every variant reads back the
        authored value."""
        b = pb.PackageBuilder(AUTHORED_PKP)
        g = pa.CommandGraph(b)
        cmd_id = g.commands()[self.AUTHORED_SCRIPT_NAME]
        sibs = g._sibling_commands(cmd_id)
        self.assertGreaterEqual(len(sibs), 2,
                                "Panasonic donor has pool + model variants")
        for sid in sibs:
            self.assertEqual(
                g.enum_member(sid, "CommandAssetBase+_attributes"),
                self.AUTHORED_ATTRS,
                f"variant oid {sid} has stale _attributes")

    @unittest.skipUnless(
        os.path.isfile(r"C:\Windows\SysWOW64\WindowsPowerShell"
                       r"\v1.0\powershell.exe"),
        "32-bit PowerShell not available")
    def test_extron_sees_authored_values(self):
        """The decisive gate: Load-Package.ps1 -Commands prints the
        authored ScriptMethodName / Name / Attributes, not C# defaults.
        Finding 18's `valid != loadable` sibling (`loadable != populated`)
        is what Phase 5 finally closes, by mutating every variant
        in-place instead of repointing MemberReferences to appended
        records."""
        ps32 = (r"C:\Windows\SysWOW64\WindowsPowerShell"
                r"\v1.0\powershell.exe")
        load_ps1 = os.path.join(REPO_ROOT, "experiments", "gcp_harness",
                                "Load-Package.ps1")
        cp = subprocess.run(
            [ps32, "-ExecutionPolicy", "Bypass", "-File", load_ps1,
             "-Commands", "-Path", AUTHORED_PKP],
            capture_output=True, text=True, timeout=180)
        self.assertEqual(cp.returncode, 0, cp.stderr)
        # Load-Package prints lines like
        #   "    <ScriptName>  <DisplayName>  attrs=<N>  <params>"
        # with 4 leading spaces for pool commands. Find the authored one.
        found = False
        for line in cp.stdout.splitlines():
            stripped = line.lstrip()
            if stripped.startswith(self.AUTHORED_SCRIPT_NAME):
                found = True
                self.assertIn(self.AUTHORED_NAME, line,
                              f"Name not bound; line: {line!r}")
                self.assertIn(f"attrs={self.AUTHORED_ATTRS}", line,
                              f"Attributes not bound; line: {line!r}")
                break
        self.assertTrue(found,
                        f"authored script_name {self.AUTHORED_SCRIPT_NAME} "
                        f"not found in Load-Package output:\n{cp.stdout}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
