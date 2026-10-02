#!/usr/bin/env python3
"""
decompile.py - decompile Crestron's SIMPL# libraries with ILSpy, for the
interoperability reading in experiments/automate_vx_threeway/REPORT.md §10 and
experiments/dm_md/DECOMPILE.md.

The owner decided (2026-09-24, ROADMAP D2) that these distributed libraries may
be decompiled for interoperability. The output is vendor-derived: it goes to
out/ beside this file, which is git-ignored. Findings describe the formats the
code shows; they never copy it.

  list                   the .clz packages in crssplus.dat and the .dll each holds
  run [NAME ...]         extract every .dll whose file name contains NAME from the
                         .clz packages, or take one from <CRESDB>/Programming/Libraries,
                         then write C# (out/<assembly>/) and IL (out/il/<assembly>.il).
                         With no NAME: the Automate VX builds and the DM library.
  run --dll PATH         the same for a .dll on disk
  hash                   SHA-256 of every .dll in out/dll/

Needs ILSpy's command-line decompiler (dotnet tool install --global ilspycmd);
REPORT.md §10 used 11.1.0.9782. Standard library otherwise. --cresdb defaults to
Crestron's standard install folder. Nothing encrypted is opened: a .clz entry
with the encryption flag set is skipped.
"""
import argparse
import hashlib
import io
import os
import shutil
import subprocess
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEFAULT_CRESDB = r"C:/Program Files (x86)/Crestron/Cresdb"
DEFAULT_NAMES = ["Automate_VX", "Automate_Vx_4Series", "Crestron.SimplSharpPro.DM"]


def splus_store(cresdb):
    return os.path.join(cresdb, "Modules", "crssplus.dat")


def libraries_dir(cresdb):
    return os.path.join(cresdb, "Programming", "Libraries")


def clz_members(store):
    """(clz name, dll name, bytes) for every .dll inside a .clz in the store."""
    outer = zipfile.ZipFile(store)
    for info in outer.infolist():
        if not info.filename.lower().endswith(".clz") or info.flag_bits & 1:
            continue
        try:
            inner = zipfile.ZipFile(io.BytesIO(outer.read(info)))
        except zipfile.BadZipFile:
            continue
        for member in inner.infolist():
            if member.filename.lower().endswith(".dll") and not member.flag_bits & 1:
                yield info.filename, os.path.basename(member.filename), inner.read(member)


def matches(filename, names):
    stem = os.path.splitext(filename)[0].lower()
    return any(stem == n.lower() for n in names)


def extract(cresdb, names, dll_dir):
    """Write the named .dll files to dll_dir; return {dll name: path}."""
    os.makedirs(dll_dir, exist_ok=True)
    got = {}
    store = splus_store(cresdb)
    if os.path.isfile(store):
        for clz, dll, data in clz_members(store):
            if matches(dll, names) and dll not in got:
                got[dll] = os.path.join(dll_dir, dll)
                with open(got[dll], "wb") as f:
                    f.write(data)
                print("extracted %s from %s (%d bytes)" % (dll, clz, len(data)))
    libs = libraries_dir(cresdb)
    if os.path.isdir(libs):
        for dll in sorted(os.listdir(libs)):
            if dll.lower().endswith(".dll") and matches(dll, names) and dll not in got:
                got[dll] = os.path.join(dll_dir, dll)
                shutil.copyfile(os.path.join(libs, dll), got[dll])
                print("copied %s from Programming/Libraries" % dll)
    return got


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def ilspy():
    found = shutil.which("ilspycmd")
    if found:
        return found
    fallback = os.path.join(os.path.expanduser("~"), ".dotnet", "tools", "ilspycmd.exe")
    return fallback if os.path.isfile(fallback) else None


def decompile(tool, dll, out):
    name = os.path.splitext(os.path.basename(dll))[0]
    project = os.path.join(out, name)
    il_dir = os.path.join(out, "il")
    os.makedirs(project, exist_ok=True)
    os.makedirs(il_dir, exist_ok=True)
    for args in ([tool, dll, "-p", "-o", project], [tool, dll, "-il", "-o", il_dir]):
        r = subprocess.run(args, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("%s failed: %s" % (" ".join(args[1:]), (r.stderr or r.stdout)[-800:]))
    count = sum(1 for _, _, files in os.walk(project) for f in files if f.endswith(".cs"))
    print("%s: %d .cs files, IL in il/%s.il, sha256 %s" % (name, count, name, sha256(dll)))


def main(argv=None):
    ap = argparse.ArgumentParser(description=(__doc__ or "").strip().split("\n\n")[0])
    ap.add_argument("--cresdb", default=DEFAULT_CRESDB)
    ap.add_argument("--out", default=OUT)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("names", nargs="*")
    run.add_argument("--dll", action="append", default=[])
    sub.add_parser("hash")
    args = ap.parse_args(argv)
    dll_dir = os.path.join(args.out, "dll")

    if args.cmd == "list":
        for clz, dll, data in clz_members(splus_store(args.cresdb)):
            print("%-40s %-40s %9d" % (clz, dll, len(data)))
        return 0
    if args.cmd == "hash":
        for dll in sorted(os.listdir(dll_dir)) if os.path.isdir(dll_dir) else []:
            print("%s  %s" % (sha256(os.path.join(dll_dir, dll)), dll))
        return 0

    tool = ilspy()
    if not tool:
        sys.exit("ilspycmd not found: dotnet tool install --global ilspycmd")
    targets = [p for p in args.dll if os.path.isfile(p)]
    if args.names or not args.dll:
        targets += list(extract(args.cresdb, args.names or DEFAULT_NAMES, dll_dir).values())
    if not targets:
        sys.exit("nothing matched; `list` shows the .clz packages")
    for dll in targets:
        decompile(tool, dll, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
