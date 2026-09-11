from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioInputSelect': {'Status': {}},
            'CardCondition': {'Status': {}},
            'Keypad': {'Status': {}},
            'OperationStatus': {'Status': {}},
            'PlayMode': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'RecordingVolume': {'Status': {}},
            'TrackNumber': {'Status': {}},
            'TrackTime': {'Status': {}},
            'Transport': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'@0IN(UN|BA|DI)\r'), self.__MatchAudioInputSelect, None)
            self.AddMatchString(compile(b'@0(CD|ST)(NC|RE|CI|CE|99|FL|BC|ER|WR|EW)\r'), self.__MatchCardCondition, None)
            self.AddMatchString(compile(b'@0ST(RU|RE|RP|ST|TS|PL|PP|S\+|S-|FF|RW|AB|EP|EA|ED)\r'), self.__MatchOperationStatus, None)
            self.AddMatchString(compile(b'@0PM(OF|AL|AR|SP)\r'), self.__MatchPlayMode, None)
            self.AddMatchString(compile(b'@0PW0(0|1)\r'), self.__MatchPower, None)
            self.AddMatchString(compile(b'@0PS0(1|2|3)\r'), self.__MatchPreset, None)
            self.AddMatchString(compile(b'@0TR([0-9]{3})\r'), self.__MatchTrackNumber, None)
            self.AddMatchString(compile(b'@0TI([0-9]{3})([0-9]{2})([0-9]{2})\r'), self.__MatchTrackTime, None)

    def SetAudioInputSelect(self, value, qualifier):

        AudioInputSelectStateValues = {
            'Unbalanced Input': '@0INUN\r',
            'Balanced Input': '@0INBA\r',
            'Digital Input': '@0INDI\r',
        }
        AudioInputSelectCmdString = AudioInputSelectStateValues[value]
        self.__SetHelper('AudioInputSelect', AudioInputSelectCmdString, value, qualifier)

    def UpdateAudioInputSelect(self, value, qualifier):

        AudioInputSelectCmdString = '@0?IN\r'
        self.__UpdateHelper('AudioInputSelect', AudioInputSelectCmdString, value, qualifier)

    def __MatchAudioInputSelect(self, match, tag):

        AudioInputSelectStateValues = {
            'UN': 'Unbalanced Input',
            'BA': 'Balanced Input',
            'DI': 'Digital Input'
        }

        value = AudioInputSelectStateValues[match.group(1).decode()]
        self.WriteStatus('AudioInputSelect', value, None)

    def UpdateCardCondition(self, value, qualifier):

        CardConditionCmdString = '@0?CD\r'
        self.__UpdateHelper('CardCondition', CardConditionCmdString, value, qualifier)

    def __MatchCardCondition(self, match, tag):

        CardConditionStateValues = {
            'NC': 'No Card',
            'RE': 'Reading',
            'CI': 'Card Inside',
            'CE': 'Card Error',
            '99': 'Card 999',
            'FL': 'Card Full',
            'BC': 'Blank Card',
            'ER': 'Read Error',
            'WR': 'Writing',
            'EW': 'Write Error'
        }

        value = CardConditionStateValues[match.group(2).decode()]
        self.WriteStatus('CardCondition', value, None)

    def SetKeypad(self, value, qualifier):

        KeypadStateValues = {
            '0': '@02300\r',
            '1': '@02301\r',
            '2': '@02302\r',
            '3': '@02303\r',
            '4': '@02304\r',
            '5': '@02305\r',
            '6': '@02306\r',
            '7': '@02307\r',
            '8': '@02308\r',
            '9': '@02309\r'
        }

        KeypadCmdString = KeypadStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def UpdateOperationStatus(self, value, qualifier):

        OperationStatusCmdString = '@0?ST\r'
        self.__UpdateHelper('OperationStatus', OperationStatusCmdString, value, qualifier)

    def __MatchOperationStatus(self, match, tag):

        OperationStatusStateValues = {
            'RU': 'Digital In Unlock',
            'RE': 'Recording',
            'RP': 'Rec Pause',
            'ST': 'Stop',
            'TS': 'Track Select',
            'PL': 'Play',
            'PP': 'Play Pause',
            'S+': 'Seek +',
            'S-': 'Seek -',
            'FF': 'Fast Forward',
            'RW': 'Fast Reverse',
            'AB': 'A-B Repeat',
            'EP': 'EDL Play',
            'EA': 'EDL A-B Repeat',
            'ED': 'Track Edit/Preset',
        }

        value = OperationStatusStateValues[match.group(1).decode()]
        self.WriteStatus('OperationStatus', value, None)

    def SetPlayMode(self, value, qualifier):

        PlayModeStateValues = {
            'Normal': '@0PMOF\r',
            'Repeat All': '@0PMAL\r',
            'Repeat TRK': '@0PMAR\r',
            'Single': '@0PMSP\r'
        }

        PlayModeCmdString = PlayModeStateValues[value]
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def UpdatePlayMode(self, value, qualifier):

        PlayModeCmdString = '@0?PM\r'
        self.__UpdateHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def __MatchPlayMode(self, match, tag):

        PlayModeStateValues = {
            'OF': 'Normal',
            'AL': 'Repeat All',
            'AR': 'Repeat TRK',
            'SP': 'Single'
        }

        value = PlayModeStateValues[match.group(1).decode()]
        self.WriteStatus('PlayMode', value, None)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '@023PW\r',
            'Off': '@02312\r',
        }

        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = '@0?PW\r'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        PowerStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = PowerStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPreset(self, value, qualifier):

        PresetStateValues = {
            '1': '@0PS01\r',
            '2': '@0PS02\r',
            '3': '@0PS03\r'
        }

        PresetCmdString = PresetStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = '@0?PS\r'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        PresetStateValues = {
            '1': '1',
            '2': '2',
            '3': '3'
        }

        value = PresetStateValues[match.group(1).decode()]
        self.WriteStatus('Preset', value, None)

    def SetRecordingVolume(self, value, qualifier):

        RecordingVolumeStateValues = {
            'Up': '@023V+\r',
            'Down': '@023V-\r'
        }

        RecordingVolumeCmdString = RecordingVolumeStateValues[value]
        self.__SetHelper('RecordingVolume', RecordingVolumeCmdString, value, qualifier)

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?TR\r'
        self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)

    def __MatchTrackNumber(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('TrackNumber', value, None)

    def UpdateTrackTime(self, value, qualifier):

        TrackTimeCmdString = '@0?TI\r'
        self.__UpdateHelper('TrackTime', TrackTimeCmdString, value, qualifier)

    def __MatchTrackTime(self, match, tag):

        Hour = match.group(1).decode()
        Mins = match.group(2).decode()
        Secs = match.group(3).decode()
        value = Hour.lstrip('0') + ':' + Mins.lstrip('0') + ':' + Secs.lstrip('0')
        self.WriteStatus('TrackTime', value, None)

    def SetTransport(self, value, qualifier):

        TransportStateValues = {
            'Track Jump >>I (Next)': '@02332\r',
            'Track Jump I<< (Back)': '@02333\r',
            'Pause': '@02348\r',
            'Fast Reverse Start': '@02350\r',
            'Fast Reverse Stop': '@0235001\r',
            'Fast Forward Start': '@02352\r',
            'Fast Forward Stop': '@0235201\r',
            'Play': '@02353\r',
            'Stop': '@02354\r',
            'Record': '@02355\r'
        }

        TransportCmdString = TransportStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
            
        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='HW', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

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

