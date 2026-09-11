from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelDiscreteCommand': {'Status': {}},
            'ChannelStep': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'ClosedCaptionAnalog': {'Status': {}},
            'ClosedCaptionDigital': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 9:
            self._DeviceID = int(value)
        else:
            self.Error(['Invalid Device ID Parameter.'])

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'M',
            'Off': 'X'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = '>{}V{}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetChannelDiscreteCommand(self, value, qualifier):

        channel = value

        if channel:
            channel = channel.split('-')

            if 1 <= len(channel) <= 2:
                try:
                    major = int(channel[0])
                    minor = int(channel[-1])
                except ValueError:
                    self.Discard('Invalid Command for SetChannelDiscreteCommand')
                    return

                if len(channel) == 1 and major <= 9999:
                    ChannelDiscreteCommandCmdString = '>{}TC={}\r'.format(self._DeviceID, major)
                elif len(channel) == 2 and major <= 999 and minor <= 999:
                    ChannelDiscreteCommandCmdString = '>{}TC={}-{}\r'.format(self._DeviceID, major, minor)
                else:
                    self.Discard('Invalid Command for SetChannelDiscreteCommand')
                    return

                self.__SetHelper('ChannelDiscreteCommand', ChannelDiscreteCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetChannelDiscreteCommand')
        else:
            self.Discard('Invalid Command for SetChannelDiscreteCommand')

    def SetChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': 'U',
            'Down': 'D'
        }

        if value in ValueStateValues:
            ChannelStepCmdString = '>{}T{}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ChannelStep', ChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelStep')

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = '>{}Q0={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def UpdateClosedCaption(self, value, qualifier):

        ClosedCaption_ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ClosedCaptionAnalog_ValueStateValues = {
            '1': 'Caption 1',
            '2': 'Caption 2',
            '3': 'Caption 3',
            '4': 'Caption 4',
            '5': 'Text 1',
            '6': 'Text 2',
            '7': 'Text 3',
            '8': 'Text 4'
        }

        ClosedCaptionDigital_ValueStateValues = {
            '1': 'Service 1',
            '2': 'Service 2',
            '3': 'Service 3',
            '4': 'Service 4',
            '5': 'Service 5',
            '6': 'Service 6'
        }

        ClosedCaptionCmdString = '>{}SQ\r'.format(self._DeviceID)
        res = self.__UpdateHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        if res:
            try:
                value = ClosedCaption_ValueStateValues[res[3]]
                self.WriteStatus('ClosedCaption', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption: Invalid/unexpected response'])

            try:
                value = ClosedCaptionAnalog_ValueStateValues[res[4]]
                self.WriteStatus('ClosedCaptionAnalog', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Analog: Invalid/unexpected response'])

            try:
                value = ClosedCaptionDigital_ValueStateValues[res[11]]
                self.WriteStatus('ClosedCaptionDigital', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Closed Caption Digital: Invalid/unexpected response'])

    def SetClosedCaptionAnalog(self, value, qualifier):

        ValueStateValues = {
            'Caption 1': '1',
            'Caption 2': '2',
            'Caption 3': '3',
            'Caption 4': '4',
            'Text 1': '5',
            'Text 2': '6',
            'Text 3': '7',
            'Text 4': '8'
        }

        if value in ValueStateValues:
            ClosedCaptionAnalogCmdString = '>{}Q1={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionAnalog')

    def UpdateClosedCaptionAnalog(self, value, qualifier):

        self.UpdateClosedCaption(value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ValueStateValues = {
            'Service 1': '1',
            'Service 2': '2',
            'Service 3': '3',
            'Service 4': '4',
            'Service 5': '5',
            'Service 6': '6'
        }

        if value in ValueStateValues:
            ClosedCaptionDigitalCmdString = '>{}Q7={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaptionDigital')

    def UpdateClosedCaptionDigital(self, value, qualifier):

        self.UpdateClosedCaption(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Ch+Menu': '1',
            'Vol+Menu': '2',
            'Ch+Vol+Menu': '3',
            'Power': '4',
            'Setup': '5',
            'Menu': '6',
            'All': '7',
            'Setup+Menu': '8',
            'Power+Setup+Menu': '9'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '>{}S4={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19',
            '0': '10',
            '-': '99'
        }

        if value in ValueStateValues:
            KeypadCmdString = '>{}KK={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '108',
            'Down': '109',
            'Left': '107',
            'Right': '106',
            'Menu': '29',
            'Guide': '63',
            'Enter': '110',
            'Exit': '111'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = '>{}KK={}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            PowerCmdString = '>{}P{}\r'.format(self._DeviceID, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        Power_ValueStateValues = {
            'U': 'On',
            'M': 'Off'
        }

        AudioMute_ValueStateValues = {
            'M': 'On',
            'U': 'Off'
        }

        PowerCmdString = '>{}SV\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = Power_ValueStateValues[res[3]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

            try:
                value = AudioMute_ValueStateValues[res[6]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/unexpected response'])

            try:
                value = int(res[8:11])
                if 0 <= value <= 100:
                    self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = '>{}VH={}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

