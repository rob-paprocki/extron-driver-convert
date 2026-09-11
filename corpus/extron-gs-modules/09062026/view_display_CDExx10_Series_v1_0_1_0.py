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
        self.Models = {
            'CDE5510': self.view_10_3347_5510,
            'CDE6510': self.view_10_3347_6510,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Brightness': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Type'], 'Status': {}},
            'Input': {'Status': {}},
            'IRRemote': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'8[0-9]{2}rg00([01])\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rb(\d{3})\r'), self.__MatchBrightness, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}r([opq])00([01])\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rn00([01])\r'), self.__MatchIRRemote, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rj[01](04|14|24|34|06|05|0A|07|09)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rl00([01])\r'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'8[0-9]{2}rf(\d{3})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'4[0-9]{2}-\r'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '99'
        elif 1 <= int(value) <= 98:
            self._DeviceID = '{0:02d}'.format(int(value))
        else:
            self.Error(['Device ID should be a value between 1 to 98 or Broadcast.'])

    def SetAspectRatio(self, value, qualifier):

        States = {
            'Full (16:9)': '0',
            'Normal (4:3)': '1',
            'Real (1:1)': '2'
        }

        CmdString = '8{0}s100{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AspectRatio', CmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '8{0}s600{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('AudioMute', CmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.__UpdateHelper('AudioMute', '8{0}gg000\r'.format(self._DeviceID), value, qualifier)

    def __MatchAudioMute(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('AudioMute', States[match.group(1).decode()], None)

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '8{0}s${1:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):
        self.__UpdateHelper('Brightness', '8{0}gb000\r'.format(self._DeviceID), value, qualifier)

    def __MatchBrightness(self, match, tag):
        self.WriteStatus('Brightness', int(match.group(1).decode()), None)

    def SetExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Power': '4',
            'Button': '8',
            'Menu': '>',
        }

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '8{0}s{1}00{2}\r'.format(self._DeviceID, TypeStates[qualifier['Type']], States[value])
        self.__SetHelper('ExecutiveMode', CmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        TypeStates = {
            'Power': 'o',
            'Button': 'p',
            'Menu': 'q',
        }

        CmdString = '8{0}g{1}000\r'.format(self._DeviceID, TypeStates[qualifier['Type']])
        self.__UpdateHelper('ExecutiveMode', CmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        TypeStates = {
            'o': 'Power',
            'p': 'Button',
            'q': 'Menu',
        }

        States = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Type': TypeStates[match.group(1).decode()]}
        value = States[match.group(2).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetInput(self, value, qualifier):

        CmdString = '8{0}s\x220{1}\r'.format(self._DeviceID, self.InputValues[value])
        self.__SetHelper('Input', CmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.__UpdateHelper('Input', '8{0}gj000\r'.format(self._DeviceID), value, qualifier)

    def __MatchInput(self, match, tag):

        self.WriteStatus('Input', self.InputNames[match.group(1).decode()], None)

    def SetIRRemote(self, value, qualifier):

        States = {
            'Enable': '001',
            'Disable': '000'
        }

        CmdString = '8{0}sB{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('IRRemote', CmdString, value, qualifier)

    def UpdateIRRemote(self, value, qualifier):
        self.__UpdateHelper('IRRemote', '8{0}gn000\r'.format(self._DeviceID), value, qualifier)

    def __MatchIRRemote(self, match, tag):

        States = {
            '1': 'Enable',
            '0': 'Disable'
        }

        self.WriteStatus('IRRemote', States[match.group(1).decode()], None)

    def SetKeypad(self, value, qualifier):

        States = {
            '0': '000',
            '1': '001',
            '2': '002',
            '3': '003',
            '4': '004',
            '5': '005',
            '6': '006',
            '7': '007',
            '8': '008',
            '9': '009'
        }

        CmdString = '8{0}s@{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Keypad', CmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        States = {
            'Up': '0',
            'Down': '1',
            'Left': '2',
            'Right': '3',
            'Enter': '4',
            'Menu': '6',
            'Exit': '7'
        }

        CmdString = '8{0}sA00{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('MenuNavigation', CmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        States = {
            'On': '1',
            'Off': '0'
        }

        CmdString = '8{0}s!00{1}\r'.format(self._DeviceID, States[value])
        self.__SetHelper('Power', CmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        self.__UpdateHelper('Power', '8{0}gl000\r'.format(self._DeviceID), value, qualifier)

    def __MatchPower(self, match, tag):

        States = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('Power', States[match.group(1).decode()], None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            CmdString = '8{0}s5{1:03d}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):
        self.__UpdateHelper('Volume', '8{0}gf000\r'.format(self._DeviceID), value, qualifier)

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '99':
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
        self.Error(['Device responded with an error message.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def view_10_3347_5510(self):

        self.InputValues = {
            'HDMI 1': '04',
            'HDMI 2': '14',
            'VGA': '06',
            'DVI': '05',
            'Media Player': '0A'
        }
        self.InputNames = {
            '04': 'HDMI 1',
            '14': 'HDMI 2',
            '06': 'VGA',
            '05': 'DVI',
            '0A': 'Media Player'
        }

    def view_10_3347_6510(self):

        self.InputValues = {
            'HDMI 1': '04',
            'HDMI 2': '14',
            'HDMI 3': '24',
            'HDMI 4': '34',
            'VGA': '06',
            'DisplayPort': '09',
            'Media Player': '0A',
            'OPS': '07'
        }
        self.InputNames = {
            '04': 'HDMI 1',
            '14': 'HDMI 2',
            '24': 'HDMI 3',
            '34': 'HDMI 4',
            '06': 'VGA',
            '09': 'DisplayPort',
            '0A': 'Media Player',
            '07': 'OPS'
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
