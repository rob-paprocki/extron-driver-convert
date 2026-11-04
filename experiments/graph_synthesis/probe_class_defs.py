#!/usr/bin/env python3
"""probe_class_defs.py -- R28 Phase 3b hypothesis #1 test.

Dump every class-defining record (ClassWithMembersAndTypes /
SystemClassWithMembersAndTypes / ClassWithMembers /
SystemClassWithMembers) from a .pkp in stream order, keyed by the
object_id at which the class is first introduced. ClassWithId records
reference these by MetadataId, so if stripping an instance shifts a
class's defining object_id, every later ClassWithId reusing it binds to
the wrong metadata.

Also dumps BinaryLibrary records (library_id -> assembly name) in
stream order for hypothesis #3.

Usage:
    probe_class_defs.py <file_a.pkp> [<file_b.pkp>]

With one file: prints its tables. With two files: diffs the tables
pair-wise.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
for _p in (_TOOLS, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd  # noqa: E402


def load(path):
    data = pd.load_bytes(path)
    parser = pd.PkpParser(data)
    parser.parse()
    return parser


def class_table(parser):
    """object_id -> (class_name, library_name, system)."""
    out = {}
    for oid, ci in parser.classinfo_by_id.items():
        lib = parser.libraries.get(ci.library_id, "<system>") if not ci.is_system else "<system>"
        out[oid] = (ci.name, lib, ci.is_system)
    return out


def dump_one(parser, label):
    print(f"=== {label} ===")
    print(f"libraries ({len(parser.libraries)}):")
    for lib_id in sorted(parser.libraries):
        print(f"  {lib_id:>4} -> {parser.libraries[lib_id]}")
    print(f"class definitions ({len(parser.classinfo_by_id)}):")
    for oid in sorted(parser.classinfo_by_id):
        ci = parser.classinfo_by_id[oid]
        lib = parser.libraries.get(ci.library_id, "<system>") if not ci.is_system else "<system>"
        print(f"  oid={oid:>5}  lib={lib!s:<55}  class={ci.name}")


def diff(a, b, label_a, label_b):
    tab_a = class_table(a)
    tab_b = class_table(b)

    lib_a = {i: n for i, n in a.libraries.items()}
    lib_b = {i: n for i, n in b.libraries.items()}

    print(f"=== libraries ===")
    print(f"  {label_a}: {len(lib_a)} libs")
    print(f"  {label_b}: {len(lib_b)} libs")
    all_lib_ids = sorted(set(lib_a) | set(lib_b))
    diff_libs = 0
    for i in all_lib_ids:
        if lib_a.get(i) != lib_b.get(i):
            diff_libs += 1
            print(f"  lib_id={i}  A={lib_a.get(i, '--')!s}  B={lib_b.get(i, '--')!s}")
    if diff_libs == 0:
        print(f"  (library tables are identical)")

    print()
    print(f"=== class definitions ===")
    print(f"  {label_a}: {len(tab_a)} classes")
    print(f"  {label_b}: {len(tab_b)} classes")

    # Classes by (name, library) across both files, grouped.
    def by_name(tab):
        d = {}
        for oid, (name, lib, system) in tab.items():
            d.setdefault((name, lib), []).append(oid)
        return d

    name_a = by_name(tab_a)
    name_b = by_name(tab_b)

    only_in_a = set(name_a) - set(name_b)
    only_in_b = set(name_b) - set(name_a)
    shifted = []
    same = 0
    for key in sorted(set(name_a) & set(name_b)):
        oids_a = sorted(name_a[key])
        oids_b = sorted(name_b[key])
        if oids_a != oids_b:
            shifted.append((key, oids_a, oids_b))
        else:
            same += 1

    print(f"  same oid, same class/lib: {same}")
    print(f"  shifted class oid:        {len(shifted)}")
    print(f"  only in {label_a}:            {len(only_in_a)}")
    print(f"  only in {label_b}:            {len(only_in_b)}")

    if shifted:
        print()
        print("--- shifted classes (first 20) ---")
        for (name, lib), oids_a, oids_b in shifted[:20]:
            print(f"  {name}")
            print(f"    lib={lib}")
            print(f"    oid_in_{label_a}: {oids_a}")
            print(f"    oid_in_{label_b}: {oids_b}")

    if only_in_a:
        print()
        print(f"--- only in {label_a} (first 20) ---")
        for key in sorted(only_in_a)[:20]:
            print(f"  {key[0]}  lib={key[1]}  oids={sorted(name_a[key])}")

    if only_in_b:
        print()
        print(f"--- only in {label_b} (first 20) ---")
        for key in sorted(only_in_b)[:20]:
            print(f"  {key[0]}  lib={key[1]}  oids={sorted(name_b[key])}")


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 2
    a = load(sys.argv[1])
    if len(sys.argv) == 2:
        dump_one(a, sys.argv[1])
        return 0
    b = load(sys.argv[2])
    diff(a, b, os.path.basename(sys.argv[1]), os.path.basename(sys.argv[2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
