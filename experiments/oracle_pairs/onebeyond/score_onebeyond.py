#!/usr/bin/env python3
"""
score_onebeyond.py - ROADMAP R14: score the two 1 Beyond camera oracle pairs
that experiments/oracle_pairs/build_index.py's corpus-driven pair set never
reaches.

Why a separate script instead of build_index.py + score.py
------------------------------------------------------------
build_index.py joins packages under corpus/extron-driver3 against modules
under corpus/extron-gs-modules by model name. The two pairs asked for here

    samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp
    samples/1 Beyond Cameras/AutoTracker3/pkp/1bynd_19_4741_v1_0_1.pkp

are not reachable that way: corpus/extron-driver3 carries exactly one 1bynd_19
package, and it is a different id (1bynd_19_20024_v1_0_0.pkp, models
IV-CAM-I12/IV-CAM-I20 - the i12/i20 donor), not one of these two. (The
corpus's *modules* side does carry both shipped .py modules, at
corpus/extron-gs-modules/09062026/onebynd_camera_{PTZ_IP12_IP20,
AutoTracker_3}_*.py - byte-identical, SHA-256-confirmed, to the samples/
copies used below - but with no matching .pkp on the packages side,
build_index.py's join never emits a pair for them.) Hence
`experiments/oracle_pairs/out/pair_index.json` and `scorecard.json` have zero
entries for 1bynd_19_4743 / 1bynd_19_4741: an acquisition gap in the corpus
snapshot, not a join-algorithm failure and not "does not exist" - see
RESULTS.md.

This script applies the same method as finding 14
(findings/14-oracle-pairs-at-scale.md) and experiments/oracle_pairs/score.py
- tools/pkp2cs.py translation, tools/wire_table.py's diff_tables as the
acceptance oracle, residual-reason accounting, and the dangling-self-call
runtime-resolvability check - directly against the two explicit pairs given
above, read from samples/ (not corpus/). It does not modify score.py,
pkp2cs.py or wire_table.py.

Usage (from the repo root):
    py -3.11 -u experiments/oracle_pairs/onebeyond/score_onebeyond.py

Output:
    experiments/oracle_pairs/onebeyond/results.json    (this run's data)
    <tmp>/onebeyond_gen/<name>.generated.py             (generated modules;
        NOT written into the repo - keeps generated/vendor-derived text out
        of committed files and keeps every path in results.json
        repo-relative, per CLAUDE.md). <tmp> is the platform temp dir by
        default, overridable with the ONEBEYOND_GEN_DIR env var.
"""
import collections
import json
import os
import sys
import tempfile
import traceback

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp2cs       # noqa: E402
import wire_table    # noqa: E402

PAIRS = [
    {
        "name": "PTZ-IP12_IP20",
        "pkp": "samples/1 Beyond Cameras/PTZ-IP12_IP20/pkp/1bynd_19_4743_v1_0_1.pkp",
        "module": "samples/1 Beyond Cameras/PTZ-IP12_IP20/Controlscript/onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py",
    },
    {
        "name": "AutoTracker3",
        "pkp": "samples/1 Beyond Cameras/AutoTracker3/pkp/1bynd_19_4741_v1_0_1.pkp",
        "module": "samples/1 Beyond Cameras/AutoTracker3/Controlscript/onebynd_camera_AutoTracker_3_v1_0_1_1.py",
    },
]

GEN_DIR = os.environ.get("ONEBEYOND_GEN_DIR") or os.path.join(
    tempfile.gettempdir(), "onebeyond_gen")
os.makedirs(GEN_DIR, exist_ok=True)


def safe_diff_tables(generated, reference):
    """wire_table.diff_tables, with a fallback if it raises the
    'unhashable type: dict' TypeError another agent may be mid-fix on
    concurrently (per the task brief). Does not edit wire_table.py; if the
    real diff can't run, falls back to a name-only (only_in_a/only_in_b/
    shared) comparison and records that the per-command diff_kinds could not
    be computed this run.
    """
    try:
        return wire_table.diff_tables(generated, reference), None
    except TypeError as e:
        if "unhashable type" not in str(e):
            raise
        a_names, b_names = set(generated.commands), set(reference.commands)
        return {
            "only_in_a": sorted(a_names - b_names),
            "only_in_b": sorted(b_names - a_names),
            "shared": sorted(a_names & b_names),
            "differences": {},
        }, "wire_table.diff_tables raised TypeError(%s); used a name-only " \
           "fallback diff for this run - differing/diff_kinds below are " \
           "not available" % e


def score_pair(pair):
    pkp_path = os.path.join(_ROOT, pair["pkp"])
    module_path = os.path.join(_ROOT, pair["module"])
    rec = {"name": pair["name"], "pkp": pair["pkp"], "module": pair["module"]}

    try:
        outs = pkp2cs.translate_pkp(pkp_path)
    except Exception as e:
        rec["status"] = "raised"
        rec["error"] = "%s: %s" % (type(e).__name__, e)
        return rec

    rec["jobs"] = len(outs)
    out = next((o for o in outs if o.get("source")), None)
    if out is None:
        rec["status"] = "no-source"
        return rec

    residuals = list(out.get("residuals") or [])
    rec["residuals"] = len(residuals)
    rec["residual_reasons"] = dict(collections.Counter(
        r["reason"] for r in residuals if isinstance(r, dict) and "reason" in r))
    rec["residual_detail"] = [dict(r) for r in residuals]

    gen_path = os.path.join(GEN_DIR, pair["name"] + ".generated.py")
    with open(gen_path, "w", encoding="utf-8") as f:
        f.write(out["source"])
    # Repo-relative note only - never the absolute tmp path (CLAUDE.md #6).
    rec["generated_written_to"] = "<tmp>/onebeyond_gen/%s.generated.py (not committed)" % pair["name"]

    rec["dangling_self_calls"] = pkp2cs.find_dangling_self_calls(out["source"])

    try:
        shipped = open(module_path, encoding="utf-8", errors="replace").read()
        generated_table = wire_table.extract_table(out["source"], "<generated %s>" % pair["name"])
        reference_table = wire_table.extract_table(shipped, pair["module"])
        d, diff_warning = safe_diff_tables(generated_table, reference_table)
        rec["status"] = "compared"
        rec["gen_cmds"] = len(generated_table.commands)
        rec["ship_cmds"] = len(reference_table.commands)
        rec["only_generated"] = d["only_in_a"]
        rec["only_shipped"] = d["only_in_b"]
        rec["shared"] = d["shared"]
        rec["differing"] = sorted(d["differences"].keys())
        rec["differences_detail"] = d["differences"]
        rec["diff_kinds"] = sorted({k for v in d["differences"].values() for k in v})
        if diff_warning:
            rec["diff_warning"] = diff_warning
    except Exception as e:
        rec["status"] = "compare-failed"
        rec["compare_error"] = "%s: %s" % (type(e).__name__, e)
        rec["compare_traceback"] = traceback.format_exc()

    return rec


def zoom_speed_check(rec):
    """finding 13 section 3: Extron's shipped 1 Beyond SetZoom computes a
    combined direction+speed byte into `speed` and then packs
    `ValueStateValues[value]` (the bare direction) instead - `speed` is dead,
    every zoom runs at speed 0. Does this scoring run see that as a wire-table
    difference on 'Zoom', and if not, why not.
    """
    return {
        "pair": rec["name"],
        "zoom_in_shared": "Zoom" in (rec.get("shared") or []),
        "zoom_in_differing": "Zoom" in (rec.get("differing") or []),
        "zoom_diff_detail": (rec.get("differences_detail") or {}).get("Zoom"),
    }


def main():
    results = []
    for pair in PAIRS:
        print("scoring", pair["name"])
        rec = score_pair(pair)
        results.append(rec)
        print("  status:", rec.get("status"))
        if rec.get("status") == "compared":
            print("  shared=%d differing=%d only_generated=%d only_shipped=%d"
                  % (len(rec["shared"]), len(rec["differing"]),
                     len(rec["only_generated"]), len(rec["only_shipped"])))
            print("  diff_kinds:", rec["diff_kinds"])
        print("  residuals:", rec.get("residuals"), rec.get("residual_reasons"))
        print("  dangling_self_calls:", rec.get("dangling_self_calls"))

    zoom = [zoom_speed_check(r) for r in results if r.get("status") == "compared"]
    for z in zoom:
        print("\nzoom-speed-0 check (finding 13 s3), %s:" % z["pair"])
        print(" ", z)

    out_path = os.path.join(_HERE, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"pairs": results, "zoom_speed_check": zoom}, f, indent=1)
    print("\nwrote %s" % os.path.relpath(out_path, _ROOT).replace(os.sep, "/"))


if __name__ == "__main__":
    main()
