#!/usr/bin/env python3
"""
pkg_dump.py - Crestron .pkg driver-package extractor, the counterpart to
pkp_dump.py.

A Crestron .pkg is a plain ZIP. Established by direct inspection (see the
project's findings/ notes):

  * <name>.dat is a JSON capability manifest.
  * Packages with a DLL (Serial/IP/Ethernet drivers) ship <name>.dll: a CLR
    assembly whose ENTIRE embedded driver-definition JSON is stored as a
    CLR ManifestResource -- raw bytes in .text behind a 4-byte
    little-endian length prefix, NOT inside a metadata heap, optionally
    preceded by a UTF-8 BOM.
  * IR packages have no DLL: <name>.ir + <name>.dat (+ a .pdf), and there is
    no driver-definition JSON to extract.

This tool does NOT hardcode any file offset. It parses the PE headers, finds
the CLI header (IMAGE_COR20_HEADER) via the COM descriptor data directory,
reads the Resources RVA/size, and walks the ManifestResource table in the
'#~' metadata heap (per ECMA-335) to resolve the resource's offset within
the Resources blob properly, then reads the 4-byte length prefix at that
offset. A brace-matched '"SchemaVersion"' scan is used ONLY as a fallback if
metadata parsing fails for any reason, and that fact is recorded in the
output 'notes'.

Usage:
    python3 pkg_dump.py <file.pkg | dir-of-pkgs> [-o out.json | -o out-dir]
    python3 pkg_dump.py <file.pkg | dir-of-pkgs> --summary

This tool fails loudly (raises) on anything unexpected: a .pkg with no
.dat, more than one .dat/.dll, a .dll with no CLI header, a .dll with no
ManifestResource rows, or a driver-definition payload that is neither
parseable as CLI metadata nor recoverable via the fallback scan.
"""
import argparse
import json
import os
import struct
import sys
import zipfile


# ==========================================================================
# Errors
# ==========================================================================

class PEFormatError(Exception):
    """The bytes handed to PEImage are not a well-formed PE/CLI assembly."""


class MetadataParseError(Exception):
    """The PE parsed, but ECMA-335 metadata inside it did not make sense."""


class DriverExtractionError(Exception):
    """Neither CLI-metadata parsing nor the brace-scan fallback worked."""


class PkgFormatError(Exception):
    """A .pkg's contents didn't match any of the shapes we know about."""


# ==========================================================================
# ECMA-335 metadata tables: names, coded-index definitions, row layouts
# ==========================================================================

TABLE_NAMES = {
    0x00: "Module", 0x01: "TypeRef", 0x02: "TypeDef", 0x03: "FieldPtr",
    0x04: "Field", 0x05: "MethodPtr", 0x06: "MethodDef", 0x07: "ParamPtr",
    0x08: "Param", 0x09: "InterfaceImpl", 0x0A: "MemberRef", 0x0B: "Constant",
    0x0C: "CustomAttribute", 0x0D: "FieldMarshal", 0x0E: "DeclSecurity",
    0x0F: "ClassLayout", 0x10: "FieldLayout", 0x11: "StandAloneSig",
    0x12: "EventMap", 0x13: "EventPtr", 0x14: "Event", 0x15: "PropertyMap",
    0x16: "PropertyPtr", 0x17: "Property", 0x18: "MethodSemantics",
    0x19: "MethodImpl", 0x1A: "ModuleRef", 0x1B: "TypeSpec", 0x1C: "ImplMap",
    0x1D: "FieldRVA", 0x1E: "ENCLog", 0x1F: "ENCMap", 0x20: "Assembly",
    0x21: "AssemblyProcessor", 0x22: "AssemblyOS", 0x23: "AssemblyRef",
    0x24: "AssemblyRefProcessor", 0x25: "AssemblyRefOS", 0x26: "File",
    0x27: "ExportedType", 0x28: "ManifestResource", 0x29: "NestedClass",
    0x2A: "GenericParam", 0x2B: "MethodSpec", 0x2C: "GenericParamConstraint",
}
TABLE_IDS = {name: tid for tid, name in TABLE_NAMES.items()}

# name -> (tag_bit_width, [table_name_or_None, ...]) per ECMA-335 II.24.2.6
CODED_INDEXES = {
    "ResolutionScope": (2, ["Module", "ModuleRef", "AssemblyRef", "TypeRef"]),
    "TypeDefOrRef": (2, ["TypeDef", "TypeRef", "TypeSpec"]),
    "MemberRefParent": (3, ["TypeDef", "TypeRef", "ModuleRef", "MethodDef", "TypeSpec"]),
    "HasConstant": (2, ["Field", "Param", "Property"]),
    "HasCustomAttribute": (5, [
        "MethodDef", "Field", "TypeRef", "TypeDef", "Param", "InterfaceImpl",
        "MemberRef", "Module", "DeclSecurity", "Property", "Event",
        "StandAloneSig", "ModuleRef", "TypeSpec", "Assembly", "AssemblyRef",
        "File", "ExportedType", "ManifestResource", "GenericParam",
        "GenericParamConstraint", "MethodSpec",
    ]),
    "HasFieldMarshal": (1, ["Field", "Param"]),
    "HasDeclSecurity": (2, ["TypeDef", "MethodDef", "Assembly"]),
    "HasSemantics": (1, ["Event", "Property"]),
    "MethodDefOrRef": (1, ["MethodDef", "MemberRef"]),
    "MemberForwarded": (1, ["Field", "MethodDef"]),
    "Implementation": (2, ["File", "AssemblyRef", "ExportedType"]),
    "CustomAttributeType": (3, [None, None, "MethodDef", "MemberRef", None, None]),
    "TypeOrMethodDef": (1, ["TypeDef", "MethodDef"]),
}

# table name -> [(column_name, kind), ...]
# kind is one of: "u16", "u32", "string", "guid", "blob",
#                 ("simple", TableName), ("coded", CodedIndexName)
TABLE_COLUMNS = {
    "Module": [("Generation", "u16"), ("Name", "string"), ("Mvid", "guid"),
               ("EncId", "guid"), ("EncBaseId", "guid")],
    "TypeRef": [("ResolutionScope", ("coded", "ResolutionScope")),
                ("Name", "string"), ("Namespace", "string")],
    "TypeDef": [("Flags", "u32"), ("Name", "string"), ("Namespace", "string"),
                ("Extends", ("coded", "TypeDefOrRef")),
                ("FieldList", ("simple", "Field")),
                ("MethodList", ("simple", "MethodDef"))],
    "FieldPtr": [("Field", ("simple", "Field"))],
    "Field": [("Flags", "u16"), ("Name", "string"), ("Signature", "blob")],
    "MethodPtr": [("Method", ("simple", "MethodDef"))],
    "MethodDef": [("RVA", "u32"), ("ImplFlags", "u16"), ("Flags", "u16"),
                  ("Name", "string"), ("Signature", "blob"),
                  ("ParamList", ("simple", "Param"))],
    "ParamPtr": [("Param", ("simple", "Param"))],
    "Param": [("Flags", "u16"), ("Sequence", "u16"), ("Name", "string")],
    "InterfaceImpl": [("Class", ("simple", "TypeDef")),
                       ("Interface", ("coded", "TypeDefOrRef"))],
    "MemberRef": [("Class", ("coded", "MemberRefParent")),
                  ("Name", "string"), ("Signature", "blob")],
    "Constant": [("Type", "u16"), ("Parent", ("coded", "HasConstant")),
                 ("Value", "blob")],
    "CustomAttribute": [("Parent", ("coded", "HasCustomAttribute")),
                         ("Type", ("coded", "CustomAttributeType")),
                         ("Value", "blob")],
    "FieldMarshal": [("Parent", ("coded", "HasFieldMarshal")),
                      ("NativeType", "blob")],
    "DeclSecurity": [("Action", "u16"), ("Parent", ("coded", "HasDeclSecurity")),
                      ("PermissionSet", "blob")],
    "ClassLayout": [("PackingSize", "u16"), ("ClassSize", "u32"),
                     ("Parent", ("simple", "TypeDef"))],
    "FieldLayout": [("Offset", "u32"), ("Field", ("simple", "Field"))],
    "StandAloneSig": [("Signature", "blob")],
    "EventMap": [("Parent", ("simple", "TypeDef")),
                 ("EventList", ("simple", "Event"))],
    "EventPtr": [("Event", ("simple", "Event"))],
    "Event": [("EventFlags", "u16"), ("Name", "string"),
              ("EventType", ("coded", "TypeDefOrRef"))],
    "PropertyMap": [("Parent", ("simple", "TypeDef")),
                     ("PropertyList", ("simple", "Property"))],
    "PropertyPtr": [("Property", ("simple", "Property"))],
    "Property": [("Flags", "u16"), ("Name", "string"), ("Type", "blob")],
    "MethodSemantics": [("Semantics", "u16"), ("Method", ("simple", "MethodDef")),
                         ("Association", ("coded", "HasSemantics"))],
    "MethodImpl": [("Class", ("simple", "TypeDef")),
                    ("MethodBody", ("coded", "MethodDefOrRef")),
                    ("MethodDeclaration", ("coded", "MethodDefOrRef"))],
    "ModuleRef": [("Name", "string")],
    "TypeSpec": [("Signature", "blob")],
    "ImplMap": [("MappingFlags", "u16"),
                ("MemberForwarded", ("coded", "MemberForwarded")),
                ("ImportName", "string"), ("ImportScope", ("simple", "ModuleRef"))],
    "FieldRVA": [("RVA", "u32"), ("Field", ("simple", "Field"))],
    "ENCLog": [("Token", "u32"), ("FuncCode", "u32")],
    "ENCMap": [("Token", "u32")],
    "Assembly": [("HashAlgId", "u32"), ("MajorVersion", "u16"),
                 ("MinorVersion", "u16"), ("BuildNumber", "u16"),
                 ("RevisionNumber", "u16"), ("Flags", "u32"),
                 ("PublicKey", "blob"), ("Name", "string"), ("Culture", "string")],
    "AssemblyProcessor": [("Processor", "u32")],
    "AssemblyOS": [("OSPlatformID", "u32"), ("OSMajorVersion", "u32"),
                    ("OSMinorVersion", "u32")],
    "AssemblyRef": [("MajorVersion", "u16"), ("MinorVersion", "u16"),
                     ("BuildNumber", "u16"), ("RevisionNumber", "u16"),
                     ("Flags", "u32"), ("PublicKeyOrToken", "blob"),
                     ("Name", "string"), ("Culture", "string"),
                     ("HashValue", "blob")],
    "AssemblyRefProcessor": [("Processor", "u32"),
                              ("AssemblyRef", ("simple", "AssemblyRef"))],
    "AssemblyRefOS": [("OSPlatformID", "u32"), ("OSMajorVersion", "u32"),
                       ("OSMinorVersion", "u32"),
                       ("AssemblyRef", ("simple", "AssemblyRef"))],
    "File": [("Flags", "u32"), ("Name", "string"), ("HashValue", "blob")],
    "ExportedType": [("Flags", "u32"), ("TypeDefId", "u32"),
                      ("TypeName", "string"), ("TypeNamespace", "string"),
                      ("Implementation", ("coded", "Implementation"))],
    "ManifestResource": [("Offset", "u32"), ("Flags", "u32"),
                          ("Name", "string"),
                          ("Implementation", ("coded", "Implementation"))],
    "NestedClass": [("NestedClass", ("simple", "TypeDef")),
                     ("EnclosingClass", ("simple", "TypeDef"))],
    "GenericParam": [("Number", "u16"), ("Flags", "u16"),
                      ("Owner", ("coded", "TypeOrMethodDef")), ("Name", "string")],
    "MethodSpec": [("Method", ("coded", "MethodDefOrRef")),
                    ("Instantiation", "blob")],
    "GenericParamConstraint": [("Owner", ("simple", "GenericParam")),
                                ("Constraint", ("coded", "TypeDefOrRef"))],
}

IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR = 14


def _u16(data, off):
    return struct.unpack_from("<H", data, off)[0]


def _u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


# ==========================================================================
# PE / CLI parsing
# ==========================================================================

class PEImage:
    """Minimal PE32/PE32+ + CLI-header (ECMA-335) reader.

    Only the pieces needed to reach the ManifestResource table and its
    backing Resources blob are implemented; this is not a general PE parser.
    """

    def __init__(self, data):
        self.data = data
        self._parse_dos_and_coff()
        self._parse_sections()

    def _parse_dos_and_coff(self):
        d = self.data
        if len(d) < 0x40 or d[0:2] != b"MZ":
            raise PEFormatError("missing MZ signature")
        e_lfanew = _u32(d, 0x3C)
        if e_lfanew <= 0 or e_lfanew + 24 > len(d):
            raise PEFormatError("e_lfanew out of range (%d)" % e_lfanew)
        if d[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
            raise PEFormatError("missing PE signature at 0x%x" % e_lfanew)
        coff_off = e_lfanew + 4
        self.number_of_sections = _u16(d, coff_off + 2)
        self.size_of_optional_header = _u16(d, coff_off + 16)
        self.optional_header_offset = coff_off + 20
        if self.size_of_optional_header < 2:
            raise PEFormatError("optional header too small / absent")
        magic = _u16(d, self.optional_header_offset)
        if magic == 0x10B:
            self.is_pe32_plus = False
            num_rva_off = self.optional_header_offset + 92
            self.data_directory_offset = self.optional_header_offset + 96
        elif magic == 0x20B:
            self.is_pe32_plus = True
            num_rva_off = self.optional_header_offset + 108
            self.data_directory_offset = self.optional_header_offset + 112
        else:
            raise PEFormatError("unrecognised optional-header magic 0x%x" % magic)
        self.number_of_rva_and_sizes = _u32(d, num_rva_off)
        self.section_table_offset = self.optional_header_offset + self.size_of_optional_header

    def _parse_sections(self):
        d = self.data
        sections = []
        for i in range(self.number_of_sections):
            so = self.section_table_offset + i * 40
            if so + 40 > len(d):
                raise PEFormatError("section table entry %d out of range" % i)
            name = d[so:so + 8].rstrip(b"\x00").decode("ascii", "replace")
            virtual_size = _u32(d, so + 8)
            virtual_address = _u32(d, so + 12)
            size_of_raw_data = _u32(d, so + 16)
            pointer_to_raw_data = _u32(d, so + 20)
            sections.append({
                "name": name,
                "virtual_size": virtual_size,
                "virtual_address": virtual_address,
                "size_of_raw_data": size_of_raw_data,
                "pointer_to_raw_data": pointer_to_raw_data,
            })
        self.sections = sections

    def com_descriptor_directory_offset(self):
        if self.number_of_rva_and_sizes <= IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR:
            raise PEFormatError("data directory array too short for COM descriptor entry")
        return self.data_directory_offset + IMAGE_DIRECTORY_ENTRY_COM_DESCRIPTOR * 8

    def rva_to_offset(self, rva):
        for s in self.sections:
            size = max(s["virtual_size"], s["size_of_raw_data"])
            if s["virtual_address"] <= rva < s["virtual_address"] + size:
                return s["pointer_to_raw_data"] + (rva - s["virtual_address"])
        raise PEFormatError("RVA 0x%x not covered by any section" % rva)

    def cor20_header(self):
        d = self.data
        dd_off = self.com_descriptor_directory_offset()
        com_rva = _u32(d, dd_off)
        com_size = _u32(d, dd_off + 4)
        if com_rva == 0 or com_size == 0:
            raise PEFormatError("no COM descriptor (CLI header) directory entry: not a CLR assembly")
        cor20_off = self.rva_to_offset(com_rva)
        if cor20_off + 72 > len(d):
            raise PEFormatError("CLI header at 0x%x runs past end of file" % cor20_off)
        cb = _u32(d, cor20_off)
        if cb < 72:
            raise PEFormatError("IMAGE_COR20_HEADER.cb implausibly small (%d)" % cb)
        return {
            "file_offset": cor20_off,
            "cb": cb,
            "major_runtime_version": _u16(d, cor20_off + 4),
            "minor_runtime_version": _u16(d, cor20_off + 6),
            "metadata_rva": _u32(d, cor20_off + 8),
            "metadata_size": _u32(d, cor20_off + 12),
            "flags": _u32(d, cor20_off + 16),
            "entry_point_token": _u32(d, cor20_off + 20),
            "resources_rva": _u32(d, cor20_off + 24),
            "resources_size": _u32(d, cor20_off + 28),
        }

    def metadata_root(self, metadata_rva, metadata_size):
        d = self.data
        meta_off = self.rva_to_offset(metadata_rva)
        if d[meta_off:meta_off + 4] != b"BSJB":
            raise MetadataParseError("metadata root missing BSJB signature at 0x%x" % meta_off)
        version_len = _u32(d, meta_off + 12)
        p = meta_off + 16 + version_len
        flags = _u16(d, p); p += 2  # noqa: E702
        num_streams = _u16(d, p); p += 2  # noqa: E702
        streams = {}
        for _ in range(num_streams):
            s_off = _u32(d, p); p += 4  # noqa: E702
            s_size = _u32(d, p); p += 4  # noqa: E702
            end = d.index(b"\x00", p)
            if end - p > 64:
                raise MetadataParseError("implausible stream-name length at 0x%x" % p)
            name = d[p:end].decode("ascii")
            p = end + 1
            p = (p + 3) & ~3  # 4-byte align
            streams[name] = (meta_off + s_off, s_size)
        return streams


def _table_ordinal(table_name):
    return TABLE_IDS[table_name]


class TablesStream:
    """Parses the '#~' (or '#-') metadata tables stream far enough to walk
    to the ManifestResource table, per ECMA-335 II.24.2.6."""

    def __init__(self, data, tilde_off, strings_off, guid_off, blob_off):
        self.data = data
        d = data
        self.heap_sizes = d[tilde_off + 6]
        valid = struct.unpack_from("<Q", d, tilde_off + 8)[0]
        p = tilde_off + 24
        self.row_counts = {}
        for i in range(64):
            if valid & (1 << i):
                if i not in TABLE_NAMES:
                    raise MetadataParseError("unknown/unsupported metadata table id 0x%x is present" % i)
                self.row_counts[i] = _u32(d, p)
                p += 4
        self._first_row_offset = p
        self.strings_off = strings_off
        self.guid_off = guid_off
        self.blob_off = blob_off

    @property
    def string_index_size(self):
        return 4 if (self.heap_sizes & 0x1) else 2

    @property
    def guid_index_size(self):
        return 4 if (self.heap_sizes & 0x2) else 2

    @property
    def blob_index_size(self):
        return 4 if (self.heap_sizes & 0x4) else 2

    def _row_count(self, table_name):
        return self.row_counts.get(_table_ordinal(table_name), 0)

    def _simple_index_size(self, table_name):
        return 4 if self._row_count(table_name) > 0xFFFF else 2

    def _coded_index_size(self, coded_name):
        bits, tables = CODED_INDEXES[coded_name]
        max_rows = max((self._row_count(t) for t in tables if t is not None), default=0)
        return 4 if max_rows >= (1 << (16 - bits)) else 2

    def _column_size(self, kind):
        if kind == "u16":
            return 2
        if kind == "u32":
            return 4
        if kind == "string":
            return self.string_index_size
        if kind == "guid":
            return self.guid_index_size
        if kind == "blob":
            return self.blob_index_size
        if isinstance(kind, tuple) and kind[0] == "simple":
            return self._simple_index_size(kind[1])
        if isinstance(kind, tuple) and kind[0] == "coded":
            return self._coded_index_size(kind[1])
        raise MetadataParseError("unknown column kind %r" % (kind,))

    def _row_size(self, table_name):
        return sum(self._column_size(kind) for _, kind in TABLE_COLUMNS[table_name])

    def _read_string(self, idx):
        off = self.strings_off + idx
        end = self.data.index(b"\x00", off)
        return self.data[off:end].decode("utf-8", "replace")

    def manifest_resources(self):
        """Walk table row-blocks in ascending table-id order (as stored)
        until ManifestResource (0x28), decoding only that table's rows."""
        d = self.data
        p = self._first_row_offset
        results = []
        for tid in sorted(self.row_counts):
            table_name = TABLE_NAMES[tid]
            count = self.row_counts[tid]
            row_size = self._row_size(table_name)
            if table_name == "ManifestResource":
                for r in range(count):
                    row_off = p + r * row_size
                    q = row_off
                    row = {}
                    for colname, kind in TABLE_COLUMNS[table_name]:
                        if kind == "u32":
                            row[colname] = _u32(d, q); q += 4  # noqa: E702
                        elif kind == "u16":
                            row[colname] = _u16(d, q); q += 2  # noqa: E702
                        elif kind == "string":
                            size = self.string_index_size
                            idx = _u16(d, q) if size == 2 else _u32(d, q)
                            q += size
                            row[colname] = self._read_string(idx)
                        elif isinstance(kind, tuple) and kind[0] == "coded":
                            size = self._coded_index_size(kind[1])
                            raw = _u16(d, q) if size == 2 else _u32(d, q)
                            q += size
                            bits, tables = CODED_INDEXES[kind[1]]
                            tag = raw & ((1 << bits) - 1)
                            index = raw >> bits
                            row[colname] = {"table": tables[tag], "row_index": index}
                        else:
                            raise MetadataParseError(
                                "unexpected column kind %r in ManifestResource" % (kind,))
                    results.append(row)
            p += row_size * count
        return results


def parse_manifest_resources_via_metadata(dll_bytes):
    """Returns (resources_data_offset_in_file, [manifest_resource_row, ...])."""
    pe = PEImage(dll_bytes)
    cor20 = pe.cor20_header()
    streams = pe.metadata_root(cor20["metadata_rva"], cor20["metadata_size"])
    tilde = streams.get("#~") or streams.get("#-")
    if tilde is None:
        raise MetadataParseError("no #~ / #- metadata tables stream present")
    strings = streams.get("#Strings")
    if strings is None:
        raise MetadataParseError("no #Strings heap present")
    guid = streams.get("#GUID", (0, 0))
    blob = streams.get("#Blob", (0, 0))
    tables = TablesStream(dll_bytes, tilde[0], strings[0], guid[0], blob[0])
    rows = tables.manifest_resources()
    if not rows:
        raise MetadataParseError("metadata parsed but ManifestResource table has zero rows")
    resources_offset = pe.rva_to_offset(cor20["resources_rva"])
    return resources_offset, rows


# ==========================================================================
# Fallback: brace-matched scan
# ==========================================================================

def brace_match_scan(data, marker):
    """Find `marker` (e.g. b'"SchemaVersion"'), walk backward to the nearest
    unescaped '{' before it, then forward doing proper brace/string/escape
    tracking to find the matching close brace. Returns the raw JSON bytes
    (no BOM). Raises DriverExtractionError if it can't be found or the
    braces never balance.
    """
    marker_idx = data.find(marker)
    if marker_idx == -1:
        raise DriverExtractionError("fallback scan: marker %r not found" % marker)
    start = data.rfind(b"{", 0, marker_idx)
    if start == -1:
        raise DriverExtractionError("fallback scan: no '{' precedes marker at %d" % marker_idx)

    depth = 0
    in_string = False
    escape = False
    i = start
    n = len(data)
    while i < n:
        b = data[i:i + 1]
        if in_string:
            if escape:
                escape = False
            elif b == b"\\":
                escape = True
            elif b == b'"':
                in_string = False
        else:
            if b == b'"':
                in_string = True
            elif b == b"{":
                depth += 1
            elif b == b"}":
                depth -= 1
                if depth == 0:
                    return data[start:i + 1]
        i += 1
    raise DriverExtractionError("fallback scan: braces never balanced starting at %d" % start)


# ==========================================================================
# Driver-definition extraction (metadata first, brace-scan fallback)
# ==========================================================================

class DriverDefinitionResult:
    def __init__(self, definition, raw_bytes, method, resource_name, notes):
        self.definition = definition
        self.raw_bytes = raw_bytes
        self.method = method              # "cli-metadata" or "brace-scan"
        self.resource_name = resource_name
        self.notes = notes


def _strip_bom(raw):
    if raw[:3] == b"\xef\xbb\xbf":
        return raw[3:], True
    return raw, False


def extract_driver_definition(dll_bytes):
    notes = []
    try:
        resources_offset, rows = parse_manifest_resources_via_metadata(dll_bytes)
    except (PEFormatError, MetadataParseError) as e:
        notes.append("CLI-metadata parse failed (%s); falling back to brace-matched "
                     "'\"SchemaVersion\"' scan" % e)
        try:
            raw = brace_match_scan(dll_bytes, b'"SchemaVersion"')
        except DriverExtractionError as e2:
            raise DriverExtractionError(
                "both CLI-metadata parsing and the brace-scan fallback failed: "
                "metadata error=%r, fallback error=%r" % (str(e), str(e2)))
        stripped, had_bom = _strip_bom(raw)
        if had_bom:
            notes.append("resource payload had a UTF-8 BOM (stripped before JSON parsing; "
                         "raw_bytes below still includes it)")
        try:
            definition = json.loads(stripped.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e3:
            raise DriverExtractionError("fallback scan found bytes but they are not valid JSON: %s" % e3)
        return DriverDefinitionResult(definition, raw, "brace-scan", None, notes)

    if len(rows) > 1:
        notes.append("DLL has %d ManifestResource rows; using the first one that parses as JSON" % len(rows))

    last_error = None
    for row in rows:
        impl = row.get("Implementation") or {}
        if impl.get("row_index", 0) != 0:
            notes.append("ManifestResource %r has a non-null Implementation "
                         "(resource lives in another file) -- skipping" % row.get("Name"))
            continue
        offset = resources_offset + row["Offset"]
        if offset + 4 > len(dll_bytes):
            last_error = "resource %r offset out of range" % row.get("Name")
            continue
        length = _u32(dll_bytes, offset)
        payload_start = offset + 4
        payload_end = payload_start + length
        if payload_end > len(dll_bytes):
            last_error = "resource %r length prefix (%d) runs past end of file" % (row.get("Name"), length)
            continue
        raw = dll_bytes[payload_start:payload_end]
        stripped, had_bom = _strip_bom(raw)
        if had_bom:
            notes.append("resource %r payload had a UTF-8 BOM (stripped before JSON parsing; "
                         "raw_bytes/size below still include it)" % row.get("Name"))
        try:
            definition = json.loads(stripped.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            last_error = "resource %r is not valid UTF-8 JSON: %s" % (row.get("Name"), e)
            continue
        return DriverDefinitionResult(definition, raw, "cli-metadata", row.get("Name"), notes)

    raise DriverExtractionError(
        "CLI metadata parsed and found %d ManifestResource row(s), but none of them held "
        "parseable JSON (last error: %s)" % (len(rows), last_error))


# ==========================================================================
# .pkg (ZIP) handling
# ==========================================================================

def _decode_json_bytes(raw, label):
    stripped, _had_bom = _strip_bom(raw)
    try:
        return json.loads(stripped.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise PkgFormatError("%s is not valid UTF-8 JSON: %s" % (label, e))


def process_pkg(pkg_path):
    notes = []
    with zipfile.ZipFile(pkg_path) as z:
        infos = z.infolist()
        members = [{"name": i.filename, "size": i.file_size,
                    "compressed_size": i.compress_size} for i in infos]
        names = [i.filename for i in infos]

        dat_names = [n for n in names if n.lower().endswith(".dat")]
        dll_names = [n for n in names if n.lower().endswith(".dll")]
        ir_names = [n for n in names if n.lower().endswith(".ir")]

        if len(dat_names) != 1:
            raise PkgFormatError(
                "%s: expected exactly one .dat manifest, found %d (%r)"
                % (pkg_path, len(dat_names), dat_names))
        if len(dll_names) > 1:
            raise PkgFormatError(
                "%s: expected at most one .dll, found %d (%r)"
                % (pkg_path, len(dll_names), dll_names))

        manifest = _decode_json_bytes(z.read(dat_names[0]), "%s (%s)" % (pkg_path, dat_names[0]))

        driver_definition = None
        resource_info = None
        if dll_names:
            dll_bytes = z.read(dll_names[0])
            result = extract_driver_definition(dll_bytes)
            notes.extend(result.notes)
            driver_definition = result.definition
            resource_info = {
                "resource_name": result.resource_name,
                "size": len(result.raw_bytes),
                "method": result.method,
            }
        else:
            notes.append("package has no .dll: no driver-definition JSON to extract")
            if ir_names:
                notes.append("IR package: %s present instead" % ir_names[0])
            else:
                notes.append("no .dll and no .ir member found -- unusual for a Crestron .pkg")

    return {
        "package": os.path.basename(pkg_path),
        "source_path": pkg_path,
        "members": members,
        "manifest": manifest,
        "driver_definition": driver_definition,
        "resource": resource_info,
        "notes": notes,
    }


def process_path(path):
    if os.path.isdir(path):
        pkgs = sorted(
            os.path.join(root, f)
            for root, _dirs, files in os.walk(path)
            for f in files
            if f.lower().endswith(".pkg")
        )
        if not pkgs:
            raise PkgFormatError("no .pkg files found under directory %s" % path)
        return [process_pkg(p) for p in pkgs]
    return [process_pkg(path)]


def summary_line(doc):
    n_members = len(doc["members"])
    if doc["resource"] is None:
        resource_part = "no-dll"
    else:
        resource_part = "resource_size=%d method=%s" % (doc["resource"]["size"], doc["resource"]["method"])
    if doc["driver_definition"] is not None:
        section_count = len(doc["driver_definition"])
    else:
        section_count = 0
    return "%-70s members=%d %s driver_sections=%d" % (
        doc["package"], n_members, resource_part, section_count)


# ==========================================================================
# CLI
# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input", help="path to a .pkg file, or a directory containing .pkg files")
    ap.add_argument("-o", "--output",
                     help="write JSON here: a file for a single package, or a directory "
                          "(one <name>.json per package) when processing a directory")
    ap.add_argument("--summary", action="store_true",
                     help="print one summary line per package instead of full JSON")
    args = ap.parse_args()

    docs = process_path(args.input)

    if args.summary:
        for doc in docs:
            print(summary_line(doc))
        return

    if len(docs) == 1 and not os.path.isdir(args.input):
        text = json.dumps(docs[0], indent=1, default=str)
        if args.output:
            with open(args.output, "w") as f:
                f.write(text)
            print("wrote %s (%d bytes)" % (args.output, len(text)), file=sys.stderr)
        else:
            print(text)
        return

    if args.output:
        os.makedirs(args.output, exist_ok=True)
        for doc in docs:
            out_path = os.path.join(args.output, os.path.splitext(doc["package"])[0] + ".json")
            with open(out_path, "w") as f:
                f.write(json.dumps(doc, indent=1, default=str))
            print("wrote %s" % out_path, file=sys.stderr)
    else:
        print(json.dumps(docs, indent=1, default=str))


if __name__ == "__main__":
    main()
