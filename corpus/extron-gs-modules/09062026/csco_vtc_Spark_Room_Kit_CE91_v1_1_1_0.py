from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
from extronlib.system import Wait, ProgramLog
import base64


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

        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPhonebookSearch = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofPeripheral = 5
        self._NumberofContactsPerSearch = 50
        self._NumberofFoldersPerSearch = 50

        self.Models = {
            'Spark Room Kit CE9.1.X': self.csco_12_3161_non_plus,
            'Spark Room Kit Plus CE9.1.X': self.csco_12_3161_plus,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioOutput': {'Parameters': ['Output'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Status': {}},
            'CallSetupMode': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusRP': {'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFocus': {'Status': {}},
            'CameraFocusPlus': {'Parameters': ['Camera'], 'Status': {}},
            'CameraPan': {'Parameters': ['Speed'], 'Status': {}},
            'CameraPanPlus': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraPresetRecall': {'Status': {}},
            'CameraPresetSave': {'Status': {}},
            'CameraPresetSavePlus': {'Parameters': ['Camera'], 'Status': {}},
            'CameraTilt': {'Parameters': ['Speed'], 'Status': {}},
            'CameraTiltPlus': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Speed'], 'Status': {}},
            'CameraZoomPlus': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
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
            'H323GatekeeperAddress': {'Status': {}},
            'H323GatekeeperAddressCommand': {'Status': {}},
            'H323GatekeeperStatus': {'Status': {}},
            'H323ProfileAuthenticationLoginNameCommand': {'Status': {}},
            'H323ProfileAuthenticationPasswordCommand': {'Status': {}},
            'Hook': {'Parameters': ['Protocol'], 'Status': {}},
            'Input': {'Status': {}},
            'InputMicLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputSignal': {'Parameters': ['Input'], 'Status': {}},
            'IPAddress': {'Status': {}},
            'IPv4AddressCommand': {'Status': {}},
            'IPv4GatewayCommand': {'Status': {}},
            'IPv4SubnetMaskCommand': {'Status': {}},
            'LayoutSet': {'Parameters': ['Target'], 'Status': {}},
            'MACAddress': {'Status': {}},
            'MicrophonesMute': {'Status': {}},
            'NetworkAssignment': {'Status': {}},
            'PhonebookFolderIDNavigation': {'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': {'Status': {}},
            'PhonebookFolderIDUpdate': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
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
            'SleepTimer': {'Status': {}},
            'SpeakerTrackControl': {'Status': {}},
            'SpeakerTrackMode': {'Status': {}},
            'Standby': {'Status': {}},
            'SubnetMask': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n')
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

        self.NumberOfButton = 0
        self.MinLabel = 1
        self.MaxLabel = 5
        self.Offset = 0
        self.newList = {}
        self.dirName = compile('\*r PhonebookSearchResult Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r PhonebookSearchResult Contact (\d+) ContactMethod 1 Number: "(.+)"')

        self.FolderIDNumber = None
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

        self.startCallHist = 1
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')

        if self._CallHistoryOccurrenceType == 'Time':
            self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self.occurrenceCount = compile('Entry (\d+) Count: (\d+)\r\n')
        self.occurrenceType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')

        self.deviceName = None
        self.deviceType = None
        self.deviceID = None

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (InternalSpeaker|Line 1) Mode: (On|Off)\r\n'), self.__MatchAudioOutput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (Auto|Dual|Single|DualPresentationOnly)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Domain Name: "(.*)"'), self.__MatchDNSDomainName, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-5]) Address: "([0-9.]{0,15})"\r\n'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'\*s SystemUnit Software Version: "([\w.]+)"\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{0,15})"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{0,15})"\r\n'), self.__MatchH323GatekeeperAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoSource: ([1-4]|Composed)\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-3]) Level: (\d+)\r\n'), self.__MatchInputMicLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Microphone [1-3]|HDMI [1-2]) Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Video Input Connector ([1-2]) Connected: (True|False|Unknown)\r\n'), self.__MatchInputSignal, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{0,15})"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "([:0-9A-Z]{17})"\r\n\*\* end\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n\*\* end\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-3])\r\n'), self.__MatchPresentationSourceStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationSourceStatusStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (On|Off)\r\n'), self.__MatchPresentationModeStatus, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusStop, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Selfview Default FullscreenMode: (Off|On|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (UpperLeft|UpperCenter|UpperRight|CenterLeft|CenterRight|LowerLeft|LowerRight)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s SIP Registration 1 Status: (Deregister|Failed|Inactive|Registered|Registering)\r\n'), self.__MatchSIPRegistrationStatus, None)
            self.AddMatchString(compile(b'\*s Cameras SpeakerTrack Status: (Active|Inactive)\r\n\*\* end\r\n'), self.__MatchSpeakerTrackControl, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|EnteringStandby|Halfwake|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'\*c xConfiguration Cameras SpeakerTrack Mode: (Auto|Off)\r\n'), self.__MatchSpeakerTrackMode, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{0,15})"\r\n'), self.__MatchSubnetMask, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchVolume, None)

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
    def NumberofPhonebookSearch(self):
        return self._NumberofPhonebookSearch

    @NumberofPhonebookSearch.setter
    def NumberofPhonebookSearch(self, value):
        self._NumberofPhonebookSearch = value

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
    def NumberofPeripheral(self):
        return self._NumberofPeripheral

    @NumberofPeripheral.setter
    def NumberofPeripheral(self, value):
        self._NumberofPeripheral = value

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

        CallHistoryCmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CallHistoryCmdString, 3, deliTag=b'** end')
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

        res = self.SendAndWait('xstatus call\r', 1, deliTag=b'** end')
        if res:
            res = res.decode()
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

    def SetCameraFocus(self, value, qualifier):

        CameraFocusCmdString = ''
        if value in ['Far', 'Near', 'Stop']:
            CameraFocusCmdString = 'xCommand Camera Ramp CameraId:1 Focus:{0}\r'.format(value)
        elif value == 'Auto':
            CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:1\r'
        else:
            self.Discard('Invalid Command for SetCameraFocus')

        if CameraFocusCmdString:
            self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraFocusPlus(self, value, qualifier):

        CameraFocusPlusCmdString = ''
        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7 and value in ['Far', 'Near', 'Stop']:
            CameraFocusPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Focus:{1}\r'.format(camID, value)
        elif value == 'Auto':
            CameraFocusPlusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:{0}\r'.format(camID)
        else:
            self.Discard('Invalid Command for SetCameraFocusPlus')

        if CameraFocusPlusCmdString:
            self.__SetHelper('CameraFocusPlus', CameraFocusPlusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocusPlus')

    def SetCameraPan(self, value, qualifier):

        camSpeed = qualifier['Speed']
        CameraPanCmdString = ''
        if 1 <= camSpeed <= 15 and value in ['Left', 'Right', 'Stop']:
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan: Stop\r'
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan:{0} PanSpeed:{1}\r'.format(value, camSpeed)

            if CameraPanCmdString:
                self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPan')
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPanPlus(self, value, qualifier):

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        CameraPanPlusCmdString = ''
        if 1 <= int(camID) <= 7 and 1 <= camSpeed <= 15 and value in ['Left', 'Right', 'Stop']:
            if value == 'Stop':
                CameraPanPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Pan: Stop\r'.format(camID)
            else:
                CameraPanPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Pan:{1} PanSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraPanPlusCmdString:
                self.__SetHelper('CameraPanPlus', CameraPanPlusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPanPlus')
        else:
            self.Discard('Invalid Command for SetCameraPanPlus')

    def SetCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 35:
            CameraPresetRecallCmdString = 'xCommand Camera Preset Activate PresetId: {0}\r'.format(value)
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 35:
            CameraPresetSaveCmdString = 'xCommand Camera Preset Store PresetId:{0} CameraId:1\r'.format(value)
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraPresetSavePlus(self, value, qualifier):

        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7 and 1 <= int(value) <= 35:
            CameraPresetSavePlusCmdString = 'xCommand Camera Preset Store PresetId:{0} CameraId:{1}\r'.format(value, camID)
            self.__SetHelper('CameraPresetSavePlus', CameraPresetSavePlusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSavePlus')

    def SetCameraTilt(self, value, qualifier):

        camSpeed = qualifier['Speed']
        CameraTiltCmdString = ''
        if 1 <= int(camSpeed) <= 15 and value in ['Up', 'Down', 'Stop']:
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt: Stop\r'
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt:{0} TiltSpeed:{1}\r'.format(value, camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraTiltPlus(self, value, qualifier):

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        CameraTiltPlusCmdString = ''
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15 and value in ['Up', 'Down', 'Stop']:
            if value == 'Stop':
                CameraTiltPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt: Stop\r'.format(camID)
            else:
                CameraTiltPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt:{1} TiltSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraTiltPlusCmdString:
                self.__SetHelper('CameraTiltPlus', CameraTiltPlusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTiltPlus')
        else:
            self.Discard('Invalid Command for SetCameraTiltPlus')

    def SetCameraZoom(self, value, qualifier):

        camSpeed = qualifier['Speed']
        CameraZoomCmdString = ''
        if 1 <= int(camSpeed) <= 15 and value in ['In', 'Out', 'Stop']:
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom: Stop\r'
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom:{0} ZoomSpeed:{1}\r'.format(value, camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetCameraZoomPlus(self, value, qualifier):

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        CameraZoomPlusCmdString = ''
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15 and value in ['In', 'Out', 'Stop']:
            if value == 'Stop':
                CameraZoomPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom: Stop\r'
            else:
                CameraZoomPlusCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom:{1} ZoomSpeed:{2}\r'.format(camID, value, camSpeed)

            if CameraZoomPlusCmdString:
                self.__SetHelper('CameraZoomPlus', CameraZoomPlusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoomPlus')
        else:
            self.Discard('Invalid Command for SetCameraZoomPlus')

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
                for i in range(button, self._NumberofPeripheral + 1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button': button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button': button + 1})
        else:
            self.Discard('Invalid Command for SetConnectedDeviceNavigation')

    def SetConnectedDeviceUpdate(self, value, qualifier):
        self.Debug = True

        ConnectedDeviceUpdateCmdString = 'xStatus Peripherals ConnectedDevice\r'
        res = self.SendAndWait(ConnectedDeviceUpdateCmdString, 3, deliTag=b'** end')
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
            DisplayModeCmdString = 'xConfiguration Video Monitors: {0}\r'.format(value.replace(' ', ''))
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):

        DisplayModeCmdString = 'xConfiguration Video Monitors\r'
        self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        ValueStateValues = {
            'Auto': 'Auto',
            'Dual': 'Dual',
            'Single': 'Single',
            'DualPresentationOnly': 'Dual Presentation Only'
        }

        value = ValueStateValues[match.group(1).decode()]
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

        if 1 <= int(qualifier['Server']) <= 5:
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

        DTMFCmdString = 'xCommand Call DTMFSend DTMFString:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

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
            FarEndCameraPresetRecallCmdString = 'xCommand Call FarEndControl RoomPreset Activate:{0}\r'.format(value)
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

        FirmwareVersionCmdString = 'xStatus SystemUnit Software Version\r'
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

        H323String = value
        if H323String:
            H323AliasE164CommandCmdString = 'xConfiguration H323 H323Alias E164: {0}\r'.format(H323String)
            self.__SetHelper('H323AliasE164Command', H323AliasE164CommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasE164Command')

    def SetH323AliasIDCommand(self, value, qualifier):

        H323String = value
        if H323String:
            H323AliasIDCommandCmdString = 'xConfiguration H323 H323Alias ID: {0}\r'.format(H323String)
            self.__SetHelper('H323AliasIDCommand', H323AliasIDCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323AliasIDCommand')

    def UpdateH323GatekeeperAddress(self, value, qualifier):

        H323GatekeeperAddressCmdString = 'xStatus H323 Gatekeeper Address\r'
        self.__UpdateHelper('H323GatekeeperAddress', H323GatekeeperAddressCmdString, value, qualifier)

    def __MatchH323GatekeeperAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('H323GatekeeperAddress', value, None)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        H323String = value
        if H323String:
            H323GatekeeperAddressCommandCmdString = 'xConfiguration H323 Gatekeeper Address: {0}\r'.format(H323String)
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

        H323String = value
        if H323String:
            H323ProfileAuthenticationLoginNameCommandCmdString = 'xConfiguration H323 Authentication LoginName: {0}\r'.format(H323String)
            self.__SetHelper('H323ProfileAuthenticationLoginNameCommand', H323ProfileAuthenticationLoginNameCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323ProfileAuthenticationLoginNameCommand')

    def SetH323ProfileAuthenticationPasswordCommand(self, value, qualifier):

        H323String = value
        if H323String:
            H323ProfileAuthenticationPasswordCommandCmdString = 'xConfiguration H323 Authentication Password: {0}\r'.format(H323String)
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
        elif value == 'Dial':
            number = qualifier['Number']
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

    def SetInputMicLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 24
        }

        input_ = self.InputMicLevelStates[qualifier['Input']]
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputMicLevelCmdString = 'xConfiguration Audio Input {0} Level:{1}\r'.format(input_, value)
            self.__SetHelper('InputMicLevel', InputMicLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLevel')

    def UpdateInputMicLevel(self, value, qualifier):

        input_ = self.InputMicLevelStates[qualifier['Input']]
        InputMicLevelCmdString = 'xConfiguration Audio Input {0} Level\r'.format(input_)
        self.__UpdateHelper('InputMicLevel', InputMicLevelCmdString, value, qualifier)

    def __MatchInputMicLevel(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('InputMicLevel', value, {'Input': match.group(1).decode()})

    def SetInputMute(self, value, qualifier):

        input_ = self.InputMuteStates[qualifier['Input']]
        if value in ['On', 'Off']:
            InputMuteCmdString = 'xConfiguration Audio Input {0} Mode:{1}\r'.format(input_, value)
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        input_ = self.InputMuteStates[qualifier['Input']]
        InputMuteCmdString = 'xConfiguration Audio Input {0} Mode\r'.format(input_)
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

        IPv4String = value
        if IPv4String:
            IPv4AddressCommandCmdString = 'xConfiguration Network 1 IPv4 Address: {0}\r'.format(IPv4String)
            self.__SetHelper('IPv4AddressCommand', IPv4AddressCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4AddressCommand')

    def SetIPv4GatewayCommand(self, value, qualifier):

        IPv4String = value
        if IPv4String:
            IPv4GatewayCommandCmdString = 'xConfiguration Network 1 IPv4 Gateway: {0}\r'.format(IPv4String)
            self.__SetHelper('IPv4GatewayCommand', IPv4GatewayCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIPv4GatewayCommand')

    def SetIPv4SubnetMaskCommand(self, value, qualifier):

        IPv4String = value
        if IPv4String:
            IPv4SubnetMaskCommandCmdString = 'xConfiguration Network 1 IPv4 SubnetMask: {0}\r'.format(IPv4String)
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

    def SetMicrophonesMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'Unmute'
        }

        MicrophonesMuteCmdString = 'xCommand Audio Microphones {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def UpdateMicrophonesMute(self, value, qualifier):

        MicrophonesMuteCmdString = 'xStatus Audio Microphones\r'
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

    def SetPhonebookFolderIDNavigation(self, value, qualifier):
        self.Debug = True

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
            for i in range(self.FolderMin, self.FolderLimit + 1):
                if str(i) in self.folderList:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {'Button': button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDNavigation')

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
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {'Button': int(i)})
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

                if self.MaxLabel > len(self.newList) and len(self.newList) == self._NumberofContactsPerSearch:
                    self.SetPhonebookUpdate('Next Search', qualifier)

                self.SetPhonebookWriteHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

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
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1}SearchField: Name ContactType: Contact {2} Offset: {3} Limit: {4}\r'.format(
                phonebookType, contact, fldID, self.Offset, self._NumberofContactsPerSearch)
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
                                 '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']),{'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

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
        inputSource = qualifier['Video Input Source']
        sendingMode = qualifier['Sending Mode']
        instanceID = qualifier['Instance']
        cmdState = ''
        if 'Stop' == value:
            cmdState = 'xCommand Presentation Stop{0}{1}\r'.format(instanceState[instanceID], self.InputSourceStates[inputSource])
        elif 'Start' == value:
            cmdState = 'xCommand Presentation Start{0}{1}{2}\r'.format(instanceState[instanceID], sendingModeStates[sendingMode], self.InputSourceStates[inputSource])
        if cmdState:
            self.__SetHelper('Presentation', cmdState, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):

        sourceValue = 'string'
        if sourceValue:
            cmdstring = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{0}"\r'.format(sourceValue)
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
        if value == '0':
            value = 'Stop'
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

        if value in ['Activate', 'Deactivate']:
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

    def csco_12_3161_non_plus(self):

        self.AudioOutputStates = {
            'Internal Speaker': 'InternalSpeaker',
            'Line': 'Line 1'
        }

        self.AudioOutputValues = {
            'InternalSpeaker': 'Internal Speaker',
            'Line 1': 'Line'
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

    def csco_12_3161_plus(self):

        self.AudioOutputStates = {
            'Internal Speaker': 'InternalSpeaker'
        }

        self.AudioOutputValues = {
            'InternalSpeaker': 'Internal Speaker'
        }

        self.InputMicLevelStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteStates = {
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3'
        }

        self.InputMuteValues = {
            'HDMI 1': 'HDMI 1',
            'HDMI 2': 'HDMI 2',
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

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################
        # Send Control Commands

    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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

    def __init__(self, Hostname, IPPort, Protocol='SSH', ServicePort=0, Credentials=(None),
                Model=None):
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