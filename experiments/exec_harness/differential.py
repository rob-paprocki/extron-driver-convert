#!/usr/bin/env python3
"""
differential.py - run drive.py's differential over finding 14's oracle pairs
(ROADMAP R13).

For each pair in experiments/oracle_pairs/out/pairs_strict.json, the package is
translated exactly as score.py translates it (the first job with source), the
generated module is written to a scratch directory, and drive.py runs it
against Extron's shipped module in its own process, with a timeout, so one
module that hangs or crashes the interpreter cannot take the run with it.

Output: out/exec_results.json (one row per pair; paths are basenames only) and
a summary on stdout. What a row means is documented in README.md.

Usage:
  python experiments/exec_harness/differential.py            all pairs
  python experiments/exec_harness/differential.py --only extr_17_17677_v1_0_0.pkp
  python experiments/exec_harness/differential.py --limit 20 --jobs 4

Standard library only.
"""
import argparse
import collections
import concurrent.futures
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "experiments", "oracle_pairs"))

TIMEOUT = 180


def run_pair(pkp, module, drivers, gs, scratch):
    """Translate one package and drive it against its shipped module."""
    import pkp2cs                                     # in the worker process
    row = {"pkp": pkp, "module": module}
    try:
        outs = pkp2cs.translate_pkp(os.path.join(drivers, pkp))
        out = next((o for o in outs if o.get("source")), None)
    except Exception as e:                            # noqa: BLE001
        row["status"] = "translate-raised"
        row["error"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        return row
    if out is None:
        row["status"] = "no-source"
        return row
    gen_path = os.path.join(scratch, pkp.replace(".pkp", ".generated.py"))
    with open(gen_path, "w", encoding="utf-8", newline="") as f:
        f.write(out["source"])
    env = dict(os.environ, PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, os.path.join(HERE, "drive.py"),
             "--generated", gen_path, "--shipped", os.path.join(gs, module)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=TIMEOUT, env=env)
    except subprocess.TimeoutExpired:
        row["status"] = "timeout"
        return row
    if proc.returncode != 0 or not proc.stdout.strip():
        row["status"] = "harness-failed"
        row["error"] = (proc.stderr or "").strip().splitlines()[-1:] or ["exit %d" % proc.returncode]
        return row
    result = json.loads(proc.stdout.strip().splitlines()[-1])
    row.update(result)
    row["status"] = ("load-failed" if ("generated_error" in result or "shipped_error" in result)
                     else "compared")
    return row


def classify(row):
    """Per pair: the worst thing seen, for the summary."""
    if row["status"] != "compared":
        return row["status"] + ("" if row["status"] != "load-failed" else
                                (": generated" if "generated_error" in row else ": shipped"))
    kinds = collections.Counter()
    for entry in row.get("commands", {}).values():
        for res in entry.values():
            for k in ("gen_raises", "ship_raises", "differ"):
                if res[k]:
                    kinds[k] += 1
    if kinds["gen_raises"]:
        return "generated raises where shipped does not"
    if kinds["differ"]:
        return "behaviour differs"
    if kinds["ship_raises"]:
        return "only shipped raises"
    return "identical on every input"


def summarise(rows):
    print("\npairs: %d" % len(rows))
    for k, n in collections.Counter(classify(r) for r in rows).most_common():
        print("  %-44s %d" % (k, n))
    calls = collections.Counter()
    cmds = collections.Counter()
    for r in rows:
        for entry in (r.get("commands") or {}).values():
            for res in entry.values():
                cmds["compared"] += 1
                calls["inputs"] += res["inputs"]
                for k in ("same", "both_reject", "gen_raises", "ship_raises", "differ"):
                    calls[k] += res[k]
                    if k != "same" and res[k]:
                        cmds[k] += 1
    print("\ncommand methods compared: %d (Set and Update counted separately)" % cmds["compared"])
    for k in ("gen_raises", "differ", "ship_raises"):
        print("  with any %-12s %d" % (k, cmds[k]))
    print("inputs run on both sides: %d; same outcome: %d (%.1f%%); both refused, "
          "differently: %d"
          % (calls["inputs"], calls["same"], 100.0 * calls["same"] / max(calls["inputs"], 1),
             calls["both_reject"]))
    exc = collections.Counter()
    for r in rows:
        for entry in (r.get("commands") or {}).values():
            for res in entry.values():
                for ex in res.get("examples", {}).get("gen_raises", [])[:1]:
                    exc[ex["generated"]["exc"]["type"]] += 1
    if exc:
        print("exception types, generated side only (first example per method):")
        for k, n in exc.most_common():
            print("  %-24s %d" % (k, n))


def main(argv=None):
    from build_index import DEFAULT_D, DEFAULT_G, resolve_gs
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drivers", default=DEFAULT_D)
    ap.add_argument("--modules", default=DEFAULT_G)
    ap.add_argument("--pairs", default=os.path.join(ROOT, "experiments", "oracle_pairs",
                                                    "out", "pairs_strict.json"))
    ap.add_argument("--only", action="append", help="a .pkp name; repeatable")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("-o", "--out", default=os.path.join(HERE, "out", "exec_results.json"))
    args = ap.parse_args(argv)

    gs = resolve_gs(args.modules)
    pairs = json.load(open(args.pairs, encoding="utf-8"))
    work = [(p["pkp"], p["matches"][0]["module"]) for p in pairs]
    if args.only:
        work = [w for w in work if w[0] in args.only]
    if args.limit:
        work = work[:args.limit]
    print("driving %d pairs, %d at a time" % (len(work), args.jobs), flush=True)

    rows = []
    with tempfile.TemporaryDirectory(prefix="exec_harness_") as scratch:
        with concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(run_pair, pkp, mod, args.drivers, gs, scratch): pkp
                       for pkp, mod in work}
            for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
                rows.append(fut.result())
                if i % 25 == 0:
                    print("  ...%d/%d" % (i, len(work)), flush=True)
    rows.sort(key=lambda r: r["pkp"])
    if not args.only and not args.limit:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "w", encoding="utf-8", newline="\n") as f:
            json.dump(rows, f, indent=1, sort_keys=True)
        print("wrote %s" % os.path.relpath(args.out, ROOT))
    summarise(rows)
    return rows


if __name__ == "__main__":
    main()
