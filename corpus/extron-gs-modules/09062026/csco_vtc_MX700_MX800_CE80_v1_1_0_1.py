from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.Debug = False
        self.Models = {}

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
            'CallAnswerStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallID': {'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryAcknowledgeAllMissedCalls': {'Status': {}},
            'CallHistoryAcknowledgeMissedCall': {'Parameters': ['Missed Call Number'], 'Status': {}},
            'CallHistoryDeleteAllEntries': {'Status': {}},
            'CallHistoryDeleteEntry': {'Parameters': ['Entry Number'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Parameters': ['Button'], 'Status': {}},
            'CallOnHold': {'Parameters': ['Call'], 'Status': {}},
            'CallProtocol': {'Parameters': ['Call'], 'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraAssignedSerialNumberCommand': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraAutofocusCommand': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraAutofocusMode': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraFocus': {'Parameters': ['Camera ID'], 'Status': {}},
            'CameraPan': {'Parameters': ['Camera ID', 'Pan Speed'], 'Status': {}},
            'CameraPreset': {'Parameters': ['Preset Number'], 'Status': {}},
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
            'Hook': {'Parameters': ['Protocol', 'Dial String'], 'Status': {}},
            'IPv4AddressCommand': {'Status': {}},
            'IPv4AddressStatus': {'Status': {}},
            'IPv4GatewayCommand': {'Status': {}},
            'IPv4GatewayStatus': {'Status': {}},
            'IPv4SubnetMaskCommand': {'Status': {}},
            'IPv4SubnetMaskStatus': {'Status': {}},
            'MicrophoneLevel': {'Parameters': ['Microphone'], 'Status': {}},
            'MicrophoneMode': {'Parameters': ['Microphone'], 'Status': {}},
            'MuteAllMicrophones': {'Status': {}},
            'PhonebookFolderIDNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': {'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearch': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type', 'Contact', 'Folder ID'], 'Status': {}},
            'PresentationMode': {'Status': {}},
            'PresentationPIPPosition': {'Status': {}},
            'RemoteNumber': {'Parameters': ['Call'], 'Status': {}},
            'SelfView': {'Status': {}},
            'SelfViewDefaultFullscreenMode': {'Status': {}},
            'SelfViewPosition': {'Status': {}},
            'Standby': {'Status': {}},
            'VideoInput': {'Parameters': ['Connector ID'], 'Status': {}}
        }

        self.CallIDList = ['','','','','']
        self.folderList = {}
        self.newList = {}

        self.__UpdateTimer = 0
        self._NumberofPhonebookSearch = 5
        self.MinLabel = 1
        self.MaxLabel = 5
        self.dirName = re.compile('\*r PhonebookSearchResult Contact (\d+) Name: \x22(.+)\x22\r\n')
        self.dirNumber = re.compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: \x22(.+)\x22')
        self.Offset = 0

        self._NumberofPhonebookFolderSearch = 5
        self.FolderMin = 1
        self.FolderLimit = 0
        self.MaxFolders = 1
        self.FolderNameRex = re.compile('\*r PhonebookSearchResult Folder (\d+) Name: \x22(.+)\x22\r\n')
        self.FolderIDRex = re.compile('\*r PhonebookSearchResult Folder (\d+) FolderId: \x22(.+)\x22')
        self.phonebookFolderID = ''

        self._NumberofCallHistory = 5
        self.prevCallHist = ''
        self.startCallHist = 1
        self.endCallHist = 0
        self.displayName = re.compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')
        self.callBackNumber = re.compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')

        self._CallHistoryOccurrenceType = 'Time'
        self.lastOccurrenceTime = re.compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
        self.occurrenceCount = re.compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')

        self.occurrenceType = re.compile('Entry (\d+) OccurrenceType: (\w*)\r\n')
        self.lastCallHist = 0
        self.advanceCallHist = True

        self.number = ''

        self.deviceUsername = 'admin'
        self.devicePassword = ''

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\*s Video PIP ActiveSpeaker Position: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchActiveSpeakerPIPPosition, None)
            self.AddMatchString(re.compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchAudioVolume, None)
            self.AddMatchString(re.compile(b'\*s Audio VolumeMute: (On|Off)\r\n'), self.__MatchAudioVolumeMute, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) AnswerState: (Unanswered|Ignored|Autoanswered|Answered)\r\n'), self.__MatchCallAnswerStatus, None)
            self.AddMatchString(re.compile(b'\*r CallHistoryRecentsResult [\s\S]+\*\* end\r\n'), self.__MatchCallHistory, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) PlacedOnHold: (True|False)\r\n'), self.__MatchCallOnHold, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) Protocol: "(h320|h323|sip)"\r\n'), self.__MatchCallProtocol, None)
            self.AddMatchString(re.compile(b'\*s Call: (\d+)\r\n'), self.__MatchCallID, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) Status: (Idle|Dialling|Ringing|Conencting|Connected|Disconnecting|OnHold|EarlyMedia|Preserved|RemotePreserved)\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n'), self.__MatchCallStatusType, None)
            self.AddMatchString(re.compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchConferenceDoNotDisturb, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) DisplayName: "(.*)"\r\n'), self.__MatchDisplayName, None)
            self.AddMatchString(re.compile(b'\*s Network 1 DNS Server ([1-3]) Address: "([0-9.]{7,15})"\r\n'), self.__MatchDNSServerAddressStatus, None)
            self.AddMatchString(re.compile(b'\*s H323 Gatekeeper Address: "([0-9.]{7,15})"\r\n'), self.__MatchH323GatekeeperAddressStatus, None)
            self.AddMatchString(re.compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(re.compile(b'\*s Network 1 IPv4 Address: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4AddressStatus, None)
            self.AddMatchString(re.compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4GatewayStatus, None)
            self.AddMatchString(re.compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{7,15})"\r\n'), self.__MatchIPv4SubnetMaskStatus, None)
            self.AddMatchString(re.compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMuteAllMicrophones, None)
            self.AddMatchString(re.compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationMode, None)
            self.AddMatchString(re.compile(b'\*s Call (\d+) RemoteNumber: "(.*)"\r\n'), self.__MatchRemoteNumber, None)
            self.AddMatchString(re.compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(re.compile(b'\*s Video Selfview FullScreenMode: (On|Off|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(re.compile(b'\*s Video Selfview PIPPosition: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(re.compile(b'\*s Standby State: (On|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(re.compile(b'\*s Video Input Connector ([1-5]) SourceId: ([1-4])\r\n'), self.__MatchVideoInput, None)

            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Login incorrect\r\n'), self.__MatchError, None)

    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):
        self._CallHistoryOccurrenceType = value
        if self._CallHistoryOccurrenceType == 'Time':
            self.lastOccurrenceTime = re.compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
            self.occurrenceCount = re.compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        elif self._CallHistoryOccurrenceType == 'Frequency':
            self.lastOccurrenceTime = re.compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = re.compile('Entry (\d+) Count: (\d+)\r\n')

    @property
    def NumberofCallHistory(self):
        return self._NumberofCallHistory

    @NumberofCallHistory.setter
    def NumberofCallHistory(self, value):
        if 1 <= int(value) <= 20:
            self._NumberofCallHistory = int(value)
        else:
            print('Number of Call History is out of range.')

    @property
    def NumberofPhonebookFolderSearch(self):
        return self._NumberofPhonebookFolderSearch

    @NumberofPhonebookFolderSearch.setter
    def NumberofPhonebookFolderSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofPhonebookFolderSearch = int(value)
        else:
            print('Number of Phonebook Folder Search is out of range.')

    @property
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberofPhonebookSearch = int(value)
        else:
            print('Number of Phonebook Search is out of range.')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self._deviceUsername + '\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self._devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetActiveSpeakerPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight',
            'Upper Center': 'UpperCenter',
            'Upper Left': 'UpperLeft',
            'Upper Right': 'UpperRight'
        }

        ActiveSpeakerPIPPositionCmdString = 'xCommand Video ActiveSpeakerPIP Set Position: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ActiveSpeakerPIPPosition', ActiveSpeakerPIPPositionCmdString, value, qualifier)

    def UpdateActiveSpeakerPIPPosition(self, value, qualifier):

        ActiveSpeakerPIPPositionCmdString = 'xStatus Video ActiveSpeaker PIPPosition\r'
        self.__UpdateHelper('ActiveSpeakerPIPPosition', ActiveSpeakerPIPPositionCmdString, value, qualifier)

    def __MatchActiveSpeakerPIPPosition(self, match, tag):

        ValueStateValues = {
            'CenterLeft': 'Center Left',
            'CenterRight': 'Center Right',
            'LowerLeft': 'Lower Left',
            'LowerRight': 'Lower Right',
            'UpperCenter': 'Upper Center',
            'UpperLeft': 'Upper Left',
            'UpperRight': 'Upper Right'
        }

        value = ValueStateValues[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('ActiveSpeakerPIPPosition', value, None)

    def SetAudioInputLineChannel(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            'Left': 'Left',
            'Mono': 'Mono',
            'Right': 'Right'
        }

        AudioInputLineChannelCmdString = 'xConfiguration Audio Input Line {0} Channel: {1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('AudioInputLineChannel', AudioInputLineChannelCmdString, value, qualifier)

    def SetAudioInputLineLevel(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 24
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioInputLineLevelCmdString = 'xConfiguration Audio Input Line {0} Level: {1}\r'.format(InputStates[qualifier['Input']], value)
            self.__SetHelper('AudioInputLineLevel', AudioInputLineLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioInputLineLevel')

    def SetAudioInputLineMode(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        AudioInputLineModeCmdString = 'xConfiguration Audio Input Line {0} Mode: {1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('AudioInputLineMode', AudioInputLineModeCmdString, value, qualifier)

    def SetAudioInputLineSource(self, value, qualifier):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        AudioInputLineSourceCmdString = 'xConfiguration Audio Input Line {0} VideoAssociation VideoInputSource: {1}\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('AudioInputLineSource', AudioInputLineSourceCmdString, value, qualifier)

    def SetAudioOutputLineChannel(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueStateValues = {
            'Left': 'Left',
            'Mono': 'Mono',
            'Right': 'Right'
        }

        AudioOutputLineChannelCmdString = 'xConfiguration Audio Output Line {0} Channel: {1}\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('AudioOutputLineChannel', AudioOutputLineChannelCmdString, value, qualifier)

    def SetAudioOutputLineLevel(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueConstraints = {
            'Min': -24,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioOutputLineLevelCmdString = 'xConfiguration Audio Output Line {0} Level: {1}\r'.format(OutputStates[qualifier['Output']], value)
            self.__SetHelper('AudioOutputLineLevel', AudioOutputLineLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioOutputLineLevel')

    def SetAudioOutputLineMode(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        AudioOutputLineModeCmdString = 'xConfiguration Audio Output Line {0} Mode: {1}\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('AudioOutputLineMode', AudioOutputLineModeCmdString, value, qualifier)

    def SetAudioVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioVolumeCmdString = 'xCommand Audio Volume Set Level: {0}\r'.format(value)
            self.__SetHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioVolume')

    def UpdateAudioVolume(self, value, qualifier):

        AudioVolumeCmdString = 'xStatus Audio Volume\r'
        self.__UpdateHelper('AudioVolume', AudioVolumeCmdString, value, qualifier)

    def __MatchAudioVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('AudioVolume', value, None)

    def SetAudioVolumeMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        AudioVolumeMuteCmdString = 'xCommand Audio Volume {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AudioVolumeMute', AudioVolumeMuteCmdString, value, qualifier)

    def UpdateAudioVolumeMute(self, value, qualifier):

        AudioVolumeMuteCmdString = 'xStatus Audio VolumeMute\r'
        self.__UpdateHelper('AudioVolumeMute', AudioVolumeMuteCmdString, value, qualifier)

    def __MatchAudioVolumeMute(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioVolumeMute', value, None)

    def UpdateCallAnswerStatus(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }
        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            CallAnswerStatusCmdString = 'xStatus Call {0} AnswerState\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('CallAnswerStatus', CallAnswerStatusCmdString, value, qualifier)

    def __MatchCallAnswerStatus(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }
        ValueStateValues = {
            'Unanswered': 'Unanswered',
            'Ignored': 'Ignored',
            'Autoanswered': 'Auto Answered',
            'Answered': 'Answered'
        }
        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallAnswerStatus', value, qualifier)

    def UpdateCallID(self, value, qualifier):

        CallIDCmdString = 'xStatus Call\r'
        self.__UpdateHelper('CallID', CallIDCmdString, value, qualifier)

    def __MatchCallID(self, match, tag):

        index = 0
        value = match.group(1).decode()
        if 1 <= int(value) <= 65535:
            while index <= 4:
                if value not in self.CallIDList:
                    if self.CallIDList[index] == '':
                        self.CallIDList[index] = value
                index += 1
        else:
            print('Invalid Command')

    def SetCallHistoryRefresh(self, value, qualifier):
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        self.Send(CallHistoryCmdString)

    def __MatchCallHistory(self, match, tag):

        res = match.group(0).decode()
        if self.prevCallHist != res:
            self.prevCallHist = res
            self.advanceCallHist = True
            displayNameList = dict(re.findall(self.displayName, res))
            callBackNumberList = dict(re.findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(re.findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(re.findall(self.occurrenceType, res))
            occurrenceCountList = dict(re.findall(self.occurrenceCount, res))

            for btn in range(1, self._NumberofCallHistory + 1):
                button = str(btn)
                index = str(btn - 1)

                if index in displayNameList:
                    self.WriteStatus('CallHistory', displayNameList[index], {'Button': button, 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', callBackNumberList[index], {'Button': button, 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', lastOccurrenceTimeList[index], {'Button': button, 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', occurrenceTypeList[index], {'Button': button, 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', occurrenceCountList[index], {'Button': button, 'Detail Type': 'Occurrence Count'})
                else:
                    self.WriteStatus('CallHistory', ' ', {'Button': button, 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', ' ', {'Button': button, 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', ' ', {'Button': button, 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', ' ', {'Button': button, 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', ' ', {'Button': button, 'Detail Type': 'Occurrence Count'})
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
            print('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistorySelect(self, value, qualifier):

        if 1 <= int(value) <= 20:
            self.number = self.ReadStatus('CallHistory', {'Button': value, 'Detail Type': 'Callback Number'})
        else:
            print('Invalid Command for SetCallHistorySelect')

    def SetCallHistoryAcknowledgeAllMissedCalls(self, value, qualifier):

        CallHistoryAcknowledgeAllMissedCallsCmdString = 'xCommand CallHistory AcknowledgeAllMissedCalls\r'
        self.__SetHelper('CallHistoryAcknowledgeAllMissedCalls', CallHistoryAcknowledgeAllMissedCallsCmdString, value, qualifier)

    def SetCallHistoryAcknowledgeMissedCall(self, value, qualifier):

        if 1 <= int(qualifier['Missed Call Number']) <= 2147483647:
            CallHistoryAcknowledgeMissedCallCmdString = 'xCommand CallHistory AcknowledgeMissedCall CallHistoryID: {0}\r'.format(qualifier['Missed Call Number'])
            self.__SetHelper('CallHistoryAcknowledgeMissedCall', CallHistoryAcknowledgeMissedCallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCallHistoryAcknowledgeMissedCall')

    def SetCallHistoryDeleteAllEntries(self, value, qualifier):

        ValueStateValues = {
            'All': 'All',
            'Missed': 'Missed',
            'Placed': 'Placed',
            'Received': 'Received'
        }

        CallHistoryDeleteAllEntriesCmdString = 'xCommand CallHistory DeleteAll Filter: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CallHistoryDeleteAllEntries', CallHistoryDeleteAllEntriesCmdString, value, qualifier)

    def SetCallHistoryDeleteEntry(self, value, qualifier):

        EntryNumberConstraints = {
            'Min': 1,
            'Max': 2147483647
        }
        if EntryNumberConstraints['Min'] <= int(qualifier['Entry Number']) <= EntryNumberConstraints['Max']:
            CallHistoryDeleteEntryCmdString = 'xCommand CallHistory DeleteEntry CallHistoryID: {0}\r'.format(qualifier['Entry Number'])
            self.__SetHelper('CallHistoryDeleteEntry', CallHistoryDeleteEntryCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCallHistoryDeleteEntry')

    def UpdateCallOnHold(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }
        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            CallOnHoldCmdString = 'xStatus Call {0} PlacedOnHold\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('CallOnHold', CallOnHoldCmdString, value, qualifier)

    def __MatchCallOnHold(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }
        ValueStateValues = {
            'True': 'Held',
            'False': 'Not Held'
        }
        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallOnHold', value, qualifier)

    def UpdateCallProtocol(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }

        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            CallProtocolCmdString = 'xStatus Call {0} Protocol\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('CallProtocol', CallProtocolCmdString, value, qualifier)

    def __MatchCallProtocol(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }
        ValueStateValues = {
            'h320': 'H320',
            'h323': 'H323',
            'sip': 'Sip'
        }
        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallProtocol', value, qualifier)

    def UpdateCallStatus(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }
        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            CallStatusCmdString = 'xStatus Call {0} Status\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }

        ValueStateValues = {
            'Idle': 'Idle',
            'Dialling': 'Dialing',
            'Ringing': 'Ringing',
            'Connecting': 'Connecting',
            'Connected': 'Connected',
            'Disconnecting': 'Disconnecting',
            'OnHold': 'On Hold',
            'EarlyMedia': 'Early Media',
            'Preserved': 'Preserved',
            'RemotePreserved': 'Remote Preserved'
        }
        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallStatus', value, qualifier)
        if value == 'Disconnecting':
            self.CallIDList[int(qualifier['Call']) - 1] = ''

    def UpdateCallStatusType(self, value, qualifier):

        CallStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4]
        }
        if CallStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            CallStatusTypeCmdString = 'xStatus Call {0} CallType\r'.format(CallStates[qualifier['Call']])
            self.__UpdateHelper('CallStatusType', CallStatusTypeCmdString, value, qualifier)

    def __MatchCallStatusType(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }

        ValueStateValues = {
            'Video': 'Video',
            'Audio': 'Audio',
            'AudioCanEscalate': 'Audio Can Escalate',
            'ForwardAllCall': 'Forward All Calls',
            'Unknown': 'Unknown'
        }

        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallStatusType', value, qualifier)

    def SetCameraAssignedSerialNumberCommand(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }
        SerialNumber = value
        if 0 <= len(SerialNumber) <= 20:
            CameraAssignedSerialNumberCommandCmdString = 'xConfiguration Cameras Camera {0} AssignedSerialNumber: "{1}"\r'.format(CameraIDStates[qualifier['Camera ID']], SerialNumber)
            self.__SetHelper('CameraAssignedSerialNumberCommand', CameraAssignedSerialNumberCommandCmdString, value, qualifier)
        else:
            print('Invalid command for SetCameraAssignedSerialNumberCommand')

    def SetCameraAutofocusCommand(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        CameraAutofocusCommandCmdString = 'xCommand Camera TriggerAutofocus CameraId: {0}\r'.format(CameraIDStates[qualifier['Camera ID']])
        self.__SetHelper('CameraAutofocusCommand', CameraAutofocusCommandCmdString, value, qualifier)

    def SetCameraAutofocusMode(self, value, qualifier):

        CameraIDStates = {
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        ValueStateValues = {
            'Auto': 'Auto',
            'Manual': 'Manual'
        }

        CameraAutofocusModeCmdString = 'xConfiguration Cameras Camera {0} Focus Mode: {1}\r'.format(CameraIDStates[qualifier['Camera ID']], ValueStateValues[value])
        self.__SetHelper('CameraAutofocusMode', CameraAutofocusModeCmdString, value, qualifier)

    def SetCameraFocus(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        ValueStateValues = {
            'Far': 'Far',
            'Near': 'Near',
            'Stop': 'Stop'
        }

        CameraFocusCmdString = 'xCommand Camera Ramp CameraId: {0} Focus: {1}\r'.format(CameraIDStates[qualifier['Camera ID']], ValueStateValues[value])
        self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)

    def SetCameraPan(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        PanSpeedStates = {
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
            '15': '15'
        }

        ValueStateValues = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop'
        }

        CameraPanCmdString = 'xCommand Camera Ramp CameraId: {0} PanSpeed: {1} Pan: {2}\r'.format(CameraIDStates[qualifier['Camera ID']], PanSpeedStates[qualifier['Pan Speed']], ValueStateValues[value])
        self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)

    def SetCameraPreset(self, value, qualifier):

        PresetNumberStates = {
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
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25',
            '26': '26',
            '27': '27',
            '28': '28',
            '29': '29',
            '30': '30',
            '31': '31',
            '32': '32',
            '33': '33',
            '34': '34',
            '35': '35'
        }

        ValueStateValues = {
            'Activate': 'Activate',
            'Remove': 'Remove'
        }

        CameraPresetCmdString = 'xCommand Camera Preset {0} PresetID: {1}\r'.format(PresetNumberStates[qualifier['Preset Number']], ValueStateValues[value])
        self.__SetHelper('CameraPreset', CameraPresetCmdString, value, qualifier)

    def SetCameraPresetStore(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        DefaultPositionStates = {
            'False': 'False',
            'True': 'True'
        }

        ValueStateValues = {
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
            '20': '20',
            '21': '21',
            '22': '22',
            '23': '23',
            '24': '24',
            '25': '25',
            '26': '26',
            '27': '27',
            '28': '28',
            '29': '29',
            '30': '30',
            '31': '31',
            '32': '32',
            '33': '33',
            '34': '34',
            '35': '35'
        }

        CameraPresetStoreCmdString = 'xCommand Camera Preset Store PresetId: {0} CameraId: {1} DefaultPosition: {2}\r'.format(ValueStateValues[value], CameraIDStates[qualifier['Camera ID']], DefaultPositionStates[qualifier['Default Position']])
        self.__SetHelper('CameraPresetStore', CameraPresetStoreCmdString, value, qualifier)

    def SetCameraSpeakerTrack(self, value, qualifier):

        ValueStateValues = {
            'Activate': 'Activate',
            'Deactivate': 'Deactivate'
        }

        CameraSpeakerTrackCmdString = 'xCommand Cameras SpeakerTrack {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraSpeakerTrack', CameraSpeakerTrackCmdString, value, qualifier)

    def SetCameraSpeakerTrackTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'Auto',
            'Conservative': 'Conservative'
        }

        CameraSpeakerTrackTrackingModeCmdString = 'xCommand Cameras SpeakerTrack TrackingMode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraSpeakerTrackTrackingMode', CameraSpeakerTrackTrackingModeCmdString, value, qualifier)

    def SetCameraTilt(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        TiltSpeedStates = {
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
            '15': '15'
        }

        ValueStateValues = {
            'Down': 'Down',
            'Up': 'Up',
            'Stop': 'Stop'
        }

        CameraTiltCmdString = 'xCommand Camera Ramp CameraId: {0} Tilt: {1} TiltSpeed: {2}\r'.format(CameraIDStates[qualifier['Camera ID']], ValueStateValues[value], TiltSpeedStates[qualifier['Tilt Speed']])
        self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)

    def SetCameraZoom(self, value, qualifier):

        CameraIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7'
        }

        ZoomSpeedStates = {
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
            '15': '15'
        }

        ValueStateValues = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop'
        }

        CameraZoomCmdString = 'xCommand Camera Ramp CameraId: {0} Zoom: {1} ZoomSpeed: {2}\r'.format(CameraIDStates[qualifier['Camera ID']], ValueStateValues[value], ZoomSpeedStates[qualifier['Zoom Speed']])
        self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)

    def SetConferenceAutoAnswerDelay(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 50
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ConferenceAutoAnswerDelayCmdString = 'xConfiguration Conference AutoAnswer Delay: {0}\r'.format(value)
            self.__SetHelper('ConferenceAutoAnswerDelay', ConferenceAutoAnswerDelayCmdString, value, qualifier)
        else:
            print('Invalid Command for SetConferenceAutoAnswerDelay')

    def SetConferenceAutoAnswerMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        ConferenceAutoAnswerModeCmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceAutoAnswerMode', ConferenceAutoAnswerModeCmdString, value, qualifier)

    def SetConferenceAutoAnswerMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        ConferenceAutoAnswerMuteCmdString = 'xConfiguration Conference AutoAnswer Mute: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceAutoAnswerMute', ConferenceAutoAnswerMuteCmdString, value, qualifier)

    def SetConferenceDefaultCallProtocol(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'Auto',
            'H323': 'H323',
            'Sip': 'Sip',
            'H320': 'H320'
        }

        ConferenceDefaultCallProtocolCmdString = 'xConfiguration Conference DefaultCall Protocol: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceDefaultCallProtocol', ConferenceDefaultCallProtocolCmdString, value, qualifier)

    def SetConferenceDefaultCallRate(self, value, qualifier):

        ValueConstraints = {
            'Min': 64,
            'Max': 6000
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            ConferenceDefaultCallRateCmdString = 'xConfiguration Conference DefaultCall Rate: {0}\r'.format(value)
            self.__SetHelper('ConferenceDefaultCallRate', ConferenceDefaultCallRateCmdString, value, qualifier)
        else:
            print('Invalid Command for SetConferenceDefaultCallRate')

    def SetConferenceDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        ConferenceDoNotDisturbCmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceDoNotDisturb', ConferenceDoNotDisturbCmdString, value, qualifier)

    def UpdateConferenceDoNotDisturb(self, value, qualifier):

        ConferenceDoNotDisturbCmdString = 'xStatus Conference DoNotDisturb\r'
        self.__UpdateHelper('ConferenceDoNotDisturb', ConferenceDoNotDisturbCmdString, value, qualifier)

    def __MatchConferenceDoNotDisturb(self, match, tag):

        ValueStateValues = {
            'Active': 'On',
            'Inactive': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ConferenceDoNotDisturb', value, None)

    def SetConferenceEncryptionMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off',
            'Best Effort': 'BestEffort'
        }

        ConferenceEncryptionModeCmdString = 'xConfiguration Conference Encryption Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceEncryptionMode', ConferenceEncryptionModeCmdString, value, qualifier)

    def SetConferenceFarEndControlMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        ConferenceFarEndControlModeCmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('ConferenceFarEndControlMode', ConferenceFarEndControlModeCmdString, value, qualifier)

    def SetConferenceSpeakerLock(self, value, qualifier):

        SpeakerStates = {
            'Local': 'local',
            'Remote': 'remote'
        }

        ValueStateValues = {
            'On': 'Set',
            'Off': 'Release'
        }

        if ValueStateValues[value] == 'Set':
            ConferenceSpeakerLockCmdString = 'xCommand Conference SpeakerLock Set Target: {0}\r'.format(SpeakerStates[qualifier['Speaker']])
            self.__SetHelper('ConferenceSpeakerLock', ConferenceSpeakerLockCmdString, value, qualifier)
        elif ValueStateValues[value] == 'Release':
            ConferenceSpeakerLockCmdString = 'xCommand Conference SpeakerLock Release\r'
            self.__SetHelper('ConferenceSpeakerLock', ConferenceSpeakerLockCmdString, value, qualifier)
        else:
            print('Invalid Command for SetConferenceSpeakerLock')

    def UpdateDisplayName(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }
        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            DisplayNameCmdString = 'xStatus Call {0} DisplayName\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('DisplayName', DisplayNameCmdString, value, qualifier)

    def __MatchDisplayName(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }

        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('DisplayName', value, qualifier)

    def SetDNSDomainNameCommand(self, value, qualifier):

        if 0 <= len(value) <= 64:
            DNSDomainNameCommandCmdString = 'xConfiguration Network 1 DNS Domain Name: \"{0}\"\r'.format(value)
            self.__SetHelper('DNSDomainNameCommand', DNSDomainNameCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDNSDomainNameCommand')

    def SetDNSServerAddressCommand(self, value, qualifier):

        ServerStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }
        if 0 <= len(value) <= 64:
            DNSServerAddressCommandCmdString = 'xConfiguration Network 1 DNS Server {0} Address: "{1}"\r'.format(ServerStates[qualifier['Server']], value)
            self.__SetHelper('DNSServerAddressCommand', DNSServerAddressCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDNSServerAddressCommand')

    def UpdateDNSServerAddressStatus(self, value, qualifier):

        ServerStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }
        DNSServerAddressStatusCmdString = 'xStatus Network 1 DNS Server {0} Address\r'.format(ServerStates[qualifier['Server']])
        self.__UpdateHelper('DNSServerAddressStatus', DNSServerAddressStatusCmdString, value, qualifier)

    def __MatchDNSServerAddressStatus(self, match, tag):

        ServerStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        qualifier = {'Server': ServerStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('DNSServerAddressStatus', value, qualifier)

    def SetDTMF(self, value, qualifier):

        ValueStateValues = {
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

        DTMFCmdString = 'xCommand Call DTMFSend DTMFString: \"{0}\"\r'.format(ValueStateValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        ValueStateValues = {
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
            '15': '15'
        }

        FarEndCameraPresetRecallCmdString = 'xCommand FarEndControl RoomPreset Activate PresetId: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('FarEndCameraPresetRecall', FarEndCameraPresetRecallCmdString, value, qualifier)

    def SetFarEndCameraPTZ(self, value, qualifier):

        ValueStateValues = {
            'Left': 'Left',
            'Right': 'Right',
            'Up': 'Up',
            'Down': 'Down',
            'Zoom In': 'ZoomIn',
            'Zoom Out': 'ZoomOut',
            'Stop': 'Stop'
        }

        if ValueStateValues[value] == 'Stop':
            FarEndCameraPTZCmdString = 'xCommand FarEndControl Camera Stop\r'
            self.__SetHelper('FarEndCameraPTZ', FarEndCameraPTZCmdString, value, qualifier)
        else:
            FarEndCameraPTZCmdString = 'xCommand FarEndControl Camera Move Value: {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('FarEndCameraPTZ', FarEndCameraPTZCmdString, value, qualifier)

    def SetFarEndCameraSourceSelect(self, value, qualifier):

        ValueStateValues = {
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
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15'
        }

        FarEndCameraSourceSelectCmdString = 'xCommand FarEndControl Source Select SourceId: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('FarEndCameraSourceSelect', FarEndCameraSourceSelectCmdString, value, qualifier)

    def SetH323AliasE164Command(self, value, qualifier):

        if 0 <= len(value) <= 30:
            H323AliasE164CommandCmdString = 'xConfiguration H323 H323Alias E164: \"{0}\"\r'.format(value)
            self.__SetHelper('H323AliasE164Command', H323AliasE164CommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetH323AliasE164Command')

    def SetH323AliasIDCommand(self, value, qualifier):

        if 0 <= len(value) <= 49:
            H323AliasIDCommandCmdString = 'xConfiguration H323 H323Alias ID: \"{0}\"\r'.format(value)
            self.__SetHelper('H323AliasIDCommand', H323AliasIDCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetH323AliasIDCommand')

    def SetH323AuthenticationMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        H323AuthenticationModeCmdString = 'xConfiguration H323 Authentication Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('H323AuthenticationMode', H323AuthenticationModeCmdString, value, qualifier)

    def SetH323CallSetupMode(self, value, qualifier):

        ValueStateValues = {
            'Direct': 'Direct',
            'Gatekeeper': 'Gatekeeper'
        }

        H323CallSetupModeCmdString = 'xConfiguration H323 CallSetup Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('H323CallSetupMode', H323CallSetupModeCmdString, value, qualifier)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        if 0 <= len(value) <= 255:
            H323GatekeeperAddressCommandCmdString = 'xConfiguration H323 Gatekeeper Address: \"{0}\"\r'.format(value)
            self.__SetHelper('H323GatekeeperAddressCommand', H323GatekeeperAddressCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetH323GatekeeperAddressCommand')

    def UpdateH323GatekeeperAddressStatus(self, value, qualifier):

        H323GatekeeperAddressStatusCmdString = 'xStatus H323 Gatekeeper Address\r'
        self.__UpdateHelper('H323GatekeeperAddressStatus', H323GatekeeperAddressStatusCmdString, value, qualifier)

    def __MatchH323GatekeeperAddressStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323GatekeeperAddressStatus', value, None)

    def UpdateH323GatekeeperStatus(self, value, qualifier):

        H323GatekeeperStatusCmdString = 'xStatus H323 Gatekeeper Status\r'
        self.__UpdateHelper('H323GatekeeperStatus', H323GatekeeperStatusCmdString, value, qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        ValueStateValues = {
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

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('H323GatekeeperStatus', value, None)

    def SetH323LoginNameCommand(self, value, qualifier):

        if 0 <= len(value) <= 50:
            H323LoginNameCommandCmdString = 'xConfiguration H323 Authentication LoginName: \"{0}\"\r'.format(value)
            self.__SetHelper('H323LoginNameCommand', H323LoginNameCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetH323LoginNameCommand')

    def SetH323PasswordCommand(self, value, qualifier):

        if 0 <= len(value) <= 50:
            H323PasswordCommandCmdString = 'xConfiguration H323 Authentication Password: \"{0}\"\r'.format(value)
            self.__SetHelper('H323PasswordCommand', H323PasswordCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetH323PasswordCommand')

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320': 'h320',
            'H323': 'h323',
            'SIP': 'sip',
            'Auto': 'Auto',
        }

        protocol = qualifier['Protocol']

        if value in ['Accept', 'Reject']:
            self.__SetHelper('Hook', 'xCommand Call {0}\r'.format(value), value, qualifier)
        elif 'Resume' in value or 'Disconnect' in value or 'Hold' in value or 'Join' in value:
            val = value.split(' ')
            cmd = val[0]
            index = int(val[1]) - 1
            try:
                self.__SetHelper('Hook', 'xCommand Call {0} CallId: {1}\r'.format(cmd, self.CallIDList[index]), value, qualifier)
                if cmd == 'Disconnect':
                    self.CallIDList[index] == ''
            except IndexError:
                print('Invalid Command for SetHook')
        elif value is 'Dial':
            number = qualifier['Number']
            if number:
                if protocol == 'Auto':
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\" Protocol:{1}\r'.format(number, Protocol_Values[protocol]), value, qualifier)
        else:
            print('Invalid Command for SetHook')

    def SetIPv4AddressCommand(self, value, qualifier):

        if 0 <= len(value) <= 64:
            IPv4AddressCommandCmdString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(value)
            self.__SetHelper('IPv4AddressCommand', IPv4AddressCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIPv4AddressCommand')

    def UpdateIPv4AddressStatus(self, value, qualifier):

        IPv4AddressStatusCmdString = 'xStatus Network 1 IPv4 Address\r'
        self.__UpdateHelper('IPv4AddressStatus', IPv4AddressStatusCmdString, value, qualifier)

    def __MatchIPv4AddressStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPv4AddressStatus', value, None)

    def SetIPv4GatewayCommand(self, value, qualifier):

        if 0 <= len(value) <= 64:
            IPv4GatewayCommandCmdString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(value)
            self.__SetHelper('IPv4GatewayCommand', IPv4GatewayCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIPv4GatewayCommand')

    def UpdateIPv4GatewayStatus(self, value, qualifier):

        IPv4GatewayStatusCmdString = 'xStatus Network 1 IPv4 Gateway\r'
        self.__UpdateHelper('IPv4GatewayStatus', IPv4GatewayStatusCmdString, value, qualifier)

    def __MatchIPv4GatewayStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPv4GatewayStatus', value, None)

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        if 0 <= len(value) <= 64:
            IPv4SubnetMaskCommandCmdString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(value)
            self.__SetHelper('IPv4SubnetMaskCommand', IPv4SubnetMaskCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetIPv4SubnetMaskCommand')

    def UpdateIPv4SubnetMaskStatus(self, value, qualifier):

        IPv4SubnetMaskStatusCmdString = 'xStatus Network 1 IPv4 SubnetMask\r'
        self.__UpdateHelper('IPv4SubnetMaskStatus', IPv4SubnetMaskStatusCmdString, value, qualifier)

    def __MatchIPv4SubnetMaskStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPv4SubnetMaskStatus', value, None)

    def SetMicrophoneLevel(self, value, qualifier):

        MicrophoneStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 70
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicrophoneLevelCmdString = 'xConfiguration Audio Input Microphone {0} Level: {1}\r'.format(MicrophoneStates[qualifier['Microphone']], value)
            self.__SetHelper('MicrophoneLevel', MicrophoneLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicrophoneLevel')

    def SetMicrophoneMode(self, value, qualifier):

        MicrophoneStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        MicrophoneModeCmdString = 'xConfiguration Audio Input Microphone {0} Mode: {1}\r'.format(MicrophoneStates[qualifier['Microphone']], ValueStateValues[value])
        self.__SetHelper('MicrophoneMode', MicrophoneModeCmdString, value, qualifier)

    def SetMuteAllMicrophones(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        MuteAllMicrophonesCmdString = 'xCommand Microphones {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MuteAllMicrophones', MuteAllMicrophonesCmdString, value, qualifier)

    def UpdateMuteAllMicrophones(self, value, qualifier):

        MuteAllMicrophonesCmdString = 'xStatus Audio Microphones Mute\r'
        self.__UpdateHelper('MuteAllMicrophones', MuteAllMicrophonesCmdString, value, qualifier)

    def __MatchMuteAllMicrophones(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MuteAllMicrophones', value, None)

    def SetPhonebookSearch(self, value, qualifier):

        self.MinLabel = 1
        self.MaxLabel = self._NumberofPhonebookSearch
        self.Offset = 0
        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookSearchSet(self, value, qualifier):

        if 1 <= value <= self._NumberofPhonebookSearch:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': int(value)})
            if number and number != '***End of list***':
                number = number[number.find(' : ') + 3:]
                commandstring = 'xCommand Dial Number:"{0}"\r'.format(number)
                self.Send(commandstring)
        else:
            print('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookFolderIDNavigation(self, value, qualifier):

        if self.FolderLimit != 0:
            buttonParam = 'Button'
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
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {buttonParam: button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {buttonParam: button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {buttonParam: i})
            else:
                print('Invalid Command for SetPhonebookFolderIDNavigation')

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
                        self.SetPhonebookUpdate('Previous Search', qualifier)
                        self.MinLabel = len(self.newList) - 4
                        self.MaxLabel = len(self.newList)
                    else:
                        self.MinLabel = 1

                if self.MaxLabel < self._NumberofPhonebookSearch:
                    self.MaxLabel = self._NumberofPhonebookSearch

                if self.MaxLabel > len(self.newList) and len(self.newList) == 250:
                    self.SetPhonebookUpdate('Next Search', qualifier)

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            print('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):
        if self.folderList:
            folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
            if folderName:
                self.FolderIDNumber = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName][0]
        else:
            print('Invalid Command for SetPhonebookFolderIDSearchSet')

    def SetPhonebookFolderIDUpdate(self, value, qualifier):

        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: 250\r'.format(phonebookValue)
            res = self.SendAndWait(cmdStr, 10, deliTag='**').decode()
            if res:
                self.folderList = {}
                folderName = re.findall(self.FolderNameRex, res)
                folderID = re.findall(self.FolderIDRex, res)
                buttonParamFolderID = 'Button'

                for i, name in folderName:
                    self.folderList[i] = {'Name': name}

                for i, id in folderID:
                    if i in self.folderList:
                        self.folderList[i]['ID'] = id
                    else:
                        self.folderList[i] = {'ID': id}

                button = 1
                for i in range(1, self._NumberofPhonebookFolderSearch + 1):
                    if str(i) in self.folderList:
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {buttonParamFolderID: int(i)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {buttonParamFolderID: button})
                    button += 1
                    for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {buttonParamFolderID: i})
        else:
            print('Invalid Command for SetPhonebookFolderIDUpdate')

    def SetPhonebookUpdate(self, value, qualifier):

        buttonParam = self.Commands['PhonebookSearchResult']['Parameters'][0]

        if value == 'Refresh':
            self.Offset = 0
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
        elif value == 'Next Search' and len(self.newList) == 250:
            self.MinLabel = 1
            self.MaxLabel = 5
            self.Offset += 250
        elif value == 'Previous Search':  # load previous set of contacts
            self.Offset -= 250

        if self.Offset < 0:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset = 0

        self.WriteStatus('PhonebookSearchResult', '***Loading Contacts***', {buttonParam: 1})
        for i in range(2, int(self._NumberofPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '...', {buttonParam: i})

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
        phonebookType = qualifier['Phonebook Type']
        contact = qualifier['Contact']
        folderID = qualifier['Folder ID']
        if phonebookType in ['Corporate', 'Local']:
            if contact:
                contact = 'SearchString: \"{0}\"'.format(contact)
            else:
                contact = ''

            if folderID:
                fldID = 'FolderID:\x22{0}\x22 '.format(folderID)
            else:
                fldID = ''
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1} SearchField: Name ContactType: Contact {2} Offset: {3} Limit: 250\r'.format(phonebookType, contact, fldID, self.Offset)
            res = self.SendAndWait(cmdStr, 15, deliTag='**').decode()
            if res:
                self.newList = {}
                nameList = re.findall(self.dirName, res)
                numberList = re.findall(self.dirNumber, res)

                for i, name in nameList:
                    self.newList[i] = {'Name': name}

                for i, number in numberList:
                    if i in self.newList:
                        self.newList[i]['Number'] = number
                    else:
                        self.newList[i] = {'Number': number}
                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            print('Invalid Command for SetPhonebookUpdateHandler')

    def SetPhonebookWriteHandler(self, value, qualifier):
        buttonParam = self.Commands['PhonebookFolderIDSearchResult']['Parameters'][0]
        button = 1
        for i in range(self.MinLabel, self.MaxLabel + 1):
            if str(i) in self.newList:
                self.WriteStatus('PhonebookSearchResult', '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']), {buttonParam: button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {buttonParam: button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {buttonParam: i})

    def UpdatePresentationMode(self, value, qualifier):

        PresentationModeCmdString = 'xStatus Conference Presentation Mode\r'
        self.__UpdateHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def __MatchPresentationMode(self, match, tag):

        ValueStateValues = {
            'Off': 'Off',
            'Sending': 'Sending',
            'Receiving': 'Receiving'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationMode', value, None)

    def SetPresentationPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight',
            'Upper Center': 'UpperCenter',
            'Upper Left': 'UpperLeft',
            'Upper Right': 'UpperRight'
        }

        PresentationPIPPositionCmdString = 'xCommand Video PresentationPIP Set Position: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresentationPIPPosition', PresentationPIPPositionCmdString, value, qualifier)

    def UpdateRemoteNumber(self, value, qualifier):

        CallIDStates = {
            '1': self.CallIDList[0],
            '2': self.CallIDList[1],
            '3': self.CallIDList[2],
            '4': self.CallIDList[3],
            '5': self.CallIDList[4],
        }
        if CallIDStates[qualifier['Call']] == '':
            self.UpdateCallID(None, None)
        else:
            RemoteNumberCmdString = 'xStatus Call {0} RemoteNumber\r'.format(CallIDStates[qualifier['Call']])
            self.__UpdateHelper('RemoteNumber', RemoteNumberCmdString, value, qualifier)

    def __MatchRemoteNumber(self, match, tag):

        CallStates = {
            self.CallIDList[0]: '1',
            self.CallIDList[1]: '2',
            self.CallIDList[2]: '3',
            self.CallIDList[3]: '4',
            self.CallIDList[4]: '5'
        }

        qualifier = {'Call': CallStates[match.group(1).decode()]}
        value = match.group(2).decode()
        self.WriteStatus('RemoteNumber', value, qualifier)

    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        SelfViewCmdString = 'xCommand Video Selfview Set Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):

        SelfViewCmdString = 'xStatus Video Selfview Mode\r'
        self.__UpdateHelper('SelfView', SelfViewCmdString, value, qualifier)

    def __MatchSelfView(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SelfView', value, None)

    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off',
            'Current': 'Current'
        }

        SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)

    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):

        SelfViewDefaultFullscreenModeCmdString = 'xStatus Video Selfview FullscreenMode\r'
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off',
            'Current': 'Current'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SelfViewDefaultFullscreenMode', value, None)

    def SetSelfViewPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left': 'UpperLeft',
            'Upper Center': 'UpperCenter',
            'Upper Right': 'UpperRight',
            'Center Left': 'CenterLeft',
            'Center Right': 'CenterRight',
            'Lower Left': 'LowerLeft',
            'Lower Right': 'LowerRight'
        }

        SelfViewPositionCmdString = 'xConfiguration Video Selfview Default PIPPosition: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)

    def UpdateSelfViewPosition(self, value, qualifier):

        SelfViewPositionCmdString = 'xStatus Video Selfview PIPPosition\r'
        self.__UpdateHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)

    def __MatchSelfViewPosition(self, match, tag):

        ValueStateValues = {
            'UpperLeft': 'Upper Left',
            'UpperCenter': 'Upper Center',
            'UpperRight': 'Upper Right',
            'CenterLeft': 'Center Left',
            'CenterRight': 'Center Right',
            'LowerLeft': 'Lower Left',
            'LowerRight': 'Lower Right'
        }

        value = ValueStateValues[match.group(1).decode() + match.group(2).decode()]
        self.WriteStatus('SelfViewPosition', value, None)

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        StandbyCmdString = 'xCommand Standby {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):
        StandbyCmdString = 'xStatus Standby State\r'
        self.__UpdateHelper('Standby', StandbyCmdString, value, qualifier)

    def __MatchStandby(self, match, tag):

        ValueStateValues = {
            'Off': 'On',
            'Standby': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)

    def SetVideoInput(self, value, qualifier):

        ConnectorIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        VideoInputCmdString = 'xCommand Video Input SetMainVideoSource ConnectorID: {0} SourceId: {1}\r'.format(ConnectorIDStates[qualifier['Connector ID']], ValueStateValues[value])
        self.__SetHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def UpdateVideoInput(self, value, qualifier):

        ConnectorIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }
        VideoInputCmdString = 'xStatus Video Input Connector {0} SourceId\r'.format(ConnectorIDStates[qualifier['Connector ID']])
        self.__UpdateHelper('VideoInput', VideoInputCmdString, value, qualifier)

    def __MatchVideoInput(self, match, tag):

        ConnectorIDStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5'
        }

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        qualifier = {'Connector ID': ConnectorIDStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('VideoInput', value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter += 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        print(match.group(0).decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.CallIDList = ['', '', '', '', '']

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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress,
                                                     self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(
                self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog(
            "{0} module received a request from the device for a {1}, "
            "but device{1} was not provided.\n Please provide a device{1} "
            "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
            "review the communication sheet.\n {2}"
            .format(__name__, credential_type, port_info), 'warning')

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
