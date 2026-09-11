from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
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
        self.Models = {}
        
        self.Debug = False

        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallInfo': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoName': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoNumber': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoQuery': {'Status': {}},
            'CallState': {'Status': {}},
            'CallStateIncomingCallID': {'Status': {}},
            'CallType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFarPanTilt': {'Status': {}},
            'CameraFarSource': {'Status': {}},
            'CameraFarZoom': {'Status': {}},
            'CameraNearPanTilt': {'Status': {}},
            'CameraNearSource': {'Status': {}},
            'CameraNearTracking': {'Status': {}},
            'CameraNearZoom': {'Status': {}},
            'CameraPresetFarRecall': {'Status': {}},
            'CameraPresetFarSave': {'Status': {}},
            'CameraPresetNearRecall': {'Status': {}},
            'CameraPresetNearSave': {'Status': {}},
            'ConfigPresentation': {'Parameters': ['Monitor'], 'Status': {}},
            'DialPhonebook': {'Status': {}},
            'DualMonitor': {'Status': {}},
            'FarSiteContent': {'Status': {}},
            'Firmware': {'Status': {}},
            'IREmulation': {'Status': {}},
            'MaxTimeInCall': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PhoneDTMF': {'Status': {}},
            'PhoneHook': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PictureInPictureLocation': {'Status': {}},
            'Reboot': {'Status': {}},
            'SleepMode': {'Status': {}},
            'SleepTime': {'Status': {}},
            'TransmitLevel': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VideoContentSource': {'Status': {}},
            'Hook': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.StartingEntry = 1
        self.EndEntry = 5
        self.Advance = True
        self.lastCallState = 0

        self._NumberOfPhonebookSearch = 5
        self.stat = compile('callinfo:(.*):(.*):(.*):.*:(.*):(muted|notmuted):.*:(\w*call|\w*only)\r\n')
        self.dirName = compile('name:\"(.*)\" sys_label')
        self.gdsName = compile('gaddrbook \d+. "([^"]+)" ')
        self.prevSearchString = '-1'
        self.prevSearchResult = ''
        self.SleepRegister = 'Disabled'
        self.nameList = []
        self.CallID = []

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(callstate registered|active: call|ended: call|(incoming: call)\[\d+\] name\[(.+)\] |dialstr\[(.+)\] state\[(ALLOCATED|RINGING|BONDING|COMPLETE)\])'), self.__MatchCallState, None)
            self.AddMatchString(compile(b'callinfo begin[\s\S]+callinfo end\r\n'), self.__MatchCallInfo, None)
            self.AddMatchString(compile(b'system is not in a call\r\n'), self.__MatchCallInfoInactive, None)
            self.AddMatchString(compile(b'contentvideoadjustment (normal|stretch|zoom)\r\n'), self.__MatchAspectRatio, None)
            self.AddMatchString(compile(b'autoanswer (yes|no|donotdisturb)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'camera far source (-?\d)\r\n'), self.__MatchCameraFarSource, None)
            self.AddMatchString(compile(b'camera near source (-?\d)\r\n'), self.__MatchCameraNearSource, None)
            self.AddMatchString(compile(b'camera near tracking (\w+)\r\n'), self.__MatchCameraNearTracking, None)
            self.AddMatchString(compile(b'configpresentation monitor(1|2):([-\w]+)\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'configpresentation monitor(1|2) ([-\w]+) succeeded\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'dualmonitor (yes|no) ?\r\n'), self.__MatchDualMonitor, None)
            self.AddMatchString(compile(b'Control event: vcbutton far(stop|play) \r\n'), self.__MatchFarSiteContent, None)
            self.AddMatchString(compile(b'maxtimeincall (\d+)\r\n'), self.__MatchMaxTimeInCall, None)
            self.AddMatchString(compile(b'pip (on|off|camera)\r\n'), self.__MatchPictureInPicture, None)
            self.AddMatchString(compile(b'pip is (on|off|camera)\r\n'), self.__MatchPictureInPicture, None)
            self.AddMatchString(compile(b'pip location get ([0-3])\r\n'), self.__MatchPictureInPictureLocation, None)
            self.AddMatchString(compile(b'pip location ([0-3])\r\n'), self.__MatchPictureInPictureLocation, None)
            self.AddMatchString(compile(b'listen (going to sleep|waking up)\r\n'), self.__MatchSleepMode, None)
            self.AddMatchString(compile(b'sleeptime (0|1|3|15|30|60|120|240|480) ?\r\n'), self.__MatchSleepTime, None)
            self.AddMatchString(compile(b'audiotransmitlevel (-?\d+) ?\r\n'), self.__MatchTransmitLevel, None)
            self.AddMatchString(compile(b'mute near (on|off)\r\n'), self.__MatchTransmitMute, None)
            self.AddMatchString(compile(b'vcbutton source get (2|3|4|5|none)\r\n'), self.__MatchVideoContentSource, None)
            self.AddMatchString(compile(b'volume (\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'gaddrbook names search .* \d+ \d+ not supported\.\r\n'), self.__MatchNoContact, None)
            self.AddMatchString(compile(b'vcbutton registered\r\n'), self.__MatchFarSiteContentRegister, None)
            self.AddMatchString(compile(b'info: event/notification already active:vcbutton\r\n'), self.__MatchFarSiteContentRegister, None)
            self.AddMatchString(compile(b'info: event/notification (already|not) active:sleep\r\n'), self.__MatchSleepRegister, None)
            self.AddMatchString(compile(b'error: (.*)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'Password:\r\r\n'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'firmwareversion,(.*)\r\n'), self.__MatchFirmware, None)
            self.AddMatchString(compile(b'Hi, my name is :.*\r\n'), self.__MatchSuccess, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = value

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchSuccess(self, match, tag):
        self.SetEcho(None, None)
        if self.SleepRegister == 'Disabled':
            self.EnableSleepRegister(None, None)

    def SetEcho(self, value, qualifier):
        self.Send('cmdecho off\r')

    def EnableSleepRegister(self, value, qualifier):

        self.Send('sleep register\r')

    def __MatchSleepRegister(self, match, tag):

        if match.group(1).decode() == 'already':
            self.SleepRegister = 'Enabled'
        if match.group(1).decode() == 'not':
            self.SleepRegister = 'Disabled'

    def SetAspectRatio(self, value, qualifier):

        if value in ['Normal', 'Stretch', 'Zoom']:
            AspectRatioCmdString = 'contentvideoadjustment {0}\r'.format(value.lower())
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetAspectRatio'])

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'contentvideoadjustment get\r'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('AspectRatio', value, None)

    def SetAutoAnswer(self, value, qualifier):

        if value in ['Yes', 'No', 'Do Not Disturb']:
            AutoAnswerCmdString = 'autoanswer {0}\r'.format(value.replace(' ', '').lower())
            self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetAutoAnswer'])

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'autoanswer get\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        value = match.group(1).decode()
        value = 'Do Not Disturb' if value == 'donotdisturb' else value.title()
        self.WriteStatus('AutoAnswer', value, None)

    def UpdateCallInfoQuery(self, value, qualifier):
        self.__UpdateHelper('CallInfoQuery', 'callinfo all\r', value, qualifier)

    def __MatchCallInfo(self, match, tag):

        result = findall(self.stat, match.group(0).decode())
        self.CallID = []

        call = 1
        for res in result:
            state = res[3].title()
            name = res[1]
            number = res[2]
            self.CallID.append(res[0])
            self.WriteStatus('CallInfo', state, {'Call': str(call)})
            type = 'Video' if 'video' in res[3] else 'Audio'
            self.WriteStatus('CallType', type, {'Call': str(call)})
            self.WriteStatus('CallInfoName', name, {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', number, {'Call': str(call)})
            call += 1

        while call <= 5:
            self.WriteStatus('CallInfo', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallType', 'Unavailable', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})
            call += 1

    def __MatchCallInfoInactive(self, match, tag):
        for call in range(1, 6):
            self.WriteStatus('CallInfo', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallType', 'Unavailable', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})

    def UpdateCallState(self, value, qualifier):

        CallStateCmdString = 'callstate unregister\r'
        self.Send(CallStateCmdString)
        CallStateCmdString = 'callstate register\r'
        self.__UpdateHelper('CallState', CallStateCmdString, value, qualifier)

    def __MatchCallState(self, match, tag):

        ValueStateValues = {
            'ALLOCATED': 'Allocated',
            'RINGING': 'Ringing',
            'BONDING': 'Ringing',
            'COMPLETE': 'Complete',
            'active: call': 'Active',
            'ended: call': 'Inactive',
        }

        value = match.group(1).decode()
        if value == 'callstate registered':
            self.WriteStatus('CallStateIncomingCallID', '', None)
            self.WriteStatus('CallState', 'Inactive', None)
        elif value in ['active: call', 'ended: call']:
            self.WriteStatus('CallStateIncomingCallID', '', None)
            self.WriteStatus('CallState', ValueStateValues[value], None)
        else:
            value1 = match.group(2)
            value2 = match.group(3)
            value3 = match.group(4)
            value4 = match.group(5)
            if value1 == b'incoming: call':
                self.WriteStatus('CallStateIncomingCallID', value2.decode(), None)
                self.WriteStatus('CallState', 'Incoming Call', None)
            else:
                self.WriteStatus('CallStateIncomingCallID', value3.decode(), None)
                self.WriteStatus('CallState', ValueStateValues[value4.decode()], None)

    def SetCameraFarPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            CameraFarPanTiltCmdString = 'camera far move {0}\r'.format(value.lower())
            self.__SetHelper('CameraFarPanTilt', CameraFarPanTiltCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraFarPanTilt'])

    def SetCameraFarSource(self, value, qualifier):

        if value in ['1', '2', '3', '4']:
            CameraFarSourceCmdString = 'camera far {0}\r'.format(value)
            self.__SetHelper('CameraFarSource', CameraFarSourceCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraFarSource'])

    def UpdateCameraFarSource(self, value, qualifier):

        CameraFarSourceCmdString = 'camera far source\r'
        self.__UpdateHelper('CameraFarSource', CameraFarSourceCmdString, value, qualifier)

    def __MatchCameraFarSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Unavailable' if value == '-1' else value
        self.WriteStatus('CameraFarSource', value, None)

    def SetCameraFarZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            CameraFarZoomCmdString = 'camera far move {0}\r'.format(value.lower())
            self.__SetHelper('CameraFarZoom', CameraFarZoomCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraFarZoom'])

    def SetCameraNearPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            CameraNearPanTiltCmdString = 'camera near move {0}\r'.format(value.lower())
            self.__SetHelper('CameraNearPanTilt', CameraNearPanTiltCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraNearPanTilt'])

    def SetCameraNearSource(self, value, qualifier):

        if value in ['1', '2', '3', '4', '6']:
            CameraNearSourceCmdString = 'camera near {0}\r'.format(value)
            self.__SetHelper('CameraNearSource', CameraNearSourceCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraNearSource'])

    def UpdateCameraNearSource(self, value, qualifier):

        CameraNearSourceCmdString = 'camera near source\r'
        self.__UpdateHelper('CameraNearSource', CameraNearSourceCmdString, value, qualifier)

    def __MatchCameraNearSource(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CameraNearSource', value, None)

    def SetCameraNearTracking(self, value, qualifier):

        if value in ['On', 'Off']:
            CameraNearTrackingCmdString = 'camera near tracking {0}\r'.format(value.lower())
            self.__SetHelper('CameraNearTracking', CameraNearTrackingCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraNearTracking'])

    def UpdateCameraNearTracking(self, value, qualifier):

        CameraNearTrackingCmdString = 'camera near tracking get\r'
        self.__UpdateHelper('CameraNearTracking', CameraNearTrackingCmdString, value, qualifier)

    def __MatchCameraNearTracking(self, match, tag):

        value = match.group(1).decode().title()
        if value in ['On', 'Off', 'Voice']:
            self.WriteStatus('CameraNearTracking', value, None)

    def SetCameraNearZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            CameraNearZoomCmdString = 'camera near move {0}\r'.format(value.lower())
            self.__SetHelper('CameraNearZoom', CameraNearZoomCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraNearZoom'])

    def SetCameraPresetFarRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 15
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetFarRecallCmdString = 'preset far go {0}\r'.format(value)
            self.__SetHelper('CameraPresetFarRecall', CameraPresetFarRecallCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraPresetFarRecall'])

    def SetCameraPresetFarSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 15
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetFarSaveCmdString = 'preset far set {0}\r'.format(value)
            self.__SetHelper('CameraPresetFarSave', CameraPresetFarSaveCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraPresetFarSave'])

    def SetCameraPresetNearRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetNearRecallCmdString = 'preset near go {0}\r'.format(value)
            self.__SetHelper('CameraPresetNearRecall', CameraPresetNearRecallCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraPresetNearRecall'])

    def SetCameraPresetNearSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetNearSaveCmdString = 'preset near set {0}\r'.format(value)
            self.__SetHelper('CameraPresetNearSave', CameraPresetNearSaveCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetCameraPresetNearSave'])

    def SetConfigPresentation(self, value, qualifier):

        mon = qualifier['Monitor']
        if value in ['Near', 'Far', 'Content', 'Near Or Far', 'Content Or Near', 'Content Or Far', 'All', 'None'] and mon in ['1', '2']:
            ConfigPresentationCmdString = 'configpresentation monitor{0} {1}\r'.format(mon, value.replace(' ', '-').lower())
            self.__SetHelper('ConfigPresentation', ConfigPresentationCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetConfigPresentation'])

    def UpdateConfigPresentation(self, value, qualifier):

        mon = qualifier['Monitor']
        if mon in ['1', '2']:
            ConfigPresentationCmdString = 'configpresentation monitor{0} get\r'.format(mon)
            self.__UpdateHelper('ConfigPresentation', ConfigPresentationCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for UpdateConfigPresentation'])

    def __MatchConfigPresentation(self, match, tag):

        qualifier = {}
        qualifier['Monitor'] = match.group(1).decode()
        value = match.group(2).decode().title().replace('-', ' ')
        self.WriteStatus('ConfigPresentation', value, qualifier)

    def SetDialPhonebook(self, value, qualifier):

        name = value
        if name:
            DialPhonebookCmdString = 'dial addressbook \"{0}\"\r'.format(name)
            self.__SetHelper('DialPhonebook', DialPhonebookCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for DialPhonebook'])

    def SetDualMonitor(self, value, qualifier):

        if value in ['Yes', 'No']:
            DualMonitorCmdString = 'dualmonitor {0}\r'.format(value.lower())
            self.__SetHelper('DualMonitor', DualMonitorCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetDualMonitor'])

    def UpdateDualMonitor(self, value, qualifier):

        DualMonitorCmdString = 'dualmonitor get\r'
        self.__UpdateHelper('DualMonitor', DualMonitorCmdString, value, qualifier)

    def __MatchDualMonitor(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('DualMonitor', value, None)

    def UpdateFarSiteContent(self, value, qualifier):

        FarSiteContentCmdString = 'vcbutton register\r'
        self.__UpdateHelper('FarSiteContent', FarSiteContentCmdString, value, qualifier)

    def __MatchFarSiteContent(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('FarSiteContent', value, None)

    def __MatchFarSiteContentRegister(self, match, tag):

        self.WriteStatus('FarSiteContent', 'Registered', None)

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = 'exportprofile\r\n'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmware', value, None)

    def SetIREmulation(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#', '.',
                     'Down', 'Left', 'Right', 'Select', 'Up', 'Auto', 'Back', 'Call', 'Far',
                     'Graphics', 'Hangup', 'Near', 'Help', 'Mute', 'Volume+', 'Volume-',
                     'Zoom+', 'Zoom-', 'Picked Up', 'Put Down', 'Camera', 'Delete', 'Directory',
                     'Home', 'Keyboard', 'Period', 'PIP', 'Preset', 'Info', 'Menu', 'Slides',
                     'Option', 'MMStop', 'MMPlay', 'MMPause', 'MMRecord', 'MMForward', 'MMRewind']:

            IREmulationCmdString = 'button {0}\r'.format(value.replace(' ', '').lower())
            self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetIREmulation'])

    def SetMaxTimeInCall(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 2880
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MaxTimeInCallCmdString = 'maxtimeincall set {0}\r'.format(value)
            self.__SetHelper('MaxTimeInCall', MaxTimeInCallCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetMaxTimeInCall'])

    def UpdateMaxTimeInCall(self, value, qualifier):

        MaxTimeInCallCmdString = 'maxtimeincall get\r'
        self.__UpdateHelper('MaxTimeInCall', MaxTimeInCallCmdString, value, qualifier)

    def __MatchMaxTimeInCall(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('MaxTimeInCall', value, None)

    def SetPhonebookNavigation(self, value, qualifier):

        self.Debug = True
        
        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and len(self.nameList) > 0:
            if 'Page' in value:
                NumberOfAdvance = self._NumberOfPhonebookSearch
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.Advance:
                    self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self._NumberOfPhonebookSearch - 1

            numOfName = len(self.nameList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < numOfName and index < self.EndEntry:
                name = self.nameList[index]
                self.WriteStatus('PhonebookSearchResult', name, {'Button': button})
                button += 1
                index += 1

            if button <= self._NumberOfPhonebookSearch:
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
                button += 1
                for i in range(button, int(self._NumberOfPhonebookSearch) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
        else:
            self.Error(['Invalid Command for SetPhonebookNavigation'])

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        ButtonConstraints = {
            'Min': 1,
            'Max': self._NumberOfPhonebookSearch
        }
        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max']:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number is None:
                number = ''
            if number != '***End of list***' and number != '':
                self.__SetHelper('PhoneHook', 'dial addressbook \"{0}\"\r'.format(number), value, qualifier)
        else:
            self.Error(['Invalid Command for SetPhonebookSearchSet'])

    def SetPhonebookUpdate(self, value, qualifier):
        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
        self.Debug = True
        type_ = qualifier['Phonebook Type']
        searchStr = value
        if searchStr is None:
            searchStr = ''
        if type_ == 'Global GDS':
            if self.prevSearchString != searchStr:
                self.prevSearchString = searchStr
            if searchStr:
                PhonebookUpdateCmdString = 'gaddrbook batch search \"{0}\" \"80\"\r'.format(searchStr)
            else:
                PhonebookUpdateCmdString = 'gaddrbook all\r'
            res = self.SendAndWait(PhonebookUpdateCmdString, 10, deliTag=b'done\r\n')
            if res:
                res = res.decode()
                self.nameList = findall(self.gdsName, res)
                numOfName = len(self.nameList)
                index = self.StartingEntry - 1
                button = 1
                self.Advance = True
                while index < numOfName and index < self.EndEntry:
                    name = self.nameList[index]
                    self.WriteStatus('PhonebookSearchResult', name, {'Button': int(button)})
                    button += 1
                    index += 1

                if button <= self._NumberOfPhonebookSearch:
                    self.Advance = False
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for i in range(button, int(self._NumberOfPhonebookSearch) + 1):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
            else:
                self.__MatchNoContact(None, None)
        else:
            if type_ == 'Local':
                PhonebookUpdateCmdString = 'addrbook names search \"{0}\" all\r'.format(searchStr)
            elif type_ == 'Global LDAP':
                PhonebookUpdateCmdString = 'gaddrbook names search \"{0}\" all\r'.format(searchStr)
            res = self.SendAndWait(PhonebookUpdateCmdString, 10, deliTag=b'done\r\n')
            if res:
                res = res.decode()
                self.nameList = findall(self.dirName, res)
                button = 1
                self.Advance = True
                for name in self.nameList:
                    self.WriteStatus('PhonebookSearchResult', name, {'Button': int(button)})
                    button += 1

                if button <= self._NumberOfPhonebookSearch:
                    self.Advance = False
                    self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for i in range(button, int(self._NumberOfPhonebookSearch) + 1):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
            else:
                self.__MatchNoContact(None, None)

    def SetPhoneDTMF(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            PhoneDTMFCmdString = 'gendial {0}\r'.format(value)
            self.__SetHelper('PhoneDTMF', PhoneDTMFCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetPhoneDTMF'])

    def SetPhoneHook(self, value, qualifier):

        ValueStateValues = {
            'Dial': 'dial phone',
            'Dial Pots': 'dial phone pots',
            'Dial ISDN Phone': 'dial phone isdn_phone',
            'Dial SIP Speakerphone': 'dial phone sip_speakerphone',
            'Flash': 'phone flash',
            'Answer': 'answer phone',
            'Hangup': 'hangup phone',
            'Hangup All': 'hangup all',
        }

        if 'Dial' in value:
            num = qualifier['Number']
            if num:
                PhoneHookCmdString = '{0} \"{1}\"\r'.format(ValueStateValues[value], num)
                self.__SetHelper('PhoneHook', PhoneHookCmdString, value, qualifier)
        elif value in ValueStateValues:
            PhoneHookCmdString = '{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('PhoneHook', PhoneHookCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetPhoneHook'])

    def __MatchNoContact(self, match, tag):
        button = 1
        self.Advance = False
        self.WriteStatus('PhonebookSearchResult', '***Not Available***', {'Button': button})
        button += 1
        for i in range(button, int(self._NumberOfPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPictureInPicture(self, value, qualifier):

        if value in ['On', 'Off', 'Camera', 'Swap']:
            PictureInPictureCmdString = 'pip {0}\r'.format(value.lower())
            self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetPictureInPicture'])

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureCmdString = 'pip get\r'
        self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def __MatchPictureInPicture(self, match, tag):

        value = match.group(1).decode().title()
        if value in ['On', 'Off', 'Camera']:
            self.WriteStatus('PictureInPicture', value, None)

    def SetPictureInPictureLocation(self, value, qualifier):

        ValueStateValues = {
            'Bottom Right': '0',
            'Top Right': '1',
            'Top Left': '2',
            'Bottom Left': '3'
        }

        if value in ValueStateValues:
            PictureInPictureLocationCmdString = 'pip location {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('PictureInPictureLocation', PictureInPictureLocationCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetPictureInPictureLocation'])

    def UpdatePictureInPictureLocation(self, value, qualifier):

        PictureInPictureLocationCmdString = 'pip location get\r'
        self.__UpdateHelper('PictureInPictureLocation', PictureInPictureLocationCmdString, value, qualifier)

    def __MatchPictureInPictureLocation(self, match, tag):

        ValueStateValues = {
            b'0': 'Bottom Right',
            b'1': 'Top Right',
            b'2': 'Top Left',
            b'3': 'Bottom Left'
        }

        value = ValueStateValues[match.group(1)]
        self.WriteStatus('PictureInPictureLocation', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'reboot now\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetSleepMode(self, value, qualifier):

        ValueStateValues = {
            'Sleep': 'sleep\r',
            'Wake': 'wake\r'
        }
        if value in ValueStateValues:
            SleepModeCmdString = ValueStateValues[value]
            self.__SetHelper('SleepMode', SleepModeCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetSleepMode'])

    def __MatchSleepMode(self, match, tag):

        SleepModeStateValues = {
            'going to sleep': 'Sleep',
            'waking up': 'Wake'
        }

        value = SleepModeStateValues[match.group(1).decode()]
        self.WriteStatus('SleepMode', value, None)

    def SetSleepTime(self, value, qualifier):

        if value in ["0", "1", "3", "15", "30", "60", "120", "240", "480"]:
            SleepTimeCmdString = 'sleeptime {0}\r'.format(value)
            self.__SetHelper('SleepTime', SleepTimeCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetSleepTime'])

    def UpdateSleepTime(self, value, qualifier):

        SleepTimeCmdString = 'sleeptime get\r'
        self.__UpdateHelper('SleepTime', SleepTimeCmdString, value, qualifier)

    def __MatchSleepTime(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SleepTime', value, None)

    def SetTransmitLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -20,
            'Max': 30
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TransmitLevelCmdString = 'audiotransmitlevel set {0}\r'.format(value)
            self.__SetHelper('TransmitLevel', TransmitLevelCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetTransmitLevel'])

    def UpdateTransmitLevel(self, value, qualifier):

        TransmitLevelCmdString = 'audiotransmitlevel get\r'
        self.__UpdateHelper('TransmitLevel', TransmitLevelCmdString, value, qualifier)

    def __MatchTransmitLevel(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('TransmitLevel', value, None)

    def SetTransmitMute(self, value, qualifier):

        if value in ['On', 'Off']:
            TransmitMuteCmdString = 'mute near {0}\r'.format(value.lower())
            self.__SetHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetTransmitMute'])

    def UpdateTransmitMute(self, value, qualifier):

        TransmitMuteCmdString = 'mute near get\r'
        self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def __MatchTransmitMute(self, match, tag):

        value = match.group(1).decode().title()
        self.WriteStatus('TransmitMute', value, None)

    def SetVideoContentSource(self, value, qualifier):

        if value in ['2', '3', '4', '5']:
            VideoContentSourceCmdString = 'vcbutton play {0}\r'.format(value)
            self.__SetHelper('VideoContentSource', VideoContentSourceCmdString, value, qualifier)
        elif value == 'Stop':
            VideoContentSourceCmdString = 'vcbutton stop\r'
            self.__SetHelper('VideoContentSource', VideoContentSourceCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetVideoContentSource'])

    def UpdateVideoContentSource(self, value, qualifier):

        VideoContentSourceCmdString = 'vcbutton source get\r'
        self.__UpdateHelper('VideoContentSource', VideoContentSourceCmdString, value, qualifier)

    def __MatchVideoContentSource(self, match, tag):

        value = match.group(1).decode()
        value = 'Stop' if value == 'none' else value
        self.WriteStatus('VideoContentSource', value, None)

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Dial 256kbps' : 'dial manual \"256\"',
            'Dial 128kbps' : 'dial manual \"128\"',
            'Dial 384kbps' : 'dial manual \"384\"',
            'Dial 512kbps' : 'dial manual \"512\"',
            'Dial 1Mbps'   : 'dial manual \"1024\"',
            'Dial 1.9Mbps'   : 'dial manual \"1920\"',
            'Dial 4Mbps'   : 'dial manual \"4096\"',
            'Hangup 1'     : 0,
            'Hangup 2'     : 1,
            'Hangup 3'     : 2,
            'Hangup 4'     : 3,
            'Hangup 5'     : 4,
            'Hangup'       : 'hangup video',
            'Hangup All'   : 'hangup all',
            'Answer'       : 'answer video',
        }


        HookCmdString = None
        if 'Dial' in value:
            num = qualifier['Number']
            if num:
                HookCmdString = '{0} \"{1}\"\r'.format(ValueStateValues[value], num)
        elif value in ['Hangup 1', 'Hangup 2', 'Hangup 3', 'Hangup 4', 'Hangup 5']:
            index = ValueStateValues[value]
            if len(self.CallID) >= index + 1:
                HookCmdString = 'hangup video {0}\r'.format(self.CallID[index])
                self.CallID.pop(index)
        else:
            HookCmdString = '{0}\r'.format(ValueStateValues[value])

        if HookCmdString:
            self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 50
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'volume set {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Error(['Invalid Command for SetVolume'])

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'volume get\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

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

            if self.SleepRegister == 'Disabled':
                self.EnableSleepRegister(None, None)
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        self.Error([match.group(0).decode()])

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

    def __init__(self, Hostname, IPPort=24, Protocol='TCP', ServicePort=0, Model=None):
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
