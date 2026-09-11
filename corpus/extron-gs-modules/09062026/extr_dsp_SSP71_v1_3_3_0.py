from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from extronlib.system import Wait

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
            'Bass': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'ListeningMode': {'Parameters': ['Source Format', 'Input'], 'Status': {}},
            'OutputGainAttenuation':{'Parameters':['Output'], 'Status': {}},
            'SourceFormat': {'Status': {}},
            'Subwoofer': {'Status': {}},
            'Treble': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'SspA([0-2][0-9])\r\n'), self.__MatchAnalogInputGain, None)
            self.AddMatchString(compile(b'Amt0([1-8])\*0([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'SspB(-?[0-1][0-9])\r\n'), self.__MatchBass, None)
            self.AddMatchString(compile(b'Exe0([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Amt([0-1])\r\n'), self.__MatchGlobalAudioMute, None)
            self.AddMatchString(compile(b'Aud0([1-5]) LMod([0-1][0-9]) Vol([0-1][0-9][0-9]) Mut([0-1])\r\n'),self.__MatchInput,None)
            self.AddMatchString(compile(b'Aud([1-5])\r\n'),self.__MatchInput,'Response')
            self.AddMatchString(compile(b'Ssp[LX]0([1-5])\*([0-1][0-9])\*([0-1][0-9])\r\n'), self.__MatchListeningMode, None)
            self.AddMatchString(compile(b'SspQ0([1-5])\*([0-1][0-9])\*([0-4])\r\n'), self.__MatchModeOverride, None) # Added to clear the match buffer for unsolicited response from input switching
            self.AddMatchString(compile(b'SspV0([1-8])\*([\-\d]+)\r\n'), self.__MatchOutputGainAttenuation, None)
            self.AddMatchString(compile(b'SrcFormat ([0-1][0-9]) Sampling 0([0-5]) EnChan ([0-1][0-9])\r\n'), self.__MatchSourceFormat, None)
            self.AddMatchString(compile(b'SspJ0([0-1])\r\n'), self.__MatchSubwoofer, None)
            self.AddMatchString(compile(b'SspT(-?[0-1][0-9])\r\n'), self.__MatchTreble, None)
            self.AddMatchString(compile(b'Vol([0-1][0-9][0-9])\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)


    def __MatchModeOverride(self, match, tag):
        # Override Response
        pass

    def SetAnalogInputGain(self, value, qualifier):

        AnalogInputGainConstraints = {
            'Min': 0,
            'Max': 24
        }
        if AnalogInputGainConstraints['Min'] <= value <= AnalogInputGainConstraints['Max']:
            AnalogInputGainCmdString = '\x1BA{0}SSP\r'.format(value)
            self.__SetHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogInputGain')

    def UpdateAnalogInputGain(self, value, qualifier):

        AnalogInputGainCmdString = '\x1BASSP\r'
        self.__UpdateHelper('AnalogInputGain', AnalogInputGainCmdString, value, qualifier)

    def __MatchAnalogInputGain(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AnalogInputGain', value, None)

    def SetAudioMute(self, value, qualifier):

        OutputName = qualifier['Output']
        AudioMuteStateValues = {
            'On': '1',
            'Off': '0'
        }
        OutputValues = {
            'Left Front': '1',
            'Center': '2',
            'Right Front': '3',
            'Left Surround': '4',
            'Right Surround': '5',
            'Left Back': '6',
            'Right Back': '7',
            'Subwoofer': '8'
        }

        AudioMuteCmdString = '{0}*{1}Z'.format(OutputValues[OutputName], AudioMuteStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        OutputName = qualifier['Output']
        OutputValues = {
            'Left Front': '1',
            'Center': '2',
            'Right Front': '3',
            'Left Surround': '4',
            'Right Surround': '5',
            'Left Back': '6',
            'Right Back': '7',
            'Subwoofer': '8'
        }
        AudioMuteCmdString = '{0}*Z'.format(OutputValues[OutputName])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }
        OutputNames = {
            '1': 'Left Front',
            '2': 'Center',
            '3': 'Right Front',
            '4': 'Left Surround',
            '5': 'Right Surround',
            '6': 'Left Back',
            '7': 'Right Back',
            '8': 'Subwoofer'
        }

        Output = OutputNames[match.group(1).decode()]
        value = AudioMuteStateNames[match.group(2).decode()]
        qualifier = {'Output': Output}
        self.WriteStatus('AudioMute', value, qualifier)

    def SetBass(self, value, qualifier):

        BassConstraints = {
            'Min': -10,
            'Max': 10
        }
        if BassConstraints['Min'] <= value <= BassConstraints['Max']:
            BassCmdString = '\x1BB{0}SSP\r'.format(value)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '\x1BBSSP\r'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Bass', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On': '1X',
            'Off': '0X'
        }
        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
            '1': 'On',
            '0': 'Off',
        }
        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        GlobalAudioMuteStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }
        GlobalAudioMuteCmdString = GlobalAudioMuteStateValues[value]
        self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)

    def UpdateGlobalAudioMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __MatchGlobalAudioMute(self, match, tag):

        GlobalAudioMuteStateNames = {
            '1': 'On',
            '0': 'Off',
        }
        value = GlobalAudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('GlobalAudioMute', value, None)

    def SetInput(self, value, qualifier):

        InputConstraints = {
            'Min': 1,
            'Max': 5
        }
        if InputConstraints['Min'] <= int(value) <= InputConstraints['Max']:
            InputCmdString = '{0}$'.format(int(value))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'

        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        GlobalAudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        InputStateNames = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        if tag == 'Response':
            InputValue = InputStateNames[match.group(1).decode()]
            self.WriteStatus('Input', InputValue, None)
        else:
            InputValue = InputStateNames[match.group(1).decode()]
            VolumeValue = int(match.group(3).decode())
            GlobalAudioMuteValue = GlobalAudioMuteStateNames[match.group(4).decode()]
            self.WriteStatus('Input', InputValue, None)
            self.WriteStatus('Volume', VolumeValue, None)
            self.WriteStatus('GlobalAudioMute', GlobalAudioMuteValue, None)

    def SetListeningMode(self, value, qualifier):

        SourceFormatStateValues = {
            'Not Present': '0',
            'Analog': '1',
            'PCM': '2',
            'Dolby Digital 5.1': '3',
            'Dolby Digital 2/0': '4',
            'Dolby Digital 2/0 Surround': '5',
            'Dolby Digital Surround EX': '6',
            'DTS Digital Surround': '7',
            'DTS-ES Matrix 6.1': '8',
            'DTS-ES Discrete 6.1': '9',
            'DTS 2-Channel': '10'
        }

        ListeningModeStateValues = {
            'Stereo': '1',
            'Mono': '2',
            'Stereo to All': '3',
            'Mono to All': '4',
            'Dolby Pro Logic': '5',
            'Dolby Pro Logic II/IIx Movie': '6',
            'Dolby Pro Logic II/IIx Music': '7',
            'Dolby Digital 5.1': '8',
            'Dolby Digital EX': '9',
            'Dolby Digital Pro Logic IIx Movie': '10',
            'Dolby Digital Pro Logic IIx Music': '11',
            'DTS': '12',
            'DTS ES Matrix': '13',
            'DTS ES Discrete': '14',
            'DTS + Dolby EX': '15',
            'DTS + Dolby Pro Logic IIx Movie': '16',
            'DTS + Dolby Pro Logic IIx Music': '17',
            'DTS Neo:6 Cinema': '18',
            'DTS Neo:6 Music': '19'
        }

        Source, Input = qualifier['Source Format'], qualifier['Input']

        if 1 <= int(Input) <= 5:
            ListeningModeCmdString = '\x1BL{0}*{1}*{2}SSP\r'.format(int(Input), SourceFormatStateValues[Source], ListeningModeStateValues[value])
            self.__SetHelper('ListeningMode', ListeningModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetListeningMode')

    def UpdateListeningMode(self, value, qualifier):

        SourceFormatStateValues = {
            'Not Present'               : '0',
            'Analog'                    : '1',
            'PCM'                       : '2',
            'Dolby Digital 5.1'         : '3',
            'Dolby Digital 2/0'         : '4',
            'Dolby Digital 2/0 Surround': '5',
            'Dolby Digital Surround EX' : '6',
            'DTS Digital Surround'      : '7',
            'DTS-ES Matrix 6.1'         : '8',
            'DTS-ES Discrete 6.1'       : '9',
            'DTS 2-Channel'             : '10'
            }
        Source, Input = qualifier['Source Format'], qualifier['Input']
        if 1 <= int(Input) <= 5:
            ListeningModeCmdString = '\x1BX{0}*{1}SSP\r'.format(int(Input),SourceFormatStateValues[Source])
            self.__UpdateHelper('ListeningMode', ListeningModeCmdString, value, qualifier)
        else:   
            self.Discard('Invalid Command')

    def __MatchListeningMode(self, match, qualifier):

        SourceFormatStateNames = {
            '00': 'Not Present',
            '01': 'Analog',
            '02': 'PCM',
            '03': 'Dolby Digital 5.1',
            '04': 'Dolby Digital 2/0',
            '05': 'Dolby Digital 2/0 Surround',
            '06': 'Dolby Digital Surround EX',
            '07': 'DTS Digital Surround',
            '08': 'DTS-ES Matrix 6.1',
            '09': 'DTS-ES Discrete 6.1',
            '10': 'DTS 2-Channel'
        }

        ListeningModeStateNames = {
            '00': 'No Listening Mode',
            '01': 'Stereo',
            '02': 'Mono',
            '03': 'Stereo to All',
            '04': 'Mono to All',
            '05': 'Dolby Pro Logic',
            '06': 'Dolby Pro Logic II/IIx Movie',
            '07': 'Dolby Pro Logic II/IIx Music',
            '08': 'Dolby Digital 5.1',
            '09': 'Dolby Digital EX',
            '10': 'Dolby Digital Pro Logic IIx Movie',
            '11': 'Dolby Digital Pro Logic IIx Music',
            '12': 'DTS',
            '13': 'DTS ES Matrix',
            '14': 'DTS ES Discrete',
            '15': 'DTS + Dolby EX',
            '16': 'DTS + Dolby Pro Logic IIx Movie',
            '17': 'DTS + Dolby Pro Logic IIx Music',
            '18': 'DTS Neo:6 Cinema',
            '19': 'DTS Neo:6 Music'
        }

        Input = match.group(1).decode()
        SourceFormat = SourceFormatStateNames[match.group(2).decode()]
        qualifier = {'Input': Input, 'Source Format': SourceFormat}
        value = ListeningModeStateNames[match.group(3).decode()]
        self.WriteStatus('ListeningMode', value, qualifier)

    def SetOutputGainAttenuation(self, value, qualifier):

        OutputName = qualifier['Output']
        OutputValues = {
            'Left Front'     : '1',
            'Center'         : '2',
            'Right Front'    : '3',
            'Left Surround'  : '4',
            'Right Surround' : '5',
            'Left Back'      : '6',
            'Right Back'     : '7',
            'Subwoofer'      : '8'
        }

        if -24 <= int(value) <= 12:
            OutputGainAttenuationCmdString = 'wV{0}*{1}SSP\r'.format(OutputValues[OutputName],value)
            self.__SetHelper('OutputGainAttenuation', OutputGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for OutputGainAttenuation')

    def UpdateOutputGainAttenuation(self, value, qualifier):

        OutputName = qualifier['Output']
        OutputValues = {
            'Left Front'     : '1',
            'Center'         : '2',
            'Right Front'    : '3',
            'Left Surround'  : '4',
            'Right Surround' : '5',
            'Left Back'      : '6',
            'Right Back'     : '7',
            'Subwoofer'      : '8'
        }

        OutputGainAttenuationCmdString = 'wV{0}SSP\r'.format(OutputValues[OutputName])
        self.__UpdateHelper('OutputGainAttenuation', OutputGainAttenuationCmdString, value, qualifier)

    def __MatchOutputGainAttenuation(self, match, tag):
        """Output Gain Attenuation MatchString Handler

        """

        OutputNames = {
            '1' : 'Left Front',
            '2' : 'Center',
            '3' : 'Right Front',
            '4' : 'Left Surround',
            '5' : 'Right Surround',
            '6' : 'Left Back',
            '7' : 'Right Back',
            '8' : 'Subwoofer'
        }

        Output = OutputNames[match.group(1).decode()]
        value = int(match.group(2).decode())
        qualifier = {'Output': Output}
        self.WriteStatus('OutputGainAttenuation', value, qualifier)

    def UpdateSourceFormat(self, value, qualifier):

        SourceFormatCmdString = '33I'
        self.__UpdateHelper('SourceFormat', SourceFormatCmdString, value, qualifier)

    def __MatchSourceFormat(self, match, tag):

        ValueStateValues = {
            '00': 'Not Present',
            '01': 'Analog',
            '02': 'PCM',
            '03': 'Dolby Digital 5.1',
            '04': 'Dolby Digital 2/0',
            '05': 'Dolby Digital 2/0 Surround',
            '06': 'Dolby Digital Surround EX',
            '07': 'DTS Digital Surround',
            '08': 'DTS-ES Matrix 6.1',
            '09': 'DTS-ES Discrete 6.1',
            '10': 'DTS 2-Channel'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SourceFormat', value, None)

    def SetSubwoofer(self, value, qualifier):

        SubwooferStateValues = {
            'On': '\x1BJ1SSP\r',
            'Off': '\x1BJ0SSP\r'
        }
        SubwooferCmdString = SubwooferStateValues[value]
        self.__SetHelper('Subwoofer', SubwooferCmdString, value, qualifier)

    def UpdateSubwoofer(self, value, qualifier):

        SubwooferCmdString = '\x1BJSSP\r'

        self.__UpdateHelper('Subwoofer', SubwooferCmdString, value, qualifier)

    def __MatchSubwoofer(self, match, tag):

        SubwooferStateNames = {
            '1': 'On',
            '0': 'Off',
        }
        value = SubwooferStateNames[match.group(1).decode()]
        self.WriteStatus('Subwoofer', value, None)

    def SetTreble(self, value, qualifier):

        TrebleConstraints = {
            'Min': -10,
            'Max': 10
        }
        if TrebleConstraints['Min'] <= value <= TrebleConstraints['Max']:
            TrebleCmdString = '\x1BT{0}SSP\r'.format(value)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '\x1BTSSP\r'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Treble', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

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

    def __MatchErrors(self, match, tag):
        self.counter = 0
        DeviceErrorCodes = {
            '13': 'Invalid value (too large)',
            '01': 'Invalid input channel number (too large)',
            '10': 'Invalid command',
            '14': 'Not valid for this configuration'
        }
        if match.group(1).decode('ascii') in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode('ascii')]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode('ascii')])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback 
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command)
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
            print(command, 'does not exist in the module')

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
        Command = self.Commands[command]
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

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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