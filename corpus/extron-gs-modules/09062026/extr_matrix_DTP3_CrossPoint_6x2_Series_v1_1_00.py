# Copyright 2026, Extron. All rights reserved.

from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from collections import OrderedDict

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
            'DTP3 CrossPoint 622': self.extr_15_17511_622,
            'DTP3 CrossPoint 622 IPCP A': self.extr_15_17511_622_A,
            'DTP3 CrossPoint 622 IPCP A SL': self.extr_15_17511_622_A_SL,
            'DTP3 CrossPoint 642': self.extr_15_17511_642,
            'DTP3 CrossPoint 642 IPCP A': self.extr_15_17511_642_A,
            'DTP3 CrossPoint 642 IPCP A SL': self.extr_15_17511_642_A_SL,
            'DTP3 CrossPoint 662': self.extr_15_17511_662,
            'DTP3 CrossPoint 662 IPCP A': self.extr_15_17511_662_A,
            'DTP3 CrossPoint 662 IPCP A SL': self.extr_15_17511_662_A_SL
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AmplifierAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'AmplifierMute': {'Parameters': ['Output'], 'Status': {}},
            'AmplifierOutputMode': { 'Status': {}},
            'AmplifierPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AnalogAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'AnalogMute': {'Parameters': ['Output'], 'Status': {}},
            'AnalogPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'ATAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'ATMute': {'Parameters': ['Output'], 'Status': {}},
            'ATPostmixerTrim': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Parameters': ['Output'], 'Status': {}},
            'AutomixerGateMonitor': {'Parameters': ['Input'], 'Status': {}},
            'AutomixerGateStatus': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FanSpeed': {'Parameters': ['Fan'], 'Status': {}},
            'FlexAnalogInputGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexDigitalInputGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputMute': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelMonitor': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelStatus': {'Parameters': ['Input'], 'Status': {}},
            'FlexInputSignalLevelValue': {'Parameters': ['Input'], 'Status': {}},
            'FlexPremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'FlexPremixerMute': {'Parameters': ['Input'], 'Status': {}},
            'Freeze': {'Parameters': ['Output'], 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'GroupMixpoint': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupOutputAttenuation': {'Parameters': ['Group'], 'Status': {}},
            'GroupPostmixerTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPrematrixTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupPremixerGain': {'Parameters': ['Group'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIDTPAttenuation': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'HDMIDTPMute': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'HDMIDTPPostmixerTrim': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'InputAudioSwitchMode': {'Parameters': ['Input'], 'Status': {}},
            'InputConnectorType': {'Parameters': ['Input'], 'Status': {}},
            'InputGain': {'Parameters': ['Input', 'Format', 'L/R'], 'Status': {}},
            'InputMute': {'Parameters': ['Input', 'L/R'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'Logo': {'Parameters': ['Output'], 'Status': {}},
            'Macro': {'Parameters': ['Macro'], 'Status': {}},
            'MacroStatus': { 'Status': {}},
            'MatrixIONameCommand': {'Parameters': ['Type', 'Number', 'Name'], 'Status': {}},
            'MatrixIONameStatus': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'MatrixIONumberSelect': { 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'MixpointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MixpointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputAudioSelect': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatusName': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PhantomPower': {'Parameters': ['Input'], 'Status': {}},
            'PostMatrixGain': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'PostMatrixMute': {'Parameters': ['Output', 'L/R'], 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'PowerSupplyVoltage': { 'Status': {}},
            'PrematrixTrim': {'Parameters': ['Input', 'L/R'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'RefreshMatrixIONames': { 'Status': {}},
            'ScalerPresetRecall': {'Parameters': ['Output'], 'Status': {}},
            'Temperature': {'Parameters': ['Scale'], 'Status': {}},
            'USBCallStatus': { 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}}
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        self.group_functions = {}
        self.matrix_tie_status = None
        self.matrix_io_names = {}
        self.matrix_io_names_received = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DsG(6002[67])\*(-?\d+)\r\n'), self.__MatchAmplifierAttenuation, None)
            self.AddMatchString(re.compile(b'DsM(6002[67])\*([01])\r\n'), self.__MatchAmplifierMute, None)
            self.AddMatchString(re.compile(b'Spkr([1-4])\r\n'), self.__MatchAmplifierOutputMode, None)
            self.AddMatchString(re.compile(b'DsG(6012[67])\*(-?\d+)\r\n'), self.__MatchAmplifierPostmixerTrim, None)
            self.AddMatchString(re.compile(b'DsG(6002[45])\*(-?\d+)\r\n'), self.__MatchAnalogAttenuation, None)
            self.AddMatchString(re.compile(b'DsM(6002[45])\*([01])\r\n'), self.__MatchAnalogMute, None)
            self.AddMatchString(re.compile(b'DsG(6012[45])\*(-?\d+)\r\n'), self.__MatchAnalogPostmixerTrim, None)
            self.AddMatchString(re.compile(b'Aspr([1-8])\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'DsG(600[3-6]\d)\*(-?\d+)\r\n'), self.__MatchATAttenuation, None)
            self.AddMatchString(re.compile(b'DsM(600[3-6]\d)\*([01])\r\n'), self.__MatchATMute, None)
            self.AddMatchString(re.compile(b'DsG(601[3-6]\d)\*(-?\d+)\r\n'), self.__MatchATPostmixerTrim, None)
            self.AddMatchString(re.compile(b'DsJ(590[0-4]\d)\*(0|1024)\r\n'), self.__MatchAutomixerGateMonitor, None)
            self.AddMatchString(re.compile(b'DsV(590[0-4]\d)\*[01]\*\d+\*([01])\r\n'), self.__MatchAutomixerGateStatus, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'DsG(400[0-4]\d)\*(-?\d+)\r\n'), self.__MatchFlexAnalogInputGain, None)
            self.AddMatchString(re.compile(b'DsH(400[0-4]\d)\*(-?\d+)\r\n'), self.__MatchFlexDigitalInputGain, None)
            self.AddMatchString(re.compile(b'DsM(400[0-4]\d)\*([01])\r\n'), self.__MatchFlexInputMute, None)
            self.AddMatchString(re.compile(b'DsJ(400[0-4]\d)\*(\d+)\r\n'), self.__MatchFlexInputSignalLevelMonitor, None)
            self.AddMatchString(re.compile(b'DsV(400[0-4]\d)\*[01]\*(\d+)\*([01])\r\n'), self.__MatchFlexInputSignalLevelStatus, None)
            self.AddMatchString(re.compile(b'DsG(401[0-4]\d)\*(-?\d+)\r\n'), self.__MatchFlexPremixerGain, None)
            self.AddMatchString(re.compile(b'DsM(401[0-4]\d)\*([01])\r\n'), self.__MatchFlexPremixerMute, None)
            self.AddMatchString(re.compile(b'Frz([1-8])\*([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'GrpmD(\d+)\*([-+]?\d+)\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'HdcpE([1-478]|[56][abAB])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI([1-4789]|[56][abAB])\*([012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([12][abAB]|[3-9])\*([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'DsG(600(?:0\d|1[0-7]))\*(-?\d+)\r\n'), self.__MatchHDMIDTPAttenuation, None)
            self.AddMatchString(re.compile(b'DsM(600(?:0\d|1[0-7]))\*([01])\r\n'), self.__MatchHDMIDTPMute, None)
            self.AddMatchString(re.compile(b'DsG(601(?:0\d|1[0-7]))\*(-?\d+)\r\n'), self.__MatchHDMIDTPPostmixerTrim, None)
            self.AddMatchString(re.compile(b'AfmtI([5-8])\*([0-2])\r\n'), self.__MatchInputAudioSwitchMode, 'Single')
            self.AddMatchString(re.compile(b'AfmtI00\*([0-2]+)\r\n'), self.__MatchInputAudioSwitchMode, 'All')
            self.AddMatchString(re.compile(b'Ityp([56])\*([12])\r\n'), self.__MatchInputConnectorType, None)
            self.AddMatchString(re.compile(b'Ds([GH])(300(?:0\d|1[0-7]))\*(-?\d+)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'DsM(300(?:0\d|1[0-7]))\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'In00 ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'SigI([1-9])\*([01])\r\n'), self.__MatchInputSignalStatus, 'Unsolicited')
            self.AddMatchString(re.compile(b'LogoE([1-8])\*(\d+)\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Mcro(STARTED|FINISHED)(\d+)\r\n'), self.__MatchMacroStatus, 'StartedFinished')
            self.AddMatchString(re.compile(b'Mcro(FAILED|KILLED)(\d+)\*(\d+)\r\n'), self.__MatchMacroStatus, 'FailedKilled')
            self.AddMatchString(re.compile(b'Nm([io])([1-9]),([ \S]{0,32})\r\n'), self.__MatchMatrixIONameStatus, None)
            self.AddMatchString(re.compile(b'DsG2(\d{2})(\d{2})\*(-?\d+)\r\n'), self.__MatchMixpointGain, None)
            self.AddMatchString(re.compile(b'DsM2(\d{2})(\d{2})\*([01])\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(re.compile(b'AfmtO(\d+)\*([0-2])\r\n'), self.__MatchOutputAudioSelect, 'Single')
            self.AddMatchString(re.compile(b'AfmtO00\*([0-2]+)\r\n'), self.__MatchOutputAudioSelect, 'All')
            self.AddMatchString(re.compile(b'Rate(\d+)\*(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'DsZ(400[0-4]\d)\*([01])\r\n'), self.__MatchPhantomPower, None)
            self.AddMatchString(re.compile(b'DsG(500(?:0\d|1[0-7]|2[4-7]))\*(-?\d+)\r\n'), self.__MatchPostMatrixGain, None)
            self.AddMatchString(re.compile(b'DsM(500(?:0\d|1[0-7]|2[4-7]))\*([01])\r\n'), self.__MatchPostMatrixMute, None)
            self.AddMatchString(re.compile(b'PsavM?([0129])\r\n'), self.__MatchPowerSaveMode, None) # SIS manual says there is a M but based on testing there isn't
            self.AddMatchString(re.compile(b'DsG(301(?:0\d|1[0-7]))\*(-?\d+)\r\n'), self.__MatchPrematrixTrim, None)
            self.AddMatchString(re.compile(b'Sts00 +(\d+\.\d+) (\d+\.\d+)F (\d+\.\d+)C (\d+) (\d+) \d\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'UphnH1\*([01])\r\n'), self.__MatchUSBCallStatus, None)
            self.AddMatchString(re.compile(b'Vmut([12][abAB]|[3-9])\*([012])\r\n'), self.__MatchVideoMute, None)

            self.AddMatchString(re.compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(re.compile(b'PrstR\d+\r\n'), self.__MatchQik, None)  # Response to a Set Preset Recall command
            self.AddMatchString(re.compile(b'Rpr\d+(?:\*\d+)?\r\n'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'Vgp00 Out1\*([0-9 -]*)Vid\r\nVgp00 Out1\*([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, None)
            self.AddMatchString(re.compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud))|(?:In(\d+) (All|Vid|Aud))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)             
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
        
        for io_list in [self.inputs, self.inputs_sl, self.outputs, self.outputs_sl, self.outputs_a_sl]:
            io_list.sort(key=lambda io: int(io))

        self.matrix_tie_status = OrderedDict((input_, OrderedDict((output, 'Untied') for output in self.outputs_a_sl)) for input_ in self.inputs_sl)

        self.Send('w0*1*1VC\r\nw0*1*2VC\r\n')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = [str(output)]
        else:
            output_range = self.outputs_a_sl
        for input_ in self.inputs_sl:
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': input_, 'Output': output})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = [output]
        else:
            output_range = self.outputs_a_sl
        for input_ in self.inputs_sl:
            inputName = self.ReadStatus('MatrixIONameStatus', {'Type': 'Input', 'Number': input_}) # get input name to write for 'Output Tie Status Name'
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                inputName = 'Untied' if not inputName else inputName # write 'Untied' for 'Output Tie Status Name' if no input name exists
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': tie_type})
                        if self.matrix_io_names_received: # only write 'Output Tie Status Name' if 'Matrix IO Name Status' has been written (prevents debug log error)
                            self.WriteStatus('OutputTieStatusName', inputName, {'Output': output, 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': output, 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': 'Audio'})
                    if self.matrix_io_names_received:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': output, 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': output, 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', input_, {'Output': output, 'Tie Type': 'Video'})
                    if self.matrix_io_names_received:
                        self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': output, 'Tie Type': 'Audio/Video'})
                        self.WriteStatus('OutputTieStatusName', inputName, {'Output': output, 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': o, 'Tie Type': 'Video'})
                if self.matrix_io_names_received:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output':o, 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': o, 'Tie Type': 'Audio'})
                if self.matrix_io_names_received:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': o, 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': o, 'Tie Type': 'Audio/Video'})
                if self.matrix_io_names_received:
                    self.WriteStatus('OutputTieStatusName', 'Untied', {'Output': o, 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        if not self.matrix_tie_status:
            return
        
        ties = {
            'Video': match.group(1).decode(),
            'Audio': match.group(2).decode()
        }

        for tag, match in ties.items():
            opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

            for output, input_ in enumerate(match.strip().split(), 1):
                if input_ in ['0', '-1']:
                    continue
                if input_ not in self.inputs_sl:
                    continue
                if str(output) not in self.outputs_a_sl:
                    continue

                if self.matrix_tie_status[input_][str(output)] == opposite_tag:
                    self.matrix_tie_status[input_][str(output)] = 'Audio/Video'
                else:
                    self.matrix_tie_status[input_][str(output)] = tag

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetAmplifierAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])
        
        value = round(value, 1)

        if 1 <= output <= 2 and -100 <= value <= 0:
            AmplifierAttenuationCmdString = 'wG{}*{}AU\r'.format(60025 + output, round(value * 10))
            self.__SetHelper('AmplifierAttenuation', AmplifierAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierAttenuation')

    def UpdateAmplifierAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            AmplifierAttenuationCmdString = 'wG{}AU\r'.format(60025 + output)
            self.__UpdateHelper('AmplifierAttenuation', AmplifierAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierAttenuation')

    def __MatchAmplifierAttenuation(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60025)
        }

        value = int(match.group(2).decode()) / 10
        if -100 <= value <= 0:
            self.WriteStatus('AmplifierAttenuation', value, qualifier)

    def SetAmplifierMute(self, value, qualifier):

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        output = int(qualifier['Output'])
        
        if 1 <= output <= 2 and value in ValueStateValues:
            AmplifierMuteCmdString = 'wM{}*{}AU\r'.format(60025 + output, ValueStateValues[value])
            self.__SetHelper('AmplifierMute', AmplifierMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierMute')

    def UpdateAmplifierMute(self, value, qualifier):

        output = int(qualifier['Output'])
        
        if 1 <= output <= 2:
            AmplifierMuteCmdString = 'wM{}AU\r'.format(60025 + output)
            self.__UpdateHelper('AmplifierMute', AmplifierMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierMute')

    def __MatchAmplifierMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60025)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AmplifierMute', value, qualifier)

    def UpdateAmplifierOutputMode(self, value, qualifier):

        AmplifierOutputModeCmdString = 'wSPKR\r'
        self.__UpdateHelper('AmplifierOutputMode', AmplifierOutputModeCmdString, value, qualifier)

    def __MatchAmplifierOutputMode(self, match, tag):

        ValueStateValues = {
            '1': 'Stereo, 4/8 ohms',
            '2': 'Bridged Mono, 8 ohms',
            '3': 'Bridged Mono, 70 volts',
            '4': 'Bridged Mono, 100 volts'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AmplifierOutputMode', value, None)

    def SetAmplifierPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])
        
        value = round(value, 1)

        if 1 <= output <= 2 and -12 <= value <= 12:
            AmplifierPostmixerTrimCmdString = 'wG{}*{}AU\r'.format(60125 + output, round(value * 10))
            self.__SetHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAmplifierPostmixerTrim')

    def UpdateAmplifierPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            AmplifierPostmixerTrimCmdString = 'wG{}AU\r'.format(60125 + output)
            self.__UpdateHelper('AmplifierPostmixerTrim', AmplifierPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAmplifierPostmixerTrim')

    def __MatchAmplifierPostmixerTrim(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60125)
        }

        value = int(match.group(2).decode()) / 10
        if -12 <= value <= 12:
            self.WriteStatus('AmplifierPostmixerTrim', value, qualifier)

    def SetAnalogAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])

        value = round(value, 1)

        if 1 <= output <= 2 and -100 <= value <= 0:
            AnalogAttenuationCmdString = 'wG{}*{}AU\r'.format(60023 + output, round(value * 10))
            self.__SetHelper('AnalogAttenuation', AnalogAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogAttenuation')

    def UpdateAnalogAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            AnalogAttenuationCmdString = 'wG{}AU\r'.format(60023 + output)
            self.__UpdateHelper('AnalogAttenuation', AnalogAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogAttenuation')

    def __MatchAnalogAttenuation(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60023)
        }

        value = int(match.group(2).decode()) / 10
        if -100 <= value <= 0:
            self.WriteStatus('AnalogAttenuation', value, qualifier)

    def SetAnalogMute(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= output <= 2 and value in ValueStateValues:
            AnalogMuteCmdString = 'wM{}*{}AU\r'.format(60023 + output, ValueStateValues[value])
            self.__SetHelper('AnalogMute', AnalogMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogMute')

    def UpdateAnalogMute(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            AnalogMuteCmdString = 'wM{}AU\r'.format(60023 + output)
            self.__UpdateHelper('AnalogMute', AnalogMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogMute')

    def __MatchAnalogMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60023)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AnalogMute', value, qualifier)

    def SetAnalogPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])

        value = round(value, 1)

        if 1 <= output <= 2 and -12 <= value <= 12:
            AnalogPostmixerTrimCmdString = 'wG{}*{}AU\r'.format(60123 + output, round(value * 10))
            self.__SetHelper('AnalogPostmixerTrim', AnalogPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogPostmixerTrim')

    def UpdateAnalogPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 2:
            AnalogPostmixerTrimCmdString = 'wG{}AU\r'.format(60123 + output)
            self.__UpdateHelper('AnalogPostmixerTrim', AnalogPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogPostmixerTrim')

    def __MatchAnalogPostmixerTrim(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60123)
        }

        value = int(match.group(2).decode()) / 10
        if -12 <= value <= 12:
            self.WriteStatus('AnalogPostmixerTrim', value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        input_ = int(qualifier['Input']) 

        ValueStateValues = {
            'Fill':     '1',
            'Follow':   '2'
        }

        if 1 <= input_ <= 8 and value in ValueStateValues:
            AspectRatioCmdString = 'w{}*{}ASPR\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 8:
            AspectRatioCmdString = 'w{}ASPR\r'.format(input_)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Fill',
            '2': 'Follow'
        }

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetATAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])

        value = round(value, 1)

        if 1 <= output <= 32 and -100 <= value <= 0:
            ATAttenuationCmdString = 'wG{}*{}AU\r'.format(60035 + output, round(value * 10))
            self.__SetHelper('ATAttenuation', ATAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATAttenuation')

    def UpdateATAttenuation(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 32:
            ATAttenuationCmdString = 'wG{}AU\r'.format(60035 + output)
            self.__UpdateHelper('ATAttenuation', ATAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATAttenuation')

    def __MatchATAttenuation(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60035)
        }

        value = int(match.group(2).decode()) / 10
        if -100 <= value <= 0:
            self.WriteStatus('ATAttenuation', value, qualifier)

    def SetATMute(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= output <= 32 and value in ValueStateValues:
            ATMuteCmdString = 'wM{}*{}AU\r'.format(60035 + output, ValueStateValues[value])
            self.__SetHelper('ATMute', ATMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATMute')

    def UpdateATMute(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 32:
            ATMuteCmdString = 'wM{}AU\r'.format(60035 + output)
            self.__UpdateHelper('ATMute', ATMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATMute')

    def __MatchATMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60035)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ATMute', value, qualifier)

    def SetATPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])

        value = round(value, 1)

        if 1 <= output <= 32 and -12 <= value <= 12:
            ATPostmixerTrimCmdString = 'wG{}*{}AU\r'.format(60135 + output, round(value * 10))
            self.__SetHelper('ATPostmixerTrim', ATPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetATPostmixerTrim')

    def UpdateATPostmixerTrim(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 32:
            ATPostmixerTrimCmdString = 'wG{}AU\r'.format(60135 + output)
            self.__UpdateHelper('ATPostmixerTrim', ATPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateATPostmixerTrim')

    def __MatchATPostmixerTrim(self, match, tag):

        qualifier = {
            'Output': str(int(match.group(1).decode()) - 60135)
        }

        value = int(match.group(2).decode()) / 10
        if -12 <= value <= 12:
            self.WriteStatus('ATPostmixerTrim', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        output = qualifier['Output']

        ValueStateValues = {
            'Execute':              '0',
            'Execute and Fill':     '1',
            'Execute and Follow':   '2'
        }

        if output in self.outputs and value in ValueStateValues:
            AutoImageCmdString = '{}*{}A'.format(output, ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetAutomixerGateMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'On':   '1024',
            'Off':  '0'
        }

        if 1 <= input_ <= 48 and value in ValueStateValues:
            AutomixerGateMonitorCmdString = 'wJ{}*{}AU\r'.format(58999 + input_, ValueStateValues[value])
            self.__SetHelper('AutomixerGateMonitor', AutomixerGateMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutomixerGateMonitor')

    def UpdateAutomixerGateMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            AutomixerGateMonitorCmdString = 'wJ{}AU\r'.format(58999 + input_)
            self.__UpdateHelper('AutomixerGateMonitor', AutomixerGateMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutomixerGateMonitor')

    def __MatchAutomixerGateMonitor(self, match, tag):

        ValueStateValues = {
            '1024': 'On',
            '0':    'Off'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 58999)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateMonitor', value, qualifier)

    def __MatchAutomixerGateStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Opened',
            '0': 'Closed'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 58999)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutomixerGateStatus', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':      '0',
            'Mode 1':   '1',
            'Mode 2':   '2'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = '{}X'.format(ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        } 

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def UpdateFanSpeed(self, value, qualifier):

        fan = int(qualifier['Fan'])

        if 1 <= fan <= 2:
            self.UpdateTemperature(None, {'Scale': 'Fahrenheit'})
        else:
            self.Discard('Invalid Command for UpdateFanSpeed')

    def SetFlexAnalogInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])
        
        value = round(value, 1)

        if 1 <= input_ <= 48 and -18 <= value <= 80:
            FlexAnalogInputGainCmdString = 'wG{}*{}AU\r'.format(39999 + input_, round(value * 10))
            self.__SetHelper('FlexAnalogInputGain', FlexAnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexAnalogInputGain')

    def UpdateFlexAnalogInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexAnalogInputGainCmdString = 'wG{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('FlexAnalogInputGain', FlexAnalogInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexAnalogInputGain')

    def __MatchFlexAnalogInputGain(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = int(match.group(2).decode()) / 10
        if -18 <= value <= 80:
            self.WriteStatus('FlexAnalogInputGain', value, qualifier)

    def SetFlexDigitalInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])
        
        value = round(value, 1)

        if 1 <= input_ <= 48 and -18 <= value <= 24:
            FlexDigitalInputGainCmdString = 'wH{}*{}AU\r'.format(39999 + input_, round(value * 10))
            self.__SetHelper('FlexDigitalInputGain', FlexDigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexDigitalInputGain')

    def UpdateFlexDigitalInputGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexDigitalInputGainCmdString = 'wH{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('FlexDigitalInputGain', FlexDigitalInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexDigitalInputGain')

    def __MatchFlexDigitalInputGain(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = int(match.group(2).decode()) / 10
        if -18 <= value <= 24:
            self.WriteStatus('FlexDigitalInputGain', value, qualifier)

    def SetFlexInputMute(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= input_ <= 48 and value in ValueStateValues:
            FlexInputMuteCmdString = 'wM{}*{}AU\r'.format(39999 + input_, ValueStateValues[value])
            self.__SetHelper('FlexInputMute', FlexInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexInputMute')

    def UpdateFlexInputMute(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexInputMuteCmdString = 'wM{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('FlexInputMute', FlexInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexInputMute')

    def __MatchFlexInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FlexInputMute', value, qualifier)

    def SetFlexInputSignalLevelMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        value = round(value, 1)
        if 1 <= input_ <= 48 and -150 <= value <= 0:
            FlexInputSignalLevelMonitorCmdString = 'wJ{}*{}AU\r'.format(39999 + input_, -round(value * 10))
            self.__SetHelper('FlexInputSignalLevelMonitor', FlexInputSignalLevelMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexInputSignalLevelMonitor')

    def UpdateFlexInputSignalLevelMonitor(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexInputSignalLevelMonitorCmdString = 'wJ{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('FlexInputSignalLevelMonitor', FlexInputSignalLevelMonitorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexInputSignalLevelMonitor')

    def __MatchFlexInputSignalLevelMonitor(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = -int(match.group(2).decode()) / 10
        if -150 <= value <= 0:
            self.WriteStatus('FlexInputSignalLevelMonitor', value, qualifier)

    def __MatchFlexInputSignalLevelStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Above',
            '1': 'Equal to or below'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = -int(match.group(2).decode()) / 10
        if -150 <= value <= 0:
            self.WriteStatus('FlexInputSignalLevelValue', value, qualifier)
        
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('FlexInputSignalLevelStatus', value, qualifier.copy())

    def SetFlexPremixerGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        value = round(value, 1)

        if 1 <= input_ <= 48 and -100 <= value <= 12:
            FlexPremixerGainCmdString = 'wG{}*{}AU\r'.format(40099 + input_, round(value * 10))
            self.__SetHelper('FlexPremixerGain', FlexPremixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexPremixerGain')

    def UpdateFlexPremixerGain(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexPremixerGainCmdString = 'wG{}AU\r'.format(40099 + input_)
            self.__UpdateHelper('FlexPremixerGain', FlexPremixerGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexPremixerGain')

    def __MatchFlexPremixerGain(self, match, tag):

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 40099)
        }

        value = int(match.group(2).decode()) / 10
        if -100 <= value <= 12:
            self.WriteStatus('FlexPremixerGain', value, qualifier)

    def SetFlexPremixerMute(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= input_ <= 48 and value in ValueStateValues:
            FlexPremixerMuteCmdString = 'wM{}*{}AU\r'.format(40099 + input_, ValueStateValues[value])
            self.__SetHelper('FlexPremixerMute', FlexPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFlexPremixerMute')

    def UpdateFlexPremixerMute(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            FlexPremixerMuteCmdString = 'wM{}AU\r'.format(40099 + input_)
            self.__UpdateHelper('FlexPremixerMute', FlexPremixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFlexPremixerMute')

    def __MatchFlexPremixerMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 40099)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FlexPremixerMute', value, qualifier)

    def SetFreeze(self, value, qualifier):

        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in self.outputs and value in ValueStateValues:
            FreezeCmdString = '{}*{}F'.format(output, ValueStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        output = qualifier['Output']

        if output in self.outputs:
            FreezeCmdString = '{}F'.format(output)
            self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFreeze')

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Output': match.group(1).decode()
        }

        if qualifier['Output'] in self.outputs:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Freeze', value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'Video':        '1',
            'Video & Sync': '2',
            'Off':          '0'
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = 'w{}*VMUT\r'.format(ValueStateValues[value])
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')
            
    def __MatchGroup(self, match, tag):

        ValueRanges = {
            'GroupMixpoint':            (-100, 12),
            'GroupOutputAttenuation':   (-100, 0),
            'GroupPostmixerTrim':       (-12, 12),
            'GroupPrematrixTrim':       (-12, 12),
            'GroupPremixerGain':        (-100, 12)
        }

        group = int(match.group(1))
        if group not in self.group_functions:
            return
        
        command = self.group_functions[group]        
        qualifier = {'Group': str(group)}

        if command == 'GroupMute':
            ValueStateValues = {
                '1': 'On',
                '0': 'Off'
            }
            value = match.group(2).decode()[-1]
            if value in ValueStateValues:
                self.WriteStatus(command, ValueStateValues[value], qualifier)
            else:
                self.Error(['Group Mute: Invalid/unexpected response'])
        else:
            value = int(match.group(2).decode()) / 10
            if ValueRanges[command][0] <= value <= ValueRanges[command][1]:
                self.WriteStatus(command, value, qualifier)

    def SetGroupMixpoint(self, value, qualifier):

        group = int(qualifier['Group'])

        value = round(value, 1)

        if 1 <= group <= 64 and -100 <= value <= 12:
            GroupMixpointCmdString = 'wD{}*{}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupMixpoint', GroupMixpointCmdString, value, qualifier)
            self.group_functions[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for SetGroupMixpoint')

    def UpdateGroupMixpoint(self, value, qualifier):

        group = int(qualifier['Group'])

        if 1 <= group <= 64:
            GroupMixpointCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMixpoint', GroupMixpointCmdString, value, qualifier)
            self.group_functions[group] = 'GroupMixpoint'
        else:
            self.Discard('Invalid Command for UpdateGroupMixpoint')

    def SetGroupMute(self, value, qualifier):

        group = int(qualifier['Group'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if 1 <= group <= 64 and value in ValueStateValues:
            GroupMuteCmdString = 'wD{}*{}GRPM\r'.format(group, ValueStateValues[value])
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
            self.group_functions[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = int(qualifier['Group']) 

        if 1 <= group <= 64:
            GroupMuteCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
            self.group_functions[group] = 'GroupMute'
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputAttenuation(self, value, qualifier):

        group = int(qualifier['Group']) 

        value = round(value, 1)

        if 1 <= group <= 64 and -100 <= value <= 0:
            GroupOutputAttenuationCmdString = 'wD{}*{}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupOutputAttenuation', GroupOutputAttenuationCmdString, value, qualifier)
            self.group_functions[group] = 'GroupOutputAttenuation'
        else:
            self.Discard('Invalid Command for SetGroupOutputAttenuation')

    def UpdateGroupOutputAttenuation(self, value, qualifier):

        group = int(qualifier['Group']) 

        if 1 <= group <= 64:
            GroupOutputAttenuationCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupOutputAttenuation', GroupOutputAttenuationCmdString, value, qualifier)
            self.group_functions[group] = 'GroupOutputAttenuation'
        else:
            self.Discard('Invalid Command for UpdateGroupOutputAttenuation')

    def SetGroupPostmixerTrim(self, value, qualifier):

        group = int(qualifier['Group'])

        value = round(value, 1)

        if 1 <= group <= 64 and -12 <= value <= 12:
            GroupPostmixerTrimCmdString = 'wD{}*{}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupPostmixerTrim', GroupPostmixerTrimCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPostmixerTrim'
        else:
            self.Discard('Invalid Command for SetGroupPostmixerTrim')

    def UpdateGroupPostmixerTrim(self, value, qualifier):

        group = int(qualifier['Group'])

        if 1 <= group <= 64:
            GroupPostmixerTrimCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPostmixerTrim', GroupPostmixerTrimCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPostmixerTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPostmixerTrim')

    def SetGroupPrematrixTrim(self, value, qualifier):

        group = int(qualifier['Group'])

        value = round(value, 1)

        if 1 <= group <= 64 and -12 <= value <= 12:
            GroupPrematrixTrimCmdString = 'wD{}*{}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupPrematrixTrim', GroupPrematrixTrimCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPrematrixTrim'
        else:
            self.Discard('Invalid Command for SetGroupPrematrixTrim')

    def UpdateGroupPrematrixTrim(self, value, qualifier):

        group = int(qualifier['Group'])

        if 1 <= group <= 64:
            GroupPrematrixTrimCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPrematrixTrim', GroupPrematrixTrimCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPrematrixTrim'
        else:
            self.Discard('Invalid Command for UpdateGroupPrematrixTrim')

    def SetGroupPremixerGain(self, value, qualifier):

        group = int(qualifier['Group'])

        value = round(value, 1)

        if 1 <= group <= 64 and -100 <= value <= 12:
            GroupPremixerGainCmdString = 'wD{}*{}GRPM\r'.format(group, round(value * 10))
            self.__SetHelper('GroupPremixerGain', GroupPremixerGainCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPremixerGain'
        else:
            self.Discard('Invalid Command for SetGroupPremixerGain')

    def UpdateGroupPremixerGain(self, value, qualifier):

        group = int(qualifier['Group'])

        if 1 <= group <= 64:
            GroupPremixerGainCmdString = 'wD{}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPremixerGain', GroupPremixerGainCmdString, value, qualifier)
            self.group_functions[group] = 'GroupPremixerGain'
        else:
            self.Discard('Invalid Command for UpdateGroupPremixerGain')

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = [
            '1',
            '2',
            '3',
            '4',
            '5A',
            '5B',
            '6A',
            '6B',
            '7',
            '8'
        ]
        input_ = qualifier['Input']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if input_ in InputStates and value in ValueStateValues:
            HDCPInputAuthorizationCmdString = 'wE{}*{}HDCP\r'.format(input_.lower(), ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        InputStates = [
            '1',
            '2',
            '3',
            '4',
            '5A',
            '5B',
            '6A',
            '6B',
            '7',
            '8'
        ]
        input_ = qualifier['Input']

        if input_ in InputStates:
            HDCPInputAuthorizationCmdString = 'wE{}HDCP\r'.format(input_.lower())
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': match.group(1).decode().upper()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        input_ = qualifier['Input']

        if input_ in self.hdcp_input_status:
            HDCPInputStatusCmdString = 'wI{}HDCP\r'.format(input_.lower())
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Connected',
            '1': 'HDCP Content',
            '2': 'No HDCP Content'
        }

        qualifier = {
            'Input': (match.group(1).decode().upper())
        }

        if qualifier['Input'] in self.hdcp_input_status:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        output = qualifier['Output']

        if output in self.hdcp_output_status:
            HDCPOutputStatusCmdString = 'wO{}HDCP\r'.format(output.lower())
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No monitor connected',
            '1': 'Monitor connected, not encrypted', 
            '2': 'Monitor connected, currently encrypted'
        }

        qualifier = {
            'Output': match.group(1).decode().upper()
        }

        if qualifier['Output'] in self.hdcp_output_status:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetHDMIDTPAttenuation(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        value = round(value, 1)

        if output in self.outputs_sl and LR in LRStates and -100 <= value <= 0:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPAttenuationCmdString = 'wG{}*{}AU\r'.format(60000 + offset, round(value * 10))
            self.__SetHelper('HDMIDTPAttenuation', HDMIDTPAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIDTPAttenuation')

    def UpdateHDMIDTPAttenuation(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if output in self.outputs_sl and LR in LRStates:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPAttenuationCmdString = 'wG{}AU\r'.format(60000 + offset)
            self.__UpdateHelper('HDMIDTPAttenuation', HDMIDTPAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPAttenuation')

    def __MatchHDMIDTPAttenuation(self, match, tag):

        output, LR = divmod(int(match.group(1).decode()) - 60000, 2)

        qualifier = {
            'Output': str(output + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Output'] in self.outputs_sl:
            value = int(match.group(2).decode()) / 10
            if -100 <= value <= 0:
                self.WriteStatus('HDMIDTPAttenuation', value, qualifier)

    def SetHDMIDTPMute(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in self.outputs_sl and LR in LRStates and value in ValueStateValues:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPMuteCmdString = 'wM{}*{}AU\r'.format(60000 + offset, ValueStateValues[value])
            self.__SetHelper('HDMIDTPMute', HDMIDTPMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIDTPMute')

    def UpdateHDMIDTPMute(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if output in self.outputs_sl and LR in LRStates:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPMuteCmdString = 'wM{}AU\r'.format(60000 + offset)
            self.__UpdateHelper('HDMIDTPMute', HDMIDTPMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPMute')

    def __MatchHDMIDTPMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        output, LR = divmod(int(match.group(1).decode()) - 60000, 2)

        qualifier = {
            'Output': str(output + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Output'] in self.outputs_sl:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDMIDTPMute', value, qualifier)

    def SetHDMIDTPPostmixerTrim(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        value = round(value, 1)

        if output in self.outputs_sl and LR in LRStates and -12 <= value <= 12:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPPostmixerTrimCmdString = 'wG{}*{}AU\r'.format(60100 + offset, round(value * 10))
            self.__SetHelper('HDMIDTPPostmixerTrim', HDMIDTPPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIDTPPostmixerTrim')

    def UpdateHDMIDTPPostmixerTrim(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if output in self.outputs_sl and LR in LRStates:
            offset = int(output) * 2 - 2
            if LR == 'Right':
                offset += 1

            HDMIDTPPostmixerTrimCmdString = 'wG{}AU\r'.format(60100 + offset)
            self.__UpdateHelper('HDMIDTPPostmixerTrim', HDMIDTPPostmixerTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDMIDTPPostmixerTrim')

    def __MatchHDMIDTPPostmixerTrim(self, match, tag):

        output, LR = divmod(int(match.group(1).decode()) - 60100, 2)

        qualifier = {
            'Output': str(output + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Output'] in self.outputs_sl:
            value = int(match.group(2).decode()) / 10
            if -12 <= value <= 12:
                self.WriteStatus('HDMIDTPPostmixerTrim', value, qualifier)

    def SetInputAudioSwitchMode(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'Auto':     '0',
            'Digital':  '1',
            'Analog':   '2'
        }

        if 5 <= input_ <= 8 and value in ValueStateValues:
            InputAudioSwitchModeCmdString = 'wI{}*{}AFMT\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSwitchMode')

    def UpdateInputAudioSwitchMode(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 5 <= input_ <= 8:
            InputAudioSwitchModeCmdString = 'wIAFMT\r'
            self.__UpdateHelper('InputAudioSwitchMode', InputAudioSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputAudioSwitchMode')

    def __MatchInputAudioSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Digital',
            '2': 'Analog'
        }

        if tag == 'Single':
            input_ = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('InputAudioSwitchMode', value, {'Input': input_})
        else:
            for input_, value in enumerate(match.group(1).decode()[4:8], 5):
                value = ValueStateValues[value]
                self.WriteStatus('InputAudioSwitchMode', value, {'Input': str(input_)})

    def SetInputConnectorType(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'TP':   '1', # Naming of this value follows PCS
            'HDMI': '2'
        }

        if 5 <= input_ <= 6 and value in ValueStateValues:
            InputConnectorTypeCmdString = 'w{}*{}ITYP\r'.format(input_, ValueStateValues[value])
            self.__SetHelper('InputConnectorType', InputConnectorTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputConnectorType')

    def UpdateInputConnectorType(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 5 <= input_ <= 6:
            InputConnectorTypeCmdString = 'w{}ITYP\r'.format(input_)
            self.__UpdateHelper('InputConnectorType', InputConnectorTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputConnectorType')

    def __MatchInputConnectorType(self, match, tag):

        ValueStateValues = {
            '1': 'TP',
            '2': 'HDMI'
        }

        qualifier = {
            'Input': match.group(1).decode()
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputConnectorType', value, qualifier)

    def SetInputGain(self, value, qualifier):

        input_ = qualifier['Input']

        FormatStates = {
            'Analog':   'G',
            'Digital':  'H'
        }
        format = qualifier['Format']

        LRStates = [
            'Left',
            'Right'
        ]
        LR = qualifier['L/R']

        value = round(value, 1)

        if input_ in self.inputs_sl and format in FormatStates and LR in LRStates and -18 <= value <= 24:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            InputGainCmdString = 'w{}{}*{}AU\r'.format(FormatStates[format], 30000 + offset, round(value * 10))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        input_ = qualifier['Input']

        FormatStates = {
            'Analog':   'G',
            'Digital':  'H'
        }
        format = qualifier['Format']

        LRStates = [
            'Left',
            'Right'
        ]
        LR = qualifier['L/R']

        if input_ in self.inputs_sl and format in FormatStates and LR in LRStates:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            InputGainCmdString = 'w{}{}AU\r'.format(FormatStates[format], 30000 + offset)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        input_, LR = divmod(int(match.group(2).decode()) - 30000, 2)

        FormatStates = {
            'G': 'Analog',
            'H': 'Digital'
        }
        
        qualifier = {
            'Input':    str(input_ + 1),
            'Format':   FormatStates[match.group(1).decode()],
            'L/R':      'Left' if LR == 0 else 'Right'
        }

        if qualifier['Input'] in self.inputs_sl:
            value = int(match.group(3).decode()) / 10
            if -18 <= value <= 24:
                self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        input_ = qualifier['Input']

        LRStates = [
            'Left',
            'Right'
        ]
        LR = qualifier['L/R']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if input_ in self.inputs_sl and LR in LRStates and value in ValueStateValues:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            InputMuteCmdString = 'wM{}*{}AU\r'.format(30000 + offset, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        input_ = qualifier['Input']

        LRStates = [
            'Left',
            'Right'
        ]
        LR = qualifier['L/R']

        if input_ in self.inputs_sl and LR in LRStates:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            InputMuteCmdString = 'wM{}AU\r'.format(30000 + offset)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        input_, LR = divmod(int(match.group(1).decode()) - 30000, 2)

        qualifier = {
            'Input':    str(input_ + 1),
            'L/R':      'Left' if LR == 0 else 'Right'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if qualifier['Input'] in self.inputs_sl:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('InputMute', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        input_ = qualifier['Input']

        if input_ in self.inputs_sl:
            InputSignalCmdString = 'w0LS\r'
            self.__UpdateHelper('InputSignalStatus', InputSignalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalStatus')

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active', 
            '0': 'Not Active'
        }

        if tag == 'Unsolicited':
            input_ = match.group(1).decode()
            if input_ in self.inputs_sl:
                self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(2).decode()], {'Input': input_})
        else:
            for input_, value in enumerate(match.group(1).decode(), 1):
                if str(input_) in self.inputs_sl:
                    self.WriteStatus('InputSignalStatus', ValueStateValues[value], {'Input': str(input_)})

    def SetLogo(self, value, qualifier):

        output = int(qualifier['Output'])

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            'Off': '0'
        }

        if 1 <= output <= 8 and value in ValueStateValues:
            LogoCmdString = 'wE{}*{}LOGO\r'.format(output, ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        output = int(qualifier['Output'])

        if 1 <= output <= 8:
            LogoCmdString = 'wE{}LOGO\r'.format(output)
            self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogo')

    def __MatchLogo(self, match, tag):

        ValueStateValues = {
            '1': '1',
            '2': '2', 
            '3': '3', 
            '4': '4', 
            '5': '5', 
            '6': '6', 
            '7': '7', 
            '8': '8', 
            '9': '9', 
            '10': '10', 
            '11': '11', 
            '12': '12', 
            '13': '13', 
            '14': '14', 
            '15': '15', 
            '16': '16',              
            '0': 'Off'
        }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Logo', value, qualifier)

    def SetMacro(self, value, qualifier):

        macro = int(qualifier['Macro'])

        ValueStateValues = {
            'Run':  'R',
            'Kill': 'K'
        }

        if 1 <= int(qualifier['Macro']) <= 64 and value in ValueStateValues:
            MacroCmdString = 'w{}{}MCRO\r'.format(ValueStateValues[value], macro)
            self.__SetHelper('Macro', MacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def __MatchMacroStatus(self, match, tag):

        macro = int(match.group(2).decode())

        if 1 <= macro <= 64:
            if tag == 'StartedFinished':
                value = 'Macro {} {}.'.format(match.group(1).decode().title(), macro)
                self.WriteStatus('MacroStatus', value, None)
            elif tag == 'FailedKilled':
                value = 'Macro {} {} Step {}.'.format(match.group(1).decode().title(), macro, int(match.group(3).decode()))
                self.WriteStatus('MacroStatus', value, None)

    def SetMatrixIONameCommand(self, value, qualifier):

        TypeStates = {
            'Input':    'NI',
            'Output':   'NO'
        }
        type_ = qualifier['Type']

        number = qualifier['Number']
        name = qualifier['Name']
        if number and name and 0 <= len(name) <= 32 and type_ in TypeStates:
            cmdstring = 'w{0},{1}{2}\r'.format(number, name, TypeStates[type_])
            cmdstring = cmdstring.encode(encoding='iso-8859-1')
            self.__SetHelper('MatrixIONameCommand', cmdstring, None, None)
            if type_ == 'Input': #only write the name if it's for input
                for output in self.outputs_sl:
                    audioVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio'}) # get audio input
                    videoVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Video'}) # get video input
                    if audioVal == number:
                        self.WriteStatus('OutputTieStatusName', name, {'Output': output, 'Tie Type': 'Audio'})
                    if videoVal == number:
                        self.WriteStatus('OutputTieStatusName', name, {'Output': output, 'Tie Type': 'Video'})
                    if audioVal == videoVal == number: # if video input is the same as audio input
                        self.WriteStatus('OutputTieStatusName', name, {'Output': output, 'Tie Type': 'Audio/Video'}) # write AV name
        else:
            self.Discard('Invalid Command for SetMatrixIONameCommand')

    def SetMatrixIONameStatus(self, query, qualifier):

        self.Send(query, pacing=0.1) # 100 pacing between queries

    def __MatchMatrixIONameStatus(self, match, tag):

        TypeStates = {
            'i': 'Input',
            'o': 'Output'
        }

        type_ = TypeStates[match.group(1).decode()]
        
        number = match.group(2).decode()
        value = match.group(3).decode()
        if (type_ == 'Input' and number not in self.inputs_sl) or (type_ == 'Output' and number not in self.outputs_sl):
            return
        
        self.WriteStatus('MatrixIONameStatus', value, {'Type': type_, 'Number': number})
        self.matrix_io_names.setdefault(type_, {}).setdefault(number, value)
        if not self.matrix_io_names_received and \
            len(self.matrix_io_names.get('Input', {})) == len(self.inputs_sl) and \
                len(self.matrix_io_names.get('Output', {})) == len(self.outputs_sl):
            self.matrix_io_names_received = True
        if type_ == 'Input': # only write the name if type is input
            for output in self.outputs_sl:
                audioVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Audio'}) # get audio input
                videoVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': 'Video'}) # get video input
                if audioVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': output, 'Tie Type': 'Audio'})
                if videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': output, 'Tie Type': 'Video'})
                if audioVal == videoVal == number:
                    self.WriteStatus('OutputTieStatusName', value, {'Output': output, 'Tie Type': 'Audio/Video'})

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        TieTypeStates = {
            'Audio':        '$', 
            'Audio/Video':  '!', 
            'Video':        '%'
        }
        tie_type = qualifier['Tie Type']
        
        if input_ in ['0'] + self.inputs_sl and output in self.outputs_a_sl + ['All'] and tie_type in TieTypeStates:
            if output == 'All':
                MatrixTieCommandCmdString = '{}*{}\r'.format(input_,  TieTypeStates[tie_type])
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                MatrixTieCommandCmdString = '{}*{}{}\r'.format(input_, output, TieTypeStates[tie_type])
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetMixpointGain(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        value = round(value, 1)

        if input_ in self.mix_point_inputs and output in self.mix_point_outputs and -100 <= value <= 12:
            MixpointGainCmdString = 'wG2{}{}*{}AU\r'.format(self.mix_point_inputs[input_], self.mix_point_outputs[output], round(value * 10))
            self.__SetHelper('MixpointGain', MixpointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointGain')

    def UpdateMixpointGain(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        if input_ in self.mix_point_inputs and output in self.mix_point_outputs:
            MixpointGainCmdString = 'wG2{}{}AU\r'.format(self.mix_point_inputs[input_], self.mix_point_outputs[output])
            self.__UpdateHelper('MixpointGain', MixpointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixpointGain')

    def __MatchMixpointGain(self, match, tag):

        input_ = match.group(1).decode()
        output = match.group(2).decode()

        if input_ in self.mix_point_inputs_status and output in self.mix_point_outputs_status:
            qualifier = {
                'Input':    self.mix_point_inputs_status[input_],
                'Output':   self.mix_point_outputs_status[output]
            }

            value = int(match.group(3).decode()) / 10
            if -100 <= value <= 12:
                self.WriteStatus('MixpointGain', value, qualifier)

    def SetMixpointMute(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if input_ in self.mix_point_inputs and output in self.mix_point_outputs and value in ValueStateValues:
            MixpointMuteCmdString = 'wM2{}{}*{}AU\r'.format(self.mix_point_inputs[input_], self.mix_point_outputs[output], ValueStateValues[value])
            self.__SetHelper('MixpointMute', MixpointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixpointMute')

    def UpdateMixpointMute(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        if input_ in self.mix_point_inputs and output in self.mix_point_outputs:
            MixpointMuteCmdString = 'wM2{}{}AU\r'.format(self.mix_point_inputs[input_], self.mix_point_outputs[output])
            self.__UpdateHelper('MixpointMute', MixpointMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMixpointMute')

    def __MatchMixpointMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        input_ = match.group(1).decode()
        output = match.group(2).decode()

        if input_ in self.mix_point_inputs_status and output in self.mix_point_outputs_status:
            qualifier = {
                'Input':    self.mix_point_inputs_status[input_],
                'Output':   self.mix_point_outputs_status[output]
            }

            value = ValueStateValues[match.group(3).decode()]
            self.WriteStatus('MixpointMute', value, qualifier)

    def SetOutputAudioSelect(self, value, qualifier):

        output = qualifier['Output']

        ValueStateValues = {
            'Original': '0',
            'From DSP': '1',
            'No Audio': '2'
        }

        if output in self.outputs_sl and value in ValueStateValues:
            OutputAudioSelectCmdString = 'wO{}*{}AFMT\r'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAudioSelect')

    def UpdateOutputAudioSelect(self, value, qualifier):

        output = qualifier['Output']

        if output in self.outputs_sl:
            OutputAudioSelectCmdString = 'wOAFMT\r'
            self.__UpdateHelper('OutputAudioSelect', OutputAudioSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputAudioSelect')

    def __MatchOutputAudioSelect(self, match, tag):

        ValueStateValues = {
            '0': 'Original',
            '1': 'From DSP',
            '2': 'No Audio'
        }

        if tag == 'Single':
            output = match.group(1).decode()
            if output in self.outputs_sl:
                value = ValueStateValues[match.group(2).decode()]
                self.WriteStatus('OutputAudioSelect', value, {'Output': output})
        else:
            for output, value in enumerate(match.group(1).decode(), 1):
                if str(output) in self.outputs_sl:
                    value = ValueStateValues[value]
                    self.WriteStatus('OutputAudioSelect', value, {'Output': str(output)})

    def SetOutputResolution(self, value, qualifier):

        output = qualifier['Output']

        ValueStateValues = {
            '640x480 (60Hz)': '10',
            '800x600 (60Hz)': '11',
            '1024x768 (60Hz)': '12',
            '1280x768 (60Hz)': '13',
            '1280x800 (60Hz)': '14',
            '1280x1024 (60Hz)': '15',
            '1360x768 (60Hz)': '16',
            '1366x768 (60Hz)': '17',
            '1440x900 (60Hz)': '18',
            '1400x1050 (60Hz)': '19',
            '1600x900 (60Hz)': '20',
            '1680x1050 (60Hz)': '21',
            '1600x1200 (60Hz)': '22',
            '1920x1200 (60Hz)': '23',
            '480p (59.94Hz)': '24',
            '480p (60Hz)': '25',
            '576p (50Hz)': '26',
            '720p (25Hz)': '29',
            '720p (29.97Hz)': '30',
            '720p (30Hz)': '31',
            '720p (50Hz)': '32',
            '720p (59.94Hz)': '33',
            '720p (60Hz)': '34',
            '1080i (50Hz)': '35',
            '1080i (59.94Hz)': '36',
            '1080i (60Hz)': '37',
            '1080p (23.98Hz)': '38',
            '1080p (24Hz)': '39',
            '1080p (25Hz)': '40',
            '1080p (29.97Hz)': '41',
            '1080p (30Hz)': '42',
            '1080p (50Hz)': '43',
            '1080p (59.94Hz)': '44',
            '1080p (60Hz)': '45',
            '2048x1080 (23.98Hz)': '46',
            '2048x1080 (24Hz)': '47',
            '2048x1080 (25Hz)': '48',
            '2048x1080 (29.97Hz)': '49',
            '2048x1080 (30Hz)': '50',
            '2048x1080 (50Hz)': '51',
            '2048x1080 (59.94Hz)': '52',
            '2048x1080 (60Hz)': '53',
            '2048x1200 (60Hz)': '54',
            '2048x1536 (60Hz)': '55',
            '2560x1080 (60Hz)': '56',
            '2560x1440 (60Hz)': '57',
            '2560x1600 (60Hz)': '58',
            '3840x2160 (23.98Hz)': '59',
            '3840x2160 (24Hz)': '60',
            '3840x2160 (25Hz)': '61',
            '3840x2160 (29.97Hz)': '62',
            '3840x2160 (30Hz)': '63',
            '3840x2160 (50Hz)': '64',
            '3840x2160 (59.94Hz)': '65',
            '3840x2160 (60Hz)': '66',
            '4096x2160 (23.98Hz)': '69',
            '4096x2160 (24Hz)': '70',
            '4096x2160 (25Hz)': '71',
            '4096x2160 (29.97Hz)': '72',
            '4096x2160 (30Hz)': '73',
            '4096x2160 (50Hz)': '74',
            '4096x2160 (59.94Hz)': '75',
            '4096x2160 (60Hz)': '76'
        }

        if output in self.outputs and value in ValueStateValues:
            OutputResolutionCmdString = 'w{}*{}RATE\r'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        output = qualifier['Output']

        if output in self.outputs:
            OutputResolutionCmdString = 'w{}RATE\r'.format(output)
            self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputResolution')

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10': '640x480 (60Hz)',
            '11': '800x600 (60Hz)',
            '12': '1024x768 (60Hz)',
            '13': '1280x768 (60Hz)',
            '14': '1280x800 (60Hz)',
            '15': '1280x1024 (60Hz)',
            '16': '1360x768 (60Hz)',
            '17': '1366x768 (60Hz)',
            '18': '1440x900 (60Hz)',
            '19': '1400x1050 (60Hz)',
            '20': '1600x900 (60Hz)',
            '21': '1680x1050 (60Hz)',
            '22': '1600x1200 (60Hz)',
            '23': '1920x1200 (60Hz)',
            '24': '480p (59.94Hz)',
            '25': '480p (60Hz)',
            '26': '576p (50Hz)',
            '29': '720p (25Hz)',
            '30': '720p (29.97Hz)',
            '31': '720p (30Hz)',
            '32': '720p (50Hz)',
            '33': '720p (59.94Hz)',
            '34': '720p (60Hz)',
            '35': '1080i (50Hz)',
            '36': '1080i (59.94Hz)',
            '37': '1080i (60Hz)',
            '38': '1080p (23.98Hz)',
            '39': '1080p (24Hz)',
            '40': '1080p (25Hz)',
            '41': '1080p (29.97Hz)',
            '42': '1080p (30Hz)',
            '43': '1080p (50Hz)',
            '44': '1080p (59.94Hz)',
            '45': '1080p (60Hz)',
            '46': '2048x1080 (23.98Hz)',
            '47': '2048x1080 (24Hz)',
            '48': '2048x1080 (25Hz)',
            '49': '2048x1080 (29.97Hz)',
            '50': '2048x1080 (30Hz)',
            '51': '2048x1080 (50Hz)',
            '52': '2048x1080 (59.94Hz)',
            '53': '2048x1080 (60Hz)',
            '54': '2048x1200 (60Hz)',
            '55': '2048x1536 (60Hz)',
            '56': '2560x1080 (60Hz)',
            '57': '2560x1440 (60Hz)',
            '58': '2560x1600 (60Hz)',
            '59': '3840x2160 (23.98Hz)',
            '60': '3840x2160 (24Hz)',
            '61': '3840x2160 (25Hz)',
            '62': '3840x2160 (29.97Hz)',
            '63': '3840x2160 (30Hz)',
            '64': '3840x2160 (50Hz)',
            '65': '3840x2160 (59.94Hz)',
            '66': '3840x2160 (60Hz)',
            '69': '4096x2160 (23.98Hz)',
            '70': '4096x2160 (24Hz)',
            '71': '4096x2160 (25Hz)',
            '72': '4096x2160 (29.97Hz)',
            '73': '4096x2160 (30Hz)',
            '74': '4096x2160 (50Hz)',
            '75': '4096x2160 (59.94Hz)',
            '76': '4096x2160 (60Hz)',
        }

        qualifier = {
            'Output': str(int(match.group(1).decode()))
        }

        if qualifier['Output'] in self.outputs:
            value = ValueStateValues[str(int(match.group(2).decode()))]
            self.WriteStatus('OutputResolution', value, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):

        if not self.matrix_tie_status:
            return
        
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
        output = match.group(1).decode()
        input_ = match.group(2).decode()
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in self.inputs_sl:
                current_tie = self.matrix_tie_status[i][output]
                if i != input_ and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output] = 'Untied'
                elif i == input_:
                    self.matrix_tie_status[i][output] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in self.inputs_sl:
                current_tie = self.matrix_tie_status[i][output]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output] = tietype
                elif input_ == '00' or i != input_:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):

        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video',
        }
        new_input = match.group(4).decode()
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in self.outputs_a_sl:
                for input_ in self.inputs_sl:
                    if input_ == new_input:
                        if self.matrix_tie_status[input_][output] in [op_tie_type, 'Audio/Video']:
                            if output in self.outputs_sl: # for regular outputs 1 - 9, merge tie normally
                                self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            if output in self.outputs_sl: # for regular outputs 1 - 9, write current tie normally
                                self.matrix_tie_status[input_][output] = tietype
                            elif output in self.outputs_a_sl and tietype == 'Audio': # for audio only outputs 10/11 that are audio only, only write if new tie is audio tie
                                self.matrix_tie_status[input_][output] = 'Audio'
                    else:
                        if self.matrix_tie_status[input_][output] == 'Audio/Video':
                            self.matrix_tie_status[input_][output] = op_tie_type
                        elif self.matrix_tie_status[input_][output] != op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Untied'

        elif tietype == 'Audio/Video':
            for output in self.outputs_a_sl:
                for input_ in self.inputs_sl:
                    if input_ == new_input:
                        if output in self.outputs_sl: # for regular outputs 1 - 9
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else: # for audio only outputs 10/11
                            self.matrix_tie_status[input_][output] = 'Audio'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPhantomPower(self, value, qualifier):

        input_ = int(qualifier['Input'])

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }
        
        if 1 <= input_ <= 48 and value in ValueStateValues:
            PhantomPowerCmdString = 'wZ{}*{}AU\r'.format(39999 + input_, ValueStateValues[value])
            self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhantomPower')

    def UpdatePhantomPower(self, value, qualifier):

        input_ = int(qualifier['Input'])

        if 1 <= input_ <= 48:
            PhantomPowerCmdString = 'wZ{}AU\r'.format(39999 + input_)
            self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePhantomPower')

    def __MatchPhantomPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {
            'Input': str(int(match.group(1).decode()) - 39999)
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PhantomPower', value, qualifier)

    def SetPostMatrixGain(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        value = round(value, 1)

        if output in self.outputs_a_sl and LR in LRStates and -100 <= value <= 12:
            offset = int(output) * 2 - 2

            if output in ['10', '11']:
                offset += 6

            if LR == 'Right':
                offset += 1

            PostMatrixGainCmdString = 'wG{}*{}AU\r'.format(50000 + offset, round(value * 10))
            self.__SetHelper('PostMatrixGain', PostMatrixGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPostMatrixGain')

    def UpdatePostMatrixGain(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if output in self.outputs_a_sl and LR in LRStates:
            offset = int(output) * 2 - 2

            if output in ['10', '11']:
                offset += 6

            if LR == 'Right':
                offset += 1

            PostMatrixGainCmdString = 'wG{}AU\r'.format(50000 + offset)
            self.__UpdateHelper('PostMatrixGain', PostMatrixGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePostMatrixGain')

    def __MatchPostMatrixGain(self, match, tag):

        output = int(match.group(1).decode())
        if 50024 <= output <= 50027:
            output -= 6
            
        output, LR = divmod(output - 50000, 2)

        qualifier = {
            'Output': str(output + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Output'] in self.outputs_a_sl:
            value = int(match.group(2).decode()) / 10
            if -100 <= value <= 12:
                self.WriteStatus('PostMatrixGain', value, qualifier)

    def SetPostMatrixMute(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        ValueStateValues = {
            'On':   '1',
            'Off':  '0'
        }

        if output in self.outputs_a_sl and LR in LRStates and value in ValueStateValues:
            offset = int(output) * 2 - 2

            if output in ['10', '11']:
                offset += 6

            if LR == 'Right':
                offset += 1

            PostMatrixMuteCmdString = 'wM{}*{}AU\r'.format(50000 + offset, ValueStateValues[value])
            self.__SetHelper('PostMatrixMute', PostMatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPostMatrixMute')

    def UpdatePostMatrixMute(self, value, qualifier):

        output = qualifier['Output']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if output in self.outputs_a_sl and LR in LRStates:
            offset = int(output) * 2 - 2

            if output in ['10', '11']:
                offset += 6
            
            if LR == 'Right':
                offset += 1

            PostMatrixMuteCmdString = 'wM{}AU\r'.format(50000 + offset)
            self.__UpdateHelper('PostMatrixMute', PostMatrixMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePostMatrixMute')

    def __MatchPostMatrixMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        
        output = int(match.group(1).decode())
        if 50024 <= output <= 50027:
            output -= 6

        output, LR = divmod(output - 50000, 2)

        qualifier = {
            'Output': str(output + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Output'] in self.outputs_a_sl:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('PostMatrixMute', value, qualifier)

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Off':      '0',
            'Mode 1':   '1',
            'Mode 2':   '2'
        }

        if value in ValueStateValues:
            PowerSaveModeCmdString = 'wM{}PSAV\r'.format(ValueStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wMPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '9': 'Low Power (Over Temperature)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdatePowerSupplyVoltage(self, value, qualifier):

        self.UpdateTemperature(None, {'Scale': 'Fahrenheit'})

    def SetPrematrixTrim(self, value, qualifier):

        input_ = qualifier['Input']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        value = round(value, 1)

        if input_ in self.inputs_sl and LR in LRStates and -12 <= value <= 12:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            PrematrixTrimCmdString = 'wG{}*{}AU\r'.format(30100 + offset, round(value * 10))
            self.__SetHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPrematrixTrim')

    def UpdatePrematrixTrim(self, value, qualifier):

        input_ = qualifier['Input']

        LRStates = {
            'Left',
            'Right'
        }
        LR = qualifier['L/R']

        if input_ in self.inputs_sl and LR in LRStates:
            offset = int(input_) * 2 - 2
            if LR == 'Right':
                offset += 1

            PrematrixTrimCmdString = 'wG{}AU\r'.format(30100 + offset)
            self.__UpdateHelper('PrematrixTrim', PrematrixTrimCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePrematrixTrim')

    def __MatchPrematrixTrim(self, match, tag):

        input_, LR = divmod(int(match.group(1).decode()) - 30100, 2)

        qualifier = {
            'Input': str(input_ + 1),
            'L/R': 'Left' if LR == 0 else 'Right'
        }

        if qualifier['Input'] in self.inputs_sl:
            value = int(match.group(2).decode()) / 10
            if -12 <= value <= 12:
                self.WriteStatus('PrematrixTrim', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 64:
            PresetRecallCmdString = '{}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetRefreshMatrix(self, value, qualifier):

        self.UpdateAllMatrixTie(value, qualifier)

    def SetRefreshMatrixIONames(self, value, qualifier):

        for input_ in self.inputs_sl:
            self.SetMatrixIONameStatus( 'w{}NI\r'.format(input_), None)
        for output in self.outputs_sl:
            self.SetMatrixIONameStatus( 'w{}NO\r'.format(output), None)

    def SetScalerPresetRecall(self, value, qualifier):

        output = qualifier['Output']

        if output in self.outputs and 1 <= int(value) <= 32:
            ScalerPresetRecallCmdString = '2*{}*{}.'.format(output, value)
            self.__SetHelper('ScalerPresetRecall', ScalerPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScalerPresetRecall')

    def UpdateTemperature(self, value, qualifier):

        ScaleStates = [
            'Fahrenheit',
            'Celsius'
        ]
        scale = qualifier['Scale']

        if scale in ScaleStates:
            TemperatureCmdString = 'S'
            self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTemperature')

    def __MatchTemperature(self, match, tag):

        self.WriteStatus('PowerSupplyVoltage', round(float(match.group(1).decode()), 2), None)

        self.WriteStatus('Temperature', round(float(match.group(2).decode()), 2), {'Scale': 'Fahrenheit'})
        self.WriteStatus('Temperature', round(float(match.group(3).decode()), 2), {'Scale': 'Celsius'})

        self.WriteStatus('FanSpeed', int(match.group(4).decode()), {'Fan': '1'})
        self.WriteStatus('FanSpeed', int(match.group(5).decode()), {'Fan': '2'})

    def UpdateUSBCallStatus(self, value, qualifier):

        USBCallStatusCmdString = 'wH1UPHN\r'
        self.__UpdateHelper('USBCallStatus', USBCallStatusCmdString, value, qualifier)

    def __MatchUSBCallStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Inactive',
            '1': 'Active'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('USBCallStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        output = qualifier['Output']

        ValueStateValues = {
            'Video':        '1', 
            'Video & Sync': '2', 
            'Off':          '0'
        }

        if output in self.hdcp_output_status + ['All'] and value in ValueStateValues:
            if output == 'All':
                VideoMuteCmdString = 'w{}*VMUT\r'.format(ValueStateValues[value])
            else:
                VideoMuteCmdString = 'w{}*{}VMUT\r'.format(output, ValueStateValues[value])
                
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        output = qualifier['Output']

        if output in self.hdcp_output_status:
            VideoMuteCmdString = 'w{}VMUT\r'.format(output)
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'Video', 
            '2': 'Video & Sync', 
            '0': 'Off'
        }

        qualifier = {
            'Output': match.group(1).decode().upper()
        }

        if qualifier['Output'] in self.hdcp_output_status:
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('VideoMute', value, qualifier)

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
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '18': 'System or command timed out',
            '22': 'Busy',
            '24': 'Privileges violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '28': 'Bad filename or file not found',
            '33': 'Bad file type or size (for logo assignment)'
        }

        value = match.group(1).decode()
        self.Error(['An error occurred: ' + DEVICE_ERROR_CODES.get(value, value + ': Unknown error')])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
        self.matrix_tie_status = None
        self.matrix_io_names = {}
        self.matrix_io_names_received = False

        self.EchoDisabled = True
        self.VerboseDisabled = True

    def extr_15_17511_622(self):
        
        self.inputs = ['1', '2', '3', '4', '5', '6', '7', '8'] # for commands that work for regular inputs only
        self.inputs_sl = self.inputs.copy() # for commands that work for regular inputs and SL 9
        
        self.outputs = ['1', '2', '7', '8'] # for commands that work for regular outputs only
        self.outputs_sl = self.outputs.copy() # for commands that work for regular outputs and SL 9
        self.outputs_a_sl = self.outputs.copy() + ['10'] # for commands that work regular outputs, SL 9, line 10, and amp 11

        self.hdcp_input_status = ['1', '2', '3', '4', '5A', '5B', '6A', '6B', '7', '8'] # for HDCP Input Status (can support SL 9)
        self.hdcp_output_status = ['1A', '1B', '2A', '2B', '7', '8'] # for HDCP Output Status (can support SL 9)


        self.mix_point_inputs = {
            'Output 1 Left':    '00',
            'Output 1 Right':   '01',
            'Output 2 Left':    '02',
            'Output 2 Right':   '03',
            'Output 7 Left':    '12',
            'Output 7 Right':   '13',
            'Output 8 Left':    '14',
            'Output 8 Right':   '15',
            'Output 10 Left':   '24', # DSPro Configurator uses 24 and 25 for AV Matrix Output 10
            'Output 10 Right':  '25',
            'Flex 1':           '28',
            'Flex 2':           '29',
            'Flex 3':           '30',
            'Flex 4':           '31',
            'Flex 5':           '32',
            'Flex 6':           '33',
            'Flex 7':           '34',
            'Flex 8':           '35',
            'Flex 9':           '36',
            'Flex 10':          '37',
            'Flex 11':          '38',
            'Flex 12':          '39',
            'Flex 13':          '40',
            'Flex 14':          '41',
            'Flex 15':          '42',
            'Flex 16':          '43',
            'Flex 17':          '44',
            'Flex 18':          '45',
            'Flex 19':          '46',
            'Flex 20':          '47',
            'Flex 21':          '48',
            'Flex 22':          '49',
            'Flex 23':          '50',
            'Flex 24':          '51',
            'Flex 25':          '52',
            'Flex 26':          '53',
            'Flex 27':          '54',
            'Flex 28':          '55',
            'Flex 29':          '56',
            'Flex 30':          '57',
            'Flex 31':          '58',
            'Flex 32':          '59',
            'Flex 33':          '60',
            'Flex 34':          '61',
            'Flex 35':          '62',
            'Flex 36':          '63',
            'Flex 37':          '64',
            'Flex 38':          '65',
            'Flex 39':          '66',
            'Flex 40':          '67',
            'Flex 41':          '68',
            'Flex 42':          '69',
            'Flex 43':          '70',
            'Flex 44':          '71',
            'Flex 45':          '72',
            'Flex 46':          '73',
            'Flex 47':          '74',
            'Flex 48':          '75'
        }

        self.mix_point_outputs = {
            'Output 1 Left':    '00',
            'Output 1 Right':   '01',
            'Output 2 Left':    '02',
            'Output 2 Right':   '03',
            'Output 7 Left' :   '12',
            'Output 7 Right':   '13',
            'Output 8 Left' :   '14',
            'Output 8 Right':   '15',
            'Line Out 1' :      '24',
            'Line Out 2' :      '25',
            'USB 1 Left':       '28',
            'USB 1 Right':      '29',
            'USB 2 Left':       '30',
            'USB 2 Right':      '31',
            'AT & Exp 1':       '36',
            'AT & Exp 2':       '37',
            'AT & Exp 3':       '38',
            'AT & Exp 4':       '39',
            'AT & Exp 5':       '40',
            'AT & Exp 6':       '41',
            'AT & Exp 7':       '42',
            'AT & Exp 8':       '43',
            'AT & Exp 9':       '44',
            'AT & Exp 10':      '45',
            'AT & Exp 11':      '46',
            'AT & Exp 12':      '47',
            'AT & Exp 13':      '48',
            'AT & Exp 14':      '49',
            'AT & Exp 15':      '50',
            'AT & Exp 16':      '51',
            'AT 17':            '52',
            'AT 18':            '53',
            'AT 19':            '54',
            'AT 20':            '55',
            'AT 21':            '56',
            'AT 22':            '57',
            'AT 23':            '58',
            'AT 24':            '59',
            'AT 25':            '60',
            'AT 26':            '61',
            'AT 27':            '62',
            'AT 28':            '63',
            'AT 29':            '64',
            'AT 30':            '65',
            'AT 31':            '66',
            'AT 32':            '67',
            'V. Send A':        '68',
            'V. Send B':        '69',
            'V. Send C':        '70',
            'V. Send D':        '71',
            'V. Send E':        '72',
            'V. Send F':        '73',
            'V. Send G':        '74',
            'V. Send H':        '75',
            'V. Send I':        '76',
            'V. Send J':        '77',
            'V. Send K':        '78',
            'V. Send L':        '79',
            'V. Send M':        '80',
            'V. Send N':        '81',
            'V. Send O':        '82',
            'V. Send P':        '83'
        }
        self.mix_point_inputs_status = {oid: enum for enum, oid in self.mix_point_inputs.items()}
        self.mix_point_outputs_status = {oid: enum for enum, oid in self.mix_point_outputs.items()}


    def extr_15_17511_622_A(self):

        self.extr_15_17511_622()

        self.outputs_a_sl.append('11')

        mix_point_inputs = {
            'Output 11 Left':   '26', # DSP Configurator Pro uses 26 and 27 for AV Matrix Output 11
            'Output 11 Right':  '27'
        }
        self.mix_point_inputs.update(mix_point_inputs)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_point_inputs.items()})

        mix_point_outputs = {
            'Amp Out 1':    '26', # Amplifier Output Mode must be Stereo for both to appear in DSP Configurator Pro
            'Amp Out 2':    '27'
        }
        self.mix_point_outputs.update(mix_point_outputs)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_point_outputs.items()})


    def extr_15_17511_622_A_SL(self):

        self.extr_15_17511_622_A()

        self.inputs_sl.append('9')
        self.outputs_sl.append('9')
        self.outputs_a_sl.append('9')

        self.hdcp_input_status.append('9')
        self.hdcp_output_status.append('9')

        mix_points = {
            'Output 9 Left':    '16',
            'Output 9 Right':   '17'
        }
        self.mix_point_inputs.update(mix_points)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_points.items()})

        self.mix_point_outputs.update(mix_points)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_points.items()})


    def extr_15_17511_642(self):

        self.extr_15_17511_622()

        self.outputs += ['3', '4']
        self.outputs_sl += ['3', '4']
        self.outputs_a_sl += ['3', '4']

        self.hdcp_output_status += ['3', '4']

        mix_points = {
            'Output 3 Left':    '04',
            'Output 3 Right':   '05',
            'Output 4 Left':    '06',
            'Output 4 Right':   '07'
        }
        self.mix_point_inputs.update(mix_points)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_points.items()})

        self.mix_point_outputs.update(mix_points)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_points.items()})


    def extr_15_17511_642_A(self):

        self.extr_15_17511_642()

        self.outputs_a_sl.append('11')

        mix_point_inputs = {
            'Output 11 Left':   '26', # DSP Configurator Pro uses 26 and 27 for AV Matrix Output 11
            'Output 11 Right':  '27'
        }
        self.mix_point_inputs.update(mix_point_inputs)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_point_inputs.items()})

        mix_point_outputs = {
            'Amp Out 1':    '26', # Amplifier Output Mode must be Stereo for both to appear in DSP Configurator Pro
            'Amp Out 2':    '27'
        }
        self.mix_point_outputs.update(mix_point_outputs)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_point_outputs.items()})

    def extr_15_17511_642_A_SL(self):

        self.extr_15_17511_642_A()

        self.inputs_sl.append('9')
        self.outputs_sl.append('9')
        self.outputs_a_sl.append('9')

        self.hdcp_input_status.append('9')
        self.hdcp_output_status.append('9')

        mix_points = {
            'Output 9 Left':    '16',
            'Output 9 Right':   '17'
        }
        self.mix_point_inputs.update(mix_points)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_points.items()})

        self.mix_point_outputs.update(mix_points)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_points.items()})

    def extr_15_17511_662(self):

        self.extr_15_17511_642()

        self.outputs += ['5', '6']
        self.outputs_sl += ['5', '6']
        self.outputs_a_sl += ['5', '6']

        self.hdcp_output_status += ['5', '6']

        mix_points = {
            'Output 5 Left':    '08',
            'Output 5 Right':   '09',
            'Output 6 Left':    '10',
            'Output 6 Right':   '11'
        }
        self.mix_point_inputs.update(mix_points)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_points.items()})

        self.mix_point_outputs.update(mix_points)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_points.items()})

    def extr_15_17511_662_A(self):

        self.extr_15_17511_662()

        self.outputs_a_sl.append('11')

        mix_point_inputs = {
            'Output 11 Left':   '26', # DSP Configurator Pro uses 26 and 27 for AV Matrix Output 11
            'Output 11 Right':  '27'
        }
        self.mix_point_inputs.update(mix_point_inputs)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_point_inputs.items()})

        mix_point_outputs = {
            'Amp Out 1':    '26', # Amplifier Output Mode must be Stereo for both to appear in DSP Configurator Pro
            'Amp Out 2':    '27'
        }
        self.mix_point_outputs.update(mix_point_outputs)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_point_outputs.items()})

    def extr_15_17511_662_A_SL(self):

        self.extr_15_17511_662_A()

        self.inputs_sl.append('9')
        self.outputs_sl.append('9')
        self.outputs_a_sl.append('9')

        self.hdcp_input_status.append('9')
        self.hdcp_output_status.append('9')

        mix_points = {
            'Output 9 Left':    '16',
            'Output 9 Right':   '17'
        }
        self.mix_point_inputs.update(mix_points)
        self.mix_point_inputs_status.update({oid: enum for enum, oid in mix_points.items()})

        self.mix_point_outputs.update(mix_points)
        self.mix_point_outputs_status.update({oid: enum for enum, oid in mix_points.items()})

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()