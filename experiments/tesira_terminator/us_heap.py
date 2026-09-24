#!/usr/bin/env python3
"""us_heap.py - ROADMAP R19: settle the Biamp Tesira DeviceFaultList
terminator (\\r\\n vs \\n) offline, from Crestron's independent library.

Background (findings/11-spec-as-referee.md, "What the spec could not
adjudicate"): of 140+ command templates compared between the Extron .pkp /
translator-generated module and Extron's own shipped ControlScript module,
exactly one -- DeviceFaultList ("DEVICE get activeFaultList") -- disagrees
on line terminator: the .pkp and the generated module both use CRLF
("\\r\\n"), the shipped module uses LF only ("\\n"). Biamp's published TTP
grammar (reference/biamp-ttp/) does not specify a terminator either way, so
it cannot referee. This script settles it from a THIRD, independent
implementation: Crestron's own Tesira driver library.

Method
------
`samples/Tesira/Crestron/*/BiampTesiraLib3.clz` is a plain ZIP (a Crestron
SIMPL# "certified module") containing `BiampTesiraLib3.dll`, a .NET
assembly. Its ECMA-335 `#US` ("User Strings") metadata heap holds every
string literal (`ldstr`) compiled into the assembly, including every TTP
command-string template. No file offsets are hardcoded: this script reuses
`tools/pkg_dump.py`'s `PEImage` / `metadata_root` (PE header + CLI header +
metadata-stream-directory walker, already written and tested for
Crestron's .pkg format) to locate the `#US` heap, then walks it per ECMA-335
II.24.2.4 (each entry is a compressed-length-prefixed UTF-16LE blob with a
1-byte trailing flag; index 0 is always the empty string). That heap-walk
logic is new here (pkg_dump.py never needed the #US heap, only
ManifestResource), but it is implemented generically against the same
`PEImage`/`metadata_root` machinery, not against any offset specific to
this one file.

It also decompresses the Extron `.pkp` (gzip-wrapped) and regex-scans its
embedded GC Python source for every `cmdString = '...'` literal, to quantify
"the only one of 140+" directly from the artifact, and reads the exact line
from Extron's shipped ControlScript module for comparison.

Usage
-----
    py -3.11 -u experiments/tesira_terminator/us_heap.py
    py -3.11 -u experiments/tesira_terminator/us_heap.py --clz "<path-to-BiampTesiraLib3.clz>"

Run with no arguments from the repo root; it locates the two shipped .clz
files, the shipped .pkp, and the shipped ControlScript module by their
known repo-relative paths.
"""
import argparse
import gzip
import hashlib
import os
import re
import sys
import zipfile

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", ".."))
_TOOLS_DIR = os.path.join(_REPO_ROOT, "tools")
sys.path.insert(0, _TOOLS_DIR)
import pkg_dump  # noqa: E402  (repo tool; reused for PE/CLI metadata parsing)

DEFAULT_CLZ_PATHS = [
    os.path.join(_REPO_ROOT, "samples", "Tesira", "Crestron",
                 "Biamp Tesira v3.3 Demo IP CP3", "BiampTesiraLib3.clz"),
    os.path.join(_REPO_ROOT, "samples", "Tesira", "Crestron",
                 "Biamp Tesira v3.3 Demo RS232 CP3", "BiampTesiraLib3.clz"),
]
DEFAULT_PKP_PATH = os.path.join(
    _REPO_ROOT, "samples", "Tesira", "pkp", "biam_25_150_v1_20_0.pkp")
DEFAULT_EXTRON_SHIPPED_PATH = os.path.join(
    _REPO_ROOT, "samples", "Tesira", "controlscript",
    "biam_dsp_TesiraSeries_v1_18_3_0.py")

DLL_MEMBER_NAME = "BiampTesiraLib3.dll"


def repo_relative(path):
    """Repo-relative, forward-slashed form of `path`, for display only.
    Mirrors experiments/crestron2cs/crestron2cs.py's provenance_path()."""
    target = os.path.abspath(path)
    if target.startswith(_REPO_ROOT):
        rel = os.path.relpath(target, _REPO_ROOT)
        return rel.replace(os.sep, "/")
    return path.replace(os.sep, "/")


# ==========================================================================
# ECMA-335 II.24.2.4 "#US" heap walker (new; built on pkg_dump.py's PE/CLI
# metadata reader rather than any hardcoded offset)
# ==========================================================================

def read_compressed_u32(data, off):
    """ECMA-335 II.23.2 compressed unsigned integer, read starting at
    absolute file offset `off`. Returns (value, absolute_offset_of_the
    _first_byte_after_the_length_encoding)."""
    b0 = data[off]
    if b0 & 0x80 == 0:
        return b0, off + 1
    if b0 & 0xC0 == 0x80:
        b1 = data[off + 1]
        return ((b0 & 0x3F) << 8) | b1, off + 2
    if b0 & 0xE0 == 0xC0:
        b1, b2, b3 = data[off + 1], data[off + 2], data[off + 3]
        return ((b0 & 0x1F) << 24) | (b1 << 16) | (b2 << 8) | b3, off + 4
    raise pkg_dump.MetadataParseError(
        "invalid compressed integer lead byte 0x%02x at file offset %d" % (b0, off))


def walk_us_heap(data, us_off, us_size):
    """Walks the '#US' heap per ECMA-335 II.24.2.4.

    Yields (blob_index, text, raw_utf16le_bytes, trailing_byte_or_None) for
    every non-empty entry. `blob_index` is the offset relative to the start
    of the heap (i.e. the value an ldstr token's low 24 bits would encode).
    Entry 0 is always a single 0x00 byte marking the empty string and is
    skipped. Every other entry is:
        <compressed length L><L-1 bytes of UTF-16LE><1 trailing flag byte>
    when L is odd (the normal case: L = 2*charcount + 1), or, if a producer
    ever emits an even length with no trailing byte, <L bytes of UTF-16LE>
    with no flag byte -- both forms are handled.
    """
    end = us_off + us_size
    pos = us_off
    while pos < end:
        blob_index = pos - us_off
        length, data_start = read_compressed_u32(data, pos)
        if length == 0:
            pos = data_start
            continue
        if length % 2 == 1:
            str_bytes = data[data_start: data_start + length - 1]
            trailing = data[data_start + length - 1]
        else:
            str_bytes = data[data_start: data_start + length]
            trailing = None
        text = str_bytes.decode("utf-16-le", "replace")
        pos = data_start + length
        yield blob_index, text, str_bytes, trailing


def load_us_heap_entries(clz_path):
    """Extracts BiampTesiraLib3.dll from a .clz (plain ZIP) and returns
    (dll_sha256, us_heap_file_offset, us_heap_size, [entries...])."""
    with zipfile.ZipFile(clz_path) as z:
        dll_bytes = z.read(DLL_MEMBER_NAME)
    dll_sha256 = hashlib.sha256(dll_bytes).hexdigest()

    pe = pkg_dump.PEImage(dll_bytes)
    cor20 = pe.cor20_header()
    streams = pe.metadata_root(cor20["metadata_rva"], cor20["metadata_size"])
    if "#US" not in streams:
        raise pkg_dump.MetadataParseError(
            "%s: no #US heap present in metadata streams %r" %
            (clz_path, sorted(streams.keys())))
    us_off, us_size = streams["#US"]
    entries = list(walk_us_heap(dll_bytes, us_off, us_size))
    return dll_sha256, us_off, us_size, entries


def read_strings_heap_names(clz_path):
    """Returns the sorted set of every name in the '#Strings' heap (type,
    method and field names) -- used only to check whether 'FaultList' is
    reflected anywhere as an identifier, not just as a literal."""
    with zipfile.ZipFile(clz_path) as z:
        dll_bytes = z.read(DLL_MEMBER_NAME)
    pe = pkg_dump.PEImage(dll_bytes)
    cor20 = pe.cor20_header()
    streams = pe.metadata_root(cor20["metadata_rva"], cor20["metadata_size"])
    strings_off, strings_size = streams["#Strings"]
    names = []
    p = strings_off
    end = strings_off + strings_size
    while p < end:
        z_ = dll_bytes.index(b"\x00", p)
        s = dll_bytes[p:z_].decode("utf-8", "replace")
        if s:
            names.append(s)
        p = z_ + 1
    return names


# ==========================================================================
# The .pkp side: decompress and regex-scan the embedded GC Python source
# ==========================================================================

CMDSTRING_RE = re.compile(r"cmdString\s*=\s*'((?:[^'\\]|\\.)*)'")


def scan_pkp_cmdstrings(pkp_path):
    """Decompresses the gzip-wrapped .pkp and finds every literal
    `cmdString = '...'` assignment in its embedded GC Python source,
    classified by terminator. Returns a dict with counts and examples."""
    with open(pkp_path, "rb") as f:
        raw_gz = f.read()
    text = gzip.decompress(raw_gz).decode("latin-1")

    crlf, lf_only, neither = [], [], []
    for m in CMDSTRING_RE.finditer(text):
        s = m.group(1)
        if s.endswith("\\r\\n"):
            crlf.append(s)
        elif s.endswith("\\n"):
            lf_only.append(s)
        else:
            neither.append(s)
    return {
        "total": len(crlf) + len(lf_only) + len(neither),
        "crlf": crlf,
        "lf_only": lf_only,
        "neither": neither,
    }


# ==========================================================================
# The Extron shipped ControlScript module side
# ==========================================================================

def find_shipped_devicefaultlist_line(py_path):
    with open(py_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if "cmdString" in line and "activeFaultList" in line:
                return lineno, line.rstrip("\n")
    return None, None


# ==========================================================================
# Report
# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--clz", action="append", default=None,
                     help="Path to a BiampTesiraLib3.clz (repeatable). "
                          "Default: both shipped IP and RS232 copies.")
    ap.add_argument("--pkp", default=DEFAULT_PKP_PATH,
                     help="Path to the Tesira .pkp (gzip-wrapped).")
    ap.add_argument("--shipped", default=DEFAULT_EXTRON_SHIPPED_PATH,
                     help="Path to Extron's shipped ControlScript module.")
    args = ap.parse_args()

    clz_paths = args.clz or DEFAULT_CLZ_PATHS

    print("=" * 78)
    print("R19: Biamp Tesira DeviceFaultList terminator -- settle from")
    print("Crestron's independent library (BiampTesiraLib3.dll, #US heap)")
    print("=" * 78)

    # ---- 1. Crestron library: #US heap contents ----
    seen_hashes = {}
    for clz_path in clz_paths:
        if not os.path.isfile(clz_path):
            print("\n[SKIP] not found: %s" % repo_relative(clz_path))
            continue
        print("\n--- %s ---" % repo_relative(clz_path))
        sha256, us_off, us_size, entries = load_us_heap_entries(clz_path)
        seen_hashes[repo_relative(clz_path)] = sha256
        print("BiampTesiraLib3.dll SHA-256: %s" % sha256)
        print("#US heap: file offset 0x%x, size %d bytes, %d entries" %
              (us_off, us_size, len(entries)))

        fault_hits = [e for e in entries if "faultlist" in e[1].lower()]
        print("\n  Entries containing 'FaultList' (any case): %d" % len(fault_hits))
        for idx, text, raw, trailing in fault_hits:
            print("    US[0x%06x] %r" % (idx, text))
        if not fault_hits:
            print("    (none -- 'activeFaultList'/'DeviceFaultList' is not a literal")
            print("     anywhere in the #US heap; not found by direct search)")

        names = read_strings_heap_names(clz_path)
        name_hits = [n for n in names if "faultlist" in n.lower()]
        print("\n  #Strings heap (type/method/field names) containing 'FaultList': %d" %
              len(name_hits))
        for n in name_hits:
            print("    %s" % n)
        if not name_hits:
            print("    (none -- not reflected as an identifier either, by method X ="
                  " scanning #Strings heap)")

        print("\n  Entries that are exactly a bare terminator (CR, LF, or CRLF):")
        for idx, text, raw, trailing in entries:
            if text in ("\r", "\n", "\r\n", "\n\r"):
                print("    US[0x%06x] repr=%r  raw=%s" % (idx, text, raw.hex()))

        print("\n  Generic command-template literals ending in a terminator")
        print("  (these are what builds EVERY attribute get/set command, including")
        print("  ones with no dedicated method -- activeFaultList has none, see above):")
        templates = [e for e in entries
                     if e[1].startswith('"{0}"') or re.match(r"^\{0\}\s", e[1])]
        for idx, text, raw, trailing in templates:
            print("    US[0x%06x] %r" % (idx, text))
        n_crlf_templates = sum(1 for _, t, _, _ in templates if t.endswith("\r\n"))
        n_lf_templates = sum(1 for _, t, _, _ in templates if t.endswith("\n") and not t.endswith("\r\n"))
        print("  -> %d generic templates end in LF only, %d end in CRLF" %
              (n_lf_templates, n_crlf_templates))

        print("\n  Session-establishment literals near the bare '\\r'/'\\n' entries")
        print("  (context: these sit next to 'login:', consistent with receive-side")
        print("  line parsing, not an outgoing command terminator):")
        lo = min(idx for idx, t, r, tr in entries if t == "login:") if any(t == "login:" for _, t, _, _ in entries) else None
        for idx, text, raw, trailing in entries:
            if lo is not None and lo - 0x10 <= idx <= lo + 0x230:
                print("    US[0x%06x] %r" % (idx, text))

    if len(set(seen_hashes.values())) == 1 and len(seen_hashes) > 1:
        print("\n[NOTE] All scanned .clz copies embed the byte-identical DLL")
        print("       (same SHA-256) -- IP and RS232 transports share one library,")
        print("       so this is not a transport-specific artifact.")

    # ---- 2. .pkp: cmdString census ----
    print("\n" + "=" * 78)
    print(".pkp cmdString census (Extron's own GC script source, decompressed)")
    print("=" * 78)
    if os.path.isfile(args.pkp):
        stats = scan_pkp_cmdstrings(args.pkp)
        print("Path: %s" % repo_relative(args.pkp))
        print("Total cmdString literals found: %d" % stats["total"])
        print("  ending '\\r\\n': %d" % len(stats["crlf"]))
        for s in stats["crlf"]:
            print("    %r" % s)
        print("  ending '\\n' only: %d" % len(stats["lf_only"]))
        print("  neither (empty / other): %d" % len(stats["neither"]))
    else:
        print("[SKIP] not found: %s" % repo_relative(args.pkp))

    # ---- 3. Extron shipped module: exact line ----
    print("\n" + "=" * 78)
    print("Extron shipped ControlScript module")
    print("=" * 78)
    if os.path.isfile(args.shipped):
        lineno, line = find_shipped_devicefaultlist_line(args.shipped)
        print("Path: %s" % repo_relative(args.shipped))
        if lineno:
            print("Line %d: %s" % (lineno, line.strip()))
        else:
            print("[NOT FOUND] no cmdString line mentioning activeFaultList "
                  "(not found by direct source scan)")
    else:
        print("[SKIP] not found: %s" % repo_relative(args.shipped))

    print("\n" + "=" * 78)
    print("See experiments/tesira_terminator/RESULT.md for the verdict.")
    print("=" * 78)


if __name__ == "__main__":
    main()
