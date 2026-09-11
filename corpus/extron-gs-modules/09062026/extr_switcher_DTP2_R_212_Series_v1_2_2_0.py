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
        self.Models = {
            'DTP2 R 212': self.extr_2_4856_NON_SA,
            'DTP2 R 212 SA': self.extr_2_4856_SA,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogAudioLineoutMode': {'Status': {}},
            'AudioFormat': {'Parameters': ['Input'], 'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'CECPower': {'Status': {}},
            'CECShowAsActiveSource': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'OutputAttenuation': {'Status': {}},
            'OutputAttenuationSA': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Status': {}},
            'OutputMuteSA': {'Parameters': ['Output'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.CECOutputEnabled = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'LineOut\*([12])\r\n'), self.__MatchAnalogAudioLineoutMode, None)
            self.AddMatchString(re.compile(b'AfmtI([0-3]) ([0-3])\r\n'), self.__MatchAudioFormat, 'Query')
            self.AddMatchString(re.compile(b'AfmtI([1-2])\*([0-3])\r\n'), self.__MatchAudioFormat, 'Unsolicited')
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Exe([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE([0-1]) ([0-1])\r\n'), self.__MatchHDCPInputAuthorization, 'Query')
            self.AddMatchString(re.compile(b'HdcpE([1-2])\*([0-1])\r\n'), self.__MatchHDCPInputAuthorization, 'Unsolicited')
            self.AddMatchString(re.compile(b'HdcpI([0-2]) ([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'In([0-2]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig([0-1]) ([0-1])\*([0-1])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'DsG6000([02])\*([0-9-]{1,5})\r\n'), self.__MatchOutputAttenuation, None)  # only catch Left channels to prevent duplicate matches
            self.AddMatchString(re.compile(b'DsM6000([02])\*([01])\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAnalogAudioLineoutMode(self, value, qualifier):

        ValueStateValues = {
            'Variable': '1',
            'Fixed': '2'
        }

        if value in ValueStateValues:
            AnalogAudioLineoutModeCmdString = '55*{}#'.format(ValueStateValues[value])
            self.__SetHelper('AnalogAudioLineoutMode', AnalogAudioLineoutModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAudioLineoutMode')

    def UpdateAnalogAudioLineoutMode(self, value, qualifier):

        AnalogAudioLineoutModeCmdString = '55#'
        self.__UpdateHelper('AnalogAudioLineoutMode', AnalogAudioLineoutModeCmdString, value, qualifier)

    def __MatchAnalogAudioLineoutMode(self, match, tag):

        ValueStateValues = {
            '1': 'Variable',
            '2': 'Fixed'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AnalogAudioLineoutMode', value, None)

    def SetAudioFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'Digital': '2',
            'Analog': '3',
            'None': '0'
        }

        if qualifier['Input'] in ['1', '2'] and value in ValueStateValues:
            AudioFormatCmdString = 'wI{0}*{1}AFMT\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Disable('Invalid Command')

    def UpdateAudioFormat(self, value, qualifier):

        AudioFormatCmdString = 'wIAFMT\r'
        self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)

    def __MatchAudioFormat(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '2': 'Digital',
            '3': 'Analog',
            '0': 'None'
        }

        if tag == 'Unsolicited':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioFormat', value, {'Input': match.group(1).decode()})
        else:
            in1 = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('AudioFormat', in1, {'Input': '1'})
            in2 = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioFormat', in2, {'Input': '2'})

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Highest Active Input': '1',
            'Lowest Active Input': '2',
            'Off': '0'
        }

        if value in ValueStateValues:
            AutoSwitchModeCmdString = 'w{0}AUSW\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On': '"PwrOn"',
            'Off': '"PwrOff"'
        }

        if value in ValueStateValues:
            if not self.CECOutputEnabled:
                self.CECOutputEnabled = True
                self.Send('wO1*2CCEC\r')

            CECPowerCmdString = 'wO1*{}DCEC\r'.format(ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)  # Query delay needed, tested with device v1_2_2
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        if not self.CECOutputEnabled:
            self.CECOutputEnabled = True
            self.Send('wO1*2CCEC\r')

        CECShowAsActiveSourceCmdString = 'wO1*\"ShowMe\"DCEC\r'
        self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)  # Query delay needed, tested with device v1_2_2

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{0}x'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'x'
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
            'On': '1',
            'Off': '0'
        }

        if qualifier['Input'] in ['1', '2'] and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Unsolicited':
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputAuthorization', value, {'Input': match.group(1).decode()})
        else:
            in1 = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('HDCPInputAuthorization', in1, {'Input': '1'})
            in2 = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputAuthorization', in2, {'Input': '2'})

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Device Detected',
            '1': 'Source Detected with HDCP',
            '2': 'Source Detected without HDCP'
        }

        in1 = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputStatus', in1, {'Input': '1'})
        in2 = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', in2, {'Input': '2'})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink Device Detected',
            '1': 'Sink Detected with HDCP',
            '2': 'Sink Detected without HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1!',
            '2': '2!',
            '0': '0!'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        in1 = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', in1, {'Input': '1'})
        in2 = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', in2, {'Input': '2'})

    def SetOutputAttenuation(self, value, qualifier):

        if -100 <= value <= 0:
            self.__SetHelper('OutputAttenuation', 'wG60000*{}AU\r'.format(round(value * 10)), value, qualifier)  # send L/R commands back-to-back
            self.__SetHelper('OutputAttenuation', 'wG60001*{}AU\r'.format(round(value * 10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        OutputAttenuationCmdString = 'wG60000AU\r'  # only query L channel
        self.__UpdateHelper('OutputAttenuation', OutputAttenuationCmdString, value, qualifier)

    def __MatchOutputAttenuation(self, match, tag):

        OutputStates = {
            '0': 'Line Out',
            '2': 'Amp Out'
        }

        value = int(match.group(2).decode()) / 10
        if self.Model == 'Non SA':
            self.WriteStatus('OutputAttenuation', value, None)
        else:
            qualifier = {'Output': OutputStates[match.group(1).decode()]}
            self.WriteStatus('OutputAttenuationSA', value, qualifier)

    def SetOutputAttenuationSA(self, value, qualifier):

        OutputStates = {
            'Line Out': ['0', '1'],
            'Amp Out': ['2', '3']
        }

        if qualifier['Output'] in OutputStates and -100 <= value <= 0:
            self.__SetHelper('OutputAttenuationSA', 'wG6000{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][0], round(value * 10)), value, qualifier)
            self.__SetHelper('OutputAttenuationSA', 'wG6000{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][1], round(value * 10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuationSA')

    def UpdateOutputAttenuationSA(self, value, qualifier):

        OutputStates = {
            'Line Out': '0',
            'Amp Out': '2'
        }

        if qualifier['Output'] in OutputStates:
            OutputAttenuationSACmdString = 'wG6000{0}AU\r'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputAttenuationSA', OutputAttenuationSACmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAttenuationSA')

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            self.__SetHelper('OutputMute', 'wM60000*{}AU\r'.format(ValueStateValues[value]), value, qualifier)
            self.__SetHelper('OutputMute', 'wM60001*{}AU\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        OutputMuteCmdString = 'wM60000AU\r'
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        OutputStates = {
            '0': 'Line Out',
            '2': 'Amp Out'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        if self.Model == 'Non SA':
            self.WriteStatus('OutputMute', value, None)
        else:
            qualifier = {'Output': OutputStates[match.group(1).decode()]}
            self.WriteStatus('OutputMuteSA', value, qualifier)

    def SetOutputMuteSA(self, value, qualifier):

        OutputStates = {
            'Line Out': ['0', '1'],
            'Amp Out': ['2', '3']
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            self.__SetHelper('OutputMuteSA', 'wM6000{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][0], ValueStateValues[value]), value, qualifier)
            self.__SetHelper('OutputMuteSA', 'wM6000{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][1], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMuteSA')

    def UpdateOutputMuteSA(self, value, qualifier):

        OutputStates = {
            'Line Out': '0',
            'Amp Out': '2'
        }

        if qualifier['Output'] in OutputStates:
            OutputMuteSACmdString = 'wM6000{0}AU\r'.format(OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputMuteSA', OutputMuteSACmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMuteSA')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'On with Sync': '2B',
            'Off': '0B'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

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
            '01' : 'Invalid input number',
            '06' : 'Invalid channel change',
            '10' : 'Invalid command',
            '13' : 'Invalid parameter',
            '14' : 'Invalid for this configuration',
            '17' : 'Invalid command for signal type',
            '24' : 'Privilege violation'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: ' + match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.CECOutputEnabled = False

    def extr_2_4856_NON_SA(self):
        self.Model = 'Non SA'

    def extr_2_4856_SA(self):
        self.Model = 'SA'

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
        
        # check incoming data if it matched any expected data from device module
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