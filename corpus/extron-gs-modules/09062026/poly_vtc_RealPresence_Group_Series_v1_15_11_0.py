from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import Wait, ProgramLog
from datetime import datetime, timedelta

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
        self._MeetingsTimeInterval = 0
        self._MeetingsTimeFormat = '%I:%M%p'
        self._NumberOfCallHistory = 5
        self._NumberOfPhonebookSearch = 5
        self.deviceUsername = 'admin'
        self.devicePassword = 'admin'

        self.Models = {
            'RealPresence Group 700': self.poly_12_385_700,
            'RealPresence Group 500': self.poly_12_385_300_500,
            'RealPresence Group 300': self.poly_12_385_300_500,
            'RealPresence Group 310': self.poly_12_385_300_500,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoShowContent': {'Status': {}},
            'CalendarStatus': {'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistorySearchResults': {'Parameters': ['Button'], 'Status': {}},
            'CallHistorySelect': {'Status': {}},
            'CallHistoryUpdate': {'Status': {}},
            'CallInfo': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoName': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoNumber': {'Parameters': ['Call'], 'Status': {}},
            'CallState': {'Status': {}},
            'CallStateIncomingCallID': {'Status': {}},
            'CameraFarPanTilt': {'Status': {}},
            'CameraFarSource': {'Status': {}},
            'CameraFarZoom': {'Status': {}},
            'CameraNearPanPosition': {'Status': {}},
            'CameraNearPanTilt': {'Status': {}},
            'CameraNearPosition': {'Status': {}},
            'CameraNearSource': {'Status': {}},
            'CameraNearTiltPosition': {'Status': {}},
            'CameraNearZoom': {'Status': {}},
            'CameraNearZoomPosition': {'Status': {}},
            'CameraNearTracking': {'Status': {}},
            'CameraNearTrackingMode': {'Status': {}},
            'CameraPresetFarRecall': {'Status': {}},
            'CameraPresetFarSave': {'Status': {}},
            'CameraPresetNearRecall': {'Status': {}},
            'CameraPresetNearSave': {'Status': {}},
            'ConfigPresentation': {'Parameters': ['Monitor'], 'Status': {}},
            'DTMF': {'Status': {}},
            'DualMonitor': {'Status': {}},
            'Firmware': {'Status': {}},
            'Hangup': {'Status': {}},
            'Hook': {'Status': {}},
            'IPAddress': {'Status': {}},
            'IREmulation': {'Status': {}},
            'LANPortSettings': {'Status': {}},
            'MeetingEnd': {'Parameters': ['Label'], 'Status': {}},
            'MeetingListQuery': {'Status': {}},
            'MeetingLocation': {'Parameters': ['Label'], 'Status': {}},
            'MeetingNumber': {'Parameters': ['Label'], 'Status': {}},
            'MeetingNumberSet': {'Status': {}},
            'MeetingOrganizer': {'Parameters': ['Label'], 'Status': {}},
            'MeetingRefresh': {'Status': {}},
            'MeetingStart': {'Parameters': ['Label'], 'Status': {}},
            'MeetingSubject': {'Parameters': ['Label'], 'Status': {}},
            'MeetingTimeCombined': {'Parameters': ['Label'], 'Status': {}},
            'MultipointAutoAnswer': {'Status': {}},
            'MultipointMode': {'Status': {}},
            'MuteFarStatus': {'Status': {}},
            'PhonebookGroupNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookGroupSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookGroupSearchSet': {'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PIPLocation': {'Status': {}},
            'PresentationStatus': {'Status': {}},
            'Reboot': {'Status': {}},
            'Selfview': {'Status': {}},
            'SleepMode': {'Status': {}},
            'SleepTime': {'Status': {}},
            'TransmitLevel': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VideoContentSource': {'Status': {}},
            'VideoFormat': {'Parameters': ['Monitor', 'Resolution'], 'Status': {}},
            'VideoFormatStatus': {'Parameters': ['Monitor'], 'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.PhonebookTimer = None
        self.SleepRegister = 'Disabled'

        self.oldres = ''
        self.uidSelected = ''
        self.uidGroupSelected = ''

        self.CallID = []
        self.CallCount = 0
        self.CallInfoRegex = compile('callinfo:(.*):(.*):(.*):.*:(.*):(muted|notmuted):.*:(\w*call|\w*only)\r\n')

        self.Meeting = compile('meeting\|(.*)\|(.*)\|(.*)\|(.*)\r\n')
        self.MeetingID = []
        self.MeetingLocation = compile('location\|(.*)\r\n')
        self.MeetingNumber = compile('dialingnumber\|(audio|video)\|([\w;:@.=&+?/\-]+)[|]?(sip|h323)?\r\n')
        self.meetingIDregX = compile('id\|(.*)\r\n')
        self.meetingOrganizerregX = compile('organizer\|(.*)\r\n')

        self.MeetingListRegex = compile(b'calendarmeetings list begin[\s\S]+calendarmeetings list end\r\n')
        self.MeetingOrganizerRegex = compile(b'calendarmeetings info start[\s\S]+calendarmeetings info end\r\n')

        self.PhonebookList = []
        self.PhonebookUIDList = []
        self.PhonebookIndex = 0
        self.PhonebookDelay = 0
        self.PhonebookNavIndex = 1
        self.PhonebookOffset = 50
        self.PhonebookAdvance = False

        self.PhonebookGroupList = []
        self.PhonebookGroupUIDList = []
        self.PhonebookGroupIndex = 0
        self.PhonebookGroupDelay = 0
        self.PhonebookGroupNavIndex = 1
        self.PhonebookGroupOffset = 50
        self.PhonebookGroupAdvance = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'calendarstatus (unavailable|established)'), self._MatchCalendarStatus, None)

            self.AddMatchString(compile(b'callinfo begin[\s\S]+callinfo end\r\n'), self.__MatchCallInfo, None)
            self.AddMatchString(compile(b'hanging up all\r\n'), self.__MatchCallInfoInactive, None)
            self.AddMatchString(compile(b'system is not in a call\r\n'), self.__MatchCallInfoInactive, None)
            self.AddMatchString(compile(b'(callstate registered|active: call|ended: call|(incoming: call)\[\d+\] name\[(.+)\] |dialstr\[(.+)\] state\[(ALLOCATED|RINGING|CONNECTING|COMPLETE)\]|already active:callstate|already active:videostate)'), self.__MatchCallState, None)

            self.AddMatchString(compile(b'(mpautoanswer|autoanswer) (yes|no|donotdisturb)\r\n'), self.__MatchAutoAnswer, None)   # necessary to combine regex
            self.AddMatchString(compile(b'autoshowcontent (on|off)\r\n'), self.__MatchAutoShowContent, None)
            self.AddMatchString(compile(b'lanport (auto|10hdx|10fdx|100hdx|100fdx|1000hdx|1000fdx)\r\n'), self.__MatchLANPortSettings, None)

            self.AddMatchString(compile(b'camera far source (-?\d)\r\n'), self.__MatchCameraFarSource, None)
            self.AddMatchString(compile(b'camera far (-?\d)\r\n'), self.__MatchCameraFarSource, None)
            self.AddMatchString(compile(b'camera near source (-?\d)\r\n'), self.__MatchCameraNearSource, None)
            self.AddMatchString(compile(b'camera near (-?\d)\r\n'), self.__MatchCameraNearSource, None)
            self.AddMatchString(compile(b'camera near tracking (on|off|On|Off|Voice|GroupFrame|FrameGroup|FrameSpeaker|FrameGroupWithTransition)\r\n'), self.__MatchCameraNearTracking, None)
            self.AddMatchString(compile(b'cameratracking near (off|speaker|group|groupwithtransition)\r\n'), self.__MatchCameraNearTrackingMode, None)
            self.AddMatchString(compile(b'camera near position (-?\d+) (-?\d+) (-?\d+)\r\n'), self.__MatchCameraNearPosition, None)
            self.AddMatchString(compile(b'camera near setposition (-?\d+) (-?\d+) (-?\d+)\r\n'), self.__MatchCameraNearPosition, None)

            self.AddMatchString(compile(b'configpresentation monitor([1-3]):([-\w]+)\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'configpresentation monitor([1-3]) ([-\w]+) succeeded\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'configlayout monitor1 (pip_lower_left|pip_lower_right|pip_upper_left|pip_top|pip_right|pip_bottom|side_by_side|full_screen|pip_upper_right)\r\n'), self.__MatchPIPLocation, None)
            self.AddMatchString(compile(b'configdisplay monitor([1-3]) (\w+ \w+ ?\w+)\r\n'), self.__MatchVideoFormatStatus, None)

            self.AddMatchString(compile(b'dualmonitor (yes|no)\r\n'), self.__MatchDualMonitor, None)
            self.AddMatchString(compile(b'mpmode (auto|discussion|presentation|fullscreen)\r\n'), self.__MatchMultipointMode, None)

            self.AddMatchString(compile(b'audiotransmitlevel (-?\d+) ?\r\n'), self.__MatchTransmitLevel, None)
            self.AddMatchString(compile(b'videomute near (on|off)\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'mute near (on|off)\r\n'), self.__MatchTransmitMute, None)
            self.AddMatchString(compile(b'mute far (on|off)\r\n'), self.__MatchMuteFarStatus, None)
            self.AddMatchString(compile(b'volume (\d+)\r\n'), self.__MatchVolume, None)

            self.AddMatchString(compile(b'vcbutton source get ([12346]|none)\r\n'), self.__MatchVideoContentSource, None)
            self.AddMatchString(compile(b'(already active:vcbutton)\r\n|vcbutton (farplay|farstop|stop|play).?\r\n'), self.__MatchPresentationStatus, None)
            self.AddMatchString(compile(b'systemsetting selfview (on|off|auto|On|Off|Auto)\r'), self.__MatchSelfview, None)

            self.AddMatchString(compile(b'sleeptime ([0-9]{1,3})\r\n'), self.__MatchSleepTime, None)
            self.AddMatchString(compile(b'listen (going to sleep|waking up)\r\n'), self.__MatchSleepMode, None)
            self.AddMatchString(compile(b'(sleep registered)\r\n|(already|not) active:sleep\r\n'), self.__MatchSleepRegister, None)

            self.AddMatchString(compile(b'Hi, my name is : '), self.__MatchSuccessLogin, None)
            self.AddMatchString(compile(rb'Software Version:    ([\d.]+)\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(compile(rb'ipaddress\s+([\d\.]+)\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'password failed'), self.__MatchFailedLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'error: (.*)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'\x00'), self.__MatchRebootInitialized, None)

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Needed'
        else:
            self.Authenticated = 'Not Needed'

        self.callhistory = Directory(self._NumberOfCallHistory, 'Number', filler='')
        self.callhistory.write_status_function = self.WriteCallHistorySearchResults

        self.phonebook = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebook_uid = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebook.write_status_function = self.WritePhonebookSearchResult

        self.phonebookGroup = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebookGroup_uid = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebookGroup.write_status_function = self.WritePhonebookGroupSearchResult

        self.CallHistoryRegex = compile(r'\"?([\w\.\,\-\#\@ ]+)\"?[\t ][\/\w]+[\t \d:]+(?:Out|In|Missed)')
        self.CallStateRegex = compile(r'(callstate registered|active: call|ended: call|(incoming: call)\[\d+\] name\[(.+)\] |dialstr\[(.+)\] state\[(ALLOCATED|RINGING|CONNECTING|COMPLETE)\]|already active:callstate|already active:videostate)')

        self.PhonebookRegex = compile(r'\d+\. (.*):(local#.*):site')
        self.PhonebookGroupRegex = compile(r'\d+\. (.*):(local#.*):group')
        self.PhonebookGlobalRegex = compile(r'globaldir \d+\. (.*)\s?:\s?(.*):site')
        self.PhonebookGlobalGroupRegex = compile(r'globaldir \d+\. (.*)\s?:\s?(.*):group')

    def WriteCallHistorySearchResults(self, value, qualifier):
        self.WriteStatus('CallHistorySearchResults', value, qualifier)

    def WritePhonebookSearchResult(self, value, qualifier):
        self.WriteStatus('PhonebookSearchResult', value, qualifier)

    def WritePhonebookGroupSearchResult(self, value, qualifier):
        self.WriteStatus('PhonebookGroupSearchResult', value, qualifier)

    @property
    def MeetingsTimeInterval(self):
        return self._MeetingsTimeInterval

    @MeetingsTimeInterval.setter
    def MeetingsTimeInterval(self, value):
        timeInterval = {
            'One Day' : 0,
            'Five Days' : 5,
            'One Week' : 7
        }

        self._MeetingsTimeInterval = timeInterval[value]

    @property
    def MeetingsTimeFormat(self):
        return self._MeetingsTimeFormat

    @MeetingsTimeFormat.setter
    def MeetingsTimeFormat(self, value):
        timeFormat = {
            '12 Hour' : '%I:%M%p',
            '24 Hour' : '%H:%M'
        }

        self._MeetingsTimeFormat = timeFormat[value]

    @property
    def NumberOfCallHistory(self):
        return self._NumberOfCallHistory

    @NumberOfCallHistory.setter
    def NumberOfCallHistory(self, value):
        self._NumberOfCallHistory = int(value)
        self.callhistory = Directory(self._NumberOfCallHistory, 'Number', filler='')
        self.callhistory.write_status_function = self.WriteCallHistorySearchResults

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = int(value)
        self.phonebook = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebook_uid = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebook.write_status_function = self.WritePhonebookSearchResult

        self.phonebookGroup = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebookGroup_uid = Directory(self._NumberOfPhonebookSearch, 'Number', filler='')
        self.phonebookGroup.write_status_function = self.WritePhonebookGroupSearchResult

    def __MatchRebootInitialized(self, match, qualifier):

        self.Authenticated = 'Needed'

    def __MatchPassword(self, match, qualifier):

        self.Authenticated = 'Prompted'
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchFailedLogin(self, value, qualifier):

        self.Authenticated = 'Failed'
        self.Error(['Log in failed. Please supply proper password'])

    def __MatchSuccessLogin(self, value, qualifier):

        self.Authenticated = 'LoggedIn'
        self.EnableSleepRegister(None, None)

    def __MatchSleepRegister(self, match, tag):

        value1 = match.group(1)
        value2 = match.group(2)
        if value1 == b'sleep registered':
            self.SleepRegister = 'Enabled'
        elif value2 == b'already':
            self.SleepRegister = 'Enabled'
        elif value2 == b'not':
            self.SleepRegister = 'Disabled'

    def EnableSleepRegister(self, value, qualifier):

        self.Send('callstate register\rlisten video\rsleep register\r')

    def SetAutoAnswer(self, value, qualifier):

        if value in ['Yes', 'No', 'Do Not Disturb']:
            self.__SetHelper('AutoAnswer', 'autoanswer {}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):
        self.__UpdateHelper('AutoAnswer', 'autoanswer get\r', qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'yes': 'Yes',
            'no': 'No',
            'donotdisturb': 'Do Not Disturb'
        }

        command = match.group(1).decode()   # autoanswer|mpautoanswer
        value = ValueStateValues[match.group(2).decode()]
        if command == 'autoanswer':
            self.WriteStatus('AutoAnswer', value, None)
        elif command == 'mpautoanswer':
            self.WriteStatus('MultipointAutoAnswer', value, None)

    def SetMultipointAutoAnswer(self, value, qualifier):

        if value in ['Yes', 'No', 'Do Not Disturb']:
            self.__SetHelper('MultipointAutoAnswer', 'mpautoanswer {}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultipointAutoAnswer')

    def UpdateMultipointAutoAnswer(self, value, qualifier):
        self.__UpdateHelper('MultipointAutoAnswer', 'mpautoanswer get\r', qualifier)

    def SetAutoShowContent(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('AutoShowContent', 'autoshowcontent {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoShowContent')

    def UpdateAutoShowContent(self, value, qualifier):
        self.__UpdateHelper('AutoShowContent', 'autoshowcontent get\r', qualifier)

    def __MatchAutoShowContent(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AutoShowContent', value, None)

    def SetCallHistoryNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.callhistory.scroll_up(1)
        elif value == 'Down':
            self.callhistory.scroll_down(1)
        elif value == 'Page Up':
            self.callhistory.scroll_up(self._NumberOfCallHistory)
        elif value == 'Page Down':
            self.callhistory.scroll_down(self._NumberOfCallHistory)
        else:
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistorySelect(self, value, qualifier):

        if 1 <= int(value) <= 10:
            result = self.ReadStatus('CallHistorySearchResults', {'Button': int(value)})
            if result not in ['***End of list***', '***Not Available***']:
                self.SetHook('Dial Auto', {'Number': result})
            else:
                self.Discard('Invalid Command for SetCallHistorySelect')
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')

    def SetCallHistoryUpdate(self, value, qualifier):
        self.Debug = True

        self.callhistory.reset(['Loading...'])
        res = self.SendAndWait('recentcalls\r', 5)
        if res:
            res = res.decode()
            new_list = findall(self.CallHistoryRegex, res)
            call_states = findall(self.CallStateRegex, res)
            for c in call_states:
                self.__MatchCallState(c, 'Update')
            if len(new_list) > 0:
                new_list.append('***End of list***')
                self.callhistory.reset(new_list)
            else:
                self.callhistory.reset(['***Not Available***'])
        else:
            self.callhistory.reset(['***Not Available***'])

    def __MatchCallInfo(self, match, tag):

        res = match.group(0).decode()
        result = findall(self.CallInfoRegex, res)
        self.CallID = []
        self.CallCount = 0
        call = 1

        for res in result:
            state = res[3].title()
            name = res[1]
            number = res[2]
            self.CallID.append(res[0])
            self.WriteStatus('CallInfo', state, {'Call': str(call)})
            self.WriteStatus('CallInfoName', name, {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', number, {'Call': str(call)})
            self.CallCount += 1
            call += 1

        while call <= 5:
            self.WriteStatus('CallInfo', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})
            call += 1

    def __MatchCallInfoInactive(self, match, tag):

        self.CallCount = 0
        self.WriteStatus('CallState', 'Inactive', None)
        self.WriteStatus('CallStateIncomingCallID', '', None)
        for call in range(1, 6):
            self.WriteStatus('CallInfo', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})

    def UpdateCallState(self, value, qualifier):

        self.__UpdateHelper('CallState', 'callinfo all\r', qualifier)

    def __MatchCallState(self, match, tag):

        ValueStateValues = {
            'ALLOCATED': 'Allocated',
            'RINGING': 'Incoming Call',
            'CONNECTING': 'Ringing',
            'COMPLETE': 'Complete',
            'active: call': 'Active',
            'ended: call': 'Inactive',
        }

        value = match.group(1).decode() if not tag else match[0]
        if value in ['callstate registered', 'already active:callstate', 'already active:videostate']:
            self.WriteStatus('CallStateIncomingCallID', '', None)
            self.WriteStatus('CallState', 'Inactive', None)
        elif value == 'active: call':
            self.WriteStatus('CallStateIncomingCallID', '', None)
            self.WriteStatus('CallState', 'Active', None)
        elif value == 'ended: call':
            self.CallCount -= 1
            self.WriteStatus('CallStateIncomingCallID', '', None)
            if self.CallCount <= 0:
                self.WriteStatus('CallState', 'Inactive', None)
        else:
            value1 = match.group(2) if not tag else match[1].encode()
            value2 = match.group(3) if not tag else match[2].encode()
            value3 = match.group(4) if not tag else match[3].encode()
            value4 = match.group(5) if not tag else match[4].encode()
            if value1 == b'incoming: call':
                self.WriteStatus('CallStateIncomingCallID', value2.decode().split(';')[0], None)
                self.WriteStatus('CallState', 'Incoming Call', None)
            else:
                self.WriteStatus('CallStateIncomingCallID', value3.decode().split(';')[0], None)
                self.WriteStatus('CallState', ValueStateValues[value4.decode()], None)

        self.UpdateCallState(None, None)

    def SetCameraFarPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            self.__SetHelper('CameraFarPanTilt', 'camera far move {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarPanTilt')

    def SetCameraFarZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            self.__SetHelper('CameraFarZoom', 'camera far move {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarZoom')

    def SetCameraFarSource(self, value, qualifier):

        if value in ['1', '2', '3', '4']:
            self.__SetHelper('CameraFarSource', 'camera far {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarSource')

    def UpdateCameraFarSource(self, value, qualifier):
        self.__UpdateHelper('CameraFarSource', 'camera far source\r', qualifier)

    def __MatchCameraFarSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Unavailable' if value == '-1' else value
        self.WriteStatus('CameraFarSource', value, None)

    def SetCameraNearPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            self.__SetHelper('CameraNearPanTilt', 'camera near move {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearPanTilt')

    def UpdateCameraNearPanPosition(self, value, qualifier):

        self.__UpdateHelper('CameraNearPanPosition', 'camera near getposition\r', qualifier)

    def __MatchCameraNearPosition(self, match, tag):

        self.WriteStatus('CameraNearPanPosition', int(match.group(1).decode()), None)
        self.WriteStatus('CameraNearTiltPosition', int(match.group(2).decode()), None)
        self.WriteStatus('CameraNearZoomPosition', int(match.group(3).decode()), None)

    def SetCameraNearPosition(self, value, qualifier):

        qualifier = {} if qualifier is None else qualifier
        pan = qualifier.get('Pan', 0)
        tilt = qualifier.get('Tilt', 0)
        zoom = qualifier.get('Zoom', 0)

        if (pan and tilt and zoom) or (pan == 0 and tilt == 0 and zoom == 0):
            self.__SetHelper('CameraNearPosition', 'camera near setposition {} {} {}\r'.format(pan, tilt, zoom), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearPosition')

    def UpdateCameraNearPosition(self, value, qualifier):

        self.__UpdateHelper('CameraNearPanPosition', 'camera near getposition\r', qualifier)

    def SetCameraNearSource(self, value, qualifier):

        if value in self.CameraNearSourceValues:
            self.__SetHelper('CameraNearSource', 'camera near {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearSource')

    def UpdateCameraNearSource(self, value, qualifier):
        self.__UpdateHelper('CameraNearSource', 'camera near source\r', qualifier)

    def __MatchCameraNearSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Unavailable' if value == '-1' else value
        self.WriteStatus('CameraNearSource', value, None)

    def UpdateCameraNearTiltPosition(self, value, qualifier):

        self.UpdateCameraNearPanPosition(value, qualifier)

    def SetCameraNearZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            self.__SetHelper('CameraNearZoom', 'camera near move {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearZoom')

    def UpdateCameraNearZoomPosition(self, value, qualifier):

        self.UpdateCameraNearPanPosition(value, qualifier)

    def SetCameraNearTracking(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('CameraNearTracking', 'camera near tracking {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearTracking')

    def UpdateCameraNearTracking(self, value, qualifier):
        self.__UpdateHelper('CameraNearTracking', 'camera near tracking get\r', qualifier)

    def __MatchCameraNearTracking(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'On': 'On',
            'off': 'Off',
            'Off': 'Off',
            'GroupFrame': 'GroupFrame',
            'FrameGroup': 'GroupFrame',
            'Voice': 'Voice',
            'FrameSpeaker': 'SpeakerFrame',
            'FrameGroupWithTransition': 'GroupFrame with Transition'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CameraNearTracking', value, None)

    def SetCameraNearTrackingMode(self, value, qualifier):

        valueStates = {
            'Speaker': 'speaker',
            'Group': 'group',
            'Group with Transition': 'groupwithtransition',
            'Off': 'off',
        }

        if value in valueStates:
            self.__SetHelper('CameraNearTrackingMode', 'cameratracking near mode {}\r'.format(valueStates[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearTrackingMode')

    def UpdateCameraNearTrackingMode(self, value, qualifier):
        self.__UpdateHelper('CameraNearTrackingMode', 'cameratracking near mode get\r', qualifier)

    def __MatchCameraNearTrackingMode(self, match, tag):

        ValueStateValues = {
            'speaker': 'Speaker',
            'group': 'Group',
            'groupwithtransition': 'Group with Transition',
            'off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CameraNearTrackingMode', value, None)

    def SetCameraPresetFarRecall(self, value, qualifier):

        if 0 <= int(value) <= 15:
            self.__SetHelper('CameraPresetFarRecall', 'preset far go {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFarRecall')

    def SetCameraPresetFarSave(self, value, qualifier):

        if 0 <= int(value) <= 15:
            self.__SetHelper('CameraPresetFarSave', 'preset far set {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFarSave')

    def SetCameraPresetNearRecall(self, value, qualifier):

        if 0 <= int(value) <= 99:
            self.__SetHelper('CameraPresetNearRecall', 'preset near go {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNearRecall')

    def SetCameraPresetNearSave(self, value, qualifier):

        if 0 <= int(value) <= 99:
            self.__SetHelper('CameraPresetNearSave', 'preset near set {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNearSave')

    def SetConfigPresentation(self, value, qualifier):

        mon = qualifier['Monitor']
        if value in ['Near', 'Far', 'Content', 'Near or Far', 'Content or Near', 'Content or Far', 'Content or Fall',
                     'All', 'None', 'Auto', 'Rec All', 'Rec Far or Near'] and mon in ['1', '2', '3']:
            self.__SetHelper('ConfigPresentation', 'configpresentation monitor{} {}\r'.format(mon, value.replace(' ', '-').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigPresentation')

    def UpdateConfigPresentation(self, value, qualifier):

        mon = qualifier['Monitor']
        if mon in ['1', '2', '3']:
            self.__UpdateHelper('ConfigPresentation', 'configpresentation monitor{} get\r'.format(mon), qualifier)
        else:
            self.Discard('Invalid Command for UpdateConfigPresentation')

    def __MatchConfigPresentation(self, match, tag):

        stateValues = {
            'near': 'Near',
            'far': 'Far',
            'content': 'Content',
            'near-or-far': 'Near or Far',
            'content-or-near': 'Content or Near',
            'content-or-far': 'Content or Far',
            'content-or-fall': 'Content or Fall',
            'all': 'All',
            'none': 'None',
            'auto': 'Auto',
            'rec-all': 'Rec All',
            'rec-far-or-near': 'Rec Far or Near',
        }

        value = stateValues[match.group(2).decode()]
        mon = match.group(1).decode()

        self.WriteStatus('ConfigPresentation', value, {'Monitor': mon})

    def SetDialPhonebook(self, value, qualifier):

        qualifier = {} if qualifier is None else qualifier
        name = qualifier.get('Name')
        if name:
            self.__SetHelper('DialPhonebook', 'dial addressbook \"{}\"\r'.format(name), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDialPhonebook')

    def SetDTMF(self, value, qualifier):

        if value in '0123456789#*':
            self.__SetHelper('DTMF', 'gendial {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetDualMonitor(self, value, qualifier):

        if value in ['Yes', 'No']:
            self.__SetHelper('DualMonitor', 'dualmonitor {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDualMonitor')

    def UpdateDualMonitor(self, value, qualifier):
        self.__UpdateHelper('DualMonitor', 'dualmonitor get\r', qualifier)

    def __MatchDualMonitor(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DualMonitor', value, None)

    def UpdateFirmware(self, value, qualifier):

        self.__UpdateHelper('Firmware', 'whoami\r\n', qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetHangup(self, value, qualifier):

        ValueStateValues = {
            '1': 0,
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            'All': 'hangup all\r'
        }

        HangupCmdString = ''
        if value == 'All':
            HangupCmdString = ValueStateValues[value]
        else:
            index = ValueStateValues[value]
            if len(self.CallID) >= int(value):
                HangupCmdString = 'hangup video {0}\r'.format(self.CallID[index])
                self.CallID.pop(index)
            else:
                self.Discard('Invalid Command for SetHangup')
        if HangupCmdString:
            self.__SetHelper('Hangup', HangupCmdString, value, qualifier)

        self.UpdateCallState(None, None)

    def SetHook(self, value, qualifier):
        qualifier = {} if qualifier is None else qualifier

        ValueStateValues = {
            'Answer': 'answer video',
            'Dial 128Kbps': 'dial manual \"128\"',
            'Dial 512Kbps': 'dial manual \"512\"',
            'Dial 832Kbps': 'dial manual \"832\"',
            'Dial 1Mbps': 'dial manual \"1024\"',
            'Dial 1.7Mbps': 'dial manual \"1700\"',
            'Dial 2Mbps': 'dial manual \"2048\"',
            'Dial 3Mbps': 'dial manual \"3072\"',
            'Dial 4Mbps': 'dial manual \"4096\"',
            'Dial 6Mbps': 'dial manual \"6144\"',
            'Dial Auto': 'dial auto',
            'Dial Contact': 'dial addressbook',
            'Dial Global Contact': 'dial addressbook_entry',
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

        if 'Dial' in value:
            if 'Global' in value and self.uidSelected:
                self.__SetHelper('Hook', '{} {}\r'.format(ValueStateValues[value], self.uidSelected), value, qualifier)
            else:
                number = qualifier.get('Number')
                if number:
                    self.__SetHelper('Hook', '{} \"{}\"\r'.format(ValueStateValues[value], number), value, qualifier)
        elif value in ['Hangup 1', 'Hangup 2', 'Hangup 3', 'Hangup 4', 'Hangup 5', 'Hangup  All']:
            HangupCmdString = ''
            if value == 'Hangup All':
                HangupCmdString = ValueStateValues[value]
            else:
                index = ValueStateValues[value]
                if len(self.CallID) >= ValueStateValues[value] + 1:
                    HangupCmdString = 'hangup video {}\r'.format(self.CallID[index])
                    self.CallID.pop(index)
                else:
                    self.Discard('Invalid Command for SetHook')
            if HangupCmdString:
                self.__SetHelper('Hook', HangupCmdString, value, qualifier)
            self.UpdateCallState(None, None)
        elif value in ValueStateValues:
            self.__SetHelper('Hook', '{}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def UpdateIPAddress(self, value, qualifier):

        self.__UpdateHelper('IPAddress', 'ipaddress get\r\n', qualifier)

    def __MatchIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPAddress', value, None)

        if self.SleepRegister == 'Disabled':
            self.EnableSleepRegister(None, None)

    def SetIREmulation(self, value, qualifier):

        if value == 'Call':
            self.__SetHelper('IREmulation', 'button button {0}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        elif value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#', '.', 'Down', 'Left', 'Right', 'Select', 'Up',
                       'Auto', 'Back', 'Far', 'Graphics', 'Hangup', 'Near', 'Mute', 'Volume+', 'Volume-', 'Zoom+', 'Zoom-',
                       'Camera', 'Delete', 'Directory', 'Home', 'Keyboard', 'Period', 'PIP', 'Preset', 'Info', 'Menu']:
            self.__SetHelper('IREmulation', 'button {}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetLANPortSettings(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'auto',
            '10 Mbps, Half Duplex': '10hdx',
            '10 Mbps, Full Duplex': '10fdx',
            '100 Mbps, Half Duplex': '100hdx',
            '100 Mbps, Full Duplex': '100fdx',
            '1000 Mbps, Half Duplex': '1000hdx',
            '1000 Mbps, Full Duplex': '1000fdx'
        }

        if value in ValueStateValues:
            self.__SetHelper('LANPortSettings', 'lanport {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLANPortSettings')

    def UpdateLANPortSettings(self, value, qualifier):

        self.__UpdateHelper('LANPortSettings', 'lanport get\r', qualifier)

    def __MatchLANPortSettings(self, match, tag):

        ValueStateValues = {
            'auto': 'Auto',
            '10hdx': '10 Mbps, Half Duplex',
            '10fdx': '10 Mbps, Full Duplex',
            '100hdx': '100 Mbps, Half Duplex',
            '100fdx': '100 Mbps, Full Duplex',
            '1000hdx': '1000 Mbps, Half Duplex',
            '1000fdx': '1000 Mbps, Full Duplex'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LANPortSettings', value, None)

    def SetMultipointMode(self, value, qualifier):

        val = value.lower()
        if val in ['auto', 'discussion', 'presentation', 'fullscreen']:
            self.__SetHelper('MultipointMode', 'mpmode {}\r'.format(val), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMultipointMode')

    def UpdateMultipointMode(self, value, qualifier):
        self.__UpdateHelper('MultipointMode', 'mpmode get\r', qualifier)

    def __MatchMultipointMode(self, match, tag):
        value = match.group(1).decode().title()
        self.WriteStatus('MultipointMode', value, None)

    def UpdateMuteFarStatus(self, value, qualifier):
        self.__UpdateHelper('MuteFarStatus', 'mute far get\r', qualifier)

    def __MatchMuteFarStatus(self, match, tag):

        valueStates = {
            'on': 'On',
            'off': 'Off',
        }
        value = valueStates[match.group(1).decode()]
        self.WriteStatus('MuteFarStatus', value, None)

    def SetPhonebookGroupNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.PhonebookGroupNavIndex -= 1
            if self.PhonebookGroupNavIndex <= 0:
                self.PhonebookGroupNavIndex = 1
            self.phonebookGroup.scroll_up(1)
            self.phonebookGroup_uid.scroll_up(1)
        elif value == 'Down':
            self.PhonebookGroupNavIndex += 1
            if self.PhonebookGroupNavIndex >= self.PhonebookGroupOffset - self._NumberOfPhonebookSearch and self.PhonebookGroupAdvance is True:
                self.PhonebookGroupIndex = self.PhonebookGroupOffset + 1
                self.PhonebookGroupOffset += 50
                self.PhonebookGroupDelay = 1.0
                self.__SetPhonebookHandler(qualifier, 'Group')
                self.phonebookGroup.scroll_down(self.PhonebookGroupNavIndex)
                self.phonebookGroup_uid.scroll_down(self.PhonebookGroupNavIndex)
            else:
                self.phonebookGroup.scroll_down(1)
                self.phonebookGroup_uid.scroll_down(1)
        elif value == 'Page Up':
            self.PhonebookGroupNavIndex -= self._NumberOfPhonebookSearch
            if self.PhonebookGroupNavIndex <= 0:
                self.PhonebookGroupNavIndex = 1
            self.phonebookGroup.scroll_up(self._NumberOfPhonebookSearch)
            self.phonebookGroup_uid.scroll_up(self._NumberOfPhonebookSearch)
        elif value == 'Page Down':
            self.PhonebookGroupNavIndex += self._NumberOfPhonebookSearch
            if self.PhonebookGroupNavIndex >= self.PhonebookGroupOffset - self._NumberOfPhonebookSearch and self.PhonebookGroupAdvance is True:
                self.PhonebookGroupIndex = self.PhonebookGroupOffset + 1
                self.PhonebookGroupOffset += 50
                self.PhonebookGroupDelay = 3.0
                self.__SetPhonebookHandler(qualifier, 'Group')
                self.phonebookGroup.scroll_down(self.PhonebookGroupNavIndex)
                self.phonebookGroup_uid.scroll_down(self.PhonebookGroupNavIndex)
            else:
                self.phonebookGroup.scroll_down(self._NumberOfPhonebookSearch)
                self.phonebookGroup_uid.scroll_down(self._NumberOfPhonebookSearch)
        else:
            self.Discard('Invalid Command for SetPhonebookGroupNavigation')

    def SetPhonebookGroupSearchSet(self, value, qualifier):
        self.Debug = True

        if 1 <= value <= 15:
            result = self.ReadStatus('PhonebookGroupSearchResult', {'Button': value})
            if result not in ['*** End of List ***', '*** Not Available ***']:
                self.uidGroupSelected = self.phonebookGroup_uid.get_entry(value)
                # TODO search contact
                self.SetPhonebookUpdate(None, {'Phonebook Type': 'Global Grouplist', 'Contact': result})
            else:
                self.Discard('Invalid Command for SetPhonebookGroupSearchSet')
        else:
            self.Discard('Invalid Command for SetPhonebookGroupSearchSet')

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        if value == 'Up':
            self.PhonebookNavIndex -= 1
            if self.PhonebookNavIndex <= 0:
                self.PhonebookNavIndex = 1
            self.phonebook.scroll_up(1)
            self.phonebook_uid.scroll_up(1)
        elif value == 'Down':
            self.PhonebookNavIndex += 1
            if self.PhonebookNavIndex >= self.PhonebookOffset - self._NumberOfPhonebookSearch and self.PhonebookAdvance is True:
                self.PhonebookIndex = self.PhonebookOffset + 1
                self.PhonebookOffset += 50
                self.PhonebookDelay = 1.0
                self.__SetPhonebookHandler(qualifier, 'Site')
                self.phonebook.scroll_down(self.PhonebookNavIndex)
                self.phonebook_uid.scroll_down(self.PhonebookNavIndex)
            else:
                self.phonebook.scroll_down(1)
                self.phonebook_uid.scroll_down(1)
        elif value == 'Page Up':
            self.PhonebookNavIndex -= self._NumberOfPhonebookSearch
            if self.PhonebookNavIndex <= 0:
                self.PhonebookNavIndex = 1
            self.phonebook.scroll_up(self._NumberOfPhonebookSearch)
            self.phonebook_uid.scroll_up(self._NumberOfPhonebookSearch)
        elif value == 'Page Down':
            self.PhonebookNavIndex += self._NumberOfPhonebookSearch
            if self.PhonebookNavIndex >= self.PhonebookOffset - self._NumberOfPhonebookSearch and self.PhonebookAdvance is True:
                self.PhonebookIndex = self.PhonebookOffset + 1
                self.PhonebookOffset += 50
                self.PhonebookDelay = 3.0
                self.__SetPhonebookHandler(qualifier, 'Site')
                self.phonebook.scroll_down(self.PhonebookNavIndex)
                self.phonebook_uid.scroll_down(self.PhonebookNavIndex)
            else:
                self.phonebook.scroll_down(self._NumberOfPhonebookSearch)
                self.phonebook_uid.scroll_down(self._NumberOfPhonebookSearch)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        if 1 <= value <= 15:
            result = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if result not in ['*** End of List ***', '*** Not Available ***']:
                self.uidSelected = self.phonebook_uid.get_entry(value)
                self.Set('Hook', 'Dial Contact', {'Number': result})
            else:
                self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        self.Debug = True
        qualifier = {} if qualifier is None else qualifier
        if 'Phonebook Type' not in qualifier:
            qualifier['Phonebook Type'] = 'Local'

        if 'Contact' not in qualifier:
            qualifier['Contact'] = ''

        self.PhonebookList = []
        self.PhonebookUIDList = []
        self.PhonebookIndex = 0
        self.PhonebookDelay = 0
        self.PhonebookNavIndex = 1
        self.PhonebookOffset = 50
        self.PhonebookAdvance = False

        self.PhonebookGroupList = []
        self.PhonebookGroupUIDList = []
        self.PhonebookGroupIndex = 0
        self.PhonebookGroupDelay = 0
        self.PhonebookGroupNavIndex = 1
        self.PhonebookGroupOffset = 50
        self.PhonebookGroupAdvance = False

        self.__SetPhonebookHandler(qualifier)

    def __SetPhonebookHandler(self, qualifier, update='Both'):

        if update in ['Both', 'Site']:
            self.phonebook.reset(['Loading...'])
        if update in ['Both', 'Group']:
            self.phonebookGroup.reset(['Loading...'])

        if 'Grouplist' not in qualifier['Phonebook Type']:
            @Wait(self.PhonebookDelay)
            def UpdatePhonebookType():
                self.__PhonebookHandler(qualifier, update)
        else:
            self.__PhonebookGrouplistHandler()

    def __PhonebookHandler(self, qualifier, update='Both'):

        searchStr = qualifier.get('Contact', '')
        phonebook = qualifier.get('Phonebook Type')

        if 'Local' in phonebook:
            if self.uidGroupSelected:
                PhonebookCmdString = 'localdir grouplist {}\r'.format(self.uidGroupSelected)
            else:
                PhonebookCmdString = 'localdir "{}" range {} {}\r'.format(searchStr, self.PhonebookIndex, self.PhonebookOffset)
            regex, regexGroup = self.PhonebookRegex, self.PhonebookGroupRegex
        else:
            if self.uidGroupSelected:
                PhonebookCmdString = 'globaldir grouplist {}\r'.format(self.uidGroupSelected)
            else:
                if searchStr:
                    PhonebookCmdString = 'globaldir {} range {} {}\r'.format(searchStr, self.PhonebookIndex, self.PhonebookOffset)
                else:
                    PhonebookCmdString = 'globaldir range {} {}\r'.format(self.PhonebookIndex, self.PhonebookOffset)
            regex, regexGroup = self.PhonebookGlobalRegex, self.PhonebookGlobalGroupRegex

        if PhonebookCmdString:
            res = self.SendAndWait(PhonebookCmdString, 10, deliTag=b'done\r\n')
            if res:
                res = res.decode()
                if update in ['Both', 'Site']:
                    new_list = findall(regex, res)
                    if len(new_list) > 0:
                        temp = list(zip(*new_list))
                        temp_list = list(temp[0])
                        if len(temp_list) < 50:
                            self.PhonebookAdvance = False
                            temp_list.append('*** End of List ***')
                        else:
                            self.PhonebookAdvance = True
                        self.PhonebookList += temp_list
                        self.PhonebookUIDList += list(temp[1])
                        self.phonebook.reset(self.PhonebookList)
                        self.phonebook_uid.reset(self.PhonebookUIDList)
                    else:
                        self.__MatchNoContact(None, 'Site')

                if update in ['Both', 'Group']:
                    new_list = findall(regexGroup, res)
                    if len(new_list) > 0:
                        temp = list(zip(*new_list))
                        temp_list = list(temp[0])
                        if len(temp_list) < 50:
                            self.PhonebookGroupAdvance = False
                            temp_list.append('*** End of List ***')
                        else:
                            self.PhonebookGroupAdvance = True
                        self.PhonebookGroupList += temp_list
                        self.PhonebookGroupUIDList += list(temp[1])
                        self.phonebookGroup.reset(self.PhonebookGroupList)
                        self.phonebookGroup_uid.reset(self.PhonebookGroupUIDList)
                    else:
                        self.__MatchNoContact(None, 'Group')
            else:
                self.__MatchNoContact(None, False)
        else:
            self.Discard('Invalid Command')

    def __PhonebookGrouplistHandler(self):

        uidSelected = ' {}'.format(self.uidGroupSelected) if self.uidGroupSelected else ''
        regex, regexGroup = self.PhonebookGlobalRegex, self.PhonebookGlobalGroupRegex
        res = self.SendAndWait('globaldir grouplist{}\r'.format(uidSelected), 10, deliTag='done\r\n')
        if res:
            res = res.decode()
            new_list = findall(regex, res)
            if len(new_list) > 0:
                temp = list(zip(*new_list))
                temp_list = list(temp[0])
                temp_list.append('*** End of List ***')
                self.PhonebookList += temp_list
                self.PhonebookUIDList += list(temp[1])
                self.phonebook.reset(self.PhonebookList)
                self.phonebook_uid.reset(self.PhonebookUIDList)
            else:
                self.__MatchNoContact(None, 'Site')

            new_list = findall(regexGroup, res)
            if len(new_list) > 0:
                temp = list(zip(*new_list))
                temp_list = list(temp[0])
                temp_list.append('*** End of List ***')
                self.PhonebookGroupList += temp_list
                self.PhonebookGroupUIDList += list(temp[1])
                self.phonebookGroup.reset(self.PhonebookGroupList)
                self.phonebookGroup_uid.reset(self.PhonebookGroupUIDList)
            else:
                self.__MatchNoContact(None, 'Group')
        else:
            self.__MatchNoContact(None, False)

    def __MatchNoContact(self, match, tag=None):

        if not tag or tag == 'Site':
            self.phonebook.reset(['*** Not Available ***'])
            self.phonebook_uid.reset(['*** Not Available ***'])
        if not tag or tag == 'Group':
            self.phonebookGroup.reset(['*** Not Available ***'])
            self.phonebookGroup_uid.reset(['*** Not Available ***'])

    def SetPIPLocation(self, value, qualifier):

        ValueStateValues = {
            'Lower Left': 'pip_lower_left',
            'Lower Right': 'pip_lower_right',
            'Upper Left': 'pip_upper_left',
            'Top': 'pip_top',
            'Right': 'pip_right',
            'Bottom': 'pip_bottom',
            'Side by Side': 'side_by_side',
            'Fullscreen': 'full_screen',
            'Upper Right': 'pip_upper_right'
        }

        if value in ValueStateValues:
            self.__SetHelper('PIPLocation', 'configlayout monitor1 {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPIPLocation')

    def UpdatePIPLocation(self, value, qualifier):

        self.__UpdateHelper('PIPLocation', 'configlayout monitor1 get\r', qualifier)

    def __MatchPIPLocation(self, match, tag):

        ValueStateValues = {
            'pip_lower_left': 'Lower Left',
            'pip_lower_right': 'Lower Right',
            'pip_upper_left': 'Upper Left',
            'pip_upper_right': 'Upper Right',
            'pip_top': 'Top',
            'pip_right': 'Right',
            'pip_bottom': 'Bottom',
            'side_by_side': 'Side by Side',
            'full_screen': 'Fullscreen'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPLocation', value, None)

    def SetReboot(self, value, qualifier):

        self.__SetHelper('Reboot', 'reboot now\r', value, qualifier)

    def SetSelfview(self, value, qualifier):

        stateValues = {
            'On': 'on',
            'Off': 'off',
            'Auto': 'auto'
        }

        if value in stateValues:
            self.__SetHelper('Selfview', 'systemsetting selfview {}\r'.format(stateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfview')

    def UpdateSelfview(self, value, qualifier):

        self.__UpdateHelper('Selfview', 'systemsetting get selfview\r', qualifier)

    def __MatchSelfview(self, match, tag):

        stateValues = {
            'on': 'On',
            'off': 'Off',
            'auto': 'Auto',
            'On': 'On',
            'Off': 'Off',
            'Auto': 'Auto',
        }

        value = stateValues[match.group(1).decode()]
        self.WriteStatus('Selfview', value, None)

    def SetSleepMode(self, value, qualifier):

        ValueStateValues = {
            'Sleep': 'sleep\r',
            'Wake': 'wake\r'
        }

        if value in ValueStateValues:
            SleepModeCmdString = ValueStateValues[value]
            self.__SetHelper('SleepMode', SleepModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepMode')

    def __MatchSleepMode(self, match, tag):

        SleepModeStateValues = {
            'going to sleep': 'Sleep',
            'waking up': 'Wake'
        }

        value = SleepModeStateValues[match.group(1).decode()]
        self.WriteStatus('SleepMode', value, None)

    def SetSleepTime(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '3': '3',
            '10': '10',
            '15': '15',
            '30': '30',
            '45': '45',
            '60': '60',
            '120': '120',
            '240': '240',
            '480': '480'
        }

        if value in ValueStateValues:
            self.__SetHelper('SleepTime', 'sleeptime {}\r'.format(ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTime')

    def UpdateSleepTime(self, value, qualifier):

        self.__UpdateHelper('SleepTime', 'sleeptime get\r', qualifier)

    def __MatchSleepTime(self, match, tag):

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '3': '3',
            '10': '10',
            '15': '15',
            '30': '30',
            '45': '45',
            '60': '60',
            '120': '120',
            '240': '240',
            '480': '480'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SleepTime', value, None)

    def SetTransmitLevel(self, value, qualifier):

        if -20 <= value <= 30:
            self.__SetHelper('TransmitLevel', 'audiotransmitlevel set {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitLevel')

    def UpdateTransmitLevel(self, value, qualifier):
        self.__UpdateHelper('TransmitLevel', 'audiotransmitlevel register\raudiotransmitlevel get\r', qualifier)

    def __MatchTransmitLevel(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('TransmitLevel', value, None)

    def SetTransmitMute(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('TransmitMute', 'mute near {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitMute')

    def UpdateTransmitMute(self, value, qualifier):
        self.__UpdateHelper('TransmitMute', 'mute register\rmute near get\r', qualifier)

    def __MatchTransmitMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('TransmitMute', value, None)

    def SetVideoContentSource(self, value, qualifier):

        if value in self.VideoContentSourceValues:
            self.__SetHelper('VideoContentSource', 'vcbutton play {}\r'.format(value), value, qualifier)
        elif value == 'Stop':
            self.__SetHelper('VideoContentSource', 'vcbutton stop\r', value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoContentSource')

    def UpdateVideoContentSource(self, value, qualifier):
        self.__UpdateHelper('VideoContentSource', 'vcbutton source get\r', qualifier)

    def __MatchVideoContentSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Stop' if value == 'none' else value
        self.WriteStatus('VideoContentSource', value, None)

    def UpdatePresentationStatus(self, value, qualifier):
        self.__UpdateHelper('PresentationStatus', 'vcbutton register\r', qualifier)

    def __MatchPresentationStatus(self, match, tag):

        value = match.group(1)
        if value:
            self.WriteStatus('PresentationStatus', 'Stop', None)
        else:
            valueStates = {
                'farplay': 'Far Site Play',
                'farstop': 'Stop',
                'stop': 'Stop',
                'play': 'Stop'
            }

            value = valueStates[match.group(2).decode()]
            self.WriteStatus('PresentationStatus', value, None)

    def SetVideoMute(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('VideoMute', 'videomute near {}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        self.__UpdateHelper('VideoMute', 'videomute near get\r', qualifier)

    def __MatchVideoMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('VideoMute', value, None)

    def SetVideoFormat(self, value, qualifier):

        MonitorStates = {
            '1': 'monitor1',
            '2': 'monitor2',
            '3': 'monitor3'
        }

        ResolutionStates = {
            '640x480p, 60 Hz': '60hz640x480p',
            '1280x720p, 50 Hz': '50hz1280x720p',
            '1280x720p, 60 Hz': '60hz1280x720p',
            '1280x1024p, 60 Hz': '60hz1280x1024p',
            '1024x768p, 60 Hz': '60hz1024x768p',
            '1920x1080p, 60 Hz': '60hz1920x1080p',
            '1920x1080i, 50 Hz': '50hz1920x1080i',
            '1920x1080i, 60 Hz': '60hz1920x1080i',
            '1920x1080p, 50 Hz': '50hz1920x1080p',
            '1920x1200p, 60 Hz': '60hz1920x1200p'
        }

        ValueStateValues = {
            'VGA': 'vga',
            'DVI': 'dvi',
            'Component': 'component',
            'HDMI': 'hdmi',
            'Off': 'off'
        }
        monitor = MonitorStates[qualifier['Monitor']]
        resolution = ResolutionStates[qualifier['Resolution']]

        if value in ValueStateValues and monitor and resolution:
            if 'Off' == value:
                VideoFormatCmdString = 'configdisplay {} Off\r'.format(monitor)
            else:
                VideoFormatCmdString = 'configdisplay {} {} {}\r'.format(monitor, ValueStateValues[value], resolution)

            self.__SetHelper('VideoFormat', VideoFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoFormat')

    def UpdateVideoFormatStatus(self, value, qualifier):

        valueStates = {
            '1': 'monitor1',
            '2': 'monitor2',
            '3': 'monitor3'
        }

        monitor = qualifier['Monitor']
        if qualifier['Monitor'] in valueStates:
            self.__UpdateHelper('VideoFormatStatus', 'configdisplay {} get\r'.format(valueStates[monitor]), qualifier)
        else:
            self.Discard('Invalid Command for UpdateVideoFormatStatus')

    def __MatchVideoFormatStatus(self, match, tag):

        monitor = match.group(1).decode()
        value = match.group(2).decode().title()
        self.WriteStatus('VideoFormatStatus', value, {'Monitor': monitor})

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 50:
            self.__SetHelper('Volume', 'volume set {}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'volume register\rvolume get\r', qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

    def UpdateCalendarStatus(self, value, qualifier):

        self.__UpdateHelper('CalendarStatus', 'calendarstatus get\r', qualifier)

    def _MatchCalendarStatus(self, match, tag):

        ValueStateValues = {
            'established': 'Established',
            'unavailable': 'Unavailable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CalendarStatus', value, None)

    def UpdateMeetingOrganizer(self, value, qualifier):

        if self.MeetingID:
            for i in range(0, len(self.MeetingID)):
                MeetingOrganizerCmdString = 'calendarmeetings info {0}\r'.format(self.MeetingID[i])
                res = self.SendAndWait(MeetingOrganizerCmdString, 8, deliRex=self.MeetingOrganizerRegex)
                if res:
                    res = res.decode()
                    meetID = findall(self.meetingIDregX, res)
                    organizerID = findall(self.meetingOrganizerregX, res)
                    if meetID:
                        if meetID[0] in self.MeetingID:
                            meetIDIndex = self.MeetingID.index(meetID[0]) + 1
                            organizer = organizerID[0]
                            meetingNumberlist = findall(self.MeetingNumber, res)  # returns tuple list [('video', '733397'), ('audio', '48527')]
                            if meetingNumberlist:
                                MeetingNumberDict = {}
                                for index in meetingNumberlist:
                                    callType = '{} {}'.format(index[0], index[2])
                                    MeetingNumberDict[callType] = index[1]    # converts tuple list to dictionary {'audio': '48527', 'video sip': '733397'}
                                if 'video h323' in MeetingNumberDict:
                                    meetingNumbers = MeetingNumberDict['video h323']
                                elif 'video sip' in MeetingNumberDict:
                                    meetingNumbers = MeetingNumberDict['video sip']
                                elif 'video ' in MeetingNumberDict:
                                    meetingNumbers = MeetingNumberDict['video ']
                                elif 'audio ' in MeetingNumberDict:
                                    meetingNumbers = MeetingNumberDict['audio ']
                                else:
                                    meetingNumbers = 'No Number to dial'
                            else:
                                meetingNumbers = 'No Number to dial'

                            meetingLocation = search(self.MeetingLocation, res)
                            if meetingLocation is None:
                                meetingLocation = ''
                            self.WriteStatus('MeetingOrganizer', organizer, {'Label': meetIDIndex})
                            self.WriteStatus('MeetingNumber', meetingNumbers, {'Label': meetIDIndex})
                            self.WriteStatus('MeetingLocation', meetingLocation.group(1), {'Label': meetIDIndex})
        else:
            self.Discard('Invalid Command for UpdateMeetingOrganizer')

    def UpdateMeetingListQuery(self, value, qualifier):

        a = datetime.now()
        b = a.strftime("%H:%M")
        self.MeetingID = []  # Clear the list for new data

        if self._MeetingsTimeInterval == 0:
            MeetingListCmdString = 'calendarmeetings list Today:{} Tomorrow:23:59\r'.format(b)  # time in 24H format HH:MM
        else:
            c = str(a + timedelta(self._MeetingsTimeInterval)).replace(' ', ':')[:16]
            MeetingListCmdString = 'calendarmeetings list Today:{} {}\r'.format(b, c)
        res = self.SendAndWait(MeetingListCmdString, 4, deliRex=self.MeetingListRegex)
        if res:
            res = res.decode()
            if self.oldres != res:
                meetingList = findall(self.Meeting, res)
                self.meetingIDList = findall(self.Meeting, res)
                if meetingList:
                    Label = 1
                    for name in meetingList[0:5]:
                        dt = datetime.strptime(name[1], "%Y-%m-%d:%H:%M")  # sort date from response to format Year|Month|Day|Hour|Minute
                        self.MeetingID.append(name[0])  # Store ID to list
                        startTime = dt.strftime(self.MeetingTimeFormat)  # Convert Military time and keep only the Hour and Minute
                        startTimeExpanded = dt.strftime("%a {}".format(self.MeetingTimeFormat))  # Convert Military time and keep only the Hour and Minute

                        dt = datetime.strptime(name[2], "%Y-%m-%d:%H:%M")  # get meeting end time and sort time
                        endTime = dt.strftime(self.MeetingTimeFormat)  # Convert Military time and keep only the Hour and Minute
                        endTimeExpanded = dt.strftime(self.MeetingTimeFormat)  # Convert Military time and keep only the Hour and Minute

                        self.WriteStatus('MeetingStart', startTime, {'Label': int(Label)})
                        self.WriteStatus('MeetingEnd', endTime, {'Label': int(Label)})
                        self.WriteStatus('MeetingSubject', name[3], {'Label': int(Label)})
                        self.WriteStatus('MeetingTimeCombined', '{}-{}'.format(startTimeExpanded, endTimeExpanded), {'Label': int(Label)})
                        Label += 1

                    clearBtn = Label  # Update labels and clear older entries if new entries are less then before
                    for emptyBtn in range(clearBtn, 6):
                        self.WriteStatus('MeetingStart', '', {'Label': emptyBtn})  # Clear Old Meetings Start
                        self.WriteStatus('MeetingEnd', '', {'Label': emptyBtn})  # Clear Old Meetings End
                        self.WriteStatus('MeetingTimeCombined', '', {'Label': emptyBtn})  # Clear Old Meetings Start
                        self.WriteStatus('MeetingSubject', '', {'Label': emptyBtn})  # Clear Old Meetings Subject
                        self.WriteStatus('MeetingOrganizer', '', {'Label': emptyBtn})  # Clear Old Meeting Organizer
                        self.WriteStatus('MeetingNumber', '', {'Label': emptyBtn})  # Clear Old Meeting Number
                        self.WriteStatus('MeetingLocation', '', {'Label': emptyBtn})  # Clear Old Location

                    self.oldres = res
                    self.UpdateMeetingOrganizer(None, None)
                else:
                    for Label in range(1, 6):
                        self.WriteStatus('MeetingStart', '', {'Label': int(Label)})  # Clear Old Meetings Start
                        self.WriteStatus('MeetingEnd', '', {'Label': int(Label)})  # Clear Old Meetings End
                        self.WriteStatus('MeetingTimeCombined', '', {'Label': int(Label)})  # Clear Old Meetings Start
                        self.WriteStatus('MeetingSubject', '', {'Label': int(Label)})  # Clear Old Meetings Subject
                        self.WriteStatus('MeetingOrganizer', '', {'Label': int(Label)})  # Clear Old Meeting info
                        self.WriteStatus('MeetingNumber', '', {'Label': int(Label)})  # Clear Old Meeting Number
                        self.WriteStatus('MeetingLocation', '', {'Label': int(Label)})  # Clear Old Location
                    self.oldres = ''
        else:
            for Label in range(1, 6):
                self.WriteStatus('MeetingStart', '', {'Label': int(Label)})  # Clear Old Meetings Start
                self.WriteStatus('MeetingEnd', '', {'Label': int(Label)})  # Clear Old Meetings End
                self.WriteStatus('MeetingTimeCombined', '', {'Label': int(Label)})  # Clear Old Meetings Start
                self.WriteStatus('MeetingSubject', '', {'Label': int(Label)})  # Clear Old Meetings Subject
                self.WriteStatus('MeetingOrganizer', '', {'Label': int(Label)})  # Clear Old Meeting info
                self.WriteStatus('MeetingNumber', '', {'Label': int(Label)})  # Clear Old Meeting Number
                self.WriteStatus('MeetingLocation', '', {'Label': int(Label)})  # Clear Old Location
            self.oldres = ''

    def SetMeetingRefresh(self, value, qualifier):

        self.UpdateMeetingListQuery(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['LoggedIn', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                sleepState = self.ReadStatus('SleepMode', None)
                if sleepState == 'Sleep' and command != 'CallInfo':
                    self.Discard('Inappropriate Command ' + command)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchError(self, match, tag):
        self.counter = 0
        if 'There is no tracking camera' in match.group(0).decode():
            self.WriteStatus('CameraNearTracking', 'Off', None)
        else:
            self.Error([match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Needed'
        else:
            self.Authenticated = 'Not Needed'

        self.oldres = ''
        self.uidSelected = ''
        self.uidGroupSelected = ''

        self.SleepRegister = 'Disabled'

    def poly_12_385_300_500(self):

        self.CameraNearSourceValues = {
            '1': '1',
            '2': '2',
        }

        self.VideoContentSourceValues = {
            '1': '1',
            '2': '2',
            '6': '6',
        }

    def poly_12_385_700(self):

        self.CameraNearSourceValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }

        self.VideoContentSourceValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '6': '6',
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


def UseAutoUpdate(func):
    def wrapper(self, *args, **kwargs):
        res = func(self, *args, **kwargs)
        if self.auto_update:
            self.write_to_driver()
        return res
    return wrapper


class Directory:

    def __init__(self, display_count, qualifier, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Button'
        self._qualifier_type = qualifier

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

    def write_to_driver(self):

        for index, entry in enumerate(self.get_displayed_entries()):
            if self._qualifier_type == 'Number':
                position_value = index + 1
            else:
                position_value = str(index + 1)
            self.write_status_function(self.entry_function(entry[0]), {self.qualifier_name: position_value})

    def write_status_function(self, value, qualifier):
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