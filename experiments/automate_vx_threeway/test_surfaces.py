#!/usr/bin/env python3
"""
test_surfaces.py - pins the offline facts REPORT.md rests on.

The two Extron drivers call one identical set of 33 URIs; the GC package types
its parameters (Enum string states for room configuration, presets, camera
switch and layout; Decimal for Scenario and the PanTilt/Zoom camera); the TOC
parser reads MadCap Flare's chunk format. Tests that need the vendor files
skip, naming them, where they are absent (tools/vendor_inputs.py).

Plain test_* functions + asserts, run by the __main__ block; no pytest.
Run: python -u experiments/automate_vx_threeway/test_surfaces.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import surfaces        # noqa: E402
import vendor_inputs   # noqa: E402


def test_extron_drivers_call_the_same_33_uris():
    vendor_inputs.require(surfaces.PKP, surfaces.CS)
    gc = surfaces.uris(surfaces.gc_script())
    with open(surfaces.CS, encoding="utf-8") as f:
        cs = surfaces.uris(f.read())
    assert gc == cs, (sorted(set(gc) ^ set(cs)))
    assert len(gc) == 33, len(gc)
    assert "get-token" in gc and "api/StartISORecord" in gc


def test_gc_parameter_types():
    vendor_inputs.require(surfaces.PKP)
    p = surfaces.gc_params()
    # 17 commands in the script's Commands table, plus ConnectionStatus, which
    # only the package carries.
    assert len(p) == 18 and "ConnectionStatus" in p, sorted(p)

    cls, _, _, states = p["RoomConfiguration"]["Value"]
    assert cls == "EnumParamAsset" and states == [str(i) for i in range(1, 100)]
    cls, _, _, states = p["Layout"]["Value"]
    assert cls == "EnumParamAsset" and states == [chr(c) for c in range(ord("A"), ord("Z") + 1)]
    for cmd in ("CameraPresetRecall", "CameraPresetSave"):
        for param in ("Camera", "Value"):
            cls, _, _, states = p[cmd][param]
            assert cls == "EnumParamAsset" and sorted(states, key=int) == [str(i) for i in range(1, 256)], (cmd, param)
    cls, _, _, states = p["SwitchCamera"]["Value"]
    assert cls == "EnumParamAsset" and len(states) == 255

    cls, lo, hi, _ = p["Scenario"]["Value"]
    assert (cls, lo, hi) == ("DecimalParamAsset", "1", None)
    for cmd in ("PanTilt", "Zoom"):
        cls, lo, hi, _ = p[cmd]["Camera"]
        assert (cls, lo, hi) == ("DecimalParamAsset", "1", "255"), cmd


def test_crestron_wrapper_builds_no_requests():
    """The SIMPL+ wrapper only forwards to the SIMPL# library: no URL in it, every
    command input calls a library method, and the transport defaults to HTTP."""
    import crestron_module as cm
    cresdb = os.environ.get("CRESDB", cm.DEFAULT_CRESDB)
    vendor_inputs.require(cm.splus_store(cresdb))
    src = cm.wrapper_source(cresdb, "1.2")
    sig = cm.interface(src)
    assert len(sig) == 102, len(sig)
    assert ("digital", "input", "PersistentLogin") in sig      # new in v1.2
    assert not re.search(r"https?://|api/|get-token", src, re.I)
    calls = cm.handlers(src)
    assert calls[("PUSH", "Pause_Recording")][-1] == "PauseRecord"
    assert calls[("RELEASE", "Camera_Up")] == ["StopCamera"]
    assert calls[("CHANGE", "Force_Change_Room_Config")] == ["ForceChangeRoomConfig"]
    assert re.search(r"propDefaultValue\s*=\s*0d", src) and "Automate.IsHttps = Request_Type" in src
    assert "#DEFINE_CONSTANT LayoutCount 25" in src


def test_toc_parser_reads_flare_chunks():
    chunk = ("define({'/Content/Topics/Automate-API/Home.htm':{i:[0],t:['Home'],b:['']},"
             "'/Content/Topics/Automate-API/API-Reference/PauseRecord-API.htm':{i:[1],t:['PauseRecord'],b:['']}});")
    assert surfaces.toc_pages(chunk) == ["/Content/Topics/Automate-API/Home.htm",
                                         "/Content/Topics/Automate-API/API-Reference/PauseRecord-API.htm"]


def test_uri_pattern_ignores_near_misses():
    src = "u = 'api/GoToScenario'\nv = \"get-token\"\nw = 'api/' + x\ny = 'apix/Foo'\n"
    assert surfaces.uris(src) == ["api/GoToScenario", "get-token"]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    passed = failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except Exception as e:                        # noqa: BLE001
            why = vendor_inputs.vendor_missing(e)
            if why:
                skipped += 1
                print("SKIP", name, "-", why)
                continue
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d skipped (vendor input absent), %d total"
          % (passed, failed, skipped, len(tests)))
    sys.exit(1 if failed else 0)
