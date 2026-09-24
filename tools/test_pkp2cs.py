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

CLOCKAUDIO_PKP = os.path.join(REPO_ROOT, "samples", "ClockAudio", "pkp", "clau_25_1777_v1_3_0.pkp")
TESIRA_PKP = os.path.join(REPO_ROOT, "samples", "Tesira", "pkp", "biam_25_150_v1_20_0.pkp")
PTZ_IP12_PKP = os.path.join(REPO_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp",
                             "1bynd_19_4743_v1_0_1.pkp")


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


def test_sethelper_updatehelper_replaced_with_fixed_sis_template():
    """GC's own __SetHelper/__UpdateHelper bodies leak GC BaseDriver runtime
    API (QueryDelayTimerIsRunning/StartQueryDelayTimer) that has no
    ControlScript equivalent -- diffing DSC's and DTP3's shipped modules
    shows __SetHelper/__UpdateHelper are byte-identical fixed, dialect-keyed
    boilerplate, not a per-driver transform of the GC body. For the
    sis_ethernet dialect (evidenced by both samples) the GC bodies must be
    replaced entirely, not transformed."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)
    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.QueryDelayTimerIsRunning(command):
            return
        self.StartQueryDelayTimer(command)
        self.Send(commandstring)
'''
    a = _analyse_src(src)
    # No SIS handshake in this fixture, so it must NOT be classified sis_ethernet:
    # "SIS" is Extron's own protocol, not a synonym for Ethernet.
    assert a.dialect == "ethernet", a.dialect
    assert "__SetHelper" not in a.methods
    assert "__UpdateHelper" not in a.methods
    assert "__SetHelper" not in a.leftover_methods
    assert "__UpdateHelper" not in a.leftover_methods
    assert a.needs_fixed_set_update_helper is True
    reasons = {r["reason"] for r in a.residuals}
    assert "gc-sethelper-updatehelper-fixed-template" in reasons, reasons


def test_full_translate_dsc_and_dtp3_have_no_query_delay_timer_dangling():
    """Integration: after the fixed sis_ethernet __SetHelper/__UpdateHelper
    template lands, QueryDelayTimerIsRunning/StartQueryDelayTimer must no
    longer appear anywhere in the generated DSC/DTP3 modules, and the
    fixed-template Send(commandstring) dispatch must still be reachable."""
    for pkp in (DSC_PKP, DTP3_PKP):
        r = pkp2cs.translate_pkp(pkp)[0]
        assert "QueryDelayTimerIsRunning" not in r["source"], pkp
        assert "StartQueryDelayTimer" not in r["source"], pkp
        dangling = [x["detail"] for x in r["residuals"] if x["reason"] == "dangling-self-call"]
        assert not any("QueryDelayTimerIsRunning" in d or "StartQueryDelayTimer" in d for d in dangling)
        assert "def __SetHelper(self, command, commandstring, value, qualifier):" in r["source"]
        assert "def __UpdateHelper(self, command, commandstring, value, qualifier):" in r["source"]


def test_full_translate_samsung_serial_has_no_query_delay_timer_or_readpower_dangling():
    """Integration: Samsung serial's own shipped __UpdateHelper drops the
    GC power-gate branch (self.ReadPower-based) entirely, along with
    QueryDelayTimerIsRunning/StartQueryDelayTimer. The remaining
    self.ReadPower(None, 'Live') call inside the GC-only update_next
    scheduler (Category A3 -- the scheduler itself has no shipped
    counterpart and no safe generic removal rule, so it is deliberately left
    in place) is caught by the same evidenced Read<X>(...,'Live') ->
    ReadStatus('<X>', ...) rule as B1 (Power is a real, surviving command),
    so it is no longer dangling either -- a side effect, not a special case."""
    r = pkp2cs.translate_job(
        [j for j in pkp2cs.discover_jobs(SAMSUNG_PKP) if j.script_file_name == "smsg_10_6738_serial.py"][0])
    assert "QueryDelayTimerIsRunning" not in r["source"]
    assert "StartQueryDelayTimer" not in r["source"]
    dangling_names = [x["detail"].split("self.")[1].split("(")[0]
                       for x in r["residuals"] if x["reason"] == "dangling-self-call"]
    assert "ReadPower" not in dangling_names, dangling_names
    assert "def __UpdateHelper(self, command, commandstring, value, qualifier):" in r["source"]
    assert "def update_next" in r["source"]
    assert "self.ReadStatus('Power', None)" in r["source"]


def test_bare_startquerydelaytimer_call_dropped_outside_sethelper():
    """Evidenced by DTP3's _cmd_SetMatrixIONameStatus: self.Send(query,
    pacing=0.1); self.StartQueryDelayTimer(1) -- a bare call to GC's
    query-throttle API outside __SetHelper/__UpdateHelper (which get their
    own fixed-template replacement). StartQueryDelayTimer/
    QueryDelayTimerIsRunning are GC BaseDriver runtime API with no
    ControlScript equivalent no matter which method calls them."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def _cmd_SetMatrixIONameStatus(self, query, qualifier):
        self.Send(query, pacing=0.1)
        self.StartQueryDelayTimer(1)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetMatrixIONameStatus"])
    assert "StartQueryDelayTimer" not in out_src, out_src
    # This test used to pin `self.Send(query, pacing=0.1)` as correct output.
    # pacing is GC BaseDriver API too: extronlib's Send takes data alone, and
    # executing the generated DTP3 module raised TypeError (ROADMAP R13).
    assert "self.Send(query)" in out_src, out_src
    reasons = {r["reason"] for r in a.residuals}
    assert "gc-query-throttle-dropped" in reasons, reasons
    assert "gc-send-pacing-dropped" in reasons, reasons


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


def test_safe_to_set_boolop_and_no_orelse_drops_guard_entirely():
    """Evidenced by Automate VX's shipped SetAutoSwitch/SetISORecording:
    'if self.__SafeToSet(X) and <cond>:' with NO else clause in the GC
    source is flattened to an unconditional call in the shipped module (the
    whole guard is dropped, not just the __SafeToSet conjunct) -- the
    presence/absence of node.orelse is the syntactic signal, already present
    in the GC source, that distinguishes this from the SetOutput/SetRecord/
    SetStream shape below."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'AutoSwitch': {'Set': True, 'Update': False, 'Status': {}},
        }
    def _cmd_SetAutoSwitch(self, value, qualifier):
        ValueStateValues = {'On': 'api/StartAutoSwitch', 'Off': 'api/StopAutoSwitch'}
        if self.__SafeToSet('AutoSwitch') and value in ValueStateValues:
            self.WriteAutoSwitch(value, qualifier, 'Emulated')
            self.__SetHelper('AutoSwitch', value, qualifier, ValueStateValues[value])
    def WriteAutoSwitch(self, value, qualifier, context):
        self.WriteStatusHelper('AutoSwitch', value, qualifier, context)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetAutoSwitch"])
    assert "__SafeToSet" not in out_src, out_src
    assert "value in ValueStateValues" not in out_src, out_src
    assert "'Emulated'" not in out_src, out_src
    assert "self.__SetHelper('AutoSwitch', value, qualifier, ValueStateValues[value])" in out_src, out_src


def test_safe_to_set_boolop_and_with_orelse_keeps_remaining_condition():
    """Evidenced by Automate VX's shipped SetOutput/SetRecord/SetStream:
    'if self.__SafeToSet(X) and value in ValueStateValues: ... else:
    self.Discard(...)' keeps the 'value in ValueStateValues' guard and the
    else clause, dropping only the always-true __SafeToSet(...) conjunct."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Output': {'Set': True, 'Update': False, 'Status': {}},
        }
    def _cmd_SetOutput(self, value, qualifier):
        ValueStateValues = {'On': 'api/StartOutput', 'Off': 'api/StopOutput'}
        if self.__SafeToSet('Output') and value in ValueStateValues:
            self.WriteOutput(value, qualifier, 'Emulated')
            self.__SetHelper('Output', value, qualifier, ValueStateValues[value])
        else:
            self.Discard('Invalid Command')
    def WriteOutput(self, value, qualifier, context):
        self.WriteStatusHelper('Output', value, qualifier, context)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetOutput"])
    assert "__SafeToSet" not in out_src, out_src
    assert "if value in ValueStateValues:" in out_src, out_src
    assert "'Emulated'" not in out_src, out_src
    assert "self.__SetHelper('Output', value, qualifier, ValueStateValues[value])" in out_src, out_src
    assert "else:" in out_src, out_src
    assert "Invalid Command for SetOutput" in out_src, out_src


def test_emulated_prewrite_dropped_when_guard_is_not_safetoset_shaped():
    """The real invariant behind the Emulated-prewrite-drop rule is the CALL
    shape (self.Write<X>(..., 'Emulated')), not the __SafeToSet guard it
    happens to sit inside in every in-sample (DSC/DTP3/Samsung/Automate VX)
    oracle. Biamp's Tesira generator never emits __SafeToSet at all -- it
    gates Set bodies on plain parameter validation instead, evidenced
    verbatim by the shipped .pkp's _cmd_SetAECEnable:
        if 1 <= int(chnl) <= 24 and value in state:
            ...
            self.WriteAECEnable(value, qualifier, 'Emulated')
            self.__SetHelper('AECEnable', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')
    The old rule only stripped the Emulated pre-write when node.test called
    __SafeToSet, so this call site (and 47 like it) survived pointed at a
    WriteAECEnable definition that gets deleted as pure wrapper boilerplate
    -- a dangling AttributeError at runtime. This must be dropped on the
    call shape alone, regardless of what the enclosing guard looks like."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'AECEnable': {'Set': True, 'Update': False, 'Live': True, 'Emulated': True,
                          'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
        }
    def _cmd_SetAECEnable(self, value, qualifier):
        state = {'On': 'true', 'Off': 'false'}
        tag = qualifier['Instance Tag']
        chnl = qualifier['Channel']
        if 1 <= int(chnl) <= 24 and value in state:
            cmdString = '{0} set aecEnable {1} {2}'.format(tag, chnl, state[value])
            self.WriteAECEnable(value, qualifier, 'Emulated')
            self.__SetHelper('AECEnable', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')
    def WriteAECEnable(self, value, qualifier, context):
        self.WriteStatusHelper('AECEnable', value, qualifier, context)
    def ReadAECEnable(self, qualifier, context):
        return self.ReadStatusHelper('AECEnable', qualifier, context)
'''
    a = _analyse_src(src)
    assert "WriteAECEnable" not in a.methods
    assert "ReadAECEnable" not in a.methods
    out_src = ast.unparse(a.methods["SetAECEnable"])
    assert "'Emulated'" not in out_src, out_src
    assert "WriteAECEnable" not in out_src, out_src
    assert "1 <= int(chnl) <= 24 and value in state" in out_src, out_src
    assert "self.__SetHelper('AECEnable', cmdString, value, qualifier)" in out_src, out_src
    assert "self.Discard('Invalid Command for SetAECEnable')" in out_src, out_src


def test_emulated_prewrite_dropped_in_dtp3_length_check_guard():
    """DTP3's shipped SetMatrixIONameString/SetMatrixIONumberSelect (a B2,
    Live=False/Emulated=True command with no ControlScript Write/Read
    wrapper at all) has this exact shape verbatim in the .pkp:
        if 0 <= len(value) <= 30:
            self.WriteMatrixIONameString(value, qualifier, 'Emulated')
        else:
            self.Discard('Invalid Command')
    This accounts for 4 of DTP3's in-sample dangling-self-call residuals
    together with the symmetric MatrixIONumberSelect case. A correctly
    generalised rule must drop this pre-write call too, even though there is
    no real Set call left over afterwards (it is a length/range check with
    only the Emulated bookkeeping call in its body)."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'MatrixIONameString': {'Set': True, 'Update': False, 'Live': False,
                                    'Emulated': True, 'Status': {}},
        }
    def _cmd_SetMatrixIONameString(self, value, qualifier):
        if 0 <= len(value) <= 30:
            self.WriteMatrixIONameString(value, qualifier, 'Emulated')
        else:
            self.Discard('Invalid Command')
    def WriteMatrixIONameString(self, value, qualifier, context):
        self.WriteStatusHelper('MatrixIONameString', value, qualifier, context)
    def ReadMatrixIONameString(self, qualifier, context):
        return self.ReadStatusHelper('MatrixIONameString', qualifier, context)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetMatrixIONameString"])
    assert "'Emulated'" not in out_src, out_src
    assert "WriteMatrixIONameString" not in out_src, out_src
    assert "0 <= len(value) <= 30" in out_src, out_src
    assert "pass" in out_src, out_src  # empty if-body after the drop needs a placeholder


def test_emulated_prewrite_rule_does_not_touch_live_or_read_calls():
    """Guardrails on the generalised rule: a Write<X>(..., 'Live') call (or
    any call whose last arg isn't the literal 'Emulated') must be left for
    the existing Live-rewrite rule, and a Read<X>(..., 'Emulated') call
    (a different construct -- it reads GC-only scratch state and its return
    value is consumed) must never be touched by this rule."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Live': False, 'Emulated': True, 'Status': {}},
        }
    def _cmd_SetFooStatus(self, value, qualifier):
        name = self.ReadFoo(None, 'Emulated')
        self.WriteBar(value, qualifier, 'Live')
        return name
    def ReadFoo(self, qualifier, context):
        return self.ReadStatusHelper('Foo', qualifier, context)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetFooStatus"])
    assert "self.ReadFoo(None, 'Emulated')" in out_src, out_src
    assert "self.WriteStatus('Bar', value, qualifier)" in out_src, out_src


def test_read_x_live_rewritten_to_readstatus_symmetric_with_write_rule():
    """Evidenced by shipped DTP3: self.ReadOutputTieStatus({...}, 'Live')
    (a cross-command call to a Read wrapper that gets deleted as pure
    status-accessor boilerplate) becomes self.ReadStatus('OutputTieStatus',
    {...}) in the shipped module -- the read-side symmetric counterpart of
    the existing Write<X>(...,'Live') -> WriteStatus(...) rule. Gated the
    same way (literal 'Live' context) so it never fires for the Emulated-
    context ReadMatrixIONameString/ReadMatrixIONumberSelect call sites
    (Category B2, deliberately left alone -- see the DTP3 residual)."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
        }
    def SetOutputTieStatusName(self, value, qualifier):
        audioVal = self.ReadOutputTieStatus({'Output': qualifier['Output'], 'Tie Type': 'Audio'}, 'Live')
    def ReadOutputTieStatus(self, qualifier, context):
        return self.ReadStatusHelper('OutputTieStatus', qualifier, context)
'''
    a = _analyse_src(src)
    assert "ReadOutputTieStatus" not in a.methods
    out_src = ast.unparse(a.methods["SetOutputTieStatusName"])
    assert "self.ReadStatus('OutputTieStatus', {'Output': qualifier['Output'], 'Tie Type': 'Audio'})" in out_src, out_src
    assert "ReadOutputTieStatus" not in out_src, out_src


def test_read_x_emulated_context_not_rewritten_to_readstatus():
    """The B1 rule must not fire on Emulated-context calls: those are the B2
    shape (a command Extron folded/eliminated, e.g. MatrixIONameString),
    where the corresponding Set/Update no longer exists in ControlScript and
    blindly rewriting to ReadStatus would silently read an always-empty
    status instead of raising the honest AttributeError."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'MatrixIONameString': {'Set': True, 'Update': False, 'Status': {}},
        }
    def _cmd_SetRefreshMatrixIONames(self, value, qualifier):
        name = self.ReadMatrixIONameString(None, 'Emulated')
    def ReadMatrixIONameString(self, qualifier, context):
        return self.ReadStatusHelper('MatrixIONameString', qualifier, context)
'''
    a = _analyse_src(src)
    out_src = ast.unparse(a.methods["SetRefreshMatrixIONames"])
    assert "self.ReadMatrixIONameString(None, 'Emulated')" in out_src, out_src
    assert "ReadStatus(" not in out_src, out_src


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


def test_direct_cmd_prefixed_call_site_is_rewritten_like_drivercmd():
    """A direct self._cmd_X(...) call (not routed through DriverCmd) must be
    rewritten the same way the def itself is renamed (_cmd_ prefix stripped),
    or the call site is left pointing at a name that no longer exists.
    Evidenced by DTP3: _cmd_UpdateAllMatrixTie is called directly from
    __MatchQik's body, not via self.DriverCmd(...)."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def __MatchQik(self, match, tag):
        self._cmd_UpdateAllMatrixTie(None, None)
    def _cmd_UpdateAllMatrixTie(self, value, qualifier):
        pass
'''
    a = _analyse_src(src)
    assert "UpdateAllMatrixTie" in a.methods, a.methods.keys()
    assert "_cmd_UpdateAllMatrixTie" not in a.methods
    out_src = ast.unparse(a.methods["__MatchQik"])
    assert "self.UpdateAllMatrixTie(None, None)" in out_src, out_src
    assert "_cmd_" not in out_src, out_src


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


def test_emulated_only_command_wrapper_drop_reports_specific_actionable_residual():
    """Category B2 (deliberately unfixed): a Live=False/Emulated=True command
    is a genuine Extron editorial restructuring/omission (evidenced
    identically in DTP3's MatrixIONameString/MatrixIONumberSelect and
    Samsung ethernet's MultiviewString), not something this tool can safely
    bridge to ReadStatus/WriteStatus. Dropping its Read/Write wrapper must
    produce a specific, actionable residual naming the command and the
    exact risk, not a silent deletion."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Live': False, 'Emulated': True, 'Status': {}},
        }
    def ReadFoo(self, qualifier, context):
        return self.ReadStatusHelper('Foo', qualifier, context)
'''
    a = _analyse_src(src)
    assert "ReadFoo" not in a.methods
    matches = [r for r in a.residuals if r["reason"] == "gc-emulated-only-command-wrapper-dropped"]
    assert len(matches) == 1, a.residuals
    assert "ReadFoo" in matches[0]["detail"]
    assert "Foo" in matches[0]["detail"]
    assert "Live=False/Emulated=True" in matches[0]["detail"]


def test_emulated_only_command_wrapper_kept_when_called_from_another_body():
    """R37 (tools/pkp2cs.py:_is_write_read_wrapper + the referenced-elsewhere
    check in analyse()): the SAME Live=False/Emulated=True shape as the test
    above, but here another retained command's Set body calls
    self.ReadFoo(...) in a value context -- exactly the Samsung ethernet
    ReadMultiviewString shape (experiments/missing_ethernet/). Before this
    fix ReadFoo was deleted unconditionally and the call below was left
    dangling: AttributeError at runtime, and find_dangling_self_calls was the
    only thing that would ever say so. Now the wrapper survives (backed by
    self._emulated_status) so the call resolves, and the new residual
    explains the substitution."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Live': False, 'Emulated': True, 'Status': {}},
            'Bar': {'Set': True, 'Update': False, 'Live': False, 'Emulated': False, 'Status': {}},
        }
    def ReadFoo(self, qualifier, context):
        return self.ReadStatusHelper('Foo', qualifier, context)
    def _cmd_SetBar(self, value, qualifier):
        mode = self.ReadFoo(qualifier, 'Emulated')
        self.__SetHelper('Bar', value, qualifier, mode)
'''
    a = _analyse_src(src)
    assert "ReadFoo" in a.methods, a.methods.keys()
    kept_src = ast.unparse(a.methods["ReadFoo"])
    assert "self._emulated_status.get('Foo')" in kept_src, kept_src
    assert "ReadStatusHelper" not in kept_src, kept_src
    assert a.needs_emulated_scratch_store is True
    matches = [r for r in a.residuals if r["reason"] == "gc-emulated-wrapper-kept-as-scratch-store"]
    assert len(matches) == 1, a.residuals
    assert "ReadFoo" in matches[0]["detail"] and "Foo" in matches[0]["detail"]
    # never silently drops it (the old B2 residual must not ALSO fire for ReadFoo)
    assert not any(r["reason"] == "gc-emulated-only-command-wrapper-dropped"
                   and "ReadFoo" in r["detail"] for r in a.residuals), a.residuals


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


def test_gc_onconnected_ondisconnected_never_carried_as_duplicate_defs():
    """emit() always synthesizes its own OnConnected/OnDisconnected (see
    onconnected-ondisconnected-synthesized). Before this fix, the GC-derived
    originals were *also* carried through as ordinary leftover methods,
    producing two `def OnConnected(self):` (and OnDisconnected) in the same
    class -- Python keeps only the last, so the first (containing
    self.__ResetLiveStatus(), a def that's correctly dropped elsewhere) was
    silent dead code with a dangling call. analyse() must not emit them as
    ordinary methods at all."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def OnConnected(self):
        """doc"""
        pass
    def OnDisconnected(self):
        """doc"""
        self.lastSend = 0
        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.__ResetLiveStatus()
'''
    a = _analyse_src(src)
    assert "OnConnected" not in a.methods, a.methods.keys()
    assert "OnDisconnected" not in a.methods, a.methods.keys()
    assert "OnConnected" not in a.leftover_methods
    assert "OnDisconnected" not in a.leftover_methods
    reasons = {r["reason"] for r in a.residuals}
    assert "gc-dual-status-no-target" in reasons, reasons


def test_gc_ondisconnected_genuine_extra_state_reset_is_carried_through():
    """Evidenced by shipped DTP3 (self.matrix_tie_status/self.matrix_io_names
    resets survive in the shipped OnDisconnected) and shipped Automate VX
    (self.Token/self.Authenticated resets, and OnConnected's
    self.TokenRequest(None, None) kickoff, both survive in the shipped
    module) -- genuine device-state resets in GC's OnConnected/OnDisconnected
    are NOT GC-only dual-status boilerplate and must reach the emitted
    module, not just the boilerplate-stripped fixed template."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {}
    def OnConnected(self):
        """doc"""
        self.DriverCmd('TokenRequest', None, None)
    def OnDisconnected(self):
        """doc"""
        self.Token = None
        self.Authenticated = False
        self.__ResetLiveStatus()
    def _cmd_TokenRequest(self, value, qualifier):
        pass
'''
    a = _analyse_src(src)
    onconnected_srcs = [ast.unparse(s) for s in a.onconnected_extra_stmts]
    ondisconnected_srcs = [ast.unparse(s) for s in a.ondisconnected_extra_stmts]
    assert "self.TokenRequest(None, None)" in onconnected_srcs, onconnected_srcs
    assert "self.Token = None" in ondisconnected_srcs, ondisconnected_srcs
    assert "self.Authenticated = False" in ondisconnected_srcs, ondisconnected_srcs
    assert not any("__ResetLiveStatus" in s for s in ondisconnected_srcs), ondisconnected_srcs


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


def test_avx_generated_onconnected_ondisconnected_match_shipped_extras():
    """Integration: AVX's shipped OnConnected calls self.TokenRequest(None, None)
    and its shipped OnDisconnected resets self.Token/self.Authenticated -- both
    real device state, not GC dual-status boilerplate. The generated module
    must reach them exactly once (no duplicate def, no dangling
    __ResetLiveStatus call)."""
    r = pkp2cs.translate_pkp(AVX_PKP)[0]
    tree = ast.parse(r["source"])
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef)][0]
    on_connected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "OnConnected"]
    on_disconnected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "OnDisconnected"]
    assert len(on_connected) == 1, "expected exactly one OnConnected def, found %d" % len(on_connected)
    assert len(on_disconnected) == 1, "expected exactly one OnDisconnected def, found %d" % len(on_disconnected)
    assert "self.TokenRequest(None, None)" in ast.unparse(on_connected[0])
    ondisc_src = ast.unparse(on_disconnected[0])
    assert "self.Token = None" in ondisc_src
    assert "self.Authenticated = False" in ondisc_src
    assert "__ResetLiveStatus" not in ondisc_src


def test_samsung_ethernet_onconnected_ondisconnected_emitted_exactly_once():
    """R37 (b): findings/19-three-questions.md section 2 recorded this job
    emitting OnConnected/OnDisconnected TWICE -- the GC-derived pair (with a
    dangling self.__ResetLiveStatus() call) plus emit()'s own synthesized
    pair, Python silently keeping only the last. That duplication already
    does not reproduce against analyse()'s OnConnected/OnDisconnected
    special-case (see test_gc_onconnected_ondisconnected_never_carried_as_
    duplicate_defs); this integration test locks it down against the actual
    package findings/19 named, so a regression here is caught directly."""
    jobs = pkp2cs.discover_jobs(SAMSUNG_PKP)
    eth = [j for j in jobs if j.script_file_name == "smsg_10_6738_ethernet.py"][0]
    r = pkp2cs.translate_job(eth)
    tree = ast.parse(r["source"])
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef)][0]
    on_connected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "OnConnected"]
    on_disconnected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "OnDisconnected"]
    assert len(on_connected) == 1, "expected exactly one OnConnected def, found %d" % len(on_connected)
    assert len(on_disconnected) == 1, "expected exactly one OnDisconnected def, found %d" % len(on_disconnected)
    assert "__ResetLiveStatus" not in ast.unparse(on_disconnected[0])


def test_dtp3_generated_ondisconnected_matches_shipped_matrix_state_reset():
    """Integration: DTP3's shipped OnDisconnected resets matrix_tie_status /
    matrix_io_names / matrix_io_names_received -- real device state carried
    from the GC original, not GC-only bookkeeping."""
    r = pkp2cs.translate_pkp(DTP3_PKP)[0]
    tree = ast.parse(r["source"])
    cls = [n for n in tree.body if isinstance(n, ast.ClassDef)][0]
    on_disconnected = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "OnDisconnected"]
    assert len(on_disconnected) == 1
    src = ast.unparse(on_disconnected[0])
    assert "self.matrix_tie_status = None" in src
    assert "self.matrix_io_names = {}" in src
    assert "self.matrix_io_names_received = False" in src
    assert "__ResetLiveStatus" not in src


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


# --- regression: a deleted wrapper must never leave a dangling self.X() call ---

def test_dangling_self_call_is_detected():
    """The Samsung ethernet job deletes ReadMultiviewString as a status-accessor
    wrapper, but MultiviewCommand's Set body calls it cross-command. Emitting a
    module with a dangling reference produces an AttributeError at runtime on a
    control system -- exactly the failure this project must never ship silently."""
    src = ("class DeviceClass:\n"
           "    def SetThing(self, value, qualifier):\n"
           "        mode = self.ReadGoneString(qualifier, 'Emulated')\n"
           "    def ReadStatus(self, command, qualifier):\n"
           "        pass\n")
    dangling = pkp2cs.find_dangling_self_calls(src)
    assert "ReadGoneString" in dangling, dangling
    assert "ReadStatus" not in dangling, dangling


def test_no_dangling_calls_when_everything_is_defined():
    src = ("class DeviceClass:\n"
           "    def SetThing(self, value, qualifier):\n"
           "        self.WriteStatus('Thing', value, qualifier)\n"
           "    def WriteStatus(self, command, value, qualifier):\n"
           "        pass\n")
    assert pkp2cs.find_dangling_self_calls(src) == []


def test_dangling_check_covers_generated_classes_not_carried_helpers():
    """A carried helper class calls a callable held in an attribute and a
    method it inherits from outside the module; neither is a dropped method.
    Only DeviceClass and the classes deriving from it are rewritten, so only
    they are checked - and there a missing method is still caught, including
    one whose name a carried helper happens to define."""
    src = ("import urllib.request\n"
           "class DeviceClass:\n"
           "    def SetThing(self, value, qualifier):\n"
           "        self.ReadGoneString(qualifier)\n"
           "        self.entry_function()\n"
           "class SerialClass(DeviceClass):\n"
           "    def Other(self):\n"
           "        self.AlsoGone()\n"
           "class Directory:\n"
           "    def __init__(self, entry_function):\n"
           "        self.entry_function = entry_function\n"
           "    def Open(self):\n"
           "        self.entry_function()\n"
           "        self.ReadGoneString()\n"
           "    def ReadGoneString(self):\n"
           "        pass\n"
           "class Handler(urllib.request.HTTPDigestAuthHandler):\n"
           "    def http_error_403(self, *a):\n"
           "        return self.http_error_401(*a)\n")
    assert pkp2cs.find_dangling_self_calls(src) == ["AlsoGone", "ReadGoneString",
                                                    "entry_function"], \
        pkp2cs.find_dangling_self_calls(src)


def test_samsung_ethernet_job_reports_dangling_reference_as_residual():
    """Integration: the real package that exposed the bug (R37).

    ReadMultiviewString used to be deleted by the write/read-wrapper pruning
    rule even though MultiviewCommand's Set body still calls it in a value
    context (`mode = self.ReadMultiviewString(qualifier, 'Emulated')`) --
    AttributeError at runtime, with only the whole-module dangling-self-call
    check (find_dangling_self_calls) to catch it after the fact. The fix
    keeps the wrapper (backed by a private self._emulated_status scratch
    dict) instead of deleting it, so the call now resolves: no
    dangling-self-call, ReadMultiviewString is defined, and the new
    gc-emulated-wrapper-kept-as-scratch-store residual explains why."""
    pkp = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "pkp",
                       "smsg_10_6738_v1_0_0.pkp")
    if not os.path.exists(pkp):
        return
    jobs = pkp2cs.discover_jobs(pkp)
    eth = [j for j in jobs if "ethernet" in j.script_file_name]
    if not eth:
        return
    result = pkp2cs.translate_job(eth[0])
    reasons = [r["reason"] for r in result["residuals"]]
    assert "dangling-self-call" not in reasons, reasons
    assert "gc-emulated-wrapper-kept-as-scratch-store" in reasons, reasons
    detail = " ".join(r["detail"] for r in result["residuals"]
                       if r["reason"] == "gc-emulated-wrapper-kept-as-scratch-store")
    assert "ReadMultiviewString" in detail, detail
    assert "def ReadMultiviewString(self, qualifier, context):" in result["source"]
    assert "self.ReadMultiviewString(" in result["source"]
    assert "self._emulated_status" in result["source"]
    import py_compile
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(result["source"].encode("utf-8"))
        tmp_path = f.name
    try:
        py_compile.compile(tmp_path, doraise=True)
    finally:
        os.remove(tmp_path)


# --------------------------------------------------------------------------
# regression: exact dangling-self-call count per generated module
#
# Started at 26 across the 5 modules (DSC 3, DTP3 10, Samsung serial 4,
# Samsung ethernet 2, Automate VX 7). Categories A/A2/A3(partial)/B1/C and
# the A/C SafeToSet-BoolOp hybrid closed 21 of them mechanically, evidenced
# against the shipped modules (see the residual reasons asserted below and
# the module docstring / commit history for the category write-up). The
# remaining 5 (DTP3's MatrixIONameString/MatrixIONumberSelect Read+Write
# pairs, Samsung ethernet's ReadMultiviewString) were Category B2: a genuine
# Extron editorial restructuring/omission with no safe automatic fix -- each
# carried a specific gc-emulated-only-command-wrapper-dropped residual
# (see the test above) rather than being silently deleted.
#
# R37 closes all 5: a Read<X>/Write<X> wrapper that a *different*, still-
# retained method's body calls (a VALUE-context call the Emulated-pre-write-
# statement-drop rule doesn't touch) is now kept, backed by a private
# self._emulated_status scratch dict, instead of deleted -- see
# gc-emulated-wrapper-kept-as-scratch-store. That call site is the only
# reason any of these 5 were ever dangling, so the count is 0 across all
# five modules; test_samsung_ethernet_job_reports_dangling_reference_as_residual
# and test_emulated_only_command_wrapper_drop_reports_specific_actionable_residual
# cover the two shapes (kept vs. genuinely silently-dropped) directly.
# --------------------------------------------------------------------------

def _dangling_names(result):
    return sorted(r["detail"].split("self.")[1].split("(")[0]
                  for r in result["residuals"] if r["reason"] == "dangling-self-call")


def test_dangling_self_call_count_regression_dsc():
    r = pkp2cs.translate_pkp(DSC_PKP)[0]
    assert _dangling_names(r) == [], _dangling_names(r)


def test_dangling_self_call_count_regression_dtp3():
    """WriteMatrixIONameString/WriteMatrixIONumberSelect used to survive here
    too (4 dangling total): DTP3's SetMatrixIONameString/SetMatrixIONumberSelect
    gate their Emulated pre-write on a plain length/range check, not
    __SafeToSet, so the old guard-shaped rule missed them. The generalised
    call-shape rule (see test_emulated_prewrite_dropped_in_dtp3_length_check_guard)
    drops both of those standalone pre-write statements. What was left was the
    two cross-command Read<X>(..., 'Emulated') calls in SetMatrixIONameCommand
    that compose the NI/NO query string from GC-only scratch state Extron
    hand-restructured away in the shipped module -- R37 keeps
    ReadMatrixIONameString/ReadMatrixIONumberSelect (backed by
    self._emulated_status) instead of deleting them, since SetMatrixIONameCommand
    still calls both in a value context, so this is now empty too. This
    generated module's SetMatrixIONameCommand diverges from the shipped one
    (which reads Number/Name from `qualifier` instead -- a genuine Extron
    command-surface consolidation, still not derivable from the .pkp alone;
    see the gc-emulated-wrapper-kept-as-scratch-store residual)."""
    r = pkp2cs.translate_pkp(DTP3_PKP)[0]
    assert _dangling_names(r) == [], _dangling_names(r)


def test_dangling_self_call_count_regression_avx():
    r = pkp2cs.translate_pkp(AVX_PKP)[0]
    assert _dangling_names(r) == [], _dangling_names(r)


def test_dangling_self_call_count_regression_samsung_serial():
    r = pkp2cs.translate_job(
        [j for j in pkp2cs.discover_jobs(SAMSUNG_PKP) if j.script_file_name == "smsg_10_6738_serial.py"][0])
    assert _dangling_names(r) == [], _dangling_names(r)


def test_dangling_self_call_count_regression_samsung_ethernet():
    """ReadMultiviewString is now kept (see
    test_samsung_ethernet_job_reports_dangling_reference_as_residual), so this
    is empty rather than ["ReadMultiviewString"]."""
    r = pkp2cs.translate_job(
        [j for j in pkp2cs.discover_jobs(SAMSUNG_PKP) if j.script_file_name == "smsg_10_6738_ethernet.py"][0])
    assert _dangling_names(r) == [], _dangling_names(r)


# --- regression: never emit a wire string absent from the source package ---

def test_invented_wire_strings_are_detected():
    """A generated module must not send bytes that appear nowhere in the .pkp it
    came from. The SIS-dialect helper template was injecting Extron's own
    'w0echo'/'w3cv' handshake into third-party Biamp and Clock Audio modules --
    fabricated wire content aimed at devices that do not speak SIS."""
    origin = "class D(BaseDriver):\n    def x(self):\n        self.Send('REAL\\r')\n"
    generated = ("class DeviceClass:\n"
                 "    def y(self):\n"
                 "        self.Send('REAL\\r')\n"
                 "        self.Send('w0echo\\r\\n')\n")
    invented = pkp2cs.find_invented_wire_strings(generated, origin)
    assert any("w0echo" in i for i in invented), invented
    assert not any("REAL" in i for i in invented), invented


def test_no_invented_strings_when_all_come_from_origin():
    origin = "class D(BaseDriver):\n    def x(self):\n        self.Send('REAL\\r')\n"
    generated = "class DeviceClass:\n    def y(self):\n        self.Send('REAL\\r')\n"
    assert pkp2cs.find_invented_wire_strings(generated, origin) == []


def test_biamp_and_clockaudio_do_not_receive_sis_handshake():
    """Integration: the two third-party packages that exposed this."""
    for folder, pkpname in [("Tesira", "biam_25_150_v1_20_0.pkp"),
                            ("ClockAudio", "clau_25_1777_v1_3_0.pkp")]:
        pkp = os.path.join(REPO_ROOT, "samples", folder, "pkp", pkpname)
        if not os.path.exists(pkp):
            continue
        for r in pkp2cs.translate_pkp(pkp):
            txt = r["source"] or ""
            assert "w0echo" not in txt, "%s still emits the SIS handshake" % pkpname
            assert "w3cv" not in txt, "%s still emits the SIS handshake" % pkpname


def test_sis_dialect_requires_sis_evidence_in_the_package():
    """The handshake template is only correct for devices that actually speak SIS.
    Classifying every Ethernet device as SIS made the translator emit Extron's
    'w0echo'/'w3cv' to third-party Biamp and Clock Audio hardware."""
    head = ("from Extron2.BaseDriver import BaseDriver\n"
            "class w(BaseDriver):\n"
            "    def __init__(self, configs):\n"
            "        super().__init__(configs)\n"
            "        self.Commands = {}\n")
    without = head + "    def ping(self):\n        self.Send('QUERY\\r')\n"
    assert _analyse_src(without).dialect == "ethernet"

    withsis = head + "    def ping(self):\n        self.Send('w0echo\\r\\n')\n"
    assert _analyse_src(withsis).dialect == "sis_ethernet"


def test_non_sis_ethernet_reports_untranslated_handshake():
    """Omitting the handshake is correct; omitting it SILENTLY is not.

    R17: Biamp's Tesira package declares BOTH a SerialProtocolAsset and an
    EthernetProtocolAsset per model (find_protocol_assets now sees both,
    where the old find_protocol_asset saw only whichever one happened to be
    first and silently lost the other) -- consistent with Tesira DSPs
    genuinely supporting either RS-232 or Ethernet/SSH control. The 'serial'
    branch's elif precedence now wins as the PRIMARY dialect (it used to be
    'ethernet' when only the first-seen asset was visible), so the specific
    residual this test originally keyed on --
    connection-handshake-not-translated, only ever emitted on the primary
    'ethernet'-dialect path -- no longer fires here; the equivalent guarantee
    (no fabricated SIS handshake anywhere in the module) is checked directly,
    and R17's own secondary-mixin residual takes its place."""
    pkp = os.path.join(REPO_ROOT, "samples", "Tesira", "pkp", "biam_25_150_v1_20_0.pkp")
    if not os.path.exists(pkp):
        return
    r = pkp2cs.translate_pkp(pkp)[0]
    assert r["dialect"] == "serial", r["dialect"]
    reasons = {x["reason"] for x in r["residuals"]}
    assert "model-declares-multiple-transports" in reasons, sorted(reasons)
    assert "ethernet-connection-settings-not-recoverable" in reasons, sorted(reasons)
    assert "w0echo" not in r["source"] and "w3cv" not in r["source"], "fabricated SIS handshake"
    assert "class EthernetClass" in r["source"]
    assert "class SerialClass" in r["source"]


def test_emulated_prewrite_dropped_when_passed_as_keyword():
    """Reviewer-found boundary: the rule keyed on 'Emulated' being the last
    POSITIONAL argument, so a generator emitting context='Emulated' would leave
    the call while its definition was still deleted -- the same dangling-reference
    bug class. Not present in any of the six packages; closed before a seventh
    device reintroduces it silently."""
    src = ("from Extron2.BaseDriver import BaseDriver\n"
           "class w(BaseDriver):\n"
           "    def __init__(self, configs):\n"
           "        super().__init__(configs)\n"
           "        self.Commands = {}\n"
           "    def _cmd_SetFoo(self, value, qualifier):\n"
           "        if 0 <= len(value) <= 30:\n"
           "            self.WriteFoo(value, qualifier, context='Emulated')\n"
           "            self.__SetHelper('Foo', 'CMD', value, qualifier)\n")
    a = _analyse_src(src)
    body = ast.unparse(a.methods["SetFoo"]) if "SetFoo" in a.methods else ""
    assert "WriteFoo" not in body, body


# --------------------------------------------------------------------------
# R16: EthernetClass Protocol/ServicePort read from the package's own
# EthernetProtocolAsset (_port + _compatibility) instead of always the
# neutral extronlib defaults.
# --------------------------------------------------------------------------

def test_ethernet_protocol_info_reads_port_and_compatibility():
    """Unit: ethernet_protocol_info resolves _compatibility through Extron's
    own ProtocolCompatibilityFlags enum (ground truth:
    experiments/protocol_assets/SURVEY.md)."""
    def enum_ref(oid):
        return {"$ref": oid}
    objs = {
        1: {"class": "Extron.Configuration.Core.Assets.Protocols.EthernetProtocolAsset",
            "members": {"_port": 3629, "_compatibility": enum_ref(2)}},
        2: {"members": {"value__": 16}},  # Ethernet_Telnet
    }
    protocol, port, compat = pkp2cs.ethernet_protocol_info(objs, objs[1])
    assert (protocol, port, compat) == ("TCP", 3629, 16)


def test_ethernet_protocol_info_dante_and_roomscheduling_stay_unmapped():
    """1024/2048 are always _port=0 in the corpus (SURVEY.md) -- auxiliary
    feature flags, not a distinct wire transport; protocol stays None so the
    EthernetClass resolver falls back rather than fabricating a protocol
    string extronlib doesn't accept."""
    objs = {
        1: {"class": "Extron.Configuration.Core.Assets.Protocols.EthernetProtocolAsset",
            "members": {"_port": 0, "_compatibility": {"$ref": 2}}},
        2: {"members": {"value__": 1024}},  # Ethernet_Dante
    }
    protocol, port, compat = pkp2cs.ethernet_protocol_info(objs, objs[1])
    assert protocol is None and port == 0 and compat == 1024


def test_resolve_ethernet_class_defaults_uses_resolved_port_and_protocol():
    """Unit: analyse()'s ethernet-dialect EthernetClass mixin picks up the
    real (protocol, port) instead of the neutral ('TCP', 0) default, and adds
    NO ethernet-connection-settings-not-recoverable residual when it does."""
    a = pkp2cs.Analysis()
    a.ethernet_info = ("UDP", 49494, 32)
    protocol, port = pkp2cs._resolve_ethernet_class_defaults(a)
    assert (protocol, port) == ("UDP", 49494)
    assert not any(r["reason"] == "ethernet-connection-settings-not-recoverable" for r in a.residuals)


def test_resolve_ethernet_class_defaults_falls_back_with_precise_reason():
    """compat=512 (SSH) resolves to SSHClass, not EthernetClass -- using it
    here would be the wrong mixin class, not a correct substitution, so this
    must fall back to the neutral default and say precisely why."""
    a = pkp2cs.Analysis()
    a.ethernet_info = ("SSH", 22, 512)
    protocol, port = pkp2cs._resolve_ethernet_class_defaults(a)
    assert (protocol, port) == ("TCP", 0)
    matches = [r for r in a.residuals if r["reason"] == "ethernet-connection-settings-not-recoverable"]
    assert len(matches) == 1, a.residuals
    assert "SSHClass" in matches[0]["detail"]


def test_resolve_ethernet_class_defaults_none_info_falls_back():
    a = pkp2cs.Analysis()
    a.ethernet_info = None
    protocol, port = pkp2cs._resolve_ethernet_class_defaults(a)
    assert (protocol, port) == ("TCP", 0)
    matches = [r for r in a.residuals if r["reason"] == "ethernet-connection-settings-not-recoverable"]
    assert len(matches) == 1 and "no EthernetProtocolAsset" in matches[0]["detail"]


def test_clockaudio_ethernet_class_matches_shipped_udp_port():
    """Integration: shipped ClockAudio (clau_dsp_CDT100_v1_0_3_0.py:421) uses
    EthernetClass(Protocol='UDP', ServicePort=49494) -- not extronlib's
    neutral ('TCP', 0) default. Confirms R16's fix reproduces the real,
    shipped, oracle-matching value straight from the package's own
    EthernetProtocolAsset (_compatibility=32 Ethernet_UDP, _port=49494),
    with no residual saying it couldn't be found."""
    if not os.path.exists(CLOCKAUDIO_PKP):
        return
    r = pkp2cs.translate_pkp(CLOCKAUDIO_PKP)[0]
    assert r["dialect"] == "ethernet", r["dialect"]
    assert "Protocol='UDP', ServicePort=49494" in r["source"], r["source"]
    reasons = {x["reason"] for x in r["residuals"]}
    assert "ethernet-connection-settings-not-recoverable" not in reasons, sorted(reasons)


def test_dsc_sshclass_port_stays_neutral_matching_shipped_oracle():
    """R16 deliberately does NOT thread the resolved _port into SSHClass:
    both shipped DSC (extr_scaler_DSC_12G_HD_A_v1_0_0_0.py:1218) and shipped
    DTP3 (extr_matrix_DTP3_CrossPoint_42_Series_v1_2_0_0.py:1315) leave
    ServicePort=0 even though DSC's own package resolves to
    _compatibility=Ethernet_SSH(512), _port=22023 -- extronlib's own
    EthernetClientInterface(Protocol='SSH', ServicePort=0) auto-selects the
    standard SSH port, so 0 is the oracle-matching value here, not a gap."""
    jobs = pkp2cs.discover_jobs(DSC_PKP)
    assert jobs[0].models[0].ethernet_info == ("SSH", 22023, 512), jobs[0].models[0].ethernet_info
    r = pkp2cs.translate_pkp(DSC_PKP)[0]
    assert r["dialect"] == "sis_ethernet", r["dialect"]
    assert "ServicePort=0" in r["source"]
    assert "ServicePort=22023" not in r["source"]


# --------------------------------------------------------------------------
# R17: find_protocol_assets returns every declared protocol asset, not just
# the first one a single-child-wrapper assumption could see.
# --------------------------------------------------------------------------

def _fake_wrapped_protocol_model(concrete_children):
    """Build the minimal raw-NRBF (objs, model) pair
    child_collection_items/find_protocol_assets need: model -> one
    AssetBase`1[[IProtocolAsset]] wrapper -> `concrete_children` (a list of
    already-concrete protocol-asset dicts)."""
    objs = {}
    next_id = [1]

    def alloc(v):
        oid = next_id[0]
        next_id[0] += 1
        objs[oid] = v
        return oid

    def make_collection(item_ids):
        items_id = alloc({"$type": "ArraySinglePrimitive", "items": [{"$ref": i} for i in item_ids]})
        list_id = alloc({"members": {"_items": {"$ref": items_id}, "_size": len(item_ids)}})
        coll_id = alloc({"members": {"Collection`1+items": {"$ref": list_id}}})
        return coll_id

    child_ids = [alloc(c) for c in concrete_children]
    wrapper_coll_id = make_collection(child_ids)
    wrapper_id = alloc({
        "class": "Extron.Configuration.Core.Assets.AssetBase`1[[Extron.Configuration.Contracts."
                 "Assets.Protocols.IProtocolAsset, Extron.Configuration.Contracts]]",
        "members": {"_internalChildCollection": {"$ref": wrapper_coll_id}},
    })
    model_coll_id = make_collection([wrapper_id])
    model = {"members": {"_internalChildCollection": {"$ref": model_coll_id}}}
    return objs, model


def test_find_protocol_assets_single_child_matches_old_behaviour():
    objs, model = _fake_wrapped_protocol_model([
        {"class": "Extron.Configuration.Core.Assets.Protocols.EthernetProtocolAsset", "members": {}},
    ])
    assets = pkp2cs.find_protocol_assets(objs, model)
    assert len(assets) == 1
    assert assets[0]["class"].endswith("EthernetProtocolAsset")
    assert pkp2cs.find_protocol_asset(objs, model) is assets[0]


def test_find_protocol_assets_returns_both_when_wrapper_holds_two():
    """R17: the 1 Beyond PTZ-IP12/IP20 shape reproduced synthetically -- one
    IProtocolAsset wrapper, two concrete children. The old find_protocol_asset
    (unwrap_generic_wrapper requiring exactly 1 child) returned None here;
    find_protocol_assets returns both."""
    objs, model = _fake_wrapped_protocol_model([
        {"class": "Extron.Configuration.Core.Assets.Protocols.EthernetProtocolAsset", "members": {}},
        {"class": "Extron.Configuration.Core.Assets.Protocols.SerialProtocolAsset", "members": {}},
    ])
    assets = pkp2cs.find_protocol_assets(objs, model)
    classes = sorted(a["class"].rsplit(".", 1)[-1] for a in assets)
    assert classes == ["EthernetProtocolAsset", "SerialProtocolAsset"], classes
    # old single-asset accessor must not silently return None any more
    assert pkp2cs.find_protocol_asset(objs, model) is not None


def test_find_protocol_assets_empty_wrapper_returns_empty_list():
    objs, model = _fake_wrapped_protocol_model([])
    assert pkp2cs.find_protocol_assets(objs, model) == []
    assert pkp2cs.find_protocol_asset(objs, model) is None


def test_ptz_ip12_models_resolve_both_protocol_assets():
    """Integration: the real donor package (ROADMAP R17, findings/19-three-
    questions.md section 2, SURVEY.md's "3,455 of 8,027 models resolve to no
    protocol asset" finding). Both models' single IProtocolAsset wrapper
    holds an EthernetProtocolAsset AND a SerialProtocolAsset; before this fix
    protocol_class was None for both."""
    if not os.path.exists(PTZ_IP12_PKP):
        return
    jobs = pkp2cs.discover_jobs(PTZ_IP12_PKP)
    assert len(jobs) == 1, jobs
    job = jobs[0]
    assert len(job.models) == 2, job.models
    for m in job.models:
        classes = sorted(c.rsplit(".", 1)[-1] for c in m.protocol_classes)
        assert classes == ["EthernetProtocolAsset", "SerialProtocolAsset"], (m.name, classes)
        assert m.protocol_class is not None


def test_ptz_ip12_translates_with_both_transport_mixins_and_no_dangling_calls():
    """Integration: end to end, both wiring classes are emitted, the
    dual-transport residual explains why, and the module is still valid,
    dangling-call-free Python."""
    if not os.path.exists(PTZ_IP12_PKP):
        return
    jobs = pkp2cs.discover_jobs(PTZ_IP12_PKP)
    result = pkp2cs.translate_job(jobs[0])
    assert result["source"] is not None
    src = result["source"]
    ast.parse(src)  # syntactically valid
    assert "class EthernetClass" in src or "class SSHClass" in src, src
    assert "class SerialClass" in src, src
    reasons = {x["reason"] for x in result["residuals"]}
    assert "model-declares-multiple-transports" in reasons, sorted(reasons)
    assert not any(x["reason"] == "model-has-no-protocol-asset" for x in result["residuals"])
    assert pkp2cs.find_dangling_self_calls(src) == []
    import py_compile
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as f:
        f.write(src.encode("utf-8"))
        tmp_path = f.name
    try:
        py_compile.compile(tmp_path, doraise=True)
    finally:
        os.remove(tmp_path)


def test_ptz_ip12_generated_module_imports_what_it_uses():
    """The generated module used `pack` 19 times with no import - a NameError
    on the processor that neither the wire table nor the dangling self.X()
    check could see. The source's own `from struct import pack` is carried."""
    if not os.path.exists(PTZ_IP12_PKP):
        return
    src = pkp2cs.translate_job(pkp2cs.discover_jobs(PTZ_IP12_PKP)[0])["source"]
    assert "from struct import pack" in src, src[:600]
    assert pkp2cs.find_unresolved_globals(src) == [], pkp2cs.find_unresolved_globals(src)


def test_bare_re_compile_import_is_carried_and_gc_runtime_imports_are_not():
    """`from re import compile` was dropped while the calls stayed, so they
    reached the builtin compile() and registered no response pattern (found by
    ROADMAP R36). The GC runtime's own packages (Extron, Extron2) do not exist
    under ControlScript and must not be carried."""
    src = ("from Extron2.BaseDriver import BaseDriver\n"
           "import Extron.Timer as CallBackTimer\n"
           "from Extron import Version\n"
           "from re import compile, search\n"
           "import time\n"
           "class Widget(BaseDriver):\n"
           "    def __init__(self, configs):\n"
           "        super().__init__(configs)\n"
           "        self.Commands = {}\n"
           "        self.AddMatchString(compile(b'X'), self.__MatchX, None)\n")
    a = pkp2cs.analyse(src, [])
    assert "from re import compile, search" in a.carried_imports, a.carried_imports
    assert "import time" in a.carried_imports, a.carried_imports
    assert not any("Extron" in line for line in a.carried_imports), a.carried_imports


def test_unresolved_global_is_detected():
    src = ("import time\n"
           "class DeviceClass:\n"
           "    def SetX(self, value, qualifier):\n"
           "        cmd = pack('>B', value)\n"
           "        time.sleep(0)\n")
    assert pkp2cs.find_unresolved_globals(src) == ["pack"]


def test_no_unresolved_globals_when_everything_is_bound():
    src = ("from struct import pack\n"
           "class DeviceClass:\n"
           "    def SetX(self, value, qualifier):\n"
           "        try:\n"
           "            cmd = pack('>B', value)\n"
           "        except ValueError as e:\n"
           "            print(e, [n for n in range(3)])\n")
    assert pkp2cs.find_unresolved_globals(src) == []


_MODULE_LEVEL_SRC = '''
from Extron2.BaseDriver import BaseDriver
import Extron.Timer as CallBackTimer
from struct import pack
FIN = 0x80
UNUSED = 1
EXP_TABLE = [0] * 4
for i in range(4):
    EXP_TABLE[i] = 1 << i
def _mask(m, d):
    return bytes(x ^ m for x in d)
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Status': {}},
        }
    def _cmd_SetFoo(self, value, qualifier):
        i = EXP_TABLE[value]
        frame = _mask(FIN, pack('>B', i))
        self.page = Scroller([], 4)
        self.Timer = CallBackTimer.Timer(1.0, self.OnConnected, None, False, [])
        self.__SetHelper('Foo', frame, value, qualifier)
class Scroller:
    def __init__(self, items, window):
        self.items = items
class ExtronTime(float):
    pass
'''


def _translate_src(src, models=SIS_MODEL):
    return pkp2cs.translate_job(pkp2cs.TranslationJob("w.py", src, models))


def test_module_level_definitions_the_module_reads_are_carried():
    """Helper classes, constants and functions outside the driver class were
    dropped wholesale, so every read of one was a NameError on the processor:
    52 of the 77 names the translation left unbound across finding 14's 314
    packages (a WebSocket driver's FIN/OPCODE/_mask, the Scroller and
    Directory helpers). They are plain Python and are carried verbatim - but
    only the ones the generated module reads, where the source put them."""
    res = _translate_src(_MODULE_LEVEL_SRC)
    out = res["source"]
    compile(out, "<generated>", "exec")
    for needed in ("FIN = 128", "def _mask(m, d):", "class Scroller:",
                   "EXP_TABLE = [0] * 4", "EXP_TABLE[i] = 1 << i"):
        assert needed in out, (needed, out)
    assert "UNUSED" not in out, "an unread constant was carried"
    assert "ExtronTime" not in out, "GC's dual-status helper class was carried"
    assert out.index("FIN = 128") < out.index("class DeviceClass")
    assert out.index("EXP_TABLE = [0] * 4") < out.index("EXP_TABLE[i] = 1 << i") \
        < out.index("class DeviceClass"), "the table's fill loop must follow its definition"
    assert out.index("class Scroller:") > out.index("class DeviceClass"), \
        "a helper defined after the driver class stays after it"
    carried = [r for r in res["residuals"] if r["reason"] == "module-level-definition-carried"]
    assert len(carried) == 1 and "Scroller" in carried[0]["detail"], res["residuals"]


def test_gc_runtime_names_stay_unbound_and_say_why():
    """CallBackTimer is `import Extron.Timer`: a GC runtime API with no
    ControlScript counterpart and no evidenced mapping. It stays an
    unresolved-global-name residual, and the residual names the import."""
    res = _translate_src(_MODULE_LEVEL_SRC)
    assert pkp2cs.find_unresolved_globals(res["source"]) == ["CallBackTimer"]
    unbound = [r for r in res["residuals"] if r["reason"] == "unresolved-global-name"]
    assert len(unbound) == 1, unbound
    assert "import Extron.Timer as CallBackTimer" in unbound[0]["detail"], unbound


def test_a_defect_in_the_source_is_reported_as_one():
    """Four of the 81 unbound names were typos in Extron's own scripts
    (`seld`, `Self`, ...). They are carried faithfully and the residual says
    the package itself is at fault."""
    src = _MODULE_LEVEL_SRC.replace("self.page = Scroller([], 4)",
                                    "seld.page = Scroller([], 4)")
    res = _translate_src(src)
    unbound = {r["detail"].split()[3]: r["detail"] for r in res["residuals"]
               if r["reason"] == "unresolved-global-name"}
    assert "seld" in unbound, unbound
    assert "unbound in the embedded script too" in unbound["seld"], unbound


def test_addmatchstring_local_is_carried_with_its_registration():
    """ATUC50: `du_talk_status_regex = br'...'` then
    `self.AddMatchString(compile(du_talk_status_regex), ...)`. The
    registrations are regenerated from the calls alone, so the local was lost -
    a NameError in __init__. Extron's shipped ATUC50 keeps the assignment
    directly above its registration; so does the generated module now."""
    src = '''
from Extron2.BaseDriver import BaseDriver
from re import compile
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': False, 'Update': True, 'Status': {}},
        }
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'A'), self.__MatchFoo, None)
            head = br'gtalk '
            talk_regex = head + br'(\\d+)\\r'
            self.AddMatchString(compile(talk_regex), self.__MatchFoo, None)
    def __MatchFoo(self, match, qualifier):
        self.WriteStatus('Foo', match.group(1).decode(), None)
'''
    res = _translate_src(src)
    out = res["source"]
    assert pkp2cs.find_unresolved_globals(out) == [], pkp2cs.find_unresolved_globals(out)
    order = [out.index(s) for s in ("compile(b'A')", "head = b'gtalk '",
                                    "talk_regex = head +", "compile(talk_regex)")]
    assert order == sorted(order), out


_STATIC_SRC = '''
from Extron2.BaseDriver import BaseDriver
from re import compile
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Status': {}},
        }
    @staticmethod
    def __constraint_checker(*value_dicts):
        return all(d['Min'] <= d['Value'] <= d['Max'] for d in value_dicts)
    unwanted_chars = compile(r'[/& ]').search
    @staticmethod
    def __check_instance_tag(inp_string, search_unwanted=unwanted_chars):
        return inp_string if not search_unwanted(inp_string) else None
    @property
    def InvokeID(self):
        return 7
    def _cmd_SetFoo(self, value, qualifier):
        tag = self.__check_instance_tag(qualifier['Instance Tag'])
        if tag and self.__constraint_checker({'Min': 0, 'Value': value, 'Max': 9}):
            self.__SetHelper('Foo', '{} {}'.format(tag, value), value, qualifier)
'''


def test_static_methods_and_class_attributes_survive_and_run():
    """ktek DM8000: every command calls self.__check_instance_tag(...) and
    self.__constraint_checker(...), both @staticmethod. The translator
    dropped every decorator, so self arrived as the first argument - a
    TypeError on every command - and dropped the class attribute the default
    argument reads, so the module could not even be imported. Neither the wire
    table nor the resolvability checks can see the first; this test runs it."""
    res = _translate_src(_STATIC_SRC)
    out = res["source"]
    assert pkp2cs.find_unresolved_globals(out) == [], pkp2cs.find_unresolved_globals(out)
    assert out.count("@staticmethod") == 2 and "@property" in out, out
    assert out.index("unwanted_chars = compile") < out.index("def __init__"), out
    # Execute the class against a stub extronlib, then call the helpers the
    # way the command bodies do.
    import types
    stub = types.ModuleType("extronlib")
    stubs = {"extronlib": stub}
    for sub, names in (("interface", ("SerialInterface", "EthernetClientInterface")),
                       ("system", ("Wait", "ProgramLog"))):
        m = types.ModuleType("extronlib." + sub)
        for n in names:
            setattr(m, n, type(n, (), {}))
        setattr(stub, sub, m)
        stubs["extronlib." + sub] = m
    saved = {k: sys.modules.get(k) for k in stubs}
    sys.modules.update(stubs)
    try:
        ns = {}
        exec(compile(out, "<generated>", "exec"), ns)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    dev = ns["DeviceClass"].__new__(ns["DeviceClass"])
    assert dev._DeviceClass__check_instance_tag("Mic1") == "Mic1"
    assert dev._DeviceClass__check_instance_tag("Mic 1") is None
    assert dev._DeviceClass__constraint_checker({"Min": 0, "Value": 3, "Max": 9})
    assert dev.InvokeID == 7


def test_unknown_decorator_is_reported_not_kept():
    src = _STATIC_SRC.replace("@property", "@functools.lru_cache()")
    res = _translate_src(src)
    dropped = [r for r in res["residuals"] if r["reason"] == "method-decorator-dropped"]
    assert len(dropped) == 1 and "lru_cache" in dropped[0]["detail"], res["residuals"]
    assert "lru_cache" not in res["source"]


def test_helper_extra_parameter_is_kept_in_the_fixed_signature():
    """ktek DM8000's GC __SetHelper takes queryDisallowTime=0 and some commands
    pass it; the four-parameter fixed template made those Set calls raise
    TypeError - found by executing the module (ROADMAP R13), invisible to every
    static check. Extron's shipped modules with that signature keep the
    parameter and ignore it."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Status': {}},
        }
    def _cmd_SetFoo(self, value, qualifier):
        self.__SetHelper('Foo', 'F{}'.format(value), value, qualifier, 3)
    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.QueryDelayTimerIsRunning():
            self.StartQueryDelayTimer(queryDisallowTime)
        self.Send(commandstring)
'''
    res = _translate_src(src)
    tree = ast.parse(res["source"])
    helper = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "__SetHelper")
    names = [p.arg for p in helper.args.args]
    assert names == ["self", "command", "commandstring", "value", "qualifier",
                     "queryDisallowTime"], names
    assert ast.unparse(helper.args.defaults[-1]) == "0"
    assert "QueryDelayTimerIsRunning" not in res["source"]
    carried = [r for r in res["residuals"] if r["reason"] == "helper-signature-carried"]
    assert len(carried) == 1 and "queryDisallowTime=0" in carried[0]["detail"], res["residuals"]
    assert pkp2cs.find_call_arity_mismatches(res["source"]) == []


def test_call_arity_mismatch_is_detected():
    src = ("class DeviceClass:\n"
           "    def __SetHelper(self, command, commandstring, value, qualifier):\n"
           "        pass\n"
           "    def Opt(self, a, b=1, *, c=2):\n"
           "        pass\n"
           "    @staticmethod\n"
           "    def Pure(x):\n"
           "        return x\n"
           "    def SetFoo(self, value, qualifier):\n"
           "        self.__SetHelper('Foo', 'F', value, qualifier, 3)\n"
           "        self.__SetHelper('Foo', 'F', value, qualifier)\n"
           "        self.Opt(1)\n"
           "        self.Opt(1, 2, c=3)\n"
           "        self.Opt(1, a=2)\n"
           "        self.Opt(1, d=2)\n"
           "        self.Pure(1)\n"
           "        self.Pure()\n"
           "        self.Opt(*[1])\n"
           "        self.Undefined(1, 2, 3)\n"
           "        self.Send('x', pacing=0.1)\n"
           "        self.Send('x')\n"
           "        self.SendAndWait('x', 1, deliTag=b'\\r')\n"
           "        self.SendAndWait('x')\n"
           "class SerialClass(DeviceClass):\n"
           "    def Error(self, message):\n"
           "        pass\n"
           "    def Discard(self, message):\n"
           "        self.Error([message], 1)\n")
    assert pkp2cs.find_call_arity_mismatches(src) == [
        ("Error", 2), ("Opt", 2), ("Pure", 0), ("Send", 2), ("SendAndWait", 1),
        ("__SetHelper", 5)], pkp2cs.find_call_arity_mismatches(src)


def test_dtp3_send_pacing_is_dropped():
    """DTP3's SetMatrixIONameStatus called self.Send(query, pacing=0.1), a GC
    BaseDriver option extronlib's Send does not take: RefreshMatrixIONames
    raised TypeError when executed (ROADMAP R13). Extron's shipped DTP3 sends
    without it."""
    res = pkp2cs.translate_job(pkp2cs.discover_jobs(DTP3_PKP)[0])
    assert "pacing" not in res["source"]
    assert pkp2cs.find_call_arity_mismatches(res["source"]) == []
    assert any(r["reason"] == "gc-send-pacing-dropped" for r in res["residuals"])


_THROTTLE_SRC = '''
from Extron2.BaseDriver import BaseDriver
import time
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': False, 'Update': True, 'Status': {}},
            'Bar': {'Set': False, 'Update': True, 'Status': {}},
            'Seq': {'Set': False, 'Update': True, 'Status': {}},
        }
        self.lastFooUpdate = 0
        self.lastBarUpdate = {}
        self.last_sequence_reset = 0
        self.seq = 0
    def _cmd_UpdateFoo(self, value, qualifier):
        ctime = time.monotonic()
        if ctime - self.lastFooUpdate > 4:
            self.lastFooUpdate = ctime
            self.__UpdateHelper('Foo', 'wQFOO\\r', value, qualifier)
        else:
            self.Discard('Device Is Busy')
    def _cmd_UpdateBar(self, value, qualifier):
        ctime = time.monotonic()
        if ctime - self.lastBarUpdate.get(qualifier['Channel'], 0) > 2:
            self.lastBarUpdate[qualifier['Channel']] = ctime
            self.__UpdateHelper('Bar', 'wQBAR\\r', value, qualifier)
    def _cmd_UpdateSeq(self, value, qualifier):
        ctime = time.monotonic()
        if ctime - self.last_sequence_reset > 10:
            self.seq = 0
        else:
            self.seq += 1
        self.__UpdateHelper('Seq', 'wQSEQ{}\\r'.format(self.seq), value, qualifier)
'''


def test_gc_query_throttle_is_dropped_whole_not_half():
    """Every write of a self.last* timer was dropped while the guard reading it
    stayed - an AttributeError on every such Update (DSC's LogoAvailability,
    found by executing the module, ROADMAP R13). The throttle shape - one
    comparison, no else or a lone Discard - now becomes its body, as in
    Extron's shipped DSC, and a per-qualifier timer's subscript store goes with
    the rest. A guard with a real else stays, and is reported."""
    res = _translate_src(_THROTTLE_SRC)
    out = res["source"]
    compile(out, "<generated>", "exec")
    assert "Device Is Busy" not in out, out
    assert "self.lastFooUpdate" not in out and "self.lastBarUpdate" not in out, out
    assert "'wQFOO\\r'" in out and "'wQBAR\\r'" in out, out
    assert "self.last_sequence_reset" in out and "self.seq += 1" in out, \
        "a throttle with a real else branch must not be rewritten"
    dropped = [r for r in res["residuals"] if r["reason"] == "gc-throttle-guard-dropped"]
    assert len(dropped) == 2, dropped
    assert pkp2cs.find_unassigned_self_attributes(out) == ["last_sequence_reset"]
    unassigned = [r for r in res["residuals"] if r["reason"] == "unassigned-self-attribute"]
    assert len(unassigned) == 1 and "code the translation dropped" in unassigned[0]["detail"], \
        unassigned


def test_unassigned_self_attribute_is_detected():
    src = ("class DeviceClass:\n"
           "    ready = True\n"
           "    def __init__(self):\n"
           "        self.counter = 0\n"
           "        setattr(self, 'Mode2', 'x')\n"
           "    def SetThing(self, value, qualifier):\n"
           "        self.counter += 1\n"
           "        self.Send('user {}'.format(self.deviceUsername))\n"
           "        cb = self.WriteGoneWrapper\n"
           "        return self.ready, self.Mode2, self.Hostname, self.Hostname2\n"
           "class EthernetClass(DeviceClass):\n"
           "    def Other(self):\n"
           "        return self.SetThing, self.lastXUpdate\n"
           "class Helper:\n"
           "    def get(self):\n"
           "        return self.entries\n")
    assert pkp2cs.find_unassigned_self_attributes(src) == [
        "Hostname2", "WriteGoneWrapper", "deviceUsername", "lastXUpdate"], \
        pkp2cs.find_unassigned_self_attributes(src)


def test_dsc_generated_module_reads_no_unassigned_attribute():
    """DSC's LogoAvailability throttle, the first bug the execution harness
    found (ROADMAP R13)."""
    src = pkp2cs.translate_job(pkp2cs.discover_jobs(DSC_PKP)[0])["source"]
    assert pkp2cs.find_unassigned_self_attributes(src) == [], \
        pkp2cs.find_unassigned_self_attributes(src)


def test_method_references_held_as_values_survive_translation():
    """Dispatch tables in __init__ hold methods as values: nec's
    {'DeviceStatus': self._cmd_UpdateDeviceStatus} (the def is renamed; the
    reference was not) and yama's {'FaderLevel': self.WriteFaderLevel} (the
    wrapper was deleted). Both generated modules raised AttributeError while
    being constructed - found by executing them (ROADMAP R13)."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Fader': {'Set': True, 'Update': True, 'Status': {}},
        }
        self.Updaters = {'Fader': self._cmd_UpdateFader}
        self.Writers = {'Fader': self.WriteFader}
    def _cmd_SetFader(self, value, qualifier):
        self.WriteFader(value, qualifier, 'Emulated')
        self.__SetHelper('Fader', 'F{}'.format(value), value, qualifier)
    def _cmd_UpdateFader(self, value, qualifier):
        self.__UpdateHelper('Fader', 'QF', value, qualifier)
    def __MatchFader(self, match, qualifier):
        self.Writers['Fader'](match.group(1).decode(), None, 'Live')
    def WriteFader(self, value, qualifier, context):
        self.WriteStatusHelper('Fader', value, qualifier, context)
'''
    res = _translate_src(src)
    out = res["source"]
    assert "self._cmd_UpdateFader" not in out and "'Fader': self.UpdateFader" in out, out
    assert pkp2cs.find_unassigned_self_attributes(out) == [], \
        pkp2cs.find_unassigned_self_attributes(out)
    tree = ast.parse(out)
    wrapper = next(n for n in ast.walk(tree)
                   if isinstance(n, ast.FunctionDef) and n.name == "WriteFader")
    assert "self.WriteStatus('Fader', value, qualifier)" in ast.unparse(wrapper), \
        ast.unparse(wrapper)
    assert "'Emulated'" not in out, "the direct Emulated pre-write is still dropped"
    kept = [r for r in res["residuals"] if r["reason"] == "gc-write-wrapper-kept-for-value-reference"]
    assert len(kept) == 1, res["residuals"]


def test_verbose_only_sis_driver_gets_the_verbose_only_template():
    """8 of finding 14's packages set VerboseDisabled but never EchoDisabled,
    and the SIS template read both: an AttributeError on every Set and Update.
    Extron's shipped modules for them drop the echo branch and reset only
    VerboseDisabled on disconnect. The verbose string is the package's own:
    the synthetic driver below sends 'w3cv\\r'; the real AXI 22 AT D Plus
    package sends 'w3cv\\r\\n', although Extron's shipped module (an earlier
    revision) sends 'w3cv\\r'."""
    src = '''
from Extron2.BaseDriver import BaseDriver
class w(BaseDriver):
    def __init__(self, configs):
        super().__init__(configs)
        self.Commands = {
            'Foo': {'Set': True, 'Update': False, 'Status': {}},
        }
        self.VerboseDisabled = True
    def _cmd_SetFoo(self, value, qualifier):
        self.__SetHelper('Foo', 'F{}\\r'.format(value), value, qualifier)
    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.VerboseDisabled:
            self.Send('w3cv\\r')
        self.Send(commandstring)
    def __MatchVerboseMode(self, match, qualifier):
        self.VerboseDisabled = False
    def OnDisconnected(self):
        self.VerboseDisabled = True
'''
    res = _translate_src(src)
    out = res["source"]
    assert res["dialect"] == "sis_ethernet", res["dialect"]
    assert "EchoDisabled" not in out and "w0echo" not in out, out
    assert "self.Send('w3cv\\r')" in out and "'w3cv\\r\\n'" not in out, out
    ondisc = out[out.index("def OnDisconnected"):]
    assert "self.VerboseDisabled = True" in ondisc.split("def ", 2)[1], ondisc[:300]
    assert pkp2cs.find_unassigned_self_attributes(out) == [], \
        pkp2cs.find_unassigned_self_attributes(out)
    axi = os.path.join(REPO_ROOT, "corpus", "extron-driver3", "extr_31_17022_v1_0_1.pkp")
    if os.path.exists(axi):
        real = pkp2cs.translate_job(pkp2cs.discover_jobs(axi)[0])["source"]
        assert "EchoDisabled" not in real, "the verbose-only template reads no echo flag"
        assert "self.Send('w3cv\\r\\n')" in real, "the package's own string, not the template's"


def test_model_with_no_protocol_asset_gets_per_model_residual():
    """Unit: a model that truly declares no ProtocolAsset at all (not a
    lookup failure -- find_protocol_assets found nothing to walk) must say so
    by name, distinguishably from R17's fixed lookup-failure case."""
    models = [pkp2cs.ModelInfo("Widget A", "w.py", "w", None, protocol_classes=[])]
    src = ("from Extron2.BaseDriver import BaseDriver\n"
           "class w(BaseDriver):\n"
           "    def __init__(self, configs):\n"
           "        super().__init__(configs)\n"
           "        self.Commands = {}\n")
    a = pkp2cs.analyse(src, models)
    matches = [r for r in a.residuals if r["reason"] == "model-has-no-protocol-asset"]
    assert len(matches) == 1, a.residuals
    assert "Widget A" in matches[0]["detail"]


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
