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
            'DTP T UWP 232 D': self.extr_2_708_UWP,
            'DTP T HWP 232 D': self.extr_2_708_HWP,
            'DTP T HWP 332 D': self.extr_2_708_HWP,
            'DTP T UWP 332 D': self.extr_2_708_UWP,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'HDCPInputAuthorizationHWP': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputAuthorizationUWP': {'Status': {}},
            'Input': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw([01])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'HdcpE([01]) ([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Update')
            self.AddMatchString(re.compile(b'HdcpE([12])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'In([12]) All\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig([01]) ([01])\*([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)


#########################################################################
    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': b'1Z',
            'Off': b'0Z'
        }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = '\x1BAUSW\x0D'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = AutoSwitchModeStateNames[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetHDCPInputAuthorizationHWP(self, value, qualifier):

        Input = qualifier['Input']
        InputNames = {
            '1': '1*',
            '2': '2*'
        }

        HDCPStateValues = {
            'On': '1HDCP',
            'Off': '0HDCP'
        }

        HDCPCmdString = '\x1BE{0}{1}\x0D'.format(InputNames[Input], HDCPStateValues[value])
        self.__SetHelper('HDCPInputAuthorizationHWP', HDCPCmdString, value, qualifier)

    def UpdateHDCPInputAuthorizationHWP(self, value, qualifier):

        HDCPCmdString = b'\x1BEHDCP\x0D'
        self.__UpdateHelper('HDCPInputAuthorizationHWP', HDCPCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):
    
        HDCPStateNames = {
            '1': 'On',
            '0': 'Off'
        }

        if self._Input == "VGA":
            if tag == 'Update':
                input1 = HDCPStateNames[match.group(1).decode()]
                self.WriteStatus('HDCPInputAuthorizationUWP', input1, None)
            elif tag == 'Set':
                value = match.group(1).decode()
                if value == '1':
                    self.WriteStatus('HDCPInputAuthorizationUWP', HDCPStateNames[match.group(2).decode()], None)

        elif self._Input == "HDMI":
            if tag == 'Update':
                input1 = HDCPStateNames[match.group(1).decode()]
                input2 = HDCPStateNames[match.group(2).decode()]
                self.WriteStatus('HDCPInputAuthorizationHWP', input1, {'Input': '1'})
                self.WriteStatus('HDCPInputAuthorizationHWP', input2, {'Input': '2'})
            elif tag == 'Set':
                self.WriteStatus('HDCPInputAuthorizationHWP', HDCPStateNames[match.group(2).decode()], {'Input': match.group(1).decode()})

    def SetHDCPInputAuthorizationUWP(self, value, qualifier):

        HDCPStateValues = {
            'On': '1HDCP',
            'Off': '0HDCP'
        }

        HDCPHDMICmdString = '\x1BE1*{0}\x0D'.format(HDCPStateValues[value])
        self.__SetHelper('HDCPInputAuthorizationUWP', HDCPHDMICmdString, value, qualifier)

    def UpdateHDCPInputAuthorizationUWP(self, value, qualifier):

        HDCPHDMICmdString = b'\x1BEHDCP\x0D'
        self.__UpdateHelper('HDCPInputAuthorizationUWP', HDCPHDMICmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1!',
            '2': '2!'
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

        InputSignalStatusCmdString = '\x1B0LS\x0D'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active'
        }

        Input1 = InputSignalStatusStateNames[match.group(1).decode()]
        Input2 = InputSignalStatusStateNames[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', Input1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', Input2, {'Input': '2'})

    def SetVideoMute(self, value, qualifier):

        VideoMuteStateValues = {
            'On': b'1B',
            'Off': b'0B'
        }

        VideoMuteCmdString = VideoMuteStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        value = VideoMuteStateNames[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
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
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number(out of range)',
            '06': 'Invalid channel change',
            '10': 'Invalid command',
            '13': 'Invalid parameter',
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

    def extr_2_708_UWP(self):

        self._Input = "VGA"

    def extr_2_708_HWP(self):

        self._Input = "HDMI"

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