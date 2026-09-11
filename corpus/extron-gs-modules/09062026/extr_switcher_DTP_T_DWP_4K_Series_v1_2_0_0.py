from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait
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
            'AnalogAudioMute': {'Status': {}},
            'AudioInputFormat': {'Parameters': ['Input'], 'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPMode': {'Status': {}},
            'HDMIOutputAudioMute': {'Status': {}},
            'Information': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'AfmtI([1|2])\*([0-2])\r\n'), self.__MatchAudioInputFormat, None)
            self.AddMatchString(re.compile(b'HdcpE(0|1) (0|1)\r\n'), self.__MatchHDCPInputAuthorization, 'Update')
            self.AddMatchString(re.compile(b'HdcpE(1|2)\*(0|1)\r\n'), self.__MatchHDCPInputAuthorization, 'Set')
            self.AddMatchString(re.compile(b'HdcpS([0-3])\r\n'), self.__MatchHDCPMode, None)
            self.AddMatchString(re.compile(b'Afmt(0|1)\r\n'), self.__MatchHDMIOutputAudioMute, None)
            self.AddMatchString(re.compile(b'In(0|1|2)Vid In(0|1|2)Aud Ausw(0|1|2) Vmt(0|1) Amt(0|1)\r\n'), self.__MatchInformation, None)
            self.AddMatchString(re.compile(b'In([0-2]) (Aud|Vid|All)\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sig(0|1) (0|1)\*(0|1)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            self.AddMatchString(re.compile(b'E(01|06|10|13)\r\n'), self.__MatchError, None)

    def UpdateInput(self, value, qualifier):
        self.UpdateInformation(value, qualifier)
        
    def UpdateAnalogAudioMute(self, value, qualifier):
        self.UpdateInformation(value, qualifier)
        
    def UpdateAutoSwitchMode(self, value, qualifier):
        self.UpdateInformation(value, qualifier)
        
    def UpdateVideoMute(self, value, qualifier):
        self.UpdateInformation(value, qualifier)
    
    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetAnalogAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z',
        }

        AnalogAudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AnalogAudioMute', AnalogAudioMuteCmdString, value, qualifier)

    def SetAudioInputFormat(self, value, qualifier):

        InputStates = {
            'HDMI': '1',
            'DisplayPort': '2'
        }

        ValueStateValues = {
            'Auto': '0',
            'Digital Embedded': '1',
            'Analog': '2'
        }

        AudioInputFormatCmdString = 'wI{0}*{1}AFMT\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])
        self.__SetHelper('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)

    def UpdateAudioInputFormat(self, value, qualifier):

        InputStates = {
            'HDMI': '1',
            'DisplayPort': '2'
        }
        InputResponseValues = {
            '0': 'Auto',
            '1': 'Digital Embedded',
            '2': 'Analog'
        }

        AudioInputFormatCmdString = 'wI{0}AFMT\r'.format(InputStates[qualifier['Input']])
        res = self.__UpdateHelperSync('AudioInputFormat', AudioInputFormatCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AudioInputFormat', InputResponseValues[res[-1]], qualifier)
            except IndexError:
                self.Error(['Audio Input Format: Invalid/Unexpected response'])

    def __MatchAudioInputFormat(self, match, tag):

        InputValues = {
            '1': 'HDMI',
            '2': 'DisplayPort'
        }
        ValueStateValues = {
            '0': 'Auto',
            '1': 'Digital Embedded',
            '2': 'Analog'
        }
        input = InputValues[match.group(1).decode()]
        qualifier = {'Input': input}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioInputFormat', value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Highest Active Input': 'w1AUSW\r',
            'Lowest Active Input': 'w2AUSW\r',
            'Off': 'w0AUSW\r'
        }

        AutoSwitchModeCmdString = ValueStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        InputStates = {
            'HDMI': '1',
            'DisplayPort': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        HDCPInputAuthorizationCmdString = 'wE{0}*{1}HDCP\r'.format(InputStates[qualifier['Input']], ValueStateValues[value])

        self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationCmdString = 'wEHDCP\r'
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, tag):

        InputValues = {
            '1': 'HDMI',
            '2': 'DisplayPort'
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        if tag == 'Update':
            hdmi = ValueStateValues[match.group(1).decode()]
            displayport = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('HDCPInputAuthorization', hdmi, {'Input': 'HDMI'})
            self.WriteStatus('HDCPInputAuthorization', displayport, {'Input': 'DisplayPort'})
        elif tag == 'Set':
            self.WriteStatus('HDCPInputAuthorization', ValueStateValues[match.group(2).decode()], {'Input': InputValues[match.group(1).decode()]})

    def SetHDCPMode(self, value, qualifier):

        ValueStateValues = {
            'Follow Input': '0',
            'Always Encrypt Output': '1',
            'Follow Input (with continuous DVI trials)': '2',
            'Always Encrypt Output (with continuous DVI trials)': '3'
        }

        HDCPModeCmdString = 'wS{0}HDCP\r'.format(ValueStateValues[value])
        self.__SetHelper('HDCPMode', HDCPModeCmdString, value, qualifier)

    def UpdateHDCPMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Follow Input',
            '1': 'Always Encrypt Output',
            '2': 'Follow Input (with continuous DVI trials)',
            '3': 'Always Encrypt Output (with continuous DVI trials)'
        }
        HDCPModeCmdString = 'wSHDCP\r'

        res = self.__UpdateHelperSync('HDCPMode', HDCPModeCmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('HDCPMode', ValueStateValues[res[-1]], qualifier)
            except IndexError:
                self.Error(['HDCP Mode: Invalid/Unexpected response'])

    def __MatchHDCPMode(self, match, tag):

        ValueStateValues = {
            '0': 'Follow Input',
            '1': 'Always Encrypt Output',
            '2': 'Follow Input (with continuous DVI trials)',
            '3': 'Always Encrypt Output (with continuous DVI trials)'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPMode', value, None)

    def SetHDMIOutputAudioMute(self, value, qualifier):

        ValueStateValues = {
            'Off': '0',
            'On': '1'
        }

        HDMIOutputAudioMuteCmdString = 'w{0}AFMT\r'.format(ValueStateValues[value])
        self.__SetHelper('HDMIOutputAudioMute', HDMIOutputAudioMuteCmdString, value, qualifier)

    def UpdateHDMIOutputAudioMute(self, value, qualifier):

        HDMIOutputAudioMuteCmdString = 'wAFMT\r'
        self.__UpdateHelper('HDMIOutputAudioMute', HDMIOutputAudioMuteCmdString, value, qualifier)

    def __MatchHDMIOutputAudioMute(self, match, tag):

        ValueStateValues = {
            '0': 'Off',
            '1': 'On'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDMIOutputAudioMute', value, None)

    def UpdateInformation(self, value, qualifier):

        InformationCmdString = 'I'
        self.__UpdateHelper('Information', InformationCmdString, value, qualifier)

    def __MatchInformation(self, match, tag):

        InputValues = {
            '0': '0',
            '1': 'HDMI',
            '2': 'DisplayPort'
        }
        AutoSwitchModeValues = {
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input',
            '0': 'Off'
        }
        VideoMuteValues = {
            '1': 'On',
            '0': 'Off'
        }
        AnalogAudioMuteValues = {
            '1': 'On',
            '0': 'Off'
        }
        video_tie = InputValues[match.group(1).decode()]
        audio_tie = InputValues[match.group(2).decode()]
        if video_tie == '0':
            self.WriteStatus('Input', '0', {'Type': 'Video'})
        else:
            self.WriteStatus('Input', video_tie, {'Type': 'Video'})

        if audio_tie == '0':
            self.WriteStatus('Input', '0', {'Type': 'Audio'})
        else:
            self.WriteStatus('Input', audio_tie, {'Type': 'Audio'})

        if audio_tie == video_tie:
            if audio_tie == '0':
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', audio_tie, {'Type': 'Audio/Video'})
        else:
            self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
        self.WriteStatus('AutoSwitchMode', AutoSwitchModeValues[match.group(3).decode()], None)
        self.WriteStatus('VideoMute', VideoMuteValues[match.group(4).decode()], None)
        self.WriteStatus('AnalogAudioMute', AnalogAudioMuteValues[match.group(5).decode()], None)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '0': '0',
            'HDMI': '1',
            'DisplayPort': '2'
        }

        InputTypeValues = {
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
        }

        type = qualifier['Type']

        commandString = '{0}{1}'.format(ValueStateValues[value], InputTypeValues[type])
        self.__SetHelper('Input', commandString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        InputValues = {
            '0': '0',
            '1': 'HDMI',
            '2': 'DisplayPort'
        }
        InputTypeNames = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'All': 'Audio/Video'
        }

        value = InputValues[match.group(1).decode()]
        Type = InputTypeNames[match.group(2).decode()]
        qualifier = {'Type': Type}

        if Type != 'Audio/Video':
            otherType = 'Video' if Type == 'Audio' else 'Audio'
            if self.ReadStatus('Input', {'Type' : otherType}) == value:
                self.WriteStatus('Input', value, {'Type' : 'Audio/Video'})
            else:
                self.WriteStatus('Input', value, qualifier)
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})
        else:
            # in the case of 'All' type, write to Audio and Video status too
            self.WriteStatus('Input', value, {'Type' : 'Video'})
            self.WriteStatus('Input', value, {'Type' : 'Audio'})
            self.WriteStatus('Input', value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'w0LS\r'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Not Active',
            '1': 'Active'
        }

        hdmiValue = ValueStateValues[match.group(1).decode()]
        displayportValue = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputSignalStatus', hdmiValue, {'Input': 'HDMI'})
        self.WriteStatus('InputSignalStatus', displayportValue, {'Input': 'DisplayPort'})

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'Off': '0B'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number',
            'E06': 'Invalid switch attempt in this mode',
            'E10': 'Invalid command',
            'E13': 'Invalid parameter',
        }

        ErrorCode = DEVICE_ERROR_CODES.get(response)
        if ErrorCode:
            self.Error([ErrorCode])
            return ''
        else:
            return response

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
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __UpdateHelperSync(self, command, commandstring, value, qualifier):
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
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                    if not res:
                        return ''
                    else:
                        return self.__CheckResponseForErrors(command, res.decode().strip())
            else:
                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
                if not res:
                    return ''
                else:
                    return self.__CheckResponseForErrors(command, res.decode().strip())

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '06': 'Invalid switch attempt in this mode',
            '10': 'Invalid command',
            '13': 'Invalid parameter',
        }
        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastHDCPInputStatusUpdate = 0
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
