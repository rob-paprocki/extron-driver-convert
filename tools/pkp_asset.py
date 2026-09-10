#!/usr/bin/env python3
"""
pkp_asset.py - add commands to an Extron .pkp's object graph.

The gap this closes
-------------------
Finding 15 measured on hardware, and a Global Configurator screenshot later
confirmed it directly: GC builds a driver's command surface from
`DriverCommandAsset` objects in the NRBF graph and never asks the embedded
Python what it can do. `experiments/skeleton_i20/build_i20.py` added 17
commands to the script's `self.Commands` table and none to the graph, so the
package loads, validates, and shows the donor's 15 commands while the other 17
sit in the file as unreachable code.

`_scriptName` is the seam:

    AssetBase+_name                 'Backlight'      <- what GC displays
    CommandAssetBase+_scriptName    'Backlight'      <- the self.Commands key
    CommandAssetBase+_attributes    DriverAttributeEnum bitfield
    _internalChildCollection        the parameter assets

A command present in both places is one GC will render AND the script will
answer.

Why clone rather than construct
-------------------------------
Same reason pkp_build.py transplants rather than synthesising a whole file: a
cloned subtree is structurally identical to one Extron shipped, so the only
way it can be wrong is in the fields we deliberately changed. Building
`OperatorFlags`, `ParamAttributeFlags` and `DriverConditionTypeFlags` from
scratch would put twenty-odd unmeasured decisions between us and a package.

Why clone/attach/detach rather than clone-whole-commands
--------------------------------------------------------
The donor has no command shaped like `ZoomPosition` (a decimal value with a
decimal speed qualifier) - it has Zoom (decimal speed + enum value) and Preset
(enum action + decimal value). Cloning whole commands can only reproduce
shapes the donor already has. Cloning individual *parameters* and attaching
them composes any shape from parts that are all still Extron's own, because
every class layout the pieces need is already defined in the stream.

What this does NOT establish
----------------------------
That GC renders the added commands, that the parameter widgets are right, or
that anything drives a camera. Package validation covers only the packaged
resources (finding 16), so a structurally broken graph still validates - the
check that matters is GC's UI, and that is a hardware gate.
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
for _p in (_HERE, os.path.join(_ROOT, "experiments", "nrbf_writeback")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd            # noqa: E402
import pkp_build as pb           # noqa: E402
import nrbf_graph as ng          # noqa: E402


COMMAND_CLASS = "Extron.Configuration.Drivers.DriverCommandAsset"

CHILD_COLLECTION = "_internalChildCollection"
ITEMS_MEMBER = "Collection`1+items"

NAME_MEMBERS = ("AssetBase+_name", "AssetBase+_defaultName")


class AssetError(Exception):
    """A clone or attachment could not be performed safely."""


def _cls(v):
    return v["class"].split(",")[0] if isinstance(v, dict) and v.get("class") else None


def _expand_slots(events, capacity, arr_id):
    """One event per array slot.

    NRBF compresses a run of empty slots into a single `ObjectNullMultiple`,
    so an array of capacity 4 holding 2 items is 3 events, not 4. Editing by
    slot index needs them one-to-one; expanding to plain `ObjectNull` records
    is exactly equivalent on the wire, just larger.
    """
    out = []
    for ev in events:
        if ev["kind"] in ("ObjectNullMultiple", "ObjectNullMultiple256"):
            out.extend({"kind": "ObjectNull"} for _ in range(ev["count"]))
        else:
            out.append(ev)
    if len(out) != capacity:
        raise AssetError("array %d: %d slots for a declared capacity of %d"
                         % (arr_id, len(out), capacity))
    return out


class CommandGraph(object):
    """The asset graph of one package, and the ability to extend it."""

    def __init__(self, builder):
        self.b = builder
        self._reparse()
        self.alloc = ng.IdAllocator(self.walker.spans)
        self.added = []

    def _reparse(self):
        """Re-derive the object model and spans from the CURRENT trace.

        Every insertion shifts event indices, so spans are rebuilt rather than
        patched - the walker is cheap next to the cost of being subtly wrong.
        """
        raw = self.b.build(compress=False)
        parser = pd.PkpParser(raw)
        parser.parse()
        self.objects = parser.objects
        self.walker = ng.EventWalker(self.b.trace)
        self.walker.verify_full_coverage()
        self._fwd, self._rev = ng.reference_graph(self.objects)

    # -- reading ----------------------------------------------------------

    def commands(self):
        """{scriptName: object id} for every DriverCommandAsset."""
        out = {}
        for oid, v in self.objects.items():
            if _cls(v) != COMMAND_CLASS:
                continue
            sn = pb.deref(self.objects, v["members"].get("CommandAssetBase+_scriptName"))
            if isinstance(sn, str):
                out[sn] = oid
        return out

    def command_names(self):
        out = {}
        for sn, oid in self.commands().items():
            out[sn] = pb.deref(self.objects, self.objects[oid]["members"]["AssetBase+_name"])
        return out

    def name_of(self, asset_id):
        return pb.deref(self.objects, self.objects[asset_id]["members"].get("AssetBase+_name"))

    def _collection_of(self, asset_id):
        """(list_object_id, array_object_id) for an asset's child collection."""
        v = self.objects[asset_id]
        coll = pb.deref(self.objects, v["members"].get(CHILD_COLLECTION))
        if not isinstance(coll, dict):
            raise AssetError("asset %d has no child collection" % asset_id)
        lst_id = pb.ref_id(coll["members"].get(ITEMS_MEMBER))
        lst = self.objects[lst_id]
        arr_id = pb.ref_id(lst["members"].get("_items"))
        return lst_id, arr_id

    def children(self, asset_id):
        lst_id, arr_id = self._collection_of(asset_id)
        n = pb.deref(self.objects, self.objects[lst_id]["members"]["_size"])
        arr = self.objects[arr_id]
        return [pb.ref_id(x) for x in arr["items"][:n]]

    def command_collections(self):
        """[(name, list_id, array_id)] for every collection that lists commands."""
        out = []
        for oid, v in self.objects.items():
            c = _cls(v)
            if not c or "IDriverCommandAsset" not in c:
                continue
            if not c.startswith("Extron.Configuration.Core.Assets.AssetBase"):
                continue
            lst_id, arr_id = self._collection_of(oid)
            out.append((pb.deref(self.objects, v["members"].get("AssetBase+_name")),
                        lst_id, arr_id))
        return sorted(out, key=lambda t: t[1])

    # -- cloning ----------------------------------------------------------

    def clone_asset(self, donor_id, name=None, script_name=None,
                    description=None, text_map=None):
        """Copy an asset and everything it exclusively owns, under fresh ids.

        `text_map` rewrites owned strings by their current text - the way to
        rename an enum's states ({'On': 'Start', 'Off': 'Stop'}). It only ever
        touches strings inside the clone, so it cannot rename the donor.

        Returns (new_root_id, idmap).
        """
        tops, renumber = ng.clone_plan(self.walker, self.objects, donor_id, self._rev)
        idmap = {}
        for oid in sorted(renumber, key=lambda o: self.walker.spans[o][0]):
            idmap[oid] = self.alloc.new(oid)

        overrides, retarget = self._string_plan(
            donor_id, name, script_name, description, text_map, renumber)
        events, pos_map = ng.clone_events(self.walker, tops, idmap, overrides)
        self._retarget_strings(events, pos_map, donor_id, retarget)
        self._append_events(events)
        self._reparse()
        return idmap[donor_id], idmap

    def clone_command(self, donor_script_name, name, script_name,
                      description=None, attributes=None, text_map=None):
        """Clone a donor command and register it in every command collection."""
        cmds = self.commands()
        if donor_script_name not in cmds:
            raise AssetError("donor command %r not in package (have %s)"
                             % (donor_script_name, sorted(cmds)))
        if script_name in cmds:
            raise AssetError("command %r already exists in the graph" % script_name)

        new_id, idmap = self.clone_asset(
            cmds[donor_script_name], name=name, script_name=script_name,
            description=description, text_map=text_map)

        if attributes is not None:
            self.set_attributes(new_id, attributes)

        for _n, lst_id, arr_id in self.command_collections():
            self._append_child(lst_id, arr_id, new_id)
        self._reparse()

        self.added.append((script_name, new_id))
        self.b.edits.append("clone-command %s <- %s (obj %d)"
                            % (script_name, donor_script_name, new_id))
        return new_id

    # -- composing --------------------------------------------------------

    def attach(self, parent_id, child_id):
        """Add an existing asset to a parent's child collection."""
        lst_id, arr_id = self._collection_of(parent_id)
        self._append_child(lst_id, arr_id, child_id)
        self._reparse()

    def detach(self, parent_id, child_id):
        """Remove a child from a parent's collection, keeping the array full."""
        lst_id, arr_id = self._collection_of(parent_id)
        arr_start, arr_end = self.walker.spans[arr_id]
        arr_ev = self.b.trace[arr_start]
        cap = arr_ev["lengths"][0]
        start = arr_start + 1
        elems = _expand_slots(self.b.trace[start:arr_end], cap, arr_id)
        hit = [i for i, e in enumerate(elems)
               if e["kind"] == "MemberReference" and e["idref"] == child_id]
        if not hit:
            raise AssetError("asset %d is not a child of %d" % (child_id, parent_id))
        del elems[hit[0]]
        elems.append({"kind": "ObjectNull"})
        self.b.trace[start:arr_end] = elems
        slots = ng.EventWalker(self.b.trace).member_slots(lst_id)
        self.b.trace[slots["_size"]]["value"] -= 1
        self.b.trace[slots["_version"]]["value"] += 1
        self._reparse()

    def rename_asset(self, asset_id, new_name):
        """Rename an asset that is already in the graph.

        A clone's name string belongs to the clone, so it can simply be
        rewritten. A string shared with the rest of the package cannot - the
        asset's name members are repointed at a fresh string instead, leaving
        every other holder alone. Which case applies is measured from the
        trace, never assumed.
        """
        slots = self.walker.member_slots(asset_id)
        i = slots["AssetBase+_name"]
        ev = self.b.trace[i]
        if ev["kind"] == "BinaryObjectString":
            sid = ev["object_id"]
        elif ev["kind"] == "MemberReference":
            sid = ev["idref"]
        else:
            raise AssetError("asset %d has no name string (%s)"
                             % (asset_id, ev["kind"]))

        start, end = self.walker.spans[asset_id]
        total = sum(1 for e in self.b.trace
                    if e["kind"] == "MemberReference" and e.get("idref") == sid)
        inside = sum(1 for j in range(start, end)
                     if self.b.trace[j]["kind"] == "MemberReference"
                     and self.b.trace[j].get("idref") == sid)
        defined_inside = start <= self.walker.spans.get(sid, (-1, -1))[0] < end

        if total == inside and defined_inside:
            self.b.trace[self.walker.spans[sid][0]]["value"] = new_name
            self._reparse()
            return

        new_sid = self.alloc.new(1)
        rescued = []
        for member in NAME_MEMBERS:
            j = slots.get(member)
            if j is None:
                continue
            held = self.b.trace[j]
            if held["kind"] == "BinaryObjectString":
                # This slot IS the string's only definition. Others still
                # point at it, so re-emit it at top level before the slot is
                # overwritten - otherwise their references would dangle.
                rescued.append(dict(held))
            elif held["kind"] != "MemberReference":
                continue
            self.b.trace[j] = {"kind": "MemberReference", "idref": new_sid}
        self._append_events(rescued + [{"kind": "BinaryObjectString",
                                        "object_id": new_sid, "value": new_name}])
        self._reparse()

    def set_range(self, param_id, minimum, maximum, interval=None, suffix=None):
        """Set a DecimalParamAsset's limits.

        `_min`/`_max` and their `_soft` twins are decimals carried as strings;
        GC shows the soft pair as the editable "Custom Range" and clamps it to
        the hard pair.
        """
        slots = self.walker.member_slots(param_id)
        for member, value in (("_min", minimum), ("_softMin", minimum),
                              ("_max", maximum), ("_softMax", maximum),
                              ("_interval", interval)):
            if value is None:
                continue
            ev = self.b.trace[slots[member]]
            if ev["kind"] not in ("MemberPrimitiveTyped", "Primitive"):
                raise AssetError("%s of asset %d is %s, not a decimal"
                                 % (member, param_id, ev["kind"]))
            ev["value"] = str(value)
        self._reparse()
        if suffix is not None:
            self.set_string_member(param_id, "_suffix", suffix)

    def set_string_member(self, asset_id, member, text):
        """Repoint one string member of an asset at a fresh string object."""
        slots = self.walker.member_slots(asset_id)
        i = slots[member]
        ev = self.b.trace[i]
        sid = self.alloc.new(1)
        self._append_events([{"kind": "BinaryObjectString",
                              "object_id": sid, "value": text}])
        if ev["kind"] != "MemberReference":
            # An inline BinaryObjectString IS the string's only definition;
            # replacing it with a reference would strand anything else that
            # points at it. Rename those at clone time via `text_map`.
            raise AssetError(
                "%s of asset %d is written inline as %s - rename it with "
                "text_map when cloning instead" % (member, asset_id, ev["kind"]))
        self.b.trace[i] = {"kind": "MemberReference", "idref": sid}
        self._reparse()

    def set_attributes(self, command_id, value):
        """Rewrite a command's DriverAttributeEnum bitfield.

        The enum is an inline value type: a ClassWithId immediately followed by
        one Primitive carrying the bits.
        """
        slots = self.walker.member_slots(command_id)
        i = slots["CommandAssetBase+_attributes"]
        ev = self.b.trace[i]
        if ev["kind"] != "ClassWithId":
            raise AssetError("attributes member is %s, not an inline enum" % ev["kind"])
        nxt = self.b.trace[i + 1]
        if nxt["kind"] != "Primitive":
            raise AssetError("attributes enum is not followed by a value")
        nxt["value"] = int(value)
        self._reparse()

    # -- internals --------------------------------------------------------

    def _string_plan(self, root, name, script_name, description, text_map, renumber):
        """How to give a clone its own text.

        Donor strings fall into two classes, and conflating them is the bug
        this guards against:

        - a string DEFINED INSIDE the clone is already being renumbered, so the
          copy simply gets a different value;
        - a SHARED string (all 15 commands point at ONE empty description) must
          not be rewritten - that would rename every command. The clone gets a
          new string object and its member is repointed at it.
        """
        m = self.objects[root]["members"]
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
                    if isinstance(self.objects.get(sid), str)
                    and self.objects[sid] == old_text]
            if not hits:
                raise AssetError(
                    "no owned string %r inside the clone of asset %d - it is "
                    "either absent or shared with the rest of the package"
                    % (old_text, root))
            for sid in hits:
                out[sid] = new_text
        return out, retarget

    def _retarget_strings(self, events, pos_map, root, retarget):
        """Point named members of the clone at brand new string objects."""
        if not retarget:
            return
        slots = self.walker.member_slots(root)
        for member, text in sorted(retarget.items()):
            idx = pos_map.get(slots[member])
            if idx is None:
                raise AssetError("member %s is not inside the cloned span" % member)
            if events[idx]["kind"] != "MemberReference":
                raise AssetError(
                    "%s is written inline as %s; repointing it would drop a "
                    "definition the clone still references"
                    % (member, events[idx]["kind"]))
            sid = self.alloc.new(1)
            events.append({"kind": "BinaryObjectString", "object_id": sid,
                           "value": text})
            events[idx] = {"kind": "MemberReference", "idref": sid}

    def _append_events(self, events):
        """Insert new records just before MessageEnd.

        NRBF resolves references by object id once the whole stream is read, so
        a record may be defined after the record that points at it.
        """
        trace = self.b.trace
        for i in range(len(trace) - 1, -1, -1):
            if trace[i]["kind"] == "MessageEnd":
                trace[i:i] = events
                return
        raise AssetError("trace has no MessageEnd to insert before")

    def _append_child(self, lst_id, arr_id, child_id):
        """Add one child to a List<T>: fill a free slot or grow the array."""
        arr_start, arr_end = self.walker.spans[arr_id]
        arr_ev = self.b.trace[arr_start]
        if arr_ev["kind"] != "BinaryArray":
            raise AssetError("collection backing store %d is %s, not a BinaryArray"
                             % (arr_id, arr_ev["kind"]))
        slots = self.walker.member_slots(lst_id)
        size_ev = self.b.trace[slots["_size"]]
        if size_ev["kind"] != "Primitive":
            raise AssetError("List._size is %s, not a Primitive" % size_ev["kind"])
        size = size_ev["value"]
        cap = arr_ev["lengths"][0]

        items_start = arr_start + 1
        elems = _expand_slots(self.b.trace[items_start:arr_end], cap, arr_id)

        new_ref = {"kind": "MemberReference", "idref": child_id}
        if size < cap:
            # .NET over-allocates (capacity 16 behind a size of 15); use the
            # free slot rather than growing.
            elems[size] = new_ref
        else:
            arr_ev["lengths"] = [cap + 1]
            elems.append(new_ref)
        self.b.trace[items_start:arr_end] = elems
        size_ev["value"] = size + 1
        self.b.trace[slots["_version"]]["value"] += 1
        # Spans past this point may have shifted; callers re-parse.
        self.walker = ng.EventWalker(self.b.trace)
        self.walker.verify_full_coverage()


def main():
    if len(sys.argv) < 2:
        print("usage: python3 tools/pkp_asset.py PACKAGE.pkp")
        return 2
    b = pb.PackageBuilder(sys.argv[1])
    g = CommandGraph(b)
    names = g.command_names()
    print("%d commands in the object graph:" % len(names))
    for sn in sorted(names):
        cid = g.commands()[sn]
        kids = [g.name_of(k) for k in g.children(cid)]
        print("   %-26s %-24s %s" % (sn, names[sn], " | ".join(str(k) for k in kids)))
    print("\ncommand collections:")
    for name, lst, arr in g.command_collections():
        size = pb.deref(g.objects, g.objects[lst]["members"]["_size"])
        print("   %-16s list=%-6d array=%-6d size=%s" % (name, lst, arr, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
