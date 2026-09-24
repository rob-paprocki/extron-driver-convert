#!/usr/bin/env python3
"""Mechanical endpoint-level cross-reference: extract every 'api/Xxx' / 'get-token'
URI literal referenced in (a) the generated module, (b) Extron's shipped module,
and classify against the documented endpoint set. Supplements wire_table's
command-NAME-keyed diff, which undercounts here because the two modules use
different command-naming abstractions for the same endpoints.

ROADMAP R32 (2026-09-23): the endpoint classification used to be two hand-
maintained Python sets (OFFICIAL_32, SUBAPI_EXAMPLE_ONLY), frozen at the size
of the harvest that existed when they were written. That is exactly the
mistake finding 08 made once already (declaring absence from a fixed,
un-refreshed search rather than checking the corpus directly) -- so this
version derives "has a dedicated doc page" by scanning
reference/automate-vx-api/API-Reference/*.md for each page's own `Base URI`
line, every run. A set that can go stale again would repeat the bug this
file exists to avoid.

The "example-only" sub-API list (endpoints named solely inside
ENDPOINTS.md's "Undocumented sub-APIs" section, sourced from GetAllStatus's
example response body, with no page of their own) is still hand-transcribed
from that section, because it is not mechanically re-derivable from the
file scan -- the scan can only prove a page EXISTS, not enumerate names
that have no page. Any name in this list that the scan finds now DOES have
a dedicated page is dropped from it automatically (see build_documented_uris()).
"""
import re, json, pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
GEN = pathlib.Path(__file__).parent / "automate_vx_docs_only.py"
SHIP = ROOT / "samples/Automate VX/Controlscript/onebynd_sm_Automate_VX_Series_v1_0_11_0.py"
API_REF_DIR = ROOT / "reference/automate-vx-api/API-Reference"

# Named only inside ENDPOINTS.md's "Undocumented sub-APIs" section (sourced
# from GetAllStatus's example response body), as of the last read of that
# section (2026-09-07 harvest). This project's own re-harvest (R32,
# 2026-09-23) found dedicated pages for 8 of these 9 -- see
# build_documented_uris(), which removes any name below that now has a page.
# Kept as the full original 9 so a removal is visible (diffed against
# DOCUMENTED_URIS) rather than silently edited away.
SUBAPI_NAMED_IN_ENDPOINTS_MD = {
    "api/AutoSwitchStatus", "api/OutputStatus", "api/ISORecordStatus",
    "api/RecordStatus", "api/CopyStatus", "api/GetLayouts", "api/LayoutStatus",
    "api/GetRoomConfigs", "api/RoomConfigStatus",
}

BASE_URI_RE = re.compile(r"\*\*Base URI\*\*:\s*/(\S+)")


def build_documented_uris():
    """Scan every harvested API-Reference page for its own `Base URI` line.
    Returns (documented, by_file) where `documented` is the set of URIs
    ('get-token' or 'api/Xxx') that have a dedicated page, and `by_file`
    maps each URI to the harvested filename it came from."""
    documented = set()
    by_file = {}
    for md in sorted(API_REF_DIR.glob("*.md")):
        text = md.read_text(encoding="utf-8")
        m = BASE_URI_RE.search(text)
        if not m:
            continue  # e.g. API-Reference.md itself is an index page, not an endpoint
        uri = m.group(1)
        documented.add(uri)
        by_file[uri] = md.name
    return documented, by_file


DOCUMENTED_URIS, DOCUMENTED_BY_FILE = build_documented_uris()

# Sub-APIs still named only inside ENDPOINTS.md with no dedicated page found
# by the scan above (recomputed every run, not hardcoded).
SUBAPI_EXAMPLE_ONLY = SUBAPI_NAMED_IN_ENDPOINTS_MD - DOCUMENTED_URIS

# Sub-APIs that WERE example-only at last count but now have a dedicated page
# -- i.e. what this re-harvest actually changed. Printed, not asserted, since
# the point of this script is to measure, not to re-freeze a number.
SUBAPI_PROMOTED_TO_DOCUMENTED = SUBAPI_NAMED_IN_ENDPOINTS_MD & DOCUMENTED_URIS


def extract_uris(path):
    src = path.read_text()
    return set(re.findall(r"'(get-token|api/[A-Za-z]+)'", src))


def classify(uri):
    if uri in DOCUMENTED_URIS:
        return "OFFICIAL"
    if uri in SUBAPI_EXAMPLE_ONLY:
        return "EXAMPLE_ONLY"
    return "DOC_GAP"


def main():
    gen_uris = extract_uris(GEN)
    ship_uris = extract_uris(SHIP)

    print("=== reference/automate-vx-api/API-Reference/ harvest, as scanned today ===")
    print("dedicated-page endpoints found:", len(DOCUMENTED_URIS))
    print("sub-APIs promoted from example-only to dedicated-page by this harvest (%d):"
          % len(SUBAPI_PROMOTED_TO_DOCUMENTED), sorted(SUBAPI_PROMOTED_TO_DOCUMENTED))
    print("sub-APIs still example-only (named in ENDPOINTS.md, no page found) (%d):"
          % len(SUBAPI_EXAMPLE_ONLY), sorted(SUBAPI_EXAMPLE_ONLY))
    print()

    print("=== generated module: endpoint URIs referenced ===")
    for u in sorted(gen_uris):
        print(" ", u, classify(u))
    print("count:", len(gen_uris))

    print()
    print("=== Extron shipped module: endpoint URIs referenced ===")
    for u in sorted(ship_uris):
        print(" ", u, classify(u))
    print("count:", len(ship_uris))

    print()
    print("=== classification of the diff ===")
    only_ship = ship_uris - gen_uris
    only_gen = gen_uris - ship_uris
    both = gen_uris & ship_uris

    print("-- in Extron shipped but NOT in generated (by URI) --")
    for u in sorted(only_ship):
        print(" ", u, classify(u))

    print("-- in generated but NOT in Extron shipped (by URI) --")
    for u in sorted(only_gen):
        print(" ", u, classify(u))

    print("-- in both (by URI) --")
    for u in sorted(both):
        print(" ", u, classify(u))

    official_covered_by_both = {u for u in both if u in DOCUMENTED_URIS}
    official_only_ship = {u for u in only_ship if u in DOCUMENTED_URIS}
    official_only_gen = {u for u in only_gen if u in DOCUMENTED_URIS}
    print()
    print("official endpoint coverage: both=%d, extron-only=%d, generated-only(unimplemented-by-extron)=%d, total-official=%d"
          % (len(official_covered_by_both), len(official_only_ship), len(official_only_gen), len(DOCUMENTED_URIS)))

    subapi_covered_by_both = {u for u in both if u in SUBAPI_EXAMPLE_ONLY}
    subapi_only_gen = {u for u in only_gen if u in SUBAPI_EXAMPLE_ONLY}
    print("sub-api (example-only) coverage: both=%d, generated-only=%d, total-listed=%d"
          % (len(subapi_covered_by_both), len(subapi_only_gen), len(SUBAPI_NAMED_IN_ENDPOINTS_MD)))

    doc_gap_in_ship = {u for u in ship_uris if classify(u) == "DOC_GAP"}
    print("DOC GAP (Extron calls, appears nowhere in corpus):", sorted(doc_gap_in_ship))

    # Headline figure, computed the way finding 08 computed it: of the URIs
    # Extron's shipped module actually calls, how many have a dedicated page?
    ship_official = {u for u in ship_uris if classify(u) == "OFFICIAL"}
    ship_docgap = {u for u in ship_uris if classify(u) == "DOC_GAP"}
    print()
    print("finding-08-style headline: Extron calls %d endpoint URIs; %d have a dedicated page, %d do not -- %s"
          % (len(ship_uris), len(ship_official), len(ship_docgap),
             sorted(ship_docgap)))


if __name__ == "__main__":
    main()
