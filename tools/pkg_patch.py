#!/usr/bin/env python3
"""
pkg_patch.py - strategy-A Crestron .pkg resource patcher.

Given a .pkg (a ZIP) whose DLL embeds the driver-definition JSON as a CLR
ManifestResource -- raw bytes in .text behind a 4-byte little-endian length
prefix, optionally preceded by a UTF-8 BOM, exactly as pkg_dump.py describes
and locates it -- replace that JSON and write a new .pkg.

This module reuses pkg_dump.py's real ECMA-335 metadata walk (PEImage,
cor20_header, parse_manifest_resources_via_metadata) to find the resource.
It does NOT hardcode any file offset for a specific driver: every location
used below is read from the PE/CLI headers or the metadata tables of the
DLL being patched.

Three edit shapes are implemented, verified against the reference Samsung
Serial DLL (see test_pkg_patch.py) by re-parsing the result with pkg_dump
and by re-walking the structures this module itself had to move:

  1. Same-size or shrinking edit -- pad the vacated tail of the resource
     with zero bytes. The metadata root, import directory etc. that follow
     the resource in the file are untouched: their absolute RVAs (recorded
     independently in the CLI header / data directories) do not depend on
     where the resource's *content* ends, only on where the *file* has
     already told the loader to look. Confirmed by direct inspection of the
     Samsung Serial DLL: finding 06 already established this for the
     same-length case; shrinking is the same argument with pad > 0.

  2. Growing edit that fits in the section's trailing slack -- the CLI
     metadata root and the Import Directory table that (in the reference
     DLL) sit immediately after the resource are shifted forward by the
     growth amount rounded up to a 4-byte boundary (dead padding bytes,
     outside the resource's own length prefix, absorb the difference), so
     the metadata root -- whose stream-name padding pkg_dump computes
     relative to its own start -- stays 4-byte aligned. A first version of
     this module shifted by the raw, unrounded growth amount; against the
     reference DLL that silently corrupted the "#Strings" stream name for
     any growth not itself a multiple of 4, caught by the metadata re-parse
     in test_pkg_patch.py, not by anything that merely re-reads the JSON.
     Within the same section's raw data, every RVA this module found to
     reference something inside that shifted block (the
     COR20 header's MetaData directory entry, the Import Directory data
     directory entry, the import descriptor's OriginalFirstThunk/Name/
     FirstThunk fields, and the individual entries of the Import Lookup
     Table and Import Address Table that those fields point at) is patched
     to match. No section header needs to change: the section's raw/virtual
     size is untouched, only content within it moved. This is implemented
     generically (a bounded walk of the import descriptor/thunk structures,
     not a hardcoded RVA list) but it ONLY runs when the observed layout
     matches what was verified against the reference DLL: the resource is
     immediately followed by the metadata root, which is immediately
     followed by the Import Directory, all inside one section. Any other
     layout is refused rather than guessed (see `PatchNotSupportedError`).

  3. Growth that exceeds the trailing slack -- refused with a clear error.
     Moving or resizing a later PE section (.rsrc / .reloc), and updating
     every RVA/offset in the file that depends on their position, is not
     implemented; emitting a corrupt image would be worse than refusing.

Authenticode: this module DETECTS and REPORTS whether the DLL carries a
Security-directory (Authenticode) signature and says what the patch does to
it (any content edit invalidates the embedded hash, since nothing here
recomputes or re-signs it). Re-signing is explicitly out of scope. An
optional --strip-signature / strip_signature=True instead removes the
Security directory and its trailing certificate bytes outright, so the
output is honestly unsigned rather than signed-but-invalid; it is off by
default and never produces a new signature.

Usage:
    python3 pkg_patch.py <in.pkg> -o <out.pkg> --json-file <new_definition.json>
    python3 pkg_patch.py <in.pkg> -o <out.pkg> --same          # identity round-trip
    python3 pkg_patch.py <in.pkg> -o <out.pkg> --same --strip-signature
"""
import argparse
import json
import os
import struct
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pkg_dump as pd  # noqa: E402


# ==========================================================================
# Errors
# ==========================================================================

class PkgPatchError(Exception):
    """Something about the input .pkg / DLL made patching impossible."""


class PatchNotSupportedError(PkgPatchError):
    """The requested edit is a real shape this module does not (yet, or
    ever, without further verification) implement -- refused rather than
    guessed. The message says exactly what was needed and why it was
    refused."""


# ==========================================================================
# PE data-directory helpers (pkg_dump.PEImage covers COM_Descriptor only;
# patching needs a couple more of the standard 16 directory entries)
# ==========================================================================

IMAGE_DIRECTORY_ENTRY_IMPORT = 1
IMAGE_DIRECTORY_ENTRY_SECURITY = 4
IMAGE_DIRECTORY_ENTRY_IAT = 12

BOM = b"\xef\xbb\xbf"


def _u32(d, o):
    return struct.unpack_from("<I", d, o)[0]


def _set_u32(d, o, v):
    struct.pack_into("<I", d, o, v)


def data_directory(pe, index):
    """Returns (rva_or_file_offset, size, field_file_offset) for data
    directory entry `index`. For IMAGE_DIRECTORY_ENTRY_SECURITY the first
    value is a raw file offset, not an RVA -- that is a documented PE
    peculiarity (the certificate table is not mapped into any section), not
    a bug here; see `signature_info`."""
    if index >= pe.number_of_rva_and_sizes:
        return 0, 0, None
    off = pe.data_directory_offset + index * 8
    return _u32(pe.data, off), _u32(pe.data, off + 4), off


def section_for_rva(pe, rva):
    for s in pe.sections:
        size = max(s["virtual_size"], s["size_of_raw_data"])
        if s["virtual_address"] <= rva < s["virtual_address"] + size:
            return s
    raise pd.PEFormatError("RVA 0x%x not covered by any section" % rva)


def signature_info(pe):
    """Authenticode (Security directory) presence, purely by inspection --
    no verification of the signature itself is attempted."""
    file_off, size, _ = data_directory(pe, IMAGE_DIRECTORY_ENTRY_SECURITY)
    present = file_off != 0 and size != 0
    info = {"present": present}
    if present:
        info["file_offset"] = file_off
        info["size"] = size
        info["ends_at_eof"] = (file_off + size == len(pe.data))
    return info


# ==========================================================================
# Locating the single embedded ManifestResource to patch
# ==========================================================================

def locate_single_embedded_resource(dll_bytes):
    """Returns (pe, cor20, row, offset, length, payload_start, payload_end).

    `offset` is the file offset of the resource's 4-byte length prefix;
    `length` is the value currently stored there; payload_start/end bracket
    the JSON bytes that follow it. All four come from pkg_dump's real
    ECMA-335 metadata walk -- nothing here is a hardcoded offset.
    """
    pe = pd.PEImage(dll_bytes)
    cor20 = pe.cor20_header()
    resources_offset, rows = pd.parse_manifest_resources_via_metadata(dll_bytes)

    embedded = [r for r in rows
                if (r.get("Implementation") or {}).get("row_index", 0) == 0]
    if len(embedded) != 1:
        raise PatchNotSupportedError(
            "expected exactly one embedded (null-Implementation) ManifestResource, "
            "found %d of %d total rows -- pkg_patch only supports the single-resource "
            "shape pkg_dump documented for Crestron Legacy/SIMPL driver DLLs" %
            (len(embedded), len(rows)))
    row = embedded[0]

    offset = resources_offset + row["Offset"]
    if offset + 4 > len(dll_bytes):
        raise PatchNotSupportedError("resource %r offset out of range" % row.get("Name"))
    length = _u32(dll_bytes, offset)
    payload_start = offset + 4
    payload_end = payload_start + length
    if payload_end > len(dll_bytes):
        raise PatchNotSupportedError(
            "resource %r length prefix (%d) runs past end of file" % (row.get("Name"), length))
    return pe, cor20, row, offset, length, payload_start, payload_end


# ==========================================================================
# Payload encoding
# ==========================================================================

def _encode_payload(new_json, add_bom):
    """bytes/bytearray input is used verbatim (the caller has full control,
    including BOM); anything else is treated as a JSON-serializable object
    and encoded as pretty-printed UTF-8 with the BOM policy applied."""
    if isinstance(new_json, (bytes, bytearray)):
        return bytes(new_json)
    payload = json.dumps(new_json, indent=2).encode("utf-8")
    has_bom = payload.startswith(BOM)
    if add_bom and not has_bom:
        payload = BOM + payload
    elif not add_bom and has_bom:
        payload = payload[len(BOM):]
    return payload


# ==========================================================================
# Import Directory / thunk-table RVA fixups (growth path only)
# ==========================================================================

def _shift_rva(value, block_lo, block_hi, growth):
    if value != 0 and block_lo <= value < block_hi:
        return value + growth
    return value


def _fix_thunk_chain(data, rva_to_offset, orig_table_rva, new_table_rva,
                      block_lo, block_hi, growth):
    """Walks a 0-terminated array of 4-byte thunk entries (an Import Lookup
    Table or Import Address Table) and shifts any entry that is an RVA
    (high bit clear -- not an ordinal import) pointing inside the moved
    block. `new_table_rva` locates the array's current position: if the
    array itself was inside the moved block its bytes already live there
    verbatim (copied, not yet fixed up), and if it was outside the block
    new_table_rva == orig_table_rva so this is a no-op lookup at the
    original position -- either way the content found there is correct to
    read before this function's own writes."""
    table_off = rva_to_offset(new_table_rva)
    i = 0
    while True:
        entry_off = table_off + i * 4
        entry = struct.unpack_from("<I", data, entry_off)[0]
        if entry == 0:
            break
        if not (entry & 0x80000000):
            new_entry = _shift_rva(entry, block_lo, block_hi, growth)
            if new_entry != entry:
                struct.pack_into("<I", data, entry_off, new_entry)
        i += 1


def _fix_import_directory(data, rva_to_offset, imp_off, imp_size,
                           block_lo, block_hi, growth):
    """Walks the (already-relocated, but content-unmodified) import
    descriptor table at file offset `imp_off`, fixing every RVA it or its
    thunk chains hold that pointed inside the moved block. Bounded by
    `imp_size` so a malformed/unterminated table fails loudly instead of
    reading off the end of the file."""
    off = imp_off
    descriptors = []
    while off - imp_off < imp_size:
        oft, tds, fc, name_rva, fit = struct.unpack_from("<IIIII", data, off)
        if oft == 0 and tds == 0 and fc == 0 and name_rva == 0 and fit == 0:
            break
        descriptors.append(off)
        off += 20
    else:
        raise PatchNotSupportedError(
            "import descriptor table at file offset 0x%x did not terminate with an "
            "all-zero descriptor within its declared size (%d bytes) -- refusing to "
            "guess where it ends" % (imp_off, imp_size))

    for desc_off in descriptors:
        oft, tds, fc, name_rva, fit = struct.unpack_from("<IIIII", data, desc_off)
        new_oft = _shift_rva(oft, block_lo, block_hi, growth)
        new_name = _shift_rva(name_rva, block_lo, block_hi, growth)
        new_fit = _shift_rva(fit, block_lo, block_hi, growth)
        struct.pack_into("<I", data, desc_off, new_oft)        # OriginalFirstThunk
        struct.pack_into("<I", data, desc_off + 12, new_name)  # Name
        struct.pack_into("<I", data, desc_off + 16, new_fit)   # FirstThunk
        if oft:
            _fix_thunk_chain(data, rva_to_offset, oft, new_oft, block_lo, block_hi, growth)
        if fit and fit != oft:
            _fix_thunk_chain(data, rva_to_offset, fit, new_fit, block_lo, block_hi, growth)


# ==========================================================================
# Core patch
# ==========================================================================

class PatchResult:
    def __init__(self, method, old_total, new_total, growth, slack, signature, notes):
        self.method = method                # "same-size" | "shrink" | "growth"
        self.old_total = old_total
        self.new_total = new_total
        self.growth = growth                # new_total - old_total (0 for same-size)
        self.slack = slack                  # available slack at growth time, else None
        self.signature = signature          # dict from signature_info() on the ORIGINAL dll
        self.notes = notes

    def as_dict(self):
        return {
            "method": self.method,
            "old_resource_total": self.old_total,
            "new_resource_total": self.new_total,
            "growth_bytes": self.growth,
            "available_slack": self.slack,
            "signature": self.signature,
            "notes": list(self.notes),
        }


def patch_resource_bytes(dll_bytes, new_json, bom=None):
    """Returns (patched_dll_bytes, PatchResult).

    `bom`: None preserves the original resource's BOM-ness; True/False
    forces one. Ignored when `new_json` is already bytes/bytearray.
    """
    pe, cor20, row, offset, length, payload_start, payload_end = \
        locate_single_embedded_resource(dll_bytes)

    old_payload = dll_bytes[payload_start:payload_end]
    old_had_bom = old_payload.startswith(BOM)
    add_bom = old_had_bom if bom is None else bool(bom)

    new_payload = _encode_payload(new_json, add_bom)
    new_length = len(new_payload)
    old_total = 4 + length
    new_total = 4 + new_length

    sig = signature_info(pe)
    notes = []
    if sig["present"]:
        notes.append(
            "DLL carries an Authenticode signature (Security directory, %d bytes at "
            "file offset 0x%x); this patch changes file content and does NOT re-sign, "
            "so the signature will fail verification against the patched file unless "
            "stripped (strip_signature=True)" % (sig["size"], sig["file_offset"]))
    else:
        notes.append("DLL carries no Authenticode signature")

    data = bytearray(dll_bytes)

    if new_total <= old_total:
        # ---- same-size / shrink: pad in place, nothing after the resource moves ----
        pad = old_total - new_total
        _set_u32(data, offset, new_length)
        data[payload_start:payload_start + new_length] = new_payload
        if pad:
            data[payload_start + new_length:payload_end] = b"\x00" * pad
        _set_u32(data, cor20["file_offset"] + 28, new_total)  # COR20.ResourcesSize
        method = "shrink" if pad else "same-size"
        result = PatchResult(method, old_total, new_total, new_total - old_total,
                              None, sig, notes)
        return bytes(data), result

    # ---- growth: needs the trailing block (metadata root + import directory) ----
    # shifted forward within its section, and every RVA pointing inside it fixed up.
    #
    # The shift MUST be a multiple of 4: the CLI metadata root's internal stream
    # headers pad each stream name to a 4-byte boundary computed relative to the
    # metadata root's own (4-byte-aligned) start, and pkg_dump's reader -- like
    # every real CLI metadata reader -- relies on that alignment holding. Moving
    # the root by a non-multiple-of-4 amount preserves its bytes but breaks that
    # alignment relationship, silently corrupting the stream directory. Verified
    # by direct reproduction against the reference DLL (a 501-byte shift, itself
    # not 4-aligned, made "#Strings" unreadable) before this rounding was added.
    # Any alignment shortfall is absorbed as dead padding after the JSON payload,
    # exactly like the shrink path's trailing pad -- invisible to resource readers,
    # which trust the resource's own length prefix, not where the next thing sits.
    growth = new_total - old_total
    alignment_pad = (-growth) % 4
    shift = growth + alignment_pad
    meta_rva = cor20["metadata_rva"]
    meta_size = cor20["metadata_size"]
    imp_rva, imp_size, imp_dd_off = data_directory(pe, IMAGE_DIRECTORY_ENTRY_IMPORT)

    if imp_rva == 0 or imp_size == 0:
        raise PatchNotSupportedError(
            "growth of %d bytes needs a relocation, and no Import Directory was found "
            "to verify one against -- refusing" % growth)

    meta_off = pe.rva_to_offset(meta_rva)
    imp_off = pe.rva_to_offset(imp_rva)

    if payload_end != meta_off:
        raise PatchNotSupportedError(
            "growth path assumes the resource is immediately followed by the CLI "
            "metadata root (the layout verified against the reference Samsung Serial "
            "DLL); resource ends at file offset 0x%x but metadata starts at 0x%x -- "
            "refusing rather than guessing a relocation" % (payload_end, meta_off))
    if imp_rva != meta_rva + meta_size:
        raise PatchNotSupportedError(
            "growth path assumes the Import Directory immediately follows the CLI "
            "metadata root; metadata ends at RVA 0x%x but the Import Directory starts "
            "at RVA 0x%x -- refusing rather than guessing a relocation" %
            (meta_rva + meta_size, imp_rva))

    sec = section_for_rva(pe, meta_rva)
    if section_for_rva(pe, imp_rva) is not sec:
        raise PatchNotSupportedError(
            "CLI metadata and the Import Directory are not in the same PE section -- "
            "growth-path relocation is not implemented for that layout")

    block_start_off = meta_off
    block_end_off = imp_off + imp_size
    block_start_rva = meta_rva
    block_len = block_end_off - block_start_off
    block_hi_rva = block_start_rva + block_len

    section_raw_end = sec["pointer_to_raw_data"] + sec["size_of_raw_data"]
    available_slack = section_raw_end - block_end_off
    if available_slack < 0:
        raise PkgPatchError(
            "computed negative trailing slack (%d) for section %r -- unexpected layout"
            % (available_slack, sec["name"]))
    if shift > available_slack:
        raise PatchNotSupportedError(
            "growth of %d bytes (%d bytes once rounded up to a 4-byte relocation shift) "
            "exceeds the %d bytes of trailing slack in section %r (0x%x..0x%x, after the "
            "metadata root + import directory that follow the resource); moving or "
            "resizing a later PE section (.rsrc/.reloc) is not implemented here -- "
            "refusing rather than emitting a corrupt image" %
            (growth, shift, available_slack, sec["name"], block_end_off, section_raw_end))

    # 1. capture the block verbatim BEFORE the payload write can clobber its start.
    block_bytes = bytes(data[block_start_off:block_end_off])

    # 2. write the grown resource, then `alignment_pad` zero bytes of dead space
    #    (part of neither the resource -- whose length prefix says `new_length`,
    #    not `new_length + alignment_pad` -- nor the block) so the block's new
    #    start is `shift` bytes on, not just `growth` bytes on.
    _set_u32(data, offset, new_length)
    data[payload_start:payload_start + new_length] = new_payload
    if alignment_pad:
        pad_start = payload_start + new_length
        data[pad_start:pad_start + alignment_pad] = b"\x00" * alignment_pad
    new_block_start_off = payload_start + new_length + alignment_pad
    assert new_block_start_off == block_start_off + shift
    assert new_block_start_off % 4 == block_start_off % 4

    # 3. re-place the (still content-unmodified) block at its new position, and
    #    zero-fill whatever slack remains after it so the section's raw size is
    #    unchanged and untouched bytes read as zero rather than stale garbage.
    data[new_block_start_off:new_block_start_off + block_len] = block_bytes
    tail_start = new_block_start_off + block_len
    if tail_start < section_raw_end:
        data[tail_start:section_raw_end] = b"\x00" * (section_raw_end - tail_start)

    # 4. fix every RVA/size field that depended on the block's old position.
    _set_u32(data, cor20["file_offset"] + 8, meta_rva + shift)   # COR20.MetaData RVA
    _set_u32(data, imp_dd_off, imp_rva + shift)                  # Import directory RVA
    _set_u32(data, cor20["file_offset"] + 28, new_total)         # COR20.ResourcesSize

    new_imp_off = imp_off + shift
    _fix_import_directory(data, pe.rva_to_offset, new_imp_off, imp_size,
                           block_start_rva, block_hi_rva, shift)

    notes.append(
        "grew resource by %d bytes (%d bytes of 4-byte alignment padding added, for a "
        "%d-byte relocation shift); shifted CLI metadata root + Import Directory "
        "(section %r) forward by the shift amount, using %d of %d bytes of trailing "
        "slack; fixed COR20 MetaData RVA, Import Directory RVA, import descriptor "
        "OriginalFirstThunk/Name/FirstThunk, and their ILT/IAT thunk-chain entries" %
        (growth, alignment_pad, shift, sec["name"], shift, available_slack))

    result = PatchResult("growth", old_total, new_total, growth, available_slack, sig, notes)
    return bytes(data), result


def _strip_authenticode(dll_bytes):
    """Removes the Security directory entry and its trailing certificate
    bytes outright. Produces an honestly-unsigned file; never produces a
    new signature (re-signing is out of scope)."""
    pe = pd.PEImage(dll_bytes)
    file_off, size, dd_off = data_directory(pe, IMAGE_DIRECTORY_ENTRY_SECURITY)
    if file_off == 0 or size == 0:
        return dll_bytes, "no Authenticode signature present; nothing to strip"
    if file_off + size != len(dll_bytes):
        raise PatchNotSupportedError(
            "Security directory (file offset 0x%x, size %d) does not end at EOF "
            "(file size %d) -- refusing to guess what else follows it" %
            (file_off, size, len(dll_bytes)))
    data = bytearray(dll_bytes)
    struct.pack_into("<II", data, dd_off, 0, 0)
    del data[file_off:]
    return bytes(data), ("stripped %d bytes of Authenticode certificate data at file "
                          "offset 0x%x" % (size, file_off))


# ==========================================================================
# .pkg (ZIP) level
# ==========================================================================

def patch_pkg(pkg_path, new_json, out_path, bom=None, strip_signature=False):
    """Reads `pkg_path`, replaces its DLL's embedded driver-definition
    resource with `new_json`, and writes `out_path`. Every other ZIP member
    is carried over with identical content and metadata (compression type,
    date, external/internal attributes) -- only the DLL's bytes differ.

    Returns the PatchResult (as_dict()-able) describing what was done.
    """
    with zipfile.ZipFile(pkg_path) as z:
        infos = z.infolist()
        dll_infos = [i for i in infos if i.filename.lower().endswith(".dll")]
        if len(dll_infos) != 1:
            raise PkgPatchError(
                "%s: expected exactly one .dll member, found %d" %
                (pkg_path, len(dll_infos)))
        dll_info = dll_infos[0]
        member_bytes = {i.filename: z.read(i.filename) for i in infos}

    patched_dll, result = patch_resource_bytes(member_bytes[dll_info.filename], new_json, bom=bom)
    if strip_signature:
        patched_dll, strip_note = _strip_authenticode(patched_dll)
        result.notes.append(strip_note)
    member_bytes[dll_info.filename] = patched_dll

    with zipfile.ZipFile(pkg_path) as zin, zipfile.ZipFile(out_path, "w") as zout:
        for info in zin.infolist():
            new_info = zipfile.ZipInfo(info.filename, date_time=info.date_time)
            new_info.compress_type = info.compress_type
            new_info.external_attr = info.external_attr
            new_info.internal_attr = info.internal_attr
            new_info.create_system = info.create_system
            new_info.create_version = info.create_version
            new_info.extract_version = info.extract_version
            new_info.flag_bits = info.flag_bits
            zout.writestr(new_info, member_bytes[info.filename])

    return result


# ==========================================================================
# CLI
# ==========================================================================

def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pkg", help="input .pkg file")
    ap.add_argument("-o", "--output", required=True, help="output .pkg path")
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--json-file",
                        help="path to a JSON file to replace the driver definition with")
    group.add_argument("--same", action="store_true",
                        help="identity round-trip: re-encode the .pkg's own current "
                             "driver definition unchanged")
    ap.add_argument("--strip-signature", action="store_true",
                     help="remove the Authenticode Security directory and its trailing "
                          "certificate bytes instead of leaving a now-invalid signature "
                          "in place; never produces a new signature")
    args = ap.parse_args()

    if args.same:
        doc = pd.process_pkg(args.pkg)
        if doc["driver_definition"] is None:
            print("error: %s has no embedded driver-definition JSON to round-trip" % args.pkg,
                  file=sys.stderr)
            return 1
        new_json = doc["driver_definition"]
    else:
        with open(args.json_file, "r", encoding="utf-8") as f:
            new_json = json.load(f)

    try:
        result = patch_pkg(args.pkg, new_json, args.output, strip_signature=args.strip_signature)
    except PkgPatchError as e:
        print("error: %s" % e, file=sys.stderr)
        return 1

    print(json.dumps(result.as_dict(), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
