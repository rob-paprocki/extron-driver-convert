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
        self.Models = {}
        self._DeviceID = pack('>B', 1)
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputStatus': {'Parameters': ['Input'], 'Status': {}},
            'Relay': {'Parameters': ['Relay Number'], 'Status': {}},
            'RelayPulse': {'Parameters': ['Relay Number'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 15:
            self._DeviceID = pack('>B', int(value))
        else:
            print('Invalid DeviceID. Range is from 1 to 15')

    def UpdateInputStatus(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        InputStatusCmdString = b'\x48\x3A' + self._DeviceID + b'\x52\x00\x00\x00\x00\x00\x00\x00\x00\xD5\x45\x44'
        res = self.__UpdateHelper('InputStatus', InputStatusCmdString, value, qualifier)
        if res:
            try:
                count = 0
                for i in range(4, 12):
                    self.WriteStatus('InputStatus', ValueStateValues[res[i]], {'Input': str(i - 3)})
                    if ValueStateValues[res[i]] == 'On':
                        count = count + 1
                if count == 8:
                    self.WriteStatus('InputStatus', 'On', {'Input': 'All'})
                else:
                    self.WriteStatus('InputStatus', 'Off', {'Input': 'All'})
            except (KeyError, IndexError):
                self.Error(['Input Status: Invalid/unexpected response'])

    def SetRelay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        relay = qualifier['Relay Number']
        if relay in ['1', '2', '3', '4', '5', '6', '7', '8', 'All']:
            if relay == 'All' and value == 'On':
                RelayCmdString = b'\x48\x3A' + self._DeviceID + b'\x57\x01\x01\x01\x01\x01\x01\x01\x01\xE2\x45\x44'
            elif relay == 'All' and value == 'Off':
                RelayCmdString = b'\x48\x3A' + self._DeviceID + b'\x57\x00\x00\x00\x00\x00\x00\x00\x00\xDA\x45\x44'
            else:
                RelayCmdString = b'\x48\x3A' + self._DeviceID + pack('>BB', 0x70, int(relay)) + ValueStateValues[value] + b'\x00\x00\x45\x44'
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        RelayCmdString = b'\x48\x3A' + self._DeviceID + b'\x53\x00\x00\x00\x00\x00\x00\x00\x00\xD6\x45\x44'
        res = self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)
        if res:
            try:
                count = 0
                for i in range(4, 12):
                    self.WriteStatus('Relay', ValueStateValues[res[i]], {'Relay Number': str(i - 3)})
                    if ValueStateValues[res[i]] == 'On':
                        count = count + 1
                if count == 8:
                    self.WriteStatus('Relay', 'On', {'Relay Number': 'All'})
                else:
                    self.WriteStatus('Relay', 'Off', {'Relay Number': 'All'})
            except (KeyError, IndexError):
                self.Error(['Relay: Invalid/unexpected response'])

    def SetRelayPulse(self, value, qualifier):

        relay = qualifier['Relay Number']
        if 0 <= value <= 999 and 1 <= int(relay) <= 8:
            RelayPulseCmdString = b'\x48\x3A' + self._DeviceID + pack('>BBBHBB', 0x70, int(relay), 0x01, value, 0x45, 0x44)
            self.__SetHelper('RelayPulse', RelayPulseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelayPulse')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x44')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = res

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x44')
            if not res:
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

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
