"""Tests for decompile.py's package reading. Synthetic packages only: no vendor material, no ilspycmd."""
import io
import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import decompile  # noqa: E402


def zip_bytes(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return buf.getvalue()


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cresdb = self.tmp.name
        os.makedirs(os.path.join(self.cresdb, "Modules"))
        os.makedirs(os.path.join(self.cresdb, "Programming", "Libraries"))
        clz_a = zip_bytes({"Automate_VX.dll": b"MZ-a", "Automate_VX.xml": b"<doc/>"})
        clz_b = zip_bytes({"Automate_Vx_4Series.dll": b"MZ-b"})
        with zipfile.ZipFile(decompile.splus_store(self.cresdb), "w") as z:
            z.writestr("Automate_VX.clz", clz_a)
            z.writestr("Automate_Vx_4Series.clz", clz_b)
            z.writestr("Other.csp", b"// SIMPL+")
            z.writestr("Broken.clz", b"not a zip")
        with open(os.path.join(decompile.libraries_dir(self.cresdb), "Crestron.SimplSharpPro.DM.dll"), "wb") as f:
            f.write(b"MZ-dm")

    def tearDown(self):
        self.tmp.cleanup()

    def test_clz_members_lists_only_dlls_and_skips_bad_packages(self):
        got = sorted((clz, dll) for clz, dll, _ in decompile.clz_members(decompile.splus_store(self.cresdb)))
        self.assertEqual(got, [("Automate_VX.clz", "Automate_VX.dll"),
                               ("Automate_Vx_4Series.clz", "Automate_Vx_4Series.dll")])

    def test_match_is_on_the_whole_stem(self):
        # "Automate_VX" must not also pull in Automate_Vx_4Series.
        self.assertTrue(decompile.matches("Automate_VX.dll", ["automate_vx"]))
        self.assertFalse(decompile.matches("Automate_Vx_4Series.dll", ["Automate_VX"]))

    def test_extract_reads_packages_and_loose_libraries(self):
        out = os.path.join(self.tmp.name, "dll")
        got = decompile.extract(self.cresdb, decompile.DEFAULT_NAMES, out)
        self.assertEqual(sorted(got), ["Automate_VX.dll", "Automate_Vx_4Series.dll",
                                       "Crestron.SimplSharpPro.DM.dll"])
        with open(got["Crestron.SimplSharpPro.DM.dll"], "rb") as f:
            self.assertEqual(f.read(), b"MZ-dm")
        self.assertEqual(len(decompile.sha256(got["Automate_VX.dll"])), 64)


if __name__ == "__main__":
    unittest.main()
