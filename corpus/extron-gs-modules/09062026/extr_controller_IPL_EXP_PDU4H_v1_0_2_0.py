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
            'ACPowerOutput': {'Parameters': ['Output'], 'Status': {}},
            'CircuitBreaker': { 'Status': {}},
            'CombinedCurrent': { 'Status': {}},
            'ManualControl': {'Parameters': ['Input'], 'Status': {}},
            'Relay': { 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Cpn([1-4]) Ppc([01])\r\n'), self.__MatchACPowerOutput, None)
            self.AddMatchString(re.compile(b'32Stat ([01])\r\n'), self.__MatchCircuitBreaker, None)
            self.AddMatchString(re.compile(b'31Stat (\d+(?:\.\d+)?)\r\n'), self.__MatchCombinedCurrent, None)
            self.AddMatchString(re.compile(b'Sio([1-4])\*([01])\r\n'), self.__MatchManualControl, None)
            self.AddMatchString(re.compile(b'Cpn1 Rly([01])\r\n'), self.__MatchRelay, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False

    def SetACPowerOutput(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= output <= 4 and value in ValueStateValues:
            ACPowerOutputCmdString = 'w{}*{}PC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('ACPowerOutput', ACPowerOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetACPowerOutput')

    def UpdateACPowerOutput(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 4:
            ACPowerOutputCmdString = 'w{}*PC\r'.format(output)
            self.__UpdateHelper('ACPowerOutput', ACPowerOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateACPowerOutput')

    def __MatchACPowerOutput(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ACPowerOutput', value, qualifier)

    def UpdateCircuitBreaker(self, value, qualifier):

        CircuitBreakerCmdString = 'w32STAT\r'
        self.__UpdateHelper('CircuitBreaker', CircuitBreakerCmdString, value, qualifier)

    def __MatchCircuitBreaker(self, match, tag):

        ValueStateValues = {
            '0': 'Tripped',
            '1': 'Closed'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CircuitBreaker', value, None)

    def UpdateCombinedCurrent(self, value, qualifier):


        CombinedCurrentCmdString = 'w31STAT\r'
        self.__UpdateHelper('CombinedCurrent', CombinedCurrentCmdString, value, qualifier)

    def __MatchCombinedCurrent(self, match, tag):

        value = float(match.group(1).decode())
        if 0 <= value <= 10.0:
            self.WriteStatus('CombinedCurrent', value, None)

    def UpdateManualControl(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 4:
            ManualControlCmdString = '{}]'.format(input_)
            self.__UpdateHelper('ManualControl', ManualControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateManualControl')

    def __MatchManualControl(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ManualControl', value, qualifier)

    def SetRelay(self, value, qualifier):

        ValueStateValues = {
            'Close':    '1',
            'Open':     '0'
        }

        if value in ValueStateValues:
            RelayCmdString = '1*{}O'.format(ValueStateValues[value])
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        RelayCmdString = '1O'
        self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)

    def __MatchRelay(self, match, tag):

        ValueStateValues = {
            '1': 'Close',
            '0': 'Open'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Relay', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n') 
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.counter = 0

        errors = {
            10: 'Invalid command',
            12: 'Command is for a port that is not available on the product',
            13: 'Invalid value (the number is out of range or too large) or parameter',
            14: 'Invalid for this configuration',
            18: 'System or command timed out',
            22: 'Busy',
            24: 'Privilege violation',
            26: 'Maximum number of connections has been exceeded',
            28: 'Bad filename or file not found',
            37: 'Invalid command while in SPD mode'
        }

        error = int(match.group(1).decode())
        
        self.Error(['An error occurred: {}: {}.'.format(error, errors.get(error, 'Unknown error'))])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.VerboseDisabled = True
        self.EchoDisabled = True

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

class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
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