from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AnalogVideoFormat': {'Parameters': ['Input'], 'Status': {}},
            'AudioInputFormat': {'Parameters': ['Input'], 'Status': {}},
            'AudioMuteGroup5': {'Status': {}},
            'BassGroup3': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GroupBass': {'Parameters': ['Group'], 'Status': {}},
            'GroupInputGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMicPremixerGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMicLineGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMixpointGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'GroupOutputGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupPostswitcherGain': {'Parameters': ['Group'], 'Status': {}},
            'GroupPreswitcherTrim': {'Parameters': ['Group'], 'Status': {}},
            'GroupTreble': {'Parameters': ['Group'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'HDMIAudioMute': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'MicPremixerGain': {'Parameters': ['Input'], 'Status': {}},
            'MicMute': {'Parameters': ['Input'], 'Status': {}},
            'MicVolumeGroup2': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'ProgramVolumeGroup1': {'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'TrebleGroup4': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.MaxInput = 8
        self.MaxMic = 2

        self.GroupFunction = {
            '1': 'ProgramVolumeGroup1',
            '2': 'MicVolumeGroup2',
            '3': 'BassGroup3',
            '4': 'TrebleGroup4',
            '5': 'AudioMuteGroup5'
        }

        self.MaxGroups = 32
        self.LevelTypes = {
            'BassGroup3': {'Min': -24, 'Max': 24},
            'GroupBass': {'Min': -24, 'Max': 24},
            'GroupInputGain': {'Min': -18, 'Max': 24},
            'GroupMicPremixerGain': {'Min': -100, 'Max': 0},
            'GroupMicLineGain': {'Min': -18, 'Max': 80},
            'GroupMixpointGain': {'Min': -35, 'Max': 25},
            'GroupOutputGain': {'Min': -100, 'Max': 0},
            'GroupPostswitcherGain': {'Min': -100, 'Max': 0},
            'GroupPreswitcherTrim': {'Min': -12, 'Max': 12},
            'GroupTreble': {'Min': -24, 'Max': 24},
            'MicPremixerGain': {'Min': -100, 'Max': 0},
            'MicVolumeGroup2': {'Min': -100, 'Max': 0},
            'ProgramVolumeGroup1': {'Min': -100, 'Max': 0},
            'TrebleGroup4': {'Min': -24, 'Max': 24},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Inp([1-3]) Typ=([1-4])\r\n'), self.__MatchAnalogVideoFormat, None)
            self.AddMatchString(compile(b'DsD(300[0-9]{2})\*([01])\r\n'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'GrpmD([0-9]{2})\*([-+]0[0-9]{4})\r\n'), self.__MatchGroupVolume, None)
            self.AddMatchString(compile(b'HdcpI([0-3]\*?){4}\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO([0-3])'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Amt([01])\r\n'), self.__MatchHDMIAudioMute, None)
            self.AddMatchString(compile(b'(Chn|Vid|Aud)(\d+)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'Frq=([01]\*?){8}\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'DsG(4010[01])\*(\d+)\r\n'), self.__MatchMicPremixerGain, None)
            self.AddMatchString(compile(b'DsM(4000[01])\*([01])\r\n'), self.__MatchMicMute, None)
            self.AddMatchString(compile(b'Psav([01])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAnalogVideoFormat(self, value, qualifier):

        AnalogVideoFormatState = {
            'Composite': '1',
            'S-Video': '2',
            'YUV': '3',
            'RGB': '4',
        }
        input_ = int(qualifier['Input'])
        if 1 <= input_ <= 3:
            AnalogVideoFormatCmdString = '{0}*{1}\\'.format(input_, AnalogVideoFormatState[value])
            self.__SetHelper('AnalogVideoFormat', AnalogVideoFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAnalogVideoFormat')

    def UpdateAnalogVideoFormat(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= 3:
            self.__UpdateHelper('AnalogVideoFormat', '{0}\\\r\n'.format(input_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAnalogVideoFormat')

    def __MatchAnalogVideoFormat(self, match, qualifier):
        AnalogVideoFormatName = {
            b'1': 'Composite',
            b'2': 'S-Video',
            b'3': 'YUV',
            b'4': 'RGB',
        }
        value = AnalogVideoFormatName[match.group(2)]
        input_ = str(int(match.group(1)))
        self.WriteStatus('AnalogVideoFormat', value, {'Input': input_})

    def SetAudioInputFormat(self, value, qualifier):

        AudioInputFormatState = {
            'Analog': '0',
            'Digital': '1',
        }
        AudioInputNumber = {
            '5': 30008,
            '6': 30010,
            '7': 30012,
            '8': 30014,
        }
        AudioInputFormatCmdString = 'WD{0}*{1}AU\r'.format(AudioInputNumber[qualifier['Input']], AudioInputFormatState[value])
        self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        AudioInputNumber = {
            '5': 30008,
            '6': 30010,
            '7': 30012,
            '8': 30014,
        }
        AudioInputFormatCmdString = 'WD{0}AU\r'.format(AudioInputNumber[qualifier['Input']])
        self.__UpdateHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def __MatchAudioInputFormat(self, match, qualifier):
        AudioInputFormatName = {
            b'0': 'Analog',
            b'1': 'Digital',
        }
        AudioInputName = {
            b'30008': '5',
            b'30010': '6',
            b'30012': '7',
            b'30014': '8',
        }
        value = AudioInputFormatName[match.group(2)]
        input_ = AudioInputName[match.group(1)]
        self.WriteStatus('AudioInputFormat', value, {'Input': input_})

    def SetAudioMuteGroup5(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        AudioMuteCmdString = 'WD5*{0}GRPM\r'.format(AudioMuteState[value])
        self.__SetHelper('AudioMuteGroup5', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMuteGroup5(self, value, qualifier):

        self.__UpdateHelper('AudioMuteGroup5', 'WD5GRPM\r', value, qualifier)

    def SetBassGroup3(self, value, qualifier):

        if self.__CheckValidLevelValue('BassGroup3', value):
            level = int(value * 10)
            InputLevelString = 'WD3*{0}GRPM\r'.format(level)
            self.__SetHelper('BassGroup3', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBassGroup3')

    def UpdateBassGroup3(self, value, qualifier):

        InputLevelString = 'WD3GRPM\r'
        self.__UpdateHelper('BassGroup3', InputLevelString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }

        value = ExecutiveModeName[match.group(1)]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetGroupBass(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupBass', value):
            self.GroupFunction[str(group)] = 'GroupBass'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupBass', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupBass')

    def UpdateGroupBass(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupBass'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupBass', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupBass')

    def SetGroupInputGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupInputGain', value):
            self.GroupFunction[str(group)] = 'GroupInputGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupInputGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupInputGain')

    def UpdateGroupInputGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupInputGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupInputGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupInputGain')

    def SetGroupMicPremixerGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupMicPremixerGain', value):
            self.GroupFunction[str(group)] = 'GroupMicPremixerGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupMicPremixerGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMicPremixerGain')

    def UpdateGroupMicPremixerGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupMicPremixerGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMicPremixerGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMicPremixerGain')

    def SetGroupMicLineGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupMicLineGain', value):
            self.GroupFunction[str(group)] = 'GroupMicLineGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupMicLineGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMicLineGain')

    def UpdateGroupMicLineGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupMicLineGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMicLineGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMicLineGain')

    def SetGroupMixpointGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupMixpointGain', value):
            self.GroupFunction[str(group)] = 'GroupMixpointGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupMixpointGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMixpointGain')

    def UpdateGroupMixpointGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupMixpointGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMixpointGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMixpointGain')

    def SetGroupMute(self, value, qualifier):

        MuteState = {
            'On': '1',
            'Off': '0'
        }
        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupMute'
            GroupMuteString = 'WD{0}*{1}GRPM\r'.format(group, MuteState[value])
            self.__SetHelper('GroupMute', GroupMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupMute'
            group = int(qualifier['Group'])
            GroupMuteString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupMute', GroupMuteString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetGroupOutputGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupOutputGain', value):
            self.GroupFunction[str(group)] = 'GroupOutputGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupOutputGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupOutputGain')

    def UpdateGroupOutputGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupOutputGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupOutputGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupOutputGain')

    def SetGroupPostswitcherGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupPostswitcherGain', value):
            self.GroupFunction[str(group)] = 'GroupPostswitcherGain'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupPostswitcherGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPostswitcherGain')

    def UpdateGroupPostswitcherGain(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupPostswitcherGain'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPostswitcherGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupPostswitcherGain')

    def SetGroupPreswitcherTrim(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupPreswitcherTrim', value):
            self.GroupFunction[str(group)] = 'GroupPreswitcherTrim'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupPreswitcherTrim', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupPreswitcherTrim')

    def UpdateGroupPreswitcherTrim(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupPreswitcherTrim'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupPreswitcherTrim', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupPreswitcherTrim')

    def SetGroupTreble(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32 and self.__CheckValidLevelValue('GroupTreble', value):
            self.GroupFunction[str(group)] = 'GroupTreble'
            level = int(value * 10)
            InputLevelString = 'WD{0}*{1}GRPM\r'.format(group, level)
            self.__SetHelper('GroupTreble', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupTreble')

    def UpdateGroupTreble(self, value, qualifier):

        group = int(qualifier['Group'])
        if 6 <= group <= 32:
            self.GroupFunction[str(group)] = 'GroupTreble'
            InputLevelString = 'WD{0}GRPM\r'.format(group)
            self.__UpdateHelper('GroupTreble', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupTreble')

    def __MatchGroupVolume(self, match, qualifier):

        AudioMuteName = {
            0: 'Off',
            1: 'On',
        }
        value = int(match.group(2).decode())
        group = str(int(match.group(1)))
        if group in self.GroupFunction:
            qualifier = {'Group': group}
            command = self.GroupFunction[group]
            if command == 'GroupMute':
                self.WriteStatus('GroupMute', AudioMuteName[value], qualifier)
            elif command == 'AudioMuteGroup5':
                self.WriteStatus('AudioMuteGroup5', AudioMuteName[value], None)
            elif command in ['ProgramVolumeGroup1', 'MicVolumeGroup2', 'BassGroup3',
                             'TrebleGroup4']:
                value = int(value / 10)
                self.WriteStatus(command, value, None)
            else:
                value = int(value / 10)
                self.WriteStatus(command, value, qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'WIHDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, qualifier):

        HDCPInputStatusStatus = {
            '2': 'No Source Connected',
            '1': 'Source Connected and is HDCP Compliant',
            '0': 'Source Connected but not HDCP Compliant',
            '3': 'HDCP Status not known',
        }
        res = match.group(0).decode()
        res = res[5:-2]
        signal = res.split('*')
        inputNumber = 5
        for input_ in signal:
            self.WriteStatus('HDCPInputStatus', HDCPInputStatusStatus[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'WOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, qualifier):

        HDCPOutputStatusName = {
            '2': 'No Output Connected',
            '1': 'Output Connected, Source Encrypted and Output is HDCP Compliant',
            '0': 'Output Connected, Source Encrypted and Output is not HDCP Compliant',
            '3': 'Output Connected, Source is not Encrypted or not connected and Output HDCP Status not known',
        }
        value = HDCPOutputStatusName[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHDMIAudioMute(self, value, qualifier):

        HDMIAudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        HDMIAudioMuteCmdString = '{0}Z'.format(HDMIAudioMuteState[value])
        self.__SetHelper('HDMIAudioMute', HDMIAudioMuteCmdString, value, qualifier)

    def UpdateHDMIAudioMute(self, value, qualifier):

        self.__UpdateHelper('HDMIAudioMute', 'Z', value, qualifier)

    def __MatchHDMIAudioMute(self, match, qualifier):
        HDMIAudioMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        value = HDMIAudioMuteName[match.group(1)]
        self.WriteStatus('HDMIAudioMute', value, None)

    def SetInput(self, value, qualifier):

        TieTypeValue = {
            'Audio/Video': '!',
            'Video': '&',
            'Audio': '$',
        }
        input_ = int(value)
        if 0 <= input_ <= self.MaxInput:
            InputCmdString = '{0}{1}'.format(input_, TieTypeValue[qualifier['Type']])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        TieTypeValue = {
            'Audio/Video': '&$',
            'Video': '&',
            'Audio': '$',
        }
        self.__UpdateHelper('Input', '{0}'.format(TieTypeValue[qualifier['Type']]), value, qualifier)

    def __MatchInput(self, match, qualifier):
        value = int(match.group(2))
        tieType = match.group(1).decode()
        if tieType == 'Chn':
            self.WriteStatus('Input', str(value), {'Type': 'Audio/Video'})
            self.WriteStatus('Input', str(value), {'Type': 'Video'})
            self.WriteStatus('Input', str(value), {'Type': 'Audio'})
        elif tieType == 'Vid':
            self.WriteStatus('Input', str(value), {'Type': 'Video'})
            currentAudioInput = self.ReadStatus('Input', {'Type': 'Audio'})

            if currentAudioInput is None:
                self.__UpdateHelper('Input', '$', value, qualifier)
            elif value == int(currentAudioInput):
                self.WriteStatus('Input', str(value), {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

        elif tieType == 'Aud':
            self.WriteStatus('Input', str(value), {'Type': 'Audio'})
            currentVideoInput = self.ReadStatus('Input', {'Type': 'Video'})

            if currentVideoInput is None:
                self.__UpdateHelper('Input', '&', value, qualifier)
            elif value == int(currentVideoInput):
                self.WriteStatus('Input', str(value), {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', 'LS', value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatus = {
            '1': 'Active',
            '0': 'Not Active',
        }
        res = match.group(0).decode()
        res = res[4:-2]
        signal = res.split('*')
        inputNumber = 1
        for input_ in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatus[input_], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMicPremixerGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.MaxMic and self.__CheckValidLevelValue('MicPremixerGain', value):
            input_ = 40100 + (int(qualifier['Input']) - 1)
            level = 2048 + (int(value) * 10)
            InputLevelString = 'WG{0}*{1}AU\r'.format(input_, level)
            self.__SetHelper('MicPremixerGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicPremixerGain')

    def UpdateMicPremixerGain(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.MaxMic:
            input_ = 40100 + (int(qualifier['Input']) - 1)
            InputLevelString = 'WG{0}AU\r'.format(input_)
            self.__UpdateHelper('MicPremixerGain', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicPremixerGain')

    def __MatchMicPremixerGain(self, match, fncN):
        value = int((int(match.group(2)) - 2048) / 10)
        input_ = str(int(match.group(1)) - 40099)
        self.WriteStatus('MicPremixerGain', value, {'Input': input_})

    def SetMicMute(self, value, qualifier):

        MicMuteState = {
            'Off': '0',
            'On': '1',
        }
        if 1 <= int(qualifier['Input']) <= self.MaxMic:
            input_ = 40000 + (int(qualifier['Input']) - 1)
            MicMuteCmdString = 'WM{0}*{1}AU\r'.format(input_, MicMuteState[value])
            self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicMute')

    def UpdateMicMute(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.MaxMic:
            input_ = 40000 + (int(qualifier['Input']) - 1)
            self.__UpdateHelper('MicMute', 'WM{0}AU\r'.format(input_), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMicMute')

    def __MatchMicMute(self, match, qualifier):
        MicMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        value = MicMuteName[match.group(2)]
        input_ = str(int(match.group(1)) - 39999)
        self.WriteStatus('MicMute', value, {'Input': input_})

    def SetMicVolumeGroup2(self, value, qualifier):

        if self.__CheckValidLevelValue('MicVolumeGroup2', value):
            level = int(value * 10)
            InputLevelString = 'WD2*{0}GRPM\r'.format(level)
            self.__SetHelper('MicVolumeGroup2', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicVolumeGroup2')

    def UpdateMicVolumeGroup2(self, value, qualifier):

        InputLevelString = 'WD2GRPM\r'
        self.__UpdateHelper('MicVolumeGroup2', InputLevelString, value, qualifier)

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeState = {
            'Off': '0',
            'On': '1',
        }
        PowerSaveModeCmdString = 'W{0}PSAV\r'.format(PowerSaveModeState[value])
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        self.__UpdateHelper('PowerSaveMode', 'WPSAV\r', value, qualifier)

    def __MatchPowerSaveMode(self, match, qualifier):
        PowerSaveModeName = {
            b'0': 'Off',
            b'1': 'On',
        }
        value = PowerSaveModeName[match.group(1)]
        self.WriteStatus('PowerSaveMode', value, None)

    def SetProgramVolumeGroup1(self, value, qualifier):

        if self.__CheckValidLevelValue('ProgramVolumeGroup1', value):
            level = int(value * 10)
            InputLevelString = 'WD1*{0}GRPM\r'.format(level)
            self.__SetHelper('ProgramVolumeGroup1', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramVolumeGroup1')

    def UpdateProgramVolumeGroup1(self, value, qualifier):

        InputLevelString = 'WD1GRPM\r'
        self.__UpdateHelper('ProgramVolumeGroup1', InputLevelString, value, qualifier)

    def SetRecallPreset(self, value, qualifier):

        PresetConstraints = {
            'Min': 1,
            'Max': 8,
        }
        if PresetConstraints['Min'] <= int(value) <= PresetConstraints['Max']:
            PresetCmdString = '{0}.'.format(value)
            self.__SetHelper('RecallPreset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        PresetConstraints = {
            'Min': 1,
            'Max': 8,
        }
        if PresetConstraints['Min'] <= int(value) <= PresetConstraints['Max']:
            PresetCmdString = '{0},'.format(value)
            self.__SetHelper('SavePreset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetTrebleGroup4(self, value, qualifier):

        if self.__CheckValidLevelValue('TrebleGroup4', value):
            level = int(value * 10)
            InputLevelString = 'WD4*{0}GRPM\r'.format(level)
            self.__SetHelper('TrebleGroup4', InputLevelString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrebleGroup4')

    def UpdateTrebleGroup4(self, value, qualifier):

        InputLevelString = 'WD4GRPM\r'
        self.__UpdateHelper('TrebleGroup4', InputLevelString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        VideoMuteCmdString = '{0}B'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.__UpdateHelper('VideoMute', 'B', value, qualifier)

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        value = VideoMuteName[match.group(1)]
        self.WriteStatus('VideoMute', value, None)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid channel number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid output number',
            '13': 'Invalid value (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def __CheckValidLevelValue(self, command, value):

        min_ = self.LevelTypes[command]['Min']
        max_ = self.LevelTypes[command]['Max']
        if min_ <= value <= max_:
            return True
        else:
            return False

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            self.Send('w3cv\r\n')

            @Wait(0.3)
            def sendCommand():
                self.Send(commandstring)
        else:
            self.Send(commandstring)

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

            if self.VerboseDisabled:
                self.Send('w3cv\r\n')

                @Wait(0.3)
                def sendCommand():
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            print(command, 'does not support Update.')

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
        for regexString in self._compile_list:
            while True:
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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
