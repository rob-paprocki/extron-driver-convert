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
        self.devicePassword = 'extron'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ContactClosureInput': {'Parameters': ['Input'], 'Status': {}},
            'FirmwareVersion': {'Status': {}},
            'IRCommand': {'Parameters': ['IR Port', 'IR Function', 'IR Playback'], 'Status': {}},
            'PulseRelay': {'Parameters': ['Pulse Time', 'Relay Port'], 'Status': {}},
            'RelayPort': {'Parameters': ['Relay Port'], 'Status': {}},
        }

        self.VerboseDisabled = True
        self.PasswdPromptCount = 0
        self.Authenticated = 'Not Needed'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Cpn([1-4]) Sio(0|1)\r\n'), self.__MatchContactClosureInput, None)
            self.AddMatchString(re.compile(b'(\d\.\d\d)\r\n'), self.__MatchFirmwareVersion, None)
            self.AddMatchString(re.compile(b'Irs(00[0-4]),(0[0-9]{2}),([0-9]{3}),(00[0-2])\r\n'), self.__MatchIRCommand, None)
            self.AddMatchString(re.compile(b'Cpn([1-4]) Rly(0|1)\r\n'), self.__MatchRelayPort, None)
            self.AddMatchString(re.compile(b'E([1|2|3][0-9])\r\n'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)  # Vrb3\r\n
            self.AddMatchString(re.compile(b'Password:'), self.__MatchPassword, None)
            self.AddMatchString(re.compile(b'Login Administrator\r\n'), self.__MatchLoginAdmin, None)
            self.AddMatchString(re.compile(b'Login User\r\n'), self.__MatchLoginUser, None)

    def SetPassword(self):
        if self.devicePassword:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def __MatchPassword(self, match, tag):
        self.PasswdPromptCount += 1
        if self.PasswdPromptCount > 1:
            self.Error(['Log in failed. Please supply proper Admin password'])
            self.Authenticated = 'None'
        else:
            self.SetPassword()

    def __MatchLoginAdmin(self, match, tag):

        self.Authenticated = 'Admin'
        self.PasswdPromptCount = 0
        self.SetVerbose()

    def __MatchLoginUser(self, match, tag):

        self.Authenticated = 'User'
        self.PasswdPromptCount = 0
        self.Error(['Logged in as User. May have limited functionality.'])
        self.SetVerbose()

    def SetVerbose(self):
        self.Send('w3cv\r')

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def UpdateContactClosureInput(self, value, qualifier):

        InputQualifierStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        Input = InputQualifierStates[qualifier['Input']]

        ContactClosureInputCmdString = '{0}]'.format(Input)
        self.__UpdateHelper('ContactClosureInput', ContactClosureInputCmdString, value, qualifier)

    def __MatchContactClosureInput(self, match, tag):

        InputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ContactClosureStates = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = InputStates[match.group(1).decode()]
        value = ContactClosureStates[match.group(2).decode()]
        self.WriteStatus('ContactClosureInput', value, {'Input': qualifier})

    def UpdateFirmwareVersion(self, value, qualifier):

        if self.VerboseDisabled and self.Authenticated in ['Admin', 'User', 'Not Needed']:
            self.Send('w3cv\r\n')

        FirmwareVersionCmdString = 'Q'
        self.__UpdateHelper('FirmwareVersion', FirmwareVersionCmdString, value, qualifier)

    def __MatchFirmwareVersion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('FirmwareVersion', value, None)

    def SetIRCommand(self, value, qualifier):

        IRPlaybackStates = {
            'Play Once': '0',
            'Play Continuously': '1',
            'Stop': '2'
        }

        IRPortStateValues = {
            'IR Port 1': '01',
            'IR Port 2': '02',
            'IR Port 3': '03',
            'IR Port 4': '04',
            'All Ports Reserved': '00'
        }

        IRPort = IRPortStateValues[qualifier['IR Port']]
        IRFunction = qualifier['IR Function']
        IRPlayback = IRPlaybackStates[qualifier['IR Playback']]

        if 0 <= int(value) <= 99 and 1 <= int(IRFunction) <= 137:
            IRCommandCmdString = 'W{0},{1},{2},{3}IR\r\n'.format(IRPort, value, IRFunction, IRPlayback)
            self.__SetHelper('IRCommand', IRCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIRCommand')

    def __MatchIRCommand(self, match, tag):

        IRPlaybackStates = {
            0: 'Play Once',
            1: 'Play Continuously',
            2: 'Stop'
        }

        IRPortStates = {
            1: 'IR Port 1',
            2: 'IR Port 2',
            3: 'IR Port 3',
            4: 'IR Port 4',
            0: 'All Ports Reserved'
        }

        IRPort = IRPortStates[int(match.group(1).decode())]
        value = str(int(match.group(2).decode()))
        IRFunction = str(int(match.group(3).decode()))
        IRPlayback = IRPlaybackStates[int(match.group(4).decode())]
        self.WriteStatus('IRCommand', value, {'IR Port': IRPort, 'IR Function': IRFunction, 'IR Playback': IRPlayback})

    def SetPulseRelay(self, value, qualifier):

        PulseTime = qualifier['Pulse Time']
        RelayPort = qualifier['Relay Port']

        if 20 <= int(PulseTime) <= 1310700 and 1 <= int(RelayPort) <= 4:
            PulseTime = int(int(PulseTime) / 20)
            RelayPortCmdString = '{0}*3*{1}O\r\n'.format(RelayPort, PulseTime)
            self.__SetHelper('RelayPort', RelayPortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPulseRelay')

    def SetRelayPort(self, value, qualifier):

        RelayPort = qualifier['Relay Port']

        RelayPortStateValues = {
            'Off': '*0O',
            'On': '*1O'
        }

        if 1 <= int(RelayPort) <= 4:
            RelayPortCmdString = '{0}{1}'.format(RelayPort, RelayPortStateValues[value])
            self.__SetHelper('RelayPort', RelayPortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelayPort')

    def UpdateRelayPort(self, value, qualifier):

        RelayPort = qualifier['Relay Port']
        if 1 <= int(RelayPort) <= 4:
            RelayPortCmdString = '{0}O'.format(RelayPort)
            self.__UpdateHelper('RelayPort', RelayPortCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRelayPort')

    def __MatchRelayPort(self, match, tag):

        RelayPortStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = match.group(1).decode()
        value = RelayPortStateValues[match.group(2).decode()]
        self.WriteStatus('RelayPort', value, {'Relay Port': qualifier})

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

        if self.Authenticated in ['User', 'Admin', 'Not Needed']:
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
        else:
            self.Discard('Authentication Invalid Command {}'.format(command))

            

    def __MatchError(self, match, tag):
        self.counter = 0

        ErrorStates = {
            'E10\r\n': 'Invalid command',
            'E12\r\n': 'Invalid port number',
            'E13\r\n': 'Invalid value or parameter',
            'E14\r\n': 'Not valid for this configuration',
            'E17\r\n': 'System timed out',
            'E22\r\n': 'Busy',
            'E24\r\n': 'Privilege violation',
            'E25\r\n': 'Device is not present',
            'E26\r\n': 'Maximum number of connections has been exceeded',
            'E27\r\n': 'Invalid event number',
            'E28\r\n': 'Bad filename or file not found',
            'E31\r\n': 'Attempt to break port pass-through when not set'
        }

        value = ErrorStates[match.group(0).decode()]
        self.Error([value])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.Authenticated = 'Not Needed'
        self.PasswdPromptCount = 0
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

    def MissingCredentialsLog(self, credential_type):
        if isinstance(self, EthernetClientInterface):
            port_info = 'IP Address: {0}:{1}'.format(self.IPAddress, self.IPPort)
        elif isinstance(self, SerialInterface):
            port_info = 'Host Alias: {0}\r\nPort: {1}'.format(self.Host.DeviceAlias, self.Port)
        else:
            return
        ProgramLog("{0} module received a request from the device for a {1}, "
                   "but device{1} was not provided.\n Please provide a device{1} "
                   "and attempt again.\n Ex: dvInterface.device{1} = '{1}'\n Please "
                   "review the communication sheet.\n {2}"
                   .format(__name__, credential_type, port_info), 'warning')


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
