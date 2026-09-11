from extronlib.system import Wait, ProgramLog
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
        self.__maxBufferSize = 2048
        self.__receiveBuffer = b''
        self.__matchStringDict = {}

        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False

        self.VerboseDisabled = True

        self.Models = {
            'DA2 HD 4K PLUS': self.extr_18_3247_DA_2,
            'DA4 HD 4K PLUS': self.extr_18_3247_DA_4,
            'DA6 HD 4K PLUS': self.extr_18_3247_DA_6,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'HDCPInputAuthorization': {'Status': {}},
            'HDCPInputStatus': {'Status': {}},
            'HDCPOutputStatus': {'Parameters': ['Output'], 'Status': {}},
            'InputSignalStatus': {'Status': {}},
            'OutputFormat': {'Parameters': ['Output'], 'Status': {}},
            'OutputSignalStatus': {'Parameters': ['Output'], 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt([01])\r\n'), self.MatchGlobalAudioMute, None)
            self.AddMatchString(compile(b'Amt([1-6])\*([01])\r\n'), self.MatchAudioMute, 'Set')
            self.AddMatchString(compile(b'Amt([01 ]{2,11})\r\n'), self.MatchAudioMute, 'Update')
            self.AddMatchString(compile(b'Vmt([012])\r\n'), self.MatchGlobalVideoMute, None)
            self.AddMatchString(compile(b'Vmt([1-6])\*([012])\r\n'), self.MatchVideoMute, 'Set')
            self.AddMatchString(compile(b'Vmt([012 ]{2,11})\r\n'), self.MatchVideoMute, 'Update')
            self.AddMatchString(compile(b'HdcpE([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(compile(b'HdcpI([012])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(compile(b'HdcpO([1-6])\*([012])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(compile(b'Vtpo([1-6])\*([1-6])\r\n'), self.__MatchOutputFormat, 'Set')
            self.AddMatchString(compile(b'Vtpo([1-6 ]+)\r\n'), self.__MatchOutputFormat, 'Update')
            self.AddMatchString(compile(b'Sig([01])\*([01 ]+)\r\n'), self.__MatchSignalStatus, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'E(01|10|13)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioMute(self, value, qualifier):

        muteStates = {
            'Off': '0',
            'On': '1'
        }

        output = int(qualifier['Output'])
        self.__SetHelper('AudioMute', '{0}*{1}Z'.format(output, muteStates[value]), value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        self.__UpdateHelper('AudioMute', 'Z', value, qualifier)

    def MatchAudioMute(self, match, tag):

        muteStates = {
            '1': 'On',
            '0': 'Off'
        }

        if tag in ['Set', 'Update']:
            if tag == 'Set':
                output, state = match.group(1).decode(), match.group(2).decode()
                self.WriteStatus('AudioMute', muteStates[state], {'Output': output})
            else:
                output, states = 1, match.group(1).decode().split()
                for i in states:
                    self.WriteStatus('AudioMute', muteStates[i], {'Output': str(output)})
                    output += 1

    def SetGlobalAudioMute(self, value, qualifier):

        AudioMuteCmd = {
            'Off': '0Z',
            'On': '1Z'
        }

        self.__SetHelper('GlobalAudioMute', AudioMuteCmd[value], value, qualifier)

    def MatchGlobalAudioMute(self, match, tag):

        muteStates = {
            '1': 'On',
            '0': 'Off'
        }

        state = muteStates[match.group(1).decode()]
        for i in range(self.OutputSize):
            self.WriteStatus('AudioMute', state, {'Output': str(i + 1)})

    def SetGlobalVideoMute(self, value, qualifier):

        VideoMuteCmd = {
            'Off': '0B',
            'On': '1B',
            'On with Sync': '2B'
        }

        self.__SetHelper('GlobalVideoMute', VideoMuteCmd[value], value, qualifier)

    def MatchGlobalVideoMute(self, match, tag):

        muteStates = {
            '1': 'On',
            '0': 'Off',
            '2': 'On with Sync'
        }

        state = muteStates[match.group(1).decode()]
        for i in range(self.OutputSize):
            self.WriteStatus('VideoMute', state, {'Output': str(i + 1)})

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '\x1BE1HDCP\r',
            'Off': '\x1BE0HDCP\r'
        }

        HDCPInputAuthorizationCmdString = ValueStateValues[value]
        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = '\x1BEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, None)

    def UpdateHDCPInputStatus(self, value, qualifier):

        self.__UpdateHelper('HDCPInputStatus', '\x1BIHDCP\r', value, qualifier)

    def UpdateHDCPOutputStatus(self, value, qualifier):

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize:
            self.__UpdateHelper('HDCPOutputStatus', '\x1BO{}HDCP\r'.format(output), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPOutputStatus')

    def __MatchHDCPInputStatus(self, match, tag):

        HdcpStates = {
            '1': 'Source Detected with HDCP',
            '0': 'No Source Device Detected',
            '2': 'Source Detected without HDCP'
        }

        self.WriteStatus('HDCPInputStatus', HdcpStates[match.group(1).decode()], None)

    def __MatchHDCPOutputStatus(self, match, tag):

        HdcpStates = {
            '1': 'Sink Detected with HDCP',
            '0': 'No Sink Device Detected',
            '2': 'Sink Detected without HDCP'
        }

        self.WriteStatus('HDCPOutputStatus', HdcpStates[match.group(2).decode()], {'Output': match.group(1).decode()})

    def UpdateInputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('InputSignalStatus', '\x1BLS\r', value, qualifier)

    def UpdateOutputSignalStatus(self, value, qualifier):

        self.__UpdateHelper('OutputSignalStatus', '\x1BLS\r', value, qualifier)

    def __MatchSignalStatus(self, match, tag):

        SignalStates = {
            '1': 'Active',
            '0': 'Not Active'
        }

        self.WriteStatus('InputSignalStatus', SignalStates[match.group(1).decode()], None)

        output, states = 1, match.group(2).decode().split()
        for i in states:
            self.WriteStatus('OutputSignalStatus', SignalStates[i], {'Output': str(output)})
            output += 1

    def SetOutputFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto': '1',
            'DVI RGB 444': '2',
            'HDMI RGB Full': '3',
            'HDMI RGB Limited': '4',
            'HDMI YUV 444 Limited': '5',
            'HDMI YUV 422 Limited': '6'
        }

        output = int(qualifier['Output'])
        if 1 <= output <= self.OutputSize:
            OutputFormatCmdString = 'w{0}*{1}VTPO\r'.format(output, ValueStateValues[value])
            self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputFormat')

    def UpdateOutputFormat(self, value, qualifier):

        OutputFormatCmdString = 'wVTPO\r'
        self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def __MatchOutputFormat(self, match, tag):

        ValueStateValues = {
            '1': 'Auto',
            '2': 'DVI RGB 444',
            '3': 'HDMI RGB Full',
            '4': 'HDMI RGB Limited',
            '5': 'HDMI YUV 444 Limited',
            '6': 'HDMI YUV 422 Limited'
        }

        if tag == 'Set':
            outputValue = match.group(1).decode()
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('OutputFormat', value, {'Output': outputValue})
        else:
            count = 1
            values = match.group(1).decode().split()
            for i in values:
                self.WriteStatus('OutputFormat', ValueStateValues[i], {'Output': str(count)})
                count += 1

    def SetVideoMute(self, value, qualifier):

        MuteStates = {
            'Off': '0',
            'On': '1',
            'On with Sync': '2'
        }
        output = int(qualifier['Output'])
        VideoMuteCmd = '{0}*{1}B'.format(qualifier['Output'], MuteStates[value])
        self.__SetHelper('VideoMute', VideoMuteCmd, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        self.__UpdateHelper('VideoMute', 'B', value, qualifier)

    def MatchVideoMute(self, match, tag):

        muteStates = {
            '1': 'On',
            '0': 'Off',
            '2': 'On with Sync'
        }

        if tag in ['Set', 'Update']:
            if tag == 'Set':
                output, state = match.group(1).decode(), match.group(2).decode()
                self.WriteStatus('VideoMute', muteStates[state], {'Output': output})
            else:
                output, states = 1, match.group(1).decode().split()
                for i in states:
                    self.WriteStatus('VideoMute', muteStates[i], {'Output': str(output)})
                    output += 1

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

        errorstring = {
            '01': 'Invalid input channel number.',
            '10': 'Invalid command.',
            '13': 'Invalid value.'
        }[match.group(1).decode()]

        try:
            self.Error([errorstring])
        except KeyError:
            self.Error(['Unknown error.'])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

    def extr_18_3247_DA_2(self):

        self.OutputSize = 2

    def extr_18_3247_DA_4(self):

        self.OutputSize = 4

    def extr_18_3247_DA_6(self):

        self.OutputSize = 6

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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
                if result:
                    index = result.start()
                    CurrentMatch['callback'](result, CurrentMatch['para'])
                    self.__receiveBuffer = self.__receiveBuffer[:result.start()] + self.__receiveBuffer[result.end():]
                else:
                    break

        if index:
            # Clear out any junk data that came in before any good matches.
            self.__receiveBuffer = self.__receiveBuffer[index:]
        else:
            # In rare cases, the buffer could be filled with garbage quickly.
            # Make sure the buffer is capped.  Max buffer size set in init.
            self.__receiveBuffer = self.__receiveBuffer[-self.__maxBufferSize:]

    # Add regular expression so that it can be check on incoming data from device.
    def AddMatchString(self, regex_string, callback, arg):
        if regex_string not in self.__matchStringDict:
            self.__matchStringDict[regex_string] = {'callback': callback, 'para': arg}

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