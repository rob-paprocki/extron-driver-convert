from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ControlObjectDecibel': {'Parameters': ['Name'], 'Status': {}},
            'ControlObjectMode': {'Parameters': ['Name'], 'Status': {}},
            'ControlObjectText': {'Parameters': ['Name'], 'Status': {}},
            'PresetRecall': {'Status': {}},
        }

    def SetControlObjectDecibel(self, value, qualifier):

        Name = qualifier['Name']
        if Name:
            ControlObjectDecibelCmdString = 'SET {} {:.1f}\r'.format(Name, value)
            self.__SetHelper('ControlObjectDecibel', ControlObjectDecibelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetControlObjectDecibel')

    def UpdateControlObjectDecibel(self, value, qualifier):

        ControlObjectDecibelCmdString = 'REFRESH\r'
        res = self.__UpdateHelper('ControlObjectDecibel', ControlObjectDecibelCmdString, value, qualifier)
        if res:
            Modes = {'FALSE': 'Off', 'TRUE': 'On'}
            for Line in res.splitlines():
                try:
                    Name, Value, *Other = Line.split('=')
                except ValueError:
                    print('ControlObjectDecibel: Invalid/unexpected response for UpdateControlObjectDecibel')
                else:
                    if not Value or Other:
                        print('ControlObjectDecibel: Unexpected response format for ' + Name)
                    elif Value in Modes:
                        self.WriteStatus('ControlObjectMode', Modes[Value], {'Name': Name})
                    else:
                        try:
                            Decibel = float(Value)
                        except ValueError:
                            self.WriteStatus('ControlObjectText', Value, {'Name': Name})
                        else:
                            self.WriteStatus('ControlObjectDecibel', Decibel, {'Name': Name})

    def SetControlObjectMode(self, value, qualifier):

        ValueStateValues = {
            'On': 'TRUE',
            'Off': 'FALSE'
        }
        Name = qualifier['Name']
        if Name:
            ControlObjectModeCmdString = 'SET {} {}\r'.format(Name, ValueStateValues[value])
            self.__SetHelper('ControlObjectMode', ControlObjectModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetControlObjectMode')

    def UpdateControlObjectMode(self, value, qualifier):

        self.UpdateControlObjectDecibel(value, qualifier)

    def SetControlObjectText(self, value, qualifier):

        Name = qualifier['Name']
        if value and Name:
            value = value.replace('"', '')
            ControlObjectTextCmdString = 'SET {} "{}"\r'.format(Name, value)
            self.__SetHelper('ControlObjectText', ControlObjectTextCmdString, value, qualifier)
        else:
            print('Invalid Command for SetControlObjectText')

    def UpdateControlObjectText(self, value, qualifier):

        self.UpdateControlObjectDecibel(value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateConstraints = {
            'Min': 0,
            'Max': 70
        }
        if ValueStateConstraints['Min'] <= int(value) <= ValueStateConstraints['Max']:
            PresetRecallCmdString = 'PRESET {}\r'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def Login(self, value, qualifier):

        if self.devicePassword is not None:
            self.__SetHelper('Login', 'LOGIN "{}"\r'.format(self.devicePassword), None, None)
        else:
            self.MissingCredentialsLog('Password')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        Errors = {
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
            '117': 'Error: Invalid Preset',
            '118': 'Error: Invalid Preset Name'
        }
        if response.startswith('ERROR='):
            ErrorNumber = response[6:-1]
            print(Errors.get(ErrorNumber, 'Unknown Error Occurred'))
            if ErrorNumber == '109':
                self.Login(None, None)
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
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
                return self.__CheckResponseForErrors(command, res)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
