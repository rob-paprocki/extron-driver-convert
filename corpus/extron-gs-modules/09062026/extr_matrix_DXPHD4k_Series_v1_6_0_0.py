from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
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
            'DXP 44 HD 4K': self.extr_15_1865_44,
            'DXP 84 HD 4K': self.extr_15_1865_84,
            'DXP 88 HD 4K': self.extr_15_1865_88,
            'DXP 168 HD 4K': self.extr_15_1865_168,
            'DXP 1616 HD 4K': self.extr_15_1865_1616,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutputMute': {'Parameters': ['Output'], 'Status': {}},
            'EDIDAssignment': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIAudioOutputMute': {'Parameters': ['Output'], 'Status': {}},
            'InputFormat': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'Temperature': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMuteGlobal, None)
            self.AddMatchString(re.compile(b'Amt(0[1-9]|1[0-6])\*([0-7])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'EdidA(0[1-9]|1[0-6])\*(0[1-9]|[1-4][0-9])\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE(0[1-9]|1[0-6])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI(0[1-9]|1[0-6])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(0?[1-9]|1[0-6])\*([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Ityp(0[1-9]|1[0-6])\*([0-7])\r\n'), self.__MatchInputFormat, None)
            self.AddMatchString(re.compile(b'In(0[1-9]|1[0-6]) Aud([\+\-])([01][0-9]|20)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'Frq00 ([01]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Sts02\*(\d+\.\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMuteGlobal, None)
            self.AddMatchString(re.compile(b'Vmt(0?[1-9]|1[0-6])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Out(0[1-4]) Vol([0-9]{1,2}|100)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(01|1[012347]|2[124568])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Rpr[0-9]{2}\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'PrstR\d+\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'Vgp00\*Out(\d{2})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(re.compile(b'Vgp00\*Out(\d{2})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False
        
    def __MatchQik(self, match, tag):
        @Wait(0.5)
        def TieTimer():
            self.UpdateAllMatrixTie(None, None)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            self.Send('w0echo\r\n')
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')

        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                value = self.matrix_tie_status[input_][output]
                self.WriteStatus('InputTieStatus', 'Video' if output + 1 > self.AudioOutputLimit and value == 'Audio/Video' else value,
                                 {'Input': str(input_ + 1), 'Output': str(output + 1)})

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

        if self.audio_status_counter == self.AudioOutputLimit and self.video_status_counter == self.OutputSize:
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def __MatchAudioMuteGlobal(self, match, qualifier):

        HDMIAudioOutputMuteName = {
            '1': 'On',
            '0': 'Off'
        }

        AudioOutputMuteName = {
            '1': 'HDMI audio mute',
            '0': 'Off'
        }

        value = match.group(1).decode()
        for i in range(self.AudioOutputLimit):
            self.WriteStatus('AudioOutputMute', AudioOutputMuteName[value], {'Output': str(i + 1)})

        for i in range(self.OutputSize):
            self.WriteStatus('HDMIAudioOutputMute', HDMIAudioOutputMuteName[value], {'Output': str(i + 1)})

    def __MatchAudioMute(self, match, qualifier):

        HDMIAudioOutputMuteName = {
            '1': 'On',
            '0': 'Off'
        }

        AudioOutputMuteName = {
            '0': 'Off',
            '1': 'HDMI audio mute',
            '2': 'Analog audio mute',
            '3': 'HDMI and Analog audio mute',
            '4': 'S/PDIF mute',
            '5': 'HDMI audio and S/PDIF mute',
            '6': 'Analog audio and S/PDIF mute',
            '7': 'HDMI audio, Analog audio, and S/PDIF mute'
        }

        output, value = int(match.group(1).decode()), match.group(2).decode()
        if 1 <= output <= self.AudioOutputLimit:
            self.WriteStatus('AudioOutputMute', AudioOutputMuteName[value], {'Output': str(output)})

        if int(value) < 2:
            self.WriteStatus('HDMIAudioOutputMute', HDMIAudioOutputMuteName[value], {'Output': str(output)})

    def SetAudioOutputMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'HDMI audio mute': '1',
            'Analog audio mute': '2',
            'HDMI and Analog audio mute': '3',
            'S/PDIF mute': '4',
            'HDMI audio and S/PDIF mute': '5',
            'Analog audio and S/PDIF mute': '6',
            'HDMI audio, Analog audio, and S/PDIF mute': '7'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit and value in ValueStateValues:
            AudioOutputMuteCmdString = '{}*{}Z'.format(output, ValueStateValues[value])
            self.__SetHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputMute')

    def UpdateAudioOutputMute(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit:
            AudioOutputMuteCmdString = '{}Z'.format(output)
            self.__UpdateHelper('AudioOutputMute', AudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutputMute')

    def UpdateEDIDAssignment(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize:
            EDIDAssignmentCmdString = 'wA{}EDID\r'.format(_input_)
            self.__UpdateHelper('EDIDAssignment', EDIDAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDIDAssignment')

    def __MatchEDIDAssignment(self, match, tag):

        value = self.EDIDStates[match.group(2).decode()]
        self.WriteStatus('EDIDAssignment', value, {'Input': str(int(match.group(1).decode()))})

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*Z',
            'Off': '0*Z'
        }

        if value in ValueStateValues:
            self.__SetHelper('GlobalAudioMute', ValueStateValues[value], value, qualifier)
        else:
            self.Discard('Invalid Command for GlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*B',
            'Off': '0*B'
        }

        if value in ValueStateValues:
            self.__SetHelper('GlobalVideoMute', ValueStateValues[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{}*{}HDCP\r'.format(_input_, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize:
            HDCPInputAuthorizationCmdString = 'wE{}HDCP\r'.format(_input_)
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': str(int(match.group(1).decode()))})

    def UpdateHDCPInputStatus(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize:
            HDCPInputStatusCmdString = 'wI{}HDCP\r'.format(_input_)
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'HDCP Content',
            '2': 'No HDCP Content'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, {'Input': str(int(match.group(1).decode()))})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            HDCPOutputStatusCmdString = 'wO{}HDCP\r'.format(output)
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No monitor connected',
            '1': 'Monitor connected, HDCP not supported',
            '2': 'Monitor connected, not encrypted',
            '3': 'Monitor connected, currently encrypted'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, {'Output': str(int(match.group(1).decode()))})

    def SetHDMIAudioOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            HDMIAudioOutputMuteCmdString = '{}*{}Z'.format(output, ValueStateValues[value])
            self.__SetHelper('HDMIAudioOutputMute', HDMIAudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIAudioOutputMute')

    def UpdateHDMIAudioOutputMute(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            HDMIAudioOutputMuteCmdString = '{}Z'.format(output)
            self.__UpdateHelper('HDMIAudioOutputMute', HDMIAudioOutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIAudioOutputMute')

    def UpdateInputFormat(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize:
            InputFormatCmdString = '{}*\x5C'.format(_input_)
            self.__UpdateHelper('InputFormat', InputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputFormat')

    def __MatchInputFormat(self, match, tag):

        ValueStateValues = {
            '0': 'No signal detected',
            '1': 'DVI RGB 444',
            '2': 'HDMI RGB 444 Full',
            '3': 'HDMI RGB 444 Limited',
            '4': 'HDMI YUV 444 Full',
            '5': 'HDMI YUV 444 Limited',
            '6': 'HDMI YUV 422 Full',
            '7': 'HDMI YUV 422 Limited'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputFormat', value, {'Input': str(int(match.group(1).decode()))})

    def SetInputGain(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize and -20 <= value <= 0:
            InputGainCmdString = '{}*{}G'.format(_input_, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        _input_ = qualifier['Input']
        if 1 <= int(_input_) <= self.InputSize:
            InputGainCmdString = '{}G'.format(_input_)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        _sign_ = match.group(2).decode()
        value = int(match.group(3).decode()) if _sign_ == '+' else int(match.group(3).decode()) * (-1)
        self.WriteStatus('InputGain', value, {'Input': str(int(match.group(1).decode()))})

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        _input_ = 1
        for stat in match.group(1).decode():
            value = 'Not Active' if stat == '0' else 'Active'
            self.WriteStatus('InputSignalStatus', value, {'Input': str(_input_)})
            _input_ += 1

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeStates = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$'
        }

        _input_ = qualifier['Input']
        output = qualifier['Output']
        tie_type = qualifier['Tie Type']

        output_num = 0 if output == 'All' else int(output)
        output_size = self.AudioOutputLimit if tie_type == 'Audio' else self.OutputSize

        if 0 <= int(_input_) <= self.InputSize and 0 <= output_num <= output_size:
            MatrixTieCommandCmdString = '{}*{}'.format(_input_, TieTypeStates[tie_type]) if output_num == 0 else '{}*{}{}'.format(_input_, output_num, TieTypeStates[tie_type])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
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
                        if output < self.AudioOutputLimit:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = 'Video'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= self.Presets:
            PresetRecallCmdString = '{}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= self.Presets:
            PresetSaveCmdString = '{},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):
        self.Debug = True
        self.UpdateAllMatrixTie(value, qualifier)

    def UpdateTemperature(self, value, qualifier):

        self.__UpdateHelper('Temperature', '2S', value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = '{:.1f}'.format(float(match.group(1).decode()))
        self.WriteStatus('Temperature', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1',
            'Video and Sync': '2'
        }

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize and value in ValueStateValues:
            VideoMuteCmdString = '{}*{}B'.format(output, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.OutputSize:
            VideoMuteCmdString = '{}B'.format(output)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
            '2': 'Video and Sync'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Output': str(int(match.group(1).decode()))})

    def __MatchVideoMuteGlobal(self, match, qualifier):

        VideoMuteName = {
            '1': 'On',
            '0': 'Off',
            '2': 'Video and Sync'
        }

        for i in range(self.OutputSize):
            self.WriteStatus('VideoMute', VideoMuteName[match.group(1).decode()], {'Output': str(i + 1)})

    def SetVolume(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit and 0 <= value <= 100:
            VolumeCmdString = '{}*{}V'.format(output, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit:
            VolumeCmdString = '{}V'.format(output)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'Output': str(int(match.group(1).decode()))})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            self.Send('w0echo\r\n') 
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

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.EchoDisabled and 'Serial' not in self.ConnectionType:
                self.Send('w0echo\r\n') 
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
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number or port number',
            '13': 'Invalid parameter (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out (caused by direct write of global presets)',
            '21': 'Invalid room number',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
        }

        self.Error([DEVICE_ERROR_CODES[match.group(1).decode()]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_15_1865_44(self):

        self.InputSize = 4
        self.OutputSize = 4
        self.AudioOutputLimit = 2
        self.Presets = 16
        self.EDIDStates = {
            '01': '1280x800 @ 60Hz',
            '02': '1440x900 @ 60Hz',
            '03': '1600x900 @ 60Hz',
            '04': '1680x1050 @ 60Hz',
            '05': '1920x1200 @ 60Hz',
            '06': '2560x1440 @ 60Hz',
            '07': '2560x1600 @ 60Hz',
            '08': '720p 2_Ch Audio @ 50Hz',
            '09': '720p 2_Ch Audio @ 60Hz',
            '10': '1080p 2_Ch Audio @ 50Hz',
            '11': '1080p 2_Ch Audio @ 60Hz',
            '12': '4K/UHD 2_Ch Audio @ 30Hz',
            '13': '720p S/PDIF Audio @ 50Hz',
            '14': '720p S/PDIF Audio @ 60Hz',
            '15': '1080p S/PDIF Audio @ 50Hz',
            '16': '1080p S/PDIF Audio @ 60Hz',
            '17': '4K/UHD S/PDIF Audio @ 30Hz',
            '18': 'Output 1',
            '19': 'Output 2',
            '20': 'Output 3',
            '21': 'Output 4',
            '26': 'User Assigned 1',
            '27': 'User Assigned 2',
            '28': 'User Assigned 3',
            '29': 'User Assigned 4',
            '30': 'User Assigned 5',
            '31': 'User Assigned 6',
            '32': 'User Assigned 7',
            '33': 'User Assigned 8'
        }

    def extr_15_1865_84(self):

        self.InputSize = 8
        self.OutputSize = 4
        self.AudioOutputLimit = 2
        self.Presets = 16
        self.EDIDStates = {
            '01': '1280x800 @ 60Hz',
            '02': '1440x900 @ 60Hz',
            '03': '1600x900 @ 60Hz',
            '04': '1680x1050 @ 60Hz',
            '05': '1920x1200 @ 60Hz',
            '06': '2560x1440 @ 60Hz',
            '07': '2560x1600 @ 60Hz',
            '08': '720p 2_Ch Audio @ 50Hz',
            '09': '720p 2_Ch Audio @ 60Hz',
            '10': '1080p 2_Ch Audio @ 50Hz',
            '11': '1080p 2_Ch Audio @ 60Hz',
            '12': '4K/UHD 2_Ch Audio @ 30Hz',
            '13': '720p S/PDIF Audio @ 50Hz',
            '14': '720p S/PDIF Audio @ 60Hz',
            '15': '1080p S/PDIF Audio @ 50Hz',
            '16': '1080p S/PDIF Audio @ 60Hz',
            '17': '4K/UHD S/PDIF Audio @ 30Hz',
            '18': 'Output 1',
            '19': 'Output 2',
            '20': 'Output 3',
            '21': 'Output 4',
            '26': 'User Assigned 1',
            '27': 'User Assigned 2',
            '28': 'User Assigned 3',
            '29': 'User Assigned 4',
            '30': 'User Assigned 5',
            '31': 'User Assigned 6',
            '32': 'User Assigned 7',
            '33': 'User Assigned 8'
        }

    def extr_15_1865_88(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.AudioOutputLimit = 2
        self.Presets = 16
        self.EDIDStates = {
            '01': '1280x800 @ 60Hz',
            '02': '1440x900 @ 60Hz',
            '03': '1600x900 @ 60Hz',
            '04': '1680x1050 @ 60Hz',
            '05': '1920x1200 @ 60Hz',
            '06': '2560x1440 @ 60Hz',
            '07': '2560x1600 @ 60Hz',
            '08': '720p 2_Ch Audio @ 50Hz',
            '09': '720p 2_Ch Audio @ 60Hz',
            '10': '1080p 2_Ch Audio @ 50Hz',
            '11': '1080p 2_Ch Audio @ 60Hz',
            '12': '4K/UHD 2_Ch Audio @ 30Hz',
            '13': '720p S/PDIF Audio @ 50Hz',
            '14': '720p S/PDIF Audio @ 60Hz',
            '15': '1080p S/PDIF Audio @ 50Hz',
            '16': '1080p S/PDIF Audio @ 60Hz',
            '17': '4K/UHD S/PDIF Audio @ 30Hz',
            '18': 'Output 1',
            '19': 'Output 2',
            '20': 'Output 3',
            '21': 'Output 4',
            '22': 'Output 5',
            '23': 'Output 6',
            '24': 'Output 7',
            '25': 'Output 8',
            '26': 'User Assigned 1',
            '27': 'User Assigned 2',
            '28': 'User Assigned 3',
            '29': 'User Assigned 4',
            '30': 'User Assigned 5',
            '31': 'User Assigned 6',
            '32': 'User Assigned 7',
            '33': 'User Assigned 8'
        }

    def extr_15_1865_168(self):

        self.InputSize = 16
        self.OutputSize = 8
        self.AudioOutputLimit = 4
        self.Presets = 32
        self.EDIDStates = {
            '01': '1280x800 @ 60Hz',
            '02': '1440x900 @ 60Hz',
            '03': '1600x900 @ 60Hz',
            '04': '1680x1050 @ 60Hz',
            '05': '1920x1200 @ 60Hz',
            '06': '2560x1440 @ 60Hz',
            '07': '2560x1600 @ 60Hz',
            '08': '720p 2_Ch Audio @ 50Hz',
            '09': '720p 2_Ch Audio @ 60Hz',
            '10': '1080p 2_Ch Audio @ 50Hz',
            '11': '1080p 2_Ch Audio @ 60Hz',
            '12': '4K/UHD 2_Ch Audio @ 30Hz',
            '13': '720p S/PDIF Audio @ 50Hz',
            '14': '720p S/PDIF Audio @ 60Hz',
            '15': '1080p S/PDIF Audio @ 50Hz',
            '16': '1080p S/PDIF Audio @ 60Hz',
            '17': '4K/UHD S/PDIF Audio @ 30Hz',
            '18': 'Output 1',
            '19': 'Output 2',
            '20': 'Output 3',
            '21': 'Output 4',
            '22': 'Output 5',
            '23': 'Output 6',
            '24': 'Output 7',
            '25': 'Output 8',
            '34': 'User Assigned 1',
            '35': 'User Assigned 2',
            '36': 'User Assigned 3',
            '37': 'User Assigned 4',
            '38': 'User Assigned 5',
            '39': 'User Assigned 6',
            '40': 'User Assigned 7',
            '41': 'User Assigned 8',
            '42': 'User Assigned 9',
            '43': 'User Assigned 10',
            '44': 'User Assigned 11',
            '45': 'User Assigned 12',
            '46': 'User Assigned 13',
            '47': 'User Assigned 14',
            '48': 'User Assigned 15',
            '49': 'User Assigned 16'
        }

    def extr_15_1865_1616(self):

        self.InputSize = 16
        self.OutputSize = 16
        self.AudioOutputLimit = 4
        self.Presets = 32
        self.EDIDStates = {
            '01': '1280x800 @ 60Hz',
            '02': '1440x900 @ 60Hz',
            '03': '1600x900 @ 60Hz',
            '04': '1680x1050 @ 60Hz',
            '05': '1920x1200 @ 60Hz',
            '06': '2560x1440 @ 60Hz',
            '07': '2560x1600 @ 60Hz',
            '08': '720p 2_Ch Audio @ 50Hz',
            '09': '720p 2_Ch Audio @ 60Hz',
            '10': '1080p 2_Ch Audio @ 50Hz',
            '11': '1080p 2_Ch Audio @ 60Hz',
            '12': '4K/UHD 2_Ch Audio @ 30Hz',
            '13': '720p S/PDIF Audio @ 50Hz',
            '14': '720p S/PDIF Audio @ 60Hz',
            '15': '1080p S/PDIF Audio @ 50Hz',
            '16': '1080p S/PDIF Audio @ 60Hz',
            '17': '4K/UHD S/PDIF Audio @ 30Hz',
            '18': 'Output 1',
            '19': 'Output 2',
            '20': 'Output 3',
            '21': 'Output 4',
            '22': 'Output 5',
            '23': 'Output 6',
            '24': 'Output 7',
            '25': 'Output 8',
            '26': 'Output 9',
            '27': 'Output 10',
            '28': 'Output 11',
            '29': 'Output 12',
            '30': 'Output 13',
            '31': 'Output 14',
            '32': 'Output 15',
            '33': 'Output 16',
            '34': 'User Assigned 1',
            '35': 'User Assigned 2',
            '36': 'User Assigned 3',
            '37': 'User Assigned 4',
            '38': 'User Assigned 5',
            '39': 'User Assigned 6',
            '40': 'User Assigned 7',
            '41': 'User Assigned 8',
            '42': 'User Assigned 9',
            '43': 'User Assigned 10',
            '44': 'User Assigned 11',
            '45': 'User Assigned 12',
            '46': 'User Assigned 13',
            '47': 'User Assigned 14',
            '48': 'User Assigned 15',
            '49': 'User Assigned 16'
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
