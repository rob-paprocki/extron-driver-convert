#!/usr/bin/env python3
"""
test_p20_wire.py - the acceptance oracle for the derived p20 driver, mirroring
experiments/skeleton_i20/test_i20_wire.py.

Same discipline as the i20 test: load the derived driver for real, drive every
command, capture the bytes it would put on the wire, and compare them against
byte templates resolved from Crestron's own SchemaVersion 2.0 definition for
IV-CAM-P20_IP - not against the i20 driver, and not against a hand-typed
expectation that could quietly drift from either.

Reuse: imports experiments/skeleton_i20/test_i20_wire.py for the generic test
harness (`check`, `StubBaseDriver`, `load_driver_class`, `hexs`, `drive`,
`age_inquiry_cache`, `template_regex`) - none of it names I20 or P20, it is a
stand-in for the GC runtime and a byte-comparison helper. Only `make()`/
`polling()`/`CONFIGS` are rewritten, because they point at a different derived
driver (build_p20 instead of build_i20).

Run: python3 experiments/skeleton_p20/test_p20_wire.py
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_I20 = os.path.join(_ROOT, "experiments", "skeleton_i20")
sys.path.insert(0, _HERE)
sys.path.insert(0, _I20)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import vendor_inputs                  # noqa: E402
# Every check here builds the driver from Extron's donor and compares it
# with Crestron's own driver; the repository publishes neither
# (vendor-files.manifest.tsv), so without them the suite is skipped, visibly.
vendor_inputs.skip_suite(
    os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp", "1bynd_19_4743_v1_0_1.pkp"),
    os.path.join(_ROOT, "samples", "Crestron 1 Beyond IV-CAM-i12_i20", "Crestron",
                 "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg"),
    os.path.join(_ROOT, "samples", "Crestron 1 Beyond IV-CAM-p12_p20", "Crestron",
                 "Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg"),
)

import build_p20                       # noqa: E402
import test_i20_wire as it              # noqa: E402  (imported as a library, not edited)
import pkp_build as pb                  # noqa: E402
import resolve_visca                    # noqa: E402  (experiments/skeleton_i20/resolve_visca.py)

PASS, FAIL = it.PASS, it.FAIL
check = it.check
StubBaseDriver = it.StubBaseDriver
load_driver_class = it.load_driver_class
hexs = it.hexs
age_inquiry_cache = it.age_inquiry_cache
template_regex = it.template_regex

P20_PKG = os.path.join(
    _ROOT, "samples", "Crestron 1 Beyond IV-CAM-p12_p20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg")

CONFIGS = {
    "Unidirectional": "True",
    "DriverParams": {"Device ID": 1},
    "CommandPacing": 0,
    "ResponseTimeout": 1,
}


def make(unidirectional="True"):
    builder = pb.PackageBuilder(build_p20.DONOR)
    slot = builder.scripts()[0]
    cls = load_driver_class(build_p20.derive(slot.source),
                            os.path.splitext(slot.key)[0])
    cfg = dict(CONFIGS)
    cfg["Unidirectional"] = unidirectional
    return cls(cfg)


def drive(d, method, *args):
    d.sent = []
    getattr(d, method)(*args)
    if len(d.sent) != 1:
        return None
    return d.sent[0]


def polling(unidirectional="False"):
    d = make(unidirectional=unidirectional)
    d.WritePower("On", None, "Live")
    return d


# ---------------------------------------------------------------------------

def test_driver_loads():
    print("\n[1] the derived p20 driver imports, instantiates and reports no init error")
    d = make()
    check("instantiated without Error()", d.errors == [], repr(d.errors))
    check("not disabled by init validation", d.disabled is False)
    check("DeviceID resolved to VISCA header 0x81", d.DeviceID == 0x81, hex(d.DeviceID))


def test_shared_set_commands():
    print("\n[2] commands shared with i20 emit the SAME bytes on p20 (i20_p20_diff.txt)")
    d = make()
    cases = [
        ("_cmd_SetMenu",        ("Toggle", None), "81 01 04 3F 02 5F FF"),
        ("_cmd_SetReboot",      ("Reboot", None), "81 01 04 3F 02 63 FF"),
        ("_cmd_SetIdentify",    ("Identify", None), "81 C2 01 01 0A FF"),
        ("_cmd_SetFreezeFrame", ("On", None),     "81 01 04 62 02 FF"),
        ("_cmd_SetFreezeFrame", ("Off", None),    "81 01 04 62 03 FF"),
        ("_cmd_SetPanTiltHome", ("Reset", None),  "81 01 06 05 FF"),
    ]
    for method, args, expect in cases:
        got = drive(d, method, *args)
        label = "%s(%s)" % (method[len("_cmd_Set"):], args[0])
        check("%-28s -> %s" % (label, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_mountmode():
    print("\n[3] MountMode - the one command family P20 has and I20 does not")
    d = make()
    cases = [
        ("Stand", "81 01 04 A4 02 FF"),
        ("Ceiling", "81 01 04 A4 03 FF"),
    ]
    for value, expect in cases:
        got = drive(d, "_cmd_SetMountMode", value, None)
        check("SetMountMode(%s) -> %s" % (value, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))
    check("SetMountMode('Invalid') is refused", drive(d, "_cmd_SetMountMode", "Invalid", None) is None)

    du = polling()
    du._canned = b""
    got = drive(du, "_cmd_UpdateMountMode", None, None)
    check("UpdateMountMode -> 81 09 04 A4 FF",
          got is not None and hexs(got) == "81 09 04 A4 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))

    # Reply parsing: COMMANDS.md:287-288 (CAM_MountModeInq).
    for reply, expect in ((b"\x90\x50\x02\xFF", "Stand"), (b"\x90\x50\x03\xFF", "Ceiling")):
        dd = polling()
        dd._canned = reply
        dd._cmd_UpdateMountMode(None, None)
        got = dd.ReadMountMode(None, "Live")
        check("%s -> %s" % (hexs(reply), expect), got == expect,
              "got %r, errors=%r" % (got, dd.errors))
    de = polling()
    de._canned = b"\x90\x50\x07\xFF"
    de._cmd_UpdateMountMode(None, None)
    check("undocumented MountMode payload 0x07 reports an error, not a guess",
          de.errors != [] and de.ReadMountMode(None, "Live") is None)


def test_nibble_encoding():
    print("\n[4] absolute-position commands, same nibble helpers i20 uses")
    d = make()
    got = drive(d, "_cmd_SetZoomPosition", 0x1A2B, {"Speed": 3})
    check("ZoomPosition(0x1A2B, spd 3)  -> 81 01 04 47 03 01 0A 02 0B FF",
          got is not None and hexs(got) == "81 01 04 47 03 01 0A 02 0B FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))
    got = drive(d, "_cmd_SetPanTiltAngle", None,
               {"Pan Speed": 0x18, "Tilt Speed": 0x14, "Pan": 0x0123, "Tilt": 0x0456})
    check("PanTiltAngle(0x0123, 0x0456) -> 81 01 06 02 18 14 00 01 02 03 00 04 05 06 FF",
          got is not None and hexs(got) == "81 01 06 02 18 14 00 01 02 03 00 04 05 06 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))
    check("_Nibbles round-trips through _FromNibbles",
          d._FromNibbles(d._Nibbles(0xBEEF, 4)) == 0xBEEF)


def test_zoom_bug_is_fixed():
    print("\n[5] E2 (reused from build_i20.patch_zoom) fixes the same defect here")
    d = make()
    got = drive(d, "_cmd_SetZoom", "Tele", {"Speed": 5})
    check("Zoom(Tele, speed 5) -> 81 01 04 07 25 FF  (0x20|5, was 0x20)",
          got is not None and hexs(got) == "81 01 04 07 25 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))
    got = drive(d, "_cmd_SetPower", "On", None)
    check("Power(On) unchanged -> 81 01 04 00 02 FF",
          got is not None and hexs(got) == "81 01 04 00 02 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_against_crestron_spec():
    print("\n[6] the expectations above are P20's Crestron driver's own, not ours")
    if not os.path.exists(P20_PKG):
        check("Crestron p20 package present", False, P20_PKG)
        return
    dd = resolve_visca.load(P20_PKG)
    expected = {
        "SetInverted":  "04 a4",
        "GetInverted":  "09 04 a4",
        "Menu":         "04 3f 02 5f",
        "Reboot":       "04 3f 02 63",
        "Identify":     "c2 01 01 0a",
    }
    for name, want in expected.items():
        t = resolve_visca.resolve(dd, name)
        flat = re.sub(r"\s+", " ", t.replace("{:hex}", "")).strip()
        check("Crestron %-16s declares %s" % (name, want), want in flat.lower(),
              "resolved to %r" % flat)


def test_removed_commands_are_gone():
    print("\n[7] the eight I-series-only commands are NOT reachable on p20")
    d = make()
    for name in build_p20._I_ONLY_COMMANDS:
        check("no _cmd_Set%s / _cmd_Update%s" % (name, name),
              not hasattr(d, "_cmd_Set%s" % name) and not hasattr(d, "_cmd_Update%s" % name))


def test_lightbar_matches_every_documented_string():
    print("\n[8] the lightbar packing is byte-identical to i20's (i20_p20_diff.txt "
          "confirms MapIndicatorLightToLedBar is the same Map on both models)")
    doc = [
        ("None", "Green",  "Off",    "00 00 00 00"),
        ("Full", "Green",  "Bright", "0C 0C 0C 0C"),
        ("Full", "Yellow", "Bright", "0F 0F 0F 0F"),
        ("Full", "Red",    "Bright", "0D 0D 0D 0D"),
        ("Half", "Green",  "Bright", "00 0C 0C 00"),
        ("Half", "Yellow", "Bright", "03 0F 0F 03"),
        ("Half", "Red",    "Bright", "01 0D 0D 01"),
    ]
    d = make()
    for width, colour, brightness, payload in doc:
        expect = "81 C1 %s FF" % payload
        got = drive(d, "_cmd_SetIndicatorLight", width, {"Color": colour, "Brightness": brightness})
        check("%-4s %-6s %-6s -> %s" % (width, colour, brightness, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_parity_commands():
    print("\n[9] the shared 'parity' block emits identical bytes to i20's")
    d = make()
    sets = [
        ("_cmd_SetExposureCompensationMode", ("On", None), "81 01 04 3E 02 FF"),
        ("_cmd_SetExposureCompensation", (7, None), "81 01 04 4E 00 00 00 07 FF"),
        ("_cmd_SetOnePushAutoFocus", ("Trigger", None), "81 01 04 18 01 FF"),
        ("_cmd_SetAutoFocusBehavior", ("Face", None), "81 C2 01 02 04 FF"),
        ("_cmd_SetAutoFocusSensitivity", (2, None), "81 C2 01 03 02 FF"),
        ("_cmd_SetAutoPrivacyMode", ("On", None), "81 01 0E 24 26 00 01 FF"),
        ("_cmd_SetAutoSoftwareUpdate", ("On", None), "81 C2 01 04 01 FF"),
    ]
    for method, args, expect in sets:
        got = drive(d, method, *args)
        check("%-28s %-8s -> %s" % (method[len("_cmd_Set"):], args[0], expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))

    du = polling()
    du._canned = b""
    inquiries = [
        ("_cmd_UpdateExposureCompensationMode", "81 09 04 3E FF"),
        ("_cmd_UpdateFocusPosition", "81 09 04 48 FF"),
        ("_cmd_UpdateAutoFocusBehavior", "81 C2 09 02 FF"),
        ("_cmd_UpdateDeviceModel", "81 09 00 02 FF"),
        ("_cmd_UpdatePanSpeedMaxStatus", "81 09 06 11 FF"),
    ]
    for method, expect in inquiries:
        got = drive(du, method, None, None)
        check("%-28s -> %s" % (method[len("_cmd_Update"):], expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_device_model_reports_p_models():
    print("\n[10] DeviceModel decodes the P20/P12 model codes (05 07 / 05 08)")
    cases = [
        (b"\x90\x50\x00\x01\x05\x07\x00\x01\x01\xFF", "IV-CAM-P20"),
        (b"\x90\x50\x00\x01\x05\x08\x00\x01\x01\xFF", "IV-CAM-P12"),
    ]
    for reply, expect in cases:
        d = polling()
        d._canned = reply
        d._cmd_UpdateDeviceModel(None, None)
        got = d.ReadDeviceModel(None, "Live")
        check("%s -> %s" % (hexs(reply), expect), got == expect,
              "got %r, errors=%r" % (got, d.errors))


def test_python35_compatible():
    print("\n[11] the emitted driver targets Python 3.5 (non-xi processors)")
    builder = pb.PackageBuilder(build_p20.DONOR)
    src = build_p20.derive(builder.scripts()[0].source)
    check("no f-strings", not re.search(r"""\bf['"]""", src))
    check("no walrus operator", ":=" not in src)
    check("compiles on this interpreter", it._compiles(src))


def test_package_reparses():
    print("\n[12] the built .pkp reads back with the derived p20 driver inside")
    out = os.path.join(_HERE, "out", "1bynd_19_20101_v1_0_0.pkp")
    if not os.path.exists(out):
        check("stage-1 package built", False, "run build_p20.py first")
        return
    b2 = pb.PackageBuilder(out)
    slots = b2.scripts()
    check("output round-trips byte-identically", True)
    check("exactly one embedded script", len(slots) == 1)
    if slots:
        src = slots[0].source
        check("carries the p20 command set", "_cmd_SetMountMode" in src)
        check("carries the E2 fix", "[PATCH E2]" in src)
        check("does NOT carry the removed I-series commands",
              "_cmd_SetTrackingFraming" not in src and "_cmd_SetCameraOutput" not in src)
        check("still compiles after the round trip", it._compiles(src))

    out2 = os.path.join(_HERE, "out", "1bynd_19_20102_v1_0_0.pkp")
    check("stage-2 (graph) package built", os.path.exists(out2),
          "run build_p20_assets.py first")
    if os.path.exists(out2):
        b3 = pb.PackageBuilder(out2)         # round-trip gate runs again on stage-2 output
        check("stage-2 output round-trips byte-identically", True)


def test_cs_module_matches():
    print("\n[13] the ControlScript module (build_p20_cs.py) agrees byte-for-byte")
    cs_path = os.path.join(_HERE, "out", "onebynd_camera_IV_CAM_P20_v1_0_0_0.py")
    if not os.path.exists(cs_path):
        check("ControlScript module built", False, "run build_p20_cs.py first")
        return
    with open(cs_path, encoding="utf-8") as fh:
        src = fh.read()
    check("carries MountMode", "def SetMountMode" in src and "def UpdateMountMode" in src)
    check("does not carry the removed I-series commands",
          "def SetTrackingFraming" not in src and "def SetCameraOutput" not in src)
    check("still compiles", it._compiles(src))


def main():
    print("test_p20_wire.py - wire oracle for the derived p20 driver")
    for fn in (test_driver_loads,
               test_shared_set_commands,
               test_mountmode,
               test_nibble_encoding,
               test_zoom_bug_is_fixed,
               test_against_crestron_spec,
               test_removed_commands_are_gone,
               test_lightbar_matches_every_documented_string,
               test_parity_commands,
               test_device_model_reports_p_models,
               test_python35_compatible,
               test_package_reparses,
               test_cs_module_matches):
        fn()
    print("\n%d passed, %d failed, %d total"
          % (len(PASS), len(FAIL), len(PASS) + len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
