from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.devicePassword = None

        self.Models = {
            'CP-X8170': self.hit_1_666_Xseries,
            'CP-WX8265': self.hit_1_666_Wseries,
            'CP-WU8460': self.hit_1_666_Wseries,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensMemory': {'Status': {}},
            'LensMemoryIndex': {'Status': {}},
            'PbyPLeftSource': {'Status': {}},
            'PbyPMainArea': {'Status': {}},
            'PbyPorPinPModeSelect': {'Status': {}},
            'PbyPRightSource': {'Status': {}},
            'PbyPSwap': {'Status': {}},
            'PinPMainArea': {'Status': {}},
            'PinPPosition': {'Status': {}},
            'PinPPrimarySource': {'Status': {}},
            'PinPSecondarySource': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Input'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['Input'], 'Status': {}},
        }

        if self.ConnectionType == 'Ethernet': # This will make sure that __MatchPassword is called for Ethernet connection
            self.Authenticated = 'Needed'  
            self.AddMatchString(re.compile(b'([A-Fa-f0-9]{8})'), self.__MatchPassword, None)
        else:
            self.Authenticated = 'Not Needed'
        self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2})')

    def __MatchPassword(self, match, tag):
        self.SetPassword(match.group(1), None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            inStr = value.decode()
            outStr = inStr + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest()) + b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Authenticated = 'Admin'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):
        AspectRatioCmdString = self.AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.AspectRatioStateNames[res[1:2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00',
        }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteStateNames[res[1:2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00',
        }
        ClosedCaptionCmdString = ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStateNames = {
            b'\x00': 'Auto',
            b'\x01': 'On',
            b'\x02': 'Off'
        }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionStateNames[res[1:2]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelStateValues = {
            '1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00',
        }
        ClosedCaptionChannelCmdString = ClosedCaptionChannelStateValues[value]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelStateNames = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionChannelStateNames[res[1:2]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateValues = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00',
        }
        ClosedCaptionModeCmdString = ClosedCaptionModeStateValues[value]
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeStateNames = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionModeStateNames[res[1:2]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusStateNames[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

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

        FreezeStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }
        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeStateNames[res[1:2]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
        }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputStateNames = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x0B': 'LAN',
            b'\x06': 'USB Type A',
            b'\x0C': 'USB Type B',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x05': 'Component',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputStateNames[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00',
            'Eco': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
        }
        LampModeCmdString = LampModeStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Eco',
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeStateNames[res[1:2]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

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

    def SetLensMemory(self, value, qualifier):

        LensMemoryStateValues = {
            'Load': b'\xBE\xEF\x03\x06\x00\xE8\x90\x06\x00\x08\x24\x00\x00',
            'Save': b'\xBE\xEF\x03\x06\x00\x14\x91\x06\x00\x09\x24\x00\x00',
            'Clear': b'\xBE\xEF\x03\x06\x00\x50\x91\x06\x00\x0A\x24\x00\x00',
        }
        LensMemoryCmdString = LensMemoryStateValues[value]
        self.__SetHelper('LensMemory', LensMemoryCmdString, value, qualifier)

    def SetLensMemoryIndex(self, value, qualifier):

        LensMemoryIndexStateValues = {
            '1': b'\xBE\xEF\x03\x06\x00\x4B\x92\x01\x00\x07\x24\x00\x00',
            '2': b'\xBE\xEF\x03\x06\x00\xDB\x93\x01\x00\x07\x24\x01\x00',
            '3': b'\xBE\xEF\x03\x06\x00\x2B\x93\x01\x00\x07\x24\x02\x00',
        }
        LensMemoryIndexCmdString = LensMemoryIndexStateValues[value]
        self.__SetHelper('LensMemoryIndex', LensMemoryIndexCmdString, value, qualifier)

    def UpdateLensMemoryIndex(self, value, qualifier):

        LensMemoryIndexStateNames = {
            b'\x00': '1',
            b'\x01': '2',
            b'\x02': '3',
        }

        LensMemoryIndexCmdString = b'\xBE\xEF\x03\x06\x00\x78\x92\x02\x00\x07\x24\x00\x00'
        res = self.__UpdateHelper('LensMemoryIndex', LensMemoryIndexCmdString, value, qualifier)
        if res:
            try:
                value = LensMemoryIndexStateNames[res[1:2]]
                self.WriteStatus('LensMemoryIndex', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lens Memory Index: Invalid/unexpected response'])

    def SetPbyPLeftSource(self, value, qualifier):

        PbyPLeftSourceStateValues = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xF2\x26\x01\x00\x15\x23\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x32\x24\x01\x00\x15\x23\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x02\x26\x01\x00\x15\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x15\x23\x0D\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xA2\x25\x01\x00\x15\x23\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x92\x27\x01\x00\x15\x23\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x62\x27\x01\x00\x15\x23\x01\x00',
        }
        PbyPLeftSourceCmdString = PbyPLeftSourceStateValues[value]
        self.__SetHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)

    def UpdatePbyPLeftSource(self, value, qualifier):

        PbyPLeftSourceStateNames = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x05': 'Component',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
        }

        PbyPLeftSourceCmdString = b'\xBE\xEF\x03\x06\x00\xC1\x26\x02\x00\x15\x23\x00\x00'
        res = self.__UpdateHelper('PbyPLeftSource', PbyPLeftSourceCmdString, value, qualifier)
        if res:
            try:
                value = PbyPLeftSourceStateNames[res[1:2]]
                self.WriteStatus('PbyPLeftSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Left Source: Invalid/unexpected response'])

    def SetPbyPMainArea(self, value, qualifier):

        PbyPMainAreaStateValues = {
            'Left': b'\xBE\xEF\x03\x06\x00\x7A\x26\x01\x00\x13\x23\x00\x00',
            'Right': b'\xBE\xEF\x03\x06\x00\xEA\x27\x01\x00\x13\x23\x01\x00',
        }
        PbyPMainAreaCmdString = PbyPMainAreaStateValues[value]
        self.__SetHelper('PbyPMainArea', PbyPMainAreaCmdString, value, qualifier)

    def UpdatePbyPMainArea(self, value, qualifier):

        PbyPMainAreaStateNames = {
            b'\x00': 'Left',
            b'\x01': 'Right'
        }

        PbyPMainAreaCmdString = b'\xBE\xEF\x03\x06\x00\x49\x26\x02\x00\x13\x23\x00\x00'
        res = self.__UpdateHelper('PbyPMainArea', PbyPMainAreaCmdString, value, qualifier)
        if res:
            try:
                value = PbyPMainAreaStateNames[res[1:2]]
                self.WriteStatus('PbyPMainArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Main Area: Invalid/unexpected response'])

    def SetPbyPorPinPModeSelect(self, value, qualifier):

        PbyPPinPStateValues = {
            'PbyP': b'\xBE\xEF\x03\x06\x00\xAE\x27\x01\x00\x10\x23\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00',
            'PinP': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x10\x23\x02\x00'
        }
        PbyPorPinPModeSelectCmdString = PbyPPinPStateValues[value]
        self.__SetHelper('PbyPorPinPModeSelect', PbyPorPinPModeSelectCmdString, value, qualifier)

    def UpdatePbyPorPinPModeSelect(self, value, qualifier):

        PbyPPinPStateNames = {
            b'\x00': 'Off',
            b'\x01': 'PbyP',
            b'\x02': 'PinP'
        }

        PbyPorPinPModeSelectCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyPorPinPModeSelect', PbyPorPinPModeSelectCmdString, value, qualifier)
        if res:
            try:
                value = PbyPPinPStateNames[res[1:2]]
                self.WriteStatus('PbyPorPinPModeSelect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP or PinP Mode Select: Invalid/unexpected response'])

    def SetPbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateValues = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\x86\x27\x01\x00\x12\x23\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x46\x25\x01\x00\x12\x23\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x76\x27\x01\x00\x12\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x16\x23\x01\x00\x12\x23\x0D\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xD6\x24\x01\x00\x12\x23\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\xE6\x26\x01\x00\x12\x23\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x16\x26\x01\x00\x12\x23\x01\x00',
        }
        PbyPRightSourceCmdString = PbyPRightSourceStateValues[value]
        self.__SetHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)

    def UpdatePbyPRightSource(self, value, qualifier):

        PbyPRightSourceStateNames = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x05': 'Component',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
        }

        PbyPRightSourceCmdString = b'\xBE\xEF\x03\x06\x00\xB5\x27\x02\x00\x12\x23\x00\x00'
        res = self.__UpdateHelper('PbyPRightSource', PbyPRightSourceCmdString, value, qualifier)
        if res:
            try:
                value = PbyPRightSourceStateNames[res[1:2]]
                self.WriteStatus('PbyPRightSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PbyP Right Source: Invalid/unexpected response'])

    def SetPbyPSwap(self, value, qualifier):

        PbyPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPSwap', PbyPSwapCmdString, value, qualifier)

    def SetPinPMainArea(self, value, qualifier):

        PinPMainAreaStateValues = {
            'Primary': b'\xBE\xEF\x03\x06\x00\x32\x22\x01\x00\x05\x23\x00\x00',
            'Secondary': b'\xBE\xEF\x03\x06\x00\xA2\x23\x01\x00\x05\x23\x01\x00'
        }
        PinPMainAreaCmdString = PinPMainAreaStateValues[value]
        self.__SetHelper('PinPMainArea', PinPMainAreaCmdString, value, qualifier)

    def UpdatePinPMainArea(self, value, qualifier):

        PinPMainAreaStateNames = {
            b'\x00': 'Primary',
            b'\x01': 'Secondary'
        }

        PinPMainAreaCmdString = b'\xBE\xEF\x03\x06\x00\x01\x22\x02\x00\x05\x23\x00\x00'
        res = self.__UpdateHelper('PinPMainArea', PinPMainAreaCmdString, value, qualifier)
        if res:
            try:
                value = PinPMainAreaStateNames[res[1:2]]
                self.WriteStatus('PinPMainArea', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Main Area: Invalid/unexpected response'])

    def SetPinPPosition(self, value, qualifier):

        PinPPositionStateValues = {
            'Top Left': b'\xBE\xEF\x03\x06\x00\x02\x23\x01\x00\x01\x23\x00\x00',
            'Top Right': b'\xBE\xEF\x03\x06\x00\x92\x22\x01\x00\x01\x23\x01\x00',
            'Bottom Left': b'\xBE\xEF\x03\x06\x00\x62\x22\x01\x00\x01\x23\x02\x00',
            'Bottom Right': b'\xBE\xEF\x03\x06\x00\xF2\x23\x01\x00\x01\x23\x03\x00'
        }
        PinPPositionCmdString = PinPPositionStateValues[value]
        self.__SetHelper('PinPPosition', PinPPositionCmdString, value, qualifier)

    def UpdatePinPPosition(self, value, qualifier):

        PinPPositionStateNames = {
            b'\x00': 'Top Left',
            b'\x01': 'Top Right',
            b'\x02': 'Bottom Left',
            b'\x03': 'Bottom Right'
        }

        PinPPositionCmdString = b'\xBE\xEF\x03\x06\x00\x31\x23\x02\x00\x01\x23\x00\x00'
        res = self.__UpdateHelper('PinPPosition', PinPPositionCmdString, value, qualifier)
        if res:
            try:
                value = PinPPositionStateNames[res[1:2]]
                self.WriteStatus('PinPPosition', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Position: Invalid/unexpected response'])

    def SetPinPPrimarySource(self, value, qualifier):

        PinPPrimarySourceStateValues = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xC3\x23\x01\x00\x04\x23\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x0E\x21\x01\x00\x04\x23\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\x23\x01\x00\x04\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x5E\x27\x01\x00\x04\x23\x0D\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x9E\x20\x01\x00\x04\x23\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\xAE\x22\x01\x00\x04\x23\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x5E\x22\x01\x00\x04\x23\x01\x00'
        }
        PinPPrimarySourceCmdString = PinPPrimarySourceStateValues[value]
        self.__SetHelper('PinPPrimarySource', PinPPrimarySourceCmdString, value, qualifier)

    def UpdatePinPPrimarySource(self, value, qualifier):

        PinPPrimarySourceStateNames = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x05': 'Component',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
        }

        PinPPrimarySourceCmdString = b'\xBE\xEF\x03\x06\x00\xFD\x23\x02\x00\x04\x23\x00\x00'
        res = self.__UpdateHelper('PinPPrimarySource', PinPPrimarySourceCmdString, value, qualifier)
        if res:
            try:
                value = PinPPrimarySourceStateNames[res[1:2]]
                self.WriteStatus('PinPPrimarySource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Primary Source: Invalid/unexpected response'])

    def SetPinPSecondarySource(self, value, qualifier):

        PinPSecondarySourceStateValues = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\x46\x23\x01\x00\x02\x23\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x86\x21\x01\x00\x02\x23\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xB6\x23\x01\x00\x02\x23\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\x27\x01\x00\x02\x23\x0D\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x16\x20\x01\x00\x02\x23\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x26\x22\x01\x00\x02\x23\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\xD6\x22\x01\x00\x02\x23\x01\x00',
        }

        PinPSecondarySourceCmdString = PinPSecondarySourceStateValues[value]
        self.__SetHelper('PinPSecondarySource', PinPSecondarySourceCmdString, value, qualifier)

    def UpdatePinPSecondarySource(self, value, qualifier):

        PinPSecondarySourceStateNames = {
            b'\x00': 'Computer 1',
            b'\x04': 'Computer 2',
            b'\x03': 'HDMI 1',
            b'\x0D': 'HDMI 2',
            b'\x05': 'Component',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
        }

        PinPSecondarySourceCmdString = b'\xBE\xEF\x03\x06\x00\x75\x23\x02\x00\x02\x23\x00\x00'
        res = self.__UpdateHelper('PinPSecondarySource', PinPSecondarySourceCmdString, value, qualifier)
        if res:
            try:
                value = PinPSecondarySourceStateNames[res[1:2]]
                self.WriteStatus('PinPSecondarySource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['PinP Secondary Source: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00',
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02': 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerStateNames[res[1:2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00',
        }
        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteStateNames[res[1:2]]
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

        LAN = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeA = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeB = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMI1 = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        HDMI2 = {
            'Up': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00'
        }

        Component = {
            'Up': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00'
        }

        SVideo = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Video = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        inputType = {
            'Computer 1': Computer1,
            'Computer 2': Computer2,
            'LAN': LAN,
            'USB Type A': USBTypeA,
            'USB Type B': USBTypeB,
            'HDMI 1': HDMI1,
            'HDMI 2': HDMI2,
            'Component': Component,
            'S-Video': SVideo,
            'Video': Video,
        }

        input_val = qualifier['Input']
        if input_val in inputType:
            VolumeCmdString = inputType[input_val][value]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolumeStatus(self, value, qualifier):

        inputType = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00'
        }

        input_val = qualifier['Input']
        if input_val in inputType:
            VolumeStatusCmdString = inputType[input_val]
            res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
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
            b'\x15': 'Invalid Command Reply.',
            b'\x1C': 'Cannot Execute Command.',
            b'\x1F': 'Authentication Error.'
        }
        if len(response) == 8:
            self.SetPassword(response, None)
            response = ''
        elif response[0:1] in DEVICE_ERROR_CODES:
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

    def hit_1_666_Xseries(self):
        self.AspectRatioStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00'
        }
        self.AspectRatioStateNames = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9'
        }

    def hit_1_666_Wseries(self):

        self.AspectRatioStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00'
        }
        self.AspectRatioStateNames = {
            b'\x10': 'Normal',
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native'
        }

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
        index = 0    # Start of possible good data

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
