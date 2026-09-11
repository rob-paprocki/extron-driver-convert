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
        self._Address = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogPad': {'Status': {}},
            'AnalogPadStatus': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'LED': {'Status': {}},
            'Mute': {'Status': {}},
            'MuteStatus': {'Status': {}},
            'RemotePower': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def Address(self):
        return self._Address

    @Address.setter
    def Address(self, value):
        if len(value) == 8:
            checkFormat = re.search(re.compile('[0-9A-Fa-f]{2}([:-][0-9A-Fa-f]{2}){2}'), value)
            if checkFormat:
                self._Address = bytes.fromhex(value.replace(':', '').replace('-', ''))
            else:
                print('Address Parameter does not have correct format. Example:   00:01:CC   or 00-01-CC')
        else:
            print('Address Parameter must have length of 8. Example:   00:01:CC   or 00-01-CC')

    def SetAnalogPad(self, value, qualifier):

        AnalogPadCmdString = b'\xAA' + self._Address + b'\x02\x17\xCC'
        self.__SetHelper('AnalogPad', AnalogPadCmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x0B',
            'Off': b'\x02\x0C'
        }

        ButtonLockCmdString = b'\xAA' + self._Address + ValueStateValues[value] + b'\xCC'
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def SetLED(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x07',
            'Off': b'\x02\x08'
        }

        LEDCmdString = b'\xAA' + self._Address + ValueStateValues[value] + b'\xCC'
        self.__SetHelper('LED', LEDCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\xAA' + self._Address + b'\x02\x16\xCC'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateAnalogPadStatus(self, value, qualifier):
        self.UpdateMuteStatus(value, qualifier)

    def UpdateButtonLock(self, value, qualifier):
        self.UpdateMuteStatus(value, qualifier)

    def UpdateLED(self, value, qualifier):
        self.UpdateMuteStatus(value, qualifier)

    def UpdateRemotePower(self, value, qualifier):
        self.UpdateMuteStatus(value, qualifier)

    def UpdateVolume(self, value, qualifier):
        self.UpdateMuteStatus(value, qualifier)

    def UpdateMuteStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteStatusCmdString = b'\xAA' + self._Address + b'\x01\x02\xCC'
        res = self.__UpdateHelper('MuteStatus', MuteStatusCmdString, value, qualifier)
        if res:
            try:
                value = format(res[-2], '#010b')
                value = ValueStateValues[value[-1]]
                self.WriteStatus('MuteStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mute Status: Invalid/unexpected response'])

            try:
                value = format(res[-2], '#010b')
                value = ValueStateValues[value[-2]]
                self.WriteStatus('AnalogPadStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Analog Pad Status: Invalid/unexpected response'])

            try:
                value = format(res[-2], '#010b')
                value = ValueStateValues[value[-3]]
                self.WriteStatus('RemotePower', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Remote Power: Invalid/unexpected response'])

            try:
                value = format(res[-2], '#010b')
                value = ValueStateValues[value[-5]]
                self.WriteStatus('LED', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LED: Invalid/unexpected response'])

            try:
                value = format(res[-2], '#010b')
                value = ValueStateValues[value[-8]]
                self.WriteStatus('ButtonLock', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Button Lock: Invalid/unexpected response'])

            try:
                value = (res[-3] - 0xC8) / 2
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetRemotePower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02\x12',
            'Off': b'\x02\x13'
        }

        RemotePowerCmdString = b'\xAA' + self._Address + ValueStateValues[value] + b'\xCC'
        self.__SetHelper('RemotePower', RemotePowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\xAA' + self._Address + pack('>3B', 0x06, int(0xC8 + (2 * value)), 0xCC)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xCC')
            if not res:
                self.Error(['{0}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\xCC')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model=None):
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
