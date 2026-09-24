"""
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
from extronlib.interface import SerialInterface, EthernetClientInterface
import re
# [PATCH C6] for the rate-limited shared queries below.
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
            # [PATCH C7] Parity with Crestron's I20 driver (v1.6).
            'ExposureCompensationMode': {'Status': {}},
            'ExposureCompensation': {'Status': {}},
            'FocusPosition': {'Status': {}},
            'OnePushAutoFocus': {'Status': {}},
            'AutoFocusBehavior': {'Status': {}},
            'AutoFocusSensitivity': {'Status': {}},
            'AutoPrivacyMode': {'Status': {}},
            'AutoSoftwareUpdate': {'Status': {}},
            'DeviceModel': {'Status': {}},
            'RomVersion': {'Status': {}},
            'PanSpeedMaxStatus': {'Status': {}},
            'TiltSpeedMaxStatus': {'Status': {}},
            # [PATCH CP5] CAM_MountMode - P-series only.
            'MountMode': {'Status': {}}
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

    # Some replies carry more than one status: pan and tilt, the camera output
    # and the switching flag, the model and the ROM version, the two maximum
    # speeds. Rate limited the way Extron rate limit pana_19_5702: one query
    # per window answers every status the reply carries. A failed query caches
    # nothing, so a poll that got no reply is retried rather than remembered.
    INQUIRY_WINDOW = 1.0
    _inquiryCache = None

    def _SharedInquiry(self, command, cmdString, value, qualifier, parse):

        if self._inquiryCache is None:
            self._inquiryCache = {}
        now = time.monotonic()
        hit = self._inquiryCache.get(cmdString)
        if hit is not None and now - hit[0] < self.INQUIRY_WINDOW:
            return hit[1]
        res = self.__UpdateHelper(command, cmdString, value, qualifier)
        if not res:
            return None
        try:
            parsed = parse(res, qualifier)
        except (KeyError, IndexError):
            self.Error(['%s: Invalid/unexpected response' % command])
            return None
        self._inquiryCache[cmdString] = (now, parsed)
        return parsed

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
    # One query answers both statuses (_SharedInquiry above), so two bound
    # labels cost one frame rather than two.
    def _PanTiltAngleInquiry(self, command, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x12, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParsePanTiltAngle)

    def _ParsePanTiltAngle(self, res, qualifier):

        pos = (self._Signed16(self._FromNibbles(res[2:6])),
               self._Signed16(self._FromNibbles(res[6:10])))
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
    # [PATCH CP7] SHARED WITH THE I20 MODULE (byte-identical templates -
    # see experiments/skeleton_p20/i20_p20_diff.txt)
    #
    # The same commands and bytes as build_i20.py's E7; requests, reply rules
    # and ranges are Crestron's (experiments/skeleton_i20/CRESTRON_PARITY.md).
    # Left out on purpose: Privacy (driver behaviour, not a camera command),
    # the press-and-hold menu (Zoom and Pan Tilt bytes), Field Of View (its
    # polynomial is IL only), PTZ Super Operation (codes undeclared) and the
    # Exposure Compensation Up/Down steps (the level is set directly).
    ######################################################

    # SetExposureCompensationMode: 81 01 04 3E {On 02 / Off 03} FF
    def SetExposureCompensationMode(self, value, qualifier):

        ValueStateValues = {
            'On':  0x02,
            'Off': 0x03
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x3E,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('ExposureCompensationMode', cmdString, value, qualifier)
            self.WriteStatus('ExposureCompensationMode', value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompensationMode')

    # GetExposureCompensationMode: 81 09 04 3E FF -> y0 50 02/03 FF
    def UpdateExposureCompensationMode(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x3E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensationMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[2]]
                self.WriteStatus('ExposureCompensationMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ExposureCompensationMode: Invalid/unexpected response'])

    # SetExposureCompensation: 81 01 04 4E 00 00 0p 0q FF, 0-14 (0x07 = 0 EV)
    def SetExposureCompensation(self, value, qualifier):

        if 0 <= int(value) <= 14:
            cmdString = pack('>9B', self.DeviceID, 0x01, 0x04, 0x4E, 0x00, 0x00,
                             *(self._Nibbles(value, 2) + [0xFF]))
            self.__SetHelper('ExposureCompensation', cmdString, value, qualifier)
            self.WriteStatus('ExposureCompensation', value, qualifier)
        else:
            self.Discard('Invalid Command for SetExposureCompensation')

    # GetExposureCompensation: 81 09 04 4E FF -> y0 50 00 00 0p 0q FF
    def UpdateExposureCompensation(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x4E, 0xFF)
        res = self.__UpdateHelper('ExposureCompensation', cmdString, value, qualifier)
        if res:
            try:
                value = self._FromNibbles(res[2:6])
                if not 0 <= value <= 14:
                    raise KeyError(value)
                self.WriteStatus('ExposureCompensation', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ExposureCompensation: Invalid/unexpected response'])

    # SetFocusPosition: 81 01 04 48 0p 0q 0r 0s FF. Crestron's ranges are
    # I20 12224-17114 and I12 15084-20664; the module accepts the union.
    def SetFocusPosition(self, value, qualifier):

        if 12224 <= int(value) <= 20664:
            cmdString = pack('>9B', self.DeviceID, 0x01, 0x04, 0x48,
                             *(self._Nibbles(value, 4) + [0xFF]))
            self.__SetHelper('FocusPosition', cmdString, value, qualifier)
            self.WriteStatus('FocusPosition', value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusPosition')

    # GetFocusPosition: 81 09 04 48 FF -> y0 50 0p 0q 0r 0s FF
    def UpdateFocusPosition(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x04, 0x48, 0xFF)
        res = self.__UpdateHelper('FocusPosition', cmdString, value, qualifier)
        if res:
            try:
                value = self._FromNibbles(res[2:6])
                self.WriteStatus('FocusPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['FocusPosition: Invalid/unexpected response'])

    # OnePushAutoFocus: 81 01 04 18 01 FF
    def SetOnePushAutoFocus(self, value, qualifier):

        cmdString = pack('>6B', self.DeviceID, 0x01, 0x04, 0x18, 0x01, 0xFF)
        self.__SetHelper('OnePushAutoFocus', cmdString, value, qualifier)

    # SetAutoFocusBehavior: 81 C2 01 02 {Global 00 / Center 01 / Face 04} FF
    def SetAutoFocusBehavior(self, value, qualifier):

        ValueStateValues = {
            'Global': 0x00,
            'Center': 0x01,
            'Face':   0x04
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x02,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoFocusBehavior', cmdString, value, qualifier)
            self.WriteStatus('AutoFocusBehavior', value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocusBehavior')

    # GetAutoFocusBehavior: 81 C2 09 02 FF -> y0 50 00 0v FF
    def UpdateAutoFocusBehavior(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Global',
            0x01: 'Center',
            0x04: 'Face'
        }

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x02, 0xFF)
        res = self.__UpdateHelper('AutoFocusBehavior', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoFocusBehavior', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoFocusBehavior: Invalid/unexpected response'])

    # SetAutoFocusSensitivity: 81 C2 01 03 {1-3} FF
    def SetAutoFocusSensitivity(self, value, qualifier):

        if 1 <= int(value) <= 3:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x03, int(value), 0xFF)
            self.__SetHelper('AutoFocusSensitivity', cmdString, value, qualifier)
            self.WriteStatus('AutoFocusSensitivity', value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocusSensitivity')

    # GetAutoFocusSensitivity: 81 C2 09 03 FF -> y0 50 00 0v FF
    def UpdateAutoFocusSensitivity(self, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x03, 0xFF)
        res = self.__UpdateHelper('AutoFocusSensitivity', cmdString, value, qualifier)
        if res:
            try:
                value = res[3]
                if not 1 <= value <= 3:
                    raise KeyError(value)
                self.WriteStatus('AutoFocusSensitivity', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoFocusSensitivity: Invalid/unexpected response'])

    # SetAutoPrivacyMode: 81 01 0E 24 26 00 {On 01 / Off 00} FF
    # The camera answers no VISCA command while in privacy mode.
    def SetAutoPrivacyMode(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        if value in ValueStateValues:
            cmdString = pack('>8B', self.DeviceID, 0x01, 0x0E, 0x24, 0x26, 0x00,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoPrivacyMode', cmdString, value, qualifier)
            self.WriteStatus('AutoPrivacyMode', value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoPrivacyMode')

    # GetAutoPrivacyMode: 81 09 0E 24 26 FF -> y0 50 00 0v FF
    def UpdateAutoPrivacyMode(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        cmdString = pack('>6B', self.DeviceID, 0x09, 0x0E, 0x24, 0x26, 0xFF)
        res = self.__UpdateHelper('AutoPrivacyMode', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoPrivacyMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoPrivacyMode: Invalid/unexpected response'])

    # SetAutoSoftwareUpdate: 81 C2 01 04 {On 01 / Off 00} FF
    def SetAutoSoftwareUpdate(self, value, qualifier):

        ValueStateValues = {
            'On':  0x01,
            'Off': 0x00
        }

        if value in ValueStateValues:
            cmdString = pack('>6B', self.DeviceID, 0xC2, 0x01, 0x04,
                             ValueStateValues[value], 0xFF)
            self.__SetHelper('AutoSoftwareUpdate', cmdString, value, qualifier)
            self.WriteStatus('AutoSoftwareUpdate', value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSoftwareUpdate')

    # GetAutoSoftwareUpdate: 81 C2 09 04 FF -> y0 50 00 0v FF
    def UpdateAutoSoftwareUpdate(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        cmdString = pack('>5B', self.DeviceID, 0xC2, 0x09, 0x04, 0xFF)
        res = self.__UpdateHelper('AutoSoftwareUpdate', cmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoSoftwareUpdate', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoSoftwareUpdate: Invalid/unexpected response'])

    # GetDeviceInformation: 81 09 00 02 FF -> y0 50 00 01 mn pq rs tu vw FF
    # Model code mn pq through Crestron's MapModelCodeToModel; the ROM version
    # rs tu as the 16-bit number it is (FormatRomVersion is IL only).
    _MODEL_CODES = {
        (0x05, 0x05): 'IV-CAM-I20',
        (0x05, 0x06): 'IV-CAM-I12',
        (0x05, 0x07): 'IV-CAM-P20',
        (0x05, 0x08): 'IV-CAM-P12'
    }

    def _VersionInquiry(self, command, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x00, 0x02, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParseVersion)

    def _ParseVersion(self, res, qualifier):

        model = self._MODEL_CODES.get((res[4], res[5]), 'Unknown')
        rom = (res[6] << 8) | res[7]
        self.WriteStatus('DeviceModel', model, qualifier)
        self.WriteStatus('RomVersion', rom, qualifier)
        return model, rom

    def UpdateDeviceModel(self, value, qualifier):

        self._VersionInquiry('DeviceModel', value, qualifier)

    def UpdateRomVersion(self, value, qualifier):

        self._VersionInquiry('RomVersion', value, qualifier)

    # GetPanTiltSpeedMax: 81 09 06 11 FF -> y0 50 ww zz FF, one byte per axis
    def _SpeedMaxInquiry(self, command, value, qualifier):

        cmdString = pack('>5B', self.DeviceID, 0x09, 0x06, 0x11, 0xFF)
        return self._SharedInquiry(command, cmdString, value, qualifier,
                                   self._ParseSpeedMax)

    def _ParseSpeedMax(self, res, qualifier):

        speeds = (res[2], res[3])
        self.WriteStatus('PanSpeedMaxStatus', speeds[0], qualifier)
        self.WriteStatus('TiltSpeedMaxStatus', speeds[1], qualifier)
        return speeds

    def UpdatePanSpeedMaxStatus(self, value, qualifier):

        self._SpeedMaxInquiry('PanSpeedMaxStatus', value, qualifier)

    def UpdateTiltSpeedMaxStatus(self, value, qualifier):

        self._SpeedMaxInquiry('TiltSpeedMaxStatus', value, qualifier)

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