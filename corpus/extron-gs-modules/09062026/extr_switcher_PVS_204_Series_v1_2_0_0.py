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
            'AutoSwitchMode': {'Status': {}},
            'AuxMixInput': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'OutputVolume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In(\d) Aud=\+?(\-?[0-9]{1,2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'Amt(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Asw\*(0|1)\r\n'), self.__MatchAutoSwitchMode, None)
            self.AddMatchString(re.compile(b'Mix(0|1)\r\n'), self.__MatchAuxMixInput, None)
            self.AddMatchString(re.compile(b'Exe(0|1)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Vid(0|1|2|3|4)\r\n'), self.__MatchVideoInput, None)
            self.AddMatchString(re.compile(b'Aud(0|1|2|3|4)\r\n'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'Chn(0|1|2|3|4)\r\n'), self.__MatchAudioVideoInput, None)
            self.AddMatchString(re.compile(b'Vid(0|1|2|3|4) Aud(0|1|2|3|4) Vol\d+\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Vol([0-9]{3})\r\n'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchError, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        channel = int(qualifier['Input'])
        if channel < 1 or channel > 7:
            self.Discard('Invalid Command for SetAudioGainAttenuation')
        elif value < -18 or value > 24:
            self.Discard('Invalid Command for SetAudioGainAttenuation')
        else:
            if value >= 0:
                AudioGainAttenuationCmdString = '{0}*{1}G'.format(channel, value)
            elif value < 0:
                AudioGainAttenuationCmdString = '{0}*{1}g'.format(channel, value)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

    def UpdateAudioGainAttenuation(self, value, qualifier):

        channel = int(qualifier['Input'])
        AudioGainAttenuationCmdString = '{0}*G'.format(channel)
        self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)

    def __MatchAudioGainAttenuation(self, match, qualifier):

        value = int(match.group(2).decode())
        self.WriteStatus('AudioGainAttenuation', value, {'Input': match.group(1).decode()})

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '1Z',
            'Off': '0Z',
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            '1': 'On',
            '0': 'Off',
        }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeState = {
            'On': '72*1#',
            'Off': '72*0#',
        }

        AutoSwitchModeCmdString = AutoSwitchModeState[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeCmdString = '72#'
        self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def __MatchAutoSwitchMode(self, match, tag):

        AutoSwitchModeState = {
            '1': 'On',
            '0': 'Off'
        }

        value = AutoSwitchModeState[match.group(1).decode()]
        self.WriteStatus('AutoSwitchMode', value, None)

    def SetAuxMixInput(self, value, qualifier):

        AuxMixInputState = {
            'On': '1M',
            'Off': '0M'
        }

        AuxMixInputCmdString = AuxMixInputState[value]

        self.__SetHelper('AuxMixInput', AuxMixInputCmdString, value, qualifier)

    def UpdateAuxMixInput(self, value, qualifier):

        AuxMixInputCmdString = 'M'
        self.__UpdateHelper('AuxMixInput', AuxMixInputCmdString, value, qualifier)

    def __MatchAuxMixInput(self, match, tag):

        AuxMixInputState = {
            '1': 'On',
            '0': 'Off'
        }

        value = AuxMixInputState[match.group(1).decode()]
        self.WriteStatus('AuxMixInput', value, None)

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
            '0': 'Off'
        }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        InputType = {
            'Video': '&',
            'Audio': '$',
            'Audio/Video': '!',
        }

        Input = qualifier['Type']

        if int(value) < 0 or int(value) > 4:
            self.Discard('Invalid Command for SetInput')
        else:
            InputCmdString = '{0}{1}'.format(value, InputType[Input])
            self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        AudioInput = match.group(2).decode()
        VideoInput = match.group(1).decode()

        if AudioInput == VideoInput:
            AVInput = VideoInput
        else:
            AVInput = '0'

        self.WriteStatus('Input', AudioInput, {'Type': 'Audio'})
        self.WriteStatus('Input', VideoInput, {'Type': 'Video'})
        self.WriteStatus('Input', AVInput, {'Type': 'Audio/Video'})

    def __MatchVideoInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Video'})

    def __MatchAudioInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Audio'})

    def __MatchAudioVideoInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Audio/Video'})
        self.WriteStatus('Input', value, {'Type': 'Video'})
        self.WriteStatus('Input', value, {'Type': 'Audio'})

    def SetOutputVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)

            self.__SetHelper('OutputVolume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('OutputVolume', VolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputVolume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            self.Send(commandstring)

           

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid Input Channel Number',
            '06': 'Invalid Channel Change',
            '10': 'Invalid Command',
            '13': 'Invalid Value',
            '14': 'Invalid Command for this configuration',
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
