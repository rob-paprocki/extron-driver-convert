from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import time
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
        self.Models = {
            'DTP CrossPoint 108 4K': self.extr_15_1691_108,
            'DTP CrossPoint 108 4K IPCP SA': self.extr_15_1691_108_SA,
            'DTP CrossPoint 108 4K IPCP MA 70': self.extr_15_1691_108_MA,
            'DTP CrossPoint 86 4K': self.extr_15_1691_86,
            'DTP CrossPoint 86 4K IPCP SA': self.extr_15_1691_86_SA,
            'DTP CrossPoint 86 4K IPCP MA 70': self.extr_15_1691_86_MA,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmplifierAttenuationMA': { 'Status': {}},
            'AmplifierAttenuationSA': {'Parameters':['L/R'], 'Status': {}},
            'AmplifierMuteMA': { 'Status': {}},
            'AmplifierMuteSA': {'Parameters':['L/R'], 'Status': {}},
            'AmplifierPostmixerTrim': {'Parameters':['L/R'], 'Status': {}},
            'AnalogAttenuation': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'AnalogMute': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'AspectRatio': {'Parameters':['Input'], 'Status': {}},
            'AutoImage': {'Parameters':['Output'], 'Status': {}},
            'DTPAttenuation': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'DTPMute': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'EDIDAssignment': {'Parameters':['Input'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'ExpansionPremixerGain': {'Parameters':['Input'], 'Status': {}},
            'ExpansionPremixerMute': {'Parameters':['Input'], 'Status': {}},
            'Freeze': {'Parameters':['Output'], 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'GroupMicLineInputGain': {'Parameters':['Group'], 'Status': {}},
            'GroupMixpoint': {'Parameters':['Group'], 'Status': {}},
            'GroupMute': {'Parameters':['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters':['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters':['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters':['Group'], 'Status': {}},
            'GroupPrematrixTrim': {'Parameters':['Group'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputAuthorization': {'Parameters':['Output'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Output'], 'Status': {}},
            'HDMIAttenuation': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'HDMIMute': {'Parameters':['L/R', 'Output'], 'Status': {}},
            'InputAudioSwitchMode': {'Parameters':['Input'], 'Status': {}},
            'InputFormat': {'Parameters':['Input'], 'Status': {}},
            'InputGain': {'Parameters':['Format', 'L/R', 'Input'], 'Status': {}},
            'InputMute': {'Parameters':['L/R', 'Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters':['Input','Output'], 'Status': {}},
            'Logo': {'Parameters':['Output'], 'Status': {}},
            'LogoAssignment': {'Parameters':['Logo'], 'Status': {}},
            'LogoAvailability': {'Parameters':['Logo'], 'Status': {}},
            'LogoKeySetting': {'Parameters':['Output'], 'Status': {}},
            'MatrixIONameCommand': {'Parameters':['Type'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters':['Type','Number'], 'Status': {}},
            'MatrixTieCommand': {'Parameters':['Input','Output','Tie Type'], 'Status': {}},
            'MicLineGain': {'Parameters': ['Input'], 'Status': {}},
            'MicLineMute': {'Parameters':['Input'], 'Status': {}},
            'MicrophoneSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'MixpointGain': {'Parameters':['Input','Output'], 'Status': {}},
            'MixpointMute': {'Parameters':['Input','Output'], 'Status': {}},
            'OutputAudioSelect': {'Parameters':['Output'], 'Status': {}},
            'OutputPostmixerTrim': {'Parameters':['L/R','Output'], 'Status': {}},
            'OutputResolution': {'Parameters':['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters':['Output','Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters':['Output','Tie Type'], 'Status': {}},
            'PhantomPower': {'Parameters':['Input'], 'Status': {}},
            'PostMatrixGain': {'Parameters':['Output','L/R'], 'Status': {}},
            'PostMatrixMute': {'Parameters':['Output','L/R'], 'Status': {}},
            'PrematrixTrim': {'Parameters':['L/R', 'Input'], 'Status': {}},
            'PremixerGain': {'Parameters':['Input'], 'Status': {}},
            'PremixerMute': {'Parameters':['Input'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'ScalerPresetRecall': {'Parameters':['Output'], 'Status': {}},
            'ScalerPresetSave': {'Parameters':['Output'], 'Status': {}},
            'TestPattern': {'Parameters':['Output'], 'Status': {}},
            'Temperature': { 'Status': {}},
            'VideoMute': {'Parameters':['Output'], 'Status': {}},
            'VirtualReturnGain': {'Parameters':['Input'], 'Status': {}},
            'VirtualReturnMute': {'Parameters':['Input'], 'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.GroupFunction = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Rpr\d\*\d+\r\n'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'Ds[gG]600(16|17)\*([-]\d{1,4}|0)\r\n'), self.__MatchAmplifierAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]600(16|17)\*(0|1)\r\n'), self.__MatchAmplifierMute, None)
            self.AddMatchString(re.compile(b'Ds[gG]6011([67])\*([0-9 -]{1,4})\r\n'), self.__MatchAmplifierPostmixerTrim, None)
            self.AddMatchString(re.compile(b'Ds[gG]6000([0-7])\*([-]\d{1,4}|0)\r\n'), self.__MatchAnalogAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]6000([0-7])\*(0|1)\r\n'), self.__MatchAnalogMute, None)
            self.AddMatchString(re.compile(b'Aspr(\d{2})\*(1|2)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'GrpmD(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32)\*([-+]{0,1}[0-9]{1,4})\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'Ds[gG]600(08|09|10|11|12|13|14|15)\*([-]\d{1,4}|0)\r\n'), self.__MatchDTPAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]600(08|09|10|11|12|13|14|15)\*(0|1)\r\n'), self.__MatchDTPMute, None)
            self.AddMatchString(re.compile(b'EdidA(0[1-9]|10)\*(0?[1-9]|[1-5][0-9]|6[0-6])\r\n'), self.__MatchEDIDAssignment, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Ds[gG]502([01][0-9])\*([0-9 -]{1,5})\r\n'), self.__MatchExpansionPremixerGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]502([01][0-9])\*([01])\r\n'), self.__MatchExpansionPremixerMute, None)
            self.AddMatchString(re.compile(b'Frz(\d{2})\*(00|01)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Ds[gG]6020([0-7])\*([-]\d{1,4}|0)\r\n'), self.__MatchHDMIAttenuation, None)
            self.AddMatchString(re.compile(b'Ds[mM]6020([0-7])\*(0|1)\r\n'), self.__MatchHDMIMute, None)
            self.AddMatchString(re.compile(b'AfmtI(\d{2})\*([0-2])\r\n'), self.__MatchInputAudioSwitchMode, 'Single')
            self.AddMatchString(re.compile(b'AfmtI([0-2]{10}|[0-2]{8})\r\n'), self.__MatchInputAudioSwitchMode, 'All')
            self.AddMatchString(re.compile(b'Ds([gGhH])300([01][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]300([01][0-9])\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'Ityp(0[1-9]|10)\*([0-7])\r\n'), self.__MatchInputFormat, None)
            self.AddMatchString(re.compile(b'Frq00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'HdcpE(\d{2})\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'LogoE([3-8])\*(.*)\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'LogoQ00\*([01]+)[\*01]+\r\n'), self.__MatchLogoAvailability, None)
            self.AddMatchString(re.compile(b'Vkef00([1-8])\*([0-4])\r\n'), self.__MatchLogoKeySetting, None)
            self.AddMatchString(re.compile(b'Nm([io])([1-9]|10),([ \S]{0,16})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'Ds[gG]4000([0-3])\*([0-9 -]{1,4})\r\n'), self.__MatchMicLineGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]4000([0-3])\*(0|1)\r\n'), self.__MatchMicLineMute, None)
            self.AddMatchString(re.compile(b'Ds[vV]4000([0-3])\*[01]\*([0-9]{1,4})\r\n'), self.__MatchMicrophoneSignalStatus, None)
            self.AddMatchString(re.compile(b'Ds[gG]2([0-9]{2})([0-9]{2})\*([-][0-9]{1,4}|0|[0-9]{1,3})\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]2([0-9]{2})([0-9]{2})\*(0|1)\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(re.compile(b'AfmtO(\d{2})\*([0-2])\r\n'), self.__MatchOutputAudioSelect, 'Single')
            self.AddMatchString(re.compile(b'AfmtO([0-2]{2,8})\r\n'), self.__MatchOutputAudioSelect, 'All')
            self.AddMatchString(re.compile(b'HdcpS(([1-8])(A|B|a|b|))\*(0|1)\r\n'), self.__MatchHDCPOutputAuthorization, None)
            self.AddMatchString(re.compile(b'Ds[gG]601(0[0-9]|1[0-5])\*([0-9 -]{1,4})\r\n'), self.__MatchOutputPostmixerTrim, None)
            self.AddMatchString(re.compile(b'HdcpI(\d{2})\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO(1|2|3|3A|3B|4|4A|4B|5|5A|5B|6|6A|6B|7|8)\*([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Rate(\d{2})\*(\d{2})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'DsZ4000([0-3])\*([01])\r\n'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'Ds[gG]301([01][0-9])\*([0-9 -]{1,4})\r\n'), self.__MatchPrematrixTrim, None)
            self.AddMatchString(re.compile(b'Ds[gG]500([01][0-9])\*([-]\d{1,4}|\d{1,3})\r\n'), self.__MatchPostMatrixGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]500([01][0-9])\*(0|1)\r\n'), self.__MatchPostMatrixMute, None)
            self.AddMatchString(re.compile(b'Ds[gG]4010([0-7])\*(-*\d{1,4})\r\n'), self.__MatchPremixerGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]4010([0-7])\*(0|1)\r\n'), self.__MatchPremixerMute, None)
            self.AddMatchString(re.compile(b'Sts00\*\d{1,3}\.\d{1,3} (\d{1,3}\.\d{1,3}) \d+ \d+\r\n'), self.__MatchTemperature, None),
            self.AddMatchString(re.compile(b'Test0([3-8])\*0([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'Vmt(([1-8])(A|B|a|b|))\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Ds[gG]5010([0-7])\*([-]\d{1,4}|\d{1,3})\r\n'), self.__MatchVirtualReturnGain, None)
            self.AddMatchString(re.compile(b'Ds[mM]5010([0-7])\*([0-1])\r\n'), self.__MatchVirtualReturnMute, None)
            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'PrstR\d+\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(re.compile(b'Vgp00 Out(\d{2})\*([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(re.compile(b'E(01|1[0-7]|2[245678]|3[012])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)


    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie( None, None)

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False


    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie( None, None)

    def __MatchPreset(self, match, tag):
        self.UpdateAllMatrixTie( None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSize)

        matrixIONameStatus = self.ReadStatus('MatrixIONameStatus', {'Type': 'Output', 'Number': str(self.OutputSize)}) # used to check if 'Matrix IO Name Status' exists or not
        for input_ in range(self.InputSize):
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': str(input_+1)}) # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': tie_type})
                        if matrixIONameStatus: # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Video'})
                    if matrixIONameStatus:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': str(output+1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio/Video'})
                if matrixIONameStatus:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': str(o+1), 'Tie Type': 'Audio/Video'})

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

        if self.audio_status_counter == self.OutputSize and self.video_status_counter == self.OutputSize:
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAmplifierAttenuationSA(self, value, qualifier):

        channelSide = {
            'Left' :'16',
            'Right':'17'
        }

        if -100 <= int(value) <= 0 and qualifier['L/R'] in channelSide:
            commandString = 'WG600{0}*{1}AU\r'.format(channelSide[qualifier['L/R']],round(value*10))
            self.__SetHelper('AmplifierAttenuationSA', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierAttenuationSA')

    def UpdateAmplifierAttenuationSA(self, value, qualifier):

        channelSide = {
            'Left' :'16',
            'Right':'17'
        }

        if qualifier['L/R'] in channelSide:
            channel = channelSide[qualifier['L/R']]
            commandString = 'WG600{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierAttenuationSA', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierAttenuationSA')

    def __MatchAmplifierAttenuation(self, match, qualifier):

        channelSide = {
            '16':'Left',
            '17':'Right'
        }

        value = int(match.group(2))/10
        if hasattr(self, 'Amplifier'):
            if self.Amplifier == 'Stereo':
                qualifier = {'L/R' :channelSide[match.group(1).decode()]}
                self.WriteStatus('AmplifierAttenuationSA', value, qualifier)
            elif self.Amplifier == 'Mono':
                self.WriteStatus('AmplifierAttenuationMA', value, None)
        else:
            self.Error(['Incorrect model'])

    def SetAmplifierAttenuationMA(self, value, qualifier):

        if -100 <= value <= 0:
            AmplifierAttenuationMACmdString = 'WG60016*{0}AU\r'.format(round(value*10))
            self.__SetHelper('AmplifierAttenuationMA', AmplifierAttenuationMACmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierAttenuationMA')

    def UpdateAmplifierAttenuationMA(self, value, qualifier):

        AmplifierAttenuationMACmdString = 'WG60016AU\r'
        self.__UpdateHelper('AmplifierAttenuationMA', AmplifierAttenuationMACmdString, value, qualifier)

    def SetAmplifierMuteSA(self, value, qualifier):

        MuteState = {
            'On' :'1',
            'Off':'0'
        }

        channelSide = {
            'Left' :'16',
            'Right':'17'
        }

        if value in MuteState and qualifier['L/R'] in channelSide:
            channel = channelSide[qualifier['L/R']]
            commandString = 'WM600{0}*{1}AU\r'.format(channel,MuteState[value])
            self.__SetHelper('AmplifierMuteSA', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierMuteSA')

    def UpdateAmplifierMuteSA(self, value, qualifier):

        channelSide = {
            'Left' :'16',
            'Right':'17'
        }

        if qualifier['L/R'] in channelSide:
            channel = channelSide[qualifier['L/R']]
            commandString = 'WM600{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierMuteSA', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierMuteSA')

    def __MatchAmplifierMute(self, match, qualifier):

        MuteState = {
            '1':'On',
            '0':'Off'
        }

        channelSide = {
            '16':'Left',
            '17':'Right'
        }

        value = MuteState[match.group(2).decode()]
        if hasattr(self, 'Amplifier'):
            if self.Amplifier == 'Stereo':
                qualifier = {'L/R': channelSide[match.group(1).decode()]}
                self.WriteStatus('AmplifierMuteSA', value, qualifier)
            elif self.Amplifier == 'Mono':
                self.WriteStatus('AmplifierMuteMA', value, None)
        else:
            self.Error(['Incorrect model'])

    def SetAmplifierPostmixerTrim(self, value, qualifier):

        channelSide = {
            'Left'  : '6',
            'Right' : '7'
        }

        if -12 <= value <= 12 and qualifier['L/R'] in channelSide:
            AmplifierPostmixerTrimCmdString = 'WG6011{0}*{1}AU\r'.format(channelSide[qualifier['L/R']], round(value * 10))
            self.__SetHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierPostmixerTrim')

    def UpdateAmplifierPostmixerTrim(self, value, qualifier):

        channelSide = {
            'Left'  : '6',
            'Right' : '7'
        }

        if qualifier['L/R'] in channelSide:
            channel = channelSide[qualifier['L/R']]
            AmplifierPostmixerTrimCmdString = 'WG6011{0}AU\r'.format(channel)
            self.__UpdateHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierPostmixerTrim')

    def __MatchAmplifierPostmixerTrim(self, match, tag):

        channelSide = {
            '6' : 'Left',
            '7' : 'Right'
        }

        qualifier = {'L/R': channelSide[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('AmplifierPostmixerTrim', value, qualifier)

    def SetAmplifierMuteMA(self, value, qualifier):

        MuteState = {
            'On' :'1',
            'Off':'0'
        }

        if value in MuteState:
            commandString = 'WM60016*{0}AU\r'.format(MuteState[value])
            self.__SetHelper('AmplifierMuteMA', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierMuteMA')

    def UpdateAmplifierMuteMA(self, value, qualifier):

        AmplifierMuteMACmdString = 'WM60016AU\r'
        self.__UpdateHelper('AmplifierMuteMA', AmplifierMuteMACmdString, value, qualifier)

    def SetAnalogAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if -100 <= int(value) <= 0:
            if 1 <= tempOutput <= 4:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    commandString = 'WG6000{0}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('AnalogAttenuation', commandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetAnalogAttenuation')
            else:
                self.Discard('Invalid Command for SetAnalogAttenuation')
        else:
            self.Discard('Invalid Command for SetAnalogAttenuation')

    def UpdateAnalogAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 4:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG6000{0}AU\r'.format(channelValue)
                self.__UpdateHelper('AnalogAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateAnalogAttenuation')
        else:
            self.Discard('Invalid Command for UpdateAnalogAttenuation')

    def __MatchAnalogAttenuation(self, match, tag):

        qualifier = {}
        OutputValue = int(match.group(1).decode())   #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode())/10
        self.WriteStatus('AnalogAttenuation', value, qualifier)

    def SetAnalogMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channelStates = {
            'Left' : 0,
            'Right': 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 4 and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM6000{0}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('AnalogMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetAnalogMute')
        else:
            self.Discard('Invalid Command for SetAnalogMute')

    def UpdateAnalogMute(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= tempOutput <= 4:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM6000{0}AU\r'.format(channelValue)
                self.__UpdateHelper('AnalogMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateAnalogMute')
        else:
            self.Discard('Invalid Command for UpdateAnalogMute')

    def __MatchAnalogMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('AnalogMute', value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill' : '1',
            'Follow' : '2'
        }

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize and value in ValueStateValues:
            AspectRatioCmdString = 'w{0}*{1}ASPR\r\n'.format(tempInput, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            AspectRatioCmdString = 'w{0}ASPR\r\n'.format(tempInput)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        InputStates = {
            '01' : '1',
            '02' : '2',
            '03' : '3',
            '04' : '4',
            '05' : '5',
            '06' : '6',
            '07' : '7',
            '08' : '8',
            '09' : '9',
            '10' : '10'
        }

        ValueStateValues = {
            '1' : 'Fill',
            '2' : 'Follow'
        }

        tempInput = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Input':tempInput})

    def SetAutoImage(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            AutoImageCmdString = '{0}*A'.format(Output)
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')
    def SetDTPAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if -100 <= int(value) <= 0:
            if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    commandString = 'WG600{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('DTPAttenuation', commandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetDTPAttenuation')
            else:
                self.Discard('Invalid Command for SetDTPAttenuation')
        else:
            self.Discard('Invalid Command for SetDTPAttenuation')

    def UpdateDTPAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG600{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('DTPAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateDTPAttenuation')
        else:
            self.Discard('Invalid Command for UpdateDTPAttenuation')

    def __MatchDTPAttenuation(self, match, tag):

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode())/10
        self.WriteStatus('DTPAttenuation', value, qualifier)

    def SetDTPMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max'] and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM600{0:02d}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('DTPMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetDTPMute')
        else:
            self.Discard('Invalid Command for SetDTPMute')

    def UpdateDTPMute(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if self.DTPConstraints['Min'] <= tempOutput <= self.DTPConstraints['Max']:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM600{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('DTPMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateDTPMute')
        else:
            self.Discard('Invalid Command for UpdateDTPMute')

    def __MatchDTPMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

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

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = self.EDIDStates[match.group(2).decode()]
        self.WriteStatus('EDIDAssignment', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Mode 1' : '1X',
            'Mode 2' : '2X',
            'Off'    : '0X'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = ValueStateValues[value]
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):


        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Mode 1',
            '2' : 'Mode 2',
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            FreezeCmdString = '{0}*{1}F'.format(Output, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            FreezeCmdString = '{0}F'.format(Output)
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        OutputStates = {
            '03' : '3',
            '04' : '4',
            '05' : '5',
            '06' : '6',
            '07' : '7',
            '08' : '8'
        }

        ValueStateValues = {
            '01' : 'On',
            '00' : 'Off'
        }

        Output = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Freeze', value, {'Output':Output})

    def SetExpansionPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -100 <= value <= 12:
            if 1 <= tempInput <= 16:
                level = round(value * 10)
                ExpansionPremixerGainCmdString = 'wG{0}*{1:05d}AU\r'.format(tempInput + 50199, level)
                self.__SetHelper('ExpansionPremixerGain', ExpansionPremixerGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetExpansionPremixerGain')
        else:
            self.Discard('Invalid Command for SetExpansionPremixerGain')

    def UpdateExpansionPremixerGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 16:
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
        if 1 <= tempInput <= 16 and value in ValueStateValues:
            ExpansionPremixerMuteCmdString = 'wM{0}*{1}AU\r'.format(tempInput + 50199, ValueStateValues[value])
            self.__SetHelper('ExpansionPremixerMute', ExpansionPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExpansionPremixerMute')

    def UpdateExpansionPremixerMute(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if 1 <= tempInput <= 16:
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

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetGlobalVideoMute(self, value, qualifier):

        GlobalMuteState={
            'Video':'1',
            'Video & Sync':'2',
            'Off':'0'
        }

        if value in GlobalMuteState:
            self.__SetHelper('GlobalVideoMute', '{0}*B'.format(GlobalMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    #####################################################
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
                if value in GroupMuteStateNames:
                    self.WriteStatus(command, GroupMuteStateNames[value], qualifier)
                else:
                    self.Error(['Invalid/unexpected response'])
            elif command in ['GroupMicLineInputGain', 'GroupPremixerGain',
                             'GroupOutputAttenuation', 'GroupMixpoint',
                             'GroupPostmixerTrim', 'GroupPrematrixTrim'
                             ]:
                qualifier = {'Group': group}
                value = int(match.group(2)) / 10
                self.WriteStatus(command, value, qualifier)

    def SetGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if -80 <= int(value) <= 80:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupMicLineInputGain', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupMicLineInputGain'
            else:
                self.Discard('Invalid Command for SetGroupMicLineInputGain')
        else:
            self.Discard('Invalid Command for SetGroupMicLineInputGain')

    def UpdateGroupMicLineInputGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMicLineInputGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMicLineInputGain'
        else:
            self.Discard('Invalid Command for UpdateGroupMicLineInputGain')

    def SetGroupMixpoint(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 12:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupMixpoint', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupMixpoint'
            else:
                self.Discard('Invalid Command for SetGroupMixpoint')
        else:
            self.Discard('Invalid Command for SetGroupMixpoint')

    def UpdateGroupMixpoint(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMixpoint', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for UpdateGroupMixpoint')

    def SetGroupMute(self, value, qualifier):

        MuteState = {
            'On':'1',
            'Off':'0'
        }

        group = qualifier['Group']
        if 1 <= int(group) <= 32 and value in MuteState:
            commandString = 'WD{0}*{1}GRPM\r'.format(group,MuteState[value])
            self.__SetHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMute', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 0:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupOutputAttenuation', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupOutputAttenuation'
            else:
                self.Discard('Invalid Command for SetGroupOutputAttenuation')
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupOutputAttenuation', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupOutputAttenuation'
        else:
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if -100 <= int(value) <= 12:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPremixerGain', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPremixerGain'
            else:
                self.Discard('Invalid Command for SetGroupPremixerGain')
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPremixerGain', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPremixerGain'
        else:
            self.Discard('Invalid Command for UpdateGroupPremixerGain')

    def SetGroupPrematrixTrim(self, value, qualifier):

        group = qualifier['Group']
        if -12 <= int(value) <= 12:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPrematrixTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPrematrixTrim'
            else:
                self.Discard('Invalid Command for SetGroupPrematrixTrim')
        else:
            self.Discard('Invalid Command for SetGroupPrematrixTrim')

    def UpdateGroupPrematrixTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPrematrixTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPrematrixTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPrematrixTrim')

    def SetGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if -12 <= int(value) <= 12:
            if 1 <= int(group) <= 32:
                commandString = 'WD{0}*{1}GRPM\r'.format(group,round(value*10))
                self.__SetHelper('GroupPostmixerTrim', commandString, value, qualifier)
                self.GroupFunction[group] = 'GroupPostmixerTrim'
            else:
                self.Discard('Invalid Command for SetGroupPostmixerTrim')
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        group = qualifier['Group']
        if 1 <= int(group) <= 32:
            commandString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPostmixerTrim', commandString, value, qualifier)
            self.GroupFunction[group] = 'GroupPostmixerTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPostmixerTrim')

    def SetHDMIAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if -100 <= value <= 0:
            if 1 <= tempOutput <= 4:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    commandString = 'WG6020{0}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('HDMIAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetHDMIAttenuation')
        else:
            self.Discard('Invalid Command for SetHDMIAttenuation')

    def UpdateHDMIAttenuation(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= tempOutput <= 4:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG6020{0}AU\r'.format(channelValue)
                self.__UpdateHelper('HDMIAttenuation', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHDMIAttenuation')
        else:
            self.Discard('Invalid Command for UpdateHDMIAttenuation')

    def __MatchHDMIAttenuation(self, match, tag):

        qualifier = {}
        OutputValue = int(match.group(1).decode()) #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode())/10
        self.WriteStatus('HDMIAttenuation', value, qualifier)

    def SetHDMIMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 4 and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM6020{0}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('HDMIMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetHDMIMute')
        else:
            self.Discard('Invalid Command for SetHDMIMute')

    def UpdateHDMIMute(self, value, qualifier):

        channelStates = {
            'Left' : 0,
            'Right': 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= 4:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM6020{0}AU\r'.format(channelValue)
                self.__UpdateHelper('HDMIMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateHDMIMute')
        else:
            self.Discard('Invalid Command for UpdateHDMIMute')

    def __MatchHDMIMute(self, match, tag):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('HDMIMute', value, qualifier)

    def SetInputAudioSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'   : '0',
            'Digital': '1',
            'Analog' : '2'
        }

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize and value in ValueStateValues:
            InputAudioSwitchModeCmdString = 'wI{0}*{1}AFMT\r\n'.format(tempInput, ValueStateValues[value])
            self.__SetHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchMode')

    def UpdateInputAudioSwitchMode(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            InputAudioSwitchModeCmdString = 'wIAFMT\r\n'
            self.__UpdateHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateInputAudioSwitchMode')

    def __MatchInputAudioSwitchMode(self, match, tag):

        InputStates = {
            '01'  : '1',
            '02'  : '2',
            '03'  : '3',
            '04'  : '4',
            '05'  : '5',
            '06'  : '6',
            '07'  : '7',
            '08'  : '8',
            '09'  : '9',
            '10' : '10'
        }

        ValueStateValues = {
            '0' : 'Auto',
            '1' : 'Digital',
            '2' : 'Analog'
        }

        if tag == 'Single':
            tempInput = InputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('InputAudioSwitchMode', value, {'Input':tempInput})
        else:
            tempInput = 0
            for i in match.group(1).decode():
                value = ValueStateValues[i]
                tempInput = tempInput + 1
                self.WriteStatus('InputAudioSwitchMode', value, {'Input':str(tempInput)})

    def SetInputGain(self, value, qualifier):

        formatStates = {
            'Analog'  : 'G',
            'Digital' : 'H'
        }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempInput = int(qualifier['Input'])
        tempFormat = qualifier['Format']
        channel = qualifier['L/R']
        if -18 <= value <= 24:
            if 1 <= tempInput <= self.InputSize:
                if tempFormat in formatStates and channel in channelStates:
                    formatValue = formatStates[tempFormat]
                    level = round(value * 10)
                    channelValue = (tempInput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    InputGainCmdString = 'w{0}{1}*{2:05d}AU\r'.format(formatValue, channelValue + 30000, level)
                    self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetInputGain')
            else:
                self.Discard('Invalid Command for SetInputGain')
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
        if 1 <= tempInput <= self.InputSize:
            if tempFormat in formatStates and channel in channelStates:
                formatValue = formatStates[tempFormat]

                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                InputGainCmdString = 'w{0}{1}AU\r'.format(formatValue, channelValue + 30000)
                self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateInputGain')
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        formatStates = {
            'G': 'Analog',
            'H': 'Digital'
        }

        qualifier = {}
        qualifier['Format'] = formatStates[match.group(1).decode().upper()]
        inputValue = int(match.group(2).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
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
        if 1 <= tempInput <= self.InputSize and value in ValueStateValues:
            if channel in channelStates:
                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                InputMuteCmdString = 'wM{0}*{1}AU\r'.format(channelValue + 30000, ValueStateValues[value])
                self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInputMute')
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
        inputValue = int(match.group(1).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = MuteStateNames[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def UpdateInputFormat(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= self.InputSize:
            InputFormatCmdString = '{0}\x2A\x5C\r'.format(input_)
            self.__UpdateHelper('InputFormat', InputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputFormat')

    def __MatchInputFormat(self, match, tag):

        ValueStateValues = {
            '0' : 'No signal detected',
            '1' : 'DVI RGB 444',
            '2' : 'HDMI RGB 444 Full',
            '3' : 'HDMI RGB 444 Limited',
            '4' : 'HDMI YUV 444 Full',
            '5' : 'HDMI YUV 444 Limited',
            '6' : 'HDMI YUV 422 Full',
            '7' : 'HDMI YUV 422 Limited'
        }

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputFormat', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
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

        InputStates = {
            '01' : '1',
            '02' : '2',
            '03' : '3',
            '04' : '4',
            '05' : '5',
            '06' : '6',
            '07' : '7',
            '08' : '8',
            '09' : '9',
            '10' : '10'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        tempInput = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': tempInput})

    def UpdateInputSignalStatus(self, value, qualifier):

        tempInput = qualifier['Input']
        if 1 <= int(tempInput) <= self.InputSize:
            InputSignalCmdString = '0LS'
            self.__UpdateHelper('InputSignalStatus', InputSignalCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active',
            '0' : 'Not Active'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputVal in signal:
            self.WriteStatus('InputSignalStatus', ValueStateValues[inputVal], {'Input':str(inputNumber)})
            inputNumber += 1

    def SetLogo(self, value, qualifier):

        ValueStateValues = {
            '1'   : '1',
            '2'   : '2',
            '3'   : '3',
            '4'   : '4',
            '5'   : '5',
            '6'   : '6',
            '7'   : '7',
            '8'   : '8',
            '9'   : '9',
            '10'  : '10',
            '11'  : '11',
            '12'  : '12',
            '13'  : '13',
            '14'  : '14',
            '15'  : '15',
            '16'  : '16',
            'Off' : '0'
        }

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            LogoCmdString = 'wE{0}*{1}LOGO\r'.format(Output, ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            LogoCmdString = 'wE{0}LOGO\r'.format(Output)
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):

        OutputStates = {
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8'
        }

        ValueStateValues = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            '5'  : '5',
            '6'  : '6',
            '7'  : '7',
            '8'  : '8',
            '9'  : '9',
            '10' : '10',
            '11' : '11',
            '12' : '12',
            '13' : '13',
            '14' : '14',
            '15' : '15',
            '16' : '16',
            '0'  : 'Off',
            '-1' : 'Off'
        }

        Output = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Logo', value, {'Output':Output})

    def SetLogoAssignment(self, value, qualifier):

        LogoStates = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            '5'  : '5',
            '6'  : '6',
            '7'  : '7',
            '8'  : '8',
            '9'  : '9',
            '10' : '10',
            '11' : '11',
            '12' : '12',
            '13' : '13',
            '14' : '14',
            '15' : '15',
            '16' : '16'
        }

        if value and qualifier['Logo'] in LogoStates:
            Logo = LogoStates[qualifier['Logo']]
            LogoAssignmentString = 'wA{0},{1}LOGO\r\n'.format(Logo, value)
            self.__SetHelper('LogoAssignment', LogoAssignmentString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoAssignment')

    def UpdateLogoAvailability(self, value, qualifier):

        if 1 <= int(qualifier['Logo']) <= 16:
            LogoAvailabilityCmdString = 'wQLOGO\r\n'
            self.__UpdateHelper('LogoAvailability', LogoAvailabilityCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateLogoAvailability')

    def __MatchLogoAvailability(self, match, tag):

        ValueStateValues = {
            '1' : 'Saved',
            '0' : 'Empty'
        }

        Logo = 1
        for i in match.group(1).decode():
            value = ValueStateValues[i]
            self.WriteStatus('LogoAvailability', value, {'Logo':str(Logo)})
            Logo += 1

    def SetLogoKeySetting(self, value, qualifier):

        ValueStateValues = {
            'Disabled'      : '0',
            'Transparency'  : '1',
            'RGB Key'       : '2',
            'Level Key'     : '3',
            'Alpha Key'     : '4'
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize and value in ValueStateValues:
            LogoKeySettingCmdString = 'w{0}*{1}VKEF\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoKeySetting')

    def UpdateLogoKeySetting(self, value, qualifier):

        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize:
            LogoKeySettingCmdString = 'w{0}VKEF\r\n'.format(Output)
            self.__UpdateHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoKeySetting')

    def __MatchLogoKeySetting(self, match, tag):

        ValueStateValues = {
            '0' : 'Disabled',
            '1' : 'Transparency',
            '2' : 'RGB Key',
            '3' : 'Level Key',
            '4' : 'Alpha Key'
        }

        Output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LogoKeySetting', value, {'Output':Output})

    def SetMicLineGain(self, value, qualifier):

        tempInput = int(qualifier['Input'])
        if -18 <= value <= 80:
            if 1 <= tempInput <= 4:
                level = round(value * 10)
                MicLineGainCmdString = 'wG{0}*{1:05d}AU\r\n'.format(tempInput + 39999, level)
                self.__SetHelper('MicLineGain', MicLineGainCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMicLineGain')
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
            'On' :'1',
            'Off':'0'
        }

        MicNum = int(qualifier['Input'])
        if 1 <= MicNum <= 4 and value in ValueStateValues:
            MicNumFix = MicNum - 1
            commandString = 'wM4000{0}*{1}AU\r'.format(MicNumFix,ValueStateValues[value])
            self.__SetHelper('MicLineMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineMute')

    def UpdateMicLineMute(self, value, qualifier):

        MicNum = int(qualifier['Input'])
        if 1 <= MicNum <= 4:
            MicNumFix = MicNum - 1
            commandString = 'wM4000{0}AU\r'.format(MicNumFix)
            self.__UpdateHelper('MicLineMute', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateMicLineMute')

    def __MatchMicLineMute(self, match, tag):

        ValueStateValues = {
            '1':'On',
            '0':'Off'
        }

        MicNumFix = int(match.group(1).decode()) + 1
        qualifier = {'Input' : str(MicNumFix)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicLineMute', value, qualifier)

    def UpdateMicrophoneSignalStatus(self, value, qualifier):

        MicNum = qualifier['Input']
        if 1 <= int(MicNum) <= 4:
            MicNumFix = int(MicNum) - 1
            self.__UpdateHelper('MicrophoneSignalStatus', 'wv4000{0}*1AU\r'.format(MicNumFix), value, qualifier)
            self.__UpdateHelper('MicrophoneSignalStatus', 'wv4000{0}AU\r'.format(MicNumFix), value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateMicrophoneSignalStatus')

    def __MatchMicrophoneSignalStatus(self, match, tag):

        qualifier = {'Input': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode())/10
        self.WriteStatus('MicrophoneSignalStatus', -value, qualifier)

    def SetMixpointGain(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']
        if -100 <= int(value) <= 12:
            if tempInput.startswith('Output') and output.startswith('Output'):
                if tempInput != output:
                    self.Discard('Invalid Command for SetMixpointGain')
                    return

            elif tempInput.startswith('V. Return') and output.startswith('V. Send'):
                if tempInput[-1] == output[-1]:
                    self.Discard('Invalid Command for SetMixpointGain')
                    return

            commandString = 'WG2{0}{1}*{2}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output],round(value*10))
            self.__SetHelper('MixpointGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']
        if tempInput.startswith('Post Matrix') and output.startswith('Output'):
            if tempInput != output:
                self.Discard('Invalid Command for UpdateMixpointGain')
                return

        elif tempInput.startswith('V. Return') and output.startswith('V. Send'):
            if tempInput[-1] == output[-1]:
                self.Discard('Invalid Command for UpdateMixpointGain')
                return

        commandString = 'WG2{0}{1}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output])
        self.__UpdateHelper('MixpointGain', commandString, value, qualifier)

    def __MatchMixpointGain(self, match, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Output 5 Left', 'Output 5 Right', 'Output 6 Left', 'Output 6 Right', 'Output 7 Left', 'Output 7 Right', 'Output 8 Left', 'Output 8 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8', 'Exp. 9', 'Exp. 10', 'Exp. 11',
                'Exp. 12', 'Exp. 13', 'Exp. 14', 'Exp. 15', 'Exp. 16')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left','Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'Output 5 Left', 'Output 5 Right', 'Output 6 Left', 'Output 6 Right', 'Output 7 Left','Output 7 Right', 'Output 8 Left', 'Output 8 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        tempInput = rows[int(match.group(1).decode())]
        Output = columns[int(match.group(2).decode())]

        qualifier = {'Input': tempInput, 'Output': Output}
        value = int(match.group(3).decode()) / 10
        self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        ValueStates = {
            'On': 1,
            'Off': 0
        }

        tempInput = qualifier['Input']
        output = qualifier['Output']
        if tempInput.startswith('Post Matrix') and output.startswith('Output'):
            if tempInput != output:
                self.Discard('Invalid Command for SetMixpointMute')
                return

        elif tempInput.startswith('Virtual Return') and output.startswith('Virtual Send'):
            if tempInput[-1] == output[-1]:
                self.Discard('Invalid Command for SetMixpointMute')
                return

        if value in ValueStates:
            commandString = 'WM2{0}{1}*{2}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output],ValueStates[value])
            self.__SetHelper('MixpointMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointMute')

    def UpdateMixpointMute(self, value, qualifier):

        tempInput = qualifier['Input']
        output = qualifier['Output']
        if tempInput.startswith('Post Matrix') and output.startswith('Output'):
            if tempInput != output:
                self.Discard('Invalid Command for UpdateMixpointMute')
                return

        elif tempInput.startswith('Virtual Return') and output.startswith('Virtual Send'):
            if tempInput[-1] == output[-1]:
                self.Discard('Invalid Command for UpdateMixpointMute')
                return
        commandString = 'WM2{0}{1}AU\r'.format(self.MixPointInputs[tempInput], self.MixPointOutputs[output])
        self.__UpdateHelper('MixpointMute', commandString, value, qualifier)

    def __MatchMixpointMute(self, match, qualifier):

        rows = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                'Output 5 Left', 'Output 5 Right', 'Output 6 Left', 'Output 6 Right', 'Output 7 Left', 'Output 7 Right', 'Output 8 Left', 'Output 8 Right',
                'Mic 1', 'Mic 2', 'Mic 3', 'Mic 4', 'V. Return A', 'V. Return B', 'V. Return C', 'V. Return D', 'V. Return E', 'V. Return F', 'V. Return G', 'V. Return H',
                'Exp. 1', 'Exp. 2', 'Exp. 3', 'Exp. 4', 'Exp. 5', 'Exp. 6', 'Exp. 7', 'Exp. 8', 'Exp. 9', 'Exp. 10', 'Exp. 11',
                'Exp. 12', 'Exp. 13', 'Exp. 14', 'Exp. 15', 'Exp. 16')

        columns = ('Output 1 Left', 'Output 1 Right', 'Output 2 Left', 'Output 2 Right', 'Output 3 Left', 'Output 3 Right', 'Output 4 Left', 'Output 4 Right',
                   'Output 5 Left', 'Output 5 Right', 'Output 6 Left', 'Output 6 Right', 'Output 7 Left', 'Output 7 Right', 'Output 8 Left', 'Output 8 Right',
                   'V. Send A', 'V. Send B', 'V. Send C', 'V. Send D', 'V. Send E', 'V. Send F', 'V. Send G', 'V. Send H')

        MuteState = {
            '1':'On',
            '0':'Off'        }

        tempInput = rows[int(match.group(1).decode())]
        Output = columns[int(match.group(2).decode())]

        qualifier = {'Input': tempInput, 'Output': Output}
        value = MuteState[match.group(3).decode()]
        self.WriteStatus('MixpointMute', value, qualifier)

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input': 'NI',
            'Output': 'NO'
        }

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 0 <= len(name) <= 16 and qualifier['Type'] in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[qualifier['Type']])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
            if qualifier['Type'] == 'Input': #only write the name if it's for input
                for x in range(1, self.InputSize + 1):
                    audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Audio'}) # get audio input
                    videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Video'}) # get video input
                    if audioVal == int(number):
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Audio'})
                    if videoVal == int(number):
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Video'})
                    if audioVal == videoVal == int(number): # if video input is the same as audio input
                        self.WriteStatus('OutputTieStatusName', name, {'Output': str(x), 'Tie Type': 'Audio/Video'}) # write AV name
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')
    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        number = match.group(2).decode()
        value = match.group(3).decode()
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        if type_ == 'Input': # only write the name if type is input
            for x in range(1, self.InputSize + 1):
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Audio'}) # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': str(x), 'Tie Type': 'Video'}) # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': str(x), 'Tie Type': 'Audio/Video'})

    def SetRefreshMatrixIONames(self, value, qualifier):

        self.UpdateMatrixIONames( None, None)

    def UpdateMatrixIONames(self, value, qualifier):
        prevTime = 0
        for i in range(1, self.InputSize+1):
            ctime = time.monotonic()
            while True:
                if ctime - prevTime > 0.2:
                    break
                else:
                    ctime = time.monotonic()
            self.Send('w{0}NI\r'.format(i))
            prevTime = ctime
        prevTime = 0
        for i in range(1, self.OutputSize+1):
            ctime = time.monotonic()
            while True:
                if ctime - prevTime > 0.2:
                    break
                else:
                    ctime = time.monotonic()
            self.Send('w{0}NO\r'.format(i))
            prevTime = ctime
    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeStates = {
            'Audio'       : '$',
            'Audio/Video' : '!',
            'Video'       : '%'
        }
        tempInput = qualifier['Input']
        Output = qualifier['Output']

        if 0 <= int(tempInput) <= self.InputSize and qualifier['Tie Type'] in TieTypeStates:
            Tie = TieTypeStates[qualifier['Tie Type']]
            if Output == 'All':
                MatrixTieCommandCmdString = '{0}*{1}\r\n'.format(tempInput,  Tie)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            elif 1 <= int(Output) <= self.OutputSize:
                MatrixTieCommandCmdString = '{0}*{1}{2}\r\n'.format(tempInput,  Output, Tie)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')
    def SetOutputAudioSelect(self, value, qualifier):

        ValueStateValues = {
            'Embedded Audio': '1',
            'No Audio'      : '2',
            'Original HDMI' : '0'
        }

        Output = qualifier['Output']
        if 1 <= int(Output) <= self.OutputSize and value in ValueStateValues:
            OutputAudioSelectCmdString = 'wO{0}*{1}AFMT\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAudioSelect')

    def UpdateOutputAudioSelect(self, value, qualifier):

        if 1 <= int(qualifier['Output']) <= self.OutputSize:
            OutputAudioSelectCmdString = 'wOAFMT\r\n'
            self.__UpdateHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Device Is Busy for UpdateOutputAudioSelect')

    def __MatchOutputAudioSelect(self, match, tag):

        OutputStates = {
            '01' : '1',
            '02' : '2',
            '03' : '3',
            '04' : '4',
            '05' : '5',
            '06' : '6',
            '07' : '7',
            '08' : '8'
        }

        ValueStateValues = {
            '1' : 'Embedded Audio',
            '2' : 'No Audio',
            '0' : 'Original HDMI'
        }

        if tag == 'Single':
            Output = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OutputAudioSelect', value, {'Output':Output})
        else:
            Output = 0
            for i in match.group(1).decode():
                value = ValueStateValues[i]
                Output += 1
                self.WriteStatus('OutputAudioSelect', value, {'Output':str(Output)})

    def SetHDCPOutputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On'   : '1',
            'Auto' : '0'
        }

        if value in ValueStateValues and qualifier['Output'] in self.OutputStates:
            Output = self.OutputStates[qualifier['Output']]
            OutputHDCPAuthorizationCmdString = 'wS{0}*{1}HDCP\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('HDCPOutputAuthorization', OutputHDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPOutputAuthorization')

    def UpdateHDCPOutputAuthorization(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            Output = self.OutputStates[qualifier['Output']]
            OutputHDCPAuthorizationCmdString = 'wS{0}HDCP\r\n'.format(Output)
            self.__UpdateHelper('HDCPOutputAuthorization', OutputHDCPAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputAuthorization')

    def __MatchHDCPOutputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Auto'
        }

        Output = self.OutputStates[match.group(1).decode().upper()]
        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('HDCPOutputAuthorization', value, {'Output':Output})

    def UpdateHDCPInputStatus(self, value, qualifier):


        if 1 <= int(qualifier['Input']) <= self.InputSize:
            HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No Source Connected',
            '1' : 'HDCP Content',
            '2' : 'No HDCP Content'
        }

        qualifier = {'Input': str(int(match.group(1).decode()))}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):


        if qualifier['Output'] in self.OutputStates:
            HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'No monitor connected',
            '1' : 'Monitor connected, HDCP not supported',
            '2' : 'Monitor connected, not encrypted',
            '3' : 'Monitor connected, currently encrypted'
        }

        qualifier = {'Output': self.OutputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetOutputPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']
        if -12 <= value <= 12:
            if 1 <= output <= self.OutputSize:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (output * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1
                    OutputPostmixerTrimCmdString = 'wG601{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('OutputPostmixerTrim', OutputPostmixerTrimCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetOutputPostmixerTrim')
            else:
                self.Discard('Invalid Command for SetOutputPostmixerTrim')
        else:
            self.Discard('Invalid Command for SetOutputPostmixerTrim')

    def UpdateOutputPostmixerTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        output = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= output <= self.OutputSize:
            if channel in channelStates:
                channelValue = (output * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1
                OutputPostmixerTrimCmdString = 'wG601{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('OutputPostmixerTrim', OutputPostmixerTrimCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdateOutputPostmixerTrim')
        else:
            self.Discard('Invalid Command for UpdateOutputPostmixerTrim')

    def __MatchOutputPostmixerTrim(self, match, tag):

        qualifier = {}
        outputValue = int(match.group(1).decode())
        if outputValue % 2 == 0:  # Even
            channelValue = int((outputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((outputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2)) / 10
        self.WriteStatus('OutputPostmixerTrim', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)'            : '10',
            '800x600 (60Hz)'            : '11',
            '1024x768 (60Hz)'           : '12',
            '1280x768 (60Hz)'           : '13',
            '1280x800 (60Hz)'           : '14',
            '1280x1024 (60Hz)'          : '15',
            '1360x768 (60Hz)'           : '16',
            '1366x768 (60Hz)'           : '17',
            '1440x900 (60Hz)'           : '18',
            '1400x1050 (60Hz)'          : '19',
            '1600x900 (60Hz)'           : '20',
            '1680x1050 (60Hz)'          : '21',
            '1600x1200 (60Hz)'          : '22',
            '1920x1200 (60Hz)'          : '23',
            '480p (59.94Hz)'            : '24',
            '480p (60Hz)'               : '25',
            '576p (50Hz)'               : '26',
            '720p (23.98Hz)'            : '27',
            '720p (24Hz)'               : '28',
            '720p (25Hz)'               : '29',
            '720p (29.97Hz)'            : '30',
            '720p (30Hz)'               : '31',
            '720p (50Hz)'               : '32',
            '720p (59.94Hz)'            : '33',
            '720p (60Hz)'               : '34',
            '1080i (50Hz)'              : '35',
            '1080i (59.94Hz)'           : '36',
            '1080i (60Hz)'              : '37',
            '1080p (23.98Hz)'           : '38',
            '1080p (24Hz)'              : '39',
            '1080p (25Hz)'              : '40',
            '1080p (29.97Hz)'           : '41',
            '1080p (30Hz)'              : '42',
            '1080p (50Hz)'              : '43',
            '1080p (59.94Hz)'           : '44',
            '1080p (60Hz)'              : '45',
            '2048x1080 2K (23.98Hz)'    : '46',
            '2048x1080 2K (24Hz)'       : '47',
            '2048x1080 2K (25Hz)'       : '48',
            '2048x1080 2K (29.97Hz)'    : '49',
            '2048x1080 2K (30Hz)'       : '50',
            '2048x1080 2K (50Hz)'       : '51',
            '2048x1080 2K (59.94Hz)'    : '52',
            '2048x1080 2K (60Hz)'       : '53',
            '1920x2160 (23.98Hz)'       : '54',
            '1920x2160 (24Hz)'          : '55',
            '1920x2160 (25Hz)'          : '56',
            '1920x2160 (29.97Hz)'       : '57',
            '1920x2160 (30Hz)'          : '58',
            '1920x2160 (50Hz)'          : '59',
            '1920x2160 (59.94Hz)'       : '60',
            '1920x2160 (60Hz)'          : '61',
            '1920x2400 (30Hz)'          : '62',
            '1920x2400 (60Hz)'          : '63',
            '2048x1200 (60Hz)'          : '64',
            '2048x1536 (60Hz)'          : '65',
            '2048x2160 (23.98Hz)'       : '66',
            '2048x2160 (24Hz)'          : '67',
            '2048x2160 (25Hz)'          : '68',
            '2048x2160 (29.97Hz)'       : '69',
            '2048x2160 (30Hz)'          : '70',
            '2048x2160 (50Hz)'          : '71',
            '2048x2160 (59.94Hz)'       : '72',
            '2048x2160 (60Hz)'          : '73',
            '2048x2400 (30Hz)'          : '74',
            '2560x1080 (60Hz)'          : '76',
            '2560x1440 (60Hz)'          : '77',
            '2560x1600 (60Hz)'          : '78',
            '3840x2160 (23.98Hz)'       : '79',
            '3840x2160 (24Hz)'          : '80',
            '3840x2160 (25Hz)'          : '81',
            '3840x2160 (29.97Hz)'       : '82',
            '3840x2160 (30Hz)'          : '83',
            '3840x2400 (30Hz)'          : '87',
            '3840x2400 (60Hz)'          : '88',
            '4096x2160 (23.98Hz)'       : '89',
            '4096x2160 (24Hz)'          : '90',
            '4096x2160 (25Hz)'          : '91',
            '4096x2160 (29.97Hz)'       : '92',
            '4096x2160 (30Hz)'          : '93',
        }

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and value in ValueStateValues:
            OutputResolutionCmdString = 'w{0}*{1}RATE\r\n'.format(Output, ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max']:
            OutputResolutionCmdString = 'w{0}RATE\r\n'.format(Output)
            self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, tag):

        OutputStates = {
            '03' : '3',
            '04' : '4',
            '05' : '5',
            '06' : '6',
            '07' : '7',
            '08' : '8'
        }

        ValueStateValues = {
            '10' : '640x480 (60Hz)',
            '11' : '800x600 (60Hz)',
            '12' : '1024x768 (60Hz)',
            '13' : '1280x768 (60Hz)',
            '14' : '1280x800 (60Hz)',
            '15' : '1280x1024 (60Hz)',
            '16' : '1360x768 (60Hz)',
            '17' : '1366x768 (60Hz)',
            '18' : '1440x900 (60Hz)',
            '19' : '1400x1050 (60Hz)',
            '20' : '1600x900 (60Hz)',
            '21' : '1680x1050 (60Hz)',
            '22' : '1600x1200 (60Hz)',
            '23' : '1920x1200 (60Hz)',
            '24' : '480p (59.94Hz)',
            '25' : '480p (60Hz)',
            '26' : '576p (50Hz)',
            '27' : '720p (23.98Hz)',
            '28' : '720p (24Hz)',
            '29' : '720p (25Hz)',
            '30' : '720p (29.97Hz)',
            '31' : '720p (30Hz)',
            '32' : '720p (50Hz)',
            '33' : '720p (59.94Hz)',
            '34' : '720p (60Hz)',
            '35' : '1080i (50Hz)',
            '36' : '1080i (59.94Hz)',
            '37' : '1080i (60Hz)',
            '38' : '1080p (23.98Hz)',
            '39' : '1080p (24Hz)',
            '40' : '1080p (25Hz)',
            '41' : '1080p (29.97Hz)',
            '42' : '1080p (30Hz)',
            '43' : '1080p (50Hz)',
            '44' : '1080p (59.94Hz)',
            '45' : '1080p (60Hz)',
            '46' : '2048x1080 2K (23.98Hz)',
            '47' : '2048x1080 2K (24Hz)',
            '48' : '2048x1080 2K (25Hz)',
            '49' : '2048x1080 2K (29.97Hz)',
            '50' : '2048x1080 2K (30Hz)',
            '51' : '2048x1080 2K (50Hz)',
            '52' : '2048x1080 2K (59.94Hz)',
            '53' : '2048x1080 2K (60Hz)',
            '54' : '1920x2160 (23.98Hz)',
            '55' : '1920x2160 (24Hz)',
            '56' : '1920x2160 (25Hz)',
            '57' : '1920x2160 (29.97Hz)',
            '58' : '1920x2160 (30Hz)',
            '59' : '1920x2160 (50Hz)',
            '60' : '1920x2160 (59.94Hz)',
            '61' : '1920x2160 (60Hz)',
            '62' : '1920x2400 (30Hz)',
            '63' : '1920x2400 (60Hz)',
            '64' : '2048x1200 (60Hz)',
            '65' : '2048x1536 (60Hz)',
            '66' : '2048x2160 (23.98Hz)',
            '67' : '2048x2160 (24Hz)',
            '68' : '2048x2160 (25Hz)',
            '69' : '2048x2160 (29.97Hz)',
            '70' : '2048x2160 (30Hz)',
            '71' : '2048x2160 (50Hz)',
            '72' : '2048x2160 (59.94Hz)',
            '73' : '2048x2160 (60Hz)',
            '74' : '2048x2400 (30Hz)',
            '75' : '2048x2400 (60Hz)',
            '76' : '2560x1080 (60Hz)',
            '77' : '2560x1440 (60Hz)',
            '78' : '2560x1600 (60Hz)',
            '79' : '3840x2160 (23.98Hz)',
            '80' : '3840x2160 (24Hz)',
            '81' : '3840x2160 (25Hz)',
            '82' : '3840x2160 (29.97Hz)',
            '83' : '3840x2160 (30Hz)',
            '84' : '3840x2160 (50Hz)',
            '85' : '3840x2160 (59.94Hz)',
            '86' : '3840x2160 (60Hz)',
            '87' : '3840x2400 (30Hz)',
            '88' : '3840x2400 (60Hz)',
            '89' : '4096x2160 (23.98Hz)',
            '90' : '4096x2160 (24Hz)',
            '91' : '4096x2160 (25Hz)',
            '92' : '4096x2160 (29.97Hz)',
            '93' : '4096x2160 (30Hz)'
        }

        Output = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputResolution', value, {'Output':Output})

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
                current_tie = self.matrix_tie_status[i][output-1]
                if i != input_-1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output-1] = 'Untied'
                elif i == input_-1:
                    self.matrix_tie_status[i][output-1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_-1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output-1] = tietype
                elif input_ == 0 or i != input_-1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output-1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = opTag

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
                    if input_ == new_input-1:
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
                    if input_ == new_input-1:
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
            'On'  : '1',
            'Off' : '0'
        }

        if value in ValueStateValues and qualifier['Input'] in InputStates:
            PhantomPowerCmdString = 'wZ4000{0}*{1}AU\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
            self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhantomPower')

    def UpdatePhantomPower(self, value, qualifier):

        InputStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3'
        }

        if qualifier['Input'] in InputStates:
            PhantomPowerCmdString = 'wZ4000{0}AU\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePhantomPower')

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

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PhantomPower', value, {'Input' : InputStates[match.group(1).decode()]})

    def SetPrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempInput = int(qualifier['Input'])
        if -12 <= value <= 12:
            if 1 <= tempInput <= self.InputSize:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempInput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    PrematrixTrimCmdString = 'wG{0}*{1}AU\r'.format(channelValue + 30100, level)
                    self.__SetHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetPrematrixTrim')
            else:
                self.Discard('Invalid Command for SetPrematrixTrim')
        else:
            self.Discard('Invalid Command for SetPrematrixTrim')

    def UpdatePrematrixTrim(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempInput = int(qualifier['Input'])
        channel = qualifier['L/R']
        if 1 <= tempInput <= self.InputSize:
            if channel in channelStates:
                channelValue = (tempInput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1
                PrematrixTrimCmdString = 'wG{0}AU\r'.format(channelValue + 30100)
                self.__UpdateHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePrematrixTrim')
        else:
            self.Discard('Invalid Command for UpdatePrematrixTrim')

    def __MatchPrematrixTrim(self, match, tag):

        qualifier = {}
        inputValue = int(match.group(1).decode())  # Even
        if inputValue % 2 == 0:
            channelValue = int((inputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:  # Odd
            channelValue = int((inputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Input'] = str(channelValue)

        value = int(match.group(2).decode()) / 10
        self.WriteStatus('PrematrixTrim', value, qualifier)

    def SetPostMatrixGain(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if -100 <= int(value) <= 12:
            if 1 <= tempOutput <= self.OutputSize:
                if channel in channelStates:
                    level = round(value * 10)
                    channelValue = (tempOutput * 2) - 2
                    if channel == 'Right':
                        channelValue = channelValue + 1

                    PostMatrixGainCmdString = 'WG500{0:02d}*{1}AU\r'.format(channelValue, level)
                    self.__SetHelper('PostMatrixGain', PostMatrixGainCmdString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetPostMatrixGain')
            else:
                self.Discard('Invalid Command for SetPostMatrixGain')
        else:
            self.Discard('Invalid Command for SetPostMatrixGain')

    def UpdatePostMatrixGain(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        tempOutput = int(qualifier['Output'])
        channel = qualifier['L/R']
        if 1 <= tempOutput <= self.OutputSize:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WG500{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('PostMatrixGain', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePostMatrixGain')
        else:
            self.Discard('Invalid Command for UpdatePostMatrixGain')

    def __MatchPostMatrixGain(self, match, qualifier):

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = int(match.group(2).decode()) / 10
        self.WriteStatus('PostMatrixGain', value, qualifier)

    def SetPostMatrixMute(self, value, qualifier):

        MuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= self.OutputSize and value in MuteState:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM500{0:02d}*{1}AU\r'.format(channelValue, MuteState[value])
                self.__SetHelper('PostMatrixMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPostMatrixMute')
        else:
            self.Discard('Invalid Command for SetPostMatrixMute')

    def UpdatePostMatrixMute(self, value, qualifier):

        channelStates = {
            'Left'  : 0,
            'Right' : 1
        }

        channel = qualifier['L/R']
        tempOutput = int(qualifier['Output'])
        if 1 <= tempOutput <= self.OutputSize:
            if channel in channelStates:
                channelValue = (tempOutput * 2) - 2
                if channel == 'Right':
                    channelValue = channelValue + 1

                commandString = 'WM500{0:02d}AU\r'.format(channelValue)
                self.__UpdateHelper('PostMatrixMute', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for UpdatePostMatrixMute')
        else:
            self.Discard('Invalid Command for UpdatePostMatrixMute')

    def __MatchPostMatrixMute(self, match, qualifier):

        MuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        OutputValue = int(match.group(1).decode())  #Even
        if OutputValue % 2 == 0:
            channelValue = int((OutputValue + 2) / 2)
            qualifier['L/R'] = 'Left'
        else:   #Odd
            channelValue = int((OutputValue + 1) / 2)
            qualifier['L/R'] = 'Right'
        qualifier['Output'] = str(channelValue)

        value = MuteState[match.group(2).decode()]
        self.WriteStatus('PostMatrixMute', value, qualifier)

    def SetPremixerGain(self, value, qualifier):

        tempInput = (int(qualifier['Input'])-1)
        if -100 <= int(value) <= 12:
            if 1 <= int(qualifier['Input']) <= 4:
                commandString = 'WG4010{0}*{1}AU\r'.format(tempInput,round(value*10))
                self.__SetHelper('PremixerGain', commandString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPremixerGain')
        else:
            self.Discard('Invalid Command for SetPremixerGain')

    def UpdatePremixerGain(self, value, qualifier):

        tempInput = (int(qualifier['Input'])-1)
        if 1 <= int(qualifier['Input']) <= 4:
            commandString = 'WG4010{0}AU\r'.format(tempInput)
            self.__UpdateHelper('PremixerGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerGain')

    def __MatchPremixerGain(self, match, qualifier):

        InputNum = {
            '0':'1',
            '1':'2',
            '2':'3',
            '3':'4'
        }

        qualifier = {'Input': InputNum[match.group(1).decode()]}
        value = int(match.group(2))/10
        self.WriteStatus('PremixerGain', value, qualifier)

    def SetPremixerMute(self, value, qualifier):

        MicInputStates = {
            '1' : '0',
            '2' : '1',
            '3' : '2',
            '4' : '3'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        tempInput = qualifier['Input']
        if tempInput in ['1', '2', '3', '4'] and value in ValueStateValues:
            PreMixMuteCmdString = 'WM4010{0}*{1}AU\r\n'.format(MicInputStates[tempInput], ValueStateValues[value])
            self.__SetHelper('PremixerMute', PreMixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPremixerMute')

    def UpdatePremixerMute(self, value, qualifier):

        MicInputStates = {
            '1' : '0',
            '2' : '1',
            '3' : '2',
            '4' : '3'
        }

        tempInput = qualifier['Input']
        if tempInput in ['1', '2', '3', '4']:
            PreMixMuteCmdString = 'WM4010{0}AU\r'.format(MicInputStates[tempInput])
            self.__UpdateHelper('PremixerMute', PreMixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePremixerMute')

    def __MatchPremixerMute(self, match, tag):

        MicInputStates = {
            '0' : '1',
            '1' : '2',
            '2' : '3',
            '3' : '4'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {'Input': MicInputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PremixerMute', value, qualifier)

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)
    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'S'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = round(float(match.group(1).decode()))
        self.WriteStatus('Temperature', value, None)

    def SetScalerPresetRecall(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and 1 <= int(value) <= 128:
            ScalerPresetRecallCmdString = '2*{0}*{1}.\r\n'.format(Output, value)
            self.__SetHelper('ScalerPresetRecall', ScalerPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetRecall')
    def SetScalerPresetSave(self, value, qualifier):

        Output = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(Output) <= self.ScaledOutputConstraints['Max'] and 1 <= int(value) <= 128:
            ScalerPresetSaveCmdString = '2*{0}*{1},\r\n'.format(Output, value)
            self.__SetHelper('ScalerPresetSave', ScalerPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetSave')
    def SetTestPattern(self, value, qualifier):

        TestPattern = {
            'Off':'0',
            'Crop':'1',
            'Alternating Pixels':'2',
            'Crosshatch':'3',
            'Color Bars':'4',
            'Grayscale':'5',
            'Blue Mode':'6'
        }

        OutputNum = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(OutputNum) <= self.ScaledOutputConstraints['Max'] and value in TestPattern:
            TestPatternCMDString = 'W{0}*{1}TEST\r'.format(OutputNum,TestPattern[value])
            self.__SetHelper('TestPattern', TestPatternCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        OutputNum = qualifier['Output']
        if self.ScaledOutputConstraints['Min'] <= int(OutputNum) <= self.ScaledOutputConstraints['Max']:
            UpdateCMDString = 'W{0}TEST\r'.format(OutputNum)
            self.__UpdateHelper('TestPattern', UpdateCMDString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTestPattern')

    def __MatchTestPattern(self, match, qualifier):

        TestPattern={
            '0':'Off',
            '1':'Crop',
            '2':'Alternating Pixels',
            '3':'Crosshatch',
            '4':'Color Bars',
            '5':'Grayscale',
            '6':'Blue Mode'
        }

        qualifier = {'Output': str(int(match.group(1).decode()))}
        value = TestPattern[str(int(match.group(2).decode()))]
        self.WriteStatus('TestPattern', value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video'         : '1',
            'Video & Sync'  : '2',
            'Off'           : '0'
        }

        Output = qualifier['Output']
        if value in ValueStateValues and qualifier['Output'] in self.OutputStates:
            if Output == 'All':
                VideoMuteCmdString = '{0}*B'.format(ValueStateValues[value])
            else:
                VideoMuteCmdString = '{0}*{1}B'.format(self.OutputStates[Output], ValueStateValues[value])

            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        Output = qualifier['Output']
        if Output != 'All' and qualifier['Output'] in self.OutputStates:
            VideoMuteCmdString = '{0}B'.format(self.OutputStates[Output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'Video',
            '2' : 'Video & Sync',
            '0' : 'Off'
        }

        Output = self.OutputStates[match.group(1).decode().upper()]
        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('VideoMute', value, {'Output':Output})

    def SetVirtualReturnGain(self, value, qualifier):

        ChannelTranslation = {
            'A':'0',
            'B':'1',
            'C':'2',
            'D':'3',
            'E':'4',
            'F':'5',
            'G':'6',
            'H':'7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        channel = qualifier['Input']
        if channel in VirtualChannels and -100 <= value <= 12:
            level = round(value*10)
            ChannelValue = ChannelTranslation[channel]
            commandString = 'WG5010{0}*{1}AU\r\n'.format(ChannelValue, level)
            self.__SetHelper('VirtualReturnGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnGain')

    def UpdateVirtualReturnGain(self, value, qualifier):

        ChannelTranslation = {
            'A':'0',
            'B':'1',
            'C':'2',
            'D':'3',
            'E':'4',
            'F':'5',
            'G':'6',
            'H':'7',
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
            '0':'A',
            '1':'B',
            '2':'C',
            '3':'D',
            '4':'E',
            '5':'F',
            '6':'G',
            '7':'H',
        }

        channel = ChannelRETranslation[match.group(1).decode()]
        qualifier = {'Input' : channel}
        value = int(match.group(2).decode())/10
        self.WriteStatus('VirtualReturnGain', value, qualifier)

    def SetVirtualReturnMute(self, value, qualifier):

        ChannelTranslation = {
            'A':'0',
            'B':'1',
            'C':'2',
            'D':'3',
            'E':'4',
            'F':'5',
            'G':'6',
            'H':'7',
        }

        VirtualChannels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        MuteStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = qualifier['Input']
        if channel in VirtualChannels and value in MuteStateValues:
            commandString = 'WM5010{0}*{1}AU\r\n'.format(ChannelTranslation[channel], MuteStateValues[value])
            self.__SetHelper('VirtualReturnMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualReturnMute')

    def UpdateVirtualReturnMute(self, value, qualifier):

        ChannelTranslation = {
            'A':'0',
            'B':'1',
            'C':'2',
            'D':'3',
            'E':'4',
            'F':'5',
            'G':'6',
            'H':'7',
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
            '1' : 'On',
            '0' : 'Off'
        }

        ChannelRETranslation = {
            '0':'A',
            '1':'B',
            '2':'C',
            '3':'D',
            '4':'E',
            '5':'F',
            '6':'G',
            '7':'H',
        }

        qualifier = {'Input' : ChannelRETranslation[match.group(1).decode()]}
        value =  MuteStateNames[match.group(2).decode()]
        self.WriteStatus('VirtualReturnMute', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        elif self.VerboseDisabled:
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
        elif self.EchoDisabled and 'Serial' not in self.ConnectionType:
            @Wait(1)
            def SendEcho():
                self.Send('w0echo\r\n')
        else:
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
            '01' : 'Invalid input channel number (out of range)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number (out of range)',
            '12' : 'Invalid output number (out of range)',
            '13' : 'Invalid value (out of range)',
            '14' : 'Invalid command for this configuration',
            '22' : 'Busy',
            '24' : 'Privileges violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found',
            '33' : 'Bad file type or size (for logo assignment)'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: '+ match.group(0).decode().strip()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.EchoDisabled = True
        self.VerboseDisabled = True


    def extr_15_1691_108(self):

        self.InputSize = 10
        self.OutputSize = 8

        self.DTPConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.ScaledOutputConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.EDIDStates	= {
            '1'  : 'Output 1',
            '2'  : 'Output 2',
            '3'  : 'Output 3',
            '4'  : 'Output 4',
            '5'  : 'Output 5A',
            '6'  : 'Output 5B',
            '7'  : 'Output 6A',
            '8'  : 'Output 6B',
            '9'  : 'Output 7',
            '10' : 'Output 8',
            '11' : '1024x768 @ 50Hz',
            '12' : '1024x768 @ 60Hz',
            '13' : '1280x720 @ 50Hz',
            '14' : '1280x720 @ 60Hz',
            '15' : '1280x768 @ 50Hz',
            '16' : '1280x768 @ 60Hz',
            '17' : '1280x800 @ 50Hz',
            '18' : '1280x800 @ 60Hz',
            '19' : '1280x1024 @ 50Hz',
            '20' : '1280x1024 @ 60Hz',
            '21' : '1360x768 @ 50Hz',
            '22' : '1360x768 @ 60Hz',
            '23' : '1366x768 @ 50Hz',
            '24' : '1366x768 @ 60Hz',
            '25' : '1400x1050 @ 50Hz',
            '26' : '1400x1050 @ 60Hz',
            '27' : '1440x900 @ 50Hz',
            '28' : '1440x900 @ 60Hz',
            '29' : '1600x900 @ 50Hz',
            '30' : '1600x900 @ 60Hz',
            '31' : '1600x1200 @ 50Hz',
            '32' : '1600x1200 @ 60Hz',
            '33' : '1680x1050 @ 50Hz',
            '34' : '1680x1050 @ 60Hz',
            '35' : '1920x1080 @ 50Hz',
            '36' : '1920x1080 @ 60Hz',
            '37' : '1920x1200 @ 50Hz',
            '38' : '1920x1200 @ 60Hz',
            '39' : '2048x1080 @ 50Hz',
            '40' : '2048x1080 @ 60Hz',
            '41' : '480p 2_Ch Audio @ 60Hz',
            '42' : '576p 2_Ch Audio @ 50Hz',
            '43' : '720p 2_Ch Audio @ 50Hz',
            '44' : '720p 2_Ch Audio @ 60Hz',
            '45' : '720p Multi_Ch Audio @ 50Hz',
            '46' : '720p Multi_Ch Audio @ 60Hz',
            '47' : '1080i 2_Ch Audio @ 50Hz',
            '48' : '1080i 2_Ch Audio @ 60Hz',
            '49' : '1080i Multi_Ch Audio @ 50Hz',
            '50' : '1080i Multi_Ch Audio @ 60Hz',
            '51' : '1080p 2_Ch Audio @ 50Hz',
            '52' : '1080p 2_Ch Audio @ 60Hz',
            '53' : '1080p Multi_Ch Audio @ 50Hz',
            '54' : '1080p Multi_Ch Audio @ 60Hz',
            '55' : '3840x2160 2_Ch Audio @ 30Hz',
            '56' : '3840x2160 Multi_Ch Audio @ 30Hz',
            '57' : 'User Assigned 1',
            '58' : 'User Assigned 2',
            '59' : 'User Assigned 3',
            '60' : 'User Assigned 4',
            '61' : 'User Assigned 5',
            '62' : 'User Assigned 6',
            '63' : 'User Assigned 7',
            '64' : 'User Assigned 8',
            '65' : 'User Assigned 9',
            '66' : 'User Assigned 10'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left'  : '12',
            'Output 7 Right' : '13',
            'Output 8 Left'  : '14',
            'Output 8 Right' : '15',
            'Mic 1': '16',
            'Mic 2': '17',
            'Mic 3': '18',
            'Mic 4': '19',
            'V. Return A': '20',
            'V. Return B': '21',
            'V. Return C': '22',
            'V. Return D': '23',
            'V. Return E': '24',
            'V. Return F': '25',
            'V. Return G': '26',
            'V. Return H': '27',
            'Exp. 1': '28',
            'Exp. 2': '29',
            'Exp. 3': '30',
            'Exp. 4': '31',
            'Exp. 5': '32',
            'Exp. 6': '33',
            'Exp. 7': '34',
            'Exp. 8': '35',
            'Exp. 9': '36',
            'Exp. 10': '37',
            'Exp. 11': '38',
            'Exp. 12': '39',
            'Exp. 13': '40',
            'Exp. 14': '41',
            'Exp. 15': '42',
            'Exp. 16': '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left'  : '12',
            'Output 7 Right' : '13',
            'Output 8 Left'  : '14',
            'Output 8 Right' : '15',
            'V. Send A': '16',
            'V. Send B': '17',
            'V. Send C': '18',
            'V. Send D': '19',
            'V. Send E': '20',
            'V. Send F': '21',
            'V. Send G': '22',
            'V. Send H': '23',
        }

        self.OutputStates = {
            '1'  : '1',
            '2'  : '2',
            '3'  : '3',
            '4'  : '4',
            '5A' : '5A',
            '5B' : '5B',
            '6A' : '6A',
            '6B' : '6B',
            '7'  : '7',
            '8'  : '8'
        }



    def extr_15_1691_108_MA(self):

        self.InputSize = 10
        self.OutputSize = 8
        self.Amplifier = 'Mono'

        self.DTPConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.ScaledOutputConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.EDIDStates = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5A',
            '6': 'Output 5B',
            '7': 'Output 6A',
            '8': 'Output 6B',
            '9': 'Output 7',
            '10': 'Output 8',
            '11': '1024x768 @ 50Hz',
            '12': '1024x768 @ 60Hz',
            '13': '1280x720 @ 50Hz',
            '14': '1280x720 @ 60Hz',
            '15': '1280x768 @ 50Hz',
            '16': '1280x768 @ 60Hz',
            '17': '1280x800 @ 50Hz',
            '18': '1280x800 @ 60Hz',
            '19': '1280x1024 @ 50Hz',
            '20': '1280x1024 @ 60Hz',
            '21': '1360x768 @ 50Hz',
            '22': '1360x768 @ 60Hz',
            '23': '1366x768 @ 50Hz',
            '24': '1366x768 @ 60Hz',
            '25': '1400x1050 @ 50Hz',
            '26': '1400x1050 @ 60Hz',
            '27': '1440x900 @ 50Hz',
            '28': '1440x900 @ 60Hz',
            '29': '1600x900 @ 50Hz',
            '30': '1600x900 @ 60Hz',
            '31': '1600x1200 @ 50Hz',
            '32': '1600x1200 @ 60Hz',
            '33': '1680x1050 @ 50Hz',
            '34': '1680x1050 @ 60Hz',
            '35': '1920x1080 @ 50Hz',
            '36': '1920x1080 @ 60Hz',
            '37': '1920x1200 @ 50Hz',
            '38': '1920x1200 @ 60Hz',
            '39': '2048x1080 @ 50Hz',
            '40': '2048x1080 @ 60Hz',
            '41': '480p 2_Ch Audio @ 60Hz',
            '42': '576p 2_Ch Audio @ 50Hz',
            '43': '720p 2_Ch Audio @ 50Hz',
            '44': '720p 2_Ch Audio @ 60Hz',
            '45': '720p Multi_Ch Audio @ 50Hz',
            '46': '720p Multi_Ch Audio @ 60Hz',
            '47': '1080i 2_Ch Audio @ 50Hz',
            '48': '1080i 2_Ch Audio @ 60Hz',
            '49': '1080i Multi_Ch Audio @ 50Hz',
            '50': '1080i Multi_Ch Audio @ 60Hz',
            '51': '1080p 2_Ch Audio @ 50Hz',
            '52': '1080p 2_Ch Audio @ 60Hz',
            '53': '1080p Multi_Ch Audio @ 50Hz',
            '54': '1080p Multi_Ch Audio @ 60Hz',
            '55': '3840x2160 2_Ch Audio @ 30Hz',
            '56': '3840x2160 Multi_Ch Audio @ 30Hz',
            '57': 'User Assigned 1',
            '58': 'User Assigned 2',
            '59': 'User Assigned 3',
            '60': 'User Assigned 4',
            '61': 'User Assigned 5',
            '62': 'User Assigned 6',
            '63': 'User Assigned 7',
            '64': 'User Assigned 8',
            '65': 'User Assigned 9',
            '66': 'User Assigned 10'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left': '12',
            'Output 7 Right': '13',
            'Output 8 Left': '14',
            'Output 8 Right': '15',
            'Mic 1': '16',
            'Mic 2': '17',
            'Mic 3': '18',
            'Mic 4': '19',
            'V. Return A': '20',
            'V. Return B': '21',
            'V. Return C': '22',
            'V. Return D': '23',
            'V. Return E': '24',
            'V. Return F': '25',
            'V. Return G': '26',
            'V. Return H': '27',
            'Exp. 1': '28',
            'Exp. 2': '29',
            'Exp. 3': '30',
            'Exp. 4': '31',
            'Exp. 5': '32',
            'Exp. 6': '33',
            'Exp. 7': '34',
            'Exp. 8': '35',
            'Exp. 9': '36',
            'Exp. 10': '37',
            'Exp. 11': '38',
            'Exp. 12': '39',
            'Exp. 13': '40',
            'Exp. 14': '41',
            'Exp. 15': '42',
            'Exp. 16': '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left': '12',
            'Output 7 Right': '13',
            'Output 8 Left': '14',
            'Output 8 Right': '15',
            'V. Send A': '16',
            'V. Send B': '17',
            'V. Send C': '18',
            'V. Send D': '19',
            'V. Send E': '20',
            'V. Send F': '21',
            'V. Send G': '22',
            'V. Send H': '23',
        }

        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5A': '5A',
            '5B': '5B',
            '6A': '6A',
            '6B': '6B',
            '7': '7',
            '8': '8'
        }



    def extr_15_1691_108_SA(self):

        self.InputSize = 10
        self.OutputSize = 8
        self.Amplifier = 'Stereo'

        self.DTPConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.ScaledOutputConstraints = {
            'Min': 5,
            'Max': 8,
        }

        self.EDIDStates = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3',
            '4': 'Output 4',
            '5': 'Output 5A',
            '6': 'Output 5B',
            '7': 'Output 6A',
            '8': 'Output 6B',
            '9': 'Output 7',
            '10': 'Output 8',
            '11': '1024x768 @ 50Hz',
            '12': '1024x768 @ 60Hz',
            '13': '1280x720 @ 50Hz',
            '14': '1280x720 @ 60Hz',
            '15': '1280x768 @ 50Hz',
            '16': '1280x768 @ 60Hz',
            '17': '1280x800 @ 50Hz',
            '18': '1280x800 @ 60Hz',
            '19': '1280x1024 @ 50Hz',
            '20': '1280x1024 @ 60Hz',
            '21': '1360x768 @ 50Hz',
            '22': '1360x768 @ 60Hz',
            '23': '1366x768 @ 50Hz',
            '24': '1366x768 @ 60Hz',
            '25': '1400x1050 @ 50Hz',
            '26': '1400x1050 @ 60Hz',
            '27': '1440x900 @ 50Hz',
            '28': '1440x900 @ 60Hz',
            '29': '1600x900 @ 50Hz',
            '30': '1600x900 @ 60Hz',
            '31': '1600x1200 @ 50Hz',
            '32': '1600x1200 @ 60Hz',
            '33': '1680x1050 @ 50Hz',
            '34': '1680x1050 @ 60Hz',
            '35': '1920x1080 @ 50Hz',
            '36': '1920x1080 @ 60Hz',
            '37': '1920x1200 @ 50Hz',
            '38': '1920x1200 @ 60Hz',
            '39': '2048x1080 @ 50Hz',
            '40': '2048x1080 @ 60Hz',
            '41': '480p 2_Ch Audio @ 60Hz',
            '42': '576p 2_Ch Audio @ 50Hz',
            '43': '720p 2_Ch Audio @ 50Hz',
            '44': '720p 2_Ch Audio @ 60Hz',
            '45': '720p Multi_Ch Audio @ 50Hz',
            '46': '720p Multi_Ch Audio @ 60Hz',
            '47': '1080i 2_Ch Audio @ 50Hz',
            '48': '1080i 2_Ch Audio @ 60Hz',
            '49': '1080i Multi_Ch Audio @ 50Hz',
            '50': '1080i Multi_Ch Audio @ 60Hz',
            '51': '1080p 2_Ch Audio @ 50Hz',
            '52': '1080p 2_Ch Audio @ 60Hz',
            '53': '1080p Multi_Ch Audio @ 50Hz',
            '54': '1080p Multi_Ch Audio @ 60Hz',
            '55': '3840x2160 2_Ch Audio @ 30Hz',
            '56': '3840x2160 Multi_Ch Audio @ 30Hz',
            '57': 'User Assigned 1',
            '58': 'User Assigned 2',
            '59': 'User Assigned 3',
            '60': 'User Assigned 4',
            '61': 'User Assigned 5',
            '62': 'User Assigned 6',
            '63': 'User Assigned 7',
            '64': 'User Assigned 8',
            '65': 'User Assigned 9',
            '66': 'User Assigned 10'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left': '12',
            'Output 7 Right': '13',
            'Output 8 Left': '14',
            'Output 8 Right': '15',
            'Mic 1': '16',
            'Mic 2': '17',
            'Mic 3': '18',
            'Mic 4': '19',
            'V. Return A': '20',
            'V. Return B': '21',
            'V. Return C': '22',
            'V. Return D': '23',
            'V. Return E': '24',
            'V. Return F': '25',
            'V. Return G': '26',
            'V. Return H': '27',
            'Exp. 1': '28',
            'Exp. 2': '29',
            'Exp. 3': '30',
            'Exp. 4': '31',
            'Exp. 5': '32',
            'Exp. 6': '33',
            'Exp. 7': '34',
            'Exp. 8': '35',
            'Exp. 9': '36',
            'Exp. 10': '37',
            'Exp. 11': '38',
            'Exp. 12': '39',
            'Exp. 13': '40',
            'Exp. 14': '41',
            'Exp. 15': '42',
            'Exp. 16': '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Output 7 Left': '12',
            'Output 7 Right': '13',
            'Output 8 Left': '14',
            'Output 8 Right': '15',
            'V. Send A': '16',
            'V. Send B': '17',
            'V. Send C': '18',
            'V. Send D': '19',
            'V. Send E': '20',
            'V. Send F': '21',
            'V. Send G': '22',
            'V. Send H': '23',
        }

        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5A': '5A',
            '5B': '5B',
            '6A': '6A',
            '6B': '6B',
            '7': '7',
            '8': '8'
        }


        ### END DTP CROSSPOINT 108 4K MODELS### BEGIN DTP CROSSPOINT 86 4K MODELS        
    def extr_15_1691_86(self):

        self.InputSize = 8
        self.OutputSize = 6

        self.DTPConstraints = {
            'Min': 5,
            'Max': 6,
        }

        self.ScaledOutputConstraints = {
            'Min': 3,
            'Max': 6,
        }

        self.EDIDStates   = {
            '1'  : 'Output 1',
            '2'  : 'Output 2',
            '3'  : 'Output 3A',
            '4'  : 'Output 3B',
            '5'  : 'Output 4A',
            '6'  : 'Output 4B',
            '7'  : 'Output 5',
            '8'  : 'Output 6',
            '9'  : '1024x768 @ 50Hz',
            '10' : '1024x768 @ 60Hz',
            '11' : '1280x720 @ 50Hz',
            '12' : '1280x720 @ 60Hz',
            '13' : '1280x768 @ 50Hz',
            '14' : '1280x768 @ 60Hz',
            '15' : '1280x800 @ 50Hz',
            '16' : '1280x800 @ 60Hz',
            '17' : '1280x1024 @ 50Hz',
            '18' : '1280x1024 @ 60Hz',
            '19' : '1360x768 @ 50Hz',
            '20' : '1360x768 @ 60Hz',
            '21' : '1366x768 @ 50Hz',
            '22' : '1366x768 @ 60Hz',
            '23' : '1400x1050 @ 50Hz',
            '24' : '1400x1050 @ 60Hz',
            '25' : '1440x900 @ 50Hz',
            '26' : '1440x900 @ 60Hz',
            '27' : '1600x900 @ 50Hz',
            '28' : '1600x900 @ 60Hz',
            '29' : '1600x1200 @ 50Hz',
            '30' : '1600x1200 @ 60Hz',
            '31' : '1680x1050 @ 50Hz',
            '32' : '1680x1050 @ 60Hz',
            '33' : '1920x1080 @ 50Hz',
            '34' : '1920x1080 @ 60Hz',
            '35' : '1920x1200 @ 50Hz',
            '36' : '1920x1200 @ 60Hz',
            '37' : '2048x1080 @ 50Hz',
            '38' : '2048x1080 @ 60Hz',
            '39' : '480p 2_Ch Audio @ 60Hz',
            '40' : '576p 2_Ch Audio @ 50Hz',
            '41' : '720p 2_Ch Audio @ 50Hz',
            '42' : '720p 2_Ch Audio @ 60Hz',
            '43' : '720p Multi_Ch Audio @ 50Hz',
            '44' : '720p Multi_Ch Audio @ 60Hz',
            '45' : '1080i 2_Ch Audio @ 50Hz',
            '46' : '1080i 2_Ch Audio @ 60Hz',
            '47' : '1080i Multi_Ch Audio @ 50Hz',
            '48' : '1080i Multi_Ch Audio @ 60Hz',
            '49' : '1080p 2_Ch Audio @ 50Hz',
            '50' : '1080p 2_Ch Audio @ 60Hz',
            '51' : '1080p Multi_Ch Audio @ 50Hz',
            '52' : '1080p Multi_Ch Audio @ 60Hz',
            '53' : '3840x2160 2_Ch Audio @ 30Hz',
            '54' : '3840x2160 Multi_Ch Audio @ 30Hz',
            '55' : 'User Assigned 1',
            '56' : 'User Assigned 2',
            '57' : 'User Assigned 3',
            '58' : 'User Assigned 4',
            '59' : 'User Assigned 5',
            '60' : 'User Assigned 6',
            '61' : 'User Assigned 7',
            '62' : 'User Assigned 8'
        }

        self.MixPointInputs = {
            'Output 1 Left'  : '00',
            'Output 1 Right' : '01',
            'Output 2 Left'  : '02',
            'Output 2 Right' : '03',
            'Output 3 Left'  : '04',
            'Output 3 Right' : '05',
            'Output 4 Left'  : '06',
            'Output 4 Right' : '07',
            'Output 5 Left'  : '08',
            'Output 5 Right' : '09',
            'Output 6 Left'  : '10',
            'Output 6 Right' : '11',
            'Mic 1' : '16',
            'Mic 2' : '17',
            'Mic 3' : '18',
            'Mic 4' : '19',
            'V. Return A' : '20',
            'V. Return B' : '21',
            'V. Return C' : '22',
            'V. Return D' : '23',
            'V. Return E' : '24',
            'V. Return F' : '25',
            'V. Return G' : '26',
            'V. Return H' : '27',
            'Exp. 1' : '28',
            'Exp. 2' : '29',
            'Exp. 3' : '30',
            'Exp. 4' : '31',
            'Exp. 5' : '32',
            'Exp. 6' : '33',
            'Exp. 7' : '34',
            'Exp. 8' : '35',
            'Exp. 9'  : '36',
            'Exp. 10' : '37',
            'Exp. 11' : '38',
            'Exp. 12' : '39',
            'Exp. 13' : '40',
            'Exp. 14' : '41',
            'Exp. 15' : '42',
            'Exp. 16' : '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left'  : '00',
            'Output 1 Right' : '01',
            'Output 2 Left'  : '02',
            'Output 2 Right' : '03',
            'Output 3 Left'  : '04',
            'Output 3 Right' : '05',
            'Output 4 Left'  : '06',
            'Output 4 Right' : '07',
            'Output 5 Left'  : '08',
            'Output 5 Right' : '09',
            'Output 6 Left'  : '10',
            'Output 6 Right' : '11',
            'V. Send A' : '16',
            'V. Send B' : '17',
            'V. Send C' : '18',
            'V. Send D' : '19',
            'V. Send E' : '20',
            'V. Send F' : '21',
            'V. Send G' : '22',
            'V. Send H' : '23',
        }

        self.OutputStates = {
            '1'  : '1',
            '2'  : '2',
            '3A' : '3A',
            '3B' : '3B',
            '4A' : '4A',
            '4B' : '4B',
            '5'  : '5',
            '6'  : '6'
        }



    def extr_15_1691_86_MA(self):

        self.InputSize = 8
        self.OutputSize = 6
        self.Amplifier = 'Mono'

        self.DTPConstraints = {
            'Min': 5,
            'Max': 6,
        }

        self.ScaledOutputConstraints = {
            'Min': 3,
            'Max': 6,
        }

        self.EDIDStates = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3A',
            '4': 'Output 3B',
            '5': 'Output 4A',
            '6': 'Output 4B',
            '7': 'Output 5',
            '8': 'Output 6',
            '9': '1024x768 @ 50Hz',
            '10': '1024x768 @ 60Hz',
            '11': '1280x720 @ 50Hz',
            '12': '1280x720 @ 60Hz',
            '13': '1280x768 @ 50Hz',
            '14': '1280x768 @ 60Hz',
            '15': '1280x800 @ 50Hz',
            '16': '1280x800 @ 60Hz',
            '17': '1280x1024 @ 50Hz',
            '18': '1280x1024 @ 60Hz',
            '19': '1360x768 @ 50Hz',
            '20': '1360x768 @ 60Hz',
            '21': '1366x768 @ 50Hz',
            '22': '1366x768 @ 60Hz',
            '23': '1400x1050 @ 50Hz',
            '24': '1400x1050 @ 60Hz',
            '25': '1440x900 @ 50Hz',
            '26': '1440x900 @ 60Hz',
            '27': '1600x900 @ 50Hz',
            '28': '1600x900 @ 60Hz',
            '29': '1600x1200 @ 50Hz',
            '30': '1600x1200 @ 60Hz',
            '31': '1680x1050 @ 50Hz',
            '32': '1680x1050 @ 60Hz',
            '33': '1920x1080 @ 50Hz',
            '34': '1920x1080 @ 60Hz',
            '35': '1920x1200 @ 50Hz',
            '36': '1920x1200 @ 60Hz',
            '37': '2048x1080 @ 50Hz',
            '38': '2048x1080 @ 60Hz',
            '39': '480p 2_Ch Audio @ 60Hz',
            '40': '576p 2_Ch Audio @ 50Hz',
            '41': '720p 2_Ch Audio @ 50Hz',
            '42': '720p 2_Ch Audio @ 60Hz',
            '43': '720p Multi_Ch Audio @ 50Hz',
            '44': '720p Multi_Ch Audio @ 60Hz',
            '45': '1080i 2_Ch Audio @ 50Hz',
            '46': '1080i 2_Ch Audio @ 60Hz',
            '47': '1080i Multi_Ch Audio @ 50Hz',
            '48': '1080i Multi_Ch Audio @ 60Hz',
            '49': '1080p 2_Ch Audio @ 50Hz',
            '50': '1080p 2_Ch Audio @ 60Hz',
            '51': '1080p Multi_Ch Audio @ 50Hz',
            '52': '1080p Multi_Ch Audio @ 60Hz',
            '53': '3840x2160 2_Ch Audio @ 30Hz',
            '54': '3840x2160 Multi_Ch Audio @ 30Hz',
            '55': 'User Assigned 1',
            '56': 'User Assigned 2',
            '57': 'User Assigned 3',
            '58': 'User Assigned 4',
            '59': 'User Assigned 5',
            '60': 'User Assigned 6',
            '61': 'User Assigned 7',
            '62': 'User Assigned 8'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Mic 1': '16',
            'Mic 2': '17',
            'Mic 3': '18',
            'Mic 4': '19',
            'V. Return A': '20',
            'V. Return B': '21',
            'V. Return C': '22',
            'V. Return D': '23',
            'V. Return E': '24',
            'V. Return F': '25',
            'V. Return G': '26',
            'V. Return H': '27',
            'Exp. 1': '28',
            'Exp. 2': '29',
            'Exp. 3': '30',
            'Exp. 4': '31',
            'Exp. 5': '32',
            'Exp. 6': '33',
            'Exp. 7': '34',
            'Exp. 8': '35',
            'Exp. 9': '36',
            'Exp. 10': '37',
            'Exp. 11': '38',
            'Exp. 12': '39',
            'Exp. 13': '40',
            'Exp. 14': '41',
            'Exp. 15': '42',
            'Exp. 16': '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'V. Send A': '16',
            'V. Send B': '17',
            'V. Send C': '18',
            'V. Send D': '19',
            'V. Send E': '20',
            'V. Send F': '21',
            'V. Send G': '22',
            'V. Send H': '23',
        }

        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3A': '3A',
            '3B': '3B',
            '4A': '4A',
            '4B': '4B',
            '5': '5',
            '6': '6'
        }

    def extr_15_1691_86_SA(self):

        self.InputSize = 8
        self.OutputSize = 6
        self.Amplifier = 'Stereo'

        self.DTPConstraints = {
            'Min': 5,
            'Max': 6,
        }

        self.ScaledOutputConstraints = {
            'Min': 3,
            'Max': 6,
        }

        self.EDIDStates = {
            '1': 'Output 1',
            '2': 'Output 2',
            '3': 'Output 3A',
            '4': 'Output 3B',
            '5': 'Output 4A',
            '6': 'Output 4B',
            '7': 'Output 5',
            '8': 'Output 6',
            '9': '1024x768 @ 50Hz',
            '10': '1024x768 @ 60Hz',
            '11': '1280x720 @ 50Hz',
            '12': '1280x720 @ 60Hz',
            '13': '1280x768 @ 50Hz',
            '14': '1280x768 @ 60Hz',
            '15': '1280x800 @ 50Hz',
            '16': '1280x800 @ 60Hz',
            '17': '1280x1024 @ 50Hz',
            '18': '1280x1024 @ 60Hz',
            '19': '1360x768 @ 50Hz',
            '20': '1360x768 @ 60Hz',
            '21': '1366x768 @ 50Hz',
            '22': '1366x768 @ 60Hz',
            '23': '1400x1050 @ 50Hz',
            '24': '1400x1050 @ 60Hz',
            '25': '1440x900 @ 50Hz',
            '26': '1440x900 @ 60Hz',
            '27': '1600x900 @ 50Hz',
            '28': '1600x900 @ 60Hz',
            '29': '1600x1200 @ 50Hz',
            '30': '1600x1200 @ 60Hz',
            '31': '1680x1050 @ 50Hz',
            '32': '1680x1050 @ 60Hz',
            '33': '1920x1080 @ 50Hz',
            '34': '1920x1080 @ 60Hz',
            '35': '1920x1200 @ 50Hz',
            '36': '1920x1200 @ 60Hz',
            '37': '2048x1080 @ 50Hz',
            '38': '2048x1080 @ 60Hz',
            '39': '480p 2_Ch Audio @ 60Hz',
            '40': '576p 2_Ch Audio @ 50Hz',
            '41': '720p 2_Ch Audio @ 50Hz',
            '42': '720p 2_Ch Audio @ 60Hz',
            '43': '720p Multi_Ch Audio @ 50Hz',
            '44': '720p Multi_Ch Audio @ 60Hz',
            '45': '1080i 2_Ch Audio @ 50Hz',
            '46': '1080i 2_Ch Audio @ 60Hz',
            '47': '1080i Multi_Ch Audio @ 50Hz',
            '48': '1080i Multi_Ch Audio @ 60Hz',
            '49': '1080p 2_Ch Audio @ 50Hz',
            '50': '1080p 2_Ch Audio @ 60Hz',
            '51': '1080p Multi_Ch Audio @ 50Hz',
            '52': '1080p Multi_Ch Audio @ 60Hz',
            '53': '3840x2160 2_Ch Audio @ 30Hz',
            '54': '3840x2160 Multi_Ch Audio @ 30Hz',
            '55': 'User Assigned 1',
            '56': 'User Assigned 2',
            '57': 'User Assigned 3',
            '58': 'User Assigned 4',
            '59': 'User Assigned 5',
            '60': 'User Assigned 6',
            '61': 'User Assigned 7',
            '62': 'User Assigned 8'
        }

        self.MixPointInputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'Mic 1': '16',
            'Mic 2': '17',
            'Mic 3': '18',
            'Mic 4': '19',
            'V. Return A': '20',
            'V. Return B': '21',
            'V. Return C': '22',
            'V. Return D': '23',
            'V. Return E': '24',
            'V. Return F': '25',
            'V. Return G': '26',
            'V. Return H': '27',
            'Exp. 1': '28',
            'Exp. 2': '29',
            'Exp. 3': '30',
            'Exp. 4': '31',
            'Exp. 5': '32',
            'Exp. 6': '33',
            'Exp. 7': '34',
            'Exp. 8': '35',
            'Exp. 9': '36',
            'Exp. 10': '37',
            'Exp. 11': '38',
            'Exp. 12': '39',
            'Exp. 13': '40',
            'Exp. 14': '41',
            'Exp. 15': '42',
            'Exp. 16': '43'
        }

        self.MixPointOutputs = {
            'Output 1 Left': '00',
            'Output 1 Right': '01',
            'Output 2 Left': '02',
            'Output 2 Right': '03',
            'Output 3 Left': '04',
            'Output 3 Right': '05',
            'Output 4 Left': '06',
            'Output 4 Right': '07',
            'Output 5 Left': '08',
            'Output 5 Right': '09',
            'Output 6 Left': '10',
            'Output 6 Right': '11',
            'V. Send A': '16',
            'V. Send B': '17',
            'V. Send C': '18',
            'V. Send D': '19',
            'V. Send E': '20',
            'V. Send F': '21',
            'V. Send G': '22',
            'V. Send H': '23',
        }

        self.OutputStates = {
            '1': '1',
            '2': '2',
            '3A': '3A',
            '3B': '3B',
            '4A': '4A',
            '4B': '4B',
            '5': '5',
            '6': '6'
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

        #check incoming data if it matched any expected data from device module
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
