from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog

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
        self.IOSize = 288

        self.Models = {
            'Smart Videohub 12x12': self.blkmd_15_926_12,
            'Smart Videohub CleanSwitch 12x12': self.blkmd_15_926_12,
            'Micro Videohub': self.blkmd_15_926_16,
            'Smart Videohub 20x20': self.blkmd_15_926_20,
            'Universal Videohub 288': self.blkmd_15_926_288,
            'Smart Videohub 40x40': self.blkmd_15_926_40,
            'Compact Videohub': self.blkmd_15_926_40,
            'Smart Videohub 12G 40x40': self.blkmd_15_926_40,
            'Universal Videohub 72': self.blkmd_15_926_72,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'HeartBeat': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixRefresh': {'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            if 'Serial' in self.ConnectionType:
                self.tie_counter = 0
                self.AddMatchString(re.compile(b'[SV]:0(?P<output>[0-9A-Fa-f]{1,3}),(?P<input>[0-9A-Fa-f]{1,3})\r?\n'), self.__MatchOutputTieStatus, None)  # Also handles Input Tie Status
            else:
                self.getRegex = re.compile(b'(?:NAK\r?\n|VIDEO OUTPUT ROUTING:\n(?P<routes>[ \d\n]+)\n)')
                self.AddMatchString(re.compile(rb'VIDEO OUTPUT ROUTING:\n(\d?\d) (\d?\d)\n\n'), self.__MatchMatrixTieStatus, None)
                self.AddMatchString(re.compile(b'NAK\r?\n'), self.__MatchError, None)

        self.matrix_tie_status = [['Untied' for _ in range(self.IOSize)] for _ in range(self.IOSize)]

    def SetEnableStatusReporting(self, value, qualifier):

        self.Send('@ ?\r')

    def UpdateHeartBeat(self, value, qualifier):

        if 'Serial' in self.ConnectionType:
            HeartBeatCmdString = '@ S?0\r'
            self.__UpdateHelper('HeartBeat', HeartBeatCmdString, value, qualifier)
        else:
            HeartBeatCmdString = 'VIDEO OUTPUT ROUTING:\r\n\r\n'
            res = self.__UpdateHelperSync('HeartBeat', HeartBeatCmdString, value, qualifier)
            if res:
                outputList = set()
                routeIter = re.finditer(r'(?P<output>\d{1,3}) (?P<input>\d{1,3})', res)
                for route in routeIter:
                    input_ = int(route.group('input'))
                    output_ = int(route.group('output'))
                    for i in range(self.IOSize):
                        current_tie = self.matrix_tie_status[i][output_]
                        if i != input_ and current_tie == 'Tied':
                            self.matrix_tie_status[i][output_] = 'Untied'
                        elif i == input_:
                            self.matrix_tie_status[input_][output_] = 'Tied'
                    outputList.add(output_)
                for o in range(self.IOSize):
                    if o not in outputList:
                        for i in range(self.IOSize):
                            current_tie = self.matrix_tie_status[i][o]
                            if current_tie == 'Tied':
                                self.matrix_tie_status[i][o] = 'Untied'
                if self.IOSize <= 16:
                    self.InputTieStatusHelper('All')
                self.OutputTieStatusHelper('All')

    def SetMatrixRefresh(self, value, qualifier):

        self.UpdateHeartBeat(None, None)

    def SetMatrixTieCommand(self, value, qualifier):

        input_ = int(qualifier['Input'])
        output_ = int(qualifier['Output'])
        if 1 <= input_ <= self.IOSize and 1 <= output_ <= self.IOSize:
            if 'Serial' in self.ConnectionType:
                MatrixTieCommandCmdString = '@ X:0/{0:01X},{1:01X}\r'.format(output_ - 1, input_ - 1)
            else:
                MatrixTieCommandCmdString = 'VIDEO OUTPUT ROUTING:\r\n{0} {1}\r\n\r\n'.format(output_ - 1, input_ - 1)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __MatchMatrixTieStatus(self, match, tag):

        output_ = int(match.group(1).decode()) + 1
        input_ = int(match.group(2).decode()) + 1
        if self.IOSize <= 16:
            self.WriteStatus('InputTieStatus', 'Tied', {'Input': str(input_), 'Output': str(output_)})
            for i in range(1, self.IOSize + 1):
                if i != input_:
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': str(i), 'Output': str(output_)})

        self.WriteStatus('OutputTieStatus', str(input_), {'Output': str(output_)})

    def __MatchOutputTieStatus(self, match, tag):

        self.tie_counter += 1
        input_ = int(match.group('input').decode(), 16)
        output_ = int(match.group('output').decode(), 16)
        for i in range(self.IOSize):
            current_tie = self.matrix_tie_status[i][output_]
            if i != input_ and current_tie == 'Tied':
                self.matrix_tie_status[i][output_] = 'Untied'
            elif i == input_:
                self.matrix_tie_status[input_][output_] = 'Tied'
        if self.tie_counter == self.IOSize:
            self.tie_counter = 0

            if self.IOSize <= 16:
                self.InputTieStatusHelper('All')
            self.OutputTieStatusHelper('All')

    def InputTieStatusHelper(self, tie, output=None):
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.IOSize)
        for input_ in range(self.IOSize):
            for output in output_range:
                value = self.matrix_tie_status[input_][output]
                self.WriteStatus('InputTieStatus', value, {'Input': str(input_ + 1), 'Output': str(output + 1)})

    def OutputTieStatusHelper(self, tie, output=None):
        TiedList = set()
        if tie == 'Individual':
            output_range = range(output - 1, output)
        else:
            output_range = range(self.IOSize)
        for input_ in range(self.IOSize):
            for output in output_range:
                tie_type = self.matrix_tie_status[input_][output]
                if tie_type == 'Tied':
                    self.WriteStatus('OutputTieStatus', str(input_ + 1), {'Output': str(output + 1)})
                    TiedList.add(output)
        for o in output_range:
            if o not in TiedList:
                self.WriteStatus('OutputTieStatus', '0', {'Output': str(o + 1)})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if 'NAK' in response:
            self.Error(['{0}: An error occurred.'.format(sourceCmdName)])
            response = ''
        return response

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

    def __UpdateHelperSync(self, command, commandstring, value, qualifier):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.getRegex)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

    def __MatchError(self, match, tag):

        self.counter = 0
        self.Error(['An error occurred.'])

    def OnConnected(self):

        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        if 'Serial' in self.ConnectionType:
            self.SetEnableStatusReporting(None, None)

    def OnDisconnected(self):

        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        if 'Serial' in self.ConnectionType:
            self.tie_counter = 0

        self.matrix_tie_status = [['Untied' for _ in range(self.IOSize)] for _ in range(self.IOSize)]

    def blkmd_15_926_12(self):
        self.IOSize = 12

    def blkmd_15_926_20(self):
        self.IOSize = 20

    def blkmd_15_926_40(self):
        self.IOSize = 40

    def blkmd_15_926_72(self):
        self.IOSize = 72

    def blkmd_15_926_288(self):
        self.IOSize = 288

    def blkmd_15_926_16(self):
        self.IOSize = 16

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

    def __ReceiveData(self, interface, data):
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0    # Start of possible good data

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
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