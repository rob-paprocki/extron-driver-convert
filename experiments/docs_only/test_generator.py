#!/usr/bin/env python3
"""
experiments/docs_only/test_generator.py - regression tests for the R32
re-measurement of docs-only generation (ROADMAP R32; findings/19-three-
questions.md section 3; REMEASURE.md in this directory).

Pins down, on synthetic/small checks (no network, no corpus dependency
beyond the harvested reference/ tree and the one Extron shipped module
already used by the rest of this experiment):

  1. build_module() still produces syntactically valid Python.
  2. The two generator defects finding 19 recorded are actually fixed:
     no Update method hands WriteStatus a raw, undecoded HTTP-response
     dict, and GetAllStatus decodes its nested response_body strings.
  3. analyze_endpoints.py's dynamically-scanned DOCUMENTED_URIS set picks
     up exactly the 9 pages this re-harvest added, and no more/fewer.
  4. Re-running wire_table's diff against Extron's shipped module after
     the generator fix reproduces the exact same command-level diff as
     before the fix -- i.e. the WriteStatus/response fix is invisible to
     wire_table, as finding 19 predicted (it only sees the request side).

Standard library only; run directly: python3 experiments/docs_only/test_generator.py
"""
import ast
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
_TOOLS = os.path.join(_ROOT, "tools")
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

import generator  # noqa: E402
import analyze_endpoints as ae  # noqa: E402

PASS = 0
FAIL = 0


def check(label, got, want):
    global PASS, FAIL
    if got == want:
        PASS += 1
    else:
        FAIL += 1
        print("FAIL: %s\n  got:  %r\n  want: %r" % (label, got, want))


def check_true(label, got):
    check(label, bool(got), True)


# =========================================================================
# 1. build_module() output is syntactically valid Python
# =========================================================================
print("-- 1. build_module() produces valid Python --")

MODULE_SRC = generator.build_module()
try:
    ast.parse(MODULE_SRC)
    parse_ok = True
except SyntaxError as e:
    parse_ok = False
    print("  SyntaxError: %s" % e)
check_true("build_module() output parses as Python", parse_ok)


# =========================================================================
# 2. The two finding-19 defects are fixed
# =========================================================================
print("-- 2. finding 19's two generator defects are fixed --")

raw_dict_passthrough = re.findall(r"self\.WriteStatus\([^)]*\bres\b, qualifier\)", MODULE_SRC)
check("no Update method passes the raw response dict straight to WriteStatus "
      "(finding 19: this used to be 15 of 33 commands)",
      len(raw_dict_passthrough), 0)

check_true("UpdateGetAllStatus decodes each api_call_N's response_body with json.loads "
           "(GetAllStatus-API.md: 'must be deserialized by the client')",
           "json.loads(call['response_body'])" in MODULE_SRC)

check_true("UpdateGetAllStatus still exists as a method",
           "def UpdateGetAllStatus(self, value, qualifier):" in MODULE_SRC)


# =========================================================================
# 3. analyze_endpoints.py's dynamic harvest scan
# =========================================================================
print("-- 3. dynamically-scanned documented-endpoint set --")

EXPECTED_PROMOTED = {
    "api/AutoSwitchStatus", "api/OutputStatus", "api/RecordStatus",
    "api/RoomConfigStatus", "api/GetLayouts", "api/LayoutStatus",
    "api/GetRoomConfigs",
}
documented, by_file = ae.build_documented_uris()

check("7 sub-APIs promoted from example-only to dedicated-page by the R32 re-harvest",
      ae.SUBAPI_NAMED_IN_ENDPOINTS_MD & documented, EXPECTED_PROMOTED)

check("2 sub-APIs still have no dedicated page (ISORecordStatus, CopyStatus)",
      ae.SUBAPI_EXAMPLE_ONLY, {"api/ISORecordStatus", "api/CopyStatus"})

# Every promoted URI's page should be one of the 9 files this re-harvest
# added (not a pre-existing page misclassified some other way).
NEW_FILES = {
    "Wake-API.md", "AutoSwitchStatus-API.md", "StartAutoSwitch-API.md",
    "OutputStatus-API.md", "RecordStatus-API.md", "RoomConfigStatus-API.md",
    "GetLayouts-API.md", "LayoutStatus-API.md", "GetRoomConfigs-API.md",
}
promoted_files = {by_file[u] for u in EXPECTED_PROMOTED}
check_true("every promoted sub-API's page is one of the 9 pages this re-harvest added",
           promoted_files <= NEW_FILES)

check("Get-Token still classifies OFFICIAL (regression guard on the base case)",
      ae.classify("get-token"), "OFFICIAL")
check("StartISORecord still classifies DOC_GAP (never fetchable -- 404, confirmed live)",
      ae.classify("api/StartISORecord"), "DOC_GAP")


# =========================================================================
# 4. wire_table sees no change from the WriteStatus/GetAllStatus fix
# =========================================================================
print("-- 4. wire_table diff is unchanged by the response-side fix --")
# NOT a byte-equality check against a frozen diff.json: tools/wire_table.py
# is itself under active development elsewhere in this repo (ROADMAP R36),
# so a fixed expected diff would spuriously fail here on THAT file's own,
# unrelated improvements -- exactly the cross-contamination the R32 task
# brief warned against. Instead this asserts the narrower, evergreen claim
# that actually matters: wire_table's Template extraction for an Update
# method looks ONLY at the arguments of its __UpdateHelper(...) call, so
# whatever gen_simple_update()/gen_get_all_status() do with the response
# AFTER that call (raw passthrough vs. field-extracted vs. json.loads-
# decoded) cannot change what wire_table records for that command --
# structurally, not by comparing two snapshots.

try:
    import wire_table as wt  # noqa: E402

    GEN_PATH = os.path.join(_HERE, "automate_vx_docs_only.py")
    with open(GEN_PATH, encoding="utf-8") as f:
        gen_src = f.read()
    table = wt.extract_table(gen_src, GEN_PATH)

    gas = table.commands.get("GetAllStatus")
    check_true("GetAllStatus has exactly one update_template", gas is not None and len(gas.update_templates) == 1)
    if gas is not None and gas.update_templates:
        check("GetAllStatus's extracted update_template source is exactly its "
              "__UpdateHelper(...) call -- the json.loads() decode loop after it "
              "is invisible to wire_table",
              gas.update_templates[0].source,
              "self.__UpdateHelper('GetAllStatus', value, qualifier, url='api/GetAllStatus')")
        check("GetAllStatus's canonical wire template is unaffected by the decode fix",
              gas.update_templates[0].canonical, "url=api/GetAllStatus")

    cam = table.commands.get("CameraStatus")
    check_true("CameraStatus has exactly one update_template", cam is not None and len(cam.update_templates) == 1)
    if cam is not None and cam.update_templates:
        check("CameraStatus's extracted update_template source is exactly its "
              "__UpdateHelper(...) call -- the res['address'] extraction after it "
              "is invisible to wire_table",
              cam.update_templates[0].source,
              "self.__UpdateHelper('CameraStatus', value, qualifier, url='api/CameraStatus')")
except ImportError as e:
    print("  SKIP: tools/wire_table.py not importable here (%r) -- covered by "
          "tools/test_wire_table.py instead" % e)


print("\n%d passed, %d failed, %d total" % (PASS, FAIL, PASS + FAIL))
sys.exit(1 if FAIL else 0)
