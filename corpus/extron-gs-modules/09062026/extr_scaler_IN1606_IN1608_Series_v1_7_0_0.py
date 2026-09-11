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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {
            'IN1606': self.extr_17_15_1606,
            'IN1608': self.extr_17_15_1608,
            'IN1608 MA': self.extr_17_15_1608_MA,
            'IN1608 SA': self.extr_17_15_1608_SA,
            'IN1608 IPCP': self.extr_17_15_1608,
            'IN1608 HDBT': self.extr_17_15_1608,
            'IN1608 MA 70': self.extr_17_15_1608_MA,
            'IN1608 MA 70 HDBT': self.extr_17_15_1608_MA,
            'IN1608 SA HDBT': self.extr_17_15_1608_SA,
            'IN1608 IPCP SA': self.extr_17_15_1608_SA,
            'IN1608 IPCP SA HDBT': self.extr_17_15_1608_SA,
            'IN1608 IPCP MA 70': self.extr_17_15_1608_MA,
            'IN1608 IPCP MA 70 HDBT': self.extr_17_15_1608_MA,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Type', 'Input'], 'Status': {}},
            'AudioFormat': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'GroupBass': {'Status': {}},
            'Ducking': {'Parameters': ['Mic/Line'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'OutputGain': {'Parameters': ['Output'], 'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'DigitalOutputMicLine': {'Status': {}},
            'DigitalOutputProgram': {'Status': {}},
            'OutputFormat': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalType': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'InputPresetRecall': {'Status': {}},
            'InputPresetSave': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MicLineInputGain': {'Parameters': ['Input'], 'Status': {}},
            'MicLineInputMute': {'Parameters': ['Input'], 'Status': {}},
            'MicMixLevel': {'Parameters': ['Mic'], 'Status': {}},
            'MicMixMute': {'Parameters': ['Mic'], 'Status': {}},
            'GroupMicMute': {'Status': {}},
            'GroupMicVolume': {'Status': {}},
            'AnalogOutputMicLine': {'Parameters': ['Output'], 'Status': {}},
            'AnalogOutput1Program': {'Status': {}},
            'AnalogOutput2Program': {'Status': {}},
            'GroupOutputMute': {'Status': {}},
            'OutputResolution': {'Status': {}},
            'GroupOutputVolume': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'GroupProgramMute': {'Status': {}},
            'GroupProgramVolume': {'Status': {}},
            'AmplifiedOutputProgram': {'Status': {}},
            'AmplifiedOutputMicLine': {'Status': {}},
            'ScreenSaverStatus': {'Status': {}},
            'SwitchTransition': {'Status': {}},
            'Temperature': {'Status': {}},
            'TestPattern': {'Status': {}},
            'GroupTreble': {'Status': {}},
            'UserPresetRecall': {'Status': {}},
            'UserPresetSave': {'Status': {}},
            'VariableAnalogOutputMicLine': {'Status': {}},
            'VariableAnalogOutputProgram': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            }

        self.EchoDisabled = True
        self.VerboseDisabled = True       

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH
            self.AddMatchString(compile(b'E([0-2][0-8])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(rb'Aspr0([1-8])\*(1|2)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(rb'Ds[GDgd]30(0|1)(00|02|04|06|08|10|12|14)\*([-+]?[0-9]{1,4})\r\n'), self.__MatchLineInputGain, None)  # only catch Left channels to prevent duplicate matches
            self.AddMatchString(compile(rb'AfmtI0([1-8])\*([0-5])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(compile(rb'Ds[Mm]6000([02456789])\*0?(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(compile(rb'GrpmD0?5\*([-+]?[0-9]{1,3})\r\n'), self.__MatchGroupBass, None)
            self.AddMatchString(compile(rb'Ds[Ee]4480(0|1)\*(0|1)\r'), self.__MatchDucking, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz(0|1)\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(rb'Ds[Gg](6000[02456789])\*([-+]?[0-9]{1,4})\r\n'), self.__MatchOutputGain, None)
            self.AddMatchString(compile(b'Vmt([0-2])\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(compile(rb'HdcpI0([3-8])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(rb'HdcpO([1-3])\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(rb'Vtpo([1-3])\*([0-7])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(compile(b'In0([1-8]) (Aud|RGB|All)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(rb'Typ0([1-8])\*([0-7])\r\n'), self.__MatchInputSignalType, None)
            self.AddMatchString(compile(rb'HdcpE0([1-8])\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'In00 ([01][*01]{10,14})\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(rb'Ds[Gg]4000(0|1)\*([-+]?[0-9]{1,4})\r\n'), self.__MatchMicLineInputGain, None)
            self.AddMatchString(compile(rb'Ds[Mm]4000(0|1)\*0?(0|1)\r\n'), self.__MatchMicLineInputandMicMixMute, None)
            self.AddMatchString(compile(rb'Ds[Gg]4010(0|1)\*(-?[0-9]{1,4})\r\n'), self.__MatchMicMixLevel, None)
            self.AddMatchString(compile(rb'GrpmD0?4\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupMicMute, None)
            self.AddMatchString(compile(rb'GrpmD0?3\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupMicVolume, None)
            self.AddMatchString(compile(b'Rate([1-9][0-9])\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(compile(rb'GrpmD0?7\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupOutputMute, None)
            self.AddMatchString(compile(rb'GrpmD0?8\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupOutputVolume, None)
            self.AddMatchString(compile(b'Psav(0|1)\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(compile(rb'GrpmD0?2\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupProgramMute, None)
            self.AddMatchString(compile(rb'GrpmD0?1\*([-+]?[0-9]{1,4})\r\n'), self.__MatchGroupProgramVolume, None)
            self.AddMatchString(compile(b'SsavS([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(compile(b'Swef(0|1)\r\n'), self.__MatchSwitchTransition, None)
            self.AddMatchString(compile(rb'(\d+)Stat (\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Test0([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(rb'GrpmD0?6\*([-+]?[0-9]{1,3})\r\n'), self.__MatchGroupTreble, None)
            self.AddMatchString(compile(rb'Vmt([1-3])\*([0-2])\r\n'), self.__MatchVideoMute, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
                    'Fill': '1',
                    'Follow': '2'
                    }

        Input = qualifier['Input']
        if Input in self.Inputs:
            commandString = 'w{0}*{1}ASPR\r'.format(Input, AspectRatioStateValues[value])
            self.__SetHelper('AspectRatio', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.Inputs:
            commandString = 'w{0}ASPR\r'.format(Input)
            self.__UpdateHelper('AspectRatio', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        AspectRatioStateNames = {
                    '1': 'Fill',
                    '2': 'Follow'
                    }

        qualifier = {'Input': match.group(1).decode()}
        value = AspectRatioStateNames[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        TypeValues = {
            'Analog': 'G300',
            'LPCM-2Ch': 'D301'
        }

        ValueConstraints = {
            'Min': -18,
            'Max': 24
            }

        Type = qualifier['Type']
        Input = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and Input in self.Inputs and Type in TypeValues:
            self.__SetHelper('LineInputGain', 'w{0}{1:02}*{2}AU\r'.format(TypeValues[Type], int(Input) * 2 - 2, round(value * 10)), value, qualifier)  
            self.__SetHelper('LineInputGain', 'w{0}{1:02}*{2}AU\r'.format(TypeValues[Type], int(Input) * 2 - 1, round(value * 10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        TypeValues = {
            'Analog': 'G300',
            'LPCM-2Ch': 'D301'
        }

        Type = qualifier['Type']
        Input = qualifier['Input']
        if Input in self.Inputs and Type in TypeValues:
            self.__UpdateHelper('LineInputGain', 'w{0}{1:02}AU\r'.format(TypeValues[Type], int(Input) * 2 - 2), value, qualifier)  # send left channel query only
        else:
            self.Discard('Invalid Command for UpdateLineInputGain')

    def __MatchLineInputGain(self, match, tag):

        TypeStates = {
            '0': 'Analog',
            '1': 'LPCM-2Ch'
        }

        qualifier = {}
        qualifier['Type'] = TypeStates[match.group(1).decode()]
        qualifier['Input'] = str(int(match.group(2).decode()) // 2 + 1)
        value = int(match.group(3).decode()) / 10
        self.WriteStatus('LineInputGain', value, qualifier)

    def SetAudioFormat(self, value, qualifier):

        AudioFormatStateValues = {
                    'Analog': '1',
                    'LPCM-2Ch': '2',
                    'Multi-Ch': '3',
                    'LPCM-2Ch Auto': '4',
                    'Multi-Ch Auto': '5',
                    'None': '0'
                    }

        Input = qualifier['Input']
        if Input in self.Inputs:
            valueStates = AudioFormatStateValues[value]
            if Input in self.AnalogInputs:
                if valueStates in ['1', '0']:
                    commandString = 'wI{0}*{1}AFMT\r'.format(Input, valueStates)
                    self.__SetHelper('AudioFormat', commandString, value, qualifier)
                else:
                    self.Discard('Invalid Command for SetAudioFormat')
            else:
                commandString = 'wI{0}*{1}AFMT\r'.format(Input, valueStates)
                self.__SetHelper('AudioFormat', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.Inputs:
            commandString = 'wI{0}AFMT\r'.format(Input)
            self.__UpdateHelper('AudioFormat', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioFormat')

    def __MatchAudioFormat(self, match, tag):

        AudioFormatStateNames = {
                    '1': 'Analog',
                    '2': 'LPCM-2Ch',
                    '3': 'Multi-Ch',
                    '4': 'LPCM-2Ch Auto',
                    '5': 'Multi-Ch Auto',
                    '0': 'None'
                    }

        qualifier = {'Input': match.group(1).decode()}
        value = AudioFormatStateNames[match.group(2).decode()]
        self.WriteStatus('AudioFormat', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        Output = qualifier['Output']
        if Output in self.AudioOutputStates:
            AudioMuteCmdString = 'wM{0}*{1}AU\r'.format(self.AudioOutputStates[Output], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        Output = qualifier['Output']
        if Output in self.AudioOutputStates:
            AudioMuteCmdString = 'wM{0}AU\r'.format(self.AudioOutputStates[Output])
            self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Output': self.OutputQualifierNames[str(int(match.group(1).decode()) + 60000)]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageStateValues = {
                    'Execute and Fill': '1',
                    'Execute and Follow': '2',
                    'Execute': '0'
                    }

        commandString = '{0}*A'.format(AutoImageStateValues[value])
        self.__SetHelper('AutoImage', commandString, value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Highest Active Input': '1',
            'Lowest Active Input': '2'
        }

        AutoSwitchModeCmdString = 'w{0}AUSW\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetGroupBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -24,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupBassCmdString = 'wD5*{0:+04d}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupBass', GroupBassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBass')

    def UpdateGroupBass(self, value, qualifier):

        GroupBassCmdString = 'wD5GRPM\r'
        self.__UpdateHelper('GroupBass', GroupBassCmdString, value, qualifier)

    def __MatchGroupBass(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupBass', value, None)

    def SetDucking(self, value, qualifier):

        MicLineStates = {
            '1': '0',
            '2': '1'
        }

        ValueStateValues = {
            'Enable': '1',
            'Disable': '0'
        }

        DuckingCmdString = 'we4480{0}*{1}au\r'.format(MicLineStates[qualifier['Mic/Line']], ValueStateValues[value])
        self.__SetHelper('Ducking', DuckingCmdString, value, qualifier)

    def UpdateDucking(self, value, qualifier):

        MicLineStates = {
            '1': '0',
            '2': '1'
        }
        DuckingCmdString = 'we4480{0}au\r'.format(MicLineStates[qualifier['Mic/Line']])
        self.__UpdateHelper('Ducking', DuckingCmdString, value, qualifier)

    def __MatchDucking(self, match, tag):

        MicLineStates = {
            '1': '2',
            '0': '1'
        }

        ValueStateValues = {
            '1': 'Enable',
            '0': 'Disable'
        }

        qualifier = {'Mic/Line': MicLineStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Ducking', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
                    'Mode 1': '1',
                    'Mode 2': '2',
                    'Off': '0'
                    }

        commandString = '{0}X'.format(ExecutiveModeStateValues[value])
        self.__SetHelper('ExecutiveMode', commandString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        commandString = 'X'
        self.__UpdateHelper('ExecutiveMode', commandString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
                    '0': 'Off',
                    '1': 'Mode 1',
                    '2': 'Mode 2'
                    }

        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
                    'On': '1',
                    'Off': '0'
                    }

        commandString = '{0}F'.format(FreezeStateValues[value])
        self.__SetHelper('Freeze', commandString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        self.__UpdateHelper('Freeze', 'F', value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeStateNames = {
                    '0': 'Off',
                    '1': 'On'
                    }

        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if -100 <= value <= 0 and Output in self.AudioOutputStates:
            OutputGainCmdString = 'wG{0}*{1}AU\r'.format(self.AudioOutputStates[Output], round(value * 10))
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputGain')

    def UpdateOutputGain(self, value, qualifier):

        Output = qualifier['Output']
        if Output in self.AudioOutputStates:
            OutputGainCmdString = 'wG{0}AU\r'.format(self.AudioOutputStates[Output])
            self.__UpdateHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputGain')

    def __MatchOutputGain(self, match, tag):

        qualifier = {'Output': self.OutputQualifierNames[match.group(1).decode()]}
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('OutputGain', value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        GlobalVideoMuteStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
            }

        commandString = '{0}B'.format(GlobalVideoMuteStateValues[value])
        self.__SetHelper('GlobalVideoMute', commandString, value, qualifier)

    def UpdateGlobalVideoMute(self, value, qualifier):

        commandString = 'B'
        self.__UpdateHelper('GlobalVideoMute', commandString, value, qualifier)

    def __MatchGlobalVideoMute(self, match, tag):

        GlobalVideoMuteStateNames = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
            }

        value = GlobalVideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('GlobalVideoMute', value, None)
        for i in self.OutputNames:
            self.WriteStatus('VideoMute', value, {'Output': self.OutputNames[i]})

    def UpdateHDCPInputStatus(self, value, qualifier):

        Input = qualifier['Input']
        HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(Input)
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        HDCPInputStatusTypeNames = {
            '0': 'No Source Device Detected',
            '1': 'Source Detected with HDCP',
            '2': 'Source Detected without HDCP'
        }

        qualifier = {'Input': match.group(1).decode()}
        value = HDCPInputStatusTypeNames[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        Output = qualifier['Output']
        if Output in self.OutputValues:
            HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(self.OutputValues[Output])
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, tag):

        HDCPOutputStatusTypeNames = {
            '0': 'No Sink Device Detected',
            '1': 'Sink Detected with HDCP',
            '2': 'Sink Detected without HDCP'
        }

        qualifier = {'Output': self.OutputNames[int(match.group(1))]}
        value = HDCPOutputStatusTypeNames[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetDigitalOutputMicLine(self, value, qualifier):

        ValueStateValues = {
            'Include': '\x1Bm20806*0au\r\x1Bm20807*0au\r\x1Bm20906*0au\r\x1Bm20907*0au\r',
            'Exclude': '\x1Bm20806*1au\r\x1Bm20807*1au\r\x1Bm20906*1au\r\x1Bm20907*1au\r'
        }

        DigitalOutputMicLineCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalOutputMicLine', DigitalOutputMicLineCmdString, value, qualifier)

    def SetDigitalOutputProgram(self, value, qualifier):

        ValueStateValues = {
            'Stereo Program': '\x1Bn50006*0au\r\x1Bn50007*0au\r\x1Bm50006*0au\r\x1Bm50007*0au\r',
            'Dual Mono Program': '\x1Bn50006*1au\r\x1Bn50007*1au\r\x1Bm50006*0au\r\x1Bm50007*0au\r',
            'No Program': '\x1Bm50006*1au\r\x1Bm50007*1au\r'
        }

        DigitalOutputProgramCmdString = ValueStateValues[value]
        self.__SetHelper('DigitalOutputProgram', DigitalOutputProgramCmdString, value, qualifier)

    def SetOutputFormat(self, value, qualifier):

        OutputFormatTypeValues = {
            'Auto': '0',
            'DVI RGB 444': '1',
            'HDMI RGB Full': '2',
            'HDMI RGB Limited': '3',
            'HDMI YUV 444 Full': '4',
            'HDMI YUV 444 Limited': '5',
            'HDMI YUV 422 Full': '6',
            'HDMI YUV 422 Limited': '7'
            }

        Output = qualifier['Output']
        if Output in self.OutputValues:
            commandString = 'w{0}*{1}VTPO\r'.format(self.OutputValues[Output], OutputFormatTypeValues[value])
            self.__SetHelper('OutputFormat', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        Output = qualifier['Output']
        if Output in self.OutputValues:
            commandString = 'w{0}VTPO\r'.format(self.OutputValues[Output])
            self.__UpdateHelper('OutputFormat', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputFormat')

    def __MatchOutputFormat(self, match, tag):

        OutputFormatTypeNames = {
            '0': 'Auto',
            '1': 'DVI RGB 444',
            '2': 'HDMI RGB Full',
            '3': 'HDMI RGB Limited',
            '4': 'HDMI YUV 444 Full',
            '5': 'HDMI YUV 444 Limited',
            '6': 'HDMI YUV 422 Full',
            '7': 'HDMI YUV 422 Limited'
            }

        qualifier = {'Output': self.OutputNames[int(match.group(1))]}
        value = OutputFormatTypeNames[match.group(2).decode()]
        self.WriteStatus('OutputFormat', value, qualifier)

    def SetInput(self, value, qualifier):

        InputTypeValues = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
            }
        otherType = None
        Type = qualifier['Type']
        if value in self.Inputs:
            commandString = '{0}{1}'.format(value, InputTypeValues[Type])
            if Type != 'Audio/Video':
                self.WriteStatus('Input', value, qualifier)
                otherType = 'Video' if Type == 'Audio' else 'Audio'
                if self.ReadStatus('Input', {'Type' : otherType}) == value:
                    self.WriteStatus('Input', value, {'Type' : 'Audio/Video'})
                else:
                    self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', value, {'Type' : 'Audio/Video'})
                self.WriteStatus('Input', value, {'Type' : 'Audio'})
                self.WriteStatus('Input', value, {'Type' : 'Video'})
            self.__SetHelper('Input', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputTypeValues = {
            'Audio'      : '$',
            'Video'      : '&',
            }

        Type = qualifier['Type']
        if Type in ['Audio', 'Video']:
            commandString = '{0}'.format(InputTypeValues[Type])
            self.__UpdateHelper('Input', commandString, value, qualifier)
        elif Type == 'Audio/Video':
            self.__UpdateHelper('Input', '$', value, qualifier)
            self.__UpdateHelper('Input', '&', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        InputTypeNames = {
            'Aud' : 'Audio',
            'RGB' : 'Video',
            'All' : 'Audio/Video'
            }

        Type = InputTypeNames[match.group(2).decode()]
        qualifier = {'Type': Type}
        value = str(int(match.group(1).decode()))
        self.WriteStatus('Input', value, qualifier)

        if Type != 'Audio/Video':
            otherType = 'Video' if Type == 'Audio' else 'Audio'
            if self.ReadStatus('Input', {'Type' : otherType}) == value:
                self.WriteStatus('Input', value, {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
        else:
            self.WriteStatus('Input', value, {'Type': 'Video'})
            self.WriteStatus('Input', value, {'Type': 'Audio'})

    def SetInputSignalType(self, value, qualifier):

        InputSignalTypeStateValues = {
                    'RGB'       : '1',
                    'YUV'       : '2',
                    'RGBcvS'    : '3',
                    'S-Video'   : '4',
                    'Composite' : '5'
                    }

        Input = qualifier['Input']
        if Input in self.AnalogInputs:
            valueState = InputSignalTypeStateValues[value]
            commandString = '{0}*{1}\x5C'.format(Input, valueState)
            self.__SetHelper('InputSignalType', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSignalType')

    def UpdateInputSignalType(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.AnalogInputs:
            commandString = '{0}\x5C'.format(Input)
            self.__UpdateHelper('InputSignalType', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalType')

    def __MatchInputSignalType(self, match, tag):

        InputSignalTypeStateNames = {
                    '1' : 'RGB',
                    '2' : 'YUV',
                    '3' : 'RGBcvS',
                    '4' : 'S-Video',
                    '5' : 'Composite',
                    }

        qualifier = {'Input': match.group(1).decode()}
        value = InputSignalTypeStateNames[match.group(2).decode()]
        self.WriteStatus('InputSignalType', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationStateValues = {
                    'On' : '1',
                    'Off' : '0'
                    }

        Input = qualifier['Input']
        if Input in self.Inputs and Input not in self.AnalogInputs:
            commandString = 'wE{0}*{1}HDCP\r'.format(Input, HDCPInputAuthorizationStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        Input = qualifier['Input']
        if Input in self.Inputs and Input not in self.AnalogInputs:
            commandString = 'wE{0}HDCP\r'.format(Input)
            self.__UpdateHelper('HDCPInputAuthorization', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        HDCPInputAuthorizationStateNames = {
                    '0' : 'Off',
                    '1' : 'On'
                    }

        qualifier = {'Input': match.group(1).decode()}
        value = HDCPInputAuthorizationStateNames[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            commandString = '2*{0}\x2E'.format(value)
            self.__SetHelper('InputPresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')
            
    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            commandString = '2*{0}\x2C'.format(value)
            self.__SetHelper('InputPresetSave', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')
            
    def UpdateInputSignalStatus(self, value, qualifier):

        commandString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', commandString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
                    '0' : 'Not Active',
                    '1' : 'Active'
                    }

        values = match.group(1).decode()
        for i in list(range(0,len(self.Inputs))):
            qualifier = {'Input': self.Inputs[i]}
            value = InputSignalStatusStateNames[values[i*2]]
            self.WriteStatus('InputSignalStatus', value, qualifier)

    def SetMicLineInputGain(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Input']
        if -18 <= value <= 60 and Mic in MicValues:
            commandString = 'wG4000{0}*{1}AU\r'.format(MicValues[Mic], round(value * 10))
            self.__SetHelper('MicLineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineInputGain')

    def UpdateMicLineInputGain(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Input']
        if Mic in MicValues:
            commandString = 'wG4000{0}AU\r'.format(MicValues[Mic])
            self.__UpdateHelper('MicLineInputGain', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicLineInputGain')

    def __MatchMicLineInputGain(self, match, tag):

        MicNames = {
            '0' : '1',
            '1' : '2'
            }

        qualifier = {'Input': MicNames[match.group(1).decode()]}
        value = int(match.group(2).decode())/10
        self.WriteStatus('MicLineInputGain', value, qualifier)

    def SetMicMixLevel(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Mic']
        if -100 <= value <= 0 and Mic in MicValues:
            commandString = 'wG4010{0}*{1}AU\r'.format(MicValues[Mic], round(value * 10))
            self.__SetHelper('MicMixLevel', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMixLevel')

    def UpdateMicMixLevel(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }
            
        Mic = qualifier['Mic']
        if Mic in MicValues:
            commandString = 'wG4010{0}AU\r'.format(MicValues[Mic])
            self.__UpdateHelper('MicMixLevel', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicMixLevel')

    def __MatchMicMixLevel(self, match, tag):

        MicNames = {
            '0' : '1',
            '1' : '2'
            }

        qualifier = {'Mic': MicNames[match.group(1).decode()]}
        value = int(match.group(2).decode())/10
        self.WriteStatus('MicMixLevel', value, qualifier)

    def SetMicLineInputMute(self, value, qualifier):

        MicLineInputMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
            }

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Input']
        if Mic in MicValues:
            commandString = 'wM4000{0}*{1}AU\r'.format(MicValues[Mic], MicLineInputMuteStateValues[value])
            self.__SetHelper('MicLineInputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineInputMute')

    def UpdateMicLineInputMute(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Input']
        if Mic in MicValues:
            commandString = 'wM4000{0}AU\r'.format(MicValues[Mic])
            self.__UpdateHelper('MicLineInputMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicLineInputMute')
            
    def SetMicMixMute(self, value, qualifier):

        MicMixMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
            }

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Mic']
        if Mic in MicValues:
            commandString = 'wM4000{0}*{1}AU\r'.format(MicValues[Mic], MicMixMuteStateValues[value])
            self.__SetHelper('MicMixMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMixMute')

    def UpdateMicMixMute(self, value, qualifier):

        MicValues = {
            '1' : '0',
            '2' : '1'
            }

        Mic = qualifier['Mic']
        if Mic in MicValues:
            commandString = 'wM4000{0}AU\r'.format(MicValues[Mic])
            self.__UpdateHelper('MicMixMute', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicMixMute')

    def __MatchMicLineInputandMicMixMute(self, match, tag):

        ValueStateValues = {
            '0' : 'Off',
            '1' : 'On'
            }

        MicNames = {
            '0' : '1',
            '1' : '2'
            }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicLineInputMute', value, {'Input': MicNames[match.group(1).decode()]})
        self.WriteStatus('MicMixMute', value, {'Mic': MicNames[match.group(1).decode()]})

    def SetGroupMicMute(self, value, qualifier):

        GroupMicMuteStateValues = {
            'On' : '1',
            'Off' : '0'
            }

        commandString = 'wD4*{0}GRPM\r'.format(GroupMicMuteStateValues[value])
        self.__SetHelper('GroupMicMute', commandString, value, qualifier)

    def UpdateGroupMicMute(self, value, qualifier):

        commandString = 'wD4GRPM\r'
        self.__UpdateHelper('GroupMicMute', commandString, value, qualifier)

    def __MatchGroupMicMute(self, match, tag):

        GroupMicMuteStateNames = {
            '+00001' : 'On',
            '+00000' : 'Off',
            '1'      : 'On',
            '0'      : 'Off'
            }

        value = GroupMicMuteStateNames[match.group(1).decode()]
        self.WriteStatus('GroupMicMute', value, None)

    def SetGroupMicVolume(self, value, qualifier):

        if -100 <= value <= 0:
            commandString = 'wD3*{0:+06d}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupMicVolume', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMicVolume')

    def UpdateGroupMicVolume(self, value, qualifier):

        commandString = 'wD3GRPM\r'
        self.__UpdateHelper('GroupMicVolume', commandString, value, qualifier)

    def __MatchGroupMicVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupMicVolume', value, None)

    def SetGroupOutputMute(self, value, qualifier):

        GroupOutputMuteStateValues = {
            'On'  : '1',
            'Off' : '0'
            }

        commandString = 'wD7*{0}GRPM\r'.format(GroupOutputMuteStateValues[value])
        self.__SetHelper('GroupOutputMute', commandString, value, qualifier)

    def UpdateGroupOutputMute(self, value, qualifier):

        commandString = 'wD7GRPM\r'
        self.__UpdateHelper('GroupOutputMute', commandString, value, qualifier)

    def __MatchGroupOutputMute(self, match, qualifier):

        GroupOutputMuteStateNames = {
            '+00001' : 'On',
            '+00000' : 'Off',
            '1'      : 'On',
            '0'      : 'Off'
            }

        value = GroupOutputMuteStateNames[match.group(1).decode()]
        self.WriteStatus('GroupOutputMute', value, qualifier)

    def SetAnalogOutputMicLine(self, value, qualifier):

        OutputStates = {
            '1' : '0',
            '2' : '2'
            }

        ValueStateValues = {
            'Include' : '0',
            'Exclude' : '1'
            }

        Output = qualifier['Output']
        AnalogOutputMicLineCmdString = '\x1Bm2080{0}*{1}au\r\x1Bm2090{0}*{1}au\r'.format(OutputStates[Output], ValueStateValues[value])
        self.__SetHelper('AnalogOutputMicLine', AnalogOutputMicLineCmdString, value, qualifier)
        
    def SetAnalogOutput1Program(self, value, qualifier):

        ValueStateValues = {
            'Left Program' : '\x1Bn50000*0au\r\x1Bm50000*0au\r\x1Bm50001*1au\r',
            'L+R Program (Mono)' : '\x1Bn50000*1au\r\x1Bm50000*0au\r\x1Bm50001*0au\r',
            'No Program' : '\x1Bm50000*1au\r\x1Bm50001*1au\r'
        }

        AnalogOutput1ProgramCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogOutput1Program', AnalogOutput1ProgramCmdString, value, qualifier)
        
    def SetAnalogOutput2Program(self, value, qualifier):

        ValueStateValues = {
            'Right Program' : '\x1Bn50002*0au\r\x1Bm50002*1au\r\x1Bm50003*0au\r',
            'L+R Program (Mono)' : '\x1Bn50002*1au\r\x1Bm50002*0au\r\x1Bm50003*0au\r',
            'No Program' : '\x1Bm50002*1au\r\x1Bm50003*1au\r'
        }

        AnalogOutput2ProgramCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogOutput2Program', AnalogOutput2ProgramCmdString, value, qualifier)
        
    def SetOutputResolution(self, value, qualifier):

        OutputResolutionStateValues = {
            '640x480 (50Hz)'   : '10',
            '800x600 (50Hz)'   : '13',
            '852x480 (50Hz)'   : '16',
            '1024x768 (50Hz)'  : '19',
            '1024x852 (50Hz)'  : '22',
            '1024x1024 (50Hz)' : '25',
            '1280x768 (50Hz)'  : '28',
            '1280x800 (50Hz)'  : '31',
            '1280x1024 (50Hz)' : '34',
            '1360x765 (50Hz)'  : '37',
            '1360x768 (50Hz)'  : '40',
            '1365x768 (50Hz)'  : '43',
            '1366x768 (50Hz)'  : '46',
            '1365x1024 (50Hz)' : '49',
            '1440x900 (50Hz)'  : '52',
            '1400x1050 (50Hz)' : '55',
            '1600x900 (50Hz)'  : '57',
            '1680x1050 (50Hz)' : '59',
            '1600x1200 (50Hz)' : '61',
            '1920x1200 (50Hz)' : '63',
            '576p (50Hz)'      : '67',
            '720p (50Hz)'      : '71',
            '1080i (50Hz)'     : '74',
            '1080p (50Hz)'     : '82',
            '2048x1080 (50Hz)' : '90',
            '640x480 (60Hz)'   : '11',
            '800x600 (60Hz)'   : '14',
            '852x480 (60Hz)'   : '17',
            '1024x768 (60Hz)'  : '20',
            '1024x852 (60Hz)'  : '23',
            '1024x1024 (60Hz)' : '26',
            '1280x768 (60Hz)'  : '29',
            '1280x800 (60Hz)'  : '32',
            '1280x1024 (60Hz)' : '35',
            '1360x765 (60Hz)'  : '38',
            '1360x768 (60Hz)'  : '41',
            '1365x768 (60Hz)'  : '44',
            '1366x768 (60Hz)'  : '47',
            '1365x1024 (60Hz)' : '50',
            '1440x900 (60Hz)'  : '53',
            '1400x1050 (60Hz)' : '56',
            '1600x900 (60Hz)'  : '58',
            '1680x1050 (60Hz)' : '60',
            '1600x1200 (60Hz)' : '62',
            '1920x1200 (60Hz)' : '64',
            '480p (60Hz)'      : '66',
            '720p (60Hz)'      : '73',
            '1080i (60Hz)'     : '76',
            '1080p (60Hz)'     : '84',
            '2048x1080 (60Hz)' : '92',
            '640x480 (75Hz)'   : '12',
            '800x600 (75Hz)'   : '15',
            '852x480 (75Hz)'   : '18',
            '1024x768 (75Hz)'  : '21',
            '1024x852 (75Hz)'  : '24',
            '1024x1024 (75Hz)' : '27',
            '1280x768 (75Hz)'  : '30',
            '1280x800 (75Hz)'  : '33',
            '1280x1024 (75Hz)' : '36',
            '1360x765 (75Hz)'  : '39',
            '1360x768 (75Hz)'  : '42',
            '1365x768 (75Hz)'  : '45',
            '1366x768 (75Hz)'  : '48',
            '1365x1024 (75Hz)' : '51',
            '1440x900 (75Hz)'  : '54',
            '1080p (23.98Hz)'  : '77',
            '2048x1080 (23.98Hz)' : '85',
            '1080p (24Hz)'     : '78',
            '2048x1080 (24Hz)' : '86',
            '720p (25Hz)'      : '68',
            '1080p (25Hz)'     : '79',
            '2048x1080 (25Hz)' : '87',
            '720p (29.97Hz)'   : '69',
            '1080p (29.97Hz)'  : '80',
            '2048x1080 (29.97Hz)' : '88',
            '720p (30Hz)'      : '70',
            '1080p (30Hz)'     : '81',
            '2048x1080 (30Hz)' : '89',
            '720p (59.94Hz)'   : '72',
            '1080i (59.94Hz)'  : '75',
            '1080p (59.94Hz)'  : '83',
            '2048x1080 (59.94Hz)' : '91',
            '480p (59.94Hz)' : '65'
        }

        commandString = 'w{0}RATE\r'.format(OutputResolutionStateValues[value])
        self.__SetHelper('OutputResolution', commandString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        commandString = 'wRATE\r'
        self.__UpdateHelper('OutputResolution', commandString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        OutputResolutionStateNames = {
            '10' : '640x480 (50Hz)',
            '13' : '800x600 (50Hz)',
            '16' : '852x480 (50Hz)',
            '19' : '1024x768 (50Hz)',
            '22' : '1024x852 (50Hz)',
            '25' : '1024x1024 (50Hz)',
            '28' : '1280x768 (50Hz)',
            '31' : '1280x800 (50Hz)',
            '34' : '1280x1024 (50Hz)',
            '37' : '1360x765 (50Hz)',
            '40' : '1360x768 (50Hz)',
            '43' : '1365x768 (50Hz)',
            '46' : '1366x768 (50Hz)',
            '49' : '1365x1024 (50Hz)',
            '52' : '1440x900 (50Hz)',
            '55' : '1400x1050 (50Hz)',
            '57' : '1600x900 (50Hz)',
            '59' : '1680x1050 (50Hz)',
            '61' : '1600x1200 (50Hz)',
            '63' : '1920x1200 (50Hz)',
            '67' : '576p (50Hz)',
            '71' : '720p (50Hz)',
            '74' : '1080i (50Hz)',
            '82' : '1080p (50Hz)',
            '90' : '2048x1080 (50Hz)',
            '11' : '640x480 (60Hz)',
            '14' : '800x600 (60Hz)',
            '17' : '852x480 (60Hz)',
            '20' : '1024x768 (60Hz)',
            '23' : '1024x852 (60Hz)',
            '26' : '1024x1024 (60Hz)',
            '29' : '1280x768 (60Hz)',
            '32' : '1280x800 (60Hz)',
            '35' : '1280x1024 (60Hz)',
            '38' : '1360x765 (60Hz)',
            '41' : '1360x768 (60Hz)',
            '44' : '1365x768 (60Hz)',
            '47' : '1366x768 (60Hz)',
            '50' : '1365x1024 (60Hz)',
            '53' : '1440x900 (60Hz)',
            '56' : '1400x1050 (60Hz)',
            '58' : '1600x900 (60Hz)',
            '60' : '1680x1050 (60Hz)',
            '62' : '1600x1200 (60Hz)',
            '64' : '1920x1200 (60Hz)',
            '66' : '480p (60Hz)',
            '73' : '720p (60Hz)',
            '76' : '1080i (60Hz)',
            '84' : '1080p (60Hz)',
            '92' : '2048x1080 (60Hz)',
            '12' : '640x480 (75Hz)',
            '15' : '800x600 (75Hz)',
            '18' : '852x480 (75Hz)',
            '21' : '1024x768 (75Hz)',
            '24' : '1024x852 (75Hz)',
            '27' : '1024x1024 (75Hz)',
            '30' : '1280x768 (75Hz)',
            '33' : '1280x800 (75Hz)',
            '36' : '1280x1024 (75Hz)',
            '39' : '1360x765 (75Hz)',
            '42' : '1360x768 (75Hz)',
            '45' : '1365x768 (75Hz)',
            '48' : '1366x768 (75Hz)',
            '51' : '1365x1024 (75Hz)',
            '54' : '1440x900 (75Hz)',
            '77' : '1080p (23.98Hz)',
            '85' : '2048x1080 (23.98Hz)',
            '78' : '1080p (24Hz)',
            '86' : '2048x1080 (24Hz)',
            '68' : '720p (25Hz)',
            '79' : '1080p (25Hz)',
            '87' : '2048x1080 (25Hz)',
            '69' : '720p (29.97Hz)',
            '80' : '1080p (29.97Hz)',
            '88' : '2048x1080 (29.97Hz)',
            '70' : '720p (30Hz)',
            '81' : '1080p (30Hz)',
            '89' : '2048x1080 (30Hz)',
            '72' : '720p (59.94Hz)',
            '75' : '1080i (59.94Hz)',
            '83' : '1080p (59.94Hz)',
            '91' : '2048x1080 (59.94Hz)',
            '65' : '480p (59.94Hz)'
            }

        value = OutputResolutionStateNames[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetGroupOutputVolume(self, value, qualifier):

        if -100 <= value <= 0:
            commandString = 'wD8*{0:+06d}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupOutputVolume', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputVolume')

    def UpdateGroupOutputVolume(self, value, qualifier):

        commandString = 'wD8GRPM\r'
        self.__UpdateHelper('GroupOutputVolume', commandString, value, qualifier)

    def __MatchGroupOutputVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupOutputVolume', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeStateValues = {
            'Off' : '0',
            'On'  : '1'
            }

        commandString = 'w{0}PSAV\r'.format(PowerSaveModeStateValues[value])
        self.__SetHelper('PowerSaveMode', commandString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        commandString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', commandString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        PowerSaveModeStateNames = {
            '0' : 'Off',
            '1' : 'On'
            }

        value = PowerSaveModeStateNames[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def SetGroupProgramMute(self, value, qualifier):

        GroupProgramMuteStateValues = {
            'On' : '1',
            'Off' : '0'
            }
        commandString = 'wD2*{0}GRPM\r'.format(GroupProgramMuteStateValues[value])
        self.__SetHelper('GroupProgramMute', commandString, value, qualifier)

    def UpdateGroupProgramMute(self, value, qualifier):

        commandString = 'wD2GRPM\r'
        self.__UpdateHelper('GroupProgramMute', commandString, value, qualifier)

    def __MatchGroupProgramMute(self, match, tag):

        GroupProgramMuteStateNames = {
            '+00001' : 'On',
            '+00000' : 'Off',
            '1'      : 'On',
            '0'      : 'Off'
            }

        value = GroupProgramMuteStateNames[match.group(1).decode()]
        self.WriteStatus('GroupProgramMute', value, None)

    def SetGroupProgramVolume(self, value, qualifier):

        if -100 <= value <= 0:
            commandString = 'wD1*{0:+06d}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupProgramVolume', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupProgramVolume')

    def UpdateGroupProgramVolume(self, value, qualifier):

        commandString = 'wD1GRPM\r'
        self.__UpdateHelper('GroupProgramVolume', commandString, value, qualifier)

    def __MatchGroupProgramVolume(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupProgramVolume', value, None)

    def SetAmplifiedOutputMicLine(self, value, qualifier):

        ValueStateValues = {
            'Include' : '\x1Bm20808*0au\r\x1Bm20809*0au\r\x1Bm20908*0au\r\x1Bm20909*0au\r',
            'Exclude' : '\x1Bm20808*1au\r\x1Bm20809*1au\r\x1Bm20908*1au\r\x1Bm20909*1au\r'
        }

        AmplifiedOutputMicLineCmdString = ValueStateValues[value]
        self.__SetHelper('AmplifiedOutputMicLine', AmplifiedOutputMicLineCmdString, value, qualifier)
        
    def SetAmplifiedOutputProgram(self, value, qualifier):

        AmplifiedOutputProgramCmdString = self.AmpValueStateValues[value]
        self.__SetHelper('AmplifiedOutputProgram', AmplifiedOutputProgramCmdString, value, qualifier)
        
    def UpdateScreenSaverStatus(self, value, qualifier):

        commandString = 'wSSSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', commandString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ScreenSaverStatusStateNames = {
            '0' : 'Active Input Detected; Timer not running',
            '2' : 'No Active Input; Timer expired; Output sync disabled',
            '1' : 'No Active Input; Timer running; Output sync enabled'
            }

        value = ScreenSaverStatusStateNames[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def SetSwitchTransition(self, value, qualifier):

        SwitchTransitionStateValues = {
            'Cut'  : '0',
            'Fade Through Black' : '1'
            }

        commandString = 'w{0}SWEF\r'.format(SwitchTransitionStateValues[value])
        self.__SetHelper('SwitchTransition', commandString, value, qualifier)

    def UpdateSwitchTransition(self, value, qualifier):

        commandString = 'wSWEF\r'
        self.__UpdateHelper('SwitchTransition', commandString, value, qualifier)

    def __MatchSwitchTransition(self, match, tag):

        SwitchTransitionStateNames = {
            '0' : 'Cut',
            '1' : 'Fade Through Black'
            }

        value = SwitchTransitionStateNames[match.group(1).decode()]
        self.WriteStatus('SwitchTransition', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        TestPatternStateValues = {
                    'Off' : '0',
                    'Crop' : '1',
                    'Alternating Pixels' : '2',
                    'Color Bars' : '3',
                    'Grayscale' : '4',
                    'Blue Mode' : '5',
                    'Audio Test' : '6'
                    }

        commandString = 'w{0}TEST\r'.format(TestPatternStateValues[value])
        self.__SetHelper('TestPattern', commandString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        commandString = 'wTEST\r'
        self.__UpdateHelper('TestPattern', commandString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        TestPatternStateNames = {
                    '0' : 'Off',
                    '1' : 'Crop',
                    '2' : 'Alternating Pixels',
                    '3' : 'Color Bars',
                    '4' : 'Grayscale',
                    '5' : 'Blue Mode',
                    '6' : 'Audio Test'
                    }

        value = TestPatternStateNames[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetGroupTreble(self, value, qualifier):

        ValueConstraints = {
            'Min' : -24,
            'Max' : 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupTrebleCmdString = 'wD6*{0:+04d}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupTreble', GroupTrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTreble')

    def UpdateGroupTreble(self, value, qualifier):

        GroupTrebleCmdString = 'wD6GRPM\r'
        self.__UpdateHelper('GroupTreble', GroupTrebleCmdString, value, qualifier)

    def __MatchGroupTreble(self, match, tag):

        value = int(match.group(1).decode())/10
        self.WriteStatus('GroupTreble', value, None)

    def SetUserPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            commandString = '1*{0}\x2E'.format(value)
            self.__SetHelper('UserPresetRecall', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetRecall')
            
    def SetUserPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            commandString = '1*{0}\x2C'.format(value)
            self.__SetHelper('UserPresetSave', commandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetSave')
            
    def SetVariableAnalogOutputMicLine(self, value, qualifier):

        ValueStateValues = {
            'Include' : '\x1Bm20804*0au\r\x1Bm20805*0au\r\x1Bm20904*0au\r\x1Bm20905*0au\r',
            'Exclude' : '\x1Bm20804*1au\r\x1Bm20805*1au\r\x1Bm20904*1au\r\x1Bm20905*1au\r'
        }

        VariableAnalogOutputMicLineCmdString = ValueStateValues[value]
        self.__SetHelper('VariableAnalogOutputMicLine', VariableAnalogOutputMicLineCmdString, value, qualifier)
        
    def SetVariableAnalogOutputProgram(self, value, qualifier):

        ValueStateValues = {
            'Stereo Program' : '\x1Bn50004*0au\r\x1Bn50005*0au\r\x1Bm50004*0au\r\x1Bm50005*0au\r',
            'Dual Mono Program' : '\x1Bn50004*1au\r\x1Bn50005*1au\r\x1Bm50004*0au\r\x1Bm50005*0au\r',
            'No Program' : '\x1Bm50004*1au\r\x1Bm50005*1au\r'
        }

        VariableAnalogOutputProgramCmdString = ValueStateValues[value]
        self.__SetHelper('VariableAnalogOutputProgram', VariableAnalogOutputProgramCmdString, value, qualifier)
        
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1',
            'Off' : '0',
            'On with Sync' : '2'
        }

        Output = qualifier['Output']
        if Output in self.OutputValues:
            VideoMuteCmdString = '{0}*{1}B'.format(self.OutputValues[Output], ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        Output = qualifier['Output']
        if Output in self.OutputValues:
            VideoMuteCmdString = '{0}*B'.format(self.OutputValues[Output])
            self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off',
            '2' : 'On with Sync'
        }

        qualifier = {'Output': self.OutputNames[int(match.group(1))]}
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
            '01' : 'Invalid input number',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: '+ match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.lastInputStatusQuery = 0
        
    def extr_17_15_1606(self):

        self.Inputs = ['1', '2', '3', '4', '5', '6']
        self.AnalogInputs = ['1', '2']
        self.OutputValues = {
            'A' : 1,
            'B' : 2
            }

        self.OutputNames = {
            1 : 'A',
            2 : 'B'
            }

        self.OutputQualifierNames = {
            '60000' : 'Output 1',
            '60002' : 'Output 2',
            '60004' : 'Left Variable Output',
            '60005' : 'Right Variable Output',
            '60006' : 'Left Digital Output',
            '60007' : 'Right Digital Output'
            }

        self.AudioOutputStates = {
            'Output 1'              : '60000',
            'Output 2'              : '60002',
            'Left Variable Output'  : '60004',
            'Right Variable Output' : '60005',
            'Left Digital Output'   : '60006',
            'Right Digital Output'  : '60007'
        }

    def extr_17_15_1608(self):

        self.Inputs = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.AnalogInputs = ['1', '2']
        self.OutputValues = {
            'A' : 1,
            'B' : 2,
            'C' : 3
            }

        self.OutputNames = {
            1 : 'A',
            2 : 'B',
            3 : 'C'
            }

        self.OutputQualifierNames = {
            '60000' : 'Output 1',
            '60002' : 'Output 2',
            '60004' : 'Left Variable Output',
            '60005' : 'Right Variable Output',
            '60006' : 'Left Digital Output',
            '60007' : 'Right Digital Output'
            }

        self.AudioOutputStates = {
            'Output 1'              : '60000',
            'Output 2'              : '60002',
            'Left Variable Output'  : '60004',
            'Right Variable Output' : '60005',
            'Left Digital Output'   : '60006',
            'Right Digital Output'  : '60007'
        }

    def extr_17_15_1608_MA(self):

        self.Inputs = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.AnalogInputs = ['1', '2']
        self.OutputValues = {
            'A' : 1,
            'B' : 2,
            'C' : 3
            }

        self.OutputNames = {
            1 : 'A',
            2 : 'B',
            3 : 'C'
            }

        self.OutputQualifierNames = {
            '60000' : 'Output 1',
            '60002' : 'Output 2',
            '60004' : 'Left Variable Output',
            '60005' : 'Right Variable Output',
            '60006' : 'Left Digital Output',
            '60007' : 'Right Digital Output',
            '60008' : 'Amplified Output'
            }

        self.AudioOutputStates = {
            'Output 1'              : '60000',
            'Output 2'              : '60002',
            'Left Variable Output'  : '60004',
            'Right Variable Output' : '60005',
            'Left Digital Output'   : '60006',
            'Right Digital Output'  : '60007',
            'Amplified Output'      : '60008'
        }

        self.AmpValueStateValues = {
            'Dual Mono Program' : '\x1Bn50008*1au\r\x1Bn50009*1au\r\x1Bm50008*0au\r\x1Bm50009*0au\r',
            'No Program' : '\x1Bm50008*1au\r\x1Bm50009*1au\r'
        }

    def extr_17_15_1608_SA(self):

        self.Inputs = ['1', '2', '3', '4', '5', '6', '7', '8']
        self.AnalogInputs = ['1', '2']
        self.OutputValues = {
            'A' : 1,
            'B' : 2,
            'C' : 3
            }

        self.OutputNames = {
            1 : 'A',
            2 : 'B',
            3 : 'C'
            }

        self.OutputQualifierNames = {
            '60000' : 'Output 1',
            '60002' : 'Output 2',
            '60004' : 'Left Variable Output',
            '60005' : 'Right Variable Output',
            '60006' : 'Left Digital Output',
            '60007' : 'Right Digital Output',
            '60008' : 'Left Amplified Output',
            '60009' : 'Right Amplified Output'
            }

        self.AudioOutputStates = {
            'Output 1'               : '60000',
            'Output 2'               : '60002',
            'Left Variable Output'   : '60004',
            'Right Variable Output'  : '60005',
            'Left Digital Output'    : '60006',
            'Right Digital Output'   : '60007',
            'Left Amplified Output'  : '60008',
            'Right Amplified Output' : '60009'
        }

        self.AmpValueStateValues = {
            'Stereo Program'    : '\x1Bn50008*0au\r\x1Bn50009*0au\r\x1Bm50008*0au\r\x1Bm50009*0au\r',
            'Dual Mono Program' : '\x1Bn50008*1au\r\x1Bn50009*1au\r\x1Bm50008*0au\r\x1Bm50009*0au\r',
            'No Program'        : '\x1Bm50008*1au\r\x1Bm50009*1au\r'
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
