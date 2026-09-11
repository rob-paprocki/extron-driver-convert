from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re

class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.devicePassword = 'password'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ControlObjectDecibel': {'Parameters': ['Name'], 'Status': {}},
            'ControlObjectMode': {'Parameters': ['Name'], 'Status': {}},
            'ControlObjectText': {'Parameters': ['Name'], 'Status': {}},
            'KeepAlive': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'Refresh': {'Status': {}},
        }

    @staticmethod
    def __constraint_checker(*value_dicts):

        return all(map(lambda x: (x['Min'] <= x['Value'] <= x['Max']), value_dicts))

    def Login(self, value, qualifier):

        self.__SetHelper('Login', 'LOGIN "{}"\r'.format(self.devicePassword), None, None)

    def SetControlObjectDecibel(self, value, qualifier):

        name = qualifier['Name']
        if name:
            if '\x20' in name:
                name = '"{}"'.format(name)
            ControlObjectDecibelCmdString = 'SET {} {:.1f}\r'.format(name, value)
            self.__SetHelper('ControlObjectDecibel', ControlObjectDecibelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlObjectDecibel')

    def SetControlObjectMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'TRUE',
            'Off': 'FALSE',
        }

        name = qualifier['Name']
        if name:
            if '\x20' in name:
                name = '"{}"'.format(name)
            ControlObjectModeCmdString = 'SET {} {}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('ControlObjectMode', ControlObjectModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlObjectMode')

    def SetControlObjectText(self, value, qualifier):

        name = qualifier['Name']
        if value and name:
            value = value.replace('"', '')
            if '\x20' in name:
                name = '"{}"'.format(name)
            ControlObjectTextCmdString = 'SET {} "{}"\r'.format(name, value)
            self.__SetHelper('ControlObjectText', ControlObjectTextCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetControlObjectText')

    def UpdateKeepAlive(self, value, qualifier):

        KeepAliveCmdString = 'KEEPALIVE\r'
        self.Send(KeepAliveCmdString)

    def SetPresetRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 200,
            'Value': int(value) if value.isdigit() else -1,
        }

        if self.__constraint_checker(ValueConstraints):
            PresetRecallCmdString = 'PRESET {}\r'.format(ValueConstraints['Value'])
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def UpdateRefresh(self, value, qualifier):

        ObjectModeStates = {
            'FALSE': 'Off',
            'TRUE': 'On',
        }

        RefreshCmdString = 'REFRESH\r'
        res = self.__UpdateHelper('Refresh', RefreshCmdString, value, qualifier)
        if res:
            for line in res.splitlines():
                try:
                    name, result, *other = line[1:].split('=')
                except ValueError:
                    self.Error(['Refresh: Invalid/unexpected response'])
                else:
                    if not result or other:
                        self.Error(['Control Object Mode: Unexpected response format for ' + name])
                    elif result in ObjectModeStates:
                        self.WriteStatus('ControlObjectMode', ObjectModeStates[result], {'Name': name})
                    else:
                        try:
                            decibel = float(result)
                        except ValueError:
                            self.WriteStatus('ControlObjectText', result, {'Name': name})
                        else:
                            self.WriteStatus('ControlObjectDecibel', decibel, {'Name': name})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_codes = {
            '101': 'Error: Invalid Command',
            '102': 'Error: Bad Arguments',
            '103': 'Error: Invalid Data Format',
            '104': 'Error: Control Object Not Found',
            '105': 'Error: Parameter Not Found',
            '106': 'Error: Data Value Not Found',
            '107': 'Error: Max Subscription Reached',
            '108': 'Error: Password Error',
            '109': 'Error: Not Yet Login',
            '110': 'Error: Command Not Supported for Control Object',
            '111': 'Error: Invalid Group Name',
            '112': 'Error: Max Control Group Reached',
            '113': 'Error: Max Control Object in Group Reached',
            '114': 'Error: Object Already in Group',
            '115': 'Error: Object Not in Group',
            '116': 'Error: Conflicting With Other Objects in Group',
            '117': 'Error: Invalid Preset #',
            '118': 'Error: Invalid Preset Name'
        }

        if response.startswith('ERROR='):
            error_number = response[6:-1]
            self.Error([error_codes.get(error_number, 'Unknown Error Occurred')])
            if error_number == '109':
                self.Login(None, None)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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