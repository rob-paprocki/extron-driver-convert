from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, match, search
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
        self.Models = {
            'Crosspoint Ultra 1212 HV': self.extr_15_68_1212_HV,
            'Crosspoint Ultra 1212 HVA': self.extr_15_68_1212_HVA,
            'Crosspoint Ultra 128 HVA': self.extr_15_68_128_HVA,
            'Crosspoint Ultra 128 HV': self.extr_15_68_128_HV,
            'Crosspoint Ultra 1616 HVA': self.extr_15_68_1616_HVA,
            'Crosspoint Ultra 1616 HV': self.extr_15_68_1616_HV,
            'Crosspoint Ultra 168 HVA': self.extr_15_68_168_HVA,
            'Crosspoint Ultra 168 HV': self.extr_15_68_168_HV,
            'Crosspoint Ultra 84 HVA': self.extr_15_68_84_HVA,
            'Crosspoint Ultra 84 HV': self.extr_15_68_84_HV,
            'Crosspoint Ultra 88 HV': self.extr_15_68_88_HV,
            'Crosspoint Ultra 88 HVA': self.extr_15_68_88_HVA,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'InputTieStatusHV': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'MatrixTieCommandHV': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusHV': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Out(\d{2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'Amt(0|1)\r\n'), self.__MatchAMute, None)
            self.AddMatchString(compile(b'Vmt(0|1)\r\n'), self.__MatchVMute, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Amt(\d+)\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'In00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Rpr\d{2}\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d{2}) ([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2}) ([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
    
    def addOutputTieStatusMatchString(self):
        if self.modelisHV:
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|RGB))|(?:In(\d+) (All|Vid|RGB))\r\n'), self.__MatchOutputTieStatusHV, None)
        else:
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|RGB|Vid|Aud))|(?:In(\d+) (All|RGB|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            if self.devicePassword:
                self.Send('{0}\r\n'.format(self.devicePassword))
            else:
                self.MissingCredentialsLog('Password')

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
        self.SetRefreshMatrix(None, None)

    def __MatchAMute(self, match, tag):

        stat = match.group(1).decode()
        for i in range(self.OutputSize):
            if stat == '1':
                self.WriteStatus('AudioMute', 'On', {'Output': str(i + 1)})
            elif stat == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(i + 1)})

    def __MatchVMute(self, match, tag):

        stat = match.group(1).decode()

        for i in range(0, self.OutputSize):
            if stat == '1':
                self.WriteStatus('VideoMute', 'On', {'Output': str(i + 1)})
            elif stat == '0':
                self.WriteStatus('VideoMute', 'Off', {'Output': str(i + 1)})

    def __MatchQik(self, match, tag):

        self.SetRefreshMatrix(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        self.__SetHelper('RefreshMatrix', 'w0*1*1vc\r', value, qualifier)
        if not self.modelisHV:
            self.__SetHelper('RefreshMatrix', 'w0*1*2vc\r', value, qualifier)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(value, qualifier)

    def UpdateInputTieStatusHV(self, value, qualifier):
        self.UpdateAllMatrixTie(value, qualifier)

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(value, qualifier)

    def UpdateOutputTieStatusHV(self, value, qualifier):
        self.UpdateAllMatrixTie(value, qualifier)

    def InputTieStatusHelper(self, tie, output=None):

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        if self.modelisHV:
            for input_ in range(self.InputSize):
                for output in output_range:
                    self.WriteStatus('InputTieStatusHV', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})
        else:
            for input_ in range(self.InputSize):
                for output in output_range:
                    self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        if self.modelisHV:
            VideoList = set()
            if tie == 'Individual':
                output_range = range(output - 1, output)
            else:
                output_range = range(self.OutputSize)

            for input_ in range(self.InputSize):
                for output in output_range:
                    tietype = self.matrix_tie_status[input_][output]
                    if tietype == 'Video':
                        self.WriteStatus('OutputTieStatusHV', str(input_ + 1), {'Output': str(output + 1)})
                        VideoList.add(output)

            for o in output_range:
                if o not in VideoList:
                    self.WriteStatus('OutputTieStatusHV', '0', {'Output': str(o + 1)})

        else:
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

        if self.modelisHV:
            current_output = int(match.group(1))
            input_list = match.group(2).decode().split()
            counter_max = 16
            for i in input_list:
                self.video_status_counter += 1
                if i != '--':
                    if i != '00':
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                    current_output += 1

            if self.video_status_counter == counter_max:
                self.InputTieStatusHelper('All')
                self.OutputTieStatusHelper('All')
        else:
            current_output = int(match.group(1))
            input_list = match.group(2).decode().split()

            opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

            for i in input_list:
                if i != '--':
                    if i != '00':
                        if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                            self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                    current_output += 1

            if tag == 'Audio':
                self.InputTieStatusHelper('All')
                self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',

        }
        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(channel, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__UpdateHelper('AudioMute', '{0}z'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):
        AudioMuteName = {
            b'0': 'Off',
            b'1': 'On',

        }
        self.WriteStatus('AudioMute', AudioMuteName[match.group(2)], {'Output': str(int(match.group(1)))})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetGlobalAudioMute(self, value, qualifier):
        AudioMuteState = {
            'Off': '0',
            'On': '1',

        }
        self.__SetHelper('GlobalAudioMute', '{0}*z'.format(AudioMuteState[value]), value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):
        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        self.__SetHelper('GlobalVideoMute', '{0}*b'.format(VideoMuteState[value]), value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active',
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for input in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatus[input], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '\x24',
            'Video': '\x26',
            'Audio/Video': '\x21'
        }

        inputValue = qualifier['Input']
        outputValue = qualifier['Output']
        tieType = TieTypeValues[qualifier['Tie Type']]

        if 0 <= int(inputValue) <= self.InputSize:
            if outputValue == 'All' and tieType == '\x21':
                self.__SetHelper('MatrixTieCommand', '{0}!\r\n'.format(inputValue, tieType), value, qualifier)
            elif outputValue == 'All' and (tieType == '\x24' or tieType == '\x26'):
                for output in range(1, self.OutputSize + 1):
                    self.__SetHelper('MatrixTieCommand', '{0}*{1}{2}\r\n'.format(inputValue, output, tieType), value, qualifier)
            elif 1 <= int(outputValue) <= self.OutputSize:
                self.__SetHelper('MatrixTieCommand', '{0}*{1}{2}\r\n'.format(inputValue, outputValue, tieType), value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetMatrixTieCommandHV(self, value, qualifier):

        input_ = int(qualifier['Input'])
        output = qualifier['Output']

        if output == 'All':
            cmdStr = ''
            for o in range(1, self.OutputSize + 1):
                cmdStr = '{0}{1}*{2}&'.format(cmdStr, input_, o)
            self.__SetHelper('MatrixTieCommandHV', cmdStr, value, qualifier)
        else:
            self.__SetHelper('MatrixTieCommandHV', '{0}*{1}&'.format(input_, output), value, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchOutputTieStatusHV(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTieHV(match, None)
        else:
            self.__MatchAllTieHV(match, None)

    def __MatchIndividualTieHV(self, match, qualifier):

        output = int(match.group(1))
        input_ = int(match.group(2))

        for i in range(self.InputSize):
            current_tie = self.matrix_tie_status[i][output - 1]
            if i == input_ - 1:
                self.matrix_tie_status[i][output - 1] = 'Video'
            elif input_ == 0 or i != input_ - 1:
                if current_tie == 'Video':
                    self.matrix_tie_status[i][output - 1] = 'Untied'

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTieHV(self, match, qualifier):

        new_input = int(match.group(4))
        for output in range(self.OutputSize):
            for input_ in range(self.InputSize):
                if input_ == new_input - 1:
                    self.matrix_tie_status[input_][output] = 'Video'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

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
            'All': 'Audio/Video',
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

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(channel, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__UpdateHelper('VideoMute', '{0}b'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        self.WriteStatus('VideoMute', VideoMuteName[match.group(2)], {'Output': str(int(match.group(1)))})

    def SetVolume(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize and 0 <= value <= 64:
            self.__SetHelper('Volume', '{0}*{1}v'.format(channel, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            VolumeCmdString = '{0}V'.format(channel)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, fncN):
        self.WriteStatus('Volume', int(match.group(2)), {'Output': str(int(match.group(1)))})

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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
        self.VerboseDisabled = True

    def extr_15_68_1212_HV(self):

        self.modelisHV = True
        self.InputSize = 12
        self.OutputSize = 12

    def extr_15_68_1212_HVA(self):

        self.modelisHV = False
        self.InputSize = 12
        self.OutputSize = 12

    def extr_15_68_128_HV(self):

        self.modelisHV = True
        self.InputSize = 12
        self.OutputSize = 8

    def extr_15_68_128_HVA(self):

        self.modelisHV = False
        self.InputSize = 12
        self.OutputSize = 8

    def extr_15_68_1616_HV(self):

        self.modelisHV = True
        self.InputSize = 16
        self.OutputSize = 16

    def extr_15_68_1616_HVA(self):

        self.modelisHV = False
        self.InputSize = 16
        self.OutputSize = 16

    def extr_15_68_168_HV(self):

        self.modelisHV = True
        self.InputSize = 16
        self.OutputSize = 8

    def extr_15_68_168_HVA(self):

        self.modelisHV = False
        self.InputSize = 16
        self.OutputSize = 8

    def extr_15_68_84_HV(self):

        self.modelisHV = True
        self.InputSize = 8
        self.OutputSize = 4

    def extr_15_68_84_HVA(self):

        self.modelisHV = False
        self.InputSize = 8
        self.OutputSize = 4

    def extr_15_68_88_HV(self):

        self.modelisHV = True
        self.InputSize = 8
        self.OutputSize = 8

    def extr_15_68_88_HVA(self):

        self.modelisHV = False
        self.InputSize = 8
        self.OutputSize = 8

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
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
        self.addOutputTieStatusMatchString()

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
        self.addOutputTieStatusMatchString()

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
        self.addOutputTieStatusMatchString()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
