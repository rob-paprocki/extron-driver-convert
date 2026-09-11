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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputMode': {'Parameters': ['Channel'], 'Status': {}},
            'InputStatus': {'Parameters': ['Channel'], 'Status': {}},
            'Output': {'Parameters': ['Channel', 'Duration'], 'Status': {}},
            'OutputStatus': {'Parameters': ['Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'>FN,MODE,([1-8]),(0|1|2|3|4)\n\r'), self.__MatchInputMode, None)
            self.AddMatchString(re.compile(b'(?:>FN,IN,(ON|OFF),[1-8]\n\r){8}'), self.__MatchInputStatus, None)
            self.AddMatchString(re.compile(b'(?:>FN,OUT,(ON|OFF),[1-8]\n\r){8}'), self.__MatchOutputStatus, None)

    def SetInputMode(self, value, qualifier):

        ChannelStates = {
            'All': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            'Independent': '0',
            'Toggle': '1',
            'Follow': '2',
            'Monostable': '3',
            'Switch': '4'
        }

        channel = qualifier['Channel']
        if channel in ['All', '1', '2', '3', '4', '5', '6', '7', '8']:
            InputModeCmdString = 'FN,MODE,{0},{1}\r'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('InputMode', InputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMode')

    def UpdateInputMode(self, value, qualifier):

        channel = qualifier['Channel']
        if channel in ['1', '2', '3', '4', '5', '6', '7', '8']:
            InputModeCmdString = 'FN,GETMODE,{0}\r'.format(channel)
            self.__UpdateHelper('InputMode', InputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMode')

    def __MatchInputMode(self, match, tag):

        ValueStateValues = {
            '0': 'Independent',
            '1': 'Toggle',
            '2': 'Follow',
            '3': 'Monostable',
            '4': 'Switch'
        }

        qualifier = {}
        qualifier['Channel'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMode', value, qualifier)

    def UpdateInputStatus(self, value, qualifier):
        InputStatusCmdString = 'FN,SRI\r'
        self.__UpdateHelper('InputStatus', InputStatusCmdString, value, qualifier)

    def __MatchInputStatus(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        val_list = re.findall('IN,(ON|OFF),([1-8])', match.group(0).decode())
        for i in range(0, len(val_list)):
            self.WriteStatus('InputStatus', ValueStateValues[val_list[i][0]], {'Channel': val_list[i][1]})

    def SetOutput(self, value, qualifier):

        ChannelStates = {
            'All': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        DurationConstraints = {
            'Min': 0,
            'Max': 65536
        }

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        channel = qualifier['Channel']
        duration = qualifier['Duration']
        if channel in ['All', '1', '2', '3', '4', '5', '6', '7', '8'] and 0 <= duration <= 65536:
            if duration != 0:
                OutputCmdString = 'FN,MON,{0},{1}\r'.format(ChannelStates[channel], duration)
            else:
                OutputCmdString = 'FN,{0},{1}\r'.format(ValueStateValues[value], ChannelStates[channel])
            self.__SetHelper('Output', OutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutput')

    def UpdateOutputStatus(self, value, qualifier):

        CmdString = 'FN,SRE\r'
        self.__UpdateHelper('OutputStatus', CmdString, value, qualifier)

    def __MatchOutputStatus(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        val_list = re.findall('OUT,(ON|OFF),([1-8])', match.group(0).decode())
        for i in range(0, len(val_list)):
            self.WriteStatus('OutputStatus', ValueStateValues[val_list[i][0]], {'Channel': val_list[i][1]})

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
