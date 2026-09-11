from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from binascii import hexlify

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
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Parameters': ['Window'], 'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPSize': {'Status': {}},
            'PIPSwap': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x8c\?([0|1|9|A|F])'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x80m\?([0|1])'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\xee\x62\?([0|1])'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\x98\?([\x41|\x46|\x48|\x50][\x31-\x33])'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\xee\x71\x30\?([0-5])'), self.__MatchPictureMode, None)
            self.AddMatchString(re.compile(b'\xa7(c|d)?\?([\x41|\x46|\x48|\x50][\x31-\x33])'), self.__MatchPIPInput, None)
            self.AddMatchString(re.compile(b'\x9a\?([0-4])'), self.__MatchPIPMode, None)
            self.AddMatchString(re.compile(b'\xa6\?([\x00-\x0A])'), self.__MatchPIPSize, None)
            self.AddMatchString(re.compile(b'\xc8\?([0|1])'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'\x80a\?(\d\d)'), self.__MatchVolume, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': b'\x8C0',
            'Fill Screen': b'\x8C1',
            '4:3': b'\x8C9',
            '16:9': b'\x8CA',
            '5:4': b'\x8CF'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x8c?'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '0': '1:1',
            '1': 'Fill Screen',
            '9': '4:3',
            'A': '16:9',
            'F': '5:4'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x80m0',
            'Off': b'\x80m1'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x80m?'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xee\x621',
            'Off': b'\xee\x620'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = b'\xee\x62?'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x98\x41\x31',
            'DisplayPort': b'\x98\x50\x31',
            'HDMI 1': b'\x98\x48\x31',
            'HDMI 2': b'\x98\x48\x32',
            'HDMI 3': b'\x98\x48\x33',
            'DVI': b'\x98\x46\x31'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x98?'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x41\x31': 'VGA',
            '\x50\x31': 'DisplayPort',
            '\x48\x31': 'HDMI 1',
            '\x48\x32': 'HDMI 2',
            '\x48\x33': 'HDMI 3',
            '\x46\x31': 'DVI'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xfb',
            'Down': b'\xfa',
            'Left': b'\xfd',
            'Right': b'\xfc',
            'Menu': b'\xf7'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\xee\x71\x300',
            'Game': b'\xee\x71\x301',
            'Movie': b'\xee\x71\x302',
            'Photo': b'\xee\x71\x303',
            'Vivid': b'\xee\x71\x304',
            'User': b'\xee\x71\x305'
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def UpdatePictureMode(self, value, qualifier):

        PictureModeCmdString = b'\xee\x71\x30?'
        self.__UpdateHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def __MatchPictureMode(self, match, tag):

        ValueStateValues = {
            '0': 'Standard',
            '1': 'Game',
            '2': 'Movie',
            '3': 'Photo',
            '4': 'Vivid',
            '5': 'User'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PictureMode', value, None)

    def SetPIPInput(self, value, qualifier):

        SelectStates = {
            'PIP / PBP Right / PBP Bottom / 4P Lower Left': b'',
            '4P Upper Right': b'c',
            '4P Lower Right': b'd'
        }

        ValueStateValues = {
            'VGA': b'\x41\x31',
            'DisplayPort': b'\x50\x31',
            'HDMI 1': b'\x48\x31',
            'HDMI 2': b'\x48\x32',
            'HDMI 3': b'\x48\x33',
            'DVI': b'\x46\x31'
        }

        PIPInputCmdString = b'\xa7' + SelectStates[qualifier['Window']] + ValueStateValues[value]
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def UpdatePIPInput(self, value, qualifier):

        SelectStates = {
            'PIP / PBP Right / PBP Bottom / 4P Lower Left': b'',
            '4P Upper Right': b'c',
            '4P Lower Right': b'd'
        }

        PIPInputCmdString = b'\xa7' + SelectStates[qualifier['Window']] + b'?'
        self.__UpdateHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def __MatchPIPInput(self, match, tag):

        SelectStates = {
            'c': '4P Upper Right',
            'd': '4P Lower Right'
        }

        ValueStateValues = {
            '\x41\x31': 'VGA',
            '\x50\x31': 'DisplayPort',
            '\x48\x31': 'HDMI 1',
            '\x48\x32': 'HDMI 2',
            '\x48\x33': 'HDMI 3',
            '\x46\x31': 'DVI'
        }
        if match.group(1):
            value = ValueStateValues[match.group(2).decode()]
            qualifier = {'Window': SelectStates[match.group(1).decode()]}
            self.WriteStatus('PIPInput', value, qualifier)
        else:
            value = ValueStateValues[match.group(2).decode()]
            qualifier = {'Window': 'PIP / PBP Right / PBP Bottom / 4P Lower Left'}
            self.WriteStatus('PIPInput', value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'Off': b'0',
            'Picture In Picture': b'1',
            'Picture By Picture (Left Right)': b'2',
            'Picture By Picture (Top Bottom)': b'3',
            '4 Pictures': b'4'
        }

        PIPModeCmdString = b'\x9a{0}' + ValueStateValues[value]
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def UpdatePIPMode(self, value, qualifier):

        PIPModeCmdString = b'\x9a?'
        self.__UpdateHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def __MatchPIPMode(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Picture In Picture',
            '2': 'Picture By Picture (Left Right)',
            '3': 'Picture By Picture (Top Bottom)',
            '4': '4 Pictures'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPMode', value, None)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xa6\x00',
            '1': b'\xa6\x01',
            '2': b'\xa6\x02',
            '3': b'\xa6\x03',
            '4': b'\xa6\x04',
            '5': b'\xa6\x05',
            '6': b'\xa6\x06',
            '7': b'\xa6\x07',
            '8': b'\xa6\x08',
            '9': b'\xa6\x09',
            '10': b'\xa6\x0A'
        }

        PIPSizeCmdString = ValueStateValues[value]
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def UpdatePIPSize(self, value, qualifier):

        PIPSizeCmdString = b'\xa6?'
        self.__UpdateHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def __MatchPIPSize(self, match, tag):

        ValueStateValues = {
            '\x00': '0',
            '\x01': '1',
            '\x02': '2',
            '\x03': '3',
            '\x04': '4',
            '\x05': '5',
            '\x06': '6',
            '\x07': '7',
            '\x08': '8',
            '\x09': '9',
            '\x0A': '10'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('PIPSize', value, None)

    def SetPIPSwap(self, value, qualifier):

        PIPSwapCmdString = b'\xe3'
        self.__SetHelper('PIPSwap', PIPSwapCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xc81',
            'Off': b'\xc80'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = b'\xc8?'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:

            result = hexlify(value.to_bytes(1, 'big')).upper()
            VolumeCmdString = b'\x80a' + result
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = b'\x80a?'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode(), 16)
        self.WriteStatus('Volume', value, None)

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
