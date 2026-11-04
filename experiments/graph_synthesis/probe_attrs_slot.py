#!/usr/bin/env python3
"""Probe what _attributes actually looks like in the donor and what
set_attributes does to the trace."""
from __future__ import annotations
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def main():
    b = pb.PackageBuilder(DONOR)
    cg = pa.CommandGraph(b)
    cmd_id = cg.commands()["Power"]
    slots = cg.walker.member_slots(cmd_id)
    print(f"Power is command oid #{cmd_id}")
    print(f"member slots keys: {sorted(slots)}")

    for member in ("CommandAssetBase+_attributes", "CommandAssetBase+_exCmdId",
                   "_attributes", "_exCmdId"):
        if member not in slots:
            print(f"  {member}: NOT PRESENT")
            continue
        i = slots[member]
        ev = b.trace[i]
        nxt = b.trace[i+1] if i+1 < len(b.trace) else None
        print(f"  {member}: slot_idx={i}")
        print(f"    ev   = {ev}")
        print(f"    next = {nxt}")

    print()
    print("Running set_attributes(cmd_id, 0x22)...")
    cg.set_attributes(cmd_id, 0x22)
    print("done. Re-reading trace around _attributes slot:")
    slots = cg.walker.member_slots(cmd_id)
    for member in ("CommandAssetBase+_attributes", "_attributes"):
        if member not in slots:
            continue
        i = slots[member]
        print(f"  {member}: ev={b.trace[i]}, next={b.trace[i+1]}")

if __name__ == "__main__":
    main()
