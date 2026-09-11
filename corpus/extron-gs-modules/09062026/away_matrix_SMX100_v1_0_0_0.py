from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'Freeze': {'Parameters': ['Input'], 'Status': {}},
            'Input': {'Parameters': ['Output', 'Layer'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'Standby': {'Status': {}},
            'Take': {'Status': {}},
            'Volume': {'Parameters': ['Input'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Au([01]),([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Sf([0-589]|1[01]),([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'IN([01]),([23]),([0-69]|1[012])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'wQ([01])\r\n'), self.__MatchStandby, None)
            self.AddMatchString(re.compile(b'AL([0-589]|1[01]),(\d+)\r\n'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'E(1[012])\r\n'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '0',
            'Preview': '1'
        }
        output = qualifier['Output']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if output in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{},{}Au'.format(OutputStates[output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            'Program': '0',
            'Preview': '1'
        }
        output = qualifier['Output']

        if output in OutputStates:
            AudioMuteCmdString = '{},Au'.format(OutputStates[output])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '0': 'Program',
            '1': 'Preview'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetFreeze(self, value, qualifier):

        InputStates = {
            'Analog 1': '0',
            'Analog 2': '1',
            'Analog 3': '2',
            'Analog 4': '3',
            'DVI 1 (Analog)': '4',
            'DVI 1 (Digital)': '8',
            'DVI 2 (Analog)': '5',
            'DVI 2 (Digital)': '9',
            'SDI 1': '10',
            'SDI 2': '11'
        }
        input_ = qualifier['Input']

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if input_ in InputStates and value in ValueStateValues:
            FreezeCmdString = '{},{}Sf'.format(InputStates[input_], ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        InputStates = {
            'Analog 1': '0',
            'Analog 2': '1',
            'Analog 3': '2',
            'Analog 4': '3',
            'DVI 1 (Analog)': '4',
            'DVI 1 (Digital)': '8',
            'DVI 2 (Analog)': '5',
            'DVI 2 (Digital)': '9',
            'SDI 1': '10',
            'SDI 2': '11'
        }
        input_ = qualifier['Input']

        if input_ in InputStates:
            FreezeCmdString = '{},Sf'.format(InputStates[input_])
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        InputStates = {
            '0': 'Analog 1',
            '1': 'Analog 2',
            '2': 'Analog 3',
            '3': 'Analog 4',
            '4': 'DVI 1 (Analog)',
            '8': 'DVI 1 (Digital)',
            '5': 'DVI 2 (Analog)',
            '9': 'DVI 2 (Digital)',
            '10': 'SDI 1',
            '11': 'SDI 2'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': InputStates[match.group(1).decode()]
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, qualifier)

    def SetInput(self, value, qualifier):

        OutputStates = {
            'Program': '0',
            'Preview': '1'
        }
        output = qualifier['Output']

        LayerStates = {
            'Background Live': '2',
            'PIP': '3'
        }
        layer = qualifier['Layer']

        ValueStateValues = {
            'Black': '0',
            'Analog 1': '1',
            'Analog 2': '2',
            'Analog 3': '3',
            'Analog 4': '4',
            'DVI 1 (Analog)': '5',
            'DVI 1 (Digital)': '9',
            'DVI 2 (Analog)': '6',
            'DVI 2 (Digital)': '10',
            'SDI 1': '11',
            'SDI 2': '12'
        }

        if output in OutputStates and layer in LayerStates and value in ValueStateValues:
            InputCmdString = '{},{},{}IN'.format(OutputStates[output], LayerStates[layer], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        OutputStates = {
            'Program': '0',
            'Preview': '1'
        }
        output = qualifier['Output']

        LayerStates = {
            'Background Live': '2',
            'PIP': '3'
        }
        layer = qualifier['Layer']

        if output in OutputStates and layer in LayerStates:
            InputCmdString = '{},{},IN'.format(OutputStates[output], LayerStates[layer])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        OutputStates = {
            '0': 'Program',
            '1': 'Preview'
        }

        LayerStates = {
            '2': 'Background Live',
            '3': 'PIP'
        }

        ValueStateValues = {
            '0': 'Black',
            '1': 'Analog 1',
            '2': 'Analog 2',
            '3': 'Analog 3',
            '4': 'Analog 4',
            '5': 'DVI 1 (Analog)',
            '9': 'DVI 1 (Digital)',
            '6': 'DVI 2 (Analog)',
            '10': 'DVI 2 (Digital)',
            '11': 'SDI 1',
            '12': 'SDI 2'
        }

        qualifier = {
            'Output': OutputStates[match.group(1).decode()],
            'Layer': LayerStates[match.group(2).decode()]
        }

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 4:
            PresetRecallCmdString = '{}Nf1Nt1Nc'.format(int(value) + 2)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            StandbyCmdString = '{}wQ'.format(ValueStateValues[value])
            self.__SetHelper('Standby', StandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def UpdateStandby(self, value, qualifier):

        StandbyCmdString = 'wQ'
        self.__UpdateHelper('Standby', StandbyCmdString, value, qualifier)

    def __MatchStandby(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)

    def SetTake(self, value, qualifier):

        TakeCmdString = '1TK'
        self.__SetHelper('Take', TakeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        InputStates = {
            'Analog 1': '0',
            'Analog 2': '1',
            'Analog 3': '2',
            'Analog 4': '3',
            'DVI 1 (Analog)': '4',
            'DVI 1 (Digital)': '8',
            'DVI 2 (Analog)': '5',
            'DVI 2 (Digital)': '9',
            'SDI 1': '10',
            'SDI 2': '11'
        }
        input_ = qualifier['Input']

        if input_ in InputStates and 0 <= value <= 255:
            VolumeCmdString = '{},{}AL'.format(InputStates[input_], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        InputStates = {
            'Analog 1': '0',
            'Analog 2': '1',
            'Analog 3': '2',
            'Analog 4': '3',
            'DVI 1 (Analog)': '4',
            'DVI 1 (Digital)': '8',
            'DVI 2 (Analog)': '5',
            'DVI 2 (Digital)': '9',
            'SDI 1': '10',
            'SDI 2': '11'
        }
        input_ = qualifier['Input']

        if input_ in InputStates:
            VolumeCmdString = '{},AL'.format(InputStates[input_])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        InputStates = {
            '0': 'Analog 1',
            '1': 'Analog 2',
            '2': 'Analog 3',
            '3': 'Analog 4',
            '4': 'DVI 1 (Analog)',
            '8': 'DVI 1 (Digital)',
            '5': 'DVI 2 (Analog)',
            '9': 'DVI 2 (Digital)',
            '10': 'SDI 1',
            '11': 'SDI 2'
        }

        qualifier = {
            'Input': InputStates[match.group(1).decode()]
        }

        value = int(match.group(2).decode())
        if 0 <= value <= 255:
            self.WriteStatus('Volume', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            standbystatus = self.ReadStatus('Standby', None)
            if standbystatus in ['On', None] and command not in ['Standby']:
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        error_map = {
            '10': 'Invalid command',
            '11': 'Index value error',
            '12': 'Index number error'
        }

        error = match.group(1).decode()
        self.Error(['An error occurred: {}: {}.'.format(error, error_map[error])])

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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

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
                    except BaseException:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}


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