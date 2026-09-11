from extronlib.interface import SerialInterface, EthernetClientInterface
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
            'Breaker': {'Parameters': ['Address'], 'Status': {}},
            'Required': {'Status': {}},
            'Zone': {'Parameters': ['Active Zone'], 'Status': {}},
        }
        
        self.deviceUsername = 'admin'
        self.devicePassword = 'pw'
        self.Authenticated = 'Not Needed'
        self.WaitingForPrompt = True
        self.LoginPromptWait = Wait(2, self.LoginPromptWaitFunc)
        self.LoginPromptWait.Cancel()

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'B0C8([0-9A-F]{2})0([12345])F0\r\n'), self.__MatchBreaker, None)
            self.AddMatchString(re.compile(b'B0B90C((01|02|03){12})F0\r\n'), self.__MatchZone, None)

            self.AddMatchString(re.compile(b'Login:'), self.__MatchUserName, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Logged in successfully'), self.__MatchAuthentication, None)

    def LoginPromptWaitFunc(self):
        self.WaitingForPrompt = False

    def __MatchAuthentication(self, match, tag):
        self.WaitingForPrompt = False
        self.Authenticated = 'Admin'

    def __MatchUserName(self, match, tag):

        self.Authenticated = 'None'
        if self.deviceUsername:
            self.Send(self.deviceUsername + '\r\n')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send(self.devicePassword + '\r\n')
        else:
            self.MissingCredentialsLog('Password')

    def SetBreaker(self, value, qualifier):

        AddressStates = {
            'Min': 1,
            'Max': 168
        }

        ValueStateValues = {
            'On': 'B0B4',
            'Off': 'B0B5'
        }

        Address = int(qualifier['Address'])
        if AddressStates['Min'] <= Address <= AddressStates['Max']:
            BreakerCmdString = ValueStateValues[value] + '{0:02X}'.format(Address) + 'F0\r\n'
            self.__SetHelper('Breaker', BreakerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBreaker')

    def UpdateBreaker(self, value, qualifier):

        Address = int(qualifier['Address'])
        BreakerCmdString = 'B0BD' + '{0:02X}'.format(Address) + 'F0\r\n'
        self.__UpdateHelper('Breaker', BreakerCmdString, value, qualifier)

    def __MatchBreaker(self, match, tag):

        ValueStateValues = {
            '2': 'On',
            '1': 'Off',
            '3': 'Tripped',
            '4': 'Faulty',
            '5': 'Empty'
        }
        AddressValue = int(match.group(1).decode(), 16)
        qualifier = {'Address': str(AddressValue)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Breaker', value, qualifier)

    def SetZone(self, value, qualifier):

        ActiveZoneStates = {
            'Min': 1,
            'Max': 12
        }

        ValueStateValues = {
            'On': 'B0B7',
            'Off': 'B0B8'
        }

        Zone = int(qualifier['Active Zone'])
        if ActiveZoneStates['Min'] <= Zone <= ActiveZoneStates['Max']:
            ZoneCmdString = ValueStateValues[value] + '{0:02X}'.format(Zone) + 'F0\r\n'
            self.__SetHelper('Zone', ZoneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone')
    
    def UpdateZone(self, value, qualifier):

        ZoneCmdString = 'B0B9F0\r\n'
        self.__UpdateHelper('Zone', ZoneCmdString, value, qualifier)

    def __MatchZone(self, match, tag):

        Statevalues = {
            '1': 'Off',
            '2': 'On',
            '3': 'Sequencing'
        }

        if match.group(1).decode():
            value = match.group(1).decode()
            zone = 1
            for i in range(1, 24, 2):
                self.WriteStatus('Zone', Statevalues[value[i]], {'Active Zone': str(zone)})
                zone += 1

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if not self.WaitingForPrompt:
            if self.Authenticated in ['Not Needed', 'Admin']:
                self.Send(commandstring)
            else:
                self.Discard('Invalid Command or Unauthenticated')
        else:
            self.Discard('Waiting for login prompt from the device.')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if not self.WaitingForPrompt:
            if self.Authenticated in ['Not Needed', 'Admin']:

                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.Send(commandstring)
            else:
                self.Discard('Invalid Command or Unauthenticated')
        else:
            self.Discard('Waiting for login prompt from the device.')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.WaitingForPrompt = True
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.LoginPromptWait.Restart()
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
