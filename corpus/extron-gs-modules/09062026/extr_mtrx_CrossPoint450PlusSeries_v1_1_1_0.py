from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
        self.Debug = False

        self.devicePassword = None

        self.Models = {
            'CrossPoint 450 Plus 128 HV': self.extr_15_66_128,
            'CrossPoint 450 Plus 128 HVA': self.extr_15_66_128,
            'CrossPoint 450 Plus 1616 HV': self.extr_15_66_1616,
            'CrossPoint 450 Plus 1616 HVA': self.extr_15_66_1616,
            'CrossPoint 450 Plus 168 HV': self.extr_15_66_168,
            'CrossPoint 450 Plus 168 HVA': self.extr_15_66_168,
            'CrossPoint 450 Plus 1212 HV': self.extr_15_66_1212,
            'CrossPoint 450 Plus 1212 HVA': self.extr_15_66_1212,
            'CrossPoint 450 Plus 124 HV': self.extr_15_66_124,
            'CrossPoint 450 Plus 124 HVA': self.extr_15_66_124,
            'CrossPoint 450 Plus 816 HV': self.extr_15_66_816,
            'CrossPoint 450 Plus 816 HVA': self.extr_15_66_816,
            'CrossPoint 450 Plus 84 HV': self.extr_15_66_84,
            'CrossPoint 450 Plus 84 HVA': self.extr_15_66_84,
            'CrossPoint 450 Plus 88 HV': self.extr_15_66_88,
            'CrossPoint 450 Plus 88 HVA': self.extr_15_66_88,
            'CrossPoint 450 Plus 3248 HV': self.extr_15_66_3248,
            'CrossPoint 450 Plus 3264 HV': self.extr_15_66_3264,
            'CrossPoint 450 Plus 4832 HV': self.extr_15_66_4832,
            'CrossPoint 450 Plus 4848 HV': self.extr_15_66_4848,
            'CrossPoint 450 Plus 4864 HV': self.extr_15_66_4864,
            'CrossPoint 450 Plus 6432 HV': self.extr_15_66_6432,
            'CrossPoint 450 Plus 6448 HV': self.extr_15_66_6448,
            'CrossPoint 450 Plus 6464 HV': self.extr_15_66_6464,
            'CrossPoint 450 Plus 3248 HVA': self.extr_15_66_3248,
            'CrossPoint 450 Plus 3264 HVA': self.extr_15_66_3264,
            'CrossPoint 450 Plus 4832 HVA': self.extr_15_66_4832,
            'CrossPoint 450 Plus 4848 HVA': self.extr_15_66_4848,
            'CrossPoint 450 Plus 4864 HVA': self.extr_15_66_4864,
            'CrossPoint 450 Plus 6432 HVA': self.extr_15_66_6432,
            'CrossPoint 450 Plus 6448 HVA': self.extr_15_66_6448,
            'CrossPoint 450 Plus 6464 HVA': self.extr_15_66_6464,
            'CrossPoint 450 Plus 2412 HV': self.extr_15_66_2412,
            'CrossPoint 450 Plus 2412 HVA': self.extr_15_66_2412,
            'CrossPoint 450 Plus 2424 HV': self.extr_15_66_2424,
            'CrossPoint 450 Plus 2424 HVA': self.extr_15_66_2424,
            'CrossPoint 450 Plus 3216 HV': self.extr_15_66_3216,
            'CrossPoint 450 Plus 3216 HVA': self.extr_15_66_3216,
            'CrossPoint 450 Plus 3232 HV': self.extr_15_66_3232,
            'CrossPoint 450 Plus 3232 HVA': self.extr_15_66_3232,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.refresh_matrix = False
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = []

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt(\d+)\*([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'In(\d+) Aud([+-][0-9]{2})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'In00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Rpr\d{2}\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Out(\d{2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'([VA])mt[01]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Mut([0-3]+)\r\n'), self.__MatchMute, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __QueuePassword(self):

        self.SetPassword()

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

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
        self.SetRefreshMatrix('All', None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('Mute', 'wvm\r', None, None)

    def __MatchMute(self, match, tag):

        stat = match.group(1).decode()
        output = 1

        for i in stat:
            if i == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '1':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            elif i == '2':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '3':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            output += 1

    def __MatchQik(self, match, tag):

        self.SetRefreshMatrix('All', None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.Debug = True
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]


        self.__UpdateHelper('AllMatrixTie', 'w0*1*1vc\r', None, None)
        self.__UpdateHelper('AllMatrixTie', 'w0*1*2vc\r', None, None)
        if self.OutputSize > 16:
            self.__UpdateHelper('AllMatrixTie', 'w0*17*1vc\r', None, None)
            self.__UpdateHelper('AllMatrixTie', 'w0*17*2vc\r', None, None)
        if self.OutputSize > 32:
            self.__UpdateHelper('AllMatrixTie', 'w0*33*1vc\r', None, None)
            self.__UpdateHelper('AllMatrixTie', 'w0*33*2vc\r', None, None)
        if self.OutputSize > 48:
            self.__UpdateHelper('AllMatrixTie', 'w0*49*1vc\r', None, None)
            self.__UpdateHelper('AllMatrixTie', 'w0*49*2vc\r', None, None)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:

                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Video'})
                    VideoList.add(output)

        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        av_counter_max = 16 if self.refresh_matrix else self.OutputSize
        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:

            if i != '--':
                if tag == 'Audio':
                    self.audio_status_counter += 1
                elif tag == 'Video':
                    self.video_status_counter += 1
                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                current_output += 1
            else:
                break

        if self.audio_status_counter == av_counter_max and self.video_status_counter == av_counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            AudioMuteCmdString = '{0}*{1}z'.format(channel, AudioMuteState[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            AudioMuteCmdString = '{0}z'.format(channel)
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):

        AudioMuteState = {
            b'0': 'Off',
            b'1': 'On',
        }

        value = AudioMuteState[match.group(2)]
        self.WriteStatus('AudioMute', value, {'Output': str(int(match.group(1)))})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }

        ExecutiveModeCmdString = '{0}x'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'x'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeState = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }

        value = ExecutiveModeState[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        GlobalAudioMuteCmdString = '{0}*z'.format(AudioMuteState[value])
        self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1'
        }

        GlobalVideoMuteCmdString = '{0}*b'.format(VideoMuteState[value])
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def SetInputGain(self, value, qualifier):

        channel = qualifier['Input']
        if -18 <= value <= 24 and 1 <= int(channel) <= self.InputSize:
            if value < 0:
                InputGainCmdString = '{0}*{1}g\r'.format(channel, abs(value))
            else:
                InputGainCmdString = '{0}*{1}G\r'.format(channel, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = qualifier['Input']
        if 1 <= int(channel) <= self.InputSize:
            InputGainCmdString = '{0}G\r'.format(channel)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        self.WriteStatus('InputGain', int(match.group(2).decode()), {'Input': str(int(match.group(1).decode()))})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        StatusStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputIndex in signal:
            self.WriteStatus('InputSignalStatus', StatusStateValues[inputIndex], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '\x24',
            'Video': '\x26',
            'Audio/Video': '\x21'
        }

        inputValue = int(qualifier['Input'])
        outputValue = qualifier['Output']
        tieType = TieTypeValues[qualifier['Tie Type']]

        if 0 <= inputValue <= self.InputSize:
            if outputValue == 'All':
                MatrixTieCommandCmdString = '{0}*{1}\r\n'.format(inputValue, tieType)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            elif 1 <= int(outputValue) <= self.OutputSize:
                MatrixTieCommandCmdString = '{0}*{1}{2}\r\n'.format(inputValue, outputValue, tieType)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __MatchOutputTieStatus(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video',
        }

        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                if i != input_ - 1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output - 1] = 'Untied'
                elif i == input_ - 1:
                    self.matrix_tie_status[i][output - 1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_ - 1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output - 1] = tietype
                elif input_ == 0 or i != input_ - 1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output - 1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video'
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        if self.matrix_tie_status[input_][output] == op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = tietype
                    else:
                        if self.matrix_tie_status[input_][output] == 'Audio/Video':
                            self.matrix_tie_status[input_][output] = op_tie_type
                        elif self.matrix_tie_status[input_][output] != op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Untied'

        elif tietype == 'Audio/Video':
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        self.matrix_tie_status[input_][output] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        state = {
            '1 - 16': 'w0*1*1vc\rw0*1*2vc\r',
            '17 - 24': 'w0*17*1vc\rw0*17*2vc\r',
            '17 - 32': 'w0*17*1vc\rw0*17*2vc\r',
            '33 - 48': 'w0*33*1vc\rw0*33*2vc\r',
            '49 - 64': 'w0*49*1vc\rw0*49*2vc\r'
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie(value, qualifier)
        else:
            self.refresh_matrix = True
            self.audio_status_counter = 0
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', state[value], value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            VideoMuteCmdString = '{0}*{1}b'.format(channel, VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            VideoMuteCmdString = '{0}b'.format(channel)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteState = {
            b'0': 'Off',
            b'1': 'On',
        }

        value = VideoMuteState[match.group(2)]
        self.WriteStatus('VideoMute', value, {'Output': str(int(match.group(1)))})

    def SetVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 0 <= value <= 64 and 1 <= channel <= self.OutputSize:
            VolumeCmdString = '{0}*{1}v'.format(channel, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            VolumeCmdString = '{0}V'.format(channel)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        value = int(match.group(2))
        self.WriteStatus('Volume', value, {'Output': str(int(match.group(1)))})

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

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '1': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid value (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
        self.refresh_matrix = False
        self.VerboseDisabled = True

    def extr_15_66_84(self):

        self.InputSize = 8
        self.OutputSize = 4

    def extr_15_66_88(self):

        self.InputSize = 8
        self.OutputSize = 8

    def extr_15_66_816(self):

        self.InputSize = 8
        self.OutputSize = 16

    def extr_15_66_124(self):

        self.InputSize = 12
        self.OutputSize = 4

    def extr_15_66_128(self):

        self.InputSize = 12
        self.OutputSize = 8

    def extr_15_66_1212(self):

        self.InputSize = 12
        self.OutputSize = 12

    def extr_15_66_1616(self):

        self.InputSize = 16
        self.OutputSize = 16

    def extr_15_66_168(self):

        self.InputSize = 16
        self.OutputSize = 8

    def extr_15_66_2412(self):

        self.InputSize = 24
        self.OutputSize = 12

    def extr_15_66_2424(self):

        self.InputSize = 24
        self.OutputSize = 24

    def extr_15_66_3216(self):

        self.InputSize = 32
        self.OutputSize = 16

    def extr_15_66_3232(self):

        self.InputSize = 32
        self.OutputSize = 32

    def extr_15_66_3248(self):

        self.InputSize = 32
        self.OutputSize = 48

    def extr_15_66_3264(self):

        self.InputSize = 32
        self.OutputSize = 64

    def extr_15_66_4832(self):

        self.InputSize = 48
        self.OutputSize = 32

    def extr_15_66_4848(self):

        self.InputSize = 48
        self.OutputSize = 48

    def extr_15_66_4864(self):

        self.InputSize = 48
        self.OutputSize = 64

    def extr_15_66_6432(self):

        self.InputSize = 64
        self.OutputSize = 32

    def extr_15_66_6448(self):

        self.InputSize = 64
        self.OutputSize = 48

    def extr_15_66_6464(self):

        self.InputSize = 64
        self.OutputSize = 64

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
