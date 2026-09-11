from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, match, search


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
        self._DeviceID = 0
        self.SerialEchoEnabled = True

        self.Models = {
            'PSR1212': self.clr1_25_47_PSR1212,
            'XAP 400': self.clr1_25_47_XAP400,
            'XAP 800': self.clr1_25_47_XAP800,
            'XAP TH2': self.clr1_25_47_XAPTH2,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Parameters': ['Device ID'], 'Status': {}},
            'DTMF': {'Parameters': ['Device ID'], 'Status': {}},
            'Hook': {'Parameters': ['Device ID'], 'Status': {}},
            'InputGain': {'Parameters': ['Device ID', 'Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Device ID', 'Input'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Device ID', 'LineInput'], 'Status': {}},
            'LineInputMute': {'Parameters': ['Device ID', 'LineInput'], 'Status': {}},
            'Macro': {'Parameters': ['Device ID'], 'Status': {}},
            'Matrix': {'Parameters': ['Device ID', 'Source', 'SourceGroup', 'Destination', 'DestinationGroup'], 'Status': {}},
            'MicGain': {'Parameters': ['Device ID', 'Mic'], 'Status': {}},
            'MicMute': {'Parameters': ['Device ID', 'Mic'], 'Status': {}},
            'OutputGain': {'Parameters': ['Device ID', 'Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Device ID', 'Output'], 'Status': {}},
            'Preset': {'Parameters': ['Device ID', 'PresetNumber'], 'Status': {}},
            'ProcessingChannelGain': {'Parameters': ['Device ID', 'ProcessingChannel'], 'Status': {}},
            'ProcessingChannelMute': {'Parameters': ['Device ID', 'ProcessingChannel'], 'Status': {}},
            'Ramp': {'Parameters': ['Device ID', 'Channel', 'Group', 'Rate'], 'Status': {}},
            'ReceiveMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Ringer': {'Parameters': ['Device ID'], 'Status': {}},
            'SafetyMute': {'Parameters': ['Device ID'], 'Status': {}},
            'SpeedDial': {'Parameters': ['Device ID'], 'Status': {}},
            'TransmitMute': {'Parameters': ['Device ID'], 'Status': {}},
            'Version': {'Parameters': ['Device ID'], 'Status': {}},
        }

    def AddMatchStringHandler(self):
        self.AddMatchString(compile('#{0}([0-9A-F]) AA 1 ([01])'.format(self.DeviceType).encode()), self.__MatchAutoAnswer, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) (TE|RING) 1 ([01])'.format(self.DeviceType).encode()), self.__MatchHook, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'GAIN (\d{1,2}) I ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchInputGain, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'MUTE (\d{1,2}) I (1|0)').encode()), self.__MatchInputMute, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'GAIN (\d{1,2}) L ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchLineInputGain, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'MUTE (\d{1,2}) L ([01])').encode()), self.__MatchLineInputMute, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'MACRO (\d{1,3})').encode()), self.__MatchMacro, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'MTRX ([0-9A-HO-Z]{1,2}) ([IMPLE]) ([0-9A-HO-Z]{1,2}) ([OPE]) ([0-4])').encode()), self.__MatchMatrix, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'GAIN (\d) M ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchMicGain, None)
        self.AddMatchString(compile('#{0}([0-7]) MUTE (\d) M ([01])'.format(self.DeviceType).encode()), self.__MatchMicMute, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'GAIN (\d{1,2}) O ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchOutputGain, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'MUTE (\d{1,2}) O ([01])').encode()), self.__MatchOutputMute, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'PRESET (\d{1,2}) ([0-2])').encode()), self.__MatchPreset, None)
        self.AddMatchString(compile('#{0}([0-7]) {1}'.format(self.DeviceType, 'GAIN ([A-H]) P ([\-0-9]{1,4}\.[0-9]{2}) A').encode()), self.__MatchProcessingChannelGain, None)
        self.AddMatchString(compile('#{0}([0-7]) MUTE ([A-H]) P ([01])'.format(self.DeviceType).encode()), self.__MatchProcessingChannelMute, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) MUTE 1 R ([01])'.format(self.DeviceType).encode()), self.__MatchReceiveMute, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) RINGER 1 ([01])'.format(self.DeviceType).encode()), self.__MatchRinger, None)
        self.AddMatchString(compile('#{0}([0-7]) SFTYMUTE ([01])'.format(self.DeviceType).encode()), self.__MatchSafetyMute, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) {1}'.format(self.DeviceType, 'SPEEDDIAL 1 (\d{1,2})').encode()), self.__MatchSpeedDial, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) STRING ([0-7])'.format(self.DeviceType).encode()), self.__MatchStringExecution, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) MUTE 1 T ([01])'.format(self.DeviceType).encode()), self.__MatchTransmitMute, None)
        self.AddMatchString(compile('#{0}([0-9A-F]) VER ([\d.]+)\r'.format(self.DeviceType).encode()), self.__MatchVersion, None)
        self.AddMatchString(compile(b'ERROR'), self.__MatchError, None)

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            AutoAnswerCmdString = '#{0}{1} AA 1 {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ValueStateValues[value])
            self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            AutoAnswerCmdString = '#{0}{1} AA 1\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoAnswer')

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutoAnswer', value, qualifier)

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D',
            '*': '*',
            '#': '#',
            ',': ','
        }

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            DTMFCmdString = '#{0}{1} DIAL 1 {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ValueStateValues[value])
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetHook(self, value, qualifier):

        HookCmdString = ''
        DeviceID = qualifier['Device ID']
        
        if DeviceID in self.DeviceIDStates:
            if value in ['On', 'Off', 'Toggle']:
                TEValues = {'On': '0', 'Off': '1', 'Toggle': '2'}
                HookCmdString = 'TE 1 {0}'.format(TEValues[value])
            elif value == 'Flash':
                HookCmdString = 'HOOK 1'
            elif value == 'Redial':
                HookCmdString = 'REDIAL 1'
            elif value == 'Dial':
                Number = qualifier['Number']
                if Number:
                    HookCmdString = 'DIAL 1 {0}'.format(Number)
            if HookCmdString:
                self.__SetHelper('Hook', '#{0}{1} {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], HookCmdString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def UpdateHook(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            self.__UpdateHelper('Hook', '#{0}{1} TE 1\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHook')

    def __MatchHook(self, match, tag):

        TEStateValues = {
            '1': 'Off',
            '0': 'On'
        }

        RingStateValues = {
            '1': 'Ringing',
            '0': 'On'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Type = match.group(2).decode()
        if Type == 'TE':
            value = TEStateValues[match.group(3).decode()]
            self.WriteStatus('Hook', value, qualifier)
        elif Type == 'RING':
            value = RingStateValues[match.group(3).decode()]
            self.WriteStatus('Hook', value, qualifier)

    def SetInputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Input = qualifier['Input']
        if -65.0 <= value <= 20.0 and self.Inputs[0] <= int(Input) <= self.Inputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} I {3:0.1f} A\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Input, value)
            self.__SetHelper('InputGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} I\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Input)
            self.__UpdateHelper('InputGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Input = match.group(2).decode()
        qualifier['Input'] = Input
        value = float(match.group(3).decode())
        if self.Inputs[0] <= int(Input) <= self.Inputs[1] and -65.0 <= value <= 20.0:
            self.WriteStatus('InputGain', value, qualifier)

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1] and DeviceID in self.DeviceIDStates:
            InputMuteCmdString = '#{0}{1} MUTE {2} I {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Input, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Input = qualifier['Input']
        if self.Inputs[0] <= int(Input) <= self.Inputs[1] and DeviceID in self.DeviceIDStates:
            InputMuteCmdString = '#{0}{1} MUTE {2} I\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Input)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Input = match.group(2).decode()
        qualifier['Input'] = Input
        value = ValueStateValues[match.group(3).decode()]
        if self.Inputs[0] <= int(Input) <= self.Inputs[1]:
            self.WriteStatus('InputMute', value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        LineInput = qualifier['LineInput']
        if -65.0 <= value <= 20.0 and self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1] and DeviceID in self.DeviceIDStates:
            LineInputGainCmdString = '#{0}{1} GAIN {2} L {3:0.1f} A\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], LineInput, value)
            self.__SetHelper('LineInputGain', LineInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1] and DeviceID in self.DeviceIDStates:
            LineInputGainCmdString = '#{0}{1} GAIN {2} L\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], LineInput)
            self.__UpdateHelper('LineInputGain', LineInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineInputGain')

    def __MatchLineInputGain(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        LineInput = match.group(2).decode()
        qualifier['LineInput'] = LineInput
        value = float(match.group(3).decode())
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1] and -65.0 <= value <= 20.0:
            self.WriteStatus('LineInputGain', value, qualifier)

    def SetLineInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1] and DeviceID in self.DeviceIDStates:
            LineInputMuteCmdString = '#{0}{1} MUTE {2} L {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], LineInput, ValueStateValues[value])
            self.__SetHelper('LineInputMute', LineInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputMute')

    def UpdateLineInputMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} L\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], LineInput)
            self.__UpdateHelper('LineInputMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLineInputMute')

    def __MatchLineInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        LineInput = match.group(2).decode()
        qualifier['LineInput'] = LineInput
        value = ValueStateValues[match.group(3).decode()]
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            self.WriteStatus('LineInputMute', value, qualifier)

    def SetMacro(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if 1 <= value <= 255 and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MACRO {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], value)
            self.__SetHelper('Macro', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def UpdateMacro(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            MacroCmdString = '#{0}{1} MACRO\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('Macro', MacroCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMacro')

    def __MatchMacro(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = int(match.group(2).decode())
        if 1 <= value <= 255:
            self.WriteStatus('Macro', value, qualifier)

    def SetMatrix(self, value, qualifier):

        SourceGroups = {'Inputs': 'I', 'Mics': 'M', 'Processing': 'P', 'LineInputs': 'L', 'ExpansionBus': 'E'}
        DestinationGroups = {'Outputs': 'O', 'Processing': 'P', 'ExpansionBus': 'E'}
        MatrixValues = {'Off': '0', 'On': '1', 'Toggle': '2', 'Non-Gated': '3', 'Gated': '4'}

        DeviceID = qualifier['Device ID']
        Source = qualifier['Source']
        Destination = qualifier['Destination']
        SourceGroup = SourceGroups[qualifier['SourceGroup']]
        DestinationGroup = DestinationGroups[qualifier['DestinationGroup']]
        if Source in self.Channels and Destination in self.Channels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MTRX {2} {3} {4} {5} {6}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Source, SourceGroup, Destination, DestinationGroup, MatrixValues[value])
            self.__SetHelper('Matrix', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrix')

    def UpdateMatrix(self, value, qualifier):

        SourceGroups = {'Inputs': 'I', 'Mics': 'M', 'Processing': 'P', 'LineInputs': 'L', 'ExpansionBus': 'E'}
        DestinationGroups = {'Outputs': 'O', 'Processing': 'P', 'ExpansionBus': 'E'}

        DeviceID = qualifier['Device ID']
        Source = qualifier['Source']
        Destination = qualifier['Destination']
        SourceGroup = SourceGroups[qualifier['SourceGroup']]
        DestinationGroup = DestinationGroups[qualifier['DestinationGroup']]
        if Source in self.Channels and Destination in self.Channels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MTRX {2} {3} {4} {5}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Source, SourceGroup, Destination, DestinationGroup)
            self.__UpdateHelper('Matrix', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMatrix')

    def __MatchMatrix(self, match, tag):

        SourceGroupStates = {
            'I': 'Inputs',
            'M': 'Mics',
            'P': 'Processing',
            'L': 'LineInputs',
            'E': 'ExpansionBus'
        }

        DestinationGroupStates = {
            'O': 'Outputs',
            'P': 'Processing',
            'E': 'ExpansionBus'
        }

        ValueStateValues = {
            '0': 'Off',
            '1': 'On',
            '2': 'Toggle',
            '3': 'Non-Gated',
            '4': 'Gated'
        }

        DeviceID = self.DeviceIDStates[match.group(1).decode()]
        Source = match.group(2).decode()
        SourceGroup = SourceGroupStates[match.group(3).decode()]
        Destination = match.group(4).decode()
        DestinationGroup = DestinationGroupStates[match.group(5).decode()]
        qualifier = {'Device ID': DeviceID, 'Source': Source, 'SourceGroup': SourceGroup, 'Destination': Destination, 'DestinationGroup': DestinationGroup}
        value = ValueStateValues[match.group(6).decode()]
        if Source in self.Channels and Destination in self.Channels:
            self.WriteStatus('Matrix', value, qualifier)

    def SetMicGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Mic = qualifier['Mic']
        if -65.0 <= value <= 20.0 and self.Mics[0] <= int(Mic) <= self.Mics[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} M {3:0.1f} A\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Mic, value)
            self.__SetHelper('MicGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} M\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Mic)
            self.__UpdateHelper('MicGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicGain')

    def __MatchMicGain(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Mic = match.group(2).decode()
        qualifier['Mic'] = Mic
        value = float(match.group(3).decode())
        if self.Mics[0] <= int(Mic) <= self.Mics[1] and -65.0 <= value <= 20.0:
            self.WriteStatus('MicGain', value, qualifier)

    def SetMicMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} M {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Mic, MuteValues[value])
            self.__SetHelper('MicMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} M\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Mic)
            self.__UpdateHelper('MicMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicMute')

    def __MatchMicMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Mic = match.group(2).decode()
        qualifier['Mic'] = Mic
        value = ValueStateValues[match.group(3).decode()]
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            self.WriteStatus('MicMute', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Output = qualifier['Output']
        if -65.0 <= value <= 20.0 and self.Outputs[0] <= int(Output) <= self.Outputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} O {3:0.1f} A\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Output, value)
            self.__SetHelper('OutputGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} O\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Output)
            self.__UpdateHelper('OutputGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Output = match.group(2).decode()
        qualifier['Output'] = Output
        value = float(match.group(3).decode())
        if self.Outputs[0] <= int(Output) <= self.Outputs[1] and -65.0 <= value <= 20.0:
            self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} O {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Output, MuteValues[value])
            self.__SetHelper('OutputMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1] and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} O\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Output)
            self.__UpdateHelper('OutputMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        Output = match.group(2).decode()
        qualifier['Output'] = Output
        value = ValueStateValues[match.group(3).decode()]
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            self.WriteStatus('OutputMute', value, qualifier)

    def SetPreset(self, value, qualifier):

        PresetValues = {
            'Off': '0',
            'Execute On': '1',
            'Execute Off': '2'
        }

        DeviceID = qualifier['Device ID']
        PresetNumber = qualifier['PresetNumber']
        if 1 <= int(PresetNumber) <= 32 and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} PRESET {2} {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], PresetNumber, PresetValues[value])
            self.__SetHelper('Preset', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        PresetNumber = qualifier['PresetNumber']
        if 1 <= int(PresetNumber) <= 32 and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} PRESET {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], PresetNumber)
            self.__UpdateHelper('Preset', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePreset')

    def __MatchPreset(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Execute On',
            '2': 'Execute Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        PresetNumber = match.group(2).decode()
        qualifier['PresetNumber'] = PresetNumber
        value = ValueStateValues[match.group(3).decode()]
        if 1 <= int(PresetNumber) <= 32:
            self.WriteStatus('Preset', value, qualifier)

    def SetProcessingChannelGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        ProcessingChannel = qualifier['ProcessingChannel']
        if -65.0 <= value <= 20.0 and ProcessingChannel in self.ProcessingChannels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} P {3:0.1f} A\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ProcessingChannel, value)
            self.__SetHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProcessingChannelGain')

    def UpdateProcessingChannelGain(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} GAIN {2} P\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateProcessingChannelGain')

    def __MatchProcessingChannelGain(self, match, tag):

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        ProcessingChannel = match.group(2).decode()
        qualifier['ProcessingChannel'] = ProcessingChannel
        value = float(match.group(3).decode())
        if ProcessingChannel in self.ProcessingChannels:
            self.WriteStatus('ProcessingChannelGain', value, qualifier)

    def SetProcessingChannelMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} P {3}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ProcessingChannel, MuteValues[value])
            self.__SetHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProcessingChannelMute')

    def UpdateProcessingChannelMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE {2} P\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateProcessingChannelMute')

    def __MatchProcessingChannelMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        ProcessingChannel = match.group(2).decode()
        qualifier['ProcessingChannel'] = ProcessingChannel
        value = ValueStateValues[match.group(3).decode()]
        if ProcessingChannel in self.ProcessingChannels:
            self.WriteStatus('ProcessingChannelMute', value, qualifier)

    def SetRamp(self, value, qualifier):

        Groups = {
            'Inputs': 'I',
            'Outputs': 'O',
            'Mics': 'M',
            'LineInputs': 'L',
            'Processing': 'P'
        }

        DeviceID = qualifier['Device ID']
        Channel = qualifier['Channel']
        Group = Groups[qualifier['Group']]
        Rate = qualifier['Rate']

        if -50 <= Rate <= 50 and -65.0 <= value <= 20.0 and Channel in self.Channels and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} RAMP {2} {3} {4} {5:0.1f}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], Channel, Group, Rate, value)
            self.__SetHelper('Ramp', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRamp')

    def SetReceiveMute(self, value, qualifier):

        MuteValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE 1 R {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], MuteValues[value])
            self.__SetHelper('ReceiveMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReceiveMute')

    def UpdateReceiveMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            ReceiveMuteCmdString = '#{0}{1} MUTE 1 R\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('ReceiveMute', ReceiveMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateReceiveMute')

    def __MatchReceiveMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ReceiveMute', value, qualifier)

    def SetRinger(self, value, qualifier):

        RingerValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} RINGER 1 {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], RingerValues[value])
            self.__SetHelper('Ringer', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRinger')

    def UpdateRinger(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            RingerCmdString = '#{0}{1} RINGER 1\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('Ringer', RingerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRinger')

    def __MatchRinger(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Ringer', value, qualifier)

    def SetSafetyMute(self, value, qualifier):

        MuteValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'
        }

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} SFTYMUTE {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], MuteValues[value])
            self.__SetHelper('SafetyMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSafetyMute')

    def UpdateSafetyMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            SafetyMuteCmdString = '#{0}{1} SFTYMUTE\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('SafetyMute', SafetyMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSafetyMute')

    def __MatchSafetyMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SafetyMute', value, qualifier)

    def SetSpeedDial(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if 1 <= int(value) <= 10 and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} SPEEDDIAL 1 {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], value)
            self.__SetHelper('SpeedDial', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeedDial')

    def UpdateSpeedDial(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            SpeedDialCmdString = '#{0}{1} SPEEDDIAL 1\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('SpeedDial', SpeedDialCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSpeedDial')

    def __MatchSpeedDial(self, match, tag):

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
            '10': '10'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SpeedDial', value, qualifier)

    def SetStringExecution(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if 0 <= int(value) <= 7 and DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} STRING {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], value)
            self.__SetHelper('StringExecution', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStringExecution')

    def UpdateStringExecution(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            StringExecutionCmdString = '#{0}{1} STRING\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('StringExecution', StringExecutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateStringExecution')

    def __MatchStringExecution(self, match, tag):

        IDStateValues = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = IDStateValues[match.group(2).decode()]
        self.WriteStatus('StringExecution', value, qualifier)

    def SetTransmitMute(self, value, qualifier):

        MuteValues = {
            'On': '1',
            'Off': '0',
            'Toggle': '2'}

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            CommandString = '#{0}{1} MUTE 1 T {2}\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID], MuteValues[value])
            self.__SetHelper('TransmitMute', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitMute')

    def UpdateTransmitMute(self, value, qualifier):

        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            TransmitMuteCmdString = '#{0}{1} MUTE 1 T\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransmitMute')

    def __MatchTransmitMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('TransmitMute', value, qualifier)

    def UpdateVersion(self, value, qualifier):
        DeviceID = qualifier['Device ID']
        if DeviceID in self.DeviceIDStates:
            VersionCmdString = '#{0}{1} VER\r'.format(self.DeviceType, self.DeviceIDStates[DeviceID])
            self.__UpdateHelper('Version', VersionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVersion')

    def __MatchVersion(self, match, tag):
        
        qualifier = {'Device ID': self.DeviceIDStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('Version', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.SerialEchoEnabled:
                self.Send('#{0}{1} SERECHO 1\r'.format(self.DeviceType, qualifier['Device ID']))
                self.SerialEchoEnabled = False
            self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error(['Invalid/Unexpected Command'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.SerialEchoEnabled = True

    def clr1_25_47_PSR1212(self):

        self.model = 'PSR1212'
        self.DeviceType = '4'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.ProcessingChannels = 'ABCDEFGH'
        self.Channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.DeviceIDStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }
        self.AddMatchStringHandler()

    def clr1_25_47_XAP800(self):

        self.model = 'XAP800'
        self.DeviceType = '5'
        self.Inputs = (1, 12)
        self.LineInputs = (9, 12)
        self.Mics = (1, 8)
        self.Outputs = (1, 12)
        self.ProcessingChannels = 'ABCDEFGH'
        self.Channels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.DeviceIDStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }
        self.AddMatchStringHandler()

    def clr1_25_47_XAPTH2(self):

        self.model = 'XAP TH2'
        self.DeviceType = '6'
        self.DeviceIDStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D',
            'E': 'E',
            'F': 'F'
        }
        self.AddMatchStringHandler()

    def clr1_25_47_XAP400(self):

        self.model = 'XAP 400'
        self.DeviceType = '7'
        self.Inputs = (1, 8)
        self.LineInputs = (5, 8)
        self.Mics = (1, 4)
        self.Outputs = (1, 8)
        self.ProcessingChannels = 'ABCD'
        self.Channels = ['A', 'B', 'C', 'D', '1', '2', '3', '4', '5', '6', '7', '8', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        self.DeviceIDStates = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }
        self.AddMatchStringHandler()

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError('{} does not support Set.'.format(command))

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError('{} does not support Update.'.format(command))

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
            raise KeyError('Invalid command for SubscribeStatus {}'.format(command))

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
            raise KeyError('Invalid command for ReadStatus: {}'.format(command))

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
