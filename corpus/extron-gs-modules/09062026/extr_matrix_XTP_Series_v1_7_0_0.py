from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from math import floor
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
            'XTP CrossPoint 1600': self.extr_15_3_1600,
            'XTP CrossPoint 3200': self.extr_15_3_3200,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'EDIDAssignment': {'Parameters': ['Input'], 'Status': {}},
            'EndpointTie': {'Parameters': ['Input', 'Tie Type'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PowerSupplyStatus': {'Parameters': ['Number'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'Relay': {'Parameters': ['Output', 'Relay'], 'Status': {}},
            'RelayPulse': {'Parameters': ['Output', 'Relay'], 'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
            'XTPInputPower': {'Parameters': ['Input'], 'Status': {}},
            'XTPOutputPower': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.devicePassword = None
        self.refresh_matrix = False

        if self.Unidirectional == 'False':

            self.AddMatchString(compile(b'Amt(\d+)\*([0-3])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exec([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'EdidA(0[1-9]|[1-2][0-9]|3[0-2])\*(00[1-9]|0[1-9][0-9]|1[0-3][0-9]|140)\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(compile(b'Etie([0-9]{2})\*([1-3])\*([1-3])\r\n'), self.__MatchEndpointTie, None)
            self.AddMatchString(compile(b'HdcpE(0[1-9]|[1-2][0-9]|3[0-2])\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI00\*([012]+)\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO00\*([0-7]+)\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Frq0+\*([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Vmt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt[0-3]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-7]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(b'Rely(\d+)\*(\d+)\*(1|0)\r\n'), self.__MatchRelay, None)
            self.AddMatchString(compile(b'Tst([01]\d)\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Out(\d{2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'PoecI00\*(?P<power>[01]{0,32})\r\n'), self.__MatchXTPInputPower, 'Polled')
            self.AddMatchString(compile(b'PoecI(?P<input>[0-9]{2})\*(?P<power>0|1)\*(?P<amount>00|13)\*(?P<status>[0-4])\r\n'), self.__MatchXTPInputPower, 'Unsolicited')
            self.AddMatchString(compile(b'PoecO00\*(?P<power>[01]{0,32})\r\n'), self.__MatchXTPOutputPower, 'Polled')
            self.AddMatchString(compile(b'PoecO(?P<output>[0-9]{2})\*(?P<power>0|1)\*(?P<amount>00|13)\*(?P<status>[0-4])\r\n'), self.__MatchXTPOutputPower, 'Unsolicited')
            self.AddMatchString(compile(b'Sts00\*(?P<voltage>[0-9]{1,2}\.[0-9]{2}( )){3,5}(?P<temperature>\+?[0-9]{3}\.[0-9]{2}( ))(?P<rpm>[0-9]{5}( )){2,7}(?P<power>[01]{2,4})\r\n'), self.__MatchPowerSupplyStatus, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'PrstR\d+\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

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
        self.SetRefreshMatrix('All', None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', 'wvm\r', value, qualifier)

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
                self.WriteStatus('AudioMute', 'Digital', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '3':
                self.WriteStatus('AudioMute', 'Digital', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            elif i == '4':
                self.WriteStatus('AudioMute', 'Analog', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '5':
                self.WriteStatus('AudioMute', 'Analog', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            elif i == '6':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '7':
                self.WriteStatus('AudioMute', 'On', {'Output': str(output)})
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            output += 1

    def __MatchQik(self, match, tag):
        self.SetRefreshMatrix('All', None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.__UpdateHelper('RefreshMatrix', 'w0*1*1vc\r', value, qualifier)
        self.__UpdateHelper('RefreshMatrix', 'w0*1*2vc\r', value, qualifier)
        if self.OutputSize > 16:
            self.__UpdateHelper('RefreshMatrix', 'w0*17*1vc\r', value, qualifier)
            self.__UpdateHelper('RefreshMatrix', 'w0*17*2vc\r', value, qualifier)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

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

            if tag == 'Audio':
                self.audio_status_counter += 1
            elif tag == 'Video':
                self.video_status_counter += 1

            if i != '--':
                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag

                current_output += 1

        if self.audio_status_counter == av_counter_max and self.video_status_counter == av_counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '3',
            'Analog': '2',
            'Digital': '1',
        }

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(channel, AudioMuteState[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            self.__UpdateHelper('AudioMute', '{0}z'.format(channel), value, qualifier)

    def __MatchAudioMute(self, match, qualifier):

        AudioMuteName = {
            '0': 'Off',
            '3': 'On',
            '2': 'Analog',
            '1': 'Digital'
        }

        self.WriteStatus('AudioMute', AudioMuteName[match.group(2).decode()], {'Output': str(int(match.group(1)))})

    def UpdateEDIDAssignment(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            EDIDAssignmentCmdString = 'wA{0}EDID\r'.format(input_)
            self.__UpdateHelper('EDIDAssignment', EDIDAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDIDAssignment')

    def __MatchEDIDAssignment(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = self.EDIDValues[str(int(match.group(2).decode()))]
        self.WriteStatus('EDIDAssignment', value, qualifier)

    def SetEndpointTie(self, value, qualifier):

        TieTypeStates = {
            'Audio': '2',
            'Video': '1',
            'Audio/Video': '3'
        }

        endpoint = int(value)
        input_ = qualifier['Input']
        tie_type = TieTypeStates[qualifier['Tie Type']]

        if 1 <= int(input_) <= self.InputSize and 1 <= endpoint <= 3:
            EndpointTieCmdString = '\x1B{0}*{1}*{2}ETIE\r'.format(input_, endpoint, tie_type)
            self.__SetHelper('EndpointTie', EndpointTieCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEndpointTie')

    def UpdateEndpointTie(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            EndpointTieStatusCmdString = '\x1B{0}ETIE\r'.format(input_)
            self.__UpdateHelper('EndpointTie', EndpointTieStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEndpointTie')

    def __MatchEndpointTie(self, match, qualifier):

        input_res = str(int(match.group(1).decode()))
        audio_tie = match.group(3).decode()
        video_tie = match.group(2).decode()

        if audio_tie == video_tie:
            self.WriteStatus('EndpointTie', audio_tie, {'Input': input_res, 'Tie Type': 'Audio/Video'})
        else:

            self.WriteStatus('EndpointTie', '0', {'Input': input_res, 'Tie Type': 'Audio/Video'})

        self.WriteStatus('EndpointTie', audio_tie, {'Input': input_res, 'Tie Type': 'Audio'})
        self.WriteStatus('EndpointTie', video_tie, {'Input': input_res, 'Tie Type': 'Video'})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        self.__SetHelper('ExecutiveMode', '\x1B{0}EXEC\r'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', '\x1BEXEC\r', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off'
        }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1).decode()], None)

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '3',
            'Analog': '2',
            'Digital': '1',
        }
        self.__SetHelper('GlobalAudioMute', '{0}*z'.format(AudioMuteState[value]), value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        self.__SetHelper('GlobalVideoMute', '{0}*b'.format(VideoMuteState[value]), value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        states = {
            'On': '1',
            'Off': '0'
        }

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            HDCPInputAuthorizationCmdString = '\x1BE{0}*{1}HDCP\r'.format(input_.zfill(2), states[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            commandstring = '\x1BE{0}HDCP\r'.format(input_)
            self.__UpdateHelper('HDCPInputAuthorization', commandstring, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, qualifier):

        states = {
            '1': 'On',
            '0': 'Off'
        }

        input_ = int(match.group(1).decode())
        value = match.group(2).decode()

        self.WriteStatus('HDCPInputAuthorization', states[value], {'Input': str(input_)})

    def UpdateHDCPInputStatus(self, value, qualifier):
        self.__UpdateHelper('HDCPInputStatus', 'wI*HDCP\r', value, qualifier)

    def __MatchHDCPInputStatus(self, match, qualifier):

        HDCPInputStatus = {
            '0': 'No Source Connected',
            '2': 'No HDCP Content',
            '1': 'HDCP Content'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('HDCPInputStatus', HDCPInputStatus[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def UpdateHDCPOutputStatus(self, value, qualifier):
        self.__UpdateHelper('HDCPOutputStatus', 'wO*HDCP\r', value, qualifier)

    def __MatchHDCPOutputStatus(self, match, qualifier):

        HDCPOutputStatus = {
            '0': 'No monitor connected',
            '1': 'Monitor connected, not encrypted',
            '2': 'No monitor connected',
            '3': 'Monitor connected, not encrypted',
            '4': 'No monitor connected',
            '5': 'Monitor connected, not encrypted',
            '6': 'No monitor connected',
            '7': 'Monitor connected, currently encrypted'
        }

        signal = match.group(1).decode()
        outputNumber = 1
        for output in signal:
            self.WriteStatus('HDCPOutputStatus', HDCPOutputStatus[output], {'Output': str(outputNumber)})
            outputNumber += 1

    def UpdateInputSignalStatus(self, value, qualifier):
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active'
        }
        signal = match.group(1).decode()
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatus[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '\x24',
            'Video': '\x26',
            'Audio/Video': '\x21'
        }

        input_ = int(qualifier['Input'])
        output = qualifier['Output']
        tieType = qualifier['Tie Type']
        outrange = ['All']
        for i in range(1, self.OutputSize + 1):
            outrange.append(str(i))

        if output not in outrange:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif input_ < 0 or input_ > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            output = '' if output == 'All' else output
            self.__SetHelper('MatrixTieCommand', '{0}*{1}{2}'.format(input_, output, TieTypeValues[tieType]), input_, qualifier)

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

    def UpdatePowerSupplyStatus(self, value, qualifier):
        PowerSupplyStatusCmdString = 'S\r'
        self.__UpdateHelper('PowerSupplyStatus', PowerSupplyStatusCmdString, value, qualifier)

    def __MatchPowerSupplyStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Installed/Normal',
            '0': 'Not Installed/Failed'
        }
        max_ = len(match.group('power').decode())
        if max_ in [2, 4]:
            for number in range(0, 4):
                qualifier = {'Number': str(number + 1)}
                if number < max_:
                    value = ValueStateValues[match.group('power').decode()[number]]
                else:
                    value = 'Not Installed/Failed'
                self.WriteStatus('PowerSupplyStatus', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) < 33:
            self.__SetHelper('PresetRecall', '\x1BR{0}PRST\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 < int(value) < 33:
            self.__SetHelper('PresetSave', '\x1BS{0}PRST\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        if value in self.RefreshMatrixValues:
            if value == 'All':
                self.UpdateAllMatrixTie(value, qualifier)
            else:
                self.refresh_matrix = True
                self.audio_status_counter = 0
                self.video_status_counter = 0
                self.__SetHelper('RefreshMatrix', self.RefreshMatrixValues[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def SetRelay(self, value, qualifier):

        RelayState = {
            'Close': '1',
            'Open': '0',
        }
        
        output = int(qualifier['Output'])
        relay = int(qualifier['Relay'])

        if output < 1 or output > self.OutputSize:
            self.Discard('Invalid Command for SetRelay')
        elif relay < 1 or relay > 2:
            self.Discard('Invalid Command for SetRelay')
        else:
            self.__SetHelper('Relay', 'w{0}*{1}*{2}RELY\r'.format(output, relay, RelayState[value]), value, qualifier)

    def UpdateRelay(self, value, qualifier):

        output = int(qualifier['Output'])
        relay = int(qualifier['Relay'])

        if output < 1 or output > self.OutputSize:
            self.Discard('Invalid Command for UpdateRelay')
        elif relay < 1 or relay > 2:
            self.Discard('Invalid Command for UpdateRelay')
        else:
            self.__UpdateHelper('Relay', 'w{0}*{1}RELY\r'.format(output, relay), value, qualifier)

    def __MatchRelay(self, match, qualifier):

        RelayState = {
            '1': 'Close',
            '0': 'Open',
        }
        output = int(match.group(1))
        relay = int(match.group(2))
        self.WriteStatus('Relay', RelayState[match.group(3).decode()], {'Output': str(output), 'Relay': str(relay)})

    def SetRelayPulse(self, value, qualifier):

        output = int(qualifier['Output'])
        relay = int(qualifier['Relay'])

        if output < 1 or output > self.OutputSize:
            self.Discard('Invalid Command for SetRelayPulse')
        elif relay < 1 or relay > 2:
            self.Discard('Invalid Command for SetRelayPulse')
        else:
            if 0.1 <= value <= 1048.5:
                self.__SetHelper('RelayPulse', 'w{0}*{1}*3*{2}RELY\r'.format(output, relay, floor((value * 62.5) + 0.5)), value, qualifier)
            else:
                self.Discard('Invalid Command for SetRelayPulse')

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Black Screen, No Audio (720p @ 50 Hz)': '2',
            'Black Screen, No Audio (720p @ 60 Hz)': '4',
            'Black Screen, No Audio (1080p @ 60 Hz)': '6',
            'Black Screen, Audio (720p @ 50 Hz)': '8',
            'Black Screen, Audio (720p @ 60 Hz)': '10',
            'Black Screen, Audio (1080p @ 60 Hz)': '12',
            'Color Bars, No Audio (720p @ 50 Hz)': '1',
            'Color Bars, No Audio (720p @ 60 Hz)': '3',
            'Color Bars, No Audio (1080p @ 60 Hz)': '5',
            'Color Bars, Audio (720p @ 50 Hz)': '7',
            'Color Bars, Audio (720p @ 60 Hz)': '9',
            'Color Bars, Audio (1080p @ 60 Hz)': '11',
            'Off': '0'
        }

        TestPatternCmdString = '\x1B{0}TEST\r'.format(ValueStateValues[value])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = '\x1BTEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '02': 'Black Screen, No Audio (720p @ 50 Hz)',
            '04': 'Black Screen, No Audio (720p @ 60 Hz)',
            '06': 'Black Screen, No Audio (1080p @ 60 Hz)',
            '08': 'Black Screen, Audio (720p @ 50 Hz)',
            '10': 'Black Screen, Audio (720p @ 60 Hz)',
            '12': 'Black Screen, Audio (1080p @ 60 Hz)',
            '01': 'Color Bars, No Audio (720p @ 50 Hz)',
            '03': 'Color Bars, No Audio (720p @ 60 Hz)',
            '05': 'Color Bars, No Audio (1080p @ 60 Hz)',
            '07': 'Color Bars, Audio (720p @ 50 Hz)',
            '09': 'Color Bars, Audio (720p @ 60 Hz)',
            '11': 'Color Bars, Audio (1080p @ 60 Hz)',
            '00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(channel, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize:
            self.__UpdateHelper('VideoMute', '{0}b'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2).decode()], {'Output': str(int(match.group(1)))})

    def SetVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetVolume')
        elif value < -64 or value > 0:
            self.Discard('Invalid Command for SetVolume')
        else:
            self.__SetHelper('Volume', '{0}*{1}v'.format(channel, value + 64), value, qualifier)

    def UpdateVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateVolume')
        else:
            self.__UpdateHelper('Volume', '{0}v'.format(channel), value, qualifier)

    def __MatchVolume(self, match, qualifier):
        self.WriteStatus('Volume', int(match.group(2)) - 64, {'Output': str(int(match.group(1)))})

    def SetXTPInputPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            XTPInputPowerCmdString = 'wI{0}*{1}POEC\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('XTPInputPower', XTPInputPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXTPInputPower')

    def UpdateXTPInputPower(self, value, qualifier):

        XTPInputPowerCmdString = 'wIPOEC\r'
        self.__UpdateHelper('XTPInputPower', XTPInputPowerCmdString, value, qualifier)

    def __MatchXTPInputPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Polled':
            input_ = 1
            for value in match.group('power').decode():
                if input_ > self.InputSize:
                    break
                self.WriteStatus('XTPInputPower', ValueStateValues[value], {'Input': str(input_)})
                input_ += 1
        elif tag == 'Unsolicited':
            input_ = match.group('input').decode().lstrip('0')
            if 1 <= int(input_) <= self.InputSize:
                self.WriteStatus('XTPInputPower', ValueStateValues[match.group('power').decode()], {'Input': input_})

    def SetXTPOutputPower(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            XTPOutputPowerCmdString = 'wO{0}*{1}POEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('XTPOutputPower', XTPOutputPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXTPOutputPower')

    def UpdateXTPOutputPower(self, value, qualifier):
        XTPOutputPowerCmdString = 'wOPOEC\r'
        self.__UpdateHelper('XTPOutputPower', XTPOutputPowerCmdString, value, qualifier)

    def __MatchXTPOutputPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Polled':
            output = 1
            for value in match.group('power').decode():
                if output > self.OutputSize:
                    break
                self.WriteStatus('XTPOutputPower', ValueStateValues[value], {'Output': str(output)})
                output += 1
        elif tag == 'Unsolicited':
            output = match.group('output').decode().lstrip('0')
            if 1 <= int(output) <= self.OutputSize:
                self.WriteStatus('XTPOutputPower', ValueStateValues[match.group('power').decode()], {'Output': output})

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
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
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True
        self.refresh_matrix = False
        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

    def extr_15_3_1600(self):

        self.InputSize = 16
        self.OutputSize = 16

        self.RefreshMatrixValues = {
            'All': None
        }

        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': '1024x768 @ 50Hz (VGA)',
            '18': '1024x768 @ 60Hz (VGA)',
            '19': '1280x720 @ 50Hz (VGA)',
            '20': '1280x720 @ 60Hz (VGA)',
            '21': '1280x768 @ 50Hz (VGA)',
            '22': '1280x768 @ 60Hz (VGA)',
            '23': '1280x800 @ 50Hz (VGA)',
            '24': '1280x800 @ 60Hz (VGA)',
            '25': '1280x1024 @ 50Hz (VGA)',
            '26': '1280x1024 @ 60Hz (VGA)',
            '27': '1360x768 @ 50Hz (VGA)',
            '28': '1360x768 @ 60Hz (VGA)',
            '29': '1366x768 @ 50Hz (VGA)',
            '30': '1366x768 @ 60Hz (VGA)',
            '31': '1400x1050 @ 50Hz (VGA)',
            '32': '1400x1050 @ 60Hz (VGA)',
            '33': '1440x900 @ 50Hz (VGA)',
            '34': '1440x900 @ 60Hz (VGA)',
            '35': '1600x900 @ 50Hz (VGA)',
            '36': '1600x900 @ 60Hz (VGA)',
            '37': '1600x1200 @ 50Hz (VGA)',
            '38': '1600x1200 @ 60Hz (VGA)',
            '39': '1680x1050 @ 50Hz (VGA)',
            '40': '1680x1050 @ 60Hz (VGA)',
            '41': '1920x1080 @ 50Hz (VGA)',
            '42': '1920x1080 @ 60Hz (VGA)',
            '43': '1920x1200 @ 50Hz (VGA)',
            '44': '1920x1200 @ 60Hz (VGA)',
            '45': '2048x1080 @ 50Hz (VGA)',
            '46': '2048x1080 @ 60Hz (VGA)',
            '47': '1024x768 @ 50Hz (DVI)',
            '48': '1024x768 @ 60Hz (DVI)',
            '49': '1280x720 @ 50Hz (DVI)',
            '50': '1280x720 @ 60Hz (DVI)',
            '51': '1280x768 @ 50Hz (DVI)',
            '52': '1280x768 @ 60Hz (DVI)',
            '53': '1280x800 @ 50Hz (DVI)',
            '54': '1280x800 @ 60Hz (DVI)',
            '55': '1280x1024 @ 50Hz (DVI)',
            '56': '1280x1024 @ 60Hz (DVI)',
            '57': '1360x768 @ 50Hz (DVI)',
            '58': '1360x768 @ 60Hz (DVI)',
            '59': '1366x768 @ 50Hz (DVI)',
            '60': '1366x768 @ 60Hz (DVI)',
            '61': '1400x1050 @ 50Hz (DVI)',
            '62': '1400x1050 @ 60Hz (DVI)',
            '63': '1440x900 @ 50Hz (DVI)',
            '64': '1440x900 @ 60Hz (DVI)',
            '65': '1600x900 @ 50Hz (DVI)',
            '66': '1600x900 @ 60Hz (DVI)',
            '67': '1600x1200 @ 50Hz (DVI)',
            '68': '1600x1200 @ 60Hz (DVI)',
            '69': '1680x1050 @ 50Hz (DVI)',
            '70': '1680x1050 @ 60Hz (DVI)',
            '71': '1920x1080 @ 50Hz (DVI)',
            '72': '1920x1080 @ 60Hz (DVI)',
            '73': '1920x1200 @ 50Hz (DVI)',
            '74': '1920x1200 @ 60Hz (DVI)',
            '75': '2048x1080 @ 50Hz (DVI)',
            '76': '2048x1080 @ 60Hz (DVI)',
            '77': '1024x768 @ 50Hz (HDMI)',
            '78': '1024x768 @ 60Hz (HDMI)',
            '79': '1280x768 @ 50Hz (HDMI)',
            '80': '1280x768 @ 60Hz (HDMI)',
            '81': '1280x800 @ 50Hz (HDMI)',
            '82': '1280x800 @ 60Hz (HDMI)',
            '83': '1280x1024 @ 50Hz (HDMI)',
            '84': '1280x1024 @ 60Hz (HDMI)',
            '85': '1360x768 @ 50Hz (HDMI)',
            '86': '1360x768 @ 60Hz (HDMI)',
            '87': '1366x768 @ 50Hz (HDMI)',
            '88': '1366x768 @ 60Hz (HDMI)',
            '89': '1400x1050 @ 50Hz (HDMI)',
            '90': '1400x1050 @ 60Hz (HDMI)',
            '91': '1440x900 @ 50Hz (HDMI)',
            '92': '1440x900 @ 60Hz (HDMI)',
            '93': '1600x900 @ 50Hz (HDMI)',
            '94': '1600x900 @ 60Hz (HDMI)',
            '95': '1600x1200 @ 50Hz (HDMI)',
            '96': '1600x1200 @ 60Hz (HDMI)',
            '97': '1680x1050 @ 50Hz (HDMI)',
            '98': '1680x1050 @ 60Hz (HDMI)',
            '99': '1920x1200 @ 50Hz (HDMI)',
            '100': '1920x1200 @ 60Hz (HDMI)',
            '101': '2048x1080 @ 50Hz (HDMI)',
            '102': '2048x1080 @ 60Hz (HDMI)',
            '103': '480p 2Ch @ 60Hz ',
            '104': '576p 2Ch @ 50Hz ',
            '105': '720p 2Ch @ 50Hz ',
            '106': '720p 2Ch @ 60Hz',
            '107': '720p Multi-Ch @ 50Hz',
            '108': '720p Multi-Ch @ 60Hz',
            '109': '1080i 2Ch @ 50Hz',
            '110': '1080i 2Ch @ 60Hz',
            '111': '1080i Multi-Ch @ 50Hz',
            '112': '1080i Multi-Ch @ 60Hz',
            '113': '1080p 2Ch @ 50Hz',
            '114': '1080p 2Ch @ 60Hz',
            '115': '1080p Multi-Ch @ 50Hz',
            '116': '1080p Multi-Ch @ 60Hz',
            '117': 'User Assigned 1',
            '118': 'User Assigned 2',
            '119': 'User Assigned 3',
            '120': 'User Assigned 4',
            '121': 'User Assigned 5',
            '122': 'User Assigned 6',
            '123': 'User Assigned 7',
            '124': 'User Assigned 8'
        }

    def extr_15_3_3200(self):

        self.InputSize = 32
        self.OutputSize = 32
        self.RefreshMatrixValues = {
            'All': None,
            '1 - 16': 'w0*1*1vc\rw0*1*2vc\r',
            '17 - 32': 'w0*17*1vc\rw0*17*2vc\r',
        }
        self.EDIDValues = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5',
            '6': 'Output 6',
            '7': 'Output 7',
            '8': 'Output 8',
            '9': 'Output 9',
            '10': 'Output 10',
            '11': 'Output 11',
            '12': 'Output 12',
            '13': 'Output 13',
            '14': 'Output 14',
            '15': 'Output 15',
            '16': 'Output 16',
            '17': 'Output 17',
            '18': 'Output 18',
            '19': 'Output 19',
            '20': 'Output 20',
            '21': 'Output 21',
            '22': 'Output 22',
            '23': 'Output 23',
            '24': 'Output 24',
            '25': 'Output 25',
            '26': 'Output 26',
            '27': 'Output 27',
            '28': 'Output 28',
            '29': 'Output 29',
            '30': 'Output 30',
            '31': 'Output 31',
            '32': 'Output 32',
            '33': '1024x768 @ 50Hz (VGA)',
            '34': '1024x768 @ 60Hz (VGA)',
            '35': '1280x720 @ 50Hz (VGA)',
            '36': '1280x720 @ 60Hz (VGA)',
            '37': '1280x768 @ 50Hz (VGA)',
            '38': '1280x768 @ 60Hz (VGA)',
            '39': '1280x800 @ 50Hz (VGA)',
            '40': '1280x800 @ 60Hz (VGA)',
            '41': '1280x1024 @ 50Hz (VGA)',
            '42': '1280x1024 @ 60Hz (VGA)',
            '43': '1360x768 @ 50Hz (VGA)',
            '44': '1360x768 @ 60Hz (VGA)',
            '45': '1366x768 @ 50Hz (VGA)',
            '46': '1366x768 @ 60Hz (VGA)',
            '47': '1400x1050 @ 50Hz (VGA)',
            '48': '1400x1050 @ 60Hz (VGA)',
            '49': '1440x900 @ 50Hz (VGA)',
            '50': '1440x900 @ 60Hz (VGA)',
            '51': '1600x900 @ 50Hz (VGA)',
            '52': '1600x900 @ 60Hz (VGA)',
            '53': '1600x1200 @ 50Hz (VGA)',
            '54': '1600x1200 @ 60Hz (VGA)',
            '55': '1680x1050 @ 50Hz (VGA)',
            '56': '1680x1050 @ 60Hz (VGA)',
            '57': '1920x1080 @ 50Hz (VGA)',
            '58': '1920x1080 @ 60Hz (VGA)',
            '59': '1920x1200 @ 50Hz (VGA)',
            '60': '1920x1200 @ 60Hz (VGA)',
            '61': '2048x1080 @ 50Hz (VGA)',
            '62': '2048x1080 @ 60Hz (VGA)',
            '63': '1024x768 @ 50Hz (DVI)',
            '64': '1024x768 @ 60Hz (DVI)',
            '65': '1280x720 @ 50Hz (DVI)',
            '66': '1280x720 @ 60Hz (DVI)',
            '67': '1280x768 @ 50Hz (DVI)',
            '68': '1280x768 @ 60Hz (DVI)',
            '69': '1280x800 @ 50Hz (DVI)',
            '70': '1280x800 @ 60Hz (DVI)',
            '71': '1280x1024 @ 50Hz (DVI)',
            '72': '1280x1024 @ 60Hz (DVI)',
            '73': '1360x768 @ 50Hz (DVI)',
            '74': '1360x768 @ 60Hz (DVI)',
            '75': '1366x768 @ 50Hz (DVI)',
            '76': '1366x768 @ 60Hz (DVI)',
            '77': '1400x1050 @ 50Hz (DVI)',
            '78': '1400x1050 @ 60Hz (DVI)',
            '79': '1440x900 @ 50Hz (DVI)',
            '80': '1440x900 @ 60Hz (DVI)',
            '81': '1600x900 @ 50Hz (DVI)',
            '82': '1600x900 @ 60Hz (DVI)',
            '83': '1600x1200 @ 50Hz (DVI)',
            '84': '1600x1200 @ 60Hz (DVI)',
            '85': '1680x1050 @ 50Hz (DVI)',
            '86': '1680x1050 @ 60Hz (DVI)',
            '87': '1920x1080 @ 50Hz (DVI)',
            '88': '1920x1080 @ 60Hz (DVI)',
            '89': '1920x1200 @ 50Hz (DVI)',
            '90': '1920x1200 @ 60Hz (DVI)',
            '91': '2048x1080 @ 50Hz (DVI)',
            '92': '2048x1080 @ 60Hz (DVI)',
            '93': '1024x768 @ 50Hz (HDMI)',
            '94': '1024x768 @ 60Hz (HDMI)',
            '95': '1280x768 @ 50Hz (HDMI)',
            '96': '1280x768 @ 60Hz (HDMI)',
            '97': '1280x800 @ 50Hz (HDMI)',
            '98': '1280x800 @ 60Hz (HDMI)',
            '99': '1280x1024 @ 50Hz (HDMI)',
            '100': '1280x1024 @ 60Hz (HDMI)',
            '101': '1360x768 @ 50Hz (HDMI)',
            '102': '1360x768 @ 60Hz (HDMI)',
            '103': '1366x768 @ 50Hz (HDMI)',
            '104': '1366x768 @ 60Hz (HDMI)',
            '105': '1400x1050 @ 50Hz (HDMI)',
            '106': '1400x1050 @ 60Hz (HDMI)',
            '107': '1440x900 @ 50Hz (HDMI)',
            '108': '1440x900 @ 60Hz (HDMI)',
            '109': '1600x900 @ 50Hz (HDMI)',
            '110': '1600x900 @ 60Hz (HDMI)',
            '111': '1600x1200 @ 50Hz (HDMI)',
            '112': '1600x1200 @ 60Hz (HDMI)',
            '113': '1680x1050 @ 50Hz (HDMI)',
            '114': '1680x1050 @ 60Hz (HDMI)',
            '115': '1920x1200 @ 50Hz (HDMI)',
            '116': '1920x1200 @ 60Hz (HDMI)',
            '117': '2048x1080 @ 50Hz (HDMI)',
            '118': '2048x1080 @ 60Hz (HDMI)',
            '119': '480p 2Ch @ 60Hz ',
            '120': '576p 2Ch @ 50Hz ',
            '121': '720p 2Ch @ 50Hz ',
            '122': '720p 2Ch @ 60Hz',
            '123': '720p Multi-Ch @ 50Hz',
            '124': '720p Multi-Ch @ 60Hz',
            '125': '1080i 2Ch @ 50Hz',
            '126': '1080i 2Ch @ 60Hz',
            '127': '1080i Multi-Ch @ 50Hz',
            '128': '1080i Multi-Ch @ 60Hz',
            '129': '1080p 2Ch @ 50Hz',
            '130': '1080p 2Ch @ 60Hz',
            '131': '1080p Multi-Ch @ 50Hz',
            '132': '1080p Multi-Ch @ 60Hz',
            '133': 'User Assigned 1',
            '134': 'User Assigned 2',
            '135': 'User Assigned 3',
            '136': 'User Assigned 4',
            '137': 'User Assigned 5',
            '138': 'User Assigned 6',
            '139': 'User Assigned 7',
            '140': 'User Assigned 8'
        }

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
