from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'DXP 44 DVI Pro': self.extr_15_49_DVI44,
            'DXP 44 HDMI': self.extr_15_49_HDMI44,
            'DXP 48 DVI Pro': self.extr_15_49_DVI48,
            'DXP 48 HDMI': self.extr_15_49_HDMI48,
            'DXP 84 HDMI': self.extr_15_49_HDMI84,
            'DXP 84 DVI Pro': self.extr_15_49_DVI84,
            'DXP 88 DVI Pro': self.extr_15_49_DVI88,
            'DXP 88 HDMI': self.extr_15_49_HDMI88,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'EDIDAssignment': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'Temperature': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb'Amt([1-8])\*([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(rb'EdidA(\d+)\*(\d+)\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(compile(b'Exe(0|1|2)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Vmt[01]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt[01]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(rb'HdcpE(\d+)\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(rb'HdcpI(\d+)\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(rb'HdcpO(\d+)\*([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Mut([0-3]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(rb'Vmt([1-8])\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(rb'In\d (\d+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(rb'Sts00\*(\d{1,2}\.\d{2}) (\d{1,2}\.\d{2}) (\-|\+)(\d{3}\.\d{2}) (\d{5}) ([01])\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(rb'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(rb'Rpr[\d]{2}\r\n'), self.__MatchPreset, None)
            self.AddMatchString(compile(rb'Vcu(\d{2}) ([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(rb'Vcu(\d{2}) ([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(rb'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
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

    def SetVerbose(self, value, qualifier):

        self.Send('w3cv\r\n')

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.Send('wvm\r')

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

        self.UpdateAllMatrixTie(None, None)

    def __MatchPreset(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

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

        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:
            if i != '-':
                if tag == 'Audio':
                    self.audio_status_counter += 1
                elif tag == 'Video':
                    self.video_status_counter += 1

                if i != '0':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag

                current_output += 1
            else:
                break

        if self.audio_status_counter == self.OutputSize and self.video_status_counter == self.OutputSize:
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        channel = int(qualifier['Output'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            self.__SetHelper('AudioMute', '{0}*{1}Z'.format(channel, AudioMuteState[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            self.__UpdateHelper('AudioMute', '{0}Z'.format(channel), value, qualifier)

    def __MatchAudioMute(self, match, qualifier):

        AudioMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        self.WriteStatus('AudioMute', AudioMuteName[match.group(2)], {'Output': str(match.group(1).decode())})

    def UpdateEDIDAssignment(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            EDIDAssignmentCmdString = 'wA{0}EDID\r'.format(input_)
            self.__UpdateHelper('EDIDAssignment', EDIDAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDIDAssignment')

    def __MatchEDIDAssignment(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = self.EDIDStates[match.group(2).decode()]
        self.WriteStatus('EDIDAssignment', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2',
        }
        self.__SetHelper('ExecutiveMode', '{0}X'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'0': 'Off',
            b'1': 'Mode 1',
            b'2': 'Mode 2',
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            HDCPAuthorizationCmdString = 'wE{0}*{1}HDCP\r\n'.format(tempInput, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            HDCPAuthorizationCmdString = 'wE{0}HDCP\r\n'.format(tempInput)
            self.__UpdateHelper('HDCPInputAuthorization', HDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        tempInput = str(int(match.group(1).decode()))
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': tempInput})

    def UpdateHDCPInputStatus(self, value, qualifier):

        inputVal = qualifier['Input']
        if 1 <= int(inputVal) <= self.InputSize:
            HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(inputVal)
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'HDCP Content',
            '2': 'No HDCP Content'
        }

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        outputVal = qualifier['Output']
        if 1 <= int(outputVal) <= self.OutputSize:
            HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(outputVal)
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

        qualifier = {'Output': str(int(match.group(1).decode()))}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio/Video': '!',
            'Video': '%',
            'Audio': '$',
        }

        Input = int(qualifier['Input'])
        tieType = qualifier['Tie Type']
        Output = qualifier['Output']

        if Output == 'All':
            Output = 0
        else:
            Output = int(qualifier['Output'])

        if Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            if Output == 0:
                MatrixTieCmdString = '{0}*{1}'.format(Input, TieTypeValues[tieType])
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)
            else:
                MatrixTieCmdString = '{0}*{1}{2}'.format(Input, Output, TieTypeValues[tieType])
                self.__SetHelper('MatrixTieCommand', MatrixTieCmdString, value, qualifier)

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

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0*Z',
            'On': '1*Z',
        }
        GlobalAudioString = AudioMuteState[value]
        self.__SetHelper('AudioMuteState', GlobalAudioString, value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0*B',
            'On': '1*B',
        }
        GlobalVideoString = VideoMuteState[value]
        self.__SetHelper('VideoMuteState', GlobalVideoString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        channel = qualifier['Output']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for SetVideoMute')
        else:
            self.__SetHelper('VideoMute', '{0}*{1}B'.format(channel, VideoMuteState[value]), value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        channel = qualifier['Output']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoMuteCmdString = '{0}B'.format(channel)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, {'Output': channel})

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        self.WriteStatus('VideoMute', VideoMuteName[match.group(2)], {'Output': str(match.group(1).decode())})

    def SetPresetSave(self, value, qualifier):

        if int(value) <= 32 or int(value) > 0:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPresetRecall(self, value, qualifier):

        if int(value) <= 32 or int(value) > 0:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateInputSignalStatus(self, value, qualifier):
               
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)
      
    def __MatchInputSignalStatus(self, match, qualifier):

        InputList = match.group(1).decode()
        inputVal = 1
        for stat in InputList:
            value = 'Not Active' if stat == '0' else 'Active'
            self.WriteStatus('InputSignalStatus', value, {'Input': str(inputVal)})
            inputVal += 1

    def UpdateTemperature(self, value, qualifier):

        self.__UpdateHelper('Temperature', 'S', value, qualifier)

    def __MatchTemperature(self, match, qualifier):

        value = int(float(match.group(4).decode()))
        self.WriteStatus('Temperature', value, None)

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
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0
        self.VerboseDisabled = True

    def extr_15_49_DVI44(self):

        self.InputSize = 4
        self.OutputSize = 4
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_DVI48(self):

        self.InputSize = 4
        self.OutputSize = 8
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '05': 'Output 5',
            '06': 'Output 6',
            '07': 'Output 7',
            '08': 'Output 8',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_DVI84(self):

        self.InputSize = 8
        self.OutputSize = 4
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_DVI88(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '05': 'Output 5',
            '06': 'Output 6',
            '07': 'Output 7',
            '08': 'Output 8',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_HDMI44(self):

        self.InputSize = 4
        self.OutputSize = 4
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_HDMI48(self):

        self.InputSize = 4
        self.OutputSize = 8
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '05': 'Output 5',
            '06': 'Output 6',
            '07': 'Output 7',
            '08': 'Output 8',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_HDMI84(self):

        self.InputSize = 8
        self.OutputSize = 4
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

    def extr_15_49_HDMI88(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.EDIDStates = {
            '01': 'Output 1',
            '02': 'Output 2',
            '03': 'Output 3',
            '04': 'Output 4',
            '05': 'Output 5',
            '06': 'Output 6',
            '07': 'Output 7',
            '08': 'Output 8',
            '09': '640x480 @ 60Hz',
            '10': '640x480 @ 75Hz',
            '11': '800x600 @ 60Hz',
            '12': '800x600 @ 75Hz',
            '13': '852x480 @ 60Hz',
            '14': '852x480 @ 75Hz',
            '15': '1024x768 @ 60Hz',
            '16': '1024x768 @ 75Hz',
            '17': '1024x852 @ 60Hz',
            '18': '1024x852 @ 75Hz',
            '19': '1280x768 @ 60Hz',
            '20': '1280x768 @ 75Hz',
            '21': '1280x1024 @ 60Hz',
            '22': '1280x1024 @ 75Hz',
            '23': '1365x768 @ 60Hz',
            '24': '1365x768 @ 75Hz',
            '25': '1366x768 @ 60Hz',
            '26': '1366x768 @ 75Hz',
            '27': '1400x1050 @ 60Hz',
            '28': '1600x1200 @ 60Hz',
            '29': '480p 2_Ch Audio @ 60Hz',
            '30': '576p 2_Ch Audio @ 60Hz',
            '31': '720p 2_Ch Audio @ 50Hz',
            '32': '720p 2_Ch Audio @ 60Hz',
            '33': '1080p Multi_Ch Audio @ 60Hz',
            '34': '1080i 2_Ch Audio @ 60Hz',
            '35': '1080p 2_Ch Audio @ 50Hz',
            '36': '1080p 2_Ch Audio @ 60Hz',
            '37': 'User Assigned 1',
            '38': 'User Assigned 2',
            '39': 'User Assigned 3',
            '40': 'User Assigned 4'
        }

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
                self.Subscription[command] = {'method': {}}

            Subscribe = self.Subscription[command]
            Method = Subscribe['method']

            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        if command in self.Subscription:
            Subscribe = self.Subscription[command]
            Method = Subscribe['method']
            Command = self.Commands[command]
            if qualifier:
                for Parameter in Command['Parameters']:
                    try:
                        Method = Method[qualifier[Parameter]]
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='Serial_RS232', Model=None):
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
