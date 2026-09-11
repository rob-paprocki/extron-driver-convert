from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import hashlib
from binascii import hexlify
from struct import unpack

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
        self.devicePassword = None


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ClosedCaptionChannel': { 'Status': {}},
            'ClosedCaptionDisplay': { 'Status': {}},
            'ClosedCaptionMode': { 'Status': {}},
            'DeviceStatus': { 'Status': {}},
            'FilterUsage': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Input': { 'Status': {}},
            'LampMode': { 'Status': {}},
            'LampUsage': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': {'Parameters':['Input'], 'Status': {}},
            'VolumeLevelStatus': {'Parameters':['Input'], 'Status': {}},
            }
        self.Authenticated = 'Not Needed' 

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)

        self.Delrex = re.compile(b'(\x15|\x06|\x1C[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|[a-fA-F0-9]{8})')

    def SetPassword(self, value, qualifier):
        """
        Sends password to the device
        """
        outStr = value.decode() + self.devicePassword
        m = hashlib.md5(outStr.encode())
        cmdString = hexlify(m.digest())+b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        self.Authenticated = 'Admin'   
        self.Send(cmdString)

    def __MatchPassword(self, match, tag):

        self.SetPassword( match.group(1), None)
    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3'       : b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00', 
            '16:9'      : b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00', 
            '14:9'      : b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00', 
            '16:10'     : b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00', 
            'Native'    : b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00', 
            'Normal'    : b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
            }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioState = {
            0x00 : '4:3', 
            0x01 : '16:9', 
            0x09 : '14:9', 
            0x0A : '16:10', 
            0x08 : 'Native', 
            0x10 : 'Normal'
            }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = AspectRatioState[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On'    : b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00', 
            'Off'   : b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
            }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            0x01 : 'On', 
            0x00 : 'Off'
            }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelState = {
            'CC1' : b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00', 
            'CC2' : b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00', 
            'CC3' : b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00', 
            'CC4' : b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
            }

        ClosedCaptionChannelCmdString = ClosedCaptionChannelState[value]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ClosedCaptionChannelState = {
            0x01 : 'CC1', 
            0x02 : 'CC2', 
            0x03 : 'CC3', 
            0x04 : 'CC4'
            }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionChannelState[res[1]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/unexpected response'])

    def SetClosedCaptionDisplay(self, value, qualifier):

        ClosedCaptionDisplayState = {
            'On'    : b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00', 
            'Off'   : b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00', 
            'Auto'  : b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
            }

        ClosedCaptionDisplayCmdString = ClosedCaptionDisplayState[value]
        self.__SetHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)

    def UpdateClosedCaptionDisplay(self, value, qualifier):

        ClosedCaptionDisplayState = {
            0x01 : 'On', 
            0x00 : 'Off', 
            0x02 : 'Auto'
            }

        ClosedCaptionDisplayCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionDisplay', ClosedCaptionDisplayCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionDisplayState[res[1]]
                self.WriteStatus('ClosedCaptionDisplay', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Display: Invalid/unexpected response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeState = {
            'Captions'  : b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00', 
            'Text'      : b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
            }

        ClosedCaptionModeCmdString = ClosedCaptionModeState[value]
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ClosedCaptionModeState = {
            0x00 : 'Captions', 
            0x01 : 'Text'
            }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionModeState[res[1]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusState = {
            0x00 : 'Normal', 
            0x01 : 'Cover Error', 
            0x02 : 'Fan Error', 
            0x03 : 'Lamp Error', 
            0x04 : 'Temp Error', 
            0x05 : 'Air Flow Error', 
            0x07 : 'Cold Error', 
            0x08 : 'Filter Error'
            }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusState[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<H', res[1:3])[0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeState = {
            'On'    : b'\xBE\xEF\x03\x06\x00\x13\xD3\x01\x00\x02\x30\x01\x00', 
            'Off'   : b'\xBE\xEF\x03\x06\x00\x83\xD2\x01\x00\x02\x30\x00\x00'
            }

        FreezeCmdString = FreezeState[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeState = {
            0x01 : 'On', 
            0x00 : 'Off'
            }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = FreezeState[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        InputState = {
            'Computer 1'    : b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00', 
            'Computer 2'    : b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00', 
            'HDMI'          : b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00', 
            'Component'     : b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00', 
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00', 
            'LAN'           : b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00', 
            'USB Type A'    : b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00', 
            'USB Type B'    : b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
            }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputState = {
            0x00 : 'Computer 1', 
            0x04 : 'Computer 2', 
            0x03 : 'HDMI', 
            0x05 : 'Component', 
            0x02 : 'S-Video', 
            0x01 : 'Video', 
            0x0B : 'LAN', 
            0x06 : 'USB Type A', 
            0x0C : 'USB Type B'
            }

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = InputState[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeState = {
            'Normal'            : b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00', 
            'Eco'               : b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00', 
            'Intelligent Eco'   : b'\xBE\xEF\x03\x06\x00\xFB\x2E\x01\x00\x00\x33\x10\x00', 
            'Saver'             : b'\xBE\xEF\x03\x06\x00\xFB\x3A\x01\x00\x00\x33\x20\x00'
            }

        LampModeCmdString = LampModeState[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeState = {
            0x00 : 'Normal', 
            0x01 : 'Eco', 
            0x10 : 'Intelligent Eco', 
            0x20 : 'Saver'
            }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = LampModeState[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = unpack('<H', res[1:3])[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        PowerState = {
            'On'    : b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00', 
            'Off'   : b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00', 
            }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x01 : 'On', 
            0x00 : 'Off', 
            0x02 : 'Cooling Down'
            }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerState[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On'    : b'\xBE\xEF\x03\x06\x00\x6B\xD9\x01\x00\x20\x30\x01\x00', 
            'Off'   : b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
            }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteState = {
            0x01 : 'On', 
            0x00 : 'Off'
            }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = VideoMuteState[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        InputStateIncrement = {
            'Computer 1'    : b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00', 
            'Computer 2'    : b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00', 
            'Component'     : b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00', 
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00', 
            'HDMI'          : b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00', 
            'LAN'           : b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00', 
            'USB Type A'    : b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00', 
            'USB Type B'    : b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00'
            }

        InputStateDecrement = {
            'Computer 1'    : b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00', 
            'Computer 2'    : b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00', 
            'Component'     : b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00', 
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00', 
            'HDMI'          : b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00', 
            'LAN'           : b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00', 
            'USB Type A'    : b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00', 
            'USB Type B'    : b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
            }

        if value == 'Up':
            VolumeCmdString = InputStateIncrement[qualifier['Input']]
        elif value == 'Down':
            VolumeCmdString = InputStateDecrement[qualifier['Input']]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
    def UpdateVolumeLevelStatus(self, value, qualifier):

        InputStates = {
            'Computer 1'    : b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00', 
            'Computer 2'    : b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00', 
            'Component'     : b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00', 
            'S-Video'       : b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00', 
            'Video'         : b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00', 
            'HDMI'          : b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00', 
            'LAN'           : b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00', 
            'USB Type A'    : b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00', 
            'USB Type B'    : b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00'
            }

        VolumeLevelStatusCmdString = InputStates[qualifier['Input']]
        res = self.__UpdateHelper('VolumeLevelStatus', VolumeLevelStatusCmdString, value, qualifier)
        if res:
            try:
                value = res[1]
                self.WriteStatus('VolumeLevelStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume Level Status: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15'    : 'Invalid Command Reply.',
            b'\x1C'    : 'Cannot Execute Command.',
            }

        if len(response) == 8:
            self.SetPassword( response, None)
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



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Delrex)
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Delrex)
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
    # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

