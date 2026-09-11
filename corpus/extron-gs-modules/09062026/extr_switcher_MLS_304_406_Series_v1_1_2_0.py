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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'MLS 304': self.extr_2_111_304,
            'MLS 304MA': self.extr_2_111_304,
            'MLS 304SA': self.extr_2_111_304,
            'MLS 406': self.extr_2_111_406,
            'MLS 406MA': self.extr_2_111_406,
            'MLS 406SA': self.extr_2_111_406,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'Bass': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputType': {'Parameters': ['Input'], 'Status': {}},
            'Loudness': {'Status': {}},
            'RGBDelay': {'Status': {}},
            'Treble': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In([0-9]) Aud=([+-][0-9]{2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'Amt([01])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Bas=([-+]\d*\.\d)\r\n'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'(Chn|Aud|Vid)([0-9])\r\n'), self.__MatchInput, 'Set')
            self.AddMatchString(re.compile(b'Loudness\*([01])\r\n'), self.__MatchLoudness, None)
            self.AddMatchString(re.compile(b'RGBDly\*([0-9]{2})\r\n'), self.__MatchRGBDelay, None)
            self.AddMatchString(re.compile(b'Trb=([-+]\d*\.\d)\r\n'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'Vid([0-9]) Aud([0-9])'), self.__MatchInput, 'Update')
            self.AddMatchString(re.compile(b'Vol([0-9]{3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'E(\d{2})\r\n'), self.__MatchError, None)

    def SetAudioGainAttenuation(self, value, qualifier):

        inputValue = qualifier['Input']
        if -42 <= int(value) <= 24 and 1 <= int(inputValue) <= self.InputSize:
            if value < 0:
                AudioGainAttenuationCmdString = '{0}*{1}g'.format(inputValue, abs(value))
            else:
                AudioGainAttenuationCmdString = '{0}*{1}G'.format(inputValue, value)

            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        inputValue = qualifier['Input']
        if 1 <= int(inputValue) <= self.InputSize:
            AudioGainAttenuationCmdString = '{0}*G'.format(inputValue)
            self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        value1 = match.group(1).decode()
        value2 = int(match.group(2).decode())
        qualifier = {'Input': value1}
        self.WriteStatus('AudioGainAttenuation', value2, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteStateValues = {
            'On': '1Z',
            'Off': '0Z',
        }

        AudioMuteCmdString = AudioMuteStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = AudioMuteStateNames[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetBass(self, value, qualifier):

        BassConstraints = {
            'Min': -10.5,
            'Max': 10.5,
        }
        BassRangeConvertion = {
            -10.5: 0,
            -9.0: 1,
            -7.5: 2,
            -6.0: 3,
            -4.5: 4,
            -3.0: 5,
            -1.5: 6,
            0.0: 7,
            1.5: 8,
            3.0: 9,
            4.5: 10,
            6.0: 11,
            7.5: 12,
            9.0: 13,
            10.5: 14,
        }
        value1 = BassRangeConvertion[value]
        if BassConstraints['Min'] <= value <= BassConstraints['Max']:
            BassCmdString = '{0}<'.format(value1)
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        BassCmdString = '<'
        self.__UpdateHelper('Bass', BassCmdString, value, qualifier)

    def __MatchBass(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('Bass', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeValues = {
            'Mode 1': '1x',
            'Mode 2': '2X',
            'Off': '0X',
        }

        ExecutiveModeCmdString = ExecutiveModeValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
            '1': 'Mode 1',
            '2': 'Mode 2',
            '0': 'Off',
        }

        value = ExecutiveModeStateNames[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        TypeT = qualifier['Type']
        TypeTCmd = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!',
        }

        if 0 <= int(value) <= self.InputSize:
            InputCmdString = '{0}{1}'.format(value, TypeTCmd[TypeT])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, tag):

        SwitchTypeNames = {
            'Chn': 'Audio/Video',
            'Aud': 'Audio',
            'Vid': 'Video'
        }

        if tag == 'Set':
            SwitchType = SwitchTypeNames[match.group(1).decode()]
            value = match.group(2).decode()
            self.WriteStatus('Input', value, {'Type': SwitchType})
            if SwitchType == 'Audio/Video':
                self.WriteStatus('Input', value, {'Type': 'Audio'})
                self.WriteStatus('Input', value, {'Type': 'Video'})
        elif tag == 'Update':
            value1 = int(match.group(1).decode())
            self.WriteStatus('Input', str(value1), {'Type': 'Video'})
            value2 = int(match.group(2).decode())
            self.WriteStatus('Input', str(value2), {'Type': 'Audio'})
            if value1 == value2:
                self.WriteStatus('Input', str(value1), {'Type': 'Audio/Video'})
            else:
                self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

    def SetInputType(self, value, qualifier):

        InputTypeValues = {
            'Video': '*1\\',
            'RGB': '*2\\',
        }

        inputValue = qualifier['Input']
        if 1 <= int(inputValue) <= self.InputSize:
            InputTypeCmdString = '{0}{1}'.format(inputValue, InputTypeValues[value])
            self.__SetHelperSynchronous('InputType', InputTypeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputType')

    def UpdateInputType(self, value, qualifier):

        InputTypeNames = {
            '1': 'Video',
            '2': 'RGB'
        }

        inputValue = qualifier['Input']
        if 1 <= int(inputValue) <= self.InputSize:
            res = self.__UpdateHelperSynchronous('InputType', '{0}\\'.format(inputValue), value, qualifier)
            if res:
                try:
                    value = InputTypeNames[res[-7]]
                    self.WriteStatus('InputType', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Type: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputType')

    def SetLoudness(self, value, qualifier):

        LoudnessStateValues = {
            'On': '29*1#',
            'Off': '29*0#',
        }

        LoudnessCmdString = LoudnessStateValues[value]
        self.__SetHelper('Loudness', LoudnessCmdString, value, qualifier)

    def UpdateLoudness(self, value, qualifier):

        LoudnessCmdString = '29#'
        self.__UpdateHelper('Loudness', LoudnessCmdString, value, qualifier)

    def __MatchLoudness(self, match, tag):

        LoudnessStateNames = {
            '1': 'On',
            '0': 'Off',
        }

        value = LoudnessStateNames[match.group(1).decode()]
        self.WriteStatus('Loudness', value, None)

    def SetRGBDelay(self, value, qualifier):

        RGBDelayRangeConvertion = {
            0.0: 0,
            0.5: 1,
            1.0: 2,
            1.5: 3,
            2.0: 4,
            2.5: 5,
            3.0: 6,
            3.5: 7,
            4.0: 8,
            4.5: 9,
            5.0: 10,
        }

        value1 = RGBDelayRangeConvertion[value]
        if 0.0 <= value <= 5.0:
            RGBDelayCmdString = '3*{0}#'.format(value1)
            self.__SetHelper('RGBDelay', RGBDelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRGBDelay')

    def UpdateRGBDelay(self, value, qualifier):

        RGBDelayCmdString = '3#'
        self.__UpdateHelper('RGBDelay', RGBDelayCmdString, value, qualifier)

    def __MatchRGBDelay(self, match, tag):

        value = int(match.group(1))
        self.WriteStatus('RGBDelay', float(value / 2), None)

    def SetTreble(self, value, qualifier):

        TrebleRangeConvertion = {
            -10.5: 0,
            -9.0: 1,
            -7.5: 2,
            -6.0: 3,
            -4.5: 4,
            -3.0: 5,
            -1.5: 6,
            0.0: 7,
            1.5: 8,
            3.0: 9,
            4.5: 10,
            6.0: 11,
            7.5: 12,
            9.0: 13,
            10.5: 14,
        }

        value1 = TrebleRangeConvertion[value]
        if -10.5 <= value <= 10.5:
            TrebleCmdString = '{0}>'.format(value1)
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        TrebleCmdString = '>'
        self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)

    def __MatchTreble(self, match, tag):

        value = float(match.group(1))
        self.WriteStatus('Treble', value, None)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
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

    def __MatchError(self, match, tag):
        self.counter = 0

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number (the number is too large)',
            'E10': 'Invalid command',
            'E13': 'Invalid value (the number is out of range / too large)',
            'E14': 'Invalid for this configuration',
            'E23': 'Checksum error (for file uploads)',
        }
        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input channel number (the number is too large)',
            'E10': 'Invalid command',
            'E13': 'Invalid value (the number is out of range / too large)',
            'E14': 'Invalid for this configuration',
            'E23': 'Checksum error (for file uploads)',
        }
        if response:
            self.counter = 0
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, k, v)
                    self.Error([errorString])
                    response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __SetHelperSynchronous(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=re.compile(b'Typ ([12])=(Vid|RGB)\r\n'))
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res.decode())

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

    def __UpdateHelperSynchronous(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=re.compile(b'Typ ([12])=(Vid|RGB)\r\n'))
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

    def extr_2_111_304(self):
        self.InputSize = 4

    def extr_2_111_406(self):
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

        # check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = re.search(regexString, self.__receiveBuffer)
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
