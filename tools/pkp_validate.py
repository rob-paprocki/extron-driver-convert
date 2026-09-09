#!/usr/bin/env python3
"""
pkp_validate.py - a pure-Python reimplementation of Extron's
`Extron.Configuration.Drivers.DriverAssetValidator.Validate(IDriverFileAsset)`.

Why this exists
---------------
Global Configurator validates a `.pkp` before it will let you select the
driver, and refuses it with a modal reading

    Invalid Driver ... Error Code: 80085

Finding 15 hit exactly that on hardware. Until now the only way to ask "would
GC accept this package?" was to install GC - which is Windows-only, licensed,
and (on this project's box) time-limited. This module answers the same question
from the object graph alone, standard library only, anywhere Python 3 runs.

It is a reimplementation, not a wrapper: parsing is delegated to
`tools/pkp_dump.py` (the repo's one NRBF reader), and everything above that is
this file.

What Extron's method does (three independent IL decodes agreed on this core)
---------------------------------------------------------------------------
    ErrorCode Validate(IDriverFileAsset a):
        if a == null: throw NullReferenceException("DriverFileAsset cannot be null.")
        if a.Filename.EndsWith("eir", InvariantCultureIgnoreCase): return Valid
        foreach (IResourceAsset r in a.Manifest):
            byte[] h = r.GetContentHashCode()        # SHA-256 over (r.Content as byte[])
            if a.ResourceHashDict.ContainsKey(r.Key):
                if SequenceEqual(a.ResourceHashDict[r.Key], h): continue
                return MismatchHash                  # 80085
            elif THIS.a.ContainsKey(r.Guid):         # ExtronDH.dat, Guid-keyed
                if SequenceEqual(THIS.a[r.Guid], h): continue
                return MismatchHash                  # 80085
            else:
                return NoHash_NoGuid                 # 80086
        return Valid

Points every decode agreed on, and this file implements verbatim:
  * The digest is plain SHA-256 over the resource's raw bytes. No salt, no
    length prefix. (Independently confirmed here against the stored digests of
    all nine sample packages, `.py` and `.pdf` alike.)
  * EVERY manifest resource is hashed. There is no per-resource extension
    filter. The single `EndsWith` in the method is applied once, before the
    loop, to the PACKAGE filename.
  * The primary lookup is by the resource's string Key; the Guid lookup is
    only a fallback for keys the package itself does not list.
  * The first failing resource wins and returns immediately.
  * `Manifest` is NOT the serialized `_manifest` field (null in every shipping
    package). It is the CHILD ASSET named "Manifest" on the root, reached
    through the root's `_internalChildCollection`. Measured on all nine
    samples; `_manifest` is null in all nine.

THE COMM-SHEET PDF (the open question in the brief): it is EMBEDDED, not
external. Every sample package's Manifest holds StreamResourceAssets whose
`ResourceAssetBase+_content` is an NRBF byte array, for the `.pdf` exactly as
for the `.py`, and sha256(those bytes) equals the stored digest in all nine.
So the PDF's hash IS checkable from the object graph, and a stale PDF digest
fails with 80085 exactly as a stale script digest does. This file hashes it.
Where a resource's content is NOT an embedded byte array we do not pretend it
passed - see UNVERIFIABLE below.

=============================================================================
WHERE THE THREE DECODES DISAGREE, OR FLAGGED AN UNCERTAINTY
=============================================================================
The repo's standing rule is that a plausible guess is worse than a recorded
gap. Each item below is a gap, what this file does about it, and what would
close it.

(1) IS THE GUID FALLBACK TABLE EVEN POPULATED WHEN GC CALLS Validate?
    Decode 1: inferred non-empty (GCP.exe carries MemberRefs to
      LoadDefaultFromResource, but no IL use-site was recovered).
    Decode 2: if the caller never loaded it, the field is null and
      `this.a.ContainsKey(...)` throws NullReferenceException rather than
      returning 80086.
    Decode 3: measured that `LoadDefaultFromResource` is called from exactly
      one place (GCPro.Services.DriverValidationService..ctor), and that NONE
      of the sampled resource GUIDs appear among ExtronDH.dat's 4,775 entries.
      It also could not confirm that a DriverValidationService is constructed
      on every path that reaches Validate.
    NOT RESOLVED. This repo does not ship ExtronDH.dat (it is an embedded
    resource of a licensed assembly), so we cannot consult the real table.
    WHAT THIS FILE DOES: the table is a caller-supplied parameter,
    `guid_hash_table`, defaulting to EMPTY. With it empty, a resource whose Key
    is absent from the package's own dict yields NoHash_NoGuid (80086) - which
    is what decode 3's measurement predicts for any modern package - and the
    Result records `guid_table_consulted=False` plus a warning, so a 80086 from
    this tool is never silently equated with a 80086 from GC. Pass a real table
    (guid string -> 32 raw bytes) to close the gap for a given package.

(2) WHICH `Filename` DOES THE "eir" BYPASS TEST?
    All three decodes agree the literal is the bare 3 characters "eir" (no
    leading dot) compared with InvariantCultureIgnoreCase against
    `IDriverDescriptorAsset.Filename` - i.e. any name whose last three
    characters are e,i,r bypasses hashing entirely.
    They disagree on what that Filename holds at validation time:
    Decode 1: the `.pkp` loader overwrites it with `Path.GetFileName(...)`, so
      it is the ON-DISK name; but decode 1 did not verify every load path
      (CachedDriverFileAsset, GC's 61 MB rehydrated catalogue).
    Decodes 2 and 3: the SERIALIZED `_filename` in the samples is often the
      authoring absolute path (e.g. 'C:\\Users\\billywong\\...\\x.pkp'), and no
      decode observed a real `.eir` asset flowing through Validate.
    NOT RESOLVED. WHAT THIS FILE DOES: it evaluates the test against BOTH
    candidates - the serialized `_filename` and the on-disk filename - and only
    takes the bypass when they AGREE. If exactly one ends in "eir" the result
    is ambiguous, so this file does NOT take the bypass; it hashes the
    resources and reports the real hash outcome, with a warning saying GC may
    return Valid regardless. (For all nine samples both candidates end in
    "pkp", so the bypass does not fire either way and the point is moot.)
    Note what this implies: nothing here treats a name ending in "eir" as
    trustworthy. An attacker-controlled `_filename` ending in "eir" is a
    validation bypass in GC; here it is a warning, never a silent pass.

(3) A RESOURCE WHOSE CONTENT IS NOT A byte[].
    All three decodes agree on the mechanism and none observed it:
    `GetContentHashCode()` returns null, and Validate passes null into
    `Enumerable.SequenceEqual`, which throws ArgumentNullException. Validate
    has a finally but no catch, so it propagates - GC returns NO ErrorCode at
    all. There is therefore no honest Extron code to report.
    WHAT THIS FILE DOES: reports the repo-local sentinel UNVERIFIABLE (-1),
    explicitly documented as NOT an Extron code, and names the resource. This
    is also the branch that would fire if a `.pdf` ever turned out to be
    referenced rather than embedded.

(4) A PACKAGE WITH NO "Manifest" CHILD ASSET.
    Decodes 2 and 3 read `get_Manifest()` as auto-creating an empty
    `AssetBase<IResourceAsset>("Manifest")` when the child is absent, so the
    loop runs zero times and Validate returns Valid. Neither executed it;
    decode 1 did not decode the getter at all and relied on the object graph.
    WHAT THIS FILE DOES: follows the majority reading for `.code` (Valid,
    because zero resources failed) but records a warning and leaves
    `verified` False, because a Valid that verified nothing is not the same
    claim as a Valid that checked every resource. The CLI exits non-zero for
    it. All nine samples have exactly one Manifest child, so this path is
    untested against a real file.

(5) `AssetBase.get_Item(string)` NAME MATCHING.
    No decode read the getter's IL. Assets carry both `AssetBase+_name` and
    `AssetBase+_defaultName`; in all nine samples the Manifest child has
    _name == "Manifest". This file matches on _name, falling back to
    _defaultName when _name is null, and treats more than one "Manifest" child
    as an unresolved ambiguity (warning + hash them all) rather than picking.

(6) DOES `get_Manifest()` FILTER OR SYNTHESISE ENTRIES?
    Decode 1 explicitly declined to decode the getter's body (a LINQ
    projection) and relied on the object graph; decodes 2 and 3 read it as a
    plain child lookup. If the getter ever filtered, the hashed set here would
    be a superset of GC's - which fails safe (we would report a mismatch GC
    ignores), never the reverse. Recorded, not resolved.

(7) EXTRA ENTRIES IN ResourceHashDict THAT NO MANIFEST RESOURCE CLAIMS.
    All decodes agree Validate iterates RESOURCES, not dict entries, so orphan
    dict keys can never cause a failure. This file matches that, and reports
    orphans as informational detail only - never as a failure.

(8) A CORROBORATION, NOT A GAP: decodes disagreed on whether the .pdf hash was
    checkable from the object graph (the brief said it was not). Measurement in
    this repo settles it - it is, see above. Recorded because the brief asked
    for it explicitly.

=============================================================================
Public API
=============================================================================
    validate(path_or_bytes, guid_hash_table=None, on_disk_name=None) -> Result
    validate_graph(objects, root, ...) -> Result      # same, over a parsed graph
    load_graph(path_or_bytes) -> (objects, root)      # raises PackageError

    Result.code       int   0 / 80085 / 80086, or a repo-local sentinel < 0
    Result.name       str   "Valid" / "MismatchHash" / "NoHash_NoGuid" / ...
    Result.details    list of str, one line per resource plus any notes
    Result.resources  list of ResourceReport
    Result.warnings   list of str - everything we could NOT establish
    Result.verified   bool  True only if every manifest resource was hashed
    Result.ok         bool  code == Valid and verified and no warnings

CLI:
    python tools/pkp_validate.py FILE...        # one line per package
    python tools/pkp_validate.py -v FILE...     # plus a line per resource
    exit 0 only if every package is Result.ok.
"""

import argparse
import gzip
import hashlib
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import pkp_dump as pd            # noqa: E402  (the repo's only NRBF reader)


# --------------------------------------------------------------------------
# Extron's enum, mirrored exactly.
# Extron.Configuration.Drivers.DriverAssetValidator+ErrorCode
# --------------------------------------------------------------------------
VALID = 0
MISMATCH_HASH = 80085
NO_HASH_NO_GUID = 80086

# Repo-local sentinels. These are NOT Extron codes and will never be returned
# by GC; they exist so this tool can say "I could not establish that" instead
# of guessing a code. Negative, so they can never collide with the enum.
UNVERIFIABLE = -1     # a resource could not be hashed at all (see gap 3)
UNPARSEABLE = -2      # the input is not a readable .pkp

CODE_NAMES = {
    VALID: "Valid",
    MISMATCH_HASH: "MismatchHash",
    NO_HASH_NO_GUID: "NoHash_NoGuid",
    UNVERIFIABLE: "Unverifiable",
    UNPARSEABLE: "Unparseable",
}

DRIVER_FILE_ASSET_CLASS = "Extron.Configuration.Drivers.DriverFileAsset"
MANIFEST_CHILD_NAME = "Manifest"


class PackageError(Exception):
    """The input could not be read as a .pkp object graph."""


# --------------------------------------------------------------------------
# graph helpers - thin, tolerant readers over PkpParser.objects
# --------------------------------------------------------------------------
def deref(objects, ref, _depth=0):
    """Follow {'$ref': id} chains. Returns None for a dangling reference."""
    while isinstance(ref, dict) and set(ref.keys()) == {"$ref"}:
        if _depth > 64:
            return None
        ref = objects.get(ref["$ref"])
        _depth += 1
    return ref


def member(objects, obj, *names):
    """First non-None member of `obj` among `names`, dereferenced.

    Members are name-mangled by declaring type when a field is shadowed
    ('AssetBase+_guid' vs '_guid'), and which spelling is populated varies
    between assets (the root carries three aliases of the child collection, the
    Manifest asset only one), so callers pass every spelling they accept.
    """
    if not isinstance(obj, dict):
        return None
    members = obj.get("members") or {}
    for n in names:
        if n in members:
            v = deref(objects, members[n])
            if v is not None:
                return v
    # suffix match, for a mangling prefix we have not seen spelled out
    for n in names:
        for k in members:
            if k.endswith("+" + n):
                v = deref(objects, members[k])
                if v is not None:
                    return v
    return None


def byte_array(value):
    """The raw bytes behind an NRBF ArraySinglePrimitive of Byte, else None.

    Returning None is meaningful: it is exactly the condition under which
    .NET's `Content as byte[]` yields null (gap 3).
    """
    if not isinstance(value, dict):
        return None
    if value.get("$type") != "ArraySinglePrimitive":
        return None
    if value.get("primitive_type") not in ("Byte", 2):
        return None
    try:
        return bytes(value.get("items") or [])
    except (TypeError, ValueError):
        return None


def asset_name(objects, asset):
    """AssetBase.Name, with the documented _name -> _defaultName fallback (gap 5)."""
    n = member(objects, asset, "AssetBase+_name", "_name")
    if isinstance(n, str) and n:
        return n
    n = member(objects, asset, "AssetBase+_defaultName", "_defaultName")
    return n if isinstance(n, str) else None


def guid_string(objects, value):
    """System.Guid -> canonical 'D' format, or None.

    .NET lays Guid out as int _a, short _b, short _c, byte _d.._k; ToString("D")
    prints a-b-c-de-fghijk. Values arrive signed from the NRBF reader, so mask.
    """
    g = deref(objects, value)
    if not (isinstance(g, dict) and str(g.get("class", "")).endswith("System.Guid")):
        return None
    m = g.get("members") or {}
    try:
        a = int(m["_a"]) & 0xFFFFFFFF
        b = int(m["_b"]) & 0xFFFF
        c = int(m["_c"]) & 0xFFFF
        rest = [int(m["_" + ch]) & 0xFF for ch in "defghijk"]
    except (KeyError, TypeError, ValueError):
        return None
    return "%08x-%04x-%04x-%02x%02x-%s" % (
        a, b, c, rest[0], rest[1], "".join("%02x" % x for x in rest[2:]))


def child_assets(objects, asset):
    """The children of an AssetBase, honouring List`1's _size.

    The chain is  asset._internalChildCollection (ObservableCollection`1)
                  -> 'Collection`1+items' (List`1)
                  -> List._items (an array whose tail past _size is null).
    Reading the raw array instead of _size hands back trailing nulls, which is
    how a 7-child asset looks like an 8-child one.
    """
    coll = member(objects, asset,
                  "AssetBase+_internalChildCollection", "_internalChildCollection")
    if not isinstance(coll, dict):
        return []
    lst = None
    for k in (coll.get("members") or {}):
        if k.endswith("items"):
            lst = deref(objects, coll["members"][k])
            break
    if not isinstance(lst, dict):
        return []
    lm = lst.get("members") or {}
    arr = deref(objects, lm.get("_items"))
    size = lm.get("_size")
    if not isinstance(arr, dict):
        return []
    items = arr.get("items") or []
    if isinstance(size, int) and 0 <= size <= len(items):
        items = items[:size]
    return [deref(objects, it) for it in items]


def resource_hash_dict(objects, root):
    """`DriverFileAsset._resourceHashDict` as {key: 32-byte digest}.

    Shape is Dictionary<string, byte[]>: {Version, Comparer, HashSize,
    KeyValuePairs}, KeyValuePairs being a BinaryArray of
    KeyValuePair<string,byte[]> with members 'key' and 'value'.

    A null field is NOT an error: `get_ResourceHashDict()` lazily creates an
    empty dictionary, so a package with no dict at all forces every resource
    down the Guid-fallback branch rather than throwing.
    """
    d = member(objects, root, "_resourceHashDict")
    if not isinstance(d, dict):
        return {}
    kvps = member(objects, d, "KeyValuePairs")
    out = {}
    for item in ((kvps or {}).get("items") or []):
        entry = deref(objects, item)
        if not isinstance(entry, dict):
            continue
        em = entry.get("members") or {}
        key = deref(objects, em.get("key"))
        val = byte_array(deref(objects, em.get("value")))
        if isinstance(key, str) and val is not None:
            out[key] = val
    return out


# --------------------------------------------------------------------------
# the package, as Validate sees it
# --------------------------------------------------------------------------
class ResourceReport(object):
    """One manifest resource and what happened to it."""

    def __init__(self, key, guid, size, computed, stored, source, code, note):
        self.key = key            # IResourceAsset.Key (the string filename)
        self.guid = guid          # IAsset.Guid, canonical string
        self.size = size          # embedded byte count, or None
        self.computed = computed  # sha256 of the embedded bytes, or None
        self.stored = stored      # the digest we compared against, or None
        self.source = source      # 'key' | 'guid' | None - which table answered
        self.code = code          # per-resource outcome
        self.note = note

    def __repr__(self):
        return "ResourceReport(%r, %s)" % (
            self.key, CODE_NAMES.get(self.code, self.code))

    def line(self):
        return "  %-13s %-34s %s" % (
            CODE_NAMES.get(self.code, self.code), self.key or "<no key>", self.note)


class Result(object):
    def __init__(self, code, path=None):
        self.code = code
        self.path = path
        self.details = []
        self.warnings = []
        self.resources = []
        self.filename = None            # serialized DriverDescriptorAsset+_filename
        self.on_disk_name = None
        self.bypassed = False           # the "eir" short circuit fired
        self.verified = False           # every manifest resource was actually hashed
        self.guid_table_consulted = False

    @property
    def name(self):
        return CODE_NAMES.get(self.code, "Code_%s" % (self.code,))

    @property
    def ok(self):
        """Valid AND we actually checked something AND nothing was unclear."""
        return self.code == VALID and self.verified and not self.warnings

    def __repr__(self):
        return "Result(%s, %d resources, %d warnings)" % (
            self.name, len(self.resources), len(self.warnings))

    def report(self, verbose=False):
        lines = ["%-13s %-6s %s" % (self.name, self.code, self.path or "<bytes>")]
        if verbose:
            lines += ["  " + d for d in self.details]
        lines += ["  WARN: " + w for w in self.warnings]
        return "\n".join(lines)


def _package_bytes(path_or_bytes):
    if isinstance(path_or_bytes, (bytes, bytearray)):
        data = bytes(path_or_bytes)
        if data[:2] == b"\x1f\x8b":
            try:
                return gzip.decompress(data)
            except Exception as e:
                raise PackageError("gzip container is corrupt: %s: %s"
                                   % (type(e).__name__, e))
        return data
    try:
        return pd.load_bytes(path_or_bytes)
    except Exception as e:
        raise PackageError("cannot read %s: %s: %s"
                           % (path_or_bytes, type(e).__name__, e))


def load_graph(path_or_bytes):
    """(objects, root) for a package. Raises PackageError on anything unreadable.

    A truncated stream shows up two ways and both are refused: PkpParser raises
    NrbfParseError mid-record, or it stops cleanly having never seen the
    MessageEnd record. Silently validating the prefix of a truncated package is
    exactly the failure this guards against.
    """
    data = _package_bytes(path_or_bytes)
    if not data:
        raise PackageError("empty input")
    parser = pd.PkpParser(data)
    try:
        parser.parse()
    except pd.NrbfParseError as e:
        raise PackageError("not a readable NRBF stream: %s" % (e,))
    except Exception as e:                # a wrong-format file can fail anywhere
        raise PackageError("not a readable NRBF stream: %s: %s"
                           % (type(e).__name__, e))
    if not parser.message_end_seen:
        raise PackageError(
            "stream ended without an NRBF MessageEnd record after %d of %d bytes "
            "- truncated, or not a .pkp" % (parser.r.tell(), len(data)))
    root = parser.objects.get(parser.root_id)
    if not isinstance(root, dict) or "members" not in root:
        raise PackageError("no root object (root_id=%r)" % (parser.root_id,))
    if root.get("class") != DRIVER_FILE_ASSET_CLASS:
        raise PackageError("root is %r, not %s"
                           % (root.get("class"), DRIVER_FILE_ASSET_CLASS))
    return parser.objects, root


def manifest_resources(objects, root):
    """(resources, warnings) - the package's manifest resources, enumerated.

    TWO schemas, and the earlier one is the reverse of the later one.

    Packages built against `Extron.Configuration.Contracts` 13.26.0.15 (1,863 of
    1,866 measured) serialize `_manifest` as null and carry the manifest as a
    CHILD ASSET named "Manifest".

    Packages built against Contracts **1.0.0.0** do the opposite: the serialized
    `_manifest` field HOLDS the manifest and there is no "Manifest" child. Three
    shipping packages are like this - `extr_10_397_v1_0_4`, `extr_1_789_v1_0_2`,
    `extr_8_89_v1_0_0`, all old Extron first-party drivers.

    An earlier revision checked only the child and returned `Valid` with ZERO
    resources verified for those three - reporting success because it had not
    looked. Differential testing against Extron's own validator caught it; the
    126-case local suite did not, because the suite had no pre-13.x package in
    it. Hence: resolve `_manifest` FIRST, and never return an empty resource
    list without saying so.
    """
    warnings = []

    direct = deref(objects, (root.get("members") or {}).get("_manifest"))
    if isinstance(direct, dict):
        resources = [c for c in child_assets(objects, direct) if isinstance(c, dict)]
        if resources:
            return resources, warnings
        warnings.append(
            "the serialized _manifest holds an asset but enumerates no resources")

    matches = [c for c in child_assets(objects, root)
               if isinstance(c, dict) and asset_name(objects, c) == MANIFEST_CHILD_NAME]
    if not matches:
        warnings.append(
            "no manifest found: neither the serialized _manifest field nor a child "
            "asset named %r yielded resources, so NOTHING in this package was "
            "verified. Treat a Valid verdict here as 'not checked', not 'checked "
            "and passed'." % MANIFEST_CHILD_NAME)
        return [], warnings
    if len(matches) > 1:
        warnings.append(
            "%d child assets are named %r; AssetBase.get_Item picks one by a rule we "
            "did not decode (gap 5), so which resources GC hashes is undetermined. "
            "All of them were hashed here." % (len(matches), MANIFEST_CHILD_NAME))
    resources = []
    for m in matches:
        resources.extend(c for c in child_assets(objects, m) if isinstance(c, dict))
    return resources, warnings


def _ends_with_eir(name):
    """Extron's test: EndsWith("eir", InvariantCultureIgnoreCase). Bare 3 chars."""
    return isinstance(name, str) and name[-3:].lower() == "eir"


# --------------------------------------------------------------------------
# the validator
# --------------------------------------------------------------------------
def validate(path_or_bytes, guid_hash_table=None, on_disk_name=None):
    """Reimplementation of DriverAssetValidator.Validate. Returns a Result.

    guid_hash_table: {guid string: 32 raw bytes}, standing in for the
        validator's ExtronDH.dat table. Defaults to empty - see gap 1. When it
        is empty and a resource key is missing from the package's own dict, the
        80086 reported here is a prediction, flagged as such in warnings.
    on_disk_name: the filename GC would see on disk. Defaults to the basename
        of `path_or_bytes` when a path was given. Used only for the "eir"
        bypass test - see gap 2.
    """
    path = None if isinstance(path_or_bytes, (bytes, bytearray)) else path_or_bytes
    path = str(path) if path is not None else None

    try:
        objects, root = load_graph(path_or_bytes)
    except PackageError as e:
        result = Result(UNPARSEABLE, path=path)
        result.details.append(str(e))
        result.warnings.append(str(e))
        return result

    return validate_graph(objects, root, guid_hash_table=guid_hash_table,
                          on_disk_name=on_disk_name, path=path)


def validate_graph(objects, root, guid_hash_table=None, on_disk_name=None, path=None):
    """The validator proper, over an already-parsed graph.

    Split out from `validate` so callers (and tests) can drive branches that no
    shipping package exercises - an absent `_resourceHashDict`, a populated
    Guid table - without having to synthesise an NRBF stream for each one.
    """
    result = Result(VALID, path=path)
    guid_hash_table = dict(guid_hash_table or {})
    result.guid_table_consulted = bool(guid_hash_table)
    if on_disk_name is None and path is not None:
        on_disk_name = os.path.basename(str(path))
    result.on_disk_name = on_disk_name

    stored_filename = member(objects, root,
                             "DriverDescriptorAsset+_filename", "_filename")
    result.filename = stored_filename if isinstance(stored_filename, str) else None

    # -- the "eir" bypass. Keyed SOLELY on the on-disk name (gap 2, now measured)
    #
    # `DriverFileAsset.LoadFromFile` overwrites `Filename` with
    # `Path.GetFileName(fi.FullName)`, so the name Validate tests is the one on
    # disk and the serialized `_filename` has no effect whatsoever. Both halves
    # were measured against Extron's validator:
    #   - a package with a corrupted digest renamed to `.eir` on disk  -> Valid
    #     (8 such mutants, including `.EIR` and `.EiR`)
    #   - a `.pkp` whose serialized `_filename` was rewritten to end in `.eir`,
    #     digest corrupted                                             -> 80085
    # An earlier revision required BOTH names to agree, which was wrong in the
    # unsafe direction (missing the real bypass) and the safe one.
    #
    # In practice the reach is bounded: LoadFromFile accepts only `.pkp` and
    # `.eir` (case-insensitive) and returns null otherwise, so `foo.weir` or a
    # bare `xxxeir` never reaches Validate at all - measured, three such files
    # byte-identical to a loading `.EIR` were refused at load.
    if _ends_with_eir(on_disk_name):
        result.bypassed = True
        result.code = VALID
        result.verified = False
        result.details.append(
            "on-disk filename %r ends in 'eir': Extron returns Valid without "
            "hashing anything." % on_disk_name)
        result.warnings.append(
            "IR bypass taken: NOTHING in this package was hash-checked. GC exempts "
            "any package whose on-disk name ends in the three characters 'eir', "
            "regardless of content. Measured against Extron's own validator.")
        return result
    if _ends_with_eir(result.filename):
        result.details.append(
            "serialized _filename %r ends in 'eir' but the on-disk name does not; "
            "LoadFromFile overwrites Filename, so this does NOT bypass validation "
            "(measured)." % result.filename)

    hashes = resource_hash_dict(objects, root)
    if not hashes:
        result.details.append(
            "_resourceHashDict is empty or absent; get_ResourceHashDict() lazily "
            "creates an empty dictionary, so every resource falls to the Guid table.")

    resources, mwarn = manifest_resources(objects, root)
    result.warnings.extend(mwarn)

    seen_keys = set()
    first_failure = None

    for res in resources:
        rm = res.get("members") or {}
        key = member(objects, res, "ResourceAssetBase+_key", "_key")
        key = key if isinstance(key, str) else None
        guid = (guid_string(objects, rm.get("AssetBase+_guid"))
                or guid_string(objects, rm.get("_guid")))
        content = member(objects, res, "ResourceAssetBase+_content", "_content")
        raw = byte_array(content)
        if key is not None:
            seen_keys.add(key)

        if raw is None:
            # gap 3: GetContentHashCode() returns null, SequenceEqual throws.
            rep = ResourceReport(
                key, guid, None, None, None, None, UNVERIFIABLE,
                "content is not an embedded byte array - cannot hash it. Extron's "
                "GetContentHashCode() would return null here and Validate would "
                "throw ArgumentNullException out of SequenceEqual rather than "
                "return any ErrorCode (gap 3).")
            result.resources.append(rep)
            result.warnings.append(
                "resource %r carries no embedded bytes, so its digest could not be "
                "checked at all (gap 3)." % (key,))
            if first_failure is None:
                first_failure = rep
            continue

        computed = hashlib.sha256(raw).digest()

        if key is not None and key in hashes:
            stored = hashes[key]
            if stored == computed:
                rep = ResourceReport(key, guid, len(raw), computed, stored, "key",
                                     VALID,
                                     "sha256 matches the package's stored digest")
            else:
                rep = ResourceReport(
                    key, guid, len(raw), computed, stored, "key", MISMATCH_HASH,
                    "stored %s != actual %s"
                    % (stored.hex()[:16], computed.hex()[:16]))
        elif guid is not None and guid in guid_hash_table:
            stored = guid_hash_table[guid]
            if stored == computed:
                rep = ResourceReport(key, guid, len(raw), computed, stored, "guid",
                                     VALID, "sha256 matches the supplied Guid table")
            else:
                rep = ResourceReport(
                    key, guid, len(raw), computed, stored, "guid", MISMATCH_HASH,
                    "Guid-table digest %s != actual %s"
                    % (stored.hex()[:16], computed.hex()[:16]))
        else:
            rep = ResourceReport(
                key, guid, len(raw), computed, None, None, NO_HASH_NO_GUID,
                "no entry under key %r%s"
                % (key, "" if result.guid_table_consulted
                   else " and no Guid table was supplied (gap 1)"))
            if not result.guid_table_consulted:
                result.warnings.append(
                    "resource %r is missing from _resourceHashDict and no ExtronDH.dat "
                    "Guid table was supplied, so 80086 here is a prediction, not a "
                    "measurement of what GC would do (gap 1)." % (key,))

        result.resources.append(rep)
        if rep.code != VALID and first_failure is None:
            first_failure = rep

    # Extron returns at the FIRST failing resource; later ones are never
    # examined. We hash everything (more useful) but take the reported code
    # from the first failure, so the code we report is the code GC would.
    if first_failure is not None:
        result.code = first_failure.code
        result.details.insert(0, "first failing resource: %r - %s"
                              % (first_failure.key, first_failure.note))
    else:
        result.code = VALID

    result.verified = bool(result.resources) and all(
        r.computed is not None for r in result.resources)
    if not resources and not mwarn:
        result.warnings.append(
            "the Manifest child asset has no resources: Validate's loop runs zero "
            "times and returns Valid having hashed nothing.")

    orphans = sorted(set(hashes) - seen_keys)
    if orphans:
        result.details.append(
            "_resourceHashDict lists %d key(s) no manifest resource claims: %s. "
            "Validate iterates resources, not dict entries, so these are inert "
            "(gap 7)." % (len(orphans), ", ".join(orphans)))

    for r in result.resources:
        result.details.append(r.line().strip())
    return result


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Validate Extron .pkp packages the way Global Configurator "
                    "does, without Global Configurator.",
        epilog="Exit status is 0 only if every package is Valid AND every "
               "resource was actually hash-checked.")
    ap.add_argument("files", nargs="+", metavar="FILE", help=".pkp package(s)")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print a line per resource")
    args = ap.parse_args(argv)

    bad = 0
    for f in args.files:
        r = validate(f)
        print(r.report(verbose=args.verbose))
        if not r.ok:
            bad += 1
    if len(args.files) > 1:
        print("%d/%d package(s) valid and fully verified"
              % (len(args.files) - bad, len(args.files)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
