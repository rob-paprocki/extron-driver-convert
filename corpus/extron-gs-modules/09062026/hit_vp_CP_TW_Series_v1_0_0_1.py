from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
import hashlib
from binascii import hexlify
from struct import unpack


class DeviceClass():

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 1
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AVMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaptionDisplay': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Parameters': ['Input'], 'Status': {}},
            'VolumeLevelStatus': {'Parameters': ['Input'], 'Status': {}}
        }
        self.Authenticated = 'Not Needed'
        if self.Unidirectional == 'False':
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'([a-fA-F0-9]{8}|\x1F\x04\x00)'), self.__MatchPassword, None)

            self.Delrex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def SetPassword(self, value, qualifier):
        outStr = str(value) + self.Password
        m = hashlib.md5(outStr.encode())
        cmdString = hexlify(m.digest()) + b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        self.Authenticated = 'Admin'
        self.Send(cmdString)

    def __MatchPassword(self, match, tag):
        value = match.group(1).decode()
        if value == '\x1F\x04\x00':
            self.Authenticated = 'None'
            print('Authentication Error')
        else:
            self.SetPassword(value, None)

    def SetAspectRatio(self, value, qualifier):
        AspectRatioState = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):
        AspectRatioState = {
            0x00: '4:3',
            0x01: '16:9',
            0x08: 'Native',
            0x09: '14:9',
            0x0A: '16:10',
            0x10: 'Normal'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            value = AspectRatioState[res[1]]
            self.WriteStatus('AspectRatio', value, qualifier)
        else:
            print('Invalid/Unexpected Response for AspectRatio')

    def SetAutoImage(self, value, qualifier):
        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier, 3)

    def SetAVMute(self, value, qualifier):
        AVMuteState = {
            'On': b'\xBE\xEF\x03\x06\x00\x6E\xF1\x01\x00\xA0\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xF0\x01\x00\xA0\x20\x00\x00'
        }

        AVMuteCmdString = AVMuteState[value]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier, 3)

    def UpdateAVMute(self, value, qualifier):
        AVMuteState = {
            0x01: 'On',
            0x00: 'Off'
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xF0\x02\x00\xA0\x20\x00\x00'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            value = AVMuteState[res[1]]
            self.WriteStatus('AVMute', value, qualifier)
        else:
            print('Invalid/Unexpected Response for AVMute')

    def SetClosedCaptionDisplay(self, value, qualifier):
        ClosedCaptionDisplayState = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }

        ClosedCaptionDisplayCmdString = ClosedCaptionDisplayState[value]
        self.__SetHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionDisplay(self, value, qualifier):
        ClosedCaptionDisplayState = {
            0x01: 'On',
            0x00: 'Off',
            0x02: 'Auto'
        }

        ClosedCaptionDisplayCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)
        if res:
            value = ClosedCaptionDisplayState[res[1]]
            self.WriteStatus('ClosedCaptionDisplay', value, qualifier)
        else:
            print('Invalid/Unexpected Response for ClosedCaptionDisplay')

    def SetClosedCaptionMode(self, value, qualifier):
        ClosedCaptionModeState = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }

        ClosedCaptionModeCmdString = ClosedCaptionModeState[value]
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):
        ClosedCaptionModeState = {
            0x00: 'Captions',
            0x01: 'Text'
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            value = ClosedCaptionModeState[res[1]]
            self.WriteStatus('ClosedCaptionMode', value, qualifier)
        else:
            print('Invalid/Unexpected Response for ClosedCaptionMode')

    def SetClosedCaptionChannel(self, value, qualifier):
        ClosedCaptionChannelState = {
            'CC1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            'CC2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            'CC3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            'CC4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
        }

        ClosedCaptionChannelCmdString = ClosedCaptionChannelState[value]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):
        ClosedCaptionChannelState = {
            0x01: 'CC1',
            0x02: 'CC2',
            0x03: 'CC3',
            0x04: 'CC4'
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            value = ClosedCaptionChannelState[res[1]]
            self.WriteStatus('ClosedCaptionChannel', value, qualifier)
        else:
            print('Invalid/Unexpected Response for ClosedCaptionChannel')

    def UpdateDeviceStatus(self, value, qualifier):
        DeviceStatusState = {
            0x00: 'Normal',
            0x01: 'Cover Error',
            0x02: 'Fan Error',
            0x03: 'Lamp Error',
            0x04: 'Temp Error',
            0x05: 'Air Flow Error',
            0x07: 'Cold Error',
            0x08: 'Filter Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            value = DeviceStatusState[res[1]]
            self.WriteStatus('DeviceStatus', value, qualifier)
        else:
            print('Invalid/Unexpected Response for DeviceStatus')

    def UpdateFilterUsage(self, value, qualifier):
        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            value = unpack('<H', res[1:3])[0]
            self.WriteStatus('FilterUsage', value, qualifier)
        else:
            print('Invalid/Unexpected Response for FilterUsage')

    def SetFreeze(self, value, qualifier):
        FreezeState = {
            'On': b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
        }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        FreezeState = {
            0x01: 'On',
            0x00: 'Off'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            value = FreezeState[res[1]]
            self.WriteStatus('Freeze', value, qualifier)
        else:
            print('Invalid/Unexpected Response for Freeze')

    def SetInput(self, value, qualifier):
        InputState = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x6E\xD6\x01\x00\x00\x20\x0D\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier, 3)

    def UpdateInput(self, value, qualifier):
        InputState = {
            0x00: 'Computer 1',
            0x04: 'Computer 2',
            0x03: 'HDMI 1',
            0x0D: 'HDMI 2',
            0x01: 'Video',
            0x06: 'USB Type A',
            0x0B: 'LAN',
            0x0C: 'USB Type B'
        }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            value = InputState[res[1]]
            self.WriteStatus('Input', value, qualifier)
        else:
            print('Invalid/Unexpected Response for Input')

    def SetLampMode(self, value, qualifier):
        LampModeState = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00',
            'Eco': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00',
            'Intelligent Eco': b'\xBE\xEF\x03\x06\x00\xFB\x2E\x01\x00\x00\x33\x10\x00',
            'Saver': b'\xBE\xEF\x03\x06\x00\xFB\x3A\x01\x00\x00\x33\x20\x00'
        }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):
        LampModeState = {
            0x00: 'Normal',
            0x01: 'Eco',
            0x10: 'Intelligent Eco',
            0x20: 'Saver'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            value = LampModeState[res[1]]
            self.WriteStatus('LampMode', value, qualifier)
        else:
            print('Invalid/Unexpected Response for LampMode')

    def UpdateLampUsage(self, value, qualifier):
        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            value = unpack('<H', res[1:3])[0]
            self.WriteStatus('LampUsage', value, qualifier)
        else:
            print('Invalid/Unexpected Response for LampUsage')

    def SetMute(self, value, qualifier):
        MuteState = {
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
        }

        MuteCmdString = MuteState[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):
        MuteState = {
            0x01: 'On',
            0x00: 'Off'
        }

        MuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        if res:
            value = MuteState[res[1]]
            self.WriteStatus('Mute', value, qualifier)
        else:
            print('Invalid/Unexpected Response for Mute')

    def SetPower(self, value, qualifier):
        PowerState = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00',
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier, 10)

    def UpdatePower(self, value, qualifier):
        PowerState = {
            0x01: 'On',
            0x00: 'Off',
            0x02: 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            if len(res) == 3:
                value = PowerState[res[1]]
                self.WriteStatus('Power', value, qualifier)
        else:
            print('Invalid/Unexpected Response for Power')

    def SetVideoMute(self, value, qualifier):
        VideoMuteState = {
            'On': b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier, 3)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteState = {
            0x01: 'On',
            0x00: 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            value = VideoMuteState[res[1]]
            self.WriteStatus('VideoMute', value, qualifier)
        else:
            print('Invalid/Unexpected Response for VideoMute')

    def SetVolume(self, value, qualifier):
        InputStateIncrement = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x07\xCE\x04\x00\x6D\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00'
        }

        InputStateDecrement = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\xD6\xCF\x05\x00\x6D\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        if value == 'Increment':
            VolumeCmdString = InputStateIncrement[qualifier['Input']]
        elif value == 'Decrement':
            VolumeCmdString = InputStateDecrement[qualifier['Input']]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier, 3)

    def UpdateVolumeLevelStatus(self, value, qualifier):
        InputState = {
            'Computer 1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer 2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'HDMI 1': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'HDMI 2': b'\xBE\xEF\x03\x06\x00\x61\xCE\x02\x00\x6D\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00'
        }

        VolumeLevelStatusCmdString = InputState[qualifier['Input']]
        res = self.__UpdateHelper('VolumeLevelStatus', VolumeLevelStatusCmdString, value, qualifier)
        if res:
            value = res[1]
            self.WriteStatus('VolumeLevelStatus', value, qualifier)
        else:
            print('Invalid/Unexpected Response for VolumeLevelStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {
            b'\x15': 'Invalid Command Reply.',
            b'\x1C': 'Cannot Execute Command.',
        }
        if response:
            if response[0:1] == b'\x1F':
                if response[1:3] == b'\x04\x00':
                    self.Authenticated = 'None'
                    print('Authentication Error.')
                    response = ''
                else:
                    print('Projector Busy Reply.')
                    response = ''
            elif response[0:1] in DEVICE_ERROR_CODES:
                print('{0} {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]]))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Delrex)
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
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
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Delrex)
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        try:
            getattr(self, 'Update%s' % command)(None, qualifier)
        except AttributeError:
            print(command, 'does not support Set.')

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
