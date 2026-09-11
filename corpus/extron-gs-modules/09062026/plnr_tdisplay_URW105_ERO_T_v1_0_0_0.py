from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Zone'], 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Input': {'Parameters':['Zone'], 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MultiSourceView': { 'Status': {}},
            'PIPPosition': { 'Status': {}},
            'PIPSize': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'ASPECT\((ZONE\.1|ZONE\.2)\):(AUTO|16X9|4X3|FILL|NATIVE|LETTERBOX)\r'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'AUDIO\.MUTE:(ON|OFF)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'SOURCE\.SELECT\((ZONE\.1|ZONE\.2)\):(OPS|HDMI\.1|HDMI\.2|DP|DP\.2|USBC)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'MULTI\.VIEW:(SINGLE|DUAL|PIP)\r'), self.__MatchMultiSourceView, None)
            self.AddMatchString(re.compile(b'LAYOUT\(PIP\):(PIP\.UL|PIP\.UR|PIP\.LL|PIP\.LR)\r'), self.__MatchPIPPosition, None)
            self.AddMatchString(re.compile(b'PIP\.SIZE:(SMALL|MEDIUM|LARGE)\r'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'DISPLAY\.POWER:(ON|OFF)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'AUDIO\.VOLUME:(100|[1-9][0-9]|[0-9])\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'!ERR ([1-6])\r'), self.__MatchError, None)

    def SetAspectRatio(self, value, qualifier):

        ZoneStates = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            'Broadcast': 'ALL'
        }

        ValueStateValues = {
            'Auto': 'AUTO',
            '16:9': '16X9',
            '4:3': '4X3',
            'Fill': 'FILL',
            'Native': 'NATIVE',
            'LetterBox': 'LETTERBOX'
        }

        if qualifier['Zone'] in ZoneStates and value in ValueStateValues:
            AspectRatioCmdString = 'ASPECT({})={}\r'.format(ZoneStates[qualifier['Zone']], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        ZoneStates = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            'Broadcast': 'ALL'
        }

        if qualifier['Zone'] in ZoneStates and qualifier['Zone'] != 'Broadcast':
            AspectRatioCmdString = 'ASPECT({})?\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ZoneStates = {
            'ZONE.1': '1',
            'ZONE.2': '2'
        }

        ValueStateValues = {
            'AUTO': 'Auto',
            '16X9': '16:9',
            '4X3': '4:3',
            'FILL': 'Fill',
            'NATIVE': 'Native',
            'LETTERBOX': 'LetterBox'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'AUDIO.MUTE={}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'AUDIO.MUTE?\r'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetInput(self, value, qualifier):

        ZoneStates = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            'Broadcast': 'ALL'
        }

        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI 1': 'HDMI.1',
            'HDMI 2': 'HDMI.2',
            'DisplayPort 1': 'DP',
            'DisplayPort 2': 'DP.2',
            'USB-C': 'USBC'
        }

        if qualifier['Zone'] in ZoneStates and value in ValueStateValues:
            InputCmdString = 'SOURCE.SELECT({})={}\r'.format(ZoneStates[qualifier['Zone']], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ZoneStates = {
            '1': 'ZONE.1',
            '2': 'ZONE.2',
            'Broadcast': 'ALL'
        }

        if qualifier['Zone'] in ZoneStates and qualifier['Zone'] != 'Broadcast':
            InputCmdString = 'SOURCE.SELECT({})?\r'.format(ZoneStates[qualifier['Zone']])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ZoneStates = {
            'ZONE.1': '1',
            'ZONE.2': '2'
        }

        ValueStateValues = {
            'OPS': 'OPS',
            'HDMI.1': 'HDMI 1',
            'HDMI.2': 'HDMI 2',
            'DP': 'DisplayPort 1',
            'DP.2': 'DisplayPort 2',
            'USBC': 'USB-C'
        }

        qualifier = {}
        qualifier['Zone'] = ZoneStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Input', value, qualifier)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = 'KEY=KEY.{}\r'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')
    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Left': 'LEFT',
            'Right': 'RIGHT',
            'Menu': 'MENU',
            'Exit': 'EXIT',
            'Enter': 'ENTER'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'KEY={}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')
    def SetMultiSourceView(self, value, qualifier):

        ValueStateValues = {
            'Single View': 'SINGLE',
            'PiP': 'PIP',
            'Dual View': 'DUAL'
        }

        if value in ValueStateValues:
            MultiSourceViewCmdString = 'MULTI.VIEW={}\r'.format(ValueStateValues[value])
            self.__SetHelper('MultiSourceView', MultiSourceViewCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultiSourceView')

    def UpdateMultiSourceView(self, value, qualifier):

        MultiSourceViewCmdString = 'MULTI.VIEW?\r'
        self.__UpdateHelper('MultiSourceView', MultiSourceViewCmdString, value, qualifier)

    def __MatchMultiSourceView(self, match, tag):

        ValueStateValues = {
            'SINGLE': 'Single View',
            'PIP': 'PiP',
            'DUAL': 'Dual View'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MultiSourceView', value, None)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left': 'PIP.UL',
            'Upper Right': 'PIP.UR',
            'Lower Left': 'PIP.LL',
            'Lower Right': 'PIP.LR'
        }

        if value in ValueStateValues:
            PIPPositionCmdString = 'LAYOUT(PIP)={}\r'.format(ValueStateValues[value])
            self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPosition')

    def UpdatePIPPosition(self, value, qualifier):

        PIPPositionCmdString = 'LAYOUT(PIP)?\r'
        self.__UpdateHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def __MatchPIPPosition(self, match, tag):

        ValueStateValues = {
            'PIP.UL': 'Upper Left',
            'PIP.UR': 'Upper Right',
            'PIP.LL': 'Lower Left',
            'PIP.LR': 'Lower Right'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPPosition', value, None)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': 'SMALL',
            'Medium': 'MEDIUM',
            'Large': 'LARGE'
        }

        if value in ValueStateValues:
            PIPSizeCmdString = 'PIP.SIZE={}\r'.format(ValueStateValues[value])
            self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPSize')

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = 'PIP.SIZE?\r'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            'SMALL': 'Small',
            'MEDIUM': 'Medium',
            'LARGE': 'Large'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = 'PIP.SWAP\r'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'ON',
            'Off': 'OFF'
        }

        if value in ValueStateValues:
            PowerCmdString = 'DISPLAY.POWER={}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'DISPLAY.POWER?\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'AUDIO.VOLUME={}\r'.format(str(value))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'AUDIO.VOLUME?\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorStateValues = {
            '1': 'Invalid syntax',
            '3': 'Command not recognized',
            '4': 'Invalid modifier',
            '5': 'Invalid operands',
            '6': 'Invalid operator'
        }

        value = ErrorStateValues[match.group(1).decode()]
        self.Error(['Error: {}'.format(value)])

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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break
                    
        if index: 
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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