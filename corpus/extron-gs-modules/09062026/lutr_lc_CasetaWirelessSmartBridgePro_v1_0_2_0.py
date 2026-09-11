from extronlib.interface import EthernetClientInterface, SerialInterface
import re
from extronlib.system import ProgramLog

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
        self.deviceUsername = None
        self.devicePassword = None
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            '4ButtonPicoControls': {'Parameters': ['Integration ID', 'Button'], 'Status': {}},
            'OutputControl': {'Parameters': ['Integration ID'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Integration ID'], 'Status': {}},
            'PicoControls': {'Parameters': ['Integration ID', 'Button'], 'Status': {}},
            'SceneTrigger': {'Parameters': ['Integration ID', 'Scene Number'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'~OUTPUT,([0-9]{1,2}),1,([0-9.]{2,6})\r'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'login:'), self.__MatchLogin, None)
            self.AddMatchString(re.compile(b'password:'), self.__MatchPassword, None)

    def __MatchLogin(self, match, tag):
        if self.deviceUsername is not None:
            self.Send('{0}\r\n'.format(self.deviceUsername))
        else:
            self.MissingCredentialsLog('Username')

    def __MatchPassword(self, match, tag):
        if self.devicePassword is not None:
            self.Send('{0}\r\n'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def Set4ButtonPicoControls(self, value, qualifier):

        ButtonStates = {
            '1': '8',
            '2/Raise': '9',
            '3/Lower': '10',
            '4': '11'
        }

        ValueStateValues = {
            'Press': '3',
            'Release': '4'
        }
        if 2 <= int(qualifier['Integration ID']) <= 50:
            ButtonPicoControlsCmdString = '#DEVICE,{0},{1},{2}\r\n'.format(qualifier['Integration ID'], ButtonStates[qualifier['Button']], ValueStateValues[value])
            self.__SetHelper('4ButtonPicoControls', ButtonPicoControlsCmdString, value, qualifier)
        else:
            print('Invalid Command for Set4ButtonPicoControls')

    def SetOutputControl(self, value, qualifier):

        ValueStateValues = {
            'Raise': '2',
            'Lower': '3',
            'Stop': '4'
        }

        if 2 <= int(qualifier['Integration ID']) <= 50:
            OutputControlCmdString = '#OUTPUT,{0},{1}\r\n'.format(qualifier['Integration ID'], ValueStateValues[value])
            self.__SetHelper('OutputControl', OutputControlCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputControl')

    def SetOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 2 <= int(qualifier['Integration ID']) <= 50:
            OutputLevelCmdString = '#OUTPUT,{0},1,{1}\r\n'.format(qualifier['Integration ID'], value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        if 2 <= int(qualifier['Integration ID']) <= 50:
            OutputLevelCmdString = '?OUTPUT,{0},1\r\n'.format(qualifier['Integration ID'])
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        qualifier = {}
        qualifier['Integration ID'] = match.group(1).decode()
        value = float(match.group(2).decode())
        if 2 <= int(qualifier['Integration ID']) <= 50 and 0 <= value <= 100:
            self.WriteStatus('OutputLevel', value, qualifier)

    def SetPicoControls(self, value, qualifier):

        ButtonStates = {
            '1': '2',
            '2': '3',
            '3': '4',
            'Raise': '5',
            'Lower': '6'
        }

        ValueStateValues = {
            'Press': '3',
            'Release': '4'
        }
        if 2 <= int(qualifier['Integration ID']) <= 50:
            PicoControlsCmdString = '#DEVICE,{0},{1},{2}\r\n'.format(qualifier['Integration ID'], ButtonStates[qualifier['Button']], ValueStateValues[value])
            self.__SetHelper('PicoControls', PicoControlsCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPicoControls')

    def SetSceneTrigger(self, value, qualifier):

        ValueStateValues = {
            'Press': '3',
            'Release': '4'
        }
        if 1 <= int(qualifier['Integration ID']) <= 50 and 1 <= int(qualifier['Scene Number']) <= 50:
            SceneTriggerCmdString = '#DEVICE,{0},{1},{2}\r\n'.format(qualifier['Integration ID'], qualifier['Scene Number'], ValueStateValues[value])
            self.__SetHelper('SceneTrigger', SceneTriggerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSceneTrigger')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
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

            self.Send(commandstring)

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
