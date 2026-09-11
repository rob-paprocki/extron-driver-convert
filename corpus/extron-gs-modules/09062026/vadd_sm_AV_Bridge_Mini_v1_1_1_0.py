from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from collections import defaultdict
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
            'AudioRoute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'AudioRouteInputStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'AudioRouteOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'HDMIInMute': {'Parameters': ['Channel'], 'Status': {}},
            'HDMIInVolume': {'Parameters': ['Channel'], 'Status': {}},
            'IPStreamOutMute': {'Parameters': ['Channel'], 'Status': {}},
            'IPStreamOutVolume': {'Parameters': ['Channel'], 'Status': {}},
            'LineInMute': {'Parameters': ['Channel'], 'Status': {}},
            'LineInVolume': {'Parameters': ['Channel'], 'Status': {}},
            'LineOutMute': {'Parameters': ['Channel'], 'Status': {}},
            'LineOutVolume': {'Parameters': ['Channel'], 'Status': {}},
            'MasterMute': { 'Status': {}},
            'MasterVolume': { 'Status': {}},
            'Reboot': {'Parameters': ['Delay'], 'Status': {}},
            'StreamingSettingStatus': {'Parameters': ['Type'], 'Status': {}},
            'USBPlaybackMute': {'Parameters': ['Channel'], 'Status': {}},
            'USBPlaybackVolume': {'Parameters': ['Channel'], 'Status': {}},
            'USBRecordMute': {'Parameters': ['Channel'], 'Status': {}},
            'USBRecordVolume': {'Parameters': ['Channel'], 'Status': {}},
        }

        self.authenticated = True

        if 'Serial' not in self.ConnectionType:
            self.authenticated = False
        
        if self.Unidirectional == 'False' and 'Serial' not in self.ConnectionType:
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)

        self.AudioCrosspointGainPattern = re.compile('(-?\d+(?:\.\d+)?)\r\n')
        self.AudioRoutePattern = re.compile('\[( |usb3_playback_(?:left|right) |line_in_[12] |hdmi_in_(?:left|right) )\]\r\n')
        self.MutePattern       = re.compile('mute:?\s+(on|off)\r\n')
        self.StreamingPattern  = re.compile('IP Custom_Frame_Rate ([\s\S]+)\r\nIP Custom_Resolution ([\s\S]+)\r\n'
                                       'IP Enabled ([\s\S]+)\r\nIP MTU ([\s\S]+)\r\nIP Port ([\s\S]+)\r\n'
                                       'IP Preset_Quality ([\s\S]+)\r\nIP Preset_Resolution ([\s\S]+)\r\n'
                                       'IP Protocol ([\s\S]+)\r\nIP URL ([\s\S]+)\r\nIP Video_Mode ([\s\S]+)\r\n'
                                       'USB Active ([\s\S]+)\r\nUSB Device ([\s\S]+)\r\nUSB Frame_Rate ([\s\S]+)\r\n'
                                       'USB Resolution ([\s\S]+)\r\nUSB Version ([\s\S]+)\r\nOK')
        self.VolumePattern     = re.compile('volume:?\s+(-?\d+\.?\d?) dB\r\n')

    def __MatchLogin(self, match, tag):

        self.Send('admin\r\n')
        self.Send(self.devicePassword + '\r\n')

        self.authenticated = True
    
    def SetAudioCrosspointGain(self, value, qualifier):

        InputStates = {
            'Line In 1':            'line_in_1',
            'Line In 2':            'line_in_2',
            'USB Playback Left':    'usb3_playback_left',
            'USB Playback Right':   'usb3_playback_right',
            'HDMI In Left':         'hdmi_in_left',
            'HDMI In Right':        'hdmi_in_right'
        }
        input_ = qualifier['Input']

        OutputStates = {
            'Line Out 1':           'line_out_1',
            'Line Out 2':           'line_out_2',
            'USB Record Left':      'usb3_record_left',
            'USB Record Right':     'usb3_record_right',
            'IP Stream Out Left':   'ip_out_left',
            'IP Stream Out Right':  'ip_out_right'
        }
        output = qualifier['Output']

        if output in OutputStates and input_ in InputStates and -12 <= value <= 12:
            AudioCrosspointGainCmdString = 'audio {} crosspoint-gain {} set {:.02f}\r'.format(OutputStates[output], InputStates[input_], value)
            self.__SetHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioCrosspointGain')

    def UpdateAudioCrosspointGain(self, value, qualifier):

        InputStates = {
            'Line In 1':            'line_in_1',
            'Line In 2':            'line_in_2',
            'USB Playback Left':    'usb3_playback_left',
            'USB Playback Right':   'usb3_playback_right',
            'HDMI In Left':         'hdmi_in_left',
            'HDMI In Right':        'hdmi_in_right'
        }
        input_ = qualifier['Input']

        OutputStates = {
            'Line Out 1':           'line_out_1',
            'Line Out 2':           'line_out_2',
            'USB Record Left':      'usb3_record_left',
            'USB Record Right':     'usb3_record_right',
            'IP Stream Out Left':   'ip_out_left',
            'IP Stream Out Right':  'ip_out_right'
        }
        output = qualifier['Output']

        if output in OutputStates and input_ in InputStates:
            AudioCrosspointGainCmdString = 'audio {0} crosspoint-gain {1} get\r'.format(OutputStates[output], InputStates[input_])
            res = self.__UpdateHelper('AudioCrosspointGain', AudioCrosspointGainCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.AudioCrosspointGainPattern, res).group(1))

                    if -12 <= value <= 12:
                        self.WriteStatus('AudioCrosspointGain', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['Audio Crosspoint Gain: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioCrosspointGain')

    def SetAudioRoute(self, value, qualifier):

        InputStates = {
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_left', 
            'HDMI In Right'      : 'hdmi_in_right'
        }
        OutputStates = {
            'Line Out 1'          : 'line_out_1', 
            'Line Out 2'          : 'line_out_2', 
            'USB Record Left'     : 'usb3_record_left', 
            'USB Record Right'    : 'usb3_record_right', 
            'IP Stream Out Left'  : 'ip_out_left', 
            'IP Stream Out Right' : 'ip_out_right'
        }

        input_value = qualifier['Input']
        output_val = qualifier['Output']
        if output_val in OutputStates and input_value in InputStates:
            AudioRouteCmdString = 'audio {0} route set {1}\r'.format(OutputStates[output_val], InputStates[input_value])
            self.__SetHelper('AudioRoute', AudioRouteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioRoute')

    def UpdateAudioRouteInputStatus(self, value, qualifier):

        InputStates = ('Line In 1', 'Line In 2', 'USB Playback Left', 'USB Playback Right', 'HDMI In Left', 'HDMI In Right')
        OutputStates = ('Line Out 1', 'Line Out 2', 'USB Record Left', 'USB Record Right', 'IP Stream Out Left', 'IP Stream Out Right')
        input_val = qualifier['Input']
        output_val = qualifier['Output']
        if output_val in OutputStates and input_val in InputStates: 
            self.UpdateAudioRouteOutputStatus(value, {'Output': output_val})
        else:
            self.Discard('Invalid Command for UpdateAudioRouteInputStatus')

    def UpdateAudioRouteOutputStatus(self, value, qualifier):

        OutputStates = {
            'Line Out 1'          : 'line_out_1', 
            'Line Out 2'          : 'line_out_2', 
            'USB Record Left'     : 'usb3_record_left', 
            'USB Record Right'    : 'usb3_record_right', 
            'IP Stream Out Left'  : 'ip_out_left', 
            'IP Stream Out Right' : 'ip_out_right'
        }
        InputValues = {
            'line_in_1'           : 'Line In 1', 
            'line_in_2'           : 'Line In 2', 
            'usb3_playback_left'  : 'USB Playback Left', 
            'usb3_playback_right' : 'USB Playback Right', 
            'hdmi_in_left'        : 'HDMI In Left', 
            'hdmi_in_right'       : 'HDMI In Right'
        }

        output_val = qualifier['Output']
        if output_val in OutputStates:
            AudioRouteOutputStatusCmdString = 'audio {0} route get\r'.format(OutputStates[output_val])
            res = self.__UpdateHelper('AudioRouteOutputStatus', AudioRouteOutputStatusCmdString, value, qualifier)
            if res:
                try:
                    inp_res = re.search(self.AudioRoutePattern, res).group(1).strip()
                    if inp_res == '':# Based on vadd_42_1405
                        inp_value = 'No Input'
                    else:
                        inp_value = InputValues[inp_res]
                    self.WriteStatus('AudioRouteOutputStatus', inp_value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['Audio Route Output Status: Invalid/unexpected response'])
                else:
                    for inp_state in InputValues.keys():
                        if inp_state != inp_res or inp_res == '':
                            self.WriteStatus('AudioRouteInputStatus', 'Untied', {'Input' : InputValues[inp_state], 'Output' : output_val})
                        else:
                            self.WriteStatus('AudioRouteInputStatus', 'Tied', {'Input' : inp_value, 'Output' : output_val})
        else:
            self.Discard('Invalid Command for UpdateAudioRouteOutputStatus')

    def SetHDMIInMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'hdmi_in_left', 
            'Right' : 'hdmi_in_right'
        }

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            HDMIInMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('HDMIInMute', HDMIInMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIInMute')

    def UpdateHDMIInMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'hdmi_in_left', 
            'Right' : 'hdmi_in_right'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            HDMIInMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('HDMIInMute', HDMIInMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('HDMIInMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['HDMI In Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHDMIInMute')

    def SetHDMIInVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'hdmi_in_left', 
            'Right' : 'hdmi_in_right'
        }

        ValueConstraints = {
            'Min' : -42,
            'Max' : 6
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            HDMIInVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('HDMIInVolume', HDMIInVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDMIInVolume')

    def UpdateHDMIInVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'hdmi_in_left', 
            'Right' : 'hdmi_in_right'
        }
        
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            HDMIInVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('HDMIInVolume', HDMIInVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -42 <= value <= 6:
                        self.WriteStatus('HDMIInVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['HDMI In Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateHDMIInVolume')

    def SetIPStreamOutMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'ip_out_left', 
            'Right' : 'ip_out_right'
        }

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            IPStreamOutMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('IPStreamOutMute', IPStreamOutMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPStreamOutMute')

    def UpdateIPStreamOutMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'ip_out_left', 
            'Right' : 'ip_out_right'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            IPStreamOutMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('IPStreamOutMute', IPStreamOutMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('IPStreamOutMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['IP Stream Out Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIPStreamOutMute')

    def SetIPStreamOutVolume(self, value, qualifier):

        ChannelStates = {
            'Left' : 'ip_out_left', 
            'Right' : 'ip_out_right'
        }

        ValueConstraints = {
            'Min' : -42,
            'Max' : 6
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            IPStreamOutVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('IPStreamOutVolume', IPStreamOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPStreamOutVolume')

    def UpdateIPStreamOutVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'ip_out_left', 
            'Right' : 'ip_out_right'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            IPStreamOutVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('IPStreamOutVolume', IPStreamOutVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -42 <= value <= 6:
                        self.WriteStatus('IPStreamOutVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['IP Stream Out Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateIPStreamOutVolume')

    def SetLineInMute(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_in_1', 
            '2' : 'line_in_2'
        }

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            LineInMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('LineInMute', LineInMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInMute')

    def UpdateLineInMute(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_in_1', 
            '2' : 'line_in_2'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            LineInMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('LineInMute', LineInMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('LineInMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['Line In Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLineInMute')

    def SetLineInVolume(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_in_1', 
            '2' : 'line_in_2'
        }

        ValueConstraints = {
            'Min' : -50,
            'Max' : 20
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LineInVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('LineInVolume', LineInVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineInVolume')

    def UpdateLineInVolume(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_in_1', 
            '2' : 'line_in_2'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            LineInVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('LineInVolume', LineInVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -50 <= value <= 20:
                        self.WriteStatus('LineInVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['Line In Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLineInVolume')

    def SetLineOutMute(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_out_1', 
            '2' : 'line_out_2'
        }

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            LineOutMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('LineOutMute', LineOutMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutMute')

    def UpdateLineOutMute(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_out_1', 
            '2' : 'line_out_2'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            LineOutMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('LineOutMute', LineOutMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('LineOutMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['Line Out Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLineOutMute')

    def SetLineOutVolume(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_out_1', 
            '2' : 'line_out_2'
        }

        ValueConstraints = {
            'Min' : -50,
            'Max' : 20
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            LineOutVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('LineOutVolume', LineOutVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLineOutVolume')

    def UpdateLineOutVolume(self, value, qualifier):

        ChannelStates = {
            '1' : 'line_out_1', 
            '2' : 'line_out_2'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            LineOutVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('LineOutVolume', LineOutVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -50 <= value <= 20:
                        self.WriteStatus('LineOutVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['Line Out Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateLineOutVolume')

    def SetMasterMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off'
        }

        if value in ValueStateValues:
            MasterMuteCmdString = 'audio master mute {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMasterMute')

    def UpdateMasterMute(self, value, qualifier):

        ValueStateValues = {
            'on' : 'On', 
            'off' : 'Off'
        }

        MasterMuteCmdString = 'audio master mute get\r'
        res = self.__UpdateHelper('MasterMute', MasterMuteCmdString, value, qualifier)
        if res:
            try:
                temp_value = re.search(self.MutePattern, res)
                value = ValueStateValues[temp_value.group(1)]
                self.WriteStatus('MasterMute', value, qualifier)
            except (KeyError, AttributeError):
                self.Error(['Master Mute: Invalid/unexpected response'])

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -50,
            'Max' : 20
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
                value = float(re.search(self.VolumePattern, res).group(1))

                if -50 <= value <= 20:
                    self.WriteStatus('MasterVolume', value, qualifier)
            except (ValueError, AttributeError):
                self.Error(['Master Volume: Invalid/unexpected response'])

    def SetReboot(self, value, qualifier):

        delay_val = qualifier['Delay']

        if 0 <= delay_val <= 99:
            if delay_val == 0:
                RebootCmdString = 'system reboot\r'
            else:
                RebootCmdString = 'system reboot {0}\r'.format(delay_val)

            self.__SetHelper('Reboot', RebootCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetReboot')

    def UpdateStreamingSettingStatus(self, value, qualifier):

        TypeStates = ('IP Custom Frame Rate', 'IP Custom Resolution', 'IP Enabled', 'IP MTU', 'IP Port',
                        'IP Preset Quality', 'IP Preset Resolution', 'IP Protocol', 'IP URL', 'IP Video Mode',
                        'USB Active', 'USB Device', 'USB Frame Rate', 'USB Resolution', 'USB Version')
                        
        type_val = qualifier['Type']
        if type_val in TypeStates:
            StreamingSettingStatusCmdString = 'streaming settings get\r'
            res = self.__UpdateHelper('StreamingSettingStatus', StreamingSettingStatusCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.StreamingPattern, res)
                    for i in range(0, 15):
                        self.WriteStatus('StreamingSettingStatus', temp_value.group(i + 1).title(), {'Type': TypeStates[i]})
                except (IndexError, AttributeError):
                    self.Error(['Streaming Setting Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStreamingSettingStatus')

    def SetUSBPlaybackMute(self, value, qualifier):

        ChannelStates = {
            'Left' : 'usb3_playback_left', 
            'Right' : 'usb3_playback_right'
        }

        ValueStateValues = {
            'On' : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            USBPlaybackMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('USBPlaybackMute', USBPlaybackMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBPlaybackMute')

    def UpdateUSBPlaybackMute(self, value, qualifier):

        ChannelStates = {
            'Left' : 'usb3_playback_left', 
            'Right' : 'usb3_playback_right'
        }
        ValueStateValues = {
            'on' : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            USBPlaybackMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('USBPlaybackMute', USBPlaybackMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('USBPlaybackMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['USB Playback Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBPlaybackMute')

    def SetUSBPlaybackVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'usb3_playback_left', 
            'Right' : 'usb3_playback_right'
        }

        ValueConstraints = {
            'Min' : -42,
            'Max' : 6
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            USBPlaybackVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('USBPlaybackVolume', USBPlaybackVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBPlaybackVolume')

    def UpdateUSBPlaybackVolume(self, value, qualifier):

        ChannelStates = {
            'Left' : 'usb3_playback_left', 
            'Right' : 'usb3_playback_right'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            USBPlaybackVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('USBPlaybackVolume', USBPlaybackVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -42 <= value <= 6:
                        self.WriteStatus('USBPlaybackVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['USB Playback Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBPlaybackVolume')

    def SetUSBRecordMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'usb3_record_left', 
            'Right' : 'usb3_record_right'
        }

        ValueStateValues = {
            'On'  : 'on', 
            'Off' : 'off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and value in ValueStateValues:
            USBRecordMuteCmdString = 'audio {0} mute {1}\r'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('USBRecordMute', USBRecordMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBRecordMute')

    def UpdateUSBRecordMute(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'usb3_record_left', 
            'Right' : 'usb3_record_right'
        }
        ValueStateValues = {
            'on'  : 'On', 
            'off' : 'Off'
        }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            USBRecordMuteCmdString = 'audio {0} mute get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('USBRecordMute', USBRecordMuteCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.MutePattern, res)
                    value = ValueStateValues[temp_value.group(1)]
                    self.WriteStatus('USBRecordMute', value, qualifier)
                except (KeyError, AttributeError):
                    self.Error(['USB Record Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBRecordMute')

    def SetUSBRecordVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'usb3_record_left', 
            'Right' : 'usb3_record_right'
        }

        ValueConstraints = {
            'Min' : -42,
            'Max' : 6
            }

        channel_val = qualifier['Channel']
        if channel_val in ChannelStates and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            USBRecordVolumeCmdString = 'audio {0} volume set {1:.1f}\r'.format(ChannelStates[channel_val], value)
            self.__SetHelper('USBRecordVolume', USBRecordVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUSBRecordVolume')

    def UpdateUSBRecordVolume(self, value, qualifier):

        ChannelStates = {
            'Left'  : 'usb3_record_left', 
            'Right' : 'usb3_record_right'
        }
        channel_val = qualifier['Channel']
        if channel_val in ChannelStates:
            USBRecordVolumeCmdString = 'audio {0} volume get\r'.format(ChannelStates[channel_val])
            res = self.__UpdateHelper('USBRecordVolume', USBRecordVolumeCmdString, value, qualifier)
            if res:
                try:
                    value = float(re.search(self.VolumePattern, res).group(1))

                    if -42 <= value <= 6:
                        self.WriteStatus('USBRecordVolume', value, qualifier)
                except (ValueError, AttributeError):
                    self.Error(['USB Record Volume: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateUSBRecordVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        elif self.authenticated:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
            res = res.decode()
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.authenticated:
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='>')
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

        self.authenticated = 'Serial' in self.ConnectionType

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

