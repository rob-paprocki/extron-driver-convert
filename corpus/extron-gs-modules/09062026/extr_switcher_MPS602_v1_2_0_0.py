from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
from extronlib.system import Wait, ProgramLog


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
        self.VerboseDisabled = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInputFormat': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'Input': {'Parameters': ['Tie Type'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MicGain': {'Status': {}},
            'MicMute': {'Status': {}},
            'MicTalkOverThreshold': {'Status': {}},
            'ProgramAudioDucking': {'Status': {}},
            'RGBBreakaway': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.MaxInput = 6

        self.LevelTypes = {
            'InputGain': {'Min': -18, 'Max': 24},
            'MicGain': {'Min': -18, 'Max': 60},
            'MicTalkOverThreshold': {'Min': 0, 'Max': 30},
            'ProgramAudioDucking': {'Min': 0, 'Max': 30},
            'Volume': {'Min': 0, 'Max': 100},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'In(?P<input>[1-6]) Aud(?P<gain>[+-][0-9]{1,2})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'Amt(?P<mute>[01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Ausw(?P<autosw>[0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(compile(b'Exe(?P<executivemode>[0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'HdcpE(?P<hdcp3>[01]) (?P<hdcp4>[01]) (?P<hdcp5>[01]) (?P<hdcp6>[01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI(?P<hdcp3>[012]) (?P<hdcp4>[012]) (?P<hdcp5>[012]) (?P<hdcp6>[012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'In(?P<input>[0-6]) (?P<type>Vid|All)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'(?P<type>Pra) (?P<input>[0-6])\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'Sig(?P<in1>[01]) (?P<in2>[01]) (?P<in3>[01]) (?P<in4>[01]) (?P<in5>[01]) (?P<in6>[01])\*[01] [01]\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Mix(?P<mute>[01])\r\n'), self.__MatchMicMute, None)
            self.AddMatchString(compile(b'Thr(?P<threshold>[0-9]{1,2})\r\n'), self.__MatchMicTalkOverThreshold, None)
            self.AddMatchString(compile(b'Adl(?P<ducking>[0-9]{1,2})\r\n'), self.__MatchProgramAudioDucking, None)
            self.AddMatchString(compile(b'In(?P<input>[12]) RGB\r\n'), self.__MatchRGBBreakaway, None)
            self.AddMatchString(compile(b'Vmt(?P<mute>[01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Vol(?P<volume>[0-9]{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'(?P<error>E[012][0-9])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerbose, None)

            self.LastUpdateTime = {'HDCPInputAuthorization': 0, 'HDCPInputStatus': 0, 'Input': 0, 'InputSignalStatus': 0}

    def __MatchVerbose(self, match, tag):
        self.VerboseDisabled = False

    def SetAudioInputFormat(self, value, qualifier):

        AudioInputFormatState = {
            'Embedded': '0',
            'Analog': '1',
            'Auto': '2',
        }

        AudioInputFormatName = {
            '0': 'Embedded',
            '1': 'Analog',
            '2': 'Auto',
        }

        input = int(qualifier['Input'])
        if 3 <= input <= self.MaxInput:
            AudioInputFormatCmdString = 'WI{0}*{1}AFMT\r'.format(input, AudioInputFormatState[value])
            res = self.__SetHelperSync('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)
            if res:
                try:
                    found = match(compile('AfmtI\*([0-2])\r\n'), res)
                    if found:
                        value = AudioInputFormatName[found.group(1)]
                        self.WriteStatus('AudioInputFormat', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Input Format: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for SetAudioInputFormat')

    def UpdateAudioInputFormat(self, value, qualifier):

        AudioInputFormatName = {
            '0': 'Embedded',
            '1': 'Analog',
            '2': 'Auto',
        }
        input_ = int(qualifier['Input'])
        if 3 <= input_ <= self.MaxInput:
            res = self.__UpdateHelperSync('AudioInputFormat', 'WI{0}AFMT\r'.format(input_), value, qualifier)
            if res:
                try:
                    found = match(compile('AfmtI\*([0-2])\r\n'), res)
                    if found:
                        value = AudioInputFormatName[found.group(1)]
                        self.WriteStatus('AudioInputFormat', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Input Format: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateAudioInputFormat')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        AudioMuteCmdString = '{0}Z'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'Z', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('mute').decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeState = {
            'Highest Active Input': '1',
            'Lowest Active Input': '2',
            'Off': '0',
        }
        AutoSwitchModeCmdString = 'W{0}AUSW\r'.format(AutoSwitchModeState[value])
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        self.__UpdateHelper('AutoSwitchMode', 'WAUSW\r', value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('autosw').decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('executivemode').decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = {
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        HDCPInputAuthorizationState = {
            'On': '1',
            'Off': '0'
        }

        HDCPInputAuthorizationName = {
            '1': 'On',
            '0': 'Off',
        }

        input_ = qualifier['Input']
        HDCPInputAuthorizationCmdString = 'WE{0}*{1}HDCP\r'.format(InputStates[input_], HDCPInputAuthorizationState[value])
        res = self.__SetHelperSync('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        if res:
            try:
                found = match(compile('HdcpE(?P<input>[3456])\*(?P<hdcp>[01])\r\n'), res)
                self.WriteStatus('HDCPInputAuthorization', HDCPInputAuthorizationName[found.group('hdcp')], {'Input': InputStates[found.group('input')]})
            except (KeyError, IndexError):
                self.Error(['HDCP Input Authorization: Invalid/Unexpected Response'])

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'WEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        HDCPInputAuthorizationName = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('HDCPInputAuthorization', HDCPInputAuthorizationName[match.group('hdcp3').decode()], {'Input': '3'})
        self.WriteStatus('HDCPInputAuthorization', HDCPInputAuthorizationName[match.group('hdcp4').decode()], {'Input': '4'})
        self.WriteStatus('HDCPInputAuthorization', HDCPInputAuthorizationName[match.group('hdcp5').decode()], {'Input': '5'})
        self.WriteStatus('HDCPInputAuthorization', HDCPInputAuthorizationName[match.group('hdcp6').decode()], {'Input': '6'})

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'WIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'Source Connected and HDCP',
            '2': 'Source Connected and No HDCP'
        }

        self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group('hdcp3').decode()], {'Input': '3'})
        self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group('hdcp4').decode()], {'Input': '4'})
        self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group('hdcp5').decode()], {'Input': '5'})
        self.WriteStatus('HDCPInputStatus', ValueStateValues[match.group('hdcp6').decode()], {'Input': '6'})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'WOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sync Detected',
            '1': 'Sync Detected with HDCP',
            '2': 'Sync Detected with No HDCP'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInput(self, value, qualifier):

        TieTypeValue = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$',
        }
        input_ = int(value)
        TieType = qualifier['Tie Type']
        if 0 <= input_ <= self.MaxInput:
            InputCmdString = '{0}{1}'.format(input_, TieTypeValue[TieType])

            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        AudioRes = self.__UpdateHelperSync('Input', '$', value, qualifier)
        VideoRes = self.__UpdateHelperSync('Input', '%', value, qualifier)

        if AudioRes and VideoRes:
            try:
                AudioMatch = match(compile('Pra ([0-6])\r\n'), AudioRes)
                if AudioMatch:
                    self.WriteStatus('Input', AudioMatch.group(1), {'Tie Type': 'Audio'})
                VideoMatch = match(compile('In([0-6]) Vid\r\n'), VideoRes)
                if VideoMatch:
                    self.WriteStatus('Input', VideoMatch.group(1), {'Tie Type': 'Video'})

                if AudioMatch and VideoMatch:
                    if AudioMatch.group(1) == VideoMatch.group(1):
                        self.WriteStatus('Input', AudioMatch.group(1), {'Tie Type': 'Audio/Video'})
                    else:
                        self.WriteStatus('Input', '0', {'Tie Type': 'Audio/Video'})
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/Unexpected Response'])

    def __MatchInput(self, match, tag):

        TieTypeStates = {
            'All': 'Audio/Video',
            'Vid': 'Video',
            'Pra': 'Audio'
        }

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '0': '0'
        }

        TieType = match.group('type').decode()

        qualifier = {}
        qualifier['Tie Type'] = TieTypeStates[TieType]
        value = ValueStateValues[match.group('input').decode()]

        if TieType == 'All' and not value == '0':
            self.WriteStatus('Input', value, {'Tie Type': 'Audio'})
            self.WriteStatus('Input', value, {'Tie Type': 'Video'})
        self.WriteStatus('Input', value, qualifier)

    def SetInputGain(self, value, qualifier):

        input = int(qualifier['Input'])
        if 1 <= input <= self.MaxInput and self.__CheckValidLevelValue('InputGain', value):
            if value < 0:
                InputGainCmdString = '{0}*{1}g'.format(input, abs(value))
            else:
                InputGainCmdString = '{0}*{1}G'.format(input, abs(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.MaxInput:
            res = self.__UpdateHelperSync('InputGain', '{0}G'.format(input_), value, qualifier)
            if res:
                try:
                    found = match(compile('Aud(?P<gain>[+-][0-9]{1,2})\r\n'), res)
                    if found:
                        value = int(found.group('gain'))
                        self.WriteStatus('InputGain', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Gain: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group('input').decode()]
        value = int(match.group('gain').decode())
        self.WriteStatus('InputGain', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', 'W0LS\r', value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in1').decode()], {'Input': '1'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in2').decode()], {'Input': '2'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in3').decode()], {'Input': '3'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in4').decode()], {'Input': '4'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in5').decode()], {'Input': '5'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group('in6').decode()], {'Input': '6'})

    def SetMicGain(self, value, qualifier):

        if self.__CheckValidLevelValue('MicGain', value):
            if value < 0:
                MicGainCmdString = '16*{0}g'.format(abs(value))
            else:
                MicGainCmdString = '16*{0}G'.format(abs(value))
            res = self.__SetHelperSync('MicGain', MicGainCmdString, value, qualifier)
            if res:
                try:
                    found = match(compile('Aud(?P<gain>[+-][0-9]{1,2})\r\n'), res)
                    if found:
                        self.WriteStatus('MicGain', int(found.group('gain')), None)
                except (KeyError, IndexError):
                    self.Error(['Mic Gain: Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        res = self.__UpdateHelperSync('MicGain', '16G', value, qualifier)
        if res:
            try:
                found = match(compile('Aud(?P<gain>[+-][0-9]{1,2})\r\n'), res)
                if found:
                    self.WriteStatus('MicGain', int(found.group('gain')), None)
            except (KeyError, IndexError):
                self.Error(['Mic Gain: Invalid/Unexpected Response'])

    def SetMicMute(self, value, qualifier):

        MicMuteState = {
            'Off': '0',
            'On': '1',
        }
        MicMuteCmdString = '{0}M'.format(MicMuteState[value])
        self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)

    def UpdateMicMute(self, value, qualifier):

        self.__UpdateHelper('MicMute', 'M', value, qualifier)

    def __MatchMicMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('mute').decode()]
        self.WriteStatus('MicMute', value, None)

    def SetMicTalkOverThreshold(self, value, qualifier):

        if self.__CheckValidLevelValue('MicTalkOverThreshold', value):
            MicTalkOverThresholdCmdString = '{0}*2#'.format(abs(value))
            self.__SetHelper('MicTalkOverThreshold', MicTalkOverThresholdCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicTalkOverThreshold')

    def UpdateMicTalkOverThreshold(self, value, qualifier):

        res = self.__UpdateHelperSync('MicTalkOverThreshold', '2#', value, qualifier)
        if res:
            try:
                found = match(compile('(?P<threshold>[0-9]{1,2})\r\n'), res)
                if found:
                    value = int(found.group('threshold'))
                    self.WriteStatus('MicTalkOverThreshold', value, None)
            except (KeyError, IndexError):
                self.Error(['Mic Talk-Over Threshold: Invalid/Unexpected Response'])

    def __MatchMicTalkOverThreshold(self, match, tag):

        value = int(match.group('threshold').decode())
        self.WriteStatus('MicTalkOverThreshold', value, None)

    def SetProgramAudioDucking(self, value, qualifier):

        if self.__CheckValidLevelValue('ProgramAudioDucking', value):
            ProgramAudioDuckingCmdString = '{0}*58#'.format(abs(value))
            self.__SetHelper('ProgramAudioDucking', ProgramAudioDuckingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramAudioDucking')

    def UpdateProgramAudioDucking(self, value, qualifier):

        res = self.__UpdateHelperSync('ProgramAudioDucking', '58#', value, qualifier)
        if res:
            try:
                found = match(compile('(?P<ducking>[0-9]{1,2})\r\n'), res)
                if found:
                    value = int(found.group('ducking'))
                    self.WriteStatus('ProgramAudioDucking', value, None)
            except (KeyError, IndexError):
                self.Error(['Program Audio Ducking: Invalid/Unexpected Response'])

    def __MatchProgramAudioDucking(self, match, tag):

        value = int(match.group('ducking').decode())
        self.WriteStatus('ProgramAudioDucking', value, None)

    def SetRGBBreakaway(self, value, qualifier):

        input_ = int(value)
        if 1 <= input_ <= 2:
            RGBBreakawayCmdString = '{0}&'.format(input_)
            self.__SetHelper('RGBBreakaway', RGBBreakawayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRGBBreakaway')

    def UpdateRGBBreakaway(self, value, qualifier):

        self.__UpdateHelper('RGBBreakaway', '&', value, qualifier)

    def __MatchRGBBreakaway(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2'
        }

        value = ValueStateValues[match.group('input').decode()]
        self.WriteStatus('RGBBreakaway', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        VideoMuteCmdString = '{0}B'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.__UpdateHelper('VideoMute', 'B', value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group('mute').decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if self.__CheckValidLevelValue('Volume', value):
            self.__SetHelper('Volume', '{0}V'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'V', value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group('volume').decode())
        self.WriteStatus('Volume', value, None)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid channel number (too large)',
            'E06': 'Invalid switch command',
            'E10': 'Invalid command',
            'E13': 'Invalid value (out of range)',
            'E14': 'Not valid for this configuration',
            'E17': 'Invalid command for signal type',
            'E22': 'Busy',
            'E25': 'Device Not Present'
        }
        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, k, v)
                    self.Error([errorString])
                    response = ''
        return response

    def __CheckValidLevelValue(self, command, value):

        min_ = self.LevelTypes[command]['Min']
        max_ = self.LevelTypes[command]['Max']
        if min_ <= value <= max_:
            return True
        else:
            return False

    def __SetHelperSync(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
            return ''
        else:
            if self.VerboseDisabled:
                res = self.SendAndWait('w3cv\r\n', self.DefaultResponseTimeout, deliTag=b'\r\n')
                if res and b'Vrb3\r\n' in res:
                    self.VerboseDisabled = False
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

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
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseDisabled:
                self.Send('w3cv\r\n')
                self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __UpdateHelperSync(self, command, commandstring, value, qualifier):

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
                self.Error(['{}: Invalid/Unexpected Response'.format(command)])
                return ''
            else:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res.decode())

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid channel number (too large)',
            'E06': 'Invalid switch command',
            'E10': 'Invalid command',
            'E13': 'Invalid value (out of range)',
            'E14': 'Not valid for this configuration',
            'E17': 'Invalid command for signal type',
            'E22': 'Busy',
            'E25': 'Device Not Present'
        }

        value = DEVICE_ERROR_CODES.get(match.group('error').decode())
        if value:
            self.Error([value])

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
                result = search(regexString, self._ReceiveBuffer)
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