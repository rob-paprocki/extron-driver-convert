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
            'DHCPSetting': { 'Status': {}},
            'PodControl': {'Parameters':['Pod'], 'Status': {}},
            'PodCurrent': {'Parameters':['Pod Number'], 'Status': {}},
            'Sequence': {'Parameters':['Direction'], 'Status': {}},
            'SequenceSwitch': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DHCP\s+:\s+(ON|OFF)(\n\r)?'), self.__MatchDHCPSetting, None)
            self.AddMatchString(re.compile(b'POD([1-4])CURRENT\r\n (\d+.\d+)A\n\r'), self.__MatchPodCurrent, None)
            self.AddMatchString(re.compile(b'ERROR: Unknown Command'), self.__MatchError, None)

    def SetDHCPSetting(self, value, qualifier):

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF'
            }

        if value in ValueStateValues:
            DHCPSettingCmdString = 'DHCP{}\r'.format(ValueStateValues[value])
            self.__SetHelper('DHCPSetting', DHCPSettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDHCPSetting')

    def UpdateDHCPSetting(self, value, qualifier):

        DHCPSettingCmdString = 'INFO\r'
        self.__UpdateHelper('DHCPSetting', DHCPSettingCmdString, value, qualifier)

    def __MatchDHCPSetting(self, match, tag):

        ValueStateValues = {
            'ON':  'On',
            'OFF': 'Off'
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DHCPSetting', value, None)

    def SetPodControl(self, value, qualifier):

        PodStates = {
            '1': 'POD1',
            '2': 'POD2',
            '3': 'POD3',
            '4': 'POD4',
            'All': 'ALL'
            }

        ValueStateValues = {
            'On':  'ON',
            'Off': 'OFF'
            }

        if qualifier['Pod'] in PodStates and value in ValueStateValues:
            PodControlCmdString = '{}{}\r'.format(PodStates[qualifier['Pod']], ValueStateValues[value])
            self.__SetHelper('PodControl', PodControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPodControl')

    def UpdatePodCurrent(self, value, qualifier):

        PodNumberStates = {
            '1': 'POD1CURRENT\r',
            '2': 'POD2CURRENT\r',
            '3': 'POD3CURRENT\r',
            '4': 'POD4CURRENT\r'
            }

        if 1 <= int(qualifier['Pod Number']) <= 4:
            PodCurrentCmdString = PodNumberStates[qualifier['Pod Number']]

            self.__UpdateHelper('PodCurrent', PodCurrentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePodCurrent')

    def __MatchPodCurrent(self, match, tag):

        qualifier = {}
        qualifier['Pod Number'] = match.group(1).decode()
        value = round(float(match.group(2).decode()))
        self.WriteStatus('PodCurrent', value, qualifier)

    def SetSequence(self, value, qualifier):

        DirectionStates = {
            'Up':   'UP',
            'Down': 'DOWN'
            }

        if qualifier['Direction'] in DirectionStates and 2 <= int(value) <= 60:
            SequenceCmdString = 'SEQ{}{}\r'.format(DirectionStates[qualifier['Direction']], value)
            self.__SetHelper('Sequence', SequenceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequence')

    def SetSequenceSwitch(self, value, qualifier):

        ValueStateValues = {
            'On':  'ACTIVATE',
            'Off': 'DEACTIVATE'
            }

        if value in ValueStateValues:
            SequenceSwitchCmdString = '{}\r'.format(ValueStateValues[value])
            self.__SetHelper('SequenceSwitch', SequenceSwitchCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequenceSwitch')

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

        self.Error([match.group(0).decode()])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()