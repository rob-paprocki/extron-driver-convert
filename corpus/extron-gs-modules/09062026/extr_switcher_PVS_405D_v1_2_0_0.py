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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'HDCPOutputStatus': {'Status': {}},
            'Input': {'Status': {}},
            'InputMute': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'PowerSaveMode': {'Status': {}},
            'VideoMute': {'Status': {}},
            'VoiceLiftContactClosure': {'Status': {}},
            'VoiceLiftRelay': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In([1-8]) Aud([-+]?[0-9]{1,2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'HdcpE([1-4])\*([01])\r\n'), self.__MatchHDCPInputAuthorization, None)
            self.AddMatchString(re.compile(b'HdcpI([1-4])\*([0-3])\r\n'), self.__MatchHDCPInputStatus, None)
            self.AddMatchString(re.compile(b'HdcpO([0-3])\r\n'), self.__MatchHDCPOutputStatus, None)
            self.AddMatchString(re.compile(b'Chn([1-5])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Imut([178])\*([01])\r\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'Psav([0-4])\r\n'), self.__MatchPowerSaveMode, None)
            self.AddMatchString(re.compile(b'Sig([0-3]) ([0-3]) ([0-3]) ([0-3])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Vmt([01])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(re.compile(b'Vol([0-9]{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Rly([01]) Sio([01])\r\n'), self.__MatchVoiceLiftStatus, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def __MatchVerboseMode(self, match, qualifier):

        self.OnConnected()
        self.VerboseDisabled = False

    def SetAudioGainAttenuation(self, value, qualifier):

        InputState = {
            'Input 1': '1',
            'Input 2': '2',
            'Input 3': '3',
            'Input 4': '4',
            'Input 5': '5',
            'VoiceLift': '7',
            'Aux': '8',
        }

        ValueConstraints = {
            'Min': -18,
            'Max': 24
        }

        Input = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            AudioGainAttenuationCmdString = '{0}*{1}G'.format(InputState[Input], value)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        InputState = {
            'Input 1': '1',
            'Input 2': '2',
            'Input 3': '3',
            'Input 4': '4',
            'Input 5': '5',
            'VoiceLift': '7',
            'Aux': '8'
        }

        Input = qualifier['Input']
        AudioGainAttenuationCmdString = '{0}G'.format(InputState[Input])
        self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, tag):

        InputState = {
            '1': 'Input 1',
            '2': 'Input 2',
            '3': 'Input 3',
            '4': 'Input 4',
            '5': 'Input 5',
            '7': 'VoiceLift',
            '8': 'Aux',
        }

        value = int(match.group(2).decode())
        self.WriteStatus('AudioGainAttenuation', value, {'Input': InputState[match.group(1).decode()]})

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '1Z',
            'Off': '0Z'
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1X',
            'Off': '0X'
        }

        ExecutiveModeCmdString = ExecutiveModeState[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeState = {
            '1': 'On',
            '0': 'Off',
        }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetHDCPInputAuthorization(self, value, qualifier):

        HDCPInputAuthorizationState = {
            'On': '1',
            'Off': '0'
        }

        Input = qualifier['Input']
        if 1 <= int(Input) <= 4:
            HDCPInputAuthorizationCmdString = '\x1BE{0}*{1}HDCP\r'.format(Input, HDCPInputAuthorizationState[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        Input = qualifier['Input']
        HDCPInputAuthorizationCmdString = '\x1BE{0}HDCP\r'.format(Input)
        self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)

    def __MatchHDCPInputAuthorization(self, match, qualifier):

        HDCPInputAuthorizationState = {
            '1': 'On',
            '0': 'Off'
        }

        value = HDCPInputAuthorizationState[match.group(2).decode()]
        self.WriteStatus('HDCPInputAuthorization', value, {'Input': match.group(1).decode()})

    def UpdateHDCPInputStatus(self, value, qualifier):

        Input = qualifier['Input']
        HDCPInputStatusCmdString = '\x1BI{0}HDCP\r'.format(Input)
        self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)

    def __MatchHDCPInputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Source detected, HDCP not compliant',
            '1': 'Source detected, HDCP compliant',
            '2': 'No source detected',
            '3': 'Unknown'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('HDCPInputStatus', value, {'Input': match.group(1).decode()})

    def UpdateHDCPOutputStatus(self, value, qualifier):

        HDCPOutputStatusCmdString = '\x1BOHDCP\r'
        self.__UpdateHelper('HDCPOutputStatus', HDCPOutputStatusCmdString, value, qualifier)

    def __MatchHDCPOutputStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Source encrypted, sink connected, HDCP not compliant',
            '1': 'Source encrypted, sink connected, HDCP compliant',
            '2': 'No sink detected',
            '3': 'Source not encrypted, sink connected, HDCP status unknown'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('HDCPOutputStatus', value, None)

    def SetInput(self, value, qualifier):

        InputState = {
            '1': '1!',
            '2': '2!',
            '3': '3!',
            '4': '4!',
            '5': '5!',
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, None)

    def SetInputMute(self, value, qualifier):

        InputMuteState = {
            'Program': '1',
            'VoiceLift': '7',
            'Aux': '8'
        }

        MuteState = {
            'On': '1',
            'Off': '0'
        }

        Input = qualifier['Input']
        InputMuteCmdString = '\x1B{0}*{1}IMUT\r'.format(InputMuteState[Input], MuteState[value])
        self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)

    def UpdateInputMute(self, value, qualifier):

        InputMuteState = {
            'Program': '1',
            'VoiceLift': '7',
            'Aux': '8'
        }

        Input = qualifier['Input']
        InputMuteCmdString = '\x1B{0}IMUT\r'.format(InputMuteState[Input])
        self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)

    def __MatchInputMute(self, match, qualifier):

        InputMuteState = {
            '1': 'On',
            '0': 'Off'
        }

        InputValues = {
            '1': 'Program',
            '7': 'VoiceLift',
            '8': 'Aux'
        }

        value = InputMuteState[match.group(2).decode()]
        self.WriteStatus('InputMute', value, {'Input': InputValues[match.group(1).decode()]})

    def SetPowerSaveMode(self, value, qualifier):

        PowerSaveModeState = {
            'Mode 1': '\x1B1PSAV\r',
            'Mode 2': '\x1B2PSAV\r',
            'Mode 3': '\x1B3PSAV\r',
            'Mode 4': '\x1B4PSAV\r',
            'Off': '\x1B0PSAV\r',
        }

        PowerSaveModeCmdString = PowerSaveModeState[value]
        self.__SetHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def UpdatePowerSaveMode(self, value, qualifier):

        PowerSaveModeCmdString = '\x1BPSAV\r'
        self.__UpdateHelper('PowerSaveMode', PowerSaveModeCmdString, value, qualifier)

    def __MatchPowerSaveMode(self, match, tag):

        PowerSaveModeState = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3',
            '4': 'Mode 4',
        }

        value = PowerSaveModeState[match.group(1).decode()]
        self.WriteStatus('PowerSaveMode', value, None)

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'WLS\x0D'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusState = {
            '1': 'Active',
            '0': 'Not Active',
        }

        Input1 = InputSignalStatusState[match.group(1).decode()]
        Input2 = InputSignalStatusState[match.group(2).decode()]
        Input3 = InputSignalStatusState[match.group(3).decode()]
        Input4 = InputSignalStatusState[match.group(4).decode()]

        self.WriteStatus('InputSignalStatus', Input1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', Input2, {'Input': '2'})
        self.WriteStatus('InputSignalStatus', Input3, {'Input': '3'})
        self.WriteStatus('InputSignalStatus', Input3, {'Input': '4'})

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'On': '1B',
            'Off': '0B',
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

    def UpdateVoiceLiftContactClosure(self, value, qualifier):

        VoiceLiftContactClosureCmdString = '34I'
        self.__UpdateHelper('VoiceLiftContactClosure', VoiceLiftContactClosureCmdString, value, qualifier)

    def __MatchVoiceLiftStatus(self, match, tag):

        ValueStateValuesRR = {
            '1': 'On',
            '0': 'Off'
        }

        ValueStateValuesCC = {
            '0': 'Open',
            '1': 'Closed'
        }

        value1 = ValueStateValuesRR[match.group(1).decode()]
        value2 = ValueStateValuesCC[match.group(2).decode()]

        self.WriteStatus('VoiceLiftRelay', value1, None)
        self.WriteStatus('VoiceLiftContactClosure', value2, None)

    def UpdateVoiceLiftRelay(self, value, qualifier):

        self.UpdateVoiceLiftContactClosure(value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

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
            '01': 'Invalid input channel',
            '10': 'Invalid command',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
            '14': 'Not valid for this configuration',
            '22': 'Busy',
            '25': 'Device not present'
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

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