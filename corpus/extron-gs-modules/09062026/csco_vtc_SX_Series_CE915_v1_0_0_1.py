from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict

import time
from datetime import datetime, timedelta, timezone

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
        self._NumberofPhonebookSearch = 5
        self._NumberofCallHistory = 5
        self._NumberofPhonebookFolderSearch = 5
        self._PhonebookSearchOffset = 50
        self._NumberofPeripheral = 5

        self.Models = {
            'SX10 CE9.15.X': self.csco_12_5454_SX10,
            'SX20 CE9.15.X': self.csco_12_5454_SX20,
            'SX80 CE9.15.X': self.csco_12_5454_SX80,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutput': {'Parameters': ['Output'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallAuthenticationRequestStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallAuthenticationResponseCommand': {'Parameters': ['Call', 'Participant Role', 'Pin'], 'Status': {}},
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
            'H323AliasE164Status': {'Status': {}},
            'H323AliasIDCommand': {'Status': {}},
            'H323AliasIDStatus': {'Status': {}},
            'H323GatekeeperAddress': {'Status': {}},
            'H323GatekeeperAddressCommand': {'Status': {}},
            'H323GatekeeperStatus': {'Status': {}},
            'H323ProfileAuthenticationLoginNameCommand': {'Status': {}},
            'H323ProfileAuthenticationPasswordCommand': {'Status': {}},
            'Hook': {'Parameters': ['Protocol', 'Number'], 'Status': {}},
            'Input': {'Status': {}},
            'InputHDMILevel': {'Parameters': ['Input'], 'Status': {}},
            'InputLineLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMicLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputSignal': {'Parameters': ['Input'], 'Status': {}},
            'InputVideoMute': {'Status': {}},
            'IPAddress': {'Status': {}},
            'IPv4AddressCommand': {'Status': {}},
            'IPv4GatewayCommand': {'Status': {}},
            'IPv4SubnetMaskCommand': {'Status': {}},
            'IREmulation': {'Parameters': ['Key'], 'Status': {}},
            'LayoutSet': {'Parameters': ['Target'], 'Status': {}},
            'Macro': {'Status': {}},
            'MacroAutoStart': {'Status': {}},
            'MacroMode': {'Status': {}},
            'RestartMacros': {'Status': {}},
            'MeetingAgenda': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingDialMode': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingDialNumber': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingEndTime': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingJoin': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingOrganizer': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingRefresh': {'Status': {}},
            'MeetingStartTime': {'Parameters': ['Meeting'], 'Status': {}},
            'MeetingTitle': {'Parameters': ['Meeting'], 'Status': {}},
            'MACAddress': {'Status': {}},
            'MicrophonesMute': {'Status': {}},
            'NetworkAssignment': {'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
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
            'PresenterTrackControl': {'Status': {}},
            'PresenterTrackMode': {'Status': {}},
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
            'SystemTimeStatus': {'Parameters': ['Type'], 'Status': {}},
            'SystemUnitNameCommand': {'Status': {}},
            'SystemUnitNameStatus': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.tshellerror = False
        self.phonebook_qualifier = {}
        self.callStatusData = OrderedDict()
        self.callEndPattern = compile('\*s Call (\d+) \(ghost=True\):\r\n')
        self.callIDPattern = compile('\*s Call (\d+) Status: [\S ]+?\r\n')
        self.callStatusPattern = compile('\*s Call \d+ Status: ([\S ]+?)\r\n')
        self.callTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n')
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "([\S ]+?)"\r\n')
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "([\S ]+?)"\r\n')
        self.deviceTypePattern = compile('\*s Call \d+ DeviceType: (Endpoint|MCU)\r\n')
        self.dirName = compile('\*r PhonebookSearchResult Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: "(.+)"\r\n')
        self.FolderNameRex = compile('\*r PhonebookSearchResult Folder (\d+) Name: "(.+)"\r\n')
        self.FolderIDRex = compile('\*r PhonebookSearchResult Folder (\d+) FolderId: "(.+)"\r\n')
        self.peripheralName = compile('\*s Peripherals ConnectedDevice \d+ Name: "(.+)"\r\n')
        self.peripheralType = compile('\*s Peripherals ConnectedDevice \d+ Type: (.+)\r\n')
        self.peripheralMAC = compile('\*s Peripherals ConnectedDevice \d+ ID: "(.+)"\r\n')
        self.MeetingID = compile('\*r BookingsListResult Booking (\d+) Id: "([\S ]+?)"\r\n')
        self.Title = compile('\*r BookingsListResult Booking (\d+) Title: "([\S ]+?)"\r\n')
        self.Agenda = compile('\*r BookingsListResult Booking (\d+) Agenda: "([\S ]+?)"\r\n')
        self.FirstName = compile('\*r BookingsListResult Booking (\d+) Organizer FirstName: "([\S ]+?)"\r\n')
        self.LastName = compile('\*r BookingsListResult Booking (\d+) Organizer LastName: "([\S ]+?)"\r\n')
        self.StartTime = compile('\*r BookingsListResult Booking (\d+) Time StartTime: "(\d+-\d+-\d+T\d+:\d+:\d+Z)"\r\n')
        self.EndTime = compile('\*r BookingsListResult Booking (\d+) Time EndTime: "(\d+-\d+-\d+T\d+:\d+:\d+Z)"\r\n')
        self.DialNumber = compile('\*r BookingsListResult Booking (\d+) DialInfo Calls Call 1 Number: "([\S ]+?)"\r\n')
        self.DialMode = compile('\*r BookingsListResult Booking (\d+) DialInfo ConnectMode: (OBTP|Manual)\r\n')
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')
        self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
        self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        self.occurrenceType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line [1-6]|HDMI [1-2]) Mode: (On|Off)\r\n'), self.__MatchAudioOutput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*s Conference Call (\d+) AuthenticationRequest: (None|HostPinOrGuest|HostPinOrGuestPin|PanelistPin)\r\n'), self.__MatchCallAuthenticationRequestStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'xstatus call\r\n\*\* end\r\n'), self.__MatchCallStatusIdle, None)
            self.AddMatchString(compile(b'\*s Call \d+ [\s\S]+\*\* end\r\n'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (Auto|Dual|Single|DualPresentationOnly|TriplePresentationOnly|Triple)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Domain Name: "([^\r\n]+)?"\r\n'), self.__MatchDNSDomainName, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-5]) Address: "([^\r\n]+)?"\r\n'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'version="([\w.]+)" apiVersion'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([^\r\n]+)?"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([^\r\n]+)?"\r\n'), self.__MatchH323GatekeeperAddress, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 H323Alias E164: "([^\r\n]+)?"\r\n'), self.__MatchH323AliasE164Status, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 H323Alias ID: "([^\r\n]+)?"\r\n'), self.__MatchH323AliasIDStatus, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoSource: ([1-6]|Composed)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (HDMI [1-3]) Level: (-?\d+)\r\n'), self.__MatchInputHDMILevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Line [1-4]) Level: (\d+)\r\n'), self.__MatchInputLineLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros AutoStart: (On|Off)\r\n'), self.__MatchMacroAutoStart, None)
            self.AddMatchString(compile(b'\*c xConfiguration Macros Mode: (On|Off)\r\n'), self.__MatchMacroMode, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-8]) Level: (\d+)\r\n'), self.__MatchInputMicLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-8]|Line [1-4]|HDMI [1-3]) Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Video Input Connector ([1-5]) Connected: (True|False|Unknown)\r\n'), self.__MatchInputSignal, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoMute: (On|Off)\r\n'), self.__MatchInputVideoMute, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([^\r\n]+)?"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Video Layout LayoutFamily (Local|Remote): "(.*?)"\r\n'), self.__MatchLayoutSet, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "([:0-9A-Z]{0,17})"\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line [1-6]|HDMI [1-2]) Level: (-?\d+)\r\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeopleCount Current: ([-\d]+)\r\n'), self.__MatchPeopleCountCurrent, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/RoomAnalytics/PeopleCount/Current"\r\n'), self.__MatchPeopleCountCurrentOff, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeopleCountOutOfCall: (On|Off)\r\n'), self.__MatchPeopleCountOutofCall, None)
            self.AddMatchString(compile(b'\*r Configuration XPath: "Configuration/RoomAnalytics/PeopleCountOutOfCall"\r\n'), self.__MatchPeopleCountOutofCallOff, None)
            self.AddMatchString(compile(b'\*s RoomAnalytics PeoplePresence: (Yes|No|Unknown)\r\n'), self.__MatchPeoplePresence, None)
            self.AddMatchString(compile(b'\*c xConfiguration RoomAnalytics PeoplePresenceDetector: (On|Off)\r\n'), self.__MatchPeoplePresenceDetector, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-4])\r\n'), self.__MatchPresentationSourceStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationSourceStatusOff, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationModeStatus, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusOff, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) \(ghost=True\):\r\n'), self.__MatchPresentationStop, None)  # unsolicited response
            self.AddMatchString(compile(b'\*c xConfiguration Cameras PresenterTrack Enabled: (True|False)\r\n'), self.__MatchPresenterTrackControl, None)
            self.AddMatchString(compile(b'\*r Configuration XPath: "Configuration/Cameras/PresenterTrack/Enabled"\r\n'), self.__MatchPresenterTrackControlOff, None)
            self.AddMatchString(compile(b'\*s Cameras PresenterTrack Status: (Off|Follow|Diagnostic|Background|Setup|Persistent)s?\r\n'), self.__MatchPresenterTrackMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Selfview Default FullscreenMode: (Off|On|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (UpperLeft|UpperCenter|UpperRight|CenterLeft|CenterRight|LowerLeft|LowerRight)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s SIP Registration 1 Status: (Deregister|Failed|Inactive|Registered|Registering)\r\n'), self.__MatchSIPRegistrationStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration SIP URI: "([^\r\n]+)?"\r\n'), self.__MatchSIPURIStatus, None)
            self.AddMatchString(compile(b'\*s Cameras SpeakerTrack Status: (Active|Inactive)\r\n'), self.__MatchSpeakerTrackControl, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|EnteringStandby|Halfwake|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'\*c xConfiguration Cameras SpeakerTrack Mode: (Auto|Off)\r\n'), self.__MatchSpeakerTrackMode, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([^\r\n]+)?"\r\n'), self.__MatchSubnetMask, None)
            self.AddMatchString(compile(b'\*s Time SystemTime: "([^\r\n]+)?"\r\n'), self.__MatchSystemTimeStatus, None)
            self.AddMatchString(compile(b'\*c xConfiguration SystemUnit Name: "([^\r\n]+)?"\r\n'), self.__MatchSystemUnitNameStatus, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchVolume, None)
            if 'Serial' in self.ConnectionType:
                self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            if self.ConnectionType == 'Ethernet':
                self.AddMatchString(compile(b'tshell: Failed to connect to system software\r\n'), self.__MatchTSHell, None)

        self.phonebook = LoadingScroller([], self._NumberofPhonebookSearch, self._PhonebookSearchOffset, self.__UpdatePhonebookHelper, end='*** End of list ***')
        self.phonebook_folder_id = Scroller([], self._NumberofPhonebookFolderSearch, end='*** End of list ***')
        self.connected_device = Scroller([], self._NumberofPeripheral, end='*** End of list ***')
        self.call_history = LoadingScroller([], self._NumberofCallHistory, 50, self.__UpdateCallHistoryHelper, end='*** End of list ***')

    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):
        self._CallHistoryOccurrenceType = value
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

        if qualifier['Output'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', 'HDMI 1', 'HDMI 2'] and value in ['On', 'Off']:
            AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode:{1}\r'.format(qualifier['Output'], value)
            self.__SetHelper('AudioOutput', AudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):
        if qualifier['Output'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', 'HDMI 1', 'HDMI 2']:
            AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode\r'.format(qualifier['Output'])
            self.__UpdateHelper('AudioOutput', AudioOutputCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioOutput')

    def __MatchAudioOutput(self, match, tag):
        Output = match.group(1).decode()
        self.WriteStatus('AudioOutput', match.group(2).decode(), {'Output': Output})

    def SetAutoAnswer(self, value, qualifier):

        if value in ['On', 'Off']:
            AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(value)
            self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):
        AutoAnswerCmdString = 'xConfiguration Conference AutoAnswer Mode\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, qualifier)

    def __MatchAutoAnswer(self, match, tag):
        self.WriteStatus('AutoAnswer', match.group(1).decode(), None)

    def UpdateCallAuthenticationRequestStatus(self, value, qualifier):

        call = int(qualifier['Call'])
        if 1 <= call <= 5:
            self.Send('xFeedback register /Status/Conference/Call\r') # send subscription
            try: # if in a call
                CallAuthenticationRequestStatusCmdString = 'xStatus Conference Call {} AuthenticationRequest\r'.format(list(self.callStatusData.keys())[call-1]) # get call ID from self.callStatusData
                self.__UpdateHelper('CallAuthenticationRequestStatus', CallAuthenticationRequestStatusCmdString, value, qualifier) # send query for initial status
            except IndexError: # if not in a call
                self.WriteStatus('CallAuthenticationRequestStatus', 'None', qualifier) # default to 'None'
        else:
            self.Discard('Invalid Command for UpdateCallAuthenticationRequestStatus')

    def __MatchCallAuthenticationRequestStatus(self, match, tag):

        ValueStateValues = {
            'None'              : 'None',
            'HostPinOrGuest'    : 'Host Pin or Guest',
            'HostPinOrGuestPin' : 'Host Pin or Guest Pin',
            'PanelistPin'       : 'Panelist Pin'
        }

        try:
            qualifier = {'Call': str(list(self.callStatusData.keys()).index(match.group(1).decode())+1)}
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('CallAuthenticationRequestStatus', value, qualifier)
        except ValueError:
            pass

    def SetCallAuthenticationResponseCommand(self, value, qualifier):

        call = qualifier['Call']
        pRole = qualifier['Participant Role']
        pin = qualifier['Pin']
        if (call == 'Not Specified' or 1 <= int(call) <= 5) and pRole in ['Cohost', 'Host', 'Panelist', 'Guest', 'Presenter'] and (pin is None or 0 <= len(pin) <= 32):
            if call == 'Not Specified':
                callID = ''
            else:
                try:
                    callID = ' CallId: {}'.format(list(self.callStatusData.keys())[int(call) - 1])
                except IndexError:
                    return self.Discard('Invalid Command for SetCallAuthenticationResponseCommand')
            pin = '' if not pin else ' Pin: {}'.format(pin)
            CallAuthenticationResponseCommandCmdString = 'xCommand Conference Call AuthenticationResponse{} ParticipantRole: {}{}\r'.format(callID, pRole, pin)
            self.__SetHelper('CallAuthenticationResponseCommand', CallAuthenticationResponseCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallAuthenticationResponseCommand')

    def SetCallHistoryRefresh(self, value, qualifier):
        self.Debug = True
        self.call_history.clear()
        self.call_history.load()
        self.SetCallHistoryWriteHandler(value, qualifier)

    def __UpdateCallHistoryHelper(self, offset, size):
        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {} Limit: {} Order: Occurrence{}\r'.format(offset, size, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CallHistoryCmdString, 5, deliTag=b'** end')
        if res:
            display_names = dict(findall(self.displayName, res.decode()))
            callback_numbers = dict(findall(self.callBackNumber, res.decode()))
            occurence_times = dict(findall(self.lastOccurrenceTime, res.decode()))
            occurence_counts = dict(findall(self.occurrenceCount, res.decode()))
            occurence_types = dict(findall(self.occurrenceType, res.decode()))

            to_add = OrderedDict()

            for index in range(0, len(display_names)):
                to_add[index] = (display_names[str(index)],
                                 callback_numbers[str(index)],
                                 occurence_times[str(index)],
                                 occurence_counts[str(index)],
                                 occurence_types[str(index)])

            return to_add.values(), len(to_add) < size
        return [], False

    def SetCallHistoryNavigation(self, value, qualifier):
        self.Debug = True
        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.call_history.all_size > 0:
            if value == 'Up':
                self.call_history.previous()
            elif value == 'Down':
                self.call_history.next()
            elif value == 'Page Up':
                self.call_history.previous_page()
            elif value == 'Page Down':
                self.call_history.next_page()

            self.SetCallHistoryWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistoryWriteHandler(self, value, qualifier):
        for i in zip(range(1, self.call_history.window + 1), self.call_history.view()):
            if i[1] not in [self.call_history.end, self.call_history.fill]:
                self.WriteStatus('CallHistory', i[1][0], {'Button': str(i[0]), 'Detail Type': 'Display Name'})
                self.WriteStatus('CallHistory', i[1][1], {'Button': str(i[0]), 'Detail Type': 'Callback Number'})
                self.WriteStatus('CallHistory', i[1][2], {'Button': str(i[0]), 'Detail Type': 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', i[1][3], {'Button': str(i[0]), 'Detail Type': 'Occurrence Count'})
                self.WriteStatus('CallHistory', i[1][4], {'Button': str(i[0]), 'Detail Type': 'Occurrence Type'})
            else:
                self.WriteStatus('CallHistory', i[1], {'Button': str(i[0]), 'Detail Type': 'Display Name'})
                self.WriteStatus('CallHistory', i[1], {'Button': str(i[0]), 'Detail Type': 'Callback Number'})
                self.WriteStatus('CallHistory', i[1], {'Button': str(i[0]), 'Detail Type': 'Last Occurrence Time'})
                self.WriteStatus('CallHistory', i[1], {'Button': str(i[0]), 'Detail Type': 'Occurrence Count'})
                self.WriteStatus('CallHistory', i[1], {'Button': str(i[0]), 'Detail Type': 'Occurrence Type'})

    def SetCallHistorySelect(self, value, qualifier):

        if 1 <= int(value) <= self.call_history.window:
            number = self.ReadStatus('CallHistory', {'Button': value, 'Detail Type': 'Callback Number'})
            if number and number not in [self.call_history.end, self.call_history.fill]:
                self.SetHook('Dial', {'Protocol': 'Auto', 'Number': number})
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
        self.__UpdateHelper('CallSetupMode', CallSetupModeCmdString, qualifier)

    def __MatchCallSetupMode(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('CallSetupMode', value, None)

    def UpdateCallStatus(self, value, qualifier):
        self.Send('xFeedback register /Status/Call\r')
        self.__UpdateHelper('CallStatus', 'xstatus call\r', qualifier)           

    def __MatchCallStatusIdle(self, match, tag):

        self.callStatusData.clear() 
        for index in range(1, 6):
            self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
            self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
            self.WriteStatus('DisplayName', '', {'Call': str(index)})
            self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
            self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(index)})

    def __MatchCallStatus(self, match, tag):

        callStatusStates = {
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

        typeStates = {
            'Video': 'Video',
            'Audio': 'Audio',
            'AudioCanEscalate': 'Audio Can Escalate',
            'ForwardAllCall': 'Forward All Call'
        }

        res = match.group(0).decode()
        if ' Status: ' in res or ' CallType: ' in res or ' DisplayName: ' in res or ' RemoteNumber: ' in res or ' DeviceType: ' in res or ' (ghost=True):' in res:  # only update status if useful to driver
            callEndIDList = findall(self.callEndPattern, res)
            if callEndIDList:  # if any calls have ended
                for index, callID in enumerate(callEndIDList):
                    if callEndIDList[index] in self.callStatusData:  # if call ID in self.callStatusData
                        del self.callStatusData[callID]  # remove it
            else:
                callIDList = findall(self.callIDPattern, res)
                callStatusList = findall(self.callStatusPattern, res)
                callTypeList = findall(self.callTypePattern, res)
                displayNameList = findall(self.displayNamePattern, res)
                remoteNumberList = findall(self.remoteNumberPattern, res)
                deviceTypeList = findall(self.deviceTypePattern, res)

                for index, callID in enumerate(callIDList):
                    if callID not in self.callStatusData:  # if call doesnt exist yet in self.callStatusData
                        self.callStatusData[callID] = {'Status': 'Idle', 'CallType': 'Unknown', 'DisplayName': '', 'RemoteNumber': '', 'DeviceType': 'Unknown'}  # initialize it

                    if callStatusList[index] == 'Idle':  # if call status is idle
                        del self.callStatusData[callID]  # remove it
                    else:
                        try:
                            self.callStatusData[callID]['Status'] = callStatusList[index]
                        except IndexError:
                            pass
                        try:
                            self.callStatusData[callID]['CallType'] = callTypeList[index]
                        except IndexError:
                            pass
                        try:
                            self.callStatusData[callID]['DisplayName'] = displayNameList[index]
                        except IndexError:
                            pass
                        try:
                            self.callStatusData[callID]['RemoteNumber'] = remoteNumberList[index]
                        except IndexError:
                            pass
                        try:
                            self.callStatusData[callID]['DeviceType'] = deviceTypeList[index]
                        except IndexError:
                            pass
            for i in range(5):
                try:
                    item = list(self.callStatusData.keys())[i]
                except IndexError:
                    item = 'None'  # used for indexes with no calls

                try:
                    self.WriteStatus('CallStatus', callStatusStates[self.callStatusData[item]['Status']], {'Call': str(i + 1)})
                except KeyError:  # if item is 'None'
                    self.WriteStatus('CallStatus', 'Idle', {'Call': str(i + 1)})
                try:
                    self.WriteStatus('CallStatusType', typeStates[self.callStatusData[item]['CallType']], {'Call': str(i + 1)})
                except KeyError:
                    self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(i + 1)})
                try:
                    self.WriteStatus('DisplayName', self.callStatusData[item]['DisplayName'], {'Call': str(i + 1)})
                except KeyError:
                    self.WriteStatus('DisplayName', '', {'Call': str(i + 1)})
                try:
                    self.WriteStatus('RemoteNumber', self.callStatusData[item]['RemoteNumber'], {'Call': str(i + 1)})
                except KeyError:
                    self.WriteStatus('RemoteNumber', '', {'Call': str(i + 1)})
                try:
                    self.WriteStatus('CallStatusDeviceType', self.callStatusData[item]['DeviceType'], {'Call': str(i + 1)})
                except KeyError:
                    self.WriteStatus('CallStatusDeviceType', 'Unknown', {'Call': str(i + 1)})

    def UpdateCallStatusDeviceType(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def UpdateCallStatusType(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

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
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 24:
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
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 24:
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

    def SetConnectedDeviceUpdate(self, value, qualifier):
        self.Debug = True
        ConnectedDeviceUpdateCmdString = 'xStatus Peripherals ConnectedDevice\r'
        res = self.SendAndWait(ConnectedDeviceUpdateCmdString, 3, deliTag=b'** end')  # ** end\r\n is used for delimiter
        if res:
            to_add = []
            for mac, name, type_ in zip(findall(self.peripheralMAC, res.decode()), findall(self.peripheralName, res.decode()), findall(self.peripheralType, res.decode())):
                to_add.append((mac, name, type_))

            self.connected_device.overwrite(to_add)
            self.SetConnectedDeviceWriteHelper(value, qualifier)

    def SetConnectedDeviceNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.connected_device.all_size > 0:
            if value == 'Up':
                self.connected_device.previous()
            elif value == 'Down':
                self.connected_device.next()
            elif value == 'Page Up':
                self.connected_device.previous_page()
            elif value == 'Page Down':
                self.connected_device.next_page()

            self.SetConnectedDeviceWriteHelper(value, qualifier)
        else:
            self.Discard('Invalid Command for SetConnectedDeviceNavigation')

    def SetConnectedDeviceWriteHelper(self, value, qualifier):
        for i in zip(range(1, self.connected_device.window + 1), self.connected_device.view()):
            if i[1] not in [self.connected_device.end, self.connected_device.fill]:
                self.WriteStatus('ConnectedDeviceMAC', i[1][0], {'Button': i[0]})
                self.WriteStatus('ConnectedDeviceName', i[1][1], {'Button': i[0]})
                self.WriteStatus('ConnectedDeviceType', i[1][2], {'Button': i[0]})
            else:
                self.WriteStatus('ConnectedDeviceMAC', i[1], {'Button': i[0]})
                self.WriteStatus('ConnectedDeviceName', i[1], {'Button': i[0]})
                self.WriteStatus('ConnectedDeviceType', i[1], {'Button': i[0]})

    def SetDisplayMode(self, value, qualifier):

        if value in self.DisplayModeStatesSet:
            DisplayModeCmdString = 'xConfiguration Video Monitors: {0}\r'.format(self.DisplayModeStatesSet[value].replace(' ', ''))
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):
        self.__UpdateHelper('DisplayMode', 'xConfiguration Video Monitors\r', qualifier)

    def __MatchDisplayMode(self, match, tag):
        value = self.DisplayModeStatesMatch[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def UpdateDisplayName(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def UpdateDNSDomainName(self, value, qualifier):

        DNSDomainNameCmdString = 'xStatus Network 1 DNS Domain Name\r'
        self.__UpdateHelper('DNSDomainName', DNSDomainNameCmdString, qualifier)

    def __MatchDNSDomainName(self, match, tag):

        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('DNSDomainName', value, None)

    def SetDNSDomainNameCommand(self, value, qualifier):

        DNSString = value
        if DNSString:
            CommandString = 'xConfiguration Network 1 DNS Domain Name: {0}\r'.format(DNSString)
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
        value = '' if not match.group(2) else match.group(2).decode()
        self.WriteStatus('DNSServerAddress', value, {'Server': server})

    def SetDNSServerAddressCommand(self, value, qualifier):

        DNSString = value
        if DNSString:
            CommandString = 'xConfiguration Network 1 DNS Server 1 Address: {0}\r'.format(DNSString)
            self.__SetHelper('DNSServerAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def SetDoNotDisturb(self, value, qualifier):

        valueStates = {
            'Active': 'Activate',
            'Inactive': 'Deactivate',
        }

        if value in valueStates:
            DoNotDisturbCmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(valueStates[value])
            self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDoNotDisturb')

    def UpdateDoNotDisturb(self, value, qualifier):
        self.__UpdateHelper('DoNotDisturb', 'xStatus Conference 1 DoNotDisturb\r', qualifier)

    def __MatchDoNotDisturb(self, match, tag):
        self.WriteStatus('DoNotDisturb', match.group(1).decode(), None)

    def SetDTMF(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            DTMFCmdString = 'xCommand Call DTMFSend DTMFString:{0}\r'.format(value)
            self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetFarEndControl(self, value, qualifier):

        if value in ['On', 'Off']:
            FarEndControlCmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(value)
            self.__SetHelper('FarEndControl', FarEndControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndControl')

    def UpdateFarEndControl(self, value, qualifier):
        self.__UpdateHelper('FarEndControl', 'xConfiguration Conference FarEndControl Mode\r', qualifier)

    def __MatchFarEndControl(self, match, tag):
        self.WriteStatus('FarEndControl', match.group(1).decode(), None)

    def SetFarEndCameraPanTilt(self, value, qualifier):

        FarEndCameraPanTiltCmdString = ''
        if value == 'Stop':
            FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Stop\r'
        elif value in ['Left', 'Right', 'Up', 'Down']:
            FarEndCameraPanTiltCmdString = 'xCommand Call FarEndControl Camera Move Value:{0}\r'.format(value)

        if FarEndCameraPanTiltCmdString:
            self.__SetHelper('FarEndCameraPanTilt', FarEndCameraPanTiltCmdString, value, qualifier)
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
            FarEndCameraSourceRecallCmdString = 'xCommand Call FarEndControl Source Select SourceId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraSource', FarEndCameraSourceRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSource')

    def SetFarEndCameraZoom(self, value, qualifier):

        if value in ['In', 'Out']:
            self.__SetHelper('FarEndCameraZoom', 'xCommand Call FarEndControl Camera Move Value:Zoom{0}\r'.format(value), value, qualifier)
        elif value == 'Stop':
            self.__SetHelper('FarEndCameraZoom', 'xCommand Call FarEndControl Camera Stop\r', value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraZoom')

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'xgetxml /status/standby\r'  # not documented, obtained via testing with device
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetH323AliasE164Command(self, value, qualifier):

        H323String = value
        if H323String:
            CommandString = 'xConfiguration H323 H323Alias E164: {0}\r'.format(H323String)
            self.__SetHelper('H323AliasE164Command', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasE164Command')

    def UpdateH323AliasE164Status(self, value, qualifier):

        H323AliasE164StatusCmdString = 'xConfiguration H323 H323Alias E164\r'
        self.__UpdateHelper('H323AliasE164Status', H323AliasE164StatusCmdString, qualifier)

    def __MatchH323AliasE164Status(self, match, tag):
        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('H323AliasE164Status', value, None)

    def SetH323AliasIDCommand(self, value, qualifier):

        H323String = value
        if H323String:
            CommandString = 'xConfiguration H323 H323Alias ID: {0}\r'.format(H323String)
            self.__SetHelper('H323AliasIDCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasIDCommand')

    def UpdateH323AliasIDStatus(self, value, qualifier):

        H323AliasIDStatusCmdString = 'xConfiguration H323 H323Alias ID\r'
        self.__UpdateHelper('H323AliasIDStatus', H323AliasIDStatusCmdString, qualifier)

    def __MatchH323AliasIDStatus(self, match, tag):
        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('H323AliasIDStatus', value, None)

    def UpdateH323GatekeeperAddress(self, value, qualifier):

        H323GatekeeperAddressCmdString = 'xStatus H323 Gatekeeper Address\r'
        self.__UpdateHelper('H323GatekeeperAddress', H323GatekeeperAddressCmdString, qualifier)

    def __MatchH323GatekeeperAddress(self, match, tag):

        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('H323GatekeeperAddress', value, None)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        H323String = value
        if H323String:
            CommandString = 'xConfiguration H323 Gatekeeper Address: {0}\r'.format(H323String)
            self.__SetHelper('H323GatekeeperAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323GatekeeperAddressCommand')

    def UpdateH323GatekeeperStatus(self, value, qualifier):

        H323GatekeeperStatusCmdString = 'xStatus H323 Gatekeeper Status\r'
        self.__UpdateHelper('H323GatekeeperStatus', H323GatekeeperStatusCmdString, qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323GatekeeperStatus', value, None)

    def SetH323ProfileAuthenticationLoginNameCommand(self, value, qualifier):

        H323String = value
        if H323String:
            CommandString = 'H323 Authentication LoginName: {0}\r'.format(H323String)
            self.__SetHelper('H323ProfileAuthenticationLoginNameCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationLoginNameCommand')

    def SetH323ProfileAuthenticationPasswordCommand(self, value, qualifier):

        H323String = value
        if H323String:
            CommandString = 'xConfiguration H323 Authentication Password: {0}\r'.format(H323String)
            self.__SetHelper('H323ProfileAuthenticationPasswordCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationPasswordCommand')

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320': 'h320',
            'H323': 'h323',
            'SIP': 'sip',
            'Auto': 'Auto',
            'Spark': 'Spark'
        }

        if value in ['Accept', 'Reject', 'Disconnect All']:
            self.__SetHelper('Hook', 'xCommand Call {0}\r'.format(value.replace('All', '')), value, qualifier)
        elif 'Resume' in value or 'Disconnect' in value or 'Hold' in value or 'Join' in value:
            val = value.split(' ')
            cmd = val[0]
            index = int(val[1]) - 1
            try:
                self.__SetHelper('Hook', 'xCommand Call {0} CallId: {1}\r'.format(cmd, list(self.callStatusData.keys())[index]), value, qualifier)
            except (TypeError, IndexError):
                self.Discard('Invalid Command for SetHook')
        elif value == 'Dial':
            protocol = qualifier['Protocol']
            number = qualifier['Number']
            if number and protocol in Protocol_Values:
                if protocol == 'Auto':
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:\"{0}\" Protocol:{1}\r'.format(number, Protocol_Values[protocol]), value, qualifier)
            else:
                self.Discard('Invalid Command for SetHook')
        else:
            self.Discard('Invalid Command for SetHook')

    def SetInput(self, value, qualifier):

        if value in self.InputStates:
            self.__SetHelper('Input', 'xCommand Video Input SetMainVideoSource ConnectorId: {0}\r'.format(self.InputStates[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xStatus Video Input MainVideoSource\r', qualifier)

    def __MatchInput(self, match, tag):
        self.WriteStatus('Input', match.group(1).decode(), None)

    def SetInputHDMILevel(self, value, qualifier):

        if qualifier['Input'] in ['HDMI 1', 'HDMI 2', 'HDMI 3'] and -24 <= value <= 0:
            InputHDMILevelCmdString = 'xConfiguration Audio Input {0} Level:{1}\r'.format(qualifier['Input'], value)
            self.__SetHelper('InputHDMILevel', InputHDMILevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputHDMILevel')

    def UpdateInputHDMILevel(self, value, qualifier):
        if qualifier['Input'] in ['HDMI 1', 'HDMI 2', 'HDMI 3']:
            InputHDMILevelCmdString = 'xConfiguration Audio Input {0} Level\r'.format(qualifier['Input'])
            self.__UpdateHelper('InputHDMILevel', InputHDMILevelCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputHDMILevel')

    def __MatchInputHDMILevel(self, match, tag):
        input_ = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('InputHDMILevel', value, {'Input': input_})

    def SetInputLineLevel(self, value, qualifier):

        if qualifier['Input'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4'] and 0 <= value <= 24:
            self.__SetHelper('InputLineLevel', 'xConfiguration Audio Input {0} Level:{1}\r'.format(qualifier['Input'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLineLevel')

    def UpdateInputLineLevel(self, value, qualifier):
        if qualifier['Input'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4']:
            self.__UpdateHelper('InputLineLevel', 'xConfiguration Audio Input {0} Level\r'.format(qualifier['Input']), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLineLevel')

    def __MatchInputLineLevel(self, match, tag):
        input_ = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('InputLineLevel', value, {'Input': input_})

    def SetInputMicLevel(self, value, qualifier):

        if qualifier['Input'] in self.MicStates and 0 <= value <= self.InputLevelMax:
            input_ = self.MicStates[qualifier['Input']]
            self.__SetHelper('InputMicLevel', 'xConfiguration Audio Input {0} Level:{1}\r'.format(input_, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLevel')

    def UpdateInputMicLevel(self, value, qualifier):
        if qualifier['Input'] in self.MicStates:
            input_ = self.MicStates[qualifier['Input']]
            self.__UpdateHelper('InputMicLevel', 'xConfiguration Audio Input {0} Level\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMicLevel')

    def __MatchInputMicLevel(self, match, tag):
        input_ = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('InputMicLevel', value, {'Input': input_})

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Off',
            'Off': 'On'
        }

        if qualifier['Input'] in self.InputMuteStates and value in ValueStateValues:
            input_ = self.InputMuteStates[qualifier['Input']]
            self.__SetHelper('InputMute', 'xConfiguration Audio Input {0} Mode:{1}\r'.format(input_, ValueStateValues[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):
        if qualifier['Input'] in self.InputMuteStates:
            input_ = self.InputMuteStates[qualifier['Input']]
            self.__UpdateHelper('InputMute', 'xConfiguration Audio Input {0} Mode\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            'On': 'Off',
            'Off': 'On'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, {'Input': match.group(1).decode()})

    def UpdateInputSignal(self, value, qualifier):

        if qualifier['Input'] in self.InputStates:
            input_ = self.InputStates[qualifier['Input']]
            self.Send('xFeedback register /Status/Video/Input/Connector/Connected\r')  # send subscription
            self.__UpdateHelper('InputSignal', 'xStatus Video Input Connector {0} Connected\r'.format(input_), qualifier)  # send query for initial status
        else:
            self.Discard('Invalid Command for UpdateInputSignal')

    def __MatchInputSignal(self, match, tag):
        input_ = self.InputStates[match.group(1).decode()]
        self.WriteStatus('InputSignal', match.group(2).decode(), {'Input': input_})

    def SetInputVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 'Mute',
            'Off' : 'Unmute'
        }

        if value in ValueStateValues:
            InputVideoMuteCmdString = 'xCommand Video Input MainVideo {}\r'.format(ValueStateValues[value])
            self.__SetHelper('InputVideoMute', InputVideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for InputVideoMute')

    def UpdateInputVideoMute(self, value, qualifier):
        InputVideoMuteCmdString = 'xStatus Video Input MainVideoMute\r'
        self.__UpdateHelper('InputVideoMute', InputVideoMuteCmdString, qualifier)

    def __MatchInputVideoMute(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('InputVideoMute', value, None)

    def SetIPv4AddressCommand(self, value, qualifier):

        IPv4String = value
        if IPv4String:
            CommandString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(IPv4String)
            self.__SetHelper('IPv4AddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4AddressCommand')

    def SetIPv4GatewayCommand(self, value, qualifier):

        IPv4String = value
        if IPv4String:
            CommandString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(IPv4String)
            self.__SetHelper('IPv4GatewayCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4GatewayCommand')

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        IPv4String = value
        if IPv4String:
            CommandString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(IPv4String)
            self.__SetHelper('IPv4SubnetMaskCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4SubnetMaskCommand')

    def SetIREmulation(self, value, qualifier):

        KeyStates = {
            'Click': 'Click',
            'Press': 'Press',
            'Release': 'Release'
        }

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
            'C': 'C',
            'Call': 'Call',
            'Down': 'Down',
            'F1': 'F1',
            'F2': 'F2',
            'F3': 'F3',
            'F4': 'F4',
            'F5': 'F5',
            'Grab': 'Grab',
            'Home': 'Home',
            'Layout': 'Layout',
            'Left': 'Left',
            'Mute': 'Mute',
            'Mute Mic': 'MuteMic',
            'Ok': 'Ok',
            'PhoneBook': 'PhoneBook',
            'Presentation': 'Presentation',
            'Right': 'Right',
            'Selfview': 'Selfview',
            'Square': 'Square',
            'Aux': 'SrcAux',
            'Camera': 'SrcCamera',
            'Doc Cam': 'SrcDocCam',
            'Pc': 'SrcPc',
            'Vcr': 'SrcVcr',
            'Star': 'Star',
            'Up': 'Up',
            'Volume Down': 'VolumeDown',
            'Volume Up': 'VolumeUp',
            'Zoom In': 'ZoomIn',
            'Zoom Out': 'ZoomOut',
            'Disconnect': 'Disconnect',
            '+': '+',
            '-': '-',
        }

        if qualifier['Key'] in KeyStates and value in ValueStateValues:
            IREmulationCmdString = 'xCommand UserInterface OSD Key {0} Key: {1}\r'.format(KeyStates[qualifier['Key']], ValueStateValues[value])
            self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetLayoutSet(self, value, qualifier):

        ValueStateValues = {
            'Auto'        : 'auto',
            'Custom'      : 'custom',
            'Equal'       : 'equal',
            'Overlay'     : 'overlay',
            'Prominent'   : 'prominent',
            'Prominent L' : 'prominent_l',
            'Single'      : 'single'
        }

        if qualifier['Target'] in ['Local', 'Remote'] and value in ValueStateValues:
            LayoutSetCmdString = 'xCommand Video Layout LayoutFamily Set Target: {0} LayoutFamily: {1}\r'.format(qualifier['Target'], ValueStateValues[value])
            if value != 'Auto':
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
            'equal': 'Equal',
            'overlay': 'Overlay',
            'prominent': 'Prominent',
            'prominent_l' : 'Prominent L',
            'single': 'Single'
        }

        qualifier = {'Target': match.group(1).decode()}
        try:
            value = ValueStateValues[match.group(2).decode()]
        except KeyError:
            value = 'Custom'
        self.WriteStatus('LayoutSet', value, qualifier)

    def SetMacro(self, value, qualifier):

        nameValue = qualifier['Name']
        if 0 <= len(nameValue) <= 255 and value in ['Activate', 'Deactivate']:
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

        MacroSetCmdString = 'xCommand Macros Runtime Restart\r'
        self.__SetHelper('RestartMacros', MacroSetCmdString, value, qualifier)

    def SetMeetingRefresh(self, value, qualifier):

        MeetingRefreshCmdString = 'xCommand Bookings List Limit:5\r'
        res = self.SendAndWait(MeetingRefreshCmdString, 10, deliTag=b'** end')  # ** end\r\n is used for delimiter
        if res:
            idList = findall(self.MeetingID, res.decode())
            titleList = findall(self.Title, res.decode())
            agendaList = findall(self.Agenda, res.decode())
            firstNameList = findall(self.FirstName, res.decode())
            lastNameList = findall(self.LastName, res.decode())
            startTimeList = findall(self.StartTime, res.decode())
            endTimeList = findall(self.EndTime, res.decode())
            dialModeList = findall(self.DialMode, res.decode())
            dialNumberDict = dict(findall(self.DialNumber, res.decode()))

            if idList:
                i = 0
                for id_, info, in idList:
                    StartDateTime = get_dt_from_str(startTimeList[i][1], '%Y-%m-%dT%H:%M:%SZ')
                    StartDateTimeTZ = StartDateTime.replace(tzinfo=timezone.utc).astimezone(tz=None)  # takes time zone and daylight savings
                    startMeeting = StartDateTimeTZ.strftime('%m/%d %I:%M%p')
                    if '-' in startMeeting:
                        startMeeting = startMeeting.replace('-', '+')
                    elif '+' in startMeeting:
                        startMeeting = startMeeting.replace('+', '-')

                    EndDateTime = get_dt_from_str(endTimeList[i][1], '%Y-%m-%dT%H:%M:%SZ')
                    EndDateTimeTZ = EndDateTime.replace(tzinfo=timezone.utc).astimezone(tz=None)
                    endMeeting = EndDateTimeTZ.strftime('%m/%d %I:%M%p')
                    if '-' in endMeeting:
                        endMeeting = endMeeting.replace('-', '+')
                    elif '+' in startMeeting:
                        endMeeting = endMeeting.replace('+', '-')
                    meetingNumber = dialNumberDict.get(str(i + 1), 'No number to dial')

                    try:
                        self.WriteStatus('MeetingTitle', '{0}'.format(titleList[i][1]), {'Meeting': str(i + 1)})
                    except IndexError:
                        self.WriteStatus('MeetingTitle', '', {'Meeting': str(i + 1)})

                    try:
                        self.WriteStatus('MeetingAgenda', '{0}'.format(agendaList[i][1]), {'Meeting': str(i + 1)})
                    except IndexError:
                        self.WriteStatus('MeetingAgenda', '', {'Meeting': str(i + 1)})

                    try:
                        firstName = firstNameList[i][1]
                    except IndexError:
                        firstName = ''
                    try:
                        lastName = lastNameList[i][1]
                    except IndexError:
                        lastName = ''
                    fullName = '{0} {1}'.format(firstName, lastName).strip()
                    self.WriteStatus('MeetingOrganizer', fullName, {'Meeting': str(i + 1)})

                    self.WriteStatus('MeetingStartTime', '{0}'.format(startMeeting), {'Meeting': str(i + 1)})
                    self.WriteStatus('MeetingEndTime', '{0}'.format(endMeeting), {'Meeting': str(i + 1)})

                    try:
                        self.WriteStatus('MeetingDialMode', '{0}'.format(dialModeList[i][1]), {'Meeting': str(i + 1)})
                    except IndexError:
                        self.WriteStatus('MeetingDialMode', '', {'Meeting': str(i + 1)})

                    self.WriteStatus('MeetingDialNumber', '{0}'.format(meetingNumber), {'Meeting': str(i + 1)})
                    i += 1
                if i <= 5:
                    for i in range(i, 6):
                        self.WriteStatus('MeetingTitle', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingAgenda', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingOrganizer', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingStartTime', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingEndTime', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingDialMode', '', {'Meeting': str(i + 1)})
                        self.WriteStatus('MeetingDialNumber', '', {'Meeting': str(i + 1)})
                        i += 1
            else:
                for i in range(1, 6):
                    self.WriteStatus('MeetingTitle', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingAgenda', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingOrganizer', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingStartTime', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingEndTime', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingDialMode', 'No bookings found', {'Meeting': str(i)})
                    self.WriteStatus('MeetingDialNumber', 'No bookings found', {'Meeting': str(i)})

    def SetMeetingJoin(self, value, qualifier):

        if 1 <= int(qualifier['Meeting']) <= 5:
            meetingNumber = self.ReadStatus('MeetingDialNumber', {'Meeting': qualifier['Meeting']})
            if meetingNumber and meetingNumber not in ['No number to dial', 'No bookings found']:
                MeetingJoinCmdString = 'xCommand Dial Number:{0}\r'.format(meetingNumber)
                self.__SetHelper('MeetingJoin', MeetingJoinCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMeetingJoin')
        else:
            self.Discard('Invalid Command for SetMeetingJoin')

    def SetMicrophonesMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'Unmute',
        }

        if value in ValueStateValues:
            MicrophonesMuteCmdString = 'xCommand Audio Microphones {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophonesMute')

    def UpdateMicrophonesMute(self, value, qualifier):
        self.Send('xFeedback register /Status/Audio/Microphones/Mute\r')  # send subscription
        self.__UpdateHelper('MicrophonesMute', 'xStatus Audio Microphones Mute\r', qualifier)  # send query for initial status

    def __MatchMicrophonesMute(self, match, tag):
        self.WriteStatus('MicrophonesMute', match.group(1).decode(), None)

    def SetOutputLevel(self, value, qualifier):

        if qualifier['Output'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', 'HDMI 1', 'HDMI 2'] and -24 <= value <= 0:
            self.__SetHelper('OutputLevel', 'xConfiguration Audio Output {0} Level:{1}\r'.format(qualifier['Output'], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):
        if qualifier['Output'] in ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5', 'Line 6', 'HDMI 1', 'HDMI 2']:
            self.__UpdateHelper('OutputLevel', 'xConfiguration Audio Output {0} Level\r'.format(qualifier['Output']), qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        Output = match.group(1).decode()
        value = int(match.group(2))
        self.WriteStatus('OutputLevel', value, {'Output': Output})

    def UpdatePeopleCountCurrent(self, value, qualifier):
        self.Send('xFeedback register /Status/RoomAnalytics/PeopleCount/Current\r')  # send subscription
        self.__UpdateHelper('PeopleCountCurrent', 'xStatus RoomAnalytics PeopleCount Current\r', qualifier)  # send query for initial status

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
        self.Send('xFeedback register /Status/RoomAnalytics/PeoplePresence\r')  # send subscription
        self.__UpdateHelper('PeoplePresence', 'xStatus RoomAnalytics PeoplePresence\r', qualifier)  # send query for initial status

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

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        if self.phonebook.all_size > 0 and value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if value == 'Up':
                self.phonebook.previous()
            elif value == 'Down':
                self.phonebook.next()
            elif value == 'Page Up':
                self.phonebook.previous_page()
            elif value == 'Page Down':
                self.phonebook.next_page()

            self.SetPhonebookWriteHandler(value, None)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchSet(self, value, qualifier):

        if value < 1 or value > self._NumberofPhonebookSearch:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number not in [self.phonebook.end, self.phonebook.fill]:
                number = number[number.find(' : ') + 3:]
                self.SetHook('Dial', {'Protocol': 'Auto', 'Number': number})

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True

        if qualifier['Phonebook Type'] in ['Corporate', 'Local'] and value in ['Refresh', 'Next Search', 'Previous Search']:
            self.phonebook_qualifier['Phonebook Type'] = qualifier.get('Phonebook Type', 'Local')
            self.phonebook_qualifier['Contact'] =  qualifier.get('Contact', '')
            self.phonebook_qualifier['FolderID'] =  qualifier.get('FolderID', '')

            if value == 'Refresh':
                self.phonebook.clear()
                self.phonebook.load()
            elif value == 'Next Search':
                self.phonebook.scroll(self.phonebook.chunk_size)
            elif value == 'Previous Search':
                self.phonebook.scroll(-self.phonebook.chunk_size)

            self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookUpdate')

    def __UpdatePhonebookHelper(self, offset, size):
        self.WriteStatus('PhonebookSearchResult', '***Loading Contacts***', {'Button': 1})
        for i in range(2, int(self._NumberofPhonebookSearch) + 1):
            self.WriteStatus('PhonebookSearchResult', '...', {'Button': i})
            
        phonebookType = self.phonebook_qualifier.get('Phonebook Type', 'Local')
        contact = self.phonebook_qualifier.get('Contact', '')
        folderID = self.phonebook_qualifier.get('FolderID', '')
        if phonebookType in ['Corporate', 'Local']:
            if contact:
                contact = 'SearchString: "{0}" '.format(contact)
            else:
                contact = ''

            if folderID:
                fldID = 'FolderID:"{0}" '.format(folderID)
            else:
                fldID = ''
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1}SearchField: Name ContactType: Contact {2} Offset: {3} Limit: {4}\r'.format(phonebookType, contact, fldID, offset, size)  # search for all contacts
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')  # ** end\r\n is used for delimiter
            if res:
                to_add = OrderedDict()  # Clear Dictionary and repopulate with new search

                nameList = findall(self.dirName, res.decode())
                numberList = findall(self.dirNumber, res.decode())
                for i, name in nameList:
                    to_add[i] = {'Name': name}

                for i, number in numberList:
                    if i in to_add:
                        to_add[i]['Number'] = number
                    else:
                        to_add[i] = {'Number': number}

                return to_add.values(), len(to_add) < size
        else:
            self.Discard('Invalid Command')

        return [], False

    def SetPhonebookWriteHandler(self, value, qualifier):
        for i in zip(range(1, self.phonebook.window + 1), self.phonebook.format(lambda x: '{0} : {1}'.format(x['Name'], x['Number']))):  # populate up to max labels configured
            self.WriteStatus('PhonebookSearchResult', i[1], {'Button': i[0]})

    def SetPhonebookFolderIDNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.phonebook_folder_id.all_size > 0:
            if value == 'Up':
                self.phonebook_folder_id.previous()
            elif value == 'Down':
                self.phonebook_folder_id.next()
            elif value == 'Page Up':
                self.phonebook_folder_id.previous_page()
            elif value == 'Page Down':
                self.phonebook_folder_id.next_page()

            self.SetPhonebookFolderIDWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDNavigation')

    def SetPhonebookFolderIDSearchSet(self, value, qualifier):
        self.Debug = True

        if 1 <= value <= self._NumberofPhonebookFolderSearch:
            folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
            if folderName not in {self.phonebook_folder_id.end, self.phonebook_folder_id.fill}:
                number = self.phonebook_folder_id[value - 1]['ID']
                self.phonebook_qualifier['FolderID'] = number
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDSearchSet')

    def SetPhonebookFolderIDUpdate(self, value, qualifier):
        self.Debug = True

        phonebookValue = qualifier.get('Phonebook Type', 'Local')
        if phonebookValue in ['Local', 'Corporate']:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: 250\r'.format(phonebookValue)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')  # ** end\r\n is used for delimiter
            if res:
                to_add = OrderedDict()

                folderName = findall(self.FolderNameRex, res.decode())
                folderID = findall(self.FolderIDRex, res.decode())
                for i, name in folderName:
                    to_add[i] = {'Name': name}

                for i, id_ in folderID:
                    if i in to_add:
                        to_add[i]['ID'] = id_
                    else:
                        to_add[i] = {'ID': id_}

                self.phonebook_folder_id.overwrite(to_add.values())
                self.SetPhonebookFolderIDWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate')

    def SetPhonebookFolderIDWriteHandler(self, value, qualifier):
        for i in zip(range(1, self.phonebook_folder_id.window + 1), self.phonebook_folder_id.format(lambda x: x['Name'])):
            self.WriteStatus('PhonebookFolderIDSearchResult', i[1], {'Button': i[0]})

    def SetPresentation(self, value, qualifier):

        sendingModeStates = {
            'Not Specified': '',
            'Local Only': ' SendingMode:LocalOnly',
            'Local and Remote': ' SendingMode:LocalRemote'
        }

        instanceStates = {
            'Not Specified': '',
            'New': ' Instance:New',
            '1': ' Instance:1',
            '2': ' Instance:2',
            '3': ' Instance:3',
            '4': ' Instance:4',
            '5': ' Instance:5',
            '6': ' Instance:6',
        }

        layoutStates = {
            'Not Specified': '',
            'Equal': ' Layout:Equal',
            'Prominent': ' Layout:Prominent',
        }

        inputSource = qualifier['Video Input Source']
        sendingMode = qualifier['Sending Mode']
        instanceID = qualifier['Instance']
        layout = qualifier['Layout']
        cmdState = ''
        if (inputSource == 'Not Specified' or 'Presentation Source' in inputSource) and (instanceID == 'Not Specified' or instanceID in ['1', '2', '3', '4', '5', '6']) and 'Stop' == value:
            cmdState = 'xCommand Presentation Stop{}{}\r'.format(instanceStates[instanceID], self.InputSourceStates[inputSource])
        elif inputSource in self.InputSourceStates and sendingMode in sendingModeStates and instanceID in instanceStates and layout in layoutStates and 'Start' == value:
            cmdState = 'xCommand Presentation Start{}{}{}{}\r'.format(instanceStates[instanceID], sendingModeStates[sendingMode], self.InputSourceStates[inputSource], layoutStates[layout])
        if cmdState:
            self.__SetHelper('Presentation', cmdState, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):

        sourceValue = value
        if sourceValue:
            cmdstring = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{0}"\r'.format(sourceValue)
            self.__SetHelper('PresentationExternalSourceSelectCommand', cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationExternalSourceSelectCommand')

    def UpdatePresentationSourceStatus(self, value, qualifier):
    
        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            self.Send('xFeedback register /Status/Conference/Presentation/LocalInstance/Source\r')  # send subscription
            self.__UpdateHelper('PresentationSourceStatus', 'xStatus Conference Presentation LocalInstance {0} Source\r'.format(instanceID), qualifier)  # send query for initial status
        else:
            self.Discard('Invalid Command for UpdatePresentationSourceStatus')

    def __MatchPresentationSourceStatus(self, match, tag):
        instanceID = match.group(1).decode()
        value = match.group(2).decode()
        if value == '0':
            value = 'Off'
        self.WriteStatus('PresentationSourceStatus', value, {'Instance': instanceID})

    def __MatchPresentationSourceStatusOff(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('PresentationSourceStatus', 'Off', {'Instance': instanceID})

    def UpdatePresentationModeStatus(self, value, qualifier):
        self.Send('xFeedback register /Status/Conference/Presentation/Mode\r')  # send subscription
        self.__UpdateHelper('PresentationModeStatus', 'xStatus Conference Presentation Mode\r', qualifier)  # send query for initial status

    def __MatchPresentationModeStatus(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('PresentationModeStatus', value, None)

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            self.Send('xFeedback register /Status/Conference/Presentation/LocalInstance/SendingMode\r')  # send subscription
            self.__UpdateHelper('PresentationSendingModeStatus', 'xStatus Conference Presentation LocalInstance {0} SendingMode\r'.format(instanceID), qualifier)  # send query for initial status
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        ValueStateValues = {
            'LocalRemote': 'Local and Remote',
            'LocalOnly': 'Local Only',
            'Off': 'Off',
        }
        instanceID = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PresentationSendingModeStatus', value, {'Instance': instanceID})

    def __MatchPresentationSendingModeStatusOff(self, match, tag):

        instanceID = match.group(1).decode()
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance': instanceID})

    def __MatchPresentationStop(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance': instanceID})
        self.WriteStatus('PresentationSourceStatus', 'Off', {'Instance': instanceID})

    def SetPresenterTrackControl(self, value, qualifier):

        ValueStateValues = {
            'On': 'True',
            'Off': 'False'
        }

        if value in ValueStateValues:
            PresenterTrackControlCmdString = 'xConfiguration Cameras PresenterTrack Enabled: {}\r'.format(ValueStateValues[value])
            self.__SetHelper('PresenterTrackControl', PresenterTrackControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresenterTrackControl')

    def UpdatePresenterTrackControl(self, value, qualifier):

        PresenterTrackControlCmdString = 'xConfiguration Cameras PresenterTrack Enabled\r'
        self.__UpdateHelper('PresenterTrackControl', PresenterTrackControlCmdString, qualifier)

    def __MatchPresenterTrackControl(self, match, tag):

        ValueStateValues = {
            'True': 'On',
            'False': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresenterTrackControl', value, None)

    def __MatchPresenterTrackControlOff(self, match, tag):

        self.WriteStatus('PresenterTrackControl', 'Off', None)

    def SetPresenterTrackMode(self, value, qualifier):

        if value in ['Off', 'Follow', 'Diagnostic', 'Background', 'Setup', 'Persistent']:
            PresenterTrackModeCmdString = 'xCommand Cameras PresenterTrack Set Mode: {}\r'.format(value)
            self.__SetHelper('PresenterTrackMode', PresenterTrackModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresenterTrackMode')

    def UpdatePresenterTrackMode(self, value, qualifier):

        PresenterTrackModeCmdString = 'xStatus Cameras PresenterTrack Status\r'
        self.__UpdateHelper('PresenterTrackMode', PresenterTrackModeCmdString, qualifier)

    def __MatchPresenterTrackMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresenterTrackMode', value, None)

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

        if value in ['On', 'Off', 'Current']:
            SelfViewDefaultFullscreenModeCmdString = 'xConfiguration Video Selfview Default FullscreenMode:{0}\r'.format(value)
            self.__SetHelper('SelfViewDefaultFullscreenMode', SelfViewDefaultFullscreenModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfViewDefaultFullscreenMode')

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
        self.Send('xFeedback register /Status/Video/Selfview/Mode\r')  # send subscription
        self.__UpdateHelper('SelfView', 'xStatus Video Selfview Mode\r', qualifier)  # send query for initial status

    def __MatchSelfView(self, match, tag):
        self.WriteStatus('SelfView', match.group(1).decode(), None)

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

        if value in ValueStateValues:
            SelfViewPositionCmdString = 'xCommand Video Selfview Set PIPPosition:{0}\r'.format(ValueStateValues[value])
            self.__SetHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfViewPosition')

    def UpdateSelfViewPosition(self, value, qualifier):
        self.Send('xFeedback register /Status/Video/Selfview/PIPPosition\r')  # send subscription
        self.__UpdateHelper('SelfViewPosition', 'xStatus Video Selfview PIPPosition\r', qualifier)  # send query for initial status

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
        value = match.group(1).decode()
        self.WriteStatus('SelfViewPosition', ValueStateValues[value], None)

    def UpdateSIPRegistrationStatus(self, value, qualifier):

        SIPRegistrationStatusCmdString = 'xStatus SIP Registration 1 Status\r'
        self.__UpdateHelper('SIPRegistrationStatus', SIPRegistrationStatusCmdString, qualifier)

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

        SIPURIString = value
        if SIPURIString:
            SIPURICommandCmdString = 'xConfiguration SIP URI: {}\r'.format(SIPURIString)
            self.__SetHelper('SIPURICommand', SIPURICommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSIPURICommand')

    def UpdateSIPURIStatus(self, value, qualifier):

        SIPURIStatusCmdString = 'xConfiguration SIP URI\r'
        self.__UpdateHelper('SIPURIStatus', SIPURIStatusCmdString, qualifier)

    def __MatchSIPURIStatus(self, match, tag):

        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('SIPURIStatus', value, None)

    def SetSleepTimer(self, value, qualifier):

        if 1 <= value <= 480:
            self.__SetHelper('SleepTimer', 'xCommand Standby ResetTimer Delay:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTimer')

    def SetStandby(self, value, qualifier):

        stateValues = {
            'Activate': 'Activate',
            'Deactivate': 'Deactivate',
            'Half Wake': 'Halfwake'
        }

        if value in stateValues:
            StandbyCmdString = 'xCommand Standby {0}\r'.format(stateValues[value])
            self.__SetHelper('Standby', StandbyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def UpdateStandby(self, value, qualifier):
        self.__UpdateHelper('Standby', 'xStatus Standby State\r', qualifier)

    def __MatchStandby(self, match, tag):
        ValueStateValues = {
            'Off': 'Deactivate',
            'Standby': 'Activate',
            'EnteringStandby': 'Entering Standby',
            'Halfwake': 'Half Wake',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Standby', value, None)

    def UpdateSystemTimeStatus(self, value, qualifier):

        if qualifier['Type'] in ['Date', 'Time']:
            SystemTimeStatusCmdString = 'xStatus Time SystemTime\r'
            self.__UpdateHelper('SystemTimeStatus', SystemTimeStatusCmdString, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSystemTimeStatus')

    def __MatchSystemTimeStatus(self, match, tag):

        value = match.group(1).decode()
        date = '' if not match.group(1) else value.split('T')[0]
        time_ = '' if not match.group(1) else value.split('T')[1][0:5]
        self.WriteStatus('SystemTimeStatus', date, {'Type': 'Date'})
        self.WriteStatus('SystemTimeStatus', time_, {'Type': 'Time'})

    def SetSystemUnitNameCommand(self, value, qualifier):

        SystemUnitNameString = value
        if SystemUnitNameString:
            SystemUnitNameCommandCmdString = 'xConfiguration SystemUnit Name: {}\r'.format(SystemUnitNameString)
            self.__SetHelper('SystemUnitNameCommand', SystemUnitNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSystemUnitNameCommand')

    def UpdateSystemUnitNameStatus(self, value, qualifier):

        SystemUnitNameStatusCmdString = 'xConfiguration SystemUnit Name\r'
        self.__UpdateHelper('SystemUnitNameStatus', SystemUnitNameStatusCmdString, qualifier)

    def __MatchSystemUnitNameStatus(self, match, tag):

        value = '' if not match.group(1) else match.group(1).decode()
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
        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('GatewayAddress', value, None)

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = 'xStatus Network 1 IPv4 Address\r'
        self.__UpdateHelper('IPAddress', IPAddressCmdString, qualifier)

    def __MatchIPAddress(self, match, tag):
        value = '' if not match.group(1) else match.group(1).decode()
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

        value = match.group(1).decode()
        self.WriteStatus('NetworkAssignment', value, None)

    def UpdateRemoteNumber(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def SetSpeakerTrackControl(self, value, qualifier):

        ValueStateValues = {
            'On': 'Activate',
            'Off': 'Deactivate'
        }

        if value in ValueStateValues:
            SpeakerTrackControlCmdString = 'xCommand Cameras SpeakerTrack {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerTrackControl')

    def UpdateSpeakerTrackControl(self, value, qualifier):
        SpeakerTrackControlCmdString = 'xStatus Cameras SpeakerTrack Status\r'
        self.__UpdateHelper('SpeakerTrackControl', SpeakerTrackControlCmdString, qualifier)

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
        self.__UpdateHelper('SpeakerTrackMode', SpeakerTrackModeCmdString, qualifier)

    def __MatchSpeakerTrackMode(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('SpeakerTrackMode', value, None)

    def UpdateSubnetMask(self, value, qualifier):

        SubnetMaskCmdString = 'xStatus Network 1 IPv4 SubnetMask\r'
        self.__UpdateHelper('SubnetMask', SubnetMaskCmdString, qualifier)

    def __MatchSubnetMask(self, match, tag):
        value = '' if not match.group(1) else match.group(1).decode()
        self.WriteStatus('SubnetMask', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.tshellerror:
            self.Discard('Inappropriate Command')
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, qualifier):

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

    def csco_12_5454_SX10(self):

        self.InputLevelMax = 24

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.InputMuteStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.InputSourceStates = {
            'Not Specified': '',
            'Presentation Source 2': ' PresentationSource:2',
            'Connector Id 2': ' ConnectorId:2',
            'Connector Id 3': ' ConnectorId:3'
        }

    def csco_12_5454_SX20(self):

        self.InputLevelMax = 24

        self.DisplayModeStatesSet = {
            'Auto': 'Auto',
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
        }

        self.DisplayModeStatesMatch = {
            'Auto': 'Auto',
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            'Composed': 'Composed',
        }

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.InputMuteStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.InputSourceStates = {
            'Not Specified': '',
            'Presentation Source 1': ' PresentationSource:1',
            'Presentation Source 2': ' PresentationSource:2',
            'Connector Id 1': ' ConnectorId:1',
            'Connector Id 2': ' ConnectorId:2'
        }

    def csco_12_5454_SX80(self):

        self.InputLevelMax = 70

        self.DisplayModeStatesSet = {
            'Auto': 'Auto',
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
            'Triple Presentation Only': 'TriplePresentationOnly',
            'Triple': 'Triple',
        }

        self.DisplayModeStatesMatch = {
            'Auto': 'Auto',
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
            'TriplePresentationOnly': 'Triple Presentation Only',
            'Triple': 'Triple',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            'Composed': 'Composed',
        }

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3',
            'Microphone 4': 'Microphone 4',
            'Microphone 5': 'Microphone 5',
            'Microphone 6': 'Microphone 6',
            'Microphone 7': 'Microphone 7',
            'Microphone 8': 'Microphone 8',
        }

        self.InputMuteStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3',
            'Microphone 4': 'Microphone 4',
            'Microphone 5': 'Microphone 5',
            'Microphone 6': 'Microphone 6',
            'Microphone 7': 'Microphone 7',
            'Microphone 8': 'Microphone 8',
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
            'Line 3': 'Line 3',
            'Line 4': 'Line 4',
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'HDMI 3': 'HDMI 3',
        }

        self.InputSourceStates = {
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

        if not self.scrollable(steps) and self.all_size:
            self.load()
            super().scroll(min(steps, self.max_offset - self.offset))
        else:
            super().scroll(steps)
    def load(self):

        chunk, self.loaded = self.__on_end_callback(self.all_size, self.chunk_size)
        self.extend(chunk)

    def scrollable(self, steps):

        return self.loaded or self.offset + steps <= self.max_offset or self.filtered

def get_dt_from_str(date_string: str, format_str: str='%Y-%m-%dT%H:%M:%SZ') -> datetime:
    """Convert 2024-09-01T14:34:02Z -> datetime(), ignoring timezone offset.Í"""

    if format_str not in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M']:
        raise ValueError('unsupport format: {}'.format(format_str))

    date, time_ = date_string.split('T')

    year, month, day = date.split('-')
    year, month, day = int(year), int(month), int(day)
    
    if format_str[-1] == 'Z':
        time_ = time_[:-1]

    if format_str in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%dT%H:%M:%S']:
        hour, minute, second = time_.split(':')
    elif format_str == '%Y-%m-%dT%H:%M':
        hour, minute = time_.split(':')
        second = '0'
    
    hour, minute, second = int(hour), int(minute), int(second)    
    
    return datetime(year, month, day, hour, minute, second)