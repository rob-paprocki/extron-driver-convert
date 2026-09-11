from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import re
from extronlib.system import Wait, ProgramLog
import time


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
            'AutoImage': {'Status': {}},
            'ButtonandIRControl': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStatus': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\x38\x30\x31\x72\x77\x30\x30(\x30|\x31|\x32|\x33|\x34)\x0D'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'\x38\x30\x31\x72\x67\x30\x30(\x30|\x31)\x0D'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'\x38\x30\x31\x72\x69\x30\x30(\x30|\x31)\x0D'), self.__MatchButtonandIRControl, None)
            self.AddMatchString(re.compile(b'\x38\x30\x31\x72\x6A([\x30|\x31][\x30|\x32][\x30-\x34])\x0D'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\x38\x30\x31\x72\x66([0-9]{3})\x0D'), self.__MatchVolumeStatus, None)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Full': b'\x38\x30\x31\x73\x31\x30\x30\x30\x0D',
            '4:3': b'\x38\x30\x31\x73\x31\x30\x30\x31\x0D',
            'Film': b'\x38\x30\x31\x73\x31\x30\x30\x32\x0D',
            'Subtitle': b'\x38\x30\x31\x73\x31\x30\x30\x33\x0D',
            'PC Mode': b'\x38\x30\x31\x73\x31\x30\x30\x34\x0D'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x38\x30\x31\x67\x77\x30\x30\x30\x0D'
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            '\x30': 'Full',
            '\x31': '4:3',
            '\x32': 'Film',
            '\x33': 'Subtitle',
            '\x34': 'PC Mode'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AspectRatio', value, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x38\x30\x31\x73\x36\x30\x30\x30\x0D'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x38\x30\x31\x67\x67\x30\x30\x30\x0D'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '\x31': 'On',
            '\x30': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x38\x30\x31\x73\x8F\x30\x30\x30\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetButtonandIRControl(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x38\x30\x31\x73\x43\x30\x30\x31\x0D',
            'Disable': b'\x38\x30\x31\x73\x43\x30\x30\x30\x0D'
        }

        ButtonandIRControlCmdString = ValueStateValues[value]
        self.__SetHelper('ButtonandIRControl', ButtonandIRControlCmdString, value, qualifier)

    def UpdateButtonandIRControl(self, value, qualifier):

        ButtonandIRControlCmdString = b'\x38\x30\x31\x67\x69\x30\x30\x30\x0D'
        self.__UpdateHelper('ButtonandIRControl', ButtonandIRControlCmdString, value, qualifier)

    def __MatchButtonandIRControl(self, match, tag):

        ValueStateValues = {
            '\x31': 'Enable',
            '\x30': 'Disable'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ButtonandIRControl', value, None)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x38\x30\x31\x73\x21\x30\x30\x33\x0D'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x38\x30\x31\x73\x22\x30\x30\x30\x0D',
            'HDMI 1': b'\x38\x30\x31\x73\x22\x30\x30\x31\x0D',
            'HDMI 2': b'\x38\x30\x31\x73\x22\x30\x30\x32\x0D',
            'HDMI 3': b'\x38\x30\x31\x73\x22\x30\x32\x31\x0D',
            'AV': b'\x38\x30\x31\x73\x22\x30\x30\x33\x0D',
            'YPbPr': b'\x38\x30\x31\x73\x22\x30\x30\x34\x0D',
            'Android': b'\x38\x30\x31\x73\x22\x31\x30\x31\x0D'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'\x38\x30\x31\x67\x6A\x30\x30\x30\x0D'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '\x30\x30\x30': 'VGA',
            '\x30\x30\x31': 'HDMI 1',
            '\x30\x30\x32': 'HDMI 2',
            '\x30\x32\x31': 'HDMI 3',
            '\x30\x30\x33': 'AV',
            '\x30\x30\x34': 'YPbPr',
            '\x31\x30\x31': 'Android'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x38\x30\x31\x73\x21\x30\x30\x31\x0D',
            'Off': b'\x38\x30\x31\x73\x21\x30\x30\x30\x0D'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x38\x30\x31\x73\x35\x33\x30\x30\r',
            'Down': b'\x38\x30\x31\x73\x35\x32\x30\x30\r'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolumeStatus(self, value, qualifier):

        VolumeStatusCmdString = b'\x38\x30\x31\x67\x66\x30\x30\x30\x0D'
        self.__UpdateHelper('VolumeStatus', VolumeStatusCmdString, value, qualifier)

    def __MatchVolumeStatus(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('VolumeStatus', value, None)

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
