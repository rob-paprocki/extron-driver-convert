from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait
from struct import pack
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'NP-P502HL': self.nec_1_1898_L,
            'NP-P502WL': self.nec_1_1898_L,
            'NP-P502HG': self.nec_1_1898_HG,
            'NP-P502HL-2': self.nec_1_1898_L,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'CommunicationStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FilterUsage': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LampMode': {'Status': {}},
            'LampUsage': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeL': {'Status': {}},
        }

        self.isConnected = 1

        self.warmingup_wait = Wait(30, self.warmingup)
        self.warmingup_wait.Cancel()

        self.coolingdown_wait = Wait(60, self.coolingdown)
        self.coolingdown_wait.Cancel()

        if self.Unidirectional == 'False':
            self.regex1 = re.compile(b'([\xA1][\x00-\xFF]{7})|([\x21][\x00-\xFF]{6})')
            self.regex2 = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{5})')
            self.regex3 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')
            self.regex4 = re.compile(b'([\xA2][\x00-\xFF]{7})|([\x22][\x00-\xFF]{6})')
            self.regexVol = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{18})')
            self.regex5 = re.compile(b'([\xA0][\x00-\xFF]{7})|([\x20][\x00-\xFF]{17})')
            self.regex6 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{13})')
            self.regex7 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{7})')
            self.regex8 = re.compile(b'([\xA3][\x00-\xFF]{7})|([\x23][\x00-\xFF]{11})')
            self.regex9 = re.compile(b'([\xA3|\xA0][\x00-\xFF]{7})|([\x20|\x23][\x00-\xFF]{21})')
            self.SetRegex = {
                'Freeze': self.regex1,
                'Power': self.regex2,
                'AudioMute': self.regex2,
                'VideoMute': self.regex2,
                'Volume': self.regex3,
                'AspectRatio': self.regex3,
                'LampMode': self.regex3
            }
            self.UpdateRegex = {
                'DeviceStatus': self.regex5,
                'FilterUsage': self.regex6,
                'LampMode': self.regex7,
                'LampUsage': self.regex8,
                'Volume': self.regexVol
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = self.AspectValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x12\x00\x00\x00\x14',
            'Off': b'\x02\x13\x00\x00\x00\x15'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x02\x0F\x00\x00\x02\x05\x00\x18'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            b'\x00\x00\x00\x00': 'Normal',
            b'\x01\x00\x00\x00': 'Cover Error',
            b'\x02\x00\x00\x00': 'Temp Error (Bi-metallic strip)',
            b'\x08\x00\x00\x00': 'Fan Error',
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
            b'\x00\x00\x00\x08': 'Foreign Matter Sensor Error',
            b'\x00\x00\x00\x20': 'Ballast Communication Error',
            b'\x00\x00\x00\x40': 'Iris Calibration Error',
            b'\x00\x00\x00\x80': 'Lens not properly installed'
        }
        ExtendedStateValues = {
            0x01: 'Portrait cover side is up',
            0x02: 'Interlock switch is open',
            0x04: 'System Error (Slave CPU)',
            0x08: 'System Error (Formatter)'
        }

        DeviceStatusCmdString = b'\x00\x88\x00\x00\x00\x88'
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            try:
                if res[13] != 0x00 and ValueStateValues.get(res[5:9]) != 'Normal':
                    value = 'Multiple Errors'
                elif res[13] != 0x00:
                    value = ExtendedStateValues[res[13]]
                else:
                    value = ValueStateValues.get(res[5:9], 'Multiple Errors')
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateFilterUsage(self, value, qualifier):

        FilterUsageCmdString = b'\x03\x95\x00\x00\x00\x98'
        res = self.__UpdateHelper('FilterUsage', FilterUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(((res[8] << 24) + (res[7] << 16) + (res[6] << 8) + res[5]) / 3600)
                self.WriteStatus('FilterUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Filter Usage: Invalid/unexpected response'])

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
            'HDMI 1': b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'HDMI 2': b'\x02\x03\x00\x00\x02\x01\xA2\xAA',
            'Computer': b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'Video': b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'HDBaseT': b'\x02\x03\x00\x00\x02\x01\xBF\xC7',
            'APPS': b'\x02\x03\x00\x00\x02\x01\x23\x2B'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetLampMode(self, value, qualifier):

        ValueStateValues = {
            'Eco 1': b'\x03\xB1\x00\x00\x02\x07\x01\xBE',
            'Eco 2': b'\x03\xB1\x00\x00\x02\x07\x02\xBF',
            'Off': b'\x03\xB1\x00\x00\x02\x07\x00\xBD'
        }

        LampModeCmdString = ValueStateValues[value]
        self.__SetHelper('LampMode', LampModeCmdString, value, qualifier)

    def UpdateLampMode(self, value, qualifier):

        ValueStateValues = {
            b'\x01': 'Eco 1',
            b'\x02': 'Eco 2',
            b'\x00': 'Off'
        }

        LampModeCmdString = b'\x03\xB0\x00\x00\x01\x07\xBB'
        res = self.__UpdateHelper('LampMode', LampModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[6:7]]
                self.WriteStatus('LampMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Lamp Mode: Invalid/unexpected response'])

    def UpdateLampUsage(self, value, qualifier):

        LampUsageCmdString = b'\x03\x96\x00\x00\x02\x00\x01\x9C'
        res = self.__UpdateHelper('LampUsage', LampUsageCmdString, value, qualifier)
        if res:
            try:
                value = int(((res[10] << 24) + (res[9] << 16) + (res[8] << 8) + res[7]) / 3600)
                self.WriteStatus('LampUsage', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Lamp Usage: Invalid/unexpected response'])

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

    def SetOnScreenDisplay(self, value, qualifier):

        OnScreenDisplayState = {
            'On': b'\x02\x15\x00\x00\x00\x17',
            'Off': b'\x02\x14\x00\x00\x00\x16'
        }

        OnScreenDisplayCmdString = OnScreenDisplayState[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def UpdateOnScreenDisplay(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x00\x00\x00\x00\x02',
            'Off': b'\x02\x01\x00\x00\x00\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def warmingup(self):
        self.isConnected = 2

    def coolingdown(self):
        self.isConnected = 1

    def UpdatePower(self, value, qualifier):

        PowerState = {
            0x04: 'On',
            0x00: 'Off',
            0x06: 'Off',
            0x0F: 'Off',
            0x10: 'Off',
            0x01: 'Warming Up',
            0x02: 'Warming Up',
            0x03: 'Warming Up',
            0x09: 'Warming Up',
            0x05: 'Cooling Down'
        }

        InputState = {
            b'\x01\x01': 'Computer',
            b'\x01\x02': 'Video',
            b'\x01\x21': 'HDMI 1',
            b'\x02\x21': 'HDMI 2',
            b'\x01\x27': 'HDBaseT',
            b'\x05\x07': 'APPS'
        }

        VideoMuteState = {
            0x01: 'On',
            0x00: 'Off'
        }

        AudioMuteState = {
            0x01: 'On',
            0x00: 'Off'
        }

        FreezeState = {
            0x01: 'On',
            0x00: 'Off'
        }

        OSDState = {
            0x00: 'On',
            0x01: 'Off'
        }

        PowerCmdString = b'\x00\xBF\x00\x00\x01\x02\xC2'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerState[res[6]]
                if self.ConnectionType == 'Ethernet':
                    if PowerValue == 'Warming Up':
                        self.isConnected = 3
                        self.warmingup_wait.Restart()
                    if PowerValue == 'Cooling Down':
                        self.isConnected = 4
                        self.coolingdown_wait.Restart()
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/Unexpected Response'])

            try:
                InputValue = InputState[res[8:10]]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

            try:
                VideoMuteValue = VideoMuteState[res[11]]
                self.WriteStatus('VideoMute', VideoMuteValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Video Mute: Invalid/Unexpected Response'])

            try:
                AudioMuteValue = AudioMuteState[res[12]]
                self.WriteStatus('AudioMute', AudioMuteValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected Response'])

            try:
                OSDValue = OSDState[res[13]]
                self.WriteStatus('OnScreenDisplay', OSDValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['On Screen Display: Invalid/Unexpected Response'])

            try:
                FreezeValue = FreezeState[res[14]]
                self.WriteStatus('Freeze', FreezeValue, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/Unexpected Response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x10\x00\x00\x00\x12',
            'Off': b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 31
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Checksum = 0x1D + value
            VolumeCmdString = pack('>11B', 0x03, 0x10, 0x00, 0x00, 0x05, 0x05, 0x00, 0x00, value, 0x00, Checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        
        VolumeLCmdString = b'\x03\x04\x00\x00\x03\x05\x00\x00\x0F'
        res = self.__UpdateHelper('Volume', VolumeLCmdString, value, qualifier)
        if res:
            try:
                value = int(res[12])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            b'\x00\x00': 'Command not recognized.',
            b'\x00\x01': 'Unsupported Command.',
            b'\x01\x00': 'Invalid values specified.',
            b'\x01\x01': 'Specified input terminal is invalid.',
            b'\x01\x02': 'Selected language is invalid.',
            b'\x02\x00': 'Memory allocation error.',
            b'\x02\x02': 'Memory in use.',
            b'\x02\x03': 'Specified value cannot be set.',
            b'\x02\x04': 'Forced onscreen mute on.',
            b'\x02\x06': 'Viewer Error.',
            b'\x02\x07': 'No Signal.',
            b'\x02\x08': 'Displaying a test pattern or Filer.',
            b'\x02\x09': 'No PC Card is inserted.',
            b'\x02\x0A': 'Memory Operation Failed.',
            b'\x02\x0C': 'An entry list is Displayed.',
            b'\x02\x0D': 'Command cannot be accepted because Power is Off.',
            b'\x02\x0E': 'Command Execution Failed.',
            b'\x02\x0F': 'No authority necessary for the operation .',
            b'\x03\x00': 'Specified gain number is incorrect.',
            b'\x03\x01': 'Specified gain is invalid.',
            b'\x03\x02': 'Adjustment failed.'
        }
        if response[0] in [0xA3, 0xA2, 0xA1, 0xA0] and response[5:7] in DEVICE_ERROR_CODES:
            if response[5:7] in DEVICE_ERROR_CODES:
                errorString = sourceCmdName + ', Error : ' + DEVICE_ERROR_CODES[response[5:7]]
                self.Error([errorString])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if self.isConnected == 1:
                self.SendAndWait(b'\x00\xBF\x00\x00\x01\x02\xC2', 3.0)
                self.isConnected = 2
                self.__SetHelper(command, commandstring, value, qualifier)
            elif self.isConnected == 3:
                self.Error(['Device is warming up and not yet ready.'])
            elif self.isConnected == 4:
                self.Error(['Device is cooling down and not yet ready.'])
            else:
                if command in self.SetRegex:
                    regex = self.SetRegex[command]
                else:
                    regex = self.regex4
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res)
                    if command == 'Power' and value == 'Off' and res:
                        self.isConnected = 1

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.isConnected == 1:
                self.SendAndWait(b'\x00\xBF\x00\x00\x01\x02\xC2', 3.0)
                self.isConnected = 2
                self.__UpdateHelper(command, commandstring, value, qualifier)
            elif self.isConnected == 3:
                self.Error(['Device is warming up and not yet ready'])
            elif self.isConnected == 4:
                self.Error(['Device is cooling down and not yet ready.'])
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                if self.ConnectionType == 'Ethernet' and self.isConnected == 1:
                    self.SendAndWait(b'\x00\xBF\x00\x00\x01\x02\xC2', 3.0)
                    self.isConnected = 2
                else:
                    try:
                        if command in self.UpdateRegex:
                            regex = self.UpdateRegex[command]
                        else:
                            regex = self.regex9

                        res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
                        if not res:
                            if self.ConnectionType == 'Ethernet':
                                self.WriteStatus('CommunicationStatus', 'No Response', None)
                            return ''
                        else:
                            if self.ConnectionType == 'Ethernet':
                                self.WriteStatus('CommunicationStatus', 'Responding', None)
                            return self.__CheckResponseForErrors(command, res)
                    except(BrokenPipeError, ConnectionResetError):
                        self.Error(['Device is not yet ready'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.isConnected = 1

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.isConnected = 0

    def nec_1_1898_HG(self):
        self.AspectValues = {
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            '5:4': b'\x03\x10\x00\x00\x05\x18\x00\x00\x08\x00\x38',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

    def nec_1_1898_L(self):
        self.AspectValues = {
            '4:3': b'\x03\x10\x00\x00\x05\x18\x00\x00\x04\x00\x34',
            'Letterbox': b'\x03\x10\x00\x00\x05\x18\x00\x00\x07\x00\x37',
            '15:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x05\x00\x35',
            '16:9': b'\x03\x10\x00\x00\x05\x18\x00\x00\x02\x00\x32',
            '16:10': b'\x03\x10\x00\x00\x05\x18\x00\x00\x06\x00\x36',
            'Auto': b'\x03\x10\x00\x00\x05\x18\x00\x00\x00\x00\x30',
            'Native': b'\x03\x10\x00\x00\x05\x18\x00\x00\x03\x00\x33'
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)


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
