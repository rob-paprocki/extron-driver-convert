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
            'AnalogInputGain': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'EXPInputAssignment': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'ListeningMode': {'Parameters': ['Input', 'Source Format'], 'Status': {}},
            'OutputTrim': {'Parameters': ['Output'], 'Status': {}},
            'SourceFormat': {'Status': {}},
            'Subwoofer': {'Status': {}},
            'Volume': {'Status': {}},
            }

        self.VerboseDisabled = True
        self.EchoDisabled = True
      
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'SspA(-?[0-9]{1,2})\r\n'), self.__MatchAnalogInputGain, None)
            self.AddMatchString(re.compile(rb'Amt(\d+)\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([0-3])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'SspE([0234])\r\n'), self.__MatchEXPInputAssignment, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, 'Global')
            self.AddMatchString(re.compile(b'Aud([1-5])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(rb'SspL([1-5])\*([0-9]{1,2})\*([1-7])\r\n'), self.__MatchListeningMode, None)
            self.AddMatchString(re.compile(rb'SspV(\d+)\*(-?[0-9]{1,2})\r\n'), self.__MatchOutputTrim, None)
            self.AddMatchString(re.compile(b'Inf33SrcFormat ([0-9]{1,2}) Sampling [0-7] EnChan [0-9]{1,2}'), self.__MatchSourceFormat, None)
            self.AddMatchString(re.compile(b'SspJ([01])\r\n'), self.__MatchSubwoofer, None)
            self.AddMatchString(re.compile(rb'Vol(\d+)'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(rb'(E\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAnalogInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AnalogInputGainCmdString = '\x1ba{}SSP\r'.format(value)
            self.__SetHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputGain')

    def UpdateAnalogInputGain(self, value, qualifier):

        AnalogInputGainCmdString = '\x1baSSP\r'
        self.__UpdateHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)

    def __MatchAnalogInputGain(self, match, tag):

        value = int(match.group(1).decode())
        if -18 <= value <= 24:
            self.WriteStatus('AnalogInputGain', value, None)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '15': '15',
            '16': '16'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            AudioMuteCmdString = '{0}*{1}Z'.format(qualifier['Output'], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '15': '15',
            '16': '16'
        }

        if qualifier['Output'] in OutputStates:
            AudioMuteCmdString = '{0}*Z'.format(qualifier['Output'])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        if tag == 'Global':
            for i in range(1, 17):
                self.WriteStatus('AudioMute', ValueStateValues[match.group(1).decode()], {'Output': str(i)})

        else:
            qualifier = {}
            qualifier['Output'] = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3',
            'Off': '0'
        }
        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateEXPInputAssignment(self, value, qualifier):

        EXPInputAssignmentCmdString = '\x1beSSP\r'
        self.__UpdateHelper('EXPInputAssignment', EXPInputAssignmentCmdString, value, qualifier)

    def __MatchEXPInputAssignment(self, match, tag):

        ValueStateValues = {
            '0': '0',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('EXPInputAssignment', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        if value in ValueStateValues:
            InputCmdString = '{0}$'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '$'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetListeningMode(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        SourceFormatStates = {
            'Not Present': '0',
            'Analog': '1',
            'PCM': '2',
            'Dolby Digital': '3',
            'Dolby Digital Plus': '4',
            'Dolby Digital Plus ATMOS': '5',
            'Dolby TrueHD': '6',
            'Dolby TrueHD ATMOS': '7',
            'DTS or DTS 96/24': '8',
            'DTS-ES (96/24, Matrix, or Discrete)': '9',
            'DTS-HD High Resolution Audio': '10',
            'DTS-HD Master Audio': '11',
            'DTS Express': '12',
            'DTS:X': '13'
        }

        ValueStateValues = {
            'Auto': '1',
            'Stereo': '2',
            'Mono': '3',
            'Stereo to all': '4',
            'Mono to all': '5',
            'Dolby Surround': '6',
            'DTS Neural:X': '7'
        }

        if value in ValueStateValues and qualifier['Input'] in InputStates and qualifier['Source Format'] in SourceFormatStates:
            ListeningModeCmdString = '\x1bl{0}*{1}*{2}SSP\r'.format(qualifier['Input'], SourceFormatStates[qualifier['Source Format']], ValueStateValues[value])
            self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetListeningMode')

    def UpdateListeningMode(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        SourceFormatStates = {
            'Not Present': '0',
            'Analog': '1',
            'PCM': '2',
            'Dolby Digital': '3',
            'Dolby Digital Plus': '4',
            'Dolby Digital Plus ATMOS': '5',
            'Dolby TrueHD': '6',
            'Dolby TrueHD ATMOS': '7',
            'DTS or DTS 96/24': '8',
            'DTS-ES (96/24, Matrix, or Discrete)': '9',
            'DTS-HD High Resolution Audio': '10',
            'DTS-HD Master Audio': '11',
            'DTS Express': '12',
            'DTS:X': '13'
        }
        if qualifier['Input'] in InputStates and qualifier['Source Format'] in SourceFormatStates:
            ListeningModeCmdString = '\x1bl{0}*{1}SSP\r'.format(qualifier['Input'], SourceFormatStates[qualifier['Source Format']])
            self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateListeningMode')

    def __MatchListeningMode(self, match, tag):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        SourceFormatStates = {
            '0': 'Not Present',
            '1': 'Analog',
            '2': 'PCM',
            '3': 'Dolby Digital',
            '4': 'Dolby Digital Plus',
            '5': 'Dolby Digital Plus ATMOS',
            '6': 'Dolby TrueHD',
            '7': 'Dolby TrueHD ATMOS',
            '8': 'DTS or DTS 96/24',
            '9': 'DTS-ES (96/24, Matrix, or Discrete)',
            '10': 'DTS-HD High Resolution Audio',
            '11': 'DTS-HD Master Audio',
            '12': 'DTS Express',
            '13': 'DTS:X'
        }

        ValueStateValues = {
            '1': 'Auto',
            '2': 'Stereo',
            '3': 'Mono',
            '4': 'Stereo to all',
            '5': 'Mono to all',
            '6': 'Dolby Surround',
            '7': 'DTS Neural:X'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        qualifier['Source Format'] = SourceFormatStates[match.group(2).decode()]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('ListeningMode', value, qualifier)

    def SetOutputTrim(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '15': '15',
            '16': '16'
        }

        ValueConstraints = {
            'Min': -24,
            'Max': 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and qualifier['Output'] in OutputStates:
            OutputTrimCmdString = '\x1bv{0}*{1}SSP\r'.format(qualifier['Output'], value)
            self.__SetHelper('OutputTrim', OutputTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputTrim')

    def UpdateOutputTrim(self, value, qualifier):
        
        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '15': '15',
            '16': '16'
        }
        
        if qualifier['Output'] in OutputStates:
            OutputTrimCmdString = '\x1bv{0}SSP\r'.format(qualifier['Output'])
            self.__UpdateHelper('OutputTrim', OutputTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputTrim')

    def __MatchOutputTrim(self, match, tag):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '15': '15',
            '16': '16'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('OutputTrim', value, qualifier)

    def UpdateSourceFormat(self, value, qualifier):

        SourceFormatCmdString = '33I'
        self.__UpdateHelper('SourceFormat', SourceFormatCmdString, value, qualifier)

    def __MatchSourceFormat(self, match, tag):

        SourceFormatStateValues = {
            '0': 'Not Present',
            '1': 'Analog',
            '2': 'PCM',
            '3': 'Dolby Digital',
            '4': 'Dolby Digital Plus',
            '5': 'Dolby Digital Plus ATMOS',
            '6': 'Dolby TrueHD',
            '7': 'Dolby TrueHD ATMOS',
            '8': 'DTS or DTS 96/24',
            '9': 'DTS-ES (96/24, Matrix, or Discrete)',
            '10': 'DTS-HD High Resolution Audio',
            '11': 'DTS-HD Master Audio',
            '12': 'DTS Express',
            '13': 'DTS:X'
        }

        value = SourceFormatStateValues[match.group(1).decode()]
        self.WriteStatus('SourceFormat', value, None)

    def SetSubwoofer(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            SubwooferCmdString = '\x1bj{0}SSP\r'.format(ValueStateValues[value])
            self.__SetHelper('Subwoofer', SubwooferCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSubwoofer')

    def UpdateSubwoofer(self, value, qualifier):

        SubwooferCmdString = '\x1bjSSP\r'
        self.__UpdateHelper('Subwoofer', SubwooferCmdString, value, qualifier)

    def __MatchSubwoofer(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Subwoofer', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}v'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'v'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        if 0 <= value <= 100:
            self.WriteStatus('Volume', value, None)

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

        DeviceErrorCodes = {
            '10': 'Unrecognized command',
            '12': 'Invalid port number',
            '13': 'Invalid parameter (number is out of range)',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System/command timed out',
            '22': 'Busy',
            '25': 'Device is not present',
            '26': 'Maximum connections exceeded',
            '30': 'Hardware Failure',
        }
        self.Error([DeviceErrorCodes.get(match.group(1).decode(), 'Unrecognized error code: {0}'.format(match.group(0).decode()))])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    
    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        
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
