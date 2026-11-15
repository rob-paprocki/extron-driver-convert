#!/usr/bin/env python3
"""
pkp_dump.py - A from-scratch [MS-NRBF] (.NET BinaryFormatter) stream parser,
purpose-built for Extron .pkp driver-package files.

An Extron .pkp file is a gzip member wrapping a raw NRBF serialization
stream. This tool:
  1. Detects & strips gzip (magic 1f 8b) if present; otherwise treats the
     input as an already-decompressed NRBF byte stream (e.g. a .raw file).
  2. Walks the NRBF record stream per [MS-NRBF] sections 2.1-2.7.
  3. Resolves MemberReference / ClassWithId back-references into a graph.
  4. Emits the whole thing as JSON: an "objects" table keyed by NRBF object
     id, plus "root_id" / "header" pointing into it.

Usage:
    python3 pkp_dump.py <input.pkp|input.raw> -o <output.json>

If the parser hits a record shape it cannot handle, it raises NrbfParseError
naming the offending record-type byte and the absolute byte offset in the
(decompressed) stream, rather than guessing.
"""
import sys
import gzip
import json
import struct
import argparse
import io


# --------------------------------------------------------------------------
# [MS-NRBF] 2.1.2.1 RecordTypeEnumeration
# --------------------------------------------------------------------------
RT_SerializedStreamHeader = 0
RT_ClassWithId = 1
RT_SystemClassWithMembers = 2
RT_ClassWithMembers = 3
RT_SystemClassWithMembersAndTypes = 4
RT_ClassWithMembersAndTypes = 5
RT_BinaryObjectString = 6
RT_BinaryArray = 7
RT_MemberPrimitiveTyped = 8
RT_MemberReference = 9
RT_ObjectNull = 10
RT_MessageEnd = 11
RT_BinaryLibrary = 12
RT_ObjectNullMultiple256 = 13
RT_ObjectNullMultiple = 14
RT_ArraySinglePrimitive = 15
RT_ArraySingleObject = 16
RT_ArraySingleString = 17
RT_MethodCall = 18
RT_MethodReturn = 19

RECORD_NAMES = {
    RT_SerializedStreamHeader: "SerializedStreamHeader",
    RT_ClassWithId: "ClassWithId",
    RT_SystemClassWithMembers: "SystemClassWithMembers",
    RT_ClassWithMembers: "ClassWithMembers",
    RT_SystemClassWithMembersAndTypes: "SystemClassWithMembersAndTypes",
    RT_ClassWithMembersAndTypes: "ClassWithMembersAndTypes",
    RT_BinaryObjectString: "BinaryObjectString",
    RT_BinaryArray: "BinaryArray",
    RT_MemberPrimitiveTyped: "MemberPrimitiveTyped",
    RT_MemberReference: "MemberReference",
    RT_ObjectNull: "ObjectNull",
    RT_MessageEnd: "MessageEnd",
    RT_BinaryLibrary: "BinaryLibrary",
    RT_ObjectNullMultiple256: "ObjectNullMultiple256",
    RT_ObjectNullMultiple: "ObjectNullMultiple",
    RT_ArraySinglePrimitive: "ArraySinglePrimitive",
    RT_ArraySingleObject: "ArraySingleObject",
    RT_ArraySingleString: "ArraySingleString",
    RT_MethodCall: "MethodCall",
    RT_MethodReturn: "MethodReturn",
}

# [MS-NRBF] 2.1.2.2 BinaryTypeEnumeration
BT_Primitive = 0
BT_String = 1
BT_Object = 2
BT_SystemClass = 3
BT_Class = 4
BT_ObjectArray = 5
BT_StringArray = 6
BT_PrimitiveArray = 7

BINTYPE_NAMES = {
    BT_Primitive: "Primitive", BT_String: "String", BT_Object: "Object",
    BT_SystemClass: "SystemClass", BT_Class: "Class",
    BT_ObjectArray: "ObjectArray", BT_StringArray: "StringArray",
    BT_PrimitiveArray: "PrimitiveArray",
}

# [MS-NRBF] 2.1.2.3 PrimitiveTypeEnumeration
PT_Boolean = 1
PT_Byte = 2
PT_Char = 3
PT_Decimal = 5
PT_Double = 6
PT_Int16 = 7
PT_Int32 = 8
PT_Int64 = 9
PT_SByte = 10
PT_Single = 11
PT_TimeSpan = 12
PT_DateTime = 13
PT_UInt16 = 14
PT_UInt32 = 15
PT_UInt64 = 16
PT_Null = 17
PT_String = 18

PRIMITIVE_NAMES = {
    PT_Boolean: "Boolean", PT_Byte: "Byte", PT_Char: "Char",
    PT_Decimal: "Decimal", PT_Double: "Double", PT_Int16: "Int16",
    PT_Int32: "Int32", PT_Int64: "Int64", PT_SByte: "SByte",
    PT_Single: "Single", PT_TimeSpan: "TimeSpan", PT_DateTime: "DateTime",
    PT_UInt16: "UInt16", PT_UInt32: "UInt32", PT_UInt64: "UInt64",
    PT_Null: "Null", PT_String: "String",
}

# [MS-NRBF] 2.4.3.1 BinaryArrayTypeEnumeration
BAT_Single = 0
BAT_Jagged = 1
BAT_Rectangular = 2
BAT_SingleOffset = 3
BAT_JaggedOffset = 4
BAT_RectangularOffset = 5

BINARY_ARRAY_TYPE_NAMES = {
    BAT_Single: "Single", BAT_Jagged: "Jagged", BAT_Rectangular: "Rectangular",
    BAT_SingleOffset: "SingleOffset", BAT_JaggedOffset: "JaggedOffset",
    BAT_RectangularOffset: "RectangularOffset",
}


class NrbfParseError(Exception):
    def __init__(self, message, offset=None, record_type=None):
        self.offset = offset
        self.record_type = record_type
        parts = [message]
        if record_type is not None:
            name = RECORD_NAMES.get(record_type, "0x%02x" % record_type)
            parts.append("record_type=%s(%r)" % (name, record_type))
        if offset is not None:
            parts.append("offset=0x%x (%d)" % (offset, offset))
        super().__init__(" | ".join(parts))


class Reader:
    """Little-endian binary cursor over the decompressed NRBF stream, with
    offset tracking so parse failures can be reported precisely."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0
        self.n = len(data)

    def tell(self):
        return self.pos

    def eof(self):
        return self.pos >= self.n

    def read(self, size):
        if self.pos + size > self.n:
            raise NrbfParseError(
                "unexpected end of stream: wanted %d bytes, have %d" %
                (size, self.n - self.pos), offset=self.pos)
        b = self.data[self.pos:self.pos + size]
        self.pos += size
        return b

    def read_byte(self):
        return self.read(1)[0]

    def read_int16(self):
        return struct.unpack("<h", self.read(2))[0]

    def read_uint16(self):
        return struct.unpack("<H", self.read(2))[0]

    def read_int32(self):
        return struct.unpack("<i", self.read(4))[0]

    def read_uint32(self):
        return struct.unpack("<I", self.read(4))[0]

    def read_int64(self):
        return struct.unpack("<q", self.read(8))[0]

    def read_uint64(self):
        return struct.unpack("<Q", self.read(8))[0]

    def read_single(self):
        return struct.unpack("<f", self.read(4))[0]

    def read_double(self):
        return struct.unpack("<d", self.read(8))[0]

    def read_7bit_encoded_int(self):
        # Same algorithm as System.IO.BinaryReader.Read7BitEncodedInt:
        # little-endian base-128, 7 bits of value per byte, high bit = "more".
        result = 0
        shift = 0
        for _ in range(5):
            b = self.read_byte()
            result |= (b & 0x7F) << shift
            if not (b & 0x80):
                return result
            shift += 7
        raise NrbfParseError("7-bit encoded int too long", offset=self.pos)

    def read_string(self):
        # [MS-NRBF] 2.1.1.6 LengthPrefixedString: 7-bit length, then that many
        # UTF-8 *bytes* (not characters).
        length = self.read_7bit_encoded_int()
        raw = self.read(length)
        return raw.decode("utf-8")


class ClassInfo:
    """Metadata captured from a class-defining record (ClassWithMembers[AndTypes],
    SystemClassWithMembers[AndTypes]), keyed by the object id it was declared
    with. ClassWithId records reuse this via their MetadataId back-reference."""

    __slots__ = ("object_id", "name", "member_names", "member_types",
                 "library_id", "is_system")

    def __init__(self, object_id, name, member_names, member_types,
                 library_id, is_system):
        self.object_id = object_id
        self.name = name
        self.member_names = member_names
        self.member_types = member_types  # list of dict describing each member's BinaryType
        self.library_id = library_id
        self.is_system = is_system


# [MS-NRBF] leaves ClassWithMembers / SystemClassWithMembers member typing to
# reflection on the already-loaded CLR type at read time, since no
# MemberTypeInfo is written on the wire. We have no CLR, so the only shapes
# we can support are ones confirmed by inspecting the actual bytes of the two
# sample .pkp files (see comments at each call site below).
#
# Each field entry is (member_name, mode), where mode is either a PT_*
# constant (the field is a bare, unwrapped primitive value with no
# record-type byte) or the sentinel string "record" (the field IS a normal
# self-describing record -- MemberReference / BinaryObjectString /
# ArraySingleObject / ObjectNull / etc, exactly like the generic fallback
# path). Real .NET types can (and do) mix both within one instance, e.g.
# List`1 below.
FIELD_RECORD = "record"

KNOWN_UNTYPED_CLASS_FIELDS = {
    "System.Guid": [
        ("_a", PT_Int32), ("_b", PT_Int16), ("_c", PT_Int16),
        ("_d", PT_Byte), ("_e", PT_Byte), ("_f", PT_Byte), ("_g", PT_Byte),
        ("_h", PT_Byte), ("_i", PT_Byte), ("_j", PT_Byte), ("_k", PT_Byte),
    ],
    # Confirmed at DSC_12G-HD.raw offset 0xdcb, SystemClassWithMembers,
    # class "System.Version": four raw Int32 fields, no record wrapper
    # (_Major=1, _Minor=0, _Build=0, _Revision=-1 i.e. 0xffffffff).
    "System.Version": [
        ("_Major", PT_Int32), ("_Minor", PT_Int32),
        ("_Build", PT_Int32), ("_Revision", PT_Int32),
    ],
}

# Keyed by the generic type's name with its "[[...]]" type-argument text
# stripped off (exact match on the non-generic prefix). Confirmed at
# DSC_12G-HD.raw offset 0x1201, SystemClassWithMembers, class
# "System.Collections.Generic.List`1[[Extron...IAsset, ...]]": member_names
# = [_items, _size, _version]; _items is a MemberReference (id 28, to an
# ArraySingleObject) -- i.e. a normal record -- while _size/_version are
# raw Int32s with no record-type byte (bytes "09 1c000000" then two bare
# Int32s follow the array reference in the driver payload).
KNOWN_UNTYPED_CLASS_FIELDS_BY_BASENAME = {
    "System.Collections.Generic.List`1": [
        ("_items", FIELD_RECORD), ("_size", PT_Int32), ("_version", PT_Int32),
    ],
}

# Nested compiler/BCL helper types whose full name carries generic-argument
# text that varies by driver (e.g. the IAsset type argument), so they're
# matched by a suffix on the name with generics stripped, rather than an
# exact string. Confirmed at DSC_12G-HD.raw offset 0x1116, ClassWithMembers,
# class "System.Collections.ObjectModel.ObservableCollection`1+SimpleMonitor
# [[Extron...IAsset, ...]]": one raw Int32 field "_busyCount", no record
# wrapper (member_count=1, name len=205 incl. generic args, then LibraryId=4,
# then raw bytes "00 00 00 00").
KNOWN_UNTYPED_CLASS_FIELDS_BY_SUFFIX = [
    ("+SimpleMonitor", [("_busyCount", PT_Int32)]),
]


class PkpParser:
    def __init__(self, data: bytes):
        self.r = Reader(data)
        self.objects = {}          # object_id -> resolved python/dict value
        self.classinfo_by_id = {}  # object_id (of the defining record) -> ClassInfo
        self.libraries = {}        # library_id -> library name string
        self.record_type_counts = {}
        self.header = None
        self.root_id = None
        self.message_end_seen = False
        self.record_log = []       # ordered list of (offset, record_type_name) for top-level records

    # -- bookkeeping -------------------------------------------------
    def _count(self, rt):
        self.record_log.append((self._last_off, RECORD_NAMES.get(rt, rt)))
        self.record_type_counts[RECORD_NAMES.get(rt, "0x%02x" % rt)] = \
            self.record_type_counts.get(RECORD_NAMES.get(rt, "0x%02x" % rt), 0) + 1

    # -- top-level driver ---------------------------------------------
    def parse(self):
        r = self.r
        while not r.eof():
            self._last_off = r.tell()
            rt = r.read_byte()
            self._count(rt)
            if rt == RT_SerializedStreamHeader:
                self._read_header()
            elif rt == RT_MessageEnd:
                self.message_end_seen = True
                break
            else:
                obj_id, value = self._read_object_record(rt, self._last_off)
                if obj_id is not None:
                    self.objects[obj_id] = value
        return self

    def _read_header(self):
        r = self.r
        root_id = r.read_int32()
        header_id = r.read_int32()
        major = r.read_int32()
        minor = r.read_int32()
        self.header = {
            "RootId": root_id, "HeaderId": header_id,
            "MajorVersion": major, "MinorVersion": minor,
        }
        self.root_id = root_id

    # -- dispatch for anything that can appear as a standalone record
    #    or as a member value -----------------------------------------
    def _read_object_record(self, rt, off):
        """Reads one record whose type byte `rt` has already been consumed.
        Returns (object_id_or_None, value)."""
        if rt == RT_BinaryLibrary:
            return self._read_binary_library()
        elif rt == RT_ClassWithMembersAndTypes:
            return self._read_class_with_members_and_types(system=False)
        elif rt == RT_SystemClassWithMembersAndTypes:
            return self._read_class_with_members_and_types(system=True)
        elif rt == RT_ClassWithMembers:
            return self._read_class_with_members(system=False)
        elif rt == RT_SystemClassWithMembers:
            return self._read_class_with_members(system=True)
        elif rt == RT_ClassWithId:
            return self._read_class_with_id()
        elif rt == RT_BinaryObjectString:
            return self._read_binary_object_string()
        elif rt == RT_BinaryArray:
            return self._read_binary_array()
        elif rt == RT_ArraySingleObject:
            return self._read_array_single_object()
        elif rt == RT_ArraySingleString:
            return self._read_array_single_string()
        elif rt == RT_ArraySinglePrimitive:
            return self._read_array_single_primitive()
        elif rt == RT_MemberPrimitiveTyped:
            return None, self._read_member_primitive_typed()
        elif rt == RT_MemberReference:
            idref = self.r.read_int32()
            return None, {"$ref": idref}
        elif rt == RT_ObjectNull:
            return None, None
        elif rt == RT_ObjectNullMultiple256:
            count = self.r.read_byte()
            return None, {"$null_run": count}
        elif rt == RT_ObjectNullMultiple:
            count = self.r.read_int32()
            return None, {"$null_run": count}
        else:
            raise NrbfParseError(
                "unhandled/unknown record type while parsing",
                offset=off, record_type=rt)

    # -- BinaryLibrary --------------------------------------------------
    def _read_binary_library(self):
        r = self.r
        lib_id = r.read_int32()
        name = r.read_string()
        self.libraries[lib_id] = name
        return None, None  # not an "object" in the graph sense

    # -- BinaryObjectString ----------------------------------------------
    def _read_binary_object_string(self):
        r = self.r
        obj_id = r.read_int32()
        value = r.read_string()
        return obj_id, value

    # -- member type info parsing (shared by ClassWithMembersAndTypes and
    #    SystemClassWithMembersAndTypes) ----------------------------------
    def _read_member_type_info(self, count):
        r = self.r
        bin_types = [r.read_byte() for _ in range(count)]
        infos = []
        for bt in bin_types:
            info = {"binary_type": BINTYPE_NAMES.get(bt, bt)}
            if bt == BT_Primitive:
                pt = r.read_byte()
                info["primitive_type"] = PRIMITIVE_NAMES.get(pt, pt)
                info["_pt"] = pt
            elif bt == BT_PrimitiveArray:
                pt = r.read_byte()
                info["primitive_type"] = PRIMITIVE_NAMES.get(pt, pt)
                info["_pt"] = pt
            elif bt == BT_SystemClass:
                info["class_name"] = r.read_string()
            elif bt == BT_Class:
                info["class_name"] = r.read_string()
                info["library_id"] = r.read_int32()
            # String, Object, ObjectArray, StringArray: no additional info
            infos.append(info)
        return infos

    def _read_class_info(self):
        r = self.r
        object_id = r.read_int32()
        name = r.read_string()
        member_count = r.read_int32()
        member_names = [r.read_string() for _ in range(member_count)]
        return object_id, name, member_names

    def _read_class_with_members_and_types(self, system):
        r = self.r
        object_id, name, member_names = self._read_class_info()
        member_types = self._read_member_type_info(len(member_names))
        library_id = None
        if not system:
            library_id = r.read_int32()
        ci = ClassInfo(object_id, name, member_names, member_types,
                        library_id, system)
        self.classinfo_by_id[object_id] = ci
        members = self._read_members(ci)
        value = self._class_instance_dict(ci, members)
        return object_id, value

    def _read_class_with_members(self, system):
        # No per-member type info is transmitted on the wire for this record
        # shape. [MS-NRBF] leaves member typing to reflection on the
        # already-loaded CLR type at read time; we have no CLR. Two BCL/CLR
        # shapes need raw (unwrapped) primitive reads because that's what the
        # real writer emits for them -- see KNOWN_UNTYPED_CLASS_FIELDS and the
        # "value__" enum case below, both confirmed against actual bytes in
        # DSC_12G-HD.raw. For everything else (confirmed against
        # ObservableCollection`1 at DSC_12G-HD.raw offset 0xdc1, object id
        # not yet assigned at that point, members _monitor/Collection`1+items)
        # each member value IS a normal self-describing record (typically
        # MemberReference/BinaryObjectString/ObjectNull/nested class), so we
        # fall back to reading one record per member, exactly like
        # ArraySingleObject's element stream.
        r = self.r
        object_id, name, member_names = self._read_class_info()
        library_id = None
        if not system:
            library_id = r.read_int32()
        base_name = name.split("[", 1)[0]
        if member_names == ["value__"]:
            # .NET enum instance. Confirmed at DSC_12G-HD.raw offset 0x8d0,
            # object id -5, class Extron...DriverPackageStateEnum:
            # LibraryId=3 then raw bytes "00 00 00 00" (Int32 0), no
            # record-type byte.
            fields = [("value__", PT_Int32)]
        elif name in KNOWN_UNTYPED_CLASS_FIELDS:
            # Confirmed at DSC_12G-HD.raw offset 0xa1b, object id 12,
            # class System.Guid: LibraryId=None (SystemClass) then 16 raw
            # bytes (Int32 + Int16 + Int16 + 8 Bytes), no record-type bytes.
            fields = KNOWN_UNTYPED_CLASS_FIELDS[name]
        elif base_name in KNOWN_UNTYPED_CLASS_FIELDS_BY_BASENAME:
            fields = KNOWN_UNTYPED_CLASS_FIELDS_BY_BASENAME[base_name]
        else:
            fields = None
            for suffix, suffix_fields in KNOWN_UNTYPED_CLASS_FIELDS_BY_SUFFIX:
                if base_name.endswith(suffix):
                    fields = suffix_fields
                    break
            # else: fields stays None -> generic self-describing-record fallback,
            # i.e. treat every member as record-typed (matches everything
            # observed that ISN'T one of the raw-field BCL shapes above, e.g.
            # ObservableCollection`1 at DSC_12G-HD.raw offset 0xdc1).

        if fields is None:
            fields = [(mname, FIELD_RECORD) for mname in member_names]
        elif member_names != [f[0] for f in fields]:
            raise NrbfParseError(
                "ClassWithMembers for known type %r has unexpected member "
                "names %r (expected %r)" %
                (name, member_names, [f[0] for f in fields]),
                offset=r.tell())

        members = {}
        member_types = []
        for fname, mode in fields:
            if mode == FIELD_RECORD:
                off = r.tell()
                rt = r.read_byte()
                obj_id, val = self._read_object_record(rt, off)
                if obj_id is not None:
                    self.objects[obj_id] = val
                    members[fname] = {"$ref": obj_id}
                else:
                    members[fname] = val
                member_types.append({"binary_type": "Unknown(untyped-member,record-read)"})
            else:
                pt = mode
                members[fname] = self._read_primitive_value(pt)
                member_types.append({"binary_type": "Primitive",
                                      "primitive_type": PRIMITIVE_NAMES.get(pt, pt),
                                      "_pt": pt})
        ci = ClassInfo(object_id, name, member_names, member_types, library_id, system)
        self.classinfo_by_id[object_id] = ci
        value = self._class_instance_dict(ci, members)
        return object_id, value

    def _read_class_with_id(self):
        r = self.r
        object_id = r.read_int32()
        metadata_id = r.read_int32()
        ci = self.classinfo_by_id.get(metadata_id)
        if ci is None:
            raise NrbfParseError(
                "ClassWithId references unknown MetadataId %d" % metadata_id,
                offset=r.tell())
        members = self._read_members(ci)
        value = self._class_instance_dict(ci, members, via_id=metadata_id)
        return object_id, value

    def _class_instance_dict(self, ci, members, via_id=None):
        d = {
            "$type": "ClassWithId" if via_id is not None else
                     ("SystemClassWithMembersAndTypes" if ci.is_system else "ClassWithMembersAndTypes"),
            "class": ci.name,
            "members": members,
        }
        if ci.library_id is not None:
            d["library"] = self.libraries.get(ci.library_id, ci.library_id)
        if via_id is not None:
            d["metadata_ref"] = via_id
        return d

    def _read_members(self, ci: ClassInfo):
        r = self.r
        members = {}
        for mname, minfo in zip(ci.member_names, ci.member_types):
            bt = minfo["binary_type"]
            if bt == "Primitive":
                members[mname] = self._read_primitive_value(minfo["_pt"])
            elif bt in ("String", "Object", "SystemClass", "Class",
                        "ObjectArray", "StringArray", "PrimitiveArray",
                        "Unknown(untyped-member,record-read)"):
                off = r.tell()
                rt = r.read_byte()
                obj_id, val = self._read_object_record(rt, off)
                if obj_id is not None:
                    self.objects[obj_id] = val
                    members[mname] = {"$ref": obj_id}
                else:
                    members[mname] = val
            else:
                raise NrbfParseError(
                    "unrecognized member binary_type %r for member %s.%s" %
                    (bt, ci.name, mname), offset=r.tell())
        return members

    def _read_primitive_value(self, pt):
        r = self.r
        if pt == PT_Boolean:
            return bool(r.read_byte())
        elif pt == PT_Byte:
            return r.read_byte()
        elif pt == PT_SByte:
            v = r.read_byte()
            return v - 256 if v >= 128 else v
        elif pt == PT_Char:
            # UTF-8 encoded character per [MS-NRBF] 2.1.1.4 (variable width)
            first = r.read_byte()
            n = 1
            if first & 0xE0 == 0xC0:
                n = 2
            elif first & 0xF0 == 0xE0:
                n = 3
            elif first & 0xF8 == 0xF0:
                n = 4
            raw = bytes([first]) + (r.read(n - 1) if n > 1 else b"")
            return raw.decode("utf-8")
        elif pt == PT_Int16:
            return r.read_int16()
        elif pt == PT_UInt16:
            return r.read_uint16()
        elif pt == PT_Int32:
            return r.read_int32()
        elif pt == PT_UInt32:
            return r.read_uint32()
        elif pt == PT_Int64:
            return r.read_int64()
        elif pt == PT_UInt64:
            return r.read_uint64()
        elif pt == PT_Single:
            return r.read_single()
        elif pt == PT_Double:
            return r.read_double()
        elif pt == PT_Decimal:
            # Transmitted as a LengthPrefixedString of the decimal's
            # invariant-culture string form.
            return r.read_string()
        elif pt == PT_DateTime:
            # 8 bytes: 62-bit tick count + 2-bit DateTimeKind (MS-NRBF 2.1.1.2)
            raw = r.read_uint64()
            ticks = raw & 0x3FFFFFFFFFFFFFFF
            kind = raw >> 62
            return {"ticks": ticks, "kind": kind}
        elif pt == PT_TimeSpan:
            return r.read_int64()
        elif pt == PT_Null:
            return None
        elif pt == PT_String:
            off = r.tell()
            rt = r.read_byte()
            _, val = self._read_object_record(rt, off)
            return val
        else:
            raise NrbfParseError("unhandled primitive type %r" % pt,
                                  offset=r.tell())

    # -- arrays -----------------------------------------------------------
    def _read_array_single_object(self):
        r = self.r
        obj_id = r.read_int32()
        length = r.read_int32()
        items = self._read_array_items(length)
        return obj_id, {"$type": "ArraySingleObject", "length": length, "items": items}

    def _read_array_single_string(self):
        r = self.r
        obj_id = r.read_int32()
        length = r.read_int32()
        items = self._read_array_items(length)
        return obj_id, {"$type": "ArraySingleString", "length": length, "items": items}

    def _read_array_items(self, length):
        """Reads `length` logical member slots, honoring null-run compression
        records (ObjectNullMultiple[256]) which can each stand in for several
        consecutive null slots."""
        r = self.r
        items = []
        while len(items) < length:
            off = r.tell()
            rt = r.read_byte()
            obj_id, val = self._read_object_record(rt, off)
            if isinstance(val, dict) and "$null_run" in val:
                items.extend([None] * val["$null_run"])
                continue
            if obj_id is not None:
                self.objects[obj_id] = val
                items.append({"$ref": obj_id})
            else:
                items.append(val)
        return items

    def _read_array_single_primitive(self):
        r = self.r
        obj_id = r.read_int32()
        length = r.read_int32()
        pt = r.read_byte()
        items = [self._read_primitive_value(pt) for _ in range(length)]
        return obj_id, {
            "$type": "ArraySinglePrimitive",
            "primitive_type": PRIMITIVE_NAMES.get(pt, pt),
            "length": length,
            "items": items,
        }

    def _read_binary_array(self):
        r = self.r
        obj_id = r.read_int32()
        bat = r.read_byte()
        rank = r.read_int32()
        lengths = [r.read_int32() for _ in range(rank)]
        lower_bounds = None
        if bat in (BAT_SingleOffset, BAT_JaggedOffset, BAT_RectangularOffset):
            lower_bounds = [r.read_int32() for _ in range(rank)]
        bt = r.read_byte()
        addl = {}
        if bt == BT_Primitive or bt == BT_PrimitiveArray:
            pt = r.read_byte()
            addl["primitive_type"] = PRIMITIVE_NAMES.get(pt, pt)
        elif bt == BT_SystemClass:
            addl["class_name"] = r.read_string()
        elif bt == BT_Class:
            addl["class_name"] = r.read_string()
            addl["library_id"] = r.read_int32()

        total = 1
        for L in lengths:
            total *= L

        if bt in (BT_Primitive,):
            items = [self._read_primitive_value(
                [k for k, v in PRIMITIVE_NAMES.items() if v == addl["primitive_type"]][0])
                for _ in range(total)]
        else:
            items = self._read_array_items(total)

        return obj_id, {
            "$type": "BinaryArray",
            "array_type": BINARY_ARRAY_TYPE_NAMES.get(bat, bat),
            "rank": rank,
            "lengths": lengths,
            "lower_bounds": lower_bounds,
            "element_binary_type": BINTYPE_NAMES.get(bt, bt),
            **addl,
            "items": items,
        }

    def _read_member_primitive_typed(self):
        r = self.r
        pt = r.read_byte()
        return {"$type": "MemberPrimitiveTyped",
                "primitive_type": PRIMITIVE_NAMES.get(pt, pt),
                "value": self._read_primitive_value(pt)}


# --------------------------------------------------------------------------
# reference resolution / graph walking helpers
# --------------------------------------------------------------------------
def resolve_refs(obj, objects, _cache=None, _in_progress=None):
    """Recursively replace {'$ref': id} with the pointed-to object.

    The NRBF object graph is a DAG (often with real sharing -- the same
    EnumStateAsset/ParamAsset instance referenced from several places) and
    sometimes cyclic (e.g. AssetBase+_parentAsset pointing back up the
    tree). Naive recursive inlining duplicates every shared subtree at each
    place it's referenced, which is exponential in fan-in x depth; on
    DSC_12G-HD.raw this produced a 516MB JSON file before this fix. `_cache`
    memoizes each object id's resolved value so it is computed exactly once
    and then reused (by reference) everywhere else it's linked from;
    `_in_progress` detects genuine cycles (a ref back to an ancestor
    currently being resolved) and emits a `{"$cycle": id}` marker instead of
    recursing forever.
    """
    if _cache is None:
        _cache = {}
    if _in_progress is None:
        _in_progress = set()
    if isinstance(obj, dict):
        if set(obj.keys()) == {"$ref"}:
            tgt = obj["$ref"]
            if tgt in _cache:
                return _cache[tgt]
            if tgt in _in_progress:
                return {"$cycle": tgt}
            if tgt not in objects:
                return {"$unresolved_ref": tgt}
            _in_progress.add(tgt)
            resolved = resolve_refs(objects[tgt], objects, _cache, _in_progress)
            _in_progress.discard(tgt)
            _cache[tgt] = resolved
            return resolved
        return {k: resolve_refs(v, objects, _cache, _in_progress) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [resolve_refs(v, objects, _cache, _in_progress) for v in obj]
    else:
        return obj


def load_bytes(path):
    with open(path, "rb") as f:
        data = f.read()
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="path to .pkp (gzip) or already-decompressed .raw NRBF stream")
    ap.add_argument("-o", "--output", help="path to write JSON (default: stdout)")
    ap.add_argument("--resolve", action="store_true",
                     help="also emit a 'resolved_root' with $ref pointers inlined. "
                          "OFF BY DEFAULT: the NRBF object graph in these files has heavy "
                          "sharing/back-references (e.g. AssetBase+_parentAsset), so naive "
                          "inlining duplicates shared subtrees at every place they're "
                          "referenced and can blow up to hundreds of MB even though the "
                          "'objects' table (the actual graph, with $ref edges) stays small.")
    args = ap.parse_args()

    data = load_bytes(args.input)
    parser = PkpParser(data)
    try:
        parser.parse()
        error = None
    except NrbfParseError as e:
        error = {
            "message": str(e),
            "offset": e.offset,
            "record_type": e.record_type,
        }

    class_instance_counts = {}
    for v in parser.objects.values():
        if isinstance(v, dict) and "class" in v:
            class_instance_counts[v["class"]] = class_instance_counts.get(v["class"], 0) + 1

    out = {
        "source_file": args.input,
        "decompressed_size": len(data),
        "bytes_consumed": parser.r.tell(),
        "fully_parsed": error is None,
        "message_end_seen": parser.message_end_seen,
        "parse_error": error,
        "header": parser.header,
        "root_id": parser.root_id,
        "libraries": parser.libraries,
        "record_type_counts": parser.record_type_counts,
        "object_count": len(parser.objects),
        "class_instance_counts": class_instance_counts,
        "objects": parser.objects,
    }
    if args.resolve and parser.root_id in parser.objects:
        out["resolved_root"] = resolve_refs(parser.objects[parser.root_id], parser.objects)

    text = json.dumps(out, indent=1, default=str)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
        print("wrote %s (%d bytes)" % (args.output, len(text)), file=sys.stderr)
    else:
        print(text)

    if error:
        print("PARSE ERROR: %s" % error["message"], file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
