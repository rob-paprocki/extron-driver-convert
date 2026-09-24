#!/usr/bin/env python3
"""
test_visca_listener.py - the loopback listener, checked without a processor.

  [1] every PROTOCOL T3 wire string decodes to the command it is for
  [2] every frame the i20 ControlScript module can send decodes, with nothing
      UNKNOWN and no unexpected byte - so if a processor capture shows either,
      the processor sent something the module does not
  [3] framing survives arbitrary TCP chunking
  [4] the camera model answers in the documented reply layouts
  [5] end to end over a real TCP socket: the module, driven through
      controlscript/loopback_steps.py by a socket stand-in for extronlib,
      against the listener - what a processor run does, minus Extron's runtime
  [6] README Path B's GC macro: every wire string is what the module sends
  [7] the 20028 / v1.6 additions: new commands decode, new inquiries answer
      as documented, and a Set round-trips through its matching inquiry

Run: python3 experiments/loopback/test_visca_listener.py
"""

import contextlib
import importlib.util
import io
import os
import socket
import sys
import tempfile
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(_HERE, "controlscript"))

import visca_listener as vl           # noqa: E402
import loopback_steps                 # noqa: E402

MODULE = os.path.join(_ROOT, "experiments", "skeleton_i20", "out",
                      "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "\n         " + detail))
    return cond


# ---------------------------------------------------------------------------
# extronlib stand-ins
# ---------------------------------------------------------------------------
class RecordingInterface(object):
    """Records what the module sends; every reply is empty."""

    def __init__(self, Hostname=None, IPPort=None, *args, **kwargs):
        self.Hostname, self.IPPort = Hostname, IPPort
        self.sent = []

    def Send(self, data):
        self.sent.append(bytes(data))

    def SendAndWait(self, data, timeout, **kwargs):
        self.sent.append(bytes(data))
        return b""

    def Connect(self, timeout=None):
        return "Connected"

    def Disconnect(self):
        pass


class SocketInterface(object):
    """What a processor's EthernetClientInterface does with the module's calls,
    over a real TCP socket. SendAndWait reads to the delimiter or the timeout
    and does not discard data already waiting; whether Extron's runtime does is
    one of the things a processor run measures."""

    def __init__(self, Hostname=None, IPPort=None, *args, **kwargs):
        self.Hostname, self.IPPort, self.sock = Hostname, IPPort, None

    def Connect(self, timeout=None):
        self.sock = socket.create_connection((self.Hostname, self.IPPort), timeout or 5)
        return "Connected"

    def Disconnect(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def Send(self, data):
        self.sock.sendall(bytes(data))

    def SendAndWait(self, data, timeout, deliTag=None, **kwargs):
        self.sock.sendall(bytes(data))
        self.sock.settimeout(timeout)
        got = b""
        try:
            while not (deliTag and got.endswith(deliTag)):
                chunk = self.sock.recv(1)
                if not chunk:
                    break
                got += chunk
        except socket.timeout:
            pass
        return got


_loads = [0]


def load_module(interface):
    pkg = types.ModuleType("extronlib")
    iface = types.ModuleType("extronlib.interface")
    setattr(iface, "SerialInterface", interface)
    setattr(iface, "EthernetClientInterface", interface)
    setattr(pkg, "interface", iface)
    sys.modules["extronlib"] = pkg
    sys.modules["extronlib.interface"] = iface
    _loads[0] += 1
    spec = importlib.util.spec_from_file_location("i20_module_%d" % _loads[0], MODULE)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def quiet(fn, *args):
    """The module prints its Error/Discard lines; keep them out of the report."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args)


def run_steps(cam, steps):
    """What main.py does per step, without extronlib's Timer."""
    for kind, command, value, qualifier, _note in steps:
        if kind == "Set":
            quiet(cam.Set, command, value, qualifier)
        else:
            quiet(cam.Update, command, qualifier)


# ---------------------------------------------------------------------------
# [1]
# ---------------------------------------------------------------------------
EXPECTED_DECODE = {
    "81 01 04 00 02 FF": ("command", "Power", "On"),
    "81 01 04 3F 02 01 FF": ("command", "Preset", "Recall 1 = TrackingShot Tracking"),
    "81 01 04 07 25 FF": ("command", "Zoom", "Tele speed 5"),
    "81 01 04 3F 02 50 FF": ("command", "Preset", "Recall 80 = TrackingFraming Start"),
    "81 09 08 01 FF": ("inquiry", "TrackingFraming", ""),
    "81 01 04 3F 02 51 FF": ("command", "Preset", "Recall 81 = TrackingFraming Stop"),
    "81 01 04 47 03 01 0A 02 0B FF": ("command", "ZoomPosition", "6699 speed 3"),
    "81 01 04 62 02 FF": ("command", "FreezeFrame", "On"),
    "81 01 04 62 03 FF": ("command", "FreezeFrame", "Off"),
    "81 C1 0D 0D 0D 0D FF": ("command", "IndicatorLight", "Full Red Bright (segments 0D 0D 0D 0D)"),
    "81 C1 00 04 04 00 FF": ("command", "IndicatorLight", "Half Green Dim (segments 00 04 04 00)"),
    "81 C1 00 00 00 00 FF": ("command", "IndicatorLight", "None (segments 00 00 00 00)"),
    "81 01 04 3F 02 6A FF": ("command", "Preset", "Recall 106 = TrackingProfile 2"),
    "81 C2 01 08 02 FF": ("command", "CameraOutput", "2"),
    "81 C2 01 08 00 FF": ("command", "CameraOutput", "0 = IntelligentSwitching Resume"),
    "81 C2 01 0B 00 FF": ("command", "IntelligentSwitching", "Pause"),
    "81 01 04 3F 02 52 FF": ("command", "Preset", "Recall 82 = TrackingMode Group"),
    "81 01 04 3F 02 53 FF": ("command", "Preset",
                             "Recall 83 = TrackingMode Presenter (docs: Pause Group Tracking)"),
}


def part1():
    print("\n[1] every PROTOCOL T3 wire string decodes to its command")
    for step, label, want in vl.EXPECTED_T3:
        d = vl.decode(bytes.fromhex(want))
        check("%-6s %-32s -> %s %s" % (step, label, d.name, d.detail),
              tuple(d) == EXPECTED_DECODE[want], "got %r" % (tuple(d),))
    check("the table covers every T3 string",
          set(h for _, _, h in vl.EXPECTED_T3) == set(EXPECTED_DECODE))


# ---------------------------------------------------------------------------
# [2]
# ---------------------------------------------------------------------------
def every_call():
    calls = []

    def S(command, value, qualifier=None):
        calls.append(("Set", command, value, qualifier))

    for command in ("Power", "AutoFocus", "Backlight", "FreezeFrame"):
        for value in ("On", "Off"):
            S(command, value)
    for value in ("Full Auto", "Manual", "Shutter Priority", "Iris Priority", "Bright"):
        S("AutoExposure", value)
    for value in ("Auto", "Indoor", "Outdoor", "One Push", "Manual", "One Push Trigger"):
        S("WhiteBalance", value)
    for command in ("Iris", "Gain", "Shutter"):
        for value in ("Up", "Down", "Reset"):
            S(command, value)
    for command, values in (("Zoom", ("Tele", "Wide", "Stop")), ("Focus", ("Far", "Near", "Stop"))):
        for value in values:
            for speed in (0, 7):
                S(command, value, {"Speed": speed})
    for value in ("Up", "Down", "Left", "Right", "Up Left", "Up Right",
                  "Down Left", "Down Right", "Stop", "Home", "Reset"):
        S("PanTilt", value, {"Pan Speed": 1, "Tilt Speed": 1})
        S("PanTilt", value, {"Pan Speed": 24, "Tilt Speed": 20})
    for action in ("Reset", "Save", "Recall"):
        for preset in (0, 1, 128, 254):
            S("Preset", preset, {"Action": action})
    for command, values in (("TrackingFraming", ("Start", "Stop")),
                            ("TrackingMode", ("Group",)),
                            ("TrackingMode", ("Presenter",)),
                            ("TrackingShot", ("Home", "Tracking")),
                            ("IntelligentSwitching", ("Resume", "Pause"))):
        for value in values:
            S(command, value)
    for n in range(1, 5):
        S("TrackingProfile", n)
        S("PresetZone", n)
    # 1..5: CameraOutput 0 was dropped in 20027 because it is byte-for-byte
    # IntelligentSwitching Resume, which is driven just above.
    for n in range(1, 6):
        S("CameraOutput", n)
    for zoom, speed in ((0, 0), (6699, 3), (16384, 7)):
        S("ZoomPosition", zoom, {"Speed": speed})
    # 20028 / v1.6 additions (CRESTRON_PARITY.md Task A).
    for value in ("On", "Off"):
        S("ExposureCompensationMode", value)
    for value in (0, 7, 14):
        S("ExposureCompensation", value)
    for value in (12224, 16444, 20664):
        S("FocusPosition", value)
    S("OnePushAutoFocus", "Trigger")
    for value in ("Global", "Center", "Face"):
        S("AutoFocusBehavior", value)
    for value in (1, 2, 3):
        S("AutoFocusSensitivity", value)
    for value in ("On", "Off"):
        S("AutoPrivacyMode", value)
    for value in ("On", "Off"):
        S("AutoSoftwareUpdate", value)
    for pan, tilt in ((-2448, -1296), (0, 0), (2448, 1296)):
        S("PanTiltAngle", None, {"Pan Speed": 1, "Tilt Speed": 20, "Pan": pan, "Tilt": tilt})
    for command in ("PanTiltHome", "Menu", "Identify", "Reboot"):
        S(command, None)
    for width in ("None", "Half", "Full"):
        for colour in ("Green", "Red", "Yellow"):
            for brightness in ("Off", "Dim", "Medium", "Bright"):
                S("IndicatorLight", width, {"Color": colour, "Brightness": brightness})
    for command in ("Power", "AutoExposure", "AutoFocus", "Backlight", "WhiteBalance",
                    "ZoomPosition", "PanAngleStatus", "TiltAngleStatus", "FreezeFrame",
                    "CameraOutput", "TrackingFraming",
                    # 20028 / v1.6: live from this build.
                    "TrackingMode", "TrackingProfile", "ExposureCompensationMode",
                    "ExposureCompensation", "FocusPosition", "AutoFocusBehavior",
                    "AutoFocusSensitivity", "AutoPrivacyMode", "AutoSoftwareUpdate",
                    "DeviceModel", "RomVersion", "PanSpeedMaxStatus", "TiltSpeedMaxStatus"):
        calls.append(("Update", command, None, None))
    for n in (2, 3, 4, 5):
        calls.append(("Update", "CameraConnectionStatus", None, {"Camera": n}))
    return calls


# Commands whose wire inquiry is shared with another status - the inquiry's
# decoded name is not the command name, so a substring check needs the alias.
ALIASES = {"PanAngleStatus": "PanTiltPosition", "TiltAngleStatus": "PanTiltPosition",
          "DeviceModel": "DeviceInformation", "RomVersion": "DeviceInformation",
          "PanSpeedMaxStatus": "PanTiltSpeedMax", "TiltSpeedMaxStatus": "PanTiltSpeedMax"}


def part2(mod):
    print("\n[2] every frame the module can send decodes, nothing unknown")
    calls = every_call() + [step[:4] for step in loopback_steps.SEQUENCE]
    bad, total = [], 0
    for kind, command, value, qualifier in calls:
        cam = mod.EthernetClass("192.0.2.1", 5500)
        if kind == "Set":
            quiet(cam.Set, command, value, qualifier)
        else:
            quiet(cam.Update, command, qualifier)
        if not cam.sent:
            bad.append("%s %s %r %r sent nothing" % (kind, command, value, qualifier))
        for frame in cam.sent:
            total += 1
            d = vl.decode(frame)
            label = d.name + " " + d.detail
            if (d.kind not in ("command", "inquiry") or "?" in d.detail
                    or ALIASES.get(command, command) not in label
                    or (kind == "Update") != (d.kind == "inquiry")):
                bad.append("%s %s %r %r -> %s -> %r" % (kind, command, value, qualifier,
                                                        vl.hexs(frame), tuple(d)))
    check("%d frames from %d calls decode to the command that sent them" % (total, len(calls)),
          not bad, "\n         ".join(bad[:10]))

    cam = mod.EthernetClass("192.0.2.1", 5500)
    quiet(cam.Set, "Preset", 255, {"Action": "Recall"})
    frames = vl.Framer().feed(cam.sent[0]) if cam.sent else []
    check("Preset 255 is not frameable: its value is the FF terminator (%s)"
          % " | ".join(vl.hexs(f) for f in frames),
          len(frames) == 2 and all(vl.decode(f).kind == "unknown" for f in frames))


# ---------------------------------------------------------------------------
# [3]
# ---------------------------------------------------------------------------
def part3():
    print("\n[3] framing survives TCP chunking")
    stream = bytes.fromhex("81 01 04 00 02 FF 81 09 08 01 FF 81 C1 00 04 04 00 FF")
    want = ["81 01 04 00 02 FF", "81 09 08 01 FF", "81 C1 00 04 04 00 FF"]
    for size in (1, 2, 5, len(stream)):
        framer, frames = vl.Framer(), []
        for i in range(0, len(stream), size):
            frames += framer.feed(stream[i:i + size])
        check("chunks of %2d bytes -> 3 frames, nothing left over" % size,
              [vl.hexs(f) for f in frames] == want and framer.flush() == b"")
    framer = vl.Framer()
    framer.feed(bytes.fromhex("81 01 04"))
    check("an unterminated tail decodes as PARTIAL", vl.decode(framer.flush()).kind == "partial")


# ---------------------------------------------------------------------------
# [4]
# ---------------------------------------------------------------------------
def part4():
    print("\n[4] the camera model answers in the documented layouts")
    m = vl.CameraModel()

    def R(h, mode="ack"):
        return [vl.hexs(r) for r in m.respond(bytes.fromhex(h), mode)]

    check("mode none answers nothing", R("81 01 04 00 02 FF", "none") == [])
    check("a command in mode ack: 90 41 FF", R("81 01 04 00 03 FF") == ["90 41 FF"])
    check("a command in mode full: 90 41 FF then 90 51 FF",
          R("81 01 04 00 02 FF", "full") == ["90 41 FF", "90 51 FF"])
    check("power follows the last Set: 90 50 02 FF", R("81 09 04 00 FF") == ["90 50 02 FF"])
    R("81 01 04 3F 02 50 FF")
    check("tracking Start -> 90 50 02 FF", R("81 09 08 01 FF") == ["90 50 02 FF"])
    R("81 01 04 3F 02 51 FF")
    check("tracking Stop -> 90 50 03 FF", R("81 09 08 01 FF") == ["90 50 03 FF"])
    R("81 01 04 47 03 01 0A 02 0B FF")
    check("zoom 6699 -> 90 50 01 0A 02 0B FF", R("81 09 04 47 FF") == ["90 50 01 0A 02 0B FF"])
    R("81 01 06 02 01 01 0F 06 07 00 0F 0A 0F 00 FF")
    check("pan -2448 / tilt -1296 -> 90 50 0F 06 07 00 0F 0A 0F 00 FF",
          R("81 09 06 12 FF") == ["90 50 0F 06 07 00 0F 0A 0F 00 FF"])
    R("81 C2 01 08 02 FF")
    check("output 2, switching on -> 90 50 01 02 FF", R("81 C2 09 08 FF") == ["90 50 01 02 FF"])
    R("81 C2 01 0B 00 FF")
    check("switching paused -> 90 50 00 02 FF", R("81 C2 09 08 FF") == ["90 50 00 02 FF"])
    check("camera 3 connected -> 90 50 00 01 FF", R("81 C2 09 0D 03 FF") == ["90 50 00 01 FF"])
    m.control("camera 3 disconnected")
    check("camera 3 disconnected -> 90 50 00 00 FF", R("81 C2 09 0D 03 FF") == ["90 50 00 00 FF"])
    check("an unknown frame gets a syntax error: 90 60 02 FF", R("81 01 7E 01 FF") == ["90 60 02 FF"])
    check("a console change is what the next poll reports",
          m.control("tracking start").startswith("camera state")
          and R("81 09 08 01 FF") == ["90 50 02 FF"])
    check("nonsense at the console is refused",
          m.control("tracking sideways").startswith("could not parse"))
    m.control("pan 1000")
    m.control("tilt -500")
    check("pan and tilt can be set from the console, like zoom and output",
          R("81 09 06 12 FF") == ["90 50 00 03 0E 08 0F 0E 00 0C FF"])


# ---------------------------------------------------------------------------
# [5]
# ---------------------------------------------------------------------------
def part5():
    print("\n[5] end to end over TCP: module -> socket -> listener -> module")
    capture = vl.Capture(os.path.join(tempfile.mkdtemp(), "e2e.tsv"), echo=False)
    listener = vl.Listener("127.0.0.1", 0, "ack", capture)
    host, port = listener.start()
    cam = load_module(SocketInterface).EthernetClass(host, port)
    try:
        check("the module connects to the listener", quiet(cam.Connect, 5) == "Connected")

        run_steps(cam, loopback_steps.T3)
        text, result = vl.summarize(vl.read_capture(capture.path))
        check("every T3 wire string reached the listener, in PROTOCOL order",
              result["seen_all"] and result["in_order"], text)
        check("nothing unknown or unexpected in the capture", result["odd"] == 0, text)

        listener.model.control("tracking start")
        quiet(cam.Update, "TrackingFraming")
        check("after Set Stop, a camera-side Start is what the poll reports",
              cam.ReadStatus("TrackingFraming") == "Start",
              "got %r" % cam.ReadStatus("TrackingFraming"))

        quiet(cam.Set, "ZoomPosition", 16384, {"Speed": 7})
        quiet(cam.Update, "ZoomPosition")
        check("ZoomPosition reads back 16384", cam.ReadStatus("ZoomPosition") == 16384,
              "got %r" % cam.ReadStatus("ZoomPosition"))

        quiet(cam.Set, "PanTiltAngle", None,
              {"Pan Speed": 1, "Tilt Speed": 1, "Pan": -2448, "Tilt": -1296})
        quiet(cam.Update, "PanAngleStatus")
        quiet(cam.Update, "TiltAngleStatus")
        pan, tilt = cam.ReadStatus("PanAngleStatus"), cam.ReadStatus("TiltAngleStatus")
        check("pan / tilt read back signed: -2448 / -1296 (got %r / %r)" % (pan, tilt),
              (pan, tilt) == (-2448, -1296))

        quiet(cam.Set, "CameraOutput", 5)
        listener.model.control("switching off")
        quiet(cam.Update, "CameraOutput")
        out = cam.ReadStatus("CameraOutput")
        check("CameraOutput reads the camera from 'y0 50 0S 0Z FF': 5 (got %r)" % out, out == 5)

        run_steps(cam, loopback_steps.EDGES + loopback_steps.POLLS)
        text, result = vl.summarize(vl.read_capture(capture.path))
        check("the whole main.py sequence decodes cleanly (%d frames)" % result["received"],
              result["odd"] == 0, text)
    finally:
        cam.Disconnect()
        listener.stop()
        capture.close()


def part6(mod):
    print("\n[6] README Path B's GC macro: every wire string is what the module sends")
    macro = loopback_steps.GC_MACRO
    check("the macro table and its expectation list line up (%d steps)" % len(macro),
          len(macro) == len(vl.EXPECTED_GC_MACRO))
    for (gc_command, gc_params, kind, command, value, qualifier), (step, label, want) in zip(
            macro, vl.EXPECTED_GC_MACRO):
        cam = mod.EthernetClass("192.0.2.1", 5500)
        quiet(cam.Set, command, value, qualifier)
        got = " | ".join(vl.hexs(f) for f in cam.sent)
        check("%-6s %-22s %-48s -> %s" % (step, gc_command, gc_params, want), got == want,
              "the module sends %s" % (got or "nothing"))
    rows = []
    for _, _, h in vl.EXPECTED_GC_MACRO:
        d = vl.decode(bytes.fromhex(h))
        rows.append({"time": "", "dir": "rx", "hex": h, "kind": d.kind, "name": d.name,
                     "detail": d.detail})
    text, result = vl.summarize(rows, expect="gc-macro")
    check("a capture of the macro, in order, passes --expect gc-macro",
          result["seen_all"] and result["in_order"] and result["odd"] == 0, text)


# ---------------------------------------------------------------------------
# [7]
# ---------------------------------------------------------------------------
# Every new 20028 / v1.6 command and inquiry decodes to the name and detail
# CRESTRON_PARITY.md's Task A / build_i20.py's [PATCH E7] say it should.
NEW_DECODE = {
    "81 01 04 3E 02 FF": ("command", "ExposureCompensationMode", "On"),
    "81 01 04 3E 03 FF": ("command", "ExposureCompensationMode", "Off"),
    "81 01 04 4E 00 00 00 0E FF": ("command", "ExposureCompensation", "14"),
    "81 01 04 48 02 0F 0C 00 FF": ("command", "FocusPosition", "12224"),
    "81 01 04 18 01 FF": ("command", "OnePushAutoFocus", "Trigger"),
    "81 C2 01 02 00 FF": ("command", "AutoFocusBehavior", "Global"),
    "81 C2 01 02 01 FF": ("command", "AutoFocusBehavior", "Center"),
    "81 C2 01 02 04 FF": ("command", "AutoFocusBehavior", "Face"),
    "81 C2 01 03 02 FF": ("command", "AutoFocusSensitivity", "2"),
    "81 01 0E 24 26 00 01 FF": ("command", "AutoPrivacyMode", "On"),
    "81 01 0E 24 26 00 00 FF": ("command", "AutoPrivacyMode", "Off"),
    "81 C2 01 04 01 FF": ("command", "AutoSoftwareUpdate", "On"),
    "81 C2 01 04 00 FF": ("command", "AutoSoftwareUpdate", "Off"),
    "81 C2 09 06 FF": ("inquiry", "TrackingMode", ""),
    "81 C2 09 07 FF": ("inquiry", "TrackingProfile", ""),
    "81 09 04 3E FF": ("inquiry", "ExposureCompensationMode", ""),
    "81 09 04 4E FF": ("inquiry", "ExposureCompensation", ""),
    "81 09 04 48 FF": ("inquiry", "FocusPosition", ""),
    "81 C2 09 02 FF": ("inquiry", "AutoFocusBehavior", ""),
    "81 C2 09 03 FF": ("inquiry", "AutoFocusSensitivity", ""),
    "81 09 0E 24 26 FF": ("inquiry", "AutoPrivacyMode", ""),
    "81 C2 09 04 FF": ("inquiry", "AutoSoftwareUpdate", ""),
    "81 09 00 02 FF": ("inquiry", "DeviceInformation", ""),
    "81 09 06 11 FF": ("inquiry", "PanTiltSpeedMax", ""),
}


def part7():
    print("\n[7] the 20028 / v1.6 additions: new commands decode, new "
          "inquiries answer as documented, Sets round-trip")
    for h, want in NEW_DECODE.items():
        d = vl.decode(bytes.fromhex(h))
        check("%-28s -> %s %s" % (h, d.name, d.detail), tuple(d) == want,
              "got %r" % (tuple(d),))

    m = vl.CameraModel()

    def R(h, mode="ack"):
        return [vl.hexs(r) for r in m.respond(bytes.fromhex(h), mode)]

    R("81 01 04 3E 03 FF")
    check("ExposureCompensationMode Off round-trips: 90 50 03 FF",
          R("81 09 04 3E FF") == ["90 50 03 FF"])
    R("81 01 04 3E 02 FF")
    check("ExposureCompensationMode On round-trips: 90 50 02 FF",
          R("81 09 04 3E FF") == ["90 50 02 FF"])

    R("81 01 04 4E 00 00 00 0E FF")
    check("ExposureCompensation 14 round-trips: 90 50 00 00 00 0E FF",
          R("81 09 04 4E FF") == ["90 50 00 00 00 0E FF"])

    R("81 01 04 48 02 0F 0C 00 FF")
    check("FocusPosition 12224 round-trips: 90 50 02 0F 0C 00 FF",
          R("81 09 04 48 FF") == ["90 50 02 0F 0C 00 FF"])

    R("81 C2 01 02 04 FF")
    check("AutoFocusBehavior Face round-trips: 90 50 00 04 FF",
          R("81 C2 09 02 FF") == ["90 50 00 04 FF"])

    R("81 C2 01 03 03 FF")
    check("AutoFocusSensitivity 3 round-trips: 90 50 00 03 FF",
          R("81 C2 09 03 FF") == ["90 50 00 03 FF"])

    R("81 01 0E 24 26 00 01 FF")
    check("AutoPrivacyMode On round-trips: 90 50 00 01 FF",
          R("81 09 0E 24 26 FF") == ["90 50 00 01 FF"])

    R("81 C2 01 04 01 FF")
    check("AutoSoftwareUpdate On round-trips: 90 50 00 01 FF",
          R("81 C2 09 04 FF") == ["90 50 00 01 FF"])

    check("GetDeviceInformation: model 05 05 = IV-CAM-I20, this listener's own "
          "ROM version and socket number: 90 50 00 01 05 05 01 00 01 FF",
          R("81 09 00 02 FF") == ["90 50 00 01 05 05 01 00 01 FF"])
    check("GetPanTiltSpeedMax: pan 0x18 / tilt 0x14, the maxima PanTiltAngle "
          "accepts: 90 50 18 14 FF",
          R("81 09 06 11 FF") == ["90 50 18 14 FF"])

    R("81 01 04 3F 02 52 FF")
    check("TrackingMode Group (preset 0x52) round-trips: 90 50 00 01 FF",
          R("81 C2 09 06 FF") == ["90 50 00 01 FF"])
    R("81 01 04 3F 02 53 FF")
    check("TrackingMode Presenter (preset 0x53) round-trips: 90 50 00 00 FF",
          R("81 C2 09 06 FF") == ["90 50 00 00 FF"])

    R("81 01 04 3F 02 6B FF")
    check("TrackingProfile 3 (preset 0x6B) round-trips: 90 50 06 0B FF",
          R("81 C2 09 07 FF") == ["90 50 06 0B FF"])

    # The Get Output reply's first byte is Intelligent Switching's status, the
    # second the camera - both from one shared inquiry (CRESTRON_PARITY.md).
    check("Get Output starts on, camera 1: 90 50 01 01 FF",
          R("81 C2 09 08 FF") == ["90 50 01 01 FF"])
    R("81 C2 01 08 03 FF")
    check("calling camera 3 changes the camera but leaves switching as found - "
          "VISCA-Intelligent-Switching-Commands.md does not say a Call Camera "
          "Output changes the flag, so this is the listener's own choice, not "
          "documented camera behaviour: 90 50 01 03 FF",
          R("81 C2 09 08 FF") == ["90 50 01 03 FF"])
    R("81 C2 01 0B 00 FF")
    check("Pause clears the switching flag, camera stays 3: 90 50 00 03 FF",
          R("81 C2 09 08 FF") == ["90 50 00 03 FF"])
    R("81 C2 01 08 04 FF")
    check("calling camera 4 while paused leaves switching off, the listener's "
          "own choice again: 90 50 00 04 FF",
          R("81 C2 09 08 FF") == ["90 50 00 04 FF"])
    R("81 C2 01 08 00 FF")
    check("Resume sets the switching flag, camera unaffected: 90 50 01 04 FF",
          R("81 C2 09 08 FF") == ["90 50 01 04 FF"])


def note_full_mode():
    print("\n[note] mode 'full' with a SendAndWait that keeps unread data - not a test")
    listener = vl.Listener("127.0.0.1", 0, "full", vl.Capture(echo=False))
    host, port = listener.start()
    cam = load_module(SocketInterface).EthernetClass(host, port)
    try:
        quiet(cam.Connect, 5)
        quiet(cam.Set, "TrackingFraming", "Stop")
        listener.model.control("tracking start")
        quiet(cam.Update, "TrackingFraming")
        print("  Set Stop, camera-side Start, poll: the module reads %r"
              % cam.ReadStatus("TrackingFraming"))
        print("  'Start' would mean the stale Completion is harmless; anything else means")
        print("  each reply lands on the next call. Which one Extron's SendAndWait does is")
        print("  for a processor run against --reply full to measure.")
    finally:
        cam.Disconnect()
        listener.stop()


def main():
    recording = load_module(RecordingInterface)
    part1()
    part2(recording)
    part3()
    part4()
    part5()
    part6(recording)
    part7()
    note_full_mode()
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), len(PASS) + len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
