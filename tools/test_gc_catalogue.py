#!/usr/bin/env python3
"""
test_gc_catalogue.py - gate for tools/gc_catalogue.py.

The fixtures are real catalogues written by Global Configurator, not
synthetic ones:

  experiments/skeleton_i20/hardware/DriverLookup.{before,after}.dat
      from the external test system, either side of the GC rebuild in
      finding 15: none of our packages before, all four after.

  corpus/extron-driver3/DriverLookup.dat
      the Windows box's catalogue, captured together with the folder it
      indexes, so the two can be compared entry for entry. Skipped when
      corpus/ is absent - it is 1.3 GB and a clone may leave it out.

Run: python3 tools/test_gc_catalogue.py
"""

import contextlib
import io
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import gc_catalogue as gc        # noqa: E402
import vendor_inputs             # noqa: E402

PASS = []
FAIL = []

HW = os.path.join(_ROOT, "experiments", "skeleton_i20", "hardware")
BEFORE = os.path.join(HW, "DriverLookup.before.dat")
AFTER = os.path.join(HW, "DriverLookup.after.dat")
A_PACKAGE = os.path.join(_ROOT, "experiments", "skeleton_i20", "out", "1bynd_19_20024_v1_0_0.pkp")
CORPUS = os.path.join(_ROOT, "corpus", "extron-driver3")

STAGED = ["1bynd_19_20020_v1_0_0.pkp", "1bynd_19_20021_v1_0_0.pkp",
          "1bynd_19_20022_v1_0_0.pkp", "1bynd_19_20023_v1_0_0.pkp"]


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def quiet(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return fn(*a)


def ours(entries):
    return [e for e in entries if e.startswith("1bynd_19_200")]


# ---------------------------------------------------------------------------

def test_before_and_after_the_rebuild():
    print("\n[1] finding 15's rebuild, read back from GC's own catalogue")
    before = gc.lookup_entries(BEFORE)
    after = gc.lookup_entries(AFTER)
    check("before the rebuild: none of our packages", ours(before) == [], str(before))
    check("after: exactly the four staged packages", ours(after) == STAGED, str(ours(after)))
    check("the rebuild changed nothing else",
          set(after) - set(STAGED) == set(before),
          "before=%s after=%s" % (before, after))


def test_only_package_names_are_counted():
    print("\n[2] entries are package filenames, not every string in the stream")
    after = gc.lookup_entries(AFTER)
    check("every entry ends in .pkp or .eir",
          all(e.lower().endswith((".pkp", ".eir")) for e in after), str(after))
    check("entries are unique and sorted", after == sorted(set(after)))


def test_rejects_what_is_not_a_catalogue():
    print("\n[3] a non-catalogue is refused, not misread")
    cases = [("empty input", b""), ("plain text", b"DriverLookup\n")]
    if os.path.isfile(A_PACKAGE):
        cases.insert(0, ("a gzipped .pkp", open(A_PACKAGE, "rb").read()))
    else:
        print("  skip a gzipped .pkp: vendor input not present (see vendor-files.manifest.tsv)")
    for label, data in cases:
        try:
            gc.lookup_entries(data)
            ok = False
        except gc.CatalogueError:
            ok = True
        check("%s raises CatalogueError" % label, ok)


def test_cli_exit_codes():
    print("\n[4] the CLI's exit codes mean what they say")
    check("--has a catalogued package exits 0", quiet(gc.main, [AFTER, "--has", "1bynd_19_20023"]) == 0)
    check("--has a missing package exits 1", quiet(gc.main, [AFTER, "--has", "no_such_driver"]) == 1)
    check("a .pkp in place of a catalogue exits 2", quiet(gc.main, [A_PACKAGE]) == 2)


def test_corpus_catalogue_matches_its_folder():
    print("\n[5] the corpus catalogue indexes exactly the folder it was captured with")
    lookup = os.path.join(CORPUS, "DriverLookup.dat")
    if not os.path.isfile(lookup):
        print("  skip corpus/ not present")
        return
    entries = gc.lookup_entries(lookup)
    missing, uncatalogued = gc.compare(entries, CORPUS)
    check("every package in the folder is catalogued", not uncatalogued,
          "%d uncatalogued, e.g. %s" % (len(uncatalogued), uncatalogued[:5]))
    check("nothing catalogued is absent from the folder", not missing,
          "%d missing, e.g. %s" % (len(missing), missing[:5]))
    check("it includes the package this project built",
          "1bynd_19_20024_v1_0_0.pkp" in entries)


def main():
    print("test_gc_catalogue.py - gate for the Global Configurator catalogue reader")
    skipped = 0
    for fn in (test_before_and_after_the_rebuild,
               test_only_package_names_are_counted,
               test_rejects_what_is_not_a_catalogue,
               test_cli_exit_codes,
               test_corpus_catalogue_matches_its_folder):
        try:
            fn()
        except Exception as e:  # noqa: BLE001
            why = vendor_inputs.vendor_missing(e)
            if not why:
                raise
            skipped += 1
            print("  SKIP %s - %s" % (fn.__name__, why))
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total; %d section(s) skipped (vendor input absent)"
          % (len(PASS), len(FAIL), total, skipped))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
