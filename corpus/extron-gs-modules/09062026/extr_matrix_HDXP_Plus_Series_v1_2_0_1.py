from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'HDXP Plus 1616': self.extr_15_135_1616,
            'HDXP Plus 3232': self.extr_15_135_3232,
            'HDXP Plus 3216': self.extr_15_135_3216,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},


            'ExecutiveMode': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        self.lastInputSignalStatusUpdate = 0
        self.refresh_matrix = False
        self.devicePassword = 'extron'

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'(?:Out(\d+) In(\d+) (All|Vid|RGB))|(?:In(\d+) (All|Vid|RGB))\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Vmt(\d+)\*([0-1])\r\n'), self.__MatchVideoMute, None)
            self.AddMatchString(compile(b'Exe([0-1])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(compile(b'Frq\d+\*(\d+)\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(compile(b'Qik\r\n'), self.__MatchQik, None)
            self.AddMatchString(compile(b'Rpr(\d+)\r\n'), self.__MatchRecallPreset, None)
            self.AddMatchString(compile(b'Vgp00 Out(\d+)\*([0-9 -]*)Vid\r\n'), self.__MatchAllMatrixTie, 'Video')
            self.AddMatchString(compile(b'Vmt[0-1]\r\n'), self.__MatchGlobalMute, None)
            self.AddMatchString(compile(b'Mut([0-1]+)\r\n'), self.__MatchMute, None)

            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

            if 'Serial' not in self.ConnectionType:
                self.AddMatchString(compile(b'Password:'), self.__MatchPassword, None)
                self.AddMatchString(compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
                self.AddMatchString(compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self, value, qualifier):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')


    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 2:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword(None, None)

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]
        self.SetRefreshMatrix('All', None)

    def __MatchGlobalMute(self, match, tag):
        self.UpdateMute(None, None)

    def UpdateMute(self, value, qualifier):
        self.__UpdateHelper('Mute', 'wVM|\r', value, qualifier)

    def __MatchMute(self, match, tag):
        stat = match.group(1).decode()
        output = 1
        for i in stat:
            if i == '0':
                self.WriteStatus('VideoMute', 'Off', {'Output': str(output)})
            elif i == '1':
                self.WriteStatus('VideoMute', 'On', {'Output': str(output)})
            output += 1

    def __MatchQik(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def __MatchRecallPreset(self, match, tag):
        self.UpdateAllMatrixTie(None, None)

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie(None, None)

    def UpdateAllMatrixTie(self, value, qualifier):

        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(self.OutputSize)] for _ in range(self.InputSize)]

        self.__UpdateHelper('RefreshMatrix', 'w0*1*1VC\r', value, qualifier)
        if self.OutputSize > 16:
            self.__UpdateHelper('RefreshMatrix', 'w0*17*1VC\r', value, qualifier)
        if self.OutputSize > 32:
            self.__UpdateHelper('RefreshMatrix', 'w0*33*1VC\r', value, qualifier)

    def InputTieStatusHelper(self, tie, output=None):

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.OutputSize)

        for input_ in range(self.InputSize):
            for output in output_range:

                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Video':
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1)})
                    VideoList.add(output)

        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1)})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        counter_max = 16 if self.refresh_matrix else self.OutputSize

        for i in input_list:

            self.video_status_counter += 1
            if i != '--':
                if i != '00':
                    self.matrix_tie_status[int(i) - 1][int(current_output - 1)] = tag
                current_output += 1

        if self.video_status_counter == counter_max:
            self.refresh_matrix = False
            self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1',
            'Off': '0'
        }
        self.__SetHelper('ExecutiveMode', '{0}x'.format(ExecutiveModeState[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'x', value, qualifier)

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeName = {
            b'1': 'On',
            b'0': 'Off',
        }
        self.WriteStatus('ExecutiveMode', ExecutiveModeName[match.group(1)], None)

    def SetGlobalVideoMute(self, value, qualifier):
        VideoMuteState = {
            'On': '1',
            'Off': '0',
        }

        self.__SetHelper('GlobalVideoMute', '{0}*b'.format(VideoMuteState[value]), value, qualifier)

    def UpdateInputSignalStatus(self, value, qualifier):
        self.__UpdateHelper('InputSignalStatus', '0LS', value, qualifier)
        
    def __MatchInputSignalStatus(self, match, qualifier):

        InputSignalStatusStatus = {
            '1': 'Active',
            '0': 'Not Active'
        }

        signal = match.group(1).decode()
        inputNumber = 1
        for inputVal in signal:
            self.WriteStatus('InputSignalStatus', InputSignalStatusStatus[inputVal], {'Input': str(inputNumber)})
            inputNumber += 1

    def SetMatrixTieCommand(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if 'All' in qualifier['Output']:
            output = 'All'
        else:
            output = int(qualifier['Output'])

        if inputVal < 0 or inputVal > self.InputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        elif output == 'All':
            self.__SetHelper('MatrixTieCommand', '{0}*&'.format(inputVal), inputVal, qualifier)
            self.SetRefreshMatrix('All', None)
        elif output <= 0 or output > self.OutputSize:
            self.Discard('Invalid Command for SetMatrixTieCommand')
        else:
            self.__SetHelper('MatrixTieCommand', '{0}*{1}&'.format(inputVal, output), inputVal, qualifier)

    def __MatchOutputTieStatus(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):

        output = int(match.group(1))
        input_ = int(match.group(2))

        for i in range(self.InputSize):
            current_tie = self.matrix_tie_status[i][output - 1]
            if i == input_ - 1:
                self.matrix_tie_status[i][output - 1] = 'Video'
            elif input_ == 0 or i != input_ - 1:
                if current_tie == 'Video':
                    self.matrix_tie_status[i][output - 1] = 'Untied'

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):

        new_input = int(match.group(4))
        for output in range(self.OutputSize):
            for input_ in range(self.InputSize):
                if input_ == new_input - 1:
                    self.matrix_tie_status[input_][output] = 'Video'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetRecall', '{0}.'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 32:
            self.__SetHelper('PresetSave', '{0},'.format(value), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetRefreshMatrix(self, value, qualifier):

        state = {
            '1 - 16': 'w0*1*1VC\r',
            '17 - 32': 'w0*17*1VC\r'
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie(value, qualifier)
        else:
            self.refresh_matrix = True
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', state[value], value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1',
        }
        channel = qualifier['Output']
        if 1 <= int(channel) <= self.OutputSize:

            self.__SetHelper('VideoMute', '{0}*{1}B'.format(channel, VideoMuteState[value]), value, qualifier)

        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):
        self.UpdateMute(None, None)

    def __MatchVideoMute(self, match, qualifier):
        VideoMuteName = {
            b'0': 'Off',
            b'1': 'On',

        }

        self.WriteStatus('VideoMute', VideoMuteName[match.group(2)], {self.Commands['VideoMute']['Parameters'][0]: str(int(match.group(1)))})

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
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
            if self.Unidirectional == 'True':
                self.Discard('Inappropriate Command ' + command)
            else:
                if self.VerboseDisabled:
                    @Wait(1)
                    def SendVerbose():
                        self.Send('w3cv\r\n')
                        self.Send(commandstring)
                else:
                    self.Send(commandstring)
        else:
            self.Discard('Inappropriate Command ' + command)

    def __MatchErrors(self, match, tag):

        DEVICE_ERROR_CODES = {

            '01': 'Invalid input number (too large)',
            '10': 'Invalid Command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid value (out of range)',
            '14': 'Command not available for this configuration',
            '17': 'System timed out',
            '21': 'Invalid room number',
            '24': 'Privilege violation',
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

        if 'Serial' not in self.ConnectionType:
            self.Authenticated = 'Not Needed'
            self.PasswdPromptCount = 0

        self.VerboseDisabled = True
        self.refresh_matrix = False

    def extr_15_135_1616(self):

        self.InputSize = 16
        self.OutputSize = 16

    def extr_15_135_3232(self):

        self.InputSize = 32
        self.OutputSize = 32

    def extr_15_135_3216(self):

        self.InputSize = 32
        self.OutputSize = 16

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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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
