from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify
from extronlib.system import ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'EcoMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Input Type'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['Input Type'], 'Status': {}},
        }

        self.Authenticated = 'Not Needed'
        self.devicePassword = None

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)
        self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            outStr = '{0}{1}'.format(value.decode(), self.devicePassword)
            code_hash = hashlib.md5(outStr.encode())
            CmdString = b''.join([hexlify(code_hash.digest()), b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'])
            self.Authenticated = 'Admin'
            self.Send(CmdString)
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):

        self.Authenticated = 'Authentication Needed'
        self.SetPassword(match.group(0), None)

    def SetAspectRatio(self, value, qualifier):

        Values = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        self.__SetHelper('AspectRatio', Values[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        Values = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native',
            b'\x10': 'Normal'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AspectRatio', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        CmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)  # Query Delay not needed, tested on CP-AW3005

    def SetClosedCaption(self, value, qualifier):

        Values = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }

        self.__SetHelper('ClosedCaption', Values[value], value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        Values = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Auto'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaption', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        Values = {
            '1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
        }

        self.__SetHelper('ClosedCaptionChannel', Values[value], value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        Values = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaptionChannel', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        Values = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }

        self.__SetHelper('ClosedCaptionMode', Values[value], value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        Values = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('ClosedCaptionMode', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        Values = {
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x08': 'Filter Error',
            b'\x03': 'Lamp Error',
            b'\x00': 'Normal',
            b'\x04': 'Temp Error'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('DeviceStatus', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        Values = {
            'Off': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00',
            'Eco 1': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
            'Eco 2': b'\xBE\xEF\x03\x06\x00\x5B\x22\x01\x00\x00\x33\x02\x00',
            'Intelligent Eco': b'\xBE\xEF\x03\x06\x00\xFB\x2E\x01\x00\x00\x33\x10\x00',
            'Saver': b'\xBE\xEF\x03\x06\x00\xFB\x3A\x01\x00\x00\x33\x20\x00'
        }

        self.__SetHelper('EcoMode', Values[value], value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        Values = {
            b'\x00': 'Off',
            b'\x01': 'Eco 1',
            b'\x02': 'Eco 2',
            b'\x10': 'Intelligent Eco',
            b'\x20': 'Saver'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('EcoMode', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('EcoMode', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        CmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', CmdString, value, qualifier)
        CmdString2 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'
        res2 = self.__UpdateHelper('FilterUsage', CmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1:2][0] * 256 + res[1:2][0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        Values = {
            'On': b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        self.__SetHelper('Freeze', Values[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        Values = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        CmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Freeze', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        Values = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.__SetHelper('Input', Values[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        Values = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x01': 'Video',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Input', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        CmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', CmdString, value, qualifier)
        CmdString2 = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'
        res2 = self.__UpdateHelper('LampUsage', CmdString2, value, qualifier)
        if res and res2:
            try:
                value = res2[1:2][0] * 256 + res[1:2][0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        Values = {
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
        }

        self.__SetHelper('AudioMute', Values[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        Values = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioMute', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        Values = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00',
            'Cinema': b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00',
            'Dynamic': b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00',
            'Board(Black)': b'\xBE\xEF\x03\x06\x00\xE3\xEF\x01\x00\xBA\x30\x20\x00',
            'Board(Green)': b'\xBE\xEF\x03\x06\x00\x73\xEE\x01\x00\xBA\x30\x21\x00',
            'Whiteboard': b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00',
            'Daytime': b'\xBE\xEF\x03\x06\x00\xE3\xC7\x01\x00\xBA\x30\x40\x00',
            'Photo': b'\xBE\xEF\x03\x06\x00\x73\xF5\x01\x00\xBA\x30\x05\x00',
            'DICOM SIM': b'\xBE\xEF\x03\x06\x00\x73\xC6\x01\x00\xBA\x30\x41\x00',
        }

        self.__SetHelper('PictureMode', Values[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        Values = {
            b'\x00': 'Normal',
            b'\x01': 'Cinema',
            b'\x04': 'Dynamic',
            b'\x20': 'Board(Black)',
            b'\x21': 'Board(Green)',
            b'\x22': 'Whiteboard',
            b'\x40': 'Daytime',
            b'\x05': 'Photo',
            b'\x41': 'DICOM SIM',
            b'\x10': 'Custom'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('PictureMode', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        Values = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00',
        }

        self.__SetHelper('Power', Values[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        Values = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02': 'Cooling Down'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Power', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        Values = {
            'On': b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00',
        }

        self.__SetHelper('VideoMute', Values[value], value, qualifier, )

    def UpdateVideoMute(self, value, qualifier):

        Values = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('VideoMute', Values[res[1:2]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        InInc = {
            'Computer In1': b'\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Computer In2': b'\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Video': b'\x57\xCD\x04\x00\x61\x20\x00\x00',
            'HDMI 1': b'\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'LAN': b'\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'USB Type A': b'\x23\xCC\x04\x00\x66\x20\x00\x00',
            'USB Type B': b'\xFB\xCF\x04\x00\x6C\x20\x00\x00'
        }

        InDec = {
            'Computer In1': b'\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'Computer In2': b'\x4A\xCC\x05\x00\x64\x20\x00\x00',
            'Video': b'\x86\xCC\x05\x00\x61\x20\x00\x00',
            'HDMI 1': b'\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'LAN': b'\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xF2\xCD\x05\x00\x66\x20\x00\x00',
            'USB Type B': b'\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        if value == 'Up':
            CmdString = b''.join([b'\xBE\xEF\x03\x06\x00', InInc[qualifier['Input Type']]])
        if value == 'Down':
            CmdString = b''.join([b'\xBE\xEF\x03\x06\x00', InDec[qualifier['Input Type']]])
        self.__SetHelper('Volume', CmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        Inputs = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
        }

        res = self.__UpdateHelper('VolumeStatus', Inputs[qualifier['Input Type']], value, qualifier)
        if res:
            try:
                self.WriteStatus('VolumeStatus', int(res[1]), qualifier)
            except (IndexError, ValueError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Busy",
            b'\x1F': "Authentication Error"
        }

        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
                if not res:
                    self.Error(['{0}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
                if not res:
                    return ''
                else:
                    if len(res) == 8:
                        self.SetPassword(res, None)
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

        self.Authenticated = 'Not Needed'

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')

    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
            return None

    def __ReceiveData(self, interface, data):
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

    # Check incoming unsolicited data to see if it was matched with device expectancy.

    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
