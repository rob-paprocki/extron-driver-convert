#!/usr/bin/env python3
"""
build_p20_cs.py - the ControlScript half of the p20 driver, mirroring
experiments/skeleton_i20/build_i20_cs.py the way build_p20.py mirrors build_i20.py.

Same donor, same transport correction (both vendors name TCP port 5500 for
BOTH i20 and p20 - see build_i20_cs.py's own header, `TcpTransport` is
declared identically in both packages), same zoom-speed bug fix. Only the
command set differs, and only where the wire diff (i20_p20_diff.txt) found a
real difference: eight I-series-only commands dropped, CAM_MountMode added.

Reuse: imports build_i20_cs and calls `patch_transport`, `patch_import_time`
and `patch_zoom` verbatim (none of the three names I20 or I12 anywhere - they
are facts about the DONOR ControlScript module, shared with build_p20.py's
reasoning for reusing build_i20.patch_zoom), and `verify` verbatim (generic:
parses the derived module, checks Commands-table/Set-Update agreement, refuses
f-strings). `NEW_METHODS`/`NEW_COMMANDS` are cut from build_i20_cs's own
constants the same way build_p20.py cuts build_i20.NEW_METHODS - see
`_p20_methods`/`_p20_commands_table`.

Run: python3 experiments/skeleton_p20/build_p20_cs.py [-o OUTDIR]
"""

import argparse
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_I20 = os.path.join(_ROOT, "experiments", "skeleton_i20")
sys.path.insert(0, _I20)

import build_i20_cs as ic              # noqa: E402  (imported as a library, not edited)
import build_p20 as bp20               # noqa: E402  (_I_ONLY_COMMANDS, _cut)

DONOR_CS = ic.DONOR_CS                 # same standalone ControlScript donor i20 derives from

PatchError = ic.PatchError
_once = ic._once
_newline = ic._newline
_relf = ic._relf
NOTES = []

patch_transport = ic.patch_transport
patch_import_time = ic.patch_import_time
patch_zoom = ic.patch_zoom
verify = ic.verify

_I_ONLY_COMMANDS = bp20._I_ONLY_COMMANDS
_cut = bp20._cut


# --------------------------------------------------------------------------
# CP1 - provenance header
# --------------------------------------------------------------------------
HEADER = '''"""
ControlScript module - Crestron 1 Beyond IV-CAM-p12 / p20

Derived by experiments/skeleton_p20/build_p20_cs.py from Extron's own
onebynd_camera_PTZ_IP12_IP20_v1_0_0_0 module - the SAME donor
experiments/skeleton_i20/build_i20_cs.py derives the i12/i20 module from.

The p20 command bytes come from Crestron's own SchemaVersion 2.0 driver
definition for IV-CAM-P20_IP (experiments/skeleton_p20/p20_wire_table.txt)
and from reference/crestron-visca/COMMANDS.md, not carried over from the i20
module by analogy. See experiments/skeleton_p20/README.md for the full I20/P20
diff and provenance of every command.

USAGE

    from onebynd_camera_IV_CAM_P20_v1_0_0_0 import EthernetClass

    cam = EthernetClass('192.168.1.50', 5500)      # TCP 5500 -- see below
    cam.Set('Power', 'On')
    cam.Set('MountMode', 'Ceiling')
    cam.Update('MountMode')
    print(cam.ReadStatus('MountMode'))

TRANSPORT: TCP port 5500, [PATCH C2] from build_i20_cs.py, reused verbatim -
Crestron's driver definition declares `{"Name": "TcpTransport", "Type":
"Tcp", "Info": {"Port": 5500}}` identically for i20 AND p20. Serial is 9600 bps.

NOT YET RUN ON A PROCESSOR OR AGAINST A P20. Commands are transcriptions of
Crestron's declarative spec for the P20 model specifically, checked
byte-for-byte offline against it.
"""
'''


def patch_header(src):
    anchor = "from extronlib.interface import SerialInterface, EthernetClientInterface"
    _once(src, anchor, "CP1 header")
    nl = _newline(src)
    return src.replace(anchor, _relf(HEADER.rstrip(), nl) + nl + anchor, 1)


# --------------------------------------------------------------------------
# CP3 - Commands table, cut from build_i20_cs.NEW_COMMANDS
# --------------------------------------------------------------------------
def _p20_commands_table():
    kept = []
    for line in ic.NEW_COMMANDS.split("\n"):
        m = re.match(r"\s*'([A-Za-z]+)':", line)
        if m and m.group(1) in _I_ONLY_COMMANDS:
            continue
        kept.append(line)
    lines = list(kept)
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip():
            lines[i] = lines[i].rstrip()
            if lines[i].endswith(","):
                lines[i] = lines[i][:-1]
            break
    return "\n".join(lines)


NEW_COMMANDS_MOUNTMODE = """,
            # [PATCH CP5] CAM_MountMode - P-series only.
            'MountMode': {'Status': {}}"""


def patch_commands_table(src):
    anchor = "            'Zoom': {'Parameters': ['Speed'], 'Status': {}},"
    _once(src, anchor, "CP3 commands table")
    nl = _newline(src)
    blob = _p20_commands_table() + NEW_COMMANDS_MOUNTMODE
    return src.replace(anchor, anchor.rstrip(",") + _relf(blob, nl), 1)


# --------------------------------------------------------------------------
# CP5 - command implementations, cut from build_i20_cs.NEW_METHODS
# --------------------------------------------------------------------------
NEW_METHODS_MOUNTMODE = r'''
    # SetInverted / GetInverted: 81 01/09 04 A4 {Inverted} FF.
    # COMMANDS.md:225-226/287-288 (CAM_MountMode, "IV-CAM-P12 and IV-CAM-P20
    # only"): Stand = 0x02, Ceiling = 0x03. Confirmed directly against P20's
    # own compiled driver, not carried over from i20 (which has no MountMode).
    def SetMountMode(self, value, qualifier):

        ValueStateValues = {
            'Stand':    0x02,
            'Ceiling':  0x03,
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0xA4,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('MountMode', cmdString, value, qualifier)
            self.WriteStatus('MountMode', value, qualifier)
        else:
            self.Discard('Invalid Command for SetMountMode')

    def UpdateMountMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Stand',
            0x03: 'Ceiling',
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0xA4, 0xFF)
        res = self.__UpdateHelper('MountMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('MountMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['MountMode: Invalid/unexpected response'])
'''


def _p20_methods():
    nm = ic.NEW_METHODS
    # TrackingFraming + TrackingMode + TrackingProfile + PresetZone +
    # TrackingShot - contiguous, all removed; ZoomPosition's own comment is
    # the end marker so it is kept intact.
    nm = _cut(nm,
             "    # Reserved presets 80/81. Documented as Start/Pause Tracking.",
             "    # SetZoomPosition: 81 01 04 47")
    # The whole Intelligent Switching (c2) family.
    nm = _cut(nm,
             "    ######################################################\n"
             "    # INTELLIGENT SWITCHING (camera selection)",
             "    ######################################################\n"
             "    # [PATCH C7] PARITY WITH CRESTRON'S I20 DRIVER (v1.6)")
    nm = nm.replace(
        "    # [PATCH C7] PARITY WITH CRESTRON'S I20 DRIVER (v1.6)",
        "    # [PATCH CP7] SHARED WITH THE I20 MODULE (byte-identical templates -\n"
        "    # see experiments/skeleton_p20/i20_p20_diff.txt)")
    return nm.rstrip() + "\n" + NEW_METHODS_MOUNTMODE


def patch_methods(src):
    anchor = "    def __CheckResponseForErrors(self, sourceCmdName, response):"
    _once(src, anchor, "CP5 methods")
    nl = _newline(src)
    return src.replace(anchor, _relf(_p20_methods().rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------

def derive(donor_source):
    src = donor_source
    for fn in (patch_header, patch_transport, patch_import_time,
               patch_commands_table, patch_zoom, patch_methods):
        src = fn(src)
    return src


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    with open(DONOR_CS, encoding="utf-8") as fh:
        donor = fh.read()
    print("donor: %s (%d bytes, shared with build_i20_cs.py)"
          % (os.path.basename(DONOR_CS), len(donor.encode())))

    derived = derive(donor)
    problems = verify(derived)
    if problems:
        print("\nVERIFICATION FAILED - not emitting:")
        for p in problems:
            print("  - %s" % p)
        return 1
    print("  derived module: %d bytes (+%d), verification clean"
          % (len(derived.encode()), len(derived.encode()) - len(donor.encode())))
    for n in NOTES:
        print("    note: %s" % n)

    out = os.path.join(args.outdir, "onebynd_camera_IV_CAM_P20_v1_0_0_0.py")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(derived)
    print("  %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
