#!/usr/bin/env python3
"""
crestron_module.py - Crestron's Automate VX SIMPL module, read from an installed
Crestron device database (REPORT.md §8, finding 20).

The .cmc in Cresdb/Modules is only the join surface. Its logic is SIMPL+ source
(.csp/.csh) stored, unencrypted, in Cresdb/Modules/crssplus.dat - a ZIP - and
that source is a thin wrapper over a compiled SIMPL# library (.clz: a ZIP holding
a .dll and, for the 3-Series build, its XML documentation). This script uses only
the readable files: the SIMPL+ source and the XML documentation. It does not open
the DLLs; experiments/crestron_decompile/decompile.py does that, for the requests
in REPORT.md §10.

  list       the database's entries for a name, with size, date and whether encrypted
  extract    write the module's .csp/.csh (every version) and the library's XML
             documentation to crestron/ beside this file (git-ignored: vendor text)
  interface  the v1.2 wrapper's inputs and outputs, and the library call each input makes
  library    the library's documented members (name and summary)

Standard library only. --cresdb defaults to Crestron's standard install folder.
"""
import argparse
import io
import os
import re
import xml.etree.ElementTree as ET
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "crestron")
DEFAULT_CRESDB = r"C:/Program Files (x86)/Crestron/Cresdb"
MODULE = "1Beyond Automate_VX"
LIBRARY = "Automate_VX.clz"                      # the 3-Series build carries Automate_VX.xml


def splus_store(cresdb):
    return os.path.join(cresdb, "Modules", "crssplus.dat")


def entries(cresdb, pattern):
    z = zipfile.ZipFile(splus_store(cresdb))
    return z, [i for i in z.infolist() if re.search(pattern, i.filename, re.I)]


def read_plain(z, info):
    if info.flag_bits & 1:
        raise PermissionError("%s is encrypted; not read" % info.filename)
    return z.read(info)


def wrapper_source(cresdb, version="1.2"):
    z, found = entries(cresdb, r"^%s_v%s\.csp$" % (re.escape(MODULE), re.escape(version)))
    if len(found) != 1:
        raise FileNotFoundError("%s_v%s.csp not in %s" % (MODULE, version, splus_store(cresdb)))
    return read_plain(z, found[0]).decode("latin-1")


_DECL = re.compile(r"^\s*(DIGITAL|ANALOG|STRING)_(INPUT|OUTPUT)\s+(.*?);", re.M | re.S)


def interface(src):
    """[(kind, direction, name)] in declaration order, _SKIP_ slots dropped."""
    out = []
    for kind, direction, body in _DECL.findall(src):
        for raw in body.split(","):
            name = raw.strip()
            if name and name != "_SKIP_":
                out.append((kind.lower(), direction.lower(), re.sub(r"\s+", "", name)))
    return out


_HANDLER = re.compile(r"^(PUSH|RELEASE|CHANGE)\s+(\w+\$?)\s*\{(.*?)^\}", re.M | re.S)


def handlers(src):
    """{(event, signal): [library calls or properties set]}."""
    out = {}
    for event, signal, body in _HANDLER.findall(src):
        calls = re.findall(r"Automate\.(\w+)\s*\(", body)
        props = re.findall(r"Automate\.(\w+)\s*=", body)
        out[(event, signal)] = calls + ["%s=" % p for p in props]
    return out


def library_members(cresdb):
    z, found = entries(cresdb, r"^%s$" % re.escape(LIBRARY))
    inner = zipfile.ZipFile(io.BytesIO(read_plain(z, found[0])))
    xml = [i for i in inner.infolist() if i.filename.lower().endswith(".xml")]
    root = ET.fromstring(read_plain(inner, xml[0]))
    out = []
    for m in root.iter("member"):
        out.append((m.get("name"), " ".join((m.findtext("summary") or "").split())))
    return out


def cmd_list(args):
    _, found = entries(args.cresdb, args.pattern)
    for i in found:
        print("%-50s %9d  %s  %04d-%02d-%02d" % (i.filename, i.file_size,
                                                "ENCRYPTED" if i.flag_bits & 1 else "plain", *i.date_time[:3]))


def cmd_extract(args):
    os.makedirs(OUT, exist_ok=True)
    z, found = entries(args.cresdb, r"^%s_v[\d.]+\.cs[ph]$" % re.escape(MODULE))
    for i in found:
        with open(os.path.join(OUT, i.filename), "wb") as f:
            f.write(read_plain(z, i))
        print("wrote crestron/%s" % i.filename)
    z, lib = entries(args.cresdb, r"^%s$" % re.escape(LIBRARY))
    inner = zipfile.ZipFile(io.BytesIO(read_plain(z, lib[0])))
    for i in inner.infolist():
        if i.filename.lower().endswith((".xml", ".info", ".config")):
            with open(os.path.join(OUT, LIBRARY + "__" + i.filename), "wb") as f:
                f.write(read_plain(inner, i))
            print("wrote crestron/%s__%s" % (LIBRARY, i.filename))


def cmd_interface(args):
    src = wrapper_source(args.cresdb, args.version)
    sig = interface(src)
    by = {}
    for kind, direction, _ in sig:
        by[(kind, direction)] = by.get((kind, direction), 0) + 1
    print("v%s: %d signals %s" % (args.version, len(sig), sorted(by.items())))
    for (event, signal), calls in sorted(handlers(src).items(), key=lambda kv: kv[0][1]):
        print("  %-8s %-28s -> %s" % (event, signal, ", ".join(calls) or "(no library call)"))
    print("URL or API strings in the wrapper:", re.findall(r"https?://|api/|get-token", src, re.I) or "none")


def cmd_library(args):
    for name, summary in library_members(args.cresdb):
        print("%-70s %s" % (name.split("Automate_VX.")[-1][:70], summary))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Crestron's Automate VX SIMPL module, from an installed Cresdb.")
    ap.add_argument("--cresdb", default=os.environ.get("CRESDB", DEFAULT_CRESDB))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list")
    p.add_argument("pattern", nargs="?", default=r"automate|1beyond")
    p.set_defaults(fn=cmd_list)
    sub.add_parser("extract").set_defaults(fn=cmd_extract)
    p = sub.add_parser("interface")
    p.add_argument("--version", default="1.2")
    p.set_defaults(fn=cmd_interface)
    sub.add_parser("library").set_defaults(fn=cmd_library)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
