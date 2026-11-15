#!/usr/bin/env python3
"""
test_avx_cs.py - the improved Automate VX module, run against a stand-in unit on this machine.

The derived module (out/onebynd_sm_Automate_VX_Series_v1_1_0_0.py, tracked) is loaded under
experiments/exec_harness's extronlib stand-in and pointed at a small HTTP server on 127.0.0.1
that answers the way the API pages document. Every fix and addition in build_avx_cs.py has a
test here. Two tests need Extron's original module (vendor material, untracked) and SKIP,
naming it, when it is absent: the build reproduces the tracked file, and every valid call sends
the same requests as Extron's module.

Plain test_* functions + asserts, run by the __main__ block; no pytest.
Run: python -u experiments/automate_vx_threeway/test_avx_cs.py
"""
import base64
import contextlib
import http.server
import importlib.util
import io
import json
import os
import sys
import threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "exec_harness"))
sys.dont_write_bytecode = True
os.environ["no_proxy"] = os.environ["NO_PROXY"] = "127.0.0.1,localhost"

import build_avx_cs as build          # noqa: E402
import extronlib_stub                 # noqa: E402
import vendor_inputs                  # noqa: E402

extronlib_stub.install()

DERIVED = build.OUT
USER, PASSWORD = "admin", "pw"


# ---------------------------------------------------------------- a stand-in Automate VX

class FakeVX:
    """POST-only JSON server on 127.0.0.1. Records every request; per-path replies override the defaults."""

    def __init__(self):
        self.requests = []          # (path, body bytes, Authorization header)
        self.replies = {}           # path -> (code, dict or raw bytes)
        self.token = "tok-1"
        self.enforce_token = False
        fake = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                auth = self.headers.get("Authorization")
                fake.requests.append((self.path, body, auth))
                code, reply = fake.reply_for(self.path, auth)
                data = reply if isinstance(reply, bytes) else json.dumps(reply).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def reply_for(self, path, auth):
        if path in self.replies:
            return self.replies[path]
        if path == "/get-token":
            if auth == base64.b64encode(("%s:%s" % (USER, PASSWORD)).encode()).decode():
                return 200, {"status": "OK", "token": self.token}
            return 401, {"status": "Error", "err": "Incorrect Username or Password"}
        if self.enforce_token and auth != self.token:
            return 401, {"status": "Error", "err": "Unauthorized"}
        return 200, {"status": "OK", "results": True}

    def paths(self):
        return [r[0] for r in self.requests]

    def close(self):
        self.server.shutdown()
        self.server.server_close()


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_DERIVED_MOD = None


def derived():
    global _DERIVED_MOD
    if _DERIVED_MOD is None:
        _DERIVED_MOD = _load(DERIVED, "avx_derived")
    return _DERIVED_MOD


class Dev:
    """A module instance on a FakeVX, with its printed log captured."""

    def __init__(self, mod, password=PASSWORD):
        self.fake = FakeVX()
        self.log = io.StringIO()
        with contextlib.redirect_stdout(self.log):
            self.d = mod.HTTPClass("127.0.0.1", self.fake.port, USER, password, Model=None, SSLVerifyMode="Off")
        self.d.RootURL = "http://127.0.0.1:%d/" % self.fake.port     # the stand-in has no TLS context

    def run(self, fn, *args):
        with contextlib.redirect_stdout(self.log):
            return fn(*args)

    def Set(self, *args):
        return self.run(self.d.Set, *args)

    def Update(self, *args):
        return self.run(self.d.Update, *args)

    def status(self, command, qualifier=None):
        return self.d.ReadStatus(command, qualifier)

    def close(self):
        self.fake.close()


def _with_dev(fn, mod=None, warm=True, **kw):
    """Run fn on a fresh device. warm: poll once first, because Extron's module (unchanged here)
    spends the first poll after start-up on logging in and sends nothing else."""
    dev = Dev(mod or derived(), **kw)
    try:
        if warm:
            dev.Update("Record")
        return fn(dev)
    finally:
        dev.close()


# ---------------------------------------------------------------- build and parity

def test_build_reproduces_the_tracked_module():
    vendor_inputs.require(build.DONOR)
    with open(build.DONOR, encoding="utf-8", newline="") as f:
        fresh = build.build(f.read())
    with open(DERIVED, encoding="utf-8") as f:
        tracked = f.read()
    assert fresh.replace("\r\n", "\n") == tracked.replace("\r\n", "\n")


VALID_CALLS = [
    ("Set", "AutoSwitch", "On", None), ("Set", "AutoSwitch", "Off", None),
    ("Set", "CameraPresetRecall", "3", {"Camera": "2"}), ("Set", "CameraPresetSave", "1", {"Camera": "1"}),
    ("Set", "ForceRoomConfiguration", "5", None), ("Set", "HomeShotPreset", None, None),
    ("Set", "ISORecording", "Start", None), ("Set", "Layout", "B", None),
    ("Set", "Output", "Off", None), ("Set", "PanTilt", "Up Left", {"Camera": 1}),
    ("Set", "PanTilt", "Stop", {"Camera": 1}), ("Set", "Record", "Start", None),
    ("Set", "Record", "Stop", None), ("Set", "RoomConfiguration", "4", None),
    ("Set", "Scenario", 3, None), ("Set", "Sleep", None, None), ("Set", "Stream", "Start", None),
    ("Set", "SwitchCamera", "2", None), ("Set", "Wake", None, None),
    ("Set", "Zoom", "In", {"Camera": 2}), ("Set", "Zoom", "Stop", {"Camera": 2}),
    ("Update", "AutoSwitch", None, None), ("Update", "ISORecording", None, None),
    ("Update", "Output", None, None), ("Update", "Record", None, None),
    ("Update", "Stream", None, None),
]


def _requests_for(mod):
    def go(dev):
        dev.run(dev.d.TokenRequest, None, None)         # both start logged in
        for kind, cmd, value, qual in VALID_CALLS:
            if kind == "Set":
                dev.Set(cmd, value, qual)
            else:
                dev.Update(cmd, qual)
        return list(dev.fake.requests)
    return _with_dev(go, mod=mod, warm=False)


def test_every_valid_call_sends_extrons_exact_requests():
    vendor_inputs.require(build.DONOR)
    original = _load(build.DONOR, "avx_extron")
    ours, theirs = _requests_for(derived()), _requests_for(original)
    assert len(ours) >= len(VALID_CALLS), ours
    assert ours == theirs, [(a, b) for a, b in zip(ours, theirs) if a != b][:3]


def test_runtime_resolvability():
    import pkp2cs
    with open(DERIVED, encoding="utf-8") as f:
        src = f.read()
    for check in (pkp2cs.find_dangling_self_calls, pkp2cs.find_unassigned_self_attributes,
                  pkp2cs.find_unresolved_globals, pkp2cs.find_call_arity_mismatches):
        assert check(src) == [], (check.__name__, check(src))


def test_every_edit_is_marked_in_the_output():
    with open(DERIVED, encoding="utf-8") as f:
        src = f.read()
    for tag in ["[E%d]" % n for n in range(2, 12)] + ["[A1]", "[A2]", "[A3]", "[A4]", "[A5]", "[A6]"]:
        assert tag in src, tag


# ---------------------------------------------------------------- the fixes

def _bodies(dev, path):
    return [json.loads(b) for p, b, a in dev.fake.requests if p == path]


def test_E2_scenario_accepts_the_help_sheets_form_and_strings():
    from decimal import Decimal

    def go(dev):
        dev.Set("Scenario", None, {"ID": "3"})
        dev.Set("Scenario", "4", None)
        dev.Set("Scenario", 5, None)
        dev.Set("Scenario", 6.0, None)
        dev.Set("Scenario", Decimal("7"), None)
        for bad in ("Home", None, 0, -1, 2.5, Decimal("2.5"), float("inf"), float("nan"), True, "3.0"):
            dev.Set("Scenario", bad, None)                # discarded, never truncated or raised
        return _bodies(dev, "/api/GoToScenario")
    assert _with_dev(go) == [{"id": "3"}, {"id": "4"}, {"id": "5"}, {"id": "6"}, {"id": "7"}]


def test_E3_room_configuration_reads_both_documented_shapes():
    def go(dev):
        dev.fake.replies["/api/RoomConfigStatus"] = (200, {"status": "OK", "roomConfig": {"id": 7, "name": "A"}})
        dev.Update("RoomConfiguration")
        first = dev.status("RoomConfiguration")
        dev.fake.replies["/api/RoomConfigStatus"] = (200, {"status": "OK", "roomConfigs": [{"id": "8", "name": "B"}]})
        dev.Update("RoomConfiguration")
        dev.fake.replies["/api/RoomConfigStatus"] = (200, {"status": "OK", "roomConfigs": None})
        dev.Update("RoomConfiguration")                   # TypeError used to escape
        return first, dev.status("RoomConfiguration")
    assert _with_dev(go) == ("7", "8")


def test_E4_E5_unexpected_replies_are_logged_not_raised():
    def go(dev):
        dev.Update("Record")                              # log in
        for body in (b"OK", b"", b"<html></html>", b"[1, 2]", {"status": "OK"}, {"status": "OK", "scenario": None}):
            dev.fake.replies["/api/ScenarioStatus"] = (200, body)
            dev.Update("Scenario")
        dev.fake.replies["/api/StartRecord"] = (200, b"not json")
        dev.Set("Record", "Start")
        dev.fake.replies["/api/StopRecord"] = (200, {"status": "Error", "err": "No recording in progress"})
        dev.Set("Record", "Stop")
        return dev.log.getvalue()
    log = _with_dev(go)
    assert "Invalid Response" in log and "Error: No recording in progress" in log


def test_E6_a_login_without_a_token_does_not_loop():
    def go(dev):
        for token_reply in ({"status": "OK"}, {"status": "OK", "token": None}, {"status": "OK", "token": ""}):
            dev.fake.replies["/get-token"] = (200, token_reply)
            before = len(dev.fake.requests)
            dev.Update("Record")
            assert dev.fake.paths()[before:] == ["/get-token"], dev.fake.paths()[before:]
            assert dev.d.Authenticated is False
        return True
    assert _with_dev(go, warm=False)


def test_E7_E8_a_rejected_token_is_replaced_and_the_command_sent():
    def go(dev):
        dev.fake.enforce_token = True
        dev.Set("Record", "Start")                        # first Set: logs in, then sends (E8)
        assert dev.fake.paths() == ["/get-token", "/api/StartRecord"], dev.fake.paths()
        dev.fake.token = "tok-2"                          # the unit forgets the old token
        dev.Set("Record", "Stop")                         # 401, log in again, repeat once (E7)
        return dev.fake.requests[2:]
    tail = _with_dev(go, warm=False)
    assert [p for p, b, a in tail] == ["/api/StopRecord", "/get-token", "/api/StopRecord"], tail
    assert tail[-1][2] == "tok-2"


def test_E7_a_poll_with_a_rejected_token_is_answered_in_the_same_poll():
    def go(dev):
        dev.fake.enforce_token = True
        dev.Update("Output")                              # logged in by the warm-up poll
        dev.fake.token = "tok-2"                          # the unit forgets the old token
        before = len(dev.fake.requests)
        dev.Update("Output")
        return dev.fake.paths()[before:], dev.status("Output")
    paths, output = _with_dev(go)
    assert paths == ["/api/OutputStatus", "/get-token", "/api/OutputStatus"], paths
    assert output == "On"


def test_E7_a_refused_endpoint_does_not_starve_other_polls():
    def go(dev):
        dev.fake.replies["/api/StreamStatus"] = (401, {"status": "Error", "err": "forbidden"})
        seen = []
        for _ in range(3):
            before = len(dev.fake.requests)
            for cmd in ("Record", "Stream", "Output"):
                dev.Update(cmd)
            seen.append("/api/OutputStatus" in dev.fake.paths()[before:])
        return seen, dev.d.Authenticated
    seen, authenticated = _with_dev(go)
    assert seen == [True, True, True] and authenticated is True


def test_E9_a_refused_login_reaches_disconnected():
    def go(dev):
        for _ in range(20):
            dev.Update("Record")
        return dev.status("ConnectionStatus")
    assert _with_dev(go, warm=False, password="wrong") == "Disconnected"


def test_E10_camera_feedback_is_a_string_for_either_shape():
    def go(dev):
        out = []
        for address in (4, "5", 6.0):
            dev.fake.replies["/api/CameraStatus"] = (200, {"status": "OK", "address": address})
            dev.Update("SwitchCamera")
            out.append(dev.status("SwitchCamera"))
        for bad in (None, 4.7, True):                     # TypeError used to escape; 4.7 is not truncated
            dev.fake.replies["/api/CameraStatus"] = (200, {"status": "OK", "address": bad})
            dev.Update("SwitchCamera")
        out.append(dev.status("SwitchCamera"))
        out.append(dev.log.getvalue().count("Switch Camera: Invalid/unexpected response"))
        return out
    assert _with_dev(go) == ["4", "5", "6", "6", 3]


def test_E11_a_malformed_results_field_is_logged_by_every_on_off_parser():
    parsers = {"AutoSwitch": ("/api/AutoSwitchStatus", "Auto Switch"),
               "ISORecording": ("/api/ISORecordStatus", "ISO Recording"),
               "Output": ("/api/OutputStatus", "Output"),
               "Record": ("/api/RecordStatus", "Record"),
               "Stream": ("/api/StreamStatus", "Stream")}

    def go(dev):
        for cmd, (path, label) in parsers.items():
            dev.fake.replies[path] = (200, {"status": "OK", "results": [True]})
            dev.Update(cmd)
        log = dev.log.getvalue()
        return [label for path, label in parsers.values() if "%s: Invalid/unexpected response" % label not in log]
    assert _with_dev(go) == []


# ---------------------------------------------------------------- the additions

def test_A1_pause_record():
    def go(dev):
        dev.Set("Record", "Pause")
        return [(p, b) for p, b, a in dev.fake.requests][-1]
    assert _with_dev(go) == ("/api/PauseRecord", b"")


def test_A2_layout_status_in_both_shapes():
    def go(dev):
        out = []
        for layout in ([{"id": "C", "name": "Layout C"}], {"id": "D", "name": "Layout D"}):
            dev.fake.replies["/api/LayoutStatus"] = (200, {"status": "OK", "layout": layout})
            dev.Update("Layout")
            out.append(dev.status("Layout"))
        return out
    assert _with_dev(go) == ["C", "D"]


def test_A3_active_talkers_from_the_documented_string_form():
    def go(dev):
        out = []
        for talkers, shot in (("[5,]", 0), ("[5,8]", 1), ("[ ]", 1)):
            dev.fake.replies["/api/GetActiveTalkers"] = (200, {"status": "OK", "talkers": talkers, "defaultShot": shot})
            dev.Update("ActiveTalker", {"Talker": "1"})
            out.append((dev.status("ActiveTalker", {"Talker": "1"}), dev.status("ActiveTalker", {"Talker": "2"}),
                        dev.status("DefaultShot")))
        return out
    assert _with_dev(go) == [("5", "None", "Off"), ("5", "8", "On"), ("None", "None", "On")]


def test_A4_recording_space_from_strings_or_numbers():
    def go(dev):
        out = []
        for avail, total in (("207", "232"), (150, 232)):
            dev.fake.replies["/api/RecordingSpaceAvail"] = (200, {"status": "OK", "available_gigabytes": avail,
                                                                  "total_gigabytes": total})
            dev.Update("RecordingSpace", {"Type": "Available"})
            out.append((dev.status("RecordingSpace", {"Type": "Available"}),
                        dev.status("RecordingSpace", {"Type": "Total"})))
        return out
    assert _with_dev(go) == [(207, 232), (150, 232)]


def test_A5_health_status():
    def go(dev):
        dev.fake.replies["/api/HealthStatus"] = (200, {"status": "Healthy", "message": ""})
        dev.Update("HealthStatus")
        return dev.status("HealthStatus")
    assert _with_dev(go) == "Healthy"


def test_A6_name_lists_and_camera_count():
    def go(dev):
        dev.fake.replies["/api/GetLayouts"] = (200, {"status": "OK", "layouts": [{"id": "A", "name": "Wide"},
                                                                                {"id": "B", "name": "Close"}]})
        dev.fake.replies["/api/GetRoomConfigs"] = (200, {"status": "OK", "roomConfigs": [{"id": 1, "name": "Lecture"},
                                                                                        {"id": "2", "name": "Panel"}]})
        dev.fake.replies["/api/GetScenarios"] = (200, {"status": "OK", "scenarios": [{"id": 3, "name": "Home"}]})
        dev.fake.replies["/api/GetCameras"] = (200, {"status": "OK", "cameras": [{"id": 1, "model": "ip20"},
                                                                                {"id": "2", "name": "IV-CAM-I12", "ip": "x"}]})
        for cmd in ("LayoutName", "RoomConfigurationName", "ScenarioName", "CameraModel"):
            dev.Update(cmd, None)
        return (dev.status("LayoutName", {"Layout": "B"}),
                dev.status("RoomConfigurationName", {"RoomConfiguration": "1"}),
                dev.status("RoomConfigurationName", {"RoomConfiguration": "2"}),
                dev.status("ScenarioName", {"Scenario": "3"}),
                dev.status("CameraModel", {"Camera": "1"}), dev.status("CameraModel", {"Camera": "2"}),
                dev.status("CameraCount"))
    assert _with_dev(go) == ("Close", "Lecture", "Panel", "Home", "ip20", "IV-CAM-I12", 2)


def test_A6_entries_that_leave_a_list_are_blanked():
    def go(dev):
        three = [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}, {"id": "3", "name": "C"}]
        dev.fake.replies["/api/GetCameras"] = (200, {"status": "OK", "cameras": three})
        dev.Update("CameraCount", None)
        dev.fake.replies["/api/GetCameras"] = (200, {"status": "OK", "cameras": three[:1]})
        dev.Update("CameraCount", None)
        return ([dev.status("CameraModel", {"Camera": c}) for c in "123"], dev.status("CameraCount"))
    assert _with_dev(go) == (["A", "", ""], 1)


def test_A4_A6_callbacks_see_a_consistent_set():
    def go(dev):
        seen = []
        dev.d.SubscribeStatus("CameraCount", None, lambda c, v, q: seen.append(
            ("count", v, [dev.d.ReadStatus("CameraModel", {"Camera": str(i)}) for i in range(1, v + 1)])))
        dev.d.SubscribeStatus("RecordingSpace", {"Type": "Available"}, lambda c, v, q: seen.append(
            ("available", v, dev.d.ReadStatus("RecordingSpace", {"Type": "Total"}))))
        dev.fake.replies["/api/GetCameras"] = (200, {"status": "OK", "cameras": [{"id": 1, "model": "ip20"},
                                                                                {"id": 2, "model": "ip12"}]})
        dev.Update("CameraCount", None)
        dev.fake.replies["/api/RecordingSpaceAvail"] = (200, {"status": "OK", "available_gigabytes": 50,
                                                              "total_gigabytes": 300})
        dev.Update("RecordingSpace", {"Type": "Available"})
        return seen
    assert _with_dev(go) == [("count", 2, ["ip20", "ip12"]), ("available", 50, 300)]


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    passed = failed = skipped = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except vendor_inputs.VendorInputMissing as e:
            skipped += 1
            print("SKIP", name, "-", e)
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d skipped, %d total" % (passed, failed, skipped, len(tests)))
    sys.exit(1 if failed else 0)
