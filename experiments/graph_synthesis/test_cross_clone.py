#!/usr/bin/env python3
"""
test_cross_clone.py - offline gate for cross_clone.py (ROADMAP R27).

Same shape as tools/test_pkp_asset.py: a check() helper, numbered sections,
one summary line. What matters here, specifically, is that a cross-package
clone can go wrong in ways a same-package clone structurally cannot - see
cross_clone.py's module docstring and RESULTS.md's R27 section for the walls
these tests pin:

  1. Version-stripped name matching works, and only where it has to
     (System.Collections.* generics whose OWN class name embeds the type
     argument's assembly version).
  2. A class name match is NOT enough on its own - `_schema_key` must catch
     a real, measured schema difference (pana's 29-member DecimalParamAsset
     vs the i20 donor's 28-member one) rather than reuse a metadata id whose
     layout silently disagrees with the bytes written against it.
  3. The real R27 pair - pana_19_5702's PanTiltAbsolutePosition into the
     untouched i20 donor - builds, round-trips through OUR OWN parser
     end to end, and does not mint a negative object id anywhere (the same
     invariant test_pkp_asset.py asserts for same-package clones, for the
     same reason: findings/18 section 6).
  4. Guards hold: cloning a script name that already exists raises rather
     than silently duplicating a command.

Run: python3 experiments/graph_synthesis/test_cross_clone.py

Extron's own loader is NOT exercised here - see RESULTS.md for that
(Load-Package.ps1 -Deserialize -Commands -Protocol, run by hand, output
captured verbatim). This file only re-proves what is checkable off a desk,
same division of labour as test_pkp_asset.py.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb           # noqa: E402
import pkp_dump as pd            # noqa: E402
import pkp_asset as pa           # noqa: E402
import nrbf_graph as ng          # noqa: E402
import cross_clone as cc         # noqa: E402

DONOR_PANA = os.path.join(_ROOT, "corpus", "extron-driver3", "pana_19_5702_v1_4_5.pkp")
TARGET_I20 = os.path.join(_ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp",
                          "1bynd_19_4743_v1_0_1.pkp")

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def skip_if_missing():
    if not (os.path.exists(DONOR_PANA) and os.path.exists(TARGET_I20)):
        print("  SKIP: donor or target sample not present in this checkout")
        return True
    return False


# ---------------------------------------------------------------------------

def test_strip_version():
    print("\n[1] strip_version")
    check("collapses a real assembly-qualified version",
          cc.strip_version(
              "System.Collections.Generic.List`1[[X, Extron.Configuration.Contracts, "
              "Version=13.26.0.15, Culture=neutral, PublicKeyToken=null]]")
          == "System.Collections.Generic.List`1[[X, Extron.Configuration.Contracts, "
             "Version=*, Culture=neutral, PublicKeyToken=null]]")
    check("a version-free name is unchanged",
          cc.strip_version("Extron.Configuration.Drivers.DriverCommandAsset")
          == "Extron.Configuration.Drivers.DriverCommandAsset")
    check("None is handled",  cc.strip_version(None) == "")
    a = cc.strip_version("...Version=1.1.24.402...")
    b = cc.strip_version("...Version=13.26.0.15...")
    check("two different real package versions strip to the same key", a == b, "%r != %r" % (a, b))


def test_schema_key_catches_real_drift():
    print("\n[2] _schema_key catches a real cross-package schema difference")
    if skip_if_missing():
        return
    pana = cc.DonorTrace(DONOR_PANA)
    i20_b = pb.PackageBuilder(TARGET_I20)
    i20_p = pd.PkpParser(i20_b.build(compress=False))
    i20_p.parse()
    i20_w = ng.EventWalker(i20_b.trace)
    i20_w.verify_full_coverage()

    def find_meta(walker, name):
        for oid, ev in walker.metadata.items():
            if ev.get("name") == name:
                return oid, ev
        return None, None

    pana_id, pana_ev = find_meta(pana.walker, "Extron.Configuration.Core.Assets.Automation.DecimalParamAsset")
    i20_id, i20_ev = find_meta(i20_w, "Extron.Configuration.Core.Assets.Automation.DecimalParamAsset")
    check("both packages define DecimalParamAsset", pana_id is not None and i20_id is not None)
    if pana_id is None or i20_id is None:
        return

    check("pana's DecimalParamAsset has 29 members (measured)",
          len(pana_ev["member_names"]) == 29, str(len(pana_ev["member_names"])))
    check("the i20 donor's DecimalParamAsset has 28 members (measured)",
          len(i20_ev["member_names"]) == 28, str(len(i20_ev["member_names"])))
    check("_bEnableCustomMinMax exists in pana's layout, not the i20 donor's",
          "_bEnableCustomMinMax" in pana_ev["member_names"]
          and "_bEnableCustomMinMax" not in i20_ev["member_names"])
    check("_schema_key disagrees between the two",
          cc._schema_key(pana_ev) != cc._schema_key(i20_ev))
    check("_schema_key agrees with itself",
          cc._schema_key(pana_ev) == cc._schema_key(pana_ev))


def _build_r27():
    b = pb.PackageBuilder(TARGET_I20)
    g = pa.CommandGraph(b)
    donor = cc.DonorTrace(DONOR_PANA)
    result = cc.clone_command_cross_package(
        g, donor, donor_script_name="PanTiltAbsolutePosition",
        name="Pan Tilt Absolute Position", script_name="PanTiltAbsolutePosition")
    return b, g, donor, result


def test_real_cross_package_clone():
    print("\n[3] the real R27 pair: pana_19_5702 -> the untouched i20 donor")
    if skip_if_missing():
        return
    before_b = pb.PackageBuilder(TARGET_I20)
    before_g = pa.CommandGraph(before_b)
    before_names = set(before_g.command_names())
    check("donor starts with 15 commands, none named PanTiltAbsolutePosition",
          len(before_names) == 15 and "PanTiltAbsolutePosition" not in before_names,
          str(sorted(before_names)))

    b, g, donor, (new_id, imported_classes, imported_libs,
                  imported_shared, schema_mismatches) = _build_r27()

    after_names = g.command_names()
    check("target now has 16 commands", len(after_names) == 16, str(len(after_names)))
    check("every original command is still present",
          before_names <= set(after_names))
    check("PanTiltAbsolutePosition is the new one",
          "PanTiltAbsolutePosition" in after_names
          and after_names["PanTiltAbsolutePosition"] == "Pan Tilt Absolute Position")

    check("DecimalParamAsset needed a real import (schema differs, RESULTS.md R27)",
          "Extron.Configuration.Core.Assets.Automation.DecimalParamAsset" in imported_classes)
    check("that import was because of a genuine schema mismatch, not a missing name",
          any(n.endswith("DecimalParamAsset") for n, _ids in schema_mismatches))
    check("no NEW BinaryLibrary was needed (both packages already declare Core)",
          imported_libs == [], str(imported_libs))
    check("five shared donor objects were closure-imported (measured in RESULTS.md)",
          len(imported_shared) == 5, str(imported_shared))

    cmds = g.commands()
    kids = g.children(cmds["PanTiltAbsolutePosition"])
    names = sorted(g.name_of(k) for k in kids)
    check("the new command has exactly Pan and Tilt as parameters",
          names == ["Pan", "Tilt"], str(names))

    # findings/18 section 6, re-asserted for the cross-package path: no NEW
    # object anywhere in the appended tail may carry a negative id.
    orig_positive_max = max(k for k in before_g.walker.spans if k > 0)
    new_negative = [ev.get("object_id") for ev in b.trace
                    if ev.get("object_id") is not None
                    and ev.get("object_id") < 0
                    and ev.get("object_id") not in before_g.walker.spans]
    check("no clone-minted object id is negative", new_negative == [], str(new_negative))
    new_positive = [ev.get("object_id") for ev in b.trace
                    if ev.get("object_id") is not None and ev.get("object_id") > orig_positive_max]
    check("at least one fresh positive id was actually minted", len(new_positive) > 0)

    # Our own parser round-trips the result end to end - the necessary (not
    # sufficient - see RESULTS.md) half of "did this build something real".
    raw = b.build(compress=False)
    parser = pd.PkpParser(raw)
    ok = True
    try:
        parser.parse()
    except Exception:
        ok = False
    check("the built package re-parses cleanly with our own reader", ok)
    walker_ok = True
    try:
        w = ng.EventWalker(b.trace)
        w.verify_full_coverage()
    except Exception:
        walker_ok = False
    check("EventWalker covers the whole trace with no drift", walker_ok)


def test_guards():
    print("\n[4] guards")
    if skip_if_missing():
        return
    b, g, donor, _result = _build_r27()
    raised = False
    try:
        cc.clone_command_cross_package(
            g, donor, donor_script_name="PanTiltAbsolutePosition",
            name="dup", script_name="PanTiltAbsolutePosition")
    except cc.CrossCloneError:
        raised = True
    check("cloning an already-present script name raises CrossCloneError", raised)

    raised = False
    try:
        donor.command_id("NoSuchCommand")
    except cc.CrossCloneError:
        raised = True
    check("looking up a nonexistent donor command raises CrossCloneError", raised)


def main():
    print("test_cross_clone.py - offline gate for cross-package object-graph synthesis")
    for fn in (test_strip_version,
               test_schema_key_catches_real_drift,
               test_real_cross_package_clone,
               test_guards):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
