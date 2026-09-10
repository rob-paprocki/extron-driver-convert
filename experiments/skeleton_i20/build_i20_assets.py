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
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_build as pb           # noqa: E402
import pkp_asset as pa           # noqa: E402


IN_PKG = os.path.join(_HERE, "out", "1bynd_19_20023_v1_0_0.pkp")
OUT_PKG = os.path.join(_HERE, "out", "1bynd_19_20024_v1_0_0.pkp")

# Attribute bitfields lifted from donor commands of the same character, rather
# than invented: 51 is a Set+Update command with feedback (Backlight, White
# Balance), 3 is Set-only (Zoom, Preset), 35 is Update-only (Connection
# Status). See findings/15 for the observed values.
ATTR_SET_UPDATE = 51
ATTR_SET_ONLY = 3
ATTR_UPDATE_ONLY = 35


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
    simple("Backlight", "Group Tracking", "GroupTracking",
           {"On": "Enable"}, ATTR_SET_ONLY,
           "Track the whole group in frame"),
    simple("Backlight", "Presenter Tracking", "PresenterTracking",
           {"On": "Enable"}, ATTR_SET_ONLY,
           "Track a single presenter"),
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
    ("Camera Output", "CameraOutput", 0, 5, ATTR_SET_UPDATE,
     "Select the camera to output; 0 resumes intelligent switching"),
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

    _zoom_position(g)
    _pan_tilt_angle(g)
    _indicator_light(g)
    _camera_connection_status(g)

    # 20023 and 20024 are otherwise identical in identity - same internal
    # driver name, same two model strings, same version - so Driver Manager
    # would list two entries a person cannot tell apart. Bump the minor so
    # the one with the full command surface is obvious in the UI.
    _bump_model_version(g, minor=2)

    after = len(g.commands())
    print("commands in the graph after : %d  (+%d)" % (after, after - before))
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
    print("   + %-24s %s" % (spec["script"], spec["name"]))


def _decimal_command(g, name, script, lo, hi, attrs, desc):
    cid = g.clone_command("Preset", name, script,
                          description=desc, attributes=attrs)
    for k in g.children(cid):
        if g.name_of(k) == "Action":
            g.detach(cid, k)
    value = [k for k in g.children(cid) if g.name_of(k) == "Value"][0]
    g.set_range(value, lo, hi)
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
    print("   + %-24s Zoom Position  (0-16384, composed)" % "ZoomPosition")


def _pan_tilt_angle(g):
    """Absolute Pan and Tilt, keeping the donor's two speed qualifiers."""
    cid = g.clone_command("PanTilt", "Pan Tilt Angle", "PanTiltAngle",
                          description="Drive the head to an absolute pan and tilt angle",
                          attributes=ATTR_SET_UPDATE)
    for k in g.children(cid):
        if g.name_of(k) == "Value":
            g.detach(cid, k)
    for label, lo, hi in (("Pan", -2448, 2448), ("Tilt", -1296, 1296)):
        p = _decimal_value_from_preset(g, name=label)
        g.attach(cid, p)
        g.set_range(p, lo, hi)
    print("   + %-24s Pan Tilt Angle  (composed)" % "PanTiltAngle")


def _indicator_light(g):
    """Three-state light bar with Color and Brightness enum qualifiers."""
    cid = g.clone_command("Backlight", "Indicator Light", "IndicatorLight",
                          description="Light bar pattern, colour and brightness",
                          attributes=ATTR_SET_ONLY,
                          text_map={"On": "None", "Off": "Half"})
    value_id, states = _states_of(g, cid)
    extra, _ = g.clone_asset(states[0], name="Full")
    g.attach(value_id, extra)

    # Colour and brightness are enums; clone White Balance's Value, which
    # already carries six states, and rename as many as each needs.
    wb = [k for k in g.children(g.commands()["WhiteBalance"])
          if g.name_of(k) == "Value"][0]
    for label, wanted in (("Color", ["Green", "Red", "Blue", "Yellow", "Cyan", "Magenta"]),
                          ("Brightness", ["Off", "Low", "Medium", "High"])):
        p, _ = g.clone_asset(wb, name=label)
        have = g.children(p)
        for sid, new_name in zip(have, wanted):
            g.rename_asset(sid, new_name)
        for sid in have[len(wanted):]:
            g.detach(p, sid)
        g.attach(cid, p)
    print("   + %-24s Indicator Light  (composed)" % "IndicatorLight")


def _camera_connection_status(g):
    """Per-camera connection feedback, addressed by a decimal Camera qualifier."""
    cid = g.clone_command("ConnectionStatus", "Camera Connection Status",
                          "CameraConnectionStatus",
                          description="Connection state of a switched camera input",
                          attributes=ATTR_UPDATE_ONLY)
    cam = _decimal_value_from_preset(g, name="Camera")
    g.attach(cid, cam)
    g.set_range(cam, 2, 5)
    print("   + %-24s Camera Connection Status  (composed)" % "CameraConnectionStatus")


if __name__ == "__main__":
    build()
