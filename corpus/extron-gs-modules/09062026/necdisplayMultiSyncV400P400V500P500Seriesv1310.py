from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
from binascii import hexlify
import re
from functools import reduce
from operator import xor

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
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioInput': {'Parameters': ['Device ID'], 'Status': {}},
            'AudioMute': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoImage': {'Parameters': ['Device ID'], 'Status': {}},
            'Backlight': {'Parameters': ['Device ID'], 'Status': {}},
            'Brightness': {'Parameters': ['Device ID'], 'Status': {}},
            'ClosedCaption': {'Parameters': ['Device ID'], 'Status': {}},
            'Contrast': {'Parameters': ['Device ID'], 'Status': {}},
            'GammaCorrection': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'LineOut': {'Parameters': ['Device ID'], 'Status': {}},
            'OnScreenDisplay': {'Parameters': ['Device ID'], 'Status': {}},
            'Overscan': {'Parameters': ['Device ID'], 'Status': {}},
            'PictureMode': {'Parameters': ['Device ID'], 'Status': {}},
            'PIPMode': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
            'TileHMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrix': {'Parameters': ['Device ID'], 'Status': {}},
            'TileMatrixComp': {'Parameters': ['Device ID'], 'Status': {}},
            'TilePosition': {'Parameters': ['Device ID'], 'Status': {}},
            'TileVMonitor': {'Parameters': ['Device ID'], 'Status': {}},
            'TVChannelCommand': {'Parameters': ['Device ID'], 'Status': {}},
            'TVChannelStatus': {'Parameters': ['Device ID'], 'Status': {}},
            'TVChannelStep': {'Parameters': ['Device ID'], 'Status': {}},
            'VideoMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Volume': {'Parameters': ['Device ID'], 'Status': {}},
            'VolumeStep': {'Parameters': ['Device ID'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.SetRegAspectRatio = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]027000[\x00-\xFF]{8}\x03')
            self.SetRegAudioInput = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]022E00[\x00-\xFF]{8}\x03')
            self.SetRegAudioMute = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]008D00[\x00-\xFF]{8}\x03')
            self.SetRegAutoImage = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]001E01[\x00-\xFF]{8}\x03')
            self.SetRegBacklight = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]001000[\x00-\xFF]{8}\x03')
            self.SetRegBrightness = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]009200[\x00-\xFF]{8}\x03')
            self.SetRegClosedCaption = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]108400[\x00-\xFF]{8}\x03')
            self.SetRegContrast = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]001200[\x00-\xFF]{8}\x03')
            self.SetRegGammaCorrection = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]026800[\x00-\xFF]{8}\x03')
            self.SetRegInput = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]006000[\x00-\xFF]{8}\x03')
            self.SetRegLineOut = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]108100[\x00-\xFF]{8}\x03')
            self.SetRegOnScreenDisplay = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02EA00[\x00-\xFF]{8}\x03')
            self.SetRegOverscan = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02E300[\x00-\xFF]{8}\x03')
            self.SetRegPictureMode = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]105100[\x00-\xFF]{8}\x03')
            self.SetRegPIPMode = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]027200[\x00-\xFF]{8}\x03')
            self.SetRegPower = re.compile(b'\x0100[\x00-\xFF]{2}0E\x020[01]C203D6[\x00-\xFF]{6}\r')
            self.SetRegTileHMonitor = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D000[\x00-\xFF]{8}\x03')
            self.SetRegTileMatrix = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D300[\x00-\xFF]{8}\x03')
            self.SetRegTileMatrixComp = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D500[\x00-\xFF]{8}\x03')
            self.SetRegTilePosition = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D200[\x00-\xFF]{8}\x03')
            self.SetRegTileVMonitor = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D100[\x00-\xFF]{8}\x03')
            self.SetRegTVChannelStep = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]008B00[\x00-\xFF]{8}\x03')
            self.SetRegTVChannelCommand = re.compile(b'\x0100[\x00-\xFF]{2}12\x02C32D[\x00-\xFF]{12}\x03')
            self.SetRegVideoMute = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]10B600[\x00-\xFF]{8}\x03')
            self.SetRegVolume = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]006200[\x00-\xFF]{8}\x03')
            self.SetRegVolumeStep = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]10AD00[\x00-\xFF]{8}\x03')

            self.GetRegAspectRatio = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]027000[\x00-\xFF]{8}\x03')
            self.GetRegAudioInput = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]022E00[\x00-\xFF]{8}\x03')
            self.GetRegAudioMute = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]008D00[\x00-\xFF]{8}\x03')
            self.GetRegBacklight = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]001000[\x00-\xFF]{8}\x03')
            self.GetRegBrightness = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]009200[\x00-\xFF]{8}\x03')
            self.GetRegContrast = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]001200[\x00-\xFF]{8}\x03')
            self.GetRegGammaCorrection = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]026800[\x00-\xFF]{8}\x03')
            self.GetRegInput = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]006000[\x00-\xFF]{8}\x03')
            self.GetRegLineOut = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]108100[\x00-\xFF]{8}\x03')
            self.GetRegMasterPower = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[12]00D6[\x00-\xFF]{10}\x03')
            self.GetRegOnScreenDisplay = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02EA00[\x00-\xFF]{8}\x03')
            self.GetRegOverscan = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02E300[\x00-\xFF]{8}\x03')
            self.GetRegPictureMode = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]105100[\x00-\xFF]{8}\x03')
            self.GetRegPIPMode = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]027200[\x00-\xFF]{8}\x03')
            self.GetRegPower = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[12]00D600[\x00-\xFF]{8}\x03')
            self.GetRegTileMatrix = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]02D300[\x00-\xFF]{8}\x03')
            self.GetRegTVChannelStatus = re.compile(b'\x0100[\x00-\xFF]{2}12\x02C32C[\x00-\xFF]{12}\x03')
            self.GetRegVideoMute = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]10B600[\x00-\xFF]{8}\x03')
            self.GetRegVolume = re.compile(b'\x0100[\x00-\xFF]{2}12\x020[01]006200[\x00-\xFF]{8}\x03')

            self.SetDelim = {
                'AspectRatio': self.SetRegAspectRatio,
                'AudioInput': self.SetRegAudioInput,
                'AudioMute': self.SetRegAudioMute,
                'AutoImage': self.SetRegAutoImage,
                'Backlight': self.SetRegBacklight,
                'Brightness': self.SetRegBrightness,
                'ClosedCaption': self.SetRegClosedCaption,
                'Contrast': self.SetRegContrast,
                'GammaCorrection': self.SetRegGammaCorrection,
                'Input': self.SetRegInput,
                'LineOut': self.SetRegLineOut,
                'OnScreenDisplay': self.SetRegOnScreenDisplay,
                'Overscan': self.SetRegOverscan,
                'PictureMode': self.SetRegPictureMode,
                'PIPMode': self.SetRegPIPMode,
                'Power': self.SetRegPower,
                'TileHMonitor': self.SetRegTileHMonitor,
                'TileMatrix': self.SetRegTileMatrix,
                'TileMatrixComp': self.SetRegTileMatrixComp,
                'TilePosition': self.SetRegTilePosition,
                'TileVMonitor': self.SetRegTileVMonitor,
                'TVChannelCommand': self.SetRegTVChannelCommand,
                'TVChannelStep': self.SetRegTVChannelStep,
                'VideoMute': self.SetRegVideoMute,
                'Volume': self.SetRegVolume,
                'VolumeStep': self.SetRegVolumeStep
            }

            self.UpdateDelim = {
                'AspectRatio': self.GetRegAspectRatio,
                'AudioInput': self.GetRegAudioInput,
                'AudioMute': self.GetRegAudioMute,
                'Backlight': self.GetRegBacklight,
                'Brightness': self.GetRegBrightness,
                'Contrast': self.GetRegContrast,
                'GammaCorrection': self.GetRegGammaCorrection,
                'Input': self.GetRegInput,
                'LineOut': self.GetRegLineOut,
                'OnScreenDisplay': self.GetRegOnScreenDisplay,
                'Overscan': self.GetRegOverscan,
                'PictureMode': self.GetRegPictureMode,
                'PIPMode': self.GetRegPIPMode,
                'Power': self.GetRegPower,
                'TileMatrix': self.GetRegTileMatrix,
                'TVChannelStatus': self.GetRegTVChannelStatus,
                'VideoMute': self.GetRegVideoMute,
                'Volume': self.GetRegVolume
            }

        self.groupID = {
            'Broadcast': 0x2A,
            'Group A': 0x31,
            'Group B': 0x32,
            'Group C': 0x33,
            'Group D': 0x34,
            'Group E': 0x35,
            'Group F': 0x36,
            'Group G': 0x37,
            'Group H': 0x38,
            'Group I': 0x39,
            'Group J': 0x3A
        }


    def SetQualifierDeviceID(self, value):
        if value == 'Broadcast':
            return 0x2A
        elif 'Group ' in value:
            return self.groupID[value]
        elif 1 <= int(value) <= 100:
            return 0x40 + int(value)
        else:
            return False

    def To_keep_alive(self):
        checksum = reduce(xor, b'\x30\x2A0A06\x0201D6\x03').to_bytes(1, 'big')
        cmdString = b''.join([b'\x01\x30\x2A0A06\x0201D6\x03', checksum, b'\r'])
        self.Send(cmdString)
        self.SixHundredSecs.Restart()

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'0E0A\x0202700001\x03',
            'Full': b'0E0A\x0202700002\x03',
            'Wide': b'0E0A\x0202700003\x03',
            'Zoom': b'0E0A\x0202700004\x03',
            'Dynamic': b'0E0A\x0202700006\x03',
            '1:1': b'0E0A\x0202700007\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AspectRatioCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Normal',
            b'2': 'Full',
            b'4': 'Wide',
            b'3': 'Zoom',
            b'6': 'Dynamic',
            b'7': '1:1'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020270\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AspectRatioCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Aspect Ratio: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def SetAudioInput(self, value, qualifier):

        ValueStateValues = {
            'IN1': b'0E0A\x02022E0001\x03',
            'IN2': b'0E0A\x02022E0002\x03',
            'HDMI 1': b'0E0A\x02022E0004\x03',
            'Option': b'0E0A\x02022E0006\x03',
            'DisplayPort 1': b'0E0A\x02022E0007\x03',
            'DisplayPort 2': b'0E0A\x02022E0008\x03',
            'HDMI 2': b'0E0A\x02022E000A\x03',
            'MP': b'0E0A\x02022E000D\x03',
            'Compute Module': b'0E0A\x02022E000E\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AudioInputCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('AudioInput', AudioInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInput')

    def UpdateAudioInput(self, value, qualifier):

        ValueStateValues = {
            b'1': 'IN1',
            b'2': 'IN2',
            b'4': 'HDMI 1',
            b'6': 'Option',
            b'7': 'DisplayPort 1',
            b'8': 'DisplayPort 2',
            b'A': 'HDMI 2',
            b'D': 'MP',
            b'E': 'Compute Module'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x02022E\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AudioInputCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('AudioInput', AudioInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AudioInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioInput')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x02008D0001\x03',
            'Off': b'0E0A\x02008D0002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AudioMuteCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'2': 'Off',
            b'0': 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x02008D\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AudioMuteCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAutoImage(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, b'0E0A\x02001E0001\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            AutoImageCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001000', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            BacklightCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def UpdateBacklight(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020010\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            BacklightCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Backlight', BacklightCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Backlight', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Backlight: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBacklight')

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02009200', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            BrightnessCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020092\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            BrightnessCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Brightness', BrightnessCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Brightness', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Brightness: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'CC1': b'0E0A\x0210840002\x03',
            'CC2': b'0E0A\x0210840003\x03',
            'CC3': b'0E0A\x0210840004\x03',
            'CC4': b'0E0A\x0210840005\x03',
            'TT1': b'0E0A\x0210840006\x03',
            'TT2': b'0E0A\x0210840007\x03',
            'TT3': b'0E0A\x0210840008\x03',
            'TT4': b'0E0A\x0210840009\x03',
            'Off': b'0E0A\x0210840001\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            ClosedCaptionCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02001200', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            ContrastCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def UpdateContrast(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020012\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            ContrastCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Contrast', ContrastCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Contrast', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Contrast: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateContrast')

    def SetGammaCorrection(self, value, qualifier):

        ValueStateValues = {
            'Native': b'0E0A\x0202680001\x03',
            '2.2': b'0E0A\x0202680004\x03',
            '2.4': b'0E0A\x0202680008\x03',
            'S Gamma': b'0E0A\x0202680007\x03',
            'DICOM SIM': b'0E0A\x0202680005\x03',
            'Programmable 1': b'0E0A\x0202680006\x03',
            'Programmable 2': b'0E0A\x020268000B\x03',
            'Programmable 3': b'0E0A\x020268000C\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            GammaCorrectionCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGammaCorrection')

    def UpdateGammaCorrection(self, value, qualifier):

        ValueStateValues = {
            b'01': 'Native',
            b'04': '2.2',
            b'08': '2.4',
            b'07': 'S Gamma',
            b'05': 'DICOM SIM',
            b'06': 'Programmable 1',
            b'0B': 'Programmable 2',
            b'0C': 'Programmable 3'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020268\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            GammaCorrectionCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('GammaCorrection', GammaCorrectionCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('GammaCorrection', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Gamma Correction: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGammaCorrection')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA (RGB)': b'0E0A\x0200600001\x03',
            'DVI': b'0E0A\x0200600003\x03',
            'Video': b'0E0A\x0200600005\x03',
            'YGA (YPbPr)': b'0E0A\x020060000C\x03',
            'Option': b'0E0A\x020060000D\x03',
            'DisplayPort 1': b'0E0A\x020060000F\x03',
            'DisplayPort 2': b'0E0A\x0200600010\x03',
            'HDMI 1': b'0E0A\x0200600011\x03',
            'HDMI 2': b'0E0A\x0200600012\x03',
            'MP': b'0E0A\x0200600087\x03',
            'Compute Module': b'0E0A\x0200600088\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            InputCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            b'01': 'VGA (RGB)',
            b'03': 'DVI',
            b'05': 'Video',
            b'0C': 'YGA (YPbPr)',
            b'0D': 'Option',
            b'0F': 'DisplayPort 1',
            b'10': 'DisplayPort 2',
            b'11': 'HDMI 1',
            b'12': 'HDMI 2',
            b'87': 'MP',
            b'88': 'Compute Module'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020060\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            InputCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInput')

    def SetLineOut(self, value, qualifier):

        ValueStateValues = {
            'Fixed': b'0E0A\x0210810001\x03',
            'Variable': b'0E0A\x0210810002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            LineOutCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('LineOut', LineOutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOut')

    def UpdateLineOut(self, value, qualifier):

        ValueStateValues = {
            b'01': 'Fixed',
            b'02': 'Variable'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x021081\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            LineOutCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('LineOut', LineOutCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('LineOut', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['LineOut: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLineOut')

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0202EA0002\x03',
            'Off': b'0E0A\x0202EA0001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            OnScreenDisplayCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOnScreenDisplay')

    def UpdateOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'1': 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202EA\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            OnScreenDisplayCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('OnScreenDisplay', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['On Screen Display: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOnScreenDisplay')

    def SetOverscan(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0202E30002\x03',
            'Off': b'0E0A\x0202E30001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            OverscanCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Overscan', OverscanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverscan')

    def UpdateOverscan(self, value, qualifier):

        ValueStateValues = {
            b'3': 'Auto',
            b'2': 'On',
            b'1': 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202E3\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            OverscanCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Overscan', OverscanCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('Overscan', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Overscan: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOverscan')

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'sRGB': b'0E0A\x021051000\x31\x03',
            'Adobe RGB SIM': b'0E0A\x021051000\x32\x03',
            'DCI SIM': b'0E0A\x021051000\x33\x03',
            'REC-Bt709': b'0E0A\x021051000\x34\x03',
            'High Bright': b'0E0A\x021051000\x35\x03',
            'Full': b'0E0A\x021051000\x36\x03',
            'DICOM SIM': b'0E0A\x021051000\x37\x03',
            'Programmable 1': b'0E0A\x021051000\x38\x03',
            'Programmable 2': b'0E0A\x021051000\x39\x03',
            'Programmable 3': b'0E0A\x021051000\x41\x03',
            'Programmable 4': b'0E0A\x021051000\x42\x03',
            'Programmable 5': b'0E0A\x021051000\x43\x03',
            'eciRGB v2': b'0E0A\x021051000\x44\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PictureModeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def UpdatePictureMode(self, value, qualifier):

        ValueStateValues = {
            b'01': 'sRGB',
            b'02': 'Adobe RGB SIM',
            b'03': 'DCI SIM',
            b'04': 'REC-Bt709',
            b'05': 'High Bright',
            b'06': 'Full',
            b'07': 'DICOM SIM',
            b'08': 'Programmable 1',
            b'09': 'Programmable 2',
            b'0A': 'Programmable 3',
            b'0B': 'Programmable 4',
            b'0C': 'Programmable 5',
            b'0D': 'eciRGB v2'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x021051\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PictureModeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[22:24]]
                    self.WriteStatus('PictureMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Picture Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePictureMode')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'0E0A\x0202720001\x03',
            'PIP': b'0E0A\x0202720002\x03',
            'Picture by Picture': b'0E0A\x0202720005\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PIPModeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            b'1': 'Off',
            b'2': 'PIP',
            b'5': 'Picture by Picture'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020272\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PIPModeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('PIPMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['PIP Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePIPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'0A0C\x02C203D60001\x03',
            'Off': b'0A0C\x02C203D60004\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB16s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PowerCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'2': 'Standby (Power Save)',
            b'3': 'Suspend (Power Save)',
            b'4': 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0A06\x0201D6\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            PowerCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('Power', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Power: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdatePower')

    def SetTileHMonitor(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        value = int(value)
        if DeviceID != 0 and 1 <= value <= 10:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D000', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TileHMonitorCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TileHMonitor', TileHMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileHMonitor')

    def SetTileMatrix(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0202D30002\x03',
            'Off': b'0E0A\x0202D30001\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TileMatrixCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrix')

    def UpdateTileMatrix(self, value, qualifier):

        ValueStateValues = {
            b'2': 'On',
            b'1': 'Off',
            b'3': 'Off'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0202D3\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TileMatrixCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('TileMatrix', TileMatrixCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('TileMatrix', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tile Matrix: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTileMatrix')

    def SetTileMatrixComp(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'0E0A\x0202D50002\x03',
            'Disable': b'0E0A\x0202D50001\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TileMatrixCompCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TileMatrixComp', TileMatrixCompCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileMatrixComp')

    def SetTilePosition(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        value = int(value)
        if DeviceID != 0 and 1 <= value <= 100:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D200', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TilePositionCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TilePosition', TilePositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilePosition')

    def SetTileVMonitor(self, value, qualifier):

        value = int(value)
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and 1 <= value <= 10:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x0202D100', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TileVMonitorCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TileVMonitor', TileVMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTileVMonitor')

    def SetTVChannelCommand(self, value, qualifier):

        temp = value
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and temp:
            try:
                channel = temp.split('.')
                if len(channel) == 2:  # If there's a successful split for the channel
                    upper_val = int(channel[0])
                    lower_val = int(channel[1])

                    if (0 <= upper_val <= 65535) and (0 <= lower_val <= 65535):
                        upperChannel = '{0:04X}'.format(int(channel[0])).encode()
                        lowerChannel = '{0:04X}'.format(int(channel[1])).encode()
                        channelByte = b''.join([b'0A12\x02C22D0000', upperChannel, lowerChannel, b'\x03'])
                        buffer = pack('>BB22s', 0x30, DeviceID, channelByte)
                        checksum = reduce(xor, buffer).to_bytes(1, 'big')
                        TVChannelCommandCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
                        self.__SetHelper('TVChannelCommand', TVChannelCommandCmdString, value, qualifier)
                    else:
                        self.Discard('Invalid Command for SetTVChannelCommand')
                else:
                    self.Discard('Invalid Command for SetTVChannelCommand')
            except ValueError:
                self.Discard('Invalid Command for SetTVChannelCommand')
        else:
            self.Discard('Invalid Command for SetTVChannelCommand')

    def UpdateTVChannelStatus(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0A06\x02C22C\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TVChannelStatusCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])

            res = self.__UpdateHelper('TVChannelStatus', TVChannelStatusCmdString, value, qualifier)
            if res:
                try:
                    major = int(res[12:20], 16)
                    minor = int(res[20:24], 16)
                    value = '{}.{}'.format(major, minor)
                    self.WriteStatus('TVChannelStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['TV Channel Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTVChannelStatus')

    def SetTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'0E0A\x02008B0001\x03',
            'Down': b'0E0A\x02008B0002\x03'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            TVChannelStepCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('TVChannelStep', TVChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTVChannelStep')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'0E0A\x0210B60001\x03',
            'Off': b'0E0A\x0210B60002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            MuteCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('VideoMute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            b'1': 'On',
            b'2': 'Off',
            b'0': 'No Signal'
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x0210B6\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            MuteCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('VideoMute', MuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[23:24]]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            result = hexlify(value.to_bytes(1, 'big')).upper()
            buffer = pack('>BB11s2ss', 0x30, DeviceID, b'0E0A\x02006200', result, b'\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            VolumeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB10s', 0x30, DeviceID, b'0C06\x020062\x03')
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            VolumeCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[22:24], 16)
                    self.WriteStatus('Volume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'0E0A\x0210AD0001\x03',
            'Down': b'0E0A\x0210AD0002\x03'
        }

        DeviceID = self.SetQualifierDeviceID(qualifier['Device ID'])
        if DeviceID != 0:
            buffer = pack('>BB14s', 0x30, DeviceID, ValueStateValues[value])
            checksum = reduce(xor, buffer).to_bytes(1, 'big')
            VolumeStepCmdString = b''.join([b'\x01', buffer, checksum, b'\r'])
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response and response[8:10].decode() == '01':
            self.Error(['{0} : An Error Occurred'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):  # all sets in legacy driver have a queryDelay of 10
        self.Debug = True

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand' or qualifier['Device ID'] == 'Broadcast' or 'Group ' in qualifier['Device ID']:
            self.Send(commandstring)
        else:
            regex = self.SetDelim[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                self.Error(['{0} : Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast' or 'Group ' in qualifier['Device ID']:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            regex = self.UpdateDelim[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        if self.ConnectionType == 'Ethernet':
            self.SixHundredSecs.Restart() 

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        if self.ConnectionType == 'Ethernet':
            self.SixHundredSecs.Cancel() 

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()

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

        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

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

        self.SixHundredSecs = Wait(600, self.To_keep_alive)
        self.SixHundredSecs.Cancel()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

