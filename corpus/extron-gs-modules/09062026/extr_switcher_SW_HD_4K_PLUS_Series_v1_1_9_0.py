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
            'SW2 HD 4K PLUS': self.extr_2_3239_sw2,
            'SW4 HD 4K PLUS': self.extr_2_3239_sw4,
            'SW6 HD 4K PLUS': self.extr_2_3239_sw6,
            'SW8 HD 4K PLUS': self.extr_2_3239_sw8,
        }



        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'CECPower': { 'Status': {}},
            'CECShowAsActiveSource': { 'Status': {}},
            'ContactPort': {'Parameters': ['Port'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'Input': { 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'TallyPort': {'Parameters': ['Port'], 'Status': {}},
            'VideoMute': { 'Status': {}},
        }
        
        self.CECEnabled = False
        self.EchoDisabled = True
        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Afmt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw([012])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Sts([1-8])\*([01]+)\r\n'), self.__MatchContactPort, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE([1-8])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'HdcpE([ 01]{3,16})\r\n'), self.__MatchHDCPInputAuthorization, 'Update')
            self.AddMatchString(re.compile(b'In([0-8]) All\r\n'), self.__MatchInput, 'Set')
            self.AddMatchString(re.compile(b'In([0-8]) Ausw([0-2]) Afmt([0-1]) Vmt([0-2])\r\n'), self.__MatchInput, 'Update')
            self.AddMatchString(re.compile(b'Sig\"?([ 01]+)\*([01])\"?\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Taly([1-8])\*([01]+)\r\n'), self.__MatchTallyPort, None)
            self.AddMatchString(re.compile(b'Vmt([012])\r\n'), self.__MatchVideoMute, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH
            self.AddMatchString(re.compile(b'(E01|E06|E10|E13)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, tag):

        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False
    
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'w{}AFMT\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off':                      '0',
            'User Priority':            '1',
            'Input Memory Priority':    '2',
        }

        if value in ValueStateValues:
            AutoSwitchModeCmdString = 'w{}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeStateNames = {
            '0': 'Off',
            '1': 'User Priority',
            '2': 'Input Memory Priority'
        }

        value = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : '"PwrOn"',
            'Off' : '"PwrOff"'
        }

        if value in ValueStateValues:
            if not self.CECEnabled:
                self.CECEnabled = True
                self.Send('wO1*2CCEC\r')

            CECPowerCmdString = '\x1BO1*{}DCEC\r'.format(ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        if not self.CECEnabled:
            self.CECEnabled = True
            self.Send('wO1*2CCEC\r')

        CECShowAsActiveSourceCmdString = 'wO01*\"ShowMe\"DCEC\r'
        self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)

    def UpdateContactPort(self, value, qualifier):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Closed'
        }

        port = int(qualifier['Port'])
        if 1 <= port <= self.InputSize:

            ContactClosureInputCmdString = 'S'
            res = self.__UpdateHelperSync('ContactPort', ContactClosureInputCmdString, value, qualifier)
            if res:
                res = res.strip()
                if res.startswith('Sts'):
                    res = res[3:]

                try:
                    for x in range(1, self.InputSize + 1):
                        qualifier = {'Port': str(x)}
                        value = ValueStateValues[res[x - 1]]
                        self.WriteStatus('ContactPort', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Contact Port: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateContactPort')

    def __MatchContactPort(self, match, tag):

        ValueStateValues = {
            0: 'Open',
            1: 'Closed'
        }

        qualifier = {'Port': match.group(1).decode()}
        if qualifier['Port'] in self.States:
            value = ValueStateValues[int(match.group(2).decode())]
            self.WriteStatus('ContactPort', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On':   '1X',
            'Off':  '0X'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        _input = qualifier['Input']
        if 1 <= int(_input) <= self.InputSize and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(_input, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        _input = qualifier['Input']

        if 1 <= int(_input) <= self.InputSize:

            HDCPInputAuthorizationCmdString = 'wEHDCP\r'
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        
        if tag == 'Update':
            test = match.group(1).decode()
            test = test.replace(' ', '')
            i = 0
            while i < len(test):
                value = ValueStateValues[test[i]]
                self.WriteStatus('HDCPInputAuthorization', value, {'Input': str(i + 1)})
                i = i + 1
        elif tag == 'Set':
            self.WriteStatus('HDCPInputAuthorization', ValueStateValues[match.group(2).decode()], {'Input': match.group(1).decode()})

    def SetInput(self, value, qualifier):

        if 0 <= int(value) <= self.InputSize:
            InputCmdString = '{0}!'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        if tag == 'Set':
            inputVal = match.group(1).decode()
            if inputVal == '0' or inputVal in self.States:
                self.WriteStatus('Input', inputVal, None)
        elif tag == 'Update':
            AudioMuteStates = {
                '1': 'On',
                '0': 'Off'
            }

            AutoSwitchModeStates = {
                '0': 'Off',
                '1': 'User Priority',
                '2': 'Input Memory Priority'
            }

            VideoMuteStates = {
                '2': 'On with Sync',
                '1': 'On',
                '0': 'Off'
            }

            self.WriteStatus('AudioMute', AudioMuteStates[match.group(3).decode()], None)
            self.WriteStatus('AutoSwitchMode', AutoSwitchModeStates[match.group(2).decode()], None)
            self.WriteStatus('VideoMute', VideoMuteStates[match.group(4).decode()], None)

            value = match.group(1).decode()
            if value == '0' or value in self.States:
                self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        _input = qualifier['Input']
        if 1 <= int(_input) <= self.InputSize:
            InputSignalStatusQueryCmdString = 'wLS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalStatusQueryCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active',
        }        
       
        valueList = match.group(1).decode().split()
        
        index = 0
        for value in valueList:
            self.WriteStatus('InputSignalStatus', InputSignalStatusStateNames[value], {'Input': str(index + 1)})
            index += 1

    def UpdateTallyPort(self, value, qualifier):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Closed'
        }

        port = qualifier['Port']
        if 1 <= int(port) <= self.InputSize:

            TallyCmdString = 'wTALY\r'
            res = self.__UpdateHelperSync('TallyPort', TallyCmdString, value, qualifier)
            if res:
                res = res.strip()
                if res.startswith('Taly'):
                    res = res[4:]

                try:
                    for x in range(1, self.InputSize + 1):
                        qualifier = {'Port': str(x)}
                        value = ValueStateValues[res[x-1]]
                        self.WriteStatus('TallyPort', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tally Port: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateTallyPort')

    def __MatchTallyPort(self, match, tag):

        ValueStateValues = {
            0: 'Open',
            1: 'Closed'
        }

        qualifier = {'Port': match.group(1).decode()}
        if qualifier['Port'] in self.States:
            value = ValueStateValues[int(match.group(2).decode())]
            self.WriteStatus('TallyPort', value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':           '1B',
            'Off':          '0B',
            'On with Sync': '2B',
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        self.UpdateInput(value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'On with Sync'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number',
            'E06': 'Invalid input selection during auto-input switching',   
            'E10': 'Invalid command',
            'E13': 'Invalid value(out of range)'
        }   

        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error(['An error occurred: {0}: {1}: {2}.'.format(sourceCmdName, k, v)])
                    response = ''
        return response

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number',
            'E06': 'Invalid input selection during auto-input switching',
            'E10': 'Invalid command',
            'E13': 'Invalid value(out of range)'
        }

        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error(['An error occurred: {}.'.format(value)])

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

    def __UpdateHelperSync(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
                
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')             
        else:
            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.SendAndWait('w3cv\r\n', self.DefaultResponseTimeout, deliTag=b'\r\n')
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                    if not res:
                        return ''
                    else:
                        return self.__CheckResponseForErrors(command, res.decode())  
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
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

        self.CECEnabled = False
        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_2_3239_sw2(self):

        self.InputSize = 2
        self.States = {'1', '2'}

    def extr_2_3239_sw4(self):

        self.InputSize = 4
        self.States = {'1', '2', '3', '4'}

    def extr_2_3239_sw6(self):

        self.InputSize = 6
        self.States = {'1', '2', '3', '4', '5', '6'}

    def extr_2_3239_sw8(self):

        self.InputSize = 8
        self.States = {'1', '2', '3', '4', '5', '6', '7', '8'}

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()