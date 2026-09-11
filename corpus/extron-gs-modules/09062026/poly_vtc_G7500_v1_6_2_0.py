from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from datetime import datetime, timedelta
from collections import defaultdict

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
        self.devicePassword = ''
        self._MeetingsTimeFormat = '%I:%M%p'
        self._MeetingsTimeInterval = 0
        self._NumberofContentResults = 5
        self._NumberofPhonebookResults = 5
        self._NumberofCallHistoryResults = 5
        self._NumberofMeetingResults = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CalendarStatus': {'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryResults': {'Parameters': ['Call'], 'Status': {}},
            'CallHistoryResultSet': {'Parameters': ['Call'], 'Status': {}},
            'CallHistoryUpdate': {'Status': {}},
            'CallInfoCallerID': {'Status': {}},
            'CallInfoName': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoNumber': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoState': {'Parameters': ['Call'], 'Status': {}},
            'CameraNearInvert': { 'Status': {}},
            'CameraNearTracking': {'Status': {}},
            'CameraNearTrackingMode': {'Status': {}},
            'CameraPTZ': {'Parameters': ['Mode'], 'Status': {}},
            'CameraSource': {'Parameters': ['Mode'], 'Status': {}},
            'ConfigDisplay1': {'Status': {}},
            'ConfigDisplay2': {'Status': {}},
            'ConfigPresentationContent': {'Status': {}},
            'ConfigPresentationSelfView': {'Status': {}},
            'ContentAuto': {'Status': {}},
            'ContentNavigation': { 'Status': {}},
            'ContentResults': {'Parameters':['Content'], 'Status': {}},
            'ContentResultSet': {'Parameters':['Content'], 'Status': {}},
            'ContentUpdate': { 'Status': {}},
            'DialString' : {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'Keypad': {'Status': {}},
            'LANPort': {'Status': {}},
            'MeetingEnd': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingListQuery': {'Status': {}},
            'MeetingLocation': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingNavigation': {'Status': {}},
            'MeetingNumber': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingNumberSet': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingOrganizer': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingRefresh': {'Status': {}},
            'MeetingStart': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingSubject': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingTimeCombined': {'Parameters': ['Meeting'], 'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MuteFarStatus': {'Status': {}},
            'PhonebookGroupNavigation': {'Status': {}},
            'PhonebookGroupResults': {'Parameters': ['Group'], 'Status': {}},
            'PhonebookGroupResultSet': {'Parameters': ['Group'], 'Status': {}},
            'PhonebookGroupSearch': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookResults': {'Parameters': ['Entry'], 'Status': {}},
            'PhonebookResultSet': {'Parameters': ['Entry', 'Type'], 'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PresentationStatus': {'Parameters': ['Site'], 'Status': {}},
            'PresetFar': {'Parameters': ['Mode'], 'Status': {}},
            'PresetNear': {'Parameters': ['Mode'], 'Status': {}},
            'ProviderLock': {'Status': {}},
            'ProviderMode': {'Status': {}},
            'Reboot': {'Status': {}},
            'Selfview': {'Status': {}},
            'SleepMode': {'Status': {}},
            'SleepTime': {'Status': {}},
            'TransmitLevel': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'Version': {'Status': {}},
            'VideoContentSource': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            if self.ConnectionType == 'Serial':
                self.AddMatchString(re.compile(b'User:'), self.__MatchUsername, None)
                self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(re.compile(b'Hi, my name is'), self.__MatchSuccess, None)
                self.AddMatchString(re.compile(b'-- login failed, retry --'), self.__MatchFail, None)

            self.AddMatchString(re.compile(b'autoanswer (yes|no|donotdisturb)\r'), self.__MatchAutoAnswer, None)
            self.AddMatchString(re.compile(b'calendarstatus (established|unavailable)\r'), self.__MatchCalendarStatus, None)
            self.AddMatchString(re.compile(b'system is not in a call\r'), self.__MatchCallInfoAll, 'Inactive')
            self.AddMatchString(re.compile(b'callinfo begin\s*(?:callinfo:.*?:.*?:.*?:.*?:.*?:.*?:.*?:.*?\s*)*callinfo end\r'), self.__MatchCallInfoAll, 'Active')
            self.AddMatchString(re.compile(b'(notify callstatus success|notify linestatus success|already active:callstatus|already active:linestatus)\r'), self.__MatchCallInfoUnsolicited, None)
            self.AddMatchString(re.compile(b'notification:callstatus:(?:incoming|outgoing):(?P<callid>\d+):(?P<name>.*?):(?P<number>.*?):(?P<state>opened|ringing|connecting|connected|disconnecting|disconnected):\d+:\d+:.*?\r'), self.__MatchCallInfoUnsolicited, None)
            self.AddMatchString(re.compile(b'notification:linestatus:(?:incoming|outgoing):(?P<number>.*?):(?P<callid>\d+):\d+:\d+:(?P<state>inactive)\r'), self.__MatchCallInfoUnsolicited, None)
            self.AddMatchString(re.compile(b'camerainvert near (on|off)\r', re.I), self.__MatchCameraNearInvert, None)
            self.AddMatchString(re.compile(b'camera near tracking (on|off)\r', re.I), self.__MatchCameraNearTracking, None)
            self.AddMatchString(re.compile(b'cameratracking near mode (off|speaker|group|groupwithtransition)\r'), self.__MatchCameraNearTrackingMode, None)
            self.AddMatchString(re.compile(b'camera (near|far) source (-1|[1-4])\r'), self.__MatchCameraSource, None)
            self.AddMatchString(re.compile(b'configdisplay monitor1 (auto|1920x1080p 50Hz|1920x1080p 60Hz|3840x2160p 25Hz|3840x2160p 30Hz|3840x2160p 50Hz|3840x2160p 60Hz)\r'), self.__MatchConfigDisplay1, None)
            self.AddMatchString(re.compile(b'configdisplay monitor2 (off|auto|1920x1080p 50Hz|1920x1080p 60Hz)\r'), self.__MatchConfigDisplay2, None)
            self.AddMatchString(re.compile(b'configpresentation content (Single|Dual)\r'), self.__MatchConfigPresentationContent, None)
            self.AddMatchString(re.compile(b'configpresentation self-view (Corner|Full Screen)\r'), self.__MatchConfigPresentationSelfView, None)
            self.AddMatchString(re.compile(b'contentauto (on|off)\r'), self.__MatchContentAuto, None)
            self.AddMatchString(re.compile(b'lanport (auto|10{1,3}[hf]dx)\r'), self.__MatchLANPort, None)
            self.AddMatchString(re.compile(b'mute far (on|off)\r|mute far no call connected\r'), self.__MatchMuteFarStatus, None)
            self.AddMatchString(re.compile(b'(vcbutton registered|already active:vcbutton)\r|vcbutton (farplay|farstop|stop|play) ?\r'), self.__MatchPresentationStatus, None)
            self.AddMatchString(re.compile(b'provider:(Poly|Zoom|Teams|LogMeIn|BlueJeans|RingCentral|camuvc|StarLeaf|DialPad) lockState:(locked|unlocked)\r'), self.__MatchProviderMode, None)
            self.AddMatchString(re.compile(b'systemsetting selfview (On|Off|Auto)\r'), self.__MatchSelfview, None)
            if self.ConnectionType == 'Serial':
                self.AddMatchString(re.compile(b'(sleep registered|already active:sleep)\r|listen (going to sleep|waking up)\r|(wake|sleep)\r\n'), self.__MatchSleepMode, None)
            else:
                self.AddMatchString(re.compile(b'(sleep registered|already active:sleep)\r|listen (going to sleep|waking up)\r|(wake|sleep)\r\r\n'), self.__MatchSleepMode, None)
            self.AddMatchString(re.compile(b'sleeptime (0|1|3|15|30|45|60|120|240|480)\r'), self.__MatchSleepTime, None)
            self.AddMatchString(re.compile(b'(audiotransmitlevel registered|already active:audiotransmitlevel)\r|audiotransmitlevel (-?\d+)\r'), self.__MatchTransmitLevel, None)
            self.AddMatchString(re.compile(b'(mute registered|already active:mute)\r|(video)?mute near (on|off)\r'), self.__MatchTransmitMute, None)
            self.AddMatchString(re.compile(b'version (.+?)\r'), self.__MatchVersion, None)
            self.AddMatchString(re.compile(b'vcbutton source get ([1-6]|none)\r'), self.__MatchVideoContentSource, None)
            self.AddMatchString(re.compile(b'(volume registered|already active:volume)\r|volume (\d+)\r'), self.__MatchVolume, None)

            self.AddMatchString(re.compile(b'error: (.*?)\r'), self.__MatchError, None)

        self.DialString = ''
        self.PhoneBookSearch = ''
        self.PhoneBookGroupSearch = ''
        self.authenticated = True
        self.password_count = 0
        self.CallInfoAll = False
        self.NotifyCallStatus = False
        self.NotifyLineStatus = False
        self.SleepRegister = False
        self.TransmitLevelRegister = False
        self.TransmitMuteRegister = False
        self.VCButtonRegister = False
        self.VolumeRegister = False
        self.CallHistoryScroller = Scroller([], self.NumberofCallHistoryResults, end='*** End of List ***')
        self.CallHistoryRegex = re.compile(b'\s?\"?(?P<dialstr>.+)\"?\t(?P<date>\d{2}/[a-zA-Z]+/\d{4}) (?P<time>\d{2}:\d{2}:\d{2})\t(?P<state>.+)\r')
        self.CallInfoData = defaultdict(lambda: {
            'callid': None,
            'name': '',
            'number': '',
            'state': 'inactive'
        })
        self.CallInfoRegex = re.compile('callinfo:(?P<callid>.*?):(?P<name>.*?):(?P<number>.*?):.*?:(?P<state>.*?):.*?:.*?:.*?\r')
        self.NotifyCallStatusRegex = re.compile(b'notification:callstatus:(?:incoming|outgoing):(?P<callid>\d+):(?P<name>.*?):(?P<number>.*?):(?P<state>opened|ringing|connecting|connected|disconnecting|disconnected):\d+:\d+:.*?\r')
        self.NotifyLineStatusRegex = re.compile(b'notification:linestatus:(?:incoming|outgoing):(?P<number>.*?):(?P<callid>\d+):\d+:\d+:(?P<state>inactive)\r')
        self.CallInfoSortKey = lambda c: (c['state'] != 'ringing', c['callid'])

        self.ContentScroller = Scroller([], self.NumberofContentResults, end='*** End of List ***')
        self.ContentListRegex = re.compile(b'content list start[\s\S]+content list end\r')
        self.ContentRegex = re.compile('content id:"(.*?)" name:"(.*?)" type:.+?shown:.*?\r')

        self.MeetingScroller = Scroller([], self._NumberofMeetingResults, end='*** End of List ***')
        self.MeetingListRegex = re.compile(b'calendarmeetings list begin[\s\S]+calendarmeetings list end\r|error: calendar service is not available\r')
        self.MeetingRegex = re.compile('meeting\|(?P<meetingid>.*?)\|(?P<start>.*?)\|(?P<end>.*?)\|(?P<subject>.*?)\r')
        self.MeetingInfoRegex = re.compile(b'calendarmeetings info start[\s\S]+calendarmeetings info end\r')
        self.MeetingIDRegex = re.compile('id\|(.*?)\r')
        self.MeetingLocationRegex = re.compile('location\|(.*?)\r')
        self.MeetingOrganizerRegex = re.compile('organizer\|(.*?)\r')
        self.MeetingNumberRegex = re.compile('dialingnumber\|(audio|video)\|(.*?)(?:\|?(sip|h323|))\r')
        
        self.PhonebookGroupScroller = LoadingScroller([], self._NumberofPhonebookResults, 50, self.__PhonebookCallback, end='*** End of List ***')
        self.PhonebookScroller = LoadingScroller([], self._NumberofPhonebookResults, 50, self.__PhonebookCallback, end='*** End of List ***')
        self.PhonebookListRegex = re.compile(b'(?:(?:local|global)dir \d+\. (.*?)\s*:\s*(.*?):(site|group)\r\s*)*(?:local|global)dir.+?range.+?done\r|info: no matched group found\r|error: command not supported in current configuration\r')
        self.PhonebookRegex = re.compile('(?:local|global)dir \d+\. (.*?)\s*:\s*(.*?):(site|group)\r')
        self.PhonebookQueryString = ''
        self.PhonebookResultListRegex = re.compile(b'(?:(?:local|global)dir \d+\. .*?\r\s*)*(?:local|global)dir entry .*? done\r|Please input a valid directory id\r')
        self.PhonebookResultRegex = re.compile('(?:local|global)dir \d+\. "(?:.*?)" (?:sip_spd:.*? sip_num:(?P<SIP_Number>.*?)|h323_spd:.*? h323_num:(?P<H323_Number>.*?) h323_ext:(?P<H323_Extension>.*?))(?::site)?\r')

    @property
    def MeetingsTimeFormat(self):
        return self._MeetingsTimeFormat

    @MeetingsTimeFormat.setter
    def MeetingsTimeFormat(self, value):
        try:
            timeFormat = {
                '12 Hour': '%I:%M%p',
                '24 Hour': '%H:%M'
            }
            self._MeetingsTimeFormat = timeFormat[value]
        except Exception:
            self.Error(['Missing Meetings Time Format parameter'])

    @property
    def MeetingsTimeInterval(self):
        return self._MeetingsTimeInterval

    @MeetingsTimeInterval.setter
    def MeetingsTimeInterval(self, value):
        try:
            timeInterval = {
                'One Day': 0,
                'Five Days': 5,
                'One Week': 7
            }

            self._MeetingsTimeInterval = timeInterval[value]
        except Exception:
            self.Error(['Missing Meetings Time Interval parameter'])

    @property
    def NumberofPhonebookResults(self):
        return self._NumberofPhonebookResults

    @NumberofPhonebookResults.setter
    def NumberofPhonebookResults(self, value):
        self._NumberofPhonebookResults = int(value)

    @property
    def NumberofCallHistoryResults(self):
        return self._NumberofCallHistoryResults

    @NumberofCallHistoryResults.setter
    def NumberofCallHistoryResults(self, value):
        self._NumberofCallHistoryResults = int(value)

    @property
    def NumberofContentResults(self):
        return self._NumberofContentResults

    @NumberofContentResults.setter
    def NumberofContentResults(self, value):
        self._NumberofContentResults = int(value)

    @property
    def NumberofMeetingResults(self):
        return self._NumberofMeetingResults

    @NumberofMeetingResults.setter
    def NumberofMeetingResults(self, value):
        self._NumberofMeetingResults = int(value)

    def __MatchUsername(self, match, tag):
        self.authenticated = False

        if self.password_count < 3:
            self.Send(self.deviceUsername + '\r')

    def __MatchPassword(self, match, tag):
        self.authenticated = False

        if self.password_count < 3:
            self.Send(self.devicePassword + '\r')

        self.password_count += 1

    def __MatchSuccess(self, match, tag):
        self.authenticated = True
        self.password_count = 0

    def __MatchFail(self, match, tag):
        self.authenticated = False

        if self.password_count > 2:
            self.Error(['Login failed. Please supply proper login credentials.'])

    def __MatchCallInfoAll(self, match, tag):
        if self.NotifyCallStatus and self.NotifyLineStatus:
            self.CallInfoAll = True

            if tag == 'Active':
                for match in self.CallInfoRegex.finditer(match.group(0).decode()):
                    match = match.groupdict()
                    callid = int(match['callid'])
                    call = self.CallInfoData[callid]
                    call['callid'] = callid
                    if match['name']:
                        call['name'] = match['name']
                    call['number'] = match['number']
                    call['state'] = match['state']

            self.__WriteCallInfo()

    def __MatchCallInfoUnsolicited(self, match, tag):

        value = match.group(1).decode()

        if value in ['notify callstatus success', 'already active:callstatus']:
            self.NotifyCallStatus = True
        elif value in ['notify linestatus success', 'already active:linestatus']:
            self.NotifyLineStatus = True
        else:
            match = match.groupdict()
            callid = int(match['callid'].decode())
            call = self.CallInfoData[callid]
            call['callid'] = callid

            try:
                name = match['name'].decode()

                if name:
                    call['name'] = name
            except:
                pass

            call['number'] = match['number'].decode()
            call['state'] = match['state'].decode()
            if call['state'] == 'inactive':
                del self.CallInfoData[callid]

            self.__WriteCallInfo()

    def __WriteCallHistory(self):
        for call, number in enumerate(self.CallHistoryScroller, 1):
            self.WriteStatus('CallHistoryResults', number, {'Call': call})

    def __WriteCallInfo(self):
        for call, info in enumerate(sorted(self.CallInfoData.values(), key=self.CallInfoSortKey), 1):
            self.WriteStatus('CallInfoName', info['name'], {'Call': call})
            self.WriteStatus('CallInfoNumber', info['number'], {'Call': call})
            self.WriteStatus('CallInfoState', info['state'].title(), {'Call': call})

            if call == 5:
                break

        for call in range(len(self.CallInfoData) + 1, 6):
            self.WriteStatus('CallInfoName', '', {'Call': call})
            self.WriteStatus('CallInfoNumber', '', {'Call': call})
            self.WriteStatus('CallInfoState', 'Inactive', {'Call': call})

        caller = ''
        for info in self.CallInfoData.values():
            if info['state'] == 'ringing':
                caller = info['name']
                if not caller:
                    caller = info['number']
                break

        self.WriteStatus('CallInfoCallerID', caller, None)

    def __WriteContent(self):
        for content, info in enumerate(self.ContentScroller, 1):
            if isinstance(info, tuple):
                self.WriteStatus('ContentResults', info[1], {'Content': content})
            else:
                self.WriteStatus('ContentResults', info, {'Content': content})

    def __WriteMeeting(self):
        for meeting, info in enumerate(self.MeetingScroller, 1):
            if isinstance(info, dict):
                self.WriteStatus('MeetingStart', info['start'].strftime(self.MeetingsTimeFormat), {'Meeting': meeting})
                self.WriteStatus('MeetingEnd', info['end'].strftime(self.MeetingsTimeFormat), {'Meeting': meeting})
                self.WriteStatus('MeetingSubject', info['subject'], {'Meeting': meeting})
                self.WriteStatus('MeetingTimeCombined', '{}-{}'.format(info['start'].strftime('%a {}'.format(self.MeetingsTimeFormat)), info['end'].strftime(self.MeetingsTimeFormat)), {'Meeting': meeting})

                self.WriteStatus('MeetingOrganizer', info['organizer'], {'Meeting': meeting})
                self.WriteStatus('MeetingNumber', info['number'], {'Meeting': meeting})
                self.WriteStatus('MeetingLocation', info['location'], {'Meeting': meeting})
            else:
                self.WriteStatus('MeetingStart', info, {'Meeting': meeting})
                self.WriteStatus('MeetingEnd', info, {'Meeting': meeting})
                self.WriteStatus('MeetingSubject', info, {'Meeting': meeting})
                self.WriteStatus('MeetingTimeCombined', info, {'Meeting': meeting})

                self.WriteStatus('MeetingOrganizer', info, {'Meeting': meeting})
                self.WriteStatus('MeetingNumber', info, {'Meeting': meeting})
                self.WriteStatus('MeetingLocation', info, {'Meeting': meeting})

    def __WritePhonebookGroup(self):
        for group, info in enumerate(self.PhonebookGroupScroller, 1):
            if isinstance(info, tuple):
                self.WriteStatus('PhonebookGroupResults', info[0], {'Group': group})
            else:
                self.WriteStatus('PhonebookGroupResults', info, {'Group': group})

    def __WritePhonebook(self):
        for entry, info in enumerate(self.PhonebookScroller, 1):
            if isinstance(info, tuple):
                self.WriteStatus('PhonebookResults', info[0], {'Entry': entry})
            else:
                self.WriteStatus('PhonebookResults', info, {'Entry': entry})

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'Yes': 'yes',
            'No': 'no',
            'Do Not Disturb': 'donotdisturb'
        }

        if value in ValueStateValues:
            AutoAnswerCmdString = 'autoanswer {}\r'.format(ValueStateValues[value])
            self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'autoanswer get\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'yes': 'Yes',
            'no': 'No',
            'donotdisturb': 'Do Not Disturb'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def UpdateCalendarStatus(self, value, qualifier):

        CalendarStatusCmdString = 'calendarstatus get\r'
        self.__UpdateHelper('CalendarStatus', CalendarStatusCmdString, value, qualifier)

    def __MatchCalendarStatus(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('CalendarStatus', value, None)

    def SetCallHistoryNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': self.CallHistoryScroller.previous,
            'Down': self.CallHistoryScroller.next,
            'Page Up': self.CallHistoryScroller.previous_page,
            'Page Down': self.CallHistoryScroller.next_page
        }

        if value in ValueStateValues and self.CallHistoryScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WriteCallHistory()
        else:
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistoryResultSet(self, value, qualifier):

        call = qualifier['Call']

        if 1 <= call <= self.CallHistoryScroller.window and self.CallHistoryScroller.offset + call <= self.CallHistoryScroller.current_size:
            self.DialString = self.CallHistoryScroller[call - 1]
        else:
            self.Discard('Invalid Command for SetCallHistoryResultSet')

    def SetCallHistoryUpdate(self, value, qualifier):

        if self.authenticated:
            self.CallHistoryScroller.clear()
            CallHistoryUpdateCmdString = 'recentcalls\r'
            res = self.SendAndWait(CallHistoryUpdateCmdString, 5)
            if res:
                matches = []

                for match in self.NotifyCallStatusRegex.finditer(res):
                    matches.append((match.start(0), match))
                for match in self.NotifyLineStatusRegex.finditer(res):
                    matches.append((match.start(0), match))
                for _, match in sorted(matches, key=lambda m: m[0]):
                    self.__MatchCallInfoUnsolicited(match, None)
                for call in self.CallHistoryRegex.findall(res):
                    self.CallHistoryScroller.append(call[0].decode())

            self.__WriteCallHistory()
        else:
            self.Discard('Inappropriate Command for SetCallHistoryUpdate')

    def SetCameraNearInvert(self, value, qualifier):
    
        ValueStateValues = [
            'On',
            'Off'
        ]

        if value in ValueStateValues:
            CameraNearInvertCmdString = 'camerainvert near {}\r'.format(value.lower())
            self.__SetHelper('CameraNearInvert', CameraNearInvertCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearInvert')

    def UpdateCameraNearInvert(self, value, qualifier):

        CameraNearInvertCmdString = 'camerainvert near get\r'
        self.__UpdateHelper('CameraNearInvert', CameraNearInvertCmdString, value, qualifier)

    def __MatchCameraNearInvert(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('CameraNearInvert', value, None)

    def SetCameraNearTracking(self, value, qualifier):

        if value in ['On', 'Off']:
            CameraNearTrackingCmdString = 'camera near tracking {}\r'.format(value.lower())
            self.__SetHelper('CameraNearTracking', CameraNearTrackingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearTracking')

    def UpdateCameraNearTracking(self, value, qualifier):

        CameraNearTrackingCmdString = 'camera near tracking get\r'
        self.__UpdateHelper('CameraNearTracking', CameraNearTrackingCmdString, value, qualifier)

    def __MatchCameraNearTracking(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('CameraNearTracking', value, None)

    def SetCameraNearTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Speaker': 'speaker',
            'Group': 'group',
            'Group with Transition': 'groupwithtransition',
            'Off': 'off'
        }

        if value in ValueStateValues:
            CameraNearTrackingModeCmdString = 'cameratracking near mode {}\r'.format(ValueStateValues[value])
            self.__SetHelper('CameraNearTrackingMode', CameraNearTrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearTrackingMode')

    def UpdateCameraNearTrackingMode(self, value, qualifier):

        CameraNearTrackingModeCmdString = 'cameratracking near mode get\r'
        self.__UpdateHelper('CameraNearTrackingMode', CameraNearTrackingModeCmdString, value, qualifier)

    def __MatchCameraNearTrackingMode(self, match, tag):

        ValueStateValues = {
            'speaker': 'Speaker',
            'group': 'Group',
            'groupwithtransition': 'Group with Transition',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CameraNearTrackingMode', value, None)

    def SetCameraPTZ(self, value, qualifier):

        mode = qualifier['Mode']

        if mode in ['Near', 'Far'] and value in ['Up', 'Down', 'Left', 'Right', 'Stop', 'Zoom+', 'Zoom-']:
            CameraPTZCmdString = 'camera {} move {}\r'.format(mode.lower(), value.lower())
            self.__SetHelper('CameraPTZ', CameraPTZCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPTZ')

    def SetCameraSource(self, value, qualifier):

        mode = qualifier['Mode']

        if mode in ['Near', 'Far'] and 1 <= int(value) <= 4:
            CameraSourceCmdString = 'camera {} {}\r'.format(mode.lower(), value)
            self.__SetHelper('CameraSource', CameraSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraSource')

    def UpdateCameraSource(self, value, qualifier):

        mode = qualifier['Mode']

        if mode in ['Near', 'Far']:
            CameraSourceCmdString = 'camera {} source\r'.format(mode.lower())
            self.__UpdateHelper('CameraSource', CameraSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCameraSource')

    def __MatchCameraSource(self, match, tag):

        qualifier = {
            'Mode': match.group(1).decode().title()
        }

        source = match.group(2).decode()
        value = 'Unavailable' if source == '-1' else source

        self.WriteStatus('CameraSource', value, qualifier)

    def SetConfigDisplay1(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            '1920x1080p @ 50Hz': '50hz1920x1080p',
            '1920x1080p @ 60Hz': '60hz1920x1080p',
            '3840x2160p @ 25Hz': '25hz3840x2160p',
            '3840x2160p @ 30Hz': '30hz3840x2160p',
            '3840x2160p @ 50Hz': '50hz3840x2160p',
            '3840x2160p @ 60Hz': '60hz3840x2160p'
        }

        if value in ValueStateValues:
            ConfigDisplay1CmdString = 'configdisplay monitor1 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ConfigDisplay1', ConfigDisplay1CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigDisplay1')

    def UpdateConfigDisplay1(self, value, qualifier):

        ConfigDisplay1CmdString = 'configdisplay monitor1 get\r'
        self.__UpdateHelper('ConfigDisplay1', ConfigDisplay1CmdString, value, qualifier)

    def __MatchConfigDisplay1(self, match, tag):

        ValueStateValues = {
            'auto': 'Auto',
            '1920x1080p 50Hz': '1920x1080p @ 50Hz',
            '1920x1080p 60Hz': '1920x1080p @ 60Hz',
            '3840x2160p 25Hz': '3840x2160p @ 25Hz',
            '3840x2160p 30Hz': '3840x2160p @ 30Hz',
            '3840x2160p 50Hz': '3840x2160p @ 50Hz',
            '3840x2160p 60Hz': '3840x2160p @ 60Hz'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ConfigDisplay1', value, None)

    def SetConfigDisplay2(self, value, qualifier):

        ValueStateValues = {
            'Off': 'off',
            'Auto': 'auto',
            '1920x1080p @ 50Hz': '50hz1920x1080p',
            '1920x1080p @ 60Hz': '60hz1920x1080p'
        }

        if value in ValueStateValues:
            ConfigDisplay2CmdString = 'configdisplay monitor2 {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ConfigDisplay2', ConfigDisplay2CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigDisplay2')

    def UpdateConfigDisplay2(self, value, qualifier):

        ConfigDisplay2CmdString = 'configdisplay monitor2 get\r'
        self.__UpdateHelper('ConfigDisplay2', ConfigDisplay2CmdString, value, qualifier)

    def __MatchConfigDisplay2(self, match, tag):

        ValueStateValues = {
            'off': 'Off',
            'auto': 'Auto',
            '1920x1080p 50Hz': '1920x1080p @ 50Hz',
            '1920x1080p 60Hz': '1920x1080p @ 60Hz'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ConfigDisplay2', value, None)

    def SetConfigPresentationContent(self, value, qualifier):

        if value in ['Single', 'Dual']:
            ConfigPresentationContentCmdString = 'configpresentation content {}\r'.format(value.lower())
            self.__SetHelper('ConfigPresentationContent', ConfigPresentationContentCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigPresentationContent')

    def UpdateConfigPresentationContent(self, value, qualifier):

        ConfigPresentationContentCmdString = 'configpresentation content get\r'
        self.__UpdateHelper('ConfigPresentationContent', ConfigPresentationContentCmdString, value, qualifier)

    def __MatchConfigPresentationContent(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ConfigPresentationContent', value, None)

    def SetConfigPresentationSelfView(self, value, qualifier):

        ValueStateValues = {
            'Corner': 'corner',
            'Full Screen': 'full-screen'
        }

        if value in ValueStateValues:
            ConfigPresentationSelfViewCmdString = 'configpresentation self-view {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ConfigPresentationSelfView', ConfigPresentationSelfViewCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigPresentationSelfView')

    def UpdateConfigPresentationSelfView(self, value, qualifier):

        ConfigPresentationSelfViewCmdString = 'configpresentation self-view get\r'
        self.__UpdateHelper('ConfigPresentationSelfView', ConfigPresentationSelfViewCmdString, value, qualifier)

    def __MatchConfigPresentationSelfView(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ConfigPresentationSelfView', value, None)

    def SetContentAuto(self, value, qualifier):

        if value in ['On', 'Off']:
            ContentAutoCmdString = 'contentauto {}\r'.format(value.lower())
            self.__SetHelper('ContentAuto', ContentAutoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContentAuto')

    def UpdateContentAuto(self, value, qualifier):

        ContentAutoCmdString = 'contentauto get\r'
        self.__UpdateHelper('ContentAuto', ContentAutoCmdString, value, qualifier)

    def __MatchContentAuto(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('ContentAuto', value, None)

    def SetContentNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':           self.ContentScroller.previous,
            'Down':         self.ContentScroller.next,
            'Page Up':      self.ContentScroller.previous_page,
            'Page Down':    self.ContentScroller.next_page
        }

        if value in ValueStateValues and self.ContentScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WriteContent()
        else:
            self.Discard('Invalid Command for SetContentNavigation')

    def SetContentResultSet(self, value, qualifier):

        content = qualifier['Content']

        ValueStateValues = [
            'Show',
            'Hide',
            'Close'
        ]

        if 1 <= content <= self.ContentScroller.window and self.ContentScroller.offset + content <= self.ContentScroller.current_size and value in ValueStateValues:
            ContentResultSetCmdString = 'content {} {}\r'.format(value.lower(), self.ContentScroller[content - 1][0])
            self.__SetHelper('ContentResultSet', ContentResultSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContentResultSet')

    def SetContentUpdate(self, value, qualifier):

        ValueStateValues = {
            'All':              '',
            'Unknown':          ' UNKNOWN',
            'Content Cam':      ' CONTENTCAM',
            'PPCIP':            ' PPCIP',
            'Miracast':         ' MIRACAST',
            'AirPlay':          ' AIRPLAY',
            'Drawing Board':    ' DRAWINGBOARD'
        }

        if self.authenticated:
            if value in ValueStateValues:
                self.ContentScroller.clear()

                ContentUpdateCmdString = 'content list{}\r'.format(ValueStateValues[value])
                res = self.SendAndWait(ContentUpdateCmdString, 5, deliRex=self.ContentListRegex)
                if res:
                    self.ContentScroller.overwrite(self.ContentRegex.findall(res.decode()))
                        
                self.__WriteContent()
            else:
                self.Discard('Invalid Command for SetContentUpdate')
        else:
            self.Discard('Invalid Command for SetContentUpdate')

    def SetDialString(self, value, qualifier):

        self.DialString = value

    def SetDTMF(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            DTMFCmdString = 'gendial {}\r'.format(value)
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Answer': 'answer video\r',
            'Dial 128Kbps': 'dial manual "128"',
            'Dial 256Kbps': 'dial manual "256"',
            'Dial 384Kbps': 'dial manual "384"',
            'Dial 512Kbps': 'dial manual "512"',
            'Dial 768Kbps': 'dial manual "768"',
            'Dial 1Mbps': 'dial manual "1024"',
            'Dial 1.4Mbps': 'dial manual "1472"',
            'Dial 1.9Mbps': 'dial manual "1920"',
            'Dial 2Mbps': 'dial manual "2048"',
            'Dial 3Mbps': 'dial manual "3072"',
            'Dial 3.8Mbps': 'dial manual "3840"',
            'Dial 4Mbps': 'dial manual "4096"',
            'Dial 6.1Mbps': 'dial manual "6144"',
            'Dial Auto': 'dial auto',
            'Dial Name': 'dial addressbook',
            'Dial UID': 'dial addressbook_entry',
            'Dial H323': 'dial phone h323',
            'Dial IP': 'dial phone ip',
            'Dial SIP': 'dial phone sip',
            'Hangup 1': 0,
            'Hangup 2': 1,
            'Hangup 3': 2,
            'Hangup 4': 3,
            'Hangup 5': 4,
            'Hangup All': 'hangup all\r'
        }

        if value.startswith('Dial '):
            number = self.DialString
            if number:
                HookCmdString = '{} \"{}\"\r'.format(ValueStateValues[value], number)
            else:
                self.Discard('Invalid Command for SetHook')
                return
        elif value in ['Hangup 1', 'Hangup 2', 'Hangup 3', 'Hangup 4', 'Hangup 5', 'Hangup  All']:
            if value == 'Hangup All':
                HookCmdString = ValueStateValues[value]
            else:
                index = ValueStateValues[value]
                if ValueStateValues[value] + 1 <= len(self.CallInfoData):
                    HookCmdString = 'hangup video {}\r'.format(sorted(self.CallInfoData.values(), key=self.CallInfoSortKey)[index]['callid'])
                else:
                    self.Discard('Invalid Command for SetHook')
                    return
        elif value in ValueStateValues:
            HookCmdString = ValueStateValues[value]
        else:
            self.Discard('Invalid Command for SetHook')
            return

        self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = [
            '1',
            '2',
            '3',
            '4',
            '5',
            '6',
            '7',
            '8',
            '9',
            '0',
            '.',
            '#',
            '*'
        ]

        if value in ValueStateValues:
            KeypadCmdString = 'button {}\r'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def UpdateLANPort(self, value, qualifier):

        LANPortCmdString = 'lanport get\r'
        self.__UpdateHelper('LANPort', LANPortCmdString, value, qualifier)

    def __MatchLANPort(self, match, tag):

        ValueStateValues = {
            'auto': 'Auto',
            '10hdx': '10 Mbps Half Duplex',
            '10fdx': '10 Mbps Full Duplex',
            '100hdx': '100 Mbps Half Duplex',
            '100fdx': '100 Mbps Full Duplex',
            '1000hdx': '1000 Mbps Half Duplex',
            '1000fdx': '1000 Mbps Full Duplex'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LANPort', value, None)

    def UpdateMeetingListQuery(self, value, qualifier):

        if self.authenticated:
            self.MeetingScroller.clear()

            current_time = datetime.now()
            if self.MeetingsTimeInterval == 0:
                MeetingListCmdString = 'calendarmeetings list today:{} tomorrow:23:59\r'.format(current_time.strftime('%H:%M'))
            else:
                MeetingListCmdString = 'calendarmeetings list today:{} {}\r'.format(current_time.strftime('%H:%M'), (current_time + timedelta(self.MeetingsTimeInterval)).strftime('%Y-%m-%d:%H:%M'))

            res = self.SendAndWait(MeetingListCmdString, 5, deliRex=self.MeetingListRegex)
            if res:
                for meeting in self.MeetingRegex.finditer(res.decode()):
                    meeting = meeting.groupdict()
                    meeting['start'] = datetime.strptime(meeting['start'], '%Y-%m-%d:%H:%M')
                    meeting['end'] = datetime.strptime(meeting['end'], '%Y-%m-%d:%H:%M')
                    meeting['organizer'] = ''
                    meeting['location'] = ''
                    meeting['number'] = 'No number to dial'

                    self.MeetingScroller.append(meeting)

            if self.MeetingScroller.all_size > 0:
                self.UpdateMeetingOrganizer()

            self.__WriteMeeting()
        else:
            self.Discard('Inappropriate Command for UpdateMeetingListQuery')

    def UpdateMeetingOrganizer(self):
        for meeting in self.MeetingScroller.all_items:
            MeetingOrganizerCmdString = 'calendarmeetings info {}\r'.format(meeting['meetingid'])
            res = self.SendAndWait(MeetingOrganizerCmdString, 3, deliRex=self.MeetingInfoRegex)
            if res:
                meetingid = self.MeetingIDRegex.search(res.decode())
                if meetingid and meeting['meetingid'] == meetingid.group(1):
                    organizer = self.MeetingOrganizerRegex.search(res.decode())
                    if organizer:
                        meeting['organizer'] = organizer.group(1)
                    else:
                        meeting['organizer'] = ''

                    location = re.search(self.MeetingLocationRegex, res.decode())
                    if location:
                        meeting['location'] = location.group(1)
                    else:
                        meeting['location'] = ''

                    numbers = {}
                    for number in re.findall(self.MeetingNumberRegex, res.decode()):
                        numbers['{}{}'.format(number[0], number[2])] = number[1]

                    if 'videoh323' in numbers:
                        number = numbers['videoh323']
                    elif 'videosip' in numbers:
                        number = numbers['videosip']
                    elif 'video' in numbers:
                        number = numbers['video']
                    elif 'audio' in numbers:
                        number = numbers['audio']
                    else:
                        number = 'No number to dial'

                    meeting['number'] = number

    def SetMeetingNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': self.MeetingScroller.previous,
            'Down': self.MeetingScroller.next,
            'Page Up': self.MeetingScroller.previous_page,
            'Page Down': self.MeetingScroller.next_page
        }

        if value in ValueStateValues and self.MeetingScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WriteMeeting()
        else:
            self.Discard('Invalid Command for SetMeetingNavigation')

    def SetMeetingNumberSet(self, value, qualifier):

        meeting = qualifier['Meeting']

        if 1 <= meeting <= self.MeetingScroller.window and self.MeetingScroller.offset + meeting <= self.MeetingScroller.current_size:
            dial_string = self.MeetingScroller[meeting - 1]['number']
            if dial_string and dial_string != 'No number to dial':
                self.DialString = dial_string
        else:
            self.Discard('Invalid Command for SetMeetingNumberSet')

    def SetMeetingRefresh(self, value, qualifier):

        self.UpdateMeetingListQuery(value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Menu': 'menu',
            'Call Screen': 'call',
            'Keyboard': 'keyboard',
            'Select': 'select',
            'Back': 'back',
            'Delete': 'delete'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = 'button {}\r'.format(ValueStateValues[value])
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def UpdateMuteFarStatus(self, value, qualifier):

        MuteFarStatusCmdString = 'mute far get\r'
        self.__UpdateHelper('MuteFarStatus', MuteFarStatusCmdString, value, qualifier)

    def __MatchMuteFarStatus(self, match, tag):

        if match.group(1):
            value = match.group(1).decode().title()
        else:
            value = 'Unknown'

        self.WriteStatus('MuteFarStatus', value, None)

    def SetPhonebookGroupNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': self.PhonebookGroupScroller.previous,
            'Down': self.PhonebookGroupScroller.next,
            'Page Up': self.PhonebookGroupScroller.previous_page,
            'Page Down': self.PhonebookGroupScroller.next_page
        }

        if value in ValueStateValues and self.PhonebookGroupScroller.current_size + self.PhonebookScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WritePhonebookGroup()
        else:
            self.Discard('Invalid Command for SetPhonebookGroupNavigation')

    def SetPhonebookGroupResultSet(self, value, qualifier):

        group = int(qualifier['Group'])

        if 1 <= group <= self.PhonebookGroupScroller.window and self.PhonebookGroupScroller.offset + group <= self.PhonebookGroupScroller.current_size:
            group_uid = self.PhonebookGroupScroller[group - 1][1]
            if group_uid:
                self.PhoneBookGroupSearch = group_uid
        else:
            self.Discard('Invalid Command for SetPhonebookGroupResultSet')

    def SetPhonebookGroupSearch(self, value, qualifier):

        self.PhoneBookGroupSearch = value

    def SetPhonebookNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': self.PhonebookScroller.previous,
            'Down': self.PhonebookScroller.next,
            'Page Up': self.PhonebookScroller.previous_page,
            'Page Down': self.PhonebookScroller.next_page
        }

        if value in ValueStateValues and self.PhonebookScroller.current_size + self.PhonebookGroupScroller.current_size > 0:
            ValueStateValues[value]()
            self.__WritePhonebook()
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookResultSet(self, value, qualifier):

        entry = int(qualifier['Entry'])

        TypeStates = [
            'Name',
            'UID',
            'H323 Number',
            'H323 Extension',
            'SIP Number'
        ]
        type_ = qualifier['Type']

        if self.authenticated:
            if 1 <= entry <= self.PhonebookScroller.window and self.PhonebookScroller.offset + entry <= self.PhonebookScroller.current_size and type_ in TypeStates:
                if type_ == 'Name':
                    dial_string = self.PhonebookScroller[entry - 1][0]
                elif type_ == 'UID':
                    dial_string = self.PhonebookScroller[entry - 1][1]
                else:
                    dial_string = ''
                    if self.PhonebookQueryString.startswith('localdir'):
                        PhonebookResultSetCmdString = 'localdir entry {}\r'.format(self.PhonebookScroller[entry - 1][1])
                    else:
                        PhonebookResultSetCmdString = 'globaldir entry {}\r'.format(self.PhonebookScroller[entry - 1][1])

                    res = self.SendAndWait(PhonebookResultSetCmdString, self.DefaultResponseTimeout, deliRex=self.PhonebookResultListRegex)
                    if res:
                        for match in self.PhonebookResultRegex.finditer(res):
                            match = match.groupdict()
                            if match[type_.replace(' ', '_')] is not None:
                                dial_string = match[type_.replace(' ', '_')].strip()
                                break

                self.DialString = dial_string
            else:
                self.Discard('Invalid Command for SetPhonebookResultSet')
        else:
            self.Discard('Invalid Command for SetPhonebookResultSet')

    def SetPhonebookSearch(self, value, qualifier):

        self.PhoneBookSearch = value

    def SetPhonebookUpdate(self, value, qualifier):

        if self.authenticated:
            if value in ['Local', 'Global', 'Global Grouplist']:
                search = self.PhoneBookSearch
                search = ' "{}"'.format(search) if search else ''

                uid = self.PhoneBookGroupSearch
                uid = ' grouplist {}'.format(uid) if uid else ''
                if value == 'Local':
                    self.PhonebookQueryString = 'localdir{}{} range {{}} {{}}\r'.format(uid, search)
                else:
                    if value == 'Global':
                        self.PhonebookQueryString = 'globaldir{}{} range {{}} {{}}\r'.format(uid, search)
                    else:
                        self.PhonebookQueryString = 'globaldir grouplist range {} {}\r'

                self.PhonebookGroupScroller.clear()
                self.PhonebookScroller.clear()
                self.PhonebookGroupScroller.load()

                self.__WritePhonebookGroup()
                self.__WritePhonebook()
            else:
                self.Discard('Invalid Command for SetPhonebookUpdate')
        else:
            self.Discard('Invalid Command for SetPhonebookUpdate')

    def __PhonebookCallback(self, size, chunk):
        if self.authenticated:
            offset = self.PhonebookScroller.all_size + self.PhonebookGroupScroller.all_size
            res = self.SendAndWait(self.PhonebookQueryString.format(offset, offset + chunk - 1), 5, deliRex=self.PhonebookListRegex)

            if res:
                results = self.PhonebookRegex.findall(res.decode())
                for entry in results:
                    if entry[2] == 'site':
                        self.PhonebookScroller.append(entry)
                    elif entry[2] == 'group':
                        self.PhonebookGroupScroller.append(entry)

                if len(results) < self.PhonebookScroller.chunk_size:
                    self.PhonebookScroller.loaded = True
                    self.PhonebookGroupScroller.loaded = True

                    return [], True
                else:
                    return [], False
            else:
                return [], False
        else:
            self.Discard('Inappropriate Command')
            return [], False

    def UpdatePresentationStatus(self, value, qualifier):

        if not self.VCButtonRegister:
            PresentationStatusCmdString = 'vcbutton register\r'
            self.__UpdateHelper('PresentationStatus', PresentationStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationStatus')

    def __MatchPresentationStatus(self, match, tag):
    
        if match.group(1):
            self.VCButtonRegister = True
            self.WriteStatus('PresentationStatus', 'Unknown', {'Site': 'Near'})
            self.WriteStatus('PresentationStatus', 'Unknown', {'Site': 'Far'})
        elif self.VCButtonRegister:
            ValueStateValues = {
                'play':     'Play',
                'farplay':  'Play',
                'farstop':  'Stop',
                'stop':     'Stop'
            }
            
            value = match.group(2).decode()
            self.WriteStatus('PresentationStatus', ValueStateValues[value], {'Site': 'Far' if 'far' in value else 'Near'})

    def SetPresetFar(self, value, qualifier):

        ModeStates = {
            'Recall': 'go',
            'Save': 'set'
        }
        mode = qualifier['Mode']

        if mode in ModeStates and 0 <= int(value) <= 15:
            PresetFarCmdString = 'preset far {} {}\r'.format(ModeStates[mode], value)
            self.__SetHelper('PresetFar', PresetFarCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetFar')

    def SetPresetNear(self, value, qualifier):

        ModeStates = {
            'Recall': 'go',
            'Save': 'set'
        }
        mode = qualifier['Mode']

        if mode in ModeStates and 0 <= int(value) <= 99:
            PresetNearCmdString = 'preset near {} {}\r'.format(ModeStates[mode], value)
            self.__SetHelper('PresetNear', PresetNearCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetNear')

    def UpdateProviderLock(self, value, qualifier):

        self.UpdateProviderMode(value, qualifier)

    def SetProviderMode(self, value, qualifier):

        ValueStateValues = {
            'Poly': 'Poly',
            'Zoom Rooms': 'Zoom',
            'Microsoft Teams': 'Teams',
            'GoToRoom': 'LogMeIn',
            'BlueJeans Rooms': 'BlueJeans',
            'RingCentral Rooms': 'RingCentral',
            'Device Mode': 'camuvc',
            'StarLeaf': 'StarLeaf',
            'Dialpad Conference Room': 'DialPad'
        }

        if value in ValueStateValues:
            ProviderModeCmdString = 'providermode set {}\r'.format(ValueStateValues[value])
            self.__SetHelper('ProviderMode', ProviderModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProviderMode')

    def UpdateProviderMode(self, value, qualifier):

        ProviderModeCmdString = 'providermode get\r'
        self.__UpdateHelper('ProviderMode', ProviderModeCmdString, value, qualifier)

    def __MatchProviderMode(self, match, tag):

        ValueStateValues = {
            'Poly': 'Poly',
            'Zoom': 'Zoom Rooms',
            'Teams': 'Microsoft Teams',
            'LogMeIn': 'GoToRoom',
            'BlueJeans': 'BlueJeans Rooms',
            'RingCentral': 'RingCentral Rooms',
            'camuvc': 'Device Mode',
            'StarLeaf': 'StarLeaf',
            'DialPad': 'Dialpad Conference Room'
        }

        self.WriteStatus('ProviderLock', match.group(2).decode().title(), None)

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ProviderMode', value, None)

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'reboot now\r', value, qualifier)

    def SetSelfview(self, value, qualifier):

        if value in ['On', 'Off', 'Auto']:
            SelfviewCmdString = 'systemsetting selfview {}\r'.format(value.lower())
            self.__SetHelper('Selfview', SelfviewCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfview')

    def UpdateSelfview(self, value, qualifier):

        SelfviewCmdString = 'systemsetting get selfview\r'
        self.__UpdateHelper('Selfview', SelfviewCmdString, value, qualifier)

    def __MatchSelfview(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('Selfview', value, None)

    def SetSleepMode(self, value, qualifier):

        if value in ['Sleep', 'Wake']:
            SleepModeCmdString = '{}\r'.format(value.lower())
            self.__SetHelper('SleepMode', SleepModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepMode')

    def __MatchSleepMode(self, match, tag):

        if match.group(1):
            self.SleepRegister = True
            self.WriteStatus('SleepMode', 'Unknown', None)
        elif self.SleepRegister:
            ValueStateValues = {
                'going to sleep': 'Sleep',
                'sleep': 'Sleep',
                'waking up': 'Wake',
                'wake': 'Wake'
            }

            value = ValueStateValues[match.group(match.lastindex).decode()]
            self.WriteStatus('SleepMode', value, None)

    def SetSleepTime(self, value, qualifier):

        if value in ['0', '1', '3', '15', '30', '45', '60', '120', '240', '480']:
            SleepTimeCmdString = 'sleeptime {}\r'.format(value)
            self.__SetHelper('SleepTime', SleepTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTime')

    def UpdateSleepTime(self, value, qualifier):

        SleepTimeCmdString = 'sleeptime get\r'
        self.__UpdateHelper('SleepTime', SleepTimeCmdString, value, qualifier)

    def __MatchSleepTime(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SleepTime', value, None)

    def SetTransmitLevel(self, value, qualifier):

        if -6 <= value <= 18:
            TransmitLevelCmdString = 'audiotransmitlevel set {}\r'.format(value)
            self.__SetHelper('TransmitLevel', TransmitLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitLevel')

    def UpdateTransmitLevel(self, value, qualifier):

        if self.TransmitLevelRegister:
            TransmitLevelCmdString = 'audiotransmitlevel get\r'
        else:
            TransmitLevelCmdString = 'audiotransmitlevel register\r'

        self.__UpdateHelper('TransmitLevel', TransmitLevelCmdString, value, qualifier)

    def __MatchTransmitLevel(self, match, tag):

        if match.group(1):
            self.TransmitLevelRegister = True
        elif self.TransmitLevelRegister:
            value = int(match.group(2).decode())
            if -6 <= value <= 18:
                self.WriteStatus('TransmitLevel', value, None)

    def SetTransmitMute(self, value, qualifier):

        if value in ['On', 'Off']:
            TransmitMuteCmdString = 'mute near {}\r'.format(value.lower())
            self.__SetHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitMute')

    def UpdateTransmitMute(self, value, qualifier):

        if self.TransmitMuteRegister:
            TransmitMuteCmdString = 'mute near get\r'
        else:
            TransmitMuteCmdString = 'mute register\r'

        self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def __MatchTransmitMute(self, match, tag):

        if match.group(1):
            self.TransmitMuteRegister = True
        else:
            value = match.group(3).decode().title()

            if match.group(2) and match.group(2).decode() == 'video':
                self.WriteStatus('VideoMute', value, None)
            elif self.TransmitMuteRegister:
                self.WriteStatus('TransmitMute', value, None)

    def UpdateVersion(self, value, qualifier):

        if not self.SleepRegister:
            VersionCmdString = 'sleep register\r'
        elif not self.NotifyCallStatus:
            VersionCmdString = 'notify callstatus\r'
        elif not self.NotifyLineStatus:
            VersionCmdString = 'notify linestatus\r'
        elif not self.CallInfoAll:
            VersionCmdString = 'callinfo all\r'
        else:
            VersionCmdString = 'version\r'
            self.__UpdateHelper('Version', VersionCmdString, value, qualifier)

            return

        self.__UpdateHelper('Version', VersionCmdString, value, qualifier)

    def __MatchVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Version', value, None)

    def SetVideoContentSource(self, value, qualifier):

        if value in ['1', '2', '3', '4', '5', '6', 'Stop']:
            if value != 'Stop':
                VideoContentSourceCmdString = 'vcbutton play {}\r'.format(value)
            else:
                VideoContentSourceCmdString = 'vcbutton stop\r'

            self.__SetHelper('VideoContentSource', VideoContentSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoContentSource')

    def UpdateVideoContentSource(self, value, qualifier):

        VideoContentSourceCmdString = 'vcbutton source get\r'
        self.__UpdateHelper('VideoContentSource', VideoContentSourceCmdString, value, qualifier)

    def __MatchVideoContentSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Stop' if value == 'none' else value
        self.WriteStatus('VideoContentSource', value, None)

    def SetVideoMute(self, value, qualifier):

        if value in ['On', 'Off']:
            VideoMuteCmdString = 'videomute near {}\r'.format(value.lower())
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'videomute near get\r'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 50:
            VolumeCmdString = 'volume set {}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if self.VolumeRegister:
            VolumeCmdString = 'volume get\r'
        else:
            VolumeCmdString = 'volume register\r'

        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        if match.group(1):
            self.VolumeRegister = True
        elif self.VolumeRegister:
            value = int(match.group(2).decode())
            if 0 <= value <= 50:
                self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        if self.authenticated:
            self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command')

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.authenticated:
            sleepmode = self.ReadStatus('SleepMode')
            # The following queries will cause the device to wake up from sleep, so block.
            if sleepmode in ['Sleep', 'Unknown', None] and command in ['CameraNearTracking', 'CameraNearTrackingMode',
                                                                       'CameraSource', 'VideoContentSource']:
                self.Discard('Inappropriate Command')
            else:
                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                self.Send(commandstring)
        else:
            self.Discard('Inapproperiate Command')

    def __MatchError(self, match, tag):

        self.counter = 0

        self.Error([match.group(0).decode().strip()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.authenticated = True
        self.password_count = 0

        self.CallInfoAll = False
        self.NotifyCallStatus = False
        self.NotifyLineStatus = False
        self.SleepRegister = False
        self.TransmitLevelRegister = False
        self.TransmitMuteRegister = False
        self.VCButtonRegister = False
        self.VolumeRegister = False

        self.CallInfoData.clear()

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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()

class Scroller:
    def __init__(self, items, window, mark_end=True, end='', fill=''):

        self.__all_items = list(items)
        self.__filtered_items = []
        self.__filter_key = None
        self.__current_items = self.__all_items
        self.__offset = 0
        self.__window = max(1, window)
        self.__mark_end = mark_end
        self.__end = end
        self.__fill = fill

    def __getitem__(self, index):

        return self.view()[index]

    def __iter__(self):

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            yield item

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                yield self.end

            for i in range(fill_count - int(self.mark_end)):
                yield self.fill

    def __str__(self):

        s = 'Offset {}/{}, viewing ({{}}) {}/{} items ({})'.format(self.offset, self.max_offset, self.window, self.current_size, self.view())

        if not self.filtered:
            return s.format('all')
        else:
            return s.format('filtered')

    @property
    def current_items(self):

        return self.__current_items.copy()

    @property
    def all_items(self):

        return self.__all_items.copy()

    @property
    def filtered_items(self):

        return self.__filtered_items.copy()

    @property
    def current_size(self):

        return len(self.__current_items)

    @property
    def all_size(self):

        return len(self.__all_items)

    @property
    def filtered_size(self):

        return len(self.__filtered_items)

    @property
    def offset(self):

        self.__offset = min(self.__offset, self.max_offset)
        return self.__offset

    @offset.setter
    def offset(self, offset):

        if 0 <= offset <= self.max_offset:
            self.__offset = offset
            return

        raise Exception('offset value \'{}\' is out of range [0, {}]'.format(offset, self.max_offset))

    @property
    def window(self):

        return self.__window

    @property
    def mark_end(self):

        return self.__mark_end

    @property
    def end(self):

        return self.__end

    @property
    def fill(self):

        return self.__fill

    @property
    def filtered(self):

        return self.__filter_key is not None

    @property
    def max_offset(self):

        return max(0, self.current_size - self.window + int(self.mark_end))

    def view(self):

        return list(self.__iter__())

    def format(self, key):

        items = []

        stop = min(self.offset + self.window, self.current_size)

        for item in self.__current_items[self.offset:stop]:
            items.append(key(item))

        fill_count = self.offset + self.window - self.current_size
        if fill_count > 0:
            if self.mark_end:
                items.append(self.end)

            for i in range(fill_count - int(self.mark_end)):
                items.append(self.fill)

        return items

    def clear(self):

        self.__all_items.clear()

        self.__filtered_items.clear()
        self.__filter_key = None

        self.__current_items = self.__all_items

        self.offset = 0

    def overwrite(self, items):

        self.clear()
        self.extend(items)

    def append(self, item):

        self.__all_items.append(item)

        if self.__filter_key is not None and self.__filter_key(item):
            self.__filtered_items.append(item)

    def extend(self, items):

        self.__all_items.extend(items)

        if self.__filter_key is not None:
            for item in items:
                if self.__filter_key(item):
                    self.__filtered_items.append(item)

    def filter(self, key):

        self.__filter_key = key

        if self.__filter_key is not None:
            self.__filtered_items = [item for item in self.__all_items if self.__filter_key(item)]
            self.__current_items = self.__filtered_items
        else:
            self.__filtered_items.clear()
            self.__current_items = self.__all_items

        self.offset = 0

    def scroll(self, steps):

        self.offset = max(0, min(self.offset + steps, self.max_offset))

    def previous(self):

        self.scroll(-1)

    def next(self):

        self.scroll(1)

    def previous_page(self):

        self.scroll(-self.window)

    def next_page(self):

        self.scroll(self.window)

    def first(self):

        self.offset = 0

    def last(self):

        self.offset = self.max_offset

class LoadingScroller(Scroller):
    def __init__(self, items, window, chunk_size, on_end_callback, mark_end=True, end='', fill=''):

        super().__init__(items, window, mark_end=mark_end, end=end, fill=fill)

        self.__loaded = False
        self.__chunk_size = max(self.window, chunk_size)
        self.__on_end_callback = on_end_callback

    @property
    def loaded(self):

        return self.__loaded

    @loaded.setter
    def loaded(self, loaded):

        if type(loaded) == bool:
            self.__loaded = loaded
            return

        raise Exception('loaded value \'{}\' is not a boolean'.format(loaded))

    @property
    def chunk_size(self):

        return self.__chunk_size

    @property
    def max_offset(self):

        if not self.filtered:
            return max(0, super().max_offset - int(self.mark_end) + (int(self.loaded) if self.mark_end else 0))
        else:
            return super().max_offset

    def clear(self):

        super().clear()
        self.loaded = False

    def scroll(self, steps):

        if not self.scrollable(steps):
            self.load()
            super().scroll(min(steps, self.max_offset - self.offset))
        else:
            super().scroll(steps)

    def load(self):

        chunk, self.loaded = self.__on_end_callback(self.all_size, self.chunk_size)
        self.extend(chunk)

    def scrollable(self, steps):

        return self.loaded or self.offset + steps <= self.max_offset or self.filtered