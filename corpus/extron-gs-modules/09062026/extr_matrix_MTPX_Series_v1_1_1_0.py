from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, match, search
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
            'MTPX 1616': self.extr_15_41_1616,
            'MTPX 168': self.extr_15_41_168,
            'MTPX 816': self.extr_15_41_816,
            'MTPX 1632': self.extr_15_41_1632,
            'MTPX 3216': self.extr_15_41_3216,
            'MTPX 3232': self.extr_15_41_3232,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}},
        }

        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = []

        self.VerboseDisabled = True
        self.refresh_matrix = False

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt(\d+)\*(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'In(\d+) Aud([+-][0-9]{2})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'Amt[0-3]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})([0-9 -]*)Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'Vgp00 Out(\d{2})([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Mut([0|2]+)\r\n'), self.__MatchMute, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Out(\d{1,2}) Vol(\d{2})\r\n'), self.__MatchVolume, None)

            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'Rpr(\d+)\r\n'), self.__MatchQik, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.UpdateAllMatrixTie(None, None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.Send('wvm\r')

    def __MatchMute(self, match, tag):
        stat = match.group(1).decode()
        for i in range(0, len(stat)):
            if stat[i] == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output': str(i + 1)})
            elif stat[i] == '2':
                self.WriteStatus('AudioMute', 'On', {'Output': str(i + 1)})

    def __MatchQik(self, match, tag):

        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.Debug = True
        self.audio_status_counter = 0
        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        self.__UpdateHelper('RefreshMatrix', 'w0*1*2vc\rw0*1*1vc\r', value, qualifier)
        if self.OutputSize > 16:
            self.__UpdateHelper('RefreshMatrix', 'w0*17*1vc\rw0*17*2vc\r', value, qualifier)

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:

                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output + 1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1), 'Tie Type': 'Video'})
                    VideoList.add(output)

        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        av_counter_max = 16 if self.refresh_matrix else self.OutputSize
        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:

            if tag == 'Audio':
                self.audio_status_counter += 1
            elif tag == 'Video':
                self.video_status_counter += 1

            if i != '--':
                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag

                current_output += 1

        if self.audio_status_counter == av_counter_max and self.video_status_counter == av_counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__SetHelper('AudioMute', '{0}*{1}z'.format(channel, AudioMuteState[value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:
            self.__UpdateHelper('AudioMute', '{0}z'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def __MatchAudioMute(self, match, qualifier):
        AudioMuteName = {
            b'0': 'Off',
            b'1': 'On',
        }
        self.WriteStatus('AudioMute', AudioMuteName[match.group(2)], {'Output': str(int(match.group(1)))})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Mode 1': '1',
            'Mode 2': '2',
            'Off': '0'
        }
        self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'Mode 1',
            b'2': 'Mode 2',
            b'0': 'Off',
        }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetGlobalAudioMute(self, value, qualifier):
        AudioMuteState = {
            'Off': '0',
            'On': '1',
        }
        self.__SetHelper('GlobalAudioMute', '{0}*z'.format(AudioMuteState[value]), value, qualifier)

    def SetInputGain(self, value, qualifier):

        inputValue = int(qualifier['Input'])
        if -18 <= value <= 24 and 1 <= inputValue <= self.InputSize:
            if value < 0:
                InputGainCmdString = '{0}*{1}g\r\n'.format(inputValue, abs(value))
            else:
                InputGainCmdString = '{0}*{1}G\r\n'.format(inputValue, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        inputValue = int(qualifier['Input'])
        if 1 <= inputValue <= self.InputSize:
            InputGainCmdString = '{0}G\r\n'.format(inputValue)
            self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputGain')

    def __MatchInputGain(self, match, tag):

        inputValue = int(match.group(1).decode())
        value = int(match.group(2).decode())
        self.WriteStatus('InputGain', value, {'Input': str(inputValue)})

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeValues = {
            'Audio': '\x24',
            'Video': '\x26',
            'Audio/Video': '\x21'
        }

        inputValue = int(qualifier['Input'])
        outputValue = qualifier['Output']
        tieType = TieTypeValues[qualifier['Tie Type']]

        if 0 <= inputValue <= self.InputSize:
            if outputValue == 'All':
                MatrixTieCommandCmdString = '{0}*{1}\r\n'.format(inputValue, tieType)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            elif 1 <= int(outputValue) <= self.OutputSize:
                MatrixTieCommandCmdString = '{0}*{1}{2}\r\n'.format(inputValue, outputValue, tieType)
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __MatchOutputTieStatus(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video'
        }

        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                if i != input_ - 1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output - 1] = 'Untied'
                elif i == input_ - 1:
                    self.matrix_tie_status[i][output - 1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output - 1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_ - 1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output - 1] = tietype
                elif input_ == 0 or i != input_ - 1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output - 1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output - 1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video'
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        if self.matrix_tie_status[input_][output] == op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Audio/Video'
                        else:
                            self.matrix_tie_status[input_][output] = tietype
                    else:
                        if self.matrix_tie_status[input_][output] == 'Audio/Video':
                            self.matrix_tie_status[input_][output] = op_tie_type
                        elif self.matrix_tie_status[input_][output] != op_tie_type:
                            self.matrix_tie_status[input_][output] = 'Untied'

        elif tietype == 'Audio/Video':
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input - 1:
                        self.matrix_tie_status[input_][output] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) < 33:
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 < int(value) < 33:
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        ValueStateValues = {
            '1 - 16': 'w0*1*1vc\rw0*1*2vc\r',
            '17 - 32': 'w0*17*1vc\rw0*17*2vc\r',
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie(value, qualifier)
        else:
            self.refresh_matrix = True
            self.audio_status_counter = 0
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', ValueStateValues[value], value, qualifier)

    def SetVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 0 <= value <= 64 and 1 <= channel <= self.VolumeOutput:
            self.__SetHelper('Volume', '{0}*{1}v'.format(channel, value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        channel = int(qualifier['Output'])
        if 1 <= channel <= self.VolumeOutput:
            self.__UpdateHelper('Volume', '{0}v'.format(channel), value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):
        self.WriteStatus('Volume', int(match.group(2)), {'Output': match.group(1).decode()})

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (too large)',
            '10': 'Invalid Command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number(too large)',
            '13': 'Invalid value (out of range)',
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
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.VerboseDisabled = True
        self.refresh_matrix = False

    def extr_15_41_1616(self):

        self.InputSize = 16
        self.OutputSize = 16
        self.VolumeOutput = 4

    def extr_15_41_168(self):

        self.InputSize = 16
        self.OutputSize = 8
        self.VolumeOutput = 4

    def extr_15_41_816(self):

        self.InputSize = 8
        self.OutputSize = 16
        self.VolumeOutput = 4

    def extr_15_41_1632(self):

        self.InputSize = 16
        self.OutputSize = 32
        self.VolumeOutput = 8

    def extr_15_41_3216(self):

        self.InputSize = 32
        self.OutputSize = 16
        self.VolumeOutput = 8

    def extr_15_41_3232(self):

        self.InputSize = 32
        self.OutputSize = 32
        self.VolumeOutput = 8

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
