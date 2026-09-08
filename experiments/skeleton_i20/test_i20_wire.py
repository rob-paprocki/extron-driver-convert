#!/usr/bin/env python3
"""
test_i20_wire.py - the acceptance oracle for the derived i20 driver.

STATUS.md's methodology note is explicit that acceptance is the wire-string
table, not file or line similarity. So this does not check that the derived
driver *looks* right: it loads the driver, drives every command, captures the
bytes it would put on the wire, and compares them against the byte templates
resolved from Crestron's own SchemaVersion 2.0 definition by resolve_visca.py.

That makes Crestron's declarative spec the referee - finding 11's pattern.
There is no i20 available to this repo, so a real device cannot arbitrate;
what CAN be established at a desk is that two vendors' encodings agree, and
that is what fails here if it stops being true.

Also checked: `wire correctness is necessary but not sufficient`. The driver
is imported and instantiated for real, so a dangling reference raises here
rather than on a processor.

Run: python3 experiments/skeleton_i20/test_i20_wire.py
"""

import os
import re
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import build_i20                      # noqa: E402
import pkp_build as pb                # noqa: E402
import resolve_visca                  # noqa: E402

PASS, FAIL = [], []
CRESTRON_PKG = os.path.join(
    _ROOT, "samples", "Crestron 1 Beyond IV-CAM-i12_i20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg")


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "\n         " + detail))
    return cond


# ---------------------------------------------------------------------------
# A stand-in for the Global Configurator runtime.
# ---------------------------------------------------------------------------
class _Mutex(object):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class StubBaseDriver(object):
    """Minimal BaseDriver. Records what the driver would transmit.

    Deliberately does NOT emulate device behaviour - the point is to observe
    the driver's output, not to simulate a camera we have never seen.
    """

    def __init__(self, configs):
        self.sent = []
        self.errors = []
        self.discards = []
        self.disabled = False
        self._canned = b""

    # -- transport -------------------------------------------------------
    def Send(self, data):
        self.sent.append(bytes(data))

    def SendAndWait(self, data, timeout, deliTag=None):
        self.sent.append(bytes(data))
        return self._canned

    # -- framework -------------------------------------------------------
    def Error(self, msgs):
        self.errors.append(msgs)

    def Discard(self, why):
        self.discards.append(why)

    def Disable(self):
        self.disabled = True

    def Mutex(self):
        return _Mutex()

    def StartQueryDelayTimer(self, t):
        pass

    def QueryDelayTimerIsRunning(self):
        return False

    def PostNewStatusEx(self, *a, **k):
        pass

    def WriteDeviceResponseStatus(self, *a, **k):
        pass


def load_driver_class(source, class_name):
    """Execute the derived driver in a namespace shaped like GC's.

    ExtronTime is supplied here because the driver uses it 7 times as a bare
    name with no import - the host populates the module globals beyond the
    driver's own import list. That is a real property of the runtime, and a
    from-scratch emitter needs to know it.
    """
    pkg = types.ModuleType("Extron2")
    mod = types.ModuleType("Extron2.BaseDriver")
    mod.BaseDriver = StubBaseDriver
    pkg.BaseDriver = mod
    sys.modules["Extron2"] = pkg
    sys.modules["Extron2.BaseDriver"] = mod

    ns = {"__name__": "derived_i20", "ExtronTime": lambda t: t}
    exec(compile(source, "<derived_i20>", "exec"), ns)
    return ns[class_name]


CONFIGS = {
    "Unidirectional": "True",
    "DriverParams": {"Device ID": 1},
    "CommandPacing": 0,
    "ResponseTimeout": 1,
}


def make(unidirectional="True"):
    builder = pb.PackageBuilder(build_i20.DONOR)
    slot = builder.scripts()[0]
    cls = load_driver_class(build_i20.derive(slot.source),
                            os.path.splitext(slot.key)[0])
    cfg = dict(CONFIGS)
    cfg["Unidirectional"] = unidirectional
    d = cls(cfg)
    return d


def hexs(b):
    return " ".join("%02X" % x for x in b)


def drive(d, method, *args):
    """Call a _cmd_ method and return the single frame it transmitted."""
    d.sent = []
    getattr(d, method)(*args)
    if len(d.sent) != 1:
        return None
    return d.sent[0]


# ---------------------------------------------------------------------------

def test_driver_loads():
    print("\n[1] the derived driver imports, instantiates and reports no init error")
    d = make()
    check("instantiated without Error()", d.errors == [], repr(d.errors))
    check("not disabled by init validation", d.disabled is False)
    check("DeviceID resolved to VISCA header 0x81", d.DeviceID == 0x81,
          hex(d.DeviceID))


def test_i20_set_commands():
    print("\n[2] i20 SET commands emit the bytes Crestron declares")
    d = make()
    cases = [
        ("_cmd_SetTrackingFraming",  ("Start", None),  "81 01 04 3F 02 50 FF"),
        ("_cmd_SetTrackingFraming",  ("Stop", None),   "81 01 04 3F 02 51 FF"),
        ("_cmd_SetGroupTracking",    ("Enable", None), "81 01 04 3F 02 52 FF"),
        ("_cmd_SetPresenterTracking", ("Enable", None), "81 01 04 3F 02 53 FF"),
        ("_cmd_SetMenu",             ("Toggle", None), "81 01 04 3F 02 5F FF"),
        ("_cmd_SetReboot",           ("Reboot", None), "81 01 04 3F 02 63 FF"),
        ("_cmd_SetIdentify",         ("Identify", None), "81 C2 01 01 0A FF"),
        ("_cmd_SetFreezeFrame",      ("On", None),     "81 01 04 62 02 FF"),
        ("_cmd_SetFreezeFrame",      ("Off", None),    "81 01 04 62 03 FF"),
        ("_cmd_SetPanTiltHome",      ("Reset", None),  "81 01 06 05 FF"),
    ]
    for method, args, expect in cases:
        got = drive(d, method, *args)
        label = "%s%s" % (method[len("_cmd_Set"):],
                          "" if args[0] is None else "(%s)" % args[0])
        check("%-28s -> %s" % (label, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_nibble_encoding():
    print("\n[3] absolute-position commands (the IL-only transformations)")
    d = make()
    # ViscaAssemble4LowerNibbles: 0x1A2B -> 01 0A 02 0B
    got = drive(d, "_cmd_SetZoomPosition", 0x1A2B, {"Speed": 3})
    check("ZoomPosition(0x1A2B, spd 3)  -> 81 01 04 47 03 01 0A 02 0B FF",
          got is not None and hexs(got) == "81 01 04 47 03 01 0A 02 0B FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))

    got = drive(d, "_cmd_SetPanTiltAngle",
                {"Pan": 0x0123, "Tilt": 0x0456},
                {"Pan Speed": 0x18, "Tilt Speed": 0x14})
    check("PanTiltAngle(0x0123, 0x0456) -> 81 01 06 02 18 14 00 01 02 03 00 04 05 06 FF",
          got is not None and
          hexs(got) == "81 01 06 02 18 14 00 01 02 03 00 04 05 06 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))

    check("_Nibbles round-trips through _FromNibbles",
          d._FromNibbles(d._Nibbles(0xBEEF, 4)) == 0xBEEF)


def test_inquiries():
    print("\n[4] UPDATE commands emit the inquiries Crestron declares")
    d = make(unidirectional="False")
    d._canned = b""          # no reply: we are checking the request only
    # Extron's __UpdateHelper bails out when Live power status is unknown -
    # `None` is in its refusal list alongside 'Off'. That is deliberate (do not
    # poll a camera you have no reason to think is awake), so a poll test has to
    # establish power first or it measures the guard rather than the command.
    d.WritePower("On", None, "Live")
    cases = [
        ("_cmd_UpdateTrackingFraming", "81 09 08 01 FF"),
        ("_cmd_UpdateZoomPosition",    "81 09 04 47 FF"),
        ("_cmd_UpdatePanTiltAngle",    "81 09 06 12 FF"),
        ("_cmd_UpdateFreezeFrame",     "81 09 04 62 FF"),
    ]
    for method, expect in cases:
        d.sent = []
        getattr(d, method)(None, {"Speed": 0, "Pan Speed": 1, "Tilt Speed": 1})
        got = d.sent[0] if d.sent else None
        check("%-28s -> %s" % (method[len("_cmd_Update"):], expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_zoom_bug_is_fixed():
    print("\n[5] E2: the zoom-speed defect is gone and Extron's other bytes are not")
    d = make()
    got = drive(d, "_cmd_SetZoom", "Tele", {"Speed": 5})
    check("Zoom(Tele, speed 5) -> 81 01 04 07 25 FF  (0x20|5, was 0x20)",
          got is not None and hexs(got) == "81 01 04 07 25 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))
    got = drive(d, "_cmd_SetZoom", "Stop", {"Speed": 5})
    check("Zoom(Stop) -> 81 01 04 07 00 FF",
          got is not None and hexs(got) == "81 01 04 07 00 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))

    # Regression: Extron's untouched commands must be untouched.
    got = drive(d, "_cmd_SetPower", "On", None)
    check("Power(On) unchanged -> 81 01 04 00 02 FF",
          got is not None and hexs(got) == "81 01 04 00 02 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))
    got = drive(d, "_cmd_SetPreset", 3, {"Action": "Recall"})
    check("Preset(Recall 3) unchanged -> 81 01 04 3F 02 03 FF",
          got is not None and hexs(got) == "81 01 04 3F 02 03 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_against_crestron_spec():
    print("\n[6] the expectations above are Crestron's, not ours")
    # Re-derive the byte templates straight from the Crestron package, so this
    # test fails if the spec says something different from what we hardcoded.
    if not os.path.exists(CRESTRON_PKG):
        check("Crestron i20 package present", False, CRESTRON_PKG)
        return
    dd = resolve_visca.load(CRESTRON_PKG)
    expected = {
        "StartTrackingFraming":    "04 3f 02 50",
        "StopTrackingFraming":     "04 3f 02 51",
        "EnableGroupTracking":     "04 3f 02 52",
        "EnablePresenterTracking": "04 3f 02 53",
        "Menu":                    "04 3f 02 5f",
        "Reboot":                  "04 3f 02 63",
    }
    for name, want in expected.items():
        t = resolve_visca.resolve(dd, name)
        flat = re.sub(r"\s+", " ", t.replace("{:hex}", "")).strip()
        check("Crestron %-24s declares %s" % (name, want), want in flat.lower(),
              "resolved to %r" % flat)


def test_lightbar_matches_every_documented_string():
    print("\n[9] the lightbar packing reproduces all 19 documented commands")
    # Verbatim from reference/crestron-visca/COMMANDS.md section 8 - both the
    # status-driven table and the user-settable table. If the derived packing
    # rule (brightness << 2 | colour, half keeps outer colour bits at
    # brightness 0) is wrong for even one row, it is the wrong rule.
    doc = [
        # (width,  colour,   brightness, expected payload)
        ("None", "Green",  "Off",    "00 00 00 00"),
        ("Full", "Green",  "Bright", "0C 0C 0C 0C"),
        ("Full", "Green",  "Medium", "08 08 08 08"),
        ("Full", "Green",  "Dim",    "04 04 04 04"),
        ("Full", "Yellow", "Bright", "0F 0F 0F 0F"),
        ("Full", "Yellow", "Medium", "0B 0B 0B 0B"),
        ("Full", "Yellow", "Dim",    "07 07 07 07"),
        ("Full", "Red",    "Bright", "0D 0D 0D 0D"),
        ("Full", "Red",    "Medium", "09 09 09 09"),
        ("Full", "Red",    "Dim",    "05 05 05 05"),
        ("Half", "Green",  "Bright", "00 0C 0C 00"),
        ("Half", "Green",  "Medium", "00 08 08 00"),
        ("Half", "Green",  "Dim",    "00 04 04 00"),
        ("Half", "Yellow", "Bright", "03 0F 0F 03"),
        ("Half", "Yellow", "Medium", "03 0B 0B 03"),
        ("Half", "Yellow", "Dim",    "03 07 07 03"),
        ("Half", "Red",    "Bright", "01 0D 0D 01"),
        ("Half", "Red",    "Medium", "01 09 09 01"),
        ("Half", "Red",    "Dim",    "01 05 05 01"),
    ]
    d = make()
    for width, colour, brightness, payload in doc:
        expect = "81 C1 %s FF" % payload
        got = drive(d, "_cmd_SetIndicatorLight", width,
                    {"Color": colour, "Brightness": brightness})
        check("%-4s %-6s %-6s -> %s" % (width, colour, brightness, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))

    # The four status-driven colours in the doc's first table must fall out of
    # the same rule - they are not a separate encoding.
    status_rows = [
        ("Full", "Green",  "Bright", "0C 0C 0C 0C", "intelligent camera function ON"),
        ("Half", "Green",  "Bright", "00 0C 0C 00", "camera output ON"),
        ("Full", "Yellow", "Bright", "0F 0F 0F 0F", "firmware update in progress"),
        ("Half", "Red",    "Bright", "01 0D 0D 01", "privacy mode ON"),
    ]
    for width, colour, brightness, payload, meaning in status_rows:
        got = drive(d, "_cmd_SetIndicatorLight", width,
                    {"Color": colour, "Brightness": brightness})
        check("status colour: %-32s = %s" % (meaning, payload),
              got is not None and hexs(got) == "81 C1 %s FF" % payload)


def test_tracking_feedback():
    print("\n[10] tracking feedback parses the documented reply")
    # reference/crestron-visca/COMMANDS.md: CAM_TrackingInq
    #     y0 50 02 FF = active,  y0 50 03 FF = paused
    for reply, expect in ((b"\x90\x50\x02\xFF", "Start"),
                          (b"\x90\x50\x03\xFF", "Stop")):
        d = make(unidirectional="False")
        d.WritePower("On", None, "Live")
        d._canned = reply
        d._cmd_UpdateTrackingFraming(None, None)
        got = d.ReadTrackingFraming(None, "Live")
        check("%s -> %s" % (hexs(reply), expect), got == expect,
              "got %r, errors=%r" % (got, d.errors))

    # A reply the documentation does not define must raise, not be guessed at.
    d = make(unidirectional="False")
    d.WritePower("On", None, "Live")
    d._canned = b"\x90\x50\x07\xFF"
    d._cmd_UpdateTrackingFraming(None, None)
    check("undocumented payload 0x07 reports an error rather than a value",
          d.errors != [] and d.ReadTrackingFraming(None, "Live") is None,
          "errors=%r status=%r" % (d.errors, d.ReadTrackingFraming(None, "Live")))


def test_reserved_presets_against_documentation():
    print("\n[11] reserved presets agree with Crestron's own preset table")
    # COMMANDS.md section 10 gives these in DECIMAL. The driver gives them in
    # hex. Checking the two against each other is the point.
    d = make()
    cases = [
        ("_cmd_SetTrackingShot",   ("Home", None),     0,   "Home Shot"),
        ("_cmd_SetTrackingShot",   ("Tracking", None), 1,   "Tracking Shot"),
        ("_cmd_SetTrackingFraming", ("Start", None),   80,  "Start Tracking"),
        ("_cmd_SetTrackingFraming", ("Stop", None),    81,  "Pause Tracking"),
        ("_cmd_SetGroupTracking",  ("Enable", None),   82,  "Start Group Tracking"),
        ("_cmd_SetMenu",           ("Toggle", None),   95,  "OSD Menu Toggle"),
        ("_cmd_SetReboot",         ("Reboot", None),   99,  "Reboot"),
    ]
    for method, args, decimal, label in cases:
        got = drive(d, method, *args)
        expect = "81 01 04 3F 02 %02X FF" % decimal
        check("preset %3d %-22s -> %s" % (decimal, label, expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))

    for value, decimal in ((1, 105), (4, 108)):
        got = drive(d, "_cmd_SetTrackingProfile", value, None)
        check("preset %d Tracking Profile %d" % (decimal, value),
              got is not None and hexs(got) == "81 01 04 3F 02 %02X FF" % decimal,
              "got %s" % (hexs(got) if got else "<nothing sent>"))
    for value, decimal in ((1, 101), (4, 104)):
        got = drive(d, "_cmd_SetPresetZone", value, None)
        check("preset %d Preset Zone %d" % (decimal, value),
              got is not None and hexs(got) == "81 01 04 3F 02 %02X FF" % decimal,
              "got %s" % (hexs(got) if got else "<nothing sent>"))

    # The one byte the two sources disagree about. Both readings are the same
    # wire byte, so the driver is correct either way - only the label is at
    # stake. Asserting the byte keeps that explicit.
    got = drive(d, "_cmd_SetPresenterTracking", "Enable", None)
    check("preset  83 CONTESTED (driver: presenter tracking / docs: pause group)"
          " -> 81 01 04 3F 02 53 FF",
          got is not None and hexs(got) == "81 01 04 3F 02 53 FF",
          "got %s" % (hexs(got) if got else "<nothing sent>"))


def test_intelligent_switching():
    print("\n[12] intelligent switching (camera selection)")
    d = make()
    cases = [
        ("_cmd_SetCameraOutput",         (1, None),         "81 C2 01 08 01 FF"),
        ("_cmd_SetCameraOutput",         (5, None),         "81 C2 01 08 05 FF"),
        ("_cmd_SetCameraOutput",         (0, None),         "81 C2 01 08 00 FF"),
        ("_cmd_SetIntelligentSwitching", ("Pause", None),   "81 C2 01 0B 00 FF"),
        ("_cmd_SetIntelligentSwitching", ("Resume", None),  "81 C2 01 08 00 FF"),
    ]
    for method, args, expect in cases:
        got = drive(d, method, *args)
        check("%-28s %-8s -> %s" % (method[len("_cmd_Set"):], args[0], expect),
              got is not None and hexs(got) == expect,
              "got %s" % (hexs(got) if got else "<nothing sent>"))

    du = make(unidirectional="False")
    du.WritePower("On", None, "Live")
    du._canned = b""
    du.sent = []
    du._cmd_UpdateCameraConnectionStatus(None, {"Camera": 3})
    check("ConnectionStatus(cam 3) -> 81 C2 09 0D 03 FF",
          du.sent and hexs(du.sent[0]) == "81 C2 09 0D 03 FF",
          "got %s" % (hexs(du.sent[0]) if du.sent else "<nothing sent>"))

    for reply, expect in ((b"\x90\x50\x00\x01\xFF", "Connected"),
                          (b"\x90\x50\x00\x00\xFF", "Disconnected")):
        dd_ = make(unidirectional="False")
        dd_.WritePower("On", None, "Live")
        dd_._canned = reply
        dd_._cmd_UpdateCameraConnectionStatus(None, {"Camera": 2})
        got = dd_.ReadCameraConnectionStatus({"Camera": 2}, "Live")
        check("%s -> %s" % (hexs(reply), expect), got == expect,
              "got %r" % got)


def test_python35_compatible():
    print("\n[7] the emitted driver targets Python 3.5 (non-xi processors)")
    builder = pb.PackageBuilder(build_i20.DONOR)
    src = build_i20.derive(builder.scripts()[0].source)
    check("no f-strings", not re.search(r"""\bf['"]""", src))
    check("no walrus operator", ":=" not in src)
    check("no dataclasses import", "dataclass" not in src)
    # 3.5 cannot parse f-strings, so a 3.5-targeted file must compile with
    # nothing newer than 3.5 syntax. We cannot run 3.5 here, but we can assert
    # the constructs that would break it are absent.
    check("compiles on this interpreter", _compiles(src))


def _compiles(src):
    try:
        compile(src, "<derived>", "exec")
        return True
    except SyntaxError:
        return False


def test_package_reparses():
    print("\n[8] the built .pkp reads back with the derived driver inside")
    out = os.path.join(_HERE, "out", "1bynd_19_20022_v1_0_0.pkp")
    if not os.path.exists(out):
        check("T2 package built", False, "run build_i20.py first")
        return
    b2 = pb.PackageBuilder(out)          # round-trip gate runs again on OUR output
    slots = b2.scripts()
    check("output round-trips byte-identically", True)   # constructor would have raised
    check("exactly one embedded script", len(slots) == 1)
    if slots:
        src = slots[0].source
        check("carries the i20 command set", "_cmd_SetTrackingFraming" in src)
        check("carries the E2 fix", "[PATCH E2]" in src)
        check("still compiles after the round trip", _compiles(src))


def main():
    print("test_i20_wire.py - wire oracle for the derived i20 driver")
    for fn in (test_driver_loads,
               test_i20_set_commands,
               test_nibble_encoding,
               test_inquiries,
               test_zoom_bug_is_fixed,
               test_against_crestron_spec,
               test_lightbar_matches_every_documented_string,
               test_tracking_feedback,
               test_reserved_presets_against_documentation,
               test_intelligent_switching,
               test_python35_compatible,
               test_package_reparses):
        fn()
    print("\n%d passed, %d failed, %d total"
          % (len(PASS), len(FAIL), len(PASS) + len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
