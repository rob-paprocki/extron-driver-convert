from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog, Timer

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
        self.deviceUsername = 'admin'
        self.devicePassword = 'adminpw'
        self.Models = {
            'C3-503': self.tv1_29_1996_503,
            'C3-540': self.tv1_29_1996_540,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInputLevel': {'Parameters':['Number'], 'Status': {}},
            'AudioInputMute': {'Parameters':['Number'], 'Status': {}},
            'AudioOutputLevel': {'Parameters':['Number'], 'Status': {}},
            'AudioOutputMute': {'Parameters':['Number'], 'Status': {}},
            'ImageFlip': {'Parameters':['Type','Window'], 'Status': {}},
            'InputRoute': {'Parameters':['Slot','Window'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'SystemStatus': { 'Status': {}},
            }

        self.Authenticated = 'Needed'
            
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Slot(?:4|18).In([0-9]{1,2}).AudioLevel = (-?\d+)\r'), self.__MatchAudioInputLevel, None)
            self.AddMatchString(re.compile(b'Slot(?:4|18).In([0-9]{1,2}).AudioMute = (On|Off).?\r'), self.__MatchAudioInputMute, None)
            self.AddMatchString(re.compile(b'Slot(?:4|18).Out([0-9]{1,2}).AudioLevel = (-?\d+)\r'), self.__MatchAudioOutputLevel, None)
            self.AddMatchString(re.compile(b'Slot(?:4|18).Out([0-9]{1,2}).AudioMute = (On|Off).?\r'), self.__MatchAudioOutputMute, None)
            self.AddMatchString(re.compile(b'Window(3[0-6]|[1-2]?\d)\.(VFlip|HFlip) = (On|Off).?\r'), self.__MatchImageFlip, None)
            self.AddMatchString(re.compile(b'routing.windows.window(\d{1,2}).input = Slot(\d{1,2}).In([1-4])\r'), self.__MatchInputRoute, None)
            self.AddMatchString(re.compile(b'System\.Status = (Busy|Serving)\r'), self.__MatchSystemStatus, None)
            self.AddMatchString(re.compile(b'!Info : User [\S]+ Logged In'), self.__MatchSuccess, None)
            self.AddMatchString(re.compile(b'!Error -(129|134) '), self.__MatchError, None)

        self.AuthenticationTimer = Timer(2, self.__QueuePassword)
        
    def SetPassword(self, value, qualifier):
        if self.deviceUsername is not None and self.devicePassword is not None:
            self.Send('login({0},{1})\r'.format(self.deviceUsername, self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __QueuePassword(self, timer, count):

        self.SetPassword(None, None)

    def __MatchSuccess(self, match, tag):

        self.Authenticated = 'Admin'
        self.AuthenticationTimer.Stop()

    def SetAudioInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : -20,
            'Max' : 20
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= self.in_outMax:
            AudioInputLevelCmdString = 'Slot{0}.In{1}.AudioLevel = {2}\r'.format(self.slotVal, number_val, value)
            self.__SetHelper('AudioInputLevel', AudioInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLevel')

    def UpdateAudioInputLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax:
            AudioInputLevelCmdString = 'Slot{0}.In{1}.AudioLevel\r'.format(self.slotVal, number_val)
            self.__UpdateHelper('AudioInputLevel', AudioInputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioInputLevel')

    def __MatchAudioInputLevel(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= self.in_outMax and -20 <= int(match.group(2).decode()) <= 20:
            qualifier = {}
            qualifier['Number'] = match.group(1).decode()
            value = int(match.group(2).decode())
            self.WriteStatus('AudioInputLevel', value, qualifier)

    def SetAudioInputMute(self, value, qualifier):

        ValueStateValues = ['On', 'Off']
        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax and value in ValueStateValues:
            AudioInputMuteCmdString = 'Slot{0}.In{1}.AudioMute = {2}\r'.format(self.slotVal, number_val, value)
            self.__SetHelper('AudioInputMute', AudioInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputMute')

    def UpdateAudioInputMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax:
            AudioInputMuteCmdString = 'Slot{0}.In{1}.AudioMute\r'.format(self.slotVal, number_val)
            self.__UpdateHelper('AudioInputMute', AudioInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioInputMute')

    def __MatchAudioInputMute(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= self.in_outMax:
            qualifier = {}
            qualifier['Number'] = match.group(1).decode()
            value = match.group(2).decode()
            self.WriteStatus('AudioInputMute', value, qualifier)

    def SetAudioOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min' : -20,
            'Max' : 20
            }

        number_val = qualifier['Number']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(number_val) <= self.in_outMax:
            AudioOutputLevelCmdString = 'Slot{0}.Out{1}.AudioLevel = {2}\r'.format(self.slotVal, number_val, value)
            self.__SetHelper('AudioOutputLevel', AudioOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLevel')

    def UpdateAudioOutputLevel(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax:
            AudioOutputLevelCmdString = 'Slot{0}.Out{1}.AudioLevel\r'.format(self.slotVal, number_val)
            self.__UpdateHelper('AudioOutputLevel', AudioOutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputLevel')
            
    def __MatchAudioOutputLevel(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= self.in_outMax and -20 <= int(match.group(2).decode()) <= 20:
            qualifier = {}
            qualifier['Number'] = match.group(1).decode()
            value = int(match.group(2).decode())
            self.WriteStatus('AudioOutputLevel', value, qualifier)

    def SetAudioOutputMute(self, value, qualifier):

        ValueStateValues = ['On', 'Off']
        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax and value in ValueStateValues:
            AudioOutputMuteCmdString = 'Slot{0}.Out{1}.AudioMute = {2}\r'.format(self.slotVal, number_val, value)
            self.__SetHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputMute')

    def UpdateAudioOutputMute(self, value, qualifier):

        number_val = qualifier['Number']
        if 1 <= int(number_val) <= self.in_outMax:
            AudioOutputMuteCmdString = 'Slot{0}.Out{1}.AudioMute\r'.format(self.slotVal, number_val)
            self.__UpdateHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputMute')

    def __MatchAudioOutputMute(self, match, tag):

        if 1 <= int(match.group(1).decode()) <= self.in_outMax:
            qualifier = {}
            qualifier['Number'] = match.group(1).decode()
            value = match.group(2).decode()
            self.WriteStatus('AudioOutputMute', value, qualifier)

    def SetImageFlip(self, value, qualifier):

        TypeStates = {
            'Vertical':   'VFlip',
            'Horizontal': 'HFlip'
            }

        ValueStateValues = ('On', 'Off')

        if qualifier['Type'] in TypeStates and 1 <= qualifier['Window'] <= 36 and value in ValueStateValues:
            ImageFlipCmdString = 'Window{}.{} = {}\r'.format(qualifier['Window'], TypeStates[qualifier['Type']], value)
            self.__SetHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetImageFlip')

    def UpdateImageFlip(self, value, qualifier):

        TypeStates = {
            'Vertical':   'VFlip',
            'Horizontal': 'HFlip'
            }

        if qualifier['Type'] in TypeStates and 1 <= qualifier['Window'] <= 36:
            ImageFlipCmdString = 'Window{}.{}\r'.format(qualifier['Window'], TypeStates[qualifier['Type']])
            self.__UpdateHelper('ImageFlip', ImageFlipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateImageFlip')

    def __MatchImageFlip(self, match, tag):

        TypeStates = {
            'VFlip': 'Vertical',
            'HFlip': 'Horizontal'
            }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(2).decode()]
        qualifier['Window'] = int(match.group(1).decode())
        value = match.group(3).decode()
        self.WriteStatus('ImageFlip', value, qualifier)

    def SetInputRoute(self, value, qualifier):

        WindowConstraints = {
            'Min' : 1,
            'Max' : 36
            }

        slotNum = qualifier['Slot']
        windowNum = qualifier['Window']
        if 1 <= int(slotNum) <= self.slotMax and WindowConstraints['Min'] <= windowNum <= WindowConstraints['Max'] and 1 <= int(value) <= 4:
            InputRouteCmdString = 'routing.windows.window{0}.input = Slot{1}.In{2}\r'.format(windowNum, slotNum, value)
            self.__SetHelper('InputRoute', InputRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputRoute')

    def UpdateInputRoute(self, value, qualifier):

        WindowConstraints = {
            'Min' : 1,
            'Max' : 36
            }

        slotNum = qualifier['Slot']
        windowNum = qualifier['Window']
        if 1 <= int(slotNum) <= self.slotMax and WindowConstraints['Min'] <= windowNum <= WindowConstraints['Max']:
            InputRouteCmdString = 'routing.windows.window{}.input\r'.format(windowNum)
            self.__UpdateHelper('InputRoute', InputRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputRoute')

    def __MatchInputRoute(self, match, tag):
        
        if 1 <= int(match.group(2).decode()) <= self.slotMax:
            qualifier = {}
            qualifier['Window'] = int(match.group(1).decode())
            qualifier['Slot'] = match.group(2).decode()
            value = match.group(3).decode()
            self.WriteStatus('InputRoute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 49
            }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetRecallCmdString = 'routing.preset.take={0}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'System.Reset()\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def UpdateSystemStatus(self, value, qualifier):

        SystemStatusCmdString = 'System.Status\r'
        self.__UpdateHelper('SystemStatus', SystemStatusCmdString, value, qualifier)

    def __MatchSystemStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemStatus', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated == 'Admin':
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
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        self.counter = 0

        if match.group(1).decode() == '134':
            self.Error(['Error -134 : UNAUTHORISED - Insufficient Permission'])
        elif match.group(1).decode() == '129':
            self.Authenticated = 'Needed'
            self.Error(['Error -129 : UNAUTHORISED - Not Logged In or Login Failed'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'Needed'
        self.AuthenticationTimer = Timer(2, self.__QueuePassword)
        
    def tv1_29_1996_503(self):

        self.slotMax = 3
        self.slotVal = 4    # Audio Slot
        self.in_outMax = 4

    def tv1_29_1996_540(self):

        self.slotMax = 16
        self.slotVal = 18   # Audio Slot
        self.in_outMax = 28

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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