#!/usr/bin/env python3
"""probe_keep_one.py - strip-and-keep-one WITHOUT rewriting values.

Isolates whether the keep-only + strip-to-root pattern itself breaks the
deserializer's view, independent of author_command_values.
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

donor = os.path.abspath(
    os.path.join(_ROOT, "..", "docs-agnostic", "corpus", "extron-driver3",
                 "1bynd_19_20024_v1_0_0.pkp"))
OUT = os.path.join(_HERE, "out", "keep_one_untouched.pkp")

b = pb.PackageBuilder(donor)
g = pa.CommandGraph(b)
cmds = g.commands()
# Pick a DIFFERENT command - one with a real script name, not the
# "UserDefinedString" placeholder command.
kept_sn = "Power" if "Power" in cmds else sorted(cmds)[0]
kept_id = cmds[kept_sn]
print("keeping command %r (object %d)" % (kept_sn, kept_id))

g.strip_to_minimum_root()
g.keep_only_command(kept_id)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
b.write(OUT)
print("wrote %s (%d bytes)" % (OUT, os.path.getsize(OUT)))
