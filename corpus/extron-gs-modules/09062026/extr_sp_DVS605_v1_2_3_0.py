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
        self.deviceUsername = 'admin'
        self.devicePassword = None
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Input'], 'Status': {}},
            'AudioFollow': { 'Status': {}},
            'InputGain': { 'Status': {}},
            'AudioFormat': {'Parameters':['Input'], 'Status': {}},
            'AudioMute': { 'Status': {}},
            'AudioOutputFormat': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'DetectedVideoInputFormat': {'Parameters':['Input'], 'Status': {}},
            'EffectDuration': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'FilmMode': {'Parameters':['Input'], 'Status': {}},
            'Freeze': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Parameters':['Output'], 'Status': {}},
            'OutputFormat': { 'Status': {}},
            'Input': {'Parameters':['Type'], 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'InputPresetSave': { 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'PIPInput': { 'Status': {}},
            'PIPPresetRecall': {'Parameters':['Inputs'], 'Status': {}},
            'PIPPresetSave': { 'Status': {}},
            'PIPSwap': { 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'UserPresetRecall': { 'Status': {}},
            'UserPresetSave': { 'Status': {}},
            'VideoEffect': { 'Status': {}},
            'InputSignalType': {'Parameters':['Input'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

        self.VerboseDisabled = True
        self.EchoDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Aspr0([1-5])\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'Aflw([0-2])\r\n'), self.__MatchAudioFollow, None)
            self.AddMatchString(re.compile(b'Aud([+-])(\d+)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'AfmtI0([1-5])\*([0-5])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'AfmtO([12])\r\n'), self.__MatchAudioOutputFormat, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Vtyp0([1-5])\*([0-7])\r\n'), self.__MatchDetectedVideoInputFormat, None)
            self.AddMatchString(re.compile(b'Edur(\d+)\r\n'), self.__MatchEffectDuration, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Film0([1-5])\*([01])\r\n'), self.__MatchFilmMode, None)
            self.AddMatchString(re.compile(b'Frz([0-3])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(re.compile(b'HdcpE0([345])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI0([1-5])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([12])\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Vtpo([0-6])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(re.compile(b'In0([1-5]) (All|RGB|Aud)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'In\d+ ([01])\*([01])\*([01])\*([01])\*([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Rate(\d+)\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'Pip0([0-4])\r\n'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'Psav([01])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(b'(\d+)Stat (\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(re.compile(b'Test([0-9]{2})\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(re.compile(b'Swef([01])\r\n'), self.__MatchVideoEffect, None)
            self.AddMatchString(re.compile(b'Typ0([1-5])\*([0-7])\r\n'), self.__MatchInputSignalType, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([+-])(\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E([0-3][0-9])\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'(Echo0|w0echo)\r\n'), self.__MatchEchoMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def __MatchEchoMode(self, match, qualifier):

        self.EchoDisabled = False
    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            'Fill'   : '1',
            'Follow' : '2'
        }

        InputValue = int(qualifier['Input'])
        if value in AspectRatioState and 1 <= InputValue <= 5:
            AspectRatioCmdString = 'W{0}*{1}ASPR\r'.format(InputValue, AspectRatioState[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def UpdateAspectRatio(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            AspectRatioCmdString = 'W{0}ASPR\r'.format(InputValue)
            self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAspectRatio')

    def __MatchAspectRatio(self, match, qualifier):

        AspectRatioName = {
            '1' : 'Fill',
            '2' : 'Follow'
        }

        value = AspectRatioName[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Input' : match.group(1).decode()})

    def SetAudioFollow(self, value, qualifier):

        AudioFollowState = {
            'Follow Main'   : '0',
            'Follow PIP'    : '1',
            'Toggle Source' : '2'
        }

        if value in AudioFollowState:
            AudioFollowCmdString = 'W{0}AFLW\r'.format(AudioFollowState[value])
            self.__SetHelper('AudioFollow', AudioFollowCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFollow')

    def UpdateAudioFollow(self, value, qualifier):

        AudioFollowCmdString = 'WAFLW\r'
        self.__UpdateHelper('AudioFollow', AudioFollowCmdString, value, qualifier)

    def __MatchAudioFollow(self, match, tag):

        AudioFollowName = {
            '0' : 'Follow Main',
            '1' : 'Follow PIP',
        }

        value = AudioFollowName[match.group(1).decode()]
        self.WriteStatus('AudioFollow', value, None)

    def SetInputGain(self, value, qualifier):

        if -53 <= value <= 24:
            if value < 0:
                self.__SetHelper('InputGain', '-{0}G'.format(abs(value)), value, qualifier)
            else:
                self.__SetHelper('InputGain', '+{0}G'.format(abs(value)), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        self.__UpdateHelper('InputGain', 'G', value, qualifier)

    def __MatchInputGain(self, match, fncN):

        value = int(match.group(2))
        if match.group(1) == b'-':
            value = value * -1
        if -53 <= value <= 24:
            self.WriteStatus('InputGain', value, None)

    def SetAudioFormat(self, value, qualifier):

        AudioFormatState={
            'Off'                   : '0',
            'Analog'                : '1',
            'Digital 1 (2Ch)'       : '2',
            'Digital 2 (Full)'      : '3',
            'Digital 3 (2Ch Auto)'  : '4',
            'Digital 4 (Full Auto)' : '5',
        }

        InputValue = int(qualifier['Input'])
        if value in AudioFormatState and  1 <= InputValue <= 5:
            AudioFormatCmdString = 'WI{0}*{1}AFMT\r'.format(InputValue, AudioFormatState[value])
            self.__SetHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            AudioFormatCmdString = 'WI{0}AFMT\r'.format(InputValue)
            self.__UpdateHelper('AudioFormat', AudioFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioFormat')

    def __MatchAudioFormat(self, match, qualifier):

        AudioFormatName={
            '0' : 'Off',
            '1' : 'Analog',
            '2' : 'Digital 1 (2Ch)',
            '3' : 'Digital 2 (Full)',
            '4' : 'Digital 3 (2Ch Auto)',
            '5' : 'Digital 4 (Full Auto)'
        }

        value = AudioFormatName[match.group(2).decode()]
        self.WriteStatus('AudioFormat', value, {'Input': match.group(1).decode()})

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        if value in AudioMuteState:
            AudioMuteCmdString = '{0}Z'.format(AudioMuteState[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteName={
            '1' : 'On',
            '0' : 'Off'
        }

        value = AudioMuteName[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAudioOutputFormat(self, value, qualifier):

        AudioOutputFormatState = {
            'Dual Mono' : '1',
            'Stereo'    : '2'
        }

        if value in AudioOutputFormatState:
            AudioOutputFormatCmdString = 'WO{0}AFMT\r'.format(AudioOutputFormatState[value])
            self.__SetHelper('AudioOutputFormat', AudioOutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputFormat')

    def UpdateAudioOutputFormat(self, value, qualifier):

        AudioOutputFormatCmdString = 'WOAFMT\r'
        self.__UpdateHelper('AudioOutputFormat', AudioOutputFormatCmdString, value, qualifier)

    def __MatchAudioOutputFormat(self, match, tag):

        AudioOutputFormatName = {
            '1' : 'Dual Mono',
            '2' : 'Stereo',
        }

        value = AudioOutputFormatName[match.group(1).decode()]
        self.WriteStatus('AudioOutputFormat', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageState = {
            'Execute'           :'0',
            'Execute and Fill'  :'1',
            'Execute and Follow':'2',
        }

        if value in AutoImageState:
            AutoImageCmdString = '{0}*A'.format(AutoImageState[value])
            self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoImage')
    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeState = {
            'Off'                   : '0',
            'Highest Active Input'  : '1',
            'Lowest Active Input'   : '2',
        }

        if value in AutoSwitchModeState:
            AutoSwitchModeCmdString = 'W{0}AUSW\r'.format(AutoSwitchModeState[value])
            self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoSwitchMode')

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'WAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeName = {
            '0' : 'Off',
            '1' : 'Highest Active Input',
            '2' : 'Lowest Active Input',
        }

        value = AutoSwitchModeName[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def UpdateDetectedVideoInputFormat(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            DetectedVideoInputFormatCmdString = '{0}*\\'.format(InputValue)
            self.__UpdateHelper('DetectedVideoInputFormat', DetectedVideoInputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDetectedVideoInputFormat')

    def __MatchDetectedVideoInputFormat(self, match, qualifier):

        VideoInputFormatName={
            '0' : 'No Signal',
            '1' : 'RGB',
            '2' : 'YUV Auto',
            '3' : 'RGBcvS',
            '4' : 'S-Video',
            '5' : 'Composite',
            '6' : 'DVI/HDMI',
        }

        value = VideoInputFormatName[match.group(2).decode()]
        self.WriteStatus('DetectedVideoInputFormat', value, {'Input' : match.group(1).decode()})

    def SetEffectDuration(self, value, qualifier):

        if 0.2 <= value <= 5.0:
            sisValue = round(value*10)
            EffectDurationCmdString = 'W{0}EDUR\r'.format(sisValue)
            self.__SetHelper('EffectDuration', EffectDurationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEffectDuration')

    def UpdateEffectDuration(self, value, qualifier):

        EffectDurationCmdString = 'WEDUR\r'
        self.__UpdateHelper('EffectDuration', EffectDurationCmdString, value, qualifier)

    def __MatchEffectDuration(self, match, fncN):

        value = float(int(match.group(1))/10)
        self.WriteStatus('EffectDuration', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1' : '1',
            'Mode 2' : '2',
            'Off'    : '0'
        }

        if value in ExecutiveModeState:
            ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def UpdateExecutiveMode(self, value, qualifier):


        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            '1' : 'Mode 1',
            '2' : 'Mode 2',
            '0' : 'Off',
        }


        value = ExecutiveModeName[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFilmMode(self, value, qualifier):

        FilmModeState = {
            'On' : '1',
            'Off' : '0',
        }

        InputValue = int(qualifier['Input'])
        if value in FilmModeState and 1 <= InputValue <= 5:
            FilmModeCmdString = 'W{0}*{1}FILM\r'.format(InputValue, FilmModeState[value])
            self.__SetHelper('FilmMode', FilmModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFilmMode')

    def UpdateFilmMode(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            FilmModeCmdString = 'W{0}FILM\r'.format(InputValue)
            self.__UpdateHelper('FilmMode', FilmModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFilmMode')

    def __MatchFilmMode(self, match, qualifier):

        FilmModeName = {
            '1' : 'On',
            '0' : 'Off',
        }

        value = FilmModeName[match.group(2).decode()]
        self.WriteStatus('FilmMode', value, {'Input': match.group(1).decode()})

    def SetFreeze(self, value, qualifier):

        FreezeState={
            'Off'           : '0',
            'Freeze All'    : '1',
            'Freeze Main'   : '2',
            'Freeze PIP'    : '3',
        }

        if value in FreezeState:
            FreezeCmdString = '{0}F'.format(FreezeState[value])
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):

        FreezeName = {
            '0' : 'Off',
            '1' : 'Freeze All',
            '2' : 'Freeze Main',
            '3' : 'Freeze PIP'
        }

        value = FreezeName[match.group(1).decode()]
        self.WriteStatus('Freeze', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationState = {
            'On'  : '1',
            'Off' : '0',
        }

        InputValue = int(qualifier['Input'])
        if value in HDCPInputAuthorizationState and 3 <= InputValue <= 5:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(InputValue, HDCPInputAuthorizationState[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 3 <= InputValue <= 5:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r'.format(InputValue)
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, qualifier):

        HDCPInputAuthorizationName={
            '1' : 'On',
            '0' : 'Off',
        }

        value = HDCPInputAuthorizationName[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input' : match.group(1).decode()})

    def UpdateHDCPInputStatus(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            HDCPInputStatusCmdString = 'WI{0}HDCP\r'.format(InputValue)
            self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def __MatchHDCPInputStatus(self, match, qualifier):

        HDCPInputStatusName = {
            '0' : 'No Source Device Detected',
            '1' : 'Source Detected with HDCP',
            '2' : 'Source Detected without HDCP',
        }

        value = HDCPInputStatusName[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, {'Input' : match.group(1).decode()})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        OutputValue = int(qualifier['Output'])
        if 1 <= OutputValue <= 2:
            HDCPOutputStatusCmdString = 'WO{0}HDCP\r'.format(OutputValue)
            self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPOutputStatus(self, match, qualifier):

        HDCPOutputStatusName={
            '0' : 'No Sink Device Detected',
            '1' : 'Sink Detected with HDCP',
            '2' : 'Sink Detected without HDCP'
        }

        value = HDCPOutputStatusName[match.group(2).decode()]
        self.WriteStatus('HDCPOutputStatus', value, {'Output' : match.group(1).decode()})

    def SetOutputFormat(self, value, qualifier):

        OutputFormatState={
            'Auto'                  : '0',
            'DVI'                   : '1',
            'HDMI 444 RGB'          : '2',
            'HDMI 444 YUV Full'     : '3',
            'HDMI 444 YUV Limited'  : '4',
            'HDMI 422 YUV Full'     : '5',
            'HDMI 422 YUV Limited'  : '6'
        }

        if value in OutputFormatState:
            OutputFormatCmdString = 'W{0}VTPO\r'.format(OutputFormatState[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        OutputFormatCmdString = 'WVTPO\r'
        self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def __MatchOutputFormat(self, match, tag):

        OutputFormatName = {
            '0' : 'Auto',
            '1' : 'DVI',
            '2' : 'HDMI 444 RGB',
            '3' : 'HDMI 444 YUV Full',
            '4' : 'HDMI 444 YUV Limited',
            '5' : 'HDMI 422 YUV Full',
            '6' : 'HDMI 422 YUV Limited'
        }

        value = OutputFormatName[match.group(1).decode()]
        self.WriteStatus('OutputFormat', value, None)

    def SetInput(self, value, qualifier):

        TieTypeState = {
            'Audio/Video'   : '!',
            'Video'         : '&',
            'Audio'         : '$'
        }

        if 1 <= int(value) <= 5 and qualifier['Type'] in TieTypeState:
            InputCmdString = '{0}{1}'.format(value, TieTypeState[qualifier['Type']])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        TieTypeState = {
            'Audio/Video' : '!',
            'Video' : '&',
            'Audio' : '$'
        }

        if qualifier['Type'] in TieTypeState:
            self.__UpdateHelper('Input', '{0}'.format(TieTypeState[qualifier['Type']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, qualifier):

        TieTypeName = {
            'All' : 'Audio/Video',
            'RGB' : 'Video',
            'Aud' : 'Audio'
        }
        othertype = None
        value = str(int(match.group(1).decode()))
        Type = TieTypeName[match.group(2).decode()]
        qualifier = {'Type' : Type}
        self.WriteStatus('Input', value, qualifier)

        if Type != 'Audio/Video':
            otherType = 'Video' if Type == 'Audio' else 'Audio'
            if self.ReadStatus('Input', {'TieType': othertype}) == value:
                self.WriteStatus('Input', value, {'Type' : 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
        else:
            self.WriteStatus('Input', value, {'Type' : 'Video'})
            self.WriteStatus('Input', value, {'Type' : 'Audio'})

    def SetInputPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('InputPresetRecall', '2*{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')
    def SetInputPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            self.__SetHelper('InputPresetSave', '2*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')
    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatusName = {
            '1' : 'Active',
            '0' : 'Not Active',
        }

        value1 = InputSignalStatusName[match.group(1).decode()]
        self.WriteStatus('InputSignalStatus', value1, {'Input' : '1'})
        value2 = InputSignalStatusName[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', value2, {'Input' : '2'})
        value3 = InputSignalStatusName[match.group(3).decode()]
        self.WriteStatus('InputSignalStatus', value3, {'Input' : '3'})
        value4 = InputSignalStatusName[match.group(4).decode()]
        self.WriteStatus('InputSignalStatus', value4, {'Input' : '4'})
        value5 = InputSignalStatusName[match.group(5).decode()]
        self.WriteStatus('InputSignalStatus', value5, {'Input' : '5'})

    def SetOutputResolution(self, value, qualifier):

        OutputResolutionState={ 
            'Custom EDID 1':'3',        'Custom EDID 2':'4',     'Custom EDID 3':'5',
            'Custom EDID 4':'6',        'Custom EDID 5':'7',
            '640x480 (50Hz)':'10',      '640x480 (60Hz)':'11',   '640x480 (75Hz)':'12',
            '800x600 (50Hz)':'13',      '800x600 (60Hz)':'14',   '800x600 (75Hz)':'15',
            '852x480 (50Hz)':'16',      '852x480 (60Hz)':'17',   '852x480 (75Hz)':'18',
            '1024x768 (50Hz)':'19',     '1024x768 (60Hz)':'20',  '1024x768 (75Hz)':'21',
            '1024x852 (50Hz)':'22',     '1024x852 (60Hz)':'23',  '1024x852 (75Hz)':'24',
            '1024x1024 (50Hz)':'25',    '1024x1024 (60Hz)':'26', '1024x1024 (75Hz)':'27',
            '1280x768 (50Hz)':'28',     '1280x768 (60Hz)':'29',  '1280x768 (75Hz)':'30',
            '1280x800 (50Hz)':'31',     '1280x800 (60Hz)':'32',  '1280x800 (75Hz)':'33',
            '1280x1024 (50Hz)':'34',    '1280x1024 (60Hz)':'35', '1280x1024 (75Hz)':'36',
            '1360x765 (50Hz)':'37',     '1360x765 (60Hz)':'38',  '1360x765 (75Hz)':'39',
            '1360x768 (50Hz)':'40',     '1360x768 (60Hz)':'41',  '1360x768 (75Hz)':'42',
            '1365x768 (50Hz)':'43',     '1365x768 (60Hz)':'44',  '1365x768 (75Hz)':'45',
            '1366x768 (50Hz)':'46',     '1366x768 (60Hz)':'47',  '1366x768 (75Hz)':'48',
            '1365x1024 (50Hz)':'49',    '1365x1024 (60Hz)':'50', '1365x1024 (75Hz)':'51',
            '1400x900 (50Hz)':'52',     '1400x900 (60Hz)':'53',  '1400x900 (75Hz)':'54',
            '1400x1050 (50Hz)':'55',    '1400x1050 (60Hz)':'56',
            '1600x900 (50Hz)':'57',     '1600x900 (60Hz)':'58',
            '1680x1050 (50Hz)':'59',    '1680x1050 (60Hz)':'60',
            '1600x1200 (50Hz)':'61',    '1600x1200 (60Hz)':'62',
            '1920x1200 (50Hz)':'63',    '1920x1200 (60Hz)':'64',
            '480p (59.94Hz)':'65',      '480p (60Hz)':'66',
            '576p (50Hz)':'67',
            '720p (25Hz)':'68',         '720p (29.97Hz)':'69',   '720p (30Hz)':'70',      '720p (50Hz)':'71',         '720p (59.94Hz)':'72',   '720p (60Hz)':'73',
            '1080i (50Hz)':'74',        '1080i (59.94Hz)':'75',  '1080i (60Hz)':'76',
            '1080p (23.98Hz)':'77',     '1080p (24Hz)':'78',     '1080p (25Hz)':'79',     '1080p (29.97Hz)':'80',     '1080p (30Hz)':'81',     '1080p (50Hz)':'82',     '1080p (59.94Hz)':'83',     '1080p (60Hz)':'84',
            '2048x1080 (23.98Hz)':'85', '2048x1080 (24Hz)':'86', '2048x1080 (25Hz)':'87', '2048x1080 (29.97Hz)':'88', '2048x1080 (30Hz)':'89', '2048x1080 (50Hz)':'90', '2048x1080 (59.94Hz)':'91', '2048x1080 (60Hz)':'92',
        }

        if value in OutputResolutionState:
            OutputResolutionCmdString = 'W{0}RATE\r'.format(OutputResolutionState[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def UpdateOutputResolution(self, value, qualifier):

        self.__UpdateHelper('OutputResolution', 'WRATE\r', value, qualifier)

    def __MatchOutputResolution(self, match, qualifier):
        OutputResolutionName={
             3:'Custom EDID 1',        4:'Custom EDID 2',     5:'Custom EDID 3',
             6:'Custom EDID 4',        7:'Custom EDID 5',
            10:'640x480 (50Hz)',      11:'640x480 (60Hz)',   12:'640x480 (75Hz)',
            13:'800x600 (50Hz)',      14:'800x600 (60Hz)',   15:'800x600 (75Hz)',
            16:'852x480 (50Hz)',      17:'852x480 (60Hz)',   18:'852x480 (75Hz)',
            19:'1024x768 (50Hz)',     20:'1024x768 (60Hz)',  21:'1024x768 (75Hz)',
            22:'1024x852 (50Hz)',     23:'1024x852 (60Hz)',  24:'1024x852 (75Hz)',
            25:'1024x1024 (50Hz)',    26:'1024x1024 (60Hz)', 27:'1024x1024 (75Hz)',
            28:'1280x768 (50Hz)',     29:'1280x768 (60Hz)',  30:'1280x768 (75Hz)',
            31:'1280x800 (50Hz)',     32:'1280x800 (60Hz)',  33:'1280x800 (75Hz)',
            34:'1280x1024 (50Hz)',    35:'1280x1024 (60Hz)', 36:'1280x1024 (75Hz)',
            37:'1360x765 (50Hz)',     38:'1360x765 (60Hz)',  39:'1360x765 (75Hz)',
            40:'1360x768 (50Hz)',     41:'1360x768 (60Hz)',  42:'1360x768 (75Hz)',
            43:'1365x768 (50Hz)',     44:'1365x768 (60Hz)',  45:'1365x768 (75Hz)',
            46:'1366x768 (50Hz)',     47:'1366x768 (60Hz)',  48:'1366x768 (75Hz)',
            49:'1365x1024 (50Hz)',    50:'1365x1024 (60Hz)', 51:'1365x1024 (75Hz)',
            52:'1400x900 (50Hz)',     53:'1400x900 (60Hz)',  54:'1400x900 (75Hz)',
            55:'1400x1050 (50Hz)',    56:'1400x1050 (60Hz)',
            57:'1600x900 (50Hz)',     58:'1600x900 (60Hz)',
            59:'1680x1050 (50Hz)',    60:'1680x1050 (60Hz)',
            61:'1600x1200 (50Hz)',    62:'1600x1200 (60Hz)',
            63:'1920x1200 (50Hz)',    64:'1920x1200 (60Hz)',
            65:'480p (59.94Hz)',      66:'480p (60Hz)',
            67:'576p (50Hz)',
            68:'720p (25Hz)',         69:'720p (29.97Hz)',   70:'720p (30Hz)',      71:'720p (50Hz)',         72:'720p (59.94Hz)',   73:'720p (60Hz)',
            74:'1080i (50Hz)',        75:'1080i (59.94Hz)',  76:'1080i (60Hz)',
            77:'1080p (23.98Hz)',     78:'1080p (24Hz)',     79:'1080p (25Hz)',     80:'1080p (29.97Hz)',     81:'1080p (30Hz)',     82:'1080p (50Hz)',     83:'1080p (59.94Hz)',     84:'1080p (60Hz)',
            85:'2048x1080 (23.98Hz)', 86:'2048x1080 (24Hz)', 87:'2048x1080 (25Hz)', 88:'2048x1080 (29.97Hz)', 89:'2048x1080 (30Hz)', 90:'2048x1080 (50Hz)', 91:'2048x1080 (59.94Hz)', 92:'2048x1080 (60Hz)',
        }

        value = OutputResolutionName[int(match.group(1))]
        self.WriteStatus('OutputResolution', value, None)

    def SetPIPInput(self, value, qualifier):

        PIPInputState = {
            'Off' : '0',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4'
        }

        if value in PIPInputState:
            PIPInputCmdString = 'W{0}PIP\r'.format(PIPInputState[value])
            self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPInput')

    def UpdatePIPInput(self, value, qualifier):

        PIPInputCmdString = 'WPIP\r'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, qualifier):

        PIPInputName={
            '0' : 'Off',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
        }

        value = PIPInputName[match.group(1).decode()]
        self.WriteStatus('PIPInput', value, None)

    def SetPIPPresetRecall(self, value, qualifier):

        InputStates = {
        	'With Inputs'    : '4',
        	'Without Inputs' : '3'
        }

        if 1 <= int(value) <= 16 and qualifier['Inputs'] in InputStates:
            self.__SetHelper('PIPPresetRecall', '{0}*{1}.'.format(InputStates[qualifier['Inputs']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPresetRecall')
    def SetPIPPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('PIPPresetSave', '4*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPPresetSave')
    def SetPIPSwap(self, value, qualifier):

        self.__SetHelper('PIPSwap', '%', value, qualifier)
    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeState = {
            'On'  : '1',
            'Off' : '0'         
        }

        if value in PowerSaveModeState:
            PowerSaveModeCmdString = 'W{0}PSAV\r'.format(PowerSaveModeState[value])
            self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerSaveMode')

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'WPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, qualifier):

        PowerSaveModeName = {
            '1' : 'On',
            '0' : 'Off'           
        }

        value = PowerSaveModeName[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('Temperature', value, None)

    def SetTestPattern(self, value, qualifier):

        TestPatternState = {
            'Off' : '0',
            'Crop' : '1',
            'Alternating Pixels' : '2',
            'Alternating Lines' : '3',
            'Crosshatch' : '4',
            '4x4 Crosshatch' : '5',
            'Color Bars' : '6',
            'Grayscale' : '7',
            'Ramp' : '8',
            'White Field' : '9',
            '1:33 Aspect Ratio' : '10',
            '1.78 Aspect Ratio' : '11',
            '1.85 Aspect Ratio' : '12',
            '2.35 Aspect Ratio' : '13',
            'Blue Mode' : '14'
        }

        if value in TestPatternState:
            TestPatternCmdString = 'W{0}TEST\r'.format(TestPatternState[value])
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def UpdateTestPattern(self, value, qualifier):

        TestPatternCmdString = 'WTEST\r'
        self.__UpdateHelper('TestPattern', TestPatternCmdString, value, qualifier)

    def __MatchTestPattern(self, match, qualifier):

        TestPatternState={
            '00' : 'Off',
            '01' : 'Crop',
            '02' : 'Alternating Pixels',
            '03' : 'Alternating Lines',
            '04' : 'Crosshatch',
            '05' : '4x4 Crosshatch',
            '06' : 'Color Bars',
            '07' : 'Grayscale',
            '08' : 'Ramp',
            '09' : 'White Field',
            '10': '1:33 Aspect Ratio',
            '11': '1.78 Aspect Ratio',
            '12': '1.85 Aspect Ratio',
            '13': '2.35 Aspect Ratio',
            '14': 'Blue Mode'
        }

        value = TestPatternState[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, None)

    def SetUserPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('UserPresetRecall', '1*{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetRecall')
    def SetUserPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 16:
            self.__SetHelper('UserPresetSave', '1*{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetSave')
    def SetVideoEffect(self, value, qualifier):

        VideoEffectState = {
            'Cut'       : '0',
            'Dissolve'  : '1'
        }

        if value in VideoEffectState:
            VideoEffectCmdString = 'W{0}SWEF\r'.format(VideoEffectState[value])
            self.__SetHelper('VideoEffect', VideoEffectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoEffect')

    def UpdateVideoEffect(self, value, qualifier):

        VideoEffectCmdString = 'WSWEF\r'
        self.__UpdateHelper('VideoEffect', VideoEffectCmdString, value, qualifier)

    def __MatchVideoEffect(self, match, qualifier):

        VideoEffectName={
            '0' : 'Cut',
            '1' : 'Dissolve'
        }

        value = VideoEffectName[match.group(1).decode()]
        self.WriteStatus('VideoEffect', value, None)

    def SetInputSignalType(self, value, qualifier):

        InputSignalTypeState={
            'RGB' : '1',
            'YUV Auto' : '2',
            'RGBcvS' : '3',
            'S-Video' : '4',
            'Composite' : '5',
            'DVI/HDMI' : '6',
            'Auto detect' : '7'
        }

        InputValue = int(qualifier['Input'])
        if value in InputSignalTypeState and 1 <= InputValue <= 5:
            InputSignalTypeCmdString = '{0}*{1}\\'.format(InputValue, InputSignalTypeState[value])
            self.__SetHelper('InputSignalType', InputSignalTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSignalType')

    def UpdateInputSignalType(self, value, qualifier):

        InputValue = int(qualifier['Input'])
        if 1 <= InputValue <= 5:
            InputSignalTypeCmdString= '{0}\\'.format(InputValue)
            self.__UpdateHelper('InputSignalType', InputSignalTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignalType')

    def __MatchInputSignalType(self, match, qualifier):

        InputSignalTypeName = {
            '1' : 'RGB',
            '2' : 'YUV Auto',
            '3' : 'RGBcvS',
            '4' : 'S-Video',
            '5' : 'Composite',
            '6' : 'DVI/HDMI',
            '7' : 'Auto detect',
        }

        value = InputSignalTypeName[match.group(2).decode()]
        self.WriteStatus('InputSignalType', value, {'Input' : match.group(1).decode()})

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off' : '0',
            'On with Sync' : '2',
            'On' : '1'
        }

        if value in VideoMuteState:
            VideoMuteCmdString = '{0}B'.format(VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteName = {
            '0' : 'Off',
            '2' : 'On with Sync',
            '1' : 'On',
        }

        value = VideoMuteName[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def SetVolume(self, value, qualifier):

        if -100 <= value <= 0:
            self.__SetHelper('Volume', '{0}V'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'V', value, qualifier)

    def __MatchVolume(self, match, fncN):

        value = int(match.group(2))
        if match.group(1) == b'-':
            value = value * -1
        if -100 <= value <= 0:
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
               
    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid channel number (too large)',
            '06' : 'Invalid switch attempt in this mode',
            '10' : 'Invalid Command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid value (out of range)',
            '14' : 'Command not available for this configuration',
            '17' : 'Invalid Command for signal type',
            '22' : 'Busy',
            '24' : 'Privilege violation',
            '25' : 'Device not present',
            '26' : 'Maximum number of connections exceeded',
            '28' : 'Bad filename or file not found',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: '+ match.group(0).decode()]) 

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0


    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.EchoDisabled = True
        
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
