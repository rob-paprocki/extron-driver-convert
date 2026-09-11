from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'Macro': {'Status': {}},
            'MicGain': {'Parameters': ['Mic'], 'Status': {}},
            'MicMute': {'Parameters': ['Mic'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'Preset': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#\d+ TE(1|0)\r\n'), self.__MatchHook, None)
            self.AddMatchString(re.compile(b'#\d+ GAIN ([1-4]|[A-D]) I ([\-0-9]{1,4})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'#\d+ MUTE ([1-4]|[A-D]) I (1|0)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'#\d+ GAIN ([1-4]) M ([\-0-9]{1,4})\r\n'), self.__MatchMicGain, None)
            self.AddMatchString(re.compile(b'#\d+ MUTE ([1-4]) M (1|0)\r\n'), self.__MatchMicMute, None)
            self.AddMatchString(re.compile(b'#\d+ GAIN ([1-4]|[A-D]) O ([\-0-9]{1,4})\r\n'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'#\d+ MUTE ([1-4]|[A-D]) O (1|0)\r\n'), self.__MatchOutputMute, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'All':
            self._DeviceID = '*'
        elif 0 <= int(value) <= 7:
            self._DeviceID = int(value)
        else:
            print('DeviceID Parameter should be a number between 0 and 7 or All, you sent {}'.format(value))

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': 'AA 1\r\n',
            'Off': 'AA 0\r\n'
        }

        AutoAnswerCmdString = '#3{0} {1}'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789ABCD#*,':
            CommandString = '#3{0} DIAL {1}\r\n'.format(self._DeviceID, value)
            self.__SetHelper('DTMF', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetDTMF')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Off': 'TE 1\r\n',
            'On': 'TE 0\r\n',
            'Flash': 'HOOK\r\n',
        }

        if value in ['On', 'Off', 'Flash']:
            HookCmdString = '#3{0} {1}'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Hook', HookCmdString, value, qualifier)
        elif value == 'Dial':
            number = qualifier['Number']
            if number:
                self.__SetHelper('Hook', '#3{0} DIAL {1}\r\n'.format(self._DeviceID, number), value, qualifier)
            else:
                print('Invalid Command for SetHook')
        else:
            print('Invalid Command for SetHook')

    def UpdateHook(self, value, qualifier):

        HookCmdString = '#3{0} TE\r\n'.format(self._DeviceID)
        self.__UpdateHelper('Hook', HookCmdString, value, qualifier)

    def __MatchHook(self, match, tag):

        ValueStateValues = {
            '1': 'Off',
            '0': 'On',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Hook', value, None)

    def SetInputGain(self, value, qualifier):

        Input = qualifier['Input']

        ValueConstraints = {
            'Min': -20,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in '1234ABCD':
            InputGainCmdString = '#3{0} GAIN {1} I {2} A\r\n'.format(self._DeviceID, Input, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        Input = qualifier['Input']
        if Input in '1234ABCD':
            InputGainCmdString = '#3{0} GAIN {1} I\r\n'.format(self._DeviceID, Input)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        qualifier = {'Input': match.group(1).decode()}
        value = int(match.group(2))
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        Input = qualifier['Input']

        ValueStateValues = {
            'On': '1\r\n',
            'Off': '0\r\n'
        }

        if Input in '1234ABCD':
            InputMuteCmdString = '#3{0} MUTE {1} I {2}'.format(self._DeviceID, Input, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        Input = qualifier['Input']
        if Input in '1234ABCD':
            InputMuteCmdString = '#3{0} MUTE {1} I\r\n'.format(self._DeviceID, Input)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Input': match.group(1).decode()}

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetMacro(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25'
        }

        MacroCmdString = '#3{0} MACRO {1}\r\n'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Macro', MacroCmdString, value, qualifier)

    def SetMicGain(self, value, qualifier):

        Mic = qualifier['Mic']

        ValueConstraints = {
            'Min': -20,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(Mic) <= 4:
            MicGainCmdString = '#3{0} GAIN {1} M {2} A\r\n'.format(self._DeviceID, Mic, value)
            self.__SetHelper('MicGain', MicGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        Mic = qualifier['Mic']
        if 1 <= int(Mic) <= 4:
            MicGainCmdString = '#3{0} GAIN {1} M\r\n'.format(self._DeviceID, Mic)
            self.__UpdateHelper('MicGain', MicGainCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMicGain')

    def __MatchMicGain(self, match, tag):

        qualifier = {'Mic': match.group(1).decode()}
        value = int(match.group(2))
        self.WriteStatus('MicGain', value, qualifier)

    def SetMicMute(self, value, qualifier):

        Mic = qualifier['Mic']

        ValueStateValues = {
            'On': '1\r\n',
            'Off': '0\r\n',
        }

        if 1 <= int(Mic) <= 4:
            MicMuteCmdString = '#3{0} MUTE {1} M {2}'.format(self._DeviceID, Mic, ValueStateValues[value])
            self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        Mic = qualifier['Mic']
        if 1 <= int(Mic) <= 4:
            MicMuteCmdString = '#3{0} MUTE {1} M\r\n'.format(self._DeviceID, Mic)
            self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMicMute')

    def __MatchMicMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = {'Mic': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicMute', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        Output = qualifier['Output']

        ValueConstraints = {
            'Min': -20,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Output in '1234ABCD':
            OutputGainCmdString = '#3{0} GAIN {1} O {2} A\r\n'.format(self._DeviceID, Output, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if Output in '1234ABCD':
            OutputGainCmdString = '#3{0} GAIN {1} O\r\n'.format(self._DeviceID, Output)
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Output': match.group(1).decode()}
        value = int(match.group(2))
        self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        Output = qualifier['Output']

        ValueStateValues = {
            'On': '1\r\n',
            'Off': '0\r\n'
        }

        if Output in '1234ABCD':
            OutputMuteCmdString = '#3{0} MUTE {1} O {2}'.format(self._DeviceID, Output, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        Output = qualifier['Output']

        if Output in '1234ABCD':
            OutputMuteCmdString = '#3{0} MUTE {1} O\r\n'.format(self._DeviceID, Output)
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Output': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        PresetCmdString = '#3{0} PRESET {1}\r\n'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        self.Send(commandstring)

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
