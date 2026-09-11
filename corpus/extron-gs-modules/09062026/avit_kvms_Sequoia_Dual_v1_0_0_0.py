from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import base64
import urllib.error
import urllib.request

class DeviceSerialClass:
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatioCustomSetting': {'Parameters': ['Window', 'Width', 'Height'], 'Status': {}},
            'AspectRatioDetectMode': {'Parameters': ['Window'], 'Status': {}},
            'AspectRatioKeep': {'Parameters': ['Window'], 'Status': {}},
            'AudioFadeTime': {'Status': {}},
            'AudioInputSource': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioVolume': {'Status': {}},
            'DefaultLayout': {'Status': {}},
            'DeviceSettings': {'Parameters': ['Mode'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'Input': {'Parameters': ['Window'], 'Status': {}},
            'InputLabel': {'Parameters': ['Port'], 'Status': {}},
            'OutputResolution': {'Status': {}},
            'Preset': {'Parameters': ['Mode'], 'Status': {}},
            'VideoFadeLevel': {'Status': {}},
            'WindowBorderWidth': {'Parameters': ['Window'], 'Status': {}},
            'WindowColor': {'Parameters': ['Window', 'Type', 'Red', 'Green', 'Blue'], 'Status': {}},
            'WindowFullScreenMode': {'Parameters': ['Window', 'Set Fullscreen to Background'], 'Status': {}},
            'WindowLabel': {'Status': {}},
            'WindowLabelFontSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelText': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelTextColor': {'Parameters': ['Window', 'Blending Level', 'Text Color Red', 'Text Color Green', 'Text Color Blue', 'Label Color Red', 'Label Color Green', 'Label Color Blue'], 'Status': {}},
            'WindowPosition': {'Parameters': ['Window', 'Top Left X Position', 'Top Left Y Position', 'Width', 'Height'], 'Status': {}},
            'WindowPriority': {'Status': {}},
            'WindowSwap': {'Parameters': ['Window'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'Dual-(?P<value>[\S ]+)[\r\n]'), self.__MatchFirmwareVersion, None)

    def SetAspectRatioCustomSetting(self, value, qualifier):

        WindowStates = {
            'All': '00',
            '1': '01',
            '2': '02'
        }

        WidthStates = {
            'Off': '0',
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

        HeightStates = {
            'Off': '0',
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

        if qualifier['Window'] in WindowStates and qualifier['Width'] in WidthStates and qualifier['Height'] in HeightStates:
            if (qualifier['Width'] == 'Off' and qualifier['Height'] == 'Off') or (qualifier['Window'] != 'Off' and qualifier['Height'] != 'Off'):
                AspectRatioCustomSettingCmdString = 'ZR 0000{} {}{}\r'.format(WindowStates[qualifier['Window']], WidthStates[qualifier['Width']], HeightStates[qualifier['Height']])
                self.__SetHelper('AspectRatioCustomSetting', AspectRatioCustomSettingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatioCustomSetting')

    def SetAspectRatioDetectMode(self, value, qualifier):

        WindowStates = {
            'All': '00',
            '1': '01',
            '2': '02'
        }

        ValueStateValues = {
            'Auto': '0',
            'Custom': '1'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            AspectRatioDetectModeCmdString = 'ZN 0000{} ARD {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('AspectRatioDetectMode', AspectRatioDetectModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatioDetectMode')

    def SetAspectRatioKeep(self, value, qualifier):

        WindowStates = {
            'All': '00',
            '1': '01',
            '2': '02'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            AspectRatioKeepCmdString = 'ZN 0000{} KAR {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('AspectRatioKeep', AspectRatioKeepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatioKeep')

    def SetAudioFadeTime(self, value, qualifier):

        ValueStateValues = {
            '0 Seconds': '0',
            '1 Second': '1',
            '2 Seconds': '2',
            '3 Seconds': '3',
            '4 Seconds': '4'
        }

        if value in ValueStateValues:
            AudioFadeTimeCmdString = 'ZO 000000 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioFadeTime', AudioFadeTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioFadeTime')

    def SetAudioInputSource(self, value, qualifier):

        ValueStateValues = {
            'DVI-L': '1',
            'DVI-R': '2',
            'HDMI-L': '3',
            'HDMI-R': '4',
            'Analog 1': '5',
            'Analog 2': '6',
            'Analog 3': '7',
            'Analog 4': '8'
        }

        if value in ValueStateValues:
            AudioInputSourceCmdString = 'ZO 000000 I {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioInputSource', AudioInputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputSource')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'ZN 000000 A {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetAudioVolume(self, value, qualifier):

        if 0 <= value <= 100:
            AudioVolumeCmdString = 'ZO 000000 V {}\r'.format(value)
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def SetDefaultLayout(self, value, qualifier):

        ValueStateValues = {
            'Picture In Picture': 'PIP',
            'Picture Over Picture': 'POP',
            'Picture By Picture': 'PBP',
            'Full Screen': 'FS'
        }

        if value in ValueStateValues:
            DefaultLayoutCmdString = 'ZA 000000 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('DefaultLayout', DefaultLayoutCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDefaultLayout')

    def SetDeviceSettings(self, value, qualifier):

        ModeStates = {
            'OSD': 'O',
            'Streaming': 'S',
            'Background Image': 'BG',
            'Window Priority / Lock Position': 'WP',
            'Video Alarm': 'VA',
            'Signal Format': 'SF',
            'Audio Follow Video': 'AFV',
            'Full Screen with Audio Output': 'FSAO',
            'Display Label Full Screen': 'DLFS'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if qualifier['Mode'] in ModeStates and value in ValueStateValues:
            DeviceSettingsCmdString = 'ZN 000000 {} {}\r'.format(ModeStates[qualifier['Mode']], ValueStateValues[value])
            self.__SetHelper('DeviceSettings', DeviceSettingsCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDeviceSettings')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'ZH 000000\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group('value').decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetInput(self, value, qualifier):

        WindowStates = {
            'All': '00',
            '1': '01',
            '2': '02'
        }

        ValueStateValues = {
            'DVI-L': '1',
            'DVI-R': '2',
            'HDMI-L': '3',
            'HDMI-R': '4'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            InputCmdString = 'ZI 0000{} I {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetInputLabel(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 4 and 1 <= len(value) <= 20:
            InputLabelCmdString = 'ZI 000000  L {} "{}"\r'.format(qualifier['Port'], value)
            self.__SetHelper('InputLabel', InputLabelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLabel')

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = {
            '640x480, 60Hz': '69',
            '800x600x 50Hz': '42',
            '800x600, 60Hz': '1',
            '800x600, 75Hz': '47',
            '1024x768, 50Hz': '50',
            '1024x768, 60Hz': '2',
            '1024x768, 75Hz': '11',
            '1280x720, 50Hz': '30',
            '1280x720, 59.94Hz': '68',
            '1280x720, 60Hz': '15',
            '1280x720, 75Hz': '48',
            '1280x768, 50Hz': '32',
            '1280x768, 60Hz': '22',
            '1280x768, 75Hz': '49',
            '1360x768, 50Hz': '38',
            '1360x768, 60Hz': '20',
            '1360x768, 75Hz': '21',
            '1400x1050, 50Hz': '34',
            '1400x1050, 60Hz': '35',
            '1400x1050, 75Hz': '50',
            '1440x900, 50Hz': '46',
            '1440x900, 60Hz': '45',
            '1440x900, 75Hz': '51',
            '1600x1200, 50Hz': '39',
            '1600x1200, 60Hz': '10',
            '1600x1200, 75Hz': '52',
            '1680x1050, 50Hz': '41',
            '1680x1050, 60Hz': '40',
            '1680x1050, 75Hz': '53',
            '1920x1080, 50Hz': '28',
            '1920x1080, 60Hz': '26',
            '1920x1200, 50Hz': '37',
            '1920x1200, 60Hz': '36'
        }

        if value in ValueStateValues:
            OutputResolutionCmdString = 'ZM 000000 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def SetPreset(self, value, qualifier):

        ModeStates = {
            'Load': 'L',
            'Save': 'S'
        }

        if qualifier['Mode'] in ModeStates and 1 <= len(value) <= 32:
            if value.lower() == 'latest':
                PresetCmdString = 'ZP 000000 {}\r'.format(ModeStates[qualifier['Mode']])
            else:
                PresetCmdString = 'ZP 000000 {} "{}"\r'.format(ModeStates[qualifier['Mode']], value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetVideoFadeLevel(self, value, qualifier):

        if 1 <= int(value) <= 15:
            VideoFadeLevelCmdString = 'ZN 000000 FADE {}\r'.format(value)
            self.__SetHelper('VideoFadeLevel', VideoFadeLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoFadeLevel')

    def SetWindowBorderWidth(self, value, qualifier):

        WindowStates = {
            'All': '00',
            '1': '01',
            '2': '02'
        }

        ValueStateValues = {
            '0 pixels': '0',
            '2 pixels': '2',
            '4 pixels': '4',
            '6 pixels': '6'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            WindowBorderWidthCmdString = 'ZB 0000{} {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('WindowBorderWidth', WindowBorderWidthCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowBorderWidth')

    def SetWindowColor(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        TypeStates = {
            'Border Color': 'B',
            'Label Background Color': 'L'
        }

        if 1 <= int(qualifier['Window']) <= 2 and qualifier['Type'] in TypeStates and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            WindowColorCmdString = 'ZC 0000{} {} {:0>3}{:0>3}{:0>3}\r'.format(WindowStates[qualifier['Window']], TypeStates[qualifier['Type']], qualifier['Red'], qualifier['Green'], qualifier['Blue'])
            self.__SetHelper('WindowColor', WindowColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowColor')

    def SetWindowFullScreenMode(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        SetFullscreentoBackgroundStates = {
            'On': '1',
            'Off': '0'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Window']) <= 2 and qualifier['Set Fullscreen to Background'] in SetFullscreentoBackgroundStates and value in ValueStateValues:
            if qualifier['Set Fullscreen to Background'] == 'Off':
                WindowFullScreenModeCmdString = 'ZF 0000{} {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            else:
                WindowFullScreenModeCmdString = 'ZF 0000{} {} {}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value], SetFullscreentoBackgroundStates[qualifier['Set Fullscreen to Background']])
            self.__SetHelper('WindowFullScreenMode', WindowFullScreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowFullScreenMode')

    def SetWindowLabel(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if value in ValueStateValues:
            WindowLabelCmdString = 'ZN 000000 L {}\r'.format(ValueStateValues[value])
            self.__SetHelper('WindowLabel', WindowLabelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowLabel')

    def SetWindowLabelFontSize(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        if 1 <= int(qualifier['Window']) <= 2 and 8 <= int(value) <= 96:
            WindowLabelFontSizeCmdString = 'ZX 0000{} F {}\r'.format(WindowStates[qualifier['Window']], value)
            self.__SetHelper('WindowLabelFontSize', WindowLabelFontSizeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowLabelFontSize')

    def SetWindowLabelText(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        if 1 <= int(qualifier['Window']) <= 2 and 1 <= len(value) <= 31:
            WindowLabelTextCmdString = 'ZX 0000{} L "{}"\r'.format(WindowStates[qualifier['Window']], value)
            self.__SetHelper('WindowLabelText', WindowLabelTextCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowLabelText')

    def SetWindowLabelTextColor(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        if 1 <= int(qualifier['Window']) <= 2 and 0 <= int(qualifier['Blending Level']) <= 7 and \
                0 <= qualifier['Text Color Red'] <= 255 and 0 <= qualifier['Text Color Green'] <= 255 and \
                0 <= qualifier['Text Color Blue'] <= 255 and 0 <= qualifier['Label Color Red'] <= 255 and \
                0 <= qualifier['Label Color Green'] <= 255 and 0 <= qualifier['Label Color Blue'] <= 255 and \
                1 <= len(value) <= 31:
            WindowLabelTextColorCmdString = 'ZL 0000{} {}{:0>3}{:0>3} {:0>3}{:0>3}{:0>3} "{}"\r'.format(WindowStates[qualifier['Window']], qualifier['Blending Level'], qualifier['Text Color Red'], qualifier['Text Color Blue'], qualifier['Label Color Red'], qualifier['Label Color Green'], qualifier['Label Color Blue'], value)
            self.__SetHelper('WindowLabelTextColor', WindowLabelTextColorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowLabelTextColor')

    def SetWindowPosition(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        if 1 <= int(qualifier['Window']) <= 2 and qualifier['Top Left X Position'] >= 0 and qualifier['Top Left Y Position'] >= 0 and qualifier['Width'] >= 0 and qualifier['Height'] >= 0:
            WindowPositionCmdString = 'ZW 0000{} {} {} {} {}\r'.format(WindowStates[qualifier['Window']], qualifier['Top Left X Position'], qualifier['Top Left Y Position'], qualifier['Width'], qualifier['Height'])
            self.__SetHelper('WindowPosition', WindowPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPosition')

    def SetWindowPriority(self, value, qualifier):

        ValueStateValues = {
            'Source 1': '01',
            'Source 2': '02'
        }

        if value in ValueStateValues:
            WindowPriorityCmdString = 'ZN 000000 WP {}\r'.format(ValueStateValues[value])
            self.__SetHelper('WindowPriority', WindowPriorityCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowPriority')

    def SetWindowSwap(self, value, qualifier):

        WindowStates = {
            '1': '01',
            '2': '02'
        }

        ValueStateValues = {
            'Set Top Most': '',
            'Swap': ' S'
        }

        if 1 <= int(qualifier['Window']) <= 2 and value in ValueStateValues:
            WindowSwapCmdString = 'ZW 0000{}{}\r'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('WindowSwap', WindowSwapCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWindowSwap')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

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

            self.Send(commandstring)

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
        index = 0  # Start of possible good data

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


class DeviceHTTPClass:
    def __init__(self, ipAddress, port):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3

        self.RootURL = 'http://{0}:{1}/'.format(ipAddress, port)
        self.Opener = urllib.request.build_opener(urllib.request.HTTPBasicAuthHandler())

        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatioCustomSetting': {'Parameters': ['Window', 'Width', 'Height'], 'Status': {}},
            'AspectRatioDetectMode': {'Parameters': ['Window'], 'Status': {}},
            'AspectRatioKeep': {'Parameters': ['Window'], 'Status': {}},
            'AudioFadeTime': {'Status': {}},
            'AudioInputSource': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AudioVolume': {'Status': {}},
            'DefaultLayout': {'Status': {}},
            'DeviceSettings': {'Parameters': ['Mode'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'Input': {'Parameters': ['Window'], 'Status': {}},
            'InputLabel': {'Parameters': ['Port'], 'Status': {}},
            'OutputResolution': {'Status': {}},
            'Preset': {'Parameters': ['Mode'], 'Status': {}},
            'VideoFadeLevel': {'Status': {}},
            'WindowBorderWidth': {'Parameters': ['Window'], 'Status': {}},
            'WindowColor': {'Parameters': ['Window', 'Type', 'Red', 'Green', 'Blue'], 'Status': {}},
            'WindowFullScreenMode': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabel': {'Status': {}},
            'WindowLabelFontSize': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelText': {'Parameters': ['Window'], 'Status': {}},
            'WindowLabelTextColor': {'Parameters': ['Window', 'Blending Level', 'Text Color Red', 'Text Color Green', 'Text Color Blue', 'Label Color Red', 'Label Color Green', 'Label Color Blue'], 'Status': {}},
            'WindowPosition': {'Parameters': ['Window', 'Top Left X Position', 'Top Left Y Position', 'Width', 'Height'], 'Status': {}},
            'WindowPriority': {'Status': {}},
            'WindowSwap': {'Parameters': ['Window'], 'Status': {}},
        }

        self.FirmwareVersionRegex = re.compile(r'Dual-(?P<value>[\S ]+?)[\r\n]')

    def SetAspectRatioCustomSetting(self, value, qualifier):

        WindowStates = {
            'All': 'all',
            '1': '1',
            '2': '2'
        }

        if qualifier['Window'] in WindowStates and 1 <= int(qualifier['Width']) <= 20 and 1 <= int(qualifier['Height']) <= 20:
            AspectRatioCustomSettingCmdString = 'cgi-bin/SetAspectRatio.cgi?window={}&type=custom&ratio=[{},{}]'.format(WindowStates[qualifier['Window']], qualifier['Width'], qualifier['Height'])
            self.__SetHelper('AspectRatioCustomSetting', value, qualifier, url=AspectRatioCustomSettingCmdString)
        else:
            self.Discard('Invalid Command for SetAspectRatioCustomSetting')

    def SetAspectRatioAutoDetectMode(self, value, qualifier):

        WindowStates = {
            'All': 'all',
            '1': '1',
            '2': '2'
        }

        if qualifier['Window'] in WindowStates:
            AspectRatioDetectModeCmdString = 'cgi-bin/SetAspectRatio.cgi?window={}&type=auto'.format(WindowStates[qualifier['Window']])
            self.__SetHelper('AspectRatioDetectMode', value, qualifier, url=AspectRatioDetectModeCmdString)
        else:
            self.Discard('Invalid Command for SetAspectRatioAutoDetectMode')

    def SetAspectRatioKeep(self, value, qualifier):

        WindowStates = {
            'All': 'all',
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            AspectRatioKeepCmdString = 'cgi-bin/SetAspectRatio.cgi?window={}&enable={}'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('AspectRatioKeep', value, qualifier, url=AspectRatioKeepCmdString)
        else:
            self.Discard('Invalid Command for SetAspectRatioKeep')

    def SetAudioFadeTime(self, value, qualifier):

        ValueStateValues = {
            '0 Seconds': '0',
            '1 Second': '1',
            '2 Seconds': '2',
            '3 Seconds': '3',
            '4 Seconds': '4'
        }

        if value in ValueStateValues:
            AudioFadeTimeCmdString = 'cgi-bin/SetAudio.cgi?fade_in={}'.format(ValueStateValues[value])
            self.__SetHelper('AudioFadeTime', value, qualifier, url=AudioFadeTimeCmdString)
        else:
            self.Discard('Invalid Command for SetAudioFadeTime')

    def SetAudioInputSource(self, value, qualifier):

        ValueStateValues = {
            'DVI-L': 'digital_1',
            'DVI-R': 'digital_2',
            'HDMI-L': 'digital_3',
            'HDMI-R': 'digital_4',
            'Analog 1': 'analog_1',
            'Analog 2': 'analog_2',
            'Analog 3': 'analog_3',
            'Analog 4': 'analog_4'
        }

        if value in ValueStateValues:
            AudioInputSourceCmdString = 'cgi-bin/SetAudio.cgi?source={}'.format(ValueStateValues[value])
            self.__SetHelper('AudioInputSource', value, qualifier, url=AudioInputSourceCmdString)
        else:
            self.Discard('Invalid Command for SetAudioInputSource')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = 'cgi-bin/SetAudio.cgi?enable={}'.format(ValueStateValues[value])
            self.__SetHelper('AudioMute', value, qualifier, url=AudioMuteCmdString)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetAudioVolume(self, value, qualifier):

        if 0 <= value <= 100:
            AudioVolumeCmdString = 'cgi-bin/SetAudio.cgi?volume={}'.format(value)
            self.__SetHelper('AudioVolume', value, qualifier, url=AudioVolumeCmdString)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def SetDefaultLayout(self, value, qualifier):

        ValueStateValues = {
            'Picture In Picture': 'PIP',
            'Picture Over Picture': 'POP',
            'Picture By Picture': 'PBP',
            'Full Screen': 'FS'
        }

        if value in ValueStateValues:
            DefaultLayoutCmdString = 'cgi-bin/SetLayout.cgi?type={}'.format(ValueStateValues[value])
            self.__SetHelper('DefaultLayout', value, qualifier, url=DefaultLayoutCmdString)
        else:
            self.Discard('Invalid Command for SetDefaultLayout')

    def SetDeviceSettings(self, value, qualifier):

        ModeStates = {
            'Background Image': 'backgroundimage',
            'Video Alarm': 'videoalarm',
            'Signal Format': 'signalformat',
            'OSD': 'osd',
            'Window Priority / Lock Position': 'lockposition',
            'Streaming': 'streaming'
        }

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if qualifier['Mode'] in ModeStates and value in ValueStateValues:
            DeviceSettingsCmdString = 'cgi-bin/SetCommonParameters.cgi?{}={}'.format(ModeStates[qualifier['Mode']], ValueStateValues[value])
            self.__SetHelper('DeviceSettings', value, qualifier, url=DeviceSettingsCmdString)
        else:
            self.Discard('Invalid Command for SetDeviceSettings')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'cgi-bin/GetHelp.cgi'
        res = self.__UpdateHelper('FirmwareVersion', value, qualifier, url=FirmwareVersionCmdString)
        if res:
            try:
                valueMatch = re.search(self.FirmwareVersionRegex, res)
                value = valueMatch.group('value')
                self.WriteStatus('FirmwareVersion', value, qualifier)
            except (ValueError, IndexError, AttributeError):
                self.Error(['Firmware Version: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        WindowStates = {
            'All': 'all',
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'DVI-L': '1',
            'DVI-R': '2',
            'HDMI-L': '3',
            'HDMI-R': '4'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            InputCmdString = 'cgi-bin/SetVideoOutputRouting.cgi?window={}&source={}'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('Input', value, qualifier, url=InputCmdString)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetInputLabel(self, value, qualifier):

        if 1 <= int(qualifier['Port']) <= 4 and 1 <= len(value) <= 20:
            tempValue = value.replace(' ', '%20')
            InputLabelCmdString = 'cgi-bin/SetInputLabel.cgi?input={}&text={}'.format(qualifier['Port'], tempValue)
            self.__SetHelper('InputLabel', value, qualifier, url=InputLabelCmdString)
        else:
            self.Discard('Invalid Command for SetInputLabel')

    def SetOutputResolution(self, value, qualifier):

        ValueStateValues = [
            '640x480, 60Hz',
            '800x600x 50Hz',
            '800x600, 60Hz'
            '800x600, 75Hz',
            '1024x768, 50Hz',
            '1024x768, 60Hz'
            '1024x768, 75Hz',
            '1280x720, 50Hz',
            '1280x720, 59.94Hz',
            '1280x720, 60Hz',
            '1280x720, 75Hz',
            '1280x768, 50Hz',
            '1280x768, 60Hz',
            '1280x768, 75Hz',
            '1360x768, 50Hz',
            '1360x768, 60Hz',
            '1360x768, 75Hz',
            '1400x1050, 50Hz',
            '1400x1050, 60Hz',
            '1400x1050, 75Hz',
            '1440x900, 50Hz',
            '1440x900, 60Hz',
            '1440x900, 75Hz',
            '1600x1200, 50Hz',
            '1600x1200, 60Hz',
            '1600x1200, 75Hz',
            '1680x1050, 50Hz',
            '1680x1050, 60Hz',
            '1680x1050, 75Hz',
            '1920x1080, 50Hz',
            '1920x1080, 60Hz',
            '1920x1200, 50Hz',
            '1920x1200, 60Hz']

        if value in ValueStateValues:
            tempValue = value.split(', ')
            OutputResolutionCmdString = 'cgi-bin/SetResolution.cgi?resolution={}_{}'.format(tempValue[0], tempValue[1])
            self.__SetHelper('OutputResolution', value, qualifier, url=OutputResolutionCmdString)
        else:
            self.Discard('Invalid Command for SetOutputResolution')

    def SetPreset(self, value, qualifier):

        ModeStates = {
            'Load': 'Load',
            'Save': 'Save'
        }

        if qualifier['Mode'] in ModeStates and 1 <= len(value) <= 32:
            tempValue = value.replace(' ', '%20')
            PresetCmdString = 'cgi-bin/Set{}Preset.cgi?file={}'.format(ModeStates[qualifier['Mode']], tempValue)
            self.__SetHelper('Preset', value, qualifier, url=PresetCmdString)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetVideoFadeLevel(self, value, qualifier):

        if 1 <= int(value) <= 15:
            VideoFadeLevelCmdString = 'cgi-bin/SetFader.cgi?fading_level={}'.format(value)
            self.__SetHelper('VideoFadeLevel', value, qualifier, url=VideoFadeLevelCmdString)
        else:
            self.Discard('Invalid Command for SetVideoFadeLevel')

    def SetWindowBorderWidth(self, value, qualifier):

        WindowStates = {
            'All': 'all',
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            '0 pixels': '0',
            '2 pixels': '2',
            '4 pixels': '4',
            '6 pixels': '6'
        }

        if qualifier['Window'] in WindowStates and value in ValueStateValues:
            WindowBorderWidthCmdString = 'cgi-bin/SetBorder.cgi?window={}&border_width={}'.format(WindowStates[qualifier['Window']], ValueStateValues[value])
            self.__SetHelper('WindowBorderWidth', value, qualifier, url=WindowBorderWidthCmdString)
        else:
            self.Discard('Invalid Command for SetWindowBorderWidth')

    def SetWindowColor(self, value, qualifier):

        TypeStates = {
            'Border Color': ['SetBorder', 'color'],
            'Label Background Color': ['SetOutputLabel', 'background_color']
        }

        if 1 <= int(qualifier['Window']) <= 2 and qualifier['Type'] in TypeStates and 0 <= qualifier['Red'] <= 255 and 0 <= qualifier['Green'] <= 255 and 0 <= qualifier['Blue'] <= 255:
            WindowColorCmdString = 'cgi-bin/{}.cgi?window={}&{}=[{},{},{}]'.format(TypeStates[qualifier['Type']][0], qualifier['Window'], TypeStates[qualifier['Type']][1],
                                                                                   qualifier['Red'], qualifier['Green'], qualifier['Blue'])
            self.__SetHelper('WindowColor', value, qualifier, url=WindowColorCmdString)
        else:
            self.Discard('Invalid Command for SetWindowColor')

    def SetWindowFullScreenMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if 1 <= int(qualifier['Window']) <= 2 and value in ValueStateValues:
            WindowFullScreenModeCmdString = 'cgi-bin/SetFullScreen.cgi?window={}&enable={}'.format(qualifier['Window'], ValueStateValues[value])
            self.__SetHelper('WindowFullScreenMode', value, qualifier, url=WindowFullScreenModeCmdString)
        else:
            self.Discard('Invalid Command for SetWindowFullScreenMode')

    def SetWindowLabel(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        if value in ValueStateValues:
            WindowLabelCmdString = 'cgi-bin/SetOutputLabel.cgi?enable={}'.format(ValueStateValues[value])
            self.__SetHelper('WindowLabel', value, qualifier, url=WindowLabelCmdString)
        else:
            self.Discard('Invalid Command for SetWindowLabel')

    def SetWindowLabelFontSize(self, value, qualifier):

        if 1 <= int(qualifier['Window']) <= 2 and 8 <= int(value) <= 96:
            WindowLabelFontSizeCmdString = 'cgi-bin/SetOutputLabel.cgi?window={}&fontsize={}'.format(qualifier['Window'], value)
            self.__SetHelper('WindowLabelFontSize', value, qualifier, url=WindowLabelFontSizeCmdString)
        else:
            self.Discard('Invalid Command for SetWindowLabelFontSize')

    def SetWindowLabelText(self, value, qualifier):

        if 1 <= int(qualifier['Window']) <= 2 and 1 <= len(value) <= 31:
            tempValue = value.replace(' ', '%20')
            WindowLabelTextCmdString = 'cgi-bin/SetOutputLabel.cgi?window={}&text={}'.format(qualifier['Window'], tempValue)
            self.__SetHelper('WindowLabelText', value, qualifier, url=WindowLabelTextCmdString)
        else:
            self.Discard('Invalid Command for SetWindowLabelText')

    def SetWindowLabelTextColor(self, value, qualifier):

        if 1 <= int(qualifier['Window']) <= 2 and 0 <= int(qualifier['Blending Level']) <= 7 and 0 <= qualifier['Text Color Red'] <= 255 and 0 <= qualifier['Text Color Green'] <= 255 and 0 <= qualifier['Text Color Blue'] <= 255 and 0 <= qualifier['Label Color Red'] <= 255 and 0 <= qualifier['Label Color Green'] <= 255 and 0 <= qualifier['Label Color Blue'] <= 255 and 1 <= len(value) <= 31:
            tempValue = value.replace(' ', '%20')
            WindowLabelTextColorCmdString = 'cgi-bin/SetOutputLabel.cgi?window={}&text={}&font_color=[{},{},{}]&background_color=' \
                                            '[{},{},{}]&blending_level={}'.format(qualifier['Window'], tempValue, qualifier['Text Color Red'],
                                                                                  qualifier['Text Color Green'], qualifier['Text Color Blue'],
                                                                                  qualifier['Label Color Red'], qualifier['Label Color Green'],
                                                                                  qualifier['Label Color Blue'], qualifier['Blending Level'])
            self.__SetHelper('WindowLabelTextColor', value, qualifier, url=WindowLabelTextColorCmdString)
        else:
            self.Discard('Invalid Command for SetWindowLabelTextColor')

    def SetWindowPosition(self, value, qualifier):

        if 1 <= int(qualifier['Window']) <= 2 and qualifier['Top Left X Position'] >= 0 and qualifier['Top Left Y Position'] >= 0 and qualifier['Width'] >= 0 and qualifier['Height'] >= 0:
            WindowPositionCmdString = 'cgi-bin/SetWindowPositionSize.cgi?window={}' \
                                      '&x={}&y={}&width={}&height={}'.format(qualifier['Window'],
                                                                             qualifier['Top Left X Position'],
                                                                             qualifier['Top Left Y Position'],
                                                                             qualifier['Width'], qualifier['Height'])
            self.__SetHelper('WindowPosition', value, qualifier, url=WindowPositionCmdString)
        else:
            self.Discard('Invalid Command for SetWindowPosition')

    def SetWindowPriority(self, value, qualifier):

        ValueStateValues = {
            'Source 1': '1',
            'Source 2': '2'
        }

        if value in ValueStateValues:
            WindowPriorityCmdString = 'cgi-bin/SetPriority.cgi?window={}'.format(ValueStateValues[value])
            self.__SetHelper('WindowPriority', value, qualifier, url=WindowPriorityCmdString)
        else:
            self.Discard('Invalid Command for SetWindowPriority')

    def SetWindowSwap(self, value, qualifier):

        if 1 <= int(qualifier['Window']) <= 2:
            WindowSwapCmdString = 'cgi-bin/SetSwap.cgi?window={}'.format(qualifier['Window'])
            self.__SetHelper('WindowSwap', value, qualifier, url=WindowSwapCmdString)
        else:
            self.Discard('Invalid Command for SetWindowSwap')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response.read().decode()

    def __SetHelper(self, command, value, qualifier, url='', data=None):
        self.Debug = True

        url = '{}{}'.format(self.RootURL, url)  # self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

    def __UpdateHelper(self, command, value, qualifier, url='', data=None):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        url = '{}{}'.format(self.RootURL, url)  # self.RootURL = 'http://<IP Address>:<Port>/'
        headers = {}
        my_request = urllib.request.Request(url, data=data, headers=headers)

        try:
            res = self.Opener.open(my_request, timeout=10)  # open() returns a http.client.HTTPResponse object if successful
        except urllib.error.HTTPError as err:  # includes HTTP status codes 101, 300-505
            self.Error(['{0} {1} - {2}'.format(command, err.code, err.reason)])
            res = ''
        except urllib.error.URLError as err:  # received if can't reach the server (times out)
            self.Error(['{0} {1}'.format(command, err.reason)])
            res = ''
        except Exception as err:  # includes HTTP status code 100 and any invalid status code
            res = ''
        else:
            if res.status not in (200, 202):
                self.Error(['{0} {1} - {2}'.format(command, res.status, res.msg)])
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res)
        return res

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class HTTPClass(DeviceHTTPClass):
    def __init__(self, ipAddress, port, deviceUsername=None, devicePassword=None, Model=None):
        self.ConnectionType = 'HTTP'
        DeviceHTTPClass.__init__(self, ipAddress, port)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}'.format(self.RootURL)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])