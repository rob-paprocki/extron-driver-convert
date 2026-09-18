#!/usr/bin/env python3
"""
doc_calls.py - run every call QUICKSTART.md and PROTOCOL.md give a tester.

The generated ControlScript module is imported with `extronlib` stubbed out, and
each documented call prints the bytes it sends or the exception it raises. This
is how the two pages were checked on 2026-09-13; re-run it after changing either
page or the module, and compare the output with the wire strings they quote.

It proves a call is well-formed. It proves nothing about a camera: every reply
is empty, so no status here comes from a device.

Run:  python3 experiments/skeleton_i20/doc_calls.py
"""
import importlib.util
import os
import sys
import types

_HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(_HERE, "out", "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")

sent = []


class _Interface(object):
    """Just enough of extronlib's interfaces to import and drive the module."""

    def __init__(self, *args, **kwargs):
        self.Hostname, self.IPPort = args[0], args[1]

    def SendAndWait(self, data, timeout, **kwargs):
        sent.append(bytes(data))
        return b""

    def Send(self, data):
        sent.append(bytes(data))

    def Connect(self, *args):
        return "Connected"

    def Disconnect(self):
        pass


def load_module():
    pkg = types.ModuleType("extronlib")
    iface = types.ModuleType("extronlib.interface")
    iface.SerialInterface = _Interface
    iface.EthernetClientInterface = _Interface
    pkg.interface = iface
    sys.modules["extronlib"] = pkg
    sys.modules["extronlib.interface"] = iface
    spec = importlib.util.spec_from_file_location("i20_module", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def hexs(b):
    return " ".join("%02X" % x for x in b)


def run(label, fn):
    del sent[:]
    try:
        fn()
        out = " | ".join(hexs(b) for b in sent) or "(nothing sent)"
    except Exception as e:  # the point is to show what raises
        out = "RAISES %s: %s" % (type(e).__name__, e)
    print("%-46s %s" % (label, out))


def main():
    cam = load_module().EthernetClass("192.0.2.1", 5500)
    S, U = cam.Set, cam.Update

    print("--- QUICKSTART sample main.py")
    run("Set Power On", lambda: S("Power", "On"))
    run("Set Preset 1 Recall", lambda: S("Preset", 1, {"Action": "Recall"}))
    run("Set Zoom Tele Speed 5", lambda: S("Zoom", "Tele", {"Speed": 5}))
    run("Set TrackingFraming Start", lambda: S("TrackingFraming", "Start"))
    run("Set TrackingProfile 2", lambda: S("TrackingProfile", 2))
    run("Set IndicatorLight Full Red Bright",
        lambda: S("IndicatorLight", "Full", {"Color": "Red", "Brightness": "Bright"}))
    run("Set CameraOutput 2", lambda: S("CameraOutput", 2))
    run("Update TrackingFraming", lambda: U("TrackingFraming"))
    print("%-46s %r  <- echoes the Set: no reply was parsed"
          % ("ReadStatus TrackingFraming", cam.ReadStatus("TrackingFraming")))

    print("--- PROTOCOL T3 control table")
    run("1 Power On", lambda: S("Power", "On"))
    run("2 Preset Recall 1", lambda: S("Preset", 1, {"Action": "Recall"}))
    run("3 Zoom Tele Speed 5", lambda: S("Zoom", "Tele", {"Speed": 5}))
    run("4 TrackingFraming Start", lambda: S("TrackingFraming", "Start"))
    run("5/7 poll TrackingFraming", lambda: U("TrackingFraming"))
    run("6 TrackingFraming Stop", lambda: S("TrackingFraming", "Stop"))
    run("8 ZoomPosition 6699 (0x1A2B) Speed 3", lambda: S("ZoomPosition", 6699, {"Speed": 3}))
    run("9 FreezeFrame On", lambda: S("FreezeFrame", "On"))
    run("9 FreezeFrame Off", lambda: S("FreezeFrame", "Off"))
    run("10 IndicatorLight Full Red Bright",
        lambda: S("IndicatorLight", "Full", {"Color": "Red", "Brightness": "Bright"}))
    run("11 IndicatorLight Half Green Dim",
        lambda: S("IndicatorLight", "Half", {"Color": "Green", "Brightness": "Dim"}))
    run("12 IndicatorLight None", lambda: S("IndicatorLight", "None"))
    run("13 TrackingProfile 2", lambda: S("TrackingProfile", 2))
    run("14 CameraOutput 2", lambda: S("CameraOutput", 2))
    run("15 IntelligentSwitching Resume", lambda: S("IntelligentSwitching", "Resume"))
    run("16 IntelligentSwitching Pause", lambda: S("IntelligentSwitching", "Pause"))
    run("T3b TrackingMode Group", lambda: S("TrackingMode", "Group"))
    run("T3b TrackingMode Presenter", lambda: S("TrackingMode", "Presenter"))

    print("--- QUICKSTART 'required' qualifiers, left out")
    run("PanTilt Home, no qualifier", lambda: S("PanTilt", "Home"))
    run("Zoom Stop, no qualifier", lambda: S("Zoom", "Stop"))
    run("Focus Far, no qualifier", lambda: S("Focus", "Far"))
    run("ZoomPosition 16384, no qualifier", lambda: S("ZoomPosition", 16384))
    run("PanTiltAngle, Pan/Tilt as the value",
        lambda: S("PanTiltAngle", {"Pan": 100, "Tilt": -50}, {"Pan Speed": 5, "Tilt Speed": 5}))
    run("PanTiltAngle, Pan/Tilt in the qualifier",
        lambda: S("PanTiltAngle", None,
                  {"Pan Speed": 5, "Tilt Speed": 5, "Pan": 100, "Tilt": -50}))
    run("Preset '1' as a string", lambda: S("Preset", "1", {"Action": "Recall"}))

    print("--- Update() on every command")
    for name in sorted(cam.Commands):
        q = {"Camera": 2} if name == "CameraConnectionStatus" else None
        run("Update %s" % name, lambda name=name, q=q: U(name, q))


if __name__ == "__main__":
    main()
