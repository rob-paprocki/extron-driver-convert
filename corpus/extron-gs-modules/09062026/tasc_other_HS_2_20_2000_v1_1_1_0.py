from extronlib.interface import EthernetClientInterface, SerialInterface
import re
from extronlib.system import ProgramLog

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FlashStart': {'Status': {}},
            'Input': {'Status': {}},
            'PlayerTime': {'Status': {}},
            'RecorderTime': {'Status': {}},
            'Repeat': {'Status': {}},
            'TrackNumber': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\n[0-1]D0(00|01|10|11|12|80|81|82|83|FF)\r'), self.__MatchDeviceStatus, None)
            self.AddMatchString(re.compile(b'\n[0-1]CC0(0|1)\r'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'\n[0-1]FF010(0|1)\r'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'\n[0-1]DD[0-9]{4}([0-9]{4}).*?\r'), self.__MatchPlayerTime, None)
            self.AddMatchString(re.compile(b'\n[0-1]13([0-9]{4}).*?\r'), self.__MatchRecorderTime, None)
            self.AddMatchString(re.compile(b'\n[0-1]B70(0|1)\r'), self.__MatchRepeat, None)
            self.AddMatchString(re.compile(b'\n[0-1]D5(00|01)([0-9]{4})\r'), self.__MatchTrackNumber, None)
            self.AddMatchString(re.compile(b'\n[0-1]AF([0-9]{4})\r'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Enter Password'), self.__MatchPassword, None)

    def __MatchPassword(self, match, tag):
        self.SetPassword(None, None)

    def SetPassword(self):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def UpdateDeviceStatus(self, value, qualifier):

        DeviceStatusCmdString = '\n050\r'
        self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)

    def __MatchDeviceStatus(self, match, tag):

        ValueStateValues = {
            '00': 'No Media Inserted',
            '10': 'Stopped',
            '11': 'Playing',
            '12': 'Ready On',
            '81': 'Record',
            '82': 'Record Ready',
            '83': 'Information Writing',
            'FF': 'Other'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('DeviceStatus', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Only Remote': '\n04C00\r',
            'Remote and Front Key': '\n04C01\r'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = '\n04CFF\r'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ValueStateValues = {
            '0': 'Only Remote',
            '1': 'Remote and Front Key'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetFlashStart(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 999
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            val = str(value).zfill(4)
            FlashStartCmdString = ''.join(['\n019', val[2], val[3], val[0], val[1], '\r'])
            self.__SetHelper('FlashStart', FlashStartCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFlashStart')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Slot 1': '\n07F0100\r',
            'Slot 2': '\n07F0101\r'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '\n07F01FF\r'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            '0': 'Slot 1',
            '1': 'Slot 2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, None)

    def UpdatePlayerTime(self, value, qualifier):

        PlayerTimeCmdString = '\n05D\r'
        self.__UpdateHelper('PlayerTime', PlayerTimeCmdString, value, qualifier)

    def __MatchPlayerTime(self, match, tag):

        temp = match.group(1).decode()
        value = ''.join([temp[0], temp[1], '.', temp[2], temp[3]])
        self.WriteStatus('PlayerTime', value, None)

    def UpdateRecorderTime(self, value, qualifier):

        RecorderTimeCmdString = '\n05813\r'
        self.__UpdateHelper('RecorderTime', RecorderTimeCmdString, value, qualifier)

    def __MatchRecorderTime(self, match, tag):

        temp = match.group(1).decode()
        value = ''.join([temp[0], temp[1], '.', temp[2], temp[3]])
        self.WriteStatus('RecorderTime', value, None)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'On': '\n03701\r',
            'Off': '\n03700\r'
        }

        RepeatCmdString = ValueStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)

    def UpdateRepeat(self, value, qualifier):

        RepeatCmdString = '\n037FF\r'
        self.__UpdateHelper('Repeat', RepeatCmdString, value, qualifier)

    def __MatchRepeat(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Repeat', value, None)

    def UpdateTrackNumber(self, value, qualifier):

        TrackNumberCmdString = b'\n055\r'
        self.__UpdateHelper('TrackNumber', TrackNumberCmdString, value, qualifier)

    def __MatchTrackNumber(self, match, tag):

        temp = match.group(2).decode()
        value = ''.join([temp[2], temp[3], temp[0], temp[1]])
        self.WriteStatus('TrackNumber', int(value), None)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '\n012\r',
            'Stop': '\n010\r',
            'Start Record': '\n01300\r',
            'Pause Record': '\n01301\r',
            'Over Write Record': '\n01320\r',
            'Pause': '\n01401\r',
            'Fast Search Forward': '\n01610\r',
            'Fast Search Backward': '\n01611\r',
            'Search Forward': '\n01600\r',
            'Search Backward': '\n01601\r',
            'Track Skip Next': '\n01A00\r',
            'Track Skip Previous': '\n01A01\r',
            'Mark Skip Next': '\n01A10\r',
            'Mark Skip Previous': '\n01A11\r',
            'Call': '\n01D\r'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -99.9,
            'Max': 99.9
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            t = '{0:.1f}'.format(abs(value))
            t1 = t.zfill(4)
            if value >= 0.0:
                temp = ''.join([t1[-3], t1[-1], '0', t1[-4]])
            elif value < 0.0:
                temp = ''.join([t1[-3], t1[-1], '1', t1[-4]])

            if temp:
                VolumeCmdString = '\n02F{0}\r'.format(temp)
                self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
            else:
                print('Invalid Command for SetVolume')
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = '\n02FFF\r'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        temp = match.group(1).decode()
        if temp[2] == '1':
            t = '-'
        else:
            t = ''
        value = ''.join([t, temp[3], temp[0], '.', temp[1]])
        self.WriteStatus('Volume', float(value), None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

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
