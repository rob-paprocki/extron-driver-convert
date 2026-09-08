#!/usr/bin/env python3
"""
build_i20_cs.py - the ControlScript half of the i20 driver.

Same derivation as build_i20.py, different target. build_i20.py produces the
driver embedded inside a .pkp, which Global Configurator loads; this produces a
standalone ControlScript module, which a Python project on an IPCP Pro imports
directly. Both drive the same camera with the same bytes.

Why this is not just the same file twice
----------------------------------------
The two forms are structurally different, and the difference is the whole
reason STATUS.md asks whether a shared intermediate representation is
justified:

                        .pkp embedded              ControlScript module
    base class          Extron2.BaseDriver         bare DeviceClass
    command methods     _cmd_SetX / _cmd_UpdateX   SetX / UpdateX
    status contexts     Live + Emulated            one status tree
    guard               __SafeToSet(command)       none
    set helper          5 args (+queryDisallowTime) 4 args
    status write        WriteStatusHelper(c,v,q,ctx) WriteStatus(c,v,q)
    transports          declared in the package    3 classes in the file

The *wire table* is identical across both. That is the finding: what differs
between Extron's two driver forms is host plumbing, not protocol - so one
extraction can feed both emitters, and `test_i20_cs_wire.py` holds them to the
same byte expectations to keep that true.

Deliverable
-----------
`out/onebynd_camera_IV_CAM_I20_v1_0_0_0.py` - drop into a ControlScript
project, instantiate `EthernetClass(ip, 5500)`, call `.Set('TrackingFraming',
'Start')`. Needs no Global Configurator, no catalogue rebuild, and no driver
library - which makes it the shortest path to a camera actually moving.

Usage: python3 experiments/skeleton_i20/build_i20_cs.py [-o OUTDIR]
"""

import argparse
import ast
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, _HERE)

import build_i20                      # noqa: E402  (shared patch helpers)

DONOR_CS = os.path.join(
    _ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "Controlscript",
    "onebynd_camera_PTZ_IP12_IP20_v1_0_0_0.py")

NOTES = []

PatchError = build_i20.PatchError
_once = build_i20._once
_newline = build_i20._newline
_relf = build_i20._relf


# --------------------------------------------------------------------------
# C1 - provenance header
# --------------------------------------------------------------------------
HEADER = '''"""
ControlScript module - Crestron 1 Beyond IV-CAM-i12 / i20

Derived by experiments/skeleton_i20/build_i20_cs.py from Extron's own
onebynd_camera_PTZ_IP12_IP20_v1_0_0_0 module. Extron's code is unchanged
except where marked [PATCH].

The i20 command bytes come from Crestron's own SchemaVersion 2.0 driver
definition and from Crestron's published VISCA documentation - not from a
generic VISCA reference. See findings/13-i20-synthesis.md.

USAGE

    from onebynd_camera_IV_CAM_I20_v1_0_0_0 import EthernetClass

    cam = EthernetClass('192.168.1.50', 5500)      # TCP 5500 -- see below
    cam.Set('Power', 'On')
    cam.Set('TrackingFraming', 'Start')
    cam.Set('IndicatorLight', 'Full', {'Color': 'Red', 'Brightness': 'Bright'})
    cam.Update('TrackingFraming')                  # -> 'Start' / 'Stop'
    print(cam.ReadStatus('TrackingFraming'))

TRANSPORT: TCP port 5500. Three independent sources agree:
  - Crestron's driver definition for both i20 and p20:
        {"Name": "TcpTransport", "Type": "Tcp", "Info": {"Port": 5500}}
  - Crestron's VISCA documentation: "By default, the port for TCP control is
    set to 5500."
  - Extron's own driver header: "Manufacturer confirmed ethernet control uses
    UDP port 5500", later corrected by revision 1_0_1 -- "Changed ethernet to
    TCP based on testing. DR# 62249".

So both vendors independently name port 5500, and both converged on TCP after
initially documenting UDP. [PATCH C2] changes this module's EthernetClass
default from UDP to TCP accordingly; the module predates Extron's own
correction. Serial is 9600 bps.

UNVERIFIED ON HARDWARE. No i20 was available to this repo. Commands are
transcriptions of Crestron's declarative spec, checked byte-for-byte offline
against it, never observed on a wire.
"""
'''


def patch_header(src):
    anchor = "from extronlib.interface import SerialInterface, EthernetClientInterface"
    _once(src, anchor, "C1 header")
    nl = _newline(src)
    return src.replace(anchor, _relf(HEADER.rstrip(), nl) + nl + anchor, 1)


# --------------------------------------------------------------------------
# C2 - transport default
# --------------------------------------------------------------------------
def patch_transport(src):
    anchor = ("    def __init__(self, Hostname, IPPort, Protocol='UDP', "
              "ServicePort=0, Model=None):")
    _once(src, anchor, "C2 transport default")
    nl = _newline(src)
    replacement = _relf(
        "    # [PATCH C2] Default was 'UDP'. Extron's own .pkp for these cameras\n"
        "    # carries the note \"Changed ethernet to TCP based on testing. DR# 62249\",\n"
        "    # and Crestron's i20 driver declares a TcpTransport.\n"
        "    def __init__(self, Hostname, IPPort, Protocol='TCP', "
        "ServicePort=0, Model=None):", nl)
    return src.replace(anchor, replacement, 1)


# --------------------------------------------------------------------------
# C3 - Commands table
# --------------------------------------------------------------------------
NEW_COMMANDS = """,
            # [PATCH C3] i20 command set.
            'TrackingFraming': {'Status': {}},
            'GroupTracking': {'Status': {}},
            'PresenterTracking': {'Status': {}},
            'TrackingProfile': {'Status': {}},
            'TrackingShot': {'Status': {}},
            'PresetZone': {'Status': {}},
            'ZoomPosition': {'Parameters': ['Speed'], 'Status': {}},
            'PanTiltAngle': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'PanTiltHome': {'Status': {}},
            'FreezeFrame': {'Status': {}},
            'Menu': {'Status': {}},
            'Identify': {'Status': {}},
            'Reboot': {'Status': {}},
            'IndicatorLight': {'Parameters': ['Color', 'Brightness'], 'Status': {}},
            'CameraOutput': {'Status': {}},
            'IntelligentSwitching': {'Status': {}},
            'CameraConnectionStatus': {'Parameters': ['Camera'], 'Status': {}}"""


def patch_commands_table(src):
    anchor = "            'Zoom': {'Parameters': ['Speed'], 'Status': {}},"
    _once(src, anchor, "C3 commands table")
    nl = _newline(src)
    # The donor's last entry carries a trailing comma; ours appends after it.
    return src.replace(
        anchor,
        anchor.rstrip(",") + _relf(NEW_COMMANDS, nl), 1)


# --------------------------------------------------------------------------
# C4 - the zoom-speed defect (same bug as the .pkp form, different line)
# --------------------------------------------------------------------------
def patch_zoom(src):
    m = re.search(
        r"( *)ZoomCmdString = pack\('>6B', self\.DeviceID, 0x01, 0x04, 0x07, "
        r"ValueStateValues\[value\], 0xFF\)", src)
    if not m:
        raise PatchError("C4: zoom command string not found in the ControlScript donor")
    indent = m.group(1)
    nl = _newline(src)
    replacement = _relf(
        indent + "# [PATCH C4] Extron transmits ValueStateValues[value] here,\n"
        + indent + "# discarding the speed computed just above, so zoom always ran\n"
        + indent + "# at speed 0. `speed` already holds direction|speed.\n"
        + indent + "ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, "
                   "speed, 0xFF)", nl)
    return src[:m.start()] + replacement + src[m.end():]


# --------------------------------------------------------------------------
# C5 - the command implementations
#
# Same wire bytes as build_i20.py's E4/E5/E6, rewritten to the ControlScript
# host contract: SetX/UpdateX names, 4-argument __SetHelper, no __SafeToSet,
# WriteStatus(command, value, qualifier).
# --------------------------------------------------------------------------
NEW_METHODS = r'''
    ######################################################
    # [PATCH C5] i20 COMMAND SET
    #
    # Byte sequences resolved from Crestron's SchemaVersion 2.0 driver
    # definition for IV-CAM-I20_IP and from Crestron's published VISCA
    # documentation. See experiments/skeleton_i20/i20_wire_table.txt.
    ######################################################

    def _Nibbles(self, value, count):
        """Split an integer into `count` bytes, one nibble each, MSB first.

        Crestron's ViscaAssemble4LowerNibbles / ViscaAssemble2LowerNibbles,
        which exist only as compiled IL in their driver (finding 07). Standard
        VISCA absolute-position encoding: 0x1A2B -> [0x01, 0x0A, 0x02, 0x0B].
        """
        return [(int(value) >> (4 * (count - 1 - i))) & 0x0F for i in range(count)]

    def _FromNibbles(self, data):
        """Inverse of _Nibbles (Crestron's ViscaExtractNibbles)."""
        out = 0
        for b in data:
            out = (out << 4) | (b & 0x0F)
        return out

    def _PresetOpcode(self, preset):
        """Recall a reserved preset. The i20 exposes its auto-switching and
        framing features this way rather than through dedicated opcodes."""
        return pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x02, preset, 0xFF)

    # Reserved presets 80/81. Documented as Start/Pause Tracking.
    def SetTrackingFraming(self, value, qualifier):

        ValueStateValues = {
            'Start': 0x50,
            'Stop':  0x51
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            self.__SetHelper('TrackingFraming', cmdString, value, qualifier)
            self.WriteStatus('TrackingFraming', value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingFraming')

    # CAM_TrackingInq: 81 09 08 01 FF -> y0 50 02 FF active / y0 50 03 FF paused
    def UpdateTrackingFraming(self, value, qualifier):

        ValueStateValues = {
            0x02: 'Start',
            0x03: 'Stop'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x08, 0x01, 0xFF)
        res = self.__UpdateHelper('TrackingFraming', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('TrackingFraming', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['TrackingFraming: Invalid/unexpected response'])

    # Reserved preset 82.
    def SetGroupTracking(self, value, qualifier):

        if value == 'Enable':
            cmdString = self._PresetOpcode(0x52)
            self.__SetHelper('GroupTracking', cmdString, value, qualifier)
            self.WriteStatus('GroupTracking', value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTracking')

    # Reserved preset 83.
    #
    # !! CONTESTED BYTE !! Crestron's driver names this EnablePresenterTracking;
    # Crestron's Reserved-Presets documentation names preset 83 "Pause Group
    # Tracking". Five other reserved presets agree between the two sources;
    # this is the only one that does not. The driver's name is used here, but
    # that is a choice - PROTOCOL.md section T3b settles it on hardware.
    def SetPresenterTracking(self, value, qualifier):

        if value == 'Enable':
            cmdString = self._PresetOpcode(0x53)
            self.__SetHelper('PresenterTracking', cmdString, value, qualifier)
            self.WriteStatus('PresenterTracking', value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresenterTracking')

    # Reserved presets 105-108 = Tracking Profile 1-4. I20 only.
    def SetTrackingProfile(self, value, qualifier):

        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x68 + int(value))
            self.__SetHelper('TrackingProfile', cmdString, value, qualifier)
            self.WriteStatus('TrackingProfile', value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingProfile')

    # Reserved presets 101-104 = Preset Zone 1-4. I20 only.
    def SetPresetZone(self, value, qualifier):

        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x64 + int(value))
            self.__SetHelper('PresetZone', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetZone')

    # Reserved presets 0 (Home Shot) and 1 (Tracking Shot).
    def SetTrackingShot(self, value, qualifier):

        ValueStateValues = {
            'Home':     0x00,
            'Tracking': 0x01
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            self.__SetHelper('TrackingShot', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingShot')

    # SetZoomPosition: 81 01 04 47 {speed} {Y4} {Y3} {Y2} {Y1} FF
    # The speed byte is a 1 Beyond extension - standard VISCA CAM_Zoom Direct
    # has no such field. Taken from Crestron's template.
    def SetZoomPosition(self, value, qualifier):

        try:
            speed = int(qualifier['Speed'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command for SetZoomPosition')
            return

        if 0 <= int(value) <= 16384 and 0 <= speed <= 7:
            cmdString = pack('>10B', self.DeviceID, 0x01, 0x04, 0x47, speed,
                             *(self._Nibbles(value, 4) + [0xFF]))
            self.__SetHelper('ZoomPosition', cmdString, value, qualifier)
            self.WriteStatus('ZoomPosition', value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomPosition')

    # GetZoomPosition: 81 09 04 47 FF -> 90 50 0p 0q 0r 0s FF
    def UpdateZoomPosition(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x47, 0xFF)
        res = self.__UpdateHelper('ZoomPosition', cmdString, value, qualifier)
        if res:
            try:
                value = self._FromNibbles(res[2:6])
                self.WriteStatus('ZoomPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ZoomPosition: Invalid/unexpected response'])

    # SetPanTiltAngle: 81 01 06 02 {pan spd} {tilt spd} {Y4..Y1} {Z4..Z1} FF
    def SetPanTiltAngle(self, value, qualifier):

        try:
            panSpeed = int(qualifier['Pan Speed'])
            tiltSpeed = int(qualifier['Tilt Speed'])
            pan = int(value['Pan'])
            tilt = int(value['Tilt'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command for SetPanTiltAngle')
            return

        if 1 <= panSpeed <= 0x18 and 1 <= tiltSpeed <= 0x14:
            payload = ([panSpeed, tiltSpeed]
                       + self._Nibbles(pan & 0xFFFF, 4)
                       + self._Nibbles(tilt & 0xFFFF, 4)
                       + [0xFF])
            cmdString = pack('>15B', self.DeviceID, 0x01, 0x06, 0x02, *payload)
            self.__SetHelper('PanTiltAngle', cmdString, value, qualifier)
            self.WriteStatus('PanTiltAngle', value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTiltAngle')

    # Pan-tiltPosInq: 81 09 06 12 FF -> 90 50 0p0q0r0s 0t0u0v0w FF
    def UpdatePanTiltAngle(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x12, 0xFF)
        res = self.__UpdateHelper('PanTiltAngle', cmdString, value, qualifier)
        if res:
            try:
                value = {'Pan': self._FromNibbles(res[2:6]),
                         'Tilt': self._FromNibbles(res[6:10])}
                self.WriteStatus('PanTiltAngle', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PanTiltAngle: Invalid/unexpected response'])

    # PanTiltReset: 81 01 06 05 FF
    def SetPanTiltHome(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x01, 0x06, 0x05, 0xFF)
        self.__SetHelper('PanTiltHome', cmdString, value, qualifier)

    # SetFreezeFrame: 81 01 04 62 {OnOff} FF   (On=0x02, Off=0x03)
    def SetFreezeFrame(self, value, qualifier):

        ValueStateValues = {
            'On':  0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x62,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('FreezeFrame', cmdString, value, qualifier)
            self.WriteStatus('FreezeFrame', value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreezeFrame')

    # GetFreezeFrame: 81 09 04 62 FF
    def UpdateFreezeFrame(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('FreezeFrame', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('FreezeFrame', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['FreezeFrame: Invalid/unexpected response'])

    # Reserved preset 95 = OSD Menu Toggle.
    def SetMenu(self, value, qualifier):

        cmdString = self._PresetOpcode(0x5F)
        self.__SetHelper('Menu', cmdString, value, qualifier)

    # Identify: 81 C2 01 01 0A FF
    def SetIdentify(self, value, qualifier):

        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x01, 0x0A, 0xFF)
        self.__SetHelper('Identify', cmdString, value, qualifier)

    # Reserved preset 99 = Reboot.
    def SetReboot(self, value, qualifier):

        cmdString = self._PresetOpcode(0x63)
        self.__SetHelper('Reboot', cmdString, value, qualifier)

    ######################################################
    # LIGHTBAR
    #
    # 8x c1 ** ** ** ** ff - four payload bytes, one per segment. Crestron's
    # driver declares {LedBar} opaque; their documentation supplies the
    # packing: each byte is (brightness << 2) | colour, with
    #   brightness  00 off, 01 dim, 10 medium, 11 bright
    #   colour      00 green, 01 red, 11 yellow   (10 undefined)
    # Half width zeroes the OUTER segments' brightness while keeping their
    # colour bits - which is why half yellow is 03 0F 0F 03, not 00 0F 0F 00.
    # This rule reproduces all 19 command strings the documentation prints.
    ######################################################

    _LIGHTBAR_COLOURS = {'Green': 0x0, 'Red': 0x1, 'Yellow': 0x3}
    _LIGHTBAR_BRIGHTNESS = {'Off': 0x0, 'Dim': 0x1, 'Medium': 0x2, 'Bright': 0x3}

    def _LightbarBytes(self, width, colour, brightness):
        c = self._LIGHTBAR_COLOURS[colour]
        b = self._LIGHTBAR_BRIGHTNESS[brightness]
        lit = (b << 2) | c
        if width == 'None':
            return [0x00, 0x00, 0x00, 0x00]
        if width == 'Half':
            return [c, lit, lit, c]
        return [lit, lit, lit, lit]

    def SetIndicatorLight(self, value, qualifier):

        colour = qualifier.get('Color') if qualifier else None
        brightness = qualifier.get('Brightness') if qualifier else None

        if value == 'None':
            colour = colour or 'Green'
            brightness = 'Off'

        if (value in ['None', 'Half', 'Full']
                and colour in self._LIGHTBAR_COLOURS
                and brightness in self._LIGHTBAR_BRIGHTNESS):
            payload = self._LightbarBytes(value, colour, brightness)
            cmdString = pack('>7B', self.DeviceID, 0xC1, *(payload + [0xFF]))
            self.__SetHelper('IndicatorLight', cmdString, value, qualifier)
            self.WriteStatus('IndicatorLight', value, qualifier)
        else:
            self.Discard('Invalid Command for SetIndicatorLight')

    ######################################################
    # INTELLIGENT SWITCHING (camera selection)
    #
    # The c2 family. Documentation gives TCP only for this family, unlike the
    # main and lightbar command sets.
    ######################################################

    # Call Camera Output: 81 c2 01 08 0Z ff   (Z = 1..5; 0 resumes switching)
    def SetCameraOutput(self, value, qualifier):

        if 0 <= int(value) <= 5:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08,
                             int(value), 0xFF)
            self.__SetHelper('CameraOutput', cmdString, value, qualifier)
            self.WriteStatus('CameraOutput', value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraOutput')

    # Get Output: 81 C2 09 08 FF
    def UpdateCameraOutput(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x08, 0xFF)
        res = self.__UpdateHelper('CameraOutput', cmdString, value, qualifier)
        if res:
            try:
                # The documentation says "see below" for this reply and then
                # prints no layout. Read on the shape the other c2 inquiries
                # use (y0 50 <payload> FF). Unverified.
                value = res[2] & 0x0F
                self.WriteStatus('CameraOutput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['CameraOutput: Invalid/unexpected response'])

    # Pause: 81 c2 01 0B 00 ff    Resume: 81 c2 01 08 00 ff
    def SetIntelligentSwitching(self, value, qualifier):

        if value == 'Pause':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x0B, 0x00, 0xFF)
        elif value == 'Resume':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08, 0x00, 0xFF)
        else:
            self.Discard('Invalid Command for SetIntelligentSwitching')
            return

        self.__SetHelper('IntelligentSwitching', cmdString, value, qualifier)
        self.WriteStatus('IntelligentSwitching', value, qualifier)

    # Check Connection Status: 81 c2 09 0d 0Z ff
    #   Disconnect: 90 50 00 00 FF     Connect: 90 50 00 01 FF
    def UpdateCameraConnectionStatus(self, value, qualifier):

        try:
            camera = int(qualifier['Camera'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command for UpdateCameraConnectionStatus')
            return

        if not 2 <= camera <= 5:
            self.Discard('Invalid Command for UpdateCameraConnectionStatus')
            return

        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x09, 0x0D, camera, 0xFF)
        res = self.__UpdateHelper('CameraConnectionStatus', cmdString, value, qualifier)
        if res:
            try:
                value = 'Connected' if res[3] else 'Disconnected'
                self.WriteStatus('CameraConnectionStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['CameraConnectionStatus: Invalid/unexpected response'])
'''


def patch_methods(src):
    anchor = "    def __CheckResponseForErrors(self, sourceCmdName, response):"
    _once(src, anchor, "C5 methods")
    nl = _newline(src)
    return src.replace(anchor, _relf(NEW_METHODS.rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------

def derive(donor_source):
    src = donor_source
    for fn in (patch_header, patch_transport, patch_commands_table,
               patch_zoom, patch_methods):
        src = fn(src)
    return src


def verify(src):
    """Static checks before this reaches a processor."""
    problems = []
    del NOTES[:]

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["module does not parse: %s" % e]

    cls = next((n for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef) and n.name == "DeviceClass"), None)
    if cls is None:
        return ["DeviceClass not found"]
    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}

    m = re.search(r"self\.Commands = \{(.*?)\n        \}", src, re.S)
    if not m:
        return ["could not locate the Commands table"]
    # Only top-level entries: one per line at the table's own indent. A looser
    # pattern also matches the nested 'Status': {} inside every entry.
    declared = set(re.findall(r"^ {12}'([A-Za-z]+)':\s*\{", m.group(1), re.M))

    # ControlScript's Set()/Update() dispatch by name, so a declared command
    # with no method is a runtime AttributeError waiting to happen. The
    # reverse (a method with no entry) is unreachable, not fatal.
    for name in sorted(declared):
        if name == "ConnectionStatus":
            continue          # status-only, written by OnConnected
        if ("Set%s" % name) not in methods and ("Update%s" % name) not in methods:
            problems.append("Commands['%s'] declared but neither Set%s nor "
                            "Update%s exists" % (name, name, name))
    for meth in sorted(methods):
        for kind in ("Set", "Update"):
            if meth.startswith(kind) and meth != kind:
                cmd = meth[len(kind):]
                if cmd and cmd[0].isupper() and cmd not in declared:
                    NOTES.append("%s implemented with no Commands entry" % meth)

    if re.search(r"""\bf['"]""", src):
        problems.append("f-string found; ControlScript on non-xi runs Python 3.5")

    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-o", "--outdir", default=os.path.join(_HERE, "out"))
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    with open(DONOR_CS, encoding="utf-8") as fh:
        donor = fh.read()
    print("donor: %s (%d bytes)" % (os.path.basename(DONOR_CS), len(donor.encode())))

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

    out = os.path.join(args.outdir, "onebynd_camera_IV_CAM_I20_v1_0_0_0.py")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(derived)
    print("  %s" % out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
