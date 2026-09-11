from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
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
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'HDCPInputAuthorization': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw([0-2])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'HdcpE([01]) ([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Update')
            self.AddMatchString(re.compile(b'HdcpE([12])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'In([12]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig([01]) ([01])\*([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Sig([01]) ([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt([0-2])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': b'1Z',
            'Off': b'0Z',
        }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On',
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeStateValues = {
            'Off': b'0',
            'Lowest Active Input': b'2',
            'Highest Active Input': b'1'
        }

        AutoSwitchModeCmdString = b'\x1B' + AutoSwitchModeStateValues[value] + b'AUSW\x0D'
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = b'\x1BAUSW\x0D'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeStateNames = {
            '0': 'Off',
            '2': 'Lowest Active Input',
            '1': 'Highest Active Input'
        }

        value = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def __MatchHDCPInputAuthorization(self, match, tag):

        HDCPStateNames = {
            '1': 'On',
            '0': 'Off',
        }

        if tag == 'Update':
            input1 = HDCPStateNames[match.group(1).decode()]
            self.WriteStatus('HDCPInputAuthorization', input1, None)
        elif tag == 'Set':
            value = match.group(1).decode()
            if value == '1':
                self.WriteStatus('HDCPInputAuthorization', HDCPStateNames[match.group(2).decode()], None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        HDCPStateValues = {
            'On': b'1HDCP',
            'Off': b'0HDCP'
        }

        HDCPCmdString = b'\x1BE1*' + HDCPStateValues[value] + b'\x0D'
        self.__SetHelper('HDCPInputAuthorization', HDCPCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPCmdString = b'\x1BEHDCP\x0D'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': b'1!',
            '2': b'2!'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = b'!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        SignalStatusCmdString = b'\x1B0LS\x0D'
        self.__UpdateHelper('InputSignalStatus', SignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        SignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active',
        }

        Input1 = SignalStatusStateNames[match.group(1).decode()]
        Input2 = SignalStatusStateNames[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', Input1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', Input2, {'Input': '2'})

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': b'1B',
            'Off': b'0B',
            'On with Sync': b'2B',
        }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '0': 'Off',
            '1': 'On',
            '2': 'On with Sync'
        }

        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            self.Send('w3cv\r\n')
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

            if self.VerboseDisabled:
                self.Send('w3cv\r\n')
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '06': 'Invalid channel change',
            '10': 'Invalid command',
            '13': 'Invalid parameter',
            '14': 'Not valid for this configuration',
            '17': 'Invalid command for signal type',
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

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

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