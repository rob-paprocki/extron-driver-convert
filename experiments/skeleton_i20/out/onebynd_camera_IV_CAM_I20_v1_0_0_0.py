"""
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
from extronlib.interface import SerialInterface, EthernetClientInterface
import re
# [PATCH C6] for the rate-limited pan/tilt query below.
import time
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.DeviceID = 1
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoExposure': { 'Status': {}},
            'AutoFocus': { 'Status': {}},
            'Backlight': { 'Status': {}},
            'Focus': {'Parameters': ['Speed'], 'Status': {}},
            'Gain': { 'Status': {}},
            'Iris': { 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': { 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'Shutter': { 'Status': {}},
            'WhiteBalance': { 'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
            # [PATCH C3] i20 command set.
            'TrackingFraming': {'Status': {}},
            'TrackingMode': {'Status': {}},
            'TrackingProfile': {'Status': {}},
            'TrackingShot': {'Status': {}},
            'PresetZone': {'Status': {}},
            'ZoomPosition': {'Parameters': ['Speed'], 'Status': {}},
            'PanTiltAngle': {'Parameters': ['Pan Speed', 'Tilt Speed', 'Pan', 'Tilt'], 'Status': {}},
            'PanAngleStatus': {'Status': {}},
            'TiltAngleStatus': {'Status': {}},
            'PanTiltHome': {'Status': {}},
            'FreezeFrame': {'Status': {}},
            'Menu': {'Status': {}},
            'Identify': {'Status': {}},
            'Reboot': {'Status': {}},
            'IndicatorLight': {'Parameters': ['Color', 'Brightness'], 'Status': {}},
            'CameraOutput': {'Status': {}},
            'IntelligentSwitching': {'Status': {}},
            'CameraConnectionStatus': {'Parameters': ['Camera'], 'Status': {}}
        }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            self.Error(['Device ID Out of Range'])

    def SetAutoExposure(self, value, qualifier):

        ValueStateValues = {
            'Full Auto':        0x00,
            'Manual':           0x03,
            'Shutter Priority': 0x0A,
            'Iris Priority':    0x0B,
            'Bright':           0x0D
        }

        if value in ValueStateValues:
            AutoExposureCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x39, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoExposure')

    def UpdateAutoExposure(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Full Auto',
            0x03: 'Manual',
            0x0A: 'Shutter Priority',
            0x0B: 'Iris Priority',
            0x0D: 'Bright'
        }

        AutoExposureCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x39, 0xFF)
        res = self.__UpdateHelper('AutoExposure', AutoExposureCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoExposure', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Exposure: Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            AutoFocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        AutoFocusCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x38, 0xFF)
        res = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Focus: Invalid/unexpected response'])

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            BacklightCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x33, ValueStateValues[value], 0xFF)
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        BacklightCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x33, 0xFF)
        res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Backlight', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Backlight: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Far':  0x20,
            'Near': 0x30,
            'Stop': 0x00
        }

        speed = int(qualifier['Speed'])

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            FocusCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x08, speed, 0xFF)
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetGain(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            GainCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0C, ValueStateValues[value], 0xFF)
            self.__SetHelper('Gain', GainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            IrisCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0B, ValueStateValues[value], 0xFF)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        pan_speed = int(qualifier['Pan Speed'])
        tilt_speed = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up':           0x0301,
            'Down':         0x0302,
            'Left':         0x0103,
            'Right':        0x0203,
            'Up Left':      0x0101,
            'Up Right':     0x0201,
            'Down Left':    0x0102,
            'Down Right':   0x0202,
            'Stop':         0x0303,
            'Home':         0x04,
            'Reset':        0x05
        }

        if 1 <= pan_speed <= 24 and 1 <= tilt_speed <= 20 and value in ValueStateValues:
            if value in ['Home', 'Reset']:
                PanTiltCmdString = pack('>5B', self.DeviceID, 0x01, 0x06, ValueStateValues[value], 0xFF)
            else:
                PanTiltCmdString = pack('>6BHB', self.DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF)

            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   0x02,
            'Off':  0x03
        }

        if value in ValueStateValues:
            PowerCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x00, ValueStateValues[value], 0xFF)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off',
            0x04: 'Internal Power Circuit Error'
        }

        PowerCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x00, 0xFF)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Reset':    0x00,
            'Save':     0x01,
            'Recall':   0x02
        }

        action = qualifier['Action']

        if action in ActionStates and 0 <= value <= 255:
            PresetCmdString = pack('>7B', self.DeviceID, 0x01, 0x04, 0x3F, ActionStates[action], value, 0xFF)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetShutter(self, value, qualifier):

        ValueStateValues = {
            'Up':       0x02,
            'Down':     0x03,
            'Reset':    0x00
        }

        if value in ValueStateValues:
            ShutterCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x0A, ValueStateValues[value], 0xFF)
            self.__SetHelper('Shutter', ShutterCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetShutter')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Auto':             0x00,
            'Indoor':           0x01,
            'Outdoor':          0x02,
            'One Push':         0x03,
            'Manual':           0x05,
            'One Push Trigger': ''
        }

        if value in ValueStateValues:
            if value != 'One Push Trigger':
                WhiteBalanceCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF)
            else:
                WhiteBalanceCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x10, 0x05, 0xFF)

            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def UpdateWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Auto',
            0x01: 'Indoor',
            0x02: 'Outdoor',
            0x03: 'One Push',
            0x05: 'Manual'
        }

        WhiteBalanceCmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x35, 0xFF)
        res = self.__UpdateHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('WhiteBalance', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['White Balance: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        speed = int(qualifier['Speed'])

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        if 0 <= speed <= 7 and value in ValueStateValues:
            if value == 'Stop':
                speed = 0x00
            else:
                speed += ValueStateValues[value]

            # [PATCH C4] Extron transmits ValueStateValues[value] here,
            # discarding the speed computed just above, so zoom always ran
            # at speed 0. `speed` already holds direction|speed.
            ZoomCmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x07, speed, 0xFF)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


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

    def _Signed16(self, value):
        """Read a 16-bit position the way SetPanTiltAngle writes it (pan & 0xFFFF),
        so a negative angle reads back as itself. The documentation gives the
        nibble layout but not the sign convention; the camera's is unmeasured."""
        return value - 0x10000 if value & 0x8000 else value

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

    # Reserved presets 82 and 83 - one setting, two values.
    #
    # !! CONTESTED BYTE !! Crestron's driver names 0x53 EnablePresenterTracking;
    # Crestron's Reserved-Presets documentation names preset 83 "Pause Group
    # Tracking". Five other reserved presets agree between the two sources;
    # this is the only one that does not. The value names used here are the
    # reading both sources support - 0x52 frames the group, 0x53 frames one
    # presenter - so the merge does not decide it. PROTOCOL.md section T3b
    # still settles it on hardware.
    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Group':     0x52,
            'Presenter': 0x53
        }

        if value in ValueStateValues:
            cmdString = self._PresetOpcode(ValueStateValues[value])
            self.__SetHelper('TrackingMode', cmdString, value, qualifier)
            self.WriteStatus('TrackingMode', value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

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
            # Pan and Tilt ride in the qualifier, matching the .pkp driver so
            # the two emitters stay byte-identical. In the .pkp that is forced
            # (GC routes every non-Value parameter through the qualifier); here
            # it is a choice, made so a programmer moving between the two forms
            # is not surprised.
            pan = int(qualifier['Pan'])
            tilt = int(qualifier['Tilt'])
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
    #
    # One inquiry, two commands. The .pkp form has to split this because a GC
    # command carries a single Value; this module mirrors the split so both
    # emitters expose the same surface.
    #
    # Rate limited the way Extron rate limit pana_19_5702: one query per window
    # answers both statuses, so two bound labels cost one frame rather than
    # two. A failed query caches nothing, so a poll that got no reply is
    # retried rather than remembered.
    PANTILT_QUERY_WINDOW = 1.0
    _lastPanTiltAngle = None
    _lastPanTiltTime = 0.0

    def _PanTiltAngleInquiry(self, command, value, qualifier):

        now = time.monotonic()
        if (self._lastPanTiltAngle is not None
                and now - self._lastPanTiltTime < self.PANTILT_QUERY_WINDOW):
            return self._lastPanTiltAngle
        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x12, 0xFF)
        res = self.__UpdateHelper(command, cmdString, value, qualifier)
        if not res:
            return None
        try:
            pos = (self._Signed16(self._FromNibbles(res[2:6])),
                   self._Signed16(self._FromNibbles(res[6:10])))
        except (KeyError, IndexError):
            self.Error(['%s: Invalid/unexpected response' % command])
            return None
        self._lastPanTiltAngle = pos
        self._lastPanTiltTime = now
        self.WriteStatus('PanAngleStatus', pos[0], qualifier)
        self.WriteStatus('TiltAngleStatus', pos[1], qualifier)
        return pos

    def UpdatePanAngleStatus(self, value, qualifier):

        self._PanTiltAngleInquiry('PanAngleStatus', value, qualifier)

    def UpdateTiltAngleStatus(self, value, qualifier):

        self._PanTiltAngleInquiry('TiltAngleStatus', value, qualifier)

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

    # Call Camera Output: 81 c2 01 08 0Z ff   (Z = 1..5)
    #
    # 0 also resumes intelligent switching, but that is byte-for-byte what
    # SetIntelligentSwitching('Resume') sends, so it is reachable by name and
    # not offered twice. The range starts at 1.
    def SetCameraOutput(self, value, qualifier):

        if 1 <= int(value) <= 5:
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
                # VISCA-Intelligent-Switching-Commands.md, Get Output:
                #   y0 50 01 0Z FF  switching on,   y0 50 00 0Z FF  switching off
                # The camera is the second payload byte. Reading the first gave
                # the switching flag instead (found by experiments/loopback).
                value = res[3] & 0x0F
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

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and len(response) == 4:
            error_map = {
                0x02: 'Syntax Error',
                0x03: 'Command Buffer Full',
                0x04: 'Command Cancelled',
                0x05: 'No Socket',
                0x41: 'Command Not Executable',
            }
            if response[1] & 0x60 == 0x60:
                self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map.get(response[2], 'Unknown Error'))])
                response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if res:
                return self.__CheckResponseForErrors(command, res)
            else:
                return ''

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if res:
                return self.__CheckResponseForErrors(command, res)
            else:
                return ''
     
            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
        
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return
        
            Method['callback'] = callback
            Method['qualifier'] = qualifier    
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)  

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
        self.counter = 0
        if not self.connectionFlag:
            self.OnConnected()
        Command = self.Commands[command]
        Status = Command['Status']
        if qualifier:
            for Parameter in Command['Parameters']:
                try:
                    Status = Status[qualifier[Parameter]]
                except KeyError:
                    if Parameter in qualifier:
                        Status[qualifier[Parameter]] = {}
                        Status = Status[qualifier[Parameter]]
                    else:
                        return  
        try:
            if Status['Live'] != value:
                Status['Live'] = value
                self.NewStatus(command, value, qualifier)
        except:
            Status['Live'] = value
            self.NewStatus(command, value, qualifier)

    # Read the value from a command.
    def ReadStatus(self, command, qualifier=None):
        Command = self.Commands.get(command, None)
        if Command:
            Status = Command['Status']
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Status = Status[qualifier[Parameter]]
                    except KeyError:
                        return None
            try:
                return Status['Live']
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

    # [PATCH C2] Default was 'UDP'. Extron's own .pkp for these cameras
    # carries the note "Changed ethernet to TCP based on testing. DR# 62249",
    # and Crestron's i20 driver declares a TcpTransport.
    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self) 
        # Check if Model belongs to a subclass       
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])