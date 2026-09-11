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
        self.NumberOfAddressBookSearch = 5
        self._NumberOfHistorySearch = 5
        self.deviceUsername = 'apiuser'
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AddressBookNavigation': {'Status': {}},
            'AddressBookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'AddressBookSearchSet': {'Status': {}},
            'AddressBookUpdate': {'Status': {}},
            'AutoViewing': {'Status': {}},
            'Broadcast': {'Parameters': ['MCU Number', 'Terminal Number'], 'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraControl': {'Parameters': ['Type', 'Control'], 'Status': {}},
            'CameraPreset': {'Parameters': ['Type', 'Action'], 'Status': {}},
            'ChairControl': {'Status': {}},
            'ConferenceCall': {'Parameters': ['Call Type', 'Bandwidth'], 'Status': {}},
            'ConferenceCallStatus': {'Status': {}},
            'ConferenceSiteIDsArray': {'Status': {}},
            'DelayConference': {'Parameters': ['Delay Time'], 'Status': {}},
            'DialBandwidth': {'Status': {}},
            'DialType': {'Status': {}},
            'FreeTalk': {'Status': {}},
            'HistoryNavigation': {'Parameters': ['Type'], 'Status': {}},
            'HistorySearchResult': {'Parameters': ['Button', 'Type'], 'Status': {}},
            'HistorySearchSet': {'Parameters': ['Type'], 'Status': {}},
            'HistoryUpdate': {'Parameters': ['Type'], 'Status': {}},
            'Hook': {'Status': {}},
            'LocalMicMute': {'Status': {}},
            'LocalSpeakerMute': {'Status': {}},
            'LocalVideoSource': {'Parameters': ['Type'], 'Status': {}},
            'RemoteMicMute': {'Parameters': ['MCU Number', 'Terminal Number'], 'Status': {}},
            'RemoteSpeakerMute': {'Parameters': ['MCU Number', 'Terminal Number'], 'Status': {}},
            'RequestFloor': {'Status': {}},
            'RollCall': {'Parameters': ['MCU Number', 'Terminal Number'], 'Status': {}},
            'ShareContent': {'Status': {}},
            'ViewSite': {'Parameters': ['MCU Number', 'Terminal Number'], 'Status': {}},
            'Volume': {'Parameters': ['Type'], 'Status': {}},
        }

        self.LoginSuccess = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Enter your login name :'), self.__MatchUserName, None)
            self.AddMatchString(re.compile(b'Enter your password :'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'.*Success!!!'), self.__MatchLoginSuccess, None)
            self.AddMatchString(re.compile(b'\r\nlogon auth fail!!!'), self.__MatchLoginFailure, None)
            self.AddMatchString(re.compile(b'(<ComeInCall>|<DisconnectCall>|<GetCallResult> CallResult:([01]))'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'<GetSiteCallResult> SiteCallResult:([01])'), self.__MatchConferenceCallStatus, None)
            self.AddMatchString(re.compile(b'<GetLocalInfo> Result:0 [\S ]+?SpeakerState:([01]) MicState:([01])[\S ]+</GetLocalInfo>'), self.__MatchLocalMicMute, None)
            self.AddMatchString(re.compile(b'<[\S]+> Result:([1256]) </[\S]+>'), self.__MatchError, None)

        self.AddBkNamePattern = re.compile('ID:[\d]{1,3} Name:\"([\S\s]+?)\" PName')
        self.AddBkCallTypePattern = re.compile('CallType:\"([\S\s]+?)\"')
        self.AddBkBWPattern = re.compile('BandWidth:([\d]{2,4})')
        self.AddBkDialStrPattern = re.compile('(IP|Number|Port):\"([\S ]+?)\"[\S ]+?</GetAddr>')

        self.MCallPattern = re.compile('<GetCallRecord> Result:0 RecordType:0[\S\s ]+? CallType:\"([\S]+)\" BandWidth:([\d]{2,4}) Number:\"([\d]+)?\" IP:\"([\d.]+)?\" <\/GetCallRecord>')
        self.MStartingEntry = 1
        self.MEndEntry = 0
        self.MAdvance = True

        self.RCallPattern = re.compile('<GetCallRecord> Result:0 RecordType:1[\S\s ]+? CallType:\"([\S]+)\" BandWidth:([\d]{2,4}) Number:\"([\d]+)?\" IP:\"([\d.]+)?\" <\/GetCallRecord>')
        self.RStartingEntry = 1
        self.REndEntry = 0
        self.RAdvance = True

        self.DCallPattern = re.compile('<GetCallRecord> Result:0 RecordType:2[\S\s ]+? CallType:\"([\S]+)\" BandWidth:([\d]{2,4}) Number:\"([\d]+)?\" IP:\"([\d.]+)?\" <\/GetCallRecord>')
        self.DStartingEntry = 1
        self.DEndEntry = 0
        self.DAdvance = True

    @property
    def NumberOfAddressBookSearch(self):
        return self._NumberOfAddressBookSearch

    @NumberOfAddressBookSearch.setter
    def NumberOfAddressBookSearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfAddressBookSearch = int(value)
            self.AddressDir = Directory(self._NumberOfAddressBookSearch, 'AddressBookSearchResult', filler='')
            self.AddressDir.write_status_function = self.WriteStatus
        else:
            self.Error(['Number Of Address Book Search should be a value between 1 to 15.'])

    @property
    def NumberOfHistorySearch(self):
        return self._NumberOfHistorySearch

    @NumberOfHistorySearch.setter
    def NumberOfHistorySearch(self, value):
        if 1 <= int(value) <= 15:
            self._NumberOfHistorySearch = value
        else:
            self.Error(['Number Of History Search should be a value between 1 to 15.'])

    def __MatchUserName(self, match, tag):
        self.SetSendName()

    def SetSendName(self):
        self.Send('{0}\r'.format(self.deviceUsername))

    def __MatchPassword(self, match, tag):
        if self.devicePassword:
            self.Send('{0}\r'.format(self.devicePassword))
        else:
            self.Send('\r')

    def __MatchLoginSuccess(self, match, tag):
        self.LoginSuccess = True

    def __MatchLoginFailure(self, match, tag):
        self.LoginSuccess = False
        self.SetSendName()
        self.Error(['Login Failed. Please enter correct Username and Password.'])

    def SetAddressBookNavigation(self, value, qualifier):
        if value == 'Up':
            self.AddressDir.scroll_up(1)
        elif value == 'Down':
            self.AddressDir.scroll_down(1)
        elif value == 'Page Up':
            self.AddressDir.scroll_up(self._NumberOfAddressBookSearch)
        elif value == 'Page Down':
            self.AddressDir.scroll_down(self._NumberOfAddressBookSearch)

    def SetAddressBookUpdate(self, value, qualifier):

        AddressBookUpdateCmdString = 'RecordBook GetAddr Sort:0 Start:1 End:1000\r'
        res = self.SendAndWait(AddressBookUpdateCmdString, 10, deliTag=b'->')
        if res:
            try:
                res = res.decode()
                self.AddNameList = re.findall(self.AddBkNamePattern, res)
                self.AddCallTypeList = re.findall(self.AddBkCallTypePattern, res)
                self.AddBWList = re.findall(self.AddBkBWPattern, res)
                self.AddDialStrList = re.findall(self.AddBkDialStrPattern, res)
                AddBk_Data = [entry for entry in zip(self.AddCallTypeList, self.AddBWList, self.AddDialStrList)]
                self.AddBK_DataDict = {}
                for i in range(0, len(self.AddNameList)):
                    self.AddBK_DataDict[self.AddNameList[i]] = AddBk_Data[i]
                new_AddBk_data = ['{0}'.format(entry[0]) for entry in zip(self.AddNameList)]
                new_AddBk_data.append('***End of List***')
                self.AddressDir.reset(new_AddBk_data)
            except (KeyError, IndexError, AttributeError):
                self.Error(['Address Update: Invalid/unexpected response'])
        else:
            new_AddBk_data = []
            new_AddBk_data.append('***Not Available***')
            self.AddressDir.reset(new_AddBk_data)

    def SetAddressBookSearchSet(self, value, qualifier):

        if 1 <= value <= self._NumberOfAddressBookSearch:
            Name = self.ReadStatus('AddressBookSearchResult', {'Button': value})
            if Name != '***End of List***' and Name != '***Not Available***':
                try:
                    DialTypeValue = self.AddBK_DataDict[Name][0]
                    BWValue = self.AddBK_DataDict[Name][1]
                    DialStrValue = self.AddBK_DataDict[Name][2][1]
                    self.SetHook('Dial', {'Dial Type': DialTypeValue, 'Dial Bandwidth': BWValue, 'Dial String': DialStrValue})
                except:
                    self.Discard('Invalid Command for SetAddressBookSearchSet')
        else:
            self.Discard('Invalid Command for SetAddressBookSearchSet')

    def SetHistoryNavigation(self, value, qualifier):

        type_ = qualifier['Type']
        if type_ in ['Missed Call', 'Received Call', 'Dialed Call'] and value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self._NumberOfHistorySearch
            else:
                NumberOfAdvance = 1

            if type_ == 'Missed Call':
                if 'Down' in value:
                    if self.MAdvance:
                        self.MStartingEntry += NumberOfAdvance
                elif 'Up' in value:
                    self.MStartingEntry -= NumberOfAdvance

                if self.MStartingEntry < 1:
                    self.MStartingEntry = 1

                self.MEndEntry = self.MStartingEntry + self._NumberOfHistorySearch - 1
                self.HistoryNav(self.MCallList, 'Missed Call', self.MStartingEntry, self.MEndEntry)

            elif type_ == 'Received Call':
                if 'Down' in value:
                    if self.RAdvance:
                        self.RStartingEntry += NumberOfAdvance
                elif 'Up' in value:
                    self.RStartingEntry -= NumberOfAdvance

                if self.RStartingEntry < 1:
                    self.RStartingEntry = 1

                self.REndEntry = self.RStartingEntry + self._NumberOfHistorySearch - 1
                self.HistoryNav(self.RCallList, 'Received Call', self.RStartingEntry, self.REndEntry)
            else:
                if 'Down' in value:
                    if self.DAdvance:
                        self.DStartingEntry += NumberOfAdvance
                elif 'Up' in value:
                    self.DStartingEntry -= NumberOfAdvance

                if self.DStartingEntry < 1:
                    self.DStartingEntry = 1

                self.DEndEntry = self.DStartingEntry + self._NumberOfHistorySearch - 1
                self.HistoryNav(self.DCallList, 'Dialed Call', self.DStartingEntry, self.DEndEntry)
        else:
            self.Discard('Invalid Command for SetHistoryNavigation')

    def HistoryNav(self, HistoryList, Type, StartingEntry, EndEntry):
        numOfName = len(HistoryList)
        index = StartingEntry - 1
        button = 1
        if Type == 'Missed Call':
            self.MAdvance = True
        elif Type == 'Received Call':
            self.RAdvance = True
        else:
            self.DAdvance = True
        while index < numOfName and index < EndEntry:
            name = HistoryList[index]
            self.WriteStatus('HistorySearchResult', name, {'Button': int(button), 'Type': Type})
            button = button + 1
            index = index + 1

        if button <= self._NumberOfHistorySearch:
            if Type == 'Missed Call':
                self.MAdvance = False
            elif Type == 'Received Call':
                self.RAdvance = False
            else:
                self.DAdvance = False
            self.WriteStatus('HistorySearchResult', '***End of List***', {'Button': button, 'Type': Type})
            button = button + 1
            for i in range(button, int(self._NumberOfHistorySearch) + 1):
                self.WriteStatus('HistorySearchResult', '', {'Button': i, 'Type': Type})

    def SetHistoryUpdate(self, value, qualifier):

        TypeStates = {
            'Missed Call': '0',
            'Received Call': '1',
            'Dialed Call': '2'
        }

        type_ = qualifier['Type']
        if type_ in TypeStates:
            HistoryUpdateCmdString = 'RecordBook GetCallRecord RecordType:{}\r'.format(TypeStates[type_])
            res = self.SendAndWait(HistoryUpdateCmdString, 10, deliTag=b'->')
            if res:
                try:
                    res = res.decode()
                    if type_ == 'Missed Call':
                        MCall_Data = re.findall(self.MCallPattern, res)
                        self.MCall_DataDict = {}
                        self.MCallList = []
                        for i in range(0, len(MCall_Data)):
                            if MCall_Data[i][2]:
                                self.MCallList.append(MCall_Data[i][2])
                                self.MCall_DataDict[MCall_Data[i][2]] = MCall_Data[i]
                            else:
                                self.MCallList.append(MCall_Data[i][3])
                                self.MCall_DataDict[MCall_Data[i][3]] = MCall_Data[i]
                            self.WriteDataforHistory(self.MCallList, type_)
                    elif type_ == 'Received Call':
                        RCall_Data = re.findall(self.RCallPattern, res)
                        self.RCall_DataDict = {}
                        self.RCallList = []
                        for i in range(0, len(RCall_Data)):
                            if RCall_Data[i][2]:
                                self.RCallList.append(RCall_Data[i][2])
                                self.RCall_DataDict[RCall_Data[i][2]] = RCall_Data[i]
                            else:
                                self.RCallList.append(RCall_Data[i][3])
                                self.RCall_DataDict[RCall_Data[i][3]] = RCall_Data[i]
                            self.WriteDataforHistory(self.RCallList, type_)
                    else:
                        DCall_Data = re.findall(self.DCallPattern, res)
                        self.DCall_DataDict = {}
                        self.DCallList = []
                        for i in range(0, len(DCall_Data)):
                            if DCall_Data[i][2]:
                                self.DCallList.append(DCall_Data[i][2])
                                self.DCall_DataDict[DCall_Data[i][2]] = DCall_Data[i]
                            else:
                                self.DCallList.append(DCall_Data[i][3])
                                self.DCall_DataDict[DCall_Data[i][3]] = DCall_Data[i]
                            self.WriteDataforHistory(self.DCallList, type_)
                except (KeyError, IndexError, AttributeError):
                    self.Error(['History Update: Invalid/unexpected response'])
            else:
                self.__MatchNoContact(type_)
        else:
            self.Discard('Invalid Command for SetHistoryUpdate')
    
    def WriteDataforHistory(self, HistoryList, Type):
        searchMax = len(HistoryList)
        if searchMax > self._NumberOfHistorySearch:
            searchMax = self._NumberOfHistorySearch
        button = 1
        for i in range(0, searchMax): # only populate up to max number configured
            name = HistoryList[button - 1]
            self.WriteStatus('HistorySearchResult', name, {'Button':button, 'Type':Type})
            button = button + 1
                            
        if button <= self._NumberOfHistorySearch:
           self.WriteStatus('HistorySearchResult', '***End of List***', {'Button':button, 'Type':Type})
           button = button + 1
           for i in range(button, self._NumberOfHistorySearch + 1):
               self.WriteStatus('HistorySearchResult', '', {'Button':i, 'Type':Type})
    
    def __MatchNoContact(self, Type):
        button = 1
        if Type == 'Missed Call':
            self.MAdvance = False
        elif Type == 'Received Call':
            self.RAdvance = False
        else:
            self.DAdvance = False
        self.WriteStatus('HistorySearchResult', '***Not Available***', {'Button': button, 'Type': Type})
        button = button + 1
        for i in range(button, int(self._NumberOfHistorySearch) + 1):
            self.WriteStatus('HistorySearchResult', '', {'Button': i, 'Type': Type})

    def SetHistorySearchSet(self, value, qualifier):

        type_ = qualifier['Type']
        if type_ in ['Missed Call', 'Received Call', 'Dialed Call'] and 1 <= value <= self._NumberOfHistorySearch:
            number = self.ReadStatus('HistorySearchResult', {'Button': value, 'Type': type_})
            if number != '***End of List***' and number != '***Not Available***':
                try:
                    if type_ == 'Missed Call':
                        DialTypeValue = self.MCall_DataDict[number][0]
                        BWValue = self.MCall_DataDict[number][1]
                        DialStrValue = number
                    elif type_ == 'Received Call':
                        DialTypeValue = self.RCall_DataDict[number][0]
                        BWValue = self.RCall_DataDict[number][1]
                        DialStrValue = number
                    else:
                        DialTypeValue = self.DCall_DataDict[number][0]
                        BWValue = self.DCall_DataDict[number][1]
                        DialStrValue = number
                    self.SetHook('Dial', {'Dial Type': DialTypeValue, 'Dial Bandwidth': BWValue, 'Dial String': DialStrValue})
                except:
                    self.Discard('Invalid Command for SetHistorySearchSet')
        else:
            self.Discard('Invalid Command for SetHistorySearchSet')

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Accept': 'Call AcceptCall\r',
            'Reject': 'Call RejectCall\r',
            'Hung Up': 'Call HangupCall\r'
        }

        if value == 'Dial' and 64 <= int(qualifier['Dial Bandwidth']) <= 7680:
            DialType = qualifier['Dial Type']
            BW = qualifier['Dial Bandwidth']
            DialStr = qualifier['Dial String']
            HookCmdString = 'Call CallNewSite CallType:"{}" String:"{}" BandWidth:{}\r'.format(DialType, DialStr, BW)
        else:
            HookCmdString = ValueStateValues[value]
        self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def SetAutoViewing(self, value, qualifier):

        ValueStateValues = {
            'On': 'ConfCtrl AutoViewSite Switch:1 Range:0 Interval:600\r',
            'Off': 'ConfCtrl AutoViewSite Switch:0\r'
        }

        AutoViewingCmdString = ValueStateValues[value]
        self.__SetHelper('AutoViewing', AutoViewingCmdString, value, qualifier)

    def SetBroadcast(self, value, qualifier):

        MCU = int(qualifier['MCU Number'])
        Ter = int(qualifier['Terminal Number'])
        if 1 <= MCU <= 192 and 1 <= Ter <= 192:
            if value == 'Start':
                BroadcastCmdString = 'ConfCtrl BroadcastSite M:{} T:{}\r'.format(MCU, Ter)
            else:
                BroadcastCmdString = 'ConfCtrl CancelBroadcastSite\r'
            self.__SetHelper('Broadcast', BroadcastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBroadcast')

    def __MatchCallStatus(self, match, tag):

        temp = match.group(1).decode()
        if temp == '<ComeInCall>':
            self.WriteStatus('CallStatus', 'Incoming Call', None)
        elif temp == '<DisconnectCall>':
            self.WriteStatus('CallStatus', 'Disconnect', None)
        else:
            if int(match.group(2).decode()) == 0:
                self.WriteStatus('CallStatus', 'In Call', None)
            elif int(match.group(2).decode()) == 1:
                self.WriteStatus('CallStatus', 'Call Failure', None)

    def SetCameraControl(self, value, qualifier):

        TypeStates = {
            'Local': '1',
            'Remote': '2'
        }

        ControlStates = {
            'Up': 'Up',
            'Down': 'Down',
            'Left': 'Left',
            'Right': 'Right',
            'Home': 'Home',
            'Focus Near': 'FocusNear',
            'Focus Far': 'FocusFar',
            'Focus Auto': 'FocusAuto',
            'Zoom In': 'ZoomIn',
            'Zoom Out': 'ZoomOut'
        }

        type_ = qualifier['Type']
        ctrl = qualifier['Control']
        if type_ in TypeStates and ctrl in ControlStates and value in ['Start', 'Stop']:
            CameraControlCmdString = 'Camera CamCtrl CamObject:{} CamCtrlKey:"{}" KeyState:"{}"\r'.format(TypeStates[type_], ControlStates[ctrl], value)
            self.__SetHelper('CameraControl', CameraControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraControl')

    def SetCameraPreset(self, value, qualifier):

        TypeStates = {
            'Local': '1',
            'Remote': '2'
        }

        ActionStates = {
            'Set': '1',
            'Recall': '3',
            'Reset': '2'
        }

        type_ = qualifier['Type']
        action = qualifier['Action']
        if type_ in TypeStates and action in ActionStates and 0 <= int(value) <= 9:
            CameraPresetCmdString = 'Camera CtrlCamPreset CamObject:{} PresetAction:{} Position:{}\r'.format(TypeStates[type_], ActionStates[action], value)
            self.__SetHelper('CameraPreset', CameraPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPreset')

    def SetChairControl(self, value, qualifier):

        ValueStateValues = {
            'Request': 'ConfCtrl RequestChair\r',
            'Release': 'ConfCtrl ReleaseChair\r'
        }

        ChairControlCmdString = ValueStateValues[value]
        self.__SetHelper('ChairControl', ChairControlCmdString, value, qualifier)

    def SetConferenceCall(self, value, qualifier):

        CallTypeStates = {
            'H323': 'H323',
            'E1': 'E1',
            'ISDN': 'ISDN',
            '4E1': '4E1',
            'H323PHONE': 'H323PHONE',
            'SIP': 'SIP',
            'SIPPHONE': 'SIPPHONE',
            'UNKNOWN': 'UNKNOWN'
        }

        callType = qualifier['Call Type']
        BW = int(qualifier['Bandwidth'])
        if callType in CallTypeStates and 64 <= BW <= 7680:
            if value == 'End':
                ConferenceCallCmdString = 'ConfCtrl EndConf\r'
            else:
                SiteArray = qualifier['Site IDs Array']
                if isinstance(SiteArray, list):
                    ConferenceCallCmdString = 'Call SiteCall CallType:"{}" SiteIDs:{} BandWidth:{}\r'.format(callType, SiteArray, BW)
                else:
                    self.Discard('Invalid Command for SetConferenceCall')
            self.__SetHelper('ConferenceCall', ConferenceCallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceCall')

    def __MatchConferenceCallStatus(self, match, tag):

        if int(match.group(1).decode()) == 0:
            self.WriteStatus('ConferenceCallStatus', 'Successful', None)
        else:
            self.WriteStatus('ConferenceCallStatus', 'Fail', None)

    def SetDelayConference(self, value, qualifier):

        Dtime = int(qualifier['Delay Time'])
        if 10 <= Dtime <= 65535:
            DelayConferenceCmdString = 'ConfCtrl DelayConf DelayConfTime:{}\r'.format(Dtime)
            self.__SetHelper('DelayConference', DelayConferenceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDelayConference')

    def SetFreeTalk(self, value, qualifier):
        FreeTalkCmdString = 'ConfCtrl FreeTalk\r'
        self.__SetHelper('FreeTalk', FreeTalkCmdString, value, qualifier)

    def SetLocalMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'AudioCtrl SetMicState Switch:0\r',
            'Off': 'AudioCtrl SetMicState Switch:1\r'
        }

        LocalMicMuteCmdString = ValueStateValues[value]
        self.__SetHelper('LocalMicMute', LocalMicMuteCmdString, value, qualifier)

    def UpdateLocalMicMute(self, value, qualifier):

        LocalMicMuteCmdString = 'Status GetLocalInfo\r'
        self.__UpdateHelper('LocalMicMute', LocalMicMuteCmdString, value, qualifier)

    def __MatchLocalMicMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        SpkVal = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('LocalSpeakerMute', SpkVal, None)
        MicVal = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('LocalMicMute', MicVal, None)

    def SetLocalSpeakerMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'AudioCtrl SetSpeakerState Switch:1\r',
            'Off': 'AudioCtrl SetSpeakerState Switch:0\r'
        }

        LocalSpeakerMuteCmdString = ValueStateValues[value]
        self.__SetHelper('LocalSpeakerMute', LocalSpeakerMuteCmdString, value, qualifier)

    def UpdateLocalSpeakerMute(self, value, qualifier):

        LocalSpeakerMuteCmdString = 'Status GetLocalInfo\r'
        self.__UpdateHelper('LocalSpeakerMute', LocalSpeakerMuteCmdString, value, qualifier)

    def SetLocalVideoSource(self, value, qualifier):

        TypeStates = {
            'Video': '1',
            'Presentation': '2'
        }

        ValueStateValues = {
            'HD 1': '0',
            'HD 2': '1',
            'SD 1': '2',
            'SD 2': '3',
            'VGA': '4'
        }

        type_ = qualifier['Type']
        if type_ in TypeStates:
            LocalVideoSourceCmdString = 'VideoCtrl SetLocalVideoSource Strm:{} VIPort:{}\r'.format(TypeStates[type_], ValueStateValues[value])
            self.__SetHelper('LocalVideoSource', LocalVideoSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLocalVideoSource')

    def SetRemoteMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MCU = int(qualifier['MCU Number'])
        Ter = int(qualifier['Terminal Number'])
        if 1 <= MCU <= 192 and 1 <= Ter <= 192:
            RemoteMicMuteCmdString = 'ConfCtrl SetSiteMicState M:{} T:{} Switch:{}\r'.format(MCU, Ter, ValueStateValues[value])
            self.__SetHelper('RemoteMicMute', RemoteMicMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRemoteMicMute')

    def SetRemoteSpeakerMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MCU = int(qualifier['MCU Number'])
        Ter = int(qualifier['Terminal Number'])
        if 1 <= MCU <= 192 and 1 <= Ter <= 192:
            RemoteSpeakerMuteCmdString = 'ConfCtrl SetSiteMicState M:{} T:{} Switch:{}\r'.format(MCU, Ter, ValueStateValues[value])
            self.__SetHelper('RemoteSpeakerMute', RemoteSpeakerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRemoteSpeakerMute')

    def SetRequestFloor(self, value, qualifier):

        RequestFloorCmdString = 'ConfCtrl RequestFloor\r'
        self.__SetHelper('RequestFloor', RequestFloorCmdString, value, qualifier)

    def SetRollCall(self, value, qualifier):

        MCU = int(qualifier['MCU Number'])
        Ter = int(qualifier['Terminal Number'])
        if 1 <= MCU <= 192 and 1 <= Ter <= 192:
            RollCallCmdString = 'ConfCtrl RollCall M:{} T:{}\r'.format(MCU, Ter)
            self.__SetHelper('RollCall', RollCallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRollCall')

    def SetShareContent(self, value, qualifier):

        ValueStateValues = {
            'On': 'VideoCtrl SendH239Content Switch:1\r',
            'Off': 'VideoCtrl SendH239Content Switch:0\r'
        }

        ShareContentCmdString = ValueStateValues[value]
        self.__SetHelper('ShareContent', ShareContentCmdString, value, qualifier)

    def SetViewSite(self, value, qualifier):

        MCU = int(qualifier['MCU Number'])
        Ter = int(qualifier['Terminal Number'])
        if 1 <= MCU <= 192 and 1 <= Ter <= 192:
            ViewSiteCmdString = 'ConfCtrl ViewSite M:{} T:{}\r'.format(MCU, Ter)
            self.__SetHelper('ViewSite', ViewSiteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetViewSite')

    def SetVolume(self, value, qualifier):

        TypeStates = {
            'Main Left': '0',
            'Main Right': '1',
            'Auxiliary Left': '2',
            'Auxiliary Right': '3',
            'Microphone': '4',
            'SPDIF': '5',
            'All Devices': '6',
            'Alert Tones': '7'
        }

        type_ = qualifier['Type']
        if 0 <= value <= 15 and type_ in TypeStates:
            VolumeCmdString = 'AudioCtrl SetVolume AOPort:{} Volume:{}'.format(TypeStates[type_], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or not self.LoginSuccess:
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

        ErrorStates = {
            '1': 'Invalid parameter is entered',
            '2': 'No incoming call so command is invalid',
            '5': 'Mandatory parameter is left out',
            '6': 'Call cannot be hanged up or rejected'
        }

        value = match.group(1).decode()
        self.Error([ErrorStates[value]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.MStartingEntry = 1
        self.MEndEntry = 0
        self.MAdvance = True

        self.RStartingEntry = 1
        self.REndEntry = 0
        self.RAdvance = True

        self.DStartingEntry = 1
        self.DEndEntry = 0
        self.DAdvance = True

        self.LoginSuccess = False

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
            self.write_to_module()
        return res

    return wrapper


class Directory:

    def __init__(self, display_count, write_function_name, filler=None):
        self._display_count = int(display_count)
        self.qualifier_name = 'Button'
        self._qualifier_type = 'Number'
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
            self._start_index = len(self.entry_list) - 1  # _start_index becomes the last item in the entry list
            if self._start_index < 0:
                self._start_index = 0

    @UseAutoUpdate
    def scroll_to_top(self):
        self._start_index = 0

    @UseAutoUpdate
    def scroll_to_bottom(self):
        self._start_index = len(self.entry_list) - 1
