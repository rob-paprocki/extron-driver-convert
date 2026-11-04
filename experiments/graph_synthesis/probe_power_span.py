#!/usr/bin/env python3
"""Verify what walker.member_slots(2498) actually points at."""
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
    span = cg.walker.spans[cmd_id]
    slots = cg.walker.member_slots(cmd_id)
    print(f"Power oid={cmd_id}")
    print(f"span = {span}")
    attrs_slot = slots["CommandAssetBase+_attributes"]
    print(f"_attributes slot = {attrs_slot}")
    print(f"slot within span? {span[0] <= attrs_slot < span[1]}")

    # Find ALL trace indices where an event with object_id == cmd_id appears.
    print()
    print(f"All events with object_id=={cmd_id}:")
    for i, ev in enumerate(b.trace):
        if ev.get("object_id") == cmd_id:
            print(f"  trace idx {i}: {ev.get('kind')} oid={ev.get('object_id')}")

    # Walker should resolve to exactly ONE span. Where does ClassWithId
    # records of DriverCommandAsset metadata_id appear and does any of them
    # have oid 2498?
    print()
    # List spans for all commands
    for name, oid in sorted(cg.commands().items(), key=lambda t: t[1]):
        s = cg.walker.spans[oid]
        print(f"  cmd {name:30} oid={oid:4} span={s}")

if __name__ == "__main__":
    main()
