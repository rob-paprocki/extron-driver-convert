from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict


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
        self.NumberOfActiveCallsSearch = '5'
        self.NumberOfMeetingsSearch = '5'
        self.NumberOfPhonebookSearch = '5'
        self.NumberOfRecentCalls = '5'
        self.deviceUsername = 'admin'
        self.devicePassword = '00000'
        self.Dialstring = ''
        self.Models = {
            'Icon 600': self.lfsz_12_46_600,
            'Icon 800': self.lfsz_12_46_800,
            'Icon 400': self.lfsz_12_46_400,
            'Icon 450': self.lfsz_12_46_450,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveCallHangup': {'Parameters': ['Position'], 'Status': {}},
            'ActiveCallNavigation': {'Status': {}},
            'ActiveCallSearch': {'Status': {}},
            'ActiveCallSearchResults': {'Parameters': ['Position'], 'Status': {}},
            'ActiveCallUpdate': {'Status': {}},
            'AntiFlicker': {'Parameters': ['Camera'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoFocus': {'Parameters': ['Camera'], 'Status': {}},
            'Brightness': {'Parameters': ['Camera'], 'Status': {}},
            'Calendar': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraReset': {'Parameters': ['Camera'], 'Status': {}},
            'CloudMeetingNavigation': {'Status': {}},
            'CloudMeetingSearch': {'Status': {}},
            'CloudMeetingSearchResults': {'Parameters': ['Position'], 'Status': {}},
            'CloudMeetingSearchSet': {'Parameters': ['Position'], 'Status': {}},
            'CloudMeetingUpdate': {'Status': {}},
            'Dial': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'FarEndCameraPan': {'Status': {}},
            'FarEndCameraSelect': {'Parameters': ['Camera'], 'Status': {}},
            'FarEndCameraTilt': {'Status': {}},
            'FarEndCameraZoom': {'Status': {}},
            'GUIOptions': {'Status': {}},
            'Hook': {'Status': {}},
            'IRRemote': {'Status': {}},
            'IRRemoteEmulate': {'Status': {}},
            'Layout': {'Status': {}},
            'NextCamera': {'Parameters': ['Camera'], 'Status': {}},
            'Pan': {'Parameters': ['Camera'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResults': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookSearchSet': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Type'], 'Status': {}},
            'PhysicalDisplayArrangement': {'Status': {}},
            'PictureinPicture': {'Status': {}},
            'PowerManagement': {'Status': {}},
            'Presentation': {'Status': {}},
            'PresentationInput': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'Reboot': {'Status': {}},
            'RecentCallsNavigation': {'Status': {}},
            'RecentCallsResults': {'Parameters': ['Position'], 'Status': {}},
            'RecentCallsResultSet': {'Parameters': ['Position'], 'Status': {}},
            'RecentCallsSearch': {'Status': {}},
            'RecentCallsUpdate': {'Status': {}},
            'RecordingSessionType': {'Status': {}},
            'StartStopRecording': {'Status': {}},
            'Tilt': {'Parameters': ['Camera'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Parameters': ['Camera'], 'Status': {}},
        }

        self.Clish = True

        self._update_time = 25
        self._active_calls = ''
        self._cloud_meetings = ''
        self._phonebook = ''
        self._recent_calls = ''
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'get camera anti-flicker (hdmi0|dvi0|dvi1|dvi2|dvi3|Vdirect0)\r\n(auto|50hz|60hz)\r\n\r\nok,00\r\n\$'), self.__MatchAntiFlicker, None)
            self.AddMatchString(re.compile(b'get audio mute\r\n(on|off)\r\n\r\nok,00\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'get call auto-answer\r\n(off|on)\r\n\r\nok,00\r\n\$'), self.__MatchAutoAnswer, None)
            self.AddMatchString(re.compile(b'get camera autofocus (hdmi0|dvi0|dvi1|dvi2|dvi3|Vdirect0)\r\n(enable|disable)\r\n\r\nok,00\r\n\$'), self.__MatchAutoFocus, None)
            self.AddMatchString(re.compile(b'get camera brightness (hdmi0|dvi0|dvi1|dvi2|dvi3|Vdirect0)\r\n(\d+)\r\n\r\nok,00\r\n\$'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'(status call active\r\n\r\nok|\d+,\d+,(off-hook|terminating|terminated|validating|dialing|proceeding|ringing|answered|answered-consult|media-connected|incoming|error-busy|error-no-answer|error-bad-number|error-unreachable|error-max-calls-exceeded|error-comm-failure)),'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'get system do-not-disturb\r\n(enabled|disabled)\r\n\r\nok,00\r\n\$'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(re.compile(b'get remote key-events\r\n(enabled|disabled)\r\n\r\nok,00\r\n\$'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'get video arrangement\r\n(apart|adjacent|adjacent-never-blank|mirrored|single|dual|default)\r\n\r\nok,00\r\n\$'), self.__MatchPhysicalDisplayArrangement, None)
            self.AddMatchString(re.compile(b'get pip\r\n(hidden|showing)\r\n\r\nok,00\r\n\$'), self.__MatchPictureinPicture, None)
            self.AddMatchString(re.compile(b'get system asleep\r\n([01])\r\n\r\nok,00\r\n\$'), self.__MatchPowerManagement, None)
            self.AddMatchString(re.compile(b'get presentation state\r\n(local.single|tx.started|rx.started|)\r\n\r\nok,00\r\n\$'), self.__MatchPresentation, None)
            self.AddMatchString(re.compile(b'get video recording-session\r\n(camera|dual-cameras|presentation|dual-presentation)\r\n\r\nok,00\r\n\$'), self.__MatchRecordingSessionType, None)
            self.AddMatchString(re.compile(b'(-?\d+)\r\n\r\nok,00\r\n\$'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'clish\r\n\$|clish\r\n\r\nerror,09\r\n\$|clish version'), self.__MatchClish, None)
            self.AddMatchString(re.compile(b'error,(0[1-9a-f]|1[012])\r\n\$'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'login as:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)    
                  
    @property
    def NumberOfPhonebookSearch(self):
        return self.NumberOfButton

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self.NumberOfButton = int(value)
        self.phonebook = Directory('PhonebookSearchResults', self.NumberOfButton, filler='')
        self.phonebook.write_status_function = self.WriteStatus

    @property
    def NumberOfMeetingsSearch(self):
        return self.NumberOfMeetings

    @NumberOfMeetingsSearch.setter
    def NumberOfMeetingsSearch(self, value):
        self.NumberOfMeetings = int(value)
        self.cloud_meetings = Directory('CloudMeetingSearchResults', self.NumberOfMeetings, filler='')
        self.cloud_meetings.write_status_function = self.WriteStatus

    @property
    def NumberOfActiveCallsSearch(self):
        return self.NumberOfActiveCalls

    @NumberOfActiveCallsSearch.setter
    def NumberOfActiveCallsSearch(self, value):
        self.NumberOfActiveCalls = int(value)
        self.active_calls = Directory('ActiveCallSearchResults', self.NumberOfActiveCalls, filler='')
        self.active_calls.write_status_function = self.WriteStatus

    @property
    def NumberOfRecentCalls(self):
        return self._NumberOfRecentCalls        

    @NumberOfRecentCalls.setter
    def NumberOfRecentCalls(self, value):
        self._NumberOfRecentCalls = int(value)
        self.recent_calls = Directory('RecentCallsResults', self._NumberOfRecentCalls, filler='')
        self.recent_calls.write_status_function = self.WriteStatus

    def __MatchClish(self, match, qualifier):
        print('Matched')
        self.Clish = False

    def __MatchLogin(self, match, tag):
        print('Login')
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

    def SetActiveCallHangup(self, value, qualifier):

        activeCall = self.ReadStatus('ActiveCallSearchResults', qualifier)
        if activeCall and activeCall in self.ActiveCalls and 1 <= int(qualifier['Position']) <= self.NumberOfActiveCalls:
            self.__SetHelper('ActiveCallHangup', 'control call hangup {}\r'.format(self.ActiveCalls[activeCall]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetActiveCallHangup')

    def SetActiveCallNavigation(self, value, qualifier):

        if value == 'Up':
            self.active_calls.scroll_up(1)
        elif value == 'Down':
            self.active_calls.scroll_down(1)
        elif value == 'Page Up':
            self.active_calls.scroll_up(self.NumberOfActiveCalls)
        elif value == 'Page Down':
            self.active_calls.scroll_down(self.NumberOfActiveCalls)

    def SetActiveCallSearch(self, value, qualifier):

        if value and self._active_calls:
            new_list = list(filter(lambda x: value in x, self._active_calls))
            new_list.append('***End of List***')
            self.active_calls.reset(new_list)
        else:
            self.Discard('Invalid Command for SetActiveCallSearch')

    def SetActiveCallUpdate(self, value, qualifier):

        self.ActiveCalls = OrderedDict()
        self.active_calls.reset(['***Loading***'])
        res = self.SendAndWait('status call active\r', 6, deliTag='$')
        if res:
            try:
                for l in res.decode().split('\r\n')[1:-3]:
                    self.ActiveCalls[l.split(',')[6]] = l.split(',')[5]
                new_list = list(self.ActiveCalls.keys())

                self._active_calls = new_list.copy()
                new_list.append('***End of List***')
                self.active_calls.reset(new_list)
            except (ValueError, IndexError):
                self.Error(['Active Call: Invalid/unexpected respons'])
                self.active_calls.reset(['***No Active Calls***'])
        else:
            self.Error(['No Response for Active Calls'])
            self.active_calls.reset(['***No Active Calls***'])

    def SetAntiFlicker(self, value, qualifier):

        if value in ['Off', '50Hz', '60Hz'] and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('AntiFlicker', 'set camera anti-flicker {} {}\r'.format(self.setCameraValues[qualifier['Camera']], value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAntiFlicker')

    def UpdateAntiFlicker(self, value, qualifier):

        if qualifier['Camera'] in self.setCameraValues:
            self.__UpdateHelper('AntiFlicker', 'get camera anti-flicker {}\r'.format(self.setCameraValues[qualifier['Camera']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAntiFlicker')

    def __MatchAntiFlicker(self, match, tag):

        ValueStateValues = {
            'auto': 'auto',
            '50hz': '50Hz',
            '60hz': '60Hz'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AntiFlicker', value, {'Camera': self.getCameraValues[match.group(1).decode()]})

    def SetAudioMute(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('AudioMute', 'set audio mute {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'get audio mute\r', value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'Enabled': 'on',
            'Disabled': 'off'
        }

        if value in ValueStateValues:
            self.__SetHelper('AutoAnswer', 'set call auto-answer {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        self.__UpdateHelper('AutoAnswer', 'get call auto-answer\r', value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'on': 'Enabled',
            'off': 'Disabled'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Enabled': 'enable',
            'Disabled': 'disable'
        }

        if value in ValueStateValues and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('AutoFocus', 'set camera autofocus {} {}\r'.format(self.setCameraValues[qualifier['Camera']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def UpdateAutoFocus(self, value, qualifier):

        if qualifier['Camera'] in self.setCameraValues:
            self.__UpdateHelper('AutoFocus', 'get camera autofocus {}\r'.format(self.setCameraValues[qualifier['Camera']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAutoFocus')

    def __MatchAutoFocus(self, match, tag):

        ValueStateValues = {
            'enable': 'Enabled',
            'disable': 'Disabled'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AutoFocus', value, {'Camera': self.getCameraValues[match.group(1).decode()]})

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100 and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('Brightness', 'set camera brightness {} {}\r'.format(self.setCameraValues[qualifier['Camera']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        if qualifier['Camera'] in self.setCameraValues:
            self.__UpdateHelper('Brightness', 'get camera brightness {}\r'.format(self.setCameraValues[qualifier['Camera']]), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateBrightness')

    def __MatchBrightness(self, match, tag):

        self.WriteStatus('Brightness', int(match.group(2).decode()), {'Camera': self.getCameraValues[match.group(1).decode()]})

    def SetCalendar(self, value, qualifier):

        if value in ['Join', 'Reject', 'Hangup']:
            self.__SetHelper('Calendar', 'control calendar {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCalendar')

    def UpdateCallStatus(self, value, qualifier):

        self.__UpdateHelper('CallStatus', 'status call active\r', value, qualifier)

    def __MatchCallStatus(self, match, tag):

        CallStatusStateNames = {
            'off-hook': 'Off Hook',
            'terminating': 'Terminating',
            'terminated': 'Terminated',
            'validating': 'Validating',
            'dialing': 'Dialing',
            'proceeding': 'Proceeding',
            'ringing': 'Far End Ringing',
            'answered': 'Answered',
            'answered-consult': 'Answered Consult',
            'media-connected': 'Connected',
            'incoming': 'Incoming',
            'error-busy': 'Busy',
            'error-no-answer': 'No Answer',
            'error-bad-number': 'Bad Number',
            'error-unreachable': 'Unreachable',
            'error-max-calls-exceeded': 'Max Calls Exceeded',
            'error-comm-failure': 'Comm Failure'
        }

        if match.group(1).decode() == 'status call active\r\n\r\nok':
            value = 'Not In Call'
        else:
            value = CallStatusStateNames[match.group(2).decode()]
        self.WriteStatus('CallStatus', value, None)

    def SetCameraReset(self, value, qualifier):

        ValueStateValues = {
            'Pan': '-p',
            'Tilt': '-t',
            'Zoom': '-z'
        }

        if value in ValueStateValues and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('CameraReset', 'set camera position -N {} {} 0\r'.format(self.setCameraValues[qualifier['Camera']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraReset')

    def SetCloudMeetingNavigation(self, value, qualifier):

        if value == 'Up':
            self.cloud_meetings.scroll_up(1)
        elif value == 'Down':
            self.cloud_meetings.scroll_down(1)
        elif value == 'Page Up':
            self.cloud_meetings.scroll_up(self.NumberOfMeetings)
        elif value == 'Page Down':
            self.cloud_meetings.scroll_down(self.NumberOfMeetings)

    def SetCloudMeetingSearch(self, value, qualifier):

        if value and self._cloud_meetings:
            new_list = list(filter(lambda x: value in x, self._cloud_meetings))
            new_list.append('***End of List***')
            self.cloud_meetings.reset(new_list)
        else:
            self.Discard('Invalid Command for SetCloudMeetingSearch')

    def SetCloudMeetingSearchSet(self, value, qualifier):

        cloudMeeting = self.ReadStatus('CloudMeetingSearchResults', qualifier)
        if cloudMeeting and cloudMeeting in self.CloudMeetings and 1 <= int(qualifier['Position']) <= self.NumberOfMeetings:
            if self.CloudMeetings[cloudMeeting]:
                self.Dialstring = self.CloudMeetings[cloudMeeting]
        else:
            self.Discard('Invalid Command for SetCloudMeetingSearchSet')

    def SetCloudMeetingUpdate(self, value, qualifier):

        self.CloudMeetings = OrderedDict()
        self.cloud_meetings.reset(['***Loading***'])
        res = self.SendAndWait('get cloud meetings\r', 15, deliTag='$')
        if res:
            try:
                for l in res.decode().split('\r\n')[1:-3]:
                    self.CloudMeetings[l.split(',')[2].replace('"', '')] = l.split(',')[0].replace('"', '')
                new_list = list(self.CloudMeetings.keys())

                self._cloud_meetings = new_list.copy()
                new_list.append('***End of List***')
                self.cloud_meetings.reset(new_list)
            except (ValueError, IndexError):
                self.Error(['Cloud Meetings: Invalid/unexpected respons'])
                self.cloud_meetings.reset(['***No Cloud Meetings***'])
        else:
            self.Error(['No Response for Cloud Meetings'])
            self.cloud_meetings.reset(['***No Cloud Meetings***'])

    def SetDial(self, value, qualifier):

        dialString = self.Dialstring
        if dialString:
            self.__SetHelper('Dial', 'control call dial {}\r'.format(dialString), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDial')

    def SetDoNotDisturb(self, value, qualifier):

        if value in ['Enabled', 'Disabled']:
            self.__SetHelper('DoNotDisturb', 'set system do-not-disturb {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):

        self.__UpdateHelper('DoNotDisturb', 'get system do-not-disturb\r', value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            'enabled': 'Enabled',
            'disabled': 'Disabled'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789#*ABCD':
            self.__SetHelper('DTMF', 'control call dtmf {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFarEndCameraPan(self, value, qualifier):

        if value in ['Left', 'Right', 'Stop']:
            state = 'stop' if value is 'Stop' else 'pan-{}'.format(value.lower())
            self.__SetHelper('FarEndCameraPan', 'set camera far position -a {}\r'.format(state), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPan')

    def SetFarEndCameraSelect(self, value, qualifier):

        if 0 <= int(qualifier['Camera']) <= 10:
            self.__SetHelper('FarEndCameraSelect', 'set camera far-position -a change-source -N {}\r'.format(qualifier['Camera']), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSelect')

    def SetFarEndCameraTilt(self, value, qualifier):

        if value in ['Up', 'Down', 'Stop']:
            state = 'stop' if value is 'Stop' else 'tilt-{}'.format(value.lower())
            self.__SetHelper('FarEndCameraTilt', 'set camera far-position -a {}\r'.format(state), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraTilt')

    def SetFarEndCameraZoom(self, value, qualifier):

        if value in ['In', 'Out', 'Stop']:
            state = 'stop' if value is 'Stop' else 'zoom-{}'.format(value.lower())
            self.__SetHelper('FarEndCameraZoom', 'set camera far-position -a {}\r'.format(state), value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraZoom')

    def SetGUIOptions(self, value, qualifier):

        ValueStateValues = {
            'On': 'show',
            'Off': 'hide'
        }

        if value in ValueStateValues:
            self.__SetHelper('GUIOptions', 'control {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetGUIOptions')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Answer': 'answer',
            'Terminate': 'hangup',
            'Reject': 'reject'
        }

        if value in ValueStateValues:
            self.__SetHelper('Hook', 'control call {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIRRemote(self, value, qualifier):

        ValueStateValues = {
            'On': 'enabled',
            'Off': 'disabled'
        }

        if value in ValueStateValues:
            self.__SetHelper('IRRemote', 'set remote key-events {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemote')

    def UpdateIRRemote(self, value, qualifier):

        self.__UpdateHelper('IRRemote', 'get remote key-events\r', value, qualifier)

    def __MatchIRRemote(self, match, tag):

        ValueStateValues = {
            'enabled': 'On',
            'disabled': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('IRRemote', value, None)

    def SetIRRemoteEmulate(self, value, qualifier):

        ValueStateValues = {
            'Mute': 'control remote mute\r',
            'Up': 'control remote up\r',
            'Down': 'control remote down\r',
            'Left': 'control remote left\r',
            'Right': 'control remote right\r',
            'Select': 'control remote ok\r'
        }

        if value in ValueStateValues:
            self.__SetHelper('IRRemoteEmulate', ValueStateValues[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRRemoteEmulate')

    def SetLayout(self, value, qualifier):

        ValueStateValues = {
            'Next': 'control layout next\r',
            'Previous': 'control layout prev\r'
        }

        if value in ValueStateValues:
            self.__SetHelper('Layout', ValueStateValues[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayout')

    def SetNextCamera(self, value, qualifier):

        if qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('NextCamera', 'set camera active {}\r'.format(self.setCameraValues[qualifier['Camera']]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetNextCamera')

    def SetPan(self, value, qualifier):

        ValueStateValues = {
            'Left': '-l',
            'Right': '-r',
            'Stop': '-s'
        }

        if value in ValueStateValues and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('Pan', 'set camera position -N {} {}\r'.format(self.setCameraValues[qualifier['Camera']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPan')

    def SetPhonebookNavigation(self, value, qualifier):

        if value == 'Up':
            self.phonebook.scroll_up(1)
        elif value == 'Down':
            self.phonebook.scroll_down(1)
        elif value == 'Page Up':
            self.phonebook.scroll_up(self.NumberOfButton)
        elif value == 'Page Down':
            self.phonebook.scroll_down(self.NumberOfButton)

    def SetPhonebookSearch(self, value, qualifier):

        if value and self._phonebook:
            new_list = list(filter(lambda x: value in x, self._phonebook))
            new_list.append('***End of List***')
            self.phonebook.reset(new_list)
        else:
            self.Discard('Invalid Command for SetPhonebookSearch')

    def SetPhonebookSearchSet(self, value, qualifier):

        phonebook = self.ReadStatus('PhonebookSearchResults', qualifier)
        if phonebook and phonebook in self.PhoneBook and 1 <= int(qualifier['Position']) <= self.NumberOfButton:
            if self.PhoneBook[phonebook]:
                self.Dialstring = self.PhoneBook[phonebook]
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        self.PhoneBook = OrderedDict()
        self.phonebook.reset(['***Loading***'])
        if qualifier['Type'] in ['Local', 'Cloud']:
            res = self.SendAndWait('get {} directory\r'.format(qualifier['Type'].lower()), self._update_time, deliTag='$')
            if res:
                try:
                    for l in res.decode().split('\r\n')[1:-3]:
                        self.PhoneBook[l.split(',')[2].replace('"', '')] = l.split(',')[0].replace('"', '')
                    new_list = list(self.PhoneBook.keys())

                    self._phonebook = new_list.copy()
                    new_list.append('***End of List***')
                    self.phonebook.reset(new_list)
                except (ValueError, IndexError):
                    self.Error(['Phonebook: Invalid/unexpected respons'])
                    self.phonebook.reset(['***No Phonebook***'])
            else:
                self.Error(['No Response for Phonebook'])
                self.phonebook.reset(['***No Phonebook***'])
        else:
            self.Discard('Invalid Command for SetPhonebookUpdate')

    def SetPhysicalDisplayArrangement(self, value, qualifier):

        ValueStateValues = {
            'Apart': 'apart',
            'Adjacent': 'adjacent',
            'Mirrored': 'mirrored',
            'Single': 'single',
            'Default': 'default',
            'Never Blank': 'adjacent-never-blank',
            'Dual': 'dual'
        }

        if value in ValueStateValues:
            self.__SetHelper('PhysicalDisplayArrangement', 'set video arrangement {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhysicalDisplayArrangement')

    def UpdatePhysicalDisplayArrangement(self, value, qualifier):

        self.__UpdateHelper('PhysicalDisplayArrangement', 'get video arrangement\r', value, qualifier)

    def __MatchPhysicalDisplayArrangement(self, match, tag):

        ValueStateValues = {
            'apart': 'Apart',
            'adjacent': 'Adjacent',
            'mirrored': 'Mirrored',
            'single': 'Single',
            'default': 'Default',
            'adjacent-never-blank': 'Never Blank',
            'dual': 'Dual'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PhysicalDisplayArrangement', value, None)

    def SetPictureinPicture(self, value, qualifier):

        ValueStateValues = {
            'On': 'show',
            'Off': 'hide'
        }

        if value in ValueStateValues:
            self.__SetHelper('PictureinPicture', 'control pip {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureinPicture')

    def UpdatePictureinPicture(self, value, qualifier):

        self.__UpdateHelper('PictureinPicture', 'get pip\r', value, qualifier)

    def __MatchPictureinPicture(self, match, tag):

        ValueStateValues = {
            'showing': 'On',
            'hidden': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureinPicture', value, None)

    def SetPowerManagement(self, value, qualifier):

        ValueStateValues = {
            'Sleep': 'sleep',
            'Awake': 'wakeup'
        }

        if value in ValueStateValues:
            self.__SetHelper('PowerManagement', 'control {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerManagement')

    def UpdatePowerManagement(self, value, qualifier):

        self.__UpdateHelper('PowerManagement', 'get system asleep\r', value, qualifier)

    def __MatchPowerManagement(self, match, tag):

        ValueStateValues = {
            '1': 'Sleep',
            '0': 'Awake'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PowerManagement', value, None)

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        if value in ValueStateValues:
            self.__SetHelper('Presentation', 'control presentation {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):

        self.__UpdateHelper('Presentation', 'get presentation state\r', value, qualifier)

    def __MatchPresentation(self, match, tag):

        ValueStateValues = {
            'local.single': 'Local',
            'tx.started': 'Transmitting',
            'rx.started': 'Receiving',
            '': 'No Presentation'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Presentation', value, None)

    def SetPresentationInput(self, value, qualifier):

        if value in self.setCameraValues:
            self.__SetHelper('PresentationInput', 'control presentation switch {}\r'.format(self.setCameraValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationInput')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 19:
            self.__SetHelper('PresetRecall', 'set camera position -P {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 19 and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('PresetSave', 'set camera preset -N {0} -P {1}\r'.format(self.setCameraValues[qualifier['Camera']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'control reboot\r', value, qualifier)

    def SetRecentCallsNavigation(self, value, qualifier):

        if value == 'Up':
            self.recent_calls.scroll_up(1)
        elif value == 'Down':
            self.recent_calls.scroll_down(1)
        elif value == 'Page Up':
            self.recent_calls.scroll_up(self._NumberOfRecentCalls)
        elif value == 'Page Down':
            self.recent_calls.scroll_down(self._NumberOfRecentCalls)

    def SetRecentCallsResultSet(self, value, qualifier):

        recentCall = self.ReadStatus('RecentCallsResults', qualifier)
        if recentCall and recentCall in self.RecentCalls and 1 <= int(qualifier['Position']) <= self._NumberOfRecentCalls:
            if self.RecentCalls[recentCall]:
                self.Dialstring = self.RecentCalls[recentCall]
        else:
            self.Discard('Invalid Command for SetRecentCallsResultSet')

    def SetRecentCallsSearch(self, value, qualifier):

        if value and self._recent_calls:
            new_list = list(filter(lambda x: value in x, self._recent_calls))
            new_list.append('***End of List***')
            self.recent_calls.reset(new_list)
        else:
            self.Discard('Invalid Command for SetRecentCallsSearch')

    def SetRecentCallsUpdate(self, value, qualifier):

        self.RecentCalls = OrderedDict()
        self.recent_calls.reset(['***Loading***'])
        res = self.SendAndWait('get recents directory\r', 15, deliTag='$')
        if res:
            try:
                new_list = []
                for entry in res.decode().split('\r\n')[1:-3]:
                    contact, number = entry.split(',')[2].replace('"', ''), entry.split(',')[0].replace('"', '')
                    self.RecentCalls[contact] = number
                    new_list.append(contact)
                new_list.reverse()  # reference lifesize_recents_v10_4.png
                self._recent_calls = new_list.copy()
                new_list.append('***End of List***')
                self.recent_calls.reset(new_list)
            except (ValueError, IndexError):
                self.Error(['Recent Calls: Invalid/unexpected respons'])
                self.recent_calls.reset(['***No Recent Calls***'])
        else:
            self.Error(['No Response for Recent Calls'])
            self.recent_calls.reset(['***No Recent Calls***'])

    def SetRecordingSessionType(self, value, qualifier):

        ValueStateValues = {
            'Camera': 'camera',
            'Dual Cameras': 'dual-cameras',
            'Presentation': 'presentation',
            'Dual Presentation': 'dual-presentation'
        }

        if value in ValueStateValues:
            self.__SetHelper('RecordingSessionType', 'set video recording-session {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecordingSessionType')

    def UpdateRecordingSessionType(self, value, qualifier):

        self.__UpdateHelper('RecordingSessionType', 'get video recording-session\r', value, qualifier)

    def __MatchRecordingSessionType(self, match, tag):

        ValueStateValues = {
            'camera': 'Camera',
            'dual-cameras': 'Dual Cameras',
            'presentation': 'Presentation',
            'dual-presentation': 'Dual Presentation'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('RecordingSessionType', value, None)

    def SetStartStopRecording(self, value, qualifier):

        if value in ['Start', 'Stop']:
            self.__SetHelper('StartStopRecording', 'control record {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetStartStopRecording')

    def SetTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': '-u',
            'Down': '-d',
            'Stop': '-s'
        }

        if value in ValueStateValues and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('Tilt', 'set camera position -N {} {}\r'.format(self.setCameraValues[qualifier['Camera']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTilt')

    def SetVideoMute(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('VideoMute', 'set video mute {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'set volume speaker {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'get volume speaker\r', value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': '-n',
            'Wide': '-f',
            'Stop': '-s'
        }

        if value in ValueStateValues and qualifier['Camera'] in self.setCameraValues:
            self.__SetHelper('Zoom', 'set camera position -N {0} {1}\r'.format(self.setCameraValues[qualifier['Camera']], ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Clish:
            @Wait(1)
            def SendClish():
                self.Send(b'clish\r')
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

            if self.Clish:
                @Wait(1)
                def SendClish():
                    self.Send(b'clish\r')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        ERROR_CODES = {
            '01': 'No Memory',
            '02': 'File Error',
            '03': 'Invalid Instance',
            '04': 'Invalid Parameter',
            '05': 'Argument is not repeatable',
            '06': 'Invalid Selection Parameter Value',
            '07': 'Missing Argument',
            '08': 'Extra Arguments on Command Line',
            '09': 'Invalid Command',
            '0a': 'Amiguous Command',
            '0b': 'Conflicting Parameter',
            '0c': 'Operational Error',
            '0d': 'No Data Available',
            '0e': 'Not In Call',
            '0f': 'Interrupted',
            '10': 'Ambiguious Selection',
            '11': 'No Matching Entries',
            '12': 'Not Supported'
        }

        self.Error(['Error: {}.'.format(ERROR_CODES[match.group(1).decode()])])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' not in self.ConnectionType:
            self._update_time = 15
        else:
            self._update_time = 25

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Clish = True

        self._active_calls = ''
        self._cloud_meetings = ''
        self._phonebook = ''
        self._recent_calls = ''

    def lfsz_12_46_600(self):

        self.setCameraValues = {
            'HDMI': 'hdmi0',
            'DVI': 'dvi0'
        }

        self.getCameraValues = {
            'hdmi0': 'HDMI',
            'dvi0': 'DVI'
        }

    def lfsz_12_46_800(self):

        self.setCameraValues = {
            'HDMI': 'hdmi0',
            'DVI 1': 'dvi0',
            'DVI 2': 'dvi1',
            'DVI 3': 'dvi2',
            'DVI 4': 'dvi3'
        }

        self.getCameraValues = {
            'hdmi0': 'HDMI',
            'dvi0': 'DVI 1',
            'dvi1': 'DVI 2',
            'dvi2': 'DVI 3',
            'dvi3': 'DVI 4'
        }

    def lfsz_12_46_400(self):

        self.setCameraValues = {
            'HDMI': 'hdmi0'
        }

        self.getCameraValues = {
            'hdmi0': 'HDMI'
        }

    def lfsz_12_46_450(self):

        self.setCameraValues = {
            'HDMI': 'Vdirect0'
        }

        self.getCameraValues = {
            'Vdirect0': 'HDMI'
        }

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

    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        return result
        
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

    def __init__(self, write_function_name, display_count, filler=None):
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
            if self._qualifier_type == 'Number':
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
            self._start_index = len(self.entry_list) - 1  
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1