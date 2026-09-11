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
            'BatteryCapacity': {'Status': {}},
            'Current': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'InternalTemperature': {'Status': {}},
            'OutletControl': {'Parameters': ['Group'], 'Status': {}},
            'RuntimeRemaining': {'Status': {}},
            'UniversalIOControl': {'Parameters': ['Port'], 'Status': {}},
            'UPSControl': {'Status': {}},
            'Voltage': {'Parameters': ['Type'], 'Status': {}},
        }

        self.authenticated = False
        self.deviceUsername = 'apc'
        self.devicePassword = 'apc'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'User Name :'), self.__MatchLoginUsername, None)
            self.AddMatchString(re.compile(b'Password  :'), self.__MatchLoginPassword, None)
            self.AddMatchString(re.compile(b'Battery Capacity: (\d+)\s?\%\r\n'), self.__MatchBatteryCapacity, None)
            self.AddMatchString(re.compile(b'Current: (\d+).+\r\n'), self.__MatchCurrent, None)
            self.AddMatchString(re.compile(b'Internal Temperature: (\d+\.\d+)C\r\n'), self.__MatchInternalTemperature, None)
            self.AddMatchString(re.compile(b'Runtime Remaining: (\d+ hr \d+ min \d+ sec)\r\n'), self.__MatchRuntimeRemaining, None)
            self.AddMatchString(re.compile(b'(Input|Output|Battery) Voltage: (\d+) VAC\r\n'), self.__MatchVoltage, None)
            self.AddMatchString(re.compile(b'(E(?:10[0-7])):([\S ]+?)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Schneider Electric'), self.__MatchLoginSuccessful, None)
            self.AddMatchString(re.compile(b'Connection Closed - Bye'), self.__MatchLoginFailed, None)

    def __MatchLoginUsername(self, match, tag):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchLoginPassword(self, match, tag):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginFailed(self, match, tag):
        self.authenticated = False
        self.Error(['Login procedure failed. Check Username and Password.'])

    def __MatchLoginSuccessful(self, match, tag):
        self.authenticated = True

    def UpdateDeviceStatus(self, value, qualifier):
        DeviceStatusCmdString = 'detstatus -all\r\n'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchBatteryCapacity(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('BatteryCapacity', value, None)

    def __MatchCurrent(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Current', value, None)

    def __MatchInternalTemperature(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('InternalTemperature', value, None)

    def __MatchRuntimeRemaining(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('RuntimeRemaining', value, None)

    def __MatchVoltage(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('Voltage', value, {'Type': match.group(1).decode()})

    def SetOutletControl(self, value, qualifier):

        group = qualifier['Group']

        state = {
            'On': 'On',
            'Off': 'Off',
            'Delay On': 'DelayOn',
            'Delay Off': 'DelayOff',
            'Delay Reboot': 'DelayReboot',
            'Delay Shutdown': 'DelayShutdown',
            'Reboot': 'Reboot',
            'Shutdown': 'Shutdown',
            'Cancel': 'Cancel'
        }[value]

        if 1 <= int(group) <= 3:
            OutletControlCmdString = 'ups -o{} {}\r\n'.format(group, state)
            self.__SetHelper('OutletControl', OutletControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutletControl')

    def SetUniversalIOControl(self, value, qualifier):

        port = qualifier['Port']
        if port in ['1', '2'] and value in ['Open', 'Close']:
            UniversalIOControlCmdString = 'uio -rc {} {}\r\n'.format(port, value.lower())
            self.__SetHelper('UniversalIOControl', UniversalIOControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUniversalIOControl')

    def SetUPSControl(self, value, qualifier):

        state = {
            'On': 'on',
            'Off': 'off',
            'Grace Off': 'graceoff',
            'Grace Reboot': 'gracereboot',
            'Grace Sleep': 'gracesleep',
            'Reboot': 'reboot',
            'Sleep': 'sleep'
        }[value]

        UPSControlCmdString = 'ups -c {}\r\n'.format(state)
        self.__SetHelper('UPSControl', UPSControlCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
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
        err_number = match.group(1).decode()
        err_message = match.group(2).decode()
        self.Error(['Error: {}: {}'.format(err_number, err_message)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.authenticated = False

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

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
