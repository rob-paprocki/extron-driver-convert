#!/usr/bin/env python3
"""probe_partial_strip.py - bisect which root-level detach breaks
the ICommandAsset property accessors in Extron's deserialiser.

The observation that motivates this probe: stripping the root to the
three load-bearing containers (commands, protocols, models) and keeping
one command deserialises cleanly through LoadFromFile + Deserialize,
but `$c.ScriptMethodName`/`$c.Name`/`$c.Attributes` all return the C#
class defaults ("", "Value", 15) instead of the authored values.

This probe builds four variants and writes each so Load-Package.ps1 can
be pointed at them individually.
"""
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

VARIANTS = [
    # (output name, hints-to-drop)
    ("strip_revhist_only.pkp", ("RevisionHistoryAsset",)),
    ("strip_revhist_param.pkp", ("RevisionHistoryAsset", "IParamAsset")),
    ("strip_revhist_resource.pkp", ("RevisionHistoryAsset", "IResourceAsset")),
    ("strip_all_three.pkp", ("RevisionHistoryAsset", "IParamAsset",
                             "IResourceAsset")),
]

for name, hints in VARIANTS:
    b = pb.PackageBuilder(DONOR)
    g = pa.CommandGraph(b)
    # Pick the second command (first non-UserDefinedString if it exists)
    cmds = g.commands()
    pick = "Power" if "Power" in cmds else sorted(cmds)[0]
    kept_id = cmds[pick]

    # Custom strip: only drop containers matching the hints for this variant
    for oid in list(g.children(1)):
        c = pa._cls(g.objects[oid]) or g.objects[oid].get("$type") or ""
        if any(h in c for h in hints):
            g.detach(1, oid)
    g.keep_only_command(kept_id)

    out = os.path.join(_HERE, "out", name)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    b.write(out)
    print(f"wrote {name} (kept {pick!r}, dropped {hints}) -> "
          f"{os.path.getsize(out)} bytes")
