#!/usr/bin/env python3
"""Mechanical endpoint-level cross-reference: extract every 'api/Xxx' / 'get-token'
URI literal referenced in (a) the generated module, (b) Extron's shipped module,
and classify against the documented endpoint set. Supplements wire_table's
command-NAME-keyed diff, which undercounts here because the two modules use
different command-naming abstractions for the same endpoints."""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = pathlib.Path(__file__).parent / "automate_vx_docs_only.py"
SHIP = ROOT / "samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py"

OFFICIAL_32 = {
    "get-token", "api/CallCameraPreset", "api/CameraStatus", "api/ChangeLayout",
    "api/CopyFiles", "api/ForceChangeRoomConfig", "api/GetActiveTalkers",
    "api/GetAllStatus", "api/GetCameras", "api/GetScenarios", "api/GoHome",
    "api/GoToScenario", "api/ImportCameraPresets", "api/Macro",
    "api/ManualSwitchCamera", "api/RecordingSpaceAvail", "api/Restart",
    "api/SaveCameraPreset", "api/ScenarioStatus", "api/ShotStatus", "api/Sleep",
    "api/StartOutput", "api/StartPT", "api/StartRecord", "api/StartStream",
    "api/StartZ", "api/StopOutput", "api/StopPT", "api/StopRecord",
    "api/StopStream", "api/StopZ", "api/StreamStatus",
}
SUBAPI_EXAMPLE_ONLY = {
    "api/AutoSwitchStatus", "api/OutputStatus", "api/ISORecordStatus",
    "api/RecordStatus", "api/CopyStatus", "api/GetLayouts", "api/LayoutStatus",
    "api/GetRoomConfigs", "api/RoomConfigStatus",
}
assert len(OFFICIAL_32) == 32, len(OFFICIAL_32)
assert len(SUBAPI_EXAMPLE_ONLY) == 9

def extract_uris(path):
    src = path.read_text()
    return set(re.findall(r"'(get-token|api/[A-Za-z]+)'", src))

gen_uris = extract_uris(GEN)
ship_uris = extract_uris(SHIP)

def classify(uri):
    if uri in OFFICIAL_32:
        return "OFFICIAL"
    if uri in SUBAPI_EXAMPLE_ONLY:
        return "EXAMPLE_ONLY"
    return "DOC_GAP"

print("=== generated module: endpoint URIs referenced ===")
for u in sorted(gen_uris):
    print(" ", u, classify(u))
print("count:", len(gen_uris))

print()
print("=== Extron shipped module: endpoint URIs referenced ===")
for u in sorted(ship_uris):
    print(" ", u, classify(u))
print("count:", len(ship_uris))

print()
print("=== classification of the diff ===")
only_ship = ship_uris - gen_uris
only_gen = gen_uris - ship_uris
both = gen_uris & ship_uris

print("-- in Extron shipped but NOT in generated (by URI) --")
for u in sorted(only_ship):
    print(" ", u, classify(u))

print("-- in generated but NOT in Extron shipped (by URI) --")
for u in sorted(only_gen):
    print(" ", u, classify(u))

print("-- in both (by URI) --")
for u in sorted(both):
    print(" ", u, classify(u))

official_covered_by_both = {u for u in both if u in OFFICIAL_32}
official_only_ship = {u for u in only_ship if u in OFFICIAL_32}
official_only_gen = {u for u in only_gen if u in OFFICIAL_32}
print()
print("official endpoint coverage: both=%d, extron-only=%d, generated-only(unimplemented-by-extron)=%d, total-official=%d"
      % (len(official_covered_by_both), len(official_only_ship), len(official_only_gen), len(OFFICIAL_32)))

subapi_covered_by_both = {u for u in both if u in SUBAPI_EXAMPLE_ONLY}
subapi_only_gen = {u for u in only_gen if u in SUBAPI_EXAMPLE_ONLY}
print("sub-api (example-only) coverage: both=%d, generated-only=%d, total-listed=%d"
      % (len(subapi_covered_by_both), len(subapi_only_gen), len(SUBAPI_EXAMPLE_ONLY)))

doc_gap_in_ship = {u for u in ship_uris if classify(u) == "DOC_GAP"}
print("DOC GAP (Extron calls, appears nowhere in corpus):", sorted(doc_gap_in_ship))
