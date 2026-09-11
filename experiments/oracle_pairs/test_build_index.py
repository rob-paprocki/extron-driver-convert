#!/usr/bin/env python3
"""
test_build_index.py - pin finding 14's oracle-pair join.

On 2026-09-11 the committed build_index.py could not reproduce its own
committed output. Its join took the first module whose name contained the
model, whatever that module's vendor, so the result depended on directory
order: rebuilding from corpus/ gave 312, 311 or 310 packages depending on the
order, and never the committed 314. The committed out/pairs_strict.json turned
out to match a first-VENDOR-CONSISTENT-match rule exactly, so that is the rule
it was produced with. build_index.match_models now implements it; these tests
keep the code and the committed result from drifting apart again.

[1]-[3] are synthetic and run anywhere. [4] and [5] need the real module list
from corpus/extron-gs-modules/ and are skipped without it (a clone may omit the
1.3 GB corpus).

Run: python3 experiments/oracle_pairs/test_build_index.py
"""

import json
import os
import random
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import build_index as bi         # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def modules_of(files):
    """The (modules, mod_vendor) pair build_index.main builds, in list order."""
    modules = {f: bi.norm(f[:-3]) for f in files}
    vendors = {f: f.lstrip("_").split("_")[0].lower() for f in files}
    return modules, vendors


def strict_pairs(rows, module_files):
    modules, vendors = modules_of(module_files)
    out = []
    for r in rows:
        vendor = r["pkp"].split("_")[0].lower()
        vendor = bi.VENDOR_ALIAS.get(vendor, vendor)
        tight, _loose = bi.match_models(set(r["models"]), vendor, modules, vendors)
        if tight:
            out.append({"pkp": r["pkp"], "matches": tight})
    return out


def real_module_files():
    gs = bi.resolve_gs(os.path.join(_ROOT, "corpus", "extron-gs-modules"))
    if not gs:
        return None
    return sorted(f for f in os.listdir(gs) if f.lower().endswith(".py"))


def committed_rows():
    with open(os.path.join(_HERE, "out", "pair_index.json")) as f:
        return json.load(f)["packages"]


# ---------------------------------------------------------------------------

def test_foreign_module_first_does_not_hide_own_vendor():
    print("\n[1] a foreign module that sorts first does not hide the right one")
    # build_index's own docstring example: absn "C110" also matches DMBC110.
    modules, vendors = modules_of(["dyna_display_DMBC110_v1_0_0_0.py",
                                   "absn_display_C110_v1_0_0_0.py"])
    tight, loose = bi.match_models({"C110"}, "absn", modules, vendors)
    check("the own-vendor module is found past the foreign one",
          tight == [{"model": "C110", "module": "absn_display_C110_v1_0_0_0.py"}],
          str(tight))
    check("no rejected entry once the own vendor matched", loose == [], str(loose))


def test_foreign_only_match_is_rejected():
    print("\n[2] a foreign-only match is rejected, not paired")
    modules, vendors = modules_of(["dyna_display_DMBC110_v1_0_0_0.py"])
    tight, loose = bi.match_models({"C110"}, "absn", modules, vendors)
    check("no pair", tight == [], str(tight))
    check("recorded as a rejected match",
          loose == [{"model": "C110", "module": "dyna_display_DMBC110_v1_0_0_0.py"}],
          str(loose))


def test_short_names_are_not_joined():
    print("\n[3] model names under four characters are not joined")
    modules, vendors = modules_of(["abcd_other_ABC_v1_0_0_0.py"])
    tight, loose = bi.match_models({"ABC"}, "abcd", modules, vendors)
    check("neither paired nor rejected", tight == [] and loose == [],
          "tight=%s loose=%s" % (tight, loose))


def test_reproduces_committed_pairs():
    print("\n[4] the join reproduces finding 14's committed pair set exactly")
    files = real_module_files()
    if files is None:
        print("  skip corpus/extron-gs-modules not present")
        return
    got = strict_pairs(committed_rows(), files)
    with open(os.path.join(_HERE, "out", "pairs_strict.json")) as f:
        committed = json.load(f)
    key = lambda p: p["pkp"]                   # noqa: E731
    check("314 packages pair", len(got) == 314, "%d" % len(got))
    check("352 pairs in total", sum(len(p["matches"]) for p in got) == 352,
          "%d" % sum(len(p["matches"]) for p in got))
    same = sorted(got, key=key) == sorted(committed, key=key)
    detail = ""
    if not same:
        a = {p["pkp"] for p in got}
        b = {p["pkp"] for p in committed}
        detail = "missing %s extra %s" % (sorted(b - a)[:4], sorted(a - b)[:4])
    check("identical to out/pairs_strict.json, match for match", same, detail)


def test_which_packages_pair_does_not_depend_on_order():
    print("\n[5] which packages pair does not depend on module order")
    files = real_module_files()
    if files is None:
        print("  skip corpus/extron-gs-modules not present")
        return
    rows = committed_rows()
    base = {p["pkp"] for p in strict_pairs(rows, files)}
    rng = random.Random(20260911)
    for i in range(3):
        shuffled = files[:]
        rng.shuffle(shuffled)
        got = {p["pkp"] for p in strict_pairs(rows, shuffled)}
        check("shuffled order %d: the same %d packages pair" % (i + 1, len(base)),
              got == base,
              "missing %s extra %s" % (sorted(base - got)[:3], sorted(got - base)[:3]))


def main():
    print("test_build_index.py - finding 14's oracle-pair join")
    for fn in (test_foreign_module_first_does_not_hide_own_vendor,
               test_foreign_only_match_is_rejected,
               test_short_names_are_not_joined,
               test_reproduces_committed_pairs,
               test_which_packages_pair_does_not_depend_on_order):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
