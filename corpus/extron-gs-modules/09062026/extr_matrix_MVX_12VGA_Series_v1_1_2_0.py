from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from re import findall, match, compile, search

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
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
            'MVX 128 VGA A': self.extr_15_1299_128_VGA_A,
            'MVX 168 VGA A': self.extr_15_1299_168_VGA_A,
            'MVX 1212 VGA A': self.extr_15_1299_1212_VGA_A,
            'MVX Plus 128 VGA A': self.extr_15_1299_128_VGA_A,
            'MVX 1616 VGA A': self.extr_15_1299_1616_VGA_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': { 'Status': {}},
            'GlobalAudioMute': { 'Status': {}},
            'GlobalVideoMute': { 'Status': {}},
            'InputGain': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'PresetSave': { 'Status': {}},
            'RefreshMatrix': { 'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }
        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Amt0?([0-9]{1,2})\*(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(compile(b'Exe(0|1)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'In0?([0-9]{1,2}) Aud\+?(\-?[0-9]{1,2})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(compile(b'In0+ ([0-1]+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Vmt0?([0-9]{1,2})\*(0|1)\r\n'), self.__MatchVideoMute, None)

            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Rpr\d+\r\n'), self.__MatchQik, None) # Response to a Set Preset Recall command
            self.AddMatchString(compile(b'Vgp00 Out(\d+) ([0-9 -]*) Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vgp00 Out(\d+) ([0-9 -]*) Aud\r\n'), self.__MatchAllMatrixTie, 'Audio')
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|Aud|RGB))|(?:In(\d+) (All|Vid|Aud|RGB))\r\n'), self.__MatchOutputTieStatus, None)

            self.AddMatchString(compile(b'Vmt(0|1)\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Amt(0|1)\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-3]*)\r\n'), self.__MatchMute, None)

            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)


    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.SetRefreshMatrix(None, None)

    def __MatchQik(self, match, tag):
        self.SetRefreshMatrix(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.Send('\x1B0*1*1VC\r')  # Update Video Status
        self.Send('\x1B0*1*2VC\r')  # Update Audio Status

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):
        AudioList = set()
        VideoList = set()

        if tie == 'Individual':
            output_range = range(output-1, output)
        else:
            output_range = range(self.OutputSize)
        for input_ in range(self.InputSize):
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Audio/Video':
                    for tie_type in ['Audio', 'Video', 'Audio/Video']:
                        self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': tie_type})
                    AudioList.add(output)
                    VideoList.add(output)
                elif tietype == 'Audio':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Audio'})
                    AudioList.add(output)
                elif tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', '0', {'Output': str(output+1), 'Tie Type': 'Audio/Video'})
                    self.WriteStatus('OutputTieStatus', str(input_+1), {'Output': str(output+1), 'Tie Type': 'Video'})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Video'})
            if o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio'})
            if o not in VideoList and o not in AudioList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o+1), 'Tie Type': 'Audio/Video'})

    def __MatchAllMatrixTie(self, match, tag):
        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        opposite_tag = 'Video' if tag == 'Audio' else 'Audio'

        for i in input_list:

            if i != '--':

                if i != '00':
                    if self.matrix_tie_status[int(i) - 1][int(current_output - 1)] == opposite_tag:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag

                current_output += 1

        if tag == 'Audio':
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')
    ###########################################
    def SetAudioMute(self, value, qualifier):
        AudioMuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetAudioMute')
        else:
            AudioMuteCmdString = '{0}*{1}Z'.format(channel, AudioMuteState[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        channel = qualifier['Output']
        AudioMuteCmdString = '{0}Z'.format(channel)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, qualifier):
        AudioMuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = AudioMuteState[match.group(2).decode()]
        self.WriteStatus('AudioMute', value, {'Output' : match.group(1).decode()})

    def SetExecutiveMode(self, value, qualifier):
        ExecutiveModeState = {
            'On'  : '1',
            'Off' : '0'
        }

        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):
        ExecutiveModeState = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetGlobalAudioMute(self, value, qualifier):
        GlobalAudioMuteState = {
            'On'  : '1*Z',
            'Off' : '0*Z'
        }

        GlobalAudioMuteCmdString = '{0}*Z'.format(GlobalAudioMuteState[value])
        self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):
        GlobalVideoMuteState = {
            'On'  : '1*B',
            'Off' : '0*B'
        }

        GlobalVideoMuteCmdString = '{0}*B'.format(GlobalVideoMuteState[value])
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def __MatchGlobalMute(self, value, qualifier):
        self.UpdateMute( None, None)

    def UpdateMute(self, value, qualifier):
        self.Send('wvm\r')

    def __MatchMute(self, match, qualifier):
        stat = match.group(1).decode()
        Output = 1
        for i in stat:
            if i == '0':
                self.WriteStatus('AudioMute', 'Off', {'Output' : str(Output)})
                self.WriteStatus('VideoMute', 'Off', {'Output' : str(Output)})
            if i == '1':
                self.WriteStatus('AudioMute', 'Off', {'Output' : str(Output)})
                self.WriteStatus('VideoMute', 'On', {'Output' : str(Output)})
            if i == '2':
                self.WriteStatus('AudioMute', 'On', {'Output' : str(Output)})
                self.WriteStatus('VideoMute', 'Off', {'Output' : str(Output)})
            if i == '3':
                self.WriteStatus('AudioMute', 'On', {'Output' : str(Output)})
                self.WriteStatus('VideoMute', 'On', {'Output' : str(Output)})
            Output+=1

    def SetInputGain(self, value, qualifier):
        channel = int(qualifier['Input'])
        if channel < 1 or channel > self.InputSize:
            self.Discard('Invalid Command for SetInputGain')
        elif value < -18 or value > 24:
            self.Discard('Invalid Command for SetInputGain')
        else:
            if value >= 0:
                InputGainCmdString = '{0}*{1}G'.format(channel, value)
            elif value < 0:
                InputGainCmdString = '{0}*{1}g'.format(channel, value)
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)

    def UpdateInputGain(self, value, qualifier):
        channel = qualifier['Input']
        InputGainCmdString = '{0}G'.format(channel)
        self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)

    def __MatchInputGain(self, match, qualifier):
        value = int(match.group(2).decode())
        self.WriteStatus('InputGain', value, {'Input' : match.group(1).decode()})

    def UpdateInputSignalStatus(self, value, qualifier):
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)


    def __MatchInputSignalStatus(self, match, qualifier):
        SignalStatusState = {
            '1' : 'Active',
            '0' : 'Not Active'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputVal in signal:
            self.WriteStatus('InputSignalStatus', SignalStatusState[inputVal], {'Input' : str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):
        TieTypeState = {
            'Audio'       : '$',
            'Video'       : '%',
            'Audio/Video' : '!'
        }

        Input = int(qualifier['Input'])
        Output = qualifier['Output']
        TieType = qualifier['Tie Type']

        if Output == 'All':
            Output = 0
        else:
            Output = int(qualifier['Output'])

        if Output < 0 or Output > self.OutputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif Input < 0 or Input > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            if Output == 0:
                for o in range(1, self.OutputSize + 1):
                    cmdStr = '{0}*{1}{2}'.format(Input, o, TieTypeState[TieType])
                    self.__SetHelper('MatrixTieCommand', cmdStr, value, qualifier)
            else:
                MatrixTieCommandCmdString = '{0}*{1}{2}'.format(Input, Output, TieTypeState[TieType])
                self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)

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
            'All': 'Audio/Video',
        }
        output = int(match.group(1))
        input_ = int(match.group(2))
        tietype = TieTypeStates[match.group(3).decode()]

        if tietype == 'Audio/Video':
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                if i != input_-1 and current_tie in ['Audio', 'Video', 'Audio/Video']:
                    self.matrix_tie_status[i][output-1] = 'Untied'
                elif i == input_-1:
                    self.matrix_tie_status[i][output-1] = 'Audio/Video'
        elif tietype in ['Video', 'Audio']:
            for i in range(self.InputSize):
                current_tie = self.matrix_tie_status[i][output-1]
                opTag = 'Audio' if tietype == 'Video' else 'Video'
                if i == input_-1:
                    if current_tie == opTag or current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[i][output-1] = tietype
                elif input_ == 0 or i != input_-1:
                    if current_tie == tietype:
                        self.matrix_tie_status[i][output-1] = 'Untied'
                    elif current_tie == 'Audio/Video':
                        self.matrix_tie_status[i][output-1] = opTag

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):
        TieTypeStates = {
            'Aud': 'Audio',
            'Vid': 'Video',
            'RGB': 'Video',
            'All': 'Audio/Video',
        }
        new_input = int(match.group(4))
        tietype = TieTypeStates[match.group(5).decode()]

        if tietype in ['Audio', 'Video']:
            op_tie_type = 'Audio' if tietype == 'Video' else 'Video'
            for output in range(self.OutputSize):
                for input_ in range(self.InputSize):
                    if input_ == new_input-1:
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
                    if input_ == new_input-1:
                        self.matrix_tie_status[input_][output] = 'Audio/Video'
                    else:
                        self.matrix_tie_status[input_][output] = 'Untied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):
        if 0 <= int(value) <= 32:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):
        if 0 <= int(value) <= 32:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.__SetHelper('RefreshMatrix', '\x1B0*1*1VC\r', value, qualifier)# Update Video Status
        self.__SetHelper('RefreshMatrix', '\x1B0*1*2VC\r', value, qualifier)# Update Audio Status


    def SetVideoMute(self, value, qualifier):
        VideoMuteState = {
            'On'  : '1',
            'Off' : '0'
        }

        channel = int(qualifier['Output'])
        if channel < 1 or channel > self.OutputSize:
            self.Discard('Invalid Command for SetVideoMute')
        else:
            VideoMuteCmdString = '{0}*{1}B'.format(channel, VideoMuteState[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        channel = qualifier['Output']
        VideoMuteCmdString = '{0}B'.format(channel)
        self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteState = {
            '1' : 'On',
            '0' : 'Off'
        }

        value = VideoMuteState[match.group(2).decode()]
        self.WriteStatus('VideoMute', value, {'Output' : match.group(1).decode()})

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
        self.counter = 0

        DEVICE_ERROR_CODES = {
            '01' : 'Invalid input number (too large)',
            '10' : 'Invalid command',
            '11' : 'Invalid preset number',
            '12' : 'Invalid output number (too large)',
            '13' : 'Invalid value (out of range)',
            '14' : 'Command not available for this configuration',
            '17' : 'System timed out',
            '22' : 'Busy',
        }

        value = match.group(1).decode()
        self.Error([DEVICE_ERROR_CODES[value]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

    def extr_15_1299_1212_VGA_A(self):
        self.InputSize = 12
        self.OutputSize = 12

    def extr_15_1299_128_VGA_A(self):
        self.InputSize = 12
        self.OutputSize = 8

    def extr_15_1299_168_VGA_A(self):
        self.InputSize = 16
        self.OutputSize = 8

    def extr_15_1299_1616_VGA_A(self):
        self.InputSize = 16
        self.OutputSize = 16

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

        #check incoming data if it matched any expected data from device module
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

