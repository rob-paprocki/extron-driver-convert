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
            'ActivatePairing': {'Status': {}},
            'BluetoothFriendlyNameCommand': {'Status': {}},
            'BluetoothFriendlyNameStatus': {'Status': {}},
            'BluetoothStatus': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'ClearBluetoothPairings': {'Status': {}},
            'CloseBluetoothConnection': {'Status': {}},
            'Mute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ACK BTN ([\s\S]*)\r'), self.__MatchBluetoothFriendlyNameStatus, None)
            self.AddMatchString(re.compile(b'ACK BTS ([012])\r'), self.__MatchBluetoothStatus, None)
            self.AddMatchString(re.compile(b'ACK BTL ([01])\r'), self.__MatchButtonLock, None)
            self.AddMatchString(re.compile(b'ACK MUTE ([01])\r'), self.__MatchMute, None)

    def SetActivatePairing(self, value, qualifier):

        ActivatePairingCmdString = 'BTB\r'
        self.__SetHelper('ActivatePairing', ActivatePairingCmdString, value, qualifier)

    def SetBluetoothFriendlyNameCommand(self, value, qualifier):

        friendlyName = value
        BluetoothFriendlyNameCommandCmdString = 'BTN ' + friendlyName + '\r'
        self.__SetHelper('BluetoothFriendlyNameCommand', BluetoothFriendlyNameCommandCmdString, value, qualifier)

    def UpdateBluetoothFriendlyNameStatus(self, value, qualifier):

        BluetoothFriendlyNameStatusCmdString = 'BTN\r'
        self.__UpdateHelper('BluetoothFriendlyNameStatus', BluetoothFriendlyNameStatusCmdString, value, qualifier)

    def __MatchBluetoothFriendlyNameStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('BluetoothFriendlyNameStatus', value, None)

    def UpdateBluetoothStatus(self, value, qualifier):

        BluetoothStatusCmdString = 'BTS\r'
        self.__UpdateHelper('BluetoothStatus', BluetoothStatusCmdString, value, qualifier)

    def __MatchBluetoothStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Idle',
            '1': 'Discoverable',
            '2': 'Connected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('BluetoothStatus', value, None)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ButtonLockCmdString = 'BTL ' + ValueStateValues[value] + '\r'
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):

        ButtonLockCmdString = 'BTL\r'
        self.__UpdateHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def __MatchButtonLock(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonLock', value, None)

    def SetClearBluetoothPairings(self, value, qualifier):

        ClearBluetoothPairingsCmdString = 'CBC\r'
        self.__SetHelper('ClearBluetoothPairings', ClearBluetoothPairingsCmdString, value, qualifier)

    def SetCloseBluetoothConnection(self, value, qualifier):

        CloseBluetoothConnectionCmdString = 'BCC\r'
        self.__SetHelper('CloseBluetoothConnection', CloseBluetoothConnectionCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
        }
        MuteCmdString = 'MUTE ' + ValueStateValues[value] + '\r'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'MUTE\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

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
