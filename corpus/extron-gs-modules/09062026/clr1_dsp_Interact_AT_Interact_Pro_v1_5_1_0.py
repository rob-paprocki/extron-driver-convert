from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
from re import compile, search

class DeviceClass:

    def __init__(self, Model):

        self.PasswdPromptCount = 0
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
            'Interact AT': self.clr1_25_104_AT,
            'Interact Pro': self.clr1_25_104_Pro,
        }
        
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'ClearEffect': {'Status': {}},
            'DTMF': {'Status': {}},
            'GlobalMute': {'Status': {}},
            'Hook': {'Status': {}},
            'LineInputGain': {'Parameters': ['LineInput'], 'Status': {}},
            'LineInputMute': {'Parameters': ['LineInput'], 'Status': {}},
            'Matrix': {'Parameters': ['Source', 'Destination'], 'Status': {}},
            'MatrixLevel': {'Parameters': ['Source', 'Destination'], 'Status': {}},
            'MicGain': {'Parameters': ['Mic'], 'Status': {}},
            'MicMute': {'Parameters': ['Mic'], 'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'PhoneReceiveGain': {'Status': {}},
            'PhoneReceiveMute': {'Status': {}},
            'PhoneTransmitGain': {'Status': {}},
            'PhoneTransmitMute': {'Status': {}},
            'Preset': {'Status': {}},
            'ProcessingChannelGain': {'Parameters': ['ProcessingChannel'], 'Status': {}},
            'ProcessingChannelMute': {'Parameters': ['ProcessingChannel'], 'Status': {}},
            'RingerEnable': {'Status': {}},
            'SpeedDial': {'Status': {}},
            'USBInGain': {'Status': {}},
            'USBInMute': {'Status': {}},
            'USBOutGain': {'Status': {}},
            'USBOutMute': {'Status': {}},
            'Version': {'Status': {}},
        }

        self.Matches = {}

        self.deviceUsername = 'Clearone'
        self.devicePassword = 'Interact'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'ERROR'), self.__MatchError, None)
            self.AddMatchString(compile(b'user:\s'), self.__MatchUsername, None)
            self.AddMatchString(compile(b'pass:\s'), self.__MatchPassword, None)
            self.Matches = {
                'AutoAnswer': {'Disabled': True, 'Criteria': [('#{0}{1} AA 1 (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchAutoAnswer, None)]},
                'GlobalMute': {'Disabled': True, 'Criteria': [('#{0}{1} GMUTE M (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchGlobalMute, None)]},
                'Hook': {'Disabled': True, 'Criteria': [('#{0}{1} TE 1 (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchHook, 'TE'),
                                                        ('#{0}{1} RING 1 (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchHook, 'RING')
                                                        ]},
                'ClearEffect': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'CLEAREFFECT \d{1,2} (0|1)').encode(), self.__MatchClearEffect, None)]},
                'LineInputGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) L ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchLineInputGain, None)]},
                'LineInputMute': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'MUTE (\d{1,2}) L (1|0)').encode(), self.__MatchLineInputMute, None)]},
                'MicGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d) M ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchMicGain, None)]},
                'MicMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE (\d) M (1|0)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchMicMute, None)]},
                'OutputGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) O ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchOutputGain, None)]},
                'OutputMute': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'MUTE (\d{1,2}) O (1|0)').encode(), self.__MatchOutputMute, None)]},
                'ProcessingChannelGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN ([A-C]) P ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchProcessingChannelGain, None)]},
                'ProcessingChannelMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE ([A-C]) P (1|0)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchProcessingChannelMute, None)]},
                'Matrix': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'MTRX ([0-9A-C]{1,2} [M|P|L|R|N|W]) ([0-9A-C]{1,2} [H|O|P|T|B|D]) (0|1|2|3|4|6)').encode(), self.__MatchMatrix, None)]},
                'MatrixLevel': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'MTRXLVL ([0-9A-C]{1,2} [M|P|L|R|N|W]) ([0-9A-C]{1,2} [H|O|P|T|B|D]) ([\-0-9]{1,4}\.[0-9]{2})').encode(), self.__MatchMatrixLevel, None)]},
                'PhoneReceiveMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE 1 R (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchPhoneReceiveMute, None)]},
                'PhoneTransmitMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE 1 T (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchPhoneTransmitMute, None)]},
                'PhoneTransmitGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) T ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchPhoneTransmitGain, None)]},
                'PhoneReceiveGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) R ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchPhoneReceiveGain, None)]},
                'RingerEnable': {'Disabled': True, 'Criteria': [('#{0}{1} RINGEREN 1 (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchRingerEnable, None)]},
                'USBInMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE 1 W (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchUSBInMute, None)]},
                'USBOutMute': {'Disabled': True, 'Criteria': [('#{0}{1} MUTE 1 D (0|1)'.format(self.DeviceType, self.DeviceID).encode(), self.__MatchUSBOutMute, None)]},
                'USBOutGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) D ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchUSBOutGain, None)]},
                'USBInGain': {'Disabled': True, 'Criteria': [('#{0}{1} {2}'.format(self.DeviceType, self.DeviceID, 'GAIN (\d{1,2}) W ([\-0-9]{1,4}\.[0-9]{2}) A').encode(), self.__MatchUSBInGain, None)]},
            }
        self.Channels = compile('([0-9]{1,2}|[A-C])')

    def SetUsername(self, value, qualifier):
        if self.deviceUsername is not None:
            self.Send(self.deviceUsername + '\r')
        else:
            self.MissingCredentialsLog('Username')

    def __MatchUsername(self, match, qualifier):
        self.SetUsername(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send(self.devicePassword + '\r')
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, qualifier):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            print('Log in failed. Please supply proper Admin password.')
        self.SetPassword(None, None)

    def SetAutoAnswer(self, value, qualifier):

        AAValues = {
            'On': '1',
            'Off': '0',
        }
        CommandString = 'AA 1 {0}'.format(AAValues[value])
        self.__SetHelper('AutoAnswer', CommandString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        self.__UpdateHelper('AutoAnswer', 'AA 1', value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        AAStates = {
            '1': 'On',
            '0': 'Off'
        }
        value = AAStates[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetClearEffect(self, value, qualifier):

        ClearEffectValues = {
            'Off': '0',
            'On': '1',
        }

        CommandString = 'CLEAREFFECT 1 {0}'.format(ClearEffectValues[value])
        self.__SetHelper('ClearEffect', CommandString, value, qualifier)

    def UpdateClearEffect(self, value, qualifier):

        CommandString = 'CLEAREFFECT 1'
        self.__UpdateHelper('ClearEffect', CommandString, value, qualifier)

    def __MatchClearEffect(self, match, tag):

        ClearEffectStates = {
            '1': 'On',
            '0': 'Off'
        }
        value = ClearEffectStates[match.group(1).decode()]
        self.WriteStatus('ClearEffect', value, None)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789ABCD*#,':
            CommandString = 'DIAL 1 {0}'.format(value)
            self.__SetHelper('DTMF', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetDTMF')

    def SetGlobalMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GlobalMuteCmdString = 'GMUTE M {0}'.format(ValueStateValues[value])
        self.__SetHelper('GlobalMute', GlobalMuteCmdString, value, qualifier)

    def UpdateGlobalMute(self, value, qualifier):

        GlobalMuteCmdString = 'GMUTE M'
        self.__UpdateHelper('GlobalMute', GlobalMuteCmdString, value, qualifier)

    def __MatchGlobalMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GlobalMute', value, None)

    def SetHook(self, value, qualifier):

        if value in ['On', 'Off']:
            TEValues = {
                'On': '0',
                'Off': '1',
            }
            CommandString = 'TE 1 {0}'.format(TEValues[value])
        elif value == 'Flash':
            CommandString = 'HOOK 1'
        elif value == 'Redial':
            CommandString = 'REDIAL 1'
        elif value == 'Dial':
            number = qualifier['Number']
            CommandString = 'DIAL 1 {0}'.format(number)
        self.__SetHelper('Hook', CommandString, value, qualifier)

    def UpdateHook(self, value, qualifier):

        self.__UpdateHelper('Hook', 'TE 1', value, qualifier)

    def __MatchHook(self, match, tag):

        if tag == 'TE':
            TEStates = {
                '0': 'On',
                '1': 'Off'
            }
            value = TEStates[match.group(1).decode()]
        elif tag == 'RING':
            RingStates = {
                '0': 'On',
                '1': 'Ringing'
            }
            value = RingStates[match.group(1).decode()]
        self.WriteStatus('Hook', value, None)

    def SetLineInputGain(self, value, qualifier):

        LineInput = qualifier['LineInput']
        if self.Gain[0] <= value <= self.Gain[1] and self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'GAIN {0} L {1:0.1f} A'.format(LineInput, value)
            self.__SetHelper('LineInputGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'GAIN {0} L'.format(LineInput)
            self.__UpdateHelper('LineInputGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateLineInputGain')

    def __MatchLineInputGain(self, match, tag):

        qualifier = {'LineInput': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('LineInputGain', value, qualifier)

    def SetLineInputMute(self, value, qualifier):

        MuteValues = {'Off': '0', 'On': '1'}
        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'MUTE {0} L {1}'.format(LineInput, MuteValues[value])
            self.__SetHelper('LineInputMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetLineInputMute')

    def UpdateLineInputMute(self, value, qualifier):

        LineInput = qualifier['LineInput']
        if self.LineInputs[0] <= int(LineInput) <= self.LineInputs[1]:
            CommandString = 'MUTE {0} L'.format(LineInput)
            self.__UpdateHelper('LineInputMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateLineInputMute')

    def __MatchLineInputMute(self, match, tag):

        MuteStates = {b'1': 'On', b'0': 'Off'}
        qualifier = {'LineInput': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('LineInputMute', value, qualifier)

    def SetMatrix(self, value, qualifier):

        MatrixValues = {
            'Cross point off': '0',
            'Cross point on': '1',
            'Gated': '4',
        }

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        CommandString = 'MTRX {0} {1} {2}'.format(self.SourceConstraints[Source], self.DestinationConstraints[Destination], MatrixValues[value])
        self.__SetHelper('Matrix', CommandString, value, qualifier)

    def UpdateMatrix(self, value, qualifier):

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        CommandString = 'MTRX {0} {1}'.format(self.SourceConstraints[Source], self.DestinationConstraints[Destination])
        self.__UpdateHelper('Matrix', CommandString, value, qualifier)

    def __MatchMatrix(self, match, tag):

        MatrixStates = {
            '0': 'Cross point off',
            '1': 'Cross point on',
            '4': 'Gated',
            '6': 'Routing Prohibited'
        }

        Source = match.group(1).decode()
        Destination = match.group(2).decode()
        qualifier = {'Source': self.SourceStates[Source], 'Destination': self.DestinationStates[Destination]}
        value = MatrixStates[match.group(3).decode()]
        self.WriteStatus('Matrix', value, qualifier)

    def SetMatrixLevel(self, value, qualifier):

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        if -18 <= value <= 0:
            CommandString = 'MTRXLVL {0} {1} {2:0.1f} A'.format(self.SourceConstraints[Source], self.DestinationConstraints[Destination], value)
            self.__SetHelper('MatrixLevel', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetMatrixLevel')

    def UpdateMatrixLevel(self, value, qualifier):

        Source = qualifier['Source']
        Destination = qualifier['Destination']
        CommandString = 'MTRXLVL {0} {1}'.format(self.SourceConstraints[Source], self.DestinationConstraints[Destination])
        self.__UpdateHelper('MatrixLevel', CommandString, value, qualifier)

    def __MatchMatrixLevel(self, match, tag):

        Source = match.group(1).decode()
        Destination = match.group(2).decode()
        qualifier = {'Source': self.SourceStates[Source], 'Destination': self.DestinationStates[Destination]}
        value = float(match.group(3))
        self.WriteStatus('MatrixLevel', value, qualifier)

    def SetMicGain(self, value, qualifier):

        Mic = qualifier['Mic']
        if self.Gain[0] <= value <= self.Gain[1] and self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'GAIN {0} M {1:0.1f} A'.format(Mic, value)
            self.__SetHelper('MicGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'GAIN {0} M'.format(Mic)
            self.__UpdateHelper('MicGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateMicGain')

    def __MatchMicGain(self, match, tag):

        qualifier = {'Mic': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('MicGain', value, qualifier)

    def SetMicMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }
        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'MUTE {0} M {1}'.format(Mic, MuteValues[value])
            self.__SetHelper('MicMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        Mic = qualifier['Mic']
        if self.Mics[0] <= int(Mic) <= self.Mics[1]:
            CommandString = 'MUTE {0} M'.format(Mic)
            self.__UpdateHelper('MicMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateMicMute')

    def __MatchMicMute(self, match, tag):

        MuteStates = {b'1': 'On', b'0': 'Off'}
        qualifier = {'Mic': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('MicMute', value, qualifier)

    def SetOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if self.Gain[0] <= value <= self.Gain[1] and self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'GAIN {0} O {1:0.1f} A'.format(Output, value)
            self.__SetHelper('OutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'GAIN {0} O'.format(Output)
            self.__UpdateHelper('OutputGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Output': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('OutputGain', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }
        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'MUTE {0} O {1}'.format(Output, MuteValues[value])
            self.__SetHelper('OutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        Output = qualifier['Output']
        if self.Outputs[0] <= int(Output) <= self.Outputs[1]:
            CommandString = 'MUTE {0} O'.format(Output)
            self.__UpdateHelper('OutputMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }
        qualifier = {'Output': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPhoneReceiveGain(self, value, qualifier):

        if self.Gain[0] <= value <= self.Gain[1]:
            CommandString = 'GAIN 1 R {0:0.1f} A'.format(value)
            self.__SetHelper('PhoneReceiveGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetPhoneReceiveGain')

    def UpdatePhoneReceiveGain(self, value, qualifier):

        CommandString = 'GAIN 1 R'
        self.__UpdateHelper('PhoneReceiveGain', CommandString, value, qualifier)

    def __MatchPhoneReceiveGain(self, match, tag):

        value = float(match.group(2))
        self.WriteStatus('PhoneReceiveGain', value, None)

    def SetPhoneReceiveMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }

        CommandString = 'MUTE 1 R {0}'.format(MuteValues[value])
        self.__SetHelper('PhoneReceiveMute', CommandString, value, qualifier)

    def UpdatePhoneReceiveMute(self, value, qualifier):

        CommandString = 'MUTE 1 R'
        self.__UpdateHelper('PhoneReceiveMute', CommandString, value, qualifier)

    def __MatchPhoneReceiveMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = MuteStates[match.group(1)]
        self.WriteStatus('PhoneReceiveMute', value, None)

    def SetPhoneTransmitGain(self, value, qualifier):

        if self.Gain[0] <= value <= self.Gain[1]:
            CommandString = 'GAIN 1 T {0:0.1f} A'.format(value)
            self.__SetHelper('PhoneTransmitGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetPhoneTransmitGain')

    def UpdatePhoneTransmitGain(self, value, qualifier):

        CommandString = 'GAIN 1 T'
        self.__UpdateHelper('PhoneTransmitGain', CommandString, value, qualifier)

    def __MatchPhoneTransmitGain(self, match, tag):

        value = float(match.group(2))
        self.WriteStatus('PhoneTransmitGain', value, None)

    def SetPhoneTransmitMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }

        CommandString = 'MUTE 1 T {0}'.format(MuteValues[value])
        self.__SetHelper('PhoneTransmitMute', CommandString, value, qualifier)

    def UpdatePhoneTransmitMute(self, value, qualifier):

        CommandString = 'MUTE 1 T'
        self.__UpdateHelper('PhoneTransmitMute', CommandString, value, qualifier)

    def __MatchPhoneTransmitMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = MuteStates[match.group(1)]
        self.WriteStatus('PhoneTransmitMute', value, None)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 4:
            CommandString = 'CPRESET {0}'.format(value)
            self.__SetHelper('Preset', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def SetProcessingChannelGain(self, value, qualifier):

        ProcessingChannel = qualifier['ProcessingChannel']
        if self.Gain[0] <= value <= self.Gain[1] and ProcessingChannel in self.ProcessingChannels:
            CommandString = 'GAIN {0} P {1:0.1f} A'.format(ProcessingChannel, value)
            self.__SetHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetProcessingChannelGain')

    def UpdateProcessingChannelGain(self, value, qualifier):

        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'GAIN {0} P'.format(ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateProcessingChannelGain')

    def __MatchProcessingChannelGain(self, match, tag):

        qualifier = {'ProcessingChannel': match.group(1).decode()}
        value = float(match.group(2))
        self.WriteStatus('ProcessingChannelGain', value, qualifier)

    def SetProcessingChannelMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }
        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'MUTE {0} P {1}'.format(ProcessingChannel, MuteValues[value])
            self.__SetHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetProcessingChannelMute')

    def UpdateProcessingChannelMute(self, value, qualifier):

        ProcessingChannel = qualifier['ProcessingChannel']
        if ProcessingChannel in self.ProcessingChannels:
            CommandString = 'MUTE {0} P'.format(ProcessingChannel)
            self.__UpdateHelper('ProcessingChannelMute', CommandString, value, qualifier)
        else:
            print('Invalid Command for UpdateProcessingChannelMute')

    def __MatchProcessingChannelMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }
        qualifier = {'ProcessingChannel': match.group(1).decode()}
        value = MuteStates[match.group(2)]
        self.WriteStatus('ProcessingChannelMute', value, qualifier)

    def SetSpeedDial(self, value, qualifier):

        if 1 <= int(value) <= 33:
            CommandString = 'SPEEDDIAL 1 {0}'.format(value)
            self.__SetHelper('SpeedDial', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetSpeedDial')

    def SetUSBInGain(self, value, qualifier):

        if self.Gain[0] <= value <= self.Gain[1]:
            CommandString = 'GAIN 1 W {0:0.1f} A'.format(value)
            self.__SetHelper('USBInGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetUSBInGain')

    def UpdateUSBInGain(self, value, qualifier):

        CommandString = 'GAIN 1 W'
        self.__UpdateHelper('USBInGain', CommandString, value, qualifier)

    def __MatchUSBInGain(self, match, tag):

        value = float(match.group(2))
        self.WriteStatus('USBInGain', value, None)

    def SetUSBInMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }

        CommandString = 'MUTE 1 W {0}'.format(MuteValues[value])
        self.__SetHelper('USBInMute', CommandString, value, qualifier)

    def UpdateUSBInMute(self, value, qualifier):

        CommandString = 'MUTE 1 W'
        self.__UpdateHelper('USBInMute', CommandString, value, qualifier)

    def __MatchUSBInMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = MuteStates[match.group(1)]
        self.WriteStatus('USBInMute', value, None)

    def SetUSBOutGain(self, value, qualifier):

        if self.Gain[0] <= value <= self.Gain[1]:
            CommandString = 'GAIN 1 D {0:0.1f} A'.format(value)
            self.__SetHelper('USBOutGain', CommandString, value, qualifier)
        else:
            print('Invalid Command for SetUSBOutGain')

    def UpdateUSBOutGain(self, value, qualifier):

        CommandString = 'GAIN 1 D'
        self.__UpdateHelper('USBOutGain', CommandString, value, qualifier)

    def __MatchUSBOutGain(self, match, tag):

        value = float(match.group(2))
        self.WriteStatus('USBOutGain', value, None)

    def SetUSBOutMute(self, value, qualifier):

        MuteValues = {
            'Off': '0',
            'On': '1',
        }

        CommandString = 'MUTE 1 D {0}'.format(MuteValues[value])
        self.__SetHelper('USBOutMute', CommandString, value, qualifier)

    def UpdateUSBOutMute(self, value, qualifier):

        CommandString = 'MUTE 1 D'
        self.__UpdateHelper('USBOutMute', CommandString, value, qualifier)

    def __MatchUSBOutMute(self, match, tag):

        MuteStates = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = MuteStates[match.group(1)]
        self.WriteStatus('USBOutMute', value, None)

    def SetRingerEnable(self, value, qualifier):

        RingerEnableValues = {
            'On': '1',
            'Off': '0',
        }
        CommandString = 'RINGEREN 1 {0}'.format(RingerEnableValues[value])
        self.__SetHelper('RingerEnable', CommandString, value, qualifier)

    def UpdateRingerEnable(self, value, qualifier):

        CommandString = 'RINGEREN 1'

        self.__UpdateHelper('RingerEnable', CommandString, value, qualifier)

    def __MatchRingerEnable(self, match, tag):

        RingerEnableStates = {
            b'1': 'On',
            b'0': 'Off'
        }
        value = RingerEnableStates[match.group(1)]
        self.WriteStatus('RingerEnable', value, None)

    def SetEnableSerialEcho(self, value, qualifier):
        self.__SetHelper('EnableSerialEcho', '#{0}0 SERECHO 1\r'.format(self.DeviceType))

    def __MatchError(self, match, tag):
        print(match.string.decode())

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send('#{0}0 {1}\r'.format(self.DeviceType, commandstring))

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            if command in self.Matches and self.Matches[command]['Disabled']:
                for criterion in self.Matches[command]['Criteria']:
                    MatchString, Function, Tag = criterion
                    self.AddMatchString(compile(MatchString), Function, Tag)
                self.Matches[command]['Disabled'] = False
            self.Send('#{0}0 {1}\r'.format(self.DeviceType, commandstring))

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def clr1_25_104_Pro(self):

        self.DeviceType = 'K'
        self.LineInputs = (1, 2)
        self.Mics = (1, 16)
        self.Outputs = (1, 8)
        self.ProcessingChannels = 'ABC'
        self.Gain = (-65.0, 20.0)
        self.DeviceID = '0'

        self.SourceConstraints = {
            'Mic Input 1': '1 M',
            'Mic Input 2': '2 M',
            'Mic Input 3': '3 M',
            'Mic Input 4': '4 M',
            'Mic Input 5': '5 M',
            'Mic Input 6': '6 M',
            'Mic Input 7': '7 M',
            'Mic Input 8': '8 M',
            'Mic Input 9': '9 M',
            'Mic Input 10': '10 M',
            'Mic Input 11': '11 M',
            'Mic Input 12': '12 M',
            'Mic Input 13': '13 M',
            'Mic Input 14': '14 M',
            'Mic Input 15': '15 M',
            'Mic Input 16': '16 M',
            'Line Input 1': '1 L',
            'Line Input 2': '2 L',
            'Telco RX': '1 R',
            'USB RX': '1 W',
            'Headset RX': '1 N',
            'Processing A': 'A P',
            'Processing B': 'B P',
            'Processing C': 'C P'
        }

        self.DestinationConstraints = {
            'Output 1': '1 O',
            'Output 2': '2 O',
            'Output 3': '3 O',
            'Output 4': '4 O',
            'Output 5': '5 O',
            'Output 6': '6 O',
            'Output 7': '7 O',
            'Output 8': '8 O',
            'Telco TX': '1 T',
            'USB TX': '1 D',
            'Headset TX': '1 H',
            'Processing A': 'A P',
            'Processing B': 'B P',
            'Processing C': 'C P',
            'Virtual Ref 1': '1 D',
            'Virtual Ref 2': '2 D'
        }

        self.SourceStates = {
            '1 M': 'Mic Input 1',
            '2 M': 'Mic Input 2',
            '3 M': 'Mic Input 3',
            '4 M': 'Mic Input 4',
            '5 M': 'Mic Input 5',
            '6 M': 'Mic Input 6',
            '7 M': 'Mic Input 7',
            '8 M': 'Mic Input 8',
            '9 M': 'Mic Input 9',
            '10 M': 'Mic Input 10',
            '11 M': 'Mic Input 11',
            '12 M': 'Mic Input 12',
            '13 M': 'Mic Input 13',
            '14 M': 'Mic Input 14',
            '15 M': 'Mic Input 15',
            '16 M': 'Mic Input 16',
            '1 L': 'Line Input 1',
            '2 L': 'Line Input 2',
            '1 R': 'Telco RX',
            '1 W': 'USB RX',
            '1 N': 'Headset RX',
            'A P': 'Processing A',
            'B P': 'Processing B',
            'C P': 'Processing C'
        }

        self.DestinationStates = {
            '1 O': 'Output 1',
            '2 O': 'Output 2',
            '3 O': 'Output 3',
            '4 O': 'Output 4',
            '5 O': 'Output 5',
            '6 O': 'Output 6',
            '7 O': 'Output 7',
            '8 O': 'Output 8',
            '1 T': 'Telco TX',
            '1 D': 'USB TX',
            '1 H': 'Headset TX',
            'A P': 'Processing A',
            'B P': 'Processing B',
            'C P': 'Processing C',
            '1 B': 'Virtual Ref 1',
            '2 B': 'Virtual Ref 2'
        }

    def clr1_25_104_AT(self):

        self.DeviceType = 'J'
        self.Mics = (1, 9)
        self.LineInputs = (1, 2)
        self.Outputs = (1, 5)
        self.DeviceID = '0'
        self.Gain = (-14.0, 18.0)

        self.SourceConstraints = {
            'Mic A1': '1 M',
            'Mic A2': '2 M',
            'Mic A3': '3 M',
            'Mic B1': '4 M',
            'Mic B2': '5 M',
            'Mic B3': '6 M',
            'Mic C1': '7 M',
            'Mic C2': '8 M',
            'Mic C3': '9 M',
            'Line Input': '2 L',
            'Telco RX': '1 R',
            'USB RX': '1 W',
        }

        self.DestinationConstraints = {
            'Loud Speaker': '1 O',
            'Line Output': '2 O',
            'Record': '3 O',
            'Telco TX': '1 T',
            'USB TX': '1 D'
        }

        self.SourceStates = {
            '1 M': 'Mic A1',
            '2 M': 'Mic A2',
            '3 M': 'Mic A3',
            '4 M': 'Mic B1',
            '5 M': 'Mic B2',
            '6 M': 'Mic B3',
            '7 M': 'Mic C1',
            '8 M': 'Mic C2',
            '9 M': 'Mic C3',
            '1 L': 'Line Input',
            '1 R': 'Telco RX',
            '1 W': 'USB RX',
        }

        self.DestinationStates = {
            '1 O': 'Loud Speaker',
            '2 O': 'Line Output',
            '3 O': 'Record',
            '1 T': 'Telco TX',
            '1 D': 'USB TX',
        }

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
            
    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
        else:
            print(command, 'does not support Update.')
            
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
        compile_dict = self._compile_list.copy()
        for regexString in compile_dict:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    compile_dict[regexString]['callback'](result, compile_dict[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self, Model)

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Model)
