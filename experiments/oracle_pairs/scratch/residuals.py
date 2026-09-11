"""Collect pkp2cs residual reasons across every oracle pair.

Residuals are where this translator records what it could not do faithfully -
it appends {"reason","detail"} rather than raising. Counting exceptions
therefore measures nothing; this is the real failure signal.
"""
import json, os, sys, collections
sys.path.insert(0, r"Z:\GitHub\rob-paprocki\extron-driver-convert\tools")
import pkp2cs
D = r"C:\Users\Public\Documents\extron\Driver3"
here = os.path.dirname(os.path.abspath(__file__))
pairs = json.load(open(os.path.join(here, "pairs_strict.json")))

per_pkg, reasons, total = {}, collections.Counter(), 0
for i, p in enumerate(pairs, 1):
    if i % 50 == 0: print("  ...%d/%d" % (i, len(pairs)), flush=True)
    try:
        outs = pkp2cs.translate_pkp(os.path.join(D, p["pkp"]))
    except Exception:
        continue
    out = next((o for o in outs if o.get("source")), None)
    if out is None: continue
    rs = list(out.get("residuals") or [])
    total += len(rs)
    kinds = collections.Counter(r["reason"] for r in rs if isinstance(r, dict) and "reason" in r)
    per_pkg[p["pkp"]] = dict(kinds)
    reasons.update(kinds)

json.dump({"per_package": per_pkg, "totals": dict(reasons)},
          open(os.path.join(here, "residuals.json"), "w"), indent=1)
print("\npackages: %d | total residual entries: %d" % (len(per_pkg), total))
print("packages with ZERO residuals: %d" % sum(1 for v in per_pkg.values() if not v))
print("\nresidual reasons by frequency:")
for r, n in reasons.most_common(20):
    pkgs = sum(1 for v in per_pkg.values() if r in v)
    print("  %-40s %6d entries  in %3d packages" % (r, n, pkgs))
