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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'BackgroundStatus': {'Status': {}},
            'Channel': {'Status': {}},
            'ChannelStatus': {'Status': {}},
            'ForegroundStatus': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Playback': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

        self.devicePassword = None

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'backgroundstatus="(\w+){0,}"'), self.__MatchBackgroundStatus, None)
            self.AddMatchString(re.compile(b'channel="(\d+){0,}"'), self.__MatchChannelStatus, None)
            self.AddMatchString(re.compile(b'foregroundstatus="(\w+){0,}"'), self.__MatchForegroundStatus, None)
            self.AddMatchString(re.compile(b'muted="(0|1)"'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'volume="([0-9]{0,2})"'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'get(\w+),(.*)statusstring="(fail.*)"', re.I), self.__MatchError, None)

    def UpdateBackgroundStatus(self, value, qualifier):

        if self.devicePassword is not None:
            BackgroundStatusCmdString = 'getcurrentmedia,passwd={0}\n'.format(self.devicePassword)
        else:
            BackgroundStatusCmdString = 'getcurrentmedia\n'
        self.__UpdateHelper('BackgroundStatus', BackgroundStatusCmdString, value, qualifier)

    def __MatchBackgroundStatus(self, match, tag):

        value = match.group(1)
        if value:
            self.WriteStatus('BackgroundStatus', value.decode().capitalize(), None)
        else:
            self.WriteStatus('BackgroundStatus', 'Status Not Available', None)

    def SetChannel(self, value, qualifier):

        ChannelStateValues = {
            'Up': 'channelup',
            'Down': 'channeldown',
        }
        if self.devicePassword is not None:
            ChannelCmdString = '{0},passwd={1}\n'.format(ChannelStateValues[value], self.devicePassword)
        else:
            ChannelCmdString = ChannelStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def UpdateChannelStatus(self, value, qualifier):

        if self.devicePassword is not None:
            ChannelStatusCmdString = 'getchannel,passwd={0}\n'.format(self.devicePassword)
        else:
            ChannelStatusCmdString = 'getchannel\n'
        self.__UpdateHelper('ChannelStatus', ChannelStatusCmdString, value, qualifier)

    def __MatchChannelStatus(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('ChannelStatus', value, None)

    def UpdateForegroundStatus(self, value, qualifier):

        if self.devicePassword is not None:
            BackgroundStatusCmdString = 'getcurrentmedia,passwd={0}\n'.format(self.devicePassword)
        else:
            BackgroundStatusCmdString = 'getcurrentmedia\n'
        self.__UpdateHelper('BackgroundStatus', BackgroundStatusCmdString, value, qualifier)

    def __MatchForegroundStatus(self, match, tag):

        value = match.group(1)
        if value:
            self.WriteStatus('ForegroundStatus', value.decode().capitalize(), None)
        else:
            self.WriteStatus('ForegroundStatus', 'Status Not Available', None)

    def SetKeypad(self, value, qualifier):

        if 0 <= int(value) <= 9:
            if self.devicePassword is not None:
                KeypadCmdString = 'ircontrol, key={0},passwd={1}\n'.format(value, self.devicePassword)
            else:
                KeypadCmdString = 'ircontrol, key={0}\n'.format(value)
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            print('Invalid Command for SetKeypad')

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up': 'UP',
            'Down': 'DOWN',
            'Quit': 'QUIT',
            'Menu': 'MENU',
            'OK': 'OK',
        }
        if self.devicePassword is not None:
            MenuNavigationCmdString = 'ircontrol, key={0},passwd={1}\n'.format(MenuNavigationStateValues[value], self.devicePassword)
        else:
            MenuNavigationCmdString = 'ircontrol, key={0}\n'.format(MenuNavigationStateValues[value])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteStateValues = {
            'On': '1',
            'Off': '0',
        }
        if self.devicePassword is not None:
            MuteCmdString = 'mute, muted={0},passwd={1}\n'.format(MuteStateValues[value], self.devicePassword)
        else:
            MuteCmdString = 'mute, muted={0}\n'.format(MuteStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        if self.devicePassword is not None:
            MuteCmdString = 'getmute,passwd={0}\n'.format(self.devicePassword)
        else:
            MuteCmdString = 'getmute\n'
        self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)

    def __MatchMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Mute', value, None)

    def SetPlayback(self, value, qualifier):

        PlaybackStateValues = {
            'Play': 'PLAY',
            'Pause': 'PAUSE',
            'Skip Forward': 'SKIPFORWARD',
            'Skip Back': 'SKIPBACK',
            'Next Item': 'NEXTITEM',
            'Previous Item': 'PREVIOUSITEM',
        }
        if self.devicePassword is not None:
            PlaybackCmdString = 'playbackcontrol, {0}, passwd={0}\n'.format(self.devicePassword)
        else:
            PlaybackCmdString = 'playbackcontrol, {0}\n'.format(PlaybackStateValues[value])
        self.__SetHelper('Playback', PlaybackCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On': '1',
            'Off': '0',
        }
        PowerCmdString = 'displaycontrol, enable={0}\n'.format(PowerStateValues[value])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 16
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = 'setvolume, volume={0}\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if self.devicePassword is not None:
            VolumeCmdString = 'getvolume,passwd={0}\n'.format(self.devicePassword)
        else:
            VolumeCmdString = 'getvolume\n'
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
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()
                
            self.Send(commandstring)

    def __MatchError(self, match, tag):

        errorList = {
            'mute': 'Mute Status Command Failed',
            'volume': 'Volume Status Command Failed',
            'operatingmode': 'Operation Mode Status Command Failed',
            'channel': 'Channel Status Command Failed',
            'currentmedia': 'Background Status and Foreground Status Command Failed',
        }
        value = errorList.get(match.group(1).decode(), 'Command {0} Failed'.format(match.group(1).decode()))
        print(value)

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
