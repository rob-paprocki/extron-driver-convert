#!/usr/bin/env python3
"""probe_refs.py -- R28 Phase 3b hypothesis #2 test.

Walk every $ref from the kept Power command in two files. Report ids
that resolve in both, ids present in only one, and ids whose resolved
values differ by class or by scalar member value. A dangling $ref
would mean the keep_only_command pattern pruned a record the kept
command still references.

Usage:
    probe_refs.py <donor.pkp> <stripped.pkp> [--target-name NAME]

Default target is the DriverCommandAsset whose _name resolves to
"Power". Use --target-name to pick a different command by its _name
or _scriptName.
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


def resolve_string(objects, ref):
    if isinstance(ref, dict) and "$ref" in ref:
        v = objects.get(ref["$ref"])
    else:
        v = ref
    # BinaryObjectString records parse to the raw string
    if isinstance(v, str):
        return v
    if isinstance(v, dict) and v.get("class") == "System.String":
        return v.get("members", {}).get("Value") or v.get("value")
    return v


def find_command(parser, target_name):
    """Return the object_id of the DriverCommandAsset whose _name or
    _scriptName resolves to target_name."""
    for oid, obj in parser.objects.items():
        if not isinstance(obj, dict):
            continue
        if obj.get("class", "").endswith("DriverCommandAsset"):
            mem = obj.get("members", {})
            name_ref = mem.get("AssetBase+_name") or mem.get("_name")
            script_ref = (mem.get("CommandAssetBase+_scriptName")
                          or mem.get("_scriptName"))
            name = resolve_string(parser.objects, name_ref)
            script = resolve_string(parser.objects, script_ref)
            if name == target_name or script == target_name:
                return oid, obj
    return None, None


def collect_refs(objects, start_id, max_depth=3):
    """Return a dict: visited_id -> object. BFS over $ref edges to
    depth max_depth."""
    visited = {}
    frontier = [(start_id, 0)]
    while frontier:
        oid, depth = frontier.pop(0)
        if oid in visited:
            continue
        obj = objects.get(oid)
        if obj is None:
            visited[oid] = None
            continue
        visited[oid] = obj
        if depth >= max_depth:
            continue
        for child in _iter_refs(obj):
            if child not in visited:
                frontier.append((child, depth + 1))
    return visited


def _iter_refs(obj):
    if isinstance(obj, dict):
        if "$ref" in obj:
            yield obj["$ref"]
            return
        for v in obj.values():
            yield from _iter_refs(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _iter_refs(v)


def describe(obj):
    if obj is None:
        return "<MISSING>"
    if isinstance(obj, dict):
        cls = obj.get("class", obj.get("$type", "?"))
        return f"{cls}"
    if isinstance(obj, str):
        return f"string({obj!r})"
    return f"{type(obj).__name__}({obj!r})"


def main():
    args = sys.argv[1:]
    target = "Power"
    if "--target-name" in args:
        i = args.index("--target-name")
        target = args[i + 1]
        args = args[:i] + args[i + 2:]
    if len(args) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    a = load(args[0])
    b = load(args[1])

    oid_a, cmd_a = find_command(a, target)
    oid_b, cmd_b = find_command(b, target)

    print(f"target name: {target!r}")
    print(f"  donor    id={oid_a}  class={describe(cmd_a)}")
    print(f"  stripped id={oid_b}  class={describe(cmd_b)}")
    print()

    if oid_a is None or oid_b is None:
        print("Could not find the target command in both files; aborting.")
        return 1

    refs_a = collect_refs(a.objects, oid_a, max_depth=3)
    refs_b = collect_refs(b.objects, oid_b, max_depth=3)

    print(f"BFS depth 3 from the Power command:")
    print(f"  donor    visited {len(refs_a)} object ids")
    print(f"  stripped visited {len(refs_b)} object ids")

    missing_in_b = [oid for oid, v in refs_a.items() if v is not None
                    and refs_b.get(oid) is None]
    missing_in_a = [oid for oid, v in refs_b.items() if v is not None
                    and refs_a.get(oid) is None]
    dangling_in_a = [oid for oid, v in refs_a.items() if v is None]
    dangling_in_b = [oid for oid, v in refs_b.items() if v is None]

    print()
    print(f"dangling (MISSING) in donor:    {len(dangling_in_a)}")
    print(f"dangling (MISSING) in stripped: {len(dangling_in_b)}")
    print()
    print(f"referenced in donor but MISSING in stripped: {len(missing_in_b)}")
    if missing_in_b:
        for oid in missing_in_b[:30]:
            print(f"  id={oid}  donor={describe(refs_a.get(oid))}")
    print()
    print(f"referenced in stripped but MISSING in donor: {len(missing_in_a)}")
    if missing_in_a:
        for oid in missing_in_a[:30]:
            print(f"  id={oid}  stripped={describe(refs_b.get(oid))}")

    # For common ids, flag class mismatches
    print()
    common = set(refs_a) & set(refs_b)
    class_mismatches = []
    for oid in common:
        va, vb = refs_a[oid], refs_b[oid]
        if (isinstance(va, dict) and isinstance(vb, dict)
                and va.get("class") != vb.get("class")):
            class_mismatches.append((oid, va.get("class"), vb.get("class")))
    print(f"class mismatches on common ids: {len(class_mismatches)}")
    for oid, ca, cb in class_mismatches[:10]:
        print(f"  id={oid}  donor={ca!s}  stripped={cb!s}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
