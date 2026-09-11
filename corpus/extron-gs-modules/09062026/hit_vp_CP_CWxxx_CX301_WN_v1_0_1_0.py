from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re
import hashlib
from binascii import hexlify


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'CCChannel': {'Status': {}},
            'CCMode': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'EcoMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['Type'], 'Status': {}},
        }

        self.Authenticated = 'Not Needed'

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)

        self.Deliregex = re.compile(b'(\x06|\x15|[\x1C\x1F][\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def __MatchPassword(self, match, tag):

        if self.devicePassword:
            outStr = match.group(1).decode() + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest()) + b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Authenticated = 'Admin'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        States = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00'
        }

        self.__SetHelper('AspectRatio', States[value], value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        States = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x09': '14:9',
            b'\x0A': '16:10',
            b'\x10': 'Normal',
            b'\x08': 'Native'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x20\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x20\x20\x00\x00'
        }

        self.__SetHelper('AudioMute', States[value], value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        CmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', CmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\x6E\xF1\x01\x00\xA0\x20\x10\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xF0\x01\x00\xA0\x20\x00\x00'
        }

        self.__SetHelper('AVMute', States[value], value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xCD\xF0\x02\x00\xA0\x20\x00\x00'
        res = self.__UpdateHelper('AVMute', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/unexpected response'])

    def SetCCChannel(self, value, qualifier):

        States = {
            '1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4': b'\xBE\xEF\x03\x06\x00\xD2\x82\x01\x00\x02\x37\x04\x00'
        }

        self.__SetHelper('CCChannel', States[value], value, qualifier)

    def UpdateCCChannel(self, value, qualifier):

        States = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('CCChannel', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('CCChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['CC Channel: Invalid/unexpected response'])

    def SetCCMode(self, value, qualifier):

        States = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }

        self.__SetHelper('CCMode', States[value], value, qualifier)

    def UpdateCCMode(self, value, qualifier):

        States = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('CCMode', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('CCMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['CC Mode: Invalid/unexpected response'])

    def SetClosedCaption(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }

        self.__SetHelper('ClosedCaption', States[value], value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        States = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02': 'Auto'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        States = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def SetEcoMode(self, value, qualifier):

        States = {
            'Off': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00',
            'Eco 1': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
            'Eco 2': b'\xBE\xEF\x03\x06\x00\x5B\x22\x01\x00\x00\x33\x02\x00',
            'Intelligent Eco': b'\xBE\xEF\x03\x06\x00\xFB\x2E\x01\x00\x00\x33\x10\x00',
            'Saver': b'\xBE\xEF\x03\x06\x00\xFB\x3A\x01\x00\x00\x33\x20\x00'
        }

        self.__SetHelper('EcoMode', States[value], value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        States = {
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
                value = States[res[1:2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Eco Mode: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString1 = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res1 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString1, value, qualifier)

        FilterUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'
        res2 = self.__UpdateHelper('FilterUsage', FilterUsageCmdString2, value, qualifier)

        if res1 and res2:
            try:
                value = 256 * res2[1] + res1[1]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        self.__SetHelper('Freeze', States[value], value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        States = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
        }

        self.__SetHelper('Input', States[value], value, qualifier)

    def UpdateInput(self, value, qualifier):

        States = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x01': 'Video',
            b'\x06': 'USB Type A',
            b'\x0C': 'USB Type B',
            b'\x0B': 'LAN',
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString1 = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res1 = self.__UpdateHelper('LampUsage', LampUsageCmdString1, value, qualifier)

        LampUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'
        res2 = self.__UpdateHelper('LampUsage', LampUsageCmdString2, value, qualifier)
        if res1 and res2:
            try:
                value = 256 * res2[1] + res1[1]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPictureMode(self, value, qualifier):

        States = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00',
            'Cinema': b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00',
            'Dynamic': b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00',
            'Board (Black)': b'\xBE\xEF\x03\x06\x00\xE3\xEF\x01\x00\xBA\x30\x20\x00',
            'Board (Green)': b'\xBE\xEF\x03\x06\x00\x73\xEE\x01\x00\xBA\x30\x21\x00',
            'Whiteboard': b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00',
            'Day Time': b'\xBE\xEF\x03\x06\x00\xE3\xC7\x01\x00\xBA\x30\x40\x00',
            'Photo': b'\xBE\xEF\x03\x06\x00\x73\xF5\x01\x00\xBA\x30\x05\x00',
        }

        self.__SetHelper('PictureMode', States[value], value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        States = {
            b'\x00': 'Normal',
            b'\x01': 'Cinema',
            b'\x04': 'Dynamic',
            b'\x20': 'Board (Black)',
            b'\x21': 'Board (Green)',
            b'\x22': 'Whiteboard',
            b'\x40': 'Day Time',
            b'\x05': 'Photo',
            b'\x10': 'Custom'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Mode: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00'
        }

        self.__SetHelper('Power', States[value], value, qualifier)

    def UpdatePower(self, value, qualifier):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cooling Down'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        States = {
            'On': b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        self.__SetHelper('VideoMute', States[value], value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        States = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }

        CmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', CmdString, value, qualifier)
        if res:
            try:
                value = States[res[1:2]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        Computer1 = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }
        Computer2 = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }
        Video = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }
        HDMI1 = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }
        HDMI2 = {
            'Up': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00'
        }
        LAN = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }
        USBA = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }
        USBB = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }
        Standby = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }
        All = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xC3\x04\x00\x50\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xC2\x05\x00\x50\x20\x00\x00'
        }

        TypeStates = {
            'Computer 1': Computer1,
            'Computer 2': Computer2,
            'HDMI 1': HDMI1,
            'HDMI 2': HDMI2,
            'Video': Video,
            'LAN': LAN,
            'USB Type A': USBA,
            'USB Type B': USBB,
            'Standby': Standby,
            'All': All,
        }

        typeVal = qualifier['Type']
        if typeVal in TypeStates:
            CmdString = TypeStates[typeVal][value]
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolumeStatus(self, value, qualifier):

        TypeStates = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00',
            'All': b'\xBE\xEF\x03\x06\x00\xCD\xC3\x02\x00\x50\x20\x00\x00',
        }

        typeVal = qualifier['Type']
        if typeVal in TypeStates:
            CmdString = TypeStates[typeVal]
            res = self.__UpdateHelper('VolumeStatus', CmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1])
                    self.WriteStatus('VolumeStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Volume Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolumeStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': 'Invalid Command.',
            b'\x1C': 'Busy.'
        }
        if len(response) == 8:
            self.__MatchPassword(response, None)
            response = ''
        elif response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            response = ''
        elif response[0:1] == b'\x1F':
            self.Authenticated = 'None'
            self.Error(['{0}: Authentication Error.'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Deliregex)
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Deliregex)
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command ' + command)
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
