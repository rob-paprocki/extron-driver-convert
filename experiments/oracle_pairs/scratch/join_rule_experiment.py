#!/usr/bin/env python3
"""
join_rule_experiment.py - ROADMAP R8: is build_index.match_models' join rule
right?

build_index.py (finding 14) joins a .pkp's declared model names against
ControlScript module filenames by substring containment, vendor-consistent,
FIRST match in directory-sorted order. That "first" is arbitrary: within one
vendor, several modules can legitimately contain the same short model
substring (a family name, a sibling model, an unrelated product that happens
to share four characters), and "first in sorted order" has no reason to be
the right one. Finding 10's Clock Audio 5940/1777 mix-up is the illustration
of the general risk, even though (checked below) 5940 does not actually
produce a false pair under today's rule on this corpus - it produces NO
match, because "CDT100 MK3" is not a substring of the one Clock Audio
module's name at all. The risk is real even where this particular instance
is not.

This is a SCRATCH, READ-ONLY experiment. It imports build_index.py and
pkp_dump.py without editing them, computes matches under three rules over the
full corpus/ library, and diffs each alternative against the committed
out/pairs_strict.json (314 packages, 352 pairs). It writes nothing under
experiments/oracle_pairs/out/ and does not touch the committed rule.

Rules compared
--------------
1. current       - build_index.match_models, unmodified: same-vendor,
                    substring containment, first module in directory-sorted
                    order. (Reproducing this exactly, byte for byte, against
                    the committed pairs is this script's own self-test.)

2. longest       - same-vendor, substring containment, but instead of "first
                    in directory order" picks the TIGHTEST fit: the candidate
                    module whose normalised filename is closest in length to
                    the normalised model name (minimum leftover characters),
                    ties broken by filename for determinism. This reads
                    "longest match" as "the model name should occupy the
                    largest share of the matched filename" - it should stop
                    a short, generic model name from preferring an unrelated
                    same-vendor module that merely happens to sort first,
                    when a more specific module also matches.

3. exact-token    - same-vendor, but instead of substring containment on the
                    fully-concatenated normalised strings, splits the model
                    name into words and the module filename into
                    underscore-delimited tokens, and requires the model's
                    normalised words to appear as a CONTIGUOUS, EXACT run of
                    the module's normalised tokens. This is what killed the
                    documented false positives in build_index's own
                    docstring (absn "C110" inside "DMBC110"; acer "K750"
                    inside a Digital Projection module) - neither is an
                    exact token, only a raw substring. It also correctly
                    produces NO match for Clock Audio 5940's "CDT100 MK3"
                    against "clau_dsp_CDT100_v1_0_3_0.py" (no "MK3" token
                    there), matching the current rule's (correct, by
                    accident) NO PAIR for that package.

                    Filenames that do not tokenise cleanly on "_" (a few
                    dozen jam vendor+type+model+version together with no
                    separator at all, e.g.
                    "acor_tdisplayAVF6510AVF8410VTF6510VTF8410v1100.py") are
                    UNRESOLVABLE under this rule and are reported as
                    no-match, never guessed.

Run (from repo root, no cd, corpus/ must be present):
    py -3.11 -u experiments/oracle_pairs/scratch/join_rule_experiment.py
Writes a JSON report to --outdir (default: the OS temp dir, NOT the repo -
this experiment adds no files under experiments/oracle_pairs/out/) and
prints the summary table used in JOIN_RULE.md.
"""

import argparse
import json
import os
import sys
import tempfile
import time

_HERE = os.path.dirname(os.path.abspath(__file__))            # .../scratch
_OP = os.path.dirname(_HERE)                                    # .../oracle_pairs
_ROOT = os.path.dirname(os.path.dirname(_OP))                   # repo root
sys.path.insert(0, _OP)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import build_index as bi          # noqa: E402  (READ ONLY - never edited)
import pkp_dump as pd             # noqa: E402


# ---------------------------------------------------------------------------
# Rule 2: same vendor, longest (tightest-fit) match
# ---------------------------------------------------------------------------

def match_longest(names, vendor, modules, mod_vendor):
    """Same as build_index.match_models, except the same-vendor candidate
    chosen for each model name is the TIGHTEST fit (module norm closest in
    length to the model norm), not the first in directory order.

    `loose` (foreign-only, rejected) entries keep the current rule's
    semantics exactly, since this experiment is only about which
    SAME-VENDOR candidate wins, not about the vendor gate itself.
    """
    tight, loose = [], []
    for n in sorted(names):
        nn = bi.norm(n)
        if len(nn) < 4:
            continue
        same_vendor = []
        foreign = None
        for mf, mn in modules.items():
            if nn not in mn:
                continue
            if mod_vendor[mf] == vendor:
                same_vendor.append(mf)
            elif foreign is None:
                foreign = mf
        if same_vendor:
            same_vendor.sort(key=lambda mf: (len(modules[mf]) - len(nn), mf))
            tight.append({"model": n, "module": same_vendor[0]})
        elif foreign is not None:
            loose.append({"model": n, "module": foreign})
    return tight, loose


# ---------------------------------------------------------------------------
# Rule 3: exact token match
# ---------------------------------------------------------------------------

def module_word_tokens(filename):
    """Module filename split on '_' into normalised word tokens, or None if
    the filename carries fewer than 3 non-empty underscore-delimited tokens
    (a jammed filename with no usable separators - can't be evaluated under
    this rule, never guessed at)."""
    stem = filename[:-3] if filename.lower().endswith(".py") else filename
    raw = [t for t in stem.split("_") if t]
    if len(raw) < 3:
        return None
    return [bi.norm(t) for t in raw]


def _contains_contiguous(hay, needle):
    L = len(needle)
    if L == 0 or L > len(hay):
        return False
    for i in range(len(hay) - L + 1):
        if hay[i:i + L] == needle:
            return True
    return False


def match_exact_token(names, vendor, module_files, mod_vendor, module_tokens):
    """Same-vendor, but the model name's normalised WORDS must appear as a
    contiguous, exact run of the module filename's normalised underscore
    tokens - not merely as a substring of the concatenated name."""
    tight, loose = [], []
    for n in sorted(names):
        words = [bi.norm(w) for w in n.split() if bi.norm(w)]
        if not words or sum(len(w) for w in words) < 4:
            continue
        found = None
        foreign = None
        for mf in module_files:                      # directory-sorted order
            toks = module_tokens.get(mf)
            if toks is None or not _contains_contiguous(toks, words):
                continue
            if mod_vendor[mf] == vendor:
                found = mf
                break
            elif foreign is None:
                foreign = mf
        if found is not None:
            tight.append({"model": n, "module": found})
        elif foreign is not None:
            loose.append({"model": n, "module": foreign})
    return tight, loose


# ---------------------------------------------------------------------------

def load_committed():
    with open(os.path.join(_OP, "out", "pairs_strict.json")) as f:
        return json.load(f)


def pair_set(strict_rows):
    """{pkp: set of (model, module)} from a pairs_strict-shaped list."""
    out = {}
    for row in strict_rows:
        out[row["pkp"]] = {(m["model"], m["module"]) for m in row["matches"]}
    return out


def diff_rule(committed, candidate):
    """Every package whose (model, module) pair set differs between the
    committed rule and a candidate rule. Returns a list of dicts, each with
    the package, what the committed rule paired, and what the candidate
    paired - enough to inspect by hand."""
    changed = []
    pkps = sorted(set(committed) | set(candidate))
    for pkp in pkps:
        a = committed.get(pkp, set())
        b = candidate.get(pkp, set())
        if a != b:
            changed.append({
                "pkp": pkp,
                "committed": sorted(a),
                "candidate": sorted(b),
                "removed": sorted(a - b),
                "added": sorted(b - a),
            })
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--drivers", default=bi.DEFAULT_D)
    ap.add_argument("--modules", default=bi.DEFAULT_G)
    ap.add_argument("--outdir", default=os.path.join(tempfile.gettempdir(),
                                                       "join_rule_experiment"))
    args = ap.parse_args()

    gs = bi.resolve_gs(args.modules)
    if not (os.path.isdir(args.drivers) and gs and os.path.isdir(gs)):
        raise SystemExit("driver library or GS modules not found; pass --drivers/--modules "
                          "(corpus/extron-driver3 and corpus/extron-gs-modules must exist)")
    os.makedirs(args.outdir, exist_ok=True)

    module_files = sorted(f for f in os.listdir(gs) if f.lower().endswith(".py"))
    modules = {f: bi.norm(f[:-3]) for f in module_files}
    mod_vendor = {f: f.lstrip("_").split("_")[0].lower() for f in module_files}
    module_tokens = {f: module_word_tokens(f) for f in module_files}
    untokenisable = sum(1 for f in module_files if module_tokens[f] is None)

    pkps = sorted(f for f in os.listdir(args.drivers) if f.lower().endswith(".pkp"))
    print("driver library: %d packages" % len(pkps))
    print("GS modules:     %d  (%s)" % (len(module_files), gs))
    print("modules with no usable '_' tokens (opaque to exact-token rule): %d"
          % untokenisable)

    t0 = time.time()
    rows = {"current": [], "longest": [], "exact-token": []}
    errors = []
    for i, f in enumerate(pkps, 1):
        if i % 200 == 0:
            print("  ...%d/%d  (%.0fs)" % (i, len(pkps), time.time() - t0), flush=True)
        try:
            parser = pd.PkpParser(pd.load_bytes(os.path.join(args.drivers, f)))
            parser.parse()
            names = bi.model_names(parser)
        except Exception as e:                          # noqa: BLE001
            errors.append({"pkp": f, "error": repr(e)[:160]})
            continue

        vendor = f.split("_")[0].lower()
        vendor = bi.VENDOR_ALIAS.get(vendor, vendor)

        tight_cur, _ = bi.match_models(names, vendor, modules, mod_vendor)
        tight_lng, _ = match_longest(names, vendor, modules, mod_vendor)
        tight_tok, _ = match_exact_token(names, vendor, module_files, mod_vendor, module_tokens)

        if tight_cur:
            rows["current"].append({"pkp": f, "matches": tight_cur})
        if tight_lng:
            rows["longest"].append({"pkp": f, "matches": tight_lng})
        if tight_tok:
            rows["exact-token"].append({"pkp": f, "matches": tight_tok})

    print("parsed %d packages, %d parse errors, %.0fs total"
          % (len(pkps) - len(errors), len(errors), time.time() - t0))

    committed = load_committed()
    committed_set = pair_set(committed)

    summary = {}
    diffs = {}
    for rule in ("current", "longest", "exact-token"):
        rset = pair_set(rows[rule])
        n_packages = len(rset)
        n_pairs = sum(len(v) for v in rset.values())
        summary[rule] = {"packages": n_packages, "pairs": n_pairs}
        diffs[rule] = diff_rule(committed_set, rset)
        print("\nrule %-12s packages=%-4d pairs=%-4d  changed-vs-committed=%d"
              % (rule, n_packages, n_pairs, len(diffs[rule])))

    out = {
        "corpus": {"drivers": os.path.relpath(args.drivers, _ROOT).replace("\\", "/"),
                   "modules": os.path.relpath(gs, _ROOT).replace("\\", "/")},
        "committed": {"packages": len(committed_set),
                      "pairs": sum(len(v) for v in committed_set.values())},
        "summary": summary,
        "errors": errors,
        "diffs": diffs,
        "untokenisable_modules": untokenisable,
    }
    out_path = os.path.join(args.outdir, "join_rule_report.json")
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1)
    print("\nwrote", out_path)


if __name__ == "__main__":
    main()
