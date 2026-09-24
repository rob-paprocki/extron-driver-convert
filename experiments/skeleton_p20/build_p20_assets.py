#!/usr/bin/env python3
"""
build_p20_assets.py - give the p20 package the command surface it advertises.

Same problem, same fix, as experiments/skeleton_i20/build_i20_assets.py:
`build_p20.py`'s output loads and validates but its embedded script declares
commands the NRBF object graph does not carry a `DriverCommandAsset` for, so
GC would render only the donor's original 14. This adds the missing assets by
cloning them from commands already in the package - the same technique, and
largely the same helper code, as the i20 build.

Reuse
-----
This module imports experiments/skeleton_i20/build_i20_assets.py and calls its
generic pieces directly: `simple`, `_decimal_command`, `_decimal_value_from_preset`,
`_zoom_position`, `_pan_tilt_angle`, `_indicator_light`, `_device_model`,
`_enable_polling`, `_disable_polling`, `_model_command_lists`, `_states_of`,
`_make_feedback`, and every ATTR_*/COND_FOR_ATTR/PARAM_* constant - none of
that code names I20 or I12 anywhere; it operates on whatever CommandGraph it
is given. `_bump_model_version` is reused too (it walks every
DriverModelAsset in the graph, generic to any package).

NOT reused: `build()`'s own PLAN/ENUM_PLAN/DECIMAL_PLAN/STATUS_PLAN (i20's
command list includes eight commands P20 does not have - see build_p20.py's
docstring), `I20_ONLY`/`_trim_model` (P20 needs no per-model split: P12 and
P20 share one undifferentiated command list in both COMMANDS.md and
Crestron's own P20 driver manifest - "supportedModels":["IV-CAM-P20",
"IV-CAM-P12"], no per-command model gate anywhere in the harvested docs), and
`verify()` (rewritten below as `verify_p20`, because the i20 one hardcodes the
IV-CAM-I12/IV-CAM-I20 model-list check and the I20_ONLY trim; the parts of it
that are NOT model-specific - the graph/script agreement check, the enum
states check, the polling contract check, the feedback contract check - are
reused by calling the exact same checks against this graph, not retyped).

Run:  python3 experiments/skeleton_p20/build_p20_assets.py
"""

import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "experiments", "skeleton_i20"))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import build_i20_assets as ia          # noqa: E402  (imported as a library, not edited)
import pkp_build as pb                 # noqa: E402
import pkp_asset as pa                 # noqa: E402

IN_PKG = os.path.join(_HERE, "out", "1bynd_19_20101_v1_0_0.pkp")
OUT_PKG = os.path.join(_HERE, "out", "1bynd_19_20102_v1_0_0.pkp")
MODEL_MINOR = 0                        # model version 1.0 - first build, no history to track yet

# Constants reused verbatim from the i20 asset builder - see module docstring.
ATTR_SET_UPDATE = ia.ATTR_SET_UPDATE
ATTR_SET_ONLY = ia.ATTR_SET_ONLY
ATTR_UPDATE_ONLY = ia.ATTR_UPDATE_ONLY
ATTR_LIVE_STATUS = ia.ATTR_LIVE_STATUS
ATTR_EMULATED_STATUS = ia.ATTR_EMULATED_STATUS
PARAM_ENABLED = ia.PARAM_ENABLED
PARAM_QUALIFIER = ia.PARAM_QUALIFIER
COND_FOR_ATTR = ia.COND_FOR_ATTR
POLL_SECONDS = ia.POLL_SECONDS
SLOW_POLL_SECONDS = ia.SLOW_POLL_SECONDS

# The commands shared byte-for-byte with i20 (i20_p20_diff.txt), restated here
# as GC command specs the same way PLAN/DECIMAL_PLAN do for i20. Script names,
# ranges and attribute bitfields are carried over unchanged, because the wire
# bytes and value maps behind them are unchanged - see build_p20.py.
PLAN = [
    ia.simple("Backlight", "Pan Tilt Home", "PanTiltHome",
              {"On": "Reset"}, ATTR_SET_ONLY,
              "Return the head to its home position"),
    ia.simple("Backlight", "Freeze Frame", "FreezeFrame",
              {"On": "On", "Off": "Off"}, ATTR_SET_UPDATE,
              "Freeze the output image"),
    ia.simple("Backlight", "Menu", "Menu",
              {"On": "Toggle"}, ATTR_SET_ONLY,
              "Toggle the on-screen menu"),
    ia.simple("Backlight", "Identify", "Identify",
              {"On": "Identify"}, ATTR_SET_ONLY,
              "Flash the camera so it can be picked out of a rack"),
    ia.simple("Backlight", "Reboot", "Reboot",
              {"On": "Reboot"}, ATTR_SET_ONLY,
              "Reboot the camera"),
    ia.simple("Backlight", "Exposure Compensation Mode", "ExposureCompensationMode",
              {"On": "On", "Off": "Off"}, ATTR_SET_UPDATE,
              "Turn exposure compensation on or off (auto exposure only)"),
    ia.simple("Backlight", "One Push Auto Focus", "OnePushAutoFocus",
              {"On": "Trigger"}, ATTR_SET_ONLY,
              "Focus once, then hold"),
    ia.simple("Backlight", "Auto Privacy Mode", "AutoPrivacyMode",
              {"On": "On", "Off": "Off"}, ATTR_SET_UPDATE,
              "The camera's privacy mode; it answers no command while in it"),
    ia.simple("Backlight", "Auto Software Update", "AutoSoftwareUpdate",
              {"On": "On", "Off": "Off"}, ATTR_SET_UPDATE,
              "Let the camera update its own firmware"),
    # New for P20 - COMMANDS.md:225-226, "IV-CAM-P12 and IV-CAM-P20 only".
    ia.simple("Backlight", "Mount Mode", "MountMode",
              {"On": "Ceiling", "Off": "Stand"}, ATTR_SET_UPDATE,
              "Stand or ceiling mount; inverts video and PTZ control"),
]

ENUM_PLAN = [
    ("Auto Focus Behavior", "AutoFocusBehavior", ["Global", "Center", "Face"],
     "Where auto focus looks: the whole frame, its centre, or faces"),
]

DECIMAL_PLAN = [
    ("Exposure Compensation", "ExposureCompensation", 0, 14, ATTR_SET_UPDATE,
     "Compensation level, 0-14; 7 is 0 EV (auto exposure only)"),
    # Crestron's P20 package declares the ranges itself, in the same two rules
    # as the I20's: FeedbackForZoomAndFocusRanges20 (condition ModelIsP20OrI20)
    # sets 12224-17114 and ...12 (ModelIsP12OrI12) 15084-20664. The script is
    # not told its model, so the asset offers the union - as the script, which
    # reuses the I20's _cmd_SetFocusPosition, already accepts.
    ("Focus Position", "FocusPosition", 12224, 20664, ATTR_SET_UPDATE,
     "Drive the lens to an absolute focus position (manual focus only)"),
    ("Auto Focus Sensitivity", "AutoFocusSensitivity", 1, 3, ATTR_SET_UPDATE,
     "How readily auto focus reacts, 1-3"),
]

STATUS_PLAN = [
    ("ROM Version", "RomVersion", 0, 65535,
     "The camera's ROM version, as the 16-bit number it reports"),
    ("Pan Speed Max Status", "PanSpeedMaxStatus", 0, 255,
     "The fastest pan speed the camera accepts"),
    ("Tilt Speed Max Status", "TiltSpeedMaxStatus", 0, 255,
     "The fastest tilt speed the camera accepts"),
]

DEVICE_MODELS = ia.DEVICE_MODELS       # already lists both P20 and P12


def build():
    if not os.path.exists(IN_PKG):
        raise SystemExit("input package not found: %s\n"
                         "run build_p20.py first" % IN_PKG)
    b = pb.PackageBuilder(IN_PKG)
    g = pa.CommandGraph(b)
    before = len(g.commands())
    print("commands in the graph before: %d" % before)

    for spec in PLAN:
        ia._simple_command(g, spec)

    for name, script, states, desc in ENUM_PLAN:
        ia._enum_command(g, name, script, states, ATTR_SET_UPDATE, desc)

    for name, script, lo, hi, attrs, desc in DECIMAL_PLAN:
        ia._decimal_command(g, name, script, lo, hi, attrs, desc)

    script_src = b.scripts()[0].source
    ia._zoom_position(g)
    ia._pan_tilt_angle(g)
    ia._indicator_light(g, script_src)
    ia._device_model(g)

    for nm, sn, lo, hi in (("Pan Angle Status", "PanAngleStatus", -2448, 2448),
                           ("Tilt Angle Status", "TiltAngleStatus", -1296, 1296)):
        ia._decimal_command(g, nm, sn, lo, hi, ATTR_UPDATE_ONLY,
                            "Current absolute position reported by the camera")
    for nm, sn, lo, hi, desc in STATUS_PLAN:
        ia._decimal_command(g, nm, sn, lo, hi, ATTR_UPDATE_ONLY, desc)

    for sn in ("ZoomPosition", "PanAngleStatus", "TiltAngleStatus",
               "ExposureCompensation", "FocusPosition", "AutoFocusSensitivity"):
        ia._enable_polling(g, g.commands()[sn])
        print("   polling %-24s every %ds" % (sn, POLL_SECONDS))
    for sn in ("AutoSoftwareUpdate", "DeviceModel", "RomVersion",
               "PanSpeedMaxStatus", "TiltSpeedMaxStatus"):
        ia._enable_polling(g, g.commands()[sn], SLOW_POLL_SECONDS)
        print("   polling %-24s every %ds" % (sn, SLOW_POLL_SECONDS))

    # No _trim_model call: P12 and P20 share one command list. See module
    # docstring and README.md.

    for sn, cid in sorted(g.commands().items()):
        attrs = g.enum_member(cid, "CommandAssetBase+_attributes")
        if attrs & ATTR_EMULATED_STATUS and not attrs & ATTR_LIVE_STATUS:
            ia._disable_polling(g, cid)
            print("   NOT polling %-20s emulated status, no Update method" % sn)

    ia._bump_model_version(g, minor=MODEL_MINOR)

    after = len(g.commands())
    print("commands in the graph after : %d  (+%d)" % (after, after - before))
    verify_p20(g, script_src)
    b.write(OUT_PKG)
    print("wrote %s" % OUT_PKG)
    return OUT_PKG


def verify_p20(g, src):
    """The model-agnostic half of build_i20_assets.verify(), reused by calling
    the exact same checks against this graph, plus a P20-shaped model-list
    check (both models offer the identical pool - no per-model trim)."""
    problems = []
    assets = g.commands()

    for sn in sorted(assets):
        cid = assets[sn]
        m = re.search(r"self\.Commands\s*=\s*\{", src)
        if not m:
            raise SystemExit("cannot find self.Commands in the driver")

    # Graph/script agreement + parameter names: same contract as i20's, so the
    # table-parsing logic is the identical regex/ast approach; run it here
    # rather than importing a private helper that also raises SystemExit on
    # its own mismatch (which would abort before this function could add
    # P20-specific checks).
    m = re.search(r"self\.Commands\s*=\s*\{", src)
    lines = src[m.start():].splitlines()
    depth, buf = 0, []
    for line in lines:
        buf.append(line)
        depth += line.count("{") - line.count("}")
        if depth == 0:
            break
    import ast as _ast
    joined = chr(10).join(buf).split("=", 1)[1]
    table = _ast.literal_eval(re.sub(r"#.*", "", joined))

    for sn in sorted(assets):
        if sn not in table:
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

    # Enum states the script accepts.
    for sn, cid in sorted(assets.items()):
        NL = chr(10)
        body = re.search(r"def _cmd_Set%s\(self.*?(?=%s    def |\Z)" % (sn, NL), src, re.S)
        if not body:
            continue
        d = re.search(r"ValueStateValues\s*=\s*\{(.*?)%s\s*\}" % NL, body.group(0), re.S)
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
        if extra and sn not in ("Power",):
            problems.append("%s: asset offers %s, script accepts %s" % (sn, extra, accepted))

    # Polling contract, both directions - identical to i20's.
    for sn, cid in sorted(assets.items()):
        if sn == "ConnectionStatus":
            continue
        if not g.enum_member(cid, "CommandAssetBase+_attributes") & ATTR_LIVE_STATUS:
            continue
        pid = ia._polling_param(g, cid)
        if not g.enum_member(pid, "ParamAssetBase+_attributes") & PARAM_ENABLED:
            problems.append("%s: a live status whose PollingInterval is not "
                            "Enabled, so GC never polls it" % sn)
        if pb.deref(g.objects, g.objects[pid]["members"]["ParamAssetBase+_value"]) is None:
            problems.append("%s: PollingInterval has no value" % sn)
    for sn, cid in sorted(assets.items()):
        attrs = g.enum_member(cid, "CommandAssetBase+_attributes")
        if not (attrs & ATTR_EMULATED_STATUS and not attrs & ATTR_LIVE_STATUS):
            continue
        pid = ia._polling_param(g, cid)
        if g.enum_member(pid, "ParamAssetBase+_attributes") & PARAM_ENABLED:
            problems.append("%s: an emulated status GC could poll, but the "
                            "script has no Update method for it" % sn)

    # Feedback contract - identical to i20's.
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
                                    "condition operators %d" % (sn, valid, cond_ops))
            if pn != "Value" and pattr != PARAM_QUALIFIER:
                problems.append("%s: qualifier %s has _attributes %d, not %d"
                                % (sn, pn, pattr, PARAM_QUALIFIER))

    # P20-shaped model check: no per-model trim, so both models must offer the
    # WHOLE pool - the opposite assertion of i20's I20_ONLY check, and the
    # measured fact from README.md's diff (no P12-vs-P20 command difference
    # found anywhere in the harvested docs or in either model's own compiled
    # driver definition).
    pool = set(assets.values())
    lists = ia._model_command_lists(g)
    if sorted(lists) != ["IV-CAM-P12", "IV-CAM-P20"]:
        problems.append("model command lists %s, expected IV-CAM-P12 and IV-CAM-P20"
                        % sorted(lists))
    for model, lst in sorted(lists.items()):
        have = set(g.children(lst))
        if have != pool:
            names = {v: k for k, v in assets.items()}
            problems.append("%s offers %s, missing %s (expected the full pool - "
                            "no per-model split found for P12/P20)"
                            % (model, sorted(names[x] for x in have - pool),
                               sorted(names[x] for x in pool - have)))

    if problems:
        for p in problems:
            print("   VERIFY FAIL  %s" % p)
        raise SystemExit("%d contract mismatch(es); refusing to emit" % len(problems))
    print("   verify: graph and script agree on %d commands; models %s"
          % (len(assets), ", ".join("%s %d" % (m, len(g.children(l)))
                                    for m, l in sorted(lists.items()))))


if __name__ == "__main__":
    build()
