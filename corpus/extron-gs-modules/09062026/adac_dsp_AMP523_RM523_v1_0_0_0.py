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
        self.Models = {
            'AMP523': self.adac_25_2736_AMP523,
            'RM523': self.adac_25_2736_RM523,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Bass': {'Status': {}},
            'Input': {'Status': {}},
            'MasterVolume': {'Status': {}},
            'Mic_WMIVolume': {'Status': {}},
            'Mute': {'Status': {}},
            'SaveSettings': {'Status': {}},
            'AllStatuses': {'Status': {}},
            'Treble': {'Status': {}},
            'WLIVolume': {'Status': {}}
        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'#F001\|[XR]001\|SA\|([0-9]|[1-7][0-9]|80)\^([0-9]|[1-7][0-9]|80)\^([1-5])\^([0-9]|[1-7][0-9]|80)\^([01])\^([0-9]|1[0-4])\^([0-9]|1[0-4])\|([0-9a-f]{4}|U)\|\r\n'), self.__MatchStatus, None)

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BassCmdString = '#|{}|F001|SB01|{}|U|\r\n'.format(self.Address, (value + 14) // 2).encode()
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBass')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Line 1': '1',
            'Line 2': '2',
            'Line 3': '3',
            'Line 4': '4',
            'WLI-WMI/MIC': '5'
        }
        InputCmdString = '#|{}|F001|SR01|{}|U|\r\n'.format(self.Address, ValueStateValues[value]).encode()
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMasterVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterVolumeCmdString = '#|{}|F001|SV01|{}|U|\r\n'.format(self.Address, abs(value)).encode()
            self.__SetHelper('MasterVolume', MasterVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterVolume')

    def SetMic_WMIVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Mic_WMIVolumeCmdString = '#|{}|F001|SVM|{}|U|\r\n'.format(self.Address, abs(value)).encode()
            self.__SetHelper('Mic_WMIVolume', Mic_WMIVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMic_WMIVolume')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        MuteCmdString = '#|{}|F001|SM01|{}|U|\r\n'.format(self.Address, ValueStateValues[value]).encode()
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetSaveSettings(self, value, qualifier):

        SaveSettingsCmdString = '#|{}|F001|SAVE|0|U|\r\n'.format(self.Address).encode()
        self.__SetHelper('SaveSettings', SaveSettingsCmdString, value, qualifier)

    def UpdateAllStatuses(self, value, qualifier):

        StatusCmdString = '#|{}|F001|GSA|0|U|\r\n'.format(self.Address).encode()
        self.__UpdateHelper('AllStatuses', StatusCmdString, value, qualifier)

    def __MatchStatus(self, match, tag):

        InputNames = {
            b'1': 'Line 1',
            b'2': 'Line 2',
            b'3': 'Line 3',
            b'4': 'Line 4',
            b'5': 'WLI-WMI/MIC'
        }
        MuteNames = {
            b'0': 'Off',
            b'1': 'On'
        }
        self.WriteStatus('WLIVolume', -int(match.group(1)), None)
        self.WriteStatus('Mic_WMIVolume', -int(match.group(2)), None)
        self.WriteStatus('Input', InputNames[match.group(3)], None)
        self.WriteStatus('MasterVolume', -int(match.group(4)), None)
        self.WriteStatus('Mute', MuteNames[match.group(5)], None)
        self.WriteStatus('Bass', int(match.group(6)) * 2 - 14, None)
        self.WriteStatus('Treble', int(match.group(7)) * 2 - 14, None)

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            TrebleCmdString = '#|{}|F001|ST01|{}|U|\r\n'.format(self.Address, (value + 14) // 2).encode()
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTreble')

    def SetWLIVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -80,
            'Max': 0
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            WLIVolumeCmdString = '#|{}|F001|SVL|{}|U|\r\n'.format(self.Address, abs(value)).encode()
            self.__SetHelper('WLIVolume', WLIVolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetWLIVolume')

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

    def adac_25_2736_RM523(self):
        self.Address = 'R001'

    def adac_25_2736_AMP523(self):
        self.Address = 'X001'

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
