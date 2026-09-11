from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
            'CompositionOutput': {'Parameters':['Type','Transition'], 'Status': {}},
            'ConnectorSelection': {'Parameters':['Type'], 'Status': {}},
            'DeviceVersion': { 'Status': {}},
            'Fade': {'Parameters':['Type'], 'Status': {}},
            'HDMIOutputSelection': {'Parameters':['Type','Transition'], 'Status': {}},
            'MemoryRecall': { 'Status': {}},
            'StillMemorySelection': {'Parameters':['Type'], 'Status': {}},
            }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x02VER:V-1200HD,([\s\S]+),[\s\S]+;'), self.__MatchDeviceVersion, None)
            self.AddMatchString(re.compile(b'\x02ERR:(0|2|5|6);'), self.__MatchError, None)

    def SetCompositionOutput(self, value, qualifier):

        TypeStates = {
            'Composition 1' : '1', 
            'Composition 2' : '2', 
            'Composition 3' : '3', 
            'Composition 4' : '4'
        }

        TransitionStates = {
            'Cut'       : '0', 
            'Auto Mix'  : '1', 
            'Auto Wipe' : '2'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        Type = qualifier['Type']
        Transition = qualifier['Transition']
        if Type in TypeStates and Transition in TransitionStates:
            CompositionOutputCmdString = '\x02CP{0}:{1},{2};'.format(TypeStates[Type], TransitionStates[Transition], ValueStateValues[value]).encode()
            self.__SetHelper('CompositionOutput', CompositionOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCompositionOutput')

    def SetConnectorSelection(self, value, qualifier):

        TypeStates = {
            'M/E 1 PGM'           : 'PM1', 
            'M/E 1 PST'           : 'PT1', 
            'M/E 2 PGM'           : 'PM2', 
            'M/E 2 PST'           : 'PT2', 
            'Composition 1 Input' : 'CS1', 
            'Composition 2 Input' : 'CS2', 
            'Composition 3 Input' : 'CS3', 
            'Composition 4 Input' : 'CS4'
        }

        ValueStateValues = {
            'SDI 1'    : '0', 
            'SDI 2'    : '1', 
            'SDI 3'    : '2', 
            'SDI 4'    : '3', 
            'SDI 5'    : '4', 
            'SDI 6'    : '5', 
            'SDI 7'    : '6', 
            'SDI 8'    : '7', 
            'SDI 9'    : '8', 
            'SDI 10'   : '9', 
            'HDMI 1'   : '10', 
            'HDMI 2'   : '11', 
            'HDMI 3'   : '12', 
            'HDMI 4'   : '13', 
            'STILL 1'  : '14', 
            'STILL 2'  : '15', 
            'EXP 1'    : '16', 
            'EXP 2'    : '17', 
            'RE-ENTRY' : '18', 
            'SIG GEN'  : '19', 
            'NONE'     : '20'
        }

        Type = qualifier['Type']
        if Type in TypeStates:
            ConnectorSelectionCmdString = '\x02{0}:{1};'.format(TypeStates[Type], ValueStateValues[value]).encode()
            self.__SetHelper('ConnectorSelection', ConnectorSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConnectorSelection')
    
    def UpdateDeviceVersion(self, value, qualifier):

        DeviceVersionCmdString = b'\x02VER;'
        self.__UpdateHelper('DeviceVersion', DeviceVersionCmdString, value, qualifier)

    def __MatchDeviceVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DeviceVersion', value, None)

    def SetFade(self, value, qualifier):

        TypeStates = {
            'HDMI 1' : '4F1:', 
            'HDMI 2' : '4F2:', 
            'BUS 1' : 'FDE:0:', 
            'BUS 2' : 'FDE:1:', 
            'BUS 3' : 'FDE:2:', 
            'BUS 4' : 'FDE:3:', 
            'BUS 5' : 'FDE:4:', 
            'BUS 6' : 'FDE:5:'
        }

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        Type = qualifier['Type']
        FadeCmdString = '\x02{0}{1};'.format(TypeStates[Type], ValueStateValues[value]).encode()
        self.__SetHelper('Fade', FadeCmdString, value, qualifier)

    def SetHDMIOutputSelection(self, value, qualifier):

        TypeStates = {
            'HDMI 1' : '1', 
            'HDMI 2' : '2'
        }

        TransitionStates = {
            'Cut' : '0', 
            'Mix' : '1'
        }

        ValueStateValues = {
            'XTP 1' : '0', 
            'XTP 2' : '1', 
            'XTP 3' : '2', 
            'XTP 4' : '3'
        }

        Type = qualifier['Type']
        Transition = qualifier['Transition']
        if Type in TypeStates and Transition in TransitionStates:
            HDMIOutputSelectionCmdString = '\x024X{0}:{1},{2};'.format(TypeStates[Type], ValueStateValues[value], TransitionStates[Transition]).encode()
            self.__SetHelper('HDMIOutputSelection', HDMIOutputSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIOutputSelection')

    def SetMemoryRecall(self, value, qualifier):

        ValueStateValues = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3', 
            '5' : '4', 
            '6' : '5', 
            '7' : '6', 
            '8' : '7'
        }

        MemoryRecallCmdString = '\x02MEM:{0};'.format(ValueStateValues[value]).encode()
        self.__SetHelper('MemoryRecall', MemoryRecallCmdString, value, qualifier)

    def SetStillMemorySelection(self, value, qualifier):

        TypeStates = {
            'STILL 1' : '1', 
            'STILL 2' : '2'
        }

        ValueStateValues = {
            '1' : '0', 
            '2' : '1', 
            '3' : '2', 
            '4' : '3', 
            '5' : '4', 
            '6' : '5', 
            '7' : '6', 
            '8' : '7', 
            '9' : '8', 
            '10' : '9', 
            '11' : '10', 
            '12' : '11', 
            '13' : '12', 
            '14' : '13', 
            '15' : '14', 
            '16' : '15'
        }

        Type = qualifier['Type']
        if Type in TypeStates:
            StillMemorySelectionCmdString = '\x02ST{0}:{1};'.format(TypeStates[Type], ValueStateValues[value]).encode()
            self.__SetHelper('StillMemorySelection', StillMemorySelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStillMemorySelection')

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

        State = {
            '0' : 'The received command contains an error.',
            '2' : 'In a busy state.',
            '5' : 'An argument of the received command is out of range.',
            '6' : 'The system is in a mode in which the received command cannot be executed.',
        }

        value = State[match.group(1).decode()]
        self.Error([value])

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
