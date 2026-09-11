from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from collections import OrderedDict


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = OrderedDict()
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
            'HDCPInputStatus': {'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'HDMIOutputAudioMute': {'Status': {}},
            'HorizontalStart': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'OutputColorBitDepthMode': {'Status': {}},
            'PixelPhase': {'Status': {}},
            'VerticalStart': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.VerboseDisabled = False

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Ausw([012])\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'HdcpE([10])( 0)?\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI([012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Afmt([01])\r\n'), self.__MatchHDMIOutputAudioMute, None)
            self.AddMatchString(re.compile(b'Hsrt2\*([0-9]{1,3})\r\n'), self.__MatchHorizontalStart, None)
            self.AddMatchString(re.compile(b'In([012]) (All|Aud|Vid)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig([01]) ([01])(.*)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'BitdV([01])\r\n'), self.__MatchOutputColorBitDepthMode, None)
            self.AddMatchString(re.compile(b'Phas2\*([0-9]{1,2})\r\n'), self.__MatchPixelPhase, None)
            self.AddMatchString(re.compile(b'Vsrt2\*([0-9]{1,3})\r\n'), self.__MatchVerticalStart, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = True

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeState = {
            'Off': 'w0AUSW\r',
            'Highest Active Input': 'W1AUSw\r',
            'Lowest Active Input': 'w2AUSW\r'
        }

        AutoSwitchModeCmdString = AutoSwitchModeState[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = 'wAUSW\r'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeState = {
            '0': 'Off',
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input'
        }

        value = AutoSwitchModeState[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': 'wE1HDCP\r',
            'Off': 'wE0HDCP\r'
        }

        HDCPInputAuthorizationCmdString = ValueStateValues[value]
        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def UpdateHDCPInputStatus(self, value, qualifier):

        HDCPInputStatusCmdString = 'wI1HDCP\r'
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Source',
            '1': 'HDCP Compliant Source',
            '2': 'Non-HDCP Compliant Source'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputStatus', value, None)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = 'wOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'No Sink',
            '1': 'HDCP Compliant Sink',
            '2': 'Non-HDCP Compliant Sink'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetHDMIOutputAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'w1AFMT\r',
            'Off': 'w0AFMT\r'
        }

        HDMIOutputAudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('HDMIOutputAudioMute', HDMIOutputAudioMuteCmdString, value, qualifier)

    def UpdateHDMIOutputAudioMute(self, value, qualifier):

        HDMIOutputAudioMuteCmdString = 'wAFMT\r'
        self.__UpdateHelper('HDMIOutputAudioMute', HDMIOutputAudioMuteCmdString, value, qualifier)

    def __MatchHDMIOutputAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIOutputAudioMute', value, None)

    def SetHorizontalStart(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            HorizontalStartCmdString = 'w2*{}HSRT\r'.format(value)
            self.__SetHelper('HorizontalStart', HorizontalStartCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHorizontalStart')

    def UpdateHorizontalStart(self, value, qualifier):

        HorizontalStartCmdString = 'w2HSRT\r'
        self.__UpdateHelper('HorizontalStart', HorizontalStartCmdString, value, qualifier)

    def __MatchHorizontalStart(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('HorizontalStart', value, None)

    def SetInput(self, value, qualifier):

        TypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
        }

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2'
        }

        mode = TypeStates[qualifier['Type']]
        InputCmdString = '{0}{1}'.format(ValueStateValues[value], mode)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        TypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
        }

        mode = TypeStates[qualifier['Type']]
        InputCmdString = mode
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        TypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }

        ValueStateValues = {
            '0': '0',
            '1': '1',
            '2': '2'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Input', value, {'Type': TypeStates[match.group(2).decode()]})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(1).decode()], {'Input': '1'})
        self.WriteStatus('InputSignalStatus', ValueStateValues[match.group(2).decode()], {'Input': '2'})

    def SetOutputColorBitDepthMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'wV0BITD\r',
            '8-Bit': 'wV1BITD\r'
        }

        OutputColorBitDepthModeCmdString = ValueStateValues[value]
        self.__SetHelper('OutputColorBitDepthMode', OutputColorBitDepthModeCmdString, value, qualifier)

    def UpdateOutputColorBitDepthMode(self, value, qualifier):

        OutputColorBitDepthModeCmdString = 'wVBITD\r'
        self.__UpdateHelper('OutputColorBitDepthMode', OutputColorBitDepthModeCmdString, value, qualifier)

    def __MatchOutputColorBitDepthMode(self, match, tag):

        ValueStateValues = {
            '0': 'Auto',
            '1': '8-Bit'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('OutputColorBitDepthMode', value, None)

    def SetPixelPhase(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 63
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PixelPhaseCmdString = 'w2*{}PHAS\r'.format(value)
            self.__SetHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPixelPhase')

    def UpdatePixelPhase(self, value, qualifier):

        PixelPhaseCmdString = 'w2PHAS\r'
        self.__UpdateHelper('PixelPhase', PixelPhaseCmdString, value, qualifier)

    def __MatchPixelPhase(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('PixelPhase', value, None)

    def SetVerticalStart(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VerticalStartCmdString = 'w2*{}VSRT\r'.format(value)
            self.__SetHelper('VerticalStart', VerticalStartCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVerticalStart')

    def UpdateVerticalStart(self, value, qualifier):

        VerticalStartCmdString = 'w2VSRT\r'
        self.__UpdateHelper('VerticalStart', VerticalStartCmdString, value, qualifier)

    def __MatchVerticalStart(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('VerticalStart', value, None)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '1B',
            'Off': '0B'
        }

        VideoMuteCmdString = VideoMuteState[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        VideoMuteCmdString = 'B'
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, tag):

        VideoMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        value = VideoMuteState[match.group(1).decode()]
        self.WriteStatus('VideoMute', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.VerboseDisabled:
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
        print(match.group(0).decode())
        ERROR_CODES = {
            '01': 'Invalid input number',
            '06': 'Invalid switch attempt in this mode',
            '10': 'Invalid command',
            '13': 'Invalid parameter',
            '14': 'Error'
        }

        value = ERROR_CODES[match.group(1).decode()]
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = False

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
