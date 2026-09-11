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
            'SW2 USB Pro': self.extr_2_5328_sw2,
            'SW4 USB Pro': self.extr_2_5328_sw4,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'HotKey': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'OutputSignalStatus': {'Parameters': ['Output'], 'Status': {}},
            'PeripheralEmulation': {'Parameters': ['Input'], 'Status': {}}
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe(0|1)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'UsbcH([01])\r\n'), self.__MatchHotKey, None)
            self.AddMatchString(re.compile(b'In([0-4]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'UsbcI\*([01 ]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'UsbcO\*([01 ]+)\r\n'), self.__MatchOutputSignalStatus, None)
            self.AddMatchString(re.compile(b'UsbcE\*([01 ]+)\r\n'), self.__MatchPeripheralEmulation, 'Query')
            self.AddMatchString(re.compile(b'UsbcE([0-4])\*([01])\r\n'), self.__MatchPeripheralEmulation, 'Unsolicited')
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, tag):
        
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, tag):

        self.EchoDisabled = False

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off'                       : '0',
            'User Defined Priority'     : '1',
            'Last Connected Input'      : '2'
        }

        if value in ValueStateValues:
            AutoSwitchStr = '\x1b{}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchStr, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchStr = '\x1bAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchStr, value, qualifier)
            
    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '0'        : 'Off',
            '1'        : 'User Defined Priority',
            '2'        : 'Last Connected Input'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetExecutiveMode(self, value, qualifier):
 
        ValueStateValues = {
            'On'  : '1X', 
            'Off' : '0X'
        }

        if value in ValueStateValues:
            ExecutiveModeString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):
  
        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        
    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1'        : 'On',
            '0'        : 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)
 
    def SetHotKey(self, value, qualifier):

        ValueStateValues = {
            'Enabled'  : '1', 
            'Disabled' : '0'
        }

        if value in ValueStateValues:
            HotKeyString = 'wH{0}USBC\r'.format(ValueStateValues[value])
            self.__SetHelper('HotKey', HotKeyString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHotKey')

    def UpdateHotKey(self, value, qualifier):

        HotKeyString = 'wHUSBC\r'
        self.__UpdateHelper('HotKey', HotKeyString, value, qualifier)

    def __MatchHotKey(self, match, tag):

        ValueStateValues = {
            '1'  : 'Enabled', 
            '0'  : 'Disabled'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HotKey', value, None)

    def SetInput(self, value, qualifier):

        if value in self.InputValues:
            InputStr = self.InputValues[value] + '!'
            self.__SetHelper('Input', InputStr, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', '!', value, qualifier)
        
    def __MatchInput(self, match, tag):

        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):
            
        InputSignalStr = '\x1BI*USBC\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStr, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):


        InputValues = {
            '0' : 'Not Active',
            '1' : 'Active'
        }
    
        val = match.group(1).decode().split()
        for input_num, signal in enumerate(val, 1):
            self.WriteStatus('InputSignalStatus', InputValues[signal], {'Input': str(input_num)})

    def UpdateOutputSignalStatus(self, value, qualifier):
            
        OutputSignalStr = '\x1BO*USBC\r'
        self.__UpdateHelper('OutputSignalStatus', OutputSignalStr, value, qualifier)
    
    def __MatchOutputSignalStatus(self, match, tag):

        OutputValues = {
            '0' : 'Not Active',
            '1' : 'Active'
        }

        val = match.group(1).decode().split()
        for output_num, signal in enumerate(val, 1):
            self.WriteStatus('OutputSignalStatus', OutputValues[signal], {'Output': str(output_num)})

    def SetPeripheralEmulation(self, value, qualifier):

        ValueStateValues = {
            'Disable' :   '0',
            'Enable'  :   '1'
        }

        input_ = self.InputValues[qualifier['Input']]
        if value in ValueStateValues:
            PeripheralEmulationStr = 'wE{0}*{1}USBC\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('PeripheralEmulation', PeripheralEmulationStr, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeripheralEmulation')

    def UpdatePeripheralEmulation(self, value, qualifier):

        if qualifier['Input'] in self.InputValues:
            PeripheralEmulationStr = 'wE*USBC\r'
            self.__UpdateHelper('PeripheralEmulation', PeripheralEmulationStr, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePeripheralEmulation')

    def __MatchPeripheralEmulation(self, match, tag):
        
        ValueStateValues = {
            '0': 'Disable',
            '1': 'Enable'
        }

        if tag == 'Unsolicited':
            input_ = match.group(1).decode()
            val = match.group(2).decode()
            self.WriteStatus('PeripheralEmulation', ValueStateValues[val], {'Input': input_})
        elif tag == 'Query':
            val = match.group(1).decode().split()
            for input_num, signal in enumerate(val, 1):
                self.WriteStatus('PeripheralEmulation', ValueStateValues[signal], {'Input': str(input_num)})

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

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input channel number',
            '06' : 'Invalid switch while in auto-switch mode',
            '10' : 'Invalid command',
            '13' : 'Invalid value',
            '14' : 'Not valid for this configuration',
            '24' : 'Privilege violation',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename/file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: '+ match.group(1).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_2_5328_sw2(self):

        self.InputValues = {
            '0' : '0',
            '1' : '1',
            '2' : '2',
        }

    def extr_2_5328_sw4(self):

        self.InputValues = {
            '0' : '0',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()