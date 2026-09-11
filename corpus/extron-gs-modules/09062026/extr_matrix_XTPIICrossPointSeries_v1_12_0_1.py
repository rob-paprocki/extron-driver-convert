from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
from math import floor
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
        self.numOfInputs = 4
        self.numOfOutputs = 4
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'XTP II CrossPoint 1600': self.extr_15_1269_1600,
            'XTP II CrossPoint 3200': self.extr_15_1269_3200,
            'XTP II CrossPoint 6400': self.extr_15_1269_6400,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogOutputVolumeEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AudioMuteEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'EndpointTie': {'Parameters': ['Input'], 'Status': {}},
            'InputExecutiveModeEndpoint': {'Parameters': ['Input'], 'Status': {}},
            'OutputExecutiveModeEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'OutputImageResetEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'HDCPInputStatusEndpoint': {'Parameters': ['Input', 'Sub Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FreezeEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputAuthorizationEndpoint': {'Parameters': ['Input', 'Sub Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'InputAudioSwitchMode': {'Parameters': ['Input'], 'Status': {}},
            'InputAudioSwitchModeEndpoint': {'Parameters': ['Input', 'Sub Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatusEndpoint': {'Parameters': ['Input', 'Sub Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PowerSupplyStatus': {'Parameters': ['Number'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'RefreshMatrixIONames': {'Status': {}},
            'Relay': {'Parameters': ['Output', 'Relay'], 'Status': {}},
            'RelayPulse': {'Parameters': ['Output', 'Relay'], 'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'VideoMuteEndpoint': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
            'WindoWallAudioMute': {'Parameters': ['Wall'], 'Status': {}},
            'WindoWallPresetRecall': {'Status': {}},
            'WindoWallTie': {'Parameters': ['Wall', 'Tie Type'], 'Status': {}},
            'WindoWallVideoMute': {'Parameters': ['Wall'], 'Status': {}},
            'XTPInputPower': {'Parameters': ['Input'], 'Status': {}},
            'XTPInputPowerStatus': {'Parameters': ['Input'], 'Status': {}},
            'XTPOutputPower': {'Parameters': ['Output'], 'Status': {}},
            'XTPOutputPowerStatus': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        self.refresh_matrix = False
        self.ConfiguredWindoWallStatus = []

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'VolR(\d{2})\*([1-2])\*(\d{2})\r\n'), self.__MatchAnalogOutputVolumeEndpoint, None)
            self.AddMatchString(compile(b'Amt(0[1-9]|[1-5][0-9]|6[0-4])\*([0-3])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'AmtR(\d+)\*([1-4])\*([0-3])\r\n'), self.__MatchAudioMuteEndpoint, None)
            self.AddMatchString(compile(b'Exec([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'ExeT(0[1-9]|[1-2][0-9]|3[0-2])\*([0-1])\r\n'), self.__MatchInputExecutiveModeEndpoint, None)
            self.AddMatchString(compile(b'ExeR(0[1-9]|[1-2][0-9]|3[0-2])\*([0-1])\r\n'), self.__MatchOutputExecutiveModeEndpoint, None)
            self.AddMatchString(compile(b'Etie(0[1-9]|[1-5][0-9]|6[0-4])\*([1-3])\*([1-3])\r\n'), self.__MatchEndpointTie, None)
            self.AddMatchString(compile(b'FrzR(\d+)\*([1-2])\*([0-1])\r\n'), self.__MatchFreezeEndpoint, None)
            self.AddMatchString(compile(b'AfmtI(\d+)\*([0-3])\r\n'), self.__MatchInputAudioSwitchMode, None)
            self.AddMatchString(compile(b'AfmtT(\d+)\*([1-4])\*([0-3])\r\n'), self.__MatchInputAudioSwitchModeEndpoint, None)
            self.AddMatchString(compile(b'HdcpE(0[1-9]|[1-5][0-9]|6[0-4])\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpTE(0[1-9]|[1-2][0-9]|3[0-2])\*([1-4])\*(0|1)\r\n'), self.__MatchHDCPInputAuthorizationEndpoint, None)
            self.AddMatchString(compile(b'HdcpI00\*([012]+)\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpT(0[1-9]|[1-2][0-9]|3[0-2])\*([1-4])\*([012])\r\n'), self.__MatchHDCPInputStatusEndpoint, None)
            self.AddMatchString(compile(b'HdcpO00\*([0-7]+)\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Nm([io])([0-9]{1,2}),([ \S]{1,12})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(compile(b'Frq0+\*([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'LsT00\*([\d* ]+)\r\n'), self.__MatchInputSignalStatusEndpoint, 'Polled')
            self.AddMatchString(compile(b'LsT(0[1-9]|[1-2][0-9]|3[0-2])\*([0-1]{4})\r\n'), self.__MatchInputSignalStatusEndpoint, 'Unsolicited')
            self.AddMatchString(compile(b'Vmt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt[0-3]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-7]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(b'Rely(0[1-9]|[1-5][0-9]|6[0-4])\*([12])\*(1|0)\r\n'), self.__MatchRelay, None)
            self.AddMatchString(compile(b'Tst([01]\d)\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'VmtR(\d+)\*([1-2])\*([0-1])\r\n'), self.__MatchVideoMuteEndpoint, None)
            self.AddMatchString(compile(b'Out(\d{2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'PoecI00\*(?P<power>[01]{0,64})\r\n'), self.__MatchXTPInputPower, 'Polled')
            self.AddMatchString(compile(b'PoecI(?P<input>[0-9]{2})\*(?P<power>0|1)\*(?P<amount>00|13)\*(?P<status>[0-4])\r\n'), self.__MatchXTPInputPower, 'Unsolicited')
            self.AddMatchString(compile(b'PoecO00\*(?P<power>[01]{0,64})\r\n'), self.__MatchXTPOutputPower, 'Polled')
            self.AddMatchString(compile(b'PoecO(?P<output>[0-9]{2})\*(?P<power>0|1)\*(?P<amount>00|13)\*(?P<status>[0-4])\r\n'), self.__MatchXTPOutputPower, 'Unsolicited')
            self.AddMatchString(compile(b'Sts00\*(.*?)(?P<power>[01]{2,4})\r\n'), self.__MatchPowerSupplyStatus, None)
            self.AddMatchString(compile(b'Chop[BZ\$\%\!]0(?P<wall>0[1-9]|[1-5][0-9]|6[0-4])\*(?P<videoInput>[0-5][0-9]|6[0-4])\*(?P<audioInput>[0-5][0-9]|6[0-4])\*(?P<videoMute>[01])\*(?P<audioMute>[01])\r\n'), self.__MatchWindoWall, None)
            self.AddMatchString(compile(b'ChopR\d+\r\n'), self.__MatchQik, None)  # Response to a Set WindoWall Preset Recall command
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'PrstR\d+\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    @property
    def NumberofInputs(self):
        return self.numOfInputs

    @NumberofInputs.setter
    def NumberofInputs(self, value):
        if 1 <= int(value) <= 64:
            self.numOfInputs = int(value)

    @property
    def NumberofOutputs(self):
        return self.numOfOutputs

    @NumberofOutputs.setter
    def NumberofOutputs(self, value):
        if 1 <= int(value) <= 64:
            self.numOfOutputs = int(value)

    def SetPassword(self):

        self.Send(self.devicePassword + '\r\n')

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

    def __MatchVerboseMode(self, match, tag):
        self.OnConnected()

        self.VerboseDisabled = False
        self.SetRefreshMatrix('All', None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')

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

        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
        for w in self.ConfiguredWindoWallStatus:
            self.Send('\x1BZ{}CHOP\r'.format(w))

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')

        self.Send('w0*1*1vc\r')
        self.Send('w0*1*2vc\r')

        if self.OutputSize > 16:
            self.UpdateMatrix(16)

        if self.OutputSize > 32:
            self.UpdateMatrix(32)
            self.UpdateMatrix(64)

    def UpdateMatrix(self, output):

        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')

        if output == 16:
            self.Send('w0*17*1vc\r')
            self.Send('w0*17*2vc\r')
        elif output == 32:
            self.Send('w0*33*1vc\r')
            self.Send('w0*33*2vc\r')
        elif output == 64:
            self.Send('w0*49*1vc\r')
            self.Send('w0*49*2vc\r')

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

        matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self.numOfOutputs)})  # used to check if 'Matrix IO Name Status' exists or not
        for input_ in range(self.InputSize):
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': str(input_ + 1)})  # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName  # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                        if matrixIONameStatus:  # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Video'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output + 1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

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
            if self.InputSize == 16:
                self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAnalogOutputVolumeEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize and -64 <= value <= 0:
            self.__SetHelper('AnalogOutputVolumeEndpoint', '\x1bR{0}*{1}*{2}v\r'.format(output_, suboutput, value + 64), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogOutputVolumeEndpoint')

    def UpdateAnalogOutputVolumeEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('AnalogOutputVolumeEndpoint', '\x1bR{0}*{1}v\r'.format(output_, suboutput), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogOutputVolumeEndpoint')

    def __MatchAnalogOutputVolumeEndpoint(self, match, tag):

        self.WriteStatus('AnalogOutputVolumeEndpoint', int(match.group(3)) - 64, {'Output': str(int(match.group(1)))})

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '3',
        }

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize and value in AudioMuteState:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(output_, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('AudioMute', '{0}z'.format(output_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        AudioMuteName = {
            '0': 'Off',
            '3': 'On',
        }

        self.WriteStatus('AudioMute', AudioMuteName[match.group(2).decode()], {'Output': str(int(match.group(1)))})

    def SetAudioMuteEndpoint(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '3',
            'Analog': '2',
            'Digital': '1',
        }

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize and value in AudioMuteState:
            self.__SetHelper('AudioMuteEndpoint', '\x1bR{0}*{1}*{2}z\r'.format(output_, suboutput, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteEndpoint')

    def UpdateAudioMuteEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('AudioMuteEndpoint', '\x1bR{0}*{1}z\r'.format(output_, suboutput), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMuteEndpoint')

    def __MatchAudioMuteEndpoint(self, match, tag):

        AudioMuteName = {
            '0': 'Off',
            '3': 'On',
            '2': 'Analog',
            '1': 'Digital'
        }

        self.WriteStatus('AudioMuteEndpoint', AudioMuteName[match.group(3).decode()], {'Output': str(int(match.group(1)))})

    def SetEndpointTie(self, value, qualifier):

        input_ = int(qualifier['Input'])
        endpoint = int(value)
        if 1 <= input_ <= self.InputSize and 1 <= endpoint <= 3:
            EndpointTieCmdString = '\x1B{0}*{1}*3ETIE\r'.format(input_, endpoint)
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

    def __MatchEndpointTie(self, match, tag):
        self.WriteStatus('EndpointTie', match.group(2).decode(), {'Input': str(int(match.group(1).decode()))})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }

        if value in ExecutiveModeState:
            self.__SetHelper('ExecutiveMode', '\x1B{0}EXEC\r'.format(ExecutiveModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', '\x1BEXEC\r', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeName = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off'
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1).decode()], None)

    def SetFreezeEndpoint(self, value, qualifier):

        VideoMuteState = {
            'Enable': '1',
            'Disable': '0',
        }

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize and value in VideoMuteState:
            self.__SetHelper('FreezeEndpoint', '\x1bR{0}*{1}*{2}F\r'.format(output_, suboutput, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreezeEndpoint')

    def UpdateFreezeEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('FreezeEndpoint', '\x1bR{0}*{1}F\r'.format(output_, suboutput), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreezeEndpoint')

    def __MatchFreezeEndpoint(self, match, tag):

        VideoMuteName = {
            '0': 'Disable',
            '1': 'Enable',
        }

        self.WriteStatus('FreezeEndpoint', VideoMuteName[match.group(3).decode()], {'Output': str(int(match.group(1)))})

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '3',
        }

        if value in AudioMuteState:
            self.__SetHelper('GlobalAudioMute', '{0}*z'.format(AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }

        if value in VideoMuteState:
            self.__SetHelper('GlobalVideoMute', '{0}*b'.format(VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetHDCPInputAuthorization(self, value, qualifier):

        states = {
            'On': '1',
            'Off': '0'
        }

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize and value in states:
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

    def __MatchHDCPInputAuthorization(self, match, tag):
        states = {
            '1': 'On',
            '0': 'Off'
        }

        input_ = int(match.group(1).decode())
        value = match.group(2).decode()
        self.WriteStatus('HDCPInputAuthorization', states[value], {'Input': str(input_)})

    def SetHDCPInputAuthorizationEndpoint(self, value, qualifier):

        states = {
        	'On': '1',
        	'Off': '0'
        }

        input_ = qualifier['Input']
        subinput = qualifier['Sub Input']
        if 1 <= int(input_) <= self.InputSize and 1 <= int(subinput) <= 3 and value in states:
            HDCPInputAuthorizationCmdString = '\x1BTE{0}*{1}*{2}HDCP\r'.format(input_.zfill(2), subinput, states[value])
            self.__SetHelper('HDCPInputAuthorizationEndpoint', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorizationEndpoint')

    def UpdateHDCPInputAuthorizationEndpoint(self, value, qualifier):

        input_ = qualifier['Input']
        subinput = qualifier['Sub Input']
        if 1 <= int(input_) <= self.InputSize and 1 <= int(subinput) <= 3:
            commandstring = '\x1BTE{0}*{1}HDCP\r'.format(input_, subinput)
            self.__UpdateHelper('HDCPInputAuthorizationEndpoint', commandstring, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorizationEndpoint')

    def __MatchHDCPInputAuthorizationEndpoint(self, match, tag):

        states = {
        	'1': 'On',
        	'0': 'Off'
        }

        input_ = int(match.group(1).decode())
        subinput = int(match.group(2).decode())
        value = match.group(3).decode()
        self.WriteStatus('HDCPInputAuthorizationEndpoint', states[value], {'Input': str(input_), 'Sub Input': str(subinput)})

    def UpdateHDCPInputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPInputStatus', 'wI*HDCP\r', value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        HDCPInputStatus = {
            '0': 'No Source Connected',
            '2': 'No HDCP Content',
            '1': 'HDCP Content'
        }

        results = match.group(1).decode()
        for index, value in enumerate(results):
            self.WriteStatus('HDCPInputStatus', HDCPInputStatus[value], {'Input': str(index + 1)})

    def UpdateHDCPInputStatusEndpoint(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputSize and 1 <= int(qualifier['Sub Input']) <= 3:
            self.__UpdateHelper('HDCPInputStatusEndpoint', 'wT{0}*{1}HDCP\r'.format(qualifier['Input'], qualifier['Sub Input']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatusEndpoint')

    def __MatchHDCPInputStatusEndpoint(self, match, tag):

        HDCPInputStatus = {
            '0': 'No Source Connected',
            '2': 'No HDCP Content',
            '1': 'HDCP Content'
        }

        state = match.group(3).decode()
        inputNumber = int(match.group(1).decode())
        subinput = match.group(2).decode()
        self.WriteStatus('HDCPInputStatusEndpoint', HDCPInputStatus[state], {'Input': str(inputNumber), 'Sub Input': subinput})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPOutputStatus', 'wO*HDCP\r', value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

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

        results = match.group(1).decode()
        for index, value in enumerate(results):
            self.WriteStatus('HDCPOutputStatus', HDCPOutputStatus[value], {'Output': str(index + 1)})

    def SetInputAudioSwitchMode(self, value, qualifier):

        InputAudioSwitchModeState = {
            'Auto': '0',
            'Digital': '1',
            'Local 2 Ch Audio': '2',
            'Digital Multi-Ch Audio': '3',

        }

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize and value in InputAudioSwitchModeState:
            self.__SetHelper('InputAudioSwitchMode', '\x1bI{0}*{1}AFMT\r'.format(input_, InputAudioSwitchModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchMode')

    def UpdateInputAudioSwitchMode(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize:
            self.__UpdateHelper('InputAudioSwitchMode', '\x1bI{0}AFMT\r'.format(input_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioSwitchMode')

    def __MatchInputAudioSwitchMode(self, match, tag):

        InputAudioSwitchModeName = {
            '0': 'Auto',
            '1': 'Digital',
            '2': 'Local 2 Ch Audio',
        }

        self.WriteStatus('InputAudioSwitchMode', InputAudioSwitchModeName[match.group(2).decode()], {'Input': str(int(match.group(1)))})

    def SetInputAudioSwitchModeEndpoint(self, value, qualifier):

        InputAudioSwitchModeState = {
            'Auto': '0',
            'Digital': '1',
            'Local 2 Ch Audio': '2',
        }

        input_ = int(qualifier['Input'])
        subinput = int(qualifier['Sub Input'])
        if 1 <= input_ <= self.InputSize and 1 <= subinput <= 3 and value in InputAudioSwitchModeState:
            self.__SetHelper('InputAudioSwitchModeEndpoint', '\x1bT{0}*{1}*{2}AFMT\r'.format(input_, subinput, InputAudioSwitchModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchModeEndpoint')

    def UpdateInputAudioSwitchModeEndpoint(self, value, qualifier):

        input_ = int(qualifier['Input'])
        subinput = int(qualifier['Sub Input'])
        if 1 <= input_ <= self.InputSize and 1 <= subinput <= 3:
            self.__UpdateHelper('InputAudioSwitchModeEndpoint', '\x1bT{0}*{1}AFMT\r'.format(input_, subinput), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioSwitchModeEndpoint')

    def __MatchInputAudioSwitchModeEndpoint(self, match, tag):

        InputAudioSwitchModeName = {
            '0': 'Auto',
            '1': 'Digital',
            '2': 'Local 2 Ch Audio',
        }

        self.WriteStatus('InputAudioSwitchModeEndpoint', InputAudioSwitchModeName[match.group(3).decode()], {'Input': str(int(match.group(1))), 'Sub Input': str(int(match.group(2)))})

    def SetInputExecutiveModeEndpoint(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1',
            'Off': '0'
        }

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize and value in ExecutiveModeState:
            self.__SetHelper('InputExecutiveModeEndpoint', '\x1BT{0}*{1}X\r'.format(input_, ExecutiveModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputExecutiveModeEndpoint')

    def UpdateInputExecutiveModeEndpoint(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize:
            self.__UpdateHelper('InputExecutiveModeEndpoint', '\x1BT{0}X\r'.format(input_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputExecutiveModeEndpoint')

    def __MatchInputExecutiveModeEndpoint(self, match, tag):

        ExecutiveModeName = {
            '1': 'On',
            '0': 'Off'
        }

        input_ = int(match.group(1).decode())
        self.WriteStatus('InputExecutiveModeEndpoint', ExecutiveModeName[match.group(2).decode()], {'Input': str(input_)})

    def SetOutputExecutiveModeEndpoint(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1',
            'Off': '0'
        }

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize and value in ExecutiveModeState:
            self.__SetHelper('OutputExecutiveModeEndpoint', '\x1BR{0}*{1}X\r'.format(output_, ExecutiveModeState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputExecutiveModeEndpoint')

    def UpdateOutputExecutiveModeEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('OutputExecutiveModeEndpoint', '\x1BR{0}X\r'.format(output_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputExecutiveModeEndpoint')

    def __MatchOutputExecutiveModeEndpoint(self, match, tag):

        ExecutiveModeName = {
            '1': 'On',
            '0': 'Off'
        }

        output_ = int(match.group(1).decode())
        self.WriteStatus('OutputExecutiveModeEndpoint', ExecutiveModeName[match.group(2).decode()], {'Output': str(output_)})

    def SetOutputImageResetEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize:
            OutputImageResetEndpointCmdString = 'wR{0}*{1}*2AADJ\r'.format(output_, suboutput)
            self.__SetHelper('OutputImageResetEndpoint', OutputImageResetEndpointCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputImageResetEndpoint')

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active'
        }

        results = match.group(1).decode()
        for index, value in enumerate(results):
            self.WriteStatus('InputSignalStatus', InputSignalStatus[value], {'Input': str(index + 1)})

    def UpdateInputSignalStatusEndpoint(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatusEndpoint', '\x1bTLS\r', value, qualifier)

    def __MatchInputSignalStatusEndpoint(self, match, tag):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active'
        }

        if tag == 'Polled':
            results = match.group(1).decode()
            for result in results.split():
                inputNumber = str(int(result.split('*')[0]))
                for index in range(4):
                    signal = result.split('*')[1][index]
                    self.WriteStatus('InputSignalStatusEndpoint', InputSignalStatus[signal], {'Input': inputNumber, 'Sub Input': str(index + 1)})
        else:
            inputNumber = str(int(match.group(1).decode()))
            results = match.group(2).decode()
            for index, signal in enumerate(results):
                self.WriteStatus('InputSignalStatusEndpoint', InputSignalStatus[signal], {'Input': inputNumber, 'Sub Input': str(index + 1)})

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Matrix IO Number']
        name = qualifier['Matrix IO Name']
        if number and name and 1 <= len(name) <= 12 and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = str(int(match.group(2).decode()))
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        if type_ == 'Input':  # only write the name if type is input
            for x in range(1, self.InputSize + 1):
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Audio'})  # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Video'})  # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio/Video'})

    def SetRefreshMatrixIONames(self, value, qualifier):

        self.UpdateMatrixIONames(None, None)

    def UpdateMatrixIONames(self, value, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '22': 'Busy',
            '24': 'Privilege violation (Users have access to all view and read commands [other than the administrator password], and can create ties, presets, and audio mutes',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename / file not found'
        }
        for i in range(1, self.numOfInputs + 1):
            if i <= self.InputSize:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')

                res = self.SendAndWait('w{0}NI\r'.format(i), 0.2, deliTag='\n')
                if res:
                    print('res[0:1]', res[0:1])
                    if res[0:1] == b'N':
                        num = int(res[3:5])
                        value = res[6:-2]
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Input', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Input {0} Name: {1}'.format(i, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Input {0} Name: Unrecognized error code: {1}'.format(i, DEVICE_ERROR_CODES[res[0:3]])])
                else:
                    self.Error(['Matrix Input {0} Name: Invalid/unexpected response'.format(i)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')
        for i in range(1, self.numOfOutputs + 1):
            if i <= self.OutputSize:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')

                res = self.SendAndWait('w{0}NO\r'.format(i), 0.2, deliTag='\n')
                print('Response', res)
                if res:
                    if res[0:1] == b'N':
                        num = int(res[3:5])
                        value = res[6:-2]
                        self.WriteStatus('MatrixIONameStatus', value, {'Type': 'Output', 'Number': str(num)})
                    else:
                        if res[1:3] in DEVICE_ERROR_CODES:
                            self.Error(['Matrix Output {0} Name: {1}'.format(i, DEVICE_ERROR_CODES[res[1:3]])])
                        else:
                            self.Error(['Matrix Output {0} Name: Unrecognized error code: {1}'.format(i, DEVICE_ERROR_CODES[res[0:3]])])
                else:
                    self.Error(['Matrix Output {0} Name: Invalid/unexpected response'.format(i)])
            else:
                self.Discard('Invalid Command for UpdateMatrixIONames')

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

    def __MatchOutputTieStatus(self, match, tag):
        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, tag):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video'
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
        if self.InputSize == 16:
            self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, tag):

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

        if self.InputSize == 16:
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

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetRecall', '\x1BR{0}PRST\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetSave', '\x1BS{0}PRST\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        state = {
            '1 - 16': 'w0*1*1vc\rw0*1*2vc\r',
            '17 - 32': 'w0*17*1vc\rw0*17*2vc\r',
            '33 - 48': 'w0*33*1vc\rw0*33*2vc\r',
            '49 - 64': 'w0*49*1vc\rw0*49*2vc\r'
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie(value, qualifier)
        elif value in state:
            self.refresh_matrix = True
            self.audio_status_counter = 0
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', state[value], value, qualifier)  # delay of 5 seconds
        else:
            self.Discard('Invalid Command for SetRefreshMatrix')

    def SetRelay(self, value, qualifier):

        RelayState = {
            'Close': '1',
            'Open': '0',
        }

        output_ = int(qualifier['Output'])
        relay = int(qualifier['Relay'])
        if 1 <= output_ <= self.OutputSize and 1 <= relay <= 2 and value in RelayState:
            self.__SetHelper('Relay', 'w{0}*{1}*{2}RELY\r'.format(output_, relay, RelayState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        output_ = int(qualifier['Output'])
        relay = int(qualifier['Relay'])
        if 1 <= output_ <= self.OutputSize and 1 <= relay <= 2:
            self.__UpdateHelper('Relay', 'w{0}*{1}RELY\r'.format(output_, relay), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRelay')

    def __MatchRelay(self, match, tag):

        RelayState = {
            '1': 'Close',
            '0': 'Open',
        }

        output_ = int(match.group(1))
        relay = int(match.group(2))
        self.WriteStatus('Relay', RelayState[match.group(3).decode()], {'Output': str(output_), 'Relay': str(relay)})

    def SetRelayPulse(self, value, qualifier):

        output = int(qualifier['Output'])
        relay = int(qualifier['Relay'])
        if 1 <= output <= self.OutputSize and 1 <= relay <= 2 and 0.1 <= value <= 1048.5:
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

        if value in ValueStateValues:
            TestPatternCmdString = '\x1B{0}TEST\r'.format(ValueStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

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

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize and value in VideoMuteState:
            self.__SetHelper('VideoMute', '{0}*{1}b'.format(output_, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('VideoMute', '{0}b'.format(output_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2).decode()], {'Output': str(int(match.group(1)))})

    def SetVideoMuteEndpoint(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize and value in VideoMuteState:
            self.__SetHelper('VideoMuteEndpoint', '\x1bR{0}*{1}*{2}b\r'.format(output_, suboutput, VideoMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMuteEndpoint')

    def UpdateVideoMuteEndpoint(self, value, qualifier):

        output_ = int(qualifier['Output'])
        suboutput = 1
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('VideoMuteEndpoint', '\x1bR{0}*{1}b\r'.format(output_, suboutput), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMuteEndpoint')

    def __MatchVideoMuteEndpoint(self, match, tag):

        VideoMuteName = {
            '0': 'Off',
            '1': 'On',
        }

        self.WriteStatus('VideoMuteEndpoint', VideoMuteName[match.group(3).decode()], {'Output': str(int(match.group(1)))})

    def SetVolume(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize and -64 <= value <= 0:
            self.__SetHelper('Volume', '{0}*{1}v'.format(output_, value + 64), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize:
            self.__UpdateHelper('Volume', '{0}v'.format(output_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        self.WriteStatus('Volume', int(match.group(2)) - 64, {'Output': str(int(match.group(1)))})

    def SetWindoWallAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Wall']) <= 64 and value in ValueStateValues:
            self.__SetHelper('WindoWallAudioMute', '\x1BZ{}*{}CHOP\r'.format(qualifier['Wall'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindoWallAudioMute')

    def UpdateWindoWallAudioMute(self, value, qualifier):

        if qualifier['Wall'] not in self.ConfiguredWindoWallStatus:
            self.ConfiguredWindoWallStatus.append(qualifier['Wall'])

        wall = int(qualifier['Wall'])
        if 1 <= wall <= 64:
            self.__UpdateHelper('WindoWallAudioMute', '\x1BZ{}CHOP\r'.format(qualifier['Wall']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindoWallAudioMute')

    def __MatchWindoWall(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        wall = str(int(match.group('wall').decode()))

        self.WriteStatus('WindoWallAudioMute', ValueStateValues[match.group('audioMute').decode()], {'Wall': wall})
        self.WriteStatus('WindoWallVideoMute', ValueStateValues[match.group('videoMute').decode()], {'Wall': wall})

        audioInput = str(int(match.group('audioInput').decode()))
        videoInput = str(int(match.group('videoInput').decode()))

        self.WriteStatus('WindoWallTie', audioInput, {'Wall': wall, 'Tie Type': 'Audio'})
        self.WriteStatus('WindoWallTie', videoInput, {'Wall': wall, 'Tie Type': 'Video'})

        if audioInput == videoInput:
            self.WriteStatus('WindoWallTie', audioInput, {'Wall': wall, 'Tie Type': 'Audio Video'})
        else:
            self.WriteStatus('WindoWallTie', '0', {'Wall': wall, 'Tie Type': 'Audio Video'})

    def SetWindoWallPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            self.__SetHelper('WindoWallPresetRecall', '\x1BR{}CHOP\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindoWallPresetRecall')

    def SetWindoWallTie(self, value, qualifier):

        TieTypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio Video': '!'
        }

        if 1 <= int(qualifier['Wall']) <= 64 and qualifier['Tie Type'] in TieTypeStates and 0 <= int(value) <= self.OutputSize:
            self.__SetHelper('WindoWallTie', '\x1B{}{}*{}CHOP\r'.format(TieTypeStates[qualifier['Tie Type']], qualifier['Wall'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindoWallTie')

    def UpdateWindoWallTie(self, value, qualifier):

        TieTypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio Video': '!'
        }

        if qualifier['Wall'] not in self.ConfiguredWindoWallStatus:
            self.ConfiguredWindoWallStatus.append(qualifier['Wall'])

        wall = int(qualifier['Wall'])
        if 1 <= wall <= 64 and qualifier['Tie Type'] in TieTypeStates:
            self.__UpdateHelper('WindoWallTie', '\x1B{}{}CHOP\r'.format(TieTypeStates[qualifier['Tie Type']], qualifier['Wall']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWindoWallTie')

    def SetWindoWallVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Wall']) <= 64 and value in ValueStateValues:
            self.__SetHelper('WindoWallVideoMute', '\x1BB{}*{}CHOP\r'.format(qualifier['Wall'], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindoWallVideoMute')

    def UpdateWindoWallVideoMute(self, value, qualifier):

        if qualifier['Wall'] not in self.ConfiguredWindoWallStatus:
            self.ConfiguredWindoWallStatus.append(qualifier['Wall'])

        wall = int(qualifier['Wall'])
        if 1 <= wall <= 64:
            self.__UpdateHelper('WindoWallVideoMute', '\x1BB{}CHOP\r'.format(qualifier['Wall']), value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateWindoWallVideoMute')

    def SetXTPInputPower(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize and value in ValueStateValues:
            XTPInputPowerCmdString = 'wI{0}*{1}POEC\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('XTPInputPower', XTPInputPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXTPInputPower')

    def UpdateXTPInputPower(self, value, qualifier):

        XTPInputPowerCmdString = 'wIPOEC\r'
        self.__UpdateHelper('XTPInputPower', XTPInputPowerCmdString, value, qualifier)

    def __MatchXTPInputPower(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        PowerStateValues = {
            '0': 'Unpowerable endpoint',
            '1': 'Power is being provided to the endpoint',
            '2': 'Power available for the endpoint, but disabled',
            '3': 'No power available for the endpoint, but enabled',
            '4': 'Fault'
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
                self.WriteStatus('XTPInputPowerStatus', PowerStateValues[match.group('status').decode()], {'Input': input_})

    def UpdateXTPInputPowerStatus(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= self.InputSize:
            XTPInputPowerStatusCmdString = 'wI{}POEC\r'.format(input_)
            self.__UpdateHelper('XTPInputPowerStatus', XTPInputPowerStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateXTPInputPowerStatus')

    def SetXTPOutputPower(self, value, qualifier):

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize and value in ValueStateValues:
            XTPOutputPowerCmdString = 'wO{0}*{1}POEC\r'.format(output_, ValueStateValues[value])
            self.__SetHelper('XTPOutputPower', XTPOutputPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetXTPOutputPower')

    def UpdateXTPOutputPower(self, value, qualifier):

        XTPOutputPowerCmdString = 'wOPOEC\r'
        self.__UpdateHelper('XTPOutputPower', XTPOutputPowerCmdString, value, qualifier)

    def __MatchXTPOutputPower(self, match, tag):

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        PowerStateValues = {
            '0': 'Unpowerable endpoint',
            '1': 'Power is being provided to the endpoint',
            '2': 'Power available for the endpoint, but disabled',
            '3': 'No power available for the endpoint, but enabled',
            '4': 'Fault'
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
                self.WriteStatus('XTPOutputPowerStatus', PowerStateValues[match.group('status').decode()], {'Output': output})
                
    def UpdateXTPOutputPowerStatus(self, value, qualifier):

        output_ = int(qualifier['Output'])
        if 1 <= output_ <= self.OutputSize:
            XTPOutputPowerStatusCmdString = 'wO{}POEC\r'.format(output_)
            self.__UpdateHelper('XTPOutputPowerStatus', XTPOutputPowerStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateXTPOutputPowerStatus')

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Timeout (caused only by direct write of global presets)',
            '22': 'Busy',
            '24': 'Privilege violation (Users have access to all view and read commands [other than the administrator password], and can create ties, presets, and audio mutes',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename / file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: E'+ value])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            print(command, value, qualifier)
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
                    print(command, value, qualifier)
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
        self.refresh_matrix = False
        self.ConfiguredWindoWallStatus = []
        
    def extr_15_1269_1600(self):
        self.InputSize = 16
        self.OutputSize = 16

    def extr_15_1269_3200(self):
        self.InputSize = 32
        self.OutputSize = 32

    def extr_15_1269_6400(self):
        self.InputSize = 64
        self.OutputSize = 64

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
