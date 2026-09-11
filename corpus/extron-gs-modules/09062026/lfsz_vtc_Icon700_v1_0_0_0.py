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
        self.devicePassword = '0000'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveCallDuration': {'Status': {}},
            'ActiveCallName': {'Status': {}},
            'ActiveMic': {'Status': {}},
            'ActiveSpeaker': {'Status': {}},
            'AntiFlicker': {'Parameters': ['Camera'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoFocus': {'Parameters': ['Camera'], 'Status': {}},
            'Brightness': {'Parameters': ['Camera'], 'Status': {}},
            'CallStatus': {'Status': {}},
            'CloudDirectoryNavigation': {'Status': {}},
            'CloudDirectoryResults': {'Parameters': ['Position'], 'Status': {}},
            'CloudDirectoryResultSet': {'Parameters': ['Position', 'Media', 'Protocol'], 'Status': {}},
            'CloudDirectoryUpdate': {'Status': {}},
            'CloudMeetingsNavigation': {'Status': {}},
            'CloudMeetingsResults': {'Parameters': ['Position'], 'Status': {}},
            'CloudMeetingsResultSet': {'Parameters': ['Position', 'Media', 'Protocol'], 'Status': {}},
            'CloudMeetingsUpdate': {'Status': {}},
            'CurrentDisplayContent': {'Status': {}},
            'DefaultContent': {'Status': {}},
            'Dial': {'Parameters': ['Media', 'Protocol', 'Number'], 'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'LayoutStart': {'Parameters': ['Content'], 'Status': {}},
            'LayoutStatus': {'Parameters': ['Content'], 'Status': {}},
            'LayoutStop': {'Parameters': ['Content'], 'Status': {}},
            'LocalView': {'Status': {}},
            'LocalViewStatus': {'Status': {}},
            'PanTilt': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'PictureinPicture': {'Status': {}},
            'PowerManagement': {'Status': {}},
            'Presentation': {'Status': {}},
            'PresentationAutostart': {'Status': {}},
            'PresentationStatus': {'Status': {}},
            'PresetRecall': {'Parameters': ['Camera'], 'Status': {}},
            'PresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'PrimaryVideoInput': {'Status': {}},
            'Reboot': {'Status': {}},
            'RecentCallsNavigation': {'Status': {}},
            'RecentCallsResults': {'Parameters': ['Position'], 'Status': {}},
            'RecentCallsUpdate': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
        }
        
        self._lastTag = 'No Call'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'status call active\r\n(.*)[\r\n]+Success, 0\r\n\$'), self.__MatchActiveCallDuration, None)
            self.AddMatchString(re.compile(b'get audio active-mic\r\n(phone|hdmi|linein|usb)\r\nSuccess, 0\r\n\$'), self.__MatchActiveMic, None)
            self.AddMatchString(re.compile(b'get audio audio-output\r\n(phone|hdmi|lineout|usb)\r\nSuccess, 0\r\n\$'), self.__MatchActiveSpeaker, None)
            self.AddMatchString(re.compile(b'get camera anti-flicker Gems-(Camera|HDMI)\r\n([0-2])\r\nSuccess, 0\r\n\$'), self.__MatchAntiFlicker, None)
            self.AddMatchString(re.compile(b'get audio mute\r\n(unmuted|muted)\r\nSuccess, 0\r\n\$'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'get call auto-answer\r\n(on|off)\r\nSuccess, 0\r\n\$'), self.__MatchAutoAnswer, None)
            self.AddMatchString(re.compile(b'get camera autofocus Gems-(Camera|HDMI)\r\n([01])\r\nSuccess, 0\r\n\$'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'get camera brightness Gems-(Camera|HDMI)\r\n(\d+)\r\nSuccess, 0\r\n\$'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'status call active\r\nUsage: status call active\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'get layout current\r\n(camera|slide)\r\nSuccess, 0\r\n\$'), self.__MatchCurrentDisplayContent, None)
            self.AddMatchString(re.compile(b'get layout default-content\r\n(camera|slide)\r\nSuccess, 0\r\n\$'), self.__MatchDefaultContent, None)
            self.AddMatchString(re.compile(b'get system do-not-disturb\r\n(enabled|disabled)\r\nSuccess, 0\r\n\$'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(re.compile(b'get layout (camera|presentation)-playing\r\n(not presenting|not playing|presenting|playing)\r\nSuccess, 0\r\n\$'), self.__MatchLayoutStatus, None)
            self.AddMatchString(re.compile(b'get local-view state\r\n(camera|slide)\r\nSuccess, 0\r\n\$'), self.__MatchLocalViewStatus, None)
            self.AddMatchString(re.compile(b'get pip\r\n(enabled|disabled)\r\nSuccess, 0\r\n\$'), self.__MatchPictureinPicture, None)
            self.AddMatchString(re.compile(b'get system asleep\r\n(asleep|awake)\r\nSuccess, 0\r\n\$'), self.__MatchPowerManagement, None)
            self.AddMatchString(re.compile(b'get layout presentation-autostart\r\n(true|false)\r\nSuccess, 0\r\n\$'), self.__MatchPresentationAutostart, None)
            self.AddMatchString(re.compile(b'get presentation state\r\n(not presenting|presenting)\r\nSuccess, 0\r\n\$'), self.__MatchPresentationStatus, None)
            self.AddMatchString(re.compile(b'get camera primary_input\r\nGems-(Camera|HDMI)\r\nSuccess, 0\r\n\$'), self.__MatchPrimaryVideoInput, None)
            self.AddMatchString(re.compile(b'get volume speaker\r\n(\d+)\r\nSuccess, 0\r\n\$'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'(No\s?Memory|IO\s?Error|Invalid\s?Instance|Invalid\s?Parameter|Repeated|Not\s?In\s?List|Missing|Too\s?Many|Invalid\s?Command|Ambiguous\s?Command|Parameter\s?Conflict|Operational\s?Error|No\s?Data|Not\s?In\s?Call|Interrupted|Ambiguous|No\s?Match|Not\s?Supported|Quit),'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login as:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'control call dial (.*) -t (video|voice) -p (auto|sip)'), self.__MatchCallState, 'Outgoing')
            self.AddMatchString(re.compile(b'EVENT incomingCallStateChanged'), self.__MatchCallState, 'Incoming')

        self.NumberofCloudMeetingsResults = 5
        self.NumberofCloudDirectoryResults = 5
        self.NumberofRecentCallsResults = 5

        self.directory_regex = re.compile('(.*)\r\n')

    @property
    def NumberofRecentCallsResults(self):
        return self._NumberofRecentCallsResults

    @NumberofRecentCallsResults.setter
    def NumberofRecentCallsResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofRecentCallsResults = int(value)
            self.recent_calls = Directory(self._NumberofRecentCallsResults, 'RecentCallsResults', filler='')
            self.recent_calls.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of Recent Calls should be a value between 1 to 10.'])

    @property
    def NumberofCloudDirectoryResults(self):
        return self._NumberofCloudDirectoryResults

    @NumberofCloudDirectoryResults.setter
    def NumberofCloudDirectoryResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofCloudDirectoryResults = int(value)
            self.cloud_directory = Directory(self._NumberofCloudDirectoryResults, 'CloudDirectoryResults', filler='')
            self.cloud_directory.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of Cloud Directory should be a value between 1 to 10.'])

    @property
    def NumberofCloudMeetingsResults(self):
        return self._NumberofCloudMeetingsResults

    @NumberofCloudMeetingsResults.setter
    def NumberofCloudMeetingsResults(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofCloudMeetingsResults = int(value)
            self.cloud_meetings = Directory(self._NumberofCloudMeetingsResults, 'CloudMeetingsResults', filler='')
            self.cloud_meetings.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of Cloud Meetings should be a value between 1 to 10.'])

    def __MatchLogin(self, match, tag):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r')

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def UpdateActiveCallDuration(self, value, qualifier):
        self.UpdateCallStatus(None, None)

    def __MatchActiveCallDuration(self, match, tag):

        value = match.group(1).decode().split(',')
        self.WriteStatus('ActiveCallName', value[6], None)
        self.WriteStatus('ActiveCallDuration', value[10], None)
        self._lastTag = 'Connected'
        self.WriteStatus('CallStatus', 'Connected', None)

    def UpdateActiveCallName(self, value, qualifier):

        self.UpdateCallStatus(None, None)

    def SetActiveMic(self, value, qualifier):

        ValueStateValues = {
            'Phone': 'phone',
            'HDMI': 'hdmi',
            'Line In': 'linein',
            'USB': 'usb'
        }

        ActiveMicCmdString = 'set audio active-mic {}\r'.format(ValueStateValues[value])
        self.__SetHelper('ActiveMic', ActiveMicCmdString, value, qualifier)

    def UpdateActiveMic(self, value, qualifier):
        self.__UpdateHelper('ActiveMic', 'get audio active-mic\r', value, qualifier)

    def __MatchActiveMic(self, match, tag):

        ValueStateValues = {
            'phone': 'Phone',
            'hdmi': 'HDMI',
            'linein': 'Line In',
            'usb': 'USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ActiveMic', value, None)

    def SetActiveSpeaker(self, value, qualifier):

        ValueStateValues = {
            'Phone': 'phone',
            'HDMI': 'hdmi',
            'Line Out': 'lineout',
            'USB': 'usb'
        }

        ActiveSpeakerCmdString = 'set audio audio-output {}\r'.format(ValueStateValues[value])
        self.__SetHelper('ActiveSpeaker', ActiveSpeakerCmdString, value, qualifier)

    def UpdateActiveSpeaker(self, value, qualifier):

        self.__UpdateHelper('ActiveSpeaker', 'get audio audio-output\r', value, qualifier)

    def __MatchActiveSpeaker(self, match, tag):

        ValueStateValues = {
            'phone': 'Phone',
            'hdmi': 'HDMI',
            'lineout': 'Line Out',
            'usb': 'USB'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ActiveSpeaker', value, None)

    def SetAntiFlicker(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        ValueStateValues = {
            'Off': '0',
            '50Hz': '1',
            '60Hz': '2'
        }

        AntiFlickerCmdString = 'set camera anti-flicker {} {}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('AntiFlicker', AntiFlickerCmdString, value, qualifier)

    def UpdateAntiFlicker(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        self.__UpdateHelper('AntiFlicker', 'get camera anti-flicker {}\r'.format(CameraStates[qualifier['Camera']]), value, qualifier)

    def __MatchAntiFlicker(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': '50Hz',
            '2': '60Hz'
        }

        qualifier = {'Camera': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AntiFlicker', value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AudioMuteCmdString = 'set audio mute {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'get audio mute\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'muted': 'On',
            'unmuted': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        AutoAnswerCmdString = 'set call auto-answer {}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        self.__UpdateHelper('AutoAnswer', 'get call auto-answer\r', value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetAutoFocus(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AutoFocusCmdString = 'set camera autofocus {} {}\r'.format(CameraStates[qualifier['Camera']], ValueStateValues[value])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        self.__UpdateHelper('AutoFocus', 'get camera autofocus {}\r'.format(CameraStates[qualifier['Camera']]), value, qualifier)

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Camera': match.group(1).decode()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutoFocus', value, qualifier)

    def SetBrightness(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        if 0 <= value <= 100:
            BrightnessCmdString = 'set camera brightness {} {}\r'.format(CameraStates[qualifier['Camera']], value)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        self.__UpdateHelper('Brightness', 'get camera brightness {}\r'.format(CameraStates[qualifier['Camera']]), value, qualifier)

    def __MatchBrightness(self, match, tag):

        qualifier = {'Camera': match.group(1).decode()}
        value = int(match.group(2).decode())
        self.WriteStatus('Brightness', value, qualifier)

    def UpdateCallStatus(self, value, qualifier):

        self.__UpdateHelper('CallStatus', 'status call active\r', value, qualifier)

    def __MatchCallStatus(self, match, tag):

        if self._lastTag != 'Incoming':
            self._lastTag = 'No Call'
            self.WriteStatus('CallStatus', 'Not In Call', None)
            self.WriteStatus('ActiveCallName', 'No Active Call', None)
            self.WriteStatus('ActiveCallDuration', 'No Active Call', None)

    def __MatchCallState(self, match, tag):

        if self._lastTag != tag:
            self._lastTag = tag
            self.WriteStatus('CallStatus', tag, None)

    def SetCloudDirectoryNavigation(self, value, qualifier):

        if value == 'Up':
            self.cloud_directory.scroll_up(1)
        elif value == 'Down':
            self.cloud_directory.scroll_down(1)
        elif value == 'Page Up':
            self.cloud_directory.scroll_up(self._NumberofCloudDirectoryResults)
        elif value == 'Page Down':
            self.cloud_directory.scroll_down(self._NumberofCloudDirectoryResults)
        else:
            self.Discard('Invalid Command for SetCloudDirectoryNavigation')

    def SetCloudDirectoryResultSet(self, value, qualifier):

        position = int(qualifier['Position'])
        media = qualifier['Media']
        protocol = qualifier['Protocol']
        if 1 <= position <= 10 and media and protocol:
            result = self.cloud_directory.get_entry(position)
            if '@' in result:
                value = result.split(':')[1].split('@')[0][1:]
                qualifier['Number'] = value
                self.SetDial(None, qualifier)
            else:
                self.Discard('Invalid Command for SetCloudDirectoryResultSet')
        else:
            self.Discard('Invalid Command for SetCloudDirectoryResultSet')

    def SetCloudDirectoryUpdate(self, value, qualifier):

        res = self.SendAndWait('get cloud directory\r', 15, deliTag=b'$')
        if res:
            new_list = []
            for index in re.findall(self.directory_regex, res.decode())[1:-1]:
                temp = index.split(',')
                new_list.append('{} : {}'.format(temp[2], temp[0]).replace('"', ''))
            new_list.append('*** End of Cloud Directory ***')
            self.cloud_directory.reset(new_list)
        else:
            self.Error(['No Results for Cloud Directory'])

    def SetCloudMeetingsNavigation(self, value, qualifier):

        if value == 'Up':
            self.cloud_meetings.scroll_up(1)
        elif value == 'Down':
            self.cloud_meetings.scroll_down(1)
        elif value == 'Page Up':
            self.cloud_meetings.scroll_up(self._NumberofCloudMeetingsResults)
        elif value == 'Page Down':
            self.cloud_meetings.scroll_down(self._NumberofCloudMeetingsResults)
        else:
            self.Discard('Invalid Command for SetCloudMeetingsNavigation')

    def SetCloudMeetingsResultSet(self, value, qualifier):

        position = int(qualifier['Position'])
        media = qualifier['Media']
        protocol = qualifier['Protocol']
        if 1 <= position <= 10 and media and protocol:
            result = self.cloud_meetings.get_entry(position)
            if '@' in result:
                value = result.split(':')[1].split('@')[0][1:]
                qualifier['Number'] = value
                self.SetDial(None, qualifier)
            else:
                self.Discard('Invalid Command for SetCloudMeetingsResultSet')
        else:
            self.Discard('Invalid Command for SetCloudMeetingsResultSet')

    def SetCloudMeetingsUpdate(self, value, qualifier):

        res = self.SendAndWait('get cloud meetings\r', 15, deliTag=b'$')
        if res:
            new_list = []
            for index in re.findall(self.directory_regex, res.decode())[1:-1]:
                temp = index.split(',')
                new_list.append('{} : {}'.format(temp[2], temp[0]).replace('"', ''))
            new_list.append('*** End of Cloud Meetings ***')
            self.cloud_meetings.reset(new_list)
        else:
            self.Error(['No Results for Cloud Meetings'])

    def UpdateCurrentDisplayContent(self, value, qualifier):

        self.__UpdateHelper('CurrentDisplayContent', 'get layout current\r', value, qualifier)

    def __MatchCurrentDisplayContent(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('CurrentDisplayContent', value, None)

    def SetDefaultContent(self, value, qualifier):

        ValueStateValues = {
            'Slide': 'slide',
            'Camera': 'camera'
        }

        DefaultContentCmdString = 'set layout default-content {}\r'.format(ValueStateValues[value])
        self.__SetHelper('DefaultContent', DefaultContentCmdString, value, qualifier)

    def UpdateDefaultContent(self, value, qualifier):

        self.__UpdateHelper('DefaultContent', 'get layout default-content\r', value, qualifier)

    def __MatchDefaultContent(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DefaultContent', value, None)

    def SetDial(self, value, qualifier):

        dial_string = qualifier['Number']
        media, protocol = qualifier['Media'], qualifier['Protocol']
        if dial_string and media in ['Video', 'Voice'] and protocol in ['Auto', 'Sip']:
            DialCmdString = 'control call dial {} -t {} -p {}\r'.format(dial_string, media.lower(), protocol.lower())
            self.__SetHelper('Dial', DialCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDial')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'true',
            'Disable': 'false'
        }

        DoNotDisturbCmdString = 'set system do-not-disturb {}\r'.format(ValueStateValues[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        self.__UpdateHelper('DoNotDisturb', 'get system do-not-disturb\r', value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            'enabled': 'Enable',
            'disabled': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789#*ABCD':
            self.__SetHelper('DTMF', 'control call dtmf "{}"\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Answer': 'answer',
            'Hangup': 'hangup',
            'Reject': 'reject',
            'Cancel': 'cancel',
            'Migrate': 'migrate'
        }

        HookCmdString = 'control call {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetLayoutStart(self, value, qualifier):

        ContentStates = {
            'Presenting': 'presenting',
            'Receiving': 'receiving'
        }

        ValueStateValues = {
            'Reverse': 'reverseL',
            'Full Screen': 'fullscreen',
            'Not Visible': 'notVisible'
        }

        LayoutStartCmdString = 'control layout start-presentation {} {}\r'.format(ContentStates[qualifier['Content']], ValueStateValues[value])
        self.__SetHelper('LayoutStart', LayoutStartCmdString, value, qualifier)

    def UpdateLayoutStatus(self, value, qualifier):

        self.__UpdateHelper('LayoutStatus', 'get layout {}-playing\r'.format(qualifier['Content'].lower()), value, qualifier)

    def __MatchLayoutStatus(self, match, tag):

        ValueStateValues = {
            'playing': 'Playing',
            'not playing': 'Not Playing',
            'presenting': 'Playing',
            'not presenting': 'Not Playing'
        }

        qualifier = {'Content': match.group(1).decode().title()}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LayoutStatus', value, qualifier)

    def SetLayoutStop(self, value, qualifier):

        ContentStates = {
            'Presenting': 'presenting',
            'Receiving': 'receiving'
        }

        LayoutStopCmdString = 'control layout stop-presentation {}\r'.format(ContentStates[qualifier['Content']])
        self.__SetHelper('LayoutStop', LayoutStopCmdString, value, qualifier)

    def SetLocalView(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        LocalViewCmdString = 'control local-view {}\r'.format(ValueStateValues[value])
        self.__SetHelper('LocalView', LocalViewCmdString, value, qualifier)

    def UpdateLocalViewStatus(self, value, qualifier):

        self.__UpdateHelper('LocalViewStatus', 'get local-view state\r', value, qualifier)

    def __MatchLocalViewStatus(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('LocalViewStatus', value, None)

    def SetPanTilt(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        states = {
            'Up': 'tilt-nudge {} ',
            'Down': 'tilt-nudge {} -',
            'Left': 'pan-nudge {} -',
            'Right': 'pan-nudge {} '
        }

        speed = qualifier['Speed']
        if 1 <= int(speed) <= 100:
            PanCmdString = 'control camera {}{}\r'.format(states[value].format(CameraStates[qualifier['Camera']]), speed)
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPictureinPicture(self, value, qualifier):

        ValueStateValues = {
            'On': 'show',
            'Off': 'hide'
        }

        PictureinPictureCmdString = 'control pip {}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureinPicture', PictureinPictureCmdString, value, qualifier)

    def UpdatePictureinPicture(self, value, qualifier):

        self.__UpdateHelper('PictureinPicture', 'get pip\r', value, qualifier)

    def __MatchPictureinPicture(self, match, tag):

        ValueStateValues = {
            'enabled': 'On',
            'disabled': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureinPicture', value, None)

    def SetPowerManagement(self, value, qualifier):

        ValueStateValues = {
            'Sleep': 'sleep',
            'Awake': 'wakeup'
        }

        PowerManagementCmdString = 'control {}\r'.format(ValueStateValues[value])
        self.__SetHelper('PowerManagement', PowerManagementCmdString, value, qualifier)

    def UpdatePowerManagement(self, value, qualifier):

        self.__UpdateHelper('PowerManagement', 'get system asleep\r', value, qualifier)

    def __MatchPowerManagement(self, match, tag):

        ValueStateValues = {
            'asleep': 'Sleep',
            'awake': 'Awake'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerManagement', value, None)

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        PresentationCmdString = 'control presentation {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Presentation', PresentationCmdString, value, qualifier)

    def SetPresentationAutostart(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'true',
            'Disable': 'false'
        }

        PresentationAutostartCmdString = 'set layout presentation-autostart {}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresentationAutostart', PresentationAutostartCmdString, value, qualifier)

    def UpdatePresentationAutostart(self, value, qualifier):

        self.__UpdateHelper('PresentationAutostart', 'get layout presentation-autostart\r', value, qualifier)

    def __MatchPresentationAutostart(self, match, tag):

        ValueStateValues = {
            'true': 'Enable',
            'false': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationAutostart', value, None)

    def UpdatePresentationStatus(self, value, qualifier):

        self.__UpdateHelper('PresentationStatus', 'get presentation state\r', value, qualifier)

    def __MatchPresentationStatus(self, match, tag):

        ValueStateValues = {
            'not presenting': 'Not Presenting',
            'presenting': 'Presenting'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationStatus', value, None)

    def SetPresetRecall(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        if 0 <= int(value) <= 9:
            PresetRecallCmdString = 'get camera preset {} {}\r'.format(CameraStates[qualifier['Camera']], value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        if 0 <= int(value) <= 9:
            PresetSaveCmdString = 'set camera preset {} {}\r'.format(CameraStates[qualifier['Camera']], value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def UpdatePrimaryVideoInput(self, value, qualifier):

        self.__UpdateHelper('PrimaryVideoInput', 'get camera primary_input\r', value, qualifier)

    def __MatchPrimaryVideoInput(self, match, tag):

        self.WriteStatus('PrimaryVideoInput', match.group(1).decode(), None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'control reboot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetRecentCallsNavigation(self, value, qualifier):

        if value == 'Up':
            self.recent_calls.scroll_up(1)
        elif value == 'Down':
            self.recent_calls.scroll_down(1)
        elif value == 'Page Up':
            self.recent_calls.scroll_up(self.NumberofRecentCallsResults)
        elif value == 'Page Down':
            self.recent_calls.scroll_down(self.NumberofRecentCallsResults)
        else:
            self.Discard('Invalid Command for SetRecentCallsNavigation')

    def SetRecentCallsUpdate(self, value, qualifier):

        res = self.SendAndWait('get recents directory\r', 15, deliTag=b'$')
        if res:
            new_list, directory = [], re.findall(self.directory_regex, res.decode())[1:-2]
            if len(directory) > 0:
                for index in directory:
                    temp = index.split(',')
                    new_list.append(temp[2].replace('"', ''))
            new_list.append('*** End of Recent Calls ***')
            self.recent_calls.reset(new_list)
        else:
            self.Error(['No Results for Recent Calls'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = 'set volume speaker {}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'get volume speaker\r', value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        CameraStates = {
            'HDMI': 'Gems-HDMI',
            'Camera': 'Gems-Camera'
        }

        states = {
            'In': ' ',
            'Out': ' -',
        }

        speed = qualifier['Speed']
        if 1 <= int(speed) <= 100:
            ZoomCmdString = 'control camera zoom-nudge {}{}{}\r'.format(CameraStates[qualifier['Camera']], states[value], speed)
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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

    def __MatchError(self, match, tag):
        self.counter = 0
        self.Error([match.group(1).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self._lastTag = 'No Call'

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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


class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=('admin', '0000'), Model=None):
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


def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_module()
        return res

    return wrapper


class Directory:

    def __init__(self, display_count, write_function_name, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
        self._write_function_name = write_function_name

        self.entry_list = []

        self._start_index = 0
        self.auto_update = True
        self.filler = filler
        self.entry_function = lambda entry: entry

    @property
    def display_count(self):
        return self._display_count

    @property
    def qualifier_type(self):
        return self._qualifier_type

    @qualifier_type.setter
    def qualifier_type(self, value):
        if value in ('Enum', 'Number'):
            self._qualifier_type = value

    def write_to_module(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Enum':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self._write_function_name, self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, value, qualifier, context):
        pass

    @UseAutoUpdate
    def add_entry(self, entry):
        if isinstance(entry, list):
            self.entry_list.extend(entry)
        else:
            self.entry_list.append(entry)

    @UseAutoUpdate
    def reset(self, newEntries=None):
        if isinstance(newEntries, list):
            self.entry_list.clear()
            self.entry_list.extend(newEntries)
        else:
            self.entry_list.clear()
        self._start_index = 0

    @UseAutoUpdate
    def remove_entry(self, display_position):
        if self.__display_position_check(display_position):
            try:
                return self.entry_list.pop(self._start_index + display_position - 1)
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_entry(self, display_position):

        if self.__display_position_check(display_position):
            try:
                return self.entry_list[self._start_index + display_position - 1]
            except IndexError:
                return self.filler
        else:
            return self.filler

    def get_displayed_entries(self):

        index = self._start_index
        while index <= self._start_index + self._display_count - 1:
            if index >= len(self.entry_list):
                yield self.filler, index + 1
            else:
                yield self.entry_list[index], index + 1
            index += 1

    def __display_position_check(self, position):

        return 0 < position <= self._display_count

    @UseAutoUpdate
    def scroll_up(self, step=1):
        if self._start_index - step >= 0:
            self._start_index -= step
        else:
            self._start_index = 0

    @UseAutoUpdate
    def scroll_down(self, step=1):
        if self._start_index + step < len(self.entry_list):
            self._start_index += step
        else:
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1
