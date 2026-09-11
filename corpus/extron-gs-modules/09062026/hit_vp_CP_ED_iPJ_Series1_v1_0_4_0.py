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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'CP-X4021N': self.hit_1_167_As2,
            'CP-X5021N': self.hit_1_167_As2,
            'CP-WX4021N': self.hit_1_167_As1,
            'CP-A221N': self.hit_1_167_As1,
            'CP-A301N': self.hit_1_167_As1,
            'CP-A302WNM': self.hit_1_167_As1,
            'CP-AW250N': self.hit_1_167_As1,
            'CP-AW251N': self.hit_1_167_As1,
            'CP-WX3011N': self.hit_1_167_As1,
            'CP-WX3014WN': self.hit_1_167_As3,
            'CP-X3014WN': self.hit_1_167_As3,
            'CP-X4014WN': self.hit_1_167_As3,
            'CP-X2514WN': self.hit_1_167_As3,
            'iPJ-AW250N': self.hit_1_167_As1,
            'iPJ-AW250NM': self.hit_1_167_As1,
            'CP-A100': self.hit_1_167_As4,
            'ED-A100': self.hit_1_167_As4,
            'ED-A110': self.hit_1_167_As4,
            'CP-A100W': self.hit_1_167_As4,
            'CP-AW312WN': self.hit_1_167_As1,
            'CP-AW252WN': self.hit_1_167_As1,
            'CP-X2021WN': self.hit_1_167_As5,
            'CP-X2521WN': self.hit_1_167_As5,
            'CP-X3021WN': self.hit_1_167_As5,
            'CP-AW2519N': self.hit_1_167_I3_As1,
            'CP-AW2519NM': self.hit_1_167_I3_As1,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioSource': {'Parameters': ['Input Type'], 'Status': {}},
            'AutoImage': {'Status': {}},
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
            'Volume': {'Parameters': ['Input Type'], 'Status': {}},
            'VolumeStatus': {'Parameters': ['Input Type'], 'Status': {}}
        }

        self.Authenticated = 'Not Needed'
        self.devicePassword = None

        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'([a-fA-F0-9]{8})'), self.__MatchPassword, None)

        self.regex = re.compile(b'(\x06|\x15|\x1C[\x00-\xFF]{2}|\x1D[\x00-\xFF]{2}|\x1F[\x00-\xFF]{2})')

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            inStr = value.group(1).decode()
            outStr = inStr + self.devicePassword
            m = hashlib.md5(outStr.encode())
            cmdString = hexlify(m.digest())+b'\xBE\xEF\x03\x06\x00\x19\xD3\x02\x00\x00\x60\x00\x00'
            self.Authenticated = 'Admin'
            self.Send(cmdString)
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.SetPassword(match, None)

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
            'On': b'\xBE\xEF\x03\x06\x00\xD6\xD2\x01\x00\x02\x20\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xD3\x01\x00\x02\x20\x00\x00'
        }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On'
        }

        AudioMuteCmdString = b'\xBE\xEF\x03\x06\x00\x75\xD3\x02\x00\x02\x20\x00\x00'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = AudioMuteStateNames[res[1:2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateAudioMute')

    def SetAudioSource(self, value, qualifier):

        InputType = qualifier['Input Type']

        if InputType in self.inputtypesource:
            try:
                AudioSourceCmdString = (self.inputtypesource[InputType])[value]
                self.__SetHelper('AudioSource', AudioSourceCmdString, value, qualifier)
            except (KeyError, IndexError):
                print('Invalid Command for SetAudioSource')
        else:
            print('Invalid Command for SetAudioSource')

    def UpdateAudioSource(self, value, qualifier):

        InputType = qualifier['Input Type']
        if InputType in self.AudioSourceStateQualifier:
            AudioSourceCmdString = self.AudioSourceStateQualifier[InputType]
            res = self.__UpdateHelper('AudioSource', AudioSourceCmdString, value, qualifier)
            if res:
                try:
                    value = self.AudioSourceStateNames[res[1:2]]
                    self.WriteStatus('AudioSource', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateAudioSource')
        else:
            print('Invalid Command for UpdateAudioSource')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x06\x00\x91\xD0\x06\x00\x0A\x20\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetCCChannel(self, value, qualifier):

        CCChannelStateValues = {
            '1': b'\xBE\xEF\x03\x06\x00\xD2\x62\x01\x00\x02\x37\x01\x00',
            '2': b'\xBE\xEF\x03\x06\x00\x22\x62\x01\x00\x02\x37\x02\x00',
            '3': b'\xBE\xEF\x03\x06\x00\xB2\x63\x01\x00\x02\x37\x03\x00',
            '4': b'\xBE\xEF\x03\x06\x00\x82\x61\x01\x00\x02\x37\x04\x00'
        }
        CCChannelCmdString = CCChannelStateValues[value]
        self.__SetHelper('CCChannel', CCChannelCmdString, value, qualifier)

    def UpdateCCChannel(self, value, qualifier):

        CCChannelStateNames = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4'
        }

        CCChannelCmdString = b'\xBE\xEF\x03\x06\x00\x71\x63\x02\x00\x02\x37\x00\x00'
        res = self.__UpdateHelper('CCChannel', CCChannelCmdString, value, qualifier)
        if res:
            try:
                value = CCChannelStateNames[res[1:2]]
                self.WriteStatus('CCChannel', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateCCChannel')

    def SetCCMode(self, value, qualifier):

        CCModeStateValues = {
            'Captions': b'\xBE\xEF\x03\x06\x00\x06\x63\x01\x00\x01\x37\x00\x00',
            'Text': b'\xBE\xEF\x03\x06\x00\x96\x62\x01\x00\x01\x37\x01\x00'
        }
        CCModeCmdString = CCModeStateValues[value]
        self.__SetHelper('CCMode', CCModeCmdString, value, qualifier)

    def UpdateCCMode(self, value, qualifier):

        CCModeStateNames = {
            b'\x00': 'Captions',
            b'\x01': 'Text'
        }

        CCModeCmdString = b'\xBE\xEF\x03\x06\x00\x35\x63\x02\x00\x01\x37\x00\x00'
        res = self.__UpdateHelper('CCMode', CCModeCmdString, value, qualifier)
        if res:
            try:
                value = CCModeStateNames[res[1:2]]
                self.WriteStatus('CCMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateCCMode')

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\x6A\x63\x01\x00\x00\x37\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFA\x62\x01\x00\x00\x37\x00\x00',
            'Auto': b'\xBE\xEF\x03\x06\x00\x9A\x63\x01\x00\x00\x37\x02\x00'
        }
        ClosedCaptionCmdString = ClosedCaptionStateValues[value]
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionStateNames = {
            b'\x02': 'Auto',
            b'\x01': 'On',
            b'\x00': 'Off'
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

        DeviceStatusCmdString = b'\xBE\xEF\x03\x06\x00\xD9\xD8\x02\x00\x20\x60\x00\x00'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = self.DeviceStatusStateNames[res[1:2]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetEcoMode(self, value, qualifier):

        EcoModeStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x3B\x23\x01\x00\x00\x33\x00\x00',
            'Eco': b'\xBE\xEF\x03\x06\x00\xAB\x22\x01\x00\x00\x33\x01\x00'
        }
        EcoModeCmdString = EcoModeStateValues[value]
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def UpdateEcoMode(self, value, qualifier):

        EcoModeStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Eco'
        }

        EcoModeCmdString = b'\xBE\xEF\x03\x06\x00\x08\x23\x02\x00\x00\x33\x00\x00'
        res = self.__UpdateHelper('EcoMode', EcoModeCmdString, value, qualifier)
        if res:
            try:
                value = EcoModeStateNames[res[1:2]]
                self.WriteStatus('EcoMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateEcoMode')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xF0\x02\x00\xA0\x10\x00\x00'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3]) * 256 + ord(res[1:2])
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateFilterUsage')

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

        InputCmdString = self.InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\xBE\xEF\x03\x06\x00\xCD\xD2\x02\x00\x00\x20\x00\x00'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.InputStateNames[res[1:2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateInput')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\xBE\xEF\x03\x06\x00\xC2\xFF\x02\x00\x90\x10\x00\x00'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = ord(res[2:3]) * 256 + ord(res[1:2])
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                print('Invalid/unexpected response for UpdateLampUsage')

    def SetPictureMode(self, value, qualifier):

        PictureModeStateValues = {
            'Normal': b'\xBE\xEF\x03\x06\x00\x23\xF6\x01\x00\xBA\x30\x00\x00',
            'Cinema': b'\xBE\xEF\x03\x06\x00\xB3\xF7\x01\x00\xBA\x30\x01\x00',
            'Dynamic': b'\xBE\xEF\x03\x06\x00\xE3\xF4\x01\x00\xBA\x30\x04\x00',
            'Board(Black)': b'\xBE\xEF\x03\x06\x00\xE3\xEF\x01\x00\xBA\x30\x20\x00',
            'Board(Green)': b'\xBE\xEF\x03\x06\x00\x73\xEE\x01\x00\xBA\x30\x21\x00',
            'Whiteboard': b'\xBE\xEF\x03\x06\x00\x83\xEE\x01\x00\xBA\x30\x22\x00',
            'Daytime': b'\xBE\xEF\x03\x06\x00\xE3\xC7\x01\x00\xBA\x30\x40\x00'
        }
        PictureModeCmdString = PictureModeStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cinema',
            b'\x04': 'Dynamic',
            b'\x20': 'Board(Black)',
            b'\x21': 'Board(Green)',
            b'\x22': 'Whiteboard',
            b'\x40': 'Daytime'
        }

        PictureModeCmdString = b'\xBE\xEF\x03\x06\x00\x10\xF6\x02\x00\xBA\x30\x00\x00'
        res = self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)
        if res:
            try:
                value = PictureModeStateNames[res[1:2]]
                self.WriteStatus('PictureMode', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdatePictureMode')

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': b'\xBE\xEF\x03\x06\x00\xBA\xD2\x01\x00\x00\x60\x01\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x2A\xD3\x01\x00\x00\x60\x00\x00'
        }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateNames = {
            b'\x00': 'Off',
            b'\x01': 'On',
            b'\x02': 'Cooling'
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
            'Off': b'\xBE\xEF\x03\x06\x00\xFB\xD8\x01\x00\x20\x30\x00\x00'
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

        InputType = qualifier['Input Type']
        if InputType in self.inputtypevolume:
            VolumeCmdString = (self.inputtypevolume[InputType])[value]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolumeStatus(self, value, qualifier):

        InputType = qualifier['Input Type']
        if InputType in self.inputtypevolume:
            VolumeStatusCmdString = self.VolumeStatusStateQualifier[InputType]
            res = self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[1])
                    self.WriteStatus('VolumeStatus', value, qualifier)
                except (ValueError, IndexError):
                    print('Invalid/unexpected response for UpdateVolumeStatus')
        else:
            print('Invalid Command for UpdateVolumeStatus')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x15': "Invalid Command",
            b'\x1C': "Busy",
            b'\x1F': "Authentication Error"
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
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                print('Inappropriate Command ', command)
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
                    return self.__CheckResponseForErrors(command + ':' + str(commandstring), res)
        else:
            print('Inappropriate Command ', command)
            return ''

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'

    def hit_1_167_As4(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x09': '14:9',
            b'\x10': 'Normal'
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x05': 'Component',
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x0E\xDD\x01\x00\x30\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x3E\xDC\x01\x00\x34\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x30\x20\x00\x00'
        }

        Componentsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xA2\xDC\x01\x00\x35\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x52\xDC\x01\x00\x35\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xC2\xDD\x01\x00\x35\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x32\xDD\x01\x00\x35\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xB6\xDC\x01\x00\x32\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xF2\xDC\x01\x00\x31\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'Component': Componentsource,
            'S-Video': SVideosource,
            'Video': Videosource,
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xDD\x02\x00\x35\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x03': 'Audio 3',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
            b'\x06': 'Lamp Time Error',
            b'\x0C': 'Lens Door Error'
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        Componentvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'Component': Componentvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
        }

    def hit_1_167_As1(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native',
            b'\x10': 'Normal'
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x03': 'HDMI',
            b'\x05': 'Component',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x0E\xDD\x01\x00\x30\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x3E\xDC\x01\x00\x34\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x30\x20\x00\x00'
        }

        LANsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x4A\xDE\x01\x00\x3B\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xBA\xDE\x01\x00\x3B\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x2A\xDF\x01\x00\x3B\x20\x03\x00',
            'Audio LAN': b'\xBE\xEF\x03\x06\x00\x8A\xD3\x01\x00\x3B\x20\x11\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xDA\xDF\x01\x00\x3B\x20\x00\x00'
        }

        USBTypeAsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xE6\xDC\x01\x00\x36\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x16\xDC\x01\x00\x36\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x86\xDD\x01\x00\x36\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x76\xDD\x01\x00\x36\x20\x00\x00'
        }

        USBTypeBsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x3E\xDF\x01\x00\x3C\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x3C\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x3C\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x3C\x20\x00\x00'
        }

        HDMIsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x2A\xDC\x01\x00\x33\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xDA\xDC\x01\x00\x33\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x4A\xDD\x01\x00\x33\x20\x03\x00',
            'Audio HDMI': b'\xBE\xEF\x03\x06\x00\x7A\xC4\x01\x00\x33\x20\x20\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xBA\xDD\x01\x00\x33\x20\x00\x00'
        }

        Componentsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xA2\xDC\x01\x00\x35\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x52\xDC\x01\x00\x35\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xC2\xDD\x01\x00\x35\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x32\xDD\x01\x00\x35\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xB6\xDC\x01\x00\x32\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xF2\xDC\x01\x00\x31\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        Standbysource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x7A\xDF\x01\x00\x3F\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x8A\xDF\x01\x00\x3F\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x1A\xDE\x01\x00\x3F\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xEA\xDE\x01\x00\x3F\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'LAN': LANsource,
            'USB Type A': USBTypeAsource,
            'USB Type B': USBTypeBsource,
            'HDMI': HDMIsource,
            'Component': Componentsource,
            'S-Video': SVideosource,
            'Video': Videosource,
            'Standby': Standbysource
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xDF\x02\x00\x3B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xDD\x02\x00\x36\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xDE\x02\x00\x3C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xDD\x02\x00\x33\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xDD\x02\x00\x35\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xDE\x02\x00\x3F\x20\x00\x00'
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x03': 'Audio 3',
            b'\x20': 'Audio HDMI',
            b'\x11': 'Audio LAN',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        LANvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeAvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeBvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMIvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        Componentvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        Standbyvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'LAN': LANvolume,
            'USB Type A': USBTypeAvolume,
            'USB Type B': USBTypeBvolume,
            'HDMI': HDMIvolume,
            'Component': Componentvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
            'Standby': Standbyvolume
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00'
        }

    def hit_1_167_As3(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x08': 'Native',
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x03': 'HDMI',
            b'\x05': 'Component',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x0E\xDD\x01\x00\x30\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x3E\xDC\x01\x00\x34\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x30\x20\x00\x00'
        }

        LANsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x4A\xDE\x01\x00\x3B\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xBA\xDE\x01\x00\x3B\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x2A\xDF\x01\x00\x3B\x20\x03\x00',
            'Audio LAN': b'\xBE\xEF\x03\x06\x00\x8A\xD3\x01\x00\x3B\x20\x11\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xDA\xDF\x01\x00\x3B\x20\x00\x00'
        }

        USBTypeAsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xE6\xDC\x01\x00\x36\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x16\xDC\x01\x00\x36\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x86\xDD\x01\x00\x36\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x76\xDD\x01\x00\x36\x20\x00\x00'
        }

        USBTypeBsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x3E\xDF\x01\x00\x3C\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x3C\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x3C\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x3C\x20\x00\x00'
        }

        HDMIsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x2A\xDC\x01\x00\x33\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xDA\xDC\x01\x00\x33\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x4A\xDD\x01\x00\x33\x20\x03\x00',
            'Audio HDMI': b'\xBE\xEF\x03\x06\x00\x7A\xC4\x01\x00\x33\x20\x20\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xBA\xDD\x01\x00\x33\x20\x00\x00'
        }

        Componentsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xA2\xDC\x01\x00\x35\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x52\xDC\x01\x00\x35\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xC2\xDD\x01\x00\x35\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x32\xDD\x01\x00\x35\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xB6\xDC\x01\x00\x32\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xF2\xDC\x01\x00\x31\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        Standbysource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x7A\xDF\x01\x00\x3F\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x8A\xDF\x01\x00\x3F\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x1A\xDE\x01\x00\x3F\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xEA\xDE\x01\x00\x3F\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'LAN': LANsource,
            'USB Type A': USBTypeAsource,
            'USB Type B': USBTypeBsource,
            'HDMI': HDMIsource,
            'Component': Componentsource,
            'S-Video': SVideosource,
            'Video': Videosource,
            'Standby': Standbysource
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xDF\x02\x00\x3B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xDD\x02\x00\x36\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xDE\x02\x00\x3C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xDD\x02\x00\x33\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xDD\x02\x00\x35\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xDE\x02\x00\x3F\x20\x00\x00'
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x03': 'Audio 3',
            b'\x20': 'Audio HDMI',
            b'\x11': 'Audio LAN',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        LANvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeAvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeBvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMIvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        Componentvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        Standbyvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'LAN': LANvolume,
            'USB Type A': USBTypeAvolume,
            'USB Type B': USBTypeBvolume,
            'HDMI': HDMIvolume,
            'Component': Componentvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
            'Standby': Standbyvolume
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00'
        }

    def hit_1_167_As2(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x10': 'Normal'
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\xAE\xD1\x01\x00\x00\x20\x05\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x03': 'HDMI',
            b'\x05': 'Component',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x0E\xDD\x01\x00\x30\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x3E\xDC\x01\x00\x34\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x30\x20\x00\x00'
        }

        LANsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x4A\xDE\x01\x00\x3B\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xBA\xDE\x01\x00\x3B\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x2A\xDF\x01\x00\x3B\x20\x03\x00',
            'Audio LAN': b'\xBE\xEF\x03\x06\x00\x8A\xD3\x01\x00\x3B\x20\x11\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xDA\xDF\x01\x00\x3B\x20\x00\x00'
        }

        USBTypeAsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xE6\xDC\x01\x00\x36\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x16\xDC\x01\x00\x36\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x86\xDD\x01\x00\x36\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x76\xDD\x01\x00\x36\x20\x00\x00'
        }

        USBTypeBsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x3E\xDF\x01\x00\x3C\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x3C\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x3C\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x3C\x20\x00\x00'
        }

        HDMIsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x2A\xDC\x01\x00\x33\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xDA\xDC\x01\x00\x33\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x4A\xDD\x01\x00\x33\x20\x03\x00',
            'Audio HDMI': b'\xBE\xEF\x03\x06\x00\x7A\xC4\x01\x00\x33\x20\x20\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xBA\xDD\x01\x00\x33\x20\x00\x00'
        }

        Componentsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xA2\xDC\x01\x00\x35\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x52\xDC\x01\x00\x35\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xC2\xDD\x01\x00\x35\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x32\xDD\x01\x00\x35\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xB6\xDC\x01\x00\x32\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xF2\xDC\x01\x00\x31\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        Standbysource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x7A\xDF\x01\x00\x3F\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x8A\xDF\x01\x00\x3F\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x1A\xDE\x01\x00\x3F\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xEA\xDE\x01\x00\x3F\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'LAN': LANsource,
            'USB Type A': USBTypeAsource,
            'USB Type B': USBTypeBsource,
            'HDMI': HDMIsource,
            'Component': Componentsource,
            'S-Video': SVideosource,
            'Video': Videosource,
            'Standby': Standbysource
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xDF\x02\x00\x3B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xDD\x02\x00\x36\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xDE\x02\x00\x3C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xDD\x02\x00\x33\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xDD\x02\x00\x35\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xDE\x02\x00\x3F\x20\x00\x00'
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x03': 'Audio 3',
            b'\x20': 'Audio HDMI',
            b'\x11': 'Audio LAN',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        LANvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeAvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeBvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMIvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        Componentvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x67\xCC\x04\x00\x65\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xB6\xCD\x05\x00\x65\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        Standbyvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'LAN': LANvolume,
            'USB Type A': USBTypeAvolume,
            'USB Type B': USBTypeBvolume,
            'HDMI': HDMIvolume,
            'Component': Componentvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
            'Standby': Standbyvolume
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'Component': b'\xBE\xEF\x03\x06\x00\x01\xCC\x02\x00\x65\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00'
        }

    def hit_1_167_As5(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00',
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x10': 'Normal',
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x03': 'HDMI',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x30\x20\x00\x00'
        }

        LANsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x4A\xDE\x01\x00\x3B\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xBA\xDE\x01\x00\x3B\x20\x02\x00',
            'Audio LAN': b'\xBE\xEF\x03\x06\x00\x8A\xD3\x01\x00\x3B\x20\x11\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xDA\xDF\x01\x00\x3B\x20\x00\x00'
        }

        USBTypeAsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xE6\xDC\x01\x00\x36\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x16\xDC\x01\x00\x36\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x76\xDD\x01\x00\x36\x20\x00\x00'
        }

        USBTypeBsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x3E\xDF\x01\x00\x3C\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x3C\x20\x02\x00',
            'Audio USB': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x3C\x20\x12\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x3C\x20\x00\x00'
        }

        HDMIsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x2A\xDC\x01\x00\x33\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xDA\xDC\x01\x00\x33\x20\x02\x00',
            'Audio HDMI': b'\xBE\xEF\x03\x06\x00\x7A\xC4\x01\x00\x33\x20\x20\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xBA\xDD\x01\x00\x33\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        Standbysource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x7A\xDF\x01\x00\x3F\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x8A\xDF\x01\x00\x3F\x20\x02\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xEA\xDE\x01\x00\x3F\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'LAN': LANsource,
            'USB Type A': USBTypeAsource,
            'USB Type B': USBTypeBsource,
            'HDMI': HDMIsource,
            'S-Video': SVideosource,
            'Video': Videosource,
            'Standby': Standbysource
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xDF\x02\x00\x3B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xDD\x02\x00\x36\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xDE\x02\x00\x3C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xDD\x02\x00\x33\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xDE\x02\x00\x3F\x20\x00\x00'
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x20': 'Audio HDMI',
            b'\x11': 'Audio LAN',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        LANvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeAvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeBvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMIvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        Standbyvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'LAN': LANvolume,
            'USB Type A': USBTypeAvolume,
            'USB Type B': USBTypeBvolume,
            'HDMI': HDMIvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
            'Standby': Standbyvolume
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00'
        }

    def hit_1_167_I3_As1(self):

        self.AspectRatioStateValues = {
            '4:3': b'\xBE\xEF\x03\x06\x00\x9E\xD0\x01\x00\x08\x20\x00\x00',
            '16:9': b'\xBE\xEF\x03\x06\x00\x0E\xD1\x01\x00\x08\x20\x01\x00',
            '16:10': b'\xBE\xEF\x03\x06\x00\x3E\xD6\x01\x00\x08\x20\x0A\x00',
            '14:9': b'\xBE\xEF\x03\x06\x00\xCE\xD6\x01\x00\x08\x20\x09\x00',
            'Native': b'\xBE\xEF\x03\x06\x00\x5E\xD7\x01\x00\x08\x20\x08\x00',
            'Normal': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x08\x20\x10\x00'
        }

        self.AspectRatioStateNames = {
            b'\x00': '4:3',
            b'\x01': '16:9',
            b'\x0A': '16:10',
            b'\x09': '14:9',
            b'\x10': 'Normal',
            b'\x08': 'Native'
        }

        self.InputStateValues = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xFE\xD2\x01\x00\x00\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\x3E\xD0\x01\x00\x00\x20\x04\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x0E\xD2\x01\x00\x00\x20\x03\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x9E\xD3\x01\x00\x00\x20\x02\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x6E\xD3\x01\x00\x00\x20\x01\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x5E\xD1\x01\x00\x00\x20\x06\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xCE\xD5\x01\x00\x00\x20\x0B\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\xFE\xD7\x01\x00\x00\x20\x0C\x00'
        }

        self.InputStateNames = {
            b'\x00': 'Computer In1',
            b'\x04': 'Computer In2',
            b'\x02': 'S-Video',
            b'\x01': 'Video',
            b'\x03': 'HDMI',
            b'\x06': 'USB Type A',
            b'\x0B': 'LAN',
            b'\x0C': 'USB Type B'
        }

        ComputerIn1source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x6E\xDC\x01\x00\x30\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x9E\xDC\x01\x00\x30\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x0E\xDD\x01\x00\x30\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xFE\xDD\x01\x00\x30\x20\x00\x00'
        }

        ComputerIn2source = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x5E\xDD\x01\x00\x34\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xAE\xDD\x01\x00\x34\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x3E\xDC\x01\x00\x34\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xCE\xDC\x01\x00\x34\x20\x00\x00'
        }

        LANsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x4A\xDE\x01\x00\x3B\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xBA\xDE\x01\x00\x3B\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x2A\xDF\x01\x00\x3B\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xDA\xDF\x01\x00\x3B\x20\x00\x00'
        }

        USBTypeAsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xE6\xDC\x01\x00\x36\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x16\xDC\x01\x00\x36\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x86\xDD\x01\x00\x36\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x76\xDD\x01\x00\x36\x20\x00\x00'
        }

        USBTypeBsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x3E\xDF\x01\x00\x3C\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xCE\xDF\x01\x00\x3C\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x5E\xDE\x01\x00\x3C\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xAE\xDE\x01\x00\x3C\x20\x00\x00'
        }

        HDMIsource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x2A\xDC\x01\x00\x33\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\xDA\xDC\x01\x00\x33\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x4A\xDD\x01\x00\x33\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xBA\xDD\x01\x00\x33\x20\x00\x00'
        }

        SVideosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\xD6\xDD\x01\x00\x32\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x26\xDD\x01\x00\x32\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xB6\xDC\x01\x00\x32\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x46\xDC\x01\x00\x32\x20\x00\x00'
        }

        Videosource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x92\xDD\x01\x00\x31\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x62\xDD\x01\x00\x31\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\xF2\xDC\x01\x00\x31\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\x02\xDC\x01\x00\x31\x20\x00\x00'
        }

        Standbysource = {
            'Audio 1': b'\xBE\xEF\x03\x06\x00\x7A\xDF\x01\x00\x3F\x20\x01\x00',
            'Audio 2': b'\xBE\xEF\x03\x06\x00\x8A\xDF\x01\x00\x3F\x20\x02\x00',
            'Audio 3': b'\xBE\xEF\x03\x06\x00\x1A\xDE\x01\x00\x3F\x20\x03\x00',
            'Off': b'\xBE\xEF\x03\x06\x00\xEA\xDE\x01\x00\x3F\x20\x00\x00'
        }

        self.inputtypesource = {
            'Computer In1': ComputerIn1source,
            'Computer In2': ComputerIn2source,
            'LAN': LANsource,
            'USB Type A': USBTypeAsource,
            'USB Type B': USBTypeBsource,
            'HDMI': HDMIsource,
            'S-Video': SVideosource,
            'Video': Videosource,
            'Standby': Standbysource
        }

        self.AudioSourceStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xDD\x02\x00\x30\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xDC\x02\x00\x34\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xDF\x02\x00\x3B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xDD\x02\x00\x36\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xDE\x02\x00\x3C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xDD\x02\x00\x33\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xDC\x02\x00\x32\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xDC\x02\x00\x31\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xDE\x02\x00\x3F\x20\x00\x00'
        }

        self.AudioSourceStateNames = {
            b'\x00': 'Off',
            b'\x01': 'Audio 1',
            b'\x02': 'Audio 2',
            b'\x03': 'Audio 3',
        }

        self.DeviceStatusStateNames = {
            b'\x00': 'Normal',
            b'\x01': 'Cover Error',
            b'\x02': 'Fan Error',
            b'\x03': 'Lamp Error',
            b'\x04': 'Temperature Error',
            b'\x05': 'Air Flow Error',
            b'\x07': 'Cold Error',
            b'\x08': 'Filter Error',
        }

        ComputerIn1volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xAB\xCC\x04\x00\x60\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x7A\xCD\x05\x00\x60\x20\x00\x00'
        }

        ComputerIn2volume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x9B\xCD\x04\x00\x64\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x4A\xCC\x05\x00\x64\x20\x00\x00'
        }

        LANvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x8F\xCE\x04\x00\x6B\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x5E\xCF\x05\x00\x6B\x20\x00\x00'
        }

        USBTypeAvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x23\xCC\x04\x00\x66\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xF2\xCD\x05\x00\x66\x20\x00\x00'
        }

        USBTypeBvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xFB\xCF\x04\x00\x6C\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x2A\xCE\x05\x00\x6C\x20\x00\x00'
        }

        HDMIvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xEF\xCC\x04\x00\x63\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x3E\xCD\x05\x00\x63\x20\x00\x00'
        }

        SVideovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x13\xCD\x04\x00\x62\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\xC2\xCC\x05\x00\x62\x20\x00\x00'
        }

        Videovolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\x57\xCD\x04\x00\x61\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x86\xCC\x05\x00\x61\x20\x00\x00'
        }

        Standbyvolume = {
            'Up': b'\xBE\xEF\x03\x06\x00\xBF\xCF\x04\x00\x6F\x20\x00\x00',
            'Down': b'\xBE\xEF\x03\x06\x00\x6E\xCE\x05\x00\x6F\x20\x00\x00'
        }

        self.inputtypevolume = {
            'Computer In1': ComputerIn1volume,
            'Computer In2': ComputerIn2volume,
            'LAN': LANvolume,
            'USB Type A': USBTypeAvolume,
            'USB Type B': USBTypeBvolume,
            'HDMI': HDMIvolume,
            'S-Video': SVideovolume,
            'Video': Videovolume,
            'Standby': Standbyvolume
        }

        self.VolumeStatusStateQualifier = {
            'Computer In1': b'\xBE\xEF\x03\x06\x00\xCD\xCC\x02\x00\x60\x20\x00\x00',
            'Computer In2': b'\xBE\xEF\x03\x06\x00\xFD\xCD\x02\x00\x64\x20\x00\x00',
            'LAN': b'\xBE\xEF\x03\x06\x00\xE9\xCE\x02\x00\x6B\x20\x00\x00',
            'USB Type A': b'\xBE\xEF\x03\x06\x00\x45\xCC\x02\x00\x66\x20\x00\x00',
            'USB Type B': b'\xBE\xEF\x03\x06\x00\x9D\xCF\x02\x00\x6C\x20\x00\x00',
            'HDMI': b'\xBE\xEF\x03\x06\x00\x89\xCC\x02\x00\x63\x20\x00\x00',
            'S-Video': b'\xBE\xEF\x03\x06\x00\x75\xCD\x02\x00\x62\x20\x00\x00',
            'Video': b'\xBE\xEF\x03\x06\x00\x31\xCD\x02\x00\x61\x20\x00\x00',
            'Standby': b'\xBE\xEF\x03\x06\x00\xD9\xCF\x02\x00\x6F\x20\x00\x00'
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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='HW', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

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
