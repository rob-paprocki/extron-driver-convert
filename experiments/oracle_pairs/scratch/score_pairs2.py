"""Score pkp2cs against every vendor-consistent .pkp <-> ControlScript pair.

Corrected harness. translate_job returns a DICT (source/residuals/commands),
not an object; an earlier run read .source as an attribute, got None, and
compared the dict's repr against the shipped module - which is why every
comparison failed with "no class definition found" while reporting 100%
translated. "Translated" also means nothing on its own here: this translator
records failure in `residuals` rather than raising.

Metric follows STATUS.md: acceptance is the wire-string table
(wire_table.diff_tables), not file or line similarity.
"""
import json, os, sys, collections
R = r"Z:\GitHub\rob-paprocki\extron-driver-convert"
sys.path.insert(0, os.path.join(R, "tools"))
import pkp2cs, wire_table

D = r"C:\Users\Public\Documents\extron\Driver3"
G = r"C:\Users\Public\Documents\extron\GS_Modules\09062026"
here = os.path.dirname(os.path.abspath(__file__))
pairs = json.load(open(os.path.join(here, "pairs_strict.json")))
OUT = os.path.join(here, "scorecard2.json")

rows = []
for i, p in enumerate(pairs, 1):
    if i % 25 == 0:
        print("  ...%d/%d" % (i, len(pairs)), flush=True)
    module = p["matches"][0]["module"]
    rec = {"pkp": p["pkp"], "module": module, "model": p["matches"][0]["model"]}
    try:
        outs = pkp2cs.translate_pkp(os.path.join(D, p["pkp"]))
    except Exception as e:
        rec.update(status="raised", error=type(e).__name__ + ": " + str(e)[:160])
        rows.append(rec); continue

    out = next((o for o in outs if o.get("source")), None)
    if out is None:
        rec.update(status="no-source")
        rows.append(rec); continue

    res = out.get("residuals")
    items = getattr(res, "items", None)
    try:
        reslist = list(res) if res is not None else []
    except TypeError:
        reslist = getattr(res, "entries", None) or []
    rec["residuals"] = len(reslist)
    kinds = []
    for r_ in reslist:
        k = getattr(r_, "kind", None) or (r_[0] if isinstance(r_, (list, tuple)) else None) \
            or (r_.get("kind") if isinstance(r_, dict) else None)
        if k: kinds.append(k)
    rec["residual_kinds"] = sorted(set(kinds))

    try:
        shipped = open(os.path.join(G, module), encoding="utf-8", errors="replace").read()
        ta = wire_table.extract_table(out["source"], "<generated>")
        tb = wire_table.extract_table(shipped, module)
        d = wire_table.diff_tables(ta, tb)
        rec["status"] = "compared"
        rec["gen_cmds"] = len(ta.commands)
        rec["ship_cmds"] = len(tb.commands)
        rec["only_generated"] = len(d.get("only_a", []))
        rec["only_shipped"] = len(d.get("only_b", []))
        rec["shared"] = len(d.get("shared", []))
        rec["differing"] = len(d.get("differences", {}))
        rec["diff_kinds"] = sorted({k for v in d.get("differences", {}).values() for k in v})
    except Exception as e:
        rec.update(status="compare-failed",
                   compare_error=type(e).__name__ + ": " + str(e)[:200])
    rows.append(rec)

json.dump(rows, open(OUT, "w"), indent=1)
st = collections.Counter(r.get("status") for r in rows)
print("\npairs attempted: %d" % len(rows))
print("status:", st.most_common())
cmp_ = [r for r in rows if r.get("status") == "compared"]
if cmp_:
    shared = sum(r["shared"] for r in cmp_)
    diff = sum(r["differing"] for r in cmp_)
    print("\ncompared pairs: %d" % len(cmp_))
    print("  shared commands:      %d" % shared)
    print("  wire-matching:        %d (%.1f%%)" % (shared - diff, 100.0*(shared-diff)/max(shared,1)))
    print("  differing:            %d" % diff)
    print("  only in generated:    %d" % sum(r["only_generated"] for r in cmp_))
    print("  only in shipped:      %d" % sum(r["only_shipped"] for r in cmp_))
    perfect = [r for r in cmp_ if r["differing"] == 0 and r["only_shipped"] == 0]
    print("  packages with a PERFECT table: %d (%.0f%%)" % (len(perfect), 100.0*len(perfect)/len(cmp_)))
    dk = collections.Counter(k for r in cmp_ for k in r.get("diff_kinds", []))
    print("  difference kinds:", dk.most_common(8))
rk = collections.Counter(k for r in rows for k in r.get("residual_kinds", []))
print("\nresidual kinds:", rk.most_common(10))
print("wrote", OUT)
