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
        self.__maxBufferSize = 100000
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.deviceUsername = 'admin'
        self.devicePassword = ''

        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPeripheral = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofPhonebookSearch = 5
        self._PhonebookSearchOffset = 50

        self.Models = {
            'Webex Room Kit CE9.5.X': self.csco_12_3911_non_P,
            'Webex Room Kit Plus CE9.5.X': self.csco_12_3911_Plus,
            'Webex Room Kit Pro CE9.5.X': self.csco_12_3911_Pro,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutput': {'Parameters': ['Output'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallAnswerState': {'Parameters': ['Call'], 'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Status': {}},
            'CallSetupMode': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusDeviceType': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFocus': {'Parameters': ['Camera'], 'Status': {}},
            'CameraPan': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraPresetRecall': {'Status': {}},
            'CameraPresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'CameraTilt': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'ConnectedDeviceMAC': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedDeviceName': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedDeviceNavigation': {'Status': {}},
            'ConnectedDeviceType': {'Parameters': ['Button'], 'Status': {}},
            'ConnectedDeviceUpdate': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'DisplayName': {'Parameters': ['Call'], 'Status': {}},
            'DNSDomainName': {'Status': {}},
            'DNSDomainNameCommand': {'Status': {}},
            'DNSServerAddress': {'Parameters': ['Server'], 'Status': {}},
            'DNSServerAddressCommand': {'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'FarEndCameraPanTilt': {'Status': {}},
            'FarEndCameraPresetRecall': {'Status': {}},
            'FarEndCameraSource': {'Status': {}},
            'FarEndCameraZoom': {'Status': {}},
            'FarEndControl': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'GatewayAddress': {'Status': {}},
            'H323AliasE164Command': {'Status': {}},
            'H323AliasIDCommand': {'Status': {}},
            'H323AliasIDStatus': {'Status': {}},
            'H323GatekeeperAddress': {'Status': {}},
            'H323GatekeeperAddressCommand': {'Status': {}},
            'H323GatekeeperStatus': {'Status': {}},
            'H323ProfileAuthenticationLoginNameCommand': {'Status': {}},
            'H323ProfileAuthenticationPasswordCommand': {'Status': {}},
            'Hook': {'Parameters': ['Protocol', 'Number'], 'Status': {}},
            'Input': {'Status': {}},
            'InputHDMILevel': {'Status': {}},
            'InputMicLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputSignal': {'Parameters': ['Input'], 'Status': {}},
            'IPAddress': {'Status': {}},
            'IPv4AddressCommand': {'Status': {}},
            'IPv4GatewayCommand': {'Status': {}},
            'IPv4SubnetMaskCommand': {'Status': {}},
            'LayoutSet': {'Parameters': ['Target'], 'Status': {}},
            'MACAddress': {'Status': {}},
            'Macro': {'Status': {}},
            'MacroAutoStart': {'Status': {}},
            'MacroMode': {'Status': {}},
            'RestartMacros': {'Status': {}},
            'MicrophonesMute': {'Status': {}},
            'NetworkAssignment': {'Status': {}},
            'PeopleCountCurrent': {'Status': {}},
            'PeopleCountOutofCall': {'Status': {}},
            'PeoplePresence': {'Status': {}},
            'PeoplePresenceDetector': {'Status': {}},
            'PhonebookFolderIDNavigation': {'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': {'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'Presentation': {'Status': {}},
            'PresentationExternalSourceSelectCommand': {'Status': {}},
            'PresentationModeStatus': {'Status': {}},
            'PresentationSendingModeStatus': {'Parameters': ['Instance'], 'Status': {}},
            'PresentationSourceStatus': {'Parameters': ['Instance'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Reboot': {'Status': {}},
            'RemoteNumber': {'Parameters': ['Call'], 'Status': {}},
            'SelfView': {'Status': {}},
            'SelfViewDefaultFullscreenMode': {'Status': {}},
            'SelfViewPosition': {'Status': {}},
            'SIPRegistrationStatus': {'Status': {}},
            'SIPURICommand': {'Status': {}},
            'SIPURIStatus': {'Status': {}},
            'SleepTimer': {'Status': {}},
            'SpeakerTrackControl': {'Status': {}},
            'SpeakerTrackMode': {'Status': {}},
            'Standby': {'Status': {}},
            'SubnetMask': {'Status': {}},
            'SystemUnitNameCommand': {'Status': {}},
            'SystemUnitNameStatus': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.tshellerror = False
        self.__CallID = []
        self.callID = compile('\*s Call (\d+) Status: \w+\r\n')
        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n')
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "(.*)"\r\n')
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "(.*)"\r\n')
        self.callStatusDeviceTypePattern = compile('\*s Call \d+ DeviceType: (Endpoint|MCU)\r\n')
        self.callStatusTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n')
        self.callAnswerStatePattern = compile('\*s Call \d+ AnswerState: (Unanswered|Ignored|Autoanswered|Answered)\r\n')
        self.MinLabel = 1
        self.MaxLabel = 5
        self.Offset = 0
        self.newList = {}
        self.dirName = compile('\*r PhonebookSearchResult Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: "(.+)"')
        self.FolderMin = 1
        self.FolderLimit = 5
        self.folderList = {}
        self.FolderNameRex = compile('\*r PhonebookSearchResult Folder (\d+) Name: "(.+)"\r\n')
        self.FolderIDRex = compile('\*r PhonebookSearchResult Folder (\d+) FolderId: "(.+)"')
        self.FolderIDNumber = ''
        self.deviceName = []
        self.deviceType = []
        self.deviceID = []
        self.MaxDevices = 0
        self.startPeripheral = 0
        self.peripheralName = compile('\*s Peripherals ConnectedDevice \d+ Name: "(.+)"\r\n')
        self.peripheralType = compile('\*s Peripherals ConnectedDevice \d+ Type: (.+)\r\n')
        self.peripheralMAC = compile('\*s Peripherals ConnectedDevice \d+ ID: "(.+)"\r\n')

        self.startCallHist = 0
        self.HistorydisplayNameList = {}
        self.HistorycallBackNumberList = {}
        self.HistorylastOccurrenceTimeList = {}
        self.HistoryoccurrenceTypeList = {}
        self.HistoryoccurrenceCountList = {}
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')

        if self._CallHistoryOccurrenceType == 'Time':
            self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) Count: (\d+)\r\n')
        self.occurrenceType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')

        if self.Unidirectional == 'False':
            self.AddMatchString( compile(b'\*c xConfiguration Audio Output (InternalSpeaker|Line [1-6]|HDMI [1-3]) Mode: (On|Off)\r\n'), self.__MatchAudioOutput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'xstatus call\r\n\*\* end\r\n'), self.__MatchCallStatusIdle, None)
            self.AddMatchString(compile(b'\*s Call (\d+) [\s\S]+\*\* end\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (Auto|Dual|Single|DualPresentationOnly|TriplePresentationOnly|Triple)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Domain Name: "(.*)"'), self.__MatchDNSDomainName, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-5]) Address: "([0-9.]{0,15})"\r\n'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'version="([\w.]+)" apiVersion'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{0,15})"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{0,15})"\r\n'), self.__MatchH323GatekeeperAddress, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 H323Alias ID: "(|[\W\w]+)"\r\n'), self.__MatchH323AliasIDStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoSource: ([1-4]|Composed)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (HDMI [1-5]) Level: (-?\d+)\r\n'), self.__MatchInputHDMILevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-3]) Level: (\d+)\r\n'), self.__MatchInputMicLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-3]|HDMI [1-5]) Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Video Input Connector ([1-2]) Connected: (True|False|Unknown)\r\n'), self.__MatchInputSignal, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{0,15})"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "(|[:0-9A-Z]{17})"\r\n\*\* end\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros AutoStart: (On|Off)\r\n'), self.__MatchMacroAutoStart, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros Mode: (On|Off)\r\n'), self.__MatchMacroMode, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n\*\* end\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeopleCount Current: ([-\d]+)\r\n'), self.__MatchPeopleCountCurrent, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/RoomAnalytics/PeopleCount/Current"\r\n'), self.__MatchPeopleCountCurrentOff, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeopleCountOutOfCall: (On|Off)\r\n'), self.__MatchPeopleCountOutofCall, None)
            self.AddMatchString(compile(b'\*r Configuration XPath: "Configuration/RoomAnalytics/PeopleCountOutOfCall"\r\n'), self.__MatchPeopleCountOutofCallOff, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeoplePresence: (Yes|No|Unknown)\r\n'), self.__MatchPeoplePresence, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeoplePresenceDetector: (On|Off)\r\n'), self.__MatchPeoplePresenceDetector, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-6])\r\n'), self.__MatchPresentationSourceStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationSourceStatusStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Off|Sending|Receiving)\r\n'), self.__MatchPresentationModeStatus, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusStop, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Selfview Default FullscreenMode: (Off|On|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (UpperLeft|UpperCenter|UpperRight|CenterLeft|CenterRight|LowerLeft|LowerRight)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s SIP Registration 1 Status: (Deregister|Failed|Inactive|Registered|Registering)\r\n'), self.__MatchSIPRegistrationStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration SIP URI: "(.*?)"\r\n'), self.__MatchSIPURIStatus, None)
            self.AddMatchString(compile(b'\*s Cameras SpeakerTrack Status: (Active|Inactive)\r\n\*\* end\r\n'), self.__MatchSpeakerTrackControl, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|EnteringStandby|Halfwake|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'\*c xConfiguration Cameras SpeakerTrack Mode: (Auto|Off)\r\n'), self.__MatchSpeakerTrackMode, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{0,15})"\r\n'), self.__MatchSubnetMask, None)
            self.AddMatchString(compile(b'\*c xConfiguration SystemUnit Name: "(.*?)"\r\n'), self.__MatchSystemUnitNameStatus, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchVolume, None)
            if 'Serial' in self.ConnectionType:
                self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            if self.ConnectionType == 'Ethernet':
                self.AddMatchString(compile(b'tshell: Failed to connect to system software\r\n'), self.__MatchTSHell, None)

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
        if value not in ['Time', 'Frequency']:
            self.Error(['Invalid Call History Occurrence Type parameter.'])

    @property
    def NumberofCallHistory(self):
        return self._NumberofCallHistory

    @NumberofCallHistory.setter
    def NumberofCallHistory(self, value):
        self._NumberofCallHistory = int(value)
        if int(value)> 20 or int(value) < 1:
            self.Error(['Number of Call History is out of range.'])

    @property
    def NumberofPeripheral(self):
        return self._NumberofPeripheral

    @NumberofPeripheral.setter
    def NumberofPeripheral(self, value):
        self._NumberofPeripheral = int(value)
        if int(value) > 10 or int(value) < 1:
            self.Error(['Number of Peripheral is out of range.'])

    @property
    def NumberofPhonebookFolderSearch(self):
        return self._NumberofPhonebookFolderSearch

    @NumberofPhonebookFolderSearch.setter
    def NumberofPhonebookFolderSearch(self, value):
        self._NumberofPhonebookFolderSearch = int(value)
        if int(value) > 10 or int(value) < 1:
            self.Error(['Number of Phonebook Folder Search is out of range.'])

    @property
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        self._NumberofPhonebookSearch = int(value)
        if int(value) > 10 or int(value) < 1:
            self.Error(['Number of Phonebook Search is out of range.'])

    @property
    def PhonebookSearchOffset(self):
        return self._PhonebookSearchOffset

    @PhonebookSearchOffset.setter
    def PhonebookSearchOffset(self, value):
        self._PhonebookSearchOffset = int(value)
        if int(value) > 250 or int(value) < 20:
            self.Error(['Phonebook Search Offset is out of range.'])

    def __MatchTSHell(self, match, tag):
        self.tshellerror = True

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername + '\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAudioOutput(self, value, qualifier):

        if value in ['On', 'Off']:
            AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode:{1}\r'.format(self.AudioOutputStates[qualifier['Output']], value)
            self.__SetHelper('AudioOutput', AudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):

        AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode\r'.format(self.AudioOutputStates[qualifier['Output']])
        self.__UpdateHelper('AudioOutput', AudioOutputCmdString, value, qualifier)

    def __MatchAudioOutput(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('AudioOutput', value, {'Output': self.AudioOutputValues[match.group(1).decode()]})

    def SetAutoAnswer(self, value, qualifier):

        if value in ['On', 'Off']:
            AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(value)
            self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('AutoAnswer', value, None)

    def SetCallHistoryRefresh(self, value, qualifier):
        self.Debug = True

        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        self.Debug = True

        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, 50, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CallHistoryCmdString, 5, deliTag=b'** end')
        if res:
            res = res.decode()
            displayNameList = dict(findall(self.displayName, res))
            callBackNumberList = dict(findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(findall(self.occurrenceType, res))
            occurrenceCountList = dict(findall(self.occurrenceCount, res))

            for button in range(1, self._NumberofCallHistory + 1):
                index = str(button - 1)
                if index in displayNameList:
                    self.WriteStatus('CallHistory', displayNameList[index], {'Button': str(button), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', callBackNumberList[index], {'Button': str(button), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', lastOccurrenceTimeList[index], {'Button': str(button), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', occurrenceTypeList[index], {'Button': str(button), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', occurrenceCountList[index], {'Button': str(button), 'Detail Type': 'Occurrence Count'})
                else:
                    self.WriteStatus('CallHistory', '', {'Button': str(button), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', '', {'Button': str(button), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', '', {'Button': str(button), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', '', {'Button': str(button), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', '', {'Button': str(button), 'Detail Type': 'Occurrence Count'})
        else:
            for index in range(1, self._NumberofCallHistory + 1):
                self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Display Name'})
                self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Callback Number'})
                self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Occurrence Type'})
                self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Occurrence Count'})

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

        if 1 <= int(value) <= 20:
            number = self.ReadStatus('CallHistory', {'Button': value, 'Detail Type': 'Callback Number'})
            if number:
                self.Send('xCommand Dial Number:"{0}"\r'.format(number))
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')

    def SetCallSetupMode(self, value, qualifier):

        if value in ['Gatekeeper', 'Direct']:
            CallSetupModeCmdString = 'xConfiguration H323 CallSetup Mode: {0}\r'.format(value)
            self.__SetHelper('CallSetupMode', CallSetupModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallSetupMode')

    def UpdateCallSetupMode(self, value, qualifier):

        CallSetupModeCmdString = 'xConfiguration H323 CallSetup Mode\r'
        self.__UpdateHelper('CallSetupMode', CallSetupModeCmdString, value, qualifier)

    def __MatchCallSetupMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('CallSetupMode', value, None)

    def UpdateCallStatus(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateDisplayName(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateRemoteNumber(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateCallStatusDeviceType(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateCallStatusType(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def UpdateCallAnswerState(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', value, qualifier)

    def __MatchCallStatusIdle(self, match, tag):

        self.__CallID = []
        for index in range(1, 6):
            self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
            self.WriteStatus('DisplayName', '', {'Call': str(index)})
            self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
            self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(index)})
            self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
            self.WriteStatus('CallAnswerState', 'Unknown', {'Call': str(index)})

    def __MatchCallStatus(self, match, tag):

        callValue = {
            'Idle': 'Idle',
            'Dialling': 'Dialing',
            'Ringing': 'Ringing',
            'Connecting': 'Connecting',
            'Connected': 'Connected',
            'Disconnecting': 'Disconnecting',
            'OnHold': 'On Hold',
            'EarlyMedia': 'Early Media',
            'Preserved': 'Preserved',
            'RemotePreserved': 'Remote Preserved',
        }

        res = match.group(0).decode()
        self.__CallID = findall(self.callID, res)
        callList = findall(self.callStatus, res)
        displayNameList = findall(self.displayNamePattern, res)
        remoteNumberList = findall(self.remoteNumberPattern, res)
        callstatusDeviceTypeList = findall(self.callStatusDeviceTypePattern, res)
        callStatusTypeList = findall(self.callStatusTypePattern, res)
        callAnswerStateList = findall(self.callAnswerStatePattern, res)

        index = 0
        for index in range(1, len(callList) + 1, 1):
            try:
                self.WriteStatus('CallStatus', callValue[callList[index - 1]], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('CallStatus', '', {'Call': str(index)})
            try:
                self.WriteStatus('DisplayName', displayNameList[index - 1], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
            try:
                self.WriteStatus('RemoteNumber', remoteNumberList[index - 1], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
            try:
                self.WriteStatus('CallStatusDeviceType', callstatusDeviceTypeList[index - 1], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(index)})
            try:
                self.WriteStatus('CallStatusType', callStatusTypeList[index - 1], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
            try:
                self.WriteStatus('CallAnswerState', callAnswerStateList[index - 1], {'Call': str(index)})
            except IndexError:
                self.WriteStatus('CallAnswerState', 'Unknown', {'Call': str(index)})
        else:
            index += 1
            while index <= 5:
                self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(index)})
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
                self.WriteStatus('CallAnswerState', 'Unknown', {'Call': str(index)})
                index += 1

    def SetCameraFocus(self, value, qualifier):

        CameraFocusCmdString = ''
        camID = qualifier.get('Camera', '1')
        if 1 <= int(camID) <= 7:
            if value in ['Far', 'Near', 'Stop']:
                CameraFocusCmdString = 'xCommand Camera Ramp CameraId:{0} Focus:{1}\r'.format(camID, value)
            elif value == 'Auto':
                CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:{0}\r'.format(camID)

            if CameraFocusCmdString:
                self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraFocus')
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        CameraPanCmdString = ''
        camID = qualifier.get('Camera', '1')
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan: Stop\r'.format(camID)
            elif value in ['Left', 'Right']:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan:{1} PanSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraPanCmdString:
                self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPan')
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetRecall', 'xCommand Camera Preset Activate PresetId: {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        camID = qualifier.get('Camera', '1')
        if 1 <= int(camID) <= 7 and 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetSave', 'xCommand Camera Preset Store PresetId:{0} CameraId:{1}\r'.format(value, camID), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraTilt(self, value, qualifier):

        CameraTiltCmdString = ''
        camID = qualifier.get('Camera', '1')
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt: Stop\r'.format(camID)
            elif value in ['Up', 'Down']:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt:{1} TiltSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraZoom(self, value, qualifier):

        CameraZoomCmdString = ''
        camID = qualifier.get('Camera', '1')
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom: Stop\r'.format(camID)
            elif value in ['In', 'Out']:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom:{1} ZoomSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetConnectedDeviceNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.MaxDevices > 0:
            if 'Page' in value:
                NumberOfAdvance = self._NumberofPeripheral
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.startPeripheral < self.MaxDevices:
                    self.startPeripheral += NumberOfAdvance
            elif 'Up' in value:
                self.startPeripheral -= NumberOfAdvance

            if self.startPeripheral < 1:
                self.startPeripheral = 0

            button = 0
            for index in range(self.startPeripheral, self.startPeripheral + self._NumberofPeripheral):
                if 0 <= index < self.MaxDevices:
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[index], {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[index], {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[index], {'Button': button + 1})
                    button += 1

            if button <= self._NumberofPeripheral:
                self.WriteStatus('ConnectedDeviceName', '***End of list***', {'Button': button + 1})
                self.WriteStatus('ConnectedDeviceType', '***End of list***', {'Button': button + 1})
                self.WriteStatus('ConnectedDeviceMAC', '***End of list***', {'Button': button + 1})
                button += 1
                for index in range(button, self._NumberofPeripheral + 1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button': button + 1})
        else:
            self.Discard('Invalid Command for SetConnectedDeviceNavigation')

    def SetConnectedDeviceUpdate(self, value, qualifier):

        ConnectedDeviceUpdateCmdString = 'xStatus Peripherals ConnectedDevice\r'
        res = self.SendAndWait(ConnectedDeviceUpdateCmdString, 3, deliTag=b'** end')  # ** end\r\n is used for delimiter
        if res:
            res = res.decode()
            self.deviceName = findall(self.peripheralName, res)
            self.deviceType = findall(self.peripheralType, res)
            self.deviceID = findall(self.peripheralMAC, res)
            self.MaxDevices = len(self.deviceName)

            button = 1
            for index in range(0, self._NumberofPeripheral):
                if index < self.MaxDevices:
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[index], {'Button': index + 1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[index], {'Button': index + 1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[index], {'Button': index + 1})
                    button += 1
            if button <= self._NumberofPeripheral:
                self.WriteStatus('ConnectedDeviceName', '***End of list***', {'Button': button})
                self.WriteStatus('ConnectedDeviceType', '***End of list***', {'Button': button})
                self.WriteStatus('ConnectedDeviceMAC', '***End of list***', {'Button': button})
                button += 1
                for index in range(button, self._NumberofPeripheral + 1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button': index})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button': index})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button': index})

    def SetDisplayMode(self, value, qualifier):

        if value in ['Dual', 'Single', 'Dual Presentation Only', 'Auto']:
            DisplayModeCmdString = 'xConfiguration Video Monitors: {0}\r'.format(self.DisplayModeStates[value])
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):

        DisplayModeCmdString = 'xConfiguration Video Monitors\r'
        self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        value = self.DisplayModeValues[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def UpdateDNSDomainName(self, value, qualifier):

        DNSDomainNameCmdString = 'xStatus Network 1 DNS Domain Name\r'
        self.__UpdateHelper('DNSDomainName', DNSDomainNameCmdString, value, qualifier)

    def __MatchDNSDomainName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DNSDomainName', value, None)

    def SetDNSDomainNameCommand(self, value, qualifier):

        DNSString = value
        if DNSString:
            DNSDomainNameCommandCmdString = 'xConfiguration Network 1 DNS Domain Name: {0}\r'.format(DNSString)
            self.__SetHelper('DNSDomainNameCommand', DNSDomainNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSDomainNameCommand')

    def UpdateDNSServerAddress(self, value, qualifier):

        if 1 <= int(qualifier['Server']) <= 5:  # 1-5 verified to work with both devices
            DNSServerAddressCmdString = 'xStatus Network 1 DNS Server {0} Address\r'.format(qualifier['Server'])
            self.__UpdateHelper('DNSServerAddress', DNSServerAddressCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDNSServerAddress')

    def __MatchDNSServerAddress(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('DNSServerAddress', value, {'Server': match.group(1).decode()})

    def SetDNSServerAddressCommand(self, value, qualifier):

        DNSString = value
        if DNSString:
            DNSServerAddressCommandCmdString = 'xConfiguration Network 1 DNS Server 1 Address: {0}\r'.format(DNSString)
            self.__SetHelper('DNSServerAddressCommand', DNSServerAddressCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def SetDoNotDisturb(self, value, qualifier):

        ValueStateValues = {
            'Active': 'Activate',
            'Inactive': 'Deactivate'
        }

        DoNotDisturbCmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbCmdString = 'xStatus Conference DoNotDisturb\r'
        self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DoNotDisturb', value, None)

    def SetDTMF(self, value, qualifier):

        if value in '0123456789*#':
            DTMFCmdString = 'xCommand Call DTMFSend DTMFString:{0}\r'.format(value)
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFarEndCameraPanTilt(self, value, qualifier):

        FarEndCameraPanTiltCmdString = ''
        if value in ['Up', 'Down', 'Left', 'Right', 'Stop']:
            if value == 'Stop':
                FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Stop\r'
            else:
                FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Move Value:{0}\r'.format(value)

            if FarEndCameraPanTiltCmdString:
                self.__SetHelper('FarEndCameraPanTilt', FarEndCameraPanTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetFarEndCameraPanTilt')
        else:
            self.Discard('Invalid Command for SetFarEndCameraPanTilt')

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            FarEndCameraPresetRecallCmdString = 'xCommand Call FarEndControl RoomPreset Activate PresetId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', FarEndCameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraSource(self, value, qualifier):

        if 0 <= int(value) <= 15:
            FarEndCameraSourceCmdString = 'xCommand Call FarEndControl Source Select SourceId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraSource', FarEndCameraSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSource')

    def SetFarEndCameraZoom(self, value, qualifier):

        FarEndCameraZoomCmdString = ''
        if value in ['In', 'Out']:
            FarEndCameraZoomCmdString = 'xCommand Call FarEndControl Camera Move Value:Zoom{0}\r'.format(value)
        elif value == 'Stop':
            FarEndCameraZoomCmdString = 'xCommand Call FarEndControl Camera Stop\r'

        if FarEndCameraZoomCmdString:
            self.__SetHelper('FarEndCameraZoom', FarEndCameraZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraZoom')

    def SetFarEndControl(self, value, qualifier):

        if value in ['On', 'Off']:
            FarEndControlCmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(value)
            self.__SetHelper('FarEndControl', FarEndControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndControl')

    def UpdateFarEndControl(self, value, qualifier):

        FarEndControlCmdString = 'xConfiguration Conference FarEndControl Mode\r'
        self.__UpdateHelper('FarEndControl', FarEndControlCmdString, value, qualifier)

    def __MatchFarEndControl(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FarEndControl', value, None)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'xgetxml /status/standby\r'  # not documented, obtained via testing with device
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def UpdateGatewayAddress(self, value, qualifier):

        GatewayAddressCmdString = 'xStatus Network 1 IPv4 Gateway\r'
        self.__UpdateHelper('GatewayAddress', GatewayAddressCmdString, value, qualifier)

    def __MatchGatewayAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('GatewayAddress', value, None)

    def SetH323AliasE164Command(self, value, qualifier):

        if value:
            H323AliasE164CommandCmdString = 'xConfiguration H323 H323Alias E164: {0}\r'.format(value)
            self.__SetHelper('H323AliasE164Command', H323AliasE164CommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasE164Command')

    def SetH323AliasIDCommand(self, value, qualifier):

        if value:
            H323AliasIDCommandCmdString = 'xConfiguration H323 H323Alias ID: {0}\r'.format(value)
            self.__SetHelper('H323AliasIDCommand', H323AliasIDCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasIDCommand')

    def UpdateH323AliasIDStatus(self, value, qualifier):

        H323AliasIDStatusCmdString = 'xConfiguration H323 H323Alias ID\r'
        self.__UpdateHelper('H323AliasIDStatus', H323AliasIDStatusCmdString, value, qualifier)

    def __MatchH323AliasIDStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323AliasIDStatus', value, None)

    def UpdateH323GatekeeperAddress(self, value, qualifier):

        H323GatekeeperAddressCmdString = 'xStatus H323 Gatekeeper Address\r'
        self.__UpdateHelper('H323GatekeeperAddress', H323GatekeeperAddressCmdString, value, qualifier)

    def __MatchH323GatekeeperAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323GatekeeperAddress', value, None)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        if value:
            H323GatekeeperAddressCommandCmdString = 'xConfiguration H323 Gatekeeper Address: {0}\r'.format(value)
            self.__SetHelper('H323GatekeeperAddressCommand', H323GatekeeperAddressCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323GatekeeperAddressCommand')

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

    def SetH323ProfileAuthenticationLoginNameCommand(self, value, qualifier):

        if value:
            H323ProfileAuthenticationLoginNameCommandCmdString = 'xConfiguration H323 Authentication LoginName: {0}\r'.format(value)
            self.__SetHelper('H323ProfileAuthenticationLoginNameCommand', H323ProfileAuthenticationLoginNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationLoginNameCommand')

    def SetH323ProfileAuthenticationPasswordCommand(self, value, qualifier):

        if value:
            H323ProfileAuthenticationPasswordCommandCmdString = 'xConfiguration H323 Authentication Password: {0}\r'.format(value)
            self.__SetHelper('H323ProfileAuthenticationPasswordCommand', H323ProfileAuthenticationPasswordCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationPasswordCommand')

    def SetHook(self, value, qualifier):

        ProtocolStates = {
            'Auto': 'Auto',
            'SIP': 'Sip',
            'H323': 'H323',
            'H320': 'H320',
            'Spark': 'Spark'
        }

        if value in ['Accept', 'Reject', 'Disconnect All']:
            self.__SetHelper('Hook', 'xCommand Call {0}\r'.format(value.replace('All', '')), value, qualifier)
        elif 'Resume' in value or 'Disconnect' in value or 'Hold' in value or 'Join' in value:
            val = value.split(' ')
            cmd = val[0]
            index = int(val[1]) - 1
            try:
                self.__SetHelper('Hook', 'xCommand Call {0} CallId: {1}\r'.format(cmd, self.__CallID[index]), value,
                                 qualifier)
            except IndexError:
                self.Discard('Invalid Command for SetHook')
        elif value == 'Dial':
            number = qualifier['Number']
            protocol = qualifier['Protocol']
            if number:
                if protocol == 'Auto':
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\" Protocol:{1}\r'.format(number, ProtocolStates[protocol]), value, qualifier)
            else:
                self.Discard('Invalid Command for SetHook')
        else:
            self.Discard('Invalid Command for SetHook')

    def SetInput(self, value, qualifier):

        if 1 <= int(value) <= 5:
            InputCmdString = 'xCommand Video Input SetMainVideoSource ConnectorId: {0}\r'.format(value)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xStatus Video Input MainVideoSource\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetInputHDMILevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -24,
            'Max': 0
        }

        if 1 <= int(qualifier['Input']) <= 5 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputHDMILevelCmdString = 'xConfiguration Audio Input {0} Level:{1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputHDMILevel', InputHDMILevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def UpdateInputHDMILevel(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= 5:
            InputHDMILevelCmdString = 'xConfiguration Audio Input {0} Level\r'.format(qualifier['Input'])
            self.__UpdateHelper('InputHDMILevel', InputHDMILevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def __MatchInputHDMILevel(self, match, tag):
        """Input HDMI Level MatchString Handler

        """
        value = int(match.group(2).decode())
        self.WriteInputHDMILevel(value, {'Input': match.group(1).decode()}, 'Live')

    def SetInputMicLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': self.InputMicLevelMax
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputMicLevelCmdString = 'xConfiguration Audio Input {0} Level:{1}\r'.format(self.InputMicLevelStates[qualifier['Input']], value)
            self.__SetHelper('InputMicLevel', InputMicLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLevel')

    def UpdateInputMicLevel(self, value, qualifier):

        InputMicLevelCmdString = 'xConfiguration Audio Input {0} Level\r'.format(self.InputMicLevelStates[qualifier['Input']])
        self.__UpdateHelper('InputMicLevel', InputMicLevelCmdString, value, qualifier)

    def __MatchInputMicLevel(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('InputMicLevel', value, {'Input': match.group(1).decode()})

    def SetInputMute(self, value, qualifier):

        if value in ['On', 'Off']:
            InputMuteCmdString = 'xConfiguration Audio Input {0} Mode:{1}\r'.format(self.InputMuteStates[qualifier['Input']], value)
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        InputMuteCmdString = 'xConfiguration Audio Input {0} Mode\r'.format(self.InputMuteStates[qualifier['Input']])
        self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)

    def __MatchInputMute(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('InputMute', value, {'Input': self.InputMuteValues[match.group(1).decode()]})

    def UpdateInputSignal(self, value, qualifier):

        if qualifier['Input'] in ['1', '2']:
            InputSignalCmdString = 'xStatus Video Input Connector {0} Connected\r'.format(qualifier['Input'])
            self.__UpdateHelper('InputSignal', InputSignalCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignal')

    def __MatchInputSignal(self, match, tag):

        value = match.group(2).decode()
        self.WriteStatus('InputSignal', value, {'Input': match.group(1).decode()})

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = 'xStatus Network 1 IPv4 Address\r'
        self.__UpdateHelper('IPAddress', IPAddressCmdString, value, qualifier)

    def __MatchIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPAddress', value, None)

    def SetIPv4AddressCommand(self, value, qualifier):

        if value:
            IPv4AddressCommandCmdString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(value)
            self.__SetHelper('IPv4AddressCommand', IPv4AddressCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4AddressCommand')

    def SetIPv4GatewayCommand(self, value, qualifier):

        if value:
            IPv4GatewayCommandCmdString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(value)
            self.__SetHelper('IPv4GatewayCommand', IPv4GatewayCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4GatewayCommand')

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        if value:
            IPv4SubnetMaskCommandCmdString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(value)
            self.__SetHelper('IPv4SubnetMaskCommand', IPv4SubnetMaskCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4SubnetMaskCommand')

    def SetLayoutSet(self, value, qualifier):

        TargetStates = {
            'Local': 'local',
            'Remote': 'remote'
        }

        ValueStateValues = {
            'Auto': 'auto',
            'Custom': 'custom',
            'Equal': 'equal',
            'Overlay': 'overlay',
            'Prominent': 'prominent',
            'Single': 'single'
        }

        LayoutSetCmdString = 'xCommand Video Layout LayoutFamily Set Target: {0} LayoutFamily:{1}\r'.format(TargetStates[qualifier['Target']], ValueStateValues[value])
        self.__SetHelper('LayoutSet', LayoutSetCmdString, value, qualifier)

    def UpdateMACAddress(self, value, qualifier):

        MACAddressCmdString = 'xStatus Network 1 Ethernet MacAddress\r'
        self.__UpdateHelper('MACAddress', MACAddressCmdString, value, qualifier)

    def __MatchMACAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MACAddress', value, None)

    def SetMacro(self, value, qualifier):

        nameValue = qualifier['Name']
        if nameValue and value in ['Activate', 'Deactivate']:
            MacroSetCmdString = 'xCommand Macros Macro {} Name: "{}"\r'.format(value, nameValue)
            self.__SetHelper('Macro', MacroSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def SetMacroAutoStart(self, value, qualifier):

        if value in ['On', 'Off']:
            MacroSetCmdString = 'xConfiguration Macros AutoStart: {}\r'.format(value)
            self.__SetHelper('MacroAutoStart', MacroSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacroAutoStart')

    def UpdateMacroAutoStart(self, value, qualifier):
        self.__UpdateHelper('MacroAutoStart', 'xConfiguration Macros AutoStart\r', value, qualifier)

    def __MatchMacroAutoStart(self, match, tag):
        self.WriteStatus('MacroAutoStart', match.group(1).decode(), None)

    def SetMacroMode(self, value, qualifier):

        if value in ['On', 'Off']:
            MacroSetCmdString = 'xConfiguration Macros Mode: {}\r'.format(value)
            self.__SetHelper('MacroMode', MacroSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacroMode')

    def UpdateMacroMode(self, value, qualifier):
        self.__UpdateHelper('MacroMode', 'xConfiguration Macros Mode\r', value, qualifier)

    def __MatchMacroMode(self, match, tag):
        self.WriteStatus('MacroMode', match.group(1).decode(), None)

    def SetRestartMacros(self, value, qualifier):

        MacroSetCmdString = 'xCommand Macros Runtime Restart\r'
        self.__SetHelper('RestartMacros', MacroSetCmdString, value, qualifier)

    def SetMicrophonesMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        MicrophonesMuteCmdString = 'xCommand Audio Microphones {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def UpdateMicrophonesMute(self, value, qualifier):

        MicrophonesMuteCmdString = 'xStatus Audio Microphones Mute\r'
        self.__UpdateHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def __MatchMicrophonesMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MicrophonesMute', value, None)

    def UpdateNetworkAssignment(self, value, qualifier):

        NetworkAssignmentCmdString = 'xConfiguration Network 1 IPv4 Assignment\r'
        self.__UpdateHelper('NetworkAssignment', NetworkAssignmentCmdString, value, qualifier)

    def __MatchNetworkAssignment(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('NetworkAssignment', value, None)

    def UpdatePeopleCountCurrent(self, value, qualifier):

        PeopleCountCurrentCmdString = 'xStatus RoomAnalytics PeopleCount Current\r'
        self.__UpdateHelper('PeopleCountCurrent', PeopleCountCurrentCmdString, value, qualifier)

    def __MatchPeopleCountCurrent(self, match, tag):
        value = match.group(1).decode()
        value = 'Off' if '-' in value else value
        self.WriteStatus('PeopleCountCurrent', value, None)

    def __MatchPeopleCountCurrentOff(self, match, tag):

        self.WriteStatus('PeopleCountCurrent', 'Off', None)

    def SetPeopleCountOutofCall(self, value, qualifier):

        if value in ['On', 'Off']:
            PeopleCountOutofCallCmdString = 'xConfiguration RoomAnalytics PeopleCountOutOfCall: {}\r'.format(value)
            self.__SetHelper('PeopleCountOutofCall', PeopleCountOutofCallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeopleCountOutofCall')

    def UpdatePeopleCountOutofCall(self, value, qualifier):

        PeopleCountOutofCallCmdString = 'xConfiguration RoomAnalytics PeopleCountOutOfCall\r'
        self.__UpdateHelper('PeopleCountOutofCall', PeopleCountOutofCallCmdString, value, qualifier)

    def __MatchPeopleCountOutofCall(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PeopleCountOutofCall', value, None)

    def __MatchPeopleCountOutofCallOff(self, match, tag):

        self.WriteStatus('PeopleCountOutofCall', 'Off', None)

    def UpdatePeoplePresence(self, value, qualifier):

        PeoplePresenceCmdString = 'xStatus RoomAnalytics PeoplePresence\r'
        self.__UpdateHelper('PeoplePresence', PeoplePresenceCmdString, value, qualifier)

    def __MatchPeoplePresence(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PeoplePresence', value, None)

    def SetPeoplePresenceDetector(self, value, qualifier):

        if value in ['On', 'Off']:
            PeoplePresenceDetectorCmdString = 'xConfiguration RoomAnalytics PeoplePresenceDetector: {}\r'.format(value)
            self.__SetHelper('PeoplePresenceDetector', PeoplePresenceDetectorCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPeoplePresenceDetector')

    def UpdatePeoplePresenceDetector(self, value, qualifier):

        PeoplePresenceDetectorCmdString = 'xConfiguration RoomAnalytics PeoplePresenceDetector\r'
        self.__UpdateHelper('PeoplePresenceDetector', PeoplePresenceDetectorCmdString, value, qualifier)

    def __MatchPeoplePresenceDetector(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PeoplePresenceDetector', value, None)

    def SetPhonebookFolderIDNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and len(self.folderList) > 0:
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
            for index in range(self.FolderMin, self.FolderLimit + 1):  # populate up to max labels configured
                if str(index) in self.folderList:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(index)]['Name']),
                                     {'Button': button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                button += 1
                for index in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': index})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDNavigation')

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):
        self.Debug = True

        if self.folderList:
            folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
            if folderName != '***End of list***':
                self.FolderIDNumber = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName][0]
        else:
            self.Discard('No Folders Found.')

    def SetPhonebookFolderIDUpdate(self, value, qualifier):

        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: 100\r'.format(
                phonebookValue)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
                res = res.decode()
                self.folderList = {}
                folderName = findall(self.FolderNameRex, res)
                folderID = findall(self.FolderIDRex, res)
                for index, name in folderName:
                    self.folderList[index] = {'Name': name}

                for index, id_ in folderID:
                    if index in self.folderList:
                        self.folderList[index]['ID'] = id_
                    else:
                        self.folderList[index] = {'ID': id_}

                button = 1
                for index in range(1, self._NumberofPhonebookFolderSearch + 1):  # populate up to max labels configured
                    if str(index) in self.folderList:
                        self.WriteStatus('PhonebookFolderIDSearchResult',
                                         '{0}'.format(self.folderList[str(index)]['Name']), {'Button': int(index)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for index in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': index})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate')

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and len(self.newList) > 0:
            if 'Page' in value:
                NumberOfAdvance = self._NumberofPhonebookSearch
            else:
                NumberOfAdvance = 1

            if 'Down' in value and self.MinLabel <= len(self.newList):  # Stop scroll up to as many configured
                self.MinLabel += NumberOfAdvance
                self.MaxLabel += NumberOfAdvance
            elif 'Up' in value:
                self.MinLabel -= NumberOfAdvance
                self.MaxLabel -= NumberOfAdvance
            if self.MinLabel < 1:  # Load Previous page if min label to show goes below 1
                if self.Offset != 0:
                    self.SetPhonebookUpdate('Previous Search', qualifier)
                    self.MinLabel = len(self.newList) - (self._NumberofPhonebookSearch - 1)
                    self.MaxLabel = len(self.newList)
                else:
                    self.MinLabel = 1  # do nothing if already at the begining of the contact list
            if self.MaxLabel < self._NumberofPhonebookSearch:
                self.MaxLabel = self._NumberofPhonebookSearch
            if self.MaxLabel > len(self.newList) and len(
                    self.newList) == self._PhonebookSearchOffset:  # Search Next Set only if contacts are more then self._PhonebookSearchOffset
                self.SetPhonebookUpdate('Next Search', qualifier)

            self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('No Contacts Found.')

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        if 1 <= value <= self._NumberofPhonebookSearch:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': int(value)})
            if number and number != '***End of list***':
                number = number[number.find(' : ') + 3:]
                commandstring = 'xCommand Dial Number:"{0}"\r'.format(number)
                self.Send(commandstring)

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True

        if value == 'Refresh':  # reset contact search to the very begining
            self.Offset = 0
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
        elif value == 'Next Search' and len(self.newList) == self._PhonebookSearchOffset:  # load next set of contacts
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset += self._PhonebookSearchOffset
        elif value == 'Previous Search':  # load previous set of contacts
            self.Offset -= self._PhonebookSearchOffset
        if self.Offset < 0:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset = 0
        self.WriteStatus('PhonebookSearchResult', '***Loading Contacts***', {'Button': 1})
        for index in range(2, int(self._NumberofPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '...', {'Button': index})

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
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
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1}SearchField: Name ContactType: Contact {2} Offset: {3} Limit: {4}\r'.format(
                phonebookType, contact, fldID, self.Offset, self._PhonebookSearchOffset)  # search for all contacts
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')  # ** end\r\n is used for delimiter
            if res:
                res = res.decode()
                self.newList = {}  # Clear Dictionary and repopulate with new search
                nameList = findall(self.dirName, res)
                numberList = findall(self.dirNumber, res)
                for index, name in nameList:
                    self.newList[index] = {'Name': name}

                for index, number in numberList:
                    if index in self.newList:
                        self.newList[index]['Number'] = number
                    else:
                        self.newList[index] = {'Number': number}

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookUpdateHandler')

    def SetPhonebookWriteHandler(self, value, qualifier):
        button = 1
        for index in range(self.MinLabel, self.MaxLabel + 1):  # populate up to max labels configured
            if str(index) in self.newList:
                self.WriteStatus('PhonebookSearchResult', '{0} : {1}'.format(self.newList[str(index)]['Name'], self.newList[str(index)]['Number']), {'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for index in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': index})

    def SetPresentation(self, value, qualifier):

        sendingModeStates = {
            'Not Specified': '',
            'Local Only': ' SendingMode:LocalOnly',
            'Local and Remote': ' SendingMode:LocalRemote'
        }
        instanceState = {
            'Not Specified': '',
            'New': ' Instance:New',
            '1': ' Instance:1',
            '2': ' Instance:2',
            '3': ' Instance:3',
            '4': ' Instance:4',
            '5': ' Instance:5',
            '6': ' Instance:6',
        }
        cmdState = ''
        if 'Stop' == value:
            cmdState = 'xCommand Presentation Stop\r'
        elif 'Start' == value:
            inputSource = qualifier['Video Input Source']
            sendingMode = qualifier['Sending Mode']
            instanceID = qualifier['Instance']
            cmdState = 'xCommand Presentation Start{0}{1}{2}\r'.format(instanceState[instanceID], sendingModeStates[sendingMode], self.InputSourceStates[inputSource])
        if cmdState:
            self.__SetHelper('Presentation', cmdState, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):

        if value:
            cmdstring = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{0}"\r'.format(value)
            self.__SetHelper('PresentationExternalSourceSelectCommand', cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationExternalSourceSelectCommand')

    def UpdatePresentationModeStatus(self, value, qualifier):

        PresentationModeStatusCmdString = 'xStatus Conference Presentation Mode\r'
        self.__UpdateHelper('PresentationModeStatus', PresentationModeStatusCmdString, value, qualifier)

    def __MatchPresentationModeStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresentationModeStatus', value, None)

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        if 1 <= int(qualifier['Instance']) <= 6:
            PresentationSendingModeCmdString = 'xStatus Conference Presentation LocalInstance {0} SendingMode\r'.format(qualifier['Instance'])
            self.__UpdateHelper('PresentationSendingModeStatus', PresentationSendingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        ValueStateValues = {
            'LocalRemote': 'Local and Remote',
            'LocalOnly': 'Local Only',
            'Off': 'Off',
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PresentationSendingModeStatus', value, {'Instance': match.group(1).decode()})

    def __MatchPresentationSendingModeStatusStop(self, match, tag):

        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance': match.group(1).decode()})

    def UpdatePresentationSourceStatus(self, value, qualifier):

        if 1 <= int(qualifier['Instance']) <= 6:
            self.__UpdateHelper('PresentationSourceStatus', 'xStatus Conference Presentation LocalInstance {0} Source\r'.format(qualifier['Instance']), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSourceStatus')

    def __MatchPresentationSourceStatus(self, match, tag):
        value = match.group(2).decode()
        value = 'Stop' if value == '0' else value
        self.WriteStatus('PresentationSourceStatus', value, {'Instance': match.group(1).decode()})

    def __MatchPresentationSourceStatusStop(self, match, tag):

        self.WriteStatus('PresentationSourceStatus', 'Stop', {'Instance': match.group(1).decode()})

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            PresetRecallCmdString = 'xCommand RoomPreset Activate PresetId:{0}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 15:
            PresetSaveCmdString = 'xCommand RoomPreset Store PresetId:{0} Type:All\r'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'xCommand SystemUnit Boot Action:Restart\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetSelfView(self, value, qualifier):

        if value in ['On', 'Off']:
            SelfViewCmdString = 'xCommand Video Selfview Set Mode:{0}\r'.format(value)
            self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfView')

    def UpdateSelfView(self, value, qualifier):

        SelfViewCmdString = 'xStatus Video Selfview Mode\r'
        self.__UpdateHelper('SelfView', SelfViewCmdString, value, qualifier)

    def __MatchSelfView(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SelfView', value, None)

    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        if value in ['On', 'Off', 'Current']:
            SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode:{0}\r'.format(value)
            self.__SetHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfViewDefaultFullscreenMode')

    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):

        SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode\r'
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        value = match.group(1).decode()
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

        SelfViewPositionCmdString = 'xCommand Video Selfview Set PIPPosition:{0}\r'.format(ValueStateValues[value])
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

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SelfViewPosition', value, None)

    def UpdateSIPRegistrationStatus(self, value, qualifier):

        SIPRegistrationStatusCmdString = 'xStatus SIP Registration 1 Status\r'
        self.__UpdateHelper('SIPRegistrationStatus', SIPRegistrationStatusCmdString, value, qualifier)

    def __MatchSIPRegistrationStatus(self, match, tag):

        ValueStateValues = {
            'Deregister': 'Deregistering',
            'Failed': 'Failed',
            'Inactive': 'Inactive',
            'Registered': 'Registered',
            'Registering': 'Registering'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SIPRegistrationStatus', value, None)

    def SetSIPURICommand(self, value, qualifier):

        if value:
            SIPURICommandCmdString = 'xConfiguration SIP URI: {}\r'.format(value)
            self.__SetHelper('SIPURICommand', SIPURICommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSIPURICommand')

    def UpdateSIPURIStatus(self, value, qualifier):

        SIPURIStatusCmdString = 'xConfiguration SIP URI\r'
        self.__UpdateHelper('SIPURIStatus', SIPURIStatusCmdString, value, qualifier)

    def __MatchSIPURIStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SIPURIStatus', value, None)

    def SetSleepTimer(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 480
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SleepTimerCmdString = 'xCommand Standby ResetTimer Delay:{0}\r'.format(value)
            self.__SetHelper('SleepTimer', SleepTimerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTimer')

    def SetSpeakerTrackControl(self, value, qualifier):

        ValueStateValues = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        SpeakerTrackControlCmdString = 'xCommand Cameras SpeakerTrack {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, value, qualifier)

    def UpdateSpeakerTrackControl(self, value, qualifier):

        SpeakerTrackControlCmdString = 'xStatus Cameras SpeakerTrack Status\r'
        self.__UpdateHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, value, qualifier)

    def __MatchSpeakerTrackControl(self, match, tag):

        ValueStateValues = {
            'Active': 'On',
            'Inactive': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SpeakerTrackControl', value, None)

    def SetSpeakerTrackMode(self, value, qualifier):

        if value in ['Auto', 'Off']:
            SpeakerTrackModeCmdString = 'xConfiguration Cameras SpeakerTrack Mode: {0}\r'.format(value)
            self.__SetHelper('SpeakerTrackMode', SpeakerTrackModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerTrackMode')

    def UpdateSpeakerTrackMode(self, value, qualifier):

        SpeakerTrackModeCmdString = 'xConfiguration Cameras SpeakerTrack Mode\r'
        self.__UpdateHelper('SpeakerTrackMode', SpeakerTrackModeCmdString, value, qualifier)

    def __MatchSpeakerTrackMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SpeakerTrackMode', value, None)

    def SetStandby(self, value, qualifier):

        if value in ['Activate', 'Deactivate', 'Halfwake']:
            StandbyCmdString = 'xCommand Standby {0}\r'.format(value)
            self.__SetHelper('Standby', StandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def UpdateStandby(self, value, qualifier):

        StandbyCmdString = 'xStatus Standby State\r'
        self.__UpdateHelper('Standby', StandbyCmdString, value, qualifier)

    def __MatchStandby(self, match, tag):

        ValueStateValues = {
            'Off': 'Deactivate',
            'Standby': 'Activate',
            'Halfwake': 'Halfwake',
            'EnteringStandby': 'Entering Standby',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)

    def UpdateSubnetMask(self, value, qualifier):

        SubnetMaskCmdString = 'xStatus Network 1 IPv4 SubnetMask\r'
        self.__UpdateHelper('SubnetMask', SubnetMaskCmdString, value, qualifier)

    def __MatchSubnetMask(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SubnetMask', value, None)

    def SetSystemUnitNameCommand(self, value, qualifier):

        if value:
            SystemUnitNameCommandCmdString = 'xConfiguration SystemUnit Name: {}\r'.format(value)
            self.__SetHelper('SystemUnitNameCommand', SystemUnitNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSystemUnitNameCommand')

    def UpdateSystemUnitNameStatus(self, value, qualifier):

        SystemUnitNameStatusCmdString = 'xConfiguration SystemUnit Name\r'
        self.__UpdateHelper('SystemUnitNameStatus', SystemUnitNameStatusCmdString, value, qualifier)

    def __MatchSystemUnitNameStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemUnitNameStatus', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'xCommand Audio Volume Set Level:{0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'xStatus Audio Volume\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.tshellerror:
            self.Discard('Inappropriate Command')
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.tshellerror:
            self.Discard('Inappropriate Command ' + command)
        elif self.Unidirectional == 'True':
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
        self.Error([match.group(0).decode().strip()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if self.tshellerror:
            self.tshellerror = False

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def csco_12_3911_non_P(self):

        self.InputMicLevelMax = 26

        self.AudioOutputStates = {
            'Internal Speaker': 'InternalSpeaker',
            'Line': 'Line 1'
        }

        self.AudioOutputValues = {
            'InternalSpeaker': 'Internal Speaker',
            'Line 1': 'Line'
        }

        self.DisplayModeStates = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'Dual Presentation Only': 'DualPresentationOnly'
        }

        self.DisplayModeValues = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'DualPresentationOnly': 'Dual Presentation Only'
        }

        self.InputMicLevelStates = {
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteStates = {
            'Internal Microphone': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteValues = {
            'Microphone 1': 'Internal Microphone',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputSourceStates = {
            'Not Specified': '',
            'Presentation Source 1': ' PresentationSource:1',
            'Presentation Source 2': ' PresentationSource:2',
            'Connector Id 1': ' ConnectorId:1',
            'Connector Id 2': ' ConnectorId:2'
        }

    def csco_12_3911_Plus(self):

        self.InputMicLevelMax = 26

        self.AudioOutputStates = {
            'Internal Speaker': 'InternalSpeaker',
            'Line': 'Line 1'
        }

        self.AudioOutputValues = {
            'InternalSpeaker': 'Internal Speaker',
            'Line 1': 'Line'
        }

        self.DisplayModeStates = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'Dual Presentation Only': 'DualPresentationOnly'
        }

        self.DisplayModeValues = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'DualPresentationOnly': 'Dual Presentation Only'
        }

        self.InputMicLevelStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteStates = {
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteValues = {
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputSourceStates = {
            'Not Specified': '',
            'Presentation Source 1': ' PresentationSource:1',
            'Presentation Source 2': ' PresentationSource:2',
            'Presentation Source 3': ' PresentationSource:3',
            'Connector Id 1': ' ConnectorId:1',
            'Connector Id 2': ' ConnectorId:2',
            'Connector Id 3': ' ConnectorId:3'
        }

    def csco_12_3911_Pro(self):

        self.InputMicLevelMax = 70

        self.AudioOutputStates = {
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
            'Line 3': 'Line 3',
            'Line 4': 'Line 4',
            'Line 5': 'Line 5',
            'Line 6': 'Line 6'
        }

        self.AudioOutputValues = {
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
            'Line 3': 'Line 3',
            'Line 4': 'Line 4',
            'Line 5': 'Line 5',
            'Line 6': 'Line 6'
        }

        self.DisplayModeStates = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'Dual Presentation Only': 'DualPresentationOnly',
            'Triple Presentation Only': 'TriplePresentationOnly',
            'Triple'  				: 'Triple'
        }

        self.DisplayModeValues = {
            'Auto'                  : 'Auto',
            'Dual'                  : 'Dual',
            'Single'                : 'Single',
            'DualPresentationly'  : 'Dual Presentation Only',
            'TriplePresentationOnly': 'Triple Presentation Only',
            'Triple'  				: 'Triple'
        }

        self.InputMicLevelStates = {
            'Microphne 1' : 'Microphone 1',
            'Microphne 2' : 'Microphone 2',
            'Microphne 3' : 'Microphone 3',
            'Microphne 4' : 'Microphone 4',
            'Microphne 5' : 'Microphone 5',
            'Microphne 6' : 'Microphone 6',
            'Microphne 7' : 'Microphone 7',
            'Microphne 8' : 'Microphone 8'
        }

        self.InputMuteStates = {
            'Microphne 1' : 'Microphone 1',
            'Microphne 2' : 'Microphone 2',
            'Microphne 3' : 'Microphone 3',
            'Microphne 4' : 'Microphone 4',
            'Microphne 5' : 'Microphone 5',
            'Microphne 6' : 'Microphone 6',
            'Microphne 7' : 'Microphone 7',
            'Microphne 8' : 'Microphone 8',
            'HDMI 1'       : 'HDMI 1',
            'HDMI 2'       : 'HDMI 2',
            'HDMI 3'       : 'HDMI 3',
            'HDMI 4'       : 'HDMI 4',
            'HDMI 5'       : 'HDMI 5',
        }

        self.InputMuteValues = {
            'Microphne 1' : 'Microphone 1',
            'Microphne 2' : 'Microphone 2',
            'Microphne 3' : 'Microphone 3',
            'Microphne 4' : 'Microphone 4',
            'Microphne 5' : 'Microphone 5',
            'Microphne 6' : 'Microphone 6',
            'Microphne 7' : 'Microphone 7',
            'Microphne 8' : 'Microphone 8',
            'HDMI 1'       : 'HDMI 1',
            'HDMI 2'       : 'HDMI 2',
            'HDMI 3'       : 'HDMI 3',
            'HDMI 4'       : 'HDMI 4',
            'HDMI 5'       : 'HDMI 5',
        }

        self.InputSourceStates = {
            'Not Specified'        : '',
            'Presentation Source 1': ' PresentationSource:1',
            'Presentation Source 2': ' PresentationSource:2',
            'Presentation Source 3': ' PresentationSource:3',
            'Presentation Source 4': ' PresentationSource:4',
            'Presentation Source 5': ' PresentationSource:5',
            'Presentation Source 6': ' PresentationSource:6',
            'Connector Id 1'       : ' ConnectorId:1',
            'Connector Id 2'       : ' ConnectorId:2',
            'Connector Id 3'       : ' ConnectorId:3',
            'Connector Id 4'       : ' ConnectorId:4',
            'Connector Id 5'       : ' ConnectorId:5',
            'Connector Id 6'       : ' ConnectorId:6'
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
