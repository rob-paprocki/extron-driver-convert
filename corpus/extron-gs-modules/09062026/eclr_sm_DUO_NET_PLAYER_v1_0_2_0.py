from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search
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
            'CurrentlyPlaying': {'Parameters': ['Player', 'Tag'], 'Status': {}},
            'FadeMode': {'Parameters': ['Player'], 'Status': {}},
            'Mute': {'Parameters': ['Player'], 'Status': {}},
            'PlaybackTempoVariation': {'Parameters': ['Player'], 'Status': {}},
            'PlayerTime': {'Parameters': ['Player', 'Type'], 'Status': {}},
            'Playlist': {'Parameters': ['Player'], 'Status': {}},
            'PlayMode': {'Parameters': ['Player'], 'Status': {}},
            'Preset': { 'Status': {}},
            'PriorityStatus': {'Parameters': ['Priority'], 'Status': {}},
            'RepeatMode': {'Parameters': ['Player'], 'Status': {}},
            'Transport': {'Parameters': ['Player'], 'Status': {}},
            'Volume': {'Parameters': ['Player'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(compile(rb'DATA PLAYER_ITEM_TAG_(ALIAS|TITLE|ARTIST|ALBUM|NAME) ([AB]) \"([^\"]*)\"\x0A'), self.__MatchCurrentlyPlaying, None)
            self.AddMatchString(compile(rb'DATA PLAYER_FADE_MODE ([AB]) (NONE|XFADE|FADE|HFADE)\x0A'), self.__MatchFadeMode, None)
            self.AddMatchString(compile(rb'DATA PLAYER_PLAYLIST_INDEX ([AB]) ([1-9]{1,2})\x0A'), self.__MatchPlaylist, None)
            self.AddMatchString(compile(rb'DATA PLAYER_MUTE ([AB]) (YES|NO)\x0A'), self.__MatchMute, None)
            self.AddMatchString(compile(rb'DATA PLAYER_VARISPEED ([AB]) (?:(-50|-(?:[1-4]?[0-9]))|(50|(?:[1-4]?[0-9])))\x0A'), self.__MatchPlaybackTempoVariation, None)
            self.AddMatchString(compile(rb'DATA PLAYER_TIME ([AB]) (\d{2}:\d{2}) (\d{2}:\d{2}) (\d{2}:\d{2})\x0A'), self.__MatchPlayerTime, None)
            self.AddMatchString(compile(rb'DATA PLAYER_PLAY_MODE ([AB]) (SEQUENTIAL|RANDOM)\x0A'), self.__MatchPlayMode, None)
            self.AddMatchString(compile(rb'DATA PRESET_INDEX (20|(?:1?[0-9]))\x0A'), self.__MatchPreset, None)
            self.AddMatchString(compile(rb'DATA PRIORITY_STATUS ([12]) (RUNNING|STOPPED)\x0A'), self.__MatchPriorityStatus, None)
            self.AddMatchString(compile(rb'DATA PLAYER_REPEAT_MODE ([AB]) (PLAY_ALL|PLAY_ONE|REPEAT_ALL|REPEAT_ONE)\x0A'), self.__MatchRepeatMode, None)
            self.AddMatchString(compile(rb'DATA PLAYER_TRANSPORT_STATUS ([AB]) (STOPPED|PLAYING|PAUSE)\x0A'), self.__MatchTransport, None)
            self.AddMatchString(compile(rb'DATA PLAYER_VOLUME ([AB]) (100|(?:[0-9]{1,2}))\x0A'), self.__MatchVolume, None)
            self.AddMatchString(compile(rb'ERROR (\d{1,2}) "(.*?)"\n'), self.__MatchError, None)

    def SetConnect(self, value, qualifier):

        self.Send('SYSTEM CONNECT\x0A')

    def UpdateCurrentlyPlaying(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            CurrentlyPlayingCmdString = 'GET PLAYER_ITEM_TAGS {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('CurrentlyPlaying', CurrentlyPlayingCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateCurrentlyPlaying')

    def __MatchCurrentlyPlaying(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        TagStates = {
            'ALIAS':  'Alias',
            'TITLE':  'Title',
            'ARTIST': 'Artist', 
            'ALBUM':  'Album',
            'NAME':   'Name'
        }

        qualifier = dict()
        qualifier['Tag'] = TagStates[match.group(1).decode()]
        qualifier['Player'] = PlayerStates[match.group(2).decode()]
        value = match.group(3).decode()
        self.WriteStatus('CurrentlyPlaying', value, qualifier)

    def SetFadeMode(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'None':   'NONE',
            'X Fade': 'XFADE',
            'Fade':   'FADE',
            'H Fade': 'HFADE'
        }

        FadeModeCmdString = 'SET PLAYER_FADE_MODE {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], ValueStateValues[value])
        self.__SetHelper('FadeMode', FadeModeCmdString, value, qualifier)

    def UpdateFadeMode(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            FadeModeCmdString = 'GET PLAYER_FADE_MODE {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('FadeMode', FadeModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFadeMode')

    def __MatchFadeMode(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'NONE':  'None',
            'XFADE': 'X Fade',
            'FADE':  'Fade',
            'HFADE': 'H Fade'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('FadeMode', value, qualifier)

    def SetMute(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'On':  'YES',
            'Off': 'NO'
        }

        MuteCmdString = 'SET PLAYER_MUTE {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], ValueStateValues[value])
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def UpdateMute(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            MuteCmdString = 'GET PLAYER_MUTE {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'YES': 'On',
            'NO':  'Off'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Mute', value, qualifier)

    def SetPlaybackTempoVariation(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueConstraints = {
            'Min': -50,
            'Max': 50
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PlaybackTempoVariationCmdString = 'SET PLAYER_VARISPEED {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], value)
            self.__SetHelper('PlaybackTempoVariation', PlaybackTempoVariationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaybackTempoVariation')

    def UpdatePlaybackTempoVariation(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            PlaybackTempoVariationCmdString = 'GET PLAYER_VARISPEED {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('PlaybackTempoVariation', PlaybackTempoVariationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlaybackTempoVariation')

    def __MatchPlaybackTempoVariation(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        if match.group(2):
            value = int(match.group(2).decode())
        else:
            value = int(match.group(3).decode())
        self.WriteStatus('PlaybackTempoVariation', value, qualifier)

    def UpdatePlayerTime(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            PlayerTimeCmdString = 'SUBSCRIBE PLAYER_TIME {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('PlayerTime', PlayerTimeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlayerTime')

    def __MatchPlayerTime(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        temp_player = PlayerStates[match.group(1).decode()]
        self.WriteStatus('PlayerTime', match.group(2).decode(), {'Player' : temp_player, 'Type' : 'Time Elapsed'})
        self.WriteStatus('PlayerTime', match.group(3).decode(), {'Player' : temp_player, 'Type' : 'Time Remaining'})
        self.WriteStatus('PlayerTime', match.group(4).decode(), {'Player' : temp_player, 'Type' : 'Total Time'})

    def SetPlaylist(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueConstraints = {
            'Min': 1,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            PlaylistCmdString = 'SET PLAYER_PLAYLIST_INDEX {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], value)
            self.__SetHelper('Playlist', PlaylistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlaylist')

    def UpdatePlaylist(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            PlaylistCmdString = 'GET PLAYER_PLAYLIST_INDEX {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('Playlist', PlaylistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlaylist')

    def __MatchPlaylist(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('Playlist', value, qualifier)

    def SetPlayMode(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'Sequential': 'SEQUENTIAL',
            'Random':     'RANDOM'
        }

        PlayModeCmdString = 'SET PLAYER_PLAY_MODE {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], ValueStateValues[value])
        self.__SetHelper('PlayMode', PlayModeCmdString, value, qualifier)

    def UpdatePlayMode(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            PlayModeCmdString = 'GET PLAYER_PLAY_MODE {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('PlayMode', PlayModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePlayMode')

    def __MatchPlayMode(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'SEQUENTIAL': 'Sequential',
            'RANDOM':     'Random'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PlayMode', value, qualifier)

    def SetPreset(self, value, qualifier):

        if 1 <= int(value) <= 20:
            PresetCmdString = 'SET PRESET_INDEX {0}\x0A'.format(value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = 'GET PRESET_INDEX\x0A'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        value = match.group(1).decode()
        self.WriteStatus('Preset', value, None)

    def UpdatePriorityStatus(self, value, qualifier):

        if qualifier['Priority'] in ['1', '2']:
            PriorityStatusCmdString = 'GET PRIORITY_STATUS {0}\x0A'.format(qualifier['Priority'])
            self.__UpdateHelper('PriorityStatus', PriorityStatusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePriorityStatus')

    def __MatchPriorityStatus(self, match, tag):

        PriorityStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'RUNNING': 'Running',
            'STOPPED': 'Stopped'
        }

        qualifier = dict()
        qualifier['Priority'] = PriorityStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('PriorityStatus', value, qualifier)

    def SetRepeatMode(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'Play All':   'PLAY_ALL',
            'Play One':   'PLAY_ONE',
            'Repeat All': 'REPEAT_ALL',
            'Repeat One': 'REPEAT_ONE'
        }

        RepeatModeCmdString = 'SET PLAYER_REPEAT_MODE {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], ValueStateValues[value])
        self.__SetHelper('RepeatMode', RepeatModeCmdString, value, qualifier)

    def UpdateRepeatMode(self, value, qualifier):

        if qualifier['Player'] in ['A','B']:
            RepeatModeCmdString = 'GET PLAYER_REPEAT_MODE {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('RepeatMode', RepeatModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateRepeatMode')

    def __MatchRepeatMode(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'PLAY_ALL':   'Play All',
            'PLAY_ONE':   'Play One',
            'REPEAT_ALL': 'Repeat All',
            'REPEAT_ONE': 'Repeat One'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('RepeatMode', value, qualifier)

    def SetTransport(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'Play':  'PLAY',
            'Pause': 'PAUSE',
            'Stop':  'STOP'
        }

        TransportCmdString = 'SET PLAYER_TRANSPORT_CONTROL {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            TransportCmdString = 'GET PLAYER_TRANSPORT_STATUS {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateTransport')

    def __MatchTransport(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueStateValues = {
            'PLAYING': 'Play',
            'PAUSE':   'Pause',
            'STOPPED': 'Stop'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('Transport', value, qualifier)

    def SetVolume(self, value, qualifier):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'SET PLAYER_VOLUME {0} {1}\x0A'.format(PlayerStates[qualifier['Player']], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        if qualifier['Player'] in ['A', 'B']:
            VolumeCmdString = 'GET PLAYER_VOLUME {0}\x0A'.format(qualifier['Player'])
            self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateVolume')

    def __MatchVolume(self, match, tag):

        PlayerStates = {
            'A': 'A',
            'B': 'B'
        }

        qualifier = dict()
        qualifier['Player'] = PlayerStates[match.group(1).decode()]
        value = int(match.group(2).decode())
        self.WriteStatus('Volume', value, qualifier)

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

    def __MatchError(self, match, tag):
        self.counter = 0
        error_code = match.group(1).decode()
        error_msg = match.group(2).decode()
        if error_code in ['9', '10']: 
            self.SetConnect( None, None)
        self.Error(['Error {}: {}'.format(error_code, error_msg)])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0
        self.SetConnect( None, None)

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
        
        #check incoming data if it matched any expected data from device module
        for regexString, CurrentMatch in self.__matchStringDict.items():
            while True:
                result = search(regexString, self.__receiveBuffer)
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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models: 
                print('Model mismatch')              
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])


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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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