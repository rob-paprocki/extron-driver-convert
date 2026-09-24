#!/usr/bin/env python3
"""
build_p20.py - derive a Crestron 1 Beyond IV-CAM-p12/p20 driver from Extron's
own 1 Beyond PTZ-IP12/IP20 package, mirroring experiments/skeleton_i20/build_i20.py
stage for stage.

Reuse, not duplication
-----------------------
This module IMPORTS experiments/skeleton_i20/build_i20.py and calls it rather
than re-deriving the same facts:

  * the donor package (same Extron shipping file, same class)
  * `patch_zoom` (E2, the zoom-speed bug fix) - applied VERBATIM. The defect
    and the fix are properties of Extron's PTZ-IP12/IP20 script, not of which
    Crestron model is being layered on top, so P20 gets the identical patch
    I20 does.
  * the generic helper methods (`_Nibbles`, `_FromNibbles`, `_Signed16`,
    `_PresetOpcode`, `_SharedInquiry`, the inquiry cache) and every command
    implementation the wire diff (i20_p20_diff.txt) found byte-identical
    between the two models - ZoomPosition, PanTiltAngle/PanAngleStatus/
    TiltAngleStatus, PanTiltHome, FreezeFrame, Menu, Identify, Reboot, the
    IndicatorLight lightbar family, and the whole "parity" block
    (ExposureCompensationMode/ExposureCompensation, FocusPosition,
    OnePushAutoFocus, AutoFocusBehavior, AutoFocusSensitivity,
    AutoPrivacyMode, AutoSoftwareUpdate, DeviceModel/RomVersion,
    PanSpeedMaxStatus/TiltSpeedMaxStatus) - these are CUT programmatically out
    of `build_i20.NEW_METHODS`/`NEW_COMMANDS` at build time (see `_cut` and
    `_p20_methods`/`_p20_commands_table` below), not retyped. If i20's wire
    bytes for any of these ever change, this file picks the change up on the
    next run rather than silently drifting from it.

What is NOT reused, and why
----------------------------
Eight I20 commands are cut out entirely: TrackingFraming, TrackingMode
(Group/Presenter tracking), TrackingProfile and PresetZone all recall reserved
VISCA presets that Crestron's own Reserved-Presets.md scopes to
IV-CAM-I12/I20/I12D-B ONLY - no row in that table names a P model, and P20's
own compiled driver definition (p20_wire_table.txt) declares no command that
reaches any of those presets. TrackingShot (presets 0/1, Home/Tracking Shot)
is scoped the same way. The three-command Intelligent Switching (`c2`) family
(CameraOutput/IntelligentSwitching/CameraConnectionStatus) is dropped for the
same reason I12_VS_I20.md already flagged it as shaky even for the I-series:
it comes from documentation, not from either model's own compiled schema, and
P20's own driver declares none of it either.

New for P20: CAM_MountMode (Stand/Ceiling), COMMANDS.md:225-226,287-288,
"IV-CAM-P12 and IV-CAM-P20 only" - and confirmed directly in P20's own
compiled driver (p20_wire_table.txt: GetInverted/SetInverted, `{Header} 09/01
04 A4 {Inverted} FF`). This is the one command family P has that I does not;
see README.md for the full diff.

Deliverable
-----------
The staged `.pkp` files below, in a new id range (201xx) so nothing here
collides with the i20 series (200xx) or any real Extron package. The last
stage, `1bynd_19_20101_v1_0_0.pkp`, carries the derived script only - it has
the same "script says 40-odd commands, graph shows 15" gap build_i20.py's own
output has, closed the same way i20's was: by build_p20_assets.py, which reads
this file's output and adds the missing DriverCommandAsset objects.

Usage: python3 experiments/skeleton_p20/build_p20.py [-o OUTDIR]
"""

import argparse
import ast
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_I20 = os.path.join(_ROOT, "experiments", "skeleton_i20")
sys.path.insert(0, _I20)
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import build_i20                       # noqa: E402  (imported as a library, not edited)
import pkp_build as pb                 # noqa: E402

DONOR = build_i20.DONOR                # same Extron shipping package i20 derives from

PatchError = build_i20.PatchError
_once = build_i20._once
_newline = build_i20._newline
_relf = build_i20._relf

NOTES = []


# --------------------------------------------------------------------------
# P1 - provenance header (P20's own text; the header content itself is
# model-specific, so this is written fresh rather than cut from i20's).
# --------------------------------------------------------------------------
HEADER_NOTE = '''
    ------------------------------------------------------------------
    DERIVED DRIVER - Crestron 1 Beyond IV-CAM-p12 / p20

    Derived by experiments/skeleton_p20/build_p20.py from Extron's own
    1bynd_19_4743 (PTZ-IP12/IP20) package - the SAME donor
    experiments/skeleton_i20/build_i20.py derives the i12/i20 driver from.
    Extron's original code is unchanged except where noted [PATCH].

    The p20 command bytes were resolved from Crestron's SchemaVersion 2.0
    driver definition (Camera_Crestron-1-Beyond_IV-CAM-P20_IP.pkg) by
    experiments/skeleton_p20/resolve_p20.py (which imports
    experiments/skeleton_i20/resolve_visca.py unmodified), cross-checked
    against reference/crestron-visca/COMMANDS.md. Every command implemented
    here that the i12/i20 driver also implements resolves to the IDENTICAL
    byte template on both models - see
    experiments/skeleton_p20/i20_p20_diff.txt, "Shared, byte-identical
    templates" (74 of 77 P20 commands). CAM_MountMode (Stand/Ceiling) is new:
    COMMANDS.md documents it as "IV-CAM-P12 and IV-CAM-P20 only", and it is
    the one command family present in P20's own compiled driver that has no
    I-series counterpart at all.

    NOT YET RUN AGAINST A P20 OR A PROCESSOR. Every added command is a
    transcription of Crestron's declarative spec for THIS model, not carried
    over from the i20 build by analogy. See experiments/skeleton_p20/README.md.
    ------------------------------------------------------------------
'''


def patch_header(src):
    anchor = "    REVISION HISTORY"
    _once(src, anchor, "P1 header")
    nl = _newline(src)
    return src.replace(anchor, _relf(HEADER_NOTE.rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------
# P2 - the zoom-speed defect: build_i20.patch_zoom, reused verbatim.
# --------------------------------------------------------------------------
patch_zoom = build_i20.patch_zoom


# --------------------------------------------------------------------------
# P3/P4 - Commands table + methods, cut from build_i20's constants
# --------------------------------------------------------------------------
# Names removed because Reserved-Presets.md and P20's own compiled driver
# definition agree they do not apply to a P model (see module docstring and
# README.md's diff section).
_I_ONLY_COMMANDS = (
    "TrackingFraming", "TrackingMode", "TrackingProfile", "PresetZone",
    "TrackingShot", "CameraOutput", "IntelligentSwitching",
    "CameraConnectionStatus",
)


def _p20_commands_table():
    """build_i20.NEW_COMMANDS, filtered to the commands P20 actually has."""
    kept = []
    for line in build_i20.NEW_COMMANDS.split("\n"):
        m = re.match(r"\s*'([A-Za-z]+)':", line)
        if m and m.group(1) in _I_ONLY_COMMANDS:
            continue
        kept.append(line)
    text = "\n".join(kept)
    # The filtered list may now end with a comma before the closing text if
    # the last kept line still carries one from being mid-list; the anchor
    # replacement in patch_commands_table appends this whole blob after the
    # donor's last entry, so a trailing comma is only wrong if the LAST
    # non-blank line has one. Strip it.
    lines = [ln for ln in text.split("\n")]
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            lines[i] = lines[i].rstrip()
            if lines[i].endswith(","):
                lines[i] = lines[i][:-1]
            break
    return "\n".join(lines)


NEW_COMMANDS_MOUNTMODE = """,
            # [PATCH P5] CAM_MountMode - P-series only (COMMANDS.md:225-226,
            # "IV-CAM-P12 and IV-CAM-P20 only"; confirmed directly in P20's own
            # compiled driver, GetInverted/SetInverted).
            'MountMode':            {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}}"""


def patch_commands_table(src):
    anchor = ("            'Zoom':                 {'Set': True,   'Update': False,"
              "    'Live': False,  'Emulated': False,  'Parameters': ['Speed'],"
              "                    'Status': {}}")
    _once(src, anchor, "P3 commands table")
    nl = _newline(src)
    blob = _p20_commands_table() + NEW_COMMANDS_MOUNTMODE
    return src.replace(anchor, anchor + _relf(blob, nl), 1)


def _cut(text, start_marker, end_marker):
    """Remove [start_marker, end_marker) from text. Both must appear once."""
    i = text.index(start_marker)
    j = text.index(end_marker, i)
    return text[:i] + text[j:]


NEW_METHODS_MOUNTMODE = r'''
    # Begin MountMode
    ####################################################################################################################
    # Crestron IV-CAM-P20_IP / IV-CAM-P12_IP: SetInverted -> 81 01 04 A4 {Inverted} FF
    #                                          GetInverted -> 81 09 04 A4 FF
    # COMMANDS.md:225-226/287-288 (CAM_MountMode, "IV-CAM-P12 and IV-CAM-P20
    # only"): Stand = 0x02, Ceiling = 0x03 - the ordinary VISCA On/Off pair,
    # not MapBooleanToBinaryOnOff's 01/00. Confirmed directly against P20's
    # own compiled driver (MapInvertedToHex: true->0x03, false->0x02) rather
    # than assumed from the i20 build, since I20/I12 have no MountMode at all.
    def _cmd_SetMountMode(self, value, qualifier):
        """Set Mount Mode
        value: Enum ('Stand'/'Ceiling')
        qualifier: None
        """
        ValueStateValues = {
            'Stand':    0x02,
            'Ceiling':  0x03,
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0xA4,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('MountMode'):
                self.WriteMountMode(value, qualifier, 'Emulated')
                self.__SetHelper('MountMode', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def _cmd_UpdateMountMode(self, value, qualifier):
        """Update Mount Mode
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'Stand',
            0x03: 'Ceiling',
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0xA4, 0xFF)
        res = self.__UpdateHelper('MountMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteMountMode(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['MountMode: Invalid/unexpected response'])

    def WriteMountMode(self, value, qualifier, context):
        self.WriteStatusHelper('MountMode', value, qualifier, context)

    def ReadMountMode(self, qualifier, context):
        return self.ReadStatusHelper('MountMode', qualifier, context)
'''


def _p20_methods():
    """build_i20.NEW_METHODS with the I-series-only command blocks cut out,
    plus MountMode appended. See module docstring for exactly which blocks
    and why; the cut points are the same "# Begin X" / "### [PATCH E..]"
    markers build_i20.py itself uses to organise the file, so a reformat of
    that file that keeps its own structure keeps this working too."""
    nm = build_i20.NEW_METHODS
    # TrackingFraming + TrackingMode (contiguous)
    nm = _cut(nm, "    # Begin TrackingFraming", "    # Begin ZoomPosition")
    # TrackingProfile + PresetZone + TrackingShot (contiguous)
    nm = _cut(nm, "    # Begin TrackingProfile", "### [PATCH E5] LIGHTBAR")
    # The whole Intelligent Switching (c2) family
    nm = _cut(nm, "### [PATCH E6] INTELLIGENT SWITCHING",
              "### [PATCH E7] PARITY WITH CRESTRON'S I20 DRIVER")
    # Re-title the section we kept (its content is unchanged; only the label
    # named the wrong model).
    nm = nm.replace(
        "### [PATCH E7] PARITY WITH CRESTRON'S I20 DRIVER (v1.6)",
        "### [PATCH P7] SHARED WITH THE I20 DRIVER (byte-identical templates -\n"
        "### see experiments/skeleton_p20/i20_p20_diff.txt)")
    return nm.rstrip() + "\n" + NEW_METHODS_MOUNTMODE


def patch_methods(src):
    anchor = "### END AUTO GENERATION OF COMMAND DEF"
    _once(src, anchor, "P4 methods")
    nl = _newline(src)
    return src.replace(anchor, _relf(_p20_methods().rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------
# Verification - build_i20.verify is generic (parses the derived source,
# checks the Commands table and _cmd_ methods agree, rejects f-strings); it
# names no i20-specific facts, so it is reused directly rather than copied.
# --------------------------------------------------------------------------
verify = build_i20.verify


def derive(donor_source):
    src = donor_source
    for fn in (patch_header, patch_zoom, patch_commands_table, patch_methods):
        src = fn(src)
    return src


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    builder = pb.PackageBuilder(DONOR)
    slot = builder.scripts()[0]
    class_name = os.path.splitext(slot.key)[0]
    print("donor: %s (shared with build_i20.py)" % os.path.basename(DONOR))
    print("  round-trips byte-identically, %d bytes" % len(builder.raw))

    derived = derive(slot.source)
    problems = verify(derived, class_name)
    if problems:
        print("\nVERIFICATION FAILED - not emitting:")
        for p in problems:
            print("  - %s" % p)
        return 1
    print("  derived driver: %d bytes (+%d), verification clean"
          % (len(derived.encode()), len(derived.encode()) - len(slot.source.encode())))
    for n in NOTES:
        print("    note: %s" % n)

    driver_path = os.path.join(args.outdir, "driver_p20.py")
    with open(driver_path, "w", encoding="utf-8") as fh:
        fh.write(derived)

    # A fresh id range (201xx): nothing observed under samples/ or corpus/
    # occupies it, and it is distinct from the i20 series (200xx) so nothing
    # collides in a shared driver library.
    b = pb.PackageBuilder(DONOR)
    b.replace_string(358, "IV-CAM-P12")
    b.replace_string(368, "IV-CAM-P20")
    b.replace_script(slot.key, derived)
    out_path = os.path.join(args.outdir, "1bynd_19_20101_v1_0_0.pkp")
    b.write(out_path)
    print("  %-30s %8d bytes  models renamed + p20 driver"
          % (os.path.basename(out_path), os.path.getsize(out_path)))
    for e in b.edits:
        print("      %s" % e)

    print("\nwrote %s" % args.outdir)
    print("next: python3 experiments/skeleton_p20/build_p20_assets.py "
          "(adds the DriverCommandAsset graph nodes GC actually renders)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
