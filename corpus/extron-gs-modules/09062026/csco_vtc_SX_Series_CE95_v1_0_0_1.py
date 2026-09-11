from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import Wait, ProgramLog
import copy

class DeviceClass:

    def __init__(self, Model):

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
        self.Model = Model
        self.Debug = False

        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofPhonebookSearch = 5
        self._NumberofCallHistory = 5
        self._NumberofPhonebookFolderSearch = 5
        self._PhonebookSearchOffset = 50
        self._NumberofPeripheral = 5

        self.deviceUsername = 'admin'
        self.devicePassword = None

        self.Models = {
            'SX10 CE9.5.X' : self.csco_12_4055_SX20_SX10,
            'SX20 CE9.5.X' : self.csco_12_4055_SX20_SX10,
            'SX80 CE9.5.X' : self.csco_12_4055_SX80,
        }
        
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutput': {'Parameters':['Output'], 'Status': {}},
            'AutoAnswer': { 'Status': {}},
            'CallHistory': {'Parameters':['Button','Detail Type'], 'Status': {}},
            'CallHistoryNavigation': { 'Status': {}},
            'CallHistoryRefresh': { 'Status': {}},
            'CallHistorySelect': { 'Status': {}},
            'CallSetupMode': { 'Status': {}},
            'CallStatus': {'Parameters':['Call'], 'Status': {}},
            'CallStatusDeviceType': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters':['Call'], 'Status': {}},
            'CameraFocus': {'Status': {}},
            'CameraPan': {'Status': {}},
            'CameraPresetRecall': { 'Status': {}},
            'CameraPresetSave': {'Status': {}},
            'CameraTilt': {'Status': {}},
            'CameraZoom': {'Status': {}},
            'ConnectedDeviceMAC': {'Parameters':['Button'], 'Status': {}},
            'ConnectedDeviceName': {'Parameters':['Button'], 'Status': {}},
            'ConnectedDeviceNavigation': { 'Status': {}},
            'ConnectedDeviceType': {'Parameters':['Button'], 'Status': {}},
            'ConnectedDeviceUpdate': { 'Status': {}},
            'DisplayMode': { 'Status': {}},
            'DisplayName': {'Parameters':['Call'], 'Status': {}},
            'DNSDomainName': { 'Status': {}},
            'DNSDomainNameCommand': { 'Status': {}},
            'DNSServerAddress': {'Parameters':['Server'], 'Status': {}},
            'DNSServerAddressCommand': { 'Status': {}},
            'DoNotDisturb': { 'Status': {}},
            'DTMF': { 'Status': {}},
            'FarEndCameraPanTilt': { 'Status': {}},
            'FarEndCameraPresetRecall': { 'Status': {}},
            'FarEndCameraSource': { 'Status': {}},
            'FarEndCameraZoom': { 'Status': {}},
            'FarEndControl': { 'Status': {}},
            'FirmwareVersion': { 'Status': {}},
            'GatewayAddress': { 'Status': {}},
            'H323AliasE164Command': { 'Status': {}},
            'H323AliasIDCommand': { 'Status': {}},
            'H323AliasIDStatus': { 'Status': {}},
            'H323GatekeeperAddress': { 'Status': {}},
            'H323GatekeeperAddressCommand': { 'Status': {}},
            'H323GatekeeperStatus': { 'Status': {}},
            'H323ProfileAuthenticationLoginNameCommand': { 'Status': {}},
            'H323ProfileAuthenticationPasswordCommand': { 'Status': {}},
            'Hook': {'Parameters':['Protocol'], 'Status': {}},
            'Input': { 'Status': {}},
            'InputLineLevel': {'Parameters':['Input'], 'Status': {}},
            'InputMicLevel': {'Parameters':['Input'], 'Status': {}},
            'InputMute': {'Parameters':['Input'], 'Status': {}},
            'InputSignal': {'Parameters':['Input'], 'Status': {}},
            'IPAddress': { 'Status': {}},
            'IPv4AddressCommand': { 'Status': {}},
            'IPv4GatewayCommand': { 'Status': {}},
            'IPv4SubnetMaskCommand': { 'Status': {}},
            'IREmulation': {'Parameters':['Key'], 'Status': {}},
            'LayoutSet': {'Parameters':['Target'], 'Status': {}},
            'Macro': { 'Status': {}},
            'MacroAutoStart': { 'Status': {}},
            'MacroMode': { 'Status': {}},
            'RestartMacros': { 'Status': {}},
            'MACAddress': { 'Status': {}},
            'MicrophonesMute': { 'Status': {}},
            'NetworkAssignment': { 'Status': {}},
            'OutputLevel': {'Parameters':['Output'], 'Status': {}},
            'PeopleCountCurrent': { 'Status': {}},
            'PeopleCountOutofCall': { 'Status': {}},
            'PeoplePresence': { 'Status': {}},
            'PeoplePresenceDetector': { 'Status': {}},
            'PhonebookFolderID': { 'Status': {}},
            'PhonebookFolderIDNavigation': { 'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters':['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': { 'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters':['Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters':['Button'], 'Status': {}},
            'PhonebookSearchSet': { 'Status': {}},
            'PhonebookUpdate': {'Parameters':['Phonebook Type'], 'Status': {}},
            'Presentation': { 'Status': {}},
            'PresentationExternalSourceSelectCommand': { 'Status': {}},
            'PresentationModeStatus': { 'Status': {}},
            'PresentationSendingModeStatus': {'Parameters':['Instance'], 'Status': {}},
            'PresentationSourceStatus': {'Parameters': ['Instance'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'Reboot': { 'Status': {}},
            'RemoteNumber': {'Parameters':['Call'], 'Status': {}},
            'SelfView': { 'Status': {}},
            'SelfViewDefaultFullscreenMode': { 'Status': {}},
            'SelfViewPosition': { 'Status': {}},
            'SIPRegistrationStatus': { 'Status': {}},
            'SIPURICommand': { 'Status': {}},
            'SIPURIStatus': { 'Status': {}},
            'SleepTimer': { 'Status': {}},
            'SpeakerTrackControl': { 'Status': {}},
            'SpeakerTrackMode': { 'Status': {}},
            'Standby': { 'Status': {}},
            'SubnetMask': { 'Status': {}},
            'SystemUnitNameCommand': { 'Status': {}},
            'SystemUnitNameStatus': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

        self.startCallHist = 0
        self.NumberOfCallPoll = 50

        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n')
        self.callStatusDeviceTypePattern = compile('\*s Call \d+ DeviceType: (Endpoint|MCU)\r\n')
        self.callStatusTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n')
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "(.*)"\r\n')
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "(.*)"\r\n')
        self.callID = compile('\*s Call (\d+) Status: \w+\r\n')
        self.__CallID = []

        self.HistorydisplayNameList = {}
        self.HistorycallBackNumberList = {}
        self.HistorylastOccurrenceTimeList = {}
        self.HistoryoccurrenceTypeList = {}
        self.HistoryoccurrenceCountList = {}
        self.MinLabel = 1
        self.MaxLabel = 5
        self.Offset = 0
        self.newList = {}
        self.dirName = compile('\*r PhonebookSearchResult Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: "(.+)"')
        self.FolderMin = 1
        self.FolderLimit = 0
        self.folderList = {}
        self.FolderNameRex = compile('\*r PhonebookSearchResult Folder (\d+) Name: "(.+)"\r\n')
        self.FolderIDRex = compile('\*r PhonebookSearchResult Folder (\d+) FolderId: "(.+)"')
        self.MaxDevices = 0
        self.startPeripheral = 0
        self.peripheralName = compile('\*s Peripherals ConnectedDevice \d+ Name: "(.+)"\r\n')
        self.peripheralType = compile('\*s Peripherals ConnectedDevice \d+ Type: (.+)\r\n')
        self.peripheralMAC = compile('\*s Peripherals ConnectedDevice \d+ ID: "(.+)"\r\n')
        
        
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')
        self.occurrenceType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')
        if self._CallHistoryOccurrenceType == 'Time':
             self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
             self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) Count: (\d+)\r\n')

        self.deviceName = None
        self.deviceType = None
        self.deviceID = None
        self.FolderID = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line \d) Mode: (On|Off)\r\n'), self.__MatchAudioOutput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'xstatus call\r\n\*\* end\r\n'), self.__MatchCallStatusIdle, None)
            self.AddMatchString(compile(b'\*s Call (\d+) [\s\S]+\*\* end\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (\w+)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Domain Name: "(.*)"'), self.__MatchDNSDomainName, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-5]) Address: "([0-9.]{0,15})"\r\n'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{0,15})"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{0,15})"\r\n'), self.__MatchH323GatekeeperAddress, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 H323Alias ID: "([\W\w]{0,})"\r\n'), self.__MatchH323AliasIDStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoSource: ([1-6]|Composed)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Line [1-4]) Level: (\d+)\r\n'), self.__MatchInputLineLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros AutoStart: (On|Off)\r\n'), self.__MatchMacroAutoStart, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros Mode: (On|Off)\r\n'), self.__MatchMacroMode, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-8]) Level: (\d+)\r\n'), self.__MatchInputMicLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input ((Microphone|Line) \d) Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Video Input Connector ([1-5]) Connected: (True|False|Unknown)\r\n'), self.__MatchInputSignal, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{0,15})"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Video Layout LayoutFamily (Local|Remote): "(.*?)"\r\n'), self.__MatchLayoutSet, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "([:0-9A-Z]{0,17})"\r\n\*\* end\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n\*\* end\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line [1-6]) Level: (-?\d+)\r\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeopleCount Current: ([-\d]+)\r\n'), self.__MatchPeopleCountCurrent, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/RoomAnalytics/PeopleCount/Current"\r\n'), self.__MatchPeopleCountCurrentOff, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeopleCountOutOfCall: (On|Off)\r\n'), self.__MatchPeopleCountOutofCall, None)
            self.AddMatchString(compile(b'\*r Configuration XPath: "Configuration/RoomAnalytics/PeopleCountOutOfCall"\r\n'), self.__MatchPeopleCountOutofCallOff, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeoplePresence: (Yes|No|Unknown)\r\n'), self.__MatchPeoplePresence, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeoplePresenceDetector: (On|Off)\r\n'), self.__MatchPeoplePresenceDetector, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-5])\r\n'), self.__MatchPresentationSourceStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off|On)\r\n'), self.__MatchPresentationModeStatus, None)
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
            self.AddMatchString(compile(b'version="([\w.]+)" apiVersion'), self.__MatchFirmwareVersion, None)
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
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        self._NumberofPhonebookSearch= int(value)

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
    def PhonebookSearchOffset(self):
        return self._PhonebookSearchOffset

    @PhonebookSearchOffset.setter
    def PhonebookSearchOffset(self, value):
        self._PhonebookSearchOffset= int(value)

    @property
    def NumberofPeripheral(self):
        return self._NumberofPeripheral

    @NumberofPeripheral.setter
    def NumberofPeripheral(self, value):
        self._NumberofPeripheral= int(value)

    def __MatchAuthentication(self, match, tag):
        self.SetAuthentication(None, None)

    def SetAuthentication(self, value, qualifier):
        self.Send(b'\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def __MatchLogin(self, match, qualifier):
        self.SetLogin(None, None)

    def SetLogin(self, value, qualifier):
        self.Send(self.deviceUsername+'\r\n')

    def __MatchPassword(self, match, qualifier):
        self.SetPassword(None, None)
        
    def SetPassword(self, value, qualifier):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAudioOutput(self, value, qualifier):

        AudioOutputStates = {
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            'Line 5'  :   'Line 5',
            'Line 6'  :   'Line 6',
            'HDMI 1'  :   'HDMI 1',
            'HDMI 2'  :   'HDMI 2',
            }

        Output = AudioOutputStates[qualifier['Output']]
        if Output and value in ['On', 'Off']:
            AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode:{1}\r'.format(Output, value)
            self.__SetHelper('AudioOutput', AudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):

        AudioOutputStates = {
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            'Line 5'  :   'Line 5',
            'Line 6'  :   'Line 6',
            'HDMI 1'  :   'HDMI 1',
            'HDMI 2'  :   'HDMI 2',
            }
        Output = AudioOutputStates[qualifier['Output']]
        AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode\r'.format(Output)
        self.__UpdateHelper('AudioOutput', AudioOutputCmdString, qualifier)

    def __MatchAudioOutput(self, match, tag):

        Output = match.group(1).decode()
        self.WriteStatus('AudioOutput', match.group(2).decode(), {'Output':Output})

    def SetAutoAnswer(self, value, qualifier):
        
        ValueStateValues = {
            'On'  : 'On', 
            'Off' : 'Off'
        }
        AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        self.WriteStatus('AutoAnswer', match.group(1).decode(), None)

    def SetCallHistoryRefresh(self, value, qualifier):

        self.startCallHist = 0
        self.NumberOfCallPoll = 50
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        self.Debug = True

        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist, self.NumberOfCallPoll, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CallHistoryCmdString, 5, deliTag=b'** end')
        if res:
            res = res.decode()
            self.HistorydisplayNameList = dict(findall(self.displayName, res))
            self.HistorycallBackNumberList = dict(findall(self.callBackNumber, res))
            self.HistorylastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            self.HistoryoccurrenceTypeList = dict(findall(self.occurrenceType, res))
            self.HistoryoccurrenceCountList = dict(findall(self.occurrenceCount, res))

            button = 1
            for index in range(0, self._NumberofCallHistory):
                if str(index) in self.HistorydisplayNameList:
                    self.WriteStatus('CallHistory', self.HistorydisplayNameList[str(index)], {'Button':str(index+1), 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory', self.HistorycallBackNumberList[str(index)], {'Button':str(index+1), 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory', self.HistorylastOccurrenceTimeList[str(index)], {'Button':str(index+1), 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', self.HistoryoccurrenceTypeList[str(index)], {'Button':str(index+1), 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory', self.HistoryoccurrenceCountList[str(index)], {'Button':str(index+1), 'Detail Type' : 'Occurrence Count'})
                    button += 1
            if button <= self._NumberofCallHistory:
                self.WriteStatus('CallHistory', '***End of list***', {'Button':str(button), 'Detail Type' : 'Display Name'})
                self.WriteStatus('CallHistory', '***End of list***', {'Button':str(button), 'Detail Type' : 'Callback Number'})
                self.WriteStatus('CallHistory', '***End of list***', {'Button':str(button), 'Detail Type' : 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', '***End of list***', {'Button':str(button), 'Detail Type' : 'Occurrence Type'})
                self.WriteStatus('CallHistory', '***End of list***', {'Button':str(button), 'Detail Type' : 'Occurrence Count'})
                for index in range(button+1, self._NumberofCallHistory + 1):
                    self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Display Name'})
                    self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Callback Number'})
                    self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Occurrence Type'})
                    self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Occurrence Count'})
        else:
            self.WriteStatus('CallHistory', '***End of list***', {'Button':'1', 'Detail Type' : 'Display Name'})
            self.WriteStatus('CallHistory', '***End of list***', {'Button':'1', 'Detail Type' : 'Callback Number'})
            self.WriteStatus('CallHistory', '***End of list***', {'Button':'1', 'Detail Type' : 'Last Occurrence Time'})
            self.WriteStatus('CallHistory', '***End of list***', {'Button':'1', 'Detail Type' : 'Occurrence Type'})
            self.WriteStatus('CallHistory', '***End of list***', {'Button':'1', 'Detail Type' : 'Occurrence Count'})
            for index in range(2, self._NumberofCallHistory + 1):
                self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Display Name'})
                self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Callback Number'})
                self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Occurrence Type'})
                self.WriteStatus('CallHistory', '', {'Button':str(index), 'Detail Type' : 'Occurrence Count'})

    def SetCallHistoryNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and len(self.HistorydisplayNameList) > 0:
            if 'Page' in value:
                NumberOfAdvance = self._NumberofCallHistory
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.startCallHist < len(self.HistorydisplayNameList):
                    self.startCallHist += NumberOfAdvance
            elif 'Up' in value:
                self.startCallHist -= NumberOfAdvance

            if self.startCallHist < 1:
                self.startCallHist = 0

            button = 1
            for index in range(self.startCallHist, self.startCallHist + self._NumberofCallHistory):
                if str(index) in self.HistorydisplayNameList:
                    self.WriteStatus('CallHistory', self.HistorydisplayNameList[str(index)],{'Button': str(button), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', self.HistorycallBackNumberList[str(index)],{'Button': str(button), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', self.HistorylastOccurrenceTimeList[str(index)],{'Button': str(button), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', self.HistoryoccurrenceTypeList[str(index)],{'Button': str(button), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', self.HistoryoccurrenceCountList[str(index)],{'Button': str(button), 'Detail Type': 'Occurrence Count'})
                    button += 1
            if button <= self._NumberofCallHistory:
                self.WriteStatus('CallHistory', '***End of list***',{'Button': str(button), 'Detail Type': 'Display Name'})
                self.WriteStatus('CallHistory', '***End of list***',{'Button': str(button), 'Detail Type': 'Callback Number'})
                self.WriteStatus('CallHistory', '***End of list***',{'Button': str(button), 'Detail Type': 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', '***End of list***',{'Button': str(button), 'Detail Type': 'Occurrence Type'})
                self.WriteStatus('CallHistory', '***End of list***',{'Button': str(button), 'Detail Type': 'Occurrence Count'})
                for index in range(button+1, self._NumberofCallHistory + 1):
                    self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', '', {'Button': str(index), 'Detail Type': 'Occurrence Count'})

    def SetCallHistorySelect(self, value, qualifier):

        if 1 <= int(value) <= 20:
            number = self.ReadStatus('CallHistory', {'Button' : value, 'Detail Type': 'Callback Number'})
            if number and number != '***End of list***':
                self.SetHook('Dial', {'Number':number, 'Protocol': 'Auto'})
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')
            
    def SetCallSetupMode(self, value, qualifier):

        ValueStateValues = {
            'Gatekeeper' : 'Gatekeeper', 
            'Direct' : 'Direct'
        }

        CallSetupModeCmdString = 'xConfiguration H323 CallSetup Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CallSetupMode', CallSetupModeCmdString, value, qualifier)
    
    def UpdateCallSetupMode(self, value, qualifier):

        CallSetupModeCmdString = 'xConfiguration H323 CallSetup Mode\r'
        self.__UpdateHelper('CallSetupMode', CallSetupModeCmdString, qualifier)

    def __MatchCallSetupMode(self, match, tag):

        ValueStateValues = {
            'Gatekeeper' : 'Gatekeeper', 
            'Direct' : 'Direct'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CallSetupMode', value, None)

    def UpdateCallStatus(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)

    def UpdateDisplayName(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)

    def UpdateRemoteNumber(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)

    def UpdateCallStatusDeviceType(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)

    def UpdateCallStatusType(self, value, qualifier):
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)

    def __MatchCallStatusIdle(self, match, tag):

        for index in range (1, 6):
            self.WriteStatus('CallStatus', 'Idle', {'Call':str(index)})
            self.WriteStatus('DisplayName', '', {'Call':str(index)})
            self.WriteStatus('RemoteNumber', '', {'Call':str(index)})
            self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call':str(index)})
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
        callstatusDeviceTypeList = findall(self.callStatusDeviceTypePattern, res)
        callStatusTypeList = findall(self.callStatusTypePattern, res)

        index = 0
        for index in range(1, len(callList) + 1, 1):
            self.WriteStatus('CallStatus', callValue[callList[index - 1]], {'Call':str(index)})
            self.WriteStatus('DisplayName', displayNameList[index - 1], {'Call': str(index)})
            self.WriteStatus('RemoteNumber', remoteNumberList[index - 1], {'Call': str(index)})
            self.WriteStatus('CallStatusDeviceType', callstatusDeviceTypeList[index - 1], {'Call': str(index)})
            self.WriteStatus('CallStatusType', callStatusTypeList[index - 1], {'Call': str(index)})
        else:
            index += 1
            while index <= 5:
                self.WriteStatus('CallStatus', 'Idle', {'Call':str(index)})
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(index)})
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
                index += 1

    def SetCameraFocus(self, value, qualifier):

        if self.Model in ['SX10 CE9.5.X', 'SX20 CE9.5.X']:
            self.SetCameraFocusSX20(value, qualifier)
        elif self.Model == 'SX80 CE9.5.X':
            self.SetCameraFocusSX80(value, qualifier)
        else:
            self.Discard('Invalid Model configured.')

    def SetCameraFocusSX80(self, value, qualifier):

        CameraFocusCmdString = ''
        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7:
            if value in ['Far', 'Near', 'Stop']:
                CameraFocusCmdString = 'xCommand Camera Ramp CameraId:{0} Focus:{1}\r'.format(camID, value)
            elif value == 'Auto':
                CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:{0}\r'.format(camID)

            if CameraFocusCmdString:
                self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraFocusSX20(self, value, qualifier):

        CameraFocusCmdString = ''
        if value in ['Far', 'Near', 'Stop']:
            CameraFocusCmdString = 'xCommand Camera Ramp CameraId:1 Focus:{0}\r'.format(value)
        elif value == 'Auto':
            CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:1\r'

        if CameraFocusCmdString:
            self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        if self.Model in ['SX10 CE9.5.X', 'SX20 CE9.5.X']:
            self.SetCameraPanSX20(value, qualifier)
        elif self.Model == 'SX80 CE9.5.X':
            self.SetCameraPanSX80(value, qualifier)
        else:
            self.Discard('Invalid Model configured.')

    def SetCameraPanSX20(self, value, qualifier):

        valueStates = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop',
        }
        CameraPanCmdString = ''
        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan: Stop\r'
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan:{0} PanSpeed:{1}\r'.format(valueStates[value], camSpeed)

            if CameraPanCmdString:
                self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPan')
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPanSX80(self, value, qualifier):

        valueStates = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop',
        }
        CameraPanCmdString = ''
        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan: Stop\r'.format(camID)
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan:{1} PanSpeed:{2}\r'.format(camID,valueStates[value], camSpeed)

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

        if self.Model in ['SX10 CE9.5.X', 'SX20 CE9.5.X']:
            self.SetCameraPresetSaveSX20(value, qualifier)
        elif self.Model == 'SX80 CE9.5.X':
            self.SetCameraPresetSaveSX80(value, qualifier)
        else:
            self.Discard('Invalid Model configured.')

    def SetCameraPresetSaveSX20(self, value, qualifier):

        if 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetSave','xCommand Camera Preset Store PresetId:{0} CameraId:1\r'.format(value),value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraPresetSaveSX80(self, value, qualifier):

        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7 and 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetSave', 'xCommand Camera Preset Store PresetId:{0} CameraId:{1}\r'.format(value, camID), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraTilt(self, value, qualifier):

        if self.Model in ['SX10 CE9.5.X', 'SX20 CE9.5.X']:
            self.SetCameraTiltSX20(value, qualifier)
        elif self.Model == 'SX80 CE9.5.X':
            self.SetCameraTiltSX80(value, qualifier)
        else:
            self.Discard('Invalid Model configured.')

    def SetCameraTiltSX20(self, value, qualifier):

        valueStates = {
            'Up': 'Up',
            'Down': 'Down',
            'Stop': 'Stop',
        }
        CameraTiltCmdString = ''
        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt:Stop\r'
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt:{0} TiltSpeed:{1}\r'.format(valueStates[value],camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraTiltSX80(self, value, qualifier):

        valueStates = {
            'Up': 'Up',
            'Down': 'Down',
            'Stop': 'Stop',
        }
        CameraTiltCmdString = ''
        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt: Stop\r'.format(camID)
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt:{1} TiltSpeed:{2}\r'.format(camID,valueStates[value],camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')


    def SetCameraZoom(self, value, qualifier):

        if self.Model in ['SX10 CE9.5.X', 'SX20 CE9.5.X']:
            self.SetCameraZoomSX20(value, qualifier)
        elif self.Model == 'SX80 CE9.5.X':
            self.SetCameraZoomSX80(value, qualifier)
        else:
            self.Discard('Invalid Model configured.')

    def SetCameraZoomSX20(self, value, qualifier):

        valueStates = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop',
        }
        CameraZoomCmdString = ''
        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom: Stop\r'
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom:{0} ZoomSpeed:{1}\r'.format(valueStates[value],camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetCameraZoomSX80(self, value, qualifier):

        valueStates = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop',
        }
        CameraZoomCmdString = ''
        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom: Stop\r'.format(camID)
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom:{1} ZoomSpeed:{2}\r'.format(camID,valueStates[value], camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetConnectedDeviceUpdate(self, value, qualifier):
        self.Debug = True

        ConnectedDeviceUpdateCmdString = 'xStatus Peripherals ConnectedDevice\r'
        res = self.SendAndWait(ConnectedDeviceUpdateCmdString, 3, deliTag='** end')  # ** end\r\n is used for delimiter
        if res:
            res = res.decode()
            self.deviceName = findall(self.peripheralName, res)
            self.deviceType = findall(self.peripheralType, res)
            self.deviceID = findall(self.peripheralMAC, res)
            self.MaxDevices = len(self.deviceName)

            button = 1
            for index in range(0, self._NumberofPeripheral):
                if index < self.MaxDevices:
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[index], {'Button':index+1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[index], {'Button':index+1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[index], {'Button':index+1})
                    button += 1
            if button <= self._NumberofPeripheral:
                self.WriteStatus('ConnectedDeviceName', '***End of list***', {'Button':button})
                self.WriteStatus('ConnectedDeviceType', '***End of list***', {'Button':button})
                self.WriteStatus('ConnectedDeviceMAC', '***End of list***', {'Button':button})
                button += 1
                for index in range(button, self._NumberofPeripheral +1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button':index})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button':index})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button':index})

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
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[index], {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[index], {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[index], {'Button':button + 1})
                    button += 1

            if button <= self._NumberofPeripheral:  # Show End of list
                self.WriteStatus('ConnectedDeviceName', '***End of list***', {'Button':button + 1})
                self.WriteStatus('ConnectedDeviceType', '***End of list***', {'Button':button + 1})
                self.WriteStatus('ConnectedDeviceMAC', '***End of list***', {'Button':button + 1})
                button += 1
                for i in range(button, self._NumberofPeripheral + 1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button':button + 1})

    def SetDisplayMode(self, value, qualifier):
        
        if self.DisplayModeStatesSet[value]:
            DisplayModeCmdString = 'xConfiguration Video Monitors: {0}\r'.format(self.DisplayModeStatesSet[value].replace(' ', ''))
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):
        self.__UpdateHelper('DisplayMode', 'xConfiguration Video Monitors\r', qualifier)

    def __MatchDisplayMode(self, match, tag):        
        value = self.DisplayModeStatesMatch[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def UpdateDNSDomainName(self, value, qualifier):

        DNSDomainNameCmdString = 'xStatus Network 1 DNS Domain Name\r'
        self.__UpdateHelper('DNSDomainName', DNSDomainNameCmdString, qualifier)

    def __MatchDNSDomainName(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('DNSDomainName', value, None)

    def SetDNSDomainNameCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 DNS Domain Name: {0}\r'.format(value)
            self.__SetHelper('DNSDomainNameCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSDomainNameCommand')

    def UpdateDNSServerAddress(self, value, qualifier):

        server = qualifier['Server']
        if 1 <= int(server) <= 5:
            DNSServerAddressCmdString = 'xStatus Network 1 DNS Server {0} Address\r'.format(server)
            self.__UpdateHelper('DNSServerAddress', DNSServerAddressCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDNSServerAddress')

    def __MatchDNSServerAddress(self, match, tag):

        server = match.group(1).decode()
        value = match.group(2).decode()
        self.WriteStatus('DNSServerAddress', value, {'Server': server})

    def SetDNSServerAddressCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 DNS Server 1 Address: {0}\r'.format(value)
            self.__SetHelper('DNSServerAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def SetDoNotDisturb(self, value, qualifier):

        valueStates = {
            'Active'    :   'Activate',
            'Inactive'  :   'Deactivate',
            }
        DoNotDisturbCmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(valueStates[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):
        self.__UpdateHelper('DoNotDisturb', 'xStatus Conference 1 DoNotDisturb\r', qualifier)

    def __MatchDoNotDisturb(self, match, tag):        
        valueStates = {
            'Active':'Active',
            'Inactive':'Inactive',
            }
        self.WriteStatus('DoNotDisturb', valueStates[match.group(1).decode()], None)

    def SetDTMF(self, value, qualifier):

        DTMFValues = {
            '0'  :   '0',
            '1'  :   '1',
            '2'  :   '2',
            '3'  :   '3',
            '4'  :   '4',
            '5'  :   '5',
            '6'  :   '6',
            '7'  :   '7',
            '8'  :   '8',
            '9'  :   '9',
            '*'  :   '*',
            '#'  :   '#',
            }
        DTMFCmdString = 'xCommand Call DTMFSend DTMFString:{0}\r'.format(DTMFValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetFarEndControl(self, value, qualifier):

        valueStates = {
            'On'   :   'On',
            'Off'  :   'Off'
            }
        FarEndControlCmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(valueStates[value])
        self.__SetHelper('FarEndControl', FarEndControlCmdString, value, qualifier)

    def UpdateFarEndControl(self, value, qualifier):
        self.__UpdateHelper('FarEndControl', 'xConfiguration Conference FarEndControl Mode\r', qualifier)

    def __MatchFarEndControl(self, match, tag):        
        self.WriteStatus('FarEndControl', match.group(1).decode(), None)

    def SetFarEndCameraPanTilt(self, value, qualifier):

        valueStates = {
            'Left'  :   'Left',
            'Right' :   'Right',
            'Up'    :   'Up',
            'Down'  :   'Down',
            }
        if value == 'Stop':
            FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Stop\r'
        else:                        
            FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Move Value:{0}\r'.format(valueStates[value])
        self.__SetHelper('FarEndCameraPanTilt', FarEndCameraPanTiltCmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            FarEndCameraPresetRecallCmdString = 'xCommand Call FarEndControl RoomPreset Activate:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', FarEndCameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraSource(self, value, qualifier):

        if 0 <= int(value) <= 15:
            FarEndCameraSourceRecallCmdString = 'xCommand Call FarEndControl Source Select SourceId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraSource', FarEndCameraSourceRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSource')

    def SetFarEndCameraZoom(self, value, qualifier):

        if value in ['In','Out']:
            self.__SetHelper('FarEndCameraZoom', 'xCommand Call FarEndControl Camera Move Value:Zoom{0}\r'.format(value), value, qualifier)
        elif value == 'Stop':
            self.__SetHelper('FarEndCameraZoom', 'xCommand Call FarEndControl Camera Stop\r', value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraZoom')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'xgetxml /status/standby\r'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetH323AliasE164Command(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 H323Alias E164: {0}\r'.format(value)
            self.__SetHelper('H323AliasE164Command', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasE164Command')

    def SetH323AliasIDCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 H323Alias ID: {0}\r'.format(value)
            self.__SetHelper('H323AliasIDCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasIDCommand')

    def UpdateH323AliasIDStatus(self, value, qualifier):

        H323AliasIDStatusCmdString = 'xConfiguration H323 H323Alias ID\r'
        self.__UpdateHelper('H323AliasIDStatus', H323AliasIDStatusCmdString, qualifier)

    def __MatchH323AliasIDStatus(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('H323AliasIDStatus', value, None)

    def UpdateH323GatekeeperAddress(self, value, qualifier):

        H323GatekeeperAddressCmdString = 'xStatus H323 Gatekeeper Address\r'
        self.__UpdateHelper('H323GatekeeperAddress', H323GatekeeperAddressCmdString, qualifier)

    def __MatchH323GatekeeperAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323GatekeeperAddress', value, None)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 Gatekeeper Address: {0}\r'.format(value)
            self.__SetHelper('H323GatekeeperAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323GatekeeperAddressCommand')

    def UpdateH323GatekeeperStatus(self, value, qualifier):

        H323GatekeeperStatusCmdString = 'xStatus H323 Gatekeeper Status\r'
        self.__UpdateHelper('H323GatekeeperStatus', H323GatekeeperStatusCmdString, qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        ValueStateValues = {
            'Required' : 'Required', 
            'Discovering' : 'Discovering', 
            'Discovered' : 'Discovered', 
            'Authenticating' : 'Authenticating', 
            'Authenticated' : 'Authenticated', 
            'Registering' : 'Registering', 
            'Registered' : 'Registered', 
            'Inactive' : 'Inactive', 
            'Rejected' : 'Rejected'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('H323GatekeeperStatus', value, None)

    def SetH323ProfileAuthenticationLoginNameCommand(self, value, qualifier):

        if value:
            CommandString = 'H323 Authentication LoginName: {0}\r'.format(value)
            self.__SetHelper('H323ProfileAuthenticationLoginNameCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationLoginNameCommand')

    def SetH323ProfileAuthenticationPasswordCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 Authentication Password: {0}\r'.format(value)
            self.__SetHelper('H323ProfileAuthenticationPasswordCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationPasswordCommand')

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320' : 'h320',
            'H323' : 'h323',
            'SIP'  : 'sip',
            'Auto' : 'Auto',
        }

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
        elif value == 'Dial':
            protocol = qualifier['Protocol']
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

    def SetInput(self, value, qualifier):

        if self.InputStates[value]:
            self.__SetHelper('Input', 'xCommand Video Input SetMainVideoSource ConnectorId: {0}\r'.format(self.InputStates[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        self.__UpdateHelper('Input', 'xStatus Video Input MainVideoSource\r', qualifier)

    def __MatchInput(self, match, tag):        
        self.WriteStatus('Input', match.group(1).decode(), None)

    def SetInputLineLevel(self, value, qualifier):

        LineStates = {
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            }

        input_ = LineStates[qualifier['Input']]
        if input_ and 0 <= value <= 24:
            self.__SetHelper('InputLineLevel', 'xConfiguration Audio Input {0} Level:{1}\r'.format(input_, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineLevel')

    def UpdateInputLineLevel(self, value, qualifier):

        LineStates = {
            'Line 1'  :   '1',
            'Line 2'  :   '2',
            'Line 3'  :   '3',
            'Line 4'  :   '4',
            }
        input_ = LineStates[qualifier['Input']]
        if input_:
            self.__UpdateHelper('InputLineLevel', 'xConfiguration Audio Input Line {0} Level\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLineLevel')

    def __MatchInputLineLevel(self, match, tag):        
        input_ = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('InputLineLevel', value, {'Input':input_})

    def SetInputMicLevel(self, value, qualifier):

        input_ = self.MicStates[qualifier['Input']]
        if input_ and 0 <= value <= self.InputLevelMax:
            self.__SetHelper('InputMicLevel', 'xConfiguration Audio Input {0} Level:{1}\r'.format(input_, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLevel')

    def UpdateInputMicLevel(self, value, qualifier):
        input_ = self.MicStates[qualifier['Input']]
        if input_:
            self.__UpdateHelper('InputMicLevel', 'xConfiguration Audio Input {0} Level\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMicLevel')

    def __MatchInputMicLevel(self, match, tag):        
        input_ = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('InputMicLevel', value, {'Input':input_})

    def SetInputMute(self, value, qualifier):

        valueStates = {
            'On'  :   'On',
            'Off'  :   'Off',
        }

        input_ = self.InputMuteStates[qualifier['Input']]
        if input_:
            self.__SetHelper('InputMute', 'xConfiguration Audio Input {0} Mode:{1}\r'.format(input_, valueStates[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):
        input_ = self.InputMuteStates[qualifier['Input']]
        if input_:
            self.__UpdateHelper('InputMute', 'xConfiguration Audio Input {0} Mode\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):        
        input_ = match.group(1).decode()
        self.WriteStatus('InputMute', match.group(3).decode(), {'Input':input_})

    def UpdateInputSignal(self, value, qualifier):

        input_ = self.InputStates[qualifier['Input']]
        if input_:
            self.__UpdateHelper('InputSignal', 'xStatus Video Input Connector {0} Connected\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignal')

    def __MatchInputSignal(self, match, tag):
        input_ = self.InputStates[match.group(1).decode()]
        self.WriteStatus('InputSignal', match.group(2).decode(), {'Input':input_})

    def SetIPv4AddressCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(value)
            self.__SetHelper('IPv4AddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4AddressCommand')

    def SetIPv4GatewayCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(value)
            self.__SetHelper('IPv4GatewayCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4GatewayCommand')

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(value)
            self.__SetHelper('IPv4SubnetMaskCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4SubnetMaskCommand')

    def SetIREmulation(self, value, qualifier):

        KeyStates = {
            'Click' : 'Click', 
            'Press' : 'Press', 
            'Release' : 'Release'
        }

        ValueStateValues = {
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
            'C' : 'C', 
            'Call' : 'Call', 
            'Down' : 'Down', 
            'F1' : 'F1', 
            'F2' : 'F2', 
            'F3' : 'F3', 
            'F4' : 'F4', 
            'F5' : 'F5', 
            'Grab' : 'Grab', 
            'Home' : 'Home', 
            'Layout' : 'Layout', 
            'Left' : 'Left', 
            'Mute' : 'Mute', 
            'Mute Mic' : 'Mute Mic', 
            'Ok' : 'Ok', 
            'PhoneBook' : 'PhoneBook', 
            'Presentation' : 'Presentation', 
            'Right' : 'Right', 
            'Selfview' : 'Selfview', 
            'Square' : 'Square', 
            'Aux' : 'SrcAux', 
            'Camera' : 'SrcCamera', 
            'Doc Cam' : 'SrcDocCam', 
            'Pc' : 'SrcPc', 
            'Vcr' : 'SrcVcr', 
            'Star' : 'Star', 
            'Up' : 'Up', 
            'Volume Down' : 'VolumeDown', 
            'Volume Up' : 'VolumeUp', 
            'Zoom In' : 'ZoomIn', 
            'Zoom Out' : 'ZoomOut',
            'Disconnect'  :   'Disconnect',
            '+'  :   '+',
            '-'  :   '-',
        }

        pressType = KeyStates[qualifier['Key']]
        if pressType:
            IREmulationCmdString = 'xCommand UserInterface OSD Key {0} Key: {1}\r'.format(pressType, ValueStateValues[value])
            self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetLayoutSet(self, value, qualifier):

        if qualifier['Target'] in ['Local', 'Remote'] and value in ['Auto', 'Custom', 'Equal', 'Overlay', 'Prominent', 'Single']:
            LayoutSetCmdString = 'xCommand Video Layout LayoutFamily Set Target: {0} LayoutFamily: {1}\r'.format(qualifier['Target'], value.lower())
            self.__SetHelper('LayoutSet', LayoutSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayoutSet')

    def UpdateLayoutSet(self, value, qualifier):

        if qualifier['Target'] in ['Local', 'Remote']:
            LayoutSetCmdString = 'xStatus Video Layout LayoutFamily {}\r'.format(qualifier['Target'])
            self.__UpdateHelper('LayoutSet', LayoutSetCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateLayoutSet')

    def __MatchLayoutSet(self, match, tag):

        ValueStateValues = {
            'equal' : 'Equal',
            'overlay' : 'Overlay',
            'prominent' : 'Prominent',
            'single' : 'Single'
        }

        qualifier = {'Target': match.group(1).decode()}
        try:
            value = ValueStateValues[match.group(2).decode()]
        except KeyError:
            value = 'Custom'
        self.WriteStatus('LayoutSet', value, qualifier)

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
        self.__UpdateHelper('MacroAutoStart', 'xConfiguration Macros AutoStart\r', qualifier)

    def __MatchMacroAutoStart(self, match, tag):

        self.WriteStatus('MacroAutoStart', match.group(1).decode(), None)

    def SetMacroMode(self, value, qualifier):

        if value in ['On', 'Off']:
            MacroSetCmdString = 'xConfiguration Macros Mode: {}\r'.format(value)
            self.__SetHelper('MacroMode', MacroSetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacroMode')

    def UpdateMacroMode(self, value, qualifier):
        self.__UpdateHelper('MacroMode', 'xConfiguration Macros Mode\r', qualifier)

    def __MatchMacroMode(self, match, tag):

        self.WriteStatus('MacroMode', match.group(1).decode(), None)

    def SetRestartMacros(self, value, qualifier):

        MacroSetCmdString = 'xCommand Macros Runtime Restart\r'.format(value)
        self.__SetHelper('RestartMacros', MacroSetCmdString, value, qualifier)

    def SetMicrophonesMute(self, value, qualifier):

        cmdVal = {
            'On':'Mute',
            'Off':'UnMute',
            }
        MicrophonesMuteCmdString = 'xCommand Audio Microphones {0}\r'.format(cmdVal[value])
        self.__SetHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def UpdateMicrophonesMute(self, value, qualifier):
        self.__UpdateHelper('MicrophonesMute', 'xStatus Audio Microphones Mute\r', qualifier)

    def __MatchMicrophonesMute(self, match, tag):
        self.WriteStatus('MicrophonesMute', match.group(1).decode(), None)

    def SetOutputLevel(self, value, qualifier):

        AudioOutputStates = {
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            'Line 5'  :   'Line 5',
            'Line 6'  :   'Line 6',
            'HDMI 1'  :   'HDMI 1',
            'HDMI 2'  :   'HDMI 2',
            }

        Output = AudioOutputStates[qualifier['Output']]
        if Output and -24 <= value <= 0:
            self.__SetHelper('OutputLevel', 'xConfiguration Audio Output {0} Level:{1}\r'.format(Output, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        AudioOutputStates = {
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            'Line 5'  :   'Line 5',
            'Line 6'  :   'Line 6',
            'HDMI 1'  :   'HDMI 1',
            'HDMI 2'  :   'HDMI 2',
            }

        Output = AudioOutputStates[qualifier['Output']]
        if Output:
            self.__UpdateHelper('OutputLevel', 'xConfiguration Audio Output {0} Level\r'.format(Output), qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):
        
        Output = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('OutputLevel', value, {'Output':Output})

    def UpdatePeopleCountCurrent(self, value, qualifier):

        PeopleCountCurrentCmdString = 'xStatus RoomAnalytics PeopleCount Current\r'
        self.__UpdateHelper('PeopleCountCurrent', PeopleCountCurrentCmdString, qualifier)

    def __MatchPeopleCountCurrent(self, match, tag):

        value = match.group(1).decode()
        if '-' in value:
            value = 'Off'
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
        self.__UpdateHelper('PeopleCountOutofCall', PeopleCountOutofCallCmdString, qualifier)

    def __MatchPeopleCountOutofCall(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PeopleCountOutofCall', value, None)

    def __MatchPeopleCountOutofCallOff(self, match, tag):

        self.WriteStatus('PeopleCountOutofCall', 'Off', None)

    def UpdatePeoplePresence(self, value, qualifier):

        PeoplePresenceCmdString = 'xStatus RoomAnalytics PeoplePresence\r'
        self.__UpdateHelper('PeoplePresence', PeoplePresenceCmdString, qualifier)

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
        self.__UpdateHelper('PeoplePresenceDetector', PeoplePresenceDetectorCmdString, qualifier)

    def __MatchPeoplePresenceDetector(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PeoplePresenceDetector', value, None)

    def SetPhonebookSearchSet(self, value, qualifier):

        if value < 1 or value > self._NumberofPhonebookSearch:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number and 'End of list' not in number:
                number = number[number.find(' : ') + 3:]
                self.SetHook('Dial', {'Number': number, 'Protocol': 'Auto'})

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
            for i in range(self.FolderMin, self.FolderLimit + 1):  # populate up to max labels configured
                if str(i) in self.folderList:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']),{'Button': button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):
        self.Debug = True

        folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
        number = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName]  # read the name and find it within the stored dictionary
        if number:
            self.FolderID = number

    def SetPhonebookFolderIDUpdate(self, value, qualifier):
        self.Debug = True

        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: 50\r'.format(phonebookValue)
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
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']),{'Button': int(i)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate')

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
                if self.MaxLabel > len(self.newList) and len(self.newList) == self._PhonebookSearchOffset:
                    self.SetPhonebookUpdate('Next Search', qualifier)

                self.SetPhonebookWriteHandler(value, qualifier)

    def SetPhonebookUpdate(self, value, qualifier):

        if value == 'Refresh':
            self.Offset = 0
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
        elif value == 'Next Search' and len(self.newList) == self._PhonebookSearchOffset:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset += self._PhonebookSearchOffset
        elif value == 'Previous Search':
            self.Offset -= self._PhonebookSearchOffset
        if self.Offset < 0:
            self.MinLabel = 1
            self.MaxLabel = self._NumberofPhonebookSearch
            self.Offset = 0
        self.WriteStatus('PhonebookSearchResult', '***Loading Contacts***', {'Button': 1})
        for i in range(2, int(self._NumberofPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '...', {'Button': i})

        phonebookType = qualifier['Phonebook Type']
        try:
            contact = qualifier['Contact']
        except (NameError, KeyError):
            contact = ''
        else:
            contact = 'SearchString: "{0}" '.format(contact)
        try:
            folderID = qualifier['FolderID']
        except (NameError, KeyError):
            folderID = ''
        else:
            folderID = 'FolderID: "{0}" '.format(folderID)
        if phonebookType:
            self.PhonebookUpdateHandler(value, {'Contact': contact, 'FolderID': folderID, 'Phonebook Type': phonebookType})
        else:
            self.Discard('Missing parameter: "Phonebook Type"')

    def PhonebookUpdateHandler(self, value, qualifier):
        self.Debug = True

        phonebookType = qualifier['Phonebook Type']
        contact = qualifier['Contact']
        folderID = qualifier['FolderID']
        if phonebookType in ['Corporate', 'Local']:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{} {}SearchField: Name ContactType: Contact {} Offset: {} Limit: {}\r'.format(phonebookType, contact, folderID, self.Offset, self._PhonebookSearchOffset)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
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
            self.Discard('Invalid Phonebook value: {}. Please use "Corporate" or "Local"'.format(phonebookType))

    def SetPhonebookWriteHandler(self, value, qualifier):
        button = 1
        for i in range(self.MinLabel, self.MaxLabel + 1):
            if str(i) in self.newList:
                self.WriteStatus('PhonebookSearchResult', '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']),{'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPresentation(self, value, qualifier):

        inputSourceStates = {
            'Not Specified': '',
            'Presentation Source 1': ' PresentationSource:1',
            'Presentation Source 2': ' PresentationSource:2',
            'Presentation Source 3': ' PresentationSource:3',
            'Presentation Source 4': ' PresentationSource:4',
            'Connector Id 1': ' ConnectorId:1',
            'Connector Id 2': ' ConnectorId:2',
            'Connector Id 3': ' ConnectorId:3',
            'Connector Id 4': ' ConnectorId:4',
            'Connector Id 5': ' ConnectorId:5',
        }
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
            cmdState = 'xCommand Presentation Start{0}{1}{2}\r'.format(instanceState[instanceID],sendingModeStates[sendingMode], inputSourceStates[inputSource])
        if cmdState:
            self.__SetHelper('Presentation', cmdState, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentationSourceStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            self.__UpdateHelper('PresentationSourceStatus', 'xStatus Conference Presentation LocalInstance {0} Source\r'.format(instanceID), qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSourceStatus')

    def __MatchPresentationSourceStatus(self, match, tag):
        instanceID = match.group(1).decode()
        value = match.group(2).decode()
        if value == '0':
            value = 'Stop'
        self.WriteStatus('PresentationSourceStatus', value, {'Instance':instanceID})

    def __MatchPresentationStop(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('PresentationSourceStatus', 'Stop', {'Instance':instanceID})

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):

        if value:
            cmdstring = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{}"\r'.format(value)
            self.__SetHelper('PresentationExternalSourceSelectCommand', cmdstring, value, qualifier)

    def UpdatePresentationModeStatus(self, value, qualifier):

        PresentationModeStatusCmdString = 'xStatus Conference Presentation Mode\r'
        self.__UpdateHelper('PresentationModeStatus', PresentationModeStatusCmdString, qualifier)

    def __MatchPresentationModeStatus(self, match, tag):
        value = match.group(1).decode()
        if value in self.PresetationModeStates:
            self.WriteStatus('PresentationModeStatus', value, None)

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            PresentationSendingModeCmdString = 'xStatus Conference Presentation LocalInstance {0} SendingMode\r'.format(instanceID)
            self.__UpdateHelper('PresentationSendingModeStatus', PresentationSendingModeCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        ValueStateValues = {
            'LocalRemote' : 'Local and Remote', 
            'LocalOnly' : 'Local Only',
            'Off' : 'Off',
        }
        instanceID = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PresentationSendingModeStatus', value, {'Instance':instanceID})

    def __MatchPresentationSendingModeStatusStop(self, match, tag):

        instanceID = match.group(1).decode()
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance':instanceID})

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

        self.__SetHelper('Reboot', 'xCommand SystemUnit Boot Action:Restart\r', value, qualifier)
    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        ValueStateValues = {
            'On'        : 'On', 
            'Off'       : 'Off', 
            'Current'   : 'Current'
        }

        SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)

    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):

        SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode\r'
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SelfViewDefaultFullscreenMode', value, None)

    def SetSelfView(self, value, qualifier):

        if value in ['On', 'Off']:
            self.__SetHelper('SelfView', 'xCommand Video Selfview Set Mode:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfView')

    def UpdateSelfView(self, value, qualifier):

        self.__UpdateHelper('SelfView', 'xStatus Video Selfview Mode\r', qualifier)

    def __MatchSelfView(self, match, tag):        
        self.WriteStatus('SelfView', match.group(1).decode(), None)

    def SetSelfViewPosition(self, value, qualifier):

        ValueStateValues = {
            'Upper Left'    : 'UpperLeft', 
            'Upper Center'  : 'UpperCenter', 
            'Upper Right'   : 'UpperRight', 
            'Center Left'   : 'CenterLeft', 
            'Center Right'  : 'CenterRight', 
            'Lower Left'    : 'LowerLeft', 
            'Lower Right'   : 'LowerRight'
        }

        SelfViewPositionCmdString = 'xCommand Video Selfview Set PIPPosition:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)

    def UpdateSelfViewPosition(self, value, qualifier):

        self.__UpdateHelper('SelfViewPosition', 'xStatus Video Selfview PIPPosition\r', qualifier)

    def __MatchSelfViewPosition(self, match, tag):        

        ValueStateValues = {
            'UpperLeft'    : 'Upper Left', 
            'UpperCenter'  : 'Upper Center', 
            'UpperRight'   : 'Upper Right', 
            'CenterLeft'   : 'Center Left', 
            'CenterRight'  : 'Center Right', 
            'LowerLeft'    : 'Lower Left', 
            'LowerRight'   : 'Lower Right'
        }
        value = match.group(1).decode()
        self.WriteStatus('SelfViewPosition', ValueStateValues[value], None)

    def UpdateSIPRegistrationStatus(self, value, qualifier):

        SIPRegistrationStatusCmdString = 'xStatus SIP Registration 1 Status\r'
        self.__UpdateHelper('SIPRegistrationStatus', SIPRegistrationStatusCmdString, qualifier)

    def __MatchSIPRegistrationStatus(self, match, tag):

        ValueStateValues = {
            'Deregister' : 'Deregistering', 
            'Failed' : 'Failed', 
            'Inactive' : 'Inactive', 
            'Registered' : 'Registered', 
            'Registering' : 'Registering'
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
        self.__UpdateHelper('SIPURIStatus', SIPURIStatusCmdString, qualifier)

    def __MatchSIPURIStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SIPURIStatus', value, None)

    def SetSleepTimer(self, value, qualifier):

        if 1 <= value <= 480:
            self.__SetHelper('SleepTimer', 'xCommand Standby ResetTimer Delay:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTimer')

    def SetStandby(self, value, qualifier):

        stateValues = {
            'Activate' : 'Activate',
            'Deactivate' : 'Deactivate',
            'Half Wake': 'Halfwake'
        }

        StandbyCmdString = 'xCommand Standby {0}\r'.format(stateValues[value])
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):

        self.__UpdateHelper('Standby', 'xStatus Standby State\r', qualifier)

    def __MatchStandby(self, match, tag):
        ValueStateValues = {
            'Off':'Deactivate',
            'Standby':'Activate',
            'EnteringStandby':'Entering Standby',
            'Halfwake':'Half Wake',
            }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)

    def SetSystemUnitNameCommand(self, value, qualifier):

        if value:
            SystemUnitNameCommandCmdString = 'xConfiguration SystemUnit Name: {}\r'.format(value)
            self.__SetHelper('SystemUnitNameCommand', SystemUnitNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSystemUnitNameCommand')

    def UpdateSystemUnitNameStatus(self, value, qualifier):

        SystemUnitNameStatusCmdString = 'xConfiguration SystemUnit Name\r'
        self.__UpdateHelper('SystemUnitNameStatus', SystemUnitNameStatusCmdString, qualifier)

    def __MatchSystemUnitNameStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SystemUnitNameStatus', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'xCommand Audio Volume Set Level:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'xStatus Audio Volume\r', qualifier)

    def __MatchVolume(self, match, tag):
        cmdValue = int(match.group(1))
        self.WriteStatus('Volume', cmdValue, None)

    def UpdateGatewayAddress(self, value, qualifier):

        GatewayAddressCmdString = 'xStatus Network 1 IPv4 Gateway\r'
        self.__UpdateHelper('GatewayAddress', GatewayAddressCmdString, qualifier)

    def __MatchGatewayAddress(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('GatewayAddress', value, None)

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = 'xStatus Network 1 IPv4 Address\r'
        self.__UpdateHelper('IPAddress', IPAddressCmdString, qualifier)

    def __MatchIPAddress(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('IPAddress', value, None)

    def UpdateMACAddress(self, value, qualifier):

        MACAddressCmdString = 'xStatus Network 1 Ethernet MacAddress\r'
        self.__UpdateHelper('MACAddress', MACAddressCmdString, qualifier)

    def __MatchMACAddress(self, match, tag):        
        value = match.group(1).decode()
        self.WriteStatus('MACAddress', value, None)

    def UpdateNetworkAssignment(self, value, qualifier):

        NetworkAssignmentCmdString = 'xConfiguration Network 1 IPv4 Assignment\r'
        self.__UpdateHelper('NetworkAssignment', NetworkAssignmentCmdString, qualifier)

    def __MatchNetworkAssignment(self, match, tag):

        ValueStateValues = {
            'Static' : 'Static', 
            'DHCP' : 'DHCP'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('NetworkAssignment', value, None)

    def SetSpeakerTrackControl(self, value, qualifier):

        ValueStateValues = {
            'On'  : 'Activate', 
            'Off' : 'Deactivate'
        }

        SpeakerTrackControlCmdString = 'xCommand Cameras SpeakerTrack {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, value, qualifier)

    def UpdateSpeakerTrackControl(self, value, qualifier):

        SpeakerTrackControlCmdString = 'xStatus Cameras SpeakerTrack Status\r'
        self.__UpdateHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, qualifier)

    def __MatchSpeakerTrackControl(self, match, tag):
        ValueStateValues = {
            'Active'    : 'On', 
            'Inactive'  : 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SpeakerTrackControl', value, None)

    def SetSpeakerTrackMode(self, value, qualifier):

        ValueStateValues = {
            'Auto'  : 'Auto', 
            'Off'   : 'Off'
        }

        SpeakerTrackModeCmdString = 'xConfiguration Cameras SpeakerTrack Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SpeakerTrackMode', SpeakerTrackModeCmdString, value, qualifier)
        
    def UpdateSpeakerTrackMode(self, value, qualifier):

        SpeakerTrackModeCmdString = 'xConfiguration Cameras SpeakerTrack Mode\r'
        self.__UpdateHelper('SpeakerTrackMode', SpeakerTrackModeCmdString, qualifier)
        
    def __MatchSpeakerTrackMode(self, match, tag):
        ValueStateValues = {
            'Auto'    : 'Auto', 
            'Off'  : 'Off'
        }
        
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('SpeakerTrackMode', value, None)

    def UpdateSubnetMask(self, value, qualifier):

        SubnetMaskCmdString = 'xStatus Network 1 IPv4 SubnetMask\r'
        self.__UpdateHelper('SubnetMask', SubnetMaskCmdString, qualifier)

    def __MatchSubnetMask(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('SubnetMask', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, qualifier):

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

    def csco_12_4055_SX20_SX10(self):

        self.InputLevelMax = 24
        self.ConnectorIDMax = 2

        self.PresetationModeStates = ['On','Off']
        
        self.DisplayModeStatesSet = {
            'Auto'  :   'Auto',
            'Single':   'Single',
            'Dual'  :   'Dual',
            'Dual Presentation Only'  :   'DualPresentationOnly',
            }
        
        self.DisplayModeStatesMatch = {
            'Auto'  :   'Auto',
            'Single':   'Single',
            'Dual'  :   'Dual',
            'DualPresentationOnly'  :   'Dual Presentation Only',
            }

        self.InputStates = {
            '1'  :   '1',
            '2'  :   '2',
            '3'  :   '3',
            'Composed'  :   'Composed',
            }

        self.MicStates = {
            'Microphone 1'  :   'Microphone 1',
            'Microphone 2'  :   'Microphone 2', 
        }

        self.InputMuteStates = {
            'Microphone 1'  :   'Microphone 1',
            'Microphone 2'  :   'Microphone 2',
            }
        
        self.PresentationStates = {
            '1'  :   '1',
            '2'  :   '2',
            'Stop'  :   'Stop',
            }

    def csco_12_4055_SX80(self):

        self.InputLevelMax = 70
        self.ConnectorIDMax = 5

        self.PresetationModeStates = ['Sending','Receiving','Off']

        self.DisplayModeStatesSet = {
            'Auto'  :   'Auto',
            'Single'  :   'Single',
            'Dual'  :   'Dual',
            'Dual Presentation Only'  :   'DualPresentationOnly',
            'Triple Presentation Only'  :   'TriplePresentationOnly',
            'Triple'  :   'Triple',
            }
        
        self.DisplayModeStatesMatch = {
            'Auto'  :   'Auto',
            'Single'  :   'Single',
            'Dual'  :   'Dual',
            'DualPresentationOnly'  :   'Dual Presentation Only',
            'TriplePresentationOnly'  :   'Triple Presentation Only',
            'Triple'  :   'Triple',
            }

        self.InputStates = {
            '1'  :   '1',
            '2'  :   '2',
            '3'  :   '3',
            '4'  :   '4',
            '5'  :   '5',
            '6'  :   '6',
            'Composed'  :   'Composed',
            }

        self.MicStates = {
            'Microphone 1'  :   'Microphone 1',
            'Microphone 2'  :   'Microphone 2',
            'Microphone 3'  :   'Microphone 3',
            'Microphone 4'  :   'Microphone 4',
            'Microphone 5'  :   'Microphone 5',
            'Microphone 6'  :   'Microphone 6',
            'Microphone 7'  :   'Microphone 7',
            'Microphone 8'  :   'Microphone 8',
            }

        self.InputMuteStates = {
            'Microphone 1'  :   'Microphone 1',
            'Microphone 2'  :   'Microphone 2',
            'Microphone 3'  :   'Microphone 3',
            'Microphone 4'  :   'Microphone 4',
            'Microphone 5'  :   'Microphone 5',
            'Microphone 6'  :   'Microphone 6',
            'Microphone 7'  :   'Microphone 7',
            'Microphone 8'  :   'Microphone 8',
            'Line 1'  :   'Line 1',
            'Line 2'  :   'Line 2',
            'Line 3'  :   'Line 3',
            'Line 4'  :   'Line 4',
            }
        
        self.PresentationStates = {
            '1'     :   '1',
            '2'     :   '2',
            '3'     :   '3',
            '4'     :   '4',
            '5'     :   '5',
            'Stop'  :   'Stop',
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
        tempCompileList = copy.copy(self.__matchStringDict)

        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in tempCompileList.items():
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
        DeviceClass.__init__(self, Model)
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
        
        
class SSHClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None), Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort, Credentials)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self, Model)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self, Model)
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