from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'ChannelStep': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Source': { 'Status': {}},
            'VolumeStep': { 'Status': {}},
        }
                        
        self.deliRegEx = {
            'Power':  compile(b'(PowerStatus : On\n|3333333333333222222\r\r\n)'),
            'Source': compile(b'Source Status : (AV|YPBPR|VGA|HDMI[1-4]?|OPS|Android)\n'),
        }

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x69\x37\x5F'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x69\xC4\xD2',
            'Down': b'\x69\xC5\xD1',
        }

        ChannelStepCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x89\x55\x06\x1B'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x69\x95\x01',
            '1': b'\x69\x92\x04',
            '2': b'\x69\xA2\xF4',
            '3': b'\x69\xB2\xE4',
            '4': b'\x69\x93\x03',
            '5': b'\x69\xA3\xF3',
            '6': b'\x69\xB3\xE3',
            '7': b'\x69\x94\x02',
            '8': b'\x69\xA4\xF2',
            '9': b'\x69\xB4\xE2',
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':     b'\x69\x46\x50',
            'Down':   b'\x69\x43\x53',
            'Left':   b'\x69\x63\x33',
            'Right':  b'\x69\x66\x30',
            'Menu':   b'\x69\x80\x16',
            'Enter':  b'\x69\x07\x8F',
            'Source': b'\x69\x19\x7D',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':  b'\x69\x53\x43',
            'Off': b'\x69\x76\x20',
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\x79\x33\x53'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = 'On' if res.decode()[0] == 'P' else 'Off'
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetSource(self, value, qualifier):

        ValueStateValues = {
            'AV':       b'\x89\x55\x0D\x14',
            'YPbPr':    b'\x89\x55\x04\x1D',
            'VGA':      b'\x89\x65\x03\x0E',
            'HDMI':     b'\x89\x65\x0E\x03',
            'HDMI 1':   b'\x89\x65\x05\x0C',
            'HDMI 2':   b'\x89\x65\x07\x0A',
            'HDMI 3':   b'\x89\x65\x09\x08',
            'HDMI 4':   b'\x89\x65\x0B\x06',
            'OPS':      b'\x89\x65\x0D\x04',
            'Android':  b'\x89\x65\x06\x0B',
        }

        SourceCmdString = ValueStateValues[value]
        self.__SetHelper('Source', SourceCmdString, value, qualifier)

    def UpdateSource(self, value, qualifier):

        ValueStateValues = {
            'AV':      'AV',
            'YPBPR':   'YPbPr',
            'VGA':     'VGA',
            'HDMI':    'HDMI',
            'HDMI1':   'HDMI 1',
            'HDMI2':   'HDMI 2',
            'HDMI3':   'HDMI 3',
            'HDMI4':   'HDMI 4',
            'OPS':     'OPS',
            'Android': 'Android',
        }

        SourceCmdString = b'\x69\x18\x7E'
        res = self.__UpdateHelper('Source', SourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res.decode()[16:-1]]
                self.WriteStatus('Source', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Source: Invalid/unexpected response'])

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x69\x82\x14',
            'Down': b'\x69\x85\x11',
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True



        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x0A')
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.deliRegEx[command])
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

