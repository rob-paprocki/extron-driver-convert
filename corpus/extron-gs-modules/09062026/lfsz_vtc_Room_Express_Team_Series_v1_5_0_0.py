from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search, findall
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'Express 220': self.lfsz_Express,
            'Room 200': self.lfsz_Room,
            'Room 220': self.lfsz_Room,
            'Team 220': self.lfsz_Team,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioCallType': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraPresetRecall': {'Status': {}},
            'CameraPresetSave': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'DTMF': {'Status': {}},
            'Hook': {'Status': {}},
            'InputFar': {'Status': {}},
            'InputNear': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'Layout': {'Status': {}},
            'PanTiltFar': {'Status': {}},
            'PanTiltNear': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookResults': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookResultSet': {'Parameters': ['Position'], 'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Type'], 'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PowerManagement': {'Status': {}},
            'Presentation': {'Status': {}},
            'Reboot': {'Status': {}},
            'RedialListNavigation': {'Status': {}},
            'RedialListResults': {'Parameters': ['Position'], 'Status': {}},
            'RedialListResultSet': {'Parameters': ['Position'], 'Status': {}},
            'RedialListUpdate': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VideoCallType': {'Status': {}},
            'Volume': {'Status': {}},
            'ZoomFar': {'Status': {}},
            'ZoomNear': {'Status': {}},
        }

        self.Authentication = 'Not Needed'
        self.DeviceState = 'Ready'

        self.callID = '1'
        self.directoryType = 'Local'

        self.NumberOfPhonebookSearch = 5
        self.RedialListDisplayCount = 5

        if 'Serial' not in self.ConnectionType:
            self.deviceUsername = 'auto'
            self.devicePassword = 'lifesize'

        self.AddMatchString(compile(b'Password: '), self.__MatchPassword, None)
        self.AddMatchString(compile(
            b'((status call active\r\n|(CS|IC),)([0-9]{1,2}),[0-9]{1,2},(Answered Number|Answered Consult|Ringing|Dialing|Off Hook|'
            b'Connected|Call Encrypted|Call Not Encrypted|Ring Incoming|Proceeding|On Hook|Unreachable|Terminated|'
            b'Terminating|Busy|Valid Number),|status call active\r\n\r\nok,00\r\n\$)'),
                            self.__MatchCallStatus, 'rex')
        self.AddMatchString(compile(b'ok,00\r\nSS,(false|true)\r\n'), self.__MatchPowerManagement, 'rex2')
        self.AddMatchString(compile(b'PS,0,1,(Initiated|Terminated),No,'), self.__MatchPresentation, 'rex3')
        self.AddMatchString(compile(b'login: '), self.__MatchUsername, None)
        self.AddMatchString(compile(b'Login incorrect'), self.__MatchFailedLogin, None)
        self.AddMatchString(compile(b'can[\x27]t resolve /var/services/comm/uictl'), self.__MatchConnection, None)
        self.PowerandPresentation = compile(b'(PS,0,1,(Initiated|Terminated),No,|ok,00\r\nSS,(false|true)\r\n'
                                            b'|((status call active\r\n|(CS|IC),)[0-9]{1,2},[0-9]{1,2},'
                                            b'(Answered Number|Answered Consult|Ringing|Dialing|Off Hook|Connected|Call Encrypted|'
                                            b'Call Not Encrypted|Ring Incoming|Proceeding|On Hook|Unreachable|Busy|Terminated|Terminating|Valid Number)'
                                            b',|status call active\r\n\r\nok,00\r\n\$))')

        self.RedialPattern = compile('(\d+),([\s\S]+),([\s\S]+),,')
        self.changeDeviceStateWait = None

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberOfPhonebookSearch = int(value)
            self.PhonebookDirectory = Directory(self._NumberOfPhonebookSearch, 'PhonebookResults', filler='')
            self.PhonebookDirectory.write_status_function = self.WriteStatus
        else:
            self.Error(['Number of Phonebook Search should be a value between 1 to 10.'])

    @property
    def RedialListDisplayCount(self):
        return self._RedialListDisplayCount

    @RedialListDisplayCount.setter
    def RedialListDisplayCount(self, value):
        if 1 <= int(value) <= 10:
            self._RedialListDisplayCount = int(value)
            self.RedialListDirectory = Directory(self._RedialListDisplayCount, 'RedialListResults', filler='')
            self.RedialListDirectory.write_status_function = self.WriteStatus
        else:
            self.Error(['Redial List Display Count should be a value between 1 to 10.'])

    def SetRedialListNavigation(self, value, qualifier):

        if value == 'Up':
            self.RedialListDirectory.scroll_up(1)
        elif value == 'Down':
            self.RedialListDirectory.scroll_down(1)
        elif value == 'Page Up':
            self.RedialListDirectory.scroll_up(self._RedialListDisplayCount)
        elif value == 'Page Down':
            self.RedialListDirectory.scroll_down(self._RedialListDisplayCount)
        else:
            self.Discard('Invalid Command for SetRedialListNavigation')

    def SetRedialListUpdate(self, value, qualifier):

        RedialListUpdateCmdString = 'get redial-list\r'
        res = self.__SetHelper('RedialListUpdate', RedialListUpdateCmdString, value, qualifier)
        if res:
            List = res.split('\x0D\x0A')
            del List[0]
            del List[-3]
            del List[-2]
            del List[-1]

            LocalList = []
            for i in range(0, len(List)):
                NewRed = List[i].split('\x2C')
                temp = '{0} : {1}'.format(NewRed[0], NewRed[1])
                LocalList.append(temp)

            LocalList.append('***End of List***')
            self.RedialListDirectory.reset(LocalList)

    def SetRedialListResultSet(self, value, qualifier):

        entry = self.ReadStatus('RedialListResults', {'Position': value})
        if entry:
            if entry != '***End of List***':
                number = entry.split(':')[1].strip()
                self.SetHook('Dial', {'Number': number})
            else:
                self.Discard('Invalid Command')

    def SetPhonebookNavigation(self, value, qualifier):

        if value == 'Up':
            self.PhonebookDirectory.scroll_up(1)
        elif value == 'Down':
            self.PhonebookDirectory.scroll_down(1)
        elif value == 'Page Up':
            self.PhonebookDirectory.scroll_up(self._NumberOfPhonebookSearch)
        elif value == 'Page Down':
            self.PhonebookDirectory.scroll_down(self._NumberOfPhonebookSearch)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookUpdate(self, value, qualifier):

        PhoneBookType = {'Local': 'local', 'Corporate': 'corporate', 'Meetings': 'meeting'}

        res = self.SendAndWait('get directory {0}\r'.format(PhoneBookType[qualifier['Type']]), 6, deliTag=b'$')
        if PhoneBookType[qualifier['Type']] == 'local':
            self.directoryType = 'local'
        elif PhoneBookType[qualifier['Type']] == 'corporate':
            self.directoryType = 'corporate'
        elif PhoneBookType[qualifier['Type']] == 'meeting':
            self.directoryType = 'meeting'
        else:
            self.Discard('Invalid Command for SetPhonebookUpdate')
        
        if res:
            res = res.decode()
            List = res.split('\x0D\x0A')
            del List[0]
            del List[-3]
            del List[-2]
            del List[-1]

            self.PhonebookNameList = []
            for x in range(0, len(List)):
                NewEntry = List[x].split('\x2C')
                if NewEntry[3] == '':
                    temp = '{0} : {1}'.format(NewEntry[0], NewEntry[1])
                else:
                    temp = '{0} : {1}'.format(NewEntry[0], NewEntry[3])
                self.PhonebookNameList.append(temp)

            self.PhonebookNameList.append('***End of List***')
            self.PhonebookDirectory.reset(self.PhonebookNameList)

    def SetPhonebookResultSet(self, value, qualifier):

        entry = self.ReadStatus('PhonebookResults', {'Position': value})
        if entry:
            if entry != '***End of list***':
                number = entry.split(':')[1].strip()
                if self.directoryType == 'local':
                    self.SetHook('Dial', {'Number': '\"local:{0}\"'.format(number)})
                elif self.directoryType == 'corporate':
                    self.SetHook('Dial', {'Number': '\"corp:{0}\"'.format(number)})
                elif self.directoryType == 'meeting':
                    self.SetHook('Dial', {'Number': '\"meeting:{0}\"'.format(number)})
                else:
                    self.Error('PhonebookResultSet: Invalid Command')
            else:
                self.Discard('Invalid Command')

    def SetPhonebookSearch(self, value, qualifier):
        PhonebookSearchList = []
        for i in range(len(self.PhonebookNameList)):
            name = self.PhonebookNameList[i].split(':')[0]
            if value.casefold() in name.casefold():
                number = self.PhonebookNameList[i].split(':')[1]
                temp = '{0} : {1}'.format(name, number)
                PhonebookSearchList.append(temp)
        PhonebookSearchList.append('***End of List***')
        self.PhonebookDirectory.reset(PhonebookSearchList)

    def changeDeviceState(self):
        self.DeviceState = 'Ready'
    
    def __MatchConnection(self, match, tag):
        self.WriteStatus('DeviceStatus', 'Not Ready', None)
        self.Discard('Device Is Busy')
        self.DeviceState = 'Busy'
        
        if self.changeDeviceStateWait:
            self.changeDeviceStateWait.Restart()
        else:
            self.changeDeviceStateWait = Wait(60, self.changeDeviceState)

    def __MatchUsername(self, match, tag):

        self.Authentication = 'None'
        if self.deviceUsername:
            self.Send('{0}\r'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):

        self.Authentication = 'None'
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
            self.Authentication = 'Logged In'
        else:
            self.MissingCredentialsLog('Password')

    def __MatchFailedLogin(self, match, tag):
        self.Authentication = 'Failed'

    def SetAudioCallType(self, value, qualifier):

        AudioCallTypeState = {
            'VoIP': '-a voip',
            'Analog': '-a tone',
            'ISDN': '-a isdn',
        }

        AudioCallTypeCmdString = 'set call dial-mode {0}\r'.format(AudioCallTypeState[value])
        self.__SetHelper('AudioCallType', AudioCallTypeCmdString, value, qualifier)

    def UpdateAudioCallType(self, value, qualifier):

        AudioCallTypeState = {
            'voip': 'VoIP',
            'tone': 'Analog',
            'isdn': 'ISDN'
        }
        CmdString = 'get call dial-mode\r'
        res = self.__UpdateHelper('AudioCallType', CmdString, value, qualifier)

        if res:
            try:
                Incoming = res.split('\r\n')
                Split = Incoming[1].split(',')
                value = AudioCallTypeState[Split[1]]
                self.WriteStatus('AudioCallType', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoAnswer(self, value, qualifier):

        AutoAnswerState = {
            'Off': 'off',
            'On': 'on'
        }

        AutoAnswerCmdString = 'set call auto-answer {0}\r'.format(AutoAnswerState[value])
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        AutoAnswerState = {
            'f': 'Off',
            'n': 'On'
        }

        AutoAnswerCmdString = 'get call auto-answer\r'
        response = self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

        if response:
            try:
                value = AutoAnswerState[response[23]]
                self.WriteStatus('AutoAnswer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetAutoFocus(self, value, qualifier):

        AutoFocusState = {
            'Off': 'disable',
            'On': 'enable'
        }

        AutoFocusCmdString = 'set camera autofocus {0}\r'.format(AutoFocusState[value])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def UpdateAutoFocus(self, value, qualifier):

        AutoFocusState = {
            's': 'Off',
            'a': 'On',
        }

        AutoFocusCmdString = 'get camera autofocus\r'
        response = self.__UpdateHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

        if response:
            try:
                value = AutoFocusState[response[24]]
                self.WriteStatus('AutoFocus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetCameraPresetRecall(self, value, qualifier):

        Constraints = {
            'Max': 19,
            'Min': 1
        }
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            CameraPresetRecallCmdString = 'set camera position -P {0}\r'.format(value)
            self.__SetHelper('CameraPresetRecall', CameraPresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetRecall')

    def SetCameraPresetSave(self, value, qualifier):

        Constraints = {
            'Max': 19,
            'Min': 1
        }
        if Constraints['Min'] <= int(value) <= Constraints['Max']:
            CameraPresetSaveCmdString = 'set camera preset -P {0}\r'.format(value)
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def UpdateCallStatus(self, value, qualifier):

        CmdString = 'status call active\r'
        self.__UpdateHelper('CallStatus', CmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

        CallStatusStateNames = {
            'Answered Number': 'Answered Number',
            'Answered Consult': 'Answered Consult',
            'Ringing': 'Ringing',
            'Dialing': 'Dialing',
            'Off Hook': 'Off Hook',
            'Connected': 'Connected',
            'Call Encrypted': 'Call Encrypted',
            'Call Not Encrypted': 'Call Not Encrypted',
            'Ring Incoming': 'Incoming',
            'Unreachable': 'Unreachable',
            'Terminated': 'Disconnected',
            'Terminating': 'Disconnecting',
            'Busy': 'Busy',
            'Valid Number': 'Valid Number',
            'status call active\r\n': 'Not In Call',
            'On Hook': 'On Hook',
            'Proceeding': 'Proceeding'
        }

        if tag == 'rex':
            if match.group(4):
                self.callID = match.group(4).decode()
            if match.group(5):
                value = CallStatusStateNames[match.group(5).decode()]
                self.WriteStatus('CallStatus', value, None)
            else:
                self.WriteStatus('CallStatus', 'Not In Call', None)
        else:
            if match.group(7):
                value = CallStatusStateNames[match.group(7).decode()]
                self.WriteStatus('CallStatus', value, None)
            else:
                self.WriteStatus('CallStatus', 'Not In Call', None)

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
            '#': '#',
            '*': '*',
            'A': 'A',
            'B': 'B',
            'C': 'C',
            'D': 'D',
            'a': 'a',
            'b': 'b',
            'c': 'c',
            'd': 'd'
        }

        DTMFCmdString = 'control call dtmf {0} {1}\r'.format(self.callID, ValueStateValues[value])
        self.__SetHelper('DTMF', DTMFCmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        PhoneCallState = {
            'Dial': 'dial',
            'Flash': 'hook flash',
            'Hang Up': 'hangup -a',
            'Reject': 'answer -r',
            'Answer': 'answer',
            'On': 'hook on',
            'Off': 'hook off',
            'Dial 2': 'add-part 1'
        }

        DialString = qualifier['Number']

        if value == 'Dial':
            PhoneCallCmdString = 'control call {0} {1}\r'.format(PhoneCallState[value], DialString)
        elif value == 'Dial 2':
            PhoneCallCmdString = 'control call {0} {1}\r'.format(PhoneCallState[value], DialString)
        elif value == 'Answer':
            PhoneCallCmdString = 'control call {0} {1} -t video\r'.format(PhoneCallState[value], self.callID)
        else:
            PhoneCallCmdString = 'control call {0}\r'.format(PhoneCallState[value])
        self.__SetHelper('Hook', PhoneCallCmdString, value, qualifier)

    def SetInputNear(self, value, qualifier):

        InputNearCmdString = 'set video primary-input {0}\r'.format(self.InputState[value])
        self.__SetHelper('InputNear', InputNearCmdString, value, qualifier)

    def UpdateInputNear(self, value, qualifier):

        InputNearCmdString = 'get video primary-input\r'
        response = self.__UpdateHelper('InputNear', InputNearCmdString, value, qualifier)

        if response:
            try:
                Input = response.split('\r\n')
                value = self.InputStateUpdate[Input[1]]
                self.WriteStatus('InputNear', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetInputFar(self, value, qualifier):

        InputFarCmdString = 'set video secondary-input {0}\r'.format(self.InputState[value])
        self.__SetHelper('InputFar', InputFarCmdString, value, qualifier)

    def UpdateInputFar(self, value, qualifier):

        InputFarCmdString = 'get video secondary-input\r'
        response = self.__UpdateHelper('InputFar', InputFarCmdString, value, qualifier)

        if response:
            try:
                Input = response.split('\r\n')
                value = self.InputStateUpdate[Input[1]]
                self.WriteStatus('InputFar', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetIRRemoteEmulation(self, value, qualifier):

        IRRemoteEmulationState = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Ok': 'ok',
            'Call': 'call',
            'Back': 'back',
            'Circle': 'cir',
            'Square': 'squ',
            'Hang Up': 'hup',
            'Volume Up': 'vup',
            'Volume Down': 'vdn',
            'Mute': 'mute',
            'Zoom In': 'zin',
            'Zoom Out': 'zout',
            'Near': 'near',
            'Far': 'far',
            'Layout': 'layout',
            'Input': 'input',
            'Mode': 'mode',
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
            '#': '#',
            'Home': 'home',
            'Directory': 'dir',
            'Yellow': 'yellow',
            'Red': 'red',
            'Blue': 'blue',
            'Green': 'green',
            'Triangle': 'tri'
        }

        Remote1 = {'Layout', 'Mode', 'Input', 'Back'}
        if value in Remote1:
            IRRemoteEmulationCmdString = 'control remote1 -d 250 {0}\r'.format(IRRemoteEmulationState[value])
        else:
            IRRemoteEmulationCmdString = 'control remote -d 250 {0}\r'.format(IRRemoteEmulationState[value])
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetLayout(self, value, qualifier):

        if 1 <= int(value) <= 20:
            LayoutCmdString = 'set video layout {0}\r'.format(value)
            self.__SetHelper('Layout', LayoutCmdString, value, qualifier)
        else:
            self.Error(['Layout: Invalid Command'])

    def UpdateLayout(self, value, qualifier):

        LayoutCmdString = 'get video layout\r'
        response = self.__UpdateHelper('Layout', LayoutCmdString, value, qualifier)

        if response:
            try:
                L1 = response.split('\r\n')
                value = str(int(L1[1]))
                self.WriteStatus('Layout', value, qualifier)
            except (ValueError, KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPanTiltFar(self, value, qualifier):

        PanTiltFarState = {
            'Up': '-u',
            'Down': '-d',
            'Left': '-l',
            'Right': '-r',
            'Stop': '-s',
        }

        PanTiltFarCmdString = 'set camera position -c n {0}\r'.format(PanTiltFarState[value])
        self.__SetHelper('PanTiltFar', PanTiltFarCmdString, value, qualifier)

    def SetPanTiltNear(self, value, qualifier):

        PanTiltNearState = {
            'Up': '-u',
            'Down': '-d',
            'Left': '-l',
            'Right': '-r',
            'Stop': '-s',
        }

        PanTiltNearCmdString = 'set camera position {0}\r'.format(PanTiltNearState[value])
        self.__SetHelper('PanTiltNear', PanTiltNearCmdString, value, qualifier)

    def SetPictureInPicture(self, value, qualifier):

        PictureInPictureState = {
            'Off': 'off',
            'On': 'on',
            'Auto': 'auto'
        }

        PictureInPictureCmdString = 'set video pip-mode {0}\r'.format(PictureInPictureState[value])
        self.__SetHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

    def UpdatePictureInPicture(self, value, qualifier):

        PictureInPictureState = {
            'off': 'Off',
            'on': 'On',
            'auto': 'Auto'
        }

        PictureInPictureCmdString = 'get video pip-mode\r'
        response = self.__UpdateHelper('PictureInPicture', PictureInPictureCmdString, value, qualifier)

        if response:
            try:
                Incoming = response.split('\r\n')
                value = PictureInPictureState[Incoming[1]]
                self.WriteStatus('PictureInPicture', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetPowerManagement(self, value, qualifier):

        if value == 'Wake':
            self.__SetHelper('PowerManagement', 'control wakeup\r', value, qualifier)
        else:
            self.__SetHelper('PowerManagement', 'control sleep\r', value, qualifier)

    def __MatchPowerManagement(self, match, tag):

        ValueStateValues = {
            b'false': 'Wake',
            b'true': 'Standby'
        }

        if tag == 'rex2':
            value1 = ValueStateValues[match.group(1)]
        elif match.group(3):
            value1 = ValueStateValues[match.group(3)]
        self.WriteStatus('PowerManagement', value1, None)

    def SetPresentation(self, value, qualifier):

        if value == 'Start':
            self.__SetHelper('Presentation', 'control call presentation 1 start\r', value, qualifier)
        else:
            self.__SetHelper('Presentation', 'control call presentation 1 stop -V\r', value, qualifier)

    def __MatchPresentation(self, match, tag):

        ValueStateValues = {
            b'Initiated': 'Start',
            b'Terminated': 'Stop'
        }

        if tag == 'rex3':
            value = ValueStateValues[match.group(1)]
        elif match.group(2):
            value = ValueStateValues[match.group(2)]
        self.WriteStatus('Presentation', value, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'control reboot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetTransmitMute(self, value, qualifier):

        TransmitMuteState = {
            'Off': 'off',
            'On': 'on'
        }

        TransmitMuteCmdString = 'set audio mute {0}\r'.format(TransmitMuteState[value])
        self.__SetHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

    def UpdateTransmitMute(self, value, qualifier):

        TransmitMuteState = {
            'off': 'Off',
            'on': 'On'
        }

        TransmitMuteCmdString = 'get audio mute\r'
        response = self.__UpdateHelper('TransmitMute', TransmitMuteCmdString, value, qualifier)

        if response:
            try:
                Incoming = response.split('\r\n')
                value = TransmitMuteState[Incoming[1]]
                self.WriteStatus('TransmitMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVideoCallType(self, value, qualifier):

        State = {
            'Auto': 'auto',
            'IP': 'ip',
            'ISDN': 'isdn'
        }

        CmdString = 'set call dial-mode -v {0}\r'.format(State[value])
        self.__SetHelper('VideoCallType', CmdString, value, qualifier)

    def UpdateVideoCallType(self, value, qualifier):

        VideoCallState = {
            'auto': 'Auto',
            'ip': 'IP',
            'isdn': 'ISDN'
        }

        CmdString = 'get call dial-mode\r'
        response = self.__UpdateHelper('VideoCallType', CmdString, value, qualifier)

        if response:
            try:
                Incoming = response.split('\r\n')
                Split = Incoming[1].split(',')
                value = VideoCallState[Split[0]]
                self.WriteStatus('VideoCallType', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'set volume speaker {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get volume speaker\r'
        response = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

        if response:
            try:
                Vol = response.split('\r\n')
                value = int(Vol[1])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Invalid/unexpected response'])

    def SetZoomFar(self, value, qualifier):

        ZoomFarState = {
            'In': '-n',
            'Out': '-f',
            'Stop': '-s',
        }

        ZoomFarCmdString = 'set camera position -c n {0}\r'.format(ZoomFarState[value])
        self.__SetHelper('ZoomFar', ZoomFarCmdString, value, qualifier)

    def SetZoomNear(self, value, qualifier):

        ZoomNearState = {
            'In': '-n',
            'Out': '-f',
            'Stop': '-s',
        }

        ZoomNearCmdString = 'set camera position {0}\r'.format(ZoomNearState[value])
        self.__SetHelper('ZoomNear', ZoomNearCmdString, value, qualifier)

    def __CheckPowerManagement(self, response):

        respex = search(self.PowerandPresentation, response.encode())
        if respex:
            if 'SS,true\r\n' in response or 'SS,false\r\n' in response:
                self.__MatchPowerManagement(respex, None)
                response = ''
            elif 'active' or 'CS' or 'IC' in response:
                self.__MatchCallStatus(respex, None)
                response = ''
            elif 'PS,0,1,Initiated,No,' in response:
                self.__MatchPresentation(respex, None)
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command == 'Presentation':
                self.Send(commandstring)
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'$')

                if not res:
                    self.Error(['Invalid/unexpected response'])
                elif command == 'Password':
                    return res.decode()
                else:
                    return self.__CheckPowerManagement(res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            if self.DeviceState == 'Ready':
                if self.Authentication in ['Not Needed', 'Logged In']:
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'$')

                    if not res:
                        self.WriteStatus('DeviceStatus', 'Not Ready', qualifier)
                        return ''
                    else:
                        self.WriteStatus('DeviceStatus', 'Ready', qualifier)
                        return self.__CheckPowerManagement(res.decode())
                elif self.Authentication == 'Failed':
                    self.WriteStatus('DeviceStatus', 'Not Ready', qualifier)
                    self.Discard('Authentication Failed: Inappropriate Command ' + command)
                elif self.Authentication == 'None':
                    self.Discard('Waiting for authentication process')
            else:
                self.WriteStatus('DeviceStatus', 'Not Ready', qualifier)
                self.Discard('Device is not ready to receive commands.')

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.Authentication = 'Not Needed'

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authentication = 'Not Needed'
        self.DeviceState = 'Ready'

    def lfsz_Room(self):

        self.InputState = {
            'HD1': 'hd0',
            'HDMI1': 'hdmi0',
            'HDMI2': 'hdmi1',
            'COMP': 'comp0',
            'DVI': 'dvi0',
        }

        self.InputStateUpdate = {
            'hd0': 'HD1',
            'hdmi0': 'HDMI1',
            'hdmi1': 'HDMI2',
            'comp0': 'COMP',
            'dvi0': 'DVI',
        }

    def lfsz_Express(self):

        self.InputState = {
            'HDMI1': 'hdmi0',
            'DVI': 'dvi0',
        }

        self.InputStateUpdate = {
            'hdmi0': 'HDMI1',
            'dvi0': 'DVI',
        }

    def lfsz_Team(self):

        self.InputState = {
            'HD1': 'hd0',
            'HDMI1': 'hdmi0',
            'DVI': 'dvi0',
        }

        self.InputStateUpdate = {
            'hd0': 'HD1',
            'hdmi0': 'HDMI1',
            'dvi0': 'DVI',
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
            if command == 'DeviceStatus' and value == 'Ready':
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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
        self.qualifier_name = 'Position'
        self._qualifier_type = 'Enum'
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
