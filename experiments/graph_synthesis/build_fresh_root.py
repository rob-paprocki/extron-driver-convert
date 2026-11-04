#!/usr/bin/env python3
"""
build_fresh_root.py - ROADMAP R28 Phase 4 POC.

The Phase 3b diagnosis said `detach`'s pool-shrink (List<T>._size going
from N to K<<N) is what breaks BinaryFormatter's bare-vs-qualified
ISerializable info.GetValue bridging. The Phase 2 keep_only_command
primitive triggers this; R27's cross-clone (which GROWS List<T>._size
by 1) does not.

Full fresh-root NRBF emission from zero bytes is a substantial new
writer. Before investing that, this POC runs one decisive measurement
to decide the scope of Phase 4 proper:

    Does `author_command_values()` on an UNMODIFIED donor -- no strip,
    no detach -- produce a .pkp whose Load-Package.ps1 -Commands prints
    the AUTHORED values (not C# class defaults)?

If YES: the pragmatic R28 is "donor + R27 cross-clone + author values
on the clone". The `keep_only_command`/`strip_to_minimum_root` strip
path is the only broken primitive; it is not needed for R28 proper.
Fresh-root emission becomes a nice-to-have, not a prerequisite.

If NO: `author_command_values` itself perturbs the ISerializable
bridging and the real fix is a fresh-root emitter after all.

Run from the repo root:
    python experiments/graph_synthesis/build_fresh_root.py
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
import extron_enums as ee     # noqa: E402

DONOR = os.path.join(_ROOT, "corpus", "extron-driver3",
                     "pana_19_5702_v1_4_5.pkp")
OUT_DIR = os.path.join(_HERE, "out")
OUT_PATH = os.path.join(OUT_DIR, "fresh_root_poc.pkp")

# One of the donor's own commands. We will overwrite its visible fields
# in place -- do NOT remove or add anything; List<T>._size stays at the
# donor's original value. If `author_command_values` is sound, the
# authored name/script_name/attributes should survive the Extron
# accessors on readback.
TARGET_SCRIPT_NAME = "AutoTracking"
AUTHORED_NAME = "POC Authored Display Name"
AUTHORED_SCRIPT_NAME = "POCAuthoredScriptName"
AUTHORED_ATTRIBUTES = (ee.DriverAttributeEnum.RuntimeVisible
                       | ee.DriverAttributeEnum.LiveStatus)   # 0x22


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    print("donor:", DONOR)
    print("out:  ", OUT_PATH)

    b = pb.PackageBuilder(DONOR)
    g = pa.CommandGraph(b)
    cmds = g.commands()
    if TARGET_SCRIPT_NAME not in cmds:
        raise SystemExit("donor has no %r command" % TARGET_SCRIPT_NAME)
    target_id = cmds[TARGET_SCRIPT_NAME]
    before_names = sorted(g.command_names())
    print("donor command count before: %d  (target oid=%d)"
          % (len(before_names), target_id))

    # The decisive step: in-place author on the donor's existing command.
    # NO detach, NO strip, NO keep_only. List sizes stay at donor's
    # originals.
    g.author_command_values(
        target_id,
        name=AUTHORED_NAME,
        script_name=AUTHORED_SCRIPT_NAME,
        attributes=AUTHORED_ATTRIBUTES,
        ex_cmd_id=ee.ExtronCommandIdEnum.General,
    )

    # Sanity: read it back through our own parser.
    after_names = set(g.command_names())
    print("donor command count after:  %d" % len(after_names))
    print("  authored script name in set: %s"
          % (AUTHORED_SCRIPT_NAME in after_names))
    print("  original script name in set: %s"
          % (TARGET_SCRIPT_NAME in after_names))
    cmds_after = g.commands()
    if AUTHORED_SCRIPT_NAME in cmds_after:
        ren_id = cmds_after[AUTHORED_SCRIPT_NAME]
        print("  authored oid stable:         %s" % (ren_id == target_id))

    b.write(OUT_PATH)
    size = os.path.getsize(OUT_PATH)
    print("wrote %s  (%d bytes)" % (OUT_PATH, size))
    print()
    print("Next: run pkp_validate and Load-Package.ps1 -Commands on it.")


if __name__ == "__main__":
    main()
