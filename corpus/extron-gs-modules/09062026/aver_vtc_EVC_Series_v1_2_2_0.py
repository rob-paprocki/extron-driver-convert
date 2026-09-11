from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import compile, findall, search
from json import loads


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

        self.devicePassword = None
        self._NumberOfPhonebookSearch = 5

        self.Models = {
            'EVC900': self.aver_12_856,
            'EVC300': self.aver_12_856,
            'EVC100': self.aver_12_856_100,
            'EVC130': self.aver_12_856_130,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraInputSwitch': {'Status': {}},
            'CameraPanTilt': {'Status': {}},
            'CameraPresetLoad': {'Status': {}},
            'CameraPresetSave': {'Status': {}},
            'CameraZoom': {'Status': {}},
            'Hook': {'Status': {}},
            'IncomingCallStatus': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'LocalMuteStatus': {'Status': {}},
            'MicGain': {'Status': {}},
            'MicInput': {'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookDial': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'VideoSwitchLayout': {'Status': {}},
            'VideoSwitchSingleDualMonitor': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Authenticated'

        self.Phonebook = PhonebookGenerator()
        self.StartingEntry = 1
        self.NumberOfButton = 0
        self.namedict = {}
        self.Phonebook.UpdatePhonebook([])
        self.Advance = True

        self.Responses = compile('\*r data=\"(.+)\"')
        self.PhonebookEntry = compile('alias=\"?(\{["a-zA-Z.0-9,:\s{\}]+})\"')

        self.AddMatchString(compile(b'Enter \? for help\r\n'), self.__MatchPasswordPrompt, None)
        self.AddMatchString(compile(b'login \w+\r\n\r\n\*r ok\r\n\r\n'), self.__MatchPasswordAck, None)
        self.AddMatchString(compile(b'login \w+\r\n\r\n\*r error'), self.__MatchPasswordNak, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = value

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPasswordPrompt(self, match, tag):
        self.SetPassword(None, None)

    def __MatchPasswordAck(self, match, tag):    
        self.Authenticated = 'Authenticated'
        print('Authenticated')

    def __MatchPasswordNak(self, match, tag):
        self.Error(['Log in failed. Please supply proper password'])
        self.Authenticated = 'Not Authenticated'

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'set System/AspectRatio 0\r',
            '1024 x 768 (4:3)': 'set System/AspectRatio 1\r',
            '1280 x 720 (16:9)': 'set System/AspectRatio 2\r'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': '1024 x 768 (4:3)',
            '2': '1280 x 720 (16:9)'
        }

        AspectRatioCmdString = 'get System/AspectRatio\r'
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            'On': 'set Call/AutoAnswer 1\r',
            'Off': 'set Call/AutoAnswer 0\r',
            'On with Mute': 'set Call/AutoAnswer 2\r',
            'Do Not Disturb': 'set Call/AutoAnswer 3\r'
        }

        AutoAnswerCmdString = ValueStateValues[value]
        self.__SetHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)

    def UpdateAutoAnswer(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off',
            '2': 'On with Mute',
            '3': 'Do Not Disturb'
        }

        AutoAnswerCmdString = 'get Call/AutoAnswer\r'
        res = self.__UpdateHelper('AutoAnswer', AutoAnswerCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                self.WriteStatus('AutoAnswer', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Answer: Invalid/unexpected response'])

    def UpdateCallStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Connected',
            '0': 'Not In Call'
        }

        CallStatusCmdString = 'get Call/Connected[1]\r'
        res = self.__UpdateHelper('CallStatus', CallStatusCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                self.WriteStatus('CallStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Call Status: Invalid/unexpected response'])

    def SetCameraInputSwitch(self, value, qualifier):

        CameraInputSwitchCmdString = 'action Camera/InputSourceSwitch\r'
        self.__SetHelper('CameraInputSwitch', CameraInputSwitchCmdString, value, qualifier)

    def SetCameraPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Left': 'action Camera/StepMove/Left\r',
            'Right': 'action Camera/StepMove/Right\r',
            'Stop': 'action Camera/StopMove\r',
            'Up': 'action Camera/StepMove/Up\r',
            'Down': 'action Camera/StepMove/Down\r'
        }

        CameraPanTiltCmdString = ValueStateValues[value]
        self.__SetHelper('CameraPanTilt', CameraPanTiltCmdString, value, qualifier)

    def SetCameraPresetLoad(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetLoadCmdString = 'set Camera/LoadPreset {0}\r'.format(value)
            self.__SetHelper('CameraPresetLoad', CameraPresetLoadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetLoad')

    def SetCameraPresetSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            CameraPresetSaveCmdString = 'set Camera/SavePreset {0}\r'.format(value)
            self.__SetHelper('CameraPresetSave', CameraPresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetSave')

    def SetCameraZoom(self, value, qualifier):

        ValueStateValues = {
            'Zoom In': 'action Camera/StepMove/ZoomIn\r',
            'Zoom Out': 'action Camera/StepMove/ZoomOut\r',
            'Stop': 'action Camera/StopMove\r'
        }

        CameraZoomCmdString = ValueStateValues[value]
        self.__SetHelper('CameraZoom', CameraZoomCmdString, value, qualifier)

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Answer': 'action Call/AnswerCall\r',
            'Reject': 'action Call/RejectCall\r',
            'Disconnect': 'action Call/DisconnectAll\r',
        }

        HookCmdString = ValueStateValues[value]
        self.__SetHelper('Hook', HookCmdString, value, qualifier)

    def UpdateIncomingCallStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'Ringing',
            '1': 'Not Ringing'
        }

        IncomingCallStatusCmdString = 'get Call/CallInStatus\r'
        res = self.__UpdateHelper('IncomingCallStatus', IncomingCallStatusCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                self.WriteStatus('IncomingCallStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Incoming Call Status: Invalid/unexpected response'])

    def SetIRRemoteEmulation(self, value, qualifier):

        IRRemoteEmulationCmdString = self.IRRemoteEmuStates[value]
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def UpdateLocalMuteStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        LocalMuteStatusCmdString = 'get Call/LocalMuted\r'
        res = self.__UpdateHelper('LocalMuteStatus', LocalMuteStatusCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                    self.WriteStatus('LocalMuteStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Local Mute Status: Invalid/unexpected response'])

    def SetMicGain(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 9
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicGainCmdString = 'set Audio/MicGain {0}\r'.format(value - 1)
            self.__SetHelper('MicGain', MicGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicGain')

    def UpdateMicGain(self, value, qualifier):

        MicGainCmdString = 'get Audio/MicGain\r'
        res = self.__UpdateHelper('MicGain', MicGainCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = int(mGroup.group(1))
                    self.WriteStatus('MicGain', value + 1, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mic Gain: Invalid/unexpected response'])

    def SetMicInput(self, value, qualifier):

        ValueStateValues = {
            'Mic In': 'set Audio/MicInput 0\r',
            'Audio In with AEC': 'set Audio/MicInput 1\r',
            'Audio In without AEC': 'set Audio/MicInput 2\r'
        }

        MicInputCmdString = ValueStateValues[value]
        self.__SetHelper('MicInput', MicInputCmdString, value, qualifier)

    def UpdateMicInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Mic In',
            '1': 'Audio In with AEC',
            '2': 'Audio In without AEC'
        }

        MicInputCmdString = 'get Audio/MicInput\r'
        res = self.__UpdateHelper('MicInput', MicInputCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = ValueStateValues[mGroup.group(1)]
                    self.WriteStatus('MicInput', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Mic Input: Invalid/unexpected response'])

    def SetPhonebookDial(self, value, qualifier):
        self.Debug = True

        number = value        
        try:
            self.namedict[number]
        except KeyError:
            self.Discard('Invalid Command for SetPhonebookDial')
        else:
            PhonebookDialCmdString = 'set Call/CallOutTo {0}\r'.format(self.namedict[number])
            self.__SetHelper('PhonebookDial', PhonebookDialCmdString, value, qualifier)

    def SetPhonebookSearch(self, value, qualifier):
        self.Debug = True

        self.StartingEntry = 1
        entries = self.Phonebook.GetEntry(self.StartingEntry, self._NumberOfPhonebookSearch, )
        button = 1

        if entries and self.namedict:
            for i in range(0, self._NumberOfPhonebookSearch):
                entry = entries[i]
                name = entry.split('|')
                self.namedict[name[0]] = entry
                self.WriteStatus('PhonebookSearchResult', name[0], {'Button': button})
                button += 1
        else:
            self.Discard('Invalid Command for SetPhonebookSearch')

    def SetPhonebookSearchSet(self, value, qualifier):
        self.Debug = True

        if 1 <= value <= self._NumberOfPhonebookSearch:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number != '***End of list***':
                self.SetPhonebookDial(number, None)
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookNavigation(self, value, qualifier):
        self.Debug = True

        if value in ['Up', 'Down', 'Page Up', 'Page Down']:
            if 'Page' in value:
                NumberOfAdvance = self._NumberOfPhonebookSearch
            else:
                NumberOfAdvance = 1

            if 'Down' in value and self.Advance:
                self.StartingEntry += NumberOfAdvance
            elif 'Up' in value:
                self.StartingEntry -= NumberOfAdvance

            if self.StartingEntry < 1:
                self.StartingEntry = 1

            self.Advance = True
            entries = self.Phonebook.GetEntry(self.StartingEntry, self._NumberOfPhonebookSearch, )
            if '***End of list***' in entries:
                self.Advance = False

            if self.namedict:
                button = 1
                for i in range(0, self._NumberOfPhonebookSearch):
                    entry = entries[i]
                    name = entry.split('|')
                    self.namedict[name[0]] = entry
                    self.WriteStatus('PhonebookSearchResult', name[0], {'Button': button})
                    button += 1
            else:
                self.Discard('Invalid Command for SetPhonebookNavigation')
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookUpdate(self, value, qualifier):
        self.Debug = True

        self.UpdatePhonebookUpdate(None, None)

    def UpdatePhonebookUpdate(self, value, qualifier):
        self.Debug = True

        if self.Authenticated == 'Authenticated':
            res = self.SendAndWait('query Phonebook/ContactList\r', 10, deliTag=b'end\r')
            if res:
                res = res.decode()
                newList = []
    
                y = []
                JsonList = findall(self.PhonebookEntry, res)
                for i in range(len(JsonList)):
                    y.append(loads(JsonList[i]))
                newList = [i['name'] + '|' + (i['sip'] + '|' + i['bitrate'] + '|' + 'sip' if i['sip'] else i['h323'] + '|' + i['bitrate'] + '|' + 'h323') for i in y]
                self.Phonebook.UpdatePhonebook(newList)
                self.StartingEntry = 1
                self.Advance = True
                entries = self.Phonebook.GetEntry(self.StartingEntry, self._NumberOfPhonebookSearch, )
                if '***End of list***' in entries:
                    self.Advance = False
                button = 1
                for i in range(0, self._NumberOfPhonebookSearch):
                    entry = entries[i]
                    name = entry.split('|')
                    self.namedict[name[0]] = entry
                    self.WriteStatus('PhonebookSearchResult', name[0], {'Button': button})
                    button += 1
        else:
            self.Discard('Inappropriate Command PhonebookUpdate')

    def SetVideoSwitchLayout(self, value, qualifier):

        VideoSwitchLayoutCmdString = 'action Video/SwitchLayout\r'
        self.__SetHelper('VideoSwitchLayout', VideoSwitchLayoutCmdString, value, qualifier)

    def SetVideoSwitchSingleDualMonitor(self, value, qualifier):

        VideoSwitchSingleDualMonitorCmdString = 'action Video/SwitchSingleDualMonitor\r'
        self.__SetHelper('VideoSwitchSingleDualMonitor', VideoSwitchSingleDualMonitorCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 32
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'set Audio/Volume {0}\r'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'get Audio/Volume\r'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                mGroup = self.Responses.search(res)
                if mGroup:
                    value = int(mGroup.group(1))
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response:
            if 'invalid access code' in response:
                self.Error(['Invalid password'])
                response = ''
            elif 'too many users' in response:
                self.Error(['There are too many users'])
                response = ''
            elif 'error invalid object' in response:
                self.Error(['{0}: Invalid object'.format(sourceCmdName)])
                response = ''
            elif 'error invalid argument' in response:
                self.Error(['{0}: Invalid argument'.format(sourceCmdName)])
                response = ''
            elif 'error command error' in response:
                self.Error(['{0}: Command error'.format(sourceCmdName)])
                response = ''
            elif 'error object disabled' in response:
                self.Error(['{0}: Object disabled'.format(sourceCmdName)])
                response = ''
            elif 'error resource busy' in response:
                self.Error(['Resource busy'])
                response = ''
            elif 'error invalid session' in response:
                self.Error(['Invalid session'])
                response = ''
            elif 'error' in response:
                self.Error(['Unknown error occured'])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'end\r')
            if not res:
                res = ''
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated == 'Authenticated':
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

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'end\r')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode())
        else:
            self.Discard('Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.Authenticated = 'Not Authenticated'

    def aver_12_856_100(self):

        self.IRRemoteEmuStates = {
            '0': 'action UI/IR/0\r',
            '1': 'action UI/IR/1\r',
            '2': 'action UI/IR/2\r',
            '3': 'action UI/IR/3\r',
            '4': 'action UI/IR/4\r',
            '5': 'action UI/IR/5\r',
            '6': 'action UI/IR/6\r',
            '7': 'action UI/IR/7\r',
            '8': 'action UI/IR/8\r',
            '9': 'action UI/IR/9\r',
            '.': 'action UI/IR/dot\r',
            'Enter': 'action UI/IR/enter\r',
            'Back': 'action UI/IR/back\r',
            'Up': 'action UI/IR/up\r',
            'Down': 'action UI/IR/down\r',
            'Left': 'action UI/IR/left\r',
            'Right': 'action UI/IR/right\r',
            'Call': 'action UI/IR/call\r',
            'Hang Up': 'action UI/IR/hangup\r',
            'Home': 'action UI/IR/home\r',
            'Info': 'action UI/IR/info\r',
            'Present VGA': 'action UI/IR/present_vga\r',
            'Phonebook': 'action UI/IR/phonebook\r',
            'Layout': 'action UI/IR/layout\r',
            'Dual': 'action UI/IR/dual\r',
            'Input': 'action UI/IR/input\r',
            'Far': 'action UI/IR/far\r',
            'Preset': 'action UI/IR/preset\r',
            'Zoom In': 'action UI/IR/zoom_in\r',
            'Zoom Out': 'action UI/IR/zoom_out\r',
            'Mute': 'action UI/IR/mute\r',
            'Volume Up': 'action UI/IR/vol_up\r',
            'Volume Down': 'action UI/IR/vol_down\r',
            'Delete': 'action UI/IR/delete\r',
            'Keypad': 'action UI/IR/keypad\r',
            'Resolution': 'action UI/IR/resolution\r'
        }

    def aver_12_856_130(self):

        self.IRRemoteEmuStates = {
            '0': 'action UI/IR/0\r',
            '1': 'action UI/IR/1\r',
            '2': 'action UI/IR/2\r',
            '3': 'action UI/IR/3\r',
            '4': 'action UI/IR/4\r',
            '5': 'action UI/IR/5\r',
            '6': 'action UI/IR/6\r',
            '7': 'action UI/IR/7\r',
            '8': 'action UI/IR/8\r',
            '9': 'action UI/IR/9\r',
            '.': 'action UI/IR/dot\r',
            'Enter': 'action UI/IR/enter\r',
            'Back': 'action UI/IR/back\r',
            'Up': 'action UI/IR/up\r',
            'Down': 'action UI/IR/down\r',
            'Left': 'action UI/IR/left\r',
            'Right': 'action UI/IR/right\r',
            'Call': 'action UI/IR/call\r',
            'Hang Up': 'action UI/IR/hangup\r',
            'Home': 'action UI/IR/home\r',
            'Info': 'action UI/IR/info\r',
            'Present VGA': 'action UI/IR/present_vga\r',
            'Phonebook': 'action UI/IR/phonebook\r',
            'Layout': 'action UI/IR/layout\r',
            'Dual': 'action UI/IR/dual\r',
            'Input': 'action UI/IR/input\r',
            'Far': 'action UI/IR/far\r',
            'Preset': 'action UI/IR/preset\r',
            'Zoom In': 'action UI/IR/zoom_in\r',
            'Zoom Out': 'action UI/IR/zoom_out\r',
            'Mute': 'action UI/IR/mute\r',
            'Volume Up': 'action UI/IR/vol_up\r',
            'Volume Down': 'action UI/IR/vol_down\r',
            'Record': 'action UI/IR/record\r',
            'Delete': 'action UI/IR/delete\r',
            'Keypad': 'action UI/IR/keypad\r',
            'Resolution': 'action UI/IR/resolution\r'
        }

    def aver_12_856(self):

        self.IRRemoteEmuStates = {
            '0': 'action UI/IR/0\r',
            '1': 'action UI/IR/1\r',
            '2': 'action UI/IR/2\r',
            '3': 'action UI/IR/3\r',
            '4': 'action UI/IR/4\r',
            '5': 'action UI/IR/5\r',
            '6': 'action UI/IR/6\r',
            '7': 'action UI/IR/7\r',
            '8': 'action UI/IR/8\r',
            '9': 'action UI/IR/9\r',
            '.': 'action UI/IR/dot\r',
            'Enter': 'action UI/IR/enter\r',
            'Back': 'action UI/IR/back\r',
            'Up': 'action UI/IR/up\r',
            'Down': 'action UI/IR/down\r',
            'Left': 'action UI/IR/left\r',
            'Right': 'action UI/IR/right\r',
            'Call': 'action UI/IR/call\r',
            'Hang Up': 'action UI/IR/hangup\r',
            'Home': 'action UI/IR/home\r',
            'Info': 'action UI/IR/info\r',
            'Present': 'action UI/IR/present\r',
            'Phonebook': 'action UI/IR/phonebook\r',
            'Layout': 'action UI/IR/layout\r',
            'Dual': 'action UI/IR/dual\r',
            'Input': 'action UI/IR/input\r',
            'Far': 'action UI/IR/far\r',
            'Preset': 'action UI/IR/preset\r',
            'Zoom In': 'action UI/IR/zoom_in\r',
            'Zoom Out': 'action UI/IR/zoom_out\r',
            'Mute': 'action UI/IR/mute\r',
            'Volume Up': 'action UI/IR/vol_up\r',
            'Volume Down': 'action UI/IR/vol_down\r',
            'Record': 'action UI/IR/record\r',
            'Delete': 'action UI/IR/delete\r',
            'Keypad': 'action UI/IR/keypad\r',
            'Resolution': 'action UI/IR/resolution\r'
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
        

class PhonebookGenerator:

    def __init__(self):
        self.Phonebook = []

    def UpdatePhonebook(self, newBook):

        self.Phonebook = sorted(newBook)

    def GetEntry(self, start, number, searchName=None):

        retList = []
        book = []
        end = start + number
        if searchName:
            for k in self.Phonebook:
                if k.lower().find(searchName.lower()) == 0 or k.lower().find(' ' + searchName.lower()) > 0:
                    book.append(k)
        else:
            book = self.Phonebook

        i = 1
        for name in book:
            if start <= i < end:
                retList.append(name)
            i += 1

        retList = sorted(retList)
        if i <= end:
            retList.append('***End of list***')
            i += 1
            for i in range(len(retList), end):
                retList.append('')
        return retList
