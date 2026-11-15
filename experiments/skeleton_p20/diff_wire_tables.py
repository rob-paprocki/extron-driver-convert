#!/usr/bin/env python3
"""
diff_wire_tables.py - compare the P20 wire table against the I20 one
(experiments/skeleton_i20/i20_wire_table.txt), command by command.

Both tables are `resolve_visca.py` output: one row per command Crestron's own
SchemaVersion 2.0 definition declares, name + resolved byte template + free
parameters. This groups commands into four buckets - I20-only, P20-only,
shared-and-byte-identical, shared-but-different - and writes the result to
i20_p20_diff.txt. Nothing under experiments/skeleton_i20/ is read except the
one wire-table text file it already publishes.

Run: python3 experiments/skeleton_p20/diff_wire_tables.py
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))

I20_TABLE = os.path.join(_ROOT, "experiments", "skeleton_i20", "i20_wire_table.txt")
P20_TABLE = os.path.join(_HERE, "p20_wire_table.txt")
OUT = os.path.join(_HERE, "i20_p20_diff.txt")


def parse(path):
    rows = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip() or line[0].isdigit() or line.startswith("  UNRESOLVED"):
                continue
            name = line.split(None, 1)[0]
            rows[name] = line.rstrip()
    return rows


def main():
    i20 = parse(I20_TABLE)
    p20 = parse(P20_TABLE)

    only_i20 = sorted(set(i20) - set(p20))
    only_p20 = sorted(set(p20) - set(i20))
    shared = sorted(set(i20) & set(p20))
    same = [n for n in shared if i20[n].strip() == p20[n].strip()]
    diff = [n for n in shared if i20[n].strip() != p20[n].strip()]

    out = []
    out.append("I20/P20 wire-table diff (resolve_visca.py output, both models' own "
               "compiled SchemaVersion 2.0 definitions)")
    out.append("=" * 78)
    out.append("")
    out.append("I20-only (%d of %d I20 commands):" % (len(only_i20), len(i20)))
    for n in only_i20:
        out.append("  " + i20[n].strip())
    out.append("")
    out.append("P20-only (%d of %d P20 commands):" % (len(only_p20), len(p20)))
    for n in only_p20:
        out.append("  " + p20[n].strip())
    out.append("")
    out.append("Shared, byte-identical templates (%d):" % len(same))
    for n in same:
        out.append("  " + n)
    out.append("")
    out.append("Shared, DIFFERENT templates (%d):" % len(diff))
    for n in diff:
        out.append("  I20: " + i20[n].strip())
        out.append("  P20: " + p20[n].strip())

    text = "\n".join(out) + "\n"
    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(text)
    sys.stdout.write(text)
    print("\nwrote %s" % OUT)


if __name__ == "__main__":
    main()
