from extronlib.interface import SerialInterface, EthernetClientInterface
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
        self.Models = {}
        self.devicePassword = None

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GetBoolean': {'Parameters': ['Control Object/Group'], 'Status': {}},
            'GetNumber': {'Parameters': ['Control Object/Group'], 'Status': {}},
            'GetString': {'Parameters':['Control Object/Group'], 'Status': {}},
            'PresetNumber': {'Status': {}},
            'PresetString': {'Status': {}},
            'SetBoolean': {'Parameters': ['Control Object/Group'], 'Status': {}},
            'SetNumber': {'Parameters': ['Control Object/Group'], 'Status': {}},
            'SetString': {'Parameters':['Control Object/Group'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'"?([^"]{1,32})"?=(TRUE|FALSE)\r'), self.__MatchGetBoolean, None)
            self.AddMatchString(re.compile(b'"?([^"]{1,32})"?=([+-]?\d*)\r'), self.__MatchGetNumber, None)
            self.AddMatchString(re.compile(b'"?([^"]{1,32})"?="?([^"]*)"?\r'), self.__MatchGetString, None)
            self.AddMatchString(re.compile(b'ERROR=(101|102|103|104|105|106|107|108|109|110|111|112|113|114|115|116|117|118)\r'), self.__MatchError, None)

    def SetPassword(self, value=None, qualifier=None):
        if self.devicePassword is not None:
            self.Send('LOGIN {0}\r'.format(self.devicePassword))
        else:
            self.MissingCredentialsLog('Password')

    def UpdateGetBoolean(self, value, qualifier):
        if '"' not in qualifier['Control Object/Group']:
            GetBooleanCmdString = 'GET "{0}"\r'.format(qualifier['Control Object/Group'])
            self.__UpdateHelper('GetBoolean', GetBooleanCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateGetBoolean')

    def __MatchGetBoolean(self, match, tag):

        ValueStateValues = {
            'TRUE': 'True',
            'FALSE': 'False'
        }

        qualifier = {}
        qualifier['Control Object/Group'] = match.group(1).decode()
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('GetBoolean', value, qualifier)

    def UpdateGetNumber(self, value, qualifier):

        if '"' not in qualifier['Control Object/Group']:
            GetNumberCmdString = 'GET "{0}"\r'.format(qualifier['Control Object/Group'])
            self.__UpdateHelper('GetNumber', GetNumberCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateGetNumber')

    def __MatchGetNumber(self, match, tag):

        qualifier = {}
        qualifier['Control Object/Group'] = match.group(1).decode()
        value = int(match.group(2).decode())
        self.WriteStatus('GetNumber', value, qualifier)
        
    def UpdateGetString(self, value, qualifier):
        if '"' not in qualifier['Control Object/Group']:
            GetStringCmdString = 'GET "{0}"\r'.format(qualifier['Control Object/Group'])
            self.__UpdateHelper('GetString', GetStringCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGetString')

    def __MatchGetString(self, match, tag):

        qualifier = {}
        qualifier['Control Object/Group'] = match.group(1).decode()
        value = match.group(2).decode()
        self.WriteStatus('GetString', value, qualifier)

    def SetPresetNumber(self, value, qualifier):

        PresetNumberCmdString = 'PRESET {0}\r'.format(value)
        self.__SetHelper('PresetNumber', PresetNumberCmdString, value, qualifier)
        
    def SetPresetString(self, value, qualifier):
        CmdString = value
        if CmdString:
            SetPresetString = 'PRESET "{0}"\r'.format(CmdString)
            self.__SetHelper('PresetString', SetPresetString, value, qualifier)
        else:
            self.Discard('Invalid Command')

    def SetSetBoolean(self, value, qualifier):

        ValueStateValues = {
            'True': 'TRUE',
            'False': 'FALSE'
        }

        if '"' not in qualifier['Control Object/Group']:
            SetBooleanCmdString = 'SET "{0}" {1}\r'.format(qualifier['Control Object/Group'], ValueStateValues[value])
            self.__SetHelper('SetBoolean', SetBooleanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetBoolean')

    def SetSetNumber(self, value, qualifier):
        if '"' not in qualifier['Control Object/Group']:
            SetNumberCmdString = 'SET "{0}" {1}\r'.format(qualifier['Control Object/Group'], value)
            self.__SetHelper('SetNumber', SetNumberCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetNumber')
            
    def SetSetString(self, value, qualifier):
        CmdString = value
        if CmdString and '"' not in qualifier['Control Object/Group']:
            SetStringCmdString = 'SET "{0}" {1}\r'.format(qualifier['Control Object/Group'], CmdString)
            self.__SetHelper('SetString', SetStringCmdString, value, qualifier)
        else:
            print('Invalid Command for SetSetString')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()
                
        self.Send(commandstring)

    def __MatchError(self, match, tag):

        DEVICE_ERROR_CODES = {
            '101': 'Invalid Command',
            '102': 'Bad Arguments',
            '103': 'Invalid Data Format',
            '104': 'Control Object Not Found',
            '105': 'Parameter Not Found',
            '106': 'Data Value Not Found',
            '107': 'Max Subscription Reached',
            '108': 'Password Error',
            '109': 'Not Logged In',
            '110': 'Command Not Supported for Control Object',
            '111': 'Invalid Group Name',
            '112': 'Max Control Group Reached',
            '113': 'Max Control Object in Group Reached',
            '114': 'Object Already in Group',
            '115': 'Object Not in Group',
            '116': 'Conflicting With Other Objects in Group',
            '117': 'Invalid Preset',
            '118': 'Invalid Preset Name',
        }

        value = DEVICE_ERROR_CODES[match.group(1).decode()]
        print(value[1])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetPassword(None, None)

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
