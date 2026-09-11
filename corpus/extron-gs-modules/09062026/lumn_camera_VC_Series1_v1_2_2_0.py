from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'VC-A30': self.lumn_19_550_A,
            'VC-G30': self.lumn_19_550_A,
            'VC-A50': self.lumn_19_550_A,
            'VC-G50': self.lumn_19_550_A,
            'VC-302': self.lumn_19_550_A,
            'VC-502': self.lumn_19_550_A,
            'VC-B20DU': self.lumn_19_550_A,
            'VC-B202DU': self.lumn_19_550_A,
            'VC-A20P': self.lumn_19_550_A,
            'VC-A60S': self.lumn_19_550_B,
            'VC-A50S': self.lumn_19_550_B,
            'VC-B20U': self.lumn_19_550_A,
            'VC-B202U': self.lumn_19_550_A
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddressSet': {'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'CameraPosition': {'Parameters': ['Device ID'], 'Status': {}},
            'DigitalZoom': {'Parameters': ['Device ID'], 'Status': {}},
            'FactoryReset': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID'], 'Status': {}},
            'FocusMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Freeze': {'Parameters': ['Device ID'], 'Status': {}},
            'Gain': {'Parameters': ['Device ID'], 'Status': {}},
            'HighResolutionMode': {'Parameters': ['Device ID'], 'Status': {}},
            'InfraredMode': {'Parameters': ['Device ID'], 'Status': {}},
            'IRRemote': {'Parameters': ['Device ID'], 'Status': {}},
            'MirrorImage': {'Parameters': ['Device ID'], 'Status': {}},
            'MotionlessPreset': {'Parameters': ['Device ID'], 'Status': {}},
            'Mute': {'Parameters': ['Device ID'], 'Status': {}},
            'PanandTiltSpeedMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PanNormal': {'Parameters': ['Device ID', 'Pan Speed'], 'Status': {}},
            'PanSmooth': {'Parameters': ['Device ID', 'Pan Speed'], 'Status': {}},
            'PictureFlip': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetReset': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSpeed1': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSpeed2': {'Parameters': ['Device ID'], 'Status': {}},
            'Resolution': {'Parameters': ['Device ID'], 'Status': {}},
            'TiltNormal': {'Parameters': ['Device ID', 'Tilt Speed'], 'Status': {}},
            'TiltSmooth': {'Parameters': ['Device ID', 'Tilt Speed'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID', 'Zoom Speed'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.matchError = re.compile(b'[\x90\xA0\xB0\xC0\xD0\xE0\xF0][\x60-\x62]([\x02-\x05\x41])\xFF')

    def SetDeviceID(self, value):
        try:
            value = int(value)
        except ValueError:
            return 0
        if 1 <= value <= 7:
            return 0x80 + value
        else:
            return 0

    def SetAddressSet(self, value, qualifier):

        AddressSetCmdString = pack('>4s', b'\x88\x30\x01\xFF')
        self.__SetHelper('AddressSet', AddressSetCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x33\x02\xFF',
            'Off': b'\x01\x04\x33\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('Backlight', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        Backlight_Values = {
            0x04: 'On',
            0x00: 'Off',
        }

        HR_Values = {
            0x20: 'On',
            0x00: 'Off',
        }
        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            CmdString = pack('>B5s', deviceID, b'\x09\x7E\x7E\x01\xFF')
            res = self.__UpdateHelper('Backlight', CmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('Backlight', Backlight_Values[res[9] & 0x04], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Update Backlight: Invalid/unexpected response for Backlight'])
                try:
                    self.WriteStatus('HighResolutionMode', HR_Values[res[9] & 0x20], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Update Backlight: Invalid/unexpected response for High Resolution Mode'])
        else:
            self.Discard('Invalid Command for UpdateBacklight')

    def SetCameraPosition(self, value, qualifier):

        Value = {
            'Home': b'\x01\x06\x04\xFF',
            'Reset': b'\x01\x06\x05\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('CameraPosition', pack('>B4s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPosition')

    def SetDigitalZoom(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x06\x02\xFF',
            'Off': b'\x01\x04\x06\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('DigitalZoom', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalZoom')

    def UpdateDigitalZoom(self, value, qualifier):

        DigitalZoom_Values = {
            0x02: 'On',
            0x03: 'Off',
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            DigitalZoomCmdString = pack('>B4s', deviceID, b'\x09\x04\x06\xFF')
            res = self.__UpdateHelper('DigitalZoom', DigitalZoomCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('DigitalZoom', DigitalZoom_Values[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Digital Zoom: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDigitalZoom')

    def SetFactoryReset(self, value, qualifier):
        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            FactoryResetCmdString = pack('>B6s', deviceID, b'\x01\x04\x3F\x03\x00\xFF')
            self.__SetHelper('FactoryReset', FactoryResetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFactoryReset')

    def SetFocus(self, value, qualifier):

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            FocusSpeed = int(qualifier['Focus Speed'])
            if 0 <= int(FocusSpeed) <= 7:
                if value == 'Far':
                    FocusCmdString = pack('>B3sBB', deviceID, b'\x01\x04\x08', FocusSpeed + 0x20, 0xFF)
                elif value == 'Near':
                    FocusCmdString = pack('>B3sBB', deviceID, b'\x01\x04\x08', FocusSpeed + 0x30, 0xFF)
                elif value == 'Stop':
                    FocusCmdString = pack('>B5s', deviceID, b'\x01\x04\x08\x00\xFF')
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFocus')
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        Value = {
            'Auto': b'\x01\x04\x38\x02\xFF',
            'Manual': b'\x01\x04\x38\x03\xFF',
            'One Push Trigger': b'\x01\x04\x18\x01\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('FocusMode', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        FocusMode_Values = {
            0x01: 'Auto',
            0x00: 'Manual',
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            FocusModeCmdString = pack('>B5s', deviceID, b'\x09\x7E\x7E\x00\xFF')
            res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('FocusMode', FocusMode_Values[res[13] & 0x01], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Focus Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFocusMode')

    def SetFreeze(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x62\x02\xFF',
            'Off': b'\x01\x04\x62\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('Freeze', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            FreezeCmdString = pack('>B4s', deviceID, b'\x09\x04\x62\xFF')
            res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('Freeze', ValueStateValues[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Freeze: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def SetGain(self, value, qualifier):

        Value = {
            'Up': b'\x01\x04\x0C\x02\xFF',
            'Down': b'\x01\x04\x0C\x03\xFF',
            'Reset': b'\x01\x04\x0C\x00\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('Gain', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGain')

    def SetHighResolutionMode(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x52\x02\xFF',
            'Off': b'\x01\x04\x52\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('HighResolutionMode', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHighResolutionMode')

    def UpdateHighResolutionMode(self, value, qualifier):
        self.UpdateBacklight(value, qualifier)

    def SetInfraredMode(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x01\x02\xFF',
            'Off': b'\x01\x04\x01\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('InfraredMode', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInfraredMode')

    def UpdateInfraredMode(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetIRRemote(self, value, qualifier):

        Value = {
            'On': b'\x01\x06\x08\x02\xFF',
            'Off': b'\x01\x06\x08\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('IRRemote', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemote')

    def UpdateIRRemote(self, value, qualifier):

        Values = {
            0x02: 'On',
            0x03: 'Off',
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            CmdString = pack('>B4s', deviceID, b'\x09\x06\x08\xFF')
            res = self.__UpdateHelper('IRRemote', CmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('IRRemote', Values[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['IR Remote: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIRRemote')

    def SetMirrorImage(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x61\x02\xFF',
            'Off': b'\x01\x04\x61\x03\xFF'
        }
        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            MirrorImageCmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('MirrorImage', MirrorImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMirrorImage')

    def UpdateMirrorImage(self, value, qualifier):

        self.UpdatePower(value, qualifier)

    def SetMotionlessPreset(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x07\x01\x02\xFF',
            'Off': b'\x01\x07\x01\x03\xFF'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            MotionlessPresetCmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('MotionlessPreset', MotionlessPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotionlessPreset')

    def SetMute(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x75\x02\xFF',
            'Off': b'\x01\x04\x75\x03\xFF',
        }[value]

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('Mute', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            MuteCmdString = pack('>B4s', deviceID, b'\x09\x04\x75\xFF')
            res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('Mute', ValueStateValues[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMute')

    def SetPanandTiltSpeedMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x01\x06\x1F\x00\xFF',
            'Smooth': b'\x01\x06\x1F\x01\xFF'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            PanandTiltSpeedModeCmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('PanandTiltSpeedMode', PanandTiltSpeedModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanandTiltSpeedMode')

    def SetPanNormal(self, value, qualifier):

        PanSpeed = int(qualifier['Pan Speed'])

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:

            if 1 <= PanSpeed <= 24:
                ValueStateValues = {
                    'Left': pack('>B3sB4s', deviceID, b'\x01\x06\x01', PanSpeed, b'\x00\x01\x03\xFF'),
                    'Right': pack('>B3sB4s', deviceID, b'\x01\x06\x01', PanSpeed, b'\x00\x02\x03\xFF'),
                    'Stop': pack('>B8s', deviceID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
                PanNormalCmdString = ValueStateValues[value]
                self.__SetHelper('PanNormal', PanNormalCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPanNormal')
        else:
            self.Discard('Invalid Command for SetPanNormal')

    def SetPanSmooth(self, value, qualifier):

        PanSpeed = int(qualifier['Pan Speed'])

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:

            if 1 <= PanSpeed <= 100:
                ValueStateValues = {
                    'Left': pack('>B3sB4s', deviceID, b'\x01\x06\x01', PanSpeed, b'\x00\x01\x03\xFF'),
                    'Right': pack('>B3sB4s', deviceID, b'\x01\x06\x01', PanSpeed, b'\x00\x02\x03\xFF'),
                    'Stop': pack('>B8s', deviceID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
                PanSmoothCmdString = ValueStateValues[value]
                self.__SetHelper('PanSmooth', PanSmoothCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPanSmooth')
        else:
            self.Discard('Invalid Command for SetPanSmooth')

    def SetPictureFlip(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x66\x02\xFF',
            'Off': b'\x01\x04\x66\x03\xFF'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            PictureFlipCmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('PictureFlip', PictureFlipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureFlip')

    def UpdatePictureFlip(self, value, qualifier):

        ValueStateValues = {
            0x02: 'On',
            0x03: 'Off'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            PictureFlipCmdString = pack('>B4s', deviceID, b'\x09\x04\x66\xFF')
            res = self.__UpdateHelper('PictureFlip', PictureFlipCmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('PictureFlip', ValueStateValues[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Flip: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureFlip')

    def SetPower(self, value, qualifier):

        Value = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF',
        }[value]
        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            self.__SetHelper('Power', pack('>B5s', deviceID, Value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            0x01: 'On',
            0x00: 'Off',
        }

        IRModeStateNames = {
            0x10: 'On',
            0x00: 'Off',
        }

        MirrorImageStateNames = {
            0x04: 'On',
            0x00: 'Off',
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            CmdString = pack('>B5s', deviceID, b'\x09\x7E\x7E\x02\xFF')
            res = self.__UpdateHelper('Power', CmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('Power', PowerStateNames[res[2] & 0x01], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response for Power'])
                try:
                    self.WriteStatus('InfraredMode', IRModeStateNames[res[3] & 0x10], qualifier)
                except (KeyError, IndexError):
                    self.Error(['InfraredMode: Invalid/unexpected response for Infrared Mode'])
                try:
                    self.WriteStatus('MirrorImage', MirrorImageStateNames[res[3] & 0x04], qualifier)
                except (KeyError, IndexError):
                    self.Error(['MirrorImage: Invalid/unexpected response for Mirror Image'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetPresetRecall(self, value, qualifier):

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            if 0 <= int(value) <= 127:
                PresetRecallCmdString = pack('>B4sBB', deviceID, b'\x01\x04\x3F\x02', int(value), 0xFF)
                self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPresetRecall')
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetReset(self, value, qualifier):

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            if 0 <= int(value) <= 127:
                PresetResetCmdString = pack('>B4sBB', deviceID, b'\x01\x04\x3F\x00', int(value), 0xFF)
                self.__SetHelper('PresetReset', PresetResetCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPresetReset')
        else:
            self.Discard('Invalid Command for SetPresetReset')

    def SetPresetSave(self, value, qualifier):

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            if 0 <= int(value) <= 127:
                PresetSaveCmdString = pack('>B4sBB', deviceID, b'\x01\x04\x3F\x01', int(value), 0xFF)
                self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPresetSave')
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetResolution(self, value, qualifier):

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            CmdString = pack('>B4s2s', deviceID, b'\x01\x06\x35\x00', self.Resolutions[value])
            self.__SetHelper('Resolution', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetResolution')

    def UpdateResolution(self, value, qualifier):
        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            CmdString = pack('>B4s', deviceID, b'\x09\x06\x23\xFF')
            res = self.__UpdateHelper('Resolution', CmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('Resolution', self.ResolutionValues[res[2]], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Resolution: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateResolution')

    def SetPresetSpeed1(self, value, qualifier):

        ValueStateValues = {
            '150 degree/second': b'\x01\x06\x20\x00\xFF',
            '250 degree/second': b'\x01\x06\x20\x01\xFF',
            '300 degree/second': b'\x01\x06\x20\x02\xFF'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            PresetSpeed1CmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('PresetSpeed1', PresetSpeed1CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSpeed1')

    def SetPresetSpeed2(self, value, qualifier):

        ValueStateValues = {
            '150 degree/second': b'\x01\x06\x20\x00\xFF',
            '250 degree/second': b'\x01\x06\x20\x01\xFF',
            '300 degree/second': b'\x01\x06\x20\x02\xFF',
            '5 degree/second': b'\x01\x06\x20\x03\xFF',
            '25 degree/second': b'\x01\x06\x20\x04\xFF',
            '50 degree/second': b'\x01\x06\x20\x05\xFF'
        }

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            PresetSpeed2CmdString = pack('>B5s', deviceID, ValueStateValues[value])
            self.__SetHelper('PresetSpeed2', PresetSpeed2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSpeed2')

    def SetTiltNormal(self, value, qualifier):

        TiltSpeed = int(qualifier['Tilt Speed'])

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:

            if 1 <= TiltSpeed <= 24:
                ValueStateValues = {
                    'Up': pack('>B4sB3s', deviceID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x01\xFF'),
                    'Down': pack('>B4sB3s', deviceID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x02\xFF'),
                    'Stop': pack('>B8s', deviceID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
                TiltNormalCmdString = ValueStateValues[value]
                self.__SetHelper('TiltNormal', TiltNormalCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTiltNormal')
        else:
            self.Discard('Invalid Command for SetTiltNormal')

    def SetTiltSmooth(self, value, qualifier):

        TiltSpeed = int(qualifier['Tilt Speed'])

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:

            if 1 <= TiltSpeed <= 100:
                ValueStateValues = {
                    'Up': pack('>B4sB3s', deviceID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x01\xFF'),
                    'Down': pack('>B4sB3s', deviceID, b'\x01\x06\x01\x00', TiltSpeed, b'\x03\x02\xFF'),
                    'Stop': pack('>B8s', deviceID, b'\x01\x06\x01\x01\x01\x03\x03\xFF')
                }
                TiltSmoothCmdString = ValueStateValues[value]
                self.__SetHelper('TiltSmooth', TiltSmoothCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetTiltSmooth')
        else:
            self.Discard('Invalid Command for SetTiltSmooth')

    def SetZoom(self, value, qualifier):

        ZoomSpeed = int(qualifier['Zoom Speed'])

        deviceID = self.SetDeviceID(qualifier['Device ID'])
        if deviceID:
            if 0 <= ZoomSpeed <= 7:
                Value = {
                    'Tele': pack('>B3sBB', deviceID, b'\x01\x04\x07', 0x20 + ZoomSpeed, 0xFF),
                    'Wide': pack('>B3sBB', deviceID, b'\x01\x04\x07', 0x30 + ZoomSpeed, 0xFF),
                    'Stop': pack('>B5s', deviceID, b'\x01\x04\x07\x00\xFF'),
                }[value]

                self.__SetHelper('Zoom', Value, value, qualifier)
            else:
                self.Discard('Invalid Command for SetZoom')
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x02': 'Syntax Error',
            b'\x03': 'Command buffer full',
            b'\x04': 'Command cancelled',
            b'\x05': 'No socket (to be cancelled)',
            b'\x41': 'Command not executable'
        }

        matchedInfo = re.search(self.matchError, response)

        if matchedInfo:
            self.Error(['{0} : {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[matchedInfo.group(1)])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xFF')
            if not res:
                self.Error(['No response received'])
            else:
                res = self.__CheckResponseForErrors(command, res)

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
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def lumn_19_550_A(self):

        self.Resolutions = {
            '1080p (60Hz)': b'\x00\xFF',
            '1080p (50Hz)': b'\x01\xFF',
            '1080p (30Hz)': b'\x02\xFF',
            '1080p (25Hz)': b'\x03\xFF',
            '1080i (60Hz)': b'\x04\xFF',
            '1080i (50hz)': b'\x05\xFF',
            '720p (60Hz)': b'\x06\xFF',
            '720p (50hz)': b'\x07\xFF',
            '720p (30Hz)': b'\x08\xFF',
            '720p (25Hz)': b'\x09\xFF',
        }

        self.ResolutionValues = {
            0x00: '1080p (60Hz)',
            0x01: '1080p (50Hz)',
            0x02: '1080p (30Hz)',
            0x03: '1080p (25Hz)',
            0x04: '1080i (60Hz)',
            0x05: '1080i (50hz)',
            0x06: '720p (60Hz)',
            0x07: '720p (50hz)',
            0x08: '720p (30Hz)',
            0x09: '720p (25Hz)',
        }

    def lumn_19_550_B(self):

        self.Resolutions = {
            '1080p (60Hz)': b'\x00\xFF',
            '1080p (50Hz)': b'\x01\xFF',
            '1080p (30Hz)': b'\x02\xFF',
            '1080p (25Hz)': b'\x03\xFF',
            '1080i (60Hz)': b'\x04\xFF',
            '1080i (50hz)': b'\x05\xFF',
            '720p (60Hz)': b'\x06\xFF',
            '720p (50hz)': b'\x07\xFF',
            '720p (30Hz)': b'\x08\xFF',
            '720p (25Hz)': b'\x09\xFF',
            '1080p (5994)': b'\x0A\xFF',
            '1080i (5994)': b'\x0B\xFF',
            '1080p (2997)': b'\x0C\xFF',
            '720p (5994)': b'\x0D\xFF',
            '720p (2997)': b'\x0E\xFF',
        }

        self.ResolutionValues = {
            0x00: '1080p (60Hz)',
            0x01: '1080p (50Hz)',
            0x02: '1080p (30Hz)',
            0x03: '1080p (25Hz)',
            0x04: '1080i (60Hz)',
            0x05: '1080i (50hz)',
            0x06: '720p (60Hz)',
            0x07: '720p (50hz)',
            0x08: '720p (30Hz)',
            0x09: '720p (25Hz)',
            0x0A: '1080p (5994)',
            0x0B: '1080i (5994)',
            0x0C: '1080p (2997)',
            0x0D: '720p (5994)',
            0x0E: '720p (2997)',
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')

            # This method is to tie an specific command with a parameter to a call back method

    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method': {}}

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
            print(command, 'does not exist in the module')

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription:
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
        Command = self.Commands[command]
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


class SerialClass(SerialInterface, DeviceClass):
    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
