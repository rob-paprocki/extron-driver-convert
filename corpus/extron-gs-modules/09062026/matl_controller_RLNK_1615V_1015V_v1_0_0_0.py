from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
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
        self.Debug = False
        self.devicePassword = 'password'
        self.deviceUsername = 'user'
        self.Models = {
            'RLNK-1615V': self.matl_20_2923_1615,
            'RLNK-1015V': self.matl_20_2923_1015,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CurrentIPAddress': {'Status': {}},
            'PowerOutlet': {'Parameters': ['Outlet Number', 'Cycle Time'], 'Status': {}},
            'PowerOutletStatus': {'Parameters': ['Outlet Number'], 'Status': {}},
            'SequencePowerOutlets': {'Parameters': ['Delay Time'], 'Status': {}},
            'SequencePowerOutletsStatus': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xFE\x03\x00\x01\x01\x03\xFF'), self.__MatchPing, None)
            self.AddMatchString(re.compile(b'\xFE([\x01-\xFF])\x00\x94\x10([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})([\x00-\xFF])\xFF'), self.__MatchCurrentIPAddress, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x20(\x10|\x12)([\x01-\x10])([\x00-\x03])([0-9]{1,4})([\x00-\xFF])\xFF'), self.__MatchPowerOutletStatus, None)
            self.AddMatchString(re.compile(b'\xFE\x08\x00\x36(\x10|\x12)([\x00-\x04])([0-9]{4})([\x00-\xFF])\xFF'), self.__MatchSequencePowerOutletsStatus, None)
            self.AddMatchString(re.compile(b'\xFE([\x01-\xFF])\x00\x10([\x00-\x11])[\x00-\xFF]{1,2}\xFF'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'\xFE\x04\x00\x02\x10\x00\x14\xFF'), self.__MatchLogInError, None)
            self.AddMatchString(re.compile(b'\xFE\x09\x00\x41\x10\x01\x01\x00\x00\x00\x00\x5A\xFF'), self.__MatchVerbose, None)

    def SetLogin(self):

        if self.deviceUsername:
            if self.devicePassword:
                DataString = b'\x00\x02\x01' + bytes(self.deviceUsername, 'ascii') + b'\x7C' + bytes(self.devicePassword, 'ascii')
                Length = pack('>B', len(DataString))
                LoginString = b'\xFE' + Length + DataString
                CheckSum = self.CalculateChecksum(LoginString)
                LoginCmdString = LoginString + CheckSum + b'\xFF'
                self.Send(LoginCmdString)
            else:
                self.MissingCredentialsLog('Password')
        else:
            self.MissingCredentialsLog('Username')

    def SetPong(self, match, tag):

        self.Send(b'\xFE\x03\x00\x01\x10\x12\xFF')

    def __MatchPing(self, match, tag):

        self.SetPong(None, None)

    def __MatchLogInError(self, match, tag):

        self.Error(['Login Failed'])
        self.SetLogin()

    def __MatchVerbose(self, match, tag):

        self.VerboseDisabled = False

    def CalculateChecksum(self, string):
        CheckSum = 0
        for i in string:
            CheckSum = CheckSum + i
        if CheckSum > 255:
            CheckSum = CheckSum & 255
        CheckSum = pack('B', CheckSum & 127)

        return CheckSum

    def UpdateCurrentIPAddress(self, value, qualifier):

        CurrentIPAddressCmdString = b'\xFE\x04\x00\x94\x02\x00\x18\xFF'
        self.__UpdateHelper('CurrentIPAddress', CurrentIPAddressCmdString, value, qualifier)

    def __MatchCurrentIPAddress(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('CurrentIPAddress', value, None)

    def SetPowerOutlet(self, value, qualifier):

        CycleTimeConstraints = {
            'Min': 0,
            'Max': 3600
        }

        PowerOutletStateValues = {
            'On': b'\x01',
            'Off': b'\x00',
            'Cycle': b'\x02'
        }

        Outlet = self.OutletNumberStates[qualifier['Outlet Number']]

        if CycleTimeConstraints['Min'] <= qualifier['Cycle Time'] <= CycleTimeConstraints['Max']:
            if value == 'Cycle':
                CycleTime = bytes(str(qualifier['Cycle Time']).zfill(4), 'ascii')
            else:
                CycleTime = b'0000'
            PowerOutlet = b'\xFE\x09\x00\x20\x01' + Outlet + PowerOutletStateValues[value] + CycleTime
            CheckSum = self.CalculateChecksum(PowerOutlet)
            PowerOutletCmdString = PowerOutlet + CheckSum + b'\xFF'
            self.__SetHelper('PowerOutlet', PowerOutletCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOutlet')

    def UpdatePowerOutletStatus(self, value, qualifier):

        PowerOutletStatus = b'\xFE\x04\x00\x20\x02' + self.OutletNumberStates[qualifier['Outlet Number']]
        CheckSum = self.CalculateChecksum(PowerOutletStatus)
        PowerOutletStatusCmdString = PowerOutletStatus + CheckSum + b'\xFF'
        self.__UpdateHelper('PowerOutletStatus', PowerOutletStatusCmdString, value, qualifier)

    def __MatchPowerOutletStatus(self, match, tag):

        PowerOutletStatusStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Cycle',
            b'\x03': 'Not Controllable'
        }

        PowerOutletStatus = self.OutletNumberStatesName[match.group(2)]
        value = PowerOutletStatusStateValues[match.group(3)]
        self.WriteStatus('PowerOutletStatus', value, {'Outlet Number': PowerOutletStatus})

    def SetSequencePowerOutlets(self, value, qualifier):

        DelayTimeConstraints = {
            'Min': 0,
            'Max': 999
        }

        SequencePowerOutletsStateValues = {
            'Up': b'\x01',
            'Down': b'\x03'
        }
        if DelayTimeConstraints['Min'] <= qualifier['Delay Time'] <= DelayTimeConstraints['Max']:
            DelayTime = bytes(str(qualifier['Delay Time']).zfill(4), 'ascii')
            SequencePowerOutlets = b'\xFE\x08\x00\x36\x01' + SequencePowerOutletsStateValues[value] + DelayTime
            CheckSum = self.CalculateChecksum(SequencePowerOutlets)
            SequencePowerOutletsCmdString = SequencePowerOutlets + CheckSum + b'\xFF'
            self.__SetHelper('SequencePowerOutlets', SequencePowerOutletsCmdString, value, qualifier)

    def UpdateSequencePowerOutletsStatus(self, value, qualifier):

        SequencePowerOutletsStatusCmdString = b'\xFE\x04\x00\x36\x02\x00\x3A\xFF'
        self.__UpdateHelper('SequencePowerOutletsStatus', SequencePowerOutletsStatusCmdString, value, qualifier)

    def __MatchSequencePowerOutletsStatus(self, match, tag):

        ValueStateValues = {
            b'\x00': 'No Sequence Status',
            b'\x01': 'Sequencing Up',
            b'\x02': 'Sequence Up Complete',
            b'\x03': 'Sequencing Down',
            b'\x04': 'Sequence Down Complete'
        }

        value = ValueStateValues[match.group(2)]
        self.WriteStatus('SequencePowerOutletsStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.VerboseDisabled:
                self.Send(b'\xFE\x09\x00\x41\x01\x01\x01\x00\x00\x00\x00\x4B\xFF')
                self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        ErrorCode = {
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
        self.Error([ErrorCode[match.group(2)]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

    def matl_20_2923_1615(self):
        self.OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F',
            '16': b'\x10'
        }
        self.OutletNumberStatesName = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8',
            b'\x09': '9',
            b'\x0A': '10',
            b'\x0B': '11',
            b'\x0C': '12',
            b'\x0D': '13',
            b'\x0E': '14',
            b'\x0F': '15',
            b'\x10': '16'
        }

    def matl_20_2923_1015(self):
        self.OutletNumberStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A'
        }
        self.OutletNumberStatesName = {
            b'\x01': '1',
            b'\x02': '2',
            b'\x03': '3',
            b'\x04': '4',
            b'\x05': '5',
            b'\x06': '6',
            b'\x07': '7',
            b'\x08': '8',
            b'\x09': '9',
            b'\x0A': '10'
        }

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
            self.SetLogin()
        return result

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
