from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
import re
from extronlib.system import Wait, ProgramLog


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
            'AudioMute': {'Status': {}},
            'ButtonResponse': {'Parameters': ['Button'], 'Status': {}},
            'ControlModuleButton': {'Parameters': ['Address', 'Button'], 'Status': {}},
            'ControlModuleLED': {'Parameters': ['Address', 'Button'], 'Status': {}},
            'DigitalIO': {'Status': {}},
            'DigitalIOPortMode': {'Status': {}},
            'DisplayMute': {'Status': {}},
            'DisplayPower': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FrontPanelLED': {'Parameters': ['LED'], 'Status': {}},
            'Input': {'Status': {}},
            'PowerSensor': {'Status': {}},
            'PowerSensorMode': {'Status': {}},
            'Relay': {'Parameters': ['Relay'], 'Status': {}},
            'RoomSelect': {'Parameters': ['Button'], 'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStepStatus': {'Status': {}}
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt(0|1)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Sw(Prs|Rls)\*(001|002|005|006|007|009|010|011|012|013|014)\r'), self.__MatchButtonResponse, None)
            self.AddMatchString(re.compile(b'Lmp(\d{2}|:\d)\*(\d{2})\r'), self.__MatchControlModuleLED, None)
            self.AddMatchString(re.compile(b'Exe(0|3)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Sio1\*(0|1)\r'), self.__MatchDigitalIO, None)
            self.AddMatchString(re.compile(b'Iom1\*(0|1|2|3)\r'), self.__MatchDigitalIOPortMode, None)
            self.AddMatchString(re.compile(b'Sio2\*(0|1)\r'), self.__MatchPowerSensor, None)
            self.AddMatchString(re.compile(b'Iom2\*(0|8)\r'), self.__MatchPowerSensorMode, None)
            self.AddMatchString(re.compile(b'Mut(0|1)\r'), self.__MatchDisplayMute, None)
            self.AddMatchString(re.compile(b'Pwr(0|1|2|3)\r'), self.__MatchDisplayPower, None)
            self.AddMatchString(re.compile(b'Chn0(\d)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Rly(\d{2})\*(1|0)\r'), self.__MatchRelay, None)
            self.AddMatchString(re.compile(b'Vol(\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Vol(\+|-)\r'), self.__MatchVolumeStepStatus, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

    def __MatchLoginAdmin(self, match, tag):
        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):
        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):
        AudioMuteStateValues = {
            'On': '1Z',
            'Off': '0Z',
        }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):
        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def __MatchButtonResponse(self, match, tag):
        ButtonResponseNames = {
            'Prs': 'Press',
            'Rls': 'Release'
        }

        ButtonType = {
            '001': 'Power On',
            '002': 'Power Off',
            '009': 'Input 1',
            '010': 'Input 2',
            '011': 'Input 3',
            '012': 'Input 4',
            '013': 'Input 5',
            '014': 'Input 6',
            '005': 'Room Select 1',
            '006': 'Room Select 2',
            '007': 'Room Select 3'
        }
        value1 = match.group(2).decode()
        value = ButtonResponseNames[match.group(1).decode()]
        if value1 in ButtonType:
            qualifier = {'Button': ButtonType[value1]}
            self.WriteStatus('ButtonResponse', value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetControlModuleButton(self, value, qualifier):
        CMButtonValues = {
            'Execute': '44',
            'Press': '42',
            'Release': '43',
        }

        CMButtonConstraints = {
            'Min': 26,
            'Max': 105,
        }

        AddressConstraints = {
            'Min': 1,
            'Max': 4,
        }

        CMButton = int(qualifier['Button'])
        Address = int(qualifier['Address'])

        if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
            if Address == 1:
                Number = (CMButton + 25)
            elif Address == 2:
                Number = (CMButton + 45)
            elif Address == 3:
                Number = (CMButton + 65)
            elif Address == 4:
                Number = (CMButton + 85)

            if CMButtonConstraints['Min'] <= Number <= CMButtonConstraints['Max']:
                CMButtonCmdString = '{0}*{1}#'.format(Number, CMButtonValues[value])
                self.__SetHelper('ControlModuleButton', CMButtonCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetControlModuleButton')
        else:
            self.Discard('Invalid Command for SetControlModuleButton')

    def SetControlModuleLED(self, value, qualifier):
        LedStatusValues = {
            'Off': '0',
            'Green': '1',
            'Red': '2',
            'Amber': '3',
            'Slowly Blinking Green': '4',
            'Slowly Blinking Red': '5',
            'Slowly Blinking Amber': '6',
            'Fast Blinking Green': '7',
            'Fast Blinking Red': '8',
            'Fast Blinking Amber': '9',
        }

        LedStatusConstraints = {
            'Min': 26,
            'Max': 105,
        }

        AddressConstraints = {
            'Min': 1,
            'Max': 4,
        }

        CMButton = int(qualifier['Button'])
        Address = int(qualifier['Address'])

        if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
            if Address == 1:
                ButtonNumber = (CMButton + 25)
            elif Address == 2:
                ButtonNumber = (CMButton + 45)
            elif Address == 3:
                ButtonNumber = (CMButton + 65)
            elif Address == 4:
                ButtonNumber = (CMButton + 85)

            if LedStatusConstraints['Min'] <= int(ButtonNumber) <= LedStatusConstraints['Max']:
                LedStatusCmdString = '{0}*{1}*51#'.format(LedStatusValues[value], ButtonNumber)
                self.__SetHelper('ControlModuleLED', LedStatusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetControlModuleLED')
        else:
            self.Discard('Invalid Command for SetControlModuleLED')

    def UpdateControlModuleLED(self, value, qualifier):
        CMButton = int(qualifier['Button'])
        Address = int(qualifier['Address'])

        AddressConstraints = {
            'Min': 1,
            'Max': 4,
        }

        ButtonConstraints = {
            'Min': 26,
            'Max': 105,
        }

        if AddressConstraints['Min'] <= Address <= AddressConstraints['Max']:
            if Address == 1:
                ButtonNumber = (CMButton + 25)
            elif Address == 2:
                ButtonNumber = (CMButton + 45)
            elif Address == 3:
                ButtonNumber = (CMButton + 65)
            elif Address == 4:
                ButtonNumber = (CMButton + 85)

            if ButtonConstraints['Min'] <= int(ButtonNumber) <= ButtonConstraints['Max']:
                LedStatusCmdString = '{0}*51#'.format(ButtonNumber)
                self.__UpdateHelper('ControlModuleLED', LedStatusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateControlModuleLED')
        else:
            self.Discard('Invalid Command for UpdateControlModuleLED')

    def __MatchControlModuleLED(self, match, tag):
        LEDnames = {
            '1': 'Display Power On',
            '2': 'Display Power Off',
            '5': 'Room/Function Button 1',
            '6': 'Room/Function Button 2',
            '7': 'Room/Function Button 3',
            '9': 'Input 1',
            '10': 'Input 2',
            '11': 'Input 3',
            '12': 'Input 4',
            '13': 'Input 5',
            '14': 'Input 6',
        }

        LedStatusNames = {
            '0': 'Off',
            '1': 'Green',
            '2': 'Red',
            '3': 'Amber',
            '4': 'Slowly Blinking Green',
            '5': 'Slowly Blinking Red',
            '6': 'Slowly Blinking Amber',
            '7': 'Fast Blinking Green',
            '8': 'Fast Blinking Red',
            '9': 'Fast Blinking Amber',
        }
            
        RangeTest = int(match.group(1).decode().replace(':',''))
        if RangeTest < 24:
            qualifier = {'LED': LEDnames[str(RangeTest)]}
            value = str(int(match.group(2).decode()))
            self.WriteStatus('FrontPanelLED', LedStatusNames[value], qualifier)
        else:
            TestForGreaterThan100 = match.group(1).decode()
            if TestForGreaterThan100[0] == ':':
                ButtNum = int(TestForGreaterThan100[1]) + 100
            else:
                ButtNum = int(TestForGreaterThan100)

            if 26 <= ButtNum <= 45:
                qualifier = {'Address': '1', 'Button': str(ButtNum - 25)}
                value = LedStatusNames[str(int(match.group(2).decode()))]
            elif 46 <= ButtNum <= 65:
                qualifier = {'Address': '2', 'Button': str(ButtNum - 45)}
                value = LedStatusNames[str(int(match.group(2).decode()))]
            elif 66 <= ButtNum <= 85:
                qualifier = {'Address': '3', 'Button': str(ButtNum - 65)}
                value = LedStatusNames[str(int(match.group(2).decode()))]
            elif 86 <= ButtNum <= 105:
                qualifier = {'Address': '4', 'Button': str(ButtNum - 85)}
                value = LedStatusNames[str(int(match.group(2).decode()))]

            self.WriteStatus('ControlModuleLED', value, qualifier)

    def SetDigitalIO(self, value, qualifier):
        DigitalIOValues = {
            'On': '1',
            'Off': '0',
        }

        DigitalIOCmdString = '1*{0}]'.format(DigitalIOValues[value])
        self.__SetHelper('DigitalIO', DigitalIOCmdString, value, qualifier)

    def UpdateDigitalIO(self, value, qualifier):
        DigitalIOCmdString = '1]'
        self.__UpdateHelper('DigitalIO', DigitalIOCmdString, value, qualifier)

    def __MatchDigitalIO(self, match, tag):
        DigitalIONames = {
            '0': 'Off',
            '1': 'On'
        }
        value = DigitalIONames[match.group(1).decode()]
        self.WriteStatus('DigitalIO', value, None)

    def SetDigitalIOPortMode(self, value, qualifier):
        DigitalIOPortMode = {
            'Input': '0',
            'Output': '1',
            'Input W/ Pull-Up': '2',
            'Output W/ Pull-Up': '3'
        }

        DigitalIOPortModeCmdString = '1*{0}['.format(DigitalIOPortMode[value])
        self.__SetHelper('DigitalIOPortMode', DigitalIOPortModeCmdString, value, qualifier)

    def UpdateDigitalIOPortMode(self, value, qualifier):
        DigitalIOPortModeCmdString = '1['
        self.__UpdateHelper('DigitalIOPortMode', DigitalIOPortModeCmdString, value, qualifier)

    def __MatchDigitalIOPortMode(self, match, tag):
        DigitalIOPortModeNames = {
            '0': 'Input',
            '1': 'Output',
            '2': 'Input W/ Pull-Up',
            '3': 'Output W/ Pull-Up'
        }
        value = DigitalIOPortModeNames[match.group(1).decode()]
        self.WriteStatus('DigitalIOPortMode', value, None)

    def SetDisplayMute(self, value, qualifier):
        DisplayMuteStateValues = {
            'On': '1M',
            'Off': '0M',
        }
        DisplayMuteCmdString = DisplayMuteStateValues[value]
        self.__SetHelper('DisplayMute', DisplayMuteCmdString, value, qualifier)

    def UpdateDisplayMute(self, value, qualifier):
        DisplayMuteCmdString = 'M'
        self.__UpdateHelper('DisplayMute', DisplayMuteCmdString, value, qualifier)

    def __MatchDisplayMute(self, match, tag):
        DisplayMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = DisplayMuteStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayMute', value, None)

    def SetDisplayPower(self, value, qualifier):
        DisplayPowerStateValues = {
            'On': '1P',
            'Off': '0P',
        }
        DisplayPowerCmdString = DisplayPowerStateValues[value]
        self.__SetHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)

    def UpdateDisplayPower(self, value, qualifier):
        DisplayPowerCmdString = 'P'
        self.__UpdateHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)

    def __MatchDisplayPower(self, match, tag):
        DisplayPowerStateNames = {
            '0': 'Off',
            '1': 'On',
            '2': 'Powering Down',
            '3': 'Powering Up',
        }

        value = DisplayPowerStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayPower', value, None)

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeStateValues = {
            'On': '3X',
            'Off': '0X'
        }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):
        ExecutiveModeStateNames = {
            '3': 'On',
            '0': 'Off'
        }
        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFrontPanelLED(self, value, qualifier):
        LEDnames = {
            'Display Power On': '1',
            'Display Power Off': '2',
            'Room/Function Button 1': '5',
            'Room/Function Button 2': '6',
            'Room/Function Button 3': '7',
            'Input 1': '9',
            'Input 2': '10',
            'Input 3': '11',
            'Input 4': '12',
            'Input 5': '13',
            'Input 6': '14',

        }

        FrontPanelLEDValues = {
            'Off': '0',
            'Green': '1',
            'Red': '2',
            'Amber': '3',
            'Slowly Blinking Green': '4',
            'Slowly Blinking Red': '5',
            'Slowly Blinking Amber': '6',
            'Fast Blinking Green': '7',
            'Fast Blinking Red': '8',
            'Fast Blinking Amber': '9',
        }

        LED = qualifier['LED']

        LedStatusCmdString = '{0}*{1}*51#'.format(FrontPanelLEDValues[value], LEDnames[LED])
        self.__SetHelper('FrontPanelLED', LedStatusCmdString, value, qualifier)

    def UpdateFrontPanelLED(self, value, qualifier):
        LEDnames = {
            'Display Power On': '1',
            'Display Power Off': '2',
            'Room/Function Button 1': '5',
            'Room/Function Button 2': '6',
            'Room/Function Button 3': '7',
            'Input 1': '9',
            'Input 2': '10',
            'Input 3': '11',
            'Input 4': '12',
            'Input 5': '13',
            'Input 6': '14',

        }

        LED = qualifier['LED']
        LedStatusCmdString = '{0}*51#'.format(LEDnames[LED])
        self.__UpdateHelper('FrontPanelLED', LedStatusCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        InputStateValues = {
            '1': '1!',
            '2': '2!',
            '3': '3!',
            '4': '4!',
            '5': '5!',
            '6': '6!',
        }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        InputCmdString = 'I'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
        InputStateNames = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
        }
        value = InputStateNames[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdatePowerSensor(self, value, qualifier):
        PowerSensorCmdString = '2]'
        self.__UpdateHelper('PowerSensor', PowerSensorCmdString, value, qualifier)

    def __MatchPowerSensor(self, match, tag):
        PowerSensorNames = {
            '0': 'Off',
            '1': 'On'
        }
        value = PowerSensorNames[match.group(1).decode()]
        self.WriteStatus('PowerSensor', value, None)

    def SetPowerSensorMode(self, value, qualifier):
        PowerSensorMode = {
            'Input': '0',
            'Power Sensor': '8'
        }

        PowerSensorModeCmdString = '2*{0}['.format(PowerSensorMode[value])
        self.__SetHelper('PowerSensorMode', PowerSensorModeCmdString, value, qualifier)

    def UpdatePowerSensorMode(self, value, qualifier):
        PowerSensorModeCmdString = '2['
        self.__UpdateHelper('PowerSensorMode', PowerSensorModeCmdString, value, qualifier)

    def __MatchPowerSensorMode(self, match, tag):
        PowerSensorMode = {
            '0': 'Input',
            '8': 'Power Sensor'
        }
        value = PowerSensorMode[match.group(1).decode()]
        self.WriteStatus('PowerSensorMode', value, None)

    def SetRelay(self, value, qualifier):
        RelayValues = {
            'Off': '0',
            'On': '1',
        }
        RelayConstraints = {
            'Min': 1,
            'Max': 6
        }
        RelaySelect = qualifier['Relay']
        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max']:
            RelayCmdString = '{0}*{1}O'.format(RelaySelect, RelayValues[value])
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):
        RelayConstraints = {
            'Min': 1,
            'Max': 6
        }
        RelaySelect = qualifier['Relay']
        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max']:
            RelayCmdString = '{0}O'.format(RelaySelect)
            self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRelay')

    def __MatchRelay(self, match, tag):
        RelayNames = {
            '0': 'Off',
            '1': 'On'
        }
        qualifier = {'Relay': str(int(match.group(1).decode()))}
        value = RelayNames[match.group(2).decode()]
        self.WriteStatus('Relay', value, qualifier)

    def SetRoomSelect(self, value, qualifier):
        RoomSelectValues = {
            'Execute': '44',
            'Press': '42',
            'Release': '43',
        }
        RoomSelectConstraints = {
            'Min': 5,
            'Max': 7,
        }
        RoomSelect = int(qualifier['Button']) + 4
        if RoomSelectConstraints['Min'] <= RoomSelect <= RoomSelectConstraints['Max']:
            RoomSelectCmdString = '{0}*{1}#'.format(RoomSelect, RoomSelectValues[value])
            self.__SetHelper('RoomSelect', RoomSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRoomSelect')

    def SetVolume(self, value, qualifier):
        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __MatchVolumeStepStatus(self, match, tag):
        value = match.group(1).decode()
        if value == '+':
            self.WriteStatus('VolumeStepStatus', 'Volume Up', None)
        elif value == '-':
            self.WriteStatus('VolumeStepStatus', 'Volume Down', None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' +  command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchErrors(self, match, qualifier):
        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
        self.VerboseDisabled = True

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
