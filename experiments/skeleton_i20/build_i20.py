#!/usr/bin/env python3
"""
build_i20.py - derive a Crestron 1 Beyond IV-CAM-i20 driver from Extron's own
1 Beyond PTZ-IP12/IP20 package, and emit testable .pkp artefacts.

Why derive rather than write
----------------------------
The embedded driver in a .pkp is ~920 lines, of which ~300 are Extron's status,
mutex, timer and response-parsing boilerplate. Rewriting that from scratch would
put a large volume of unmeasured code between us and the question we actually
want answered ("does a substituted driver run on a processor?"). So this script
takes Extron's shipping 1 Beyond camera driver and applies a small number of
NAMED, individually verifiable edits. Everything not listed here is byte-for-byte
Extron's.

The edits
---------
  E1  provenance header - records what this file is and what it came from
  E2  fix Extron's zoom-speed bug (see below)
  E3  extend the Commands table with the i20 command set
  E4  add the i20 command implementations

E2 is a real defect in the shipped driver, not a stylistic change:
`_cmd_SetZoom` computes `speed` (direction nibble + speed) and then transmits
`ValueStateValues[value]`, discarding it - so zoom always runs at speed 0. The
same defect is present in the standalone ControlScript module
(onebynd_camera_AutoTracker_3_v1_0_1_1.py). Crestron's driver encodes the same
command as a single {SpeedAndDirection} byte and is correct.

Where the i20 command bytes come from
-------------------------------------
Every byte sequence added by E4 was resolved from Crestron's own
SchemaVersion 2.0 driver definition by resolve_visca.py - not guessed, and not
taken from a general VISCA reference. The i20's headline auto-switching
features turn out to need no new protocol machinery at all: they are reserved
preset numbers on the standard VISCA preset command.

    StartTrackingFraming        81 01 04 3F 02 50 FF
    StopTrackingFraming         81 01 04 3F 02 51 FF
    EnableGroupTracking         81 01 04 3F 02 52 FF
    EnablePresenterTracking     81 01 04 3F 02 53 FF
    Menu                        81 01 04 3F 02 5F FF
    Reboot                      81 01 04 3F 02 63 FF

Usage: python3 experiments/skeleton_i20/build_i20.py [-o OUTDIR]
"""

import argparse
import ast
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "tools"))

import pkp_build as pb            # noqa: E402

DONOR = os.path.join(
    _ROOT, "samples", "1 Beyond Cameras", "PTZ-IP12_IP20", "pkp",
    "1bynd_19_4743_v1_0_1.pkp")


NOTES = []


class PatchError(Exception):
    """An edit did not find its anchor - refuse to emit a half-patched driver."""


def _newline(src):
    """The donor's line ending. Extron's embedded drivers are CRLF; inserted
    text has to match or the file ends up mixed."""
    return "\r\n" if "\r\n" in src else "\n"


def _relf(text, nl):
    """Re-line-end `text` (authored with \\n here) to the donor's convention."""
    return text.replace("\r\n", "\n").replace("\n", nl)


def _once(haystack, needle, what):
    n = haystack.count(needle)
    if n != 1:
        raise PatchError("anchor for %s matched %d times, expected 1: %r"
                         % (what, n, needle[:70]))


# --------------------------------------------------------------------------
# E1 - provenance header
# --------------------------------------------------------------------------
HEADER_NOTE = '''
    ------------------------------------------------------------------
    DERIVED DRIVER - Crestron 1 Beyond IV-CAM-i12 / i20

    Derived by experiments/skeleton_i20/build_i20.py from Extron's own
    1bynd_19_4743 (PTZ-IP12/IP20) package. Extron's original code is
    unchanged except where noted as [PATCH].

    The i20 command bytes were resolved from Crestron's SchemaVersion 2.0
    driver definition (Camera_Crestron-1-Beyond_IV-CAM-I20_IP.pkg), not from
    a generic VISCA reference. Cross-vendor agreement was verified on the
    commands both vendors implement - identical bytes AND identical value
    tables (e.g. exposure mode Full Auto=0x00, Manual=0x03, Shutter
    Priority=0x0A, Iris Priority=0x0B).

    UNVERIFIED ON HARDWARE. No i20 was available to this repo. Every added
    command is a transcription of Crestron's declarative spec; none has been
    observed on a wire. Treat status feedback in particular as provisional -
    the inquiry REQUESTS are specified by Crestron, but their RESPONSE
    layouts were not fully declared and are parsed here on the same pattern
    Extron uses for the equivalent PTZ-IP responses.
    ------------------------------------------------------------------
'''


def patch_header(src):
    anchor = "    REVISION HISTORY"
    _once(src, anchor, "E1 header")
    nl = _newline(src)
    return src.replace(anchor, _relf(HEADER_NOTE.rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------
# E2 - the zoom-speed defect
# --------------------------------------------------------------------------
ZOOM_BAD = ("            ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, "
            "0x07, ValueStateValues[value], 0xFF)")
ZOOM_GOOD = ("            # [PATCH E2] Extron's shipped driver transmits "
             "ValueStateValues[value] here,\n"
             "            # discarding the speed computed immediately above, so zoom "
             "always ran at\n"
             "            # speed 0. Crestron encodes this as one "
             "{SpeedAndDirection} byte; `speed`\n"
             "            # already holds exactly that.\n"
             "            ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, "
             "0x07, speed, 0xFF)")


def patch_zoom(src):
    _once(src, ZOOM_BAD, "E2 zoom fix")
    return src.replace(ZOOM_BAD, _relf(ZOOM_GOOD, _newline(src)), 1)


# --------------------------------------------------------------------------
# E3 - Commands table
# --------------------------------------------------------------------------
NEW_COMMANDS = """,
            # [PATCH E3] i20 command set. Bytes resolved from Crestron's
            # SchemaVersion 2.0 definition by resolve_visca.py.
            'TrackingFraming':      {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'GroupTracking':        {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,                                               'Status': {}},
            'PresenterTracking':    {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,                                               'Status': {}},
            'ZoomPosition':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,   'Parameters': ['Speed'],                    'Status': {}},
            'PanTiltAngle':         {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,  'Parameters': ['Pan Speed', 'Tilt Speed', 'Pan', 'Tilt'],   'Status': {}},
            'PanAngleStatus':       {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                              'Status': {}},
            'TiltAngleStatus':      {'Set': False,  'Update': True,     'Live': True,   'Emulated': False,                              'Status': {}},
            'PanTiltHome':          {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'FreezeFrame':          {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'Menu':                 {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'Identify':             {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'TrackingProfile':      {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,                                               'Status': {}},
            'PresetZone':           {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'TrackingShot':         {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}},
            'IndicatorLight':       {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,   'Parameters': ['Color', 'Brightness'],      'Status': {}},
            'CameraOutput':         {'Set': True,   'Update': True,     'Live': True,   'Emulated': True,                                               'Status': {}},
            'IntelligentSwitching': {'Set': True,   'Update': False,    'Live': False,  'Emulated': True,                                               'Status': {}},
            'CameraConnectionStatus': {'Set': False, 'Update': True,    'Live': True,   'Emulated': False,  'Parameters': ['Camera'],                   'Status': {}},
            'Reboot':               {'Set': True,   'Update': False,    'Live': False,  'Emulated': False,                                              'Status': {}}"""


def patch_commands_table(src):
    anchor = ("            'Zoom':                 {'Set': True,   'Update': False,"
              "    'Live': False,  'Emulated': False,  'Parameters': ['Speed'],"
              "                    'Status': {}}")
    _once(src, anchor, "E3 commands table")
    return src.replace(anchor, anchor + _relf(NEW_COMMANDS, _newline(src)), 1)


# --------------------------------------------------------------------------
# E4 - command implementations
# --------------------------------------------------------------------------
NEW_METHODS = r'''
################################################################
### [PATCH E4] i20 COMMAND SET
###
### Byte sequences resolved from Crestron's SchemaVersion 2.0 driver
### definition for IV-CAM-I20_IP. See experiments/skeleton_i20/i20_wire_table.txt.
################################################################

    def _Nibbles(self, value, count):
        """Split an integer into `count` bytes, each carrying one nibble in
        its low 4 bits, most-significant first.

        This is Crestron's ViscaAssemble4LowerNibbles / ViscaAssemble2LowerNibbles,
        which finding 07 identified as having no declarative definition in their
        driver - the behaviour lived only as compiled IL. It is standard VISCA
        absolute-position encoding, so it is reimplemented here rather than
        recovered: 0x1A2B -> [0x01, 0x0A, 0x02, 0x0B].
        """
        return [(int(value) >> (4 * (count - 1 - i))) & 0x0F for i in range(count)]

    def _FromNibbles(self, data):
        """Inverse of _Nibbles (Crestron's ViscaExtractNibbles)."""
        out = 0
        for b in data:
            out = (out << 4) | (b & 0x0F)
        return out

    def _Signed16(self, value):
        """Read a 16-bit position the way SetPanTiltAngle writes it (pan & 0xFFFF),
        so a negative angle reads back as itself. The documentation gives the
        nibble layout but not the sign convention; the camera's is unmeasured."""
        return value - 0x10000 if value & 0x8000 else value

    def _PresetOpcode(self, preset):
        """Recall a reserved preset. The i20 exposes its auto-switching and
        framing features this way rather than through dedicated opcodes."""
        return pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, 0x02, preset, 0xFF)

    # Begin TrackingFraming
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: StartTrackingFraming / StopTrackingFraming
    def _cmd_SetTrackingFraming(self, value, qualifier):
        """Set Tracking Framing
        value: Enum ('Start'/'Stop')
        qualifier: None
        """
        ValueStateValues = {
            'Start':    0x50,
            'Stop':     0x51,
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            if self.__SafeToSet('TrackingFraming'):
                self.WriteTrackingFraming(value, qualifier, 'Emulated')
                self.__SetHelper('TrackingFraming', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetTrackingFraming -> 81 09 08 01 FF
    #
    # Reply layout is documented (reference/crestron-visca/COMMANDS.md, the
    # CAM_TrackingInq rows):
    #     y0 50 02 FF   tracking active
    #     y0 50 03 FF   tracking paused
    # which is VISCA's usual 0x02=on / 0x03=off convention, the same one Power
    # and IR_ReceiveInq use on this camera.
    def _cmd_UpdateTrackingFraming(self, value, qualifier):
        """Update Tracking Framing
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'Start',
            0x03: 'Stop'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x08, 0x01, 0xFF)
        res = self.__UpdateHelper('TrackingFraming', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteTrackingFraming(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['TrackingFraming: Invalid/unexpected response'])

    def WriteTrackingFraming(self, value, qualifier, context):
        self.WriteStatusHelper('TrackingFraming', value, qualifier, context)

    def ReadTrackingFraming(self, qualifier, context):
        return self.ReadStatusHelper('TrackingFraming', qualifier, context)

    # Begin GroupTracking
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: EnableGroupTracking -> reserved preset 0x52
    def _cmd_SetGroupTracking(self, value, qualifier):
        """Set Group Tracking
        value: Enum ('Enable')
        qualifier: None
        """
        if value == 'Enable':
            cmdString = self._PresetOpcode(0x52)
            if self.__SafeToSet('GroupTracking'):
                self.WriteGroupTracking(value, qualifier, 'Emulated')
                self.__SetHelper('GroupTracking', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def WriteGroupTracking(self, value, qualifier, context):
        self.WriteStatusHelper('GroupTracking', value, qualifier, context)

    def ReadGroupTracking(self, qualifier, context):
        return self.ReadStatusHelper('GroupTracking', qualifier, context)

    # Begin PresenterTracking
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: EnablePresenterTracking -> reserved preset 0x53
    #
    # !! DOCS AND IMPLEMENTATION DISAGREE ON THIS BYTE !!
    # Crestron's own driver names preset 0x53 "EnablePresenterTracking".
    # Crestron's own documentation (COMMANDS.md section 10, from the
    # Reserved-Presets page) names preset 83 decimal - the same byte -
    # "Pause Group Tracking". Five of the six reserved presets agree exactly
    # between the two sources (0x50, 0x51, 0x52, 0x5F, 0x63); this is the
    # only one that does not.
    #
    # The name here follows the driver, because a shipped driver is the more
    # specific artefact - but that is a choice, not a finding. Step 7 of
    # PROTOCOL.md is designed to settle it on hardware: start group tracking
    # with 0x52, then send 0x53, and observe whether group tracking PAUSES
    # (documentation is right) or presenter mode ENGAGES (driver is right).
    def _cmd_SetPresenterTracking(self, value, qualifier):
        """Set Presenter Tracking
        value: Enum ('Enable')
        qualifier: None
        """
        if value == 'Enable':
            cmdString = self._PresetOpcode(0x53)
            if self.__SafeToSet('PresenterTracking'):
                self.WritePresenterTracking(value, qualifier, 'Emulated')
                self.__SetHelper('PresenterTracking', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def WritePresenterTracking(self, value, qualifier, context):
        self.WriteStatusHelper('PresenterTracking', value, qualifier, context)

    def ReadPresenterTracking(self, qualifier, context):
        return self.ReadStatusHelper('PresenterTracking', qualifier, context)

    # Begin ZoomPosition
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetZoomPosition
    #   81 01 04 47 {ZoomSpeedHex} {Y4} {Y3} {Y2} {Y1} FF
    # Note the speed byte: standard VISCA CAM_Zoom Direct has no such field.
    # It is a 1 Beyond extension, and is taken from Crestron's template.
    def _cmd_SetZoomPosition(self, value, qualifier):
        """Set Zoom Position
        value: Decimal (0 - 16384)
        qualifier: {'Speed' : Decimal}
        """
        try:
            speed = int(qualifier['Speed'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if 0 <= int(value) <= 16384 and 0 <= speed <= 7:
            cmdString = pack('>10B', self.DeviceID, 0x01, 0x04, 0x47, speed,
                             *(self._Nibbles(value, 4) + [0xFF]))
            if self.__SafeToSet('ZoomPosition'):
                self.WriteZoomPosition(value, qualifier, 'Emulated')
                self.__SetHelper('ZoomPosition', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetZoomPosition -> 81 09 04 47 FF
    def _cmd_UpdateZoomPosition(self, value, qualifier):
        """Update Zoom Position
        value: Decimal
        qualifier: {'Speed' : Decimal}
        """
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x47, 0xFF)
        res = self.__UpdateHelper('ZoomPosition', cmdString, value, qualifier)
        if res:
            try:
                # Reply 90 50 0p 0q 0r 0s FF - four nibbles, as sent.
                value = self._FromNibbles(res[2:6])
                self.WriteZoomPosition(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['ZoomPosition: Invalid/unexpected response'])

    def WriteZoomPosition(self, value, qualifier, context):
        self.WriteStatusHelper('ZoomPosition', value, qualifier, context)

    def ReadZoomPosition(self, qualifier, context):
        return self.ReadStatusHelper('ZoomPosition', qualifier, context)

    # Begin PanTiltAngle
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetPanTiltAngle
    #   81 01 06 02 {PanSpeed} {TiltSpeed} {Y4..Y1} {Z4..Z1} FF
    def _cmd_SetPanTiltAngle(self, value, qualifier):
        """Set Pan/Tilt Angle
        value: None
        qualifier: {'Pan Speed': Decimal, 'Tilt Speed': Decimal,
                    'Pan': Decimal, 'Tilt': Decimal}

        Every parameter arrives in the qualifier because none of them is the
        asset's `Value`. That is Extron's own convention for a multi-number
        command - see pana_19_5702's PanTiltAbsolutePosition, whose asset is
        `Pan(Decimal) | Tilt(Decimal)` with no Value and whose script reads
        `qualifier['Pan']`. An earlier revision took pan and tilt from `value`
        as a dict, which GC cannot express and which therefore never ran.
        """
        try:
            panSpeed = int(qualifier['Pan Speed'])
            tiltSpeed = int(qualifier['Tilt Speed'])
            pan = int(qualifier['Pan'])
            tilt = int(qualifier['Tilt'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if 1 <= panSpeed <= 0x18 and 1 <= tiltSpeed <= 0x14:
            payload = ([panSpeed, tiltSpeed]
                       + self._Nibbles(pan & 0xFFFF, 4)
                       + self._Nibbles(tilt & 0xFFFF, 4)
                       + [0xFF])
            cmdString = pack('>15B', self.DeviceID, 0x01, 0x06, 0x02, *payload)
            if self.__SafeToSet('PanTiltAngle'):
                self.__SetHelper('PanTiltAngle', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Position feedback is split in two because ONE VISCA inquiry returns both
    # numbers and a GC command can only carry one Value. Extron solves it the
    # same way in pana_19_5702 (PanPositionStatus / TiltPositionStatus), so the
    # split is their pattern rather than our invention.
    #
    # Crestron IV-CAM-I20_IP: GetPanTiltAngle -> 81 09 06 12 FF
    #   reply  y0 50 0p0q0r0s 0t0u0v0w FF
    def _PanTiltAngleInquiry(self, command, value, qualifier):
        """Send the shared inquiry; return (pan, tilt) or None."""
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x12, 0xFF)
        res = self.__UpdateHelper(command, cmdString, value, qualifier)
        if not res:
            return None
        try:
            return (self._Signed16(self._FromNibbles(res[2:6])),
                    self._Signed16(self._FromNibbles(res[6:10])))
        except (KeyError, IndexError):
            self.Error(['%s: Invalid/unexpected response' % command])
            return None

    def _cmd_UpdatePanAngleStatus(self, value, qualifier):
        """Update Pan Angle Status
        value: Decimal
        qualifier: None
        """
        pos = self._PanTiltAngleInquiry('PanAngleStatus', value, qualifier)
        if pos is not None:
            self.WritePanAngleStatus(pos[0], qualifier, 'Live')

    def WritePanAngleStatus(self, value, qualifier, context):
        self.WriteStatusHelper('PanAngleStatus', value, qualifier, context)

    def ReadPanAngleStatus(self, qualifier, context):
        return self.ReadStatusHelper('PanAngleStatus', qualifier, context)

    def _cmd_UpdateTiltAngleStatus(self, value, qualifier):
        """Update Tilt Angle Status
        value: Decimal
        qualifier: None
        """
        pos = self._PanTiltAngleInquiry('TiltAngleStatus', value, qualifier)
        if pos is not None:
            self.WriteTiltAngleStatus(pos[1], qualifier, 'Live')

    def WriteTiltAngleStatus(self, value, qualifier, context):
        self.WriteStatusHelper('TiltAngleStatus', value, qualifier, context)

    def ReadTiltAngleStatus(self, qualifier, context):
        return self.ReadStatusHelper('TiltAngleStatus', qualifier, context)

    # Begin PanTiltHome
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: PanTiltReset -> 81 01 06 05 FF
    def _cmd_SetPanTiltHome(self, value, qualifier):
        """Set Pan/Tilt Home
        value: Enum ('Reset')
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0x01, 0x06, 0x05, 0xFF)
        if self.__SafeToSet('PanTiltHome'):
            self.__SetHelper('PanTiltHome', cmdString, value, qualifier, 3)

    # Begin FreezeFrame
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: SetFreezeFrame -> 81 01 04 62 {OnOff} FF
    # OnOff from Crestron's MapBooleanToViscaOnOff: On=0x02, Off=0x03.
    def _cmd_SetFreezeFrame(self, value, qualifier):
        """Set Freeze Frame
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x62,
                             ValueStateValues[value], 0xFF)
            if self.__SafeToSet('FreezeFrame'):
                self.WriteFreezeFrame(value, qualifier, 'Emulated')
                self.__SetHelper('FreezeFrame', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Crestron IV-CAM-I20_IP: GetFreezeFrame -> 81 09 04 62 FF
    def _cmd_UpdateFreezeFrame(self, value, qualifier):
        """Update Freeze Frame
        value: Enum
        qualifier: None
        """
        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x62, 0xFF)
        res = self.__UpdateHelper('FreezeFrame', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteFreezeFrame(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['FreezeFrame: Invalid/unexpected response'])

    def WriteFreezeFrame(self, value, qualifier, context):
        self.WriteStatusHelper('FreezeFrame', value, qualifier, context)

    def ReadFreezeFrame(self, qualifier, context):
        return self.ReadStatusHelper('FreezeFrame', qualifier, context)

    # Begin Menu
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Menu -> reserved preset 0x5F
    def _cmd_SetMenu(self, value, qualifier):
        """Set Menu
        value: Enum ('Toggle')
        qualifier: None
        """
        cmdString = self._PresetOpcode(0x5F)
        if self.__SafeToSet('Menu'):
            self.__SetHelper('Menu', cmdString, value, qualifier, 3)

    # Begin Identify
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Identify -> 81 C2 01 01 0A FF (custom command)
    def _cmd_SetIdentify(self, value, qualifier):
        """Set Identify
        value: Enum ('Identify')
        qualifier: None
        """
        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x01, 0x0A, 0xFF)
        if self.__SafeToSet('Identify'):
            self.__SetHelper('Identify', cmdString, value, qualifier, 3)

    # Begin Reboot
    ####################################################################################################################
    # Crestron IV-CAM-I20_IP: Reboot -> reserved preset 0x63
    def _cmd_SetReboot(self, value, qualifier):
        """Set Reboot
        value: Enum ('Reboot')
        qualifier: None
        """
        cmdString = self._PresetOpcode(0x63)
        if self.__SafeToSet('Reboot'):
            self.__SetHelper('Reboot', cmdString, value, qualifier, 5)

    # Begin TrackingProfile
    ####################################################################################################################
    # Reserved presets 105-108 decimal (0x69-0x6C) = Tracking Profile 1-4.
    # I20 only. Source: reference/crestron-visca/COMMANDS.md section 10.
    # Crestron's driver declares SetTrackingFramingProfile as a preset recall
    # but supplies no preset value; the documentation supplies it.
    def _cmd_SetTrackingProfile(self, value, qualifier):
        """Set Tracking Profile
        value: Decimal (1 - 4)
        qualifier: None
        """
        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x68 + int(value))
            if self.__SafeToSet('TrackingProfile'):
                self.WriteTrackingProfile(value, qualifier, 'Emulated')
                self.__SetHelper('TrackingProfile', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def WriteTrackingProfile(self, value, qualifier, context):
        self.WriteStatusHelper('TrackingProfile', value, qualifier, context)

    def ReadTrackingProfile(self, qualifier, context):
        return self.ReadStatusHelper('TrackingProfile', qualifier, context)

    # Begin PresetZone
    ####################################################################################################################
    # Reserved presets 101-104 decimal (0x65-0x68) = Preset Zone 1-4. I20 only.
    def _cmd_SetPresetZone(self, value, qualifier):
        """Set Preset Zone
        value: Decimal (1 - 4)
        qualifier: None
        """
        if 1 <= int(value) <= 4:
            cmdString = self._PresetOpcode(0x64 + int(value))
            if self.__SafeToSet('PresetZone'):
                self.__SetHelper('PresetZone', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Begin TrackingShot
    ####################################################################################################################
    # Reserved presets 0 (Home Shot) and 1 (Tracking Shot).
    def _cmd_SetTrackingShot(self, value, qualifier):
        """Set Tracking Shot
        value: Enum ('Home'/'Tracking')
        qualifier: None
        """
        ValueStateValues = {
            'Home':     0x00,
            'Tracking': 0x01
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            if self.__SafeToSet('TrackingShot'):
                self.__SetHelper('TrackingShot', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

################################################################
### [PATCH E5] LIGHTBAR
###
### Command format 8x c1 ** ** ** ** ff - four payload bytes, one per
### lightbar segment. Crestron's driver declares this as
### SetIndicatorLight -> {Header} c1 {LedBar} FF with {LedBar} opaque; the
### documentation supplies the packing.
###
### Each payload byte is (brightness << 2) | colour, with
###     brightness  00 off, 01 dim, 10 medium, 11 bright
###     colour      00 green, 01 red, 11 yellow   (10 undefined)
### Half width leaves the two OUTER segments at brightness 00 while keeping
### their colour bits - which is why "half yellow" is 03 0F 0F 03 and not
### 00 0F 0F 00. That rule reproduces all 19 command strings printed in the
### documentation; test_i20_wire.py asserts every one of them.
###
### Segment geometry differs by model but the wire format does not: I20 has
### two outer segments of 4 lights and two inner of 3 (14 total); P20 has
### four segments of 4 (16 total).
################################################################

    _LIGHTBAR_COLOURS = {'Green': 0x0, 'Red': 0x1, 'Yellow': 0x3}
    _LIGHTBAR_BRIGHTNESS = {'Off': 0x0, 'Dim': 0x1, 'Medium': 0x2, 'Bright': 0x3}

    def _LightbarBytes(self, width, colour, brightness):
        """The four payload bytes for a width/colour/brightness combination."""
        c = self._LIGHTBAR_COLOURS[colour]
        b = self._LIGHTBAR_BRIGHTNESS[brightness]
        lit = (b << 2) | c
        if width == 'None':
            return [0x00, 0x00, 0x00, 0x00]
        if width == 'Half':
            return [c, lit, lit, c]
        return [lit, lit, lit, lit]

    # Begin IndicatorLight
    ####################################################################################################################
    def _cmd_SetIndicatorLight(self, value, qualifier):
        """Set Indicator Light (lightbar)
        value: Enum ('None'/'Half'/'Full')
        qualifier: {'Color': Enum, 'Brightness': Enum}
        """
        colour = qualifier.get('Color') if qualifier else None
        brightness = qualifier.get('Brightness') if qualifier else None

        if value == 'None':
            # Colour and brightness are irrelevant when nothing is lit, but the
            # qualifiers still have to be valid keys for the status tree.
            colour = colour or 'Green'
            brightness = 'Off'

        if (value in ['None', 'Half', 'Full']
                and colour in self._LIGHTBAR_COLOURS
                and brightness in self._LIGHTBAR_BRIGHTNESS):
            payload = self._LightbarBytes(value, colour, brightness)
            cmdString = pack('>7B', self.DeviceID, 0xC1, *(payload + [0xFF]))
            if self.__SafeToSet('IndicatorLight'):
                self.WriteIndicatorLight(value, qualifier, 'Emulated')
                self.__SetHelper('IndicatorLight', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    def WriteIndicatorLight(self, value, qualifier, context):
        self.WriteStatusHelper('IndicatorLight', value, qualifier, context)

    def ReadIndicatorLight(self, qualifier, context):
        return self.ReadStatusHelper('IndicatorLight', qualifier, context)

################################################################
### [PATCH E6] INTELLIGENT SWITCHING (camera selection)
###
### The c2 command family, documented at
### reference/crestron-visca/COMMANDS.md section 9. Transport is TCP only
### for this family - the documentation does not offer serial, unlike the
### main and lightbar sets.
################################################################

    # Begin CameraOutput
    ####################################################################################################################
    # Call Camera Output:            8x c2 01 08 0Z ff   (Z = 1..5)
    # Resume Intelligent Switching:  8x c2 01 08 00 ff
    def _cmd_SetCameraOutput(self, value, qualifier):
        """Set Camera Output
        value: Decimal (1 - 5), or 0 to resume intelligent switching
        qualifier: None
        """
        if 0 <= int(value) <= 5:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08,
                             int(value), 0xFF)
            if self.__SafeToSet('CameraOutput'):
                self.WriteCameraOutput(value, qualifier, 'Emulated')
                self.__SetHelper('CameraOutput', cmdString, value, qualifier, 3)
        else:
            self.Discard('Invalid Command')

    # Get Output: 8x C2 09 08 FF
    def _cmd_UpdateCameraOutput(self, value, qualifier):
        """Update Camera Output
        value: Decimal
        qualifier: None
        """
        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x08, 0xFF)
        res = self.__UpdateHelper('CameraOutput', cmdString, value, qualifier)
        if res:
            try:
                # VISCA-Intelligent-Switching-Commands.md, Get Output:
                #   y0 50 01 0Z FF  switching on,   y0 50 00 0Z FF  switching off
                # The camera is the second payload byte. Reading the first gave
                # the switching flag instead (found by experiments/loopback).
                value = res[3] & 0x0F
                self.WriteCameraOutput(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['CameraOutput: Invalid/unexpected response'])

    def WriteCameraOutput(self, value, qualifier, context):
        self.WriteStatusHelper('CameraOutput', value, qualifier, context)

    def ReadCameraOutput(self, qualifier, context):
        return self.ReadStatusHelper('CameraOutput', qualifier, context)

    # Begin IntelligentSwitching
    ####################################################################################################################
    # Pause:  8x c2 01 0B 00 ff        Resume: 8x c2 01 08 00 ff
    def _cmd_SetIntelligentSwitching(self, value, qualifier):
        """Set Intelligent Switching
        value: Enum ('Resume'/'Pause')
        qualifier: None
        """
        if value == 'Pause':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x0B, 0x00, 0xFF)
        elif value == 'Resume':
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x08, 0x00, 0xFF)
        else:
            self.Discard('Invalid Command')
            return

        if self.__SafeToSet('IntelligentSwitching'):
            self.WriteIntelligentSwitching(value, qualifier, 'Emulated')
            self.__SetHelper('IntelligentSwitching', cmdString, value, qualifier, 3)

    def WriteIntelligentSwitching(self, value, qualifier, context):
        self.WriteStatusHelper('IntelligentSwitching', value, qualifier, context)

    def ReadIntelligentSwitching(self, qualifier, context):
        return self.ReadStatusHelper('IntelligentSwitching', qualifier, context)

    # Begin CameraConnectionStatus
    ####################################################################################################################
    # Check Connection Status: 8x c2 09 0d 0Z ff
    #   Disconnect: Y0 50 00 00 FF     Connect: Y0 50 00 01 FF
    def _cmd_UpdateCameraConnectionStatus(self, value, qualifier):
        """Update Camera Connection Status
        value: Enum
        qualifier: {'Camera' : Decimal 2-5}
        """
        try:
            camera = int(qualifier['Camera'])
        except (KeyError, TypeError, ValueError):
            self.Discard('Invalid Command')
            return

        if not 2 <= camera <= 5:
            self.Discard('Invalid Command')
            return

        cmdString = pack('>6B', self.DeviceID, 0xC2, 0x09, 0x0D, camera, 0xFF)
        res = self.__UpdateHelper('CameraConnectionStatus', cmdString, value, qualifier)
        if res:
            try:
                value = 'Connected' if res[3] else 'Disconnected'
                self.WriteCameraConnectionStatus(value, qualifier, 'Live')
            except (KeyError, IndexError):
                self.Error(['CameraConnectionStatus: Invalid/unexpected response'])

    def WriteCameraConnectionStatus(self, value, qualifier, context):
        self.WriteStatusHelper('CameraConnectionStatus', value, qualifier, context)

    def ReadCameraConnectionStatus(self, qualifier, context):
        return self.ReadStatusHelper('CameraConnectionStatus', qualifier, context)
'''


def patch_methods(src):
    # Single-line anchor: the donor is CRLF, so a multi-line anchor would bake
    # in a line-ending assumption.
    anchor = "### END AUTO GENERATION OF COMMAND DEF"
    _once(src, anchor, "E4 methods")
    nl = _newline(src)
    return src.replace(anchor, _relf(NEW_METHODS.rstrip(), nl) + nl + nl + anchor, 1)


# --------------------------------------------------------------------------
# Verification - refuse to emit a driver that cannot be true
# --------------------------------------------------------------------------
def verify(src, class_name):
    """Static checks. None of these prove the driver works on hardware; they
    prove it is not obviously broken before it costs someone a site visit."""
    problems = []

    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return ["driver does not parse: %s" % e]

    cls = next((n for n in ast.walk(tree)
                if isinstance(n, ast.ClassDef) and n.name == class_name), None)
    if cls is None:
        return ["class %s not found in derived driver" % class_name]

    methods = {n.name for n in cls.body if isinstance(n, ast.FunctionDef)}

    # Every command declared Set/Update must have the matching implementation,
    # and every implementation must be declared. Finding 07's rule, applied to
    # ourselves: a table that promises more than the code delivers is exactly
    # the partial-extraction failure mode.
    m = re.search(r"self\.Commands = \{(.*?)\n        \}", src, re.S)
    if not m:
        return ["could not locate the Commands table"]
    declared = {}
    for line in m.group(1).split("\n"):
        km = re.match(r"\s*'([A-Za-z]+)':\s*\{(.*)", line)
        if km:
            declared[km.group(1)] = km.group(2)

    for name, body in sorted(declared.items()):
        if "'Set': True" in body and ("_cmd_Set%s" % name) not in methods:
            problems.append("Commands['%s'] declares Set but _cmd_Set%s is missing"
                            % (name, name))
        if "'Update': True" in body and ("_cmd_Update%s" % name) not in methods:
            problems.append("Commands['%s'] declares Update but _cmd_Update%s is missing"
                            % (name, name))

    # The reverse direction is NOT fatal, and the asymmetry is the point: a
    # table entry with no method makes GC call something that does not exist,
    # while a method with no table entry is unreachable code. Extron's own
    # driver carries _cmd_SetSyncEmulatedStatus, a framework hook rather than a
    # device command, so treating this as an error would fail on the donor
    # itself - and a check that fails on known-good input teaches you nothing.
    for meth in sorted(methods):
        for kind in ("Set", "Update"):
            if meth.startswith("_cmd_%s" % kind):
                cmd = meth[len("_cmd_%s" % kind):]
                if cmd in declared and ("'%s': True" % kind) not in declared[cmd]:
                    problems.append("%s implemented but Commands['%s'] has '%s': False"
                                    % (meth, cmd, kind))
                elif cmd not in declared:
                    NOTES.append("%s implemented with no Commands entry (framework hook?)"
                                 % meth)

    # Python 3.5 target: non-xi processors run 3.5, so no f-strings.
    if re.search(r"""\bf['"]""", src):
        problems.append("f-string found; embedded drivers must run on Python 3.5")

    return problems


# --------------------------------------------------------------------------

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
    print("donor: %s" % os.path.basename(DONOR))
    print("  round-trips byte-identically, %d bytes" % len(builder.raw))
    print("  embedded script: %s (%d bytes, class %s)"
          % (slot.key, len(slot.source.encode()), class_name))

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

    driver_path = os.path.join(args.outdir, "driver_i20.py")
    with open(driver_path, "w", encoding="utf-8") as fh:
        fh.write(derived)

    # ---- the staged artefacts, one per gate in PROTOCOL.md ----------------
    # Each stage changes exactly ONE thing relative to the one before it, so a
    # failure names its own cause. Filenames use ids in the 200xx range, which
    # no observed Extron package occupies, so nothing in a real driver library
    # is shadowed or overwritten.
    #
    # Note the internal identity string ('1bynd_19_4743', object 15) is left
    # alone in every stage. T0 is precisely the experiment that establishes
    # whether GC tolerates a filename that disagrees with it; changing both at
    # once would confound the two.
    stages = []

    def stage(filename, what, mutate=None):
        b = pb.PackageBuilder(DONOR)
        if mutate:
            mutate(b)
        stages.append((filename, b, what))

    # T0 - byte-identical copy under a new filename. Discovery only.
    stage("1bynd_19_20020_v1_0_0.pkp", "T0 control: unmodified copy")

    # T1 - model names only. Does metadata survive a catalogue rebuild?
    def rename(b):
        b.replace_string(358, "IV-CAM-I12")
        b.replace_string(368, "IV-CAM-I20")
    stage("1bynd_19_20021_v1_0_0.pkp", "T1 identity: models renamed", rename)

    # T2 - driver only. Does a substituted script load and run?
    stage("1bynd_19_20022_v1_0_0.pkp", "T2 driver: i20 command set",
          lambda b: b.replace_script(slot.key, derived))

    # T3 - the deliverable: both.
    def both(b):
        rename(b)
        b.replace_script(slot.key, derived)
    stage("1bynd_19_20023_v1_0_0.pkp", "T3 deliverable: renamed + i20 driver", both)

    for filename, b, what in stages:
        path = os.path.join(args.outdir, filename)
        b.write(path)
        print("  %-30s %8d bytes  %s" % (filename, os.path.getsize(path), what))
        for e in b.edits:
            print("      %s" % e)

    print("\nwrote %s" % args.outdir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
