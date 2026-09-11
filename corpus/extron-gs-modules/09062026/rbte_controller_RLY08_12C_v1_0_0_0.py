from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self._Address = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChangeAddress': {'Parameters': ['New Address'], 'Status': {}},
            'Relay': {'Parameters': ['Relay'], 'Status': {}},
        }

    @property
    def Address(self):
        return self._Address

    @Address.setter
    def Address(self, value):
        if 1 <= int(value) <= 8:
            self._Address = int(value)

    def SetChangeAddress(self, value, qualifier):

        NewAddressStates = {
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08
        }

        self.__SetHelper('ChangeAddress', pack('>BB', self._Address, 0xA0), value, qualifier)
        self.__SetHelper('ChangeAddress', pack('>BB', self._Address, 0xAA), value, qualifier)
        self.__SetHelper('ChangeAddress', pack('>BB', self.Address, 0xA5), value, qualifier)
        self.__SetHelper('ChangeAddress', pack('>BB', self._Address, NewAddressStates[qualifier['New Address']]), value, qualifier)

    def UpdateRelay(self, value, qualifier):

        MaskValues = {
            '1': 1,
            '2': 2,
            '3': 4,
            '4': 8,
            '5': 16,
            '6': 32,
            '7': 64,
            '8': 128
        }

        RelayCmdString = pack('>BB', self._Address, 0x5B)
        res = self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)
        if res:
            try:
                for i in range(1, 9):
                    value = res[0] & MaskValues[str(i)]
                    if value == MaskValues[str(i)]:
                        value = 'On'
                    else:
                        value = 'Off'
                    self.WriteStatus('Relay', value, {'Relay': str(i)})
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateHeartbeat')

    def SetRelay(self, value, qualifier):

        RelayStates = {
            '1': [0x65, 0x6F],
            '2': [0x66, 0x70],
            '3': [0x67, 0x71],
            '4': [0x68, 0x72],
            '5': [0x69, 0x73],
            '6': [0x6A, 0x74],
            '7': [0x6B, 0x75],
            '8': [0x6C, 0x76],
            'All': [0x64, 0x6E]
        }

        if value == 'On':
            RelayCmdString = pack('>BB', self._Address, RelayStates[qualifier['Relay']][0])
        else:
            RelayCmdString = pack('>BB', self._Address, RelayStates[qualifier['Relay']][1])
        self.__SetHelper('Relay', RelayCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=2)
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                return res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=1)
            if res:
                return res

            

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
