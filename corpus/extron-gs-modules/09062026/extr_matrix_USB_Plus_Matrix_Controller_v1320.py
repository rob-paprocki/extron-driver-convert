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
        self.__receiveBuffer = b''
        self.__maxBufferSize = 2048
        self.__matchStringDict = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BreakAllMatrixTies': {'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'RefreshMatrix': {'Status': {}},
            'USBExtenderConnectionStatus': {'Parameters': ['Channel', 'Type'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(b'Ver\d+\*(.*)\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(compile(b'Out(\d+) In(\d+) ALL\r\n'), self.__MatchOutputTieStatus, None)
            self.AddMatchString(compile(b'Vgp00 Out[\d]?(\d{2})\*([0-9 -]*) Vid\r\n'), self.__MatchAllMatrixTie, 'Tied')
            self.AddMatchString(compile(b'CONN([OI])([012-]{1,63})\r\n'), self.__MatchUSBExtenderConnectionStatus, None)
            self.AddMatchString(compile(b'E(\d+)\r\n'), self.__MatchError, None)

        self.refresh_matrix = False
        Wait(3, self.UpdateAllMatrixTie)
        self.UpdateAllMatrixTieWait = Wait(0.5, self.SendUpdateMatrixCmd)
        self.UpdateAllMatrixTieWait.Cancel()
    
    def SendUpdateMatrixCmd(self):
        try:
            cmd = next(self.UpdateAllMatrixTieIter)
            self.Send(cmd)
            self.UpdateAllMatrixTieWait.Restart()
        except StopIteration:
            pass

    def UpdateAllMatrixTie(self):

        self.video_status_counter = 0
        self.matrix_tie_status = [['Untied' for _ in range(63)] for _ in range(63)]
        self.UpdateAllMatrixTieIter = iter(['w0*1*1vc\r', 'w0*17*1vc\r', 'w0*33*1vc\r', 'w0*48*1vc\r'])
        self.SendUpdateMatrixCmd()

    def UpdateInputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie()

    def UpdateOutputTieStatus(self, value, qualifier):
        self.UpdateAllMatrixTie()

    def InputTieStatusHelper(self, tie, output=None):

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(63)
        for input_ in range(63):
            for output in output_range:
                self.WriteStatus('InputTieStatus', self.matrix_tie_status[input_][output], {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):

        VideoList = set()

        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(63)
        for input_ in range(63):
            for output in output_range:
                tietype = self.matrix_tie_status[input_][output]
                if tietype == 'Tied':
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1)})
                    VideoList.add(output)
        for o in output_range:
            if o not in VideoList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1)})

    def __MatchAllMatrixTie(self, match, tag):

        current_output = int(match.group(1))
        input_list = match.group(2).decode().split()

        counter_max = 16 if self.refresh_matrix else 64

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

    def SetBreakAllMatrixTies(self, value, qualifier):

        BreakAllMatrixTiesCmdString = '0*!'
        self.__SetHelper('BreakAllMatrixTies', BreakAllMatrixTiesCmdString, value, qualifier)

    def UpdateFirmwareVersion(self, value, qualifier):

        FirmwareVersionCmdString = 'q'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def __MatchOutputTieStatus(self, match, qualifier):

        if match.group(1):
            self.__MatchIndividualTie(match, None)
        else:
            self.__MatchAllTie(match, None)

    def __MatchIndividualTie(self, match, qualifier):

        output = int(match.group(1))
        input_ = int(match.group(2))

        for i in range(63):
            current_tie = self.matrix_tie_status[i][output - 1]
            if i == input_ - 1:
                self.matrix_tie_status[i][output - 1] = 'Tied'
            elif input_ == 0 or i != input_ - 1:
                if current_tie == 'Tied':
                    self.matrix_tie_status[i][output - 1] = 'Untied'

        self.OutputTieStatusHelper('Individual', output)
        self.InputTieStatusHelper('Individual', output)

    def __MatchAllTie(self, match, qualifier):

        new_input = int(match.group(4))
        for output in range(63):
            for input_ in range(63):
                if input_ == new_input - 1:
                    self.matrix_tie_status[input_][output] = 'Tied'

        self.InputTieStatusHelper('All')
        self.OutputTieStatusHelper('All')

    def SetMatrixTieCommand(self, value, qualifier):

        if 0 <= int(qualifier['Input']) <= 63 and 1 <= int(qualifier['Output']) <= 63:
            MatrixTieCommandCmdString = '{0}*{1}!\r\n'.format(qualifier['Input'], qualifier['Output'])
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def SetRefreshMatrix(self, value, qualifier):

        state = {
            '1 - 16': 'w0*1*1vc\r',
            '17 - 32': 'w0*17*1vc\r',
            '33 - 47': 'w0*33*1vc\r',
            '48 - 63': 'w0*48*1vc\r'
        }

        if not value or value == 'All':
            self.UpdateAllMatrixTie()
        else:
            self.refresh_matrix = True
            self.video_status_counter = 0
            self.__SetHelper('RefreshMatrix', state[value], value, qualifier)

    def UpdateUSBExtenderConnectionStatus(self, value, qualifier):

        USBExtenderConnectionStatusCmdString = 'WCONNO\rWCONNI\r'
        self.__UpdateHelper('USBExtenderConnectionStatus', USBExtenderConnectionStatusCmdString, value, qualifier)

    def __MatchUSBExtenderConnectionStatus(self, match, tag):

        TypeStates = {
            'I': 'Input',
            'O': 'Output',
        }

        ValueStateValues = {
            '1': 'Online',
            '0': 'Offline',
            '2': 'Unknown Device',
            '-': 'Not Configured'
        }

        _type = TypeStates[match.group(1).decode()]
        for i in range(0, len(match.group(2).decode())):
            value = ValueStateValues[match.group(2).decode()[i]]
            self.WriteStatus('USBExtenderConnectionStatus', value, {'Type': _type, 'Channel': str(i + 1)})

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number',
            '10': 'Invalid command',
            '12': 'Invalid output number',
            '13': 'Invalid value',
            '14': 'Invalid command for this configuration',
            '95': 'Configuration file does not exist',
            '96': 'Transmitter is offline',
            '97': 'Receiver is offline',
            '98': 'Maximum number of receivers are tied to the transmitter',
            '99': 'No configuration loaded',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error(['Error occurred: {0}'.format(DEVICE_ERROR_CODES[value])])
        else:
            self.Error(['Unrecognized error code: ' + match.group(0).decode()])

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

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.UpdateAllMatrixTie()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.refresh_matrix = False

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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
        except BaseException:
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
