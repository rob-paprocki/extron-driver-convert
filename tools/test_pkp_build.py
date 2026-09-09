#!/usr/bin/env python3
"""
test_pkp_build.py - offline gate for tools/pkp_build.py.

The hardware battery in experiments/skeleton_i20/PROTOCOL.md is expensive to
run (it costs a trip to a system this repo has no access to), so everything
that can be settled at a desk is settled here first. Three properties matter:

  1. Every real package in samples/ round-trips byte-for-byte through the
     builder. If it does not, we do not understand the graph.
  2. A substitution changes what it was asked to change and nothing else -
     checked by re-parsing the OUTPUT and diffing the object graph, not by
     trusting the writer.
  3. Substitutions of a different length work, since a synthesised driver is
     never the same size as the donor's. This is the property nrbf_write.py's
     own tests do not cover.

Run: python3 tools/test_pkp_build.py
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import pkp_dump as pd            # noqa: E402
import pkp_build as pb           # noqa: E402


PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def all_packages():
    out = []
    for root, _dirs, files in os.walk(os.path.join(_ROOT, "samples")):
        for f in files:
            if f.endswith(".pkp"):
                out.append(os.path.join(root, f))
    return sorted(out)


def camera_donor():
    for p in all_packages():
        if os.path.basename(p).startswith("1bynd_19_4743"):
            return p
    raise SystemExit("camera donor 1bynd_19_4743 not found under samples/")


# ---------------------------------------------------------------------------

def test_all_donors_round_trip():
    print("\n[1] every sample package round-trips byte-identically")
    for p in all_packages():
        name = os.path.basename(p)
        try:
            b = pb.PackageBuilder(p)          # raises RoundTripError on failure
            same = b.raw_bytes() == b.raw
        except pb.RoundTripError as e:
            same = False
            print("      %s" % e)
        check("round-trip %s" % name, same)


def test_unmutated_build_is_stable():
    print("\n[2] an unmutated build reproduces the donor's NRBF stream")
    b = pb.PackageBuilder(camera_donor())
    check("uncompressed build == donor raw", b.build(compress=False) == b.raw)
    check("no edits recorded", b.edits == [])


def test_scripts_discovered():
    print("\n[3] the embedded driver is found and is the 1 Beyond VISCA module")
    b = pb.PackageBuilder(camera_donor())
    slots = b.scripts()
    check("exactly one .py slot", len(slots) == 1,
          "found %r" % [s.key for s in slots])
    if not slots:
        return
    s = slots[0]
    check("key names the package", s.key.endswith(".py"), s.key)
    check("source is VISCA", "0xFF" in s.source or "DeviceID" in s.source)
    check("source parses as Python", _compiles(s.source))


def _compiles(src):
    try:
        compile(src, "<embedded>", "exec")
        return True
    except SyntaxError:
        return False


def test_script_substitution_same_length():
    print("\n[4] equal-length substitution changes only the payload")
    b = pb.PackageBuilder(camera_donor())
    slot = b.scripts()[0]
    original = slot.source
    # Same byte count, different content: flip a comment marker in place.
    mutated = "# padded ----\n" + original[len("# padded ----\n"):]
    check("test fixture is equal length",
          len(mutated.encode()) == len(original.encode()))
    b.replace_script(slot.key, mutated)
    out = b.build(compress=False)
    check("output is the same size as the donor", len(out) == len(b.raw))
    check("output differs from the donor", out != b.raw)
    reread = _scripts_of_raw(out)
    check("re-parsed output carries the mutation",
          reread.get(slot.key, "").startswith("# padded ----"))


def test_script_substitution_different_length():
    print("\n[5] different-length substitution rewrites the array length")
    b = pb.PackageBuilder(camera_donor())
    slot = b.scripts()[0]
    tiny = "class DeviceClass:\n    pass\n"
    old, new = b.replace_script(slot.key, tiny)
    check("reported old length matches source",
          old == len(slot.source.encode("utf-8")), "%d" % old)
    check("reported new length matches replacement",
          new == len(tiny.encode("utf-8")), "%d" % new)
    out = b.build(compress=False)
    check("output shrank by the byte difference",
          len(b.raw) - len(out) == old - new,
          "delta=%d expected=%d" % (len(b.raw) - len(out), old - new))
    reread = _scripts_of_raw(out)
    check("re-parsed output carries the short script", reread.get(slot.key) == tiny)


def test_growth_substitution():
    print("\n[6] a LARGER script also works (the synthesised-driver case)")
    b = pb.PackageBuilder(camera_donor())
    slot = b.scripts()[0]
    bigger = slot.source + "\n# " + ("x" * 50000) + "\n"
    old, new = b.replace_script(slot.key, bigger)
    out = b.build(compress=False)
    check("output grew by the byte difference",
          len(out) - len(b.raw) == new - old,
          "delta=%d expected=%d" % (len(out) - len(b.raw), new - old))
    reread = _scripts_of_raw(out)
    check("re-parsed output carries the larger script", reread.get(slot.key) == bigger)


def test_only_intended_object_changes():
    print("\n[7] substitution leaves every other object in the graph untouched")
    b = pb.PackageBuilder(camera_donor())
    slot = b.scripts()[0]
    before = _graph_fingerprint(b.raw)
    b.replace_script(slot.key, "class DeviceClass:\n    pass\n")
    after = _graph_fingerprint(b.build(compress=False))
    check("same object ids present", set(before) == set(after),
          "added=%s removed=%s" % (sorted(set(after) - set(before))[:5],
                                   sorted(set(before) - set(after))[:5]))
    differing = sorted(k for k in before if before[k] != after.get(k))
    # TWO objects, not one: replace_script also refreshes the stored SHA-256,
    # because a package whose script disagrees with its digest is rejected by
    # GC at selection time (error 80085 - see findings/15). Verified against
    # Extron's own DriverAssetValidator.
    hash_id = b.resource_hashes()[slot.key][0]
    expected = sorted([slot.content_id, hash_id])
    check("exactly two objects differ: the script and its digest",
          len(differing) == 2, "differing=%s expected=%s" % (differing[:8], expected))
    check("and they are the right two", differing == expected,
          "changed %s, expected %s" % (differing, expected))

    # Without the refresh, exactly one object changes - which is precisely the
    # package GC refuses. Kept as the control for the pair above.
    b2 = pb.PackageBuilder(camera_donor())
    s2 = b2.scripts()[0]
    b2.replace_script(s2.key, "class DeviceClass:\n    pass\n", refresh_hash=False)
    only = [k for k in before if before[k] != _graph_fingerprint(b2.build(compress=False)).get(k)]
    check("refresh_hash=False changes only the script", only == [s2.content_id],
          "differing=%s" % only[:8])


def test_string_substitution():
    print("\n[8] string substitution targets exactly one object")
    b = pb.PackageBuilder(camera_donor())
    strings = b.strings()
    oid = sorted(strings)[len(strings) // 2]
    before = b.replace_string(oid, "TRANSPLANT-MARKER")
    out = b.build(compress=False)
    after = _strings_of_raw(out)
    check("target string changed", after.get(oid) == "TRANSPLANT-MARKER",
          "was %r" % before)
    others_before = {k: v for k, v in strings.items() if k != oid}
    others_after = {k: v for k, v in after.items() if k != oid}
    check("no other string changed", others_before == others_after)


def test_refuses_to_bypass_the_gate():
    print("\n[9] the round-trip gate cannot be skipped")
    check("PackageBuilder has no bypass flag",
          "force" not in pb.PackageBuilder.__init__.__code__.co_varnames,
          str(pb.PackageBuilder.__init__.__code__.co_varnames))
    try:
        pb.PackageBuilder(os.path.join(_ROOT, "tools", "pkp_build.py"))
        ok = False
    except Exception:
        ok = True
    check("a non-package donor raises rather than building", ok)


def test_missing_script_is_loud():
    print("\n[10] a bad substitution name fails loudly, not silently")
    b = pb.PackageBuilder(camera_donor())
    try:
        b.replace_script("not_a_real_script.py", "pass\n")
        ok = False
    except pb.TransplantError:
        ok = True
    check("unknown script key raises TransplantError", ok)
    try:
        pb.mutate_primitive_array_by_object_id(b.trace, 9999999, b"x")
        ok = False
    except pb.TransplantError:
        ok = True
    check("unknown array object id raises TransplantError", ok)


def test_gzip_output_is_loadable():
    print("\n[11] the gzipped artefact is what pkp_dump would read back")
    b = pb.PackageBuilder(camera_donor())
    slot = b.scripts()[0]
    b.replace_script(slot.key, "class DeviceClass:\n    pass\n")
    import gzip
    packed = b.build(compress=True)
    check("output is gzip", packed[:2] == b"\x1f\x8b")
    check("gunzips to the built stream",
          gzip.decompress(packed) == b.build(compress=False))


# -- helpers ----------------------------------------------------------------

def _scripts_of_raw(raw):
    parser = pd.PkpParser(raw)
    parser.parse()
    out = {}
    for v in parser.objects.values():
        if not (isinstance(v, dict) and v.get("class") == pb.STREAM_ASSET_CLASS):
            continue
        m = v.get("members", {})
        key = pb.deref(parser.objects, m.get("ResourceAssetBase+_key"))
        content = pb.deref(parser.objects, m.get("ResourceAssetBase+_content"))
        if isinstance(key, str) and key.endswith(".py") and isinstance(content, dict):
            out[key] = bytes(content["items"]).decode("utf-8")
    return out


def _strings_of_raw(raw):
    parser = pd.PkpParser(raw)
    parser.parse()
    return {oid: v for oid, v in parser.objects.items() if isinstance(v, str)}


def _graph_fingerprint(raw):
    """{object_id: cheap stable summary} for every object, so 'what changed'
    is answered by re-reading the output rather than by trusting the writer."""
    parser = pd.PkpParser(raw)
    parser.parse()
    fp = {}
    for oid, v in parser.objects.items():
        if isinstance(v, dict) and v.get("$type") == "ArraySinglePrimitive":
            fp[oid] = ("arr", v.get("primitive_type"), len(v.get("items", [])),
                       hash(bytes(v["items"])) if v.get("items") else 0)
        elif isinstance(v, str):
            fp[oid] = ("str", v)
        elif isinstance(v, dict):
            fp[oid] = ("obj", v.get("class"), tuple(sorted(v.get("members", {}))))
        else:
            fp[oid] = ("val", repr(v)[:80])
    return fp


def main():
    print("test_pkp_build.py - offline gate for the .pkp transplant builder")
    for fn in (test_all_donors_round_trip,
               test_unmutated_build_is_stable,
               test_scripts_discovered,
               test_script_substitution_same_length,
               test_script_substitution_different_length,
               test_growth_substitution,
               test_only_intended_object_changes,
               test_string_substitution,
               test_refuses_to_bypass_the_gate,
               test_missing_script_is_loud,
               test_gzip_output_is_loadable):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
