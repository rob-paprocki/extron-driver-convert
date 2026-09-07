#!/usr/bin/env python3
"""
test_nrbf_write.py - tests for nrbf_write.py (Q1a: can we WRITE a .pkp's
underlying NRBF stream at all?).

No pytest is installed in this environment, so these are plain test_*
functions collected and run by the __main__ block at the bottom (asserts
only, no fixtures), same style as tools/test_pkg_dump.py.

Run: python3 experiments/nrbf_writeback/test_nrbf_write.py
"""
import gzip
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))

import pkp_dump as pd            # noqa: E402
import nrbf_write as nw          # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SAMSUNG = os.path.join(REPO_ROOT, "samples", "Samsung QNxxLS03DAFXZA", "pkp", "smsg_10_6738_v1_0_0.pkp")
DSC = os.path.join(REPO_ROOT, "samples", "DSC_12G-HD", "pkp", "extr_17_17677_v1_0_0.pkp")
DTP3 = os.path.join(REPO_ROOT, "samples", "DTP3 CP 42", "pkp", "extr_15_17578_v1_3_0.pkp")
AUTOMATE_VX = os.path.join(REPO_ROOT, "samples", "Automate VX", "pkp", "1bynd_42_4279_v1_0_11.pkp")

ALL_PKPS = [SAMSUNG, DSC, DTP3, AUTOMATE_VX]


def _require_samples():
    missing = [p for p in ALL_PKPS if not os.path.isfile(p)]
    assert not missing, "missing sample .pkp files: %r" % missing


# --------------------------------------------------------------------------
# Writer primitives: exact inverse of pkp_dump.Reader, checked directly
# against struct-level expectations (not just round-tripped through
# themselves, which would tautologically always pass).
# --------------------------------------------------------------------------
def test_write_int32_matches_struct_little_endian():
    w = nw.Writer()
    w.write_int32(-1)
    assert w.bytes() == b"\xff\xff\xff\xff"
    w2 = nw.Writer()
    w2.write_int32(1)
    assert w2.bytes() == b"\x01\x00\x00\x00"


def test_write_7bit_encoded_int_matches_dotnet_canonical_form():
    # Canonical Write7BitEncodedInt: values < 128 are one byte with no
    # continuation bit; 128 needs a second byte since 7 bits alone can't
    # hold it.
    w = nw.Writer()
    w.write_7bit_encoded_int(127)
    assert w.bytes() == b"\x7f"
    w2 = nw.Writer()
    w2.write_7bit_encoded_int(128)
    assert w2.bytes() == b"\x80\x01"
    w3 = nw.Writer()
    w3.write_7bit_encoded_int(300)  # 300 = 0b1_0010_1100
    assert w3.bytes() == b"\xac\x02"


def test_write_7bit_encoded_int_inverts_reader_read_7bit_encoded_int():
    for value in (0, 1, 63, 64, 127, 128, 129, 300, 16383, 16384, 2_000_000):
        w = nw.Writer()
        w.write_7bit_encoded_int(value)
        r = pd.Reader(w.bytes())
        assert r.read_7bit_encoded_int() == value
        assert r.eof()


def test_write_string_round_trips_through_reader_read_string():
    for s in ("", "a", "hello world", "Extron.Configuration.Drivers.DriverFileAsset",
              "unicode: éè中文"):
        w = nw.Writer()
        w.write_string(s)
        r = pd.Reader(w.bytes())
        assert r.read_string() == s


# --------------------------------------------------------------------------
# The core deliverable: byte-identical round trip, all 4 samples.
# --------------------------------------------------------------------------
def _round_trip(path):
    data = pd.load_bytes(path)
    parser, trace = nw.parse_and_trace(data)
    out = nw.write_trace(trace)
    return data, out, parser


def test_roundtrip_byte_identical_samsung():
    _require_samples()
    data, out, _ = _round_trip(SAMSUNG)
    assert out == data, "first divergence at %r" % (_first_diff(data, out),)


def test_roundtrip_byte_identical_dsc_12g_hd():
    _require_samples()
    data, out, _ = _round_trip(DSC)
    assert out == data, "first divergence at %r" % (_first_diff(data, out),)


def test_roundtrip_byte_identical_dtp3_cp_42():
    _require_samples()
    data, out, _ = _round_trip(DTP3)
    assert out == data, "first divergence at %r" % (_first_diff(data, out),)


def test_roundtrip_byte_identical_automate_vx():
    _require_samples()
    data, out, _ = _round_trip(AUTOMATE_VX)
    assert out == data, "first divergence at %r" % (_first_diff(data, out),)


def _first_diff(a, b):
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return ("offset", i, "len_a", len(a), "len_b", len(b))
    if len(a) != len(b):
        return ("length mismatch only", "len_a", len(a), "len_b", len(b))
    return None


def test_roundtrip_works_through_the_original_gzip_pkp_too():
    # load_bytes() strips gzip; confirm the .pkp files really are gzip
    # members (not already-raw), so the round trip is exercised on the
    # actual shipped artifact, not just a pre-unwrapped .raw fixture.
    _require_samples()
    with open(DSC, "rb") as f:
        raw = f.read()
    assert raw[:2] == b"\x1f\x8b"
    decompressed = gzip.decompress(raw)
    parser, trace = nw.parse_and_trace(decompressed)
    out = nw.write_trace(trace)
    assert out == decompressed


# --------------------------------------------------------------------------
# The structural claim behind the whole design (see nrbf_write.py module
# docstring): the stream is NOT one deeply-nested recursive tree; the vast
# majority of objects are separate, sibling records reached via repeated
# passes of parse()'s OUTER loop, which is exactly why a naive
# "reconstruct-a-DFS-order-from-the-JSON-graph" writer would not be able to
# reproduce the real interleaving and a full trace was necessary instead.
# --------------------------------------------------------------------------
def test_stream_is_not_simple_dfs_dsc_12g_hd():
    _require_samples()
    data = pd.load_bytes(DSC)
    parser = pd.PkpParser(data)
    parser.parse()
    # ClassWithId is only ever reached as a record dispatched from
    # parse()'s outer while loop or from a nested member/array-item read;
    # _count() only increments on the outer loop. Thousands of hits here
    # means thousands of outer-loop passes, i.e. a mostly-flat stream, not
    # a single recursively-unwound tree from one root record.
    assert parser.record_type_counts.get("ClassWithId", 0) > 4000
    assert len(parser.objects) > 8000


# --------------------------------------------------------------------------
# Fidelity gap this experiment exists to demonstrate: pkp_dump's own public
# JSON ("objects" table) throws away exactly the two things a writer needs
# (per-member wire width/BinaryType, and untyped-vs-typed class shape) -
# this is *why* nrbf_write.py works from a parse trace instead.
# --------------------------------------------------------------------------
def test_plain_pkp_dump_json_does_not_carry_member_wire_types():
    _require_samples()
    data = pd.load_bytes(DSC)
    parser = pd.PkpParser(data)
    parser.parse()
    root = parser.objects[parser.root_id]
    assert root["members"], "expected the root object to have members"
    for k in ("member_types", "binary_type", "_pt"):
        assert k not in root, "pkp_dump's emitted dict unexpectedly carries %r" % (k,)


def test_plain_pkp_dump_json_conflates_typed_and_untyped_class_records():
    # Both RT_ClassWithMembersAndTypes and RT_ClassWithMembers collapse to
    # the same "$type": "ClassWithMembersAndTypes" string in pkp_dump's
    # output (see pkp_dump.py _class_instance_dict) - real bug class for
    # any writer that trusts the JSON dict alone instead of ClassInfo.
    _require_samples()
    data = pd.load_bytes(DSC)
    parser = pd.PkpParser(data)
    parser.parse()
    guid_objs = [v for v in parser.objects.values()
                 if isinstance(v, dict) and v.get("class") == "System.Guid"]
    assert guid_objs, "expected at least one System.Guid instance in this sample"
    # System.Guid is written via the untyped SystemClassWithMembers shape
    # (see pkp_dump.py KNOWN_UNTYPED_CLASS_FIELDS comment, confirmed at
    # DSC_12G-HD.raw offset 0xa1b) yet still reports $type
    # "SystemClassWithMembersAndTypes" - the two wire shapes are
    # indistinguishable from the JSON alone.
    assert guid_objs[0]["$type"] == "SystemClassWithMembersAndTypes"


# --------------------------------------------------------------------------
# Mutation test: change one string value, re-serialize, re-parse with the
# UNMODIFIED tools/pkp_dump.py (not our tracing subclass) and confirm the
# mutation stuck and the rest of the graph is untouched.
# --------------------------------------------------------------------------
def test_mutation_changes_only_the_targeted_string():
    _require_samples()
    data = pd.load_bytes(DSC)

    # Baseline: confirm the target ahead of time so the assertion below is
    # meaningful (object 29 is a RevisionHistoryAsset; its _author member
    # points to a uniquely-valued BinaryObjectString "username", object id
    # 37 - not shared with any other string in the file).
    baseline = pd.PkpParser(data)
    baseline.parse()
    assert baseline.objects[37] == "username"
    assert baseline.objects[29]["members"]["_author"] == {"$ref": 37}
    assert [oid for oid, v in baseline.objects.items() if v == "username"] == [37]

    parser, trace = nw.parse_and_trace(data)
    nw.mutate_string_by_object_id(trace, 37, "nrbf-writeback-mutation-test")
    mutated_bytes = nw.write_trace(trace)

    assert mutated_bytes != data

    reparsed = pd.PkpParser(mutated_bytes)
    reparsed.parse()

    # The mutation landed exactly where intended.
    assert reparsed.objects[37] == "nrbf-writeback-mutation-test"
    assert reparsed.objects[29]["members"]["_author"] == {"$ref": 37}

    # Everything else in the graph is untouched: same object count, same
    # per-class instance counts, same record-type counts, and the sibling
    # revision's author (a different string, object id 44) is unaffected.
    assert len(reparsed.objects) == len(baseline.objects)
    assert reparsed.record_type_counts == baseline.record_type_counts
    assert reparsed.objects[30]["members"]["_author"] == {"$ref": 44}
    assert reparsed.objects[44] == "billywong"

    def class_counts(objs):
        counts = {}
        for v in objs.values():
            if isinstance(v, dict) and "class" in v:
                counts[v["class"]] = counts.get(v["class"], 0) + 1
        return counts

    assert class_counts(reparsed.objects) == class_counts(baseline.objects)


def test_mutation_rejects_unknown_object_id():
    _require_samples()
    data = pd.load_bytes(DSC)
    _, trace = nw.parse_and_trace(data)
    try:
        nw.mutate_string_by_object_id(trace, -999999, "x")
        assert False, "expected TraceError for a non-existent object id"
    except nw.TraceError:
        pass


# --------------------------------------------------------------------------
# Scope boundary: write_primitive_value refuses to guess at the one
# genuinely untested/lossy shape (Primitive-typed String) rather than
# emitting silently-wrong bytes.
# --------------------------------------------------------------------------
def test_writer_refuses_to_guess_primitive_string_shape():
    w = nw.Writer()
    try:
        nw.write_primitive_value(w, pd.PT_String, "whatever")
        assert False, "expected TraceError for PT_String as a raw Primitive value"
    except nw.TraceError:
        pass


def test_writer_refuses_unknown_primitive_type():
    w = nw.Writer()
    try:
        nw.write_primitive_value(w, 255, 0)
        assert False, "expected TraceError for an unhandled primitive type code"
    except nw.TraceError:
        pass


if __name__ == "__main__":
    tests = [(name, fn) for name, fn in sorted(globals().items())
             if name.startswith("test_") and callable(fn)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print("PASS", name)
        except AssertionError as e:
            failed += 1
            print("FAIL", name, "-", e)
        except Exception as e:
            failed += 1
            print("ERROR", name, "-", repr(e))
    print("%d/%d passed" % (len(tests) - failed, len(tests)))
    sys.exit(1 if failed else 0)
