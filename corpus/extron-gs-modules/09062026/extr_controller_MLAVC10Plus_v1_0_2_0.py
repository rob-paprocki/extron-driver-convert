from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search

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
            'AudioMute': {'Status': {}},
            'Relay': {'Status': {}},
            'RelayPulse': {'Status': {}},
            'SoftStart': {'Status': {}},
            'Volume': {'Status': {}},
            'VolumeStep': {'Status': {}}
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt([0-1])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Rly1\*([0-1])\r\n'), self.__MatchRelay, None)
            self.AddMatchString(compile(b'Vlcm S([0-1]) \r\n'), self.__MatchSoftStart, None)
            self.AddMatchString(compile(b'Vol([0-9]{3})\r\n'), self.__MatchVolume, None)

            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        AudioMuteCmdString = '{0}Z'.format(AudioMuteState[value])

        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteName = {
            '0': 'Off',
            '1': 'On'
        }
        value = match.group(1).decode()
        self.WriteStatus('AudioMute', AudioMuteName[value], None)

    def SetRelay(self, value, qualifier):

        RelayName = {
            'Open': '0',
            'Close': '1',
        }
        RelayCmdString = '1*{0}O'.format(RelayName[value])
        self.__SetHelper('Relay', RelayCmdString, value, qualifier)

    def UpdateRelay(self, value, qualifier):

        RelayCmdString = '1O'
        self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)

    def __MatchRelay(self, match, tag):

        RelayName = {
            '0': 'Open',
            '1': 'Close'
        }
        value = match.group(1).decode()
        self.WriteStatus('Relay', RelayName[value], None)

    def SetRelayPulse(self, value, qualifier):

        RelayPulseConstraints = {
            'Min': 0.24,
            'Max': 1310.7
        }
        if value < RelayPulseConstraints['Min'] or value > RelayPulseConstraints['Max']:
            self.Discard('Invalid Command for SetRelayPulse')
        else:
            RelayPulseTime = int(value / 0.02)
            RelayPulseCmdString = '1*3*{0}O'.format(RelayPulseTime)
            self.__SetHelper('RelayPulse', RelayPulseCmdString, value, qualifier)

    def SetSoftStart(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        SoftStartCmdString = 'wS*{0}VLCM\r'.format(ValueStateValues[value])
        self.__SetHelper('SoftStart', SoftStartCmdString, value, qualifier)

    def UpdateSoftStart(self, value, qualifier):

        SoftStartCmdString = 'wSVLCM\r'
        self.__UpdateHelper('SoftStart', SoftStartCmdString, value, qualifier)

    def __MatchSoftStart(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]

        self.WriteStatus('SoftStart', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }
        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            self.Discard('Invalid Command for SetVolume')
        else:
            self.__SetHelper('Volume', '{0}V'.format(value), value, qualifier)

    def UpdateVolume(self, value, qualifier):

        self.__UpdateHelper('Volume', 'V', value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1))

        self.WriteStatus('Volume', value, None)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': '+V',
            'Down': '-V'
        }

        VolumeStepCmdString = ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        if self.initializationChk:
            self.initializationChk = False
            self.OnConnected()
            
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.initializationChk = False
                self.OnConnected()

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            self.Send(commandstring)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '22': 'Busy',
            '24': 'Privilege violation',
            '25': 'Device not present',
            '26': 'Maximum number of connections exceeded',
            '27': 'Invalid event number',
            '28': 'Bad filename or file not found',
            '30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            '31': 'Attempt to break port pass-through when it has not been set',
            '32': 'Incorrect V-chip password'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.UpdateSoftStart(None, None)

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
                result = search(regexString, self._ReceiveBuffer)
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
