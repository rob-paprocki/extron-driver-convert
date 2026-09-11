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
        self.Models = {
            'iSound 1616D': self.infb_25_16925_16,
            'iSound 44D': self.infb_25_16925_4,
            'iSound 88D': self.infb_25_16925_8,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputGain': {'Parameters':['Input'], 'Status': {}},
            'InputLevel': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputGain': {'Parameters':['Output'], 'Status': {}},
            'OutputLevel': {'Parameters':['Output'], 'Status': {}},
            'OutputMute': {'Parameters':['Output'], 'Status': {}},
            'Scene': {'Parameters':['Type'], 'Status': {}},
            'SystemMute': { 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'get:input#gain#0-\d{1,2}#([#\-\d]+)'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'get:input#level#0-\d{1,2}#([#\-.\d]+)'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'get:input#mute#0-\d{1,2}#([#01]+)'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'get:output#gain#0-\d{1,2}#([#\-\d]+)'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'get:output#level#0-\d{1,2}#([#\-.\d]+)'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'get:output#mute#0-\d{1,2}#([#01]+)'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'get:sysctl#mute#([01])'), self.__MatchSystemMute, None)

    def SetInputGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.size and -72 <= value <= 12:
            InputGainCmdString = 'set:input#gain#{0}#{1}\r'.format(int(qualifier['Input']) - 1, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.size:
            InputGainCmdString = 'get:input#gain#0-{}\r'.format(self.size - 1)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        gain_list = match.group(1).decode().split('#')
        for gain in range(0, len(gain_list)):
            value = int(gain_list[gain])
            if -72 <= value <= 12:
                self.WriteStatus('InputGain', value, {'Input' : str(gain + 1)})

    def UpdateInputLevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.size:
            InputLevelCmdString = 'get:input#level#0-{}\r'.format(self.size - 1)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        level_list = match.group(1).decode().split('#')
        for level in range(0, len(level_list)):
            value = float(level_list[level])
            self.WriteStatus('InputLevel', value, {'Input' : str(level + 1)})

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Input']) <= self.size and value in ValueStateValues:
            InputMuteCmdString = 'set:input#mute#{0}#{1}\r'.format(int(qualifier['Input']) - 1, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.size:
            InputMuteCmdString = 'get:input#mute#0-{}\r'.format(self.size - 1)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        mute_list = match.group(1).decode().split('#')
        for mute in range(0, len(mute_list)):
            value = ValueStateValues[mute_list[mute]]
            self.WriteStatus('InputMute', value, {'Input' : str(mute + 1)})

    def SetMatrixTieCommand(self, value, qualifier):

        ValueStateValues = {
            'Open'  : '1',
            'Close' : '0'
        }

        if 1 <= int(qualifier['Input']) <= self.size and 1 <= int(qualifier['Output']) <= self.size and value in ValueStateValues:
            MatrixTieCommandCmdString = 'set:mixer#switch#{0}#{1}#{2}\r'.format(int(qualifier['Input']) - 1, int(qualifier['Output']) - 1, ValueStateValues[value])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetOutputGain(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.size and -72 <= value <= 12:
            OutputGainCmdString = 'set:output#gain#{0}#{1}\r'.format(int(qualifier['Output']) - 1, value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.size:
                OutputGainCmdString = 'get:output#gain#0-{}\r'.format(self.size - 1)
                self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        gain_list = match.group(1).decode().split('#')
        for gain in range(0, len(gain_list)):
            value = int(gain_list[gain])
            if -72 <= value <= 12:
                self.WriteStatus('OutputGain', value, {'Output' : str(gain + 1)})

    def UpdateOutputLevel(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.size:
            OutputLevelCmdString = 'get:output#level#0-{}\r'.format(self.size - 1)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        level_list = match.group(1).decode().split('#')
        for level in range(0, len(level_list)):
            value = float(level_list[level])
            self.WriteStatus('OutputLevel', value, {'Output' : str(level + 1)})

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Output']) <= self.size and value in ValueStateValues:
            OutputMuteCmdString = 'set:output#mute#{0}#{1}\r'.format(int(qualifier['Output']) - 1, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.size:
            OutputMuteCmdString = 'get:output#mute#0-{}\r'.format(self.size - 1)
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        mute_list = match.group(1).decode().split('#')
        for mute in range(0, len(mute_list)):
            value = ValueStateValues[mute_list[mute]]
            self.WriteStatus('OutputMute', value, {'Output' : str(mute + 1)})

    def SetScene(self, value, qualifier):

        TypeStates = {
            'Recall' : 'toggle',
            'Save'   : 'save'
        }

        if qualifier['Type'] in TypeStates and 1 <= int(value) <= 16:
            SceneCmdString = 'scene:{0}#{1}\r'.format(TypeStates[qualifier['Type']], int(value) - 1)
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def SetSystemMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues:
            SystemMuteCmdString = 'set:sysctl#mute#{}\r'.format(ValueStateValues[value])
            self.__SetHelper('SystemMute', SystemMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSystemMute')

    def UpdateSystemMute(self, value, qualifier):

        SystemMuteCmdString = 'get:sysctl#mute\r'
        self.__UpdateHelper('SystemMute', SystemMuteCmdString, value, qualifier)

    def __MatchSystemMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SystemMute', value, None)

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

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def infb_25_16925_16(self):

        self.size = 16

    def infb_25_16925_4(self):

        self.size = 4

    def infb_25_16925_8(self):

        self.size = 8

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])