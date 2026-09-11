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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputStatus': {'Parameters': ['Input'], 'Status': {}},
            'AllRelays': {'Status': {}},
            'Relay': {'Parameters': ['Relay'], 'Status': {}},
            'RelayPulse': {'Parameters': ['Relay'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
       
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Cpn0?([1-4]) Sio([0-1])\r\n'), self.__MatchInputStatus, None)
            self.AddMatchString(compile(b'Cpn0?([1-8]) Rly([0-1])\r\n'), self.__MatchRelay, None)
            self.AddMatchString(compile(rb'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)            
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
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

    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()

        self.VerboseDisabled = False

    def UpdateInputStatus(self, value, qualifier):

        InputConstraints = {
            'Min': 1,
            'Max': 4
        }

        InputSelect = qualifier['Input']
        if InputConstraints['Min'] <= int(InputSelect) <= InputConstraints['Max']:
            InputStatusCmdString = '{0}]'.format(InputSelect)
            self.__UpdateHelper('InputStatus', InputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputStatus')

    def __MatchInputStatus(self, match, tag):

        InputStatusNames = {
            '0': 'Off',
            '1': 'On'
        }

        qualifier = {'Input': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('InputStatus', InputStatusNames[value], qualifier)

    def UpdateAllRelays(self, value, qualifier):

        AllRelaysCmdString = '1o2o3o4o5o6o7o8o'

        self.__UpdateHelper('AllRelays', AllRelaysCmdString, value, qualifier)

    def SetRelay(self, value, qualifier):

        RelayValues = {
            'Open': '0',
            'Close': '1',
        }

        RelayConstraints = {
            'Min': 1,
            'Max': 8
        }

        RelaySelect = qualifier['Relay']
        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max']:
            RelayCmdString = '{0}*{1}O'.format(RelaySelect, RelayValues[value])
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def __MatchRelay(self, match, tag):

        RelayNames = {
            '0': 'Open',
            '1': 'Close'
        }

        qualifier = {'Relay': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('Relay', RelayNames[value], qualifier)

    def SetRelayPulse(self, value, qualifier):

        RelayPortConstraints = {
            'Min': 1,
            'Max': 8
        }
        RelayPulseConstraints = {
            'Min': 0.02,
            'Max': 1310.7
        }
        RelaySelect = qualifier['Relay']
        if RelayPulseConstraints['Min'] <= value <= RelayPulseConstraints['Max'] and RelayPortConstraints['Min'] <= int(RelaySelect) <= RelayPortConstraints['Max']:
            RelayPulseTime = int(value / 0.02)
            RelayPulseCmdString = '{0}*3*{1}O'.format(RelaySelect, RelayPulseTime)
            self.__SetHelper('RelayPulse', RelayPulseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelayPulse')

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
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
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
            '10': 'Invalid command',
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
            '31': 'Attempt to break port pass-through when it has not been set'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode().strip()])

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
