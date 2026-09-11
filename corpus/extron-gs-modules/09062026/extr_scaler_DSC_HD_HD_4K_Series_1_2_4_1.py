from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
            'DSC HD-HD 4K Plus A': self.extr_17_2211_plus,
            'DSC HD-HD 4K Plus A xi': self.extr_17_2211_plus_xi,
            'DSC HD-HD 4K A': self.extr_17_2211_non_plus,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioFormat': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FilmModeDetection': {'Status': {}},
            'Freeze': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'HDCPOutputStatusXI': {'Parameters': ['Output'], 'Status': {}},
            'InputGain': {'Status': {}},
            'InputPresetRecall': {'Status': {}},
            'InputPresetSave': {'Status': {}},
            'InputSignalStatus': {'Status': {}},
            'InputSignalStatusXI': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalType': {'Status': {}},
            'InputSignalTypeXI': {'Parameters': ['Input'], 'Status': {}},
            'Logo': {'Status': {}},
            'LogoAssignment': {'Parameters': ['Logo'], 'Status': {}},
            'LogoAvailability': {'Parameters': ['Logo'], 'Status': {}},
            'LogoKeySetting': {'Parameters': ['Logo'], 'Status': {}},
            'OutputFormat': {'Status': {}},
            'OutputFormatXI': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'ScreenSaverStatus': {'Status': {}},
            'Temperature': {'Status': {}},
            'TestPattern': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VideoMuteXI': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        self.EchoDisabled = True
        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'Aud([+-])(\d+)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(rb'AfmtI1\*([0-5])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Amt([01]) ([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(rb'Amt([12])\*([01])\r\n'), self.__MatchAudioMuteSet, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchGlobalAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(rb'Film1\*([01])\r\n'), self.__MatchFilmModeDetection, None)
            self.AddMatchString(re.compile(rb'Frz1\*([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(rb'Vtpo([1-2])\*([0-7])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(rb'HdcpO([12])\*([02])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(rb'Aspr1\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(rb'In00 ([01])\*?([01]?)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vid(1|2) Typ(0|1|2) Amt[01] Blk[012] Hrt[0-9.]+ Vrt[0-9.]+\r\n'), self.__MatchInputSignalType, None)
            self.AddMatchString(re.compile(rb'LogoE(?:1\*)?(\d{1,3})\r\n'), self.__MatchLogo, None)
            self.AddMatchString(re.compile(rb'LogoA(\d{3}),(.*?)\r\n'), self.__MatchLogoAssignment, None)
            self.AddMatchString(re.compile(rb'LogoQ00\*([01]+[*01]+)\r\n'), self.__MatchLogoAvailability, None)
            self.AddMatchString(re.compile(rb'Lkef(\d{3})\*([0-4])\r\n'), self.__MatchLogoKeySetting, None)
            self.AddMatchString(re.compile(rb'Rate1\*(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Psav([01])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(rb'SsavS1\*([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(re.compile(rb'20Stat (\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(rb'Test1\*0?([0-6])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(rb'Vmt([12])\*([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vmt([012])\r\n'), self.__MatchGlobalVideoMute, None)
            self.AddMatchString(re.compile(rb'HdcpE1\*([0-1])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(rb'Vol([+-])(\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(rb'E(\d+)\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'Echo0\r\n'), self.__MatchEchoMode, None)  # Echo Mode for SSH

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()        
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):
        self.EchoDisabled = False

    def SetInputGain(self, value, qualifier):

        InputGainConstraints = {
            'Min': -18,
            'Max': 24
        }

        InputGainCmdString = ''
        if InputGainConstraints['Min'] <= value < 0:
            InputGainCmdString = '{0}G'.format(value)
        elif 0 <= value <= InputGainConstraints['Max']:
            InputGainCmdString = '+{0}G'.format(value)

        if InputGainCmdString:
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputGainCmdString = 'G'
        self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)

    def __MatchInputGain(self, match, tag):

        sign = match.group(1).decode()
        value = int(match.group(2).decode())
        if sign == '-':
            value *= -1
        self.WriteStatus('InputGain', value, None)

    def SetAudioFormat(self, value, qualifier):

        AudioFormatStateValues = {
            'None': '0',
            'Analog': '1',
            'LPCM-2Ch': '2',
            'Multi-Ch': '3',
            'LPCM-2Ch Auto': '4',
            'Multi-Ch Auto': '5'
        }

        if value in AudioFormatStateValues:
            AudioFormatString = 'wI1*{0}AFMT\r'.format(AudioFormatStateValues[value])
            self.__SetHelper('AudioFormat', AudioFormatString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        AudioFormatCmdString = 'wI1AFMT\r'
        self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)

    def __MatchAudioFormat(self, match, tag):

        AudioFormatStateNames = {
            '0': 'None',
            '1': 'Analog',
            '2': 'LPCM-2Ch',
            '3': 'Multi-Ch',
            '4': 'LPCM-2Ch Auto',
            '5': 'Multi-Ch Auto'
        }

        value = AudioFormatStateNames[match.group(1).decode()]
        self.WriteStatus('AudioFormat', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioInputStateValue = {
            'Analog': '1',
            'Digital': '2'
        }

        if qualifier['Output'] in AudioInputStateValue and value in AudioMuteStateValues:
            AudioMuteCmdString = '{0}*{1}Z'.format(AudioInputStateValue[qualifier['Output']], AudioMuteStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMuteSet(self, match, tag):

        AudioMuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        AudioInputStateNames = {
            '1': 'Analog',
            '2': 'Digital'
        }

        value = AudioMuteStateNames[match.group(2).decode()]
        qualifier = {'Output': AudioInputStateNames[match.group(1).decode()]}
        self.WriteStatus('AudioMute', value, qualifier)

    def __MatchGlobalAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        qualifier = {'Output': 'Analog'}
        self.WriteStatus('AudioMute', value, qualifier)
        qualifier = {'Output': 'Digital'}
        self.WriteStatus('AudioMute', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        qualifier = {'Output': 'Analog'}
        self.WriteStatus('AudioMute', value, qualifier)
        value = AudioMuteStateNames[match.group(2).decode()]
        qualifier = {'Output': 'Digital'}
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        ValueStateValues = {
            'Execute': '1*0A',
            'Execute and Fill': '1*1A',
            'Execute and Follow': '1*2A'
        }

        if value in ValueStateValues:
            AutoImageCmdString = '{0}'.format(ValueStateValues[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ExecutiveModeStateValues:
            ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFilmModeDetection(self, value, qualifier):

        FilmModeDetectionStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in FilmModeDetectionStateValues:
            FilmModeDetectionCmdString = 'w1*{0}FILM\r'.format(FilmModeDetectionStateValues[value])
            self.__SetHelper('FilmModeDetection', FilmModeDetectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFilmModeDetection')

    def UpdateFilmModeDetection(self, value, qualifier):

        FilmModeDetectionCmdString = 'w1FILM\r'
        self.__UpdateHelper('FilmModeDetection', FilmModeDetectionCmdString, value, qualifier)

    def __MatchFilmModeDetection(self, match, tag):

        FilmModeDetectionStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = FilmModeDetectionStateNames[match.group(1).decode()]
        self.WriteStatus('FilmModeDetection', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in FreezeStateValues:
            FreezeCmdString = '1*{0}F'.format(FreezeStateValues[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = '1F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, tag):

        FreezeStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = FreezeStateNames[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }

        if value in ValueStateValues:
            GlobalAudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalAudioMute')

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'On with Sync': '2B',
            'Off': '0B'
        }

        if value in ValueStateValues:
            GlobalVideoMuteCmdString = ValueStateValues[value]
            self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGlobalVideoMute')

    def SetOutputFormat(self, value, qualifier):

        if value in self.OutputFormatStateValues:
            OutputFormatCmdString = 'w1*{}VTPO\r'.format(self.OutputFormatStateValues[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        OutputFormatCmdString = 'w1VTPO\r'
        self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def SetOutputFormatXI(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates and value in self.OutputFormatStateValues:
            OutputFormatCmdString = 'w{0}*{1}VTPO\r'.format(self.OutputStates[qualifier['Output']], self.OutputFormatStateValues[value])
            self.__SetHelper('OutputFormatXI', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormatXI')

    def UpdateOutputFormatXI(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            OutputFormatCmdString = 'w{0}VTPO\r'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('OutputFormatXI', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputFormatXI')

    def __MatchOutputFormat(self, match, tag):

        OutputFormatStateNames = {
            '0': 'Auto',
            '1': 'DVI RGB 444',
            '2': 'HDMI RGB 444 Full',
            '3': 'HDMI RGB 444 Limited',
            '5': 'HDMI YUV 444 Limited',
            '7': 'HDMI YUV 422 Limited',
            '9': 'HDMI YUV 420 Limited'
        }

        value = OutputFormatStateNames[match.group(2).decode()]
        if self.NonXIModel:
            self.WriteStatus('OutputFormat', value, None)
        else:
            qualifier = {'Output': self.OutputValue[match.group(1).decode()]}
            self.WriteStatus('OutputFormatXI', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wO1HDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def UpdateHDCPOutputStatusXI(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            HDCPOutputStatusCmdString = 'wO{}HDCP\r'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('HDCPOutputStatusXI', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatusXI')

    def __MatchHDCPOutputStatus(self, match, tag):

        HDCPOutputStatusStateNames = {
            '0': 'No Sink Device Detected',
            '1': 'Sink Detected without HDCP',
            '2': 'Sink Detected with HDCP'
        }

        value = HDCPOutputStatusStateNames[match.group(2).decode()]
        if self.NonXIModel:
            self.WriteStatus('HDCPOutputStatus', value, None)
        else:
            qualifier = {'Output': self.OutputValue[match.group(1).decode()]}
            self.WriteStatus('HDCPOutputStatusXI', value, qualifier)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            'Fill': '1',
            'Follow': '2',
        }

        if value in AspectRatioStateValues:
            AspectRatioCmdString = 'w1*{0}ASPR\r'.format(AspectRatioStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'w1ASPR\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        AspectRatioStateNames = {
            '1': 'Fill',
            '2': 'Follow',
        }

        value = AspectRatioStateNames[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            HDCPInputAuthorizationCmdString = '\x1BE1*{0}HDCP\r'.format(ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = '\x1BE1HDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def SetInputPresetRecall(self, value, qualifier):

        InputPresetConstraints = {
            'Min': 1,
            'Max': 128
        }

        if InputPresetConstraints['Min'] <= int(value) <= InputPresetConstraints['Max']:
            InputPresetCmdString = '2*1*{0}.'.format(value)
            self.__SetHelper('InputPresetRecall', InputPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetInputPresetSave(self, value, qualifier):

        InputPresetConstraints = {
            'Min': 1,
            'Max': 128
        }

        if InputPresetConstraints['Min'] <= int(value) <= InputPresetConstraints['Max']:
            InputPresetCmdString = '2*1*{0},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def UpdateInputSignalStatusXI(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '1': 'Active',
            '0': 'Not Active'
        }

        if match.group(2):
            qualifier = {'Input': 'A'}
            value = InputSignalStatusStateNames[match.group(1).decode()]
            self.WriteStatus('InputSignalStatusXI', value, qualifier)
            qualifier = {'Input': 'B'}
            value = InputSignalStatusStateNames[match.group(2).decode()]
            self.WriteStatus('InputSignalStatusXI', value, qualifier)
        else:
            value = InputSignalStatusStateNames[match.group(1).decode()]
            self.WriteStatus('InputSignalStatus', value, None)

    def UpdateInputSignalType(self, value, qualifier):

        InputSignalTypeCmdString = '1*I'
        self.__UpdateHelper('InputSignalType', InputSignalTypeCmdString, value, qualifier)

    def UpdateInputSignalTypeXI(self, value, qualifier):

        if qualifier['Input'] in self.OutputStates:
            InputSignalTypeXICmdString = '{}*I'.format(self.OutputStates[qualifier['Input']])
            self.__UpdateHelper('InputSignalTypeXI', InputSignalTypeXICmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalTypeXI')

    def __MatchInputSignalType(self, match, tag):

        ValueStateValues = {
            '1': 'HDMI',
            '2': 'DVI',
            '0': 'No Signal'
        }

        value = ValueStateValues[match.group(2).decode()]
        if self.NonXIModel:
            self.WriteStatus('InputSignalType', value, None)
        else:
            qualifier = {'Input': self.OutputValue[match.group(1).decode()]}
            self.WriteStatus('InputSignalTypeXI', value, qualifier)

    def SetLogo(self, value, qualifier):

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
            'Screen Saver': '101',
            'HDCP': '201',
            'Off': '0'
        }

        if value in ValueStateValues:
            LogoCmdString = 'wE1*{}LOGO\r'.format(ValueStateValues[value])
            self.__SetHelper('Logo', LogoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogo')

    def UpdateLogo(self, value, qualifier):

        LogoCmdString = 'wE1LOGO\r'
        self.__UpdateHelper('Logo', LogoCmdString, value, qualifier)

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
            '101': 'Screen Saver',
            '201': 'HDCP',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Logo', value, None)

    def SetLogoAssignment(self, value, qualifier):

        LogoStates = {
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
            'Screen Saver': '101',
            'HDCP': '201'
        }

        if qualifier['Logo'] in LogoStates and value:
            LogoAssignmentString = 'wA{0},{1}LOGO\r'.format(LogoStates[qualifier['Logo']], value)
            self.__SetHelper('LogoAssignment', LogoAssignmentString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoAssignment')

    def UpdateLogoAssignment(self, value, qualifier):

        LogoStates = {
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
            'Screen Saver': '101',
            'HDCP': '201'
        }

        if qualifier['Logo'] in LogoStates:
            LogoAssignmentCmdString = 'wA{}LOGO\r'.format(LogoStates[qualifier['Logo']])
            self.__UpdateHelper('LogoAssignment', LogoAssignmentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoAssignment')

    def __MatchLogoAssignment(self, match, tag):

        LogoStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: '11',
            12: '12',
            13: '13',
            14: '14',
            15: '15',
            16: '16',
            101: 'Screen Saver',
            201: 'HDCP'
        }

        qualifier = {'Logo': LogoStates[int(match.group(1).decode())]}
        value = match.group(2).decode()
        self.WriteStatus('LogoAssignment', value, qualifier)

    def UpdateLogoAvailability(self, value, qualifier):

        if qualifier['Logo'] in ['Screen Saver', 'HDCP'] or 1 <= int(qualifier['Logo']) <= 16:          
            LogoAvailabilityCmdString = 'wQLOGO\r'
            self.__UpdateHelper('LogoAvailability', LogoAvailabilityCmdString, value, qualifier)           
        else:
            self.Discard('Invalid Command for UpdateLogoAvailability')

    def __MatchLogoAvailability(self, match, tag):

        ValueStateValues = {
            '1': 'Saved',
            '0': 'Empty'
        }
        results = match.group(1).decode().split('*')
        logo = 1
        for i in results[0]:
            value = ValueStateValues[i]
            self.WriteStatus('LogoAvailability', value, {'Logo': str(logo)})
            logo += 1
        self.WriteStatus('LogoAvailability', ValueStateValues[results[1]], {'Logo': 'Screen Saver'})
        self.WriteStatus('LogoAvailability', ValueStateValues[results[2]], {'Logo': 'HDCP'})

    def SetLogoKeySetting(self, value, qualifier):

        LogoStates = {
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
            'Screen Saver': '101',
            'HDCP': '201'
        }

        ValueStateValues = {
            'Disabled': '0',
            'Transparency': '1',
            'RGB Key': '2',
            'Level Key': '3',
            'Alpha Key': '4'
        }

        if qualifier['Logo'] in LogoStates and value in ValueStateValues:
            LogoKeySettingCmdString = 'w{0}*{1}LKEF\r'.format(LogoStates[qualifier['Logo']], ValueStateValues[value])
            self.__SetHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLogoKeySetting')

    def UpdateLogoKeySetting(self, value, qualifier):

        LogoStates = {
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
            'Screen Saver': '101',
            'HDCP': '201'
        }

        if qualifier['Logo'] in LogoStates:
            LogoKeySettingCmdString = 'w{}LKEF\r'.format(LogoStates[qualifier['Logo']])
            self.__UpdateHelper('LogoKeySetting', LogoKeySettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLogoKeySetting')

    def __MatchLogoKeySetting(self, match, tag):

        LogoStates = {
            1: '1',
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: '11',
            12: '12',
            13: '13',
            14: '14',
            15: '15',
            16: '16',
            101: 'Screen Saver',
            201: 'HDCP'
        }

        ValueStateValues = {
            '0': 'Disabled',
            '1': 'Transparency',
            '2': 'RGB Key',
            '3': 'Level Key',
            '4': 'Alpha Key'
        }

        qualifier = {'Logo': LogoStates[int(match.group(1).decode())]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LogoKeySetting', value, qualifier)

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480 (60Hz)': '10',
            '800x600 (60Hz)': '11',
            '1024x768 (60Hz)': '12',
            '1280x768 (60Hz)': '13',
            '1280x800 (60Hz)': '14',
            '1280x1024 (60Hz)': '15',
            '1360x768 (60Hz)': '16',
            '1366x768 (60Hz)': '17',
            '1440x900 (50Hz)': '18',
            '1400x1050 (50Hz)': '19',
            '1600x900 (50Hz)': '20',
            '1680x1050 (50Hz)': '21',
            '1600x1200 (50Hz)': '22',
            '1920x1200 (50Hz)': '23',
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
            '3480x2160 (23.98Hz)': '59',
            '3480x2160 (24Hz)': '60',
            '3480x2160 (25Hz)': '61',
            '3480x2160 (29.97Hz)': '62',
            '3480x2160 (30Hz)': '63',
            '3480x2160 (50Hz)': '64',
            '3480x2160 (59.94Hz)': '65',
            '3480x2160 (60Hz)': '66',
            '4096x2160 (23.98Hz)': '69',
            '4096x2160 (24Hz)': '70',
            '4096x2160 (25Hz)': '71',
            '4096x2160 (29.97Hz)': '72',
            '4096x2160 (30Hz)': '73',
            '4096x2160 (50Hz)': '74',
            '4096x2160 (59.94Hz)': '75',
            '4096x2160 (60Hz)': '76',
            'Custom Rate 1': '201',
            'Custom Rate 2': '202',
            'Custom Rate 3': '203'
        }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'w1*{}RATE\r'.format(ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'w1RATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

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
            '18': '1440x900 (50Hz)',
            '19': '1400x1050 (50Hz)',
            '20': '1600x900 (50Hz)',
            '21': '1680x1050 (50Hz)',
            '22': '1600x1200 (50Hz)',
            '23': '1920x1200 (50Hz)',
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
            '59': '3480x2160 (23.98Hz)',
            '60': '3480x2160 (24Hz)',
            '61': '3480x2160 (25Hz)',
            '62': '3480x2160 (29.97Hz)',
            '63': '3480x2160 (30Hz)',
            '64': '3480x2160 (50Hz)',
            '65': '3480x2160 (59.94Hz)',
            '66': '3480x2160 (60Hz)',
            '69': '4096x2160 (23.98Hz)',
            '70': '4096x2160 (24Hz)',
            '71': '4096x2160 (25Hz)',
            '72': '4096x2160 (29.97Hz)',
            '73': '4096x2160 (30Hz)',
            '74': '4096x2160 (50Hz)',
            '75': '4096x2160 (59.94Hz)',
            '76': '4096x2160 (60Hz)',
            '201': 'Custom Rate 1',
            '202': 'Custom Rate 2',
            '203': 'Custom Rate 3'
        }

        value = ValueStateValues[str(int(match.group(1).decode()))]
        self.WriteStatus('OutputResolution', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in PowerSaveModeStateValues:
            PowerSaveModeCmdString = 'w{0}PSAV\r'.format(PowerSaveModeStateValues[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        PowerSaveModeStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        value = PowerSaveModeStateNames[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdateScreenSaverStatus(self, value, qualifier):

        commandString = 'wS1SSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', commandString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, qualifier):

        ScreenSaverStatusStateNames = {
            '0': 'Active Input Detected; Timer not running',
            '2': 'No Active Input; Timer expired; Output sync disabled',
            '1': 'No Active Input; Timer running; Output sync enabled'
        }

        value = ScreenSaverStatusStateNames[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, qualifier)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        TestPatternStateValues = {
            'Off': '0',
            'Crop': '1',
            'Alternating Pixels': '2',
            'Crosshatch': '3',
            'Color Bars': '4',
            '32-level split Grayscale': '5',
            'Audio Test': '6',
        }

        if value in TestPatternStateValues:
            TestPatternCmdString = 'w1*{0}TEST\r'.format(TestPatternStateValues[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'w1TEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, tag):

        TestPatternStateNames = {
            '0': 'Off',
            '1': 'Crop',
            '2': 'Alternating Pixels',
            '3': 'Crosshatch',
            '4': 'Color Bars',
            '5': '32-level split Grayscale',
            '6': 'Audio Test',
        }

        value = TestPatternStateNames[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
        }

        if value in VideoMuteStateValues:
            VideoMuteCmdString = '1*{}B'.format(VideoMuteStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = '1*B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVideoMuteXI(self, value, qualifier):

        VideoMuteStateValues = {
            'On': '1',
            'On with Sync': '2',
            'Off': '0'
        }

        if qualifier['Output'] in self.OutputStates and value in VideoMuteStateValues:
            VideoMuteCmdString = '{0}*{1}B'.format(self.OutputStates[qualifier['Output']], VideoMuteStateValues[value])
            self.__SetHelper('VideoMuteXI', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMuteXI')

    def UpdateVideoMuteXI(self, value, qualifier):

        if qualifier['Output'] in self.OutputStates:
            VideoMuteCmdString = '{0}*B'.format(self.OutputStates[qualifier['Output']])
            self.__UpdateHelper('VideoMuteXI', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoMuteXI')

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value = VideoMuteStateNames[match.group(2).decode()]
        if self.NonXIModel:
            self.WriteStatus('VideoMute', value, None)
        else:
            qualifier = self.OutputValue[match.group(1).decode()]
            self.WriteStatus('VideoMuteXI', value, {'Output': qualifier})

    def __MatchGlobalVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '1': 'On',
            '2': 'On with Sync',
            '0': 'Off'
        }

        value = VideoMuteStateNames[match.group(1).decode()]
        if self.NonXIModel:
            self.WriteStatus('VideoMute', value, None)
        else:
            qualifier = {'Output': 'A'}
            self.WriteStatus('VideoMuteXI', value, qualifier)
            qualifier = {'Output': 'B'}
            self.WriteStatus('VideoMuteXI', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        sign = match.group(1).decode()
        value = int(match.group(2).decode())
        if sign == '-':
            value *= -1
        self.WriteStatus('Volume', value, None)

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
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Invalid command for this configuration',
            '17': 'Invalid command for signal type',
            '22': 'Busy',
            '24': 'Privilege violation',
            '28': 'Bad filename or file not found',
            '33': 'Bad file type or size'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: ' + match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.EchoDisabled = True
        self.VerboseDisabled = True
        self.lastLogoAvailabilityUpdate = 0
        
    def extr_17_2211_non_plus(self):

        self.NonXIModel = True
        self.NonPlusModel = True

        self.OutputFormatStateValues = {
            'Auto': '0',
            'DVI RGB 444': '1',
            'HDMI RGB 444 Full': '2',
            'HDMI RGB 444 Limited': '3',
            'HDMI YUV 444 Limited': '5',
            'HDMI YUV 422 Limited': '7'
        }

    def extr_17_2211_plus(self):

        self.NonXIModel = True
        self.NonPlusModel = False

        self.OutputFormatStateValues = {
            'Auto': '0',
            'DVI RGB 444': '1',
            'HDMI RGB 444 Full': '2',
            'HDMI RGB 444 Limited': '3',
            'HDMI YUV 444 Limited': '5',
            'HDMI YUV 422 Limited': '7',
            'HDMI YUV 420 Limited': '9'
        }

    def extr_17_2211_plus_xi(self):

        self.NonXIModel = False
        self.NonPlusModel = False

        self.OutputValue = {
            '1': 'A',
            '2': 'B'
        }

        self.OutputStates = {
            'A': '1',
            'B': '2'
        }

        self.OutputFormatStateValues = {
            'Auto': '0',
            'DVI RGB 444': '1',
            'HDMI RGB 444 Full': '2',
            'HDMI RGB 444 Limited': '3',
            'HDMI YUV 444 Limited': '5',
            'HDMI YUV 422 Limited': '7',
            'HDMI YUV 420 Limited': '9'
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
