from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'Button': {'Status': {}},
            'Channel6InputSelect': {'Status': {}},
            'ChannelSelect': {'Parameters': ['Target'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'MemoryRecall': {'Status': {}},
            'OutputBusAssign': {'Parameters': ['Connector'], 'Status': {}},
            'TransitionEffect': {'Status': {}},
            'TransitionTime': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\x02VER:V-60HD,(.*?);'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\x02ERR:([045]);'), self.__MatchError, None)

    def SetButton(self, value, qualifier):

        ValueStateValues = {
            'Cut': 'CUT',
            'Auto': 'ATO',
            'PinP 1': 'P1S',
            'PinP 2': 'P2S',
            'Split': 'SPT',
            'DSK': 'DSK',
            'DSK PVW': 'DVW',
            'DSK Auto Mixing': 'ATM',
            'DSK Output Fade': 'FDE',
        }

        if value in ValueStateValues:
            ButtonCmdString = '\x02{};'.format(ValueStateValues[value])
            self.__SetHelper('Button', ButtonCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButton')

    def SetChannel6InputSelect(self, value, qualifier):

        ValueStateValues = {
            'HDMI': '0',
            'RGB/COMPONENT': '1',
        }

        if value in ValueStateValues:
            Channel6InputSelectCmdString = '\x02IPS:{};'.format(ValueStateValues[value])
            self.__SetHelper('Channel6InputSelect', Channel6InputSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel6InputSelect')

    def SetChannelSelect(self, value, qualifier):

        TargetStates = {
            'Local': 'PGM',
            'Preset': 'PST',
            'AUX': 'AUX',
        }

        ValueStateValues = {
            'SDI In 1': '0',
            'SDI In 2': '1',
            'SDI In 3': '2',
            'SDI In 4': '3',
            'HDMI In 5': '4',
            'HDMI/RGB In 6': '5',
            'STILL/BKG In 7': '6',
            'STILL/BKG In 8': '7',
        }

        target = qualifier['Target']
        if value in value and target in TargetStates:
            ChannelSelectCmdString = '\x02{}:{};'.format(TargetStates[target], ValueStateValues[value])
            self.__SetHelper('ChannelSelect', ChannelSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelSelect')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = '\x02VER;'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetMemoryRecall(self, value, qualifier):

        ValueStateValues = tuple(str(cnt) for cnt in range(1, 9))

        if value in ValueStateValues:
            MemoryRecallCmdString = '\x02MEM:{};'.format(int(value) - 1)
            self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMemoryRecall')

    def SetOutputBusAssign(self, value, qualifier):

        ConnectorStates = {
            'SDI OUT 1': 'OS1',
            'SDI OUT 2': 'OS2',
            'HDMI OUT 1': 'OH1',
            'HDMI OUT 2': 'OH2',
        }

        ValueStateValues = {
            'PGM': '0',
            'PVW': '1',
            'AUX': '2',
        }

        connector = qualifier['Connector']
        if value in ValueStateValues and connector in ConnectorStates:
            OutputBusAssignCmdString = '\x02{}:{};'.format(ConnectorStates[connector], ValueStateValues[value])
            self.__SetHelper('OutputBusAssign', OutputBusAssignCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputBusAssign')

    def SetTransitionEffect(self, value, qualifier):

        ValueStateValues = {
            'Mix': '0',
            'Wipe 1': '1',
            'Wipe 2': '2',
        }

        if value in ValueStateValues:
            TransitionEffectCmdString = '\x02TRS:{};'.format(ValueStateValues[value])
            self.__SetHelper('TransitionEffect', TransitionEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionEffect')

    def SetTransitionTime(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 4,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TransitionTimeCmdString = '\x02TIM:{};'.format(int(value * 10))
            self.__SetHelper('TransitionTime', TransitionTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransitionTime')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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

        error = {
            '0': 'Syntax Error: The received command contains an error.',
            '4': 'Invalid: This has no effect because it is controlled by another setting.',
            '5': 'Out of Range Error: An argument of the received command is out of range.'
        }

        value = match.group(1).decode()
        self.Error([error[value]])

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
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='SW', CharDelay=0, Mode='RS232', Model=None):
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