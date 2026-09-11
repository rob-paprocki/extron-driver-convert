"""Build the .pkp <-> ControlScript oracle-pair index from the local GC install."""
import os, re, sys, json, traceback
sys.path.insert(0, r"Z:\GitHub\rob-paprocki\extron-driver-convert\tools")
import pkp_dump as pd

D = r"C:\Users\Public\Documents\extron\Driver3"
G = r"C:\Users\Public\Documents\extron\GS_Modules\09062026"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pair_index.json")

norm = lambda s: re.sub(r'[^a-z0-9]', '', s.lower())
modules = {f: norm(f[:-3]) for f in os.listdir(G) if f.lower().endswith('.py')}

def model_names(par):
    out = set()
    for v in par.objects.values():
        if not (isinstance(v, dict) and (v.get("class") or "").endswith("DriverModelAsset")):
            continue
        for k, raw in (v.get("members") or {}).items():
            if not k.endswith("_name") or k.endswith("_defaultName"):
                continue
            if isinstance(raw, dict) and "$ref" in raw:
                raw = par.objects.get(raw["$ref"])
            if isinstance(raw, str) and raw.strip():
                out.add(raw.strip())
    return out

rows, errors = [], []
pkps = sorted(f for f in os.listdir(D) if f.lower().endswith('.pkp'))
for i, f in enumerate(pkps, 1):
    if i % 100 == 0:
        print("  ...%d/%d" % (i, len(pkps)), flush=True)
    try:
        par = pd.PkpParser(pd.load_bytes(os.path.join(D, f)))
        par.parse()
        names = model_names(par)
    except Exception as e:
        errors.append((f, repr(e)[:120])); continue
    matches = []
    for n in sorted(names):
        nn = norm(n)
        if len(nn) < 4:
            continue
        for mf, mn in modules.items():
            if nn in mn:
                matches.append({"model": n, "module": mf})
                break
    rows.append({"pkp": f, "models": sorted(names), "matches": matches})

json.dump({"packages": rows, "errors": errors}, open(OUT, "w"), indent=1)
paired = [r for r in rows if r["matches"]]
allm = sum(len(r["models"]) for r in rows)
print("\nparsed %d packages (%d errors)" % (len(rows), len(errors)))
print("model entries: %d" % allm)
print("packages with >=1 GS-module match: %d (%.0f%%)" % (paired and len(paired) or 0,
      100.0 * len(paired) / max(len(rows), 1)))
print("wrote %s" % OUT)
