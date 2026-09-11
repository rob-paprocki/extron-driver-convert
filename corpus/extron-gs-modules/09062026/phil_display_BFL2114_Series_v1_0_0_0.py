from extronlib.interface import SerialInterface, EthernetClientInterface
from functools import reduce
from operator import xor
import re
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False

        self.Models = {
            '50BFL2114/12': self.phil_10_5279_other,
            '58BFL2114/12': self.phil_10_5279_other,
            '65BFL2114/12': self.phil_10_5279_other,
            '70BFL2114/12': self.phil_10_5279_other,
            '75BFL2114/12': self.phil_10_5279_75,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.set_regex = re.compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:\x00\x16|\x01\x17|\x02\x14)\xA5\xA5')
        self.get_regex = {
            'Power': re.compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                   br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x18'
                                   br'[\x00-\x03][\x38-\x3B])\xA5\xA5'),
            'Input': re.compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                   br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\xAC'
                                   br'[\x01\x08-\x0B][\x00-\xFF])\xA5\xA5'),
            'Volume': re.compile(br'\x0E\x0D\x00\x00\x05\x04\x00\x0C\x16(?:(?:\x01\x17|\x02\x14)|'
                                   br'\x00\x16\xA5\xA5\x0E\x0E\x00\x00\x05\x05\x00\x0C\x22\x44'
                                   br'[\x00-\x64][\x00-\xFF])\xA5\xA5'),
        }

    def _createstring(self, payload):
        payload.append(reduce(xor, payload))
        result = [0x0E, len(payload) + 10, 0, 0, 5, len(payload) + 1, 0, 0x0C]
        result.extend(payload)
        result.extend([0xA5, 0xA5])
        return bytes(result)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        if value in ValueStateValues:
            payload = [0x20, 0x46, ValueStateValues[value]]
            AudioMuteCmdString = self._createstring(payload)
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 1,
            'Down': 2
        }

        if value in ValueStateValues:
            payload = [0x20, 0x1B, 0xFF, 0xFF, 0xFF, ValueStateValues[value], 0xFF]
            ChannelCmdString = self._createstring(payload)
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def SetInput(self, value, qualifier):

        if value in self.SetSource:
            payload = [0x20, 0xAC, self.SetSource[value]]
            InputCmdString = self._createstring(payload)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        payload = [0x21, 0xAC]
        InputCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = self.GetSource[res[23]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        if value in ValueStateValues:
            payload = [0x20, 0x18, ValueStateValues[value]]
            PowerCmdString = self._createstring(payload)
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off',
            3: 'Cooling Down',
            2: 'Warming Up'
        }

        payload = [0x21, 0x18]
        PowerCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[23]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            payload = [0x20, 0x44, value]
            VolumeCmdString = self._createstring(payload)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        payload = [0x21, 0x44]
        VolumeCmdString = self._createstring(payload)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[23]
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        Error_codes = {
            0x01: 'NACK: payload checksum failure or a malformed payload.',
            0x02: 'NAV: command received is not implemented by the TV set.'
        }
        if response and response[9] in Error_codes:
            self.Error(['{} command error: {}'.format(sourceCmdName, Error_codes[response[9]])])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex[command])
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

    def phil_10_5279_other(self):

        self.SetSource = {
            'Main Tuner': 1,
            'HDMI 1':     8,
            'HDMI 2':     9,
            'USB':        11,
        }

        self.GetSource = {
            1:  'Main Tuner',
            8:  'HDMI 1',
            9:  'HDMI 2',
            11: 'USB',
        }

    def phil_10_5279_75(self):

        self.SetSource = {
            'Main Tuner': 1,
            'HDMI 1':     8,
            'HDMI 2':     9,
            'HDMI 3':     10,
            'USB':        11,
        }

        self.GetSource = {
            1:  'Main Tuner',
            8:  'HDMI 1',
            9:  'HDMI 2',
            10: 'HDMI 3',
            11: 'USB',
        }

    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}
        
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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