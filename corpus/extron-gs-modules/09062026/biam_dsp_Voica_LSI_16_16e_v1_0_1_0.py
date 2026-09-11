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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'
        self.Token = 0

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'EmergencyZoneStatus': {'Parameters': ['Zone ID'], 'Status': {}},
            'Handshake': {'Status': {}},
            'LocalSilence': {'Status': {}},
            'ResetSystemFault': {'Status': {}},
            'VirtualInput': {'Parameters': ['Input'], 'Status': {}},
            'VirtualInputGroup': {'Parameters': ['Lowest Input Number', 'Highest Input Number'], 'Status': {}},
            'VirtualInputType': {'Parameters': ['Input'], 'Status': {}},
        }

        if self.ConnectionType == 'Serial':
            self.Authenticated = True
        else:
            self.Authenticated = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'<ZoneStatus Command="Z"><State>STATE_OK</State><Zone Id="([\d]+)"><ZoneState>(Inactive|Muted|Announcing)</ZoneState><ZoneAvailable>(Yes|No)</ZoneAvailable>([\w<>/" ]+|)</ZoneStatus>'), self.__MatchEmergencyZoneStatus, None)
            self.AddMatchString(re.compile(b'<Query Command="I"><State>STATE_OK</State><VirtualInputDetail id="([\d]+)"><Name>[\w ]+</Name><Description>[\w ]+</Description><Function>(Fault|Alarm|Reset|All silence|All reset)</Function>([\w=<>/" ]+|)</VirtualInputDetail></Query>'), self.__MatchVirtualInputType, None)
            self.AddMatchString(re.compile(b'<Status Command="H"><State>STATE_OK</State><Token>([\d]+)<Token></Status>'), self.__MatchHandshake, None)
            self.AddMatchString(re.compile(b'<Status Command="U"><State>STATE_OK</State></Status>'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'<Status Command="P"><State>STATE_OK</State></Status>'), self.__MatchAuthorization, None)
            self.AddMatchString(re.compile(b'<Status Command="A"><State>AUTH_SUCCESS</State></Status>'), self.__MatchLoginSuccess, None)
            self.AddMatchString(re.compile(b'<State>STATE_FAULT</State>'), self.__MatchError, None)

    def SetLogin(self):
        if self.deviceUsername:
            self.Send('U ' + self.deviceUsername)
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send('P ' + self.devicePassword)
        else:
            self.MissingCredentialsLog('Password')

    def __MatchAuthorization(self, match, tag):
        self.Send('A')

    def __MatchLoginSuccess(self, match, tag):
        self.Authenticated = True

    def UpdateEmergencyZoneStatus(self, value, qualifier):

        zoneID = qualifier['Zone ID']
        if zoneID:
            EmergencyZoneStatusCmdString = 'Z Z {0}'.format(zoneID)
            self.__UpdateHelper('EmergencyZoneStatus', EmergencyZoneStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEmergencyZoneStatus')

    def __MatchEmergencyZoneStatus(self, match, tag):

        qualifier = {'Zone ID': match.group(1).decode()}
        value = match.group(2).decode()
        self.WriteStatus('EmergencyZoneStatus', value, qualifier)

    def UpdateHandshake(self, value, qualifier):

        if 'Serial' not in self.ConnectionType:
            HandshakeCmdString = 'H 1 {0}'.format(self.Token)
        else:
            HandshakeCmdString = 'H 0 {0}'.format(self.Token)

        self.__UpdateHelper('Handshake', HandshakeCmdString, value, qualifier)

    def __MatchHandshake(self, match, tag):

        self.Token = int(match.group(1).decode())

    def SetLocalSilence(self, value, qualifier):

        LocalSilenceCmdString = 'F A'
        self.__SetHelper('LocalSilence', LocalSilenceCmdString, value, qualifier)

    def SetResetSystemFault(self, value, qualifier):

        ResetSystemFaultCmdString = 'R S'
        self.__SetHelper('ResetSystemFault', ResetSystemFaultCmdString, value, qualifier)

    def SetVirtualInput(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        input = qualifier['Input']
        if 1 <= input <= 500:
            VirtualInputCmdString = 'I {0} {1}'.format(input, ValueStateValues[value])
            self.__SetHelper('VirtualInput', VirtualInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualInput')

    def SetVirtualInputGroup(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        Linput = qualifier['Lowest Input Number']
        Hinput = qualifier['Highest Input Number']
        if 1 <= Linput < Hinput <= 500:
            VirtualInputGroupCmdString = 'G {0}-{1} {2}'.format(Linput, Hinput, ValueStateValues[value])
            self.__SetHelper('VirtualInputGroup', VirtualInputGroupCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualInputGroup')

    def UpdateVirtualInputType(self, value, qualifier):

        input = qualifier['Input']
        if 1 <= input <= 500:
            VirtualInputTypeCmdString = 'Q I {0}'.format(input)
            self.__UpdateHelper('VirtualInputType', VirtualInputTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualInputType')

    def __MatchVirtualInputType(self, match, tag):

        ValueStateValues = {
            'Fault': 'Fault',
            'Alarm': 'Alarm',
            'Reset': 'Reset',
            'All reset': 'Reset All',
            'All silence': 'Silence All'
        }

        qualifier = {'Input': int(match.group(1).decode())}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VirtualInputType', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True
        if self.Authenticated:
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

            if self.Authenticated:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.Error(["Error Occured"])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if self.ConnectionType != 'Serial':
            self.Authenticated = False
        self.Token = 0

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
                    except BaseException:
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
        except BaseException:
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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
            DeviceClass.SetLogin(self)
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
