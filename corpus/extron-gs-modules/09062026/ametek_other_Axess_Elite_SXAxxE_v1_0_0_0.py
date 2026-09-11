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
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BaudRate': {'Status': {}},
            'OutletControl': {'Parameters': ['Outlet'], 'Status': {}},
            'RelayControl': {'Parameters': ['Relay'], 'Status': {}},
        }

        self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Baud Rate:\s+(2400|9600|57600|115200)\r\n'), self.__MatchBaudRate, None)
            self.AddMatchString(re.compile(b'Outlet ([1-8]):\s+(On|Off)\r\n'), self.__MatchOutletControl, None)
            self.AddMatchString(re.compile(b'(Aux [12]):\s+(On|Off)\r\n'), self.__MatchRelayControl, None)
            self.AddMatchString(re.compile(b'(Bad command or parameter|Invalid Command)\r\n'), self.__MatchError, None)
            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(re.compile(b'\xFF\xFB\x01'), self.__MatchHandshake, None)
                self.AddMatchString(re.compile(b'User>'), self.__MatchUsername, None)
                self.AddMatchString(re.compile(b'Password>'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Axess ELITE>'), self.__MatchAuthenticated, None)

    def __MatchHandshake(self, match, tag):
        self.Send(b'\xFF\xFB\x1F\xFF\xFB\x20\xFF\xFB\x18\xFF\xFB\x27\xFF\xFD\x01\xFF\xFB\x03\xFF\xFD\x03')

    def __MatchUsername(self, match, tag):
        self.Send(self.deviceUsername + '\r\n')

    def __MatchPassword(self, match, tag):
        self.Send(self.devicePassword + '\r\n')

    def __MatchAuthenticated(self, match, tag):
        self.Authenticated = True

    def UpdateBaudRate(self, value, qualifier):

        BaudRateCmdString = 'get console\r\n'
        self.__UpdateHelper('BaudRate', BaudRateCmdString, value, qualifier)

    def __MatchBaudRate(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('BaudRate', value, None)

    def SetOutletControl(self, value, qualifier):

        outlet = int(qualifier['Outlet'])
        if 1 <= outlet <= 8 and value in ['On', 'Off', 'Reboot']:
            OutletControlCmdString = 'set outlet {} {}\r\n'.format(outlet, value.lower())
            self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def UpdateOutletControl(self, value, qualifier):

        outlet = int(qualifier['Outlet'])
        if 1 <= outlet <= 8:
            OutletControlCmdString = 'get outlet {}\r\n'.format(outlet)
            self.__UpdateHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutletControl')

    def __MatchOutletControl(self, match, tag):

        qualifier = {}
        qualifier['Outlet'] = match.group(1).decode()
        value = match.group(2).decode().title()
        self.WriteStatus('OutletControl', value, qualifier)

    def SetRelayControl(self, value, qualifier):

        RelayStates = {
            'Aux 1': '9',
            'Aux 2': '10'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'Reboot': 'reboot'
        }

        RelayControlCmdString = 'set outlet {} {}\r\n'.format(RelayStates[qualifier['Relay']], ValueStateValues[value])
        self.__SetHelper('RelayControl', RelayControlCmdString, value, qualifier)

    def UpdateRelayControl(self, value, qualifier):

        RelayStates = {
            'Aux 1': '9',
            'Aux 2': '10'
        }

        RelayControlCmdString = 'get outlet {}\r\n'.format(RelayStates[qualifier['Relay']])
        self.__UpdateHelper('RelayControl', RelayControlCmdString, value, qualifier)

    def __MatchRelayControl(self, match, tag):

        qualifier = {}
        qualifier['Relay'] = match.group(1).decode()
        value = match.group(2).decode().title()
        self.WriteStatus('RelayControl', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated:
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
        else:
            if 'Serial' in self.ConnectionType:
                self.Send('\r')
            else:
                self.Discard('Ethenet Protocol: Waiting for device to Authenticate')

    def __MatchError(self, match, tag):
        self.Error([match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = False

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
