from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
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
            'M230X': self.nec_1_165_Lamp2X,
            'M260W': self.nec_1_165_Lamp2W,
            'M260WS': self.nec_1_165_Lamp2W,
            'M260X': self.nec_1_165_Lamp2X,
            'M260XS': self.nec_1_165_Lamp2X,
            'M300W': self.nec_1_165_Lamp2W,
            'M300WS': self.nec_1_165_Lamp2W,
            'M300X': self.nec_1_165_Lamp2X,
            'M300XS': self.nec_1_165_Lamp2X,
            'M350XS': self.nec_1_165_Lamp2X,
            'M350X': self.nec_1_165_Lamp2X,
            'NP-M420X': self.nec_1_165_Lamp2X,
            'NP-M420XV': self.nec_1_165_Lamp2X,
            'M311W': self.nec_1_165_Lamp1W,
            'NP-M260X': self.nec_1_165_Lamp2X,
            'NP-M260W': self.nec_1_165_Lamp2W,
            'NP-M271W': self.nec_1_165_Lamp1W,
            'NP-M271X': self.nec_1_165_Lamp1X,
            'NP-M300X': self.nec_1_165_Lamp2X,
            'NP-M311W': self.nec_1_165_Lamp1W,
            'NP-M311X': self.nec_1_165_Lamp1X,
            'NP-M350X': self.nec_1_165_Lamp2X,
            'NP-M360X': self.nec_1_165_Lamp1X,
            'NP-M361X': self.nec_1_165_Lamp1X,
            'M420X': self.nec_1_165_Lamp2X,
            'M420XV': self.nec_1_165_Lamp2X,
            'NP-M230X': self.nec_1_165_Lamp2X,
            'NP-M260WS': self.nec_1_165_Lamp2W,
            'NP-M260XS': self.nec_1_165_Lamp2X,
            'NP-M300W': self.nec_1_165_Lamp2W,
            'NP-M300WS': self.nec_1_165_Lamp2W,
            'NP-M300XS': self.nec_1_165_Lamp2X,
            'NP-M350XS': self.nec_1_165_Lamp2X,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'Magnify': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.AspectRatio_Set = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')
        self.AudioMute_Set = re.compile(b'(\x22\x12[\x00-\xFF]{4})|(\xA2\x12[\x00-\xFF]{6})')
        self.AutoImage_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
        self.ClosedCaption_Set = re.compile(b'(\x23\xB1[\x00-\xFF]{6}$)|(\xA3\xB1[\x00-\xFF]{6})')
        self.Freeze_Set = re.compile(b'(\x21\x98[\x00-xFF]{5})|(\xA1\x98[\x00-\xFF]{6})')
        self.Input_Set = re.compile(b'(\x22\x03[\x00-\xFF]{5})|(\xA2\x03[\x00-\xFF]{6})')
        self.LampMode_Set = re.compile(b'(\x23\xB1[\x00-\xFF]{6})|(\xA3\xB1[\x00-\xFF]{6})')
        self.Magnify_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
        self.MenuNavigation_Set = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
        self.Power_Set = re.compile(b'(\x22\x00[\x00-\xFF]{4})|(\xA2\x00[\x00-\xFF]{6})')
        self.VideoMute_Set = re.compile(b'(\x22[\x00-\xFF]{5})|(\xA2\x10[\x00-\xFF]{6})')
        self.Volume_Set = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')

        self.AspectRatio_Update = re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})')
        self.ClosedCaption_Update = re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})')
        self.DeviceStatus_Update = re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})')
        self.FilterUsage_Update = re.compile(b'(\x23\x8A[\x00-\xFF]{102})|(\xA3\x8A[\x00-\xFF]{6})')
        self.Input_Update = re.compile(b'(\x20\xC0[\x00-\xFF]{102})|(\xA0\xC0[\x00-\xFF]{6})')
        self.LampMode_Update = re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})')
        self.LampUsage_Update = re.compile(b'(\x23\x96[\x00-\xFF]{10})|(\xA3[\x00-\xFF]{7})')
        self.Power_Update = re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
        self.Volume_Update = re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.ARValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = self.ARStates[res[12]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAudioMute(self, value, qualifier):

        AudioMuteValues = {
            'On': b'\x02\x12\x00\x00\x00\x14',
            'Off': b'\x02\x13\x00\x00\x00\x15'
        }

        AudioMuteCmdString = AudioMuteValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ClosedCaptionValues = {
            'CC1': 0x01,
            'CC2': 0x02,
            'CC3': 0x03,
            'CC4': 0x04,
            'TEXT1': 0x05,
            'TEXT2': 0x06,
            'TEXT3': 0x07,
            'TEXT4': 0x08,
            'Off': 0x00
        }

        CheckSum = 0xBF + ClosedCaptionValues[value]
        ClosedCaptionCmdString = pack('>8B', 0x03, 0xB1, 0x00, 0x00, 0x02, 0x09, ClosedCaptionValues[value], CheckSum)
        self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaptionValues = {
            0x01: 'CC1',
            0x02: 'CC2',
            0x03: 'CC3',
            0x04: 'CC4',
            0x05: 'TEXT1',
            0x06: 'TEXT2',
            0x07: 'TEXT3',
            0x08: 'TEXT4',
            0x00: 'Off'
        }

        ClosedCaptionCmdString = b'\x03\xB0\x00\x00\x01\x09\xBD'
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaptionValues[res[6]]
                self.WriteStatus('ClosedCaption', value, None)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp Cover Error',
            b'\x02\x00\x00\x00': 'Temperature Error',
            b'\x10\x00\x00\x00': 'Fan Failure',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Error',
            b'\x80\x00\x00\x00': 'Lamp Life Expired',
            b'\x00\x01\x00\x00': 'Lamp Beyond Limit',
            b'\x00\x02\x00\x00': 'Format Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Failure',
            b'\x00\x00\x08\x00': 'Lamp Housing Error',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'High Temperature',
            b'\x00\x00\x00\x08': 'Sensor Error',
            b'\x00\x00\x00\x10': 'Pump Error'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                value = DeviceStatusValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, None)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                filter_value = int(((res[94] << 24) + (res[93] << 16) + (res[92] << 8) + res[91]) / 3600)
                operate_value = int(((res[102] << 24) + (res[101] << 16) + (res[100] << 8) + res[99]) / 3600)
                self.WriteStatus('OperationHours', operate_value, None)
                self.WriteStatus('FilterUsage', filter_value, None)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

    def SetFreeze(self, value, qualifier):

        FreezeValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = FreezeValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetInput(self, value, qualifier):

        InputValues = {
            'Computer 1': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'Computer 2': b'\x02\x03\x00\x00\x02\x01\x02\x0A',
            'HDMI': b'\x02\x03\x00\x00\x02\x01\x1A\x22',
            'Video': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'S-Video': b'\x02\x03\x00\x00\x02\x01\x0B\x13',
            'Viewer': b'\x02\x03\x00\x00\x02\x01\x1F\x27',
            'Network': b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'USB Display': b'\x02\x03\x00\x00\x02\x01\x22\x2A'
        }

        InputCmdString = InputValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputValues = {
            b'\x01\x01': 'Computer 1',
            b'\x02\x01': 'Computer 2',
            b'\x01\x06': 'HDMI',
            b'\x01\x02': 'Video',
            b'\x01\x03': 'S-Video',
            b'\x01\x07': 'Viewer',
            b'\x02\x07': 'Network',
            b'\x04\x07': 'USB Display'
        }
        AudioMuteValues = {
            0x01: 'On',
            0x00: 'Off'
        }
        VideoMuteValues = {
            0x01: 'On',
            0x00: 'Off'
        }
        FreezeValues = {
            0x01: 'On',
            0x00: 'Off'
        }
        InputCmdString = b'\x00\xC0\x00\x00\x00\xC0'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                inputValue = InputValues[res[11:13]]
                self.WriteStatus('Input', inputValue, None)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            try:
                audioValue = AudioMuteValues[res[34]]
                self.WriteStatus('AudioMute', audioValue, None)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

            try:
                videoValue = VideoMuteValues[res[33]]
                self.WriteStatus('VideoMute', videoValue, None)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

            try:
                freezeValue = FreezeValues[res[36]]
                self.WriteStatus('Freeze', freezeValue, None)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

    def SetLampMode(self, value, qualifier):

        LampModeCmdString = self.LampModeValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = self.LampModeNames[res[6]]
                self.WriteStatus('LampMode', value, None)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                lampHour = int(unpack('>I', res[10:11] + res[9:10] + res[8:9] + res[7:8])[0] / 3600)  # Value of Lamp usage is in seconds
                self.WriteStatus('LampUsage', lampHour, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

    def SetMagnify(self, value, qualifier):

        MagnifyValues = {
            'Up': b'\x02\x0F\x00\x00\x02\x0F\x00\x22',
            'Down': b'\x02\x0F\x00\x00\x02\x10\x00\x23'
        }
        MagnifyCmdString = MagnifyValues[value]
        self.__SetHelper('Magnify', MagnifyCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationValues = {
            'Menu': 0x06,
            'Up': 0x07,
            'Down': 0x08,
            'Left': 0x0A,
            'Right': 0x09,
            'Enter': 0x0B,
            'Cancel': 0x0C
        }
        CheckSum = 0x13 + MenuNavigationValues[value]
        MenuNavigationCmdString = pack('>8B', 0x02, 0x0F, 0x00, 0x00, 0x02, MenuNavigationValues[value], 0x00, CheckSum)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def UpdateOperationHours(self, value, qualifier):

        self.UpdateFilterUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03'
        }
        PowerCmdString = PowerValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerValues = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x05: 'Cooling',
            0x02: 'Warming',
            0x09: 'Warming',
            0x0F: 'Off'
        }

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = PowerValues[res[10]]
                self.WriteStatus('Power', value, None)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = VideoMuteValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 31
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            CheckSum = 0x1D + value
            VolumeCmdString = pack('11B', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, CheckSum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[12]
                self.WriteStatus('Volume', value, None)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, command, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'Unknown command.',
            b'\x00\x01': 'Unsupported Command.',
            b'\x01\x00': 'Invalid values specificed.',
            b'\x01\x01': 'Specified terminal is unavailable or cannot be selected.',
            b'\x02\x03': 'Setting not possible.',
            b'\x02\x0D': 'Power Off inhibited.'
        }
        if (response[0:1] == b'\xA0' or response[0:1] == b'\xA1' or response[0:1] == b'\xA2' or response[0:1] == b'\xA3') and response[5:7] in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[response[5:7]]])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        CommandDelimValues = {
            'AspectRatio': self.AspectRatio_Set,
            'AudioMute': self.AudioMute_Set,
            'AutoImage': self.AutoImage_Set,
            'ClosedCaption': self.ClosedCaption_Set,
            'Freeze': self.Freeze_Set,
            'Input': self.Input_Set,
            'LampMode': self.LampMode_Set,
            'Magnify': self.Magnify_Set,
            'MenuNavigation': self.MenuNavigation_Set,
            'Power': self.Power_Set,
            'VideoMute': self.VideoMute_Set,
            'Volume': self.Volume_Set
        }

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            res = ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=CommandDelimValues[command])
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        CommandDelimValues = {
            'AspectRatio': self.AspectRatio_Update,
            'ClosedCaption': self.ClosedCaption_Update,
            'DeviceStatus': self.DeviceStatus_Update,
            'FilterUsage': self.FilterUsage_Update,
            'Input': self.Input_Update,
            'LampMode': self.LampMode_Update,
            'LampUsage': self.LampUsage_Update,
            'Power': self.Power_Update,
            'Volume': self.Volume_Update
        }

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=CommandDelimValues[command])
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

    def nec_1_165_Lamp1X(self):
        self.LampModeValues = {
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Auto Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
        }

        self.LampModeNames = {
            0x00: 'Off',
            0x01: 'Auto Eco',
            0x02: 'Normal',
            0x03: 'Eco'
        }

        self.ARValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Wide Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

        self.ARStates = {
            0x00: 'Auto',
            0x04: '4:3',
            0x02: '16:9',
            0x05: '15:9',
            0x06: '16:10',
            0x01: 'Wide Zoom',
            0x03: 'Native'
        }

    def nec_1_165_Lamp1W(self):

        self.LampModeValues = {
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Auto Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
        }

        self.LampModeNames = {
            0x00: 'Off',
            0x01: 'Auto Eco',
            0x02: 'Normal',
            0x03: 'Eco'
        }

        self.ARValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

        self.ARStates = {
            0x00: 'Auto',
            0x04: '4:3',
            0x02: '16:9',
            0x05: '15:9',
            0x06: '16:10',
            0x07: 'Letterbox',
            0x03: 'Native'
        }

    def nec_1_165_Lamp2X(self):

        self.LampModeValues = {
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Auto Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
        }

        self.LampModeNames = {
            0x00: 'Off',
            0x01: 'Auto Eco',
            0x02: 'Eco 1',
            0x03: 'Eco 2'
        }

        self.ARValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Wide Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

        self.ARStates = {
            0x00: 'Auto',
            0x04: '4:3',
            0x02: '16:9',
            0x05: '15:9',
            0x06: '16:10',
            0x01: 'Wide Zoom',
            0x03: 'Native'
        }

    def nec_1_165_Lamp2W(self):

        self.LampModeValues = {
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Auto Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x03\xC0'
        }

        self.LampModeNames = {
            0x00: 'Off',
            0x01: 'Auto Eco',
            0x02: 'Eco 1',
            0x03: 'Eco 2'
        }

        self.ARValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

        self.ARStates = {
            0x00: 'Auto',
            0x04: '4:3',
            0x02: '16:9',
            0x05: '15:9',
            0x06: '16:10',
            0x07: 'Letterbox',
            0x03: 'Native'
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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
