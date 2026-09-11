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
        self.Models = {
            '8975WUA': self.dukn_1_1846_WUA,
            '8979WUA': self.dukn_1_1846_WUA,
            '8975WU': self.dukn_1_1846_WU,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionChannel': {'Status': {}},
            'ClosedCaptionMode': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VolumeLevelStatus': {'Status': {}},
            'VolumeStep': {'Status': {}},
            'Zoom': {'Status': {}},
        }

        self.Authenticated = 'Not Needed'
        self.devicePassword = ''

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'([a-f0-9]{8})'), self.__MatchPassword, None)

        self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2})')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            startStr = match.group(1).decode()
            endStr = startStr + self.devicePassword
            code_hash = hashlib.md5(endStr.encode())
            CmdString = hexlify(code_hash.digest()) + b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Authenticated = 'Admin'
            self.Send(CmdString)
        else:
            self.MissingCredentialsLog('Password')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': [b'\x5E\xDD', b'\x10\x00'],
            '4:3': [b'\x9E\xD0', b'\x00\x00'],
            '16:9': [b'\x0E\xD1', b'\x01\x00'],
            '16:10': [b'\x3E\xD6', b'\x0A\x00'],
            '14:9': [b'\xCE\xD6', b'\x09\x00'],
            'Native': [b'\x5E\xD7', b'\x08\x00']
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x08\x20' + ValueStateValues[value][1]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            16: 'Normal',
            0: '4:3',
            1: '16:9',
            10: '16:10',
            9: '14:9',
            8: 'Native'
        }

        AspectRatioCmdString = b'\xBE\xEF\x03\x06\x00\xAD\xD0\x02\x00\x08\x20\x00\x00'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/Unexpected Response'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\xD6\xD2', b'\x01\x00'],
            'Off': [b'\x46\xD3', b'\x00\x00']
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x20' + ValueStateValues[value][1]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6E\xF1', b'\x01\x00'],
            'Off': [b'\xFE\xF0', b'\x00\x00']
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\xA0\x20' + ValueStateValues[value][1]
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        AVMuteCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xF0\x02\x00\xA0\x20\x00\x00'
        res = self.__UpdateHelper('AVMute', AVMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('AVMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AV Mute: Invalid/Unexpected Response'])

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6A\x63', b'\x01\x00'],
            'Off': [b'\xFA\x62', b'\x00\x00'],
            'Auto': [b'\x9A\x63', b'\x02\x00']
        }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            2: 'Auto'
        }

        ClosedCaptionCmdString = b'\xBE\xEF\x03\x06\x00\xC9\x62\x02\x00\x00\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/Unexpected Response'])

    def SetClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            '1': [b'\xD2\x62', b'\x01\x00'],
            '2': [b'\x22\x62', b'\x02\x00'],
            '3': [b'\xB2\x63', b'\x03\x00'],
            '4': [b'\x82\x61', b'\x04\x00']
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)

    def UpdateClosedCaptionChannel(self, value, qualifier):

        ValueStateValues = {
            1: '1',
            2: '2',
            3: '3',
            4: '4'
        }

        ClosedCaptionChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionChannel', ClosedCaptionChannelCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionChannel', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Channel: Invalid/Unexpected Response'])

    def SetClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            'Captions': [b'\x06\x63', b'\x00\x00'],
            'Text': [b'\x96\x62', b'\x01\x00']
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x01\x37' + ValueStateValues[value][1]
        self.__SetHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)

    def UpdateClosedCaptionMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Captions',
            1: 'Text'
        }

        ClosedCaptionModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('ClosedCaptionMode', ClosedCaptionModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('ClosedCaptionMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Mode: Invalid/Unexpected Response'])

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Cover Error',
            2: 'Fan Error',
            3: 'Lamp Error',
            4: 'Temp Error',
            5: 'Air Flow Error',
            7: 'Cold Error',
            8: 'Filter Error'
        }

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/Unexpected Response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString1 = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        FilterUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\xD6\xFC\x02\x00\x9F\x10\x00\x00'

        low_bytes = self.__UpdateHelper('FilterUsage', FilterUsageCmdString1, value, qualifier)
        high_bytes = self.__UpdateHelper('FilterUsage', FilterUsageCmdString2, value, qualifier)

        if low_bytes and high_bytes:
            try:
                filter_time = high_bytes[1:2] + low_bytes[1:2]
                value = unpack('>H', filter_time)[0]
                self.WriteStatus('FilterUsage', value, qualifier)
            except (TypeError, IndexError):
                self.Error(['Filter Usage: Invalid/Unexpected Response'])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Increment': [b'\x6A\x93', b'\x04\x00'],
            'Decrement': [b'\xBB\x92', b'\x05\x00']
        }

        FocusCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + ValueStateValues[value][1] + b'\x00\x24\x00\x00'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\x83\xD2', b'\x00\x00'],
            'On': [b'\x13\xD3', b'\x01\x00']
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x02\x30' + ValueStateValues[value][1]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        ValueStateValues = {
            0: 'Off',
            1: 'On'
        }

        FreezeCmdString = b'\xBE\xEF\x03\x06\x00\xB0\xD2\x02\x00\x02\x30\x00\x00'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00' + self.SetInputState[value][0] + b'\x01\x00\x00\x20' + self.SetInputState[value][1]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.GetInputState[res[1]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': [b'\x3B\x23', b'\x00\x00'],
            'Eco': [b'\xAB\x22', b'\x01\x00']
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x33' + ValueStateValues[value][1]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0: 'Normal',
            1: 'Eco'
        }

        LampModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/Unexpected Response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString1 = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        LampUsageCmdString2 = b'\xBE\xEF\x03\x06\x00\x2A\xFD\x02\x00\x9E\x10\x00\x00'

        low_bytes = self.__UpdateHelper('LampUsage', LampUsageCmdString1, value, qualifier)
        high_bytes = self.__UpdateHelper('LampUsage', LampUsageCmdString2, value, qualifier)

        if low_bytes and high_bytes:
            try:
                lamp_time = high_bytes[1:2] + low_bytes[1:2]
                value = unpack('>H', lamp_time)[0]
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, TypeError, IndexError):
                self.Error(['Lamp Usage: Invalid/Unexpected Response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'Off': [b'\x2A\xD3', b'\x00\x00'],
            'On': [b'\xBA\xD2', b'\x01\x00']
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x00\x60' + ValueStateValues[value][1]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            2: 'Cooling Down'
        }

        PowerCmdString = b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': [b'\x6B\xD9', b'\x01\x00'],
            'Off': [b'\xFB\xD8', b'\x00\x00']
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + b'\x01\x00\x20\x30' + ValueStateValues[value][1]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        VideoMuteCmdString = b'\xBE\xEF\x03\x06\x00\xC8\xD8\x02\x00\x20\x30\x00\x00'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[1]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

    def UpdateVolumeLevelStatus(self, value, qualifier):

        VolumeLevelStatusCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xC3\x02\x00\x50\x20\x00\x00'
        res = self.__UpdateHelper('VolumeLevelStatus', VolumeLevelStatusCmdString, value, qualifier)
        if res:
            try:
                value = unpack('>B', res[1:2])[0]
                self.WriteStatus('VolumeLevelStatus', value, qualifier)
            except (ValueError, TypeError, IndexError):
                self.Error(['Volume Level Status: Invalid/Unexpected Response'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': [b'\xAB\xC3', b'\x04\x00'],
            'Down': [b'\x7A\xC2', b'\x05\x00']
        }

        VolumeStepCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + ValueStateValues[value][1] + b'\x50\x20\x00\x00'
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Increment': [b'\x96\x92', b'\x04\x00'],
            'Decrement': [b'\x47\x93', b'\x05\x00']
        }

        ZoomCmdString = b'\xBE\xEF\x03\x06\x00' + ValueStateValues[value][0] + ValueStateValues[value][1] + b'\x01\x24\x00\x00'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Projector Error",
            b'\x1F': "Authentication Error",
        }

        if response[0:1] in DEVICE_ERROR_CODES:
            self.Error(['{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[0:1]])])
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
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
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

    def dukn_1_1846_WU(self):

        self.SetInputState = {
            'Computer 1': [b'\xFE\xD2', b'\x00\x00'],
            'Computer 2': [b'\x3E\xD0', b'\x04\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'USB A': [b'\x5E\xD1', b'\x06\x00'],
            'USB B': [b'\xFE\xD7', b'\x0C\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'HDBaseT': [b'\xAE\xDE', b'\x11\x00'],
            'Component': [b'\xAE\xD1', b'\x05\x00'],
            'S-Video': [b'\x9E\xD3', b'\x02\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.GetInputState = {
            0: 'Computer 1',
            4: 'Computer 2',
            11: 'LAN',
            6: 'USB A',
            12: 'USB B',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            5: 'Component',
            2: 'S-Video',
            1: 'Video'
        }

    def dukn_1_1846_WUA(self):

        self.SetInputState = {
            'Computer 1': [b'\xFE\xD2', b'\x00\x00'],
            'LAN': [b'\xCE\xD5', b'\x0B\x00'],
            'USB A': [b'\x5E\xD1', b'\x06\x00'],
            'USB B': [b'\xFE\xD7', b'\x0C\x00'],
            'HDMI 1': [b'\x0E\xD2', b'\x03\x00'],
            'HDMI 2': [b'\x6E\xD6', b'\x0D\x00'],
            'HDBaseT': [b'\xAE\xDE', b'\x11\x00'],
            'Component': [b'\xAE\xD1', b'\x05\x00'],
            'S-Video': [b'\x9E\xD3', b'\x02\x00'],
            'Video': [b'\x6E\xD3', b'\x01\x00']
        }

        self.GetInputState = {
            0: 'Computer 1',
            11: 'LAN',
            6: 'USB A',
            12: 'USB B',
            3: 'HDMI 1',
            13: 'HDMI 2',
            17: 'HDBaseT',
            5: 'Component',
            2: 'S-Video',
            1: 'Video'
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
