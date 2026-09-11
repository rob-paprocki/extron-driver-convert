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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AvailableSources': {'Status': {}},
            'BootPreset1Autoload': {'Status': {}},
            'ChannelMode': {'Status': {}},
            'FadeMode': {'Status': {}},
            'Firmwareversion': {'Status': {}},
            'OpenPlaylistCommand': {'Status': {}},
            'OpenSourceCommand': {'Status': {}},
            'PlayerMode': {'Status': {}},
            'Preset': {'Status': {}},
            'ReloadEthernetConfig': {'Status': {}},
            'ReloadEventConfig': {'Status': {}},
            'ReloadPresetConfig': {'Status': {}},
            'ReloadStoreandForwardConfig': {'Status': {}},
            'ReloadWifiConfig': {'Status': {}},
            'Repeat': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'{"title":[\s\S]+,"SourceList":([\s\S]+),[\s\S]+"preset":([1-9]|1[0-9]|20),"volume":([0-9]|[1-9][0-9]|100),[\s\S]+"repeat":([0-3]),"playmode":([0-1]),"fade":([0-2]),"bootpreset1":([0-1]),[\s\S]+}\r?\n?'), self.__MatchAvailableSources, None)
            self.AddMatchString(re.compile(b'{"version":"([\s\S]+)"}\r?\n?'), self.__MatchFirmwareversion, None)

    def UpdateAvailableSources(self, value, qualifier):

        AvailableSourcesCmdString = '{"jsonrpc":"2.0","method":"Player.GetStatsEx"}\r\n'
        self.__UpdateHelper('AvailableSources', AvailableSourcesCmdString, value, qualifier)

    def __MatchAvailableSources(self, match, tag):

        BootPreset1AutoloadValue = {
            '0': 'Keep Last Status',
            '1': 'Boot Preset 1'
        }
        FadeModeValue = {
            '0': 'Off',
            '1': 'Crossfade',
            '2': 'On'
        }
        PlayerModeValues = {
            '0': 'Sequential',
            '1': 'Random'
        }
        RepeatValues = {
            '0': 'Play All',
            '1': 'Play One',
            '2': 'Repeat All',
            '3': 'Repeat One'
        }
        self.WriteStatus('AvailableSources', match.group(1).decode(), None)

        self.WriteStatus('Preset', match.group(2).decode(), None)

        self.WriteStatus('Volume', int(match.group(3).decode()), None)

        self.WriteStatus('Repeat', RepeatValues[match.group(4).decode()], None)

        self.WriteStatus('PlayerMode', PlayerModeValues[match.group(5).decode()], None)

        self.WriteStatus('FadeMode', FadeModeValue[match.group(6).decode()], None)

        self.WriteStatus('BootPreset1Autoload', BootPreset1AutoloadValue[match.group(7).decode()], None)

    def SetBootPreset1Autoload(self, value, qualifier):

        ValueStateValues = {
            'Keep Last Status': '{"jsonrpc":"2.0","method":"Device.BootPreset1","BootPreset1":0}\r\n',
            'Boot Preset 1': '{"jsonrpc":"2.0","method":"Device.BootPreset1","BootPreset1":1}\r\n'
        }

        BootPreset1AutoloadCmdString = ValueStateValues[value]
        self.__SetHelper('BootPreset1Autoload', BootPreset1AutoloadCmdString, value, qualifier)
    
    def UpdateBootPreset1Autoload(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def SetChannelMode(self, value, qualifier):

        ValueStateValues = {
            'Mono': '{"jsonrpc":"2.0","method":"Device.Channels","Channels":1}\r\n',
            'Stereo': '{"jsonrpc":"2.0","method":"Device.Channels","Channels":2}\r\n'
        }

        ChannelModeCmdString = ValueStateValues[value]
        self.__SetHelper('ChannelMode', ChannelModeCmdString, value, qualifier)

    def SetFadeMode(self, value, qualifier):

        ValueStateValues = {
            'Off': '{"jsonrpc":"2.0","method":"Player.Fade","Fade":0}\r\n',
            'Crossfade': '{"jsonrpc":"2.0","method":"Player.Fade","Fade":1}\r\n',
            'On': '{"jsonrpc":"2.0","method":"Player.Fade","Fade":2}\r\n'
        }

        FadeModeCmdString = ValueStateValues[value]
        self.__SetHelper('FadeMode', FadeModeCmdString, value, qualifier)
        
    def UpdateFadeMode(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def UpdateFirmwareversion(self, value, qualifier):

        FirmwareversionCmdString = '{"jsonrpc":"2.0","method":"Firmware.GetVersion"}\r\n'
        self.__UpdateHelper('Firmwareversion', FirmwareversionCmdString, value, qualifier)

    def __MatchFirmwareversion(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Firmwareversion', value, None)

    def SetOpenPlaylistCommand(self, value, qualifier):

        playlist_string = value
        if playlist_string:
            OpenPlaylistCommandCmdString = '{{"jsonrpc":"2.0","method":"Player.Open","Playlist":"{}"}}\r\n'.format(playlist_string)
            self.__SetHelper('OpenPlaylistCommand', OpenPlaylistCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpenPlaylistCommand')

    def SetOpenSourceCommand(self, value, qualifier):

        playlist_string = value
        if playlist_string:
            OpenSourceCommandCmdString = '{{"jsonrpc":"2.0","method":"Player.Open","Source":"{}"}}\r\n'.format(playlist_string)
            self.__SetHelper('OpenSourceCommand', OpenSourceCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOpenSourceCommand')

    def SetPlayerMode(self, value, qualifier):

        ValueStateValues = {
            'Sequential': '{"jsonrpc":"2.0","method":"Player.Mode","PlayMode":0}\r\n',
            'Random': '{"jsonrpc":"2.0","method":"Player.Mode","PlayMode":1}\r\n'
        }

        PlayerModeCmdString = ValueStateValues[value]
        self.__SetHelper('PlayerMode', PlayerModeCmdString, value, qualifier)
        
    def UpdatePlayerMode(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1': '{"jsonrpc":"2.0","method":"Player.Open","Preset":1}\r\n',
            '2': '{"jsonrpc":"2.0","method":"Player.Open","Preset":2}\r\n',
            '3': '{"jsonrpc":"2.0","method":"Player.Open","Preset":3}\r\n',
            '4': '{"jsonrpc":"2.0","method":"Player.Open","Preset":4}\r\n',
            '5': '{"jsonrpc":"2.0","method":"Player.Open","Preset":5}\r\n',
            '6': '{"jsonrpc":"2.0","method":"Player.Open","Preset":6}\r\n',
            '7': '{"jsonrpc":"2.0","method":"Player.Open","Preset":7}\r\n',
            '8': '{"jsonrpc":"2.0","method":"Player.Open","Preset":8}\r\n',
            '9': '{"jsonrpc":"2.0","method":"Player.Open","Preset":9}\r\n',
            '10': '{"jsonrpc":"2.0","method":"Player.Open","Preset":10}\r\n',
            '11': '{"jsonrpc":"2.0","method":"Player.Open","Preset":11}\r\n',
            '12': '{"jsonrpc":"2.0","method":"Player.Open","Preset":12}\r\n',
            '13': '{"jsonrpc":"2.0","method":"Player.Open","Preset":13}\r\n',
            '14': '{"jsonrpc":"2.0","method":"Player.Open","Preset":14}\r\n',
            '15': '{"jsonrpc":"2.0","method":"Player.Open","Preset":15}\r\n',
            '16': '{"jsonrpc":"2.0","method":"Player.Open","Preset":16}\r\n',
            '17': '{"jsonrpc":"2.0","method":"Player.Open","Preset":17}\r\n',
            '18': '{"jsonrpc":"2.0","method":"Player.Open","Preset":18}\r\n',
            '19': '{"jsonrpc":"2.0","method":"Player.Open","Preset":19}\r\n',
            '20': '{"jsonrpc":"2.0","method":"Player.Open","Preset":20}\r\n'
        }

        PresetCmdString = ValueStateValues[value]
        self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        
    def UpdatePreset(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def SetReloadEthernetConfig(self, value, qualifier):

        ReloadEthernetConfigCmdString = '{"jsonrpc":"2.0","method":"Ethernet.Reload"}\r\n'
        self.__SetHelper('ReloadEthernetConfig', ReloadEthernetConfigCmdString, value, qualifier)

    def SetReloadEventConfig(self, value, qualifier):

        ValueStateValues = {
            'GPI1': '{"jsonrpc":"2.0","method":"Event.Reload","Index":"GPI1"}\r\n',
            'GPI2': '{"jsonrpc":"2.0","method":"Event.Reload","Index":"GPI2"}\r\n',
            'Silence': '{"jsonrpc":"2.0","method":"Event.Reload","Index":"SILENCE"}\r\n'
        }

        ReloadEventConfigCmdString = ValueStateValues[value]
        self.__SetHelper('ReloadEventConfig', ReloadEventConfigCmdString, value, qualifier)

    def SetReloadPresetConfig(self, value, qualifier):

        ValueStateValues = {
            '1': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":1}\r\n',
            '2': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":2}\r\n',
            '3': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":3}\r\n',
            '4': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":4}\r\n',
            '5': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":5}\r\n',
            '6': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":6}\r\n',
            '7': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":7}\r\n',
            '8': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":8}\r\n',
            '9': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":9}\r\n',
            '10': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":10}\r\n',
            '11': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":11}\r\n',
            '12': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":12}\r\n',
            '13': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":13}\r\n',
            '14': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":14}\r\n',
            '15': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":15}\r\n',
            '16': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":16}\r\n',
            '17': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":17}\r\n',
            '18': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":18}\r\n',
            '19': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":19}\r\n',
            '20': '{"jsonrpc":"2.0","method":"Preset.Reload","Index":20}\r\n'
        }

        ReloadPresetConfigCmdString = ValueStateValues[value]
        self.__SetHelper('ReloadPresetConfig', ReloadPresetConfigCmdString, value, qualifier)

    def SetReloadStoreandForwardConfig(self, value, qualifier):

        ReloadStoreandForwardConfigCmdString = '{"jsonrpc":"2.0","method":"SAF.Reload"}\r\n'
        self.__SetHelper('ReloadStoreandForwardConfig', ReloadStoreandForwardConfigCmdString, value, qualifier)

    def SetReloadWifiConfig(self, value, qualifier):

        ReloadWifiConfigCmdString = '{"jsonrpc":"2.0","method":"Wifi.Reload"}\r\n'
        self.__SetHelper('ReloadWifiConfig', ReloadWifiConfigCmdString, value, qualifier)

    def SetRepeat(self, value, qualifier):

        ValueStateValues = {
            'Play All': '{"jsonrpc":"2.0","method":"Player.Repeat","Repeat":0}\r\n',
            'Play One': '{"jsonrpc":"2.0","method":"Player.Repeat","Repeat":1}\r\n',
            'Repeat All': '{"jsonrpc":"2.0","method":"Player.Repeat","Repeat":2}\r\n',
            'Repeat One': '{"jsonrpc":"2.0","method":"Player.Repeat","Repeat":3}\r\n'
        }

        RepeatCmdString = ValueStateValues[value]
        self.__SetHelper('Repeat', RepeatCmdString, value, qualifier)
        
    def UpdateRepeat(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': '{"jsonrpc":"2.0","method":"Player.Play"}\r\n',
            'Stop': '{"jsonrpc":"2.0","method":"Player.Stop"}\r\n',
            'Next': '{"jsonrpc":"2.0","method":"Player.Next"}\r\n',
            'Previous': '{"jsonrpc":"2.0","method":"Player.Prev"}\r\n'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{{"jsonrpc":"2.0","method":"Player.Volume","Volume":{0}}}\r\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
        
    def UpdateVolume(self, value, qualifier):
        self.UpdateAvailableSources(value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

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
                    except:
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
            except:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)

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
