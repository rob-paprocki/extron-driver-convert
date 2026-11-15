#!/usr/bin/env python3
"""
resolve_p20.py - run resolve_visca.py against Crestron's IV-CAM-P20 driver and
write p20_wire_table.txt.

This does not reimplement anything: it imports
experiments/skeleton_i20/resolve_visca.py (the tool is already model-agnostic -
it takes a .pkg path and walks whatever Template chain that package declares)
and points it at the P20 package instead of the I20 one. Nothing under
experiments/skeleton_i20/ is modified.

Run: python3 experiments/skeleton_p20/resolve_p20.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "skeleton_i20"))

import resolve_visca  # noqa: E402  (experiments/skeleton_i20/resolve_visca.py, imported not edited)

P20_PKG = os.path.join(
    _ROOT, "samples", "Crestron 1 Beyond IV-CAM-p12_p20", "Crestron",
    "Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg")

OUT = os.path.join(_HERE, "p20_wire_table.txt")


def main():
    dd = resolve_visca.load(P20_PKG)
    rows, broken = [], []
    for c in dd["Commands"]:
        n = c["Name"]
        t = resolve_visca.normalise(resolve_visca.resolve(dd, n))
        params = sorted(set(__import__("re").findall(r"\{([A-Za-z][^}]*)\}", t)))
        rows.append((n, t, params))
        if "<" in t:
            broken.append((n, t))

    lines = []
    for n, t, params in rows:
        lines.append("%-28s %-56s %s" % (n, t, ",".join(params)))
    literal = sum(1 for _n, _t, p in rows if not p)
    lines.append("")
    lines.append("%d commands: %d literal, %d parameterised, %d UNRESOLVED"
                 % (len(rows), literal, len(rows) - literal - len(broken), len(broken)))
    for n, t in broken:
        lines.append("  UNRESOLVED %s -> %s" % (n, t))

    text = "\n".join(lines) + "\n"
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    sys.stdout.write(text)
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
