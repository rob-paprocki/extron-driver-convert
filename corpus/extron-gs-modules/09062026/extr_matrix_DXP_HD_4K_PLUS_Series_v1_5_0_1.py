from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, search

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
        self.Models = {
            'DXP 44 HD 4K PLUS': self.extr_15_3493_44,
            'DXP 84 HD 4K PLUS': self.extr_15_3493_84,
            'DXP 88 HD 4K PLUS': self.extr_15_3493_88,
            'DXP 168 HD 4K PLUS': self.extr_15_3493_168,
            'DXP 1616 HD 4K PLUS': self.extr_15_3493_1616,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AudioOutputBreakaway': {'Parameters': ['Output', 'Input'], 'Status': {}},
            'AudioOutput2Breakaway': {'Parameters': ['Input'], 'Status': {}},
            'AudioOutputMute': {'Parameters': ['Output'], 'Status': {}},
            'CECAudioMute': {'Parameters': ['Output'], 'Status': {}},
            'CECPower': {'Parameters': ['Output'], 'Status': {}},
            'CECShowAsActiveSource': {'Parameters': ['Output'], 'Status': {}},
            'CECVolume': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIMatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'HDMIMatrixTieCommandandAnalogAudioFollow': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type', 'Number', 'Name'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'Temperature': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.TieTimer = None
        self.MatrixIONameStatus = False
        self.CECOutputList = []
        
        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt([0-1])\r\n'), self.__MatchAudioMuteGlobal, None)
            self.AddMatchString(compile(b'Amt([0-9]{1,2})\*([0-7])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe(0|1|2)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'HdcpE(\d+)\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI00\*([012]+)\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO00\*([0-7]+)\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'In([0-9]{2}) Aud((\+|-)[0-9]{2,3})'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'Frq00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Nm([io])([0-9]{1,2}),([ \S]{1,16})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(compile(b'Vmt([0-1])\r\n'), self.__MatchVideoMuteGlobal, None)
            self.AddMatchString(compile(b'Vmt([0-9]{1,2})\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Sts00\*([0-9\.]+) ([0-9\.]+) (\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Out([0-9]{2}) Vol([0-9]{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)

            self.AddMatchString(compile(b'Rpr[0-9]{2}\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'PrstR\d+\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Vgp00\*Out(\d{2})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00\*Out(\d{2})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, tag):

        self.OnConnected()

        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchEchoMode(self, match, tag):

        self.EchoDisabled = False

    def __MatchQik(self, match, tag):

        @Wait(0.5)
        def TieTimer():
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
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': str(input_ + 1)})  # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName  # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                        if self.MatrixIONameStatus:  # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    if self.MatrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Video'})
                    if self.MatrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Video'})
                if self.MatrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
                if self.MatrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})
                if self.MatrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

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

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.OutputSize and value in AudioMuteState:
            self.__SetHelper('AudioMute', '{0}*{1}Z'.format(channel, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 0 or channel > self.OutputSize:
            self.Discard('Invalid Command for UpdateAudioMute')
        else:
            self.__UpdateHelper('AudioMute', '{0}Z'.format(channel), value, qualifier)

    def __MatchAudioMuteGlobal(self, match, tag):

        AudioMuteName = {
            '1': 'On',
            '0': 'Off',
        }

        AudioOutputMuteName = {
            '1': 'HDMI audio mute',
            '0': 'Off',
        }

        for i in range(1, self.AudioOutputLimit + 1):
            self.WriteStatus('AudioOutputMute', AudioOutputMuteName[match.group(1).decode()], {'Output': str(i)})

        for i in range(1, self.OutputSize + 1):
            self.WriteStatus('AudioMute', AudioMuteName[match.group(1).decode()], {'Output': str(i)})

    def __MatchAudioMute(self, match, tag):

        AudioMuteName = {
            '1': 'On',
            '0': 'Off',
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

        if 1 <= int(match.group(1).decode()) <= self.AudioOutputLimit:
            self.WriteStatus('AudioOutputMute', AudioOutputMuteName[match.group(2).decode()], {'Output': str(int(match.group(1).decode()))})

        if int(match.group(2).decode()) < 2:
            self.WriteStatus('AudioMute', AudioMuteName[match.group(2).decode()], {'Output': str(int(match.group(1).decode()))})

    def SetAudioOutputMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'HDMI audio mute': '1',
            'Analog audio mute': '2',
            'HDMI and Analog audio mute': '3',
            'S/PDIF mute': '4',
            'HDMI audio and S/PDIF mute': '5',
            'Analog audio and S/PDIF mute': '6',
            'HDMI audio, Analog audio, and S/PDIF mute': '7'
        }

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.AudioOutputLimit and value in AudioMuteState:
            self.__SetHelper('AudioOutputMute', '{0}*{1}Z'.format(channel, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputMute')

    def UpdateAudioOutputMute(self, value, qualifier):

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.AudioOutputLimit:
            self.Discard('Invalid Command for UpdateAudioOutputMute')
        else:
            self.__UpdateHelper('AudioOutputMute', '{0}Z'.format(channel), value, qualifier)

    def SetAudioOutputBreakaway(self, value, qualifier):

        Input, Output = int(qualifier['Input']), int(qualifier['Output'])
        if Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetAudioOutputBreakaway')
        elif Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Command for SetAudioOutputBreakaway')
        else:
            AudioTieCmdString = '{0}*{1}$'.format(Input, Output)
            self.__SetHelper('AudioOutputBreakaway', AudioTieCmdString, value, qualifier)

    def SetAudioOutput2Breakaway(self, value, qualifier):

        Input = int(qualifier['Input'])
        if Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetAudioOutput2Breakaway')
        else:
            AudioTieCmdString = '{0}*2$'.format(Input)  # only supported for output 2
            self.__SetHelper('AudioOutput2Breakaway', AudioTieCmdString, value, qualifier)

    def SetCECAudioMute(self, value, qualifier):

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize:
            if output not in self.CECOutputList:  # ensures to only enable once
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))
            CECAudioMuteCmdString = 'wO{}*%44%43DCEC\r'.format(output)
            self.__SetHelper('CECAudioMute', CECAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECAudioMute')

    def SetCECPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'PwrOn',
            'Off': 'PwrOff'
        }

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize and value in ValueStateValues:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECPowerCmdString = 'wO{}*\"{}\"DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECShowAsActiveSourceCmdString = 'wO{}*\"ShowMe\"DCEC\r'.format(output)
            self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECShowAsActiveSource')

    def SetCECVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '%44%41',
            'Down': '%44%42'
        }

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize and value in ValueStateValues:
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECVolumeCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECVolume', CECVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECVolume')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2',
        }

        if value in ExecutiveModeState:
            self.__SetHelper('ExecutiveMode', '{0}X'.format(ExecutiveModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeName = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1).decode()], None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize and value in ValueStateValues:
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

        if 1 <= int(qualifier['Input']) <= self.InputSize:
            self.__UpdateHelper('HDCPInputStatus', 'wIHDCP\r', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'HDCP Content',
            '2': 'No HDCP Content'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('HDCPInputStatus', ValueStateValues[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def UpdateHDCPOutputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            self.__UpdateHelper('HDCPOutputStatus', 'wOHDCP\r', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No monitor connected',
            '1': 'Monitor connected, HDCP not supported',
            '2': 'Monitor connected, not encrypted',
            '3': 'Monitor connected, currently encrypted'
        }

        signal = match.group(1).decode()
        outputNumber = 1
        for output in signal:
            self.WriteStatus('HDCPOutputStatus', ValueStateValues[output], {'Output': str(outputNumber)})
            outputNumber += 1

    def SetHDMIMatrixTieCommand(self, value, qualifier):

        Input = int(qualifier['Input'])
        Output = qualifier['Output']

        if Output == 'All':
            Output = 0
        else:
            Output = int(qualifier['Output'])

        if Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Command for SetHDMIMatrixTieCommand')
        elif Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetHDMIMatrixTieCommand')
        else:
            if Output == 0:
                MatrixTieCmdString = '{0}*&'.format(Input)
                self.__SetHelper('HDMIMatrixTieCommand', MatrixTieCmdString, value, qualifier)
            else:
                MatrixTieCmdString = '{0}*{1}&'.format(Input, Output)
                self.__SetHelper('HDMIMatrixTieCommand', MatrixTieCmdString, value, qualifier)

    def SetHDMIMatrixTieCommandandAnalogAudioFollow(self, value, qualifier):

        Input = int(qualifier['Input'])
        Output = qualifier['Output']

        if Output == 'All':
            Output = 0
        else:
            Output = int(qualifier['Output'])

        if Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Command for SetHDMIMatrixTieCommandandAnalogAudioFollow')
        elif Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetHDMIMatrixTieCommandandAnalogAudioFollow')
        else:
            if Output == 0:
                MatrixTieCmdString = '{0}*!'.format(Input)
                self.__SetHelper('HDMIMatrixTieCommandandAnalogAudioFollow', MatrixTieCmdString, value, qualifier)
            else:
                MatrixTieCmdString = '{0}*{1}!'.format(Input, Output)
                self.__SetHelper('HDMIMatrixTieCommandandAnalogAudioFollow', MatrixTieCmdString, value, qualifier)

    def SetInputGain(self, value, qualifier):

        inputVal = qualifier['Input']
        if 1 <= int(inputVal) <= self.InputSize and -20 <= value <= 0:
            InputGainCmdString = '{0}*{1}G'.format(inputVal, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        inputVal = qualifier['Input']
        if 1 <= int(inputVal) <= self.InputSize:
            InputGainCmdString = '{0}G'.format(inputVal)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        inputVal = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        self.WriteStatus('InputGain', value, {'Input': inputVal})

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 1 <= len(name) <= 16 and qualifier['Type'] in TypeStates:
            if name == ' ': # if name is a space
                name = '{} {}'.format(qualifier['Type'], number) # reset to default name
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def UpdateMatrixIONameStatus(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        if str(qualifier['Number']).isdigit() and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0}{1}\r'.format(qualifier['Number'], TypeStates[qualifier['Type']])
            self.__UpdateHelper('MatrixIONameStatus', cmdstring, value, qualifier)
            self.MatrixIONameStatus = True # allows 'Output Tie Status Name' to be written in OutputTieStatusHelper()
        else:
            self.Discard('Invalid Command for UpdateMatrixIONameStatus')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = str(int(match.group(2).decode()))
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        
        # write 'Output Tie Status Name'
        if self.MatrixIONameStatus and type_ == 'Input': # only write the name if 'Matrix IO Name Status' has been written and type is input
            for output in range(1, self.InputSize + 1):
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(output), 'Tie Type': 'Audio'})  # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(output), 'Tie Type': 'Video'})  # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(output), 'Tie Type': 'Audio/Video'})

    def __MatchOutputTieStatus(self, match, tag):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, tag):

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

    def __MatchAllTie(self, match, tag):

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

    def SetRefreshMatrix(self, value, qualifier):
        self.Debug = True
        self.UpdateAllMatrixTie(value, qualifier)

    def SetVolume(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit and 0 <= value <= 100:
            VolumeCmdString = '{0}*{1}V'.format(output, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        output = qualifier['Output']
        if 1 <= int(output) <= self.AudioOutputLimit:
            VolumeCmdString = '{0}V'.format(output)
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        output = str(int(match.group(1).decode()))
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, {'Output': output})

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0*Z',
            'On': '1*Z',
        }

        if value in AudioMuteState:
            GlobalAudioString = AudioMuteState[value]
            self.__SetHelper('AudioMuteState', GlobalAudioString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0*B',
            'On': '1*B'
        }

        if value in VideoMuteState:
            GlobalVideoString = VideoMuteState[value]
            self.__SetHelper('VideoMuteState', GlobalVideoString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def __MatchVideoMuteGlobal(self, match, tag):

        VideoMuteName = {
            '1': 'On',
            '0': 'Off'
        }

        for i in range(1, self.OutputSize + 1):
            self.WriteStatus('VideoMute', VideoMuteName[match.group(1).decode()], {'Output': str(i)})

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
            'Video and Sync': '2'
        }

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize and value in VideoMuteState:
            self.__SetHelper('VideoMute', '{0}*{1}B'.format(channel, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        channel = qualifier['Output']
        if int(channel) < 0 or int(channel) > self.OutputSize:
            self.Discard('Invalid Command for UpdateVideoMute')
        else:
            VideoMuteCmdString = '{0}B'.format(channel)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
            '2': 'Video and Sync'
        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2).decode()], {'Output': match.group(1).decode()})

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputList = match.group(1).decode()
        inputVal = 1
        for stat in InputList:
            value = 'Not Active' if stat == '0' else 'Active'
            self.WriteStatus('InputSignalStatus', value, {'Input': str(inputVal)})
            inputVal += 1

    def UpdateTemperature(self, value, qualifier):

        self.__UpdateHelper('Temperature', 'S', value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(float(match.group(2).decode()))
        self.WriteStatus('Temperature', value, None)

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
            '28': 'Bad filename or file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E' + match.group(1).decode()])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0        

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.MatrixIONameStatus = False
        self.CECOutputList.clear()
        
    def extr_15_3493_44(self):

        self.InputSize = 4
        self.OutputSize = 4
        self.AudioOutputLimit = 2

    def extr_15_3493_84(self):
        self.InputSize = 8
        self.OutputSize = 4
        self.AudioOutputLimit = 2

    def extr_15_3493_88(self):

        self.InputSize = 8
        self.OutputSize = 8
        self.AudioOutputLimit = 2

    def extr_15_3493_168(self):
        
        self.InputSize = 16
        self.OutputSize = 8
        self.AudioOutputLimit = 4

    def extr_15_3493_1616(self):

        self.InputSize = 16
        self.OutputSize = 16
        self.AudioOutputLimit = 4

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