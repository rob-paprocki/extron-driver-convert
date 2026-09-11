from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


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
            'BassLevel': {'Parameters': ['Channel Attribute', 'Channel Number'], 'Status': {}},
            'Channel': {'Parameters': ['Channel Attribute', 'Channel Number'], 'Status': {}},
            'CrosspointGain': {'Parameters': ['Source Channel', 'Destination Channel'], 'Status': {}},
            'InputGain': {'Parameters': ['Channel Number'], 'Status': {}},
            'OutputGain': {'Parameters': ['Channel Number'], 'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'StayConnected': {'Status': {}},
            'TrebleLevel': {'Parameters': ['Channel Attribute', 'Channel Number'], 'Status': {}},
        }

        self.ChannelAttributeStates = {
            'Input': 0,
            'Output': 1
        }

        self.ChannelNumberStates = {
            '1': 0,
            '2': 1,
            '3': 2,
            '4': 3,
            '5': 4,
            '6': 5,
            '7': 6,
            '8': 7
        }

        self.MatchChannelAttributeStates = {
            b'\x00': 'Input',
            b'\x01': 'Output'
        }

        self.MatchChannelNumberStates = {
            b'\x00': '1',
            b'\x01': '2',
            b'\x02': '3',
            b'\x03': '4',
            b'\x04': '5',
            b'\x05': '6',
            b'\x06': '7',
            b'\x07': '8'
        }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xAA\x04([\x00-\x01])([\x00-\x07])\x00([\x00-\x18])'), self.__MatchBassLevel, None)
            self.AddMatchString(re.compile(b'\x92\x03([\x00-\x01])([\x00-\x07])([\x00-\x01])'), self.__MatchChannel, None)
            self.AddMatchString(re.compile(b'\x95\x05\x00([\x00-\x07])\x01([\x00-\x07])([\x00-\x81])'), self.__MatchCrosspointGain, None)
            self.AddMatchString(re.compile(b'\x91\x03\x00([\x00-\x07])([\x00-\x7E])'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'\x91\x03\x01([\x00-\x07])([\x00-\x7E])'), self.__MatchOutputGain, None)
            self.AddMatchString(re.compile(b'\xC0\x09[\x00-\x01][\x00-\x07]'), self.__MatchStayConnected, None)
            self.AddMatchString(re.compile(b'\xF4\x01([\x00-\x01])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\xAA\x04([\x00-\x01])([\x00-\x07])\x01([\x00-\x18])'), self.__MatchTrebleLevel, None)
       
    def SetBassLevel(self, value, qualifier):

        attribute = qualifier['Channel Attribute']
        number = qualifier['Channel Number']

        if 0 <= value <= 24 and 1 <= int(number) <= 8 and attribute in self.ChannelAttributeStates:
            BassLevelCmdString = pack('BBBBBB', 0xAA, 0x04, self.ChannelAttributeStates[attribute], self.ChannelNumberStates[number], 0x00, value)
            self.__SetHelper('BassLevel', BassLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBassLevel')

    def __MatchBassLevel(self, match, tag):

        attribute = self.MatchChannelAttributeStates[match.group(1)]
        number = self.MatchChannelNumberStates[match.group(2)]

        value = ord(match.group(3))
        self.WriteStatus('BassLevel', value, {'Channel Attribute': attribute, 'Channel Number': number})

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        attribute = qualifier['Channel Attribute']
        number = qualifier['Channel Number']

        if 1 <= int(number) <= 8 and attribute in self.ChannelAttributeStates:
            ChannelCmdString = pack('BBBBB', 0x92, 0x03, self.ChannelAttributeStates[attribute], self.ChannelNumberStates[number], ValueStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetChannel')

    def __MatchChannel(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        attribute = self.MatchChannelAttributeStates[match.group(1)]
        number = self.MatchChannelNumberStates[match.group(2)]
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('Channel', value, {'Channel Attribute': attribute, 'Channel Number': number})

    def SetCrosspointGain(self, value, qualifier):

        source = qualifier['Source Channel']
        destination = qualifier['Destination Channel']

        if 0 <= value <= 81 and 1 <= int(source) <= 8 and 1 <= int(destination) <= 8:
            CrosspointGainCmdString = pack('BBBBBBB', 0x95, 0x05, 0x00, self.ChannelNumberStates[source], 0x01, self.ChannelNumberStates[destination], value)
            self.__SetHelper('CrosspointGain', CrosspointGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointGain')

    def __MatchCrosspointGain(self, match, tag):

        source = self.MatchChannelNumberStates[match.group(1)]
        destination = self.MatchChannelNumberStates[match.group(2)]

        value = ord(match.group(3))
        self.WriteStatus('CrosspointGain', value, {'Source Channel': source, 'Destination Channel': destination})

    def SetInputGain(self, value, qualifier):

        number = qualifier['Channel Number']

        if 0 <= value <= 126 and 1 <= int(number) <= 8:
            InputGainCmdString = pack('BBBBB', 0x91, 0x03, 0x00, self.ChannelNumberStates[number], value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def __MatchInputGain(self, match, tag):

        number = self.MatchChannelNumberStates[match.group(1)]

        value = ord(match.group(2))
        self.WriteStatus('InputGain', value, {'Channel Number': number})

    def SetOutputGain(self, value, qualifier):

        number = qualifier['Channel Number']

        if 0 <= value <= 126 and 1 <= int(number) <= 8:
            OutputGainCmdString = pack('BBBBB', 0x91, 0x03, 0x01, self.ChannelNumberStates[number], value)
            self.__SetHelper('OutputGain', OutputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputGain')

    def __MatchOutputGain(self, match, tag):

        number = self.MatchChannelNumberStates[match.group(1)]

        value = ord(match.group(2))
        self.WriteStatus('OutputGain', value, {'Channel Number': number})

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('BBB', 0xF4, 0x01, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            PresetRecallCmdString = pack('BBBB', 0xF1, 0x02, 0x00, int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def UpdateStayConnected(self, value, qualifier):

        StayConnectedCmdString = pack('BBBBB', 0xF0, 0x03, 0x40, 0x00, 0x00)
        self.__UpdateHelper('StayConnected', StayConnectedCmdString, value, qualifier)
               
    def __MatchStayConnected(self, match, tag):
        self.WriteStatus('ConnectionStatus', 'Connected')
        
    def SetTrebleLevel(self, value, qualifier):

        attribute = qualifier['Channel Attribute']
        number = qualifier['Channel Number']

        if 0 <= value <= 24 and 1 <= int(number) <= 8 and attribute in self.ChannelAttributeStates:
            TrebleLevelCmdString = pack('BBBBBB', 0xAA, 0x04, self.ChannelAttributeStates[attribute], self.ChannelNumberStates[number], 0x01, value)
            self.__SetHelper('TrebleLevel', TrebleLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTrebleLevel')

    def __MatchTrebleLevel(self, match, tag):

        attribute = self.MatchChannelAttributeStates[match.group(1)]
        number = self.MatchChannelNumberStates[match.group(2)]

        value = ord(match.group(3))
        self.WriteStatus('TrebleLevel', value, {'Channel Attribute': attribute, 'Channel Number': number})

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
