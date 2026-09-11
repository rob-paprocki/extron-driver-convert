import sys, os
sys.path.insert(0, r"Z:\GitHub\rob-paprocki\extron-driver-convert\tools")
import pkp_validate as pv
from collections import Counter

listfile = sys.argv[1]
outfile = sys.argv[2]
paths = [l.rstrip("\n") for l in open(listfile, encoding="utf-8-sig") if l.strip()]
c = Counter()
rows = []
for p in paths:
    try:
        r = pv.validate(p)
        rows.append((r.code, r.name, r.verified, len(r.warnings), p))
        c[(r.name, r.verified, bool(r.warnings))] += 1
    except Exception as e:
        rows.append((-99, "EXCEPTION:" + type(e).__name__ + ":" + str(e)[:80], False, 0, p))
        c[("EXCEPTION:" + type(e).__name__, False, True)] += 1
for k, v in c.most_common():
    print(v, k)
with open(outfile, "w", encoding="utf-8") as f:
    for row in rows:
        f.write("%s\t%s\t%s\t%s\t%s\n" % row)
print("wrote", outfile, len(rows))
