from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog
import re


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
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioCrosspointGain': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'AudioInputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'AudioMatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'AudioOutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'AutoFocus': {'Parameters': ['Camera'], 'Status': {}},
            'EasyMICMute': {'Parameters': ['Channel'], 'Status': {}},
            'EasyMICVolume': {'Parameters': ['Channel'], 'Status': {}},
            'Focus': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'LineInMute': {'Parameters': ['Channel'], 'Status': {}},
            'LineInVolume': {'Parameters': ['Channel'], 'Status': {}},
            'LineOutMute': {'Parameters': ['Channel'], 'Status': {}},
            'LineOutVolume': {'Parameters': ['Channel'], 'Status': {}},
            'MasterMute': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'Pan': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'PIP': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PresetRecall': {'Parameters': ['Camera'], 'Status': {}},
            'PresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'ProgramInput': {'Status': {}},
            'Standby': {'Parameters': ['Camera'], 'Status': {}},
            'StreamInput': {'Status': {}},
            'Tilt': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'USBMute': {'Parameters': ['Channel'], 'Status': {}},
            'USBVolume': {'Parameters': ['Channel'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Zoom': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
        }

        self.LastOutputUpdate = {'Line Out 1': 0, 'Line Out 2': 0, 'Line Out 3': 0, 'Line Out 4': 0, 'USB Record': 0, 'HDMI': 0}
        self.Authenticated = True       

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Login incorrect'), self.__MatchLoginIncorrect, None)
            self.AddMatchString(re.compile(b'Welcome'), self.__MatchAuthenticationSuccess, None)
        AudioCrosspointGainPattern = re.compile(rb'\x1B\[0m(?P<gain>-?[\.0-9]+)\x1B\[0m\r\n|ERROR\r\n')
        AudioOutputTieStatusPattern = re.compile(rb'\[( | usb_playback | line_in_[1-4] | easy_mic_[1-4] | auto_mic_mix | hdmi_in )\]\r\n|ERROR\r\n')
        InputPattern = re.compile(rb'source:\s+(input[1-4]|stream)\r\n|ERROR\r\n')
        MutePattern = re.compile(rb'mute:\s+(?P<mute>on|off)\r\n|ERROR\r\n')
        VolumePattern = re.compile(rb'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n|ERROR\r\n')

        self.REPatterns = {
            'AudioCrosspointGain': AudioCrosspointGainPattern,
            'AudioOutputTieStatus': AudioOutputTieStatusPattern,
            'EasyMICMute': MutePattern,
            'EasyMICVolume': VolumePattern,
            'LineInMute': MutePattern,
            'LineInVolume': VolumePattern,
            'LineOutMute': MutePattern,
            'LineOutVolume': VolumePattern,
            'MasterMute': MutePattern,
            'MasterVolume': VolumePattern,
            'ProgramInput': InputPattern,
            'StreamInput': InputPattern,
            'USBMute': MutePattern,
            'USBVolume': VolumePattern,
            'VideoMute': MutePattern
        }

    def __MatchLogin(self, match, tag):
        self.Authenticated = False
        self.SetSendLogin(None, None)

    def SetSendLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r')

    def __MatchPassword(self, match, tag):
        self.Authenticated = False
        self.SetSendPassword(None, None)

    def SetSendPassword(self, value, qualifier):
        self.Send(self.devicePassword + '\r')

    def __MatchLoginIncorrect(self, match, tag):
        self.Error(['Incorrect login'])

    def __MatchAuthenticationSuccess(self, match, tag):
        self.Authenticated = True

    def SetAudioCrosspointGain(self, value, qualifier):

        InputStates = {
            'Line In 1': 'line_in_1',
            'Line In 2': 'line_in_2',
            'Line In 3': 'line_in_3',
            'Line In 4': 'line_in_4',
            'Auto Mic Mix': 'auto_mic_mix',
            'EasyMIC 1': 'easy_mic_1',
            'EasyMIC 2': 'easy_mic_2',
            'EasyMIC 3': 'easy_mic_3',
            'EasyMIC 4': 'easy_mic_4',
            'USB Playback': 'usb_playback',
            'HDMI': 'hdmi_in'
        }

        OutputStates = {
            'Line Out 1': 'line_out_1',
            'Line Out 2': 'line_out_2',
            'Line Out 3': 'line_out_3',
            'Line Out 4': 'line_out_4',
            'USB Record': 'usb_record',
            'HDMI': 'hdmi_out'
        }

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioCrosspointGainCmdString = 'audio {0} crosspoint-gain {1} set {2:.1f}\r'.format(OutputStates[qualifier['Output']], InputStates[qualifier['Input']], value)
            self.__SetHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioCrosspointGain')

    def UpdateAudioCrosspointGain(self, value, qualifier):

        InputStates = {
            'Line In 1': 'line_in_1',
            'Line In 2': 'line_in_2',
            'Line In 3': 'line_in_3',
            'Line In 4': 'line_in_4',
            'Auto Mic Mix': 'auto_mic_mix',
            'EasyMIC 1': 'easy_mic_1',
            'EasyMIC 2': 'easy_mic_2',
            'EasyMIC 3': 'easy_mic_3',
            'EasyMIC 4': 'easy_mic_4',
            'USB Playback': 'usb_playback',
            'HDMI': 'hdmi_in'
        }

        OutputStates = {
            'Line Out 1': 'line_out_1',
            'Line Out 2': 'line_out_2',
            'Line Out 3': 'line_out_3',
            'Line Out 4': 'line_out_4',
            'USB Record': 'usb_record',
            'HDMI': 'hdmi_out'
        }

        AudioCrosspointGainCmdString = 'audio {0} crosspoint-gain {1} get\r'.format(OutputStates[qualifier['Output']], InputStates[qualifier['Input']])
        res = self.__UpdateHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'\x1B\[0m(?P<gain>-?[\.0-9]+)\x1B\[0m\r\n', res).group('gain'))
                self.WriteStatus('AudioCrosspointGain', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AudioCrosspointGain: Invalid/unexpected response'])

    def UpdateAudioInputTieStatus(self, value, qualifier):

        output = qualifier['Output']
        if output in ['Line Out 1', 'Line Out 2', 'Line Out 3', 'Line Out 4', 'USB Record', 'HDMI']:
            self.UpdateAudioOutputTieStatus(value, {'Output': output})

    def SetAudioMatrixTieCommand(self, value, qualifier):

        InputStates = {
            'Line In 1': 'line_in_1',
            'Line In 2': 'line_in_2',
            'Line In 3': 'line_in_3',
            'Line In 4': 'line_in_4',
            'Auto Mic Mix': 'auto_mic_mix',
            'EasyMIC 1': 'easy_mic_1',
            'EasyMIC 2': 'easy_mic_2',
            'EasyMIC 3': 'easy_mic_3',
            'EasyMIC 4': 'easy_mic_4',
            'USB Playback': 'usb_playback',
            'None': '',
            'HDMI': 'hdmi_in'
        }

        OutputStates = {
            'Line Out 1': 'line_out_1',
            'Line Out 2': 'line_out_2',
            'Line Out 3': 'line_out_3',
            'Line Out 4': 'line_out_4',
            'USB Record': 'usb_record',
            'HDMI': 'hdmi_out'
        }
        AudioMatrixTieCommandCmdString = 'audio {0} route set {1}\r'.format(OutputStates[qualifier['Output']], InputStates[qualifier['Input']])
        self.__SetHelper('AudioMatrixTieCommand', AudioMatrixTieCommandCmdString, value, qualifier)

    def UpdateAudioOutputTieStatus(self, value, qualifier):

        OutputStates = {
            'Line Out 1': 'line_out_1',
            'Line Out 2': 'line_out_2',
            'Line Out 3': 'line_out_3',
            'Line Out 4': 'line_out_4',
            'USB Record': 'usb_record',
            'HDMI': 'hdmi_out'
        }

        InputValues = {
            'line_in_1': 'Line In 1',
            'line_in_2': 'Line In 2',
            'line_in_3': 'Line In 3',
            'line_in_4': 'Line In 4',
            'auto_mic_mix': 'Auto Mic Mix',
            'easy_mic_1': 'EasyMIC 1',
            'easy_mic_2': 'EasyMIC 2',
            'easy_mic_3': 'EasyMIC 3',
            'easy_mic_4': 'EasyMIC 4',
            'usb_playback': 'USB Playback',
            'hdmi_in': 'HDMI'
        }

        output = qualifier['Output']
     
        AudioOutputTieStatusCmdString = 'audio {0} route get\r'.format(OutputStates[output])
        res = self.__UpdateHelper('AudioOutputTieStatus', AudioOutputTieStatusCmdString, value, qualifier)
        if res:
            try:
                inputRes = re.search(r'\[( | usb_playback | line_in_[1-4] | easy_mic_[1-4] | auto_mic_mix | hdmi_in )\]\r\n', res).group(1).strip()
                if inputRes == '':
                    inputValue = 'None'
                else:
                    inputValue = InputValues[inputRes]
            except (KeyError, IndexError):
                self.Error(['AudioOutputTieStatus: Invalid/unexpected response'])
            else:
                for input in InputValues.keys():
                    if input != inputRes or inputRes == '':
                        self.WriteStatus('AudioInputTieStatus', 'Untied', {'Input': InputValues[input], 'Output': output})
                    else:
                        self.WriteStatus('AudioInputTieStatus', 'Tied', {'Input': inputValue, 'Output': output})
                self.WriteStatus('AudioOutputTieStatus', inputValue, qualifier)
        

    def SetAutoFocus(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        ValueStateValues = {
            'On': 'auto',
            'Off': 'manual'
        }

        AutoFocusCmdString = 'camera {0} focus mode {1}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetEasyMICMute(self, value, qualifier):

        ChannelStates = {
            '1': 'easy_mic_1',
            '2': 'easy_mic_2',
            '3': 'easy_mic_3',
            '4': 'easy_mic_4'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        EasyMICMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('EasyMICMute', EasyMICMuteCmdString, value, qualifier)

    def UpdateEasyMICMute(self, value, qualifier):

        ChannelStates = {
            '1': 'easy_mic_1',
            '2': 'easy_mic_2',
            '3': 'easy_mic_3',
            '4': 'easy_mic_4'
        }

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        EasyMICMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('EasyMICMute', EasyMICMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('EasyMICMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['EastMICMute: Invalid/unexpected response'])

    def SetEasyMICVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'easy_mic_1',
            '2': 'easy_mic_2',
            '3': 'easy_mic_3',
            '4': 'easy_mic_4'
        }

        ValueConstraints = {
            'Min': -42,
            'Max': 6
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            EasyMICVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('EasyMICVolume', EasyMICVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEasyMICVolume')

    def UpdateEasyMICVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'easy_mic_1',
            '2': 'easy_mic_2',
            '3': 'easy_mic_3',
            '4': 'easy_mic_4'
        }

        EasyMICVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('EasyMICVolume', EasyMICVolumeCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n', res).group('volume'))
                self.WriteStatus('EasyMICVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['EasyMicVolume: Invalid/unexpected response'])

    def SetFocus(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        SpeedStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            'Near': 'near',
            'Far': 'far',
            'Stop': 'stop'
        }

        FocusCmdString = 'camera {0} focus {1} {2}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value], '' if value == 'Stop' else SpeedStates[qualifier['Speed']])
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetLineInMute(self, value, qualifier):

        ChannelStates = {
            '1': 'line_in_1',
            '2': 'line_in_2',
            '3': 'line_in_3',
            '4': 'line_in_4',
            'HDMI': 'hdmi_in'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        LineInMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('LineInMute', LineInMuteCmdString, value, qualifier)

    def UpdateLineInMute(self, value, qualifier):

        ChannelStates = {
            '1': 'line_in_1',
            '2': 'line_in_2',
            '3': 'line_in_3',
            '4': 'line_in_4',
            'HDMI': 'hdmi_in'
        }

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        LineInMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('LineInMute', LineInMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('LineInMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LineInMute: Invalid/unexpected response'])

    def SetLineInVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'line_in_1',
            '2': 'line_in_2',
            '3': 'line_in_3',
            '4': 'line_in_4',
            'HDMI': 'hdmi_in'
        }

        ValueConstraints = {
            'Min': -50,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LineInVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('LineInVolume', LineInVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInVolume')

    def UpdateLineInVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'line_in_1',
            '2': 'line_in_2',
            '3': 'line_in_3',
            '4': 'line_in_4',
            'HDMI': 'hdmi_in'
        }

        LineInVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('LineInVolume', LineInVolumeCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n', res).group('volume'))
                self.WriteStatus('LineInVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LineInVolume: Invalid/unexpected response'])

    def SetLineOutMute(self, value, qualifier):

        ChannelStates = {
            '1': 'line_out_1',
            '2': 'line_out_2',
            '3': 'line_out_3',
            '4': 'line_out_4',
            'HDMI': 'hdmi_out'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        LineOutMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('LineOutMute', LineOutMuteCmdString, value, qualifier)

    def UpdateLineOutMute(self, value, qualifier):

        ChannelStates = {
            '1': 'line_out_1',
            '2': 'line_out_2',
            '3': 'line_out_3',
            '4': 'line_out_4',
            'HDMI': 'hdmi_out'
        }

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        LineOutMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('LineOutMute', LineOutMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('LineOutMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LineOutMute: Invalid/unexpected response'])

    def SetLineOutVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'line_out_1',
            '2': 'line_out_2',
            '3': 'line_out_3',
            '4': 'line_out_4',
            'HDMI': 'hdmi_out'
        }

        ValueConstraints = {
            'Min': -50,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LineOutVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('LineOutVolume', LineOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutVolume')

    def UpdateLineOutVolume(self, value, qualifier):

        ChannelStates = {
            '1': 'line_out_1',
            '2': 'line_out_2',
            '3': 'line_out_3',
            '4': 'line_out_4',
            'HDMI': 'hdmi_out'
        }

        LineOutVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('LineOutVolume', LineOutVolumeCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n', res).group('volume'))
                self.WriteStatus('LineOutVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['LineOutVolume: Invalid/unexpected response'])

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        MasterMuteCmdString = 'audio master mute {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)

    def UpdateMasterMute(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        MasterMuteCmdString = 'audio master mute get\r'
        res = self.__UpdateHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('MasterMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['MasterMute: Invalid/unexpected response'])

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -50,
            'Max': 20
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = 'audio master volume set {0:.1f}\r'.format(value)
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterVolume')

    def UpdateMasterVolume(self, value, qualifier):

        MasterVolumeCmdString = 'audio master volume get\r'
        res = self.__UpdateHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n', res).group('volume'))
                self.WriteStatus('MasterVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['MasterVolume: Invalid/unexpected response'])

    def SetPan(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        SpeedStates = {
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
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24'
        }

        ValueStateValues = {
            'Left': 'left',
            'Right': 'right',
            'Stop': 'stop'
        }

        PanCmdString = 'camera {0} pan {1} {2}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value], '' if value == 'Stop' else SpeedStates[qualifier['Speed']])
        self.__SetHelper('Pan', PanCmdString, value, qualifier)

    def SetPIP(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        PIPCmdString = 'video stream pip {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIP', PIPCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'input1',
            '2': 'input2',
            '3': 'input3',
            '4': 'input4'
        }

        PIPInputCmdString = 'video stream pip inset {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

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
            '16': '16'
        }

        PresetRecallCmdString = 'camera {0} preset recall {1}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

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
            '16': '16'
        }

        PresetSaveCmdString = 'camera {0} preset store {1}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetProgramInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'input1',
            '2': 'input2',
            '3': 'input3',
            '4': 'input4',
            'Stream Input': 'stream'
        }

        ProgramInputCmdString = 'video program source set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ProgramInput', ProgramInputCmdString, value, qualifier)

    def UpdateProgramInput(self, value, qualifier):

        ValueStateValues = {
            'input1': '1',
            'input2': '2',
            'input3': '3',
            'input4': '4',
            'stream': 'Stream Input'
        }

        ProgramInputCmdString = 'video program source get\r'
        res = self.__UpdateHelper('ProgramInput', ProgramInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'source:\s+(input[1-4]|stream)\r\n', res).group(1)]
                self.WriteStatus('ProgramInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ProgramInput: Invalid/unexpected response'])

    def SetStandby(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }
        StandbyCmdString = 'camera {0} standby {1}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def SetStreamInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'input1',
            '2': 'input2',
            '3': 'input3',
            '4': 'input4'
        }

        StreamInputCmdString = 'video stream source set {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('StreamInput', StreamInputCmdString, value, qualifier)

    def UpdateStreamInput(self, value, qualifier):

        ValueStateValues = {
            'input1': '1',
            'input2': '2',
            'input3': '3',
            'input4': '4'
        }

        StreamInputCmdString = 'video stream source get\r'
        res = self.__UpdateHelper('StreamInput', StreamInputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'source:\s+(input[1-4]|stream)\r\n', res).group(1)]
                self.WriteStatus('StreamInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['StreamInput: Invalid/unexpected response'])

    def SetTilt(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        SpeedStates = {
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
            '17': '17',
            '18': '18',
            '19': '19',
            '20': '20'
        }

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Stop': 'stop'
        }

        TiltCmdString = 'camera {0} tilt {1} {2}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value], '' if value == 'Stop' else SpeedStates[qualifier['Speed']])
        self.__SetHelper('Tilt', TiltCmdString, value, qualifier)

    def SetUSBMute(self, value, qualifier):

        ChannelStates = {
            'Record': 'usb_record',
            'Playback': 'usb_playback'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        USBMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[qualifier['Channel']], ValueStateValues[value])
        self.__SetHelper('USBMute', USBMuteCmdString, value, qualifier)

    def UpdateUSBMute(self, value, qualifier):

        ChannelStates = {
            'Record': 'usb_record',
            'Playback': 'usb_playback'
        }

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        USBMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('USBMute', USBMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('USBMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['USBMute: Invalid/unexpected response'])

    def SetUSBVolume(self, value, qualifier):

        ChannelStates = {
            'Record': 'usb_record',
            'Playback': 'usb_playback'
        }

        ValueConstraints = {
            'Min': -42,
            'Max': 6
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            USBVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[qualifier['Channel']], value)
            self.__SetHelper('USBVolume', USBVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBVolume')

    def UpdateUSBVolume(self, value, qualifier):

        ChannelStates = {
            'Record': 'usb_record',
            'Playback': 'usb_playback'
        }

        USBVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[qualifier['Channel']])
        res = self.__UpdateHelper('USBVolume', USBVolumeCmdString, value, qualifier)
        if res:
            try:
                value = float(re.search(r'volume:?\s+(?P<volume>\-?\d+\.?\d+) dB\r\n', res).group('volume'))
                self.WriteStatus('USBVolume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['USBVolume: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        VideoMuteCmdString = 'video mute {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        VideoMuteCmdString = 'video mute get\r'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(r'mute:\s+(?P<mute>on|off)\r\n', res).group('mute')]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def SetZoom(self, value, qualifier):

        CameraStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        SpeedStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        ValueStateValues = {
            'In': 'in',
            'Out': 'out',
            'Stop': 'stop'
        }

        ZoomCmdString = 'camera {0} zoom {1} {2}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value], '' if value == 'Stop' else SpeedStates[qualifier['Speed']])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'ERROR' in response:
            self.Error(['{}: ERROR'.format(sourceCmdName)])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Authenticated: 
            if self.Unidirectional == 'True':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'>')
                if not res:
                    self.Error(['{}: Invalid/unexpected response'.format(command)])
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Error(['Not Authenticated'])

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.Authenticated:        
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
                return ''
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.REPatterns[command])
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Error(['Not Authenticated'])            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.LastOutputUpdate = {'Line Out 1': 0, 'Line Out 2': 0, 'Line Out 3': 0, 'Line Out 4': 0, 'USB Record': 0, 'HDMI': 0}
        self.Authenticated = True
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
