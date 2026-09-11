from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

def print(*args):
    printStr = ''
    if len(args) == 1:
        ProgramLog(args[0], 'info') 
    else:
        for s in args:
            printStr += '{} '.format(s)
        ProgramLog(printStr, 'info')

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
            'IN1808': self.extr_17_3966_1808,
            'IN1808 IPCP SA': self.extr_17_3966_1808SA,
            'IN1808 IPCP MA 70': self.extr_17_3966_1808MA,
            'IN1806': self.extr_17_3966_1806,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AudioFormat': {'Parameters': ['Input'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'CECAudioMute': {'Parameters': ['Output'], 'Status': {}},
            'CECPower': {'Parameters': ['Output'], 'Status': {}},
            'CECShowAsActiveSource': {'Parameters': ['Output'], 'Status': {}},
            'CECVolume': {'Parameters': ['Output'], 'Status': {}},
            'EmbeddedInputGain': {'Parameters': ['Input'], 'Status': {}},
            'EmbeddedInputMute': {'Parameters': ['Input'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'GroupBass': {'Status': {}},
            'GroupLineMute': {'Status': {}},
            'GroupLineVolume': {'Status': {}},
            'GroupMicMute': {'Status': {}},
            'GroupMicVolume': {'Status': {}},
            'GroupOutputMute': {'Status': {}},
            'GroupOutputVolume': {'Status': {}},
            'GroupProgramMute': {'Status': {}},
            'GroupProgramVolume': {'Status': {}},
            'GroupTreble': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputPresetRecall': {'Status': {}},
            'InputPresetSave': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalType': {'Parameters': ['Input'], 'Status': {}},
            'LineInputGain': {'Parameters': ['Input'], 'Status': {}},
            'LineInputMute': {'Parameters': ['Input'], 'Status': {}},
            'Logo': {'Status': {}},
            'LoopOut': {'Status': {}},
            'MicLineInputGain': {'Parameters': ['Input'], 'Status': {}},
            'MicLineInputMute': {'Parameters': ['Input'], 'Status': {}},
            'OutputAttenuation': {'Parameters': ['Output'], 'Status': {}},
            'OutputFormat': {'Parameters': ['Output'], 'Status': {}},
            'OutputMute': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'ScreenSaverStatus': {'Status': {}},
            'Temperature': {'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            }

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.lastInputSignalUpdate = 0
        self.CECOutputList = []      

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'Aspr([1-8])\*([1-2])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(rb'AfmtI([1-8])\*([0-5])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(rb'DsG300(0[02468]|1[024])\*([0-9-]{1,4})\r\n'), self.__MatchEmbeddedInputGain, None)  
            self.AddMatchString(re.compile(rb'DsM300(0[02468]|1[024])\*([01])\r\n'), self.__MatchEmbeddedInputMute, None)
            self.AddMatchString(re.compile(b'Exe([0-4])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(rb'Frz1\*([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'Vmt([0-2]) ([0-2]) ([0-2])\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchGlobalVideoMuteEx, None)
            self.AddMatchString(re.compile(rb'GrpmD7\*([0-9-]{1,4})\r\n'), self.__MatchGroupBass, None)
            self.AddMatchString(re.compile(rb'GrpmD6\*([01])\r\n'), self.__MatchGroupLineMute, None)
            self.AddMatchString(re.compile(rb'GrpmD5\*([0-9-]{1,5})\r\n'), self.__MatchGroupLineVolume, None)
            self.AddMatchString(re.compile(rb'GrpmD2\*([01])\r\n'), self.__MatchGroupMicMute, None)
            self.AddMatchString(re.compile(rb'GrpmD1\*([0-9-]{1,5})\r\n'), self.__MatchGroupMicVolume, None)
            self.AddMatchString(re.compile(rb'GrpmD10\*([01])\r\n'), self.__MatchGroupOutputMute, None)
            self.AddMatchString(re.compile(rb'GrpmD9\*([0-9-]{1,5})\r\n'), self.__MatchGroupOutputVolume, None)
            self.AddMatchString(re.compile(rb'GrpmD4\*([01])\r\n'), self.__MatchGroupProgramMute, None)
            self.AddMatchString(re.compile(rb'GrpmD3\*([0-9-]{1,5})\r\n'), self.__MatchGroupProgramVolume, None)
            self.AddMatchString(re.compile(rb'GrpmD8\*([0-9-]{1,4})\r\n'), self.__MatchGroupTreble, None)
            self.AddMatchString(re.compile(rb'HdcpE([2-8])\*([01])'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(rb'HdcpI([1-8])\*([012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(rb'HdcpO([1-3])\*([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(rb'In([1-9])\*1 (All|Aud|Vid)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'In00 ([01*]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(rb'Vtyp([1-8])\*([0-3])\r\n'), self.__MatchInputSignalType, None)
            self.AddMatchString(re.compile(rb'DsG(4000[234]|30016)\*([0-9-]{1,4})\r\n'), self.__MatchLineInputGain, None) 
            self.AddMatchString(re.compile(rb'DsM(4000[234]|30016)\*([01])\r\n'), self.__MatchLineInputMute, None)
            self.AddMatchString(re.compile(rb'LogoE1\*([0-9]|1[0-6])\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(b'Lout([1-8])\r\n'), self.__MatchLoopOut, None)
            self.AddMatchString(re.compile(rb'DsG4000([01])\*([0-9-]{1,4})\r\n'), self.__MatchMicLineInputGain, None)
            self.AddMatchString(re.compile(rb'DsM4000([01])\*([01])\r\n'), self.__MatchMicLineInputMute, None)
            self.AddMatchString(re.compile(rb'DsG600(0[0246789]|10)\*([0-9-]{1,5})\r\n'), self.__MatchOutputAttenuation, None)  
            self.AddMatchString(re.compile(rb'Vtpo([1-3])\*([0123579])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(rb'DsM600(0[0246789]|10)\*([01])\r\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(rb'Rate1\*([0-9]{3})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Psav([0-2])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(rb'SsavS1\*([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(rb'20Stat (\d{2})\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(rb'Test1\*([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(rb'Vmt([1-3])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'E([0-3][0-8])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Fill': '1',
            'Follow': '2'
        }

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            AspectRatioCmdString = 'w{0}*{1}ASPR\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            AspectRatioCmdString = 'w{0}ASPR\r'.format(qualifier['Input'])
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '1': 'Fill',
            '2': 'Follow'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, qualifier)

    def SetAudioFormat(self, value, qualifier):

        ValueStateValues = {
            'Analog Aux': '1',
            'LPCM-2Ch': '2',
            'Multi-Ch': '3',
            'LPCM-2Ch Auto AUX': '4',
            'Multi-Ch Auto AUX': '5',
            'None': '0'
        }

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            AudioFormatCmdString = 'wI{0}*{1}AFMT\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            AudioFormatCmdString = 'wI{0}AFMT\r'.format(qualifier['Input'])
            self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioFormat')

    def __MatchAudioFormat(self, match, tag):

        ValueStateValues = {
            '1': 'Analog Aux',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch',
            '4': 'LPCM-2Ch Auto AUX',
            '5': 'Multi-Ch Auto AUX',
            '0': 'None'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioFormat', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute': '0',
            'Execute and Fill': '1',
            'Execute and Follow': '2'
        }

        AutoImageCmdString = '1*{0}A'.format(ValueStateValues[value])
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeStateValues = {
             'User Defined Priority': 'w1AUSW\r',
             'Input Memory Priority': 'w2AUSW\r',
             'Off': 'w0AUSW\r',
        }

        AutoSwitchModeCmdString = AutoSwitchModeStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, qualifier):

        AutoSwitchModeStateNames = {
            '0': 'Off',
            '1': 'User Defined Priority',
            '2': 'Input Memory Priority',
        }

        AutoSwitchModeCmdString = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', AutoSwitchModeCmdString, qualifier)

    def SetCECAudioMute(self, value, qualifier):

        OutputStates = {
            '1A': '1',
            '1B': '2',
            'Loop Out': '3'
        }

        if qualifier['Output'] in OutputStates:
            output = OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:  
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))
            CECAudioMuteCmdString = 'wO{}*%44%43DCEC\r'.format(output)
            self.__SetHelper('CECAudioMute', CECAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECAudioMute')

    def SetCECPower(self, value, qualifier):

        OutputStates = {
            '1A': '1',
            '1B': '2',
            'Loop Out': '3'
        }

        ValueStateValues = {
            'On': '%04',
            'Off': '%36'
        }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            output = OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECPowerCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECPower', CECPowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECPower')

    def SetCECShowAsActiveSource(self, value, qualifier):

        OutputStates = {
            '1A': '1',
            '1B': '2',
            'Loop Out': '3'
        }

        if qualifier['Output'] in OutputStates:
            output = OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECShowAsActiveSourceCmdString = 'wO{}*\"ShowMe\"DCEC\r'.format(output)
            self.__SetHelper('CECShowAsActiveSource', CECShowAsActiveSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECShowAsActiveSource')

    def SetCECVolume(self, value, qualifier):

        OutputStates = {
            '1A': '1',
            '1B': '2',
            'Loop Out': '3'
        }

        ValueStateValues = {
            'Up': '%44%41',
            'Down': '%44%42'
        }

        if qualifier['Output'] in OutputStates and value in ValueStateValues:
            output = OutputStates[qualifier['Output']]
            if output not in self.CECOutputList:
                self.CECOutputList.append(output)
                self.Send('wO{}*2CCEC\r'.format(output))

            CECVolumeCmdString = 'wO{}*{}DCEC\r'.format(output, ValueStateValues[value])
            self.__SetHelper('CECVolume', CECVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCECVolume')

    def SetEmbeddedInputGain(self, value, qualifier):

        InputStates = {
            '1': ['00', '01'],
            '2': ['02', '03'],
            '3': ['04', '05'],
            '4': ['06', '07'],
            '5': ['08', '09'],
            '6': ['10', '11'],
            '7': ['12', '13'],
            '8': ['14', '15']
        }

        ValueConstraints = {
            'Min': -18,
            'Max': 24
            }

        if 1 <= int(qualifier['Input']) <= self.InputMax and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            self.__SetHelper('EmbeddedInputGain', 'wG300{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], round(value * 10)), value, qualifier)
            self.__SetHelper('EmbeddedInputGain', 'wG300{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], round(value * 10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetEmbeddedInputGain')

    def UpdateEmbeddedInputGain(self, value, qualifier):

        InputStates = {
            '1': '00',
            '2': '02',
            '3': '04',
            '4': '06',
            '5': '08',
            '6': '10',
            '7': '12',
            '8': '14'
        }

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            EmbeddedInputGainCmdString = 'wG300{0}AU\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('EmbeddedInputGain', EmbeddedInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEmbeddedInputGain')

    def __MatchEmbeddedInputGain(self, match, tag):

        InputStates = {
            '00': '1',
            '02': '2',
            '04': '3',
            '06': '4',
            '08': '5',
            '10': '6',
            '12': '7',
            '14': '8'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode()) / 10
        self.WriteStatus('EmbeddedInputGain', value, qualifier)

    def SetEmbeddedInputMute(self, value, qualifier):

        InputStates = {
            '1': ['00', '01'],
            '2': ['02', '03'],
            '3': ['04', '05'],
            '4': ['06', '07'],
            '5': ['08', '09'],
            '6': ['10', '11'],
            '7': ['12', '13'],
            '8': ['14', '15']
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            self.__SetHelper('EmbeddedInputMute', 'wM300{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], ValueStateValues[value]), value, qualifier)  
            self.__SetHelper('EmbeddedInputMute', 'wM300{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetEmbeddedInputMute')

    def UpdateEmbeddedInputMute(self, value, qualifier):

        InputStates = {
            '1': '00',
            '2': '02',
            '3': '04',
            '4': '06',
            '5': '08',
            '6': '10',
            '7': '12',
            '8': '14'
        }

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            EmbeddedInputMuteCmdString = 'wM300{0}AU\r'.format(InputStates[qualifier['Input']])
            self.__UpdateHelper('EmbeddedInputMute', EmbeddedInputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateEmbeddedInputMute')

    def __MatchEmbeddedInputMute(self, match, tag):

        InputStates = {
            '00': '1',
            '02': '2',
            '04': '3',
            '06': '4',
            '08': '5',
            '10': '6',
            '12': '7',
            '14': '8'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('EmbeddedInputMute', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3',
            'Mode 4': '4',
        }

        ExecutiveModeCmdString = '{0}X'.format(ValueStateValues[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3',
            '4': 'Mode 4',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FreezeCmdString = '1*{0}F'.format(ValueStateValues[value])
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '1F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
        }

        GlobalVideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def UpdateGlobalVideoMute(self, value, qualifier):

        GlobalVideoMuteCmdString = 'B'
        self.__UpdateHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def __MatchGlobalVideoMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value1 = ValueStateValues[match.group(1).decode()]
        value2 = ValueStateValues[match.group(2).decode()]
        value3 = ValueStateValues[match.group(3).decode()]
        if value1 == value2 == value3:
            self.WriteStatus('GlobalVideoMute', value1, None)
        else:
            self.WriteStatus('GlobalVideoMute', 'Off', None)

        self.WriteStatus('VideoMute', value1, {'Output': '1A'})
        self.WriteStatus('VideoMute', value2, {'Output': '1B'})
        self.WriteStatus('VideoMute', value3, {'Output': 'Loop Out'})

    def __MatchGlobalVideoMuteEx(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GlobalVideoMute', value, None)

        self.WriteStatus('VideoMute', value, {'Output': '1A'})
        self.WriteStatus('VideoMute', value, {'Output': '1B'})
        self.WriteStatus('VideoMute', value, {'Output': 'Loop Out'})

    def SetGroupBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -24,
            'Max': 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupBassCmdString = 'wD7*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupBass', GroupBassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBass')

    def UpdateGroupBass(self, value, qualifier):

        GroupBassCmdString = 'wD7GRPM\r'
        self.__UpdateHelper('GroupBass', GroupBassCmdString, value, qualifier)

    def __MatchGroupBass(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupBass', value, None)

    def SetGroupLineMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GroupLineMuteCmdString = 'wD6*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupLineMute', GroupLineMuteCmdString, value, qualifier)

    def UpdateGroupLineMute(self, value, qualifier):

        GroupLineMuteCmdString = 'wD6GRPM\r'
        self.__UpdateHelper('GroupLineMute', GroupLineMuteCmdString, value, qualifier)

    def __MatchGroupLineMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupLineMute', value, None)

    def SetGroupLineVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupLineVolumeCmdString = 'wD5*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupLineVolume', GroupLineVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLineVolume')

    def UpdateGroupLineVolume(self, value, qualifier):

        GroupLineVolumeCmdString = 'wD5GRPM\r'
        self.__UpdateHelper('GroupLineVolume', GroupLineVolumeCmdString, value, qualifier)

    def __MatchGroupLineVolume(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupLineVolume', value, None)

    def SetGroupMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GroupMicMuteCmdString = 'wD2*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupMicMute', GroupMicMuteCmdString, value, qualifier)

    def UpdateGroupMicMute(self, value, qualifier):

        GroupMicMuteCmdString = 'wD2GRPM\r'
        self.__UpdateHelper('GroupMicMute', GroupMicMuteCmdString, value, qualifier)

    def __MatchGroupMicMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupMicMute', value, None)

    def SetGroupMicVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupMicVolume = 'wD1*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupMicVolume', GroupMicVolume, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMicVolume')

    def UpdateGroupMicVolume(self, value, qualifier):

        GroupMicVolume = 'wD1GRPM\r'
        self.__UpdateHelper('GroupMicVolume', GroupMicVolume, value, qualifier)

    def __MatchGroupMicVolume(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupMicVolume', value, None)

    def SetGroupOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GroupOutputMuteCmdString = 'wD10*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupOutputMute', GroupOutputMuteCmdString, value, qualifier)

    def UpdateGroupOutputMute(self, value, qualifier):

        GroupOutputMuteCmdString = 'wD10GRPM\r'
        self.__UpdateHelper('GroupOutputMute', GroupOutputMuteCmdString, value, qualifier)

    def __MatchGroupOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupOutputMute', value, None)

    def SetGroupOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupOutputVolumeCmdString = 'wD9*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupOutputVolume', GroupOutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputVolume')

    def UpdateGroupOutputVolume(self, value, qualifier):

        GroupOutputVolumeCmdString = 'wD9GRPM\r'
        self.__UpdateHelper('GroupOutputVolume', GroupOutputVolumeCmdString, value, qualifier)

    def __MatchGroupOutputVolume(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupOutputVolume', value, None)

    def SetGroupProgramMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        GroupProgramMuteCmdString = 'wD4*{0}GRPM\r'.format(ValueStateValues[value])
        self.__SetHelper('GroupProgramMute', GroupProgramMuteCmdString, value, qualifier)

    def UpdateGroupProgramMute(self, value, qualifier):

        GroupProgramMuteCmdString = 'wD4GRPM\r'
        self.__UpdateHelper('GroupProgramMute', GroupProgramMuteCmdString, value, qualifier)

    def __MatchGroupProgramMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('GroupProgramMute', value, None)

    def SetGroupProgramVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 12
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupProgramVolume = 'wD3*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupProgramVolume', GroupProgramVolume, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupProgramVolume')

    def UpdateGroupProgramVolume(self, value, qualifier):

        GroupProgramVolume = 'wD3GRPM\r'
        self.__UpdateHelper('GroupProgramVolume', GroupProgramVolume, value, qualifier)

    def __MatchGroupProgramVolume(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupProgramVolume', value, None)

    def SetGroupTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -24,
            'Max': 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            GroupTrebleCmdString = 'wD8*{0}GRPM\r'.format(round(value * 10))
            self.__SetHelper('GroupTreble', GroupTrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTreble')

    def UpdateGroupTreble(self, value, qualifier):

        GroupTrebleCmdString = 'wD8GRPM\r'
        self.__UpdateHelper('GroupTreble', GroupTrebleCmdString, value, qualifier)

    def __MatchGroupTreble(self, match, tag):

        value = int(match.group(1).decode()) / 10
        self.WriteStatus('GroupTreble', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 2 <= int(qualifier['Input']) <= self.InputMax:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        if 2 <= int(qualifier['Input']) <= self.InputMax:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            HDCPInputStatusCmdString = 'wI{0}HDCP\r'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source Device Detected',
            '2': 'Source Detected with HDCP',
            '1': 'Source Detected without HDCP'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        OutputStates = {
            '1A': '1',
            '1B': '2',
            'Loop Out': '3',
        }

        HDCPOutputStatusCmdString = 'wO{0}HDCP\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        OutputStates = {
            '1': '1A',
            '2': '1B',
            '3': 'Loop Out'
        }

        ValueStateValues = {
            '0': 'No Sink Device Detected',
            '2': 'Sink Detected with HDCP',
            '1': 'Sink Detected without HDCP'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, qualifier)

    def SetInput(self, value, qualifier):

        InputTypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
        }

        type_ = qualifier['Type']
        if value in self.InputStates:
            if value == 'Aux' and type_ != 'Audio':  
                self.Discard('Invalid Command for SetInput')  
                return  

            InputCmdString = '{0}*1{1}'.format(self.InputStates[value], InputTypeStates[type_])            
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputTypeStates = {
            'Audio' : '$',
            'Video' : '%',
        }

        type_ = qualifier['Type']
        if type_ in InputTypeStates:
            InputCmdString = '{0}'.format(InputTypeStates[type_])
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        elif type_ == 'Audio/Video':
            self.__UpdateHelper('Input', '!', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, qualifier):

        InputTypeValues = {
            'Aud' : 'Audio',
            'Vid' : 'Video',
            'All' : 'Audio/Video'
        }

        type_ = InputTypeValues[match.group(2).decode()]
        qualifier = {'Type': type_}
        value = self.InputValues[match.group(1).decode()]
        self.WriteStatus('Input', value, qualifier)

        if type_ != 'Audio/Video': 
            otherType = 'Video' if type_ == 'Audio' else 'Audio' 
            self.WriteStatus('Input', '0', {'Type': 'Audio/Video'}) 
        else: 
            self.WriteStatus('Input', value, {'Type': 'Audio'})
            self.WriteStatus('Input', value, {'Type': 'Video'})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)    

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1' : 'Active', 
            '0' : 'Not Active'
        }

        values = match.group(1).decode().split('*')
        for input_, value in enumerate(values):
            qualifier = {'Input': str(input_+1)}
            value = ValueStateValues[value]
            self.WriteStatus('InputSignalStatus', value, qualifier)

    def UpdateInputSignalType(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputMax:
            InputSignalTypeCmdString = '{0}*\x5c'.format(qualifier['Input'])
            self.__UpdateHelper('InputSignalType', InputSignalTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalType')

    def __MatchInputSignalType(self, match, tag):

        ValueStateValues = {
            '0' : 'No Signal', 
            '1' : 'DVI', 
            '2' : 'HDMI', 
            '3' : 'DisplayPort'
        }

        qualifier = {}
        qualifier['Input'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalType', value, qualifier)

    def SetLineInputGain(self, value, qualifier):

        InputStates = {
            'Line In 3'   : '40002',
            'Line In 4'   : '40003',
            'Aux'         : ['30016', '30017'],
            'File Player' : ['40004', '40005']
        }

        ValueConstraints = {
            'Min' : -18,
            'Max' : 24
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if qualifier['Input'] in ['Aux', 'File Player']:
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], round(value*10)), value, qualifier) 
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], round(value*10)), value, qualifier)
            else:
                self.__SetHelper('LineInputGain', 'wG{0}*{1}AU\r'.format(InputStates[qualifier['Input']], round(value*10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInputGain')

    def UpdateLineInputGain(self, value, qualifier):

        InputStates = {
            'Line In 3'   : '40002',
            'Line In 4'   : '40003',
            'Aux'         : '30016',
            'File Player' : '40004'
        }

        LineInputGainCmdString = 'wG{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('LineInputGain', LineInputGainCmdString, value, qualifier)

    def __MatchLineInputGain(self, match, tag):

        InputStates = {
            '40002' : 'Line In 3',
            '40003' : 'Line In 4',
            '30016' : 'Aux',
            '40004' : 'File Player'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())/10
        self.WriteStatus('LineInputGain', value, qualifier)

    def SetLineInputMute(self, value, qualifier):

        InputStates = {
            'Line In 3'   : '40002',
            'Line In 4'   : '40003',
            'Aux'         : ['30016', '30017'],
            'File Player' : ['40004', '40005']
        }

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        if qualifier['Input'] in ['Aux', 'File Player']:
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']][0], ValueStateValues[value]), value, qualifier) 
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']][1], ValueStateValues[value]), value, qualifier)
        else:
            self.__SetHelper('LineInputMute', 'wM{0}*{1}AU\r'.format(InputStates[qualifier['Input']], ValueStateValues[value]), value, qualifier)

    def UpdateLineInputMute(self, value, qualifier):

        InputStates = {
            'Line In 3'   : '40002',
            'Line In 4'   : '40003',
            'Aux'         : '30016',
            'File Player' : '40004'
        }

        LineInputMuteCmdString = 'wM{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('LineInputMute', LineInputMuteCmdString, value, qualifier)

    def __MatchLineInputMute(self, match, tag):

        InputStates = {
            '40002' : 'Line In 3',
            '40003' : 'Line In 4',
            '30016' : 'Aux',
            '40004' : 'File Player'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LineInputMute', value, qualifier)

    def SetLogo(self, value, qualifier):

        logo = 0 if value == 'Off' else int(value)
        if 0 <= logo <= 16:
            self.__SetHelper('Logo', 'wE1*{}LOGO\r'.format(logo), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        self.__UpdateHelper('Logo', 'wE1LOGO\r', value, qualifier)

    def __MatchLogo(self, match, qualifier):

        value = 'Off' if match.group(1).decode() == '0' else match.group(1).decode()
        self.WriteStatus('Logo', value, qualifier)

    def SetLoopOut(self, value, qualifier):

        if 1 <= int(value) <= self.InputMax:
            self.__SetHelper('LoopOut', 'w{}LOUT\r'.format(int(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoopOut')

    def UpdateLoopOut(self, value, qualifier):

        self.__UpdateHelper('LoopOut', 'wLOUT\r', value, qualifier)

    def __MatchLoopOut(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('LoopOut', value, qualifier)

    def SetMicLineInputGain(self, value, qualifier):

        InputStates = {
            '1' : '0',
            '2' : '1'
        }

        ValueConstraints = {
            'Min' : -18,
            'Max' : 80
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicLineInputGainCmdString = 'wG4000{0}*{1}AU\r'.format(InputStates[qualifier['Input']], round(value*10))
            self.__SetHelper('MicLineInputGain', MicLineInputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicLineInputGain')

    def UpdateMicLineInputGain(self, value, qualifier):

        InputStates = {
            '1' : '0',
            '2' : '1'
        }

        MicLineInputGainCmdString = 'wG4000{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('MicLineInputGain', MicLineInputGainCmdString, value, qualifier)

    def __MatchMicLineInputGain(self, match, tag):

        InputStates = {
            '0' : '1',
            '1' : '2'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = int(match.group(2).decode())/10
        self.WriteStatus('MicLineInputGain', value, qualifier)

    def SetMicLineInputMute(self, value, qualifier):

        InputStates = {
            '1' : '0',
            '2' : '1'
        }

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        MicLineInputMuteCmdString = 'wM4000{0}*{1}AU\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('MicLineInputMute', MicLineInputMuteCmdString, value, qualifier)

    def UpdateMicLineInputMute(self, value, qualifier):

        InputStates = {
            '1' : '0',
            '2' : '1'
        }

        MicLineInputMuteCmdString = 'wM4000{0}AU\r'.format(InputStates[qualifier['Input']])
        self.__UpdateHelper('MicLineInputMute', MicLineInputMuteCmdString, value, qualifier)

    def __MatchMicLineInputMute(self, match, tag):

        InputStates = {
            '0' : '1',
            '1' : '2'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Input'] = InputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('MicLineInputMute', value, qualifier)

    def SetOutputAttenuation(self, value, qualifier):

        OutputStates = {
            'HDMI Out'          : ['00', '01'],
            'DTP2/XTP/HDBT Out' : ['02', '03'],
            'DTP Analog Out'    : ['04', '05'],
            'Line Out 1'        : '06',
            'Line Out 2'        : '07',
            'Line Out 3'        : '08',
            'Line Out 4'        : '09',
            'Amp Out'           : ['10', '11']
        }

        ValueConstraints = {
            'Min' : -100,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            if 'Line Out' not in qualifier['Output']: 
                if qualifier['Output'] == 'Amp Out' and self.Model == '1808MA': 
                    self.__SetHelper('OutputAttenuation', 'wG60010*{}AU\r'.format(round(value*10)), value, qualifier, 3)
                else:
                    self.__SetHelper('OutputAttenuation', 'wG600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][0], round(value*10)), value, qualifier) 
                    self.__SetHelper('OutputAttenuation', 'wG600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][1], round(value*10)), value, qualifier)
            else: 
                self.__SetHelper('OutputAttenuation', 'wG600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']], round(value*10)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputAttenuation')

    def UpdateOutputAttenuation(self, value, qualifier):

        OutputStates = {
            'HDMI Out'          : '00',
            'DTP2/XTP/HDBT Out' : '02',
            'DTP Analog Out'    : '04',
            'Line Out 1'        : '06',
            'Line Out 2'        : '07',
            'Line Out 3'        : '08',
            'Line Out 4'        : '09',
            'Amp Out'           : '10'
        }

        OutputAttenuationCmdString = 'wG600{0}AU\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputAttenuation', OutputAttenuationCmdString, value, qualifier)

    def __MatchOutputAttenuation(self, match, tag):

        OutputStates = {
            '00' : 'HDMI Out',
            '02' : 'DTP2/XTP/HDBT Out',
            '04' : 'DTP Analog Out',
            '06' : 'Line Out 1',
            '07' : 'Line Out 2',
            '08' : 'Line Out 3',
            '09' : 'Line Out 4',
            '10' : 'Amp Out'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = int(match.group(2).decode())/10
        self.WriteStatus('OutputAttenuation', value, qualifier)

    def SetOutputFormat(self, value, qualifier):

        OutputStates = {
            '1A' : '1', 
            '1B' : '2',
            'Loop Out': '3'
        }

        ValueStateValues = {
            'Auto' : '0', 
            'DVI RGB 444' : '1', 
            'HDMI RGB 444 Full' : '2', 
            'HDMI RGB 444 Limited' : '3',
            'HDMI YUV 444 Limited' : '5', 
            'HDMI YUV 422 Limited' : '7', 
            'HDMI YUV 420 Limited' : '9'
        }

        OutputFormatCmdString = 'w{0}*{1}VTPO\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def UpdateOutputFormat(self, value, qualifier):

        OutputStates = {
            '1A': '1', 
            '1B': '2',
            'Loop Out': '3',
        }

        OutputFormatCmdString = 'w{0}*VTPO\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def __MatchOutputFormat(self, match, tag):

        OutputStates = {
            '1' : '1A', 
            '2' : '1B',
            '3' : 'Loop Out',
        }

        ValueStateValues = {
            '0' : 'Auto', 
            '1' : 'DVI RGB 444', 
            '2' : 'HDMI RGB 444 Full', 
            '3' : 'HDMI RGB 444 Limited', 
            '5' : 'HDMI YUV 444 Limited', 
            '7' : 'HDMI YUV 422 Limited', 
            '9' : 'HDMI YUV 420 Limited'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputFormat', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        OutputStates = {
            'HDMI Out'          : ['00', '01'],
            'DTP2/XTP/HDBT Out' : ['02', '03'],
            'DTP Analog Out'    : ['04', '05'],
            'Line Out 1'        : '06',
            'Line Out 2'        : '07',
            'Line Out 3'        : '08',
            'Line Out 4'        : '09',
            'Amp Out'           : ['10', '11']
        }

        ValueStateValues = {
            'On' : '1',
            'Off' : '0'
        }

        if 'Line Out' not in qualifier['Output']: 
            if qualifier['Output'] == 'Amp Out' and self.Model == '1808MA': 
                self.__SetHelper('OutputMute', 'wM60010*{}AU\r'.format(ValueStateValues[value]), value, qualifier)
            else:
                self.__SetHelper('OutputMute', 'wM600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][0], ValueStateValues[value]), value, qualifier)
                self.__SetHelper('OutputMute', 'wM600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']][1], ValueStateValues[value]), value, qualifier)
        else: 
            self.__SetHelper('OutputMute', 'wM600{0}*{1}AU\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value]), value, qualifier)

    def UpdateOutputMute(self, value, qualifier):

        OutputStates = {
            'HDMI Out'          : '00',
            'DTP2/XTP/HDBT Out' : '02',
            'DTP Analog Out'    : '04',
            'Line Out 1'        : '06',
            'Line Out 2'        : '07',
            'Line Out 3'        : '08',
            'Line Out 4'        : '09',
            'Amp Out'           : '10'
        }

        OutputMuteCmdString = 'wM600{0}AU\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)

    def __MatchOutputMute(self, match, tag):

        OutputStates = {
            '00' : 'HDMI Out',
            '02' : 'DTP2/XTP/HDBT Out',
            '04' : 'DTP Analog Out',
            '06' : 'Line Out 1',
            '07' : 'Line Out 2',
            '08' : 'Line Out 3',
            '09' : 'Line Out 4',
            '10' : 'Amp Out'
        }

        ValueStateValues = {
            '1' : 'On',
            '0' : 'Off'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480' : '10', 
            '800x600' : '11', 
            '1024x768' : '12', 
            '1280x768' : '13', 
            '1280x800' : '14', 
            '1280x1024' : '15', 
            '1360x768' : '16', 
            '1366x768' : '17', 
            '1440x900' : '18', 
            '1400x1050' : '19', 
            '1600x900' : '20', 
            '1680x1050' : '21', 
            '1600x1200' : '22', 
            '1920x1200' : '23', 
            '480p (59.94Hz)' : '24', 
            '480p (60Hz)' : '25', 
            '576p' : '26', 
            '720p (25Hz)' : '29', 
            '720p (29.97Hz)' : '30', 
            '720p (30Hz)' : '31', 
            '720p (50Hz)' : '32', 
            '720p (59.94Hz)' : '33', 
            '720p (60Hz)' : '34', 
            '1080i (50Hz)' : '35', 
            '1080i (59.94Hz)' : '36', 
            '1080i (60Hz)' : '37', 
            '1080p (23.98Hz)' : '38', 
            '1080p (24Hz)' : '39', 
            '1080p (25Hz)' : '40', 
            '1080p (29.97Hz)' : '41', 
            '1080p (30Hz)' : '42', 
            '1080p (50Hz)' : '43', 
            '1080p (59.94Hz)' : '44', 
            '1080p (60Hz)' : '45', 
            '2048x1080 (2K) (23.98Hz)' : '46', 
            '2048x1080 (2K) (24Hz)' : '47', 
            '2048x1080 (2K) (25Hz)' : '48', 
            '2048x1080 (2K) (29.97Hz)' : '49', 
            '2048x1080 (2K) (30Hz)' : '50', 
            '2048x1080 (2K) (50Hz)' : '51', 
            '2048x1080 (2K) (59.94Hz)' : '52', 
            '2048x1080 (2K) (60Hz)' : '53', 
            '2048x1200 (60Hz)' : '54', 
            '2048x1536 (60Hz)' : '55', 
            '2560x1080 (60Hz)' : '56', 
            '2560x1440 (60Hz)' : '57', 
            '2560x1600 (60Hz)' : '58', 
            '3840x2160 (23.98Hz)' : '59', 
            '3840x2160 (24Hz)' : '60', 
            '3840x2160 (25Hz)' : '61', 
            '3840x2160 (29.97Hz)' : '62', 
            '3840x2160 (30Hz)' : '63', 
            '3840x2160 (50Hz)' : '64', 
            '3840x2160 (59.94Hz)' : '65', 
            '3840x2160 (60Hz)' : '66', 
            '4096x2160 (23.98Hz)' : '69', 
            '4096x2160 (24Hz)' : '70', 
            '4096x2160 (25Hz)' : '71', 
            '4096x2160 (29.97Hz)' : '72', 
            '4096x2160 (30Hz)' : '73', 
            '4096x2160 (50Hz)' : '74', 
            '4096x2160 (59.94Hz)' : '75', 
            '4096x2160 (60Hz)' : '76', 
            'Custom 1' : '201', 
            'Custom 2' : '202', 
            'Custom 3' : '203', 
            'Custom 4' : '204', 
            'Custom 5' : '205',
            'Custom 6' : '206',
            'Custom 7' : '207',
            'Custom 8' : '208',
            'Custom 9' : '209',
            'Custom 10' : '210',
        }

        OutputResolutionCmdString = 'w1*{0}RATE\r'.format(ValueStateValues[value])
        self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w1RATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        ValueStateValues = {
            '10' : '640x480', 
            '11' : '800x600', 
            '12' : '1024x768', 
            '13' : '1280x768', 
            '14' : '1280x800', 
            '15' : '1280x1024', 
            '16' : '1360x768', 
            '17' : '1366x768', 
            '18' : '1440x900', 
            '19' : '1400x1050', 
            '20' : '1600x900', 
            '21' : '1680x1050', 
            '22' : '1600x1200', 
            '23' : '1920x1200', 
            '24' : '480p (59.94Hz)', 
            '25' : '480p (60Hz)', 
            '26' : '576p', 
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
            '46' : '2048x1080 (2K) (23.98Hz)', 
            '47' : '2048x1080 (2K) (24Hz)', 
            '48' : '2048x1080 (2K) (25Hz)', 
            '49' : '2048x1080 (2K) (29.97Hz)', 
            '50' : '2048x1080 (2K) (30Hz)', 
            '51' : '2048x1080 (2K) (50Hz)', 
            '52' : '2048x1080 (2K) (59.94Hz)', 
            '53' : '2048x1080 (2K) (60Hz)', 
            '54' : '2048x1200 (60Hz)', 
            '55' : '2048x1536 (60Hz)', 
            '56' : '2560x1080 (60Hz)', 
            '57' : '2560x1440 (60Hz)', 
            '58' : '2560x1600 (60Hz)', 
            '59' : '3840x2160 (23.98Hz)', 
            '60' : '3840x2160 (24Hz)', 
            '61' : '3840x2160 (25Hz)', 
            '62' : '3840x2160 (29.97Hz)', 
            '63' : '3840x2160 (30Hz)', 
            '64' : '3840x2160 (50Hz)', 
            '65' : '3840x2160 (59.94Hz)', 
            '66' : '3840x2160 (60Hz)', 
            '69' : '4096x2160 (23.98Hz)', 
            '70' : '4096x2160 (24Hz)', 
            '71' : '4096x2160 (25Hz)', 
            '72' : '4096x2160 (29.97Hz)', 
            '73' : '4096x2160 (30Hz)', 
            '74' : '4096x2160 (50Hz)', 
            '75' : '4096x2160 (59.94Hz)', 
            '76' : '4096x2160 (60Hz)', 
            '201' : 'Custom 1', 
            '202' : 'Custom 2', 
            '203' : 'Custom 3', 
            '204' : 'Custom 4', 
            '205' : 'Custom 5',
            '206' : 'Custom 6',
            '207' : 'Custom 7',
            '208' : 'Custom 8',
            '209' : 'Custom 9',
            '210' : 'Custom 10'
        }

        value = ValueStateValues[str(int(match.group(1).decode()))]
        self.WriteStatus('OutputResolution', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        ValueStateValues = {
            'Lowest' : '1', 
            'Off' : '0',
            'Low' : '2'
        }

        PowerSaveModeCmdString = 'w{0}PSAV\r'.format(ValueStateValues[value])
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        ValueStateValues = {
            '1' : 'Lowest', 
            '0' : 'Off',
            '2' : 'Low' 
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):


        ScreenSaverStatusCmdString = 'wS1SSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', ScreenSaverStatusCmdString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, tag):

        ValueStateValues = {
            '0' : 'Active Input Detected; Timer not running', 
            '1' : 'No Active Input; Timer running; Output sync enabled', 
            '2' : 'No Active Input; Timer expired; Output sync disabled'
        }


        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Crop' : '1', 
            'Alternating Pixels' : '2', 
            'Crosshatch' : '3', 
            'Color Bars' : '4', 
            'Grayscale' : '5', 
            'Audio Test' : '6', 
            'Off' : '0'
        }

        TestPatternCmdString = 'w1*{0}TEST\r'.format(ValueStateValues[value])
        self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'w1TEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        ValueStateValues = {
            '1' : 'Crop', 
            '2' : 'Alternating Pixels', 
            '3' : 'Crosshatch', 
            '4' : 'Color Bars', 
            '5' : 'Grayscale', 
            '6' : 'Audio Test', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetRecallCmdString = "2*{0}.".format(value)
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')
    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            InputPresetSaveCmdString = "2*{0},".format(value)
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')
    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            '1A' : '1', 
            '1B' : '2',
            'Loop Out' : '3'
        }

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0', 
            'On with Sync' : '2'
        }

        VideoMuteCmdString = '{0}*{1}B'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        OutputStates = {
            '1A' : '1', 
            '1B' : '2',
            'Loop Out' : '3'
        }

        VideoMuteCmdString = '{0}*B'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        OutputStates = {
            '1' : '1A', 
            '2' : '1B',
            '3' : 'Loop Out'
        }

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off', 
            '2' : 'On with Sync'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
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
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number or output number',
            '13' : 'Invalid parameter',
            '14' : 'Invalid for this configuration',
            '17' : 'Invalid command for signal type',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '28' : 'Bad filename or file not found',
            '33' : 'Bad file type for logo'
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
        self.lastInputSignalUpdate = 0
        self.CECOutputList.clear()
        
    def extr_17_3966_1806(self):
        self.Model = '1806'
        self.InputMax = 6
        self.InputStates = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', 'Aux': '9'}
        self.InputValues = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '9': 'Aux'}

    def extr_17_3966_1808(self):
        self.Model = '1808'
        self.InputMax = 8
        self.InputStates = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 'Aux': '9'}
        self.InputValues = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': 'Aux'}

    def extr_17_3966_1808MA(self):
        self.Model = '1808MA'
        self.InputMax = 8
        self.InputStates = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 'Aux': '9'}
        self.InputValues = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': 'Aux'}

    def extr_17_3966_1808SA(self):
        self.Model = '1808SA'
        self.InputMax = 8
        self.InputStates = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', 'Aux': '9'}
        self.InputValues = {'1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': 'Aux'}
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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')
  
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
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]))#, sep='\r\n')
  
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
