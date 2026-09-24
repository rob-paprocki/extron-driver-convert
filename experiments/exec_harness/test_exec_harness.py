#!/usr/bin/env python3
"""
test_exec_harness.py - tests for the offline execution harness (ROADMAP R13).

Plain test_* functions + asserts, run by the __main__ block; no pytest.
Each test that loads a module runs drive.py in a subprocess, as
differential.py does, because drive.py patches the process it runs in.

Run: python -u experiments/exec_harness/test_exec_harness.py
"""
import json
import os
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))

import drive            # noqa: E402
import extronlib_stub   # noqa: E402

DSC_PKP = os.path.join(ROOT, "samples", "DSC_12G-HD", "pkp", "extr_17_17677_v1_0_0.pkp")
DSC_SHIPPED = os.path.join(ROOT, "samples", "DSC_12G-HD", "controlscript",
                           "extr_scaler_DSC_12G_HD_A_v1_0_0_0.py")


def _run(args):
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    p = subprocess.run([sys.executable, os.path.join(HERE, "drive.py")] + args,
                       capture_output=True, text=True, encoding="utf-8", env=env)
    assert p.returncode == 0, p.stderr[-2000:]
    return json.loads(p.stdout.strip().splitlines()[-1])


def _write(tmp, name, src):
    path = os.path.join(tmp, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(textwrap.dedent(src))
    return path


# A minimal ControlScript device module in the shape both Extron and pkp2cs
# emit: DeviceClass with Set/Update dispatch, a transport class deriving from it.
_MODULE = '''
from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):
        self.Commands = {{
            'ConnectionStatus': {{'Status': {{}}}},
            'Power': {{'Parameters': ['Zone'], 'Status': {{}}}},
        }}

{helpers}
    def SetPower(self, value, qualifier):
        ValueStateValues = {{'On': '1', 'Off': '0'}}
        if value in ValueStateValues and 1 <= int(qualifier['Zone']) <= 4:
            self.Send({send})
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):
        self.Send('Q{{}}\\r'.format(qualifier['Zone']))

    def Set(self, command, value, qualifier=None):
        getattr(self, 'Set%s' % command)(value, qualifier)

    def Update(self, command, qualifier=None):
        getattr(self, 'Update%s' % command)(None, qualifier)

class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=9600, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud)
        DeviceClass.__init__(self)

    def Error(self, message):
        print(message)

    def Discard(self, message):
        self.Error([message])
'''


def _module(helpers="", send="'P{}{}\\\\r'.format(qualifier['Zone'], ValueStateValues[value])"):
    return _MODULE.format(helpers=helpers, send=send)


# --------------------------------------------------------------------------
# the stand-in extronlib
# --------------------------------------------------------------------------

def test_stub_resolves_modelled_and_unmodelled_names():
    extronlib_stub.install()
    try:
        from extronlib.interface import EthernetClientInterface
        from extronlib.system import Wait, Timer
        from extronlib import event, system
        from extronlib.ui import Button            # not modelled: a placeholder
        import extronlib.standard.exml.etree.ElementTree as ET
        assert system.Wait is Wait
        assert ET.fromstring("<a><b/></a>").find("b") is not None
        assert Button("x", 1) is not None

        @event(Button, "Pressed")
        def handler(button, state):
            return state
        assert handler(None, "on") == "on", "event must decorate, not replace"

        iface = EthernetClientInterface("192.0.2.1", 23)
        iface.Send("w1\r")
        iface.Send(b"\x81\x01")
        assert iface._harness_sent == [("Send", b"w1\r"), ("Send", b"\x81\x01")]
        assert iface.SendAndWait("q", 1, deliTag=b"\r") is None

        fired = []
        Wait(0, lambda: fired.append(1))

        @Timer(1)
        def tick(timer, count):
            fired.append(2)
        assert fired == [], "Wait and Timer must never fire"
    finally:
        extronlib_stub.uninstall()


# --------------------------------------------------------------------------
# inputs come from the method bodies
# --------------------------------------------------------------------------

def test_candidates_come_from_value_maps_literals_and_bounds():
    src = '''
    def SetLevel(self, value, qualifier):
        ValueConstraints = {'Min': -100, 'Max': 12}
        Modes = {'Auto': 'A', 'Manual': 'M'}
        if qualifier['Mode'] in Modes and 1 <= int(qualifier['Input']) <= 8 \\
                and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.Send('L{}'.format(value))
        elif qualifier['Mode'] == 'Off':
            pass
    '''
    cands = drive.Candidates()
    drive.scan_method(src, cands)
    for v in (-100, -101, -99, 12, 11, 13):
        assert v in cands.values, (v, cands.values)
    assert cands.quals["Mode"] == ["Auto", "Manual", "Off"], cands.quals
    for v in ("1", 1, "8", 8, "9"):
        assert v in cands.quals["Input"], (v, cands.quals["Input"])


def test_inputs_vary_one_qualifier_key_at_a_time_and_are_capped():
    cands = drive.Candidates()
    cands.values = ["On", "Off"]
    cands.quals = {"Zone": ["1", "2", "3"]}
    inputs = drive.build_inputs(cands, ["Zone"], "set")
    assert ("On", {"Zone": "1"}) in inputs and ("On", {"Zone": "3"}) in inputs
    assert ("", {"Zone": "1"}) in inputs, "adversarial values are always added"
    assert len(inputs) <= drive.MAX_INPUTS


# --------------------------------------------------------------------------
# the differential
# --------------------------------------------------------------------------

def test_identical_modules_compare_identical():
    with tempfile.TemporaryDirectory() as tmp:
        a = _write(tmp, "a.py", _module())
        b = _write(tmp, "b.py", _module())
        res = _run(["--generated", a, "--shipped", b])
    power = res["commands"]["Power"]
    for kind in ("set", "update"):
        r = power[kind]
        assert r["same"] == r["inputs"] and r["inputs"] > 3, r


def test_a_stripped_staticmethod_is_caught():
    """Finding 14 section 7's bug, which no static check can see: the
    generated side lost @staticmethod, so self arrives as the argument."""
    helper = '''
    @staticmethod
    def __zone(z):
        return int(z)
'''
    broken = helper.replace("    @staticmethod\n", "")
    send = "'P{}{}\\\\r'.format(self.__zone(qualifier['Zone']), ValueStateValues[value])"
    with tempfile.TemporaryDirectory() as tmp:
        gen = _write(tmp, "gen.py", _module(broken, send))
        ship = _write(tmp, "ship.py", _module(helper, send))
        res = _run(["--generated", gen, "--shipped", ship])
    r = res["commands"]["Power"]["set"]
    assert r["gen_raises"] >= 2, r
    ex = r["examples"]["gen_raises"][0]
    assert ex["generated"]["exc"]["type"] == "TypeError", ex
    assert ex["shipped"]["sent"], ex


def test_different_bytes_are_a_difference():
    with tempfile.TemporaryDirectory() as tmp:
        gen = _write(tmp, "gen.py", _module(send="'P{}\\\\r'.format(qualifier['Zone'])"))
        ship = _write(tmp, "ship.py", _module())
        res = _run(["--generated", gen, "--shipped", ship])
    r = res["commands"]["Power"]["set"]
    assert r["differ"] >= 2 and r["gen_raises"] == 0, r


def test_an_import_failure_is_reported_not_raised():
    with tempfile.TemporaryDirectory() as tmp:
        gen = _write(tmp, "gen.py", "import no_such_module_anywhere\n")
        ship = _write(tmp, "ship.py", _module())
        res = _run(["--generated", gen, "--shipped", ship])
    assert res["generated_error"]["stage"] == "import", res
    assert res["generated_error"]["type"] in ("ModuleNotFoundError", "ImportError"), res
    assert "commands" not in res


# --------------------------------------------------------------------------
# a real pair
# --------------------------------------------------------------------------

def test_dsc_pair_runs_and_shows_what_the_wire_table_only_described():
    """DSC 12G-HD, one of the four in-sample pairs. Before 2026-09-23 every
    Update('LogoAvailability') raised AttributeError on a GC throttle timer
    the translation half-dropped - found by this harness. What remains is the
    LogoAssignment difference STATUS's scorecard attributes to Extron's own
    .pkp script: the generated module sends 'wANoneLOGO' where the shipped
    one sends 'wA1LOGO'."""
    if not (os.path.exists(DSC_PKP) and os.path.exists(DSC_SHIPPED)):
        print("  skip: DSC sample not present")
        return
    import pkp2cs
    src = pkp2cs.translate_job(pkp2cs.discover_jobs(DSC_PKP)[0])["source"]
    with tempfile.TemporaryDirectory() as tmp:
        gen = _write(tmp, "gen.py", src)
        res = _run(["--generated", gen, "--shipped", DSC_SHIPPED])
    assert res["generated_class"] == res["shipped_class"] == "SSHClass", res
    avail = res["commands"]["LogoAvailability"]["update"]
    for ex in avail["examples"].get("gen_raises", []):
        assert ex["generated"]["exc"]["type"] != "AttributeError", ex
    assign = res["commands"]["LogoAssignment"]["update"]
    sent = [ex["generated"]["sent"] for ex in assign["examples"]["differ"]]
    assert bytes.fromhex(sent[0][0]) == b"wANoneLOGO\r", sent
    total = sum(r["inputs"] for c in res["commands"].values() for r in c.values())
    same = sum(r["same"] for c in res["commands"].values() for r in c.values())
    assert total > 100 and same / total > 0.8, (same, total)


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    passed = failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except Exception as e:                        # noqa: BLE001
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d total" % (passed, failed, len(tests)))
    sys.exit(1 if failed else 0)
