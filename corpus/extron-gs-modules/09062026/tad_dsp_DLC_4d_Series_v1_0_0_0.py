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
            'InputGain': {'Parameters':['Channel'], 'Status': {}},
            'OutputGain': {'Parameters':['Channel'], 'Status': {}},
            'OutputMute': {'Parameters':['Channel'], 'Status': {}},
            'Power': { 'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\+IN-([1-3]0[0-3])\.GAIN ([-\d.]+)'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'\+OUT-([1-4])\.GAIN ([-\d.]+)'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'\+OUT-([1-4])\.MUTE ([01])'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'\+SYSTEM\.STATUS\.STATE \"(INIT|STANDBY|ON|FAULT)\"'), self.__MatchPower, None)

    def SetInputGain(self, value, qualifier):

        ChannelStates = {
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102',
            'Analog Input 4': '103',
            'SPDIF (Left)'  : '200',
            'SPDIF (Right)' : '201',
            'Dante 1'       : '300',
            'Dante 2'       : '301',
            'Dante 3'       : '302',
            'Dante 4'       : '303'
        }

        if qualifier['Channel'] in ChannelStates and -15.0 <= value <= 15.0:
            value = round(value, 1)
            value = 0.0 if value == -0.0 else value
            InputGainCmdString = 'SET IN-{0}.GAIN {1}\n'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        ChannelStates = {
            'Analog Input 1': '100',
            'Analog Input 2': '101',
            'Analog Input 3': '102',
            'Analog Input 4': '103',
            'SPDIF (Left)'  : '200',
            'SPDIF (Right)' : '201',
            'Dante 1'       : '300',
            'Dante 2'       : '301',
            'Dante 3'       : '302',
            'Dante 4'       : '303'
        }

        if qualifier['Channel'] in ChannelStates:
            InputGainCmdString = 'GET IN-{0}.GAIN\n'.format(ChannelStates[qualifier['Channel']])
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        ChannelStates = {
            '100' : 'Analog Input 1',
            '101' : 'Analog Input 2',
            '102' : 'Analog Input 3',
            '103' : 'Analog Input 4',
            '200' : 'SPDIF (Left)',
            '201' : 'SPDIF (Right)',
            '300' : 'Dante 1',
            '301' : 'Dante 2',
            '302' : 'Dante 3',
            '303' : 'Dante 4'
        }

        qualifier = {'Channel' : ChannelStates[match.group(1).decode()]}
        value = float(match.group(2).decode())
        if -15.0 <= value <= 15.0:
            self.WriteStatus('InputGain', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4 and -30.0 <= value <= 15.0:
            value = round(value, 1)
            value = 0.0 if value == -0.0 else value
            OutputGainCmdString = 'SET OUT-{0}.GAIN {1}\n'.format(qualifier['Channel'], value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4:
            OutputGainCmdString = 'GET OUT-{0}.GAIN\n'.format(qualifier['Channel'])
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Channel' : match.group(1).decode()}
        value = float(match.group(2).decode())
        if -30.0 <= value <= 15.0:
            self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        if 1 <= int(qualifier['Channel']) <= 4 and value in ValueStateValues:
            OutputMuteCmdString = 'SET OUT-{0}.MUTE {1}\n'.format(qualifier['Channel'], ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 4:
            OutputMuteCmdString = 'GET OUT-{0}.MUTE\n'.format(qualifier['Channel'])
            self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Channel' : match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'POWER_ON\n',
            'Off' : 'POWER_OFF\n'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'GET SYSTEM.STATUS.STATE\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'ON'        : 'On',
            'STANDBY'   : 'Off',
            'INIT'      : 'Initializing',
            'FAULT'     : 'Fault'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

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