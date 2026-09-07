#!/usr/bin/env python3
"""
nrbf_write.py - Q1a (nrbf-writeback experiment): can we WRITE a .NET
BinaryFormatter (NRBF) stream, not just read one?

Approach
--------
tools/pkp_dump.py's public JSON output ("objects" table) is, by design,
LOSSY for reserialization purposes: two facts the wire format needs are
thrown away on the way to JSON:

  1. Per-member wire width/type (e.g. Int16 vs Int32 vs UInt32, or whether a
     class was declared via the untyped ClassWithMembers/SystemClassWithMembers
     shape vs the typed ClassWithMembersAndTypes/SystemClassWithMembersAndTypes
     shape). This lives only in pkp_dump's transient `ClassInfo` objects, never
     reaching the emitted dict (see pkp_dump._class_instance_dict, which emits
     only {$type, class, members, library, metadata_ref} - no per-member
     BinaryType info at all).
  2. Stream *order*/interleaving. NRBF is not a naive single recursive-descent
     serialization of the object graph: measured directly on the samples
     (see test_nrbf_write.py:test_stream_is_not_simple_dfs), the .NET writer
     defines the vast majority of objects as flat, single-level records
     reached through repeated iterations of the OUTER read loop (e.g. DSC
     12G-HD has 4279 ClassWithId instances counted by pkp_dump's own top-level
     `_count()`, which only fires once per outer-loop iteration - i.e. that
     many outer-loop passes, not one deeply nested tree). Which member
     positions get a fresh inline body vs. defer to a later top-level slot is
     a decision made by .NET's ObjectWriter that pkp_dump's graph output does
     not record at all.

So instead of reconstructing the record layout FROM the (lossy) JSON graph,
this module builds a byte-exact, order-preserving TRACE by subclassing
pkp_dump.PkpParser and hooking its two record-dispatch chokepoints
(`_read_object_record`, which every record - top-level or nested - passes
through, and `_read_primitive_value`, which every raw/unwrapped primitive
read passes through). Each hook appends a small event describing exactly
what was read, in exactly the position it was read, using a stack of
"current child list" scopes so a parent's event always precedes its
children's events - with NO list.insert() (which would be O(n) per call
and O(n^2) overall on files with tens of thousands of objects).

NrbfWriter then replays that trace, event by event, writing bytes with the
literal inverse of every pkp_dump Reader operation used to decode it. For an
UNMUTATED trace, replaying reproduces the original bytes ONLY IF pkp_dump's
own primitive codecs are canonical (7-bit length ints minimal-width, IEEE754
passthrough, etc) - which is what the round-trip test in
test_nrbf_write.py actually measures, byte-for-byte, rather than assuming.

For MUTATION: because NRBF has no absolute-offset pointers anywhere (every
cross-reference is a logical object id, not a byte offset), changing one
string's *value* only changes that string's own encoded length-prefix +
UTF-8 payload; everything else in the file is serial and shifts along
without needing any fix-up. `mutate_string_by_object_id` exploits exactly
this property.

Scope/boundary (read before assuming more than this proves):
  - This proves the WIRE FORMAT is writable from a full parse trace built by
    this library, faithfully enough to reproduce four real, complex Extron
    packages byte-for-byte (or to name precisely where it fails to).
  - It does NOT prove Global Configurator will *accept* a package assembled
    from scratch (no existing trace to start from) - that would additionally
    require knowing which fields GC actually validates/requires at load time,
    and there is no GC install available here to test against. Nothing here
    exercises that.
"""
import io
import os
import sys
import struct
import gzip

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import pkp_dump as pd  # noqa: E402


# --------------------------------------------------------------------------
# Reverse lookups from pkp_dump's name tables back to wire codes. pkp_dump
# resolves BAT_*/BT_*/PT_* integer codes to human-readable strings for JSON;
# we need to go the other way for the handful of places we read pkp_dump's
# resolved-value dicts (BinaryArray, ArraySinglePrimitive, MemberPrimitiveTyped)
# instead of talking to ClassInfo directly.
# --------------------------------------------------------------------------
PT_BY_NAME = {v: k for k, v in pd.PRIMITIVE_NAMES.items()}
BT_BY_NAME = {v: k for k, v in pd.BINTYPE_NAMES.items()}
BAT_BY_NAME = {v: k for k, v in pd.BINARY_ARRAY_TYPE_NAMES.items()}


class TraceError(Exception):
    pass


# --------------------------------------------------------------------------
# Writer: the literal mirror of pkp_dump.Reader.
# --------------------------------------------------------------------------
class Writer:
    def __init__(self):
        self.buf = bytearray()

    def bytes(self):
        return bytes(self.buf)

    def write(self, b):
        self.buf.extend(b)

    def write_byte(self, v):
        self.buf.append(v & 0xFF)

    def write_int16(self, v):
        self.buf.extend(struct.pack("<h", v))

    def write_uint16(self, v):
        self.buf.extend(struct.pack("<H", v))

    def write_int32(self, v):
        self.buf.extend(struct.pack("<i", v))

    def write_uint32(self, v):
        self.buf.extend(struct.pack("<I", v))

    def write_int64(self, v):
        self.buf.extend(struct.pack("<q", v))

    def write_uint64(self, v):
        self.buf.extend(struct.pack("<Q", v))

    def write_single(self, v):
        self.buf.extend(struct.pack("<f", v))

    def write_double(self, v):
        self.buf.extend(struct.pack("<d", v))

    def write_7bit_encoded_int(self, value):
        # Mirror of System.IO.BinaryWriter.Write7BitEncodedInt: canonical
        # (minimal-byte) little-endian base-128 encoding. Treat as unsigned
        # 32-bit per [MS-NRBF] 2.1.1.5 (lengths/ids used here are never
        # negative).
        v = value & 0xFFFFFFFF
        while True:
            b = v & 0x7F
            v >>= 7
            if v:
                self.write_byte(b | 0x80)
            else:
                self.write_byte(b)
                break

    def write_string(self, s):
        raw = s.encode("utf-8")
        self.write_7bit_encoded_int(len(raw))
        self.write(raw)


def write_primitive_value(w: Writer, pt, value):
    """Inverse of pkp_dump.PkpParser._read_primitive_value, for every pt this
    project's samples exercise. Raises TraceError (not a silent guess) for
    pt values none of the four samples exercise, since we have no observed
    byte layout to validate against (see test_nrbf_write.py coverage notes)."""
    if pt == pd.PT_Boolean:
        w.write_byte(1 if value else 0)
    elif pt == pd.PT_Byte:
        w.write_byte(value)
    elif pt == pd.PT_SByte:
        w.write_byte(value & 0xFF)
    elif pt == pd.PT_Char:
        w.write(value.encode("utf-8"))
    elif pt == pd.PT_Int16:
        w.write_int16(value)
    elif pt == pd.PT_UInt16:
        w.write_uint16(value)
    elif pt == pd.PT_Int32:
        w.write_int32(value)
    elif pt == pd.PT_UInt32:
        w.write_uint32(value)
    elif pt == pd.PT_Int64:
        w.write_int64(value)
    elif pt == pd.PT_UInt64:
        w.write_uint64(value)
    elif pt == pd.PT_Single:
        w.write_single(value)
    elif pt == pd.PT_Double:
        w.write_double(value)
    elif pt == pd.PT_Decimal:
        w.write_string(value)
    elif pt == pd.PT_DateTime:
        raw = (value["kind"] << 62) | value["ticks"]
        w.write_uint64(raw)
    elif pt == pd.PT_TimeSpan:
        w.write_int64(value)
    elif pt == pd.PT_Null:
        pass  # PT_Null members carry no bytes on the wire at all.
    elif pt == pd.PT_String:
        # UNTESTED PATH: none of the 4 samples ever declare a member as
        # BinaryType=Primitive with PrimitiveType=String (verified by
        # inspecting every ClassInfo.member_types across all 4 files -
        # zero hits). pkp_dump itself reads this shape by recursing into
        # _read_object_record and then *discarding* whether that nested
        # record was a fresh BinaryObjectString or a MemberReference
        # (pkp_dump.py:630-634) - so pkp_dump's own parse of this shape is
        # already lossy and this writer cannot round-trip it either. We
        # raise rather than guess.
        raise TraceError(
            "PT_String as a raw Primitive-typed value has no observed byte "
            "layout in any of the 4 samples, and pkp_dump's own reader "
            "discards the info (fresh-string-vs-reference) needed to write "
            "it back; refusing to guess")
    else:
        raise TraceError("unhandled primitive type %r in writer" % (pt,))


# --------------------------------------------------------------------------
# TracingPkpParser: subclasses the real parser purely to observe it. It
# changes no parsing decision pkp_dump.PkpParser makes; it only appends a
# trace event each time a record or primitive is decoded, in exactly the
# nesting position it was decoded (parent events precede child events),
# using an explicit list-of-scopes stack instead of list.insert() so the
# whole trace is built in O(n) rather than O(n^2).
# --------------------------------------------------------------------------
class TracingPkpParser(pd.PkpParser):
    def __init__(self, data):
        super().__init__(data)
        self.trace = []            # top-level scope (flat, ordered)
        self._scopes = [self.trace]

    def _push_scope(self):
        scope = []
        self._scopes.append(scope)
        return scope

    def _pop_scope(self):
        return self._scopes.pop()

    def _emit(self, event):
        """Append a leaf event (no children of its own) to the innermost
        currently-open scope."""
        self._scopes[-1].append(event)

    # -- header -----------------------------------------------------------
    def _read_header(self):
        super()._read_header()
        self._emit({
            "kind": "Header",
            "root_id": self.header["RootId"],
            "header_id": self.header["HeaderId"],
            "major": self.header["MajorVersion"],
            "minor": self.header["MinorVersion"],
        })

    # -- library ------------------------------------------------------------
    def _read_binary_library(self):
        obj_id, value = super()._read_binary_library()
        # lib_id/name were just added to self.libraries; find them without
        # re-deriving (grab the last inserted key, which for a plain read
        # pass is exactly the one just parsed - Python dicts preserve
        # insertion order).
        lib_id = next(reversed(self.libraries))
        self._emit({"kind": "BinaryLibrary", "lib_id": lib_id, "name": self.libraries[lib_id]})
        return obj_id, value

    # -- the one true chokepoint: every record, top-level or nested,
    #    passes through here. --------------------------------------------
    def _read_object_record(self, rt, off):
        if rt == pd.RT_BinaryLibrary:
            # No children of its own; _read_binary_library (above) already
            # emitted the event directly into the current scope.
            return super()._read_object_record(rt, off)

        scope = self._push_scope()
        try:
            obj_id, value = super()._read_object_record(rt, off)
        finally:
            children = self._pop_scope()
            assert children is scope

        event = self._build_event(rt, obj_id, value)
        if event is None:
            # Shouldn't happen for any rt reaching this branch; fail loudly
            # rather than silently dropping a record.
            raise TraceError("no event built for record_type=%r" % (rt,))
        if (rt == pd.RT_MemberPrimitiveTyped and event["pt"] != pd.PT_String):
            # _read_member_primitive_typed() reads its boxed value via
            # _read_primitive_value(), which (for every pt except PT_String)
            # is ALSO independently traced by our _read_primitive_value
            # override into `children` - a duplicate of the value already
            # embedded in this event's own "value" field (confirmed live:
            # DSC_12G-HD.raw offset ~0x7c9e, a boxed Int32 0 - without this,
            # write-back emitted the Int32 bytes twice). Discard the
            # duplicate. When pt IS PT_String, _read_primitive_value
            # recurses into a *real* nested record (BinaryObjectString/
            # MemberReference/ObjectNull) instead of emitting a bare
            # 'Primitive' leaf, so `children` there holds genuine required
            # data and must NOT be discarded (untested by any of the 4
            # samples either way - see the PT_String note elsewhere).
            children = []
        self._scopes[-1].append((event, children))
        return obj_id, value

    def _build_event(self, rt, obj_id, value):
        if rt in (pd.RT_ClassWithMembersAndTypes, pd.RT_SystemClassWithMembersAndTypes):
            ci = self.classinfo_by_id[obj_id]
            return {
                "kind": "ClassWithMembersAndTypes",
                "system": ci.is_system,
                "object_id": obj_id,
                "name": ci.name,
                "member_names": ci.member_names,
                "member_types": ci.member_types,
                "library_id": ci.library_id,
            }
        if rt in (pd.RT_ClassWithMembers, pd.RT_SystemClassWithMembers):
            ci = self.classinfo_by_id[obj_id]
            return {
                "kind": "ClassWithMembers",
                "system": ci.is_system,
                "object_id": obj_id,
                "name": ci.name,
                "member_names": ci.member_names,
                "library_id": ci.library_id,
            }
        if rt == pd.RT_ClassWithId:
            return {"kind": "ClassWithId", "object_id": obj_id,
                    "metadata_id": value["metadata_ref"]}
        if rt == pd.RT_BinaryObjectString:
            return {"kind": "BinaryObjectString", "object_id": obj_id, "value": value}
        if rt == pd.RT_ArraySingleObject:
            return {"kind": "ArraySingleObject", "object_id": obj_id, "length": value["length"]}
        if rt == pd.RT_ArraySingleString:
            return {"kind": "ArraySingleString", "object_id": obj_id, "length": value["length"]}
        if rt == pd.RT_ArraySinglePrimitive:
            return {"kind": "ArraySinglePrimitive", "object_id": obj_id,
                    "length": value["length"],
                    "pt": PT_BY_NAME[value["primitive_type"]]}
        if rt == pd.RT_BinaryArray:
            bt = BT_BY_NAME[value["element_binary_type"]]
            ev = {
                "kind": "BinaryArray", "object_id": obj_id,
                "bat": BAT_BY_NAME[value["array_type"]],
                "rank": value["rank"], "lengths": value["lengths"],
                "lower_bounds": value["lower_bounds"], "bt": bt,
            }
            if bt in (pd.BT_Primitive, pd.BT_PrimitiveArray):
                ev["pt"] = PT_BY_NAME[value["primitive_type"]]
            elif bt == pd.BT_SystemClass:
                ev["class_name"] = value["class_name"]
            elif bt == pd.BT_Class:
                ev["class_name"] = value["class_name"]
                ev["library_id"] = value["library_id"]
            return ev
        if rt == pd.RT_MemberPrimitiveTyped:
            return {"kind": "MemberPrimitiveTyped",
                    "pt": PT_BY_NAME[value["primitive_type"]],
                    "value": value["value"]}
        if rt == pd.RT_MemberReference:
            return {"kind": "MemberReference", "idref": value["$ref"]}
        if rt == pd.RT_ObjectNull:
            return {"kind": "ObjectNull"}
        if rt == pd.RT_ObjectNullMultiple256:
            return {"kind": "ObjectNullMultiple256", "count": value["$null_run"]}
        if rt == pd.RT_ObjectNullMultiple:
            return {"kind": "ObjectNullMultiple", "count": value["$null_run"]}
        return None

    # -- raw/unwrapped primitive reads (class members in Primitive mode,
    #    and ArraySinglePrimitive/BinaryArray element values) --------------
    def _read_primitive_value(self, pt):
        value = super()._read_primitive_value(pt)
        if pt != pd.PT_String:
            # PT_String delegates to _read_object_record internally (see
            # pkp_dump.py:630-634), which already emitted its own event in
            # the right slot; emitting a second event here would duplicate
            # bytes on write-back. Not exercised by any of the 4 samples
            # (see PT_String note in write_primitive_value above).
            self._emit({"kind": "Primitive", "pt": pt, "value": value})
        return value

    # -- top-level loop: only change from pkp_dump.PkpParser.parse() is
    #    emitting a MessageEnd event; everything else is identical. --------
    def parse(self):
        r = self.r
        while not r.eof():
            self._last_off = r.tell()
            rt = r.read_byte()
            self._count(rt)
            if rt == pd.RT_SerializedStreamHeader:
                self._read_header()
            elif rt == pd.RT_MessageEnd:
                self.message_end_seen = True
                self._emit({"kind": "MessageEnd"})
                break
            else:
                obj_id, value = self._read_object_record(rt, self._last_off)
                if obj_id is not None:
                    self.objects[obj_id] = value
        return self

    def flat_trace(self):
        """Depth-first flatten of the nested (event, children) scope tree
        built during parse() back into one flat, write-ready event list, in
        exactly original byte order."""
        out = []

        def walk(scope):
            for item in scope:
                if isinstance(item, tuple):
                    event, children = item
                    out.append(event)
                    walk(children)
                else:
                    out.append(item)

        walk(self.trace)
        return out


def parse_and_trace(data: bytes):
    """Parse `data` (already-decompressed NRBF bytes) with a TracingPkpParser
    and return (parser, flat_trace_list)."""
    p = TracingPkpParser(data)
    p.parse()
    return p, p.flat_trace()


# --------------------------------------------------------------------------
# NrbfWriter: replays a flat trace (as produced by parse_and_trace) into
# bytes, using the literal inverse of the pkp_dump.Reader operation that
# produced each event.
# --------------------------------------------------------------------------
class NrbfWriter:
    def __init__(self):
        self.w = Writer()

    def write_trace(self, trace):
        for event in trace:
            self._write_event(event)
        return self.w.bytes()

    def _write_event(self, ev):
        kind = ev["kind"]
        w = self.w
        if kind == "Header":
            w.write_byte(pd.RT_SerializedStreamHeader)
            w.write_int32(ev["root_id"])
            w.write_int32(ev["header_id"])
            w.write_int32(ev["major"])
            w.write_int32(ev["minor"])
        elif kind == "BinaryLibrary":
            w.write_byte(pd.RT_BinaryLibrary)
            w.write_int32(ev["lib_id"])
            w.write_string(ev["name"])
        elif kind == "ClassWithMembersAndTypes":
            w.write_byte(pd.RT_SystemClassWithMembersAndTypes if ev["system"]
                         else pd.RT_ClassWithMembersAndTypes)
            w.write_int32(ev["object_id"])
            w.write_string(ev["name"])
            w.write_int32(len(ev["member_names"]))
            for mname in ev["member_names"]:
                w.write_string(mname)
            self._write_member_type_info(ev["member_types"])
            if not ev["system"]:
                w.write_int32(ev["library_id"])
        elif kind == "ClassWithMembers":
            w.write_byte(pd.RT_SystemClassWithMembers if ev["system"]
                         else pd.RT_ClassWithMembers)
            w.write_int32(ev["object_id"])
            w.write_string(ev["name"])
            w.write_int32(len(ev["member_names"]))
            for mname in ev["member_names"]:
                w.write_string(mname)
            if not ev["system"]:
                w.write_int32(ev["library_id"])
        elif kind == "ClassWithId":
            w.write_byte(pd.RT_ClassWithId)
            w.write_int32(ev["object_id"])
            w.write_int32(ev["metadata_id"])
        elif kind == "BinaryObjectString":
            w.write_byte(pd.RT_BinaryObjectString)
            w.write_int32(ev["object_id"])
            w.write_string(ev["value"])
        elif kind == "ArraySingleObject":
            w.write_byte(pd.RT_ArraySingleObject)
            w.write_int32(ev["object_id"])
            w.write_int32(ev["length"])
        elif kind == "ArraySingleString":
            w.write_byte(pd.RT_ArraySingleString)
            w.write_int32(ev["object_id"])
            w.write_int32(ev["length"])
        elif kind == "ArraySinglePrimitive":
            w.write_byte(pd.RT_ArraySinglePrimitive)
            w.write_int32(ev["object_id"])
            w.write_int32(ev["length"])
            w.write_byte(ev["pt"])
        elif kind == "BinaryArray":
            w.write_byte(pd.RT_BinaryArray)
            w.write_int32(ev["object_id"])
            w.write_byte(ev["bat"])
            w.write_int32(ev["rank"])
            for L in ev["lengths"]:
                w.write_int32(L)
            if ev["lower_bounds"] is not None:
                for lb in ev["lower_bounds"]:
                    w.write_int32(lb)
            w.write_byte(ev["bt"])
            if ev["bt"] in (pd.BT_Primitive, pd.BT_PrimitiveArray):
                w.write_byte(ev["pt"])
            elif ev["bt"] == pd.BT_SystemClass:
                w.write_string(ev["class_name"])
            elif ev["bt"] == pd.BT_Class:
                w.write_string(ev["class_name"])
                w.write_int32(ev["library_id"])
        elif kind == "MemberReference":
            w.write_byte(pd.RT_MemberReference)
            w.write_int32(ev["idref"])
        elif kind == "ObjectNull":
            w.write_byte(pd.RT_ObjectNull)
        elif kind == "ObjectNullMultiple256":
            w.write_byte(pd.RT_ObjectNullMultiple256)
            w.write_byte(ev["count"])
        elif kind == "ObjectNullMultiple":
            w.write_byte(pd.RT_ObjectNullMultiple)
            w.write_int32(ev["count"])
        elif kind == "MemberPrimitiveTyped":
            w.write_byte(pd.RT_MemberPrimitiveTyped)
            w.write_byte(ev["pt"])
            write_primitive_value(w, ev["pt"], ev["value"])
        elif kind == "Primitive":
            write_primitive_value(w, ev["pt"], ev["value"])
        elif kind == "MessageEnd":
            w.write_byte(pd.RT_MessageEnd)
        else:
            raise TraceError("unknown trace event kind %r" % (kind,))

    def _write_member_type_info(self, member_types):
        # Mirror of pkp_dump._read_member_type_info: ALL N binary_type bytes
        # form one contiguous block first, and only after that block do the
        # per-member "extra" payloads (primitive code / class name / library
        # id) follow, in the same member order. Confirmed against the actual
        # bytes (DSC_12G-HD.raw offset 0x39e/926: the DriverFileAsset class,
        # 20 members, emits 20 raw BT bytes "04 04 03 04 03 03 03 01 01 01
        # 01 00 04 04 01 01 03 03 00 04" as one run, THEN member 0's Class
        # extra info ("c0 01" length-prefixed "Extron...IAsset`1[[...]]"
        # string + library_id) - NOT interleaved bt0,extra0,bt1,extra1,...
        w = self.w
        bts = [BT_BY_NAME[info["binary_type"]] for info in member_types]
        for bt in bts:
            w.write_byte(bt)
        for bt, info in zip(bts, member_types):
            if bt in (pd.BT_Primitive, pd.BT_PrimitiveArray):
                w.write_byte(info["_pt"])
            elif bt == pd.BT_SystemClass:
                w.write_string(info["class_name"])
            elif bt == pd.BT_Class:
                w.write_string(info["class_name"])
                w.write_int32(info["library_id"])
            # String / Object / ObjectArray / StringArray: nothing extra.


def write_trace(trace) -> bytes:
    return NrbfWriter().write_trace(trace)


# --------------------------------------------------------------------------
# Mutation helper: change one BinaryObjectString's value in-place in a flat
# trace. Safe because NRBF has no absolute-offset pointers - every other
# byte in the file is either unrelated or simply follows serially, so
# changing the length + payload of exactly one string leaves the rest of
# the graph structurally untouched (ids, refs, counts are all unaffected).
# --------------------------------------------------------------------------
def mutate_string_by_object_id(trace, object_id, new_value):
    hits = 0
    for ev in trace:
        if ev.get("kind") == "BinaryObjectString" and ev.get("object_id") == object_id:
            ev["value"] = new_value
            hits += 1
    if hits == 0:
        raise TraceError("no BinaryObjectString event with object_id=%r" % (object_id,))
    if hits > 1:
        raise TraceError("multiple BinaryObjectString events with object_id=%r (unexpected: "
                          "ids should be unique)" % (object_id,))
    return hits


def gunzip_if_needed(data: bytes) -> bytes:
    return gzip.decompress(data) if data[:2] == b"\x1f\x8b" else data


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", help=".pkp or .raw file")
    ap.add_argument("-o", "--output", help="path to write re-serialized raw NRBF bytes")
    args = ap.parse_args()
    data = pd.load_bytes(args.input)
    parser, trace = parse_and_trace(data)
    out = write_trace(trace)
    identical = out == data
    print("input bytes:      %d" % len(data))
    print("output bytes:     %d" % len(out))
    print("byte-identical:   %s" % identical)
    if not identical:
        n = min(len(data), len(out))
        first_diff = next((i for i in range(n) if data[i] != out[i]), n)
        print("first divergence at byte offset 0x%x (%d)" % (first_diff, first_diff))
    if args.output:
        with open(args.output, "wb") as f:
            f.write(out)
        print("wrote %s" % args.output)
