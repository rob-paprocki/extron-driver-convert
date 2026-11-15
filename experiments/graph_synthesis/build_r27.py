#!/usr/bin/env python3
"""
build_r27.py - ROADMAP R27: clone pana_19_5702's PanTiltAbsolutePosition
command into the untouched i20 donor (1bynd_19_4743_v1_0_1.pkp), across
packages, and write the result.

Run from the repo root:
    py -3.11 -u experiments/graph_synthesis/build_r27.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb        # noqa: E402
import pkp_asset as pa        # noqa: E402
import cross_clone as cc      # noqa: E402

DONOR_PANA = os.path.join(_ROOT, "corpus", "extron-driver3", "pana_19_5702_v1_4_5.pkp")
TARGET_I20 = os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp",
                          "1bynd_19_4743_v1_0_1.pkp")
OUT_PATH = os.path.join(_HERE, "out", "1bynd_19_r27_cross_clone.pkp")


def main():
    print("donor (foreign) :", DONOR_PANA)
    print("target (i20)    :", TARGET_I20)

    target_b = pb.PackageBuilder(TARGET_I20)
    print("target donor round-trips byte-identically: %d bytes" % len(target_b.raw))
    g = pa.CommandGraph(target_b)
    before = sorted(g.command_names())
    print("\ntarget commands before (%d):" % len(before))
    for sn in before:
        print("   ", sn)

    donor = cc.DonorTrace(DONOR_PANA)

    (new_id, imported_classes, imported_libs, imported_shared,
     schema_mismatches) = cc.clone_command_cross_package(
        g, donor, donor_script_name="PanTiltAbsolutePosition",
        name="Pan Tilt Absolute Position",
        script_name="PanTiltAbsolutePosition",
    )

    print("\nnew command object id:", new_id)
    print("class metadata records IMPORTED (no schema-identical match in target): %d"
          % len(imported_classes))
    for c in imported_classes:
        print("   IMPORTED CLASS:", c)
    print("library records imported: %d" % len(imported_libs))
    for lib in imported_libs:
        print("   IMPORTED LIBRARY:", lib)
    print("shared leaf objects imported (closure): %d" % len(imported_shared))
    for oid, desc in imported_shared:
        print("   shared %-6d %s" % (oid, desc))
    print("classes found by NAME but rejected on SCHEMA mismatch: %d" % len(schema_mismatches))
    for name, target_ids in schema_mismatches:
        print("   SCHEMA MISMATCH:", name, "target ids tried:", target_ids)

    after = sorted(g.command_names())
    print("\ntarget commands after (%d):" % len(after))
    for sn in after:
        marker = "  <-- NEW" if sn not in before else ""
        print("   ", sn, marker)

    # Structural sanity before writing: the new command's own parameters,
    # read back through the SAME object model pkp_asset itself uses.
    cmds = g.commands()
    kids = g.children(cmds["PanTiltAbsolutePosition"])
    print("\nPanTiltAbsolutePosition parameters (%d):" % len(kids))
    for k in kids:
        nm = g.name_of(k)
        cls = pa._cls(g.objects[k])
        print("   ", nm, cls)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    target_b.write(OUT_PATH)
    print("\nwrote", OUT_PATH, "(%d bytes)" % os.path.getsize(OUT_PATH))
    return 0


if __name__ == "__main__":
    sys.exit(main())
