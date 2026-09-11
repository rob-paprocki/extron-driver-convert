#!/usr/bin/env python3
"""
score.py - run pkp2cs across every oracle pair and score it two ways.

Metric, per STATUS.md: acceptance is the wire-string table
(`wire_table.diff_tables`), never file or line similarity. And wire
correctness is *necessary but not sufficient* - so this also collects
residuals, which is where pkp2cs records what it could not translate
faithfully.

Read this before trusting a number from here
--------------------------------------------
Four harness bugs were written and corrected while building this, all the same
shape: an API was assumed rather than read, and each wrong assumption produced
a clean-looking number instead of a crash.

  1. `translate_job` returns a **dict**, not an object. Reading `.source` as an
     attribute yields None, and comparing the dict's repr against the shipped
     module fails with "no class definition found" for every pair - while a
     naive harness reports "100% translated".
  2. Counting exceptions measures nothing. pkp2cs records failure by appending
     to `residuals`; it does not raise. Every package in this set translates
     "successfully" and every package has residuals.
  3. `diff_tables` returns `only_in_a` / `only_in_b`. Reading `only_a` /
     `only_b` gives 0 and 0, which reads as perfect coverage.
  4. `Residuals` is a `list` subclass of `{"reason", "detail"}` dicts. Reading
     `kind` gives an empty set, which reads as no residuals at all.

Each of those failure modes is silent and flattering. That is the argument for
the repo's own rule - a plausible guess is worse than a recorded gap, because
it scores well.

Usage: python3 experiments/oracle_pairs/score.py
       (run build_index.py first)
"""

import argparse
import collections
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp2cs                    # noqa: E402
import wire_table                # noqa: E402

from build_index import DEFAULT_D, DEFAULT_G, resolve_gs   # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drivers", default=DEFAULT_D)
    ap.add_argument("--modules", default=DEFAULT_G)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()

    gs = resolve_gs(args.modules)
    pairs = json.load(open(os.path.join(args.outdir, "pairs_strict.json")))
    print("scoring %d packages" % len(pairs))

    rows = []
    for i, p in enumerate(pairs, 1):
        if i % 50 == 0:
            print("  ...%d/%d" % (i, len(pairs)), flush=True)
        module = p["matches"][0]["module"]
        rec = {"pkp": p["pkp"], "module": module, "model": p["matches"][0]["model"]}
        try:
            outs = pkp2cs.translate_pkp(os.path.join(args.drivers, p["pkp"]))
        except Exception as e:                        # noqa: BLE001
            rec.update(status="raised", error=type(e).__name__ + ": " + str(e)[:160])
            rows.append(rec)
            continue

        out = next((o for o in outs if o.get("source")), None)
        if out is None:
            rec.update(status="no-source")
            rows.append(rec)
            continue

        # Residuals subclasses list; entries are {"reason", "detail"}.
        residuals = list(out.get("residuals") or [])
        rec["residuals"] = len(residuals)
        rec["residual_reasons"] = dict(collections.Counter(
            r["reason"] for r in residuals if isinstance(r, dict) and "reason" in r))

        try:
            shipped = open(os.path.join(gs, module), encoding="utf-8",
                           errors="replace").read()
            generated = wire_table.extract_table(out["source"], "<generated>")
            reference = wire_table.extract_table(shipped, module)
            d = wire_table.diff_tables(generated, reference)
            rec.update(status="compared",
                       gen_cmds=len(generated.commands),
                       ship_cmds=len(reference.commands),
                       only_generated=len(d["only_in_a"]),
                       only_shipped=len(d["only_in_b"]),
                       shared=len(d["shared"]),
                       differing=len(d["differences"]),
                       diff_kinds=sorted({k for v in d["differences"].values() for k in v}))
        except Exception as e:                        # noqa: BLE001
            rec.update(status="compare-failed",
                       compare_error=type(e).__name__ + ": " + str(e)[:200])
        rows.append(rec)

    json.dump(rows, open(os.path.join(args.outdir, "scorecard.json"), "w"), indent=1)
    report(rows)
    print("wrote %s" % os.path.join(args.outdir, "scorecard.json"))


def report(rows):
    status = collections.Counter(r.get("status") for r in rows)
    compared = [r for r in rows if r.get("status") == "compared"]
    print("\npackages: %d   %s" % (len(rows), dict(status)))
    if not compared:
        return

    shared = sum(r["shared"] for r in compared)
    differing = sum(r["differing"] for r in compared)
    perfect = [r for r in compared if r["differing"] == 0 and r["only_shipped"] == 0]
    print("\n-- wire table (the acceptance oracle) --")
    print("  shared commands:   %d" % shared)
    print("  wire-matching:     %d (%.1f%%)" % (shared - differing,
                                                100.0 * (shared - differing) / max(shared, 1)))
    print("  differing:         %d" % differing)
    print("  only in generated: %d" % sum(r["only_generated"] for r in compared))
    print("  only in shipped:   %d" % sum(r["only_shipped"] for r in compared))
    print("  perfect packages:  %d (%.0f%%)" % (len(perfect),
                                                100.0 * len(perfect) / len(compared)))
    kinds = collections.Counter(k for r in compared for k in r.get("diff_kinds", []))
    for k, n in kinds.most_common():
        print("      %-34s %d packages" % (k, n))

    print("\n-- residuals (necessary but not sufficient) --")
    reasons = collections.Counter()
    for r in rows:
        reasons.update(r.get("residual_reasons", {}))
    clean = sum(1 for r in rows if not r.get("residuals"))
    print("  packages with zero residuals: %d of %d" % (clean, len(rows)))
    for reason, n in reasons.most_common(12):
        pkgs = sum(1 for r in rows if reason in (r.get("residual_reasons") or {}))
        print("      %-42s %6d in %3d packages" % (reason, n, pkgs))

    # The point of collecting both: a perfect table does not mean a working
    # module. Cross-reference them rather than reporting them side by side.
    dangling = {r["pkp"] for r in rows
                if "dangling-self-call" in (r.get("residual_reasons") or {})}
    if dangling:
        def rate(rs):
            sh = sum(r["shared"] for r in rs)
            df = sum(r["differing"] for r in rs)
            return 100.0 * (sh - df) / max(sh, 1), len(rs)
        with_d = [r for r in compared if r["pkp"] in dangling]
        without = [r for r in compared if r["pkp"] not in dangling]
        print("\n-- the trap --")
        print("  packages that would raise AttributeError at runtime: %d (%.0f%%)"
              % (len(dangling), 100.0 * len(dangling) / len(rows)))
        print("  wire-match WITHOUT dangling calls: %.1f%% (n=%d)" % rate(without))
        print("  wire-match WITH    dangling calls: %.1f%% (n=%d)" % rate(with_d))
        broken_perfect = [r for r in with_d
                          if r["differing"] == 0 and r["only_shipped"] == 0]
        print("  PERFECT wire table but still raises: %d packages" % len(broken_perfect))


if __name__ == "__main__":
    main()
