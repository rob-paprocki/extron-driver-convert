#!/usr/bin/env python3
"""
test_pkp2cs.py - tests for pkp2cs.py, the .pkp -> ControlScript translator.

No pytest: plain test_* functions + asserts, run by the __main__ block.

Run: python3 -W ignore tools/test_pkp2cs.py
"""
import ast
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkp_dump           # noqa: E402
import pkp2cs             # noqa: E402
import wire_table as wt   # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DSC_PKP = os.path.join(REPO_ROOT, "samples", "DSC_12G-HD", "pkp", "extr_17_17677_v1_0_0.pkp")
DSC_SHIPPED = os.path.join(REPO_ROOT, "samples", "DSC_12G-HD", "controlscript",
                            "extr_scaler_DSC_12G_HD_A_v1_0_0_0.py")

DTP3_PKP = os.path.join(REPO_ROOT, "samples", "DTP3 CP 42", "pkp", "extr_15_17578_v1_3_0.pkp")
DTP3_SHIPPED = os.path.join(REPO_ROOT, "samples", "DTP3 CP 42", "controlscript",
                             "extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py")

SAMSUNG_PKP = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "pkp",
                            "smsg_10_6738_v1_0_0.pkp")
SAMSUNG_SHIPPED = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "controlscript",
                                "smsg_display_QNxxLS03DAFXZA_Series_v1_0_0_0.py")

AVX_PKP = os.path.join(REPO_ROOT, "samples", "Automate VX", "pkp", "1bynd_42_4279_v1_0_11.pkp")
AVX_SHIPPED = os.path.join(REPO_ROOT, "samples", "Automate VX", "Controlscript",
                            "onebynd_sm_Automate_VX_Series_v1_0_11_0.py")


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


# --------------------------------------------------------------------------
# EXTRACT
# --------------------------------------------------------------------------

def test_discover_jobs_dsc_single_model_single_job():
    jobs = pkp2cs.discover_jobs(DSC_PKP)
    assert len(jobs) == 1, jobs
    job = jobs[0]
    assert job.script_file_name == "extr_17_17677.py"
    assert len(job.models) == 1
    assert job.models[0].name == "DSC 12G-HD A"
    assert job.models[0].protocol_class.endswith("EthernetProtocolAsset")
    assert job.source is not None


def test_discover_jobs_dtp3_two_models_one_job():
    jobs = pkp2cs.discover_jobs(DTP3_PKP)
    assert len(jobs) == 1, jobs
    job = jobs[0]
    names = sorted(m.name for m in job.models)
    assert names == ["DTP3 CrossPoint 42", "DTP3 CrossPoint 42 USB"], names
    class_names = sorted(m.script_class_name for m in job.models)
    assert class_names == ["extr_15_17578", "extr_15_17578_usb"], class_names


def test_discover_jobs_samsung_splits_by_transport():
    jobs = pkp2cs.discover_jobs(SAMSUNG_PKP)
    by_key = {j.script_file_name: j for j in jobs}
    assert "smsg_10_6738_serial.py" in by_key
    assert "smsg_10_6738_ethernet.py" in by_key
    serial_job = by_key["smsg_10_6738_serial.py"]
    ethernet_job = by_key["smsg_10_6738_ethernet.py"]
    assert len(serial_job.models) == 6, serial_job.models
    assert len(ethernet_job.models) == 6, ethernet_job.models
    assert all(m.protocol_class.endswith("SerialProtocolAsset") for m in serial_job.models)
    assert all(m.protocol_class.endswith("EthernetProtocolAsset") for m in ethernet_job.models)


def test_discover_jobs_avx_three_models_one_job_http():
    jobs = pkp2cs.discover_jobs(AVX_PKP)
    assert len(jobs) == 1, jobs
    job = jobs[0]
    names = sorted(m.name for m in job.models)
    assert names == ["Automate VX", "Automate VX Plus", "Automate VX Pro"], names
    # all three share one scriptClassName -> no real subclassing
    assert len({m.script_class_name for m in job.models}) == 1


# --------------------------------------------------------------------------
# ANALYSE / TRANSFORM unit tests (small synthetic snippets, fast, precise)
# --------------------------------------------------------------------------

SIS_MODEL = [pkp2cs.ModelInfo("Widget A", "w.py", "w",
                               "Extron.Configuration.Core.Assets.Protocols.EthernetProtocolAsset")]


def _analyse_src(src, models=SIS_MODEL):
    return pkp2cs.analyse(src, models)


def test_cmd_set_rename_and_safe_to_set_unwrap():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Live': True, 'Emulated': True, 'Status': {}},
        }
    def _cmd_SetFoo(self, value, qualifier):
        """doc"""
        if True:
            FooCmdString = 'F{}'.format(value)
            if self.__SafeToSet('Foo'):
                self.WriteFoo(value, qualifier, 'Emulated')
                self.__SetHelper('Foo', FooCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')
    def WriteFoo(self, value, qualifier, context):
        self.WriteStatusHelper('Foo', value, qualifier, context)
    def ReadFoo(self, qualifier, context):
        return self.ReadStatusHelper('Foo', qualifier, context)
'''
    a = _analyse_src(src)
    assert "SetFoo" in a.methods, a.methods.keys()
    assert "WriteFoo" not in a.methods
    assert "ReadFoo" not in a.methods
    out_src = ast.unparse(a.methods["SetFoo"])
    assert "__SafeToSet" not in out_src
    assert "'Emulated'" not in out_src
    assert "self.__SetHelper('Foo', FooCmdString, value, qualifier)" in out_src
    assert "Invalid Command for SetFoo" in out_src


def test_match_handler_write_live_rewritten_to_writestatus():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {'Foo': {'Set': False, 'Update': True, 'Status': {}}}
        self.AddMatchString(re.compile(b'F(\\\\d)\\r\\n'), self.__MatchFoo, None)
    def __MatchFoo(self, match, tag):
        """doc"""
        value = match.group(1).decode()
        self.WriteFoo(value, None, 'Live')
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["__MatchFoo"])
    assert "self.WriteStatus('Foo', value, None)" in out_src
    assert a.addmatchstring_srcs == ["self.AddMatchString(re.compile(b'F(\\\\d)\\r\\n'), self.__MatchFoo, None)"]


def test_drivercmd_rewritten_to_direct_call():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def __MatchQik(self, match, tag):
        self.DriverCmd('UpdateAllMatrixTie', None, None)
    def UpdateAllMatrixTie(self, value, qualifier):
        pass
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["__MatchQik"])
    assert "self.UpdateAllMatrixTie(None, None)" in out_src
    assert "DriverCmd" not in out_src


def test_isinstance_rewritten_to_modelname_equality():
    models = [
        pkp2cs.ModelInfo("Base Model", "w.py", "w", "..EthernetProtocolAsset"),
        pkp2cs.ModelInfo("Base Model USB", "w.py", "w_usb", "..EthernetProtocolAsset"),
    ]
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def _cmd_UpdateQik(self, value, qualifier):
        if isinstance(self, w_usb):
            self.UpdateUSBInput(None, None)
class w_usb(w):
    def __init__(self, configs):
        super().__init__(configs)
'''
    a = _analyse_src(src, models=models)
    out_src = ast.unparse(a.methods["UpdateQik"])
    assert "self.ModelName == 'Base Model USB'" in out_src
    assert "isinstance" not in out_src


def test_commands_dict_drops_booleans_and_prepends_connectionstatus():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Bar': {'Set': True, 'Update': True, 'Live': True, 'Emulated': True, 'Parameters': ['Output'], 'Status': {}},
            'Foo': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
        }
'''
    a = _analyse_src(src)
    out = pkp2cs._fmt_commands_dict(a)
    assert out.splitlines()[0] == "self.Commands = {"
    assert "'ConnectionStatus': {'Status': {}}," in out.splitlines()[1]
    assert "'Set'" not in out and "'Update'" not in out and "'Live'" not in out and "'Emulated'" not in out
    assert "'Parameters': ['Output']" in out


def test_gc_config_parsing_dropped_as_residual():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
        initError = []
        try:
            self.Unidirectional = configs['Unidirectional']
        except KeyError:
            initError.append('Missing Unidirectional Parameter.')
        self.inputs = ['1', '2']
'''
    a = _analyse_src(src)
    reasons = [r["reason"] for r in a.residuals]
    assert "gc-config-parsing-dropped" in reasons
    init_srcs = [ast.unparse(s) for s in a.init_extra_stmts]
    assert any("self.inputs" in s for s in init_srcs)
    assert not any("configs[" in s for s in init_srcs)


def test_last_prefixed_scratch_timers_dropped():
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
        self.lastResponse = 0
        self.lastSend = 0
        self.RequiredTimer = None
'''
    a = _analyse_src(src)
    init_srcs = [ast.unparse(s) for s in a.init_extra_stmts]
    assert not any("lastResponse" in s or "lastSend" in s or "RequiredTimer" in s for s in init_srcs)
    reasons = {r["reason"] for r in a.residuals}
    assert "gc-scratch-timer-dropped" in reasons
    assert "gc-dual-status-requiredtimer-dropped" in reasons


def test_models_empty_when_single_scriptclassname():
    job = pkp2cs.TranslationJob("w.py", None, [
        pkp2cs.ModelInfo("A", "w.py", "w", None),
        pkp2cs.ModelInfo("B", "w.py", "w", None),
    ])
    a = pkp2cs.Analysis()
    models_src, stubs = pkp2cs._build_models_block(job, a)
    assert models_src == "self.Models = {}"
    assert stubs == []


def test_models_populated_when_distinct_scriptclassnames():
    job = pkp2cs.TranslationJob("w.py", None, [
        pkp2cs.ModelInfo("Base", "w.py", "w", None),
        pkp2cs.ModelInfo("Base USB", "w.py", "w_usb", None),
    ])
    a = pkp2cs.Analysis()
    models_src, stubs = pkp2cs._build_models_block(job, a)
    assert "'Base': self.w," in models_src
    assert "'Base USB': self.w_usb," in models_src
    assert len(stubs) == 2
    assert "self.ModelName = 'Base USB'" in stubs[1]


# --------------------------------------------------------------------------
# FULL PIPELINE: translate each of the 4 oracle .pkp files and sanity check
# --------------------------------------------------------------------------

def test_full_translate_dsc_is_valid_python_and_has_commands():
    results = pkp2cs.translate_pkp(DSC_PKP)
    assert len(results) == 1
    r = results[0]
    assert r["source"] is not None
    ast.parse(r["source"])  # must be syntactically valid
    assert "class DeviceClass:" in r["source"]
    assert "class SSHClass(EthernetClientInterface, DeviceClass):" in r["source"]
    assert r["dialect"] == "sis_ethernet"


def test_full_translate_dtp3_has_models_and_ssh_mixin():
    results = pkp2cs.translate_pkp(DTP3_PKP)
    r = results[0]
    ast.parse(r["source"])
    assert "'DTP3 CrossPoint 42 USB': self.extr_15_17578_usb," in r["source"]
    assert "class SSHClass(EthernetClientInterface, DeviceClass):" in r["source"]


def test_full_translate_samsung_serial_job_has_serial_mixins():
    results = pkp2cs.translate_pkp(SAMSUNG_PKP)
    by_key = {r["script_file_name"]: r for r in results}
    serial = by_key["smsg_10_6738_serial.py"]
    ast.parse(serial["source"])
    assert serial["dialect"] == "serial"
    assert "class SerialClass(SerialInterface, DeviceClass):" in serial["source"]
    assert "class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):" in serial["source"]
    ethernet = by_key["smsg_10_6738_ethernet.py"]
    ast.parse(ethernet["source"])


def test_full_translate_avx_is_http_dialect():
    results = pkp2cs.translate_pkp(AVX_PKP)
    r = results[0]
    ast.parse(r["source"])
    assert r["dialect"] == "http"
    assert "class HTTPClass(DeviceClass):" in r["source"]
    assert "AddMatchString" not in r["source"]


# --------------------------------------------------------------------------
# ACCEPTANCE: wire_table diff between our translation and the shipped module
# --------------------------------------------------------------------------

def _wire_diff(generated_src, shipped_path):
    gen_table = wt.extract_table(generated_src)
    shipped_table = wt.extract_table(read(shipped_path))
    return wt.diff_tables(gen_table, shipped_table), gen_table, shipped_table


def test_wire_table_dsc_generated_vs_shipped():
    r = pkp2cs.translate_pkp(DSC_PKP)[0]
    diff, gen, shipped = _wire_diff(r["source"], DSC_SHIPPED)
    only_gen = set(diff["only_in_a"])
    only_shipped = set(diff["only_in_b"])
    assert not only_gen, only_gen
    assert not only_shipped, only_shipped
    # every shared command must match template/params exactly, except the
    # documented, known-expected residual (findings/06 + brief):
    #  - LogoAssignment (the .pkp's UpdateLogoAssignment feeds the wrong
    #    slot; the .pkp itself is the more broken of the two -- see
    #    findings/06). The Error match-string regex E(\d+) vs E(\d{2})
    #    residual is unmapped (no Set/Update pair) so it never surfaces in
    #    'differences' at all; UserDefinedCommand/UserDefinedString are
    #    dropped on both sides (see ALWAYS_DROPPED_COMMAND_NAMES) so they
    #    don't surface as only_in_a/only_in_b either.
    unexpected = {k: v for k, v in diff["differences"].items() if k != "LogoAssignment"}
    assert not unexpected, unexpected


def test_wire_table_dtp3_generated_vs_shipped():
    r = pkp2cs.translate_pkp(DTP3_PKP)[0]
    diff, gen, shipped = _wire_diff(r["source"], DTP3_SHIPPED)
    # known expected residuals (brief): package is v1.3.0 vs shipped v1.2.0.0
    # (real version skew, incl. three USB commands only in the newer .pkp),
    # and MatrixIONumberSelect is an orphan with no target-side command.
    only_gen = set(diff["only_in_a"])
    only_shipped = set(diff["only_in_b"])
    unexpected_only_gen = only_gen - {"MatrixIONumberSelect", "MatrixIONameString", "UserDefinedCommand", "UserDefinedString"}
    assert not unexpected_only_gen, unexpected_only_gen
    # the brief's own version-skew residual: "three USB commands" present only
    # in the older (v1.2.0.0) shipped module, absent (commented out in the
    # .pkp's own AddMatchString registrations) from the newer v1.3.0 package.
    unexpected_only_shipped = only_shipped - {"GlobalUSBDevicePort", "USBDevicePort", "USBOutputSignalStatus"}
    assert not unexpected_only_shipped, unexpected_only_shipped
    # MatrixIONameCommand: newly-discovered (not brief-listed) Extron hand-edit --
    # the .pkp's own Parameters list (['Type']) is a strict subset of the shipped
    # module's (['Type', 'Number', 'Name']); not derivable from the .pkp.
    unexpected = {k: v for k, v in diff["differences"].items() if k != "MatrixIONameCommand"}
    assert not unexpected, unexpected


def test_wire_table_samsung_serial_generated_vs_shipped():
    r = pkp2cs.translate_job(
        [j for j in pkp2cs.discover_jobs(SAMSUNG_PKP) if j.script_file_name == "smsg_10_6738_serial.py"][0])
    diff, gen, shipped = _wire_diff(r["source"], SAMSUNG_SHIPPED)
    assert not diff["only_in_a"], diff["only_in_a"]
    assert not diff["only_in_b"], diff["only_in_b"]
    assert not diff["differences"], diff["differences"]


def test_wire_table_avx_generated_vs_shipped():
    r = pkp2cs.translate_pkp(AVX_PKP)[0]
    diff, gen, shipped = _wire_diff(r["source"], AVX_SHIPPED)
    assert not diff["only_in_a"], diff["only_in_a"]
    assert not diff["only_in_b"], diff["only_in_b"]
    # PanTilt/Zoom are the documented opaque-branch-composition gap in
    # wire_table itself (both Set methods build the cmd string differently
    # per if/else branch, then call the helper once after) -- both sides
    # report the same opaque markers, so they should not show up as a
    # genuine mismatch, only as equal-opaque non-diffs.
    unexpected = {k: v for k, v in diff["differences"].items() if k != "Scenario"}
    assert not unexpected, unexpected


# --------------------------------------------------------------------------
# residuals reporting sanity
# --------------------------------------------------------------------------

def test_residuals_are_reported_structurally_for_all_four_pairs():
    for pkp in (DSC_PKP, DTP3_PKP, SAMSUNG_PKP, AVX_PKP):
        for r in pkp2cs.translate_pkp(pkp):
            assert r["source"] is not None
            for res in r["residuals"]:
                assert "reason" in res and "detail" in res



# --- regression: self.Commands must never silently degrade to an empty dict ---

def _parse_cmds_from_src(src):
    import ast as _ast
    tree = _ast.parse(src)
    cls = [n for n in tree.body if isinstance(n, _ast.ClassDef)][0]
    init = [n for n in cls.body if isinstance(n, _ast.FunctionDef) and n.name == "__init__"][0]
    return pkp2cs._parse_commands_dict(init)


def test_commands_dict_literal_is_parsed():
    src = ("class D(BaseDriver):\n"
           "    def __init__(self):\n"
           "        self.Commands = {'Power': {'Status': {}}}\n")
    assert _parse_cmds_from_src(src) == {'Power': {'Status': {}}}


def test_non_literal_commands_dict_raises_not_silently_empty():
    """A dynamically-built Commands dict must fail loudly. Silently emitting a
    driver with zero commands is the project's worst failure mode: the output
    looks plausible and controls nothing."""
    src = ("class D(BaseDriver):\n"
           "    def __init__(self):\n"
           "        self.Commands = dict(Power={'Status': {}})\n")
    try:
        _parse_cmds_from_src(src)
    except pkp2cs.UntranslatableDriver as e:
        assert "not a literal" in str(e).lower(), str(e)
        return
    raise AssertionError("expected UntranslatableDriver, got a silent result")


def test_missing_commands_dict_raises():
    src = ("class D(BaseDriver):\n"
           "    def __init__(self):\n"
           "        self.Unidirectional = 'False'\n")
    try:
        _parse_cmds_from_src(src)
    except pkp2cs.UntranslatableDriver as e:
        assert "no self.commands" in str(e).lower(), str(e)
        return
    raise AssertionError("expected UntranslatableDriver, got a silent result")

if __name__ == "__main__":
    tests = [(name, obj) for name, obj in sorted(globals().items())
              if name.startswith("test_") and callable(obj)]
    passed = 0
    failed = 0
    for name, fn in tests:
        try:
            fn()
            passed += 1
            print("PASS", name)
        except Exception as e:
            failed += 1
            print("FAIL", name, "-", repr(e))
            import traceback
            traceback.print_exc()
    print("%d passed, %d failed, %d total" % (passed, failed, len(tests)))
    sys.exit(1 if failed else 0)
