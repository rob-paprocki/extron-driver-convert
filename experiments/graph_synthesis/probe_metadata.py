#!/usr/bin/env python3
"""Compare the class-metadata events for enum class records between
the unmodified 20024 donor and the edited strip_revhist_only build."""
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


def enum_class_defs(path, label):
    b = pb.PackageBuilder(path)
    print(f"\n== {label}  ({path})")
    # Find the class-definition events for every inline/negative-id enum
    # class we care about.
    seen = []
    for i, ev in enumerate(b.trace):
        if ev.get("kind") in ("ClassWithMembers", "ClassWithMembersAndTypes"):
            cname = ev.get("class", "")
            if "Enum" in cname or "Flags" in cname:
                oid = ev.get("object_id")
                nnames = ev.get("member_names", [])
                seen.append((i, oid, cname, nnames))
    for i, oid, cname, nnames in seen:
        print(f"  trace[{i:5}]  obj={oid:5}  {cname}")
        print(f"              members={nnames}")
    # Also: find the class definition for 'DriverCommandAsset' (the main
    # command class) and show its first-instance byte slice near the top
    # of the trace vs. deeper.
    for i, ev in enumerate(b.trace):
        if (ev.get("kind") == "ClassWithMembersAndTypes"
            and "DriverCommandAsset" in (ev.get("class", ""))):
            print(f"  DriverCommandAsset class def at trace[{i}] "
                  f"obj={ev.get('object_id')}")
            break
    return b


enum_class_defs(DONOR, "UNMODIFIED 20024")
enum_class_defs(EDITED, "EDITED strip_revhist_only")
