from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'MLS 506SA': self.extr_2_17_MASA,
            'MLS 506': self.extr_2_17_506,
            'MLS 506MA': self.extr_2_17_MASA,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'Bass': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'Treble': {'Parameters': ['Input'], 'Status': {}},
            'VideoConfiguration': {'Parameters': ['Input'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Vid(\d) Aud(\d) Clp(\d)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'(Chn|Aud|Vid)(\d)\r\n'), self.__MatchInputSingle, None)
            self.AddMatchString(re.compile(b'Vol(\d{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Amt(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'In(\d) Trb=(-|\+)(\d{2})\r\n'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'In(\d) Bas=(-|\+)(\d{2})\r\n'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'In(\d) Aud=(-|\+)(\d{2})\r\n'), self.__MatchAudioGainAttenuation, '506')
            self.AddMatchString(re.compile(b'In(\d) Aud=(\d{3})\r\n'), self.__MatchAudioGainAttenuation, '506MASA')
            self.AddMatchString(re.compile(b'Exe(0|1)\r\n'), self.__MatchExecutiveMode, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        Input = qualifier['Input']
        if self.InputConstraints['Min'] < int(Input) <= self.InputConstraints['Max']:
            if self.AudioGainConstraints['Min'] <= int(value) <= self.AudioGainConstraints['Max']:
                if value >= 0:
                    AudioGainCmdString = '{0}*{1}G'.format(Input, value)
                elif value < 0:
                    RemoveNegative = -value
                    AudioGainCmdString = '{0}*{1}g'.format(Input, RemoveNegative)
                self.__SetHelper('AudioGainAttenuation', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        Input = qualifier['Input']
        if self.InputConstraints['Min'] < int(Input) <= self.InputConstraints['Max']:
            AudioGainCmdString = '{0}*G'.format(Input)
            self.__UpdateHelper('AudioGainAttenuation', AudioGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def __MatchAudioGainAttenuation(self, match, tag):
        if tag == '506MASA':
            qualifier = {'Input': str(int(match.group(1).decode()))}
            value = int(match.group(2).decode())
            self.WriteStatus('AudioGainAttenuation', value, qualifier)
        elif tag == '506':
            qualifier = {'Input': str(int(match.group(1).decode()))}
            PostiveNegativeCheck = match.group(2).decode()
            if PostiveNegativeCheck == '+':
                value = int(match.group(3).decode())
            elif PostiveNegativeCheck == '-':
                value = int(match.group(3).decode())
                value = -value
            self.WriteStatus('AudioGainAttenuation', value, qualifier)


    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '1Z',
            'Off': '0Z',
        }
        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBass(self, value, qualifier):

        BassConstraints = {
            'Min': -14,
            'Max': 14
        }
        Convert = {
            -14: 0,
            -12: 1,
            -10: 2,
            -8: 3,
            -6: 4,
            -4: 5,
            -2: 6,
            0: 7,
            2: 8,
            4: 9,
            6: 10,
            8: 11,
            10: 12,
            12: 13,
            14: 14,
        }

        Channel = qualifier['Input']

        if self.InputConstraints['Min'] < int(Channel) <= self.InputConstraints['Max']:
            if BassConstraints['Min'] <= int(value) <= BassConstraints['Max']:
                BassCmdString = '{0}*{1}<'.format(Channel, Convert[value])
                self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        Channel = qualifier['Input']

        if self.InputConstraints['Min'] < int(Channel) <= self.InputConstraints['Max']:
            BassCmdString = '{0}*<'.format(Channel)
            self.__UpdateHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBass')

    def __MatchBass(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()))}
        PostiveNegativeCheck = match.group(2).decode()
        if PostiveNegativeCheck == '+':
            value = int(match.group(3).decode())
        elif PostiveNegativeCheck == '-':
            value = int(match.group(3).decode())
            value = -value
        self.WriteStatus('Bass', value, qualifier)

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
            '0': 'Off'
        }
        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        SwitchType = qualifier['Type']

        SwitchTypeNames = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }
        if int(value) < self.InputConstraints['Min'] or int(value) > self.InputConstraints['Max']:
            self.Discard('Invalid Command for SetInput')
        else:
            InputCmdString = '{0}{1}'.format(int(value), SwitchTypeNames[SwitchType])
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        videoInputValue = match.group(1).decode()
        audioInputValue = match.group(2).decode()

        if videoInputValue == audioInputValue:
            Channel = videoInputValue
        else:
            Channel = 0

        self.WriteStatus('Input', str(audioInputValue), {'Type': 'Audio'})
        self.WriteStatus('Input', str(videoInputValue), {'Type': 'Video'})
        self.WriteStatus('Input', str(Channel), {'Type': 'Audio/Video'})

    def __MatchInputSingle(self, match, tag):

        CurrentAud = ''
        CurrentVid = ''
        CurrentAud = self.ReadStatus('Input', {'Type': 'Audio'})
        CurrentVid = self.ReadStatus('Input', {'Type': 'Video'})

        Type = match.group(1).decode()
        InputValue = match.group(2).decode()

        if Type == 'Chn':
            self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
            self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
            self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
        elif Type == 'Aud':
            if InputValue == CurrentVid:
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
        elif Type == 'Vid':
            if InputValue == CurrentAud:
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio/Video'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Audio'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
                self.WriteStatus('Input', str(InputValue), {'Type': 'Video'})

    def SetTreble(self, value, qualifier):

        TrebleConstraints = {
            'Min': -14,
            'Max': 14
        }
        Convert = {
            -14: 0,
            -12: 1,
            -10: 2,
            -8: 3,
            -6: 4,
            -4: 5,
            -2: 6,
            0: 7,
            2: 8,
            4: 9,
            6: 10,
            8: 11,
            10: 12,
            12: 13,
            14: 14,
        }

        Channel = qualifier['Input']

        if self.InputConstraints['Min'] < int(Channel) <= self.InputConstraints['Max']:
            if TrebleConstraints['Min'] <= value <= TrebleConstraints['Max']:
                TrebleCmdString = '{0}*{1}>'.format(Channel, Convert[value])
                self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        Channel = qualifier['Input']

        if self.InputConstraints['Min'] < int(Channel) <= self.InputConstraints['Max']:
            TrebleCmdString = '{0}*>'.format(Channel)
            self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTreble')

    def __MatchTreble(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()))}
        PostiveNegativeCheck = match.group(2).decode()
        if PostiveNegativeCheck == '+':
            value = int(match.group(3).decode())
        elif PostiveNegativeCheck == '-':
            value = int(match.group(3).decode())
            value = -value
        self.WriteStatus('Treble', value, qualifier)

    def SetVideoConfiguration(self, value, qualifier):

        VideoConfigurationConstraints = {
            'Min': 1,
            'Max': 3
        }
        VideoConfigurationState = {
            'Video': '1',
            'YUV': '0'
        }

        Input = qualifier['Input']
        if VideoConfigurationConstraints['Min'] <= int(Input) <= VideoConfigurationConstraints['Max']:
            VideoConfigurationCmdString = '{0}*{1}\\'.format(Input, VideoConfigurationState[value])
            self.__SetHelper('VideoConfiguration', VideoConfigurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoConfiguration')

    def UpdateVideoConfiguration(self, value, qualifier):

        VideoConfigurationConstraints = {
            'Min': 1,
            'Max': 3
        }
        VideoConfigStates = {
            '0': 'YUV',
            '1': 'Video'
        }
        Input = qualifier['Input']
        if VideoConfigurationConstraints['Min'] <= int(Input) <= VideoConfigurationConstraints['Max']:
            VideoConfigurationCmdString = '{0}\\'.format(Input)
            response = self.__UpdateHelperSYNC('VideoConfiguration', VideoConfigurationCmdString, value, qualifier)
            if response:
                try:
                    value = VideoConfigStates[response[-7]]
                    self.WriteStatus('VideoConfiguration', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Video Configuration: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoConfiguration')

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

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

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

    def __UpdateHelperSYNC(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number (too large)',
            'E10': 'Invalid command',
            'E11': 'Invalid preset number',
            'E12': 'Invalid port number',
            'E13': 'Invalid parameter',
            'E14': 'Command not available for this configuration',
            'E17': 'System timed out',
            'E22': 'Busy',
            'E24': 'Privilege violation',
            'E25': 'Device not present',
            'E26': 'Maximum number of connections exceeded',
            'E27': 'Invalid event number',
            'E28': 'Bad filename or file not found',
            'E30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            'E31': 'Attempt to break port pass-through when it has not been set',
            'E32': 'Incorrect V-chip password'
        }
        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, k, v)
                    self.Error([errorString])
                    print(errorString)
                    response = ''
        return response

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def extr_2_17_506(self):

        self.InputConstraints = {
            'Min': 0,
            'Max': 6,
        }
        self.AudioGainConstraints = {
            'Min': -15,
            'Max': 9
        }

    def extr_2_17_MASA(self):

        self.InputConstraints = {
            'Min': 0,
            'Max': 7,
        }
        self.AudioGainConstraints = {
            'Min': 0,
            'Max': 100
        }

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
                self.Subscription[command] = {'method': {}}

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
        if command in self.Subscription:
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
        # handling incoming unsolicited data
        self._ReceiveBuffer += data
        # check incoming data if it matched any expected data from device module
        if self.CheckMatchedString() and len(self._ReceiveBuffer) > 10000:
            self._ReceiveBuffer = b''

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self._compile_list:
            self._compile_list[regex_string] = {'callback': callback, 'para': arg}

   # Check incoming unsolicited data to see if it was matched with device expectancy.
    def CheckMatchedString(self):
        for regexString in self._compile_list:
            while True:
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
