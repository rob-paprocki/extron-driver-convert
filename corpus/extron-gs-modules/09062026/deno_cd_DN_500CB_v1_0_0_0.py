from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
            'CurrentTrackTime': {'Status': {}},
            'DiscTray': {'Status': {}},
            'ElapsedTime': {'Status': {}},
            'Keypad': {'Status': {}},
            'MediaStatus': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RemainingTime': {'Status': {}},
            'TotalTrackNumber': {'Status': {}},
            'TrackInformation': {'Parameters': ['Track'], 'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'@0tl(\d{3})(\d{2})\r', re.I), self.__MatchCurrentTrackTime, None)
            self.AddMatchString(re.compile(b'@0ET(\d{3})(\d{2})(\d{2})\r', re.I), self.__MatchElapsedTime, None)
            self.AddMatchString(re.compile(b'@0CD(NC|CI)\r', re.I), self.__MatchMediaStatus, None)
            self.AddMatchString(re.compile(b'@0mt0(0|1)\r', re.I), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'@0RM(\d{3})(\d{2})(\d{2})\r', re.I), self.__MatchRemainingTime, None)
            self.AddMatchString(re.compile(b'@0Tt(\d{4})\r', re.I), self.__MatchTotalTrackNumber, None)
            self.AddMatchString(re.compile(b'@0(at|ti|al)([^\r]{0,64})\r'), self.__MatchTrackInformation, None)
            self.AddMatchString(re.compile(b'@0Tr(\d{4})\r', re.I), self.__MatchTrackNumber, None)
            self.AddMatchString(re.compile(b'@0ST(PL|PP|DVFF|DVFR)\r', re.I), self.__MatchTransport, None)
            self.AddMatchString(re.compile(b'\x15'), self.__MatchError, None)

    def UpdateCurrentTrackTime(self, value, qualifier):

        CurrentTrackTimeCmdString = '@0?tl\r'
        self.__UpdateHelper('CurrentTrackTime', CurrentTrackTimeCmdString, value, qualifier)

    def __MatchCurrentTrackTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode()
        self.WriteStatus('CurrentTrackTime', value, None)

    def SetDiscTray(self, value, qualifier):

        ValueStateValues = {
            'Open': 'OP',
            'Close': 'CL'
        }

        DiscTrayCmdString = '@0PCDTRY{}\r'.format(ValueStateValues[value])
        self.__SetHelper('DiscTray', DiscTrayCmdString, value, qualifier)

    def UpdateElapsedTime(self, value, qualifier):

        ElapsedTimeCmdString = '@0?ET\r'
        self.__UpdateHelper('ElapsedTime', ElapsedTimeCmdString, value, qualifier)

    def __MatchElapsedTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        self.WriteStatus('ElapsedTime', value, None)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            KeypadCmdString = '@0PCTKEY{}\r'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetKeypad')

    def UpdateMediaStatus(self, value, qualifier):

        MediaStatusCmdString = '@0?CD\r'
        self.__UpdateHelper('MediaStatus', MediaStatusCmdString, value, qualifier)

    def __MatchMediaStatus(self, match, tag):

        ValueStateValues = {
            'NC': 'No Disc',
            'CI': 'Disc In'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('MediaStatus', value, None)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        MuteCmdString = '@0mt{}\r'.format(ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        MuteCmdString = '@0?mt\r'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        PowerCmdString = '@0PW0{}\r'.format(ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdateRemainingTime(self, value, qualifier):

        RemainingTimeCmdString = '@0?RM\r'
        self.__UpdateHelper('RemainingTime', RemainingTimeCmdString, value, qualifier)

    def __MatchRemainingTime(self, match, tag):

        value = match.group(1).decode() + ':' + match.group(2).decode() + ':' + match.group(3).decode()
        self.WriteStatus('RemainingTime', value, None)

    def UpdateTotalTrackNumber(self, value, qualifier):

        TotalTrackNumberCmdString = '@0?Tt\r'
        self.__UpdateHelper('TotalTrackNumber', TotalTrackNumberCmdString, value, qualifier)

    def __MatchTotalTrackNumber(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('TotalTrackNumber', value, None)

    def UpdateTrackInformation(self, value, qualifier):

        TrackStates = {
            'Title': 'ti',
            'Artist': 'at',
            'Album': 'al'
        }

        TrackInformationCmdString = '@0?{}\r'.format(TrackStates[qualifier['Track']])
        self.__UpdateHelper('TrackInformation', TrackInformationCmdString, value, qualifier)

    def __MatchTrackInformation(self, match, tag):

        TrackStates = {
            'ti': 'Title',
            'at': 'Artist',
            'al': 'Album'
        }

        qualifier = {}
        qualifier['Track'] = TrackStates[match.group(1).decode()]
        value = match.group(2).decode()
        self.WriteStatus('TrackInformation', value, qualifier)

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = '@0?Tr\r'
        self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)

    def __MatchTrackNumber(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('TrackNumber', value, None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '@02353\r',
            'Stop': '@02354\r',
            'Pause': '@02348\r',
            'Track/Jump Next': '@02332\r',
            'Track/Jump Prev': '@02333\r',
            'Fast Forward': '@0PCSLSF\r',
            'Reverse': '@0PCSLSR\r',
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        TransportCmdString = '@0?ST\r'
        self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)

    def __MatchTransport(self, match, tag):

        ValueStateValues = {
            'PL': 'Play',
            'PP': 'Pause',
            'DVFF': 'Fast Forward',
            'DVFR': 'Reverse'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Transport', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
            
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        print('Device responded with an error.')

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
