from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, match, findall, search
from extronlib.system import ProgramLog, Wait

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
        self._NumberOfPhonebookSearch = 5
        self.deviceUsername = 'debug'
        self.devicePassword = 'Change_Me'
        self.Models = {}
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallEnd': {'Status': {}},
            'CallStartCommand': {'Parameters': ['Call Type', 'Bandwidth', 'Number'], 'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraAutoFocus': {'Parameters': ['Camera', 'Camera ID'], 'Status': {}},
            'CameraFocus': {'Parameters': ['Camera', 'Camera ID'], 'Status': {}},
            'CameraNavigationControl': {'Parameters': ['Camera', 'Camera ID'], 'Status': {}},
            'CameraPreset': {'Parameters': ['Camera', 'Action', 'Camera ID'], 'Status': {}},
            'CameraSource': {'Parameters': ['Camera'], 'Status': {}},
            'CameraZoom': {'Parameters': ['Camera', 'Camera ID'], 'Status': {}},
            'IREmulation': {'Parameters': ['Action'], 'Status': {}},
            'Layout': {'Status': {}},
            'MicMute': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'Presentation': {'Status': {}},
            'SpeakerVolume': {'Status': {}},
        }

        self.LoginSuccess = False
        self.CallFromAddress = False

        self.StartingEntry = 1
        self.EndEntry = 0
        self.Advance = True

        self.NumberOfButton = 0
        self.nameList = []

        self.PhoneResponsePattern = compile(r'ID:\d+  Name:([\S\s]+?)  PName')
        self.PhoneResponseDialPattern = compile(r'ID:(\d+)  Name:([\S\s]+?)  PName')
        self.CallStatusPattern = compile(r'[\S\s]+The endpoint is ([\S\s]+)\.')
        self.NumberPattern = compile(r'([0-9 \.\+\*#]|'')')  

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'.*Enter your login name : \n\r'), self.__MatchName, None)
            self.AddMatchString(compile(b'.*Enter your password : \n\r'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'.*Success!!!\r\n'), self.__MatchLoginSuccess, None)
            self.AddMatchString(compile(b'\r\nlogon auth fail!!!'), self.__MatchLoginFailure, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 15:
            self.NumberOfButton = int(value)

    def __MatchName(self, match, tag):
        if self.deviceUsername is not None:
            self.Send('{0}\r'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')    

    def __MatchPassword(self, match, tag):
        if self.devicePassword is not None:
            self.Send('{0}\r'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')    

    def __MatchLoginSuccess(self, match, tag):
        self.LoginSuccess = True

    def __MatchLoginFailure(self, match, tag):

        self.LoginSuccess = False
        self.SetSendName(None, None)
        self.Error(['Login Failed. Please enter correct Username and Password.'])

    def SetCallEnd(self, value, qualifier):

        CallEndCmdString = 'mc endcall\r'
        self.__SetHelper('CallEnd', CallEndCmdString, value, qualifier)

    def SetCallStartCommand(self, value, qualifier):

        CallTypeStates = ['H.323', 'SIP', 'E1', 'ISDN', 'AUTO']

        BandwidthStates = {
            '64 kbps': '1',
            '128 kbps': '2',
            '192 kbps': '3',
            '256 kbps': '4',
            '320 kbps': '5',
            '384 kbps': '6',
            '512 kbps': '7',
            '768 kbps': '8',
            '1024 kbps': '9',
            '1152 kbps': '10',
            '1472 kbps': '11',
            '1536 kbps': '12',
            '1920 kbps': '13',
            '2048 kbps': '14',
            '3 Mbps': '15',
            '4 Mbps': '16',
            '5 Mbps': '17',
            '6 Mbps': '18',
            '7 Mbps': '19',
            '8 Mbps': '20',
            '2 x 64 kbps': '21',
            '3 x 64 kbps': '22',
            '4 x 64 kbps': '23',
            '5 x 64 kbps': '24',
            '6 x 64 kbps': '25'
        }

        CallStartCommandCmdString = ''
        if not self.CallFromAddress:
            callType = qualifier['Call Type']
            bandwidth = qualifier['Bandwidth']
            if callType == '4E1' and bandwidth in BandwidthStates:
                CallStartCommandCmdString = 'mc call 4E1 {}\r'.format(BandwidthStates[bandwidth])
            elif callType in ['H.323PHONE', 'SIPPHONE', 'PSTN']:
                number = qualifier['Number']
                if number:
                    CallStartCommandCmdString = 'mc call {} {}\r'.format(callType, number)
            elif callType in CallTypeStates and bandwidth in BandwidthStates:
                number = qualifier['Number']
                if number:
                    CallStartCommandCmdString = 'mc call {} {} {}\r'.format(callType, number, BandwidthStates[bandwidth])

            if CallStartCommandCmdString:
                self.__SetHelper('CallStartCommand', CallStartCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCallStartCommand')
        elif self.CallFromAddress: 
            number = qualifier['Number']
            CallStartCommandCmdString = 'mc callfromaddr {}\r'.format(number)
            if CallStartCommandCmdString:
                self.__SetHelper('CallStartCommand', CallStartCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetCallStartCommand')

    def UpdateCallStatus(self, value, qualifier):

        ValueStateValues = {
            'Not In A Call': 'Not In A Call',
            'In A Point-To-Point Conference': 'In A Point-To-Point Conference',
            'In A Multipoint Conference Held On A Remote Mcu': 'In A Multipoint Conference Held On A Remote MCU',
            'In A Multipoint Conference Held On The Local Mcu': 'In A Multipoint Conference Held On The Local MCU'
        }
        CallStatusCmdString = 'mc callstate\r'
        res = self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
        if res:
            try:
                found = match(self.CallStatusPattern, res)
                self.WriteStatus('CallStatus', ValueStateValues[found.group(1).title()], qualifier)
            except (KeyError, AttributeError):
                self.Error(['Call Status: Invalid/unexpected response'])

    def SetCameraAutoFocus(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        CameraIDStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop'
        }

        CamState = qualifier['Camera']
        CamID = qualifier['Camera ID']
        if CamState in CameraStates and CamID in CameraIDStates:
            CameraAutoFocusCmdString = 'mnt Cameractrl {} {} focusauto {}\r'.format(CameraIDStates[CamID], CameraStates[CamState], ValueStateValues[value])
            self.__SetHelper('CameraAutoFocus', CameraAutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraAutoFocus')

    def SetCameraFocus(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        CameraIDStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        ValueStateValues = {
            'Start In': 'focusin start',
            'Start Out': 'focusout start',
            'Stop In': 'focusin stop',
            'Stop Out': 'focusout stop'
        }

        CamState = qualifier['Camera']
        CamID = qualifier['Camera ID']
        if CamState in CameraStates and CamID in CameraIDStates:
            CameraFocusCmdString = 'mnt Cameractrl {} {} {}\r'.format(CameraIDStates[CamID], CameraStates[CamState], ValueStateValues[value])
            self.__SetHelper('CameraFocus', CameraFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFocus')

    def SetCameraNavigationControl(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        CameraIDStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        ValueStateValues = {
            'Start Left': 'left start',
            'Stop Left': 'left stop',
            'Start Right': 'right start',
            'Stop Right': 'right stop',
            'Start Up': 'up start',
            'Stop Up': 'up stop',
            'Start Down': 'down start',
            'Stop Down': 'down stop',
            'Start Home': 'home start',
            'Stop Home': 'home stop'
        }

        CamState = qualifier['Camera']
        CamID = qualifier['Camera ID']
        if CamState in CameraStates and CamID in CameraIDStates:
            CameraNavigationControlCmdString = 'mnt Cameractrl {} {} {}\r'.format(CameraIDStates[CamID], CameraStates[CamState], ValueStateValues[value])
            self.__SetHelper('CameraNavigationControl', CameraNavigationControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNavigationControl')

    def SetCameraPreset(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        ActionStates = {
            'Save': '0',
            'Recall': '1'
        }

        CameraIDStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        CamState = qualifier['Camera']
        CamID = qualifier['Camera ID']
        action = qualifier['Action']
        if CamState in CameraStates and CamID in CameraIDStates and action in ActionStates and 1 <= int(value) <= 30:
            CameraPresetCmdString = 'mnt CtrlCamPreset {} {} {} {}\r'.format(CameraIDStates[CamID], CameraStates[CamState], ActionStates[action], value)
            self.__SetHelper('CameraPreset', CameraPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPreset')

    def SetCameraSource(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        CamState = qualifier['Camera']
        if CamState in CameraStates:
            CameraSourceCmdString = 'mnt SelectCamSource {} {}\r'.format(CameraStates[CamState], ValueStateValues[value])
            self.__SetHelper('CameraSource', CameraSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraSource')

    def SetCameraZoom(self, value, qualifier):

        CameraStates = {
            'Local': '0',
            'Remote': '1'
        }

        CameraIDStates = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7'
        }

        ValueStateValues = {
            'Start In': 'zoomin start',
            'Start Out': 'zoomout start',
            'Stop In': 'zoomin stop',
            'Stop Out': 'zoomout stop'
        }

        CamState = qualifier['Camera']
        CamID = qualifier['Camera ID']
        if CamState in CameraStates and CamID in CameraIDStates:
            CameraZoomCmdString = 'mnt Cameractrl {} {} {}\r'.format(CameraIDStates[CamID], CameraStates[CamState], ValueStateValues[value])
            self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraZoom')

    def SetIREmulation(self, value, qualifier):

        ActionStates = {
            'Press': 'press',
            'Release': 'release',
            'Press & Release': 'action',
            'Press & Hold': 'longpress'
        }

        ValueStateValues = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'OK': 'ok',
            'Home': 'home',
            'Power': 'power',
            'Layout': 'layout',
            'Camera': 'camera',
            'Display': 'display',
            'Presentation': 'presentation',
            'Mute': 'mute',
            'Volume Up': 'volumeup',
            'Volume Down': 'volumedown',
            'Zoom In': 'zoomin',
            'Zoom Out': 'zoomout',
            'Return': 'return',
            'Call': 'call',
            'Hangup': 'hangup',
            'Help': 'help',
            'Delete': 'delete',
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
            'Swap': 'swap',
            'Resize': 'resize',
            'Conference': 'conf',
            'Preset': 'preset',
            'Speaker': 'speaker',
            'Page Up': 'pageup',
            'Page Down': 'pagedown',
            'Address': 'address',
            '*': 'star',
            '#': 'pound',
            'Second Call': 'secondcall'
        }

        action = qualifier['Action']
        if action in ActionStates:
            IREmulationCmdString = 'rc key {} {}\r'.format(ValueStateValues[value], ActionStates[action])
            self.__SetHelper('IREmulation', IREmulationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetLayout(self, value, qualifier):

        ValueStateValues = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '10': '9',
            '11': '10',
            '12': '11',
            '13': '12',
            '14': '13',
            '15': '14',
            '16': '15',
            '17': '16',
            '18': '17',
            '19': '18',
            '20': '19'
        }

        LayoutCmdString = 'mc SetLayout {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Layout', LayoutCmdString, value, qualifier)

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        MicMuteCmdString = 'mnt audio SetMicState {}\r'.format(ValueStateValues[value])
        self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)

    def SetPhonebookNavigation(self, value, qualifier):

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self.NumberOfButton
            else:
                NumberOfAdvance = 1

            if 'Down' in value:
                if self.Advance:
                    self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.EndEntry = self.StartingEntry + self.NumberOfButton - 1

            numOfName = len(self.nameList)
            index = self.StartingEntry - 1
            button = 1
            self.Advance = True
            while index < numOfName and index < self.EndEntry:
                name = self.nameList[index]
                self.WriteStatus('PhonebookSearchResult', name, {'Button': int(button)})
                button = button + 1
                index = index + 1

            if button <= self.NumberOfButton:
                self.Advance = False
                self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
                button = button + 1
                for i in range(button, int(self.NumberOfButton) + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self.NumberOfButton
        }

        #if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
        name = self.ReadStatus('PhonebookSearchResult', {'Button': value})
        res = self.__SetHelper('PhonebookSearchSet', 'data addr findbyname {}\r'.format(name), None, qualifier)
        if res:
            IDnameList = findall(self.PhoneResponseDialPattern, res)
            if IDnameList and IDnameList[0][1] == name:
                self.CallFromAddress = True
        #    self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        self.SetPhonebookUpdateHandler(value, qualifier)

    def SetPhonebookUpdateHandler(self, value, qualifier):
        searchStr = value
        if searchStr:
            if searchStr.isdigit() and (1 <= int(searchStr) <= 5000):
                PhonebookUpdateCmdString = 'data addr findbyid {}\r'.format(searchStr)
            else:
                PhonebookUpdateCmdString = 'data addr findbyname {}\r'.format(searchStr)
        else:
            PhonebookUpdateCmdString = 'data addr readall\r'
        res = self.__SetHelper('PhonebookUpdate', PhonebookUpdateCmdString, None, qualifier)
        if res:
            self.nameList = findall(self.PhoneResponsePattern, res)
            searchMax = len(self.nameList)
            if searchMax > self.NumberOfButton:
                searchMax = self.NumberOfButton
            button = 1
            for name in range(0, searchMax):  
                name = self.nameList[button - 1]
                self.WriteStatus('PhonebookSearchResult', name, {'Button': button})
                button = button + 1

            if button <= self.NumberOfButton:
                self.WriteStatus('PhonebookSearchResult', '***End of list***', {'Button': button})
                button = button + 1
                for i in range(button, self.NumberOfButton + 1):
                    self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
        else:
            self.__MatchNoContact(None, None)

    def __MatchNoContact(self, match, tag):
        button = 1
        self.Advance = False
        self.WriteStatus('PhonebookSearchResult', '***Not Available***', {'Button': button})
        button = button + 1
        for i in range(button, int(self.NumberOfButton) + 1):
            self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPresentation(self, value, qualifier):

        ValueStateValues = {
            'Start': '1',
            'Stop': '0',
        }

        PresentationCmdString = 'mc sendaux {}\r'.format(ValueStateValues[value])
        self.__SetHelper('Presentation', PresentationCmdString, value, qualifier)

    def SetSpeakerVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 21
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SpeakerVolumeCmdString = 'mnt audio SetVolume 0 {}\r'.format(value)
            self.__SetHelper('SpeakerVolume', SpeakerVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSpeakerVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            if command in ['PhonebookSearchSet', 'PhonebookUpdate']:                
                res = self.SendAndWait(commandstring, 10, deliTag=b'->')
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'->')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                if command in ['PhonebookSearchSet', 'PhonebookUpdate']:
                    return self.__CheckResponseForErrors(command, res.decode())
                else:
                    res = self.__CheckResponseForErrors(command, res.decode())

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'->')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())            

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.LoginSuccess = False
        self.CallFromAddress = False

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
        
