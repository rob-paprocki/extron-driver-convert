from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelExert': {'Parameters': ['Channel'], 'Status': {}},
            'ChannelLevel': {'Parameters': ['Channel'], 'Status': {}},
            'RelayStatus': {'Parameters': ['Channel'], 'Status': {}},
            'Scene': {'Status': {}},
            'SceneStatus': {'Parameters': ['Scene'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xA5.\x0D([\x00-\xFF]{2})([\x00-\x64]{16})([\x00-\xFF]{2})([\x00-\xFF]{2})'), self.__MatchChannelLevel, None)

    def checksum(self, command):
        odd_bytes = command[::2]
        even_bytes = command[1::2]

        odd_checksum = 0
        even_checksum = 0

        for i in odd_bytes:
            odd_checksum ^= i

        for i in even_bytes:
            even_checksum ^= i

        return command + bytes([(~odd_checksum) & 0xFF]) + bytes([(~even_checksum) & 0xFF])
    
    def SetChannelExert(self, value, qualifier):

        ChannelStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F',
            '16': b'\x10'
        }

        ChannelExertStateValues = {
            'On': b'\x01',
            'Off': b'\x02'
        }

        Channel = qualifier['Channel']

        if not all([Channel in ChannelStates,
                    value in ChannelExertStateValues]):
            self.Discard('Invalid Command for SetChannelExert')
            return

        ChannelExertCmdString = self.checksum(b'\xA5\x08\x7A' + ChannelStates[Channel] + ChannelExertStateValues[value] + b'\x00')
        self.__SetHelper('ChannelExert', ChannelExertCmdString, value, qualifier)
           
    def SetChannelLevel(self, value, qualifier):

        ChannelStates = {
            '1': b'\x01',
            '2': b'\x02',
            '3': b'\x03',
            '4': b'\x04',
            '5': b'\x05',
            '6': b'\x06',
            '7': b'\x07',
            '8': b'\x08',
            '9': b'\x09',
            '10': b'\x0A',
            '11': b'\x0B',
            '12': b'\x0C',
            '13': b'\x0D',
            '14': b'\x0E',
            '15': b'\x0F',
            '16': b'\x10'
        }

        Channel = qualifier['Channel']

        if not all([Channel in ChannelStates,
                    0 <= value <= 100]):
            self.Discard('Invalid Command for SetChannelLevel')
            return

        ChannelLevelCmdString = self.checksum(b'\xA5\x08\x7A' + ChannelStates[Channel] + b'\x05' + pack('>B', value))
        self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)

    def UpdateChannelLevel(self, value, qualifier):
        
        HeartbeatCmdString = self.checksum(b'\xA5\x05\x0C')
        self.__UpdateHelper('ChannelLevel', HeartbeatCmdString, value, qualifier)
        
    def __MatchChannelLevel(self, match, tag):

        RelayStatusStates = {
            '0': 'Open',
            '1': 'Closed'
        }

        SceneStatusStates = {
            '0000': 'Disable',
            '0001': 'Active',
            '0010': 'Idle',
            '0011': 'Error'
        }
        relay_data = '{:016b}'.format(unpack('>H', match.group(1))[0])[::-1]
        for i in range(0, 16):
            value = RelayStatusStates[relay_data[i]]
            self.WriteStatus('RelayStatus', value, {'Channel': str(i + 1)})
        for i in range(0, 16):
            value = match.group(2)[i]
            self.WriteStatus('ChannelLevel', value, {'Channel': str(i + 1)})
        scene_data = '{:016b}'.format(unpack('>H', match.group(3))[0])
        for i in range(0, 4):
            value = SceneStatusStates[scene_data[i * 4:(i + 1) * 4]]
            self.WriteStatus('SceneStatus', value, {'Scene': str(i + 1)})    

    def SetScene(self, value, qualifier):

        SceneStateValues = {
            '1': b'\xA5\x06\x85\x01',
            '2': b'\xA5\x06\x85\x02',
            '3': b'\xA5\x06\x85\x03',
            '4': b'\xA5\x06\x85\x04'
        }

        SceneCmdString = self.checksum(SceneStateValues[value])
        self.__SetHelper('Scene', SceneCmdString, value, qualifier)

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
