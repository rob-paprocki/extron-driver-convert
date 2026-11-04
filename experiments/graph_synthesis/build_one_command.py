#!/usr/bin/env python3
"""build_one_command.py - ROADMAP R28 Phase 2 MVP.

Produces experiments/graph_synthesis/out/one_command.pkp: a package built
by starting from the i20 donor, stripping the root to the three load-
bearing containers (measured by probe_minimal_root.py), detaching every
command except one, and authoring that surviving command's visible fields
fresh using the enum vocabulary in tools/extron_enums.py.

Not true zero-byte authoring -- the root DriverFileAsset, the three root-
level containers, the DriverModelAsset, the EthernetProtocolAsset, and
the surviving command's class metadata and parameter-collection
wrappers all still come from the donor's byte stream. RESULTS.md R28
documents the structural authoring work that remains to reach every-byte-
authored.

What this experiment DOES establish: the four enum vocabularies in
tools/extron_enums.py are correct -- a .pkp written with authored values
for DriverAttributeEnum and ExtronCommandIdEnum round-trips through our
Python validator (tools/pkp_validate.py) AND through Extron's own
BinaryFormatter deserializer (experiments/gcp_harness/Load-Package.ps1).

Run from the repo root:  py -3.11 -u experiments/graph_synthesis/build_one_command.py
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

# Donor candidates, in preference order. Vendor material is untracked and
# per-worktree, so we fall back to whatever is reachable. First existing
# path wins. See vendor-files.manifest.tsv.
_DONOR_CANDIDATES = [
    # A plain shipping donor is preferred: ones built by finding 18's
    # cross-clone work (e.g. 1bynd_19_20024) carry a structural quirk
    # that makes ScriptMethodName/Name/Attributes read back as the
    # defaults through Extron's deserialiser, which would mask our
    # authored values. Shipping Panasonic donor sidesteps that.
    os.path.join(_ROOT, "..", "docs-agnostic", "corpus", "extron-driver3",
                 "pana_10_17060_v1_0_0.pkp"),
    os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20",
                 "pkp", "1bynd_19_4743_v1_0_1.pkp"),
    # Fallback: any .pkp in the sibling corpus dir.
]
OUT_PATH = os.path.join(_HERE, "out", "one_command.pkp")


def _pick_donor():
    for path in _DONOR_CANDIDATES:
        if os.path.isfile(path):
            return os.path.abspath(path)
    # Last-resort scan of a sibling worktree's corpus (common case for a
    # worktree spawned without a vendor-file sync).
    scan_root = os.path.abspath(
        os.path.join(_ROOT, "..", "docs-agnostic", "corpus",
                     "extron-driver3"))
    if os.path.isdir(scan_root):
        for name in sorted(os.listdir(scan_root)):
            if name.endswith(".pkp"):
                return os.path.join(scan_root, name)
    return None

# Authored values -- deliberately generic placeholders (not vendor-derived
# product names) so the output .pkp is obviously our own build artefact.
NEW_COMMAND_NAME = "Test Command"
NEW_SCRIPT_NAME = "TestCommand"
# RuntimeVisible so GC would render the command; LiveStatus so polling
# would treat its output as live, not emulated. Both bits are widely
# attested on shipping commands.
NEW_ATTRIBUTES = (ee.DriverAttributeEnum.RuntimeVisible
                  | ee.DriverAttributeEnum.LiveStatus)
# ExtronCommandIdEnum.General is the safe default for every new command;
# the DLL's own property comment reserves the other three values
# (Power/Input/LampHour) for legacy well-known commands.
NEW_EX_CMD_ID = ee.ExtronCommandIdEnum.General


def main():
    donor = _pick_donor()
    if donor is None:
        print("error: no donor .pkp found on any candidate path",
              file=sys.stderr)
        print("       (vendor material; untracked -- see "
              "vendor-files.manifest.tsv)", file=sys.stderr)
        return 2
    print("donor: %s" % donor)

    b = pb.PackageBuilder(donor)
    g = pa.CommandGraph(b)

    before = g.commands()
    print("donor has %d commands" % len(before))

    # Pick the first command by object id as the one we'll keep and
    # re-author. We don't care which: the point is to prove the enum
    # vocabulary authors values GC accepts, not which command wins.
    kept_script_name = sorted(before, key=lambda sn: before[sn])[0]
    kept_id = before[kept_script_name]
    print("keeping command %r (object %d) for re-authoring"
          % (kept_script_name, kept_id))

    print("stripping root to load-bearing containers...")
    dropped = g.strip_to_minimum_root()
    print("  detached %d root children: %s" % (len(dropped), dropped))

    print("detaching every other command...")
    detached = g.keep_only_command(kept_id)
    print("  detached %d command links across collections" % detached)

    print("authoring values using tools/extron_enums.py...")
    g.author_command_values(
        kept_id,
        name=NEW_COMMAND_NAME,
        script_name=NEW_SCRIPT_NAME,
        attributes=NEW_ATTRIBUTES,
        ex_cmd_id=NEW_EX_CMD_ID,
    )
    print("  attributes = 0x%X (%s)" % (
        int(NEW_ATTRIBUTES),
        " | ".join(str(f) for f in ee.DriverAttributeEnum
                   if f & NEW_ATTRIBUTES)))
    print("  _exCmdId   = %d (%s)" % (
        int(NEW_EX_CMD_ID), NEW_EX_CMD_ID.name))

    # Walk the IDriverCommandAsset pool to count commands GC would actually
    # see after the detaches. (`g.commands()` scans every DriverCommandAsset
    # record in the graph, including ones now orphaned from every list.)
    all_cmds = g.commands()
    live_from_pool = set()
    for _n, parent_id in g._command_parents():
        for child_id in g.children(parent_id):
            if child_id in {v for v in all_cmds.values()}:
                live_from_pool.add(child_id)

    print("\nfinal command set (%d records in graph, %d live in collections):"
          % (len(all_cmds), len(live_from_pool)))
    for sn, oid in sorted(all_cmds.items(), key=lambda kv: kv[1]):
        if oid not in live_from_pool:
            continue
        attrs = g.enum_member(oid, "CommandAssetBase+_attributes")
        # exCmdId member name depends on vintage: try the qualified form
        # first, then the bare form, mirroring set_ex_cmd_id's resolver.
        slots = g.walker.member_slots(oid)
        exname = ("CommandAssetBase+_exCmdId" if "CommandAssetBase+_exCmdId"
                  in slots else "_exCmdId")
        ex = g.enum_member(oid, exname)
        print("  %-24s (obj %-4d) attrs=0x%02X exCmdId=%d"
              % (sn, oid, attrs, ex))

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    b.write(OUT_PATH)
    print("\nwrote %s (%d bytes)" % (OUT_PATH, os.path.getsize(OUT_PATH)))
    for e in b.edits:
        print("  edit: %s" % e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
