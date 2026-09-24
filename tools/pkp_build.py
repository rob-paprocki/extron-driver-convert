#!/usr/bin/env python3
"""
pkp_build.py - build a new Extron .pkp by transplanting content into a real
donor package.

Why a transplant and not a from-scratch object graph
----------------------------------------------------
Finding 12 measured that Global Configurator ingests a package produced by
our NRBF writer, including a mutated one - but every package tested there
descended from a real package's byte stream. Assembling an object graph
from scratch is a separate, untested step (ROADMAP.md R28: "a graph
assembled from scratch"). This module deliberately stays on the measured
side of that line: it reads a real package, changes named things inside it,
and writes it back.

The safety property that makes that trustworthy
-----------------------------------------------
Before ANY mutation is permitted, the donor's own trace is replayed and
compared byte-for-byte against the donor's decompressed bytes. If we cannot
reproduce the file we did not modify, we have not understood its graph, and
we are not allowed to ship a file we did modify. `PackageBuilder.__init__`
raises `RoundTripError` in that case; there is no flag to bypass it.

Why mutation is structurally safe
---------------------------------
NRBF carries no absolute-offset pointers - every cross-reference is a logical
object id. Changing a string's value, or a primitive array's element count,
changes only that record's own length prefix and payload; every later record
simply shifts along. See nrbf_write.mutate_string_by_object_id for the same
argument applied to strings.

What this does NOT establish
----------------------------
That GC accepts the result, that it can be placed in a project, that it
builds, uploads, or drives a device. Those are hardware gates, and they are
what experiments/skeleton_i20/PROTOCOL.md exists to measure.

Usage
-----
    python3 tools/pkp_build.py DONOR.pkp --list
    python3 tools/pkp_build.py DONOR.pkp --replace-script NAME.py=new_driver.py \\
                               --set-string 22=NewModelName -o out.pkp
"""

import argparse
import gzip
import hashlib
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, os.path.join(_ROOT, "experiments", "nrbf_writeback")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd            # noqa: E402
import nrbf_write as nw          # noqa: E402


STREAM_ASSET_CLASS = "Extron.Configuration.Core.Assets.Resource.StreamResourceAsset"


class RoundTripError(Exception):
    """The donor could not be reproduced byte-for-byte from its own trace."""


class TransplantError(Exception):
    """A requested substitution could not be applied unambiguously."""


def deref(objs, ref):
    """Follow one {'$ref': id} indirection against PkpParser.objects."""
    if isinstance(ref, dict) and "$ref" in ref:
        return objs.get(ref["$ref"])
    return ref


def ref_id(ref):
    """The object id behind a {'$ref': id} member, or None."""
    if isinstance(ref, dict) and "$ref" in ref:
        return ref["$ref"]
    return None


class ScriptSlot(object):
    """One embedded script inside a package, and the object ids that carry it."""

    def __init__(self, asset_id, key, key_id, content_id, source):
        self.asset_id = asset_id
        self.key = key
        self.key_id = key_id
        self.content_id = content_id
        self.source = source

    def __repr__(self):
        return "ScriptSlot(key=%r, content_id=%d, %d bytes)" % (
            self.key, self.content_id, len(self.source.encode("utf-8")))


def mutate_primitive_array_by_object_id(trace, object_id, new_bytes):
    """Replace an ArraySinglePrimitive's payload, changing its length.

    The flat trace lays an ArraySinglePrimitive event down immediately
    followed by exactly `length` Primitive events, one per element (see
    nrbf_write.TracingPkpParser._read_primitive_value). So the edit is:
    rewrite the header event's length, then swap that contiguous run of
    element events for a new one.
    """
    idx = None
    for i, ev in enumerate(trace):
        if ev.get("kind") == "ArraySinglePrimitive" and ev.get("object_id") == object_id:
            if idx is not None:
                raise TransplantError(
                    "multiple ArraySinglePrimitive events with object_id=%r" % (object_id,))
            idx = i
    if idx is None:
        raise TransplantError(
            "no ArraySinglePrimitive event with object_id=%r" % (object_id,))

    header = trace[idx]
    pt = header["pt"]
    old_len = header["length"]

    # Verify the run really is `old_len` Primitive events of this type before
    # touching anything - a mismatch means our model of the trace is wrong,
    # and silently writing a corrupt package is the failure mode to avoid.
    run = trace[idx + 1: idx + 1 + old_len]
    if len(run) != old_len or any(
            ev.get("kind") != "Primitive" or ev.get("pt") != pt for ev in run):
        raise TransplantError(
            "object %d: expected %d contiguous Primitive(pt=%d) events after the "
            "array header, found %d matching" % (
                object_id, old_len,  pt,
                sum(1 for ev in run
                    if ev.get("kind") == "Primitive" and ev.get("pt") == pt)))

    new_run = [{"kind": "Primitive", "pt": pt, "value": b} for b in new_bytes]
    header["length"] = len(new_run)
    trace[idx + 1: idx + 1 + old_len] = new_run
    return old_len, len(new_run)


class PackageBuilder(object):
    """Read a donor .pkp, substitute named content, write a new .pkp.

    Construction parses the donor and immediately proves the round-trip. Any
    instance you hold is therefore one whose graph we demonstrably understand.
    """

    def __init__(self, donor_path):
        self.donor_path = donor_path
        self.raw = pd.load_bytes(donor_path)          # decompressed NRBF
        self.parser, self.trace = nw.parse_and_trace(self.raw)
        rebuilt = nw.write_trace(self.trace)
        if rebuilt != self.raw:
            n = min(len(rebuilt), len(self.raw))
            first = next((i for i in range(n) if rebuilt[i] != self.raw[i]), n)
            raise RoundTripError(
                "%s: donor does not round-trip (in=%d out=%d, first difference at "
                "byte %d) - refusing to build from a graph we cannot reproduce"
                % (donor_path, len(self.raw), len(rebuilt), first))
        self.objects = self.parser.objects
        self._edits = []

    # -- inspection --------------------------------------------------------

    def scripts(self):
        """Every embedded .py script in the donor, as ScriptSlot objects."""
        out = []
        for oid, v in self.objects.items():
            if not (isinstance(v, dict) and v.get("class") == STREAM_ASSET_CLASS):
                continue
            members = v.get("members", {})
            key_ref = members.get("ResourceAssetBase+_key")
            key = deref(self.objects, key_ref)
            if not (isinstance(key, str) and key.endswith(".py")):
                continue
            content_ref = members.get("ResourceAssetBase+_content")
            content = deref(self.objects, content_ref)
            if not (isinstance(content, dict)
                    and content.get("$type") == "ArraySinglePrimitive"):
                continue
            out.append(ScriptSlot(
                asset_id=oid, key=key, key_id=ref_id(key_ref),
                content_id=ref_id(content_ref),
                source=bytes(content["items"]).decode("utf-8")))
        out.sort(key=lambda s: s.content_id)
        return out

    def strings(self):
        """{object_id: value} for every BinaryObjectString in the donor."""
        return {ev["object_id"]: ev["value"]
                for ev in self.trace if ev.get("kind") == "BinaryObjectString"}

    def find_strings(self, pattern, flags=re.I):
        """[(object_id, value)] for strings matching a regex. Used to locate
        model/manufacturer text without hardcoding ids per donor."""
        rx = re.compile(pattern, flags)
        return sorted((oid, v) for oid, v in self.strings().items() if rx.search(v))

    # -- mutation ----------------------------------------------------------

    # -- integrity ---------------------------------------------------------

    def resource_hashes(self):
        """{resource key: (hash_object_id, current 32-byte digest)}.

        `DriverFileAsset._resourceHashDict` is a
        Dictionary<string, byte[]> whose KeyValuePairs array holds one entry
        per packaged resource - the embedded `.py` and the comm-sheet `.pdf`.
        Each value is the **SHA-256 of that resource's bytes**, verified
        against Extron's own stored digest.
        """
        root = self.objects.get(1)
        if not (isinstance(root, dict) and "_resourceHashDict" in (root.get("members") or {})):
            raise TransplantError("no _resourceHashDict on the root asset")
        d = deref(self.objects, root["members"]["_resourceHashDict"])
        kvps = deref(self.objects, (d.get("members") or {}).get("KeyValuePairs"))
        out = {}
        for item in (kvps or {}).get("items") or []:
            entry = deref(self.objects, item)
            if not isinstance(entry, dict):
                continue
            members = entry.get("members") or {}
            key = deref(self.objects, members.get("key"))
            vref = members.get("value")
            value = deref(self.objects, vref)
            if isinstance(key, str) and isinstance(value, dict):
                out[key] = (ref_id(vref), bytes(value.get("items") or []))
        return out

    def refresh_resource_hash(self, key=None, source=None):
        """Recompute the stored SHA-256 for one resource (or every script).

        Global Configurator validates a package before use:
        `DriverAssetValidator.Validate` returns `MismatchHash = 80085` when a
        resource's bytes disagree with this digest, and GC shows "Invalid
        Driver ... Error Code: 80085". Substituting a script without
        refreshing the hash therefore produces a package that indexes, appears
        in Driver Manager, and is refused on selection.

        `.NET`'s own `DriverFileAssetExtensions.RefreshResourceHash` does the
        same thing; this reimplements it so the repo stays standard-library
        only and does not need GC installed.
        """
        hashes = self.resource_hashes()
        targets = [key] if key else [s.key for s in self.scripts()]
        changed = []
        for k in targets:
            if k not in hashes:
                raise TransplantError("no stored hash for resource %r (have: %s)"
                                      % (k, ", ".join(sorted(hashes))))
            # `source` must be passed by replace_script: mutations live in the
            # trace, while self.objects still holds the ORIGINAL parse. Hashing
            # scripts() here would digest the script we just replaced, match the
            # stored value, and silently skip - leaving a package that fails
            # with 80085 while reporting success.
            if source is not None:
                text = source
            else:
                slot = next((s for s in self.scripts() if s.key == k), None)
                if slot is None:
                    raise TransplantError("resource %r is not an embedded script" % (k,))
                text = slot.source
            hash_id, before = hashes[k]
            digest = hashlib.sha256(text.encode("utf-8")).digest()
            if digest == before:
                continue
            mutate_primitive_array_by_object_id(self.trace, hash_id, digest)
            self._edits.append("hash %s: %s -> %s" % (k, before[:4].hex(), digest[:4].hex()))
            changed.append(k)
        return changed

    # -- mutation ----------------------------------------------------------

    def replace_script(self, key, new_source, refresh_hash=True):
        """Swap the source of the embedded script named `key`.

        `refresh_hash` defaults to True because a package whose script does not
        match its stored digest is rejected by GC at selection time (error
        80085). Pass False only to reproduce that failure deliberately.
        """
        slots = [s for s in self.scripts() if s.key == key]
        if not slots:
            raise TransplantError("no embedded script named %r (have: %s)" % (
                key, ", ".join(sorted(s.key for s in self.scripts())) or "none"))
        if len(slots) > 1:
            raise TransplantError("%r is ambiguous: %d slots" % (key, len(slots)))
        slot = slots[0]
        payload = new_source.encode("utf-8")
        old, new = mutate_primitive_array_by_object_id(
            self.trace, slot.content_id, payload)
        self._edits.append("script %s: %d -> %d bytes%s"
                           % (key, old, new,
                              "" if refresh_hash else "  [HASH NOT REFRESHED -> GC error 80085]"))
        if refresh_hash:
            self.refresh_resource_hash(key, source=new_source)
        return old, new

    def replace_string(self, object_id, new_value):
        """Swap one BinaryObjectString's value (model name, class name, ...)."""
        before = self.strings().get(object_id)
        if before is None:
            raise TransplantError("no BinaryObjectString with object_id=%r" % (object_id,))
        nw.mutate_string_by_object_id(self.trace, object_id, new_value)
        self._edits.append("string %d: %r -> %r" % (object_id, before, new_value))
        return before

    # -- output ------------------------------------------------------------

    def raw_bytes(self):
        """The rebuilt, still-uncompressed NRBF stream."""
        return nw.write_trace(self.trace)

    def build(self, compress=True):
        """The finished package bytes. Donors ship gzipped; match that."""
        data = self.raw_bytes()
        if not compress:
            return data
        # mtime=0 so a rebuild of identical content is itself byte-stable,
        # which is what makes 'did anything change?' a meaningful question.
        return gzip.compress(data, mtime=0)

    def write(self, path, compress=True):
        with open(path, "wb") as fh:
            fh.write(self.build(compress=compress))
        return path

    @property
    def edits(self):
        return list(self._edits)


def _parse_kv(items, what):
    out = []
    for item in items or []:
        if "=" not in item:
            raise SystemExit("--%s expects NAME=VALUE, got %r" % (what, item))
        k, v = item.split("=", 1)
        out.append((k, v))
    return out


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("donor", help="donor .pkp to transplant into")
    ap.add_argument("--list", action="store_true",
                    help="list embedded scripts and exit")
    ap.add_argument("--grep", metavar="REGEX",
                    help="list donor strings matching REGEX (to find metadata ids)")
    ap.add_argument("--replace-script", action="append", metavar="KEY=FILE",
                    help="replace embedded script KEY with the contents of FILE")
    ap.add_argument("--set-string", action="append", metavar="ID=VALUE",
                    help="set BinaryObjectString ID to VALUE")
    ap.add_argument("--no-refresh-hash", action="store_true",
                    help="do NOT recompute the stored SHA-256 after replacing a "
                         "script; produces a package GC refuses with error 80085")
    ap.add_argument("--hashes", action="store_true",
                    help="print the package's stored resource hashes and exit")
    ap.add_argument("-o", "--output", help="path to write the new .pkp")
    args = ap.parse_args()

    b = PackageBuilder(args.donor)
    print("donor round-trips byte-identically: %d bytes" % len(b.raw))

    if args.hashes:
        for k, (oid, digest) in sorted(b.resource_hashes().items()):
            ok = "" 
            slot = next((s for s in b.scripts() if s.key == k), None)
            if slot is not None:
                actual = hashlib.sha256(slot.source.encode("utf-8")).digest()
                ok = "  OK" if actual == digest else "  MISMATCH (actual %s)" % actual.hex()[:16]
            print("  %-34s #%-6s %s%s" % (k, oid, digest.hex(), ok))
        return 0

    if args.grep:
        for oid, val in b.find_strings(args.grep):
            print("  %6d  %r" % (oid, val))
        return 0

    if args.list or not (args.replace_script or args.set_string):
        for s in b.scripts():
            print("  %s  (asset %d, content object %d, %d bytes)"
                  % (s.key, s.asset_id, s.content_id, len(s.source.encode("utf-8"))))
        return 0

    for key, path in _parse_kv(args.replace_script, "replace-script"):
        with open(path, encoding="utf-8") as fh:
            b.replace_script(key, fh.read(), refresh_hash=not args.no_refresh_hash)
    for sid, val in _parse_kv(args.set_string, "set-string"):
        b.replace_string(int(sid), val)

    for e in b.edits:
        print("  edit: %s" % e)

    if not args.output:
        raise SystemExit("refusing to discard a mutated package: pass -o OUTPUT")
    b.write(args.output)
    print("wrote %s (%d bytes)" % (args.output, os.path.getsize(args.output)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
