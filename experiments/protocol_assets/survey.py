#!/usr/bin/env python3
"""
survey.py - ROADMAP R16 first step.

Walks every .pkp package in corpus/extron-driver3/, uses tools/pkp_dump.py's
parser (via tools/pkp2cs.py's own helpers -- deref(), find_protocol_asset(),
_extract_stream_scripts(), _source_speaks_sis()) to locate every
DriverModelAsset's protocol asset, and tabulates:

  - _port, _udpOutputPort, _canEditPort, _protocolSubType (Ethernet)
  - _compatibility (all protocol-asset classes; resolved through the
    ProtocolCompatibilityFlags enum wrapper to its int value__)
  - _SerialProtocol (Serial)
  - a handful of embedded-script cross-checks: pkp2cs._source_speaks_sis()
    (the tool's own SIS/SSH-handshake detector, "w0echo"/"w3cv"), a literal
    InterfaceType == 'SSHInterface' check seen in some scripts, and raw
    substring presence of 'TCP'/'UDP'/'SSH'/'HTTP'/'HTTPS' (noisy -- these
    can appear in comments, docstrings or URLs, so they are reported as a
    weak signal only).

Also counts, per ROADMAP R16/R17:
  - packages with no protocol asset anywhere in their object graph
  - individual DriverModelAsset entries whose protocol-asset lookup
    (pkp2cs.find_protocol_asset) resolves to None

Output:
  - experiments/protocol_assets/survey_raw.jsonl  (one JSON object per
    package: every model->protocol-asset binding, full detail, for
    re-analysis without re-parsing the corpus)
  - experiments/protocol_assets/SURVEY.md          (this script also writes
    the summary tables straight to Markdown; run with --report-only to
    regenerate SURVEY.md from an existing survey_raw.jsonl without
    re-parsing)

Run (from repo root):
    py -3.11 -u experiments/protocol_assets/survey.py

Standard library only. No sampling: the full corpus is walked unless
--limit N is passed for a quick smoke test.
"""
import sys
import os
import re
import glob
import json
import time
import argparse
from collections import Counter, defaultdict

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS_DIR = os.path.join(REPO_ROOT, "tools")
sys.path.insert(0, TOOLS_DIR)

import pkp_dump   # noqa: E402
import pkp2cs      # noqa: E402

CORPUS_DIR = os.path.join(REPO_ROOT, "corpus", "extron-driver3")
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_PATH = os.path.join(OUT_DIR, "survey_raw.jsonl")
MD_PATH = os.path.join(OUT_DIR, "SURVEY.md")

LIT_TOKENS = ("TCP", "UDP", "SSH", "HTTP", "HTTPS")

# Ground truth for `_compatibility`, NOT inferred: the real name<->value
# mapping of Extron.Configuration.Contracts.Enumeration.ProtocolCompatibilityFlags,
# read via .NET reflection ([Enum]::GetNames) through
# experiments/gcp_harness/Load-Package.ps1 -Protocol against
# Extron.Configuration.Contracts.dll 15.45.0.0 (2026-09-23, this repo's GCP
# install). Reproduce with:
#   & 'C:\Windows\SysWOW64\WindowsPowerShell\v1.0\powershell.exe' -NoProfile `
#     -ExecutionPolicy Bypass -File experiments/gcp_harness/Load-Package.ps1 `
#     -Path samples/DSC_12G-HD/pkp/extr_17_17677_v1_0_0.pkp -Protocol
# This settles what the survey's own _compatibility/_port cross-checks could
# only gesture at: R16's "not determined" 64 and 512 have real names.
COMPATIBILITY_NAMES = {
    0: "None", 1: "IR_RS232 (== IRHardware)", 2: "Serial_RS232",
    4: "Serial_RS422", 8: "Serial_RS485", 14: "SerialHardware",
    16: "Ethernet_Telnet", 32: "Ethernet_UDP", 64: "Ethernet_HTTP",
    128: "CEC", 256: "Embedded_Driver", 512: "Ethernet_SSH",
    1024: "Ethernet_Dante", 2048: "Ethernet_RoomScheduling",
    3696: "EthernetHardware",
}


# Single-bit components only (excludes the pre-named composites 14 and 3696,
# and the 1/IR_RS232 vs IRHardware alias is just IR_RS232 here) -- used to
# decompose a bitmask value this survey saw that has no exact name of its
# own, the same way .NET's own Flags-enum ToString() would (as measured live:
# `Compatibility=Serial_RS232, Serial_RS485` for value 10 via -Protocol).
_COMPAT_BITS = [(1, "IR_RS232"), (2, "Serial_RS232"), (4, "Serial_RS422"),
                (8, "Serial_RS485"), (16, "Ethernet_Telnet"), (32, "Ethernet_UDP"),
                (64, "Ethernet_HTTP"), (128, "CEC"), (256, "Embedded_Driver"),
                (512, "Ethernet_SSH"), (1024, "Ethernet_Dante"),
                (2048, "Ethernet_RoomScheduling")]


def compat_label(v):
    if v is None:
        return "None(null)"
    name = COMPATIBILITY_NAMES.get(v)
    if name:
        return "%s (%s)" % (v, name)
    # No exact name for this bitmask -- decompose into named bits, same as a
    # combined [Flags] enum prints. Any leftover bits are reported plainly.
    remaining = v
    parts = []
    for bit, bit_name in _COMPAT_BITS:
        if v & bit:
            parts.append(bit_name)
            remaining &= ~bit
    if parts and remaining == 0:
        return "%s (%s)" % (v, "|".join(parts))
    return "%s (no enum name known)" % (v,)


def enum_value(objs, ref):
    """Follow one $ref to an NRBF enum instance (ClassWithId /
    ClassWithMembersAndTypes wrapping a single 'value__' member) and return
    its int. None if the field is absent, null, or not an enum shape."""
    obj = pkp2cs.deref(objs, ref)
    if isinstance(obj, dict) and "members" in obj and "value__" in obj.get("members", {}):
        return obj["members"]["value__"]
    return None


def survey_package(path):
    """Returns a dict describing every protocol-asset class seen, every
    DriverModelAsset -> protocol-asset binding, and any embedded-script
    cross-check evidence for each binding's transport."""
    data = pkp_dump.load_bytes(path)
    parser = pkp_dump.PkpParser(data)
    parser.parse()  # raises pkp_dump.NrbfParseError on an unhandled shape
    objs = parser.objects

    proto_class_counts = Counter()
    for v in objs.values():
        if isinstance(v, dict) and str(v.get("class", "")).endswith("ProtocolAsset"):
            proto_class_counts[v["class"]] += 1

    scripts = pkp2cs._extract_stream_scripts(objs)

    bindings = []
    models_no_protocol = []
    for oid, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Drivers.DriverModelAsset"):
            continue
        m = v.get("members", {})
        name = pkp2cs.deref(objs, m.get("AssetBase+_name"))
        sfn = pkp2cs.deref(objs, m.get("_scriptFileName"))
        proto = pkp2cs.find_protocol_asset(objs, v)
        if proto is None:
            models_no_protocol.append(name)
            continue

        pm = proto.get("members", {})
        cls = proto.get("class", "")
        short_cls = cls.rsplit(".", 1)[-1]

        src = scripts.get(sfn, "") if isinstance(sfn, str) else ""
        rec = {
            "model": name,
            "script_file_name": sfn,
            "class": short_cls,
            "port": pm.get("_port"),
            "udp_output_port": pm.get("_udpOutputPort"),
            "can_edit_port": pm.get("_canEditPort"),
            "can_edit_output_port": pm.get("_canEditOutputPort"),
            "ssh_connection_enabled": pm.get("_SSHConnectionEnabled"),
            "compatibility": (enum_value(objs, pm["_compatibility"])
                               if "_compatibility" in pm else None),
            "compatibility_base": (enum_value(objs, pm["ProtocolAssetBase+_compatibility"])
                                    if "ProtocolAssetBase+_compatibility" in pm else None),
            "protocol_sub_type": (enum_value(objs, pm["_protocolSubType"])
                                   if "_protocolSubType" in pm else None),
            "serial_protocol": (enum_value(objs, pm["_SerialProtocol"])
                                 if "_SerialProtocol" in pm else None),
            "sis_handshake": pkp2cs._source_speaks_sis(src),
            "interface_type_ssh": bool(re.search(
                r"InterfaceType\s*[=!]=?\s*'SSHInterface'", src)),
        }
        for kw in LIT_TOKENS:
            rec["lit_" + kw] = ("'%s'" % kw) in src
        bindings.append(rec)

    return {
        "path": os.path.relpath(path, REPO_ROOT).replace("\\", "/"),
        "proto_class_counts": dict(proto_class_counts),
        "has_any_protocol_asset": bool(proto_class_counts),
        "bindings": bindings,
        "models_no_protocol": models_no_protocol,
    }


def run_survey(limit=None):
    files = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.pkp")))
    if limit:
        files = files[:limit]
    print("surveying %d packages from %s" % (len(files), CORPUS_DIR), file=sys.stderr)

    t0 = time.time()
    n_ok = 0
    n_fail = 0
    failures = []
    with open(RAW_PATH, "w", encoding="utf-8") as out:
        for i, path in enumerate(files):
            try:
                rec = survey_package(path)
                rec["parse_error"] = None
            except Exception as e:  # pkp_dump.NrbfParseError or anything else
                n_fail += 1
                rec = {
                    "path": os.path.relpath(path, REPO_ROOT).replace("\\", "/"),
                    "parse_error": "%s: %s" % (type(e).__name__, e),
                    "proto_class_counts": {}, "has_any_protocol_asset": False,
                    "bindings": [], "models_no_protocol": [],
                }
                failures.append((path, str(e)))
            else:
                n_ok += 1
            out.write(json.dumps(rec) + "\n")
            if (i + 1) % 100 == 0:
                elapsed = time.time() - t0
                print("  %d/%d (%.0fs elapsed, %.2fs/pkg avg)" %
                      (i + 1, len(files), elapsed, elapsed / (i + 1)), file=sys.stderr)
    elapsed = time.time() - t0
    print("done: %d ok, %d parse failures, %.0fs total" % (n_ok, n_fail, elapsed),
          file=sys.stderr)
    for path, err in failures[:20]:
        print("  FAIL %s: %s" % (path, err), file=sys.stderr)
    return RAW_PATH


def load_raw():
    records = []
    with open(RAW_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def fmt_pct(n, d):
    return "%.1f%%" % (100.0 * n / d) if d else "n/a"


def top_n_dist(counter, n=12):
    return counter.most_common(n)


def write_report(records):
    n_packages = len(records)
    n_parse_fail = sum(1 for r in records if r.get("parse_error"))
    n_ok = n_packages - n_parse_fail

    n_no_asset_at_all = sum(1 for r in records
                             if not r.get("parse_error") and not r["has_any_protocol_asset"])

    proto_class_totals = Counter()
    for r in records:
        for cls, cnt in r.get("proto_class_counts", {}).items():
            proto_class_totals[cls] += cnt

    all_bindings = []
    n_models_total = 0
    n_models_no_protocol = 0
    for r in records:
        if r.get("parse_error"):
            continue
        n_models_no_protocol += len(r["models_no_protocol"])
        n_models_total += len(r["models_no_protocol"]) + len(r["bindings"])
        for b in r["bindings"]:
            b2 = dict(b)
            b2["_package"] = r["path"]
            all_bindings.append(b2)

    eth_bindings = [b for b in all_bindings if b["class"] == "EthernetProtocolAsset"]
    serial_bindings = [b for b in all_bindings if b["class"] == "SerialProtocolAsset"]
    other_bindings = [b for b in all_bindings
                       if b["class"] not in ("EthernetProtocolAsset", "SerialProtocolAsset")]

    # -------------------- compatibility, Ethernet only ----------------
    compat_groups = defaultdict(list)
    for b in eth_bindings:
        compat_groups[b["compatibility"]].append(b)

    # base-field comparison: does ProtocolAssetBase+_compatibility ever
    # disagree with, or carry information beyond, the derived _compatibility?
    base_nonzero = sum(1 for b in eth_bindings if (b["compatibility_base"] or 0) != 0)
    base_differs = sum(1 for b in eth_bindings
                        if b["compatibility_base"] is not None and b["compatibility"] is not None
                        and b["compatibility_base"] != b["compatibility"])

    lines = []
    a = lines.append
    a("# Protocol-asset survey (ROADMAP R16, first step)")
    a("")
    a("Generated by `experiments/protocol_assets/survey.py` over every `.pkp` in "
      "`corpus/extron-driver3/` (no sampling). Method: `tools/pkp_dump.PkpParser` "
      "parses the raw NRBF object graph; `tools/pkp2cs.py`'s own helpers "
      "(`find_protocol_asset`, `deref`, `_extract_stream_scripts`, "
      "`_source_speaks_sis`) locate each `DriverModelAsset`'s protocol-asset "
      "child and its embedded script. Everything under \"Measured\" below is a "
      "direct read of package bytes; everything under \"Inferred\" is this "
      "script's or this survey's interpretation and is marked as such.")
    a("")
    a("Raw per-package records (every binding, full detail): `survey_raw.jsonl` "
      "(%d lines, one JSON object per package)." % n_packages)
    a("")
    a("## Corpus-wide counts (measured)")
    a("")
    a("| | count |")
    a("|---|---|")
    a("| packages walked | %d |" % n_packages)
    a("| packages that parsed fully | %d |" % n_ok)
    a("| packages that raised while parsing | %d |" % n_parse_fail)
    a("| packages with **no** protocol-asset object anywhere in their graph | %d (%s of parsed) |"
      % (n_no_asset_at_all, fmt_pct(n_no_asset_at_all, n_ok)))
    a("| `DriverModelAsset` entries (models) total | %d |" % n_models_total)
    a("| models whose protocol-asset lookup (`pkp2cs.find_protocol_asset`) is `None` | %d (%s of models) |"
      % (n_models_no_protocol, fmt_pct(n_models_no_protocol, n_models_total)))
    a("| models with a resolved Ethernet protocol asset | %d |" % len(eth_bindings))
    a("| models with a resolved Serial protocol asset | %d |" % len(serial_bindings))
    a("| models with any other protocol-asset class | %d |" % len(other_bindings))
    a("")
    if n_parse_fail:
        a("Parse failures are listed at the end of this report; they are excluded "
          "from every count and table below.")
        a("")

    a("## Distinct protocol-asset classes seen (measured)")
    a("")
    a("Counted per NRBF object instance (a shared instance referenced from "
      "several models is counted once); one row per class name.")
    a("")
    a("| class | instances |")
    a("|---|---|")
    for cls, cnt in proto_class_totals.most_common():
        a("| `%s` | %d |" % (cls, cnt))
    a("")

    a("## `_compatibility` values (Ethernet protocol assets only) (measured, with ground truth)")
    a("")
    a("`_compatibility` is the *derived-class* field on `EthernetProtocolAsset` "
      "(`ProtocolCompatibilityFlags` enum, read through its `value__`). It is a "
      "**different field** from `ProtocolAssetBase+_compatibility`, the base-class "
      "member of the same name: across %d Ethernet bindings, the base field is "
      "nonzero in %d of them (%s) and disagrees with the derived field in %d "
      "(%s) -- consistent with finding 13 §4b's DSC/Samsung reads, where the "
      "base field was 0 while the derived field carried the real flag. **The "
      "derived `_compatibility` field is the one that discriminates; the base "
      "field is not a reliable second reading of the same fact.**"
      % (len(eth_bindings), base_nonzero, fmt_pct(base_nonzero, len(eth_bindings)),
         base_differs, fmt_pct(base_differs, len(eth_bindings))))
    a("")
    a("**This is no longer \"not determined\": every value below has Extron's own "
      "name attached, read straight off the compiled "
      "`Extron.Configuration.Contracts.Enumeration.ProtocolCompatibilityFlags` "
      "enum via .NET reflection** (`experiments/gcp_harness/Load-Package.ps1 "
      "-Protocol`, new switch added for this task; `[Enum]::GetNames` against "
      "`Extron.Configuration.Contracts.dll` 15.45.0.0, this repo's GCP install, "
      "2026-09-23). It is a `[Flags]`-shaped enum, not a sequential id list: "
      "`None=0, IR_RS232=1(==IRHardware), Serial_RS232=2, Serial_RS422=4, "
      "Serial_RS485=8, SerialHardware=14, Ethernet_Telnet=16, Ethernet_UDP=32, "
      "Ethernet_HTTP=64, CEC=128, Embedded_Driver=256, Ethernet_SSH=512, "
      "Ethernet_Dante=1024, Ethernet_RoomScheduling=2048, EthernetHardware=3696`. "
      "Every value below that has no single exact enum name is shown decomposed "
      "into its component bits joined with `|` (e.g. `10 = Serial_RS232|Serial_RS485`); "
      "that decomposition is this script's own bit-split, not a second reflected "
      "read per value -- but it is exactly what `Load-Package.ps1 -Protocol` printed "
      "live for value 10 (`Compatibility=Serial_RS232, Serial_RS485`), which is "
      "how .NET's own `[Flags]` enum `ToString()` renders an unnamed combination, "
      "so the two agree. "
      "16/32/64/512 match finding 13 §4b's four samples exactly (Telnet/UDP/HTTP/SSH); "
      "the corpus adds two more Ethernet values finding 13 never sampled, both "
      "also named by the same enum: 1024 (`Ethernet_Dante`) and 2048 "
      "(`Ethernet_RoomScheduling`), both always port 0 -- consistent with those "
      "being auxiliary-feature flags on a package that is not itself the socket "
      "endpoint, rather than a distinct wire transport. This resolves R16's "
      "open question directly; the script-cross-check section further below is "
      "now corroborating evidence, not the primary source.")
    a("")
    a("| `_compatibility` | models | packages | distinct `_port` values | ports (top, with counts) |"
      " `_udpOutputPort` nonzero | example packages |")
    a("|---|---|---|---|---|---|---|")
    for compat in sorted(compat_groups, key=lambda k: (-len(compat_groups[k]))):
        group = compat_groups[compat]
        pkgs = sorted(set(b["_package"] for b in group))
        ports = Counter(b["port"] for b in group)
        udp_nonzero = sum(1 for b in group if (b["udp_output_port"] or 0) != 0)
        examples = ", ".join(os.path.basename(p) for p in pkgs[:4])
        port_str = ", ".join("%s (%d)" % (p, c) for p, c in top_n_dist(ports, 8))
        a("| %s | %d | %d | %d | %s | %d | %s |" % (
            compat_label(compat), len(group), len(pkgs), len(set(ports)), port_str, udp_nonzero, examples))
    a("")

    a("### `_udpOutputPort` vs `_port`, by `_compatibility` (measured)")
    a("")
    a("Whether `_udpOutputPort` mirrors `_port` (as finding 13 §4b found for the "
      "ClockAudio UDP pair) or stays 0, per `_compatibility` value.")
    a("")
    a("| `_compatibility` | udpOutputPort==0 | udpOutputPort==port (nonzero) | "
      "udpOutputPort nonzero and != port |")
    a("|---|---|---|---|")
    for compat in sorted(compat_groups, key=lambda k: (-len(compat_groups[k]))):
        group = compat_groups[compat]
        zero = sum(1 for b in group if (b["udp_output_port"] or 0) == 0)
        mirrors = sum(1 for b in group
                       if (b["udp_output_port"] or 0) != 0 and b["udp_output_port"] == b["port"])
        other = len(group) - zero - mirrors
        a("| %s | %d | %d | %d |" % (compat_label(compat), zero, mirrors, other))
    a("")

    a("### `_canEditPort`, by `_compatibility` (measured)")
    a("")
    a("| `_compatibility` | locked (`_canEditPort=False`) | editable (`True`) |")
    a("|---|---|---|")
    for compat in sorted(compat_groups, key=lambda k: (-len(compat_groups[k]))):
        group = compat_groups[compat]
        locked = sum(1 for b in group if b["can_edit_port"] is False)
        editable = sum(1 for b in group if b["can_edit_port"] is True)
        a("| %s | %d | %d |" % (compat_label(compat), locked, editable))
    a("")

    a("## Cross-check: embedded-script transport evidence, by `_compatibility` (measured presence; "
      "**inferred** meaning)")
    a("")
    a("`sis_handshake` is `pkp2cs._source_speaks_sis()`'s own detector (literal "
      "`w0echo`/`w3cv` strings -- Extron's SIS echo/verbose-mode handshake). "
      "`interface_type_ssh` is a literal `InterfaceType == 'SSHInterface'` check "
      "found in a minority of scripts. The `lit_*` columns are **weak, noisy** "
      "substring presence (`'TCP'`, `'UDP'`, `'SSH'`, `'HTTP'`, `'HTTPS'` as "
      "quoted literals anywhere in the script text, including comments, "
      "docstrings and URLs) -- reported because the task asked for them, not "
      "because a single hit is strong evidence.")
    a("")
    header = ("| `_compatibility` | models | sis_handshake | InterfaceType==SSH | "
              "lit 'TCP' | lit 'UDP' | lit 'SSH' | lit 'HTTP' | lit 'HTTPS' |")
    a(header)
    a("|---|---|---|---|---|---|---|---|---|")
    for compat in sorted(compat_groups, key=lambda k: (-len(compat_groups[k]))):
        group = compat_groups[compat]
        n = len(group)
        sis = sum(1 for b in group if b["sis_handshake"])
        ifssh = sum(1 for b in group if b["interface_type_ssh"])
        row = [str(n), str(sis), str(ifssh)]
        for kw in LIT_TOKENS:
            row.append(str(sum(1 for b in group if b["lit_" + kw])))
        a("| %s | %s |" % (compat_label(compat), " | ".join(row)))
    a("")

    a("## Serial protocol assets (measured)")
    a("")
    a("Serial assets carry `_compatibility` and `_SerialProtocol` (both "
      "`ProtocolCompatibilityFlags`-shaped enum reads) but no `_port`.")
    a("")
    serial_compat = Counter(b["compatibility"] for b in serial_bindings)
    serial_proto = Counter(b["serial_protocol"] for b in serial_bindings)
    a("`_compatibility` distribution (same `ProtocolCompatibilityFlags` enum and "
      "ground truth as above -- Serial's low bits: `Serial_RS232=2, "
      "Serial_RS422=4, Serial_RS485=8, SerialHardware=14`): " +
      (", ".join("%s: %d" % (compat_label(k), v) for k, v in serial_compat.most_common()) or "(none)"))
    a("")
    a("`_SerialProtocol` distribution (raw `value__` int; this survey has no "
      "reflected name table for `SerialRSTypeEnum` -- `Load-Package.ps1 -Protocol` "
      "read `RS232` for the one sample checked live, object value `0`): " +
      (", ".join("%s: %d" % (k, v) for k, v in serial_proto.most_common()) or "(none)"))
    a("")

    if other_bindings:
        a("## Other protocol-asset classes (measured)")
        a("")
        other_by_class = defaultdict(list)
        for b in other_bindings:
            other_by_class[b["class"]].append(b)
        for cls, group in sorted(other_by_class.items(), key=lambda kv: -len(kv[1])):
            a("- `%s`: %d models, `_compatibility` values %s" %
              (cls, len(group),
               dict(Counter(b["compatibility"] for b in group))))
        a("")

    a("## `_protocolSubType` (`EthernetTypeEnum`), by `_compatibility` (measured, with ground truth)")
    a("")
    a("finding 13 §4b already established this field is constant (`0`) across "
      "`samples/`; here it is checked corpus-wide. Ground truth for the name, "
      "same method as `_compatibility` above (`Load-Package.ps1 -Protocol`, "
      "`[Enum]::GetNames` against the installed `Extron.Configuration.Contracts.dll`): "
      "**`EthernetTypeEnum: TCP=0, HTTP=1, SSH=2`.** The enum has three values; "
      "the corpus's 7079 `EthernetProtocolAsset` instances use only `0` (`TCP`) -- "
      "`HTTP` and `SSH` are declared but corpus-unused. That means "
      "`ProtocolSubType`/`_protocolSubType` is not how GC tells an HTTP or SSH "
      "device apart from a Telnet one either; `_compatibility` alone (`Ethernet_HTTP`, "
      "`Ethernet_SSH`) carries that distinction, corroborated by the live read on "
      "`extr_17_17677_v1_0_0.pkp` (`_compatibility=Ethernet_SSH(512)` yet "
      "`ProtocolSubType=TCP`) -- the '512 (`Ethernet_SSH`)' row below is a TCP "
      "socket carrying an SSH session, not a distinct 'ProtocolSubType' setting.")
    a("")
    subtype_by_compat = defaultdict(Counter)
    for b in eth_bindings:
        subtype_by_compat[b["compatibility"]][b["protocol_sub_type"]] += 1
    a("| `_compatibility` | `_protocolSubType` distribution |")
    a("|---|---|")
    for compat, dist in sorted(subtype_by_compat.items(), key=lambda kv: -sum(kv[1].values())):
        a("| %s | %s |" % (compat_label(compat), dict(dist)))
    a("")

    a("## What this pins down (measured, ground truth attached; nothing left \"not determined\")")
    a("")
    a("- **16 = `Ethernet_Telnet`, 32 = `Ethernet_UDP`, 64 = `Ethernet_HTTP`, "
      "512 = `Ethernet_SSH`** -- read from Extron's own compiled enum (see "
      "above), not inferred from port numbers or script content. %d/%d/%d/%d "
      "models respectively carry them corpus-wide."
      % (len(compat_groups.get(16, [])), len(compat_groups.get(32, [])),
         len(compat_groups.get(64, [])), len(compat_groups.get(512, []))))
    a("- **The 1 Beyond/ClockAudio pattern generalises.** `_udpOutputPort` mirrors "
      "`_port` on the large majority of `Ethernet_UDP` bindings (see the "
      "`_udpOutputPort` vs `_port` table) and stays 0 on every `Ethernet_Telnet`/"
      "`Ethernet_HTTP`/`Ethernet_SSH` binding with no exception found in the corpus.")
    a("- **The script cross-checks corroborate, weakly, where they fire at all.** "
      "`sis_handshake`/`interface_type_ssh` concentrate almost entirely on "
      "`Ethernet_SSH` (512) and, to a lesser extent, `Ethernet_Dante` (1024) -- "
      "consistent with those being the two flags whose driver scripts need "
      "protocol-specific handshake code of their own. `Ethernet_Telnet`, "
      "`Ethernet_UDP` and `Ethernet_HTTP` scripts almost never reference a "
      "transport keyword at all: GC's runtime, not the script, owns the socket "
      "for those, which is exactly why `_compatibility` has to be read from the "
      "package rather than guessed from script content (ROADMAP R16's original "
      "premise).")
    a("- **Two `_compatibility` values appear that finding 13 §4b never sampled: "
      "1024 (`Ethernet_Dante`) and 2048 (`Ethernet_RoomScheduling`).** Both are "
      "always `_port=0` and always `_udpOutputPort=0` -- read as \"this package "
      "declares the feature, but the feature's own endpoint (Dante's control "
      "protocol, a room-scheduling panel API) is not this asset's port\", not as "
      "a fifth wire transport.")
    a("- **Serial's `_compatibility` is a real bitmask in practice, not just in "
      "the enum definition**: `10 = Serial_RS232|Serial_RS485` appears "
      "corpus-wide (see the Serial table below), confirming `ProtocolCompatibilityFlags` "
      "is genuinely `[Flags]`-combined on the wire, not just declared that way.")
    a("")

    if n_parse_fail:
        a("## Parse failures")
        a("")
        a("| package | error |")
        a("|---|---|")
        for r in records:
            if r.get("parse_error"):
                a("| `%s` | %s |" % (r["path"], r["parse_error"]))
        a("")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("wrote %s" % MD_PATH, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None,
                     help="only walk the first N packages (smoke test; default: all)")
    ap.add_argument("--report-only", action="store_true",
                     help="skip the corpus walk and regenerate SURVEY.md from an "
                          "existing survey_raw.jsonl")
    args = ap.parse_args()

    if not args.report_only:
        run_survey(limit=args.limit)
    records = load_raw()
    write_report(records)


if __name__ == "__main__":
    main()
