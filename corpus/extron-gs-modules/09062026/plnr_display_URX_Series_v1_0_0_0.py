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
            'Input': { 'Status': {}},
            'InputMode': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'MultipleInput': {'Parameters':['Input'], 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
        }
                        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\(0;INS=([04567])\)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\(0;INM=([02])\)\r'), self.__MatchInputMode, None)
            self.AddMatchString(re.compile(b'\(0;MI([1-4])=([012])\)\r'), self.__MatchMultipleInput, None)
            self.AddMatchString(re.compile(b'\(0;STA=([0-4])\)\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\(([1-9]|1[01]);(INS|INM|KEY|MI[1-4]|PSA|PSS|PWR|STA)=[\"\w ]+\)\r'), self.__MatchError, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort' : '0', 
            'HDMI 1' : '4', 
            'HDMI 2' : '5', 
            'HDMI 3' : '6', 
            'HDMI 4' : '7'
        }
        
        if value in ValueStateValues:
            InputCmdString = '(INS={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')
            
    def UpdateInput(self, value, qualifier):
        
        InputCmdString = '(INS?)\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):
       
        ValueStateValues = {
            '0': 'DisplayPort', 
            '4': 'HDMI 1', 
            '5': 'HDMI 2', 
            '6': 'HDMI 3', 
            '7': 'HDMI 4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetInputMode(self, value, qualifier):
        
        ValueStateValues = {
            'Single'  : '0', 
            'Multiple': '2'
        }
        
        if value in ValueStateValues:
            InputModeCmdString = '(INM={})\r'.format(ValueStateValues[value])
            self.__SetHelper('InputMode', InputModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMode')
            
    def UpdateInputMode(self, value, qualifier):
        
        InputModeCmdString = '(INM?)\r'
        self.__UpdateHelper('InputMode', InputModeCmdString, value, qualifier)

    def __MatchInputMode(self, match, tag):
        
        ValueStateValues = {
            '0': 'Single', 
            '2': 'Multiple'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputMode', value, None)

    def SetMenuNavigation(self, value, qualifier):
        
        ValueStateValues = {
            'Menu' : '3', 
            'Up'   : '5', 
            'Down' : '6', 
            'Left' : '7', 
            'Right': '8', 
            'Enter': '4'
        }
        
        if value in ValueStateValues:
            MenuNavigationCmdString = '(KEY={})\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMultipleInput(self, value, qualifier):
        
        InputStates = {
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4'
        }

        ValueStateValues = {
            'Input Source': '0', 
            'DisplayPort' : '1', 
            'HDMI'        : '2'
        }
        
        if value in ValueStateValues and qualifier['Input'] in InputStates:
            MultipleInputCmdString = '(MI{}={})\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('MultipleInput', MultipleInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultipleInput')
            
    def UpdateMultipleInput(self, value, qualifier):

        InputStates = {
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4'
        }
        
        if qualifier['Input'] in InputStates:
            MultipleInputCmdString = '(MI{}?)\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('MultipleInput', MultipleInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMultipleInput')

    def __MatchMultipleInput(self, match, tag):
        
        InputStates = {
            '1': '1', 
            '2': '2', 
            '3': '3', 
            '4': '4'
        }

        ValueStateValues = {
            '0': 'Input Source', 
            '1': 'DisplayPort', 
            '2': 'HDMI'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MultipleInput', value, qualifier)

    def SetPower(self, value, qualifier):
        
        ValueStateValues = {
            'On' : '1', 
            'Off': '0'
        }
        
        if value in ValueStateValues:
            PowerCmdString = '(PWR={})\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
            
    def UpdatePower(self, value, qualifier):      

        PowerCmdString = '(STA?)\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):
        
        ValueStateValues = {
            '2' : 'On', 
            '0' : 'Off', 
            '1' : 'Powering Up', 
            '3' : 'Powering Down', 
            '4' : 'Error'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):
        
        if 0 <= int(value) <= 7:
            PresetRecallCmdString = '(PSA={})\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):
        
        if 0 <= int(value) <= 7:
            PresetSaveCmdString = '(PSS={})\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

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

        COMMANDS = {
            'INS': 'Input',
            'INM': 'Input Mode',
            'KEY': 'Menu Navigation',
            'MI1': 'Multi Input 1',
            'MI2': 'Multi Input 2',
            'MI3': 'Multi Input 3',
            'MI4': 'Multi Input 4',
            'PSA': 'Preset Recall',
            'PSS': 'Preset Save',
            'PWR': 'Power',
            'STA': 'Power'
        }
        
        ERROR_CODES = {
            '1' : 'Unknown command code',
            '2' : 'Invalid operator',
            '3' : 'Destination parameter',
            '4' : 'Setting not available',
            '5' : 'Setting value not available',
            '6' : 'Setting value not supported',
            '7' : 'String too long',
            '8' : 'Command not supported in standby mode',
            '9' : 'Invalid parameter',
            '10': 'Error processing command',
            '11': 'Password not entered'
        }
        
        command = COMMANDS[match.group(2).decode()]
        value = ERROR_CODES[match.group(1).decode()]
        self.Error(['{}: {}.'.format(command, value)])

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])