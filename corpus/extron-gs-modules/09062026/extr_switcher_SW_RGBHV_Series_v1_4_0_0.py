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
            'SW2 RGBHV': self.extr_2_120_sw2,
            'SW4 RGBHV': self.extr_2_120_sw4,
            'SW6 RGBHV': self.extr_2_120_sw6,
            'SW2 RGBHV A': self.extr_2_120_sw2_A,
            'SW4 RGBHV A': self.extr_2_120_sw4_A,
            'SW6 RGBHV A': self.extr_2_120_sw6_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Sig ([01]) ([01]) ?([01])? ?([01])? ?([01])? ?([01])?\r\n'), self.__MatchInputSignalStatus, None)
        self.UpdateStatusRegex = re.compile('V([0-6]) A([0-6]|x) F[0-6] Vmt(1|0) Amt(1|0)\r\n')

    def SetAudioGainAttenuation(self, value, qualifier):

        if (-18 <= value <= 24) and (1 <= int(qualifier['Input']) <= self.InputSize):
            if value >= 0:
                InputGainCmdString = '{0}*{1}G'.format(qualifier['Input'], value)
            elif value < 0:
                InputGainCmdString = '{0}*{1}g'.format(qualifier['Input'], -value)

            self.__SetHelper('AudioGainAttenuation', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        if 1 <= int(qualifier['Input']) <= self.InputSize:
            InputGainCmdString = 'V{0}G'.format(qualifier['Input'])
            res = self.__UpdateHelper('AudioGainAttenuation', InputGainCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('AudioGainAttenuation', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Audio Gain Attenuation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '{0}Z'.format(ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetInput(self, value, qualifier):

        TypeStates = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }
        if self.audio:
            if value == '0':
                InputACmdString = '0{0}'.format(TypeStates[qualifier['Type']])
                self.__SetHelper('Input', InputACmdString, value, qualifier)
            elif 1 <= int(value) <= self.InputSize:
                InputACmdString = '{0}{1}'.format(value, TypeStates[qualifier['Type']])
                self.__SetHelper('Input', InputACmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')
        else:
            if value == '0':
                InputCmdString = '0!'
                self.__SetHelper('Input', InputCmdString, value, qualifier)
            elif 1 <= int(value) <= self.InputSize:
                InputCmdString = '{0}!'.format(value)
                self.__SetHelper('Input', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        InputCmdString = 'I'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                match = re.search(self.UpdateStatusRegex, res)
                video_tie = match.group(1)
                audio_tie = match.group(2)
                video_mute = match.group(3)
                audio_mute = match.group(4)
                if audio_tie == 'x' and not self.audio:
                    if video_tie == '0':
                        self.WriteStatus('Input', '0', None)
                    else:
                        self.WriteStatus('Input', video_tie, None)
                elif self.audio:
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

                if self.audio:
                    self.WriteStatus('AudioMute', ValueStateValues[audio_mute], None)

                self.WriteStatus('VideoMute', ValueStateValues[video_mute], None)

            except (KeyError, IndexError, AttributeError):
                self.Error(['Input : Invalid/unexpected response'])

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = '0S'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        ValueStateValues = {
            '0': 'Not Active',
            '1': 'Active'
        }

        try:
            for x in range(1, self.InputSize + 1):
                qualifier = {'Input': str(x)}
                value = ValueStateValues[match.group(x).decode()]
                self.WriteStatus('InputSignalStatus', value, qualifier)
        except AttributeError:
            self.Error(['Input Signal Status: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        VideoMuteCmdString = '{0}B'.format(ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid Input number (out of Range)',
            'E10': 'Invalid command',
            'E06': 'Invalid Input channel change (autoswitch mode active)',
            'E09': 'Invalid function (mode) parameter',
            'E13': 'Invalid value'
        }

        if response:
            error_code = DEVICE_ERROR_CODES.get(response[:-2])
            if error_code:
                self.Error(['{0}: {1}'.format(sourceCmdName, error_code)])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        elif command == 'InputSignalStatus':
            self.Send(commandstring)
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def extr_2_120_sw2(self):
        self.audio = False
        self.InputSize = 2

    def extr_2_120_sw4(self):
        self.audio = False
        self.InputSize = 4

    def extr_2_120_sw6(self):
        self.audio = False
        self.InputSize = 6

    def extr_2_120_sw2_A(self):
        self.audio = True
        self.InputSize = 2

    def extr_2_120_sw4_A(self):
        self.audio = True
        self.InputSize = 4

    def extr_2_120_sw6_A(self):
        self.audio = True
        self.InputSize = 6

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
