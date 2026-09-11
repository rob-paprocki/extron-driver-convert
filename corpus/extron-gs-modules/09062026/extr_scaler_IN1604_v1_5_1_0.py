from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import search, compile

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}


        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters':['Input'], 'Status': {}},
            'AudioFormat': {'Parameters':['Input'], 'Status': {}},
            'AudioMute': {'Parameters':['Output'], 'Status': {}},
            'AutoImage': { 'Status': {}},
            'AutoSwitchMode': { 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'GlobalAudioMute': { 'Status': {}},
            'HDCPInputAuthorization': {'Parameters':['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters':['Input'], 'Status': {}},
            'HDCPOutputStatus': { 'Status': {}},
            'HorizontalSize': { 'Status': {}},
            'Input': { 'Status': {}},
            'InputGain': { 'Status': {}},
            'InputSignalType': { 'Status': {}},
            'InputPresetRecall': { 'Status': {}},
            'InputPresetSave': { 'Status': {}},
            'OutputFormat': { 'Status': {}},
            'OutputVolume': { 'Status': {}},
            'PowerSaveMode': { 'Status': {}},
            'ScreenSaverTimeout': { 'Status': {}},
            'ScreenSaverMode': { 'Status': {}},
            'ScreenSaverStatus': { 'Status': {}},
            'InputSignalStatus': {'Parameters':['Input'], 'Status': {}},
            'OutputResolution': { 'Status': {}},
            'Temperature': { 'Status': {}},
            'TestPattern': { 'Status': {}},
            'UserPresetRecall': { 'Status': {}},
            'UserPresetSave': { 'Status': {}},
            'VerticalSize': { 'Status': {}},
            'VideoMute': { 'Status': {}},
            }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'In([1-4]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'AfmtI([1-4])\*([0-8])\r\n'), self.__MatchAudioFormat, None)
            self.AddMatchString(compile(b'Aspr(\d+)\*(\d+)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'Amt([01])\r\n|Amt([01]) ([01])\r\n|Amt([12])\*([01])\r\n'), self.__MatchGlobalAudioMute, None)
            self.AddMatchString(compile(b'HdcpE([2-4])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'Hdcp(I[2-4])\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO1\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Hsiz(\d+)\r\n'), self.__MatchHorizontalSize, None)
            self.AddMatchString(compile(b'Aud([+-])(\d+)\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'Typ1\*([0-4])\r\n'), self.__MatchInputSignalType, None)
            self.AddMatchString(compile(b'Vtpo([0-7])\r\n'), self.__MatchOutputFormat, None)
            self.AddMatchString(compile(b'Vol(-? ?[0-9]{3})\r\n'), self.__MatchOutputVolume, None)
            self.AddMatchString(compile(b'Psav([01])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(compile(b'Rate(\d{2,3})\r\n'), self.__MatchOutputResolution, None)
            self.AddMatchString(compile(b'In00 ([01]{4})\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'SsavM([12])\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(compile(b'SsavS([0-2])\r\n'), self.__MatchScreenSaverStatus, None)
            self.AddMatchString(compile(b'SsavT(\d+)\r\n'), self.__MatchScreenSaverTimeout, None)
            self.AddMatchString(compile(b'(\d+)Stat (\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'Test0([0-7])\r\n'), self.__MatchTestPattern, None)
            self.AddMatchString(compile(b'Vsiz(\d+)\r\n'), self.__MatchVerticalSize, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'E(\d{2})\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioFormat(self, value, qualifier):

        AudioFormatStateValues = {
                    'Analog 1' : '1', 
                    'Analog 2' : '2', 
                    'LPCM-2Ch' : '3', 
                    'Multi-Ch' : '4', 
                    'LPCM-2Ch Auto (analog 1)' : '5', 
                    'Multi-Ch Auto (analog 1)' : '6', 
                    'LPCM-2Ch Auto (analog 2)' : '7', 
                    'Multi-Ch Auto (analog 2)' : '8', 
                    'None' : '0'
                    }

        input_ = qualifier['Input']
        if 1 <= int(input_) <= 4:
            valueStates = AudioFormatStateValues[value]
            if input_ == '1':
                if valueStates in ['2', '1', '0']:
                    commandString = 'wI{0}*{1}AFMT\r'.format(input_, valueStates)
                    self.__SetHelper('AudioFormat', commandString, value, qualifier)
                else :
                    self.Discard('Invalid Command for SetAudioFormat')
            else :
                commandString = 'wI{0}*{1}AFMT\r'.format(input_, valueStates)
                self.__SetHelper('AudioFormat', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for SetAudioFormat')

    def UpdateAudioFormat(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= 4:
            commandString = 'wI{0}AFMT\r'.format(input_)
            self.__UpdateHelper('AudioFormat', commandString, value, qualifier)
        else :
            self.Discard('Invalid Command for UpdateAudioFormat')

    def __MatchAudioFormat(self, match, qualifier):

        AudioFormatStateNames = {
                    '1' : 'Analog 1', 
                    '2' : 'Analog 2', 
                    '3' : 'LPCM-2Ch', 
                    '4' : 'Multi-Ch', 
                    '5' : 'LPCM-2Ch Auto (analog 1)', 
                    '6' : 'Multi-Ch Auto (analog 1)', 
                    '7' : 'LPCM-2Ch Auto (analog 2)', 
                    '8' : 'Multi-Ch Auto (analog 2)', 
                    '0' : 'None'
                    }

        input_ = match.group(1).decode().replace('0', '')
        value = AudioFormatStateNames[match.group(2).decode()]
        self.WriteStatus('AudioFormat', value, {'Input' : input_})

    def SetAspectRatio(self, value, qualifier):

        Input = int(qualifier['Input'])
        if Input < 1 or Input > 4:
            self.Discard('Invalid Command for SetAspectRatio')
        else:
            AspectStateValues = {
                'Fill' : '1',
                'Follow' : '2',
                }
            AspectCmdString = 'w{0}*{1}ASPR\r'.format(Input, AspectStateValues[value])
            self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        Input = int(qualifier['Input'])
        if Input < 1 or Input > 4:
            self.Discard('Invalid Command for UpdateAspectRatio')
        else:
            AspectCmdString= 'w{0}ASPR\r'.format(Input)
            self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, qualifier):

        AspectStateNames = {
             1 : 'Fill' ,
             2 : 'Follow',
             }
        Input = match.group(1).decode()
        State = int(match.group(2).decode())
        value = AspectStateNames[State]
        self.WriteStatus('AspectRatio', value, {'Input' :  Input})

    def SetGlobalAudioMute(self, value, qualifier):

        GlobalAudioMuteStateValues = {
            'On' : '1Z',
            'Off' : '0Z',
            }

        GlobalAudioCmdString = GlobalAudioMuteStateValues[value]
        self.__SetHelper('GlobalAudioMute', GlobalAudioCmdString, value, qualifier)

    def UpdateGlobalAudioMute(self, value, qualifier):

        GlobalAudioCmdString = 'Z'
        self.__UpdateHelper('GlobalAudioMute', GlobalAudioCmdString, value, qualifier)

    def __MatchGlobalAudioMute(self, match, tag):

        OutputValue = {
             1 : '5-Pole Captive',
             2 : 'HDMI'
            }

        MuteState = {
             1 : 'On',
             0 : 'Off'
            }

        if match.group(4):
            Output = OutputValue[int(match.group(4).decode())]
            State1 = MuteState[int(match.group(5).decode())]
            self.WriteStatus('AudioMute', State1, {'Output' : Output})
            if Output == '5-Pole Captive':
                Output = 'HDMI'
            else:
                Output = '5-Pole Captive'
            State2 = self.ReadStatus('AudioMute', {'Output' : Output})
            if State1 == State2:
                self.WriteStatus('GlobalAudioMute', State1, None)
        elif match.group(2):
            State1 = MuteState[int(match.group(2).decode())]
            State2 = MuteState[int(match.group(3).decode())]
            if State1 == State2:
                self.WriteStatus('GlobalAudioMute', State1, None )
            self.WriteStatus('AudioMute', State1, {'Output' : '5-Pole Captive'})
            self.WriteStatus('AudioMute', State2, {'Output' : 'HDMI'})
        else:
            State = MuteState[int(match.group(1).decode())]
            self.WriteStatus('GlobalAudioMute', State, None)
            self.WriteStatus('AudioMute', State, {'Output' : '5-Pole Captive'})
            self.WriteStatus('AudioMute', State, {'Output' : 'HDMI'})

    def SetAutoImage(self, value, qualifier):

        AutoImageStateValues = {
             'Execute' : 'A',
             'Execute And Fill' : '1*A',
             'Execute And Follow' : '2*A',
            }

        AutoImageCmdString = AutoImageStateValues[value]
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeStateValues = {
             'Highest Active Input' : 'w1AUSW\r',
             'Lowest Active Input'  : 'w2AUSW\r',
             'Off'                  : 'w0AUSW\r',
            }

        AutoSwitchModeCmdString = AutoSwitchModeStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, qualifier):

        AutoSwitchModeStateNames = {
                    '0' : 'Off',
                    '1' : 'Highest Active Input',
                    '2' : 'Lowest Active Input',
                    }
        AutoSwitchModeCmdString = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', AutoSwitchModeCmdString, qualifier)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            '5-Pole Captive' : '1',
            'HDMI'           : '2'
        }

        ValueStateValues = {
            'On'  : '1',
            'Off' : '0'
        }

        Output = OutputStates[qualifier['Output']]
        AudioMuteCmdString = '{0}*{1}Z'.format(Output, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        if qualifier['Output'] in ('5-Pole Captive', 'HDMI'):
            self.UpdateGlobalAudioMute(value, None)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'Mode 1' : '1X',
            'Mode 2' : '2X',
            'Off' : '0X',
             }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier )

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeStateValues = {
              '1' : 'Mode 1',
              '2' : 'Mode 2',
              '0' : 'Off',
               }

        Mode = match.group(1).decode()
        value = ExecutiveModeStateValues[Mode]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
             'On' : '1F',
             'Off' : '0F',
            }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):

        FreezeStateNames = {
            '0' : 'Off' ,
            '1' : 'On'  ,
            }

        Mode = match.group(1).decode()
        value = FreezeStateNames[Mode]
        self.WriteStatus('Freeze', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On'  : '1', 
            'Off' : '0'
        }

        if 2 <= int(qualifier['Input']) <= 4:
            HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r\n'.format(qualifier['Input'], ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        if 2 <= int(qualifier['Input']) <= 4:
            HDCPInputAuthorizationCmdString = 'wE{0}HDCP\r\n'.format(qualifier['Input'])
            self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputAuthorization')

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        Input = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': Input})

    def UpdateHDCPInputStatus(self, value, qualifier):

        Input = qualifier['Input']
        InputStates = {
            '2' : 'I2',
            '3' : 'I3',
            '4' : 'I4'
        }
        HDCPInputStatusCmdString = 'w{0}HDCP\r'.format(InputStates[Input])
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        HDCPStateValues = {
            '0' : 'No Source Device Detected',
            '1' : 'Source Detected with HDCP',
            '2' : 'Source Detected without HDCP'
        }

        InputNames = {
            'I2' : '2',
            'I3' : '3',
            'I4' : '4'
        }
        Input = InputNames[match.group(1).decode()]
        value = HDCPStateValues[match.group(2).decode()]
        qualifier = {'Input' : Input}
        self.WriteStatus('HDCPInputStatus', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wO1HDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        HDCPOutputStatusTypeNames = {
            '0' : 'No Sink Device Detected',
            '1' : 'Sink Detected with HDCP',
            '2' : 'Sink Detected without HDCP'
        }

        value = HDCPOutputStatusTypeNames[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHorizontalSize(self, value, qualifier):

        HorizontalSizeConstraints = {
            'Min' : 10,
            'Max' : 4096,
            }

        if HorizontalSizeConstraints['Min'] <= value <= HorizontalSizeConstraints['Max']:
            HorizontalSizeCmdString = 'w{0}HSIZ\r'.format(value)
            self.__SetHelper('HorizontalSize',HorizontalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSize')

    def UpdateHorizontalSize(self, value, qualifier):

        HorizontalSizeCmdString = 'wHSIZ\r'
        self.__UpdateHelper('HorizontalSize', HorizontalSizeCmdString, value, qualifier)

    def __MatchHorizontalSize(self, match, qualifier):

        Size = int(match.group(1).decode())
        self.WriteStatus('HorizontalSize', Size, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            '1' : '1!',
            '2' : '2!',
            '3' : '3!',
            '4' : '4!'
            }

        InputCmdString =InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString ='!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, qualifier )

    def SetInputGain(self, value, qualifier):

        VolumeConstraints = {
            'Min' : -18,
            'Max' : 24,
            }

        if VolumeConstraints['Min'] <= int(value) <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}G'.format(value)
            self.__SetHelper('InputGain',VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        VolumeCmdString = 'G'
        self.__UpdateHelper('InputGain', VolumeCmdString, value, qualifier)

    def __MatchInputGain(self, match, qualifier):

        VolumeConstraints = {
            'Min' : -18,
            'Max' : 24,
            }

        Volume = int(match.group(1).decode() + match.group(2).decode())
        if VolumeConstraints['Min'] <= Volume <= VolumeConstraints['Max']:
            self.WriteStatus('InputGain', Volume, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetInputPresetSave(self, value, qualifier):

        InputPresetSave = {
            'Min' : 1,
            'Max' : 16,
            }

        if InputPresetSave['Min'] <= int(value) <= InputPresetSave['Max']:
            InputPresetSaveCmdString = '2*{0},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetSave')

    def SetInputPresetRecall(self, value, qualifier):

        InputPresetRecall = {
            'Min' : 1,
            'Max' : 16,
            }

        if InputPresetRecall['Min'] <= int(value) <= InputPresetRecall['Max']:
            InputPresetRecallCmdString = '2*{0}.'.format(value)
            self.__SetHelper('InputPresetRecall',InputPresetRecallCmdString,value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def UpdateInputSignalStatus(self, value, qualifier):

        SignalCmdString= 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', SignalCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, qualifier):

        SignalStateNames = {
            '0' : 'Not Active',
            '1' : 'Active',
           }
        
        for input_number, signal in enumerate(match.group(1).decode()):
            self.WriteStatus('InputSignalStatus', SignalStateNames[signal], {'Input' : str(input_number + 1)})

    def SetInputSignalType(self, value, qualifier):

        ValueStateValues = {
            'RGB' : '1',
            'YUV' : '2',
            'S-Video' : '3',
            'Composite' : '4',
        }

        InputSignalTypeCmdString = '1*' + ValueStateValues[value] + '\x5C'
        self.__SetHelper('InputSignalType', InputSignalTypeCmdString.encode(), value, qualifier)

    def UpdateInputSignalType(self, value, qualifier):

        InputSignalTypeCmdString = b'1\x5C'
        self.__UpdateHelper('InputSignalType', InputSignalTypeCmdString, value, qualifier)

    def __MatchInputSignalType(self, match, tag):

        ValueStateValues = {
            '1' : 'RGB',
            '2' : 'YUV',
            '3' : 'S-Video',
            '4' : 'Composite',
            '0' : 'No Signal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('InputSignalType', value, None)

    def SetOutputFormat(self, value, qualifier):

        OutputFormat = {
            'Auto'                  : '0',
            'DVI RGB 444'           : '1',
            'HDMI RGB Full'         : '2',
            'HDMI RGB Limited'      : '3',
            'HDMI YUV 444 Full'     : '4',
            'HDMI YUV 444 Limited'  : '5',
            'HDMI YUV 422 Full'     : '6',
            'HDMI YUV 422 Limited'  : '7'
            }

        OutputCmdString = 'w{0}VTPO\r'.format(OutputFormat[value])
        self.__SetHelper('OutputFormat',OutputCmdString,value, qualifier)

    def UpdateOutputFormat(self, value, qualifier):

        OutputCmdString = 'wVTPO\r'
        self.__UpdateHelper('OutputFormat', OutputCmdString, value, qualifier)

    def __MatchOutputFormat(self, match, qualifier):

        Output = {
            '0' : 'Auto',
            '1' : 'DVI RGB 444',
            '2' : 'HDMI RGB Full',
            '3' : 'HDMI RGB Limited',
            '4' : 'HDMI YUV 444 Full',
            '5' : 'HDMI YUV 444 Limited',
            '6' : 'HDMI YUV 422 Full',
            '7' : 'HDMI YUV 422 Limited'
            }

        self.WriteStatus('OutputFormat', Output[match.group(1).decode()], qualifier)

    def SetOutputResolution(self, value, qualifier):

        OutputResolutionConstraints = {
            '640x480 60Hz' : '10',
            '800x600 60Hz' : '11',
            '1024x768 60Hz' : '12',
            '1280x768 60Hz' : '13',
            '1280x800 60Hz' : '14',
            '1280x1024 60Hz' : '15',
            '1360x768 60Hz' : '16',
            '1366x768 60Hz' : '17',
            '1440x900 60Hz' : '18',
            '1400x1050 60Hz' : '19',
            '1600x900 60Hz' : '20',
            '1680x1050 60Hz' : '21',
            '1600x1200 60Hz' : '22',
            '1920x1200 60Hz' : '23',
            '480p 59.94Hz' : '24',
            '480p 60Hz' : '25',
            '576p 50Hz' : '26',
            '720p 25Hz' : '29',
            '720p 29.97Hz' : '30',
            '720p 30Hz' : '31',
            '720p 50Hz' : '32',
            '720p 59.94Hz' : '33',
            '720p 60Hz' : '34',
            '1080i 50Hz' : '35',
            '1080i 59.94Hz' : '36',
            '1080i 60Hz' : '37',
            '1080p 23.98Hz' : '38',
            '1080p 24Hz' : '39',
            '1080p 25Hz' : '40',
            '1080p 29.97Hz' : '41',
            '1080p 30Hz' : '42',
            '1080p 50Hz' : '43',
            '1080p 59.94Hz' : '44',
            '1080p 60Hz' : '45',
            '2048x1080 2k 23.98Hz' : '46',
            '2048x1080 2k 24Hz' : '47',
            '2048x1080 2k 25Hz' : '48',
            '2048x1080 2k 29.97Hz' : '49',
            '2048x1080 2k 30Hz' : '50',
            '2048x1080 2k 50Hz' : '51',
            '2048x1080 2k 59.94Hz' : '52',
            '2048x1080 2k 60Hz' : '53',
            'Custom 1' : '201',
            'Custom 2' : '202',
            'Custom 3' : '203',
            'Custom 4' : '204',
            'Custom 5' : '205',
        }

        OutputResolutionCmdString = 'w{0}RATE\r'.format(OutputResolutionConstraints[value])
        self.__SetHelper('OutputResolution',OutputResolutionCmdString,value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputResolutionCmdString = 'wRATE\r'
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, qualifier):

        OutputResolutionConstraints = {
            '10' : '640x480 60Hz',
            '11' : '800x600 60Hz',
            '12' : '1024x768 60Hz',
            '13' : '1280x768 60Hz',
            '14' : '1280x800 60Hz',
            '15' : '1280x1024 60Hz',
            '16' : '1360x768 60Hz',
            '17' : '1366x768 60Hz',
            '18' : '1440x900 60Hz',
            '19' : '1400x1050 60Hz',
            '20' : '1600x900 60Hz',
            '21' : '1680x1050 60Hz',
            '22' : '1600x1200 60Hz',
            '23' : '1920x1200 60Hz',
            '24' : '480p 59.94Hz',
            '25' : '480p 60Hz',
            '26' : '576p 50Hz',
            '29' : '720p 25Hz',
            '30' : '720p 29.97Hz',
            '31' : '720p 30Hz',
            '32' : '720p 50Hz',
            '33' : '720p 59.94Hz',
            '34' : '720p 60Hz',
            '35' : '1080i 50Hz',
            '36' : '1080i 59.94Hz',
            '37' : '1080i 60Hz',
            '38' : '1080p 23.98Hz',
            '39' : '1080p 24Hz',
            '40' : '1080p 25Hz',
            '41' : '1080p 29.97Hz',
            '42' : '1080p 30Hz',
            '43' : '1080p 50Hz',
            '44' : '1080p 59.94Hz',
            '45' : '1080p 60Hz',
            '46' : '2048x1080 2k 23.98Hz',
            '47' : '2048x1080 2k 24Hz',
            '48' : '2048x1080 2k 25Hz',
            '49' : '2048x1080 2k 29.97Hz',
            '50' : '2048x1080 2k 30Hz',
            '51' : '2048x1080 2k 50Hz',
            '52' : '2048x1080 2k 59.94Hz',
            '53' : '2048x1080 2k 60Hz',
            '201': 'Custom 1',
            '202': 'Custom 2',
            '203': 'Custom 3',
            '204': 'Custom 4',
            '205': 'Custom 5',
        }

        value = OutputResolutionConstraints[match.group(1).decode()]
        self.WriteStatus('OutputResolution', value, None)

    def SetOutputVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : -100,
            'Max' : 0
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputVolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = 'V'
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputVolume', value, None)

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeStateValues = {
            'Off' : 'w0PSAV\r',
            'On' :  'w1PSAV\r',
            }
        PowerSaveModeCmdString = PowerSaveModeStateValues[value]
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value,qualifier)

    def __MatchPowerSaveMode(self, match, qualifier):

        PowerSaveModeStateNames = {
            0 : 'Off' ,
            1 : 'On'  ,
            }

        Mode = PowerSaveModeStateNames[int(match.group(1).decode())]
        self.WriteStatus('PowerSaveMode', Mode, qualifier)

    def SetScreenSaverMode(self, value, qualifier):

        ScreenModeStateValues = {
            'Black Screen' : 1,
            'Blue Screen' : 2,
            }

        ModeCmdString = 'wM'+str(ScreenModeStateValues[value])+'SSAV\r'
        self.__SetHelper('ScreenSaverMode', ModeCmdString, value, qualifier)

    def UpdateScreenSaverMode(self, value, qualifier):


        ModeCmdString = 'wMSSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, qualifier):

        ScreenModeStateValues = {
            '1' : 'Black Screen',
            '2' : 'Blue Screen',
            }

        Mode = match.group(1).decode()
        self.WriteStatus('ScreenSaverMode', ScreenModeStateValues[Mode], qualifier)

    def UpdateScreenSaverStatus(self, value, qualifier):

        commandString = 'wSSSAV\r'
        self.__UpdateHelper('ScreenSaverStatus', commandString, value, qualifier)

    def __MatchScreenSaverStatus(self, match, qualifier):

        ScreenSaverStatusStateNames = {
            '0' : 'Active Input Detected; Timer not running',
            '2' : 'No Active Input; Timer expired; Output sync disabled',
            '1' : 'No Active Input; Timer running; Output sync enabled'
            }

        value = ScreenSaverStatusStateNames[match.group(1).decode()]
        self.WriteStatus('ScreenSaverStatus', value, qualifier)

    def SetScreenSaverTimeout(self, value, qualifier):


        TimerStateValues = {
            'Disabled' : 0,
            'NoTimeOut' : 501,
            }

        if value < TimerStateValues['Disabled'] or value > TimerStateValues['NoTimeOut']:
            self.Discard('Invalid Command for SetScreenSaverTimeout')
        elif value == TimerStateValues['Disabled']:
            TimerCmdString = 'wT'+str(TimerStateValues['Disabled'])+'SSAV\r'
            self.__SetHelper('ScreenSaverTimeout', TimerCmdString, str(value), qualifier)
        elif value == TimerStateValues['NoTimeOut']:
            TimerCmdString = 'wT'+str(TimerStateValues['NoTimeOut'])+'SSAV\r'
            self.__SetHelper('ScreenSaverTimeout', TimerCmdString, str(value), qualifier)
        else:
            TimerCmdString = 'wT'+str(value)+'SSAV\r'
            self.__SetHelper('ScreenSaverTimeout', TimerCmdString, str(value), qualifier)

    def UpdateScreenSaverTimeout(self, value, qualifier):

        TimerCmdString = 'wTSSAV\r'
        self.__UpdateHelper('ScreenSaverTimeout', TimerCmdString, value, qualifier)

    def __MatchScreenSaverTimeout(self, match, qualifier):

        Time = int(match.group(1).decode())
        self.WriteStatus('ScreenSaverTimeout', Time, qualifier)

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, qualifier):

        value = int(match.group(2).decode())
        self.WriteStatus('Temperature', value, qualifier )

    def SetTestPattern(self, value, qualifier):

        TestPatternStateValues = {
                    'None' : '0',
                    'Crop' : '1',
                    'Alternating Pixels' : '2',
                    'Crosshatch' : '3',
                    'Color Bars' : '4',
                    'Grayscale' : '5',
                    'Blue Mode' : '6',
                    'Audio Test Pattern' : '7'
                    }

        commandString = 'w{0}TEST\r'.format(TestPatternStateValues[value])
        self.__SetHelper('TestPattern', commandString, value, qualifier)

    def UpdateTestPattern(self, value, qualifier):

        commandString = 'wTEST\r'
        self.__UpdateHelper('TestPattern', commandString, value, qualifier)

    def __MatchTestPattern(self, match, qualifier):

        TestPatternStateNames = {
                    '0' : 'None',
                    '1' : 'Crop',
                    '2' : 'Alternating Pixels',
                    '3' : 'Crosshatch',
                    '4' : 'Color Bars',
                    '5' : 'Grayscale',
                    '6' : 'Blue Mode',
                    '7' : 'Audio Test Pattern',
                    }

        value = TestPatternStateNames[match.group(1).decode()]
        self.WriteStatus('TestPattern', value, qualifier)

    def SetUserPresetSave(self, value, qualifier):

        UserPresetSave = {
            'Min' : 1,
            'Max' : 16,
            }

        if int(value) < UserPresetSave['Min'] or int(value) > UserPresetSave['Max']:
            self.Discard('Invalid Command for SetUserPresetSave')
        else:
            UserPresetSaveCmdString = '1*{0},'.format(value)
            self.__SetHelper('UserPresetSave', UserPresetSaveCmdString, value, qualifier)

    def SetUserPresetRecall(self, value, qualifier):

        UserPresetRecall = {
            'Min' : 1,
            'Max' : 16,
            }

        if UserPresetRecall['Min'] <= int(value) <= UserPresetRecall['Max']:
            UserPresetRecallCmdString = '1*{0}.'.format(value)
            self.__SetHelper('UserPresetRecall', UserPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUserPresetRecall')

    def SetVerticalSize(self, value, qualifier):

        VerticalSizeConstraints = {
            'Min' : 10,
            'Max' : 2400,
            }

        if VerticalSizeConstraints['Min'] <= value <= VerticalSizeConstraints['Max']:
            VerticalSizeCmdString = 'w{0}VSIZ\r'.format(value)
            self.__SetHelper('VerticalSize',VerticalSizeCmdString,value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSize')

    def UpdateVerticalSize(self, value, qualifier):

        VerticalSizeCmdString = 'wVSIZ\r'
        self.__UpdateHelper('VerticalSize', VerticalSizeCmdString, value, qualifier)

    def __MatchVerticalSize(self, match, qualifier):

        Size = int(match.group(1).decode())
        self.WriteStatus('VerticalSize', Size, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On'            : '1B',
            'On with Sync'  : '2B',
            'Off'           : '0B'
            }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteStateNames = {
            '0' : 'Off' ,
            '1' : 'On' ,
            '2' : 'On with Sync' ,
            }

        value = match.group(1).decode()
        self.WriteStatus('VideoMute', VideoMuteStateNames[value], qualifier)

    def __MatchError(self, match, qualifier):
        self.counter = 0

        DeviceErrorCodes = {
            '01' : 'Invalid input number',
            '06' : 'Invalid switch attempt in this mode',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid port number',
            '13' : 'Invalid parameter',
            '14' : 'Not valid for this configuration',
            '17' : 'Invalid command for signal type',
            '22' : 'Busy'
        }

        self.Error([DeviceErrorCodes.get(match.group(1).decode(), 'Unrecognized error code: {0}'.format(match.group(0).decode()))])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True        
        if self.VerboseDisabled:
            self.Send('w3cv\r\n')
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
            print(command, 'does not exist in the module')

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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data
        
        #check incoming data if it matched any expected data from device module
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
