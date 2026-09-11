from extronlib.interface import EthernetClientInterface
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
            'DeviceType': {'Status': {}},
            'PresetRecall': {'Parameters': ['Type', 'Origin', 'Destination'], 'Status': {}},
            'Source': {'Parameters': ['Web RCS', 'Type', 'Layer'], 'Status': {}},
            'Take': {'Parameters': ['Web RCS'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DEV105\r\n'), self.__MatchDeviceType, None)
            self.AddMatchString(re.compile(b'E(1[0123])\r\n'), self.__MatchError, None)

    def __ConstraintChecker(self, *args):

        try:
            for x in args:
                if not(x['Min'] <= int(x['Value']) <= x['Max']):
                    return False
            return True
        except:
            return False

    def UpdateDeviceType(self, value, qualifier):

        DeviceTypeCmdString = '?\n'
        self.__UpdateHelper('DeviceType', DeviceTypeCmdString, value, qualifier)

    def __MatchDeviceType(self, match, tag):

        self.WriteStatus('DeviceType', 'NeXtage 16 - 4K', None)

    def SetPresetRecall(self, value, qualifier):

        TypeStates = {
            'Program': '0',
            'Preview': '1'
        }
        OriginConstraints = {
            'Min': 1,
            'Max': 144,
            'Value': int(qualifier['Origin'])
        }
        DestinationConstraints = {
            'Min': 1,
            'Max': 8,
            'Value': int(qualifier['Destination'])
        }

        Type = qualifier['Type']
        if Type in TypeStates and self.__ConstraintChecker(OriginConstraints, DestinationConstraints):
            PresetRecallCmdString = '{}PMmet\n{}PMscf\n{}PMprf\n1PMloa\n'.format(OriginConstraints['Value'] - 1, DestinationConstraints['Value'] - 1, TypeStates[Type])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetSource(self, value, qualifier):

        WebRCSConstraints = {
            'Min': 1,
            'Max': 144,
            'Value': int(qualifier['Web RCS'])
        }
        TypeStates = {
            'Program': '0',
            'Preview': '1'
        }
        LayerStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3'
        }
        ValueConstraints = {
            'Min': 1,
            'Max': 8,
            'Value': value
        }

        Type = qualifier['Type']
        Layer = qualifier['Layer']
        if Type in TypeStates and Layer in LayerStates and self.__ConstraintChecker(WebRCSConstraints, ValueConstraints):
            SourceCmdString = '{},{},{},{}SPPEi\n'.format(WebRCSConstraints['Value'] - 1, TypeStates[Type], LayerStates[Layer], value)
            self.__SetHelper('Source', SourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSource')

    def SetTake(self, value, qualifier):

        WebRCSConstraints = {
            'Min': 1,
            'Max': 144,
            'Value': int(qualifier['Web RCS'])
        }

        if self.__ConstraintChecker(WebRCSConstraints):
            TakeCmdString = '{},1SPCtk\n'.format(WebRCSConstraints['Value'] - 1)
            self.__SetHelper('Take', TakeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTake')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('{}: Inappropriate Command'.format(command))
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):

        Errors = {
            b'10': 'Register name error',
            b'11': 'Index value out of range error',
            b'12': 'Index number error',
            b'13': 'Value out of range error',
        }
        self.Error([Errors[match.group(1)]])

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
        method = 'Set%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(value, qualifier)
        else:
            print(command, 'does not support Set.')
    # Send Update Commands

    def Update(self, command, qualifier=None):
        method = 'Update%s' % command
        if hasattr(self, method) and callable(getattr(self, method)):
            getattr(self, method)(None, qualifier)
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
