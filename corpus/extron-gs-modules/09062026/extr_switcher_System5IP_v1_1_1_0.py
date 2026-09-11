from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'AudioMute': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'Bass': {'Status': {}},
            'DisplayMute': {'Status': {}},
            'DisplayPower': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputType': {'Parameters': ['Input'], 'Status': {}},
            'Relay': {'Parameters': ['Relay'], 'Status': {}},
            'RelayPulse': {'Parameters': ['Relay'], 'Status': {}},
            'Treble': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = 'extron'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Amt([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Inp0([0-5])\sAud=([-+][0-4]\d|\s00)dB\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(compile(b'Bas(0\d|10)\r\n'), self.__MatchBass, None)
            self.AddMatchString(compile(b'Mut([0-1])\r\n'), self.__MatchDisplayMute, None)
            self.AddMatchString(compile(b'Pwr([0-3])\r\n'), self.__MatchDisplayPower, None)
            self.AddMatchString(compile(b'Exe([0-3])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Vid0([0-5]) Aud0([0-5])\r\n'), self.__MatchInput, 'Update')
            self.AddMatchString(compile(b'(Chn|Aud|Vid)0([0-5])\r\n'), self.__MatchInput, 'Set')
            self.AddMatchString(compile(b'Rly0([1-6])\*([0-1])\r\n'), self.__MatchRelay, None)
            self.AddMatchString(compile(b'Trb(0\d|10)\r\n'), self.__MatchTreble, None)
            self.AddMatchString(compile(b'Inp0([1-5]) Typ=([12])\r\n'), self.__MatchInputType, None)
            self.AddMatchString(compile(b'Vol0([0-3]\d|40)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
        if 'Serial' not in self.ConnectionType:
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')


    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'Off': '0',
            'On': '1'
        }

        AudioMuteCmdString = '{0}Z\r\n'.format(AudioMuteStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z\r\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        AudioGainAttenuationConstraints = {
            'Min': -40,
            'Max': 30
        }
        ChannelConstraints = {
            'Min': 1,
            'Max': 5
        }
        channel = qualifier['Input']
        AudioGainAttenuationCmdString = None
        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max'] and AudioGainAttenuationConstraints['Min'] <= value <= AudioGainAttenuationConstraints['Max']:
            if value >= 0:
                AudioGainAttenuationCmdString = '{0}*{1}G\r\n'.format(channel, value)
            elif value < 0:
                AudioGainAttenuationCmdString = '{0}*{1}g\r\n'.format(channel, -value)
            if AudioGainAttenuationCmdString:
                self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 5
        }
        channel = qualifier['Input']

        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max']:
            AudioGainAttenuationCmdString = '{0}*G\r\n'.format(channel)
            self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        value = int(match.group(2).decode())
        input_ = match.group(1).decode()

        qualifier = {'Input': input_}
        self.WriteStatus('AudioGainAttenuation', value, qualifier)

    def SetBass(self, value, qualifier):

        BassConstraints = {
            'Min': -10,
            'Max': 10
        }

        if BassConstraints['Min'] <= value <= BassConstraints['Max']:
            scale = (value * 0.5) + 5
            BassCmdString = '{0}<\r\n'.format(int(scale))
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '<\r\n'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        scale = int(match.group(1).decode())
        value = (2 * scale) - 10
        self.WriteStatus('Bass', value, None)

    def SetDisplayMute(self, value, qualifier):

        DisplayMuteStateValues = {
            'Off': '0',
            'On': '1'
        }

        DisplayMuteCmdString = '{0}M\r\n'.format(DisplayMuteStateValues[value])
        self.__SetHelper('DisplayMute', DisplayMuteCmdString, value, qualifier)

    def UpdateDisplayMute(self, value, qualifier):

        DisplayMuteCmdString = 'M\r\n'
        self.__UpdateHelper('DisplayMute', DisplayMuteCmdString, value, qualifier)

    def __MatchDisplayMute(self, match, tag):

        DisplayMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = DisplayMuteStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayMute', value, None)

    def SetDisplayPower(self, value, qualifier):

        DisplayPowerStateValues = {
            'Off': '0',
            'On': '1'
        }

        DisplayPowerCmdString = '{0}P\r\n'.format(DisplayPowerStateValues[value])
        self.__SetHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)

    def UpdateDisplayPower(self, value, qualifier):

        DisplayPowerCmdString = 'P\r\n'
        self.__UpdateHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)

    def __MatchDisplayPower(self, match, tag):

        DisplayPowerStateNames = {
            '0': 'Off',
            '1': 'On',
            '2': 'Cooling',
            '3': 'Warming'
        }

        value = DisplayPowerStateNames[match.group(1).decode()]
        self.WriteStatus('DisplayPower', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3',
            'Off': '0'
        }
        commandString = '{0}X\r\n'.format(ExecutiveModeStateValues[value])
        self.__SetHelper('ExecutiveMode', commandString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        commandString = 'X\r\n'
        self.__UpdateHelper('ExecutiveMode', commandString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3'
        }

        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputTypeValues = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }

        ChannelConstraints = {
            'Min': 0,
            'Max': 5
        }

        if ChannelConstraints['Min'] <= int(value) <= ChannelConstraints['Max']:
            InputCmdString = '{0}{1}\r\n'.format(value, InputTypeValues[qualifier['Type']])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I\r\n'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        InputTypeNames = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'Chn': 'Audio/Video'
        }

        if tag == 'Set':
            value = match.group(2).decode()
            Type = InputTypeNames[match.group(1).decode()]
            if Type != 'Audio/Video':
                qualifier = {'Type': Type}
                self.WriteStatus('Input', value, qualifier)
            else:
                for type_ in ['Audio', 'Video', 'Audio/Video']:
                    qualifier = {'Type': type_}
                    self.WriteStatus('Input', value, qualifier)

        if tag == 'Update':
            videoInputValue = match.group(1).decode()
            audioInputValue = match.group(2).decode()

            if videoInputValue == audioInputValue:
                AVInputValue = videoInputValue
            else:
                AVInputValue = '0'

            self.WriteStatus('Input', audioInputValue, {'Type': 'Audio'})
            self.WriteStatus('Input', videoInputValue, {'Type': 'Video'})
            self.WriteStatus('Input', AVInputValue, {'Type': 'Audio/Video'})

    def SetRelay(self, value, qualifier):

        RelayStateValues = {
            'Open': '0',
            'Close': '1'
        }

        RelayConstraints = {
            'Min': 1,
            'Max': 6
        }

        RelaySelect = qualifier['Relay']

        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max']:
            RelayCmdString = '{0}*{1}O\r\n'.format(RelaySelect, RelayStateValues[value])
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        RelayConstraints = {
            'Min': 1,
            'Max': 6
        }

        RelaySelect = qualifier['Relay']

        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max']:
            RelayCmdString = '{0}O\r\n'.format(RelaySelect)
            self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)
        else:
            Self.Discard('Invalid Command')

    def __MatchRelay(self, match, tag):

        RelayStateNames = {
            '0': 'Open',
            '1': 'Close'
        }

        value = RelayStateNames[match.group(2).decode()]
        RelaySelect = match.group(1).decode()

        qualifier = {'Relay': RelaySelect}
        self.WriteStatus('Relay', value, qualifier)

    def SetRelayPulse(self, value, qualifier):

        RelayConstraints = {
            'Min': 1,
            'Max': 6
        }

        RelayPulseConstraints = {
            'Min': 0.02,
            'Max': 1310.7
        }

        RelaySelect = qualifier['Relay']

        if RelayConstraints['Min'] <= int(RelaySelect) <= RelayConstraints['Max'] and RelayPulseConstraints['Min'] <= value <= RelayPulseConstraints['Max']:
            RelayPulseTime = int(value / 0.02)
            RelayPulseCmdString = '{0}*3*{1}O\r\n'.format(RelaySelect, RelayPulseTime)
            self.__SetHelper('RelayPulse', RelayPulseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelayPulse')

    def SetTreble(self, value, qualifier):

        TrebleConstraints = {
            'Min': -10,
            'Max': 10
        }

        if TrebleConstraints['Min'] <= value <= TrebleConstraints['Max']:
            scale = (value * 0.5) + 5
            TrebleCmdString = '{0}>\r\n'.format(int(scale))
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '>\r\n'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        scale = int(match.group(1).decode())
        value = (2 * scale) - 10
        self.WriteStatus('Treble', value, None)

    def SetInputType(self, value, qualifier):

        InputTypeValues = {
            'RGB': '1',
            'Video': '2'
        }

        ChannelConstraints = {
            'Min': 1,
            'Max': 5
        }
        channel = qualifier['Input']
        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max']:
            InputTypeCmdString = '{0}*{1}\\\r\n'.format(channel, InputTypeValues[value])
            self.__SetHelper('InputType', InputTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputType')

    def UpdateInputType(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 5
        }
        channel = qualifier['Input']

        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max']:
            InputTypeCmdString = '{0}\\\r\n'.format(channel)
            self.__UpdateHelper('InputType', InputTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputType')

    def __MatchInputType(self, match, tag):

        InputTypeNames = {
            '1': 'RGB',
            '2': 'Video'
        }

        value = InputTypeNames[match.group(2).decode()]
        input_ = match.group(1).decode()
        qualifier = {'Input': input_}
        self.WriteStatus('InputType', value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 40
        }

        if VolumeConstraints['Min'] <= int(value) <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V\r\n'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = (int(match.group(1)))
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
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

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):

        DeviceErrorCodes = {
            '01' : 'Invalid input number (too large)',
            '12' : 'Invalid port number',
            '13' : 'Invalid value',
            '14' : 'Not valid for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
            '23' : 'Checksum error (for file uploads)',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '27' : 'Invalid event number',
            '28' : 'Bad filename or file not found'
        }

        if match.group(1).decode() in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode()]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
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
            raise AttributeError(command, 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        #check incoming data if it matched any expected data from device module
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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