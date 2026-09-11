from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack

class DeviceSerialClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'EnableReturnCode': {'Status': {}},
            'MicrophoneStatus': {'Parameters': ['Microphone'], 'Status': {}},
        }

        self.AddMatchString(re.compile(b'\x1B\\x24\x0D\x05\x04\x00\x0E\x00([\x01-\xFF])\x02'), self.__MatchMicrophoneStatus, 'On')
        self.AddMatchString(re.compile(b'\x1B\\x24\x0D\x05\x08\x00\x01\x00([\x01-\xFF])\x02\x01\x00\x03\x00\x1B\\x24\x0D\x05\x04\x00\x02\x00\x01\x00'), self.__MatchMicrophoneStatus, 'On')
        self.AddMatchString(re.compile(b'\x1B\\x24\x0D\x05\x04\x00\x0F\x00([\x01-\xFF])\x02'), self.__MatchMicrophoneStatus, 'Off')
        self.AddMatchString(re.compile(b'\x1B\\x24\x0D\x05\x08\x00\x01\x00([\x01-\xFF])\x02\x02\x00\x03\x00\x1B\\x24\x0D\x05\x04\x00\x02\x00\x00\x00'), self.__MatchMicrophoneStatus, 'Off')

    def SetEnableReturnCode(self, value, qualifier):
        self.__SetHelper('EnableReturnCode', b'\x1B\x24\x0D\x03\x02\x00\x1E\x00\x90', value, qualifier)

    def __MatchMicrophoneStatus(self, match, tag):
        Mic = str(match.group(1)[0])
        self.WriteStatus('MicrophoneStatus', tag, {'Microphone': Mic})

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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
                    except BaseException:
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
                    except BaseException:
                        break
            if 'callback' in Method and Method['callback']:
                Method['callback'](command, value, qualifier)

    # Save new status to the command
    def WriteStatus(self, command, value, qualifier=None):
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
        except BaseException:
            return None

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
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

class DeviceEthernetClass:

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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChairmanStatus': {'Status': {}},
            'ClearRequestToSpeakListAndSpeakersList': {'Status': {}},
            'DualDelegateMicrophoneControl': {'Parameters': ['Dual Delegate Unit', 'L/R'], 'Status': {}},
            'DualDelegateMicrophoneControlLastActioned': {'Parameters': ['L/R'], 'Status': {}},
            'MicrophoneControl': {'Parameters': ['Microphone'], 'Status': {}},
            'MicrophoneControlLastActioned': {'Status': {}},
            'RequestToSpeakList': {'Parameters': ['Index'], 'Status': {}},
            'SpeakersList': {'Parameters': ['Index'], 'Status': {}},
            'WirelessMicrophoneControl': {'Parameters': ['Microphone'], 'Status': {}},
            'WirelessMicrophoneControlLastActioned': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x05\x01\x00\x43\x18[\x00]{11}\x01[\x00-\xFF](?P<Microphone>[\x00-\xF5])\x3E(?P<State>[\x00\x01\x02\x0E\x0F])\x00\x03'), self.__MatchWirelessMicrophoneControl, None)
            self.AddMatchString(re.compile(b'\x05[\x00-\xFF]\x00\x43\x14[\x00]{11}(?P<State>[\x00\x01\x02\x0E\x0F])\x00(?P<Microphone>[\x00-\xF5])\x3E'), self.__MatchWirelessMicrophoneControl, None)
            self.AddMatchString(re.compile(b'\x05\x01\x00\x43\x18[\x00]{11}\x01[\x00-\xFF](?P<UnitID>[\x00-\xFF]{2})(?P<State>[\x01\x0E])\x00\x03'), self.__MatchMicrophoneControl, 'On')
            self.AddMatchString(re.compile(b'\x05\x01\x00\x43\x18[\x00]{11}\x01[\x00-\xFF](?P<UnitID>[\x00-\xFF]{2})(?P<State>[\x00\x02\x0F])\x00\x03'), self.__MatchMicrophoneControl, 'Off')
            self.AddMatchString(re.compile(b'\x05\x0E\x00\x43\x14[\x00]{11}\x0E[\x00-\xFF](?P<UnitID>[\x00-\xF5][\x03\x02])'), self.__MatchMicrophoneControl, 'On')
            self.AddMatchString(re.compile(b'\x05\x0F\x00\x43\x14[\x00]{11}\x0F[\x00-\xFF](?P<UnitID>[\x00-\xF5][\x03\x02])'), self.__MatchMicrophoneControl, 'Off')
            self.AddMatchString(re.compile(b'\x05\x02\x00\x43\x14[\x00]{11}\x02\x00(\x01|\x00)\x00'), self.__MatchChairmanStatus, None)
            self.AddMatchString(re.compile(b'\x05\x06\x00\x43\x16[\x00]{11}\x06\x00(?P<UnitID>[\x00-\xF5]\x02)'), self.__MatchMicrophoneControl, 'Off')
            self.AddMatchString(re.compile(b'\x04\x25\x00\x43[\x1A-\xFF][\x00]{11}\x25\x00\x00\x00(?P<Length>[\x01-\x19])\x00(?P<List>([\x00-\xF5]\x02[\x00-\xF5]\x00){1,25})'), self.__MatchRequestToSpeakList, None)
            self.AddMatchString(re.compile(b'\x04\x25\x00\x43\x16[\x00]{11}\x25\x00\x00\x00\x00\x00'), self.__MatchRequestToSpeakList, 'ClearList')
            self.AddMatchString(re.compile(b'\x04\\x2E\x00\x43[\x19-\xFF][\x00]{11}\\x2E\x00\x00\x00(?P<Length>[\x01-\x19])\x00(?P<List>([\x00-\xF5][\x02\x03][\x00-\x01]){1,25})'), self.__MatchSpeakersList, None)
            self.AddMatchString(re.compile(b'\x04\\x2E\x00\x43\x16[\x00]{11}\\x2E\x00\x00\x00\x00'), self.__MatchSpeakersList, 'ClearList')
            self.AddMatchString(re.compile(b'\x04\x2F\x00\x43\x14[\x00]{11}\x2F\x00\x00\x00'), self.__MatchClearSpeakersList, 'ClearSpeakersList')

# BEGIN AUTO GENERATION OF COMMAND DEF    

    def __MatchChairmanStatus(self, match, qualifier):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ChairmanStatus', value, None)

    def SetClearRequestToSpeakListAndSpeakersList(self, value, qualifier):

        MM_C_RTS_CLEAR = b'\x03\x26\x00\x43\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x26\x00'
        MM_C_SPK_CLEAR = b'\x03\x2F\x00\x43\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2F\x00'

        self.__SetHelper('ClearRequestToSpeakListAndSpeakersList', MM_C_RTS_CLEAR + MM_C_SPK_CLEAR, value, qualifier)

    def __MatchClearSpeakersList(self, match, qualifier):
        for i in range(1, 246):
            self.WriteStatus('MicrophoneControl', 'Off', {'Microphone': str(i)})
            
    # Dual Delegate Microphone Control    
    def SetDualDelegateMicrophoneControl(self, value, qualifier):

        Microphone_Offset = 256 if qualifier['L/R'] == 'Right' else 0

        CCU_Offset = 512

        UnitID = int(qualifier['Dual Delegate Unit']) + CCU_Offset + Microphone_Offset
        Mic = pack('H', UnitID)

        MM_C_MICRO_ON = b'\x03\x22\x00\x43\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\x00' + Mic + b'\x01'
        MM_C_MICRO_OFF = b'\x03\x22\x00\x43\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\x00' + Mic + b'\x00'
        MM_C_SPK_APPEND = b'\x03\x30\x00\x43\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\x00' + Mic
        MM_C_SPK_REMOVE = b'\x03\x31\x00\x43\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x31\x00' + Mic
        MM_C_RTS_APPEND = b'\x03\x3E\x00\x43\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3E\x00' + Mic + b'\xFF\xFF'
        MM_C_RTS_REMOVE = b'\x03\x27\x00\x43\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x27\x00' + Mic + b'\xFF\xFF'

        States = {
            'On': MM_C_MICRO_ON,
            'Off': MM_C_MICRO_OFF + MM_C_SPK_REMOVE + MM_C_RTS_REMOVE,
            'Add to Speakers List': MM_C_SPK_APPEND,
            'Remove from Speakers List': MM_C_SPK_REMOVE,
            'Add to Request To Speak List': MM_C_RTS_APPEND,
            'Remove from Request To Speak List': MM_C_RTS_REMOVE,
        }

        if 1 <= int(qualifier['Dual Delegate Unit']) <= 245:
            self.__SetHelper('DualDelegateMicrophoneControl', States[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetDualDelegateMicrophoneControl')

    def UpdateRequestToSpeakList(self, value, qualifier):
        MM_C_RTS_GET = b'\x03\x25\x00\x43\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x25\x00'
        self.__UpdateHelper('RequestToSpeakList', MM_C_RTS_GET, value, qualifier)
        
    def __MatchRequestToSpeakList(self, match, tag):
        if tag == 'ClearList':
            for i in range(1, 26):
                self.WriteStatus('RequestToSpeakList', '0', {'Index': str(i)})
        else:
            Length = match.group('Length')[0]
            List = match.group('List')
            for i in range(1, 26):
                Index = (i - 1) * 4
                if i <= Length:
                    self.WriteStatus('RequestToSpeakList', str(List[Index]), {'Index': str(i)})
                    self.WriteStatus('MicrophoneControl', 'Request To Speak', {'Microphone': str(List[Index])})
                else:
                    self.WriteStatus('RequestToSpeakList', '0', {'Index': str(i)})

    def UpdateSpeakersList(self, value, qualifier):

        MM_C_SPK_GET = b'\x03\x2E\x00\x43\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x2E\x00'
        self.__UpdateHelper('SpeakersList', MM_C_SPK_GET, value, qualifier)

    def __MatchSpeakersList(self, match, tag):
        if tag == 'ClearList':
            for i in range(1, 26):
                self.WriteStatus('SpeakersList', '0', {'Index': str(i)})
            for i in range(1, 246):
                self.WriteStatus('MicrophoneControl', 'Off', {'Microphone': str(i)})
                self.WriteStatus('DualDelegateMicrophoneControl', 'Off', {'Dual Delegate Unit': str(i), 'L/R': 'Left'})
                self.WriteStatus('DualDelegateMicrophoneControl', 'Off', {'Dual Delegate Unit': str(i), 'L/R': 'Right'})
        else:
            Length = match.group('Length')[0]
            List = match.group('List')
            for i in range(1, 26):
                Index = (i - 1) * 3
                if i <= Length:
                    self.WriteStatus('SpeakersList', str(List[Index]), {'Index': str(i)})
                    self.WriteStatus('MicrophoneControl', 'On', {'Microphone': str(List[Index])})
                    self.WriteStatus('MicrophoneControlLastActioned', str(List[Index]), None)
                    if List[Index + 1] == 2:
                        self.WriteStatus('DualDelegateMicrophoneControl', 'On', {'Dual Delegate Unit': str(List[Index]), 'L/R': 'Left'})
                        self.WriteStatus('DualDelegateMicrophoneControlLastActioned', str(List[Index]), {'L/R': 'Left'})
                    else:
                        self.WriteStatus('DualDelegateMicrophoneControl', 'On', {'Dual Delegate Unit': str(List[Index]), 'L/R': 'Right'})
                        self.WriteStatus('DualDelegateMicrophoneControlLastActioned', str(List[Index]), {'L/R': 'Right'})
                else:
                    self.WriteStatus('SpeakersList', '0', {'Index': str(i)})

    def SetMicrophoneControl(self, value, qualifier):

        UnitID = int(qualifier['Microphone']) + 512
        Mic = pack('H', UnitID)

        MM_C_MICRO_ON = b'\x03\x22\x00\x43\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\x00' + Mic + b'\x01'
        MM_C_MICRO_OFF = b'\x03\x22\x00\x43\x15\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x22\x00' + Mic + b'\x00'
        MM_C_SPK_APPEND = b'\x03\x30\x00\x43\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x30\x00' + Mic
        MM_C_SPK_REMOVE = b'\x03\x31\x00\x43\x14\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x31\x00' + Mic
        MM_C_RTS_APPEND = b'\x03\x3E\x00\x43\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3E\x00' + Mic + b'\xFF\xFF'
        MM_C_RTS_REMOVE = b'\x03\x27\x00\x43\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x27\x00' + Mic + b'\xFF\xFF'

        States = {
            'On': MM_C_MICRO_ON,
            'Off': MM_C_MICRO_OFF + MM_C_SPK_REMOVE + MM_C_RTS_REMOVE,
            'Add to Speakers List': MM_C_SPK_APPEND,
            'Remove from Speakers List': MM_C_SPK_REMOVE,
            'Add to Request To Speak List': MM_C_RTS_APPEND,
            'Remove from Request To Speak List': MM_C_RTS_REMOVE,
        }

        if 1 <= int(qualifier['Microphone']) <= 245:
            self.__SetHelper('MicrophoneControl', States[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetMicrophoneControl')

    def __MatchMicrophoneControl(self, match, tag):
        UnitID = unpack('H', match.group('UnitID'))[0]
        Mic = int(UnitID % 512)

        if 1 <= Mic <= 245:
            self.WriteStatus('MicrophoneControl', tag, {'Microphone': str(Mic)})
            self.WriteStatus('DualDelegateMicrophoneControl', tag, {'Dual Delegate Unit': str(Mic), 'L/R': 'Left'})
            self.WriteStatus('DualDelegateMicrophoneControlLastActioned', str(Mic), {'L/R': 'Left'})
        else:
            Mic -= 255
            self.WriteStatus('DualDelegateMicrophoneControl', tag, {'Dual Delegate Unit': str(Mic), 'L/R': 'Right'})
            self.WriteStatus('DualDelegateMicrophoneControlLastActioned', str(Mic), {'L/R': 'Right'})

        self.WriteStatus('MicrophoneControlLastActioned', str(Mic), None)

    def SetWirelessMicrophoneControl(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00,
            'Add to Speakers List': 0x30,
            'Remove from Speakers List': 0x31,
            'Add to Request To Speak List': 0x3E,
            'Remove from Request To Speak List': 0x27,
        }

        mic_num = int(qualifier['Microphone'])
        if 1 <= mic_num <= 245 and value in ValueStateValues:
            if value in ['On', 'Off']:
                WirelessMicrophoneControlCmdString = pack('21B', 0x03, 0x22, 0x00, 0x43, 0x15, 0x00, 0x00, 0x00, 0x00,
                                                          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x22, 0x00, mic_num,
                                                          0x3E, ValueStateValues[value])
            elif value in ['Add to Speakers List', 'Remove from Speakers List']:
                WirelessMicrophoneControlCmdString = pack('20B', 0x03, ValueStateValues[value], 0x00, 0x43, 0x14, 0x00,
                                                          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                          ValueStateValues[value], 0x00, mic_num, 0x3E)
            else:
                WirelessMicrophoneControlCmdString = pack('22B', 0x03, ValueStateValues[value], 0x00, 0x43, 0x16, 0x00,
                                                          0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                                          ValueStateValues[value], 0x00, mic_num, 0x3E, 0xFF, 0xFF)
            self.__SetHelper('WirelessMicrophoneControl', WirelessMicrophoneControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWirelessMicrophoneControl')

    def __MatchWirelessMicrophoneControl(self, match, qualifier):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off',
            b'\x02': 'Off',
            b'\x0E': 'On',
            b'\x0F': 'Off',
        }

        mic_num = unpack('B', match.group('Microphone'))[0]
        qualifier = {'Microphone': str(mic_num)}
        value = ValueStateValues[match.group('State')]
        self.WriteStatus('WirelessMicrophoneControl', value, qualifier)
        self.WriteStatus('WirelessMicrophoneControlLastActioned', str(mic_num), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
                    except:
                        if Parameter in qualifier:
                            Method[qualifier[Parameter]] = {}
                            Method = Method[qualifier[Parameter]]
                        else:
                            return

            Method['callback'] = callback
            Method['qualifier'] = qualifier
        else:
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ', command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
        
    def Connect(self, *args, **kwargs):
        result = EthernetClientInterface.Connect(self, *args, **kwargs)
        if result == 'Connected':
            self.Send(b'\x27\x70\x44\x00\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            self.Send(b'\x03\x1E\x00\x43\x12\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1E\x00')
        return result
