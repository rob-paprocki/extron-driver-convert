#!/usr/bin/env python3
"""
test_pkp_asset.py - offline gate for nrbf_graph.py and pkp_asset.py.

Adding an object to a .pkp is the step that had never been taken, so these
tests are about one question: did the edit change EXACTLY what it claimed, and
nothing else? The expensive gate is Global Configurator on a machine this repo
cannot reach, so everything checkable at a desk is checked here first.

Four properties:

  1. The event grammar is right. `EventWalker` must consume every trace in
     samples/ end to end - a wrong grammar drifts, and drift is loud.
  2. A clone is isolated. The donor command, its parameters and its states are
     untouched, and the copy shares no parameter object with the original.
  3. Every other command survives. The 15 the donor shipped are compared
     name-for-name, parameter-for-parameter, state-for-state after the edit.
  4. Guards hold. Renaming a shared string, detaching a non-child, or cloning
     a command whose script name already exists must raise rather than
     silently produce a broken package.
  5. No clone mints a NEGATIVE object id. .NET reserves those for its own
     value-type bookkeeping; a new one makes BinaryFormatter throw and GC drop
     the package from its catalogue silently. Nothing downstream of our own
     parser can see this, so it is asserted directly - see findings/18 s6.

Run: python3 tools/test_pkp_asset.py
"""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)

import pkp_dump as pd            # noqa: E402
import vendor_inputs            # noqa: E402
import pkp_build as pb           # noqa: E402
import pkp_asset as pa           # noqa: E402
import nrbf_graph as ng          # noqa: E402


PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("  %-4s %s%s" % ("ok" if cond else "FAIL", name,
                           "" if cond or not detail else "  <- " + detail))
    return cond


def all_packages():
    out = []
    for root, _dirs, files in os.walk(os.path.join(_ROOT, "samples")):
        for f in files:
            if f.endswith(".pkp"):
                out.append(os.path.join(root, f))
    return sorted(out)


def camera_donor():
    for p in all_packages():
        if os.path.basename(p).startswith("1bynd_19_4743"):
            return p
    raise SystemExit("camera donor 1bynd_19_4743 not found under samples/")


def surface(g):
    """{scriptName: (display name, ((param, class, (states...)), ...))}."""
    out = {}
    for sn, cid in g.commands().items():
        ps = []
        for k in g.children(cid):
            cls = g.objects[k]["class"].split(",")[0].split(".")[-1]
            states = tuple(g.name_of(s) for s in g.children(k)) \
                if cls == "EnumParamAsset" else ()
            ps.append((g.name_of(k), cls, states))
        out[sn] = (g.name_of(cid), tuple(ps))
    return out


# ---------------------------------------------------------------------------

def test_grammar_covers_every_package():
    print("\n[1] the record grammar consumes every sample trace exactly")
    for p in all_packages():
        name = os.path.basename(p)
        try:
            b = pb.PackageBuilder(p)
            w = ng.EventWalker(b.trace)
            w.verify_full_coverage()
            ok = True
            detail = ""
        except Exception as e:
            ok = False
            detail = str(e)[:80]
        check("walk %s" % name, ok, detail)


def test_spans_partition_the_trace():
    print("\n[2] spans nest properly and every object is claimed once")
    b = pb.PackageBuilder(camera_donor())
    w = ng.EventWalker(b.trace)
    w.verify_full_coverage()
    spans = sorted(w.spans.values())
    overlap = 0
    for i in range(1, len(spans)):
        a_s, a_e = spans[i - 1]
        b_s, b_e = spans[i]
        # Properly nested or disjoint - never partially overlapping.
        if b_s < a_e and b_e > a_e:
            overlap += 1
    check("no partially overlapping spans", overlap == 0, "%d overlaps" % overlap)
    check("every span is non-empty", all(e > s for s, e in spans))
    check("object count is plausible", 1000 < len(w.spans) < 3000,
          "%d objects" % len(w.spans))


def test_clone_is_isolated():
    print("\n[3] a cloned command shares nothing mutable with its donor")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    before = surface(g)
    donor_id = g.commands()["Backlight"]
    donor_params = set(g.children(donor_id))

    new_id = g.clone_command("Backlight", "Auto Tracking", "TrackingFraming",
                             description="Start or stop tracking",
                             text_map={"On": "Start", "Off": "Stop"})
    after = surface(g)

    check("command count rose by exactly one",
          len(after) == len(before) + 1, "%d -> %d" % (len(before), len(after)))
    check("the new command is present by script name", "TrackingFraming" in after)
    check("the donor is unchanged", after["Backlight"] == before["Backlight"],
          "%r" % (after["Backlight"],))
    new_params = set(g.children(new_id))
    check("no parameter object is shared with the donor",
          donor_params.isdisjoint(new_params),
          "shared=%s" % sorted(donor_params & new_params))
    check("states were renamed on the copy only",
          after["TrackingFraming"][1][0][2] == ("Start", "Stop"),
          "%r" % (after["TrackingFraming"][1][0],))
    check("donor states still On/Off",
          after["Backlight"][1][0][2] == ("On", "Off"))


def test_every_other_command_survives():
    print("\n[4] adding commands leaves all 15 originals identical")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    before = surface(g)
    for i, (nm, sn) in enumerate([("Auto Tracking", "TrackingFraming"),
                                  ("Menu", "Menu"),
                                  ("Reboot", "Reboot")]):
        g.clone_command("Backlight", nm, sn, text_map={"On": "A%d" % i})
    after = surface(g)
    same = {k: v for k, v in after.items() if k in before}
    check("all 15 originals still present", set(before) <= set(after),
          "lost=%s" % sorted(set(before) - set(after)))
    diff = [k for k in before if before[k] != same.get(k)]
    check("none of them changed in any way", not diff, "changed=%s" % diff)


def test_collections_all_updated():
    print("\n[5] a new command is registered in EVERY command collection")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    n_before = [pb.deref(g.objects, g.objects[l]["members"]["_size"])
                for _n, l, _a in g.command_collections()]
    new_id = g.clone_command("Backlight", "Menu", "Menu", text_map={"On": "Toggle"})
    listed = []
    for _n, lst_id, arr_id in g.command_collections():
        size = pb.deref(g.objects, g.objects[lst_id]["members"]["_size"])
        ids = [pb.ref_id(x) for x in g.objects[arr_id]["items"][:size]]
        listed.append(new_id in ids)
    n_after = [pb.deref(g.objects, g.objects[l]["members"]["_size"])
               for _n, l, _a in g.command_collections()]
    check("there is more than one command collection", len(listed) >= 3,
          "%d" % len(listed))
    check("every collection lists the new command", all(listed), str(listed))
    check("every collection's size grew by one",
          all(b_ + 1 == a_ for b_, a_ in zip(n_before, n_after)),
          "%s -> %s" % (n_before, n_after))


def test_array_growth_beyond_capacity():
    print("\n[6] growth past the donor's spare slot works (capacity 16, size 15)")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    for i in range(4):
        g.clone_command("Backlight", "Extra %d" % i, "Extra%d" % i,
                        text_map={"On": "S%d" % i})
    sizes = []
    caps = []
    for _n, lst_id, arr_id in g.command_collections():
        sizes.append(pb.deref(g.objects, g.objects[lst_id]["members"]["_size"]))
        caps.append(len(g.objects[arr_id]["items"]))
    check("all collections reached 19", sizes == [19] * len(sizes), str(sizes))
    check("capacity grew to hold them", all(c >= 19 for c in caps), str(caps))
    check("output re-parses", len(surface(g)) == 19)


def test_compose_a_shape_the_donor_lacks():
    print("\n[7] parameters compose: a decimal value beside a decimal speed")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    zid = g.clone_command("Zoom", "Zoom Position", "ZoomPosition")
    kids = {g.name_of(k): k for k in g.children(zid)}
    check("the clone starts with the donor's enum Value",
          g.objects[kids["Value"]]["class"].split(",")[0].endswith("EnumParamAsset"))
    g.detach(zid, kids["Value"])
    src = [k for k in g.children(g.commands()["Preset"]) if g.name_of(k) == "Value"][0]
    newval, _ = g.clone_asset(src, name="Value")
    g.attach(zid, newval)
    g.set_range(newval, 0, 16384)
    shape = [(g.name_of(k), g.objects[k]["class"].split(",")[0].split(".")[-1])
             for k in g.children(zid)]
    check("composed shape is Speed+Value, both decimal",
          shape == [("Speed", "DecimalParamAsset"), ("Value", "DecimalParamAsset")],
          str(shape))
    donor_shape = [(g.name_of(k), g.objects[k]["class"].split(",")[0].split(".")[-1])
                   for k in g.children(g.commands()["Zoom"])]
    check("the donor Zoom still has its enum Value",
          donor_shape == [("Speed", "DecimalParamAsset"), ("Value", "EnumParamAsset")],
          str(donor_shape))
    rng = g.objects[newval]["members"]
    check("range was applied",
          pb.deref(g.objects, rng["_max"])["value"] == "16384",
          repr(pb.deref(g.objects, rng["_max"])))


def test_no_new_negative_ids():
    print("\n[8] every id a clone mints is POSITIVE (a negative one kills the package)")
    b = pb.PackageBuilder(camera_donor())
    before = set(ng.EventWalker(b.trace).spans)
    g = pa.CommandGraph(b)
    g.clone_command("Backlight", "Auto Tracking", "TrackingFraming",
                    description="d", text_map={"On": "Start", "Off": "Stop"})
    after = set(ng.EventWalker(b.trace).spans)
    minted = after - before
    check("the clone did mint ids", len(minted) > 20, "%d" % len(minted))
    negatives = sorted(i for i in minted if i < 0)
    # Measured 2026-09-09 against Extron 15.27.0.0: mirroring .NET's negative
    # ids for inline value types makes BinaryFormatter throw "An object cannot
    # be registered twice", LoadFromFile return null, and GC drop the package
    # from its catalogue entirely. Nothing in a pure-Python check sees this -
    # the package parses and validates - so the invariant is asserted directly.
    check("none of them is negative", not negatives,
          "minted negatives: %s" % negatives[:8])
    check("the donor's own negative ids are untouched",
          all(i in after for i in before if i < 0))

    alloc = ng.IdAllocator(ng.EventWalker(b.trace).spans)
    check("IdAllocator ignores the sign of the original",
          alloc.new(-999) > 0 and alloc.new(1) > 0)


def test_guards():
    print("\n[9] unsafe edits raise instead of producing a broken package")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)

    try:
        g.clone_command("Backlight", "Dup", "Backlight")
        ok = False
    except pa.AssetError:
        ok = True
    check("duplicate script name is refused", ok)

    try:
        g.clone_command("NoSuchCommand", "X", "X")
        ok = False
    except pa.AssetError:
        ok = True
    check("unknown donor is refused", ok)

    try:
        g.clone_command("Backlight", "X", "X", text_map={"NotAState": "Y"})
        ok = False
    except pa.AssetError:
        ok = True
    check("renaming a string that is not in the clone is refused", ok)

    cid = g.commands()["Zoom"]
    try:
        g.detach(cid, g.commands()["Preset"])
        ok = False
    except pa.AssetError:
        ok = True
    check("detaching a non-child is refused", ok)


def test_shared_description_not_clobbered():
    print("\n[10] giving one command a description does not describe the other 14")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    desc_before = {sn: pb.deref(g.objects,
                                g.objects[cid]["members"]["CommandAssetBase+_description"])
                   for sn, cid in g.commands().items()}
    g.clone_command("Backlight", "Auto Tracking", "TrackingFraming",
                    description="UNIQUE-MARKER", text_map={"On": "Start", "Off": "Stop"})
    desc_after = {sn: pb.deref(g.objects,
                               g.objects[cid]["members"]["CommandAssetBase+_description"])
                  for sn, cid in g.commands().items()}
    check("the new command has its description",
          desc_after.get("TrackingFraming") == "UNIQUE-MARKER",
          repr(desc_after.get("TrackingFraming")))
    leaked = [k for k, v in desc_after.items()
              if k in desc_before and v != desc_before[k]]
    check("no existing description changed", not leaked, "leaked=%s" % leaked)


def test_output_is_a_loadable_package():
    print("\n[11] the built package re-parses and passes Extron's integrity rule")
    import pkp_validate as pv
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    g.clone_command("Backlight", "Auto Tracking", "TrackingFraming",
                    text_map={"On": "Start", "Off": "Stop"})
    raw = b.build(compress=False)
    parser = pd.PkpParser(raw)
    parser.parse()
    check("output parses", len(parser.objects) > 1400, "%d objects" % len(parser.objects))
    packed = b.build(compress=True)
    check("output is gzip", packed[:2] == b"\x1f\x8b")
    res = pv.validate(packed, on_disk_name="test.pkp")
    check("validator returns Valid", res.code == 0,
          "%s (%s)" % (res.name, res.code))


def test_enum_members():
    print("\n[12] inline enum members read, and write on the copy only")
    b = pb.PackageBuilder(camera_donor())
    g = pa.CommandGraph(b)
    cmds = g.commands()
    cond, attr = "ParamAssetBase+_conditionTypes", "ParamAssetBase+_attributes"
    value = [k for k in g.children(cmds["Preset"]) if g.name_of(k) == "Value"][0]
    speed = [k for k in g.children(cmds["Zoom"]) if g.name_of(k) == "Speed"][0]
    # Preset's Value is only ever sent, so GC offers it in no condition; a
    # clone that should be feedback has to be given a nonzero value.
    check("Preset's Value is not condition-capable", g.enum_member(value, cond) == 0,
          str(g.enum_member(value, cond)))
    check("a Value carries attributes 15 and a qualifier 13",
          (g.enum_member(value, attr), g.enum_member(speed, attr)) == (15, 13),
          str((g.enum_member(value, attr), g.enum_member(speed, attr))))
    check("command attributes read through the same path",
          g.enum_member(cmds["Backlight"], "CommandAssetBase+_attributes") == 51)
    copy, _ = g.clone_asset(value, name="Value")
    g.set_enum_member(copy, cond, 3)
    check("the copy reads back 3", g.enum_member(copy, cond) == 3)
    check("the donor still reads 0", g.enum_member(value, cond) == 0)


def main():
    print("test_pkp_asset.py - offline gate for object-graph synthesis")
    # Every test here reads the sample packages, the camera donor above all;
    # without them the suite would pass on an empty list, so it is skipped.
    vendor_inputs.skip_suite(os.path.join(_ROOT, "samples", "1 Beyond Cameras",
                                          "PTZ-IP12_IP20", "pkp", "1bynd_19_4743_v1_0_1.pkp"))
    for fn in (test_grammar_covers_every_package,
               test_spans_partition_the_trace,
               test_clone_is_isolated,
               test_every_other_command_survives,
               test_collections_all_updated,
               test_array_growth_beyond_capacity,
               test_compose_a_shape_the_donor_lacks,
               test_no_new_negative_ids,
               test_guards,
               test_shared_description_not_clobbered,
               test_output_is_a_loadable_package,
               test_enum_members):
        fn()
    total = len(PASS) + len(FAIL)
    print("\n%d passed, %d failed, %d total" % (len(PASS), len(FAIL), total))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
