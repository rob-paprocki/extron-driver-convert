#!/usr/bin/env python3
"""Verify set_attributes' mutation survives the writeback."""
from __future__ import annotations
import os, sys
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))
import pkp_build as pb              # noqa: E402
import pkp_asset as pa              # noqa: E402
import pkp_dump as pd               # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")

def main():
    b = pb.PackageBuilder(DONOR)
    cg = pa.CommandGraph(b)
    cmd_id = cg.commands()["Power"]

    # Direct enum-slot mutation, no strings.
    cg.set_attributes(cmd_id, 0x22)

    # Build and reparse from the output bytes.
    out = b.build()
    import gzip
    raw = gzip.decompress(out)
    parser = pd.PkpParser(raw)
    parser.parse()

    # Walk the reparse's trace to find the Power command and its attrs slot.
    from importlib import import_module
    sys.path.insert(0, os.path.join(_ROOT, "experiments", "nrbf_writeback"))
    nw = import_module("nrbf_write")
    parser2, trace2 = nw.parse_and_trace(raw)

    import nrbf_graph as ng
    walker2 = ng.EventWalker(trace2)
    slots2 = walker2.member_slots(cmd_id)
    i = slots2["CommandAssetBase+_attributes"]
    print(f"After rebuild+reparse:")
    print(f"  _attributes slot ev = {trace2[i]}")
    print(f"  _attributes next    = {trace2[i+1]}")

if __name__ == "__main__":
    main()
