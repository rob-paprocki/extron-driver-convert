from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
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

        self.devicePassword = None
        self._NumberOfPhonebookSearch = 5
        self._PhonebookSearchOffset = 50

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'CallInfoName': {'Parameters': ['Call'], 'Status': {}},
            'CallInfoNumber': {'Parameters': ['Call'], 'Status': {}},
            'CallState': {'Parameters': ['Call'], 'Status': {}},
            'CallType': {'Parameters': ['Call'], 'Status': {}},
            'CameraFarPanTilt': {'Status': {}},
            'CameraFarSource': {'Status': {}},
            'CameraFarTracking': {'Status': {}},
            'CameraFarZoom': {'Status': {}},
            'CameraNearPanTilt': {'Status': {}},
            'CameraNearSource': {'Status': {}},
            'CameraNearTracking': {'Status': {}},
            'CameraNearZoom': {'Status': {}},
            'CameraPresetFarRecall': {'Status': {}},
            'CameraPresetFarSave': {'Status': {}},
            'CameraPresetNearRecall': {'Status': {}},
            'CameraPresetNearSave': {'Status': {}},
            'ConfigPresentation': {'Parameters': ['Monitor'], 'Status': {}},
            'DTMF': {'Status': {}},
            'DualMonitor': {'Status': {}},
            'Hook': {'Parameters': ['Speed'], 'Status': {}},
            'IREmulation': {'Status': {}},
            'MaxTimeInCall': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookNavigation': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookSearch': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PhonebookUpdate': {'Parameters': ['Phonebook Type'], 'Status': {}},
            'PictureInPicture': {'Status': {}},
            'PictureInPictureLocation': {'Status': {}},
            'Reboot': {'Status': {}},
            'Sleep': {'Status': {}},
            'SleepTime': {'Status': {}},
            'TransmitLevel': {'Status': {}},
            'TransmitMute': {'Status': {}},
            'VisualConcert': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.Advance = False

        self.stat = compile('callinfo:(.*):(.*):(.*):.*:(.*):(muted|notmuted):.*:(\w*call|\w*only)\r\n')
        self.gdsName = compile('abk (\d+)\. (.+) spd:')
        self.MinLabel = 0
        self.MaxLabel = 5
        self.lastindex = 0
        self.numOfName = 0
        self.nameDict = {}

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(compile(b'error: (.*)\r\n'), self.__MatchError, None)
            self.AddMatchString(compile(b'autoanswer (yes|no|donotdisturb)\r\n'), self.__MatchAutoAnswer, None)
            self.AddMatchString(compile(b'callinfo begin[\s\S]+callinfo end\r\n'), self.__MatchCallState, None)
            self.AddMatchString(compile(b'system is not in a call\r\n'), self.__MatchCallStateInactive, None)
            self.AddMatchString(compile(b'camera far source (-?\d)\r\n'), self.__MatchCameraFarSource, None)
            self.AddMatchString(compile(b'camera far tracking (on|off|to_presets)'), self.__MatchCameraFarTracking, None)
            self.AddMatchString(compile(b'camera near source (-?\d)\r\n'), self.__MatchCameraNearSource, None)
            self.AddMatchString(compile(b'camera near tracking (on|off|to_presets)'), self.__MatchCameraNearTracking, None)
            self.AddMatchString(compile(b'configpresentation monitor([12]):([-\w]+)\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'configpresentation monitor([12]) ([-\w]+) succeeded\r\n'), self.__MatchConfigPresentation, None)
            self.AddMatchString(compile(b'dualmonitor (yes|no) ?\r\n'), self.__MatchDualMonitor, None)
            self.AddMatchString(compile(b'maxtimeincall (\d+)\r\n'), self._MatchMaxTimeInCall, None)
            self.AddMatchString(compile(b'pip (on|off|camera)\r\n'), self.__MatchPictureInPicture, None)
            self.AddMatchString(compile(b'pip is (on|off|camera)\r\n'), self.__MatchPictureInPicture, None)
            self.AddMatchString(compile(b'pip location get ([0-3])\r\n'), self.__MatchPictureInPictureLocation, None)
            self.AddMatchString(compile(b'pip location ([0-3])\r\n'), self.__MatchPictureInPictureLocation, None)
            self.AddMatchString(compile(b'sleeptime (0|1|3|15|30|60|120|240|480) ?\r\n'), self.__MatchSleepTime, None)
            self.AddMatchString(compile(b'audiotransmitlevel (-?\d+) ?\r\n'), self.__MatchTransmitLevel, None)
            self.AddMatchString(compile(b'mute near (on|off)\r\n'), self.__MatchTransmitMute, None)
            self.AddMatchString(compile(b'volume (\d+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(compile(b'Control event: vcbutton (stop|play|farplay) \r\n'), self.__MatchVisualConcert, None)
            self.AddMatchString(compile(b'vcbutton (stop|play) \r\n'), self.__MatchVisualConcert, None)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        self._NumberOfPhonebookSearch = value

    @property
    def PhonebookSearchOffset(self):
        return self._PhonebookSearchOffset

    @PhonebookSearchOffset.setter
    def PhonebookSearchOffset(self, value):
        self._PhonebookSearchOffset = value

    def __MatchPassword(self, match, qualifier):

        self.SetPassword(None, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def SetAutoAnswer(self, value, qualifier):

        if value in ['Yes', 'No', 'Do Not Disturb']:
            self.__SetHelper('AutoAnswer', 'autoanswer {0}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoAnswer')

    def UpdateAutoAnswer(self, value, qualifier):
        self.__UpdateHelper('AutoAnswer', 'autoanswer get\r', qualifier)

    def __MatchAutoAnswer(self, match, tag):
        value = match.group(1).decode()
        value = 'Do Not Disturb' if value == 'donotdisturb' else value.title()

        self.WriteStatus('AutoAnswer', value, None)

    def UpdateCallState(self, value, qualifier):

        self.__UpdateHelper('CallState', 'callinfo all\r', qualifier)

    def __MatchCallState(self, match, tag):

        res = match.group(0).decode()
        result = findall(self.stat, res)
        call = 1

        for res in result:
            state = res[3].title()
            name = res[1]
            number = res[2]
            self.WriteStatus('CallState', state, {'Call': str(call)})
            self.WriteStatus('CallInfoName', name, {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', number, {'Call': str(call)})
            type_ = 'Video' if 'video' in res[5] else 'Audio'
            self.WriteStatus('CallType', type_, {'Call': str(call)})
            call += 1
        while call <= 3:
            self.WriteStatus('CallState', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})
            self.WriteStatus('CallType', 'Unavailable', {'Call': str(call)})
            call += 1

    def __MatchCallStateInactive(self, match, tag):

        for call in range(1, 4):
            self.WriteStatus('CallState', 'Inactive', {'Call': str(call)})
            self.WriteStatus('CallInfoName', '', {'Call': str(call)})
            self.WriteStatus('CallInfoNumber', '', {'Call': str(call)})
            self.WriteStatus('CallType', 'Unavailable', {'Call': str(call)})

    def SetCameraFarPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            self.__SetHelper('CameraFarPanTilt', 'camera far move {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarPanTilt')

    def SetCameraFarSource(self, value, qualifier):

        if value in ['1', '2', '3', '4', '5']:
            self.__SetHelper('CameraFarSource', 'camera far {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarSource')

    def UpdateCameraFarSource(self, value, qualifier):
        self.__UpdateHelper('CameraFarSource', 'camera far source\r', qualifier)

    def __MatchCameraFarSource(self, match, tag):
        value = match.group(1).decode()
        value = 'Unavailable' if value == '-1' else value

        self.WriteStatus('CameraFarSource', value, None)

    def SetCameraFarTracking(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'To Preset': 'to_presets'
        }

        CameraFarTrackingCmdString = 'camera far tracking {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraFarTracking', CameraFarTrackingCmdString, value, qualifier)

    def UpdateCameraFarTracking(self, value, qualifier):

        CameraFarTrackingCmdString = 'camera far tracking get\r'
        self.__UpdateHelper('CameraFarTracking', CameraFarTrackingCmdString, qualifier)

    def __MatchCameraFarTracking(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off',
            'to_presets': 'To Preset'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CameraFarTracking', value, None)

    def SetCameraFarZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            self.__SetHelper('CameraFarZoom', 'camera far move {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraFarZoom')

    def SetCameraNearPanTilt(self, value, qualifier):

        if value in ['Left', 'Right', 'Up', 'Down', 'Stop']:
            self.__SetHelper('CameraNearPanTilt', 'camera near move {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearPanTilt')

    def SetCameraNearSource(self, value, qualifier):

        if value in ['1', '2', '3', '4']:
            self.__SetHelper('CameraNearSource', 'camera near {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearSource')

    def UpdateCameraNearSource(self, value, qualifier):
        self.__UpdateHelper('CameraNearSource', 'camera near source\r', qualifier)

    def __MatchCameraNearSource(self, match, tag):
        value = match.group(1).decode()

        self.WriteStatus('CameraNearSource', value, None)

    def SetCameraNearTracking(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'To Preset': 'to_presets'
        }

        CameraNearTrackingCmdString = 'camera near tracking {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('CameraNearTracking', CameraNearTrackingCmdString, value, qualifier)

    def UpdateCameraNearTracking(self, value, qualifier):

        CameraNearTrackingCmdString = 'camera near tracking get\r'
        self.__UpdateHelper('CameraNearTracking', CameraNearTrackingCmdString, qualifier)

    def __MatchCameraNearTracking(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off',
            'to_presets': 'To Preset'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('CameraNearTracking', value, None)

    def SetCameraNearZoom(self, value, qualifier):

        if value in ['Zoom+', 'Zoom-', 'Stop']:
            self.__SetHelper('CameraNearZoom', 'camera near move {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraNearZoom')

    def SetCameraPresetFarRecall(self, value, qualifier):

        if 0 <= int(value) <= 15:
            self.__SetHelper('CameraPresetFarRecall', 'preset far go {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFarRecall')

    def SetCameraPresetFarSave(self, value, qualifier):

        if 0 <= int(value) <= 15:
            self.__SetHelper('CameraPresetFarSave', 'preset far set {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetFarSave')

    def SetCameraPresetNearRecall(self, value, qualifier):

        if 0 <= int(value) <= 99:
            self.__SetHelper('CameraPresetNearRecall', 'preset near go {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNearRecall')

    def SetCameraPresetNearSave(self, value, qualifier):

        if 0 <= int(value) <= 99:
            self.__SetHelper('CameraPresetNearSave', 'preset near set {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetCameraPresetNearSave')

    def SetConfigPresentation(self, value, qualifier):

        mon = qualifier['Monitor']
        if value in ['Near', 'Far', 'Content', 'Near Or Far', 'Content Or Near', 'Content Or Far', 'All', 'None'] and mon in ['1', '2']:
            self.__SetHelper('ConfigPresentation', 'configpresentation monitor{0} {1}\r'.format(mon, value.replace(' ', '-').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetConfigPresentation')

    def UpdateConfigPresentation(self, value, qualifier):
        mon = qualifier['Monitor']
        if mon in ['1', '2']:
            self.__UpdateHelper('ConfigPresentation', 'configpresentation monitor{0} get\r'.format(mon), qualifier)
        else:
            self.Discard('Invalid Command for UpdateConfigPresentation')

    def __MatchConfigPresentation(self, match, tag):
        value = match.group(2).decode().title().replace('-', ' ')
        mon = match.group(1).decode()

        self.WriteStatus('ConfigPresentation', value, {'Monitor': mon})

    def SetDTMF(self, value, qualifier):

        if value in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '*', '#']:
            self.__SetHelper('DTMF', 'gendial {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDTMF')

    def SetDualMonitor(self, value, qualifier):

        if value in ['Yes', 'No']:
            self.__SetHelper('DualMonitor', 'dualmonitor {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetDualMonitor')

    def UpdateDualMonitor(self, value, qualifier):
        self.__UpdateHelper('DualMonitor', 'dualmonitor get\r', qualifier)

    def __MatchDualMonitor(self, match, tag):
        value = match.group(1).decode().title()

        self.WriteStatus('DualMonitor', value, None)

    def SetHook(self, value, qualifier):

        SpeedStates = {
            '56': '56',
            '64': '64',
            '2x56': '2x56',
            '112': '112',
            '2x64': '2x64',
            '128': '128',
            '168': '168',
            '192': '192',
            '224': '224',
            '256': '256',
            '280': '280',
            '320': '320',
            '336': '336',
            '384': '384',
            '392': '392',
            '7x64': '7x64',
            '8x56': '8x56',
            '504': '504',
            '512': '512',
            '560': '560',
            '576': '576',
            '616': '616',
            '640': '640',
            '672': '672',
            '704': '704',
            '728': '728',
            '768': '768',
            '784': '784',
            '832': '832',
            '840': '840',
            '16x56': '16x56',
            '14x64': '14x64',
            '952': '952',
            '960': '960',
            '1008': '1008',
            '1024': '1024',
            '1064': '1064',
            '1088': '1088',
            '1120': '1120',
            '1152': '1152',
            '1176': '1176',
            '1216': '1216',
            '1232': '1232',
            '1280': '1280',
            '1288': '1288',
            '24x256': '24x256',
            '21x64': '21x64',
            '1400': '1400',
            '1408': '1408',
            '1456': '1456',
            '1472': '1472',
            '1512': '1512',
            '1536': '1536',
            '1568': '1568',
            '1600': '1600',
            '1624': '1624',
            '1664': '1664',
            '1680': '1680',
            '1728': '1728',
            '1736': '1736',
            '32x56': '32x56',
            '28x64': '28x64',
            '1848': '1848',
            '1856': '1856',
            '1904': '1904',
            '1920': '1920',
            'None': ''
        }

        valueCmd = {
            'Dial Addressbook Name': 'dial addressbook',
            'Dial Manual 56': 'dial manual 56',
            'Dial Manual 64': 'dial manual 64',
            'Dial Phone': 'dial phone',
            'Answer Video': 'answer video\r',
            'Answer Phone': 'answer phone\r',
            'Hangup Video': 'hangup video\r',
            'Hangup Phone': 'hangup phone\r',
            'Hangup All': 'hangup all\r',
            'Flash': 'phone flash\r',
            'Dial Auto Speed': 'dial auto',
            'Dial Manual Speed': 'dial manual'
        }

        speed = SpeedStates[qualifier['Speed']]
        number = qualifier['Number']
        if value == 'Dial Addressbook Name' and number:
            self.__SetHelper('Hook', '{0} \"{1}\"\r'.format(valueCmd[value], number), value, qualifier)
        elif value in ['Dial Manual 56', 'Dial Manual 64', 'Dial Phone'] and number:
            self.__SetHelper('Hook', '{0} \"{1}\"\r'.format(valueCmd[value], number), value, qualifier)
        elif value in ['Dial Auto Speed', 'Dial Manual Speed'] and number:
            self.__SetHelper('Hook', '{0} \"{1}\" \"{2}\"\r'.format(valueCmd[value], speed, number), value, qualifier)
        elif value in valueCmd:
            self.__SetHelper('Hook', valueCmd[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetHook')

    def SetIREmulation(self, value, qualifier):

        if value.lower().replace(' ', '') in ['#', '*', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.',
                                              'down', 'left', 'right', 'select', 'up',
                                              'auto', 'callhangup', 'far', 'graphics', 'near', 'zoom+', 'zoom-',
                                              'help', 'mute', 'snapshot', 'volume+', 'volume-',
                                              'pickedup', 'putdown',
                                              'camera', 'delete', 'directory', 'home', 'keyboard', 'period', 'pip', 'preset',
                                              'info', 'menu', 'slides']:
            self.__SetHelper('IREmulation', 'button {0}\r'.format(value.replace(' ', '').lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetIREmulation')

    def SetMaxTimeInCall(self, value, qualifier):

        if 0 <= value <= 999:
            self.__SetHelper('MaxTimeInCall', 'maxtimeincall set {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetMaxTimeInCall')

    def UpdateMaxTimeInCall(self, value, qualifier):
        self.__UpdateHelper('MaxTimeInCall', 'maxtimeincall get\r', qualifier)

    def _MatchMaxTimeInCall(self, match, tag):
        value = int(match.group(1))
        self.WriteStatus('MaxTimeInCall', value, None)

    def SetPhonebookNavigation(self, value, qualifier):

        if self.MaxLabel != 0 and self.numOfName > 0:
            if value in ['Up', 'Down', 'Page Up', 'Page Down']:
                if 'Page' in value:
                    NumberOfAdvance = self._NumberOfPhonebookSearch
                else:
                    NumberOfAdvance = 1

                if 'Down' in value and self.MaxLabel <= len(self.nameDict):
                    self.MinLabel += NumberOfAdvance
                    self.MaxLabel += NumberOfAdvance
                elif 'Up' in value:
                    self.MinLabel -= NumberOfAdvance
                    self.MaxLabel -= NumberOfAdvance

                if self.MinLabel < 0:
                    self.MinLabel = 0

                if self.MaxLabel < self._NumberOfPhonebookSearch:
                    self.MaxLabel = self._NumberOfPhonebookSearch

                if self.MaxLabel > self.lastindex and self.Advance is True:
                    self.lastindex = self._PhonebookSearchOffset + self.MinLabel
                    self.SetPhonebookUpdateHandler(qualifier)
                else:
                    button = 1
                    for i in range(self.MinLabel, self.MaxLabel):
                        if str(i) in self.nameDict:
                            self.WriteStatus('PhonebookSearchResult', self.nameDict[str(i)]['Name'], {'Button': button})
                            button += 1
                    if button <= self._NumberOfPhonebookSearch:
                        self.WriteStatus('PhonebookSearchResult', '***End of List***', {'Button': button})
                        button += 1
                        for i in range(button, self._NumberOfPhonebookSearch + 1):
                            self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearch(self, value, qualifier):

        self.EndEntry = self._NumberOfPhonebookSearch

    def SetPhonebookSearchSet(self, value, qualifier):

        ButtonConstraints = {
            'Min': 1,
            'Max': self._NumberOfPhonebookSearch
        }
        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max']:
            number = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if number == '***End of List***' or number == '***No Results***' or number == '':
                pass
            else:
                self.SetHook('Dial Addressbook Name',{'Number':number,'Speed':'None'})
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        self.nameDict = {}
        self.MinLabel = 0
        self.MaxLabel = self._NumberOfPhonebookSearch
        self.lastindex = self._PhonebookSearchOffset
        self.SetPhonebookUpdateHandler(qualifier)

    def SetPhonebookUpdateHandler(self, qualifier):

        phoneType = {'Local': 'abk', 'Global': 'gbak'}
        type_ = qualifier['Phonebook Type']
        searchStr = qualifier['Contact']

        if searchStr is None:
            searchStr = ''

        if searchStr:
            cmdStr = '{0} batch search \"{1}\" \"{2}\"\r'.format(phoneType[type_], searchStr, self.lastindex)
        else:
            cmdStr = '{0} range {1} {2}\r'.format(phoneType[type_], self.MinLabel, self.lastindex)
        res = self.SendAndWait(cmdStr, 10)
        if res:
            nameList = findall(self.gdsName, res)
            self.numOfName = len(nameList)
            if self.numOfName >= self._PhonebookSearchOffset:
                self.Advance = True
            else:
                self.Advance = False
            if self.numOfName > 0:
                for i, name in nameList:
                    self.nameDict[i] = {'Name': name}
                button = 1
                for i in range(self.MinLabel, self.MaxLabel):
                    if str(i) in self.nameDict:
                        self.WriteStatus('PhonebookSearchResult', self.nameDict[str(i)]['Name'], {'Button': button})
                        button += 1

                if button <= self._NumberOfPhonebookSearch and self.numOfName > 0:
                    self.WriteStatus('PhonebookSearchResult', '***End of List***', {'Button': button})
                    button += 1
                    for i in range(button, self._NumberOfPhonebookSearch + 1):
                        self.WriteStatus('PhonebookSearchResult', '', {'Button': i})
            else:
                self.__MatchNoContact()
        else:
            self.WriteStatus('PhonebookSearchResult', '***No Results***', {'Button': 1})
            for i in range(2, self._NumberOfPhonebookSearch + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def __MatchNoContact(self):

        self.WriteStatus('PhonebookSearchResult', '***End of List***', {'Button': 1})
        for i in range(2, self._NumberOfPhonebookSearch + 1):
            self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def SetPictureInPicture(self, value, qualifier):

        if value in ['On', 'Off', 'Camera', 'Swap', 'Auto']:
            self.__SetHelper('PictureInPicture', 'pip {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPicture')

    def UpdatePictureInPicture(self, value, qualifier):
        self.__UpdateHelper('PictureInPicture', 'pip get\r', qualifier)

    def __MatchPictureInPicture(self, match, tag):
        value = match.group(1).decode().title()
        if value in ['On', 'Off', 'Camera']:
            self.WriteStatus('PictureInPicture', value, None)

    def SetPictureInPictureLocation(self, value, qualifier):

        valueCmd = {
            'Bottom Right': '0',
            'Top Right': '1',
            'Top Left': '2',
            'Bottom Left': '3',
        }

        if value in valueCmd:
            self.__SetHelper('PictureInPictureLocation', 'pip location {0}\r'.format(valueCmd[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureInPictureLocation')

    def UpdatePictureInPictureLocation(self, value, qualifier):
        self.__UpdateHelper('PictureInPictureLocation', 'pip location get\r', qualifier)

    def __MatchPictureInPictureLocation(self, match, tag):
        valueCmd = {
            b'0': 'Bottom Right',
            b'1': 'Top Right',
            b'2': 'Top Left',
            b'3': 'Bottom Left',
        }

        value = valueCmd[match.group(1)]
        self.WriteStatus('PictureInPictureLocation', value, None)

    def SetReboot(self, value, qualifier):
        self.__SetHelper('Reboot', 'reboot now\r', value, qualifier)

    def SetSleep(self, value, qualifier):
        self.__SetHelper('Sleep', 'sleep\r', value, qualifier)

    def SetSleepTime(self, value, qualifier):
        if value in ["0", "1", "3", "15", "30", "60", "120", "240", "480"]:
            self.__SetHelper('SleepTime', 'sleeptime {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetSleepTime')

    def UpdateSleepTime(self, value, qualifier):
        self.__UpdateHelper('SleepTime', 'sleeptime get\r', qualifier)

    def __MatchSleepTime(self, match, tag):
        value = match.group(1).decode()
        self.WriteStatus('SleepTime', value, None)

    def SetTransmitLevel(self, value, qualifier):
        if -20 <= value <= 30:
            self.__SetHelper('TransmitLevel', 'audiotransmitlevel set {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitLevel')

    def UpdateTransmitLevel(self, value, qualifier):
        self.__UpdateHelper('TransmitLevel', 'audiotransmitlevel get\r', qualifier)

    def __MatchTransmitLevel(self, match, tag):
        value = int(match.group(1))
        self.WriteStatus('TransmitLevel', value, None)

    def SetTransmitMute(self, value, qualifier):
        if value in ['On', 'Off']:
            self.__SetHelper('TransmitMute', 'mute near {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransmitMute')

    def UpdateTransmitMute(self, value, qualifier):
        self.__UpdateHelper('TransmitMute', 'mute near get\r', qualifier)

    def __MatchTransmitMute(self, match, tag):
        value = match.group(1).decode().title()
        self.WriteStatus('TransmitMute', value, None)

    def SetVisualConcert(self, value, qualifier):
        if value in ['Play', 'Stop']:
            self.__SetHelper('VisualConcert', 'vcbutton {0}\r'.format(value.lower()), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVisualConcert')

    def UpdateVisualConcert(self, value, qualifier):
        self.__UpdateHelper('VisualConcert', 'vcbutton register\r', qualifier)
        self.__UpdateHelper('VisualConcert', 'vcbutton get\r', qualifier)

    def __MatchVisualConcert(self, match, tag):

        value = match.group(1).decode()
        value = 'Far Play' if value == 'farplay' else value.title()
        self.WriteStatus('VisualConcert', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 50:
            self.__SetHelper('Volume', 'volume set {0}\r'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', 'volume get\r', qualifier)

    def __MatchVolume(self, match, tag):
        value = int(match.group(1))
        self.WriteStatus('Volume', value, None)

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