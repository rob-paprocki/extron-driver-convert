#!/usr/bin/env python3
"""
surfaces.py - the measurements behind the Automate VX three-way verification
(REPORT.md, finding 20).

  extract   write the GC package's embedded script beside this file
            (1bynd_42_4279.embedded.py: Extron's code, git-ignored) and print
            the URI set each Extron driver calls, and their difference
  params    the GC package's parameters: class (Enum / Decimal), limits and
            enum states, read from the object graph by pkp_asset.CommandGraph
  toc       fetch the documentation site's own table of contents
            (Data/HelpSystem.xml names the TOC; its _Chunk0.js lists the
            pages) and compare it with the harvest under reference/automate-vx-api/
  probe     HTTP status of every API page name in probe_names.txt, in both
            URL shapes the site uses (<Name>-API.htm and <Name>.htm)

Standard library only. The vendor files it reads are not in the repository;
vendor-files.manifest.tsv lists them.
"""
import argparse
import glob
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))

PKP = os.path.join(ROOT, "samples", "Automate VX", "pkp", "1bynd_42_4279_v1_0_11.pkp")
CS = os.path.join(ROOT, "samples", "Automate VX", "Controlscript",
                  "onebynd_sm_Automate_VX_Series_v1_0_11_0.py")
EMBEDDED = os.path.join(HERE, "1bynd_42_4279.embedded.py")
HARVEST = os.path.join(ROOT, "reference", "automate-vx-api")
SITE = "https://sdkcon78221.crestron.com/sdk/Automate-VX-API/"
API_PAGES = SITE + "Content/Topics/Automate-API/API-Reference/"

# Every endpoint a driver calls appears as one string literal: 'api/<Name>' or 'get-token'.
_URI = re.compile(r"""['"](api/[A-Za-z]+|get-token)['"]""")


def gc_script():
    """The GC package's embedded script (one per package here)."""
    import pkp2cs
    jobs = [j for j in pkp2cs.discover_jobs(PKP) if j.source]
    if len(jobs) != 1:
        raise ValueError("expected one embedded script in %s, found %d" % (PKP, len(jobs)))
    return jobs[0].source


def uris(source):
    return sorted(set(_URI.findall(source)))


def gc_params():
    """{command script name: {parameter name: (class, min, max, [states])}}."""
    import pkp_asset
    import pkp_build
    graph = pkp_asset.CommandGraph(pkp_build.PackageBuilder(PKP))
    out = {}
    for script_name, cid in sorted(graph.commands().items()):
        params = {}
        for k in graph.children(cid):
            obj = graph.objects[k]
            cls = obj["class"].split(",")[0].split(".")[-1]
            members = obj.get("members", {})
            lo = _primitive(graph, members.get("_min"))
            hi = _primitive(graph, members.get("_max"))
            states = [graph.name_of(s) for s in graph.children(k)] if cls == "EnumParamAsset" else []
            params[graph.name_of(k)] = (cls, lo, hi, states)
        out[script_name] = params
    return out


def _primitive(graph, ref):
    import pkp_build
    if ref is None:
        return None
    v = pkp_build.deref(graph.objects, ref)
    return v.get("value") if isinstance(v, dict) else v


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "extron-driver-convert/automate_vx_threeway"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""


def toc_pages(chunk_js):
    """Page paths listed in a MadCap Flare TOC chunk."""
    return re.findall(r"'(/Content[^']+)'", chunk_js)


def live_toc():
    status, xml = _get(SITE + "Data/HelpSystem.xml")
    if status != 200:
        raise RuntimeError("HelpSystem.xml: HTTP %d" % status)
    m = re.search(r'\bToc="([^"]+)\.js"', xml)
    if not m:
        raise RuntimeError("HelpSystem.xml names no Toc")
    toc = m.group(1)
    built = re.search(r'\bBuildTime="([^"]+)"', xml)
    status, chunk = _get(SITE + toc + "_Chunk0.js")
    if status != 200:
        raise RuntimeError("%s_Chunk0.js: HTTP %d" % (toc, status))
    return (built.group(1) if built else None), toc_pages(chunk)


def harvested_pages():
    pages = set()
    for p in glob.glob(os.path.join(HARVEST, "**", "*.md"), recursive=True):
        with open(p, encoding="utf-8") as f:
            first = f.readline()
        m = re.match(r"Source:\s*(\S+)", first)
        if m:
            pages.add(m.group(1).split("/sdk/Automate-VX-API")[-1])
    return pages


def cmd_extract(_):
    src = gc_script()
    with open(EMBEDDED, "w", encoding="utf-8") as f:
        f.write(src)
    with open(CS, encoding="utf-8") as f:
        cs = uris(f.read())
    gc = uris(src)
    print("wrote %s (%d lines)" % (os.path.relpath(EMBEDDED, ROOT), src.count("\n") + 1))
    print("GC calls %d URIs, ControlScript %d; only GC: %s; only ControlScript: %s"
          % (len(gc), len(cs), sorted(set(gc) - set(cs)) or "none", sorted(set(cs) - set(gc)) or "none"))
    for u in gc:
        print("   ", u)


def cmd_params(_):
    for name, params in gc_params().items():
        print(name)
        for pname, (cls, lo, hi, states) in params.items():
            shown = states if len(states) <= 8 else states[:3] + ["..."] + states[-2:]
            print("    %-8s %-18s min=%s max=%s states=%d %s" % (pname, cls, lo, hi, len(states), shown if states else ""))


def cmd_toc(_):
    built, live = live_toc()
    have = harvested_pages()
    print("site TOC built %s: %d pages; harvest: %d pages" % (built, len(live), len(have)))
    for p in sorted(set(live) - have):
        print("   in TOC, not harvested:", p)
    for p in sorted(have - set(live)):
        print("   harvested, not in TOC:", p)


def cmd_probe(args):
    with open(args.names, encoding="utf-8") as f:
        names = [n.strip() for n in f if n.strip() and not n.startswith("#")]
    for n in names:
        a, _ = _get(API_PAGES + n + "-API.htm")
        b, _ = _get(API_PAGES + n + ".htm")
        print("%-28s %s %s" % (n, a, b))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Measurements behind the Automate VX three-way verification.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("extract").set_defaults(fn=cmd_extract)
    sub.add_parser("params").set_defaults(fn=cmd_params)
    sub.add_parser("toc").set_defaults(fn=cmd_toc)
    p = sub.add_parser("probe")
    p.add_argument("names", nargs="?", default=os.path.join(HERE, "probe_names.txt"))
    p.set_defaults(fn=cmd_probe)
    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
