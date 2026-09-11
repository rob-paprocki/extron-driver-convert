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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DisplayMode': {'Parameters': ['Horizontal Position', 'Vertical Position'], 'Status': {}},
            'Input': {'Parameters': ['Horizontal Position', 'Vertical Position'], 'Status': {}},
            'Power': {'Parameters': ['Horizontal Position', 'Vertical Position'], 'Status': {}},
            'WallSize': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'done MyWall get DisplayMode (wall|\d+,\d+) (ActualSize|FitToScreen|AspectRatio|mixed|unknown)\r\n', re.I), self.__MatchDisplayMode, None)
            self.AddMatchString(re.compile(b'done MyWall get SelInput (wall|\d+,\d+) (DisplayPort[12]|HDMI[12]|mixed|unknown)\r\n', re.I), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'done MyWall get OpState (wall|\d+,\d+) (on|idle|mixed|unknown)\r\n', re.I), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'done MyWall get WallSize (\d+x\d+)\r\n', re.I), self.__MatchWallSize, None)
            self.AddMatchString(re.compile(b'error (syntax|not|incomplete|system)[ \S]+\r\n', re.I), self.__MatchError, None)

    def SetDisplayMode(self, value, qualifier):

        ValueStateValues = {
            'Actual Size': 'ActualSize',
            'Fit to Screen': 'FitToScreen',
            'Aspect Ratio': 'AspectRatio'
        }

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            DisplayModeCmdString = 'MyWall set DisplayMode {0} {1}\r\n'.format(device, ValueStateValues[value])
            self.__SetHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayMode')

    def UpdateDisplayMode(self, value, qualifier):

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            DisplayModeCmdString = 'MyWall get DisplayMode {}\r\n'.format(device)
            self.__UpdateHelper('DisplayMode', DisplayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateDisplayMode')

    def __MatchDisplayMode(self, match, tag):

        ValueStateValues = {
            'actualsize': 'Actual Size',
            'fittoscreen': 'Fit to Screen',
            'aspectratio': 'Aspect Ratio',
            'mixed': 'Mixed',
            'unknown': 'Unknown'
        }

        device = ['0', '0'] if match.group(1).decode() == 'wall' else match.group(1).decode().split(',')
        qualifier = {'Horizontal Position': int(device[0]), 'Vertical Position': int(device[1])}
        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('DisplayMode', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DisplayPort 1': 'DisplayPort1',
            'DisplayPort 2': 'DisplayPort2',
            'HDMI 1': 'HDMI1',
            'HDMI 2': 'HDMI2'
        }

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            InputCmdString = 'MyWall set SelInput {0} {1}\r\n'.format(device, ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            InputCmdString = 'MyWall get SelInput {}\r\n'.format(device)
            self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInput')

    def __MatchInput(self, match, tag):

        ValueStateValues = {
            'displayport1': 'DisplayPort 1',
            'displayport2': 'DisplayPort 2',
            'hdmi1': 'HDMI 1',
            'hdmi2': 'HDMI 2',
            'mixed': 'Mixed',
            'unknown': 'Unknown'
        }

        device = ['0', '0'] if match.group(1).decode() == 'wall' else match.group(1).decode().split(',')
        qualifier = {'Horizontal Position': int(device[0]), 'Vertical Position': int(device[1])}
        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('Input', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Idle': 'idle'
        }

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            PowerCmdString = 'MyWall set OpState {0} {1}\r\n'.format(device, ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        device = ''
        if qualifier['Horizontal Position'] == 0 and qualifier['Vertical Position'] == 0:
            device = 'wall'
        elif isinstance(qualifier['Horizontal Position'], int) and isinstance(qualifier['Vertical Position'], int):
            device = '{0},{1}'.format(qualifier['Horizontal Position'], qualifier['Vertical Position'])

        if device:
            PowerCmdString = 'MyWall get OpState {}\r\n'.format(device)
            self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePower')

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'idle': 'Idle',
            'mixed': 'Mixed',
            'unknown': 'Unknown'
        }

        device = ['0', '0'] if match.group(1).decode() == 'wall' else match.group(1).decode().split(',')
        qualifier = {'Horizontal Position': int(device[0]), 'Vertical Position': int(device[1])}
        value = ValueStateValues[match.group(2).decode().lower()]
        self.WriteStatus('Power', value, qualifier)

    def UpdateWallSize(self, value, qualifier):

        WallSizeCmdString = 'MyWall get WallSize\r\n'
        self.__UpdateHelper('WallSize', WallSizeCmdString, value, qualifier)

    def __MatchWallSize(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('WallSize', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        ERROR_CODES = {
            'syntax': 'The command syntax could not be identified.',
            'not': 'The command is currently not supported.',
            'incomplete': 'The command could not be fully executed.',
            'system': 'The command could not be executed because the system was busy with other tasks.'
        }
        self.Error([ERROR_CODES[match.group(1).decode()]])

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
