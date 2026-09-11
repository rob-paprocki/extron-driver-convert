from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search
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
        
        self.deviceUsername = 'admin'
        self.devicePassword = 'TANDBERG'
        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPhonebookSearch = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofPeripheral = 5
        self._NumberofContactsPerSearch = 50
        self._NumberofFoldersPerSearch = 50

        self.Debug = False

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Status': {}},
            'CallSetupMode': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFocus': {'Status': {}},
            'CameraPan': {'Parameters': ['Speed'], 'Status': {}},
            'CameraPresetRecall': {'Status': {}},
            'CameraPresetSave': {'Status': {}},
            'CameraTilt': {'Parameters': ['Speed'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Speed'], 'Status': {}},
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
            'DNSServerAddressCommand': {'Parameters': ['Server'], 'Status': {}},
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
            'Hook': {'Parameters': ['Number', 'Protocol'], 'Status': {}},
            'Input': {'Status': {}},
            'InputMicLevel': {'Parameters': ['Microphone'], 'Status': {}},
            'InputMute': {'Status': {}},
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
            'PhonebookFolderIDUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Contact', 'FolderID', 'Phonebook Type'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Contact', 'FolderID', 'Phonebook Type'], 'Status': {}},
            'Presentation': {'Parameters': ['Instance'], 'Status': {}},
            'PresentationExternalSourceSelectCommand': {'Status': {}},
            'PresentationMode': {'Status': {}},
            'PresentationSendingMode': {'Parameters': ['Connector ID'], 'Status': {}},
            'PresentationSendingModeStatus': {'Parameters': ['Instance'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Reboot': {'Status': {}},
            'RemoteNumber': {'Parameters': ['Call'], 'Status': {}},
            'SelfView': {'Status': {}},
            'SelfViewDefaultFullscreenMode': {'Status': {}},
            'SelfViewPosition': {'Status': {}},
            'SIPRegistrationStatus': {'Status': {}},
            'SleepTimer': {'Status': {}},
            'Standby': {'Status': {}},
            'SubnetMask': {'Status': {}},
            'Volume': {'Status': {}}
            }

        self.callStatus = compile('\*s Call \d+ Status: (\w+)\r\n')
        self.callStatusTypePattern = compile('\*s Call \d+ CallType: (Video|Audio|AudioCanEscalate|ForwardAllCall|Unknown)\r\n')
        self.displayNamePattern = compile('\*s Call \d+ DisplayName: "(.*)"\r\n')
        self.remoteNumberPattern = compile('\*s Call \d+ RemoteNumber: "(.*)"\r\n')
        self.callID = compile('\*s Call (\d+) Status: \w+\r\n')
        self.__LastCallStatus = 0
        self.__CallID = []

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

        self.startCallHist = 1
        self.callBackNumber = compile('Entry (\d+) CallbackNumber: "([^"]*)"\r\n')
        self.displayName = compile('Entry (\d+) DisplayName: "([^"]*)"\r\n')
        if self._CallHistoryOccurrenceType == 'Time':
             self.lastOccurrenceTime = compile('Entry (\d+) LastOccurrenceStartTime: "([^"]*)"\r\n')
             self._CallHistoryOccurrenceTypeCount = compile('Entry (\d+) OccurrenceCount: (\d+)\r\n')
        else:
            self.lastOccurrenceTime = compile('Entry (\d+) StartTime: "([^"]*)"\r\n')
            self._CallHistoryOccurrenceTypeCount = compile('Entry (\d+) Count: (\d+)\r\n')
        self._CallHistoryOccurrenceTypeType = compile('Entry (\d+) OccurrenceType: (\w*)\r\n')

        self.lastCallHist = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*c xConfiguration Conference AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (\w+)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Domain Name: "(.*)"'), self.__MatchDNSDomainName, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-5]) Address: "([0-9.]{7,15})"\r\n'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'\*s SystemUnit Software Version: "([\w\.]+)"\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{7,15})"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Address: "([0-9.]{7,15})"\r\n'), self.__MatchH323GatekeeperAddress, None)
            self.AddMatchString(compile(b'\*s H323 Gatekeeper Status: (Required|Discovering|Discovered|Authenticating|Authenticated|Registering|Registered|Inactive|Rejected)\r\n'), self.__MatchH323GatekeeperStatus, None)
            self.AddMatchString(compile(b'\*s Video Input MainVideoSource: ([1-5])\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input Microphone ([23]) Level: (\d+)\r\n'), self.__MatchInputMicLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input Microphone 1 Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Video Input Connector ([12]) Connected: (True|False|Unknown)\r\n'), self.__MatchInputSignal, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{7,15})"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "([:0-9A-Z]{17})"\r\n\*\* end\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n\*\* end\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) Source: ([0-5])\r\n'), self.__MatchPresentation, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/Source"\r\n'), self.__MatchPresentationStop, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationMode, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalInstance ([1-6]) SendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingModeStatus, None)
            self.AddMatchString(compile(b'\*r Status XPath: "Status/Conference/Presentation/LocalInstance\[([1-6])\]/SendingMode"\r\n'), self.__MatchPresentationSendingModeStatusStop, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Selfview Default FullscreenMode: (Off|On|Current)\r\n'), self.__MatchSelfViewDefaultFullscreenMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (UpperLeft|UpperCenter|UpperRight|CenterLeft|CenterRight|LowerLeft|LowerRight)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s SIP Registration 1 Status: (Deregister|Failed|Inactive|Registered|Registering)\r\n'), self.__MatchSIPRegistrationStatus, None)
            self.AddMatchString(compile(b'\*s Standby State: (Standby|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{7,15})"\r\n'), self.__MatchSubnetMask, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchVolume, None)

            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)

            self.AddMatchString(compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchAuthentication, None)

    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):
        self._CallHistoryOccurrenceType = value

    @property
    def NumberofCallHistory(self):
        return self._NumberofCallHistory

    @NumberofCallHistory.setter
    def NumberofCallHistory(self, value):
        self._NumberofCallHistory = value

    @property
    def NumberofPeripheral(self):
        return self._NumberofPeripheral

    @NumberofPeripheral.setter
    def NumberofPeripheral(self, value):
        self._NumberofPeripheral = value

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

    @property
    def PhonebookSearchOffset(self):
        return self._PhonebookSearchOffset

    @PhonebookSearchOffset.setter
    def PhonebookSearchOffset(self, value):
        self._PhonebookSearchOffset = value

    def __MatchAuthentication(self, match, tag):
        self.SetAuthentication(None, None)

    def SetAuthentication(self, value, qualifier):
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

    def SetAutoAnswer(self, value, qualifier):

        States = {
            'On': 'On',
            'Off': 'Off'
        }
        CmdString = 'xConfiguration Conference AutoAnswer Mode: {0}\r'.format(States[value])
        self.__SetHelper('AutoAnswer', CmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):
        self.__UpdateHelper('AutoAnswer', 'xConfiguration Conference AutoAnswer Mode\r', qualifier)

    def __MatchAutoAnswer(self, match, tag):
        self.WriteStatus('AutoAnswer', match.group(1).decode(), None)

    def SetCallHistoryRefresh(self, value, qualifier):
        self.Debug = True
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        self.Debug = True
        CmdString = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(CmdString, 3, deliTag='** end')
        if res:
            displayNameList = dict(findall(self.displayName, res))
            callBackNumberList = dict(findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(findall(self._CallHistoryOccurrenceTypeType, res))
            occurrenceCountList = dict(findall(self._CallHistoryOccurrenceTypeCount, res))

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
            self.Discard('Invalid Command for SetCallHistoryNavigation')

    def SetCallHistorySelect(self, value, qualifier):
        self.Debug = True

        if 1 <= int(value) <= 20:
            number = self.ReadStatus('CallHistory', {'Button': value, 'Detail Type': 'Callback Number'})
            if number:
                self.Send('xCommand Dial Number:"{0}"\r'.format(number))
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')

    def SetCallSetupMode(self, value, qualifier):

        States = {
            'Gatekeeper': 'Gatekeeper',
            'Direct': 'Direct'
        }

        CmdString = 'xConfiguration H323 CallSetup Mode: {0}\r'.format(States[value])
        self.__SetHelper('CallSetupMode', CmdString, value, qualifier)

    def UpdateCallSetupMode(self, value, qualifier):
        CmdString = 'xConfiguration H323 CallSetup Mode\r'
        self.__UpdateHelper('CallSetupMode', CmdString, qualifier)

    def __MatchCallSetupMode(self, match, tag):
        States = {
            'Gatekeeper': 'Gatekeeper',
            'Direct': 'Direct'
        }
        self.WriteStatus('CallSetupMode', value, None)

    def UpdateCallStatus(self, value, qualifier):
        self.__UpdateHelper('CallStatusRP', 'xstatus call\r', qualifier)
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


    def SetCameraFocus(self, value, qualifier):

        if value in ['Far', 'Near', 'Stop', 'Auto']:
            if value == 'Auto':
                CmdString = 'xCommand Camera TriggerAutoFocus CameraId:1\r'
            else:
                CmdString = 'xCommand Camera Ramp CameraId:1 Focus:{0}\r'.format(value)
            self.__SetHelper('CameraFocus', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        States = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop',
        }

        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CmdString = 'xCommand Camera Ramp CameraId:1 Pan: Stop\r'
            else:
                CmdString = 'xCommand Camera Ramp CameraId:1 Pan:{0} PanSpeed:{1}\r'.format(States[value],camSpeed)
            self.__SetHelper('CameraPan', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPan')


    def SetCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetRecall', 'xCommand Camera Preset Activate PresetId: {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')
        

    def SetCameraPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 35:
            self.__SetHelper('CameraPresetSave', 'xCommand Camera Preset Store PresetId:{0} CameraId:1\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraTilt(self, value, qualifier):

        States = {
            'Up'  : 'Up',
            'Down': 'Down',
            'Stop': 'Stop',
        }

        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CmdString = 'xCommand Camera Ramp CameraId:1 Tilt:Stop\r'
            else:
                CmdString = 'xCommand Camera Ramp CameraId:1 Tilt:{0} TiltSpeed:{1}\r'.format(States[value],camSpeed)
            self.__SetHelper('CameraTilt', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraTilt')


    def SetCameraZoom(self, value, qualifier):

        States = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop',
        }

        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            if value == 'Stop':
                CmdString = 'xCommand Camera Ramp CameraId:1 Zoom: Stop\r'
            else:
                CmdString = 'xCommand Camera Ramp CameraId:1 Zoom:{0} ZoomSpeed:{1}\r'.format(States[value],camSpeed)
            self.__SetHelper('CameraZoom', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraZoom')


    def SetConnectedDeviceUpdate(self, value, qualifier):
        self.Debug = True

        res = self.SendAndWait( 'xStatus Peripherals ConnectedDevice\r' , 5, deliTag='** end')
        if res:
            self.deviceName = findall(self.peripheralName, res)
            self.deviceType = findall(self.peripheralType, res)
            self.deviceID = findall(self.peripheralMAC, res)
            self.MaxDevices = len(self.deviceName)

            for button in range(0, self._NumberofPeripheral):
                if button < self.MaxDevices:
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[button], {'Button':button+1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[button], {'Button':button+1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[button], {'Button':button+1})
                else:
                    self.WriteStatus('ConnectedDeviceName', '***End of List***', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceType', '***End of List***', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', '***End of List***', {'Button':button + 1})
                    button += 1
                    self.WriteStatus('ConnectedDeviceName', '', {'Button':button+1})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button':button+1})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button':button+1})

    def SetConnectedDeviceNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
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
            for i in range(self.startPeripheral, self.startPeripheral + self._NumberofPeripheral):
                if 0 <= i < self.MaxDevices:
                    self.WriteStatus('ConnectedDeviceName', self.deviceName[i], {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceType', self.deviceType[i], {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', self.deviceID[i], {'Button':button + 1})
                    button += 1

            if button <= self._NumberofPeripheral:
                self.WriteStatus('ConnectedDeviceName', '***End of List***', {'Button':button + 1})
                self.WriteStatus('ConnectedDeviceType', '***End of List***', {'Button':button + 1})
                self.WriteStatus('ConnectedDeviceMAC', '***End of List***', {'Button':button + 1})
                button += 1
                for i in range(button, self._NumberofPeripheral + 1):
                    self.WriteStatus('ConnectedDeviceName', '', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceType', '', {'Button':button + 1})
                    self.WriteStatus('ConnectedDeviceMAC', '', {'Button':button + 1})
        else:
            self.Discard('Invalid Command for SetConnectedDeviceNavigation')

    def SetDisplayMode(self, value, qualifier):

        States = {
            'Auto'  :   'Auto',
            'Dual Presentation Only'  :   'DualPresentationOnly',
            }
                
        CmdString = 'xConfiguration Video Monitors: {0}\r'.format(States[value])
        self.__SetHelper('DisplayMode', CmdString, value, qualifier)

    def UpdateDisplayMode(self, value, qualifier):
        self.__UpdateHelper('DisplayMode', 'xConfiguration Video Monitors\r', qualifier)

    def __MatchDisplayMode(self, match, tag):
        States = {
            'Auto'  :   'Auto',
            'DualPresentationOnly'  :   'Dual Presentation Only',
            }
        self.WriteStatus('DisplayMode', States[match.group(1).decode()], None)

    def UpdateDNSDomainName(self, value, qualifier):
        self.__UpdateHelper('DNSDomainName', 'xStatus Network 1 DNS Domain Name\r' , qualifier)

    def __MatchDNSDomainName(self, match, tag):
        self.WriteStatus('DNSDomainName',  match.group(1).decode() , None)

    def SetDNSDomainNameCommand(self, value, qualifier):
        if value:
            CommandString = 'xConfiguration Network 1 DNS Domain Name: {0}\r'.format(value)
            self.__SetHelper('DNSDomainNameCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSDomainNameCommand')

    def UpdateDNSServerAddress(self, value, qualifier):

        server = qualifier['Server']
        if 1 <= int(server) <= 3:
            self.__UpdateHelper('DNSServerAddress', 'xStatus Network 1 DNS Server {0} Address\r'.format(server) , qualifier)
        else:
            self.Discard('Invalid Command for UpdateDNSServerAddress')

    def __MatchDNSServerAddress(self, match, tag):
        self.WriteStatus('DNSServerAddress',  match.group(2).decode() , {'Server': match.group(1).decode() })

    def SetDNSServerAddressCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration Network 1 DNS Server 1 Address: {0}\r'.format(value)
            self.__SetHelper('DNSServerAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDNSServerAddressCommand')

    def SetDoNotDisturb(self, value, qualifier):

        States = {
            'Active'    :   'Activate',
            'Inactive'  :   'Deactivate',
            }
        CmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(States[value])
        self.__SetHelper('DoNotDisturb', CmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):
        self.__UpdateHelper('DoNotDisturb', 'xStatus Conference DoNotDisturb\r', qualifier)

    def __MatchDoNotDisturb(self, match, tag):        
        States = {
            'Active':'Active',
            'Inactive':'Inactive',
            }
        self.WriteStatus('DoNotDisturb', States[match.group(1).decode()], None)

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

        CmdString = 'xCommand Call DTMFSend DTMFString:{0}\r'.format(DTMFValues[value])
        self.__SetHelper('DTMF', CmdString, value, qualifier)

    def SetFarEndControl(self, value, qualifier):

        States = {
            'On'   :   'On',
            'Off'  :   'Off'
            }
        CmdString = 'xConfiguration Conference FarEndControl Mode: {0}\r'.format(States[value])
        self.__SetHelper('FarEndControl', CmdString, value, qualifier)

    def UpdateFarEndControl(self, value, qualifier):
        self.__UpdateHelper('FarEndControl', 'xConfiguration Conference FarEndControl Mode\r', qualifier)

    def __MatchFarEndControl(self, match, tag):        
        self.WriteStatus('FarEndControl', match.group(1).decode(), None)

    def SetFarEndCameraPanTilt(self, value, qualifier):

        States = {
            'Left'  :   'Left',
            'Right' :   'Right',
            'Up'    :   'Up',
            'Down'  :   'Down',
            }
        if value == 'Stop':
            CmdString = 'xCommand Call FarEndControl Camera Stop\r'
        else:                        
            CmdString = 'xCommand Call FarEndControl Camera Move Value:{0}\r'.format(States[value])
        self.__SetHelper('FarEndCameraPanTilt', CmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl RoomPreset Activate:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraSource(self, value, qualifier):

        if 0 <= int(value) <= 15:
            CmdString = 'xCommand Call FarEndControl Source Select SourceId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraSource', CmdString, value, qualifier)
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
        self.__UpdateHelper('FirmwareVersion', 'xStatus SystemUnit Software Version\r' , qualifier)

    def __MatchFirmwareVersion(self, match, tag):
        self.WriteStatus('FirmwareVersion',  match.group(1).decode() , None)

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

    def UpdateH323GatekeeperAddress(self, value, qualifier):
        self.__UpdateHelper('H323GatekeeperAddress', 'xStatus H323 Gatekeeper Address\r' , qualifier)

    def __MatchH323GatekeeperAddress(self, match, tag):
        self.WriteStatus('H323GatekeeperAddress',  match.group(1).decode() , None)

    def SetH323GatekeeperAddressCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 Gatekeeper Address: {0}\r'.format(value)
            self.__SetHelper('H323GatekeeperAddressCommand', CommandString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetH323GatekeeperAddressCommand')


    def UpdateH323GatekeeperStatus(self, value, qualifier):
        self.__UpdateHelper('H323GatekeeperStatus', 'xStatus H323 Gatekeeper Status\r' , qualifier)

    def __MatchH323GatekeeperStatus(self, match, tag):

        States = {
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

        self.WriteStatus('H323GatekeeperStatus',  States[match.group(1).decode()] , None)

    def SetH323ProfileAuthenticationLoginNameCommand(self, value, qualifier):

        if value:
            CommandString = 'xConfiguration H323 Authentication LoginName: {0}\r'.format(value)
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

    def SetInput(self, value, qualifier):

        States = {
            '1'  :   '1',
            '2'  :   '2',
            '3'  :   '3',
            '4'  :   '4',
            '5'  :   '5'
            }

        self.__SetHelper('Input', 'xCommand Video Input SetMainVideoSource ConnectorId: {0}\r'.format(States[value]), value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', 'xStatus Video Input MainVideoSource\r', qualifier)

    def __MatchInput(self, match, tag):        
        self.WriteStatus('Input', match.group(1).decode(), None)

    def SetInputMicLevel(self, value, qualifier):

        States = {
            '2'  :   '2',
            '3'  :   '3', 
        }

        if 0 <= value <= 24:
            self.__SetHelper('InputMicLevel', 'xConfiguration Audio Input Microphone {0} Level:{1}\r'.format(States[qualifier['Microphone']], value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMicLevel')

    def UpdateInputMicLevel(self, value, qualifier):

        States = {
            '2': '2',
            '3': '3',
        }

        self.__UpdateHelper('InputMicLevel', 'xConfiguration Audio Input Microphone {0} Level\r'.format(States[qualifier['Microphone']]), qualifier)

    def __MatchInputMicLevel(self, match, tag):        
        self.WriteStatus('InputMicLevel',  int(match.group(2).decode()) , { 'Microphone' : match.group(1).decode() })

    def SetInputMute(self, value, qualifier):

        States = {
            'On'  :   'On',
            'Off'  :   'Off',
        }

        self.__SetHelper('InputMute', 'xConfiguration Audio Input 1 Mode:{}\r'.format(States[value]), value, qualifier)

    def UpdateInputMute(self, value, qualifier):
        self.__UpdateHelper('InputMute', 'xConfiguration Audio Input 1 Mode\r', qualifier)

    def __MatchInputMute(self, match, tag):        
        self.WriteStatus('InputMute', match.group(1).decode(), None)

    def UpdateInputSignal(self, value, qualifier):

        input_ = qualifier['Input']
        if 1 <= int(input_) <= 2:
            self.__UpdateHelper('InputSignal', 'xStatus Video Input Connector {0} Connected\r'.format(input_), qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputSignal')

    def __MatchInputSignal(self, match, tag):
        self.WriteStatus('InputSignal', match.group(2).decode(), {'Input':match.group(1).decode()})

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

    def UpdateGatewayAddress(self, value, qualifier):
        self.__UpdateHelper('GatewayAddress', 'xStatus Network 1 IPv4 Gateway\r' , qualifier)

    def __MatchGatewayAddress(self, match, tag):
        self.WriteStatus('GatewayAddress',  match.group(1).decode() , None)

    def UpdateIPAddress(self, value, qualifier):
        self.__UpdateHelper('IPAddress', 'xStatus Network 1 IPv4 Address\r' , qualifier)

    def __MatchIPAddress(self, match, tag):
        self.WriteStatus('IPAddress',  match.group(1).decode() , None)

    def UpdateSubnetMask(self, value, qualifier):
        self.__UpdateHelper('SubnetMask', 'xStatus Network 1 IPv4 SubnetMask\r' , qualifier)

    def __MatchSubnetMask(self, match, tag):
        self.WriteStatus('SubnetMask',  match.group(1).decode() , None)

    def SetLayoutSet(self, value, qualifier):

        TargetStates = {
            'Local' : 'Local', 
            'Remote' : 'Remote'
        }

        States = {
            'Auto' : 'auto', 
            'Custom' : 'custom', 
            'Equal' : 'equal', 
            'Overlay' : 'overlay', 
            'Prominent' : 'prominent', 
            'Single' : 'single'
        }
        
        targetValue = TargetStates[qualifier['Target']]
        if targetValue:
            CmdString = 'xCommand Video Layout LayoutFamily Set Target: {0} LayoutFamily:{1}\r'.format(targetValue, States[value])
            self.__SetHelper('LayoutSet', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayoutSet')

    def SetMicrophonesMute(self, value, qualifier):

        States = {
            'On':'Mute',
            'Off':'UnMute',
            }
        self.__SetHelper('MicrophonesMute', 'xCommand Audio Microphones {0}\r'.format(States[value]) , value, qualifier)
    def UpdateMicrophonesMute(self, value, qualifier):
        self.__UpdateHelper('MicrophonesMute', 'xStatus Audio Microphones\r', qualifier)

    def __MatchMicrophonesMute(self, match, tag):
        
        self.WriteStatus('MicrophonesMute', match.group(1).decode(), None)

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        if value < 1 or value > self._NumberofPhonebookSearch:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number is not None and number != '***End of list***':
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
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']),{'Button': button})
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

        folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
        if folderName != '***End of list***' and folderName is not None:
            self.FolderIDNumber = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName][0]

    def SetPhonebookFolderIDUpdate(self, value, qualifier):
        self.Debug = True

        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: {1}\r'.format(phonebookValue,self._NumberofFoldersPerSearch)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
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
                fldID = 'FolderID: "{0}" '.format(folderID)
            else:
                fldID = ''
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} {1}SearchField: Name ContactType: Contact {2} Offset: {3} Limit: {4}\r'.format(phonebookType, contact, fldID, self.Offset, self._NumberofContactsPerSearch)
            res = self.SendAndWait(cmdStr, 10, deliTag=b'** end')
            if res:
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
                self.WriteStatus('PhonebookSearchResult', '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']),{'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPresentation(self, value, qualifier):

        States = {
            '1'  :   '1',
            '2'  :   '2',
            '3'  :   '3',
            '4'  :   '4',
            'Stop'  :   'Stop',
            }

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
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
        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            self.__UpdateHelper('Presentation', 'xStatus Conference Presentation LocalInstance {0} Source\r'.format(instanceID), qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentation')

    def __MatchPresentation(self, match, tag):
        instanceID = match.group(1).decode()
        value = match.group(2).decode()
        if value == '0':
            value = 'Stop'
        self.WriteStatus('Presentation', value, {'Instance':instanceID})

    def __MatchPresentationStop(self, match, tag):
        instanceID = match.group(1).decode()
        self.WriteStatus('Presentation', 'Stop', {'Instance':instanceID})

    def SetPresentationExternalSourceSelectCommand(self, value, qualifier):
        if value:
            Cmdstring = 'xCommand UserInterface Presentation ExternalSource Select SourceIdentifier: "{}"\r'.format(value)
            self.__SetHelper('PresentationExternalSourceSelectCommand', Cmdstring, value, qualifier)

    def UpdatePresentationMode(self, value, qualifier):
        self.__UpdateHelper('PresentationMode', 'xStatus Conference Presentation Mode\r' , qualifier)

    def __MatchPresentationMode(self, match, tag):
        self.WriteStatus('PresentationMode',  match.group(1).decode() , None)

    def SetPresentationSendingMode(self, value, qualifier):

        States = {
            'Local and Remote' : 'LocalRemote',
            'Local Only' : 'LocalOnly'
        }

        connectorID = int(qualifier['Connector ID'])
        if 1 <= connectorID <= 2:
            Cmdstring = 'xCommand Presentation Start SendingMode: {0} connectorID: {1}\r'.format(States[value], connectorID)
            self.__SetHelper('PresentationSendingMode', Cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentationSendingMode')

    def UpdatePresentationSendingModeStatus(self, value, qualifier):

        instanceID = qualifier['Instance']
        if 1 <= int(instanceID) <= 6:
            Cmdstring = 'xStatus Conference Presentation LocalInstance {0} SendingMode\r'.format(instanceID)
            self.__UpdateHelper('PresentationSendingModeStatus', Cmdstring, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePresentationSendingModeStatus')

    def __MatchPresentationSendingModeStatus(self, match, tag):

        States = {
            'LocalRemote' : 'Local and Remote', 
            'LocalOnly' : 'Local Only',
            'Off' : 'Off',
        }

        self.WriteStatus('PresentationSendingModeStatus', States[match.group(2).decode()], {'Instance':match.group(1).decode()})

    def __MatchPresentationSendingModeStatusStop(self, match, tag):
        self.WriteStatus('PresentationSendingModeStatus', 'Off', {'Instance':match.group(1).decode()})

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            Cmdstring = 'xCommand RoomPreset Activate PresetId:{0}\r'.format(value)
            self.__SetHelper('PresetRecall', Cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 15:
            Cmdstring = 'xCommand RoomPreset Store PresetId:{0} Type:All\r'.format(value)
            self.__SetHelper('PresetSave', Cmdstring, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetReboot(self, value, qualifier):
        self.__SetHelper('Reboot', 'xCommand SystemUnit Boot Action:Restart\r', value, qualifier)

    def SetSelfViewDefaultFullscreenMode(self, value, qualifier):

        States = {
            'On'        : 'On', 
            'Off'       : 'Off', 
            'Current'   : 'Current'
        }

        Cmdstring = 'xConfiguration Video Selfview Default FullscreenMode:{0}\r'.format(States[value])
        self.__SetHelper('SelfViewDefaultFullscreenMode', Cmdstring, value, qualifier)
    def UpdateSelfViewDefaultFullscreenMode(self, value, qualifier):
        self.__UpdateHelper('SelfViewDefaultFullscreenMode', 'xConfiguration Video Selfview Default FullscreenMode\r' , qualifier)

    def __MatchSelfViewDefaultFullscreenMode(self, match, tag):

        States = {
            'On' : 'On', 
            'Off' : 'Off', 
            'Current' : 'Current'
        }

        self.WriteStatus('SelfViewDefaultFullscreenMode',  States[match.group(1).decode()] , None)

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

        States = {
            'Upper Left'    : 'UpperLeft', 
            'Upper Center'  : 'UpperCenter', 
            'Upper Right'   : 'UpperRight', 
            'Center Left'   : 'CenterLeft', 
            'Center Right'  : 'CenterRight', 
            'Lower Left'    : 'LowerLeft', 
            'Lower Right'   : 'LowerRight'
        }

        self.__SetHelper('SelfViewPosition', 'xCommand Video Selfview Set PIPPosition:{0}\r'.format(States[value]) , value, qualifier)

    def UpdateSelfViewPosition(self, value, qualifier):
        self.__UpdateHelper('SelfViewPosition', 'xStatus Video Selfview PIPPosition\r', qualifier)

    def __MatchSelfViewPosition(self, match, tag):        

        States = {
            'UpperLeft'    : 'Upper Left', 
            'UpperCenter'  : 'Upper Center', 
            'UpperRight'   : 'Upper Right', 
            'CenterLeft'   : 'Center Left', 
            'CenterRight'  : 'Center Right', 
            'LowerLeft'    : 'Lower Left', 
            'LowerRight'   : 'Lower Right'
        }
        self.WriteStatus('SelfViewPosition', States[match.group(1).decode()], None)

    def UpdateSIPRegistrationStatus(self, value, qualifier):
        self.__UpdateHelper('SIPRegistrationStatus', 'xStatus SIP Registration 1 Status\r', qualifier)

    def __MatchSIPRegistrationStatus(self, match, tag):

        States = {
            'Deregister' : 'Deregistering', 
            'Failed' : 'Failed', 
            'Inactive' : 'Inactive', 
            'Registered' : 'Registered', 
            'Registering' : 'Registering'
        }

        self.WriteStatus('SIPRegistrationStatus',  States[match.group(1).decode()] , None)

    def SetSleepTimer(self, value, qualifier):

        if 1 <= value <= 480:
            self.__SetHelper('SleepTimer', 'xCommand Standby ResetTimer Delay:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTimer')


    def SetStandby(self, value, qualifier):

        if value in ['Active','Deactivate']:
            CmdString = 'xCommand Standby {0}\r'.format(value)
            self.__SetHelper('Standby', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetStandby')

    def UpdateStandby(self, value, qualifier):
        self.__UpdateHelper('Standby', 'xStatus Standby State\r', qualifier)

    def __MatchStandby(self, match, tag):
        States = {
            'Off':'Deactivate',
            'Standby':'Activate',
            }

        self.WriteStatus('Standby',  States[match.group(1).decode()] , None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            self.__SetHelper('Volume', 'xCommand Audio Volume Set Level:{0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'xStatus Audio Volume\r', qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume',  int(match.group(1)) , None)

    def UpdateMACAddress(self, value, qualifier):
        self.__UpdateHelper('MACAddress', 'xStatus Network 1 Ethernet MacAddress\r' , qualifier)

    def __MatchMACAddress(self, match, tag):        
        self.WriteStatus('MACAddress',  match.group(1).decode() , None)

    def UpdateNetworkAssignment(self, value, qualifier):
        self.__UpdateHelper('NetworkAssignment', 'xConfiguration Network 1 IPv4 Assignment\r' , qualifier)

    def __MatchNetworkAssignment(self, match, tag):

        States = {
            'Static' : 'Static', 
            'DHCP' : 'DHCP'
        }
        
        self.WriteStatus('NetworkAssignment',  States[match.group(1).decode()] , None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True


        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, qualifier):
        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command. Unidirectional mode.')
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
            print(command, 'does not exist in the module')

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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}                

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