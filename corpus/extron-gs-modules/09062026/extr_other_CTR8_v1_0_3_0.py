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
        self.VerboseDisabled = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AVMute': {'Parameters': ['LED'], 'Status': {}},
            'AVMuteStatus': {'Status': {}},
            'COMPortBaudRate': {'Status': {}},
            'ContactClosureInput': {'Parameters': ['Contact'], 'Status': {}},
            'Input': {'Status': {}},
            'LEDStatus': {'Status': {}},
            'Mode': {'Status': {}},
            'Tally': {'Parameters': ['Tally'], 'Status': {}},
        }

        self.lastTallyUpdate = 0
        self.lastContactUpdate = 0
        self.lastModeUpdate = 'Default'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Mutm([0-3])\*([0-2])\r\n'), self.__MatchAVMuteStatus, None)
            self.AddMatchString(re.compile(b'(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n'),
                                self.__MatchCOMPortBaudRate, None)
            self.AddMatchString(re.compile(b'Chn ([0-8])\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Sts([1-8])\*(0|1)\r\n'), self.__MatchContactClosureInput, None)
            self.AddMatchString(re.compile(b'Mode(0|1)\r\n'), self.__MatchMode, None)
            self.AddMatchString(re.compile(b'Taly([1-8])\*([01])\r\n'), self.__MatchTally, None)
            self.AddMatchString(re.compile(b'E(\d+)\r\n'), self.__MatchErrors, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

        self.Regex = {
            'AVMuteStatus': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?([0-3]\*[0-2]\r\n)|E\d+\r\n'),
            'COMPortBaudRate': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?((9600|19200|38400|57600),[nN],8,1\r\n)|E\d+\r\n'),
            'ContactClosureInput': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?([01]{8}\r\n)|E\d+\r\n'),
            'Input': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?([0-8]\r\n)|E\d+\r\n'),
            'Mode': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?([01]\r\n)|E\d+\r\n'),
            'Tally': re.compile(
                b'(Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?([01]{8}\r\n)|E\d+\r\n')
        }

        self.RegexPattern = re.compile(
            b'(?P<matchstring>Mutm([0-3])\*([0-2])\r\n|(Cpn2 Ccp)?(9600|19200|38400|57600),[nN],8,1\r\n|Chn ([0-8])\r\n|Sts([1-8])\*(0|1)\r\n|Mode(0|1)\r\n|Taly([1-8])\*([01])\r\n)?(?P<mode>[0-3]\*[0-2]\r\n|[0-8]+\r\n|(9600|19200|38400|57600),[nN],8,1\r\n)')

    def UpdateModeFunctions(self, value):

        if self.lastModeUpdate != value:
            if value == 'Default':
                self.UpdateAVMuteStatus(value, None)
                self.UpdateInput(value, None)
            elif value == 'Advanced':
                self.UpdateContactClosureInput(value, {'Contact': '1'})
                self.UpdateTally(value, {'Tally': '1'})
        self.lastModeUpdate = value

    def SetAVMute(self, value, qualifier):

        AVMuteValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2',
            'Mode 3': '3'
        }

        LEDValues = {
            'Always On': '0',
            'Off When Muted': '1',
            'Blink When Muted': '2'
        }

        if self.ReadStatus('Mode', None) == 'Default' or self.Unidirectional == 'True':
            LEDSelect = qualifier['LED']
            if (AVMuteValues[value] == '0') and (LEDValues[LEDSelect] != '0'):
                self.Discard('Invalid Command for SetAVMute')
            else:
                AVMuteCmdString = 'w{0}*{1}MUTM\r'.format(AVMuteValues[value], LEDValues[LEDSelect])
                self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def UpdateAVMuteStatus(self, value, qualifier):

        AVMuteNames = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3'
        }

        LEDNames = {
            '0': 'Always On',
            '1': 'Off When Muted',
            '2': 'Blink When Muted'
        }

        AVMuteStatusCmdString = 'wMUTM\r'
        if self.ReadStatus('Mode', None) == 'Default':
            res = self.__UpdateHelper('AVMuteStatus', AVMuteStatusCmdString, value, qualifier)
            if res:
                try:
                    AVMuteValue = AVMuteNames[res[0]]
                    LEDStatusValue = LEDNames[res[2]]
                    self.WriteStatus('AVMuteStatus', AVMuteValue, None)
                    self.WriteStatus('LEDStatus', LEDStatusValue, None)
                except (KeyError, IndexError):
                    self.Error(['AVMuteStatus: Invalid/unexpected response'])

    def __MatchAVMuteStatus(self, match, tag):

        AVMuteNames = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2',
            '3': 'Mode 3'
        }

        LEDNames = {
            '0': 'Always On',
            '1': 'Off When Muted',
            '2': 'Blink When Muted'
        }

        AVMuteValue = AVMuteNames[match.group(1).decode()]
        LEDValue = LEDNames[match.group(2).decode()]
        self.WriteStatus('AVMuteStatus', AVMuteValue, None)
        self.WriteStatus('LEDStatus', LEDValue, None)

    def SetCOMPortBaudRate(self, value, qualifier):

        ValueStateValues = {
            '9600': '9600',
            '19200': '19200',
            '38400': '38400',
            '57600': '57600'
        }

        COMPortBaudRateCmdString = 'w2*{0},n,8,1CP\r'.format(ValueStateValues[value])
        self.__SetHelper('COMPortBaudRate', COMPortBaudRateCmdString, value, qualifier)

    def UpdateCOMPortBaudRate(self, value, qualifier):

        COMPortBaudRateCmdString = 'w2CP\r'
        self.__UpdateHelper('COMPortBaudRate', COMPortBaudRateCmdString, value, qualifier)

    def __MatchCOMPortBaudRate(self, match, tag):

        ValueStateValues = {
            '9600': '9600',
            '19200': '19200',
            '38400': '38400',
            '57600': '57600'
        }

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('COMPortBaudRate', value, None)

    def UpdateContactClosureInput(self, value, qualifier):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Closed'
        }

        if self.ReadStatus('Mode', None) == 'Advanced':
            ContactClosureInputCmdString = 'S'
            res = self.__UpdateHelper('ContactClosureInput', ContactClosureInputCmdString, value, qualifier)
            if res:
                try:
                    for x in range(1, 9):
                        qualifier = {'Contact': str(x)}
                        value = ValueStateValues[res[x - 1]]
                        self.WriteStatus('ContactClosureInput', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['ContactClosureInput: Invalid/unexpected response'])

    def __MatchContactClosureInput(self, match, tag):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Closed'
        }

        ContactStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        qualifier = {}
        qualifier['Contact'] = ContactStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ContactClosureInput', value, qualifier)

    def SetInput(self, value, qualifier):

        if self.ReadStatus('Mode', None) == 'Default' or self.Unidirectional == 'True':
            if 0 <= int(value) <= 8:
                InputCmdString = '{0}!'.format(value)
                self.__SetHelper('Input', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        if self.ReadStatus('Mode', None) == 'Default':
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    value = res.strip()
                    self.WriteStatus('Input', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])

    def __MatchInput(self, match, tag):

        InputValue = match.group(1).decode().strip()
        self.WriteStatus('Input', InputValue, None)

    def UpdateLEDStatus(self, value, qualifier):

        self.UpdateAVMuteStatus(value, qualifier)

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Default': '0',
            'Advanced': '1'
        }

        ModeCmdString = 'w{0}MODE\r'.format(ValueStateValues[value])
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def UpdateMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Default',
            '1': 'Advanced'
        }

        ModeCmdString = 'wMODE\r'
        res = self.__UpdateHelper('Mode', ModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Mode', value, qualifier)
                self.UpdateModeFunctions(value)
            except (KeyError, IndexError):
                self.Error(['Mode: Invalid/unexpected response'])

    def __MatchMode(self, match, tag):

        ValueStateValues = {
            '0': 'Default',
            '1': 'Advanced'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mode', value, None)

    def SetTally(self, value, qualifier):

        ValueStateValues = {
            'Open': '0',
            'Close': '1'
        }

        TallyStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        if self.ReadStatus('Mode', None) == 'Advanced' or self.Unidirectional == 'True':
            TallyCmdString = 'w{0}*{1}TALY\r'.format(TallyStates[qualifier['Tally']], ValueStateValues[value])
            self.__SetHelper('Tally', TallyCmdString, value, qualifier)

    def UpdateTally(self, value, qualifier):

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        if self.ReadStatus('Mode', None) == 'Advanced':
            TallyCmdString = 'wTALY\r'
            res = self.__UpdateHelper('Tally', TallyCmdString, value, qualifier)
            if res:
                try:
                    for x in range(1, 9):
                        qualifier = {'Tally': str(x)}
                        value = ValueStateValues[res[x - 1]]
                        self.WriteStatus('Tally', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Tally: Invalid/unexpected response'])

    def __MatchTally(self, match, tag):

        TallyStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8'
        }

        ValueStateValues = {
            '0': 'Open',
            '1': 'Close'
        }

        qualifier = {}
        qualifier['Tally'] = TallyStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Tally', value, qualifier)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def MatchStrings(self, string):

        match = re.match(self.RegexPattern, string)
        if 'Mutm' in string:
            self.__MatchAVMuteStatus(match, None)
        elif '8,1' in string:
            self.__MatchCOMPortBaudRate(match, None)
        elif 'Chn' in string:
            self.__MatchInput(match, None)
        elif 'Sts' in string:
            self.__MatchContactClosureInput(match, None)
        elif 'Mode' in string:
            self.__MatchMode(match, None)
        elif 'Taly' in string:
            self.__MatchTally(match, None)
        else:
            return

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number (too large)',
            'E10': 'Invalid command',
            'E11': 'Invalid preset number',
            'E12': 'Invalid port number',
            'E13': 'Invalid parameter',
            'E14': 'Command not available for this configuration',
            'E17': 'System timed out',
            'E22': 'Busy',
            'E24': 'Privilege violation',
            'E25': 'Device not present',
            'E26': 'Maximum number of connections exceeded',
            'E27': 'Invalid event number',
            'E28': 'Bad filename or file not found',
            'E30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            'E31': 'Attempt to break port pass-through when it has not been set',
            'E32': 'Incorrect V-chip password'
        }

        if response:
            try:
                match = re.match(self.RegexPattern, response)
                if response in DEVICE_ERROR_CODES:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, response, DEVICE_ERROR_CODES[response])
                    self.Error([errorString])
                    response = b''
                elif match.group('matchstring'):
                    self.MatchStrings(matchstring)
                    response = match.group('mode')
            except AttributeError:
                self.Error(['{}: Invalid/unexpected response'.format(sourceCmdName)])
        return response.decode()

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if command == 'COMPortBaudRate':
                self.Send(commandstring)
            else:

                if self.initializationChk:
                    self.OnConnected()
                    self.initializationChk = False

                self.counter = self.counter + 1
                if self.counter > self.connectionCounter and self.connectionFlag:
                    self.OnDisconnected()

                res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex[command])
                if not res:
                    if 'Mode' == command:
                        return ''
                else:
                    return self.__CheckResponseForErrors(command, res)

    def __MatchErrors(self, match, qualifier):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input number (too large)',
            '10': 'Invalid command',
            '11': 'Invalid preset number',
            '12': 'Invalid port number',
            '13': 'Invalid parameter',
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

        errorString = DEVICE_ERROR_CODES.get(match.group(1).decode(), 'Unknown error: ' + match.group(0).decode())
        self.Error([errorString])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastTallyUpdate = 0
        self.lastContactUpdate = 0
        self.VerboseDisabled = True
        self.lastModeUpdate = 'Default'

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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

