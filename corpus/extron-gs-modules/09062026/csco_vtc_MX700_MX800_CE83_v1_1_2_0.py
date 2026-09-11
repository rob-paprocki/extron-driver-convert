from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
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
        self.Models = {}

        self.deviceUsername = 'admin'
        self.devicePassword = ''
        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPhonebookSearch = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofContactsPerSearch = 50
        self._NumberofFoldersPerSearch = 50
        self.FolderIDNumber = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveSpeakerPIPPosition': {'Status': {}},
            'AudioInputLineChannel': {'Parameters': ['Input'], 'Status': {}},
            'AudioInputLineLevel': {'Parameters': ['Input'], 'Status': {}},
            'AudioInputLineMode': {'Parameters': ['Input'], 'Status': {}},
            'AudioInputLineSource': {'Parameters': ['Input'], 'Status': {}},
            'AudioOutputLineChannel': {'Parameters': ['Output'], 'Status': {}},
            'AudioOutputLineLevel': {'Parameters': ['Output'], 'Status': {}},
            'AudioOutputLineMode': {'Parameters': ['Output'], 'Status': {}},
            'AudioVolume': {'Status': {}},
            'AudioVolumeMute': {'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryAcknowledgeAllMissedCalls': {'Status': {}},
            'CallHistoryAcknowledgeMissedCall': {'Parameters': ['Missed Call Number'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Parameters': ['Button'], 'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraAssignedSerialNumberCommand': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraAutofocusCommand': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraAutofocusMode': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraFocus': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraPan': {'Parameters': ['Camera ID', 'Pan Speed'], 'Status': {}},
            'CameraPreset': {'Status': {}},
            'CameraPresetStore': {'Parameters': ['Camera ID', 'Default Position'], 'Status': {}},
            'CameraSpeakerTrack': {'Status': {}},
            'CameraSpeakerTrackTrackingMode': {'Status': {}},
            'CameraTilt': {'Parameters': ['Camera ID', 'Tilt Speed'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Camera ID', 'Zoom Speed'], 'Status': {}},
            'ConferenceAutoAnswerDelay': {'Status': {}},
            'ConferenceAutoAnswerMode': {'Status': {}},
            'ConferenceAutoAnswerMute': {'Status': {}},
            'ConferenceDefaultCallProtocol': {'Status': {}},
            'ConferenceDefaultCallRate': {'Status': {}},
            'ConferenceDoNotDisturb': {'Status': {}},
            'ConferenceEncryptionMode': {'Status': {}},
            'ConferenceFarEndControlMode': {'Status': {}},
            'ConferenceSpeakerLock': {'Parameters': ['Speaker'], 'Status': {}},
            'DisplayName': {'Parameters': ['Call'], 'Status': {}},
            'DNSDomainNameCommand': {'Status': {}},
            'DNSServerAddressCommand': {'Parameters': ['Server'], 'Status': {}},
            'DNSServerAddressStatus': {'Parameters': ['Server'], 'Status': {}},
            'DTMF': {'Status': {}},
            'FarEndCameraPresetRecall': {'Status': {}},
            'FarEndCameraPTZ': {'Status': {}},
            'FarEndCameraSourceSelect': {'Status': {}},
            'H323AliasE164Command': {'Status': {}},
            'H323AliasIDCommand': {'Status': {}},
            'H323AuthenticationMode': {'Status': {}},
            'H323CallSetupMode': {'Status': {}},
            'H323GatekeeperAddressCommand': {'Status': {}},
            'H323GatekeeperAddressStatus': {'Status': {}},
            'H323GatekeeperStatus': {'Status': {}},
            'H323LoginNameCommand': {'Status': {}},
            'H323PasswordCommand': {'Status': {}},
            'Hook': {'Parameters': ['Protocol'], 'Status': {}},
            'IPv4AddressCommand': {'Status': {}},
            'IPv4AddressStatus': {'Status': {}},
            'IPv4GatewayCommand': {'Status': {}},
            'IPv4GatewayStatus': {'Status': {}},
            'IPv4SubnetMaskCommand': {'Status': {}},
            'IPv4SubnetMaskStatus': {'Status': {}},
            'LayoutSet': {'Parameters': ['Target'], 'Status': {}},
            'MicrophoneLevel': {'Parameters': ['Microphone'], 'Status': {}},
            'MicrophoneMode': {'Parameters': ['Microphone'], 'Status': {}},
            'MuteAllMicrophones': {'Status': {}},
            'PhonebookFolderIDNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': {'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'Presentation': {'Parameters': ['Instance'], 'Status': {}},
            'PresentationDefaultSource': {'Status': {}},
            'PresentationMode': {'Status': {}},
            'PresentationPIPPosition': {'Status': {}},
            'PresentationSendingMode': {'Parameters': ['Connector ID'], 'Status': {}},
            'PresentationSendingModeStatus': {'Parameters': ['Instance'], 'Status': {}},
            'RemoteNumber': {'Parameters': ['Call'], 'Status': {}},
            'SelfView': {'Status': {}},
            'SelfViewDefaultFullscreenMode': {'Status': {}},
            'SelfViewPosition': {'Status': {}},
            'Standby': {'Status': {}},
            'VideoInput': {'Parameters': ['Connector ID'], 'Status': {}},
            'VideoSetMainVideoSource': {'Parameters': ['Connector ID'], 'Status': {}},
        }

        self.folderList = {}
        self.newList = {}

        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n')
        self.callStatusTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n')
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "(.*)"\r\n')
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "(.*)"\r\n')
        self.callID = compile('\*s Call (\d+) Status: \w+\r\n')
        self.__CallID = []

        self.MinLabel = 1
        self.MaxLabel = 5
        self.dirName = compile('\*r PhonebookSearchResult Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: "(.+)"')
        self.Offset = 0

        self.FolderMin = 1
        self.FolderLimit = 0
        self.MaxFolders = 1
        self.FolderNameRex = compile('\*r PhonebookSearchResult Folder (\d+) Name: "(.+)"\r\n')
        self.FolderIDRex = compile('\*r PhonebookSearchResult Folder (\d+) FolderId: "(.+)"')

        self.prevCallHist = ''
        self.startCallHist = 1
        self.endCallHist = 0
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        
        if self._CallHistoryOccurrenceType == 'Time':
            self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) Count: (\d+)\r\n')
        self.occurrenceType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')
        self.advanceCallHist = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*s Video PIP ActiveSpeaker Position: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchActiveSpeakerPIPPosition, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchAudioVolume, None)
            self.AddMatchString(compile(b'\*s Audio VolumeMute: (On|Off)\r\n'), self.__MatchAudioVolumeMute, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchConferenceDoNotDisturb, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-3]) Address: "([0-9.]{7,15})"\r\n'), self.__MatchDNSServerAddressStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{7,15})"\r\n'), self.__MatchH323GatekeeperAddressStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4AddressStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4GatewayStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4SubnetMaskStatus, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMuteAllMicrophones, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-5])\r\n'), self.__MatchPresentation, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationMode, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusStop, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*s Video Selfview FullscreenMode: (On|Off|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchTelnetNegotiation, None)


    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):

        self._CallHistoryOccurrenceType = value
        if self._CallHistoryOccurrenceType == 'Time':
            self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) Count: (\d+)\r\n')

    @property
    def NumberofCallHistory(self):
        return self._NumberofCallHistory

    @NumberofCallHistory.setter
    def NumberofCallHistory(self, value):
        self._NumberofCallHistory = value

    @property
    def NumberofPhonebookFolderSearch(self):
        return self._NumberofPhonebookFolderSearch

    @NumberofPhonebookFolderSearch.setter
    def NumberofPhonebookFolderSearch(self, value):
        self._NumberofPhonebookFolderSearch = value

    @property
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        self._NumberofPhonebookSearch = value

    def __MatchTelnetNegotiation(self, match, tag):
        self.Send(b'\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetActiveSpeakerPIPPosition(self, value, qualifier):

        States = {
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight',
            'Upper Center': 'UpperCenter',
            'Upper Left': 'UpperLeft',
            'Upper Right': 'UpperRight'
        }

        CmdString = 'xCommand Video ActiveSpeakerPIP Set Position: {0}\r'.format(States[value])
        self.__SetHelper('ActiveSpeakerPIPPosition', CmdString, value, qualifier)

    def UpdateActiveSpeakerPIPPosition(self, value, qualifier):
        self.__UpdateHelper('ActiveSpeakerPIPPosition', 'xStatus Video ActiveSpeaker PIPPosition\r', value, qualifier)

    def __MatchActiveSpeakerPIPPosition(self, match, tag):

        States = {
            'CenterLeft': 'Center Left',
            'CenterRight': 'Center Right',
            'LowerLeft': 'Lower Left',
            'LowerRight': 'Lower Right',
            'UpperCenter': 'Upper Center',
            'UpperLeft': 'Upper Left',
            'UpperRight': 'Upper Right'
        }

        value = States[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('ActiveSpeakerPIPPosition', value, None)

    def SetAudioInputLineChannel(self, value, qualifier):

        States = {
            'Left': 'Left',
            'Mono': 'Mono',
            'Right': 'Right'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {0} Channel: {1}\r'.format(qualifier['Input'], States[value])
            self.__SetHelper('AudioInputLineChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineChannel')

    def SetAudioInputLineLevel(self, value, qualifier):

        if 0 <= value <= 24 and 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {0} Level: {1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('AudioInputLineLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineLevel')

    def SetAudioInputLineMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {0} Mode: {1}\r'.format(qualifier['Input'], States[value])
            self.__SetHelper('AudioInputLineMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineMode')

    def SetAudioInputLineSource(self, value, qualifier):

        if 1 <= int(value) <= 5 and 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {0} VideoAssociation VideoInputSource: {1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('AudioInputLineSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineSource')

    def SetAudioOutputLineChannel(self, value, qualifier):

        States = {
            'Left': 'Left',
            'Mono': 'Mono',
            'Right': 'Right'
        }

        if 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {0} Channel: {1}\r'.format(qualifier['Output'], States[value])
            self.__SetHelper('AudioOutputLineChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineChannel')

    def SetAudioOutputLineLevel(self, value, qualifier):

        if 0 <= value <= 24 and 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {0} Level: {1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('AudioOutputLineLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineLevel')

    def SetAudioOutputLineMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        if 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {0} Mode: {1}\r'.format(qualifier['Output'], States[value])
            self.__SetHelper('AudioOutputLineMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineMode')

    def SetAudioVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'xCommand Audio Volume Set Level: {0}\r'.format(value)
            self.__SetHelper('AudioVolume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):
        self.__UpdateHelper('AudioVolume', 'xStatus Audio Volume\r', value, qualifier)

    def __MatchAudioVolume(self, match, tag):
        self.WriteStatus('AudioVolume', int(match.group(1).decode()), None)

    def SetAudioVolumeMute(self, value, qualifier):

        States = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        CmdString = 'xCommand Audio Volume {0}\r'.format(States[value])
        self.__SetHelper('AudioVolumeMute', CmdString, value, qualifier)

    def UpdateAudioVolumeMute(self, value, qualifier):
        self.__UpdateHelper('AudioVolumeMute', 'xStatus Audio VolumeMute\r', value, qualifier)

    def __MatchAudioVolumeMute(self, match, tag):
        self.WriteStatus('AudioVolumeMute', match.group(1).decode(), None)

    def SetCallHistoryRefresh(self, value, qualifier):
        
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        self.Debug = True
        
        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CallHistoryCmdString, 3, deliTag=b'** end')
        if res:
            res = res.decode()
            displayNameList = dict(findall(self.displayName, res))
            callBackNumberList = dict(findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(findall(self.occurrenceType, res))
            occurrenceCountList = dict(findall(self.occurrenceCount, res))

            for button in range(1, self._NumberofCallHistory+1):
                index = str(button-1)

                if index in displayNameList:
                    self.WriteStatus('CallHistory',displayNameList[index], {'Button':str(button), 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory',callBackNumberList[index], {'Button':str(button), 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory',lastOccurrenceTimeList[index], {'Button':str(button), 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory',occurrenceTypeList[index], {'Button':str(button), 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory',occurrenceCountList[index], {'Button':str(button), 'Detail Type' : 'Occurrence Count'})
                else:
                    self.WriteStatus('CallHistory','', {'Button':str(button), 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory','', {'Button':str(button), 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory','', {'Button':str(button), 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory','', {'Button':str(button), 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory','', {'Button':str(button), 'Detail Type' : 'Occurrence Count'})
        else:
            for index in range(1, self._NumberofCallHistory + 1):
                self.WriteStatus('CallHistory','', {'Button':str(index), 'Detail Type' : 'Display Name'})
                self.WriteStatus('CallHistory','', {'Button':str(index), 'Detail Type' : 'Callback Number'})
                self.WriteStatus('CallHistory','', {'Button':str(index), 'Detail Type' : 'Last Occurrence Time'})
                self.WriteStatus('CallHistory','', {'Button':str(index), 'Detail Type' : 'Occurrence Type'})
                self.WriteStatus('CallHistory','', {'Button':str(index), 'Detail Type' : 'Occurrence Count'})

    def SetCallHistoryNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self._NumberofCallHistory
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                self.startCallHist += NumberOfAdvance
            elif 'Up' in value:
                self.startCallHist -= NumberOfAdvance

            if self.startCallHist < 1:
                self.startCallHist = 1

            self.__UpdateCallHistoryHelper(value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetCallHistorySelect(self, value, qualifier):
        self.Debug = True
        
        if 1 <= int(qualifier['Button']) <= 20:
            number = self.ReadStatus('CallHistory', {'Button': qualifier['Button'], 'Detail Type': 'Callback Number'})
            if number:
                self.Send('xCommand Dial Number:"{0}"\r'.format(number))
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')

    def SetCallHistoryAcknowledgeAllMissedCalls(self, value, qualifier):

        self.__SetHelper('CallHistoryAcknowledgeAllMissedCalls', 'xCommand CallHistory AcknowledgeAllMissedCalls\r', value, qualifier)

    def SetCallHistoryAcknowledgeMissedCall(self, value, qualifier):

        if 1 <= int(qualifier['Missed Call Number']) <= 2147483647:
            CmdString = 'xCommand CallHistory AcknowledgeMissedCall CallHistoryID: {0}\r'.format(qualifier['Missed Call Number'])
            self.__SetHelper('CallHistoryAcknowledgeMissedCall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallHistoryAcknowledgeAllMissedCalls')

    def UpdateCallStatus(self, value, qualifier):
        res = self.SendAndWait('xstatus call\r', 1, deliTag=b'** end')
        if res:
            res = res.decode()
            callValue = {
                'Idle': 'Idle',
                'Dialing': 'Dialing',
                'Ringing': 'Ringing',
                'Connecting': 'Connecting',
                'Connected': 'Connected',
                'Disconnecting': 'Disconnecting',
                'OnHold': 'On Hold',
                'EarlyMedia': 'Early Media',
                'Preserved': 'Preserved',
                'RemotePreserved': 'Remote Preserved',
            }
            self.__CallID = findall(self.callID, res)
            callList = findall(self.callStatus, res)
            displayNameList = findall(self.displayNamePattern, res)
            remoteNumberList = findall(self.remoteNumberPattern, res)
            callStatusTypeList = findall(self.callStatusTypePattern, res)
            index = 0
            if len(self.__CallID) > 0:
                for index in range(1, len(callList) + 1):
                    self.WriteStatus('CallStatus', callValue[callList[index - 1]], {'Call': str(index)})
                    self.WriteStatus('DisplayName', displayNameList[index - 1], {'Call': str(index)})
                    self.WriteStatus('RemoteNumber', remoteNumberList[index - 1], {'Call': str(index)})
                    self.WriteStatus('CallStatusType', callStatusTypeList[index - 1], {'Call': str(index)})
            else:
                index += 1
                while index <= 5:
                    self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
                    self.WriteStatus('DisplayName', '', {'Call': str(index)})
                    self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                    self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
                    index += 1
        else:
            for index in range(1, 6):
                self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})

    def SetCameraAssignedSerialNumberCommand(self, value, qualifier):

        if 1 <= int(qualifier['Camera ID']) <= 7:
            SerialNumber = qualifier['Serial Number']
            CmdString = 'xConfiguration Cameras Camera {0} AssignedSerialNumber: "{1}"\r'.format(qualifier['Camera ID'], SerialNumber)
            self.__SetHelper('CameraAssignedSerialNumberCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAssignedSerialNumberCommand')

    def SetCameraAutofocusCommand(self, value, qualifier):

        if 1 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xCommand Camera TriggerAutofocus CameraId: {0}\r'.format(qualifier['Camera ID'])
            self.__SetHelper('CameraAutofocusCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAutofocusCommand')

    def SetCameraAutofocusMode(self, value, qualifier):

        States = {
            'Auto': 'Auto',
            'Manual': 'Manual'
        }

        if 2 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xConfiguration Cameras Camera {0} Focus Mode: {1}\r'.format(qualifier['Camera ID'], States[value])
            self.__SetHelper('CameraAutofocusMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAutofocusMode')

    def SetCameraFocus(self, value, qualifier):

        States = {
            'Far': 'Far',
            'Near': 'Near',
            'Stop': 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xCommand Camera Ramp CameraId: {0} Focus: {1}\r'.format(qualifier['Camera ID'], States[value])
            self.__SetHelper('CameraFocus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        States = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Pan Speed']) <= 15:
            CmdString = 'xCommand Camera Ramp CameraId: {0} PanSpeed: {1} Pan: {2}\r'.format(qualifier['Camera ID'], qualifier['Pan Speed'], States[value])
            self.__SetHelper('CameraPan', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPreset(self, value, qualifier):

        if 1 <= int(value) <= 35:
            CmdString = 'xCommand Camera Preset Activate PresetId: {}\r'.format(value)
            self.__SetHelper('CameraPreset', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPreset')

    def SetCameraPresetStore(self, value, qualifier):

        CameraID = int(qualifier['Camera ID'])

        DefaultPositionStates = {
            'False': 'False',
            'True': 'True'
        }

        DefaultPosition = DefaultPositionStates[qualifier['Default Position']]

        if 1 <= int(value) <= 35 and 1 <= CameraID <= 7:
            CmdString = 'xCommand Camera Preset Store PresetId: {0} CameraId: {1} DefaultPosition: {2}\r'.format(value, CameraID, DefaultPosition)
            self.__SetHelper('CameraPresetStore', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetStore')

    def SetCameraSpeakerTrack(self, value, qualifier):

        States = {
            'Activate': 'Activate',
            'Deactivate': 'Deactivate'
        }

        CmdString = 'xCommand Cameras SpeakerTrack {0}\r'.format(States[value])
        self.__SetHelper('CameraSpeakerTrack', CmdString, value, qualifier)

    def SetCameraSpeakerTrackTrackingMode(self, value, qualifier):

        States = {
            'Auto': 'Auto',
            'Conservative': 'Conservative'
        }

        CmdString = 'xConfiguration Cameras SpeakerTrack TrackingMode: {0}\r'.format(States[value])
        self.__SetHelper('CameraSpeakerTrackTrackingMode', CmdString, value, qualifier)

    def SetCameraTilt(self, value, qualifier):

        States = {
            'Down': 'Down',
            'Up': 'Up',
            'Stop': 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Tilt Speed']) <= 15:
            CmdString = 'xCommand Camera Ramp CameraId: {0} Tilt: {1} TiltSpeed: {2}\r'.format(qualifier['Camera ID'], States[value], qualifier['Tilt Speed'])
            self.__SetHelper('CameraTilt', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraZoom(self, value, qualifier):

        States = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Zoom Speed']) <= 15:
            CmdString = 'xCommand Camera Ramp CameraId: {0} Zoom: {1} ZoomSpeed: {2}\r'.format(qualifier['Camera ID'], States[value], qualifier['Zoom Speed'])
            self.__SetHelper('CameraZoom', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetConferenceAutoAnswerDelay(self, value, qualifier):

        if 0 <= value <= 50:
            CmdString = 'xConfiguration Conference AutoAnswer Delay: {0}\r'.format(value)
            self.__SetHelper('ConferenceAutoAnswerDelay', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceAutoAnswerDelay')

    def SetConferenceAutoAnswerMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        CmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(States[value])
        self.__SetHelper('ConferenceAutoAnswerMode', CmdString, value, qualifier)

    def SetConferenceAutoAnswerMute(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        CmdString = 'xConfiguration Conference AutoAnswer Mute: {0}\r'.format(States[value])
        self.__SetHelper('ConferenceAutoAnswerMute', CmdString, value, qualifier)

    def SetConferenceDefaultCallProtocol(self, value, qualifier):

        States = {
            'Auto': 'Auto',
            'H323': 'H323',
            'Sip': 'Sip',
            'H320': 'H320'
        }

        CmdString = 'xConfiguration Conference DefaultCall Protocol: {0}\r'.format(States[value])
        self.__SetHelper('ConferenceDefaultCallProtocol', CmdString, value, qualifier)

    def SetConferenceDefaultCallRate(self, value, qualifier):

        if 64 <= value <= 6000:
            CmdString = 'xConfiguration Conference DefaultCall Rate: {0}\r'.format(value)
            self.__SetHelper('ConferenceDefaultCallRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceDefaultCallRate')

    def SetConferenceDoNotDisturb(self, value, qualifier):

        States = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        CmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(States[value])
        self.__SetHelper('ConferenceDoNotDisturb', CmdString, value, qualifier)

    def UpdateConferenceDoNotDisturb(self, value, qualifier):
        self.__UpdateHelper('ConferenceDoNotDisturb', 'xStatus Conference DoNotDisturb\r', value, qualifier)

    def __MatchConferenceDoNotDisturb(self, match, tag):

        States = {
            'Active': 'On',
            'Inactive': 'Off'
        }

        self.WriteStatus('ConferenceDoNotDisturb', States[match.group(1).decode()], None)

    def SetConferenceEncryptionMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off',
            'Best Effort': 'BestEffort'
        }

        CmdString = 'xConfiguration Conference Encryption Mode: {0}\r'.format(States[value])
        self.__SetHelper('ConferenceEncryptionMode', CmdString, value, qualifier)

    def SetConferenceFarEndControlMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        CmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(States[value])
        self.__SetHelper('ConferenceFarEndControlMode', CmdString, value, qualifier)

    def SetConferenceSpeakerLock(self, value, qualifier):

        SpeakerStates = {
            'Local': 'local',
            'Remote': 'remote'
        }

        States = {
            'On': 'Set',
            'Off': 'Release'
        }

        if States[value] == 'Set':
            CmdString = 'xCommand Conference SpeakerLock Set Target: {0}\r'.format(SpeakerStates[qualifier['Speaker']])
            self.__SetHelper('ConferenceSpeakerLock', CmdString, value, qualifier)
        elif States[value] == 'Release':
            CmdString = 'xCommand Conference SpeakerLock Release\r'
            self.__SetHelper('ConferenceSpeakerLock', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceSpeakerLock')

    def SetDNSDomainNameCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 DNS Domain Name: \"{0}\"\r'.format(value)
        self.__SetHelper('DNSDomainNameCommand', CmdString, value, qualifier)

    def SetDNSServerAddressCommand(self, value, qualifier):

        if 1 <= int(qualifier['Server']) <= 3:
            CmdString = 'xConfiguration Network 1 DNS Server {0} Address: "{1}"\r'.format(qualifier['Server'], value)
            self.__SetHelper('DNSServerAddressCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def UpdateDNSServerAddressStatus(self, value, qualifier):

        if 1 <= int(qualifier['Server']) <= 3:
            CmdString = 'xStatus Network 1 DNS Server {0} Address\r'.format(qualifier['Server'])
            self.__UpdateHelper('DNSServerAddressStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDNSServerAddressStatus')

    def __MatchDNSServerAddressStatus(self, match, tag):
        self.WriteStatus('DNSServerAddressStatus', match.group(2).decode(), {'Server': match.group(1).decode()})

    def SetDTMF(self, value, qualifier):

        States = {
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '*': '*',
            '#': '#'
        }

        CmdString = 'xCommand Call DTMFSend DTMFString: \"{0}\"\r'.format(States[value])
        self.__SetHelper('DTMF', CmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl RoomPreset Activate PresetId: {0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraPTZ(self, value, qualifier):

        States = {
            'Left': 'Left',
            'Right': 'Right',
            'Up': 'Up',
            'Down': 'Down',
            'Zoom In': 'ZoomIn',
            'Zoom Out': 'ZoomOut',
            'Stop': 'Stop'
        }

        if States[value] == 'Stop':
            CmdString = 'xCommand Call FarEndControl Camera Stop\r'
            self.__SetHelper('FarEndCameraPTZ', CmdString, value, qualifier)
        else:
            CmdString = 'xCommand Call FarEndControl Camera Move Value: {0}\r'.format(States[value])
            self.__SetHelper('FarEndCameraPTZ', CmdString, value, qualifier)

    def SetFarEndCameraSourceSelect(self, value, qualifier):

        if 1 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl Source Select SourceId: {0}\r'.format(value)
            self.__SetHelper('FarEndCameraSourceSelect', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSourceSelect')

    def SetH323AliasE164Command(self, value, qualifier):

        CmdString = 'xConfiguration H323 H323Alias E164: \"{0}\"\r'.format(value)
        self.__SetHelper('H323AliasE164Command', CmdString, value, qualifier)

    def SetH323AliasIDCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 H323Alias ID: \"{0}\"\r'.format(value)
        self.__SetHelper('H323AliasIDCommand', CmdString, value, qualifier)

    def SetH323AuthenticationMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        CmdString = 'xConfiguration H323 Authentication Mode: {0}\r'.format(States[value])
        self.__SetHelper('H323AuthenticationMode', CmdString, value, qualifier)

    def SetH323CallSetupMode(self, value, qualifier):

        States = {
            'Direct': 'Direct',
            'Gatekeeper': 'Gatekeeper'
        }

        CmdString = 'xConfiguration H323 CallSetup Mode: {0}\r'.format(States[value])
        self.__SetHelper('H323CallSetupMode', CmdString, value, qualifier)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Gatekeeper Address: \"{0}\"\r'.format(value)
        self.__SetHelper('H323GatekeeperAddressCommand', CmdString, value, qualifier)

    def UpdateH323GatekeeperAddressStatus(self, value, qualifier):

        self.__UpdateHelper('H323GatekeeperAddressStatus', 'xStatus H323 Gatekeeper Address\r', value, qualifier)

    def __MatchH323GatekeeperAddressStatus(self, match, tag):
        self.WriteStatus('H323GatekeeperAddressStatus', match.group(1).decode(), None)

    def UpdateH323GatekeeperStatus(self, value, qualifier):

        self.__UpdateHelper('H323GatekeeperStatus', 'xStatus H323 Gatekeeper Status\r', value, qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        States = {
            'Required': 'Required',
            'Discovering': 'Discovering',
            'Discovered': 'Discovered',
            'Authenticating': 'Authenticating',
            'Authenticated': 'Authenticated',
            'Registering': 'Registering',
            'Registered': 'Registered',
            'Inactive': 'Inactive',
            'Rejected': 'Rejected'
        }

        self.WriteStatus('H323GatekeeperStatus', States[match.group(1).decode()], None)

    def SetH323LoginNameCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Authentication LoginName: \"{0}\"\r'.format(value)
        self.__SetHelper('H323LoginNameCommand', CmdString, value, qualifier)

    def SetH323PasswordCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Authentication Password: \"{0}\"\r'.format(value)
        self.__SetHelper('H323PasswordCommand', CmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320': 'h320',
            'H323': 'h323',
            'SIP': 'sip',
            'Auto': 'Auto',
        }

        protocol = qualifier['Protocol']

        if value in ['Accept', 'Reject']:
            self.__SetHelper('Hook', 'xCommand Call {0}\r'.format(value.replace(' ', '')), value, qualifier)
        elif 'Resume' in value or 'Disconnect' in value or 'Hold' in value or 'Join' in value:
            val = value.split(' ')
            cmd = val[0]
            index = int(val[1]) - 1
            try:
                self.__SetHelper('Hook', 'xCommand Call {0} CallId: {1}\r'.format(cmd, self.__CallID[index]), value, qualifier)
            except IndexError:
                self.Discard('Invalid Command for SetHook')
        elif value is 'Dial':
            number = qualifier['Number']
            if number:
                if protocol == 'Auto':
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\" Protocol:{1}\r'.format(number, Protocol_Values[protocol]), value, qualifier)
            else:
                self.Discard('Invalid Command for SetHook')
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIPv4AddressCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(value)
        self.__SetHelper('IPv4AddressCommand', CmdString, value, qualifier)

    def UpdateIPv4AddressStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4AddressStatus', 'xStatus Network 1 IPv4 Address\r', value, qualifier)

    def __MatchIPv4AddressStatus(self, match, tag):
        self.WriteStatus('IPv4AddressStatus', match.group(1).decode(), None)

    def SetIPv4GatewayCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(value)
        self.__SetHelper('IPv4GatewayCommand', CmdString, value, qualifier)

    def UpdateIPv4GatewayStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4GatewayStatus', 'xStatus Network 1 IPv4 Gateway\r', value, qualifier)

    def __MatchIPv4GatewayStatus(self, match, tag):
        self.WriteStatus('IPv4GatewayStatus', match.group(1).decode(), None)

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(value)
        self.__SetHelper('IPv4SubnetMaskCommand', CmdString, value, qualifier)

    def UpdateIPv4SubnetMaskStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4SubnetMaskStatus', 'xStatus Network 1 IPv4 SubnetMask\r', value, qualifier)

    def __MatchIPv4SubnetMaskStatus(self, match, tag):
        self.WriteStatus('IPv4SubnetMaskStatus', match.group(1).decode(), None)

    def SetLayoutSet(self, value, qualifier):

        TargetStates = {
            'Local': 'Local',
            'Remote': 'Remote'
        }

        Target = TargetStates[qualifier['Target']]

        States = {
            'Auto': 'auto',
            'Custom': 'custom',
            'Equal': 'equal',
            'Overlay': 'overlay',
            'Prominent': 'prominent',
            'Single': 'single'
        }

        CmdString = 'xCommand Video Layout LayoutFamily Set Target: {0} LayoutFamily:{1}\r'.format(Target, States[value])
        self.__SetHelper('LayoutSet', CmdString, value, qualifier)

    def SetMicrophoneLevel(self, value, qualifier):

        if 0 <= value <= 70 and 1 <= int(qualifier['Microphone']) <= 8:
            CmdString = 'xConfiguration Audio Input Microphone {0} Level: {1}\r'.format(qualifier['Microphone'], value)
            self.__SetHelper('MicrophoneLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneLevel')

    def SetMicrophoneMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        if 1 <= int(qualifier['Microphone']) <= 8:
            CmdString = 'xConfiguration Audio Input Microphone {0} Mode: {1}\r'.format(qualifier['Microphone'], States[value])
            self.__SetHelper('MicrophoneMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def SetMuteAllMicrophones(self, value, qualifier):

        States = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        CmdString = 'xCommand Audio Microphones {0}\r'.format(States[value])
        self.__SetHelper('MuteAllMicrophones', CmdString, value, qualifier)

    def UpdateMuteAllMicrophones(self, value, qualifier):
        self.__UpdateHelper('MuteAllMicrophones', 'xStatus Audio Microphones Mute\r', value, qualifier)

    def __MatchMuteAllMicrophones(self, match, tag):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        self.WriteStatus('MuteAllMicrophones', States[match.group(1).decode()], None)

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True
        
        if 1 <= value <= self._NumberofPhonebookSearch:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': int(value)})
            if number and number != '***End of list***':
                number = number[number.find(' : ') + 3:]
                commandstring = 'xCommand Dial Number:"{0}"\r'.format(number)
                self.Send(commandstring)

    def SetPhonebookFolderIDNavigation(self, value, qualifier):
        self.Debug = True
        
        if self.FolderLimit != 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down']:
                if 'Page' in value:
                    NumberOfAdvance = self._NumberofPhonebookFolderSearch
                else:
                    NumberOfAdvance = 1

                if 'Down' in value and self.FolderMin <= len(self.folderList):
                    self.FolderMin += NumberOfAdvance
                    self.FolderLimit += NumberOfAdvance
                elif 'Up' in value:
                    self.FolderMin -= NumberOfAdvance
                    self.FolderLimit -= NumberOfAdvance

                if self.FolderMin < 1:
                    self.FolderMin = 1

                if self.FolderLimit < self._NumberofPhonebookFolderSearch:
                    self.FolderLimit = self._NumberofPhonebookFolderSearch

            button = 1
            for i in range(self.FolderMin, self.FolderLimit + 1):
                if str(i) in self.folderList:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']),
                                     {'Button': button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
            else:
                self.Discard('Invalid Command for SetPhonebookFolderIDNavigation')

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True
        
        if self.MaxLabel != 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down']:
                if 'Page' in value:
                    NumberOfAdvance = self._NumberofPhonebookSearch
                else:
                    NumberOfAdvance = 1

                if 'Down' in value and self.MinLabel <= len(self.newList):
                    self.MinLabel += NumberOfAdvance
                    self.MaxLabel += NumberOfAdvance
                elif 'Up' in value:
                    self.MinLabel -= NumberOfAdvance
                    self.MaxLabel -= NumberOfAdvance

                if self.MinLabel < 1:
                    if self.Offset != 0:
                        self.SetPhonebookUpdate('Previous Search', qualifier)
                        self.MinLabel = len(self.newList) - (self._NumberofPhonebookSearch - 1)
                        self.MaxLabel = len(self.newList)
                    else:
                        self.MinLabel = 1

                if self.MaxLabel < self._NumberofPhonebookSearch:
                    self.MaxLabel = self._NumberofPhonebookSearch

                if self.MaxLabel > len(self.newList) and len(self.newList) == self._NumberofContactsPerSearch:
                    self.SetPhonebookUpdate('Next Search', qualifier)

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):
        self.Debug = True
        
        if self.folderList:
            folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
            if folderName != '***End of list***':
                self.FolderIDNumber = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName][0]
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDSearchSet')

    def SetPhonebookFolderIDUpdate(self, value, qualifier):
        self.Debug = True
        
        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: {1}\r'.format(phonebookValue, self._NumberofFoldersPerSearch)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
                res = res.decode()
                self.folderList = {}
                folderName = findall(self.FolderNameRex, res)
                folderID = findall(self.FolderIDRex, res)

                for i, name in folderName:
                    self.folderList[i] = {'Name': name}

                for i, id_ in folderID:
                    if i in self.folderList:
                        self.folderList[i]['ID'] = id_
                    else:
                        self.folderList[i] = {'ID': id_}

                button = 1
                for i in range(1, self._NumberofPhonebookFolderSearch + 1):
                    if str(i) in self.folderList:
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']),
                                         {'Button': int(i)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate')

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True
        
        if value == 'Refresh':
            self.Offset = 0
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
        elif value == 'Next Search' and len(self.newList) == self._NumberofContactsPerSearch:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset += self._NumberofContactsPerSearch
        elif value == 'Previous Search':
            self.Offset -= self._NumberofContactsPerSearch

        if self.Offset < 0:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset = 0

        self.WriteStatus('PhonebookSearchResult', '***Loading Contacts***', {'Button': 1})
        for i in range(2, int(self._NumberofPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '...', {'Button': i})

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
        self.Debug = True
        
        phonebookType = qualifier['Phonebook Type']
        contact = qualifier['Contact']
        folderID = qualifier['FolderID']
        if phonebookType in ['Corporate', 'Local']:
            if contact:
                contact = 'SearchString: "{0}" '.format(contact)
            else:
                contact = ''

            if folderID:
                fldID = 'FolderID:"{0}" '.format(folderID)
            else:
                fldID = ''
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1}SearchField: Name ContactType: Contact {2} Offset: {3} Limit: {4}\r'.format(phonebookType, contact, fldID, self.Offset, self._NumberofContactsPerSearch)
            res = self.SendAndWait(cmdStr, 15, deliTag=b'** end')
            if res:
                res = res.decode()
                self.newList = {}
                nameList = findall(self.dirName, res)
                numberList = findall(self.dirNumber, res)

                for i, name in nameList:
                    self.newList[i] = {'Name': name}

                for i, number in numberList:
                    if i in self.newList:
                        self.newList[i]['Number'] = number
                    else:
                        self.newList[i] = {'Number': number}

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookUpdateHandler')

    def SetPhonebookWriteHandler(self, value, qualifier):
        self.Debug = True
        
        button = 1
        for i in range(self.MinLabel, self.MaxLabel + 1):
            if str(i) in self.newList:
                self.WriteStatus('PhonebookSearchResult',
                                 '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']),
                                 {'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPresentation(self, value, qualifier):

        States = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            'Stop': 'Stop',
        }

        instanceID = qualifier['Instance']
        if States[value] and 1 <= int(instanceID) <= 6:
            if 'Stop' == value:
                cmdState = 'xCommand Presentation Stop Instance:{0}\r'.format(instanceID)
            else:
                cmdState = 'xCommand Presentation Start ConnectorId:{0} Instance:{1}\r'.format(States[value], instanceID)
            if cmdState:
                self.__SetHelper('Presentation', cmdState, value, qualifier)
            else:
                self.Discard('Invalid Command for SetPresentation')
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):
        if 1 <= int(qualifier['Instance']) <= 6:
            self.__UpdateHelper('Presentation', 'xStatus Conference Presentation LocalInstance {0} Source\r'.format(qualifier['Instance']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentation')

    def __MatchPresentation(self, match, tag):
        value = match.group(2).decode()
        if value == '0':
            value = 'Stop'
        self.WriteStatus('Presentation', value, {'Instance': match.group(1).decode()})

    def __MatchPresentationStop(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('Presentation', 'Stop', {'Instance': instanceID})

    def UpdatePresentationMode(self, value, qualifier):

        self.__UpdateHelper('PresentationMode', 'xStatus Conference Presentation Mode\r', value, qualifier)

    def __MatchPresentationMode(self, match, tag):

        States = {
            'Off': 'Off',
            'Sending': 'Sending',
            'Receiving': 'Receiving'
        }

        self.WriteStatus('PresentationMode', States[match.group(1).decode()], None)

    def SetPresentationDefaultSource(self, value, qualifier):

        if 1 <= int(value) <= 4:
            CmdString = 'xConfiguration Video Presentation DefaultSource: {}\r'.format(value)
            self.__SetHelper('PresentationDefaultSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetPresentationSendingMode(self, value, qualifier):

        States = {
            'Local and Remote': 'LocalRemote',
            'Local Only': 'LocalOnly'
        }

        connectorID = int(qualifier['Connector ID'])
        if 1 <= connectorID <= 5:
            CmdString = 'xCommand Presentation Start SendingMode: {0} connectorID: {1}\r'.format(States[value], connectorID)
            self.__SetHelper('PresentationSendingMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationSendingMode')

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 5:
            CmdString = 'xStatus Conference Presentation LocalInstance {0} SendingMode\r'.format(instanceID)
            self.__UpdateHelper('PresentationSendingModeStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        States = {
            'LocalRemote': 'Local and Remote',
            'LocalOnly': 'Local Only',
            'Off': 'Off',
        }

        self.WriteStatus('PresentationSendingModeStatus', States[match.group(2).decode()], {'Instance': match.group(1).decode()})

    def __MatchPresentationSendingModeStatusStop(self, match, tag):
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance': match.group(1).decode()})

    def SetPresentationPIPPosition(self, value, qualifier):

        States = {
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight',
            'Upper Center': 'UpperCenter',
            'Upper Left': 'UpperLeft',
            'Upper Right': 'UpperRight'
        }

        CmdString = 'xCommand Video PresentationPIP Set Position: {0}\r'.format(States[value])
        self.__SetHelper('PresentationPIPPosition', CmdString, value, qualifier)

    def SetSelfView(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        CmdString = 'xCommand Video Selfview Set Mode: {0}\r'.format(States[value])
        self.__SetHelper('SelfView', CmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):
        self.__UpdateHelper('SelfView', 'xStatus Video Selfview Mode\r', value, qualifier)

    def __MatchSelfView(self, match, tag):

        States = {
            'On': 'On',
            'Off': 'Off'
        }

        self.WriteStatus('SelfView', States[match.group(1).decode()], None)

    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off',
            'Current': 'Current'
        }

        CmdString = 'xConfiguration Video Selfview Default FullscreenMode: {0}\r'.format(States[value])
        self.__SetHelper('SelfViewDefaultFullscreenMode', CmdString, value, qualifier)

    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', 'xStatus Video Selfview FullscreenMode\r', value, qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        States = {
            'On': 'On',
            'Off': 'Off',
            'Current': 'Current'
        }

        self.WriteStatus('SelfViewDefaultFullscreenMode', States[match.group(1).decode()], None)

    def SetSelfViewPosition(self, value, qualifier):

        States = {
            'Upper Left': 'UpperLeft',
            'Upper Center': 'UpperCenter',
            'Upper Right': 'UpperRight',
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight'
        }

        CmdString = 'xConfiguration Video Selfview Default PIPPosition: {0}\r'.format(States[value])
        self.__SetHelper('SelfViewPosition', CmdString, value, qualifier)

    def UpdateSelfViewPosition(self, value, qualifier):
        self.__UpdateHelper('SelfViewPosition', 'xStatus Video Selfview PIPPosition\r', value, qualifier)

    def __MatchSelfViewPosition(self, match, tag):

        States = {
            'UpperLeft': 'Upper Left',
            'UpperCenter': 'Upper Center',
            'UpperRight': 'Upper Right',
            'CenterLeft': 'Center Left',
            'CenterRight': 'Center Right',
            'LowerLeft': 'Lower Left',
            'LowerRight': 'Lower Right'
        }

        value = States[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('SelfViewPosition', value, None)

    def SetStandby(self, value, qualifier):

        States = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        CmdString = 'xCommand Standby {0}\r'.format(States[value])
        self.__SetHelper('Standby', CmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):
        self.__UpdateHelper('Standby', 'xStatus Standby State\r', value, qualifier)

    def __MatchStandby(self, match, tag):

        States = {
            'Off': 'On',
            'Standby': 'Off'
        }

        self.WriteStatus('Standby', States[match.group(1).decode()], None)

    def SetVideoSetMainVideoSource(self, value, qualifier):

        if 1 <= int(qualifier['Connector ID']) <= 5:
            CmdString = 'xCommand Video Input SetMainVideoSource ConnectorID: {}\r'.format(qualifier['Connector ID'])
            self.__SetHelper('VideoSetMainVideoSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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