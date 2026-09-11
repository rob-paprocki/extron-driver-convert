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
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMatrixTieCommand': {'Parameters':['Input','Output'], 'Status': {}},
            'AudioMute': {'Parameters':['Channel'], 'Status': {}},
            'CameraHome': {'Parameters':['Camera'], 'Status': {}},
            'CameraPan': {'Parameters':['Camera','Speed'], 'Status': {}},
            'CameraPresetRecall': {'Parameters':['Camera'], 'Status': {}},
            'CameraPresetSave': {'Parameters':['Camera', 'Current Color Setting'], 'Status': {}},
            'CameraStandby': {'Parameters':['Camera'], 'Status': {}},
            'CameraTilt': {'Parameters':['Camera','Speed'], 'Status': {}},
            'CameraZoom': {'Parameters':['Camera','Speed'], 'Status': {}},
            'Input': { 'Status': {}},
            'PIPLayout': { 'Status': {}},
            'PIPMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'StreamingSettingStatus': {'Parameters':['Type'], 'Status': {}},
            'Trigger': {'Parameters':['Index'], 'Status': {}},
            'VideoMute': { 'Status': {}},
            'VolumeDiscrete': {'Parameters':['Channel'], 'Status': {}},
            'VolumeStep': {'Parameters':['Channel'], 'Status': {}},
        }

        self.Authenticated = True

        self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)
        self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
        self.AddMatchString(re.compile(b'Welcome'), self.__MatchAuthenticated, None)

        self.set_regex = re.compile(b'login:|Password:|>')
        self.update_regex = {
            'AudioMute':              re.compile(b'mute:\s*(on|off)|login:|Password:'),
            'CameraStandby':          re.compile(b'standby:\s*(on|off)|login:|Password:'),
            'Input':                  re.compile(b'source:\s*input([1-5])|login:|Password:'),
            'Power':                  re.compile(b'standby:\s*(on|off)|login:|Password:'),
            'StreamingSettingStatus': re.compile(b'[\s\S]+?>|login:|Password:'),
            'VideoMute':              re.compile(b'mute:\s*(on|off)|login:|Password:'),
            'VolumeDiscrete':         re.compile(b'volume:\s*(-?[0-9]{1,2})\.0 dB|login:|Password:'),
        }

        self.parse_regex = {
            'AudioMute':        re.compile('mute:\s*(on|off)'),
            'CameraStandby':    re.compile('standby:\s*(on|off)'),
            'Input':            re.compile('source:\s*input([1-5])'),
            'Power':            re.compile('standby:\s*(on|off)'),
            'VideoMute':        re.compile('mute:\s*(on|off)'),
            'VolumeDiscrete':   re.compile('volume:\s*(-?[0-9]{1,2})\.0 dB'),
        }
        self.StreamingPattern  = re.compile('USB Active ([\s\S]+?)\r\nUSB Device ([\s\S]+?)\r\nUSB Frame_Rate ([\s\S]+?)\r\n'
                                       'USB Resolution ([\s\S]+?)\r\nUSB Version ([\s\S]+?)\r\n')
        
    def __MatchLogin(self, value, qualifier):

        self.Authenticated = False
        self.Send('admin\r\n')

    def __MatchPassword(self, value, qualifier):

        self.Authenticated = False
        self.Send(self.devicePassword + '\r\n')

    def __MatchAuthenticated(self, value, qualifier):

        self.Authenticated = True
    
    def SetAudioMatrixTieCommand(self, value, qualifier):

        InputStates = {
            'Line 1':             'line_in_1',
            'Line 2':             'line_in_2',
            'USB Playback Left':  'usb3_playback_left',
            'USB Playback Right': 'usb3_playback_right',
            'HDMI Left':          'hdmi_in_left',
            'HDMI Right':         'hdmi_in_right',
        }
        input_ = qualifier['Input']

        OutputStates = {
            'Line 1':           'line_out_1',
            'Line 2':           'line_out_2',
            'USB Record Left':  'usb3_record_left',
            'USB Record Right': 'usb3_record_right',
            'HDMI Left':        'hdmi_out_left',
            'HDMI Right':       'hdmi_out_right',
        }
        output = qualifier['Output']

        if input_ in InputStates and output in OutputStates:
            AudioMatrixTieCommandCmdString = 'audio {} route set {}\r\n'.format(OutputStates[output], InputStates[input_])
            self.__SetHelper('AudioMatrixTieCommand', AudioMatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMatrixTieCommand')

    def SetAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master'             : 'master', 
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_left', 
            'HDMI In Right'      : 'hdmi_in_right', 
            'Dante In 1'         : 'dante_in_1', 
            'Dante In 2'         : 'dante_in_2', 
            'Dante In 3'         : 'dante_in_3', 
            'Dante In 4'         : 'dante_in_4',
            'Line Out 1'         : 'line_out_1',
            'Line Out 2'         : 'line_out_2',
            'USB Record Left'    : 'usb3_record_left',
            'USB Record Right'   : 'usb3_record_right',
            'HDMI Out Left'      : 'hdmi_out_left',
            'HDMI Out Right'     : 'hdmi_out_right',
            'Dante Out 1'        : 'dante_out_1',
            'Dante Out 2'        : 'dante_out_2',
            'Dante Out 3'        : 'dante_out_3',
            'Dante Out 4'        : 'dante_out_4'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }

        if channel in ChannelStates and value in ValueStateValues:
            AudioMuteCmdString = 'audio {} mute {}\r\n'.format(ChannelStates[channel], ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ChannelStates = {
            'Master'             : 'master', 
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_left', 
            'HDMI In Right'      : 'hdmi_in_right', 
            'Dante In 1'         : 'dante_in_1', 
            'Dante In 2'         : 'dante_in_2', 
            'Dante In 3'         : 'dante_in_3', 
            'Dante In 4'         : 'dante_in_4',
            'Line Out 1'         : 'line_out_1',
            'Line Out 2'         : 'line_out_2',
            'USB Record Left'    : 'usb3_record_left',
            'USB Record Right'   : 'usb3_record_right',
            'HDMI Out Left'      : 'hdmi_out_left',
            'HDMI Out Right'     : 'hdmi_out_right',
            'Dante Out 1'        : 'dante_out_1',
            'Dante Out 2'        : 'dante_out_2',
            'Dante Out 3'        : 'dante_out_3',
            'Dante Out 4'        : 'dante_out_4'
        }
        channel = qualifier['Channel']

        ValueStateValues = {
            'on':   'On',
            'off':  'Off'
        }

        if channel in ChannelStates:
            AudioMuteCmdString = 'audio {} mute get\r\n'.format(ChannelStates[channel])
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[self.parse_regex['AudioMute'].search(res).group(1)]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (AttributeError, KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetCameraHome(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        camera_val = qualifier['Camera']
        if camera_val in CameraStates:
            CameraHomeCmdString = 'camera {} home\r\n'.format(CameraStates[camera_val])
            self.__SetHelper('CameraHome', CameraHomeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraHome')
    def SetCameraPan(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        panSpd = int(qualifier['Speed'])

        ValueStateValues = {
            'Left':  'left {}'.format(panSpd),
            'Right': 'right {}'.format(panSpd),
            'Stop':  'stop'
        }

        camera_val = qualifier['Camera']
        if camera_val in CameraStates and 1 <= panSpd <= 24 and value in ValueStateValues:
            CameraPanCmdString = 'camera {} pan {}\r\n'.format(CameraStates[camera_val], ValueStateValues[value])
            self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPresetRecall(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        camera_val = qualifier['Camera']
        if camera_val in CameraStates and 1 <= int(value) <= 16:
            CameraPresetRecallCmdString = 'camera {} preset recall {}\r\n'.format(CameraStates[camera_val], value)
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        CurrentColorSettingStates = {
            'True' : ' save-ccu',
            'False' : ''
        }

        camera_val = qualifier['Camera']
        if camera_val in CameraStates and qualifier['Current Color Setting'] in CurrentColorSettingStates and 1 <= int(value) <= 16:
            CameraPresetSaveCmdString = 'camera {} preset store {}{}\r\n'.format(CameraStates[camera_val], value, CurrentColorSettingStates[qualifier['Current Color Setting']])
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier) 
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraStandby(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        ValueStateValues = {
            'On':  'on', 
            'Off': 'off'
        }

        camera_val = qualifier['Camera']
        if value in ValueStateValues and camera_val in CameraStates:
            CameraStandbyCmdString = 'camera {} standby {}\r\n'.format(CameraStates[camera_val], ValueStateValues[value])
            self.__SetHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraStandby')

    def UpdateCameraStandby(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }
        ValueStateValues = {
            'on':  'On', 
            'off': 'Off'
        }

        camera_val = qualifier['Camera']
        if camera_val in CameraStates:
            CameraStandbyCmdString = 'camera {} standby get\r\n'.format(CameraStates[camera_val])
            res = self.__UpdateHelper('CameraStandby', CameraStandbyCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[self.parse_regex['CameraStandby'].search(res).group(1)]
                    self.WriteStatus('CameraStandby', value, qualifier)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['Camera Standby: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateCameraStandby')

    def SetCameraTilt(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        tiltSpd = int(qualifier['Speed'])

        ValueStateValues = {
            'Up':   'up {}'.format(tiltSpd),
            'Down': 'down {}'.format(tiltSpd),
            'Stop': 'stop'
        }

        camera_val = qualifier['Camera']
        if value in ValueStateValues and 1 <= tiltSpd <= 20 and camera_val in CameraStates:
            CameraTiltCmdString = 'camera {} tilt {}\r\n'.format(CameraStates[camera_val], ValueStateValues[value])
            self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraZoom(self, value, qualifier):

        CameraStates = {
            '1' : '2', 
            '2' : '3', 
            '3' : '4', 
            '4' : '5'
        }

        zoomSpd = int(qualifier['Speed'])

        ValueStateValues = {
            'In':   'in {}'.format(zoomSpd),
            'Out':  'out {}'.format(zoomSpd),
            'Stop': 'stop'
        }

        camera_val = qualifier['Camera']
        if value in ValueStateValues and 1 <= zoomSpd <= 24 and camera_val in CameraStates:
            CameraZoomCmdString = 'camera {} zoom {}\r\n'.format(CameraStates[camera_val], ValueStateValues[value])
            self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI':     '1',
            'Camera 1': '2',
            'Camera 2': '3',
            'Camera 3': '4',
            'Camera 4': '5'
        }

        if value in ValueStateValues:
            InputCmdString = 'video source set input{}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'HDMI',
            '2': 'Camera 1',
            '3': 'Camera 2',
            '4': 'Camera 3',
            '5': 'Camera 4'
        }

        InputCmdString = 'video source get\r\n'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.parse_regex['Input'].search(res).group(1)]
                self.WriteStatus('Input', value, qualifier)
            except (AttributeError, KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetPIPLayout(self, value, qualifier):

        ValueStateValues = {
            'Upper Right': 'upper_right', 
            'Lower Right': 'lower_right', 
            'Lower Left':  'lower_left',  
            'Upper Left':  'upper_left',  
            'Top Bottom':  'top_bottom',  
            'Left Right':  'left_right'
        }

        if value in ValueStateValues:
            PIPLayoutCmdString = 'video pip layout {0}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PIPLayout', PIPLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPLayout')

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On':     'on', 
            'Off':    'off',
            'Toggle': 'toggle'
        }

        if value in ValueStateValues:
            PIPModeCmdString = 'video pip {0}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   'off',
            'Off':  'on'
        }

        if value in ValueStateValues:
            PowerCmdString = 'system standby {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            'off':  'On',
            'on':   'Off'
        }

        PowerCmdString = 'system standby get\r\n'
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.parse_regex['Power'].search(res).group(1)]
                self.WriteStatus('Power', value, qualifier)
            except (AttributeError, KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def UpdateStreamingSettingStatus(self, value, qualifier):

        TypeStates = ('USB Active', 'USB Device', 'USB Frame Rate', 'USB Resolution', 'USB Version')
                        
        type_val = qualifier['Type']
        if type_val in TypeStates:
            StreamingSettingStatusCmdString = 'streaming settings get\r\n'
            res = self.__UpdateHelper('StreamingSettingStatus', StreamingSettingStatusCmdString, value, qualifier)
            if res:
                try:
                    temp_value = re.search(self.StreamingPattern, res)
                    for i in range(0, 5):
                        self.WriteStatus('StreamingSettingStatus', temp_value.group(i + 1).strip().title(), {'Type': TypeStates[i]})
                except (IndexError, AttributeError):
                    self.Error(['Streaming Setting Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateStreamingSettingStatus')

    def SetTrigger(self, value, qualifier):

        index = qualifier['Index']

        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }

        if 1 <= int(index) <= 50 and value in ValueStateValues:
            TriggerCmdString = 'trigger {} {}\r\n'.format(index, ValueStateValues[value])
            self.__SetHelper('Trigger', TriggerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrigger')

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On':   'on',
            'Off':  'off'
        }

        if value in ValueStateValues:
            VideoMuteCmdString = 'video mute {}\r\n'.format(ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            'on':   'On',
            'off':  'Off'
        }

        VideoMuteCmdString = 'video mute get\r\n'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[self.parse_regex['VideoMute'].search(res).group(1)]
                self.WriteStatus('VideoMute', value, qualifier)
            except (AttributeError, KeyError, IndexError):
                self.Error(['Video Mute: Invalid/unexpected response'])

    def SetVolumeDiscrete(self, value, qualifier):

        ChannelStates = {
            'Master'             : 'master', 
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_1_left', 
            'HDMI In Right'      : 'hdmi_in_1_right', 
            'Dante In 1'         : 'dante_in_1', 
            'Dante In 2'         : 'dante_in_2', 
            'Dante In 3'         : 'dante_in_3', 
            'Dante In 4'         : 'dante_in_4',
            'Line Out 1'         : 'line_out_1',
            'Line Out 2'         : 'line_out_2',
            'USB Record Left'    : 'usb3_record_left',
            'USB Record Right'   : 'usb3_record_right',
            'HDMI Out Left'      : 'hdmi_out_left',
            'HDMI Out Right'     : 'hdmi_out_right',
            'Dante Out 1'        : 'dante_out_1',
            'Dante Out 2'        : 'dante_out_2',
            'Dante Out 3'        : 'dante_out_3',
            'Dante Out 4'        : 'dante_out_4'
        }
        channel = qualifier['Channel']

        if qualifier['Channel'] in ChannelStates and -50 <= value <= 20:
            VolumeDiscreteCmdString = 'audio {} volume set {}\r\n'.format(ChannelStates[channel], value)
            self.__SetHelper('VolumeDiscrete', VolumeDiscreteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeDiscrete')

    def UpdateVolumeDiscrete(self, value, qualifier):

        ChannelStates = {
            'Master'             : 'master', 
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_left', 
            'HDMI In Right'      : 'hdmi_in_right', 
            'Dante In 1'         : 'dante_in_1', 
            'Dante In 2'         : 'dante_in_2', 
            'Dante In 3'         : 'dante_in_3', 
            'Dante In 4'         : 'dante_in_4',
            'Line Out 1'         : 'line_out_1',
            'Line Out 2'         : 'line_out_2',
            'USB Record Left'    : 'usb3_record_left',
            'USB Record Right'   : 'usb3_record_right',
            'HDMI Out Left'      : 'hdmi_out_left',
            'HDMI Out Right'     : 'hdmi_out_right',
            'Dante Out 1'        : 'dante_out_1',
            'Dante Out 2'        : 'dante_out_2',
            'Dante Out 3'        : 'dante_out_3',
            'Dante Out 4'        : 'dante_out_4'
        }
        channel = qualifier['Channel']


        if channel in ChannelStates:
            VolumeDiscreteCmdString = 'audio {} volume get\r\n'.format(ChannelStates[channel])
            res = self.__UpdateHelper('VolumeDiscrete', VolumeDiscreteCmdString, value, qualifier)
            if res:
                try:
                    value = int(self.parse_regex['VolumeDiscrete'].search(res).group(1))
                    if -50 <= value <= 20:
                        self.WriteStatus('VolumeDiscrete', value, qualifier)
                except (ValueError, IndexError, AttributeError):
                    self.Error(['Volume Discrete: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVolumeDiscrete')

    def SetVolumeStep(self, value, qualifier):

        ChannelStates = {
            'Master'             : 'master', 
            'Line In 1'          : 'line_in_1', 
            'Line In 2'          : 'line_in_2', 
            'USB Playback Left'  : 'usb3_playback_left', 
            'USB Playback Right' : 'usb3_playback_right', 
            'HDMI In Left'       : 'hdmi_in_1_left', 
            'HDMI In Right'      : 'hdmi_in_1_right', 
            'Dante In 1'         : 'dante_in_1', 
            'Dante In 2'         : 'dante_in_2', 
            'Dante In 3'         : 'dante_in_3', 
            'Dante In 4'         : 'dante_in_4',
            'Line Out 1'         : 'line_out_1',
            'Line Out 2'         : 'line_out_2',
            'USB Record Left'    : 'usb3_record_left',
            'USB Record Right'   : 'usb3_record_right',
            'HDMI Out Left'      : 'hdmi_out_left',
            'HDMI Out Right'     : 'hdmi_out_right',
            'Dante Out 1'        : 'dante_out_1',
            'Dante Out 2'        : 'dante_out_2',
            'Dante Out 3'        : 'dante_out_3',
            'Dante Out 4'        : 'dante_out_4'
        }
        channel = qualifier['Channel']

        ValueStateValues = [
            'Up',
            'Down'
        ]

        if channel in ChannelStates and value in ValueStateValues:
            VolumeStepCmdString = 'audio {} volume {}\r\n'.format(ChannelStates[channel], value.lower())
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'login:' in response:
            self.__MatchLogin(None, None)
            response = ''
        if 'Password:' in response:
            self.__MatchPassword(None, None)
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

                if command in ['StreamingSettingStatus']:
                    timeout = 5
                else:
                    timeout = self.DefaultResponseTimeout
                res = self.SendAndWait(commandstring, timeout, deliRex=self.update_regex[command])
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

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