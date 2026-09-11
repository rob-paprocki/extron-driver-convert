from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search

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
            'PowerOutlet': {'Parameters': ['Number'], 'Status': {}},
            'SerialNumber': {'Status': {}},
        }

        self.authenticated = False
        self.deviceUsername = 'apc'
        self.devicePassword = 'apc'
        self._DisplayID = 1

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'User Name :'), self.__MatchLoginUsername, None)
            self.AddMatchString(compile(b'Password  :'), self.__MatchLoginPassword, None)
            self.AddMatchString(compile(b'E000: Success\r\n(?: [1-8]: [\S ]+?: (?:On|Off)\*? \r\n){8}\r\napc>'), self.__MatchPowerOutlet, None)
            self.AddMatchString(compile(b'E000: Success\r\nHardware Factory\r\n-+?\r\nModel Number: \t\t(?:[\S ]+?)\r\nSerial Number: \t\t([\S ]+?)\r\n'), self.__MatchSerialNumber, None)
            self.AddMatchString(compile(b'(E(?:10[0-7]|20\d|210)):([\S ]+?)\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'Schneider Electric'), self.__MatchLoginSuccessful, None)
            self.AddMatchString(compile(b'Connection Closed - Bye'), self.__MatchLoginFailed, None)

        self.PowerOutletRegEx = compile(b'([1-8]): [\S ]+?: (On|Off)\*? \r\n')

    @property
    def DisplayID(self):
        return self._DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if 1 <= int(value) <= 4:
            self._DisplayID = int(value)
        else:
            print('Invalid DisplayID entered. Range is from 1 to 4')

    def __MatchLoginUsername(self, match, tag):
        self.SetUsername()

    def SetUsername(self):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchLoginPassword(self, match, tag):
        self.SetPassword()

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchLoginFailed(self, match, tag):

        self.authenticated = False
        self.Error(['Login procedure failed. Check Username and Password.'])

    def __MatchLoginSuccessful(self, match, tag):

        self.authenticated = True

    def SetPowerOutlet(self, value, qualifier):

        ValueStateValues = {
            'On': 'olOn',
            'Off': 'olOff'
        }

        outlet_number = qualifier['Number']
        if (outlet_number == 'All') or (outlet_number.isdigit() and 1 <= int(outlet_number) <= 8):
            PowerOutletCmdString = '{} {}:{}\r\n'.format(ValueStateValues[value], self._DisplayID, outlet_number.lower())
            self.__SetHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOutlet')

    def UpdatePowerOutlet(self, value, qualifier):

        outlet_number = qualifier['Number']
        if (outlet_number == 'All') or (outlet_number.isdigit() and 1 <= int(outlet_number) <= 8):
            PowerOutletCmdString = 'olStatus {}:all\r\n'.format(self._DisplayID)
            self.__UpdateHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdatePowerOutlet')

    def __MatchPowerOutlet(self, match, tag):

        for result in self.PowerOutletRegEx.findall(match.group(0)):
            qualifier = dict()
            qualifier['Number'] = result[0].decode()
            value = result[1].decode()
            self.WriteStatus('PowerOutlet', value, qualifier)

    def UpdateSerialNumber(self, value, qualifier):

        SerialNumberCmdString = 'about\r\n'
        self.__UpdateHelper('SerialNumber', SerialNumberCmdString, value, qualifier)

    def __MatchSerialNumber(self, match, tag):

        value = (match.group(1).decode()).strip()
        self.WriteStatus('SerialNumber', value, None)

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
        else:
            self.Discard('Device is not Authenticated')

    def __MatchError(self, match, tag):

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
                result = search(regexString, self._ReceiveBuffer)
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
