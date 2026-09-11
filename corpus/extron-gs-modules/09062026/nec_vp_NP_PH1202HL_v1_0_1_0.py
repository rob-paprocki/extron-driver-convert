from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'LensProfile': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}}
        }

        if self.Unidirectional == 'False':

            self.regex1 = re.compile(b'(\xA1[\x00-\xFF]{7})|(\x21[\x00-\xFF]{6})')
            self.regex2 = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{5})')
            self.regex3 = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7,8})')
            self.regex4 = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{6})')
            self.regex10 = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{7})')

            self.regex5 = re.compile(b'(\xA0[\x00-\xFF]{7})|(\x20[\x00-\xFF]{17})')
            self.regex6 = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{13})')
            self.regex7 = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{7,8})')
            self.regex8 = re.compile(b'(\xA3[\x00-\xFF]{7})|(\x23[\x00-\xFF]{11})')
            self.regex9 = re.compile(b'(\xA0[\x00-\xFF]{7})|(\x20[\x00-\xFF]{21})')
            self.regex11 = re.compile(b'(\xA2[\x00-\xFF]{7})|(\x22[\x00-\xFF]{7})')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0F\x00\x3F',
            '4:3 (Windows)': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            '5:4': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0B\x00\x3B',
            '16:9 (Wide Screen)': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0D\x00\x3D',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0C\x00\x3C',
            'Zoom (Full)': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x0E\x00\x3E',
            'Letter Box': b'\x03\x10\x00\x00\x05\x18\x00\x00\x01\x00\x31'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error(Bi-metallic strip)',
            b'\x10\x00\x00\x00': 'Fan Error',
            b'\x20\x00\x00\x00': 'Power Error',
            b'\x40\x00\x00\x00': 'Lamp Off',
            b'\x80\x00\x00\x00': 'Replace Lamp',
            b'\x00\x01\x00\x00': 'Lamp Life Expired',
            b'\x00\x02\x00\x00': 'Formatter Error',
            b'\x00\x00\x02\x00': 'FPGA Error',
            b'\x00\x00\x04\x00': 'Temp Sensor Error',
            b'\x00\x00\x08\x00': 'Lamp Not Present',
            b'\x00\x00\x10\x00': 'Lamp Data Error',
            b'\x00\x00\x20\x00': 'Mirror Cover Error',
            b'\x00\x00\x00\x04': 'Temperature Error due to Dust',
            b'\x00\x00\x00\x10': 'Foreign Matter Sensor Error',
            b'\x00\x00\x00\x20': 'Ballast Communication Error',
            b'\x00\x00\x00\x40': 'Iris Callibration Error',
            b'\x00\x00\x00\x80': 'Lens not properly installed'
        }
        ExtendedStateValues = {
            0x01: 'Portrait cover side is up',
            0x02: 'Interlock switch is open',
            0x04: 'System Error',
            0x10: 'System Formatter Error'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if res[13] != 0x00:
                    value = ExtendedStateValues.get(res[13], 'Multiple Errors')
                else:
                    value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except IndexError:
                print('Device Status: Invalid/unexpected response for UpdateDeviceStatus')

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x95\x00\x00\x00\x98'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = ((res[8] << 24) + (res[7] << 16) + (res[6] << 8) + res[5]) / 3600
                self.WriteStatus('FilterUsage', int(value), qualifier)
            except (ValueError, IndexError):
                print('Filter Usage: Invalid/unexpected response for UpdateFilterUsage')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x98\x00\x00\x01\x01\x9B',
            'Off': b'\x01\x98\x00\x00\x01\x02\x9C'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'Display Port': b'\x02\x03\x00\x00\x02\x01\xA6\xAE',
            'BNC': b'\x02\x03\x00\x00\x02\x01\x02\x0A',
            'BNC(CV)': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'BNC(Y/C)': b'\x02\x03\x00\x00\x02\x01\x0B\x13',
            'Computer': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'HDBaseT': b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'Slot': b'\x02\x03\x00\x00\x02\x01\xAB\xB3'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'\x03\xB1\x00\x00\x02\x07\x00\xBD',
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x03\xC0',
            'Long Life': b'\x03\xB1\x00\x00\x02\x07\x04\xC1'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Normal',
            0x02: 'Eco 1',
            0x03: 'Eco 2',
            0x04: 'Long Life'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                print('Lamp Mode: Invalid/unexpected response for UpdateLampMode')

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = ((res[10] << 24) + (res[9] << 16) + (res[8] << 8) + res[7]) / 3600
                self.WriteStatus('LampUsage', int(value), qualifier)
            except (ValueError, IndexError):
                print('Lamp Usage: Invalid/unexpected response for UpdateLampUsage')

    def SetLensProfile(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x02\x27\x00\x00\x01\x00\x2A',
            '2': b'\x02\x27\x00\x00\x01\x01\x2B'
        }
        LensProfileCmdString = ValueStateValues[value]
        self.__SetHelper('LensProfile', LensProfileCmdString, value, qualifier)

    def UpdateLensProfile(self, value, qualifier):

        ValueStateValues = {
            0: '1',
            1: '2'
        }

        LensProfileCmdString = b'\x02\x28\x00\x00\x00\x2A'
        res = self.__UpdateHelper('LensProfile', LensProfileCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[5]]
                self.WriteStatus('LensProfile', value, qualifier)
            except (KeyError, IndexError):
                print('Lens Profile: Invalid/unexpected response for UpdateLensProfile')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x02\x0F\x00\x00\x02\x06\x00\x19',
            'Up': b'\x02\x0F\x00\x00\x02\x07\x00\x1A',
            'Down': b'\x02\x0F\x00\x00\x02\x08\x00\x1B',
            'Left': b'\x02\x0F\x00\x00\x02\x0A\x00\x1D',
            'Right': b'\x02\x0F\x00\x00\x02\x09\x00\x1C',
            'Enter': b'\x02\x0F\x00\x00\x02\x0B\x00\x1E',
            'Exit': b'\x02\x0F\x00\x00\x02\x0C\x00\x1F'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'Off': b'\x03\xB1\x00\x00\x03\xC5\x02\x00\x7E',
            'BNC(CV)': b'\x03\xB1\x00\x00\x03\xC5\x02\x01\x7F',
            'BNC(Y/C)': b'\x03\xB1\x00\x00\x03\xC5\x02\x02\x80',
            'HDMI': b'\x03\xB1\x00\x00\x03\xC5\x02\x03\x81',
            'SLOT': b'\x03\xB1\x00\x00\x03\xC5\x02\x04\x82',
            'DisplayPort': b'\x03\xB1\x00\x00\x03\xC5\x02\x05\x83',
            'Computer': b'\x03\xB1\x00\x00\x03\xC5\x02\x06\x84',
            'BNC': b'\x03\xB1\x00\x00\x03\xC5\x02\x07\x85',
            'HDBaseT': b'\x03\xB1\x00\x00\x03\xC5\x02\x08\x86'
        }

        PIPInputCmdString = ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Off',
            0x01: 'BNC(CV)',
            0x02: 'BNC(Y/C)',
            0x03: 'HDMI',
            0x04: 'SLOT',
            0x05: 'DisplayPort',
            0x06: 'Computer',
            0x07: 'BNC',
            0x08: 'HDBaseT'
        }

        PIPInputCmdString = b'\x03\xB0\x00\x00\x02\xC5\x02\x7C'
        res = self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('PIPInput', value, qualifier)
            except (KeyError, IndexError):
                print('PIP Input: Invalid/unexpected response for UpdatePIPInput')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'PIP': b'\x03\xB1\x00\x00\x03\xC5\x00\x00\x7C',
            'Picture By Picture': b'\x03\xB1\x00\x00\x03\xC5\x00\x01\x7D'
        }

        PIPModeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        ValueStateValues = {
            0x00: 'PIP',
            0x01: 'Picture By Picture'
        }

        PIPModeCmdString = b'\x03\xB0\x00\x00\x02\xC5\x00\x7A'
        res = self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('PIPMode', value, qualifier)
            except (KeyError, IndexError):
                print('PIP Mode: Invalid/unexpected response for UpdatePIPMode')

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top-Left': b'\x03\xB1\x00\x00\x03\xC5\x01\x00\x7D',
            'Top-Right': b'\x03\xB1\x00\x00\x03\xC5\x01\x01\x7E',
            'Bottom-Left': b'\x03\xB1\x00\x00\x03\xC5\x01\x02\x7F',
            'Bottom-Right': b'\x03\xB1\x00\x00\x03\xC5\x01\x03\x80'
        }

        PIPPositionCmdString = ValueStateValues[value]
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def UpdatePIPPosition(self, value, qualifier):

        ValueStateValues = {
            0x00: 'Top-Left',
            0x01: 'Top-Right',
            0x02: 'Bottom-Left',
            0x03: 'Bottom-Right'
        }

        PIPPositionCmdString = b'\x03\xB0\x00\x00\x02\xC5\x01\x7B'
        res = self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('PIPPosition', value, qualifier)
            except (KeyError, IndexError):
                print('PIP Position: Invalid/unexpected response for UpdatePIPPosition')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerStateValues = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x0F: 'Off',
            0x10: 'Off',
            0x05: 'Cooling'
        }
        InputStateValues = {
            b'\x01\x21': 'HDMI',
            b'\x01\x22': 'Display Port',
            b'\x02\x01': 'BNC',
            b'\x01\x02': 'BNC(CV)',
            b'\x01\x03': 'BNC(Y/C)',
            b'\x01\x01': 'Computer',
            b'\x02\x07': 'HDBaseT',
            b'\x01\x23': 'Slot'
        }
        OtherStateValues = {
            0x01: 'On',
            0x00: 'Off'
        }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerStateValues[res[6]]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response for Power for UpdatePower')
            try:
                InputValue = InputStateValues[res[8:10]]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response for Input')
            try:
                VideoMuteValue = OtherStateValues[res[11]]
                self.WriteStatus('VideoMute', VideoMuteValue, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response for Video Mute')
            try:
                FreezeValue = OtherStateValues[res[14]]
                self.WriteStatus('Freeze', FreezeValue, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/unexpected response for Freeze')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': ': Command not recognized.',
            b'\x00\x01': ': Unsupported Command.',
            b'\x01\x00': ': Invalid values specificed.',
            b'\x01\x01': ': Specified input terminal is invalid.',
            b'\x01\x02': ': Selected language is invalid.',
            b'\x02\x00': ': Memory allocation error.',
            b'\x02\x02': ': Memory in use.',
            b'\x02\x03': ': Specified value cannot be set.',
            b'\x02\x04': ': Forced onscreen mute on.',
            b'\x02\x06': ': Viewer Error.',
            b'\x02\x07': ': No Signal.',
            b'\x02\x08': ': Displaying a test pattern or Filer.',
            b'\x02\x09': ': No PC Card is inserted.',
            b'\x02\x0A': ': Memory Operation Failed.',
            b'\x02\x0C': ': An entry list is Displayed.',
            b'\x02\x0D': ': Command cannot be accepted because Power is Off.',
            b'\x02\x0E': ': Command Execution Failed.',
            b'\x02\x0F': ': No authority neccessary for the operation .',
            b'\x03\x00': ': Specified gain number is incorrect.',
            b'\x03\x01': ': Specified gain is invalid.',
            b'\x03\x02': ': Adjustment failed.'
            }
        if response[0] in [0xA3, 0xA2, 0xA1, 0xA0]:
            print(sourceCmdName + DEVICE_ERROR_CODES.get(response[5:7], ': An unknown error occurred.'))
            return b''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command == 'Freeze':
                regex = self.regex1
            elif command in ['Power']:
                regex = self.regex2
            elif command in ['AspectRatio', 'LampMode', 'PIPInput', 'PIPMode', 'PIPPosition']:
                regex = self.regex3
            elif command == 'LensProfile':
                regex = self.regex10
            else:
                regex = self.regex4

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            if not res:
                print('No response received')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if command == 'DeviceStatus':
                regex = self.regex5
            elif command == 'FilterUsage':
                regex = self.regex6
            elif command in ['LampMode', 'PIPInput', 'PIPMode', 'PIPPosition']:
                regex = self.regex7
            elif command == 'LampUsage':
                regex = self.regex8
            elif command == 'LensProfile':
                regex = self.regex11
            else:
                regex = self.regex9

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
