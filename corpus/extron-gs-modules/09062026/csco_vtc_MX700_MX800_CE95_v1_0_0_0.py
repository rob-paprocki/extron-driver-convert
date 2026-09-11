from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search


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
        self.devicePassword = None

        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofPhonebookSearch = 5

        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ActiveSpeakerPIPPosition': { 'Status': {}},
            'AudioInputLineChannel': {'Parameters':['Input'], 'Status': {}},
            'AudioInputLineLevel': {'Parameters':['Input'], 'Status': {}},
            'AudioInputLineMode': {'Parameters':['Input'], 'Status': {}},
            'AudioInputLineSource': {'Parameters':['Input'], 'Status': {}},
            'AudioOutputLineChannel': {'Parameters':['Output'], 'Status': {}},
            'AudioOutputLineLevel': {'Parameters':['Output'], 'Status': {}},
            'AudioOutputLineMode': {'Parameters':['Output'], 'Status': {}},
            'AudioVolume': { 'Status': {}},
            'AudioVolumeMute': { 'Status': {}},
            'CallHistory': {'Parameters':['Button','Detail Type'], 'Status': {}},
            'CallHistoryAcknowledgeAllMissedCalls': { 'Status': {}},
            'CallHistoryAcknowledgeMissedCall': {'Parameters':['Missed Call Number'], 'Status': {}},
            'CallHistoryNavigation': { 'Status': {}},
            'CallHistoryRefresh': { 'Status': {}},
            'CallHistorySelect': {'Parameters':['Button'], 'Status': {}},
            'CallStatus': {'Parameters':['Call'], 'Status': {}},
            'CallStatusRP': { 'Status': {}},
            'CallStatusType': {'Parameters':['Call'], 'Status': {}},
            'CameraAssignedSerialNumberCommand': {'Parameters':['Camera ID'], 'Status': {}},
            'CameraAutofocusCommand': {'Parameters':['Camera ID'], 'Status': {}},
            'CameraAutofocusMode': {'Parameters':['Camera ID'], 'Status': {}},
            'CameraFocus': {'Parameters':['Camera ID'], 'Status': {}},
            'CameraPan': {'Parameters':['Camera ID','Pan Speed'], 'Status': {}},
            'CameraPreset': { 'Status': {}},
            'CameraPresetStore': {'Parameters':['Camera ID','Default Position'], 'Status': {}},
            'CameraSpeakerTrack': { 'Status': {}},
            'CameraSpeakerTrackTrackingMode': { 'Status': {}},
            'CameraTilt': {'Parameters':['Camera ID','Tilt Speed'], 'Status': {}},
            'CameraZoom': {'Parameters':['Camera ID','Zoom Speed'], 'Status': {}},
            'ConferenceAutoAnswerDelay': { 'Status': {}},
            'ConferenceAutoAnswerMode': { 'Status': {}},
            'ConferenceAutoAnswerMute': { 'Status': {}},
            'ConferenceDefaultCallProtocol': { 'Status': {}},
            'ConferenceDefaultCallRate': { 'Status': {}},
            'ConferenceDoNotDisturb': { 'Status': {}},
            'ConferenceEncryptionMode': { 'Status': {}},
            'ConferenceFarEndControlMode': { 'Status': {}},
            'ConferenceSpeakerLock': {'Parameters':['Speaker'], 'Status': {}},
            'DisplayName': {'Parameters':['Call'], 'Status': {}},
            'DNSDomainNameCommand': { 'Status': {}},
            'DNSServerAddressCommand': {'Parameters':['Server'], 'Status': {}},
            'DNSServerAddressStatus': {'Parameters':['Server'], 'Status': {}},
            'DTMF': { 'Status': {}},
            'FarEndCameraPresetRecall': { 'Status': {}},
            'FarEndCameraPTZ': { 'Status': {}},
            'FarEndCameraSourceSelect': { 'Status': {}},
            'H323AliasE164Command': { 'Status': {}},
            'H323AliasIDCommand': { 'Status': {}},
            'H323AuthenticationMode': { 'Status': {}},
            'H323CallSetupMode': { 'Status': {}},
            'H323GatekeeperAddressCommand': { 'Status': {}},
            'H323GatekeeperAddressStatus': { 'Status': {}},
            'H323GatekeeperStatus': { 'Status': {}},
            'H323LoginNameCommand': { 'Status': {}},
            'H323PasswordCommand': { 'Status': {}},
            'Hook': {'Parameters':['Protocol'], 'Status': {}},
            'IPv4AddressCommand': { 'Status': {}},
            'IPv4AddressStatus': { 'Status': {}},
            'IPv4GatewayCommand': { 'Status': {}},
            'IPv4GatewayStatus': { 'Status': {}},
            'IPv4SubnetMaskCommand': { 'Status': {}},
            'IPv4SubnetMaskStatus': { 'Status': {}},
            'LayoutSet': {'Parameters':['Target'], 'Status': {}},
            'MicrophoneLevel': {'Parameters':['Microphone'], 'Status': {}},
            'MicrophoneMode': {'Parameters':['Microphone'], 'Status': {}},
            'MuteAllMicrophones': { 'Status': {}},
            'PhonebookFolderIDNavigation': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters':['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': { 'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookSearch': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters':['Button'], 'Status': {}},
            'PhonebookSearchSet': { 'Status': {}},
            'PhonebookUpdate': {'Parameters':['Phonebook Type'], 'Status': {}},
            'Presentation': {'Parameters':['Instance'], 'Status': {}},
            'PresentationDefaultSource': { 'Status': {}},
            'PresentationMode': { 'Status': {}},
            'PresentationPIPPosition': { 'Status': {}},
            'PresentationSendingMode': {'Parameters':['Connector ID'], 'Status': {}},
            'PresentationSendingModeStatus': {'Parameters':['Instance'], 'Status': {}},
            'PresentationSourceStatus': {'Parameters':['Instance'], 'Status': {}},
            'RemoteNumber': {'Parameters':['Call'], 'Status': {}},
            'SelfView': { 'Status': {}},
            'SelfViewDefaultFullscreenMode': { 'Status': {}},
            'SelfViewPosition': { 'Status': {}},
            'Standby': { 'Status': {}},
            'VideoSetMainVideoSource': {'Parameters':['Connector ID'], 'Status': {}},
        }

        self.folderList = {}
        self.newList = {}

        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n') # Call status
        self.callStatusTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n') # Call Status Type
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "(.*)"\r\n') # Display Name status
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "(.*)"\r\n') # Remote Number status
        self.callID = compile('\*s Call (\d+) Status: \w+\r\n')  # Call ID
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
        self._NumberofPhonebookResults = 50

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
        self.lastCallHist = 0
        self.advanceCallHist = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*s Video PIP ActiveSpeaker Position: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchActiveSpeakerPIPPosition, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchAudioVolume, None)
            self.AddMatchString(compile(b'\*s Audio VolumeMute: (On|Off)\r\n'), self.__MatchAudioVolumeMute, None)
            self.AddMatchString(compile(b'\*r CallHistoryRecentsResult [\s\S]+\*\* end\r\n'), self.__MatchCallHistory, None)
            self.AddMatchString(compile(b'xstatus call\r\n\*\* end\r\n'), self.__MatchCallStatusIdle, None)
            self.AddMatchString(compile(b'\*s Call (\d+) [\s\S]+\*\* end\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchConferenceDoNotDisturb, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-3]) Address: "([0-9.]{7,15})"\r\n'), self.__MatchDNSServerAddressStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{7,15})"\r\n'), self.__MatchH323GatekeeperAddressStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4AddressStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4GatewayStatus, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4SubnetMaskStatus, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMuteAllMicrophones, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-5])\r\n'), self.__MatchPresentation, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-5])\r\n'), self.__MatchPresentationSourceStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationMode, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusStop, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*s Video Selfview FullscreenMode: (On|Off|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|Off|EnteringStandby|Halfwake)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchAuthentication, None)

    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):
        self._CallHistoryOccurrenceType= value

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
        self._NumberofCallHistory= int(value)

    @property
    def NumberofPhonebookFolderSearch(self):
        return self._NumberofPhonebookFolderSearch

    @NumberofPhonebookFolderSearch.setter
    def NumberofPhonebookFolderSearch(self, value):
        self._NumberofPhonebookFolderSearch= int(value)

    @property
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        self._NumberofPhonebookSearch= int(value)

    def __MatchAuthentication(self, match, tag):
        self.SetAuthentication(None, None)

    def SetAuthentication(self, value, qualifier):
        self.Send(b'\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername+'\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword( None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetActiveSpeakerPIPPosition(self, value, qualifier):

        States = {
            'Center Left'  : 'CenterLeft',
            'Center Right' : 'CenterRight',
            'Lower Left'   : 'LowerLeft',
            'Lower Right'  : 'LowerRight',
            'Upper Center' : 'UpperCenter',
            'Upper Left'   : 'UpperLeft',
            'Upper Right'  : 'UpperRight'
        }

        CmdString = 'xCommand Video ActiveSpeakerPIP Set Position: {}\r'.format(States[value])
        self.__SetHelper('ActiveSpeakerPIPPosition', CmdString, value, qualifier)

    def UpdateActiveSpeakerPIPPosition(self, value, qualifier):
        self.__UpdateHelper('ActiveSpeakerPIPPosition', 'xStatus Video ActiveSpeaker PIPPosition\r' , value, qualifier)

    def __MatchActiveSpeakerPIPPosition(self, match, tag):

        States = {
            'CenterLeft'  : 'Center Left',
            'CenterRight' : 'Center Right',
            'LowerLeft'   : 'Lower Left',
            'LowerRight'  : 'Lower Right',
            'UpperCenter' : 'Upper Center',
            'UpperLeft'   : 'Upper Left',
            'UpperRight'  : 'Upper Right'
        }

        value = States[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('ActiveSpeakerPIPPosition', value, None)

    def SetAudioInputLineChannel(self, value, qualifier):

        States = {
            'Left'  : 'Left',
            'Mono'  : 'Mono',
            'Right' : 'Right'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {} Channel: {}\r'.format(qualifier['Input'],States[value])
            self.__SetHelper('AudioInputLineChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineChannel')

    def SetAudioInputLineLevel(self, value, qualifier):

        if 0 <= value <= 24 and 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {} Level: {}\r'.format(qualifier['Input'], value)
            self.__SetHelper('AudioInputLineLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineLevel')

    def SetAudioInputLineMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        if 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {} Mode: {}\r'.format(qualifier['Input'], States[value])
            self.__SetHelper('AudioInputLineMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineMode')

    def SetAudioInputLineSource(self, value, qualifier):

        if 1 <= int(value) <= 5 and 1 <= int(qualifier['Input']) <= 4:
            CmdString = 'xConfiguration Audio Input Line {} VideoAssociation VideoInputSource: {}\r'.format(qualifier['Input'], value)
            self.__SetHelper('AudioInputLineSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioInputLineSource')

    def SetAudioOutputLineChannel(self, value, qualifier):

        States = {
            'Left'  : 'Left',
            'Mono'  : 'Mono',
            'Right' : 'Right'
        }

        if 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {} Channel: {}\r'.format(qualifier['Output'], States[value])
            self.__SetHelper('AudioOutputLineChannel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineChannel')

    def SetAudioOutputLineLevel(self, value, qualifier):

        if -24 <= value <= 0 and 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {} Level: {}\r'.format(qualifier['Output'], value)
            self.__SetHelper('AudioOutputLineLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineLevel')

    def SetAudioOutputLineMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        if 1 <= int(qualifier['Output']) <= 6:
            CmdString = 'xConfiguration Audio Output Line {} Mode: {}\r'.format(qualifier['Output'], States[value])
            self.__SetHelper('AudioOutputLineMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutputLineMode')

    def SetAudioVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = 'xCommand Audio Volume Set Level: {}\r'.format(value)
            self.__SetHelper('AudioVolume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):
        self.__UpdateHelper('AudioVolume', 'xStatus Audio Volume\r', value, qualifier)

    def __MatchAudioVolume(self, match, tag):
        self.WriteStatus('AudioVolume',  int(match.group(1).decode()) , None)

    def SetAudioVolumeMute(self, value, qualifier):

        States = {
            'On'  : 'Mute',
            'Off' : 'Unmute'
        }

        CmdString = 'xCommand Audio Volume {}\r'.format(States[value])
        self.__SetHelper('AudioVolumeMute', CmdString, value, qualifier)

    def UpdateAudioVolumeMute(self, value, qualifier):
        self.__UpdateHelper('AudioVolumeMute', 'xStatus Audio VolumeMute\r' , value, qualifier)

    def __MatchAudioVolumeMute(self, match, tag):
        self.WriteStatus('AudioVolumeMute',  match.group(1).decode() , None)

    def SetCallHistoryRefresh(self, value, qualifier):
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        CmdString = 'xCommand CallHistory Recents Filter: All Offset: {} Limit: {} Order: Occurrence{}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        self.Send(CmdString)

    def __MatchCallHistory(self, match, tag):

        res = match.group(0).decode()
        if self.prevCallHist != res:
            self.prevCallHist = res
            self.advanceCallHist = True
            displayNameList = dict(findall(self.displayName, res))
            callBackNumberList = dict(findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(findall(self.occurrenceType, res))
            occurrenceCountList = dict(findall(self.occurrenceCount, res))

            for btn in range(1, self._NumberofCallHistory+1):
                button = str(btn)
                index = str(btn-1)

                if index in displayNameList:
                    self.WriteStatus('CallHistory', displayNameList[index], {'Button':button, 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory', callBackNumberList[index], {'Button':button, 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory', lastOccurrenceTimeList[index], {'Button':button, 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', occurrenceTypeList[index], {'Button':button, 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory', occurrenceCountList[index], {'Button':button, 'Detail Type' : 'Occurrence Count'})
                else:
                    self.WriteStatus('CallHistory', '', {'Button':button, 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory', '', {'Button':button, 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory', '', {'Button':button, 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', '', {'Button':button, 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory', '', {'Button':button, 'Detail Type' : 'Occurrence Count'})
                    self.advanceCallHist = False

    def SetCallHistoryNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self._NumberofCallHistory
            else:
                NumberOfAdvance = 1

            if 'Down' in value and self.advanceCallHist:
                self.startCallHist += NumberOfAdvance
            elif 'Up' in value:
                self.startCallHist -= NumberOfAdvance

            if self.startCallHist < 1:
                self.startCallHist = 1

            self.__UpdateCallHistoryHelper(value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistorySelect(self, value, qualifier):

        number = self.ReadStatus('CallHistory', {'Button' : str(qualifier['Button']), 'Detail Type': 'Callback Number'})
        if number:
            self.SetHook('Dial', {'Number': number, 'Protocol': 'Auto'})

    def SetCallHistoryAcknowledgeAllMissedCalls(self, value, qualifier):

        self.__SetHelper('CallHistoryAcknowledgeAllMissedCalls', 'xCommand CallHistory AcknowledgeAllMissedCalls\r', value, qualifier)

    def SetCallHistoryAcknowledgeMissedCall(self, value, qualifier):

        if 1 <= int(qualifier['Missed Call Number']) <= 2147483647:
            CmdString = 'xCommand CallHistory AcknowledgeMissedCall CallHistoryID: {}\r'.format(qualifier['Missed Call Number'])
            self.__SetHelper('CallHistoryAcknowledgeMissedCall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallHistoryAcknowledgeMissedCall')

    def UpdateCallStatus(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateDisplayName(self, value, qualifier):
        self.__UpdateHelper('DisplayName', 'xstatus call\r', value, qualifier)

    def UpdateRemoteNumber(self, value, qualifier):
        self.__UpdateHelper('RemoteNumber', 'xstatus call\r', value, qualifier)

    def UpdateCallStatusType(self, value, qualifier):
        self.__UpdateHelper('CallStatusType', 'xstatus call\r', value, qualifier)

    def __MatchCallStatusIdle(self, match, tag):

        for index in range (1, 6):
            self.WriteStatus('CallStatus', 'Idle', {'Call':str(index)})
            self.WriteStatus('DisplayName', '', {'Call':str(index)})
            self.WriteStatus('RemoteNumber', '', {'Call':str(index)})
            self.WriteStatus('CallStatusType', 'Unknown', {'Call':str(index)})

    def __MatchCallStatus(self, match, tag):

        callValue = {
            'Idle'           :'Idle',
            'Dialling'       :'Dialing',
            'Ringing'        :'Ringing',
            'Connecting'     :'Connecting',
            'Connected'      :'Connected',
            'Disconnecting'  :'Disconnecting',
            'OnHold'         :'On Hold',
            'EarlyMedia'     :'Early Media',
            'Preserved'      :'Preserved',
            'RemotePreserved':'Remote Preserved',
        }

        res = match.group(0).decode()
        self.__CallID = findall(self.callID, res)
        callList = findall(self.callStatus, res)
        displayNameList = findall(self.displayNamePattern, res)
        remoteNumberList = findall(self.remoteNumberPattern, res)
        callStatusTypeList = findall(self.callStatusTypePattern, res)
        index = 1
        for index in range(1, len(callList) + 1):
            self.WriteStatus('CallStatus', callValue[callList[index - 1]], {'Call':str(index)})
            self.WriteStatus('DisplayName', displayNameList[index - 1], {'Call': str(index)})
            self.WriteStatus('RemoteNumber', remoteNumberList[index - 1], {'Call': str(index)})
            self.WriteStatus('CallStatusType', callStatusTypeList[index - 1], {'Call': str(index)})
        else:
            index += 1
            while index <= 5:
                self.WriteStatus('CallStatus', 'Idle', {'Call':str(index)})
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
                index += 1

    def SetCameraAssignedSerialNumberCommand(self, value, qualifier):

        if 1 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xConfiguration Cameras Camera {} AssignedSerialNumber: "{}"\r'.format(qualifier['Camera ID'], value)
            self.__SetHelper('CameraAssignedSerialNumberCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAssignedSerialNumberCommand')

    def SetCameraAutofocusCommand(self, value, qualifier):

        if 1 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xCommand Camera TriggerAutofocus CameraId: {}\r'.format(qualifier['Camera ID'])
            self.__SetHelper('CameraAutofocusCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAutofocusCommand')

    def SetCameraAutofocusMode(self, value, qualifier):

        States = {
            'Auto'   : 'Auto',
            'Manual' : 'Manual'
        }

        if 2 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xConfiguration Cameras Camera {} Focus Mode: {}\r'.format(qualifier['Camera ID'], States[value])
            self.__SetHelper('CameraAutofocusMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAutofocusMode')

    def SetCameraFocus(self, value, qualifier):

        States = {
            'Far'  : 'Far',
            'Near' : 'Near',
            'Stop' : 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7:
            CmdString = 'xCommand Camera Ramp CameraId: {} Focus: {}\r'.format(qualifier['Camera ID'],States[value])
            self.__SetHelper('CameraFocus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        States = {
            'Left'  : 'Left',
            'Right' : 'Right',
            'Stop'  : 'Stop'
        }

        CameraPanCmdString = ''
        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Pan Speed']) <= 15:
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{} Pan: Stop\r'.format(qualifier['Camera ID'])
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{} Pan:{} PanSpeed:{}\r'.format(qualifier['Camera ID'], States[value], qualifier['Pan Speed'])

            if CameraPanCmdString:
                self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPan')
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
            'False' : 'False',
            'True'  : 'True'
        }

        DefaultPosition = DefaultPositionStates[qualifier['Default Position']]
        if 1 <= int(value) <= 35 and 1 <= CameraID <= 7:
            CmdString = 'xCommand Camera Preset Store PresetId: {} CameraId: {} DefaultPosition: {}\r'.format(value, CameraID, DefaultPosition)
            self.__SetHelper('CameraPresetStore', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetStore')

    def SetCameraSpeakerTrack(self, value, qualifier):

        States = {
            'Activate'   : 'Activate',
            'Deactivate' : 'Deactivate'
        }

        CmdString = 'xCommand Cameras SpeakerTrack {}\r'.format(States[value])
        self.__SetHelper('CameraSpeakerTrack', CmdString, value, qualifier)

    def SetCameraSpeakerTrackTrackingMode(self, value, qualifier):

        States = {
            'Auto'         : 'Auto',
            'Conservative' : 'Conservative'
        }

        CmdString = 'xConfiguration Cameras SpeakerTrack TrackingMode: {}\r'.format(States[value])
        self.__SetHelper('CameraSpeakerTrackTrackingMode', CmdString, value, qualifier)

    def SetCameraTilt(self, value, qualifier):


        States = {
            'Down' : 'Down',
            'Up'   : 'Up',
            'Stop' : 'Stop'
        }

        CameraTiltCmdString = ''
        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Tilt Speed']) <= 15:
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId: {} Tilt: Stop\r'.format(qualifier['Camera ID'])
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId: {} Tilt: {} TiltSpeed: {}\r'.format(qualifier['Camera ID'], States[value], qualifier['Tilt Speed'])

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraZoom(self, value, qualifier):


        States = {
            'In'   : 'In',
            'Out'  : 'Out',
            'Stop' : 'Stop'
        }

        if 1 <= int(qualifier['Camera ID']) <= 7 and 1 <= int(qualifier['Zoom Speed']) <= 15:
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId: {}\r'.format(qualifier['Camera ID'])
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId: {} Zoom: {} ZoomSpeed: {}\r'.format(qualifier['Camera ID'], States[value], qualifier['Zoom Speed'])

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetConferenceAutoAnswerDelay(self, value, qualifier):

        if 0 <= value <= 50:
            CmdString = 'xConfiguration Conference AutoAnswer Delay: {}\r'.format(value)
            self.__SetHelper('ConferenceAutoAnswerDelay', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceAutoAnswerDelay')

    def SetConferenceAutoAnswerMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        CmdString = 'xConfiguration Conference AutoAnswer Mode: {}\r'.format(States[value])
        self.__SetHelper('ConferenceAutoAnswerMode', CmdString, value, qualifier)

    def SetConferenceAutoAnswerMute(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        CmdString = 'xConfiguration Conference AutoAnswer Mute: {}\r'.format(States[value])
        self.__SetHelper('ConferenceAutoAnswerMute', CmdString, value, qualifier)

    def SetConferenceDefaultCallProtocol(self, value, qualifier):

        States = {
            'Auto' : 'Auto',
            'H323' : 'H323',
            'Sip'  : 'Sip',
            'H320' : 'H320'
        }

        CmdString = 'xConfiguration Conference DefaultCall Protocol: {}\r'.format(States[value])
        self.__SetHelper('ConferenceDefaultCallProtocol', CmdString, value, qualifier)

    def SetConferenceDefaultCallRate(self, value, qualifier):

        if 64 <= value <= 6000:
            CmdString = 'xConfiguration Conference DefaultCall Rate: {}\r'.format(value)
            self.__SetHelper('ConferenceDefaultCallRate', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceDefaultCallRate')

    def SetConferenceDoNotDisturb(self, value, qualifier):

        States = {
            'On'  : 'Activate',
            'Off' : 'Deactivate'
        }

        CmdString = 'xCommand Conference DoNotDisturb {}\r'.format(States[value])
        self.__SetHelper('ConferenceDoNotDisturb', CmdString, value, qualifier)

    def UpdateConferenceDoNotDisturb(self, value, qualifier):
        self.__UpdateHelper('ConferenceDoNotDisturb', 'xStatus Conference DoNotDisturb\r', value, qualifier)

    def __MatchConferenceDoNotDisturb(self, match, tag):

        States = {
            'Active'   : 'On',
            'Inactive' : 'Off'
        }

        self.WriteStatus('ConferenceDoNotDisturb', States[match.group(1).decode()], None)

    def SetConferenceEncryptionMode(self, value, qualifier):

        States = {
            'On'          : 'On',
            'Off'         : 'Off',
            'Best Effort' : 'BestEffort'
        }

        CmdString = 'xConfiguration Conference Encryption Mode: {}\r'.format(States[value])
        self.__SetHelper('ConferenceEncryptionMode', CmdString, value, qualifier)

    def SetConferenceFarEndControlMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        CmdString = 'xConfiguration Conference FarEndControl Mode: {}\r'.format(States[value])
        self.__SetHelper('ConferenceFarEndControlMode', CmdString, value, qualifier)

    def SetConferenceSpeakerLock(self, value, qualifier):

        SpeakerStates = {
            'Local'  : 'local',
            'Remote' : 'remote'
        }

        States = {
            'On'  : 'Set',
            'Off' : 'Release'
        }

        if States[value] == 'Set':
            CmdString = 'xCommand Conference SpeakerLock Set Target: {}\r'.format(SpeakerStates[qualifier['Speaker']])
            self.__SetHelper('ConferenceSpeakerLock', CmdString, value, qualifier)
        elif States[value] == 'Release':
            CmdString = 'xCommand Conference SpeakerLock Release\r'
            self.__SetHelper('ConferenceSpeakerLock', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetConferenceSpeakerLock')

    def SetDNSDomainNameCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 DNS Domain Name: "{}"\r'.format(value)
        self.__SetHelper('DNSDomainNameCommand', CmdString, value, qualifier)

    def SetDNSServerAddressCommand(self, value, qualifier):

        if 1 <= int(qualifier['Server']) <= 3:
            CmdString = 'xConfiguration Network 1 DNS Server {} Address: "{}"\r'.format(qualifier['Server'], value)
            self.__SetHelper('DNSServerAddressCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def UpdateDNSServerAddressStatus(self, value, qualifier):

        if 1 <= int(qualifier['Server']) <= 3:
            CmdString = 'xStatus Network 1 DNS Server {} Address\r'.format(qualifier['Server'])
            self.__UpdateHelper('DNSServerAddressStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDNSServerAddressStatus')

    def __MatchDNSServerAddressStatus(self, match, tag):
        self.WriteStatus('DNSServerAddressStatus',  match.group(2).decode() , {'Server' : match.group(1).decode()})

    def SetDTMF(self, value, qualifier):

        States = {
            '0' : '0',
            '1' : '1',
            '2' : '2',
            '3' : '3',
            '4' : '4',
            '5' : '5',
            '6' : '6',
            '7' : '7',
            '8' : '8',
            '9' : '9',
            '*' : '*',
            '#' : '#'
        }

        CmdString = 'xCommand Call DTMFSend DTMFString: "{}"\r'.format(States[value])
        self.__SetHelper('DTMF', CmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl RoomPreset Activate PresetId: {}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraPTZ(self, value, qualifier):

        States = {
            'Left'     : 'Left',
            'Right'    : 'Right',
            'Up'       : 'Up',
            'Down'     : 'Down',
            'Zoom In'  : 'ZoomIn',
            'Zoom Out' : 'ZoomOut',
            'Stop'     : 'Stop'
        }

        if States[value] == 'Stop':
            CmdString = 'xCommand Call FarEndControl Camera Stop\r'
            self.__SetHelper('FarEndCameraPTZ', CmdString, value, qualifier)
        else:
            CmdString = 'xCommand Call FarEndControl Camera Move Value: {}\r'.format(States[value])
            self.__SetHelper('FarEndCameraPTZ', CmdString, value, qualifier)

    def SetFarEndCameraSourceSelect(self, value, qualifier):

        if 1 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl Source Select SourceId: {}\r'.format(value)
            self.__SetHelper('FarEndCameraSourceSelect', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSourceSelect')

    def SetH323AliasE164Command(self, value, qualifier):

        CmdString = 'xConfiguration H323 H323Alias E164: "{}"\r'.format(value)
        self.__SetHelper('H323AliasE164Command', CmdString, value, qualifier)

    def SetH323AliasIDCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 H323Alias ID: "{}"\r'.format(value)
        self.__SetHelper('H323AliasIDCommand', CmdString, value, qualifier)

    def SetH323AuthenticationMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        CmdString = 'xConfiguration H323 Authentication Mode: {}\r'.format(States[value])
        self.__SetHelper('H323AuthenticationMode', CmdString, value, qualifier)

    def SetH323CallSetupMode(self, value, qualifier):

        States = {
            'Direct'     : 'Direct',
            'Gatekeeper' : 'Gatekeeper'
        }

        CmdString = 'xConfiguration H323 CallSetup Mode: {}\r'.format(States[value])
        self.__SetHelper('H323CallSetupMode', CmdString, value, qualifier)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Gatekeeper Address: "{}"\r'.format(value)
        self.__SetHelper('H323GatekeeperAddressCommand', CmdString, value, qualifier)

    def UpdateH323GatekeeperAddressStatus(self, value, qualifier):

        self.__UpdateHelper('H323GatekeeperAddressStatus', 'xStatus H323 Gatekeeper Address\r' , value, qualifier)

    def __MatchH323GatekeeperAddressStatus(self, match, tag):
        self.WriteStatus('H323GatekeeperAddressStatus',  match.group(1).decode() , None)

    def UpdateH323GatekeeperStatus(self, value, qualifier):

        self.__UpdateHelper('H323GatekeeperStatus', 'xStatus H323 Gatekeeper Status\r' , value, qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        States = {
            'Required'       : 'Required',
            'Discovering'    : 'Discovering',
            'Discovered'     : 'Discovered',
            'Authenticating' : 'Authenticating',
            'Authenticated'  : 'Authenticated',
            'Registering'    : 'Registering',
            'Registered'     : 'Registered',
            'Inactive'       : 'Inactive',
            'Rejected'       : 'Rejected'
        }

        self.WriteStatus('H323GatekeeperStatus',  States[match.group(1).decode()] , None)

    def SetH323LoginNameCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Authentication LoginName: "{}"\r'.format(value)
        self.__SetHelper('H323LoginNameCommand', CmdString, value, qualifier)

    def SetH323PasswordCommand(self, value, qualifier):

        CmdString = 'xConfiguration H323 Authentication Password: "{}"\r'.format(value)
        self.__SetHelper('H323PasswordCommand', CmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320' : 'h320',
            'H323' : 'h323',
            'SIP'  : 'sip',
            'Auto' : 'Auto',
        }

        if value in ['Accept', 'Reject']:
            self.__SetHelper('Hook', 'xCommand Call {}\r'.format(value.replace(' ', '')), value, qualifier)
        elif 'Resume' in value or 'Disconnect' in value or 'Hold' in value or 'Join' in value:
            val = value.split(' ')
            cmd = val[0]
            index = int(val[1]) - 1
            try:
                self.__SetHelper('Hook', 'xCommand Call {} CallId: {}\r'.format(cmd, self.__CallID[index]), value, qualifier)
            except IndexError:
                self.Discard('Invalid Command for SetHook')
        elif value is 'Dial':
            try:
                number =  qualifier['Number']
            except KeyError:
                number = None
            try:
                protocol = qualifier['Protocol']
            except KeyError:
                protocol = 'Auto'
            if number:
                if protocol == 'Auto':
                    self.__SetHelper('Hook', 'xCommand Dial Number:"{}"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:"{}" Protocol:{}\r'.format(number, Protocol_Values[protocol]), value, qualifier)
            else:
                self.Discard('Invalid Command for SetHook, Number qualifier is missing')
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIPv4AddressCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 Address: {}\r'.format(value)
        self.__SetHelper('IPv4AddressCommand', CmdString, value, qualifier)

    def UpdateIPv4AddressStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4AddressStatus', 'xStatus Network 1 IPv4 Address\r', value, qualifier)

    def __MatchIPv4AddressStatus(self, match, tag):
        self.WriteStatus('IPv4AddressStatus',  match.group(1).decode() , None)

    def SetIPv4GatewayCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 Gateway: {}\r'.format(value)
        self.__SetHelper('IPv4GatewayCommand', CmdString, value, qualifier)

    def UpdateIPv4GatewayStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4GatewayStatus', 'xStatus Network 1 IPv4 Gateway\r', value, qualifier)

    def __MatchIPv4GatewayStatus(self, match, tag):
        self.WriteStatus('IPv4GatewayStatus',  match.group(1).decode() , None)

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        CmdString = 'xConfiguration Network 1 IPv4 SubnetMask: {}\r'.format(value)
        self.__SetHelper('IPv4SubnetMaskCommand', CmdString, value, qualifier)

    def UpdateIPv4SubnetMaskStatus(self, value, qualifier):

        self.__UpdateHelper('IPv4SubnetMaskStatus', 'xStatus Network 1 IPv4 SubnetMask\r' , value, qualifier)

    def __MatchIPv4SubnetMaskStatus(self, match, tag):
        self.WriteStatus('IPv4SubnetMaskStatus',  match.group(1).decode() , None)

    def SetLayoutSet(self, value, qualifier):

        TargetStates = {
            'Local' : 'Local',
            'Remote' : 'Remote'
        }

        Target = TargetStates[qualifier['Target']]

        States = {
            'Auto' : 'auto',
            'Custom' : 'custom',
            'Equal' : 'equal',
            'Overlay' : 'overlay',
            'Prominent' : 'prominent',
            'Single' : 'single'
        }

        CmdString = 'xCommand Video Layout LayoutFamily Set Target: {} LayoutFamily:{}\r'.format(Target, States[value])
        self.__SetHelper('LayoutSet', CmdString, value, qualifier)

    def SetMicrophoneLevel(self, value, qualifier):

        if 0 <= value <= 70 and 1 <= int(qualifier['Microphone']) <= 8:
            CmdString = 'xConfiguration Audio Input Microphone {} Level: {}\r'.format(qualifier['Microphone'], value)
            self.__SetHelper('MicrophoneLevel', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneLevel')

    def SetMicrophoneMode(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        if 1 <= int(qualifier['Microphone']) <= 8:
            CmdString = 'xConfiguration Audio Input Microphone {} Mode: {}\r'.format(qualifier['Microphone'], States[value])
            self.__SetHelper('MicrophoneMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneMode')

    def SetMuteAllMicrophones(self, value, qualifier):

        States = {
            'On'  : 'Mute',
            'Off' : 'Unmute'
        }

        CmdString = 'xCommand Audio Microphones {}\r'.format(States[value])
        self.__SetHelper('MuteAllMicrophones', CmdString, value, qualifier)

    def UpdateMuteAllMicrophones(self, value, qualifier):
        self.__UpdateHelper('MuteAllMicrophones', 'xStatus Audio Microphones Mute\r' , value, qualifier)

    def __MatchMuteAllMicrophones(self, match, tag):

        States = {
            'On' : 'On',
            'Off' : 'Off'
        }

        self.WriteStatus('MuteAllMicrophones',  States[match.group(1).decode()] , None)

    def SetPhonebookSearch(self, value, qualifier):

        self.MinLabel = 1
        self.MaxLabel = self._NumberofPhonebookSearch
        self.Offset = 0
        try:
            phonebookType = qualifier['Phonebook Type']
        except KeyError:
            phonebookType = None
        try:
            contact = qualifier['Contact']
        except KeyError:
            contact = None
        try:
            folderID = qualifier['FolderID']
        except KeyError:
            folderID = ''
        if phonebookType and contact:
            self.SetPhonebookUpdateHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookSearch, Missing "Phonebook Type" and "Contact" qualifier')

    def SetPhonebookSearchSet(self, value, qualifier):

        if value < 1 or value > self._NumberofPhonebookSearch:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number:
                number = number[number.find(' : ')+3:]
                self.SetHook('Dial', {'Number': number, 'Protocol': 'Auto'})

    def SetPhonebookFolderIDNavigation(self, value, qualifier):

        if self.FolderLimit != 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down']:
                if 'Page' in value:
                    NumberOfAdvance = self._NumberofPhonebookSearch
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
            for i in range(self.FolderMin,self.FolderLimit + 1):
                if str(i) in self.folderList:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{}'.format(self.folderList[str(i)]['Name']), {'Button':button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button':button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button':i})
            else:
                self.Discard('Invalid Command for SetPhonebookFolderIDNavigation')

    def SetPhonebookNavigation(self, value, qualifier):

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
                        self.SetPhonebookUpdate('Previous Search',qualifier)
                        self.MinLabel = len(self.newList) - 4
                        self.MaxLabel = len(self.newList)
                    else:
                        self.MinLabel = 1
                if self.MaxLabel < self._NumberofPhonebookSearch:
                    self.MaxLabel = self._NumberofPhonebookSearch
                if self.MaxLabel > len(self.newList) and len(self.newList) == self._NumberofPhonebookResults:
                    self.SetPhonebookUpdate('Next Search',qualifier)

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):

        folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button':value})
        number = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName]
        if number:
            self.SetHook('Dial', {'Number': number, 'Protocol': 'Auto'})

    def SetPhonebookFolderIDUpdate(self, value, qualifier):

        try:
            phonebookValue = qualifier['Phonebook Type']
        except KeyError:
            phonebookValue = None
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{} ContactType: Folder Offset: 0 Limit: 50\r'.format(phonebookValue)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
                res = res.decode()
                self.folderList = {}
                folderName = findall(self.FolderNameRex, res)
                folderID = findall(self.FolderIDRex,res)
                for i, name in folderName:
                    self.folderList[i] = {'Name': name}

                for i, id_ in folderID:
                    if i in self.folderList:
                        self.folderList[i]['ID'] = id_
                    else:
                        self.folderList[i] = {'ID': id_}

                button = 1
                for i in range(1,self._NumberofPhonebookFolderSearch + 1):
                    if str(i) in self.folderList:
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{}'.format(self.folderList[str(i)]['Name']), {'Button':int(i)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button':button})
                    button += 1
                    for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button':i})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate, Missing Phonebook Type qualifier')

    def SetPhonebookUpdate(self, value, qualifier):

        if value == 'Refresh':
            self.Offset = 0
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
        elif value == 'Next Search' and len(self.newList) == self._NumberofPhonebookResults:
            self.MinLabel = 1
            self.MaxLabel = 5
            self.Offset += self._NumberofPhonebookResults
        elif value == 'Previous Search':
            self.Offset -= self._NumberofPhonebookResults
        if self.Offset < 0:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset = 0

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):

        try:
            phonebookType = qualifier['Phonebook Type']
        except KeyError:
            phonebookType = None
        try:
            contact = qualifier['Contact']
        except KeyError:
            contact = ''
        try:
            folderID = qualifier['FolderID']
        except KeyError:
            folderID = ''
        if phonebookType in ['Corporate', 'Local']:
            if contact:
                contact = 'SearchString: "{}"'.format(contact)
            if folderID:
                folderID = 'FolderID:"{}" '.format(folderID)
            cmdStr = 'xCommand Phonebook Search PhonebookType:{} {} SearchField: Name ContactType: Contact {} Offset: {} Limit: {}\r'.format(phonebookType, contact, folderID, self.Offset, self._NumberofPhonebookResults)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
                res = res.decode()
                self.newList = {}
                nameList = findall(self.dirName, res)
                numberList = findall(self.dirNumber, res)
                for i, name in nameList:
                    self.newList[i] = {'Name':name}

                for i, number in numberList:
                    if i in self.newList:
                        self.newList[i]['Number'] = number
                    else:
                        self.newList[i] = {'Number': number}

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookUpdateHandler, Missing Phonebook Type qualifier')

    def SetPhonebookWriteHandler(self, value, qualifier):
        button = 1
        for i in range(self.MinLabel,self.MaxLabel + 1):
            if str(i) in self.newList:
                self.WriteStatus('PhonebookSearchResult', '{} : {}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']), {'Button':button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button':button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button':i})

    def SetPresentation(self, value, qualifier):

        States = {
            '1'     :   '1',
            '2'     :   '2',
            '3'     :   '3',
            '4'     :   '4',
            '5'     :   '5',
            'Stop'  :   'Stop',
        }

        instanceID = qualifier['Instance']
        if States[value] and 1 <= int(instanceID) <= 6:
            if 'Stop' == value:
                cmdState = 'xCommand Presentation Stop Instance:{}\r'.format(instanceID)
            else:
                cmdState = 'xCommand Presentation Start ConnectorId:{} Instance:{}\r'.format(States[value], instanceID)
            self.__SetHelper('Presentation', cmdState, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):
        if 1 <= int(qualifier['Instance']) <= 6:
            self.__UpdateHelper('Presentation', 'xStatus Conference Presentation LocalInstance {} Source\r'.format(qualifier['Instance']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentation')

    def __MatchPresentation(self, match, tag):
        value = match.group(2).decode()
        if value == '0':
            value = 'Stop'
        self.WriteStatus('Presentation', value, {'Instance': match.group(1).decode()})

    def UpdatePresentationSourceStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            cmdString = 'xStatus Conference Presentation LocalInstance {} Source\r'.format(instanceID)
            self.__UpdateHelper('PresentationSourceStatus', cmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSourceStatus')

    def __MatchPresentationSourceStatus(self, match, tag):
        instanceID = match.group(1).decode()
        value = match.group(2).decode()
        if value == '0':
            value = 'Off'
        self.WriteStatus('PresentationSourceStatus', value, {'Instance':instanceID})

    def __MatchPresentationStop(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('Presentation', 'Stop', {'Instance':instanceID})

    def UpdatePresentationMode(self, value, qualifier):

        self.__UpdateHelper('PresentationMode', 'xStatus Conference Presentation Mode\r' , value, qualifier)

    def __MatchPresentationMode(self, match, tag):

        States = {
            'Off'       : 'Off',
            'Sending'   : 'Sending',
            'Receiving' : 'Receiving'
        }

        self.WriteStatus('PresentationMode',  States[match.group(1).decode()] , None)

    def SetPresentationDefaultSource(self, value, qualifier):

        if 1 <= int(value) <= 4:
            CmdString = 'xConfiguration Video Presentation DefaultSource: {}\r'.format(value)
            self.__SetHelper('PresentationDefaultSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationDefaultSource')

    def SetPresentationSendingMode(self, value, qualifier):

        States = {
            'Local and Remote'  : 'LocalRemote',
            'Local Only'        : 'LocalOnly'
        }

        connectorID = int(qualifier['Connector ID'])
        if 1 <= connectorID <= 5:
            CmdString = 'xCommand Presentation Start SendingMode: {} connectorID: {}\r'.format(States[value], connectorID)
            self.__SetHelper('PresentationSendingMode', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationSendingMode')

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            CmdString = 'xStatus Conference Presentation LocalInstance {} SendingMode\r'.format(instanceID)
            self.__UpdateHelper('PresentationSendingModeStatus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        States = {
            'LocalRemote' : 'Local and Remote',
            'LocalOnly' : 'Local Only',
            'Off' : 'Off',
        }

        self.WriteStatus('PresentationSendingModeStatus', States[match.group(2).decode()], {'Instance': match.group(1).decode()})

    def __MatchPresentationSendingModeStatusStop(self, match, tag):
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance' : match.group(1).decode()})

    def SetPresentationPIPPosition(self, value, qualifier):

        States = {
            'Center Left'  : 'CenterLeft' ,
            'Center Right' : 'CenterRight',
            'Lower Left'   : 'LowerLeft'  ,
            'Lower Right'  : 'LowerRight' ,
            'Upper Center' : 'UpperCenter',
            'Upper Left'   : 'UpperLeft'  ,
            'Upper Right'  : 'UpperRight'
        }

        CmdString = 'xCommand Video PresentationPIP Set Position: {}\r'.format(States[value])
        self.__SetHelper('PresentationPIPPosition', CmdString, value, qualifier)

    def SetSelfView(self, value, qualifier):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        CmdString = 'xCommand Video Selfview Set Mode: {}\r'.format(States[value])
        self.__SetHelper('SelfView', CmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):
        self.__UpdateHelper('SelfView', 'xStatus Video Selfview Mode\r' , value, qualifier)

    def __MatchSelfView(self, match, tag):

        States = {
            'On'  : 'On',
            'Off' : 'Off'
        }

        self.WriteStatus('SelfView',  States[match.group(1).decode()] , None)

    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        States = {
            'On'      : 'On',
            'Off'     : 'Off',
            'Current' : 'Current'
        }

        CmdString = 'xConfiguration Video Selfview Default FullscreenMode: {}\r'.format(States[value])
        self.__SetHelper('SelfViewDefaultFullscreenMode', CmdString, value, qualifier)

    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', 'xStatus Video Selfview FullscreenMode\r' , value, qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        States = {
            'On'      : 'On',
            'Off'     : 'Off',
            'Current' : 'Current'
        }

        self.WriteStatus('SelfViewDefaultFullscreenMode',  States[match.group(1).decode()] , None)

    def SetSelfViewPosition(self, value, qualifier):

        States = {
            'Upper Left'   : 'UpperLeft'  ,
            'Upper Center' : 'UpperCenter',
            'Upper Right'  : 'UpperRight' ,
            'Center Left'  : 'CenterLeft' ,
            'Center Right' : 'CenterRight',
            'Lower Left'   : 'LowerLeft'  ,
            'Lower Right'  : 'LowerRight'
        }

        CmdString = 'xConfiguration Video Selfview Default PIPPosition: {}\r'.format(States[value])
        self.__SetHelper('SelfViewPosition', CmdString, value, qualifier)

    def UpdateSelfViewPosition(self, value, qualifier):
        self.__UpdateHelper('SelfViewPosition', 'xStatus Video Selfview PIPPosition\r' , value, qualifier)

    def __MatchSelfViewPosition(self, match, tag):

        States = {
            'UpperLeft'   : 'Upper Left',
            'UpperCenter' : 'Upper Center',
            'UpperRight'  : 'Upper Right',
            'CenterLeft'  : 'Center Left',
            'CenterRight' : 'Center Right',
            'LowerLeft'   : 'Lower Left',
            'LowerRight'  : 'Lower Right'
        }

        value = States[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('SelfViewPosition', value, None)

    def SetStandby(self, value, qualifier):

        States = {
            'On'  : 'Activate',
            'Off' : 'Deactivate',
            'Halfwake': 'Halfwake'
        }

        CmdString = 'xCommand Standby {}\r'.format(States[value])
        self.__SetHelper('Standby', CmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):
        self.__UpdateHelper('Standby', 'xStatus Standby State\r' , value, qualifier)

    def __MatchStandby(self, match, tag):

        States = {
            'Off'     : 'On',
            'Standby' : 'Off',
            'Halfwake': 'Halfwake',
            'EnteringStandby': 'Entering'
        }

        self.WriteStatus('Standby', States[match.group(1).decode()], None)

    def SetVideoSetMainVideoSource(self, value, qualifier):

        if 1 <= int(qualifier['Connector ID']) <= 5:
            CmdString = 'xCommand Video Input SetMainVideoSource ConnectorID: {}\r'.format(qualifier['Connector ID'])
            self.__SetHelper('VideoSetMainVideoSource', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoSetMainVideoSource')

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()