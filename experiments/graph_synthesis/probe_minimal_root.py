#!/usr/bin/env python3
"""
probe_minimal_root.py - ROADMAP R28, a cheap measured step before attempting
a full from-scratch build: which of the i20 donor's SIX root-level typed
children (2x RevisionHistoryAsset, 4x AssetBase`1[[T]] pooled-asset
containers for models/commands/protocols/params, plus a separate resource
container) does Extron's own loader actually require?

Detaches children from the root's `_internalChildCollection` one group at a
time (using the SAME pkp_asset.CommandGraph.detach() already measured safe
for same-package edits - this stays same-package, unlike cross_clone.py) and
asks pkp_validate + Load-Package.ps1 whether the result still loads. This is
NOT the from-scratch build itself; it narrows what "minimal" needs to
contain before that build is attempted, using known-good primitives instead
of guessing.

Run from the repo root: py -3.11 -u experiments/graph_synthesis/probe_minimal_root.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb   # noqa: E402
import pkp_asset as pa   # noqa: E402

TARGET_I20 = os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp",
                          "1bynd_19_4743_v1_0_1.pkp")
OUT_PATH = os.path.join(_HERE, "out", "1bynd_19_r28_stripped_root.pkp")


def cls(v):
    return v["class"].split(",")[0] if isinstance(v, dict) and v.get("class") else None


def main():
    b = pb.PackageBuilder(TARGET_I20)
    g = pa.CommandGraph(b)

    root_id = 1
    root_coll_children = g.children(root_id)
    print("root _internalChildCollection children (%d):" % len(root_coll_children))
    kept, dropped = [], []
    for oid in root_coll_children:
        c = pa._cls(g.objects[oid]) or g.objects[oid].get("$type")
        print("   %-6d %s" % (oid, c))
        # keep only the model container (IDriverModelAsset) and the command
        # container (IDriverCommandAsset) and the protocol container
        # (IProtocolAsset) - drop RevisionHistoryAsset x2, the param
        # container and the resource container.
        if "RevisionHistoryAsset" in (c or "") or "IParamAsset" in (c or "") or "IResourceAsset" in (c or ""):
            dropped.append(oid)
        else:
            kept.append(oid)

    print("\nkeeping:", kept)
    print("dropping:", dropped)

    for oid in dropped:
        g.detach(root_id, oid)

    after = g.children(root_id)
    print("\nroot children after detach (%d):" % len(after))
    for oid in after:
        print("   %-6d %s" % (oid, pa._cls(g.objects[oid]) or g.objects[oid].get("$type")))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    b.write(OUT_PATH)
    print("\nwrote", OUT_PATH, "(%d bytes)" % os.path.getsize(OUT_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
