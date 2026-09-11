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
        self.Debug = False
        self.Models = {}

        self.devicePassword = None
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Channel'           : {'Status': {}},
            'ChannelStatus'     : {'Status': {}},
            'CurrentMedia'      : {'Status': {}},
            'DisplayPower'      : {'Status': {}},
            'InputCommand'      : {'Status': {}},
            'Mute'              : {'Status': {}},
            'Reboot'            : {'Parameters':['Device'], 'Status': {}},
            'Volume'            : {'Status': {}}
            }
        
        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'getchannel,channel="(\d+)",status="0",statusstring="Success"(?:\r|\n|\r\n)'), self.__MatchChannelStatus, None)
            self.AddMatchString(re.compile(b'getcurrentmedia,currentmedia="(.*)",status="0",statusstring="Success"(?:\r|\n|\r\n)'), self.__MatchCurrentMedia, None)
            self.AddMatchString(re.compile(b'(?:get)?mute,muted="(0|1)",status="0",statusstring="Success"(?:\r|\n|\r\n)'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'getvolume,volume="(\d{1,2})",status="0",statusstring="Success"(?:\r|\n|\r\n)'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b',status="([1-9]|\d{2}|\d{3})",'), self.__MatchError, None)

    @property
    def devicePassword(self):
        return self._devicePassword
    
    @devicePassword.setter
    def devicePassword(self, value):
        if value:
            self._devicePassword = ',passwd="' + value + '"'
        else:
            self._devicePassword = ''

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up' : 'channelup', 
            'Down' : 'channeldown'
        }

        ChannelCmdString = '{0}{1}\r\n'.format(ValueStateValues[value], self._devicePassword)
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def UpdateChannelStatus(self, value, qualifier):

        ChannelStatusCmdString = 'getchannel{0}\r\n'.format(self._devicePassword)
        self.__UpdateHelper('ChannelStatus', ChannelStatusCmdString, value, qualifier)

    def __MatchChannelStatus(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('ChannelStatus', value, None)

    def UpdateCurrentMedia(self, value, qualifier):


        CurrentMediaCmdString = 'getcurrentmedia{0}\r\n'.format(self._devicePassword)
        self.__UpdateHelper('CurrentMedia', CurrentMediaCmdString, value, qualifier)

    def __MatchCurrentMedia(self, match, tag):


        value = match.group(1).decode()
        self.WriteStatus('CurrentMedia', value, None)

    def SetDisplayPower(self, value, qualifier):

        ValueStateValues = {
            'On' : 'enable="1"', 
            'Off' : 'enable="0"'
        }

        DisplayPowerCmdString = 'displaycontrol{0},{1}\r\n'.format(self._devicePassword, ValueStateValues[value]) 
        self.__SetHelper('DisplayPower', DisplayPowerCmdString, value, qualifier)



    def SetInputCommand(self, value, qualifier):

        inputStr = value
        if inputStr:
            value = inputStr.replace('\\', r'\\').replace('"', r'\"')
            InputCommandCmdString = 'displaycontrol{0},input="{1}"\r\n'.format(self._devicePassword, value)  
            self.__SetHelper('InputCommand', InputCommandCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputCommand')


    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On' : '1', 
            'Off' : '0'
        }

        MuteCmdString = 'mute{0},muted="{1}"\r\n'.format(self._devicePassword, ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def UpdateMute(self, value, qualifier):

        MuteCmdString = 'getmute{0}\r\n'.format(self._devicePassword)
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1' : 'On', 
            '0' : 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetReboot(self, value, qualifier):

        DeviceStates = {
            'Single Unit' : '', 
            'Broadcast' : ',broadcast'
        }

        RebootCmdString = 'reboot{1}{0}\r\n'.format(self._devicePassword, DeviceStates[qualifier['Device']])
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)


    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 16
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'setvolume{0},volume="{1}"\r\n'.format(self._devicePassword, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')
            
    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'getvolume{0}\r\n'.format(self._devicePassword)
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def __MatchError(self, match, tag):


        DeviceErrors = {
            '1'   : 'An unexpected error has occurred',
            '26'  : 'Channel to be viewed has not been specified',
            '27'  : 'The specified channel is invalid',
            '30'  : 'Invalid command',
            '132' : 'Request failed. An unknown command parameter was found',
            '139' : 'This command is invalid in this operating mode',
            '140' : 'No muted value specified',
            '141' : 'Muted value specified was invalid',
            '142' : 'No volume value specified',
            '143' : 'Volume value specified was invalid',
            '144' : 'No synchronisation label specified',
            '145' : 'All Units not specified and no individual units specified',
            '146' : 'Specify enable or input but not both',
            '154' : 'Unit name specified was invalid',
            '155' : 'Network update process is already running',
            '156' : 'Network update could not be started due to Network Access limits',
            '157' : 'No locations were specified',
            '158' : 'Invalid media location specified',
            '159' : 'Invalid config location specified',
            '160' : 'Invalid software location specified',
            '161' : 'Invalid super file location specified',
            '162' : 'DHCP must be true or false',
            '163' : 'When DHCP set to false, must specify IP address and netmask',
            '164' : 'When IP address is specified, must also specify netmask',
            '165' : 'Invalid IP address specified',
            '166' : 'Invalid netmask specified',
            '167' : 'Invalid gateway specified',
            '168' : 'Invalid nameserver specified',
            '169' : 'Invalid hostname specified',
            '170' : 'DHCP was specified together with IP address, netmask, gateway or nameserver',
            '171' : 'No network configuration items specified',
            '172' : 'Cannot specify IP address, netmask, gateway or nameserver when in DHCP mode',
            '173' : 'Password must be specified and be correct',
            '174' : 'No enablement code specified',
            '175' : 'The enablement code must be in the format XXX/XXX/XXX/XXX/XXX (where XXX is 000 : 255)',
            '176' : 'Reusing enablement code',
            '177' : 'Unknown feature codes',
            '178' : 'Invalid enablement code',
            '179' : 'Code not for this unit',
            '180' : 'This command is invalid during External Mute'
        }

        try:
            value = DeviceErrors[match.group(1).decode()]
            print(value)
        except(KeyError):
            print('An Unknown Error Occurred')

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
                self.Subscription[command] = {'method':{}}
        
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
        if command in self.Subscription :
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
            self._compile_list[regex_string] = {'callback': callback, 'para':arg}
                

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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
