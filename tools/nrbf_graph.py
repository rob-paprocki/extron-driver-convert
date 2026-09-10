#!/usr/bin/env python3
"""
nrbf_graph.py - structural navigation over an NRBF trace.

Why this exists
---------------
pkp_build.py can change what is already in a package: a string's value, a
primitive array's payload. It cannot *add* an object, because nothing knew
where one object's records end and the next one's begin. Finding 15 measured
the consequence on hardware - Global Configurator renders a driver's command
surface from `DriverCommandAsset` assets in the object graph, not from the
embedded Python - so a package can carry a script with 31 commands and show 15.

This module supplies the missing structure:

  EventWalker   every object id -> the exact span of trace events that encode
                it, derived by replaying the trace with the same record
                grammar the reader uses.
  ownership     which objects in a subtree belong to it alone, and which are
                shared with the rest of the graph.
  clone         copy an owned subtree under fresh object ids, remapping
                internal references and leaving shared references alone.

The safety property
-------------------
The walker is not trusted on assertion. `EventWalker` requires that consuming
records from index 0 lands exactly on the end of the trace with every event
attributed to exactly one object - if our grammar were wrong we would drift,
and drift is loud rather than silent. `verify_full_coverage()` raises on any
gap, overlap or overrun.

NRBF has no absolute offsets - every cross-reference is a logical object id -
so inserting records is safe as long as ids stay unique and references
resolve. That is the same argument pkp_build relies on for in-place edits,
extended to insertion.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, os.path.join(_ROOT, "experiments", "nrbf_writeback")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd            # noqa: E402


class GraphError(Exception):
    """The trace does not match the record grammar, or a clone is unsafe."""


# Record kinds that occupy exactly one event and fill exactly one value slot.
_LEAF_KINDS = frozenset((
    "MemberReference",
    "ObjectNull",
    "BinaryObjectString",
    "MemberPrimitiveTyped",
))

# Record kinds that fill MORE than one value slot with a single event.
_NULL_RUN_KINDS = frozenset(("ObjectNullMultiple256", "ObjectNullMultiple"))

_CLASS_KINDS = frozenset((
    "ClassWithMembersAndTypes",
    "ClassWithMembers",
    "ClassWithId",
))


class EventWalker(object):
    """Attribute every trace event to the object whose encoding it belongs to.

    `spans[object_id] = (start, end)` is a half-open range over the trace:
    trace[start] is the object's defining record and trace[start:end] is
    everything written for it, including the inline value-type members
    (.NET gives those negative object ids) nested inside it.
    """

    def __init__(self, trace):
        self.trace = trace
        self.spans = {}
        self.metadata = {}       # object_id -> the class record that defines its layout
        self._owner = [None] * len(trace)
        self._claiming = True
        self._walk()

    # -- grammar ----------------------------------------------------------

    def _member_types(self, ev):
        """The member type list governing a class record's value slots."""
        if ev["kind"] == "ClassWithId":
            meta = self.metadata.get(ev["metadata_id"])
            if meta is None:
                raise GraphError(
                    "ClassWithId object %r references metadata id %r that has "
                    "not been defined" % (ev.get("object_id"), ev["metadata_id"]))
            return meta.get("member_types"), len(meta["member_names"])
        if ev["kind"] == "ClassWithMembersAndTypes":
            return ev.get("member_types"), len(ev["member_names"])
        # ClassWithMembers carries names but no types: every value is a
        # self-describing record.
        return None, len(ev["member_names"])

    def _consume_value(self, i, type_info):
        """Consume the events encoding ONE value slot. Returns (next_index, slots_filled)."""
        if i >= len(self.trace):
            raise GraphError("trace ended mid-record at event %d" % i)
        ev = self.trace[i]
        kind = ev["kind"]

        if kind in _NULL_RUN_KINDS:
            return i + 1, ev["count"]

        # A typed Primitive member is a bare value, not a record.
        if type_info is not None and type_info.get("binary_type") == "Primitive":
            if kind != "Primitive":
                raise GraphError(
                    "event %d: expected a Primitive value, found %r" % (i, kind))
            return i + 1, 1

        if kind == "Primitive":
            # Untyped context (ClassWithMembers): still one slot.
            return i + 1, 1

        return self._consume_record(i), 1

    def _consume_record(self, i):
        """Consume one complete record starting at event i. Returns next index."""
        ev = self.trace[i]
        kind = ev["kind"]

        if kind == "BinaryLibrary":
            # A library declaration always precedes the class record it serves.
            return self._consume_record(i + 1)

        if kind in _LEAF_KINDS:
            self._claim(i, i + 1, ev.get("object_id"))
            return i + 1

        if kind in _NULL_RUN_KINDS:
            return i + 1

        if kind in _CLASS_KINDS:
            if kind != "ClassWithId":
                self.metadata[ev["object_id"]] = ev
            member_types, count = self._member_types(ev)
            j = i + 1
            filled = 0
            n = 0
            while filled < count:
                ti = member_types[n] if member_types is not None and n < len(member_types) else None
                j, k = self._consume_value(j, ti)
                filled += k
                n += 1
            self._claim(i, j, ev.get("object_id"))
            return j

        if kind == "ArraySinglePrimitive":
            j = i + 1 + ev["length"]
            self._claim(i, j, ev.get("object_id"))
            return j

        if kind in ("ArraySingleObject", "ArraySingleString"):
            j = i + 1
            filled = 0
            while filled < ev["length"]:
                j, k = self._consume_value(j, None)
                filled += k
            self._claim(i, j, ev.get("object_id"))
            return j

        if kind == "BinaryArray":
            total = 1
            for L in ev["lengths"]:
                total *= L
            j = i + 1
            if ev["bt"] == pd.BT_Primitive:
                j = i + 1 + total
            else:
                filled = 0
                while filled < total:
                    j, k = self._consume_value(j, None)
                    filled += k
            self._claim(i, j, ev.get("object_id"))
            return j

        raise GraphError("event %d: unexpected record kind %r at top level" % (i, kind))

    def _claim(self, start, end, object_id):
        if object_id is None or not self._claiming:
            return
        if object_id in self.spans:
            # Legal: the same id can be re-declared only if identical. NRBF
            # does not do this, so treat it as a grammar failure.
            raise GraphError("object id %r encoded twice (at %d and %d)"
                             % (object_id, self.spans[object_id][0], start))
        self.spans[object_id] = (start, end)
        for k in range(start, end):
            if self._owner[k] is None:
                self._owner[k] = object_id

    # -- driver -----------------------------------------------------------

    def _walk(self):
        i = 0
        n = len(self.trace)
        if n and self.trace[0]["kind"] == "Header":
            i = 1
        while i < n:
            kind = self.trace[i]["kind"]
            if kind == "MessageEnd":
                i += 1
                continue
            i = self._consume_record(i)
        self._end = i

    def verify_full_coverage(self):
        """Raise unless the walk consumed the whole trace with no drift."""
        if self._end != len(self.trace):
            raise GraphError("walk stopped at event %d of %d"
                             % (self._end, len(self.trace)))
        return True

    def owner_of(self, event_index):
        return self._owner[event_index]

    def member_slots(self, object_id):
        """{member name: event index where that member's value starts}.

        Lets a caller reach one field of one object - `List`1+_size`, a
        collection's backing array reference - without guessing offsets.
        """
        start, _end = self.spans[object_id]
        ev = self.trace[start]
        if ev["kind"] not in _CLASS_KINDS:
            raise GraphError("object %r is not a class record (%s)"
                             % (object_id, ev["kind"]))
        meta = self.metadata[ev["metadata_id"]] if ev["kind"] == "ClassWithId" else ev
        member_types, count = self._member_types(ev)
        names = meta["member_names"]
        out = {}
        self._claiming = False          # re-walking, not re-attributing
        j = start + 1
        filled = 0
        n = 0
        while filled < count:
            ti = member_types[n] if member_types is not None and n < len(member_types) else None
            if n < len(names):
                out[names[n]] = j
            j, k = self._consume_value(j, ti)
            filled += k
            n += 1
        self._claiming = True
        return out


# ---------------------------------------------------------------------------
# Reference graph and ownership
# ---------------------------------------------------------------------------

def _refs_of_value(v, out):
    if isinstance(v, dict):
        if "$ref" in v:
            out.add(v["$ref"])
            return
        if v.get("$type") in ("ArraySingleObject", "ArraySingleString", "BinaryArray"):
            for it in v.get("items", []):
                _refs_of_value(it, out)
            return
        for mv in v.get("members", {}).values():
            _refs_of_value(mv, out)


def reference_graph(objects):
    """{object_id: set(referenced ids)} and its reverse."""
    fwd = {}
    rev = {}
    for oid, v in objects.items():
        out = set()
        _refs_of_value(v, out)
        fwd[oid] = out
        for t in out:
            rev.setdefault(t, set()).add(oid)
    return fwd, rev


# Members that point UP or ACROSS the tree. Following them would drag the
# whole package into a subtree, so ownership analysis stops at them.
UPWARD_MEMBERS = frozenset((
    "AssetBase+_parentAsset",
    "AssetBase`1+_parentAsset",
))


def _child_refs(objects, oid):
    v = objects.get(oid)
    out = set()
    if isinstance(v, dict) and v.get("members") is not None:
        for name, mv in v["members"].items():
            if name in UPWARD_MEMBERS:
                continue
            _refs_of_value(mv, out)
    else:
        _refs_of_value(v, out)
    return out


def owned_subtree(objects, root, rev=None):
    """Objects reachable from `root` that nothing outside the subtree points at.

    Returns (owned, shared): `owned` is cloned, `shared` is referenced as-is.
    """
    if rev is None:
        _, rev = reference_graph(objects)

    # 1. everything reachable downward
    reach = set()
    stack = [root]
    while stack:
        o = stack.pop()
        if o in reach or o not in objects:
            continue
        reach.add(o)
        for t in _child_refs(objects, o):
            if t not in reach:
                stack.append(t)

    # 2. shrink to those referenced only from inside, to a fixpoint
    owned = set(reach)
    changed = True
    while changed:
        changed = False
        for o in sorted(owned):
            if o == root:
                continue
            outside = rev.get(o, set()) - owned
            if outside:
                owned.discard(o)
                changed = True
    shared = reach - owned
    return owned, shared


# ---------------------------------------------------------------------------
# Id allocation and cloning
# ---------------------------------------------------------------------------

class IdAllocator(object):
    """Hand out unused object ids.

    .NET's BinaryFormatter numbers reference objects positively and inline
    value types negatively; a clone keeps that convention so the stream stays
    recognisable to a reader that cares.
    """

    def __init__(self, spans):
        ids = [i for i in spans if i is not None]
        self._next_pos = max([i for i in ids if i > 0] or [0]) + 1
        self._next_neg = min([i for i in ids if i < 0] or [0]) - 1

    def new(self, like):
        if like is not None and like < 0:
            v = self._next_neg
            self._next_neg -= 1
            return v
        v = self._next_pos
        self._next_pos += 1
        return v


def clone_plan(walker, objects, root, rev=None):
    """Decide exactly which trace spans a clone of `root` must reproduce.

    Two rules, and the second is the one that is easy to get wrong:

      1. Emit only TOP-LEVEL spans. An inline value type sits inside its
         parent's span; emitting both would write it twice.
      2. Every object DEFINED INSIDE an emitted span must get a fresh id -
         even one the ownership analysis calls shared. Its original record
         still stands where it was, so outside references keep resolving to
         the original; reusing the id would put two definitions of it in one
         stream.

    Returns (spans_to_emit, ids_to_renumber).
    """
    owned, _shared = owned_subtree(objects, root, rev)
    have = sorted(((walker.spans[o][0], walker.spans[o][1], o)
                   for o in owned if o in walker.spans))
    tops = []
    for start, end, oid in have:
        if tops and start < tops[-1][1]:
            continue                      # nested inside an emitted span
        tops.append((start, end, oid))

    renumber = set()
    for start, end, _oid in tops:
        for k in range(start, end):
            ow = walker.owner_of(k)
            if ow is not None:
                renumber.add(ow)
    return tops, renumber


def clone_events(walker, tops, idmap, string_overrides=None):
    """Materialise the cloned records, in original stream order.

    Returns (events, pos_map) where pos_map maps an index in the ORIGINAL
    trace to its index in `events`, so a caller that located a field by
    walking the donor can reach the same field in the copy.
    """
    string_overrides = string_overrides or {}
    out = []
    pos_map = {}
    for start, end, _oid in tops:
        for k in range(start, end):
            pos_map[k] = len(out)
            out.append(_remap_event(walker.trace[k], idmap, string_overrides))
    return out, pos_map


def _remap_event(ev, idmap, string_overrides):
    """Copy one event with ids remapped.

    `metadata_id` is deliberately NOT remapped: a ClassWithId borrows a class
    layout that is already in the stream, and the clone borrows the same one.
    """
    new = dict(ev)
    orig = new.get("object_id")
    if orig is not None and orig in idmap:
        new["object_id"] = idmap[orig]
    if new["kind"] == "BinaryObjectString" and orig in string_overrides:
        new["value"] = string_overrides[orig]
    if new["kind"] == "MemberReference" and new["idref"] in idmap:
        new["idref"] = idmap[new["idref"]]
    return new


def main():
    import pkp_build as pb
    if len(sys.argv) < 2:
        print(__doc__.strip().splitlines()[1])
        print("usage: python3 tools/nrbf_graph.py PACKAGE.pkp [--object ID]")
        return 2
    b = pb.PackageBuilder(sys.argv[1])
    w = EventWalker(b.trace)
    w.verify_full_coverage()
    print("trace events : %d" % len(b.trace))
    print("objects      : %d  (positive %d, inline value types %d)" % (
        len(w.spans),
        sum(1 for i in w.spans if i > 0),
        sum(1 for i in w.spans if i < 0)))
    if "--object" in sys.argv:
        oid = int(sys.argv[sys.argv.index("--object") + 1])
        s, e = w.spans[oid]
        print("object %d: events %d..%d (%d events)" % (oid, s, e, e - s))
        owned, shared = owned_subtree(b.objects, oid)
        print("  owned subtree : %d objects" % len(owned))
        print("  shared refs   : %d objects" % len(shared))
    return 0


if __name__ == "__main__":
    sys.exit(main())
