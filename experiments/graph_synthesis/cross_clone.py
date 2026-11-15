#!/usr/bin/env python3
"""
cross_clone.py - ROADMAP R27: clone a DriverCommandAsset across packages.

tools/pkp_asset.py's CommandGraph.clone_command only ever copies within one
package's own trace: donor and target share one EventWalker, one object id
space, and - critically - one set of already-defined class-metadata records
and "shared" leaf objects (every reference a same-package clone leaves
untouched still resolves, because target IS the donor).

None of that holds across packages. Two donor-side facts a same-package
clone never has to deal with:

  1. CLASS METADATA lives outside the cloned span. A `ClassWithId` event's
     `metadata_id` is a donor object id pointing at the `ClassWithMembersAndTypes`
     / `ClassWithMembers` record that first defined that layout - usually
     emitted once, early, the first time the type was used, nowhere near the
     command being cloned. Measured (`RESULTS.md` R27): of the 14 distinct
     class layouts `pana_19_5702`'s `PanTiltAbsolutePosition` subtree needs,
     every one is defined OUTSIDE the cloned span.

  2. SHARED LEAF OBJECTS are real content the clone still needs, referenced
     from outside the subtree too: parameter names ("Pan", "Tilt"), the
     empty string every unused text field points at, an empty backing array
     shared by every childless parameter's collection. Measured: 12 of them,
     for this one command.

Both are invisible in a same-package clone because "outside the cloned
span" still means "inside the trace being edited" - the reference resolves
whether or not it was renumbered. Across packages it does not: importing
this command into the i20 donor without resolving these two would leave
`ClassWithId.metadata_id` and `MemberReference.idref` pointing at object ids
that belong to a DIFFERENT package's numbering, which either dangle or -
worse - silently collide with something unrelated the target already uses
that id for.

What this module adds, on top of nrbf_graph's existing primitives
--------------------------------------------------------------------
1. CLASS METADATA: name-matched reuse, falling back to import.
   Most class layouts a donor command needs (`DriverCommandAsset` itself,
   `DecimalParamAsset`, the `DriverAttributeEnum`/... bitfield enums,
   `System.Guid`, ...) already exist in the target under a different object
   id, because every `.pkp` defines them independently. `metadata_id` is
   repointed at the target's own matching definition, found by class name.

   One wrinkle, measured rather than assumed: `System.Collections.*` generic
   wrapper classes (`List`1[[...IParamAsset...]]`,
   `ObservableCollection`1[[...]]`) embed the TYPE ARGUMENT's
   assembly-qualified name inside their own class name string, including its
   `Version=X.X.X.X`. Two packages built against different
   `Extron.Configuration.Contracts` versions (13.26.0.15 for the donor used
   here, 1.1.24.402 for the i20 target) therefore have literally different
   class-name strings for what is structurally the identical generic
   collection. Finding 12 already measured that GC tolerates assembly-
   version skew at the whole-package level (a package declares 13.26.0.15
   while the installed DLL is 15.27.0.0, and GC loads it anyway); this is
   the same tolerance showing up as a name-matching problem instead of a
   loader problem. Fixed with a `Version=\\d+\\.\\d+\\.\\d+\\.\\d+` -> `Version=*`
   strip before comparing names.

   When no match exists even after stripping, the donor's own class-defining
   record (and, if needed, its `BinaryLibrary`) is imported under a fresh id,
   inserted immediately before the first place that needs it - matching the
   definition-before-first-use order a real .NET writer uses, which
   `nrbf_graph`'s own parser already depends on to read at all.

2. SHARED LEAF OBJECTS: closure import. Every `MemberReference` the cloned
   spans make to an id outside the target's graph is resolved to a fixpoint:
   import the referenced object too (verbatim text for a string; recursively,
   via the same `clone_plan`/`clone_events` primitives used for the command
   itself, for anything else), fresh id, until nothing points outside the
   graph any more.

R27's specific pair (`pana_19_5702`'s `PanTiltAbsolutePosition` into the i20
donor) exercises path 2 for real (12 shared objects) and exercises path 1's
name-matching machinery for real (6 of 14 classes only resolve after the
version strip) but never needs path 1's IMPORT fallback - every class layout
the command needs already exists in the target by name or by stripped name.
`test_cross_clone.py` exercises the import fallback directly, with a
synthetic donor class the target cannot possibly already have, so that path
is measured too, not just written.
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
_NWB = os.path.join(_ROOT, "experiments", "nrbf_writeback")
for _p in (_TOOLS, _NWB, _HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_build as pb            # noqa: E402
import pkp_dump as pd             # noqa: E402
import nrbf_graph as ng           # noqa: E402
import pkp_asset as pa            # noqa: E402


VERSION_RE = re.compile(r"Version=\d+\.\d+\.\d+\.\d+")


class CrossCloneError(pa.AssetError):
    pass


def strip_version(name):
    """Collapse an assembly-qualified type name's literal Version=X.X.X.X.

    Only System.Collections.* generic wrappers carry a version inside their
    OWN class name (via the type argument's assembly-qualified name); every
    other class name measured in this repo is version-free, so stripping is
    a no-op for them and this is safe to apply unconditionally.
    """
    return VERSION_RE.sub("Version=*", name or "")


class DonorTrace(object):
    """A donor package, parsed and walked once, independent of any target."""

    def __init__(self, path):
        self.path = path
        self.b = pb.PackageBuilder(path)
        raw = self.b.build(compress=False)
        self.parser = pd.PkpParser(raw)
        self.parser.parse()
        self.objects = self.parser.objects
        self.walker = ng.EventWalker(self.b.trace)
        self.walker.verify_full_coverage()
        _fwd, self.rev = ng.reference_graph(self.objects)

    def command_id(self, script_name):
        for oid, v in self.objects.items():
            if pa._cls(v) != pa.COMMAND_CLASS:
                continue
            sn = pb.deref(self.objects, v["members"].get("CommandAssetBase+_scriptName"))
            if sn == script_name:
                return oid
        have = sorted(
            pb.deref(self.objects, v["members"].get("CommandAssetBase+_scriptName"))
            for oid, v in self.objects.items() if pa._cls(v) == pa.COMMAND_CLASS)
        raise CrossCloneError("%s: no command %r (have %s)"
                              % (self.path, script_name, have))

    def library_name(self, lib_id):
        return self.parser.libraries.get(lib_id)


def _schema_key(ev):
    """A class-defining event's field layout, version-stripped, as a
    hashable key: (name, system, member_names, per-member type shape).

    Two packages can define a class under the IDENTICAL name with a
    DIFFERENT layout - measured directly (RESULTS.md R27): `pana_19_5702`
    (built against `Extron.Configuration.Core 13.26.0.15`) defines
    `DecimalParamAsset` with 29 members, including `_bEnableCustomMinMax`;
    the i20 donor (built against `1.1.24.402`) defines the SAME class name
    with 28 - that field does not exist at all. Reusing the i20 donor's
    metadata id for a `ClassWithId` written against pana's 29-member layout
    reads every member after the 8th one field off by one presence - not a
    crash at the point of reuse, but a byte-level desync that only surfaces
    many records later (as an `unhandled record type` a few hundred bytes
    into a re-parse, one of the least direct exceptions this codebase
    produces for a wrong assumption). Name-matched reuse is only safe when
    the schema is IDENTICAL; this key is what proves that rather than
    assumes it.
    """
    names = tuple(ev.get("member_names") or ())
    types = ev.get("member_types")
    if types is None:
        type_shapes = None  # ClassWithMembers: no wire-level type info at all
    else:
        shapes = []
        for info in types:
            bt = info.get("binary_type")
            if bt == "Primitive":
                shapes.append((bt, info.get("_pt")))
            elif bt in ("Class", "SystemClass"):
                shapes.append((bt, strip_version(info.get("class_name"))))
            else:
                shapes.append((bt,))
        type_shapes = tuple(shapes)
    return (strip_version(ev.get("name")), ev.get("system"), names, type_shapes)


def _target_metadata_index(target_graph):
    """{stripped class name: [(target object id, schema_key), ...]}."""
    idx = {}
    for tid, tev in target_graph.walker.metadata.items():
        idx.setdefault(strip_version(tev.get("name")), []).append((tid, _schema_key(tev)))
    return idx


def _target_library_index(target_graph):
    """{stripped library name: target lib_id}, plus the max lib_id in use."""
    idx = {}
    max_id = 0
    for ev in target_graph.b.trace:
        if ev.get("kind") == "BinaryLibrary":
            idx.setdefault(strip_version(ev["name"]), ev["lib_id"])
            max_id = max(max_id, ev["lib_id"])
    return idx, max_id


def _string_plan(objects, root, name, script_name, description, text_map, renumber):
    """Same rule as pkp_asset.CommandGraph._string_plan, parametrized by
    donor objects instead of a bound self.objects."""
    m = objects[root]["members"]
    out = {}
    retarget = {}

    def put(member, value):
        if value is None or member not in m:
            return
        sid = pb.ref_id(m.get(member))
        if sid is None:
            retarget[member] = value
        elif sid in renumber:
            out[sid] = value
        else:
            retarget[member] = value

    put("AssetBase+_name", name)
    put("AssetBase+_defaultName", name)
    put("CommandAssetBase+_internalName", name)
    put("CommandAssetBase+_scriptName", script_name)
    put("CommandAssetBase+_description", description)

    for old_text, new_text in (text_map or {}).items():
        hits = [sid for sid in renumber
                if isinstance(objects.get(sid), str) and objects[sid] == old_text]
        if not hits:
            raise CrossCloneError(
                "no owned string %r inside the donor clone of asset %d - it is "
                "either absent or shared with the rest of the donor package"
                % (old_text, root))
        for sid in hits:
            out[sid] = new_text
    return out, retarget


def _retarget_strings(target_graph, donor_walker, events, pos_map, root, retarget):
    if not retarget:
        return
    slots = donor_walker.member_slots(root)
    for member, text in sorted(retarget.items()):
        idx = pos_map.get(slots[member])
        if idx is None:
            raise CrossCloneError("member %s is not inside the donor's cloned span" % member)
        if events[idx]["kind"] != "MemberReference":
            raise CrossCloneError(
                "%s is written inline as %s in the donor; repointing it would drop "
                "a definition the clone still references" % (member, events[idx]["kind"]))
        sid = target_graph.alloc.new(1)
        events.append({"kind": "BinaryObjectString", "object_id": sid, "value": text})
        events[idx] = {"kind": "MemberReference", "idref": sid}


def _raw_refs(walker, tops, exclude=frozenset()):
    """MemberReference idrefs appearing in the RAW donor trace across `tops`,
    in first-seen order, before any id remapping. `exclude` is a set of trace
    indices to skip (severed upward references - see _severed_indices_for)."""
    out = []
    seen = set()
    for s, e, _oid in tops:
        for k in range(s, e):
            if k in exclude:
                continue
            ev = walker.trace[k]
            if ev["kind"] == "MemberReference":
                r = ev["idref"]
                if r not in seen:
                    seen.add(r)
                    out.append(r)
    return out


def _upward_indices_for(donor, tops):
    """Trace indices holding an UPWARD_MEMBERS reference (`_parentAsset`) for
    any object whose own span is one of `tops`.

    Ownership analysis (`nrbf_graph.owned_subtree`) already refuses to walk
    these when deciding what a clone owns - that is exactly why cloning a
    command within its OWN package never drags in the whole ancestor chain
    up to the package root. A cross-package closure has to enforce the same
    refusal explicitly when DISCOVERING what to import: a plain reference
    scan has no such rule built in, and measured directly (see RESULTS.md
    R27) walking one `_parentAsset` is enough to pull in the donor's root
    DriverFileAsset - and from there, by ordinary downward reachability, the
    other 17,000-odd objects in the donor's WHOLE package.

    These candidates are NOT automatically severed. A parameter's
    `_parentAsset` pointing at the very command it belongs to is an upward
    reference too, but its target ends up in `idmap` anyway (the command is
    the clone's own root) - severing it would needlessly null out a
    perfectly resolvable, correct reference. `clone_command_cross_package`
    decides per-candidate, once the final idmap is known: resolvable ones
    are left as ordinary references, only the ones still pointing outside
    the clone are severed to `ObjectNull`.
    """
    idxs = set()
    for _s, _e, oid in tops:
        v = donor.objects.get(oid)
        if not (isinstance(v, dict) and v.get("members")):
            continue
        for mname in v["members"]:
            if mname not in ng.UPWARD_MEMBERS:
                continue
            slots = donor.walker.member_slots(oid)
            idx = slots.get(mname)
            if idx is not None and donor.walker.trace[idx]["kind"] == "MemberReference":
                idxs.add(idx)
    return idxs


def _meta_refs(donor, tops, resolved):
    """Distinct ClassWithId metadata_ids referenced in the raw donor trace
    across `tops`, not already in `resolved`, in first-seen order."""
    out = []
    seen = set()
    for s, e, _oid in tops:
        for k in range(s, e):
            ev = donor.walker.trace[k]
            if ev["kind"] == "ClassWithId":
                mid = ev["metadata_id"]
                if mid not in resolved and mid not in seen:
                    seen.add(mid)
                    out.append(mid)
    return out


def _add_claimed(claimed, new_tops, is_meta):
    """Add `new_tops` to the accumulated (start, end, oid, is_meta) list,
    keeping it free of overlaps.

    Two SEPARATE `clone_plan` calls, run one after another for two different
    roots discovered independently, can return spans where one CONTAINS the
    other: measured directly (RESULTS.md R27) - a shared string ("seconds")
    is discovered and imported on its own via an ordinary MemberReference,
    and only later does a class-metadata import turn out to need the OBJECT
    THAT STRING SITS INSIDE (a DecimalParamAsset instance whose own `_suffix`
    happens to be that same string) - whose span, being the metadata
    object's ENTIRE instance, textually CONTAINS the smaller span already
    claimed for the string alone. `clone_plan`'s own nested-span filter only
    dedupes within ONE call's own results; across separate calls each is
    blind to what the other already claimed, and `ng.clone_events` has no
    overlap check of its own - it would emit the contained span TWICE,
    producing two records for the same NEW object id, which is exactly the
    "object id encoded twice" a re-parse catches (loudly, not silently).
    """
    for ns, ne, noid in new_tops:
        if any(cs <= ns and ne <= ce for cs, ce, _co, _cm in claimed):
            continue  # already covered by something claimed earlier
        claimed[:] = [c for c in claimed if not (ns <= c[0] and c[1] <= ne)]
        claimed.append((ns, ne, noid, is_meta))


def _resolve_graph(target_graph, donor, tops, idmap):
    """Extend `idmap` to a fixpoint over TWO kinds of donor-graph edges a
    same-package clone never has to resolve:

      - MemberReference idrefs to shared objects outside the cloned subtree
        (imported verbatim, recursively - a string's text, an object's own
        owned span);
      - ClassWithId metadata_ids whose defining record the target does not
        already carry under an IDENTICAL schema (name-matched reuse when the
        schema matches - see _schema_key - imported, full span, otherwise).

    A class-metadata import is importing an OBJECT like any other: NRBF has
    no schema-only record, so a `ClassWithMembersAndTypes` occurrence is
    simultaneously a type declaration AND that type's first instance -
    `clone_plan(root=metadata_id)` naturally captures both, and whatever
    that first instance's own fields reference recurses through the SAME
    queue. Metadata objects are kept in a separate list and prepended in
    front of everything else in the final span order, so every class
    declaration precedes every use of it - measured to matter directly (see
    RESULTS.md R27): a class-defining record read out of stream order is
    exactly the failure this fixes.

    Returns (final_tops, severed: raw indices whose UPWARD_MEMBERS
    reference still points outside the final idmap, imported_shared,
    imported_classes, imported_libs, schema_mismatches).
    """
    claimed = [(s, e, oid, False) for s, e, oid in tops]
    upward = set(_upward_indices_for(donor, tops))
    imported_shared = []
    imported_classes = []
    schema_mismatches = []

    target_class_idx = _target_metadata_index(target_graph)

    def scan(batch):
        up = _upward_indices_for(donor, batch)
        upward.update(up)
        objs = [r for r in _raw_refs(donor.walker, batch, up) if r not in idmap]
        metas = _meta_refs(donor, batch, idmap)
        return objs, metas

    obj_pending, meta_pending = scan(tops)
    obj_seen, meta_seen = set(obj_pending), set(meta_pending)

    while obj_pending or meta_pending:
        while obj_pending:
            oid = obj_pending.pop(0)
            if oid in idmap:
                continue
            sub_tops, sub_renumber = ng.clone_plan(donor.walker, donor.objects, oid, donor.rev)
            for sid in sorted(sub_renumber, key=lambda o: donor.walker.spans[o][0]):
                if sid not in idmap:
                    idmap[sid] = target_graph.alloc.new(sid)
            _add_claimed(claimed, sub_tops, False)
            val = donor.objects.get(oid)
            desc = val if isinstance(val, str) else (
                pa._cls(val) or (val.get("$type") if isinstance(val, dict) else repr(val)))
            imported_shared.append((oid, desc))
            o2, m2 = scan(sub_tops)
            for r in o2:
                if r not in idmap and r not in obj_seen:
                    obj_pending.append(r)
                    obj_seen.add(r)
            for m in m2:
                if m not in idmap and m not in meta_seen:
                    meta_pending.append(m)
                    meta_seen.add(m)

        while meta_pending:
            mid = meta_pending.pop(0)
            if mid in idmap:
                continue
            donor_meta_ev = donor.walker.metadata.get(mid)
            if donor_meta_ev is None:
                raise CrossCloneError(
                    "class metadata id %d referenced but not defined anywhere "
                    "in the donor's own trace" % mid)
            name = strip_version(donor_meta_ev.get("name"))
            donor_key = _schema_key(donor_meta_ev)
            match = next((tid for tid, tkey in target_class_idx.get(name, ())
                         if tkey == donor_key), None)
            if match is None and name in target_class_idx:
                schema_mismatches.append(
                    (donor_meta_ev.get("name"),
                     [tid for tid, _ in target_class_idx[name]]))
            if match is not None:
                idmap[mid] = match
                continue

            sub_tops, sub_renumber = ng.clone_plan(donor.walker, donor.objects, mid, donor.rev)
            for sid in sorted(sub_renumber, key=lambda o: donor.walker.spans[o][0]):
                if sid not in idmap:
                    idmap[sid] = target_graph.alloc.new(sid)
            _add_claimed(claimed, sub_tops, True)
            imported_classes.append(donor_meta_ev.get("name"))
            target_class_idx.setdefault(name, []).append((idmap[mid], donor_key))
            o2, m2 = scan(sub_tops)
            for r in o2:
                if r not in idmap and r not in obj_seen:
                    obj_pending.append(r)
                    obj_seen.add(r)
            for m in m2:
                if m not in idmap and m not in meta_seen:
                    meta_pending.append(m)
                    meta_seen.add(m)

    meta_tops = [(s, e, oid) for s, e, oid, is_meta in claimed if is_meta]
    obj_tops = [(s, e, oid) for s, e, oid, is_meta in claimed if not is_meta]
    severed = {idx for idx in upward if donor.walker.trace[idx]["idref"] not in idmap}
    return meta_tops + obj_tops, severed, imported_shared, imported_classes, schema_mismatches


def _fix_embedded_libraries(target_graph, donor, events):
    """Remap every library_id a cross-package clone actually writes bytes
    for: a class-defining event's own outer library_id, and any per-member
    `binary_type: Class` type-info entry's library_id (a field whose static
    TYPE is itself a concrete class carries its OWN library reference,
    independent of the declaring class's). Both are read straight off the
    donor's bytes by `clone_events`/`_remap_event`, which only ever remaps
    object ids - never a library_id, since a same-package clone never needs
    to.

    Reuses the target's existing declaration for the same assembly by
    version-stripped name (matching how finding 12 measured GC tolerates
    assembly-version skew at the whole-package level); only mints a new
    `BinaryLibrary` record, inserted immediately before the event that needs
    it, when the target truly has no declaration for that assembly at all.
    Returns the list of newly-imported library name strings.
    """
    target_lib_idx, lib_next_id = _target_library_index(target_graph)
    imported_libs = []

    def resolve(lib_id, insert_at):
        nonlocal lib_next_id
        lib_name = donor.library_name(lib_id)
        stripped = strip_version(lib_name)
        if stripped in target_lib_idx:
            return target_lib_idx[stripped], 0
        lib_next_id += 1
        events.insert(insert_at, {"kind": "BinaryLibrary", "lib_id": lib_next_id, "name": lib_name})
        target_lib_idx[stripped] = lib_next_id
        imported_libs.append(lib_name)
        return lib_next_id, 1

    i = 0
    while i < len(events):
        ev = events[i]
        advance = 1
        if ev["kind"] in ("ClassWithMembersAndTypes", "ClassWithMembers") and ev.get("library_id") is not None:
            new_lib, ins = resolve(ev["library_id"], i)
            ev["library_id"] = new_lib
            i += ins
            advance = 1
        if ev["kind"] in ("ClassWithMembersAndTypes",) and ev.get("member_types"):
            for info in ev["member_types"]:
                if info.get("binary_type") == "Class" and info.get("library_id") is not None:
                    new_lib, ins = resolve(info["library_id"], i)
                    info["library_id"] = new_lib
                    i += ins
        if ev["kind"] == "BinaryArray" and ev.get("bt") == pd.BT_Class and ev.get("library_id") is not None:
            new_lib, ins = resolve(ev["library_id"], i)
            ev["library_id"] = new_lib
            i += ins
        i += advance
    return imported_libs


def clone_command_cross_package(target_graph, donor, donor_script_name,
                                 name, script_name, description=None,
                                 attributes=None, text_map=None):
    """Clone `donor_script_name` out of a DIFFERENT package (`donor`, a
    DonorTrace) into `target_graph` (a pkp_asset.CommandGraph): import
    whatever class/library/shared-object records the target does not
    already have, register the result in every command collection.

    Returns (new_object_id, imported_class_names, imported_library_names,
    imported_shared_objects, schema_mismatches - [(donor class name, [target
    ids found under that name whose schema did NOT match])]).
    """
    donor_cmd_id = donor.command_id(donor_script_name)

    if script_name in target_graph.commands():
        raise CrossCloneError("command %r already exists in the target graph" % script_name)

    tops, renumber = ng.clone_plan(donor.walker, donor.objects, donor_cmd_id, donor.rev)
    idmap = {}
    for oid in sorted(renumber, key=lambda o: donor.walker.spans[o][0]):
        idmap[oid] = target_graph.alloc.new(oid)

    overrides, retarget = _string_plan(
        donor.objects, donor_cmd_id, name, script_name, description, text_map, renumber)

    # Resolve every reference (object AND class-metadata) the command's own
    # owned subtree still makes to something outside it, BEFORE emitting any
    # events - so the single clone_events pass below has a complete idmap
    # and never has to patch up an already-written reference.
    (all_tops, severed, imported_shared, imported_classes,
     schema_mismatches) = _resolve_graph(target_graph, donor, tops, idmap)

    events, pos_map = ng.clone_events(donor.walker, all_tops, idmap, overrides)
    for idx in severed:
        pidx = pos_map.get(idx)
        if pidx is not None:
            events[pidx] = {"kind": "ObjectNull"}
    _retarget_strings(target_graph, donor.walker, events, pos_map, donor_cmd_id, retarget)

    # clone_events (like same-package clone_asset) deliberately never touches
    # metadata_id - within one package the metadata a ClassWithId points at
    # is untouched by the clone and stays valid as-is. Across packages it
    # is NOT untouched: _resolve_graph above populated idmap with a target-
    # space id for every metadata_id the cloned spans reference (reused or
    # imported), and that mapping has to be applied here, once, now that it
    # is complete - the same fixpoint-before-you-write discipline
    # clone_command_cross_package already uses for object ids.
    for ev in events:
        if ev["kind"] == "ClassWithId":
            ev["metadata_id"] = idmap[ev["metadata_id"]]

    imported_libs = _fix_embedded_libraries(target_graph, donor, events)

    target_graph._append_events(events)
    target_graph._reparse()

    new_id = idmap[donor_cmd_id]
    if attributes is not None:
        target_graph.set_attributes(new_id, attributes)

    for _n, lst_id, arr_id in target_graph.command_collections():
        target_graph._append_child(lst_id, arr_id, new_id)
    target_graph._reparse()

    target_graph.added.append((script_name, new_id))
    return new_id, imported_classes, imported_libs, imported_shared, schema_mismatches
