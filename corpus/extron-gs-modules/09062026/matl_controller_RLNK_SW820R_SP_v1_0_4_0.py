from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import ProgramLog
from struct import pack


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
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'
        self.Debug = False
        self.Models = {}
        
        self.PasswordPromptCount = 0

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DryContacts': {'Parameters': ['Cycle Time', 'Contact Number'], 'Status': {}},
            'PowerOutlet': {'Parameters': ['Cycle Time', 'Outlet Number'], 'Status': {}},
            'Temperature': {'Status': {}},
        }
        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x00\x14\xFF'), self.__MatchLogInError, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x41\x10\x01\x01\x00\x00\x00\x00\x5A\xFF'), self.__MatchVerbose, None)

            self.AddMatchString(re.compile(b'\xFE\x09\x00\x30(\x10|\x12)([\x01-\x08])([\x00-\x03])([0-9]{1,4})([\x01-\xFF])\xFF'), self.__MatchDryContacts, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x20(\x10|\x12)([\x01-\x08])([\x00-\x03])([0-9]{1,4})([\x01-\xFF])\xFF'), self.__MatchPowerOutlet, None)
            self.AddMatchString(re.compile(b'\xFE\x06\x00\x55\x10([0-9]{1,3})([\x01-\xFF])\xFF'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x10\x10([\x00-\xFF])([\x00-\xFF])\xFF'), self.__MatchError, None)

    def SetLogin(self, match, tag):
        if self.deviceUsername is None:
            self.MissingCredentialsLog('Username')
            return
        
        if self.devicePassword is None:
            self.MissingCredentialsLog('Password')
            return
        
        LoginString = b'\xFE\x10\x00\x02\x01' + bytes(self.deviceUsername, 'ascii') + b'\x7C' + bytes(self.devicePassword, 'ascii')
        CheckSum = self.CalculateChecksum(LoginString)
        LoginCmdString = LoginString + CheckSum + b'\xFF'
        self.Send(LoginCmdString)

    def __MatchLogInError(self, match, tag):
        self.PasswordPromptCount += 1
        if self.PasswordPromptCount > 2:
            print('Incorrect login credentials provided.')
        else:
            self.SetLogin(None, None)

    def __MatchVerbose(self, match, tag):

        self.VerboseDisabled = False

    def SetVerbose(self, value, qualifier):

        self.Send(b'\xFE\x09\x00\x41\x01\x01\x01\x00\x00\x00\x00\x4B\xFF')

    def CalculateChecksum(self, string):
        CheckSum = 0
        for i in string:
            CheckSum = CheckSum + i
        CheckSum = pack('B', CheckSum & 127)

        return CheckSum

    def SetDryContacts(self, value, qualifier):

        CycleTimeConstraints = {
            'Min': 0,
            'Max': 3600
        }

        ContactNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08'
        }

        DryContactStates = {
            'On': b'\x01',
            'Off': b'\x00',
            'Cycle': b'\x02'
        }

        Contact = ContactNumberStates[qualifier['Contact Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = '{0}'.format(qualifier['Cycle Time']).zfill(4).encode()
            else:
                CycleTime = b'0000'
            DryContacts = b'\xFE\x09\x00\x30\x01' + Contact + DryContactStates[value] + CycleTime
            CheckSum = self.CalculateChecksum(DryContacts)
            DryContactsCmdString = DryContacts + CheckSum + b'\xFF'
            self.__SetHelper('DryContacts', DryContactsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDryContacts')

    def UpdateDryContacts(self, value, qualifier):

        ContactNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08'
        }

        DryContacts = b'\xFE\x04\x00\x30\x02' + ContactNumberStates[qualifier['Contact Number']]
        CheckSum = self.CalculateChecksum(DryContacts)
        DryContactsCmdString = DryContacts + CheckSum + b'\xFF'
        self.__UpdateHelper('DryContacts', DryContactsCmdString, value, qualifier)

    def __MatchDryContacts(self, match, tag):

        ContactNumberStates = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8'
        }

        DryContactValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cycle',
            b'\x03': 'Not Controllable'
        }

        CycleTime = int(match.group(4).decode())
        ContactNumber = ContactNumberStates[match.group(2)]
        value = DryContactValues[match.group(3)]
        self.WriteStatus('DryContacts', value, {'Cycle Time': CycleTime, 'Contact Number': ContactNumber})

    def SetPowerOutlet(self, value, qualifier):

        CycleTimeConstraints = {
            'Min': 0,
            'Max': 3600
        }

        OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08'
        }

        PowerOutletStates = {
            'On': b'\x01',
            'Off': b'\x00',
            'Cycle': b'\x02',
        }

        Outlet = OutletNumberStates[qualifier['Outlet Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = '{0}'.format(qualifier['Cycle Time']).zfill(4).encode()
            else:
                CycleTime = b'0000'

            PowerOutlet = b'\xFE\x09\x00\x20\x01' + Outlet + PowerOutletStates[value] + CycleTime
            CheckSum = self.CalculateChecksum(PowerOutlet)
            PowerOutletCmdString = PowerOutlet + CheckSum + b'\xFF'
            self.__SetHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPowerOutlet')

    def UpdatePowerOutlet(self, value, qualifier):

        OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08'
        }

        PowerOutlet = b'\xFE\x04\x00\x20\x02' + OutletNumberStates[qualifier['Outlet Number']]
        CheckSum = self.CalculateChecksum(PowerOutlet)
        PowerOutletCmdString = PowerOutlet + CheckSum + b'\xFF'
        self.__UpdateHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)

    def __MatchPowerOutlet(self, match, tag):

        OutletNumberStates = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8'
        }

        PowerOutletState = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cycle',
            b'\x03': 'Not Controllable'
        }

        CycleTime = int(match.group(4).decode())
        PowerOutlet = OutletNumberStates[match.group(2)]
        value = PowerOutletState[match.group(3)]
        self.WriteStatus('PowerOutlet', value, {'Cycle Time': CycleTime, 'Outlet Number': PowerOutlet})

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = b'\xFE\x04\x00\x55\x02\x00\x59\xFF'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            if self.VerboseDisabled:
                self.SetVerbose(None, None)
                
            self.Send(commandstring)            

    def __MatchError(self, match, tag):

        ErrorState = {
            b'\x01': 'Bad Checksum',
            b'\x02': 'Bad Length',
            b'\x03': 'Escaped Error',
            b'\x04': 'Invalid Command',
            b'\x05': 'Invalid Sub-Command',
            b'\x06': 'Invalid Qty Data Bytes',
            b'\x07': 'Invalid Data Byte Values',
            b'\x08': 'Access Denied (Credentials)',
            b'\x10': 'Unknown',
            b'\x11': 'Access Denied (EPO)'
        }

        errorstring = ErrorState[match.group(1)]
        print(errorstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetLogin(None, None)

        if self.VerboseDisabled:
            self.SetVerbose(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.PasswordPromptCount = 0
        self.VerboseDisabled = True

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
