#!/usr/bin/env python3
"""
gc_catalogue.py - what Global Configurator actually catalogued.

GC keeps two index files beside its driver library:

    Driver3/DriverLookup.dat   one entry per catalogued package file
    Driver3/DataFile.dat       the parsed catalogue itself

Both are raw NRBF - the same serialisation as a .pkp, minus the gzip - so
pkp_dump reads them.

Why this exists
---------------
Finding 18 built a package that parsed, round-tripped, validated and passed
every local test, and Global Configurator did not list it at all. The only
symptom of failing the catalogue-parse gate is ABSENCE: the package is simply
not in Driver Manager. Absence from DriverLookup.dat, after a rebuild that
post-dates the install, is that symptom measured rather than eyeballed.

What this does NOT tell you
---------------------------
Why a package is missing. For that, deserialize it through Extron's own code:
experiments/gcp_harness/Load-Package.ps1 -Deserialize (Windows, 32-bit
PowerShell). This tool only reports what GC recorded.

Usage
-----
    python3 tools/gc_catalogue.py                       # installed catalogue, else corpus snapshot
    python3 tools/gc_catalogue.py LOOKUP.dat --list
    python3 tools/gc_catalogue.py LOOKUP.dat --has 1bynd_19_20024   # exit 0 if present, 1 if not
    python3 tools/gc_catalogue.py LOOKUP.dat --against DRIVER_DIR   # catalogue vs folder contents
"""

import argparse
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import pkp_dump as pd            # noqa: E402

INSTALLED = r"C:\Users\Public\Documents\extron\Driver3\DriverLookup.dat"
SNAPSHOT = os.path.join(_ROOT, "corpus", "extron-driver3", "DriverLookup.dat")

PACKAGE_EXTS = (".pkp", ".eir")


class CatalogueError(Exception):
    """The file is not a Global Configurator catalogue we can read."""


def default_path():
    """The live catalogue on the Windows box, else the committed snapshot."""
    for p in (INSTALLED, SNAPSHOT):
        if os.path.isfile(p):
            return p
    return None


def lookup_entries(path_or_bytes):
    """Package filenames recorded in a DriverLookup.dat, sorted.

    Only strings that look like package filenames are returned; the catalogue
    also carries other strings, and counting all of them overstates coverage.
    """
    if isinstance(path_or_bytes, (bytes, bytearray)):
        raw = bytes(path_or_bytes)
    else:
        with open(path_or_bytes, "rb") as f:
            raw = f.read()
    if raw[:2] == b"\x1f\x8b":
        raise CatalogueError(
            "this is gzip - a .pkp package, not a catalogue. GC's catalogue "
            "files are raw NRBF.")
    if not raw or raw[0] != 0x00:
        raise CatalogueError("not an NRBF stream (no SerializedStreamHeader)")
    parser = pd.PkpParser(raw)
    parser.parse()
    names = {v for v in parser.objects.values()
             if isinstance(v, str) and v.lower().endswith(PACKAGE_EXTS)}
    return sorted(names)


def folder_packages(driver_dir):
    return sorted(f for f in os.listdir(driver_dir) if f.lower().endswith(PACKAGE_EXTS))


def compare(entries, driver_dir):
    """(catalogued-but-absent, present-but-uncatalogued) against a folder."""
    on_disk = set(folder_packages(driver_dir))
    listed = set(entries)
    return sorted(listed - on_disk), sorted(on_disk - listed)


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="List what Global Configurator catalogued (DriverLookup.dat).")
    ap.add_argument("lookup", nargs="?", help="DriverLookup.dat (default: installed, else corpus snapshot)")
    ap.add_argument("--has", metavar="SUBSTR", help="exit 0 if an entry contains SUBSTR, else 1")
    ap.add_argument("--list", action="store_true", help="print every entry")
    ap.add_argument("--against", metavar="DIR", help="compare the catalogue with a driver folder")
    args = ap.parse_args(argv)

    path = args.lookup or default_path()
    if not path:
        print("no DriverLookup.dat found; pass a path", file=sys.stderr)
        return 2
    try:
        entries = lookup_entries(path)
    except CatalogueError as e:
        print("%s: %s" % (path, e), file=sys.stderr)
        return 2

    print("%s: %d catalogued packages" % (path, len(entries)))
    if args.list:
        for e in entries:
            print("  " + e)
    if args.against:
        missing, uncatalogued = compare(entries, args.against)
        print("  listed but not in folder : %d" % len(missing))
        for m in missing[:50]:
            print("    " + m)
        print("  in folder but not listed : %d" % len(uncatalogued))
        for u in uncatalogued[:50]:
            print("    " + u)
    if args.has is not None:
        hits = [e for e in entries if args.has.lower() in e.lower()]
        for h in hits:
            print("  has: " + h)
        if not hits:
            print("  not catalogued: %s" % args.has)
        return 0 if hits else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
