#!/usr/bin/env python3
"""Quick probe: for each command in a donor, show the oid, defined-location,
and sharing of its _name and _scriptName strings."""
from __future__ import annotations
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def count_refs(trace, sid):
    return sum(1 for e in trace
               if e.get("kind") == "MemberReference" and e.get("idref") == sid)

def main():
    b = pb.PackageBuilder(DONOR)
    cg = pa.CommandGraph(b)
    print("cmd_id  scriptName             | field          sid    defined_in_cmd  total_refs  from_cmd")
    for script_name, cmd_id in sorted(cg.commands().items(), key=lambda t: t[1]):
        start, end = cg.walker.spans[cmd_id]
        slots = cg.walker.member_slots(cmd_id)
        for member in ("AssetBase+_name", "CommandAssetBase+_scriptName"):
            if member not in slots:
                continue
            ev = cg.b.trace[slots[member]]
            if ev["kind"] == "BinaryObjectString":
                sid = ev["object_id"]
            elif ev["kind"] == "MemberReference":
                sid = ev["idref"]
            else:
                print(f"{cmd_id:6d}  {script_name[:22]:22} | {member:22} kind={ev['kind']}")
                continue
            string_span = cg.walker.spans.get(sid, (-1, -1))
            defined_in = start <= string_span[0] < end
            total = count_refs(cg.b.trace, sid)
            inside = sum(1 for j in range(start, end)
                         if cg.b.trace[j]["kind"] == "MemberReference"
                         and cg.b.trace[j].get("idref") == sid)
            if ev["kind"] == "BinaryObjectString":
                total += 1; inside += 1
            print(f"{cmd_id:6d}  {script_name[:22]:22} | {member:22} #{sid:<6} {str(defined_in):14} {total:10}  {inside}")

if __name__ == "__main__":
    main()
