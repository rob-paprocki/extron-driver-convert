#!/usr/bin/env python3
"""
mutate_protocol.py - ROADMAP R26: mutate a protocol asset's inline scalar
fields (`_port`, and an enum-wrapped field like `_compatibility`) inside a
`tools/pkp_build.PackageBuilder` trace, without editing pkp_build.py or
experiments/nrbf_writeback/nrbf_write.py.

Why this needs its own code
----------------------------
`PackageBuilder` (tools/pkp_build.py) only exposes mutation for two record
shapes that carry their own NRBF object id: `replace_script` (an
ArraySinglePrimitive byte payload) and `replace_string` (a
BinaryObjectString). `_port` is neither - it is a bare Int32 written inline
as one of EthernetProtocolAsset's own class members, with no object id of
its own. `_compatibility` is a reference to a *nested* single-field enum
instance (`Extron.Configuration.Contracts.Enumeration.ProtocolCompatibilityFlags`,
one member: `value__`, itself a bare inline Int32) - it does have an object
id (share pkp_build.deref(objs, member_ref)["$ref"] to find it), but that
object's own only member is the same "bare inline primitive" shape as
`_port`.

How the mutation is done
-------------------------
`experiments/nrbf_writeback/nrbf_write.TracingPkpParser` builds two parallel
representations of one parse:
  - `parser.trace`   a NESTED (event, children) tree, exactly one child slot
                      per class member, in member-declaration order (see the
                      chokepoint in `TracingPkpParser._read_object_record`
                      and the primitive-emit path in
                      `TracingPkpParser._read_primitive_value`).
  - `PackageBuilder.trace` (== `nw.parse_and_trace(...)[1]`, i.e.
                      `parser.flat_trace()`) a FLAT list used by
                      `NrbfWriter.write_trace` to serialize back to bytes.

`flat_trace()` is a straight depth-first walk that *appends the same dict
objects* into the flat list - it does not copy them. So a leaf event
(`{"kind": "Primitive", "pt": ..., "value": ...}`) found by walking the
NESTED tree is the exact same Python object that later gets serialized from
the FLAT list. Mutating `leaf["value"]` in place is therefore sufficient;
there is no need to separately locate or edit the flat list.

Each class member contributes exactly ONE entry to its declaring class's
children list, whether that member is a primitive (a bare leaf dict) or a
record (an `(event, children)` tuple) - `PkpParser._read_members` calls
either `_read_primitive_value` (one `_emit`) or `_read_object_record` (one
chokepoint push/pop) per member, never more than one. So
`children[member_names.index(name)]` is reliable.

Both `_port` and an enum's `value__` are fixed-width Int32 (see
KNOWN_UNTYPED_CLASS_FIELDS / write_primitive_value: PT_Int32 is always 4
bytes on the wire), so changing the VALUE in place changes no record's
length and shifts no later byte offset - this class of edit is structurally
even safer than a string edit (which can change length).
"""
import sys
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_TOOLS = os.path.join(_ROOT, "tools")
_NRBF = os.path.join(_ROOT, "experiments", "nrbf_writeback")
for _p in (_TOOLS, _NRBF):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import pkp_dump as pd     # noqa: E402
import pkp_build as pb    # noqa: E402


class MutationError(Exception):
    pass


def _find_class_node(nested, object_id):
    """Recursively search a TracingPkpParser nested trace (a list whose
    items are either bare leaf dicts or (event, children) tuples) for the
    (event, children) tuple whose event carries this NRBF object id.
    Returns None if not found."""
    for item in nested:
        if isinstance(item, tuple):
            event, children = item
            if event.get("object_id") == object_id:
                return event, children
            found = _find_class_node(children, object_id)
            if found is not None:
                return found
    return None


def _leaf_primitive(node_children, index, what):
    if index >= len(node_children):
        raise MutationError("%s: member index %d out of range (%d children)"
                             % (what, index, len(node_children)))
    leaf = node_children[index]
    if not (isinstance(leaf, dict) and leaf.get("kind") == "Primitive"):
        raise MutationError(
            "%s: expected a bare Primitive leaf at index %d, found %r"
            % (what, index, leaf))
    return leaf


def set_inline_int_member(builder, class_object_id, member_name, new_value):
    """Mutate a bare (inline, unwrapped) Int32 class member in place - e.g.
    EthernetProtocolAsset._port or ._udpOutputPort.

    `builder` is a `pkp_build.PackageBuilder` whose donor has already been
    round-trip-verified (that happens in `PackageBuilder.__init__`).
    `class_object_id` is the NRBF object id of the class instance that owns
    `member_name` (e.g. the EthernetProtocolAsset's own object id, as read
    from `builder.objects`).
    """
    node = _find_class_node(builder.parser.trace, class_object_id)
    if node is None:
        raise MutationError("no class node with object_id=%r found in trace"
                             % (class_object_id,))
    event, children = node
    member_names = event.get("member_names")
    if member_names is None or member_name not in member_names:
        raise MutationError("object %r (class %r) has no member %r (has: %s)"
                             % (class_object_id, event.get("name"), member_name,
                                ", ".join(member_names or [])))
    idx = member_names.index(member_name)
    leaf = _leaf_primitive(children, idx,
                            "object %r member %r" % (class_object_id, member_name))
    before = leaf["value"]
    if before == new_value:
        raise MutationError("object %r member %r is already %r - not a mutation"
                             % (class_object_id, member_name, new_value))
    leaf["value"] = new_value
    builder._edits.append("inline-int object=%s member=%s: %r -> %r"
                           % (class_object_id, member_name, before, new_value))
    return before


def set_enum_ref_member(builder, class_object_id, member_name, new_value):
    """Mutate a member that is itself a $ref to a single-field enum instance
    (`{member_name: value__}`, e.g. ProtocolCompatibilityFlags) - e.g.
    EthernetProtocolAsset._compatibility.

    Resolves the ref from `builder.objects` (the ORIGINAL, unmutated parse -
    safe, because this function only ever reads the ref id, never a value,
    from there), then mutates that enum instance's sole `value__` leaf.
    """
    owner = builder.objects.get(class_object_id)
    if not isinstance(owner, dict):
        raise MutationError("no object with id=%r" % (class_object_id,))
    members = owner.get("members", {})
    if member_name not in members:
        raise MutationError("object %r (class %r) has no member %r (has: %s)"
                             % (class_object_id, owner.get("class"), member_name,
                                ", ".join(members)))
    ref = members[member_name]
    enum_id = pb.ref_id(ref)
    if enum_id is None:
        raise MutationError("object %r member %r is not a $ref (got %r) - "
                             "not this function's shape" % (class_object_id, member_name, ref))
    enum_obj = builder.objects.get(enum_id)
    if not (isinstance(enum_obj, dict)
            and list(enum_obj.get("members", {})) == ["value__"]):
        raise MutationError("object %r is not a single-field ('value__') enum "
                             "instance: %r" % (enum_id, enum_obj))

    node = _find_class_node(builder.parser.trace, enum_id)
    if node is None:
        raise MutationError("no class node with object_id=%r (the enum instance) "
                             "found in trace" % (enum_id,))
    event, children = node
    leaf = _leaf_primitive(children, 0,
                            "enum object %r (%s.%s)" % (enum_id, class_object_id, member_name))
    before = leaf["value"]
    if before == new_value:
        raise MutationError("object %r member %r is already %r - not a mutation"
                             % (class_object_id, member_name, new_value))
    leaf["value"] = new_value
    builder._edits.append("enum-ref object=%s member=%s (enum obj=%s): %r -> %r"
                           % (class_object_id, member_name, enum_id, before, new_value))
    return before


def find_protocol_assets_for_model(objs, model):
    """Every concrete protocol-asset dict directly under `model`, keyed by
    NRBF object id. NOT `tools/pkp2cs.find_protocol_asset` - that function's
    own docstring assumes "a DriverModelAsset owns exactly one ProtocolAsset
    child", which this repo's own 1 Beyond PTZ-IP12/IP20 donor violates: its
    model's single `AssetBase\\`1[[IProtocolAsset]]` wrapper node holds TWO
    concrete children (an EthernetProtocolAsset AND a SerialProtocolAsset),
    not one. `pkp2cs.unwrap_generic_wrapper` requires `len(kids) == 1` and
    returns None otherwise, so `pkp2cs.find_protocol_asset` silently returns
    None for both of this donor's models - directly reproducing ROADMAP
    R17's "resolves to None, silently" failure mode, measured here on a
    donor this task already had to load. This function does not share that
    assumption: it walks every wrapper's children (however many) looking for
    a class ending in "ProtocolAsset"."""
    import pkp2cs  # noqa: E402
    out = {}
    for wrapper in pkp2cs.child_collection_items(objs, model):
        if not isinstance(wrapper, dict):
            continue
        candidates = [wrapper]
        cls = wrapper.get("class", "")
        if cls.startswith("Extron.Configuration.Core.Assets.AssetBase`1[["):
            candidates = pkp2cs.child_collection_items(objs, wrapper)
        for c in candidates:
            if isinstance(c, dict) and c.get("class", "").endswith("ProtocolAsset"):
                for oid, v in objs.items():
                    if v is c:
                        out[oid] = c
                        break
    return out


def find_ethernet_protocol_asset(builder, model_name=None):
    """Locate the (object_id, raw dict, model_name) of an EthernetProtocolAsset
    in the donor - the first one found, or the one belonging to `model_name`
    if given."""
    sys.path.insert(0, _TOOLS)
    import pkp2cs  # noqa: E402
    objs = builder.objects
    for oid, v in objs.items():
        if not (isinstance(v, dict) and v.get("class") ==
                "Extron.Configuration.Drivers.DriverModelAsset"):
            continue
        name = pkp2cs.deref(objs, v.get("members", {}).get("AssetBase+_name"))
        if model_name is not None and name != model_name:
            continue
        for poid, proto in find_protocol_assets_for_model(objs, v).items():
            if proto.get("class", "").endswith("EthernetProtocolAsset"):
                return poid, proto, name
    raise MutationError("no EthernetProtocolAsset found (model_name=%r)" % (model_name,))
