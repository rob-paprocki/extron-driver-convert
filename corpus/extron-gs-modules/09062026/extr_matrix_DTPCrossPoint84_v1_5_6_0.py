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
            'AmplifierAttenuation': {'Parameters': ['L/R'], 'Status': {}},
            'AmplifierMute': {'Parameters': ['L/R'], 'Status': {}},
            'AnalogAttenuation': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'AnalogMute': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Parameters': ['Output'], 'Status': {}},
            'DTPAnalogAttenuation': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'DTPAnalogMute': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'DTPAttenuation': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'DTPMute': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'EDIDAssignment': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'ExpansionPremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'ExpansionPremixerMute': {'Parameters': ['Input'], 'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'GroupMicLineInputGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMixpoint': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters': ['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPrematrixTrim': {'Parameters': ['Group'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIAttenuation': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'HDMIMute': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'InputAudioSwitchMode': {'Parameters': ['Input'], 'Status': {}},
            'InputFormat': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Format', 'L/R', 'Input'], 'Status': {}},
            'InputMute': {'Parameters': ['L/R', 'Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'MicLineGain': {'Parameters': ['Input'], 'Status': {}},
            'MicLineMute': {'Parameters': ['Input'], 'Status': {}},
            'MicrophoneSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MixpointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MixpointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputAudioSelect': {'Parameters': ['Output'], 'Status': {}},
            'OutputPostmixerTrim': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PhantomPower': {'Parameters': ['Input'], 'Status': {}},
            'PostMatrixGain': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'PostMatrixMute': {'Parameters': ['L/R', 'Output'], 'Status': {}},
            'PrematrixTrim': {'Parameters': ['L/R', 'Input'], 'Status': {}},
            'PremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'PremixerMute': {'Parameters': ['Input'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'ScalerPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'ScalerPresetSave': {'Parameters': ['Output'], 'Status': {}},
            'TestPattern': {'Parameters': ['Output'], 'Status': {}},
            'Temperature': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'VirtualReturnGain': {'Parameters': ['Input'], 'Status': {}},
            'VirtualReturnMute': {'Parameters': ['Input'], 'Status': {}},
        }

        self.InputSize = 8
        self.OutputSize = 4

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'
        self.GroupFunction = {}
        self.devicePassword = None

        if self.Unidirectional == 'False':

            self.AddMatchString(compile(b'Ds[gG]6030([01])\*([-]\d{1,4}|0)\r\n'), self.__MatchAmplifierAttenuation, None)
            self.AddMatchString(compile(b'Ds[mM]6030([01])\*([01])\r\n'), self.__MatchAmplifierMute, None)
            self.AddMatchString(compile(b'Ds[gG]6000([0-7])\*([-]\d{1,4}|0)\r\n'), self.__MatchAnalogAttenuation, None)
            self.AddMatchString(compile(b'Ds[mM]6000([0-7])\*([01])\r\n'), self.__MatchAnalogMute, None)
            self.AddMatchString(compile(b'Aspr(\d{2})\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'Ds[gG]6030([4-7])\*([-]\d{1,4}|0)\r\n'), self.__MatchDTPAnalogAttenuation, None)
            self.AddMatchString(compile(b'Ds[mM]6030([4-7])\*([01])\r\n'), self.__MatchDTPAnalogMute, None)
            self.AddMatchString(compile(b'Ds[gG]6020([4-7])\*([-]\d{1,4}|0)\r\n'), self.__MatchDTPAttenuation, None)
            self.AddMatchString(compile(b'Ds[mM]6020([4-7])\*([01])\r\n'), self.__MatchDTPMute, None)
            self.AddMatchString(compile(b'EdidA(0[1-9]|10)\*(0?[1-9]|[1-5][0-9]|6[0-6])\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Ds[gG]502(0[0-7])\*([0-9 -]{1,5})\r\n'), self.__MatchExpansionPremixerGain, None)
            self.AddMatchString(compile(b'Ds[mM]502(0[0-7])\*([01])\r\n'), self.__MatchExpansionPremixerMute, None)
            self.AddMatchString(compile(b'GrpmD([1-3]?[0-9])\*([-+]{0,1}[0-9]{1,4})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(compile(b'HdcpE(\d{2})\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI(\d{2})\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO([1234])\*([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Ds[gG]6020([0-3])\*([-]\d{1,4}|0)\r\n'), self.__MatchHDMIAttenuation, None)
            self.AddMatchString(compile(b'Ds[mM]6020([0-3])\*([01])\r\n'), self.__MatchHDMIMute, None)
            self.AddMatchString(compile(b'AfmtI0(\d)\*([0-2])\r\n'), self.__MatchInputAudioSwitchMode, None)
            self.AddMatchString(compile(b'Ds([gGhH])300([01][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'Ds[mM]300([01][0-9])\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'Ityp(0[1-9]|10)\*([0-7])\r\n'), self.__MatchInputFormat, None)
            self.AddMatchString(compile(b'Frq0+ ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Ds[gG]4000([0-3])\*([0-9 -]{1,4})\r\n'), self.__MatchMicLineGain, None)
            self.AddMatchString(compile(b'Ds[mM]4000([0-3])\*([01])\r\n'), self.__MatchMicLineMute, None)
            self.AddMatchString(compile(b'Ds[vV]4000([0-3])\*[01]\*([0-9]{1,4})\r\n'), self.__MatchMicrophoneSignalStatus, None)
            self.AddMatchString(compile(b'Ds[gG]2([0-9]{2})([0-9]{2})\*([-][0-9]{1,3}|0|[0-9]{1,3})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(compile(b'Ds[mM]2([0-9]{2})([0-9]{2})\*([01])\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(compile(b'AfmtO(\d{2})\*([0-2])\r\n'), self.__MatchOutputAudioSelect, 'Single')
            self.AddMatchString(compile(b'AfmtO([0-2]{2,8})\r\n'), self.__MatchOutputAudioSelect, 'All')
            self.AddMatchString(compile(b'Ds[gG]6010([0-7])\*([0-9 -]{1,4})\r\n'), self.__MatchOutputPostmixerTrim, None)
            self.AddMatchString(compile(b'Rate(\d{2})\*(\d{2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(compile(b'DsZ4000([0-3])\*([01])\r\n'), self.__MatchPhantomPower, None)
            self.AddMatchString(compile(b'Rpr\d\*\d+\r\n'), self.__MatchPreset, None)
            self.AddMatchString(compile(b'Ds[gG]301([01][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchPrematrixTrim, None)
            self.AddMatchString(compile(b'Ds[gG]5000([0-7])\*([-]\d{1,4}|\d{1,3})\r\n'), self.__MatchPostMatrixGain, None)
            self.AddMatchString(compile(b'Ds[mM]5000([0-7])\*([01])\r\n'), self.__MatchPostMatrixMute, None)
            self.AddMatchString(compile(b'Ds[gG]4010([0-3])\*(-*\d{1,4})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(compile(b'Ds[mM]4010([0-3])\*([01])\r\n'), self.__MatchPremixerMute, None)
            self.AddMatchString(compile(b'Sts00\*\d{1,3}\.\d{1,3} (\d{1,3}\.\d{1,3}) \d+ \d+\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Test0([34])\*(0[0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vmt([1-4])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Ds[gG]5010([0-7])\*([-]\d{1,4}|\d{1,3})\r\n'), self.__MatchVirtualReturnGain, None)
            self.AddMatchString(compile(b'Ds[mM]5010([0-7])\*([0-1])\r\n'), self.__MatchVirtualReturnMute, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'PrstR\d+\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'E(01|1[0-7]|2[245678])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

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
        self.UpdateAllMatrixTie(None, None)

    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def __MatchPreset(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.__UpdateHelper('RefreshMatrix', '1%2%3%4%1$2$3$4$', value, qualifier)

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

    def SetAmplifierAttenuation(self, value, qualifier):

        AmplifierAttenuationConstraints = {
            'Min': -100,
            'Max': 0,
        }

        channelSide = {
            'Left': '0',
            'Right': '1'
        }

        channel = channelSide[qualifier['L/R']]
        if AmplifierAttenuationConstraints['Min'] <= int(value) <= AmplifierAttenuationConstraints['Max']:
            commandString = 'WG6030{0}*{1}AU\r'.format(channel, round(value * 10))
            self.__SetHelper('AmplifierAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierAttenuation')

    def UpdateAmplifierAttenuation(self, value, qualifier):

        channelSide = {
            'Left': '0',
            'Right': '1'
        }

        channel = channelSide[qualifier['L/R']]
        commandString = 'WG6030{0}AU\r'.format(channel)
        self.__UpdateHelper('AmplifierAttenuation', commandString, value, qualifier)

    def __MatchAmplifierAttenuation(self, match, qualifier):

        channelSide = {
            '0': 'Left',
            '1': 'Right'
        }

        value = int(match.group(2)) / 10
        qualifier = {'L/R': channelSide[match.group(1).decode()]}
        self.WriteStatus('AmplifierAttenuation', value, qualifier)

    def SetAmplifierMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        channelSide = {
            'Left': '0',
            'Right': '1'
        }

        channel = channelSide[qualifier['L/R']]
        commandString = 'WM6030{0}*{1}AU\r'.format(channel, MuteState[value])
        self.__SetHelper('AmplifierMute', commandString, value, qualifier)

    def UpdateAmplifierMute(self, value, qualifier):

        channelSide = {
            'Left': '0',
            'Right': '1'
        }

        channel = channelSide[qualifier['L/R']]
        commandString = 'WM6030{0}AU\r'.format(channel)
        self.__UpdateHelper('AmplifierMute', commandString, value, qualifier)

    def __MatchAmplifierMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }
        channelSide = {
            '0': 'Left',
            '1': 'Right'
        }

        value = MuteState[match.group(2).decode()]
        qualifier = {'L/R': channelSide[match.group(1).decode()]}
        self.WriteStatus('AmplifierMute', value, qualifier)

    def SetAnalogAttenuation(self, value, qualifier):

        AnalogAttenuationConstraints = {
            'Min': -100,
            'Max': 0,
        }

        OutputConstraints = {
            'Min': 1,
            'Max': 4,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if AnalogAttenuationConstraints['Min'] <= int(value) <= AnalogAttenuationConstraints['Max'] and \
                OutputConstraints['Min'] <= output <= OutputConstraints['Max']:
            commandString = 'WG6000{0}*{1}AU\r'.format(TranslationToNumber, round(value * 10))
            self.__SetHelper('AnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAttenuation')

    def UpdateAnalogAttenuation(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        OutputConstraints = {
            'Min': 1,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if OutputConstraints['Min'] <= output <= OutputConstraints['Max']:
            commandString = 'WG6000{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('AnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogAttenuation')

    def __MatchAnalogAttenuation(self, match, qualifier):

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = int(match.group(2)) / 10
        self.WriteStatus('AnalogAttenuation', value, qualifier)

    def SetAnalogMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        OutputConstraints = {
            'Min': 1,
            'Max': 4,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if OutputConstraints['Min'] <= output <= OutputConstraints['Max']:
            commandString = 'WM6000{0}*{1}AU\r'.format(TranslationToNumber, MuteState[value])
            self.__SetHelper('AnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogMute')

    def UpdateAnalogMute(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        OutputConstraints = {
            'Min': 1,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if OutputConstraints['Min'] <= output <= OutputConstraints['Max']:
            commandString = 'WM6000{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('AnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogMute')

    def __MatchAnalogMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('AnalogMute', value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        AspectRatio = {
            'Fill': '1',
            'Follow': '2',
        }

        InputConstraints = {
            'Max': 8,
            'Min': 1
        }

        InputNum = qualifier['Input']
        if InputConstraints['Min'] <= int(InputNum) <= InputConstraints['Max']:
            AspectRatioCMDString = 'W{0}*{1}ASPR\r'.format(InputNum, AspectRatio[value])
            self.__SetHelper('AspectRatio', AspectRatioCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        InputConstraints = {
            'Max': 8,
            'Min': 1
        }

        input_ = qualifier['Input']
        if InputConstraints['Min'] <= int(input_) <= InputConstraints['Max']:
            commandString = 'W{0}ASPR\r'.format(input_)
            self.__UpdateHelper('AspectRatio', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, qualifier):

        AspectRatio = {
            '1': 'Fill',
            '2': 'Follow',
        }

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = AspectRatio[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        Output = qualifier['Output']
        if 3 <= int(Output) <= 4:
            AutoImageCmdString = '{0}*A'.format(Output)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetDTPAnalogAttenuation(self, value, qualifier):

        DTPOutputAttenuationConstraints = {
            'Min': -100,
            'Max': 0,
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPOutputAttenuationConstraints['Min'] <= int(value) <= DTPOutputAttenuationConstraints['Max'] and \
                DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WG6030{0}*{1}AU\r'.format(TranslationToNumber, round(value * 10))
            self.__SetHelper('DTPAnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTPAnalogAttenuation')

    def UpdateDTPAnalogAttenuation(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WG6030{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('DTPAnalogAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDTPAnalogAttenuation')

    def __MatchDTPAnalogAttenuation(self, match, qualifier):

        channelSide = {
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = int(match.group(2)) / 10
        self.WriteStatus('DTPAnalogAttenuation', value, qualifier)

    def SetDTPAnalogMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WM6030{0}*{1}AU\r'.format(TranslationToNumber, MuteState[value])
            self.__SetHelper('DTPAnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTPAnalogMute')

    def UpdateDTPAnalogMute(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WM6030{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('DTPAnalogMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDTPAnalogMute')

    def __MatchDTPAnalogMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('DTPAnalogMute', value, qualifier)

    def SetDTPAttenuation(self, value, qualifier):

        DTPAttenuationConstraints = {
            'Min': -100,
            'Max': 0
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPAttenuationConstraints['Min'] <= int(value) <= DTPAttenuationConstraints['Max'] \
                and DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WG6020{0}*{1}AU\r'.format(TranslationToNumber, round(value * 10))
            self.__SetHelper('DTPAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTPAttenuation')

    def UpdateDTPAttenuation(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WG6020{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('DTPAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDTPAttenuation')

    def __MatchDTPAttenuation(self, match, qualifier):

        channelSide = {
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = int(match.group(2)) / 10
        self.WriteStatus('DTPAttenuation', value, qualifier)

    def SetDTPMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WM6020{0}*{1}AU\r'.format(TranslationToNumber, MuteState[value])
            self.__SetHelper('DTPMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTPMute')

    def UpdateDTPMute(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        DTPConstraints = {
            'Min': 3,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if DTPConstraints['Min'] <= output <= DTPConstraints['Max']:
            commandString = 'WM6020{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('DTPMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDTPMute')

    def __MatchDTPMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('DTPMute', value, qualifier)

    def UpdateEDIDAssignment(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            EDIDAssignmentCmdString = 'wA{0}EDID\r'.format(input_)
            self.__UpdateHelper('EDIDAssignment', EDIDAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEDIDAssignment')

    def __MatchEDIDAssignment(self, match, tag):

        EDIDStates = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': '1024x768 @ 50Hz (DVI)',
            '6': '1024x768 @ 60Hz (DVI)',
            '7': '1280x720 @ 50Hz (DVI)',
            '8': '1280x720 @ 60Hz (DVI)',
            '9': '1280x768 @ 50Hz (DVI)',
            '10': '1280x768 @ 60Hz (DVI)',
            '11': '1280x800 @ 50Hz (DVI)',
            '12': '1280x800 @ 60Hz (DVI)',
            '13': '1280x1024 @ 50Hz (DVI)',
            '14': '1280x1024 @ 60Hz (DVI)',
            '15': '1360x768 @ 50Hz (DVI)',
            '16': '1360x768 @ 60Hz (DVI)',
            '17': '1366x768 @ 50Hz (DVI)',
            '18': '1366x768 @ 60Hz (DVI)',
            '19': '1400x1050 @ 50Hz (DVI)',
            '20': '1400x1050 @ 60Hz (DVI)',
            '21': '1440x900 @ 50Hz (DVI)',
            '22': '1440x900 @ 60Hz (DVI)',
            '23': '1600x900 @ 50Hz (DVI)',
            '24': '1600x900 @ 60Hz (DVI)',
            '25': '1600x1200 @ 50Hz (DVI)',
            '26': '1600x1200 @ 60Hz (DVI)',
            '27': '1680x1050 @ 50Hz (DVI)',
            '28': '1680x1050 @ 60Hz (DVI)',
            '29': '1920x1080 @ 50Hz (DVI)',
            '30': '1920x1080 @ 60Hz (DVI)',
            '31': '1920x1200 @ 50Hz (DVI)',
            '32': '1920x1200 @ 60Hz (DVI)',
            '33': '2048x1080 @ 50Hz (DVI)',
            '34': '2048x1080 @ 60Hz (DVI)',
            '35': '1024x768 @ 50Hz (HDMI)',
            '36': '1024x768 @ 60Hz (HDMI)',
            '37': '1280x768 @ 50Hz (HDMI)',
            '38': '1280x768 @ 60Hz (HDMI)',
            '39': '1280x800 @ 50Hz (HDMI)',
            '40': '1280x800 @ 60Hz (HDMI)',
            '41': '1280x1024 @ 50Hz (HDMI)',
            '42': '1280x1024 @ 60Hz (HDMI)',
            '43': '1360x768 @ 50Hz (HDMI)',
            '44': '1360x768 @ 60Hz (HDMI)',
            '45': '1366x768 @ 50Hz (HDMI)',
            '46': '1366x768 @ 60Hz (HDMI)',
            '47': '1400x1050 @ 50Hz (HDMI)',
            '48': '1400x1050 @ 60Hz (HDMI)',
            '49': '1440x900 @ 50Hz (HDMI)',
            '50': '1440x900 @ 60Hz (HDMI)',
            '51': '1600x900 @ 50Hz (HDMI)',
            '52': '1600x900 @ 60Hz (HDMI)',
            '53': '1600x1200 @ 50Hz (HDMI)',
            '54': '1600x1200 @ 60Hz (HDMI)',
            '55': '1680x1050 @ 50Hz (HDMI)',
            '56': '1680x1050 @ 60Hz (HDMI)',
            '57': '1920x1200 @ 50Hz (HDMI)',
            '58': '1920x1200 @ 60Hz (HDMI)',
            '59': '2048x1080 @ 50Hz (HDMI)',
            '60': '2048x1080 @ 60Hz (HDMI)',
            '61': '480p 2_Ch Audio @ 60Hz',
            '62': '576p 2_Ch Audio @ 50Hz',
            '63': '720p 2_Ch Audio @ 50Hz',
            '64': '720p 2_Ch Audio @ 60Hz',
            '65': '720p Multi_Ch Audio @ 50Hz',
            '66': '720p Multi_Ch Audio @ 60Hz',
            '67': '1080i 2_Ch Audio @ 50Hz',
            '68': '1080i 2_Ch Audio @ 60Hz',
            '69': '1080i Multi_Ch Audio @ 50Hz',
            '70': '1080i Multi_Ch Audio @ 60Hz',
            '71': '1080p 2_Ch Audio @ 50Hz',
            '72': '1080p 2_Ch Audio @ 60Hz',
            '73': '1080p Multi_Ch Audio @ 50Hz',
            '74': '1080p Multi_Ch Audio @ 60Hz',
            '75': 'User Assigned 1',
            '76': 'User Assigned 2',
            '77': 'User Assigned 3',
            '78': 'User Assigned 4',
            '79': 'User Assigned 5',
            '80': 'User Assigned 6',
            '81': 'User Assigned 7',
            '82': 'User Assigned 8'
        }

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = EDIDStates[match.group(2).decode()]
        self.WriteStatus('EDIDAssignment', value, qualifier)

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

        ExecutiveModeState = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeState[match.group(1)], None)

    def SetExpansionPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -100 <= value <= 12 and 1 <= tempInput <= 8:
            level = round(value * 10)
            ExpansionPremixerGainCmdString = 'wG{0}*{1:05d}AU\r'.format(tempInput + 50199, level)
            self.__SetHelper('ExpansionPremixerGain', ExpansionPremixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExpansionPremixerGain')

    def UpdateExpansionPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 8:
            ExpansionPremixerGainCmdString = 'wG{0}AU\r'.format(tempInput + 50199)
            self.__UpdateHelper('ExpansionPremixerGain', ExpansionPremixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExpansionPremixerGain')

    def __MatchExpansionPremixerGain(self, match, tag):

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = int(match.group(2)) / 10
        self.WriteStatus('ExpansionPremixerGain', value, qualifier)

    def SetExpansionPremixerMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 8:
            ExpansionPremixerMuteCmdString = 'wM{0}*{1}AU\r'.format(tempInput + 50199, ValueStateValues[value])
            self.__SetHelper('ExpansionPremixerMute', ExpansionPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExpansionPremixerMute')

    def UpdateExpansionPremixerMute(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 8:
            ExpansionPremixerMuteCmdString = 'wM{0}AU\r'.format(tempInput + 50199)
            self.__UpdateHelper('ExpansionPremixerMute', ExpansionPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateExpansionPremixerMute')

    def __MatchExpansionPremixerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ExpansionPremixerMute', value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        GlobalMuteState = {
            'Video': '1',
            'Video & Sync': '2',
            'Off': '0'
        }

        self.__SetHelper('GlobalVideoMute', '{0}*B'.format(GlobalMuteState[value]), value, qualifier)

    def __MatchGroup(self, match, tag):

        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                GroupMuteStateNames = {
                    '1': 'On',
                    '0': 'Off'
                }
                qualifier = {'Group': group}
                value = match.group(2).decode()[-1]
                self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
            elif command in ['GroupMicLineInputGain', 'GroupPremixerGain',
                             'GroupOutputAttenuation', 'GroupMixpoint',
                             'GroupPostmixerTrim', 'GroupPrematrixTrim'
                             ]:
                qualifier = {'Group': group}
                value = int(match.group(2)) / 10
                self.WriteStatus(command, value, qualifier)

    def SetGroupMicLineInputGain(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        GroupMicLineInputGainConstraints = {
            'Min': -18,
            'Max': 80,
        }

        group = qualifier['Group']
        if GroupMicLineInputGainConstraints['Min'] <= int(value) <= GroupMicLineInputGainConstraints['Max'] and \
                GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupMicLineInputGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
        else:
            self.Discard('Invalid Command for SetGroupMicLineInputGain')

    def UpdateGroupMicLineInputGain(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMicLineInputGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
        else:
            self.Discard('Invalid Command for UpdateGroupMicLineInputGain')

    def SetGroupMixpoint(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        Constraints = {
            'Min': -35,
            'Max': 25,
        }

        group = qualifier['Group']
        if Constraints['Min'] <= int(value) <= Constraints['Max'] and GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupMixpoint', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for SetGroupMixpoint')

    def UpdateGroupMixpoint(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMixpoint', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for UpdateGroupMixpoint')

    def SetGroupMute(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        group = qualifier['Group']
        channel = qualifier['Group']
        if GroupConstraints['Min'] <= int(channel) <= GroupConstraints['Max']:
            commandString = 'WD{0}*{1}GRPM\r'.format(channel, MuteState[value])
            self.__SetHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        Constraints = {
            'Min': -100,
            'Max': 0,
        }

        group = qualifier['Group']
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
                commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
                self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupOutputAttenuation'
            else:
                self.Discard('Invalid Command for SetGroupOutputAttenuation')
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
        else:
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPremixerGain(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        Constraints = {
            'Min': -100,
            'Max': 12,
        }

        group = qualifier['Group']
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
                commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
                self.__SetHelper('GroupPremixerGain', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPremixerGain'
            else:
                self.Discard('Invalid Command for SetGroupPremixerGain')
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPremixerGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPremixerGain'
        else:
            self.Discard('Invalid Command for UpdateGroupPremixerGain')

    def SetGroupPrematrixTrim(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        Constraints = {
            'Min': -12,
            'Max': 12,
        }

        group = qualifier['Group']
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
                commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
                self.__SetHelper('GroupPrematrixTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPrematrixTrim'
            else:
                self.Discard('Invalid Command for SetGroupPrematrixTrim')
        else:
            self.Discard('Invalid Command for SetGroupPrematrixTrim')

    def UpdateGroupPrematrixTrim(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPrematrixTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPrematrixTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPrematrixTrim')

    def SetGroupPostmixerTrim(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        Constraints = {
            'Min': -12,
            'Max': 12,
        }

        group = qualifier['Group']
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
                commandString = 'WD{0}*{1}GRPM\r'.format(group, round(value * 10))
                self.__SetHelper('GroupPostmixerTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPostmixerTrim'
            else:
                self.Discard('Invalid Command for SetGroupPostmixerTrim')
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        GroupConstraints = {
            'Min': 1,
            'Max': 32,
        }

        group = qualifier['Group']
        if GroupConstraints['Min'] <= int(group) <= GroupConstraints['Max']:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPostmixerTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPostmixerTrim')

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

        InputStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        tempInput = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': tempInput})

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(qualifier['Input'])
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

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

        outputVal = int(qualifier['Output'])
        if 1 <= outputVal <= 4:
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

        qualifier = {'Output': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetHDMIAttenuation(self, value, qualifier):

        HDMIAttenuationConstraints = {
            'Min': -100,
            'Max': 0,
        }

        HDMIConstraints = {
            'Min': 1,
            'Max': 2,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
        }

        channel = int(channelSide[qualifier['L/R']])
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if HDMIAttenuationConstraints['Min'] <= int(value) <= HDMIAttenuationConstraints['Max']:
            if HDMIConstraints['Min'] <= output <= HDMIConstraints['Max']:
                commandString = 'WG6020{0}*{1}AU\r'.format(TranslationToNumber, round(value * 10))
                self.__SetHelper('HDMIAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetHDMIAttenuation')
        else:
            self.Discard('Invalid Command for SetHDMIAttenuation')

    def UpdateHDMIAttenuation(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
        }

        HDMIConstraints = {
            'Min': 1,
            'Max': 2,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if HDMIConstraints['Min'] <= output <= HDMIConstraints['Max']:
            commandString = 'WG6020{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('HDMIAttenuation', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIAttenuation')

    def __MatchHDMIAttenuation(self, match, qualifier):

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = int(match.group(2)) / 10
        self.WriteStatus('HDMIAttenuation', value, qualifier)

    def SetHDMIMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        HDMIConstraints = {
            'Min': 1,
            'Max': 2,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
        }

        channel = int(channelSide[qualifier['L/R']])
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if HDMIConstraints['Min'] <= output <= HDMIConstraints['Max']:
            commandString = 'WM6020{0}*{1}AU\r'.format(TranslationToNumber, MuteState[value])
            self.__SetHelper('HDMIMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIMute')

    def UpdateHDMIMute(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        HDMIConstraints = {
            'Min': 1,
            'Max': 2,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if HDMIConstraints['Min'] <= output <= HDMIConstraints['Max']:
            commandString = 'WM6020{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('HDMIMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIMute')

    def __MatchHDMIMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('HDMIMute', value, qualifier)

    def SetInputAudioSwitchMode(self, value, qualifier):

        InputAudioSwitchMode = {
            'Auto': '0',
            'Digital': '1',
            'Analog': '2'
        }

        InputConstraints = {
            'Min': 1,
            'Max': 8,
        }

        InputNum = qualifier['Input']
        if InputConstraints['Min'] <= int(InputNum) <= InputConstraints['Max']:
            InputAudioSwitchSwitchModeCMDString = 'WI{0}*{1}AFMT\r'.format(InputNum, InputAudioSwitchMode[value])
            self.__SetHelper('InputAudioSwitchMode', InputAudioSwitchSwitchModeCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchMode')

    def UpdateInputAudioSwitchMode(self, value, qualifier):

        InputConstraints = {
            'Min': 1,
            'Max': 8,
        }

        InputNum = qualifier['Input']
        if InputConstraints['Min'] <= int(InputNum) <= InputConstraints['Max']:
            UpdateCMDString = 'WI{0}AFMT\r'.format(InputNum)
            self.__UpdateHelper('InputAudioSwitchMode', UpdateCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioSwitchMode')

    def __MatchInputAudioSwitchMode(self, match, qualifier):

        InputAudioSwitchMode = {
            '1': 'Digital',
            '2': 'Analog',
            '0': 'Auto',
        }

        qualifier = {'Input': match.group(1).decode()}
        value = InputAudioSwitchMode[match.group(2).decode()]
        self.WriteStatus('InputAudioSwitchMode', value, qualifier)

    def UpdateInputFormat(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            InputFormatCmdString = '{0}\x2A\x5C\r'.format(input_)
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

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputFormat', value, qualifier)

    def SetInputGain(self, value, qualifier):

        formatStates = {
            'Analog': 'G',
            'Digital': 'H'
        }

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        tempInput = int(qualifier['Input'])
        tempFormat = qualifier['Format']
        channel = qualifier['L/R']

        if -18 <= value <= 24 and 1 <= tempInput <= self.InputSize and tempFormat in formatStates and channel in channelStates:
            formatValue = formatStates[tempFormat]
            level = round(value * 10)
            channelValue = (tempInput * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1

            InputGainCmdString = 'w{0}{1}*{2:05d}AU\r'.format(formatValue, channelValue + 30000, level)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        formatStates = {
            'Analog': 'G',
            'Digital': 'H'
        }

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        tempInput = int(qualifier['Input'])
        tempFormat = qualifier['Format']
        channel = qualifier['L/R']

        if 1 <= tempInput <= self.InputSize and \
                tempFormat in formatStates and \
                channel in channelStates:
            formatValue = formatStates[tempFormat]

            channelValue = (tempInput * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1

            InputGainCmdString = 'w{0}{1}AU\r'.format(formatValue, channelValue + 30000)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        formatStates = {
            'G': 'Analog',
            'H': 'Digital'
        }

        qualifier = {'Format': formatStates[match.group(1).decode().upper()]}

        inputValue = int(match.group(2).decode())
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = int(match.group(3).decode()) / 10
        self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= self.InputSize and channel in channelStates:
            channelValue = (tempInput * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1

            InputMuteCmdString = 'wM{0}*{1}AU\r'.format(channelValue + 30000, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])

        if channel in channelStates:
            channelValue = (tempInput * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1
            InputMuteCmdString = 'wM{0}AU\r'.format(channelValue + 30000)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        inputValue = int(match.group(1).decode())
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

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
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
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

    def SetMicLineGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -18 <= value <= 80 and 1 <= tempInput <= 4:
            level = round(value * 10)
            MicLineGainCmdString = 'wG{0}*{1:05d}AU\r\n'.format(tempInput + 39999, level)
            self.__SetHelper('MicLineGain', MicLineGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineGain')

    def UpdateMicLineGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 8:
            MicLineGainCmdString = 'wG{0}AU\r'.format(tempInput + 39999)
            self.__UpdateHelper('MicLineGain', MicLineGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicLineGain')

    def __MatchMicLineGain(self, match, tag):

        qualifier = {'Input': str(int(match.group(1)) + 1)}
        value = int(match.group(2)) / 10
        self.WriteStatus('MicLineGain', value, qualifier)

    def SetMicLineMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MicNum = int(qualifier['Input'])

        if 1 <= MicNum <= 4:

            MicNumFix = MicNum - 1
            commandString = 'wM4000{0}*{1}AU\r'.format(MicNumFix, ValueStateValues[value])
            self.__SetHelper('MicLineMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineMute')

    def UpdateMicLineMute(self, value, qualifier):

        MicNum = int(qualifier['Input'])

        if 1 <= MicNum <= 4:

            MicNumFix = MicNum - 1
            commandString = 'wM4000{0}AU\r'.format(MicNumFix)
            self.__UpdateHelper('MicLineMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicLineMute')

    def __MatchMicLineMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MicNumFix = int(match.group(1).decode()) + 1
        qualifier = {'Input': str(MicNumFix)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicLineMute', value, qualifier)

    def UpdateMicrophoneSignalStatus(self, value, qualifier):

        MicNum = qualifier['Input']

        if 1 <= int(MicNum) <= 4:

            MicNumFix = int(MicNum) - 1
            self.__UpdateHelper('MicrophoneSignalStatus', 'wv4000{0}*1AU\r'.format(MicNumFix), value, qualifier)
            self.__UpdateHelper('MicrophoneSignalStatus', 'wv4000{0}AU\r'.format(MicNumFix), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicrophoneSignalStatus')

    def __MatchMicrophoneSignalStatus(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('MicrophoneSignalStatus', -value, qualifier)

    def SetMixpointGain(self, value, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        Constraints = {
            'Min': -35,
            'Max': 25,
        }

        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            row = qualifier['Input']
            column = qualifier['Output']

            if rows.index(row) < 8 and columns.index(column) < 8 and rows.index(row) != columns.index(column):
                self.Discard('Invalid Command for SetMixpointGain')
            elif 11 < rows.index(row) < 20 and columns.index(column) > 7 and rows.index(row) - 4 == columns.index(column):
                self.Discard('Invalid Command for SetMixpointGain')
            else:
                commandString = 'WG2{0:02d}{1:02d}*{2}AU\r'.format(rows.index(row), columns.index(column), round(value * 10))
                self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        row = qualifier['Input']
        column = qualifier['Output']

        if rows.index(row) < 8 and columns.index(column) < 8 and rows.index(row) != columns.index(column):
            self.Discard('Invalid Command for UpdateMixpointGain')
        elif 11 < rows.index(row) < 20 and columns.index(column) > 7 and rows.index(row) - 4 == columns.index(column):
            self.Discard('Invalid Command for UpdateMixpointGain')
        else:
            commandString = 'WG2{0:02d}{1:02d}AU\r'.format(rows.index(row), columns.index(column))
            self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        inputVal = rows[int(match.group(1).decode())]
        Output = columns[int(match.group(2).decode())]

        qualifier = {'Input': inputVal, 'Output': Output}
        value = int(match.group(3).decode()) / 10
        self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        ValueStates = {
            'On': 1,
            'Off': 0
        }

        row = qualifier['Input']
        column = qualifier['Output']

        if rows.index(row) < 8 and columns.index(column) < 8 and rows.index(row) != columns.index(column):
            self.Discard('Invalid Command for SetMixpointMute')
        elif 11 < rows.index(row) < 20 and columns.index(column) > 7 and rows.index(row) - 4 == columns.index(column):
            self.Discard('Invalid Command for SetMixpointMute')
        else:
            commandString = 'WM2{0:02d}{1:02d}*{2}AU\r'.format(rows.index(row), columns.index(column), ValueStates[value])
            self.__SetHelper('MixpointMute', commandString, value, qualifier)

    def UpdateMixpointMute(self, value, qualifier):

        row = qualifier['Input']
        column = qualifier['Output']

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        if rows.index(row) < 8 and columns.index(column) < 8 and rows.index(row) != columns.index(column):
            self.Discard('Invalid Command for UpdateMixpointMute')
        elif 11 < rows.index(row) < 20 and columns.index(column) > 7 and rows.index(row) - 4 == columns.index(column):
            self.Discard('Invalid Command for UpdateMixpointMute')
        else:
            commandString = 'WM2{0:02d}{1:02d}AU\r'.format(rows.index(row), columns.index(column))
            self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        inputVal = rows[int(match.group(1).decode())]
        Output = columns[int(match.group(2).decode())]

        qualifier = {'Input': inputVal, 'Output': Output}
        value = MuteState[match.group(3).decode()]
        self.WriteStatus('MixpointMute', value, qualifier)

    def SetOutputAudioSelect(self, value, qualifier):

        ValueStateValues = {
            'Embedded Audio': '1',
            'No Audio': '2',
            'Original HDMI': '0'
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize:
            OutputAudioSelectCmdString = 'wO{0}*{1}AFMT\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAudioSelect')

    def UpdateOutputAudioSelect(self, value, qualifier):
        OutputAudioSelectCmdString = 'wOAFMT\r\n'
        self.__UpdateHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)

    def __MatchOutputAudioSelect(self, match, tag):

        OutputStates = {
            '01': '1',
            '02': '2',
            '03': '3',
            '04': '4',
            '05': '5',
            '06': '6',
            '07': '7',
            '08': '8'
        }

        ValueStateValues = {
            '1': 'Embedded Audio',
            '2': 'No Audio',
            '0': 'Original HDMI'
        }

        if tag == 'Single':
            Output = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OutputAudioSelect', value, {'Output': Output})
        else:
            Output = 0
            for i in match.group(1).decode():
                value = ValueStateValues[i]
                Output = Output + 1
                self.WriteStatus('OutputAudioSelect', value, {'Output': str(Output)})

    def SetOutputPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']
        if -12 <= value <= 12 and 1 <= output <= 4 and channel in channelStates:
            level = round(value * 10)
            channelValue = (output * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1
            OutputPostmixerTrimCmdString = 'wG6010{0}*{1}AU\r'.format(channelValue, level)
            self.__SetHelper('OutputPostmixerTrim', OutputPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputPostmixerTrim')

    def UpdateOutputPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']

        if 1 <= output <= 4 and channel in channelStates:
            channelValue = (output * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1
            OutputPostmixerTrimCmdString = 'wG6010{0}AU\r'.format(channelValue)
            self.__UpdateHelper('OutputPostmixerTrim', OutputPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputPostmixerTrim')

    def __MatchOutputPostmixerTrim(self, match, tag):

        qualifier = {}
        outputValue = int(match.group(1).decode())
        if outputValue % 2 == 0:
            channelValue = int((outputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((outputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2)) / 10
        self.WriteStatus('OutputPostmixerTrim', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        OutputConstraints = {
            'Min': 3,
            'Max': 4
        }

        OutputResolution = {
            '2048x1080 2K (60Hz)': '92',
            '1024x768 (60Hz)': '20',
            '1280x1024 (60Hz)': '35',
            '1440x900 (60Hz)': '53',
            '1680x1050 (60Hz)': '60',
            '480p (59.94Hz)': '65',
            '720p (25Hz)': '68',
            '720p (50Hz)': '71',
            '1080i (50Hz)': '74',
            '1080p (23.98Hz)': '77',
            '1080p (29.97Hz)': '80',
            '1080p (59.94Hz)': '83',
            '2048x1080 2K (24Hz)': '86',
            '2048x1080 2K (30Hz)': '89',
            '640x480 (60Hz)': '11',
            '1280x768 (60Hz)': '29',
            '1360x768 (60Hz)': '41',
            '1400x1050 (60Hz)': '56',
            '1600x1200 (60Hz)': '62',
            '480p (60Hz)': '66',
            '720p (29.97Hz)': '69',
            '720p (59.94Hz)': '72',
            '1080i (59.94Hz)': '75',
            '1080p (24Hz)': '78',
            '1080p (30Hz)': '81',
            '1080p (60Hz)': '84',
            '2048x1080 2K (25Hz)': '87',
            '2048x1080 2K (50Hz)': '90',
            '800x600 (60Hz)': '14',
            '1280x800 (60Hz)': '32',
            '1366x768 (60Hz)': '47',
            '1600x900 (60Hz)': '58',
            '1920x1200 (60Hz)': '64',
            '576p': '67',
            '720p (30Hz)': '70',
            '720p (60Hz)': '73',
            '1080i (60Hz)': '76',
            '1080p (25Hz)': '79',
            '1080p (50Hz)': '82',
            '2048x1080 2K (23.98Hz)': '85',
            '2048x1080 2K (29.97Hz)': '88',
            '2048x1080 2K (59.94Hz)': '91',
        }

        OutputNum = qualifier['Output']
        if OutputConstraints['Min'] <= int(OutputNum) <= OutputConstraints['Max']:
            OutputResolutionCMDString = 'W{0}*{1}RATE\r'.format(OutputNum, OutputResolution[value])
            self.__SetHelper('OutputResolution', OutputResolutionCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputConstraints = {
            'Min': 3,
            'Max': 4
        }

        OutputNum = qualifier['Output']
        if OutputConstraints['Min'] <= int(OutputNum) <= OutputConstraints['Max']:
            UpdateCMDString = 'W{0}RATE\r'.format(OutputNum)
            self.__UpdateHelper('OutputResolution', UpdateCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, qualifier):

        OutputResolution = {
            '92': '2048x1080 2K (60Hz)',
            '20': '1024x768 (60Hz)',
            '35': '1280x1024 (60Hz)',
            '53': '1440x900 (60Hz)',
            '60': '1680x1050 (60Hz)',
            '65': '480p (59.94Hz)',
            '68': '720p (25Hz)',
            '71': '720p (50Hz)',
            '74': '1080i (50Hz)',
            '77': '1080p (23.98Hz)',
            '80': '1080p (29.97Hz)',
            '83': '1080p (59.94Hz)',
            '86': '2048x1080 2K (24Hz)',
            '89': '2048x1080 2K (30Hz)',
            '11': '640x480 (60Hz)',
            '29': '1280x768 (60Hz)',
            '41': '1360x768 (60Hz)',
            '56': '1400x1050 (60Hz)',
            '62': '1600x1200 (60Hz)',
            '66': '480p (60Hz)',
            '69': '720p (29.97Hz)',
            '72': '720p (59.94Hz)',
            '75': '1080i (59.94Hz)',
            '78': '1080p (24Hz)',
            '81': '1080p (30Hz)',
            '84': '1080p (60Hz)',
            '87': '2048x1080 2K (25Hz)',
            '90': '2048x1080 2K (50Hz)',
            '14': '800x600 (60Hz)',
            '32': '1280x800 (60Hz)',
            '47': '1366x768 (60Hz)',
            '58': '1600x900 (60Hz)',
            '64': '1920x1200 (60Hz)',
            '67': '576p',
            '70': '720p (30Hz)',
            '73': '720p (60Hz)',
            '76': '1080i (60Hz)',
            '79': '1080p (25Hz)',
            '82': '1080p (50Hz)',
            '85': '2048x1080 2K (23.98Hz)',
            '88': '2048x1080 2K (29.97Hz)',
            '91': '2048x1080 2K (59.94Hz)',
        }

        qualifier = {'Output': str(int(match.group(1).decode()))}
        value = OutputResolution[str(int(match.group(2).decode()))]
        self.WriteStatus('OutputResolution', value, qualifier)

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

    def SetPhantomPower(self, value, qualifier):

        InputStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        PhantomPowerCmdString = 'wZ4000{0}*{1}AU\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)

    def UpdatePhantomPower(self, value, qualifier):

        InputStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3'
        }

        PhantomPowerCmdString = 'wZ4000{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)

    def __MatchPhantomPower(self, match, tag):

        InputStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PhantomPower', value, qualifier)

    def SetPrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        channel = qualifier['L/R']
        inputVal = int(qualifier['Input'])
        if -12 <= value <= 12 and 1 <= inputVal <= 8 and channel in channelStates:
            level = round(value * 10)
            channelValue = (inputVal * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1

            PrematrixTrimCmdString = 'wG{0}*{1}AU\r'.format(channelValue + 30100, level)
            self.__SetHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPrematrixTrim')

    def UpdatePrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left': 0,
            'Right': 1
        }

        inputVal = int(qualifier['Input'])
        channel = qualifier['L/R']

        if 1 <= inputVal <= 8 and channel in channelStates:
            channelValue = (inputVal * 2) - 2
            if channel == 'Right':
                channelValue = channelValue + 1
            PrematrixTrimCmdString = 'wG{0}AU\r'.format(channelValue + 30100)
            self.__UpdateHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePrematrixTrim')

    def __MatchPrematrixTrim(self, match, tag):

        qualifier = {}
        inputValue = int(match.group(1).decode())
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = int(match.group(2).decode()) / 10
        self.WriteStatus('PrematrixTrim', value, qualifier)

    def SetPremixerGain(self, value, qualifier):

        PremixerGainConstraints = {
            'Min': -100,
            'Max': 12,
        }

        PremixerConstraints = {
            'Min': 1,
            'Max': 4,
        }

        input_ = (int(qualifier['Input']) - 1)
        if PremixerGainConstraints['Min'] <= int(value) <= PremixerGainConstraints['Max'] and \
                PremixerConstraints['Min'] <= int(qualifier['Input']) <= PremixerConstraints['Max']:
            commandString = 'WG4010{0}*{1}AU\r'.format(input_, round(value * 10))
            self.__SetHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        PremixerConstraints = {
            'Min': 1,
            'Max': 4,
        }

        input_ = (int(qualifier['Input']) - 1)
        if PremixerConstraints['Min'] <= int(qualifier['Input']) <= PremixerConstraints['Max']:
            commandString = 'WG4010{0}AU\r'.format(input_)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, qualifier):

        InputNum = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4'
        }

        qualifier = {'Input': InputNum[match.group(1).decode()]}
        value = int(match.group(2)) / 10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPremixerMute(self, value, qualifier):

        MicInputStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        input_ = qualifier['Input']
        if input_ in ['1', '2', '3', '4']:
            PremixerMuteCmdString = 'WM4010{0}*{1}AU\r\n'.format(MicInputStates[input_], ValueStateValues[value])
            self.__SetHelper('PremixerMute', PremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerMute')

    def UpdatePremixerMute(self, value, qualifier):

        MicInputStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3'
        }

        input_ = qualifier['Input']
        if input_ in ['1', '2', '3', '4']:
            PremixerMuteCmdString = 'WM4010{0}AU\r'.format(MicInputStates[input_])
            self.__UpdateHelper('PremixerMute', PremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerMute')

    def __MatchPremixerMute(self, match, tag):

        MicInputStates = {
            '0': '1',
            '1': '2',
            '2': '3',
            '3': '4'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Input': MicInputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PremixerMute', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        Constraints = {
            'Max': 32,
            'Min': 1
        }

        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            PresetRecallCMDString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPostMatrixGain(self, value, qualifier):

        PostMatrixGainConstraints = {
            'Min': -100,
            'Max': 12,
        }

        PostMatrixConstraints = {
            'Min': 1,
            'Max': 4,
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if PostMatrixGainConstraints['Min'] <= int(value) <= PostMatrixGainConstraints['Max'] and \
                PostMatrixConstraints['Min'] <= output <= PostMatrixConstraints['Max']:
            commandString = 'WG5000{0}*{1}AU\r'.format(TranslationToNumber, round(value * 10))
            self.__SetHelper('PostMatrixGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPostMatrixGain')

    def UpdatePostMatrixGain(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        PostMatrixConstraints = {
            'Min': 1,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if PostMatrixConstraints['Min'] <= output <= PostMatrixConstraints['Max']:
            commandString = 'WG5000{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('PostMatrixGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePostMatrixGain')

    def __MatchPostMatrixGain(self, match, qualifier):

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = int(match.group(2)) / 10
        self.WriteStatus('PostMatrixGain', value, qualifier)

    def SetPostMatrixMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        PostMatrixConstraints = {
            'Min': 1,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if PostMatrixConstraints['Min'] <= output <= PostMatrixConstraints['Max']:
            commandString = 'WM5000{0}*{1}AU\r'.format(TranslationToNumber, MuteState[value])
            self.__SetHelper('PostMatrixMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPostMatrixMute')

    def UpdatePostMatrixMute(self, value, qualifier):

        channelSide = {
            'Left': 10,
            'Right': 20
        }

        PostMatrixConstraints = {
            'Min': 1,
            'Max': 4,
        }

        translation = {
            '11': 0,
            '21': 1,
            '12': 2,
            '22': 3,
            '13': 4,
            '23': 5,
            '14': 6,
            '24': 7,
        }

        channel = channelSide[qualifier['L/R']]
        output = int(qualifier['Output'])
        TranslationToNumber = translation[str((channel + output))]

        if PostMatrixConstraints['Min'] <= output <= PostMatrixConstraints['Max']:
            commandString = 'WM5000{0}AU\r'.format(TranslationToNumber)
            self.__UpdateHelper('PostMatrixMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePostMatrixMute')

    def __MatchPostMatrixMute(self, match, qualifier):

        MuteState = {
            '1': 'On',
            '0': 'Off'
        }

        channelSide = {
            0: 'Left',
            1: 'Right',
            2: 'Left',
            3: 'Right',
            4: 'Left',
            5: 'Right',
            6: 'Left',
            7: 'Right',
        }

        translation = {
            0: '1',
            1: '1',
            2: '2',
            3: '2',
            4: '3',
            5: '3',
            6: '4',
            7: '4',
        }

        qualifier = {'L/R': channelSide[int(match.group(1).decode())], 'Output': translation[int(match.group(1).decode())]}
        value = MuteState[match.group(2).decode()]
        self.WriteStatus('PostMatrixMute', value, qualifier)

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetScalerPresetRecall(self, value, qualifier):

        Output = qualifier['Output']
        if 3 <= int(Output) <= 4 and 1 <= int(value) <= 128:
            ScalerPresetRecallCmdString = '2*{0}*{1}.\r\n'.format(Output, value)
            self.__SetHelper('ScalerPresetRecall', ScalerPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetRecall')

    def SetScalerPresetSave(self, value, qualifier):

        Output = qualifier['Output']
        if 3 <= int(Output) <= 4 and 1 <= int(value) <= 128:
            ScalerPresetSaveCmdString = '2*{0}*{1},\r\n'.format(Output, value)
            self.__SetHelper('ScalerPresetSave', ScalerPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetSave')

    def SetTestPattern(self, value, qualifier):

        TestConstraints = {
            'Min': 3,
            'Max': 4,
        }

        TestPattern = {
            'Off': '0',
            'Crop': '1',
            'Alternating Pixels': '2',
            'Crosshatch': '3',
            'Color Bars': '4',
            'Grayscale': '5',
            'Blue Mode': '6',
            'Crop and Pink Noise': '7',
        }

        OutputNum = qualifier['Output']
        if TestConstraints['Min'] <= int(OutputNum) <= TestConstraints['Max']:
            TestPatternCMDString = 'W{0}*{1}TEST\r'.format(OutputNum, TestPattern[value])
            self.__SetHelper('TestPattern', TestPatternCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestConstraints = {
            'Min': 3,
            'Max': 4,
        }

        OutputNum = qualifier['Output']
        if TestConstraints['Min'] <= int(OutputNum) <= TestConstraints['Max']:
            UpdateCMDString = 'W{0}TEST\r'.format(OutputNum)
            self.__UpdateHelper('TestPattern', UpdateCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTestPattern')

    def __MatchTestPattern(self, match, qualifier):

        TestPattern = {
            '0': 'Off',
            '1': 'Crop',
            '2': 'Alternating Pixels',
            '3': 'Crosshatch',
            '4': 'Color Bars',
            '5': 'Grayscale',
            '6': 'Blue Mode',
            '7': 'Crop and Pink Noise',
        }

        qualifier = {'Output': str(int(match.group(1).decode()))}
        value = TestPattern[str(int(match.group(2).decode()))]
        self.WriteStatus('TestPattern', value, qualifier)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'S'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = round(float(match.group(1).decode()))
        self.WriteStatus('Temperature', value, None)

    def SetVideoMute(self, value, qualifier):

        TypeState = {
            'Video': '1',
            'Video & Sync': '2',
        }

        MuteConstraints = {
            'Min': 1,
            'Max': 4,
        }

        output = qualifier['Output']
        if MuteConstraints['Min'] <= int(output) <= MuteConstraints['Max']:
            if value == 'Off':
                commandString = '{0}*0B\r'.format(output)
            else:
                commandString = '{0}*{1}B\r'.format(output, TypeState[value])
            self.__SetHelper('VideoMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        MuteConstraints = {
            'Min': 1,
            'Max': 4,
        }

        output = qualifier['Output']
        if MuteConstraints['Min'] <= int(output) <= MuteConstraints['Max']:
            commandString = '{0}B\r'.format(output)
            self.__UpdateHelper('VideoMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, qualifier):

        Type = {
            '0': 'Off',
            '1': 'Video',
            '2': 'Video & Sync'
        }

        qualifier = {'Output': match.group(1).decode()}
        value = Type[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, qualifier)

    def SetVirtualReturnGain(self, value, qualifier):

        ChannelTranslation = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        channel = qualifier['Input']
        if channel in VirtualChannels and -100 <= value <= 12:
            level = round(value * 10)
            ChannelValue = ChannelTranslation[channel]
            commandString = 'WG5010{0}*{1}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnGain')

    def UpdateVirtualReturnGain(self, value, qualifier):

        ChannelTranslation = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        channel = qualifier['Input']
        if channel in VirtualChannels:
            ChannelValue = ChannelTranslation[channel]
            commandString = 'WG5010{0}AU\r\n'.format(ChannelValue)
            self.__UpdateHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnGain')

    def __MatchVirtualReturnGain(self, match, tag):

        ChannelRETranslation = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H',
        }

        channel = ChannelRETranslation[match.group(1).decode()]
        qualifier = {'Input': channel}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('VirtualReturnGain', value, qualifier)

    def SetVirtualReturnMute(self, value, qualifier):

        ChannelTranslation = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        MuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['Input']
        if channel in VirtualChannels:
            commandString = 'WM5010{0}*{1}AU\r\n'.format(ChannelTranslation[channel], MuteStateValues[value])
            self.__SetHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnMute')

    def UpdateVirtualReturnMute(self, value, qualifier):

        ChannelTranslation = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        channel = qualifier['Input']
        if channel in VirtualChannels:
            commandString = 'WM5010{0}AU\r\n'.format(ChannelTranslation[channel])
            self.__UpdateHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVirtualReturnMute')

    def __MatchVirtualReturnMute(self, match, tag):

        MuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        ChannelRETranslation = {
            '0': 'A',
            '1': 'B',
            '2': 'C',
            '3': 'D',
            '4': 'E',
            '5': 'F',
            '6': 'G',
            '7': 'H',
        }

        qualifier = {'Input': ChannelRETranslation[match.group(1).decode()]}
        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('VirtualReturnMute', value, qualifier)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '22': 'Busy',
            '24': 'Privileges violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found'
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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

        self.VerboseDisabled = True

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
        index = 0  # Start of possible good data

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
