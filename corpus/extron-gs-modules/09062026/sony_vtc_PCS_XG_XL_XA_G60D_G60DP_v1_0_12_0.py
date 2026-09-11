from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re
from struct import pack
from re import compile, findall, DOTALL, match, search


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
            'PCS-XG100S': self.model_XG100,
            'PCS-XG100': self.model_XG100,
            'PCS-XG80': self.model_XG80,
            'PCS-XG77': self.model_XG77,
            'PCS-XG55': self.model_XG55G60,
            'PCS-XL55': self.model_XL55,
            'PCS-XA55': self.model_XG55G60,
            'PCS-XA80': self.model_XG80,
            'PCS-G60D': self.model_XG55G60,
            'PCS-G60DP': self.model_XG55G60,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAnswer': {'Status': {}},
            'AutoFocus': {'Status': {}},
            'CallerID': {'Status': {}},
            'CallStatus': {'Status': {}},
            'DialPhonebook': {'Status': {}},
            'FocusFar': {'Status': {}},
            'FocusNear': {'Parameters': ['Speed'], 'Status': {}},
            'Hook': {'Status': {}},
            'InputFar': {'Status': {}},
            'InputNear': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'Layout': {'Status': {}},
            'MicrophoneMute': {'Status': {}},
            'NetworkSet': {'Status': {}},
            'PanTiltFar': {'Status': {}},
            'PanNear': {'Parameters': ['Pan Speed'], 'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookTotalContacts': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PlayMode': {'Parameters': ['Mode'], 'Status': {}},
            'Power': {'Status': {}},
            'Presentation': {'Status': {}},
            'PresetRecallFar': {'Status': {}},
            'PresetRecallNear': {'Status': {}},
            'PresetSaveFar': {'Status': {}},
            'PresetSaveNear': {'Status': {}},
            'Record': {'Status': {}},
            'Streaming': {'Status': {}},
            'TiltNear': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Volume': {'Status': {}},
            'ZoomFar': {'Status': {}},
            'ZoomNear': {'Parameters': ['Speed'], 'Status': {}},
        }

        self.PageUp = 0
        self.PageDown = 0
        self.MaxEntries = 0
        self.Authenticated = 'None'

        self.Phonebook = compile('([0-9]{1,3}):(.*)\r\r\n')
        self.Phonebooklist = []
        self.PhoneBookTempList = []

        if 'Serial' not in self.ConnectionType:
            self.deviceUsername = None
            self.devicePassword = None
        else:
            self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(ring manual\r\r\n([\s\S]+)\r\r\n\r\nCNTR>|connect complete|connect status\x0D\x0D\x0A2|connect status\x0D\x0D\x0A3|disconnect|dial cancel)'), self.__MatchCallStatus, None)
            self.AddMatchString(compile(b'status power (power-on|stand-by)'), self.__MatchPower, None)
            self.AddMatchString(compile(b'status macstatus\r\r\n(CAMERA|HDMI|DVI-I1|DVI-I2|RGB|YPbPr|S-VIDEO)\r'), self.__MatchInputNear, None)
            self.AddMatchString(compile(b'(not init|busy|syntax error|socket error|execute error|buffer full|not supported|not power on|on network test|not communication|on update|not connect|timeout|preset type error|preset no memory|error)\r'),
                                self.__MatchError, None)
            self.AddMatchString(compile(b'audio mic-(on|off)\r'), self.__MatchMicrophoneMute, None)
            self.AddMatchString(compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)

        self.AddMatchString(compile(b'\xFF\xFD\x18'), self.__MatchTelnetInitiate, None)
        self.PhonebookPattern = compile(b'list index(.*)CNTR>')

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= int(value) <= 10:
            self._NumberOfPhonebookSearch = int(value)
        else:
            self.Error(['NumberOfPhonebookSearch should be a value between 1 to 10.'])

    def __MatchLogin(self, match, qualifier):
        if self.deviceUsername:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
            self.Authenticated = 'User'
        else:
            self.MissingCredentialsLog('Password')

    def __MatchTelnetInitiate(self, match, qualifier):
        self.SetMatchTelnetInitiate(None, None)

    def SetMatchTelnetInitiate(self, value, qualifier):
        self.Send('\xFF\xFB\x18\xFF\xFB\x1F\xFF\xFC\x20\xFF\xFC\x23\xFF\xFB\x27\xFF\xFA\x1F')
        self.Send('\x00\x50\x00\x19\xFF\xF0\xFF\xFA\x27\x00\xFF\xF0\xFF\xFA\x18\x00\x41\x4E')
        self.Send('\x53\x49\xFF\xF0\xFF\xFD\x03\xFF\xFB\x01\xFF\xFE\x05\xFF\xFC\x21')

    def SetAutoAnswer(self, value, qualifier):

        States = {
            'On': 'setup save answer autoincome-on\r\n',
            'Off': 'setup save answer autoincome-off\r\n'
        }

        CmdString = States[value]
        self.__SetHelper('AutoAnswer', CmdString, value, qualifier)

    def SetAutoFocus(self, value, qualifier):

        CmdString = 'camera focus-auto\r\n'
        self.__SetHelper('AutoFocus', CmdString, value, qualifier)

    def __MatchCallStatus(self, match, tag):

        CallStatusState = {
            'connect complete': 'Connected',
            'connect status\x0D\x0D\x0A3': 'Connecting',
            'disconnect': 'Disconnected',
            'dial cancel': 'Dial Cancelled',
            'connect status\x0D\x0D\x0A2': 'Outgoing',

        }
        if 'ring manual' in match.group(1).decode():
            self.WriteStatus('CallStatus', 'Incoming', None)
            ID = match.group(2).decode()
            self.WriteStatus('CallerID', ID, None)
        else:
            value = CallStatusState[match.group(1).decode()]
            self.WriteStatus('CallStatus', value, None)
            self.WriteStatus('CallerID', '', None)

    def SetDialPhonebook(self, value, qualifier):

        number = value
        if number:
            DialPhonebookCmdString = 'dial list {0}\r'.format(number)
            self.__SetHelper('DialPhonebook', DialPhonebookCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDialPhonebook')

    def SetFocusFar(self, value, qualifier):

        States = {
            'Far': 'far',
            'Near': 'near',
            'Stop': 'stop'
        }

        CmdString = 'far camera focus-{0}\r\n'.format(States[value])
        self.__SetHelper('FocusFar', CmdString, value, qualifier)

    def SetFocusNear(self, value, qualifier):

        States = {
            'Far': 'far',
            'Near': 'near',
            'Stop': 'stop'
        }

        Speed = int(qualifier['Speed'])
        if 0 < Speed <= 17:
            if value != 'Stop':
                CmdString = 'camera focus-{0} /{1}/\r\n'.format(States[value], Speed)
            elif value == 'Stop':
                CmdString = 'camera focus-{0}\r\n'.format(States[value])

            self.__SetHelper('FocusNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocusNear')

    def SetHook(self, value, qualifier):

        States = {
            'Hang Up': 'disconnect\r\n',
            'Answer Call': 'answer accept\r\n',
            'Reject Call': 'answer reject\r\n',
        }

        if value == 'Dial':
            DialString = qualifier['Number']
            if DialString:
                CmdString = 'dial /{0}/\r\n'.format(DialString)
            else:
                self.Discard('Invalid Command for SetHook')
        else:
            CmdString = '{0}'.format(States[value])

        self.__SetHelper('Hook', CmdString, value, qualifier)

    def SetInputFar(self, value, qualifier):

        CmdString = 'far video {0}\r\n'.format(self.InputStates[value])
        self.__SetHelper('InputFar', CmdString, value, qualifier)

    def SetInputNear(self, value, qualifier):

        CmdString = 'video {0}\r\n'.format(self.InputStates[value])
        self.__SetHelper('InputNear', CmdString, value, qualifier)

    def UpdateInputNear(self, value, qualifier):

        CmdString = 'status macstatus\r\n'
        self.__UpdateHelper('InputNear', CmdString, value, qualifier)

    def __MatchInputNear(self, match, tag):

        value = self.InputStateFeedBack[match.group(1).decode()]
        self.WriteStatus('InputNear', value, None)

    def SetIRRemoteEmulation(self, value, qualifier):

        States = {
            '1': '0',
            '2': '1',
            '3': '2',
            '4': '3',
            '5': '4',
            '6': '5',
            '7': '6',
            '8': '7',
            '9': '8',
            '0': '9',
            '*': '10',
            '#': '11',
            'Mic': '16',
            'Connect': '17',
            'Volume Down': '19',
            'Volume Up': '18',
            'Power': '21',
            'Camera': '23',
            'Zoom In': '31',
            'Zoom Out': '30',
            'Disconnect': '45',
            'Back': '52',
            'Tools': '58',
            'Video': '65',
            'F1': '95',
            'F2': '96',
            'F3': '97',
            'F4': '98',
            'Return': '102',
            'Layout': '104',
            'Presentation': '107',
            'Enter': '110',
            'Up': '111',
            'Down': '119',
            'Left': '123',
            'Right': '115',
            'Stop': '144',
            '11': '192',
            '12': '193',
            '13': '194',
            '14': '195',
            '15': '196',
            '16': '197',
        }

        CmdString = 'remcom {0}\r\n'.format(States[value])
        self.__SetHelper('IRRemoteEmulation', CmdString, value, qualifier)

    def SetLayout(self, value, qualifier):

        States = {
            'Full': 'full',
            'Side By Side': 'sidebyside',
            'Picture And Picture': 'pandp',
            'PIP - Upper Right': 'pinp-upright',
            'PIP - Upper Left': 'pinp-upleft',
            'PIP - Lower Right': 'pinp-downright',
            'PIP - Lower Left': 'pinp-downleft',
            'PIP - Bottom Most Left': 'pinp-downrightside'
        }

        CmdString = 'layout {0}\r\n'.format(States[value])
        self.__SetHelper('Layout', CmdString, value, qualifier)

    def SetMicrophoneMute(self, value, qualifier):

        States = {
            'On': 'audio mic-on\r\n',
            'Off': 'audio mic-off\r\n'
        }

        CmdString = States[value]
        self.__SetHelper('MicrophoneMute', CmdString, value, qualifier)

    def __MatchMicrophoneMute(self, match, tag):

        stateValues = {
            'on': 'On',
            'off': 'Off',
        }

        value = stateValues[match.group(1).decode()]
        self.WriteStatus('MicrophoneMute', value, None)

    def SetNetworkSet(self, value, qualifier):

        ip_address = qualifier['IP Address']
        subnet = qualifier['Subnet']
        gateway = qualifier['Gateway']
        dns_p = qualifier['DNS Primary']
        dns_a = qualifier['DNS Alternate']

        NetworkSetCmdString = 'setup save lan //{0}/{1}/{2}/{3}/{4}/\r\n'.format(ip_address, subnet, gateway, dns_p, dns_a)
        self.__SetHelper('NetworkSet', NetworkSetCmdString, value, qualifier)

    def SetPanTiltFar(self, value, qualifier):

        States = {
            'Up': 'up',
            'Down': 'down',
            'Left': 'left',
            'Right': 'right',
            'Stop': 'pantilt-stop'
        }

        CmdString = 'far camera {0}\r\n'.format(States[value])
        self.__SetHelper('PanTiltFar', CmdString, value, qualifier)

    def SetPanNear(self, value, qualifier):

        States = {
            'Left': 'left',
            'Right': 'right',
            'Stop': 'stop'
        }

        PanSpeed = int(qualifier['Pan Speed'])
        if 0 < PanSpeed <= 18:
            if value != 'Stop':
                CmdString = 'camera {0} /{1}/\r\n'.format(States[value], PanSpeed)
            elif value == 'Stop':
                CmdString = 'camera pantilt-{0}\r\n'.format(States[value])
            self.__SetHelper('PanNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanNear')

    def SetPhonebookNavigation(self, value, qualifier):

        if value in ['Page Up', 'Page Down']:

            if 'Page Up' in value:
                self.PageUp = self.PageUp - self._NumberOfPhonebookSearch
                self.PageDown = self.PageDown - self._NumberOfPhonebookSearch
            elif 'Page Down' in value:
                if self.PageDown <= self.MaxEntries:
                    self.PageUp = self.PageUp + self._NumberOfPhonebookSearch
                    self.PageDown = self.PageDown + self._NumberOfPhonebookSearch

            if self.PageUp < 0:
                self.PageUp = 0

            if self.PageDown < self._NumberOfPhonebookSearch:
                self.PageDown = self._NumberOfPhonebookSearch

            self.SetPhonebookUpdateHandler(value, qualifier)
        else:
            self.Discard('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookUpdateHandler(self, value, qualifier):

        i = 1
        for name in self.Phonebooklist[self.PageUp:self.PageDown]:
            if type(name) is tuple:
                name = name[1]

            self.WriteStatus('PhonebookSearchResult', name, {'Button': i})
            i += 1

        if self.PageDown > self.MaxEntries:
            emptyEntries = self.PageDown - self.MaxEntries
            clearEntries = self._NumberOfPhonebookSearch - emptyEntries
            emptyEntries = emptyEntries + 1

            if clearEntries < 0:
                clearEntries = 0
            if emptyEntries > self._NumberOfPhonebookSearch:
                emptyEntries = self._NumberOfPhonebookSearch

            for i in range(clearEntries + 1, emptyEntries + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1})

    def SetPhonebookSearch(self, value, qualifier):

        PhoneBookSearchList = []

        for i in range(0, len(self.PhoneBookTempList)):
            if isinstance(self.PhoneBookTempList[i], tuple):
                name = self.PhoneBookTempList[i][1]
            else:
                name = self.PhoneBookTempList[i]

            if value.casefold() in name.casefold():
                PhoneBookSearchList.append(name)

        self.MaxEntries = len(PhoneBookSearchList)

        self.PageUp = 0
        self.PageDown = self._NumberOfPhonebookSearch

        PhoneBookSearchList.append('*** End of List ***')
        self.Phonebooklist = PhoneBookSearchList

        i = 1
        for name in PhoneBookSearchList[self.PageUp:self.PageDown]:
            if type(name) is tuple:
                name = name[1]

            self.WriteStatus('PhonebookSearchResult', name, {'Button': i})
            i += 1

        if self.PageDown > self.MaxEntries:
            emptyEntries = self.PageDown - self.MaxEntries
            clearEntries = self._NumberOfPhonebookSearch - emptyEntries
            emptyEntries = emptyEntries + 1

            if clearEntries < 0:
                clearEntries = 0
            if emptyEntries > self._NumberOfPhonebookSearch:
                emptyEntries = self._NumberOfPhonebookSearch

            for i in range(clearEntries + 1, emptyEntries + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i + 1})

    def SetPhonebookSearchSet(self, value, qualifier):

        ButtonConstraints = {
            'Min': 1,
            'Max': self._NumberOfPhonebookSearch
        }

        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max']:
            entry = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if entry != '':
                for i in range(0, len(self.PhoneBookTempList)):
                    if entry == '*** End of List ***':
                        break
                    else:
                        if entry in self.PhoneBookTempList[i][1]:
                            setValue = self.PhoneBookTempList[i][0]
                            DialCmdString = 'dial list {0}\r'.format(setValue)
                            self.__SetHelper('DialPhonebook', DialCmdString, value, qualifier)
                            break
            else:
                self.Discard('Invalid Command for SetPhonebookSearchSet')
        else:
            self.Discard('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        PhonebookUpdateCmdString = 'list load index\r'
        res = self.__SetHelper('PhonebookUpdate', PhonebookUpdateCmdString, value, qualifier)
        if res:
            self.Phonebooklist = findall(self.Phonebook, res.decode())
            self.MaxEntries = len(self.Phonebooklist)
            self.Phonebooklist.append((str(self.MaxEntries + 1), '*** End of List ***'))
            self.PhoneBookTempList = self.Phonebooklist
            self.PageUp = 0
            self.PageDown = self._NumberOfPhonebookSearch
            self.WriteStatus('PhonebookTotalContacts', self.MaxEntries, None)
            i = 1
            for name in self.Phonebooklist[0:self._NumberOfPhonebookSearch]:
                self.WriteStatus('PhonebookSearchResult', name[1], {'Button': i})
                i = i + 1

    def SetPlayMode(self, value, qualifier):

        ModeStates = {
            'Record': 'record ',
            'Stream': 'stream '
        }

        ValueStateValues = {
            'Start': 'start\r\n',
            'Stop': 'stop\r\n'
        }

        mode = qualifier['Mode']

        PlayModeCmdString = ModeStates[mode] + ValueStateValues[value]
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        State = {
            'On': 'power-on',
            'Off': 'stand-by',
        }
        CmdString = '{0}\r\n'.format(State[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        CmdString = 'status power\r\n'
        self.__UpdateHelper('Power', CmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        State = {
            'power-on': 'On',
            'stand-by': 'Off'
        }

        value = State[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresentation(self, value, qualifier):

        States = {
            'Start': 'rgb start\r\n',
            'Stop': 'rgb stop\r\n'
        }

        CmdString = '{0}'.format(States[value])
        self.__SetHelper('Presentation', CmdString, value, qualifier)

    def SetPresetRecallFar(self, value, qualifier):

        if 1 <= int(value) <= 6:
            CmdString = 'far camera move /{0}/\r\n'.format(value)
            self.__SetHelper('PresetRecallFar', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallFar')

    def SetPresetRecallNear(self, value, qualifier):

        if 1 <= int(value) <= 100:
            CmdString = 'camera move /{0}/\r\n'.format(value)
            self.__SetHelper('PresetRecallNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecallNear')

    def SetPresetSaveFar(self, value, qualifier):

        if 1 <= int(value) <= 6:
            CmdString = 'far camera save /{0}/\r\n'.format(value)
            self.__SetHelper('PresetSaveFar', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSaveFar')

    def SetPresetSaveNear(self, value, qualifier):

        if 1 <= int(value) <= 100:
            CmdString = 'camera save /{0}/\r\n'.format(value)
            self.__SetHelper('PresetSaveNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSaveNear')

    def SetRecord(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'recording-on',
            'Disable': 'recording-off'
        }

        RecordCmdString = 'setup save admin {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Record', RecordCmdString, value, qualifier)

    def SetStreaming(self, value, qualifier):

        ValueStateValues = {
            'Enable': 'streaming-on',
            'Disable': 'streaming-off'
        }

        StreamingCmdString = 'setup save admin {0}\r\n'.format(ValueStateValues[value])
        self.__SetHelper('Streaming', StreamingCmdString, value, qualifier)

    def SetTiltNear(self, value, qualifier):

        States = {
            'Up': 'up',
            'Down': 'down',
            'Stop': 'stop'
        }

        Speed = int(qualifier['Tilt Speed'])
        if 0 < Speed <= 14:
            if value != 'Stop':
                CmdString = 'camera {0} /{1}/\r\n'.format(States[value], Speed)
            elif value == 'Stop':
                CmdString = 'camera pantilt-{0}\r\n'.format(States[value])
            self.__SetHelper('PanNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTiltNear')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 23:
            CmdString = 'audio volume-{0}\r\n'.format(value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def SetZoomFar(self, value, qualifier):

        States = {
            'In': 'tele',
            'Out': 'wide',
            'Stop': 'stop',
        }

        CmdString = 'far camera zoom-{0}\r\n'.format(States[value])
        self.__SetHelper('ZoomFar', CmdString, value, qualifier)

    def SetZoomNear(self, value, qualifier):

        States = {
            'In': 'tele',
            'Out': 'wide',
            'Stop': 'stop'
        }

        Speed = int(qualifier['Speed'])

        if 0 < Speed <= 17:
            if value == 'In' or value == 'Out':
                CmdString = 'camera zoom-{0} /{1}/\r\n'.format(States[value], Speed)
            elif value == 'Stop':
                CmdString = 'camera zoom-{0}\r\n'.format(States[value])

            self.__SetHelper('ZoomNear', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoomNear')

    def __MatchError(self, match, tag):

        Errors = {
            'syntax error': 'Syntax Error',
            'status error': 'Status Error',
            'socket error': 'Socket Error',
            'not init': 'Not Initialized',
            'busy': 'Under Execution',
            'execute error': 'Execution Error',
            'buffer full': 'Buffer full',
            'not supported': 'Not Supported',
            'not power on': 'Power error',
            'on network test': 'During network measurement',
            'not communication': 'Not communicated (far control)',
            'on update': 'During Updating',
            'not connect': 'No Camera Connected',
            'timeout': 'Time out',
            'preset type error': 'Preset Type Error',
            'preset no memory': 'No preset setting registered',
            'error': 'Error Type: Other',
        }

        self.counter = 0
        value = match.group(1).decode()
        self.Error([Errors[value]])

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if command == 'PhonebookUpdate':
            res = self.SendAndWait(commandstring, 5)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                return res
        else:
            self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Authenticated in ['User', 'Not Needed']:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)
        else:
            self.Discard('Unauthenticated: Inappropriate Command ' + command)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def model_XG100(self):

        self.model = 'XG100'
        self.InputStates = {
            'Main Camera': 'camera',
            'HDMI': 'hdmi',
            'DVI 1': 'dvi-i1',
            'DVI 2': 'dvi-i2',
        }

        self.InputStateFeedBack = {
            'CAMERA': 'Main Camera',
            'HDMI': 'HDMI',
            'DVI-I1': 'DVI 1',
            'DVI-I2': 'DVI 2',
        }

    def model_XG80(self):

        self.model = 'other'
        self.InputStates = {
            'Main Camera': 'camera',
            'RGB': 'rgb',
            'YPbPr': 'ypbpr',
            'S-Video': 's-video',
        }

        self.InputStateFeedBack = {
            'CAMERA': 'Main Camera',
            'RGB': 'RGB',
            'YPbPr': 'YPbPr',
            'S-VIDEO': 'S-Video',
        }

    def model_XG77(self):

        self.model = 'other'
        self.InputStates = {
            'Main Camera': 'camera',
            'DVI 1': 'dvi-i1',
            'DVI 2': 'dvi-i2',
        }

        self.InputStateFeedBack = {
            'CAMERA': 'Main Camera',
            'DVI-I1': 'DVI 1',
            'DVI-I2': 'DVI 2',
        }

    def model_XG55G60(self):

        self.model = 'other'
        self.InputStates = {
            'Main Camera': 'camera',
            'RGB': 'rgb',
            'YPbPr': 'ypbpr',
        }

        self.InputStateFeedBack = {
            'CAMERA': 'Main Camera',
            'RGB': 'RGB',
            'YPbPr': 'YPbPr',
        }

    def model_XL55(self):

        self.model = 'other'
        self.InputStates = {
            'Main Camera': 'camera',
            'RGB': 'rgb',
        }

        self.InputStateFeedBack = {
            'CAMERA': 'Main Camera',
            'RGB': 'RGB',
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
