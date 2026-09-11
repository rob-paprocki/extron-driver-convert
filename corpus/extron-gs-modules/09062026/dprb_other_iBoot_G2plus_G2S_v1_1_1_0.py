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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Event': {'Parameters': ['Number'], 'Status': {}},
            'ExpansionLinktoMain': {'Parameters': ['Port'], 'Status': {}},
            'OutletPower': {'Parameters': ['Outlet'], 'Status': {}},
            'PowerCycleTime': {'Status': {}},
            'RebootRequiredStatus': {'Status': {}},
        }

        self.loggedIn = False
        self.FirstLogin = True
        self.deviceUsername = 'Admin'
        self.devicePassword = 'Admin'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(Main Outlet|EXP1|EXP2):[ \t]*(On|Off)[ \t]*(L|)?[ \t]*\r\n'), self.__MatchOutletPower, None)
            self.AddMatchString(re.compile(b'User>'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password>'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'iBoot>'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'iBoot Reboot Required>'), self.__MatchRebootRequiredStatus, None)
            self.AddMatchString(re.compile(b'\xFF\xFB\x01'), self.__MatchHandshake, None)

    def __MatchUsername(self, match, tag):

        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):

        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLogin(self, match, tag):

        self.WriteStatus('RebootRequiredStatus', 'No Reboot Required', None)
        self.loggedIn = True
        if self.FirstLogin:
            self.FirstLogin = False
            self.SetExpansionMode(None, None)

    def __MatchHandshake(self, match, tag):
        self.SetHandshake(None, None)

    def SetHandshake(self, value, qualifier):
        self.Send(b'\xFF\xFB\x1F\xFF\xFB\x20\xFF\xFB\x18\xFF\xFB\x27\xFF\xFD\x01\xFF\xFB\x03\xFF\xFD\x03')

    def SetExpansionMode(self, value, qualifier):
        self.Send('set expansion mode power\r\n')

    def SetEvent(self, value, qualifier):

        NumberStates = {
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
            'Run': 'run',
            'Hold': 'hold'
        }

        EventCmdString = 'set event {0} {1}\r\n'.format(NumberStates[qualifier['Number']], ValueStateValues[value])
        self.__SetHelper('Event', EventCmdString, value, qualifier)

    def SetExpansionLinktoMain(self, value, qualifier):

        PortStates = {
            '1': '1',
            '2': '2'
        }

        ValueStates = {
            'On': 'yes',
            'Off': 'no'
        }

        ExpansionLinktoMainCmdString = 'set expansion exp{0} link {1}\r\n'.format(PortStates[qualifier['Port']], ValueStates[value])
        self.__SetHelper('ExpansionLinktoMain', ExpansionLinktoMainCmdString, value, qualifier)

    def UpdateExpansionLinktoMain(self, value, qualifier):
        self.UpdateOutletPower(value, qualifier)

    def SetOutletPower(self, value, qualifier):

        OutletStates = {
            'Main': 'main',
            'Expansion 1': 'exp1',
            'Expansion 2': 'exp2'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'Cycle': 'cycle'
        }

        OutletPowerCmdString = 'set {0} {1}\r\n'.format(OutletStates[qualifier['Outlet']], ValueStateValues[value])
        self.__SetHelper('OutletPower', OutletPowerCmdString, value, qualifier)

    def UpdateOutletPower(self, value, qualifier):
        OutletPowerCmdString = 'get status\r\n'
        self.__UpdateHelper('OutletPower', OutletPowerCmdString, value, qualifier)

    def __MatchOutletPower(self, match, tag):

        OutletStates = {
            'Main Outlet': 'Main',
            'EXP1': 'Expansion 1',
            'EXP2': 'Expansion 2'
        }

        PortStates = {
            'EXP1': '1',
            'EXP2': '2'
        }

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off',
        }

        qualifier = {'Outlet': OutletStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutletPower', value, qualifier)

        if match.group(1).decode() != 'Main Outlet':
            if match.group(3).decode() == 'L':
                qualifier = {'Port': PortStates[match.group(1).decode()]}
                self.WriteStatus('ExpansionLinktoMain', 'On', qualifier)
            else:
                qualifier = {'Port': PortStates[match.group(1).decode()]}
                self.WriteStatus('ExpansionLinktoMain', 'Off', qualifier)

    def SetPowerCycleTime(self, value, qualifier):

        if 1 <= value <= 999:
            PowerCycleTimeCmdString = 'set cycle {0}\r\n'.format(value)
            self.__SetHelper('PowerCycleTime', PowerCycleTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerCycleTime')

    def __MatchRebootRequiredStatus(self, match, tag):

        self.WriteStatus('RebootRequiredStatus', 'Reboot Required', None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.loggedIn:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self.loggedIn == False:
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

        self.FirstLogin = True
        self.loggedIn = False

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
