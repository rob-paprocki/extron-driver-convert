from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
            'AudioCrosspointGain': {'Parameters': ['Output', 'Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'AudioRoute': {'Parameters': ['Channel'], 'Status': {}},
            'AudioVolume': {'Parameters': ['Channel'], 'Status': {}},
            'CameraStandby': {'Parameters': ['Camera'], 'Status': {}},
            'Focus': {'Parameters': ['Camera', 'Focus Speed'], 'Status': {}},
            'FocusMode': {'Parameters': ['Camera'], 'Status': {}},
            'Home': {'Parameters': ['Camera'], 'Status': {}},
            'Input': { 'Status': {}},
            'IPStreaming': { 'Status': {}},
            'Pan': {'Parameters': ['Camera', 'Pan Speed'], 'Status': {}},
            'PIPLayout': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'PresetRecall': {'Parameters': ['Camera'], 'Status': {}},
            'PresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'StreamingSettingStatus': {'Parameters': ['Type'], 'Status': {}},
            'Tilt': {'Parameters': ['Camera', 'Tilt Speed'], 'Status': {}},
            'Trigger': {'Parameters':['Index','Block'], 'Status': {}},
            'VideoMute': {'Parameters': ['Channel'], 'Status': {}},
            'VideoType': {'Parameters': ['Channel'], 'Status': {}},
            'Zoom': {'Parameters': ['Camera', 'Zoom Speed'], 'Status': {}},
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'login:'), self.__MatchUsername, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)

        self.SetRegex = re.compile(b'OK\r\n|login:|Password:|ERROR\r\n')
        self.UpdateRegex = {
            'AudioCrosspointGain'    : '(\-?\d+\.\d+)\r\n',
            'AudioMute'              : 'mute:[ ]{0,9}(on|off)\r\n',
            'AudioVolume'            : 'volume:?[ ]{0,9}(\-?\d+\.\d) dB\r\n',
            'AudioRoute'             : '\[[ ]{0,9}(line_in_[12]|usb3_playback_(left|right)|hdmi_in_[12]_(left|right)|dante_in_[1-4])[ ]{0,9}\]\r\n',
            'CameraStandby'          : 'standby:[ ]{0,9}(on|off)\r\n',
            'FocusMode'              : 'auto_focus:[ ]{0,9}(on|off)\r\n',
            'Input'                  : 'source:[ ]{0,9}(?:input)? ?([12])\r\n',
            'IPStreaming'            : 'enabled:[ ]{0,9}(true|false)\r\n',
            'Power'                  : 'standby:[ ]{0,9}(on|off)\r\n',
            'StreamingSettingStatus' : '[\s\S]+?>',
            'VideoMute'              : 'mute:[ ]{0,9}(on|off)\r\n',
            'VideoType'              : 'input type:[ ]{0,9}(camera|video)\r\n',
        }
        
        self.StreamingPattern  = re.compile('IP Custom_Frame_Rate ([\s\S]+)\r\nIP Custom_Resolution ([\s\S]+)\r\n'
                                       'IP Enabled ([\s\S]+)\r\nIP MTU ([\s\S]+)\r\nIP Port ([\s\S]+)\r\n'
                                       'IP Preset_Quality ([\s\S]+)\r\nIP Preset_Resolution ([\s\S]+)\r\n'
                                       'IP Protocol ([\s\S]+)\r\nIP URL ([\s\S]+)\r\nIP Video_Mode ([\s\S]+)\r\n'
                                       'USB Active ([\s\S]+)\r\nUSB Device ([\s\S]+)\r\nUSB Frame_Rate ([\s\S]+)\r\n'
                                       'USB Resolution ([\s\S]+)\r\nUSB Version ([\s\S]+)\r\nOK')
        
    def SetSendUsername(self, value, qualifier):

        self.Send(self.deviceUsername + '\r\n')

    def SetSendPassword(self, value, qualifier):

        self.Send(self.devicePassword + '\r\n')

    def __MatchUsername(self, match, tag):

        self.SetSendUsername( None, None)

    def __MatchPassword(self, match, tag):

        self.SetSendPassword( None, None)

    def SetAudioCrosspointGain(self, value, qualifier):

        OutputStates = {
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        InputStates = {
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4'
        }

        if -12 <= value <= 12 and qualifier['Output'] in OutputStates and qualifier['Input'] in InputStates:
            AudioCrosspointGainCmdString = 'audio {output} crosspoint-gain {input} set {level}\r\n'.format(output=qualifier['Output'].replace(' ', '_').lower(),
                                                                                                           input=qualifier['Input'].replace(' ', '_').lower(),
                                                                                                           level=value)
            self.__SetHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioCrosspointGain')

    def UpdateAudioCrosspointGain(self, value, qualifier):

        OutputStates = {
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        InputStates = {
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4'
        }

        if qualifier['Output'] in OutputStates and qualifier['Input'] in InputStates:
            AudioCrosspointGainCmdString = 'audio {output} crosspoint-gain {input} get\r\n'.format(output=qualifier['Output'].replace(' ', '_').lower(),
                                                                                                   input=qualifier['Input'].replace(' ', '_').lower())
            res = self.__UpdateHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(re.search(self.UpdateRegex['AudioCrosspointGain'], res).group(1)))
                    self.WriteStatus('AudioCrosspointGain', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Audio Crosspoint Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioCrosspointGain')

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4',
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        if value in ['On', 'Off'] and qualifier['Channel'] in ChannelStates:
            AudioMuteCmdString = 'audio {channel} mute {state}\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower(),
                                                                           state=value.lower())
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4',
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioMuteCmdString = 'audio {channel} mute get\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower())
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = re.search(self.UpdateRegex['AudioMute'], res).group(1).title()
                    self.WriteStatus('AudioMute', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetAudioRoute(self, value, qualifier):

        ChannelStates = {
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        ValueStateValues = {
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4'
        }

        if value in ValueStateValues and qualifier['Channel'] in ChannelStates:
            AudioRouteCmdString = 'audio {channel} route set {input}\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower(),
                                                                                 input=value.replace(' ', '_').lower())
            self.__SetHelper('AudioRoute', AudioRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioRoute')

    def UpdateAudioRoute(self, value, qualifier):

        ChannelStates = {
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        ValueStateValues = {
            'line_in_1'          : 'Line In 1',
            'line_in_2'          : 'Line In 2',
            'usb3_playback_left' : 'USB3 Playback Left',
            'usb3_playback_right': 'USB3 Playback Right',
            'hdmi_in_1_left'     : 'HDMI In 1 Left',
            'hdmi_in_1_right'    : 'HDMI In 1 Right',
            'hdmi_in_2_left'     : 'HDMI In 2 Left',
            'hdmi_in_2_right'    : 'HDMI In 2 Right',
            'dante_in_1'         : 'Dante In 1',
            'dante_in_2'         : 'Dante In 2',
            'dante_in_3'         : 'Dante In 3',
            'dante_in_4'         : 'Dante In 4'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioRouteCmdString = 'audio {channel} route get\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower())
            res = self.__UpdateHelper('AudioRoute', AudioRouteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[re.search(self.UpdateRegex['AudioRoute'], res).group(1)]
                    self.WriteStatus('AudioRoute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Route: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioRoute')

    def SetAudioVolume(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4',
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        if -50 <= value <= 20 and qualifier['Channel'] in ChannelStates:
            AudioVolumeCmdString = 'audio {channel} volume set {level}\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower(),
                                                                                   level=value)
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Line In 1',
            'Line In 2',
            'USB3 Playback Left',
            'USB3 Playback Right',
            'HDMI In 1 Left',
            'HDMI In 1 Right',
            'HDMI In 2 Left',
            'HDMI In 2 Right',
            'Dante In 1',
            'Dante In 2',
            'Dante In 3',
            'Dante In 4',
            'Line Out 1',
            'Line Out 2',
            'USB3 Record Left',
            'USB3 Record Right',
            'IP Out Left',
            'IP Out Right',
            'HDMI Out Left',
            'HDMI Out Right',
            'Dante Out 1',
            'Dante Out 2',
            'Dante Out 3',
            'Dante Out 4'
        }

        if qualifier['Channel'] in ChannelStates:
            AudioVolumeCmdString = 'audio {channel} volume get\r\n'.format(channel=qualifier['Channel'].replace(' ', '_').lower())
            res = self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = int(float(re.search(self.UpdateRegex['AudioVolume'], res).group(1)))
                    self.WriteStatus('AudioVolume', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Audio Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioVolume')

    def SetCameraStandby(self, value, qualifier):

        if value in ['On', 'Off'] and qualifier['Camera'] in '12':
            CameraStandbyCmdString = 'camera {camera} standby {state}\r\n'.format(camera=qualifier['Camera'], state=value.lower())
            self.__SetHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraStandby')

    def UpdateCameraStandby(self, value, qualifier):

        if qualifier['Camera'] in '12':
            CameraStandbyCmdString = 'camera {camera} standby get\r\n'.format(camera=qualifier['Camera'])
            res = self.__UpdateHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
            if res:
                try:
                    value = re.search(self.UpdateRegex['CameraStandby'], res).group(1).title()
                    self.WriteStatus('CameraStandby', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Camera Standby: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCameraStandby')

    def SetFocus(self, value, qualifier):

        focusSpd = int(qualifier['Focus Speed'])

        ValueStateValues = {
            'Near': 'near {}'.format(focusSpd),
            'Far' : 'far {}'.format(focusSpd),
            'Stop': 'stop'
        }

        if value in ValueStateValues and qualifier['Camera'] in '12' and 1 <= focusSpd <= 8:
            FocusCmdString = 'camera {camera} focus {state}\r\n'.format(camera=qualifier['Camera'], state=ValueStateValues[value])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetFocusMode(self, value, qualifier):

        if value in ['Auto', 'Manual'] and qualifier['Camera'] in '12':
            FocusModeCmdString = 'camera {camera} focus mode {state}\r\n'.format(camera=qualifier['Camera'], state=value.lower())
            self.__SetHelper('FocusMode', FocusModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusMode')

    def UpdateFocusMode(self, value, qualifier):

        ValueStateValues = {
            'on' : 'Auto',
            'off': 'Manual'
        }

        if qualifier['Camera'] in '12':
            FocusModeCmdString = 'camera {camera} focus mode get\r\n'.format(camera=qualifier['Camera'])
            res = self.__UpdateHelper('FocusMode', FocusModeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[re.search(self.UpdateRegex['FocusMode'], res).group(1)]
                    self.WriteStatus('FocusMode', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Focus Mode: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateFocusMode')

    def SetHome(self, value, qualifier):

        if qualifier['Camera'] in '12':
            HomeCmdString = 'camera {camera} home\r\n'.format(camera=qualifier['Camera'])
            self.__SetHelper('Home', HomeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHome')

    def SetInput(self, value, qualifier):

        if value in '12':
            InputCmdString = 'video program source set input{state}\r\n'.format(state=value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'video program source get\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = re.search(self.UpdateRegex['Input'], res).group(1)
                self.WriteStatus('Input', value, qualifier)
            except (AttributeError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetIPStreaming(self, value, qualifier):

        if value in ['On', 'Off']:
            IPStreamingCmdString = 'streaming ip enable {state}\r\n'.format(state=value.lower())
            self.__SetHelper('IPStreaming', IPStreamingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPStreaming')

    def UpdateIPStreaming(self, value, qualifier):

        ValueStateValues = {
            'true' : 'On',
            'false': 'Off'
        }

        IPStreamingCmdString = 'streaming ip enable get\r\n'
        res = self.__UpdateHelper('IPStreaming', IPStreamingCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(self.UpdateRegex['IPStreaming'], res).group(1)]
                self.WriteStatus('IPStreaming', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IP Streaming: Invalid/unexpected response'])

    def SetPan(self, value, qualifier):

        panSpd = int(qualifier['Pan Speed'])

        ValueStateValues = {
            'Left' : 'left {}'.format(panSpd),
            'Right': 'right {}'.format(panSpd),
            'Stop' : 'stop'
        }

        if value in ValueStateValues and qualifier['Camera'] in '12' and 1 <= panSpd <= 24:
            PanCmdString = 'camera {camera} pan {state}\r\n'.format(camera=qualifier['Camera'], state=ValueStateValues[value])
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPIPLayout(self, value, qualifier):

        ValueStateValues = {
            'Upper Right' : 'upper_right', 
            'Lower Right' : 'lower_right', 
            'Lower Left'  : 'lower_left', 
            'Upper Left'  : 'upper_left', 
            'Top Bottom'  : 'top_bottom', 
            'Left Right'  : 'left_right'
        }

        PIPLayoutCmdString = 'video program pip layout {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On'     : 'on', 
            'Off'    : 'off',
            'Toggle' : 'toggle'
        }

        PIPModeCmdString = 'video program pip {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'off',
            'Off': 'on'
        }

        if value in ValueStateValues:
            PowerCmdString = 'system standby {state}\r\n'.format(state=ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'off': 'On',
            'on' : 'Off'
        }

        PowerCmdString = 'system standby get\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[re.search(self.UpdateRegex['Power'], res).group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetPresetRecall(self, value, qualifier):

        if qualifier['Camera'] in '12' and 1 <= int(value) <= 16:
            PresetRecallCmdString = 'camera {camera} preset recall {preset}\r\n'.format(camera=qualifier['Camera'], preset=value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')
    def SetPresetSave(self, value, qualifier):


        if qualifier['Camera'] in '12' and 1 <= int(value) <= 16:
            PresetSaveCmdString = 'camera {camera} preset store {preset}\r\n'.format(camera=qualifier['Camera'], preset=value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdateStreamingSettingStatus(self, value, qualifier):

        TypeStates = ('IP Custom Frame Rate', 'IP Custom Resolution', 'IP Enabled', 'IP MTU', 'IP Port',
                        'IP Preset Quality', 'IP Preset Resolution', 'IP Protocol', 'IP URL', 'IP Video Mode',
                        'USB Active', 'USB Device', 'USB Frame Rate', 'USB Resolution', 'USB Version')
                        
        type_val = qualifier['Type']
        if type_val in TypeStates:
            StreamingSettingStatusCmdString = 'streaming settings get\r\n'
            res = self.__UpdateHelper('StreamingSettingStatus', StreamingSettingStatusCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.StreamingPattern, res)
                    for i in range(0, 15):
                        self.WriteStatus('StreamingSettingStatus', temp_value.group(i + 1).strip().title(), {'Type': TypeStates[i]})
                except (IndexError, AttributeError):
                    self.Error(['Streaming Setting Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStreamingSettingStatus')

    def SetTilt(self, value, qualifier):


        tiltSpd = int(qualifier['Tilt Speed'])

        ValueStateValues = {
            'Up'  : 'up {}'.format(tiltSpd),
            'Down': 'down {}'.format(tiltSpd),
            'Stop': 'stop'
        }

        if value in ValueStateValues and qualifier['Camera'] in '12':
            TiltCmdString = 'camera {camera} tilt {state}\r\n'.format(camera=qualifier['Camera'], state=ValueStateValues[value])
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetTrigger(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }
        index_val = int(qualifier['Index'])
        block_sec = int(qualifier['Block'])

        if value in ValueStateValues and 1 <= index_val <= 10 and block_sec >= 0:
            if block_sec == 0:
                TriggerCmdString = 'trigger {0} {1}\r\n'.format(index_val, ValueStateValues[value])
            else:
                TriggerCmdString = 'trigger {0} {1} block {2}\r\n'.format(index_val, ValueStateValues[value], block_sec)
            self.__SetHelper('Trigger', TriggerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrigger')

    def SetVideoMute(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Input 1',
            'Input 2'
        }

        if value in ['On', 'Off'] and qualifier['Channel'] in ChannelStates:
            VideoMuteCmdString = 'video {channel} mute {state}\r\n'.format(channel=qualifier['Channel'].replace(' ', '').lower(),
                                                                           state=value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ChannelStates = {
            'Master',
            'Input 1',
            'Input 2'
        }

        ValueStateValues = {
            'on' : 'On',
            'off': 'Off'
        }

        if qualifier['Channel'] in ChannelStates:
            VideoMuteCmdString = 'video {channel} mute get\r\n'.format(channel=qualifier['Channel'].replace(' ', '').lower())
            res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[re.search(self.UpdateRegex['VideoMute'], res).group(1)]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def SetVideoType(self, value, qualifier):


        ChannelStates = {
            'Input 1': 'input1',
            'Input 2': 'input2'
        }

        ValueStateValues = {
            'Camera': 'camera',
            'Video' : 'video'
        }

        if value in ValueStateValues and qualifier['Channel'] in ChannelStates:
            VideoTypeCmdString = 'video {channel} type set {state}\r\n'.format(channel=ChannelStates[qualifier['Channel']], state=ValueStateValues[value])
            self.__SetHelper('VideoType', VideoTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoType')

    def UpdateVideoType(self, value, qualifier):


        ChannelStates = {
            'Input 1': 'input1',
            'Input 2': 'input2'
        }

        ValueStateValues = {
            'camera': 'Camera',
            'video' : 'Video'
        }

        if qualifier['Channel'] in ChannelStates:
            VideoTypeCmdString = 'video {channel} type get\r\n'.format(channel=ChannelStates[qualifier['Channel']])
            res = self.__UpdateHelper('VideoType', VideoTypeCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[re.search(self.UpdateRegex['VideoType'], res).group(1)]
                    self.WriteStatus('VideoType', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Type: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoType')

    def SetZoom(self, value, qualifier):

        zoomSpd = int(qualifier['Zoom Speed'])

        ValueStateValues = {
            'In'  : 'in {}'.format(zoomSpd),
            'Out' : 'out {}'.format(zoomSpd),
            'Stop': 'stop'
        }

        if value in ValueStateValues and qualifier['Camera'] in '12' and 1 <= zoomSpd <= 7:
            ZoomCmdString = 'camera {camera} zoom {state}\r\n'.format(camera=qualifier['Camera'], state=ValueStateValues[value])
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'login:' in response:
            self.SetSendUsername( None, None)
            return ''
        elif 'Password:' in response:
            self.SetSendPassword( None, None)
            return ''
        elif 'ERROR\r\n' in response:
            self.Error(['Invalid/Unexpected Response: {0}'.format(sourceCmdName)])
            return ''
        else:
            return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            res = res.decode()
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            regex = re.compile('{}|login:|Password:|ERROR\r\n'.format(self.UpdateRegex[command]).encode())
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex)
            res = res.decode()
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

