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
            'AudioMode': {'Parameters': ['Zone'], 'Status': {}},
            'HDMIOutput': {'Status': {}},
            'Input': {'Parameters': ['Zone'], 'Status': {}},
            'Keypad': {'Parameters': ['Zone'], 'Status': {}},
            'MenuNavigation': {'Parameters': ['Zone'], 'Status': {}},
            'Mute': {'Parameters': ['Zone'], 'Status': {}},
            'Power': {'Parameters': ['Zone'], 'Status': {}},
            'Transport': {'Parameters': ['Zone'], 'Status': {}},
            'TuneFM': {'Parameters': ['Zone'], 'Status': {}},
            'TuneFMStatus': {'Parameters': ['Zone'], 'Status': {}},
            'Volume': {'Parameters': ['Zone'], 'Status': {}},
            'Zone1OnScreenDisplay': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x0B\x00\x01(\x00|\x01|\x02)\x0D'), self.__MatchAudioMode, None)
            self.AddMatchString(re.compile(b'!\x01\x4F\x00\x01(\x02|\x03|\x04)\x0D'), self.__MatchHDMIOutput, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x1D\x00\x01([\x00-\x06]|\x08|\x09|\x0B|[\x0E-\x11])\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x0E\x00\x01(\x00|\x01)\x0D'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x00\x00\x01(\x00|\x01)\x0D'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x16\x00\x02([\x55-\x6C])([\x00-\x63])\x0D'), self.__MatchTuneFMStatus, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)\x0D\x00\x01([\x00-\x63])\x0D'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'!\x01\x4E\x00\x01(\x00|\x01)\x0D'), self.__MatchZone1OnScreenDisplay, None)
            self.AddMatchString(re.compile(b'!(\x01|\x02)(\x08|\x0B|\x25|\x1D|\x0E|\x00|\x0D|\x4F|\x16|\x4E)(\x82|\x83|\x84|\x85|\x86)[\x00-\xFF]{1,4}\x0D'), self.__MatchError, None)

    def SetAudioMode(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            ValueStateValues = {
                'Analogue': 0,
                'Digital': 1,
                'HDMI': 2
            }
            AudioModeCmdString = bytes((0x21, Zone, 0x0B, 1, ValueStateValues[value], 13))
            self.__SetHelper('AudioMode', AudioModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetAudioMode')

    def UpdateAudioMode(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            AudioModeCmdString = bytes((0x21, Zone, 0x0B, 1, 0xF0, 13))
            self.__UpdateHelper('AudioMode', AudioModeCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateAudioMode')

    def __MatchAudioMode(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Analogue',
            b'\x01': 'Digital',
            b'\x02': 'HDMI'
        }
        qualifier = {'Zone': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('AudioMode', value, qualifier)

    def SetHDMIOutput(self, value, qualifier):

        ValueStateValues = {
            '1': b'!\x01\x4F\x01\x02\x0D',
            '2': b'!\x01\x4F\x01\x03\x0D',
            'Both': b'!\x01\x4F\x01\x04\x0D'
        }
        HDMIOutputCmdString = ValueStateValues[value]
        self.__SetHelper('HDMIOutput', HDMIOutputCmdString, value, qualifier)

    def UpdateHDMIOutput(self, value, qualifier):

        HDMIOutputCmdString = b'!\x01\x4F\x01\xF0\x0D'
        self.__UpdateHelper('HDMIOutput', HDMIOutputCmdString, value, qualifier)

    def __MatchHDMIOutput(self, match, tag):

        ValueStateValues = {
            b'\x02': '1',
            b'\x03': '2',
            b'\x04': 'Both'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('HDMIOutput', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'CD': (0x76, 0x06),
            'BD': (0x62, 0x07),
            'AV': (0x5E, 0x09),
            'SAT': (0x1B, 0x14),
            'PVR': (0x60, 0x0F),
            'VCR': (0x77, 0x15),
            'AUX': (0x63, 0x0D),
            'Display': (0x3A,),
            'Tuner (FM)': (0x1C, 0x0E),
            'Net': (0x5C, 0x13),
            'USB': (0x5D, 0x12),
            'STB': (0x64, 0x08),
            'Game': (0x61, 0x0B)
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2) and not (Zone == 2 and value == 'Display'):
            InputCmdString = bytes((0x21, Zone, 8, 2, (0x10, 0x17)[Zone - 1], ValueStateValues[value][Zone - 1], 13))
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            InputCmdString = bytes((0x21, Zone, 0x1D, 1, 0xF0, 13))
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            b'\x00': 'Follow Zone 1',
            b'\x01': 'CD',
            b'\x02': 'BD',
            b'\x03': 'AV',
            b'\x04': 'SAT',
            b'\x05': 'PVR',
            b'\x06': 'VCR',
            b'\x08': 'AUX',
            b'\x09': 'Display',
            b'\x0B': 'Tuner (FM)',
            b'\x0E': 'Net',
            b'\x0F': 'USB',
            b'\x10': 'STB',
            b'\x11': 'Game'
        }
        qualifier = {'Zone': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Input', value, qualifier)

    def SetKeypad(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            KeypadCmdString = bytes((0x21, Zone, 8, 2, 0x10, int(value), 0x0D))
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Disc (Record) (Enter Trim Menu)': 0x5A,
            'System Menu': 0x52,
            'Up': 0x56,
            'Down': 0x55,
            'Left': 0x51,
            'Right': 0x50,
            'OK': 0x57,
            'Home': 0x2B,
            'Red': 0x29,
            'Green': 0x2A,
            'Yellow': 0x2B,
            'Blue': 0x37
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            MenuNavigationCmdString = bytes((0x21, Zone, 8, 2, 0x10, ValueStateValues[value], 0x0D))
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': (0x1A, 4),
            'Off': (0x78, 5)
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            MuteCmdString = bytes((0x21, Zone, 8, 2, (0x10, 0x17)[Zone - 1], ValueStateValues[value][Zone - 1], 13))
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            MuteCmdString = bytes((0x21, Zone, 0x0E, 1, 0xF0, 13))
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }
        qualifier = {'Zone': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Mute', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x7B,
            'Off': 0x7C
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            PowerCmdString = bytes((0x21, Zone, 8, 2, (0x10, 0x17)[Zone - 1], ValueStateValues[value], 13))
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            PowerCmdString = bytes((0x21, Zone, 0, 1, 0xF0, 13))
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            b'\x01': 'On',
            b'\x00': 'Off'
        }
        qualifier = {'Zone': str(ord(match.group(1)))}
        value = ValueStateValues[match.group(2)]
        self.WriteStatus('Power', value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Rewind': 0x79,
            'Fast Forward': 0x34,
            'Previous': 0x21,
            'Next': 0x0B,
            'Stop': 0x36,
            'Play': 0x35,
            'Pause': 0x30,
            'Random': 0x4C,
            'Repeat': 0x31
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            TransportCmdString = bytes((0x21, Zone, 8, 2, 0x10, ValueStateValues[value], 0x0D))
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTransport')

    def SetTuneFM(self, value, qualifier):

        ValueStateValues = {
            'Increment': 1,
            'Decrement': 0
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            TuneFMCmdString = bytes((0x21, Zone, 0x16, 1, ValueStateValues[value], 0x0D))
            self.__SetHelper('TuneFM', TuneFMCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTuneFM')

    def UpdateTuneFMStatus(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            TuneFMStatusCmdString = bytes((0x21, Zone, 0x16, 1, 0xF0, 0x0D))
            self.__UpdateHelper('TuneFMStatus', TuneFMStatusCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateTuneFMStatus')

    def __MatchTuneFMStatus(self, match, tag):

        qualifier = {'Zone': str(ord(match.group(1)))}
        value = (ord(match.group(2)) * 100 + ord(match.group(3))) / 100
        self.WriteStatus('TuneFMStatus', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2) and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = bytes((0x21, Zone, 0x0D, 1, value, 13))
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        Zone = int(qualifier['Zone'])
        if Zone in (1, 2):
            VolumeCmdString = bytes((0x21, Zone, 0x0D, 1, 0xF0, 13))
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        qualifier = {'Zone': str(ord(match.group(1)))}
        value = ord(match.group(2))
        self.WriteStatus('Volume', value, qualifier)

    def SetZone1OnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'!\x01\x4E\x01\xF1\x0D',
            'Off': b'!\x01\x4E\x01\xF2\x0D'
        }

        Zone1OnScreenDisplayCmdString = ValueStateValues[value]
        self.__SetHelper('Zone1OnScreenDisplay', Zone1OnScreenDisplayCmdString, value, qualifier)

    def UpdateZone1OnScreenDisplay(self, value, qualifier):

        Zone1OnScreenDisplayCmdString = b'!\x01\x4E\x01\xF0\x0D'
        self.__UpdateHelper('Zone1OnScreenDisplay', Zone1OnScreenDisplayCmdString, value, qualifier)

    def __MatchZone1OnScreenDisplay(self, match, tag):

        ValueStateValues = {
            b'\x00': 'On',
            b'\x01': 'Off'
        }
        value = ValueStateValues[match.group(1)]
        self.WriteStatus('Zone1OnScreenDisplay', value, None)

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

        Commands = {
            b'\x0B': 'Audio Mode',
            b'\x1D': 'Input',
            b'\x0E': 'Mute',
            b'\x00': 'Power',
            b'\x0D': 'Volume',
            b'\x08': 'RC5 IR',
            b'\x4F': 'HDMI Output',
            b'\x16': 'Tune FM',
            b'\x4E': 'Zone 1 On Screen Display'
        }
        Errors = {
            b'\x82': 'Invalid Zone',
            b'\x83': 'Command Not Recognised',
            b'\x84': 'Parameter Not Recognised',
            b'\x85': 'Command Invalid At This Time',
            b'\x86': 'Invalid Data Length'
        }
        print('{}: {}'.format(Commands[match.group(2)], Errors[match.group(3)]))

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
