#!/usr/bin/env python3
"""Compare the Power command's record layout between the unmodified
20024 donor and the strip+keep-one edited .pkp -- to find what the
deserialiser's property accessors see differently."""
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb
import pkp_asset as pa

DONOR = os.path.abspath(
    os.path.join(_ROOT, "..", "docs-agnostic", "corpus", "extron-driver3",
                 "1bynd_19_20024_v1_0_0.pkp"))
EDITED = "experiments/graph_synthesis/out/strip_revhist_only.pkp"


def dump(label, path):
    b = pb.PackageBuilder(path)
    g = pa.CommandGraph(b)
    powers = [(sn, oid) for sn, oid in g.commands().items() if sn == "Power"]
    print(f"\n== {label}  path={path}")
    print(f"   Power ids: {powers}")
    pid = powers[0][1]
    slots = g.walker.member_slots(pid)
    print(f"   members (object {pid}):")
    for m, i in sorted(slots.items(), key=lambda kv: kv[1]):
        ev = g.b.trace[i]
        k = ev.get("kind")
        if k == "BinaryObjectString":
            v = repr(ev.get("value", ""))
        elif k == "MemberReference":
            v = f"ref->{ev.get('idref')}"
        elif k == "ClassWithId":
            v = f"cls-id={ev.get('metadata_id')}"
        elif k == "ClassWithMembers":
            v = f"cls-members class={ev.get('class', '?')[:60]}"
        else:
            v = repr(ev)[:80]
        print(f"     {m:40} {k:24} {v}")
    # Also print the DriverCommandAsset class record's metadata
    start, _ = g.walker.spans[pid]
    ev = g.b.trace[start]
    print(f"   defining record at trace[{start}]: kind={ev['kind']}")
    if ev["kind"] == "ClassWithId":
        meta = g.walker.metadata[ev["metadata_id"]]
        cname = meta.get("class") or meta.get("class_name") or meta.get("name", "?")
        print(f"   class metadata id={ev['metadata_id']} name={cname}")
        print(f"   member order: {meta.get('member_names')}")
    return g, pid


dump("UNMODIFIED 20024", DONOR)
dump("EDITED strip_revhist_only", EDITED)
