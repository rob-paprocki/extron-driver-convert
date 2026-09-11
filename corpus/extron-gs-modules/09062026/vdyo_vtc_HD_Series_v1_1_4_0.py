from extronlib.interface import SerialInterface, EthernetClientInterface
import re
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
        self.deviceUsername = 'vrxci'
        self.devicePassword = 'vrxci'
        self._NumberOfPhonebookSearch = 5
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CallStatus': {'Status': {}},
            'CameraMute': {'Status': {}},
            'Hook': {'Status': {}},
            'IRRemoteEmulation': {'Status': {}},
            'MicLevel': {'Status': {}},
            'MicMute': {'Status': {}},
            'Pan': {'Status': {}},
            'PhonebookNavigation': {'Status': {}},
            'PhonebookSearch': {'Status': {}},
            'PhonebookSearchResult': {'Parameters': ['Button'], 'Status': {}},
            'PhonebookSearchSet': {'Status': {}},
            'PhonebookUpdate': {'Status': {}},
            'PIN': {'Status': {}},
            'RecordStatus': {'Status': {}},
            'ShareStatus': {'Status': {}},
            'Shutdown': {'Status': {}},
            'SpeakerLevel': {'Status': {}},
            'Tilt': {'Status': {}},
            'Zoom': {'Status': {}}
        }

        self.PhonebookOffset = 0
        self.Advance = True

        

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(Status|set) Call.State (Idle|Ringing|Calling|Joining|Joined|Leaving)'), self.__MatchCallStatus, None)
            self.AddMatchString(re.compile(b'(Status|set) Camera.1.Mute.Local (yes|no|Yes|No)'), self.__MatchCameraMute, None)
            self.AddMatchString(re.compile(b'(Status|set) Microphone.1.Level ([0-9]{1,5})\n'), self.__MatchMicLevel, None)
            self.AddMatchString(re.compile(b'(Status|set) Microphone.1.Mute.Local (yes|no|Yes|No)'), self.__MatchMicMute, None)
            self.AddMatchString(re.compile(b'(Address .*?)?OK 124\n', re.DOTALL), self.__MatchPhonebook, None)
            self.AddMatchString(re.compile(b'(Status|set) Call.Recording (yes|no|Yes|No)'), self.__MatchRecordStatus, None)
            self.AddMatchString(re.compile(b'(Status|set) Share.1.Mute.Local (yes|no|Yes|No)'), self.__MatchShareStatus, None)
            self.AddMatchString(re.compile(b'(Status|set) Speaker.1.Level ([0-9]{1,5})\n'), self.__MatchSpeakerLevel, None)
            self.AddMatchString(re.compile(b'(VCXCI_ERROR)(_BADREQUEST|_NOT_INITIALIZED|_REQUESTFAILED|_UNAUTHORIZED|_SENDING_REQUEST|_NOT_IMPLEMENTED|_CAPACITY|_INVALID_MESSAGE|_NOT_FOUND|_NOT_UNIQUE|_RESPONSE_TIMEOUT|_UNKNOWNSTATUS|_INVALID_PARAMETER){0,1}\n'), self.__MatchError, None)
            self.AddressResponsePattern = re.compile('Address \d+/\d+ (.+?|".+?([ ](.)*)*") (Room|User|Legacy) (.+?|".+?([ ]([.])*)*?") ([0-9-]+)', re.UNICODE)

    @property
    def NumberOfPhonebookSearch(self):
        return self._NumberOfPhonebookSearch

    @NumberOfPhonebookSearch.setter
    def NumberOfPhonebookSearch(self, value):
        if 1 <= value <= 10:
                self._NumberOfPhonebookSearch = value

    def UpdateCallStatus(self, value, qualifier):

        self.__UpdateHelper('CallStatus', 'Request Status Call.State\n', value, qualifier)

    def __MatchCallStatus(self, match, tag):

        ValueStateValues = {
            'Ringing': 'Ringing',
            'Calling': 'Calling',
            'Joining': 'Joining',
            'Joined': 'Joined',
            'Idle': 'Idle',
            'Leaving': 'Leaving'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('CallStatus', value, None)

    def SetCameraMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'yes',
            'Off': 'no'
        }

        CameraMuteCmdString = 'Request Set Camera.1.Mute.Local {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('CameraMute', CameraMuteCmdString, value, qualifier)

    def UpdateCameraMute(self, value, qualifier):

        CameraMuteCmdString = 'Request Status Camera.1.Mute.Local\n'
        self.__UpdateHelper('CameraMute', CameraMuteCmdString, value, qualifier)

    def __MatchCameraMute(self, match, tag):

        ValueStateValues = {
            'yes': 'On',
            'no': 'Off'
        }

        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('CameraMute', value, None)

    def SetHook(self, value, qualifier):

        ValueStateValues = {
            'Call Direct': 'Call',
            'Join Room': 'Join',
            'Disconnect': 'Disconnect',
            'Answer': 'Answer Accept',
            'Reject': 'Answer Reject'
        }
        HookCmdString = ''
        if value in ['Disconnect', 'Answer', 'Reject']:
            HookCmdString = 'Request {0}\n'.format(ValueStateValues[value])
        else:
            HookName = qualifier['Name']
            if HookName:
                PIN = qualifier['PIN']
                if PIN:
                    HookCmdString = 'Request {0} Name "{1}" {2}\n'.format(ValueStateValues[value], HookName, PIN)
                else:
                    HookCmdString = 'Request {0} Name "{1}"\n'.format(ValueStateValues[value], HookName)
        self.__SetHelper('Hook', HookCmdString.encode(), value, qualifier)

    def SetIRRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            'Manage': 77,
            'Self-View': 86,
            'Privacy': 80,
            'Toggle': 84,
            'Connect': 113,
            'Disconnect': 8,
            'Mute': 35,
            'Volume Up': 107,
            'Volume Down': 189,
            'Status': 90,
            'Share': 72,
            'Left': 37,
            'Up': 38,
            'Right': 39,
            'Down': 40,
            'Zoom In': 33,
            'Zoom Out': 34,
            'A': 118,
            'B': 119,
            'C': 120,
            'D': 122,
            '0': 48,
            '1': 49,
            '2': 50,
            '3': 51,
            '4': 52,
            '5': 53,
            '6': 54,
            '7': 55,
            '8': 56,
            '9': 57,
            '#': 111,
            '*': 106,
            'Del': 8,
            'Ok': 13,
            'Back': 27,
            'Home': 36,
            'Settings': 83,
        }

        IRRemoteEmulationCmdString = 'Request 1234 KeyPress Remote {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('IRRemoteEmulation', IRRemoteEmulationCmdString, value, qualifier)

    def SetMicLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MicLevelCmdString = 'Request Set Microphone.1.Level {0}\n'.format(int(65535 / 100 * value))
            self.__SetHelper('MicLevel', MicLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMicLevel')

    def UpdateMicLevel(self, value, qualifier):

        MicLevelCmdString = 'Request Status Microphone.1.Level\n'
        self.__UpdateHelper('MicLevel', MicLevelCmdString, value, qualifier)

    def __MatchMicLevel(self, match, tag):

        value = round(int(match.group(2).decode()) * 100 / 65535)
        self.WriteStatus('MicLevel', value, None)

    def SetMicMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'yes',
            'Off': 'no'
        }

        MicMuteCmdString = 'Request Set Microphone.1.Mute.Local {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('MicMute', MicMuteCmdString, value, qualifier)

    def UpdateMicMute(self, value, qualifier):

        CmdString = 'Request Status Microphone.1.Mute.Local\n'
        self.__UpdateHelper('MicMute', CmdString, value, qualifier)

    def __MatchMicMute(self, match, tag):

        ValueStateValues = {
            'yes': 'On',
            'no': 'Off'
        }

        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('MicMute', value, None)

    def SetPan(self, value, qualifier):

        ValueStateValues = {
            'Left': 'Left',
            'Right': 'Right'
        }

        PanCmdString = 'Request Set Camera.1.Pan {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('Pan', PanCmdString, value, qualifier)

    def SetPhonebookNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': -1,
            'Down': 1,
            'Page Up': -1 * self._NumberOfPhonebookSearch,
            'Page Down': self._NumberOfPhonebookSearch
        }
        if self.Advance or value in ['Up', 'Page Up']:
            try:
                self.PhonebookOffset += ValueStateValues[value]
                if self.PhonebookOffset < 0:
                    self.PhonebookOffset = 0
                self.SetPhonebookUpdate(value, qualifier)
            except:
                print('Invalid Command for SetPhonebookNavigation')

    def SetPhonebookSearchSet(self, value, qualifier):

        ButtonConstraints = {
            'Min': 1,
            'Max': 10
        }

        if ButtonConstraints['Min'] <= value <= ButtonConstraints['Max']:
            hookName = self.ReadStatus('PhonebookSearchResult', {'Button': value})
            if hookName:
                hookName = hookName.split(' :')[0]
                self.Send('Request Call Name "{}"\n'.format(HookName))
        else:
            print('Invalid Command for SetPhonebookSearchSet')

    def SetPhonebookUpdate(self, value, qualifier):

        AddressPattern = value
        if not AddressPattern:
            AddressPattern = ''
        PhonebookUpdateCmdString = 'Request 124 Addresses "{0}" Any Ascending {1} {2}\n'.format(
            AddressPattern,
            self.PhonebookOffset,
            self._NumberOfPhonebookSearch
        )
        self.__UpdateHelper('PhonebookUpdate', PhonebookUpdateCmdString, value, qualifier)

    def __MatchPhonebook(self, match, tag):

        if match.group(1):
            NameList = re.findall(self.AddressResponsePattern, match.group(1).decode())
            self.Advance = True
            button = 1
            for entityID, _, _, type, name, _, _, ext in NameList:
                DirString = '{0} :{1}'.format(name.replace('"', ''), ext)
                self.WriteStatus('PhonebookSearchResult', DirString, {'Button': button})
                button += 1
        else:
            DirString = '*** End Of List ***'
            button = 1
            self.WriteStatus('PhonebookSearchResult', DirString, {'Button': button})

        if button <= self._NumberOfPhonebookSearch:
            DirString = '*** End Of List ***'
            self.WriteStatus('PhonebookSearchResult', DirString, {'Button': button})
            self.Advance = False
            for i in range(button + 1, self._NumberOfPhonebookSearch + 1):
                self.WriteStatus('PhonebookSearchResult', '', {'Button': i})

    def UpdateRecordStatus(self, value, qualifier):

        RecordStatusCmdString = 'Request Status Call.Recording\n'
        self.__UpdateHelper('RecordStatus', RecordStatusCmdString, value, qualifier)

    def __MatchRecordStatus(self, match, tag):

        ValueStateValues = {
            'yes': 'On',
            'no': 'Off'
        }

        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('RecordStatus', value, None)

    def SetShareStatus(self, value, qualifier):

        ValueStateValues = {
            'Active': 'no',
            'Inactive': 'yes'
        }

        ShareStatusCmdString = 'Request Set Share.1.Mute.Local {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('ShareStatus', ShareStatusCmdString, value, qualifier)

    def UpdateShareStatus(self, value, qualifier):

        ShareStatusCmdString = 'Request Status Share.1.Mute.Local\n'
        self.__UpdateHelper('ShareStatus', ShareStatusCmdString, value, qualifier)

    def __MatchShareStatus(self, match, tag):

        ValueStateValues = {
            'no': 'Active',
            'yes': 'Inactive'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ShareStatus', value, None)

    def SetShutdown(self, value, qualifier):

        self.__SetHelper('Shutdown', 'Request 1234 Shutdown\n', value, qualifier)

    def SetSpeakerLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            SpeakerLevelCmdString = 'Request Set Speaker.1.Level {0}\n'.format(int(65535 / 100 * value))
            self.__SetHelper('SpeakerLevel', SpeakerLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSpeakerLevel')

    def UpdateSpeakerLevel(self, value, qualifier):

        SpeakerLevelCmdString = 'Request Status Speaker.1.Level\n'
        self.__UpdateHelper('SpeakerLevel', SpeakerLevelCmdString, value, qualifier)

    def __MatchSpeakerLevel(self, match, tag):

        value = round(int(match.group(2).decode()) * 100 / 65535)
        self.WriteStatus('SpeakerLevel', value, None)

    def SetTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': 'Up',
            'Down': 'Down'
        }

        TiltCmdString = 'Request Set Camera.1.Tilt {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('Tilt', TiltCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': 'In',
            'Out': 'Out'
        }

        ZoomCmdString = 'Request Set Camera.1.Zoom {0}\n'.format(ValueStateValues[value])
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        Errors = {
            '_BADREQUEST': 'An error occurred when parsing the request',
            '_NOT_INITIALIZED': 'Initialization has not been successfully completed and must be called before using any other Request.',
            '_REQUESTFAILED': 'Backend could not process the request',
            '_UNAUTHORIZED' : 'Authorization failed, most likely due to the username and password not matching those expected by the \
                                    VidyoRoom or another Con-roller with the name "Extron Controller" is already registered with the Vidyo-Room.',
            '_SENDING_REQUEST': 'An error occurred when sending the request.',
            '_NOT_IMPLEMENTED': 'Feature being used is yet to be implemented.',
            '_CAPACITY': 'The request to join was rejected because the system\'s capacity was exceeded.',
            '_INVALID_MESSAGE': 'The Register request is not for either status or event.',
            '_NOT_FOUND': 'The VidyoRoom could not find the entity being addressed in a Join or a Call request.',
            '_NOT_UNIQUE': 'The VidyoRoom found more than one entity matching the string identifying the addressable entity.',
            '_RESPONSE_TIMEOUT': 'There was a timeout in receiving a response for this event.',
            '_UNKNOWNSTATUS': 'The Register request asked to receive status updates for an un-known location within the hierarchical status data structure.',
            '_INVALID_PARAMETER': 'The Register request asked to received event or status of an un-known type.',
        }

        try:
            print(Errors[match.group(2).decode()])
        except:
            self.Error(['A general error occurred without the ability of the VidyoRoom to di-agnose the problem.'])

    def SetInitializeString(self, value, qualifier):

        self.Send('Request 123 Initialize {0} {1} "Extron Controller"\n'.format(self.deviceUsername, self.devicePassword))
        self.WriteStatus('CallStatus', 'Idle', None)
        
    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetInitializeString(None, None)

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
