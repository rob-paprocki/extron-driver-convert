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
        self.DeviceID = '1'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoConfigure': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'OSD': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteLock': {'Status': {}},
            'Volume': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'c [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchAspectRatio, None)
            self.AddMatchString(re.compile(b'b [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'l [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchOSD, None)
            self.AddMatchString(re.compile(b'a [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'm [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchRemoteLock, None)
            self.AddMatchString(re.compile(b'd [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'f [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'e [0-9A-F]{1,2} OK([0-9]{1,2})x'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'(.) ([0-9A-F]{1,2}) NG(.*)x'), self.__MatchError, None)

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        elif 1 <= int(value) <= 99:
            self._DeviceID = int(value)


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal Screen (4:3)': '01',
            'Wide Screen (16:9)': '02',
            'Zoom 1': '04',
            'Zoom 2': '05',
            'Original': '06',
            '14:9': '07',
            'Just Scan': '09',
            '1:1': '09',
        }
        AspectRatioCmdString = 'kc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])

        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        AspectRatioCmdString = 'kc {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def __MatchAspectRatio(self, match, tag):

        ValueStateValues = {
            1: 'Normal Screen (4:3)',
            2: 'Wide Screen (16:9)',
            4: 'Zoom 1',
            5: 'Zoom 2',
            6: 'Original',
            7: '14:9',
        }

        inputValue = self.ReadStatus('Input', None)
        aspectValue = int(match.group(1).decode())

        if aspectValue == 9 and '(PC)' in inputValue:
            self.WriteStatus('AspectRatio', '1:1', None)
        elif aspectValue == 9 and '(DTV)' in inputValue:
            self.WriteStatus('AspectRatio', 'Just Scan', None)
        else:
            if 1 <= aspectValue <= 7:
                value = ValueStateValues[aspectValue]
                self.WriteStatus('AspectRatio', value, None)
            else:
                self.Discard('Inappropriate Command')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01'
        }

        AudioMuteCmdString = 'ke {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'ke {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            0: 'On',
            1: 'Off'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoConfigure(self, value, qualifier):

        AutoConfigureCmdString = 'ju {0:02X} 01\r'.format(self._DeviceID)
        self.__SetHelper('AutoConfigure', AutoConfigureCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': '02',
            'Component 1': '04',
            'Component 2': '05',
            'RGB (PC)': '07',
            'HDMI (DTV)': '08',
            'HDMI (PC)': '09',
        }

        InputCmdString = 'kb {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'kb {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            2: 'AV',
            4: 'Component 1',
            5: 'Component 2',
            7: 'RGB (PC)',
            8: 'HDMI (DTV)',
            9: 'HDMI (PC)'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('Input', value, None)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': '10',
            '1': '11',
            '2': '12',
            '3': '13',
            '4': '14',
            '5': '15',
            '6': '16',
            '7': '17',
            '8': '18',
            '9': '19'
        }

        KeypadCmdString = 'mc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '00',
            'Down': '01',
            'Left': '03',
            'Right': '02',
            'Menu': '43',
            'Exit': '5B',
            'Set': '44'
        }

        MenuNavigationCmdString = 'mc {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetOSD(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        OSDCmdString = 'kl {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('OSD', OSDCmdString, value, qualifier)

    def UpdateOSD(self, value, qualifier):

        OSDCmdString = 'kl {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('OSD', OSDCmdString, value, qualifier)

    def __MatchOSD(self, match, tag):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('OSD', value, None)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        PowerCmdString = 'ka {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'ka {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('Power', value, None)

    def SetRemoteLock(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        RemoteLockCmdString = 'km {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def UpdateRemoteLock(self, value, qualifier):

        RemoteLockCmdString = 'km {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('RemoteLock', RemoteLockCmdString, value, qualifier)

    def __MatchRemoteLock(self, match, tag):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('RemoteLock', value, None)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'kf {0:02X} {1:02X}\r'.format(self._DeviceID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'kf {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1), 16)
        self.WriteStatus('Volume', value, None)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00'
        }

        VideoMuteCmdString = 'kd {0:02X} {1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = 'kd {0:02X} FF\r'.format(self._DeviceID)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        value = ValueStateValues[int(match.group(1).decode())]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 0:
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

        errorCommand = {
            'c': 'Aspect Ratio',
            'b': 'Input',
            'l': 'OSD',
            'a': 'Power',
            'm': 'Remote Lock',
            'd': 'Screen Mute',
            'f': 'Volume',
            'e': 'Volume Mute',
        }

        tempError = errorCommand.get(match.group(1).decode(), 'Unknown Command')
        value = 'DeviceID: {0}, Command: {1}, Error: {2}'.format(match.group(2).decode(), tempError, match.group(3).decode())
        print(value)

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
