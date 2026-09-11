#!/usr/bin/env python3
"""Run tools/pkp_validate.validate over a list of packages -> TSV."""
import sys, os, traceback

REPO = r"Z:\GitHub\rob-paprocki\extron-driver-convert"
sys.path.insert(0, os.path.join(REPO, "tools"))
import pkp_validate as V

list_file, out_file = sys.argv[1], sys.argv[2]
with open(list_file, "r", encoding="utf-8") as fh:
    paths = [ln.strip() for ln in fh if ln.strip()]

with open(out_file, "w", encoding="utf-8", newline="\n") as out:
    out.write("path\tstatus\tcode\tname\tverified\tbypassed\tnres\twarnings\n")
    for i, p in enumerate(paths, 1):
        try:
            r = V.validate(p)
            warn = " | ".join(w.replace("\t", " ").replace("\n", " ")
                              for w in r.warnings)
            out.write("%s\tok\t%s\t%s\t%s\t%s\t%d\t%s\n" % (
                p, r.code, r.name, r.verified, r.bypassed, len(r.resources), warn))
        except Exception as e:
            out.write("%s\tpy_throw\t\t%s\t\t\t\t%s\n" % (
                p, type(e).__name__,
                str(e).replace("\t", " ").replace("\n", " ")))
        if i % 200 == 0:
            out.flush()
            print("  ...%d" % i, flush=True)
print("done %d" % len(paths))
