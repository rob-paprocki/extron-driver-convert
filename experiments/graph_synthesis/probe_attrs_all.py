#!/usr/bin/env python3
"""Dump every ClassWithId whose metadata_id matches DriverAttributeEnum's
definition, with its following Primitive value. The hypothesis: Power's
_attributes is stored in the stream MULTIPLE times (once per model variant
referencing it), and we only mutated one of them."""
from __future__ import annotations
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "nrbf_writeback"))
import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def main():
    b = pb.PackageBuilder(DONOR)
    # Find the metadata_id of DriverAttributeEnum's class defn
    attr_defn_mids = set()
    for ev in b.trace:
        if ev.get("kind") in ("ClassWithMembersAndTypes", "ClassWithMembers",
                              "SystemClassWithMembersAndTypes",
                              "SystemClassWithMembers"):
            name = ev.get("name", "")
            if "DriverAttributeEnum" in name:
                attr_defn_mids.add(ev.get("object_id"))
                print(f"DriverAttributeEnum defn at trace idx with oid "
                      f"{ev.get('object_id')}: name={name}")

    # The Power command is at #2498. We mutated its _attributes Primitive.
    # Find ALL Primitives that follow a ClassWithId whose metadata_id is
    # one of attr_defn_mids. Those are all attribute values in the stream.
    counts = {}
    print()
    for i, ev in enumerate(b.trace):
        if ev.get("kind") == "ClassWithId" and ev.get("metadata_id") in attr_defn_mids:
            if i+1 < len(b.trace) and b.trace[i+1].get("kind") == "Primitive":
                val = b.trace[i+1]["value"]
                counts[val] = counts.get(val, 0) + 1
    print(f"Primitive values following DriverAttributeEnum ClassWithIds: {counts}")
    print(f"total attr Primitives: {sum(counts.values())}")

    # Also check: what are the first few occurrences in the stream?
    print()
    print("First 10 DriverAttributeEnum values in stream order:")
    n = 0
    for i, ev in enumerate(b.trace):
        if ev.get("kind") == "ClassWithId" and ev.get("metadata_id") in attr_defn_mids:
            if i+1 < len(b.trace) and b.trace[i+1].get("kind") == "Primitive":
                print(f"  trace idx {i}: ClassWithId oid={ev.get('object_id')} "
                      f"meta={ev.get('metadata_id')} -> value={b.trace[i+1]['value']}")
                n += 1
                if n >= 10:
                    break

if __name__ == "__main__":
    main()
