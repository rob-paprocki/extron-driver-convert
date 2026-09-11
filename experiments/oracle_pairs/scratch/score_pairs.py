"""Score pkp2cs against every vendor-consistent .pkp <-> ControlScript pair.

The repo's scorecard has always rested on 4 pairs, all Extron-authored for
Extron hardware. This runs the same oracle (wire_table.diff_tables) over
hundreds of third-party pairs the translator was never tuned on.
"""
import json, os, sys, traceback, collections
R = r"Z:\GitHub\rob-paprocki\extron-driver-convert"
sys.path.insert(0, os.path.join(R, "tools"))
import pkp2cs, wire_table

D = r"C:\Users\Public\Documents\extron\Driver3"
G = r"C:\Users\Public\Documents\extron\GS_Modules\09062026"
pairs = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    "pairs_strict.json")))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scorecard.json")

rows = []
for i, p in enumerate(pairs, 1):
    if i % 25 == 0:
        print("  ...%d/%d" % (i, len(pairs)), flush=True)
    rec = {"pkp": p["pkp"], "module": p["matches"][0]["module"],
           "model": p["matches"][0]["model"]}
    try:
        jobs = pkp2cs.discover_jobs(os.path.join(D, p["pkp"]))
        outs = [pkp2cs.translate_job(j) for j in jobs]
        gen = outs[0] if outs else None
        if isinstance(gen, tuple):
            gen = gen[0]
        if not isinstance(gen, str):
            gen = getattr(gen, "source", None) or str(gen)
        rec["translated"] = True
    except Exception as e:
        rec.update(translated=False, error=type(e).__name__ + ": " + str(e)[:160])
        rows.append(rec); continue
    try:
        shipped = open(os.path.join(G, rec["module"]), encoding="utf-8",
                       errors="replace").read()
        ta = wire_table.extract_table(gen, "<generated>")
        tb = wire_table.extract_table(shipped, rec["module"])
        d = wire_table.diff_tables(ta, tb)
        rec["diff"] = {k: (len(v) if isinstance(v, (list, dict)) else v)
                       for k, v in d.items()}
        rec["gen_cmds"] = len(getattr(ta, "commands", {}) or {})
        rec["ship_cmds"] = len(getattr(tb, "commands", {}) or {})
    except Exception as e:
        rec["compare_error"] = type(e).__name__ + ": " + str(e)[:160]
    rows.append(rec)

json.dump(rows, open(OUT, "w"), indent=1)
ok = [r for r in rows if r.get("translated")]
raised = [r for r in rows if not r.get("translated")]
cmp_ok = [r for r in ok if "diff" in r]
print("\npairs attempted:        %d" % len(rows))
print("translated without raising: %d (%.0f%%)" % (len(ok), 100.0*len(ok)/max(len(rows),1)))
print("translator raised:      %d" % len(raised))
print("wire tables compared:   %d" % len(cmp_ok))
c = collections.Counter(r["error"].split(":")[0] for r in raised)
print("raise types:", c.most_common(8))
print("wrote", OUT)
