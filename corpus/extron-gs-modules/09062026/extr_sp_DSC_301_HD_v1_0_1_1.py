from extronlib.interface import SerialInterface, EthernetClientInterface
from re import search, compile
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
        self.VerboseDisabled = True

        self.Debug = False

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Parameters': ['Input'], 'Status': {}},
            'AudioGainAttenuation': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AutoSwitch': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'HDCPInputStatus': {'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'HDMIOutputFormat': {'Status': {}},
            'HorizontalSize': {'Status': {}},
            'Input': {'Status': {}},
            'InputPresetRecall': {'Status': {}},
            'InputPresetSave': {'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'ScreenSaverTimeout': {'Status': {}},
            'ScreenSaverMode': {'Status': {}},
            'SignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'Resolution': {'Status': {}},
            'Temperature': {'Status': {}},
            'UserPresetRecall': {'Status': {}},
            'UserPresetSave': {'Status': {}},
            'VerticalSize': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.InputSize = 3

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Aspr([1-3])\*([12])\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitch, None)
            self.AddMatchString(compile(b'In([1-3]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frz([01])\r\n'), self.__MatchFreeze, None)
            self.AddMatchString(compile(b'Hsiz(\d+)\r\n'), self.__MatchHorizontalSize, None)
            self.AddMatchString(compile(b'HdcpI3\*([0-2])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO1\*([0-2])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Vtpo([0-7])\r\n'), self.__MatchHDMIOutputFormat, None)
            self.AddMatchString(compile(b'Psav([01])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(compile(b'In00 ([01])\*([01])\*([01])\r\n'), self.__MatchSignalStatus, None)
            self.AddMatchString(compile(b'20Stat(\d+)\r\n'), self.__MatchTemperature, None)
            self.AddMatchString(compile(b'SsavT(\d+)\r\n'), self.__MatchScreenSaverTimeout, None)
            self.AddMatchString(compile(b'SsavM([12])\r\n'), self.__MatchScreenSaverMode, None)
            self.AddMatchString(compile(b'Vsiz(\d+)\r\n'), self.__MatchVerticalSize, None)
            self.AddMatchString(compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Aud([+-])(\d+)\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(compile(b'Rate([0-9]{2})\r\n'), self.__MatchResolution, None)
            self.AddMatchString(compile(b'E([0-3][0-9])\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, value, qualifier):
        self.VerboseDisabled = False

    def SetAspectRatio(self, value, qualifier):

        Input = int(qualifier['Input'])
        if Input < 1 or Input > self.InputSize:
            self.Discard('Invalid Command for SetAspectRatio')
        else:
            AspectStateValues = {
                'Fill Mode': '1',
                'Follow Mode': '2',
            }
            AspectCmdString = chr(27) + '{}*{}ASPR\r'.format(Input, AspectStateValues[value])
            self.__SetHelper('AspectRatio', AspectCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        channel = qualifier[self.Commands['AspectRatio']['Parameters'][0]]
        if int(channel) < 1 or int(channel) > self.InputSize:
            self.Discard('Invalid Command for UpdateAspectRatio')
        else:
            AspectCmdString = chr(27) + str(channel) + 'ASPR\r'
            self.__UpdateHelper('AspectRatio', AspectCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, qualifier):

        AspectStateNames = {
            '1': 'Fill Mode',
            '2': 'Follow Mode',
        }
        Input = match.group(1).decode()
        value = AspectStateNames[match.group(2).decode()]
        self.WriteStatus('AspectRatio', value, {'Input': Input})

    def SetAudioGainAttenuation(self, value, qualifier):

        VolumeConstraints = {
            'Min': -18,
            'Max': 12,
        }

        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            self.Discard('Invalid Command for SetAudioGainAttenuation')
        else:
            VolumeCmdString = '{0}G'.format(value)
            self.__SetHelper('AudioGainAttenuation', VolumeCmdString, str(value), qualifier)

    def UpdateAudioGainAttenuation(self, value, qualifier):

        VolumeCmdString = 'G'
        self.__UpdateHelper('AudioGainAttenuation', VolumeCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, qualifier):

        Volume = int(match.group(1).decode() + match.group(2).decode())
        self.WriteStatus('AudioGainAttenuation', Volume, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'Mute': '1Z',
            'Unmute': '0Z',
        }

        AspectCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AspectCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        MuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', MuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, qualifier):

        AudioMuteStateNames = {
            0: 'Unmute',
            1: 'Mute',
        }

        State = int(match.group(1).decode())
        value = AudioMuteStateNames[State]
        self.WriteStatus('AudioMute', value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageStateValues = {
            'Execute': 'A',
            'Execute And Fill': '1*A',
            'Execute And Follow': '2*A',
        }

        AutoImageCmdString = AutoImageStateValues[value]
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAutoSwitch(self, value, qualifier):

        AutoSwitchStateValues = {
            'High': 'w1AUSW\r',
            'Low': 'w2AUSW\r',
            'Off': 'w0AUSW\r',
        }

        AutoSwitchCmdString = AutoSwitchStateValues[value]

        self.__SetHelper('AutoSwitch', AutoSwitchCmdString, value, qualifier)

    def UpdateAutoSwitch(self, value, qualifier):

        AutoSwitchCmdString = 'wAUSW\r\n'
        self.__UpdateHelper('AutoSwitch', AutoSwitchCmdString, value, qualifier)

    def __MatchAutoSwitch(self, match, qualifier):

        AutoSwitchStateNames = {
            '0': 'Off',
            '1': 'High',
            '2': 'Low',
        }
        AutoSwitchCmdString = AutoSwitchStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitch', AutoSwitchCmdString, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeStateValues = {
            'Mode 1': '1X',
            'Mode 2': '2X',
            'Off': '0X',
        }

        ExecutiveModeCmdString = ExecutiveModeStateValues[value]

        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeStateValues = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off',
        }

        Mode = match.group(1).decode()
        value = ExecutiveModeStateValues[Mode]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeStateValues = {
            'On': '1F',
            'Off': '0F',
        }

        FreezeCmdString = FreezeStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def UpdateFreeze(self, value, qualifier):

        FreezeCmdString = 'F'
        self.__UpdateHelper('Freeze', FreezeCmdString, value, qualifier)

    def __MatchFreeze(self, match, qualifier):

        FreezeStateNames = {
            '0': 'Off',
            '1': 'On',
        }

        Mode = match.group(1).decode()
        value = FreezeStateNames[Mode]
        self.WriteStatus('Freeze', value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            '1': '1!',
            '2': '2!',
            '3': '3!'
        }

        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, qualifier)

    def SetInputPresetSave(self, value, qualifier):

        InputPresetSave = {
            'Min': 0,
            'Max': 128,
        }

        if int(value) < InputPresetSave['Min'] or int(value) > InputPresetSave['Max']:
            self.Discard('Invalid Command for SetInputPresetSave')
        else:
            InputPresetSaveCmdString = '2*{0},'.format(value)
            self.__SetHelper('InputPresetSave', InputPresetSaveCmdString, value, qualifier)

    def SetInputPresetRecall(self, value, qualifier):

        InputPresetRecall = {
            'Min': 0,
            'Max': 128,
        }

        if InputPresetRecall['Min'] <= int(value) <= InputPresetRecall['Max']:
            InputPresetRecallCmdString = '2*{0}.'.format(value)
            self.__SetHelper('InputPresetRecall', InputPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputPresetRecall')

    def SetHDMIOutputFormat(self, value, qualifier):

        HDMIOutputFormat = {
            'Auto': '0',
            'DVI': '1',
            'HDMI RGB FULL': '2',
            'HDMI RGB LIMITED': '3',
            'HDMI 444 YUV FULL': '4',
            'HDMI 444 YUV LIMITED': '5',
            'HDMI 422 YUV FULL': '6',
            'HDMI 422 YUV LIMITED': '7',
        }
        HDMIOutputCmdString = 'w{0}VTPO\r'.format(HDMIOutputFormat[value])
        self.__SetHelper('HDMIOutputFormat', HDMIOutputCmdString, value, qualifier)

    def UpdateHDMIOutputFormat(self, value, qualifier):

        HDMIOutputCmdString = 'wVTPO\r'
        self.__UpdateHelper('HDMIOutputFormat', HDMIOutputCmdString, value, qualifier)

    def __MatchHDMIOutputFormat(self, match, qualifier):

        HDMIOutput = {
            '0': 'Auto',
            '1': 'DVI',
            '2': 'HDMI RGB FULL',
            '3': 'HDMI RGB LIMITED',
            '4': 'HDMI 444 YUV FULL',
            '5': 'HDMI 444 YUV LIMITED',
            '6': 'HDMI 422 YUV FULL',
            '7': 'HDMI 422 YUV LIMITED',
        }
        self.WriteStatus('HDMIOutputFormat', HDMIOutput[match.group(1).decode()], qualifier)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wI3HDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No source detected',
            '1': 'Source detected with HDCP',
            '2': 'Source detected but no HDCP is present'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputStatus', value, None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wO1HDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No sink detected',
            '1': 'Sink detected with HDCP',
            '2': 'Sink detected but no HDCP is present'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHorizontalSize(self, value, qualifier):

        HorizontalSizeConstraints = {
            'Min': 0,
            'Max': 4400,
        }

        if HorizontalSizeConstraints['Min'] <= value <= HorizontalSizeConstraints['Max']:
            HorizontalSizeCmdString = 'w{0}HSIZ\r'.format(value)
            self.__SetHelper('HorizontalSize', HorizontalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalSize')

    def UpdateHorizontalSize(self, value, qualifier):

        HorizontalSizeCmdString = 'wHSIZ\r'
        self.__UpdateHelper('HorizontalSize', HorizontalSizeCmdString, value, qualifier)

    def __MatchHorizontalSize(self, match, qualifier):

        Size = int(match.group(1).decode())
        self.WriteStatus('HorizontalSize', Size, qualifier)

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeStateValues = {
            'Off': 'w0PSAV\r',
            'On': 'w1PSAV\r',
        }
        PowerSaveModeCmdString = PowerSaveModeStateValues[value]
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = 'wPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, qualifier):

        PowerSaveModeStateNames = {
            0: 'Off',
            1: 'On',
        }
        Mode = PowerSaveModeStateNames[int(match.group(1).decode())]
        self.WriteStatus('PowerSaveMode', Mode, qualifier)

    def SetScreenSaverTimeout(self, value, qualifier):

        TimerStateValues = {
            'Disabled': 0,
            'NoTimeOut': 501,
        }
        TimerCmdString = ''
        if value < TimerStateValues['Disabled'] or value > TimerStateValues['NoTimeOut']:
            self.Discard('Invalid Command for SetScreenSaverTimeout')
        elif value == TimerStateValues['Disabled']:
            TimerCmdString = 'wT' + str(TimerStateValues['Disabled']) + 'SSAV\r'
        elif value == TimerStateValues['NoTimeOut']:
            TimerCmdString = 'wT' + str(TimerStateValues['NoTimeOut']) + 'SSAV\r'
        else:
            TimerCmdString = 'wT' + str(value) + 'SSAV\r'
        if TimerCmdString:
            self.__SetHelper('ScreenSaverTimeout', TimerCmdString, str(value), qualifier)
        else:
            self.Discard('Invalid Command for SetScreenSaverTimeout')

    def UpdateScreenSaverTimeout(self, value, qualifier):

        TimerCmdString = 'wTSSAV\r'
        self.__UpdateHelper('ScreenSaverTimeout', TimerCmdString, value, qualifier)

    def __MatchScreenSaverTimeout(self, match, qualifier):

        time = int(match.group(1).decode())
        self.WriteStatus('ScreenSaverTimeout', time, qualifier)

    def SetScreenSaverMode(self, value, qualifier):

        ScreenModeStateValues = {
            'Black Screen': 1,
            'Blue Screen': 2,
        }

        ModeCmdString = 'wM' + str(ScreenModeStateValues[value]) + 'SSAV\r'
        self.__SetHelper('ScreenSaverMode', ModeCmdString, value, qualifier)

    def UpdateScreenSaverMode(self, value, qualifier):

        ModeCmdString = 'wMSSAV\r'
        self.__UpdateHelper('ScreenSaverMode', ModeCmdString, value, qualifier)

    def __MatchScreenSaverMode(self, match, qualifier):

        ScreenModeStateValues = {
            '1': 'Black Screen',
            '2': 'Blue Screen',
        }
        Mode = match.group(1).decode()
        self.WriteStatus('ScreenSaverMode', ScreenModeStateValues[Mode], qualifier)

    def SetUserPresetSave(self, value, qualifier):

        UserPresetSave = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        UserPresetSaveCmdString = '1*{0},'.format(UserPresetSave[value])
        self.__SetHelper('UserPresetSave', UserPresetSaveCmdString, value, qualifier)

    def SetUserPresetRecall(self, value, qualifier):

        UserPresetRecall = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        UserPresetRecallCmdString = '1*{0}.'.format(UserPresetRecall[value])
        self.__SetHelper('UserPresetRecall', UserPresetRecallCmdString, value, qualifier)

    def SetVerticalSize(self, value, qualifier):

        VerticalSizeConstraints = {
            'Min': 0,
            'Max': 4400,
        }

        if VerticalSizeConstraints['Min'] <= value <= VerticalSizeConstraints['Max']:
            VerticalSizeCmdString = 'w{0}VSIZ\r'.format(value)
            self.__SetHelper('VerticalSize', VerticalSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalSize')

    def __MatchVerticalSize(self, match, qualifier):

        Size = int(match.group(1).decode())
        self.WriteStatus('VerticalSize', Size, qualifier)

    def UpdateVerticalSize(self, value, qualifier):

        VerticalSizeCmdString = 'wVSIZ\r'
        self.__UpdateHelper('VerticalSize', VerticalSizeCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'Mode 1': '1B',
            'Mode 2': '2B',
            'Off': '0B'
        }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):

        VideoMuteStateNames = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
        }
        value = match.group(1).decode()
        self.WriteStatus('VideoMute', VideoMuteStateNames[value], qualifier)

    def SetResolution(self, value, qualifier):

        ResolutionConstraints = {
            '640x480 50Hz': '10',
            '640x480 60Hz': '11',
            '640x480 75Hz': '12',
            '800x600 50Hz': '13',
            '800x600 60Hz': '14',
            '800x600 75Hz': '15',
            '852x480 50Hz': '16',
            '852x480 60Hz': '17',
            '852x480 75Hz': '18',
            '1024x768 50Hz': '19',
            '1024x768 60Hz': '20',
            '1024x768 75Hz': '21',
            '1024x852 50Hz': '22',
            '1024x852 60Hz': '23',
            '1024x852 75Hz': '24',
            '1024x1024 50Hz': '25',
            '1024x1024 60Hz': '26',
            '1024x1024 75Hz': '27',
            '1280x768 50Hz': '28',
            '1280x768 60Hz': '29',
            '1280x768 75Hz': '30',
            '1280x800 50Hz': '31',
            '1280x800 60Hz': '32',
            '1280x800 75Hz': '33',
            '1280x1024 50Hz': '34',
            '1280x1024 60Hz': '35',
            '1280x1024 75Hz': '36',
            '1360x765 50Hz': '37',
            '1360x765 60Hz': '38',
            '1360x765 75Hz': '39',
            '1360x768 50Hz': '40',
            '1360x768 60Hz': '41',
            '1360x768 75Hz': '42',
            '1365x768 50Hz': '43',
            '1365x768 60Hz': '44',
            '1365x768 75Hz': '45',
            '1366x768 50Hz': '46',
            '1366x768 60Hz': '47',
            '1366x768 75Hz': '48',
            '1365x1024 50Hz': '49',
            '1365x1024 60Hz': '50',
            '1365x1024 75Hz': '51',
            '1440x900 50Hz': '52',
            '1440x900 60Hz': '53',
            '1440x900 75Hz': '54',
            '1400x1050 50Hz': '55',
            '1400x1050 60Hz': '56',
            '1600x900 50Hz': '57',
            '1600x900 60Hz': '58',
            '1680x1050 50Hz': '59',
            '1680x1050 60Hz': '60',
            '1600x1200 50Hz': '61',
            '1600x1200 60Hz': '62',
            '1920x1200 50Hz': '63',
            '1920x1200 60Hz': '64',
            '480p 59.94Hz': '65',
            '480p 60Hz': '66',
            '576p 50Hz': '67',
            '720p 25Hz': '68',
            '720p 29.97Hz': '69',
            '720p 30Hz': '70',
            '720p 50Hz': '71',
            '720p 59.94Hz': '72',
            '720p 60Hz': '73',
            '1080i 50Hz': '74',
            '1080i 59.94Hz': '75',
            '1080i 60Hz': '76',
            '1080p 23.98Hz': '77',
            '1080p 24Hz': '78',
            '1080p 25Hz': '79',
            '1080p 29.97Hz': '80',
            '1080p 30Hz': '81',
            '1080p 50Hz': '82',
            '1080p 59.94Hz': '83',
            '1080p 60Hz': '84',
            '2048x1080 2k 23.98Hz': '85',
            '2048x1080 2k 24Hz': '86',
            '2048x1080 2k 25Hz': '87',
            '2048x1080 2k 29.97Hz': '88',
            '2048x1080 2k 30Hz': '89',
            '2048x1080 2k 50Hz': '90',
            '2048x1080 2k 59.94Hz': '91',
            '2048x1080 2k 60Hz': '92',
        }

        ResolutionCmdString = 'w{0}RATE\r'.format(ResolutionConstraints[value])
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def UpdateResolution(self, value, qualifier):

        ResolutionCmdString = 'wRATE\r\n'
        self.__UpdateHelper('Resolution', ResolutionCmdString, value, qualifier)

    def __MatchResolution(self, match, qualifier):

        ResolutionConstraints = {
            '10': '640x480 50Hz',
            '11': '640x480 60Hz',
            '12': '640x480 75Hz',
            '13': '800x600 50Hz',
            '14': '800x600 60Hz',
            '15': '800x600 75Hz',
            '16': '852x480 50Hz',
            '17': '852x480 60Hz',
            '18': '852x480 75Hz',
            '19': '1024x768 50Hz',
            '20': '1024x768 60Hz',
            '21': '1024x768 75Hz',
            '22': '1024x852 50Hz',
            '23': '1024x852 60Hz',
            '24': '1024x852 75Hz',
            '25': '1024x1024 50Hz',
            '26': '1024x1024 60Hz',
            '27': '1024x1024 75Hz',
            '28': '1280x768 50Hz',
            '29': '1280x768 60Hz',
            '30': '1280x768 75Hz',
            '31': '1280x800 50Hz',
            '32': '1280x800 60Hz',
            '33': '1280x800 75Hz',
            '34': '1280x1024 50Hz',
            '35': '1280x1024 60Hz',
            '36': '1280x1024 75Hz',
            '37': '1360x765 50Hz',
            '38': '1360x765 60Hz',
            '39': '1360x765 75Hz',
            '40': '1360x768 50Hz',
            '41': '1360x768 60Hz',
            '42': '1360x768 75Hz',
            '43': '1365x768 50Hz',
            '44': '1365x768 60Hz',
            '45': '1365x768 75Hz',
            '46': '1366x768 50Hz',
            '47': '1366x768 60Hz',
            '48': '1366x768 75Hz',
            '49': '1365x1024 50Hz',
            '50': '1365x1024 60Hz',
            '51': '1365x1024 75Hz',
            '52': '1440x900 50Hz',
            '53': '1440x900 60Hz',
            '54': '1440x900 75Hz',
            '55': '1400x1050 50Hz',
            '56': '1400x1050 60Hz',
            '57': '1600x900 50Hz',
            '58': '1600x900 60Hz',
            '59': '1680x1050 50Hz',
            '60': '1680x1050 60Hz',
            '61': '1600x1200 50Hz',
            '62': '1600x1200 60Hz',
            '63': '1920x1200 50Hz',
            '64': '1920x1200 60Hz',
            '65': '480p 59.94Hz',
            '66': '480p 60Hz',
            '67': '576p 50Hz',
            '68': '720p 25Hz',
            '69': '720p 29.97Hz',
            '70': '720p 30Hz',
            '71': '720p 50Hz',
            '72': '720p 59.94Hz',
            '73': '720p 60Hz',
            '74': '1080i 50Hz',
            '75': '1080i 59.94Hz',
            '76': '1080i 60Hz',
            '77': '1080p 23.98Hz',
            '78': '1080p 24Hz',
            '79': '1080p 25Hz',
            '80': '1080p 29.97Hz',
            '81': '1080p 30Hz',
            '82': '1080p 50Hz',
            '83': '1080p 59.94Hz',
            '84': '1080p 60Hz',
            '85': '2048x1080 2k 23.98Hz',
            '86': '2048x1080 2k 24Hz',
            '87': '2048x1080 2k 25Hz',
            '88': '2048x1080 2k 29.97Hz',
            '89': '2048x1080 2k 30Hz',
            '90': '2048x1080 2k 50Hz',
            '91': '2048x1080 2k 59.94Hz',
            '92': '2048x1080 2k 60Hz',
        }

        value = ResolutionConstraints[match.group(1).decode()]
        self.WriteStatus('Resolution', value, None)

    def UpdateSignalStatus(self, value, qualifier):
        SignalCmdString = 'w0LS\r'
        self.__UpdateHelper('SignalStatus', SignalCmdString, value, qualifier)

    def __MatchSignalStatus(self, match, qualifier):

        SignalStateNames = {
            '0': 'Signal Not Detected',
            '1': 'Signal Detected',
        }

        self.WriteStatus('SignalStatus', SignalStateNames[match.group(1).decode()], {'Input': '1'})
        self.WriteStatus('SignalStatus', SignalStateNames[match.group(2).decode()], {'Input': '2'})
        self.WriteStatus('SignalStatus', SignalStateNames[match.group(3).decode()], {'Input': '3'})

    def UpdateTemperature(self, value, qualifier):

        TemperatureCmdString = 'w20STAT\r'
        self.__UpdateHelper('Temperature', TemperatureCmdString, value, qualifier)

    def __MatchTemperature(self, match, qualifier):

        value = int(match.group(1).decode())
        self.WriteStatus('Temperature', value, qualifier)

    def __MatchError(self, match, qualifier):

        DeviceErrorCodes = {
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'Invalid command for signal type',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }
        if match.group(1).decode('ascii') in DeviceErrorCodes:
            self.Error([DeviceErrorCodes[match.group(1).decode('ascii')]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode('ascii')])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
