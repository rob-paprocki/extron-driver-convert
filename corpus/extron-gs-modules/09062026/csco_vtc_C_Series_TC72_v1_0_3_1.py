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

        self.deviceUsername = 'admin'
        self.devicePassword = 'TANDBERG'
        self._CallHistoryOccurrenceType = 'Time'
        self._NumberofCallHistory = 5
        self._NumberofPhonebookFolderSearch = 5
        self._NumberofPhonebookSearch = 5
        self._NumberofContactsPerSearch = 50
        self._NumberofFoldersPerSearch = 50

        self.Models = {
            'C20 TC7.2.X': self.csco_12_2062_C20,
            'C40 TC7.2.X': self.csco_12_2062_C40,
            'C60 TC7.2.X': self.csco_12_2062_C60,
            'C90 TC7.2.X': self.csco_12_2062_C90,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AssignLocalOutput': {'Parameters': ['Layout ID', 'Output ID'], 'Status': {}},
            'AudioOutput': {'Parameters': ['Output'], 'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallHistory': {'Parameters': ['Button', 'Detail Type'], 'Status': {}},
            'CallHistoryNavigation': {'Status': {}},
            'CallHistoryRefresh': {'Status': {}},
            'CallHistorySelect': {'Parameters': ['Button'], 'Status': {}},
            'CallSetupMode': {'Status': {}},
            'CallStatus': {'Parameters': ['Call'], 'Status': {}},
            'CallStatusType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFocus': {'Parameters': ['Camera'], 'Status': {}},
            'CameraPan': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraPresetRecall': {'Status': {}},
            'CameraPresetSave': {'Parameters': ['Camera'], 'Status': {}},
            'CameraPresetSaveC20': {'Status': {}},
            'CameraTilt': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Camera', 'Speed'], 'Status': {}},
            'CameraFocusC20': {'Status': {}},
            'CameraPanC20': {'Parameters': ['Speed'], 'Status': {}},
            'CameraTiltC20': {'Parameters': ['Speed'], 'Status': {}},
            'CameraZoomC20': {'Parameters': ['Speed'], 'Status': {}},
            'CloseMenu': {'Status': {}},
            'DisplayMode': {'Status': {}},
            'DisplayName': {'Parameters': ['Call'], 'Status': {}},
            'DNSServerAddress': {'Parameters': ['Server'], 'Status': {}},
            'DoNotDisturb': {'Status': {}},
            'DTMF': {'Status': {}},
            'FarEndCameraPanTilt': {'Status': {}},
            'FarEndCameraPresetRecall': {'Status': {}},
            'FarEndCameraPresetSave': {'Status': {}},
            'FarEndCameraSource': {'Status': {}},
            'FarEndCameraZoom': {'Status': {}},
            'FarEndControl': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'GatewayAddress': {'Status': {}},
            'Hook': {'Parameters': ['Protocol','Number'], 'Status': {}},
            'Input': {'Status': {}},
            'InputLevel': {'Parameters': ['Input'], 'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'IPAddress': {'Status': {}},
            'IREmulation': {'Parameters': ['Press Type'], 'Status': {}},
            'Layout': {'Parameters': ['Layout ID'], 'Status': {}},
            'LayoutSet': {'Parameters': ['Target'], 'Status': {}},
            'MACAddress': {'Status': {}},
            'MicrophonesMute': {'Status': {}},
            'MissedCallNotification': {'Status': {}},
            'NetworkAssignment': {'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'PhonebookFolderIDNavigation': {'Status': {}},
            'PhonebookFolderIDSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookFolderIDSearchSet': {'Status': {}},
            'PhonebookFolderIDUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type','Contact','FolderID'], 'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type','Contact','FolderID'], 'Status': {}},
            'PictureInPicture': {'Status': {}},
            'Presentation': {'Status': {}},
            'PresentationMode': {'Status': {}},
            'PresentationSendingMode': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Reboot': {'Status': {}},
            'RemoteNumber': {'Parameters': ['Call'], 'Status': {}},
            'SelfView': {'Status': {}},
            'SelfViewPosition': {'Status': {}},
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
        self.MaxLabel = 0
        self.Offset = 0
        self.dirName = compile('\*r ResultSet Contact (\d+) Name: "(.+)"\r\n')
        self.dirNumber = compile('\*r ResultSet Contact (\d+) ContactMethod 1 Number: "(.+)"')

        self.newList = {}
        self.folderList = {}
        self.FolderIDNumber = None
        self.FolderMin = 1
        self.FolderLimit = 0
        self.FolderNameRex = compile('\*r ResultSet Folder (\d+) Name: "(.+)"\r\n')
        self.FolderIDRex = compile('\*r ResultSet Folder (\d+) FolderId: "(.+)"')

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
        self.CallHistoryAdvance = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line \d) Mode: (On|Off)\r\n'), self.__MatchAudioOutput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference 1 AutoAnswer Mode: (Off|On)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'\*c xConfiguration H323 Profile 1 CallSetup Mode: (Direct|Gatekeeper)\r\n'), self.__MatchCallSetupMode, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video Monitors: (\w+)\r\n'), self.__MatchDisplayMode, None)
            self.AddMatchString(compile(b'\*s Network 1 DNS Server ([1-3]) Address: "([0-9.]{7,15})"'), self.__MatchDNSServerAddress, None)
            self.AddMatchString(compile(b'\*s Conference DoNotDisturb: (Inactive|Active)\r\n'), self.__MatchDoNotDisturb, None)
            self.AddMatchString(compile(b'\*c xConfiguration Conference 1 FarEndControl Mode: (Off|On)\r\n'), self.__MatchFarEndControl, None)
            self.AddMatchString(compile(b'\*s SystemUnit Software Version: "([\w.]+)"\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Gateway: "([0-9.]{7,15})"\r\n'), self.__MatchGatewayAddress, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video MainVideoSource: ([1-5])\r\n'), self.__MatchInput, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input (Line [1-4]|Microphone [1-8]) Level: (\d+)\r\n'), self.__MatchInputLevel, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Input ((Microphone|Line) \d) Mode: (On|Off)\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 Address: "([0-9.]{7,15})"\r\n'), self.__MatchIPAddress, None)
            self.AddMatchString(compile(b'\*s Network 1 Ethernet MacAddress: "([:0-9A-Z]{17})"\r\n\*\* end\r\n'), self.__MatchMACAddress, None)
            self.AddMatchString(compile(b'\*s Audio Microphones Mute: (Off|On)\r\n'), self.__MatchMicrophonesMute, None)
            self.AddMatchString(compile(b'\*c xConfiguration Video OSD MissedCallsNotification: (On|Off)\r'), self.__MatchMissedCallNotification, None)
            self.AddMatchString(compile(b'\*c xConfiguration Network 1 IPv4 Assignment: (DHCP|Static)\r\n\*\* end\r\n'), self.__MatchNetworkAssignment, None)
            self.AddMatchString(compile(b'\*c xConfiguration Audio Output (Line \d) Level: (-{0,1}\d+)\r\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalSource: ([0-5])\r\n'), self.__MatchPresentation, None)
            self.AddMatchString(compile(b'\*s Conference Presentation Mode: (Sending|Receiving|Off)\r\n'), self.__MatchPresentationMode, None)
            self.AddMatchString(compile(b'\*s Conference Presentation LocalSendingMode: (Off|LocalRemote|LocalOnly)\r\n'), self.__MatchPresentationSendingMode, None)
            self.AddMatchString(compile(b'\*s Video Selfview Mode: (On|Off)\r\n'), self.__MatchSelfView, None)
            self.AddMatchString(compile(b'\*s Video Selfview PIPPosition: (Upper|Center|Lower)(Left|Center|Right)\r\n'), self.__MatchSelfViewPosition, None)
            self.AddMatchString(compile(b'\*s Standby Active: (On|Off)\r\n'), self.__MatchStandby, None)
            self.AddMatchString(compile(b'\*s Network 1 IPv4 SubnetMask: "([0-9.]{7,15})"\r\n'), self.__MatchSubnetMask, None)
            self.AddMatchString(compile(b'\*s Audio Volume: (\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'Login incorrect\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'\xFF\xFD\x18\xFF\xFD\x20\xFF\xFD\x23\xFF\xFD\x27'), self.__MatchAuthentication, None)
            self.AddMatchString(compile(b'Welcome to Cisco C90'), self.__MatchSuccess, None)

    @property
    def CallHistoryOccurrenceType(self):
        return self._CallHistoryOccurrenceType

    @CallHistoryOccurrenceType.setter
    def CallHistoryOccurrenceType(self, value):
        self._CallHistoryOccurrenceType = value

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

    def __MatchSuccess(self, match, tag):
        self.SetEchoOff(None, None)

    def SetEchoOff(self, value, qualifier):
        self.Send('echo off\r')

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

    def SetAssignLocalOutput(self, value, qualifier):

        layout = qualifier['Layout ID']
        output = qualifier['Output ID']
        if 1 <= layout <= 2147483647 and 1 <= output <= 65534:
            AssignLocalOutputCmdString = 'xCommand Video Layout AssignLocalOutput OutputId:{0} LayoutId:{1}\r'.format(output, layout)
            self.__SetHelper('AssignLocalOutput', AssignLocalOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAssignLocalOutput')

    def SetAudioOutput(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        Output = self.AudioOutputStates[qualifier['Output']]
        if Output:
            AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode:{1}\r'.format(Output, ValueStateValues[value])
            self.__SetHelper('AudioOutput', AudioOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioOutput')

    def UpdateAudioOutput(self, value, qualifier):

        Output = self.AudioOutputStates[qualifier['Output']]
        AudioOutputCmdString = 'xConfiguration Audio Output {0} Mode\r'.format(Output)
        self.__UpdateHelper('AudioOutput', AudioOutputCmdString, value, qualifier)

    def __MatchAudioOutput(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        Output = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioOutput', value, {'Output': Output})

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        AutoAnswerCmdString = 'xConfiguration Conference 1 AutoAnswer Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerCmdString = 'xConfiguration Conference 1 AutoAnswer Mode\r'
        self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def __MatchAutoAnswer(self, match, tag):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AutoAnswer', value, None)

    def SetCallHistoryRefresh(self, value, qualifier):
        self.__UpdateCallHistoryHelper(value, qualifier)

    def __UpdateCallHistoryHelper(self, value, qualifier):
        cmdStr = 'xCommand CallHistory Recents Filter: All Offset: {0} Limit: {1} Order: Occurrence{2}\r'.format(self.startCallHist - 1, self._NumberofCallHistory, self._CallHistoryOccurrenceType)
        res = self.SendAndWait(cmdStr, 3, deliTag=b'** end')
        if res:
            res = res.decode()
            displayNameList = dict(findall(self.displayName, res))
            callBackNumberList = dict(findall(self.callBackNumber, res))
            lastOccurrenceTimeList = dict(findall(self.lastOccurrenceTime, res))
            occurrenceTypeList = dict(findall(self.occurrenceType, res))
            occurrenceCountList = dict(findall(self.occurrenceCount, res))

            if len(displayNameList) >= self._NumberofCallHistory:
                self.CallHistoryAdvance = True
            else:
                self.CallHistoryAdvance = False

            for btn in range(1, self._NumberofCallHistory + 1):
                index = str(btn - 1)
                if index in displayNameList:
                    self.WriteStatus('CallHistory', displayNameList[index], {'Button': str(btn), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', callBackNumberList[index], {'Button': str(btn), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', lastOccurrenceTimeList[index], {'Button': str(btn), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', occurrenceTypeList[index], {'Button': str(btn), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', occurrenceCountList[index], {'Button': str(btn), 'Detail Type': 'Occurrence Count'})
                else:
                    self.WriteStatus('CallHistory', '', {'Button': str(btn), 'Detail Type': 'Display Name'})
                    self.WriteStatus('CallHistory', '', {'Button': str(btn), 'Detail Type': 'Callback Number'})
                    self.WriteStatus('CallHistory', '', {'Button': str(btn), 'Detail Type': 'Last Occurrence Time'})
                    self.WriteStatus('CallHistory', '', {'Button': str(btn), 'Detail Type': 'Occurrence Type'})
                    self.WriteStatus('CallHistory', '', {'Button': str(btn), 'Detail Type': 'Occurrence Count'})

    def SetCallHistoryNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down'] and self.CallHistoryAdvance:
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

        ButtonStates = {str(a): str(a) for a in range(1, 21)}
        number = self.ReadStatus('CallHistory', {'Button': ButtonStates[qualifier['Button']], 'Detail Type': 'Callback Number'})
        if number:
            self.Send('xCommand Dial Number:"{0}"\r'.format(number))
        else:
            self.Discard('Invalid Command for SetCallHistorySelect')

    def SetCallSetupMode(self, value, qualifier):

        ValueStateValues = {
            'Gatekeeper': 'Gatekeeper',
            'Direct': 'Direct'
        }

        CallSetupModeCmdString = 'xConfiguration H323 Profile 1 CallSetup Mode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CallSetupMode', CallSetupModeCmdString, value, qualifier)

    def UpdateCallSetupMode(self, value, qualifier):
        AudioOutputCmdString = 'xConfiguration H323 Profile 1 CallSetup Mode\r'
        self.__UpdateHelper('CallSetupMode', AudioOutputCmdString, value, qualifier)

    def __MatchCallSetupMode(self, match, tag):
        ValueStateValues = {
            'Gatekeeper': 'Gatekeeper',
            'Direct': 'Direct'
        }
        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CallSetupMode', value, None)

    def UpdateCallStatus(self, value, qualifier):
        cmdStr = 'xstatus call\r'
        res = self.SendAndWait(cmdStr, 1, deliTag=b'** end')
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
        else:
            for index in range(1, 6):
                self.WriteStatus('CallStatus', 'Idle', {'Call': str(index)})
                self.WriteStatus('DisplayName', '', {'Call': str(index)})
                self.WriteStatus('RemoteNumber', '', {'Call': str(index)})
                self.WriteStatus('CallStatusType', 'Unknown', {'Call': str(index)})
                    
    def UpdateCallStatusType(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def SetCameraFocus(self, value, qualifier):

        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7:
            CameraFocusCmdString = ''
            if value in ['Far', 'Near', 'Stop']:
                CameraFocusCmdString = 'xCommand Camera Ramp CameraId:{0} Focus:{1}\r'.format(camID, value)
            elif value is 'Auto':
                CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:{0}\r'.format(camID)
            else:
                self.Discard('Invalid Command for SetCameraFocus')

            if CameraFocusCmdString:
                self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraFocus')
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraPan(self, value, qualifier):

        valueStates = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop',
        }

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            CameraPanCmdString = ''
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan: Stop\r'.format(camID)
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:{0} Pan:{1} PanSpeed:{2}\r'.format(camID, valueStates[value], camSpeed)

            if CameraPanCmdString:
                self.__SetHelper('CameraPan', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPan')
        else:
            self.Discard('Invalid Command for SetCameraPan')

    def SetCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 35:
            CameraPresetRecallCmdString = 'xCommand Camera Preset Activate PresetId: {0}\r'.format(value)
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        camID = qualifier['Camera']
        if 1 <= int(camID) <= 7 and 1 <= int(value) <= 35:
            CameraPresetSaveCmdString = 'xCommand Camera Preset Store PresetId: {0} CameraId: {1}\r'.format(value, camID)
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraPresetSaveC20(self, value, qualifier):

        if 1 <= int(value) <= 35:
            CameraPresetSaveCmdString = 'xCommand Camera Preset Store PresetId: {0} CameraId: 1\r'.format(value)
            self.__SetHelper('CameraPresetSaveC20', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSaveC20')

    def SetCameraTilt(self, value, qualifier):

        valueStates = {
            'Up': 'Up',
            'Down': 'Down',
        }

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            CameraTiltCmdString = ''
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt: Stop\r'.format(camID)
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:{0} Tilt:{1} TiltSpeed:{2}\r'.format(camID, valueStates[value], camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTilt', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTilt')
        else:
            self.Discard('Invalid Command for SetCameraTilt')

    def SetCameraZoom(self, value, qualifier):

        valueStates = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop',
        }

        camID = qualifier['Camera']
        camSpeed = qualifier['Speed']
        if 1 <= int(camID) <= 7 and 1 <= int(camSpeed) <= 15:
            CameraZoomCmdString = ''
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom: Stop\r'.format(camID)
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:{0} Zoom:{1} ZoomSpeed:{2}\r'.format(camID, valueStates[value], camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoom')
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetCameraFocusC20(self, value, qualifier):

        CameraFocusCmdString = ''
        if value in ['Far', 'Near', 'Stop']:
            CameraFocusCmdString = 'xCommand Camera Ramp CameraId:1 Focus:{0}\r'.format(value)
        elif value is 'Auto':
            CameraFocusCmdString = 'xCommand Camera TriggerAutoFocus CameraId:1\r'
        else:
            self.Discard('Invalid Command for SetCameraFocusC20')

        if CameraFocusCmdString:
            self.__SetHelper('CameraFocusC20', CameraFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocusC20')

    def SetCameraPanC20(self, value, qualifier):

        valueStates = {
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop',
        }

        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            CameraPanCmdString = ''
            if value == 'Stop':
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan: Stop\r'
            else:
                CameraPanCmdString = 'xCommand Camera Ramp CameraId:1 Pan:{0} PanSpeed:{1}\r'.format(valueStates[value], camSpeed)

            if CameraPanCmdString:
                self.__SetHelper('CameraPanC20', CameraPanCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraPanC20')
        else:
            self.Discard('Invalid Command for SetCameraPanC20')

    def SetCameraTiltC20(self, value, qualifier):

        valueStates = {
            'Up': 'Up',
            'Down': 'Down',
        }
        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            CameraTiltCmdString = ''
            if value == 'Stop':
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt: Stop\r'
            else:
                CameraTiltCmdString = 'xCommand Camera Ramp CameraId:1 Tilt:{0} TiltSpeed:{1}\r'.format(valueStates[value], camSpeed)

            if CameraTiltCmdString:
                self.__SetHelper('CameraTiltC20', CameraTiltCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraTiltC20')
        else:
            self.Discard('Invalid Command for SetCameraTiltC20')

    def SetCameraZoomC20(self, value, qualifier):

        valueStates = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop',
        }

        camSpeed = qualifier['Speed']
        if 1 <= int(camSpeed) <= 15:
            CameraZoomCmdString = ''
            if value == 'Stop':
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom: Stop\r'
            else:
                CameraZoomCmdString = 'xCommand Camera Ramp CameraId:1 Zoom:{0} ZoomSpeed:{1}\r'.format(valueStates[value], camSpeed)

            if CameraZoomCmdString:
                self.__SetHelper('CameraZoomC20', CameraZoomCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCameraZoomC20')
        else:
            self.Discard('Invalid Command for SetCameraZoomC20')

    def SetCloseMenu(self, value, qualifier):

        CloseMenuCmdString = 'xCommand UserInterface OSD Close Element: Menu\r'
        self.__SetHelper('CloseMenu', CloseMenuCmdString, value, qualifier)

    def SetDisplayMode(self, value, qualifier):

        if self.DisplayModeStatesSet[value]:
            DisplayModeCmdString = 'xConfiguration Video Monitors: {0}\r'.format(self.DisplayModeStatesSet[value])
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):

        DisplayModeCmdString = 'xConfiguration Video Monitors\r'
        self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)

    def __MatchDisplayMode(self, match, tag):

        value = self.DisplayModeStatesMatch[match.group(1).decode()]
        self.WriteStatus('DisplayMode', value, None)

    def UpdateDisplayName(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def UpdateDNSServerAddress(self, value, qualifier):

        ServerStates = {
            '1': '1',
            '2': '2',
            '3': '3'
        }
        DNSServerAddressCmdString = 'xStatus Network DNS Server {0} Address\r'.format(ServerStates[qualifier['Server']])
        self.__UpdateHelper('DNSServerAddress', DNSServerAddressCmdString, value, qualifier)

    def __MatchDNSServerAddress(self, match, tag):

        ServerStates = {
            '1': '1',
            '2': '2',
            '3': '3'

        }

        qualifier = {}
        qualifier['Server'] = ServerStates[match.group(1).decode()]
        value = match.group(2).decode()
        self.WriteStatus('DNSServerAddress', value, qualifier)

    def SetDoNotDisturb(self, value, qualifier):

        valueStates = {
            'Active': 'Activate',
            'Inactive': 'Deactivate',
        }

        DoNotDisturbCmdString = 'xCommand Conference DoNotDisturb {0}\r'.format(valueStates[value])
        self.__SetHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def UpdateDoNotDisturb(self, value, qualifier):

        DoNotDisturbCmdString = 'xStatus Conference DoNotDisturb\r'
        self.__UpdateHelper('DoNotDisturb', DoNotDisturbCmdString, value, qualifier)

    def __MatchDoNotDisturb(self, match, tag):

        ValueStateValues = {
            'Active': 'Active',
            'Inactive': 'Inactive',
        }
        value = ValueStateValues[match.group(1).decode()]
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

        DTMFCmdString = 'xCommand DTMFSend DTMFString:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetFarEndCameraPanTilt(self, value, qualifier):

        valueStates = {
            'Left': 'Left',
            'Right': 'Right',
            'Up': 'Up',
            'Down': 'Down',
        }
        if value == 'Stop':
            FarEndCameraPanTiltCmdString = 'xCommand FarEndControl Camera Move Stop\r'
        else:
            FarEndCameraPanTiltCmdString = 'xCommand FarEndControl Camera Move:{0}\r'.format(valueStates[value])
        self.__SetHelper('FarEndCameraPanTilt', FarEndCameraPanTiltCmdString, value, qualifier)

    def SetFarEndCameraPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 15:
            FarEndCameraPresetRecallCmdString = 'xCommand FarEndControl Preset Activate PresetId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetRecall', FarEndCameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetRecall')

    def SetFarEndCameraPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 15:
            FarEndCameraPresetSaveCmdString = 'xCommand FarEndControl Preset Store PresetId: {0}\r'.format(value)
            self.__SetHelper('FarEndCameraPresetSave', FarEndCameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraPresetSave')

    def SetFarEndCameraSource(self, value, qualifier):

        if 0 <= int(value) <= 15:
            FarEndCameraSourceCmdString = 'xCommand FarEndControl Source Select SourceId:{0}\r'.format(value)
            self.__SetHelper('FarEndCameraSource', FarEndCameraSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFarEndCameraSource')

    def SetFarEndCameraZoom(self, value, qualifier):

        if value == 'Stop':
            FarEndCameraZoomCmdString = 'xCommand FarEndControl Camera Stop\r'
        else:
            FarEndCameraZoomCmdString = 'xCommand FarEndControl Camera Move Value:Zoom{0}\r'.format(value)
        self.__SetHelper('FarEndCameraZoom', FarEndCameraZoomCmdString, value, qualifier)

    def SetFarEndControl(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        FarEndControlCmdString = 'xConfiguration Conference 1 FarEndControl Mode: {0}'.format(ValueStateValues[value])
        self.__SetHelper('FarEndControl', FarEndControlCmdString, value, qualifier)

    def UpdateFarEndControl(self, value, qualifier):

        FarEndControlCmdString = 'xConfiguration Conference 1 FarEndControl Mode\r'
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

    def SetHook(self, value, qualifier):

        Protocol_Values = {
            'H320': 'H320',
            'H323': 'H323',
            'SIP': 'Sip',
            'Auto': 'Auto',
        }

        protocol = qualifier['Protocol']

        if value in ['Disconnect All', 'Accept', 'Reject', 'Hold All']:
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
                    self.__SetHelper('Hook', 'xCommand Dial Number:"{0}"\r'.format(number), value, qualifier)
                else:
                    self.__SetHelper('Hook', 'xCommand Dial Number:"{0}" Protocol:{1}\r'.format(number, Protocol_Values[protocol]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def SetInput(self, value, qualifier):

        if self.InputStates[value]:
            InputCmdString = 'xConfiguration Video MainVideoSource: {0}\r'.format(self.InputStates[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'xConfiguration Video MainVideoSource\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetInputLevel(self, value, qualifier):

        input_ = qualifier['Input']
        if self.InputMuteLevelStates[input_] and 0 <= value <= 24:
            InputLevelCmdString = 'xConfiguration Audio Input {0} Level:{1}\r'.format(self.InputMuteLevelStates[input_], value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        input_ = qualifier['Input']
        if self.InputMuteLevelStates[input_]:
            InputLevelCmdString = 'xConfiguration Audio Input {0} Level\r'.format(self.InputMuteLevelStates[input_])
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        input_ = self.InputMuteLevelStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('InputLevel', value, {'Input': input_})

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }
        input_ = qualifier['Input']
        if self.InputMuteLevelStates[input_]:
            InputMuteCmdString = 'xConfiguration Audio Input {0} Mode:{1}\r'.format(self.InputMuteLevelStates[input_], ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        input_ = qualifier['Input']
        if self.InputMuteLevelStates[input_]:
            InputMuteCmdString = 'xConfiguration Audio Input {0} Mode\r'.format(self.InputMuteLevelStates[input_])
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        input_ = self.InputMuteLevelStates[match.group(1).decode()]
        self.WriteStatus('InputMute', match.group(3).decode(), {'Input': input_})

    def UpdateIPAddress(self, value, qualifier):

        IPAddressCmdString = 'xStatus Network 1 IPv4 Address\r'
        self.__UpdateHelper('IPAddress', IPAddressCmdString, value, qualifier)

    def __MatchIPAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('IPAddress', value, None)

    def SetIREmulation(self, value, qualifier):

        PressTypeStates = {
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
            'Disconnect': 'Disconnect',
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
            'DocCam': 'SrcDocCam',
            'PC': 'SrcPc',
            'VCR': 'SrcVcr',
            'Star': 'Star',
            'Up': 'Up',
            'Volume Down': 'VolumeDown',
            'Volume Up': 'VolumeUp',
            'Zoom In': 'ZoomIn',
            'Zoom Out': 'ZoomOut'
        }

        pressType = PressTypeStates[qualifier['Press Type']]
        if pressType:
            IREmulationCmdString = 'xCommand Key {0} Key: {1}\r'.format(pressType, ValueStateValues[value])
            self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetLayout(self, value, qualifier):

        id_ = qualifier['Layout ID']
        if 1 <= id_ <= 65535:
            if value in ['Add', 'Remove']:
                self.__SetHelper('Layout', 'xCommand Video Layout {0} LayoutId: {1}\r'.format(value, id_), value, qualifier)
            elif value in ['Remove All', 'Reset']:
                self.__SetHelper('Layout', 'xCommand Video Layout {0}\r'.format(value.replace(' ', '')), value, qualifier)
            else:
                self.Discard('Invalid Command for SetLayout')
        else:
            self.Discard('Invalid Command for SetLayout')

    def SetLayoutSet(self, value, qualifier):

        targetStates = {
            'Local': 'Local',
            'Remote': 'Remote'
        }

        target = targetStates[qualifier['Target']]
        if target and value in ['Auto', 'Custom', 'Equal', 'Fullscreen', 'Overlay', 'Presentation Large Speaker', 'Presentation Small Speaker', 'Prominent', 'Single']:
            self.__SetHelper('LayoutSet', 'xCommand Video PictureLayoutSet Target: {0} LayoutFamily: {1}\r'.format(target, value.replace(' ', '')), value, qualifier)
        elif target and value == 'Speaker Full':
            self.__SetHelper('LayoutSet', 'xCommand Video PictureLayoutSet Target: {0} LayoutFamily: Speaker_Full\r'.format(target), value, qualifier)
        else:
            self.Discard('Invalid Command for SetLayoutSet')

    def UpdateMACAddress(self, value, qualifier):

        MACAddressCmdString = 'xStatus Network 1 Ethernet MacAddress\r'
        self.__UpdateHelper('MACAddress', MACAddressCmdString, value, qualifier)

    def __MatchMACAddress(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MACAddress', value, None)

    def SetMicrophonesMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute',
            'Off': 'UnMute',
        }

        MicrophonesMuteCmdString = 'xCommand Audio Microphones {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def UpdateMicrophonesMute(self, value, qualifier):

        MicrophonesMuteCmdString = 'xStatus Audio Microphones\r'
        self.__UpdateHelper('MicrophonesMute', MicrophonesMuteCmdString, value, qualifier)

    def __MatchMicrophonesMute(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('MicrophonesMute', value, None)

    def SetMissedCallNotification(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        MissedCallNotificationCmdString = 'xConfiguration Video OSD MissedCallsNotification: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MissedCallNotification', MissedCallNotificationCmdString, value, qualifier)

    def UpdateMissedCallNotification(self, value, qualifier):

        MissedCallNotificationCmdString = 'xConfiguration Video OSD MissedCallsNotification\r'
        self.__UpdateHelper('MissedCallNotification', MissedCallNotificationCmdString, value, qualifier)

    def __MatchMissedCallNotification(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('MissedCallNotification', value, None)

    def UpdateNetworkAssignment(self, value, qualifier):

        NetworkAssignmentCmdString = 'xConfiguration Network 1 IPv4 Assignment\r'
        self.__UpdateHelper('NetworkAssignment', NetworkAssignmentCmdString, value, qualifier)

    def __MatchNetworkAssignment(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('NetworkAssignment', value, None)

    def SetOutputLevel(self, value, qualifier):

        Output = self.AudioOutputStates[qualifier['Output']]
        if Output and -24 <= value <= 0:
            OutputLevelCmdString = 'xConfiguration Audio Output {0} Level:{1}\r'.format(Output, value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        Output = self.AudioOutputStates[qualifier['Output']]
        if Output:
            OutputLevelCmdString = 'xConfiguration Audio Output {0} Level\r'.format(Output)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        Output = self.AudioOutputStates[match.group(1).decode()]
        value = int(match.group(2))
        self.WriteStatus('OutputLevel', value, {'Output': Output})

    def SetPhonebookSearchSet(self, value, qualifier):

        if value < 1 or value > self._NumberofPhonebookSearch:
            self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number:
                number = number[number.find(' : ') + 3:]
                commandstring = 'xCommand Dial Number:"{0}"\r'.format(number)
                self.Send(commandstring)

    def SetPhonebookFolderIDNavigation(self, value, qualifier):

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
                    self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {'Button': button})
                    button += 1

            if button <= self._NumberofPhonebookFolderSearch:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                button += 1
                for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
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
        if self.folderList:
            folderName = self.ReadStatus('PhonebookFolderIDSearchResult', {'Button': value})
            if folderName != '***End of list***':
                self.FolderIDNumber = [v['ID'] for v in self.folderList.values() if v['Name'] == folderName][0]
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDSearchSet')

    def SetPhonebookFolderIDUpdate(self, value, qualifier):

        phonebookValue = qualifier['Phonebook Type']
        self.FolderMin = 1
        self.FolderLimit = self._NumberofPhonebookFolderSearch
        if phonebookValue:
            self.WriteStatus('PhonebookFolderIDSearchResult', '***Loading Folders***', {'Button': 1})
            for i in range(2, int(self._NumberofPhonebookFolderSearch) + 1):
                self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
            cmdStr = 'xCommand Phonebook Search PhonebookType:{0} ContactType: Folder Offset: 0 Limit: {1}\r'.format(phonebookValue, self._NumberofFoldersPerSearch)
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
                        self.WriteStatus('PhonebookFolderIDSearchResult', '{0}'.format(self.folderList[str(i)]['Name']), {'Button': int(i)})
                        button += 1

                if button <= self._NumberofPhonebookFolderSearch:
                    self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': button})
                    button += 1
                    for i in range(button, int(self._NumberofPhonebookFolderSearch) + 1):
                        self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
            else:
                self.WriteStatus('PhonebookFolderIDSearchResult', '***End of list***', {'Button': 1})
                for i in range(2, int(self._NumberofPhonebookFolderSearch) + 1):
                    self.WriteStatus('PhonebookFolderIDSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookFolderIDUpdate')

    def SetPhonebookUpdate(self, value, qualifier):
        
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
            self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
        
        phonebookType =  qualifier['Phonebook Type']
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
                self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': 1})
                for i in range(2, self._NumberofPhonebookSearch + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookUpdateHandler')

    def SetPhonebookWriteHandler(self, value, qualifier):
        
        button = 1
        for i in range(self.MinLabel, self.MaxLabel + 1):
            if str(i) in self.newList:
                self.WriteStatus('PhonebookSearchResult', '{0} : {1}'.format(self.newList[str(i)]['Name'], self.newList[str(i)]['Number']), {'Button': button})
                button += 1

        if button <= self._NumberofPhonebookSearch:
            self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
            button += 1
            for i in range(button, int(self._NumberofPhonebookSearch) + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPictureInPicture(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        PictureInPictureCmdString = 'xCommand CamCtrlPip Mode:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def SetPresentation(self, value, qualifier):

        if self.PresentationStates[value]:
            if value == 'Stop':
                PresentationCmdString = 'xCommand Presentation Stop\r'
            else:
                PresentationCmdString = 'xCommand Presentation Start PresentationSource: {0}\r'.format(self.PresentationStates[value])
            self.__SetHelper('Presentation', PresentationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresentation')

    def UpdatePresentation(self, value, qualifier):

        PresentationCmdString = 'xStatus Conference Presentation LocalSource\r'
        self.__UpdateHelper('Presentation', PresentationCmdString, value, qualifier)

    def __MatchPresentation(self, match, tag):

        value = match.group(1).decode()
        value = 'Stop' if value == '0' else value
        self.WriteStatus('Presentation', value, None)

    def UpdatePresentationMode(self, value, qualifier):

        PresentationModeCmdString = 'xStatus Conference Presentation Mode\r'
        self.__UpdateHelper('PresentationMode', PresentationModeCmdString, value, qualifier)

    def __MatchPresentationMode(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('PresentationMode', value, None)

    def SetPresentationSendingMode(self, value, qualifier):

        ValueStateValues = {
            'Local and Remote': 'LocalRemote',
            'Local Only': 'LocalOnly',
        }

        PresentationSendingModeCmdString = 'xCommand Presentation Start SendingMode: {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresentationSendingMode', PresentationSendingModeCmdString, value, qualifier)

    def UpdatePresentationSendingMode(self, value, qualifier):

        PresentationSendingModeCmdString = 'xStatus Conference Presentation LocalSendingMode\r'
        self.__UpdateHelper('PresentationSendingMode', PresentationSendingModeCmdString, value, qualifier)

    def __MatchPresentationSendingMode(self, match, tag):

        ValueStateValues = {
            'LocalRemote': 'Local and Remote',
            'LocalOnly': 'Local Only',
            'Off': 'Off',
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PresentationSendingMode', value, None)

    def SetPresetRecall(self, value, qualifier):

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

        PresetRecallCmdString = 'xCommand Preset Activate PresetId:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

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

        PresetSaveCmdString = 'xCommand Preset Store PresetId:{0} Type:All\r'.format(ValueStateValues[value])
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'xCommand Boot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def UpdateRemoteNumber(self, value, qualifier):

        self.UpdateCallStatus(value, qualifier)

    def SetSelfView(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        SelfViewCmdString = 'xCommand Video Selfview Set Mode:{0}\r'.format(ValueStateValues[value])
        self.__SetHelper('SelfView', SelfViewCmdString, value, qualifier)

    def UpdateSelfView(self, value, qualifier):

        SelfViewCmdString = 'xStatus Video Selfview Mode\r'
        self.__UpdateHelper('SelfView', SelfViewCmdString, value, qualifier)

    def __MatchSelfView(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('SelfView', value, None)

    def SetSelfViewPosition(self, value, qualifier):

        if value in ['Upper Left', 'Upper Center', 'Upper Right', 'Center Left', 'Center Right', 'Lower Left', 'Lower Right']:
            SelfViewPositionCmdString = 'xCommand Video Selfview Set PIPPosition:{0}\r'.format(value.replace(' ', ''))
            self.__SetHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSelfViewPosition')

    def UpdateSelfViewPosition(self, value, qualifier):

        SelfViewPositionCmdString = 'xStatus Video Selfview PIPPosition\r'
        self.__UpdateHelper('SelfViewPosition', SelfViewPositionCmdString, value, qualifier)

    def __MatchSelfViewPosition(self, match, tag):

        value = match.group(1).decode() + ' ' + match.group(2).decode()
        self.WriteStatus('SelfViewPosition', value, None)

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

    def SetStandby(self, value, qualifier):

        ValueStateValues = {
            'Activate': 'Activate',
            'Deactivate': 'Deactivate'
        }

        StandbyCmdString = 'xCommand Standby {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def UpdateStandby(self, value, qualifier):

        StandbyCmdString = 'xStatus Standby\r'
        self.__UpdateHelper('Standby', StandbyCmdString, value, qualifier)

    def __MatchStandby(self, match, tag):

        ValueStateValues = {
            'Off': 'Deactivate',
            'On': 'Activate',
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

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command.Unidirectional mode.')
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

    def csco_12_2062_C20(self):

        self.DisplayModeStatesSet = {
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
            'Quadruple': 'Quadruple',
            'Triple': 'Triple',
        }

        self.DisplayModeStatesMatch = {
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
            'Quadruple': 'Quadruple',
            'Triple': 'Triple',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
        }

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.PresentationStates = {
            '1': '1',
            '2': '2',
            'Stop': 'Stop',
        }

    def csco_12_2062_C40(self):

        self.DisplayModeStatesSet = {
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
        }

        self.DisplayModeStatesMatch = {
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        self.AudioOutputStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.LineStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
        }

        self.InputMuteLevelStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.PresentationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            'Stop': 'Stop',
        }

    def csco_12_2062_C60(self):

        self.DisplayModeStatesSet = {
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
        }

        self.DisplayModeStatesMatch = {
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
        }

        self.AudioOutputStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.LineStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.MicStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3',
            'Microphone 4': 'Microphone 4',
        }

        self.InputMuteLevelStates = {
            'Microphone 1': 'Microphone 1',
            'Microphone 2': 'Microphone 2',
            'Microphone 3': 'Microphone 3',
            'Microphone 4': 'Microphone 4',
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
        }

        self.PresentationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            'Stop': 'Stop',
        }

    def csco_12_2062_C90(self):

        self.DisplayModeStatesSet = {
            'Single': 'Single',
            'Dual': 'Dual',
            'Dual Presentation Only': 'DualPresentationOnly',
            'Quadruple': 'Quadruple',
        }

        self.DisplayModeStatesMatch = {
            'Single': 'Single',
            'Dual': 'Dual',
            'DualPresentationOnly': 'Dual Presentation Only',
            'Quadruple': 'Quadruple',
        }

        self.InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
        }

        self.AudioOutputStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
            'Line 3': 'Line 3',
            'Line 4': 'Line 4',
            'Line 5': 'Line 5',
            'Line 6': 'Line 6',
        }

        self.LineStates = {
            'Line 1': 'Line 1',
            'Line 2': 'Line 2',
            'Line 3': 'Line 3',
            'Line 4': 'Line 4',
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

        self.InputMuteLevelStates = {
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
        }

        self.PresentationStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            'Stop': 'Stop',
        }

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
