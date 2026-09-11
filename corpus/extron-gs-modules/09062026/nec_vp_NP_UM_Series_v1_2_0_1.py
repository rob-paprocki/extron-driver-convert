from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
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
            'NP-UM351WG': self.nec_1_1364_WSeries,
            'NP-UM351W': self.nec_1_1364_WSeries,
            'NP-UM361X': self.nec_1_1364_XSeries,
            'NP-UM301X': self.nec_1_1364_XSeries,
            'NP-UM301W': self.nec_1_1364_301W,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Freeze': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OperationHours': {'Status': {}},
            'Power': {'Status': {}},
            'SignalStatus': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}}
        }       

        if self.Unidirectional == 'False':
            self.SetAspectRatioRegex = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')
            self.SetAutoImageRegex = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
            self.SetAudioMuteRegex = re.compile(b'(\x22\x12[\x00-\xFF]{4})|(\xA2\x12[\x00-\xFF]{6})')
            self.SetFreezeRegex = re.compile(b'(\x21\x98[\x00-xFF]{5})|(\xA1\x98[\x00-\xFF]{6})')
            self.SetInputRegex = re.compile(b'(\x22\x03[\x00-\xFF]{5})|(\xA2\x03[\x00-\xFF]{6})')
            self.SetLampModeRegex = re.compile(b'(\x23\xB1[\x00-\xFF]{6})|(\xA3\xB1[\x00-\xFF]{6})')
            self.SetMenuNavigationRegex = re.compile(b'(\x22\x0F[\x00-\xFF]{5})|(\xA2\x0F[\x00-\xFF]{6})')
            self.SetPowerRegex = re.compile(b'(\x22\x00[\x00-\xFF]{4})|(\xA2\x00[\x00-\xFF]{6})')
            self.SetVideoMuteRegex = re.compile(b'(\x22[\x00-\xFF]{5})|(\xA2\x10[\x00-\xFF]{6})')
            self.SetVolumeRegex = re.compile(b'(\x23\x10[\x00-\xFF]{6})|(\xA3\x10[\x00-\xFF]{6})')

            self.UpdateAspectRatioRegex = re.compile(b'(\x23\x04[\x00-\xFF]{17})|(\xA3\x04[\x00-\xFF]{6})')
            self.UpdateDeviceStatusRegex = re.compile(b'(\x20\x88[\x00-\xFF]{16})|(\xA0\x88[\x00-\xFF]{6})')
            self.UpdateFreezeRegex = re.compile(b'(\x20\xC0[\x00-\xFF]{132})|(\xA0\xC0[\x00-\xFF]{6})')
            self.UpdateFilterUsageRegex = re.compile(b'(\x23\x8A[\x00-\xFF]{102})|(\xA3\x8A[\x00-\xFF]{6})')
            self.UpdateInputRegex = re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.UpdateLampModeRegex = re.compile(b'(\x23\xB0[\x00-\xFF]{6})|(\xA3\xB0[\x00-\xFF]{6})')
            self.UpdateLampUsageRegex = re.compile(b'(\x23\x8C[\x00-\xFF]{20})|(\xA3\x96[\x00-\xFF]{6})')
            self.UpdatePowerRegex = re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.UpdateVideoMuteRegex = re.compile(b'(\x20\x85[\x00-\xFF]{20})|(\xA0\x85[\x00-\xFF]{6})')
            self.UpdateVolumeRegex = re.compile(b'(\x23[\x00-\xFF]{18})|(\xA3[\x00-\xFF]{7})')

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectRatio[value]
        res = self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res[0:2] == b'\x23\x10':
            pass
        elif res[0:2] == b'\xA3\x10':
            self.__CheckResponseForErrors('AspectRatio', res)
        else:
            print('Invalid/Unexpected Response for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x03\x04\x00\x00\x03\x18\x00\x00\x22'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    value = self.AspectRatioValues[res[12]]
                    self.WriteStatus('AspectRatio', value, qualifier)
                else:
                    self.__CheckResponseForErrors('AspectRatio', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x12\x00\x00\x00\x14',
            'Off': b'\x02\x13\x00\x00\x00\x15',
        }

        AudioMuteCmdString = ValueStateValues[value]
        res = self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if len(res) != 6:
            self.__CheckResponseForErrors('AudioMute', res)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdateVideoMute(value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        res = self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        if res[0:2] == b'\x22\x0F':
            pass
        elif res[0:2] == b'\xA2\x0F':
            self.__CheckResponseForErrors('AutoImage', res)
        else:
            print('Invalid/Unexpected Response for SetAutoImage')

    def UpdateDeviceStatus(self, value, qualifier):

        ErrorStatus = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Lamp Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error (Bimetal)',
            b'\x10\x00\x00\x00': 'Fan Failure',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp1 Error',
            b'\x80\x00\x00\x00': 'Lamp1 Life Expired',
            b'\x00\x01\x00\x00': 'Lamp1 Life Limit Reached',
            b'\x00\x02\x00\x00': 'Formatter Error',
            b'\x00\x04\x00\x00': 'Lamp2 Error',
            b'\x00\x00\x02\x00': 'FPGA error',
            b'\x00\x00\x04\x00': 'Temp Error (Sensor)',
            b'\x00\x00\x08\x00': 'Lamp1 Housing Error',
            b'\x00\x00\x10\x00': 'Lamp1 Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x40\x00': 'Lamp2 Life Expired',
            b'\x00\x00\x80\x00': 'Lamp2 Life Limit Reached',
            b'\x00\x00\x00\x01': 'Lamp2 Housing Error',
            b'\x00\x00\x00\x02': 'Lamp2 Data Error',
            b'\x00\x00\x00\x04': 'High Temp Due to Dust',
            b'\x00\x00\x00\x08': 'Foreign Object Sensor Error',
            b'\x00\x00\x00\x10': 'Pump Error',
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 18:
                    value = ErrorStatus.get(res[5:9], 'Multiple Errors')
                    self.WriteStatus('DeviceStatus', value, qualifier)
                else:
                    self.__CheckResponseForErrors('DeviceStatus', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateDeviceStatus')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = ValueStateValues[value]
        res = self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        try:
            if len(res) != 7:
                self.__CheckResponseForErrors('Freeze', res)
        except (KeyError, IndexError):
            print('Invalid/Unexpected Response for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeStateValues = {
            0x01: 'On',
            0x00: 'Off',
            0xFF: 'Not Supported'
        }

        FreezeCmdString = b'\x00\xC0\x00\x00\x00\xC0'
        res = self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 134:

                    value = FreezeStateValues[res[36]]
                    self.WriteStatus('Freeze', value, qualifier)
                else:
                    self.__CheckResponseForErrors('Freeze', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateFreeze')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x8A\x00\x00\x00\x8D'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 104:
                    filter_str = res[91:95]
                    filter_str = filter_str[::-1]
                    filter_val1 = filter_str[0]
                    filter_val2 = filter_str[1]
                    filter_val3 = filter_str[2]
                    filter_val4 = filter_str[3]
                    filter_value = round(int(hex(filter_val1) + hex(filter_val2)[2:4] + hex(filter_val3)[2:4] + hex(filter_val4)[2:4], 16) / 3600)
                    self.WriteStatus('FilterUsage', filter_value, qualifier)

                    operate_str = res[99:103]
                    operate_str = operate_str[::-1]
                    operate_val1 = operate_str[0]
                    operate_val2 = operate_str[1]
                    operate_val3 = operate_str[2]
                    operate_val4 = operate_str[3]
                    operate_value = round(int(hex(operate_val1) + hex(operate_val2)[2:4] + hex(operate_val3)[2:4] + hex(operate_val4)[2:4], 16) / 3600)

                    self.WriteStatus('OperationHours', operate_value, qualifier)
                else:
                    self.__CheckResponseForErrors('FilterUsage', res)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateFilterUsage')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'HDMI1': b'\x02\x03\x00\x00\x02\x01\x1A\x22',
            'HDMI2': b'\x02\x03\x00\x00\x02\x01\x1B\x23',
            'Video': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'USB-A': b'\x02\x03\x00\x00\x02\x01\x1F\x27',
            'LAN': b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'USB-B': b'\x02\x03\x00\x00\x02\x01\x22\x2A'
        }

        InputCmdString = ValueStateValues[value]
        res = self.__SetHelper('Input', InputCmdString, value, qualifier)
        if len(res) != 7:
            self.__CheckResponseForErrors('Input', res)

    def UpdateInput(self, value, qualifier):

        InputStateValues = {
            b'\x01\x01': 'Computer',
            b'\x01\x06': 'HDMI1',
            b'\x01\x21': 'HDMI1',
            b'\x03\x06': 'HDMI2',
            b'\x02\x21': 'HDMI2',
            b'\x01\x02': 'Video',
            b'\x01\x07': 'USB-A',
            b'\x02\x07': 'LAN',
            b'\x04\x07': 'USB-B',
        }

        SignalStateValues = {
            0x01: 'Signal Present',
            0x00: 'No Signal Present',
            0x02: 'Viewer displaying',
            0x03: 'Test pattern displaying',
            0x04: 'LAN displaying',
        }

        InputCmdString = b'\x00\x85\x00\x00\x01\x02\x88'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:

                    value = InputStateValues[res[7:9]]
                    self.WriteStatus('Input', value, qualifier)

                    signal_value = SignalStateValues[res[13]]
                    self.WriteStatus('SignalStatus', signal_value, qualifier)
                else:
                    self.__CheckResponseForErrors('Input', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateInput')

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco': b'\x03\xB1\x00\x00\x02\x07\x01\xBE'
        }

        LampModeCmdString = ValueStateValues[value]
        res = self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)
        if res[0:2] == b'\x23\xB1':
            pass
        elif res[0:2] == b'\xA3\xB1':
            self.__CheckResponseForErrors('LampMode', res)
        else:
            print('Invalid/Unexpected Response for SetLampMode')

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x01: 'Eco',
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                if res[0:2] == b'\x23\xB0':
                    value = ValueStateValues[res[6]]
                    self.WriteStatus('LampMode', value, qualifier)
                elif res[0:2] == b'\xA3\xB0':
                    self.__CheckResponseForErrors('LampMode', res)
                else:
                    print('Invalid/Unexpected Response for UpdateLampMode')
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x8C\x00\x00\x00\x8F'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    temp_usage = res[5:9]
                    temp_usage = temp_usage[::-1]
                    lamp_val1 = temp_usage[0]
                    lamp_val2 = temp_usage[1]
                    lamp_val3 = temp_usage[2]
                    lamp_val4 = temp_usage[3]
                    lamp_value = round(int(hex(lamp_val1) + hex(lamp_val2)[2:4] + hex(lamp_val3)[2:4] + hex(lamp_val4)[2:4], 16) / 3600)

                    self.WriteStatus('LampUsage', lamp_value, qualifier)
                else:
                    self.__CheckResponseForErrors('LampUsage', res)
            except (IndexError, ValueError):
                print('Invalid/Unexpected Response for UpdateLampUsage')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Cancel': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        res = self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        if len(res) != 7:
            self.__CheckResponseForErrors('MenuNavigation', res)

    def UpdateOperationHours(self, value, qualifier):
        self.UpdateFilterUsage(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03',
        }

        PowerCmdString = ValueStateValues[value]
        res = self.__SetHelper('Power', PowerCmdString, value, qualifier)
        if len(res) != 6:
            self.__CheckResponseForErrors('Power', res)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x00\x85\x00\x00\x01\x01\x87'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = self.PowerStateValues[res[10]]
                    self.WriteStatus('Power', value, qualifier)
                else:
                    self.__CheckResponseForErrors('Power', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdatePower')

    def UpdateSignalStatus(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        res = self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if len(res) != 6:
            self.__CheckResponseForErrors('VideoMute', res)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        VideoMuteCmdString = b'\x00\x85\x00\x00\x01\x03\x89'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 22:
                    value = ValueStateValues[res[5]]
                    self.WriteStatus('VideoMute', value, qualifier)

                    mute_val = ValueStateValues[res[6]]
                    self.WriteStatus('AudioMute', mute_val, qualifier)

                else:
                    self.__CheckResponseForErrors('VideoMute', res)
            except (KeyError, IndexError):
                print('Invalid/Unexpected Response for UpdateVideoMute')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            CKS = 0x1D + value
            VolumeCmdString = pack('>11B', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, CKS)
            res = self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
            if res[0:2] == b'\x23\x10':
                pass
            elif res[0:2] == b'\xA3\x10':
                self.__CheckResponseForErrors('Volume', res)
            else:
                print('Invalid/Unexpected Response for SetVolume')
        else:
            print('Invalid Command')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                if len(res) == 19:
                    if 0 <= res[12] <= 63:
                        value = res[12]
                        self.WriteStatus('Volume', value, None)
                else:
                    self.__CheckResponseForErrors('Volume', res)
            except (ValueError, IndexError):
                print('Invalid/Unexpected Response for UpdateVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': "Unknown Command",
            b'\x00\x01': "The current model does not support this function.",
            b'\x01\x00': "Unvalid values specified",
            b'\x01\x01': "Specified terminal is unavailable or cannot be selected",
            b'\x01\x02': "Selected language is not available",
            b'\x02\x00': "Available memory reservation error",
            b'\x02\x02': "Operating memory",
            b'\x02\x03': "Setting not possible",
            b'\x02\x04': "On Forced on-screen mute mode",
            b'\x02\x07': "No Signal",
            b'\x02\x08': "Displaying a test pattern or PC Card Fills screen.",
            b'\x02\x0A': "Memory Operation Failed",
            b'\x02\x0D': "Power Off inhibited",
            b'\x02\x0E': "Execution error",
            b'\x02\x0F': "No operation authority",
            b'\x03\x00': "Specified gain number is wrong",
            b'\x03\x01': "Specified gain not available",
            b'\x03\x02': "Adjustment failed",
        }

        if response[-3:-1] in DEVICE_ERROR_CODES:
            print('{0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[response[-3:-1]]))
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        CommandDelimValues = {
            'AspectRatio': self.SetAspectRatioRegex,
            'AutoImage': self.SetAutoImageRegex,
            'AudioMute': self.SetAudioMuteRegex,
            'Freeze': self.SetFreezeRegex,
            'Input': self.SetInputRegex,
            'LampMode': self.SetLampModeRegex,
            'MenuNavigation': self.SetMenuNavigationRegex,
            'Power': self.SetPowerRegex,
            'VideoMute': self.SetVideoMuteRegex,
            'Volume': self.SetVolumeRegex
        }

        if self.Unidirectional == 'True' or command == 'UserDefinedCommand':
            self.Send(commandstring)
            res = ''
        else:
            regex = CommandDelimValues[command]
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                print('No Response')
                print('Invalid/Unexpected Response')
        return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        CommandDelimValues = {
            'AspectRatio': self.UpdateAspectRatioRegex,
            'DeviceStatus': self.UpdateDeviceStatusRegex,
            'Freeze': self.UpdateFreezeRegex,
            'FilterUsage': self.UpdateFilterUsageRegex,
            'Input': self.UpdateInputRegex,
            'LampMode': self.UpdateLampModeRegex,
            'LampUsage': self.UpdateLampUsageRegex,
            'Power': self.UpdatePowerRegex,
            'VideoMute': self.UpdateVideoMuteRegex,
            'Volume': self.UpdateVolumeRegex,
        }

        regex = CommandDelimValues[command]

        if self.Unidirectional == 'True':
            print('Inappropriate Command')
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                return ''
            else:
                return res            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def nec_1_1364_301W(self):    

        self.AspectRatio = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E',
        }

        self.AspectRatioValues = {
            0x00: 'Auto',
            0x01: '4:3',
            0x02: '16:9',
            0x0D: '15:9',
            0x0C: '16:10',
            0x07: 'Letterbox',
            0x0E: 'Native',
        }
        self.PowerStateValues = {
            0x04: 'On',
            0x00: 'Off',
            0x02: 'Warming Up'
        }

    def nec_1_1364_WSeries(self):   

        self.AspectRatio = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E',
        }

        self.AspectRatioValues = {
            0x00: 'Auto',
            0x01: '4:3',
            0x02: '16:9',
            0x0D: '15:9',
            0x0C: '16:10',
            0x07: 'Letterbox',
            0x0E: 'Native',
        }

        self.PowerStateValues = {
            0x04: 'On',
            0x00: 'Off',
            0x05: 'Cooling Down',
            0x02: 'Warming Up',
        }

    def nec_1_1364_XSeries(self):   

        self.AspectRatio = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            'Wide Zoom': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E',
        }

        self.AspectRatioValues = {
            0x00: 'Auto',
            0x01: '4:3',
            0x02: '16:9',
            0x0D: '15:9',
            0x0C: '16:10',
            0x03: 'Wide Zoom',
            0x0E: 'Native',
        }

        self.PowerStateValues = {
            0x04: 'On',
            0x00: 'Off',
            0x05: 'Cooling Down',
            0x02: 'Warming Up',
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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