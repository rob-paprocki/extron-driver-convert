#!/usr/bin/env python3
"""
verify_vendor_files.py - check a local copy of the vendor material against
vendor-files.manifest.tsv.

The repository does not publish vendor material: Extron and Crestron packages
and modules, documentation harvested from vendor sites, Global Configurator's
catalogue data, and the packages this project built or mutated from vendor
ones. The manifest names every such file with its SHA-256 and size, at the
path the tools and tests read it from. Whoever has the material puts it at
those paths; this reports what is present and matching, missing, or
different. Tests that need a missing file skip with a message naming it.

Usage:
  python tools/verify_vendor_files.py                  the whole manifest
  python tools/verify_vendor_files.py --only samples/  one prefix
  python tools/verify_vendor_files.py -v               list every problem

Exit status 0 when every listed file (under --only) is present and matches,
1 otherwise. Standard library only.
"""
import argparse
import hashlib
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MANIFEST = os.path.join(_ROOT, "vendor-files.manifest.tsv")


def load_manifest(path):
    """[(sha256, size, relpath)] from a manifest: '#' lines are comments."""
    entries = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) != 3 or len(parts[0]) != 64:
                raise ValueError("%s:%d: expected 'sha256<TAB>size<TAB>path', got %r"
                                 % (path, n, line[:80]))
            entries.append((parts[0], int(parts[1]), parts[2]))
    return entries


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify(root, entries):
    """{'ok': [...], 'missing': [...], 'different': [...]} of relpaths."""
    out = {"ok": [], "missing": [], "different": []}
    for sha, size, rel in entries:
        full = os.path.join(root, *rel.split("/"))
        if not os.path.isfile(full):
            out["missing"].append(rel)
        elif os.path.getsize(full) != size or sha256_of(full) != sha:
            out["different"].append(rel)
        else:
            out["ok"].append(rel)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=DEFAULT_MANIFEST)
    ap.add_argument("--root", default=_ROOT, help="the checkout the manifest's paths are under")
    ap.add_argument("--only", help="check only paths starting with this prefix")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    entries = load_manifest(args.manifest)
    if args.only:
        entries = [e for e in entries if e[2].startswith(args.only)]
    result = verify(args.root, entries)
    print("%d listed%s: %d present and matching, %d missing, %d different"
          % (len(entries), " under %s" % args.only if args.only else "",
             len(result["ok"]), len(result["missing"]), len(result["different"])))
    for kind in ("different", "missing"):
        items = result[kind]
        shown = items if args.verbose else items[:10]
        for rel in shown:
            print("  %-9s %s" % (kind, rel))
        if len(items) > len(shown):
            print("  ... %d more %s (-v lists them all)" % (len(items) - len(shown), kind))
    return 0 if not result["missing"] and not result["different"] else 1


if __name__ == "__main__":
    sys.exit(main())
