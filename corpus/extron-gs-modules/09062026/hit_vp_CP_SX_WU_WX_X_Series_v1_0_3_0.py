from extronlib.interface import EthernetClientInterface, SerialInterface
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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False

        self.Models = {
            'CP-X8150': self.hit_1_329_CP_X,
            'CP-X8160': self.hit_1_329_CP_X,
            'CP-WX8240': self.hit_1_329_CP,
            'CP-WX8255': self.hit_1_329_CP,
            'CP-WU8440': self.hit_1_329_CP,
            'CP-WU8450': self.hit_1_329_CP,
            'CP-SX8350': self.hit_1_329_CP,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoKeystoneV': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'LampMode': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'KeystoneH': {'Status': {}},
            'KeystoneHReset': {'Status': {}},
            'KeystoneV': {'Status': {}},
            'KeystoneVReset': {'Status': {}},
            'LensMemoryIndex': {'Status': {}},
            'LensMemory': {'Status': {}},
            'LensShift': {'Parameters':['Shift'], 'Status': {}},
            'LensShiftCenter': {'Status': {}},
            'LampUsage': {'Status': {}},
            'PbyP': {'Status': {}},
            'PbyPMainArea': {'Status': {}},
            'PbyPRightSource': {'Status': {}},
            'PbyPLeftSource': {'Status': {}},
            'PbyPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['InputSelect'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['InputSelect'], 'Status': {}},
            'Zoom': {'Status': {}}
        }

        self.Authenticated = 'Not Needed'
        self.devicePassword = None

        if self.Unidirectional == 'False':
            if 'Ethernet' == self.ConnectionType:
                self.AddMatchString(re.compile(b'([a-f0-9]{8}|\x1F\x04\x00)'), self.__MatchPassword, None)

        self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def __MatchPassword(self, match, tag):
        value = match.group(1).decode()
        if value == '\x1F\x04\x00':
            self.Authenticated = 'None'
            print('Authentication Error')
        else:
            self.SetPassword(value, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            inStr = value.group(1).decode()
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
                print('Invalid/unexpected response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):
        AudioMuteStateValues = {
            'On' : b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off' : b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00',
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
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAutoKeystoneV(self, value, qualifier):

        AutoKeystoneVCmdString = b'\xBE\xEF\x03\x06\x00\xE5\xD1\x06\x00\x0D\x20\x00\x00'
        self.__SetHelper('AutoKeystoneV', AutoKeystoneVCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

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
            b'\x00': '1',
            b'\x01': '2',
            b'\x02': '3',
            b'\x03': '4',
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionChannelStateNames[res[1:2]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateClosedCaptionChannel')

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
                print('Invalid/unexpected response for UpdateClosedCaptionMode')

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
                print('Invalid/unexpected response for UpdateClosedCaption')

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
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetKeystoneH(self, value, qualifier):
        KeystoneHStateValues = {
            'Increment' : b'\xBE\xEF\x03\x06\x00\x8F\xD0\x04\x00\x0B\x20\x00\x00', 
            'Decrement' : b'\xBE\xEF\x03\x06\x00\x5E\xD1\x05\x00\x0B\x20\x00\x00'
        }
        KeystoneHCmdString = KeystoneHStateValues[value]
        self.__SetHelper('KeystoneH', KeystoneHCmdString, value, qualifier)

    def SetKeystoneHReset(self, value, qualifier):

        KeystoneHResetCmdString = b'\xBE\xEF\x03\x06\x00\x98\xD8\x06\x00\x20\x70\x00\x00'
        self.__SetHelper('KeystoneHReset', KeystoneHResetCmdString, value, qualifier)

    def SetKeystoneV(self, value, qualifier):
        KeystoneHStateValues = {
            'Increment' : b'\xBE\xEF\x03\x06\x00\xDF\xD3\x04\x00\x07\x20\x00\x00', 
            'Decrement' : b'\xBE\xEF\x03\x06\x00\x0E\xD2\x05\x00\x07\x20\x00\x00'
        }
        KeystoneVCmdString = KeystoneHStateValues[value]
        self.__SetHelper('KeystoneV', KeystoneVCmdString, value, qualifier)

    def SetKeystoneVReset(self, value, qualifier):

        KeystoneVResetCmdString = b'\xBE\xEF\x03\x06\x00\x08\xD0\x06\x00\x0C\x70\x00\x00'
        self.__SetHelper('KeystoneVReset', KeystoneVResetCmdString, value, qualifier)

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
                print('Invalid/unexpected response for UpdateLampMode')

    def UpdateFilterUsage(self, value, qualifier):
        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3]) * 256 + ord(res[1:2])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')
                
    def SetFocus(self, value, qualifier):
        ValueStateValues = {
            'Increase' : b'\xBE\xEF\x03\x06\x00\x6A\x93\x04\x00\x00\x24\x00\x00', 
            'Decrease' : b'\xBE\xEF\x03\x06\x00\xBB\x92\x05\x00\x00\x24\x00\x00'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

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
                print('Invalid/unexpected response for UpdateFreeze')

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
                print('Invalid/unexpected response for UpdateInput')

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
                print('Invalid/unexpected response for UpdateLensMemoryIndex')

    def SetLensMemory(self, value, qualifier):
        LensMemoryStateValues = {
            'Load': b'\xBE\xEF\x03\x06\x00\xE8\x90\x06\x00\x08\x24\x00\x00',
            'Save': b'\xBE\xEF\x03\x06\x00\x14\x91\x06\x00\x09\x24\x00\x00',
            'Clear': b'\xBE\xEF\x03\x06\x00\x50\x91\x06\x00\x0A\x24\x00\x00',
        }
        LensMemoryCmdString = LensMemoryStateValues[value]
        self.__SetHelper('LensMemory', LensMemoryCmdString, value, qualifier)

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3]) * 256 + ord(res[1:2])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')
                
    def SetLensShift(self, value, qualifier):
        ValueStateValues = {
            'Up' : {
                'Horizontal' : b'\xBE\xEF\x03\x06\x00\x2E\x93\x04\x00\x03\x24\x00\x00', 
                'Vertical' : b'\xBE\xEF\x03\x06\x00\xD2\x92\x04\x00\x02\x24\x00\x00'
            }, 
            'Down' : {
                'Horizontal' : b'\xBE\xEF\x03\x06\x00\xFF\x92\x05\x00\x03\x24\x00\x00', 
                'Vertical' : b'\xBE\xEF\x03\x06\x00\x03\x93\x05\x00\x02\x24\x00\x00'
            }
        }

        LensShiftCmdString = ValueStateValues[value][qualifier['Shift']]
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetLensShiftCenter(self, value, qualifier):
        LensShiftCenterCmdString = b'\xBE\xEF\x03\x06\x00\xB8\x93\x06\x00\x04\x24\x00\x00'
        self.__SetHelper('LensShiftCenter', LensShiftCenterCmdString, value, qualifier)

    def SetPbyP(self, value, qualifier):
        PbyPStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xAE\x27\x01\x00\x10\x23\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x3E\x26\x01\x00\x10\x23\x00\x00',
        }
        PbyPCmdString = PbyPStateValues[value]
        self.__SetHelper('PbyP', PbyPCmdString, value, qualifier)

    def UpdatePbyP(self, value, qualifier):
        PbyPStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        PbyPCmdString = b'\xBE\xEF\x03\x06\x00\x0D\x26\x02\x00\x10\x23\x00\x00'
        res = self.__UpdateHelper('PbyP', PbyPCmdString, value, qualifier)
        if res:
            try:
                value = PbyPStateNames[res[1:2]]
                self.WriteStatus('PbyP', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePbyP')

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
                print('Invalid/unexpected response for UpdatePbyPMainArea')

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
                print('Invalid/unexpected response for UpdatePbyPRightSource')

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
                print('Invalid/unexpected response for UpdatePbyPLeftSource')

    def SetPbyPSwap(self, value, qualifier):
        PbyPSwapCmdString = b'\xBE\xEF\x03\x06\x00\x01\x27\x06\x00\x16\x23\x00\x00'
        self.__SetHelper('PbyPSwap', PbyPSwapCmdString, value, qualifier)

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
                print('Invalid/unexpected response for UpdatePower')

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
                print('Invalid/unexpected response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):
        InputIncrementStates = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
        }

        InputDecrementStates = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
        }

        if value in ['Up', 'Down']:
            if value == 'Up':
                VolumeCmdString = InputIncrementStates[qualifier['InputSelect']]
            if value == 'Down':
                VolumeCmdString = InputDecrementStates[qualifier['InputSelect']]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolumeStatus(self, value, qualifier):
        InputStates = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
        }

        VolumeStatusCmdString = InputStates[qualifier['InputSelect']]
        res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
        if res:
            try:
                value = int(res[1])
                self.WriteStatus('VolumeStatus', value, qualifier)
            except (KeyError, IndexError, ValueError):
                print('Invalid/unexpected response for UpdateVolumeStatus')
                
    def SetZoom(self, value, qualifier):
        ValueStateValues = {
            'In' : b'\xBE\xEF\x03\x06\x00\x96\x92\x04\x00\x01\x24\x00\x00', 
            'Out' : b'\xBE\xEF\x03\x06\x00\x47\x93\x05\x00\x01\x24\x00\x00'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Busy",
            b'\x1F': "Authentication Error",
        }
        if response[0:1] in DEVICE_ERROR_CODES:
            print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]]))
            if response[0:1] == b'\x1F':
                self.Authenticated = 'None'
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.regex)
            if not res:
                print('Unexpected/Invalid response for Set{}'.format(command))
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter += 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
                return ''
            else:
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
        
    def hit_1_329_CP_X(self):

        self.AspectRatioStateValues = {
            '4:3' :    b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9' :   b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '14:9' :   b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            '16:10' :  b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }
        self.AspectRatioStateNames = {
            b'\x00' : '4:3',
            b'\x01' : '16:9',
            b'\x09' : '14:9',
            b'\x0A' : '16:10',
            b'\x10' : 'Normal'
        }

    def hit_1_329_CP(self):

        self.AspectRatioStateValues = {
            '4:3' :    b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9' :   b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '14:9' :   b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            '16:10' :  b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            'Normal' : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
            'Native' : b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00'
        }
        self.AspectRatioStateNames = {
            b'\x00' : '4:3',
            b'\x01' : '16:9',
            b'\x09' : '14:9',
            b'\x0A' : '16:10',
            b'\x10' : 'Normal',
            b'\x08' : 'Native'
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

    def __ReceiveData(self, interface, data):
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

    # Check incoming unsolicited data to see if it matched with device expectancy. 
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

    # This method is to tie a specific command with specific parameter to a call back method
    # when it value is updated. It all setup how often the command to be query, if the command
    # have the update method.
    # interval 0 is for query once, any other integer is used as the query interval.
    # If command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')
        
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
        if self.connectionFlag == False:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

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
