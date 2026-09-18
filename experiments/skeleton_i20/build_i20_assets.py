#!/usr/bin/env python3
"""
build_i20_assets.py - give the i20 package the command surface it advertises.

The problem, measured
---------------------
`build_i20.py` produced `1bynd_19_20023`, which loads in Global Configurator
and validates against Extron's own `DriverAssetValidator`. It shows 15
commands. Its embedded script declares 31. GC renders a driver's command
surface from `DriverCommandAsset` objects in the NRBF object graph and never
asks the script what it can do (finding 15, confirmed by GCP screenshot
2026-09-09), so the 17 i20 commands were unreachable code inside a valid file.

This script adds the missing 17 assets, so that the graph and the script agree.

How each command is built
-------------------------
Every asset is CLONED from one Extron shipped in this same package, then
renamed and re-shaped. Nothing is constructed from scratch, so the flag
objects, operator sets and condition types are Extron's own and the only
things that can be wrong are the fields named here.

Where the donor has no command of the right shape - `ZoomPosition` needs a
decimal value with a decimal speed qualifier, and the donor pairs a decimal
speed with an ENUM value - the parameters are composed: clone the closest
command, detach the parameter that does not fit, and graft one cloned from
another command that has the right type.

Run:  python3 experiments/skeleton_i20/build_i20_assets.py
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_build as pb           # noqa: E402
import pkp_asset as pa           # noqa: E402


IN_PKG = os.path.join(_HERE, "out", "1bynd_19_20023_v1_0_0.pkp")
# Every rebuild GC has seen gets a new file name and model version, because a
# GC project that already holds an older build keeps using it. 20025 / v1.3
# made feedback bindable; 20026 / v1.4 makes GC poll it; 20027 / v1.5 tidies
# the command surface (one Tracking Mode instead of two enable-only commands,
# Camera Output 1-5 rather than 0-5).
OUT_PKG = os.path.join(_HERE, "out", "1bynd_19_20027_v1_0_0.pkp")
MODEL_MINOR = 5

# DriverAttributeEnum bits for a live and an emulated status
# (Extron.Configuration.Contracts).
ATTR_LIVE_STATUS = 32
ATTR_EMULATED_STATUS = 16
# ParamAttributeFlags.Enabled.
PARAM_ENABLED = 1
# Seconds, as on every command GC polls in the donor and in pana_19_5702.
POLL_SECONDS = 3

# Attribute bitfields lifted from donor commands of the same character, rather
# than invented: 51 is a Set+Update command with feedback (Backlight, White
# Balance), 3 is Set-only (Zoom, Preset), 35 is Update-only (Connection
# Status). See findings/15 for the observed values.
ATTR_SET_UPDATE = 51
ATTR_SET_ONLY = 3
ATTR_UPDATE_ONLY = 35
# 19 is Set-only with an EMULATED status and no live one: the command can be
# shown on a button that lights, but GC must never poll it, because the script
# has no Update method to answer. Extron's own example in this package is
# User Defined String, whose Value carries condition type 2 (Emulation) where
# a live status carries 1 and a command with both carries 3.
ATTR_SET_EMULATED = 19

# A command's feedback flag is not enough for GC to offer its value as a
# status: the Value parameter's own ParamAssetBase+_conditionTypes must be
# nonzero too. Extron's feedback values carry 3 on Set+Update commands and 1
# on Update-only ones (pana_19_5702 ZoomPosition, PanPositionStatus;
# 7th_29_17052 PresetResult). Preset's Value, the donor for every decimal
# here, carries 0 because it is only ever sent, so its clones could be
# pressed but never shown on a label until this was set.
COND_FOR_ATTR = {ATTR_SET_UPDATE: 3, 59: 3, ATTR_UPDATE_ONLY: 1,
                 ATTR_SET_EMULATED: 2}

# ParamAssetBase+_attributes: 15 on a command's Value, 13 on a qualifier
# (Extron's own Speed and 7th_29_17052 PresetResult's Preset). A qualifier
# cloned from a Value keeps 15, and GC then offers no way to choose it.
PARAM_VALUE = 15
PARAM_QUALIFIER = 13


def _polling_param(g, command_id):
    return pb.ref_id(g.objects[command_id]["members"]["PollingInterval"])


def _enable_polling(g, command_id, seconds=POLL_SECONDS):
    """Make GC poll a live status.

    GC's compiler polls a command only if CommandAssetExtensions.HasPollingValue
    holds: its PollingInterval parameter exists, carries ParamAttributeFlags
    .Enabled, and has a value (Extron.Configuration.Core, read with ildasm on
    2026-09-15). Preset, Zoom and ConnectionStatus are never polled, so every
    status cloned from them had Enabled clear (attributes 12) and the processor
    never asked for it. Extron's polled statuses carry 13 and 3 seconds.
    """
    pid = _polling_param(g, command_id)
    attr = g.enum_member(pid, "ParamAssetBase+_attributes")
    g.set_enum_member(pid, "ParamAssetBase+_attributes", attr | PARAM_ENABLED)
    slots = g.walker.member_slots(pid)
    for member in ("ParamAssetBase+_value", "ParamAssetBase+_defaultValue"):
        ev = g.b.trace[slots[member]]
        if ev["kind"] != "MemberPrimitiveTyped":
            raise SystemExit("%s of polling interval %d is %s, not a decimal"
                             % (member, pid, ev["kind"]))
        ev["value"] = str(seconds)
    g._reparse()


def _disable_polling(g, command_id):
    """Stop GC polling a command the script cannot answer.

    The mirror of the rule above, and it matters as soon as a Set-only command
    is given an emulated status: once GC can bind it, GC can also poll it, and
    a clone of a polled donor carries Enabled. The script has no Update method
    for such a command, so the poll would raise on the processor. Extron's own
    attributes-19 command, User Defined String, carries 12 - not Enabled.
    """
    pid = _polling_param(g, command_id)
    attr = g.enum_member(pid, "ParamAssetBase+_attributes")
    g.set_enum_member(pid, "ParamAssetBase+_attributes", attr & ~PARAM_ENABLED)


def _make_feedback(g, param_id, attrs):
    """Let GC offer a decimal Value as a status, the way Extron's own do.

    Two members gate it. `_conditionTypes` must be nonzero, and
    `_validOperators` must carry the condition operators: GC lists a status
    with `_validOperators` 1 but offers no comparison for it, so a label or
    monitor still has nothing to bind (2026-09-14, on 20024). Extron's values
    are the condition operators alone on an Update-only command
    (pana_19_5702 PanPositionStatus: 282001408) and action | condition on a
    Set+Update one (ZoomPosition: 7 | 282001408 = 282001415).
    """
    g.set_enum_member(param_id, "ParamAssetBase+_conditionTypes", COND_FOR_ATTR[attrs])
    cond_ops = g.enum_member(param_id, "ParamAssetBase+_conditionOperators")
    act_ops = g.enum_member(param_id, "ParamAssetBase+_actionOperators")
    valid = cond_ops if attrs == ATTR_UPDATE_ONLY else (cond_ops | act_ops)
    g.set_enum_member(param_id, "ParamAssetBase+_validOperators", valid)


def simple(donor, name, script, states, attrs, description=None):
    """A command whose only parameter is the donor's enum Value, restated."""
    return {"kind": "simple", "donor": donor, "name": name, "script": script,
            "states": states, "attrs": attrs, "description": description}


# Every state name here comes from the embedded script's own docstring, so the
# asset's enum and the Python that answers it cannot disagree.
PLAN = [
    simple("Backlight", "Auto Tracking", "TrackingFraming",
           {"On": "Start", "Off": "Stop"}, ATTR_SET_UPDATE,
           "Start or stop automatic subject tracking"),
    # One setting, two values. Until 20027 this was two commands with one
    # value each, so a button could latch either on and release neither.
    simple("Backlight", "Tracking Mode", "TrackingMode",
           {"On": "Group", "Off": "Presenter"}, ATTR_SET_EMULATED,
           "Frame the whole group, or a single presenter"),
    simple("Backlight", "Pan Tilt Home", "PanTiltHome",
           {"On": "Reset"}, ATTR_SET_ONLY,
           "Return the head to its home position"),
    simple("Backlight", "Freeze Frame", "FreezeFrame",
           {"On": "On", "Off": "Off"}, ATTR_SET_UPDATE,
           "Freeze the output image"),
    simple("Backlight", "Menu", "Menu",
           {"On": "Toggle"}, ATTR_SET_ONLY,
           "Toggle the on-screen menu"),
    simple("Backlight", "Identify", "Identify",
           {"On": "Identify"}, ATTR_SET_ONLY,
           "Flash the camera so it can be picked out of a rack"),
    simple("Backlight", "Tracking Shot", "TrackingShot",
           {"On": "Home", "Off": "Tracking"}, ATTR_SET_ONLY,
           "Choose the shot the tracker returns to"),
    simple("Backlight", "Intelligent Switching", "IntelligentSwitching",
           {"On": "Resume", "Off": "Pause"}, ATTR_SET_ONLY,
           "Resume or pause the camera's internal auto-switching"),
    simple("Backlight", "Reboot", "Reboot",
           {"On": "Reboot"}, ATTR_SET_ONLY,
           "Reboot the camera"),
]

# Commands whose value is a number, built from Preset (enum Action + decimal
# Value) by dropping the Action.
DECIMAL_PLAN = [
    ("Tracking Profile", "TrackingProfile", 1, 4, ATTR_SET_ONLY,
     "Select one of the four stored tracking profiles"),
    ("Preset Zone", "PresetZone", 1, 4, ATTR_SET_ONLY,
     "Select one of the four preset zones"),
    # 1, not 0: value 0 sends the same frame as Intelligent Switching Resume,
    # which already offers it by name.
    ("Camera Output", "CameraOutput", 1, 5, ATTR_SET_UPDATE,
     "Select the camera to output"),
]


def build():
    if not os.path.exists(IN_PKG):
        raise SystemExit("input package not found: %s\n"
                         "run build_i20.py first" % IN_PKG)
    b = pb.PackageBuilder(IN_PKG)
    g = pa.CommandGraph(b)
    before = len(g.commands())
    print("commands in the graph before: %d" % before)

    for spec in PLAN:
        _simple_command(g, spec)

    for name, script, lo, hi, attrs, desc in DECIMAL_PLAN:
        _decimal_command(g, name, script, lo, hi, attrs, desc)

    script_src = b.scripts()[0].source
    _zoom_position(g)
    _pan_tilt_angle(g)
    _indicator_light(g, script_src)
    _camera_connection_status(g)

    # Position feedback, split in two because one VISCA inquiry returns both
    # numbers and a GC command carries one Value. Extron does the same in
    # pana_19_5702 (PanPositionStatus / TiltPositionStatus).
    for nm, sn, lo, hi in (("Pan Angle Status", "PanAngleStatus", -2448, 2448),
                           ("Tilt Angle Status", "TiltAngleStatus", -1296, 1296)):
        _decimal_command(g, nm, sn, lo, hi, ATTR_UPDATE_ONLY,
                         "Current absolute position reported by the camera")

    # 20023 and 20024 are otherwise identical in identity - same internal
    # driver name, same two model strings, same version - so Driver Manager
    # would list two entries a person cannot tell apart. Bump the minor so
    # the one with the full command surface is obvious in the UI.
    # Live statuses whose donor was never polled.
    for sn in ("ZoomPosition", "CameraOutput", "CameraConnectionStatus",
               "PanAngleStatus", "TiltAngleStatus"):
        _enable_polling(g, g.commands()[sn])
        print("   polling %-24s every %ds" % (sn, POLL_SECONDS))

    # Emulated status, no live one: bindable, but GC must never poll it.
    for sn, cid in sorted(g.commands().items()):
        attrs = g.enum_member(cid, "CommandAssetBase+_attributes")
        if attrs & ATTR_EMULATED_STATUS and not attrs & ATTR_LIVE_STATUS:
            _disable_polling(g, cid)
            print("   NOT polling %-20s emulated status, no Update method" % sn)

    _bump_model_version(g, minor=MODEL_MINOR)

    after = len(g.commands())
    print("commands in the graph after : %d  (+%d)" % (after, after - before))
    verify(g, script_src)
    b.write(OUT_PKG)
    print("wrote %s" % OUT_PKG)
    return OUT_PKG


def _bump_model_version(g, minor):
    """Set every DriverModelAsset's version minor, so GC can distinguish builds."""
    import pkp_dump as _pd            # noqa: F401  (kept for symmetry)
    models = [oid for oid, v in g.objects.items()
              if isinstance(v, dict)
              and v.get("class", "").split(",")[0]
              == "Extron.Configuration.Drivers.DriverModelAsset"]
    for oid in models:
        ver_id = pb.ref_id(g.objects[oid]["members"]["_ver"])
        slots = g.walker.member_slots(ver_id)
        ev = g.b.trace[slots["_Minor"]]
        if ev["kind"] != "Primitive":
            raise SystemExit("version _Minor is %s, not a Primitive" % ev["kind"])
        ev["value"] = minor
    g._reparse()
    print("   model version minor -> %d on %d models" % (minor, len(models)))


def verify(g, src):
    """Refuse to emit unless the asset tree and the script agree.

    Both halves of the contract are checkable here, and both have already been
    wrong once:

      * a command in the graph with no `self.Commands` entry is a control GC
        draws and the driver ignores;
      * an enum state the script does not accept is an option that silently
        Discards - the first build offered Blue, Cyan, Magenta, Low and High,
        none of which the lightbar code knows;
      * a parameter name mismatch means GC sends a qualifier key the script
        never reads.
    """
    import ast

    m = re.search(r"self\.Commands\s*=\s*\{", src)
    if not m:
        raise SystemExit("cannot find self.Commands in the driver")
    lines = src[m.start():].splitlines()
    depth = 0
    buf = []
    for line in lines:
        buf.append(line)
        depth += line.count("{") - line.count("}")
        if depth == 0:
            break
    joined = chr(10).join(buf).split("=", 1)[1]
    table = ast.literal_eval(re.sub(r"#.*", "", joined))

    problems = []
    assets = g.commands()

    for sn in sorted(assets):
        if sn not in table:
            # ConnectionStatus is an asset with no script entry in Extron's own
            # donor - the framework answers it - so it is not an error.
            if sn != "ConnectionStatus":
                problems.append("%s: in the graph, not in self.Commands" % sn)
            continue
        params = [g.name_of(k) for k in g.children(assets[sn]) if g.name_of(k) != "Value"]
        declared = table[sn].get("Parameters") or []
        if sorted(params) != sorted(declared):
            problems.append("%s: asset params %s vs script Parameters %s"
                            % (sn, params, declared))

    for sn in sorted(table):
        if sn not in assets:
            problems.append("%s: in self.Commands, not in the graph" % sn)

    # Enum states the script actually accepts, where it says so plainly.
    for sn, cid in sorted(assets.items()):
        NL = chr(10)
        body = re.search(r"def _cmd_Set%s\(self.*?(?=%s    def |\Z)" % (sn, NL),
                         src, re.S)
        if not body:
            continue
        d = re.search(r"ValueStateValues\s*=\s*\{(.*?)%s\s*\}" % NL,
                      body.group(0), re.S)
        accepted = re.findall(r"'([^']+)'\s*:", d.group(1)) if d else None
        if accepted is None:
            lit = re.search(r"value in \[([^\]]+)\]", body.group(0))
            accepted = re.findall(r"'([^']+)'", lit.group(1)) if lit else None
        if not accepted:
            continue
        value = [k for k in g.children(cid) if g.name_of(k) == "Value"]
        if not value:
            continue
        states = [g.name_of(x) for x in g.children(value[0])]
        if not states:
            continue
        extra = sorted(set(states) - set(accepted))
        # A state the script does not Set can still be status-only - Extron's
        # own Power carries 'Internal Power Circuit Error' that way - so this
        # is only an error for commands we added.
        if extra and sn not in ("Power",):
            problems.append("%s: asset offers %s, script accepts %s"
                            % (sn, extra, accepted))

    # Feedback GC polls: HasPollingValue must hold for every live status. The
    # donor's own ConnectionStatus is answered by the framework, not polled.
    for sn, cid in sorted(assets.items()):
        if sn == "ConnectionStatus":
            continue
        if not g.enum_member(cid, "CommandAssetBase+_attributes") & ATTR_LIVE_STATUS:
            continue
        pid = _polling_param(g, cid)
        if not g.enum_member(pid, "ParamAssetBase+_attributes") & PARAM_ENABLED:
            problems.append("%s: a live status whose PollingInterval is not "
                            "Enabled, so GC never polls it" % sn)
        if pb.deref(g.objects, g.objects[pid]["members"]["ParamAssetBase+_value"]) is None:
            problems.append("%s: PollingInterval has no value" % sn)

    # And the mirror of it. A command with an emulated status but no live one
    # has no Update method in the script, so a poll would raise on the
    # processor - and it only became reachable when such a command was first
    # made bindable, because GC cannot poll what nothing can bind.
    for sn, cid in sorted(assets.items()):
        attrs = g.enum_member(cid, "CommandAssetBase+_attributes")
        if not (attrs & ATTR_EMULATED_STATUS and not attrs & ATTR_LIVE_STATUS):
            continue
        pid = _polling_param(g, cid)
        if g.enum_member(pid, "ParamAssetBase+_attributes") & PARAM_ENABLED:
            problems.append("%s: an emulated status GC could poll, but the "
                            "script has no Update method for it" % sn)

    # Feedback GC can bind: a command flagged for feedback needs a Value that
    # is condition-capable, and every other parameter must be a qualifier.
    for sn, cid in sorted(assets.items()):
        want = COND_FOR_ATTR.get(g.enum_member(cid, "CommandAssetBase+_attributes"))
        if want is None:
            continue
        for k in g.children(cid):
            pn = g.name_of(k)
            cond = g.enum_member(k, "ParamAssetBase+_conditionTypes")
            pattr = g.enum_member(k, "ParamAssetBase+_attributes")
            if pn == "Value" and not cond:
                problems.append("%s: Value has _conditionTypes 0, so GC offers "
                                "no status to bind (want %d)" % (sn, want))
            if pn == "Value":
                cond_ops = g.enum_member(k, "ParamAssetBase+_conditionOperators")
                valid = g.enum_member(k, "ParamAssetBase+_validOperators")
                if valid & cond_ops != cond_ops:
                    problems.append("%s: Value's _validOperators %d lacks its "
                                    "condition operators %d, so GC offers no "
                                    "comparison" % (sn, valid, cond_ops))
            if pn != "Value" and pattr != PARAM_QUALIFIER:
                problems.append("%s: qualifier %s has _attributes %d, not %d"
                                % (sn, pn, pattr, PARAM_QUALIFIER))

    if problems:
        for p in problems:
            print("   VERIFY FAIL  %s" % p)
        raise SystemExit("%d contract mismatch(es); refusing to emit" % len(problems))
    print("   verify: graph and script agree on %d commands" % len(assets))


# -- builders ---------------------------------------------------------------

def _states_of(g, command_id):
    value = [k for k in g.children(command_id) if g.name_of(k) == "Value"]
    if not value:
        raise SystemExit("command %d has no Value parameter" % command_id)
    return value[0], g.children(value[0])


def _simple_command(g, spec):
    """Clone Backlight, rename its two states, and drop one if unused."""
    cid = g.clone_command(spec["donor"], spec["name"], spec["script"],
                          description=spec["description"],
                          attributes=spec["attrs"],
                          text_map=spec["states"])
    # A single-state command (Enable, Reboot, Identify) needs the donor's
    # second state removed, not merely renamed.
    if len(spec["states"]) == 1:
        value_id, states = _states_of(g, cid)
        keep = list(spec["states"].values())[0]
        for sid in states:
            if g.name_of(sid) != keep:
                g.detach(value_id, sid)
    # The Backlight donor is a Set+Update command, so its Value already carries
    # the condition type and operators a live status needs, and the Set+Update
    # clones inherit them correctly. An emulated-only status is the one shape
    # the donor cannot supply: it needs condition type 2 (Emulation) where the
    # donor has 3. Only that case is rewritten, so every command that already
    # works on hardware keeps the exact members it has today.
    if spec["attrs"] == ATTR_SET_EMULATED:
        value_id = _states_of(g, cid)[0]
        _make_feedback(g, value_id, spec["attrs"])
    print("   + %-24s %s" % (spec["script"], spec["name"]))


def _decimal_command(g, name, script, lo, hi, attrs, desc):
    cid = g.clone_command("Preset", name, script,
                          description=desc, attributes=attrs)
    for k in g.children(cid):
        if g.name_of(k) == "Action":
            g.detach(cid, k)
    value = [k for k in g.children(cid) if g.name_of(k) == "Value"][0]
    g.set_range(value, lo, hi)
    if attrs in COND_FOR_ATTR:
        _make_feedback(g, value, attrs)
    print("   + %-24s %s  (%s-%s)" % (script, name, lo, hi))


def _decimal_value_from_preset(g, name="Value"):
    """A fresh DecimalParamAsset, cloned from Preset's numeric Value."""
    src = [k for k in g.children(g.commands()["Preset"])
           if g.name_of(k) == "Value"][0]
    new_id, _ = g.clone_asset(src, name=name)
    return new_id


def _zoom_position(g):
    """Decimal position 0-16384 with the donor's decimal Speed qualifier."""
    cid = g.clone_command("Zoom", "Zoom Position", "ZoomPosition",
                          description="Drive the lens to an absolute zoom position",
                          attributes=ATTR_SET_UPDATE)
    for k in g.children(cid):
        if g.name_of(k) == "Value":
            g.detach(cid, k)
    value = _decimal_value_from_preset(g)
    g.attach(cid, value)
    g.set_range(value, 0, 16384)
    _make_feedback(g, value, ATTR_SET_UPDATE)
    print("   + %-24s Zoom Position  (0-16384, composed)" % "ZoomPosition")


def _pan_tilt_angle(g):
    """Absolute Pan and Tilt, keeping the donor's two speed qualifiers."""
    # Set-only. Extron's own absolute-position command (pana_19_5702's
    # PanTiltAbsolutePosition) is Set:True/Update:False for the same reason:
    # with no Value parameter there is nothing for feedback to land in.
    cid = g.clone_command("PanTilt", "Pan Tilt Angle", "PanTiltAngle",
                          description="Drive the head to an absolute pan and tilt angle",
                          attributes=ATTR_SET_ONLY)
    for k in g.children(cid):
        if g.name_of(k) == "Value":
            g.detach(cid, k)
    for label, lo, hi in (("Pan", -2448, 2448), ("Tilt", -1296, 1296)):
        p = _decimal_value_from_preset(g, name=label)
        g.attach(cid, p)
        g.set_range(p, lo, hi)
    print("   + %-24s Pan Tilt Angle  (composed)" % "PanTiltAngle")


def _lightbar_states(script_src, const):
    """The keys of a lightbar constant, read from the driver's own source.

    Hardcoding these once already shipped an asset offering Blue, Cyan,
    Magenta, Low and High - none of which the script accepts, so GC would have
    drawn five options that silently Discard. Read them instead.
    """
    m = re.search(r"%s\s*=\s*\{(.*?)\}" % const, script_src, re.S)
    if not m:
        raise SystemExit("cannot find %s in the embedded driver" % const)
    keys = re.findall(r"'([^']+)'\s*:", m.group(1))
    if not keys:
        raise SystemExit("%s parsed but is empty" % const)
    return keys


def _indicator_light(g, script_src):
    """Three-state light bar with Color and Brightness enum qualifiers."""
    cid = g.clone_command("Backlight", "Indicator Light", "IndicatorLight",
                          description="Light bar pattern, colour and brightness",
                          attributes=ATTR_SET_ONLY,
                          text_map={"On": "None", "Off": "Half"})
    value_id, states = _states_of(g, cid)
    extra, _ = g.clone_asset(states[0], name="Full")
    g.attach(value_id, extra)

    # Colour and brightness are enums; clone White Balance's Value, which
    # already carries six states, and keep as many as each needs.
    wb = [k for k in g.children(g.commands()["WhiteBalance"])
          if g.name_of(k) == "Value"][0]
    for label, const in (("Color", "_LIGHTBAR_COLOURS"),
                         ("Brightness", "_LIGHTBAR_BRIGHTNESS")):
        wanted = _lightbar_states(script_src, const)
        p, _ = g.clone_asset(wb, name=label)
        have = g.children(p)
        if len(wanted) > len(have):
            raise SystemExit("%s needs %d states, donor enum has %d"
                             % (label, len(wanted), len(have)))
        for sid, new_name in zip(have, wanted):
            g.rename_asset(sid, new_name)
        for sid in have[len(wanted):]:
            g.detach(p, sid)
        g.attach(cid, p)
        print("   + %-24s %s %s" % ("IndicatorLight", label, wanted))


def _camera_connection_status(g):
    """Per-camera connection feedback, addressed by a decimal Camera qualifier."""
    cid = g.clone_command("ConnectionStatus", "Camera Connection Status",
                          "CameraConnectionStatus",
                          description="Connection state of a switched camera input",
                          attributes=ATTR_UPDATE_ONLY)
    cam = _decimal_value_from_preset(g, name="Camera")
    g.attach(cid, cam)
    g.set_range(cam, 2, 5)
    g.set_enum_member(cam, "ParamAssetBase+_attributes", PARAM_QUALIFIER)
    print("   + %-24s Camera Connection Status  (composed)" % "CameraConnectionStatus")


if __name__ == "__main__":
    build()
