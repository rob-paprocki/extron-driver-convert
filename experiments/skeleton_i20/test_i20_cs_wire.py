#!/usr/bin/env python3
"""
test_i20_cs_wire.py - wire oracle for the ControlScript i20 module.

Two jobs:

  1. The same byte expectations as test_i20_wire.py, applied to the other
     emitter. Every command must produce identical bytes in both driver forms.
  2. The ControlScript-specific surface: the public Set/Update/ReadStatus
     dispatch, the three transport classes, and the UDP->TCP default change.

Job 1 is the interesting one. STATUS.md asks whether a shared intermediate
representation is justified; if the two emitters ever disagree on a byte, the
answer is no. So rather than restating the expectations, this imports them
from test_i20_wire.py where possible and asserts equality directly.

Run: python3 experiments/skeleton_i20/test_i20_cs_wire.py
"""

import os
import re
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import vendor_inputs                  # noqa: E402
# Every check here builds the driver from Extron's donor and compares it
# with Crestron's own driver; the repository publishes neither
# (vendor-files.manifest.tsv), so without them the suite is skipped, visibly.
vendor_inputs.skip_suite(
    os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp", "1bynd_19_4743_v1_0_1.pkp"),
    os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "Controlscript",
                 "onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py"),
    os.path.join(_ROOT, "samples", "Crestron 1 Beyond IV-CAM-i12_i20", "Crestron",
                 "Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg"),
)

import build_i20                       # noqa: E402
import build_i20_cs                    # noqa: E402
import pkp_build as pb                 # noqa: E402
import test_i20_wire as pkp_tests      # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "\n         " + detail))
    return cond


# ---------------------------------------------------------------------------
# extronlib stand-in. ControlScript modules inherit from the real interface
# classes; here they inherit from recorders.
# ---------------------------------------------------------------------------
class _Recorder(object):
    def __init__(self, *a, **k):
        self.sent = []
        self.errors = []
        self.discards = []
        self._canned = b""

    def Send(self, data):
        self.sent.append(bytes(data))

    def SendAndWait(self, data, timeout, deliTag=None):
        self.sent.append(bytes(data))
        return self._canned

    def Disconnect(self):
        pass


class StubSerialInterface(_Recorder):
    def __init__(self, Host=None, Port=None, *a, **k):
        _Recorder.__init__(self)
        self.Host = types.SimpleNamespace(DeviceAlias="stub")
        self.Port = Port


class StubEthernetClientInterface(_Recorder):
    def __init__(self, Hostname=None, IPPort=None, Protocol=None, ServicePort=0):
        _Recorder.__init__(self)
        self.Hostname = Hostname
        self.IPPort = IPPort
        self.Protocol = Protocol


def load_module(source):
    """Execute the derived ControlScript module against a stub extronlib."""
    extronlib = types.ModuleType("extronlib")
    interface = types.ModuleType("extronlib.interface")
    interface.SerialInterface = StubSerialInterface
    interface.EthernetClientInterface = StubEthernetClientInterface
    extronlib.interface = interface
    sys.modules["extronlib"] = extronlib
    sys.modules["extronlib.interface"] = interface

    mod = types.ModuleType("derived_i20_cs")
    exec(compile(source, "<derived_i20_cs>", "exec"), mod.__dict__)
    return mod


def build():
    with open(build_i20_cs.DONOR_CS, encoding="utf-8") as fh:
        return build_i20_cs.derive(fh.read())


SOURCE = build()
MOD = load_module(SOURCE)


def make(unidirectional="True"):
    d = MOD.EthernetClass("10.0.0.1", 5500)
    d.Unidirectional = unidirectional
    return d


def hexs(b):
    return " ".join("%02X" % x for x in b)


def drive(d, method, *args):
    d.sent = []
    getattr(d, method)(*args)
    return d.sent[0] if len(d.sent) == 1 else None


# ---------------------------------------------------------------------------

def test_module_loads():
    print("\n[1] the module imports and all three transport classes construct")
    check("module parses and executes", MOD is not None)
    for name in ("DeviceClass", "SerialClass", "SerialOverEthernetClass",
                 "EthernetClass"):
        check("%s present" % name, hasattr(MOD, name))
    d = MOD.EthernetClass("10.0.0.1", 5500)
    check("EthernetClass instantiates", d is not None)
    check("DeviceID defaults to VISCA header 0x81", d.DeviceID == 0x81,
          hex(d.DeviceID))
    check("SerialClass instantiates", MOD.SerialClass(None, None) is not None)
    check("SerialOverEthernetClass instantiates",
          MOD.SerialOverEthernetClass("10.0.0.1", 5500) is not None)


def test_transport_default_is_tcp():
    print("\n[2] C2: EthernetClass defaults to TCP, not UDP")
    d = MOD.EthernetClass("10.0.0.1", 5500)
    check("default Protocol is TCP", d.Protocol == "TCP", repr(d.Protocol))
    d2 = MOD.EthernetClass("10.0.0.1", 5500, "UDP")
    check("an explicit Protocol still wins", d2.Protocol == "UDP", repr(d2.Protocol))


def test_same_bytes_as_the_pkp_driver():
    print("\n[3] EVERY command emits the same bytes as the .pkp driver")
    # The point of the whole exercise: two emitters, one wire table. Byte
    # expectations are not restated here - they are taken from the .pkp
    # driver's own output, so the two can never silently drift apart.
    builder = pb.PackageBuilder(build_i20.DONOR)
    slot = builder.scripts()[0]
    pkp_cls = pkp_tests.load_driver_class(build_i20.derive(slot.source),
                                          os.path.splitext(slot.key)[0])
    cfg = dict(pkp_tests.CONFIGS)
    pkp = pkp_cls(cfg)
    pkp.WritePower("On", None, "Live")

    cs = make()

    cases = [
        # (command, args)                                  both drivers get these
        ("TrackingFraming",      ("Start", None)),
        ("TrackingFraming",      ("Stop", None)),
        ("TrackingMode",         ("Group", None)),
        ("TrackingMode",         ("Presenter", None)),
        ("Menu",                 ("Toggle", None)),
        ("Reboot",               ("Reboot", None)),
        ("Identify",             ("Identify", None)),
        ("FreezeFrame",          ("On", None)),
        ("FreezeFrame",          ("Off", None)),
        ("PanTiltHome",          ("Reset", None)),
        ("TrackingShot",         ("Home", None)),
        ("TrackingShot",         ("Tracking", None)),
        ("TrackingProfile",      (2, None)),
        ("PresetZone",           (3, None)),
        ("CameraOutput",         (2, None)),
        ("IntelligentSwitching", ("Pause", None)),
        ("IntelligentSwitching", ("Resume", None)),
        ("ZoomPosition",         (0x1A2B, {"Speed": 3})),
        ("Zoom",                 ("Tele", {"Speed": 5})),
        ("Power",                ("On", None)),
        ("Preset",               (3, {"Action": "Recall"})),
        # v1.6 parity commands
        ("ExposureCompensationMode", ("On", None)),
        ("ExposureCompensationMode", ("Off", None)),
        ("ExposureCompensation", (0, None)),
        ("ExposureCompensation", (14, None)),
        ("FocusPosition",        (12224, None)),
        ("FocusPosition",        (20664, None)),
        ("OnePushAutoFocus",     ("Trigger", None)),
        ("AutoFocusBehavior",    ("Global", None)),
        ("AutoFocusBehavior",    ("Center", None)),
        ("AutoFocusBehavior",    ("Face", None)),
        ("AutoFocusSensitivity", (1, None)),
        ("AutoFocusSensitivity", (3, None)),
        ("AutoPrivacyMode",      ("On", None)),
        ("AutoPrivacyMode",      ("Off", None)),
        ("AutoSoftwareUpdate",   ("On", None)),
        ("AutoSoftwareUpdate",   ("Off", None)),
    ]
    for command, args in cases:
        a = drive(pkp, "_cmd_Set%s" % command, *args)
        b = drive(cs, "Set%s" % command, *args)
        label = "Set%s(%s)" % (command, args[0])
        check("%-34s %s" % (label, hexs(b) if b else "<nothing sent>"),
              a is not None and b is not None and a == b,
              "pkp=%s  cs=%s" % (hexs(a) if a else "<none>",
                                 hexs(b) if b else "<none>"))

    # PanTiltAngle carries every parameter in the qualifier (see findings/18
    # s8): GC routes non-Value parameters that way, and the ControlScript form
    # mirrors it so the two emitters cannot drift.
    args = (None,
            {"Pan Speed": 0x18, "Tilt Speed": 0x14,
             "Pan": 0x0123, "Tilt": 0x0456})
    a = drive(pkp, "_cmd_SetPanTiltAngle", *args)
    b = drive(cs, "SetPanTiltAngle", *args)
    check("SetPanTiltAngle                    %s" % (hexs(b) if b else "<none>"),
          a is not None and a == b,
          "pkp=%s  cs=%s" % (hexs(a) if a else "<none>", hexs(b) if b else "<none>"))

    # Lightbar: all 19 documented combinations, both drivers.
    mismatches = []
    for width in ("None", "Half", "Full"):
        for colour in ("Green", "Red", "Yellow"):
            for brightness in ("Dim", "Medium", "Bright"):
                q = {"Color": colour, "Brightness": brightness}
                a = drive(pkp, "_cmd_SetIndicatorLight", width, q)
                b = drive(cs, "SetIndicatorLight", width, q)
                if a != b:
                    mismatches.append("%s/%s/%s" % (width, colour, brightness))
    check("all 27 lightbar combinations agree between the two emitters",
          not mismatches, "differ: %s" % mismatches[:5])


def test_inquiries_match():
    print("\n[4] UPDATE requests match the .pkp driver too")
    builder = pb.PackageBuilder(build_i20.DONOR)
    slot = builder.scripts()[0]
    pkp_cls = pkp_tests.load_driver_class(build_i20.derive(slot.source),
                                          os.path.splitext(slot.key)[0])
    cfg = dict(pkp_tests.CONFIGS)
    cfg["Unidirectional"] = "False"
    pkp = pkp_cls(cfg)
    pkp.WritePower("On", None, "Live")
    pkp._canned = b""

    cs = make(unidirectional="False")
    cs._canned = b""

    for command, qual in (("TrackingFraming", None),
                          ("ZoomPosition", {"Speed": 0}),
                          ("PanAngleStatus", {}),
                          ("TiltAngleStatus", {}),
                          ("FreezeFrame", None),
                          ("CameraOutput", None),
                          # v1.6
                          ("TrackingMode", None),
                          ("TrackingProfile", None),
                          ("IntelligentSwitching", None),
                          ("ExposureCompensationMode", None),
                          ("ExposureCompensation", None),
                          ("FocusPosition", None),
                          ("AutoFocusBehavior", None),
                          ("AutoFocusSensitivity", None),
                          ("AutoPrivacyMode", None),
                          ("AutoSoftwareUpdate", None),
                          ("DeviceModel", None),
                          ("RomVersion", None),
                          ("PanSpeedMaxStatus", None),
                          ("TiltSpeedMaxStatus", None)):
        pkp.sent = []
        getattr(pkp, "_cmd_Update%s" % command)(None, qual)
        cs.sent = []
        getattr(cs, "Update%s" % command)(None, qual)
        a = pkp.sent[0] if pkp.sent else None
        b = cs.sent[0] if cs.sent else None
        check("Update%-22s %s" % (command, hexs(b) if b else "<nothing sent>"),
              a is not None and a == b,
              "pkp=%s  cs=%s" % (hexs(a) if a else "<none>",
                                 hexs(b) if b else "<none>"))


def test_public_dispatch():
    print("\n[5] the public Set/Update/ReadStatus surface works end to end")
    # This is what a project actually calls - not the Set<Command> methods.
    d = make()
    d.sent = []
    d.Set("TrackingFraming", "Start")
    check("Set('TrackingFraming', 'Start') -> 81 01 04 3F 02 50 FF",
          d.sent and hexs(d.sent[0]) == "81 01 04 3F 02 50 FF",
          "got %s" % (hexs(d.sent[0]) if d.sent else "<nothing sent>"))
    check("status now reads Start",
          d.ReadStatus("TrackingFraming") == "Start",
          repr(d.ReadStatus("TrackingFraming")))

    d.sent = []
    d.Set("IndicatorLight", "Half", {"Color": "Red", "Brightness": "Dim"})
    check("Set('IndicatorLight', 'Half', red/dim) -> 81 C1 01 05 05 01 FF",
          d.sent and hexs(d.sent[0]) == "81 C1 01 05 05 01 FF",
          "got %s" % (hexs(d.sent[0]) if d.sent else "<nothing sent>"))

    # Update through the public entry point, with a canned documented reply.
    du = make(unidirectional="False")
    du._canned = b"\x90\x50\x03\xFF"
    du.Update("TrackingFraming")
    check("Update('TrackingFraming') with 90 50 03 FF -> Stop",
          du.ReadStatus("TrackingFraming") == "Stop",
          repr(du.ReadStatus("TrackingFraming")))

    # An unknown command must raise, not pass silently. Extron's dispatch
    # raises AttributeError for an unsupported Set and KeyError for an unknown
    # ReadStatus - asserting the actual contract, not a tidier one.
    try:
        d.Set("NoSuchCommand", "x")
        ok = False
    except AttributeError:
        ok = True
    check("Set() on an unknown command raises AttributeError", ok)
    try:
        d.ReadStatus("NoSuchCommand")
        ok = False
    except KeyError:
        ok = True
    check("ReadStatus() on an unknown command raises KeyError", ok)


def test_subscribe_status():
    print("\n[6] SubscribeStatus delivers tracking-state changes to a callback")
    d = make(unidirectional="False")
    seen = []
    d.SubscribeStatus("TrackingFraming", None,
                      lambda cmd, val, q: seen.append(val))
    d._canned = b"\x90\x50\x02\xFF"
    d.Update("TrackingFraming")
    check("callback fired with 'Start'", seen == ["Start"], repr(seen))
    d._canned = b"\x90\x50\x03\xFF"
    d.Update("TrackingFraming")
    check("callback fired with 'Stop' on change", seen == ["Start", "Stop"],
          repr(seen))
    # NewStatus only fires on change - repeating the same reply must not re-fire.
    d.Update("TrackingFraming")
    check("no duplicate callback when the state is unchanged",
          seen == ["Start", "Stop"], repr(seen))


def test_undocumented_reply_is_an_error():
    print("\n[7] an undefined reply payload errors rather than being guessed")
    # Unlike the .pkp form, a ControlScript module's Error() *prints* - each
    # transport class overrides it to write host/port context to the console.
    # So the error has to be captured from stdout, not from a list.
    import contextlib
    import io

    d = make(unidirectional="False")
    d._canned = b"\x90\x50\x07\xFF"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        d.Update("TrackingFraming")
    out = buf.getvalue()
    check("payload 0x07 reports an error",
          "Invalid/unexpected response" in out, repr(out))
    check("and leaves status unset", d.ReadStatus("TrackingFraming") is None,
          repr(d.ReadStatus("TrackingFraming")))

    # A documented payload must NOT print an error.
    d2 = make(unidirectional="False")
    d2._canned = b"\x90\x50\x02\xFF"
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        d2.Update("TrackingFraming")
    check("a documented payload is silent and sets status",
          buf2.getvalue() == "" and d2.ReadStatus("TrackingFraming") == "Start",
          "printed %r, status %r" % (buf2.getvalue(),
                                     d2.ReadStatus("TrackingFraming")))


def test_position_and_output_feedback():
    print("\n[10] position and camera-output replies read back as sent")
    # Pan/tilt are read the way SetPanTiltAngle writes them (pan & 0xFFFF), so a
    # negative angle must come back negative, not as 63088.
    for reply, pan, tilt in ((b"\x90\x50\x0F\x06\x07\x00\x0F\x0A\x0F\x00\xFF", -2448, -1296),
                             (b"\x90\x50\x00\x09\x09\x00\x00\x05\x01\x00\xFF", 2448, 1296)):
        d = make(unidirectional="False")
        d._canned = reply
        d.Update("PanAngleStatus")
        d.Update("TiltAngleStatus")
        got = (d.ReadStatus("PanAngleStatus"), d.ReadStatus("TiltAngleStatus"))
        check("%s -> pan %d, tilt %d" % (hexs(reply), pan, tilt), got == (pan, tilt),
              "got %r" % (got,))

    # Get Output, VISCA-Intelligent-Switching-Commands.md: y0 50 0S 0Z FF,
    # S = switching on/off, Z = camera.
    for reply, camera in ((b"\x90\x50\x01\x03\xFF", 3), (b"\x90\x50\x00\x05\xFF", 5)):
        d = make(unidirectional="False")
        d._canned = reply
        d.Update("CameraOutput")
        got = d.ReadStatus("CameraOutput")
        check("%s -> camera %d, not the switching flag" % (hexs(reply), camera),
              got == camera, "got %r" % (got,))


def test_v16_statuses_match():
    print("\n[11] v1.6 statuses read back the same in both emitters")
    # One reply per case, fed to both drivers; every status the reply carries
    # must come out equal and set. The .pkp side is test_i20_wire.py [15]'s
    # subject, so agreement here is agreement with Crestron's reply rules.
    builder = pb.PackageBuilder(build_i20.DONOR)
    slot = builder.scripts()[0]
    pkp_cls = pkp_tests.load_driver_class(build_i20.derive(slot.source),
                                          os.path.splitext(slot.key)[0])
    cases = [
        ("TrackingMode", b"\x90\x50\x00\x01\xFF", ["TrackingMode"]),
        ("TrackingProfile", b"\x90\x50\x06\x0B\xFF", ["TrackingProfile"]),
        ("ExposureCompensationMode", b"\x90\x50\x02\xFF", ["ExposureCompensationMode"]),
        ("ExposureCompensation", b"\x90\x50\x00\x00\x00\x0B\xFF", ["ExposureCompensation"]),
        ("FocusPosition", b"\x90\x50\x04\x01\x02\x03\xFF", ["FocusPosition"]),
        ("AutoFocusBehavior", b"\x90\x50\x00\x01\xFF", ["AutoFocusBehavior"]),
        ("AutoFocusSensitivity", b"\x90\x50\x00\x03\xFF", ["AutoFocusSensitivity"]),
        ("AutoPrivacyMode", b"\x90\x50\x00\x00\xFF", ["AutoPrivacyMode"]),
        ("AutoSoftwareUpdate", b"\x90\x50\x00\x01\xFF", ["AutoSoftwareUpdate"]),
        ("IntelligentSwitching", b"\x90\x50\x01\x04\xFF",
         ["IntelligentSwitching", "CameraOutput"]),
        ("DeviceModel", b"\x90\x50\x00\x01\x05\x06\xAB\xCD\x01\xFF",
         ["DeviceModel", "RomVersion"]),
        ("PanSpeedMaxStatus", b"\x90\x50\x18\x14\xFF",
         ["PanSpeedMaxStatus", "TiltSpeedMaxStatus"]),
    ]
    for command, reply, statuses in cases:
        cfg = dict(pkp_tests.CONFIGS)
        cfg["Unidirectional"] = "False"
        pkp = pkp_cls(cfg)
        pkp.WritePower("On", None, "Live")
        pkp._canned = reply
        getattr(pkp, "_cmd_Update%s" % command)(None, None)
        a = [pkp.ReadStatusHelper(s, None, "Live") for s in statuses]

        cs = make(unidirectional="False")
        cs._canned = reply
        cs.Update(command)
        b = [cs.ReadStatus(s) for s in statuses]
        check("%-22s %s -> %s" % (command, hexs(reply), b),
              a == b and None not in b, "pkp=%r  cs=%r" % (a, b))


def test_python35_compatible():
    print("\n[8] the module targets Python 3.5 (non-xi processors)")
    check("no f-strings", not re.search(r"""\bf['"]""", SOURCE))
    check("no walrus operator", ":=" not in SOURCE)
    check("compiles", _compiles(SOURCE))
    # time is [PATCH C6], for the rate-limited pan/tilt query. The .pkp driver
    # already imports it; this list is the standard library a processor has, so
    # the point of the check is that nothing NEW is needed to run the module.
    check("imports only extronlib, re, struct and time",
          set(re.findall(r"^(?:from|import) +([A-Za-z_][\w.]*)", SOURCE, re.M))
          <= {"extronlib.interface", "re", "struct", "time"},
          repr(set(re.findall(r"^(?:from|import) +([A-Za-z_][\w.]*)",
                              SOURCE, re.M))))


def _compiles(src):
    try:
        compile(src, "<derived>", "exec")
        return True
    except SyntaxError:
        return False


def test_emitted_file_is_current():
    print("\n[9] the file in out/ matches what the builder produces now")
    out = os.path.join(_HERE, "out", "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")
    if not os.path.exists(out):
        check("module emitted", False, "run build_i20_cs.py first")
        return
    with open(out, encoding="utf-8") as fh:
        on_disk = fh.read()
    check("out/ is up to date with the builder", on_disk == SOURCE,
          "regenerate with build_i20_cs.py")


def main():
    print("test_i20_cs_wire.py - wire oracle for the ControlScript i20 module")
    for fn in (test_module_loads,
               test_transport_default_is_tcp,
               test_same_bytes_as_the_pkp_driver,
               test_inquiries_match,
               test_public_dispatch,
               test_subscribe_status,
               test_undocumented_reply_is_an_error,
               test_position_and_output_feedback,
               test_v16_statuses_match,
               test_python35_compatible,
               test_emitted_file_is_current):
        fn()
    print("\n%d passed, %d failed, %d total"
          % (len(PASS), len(FAIL), len(PASS) + len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
