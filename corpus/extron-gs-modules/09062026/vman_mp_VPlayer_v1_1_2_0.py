from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
import datetime as dt

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
        self._GroupID = 1
        self._PlaylistLength = ListNavigation()
        self._PlaylistLength.Max = 5
        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'CueUp': {'Parameters': ['Timecode'], 'Status': {}},
            'CurrentClipTimeRemaining': {'Status': {}},
            'Fade': {'Parameters': ['Time'], 'Status': {}},
            'Fullscreen': {'Status': {}},
            'LoadPlaylist': {'Parameters': ['Path', 'List Name'], 'Status': {}},
            'LoopPlaylist': {'Status': {}},
            'PlayClip': {'Status': {}},
            'PlaylistNavigation': {'Status': {}},
            'PlaylistResult': {'Parameters': ['Position'], 'Status': {}},
            'PlaylistResultSet': {'Status': {}},
            'PlaylistUpdate': {'Parameters': ['Result Type'], 'Status': {}},
            'Reboot': {'Status': {}},
            'Shuffle': {'Status': {}},
            'Shutdown': {'Status': {}},
            'Transport': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.Playlist = ListNavigation()
        self.LastPlaylistUpdate = 0
        self.LastPlaylist = ''
        self.CurrentPlaylist = ''

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'([0-9]{1,3})\r\d\r(0|1)\r(0|1)\r(0|1)\r(0|1)\r'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'getstatus\r(\d{2}-\d{2}-\d{2}-\d{2})\r(\d{2}-\d{2}-\d{2}-\d{2})\r'), self.__MatchCurrentClipTimeRemaining, None)

        self.regex = re.compile(b'((?:\d+:\s?[^\\x02]*(\x02|))+)\r')
        
    @property
    def GroupID(self):
        return self._GroupID

    @GroupID.setter
    def GroupID(self, value):
        if 0<= int(value) <= 65535:
            self._GroupID = value
        else:
            print('Invalid GroupID. Range is from 0 to 65535')

    @property
    def PlaylistLength(self):
        return self._PlaylistLength.Max

    @PlaylistLength.setter
    def PlaylistLength(self, value):
        if 1 <= int(value) <= 15:
            self._PlaylistLength.Max = int(value)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = '{0}|1|Mute|{1}\r'.format(self._GroupID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = '{0}|1|GetClipProperties\r'.format(self._GroupID)
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        self.WriteStatus('AudioMute', ValueStateValues[match.group(2).decode()], None)
        self.WriteStatus('Fullscreen', ValueStateValues[match.group(5).decode()], None)
        self.WriteStatus('Shuffle', ValueStateValues[match.group(4).decode()], None)
        self.WriteStatus('LoopPlaylist', ValueStateValues[match.group(3).decode()], None)
        self.WriteStatus('Volume', int(match.group(1).decode()), None)

    def SetCueUp(self, value, qualifier):

        timecode = qualifier['Timecode']
        if timecode:
            CueUpCmdString = '{0}|1|CueUp|{1}\r'.format(self._GroupID, timecode)
            self.__SetHelper('CueUp', CueUpCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCueUp')

    def UpdateCurrentClipTimeRemaining(self, value, qualifier):

        CurrentClipTimeRemainingCmdString = '{0}|1|GetStatus\r'.format(self._GroupID)
        self.__UpdateHelper('CurrentClipTimeRemaining', CurrentClipTimeRemainingCmdString, value, qualifier)

    def __MatchCurrentClipTimeRemaining(self, match, tag):

        currPos = match.group(1).decode().replace('-', ':')
        currPos = currPos.split(':')
        durClip = match.group(2).decode().replace('-', ':')
        durClip = durClip.split(':')

        currPos_dt = dt.timedelta(hours=int(currPos[1]), minutes=int(currPos[2]), seconds=int(currPos[3]))
        durClip_dt = dt.timedelta(hours=int(durClip[1]), minutes=int(durClip[2]), seconds=int(durClip[3]))

        diff = str(durClip_dt - currPos_dt).split(':')
        timeRemaining = '{0}:{1}:{2}'.format(diff[0], diff[1], diff[2])
        self.WriteStatus('CurrentClipTimeRemaining', timeRemaining, None)

    def SetFade(self, value, qualifier):

        ValueStateValues = {
            'In': 'FadeIn',
            'Out': 'FadeOut'
        }

        timeval = qualifier['Time']
        if timeval:
            FadeCmdString = '{0}|1|{1}|{2}\r'.format(self._GroupID, ValueStateValues[value], timeval)
            self.__SetHelper('Fade', FadeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFade')

    def SetFullscreen(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        FullscreenCmdString = '{0}|1|FullScreen|{1}\r'.format(self._GroupID, ValueStateValues[value])
        self.__SetHelper('Fullscreen', FullscreenCmdString, value, qualifier)

    def SetLoadPlaylist(self, value, qualifier):

        path = qualifier['Path']
        name = qualifier['List Name']
        if path and name:
            LoadPlaylistCmdString = '{0}|1|LoadPlaylist|{1}\r'.format(self._GroupID, path + '/' + name)
            self.__SetHelper('LoadPlaylist', LoadPlaylistCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLoadPlaylist')

    def SetLoopPlaylist(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        LoopPlaylistCmdString = '{0}|1|LoopPlaylist|{1}\r'.format(self._GroupID, ValueStateValues[value])
        self.__SetHelper('LoopPlaylist', LoopPlaylistCmdString, value, qualifier)

    def SetPlayClip(self, value, qualifier):

        id = value
        if id:
            PlayClipCmdString = '{0}|1|PlayClip|{1};;;;;\r'.format(self._GroupID, id)
            self.__SetHelper('PlayClip', PlayClipCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPlayClip')

    def SetPlaylistNavigation(self, value, qualifier):

        self.Playlist.Navigate(value, self.WriteStatus)

    def SetPlaylistResultSet(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': self._PlaylistLength.Max
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp_Id = self.ReadStatus('PlaylistResult', {'Position': value})
            if temp_Id not in ['***Not Available***', '***End of list***', None]:
                clipId = temp_Id[:temp_Id.find(':') - 1]
        else:
            self.Discard('Invalid Command for SetPlaylistResultSet')

    def SetPlaylistUpdate(self, value, qualifier):

        self.SetPlaylistUpdateHandler(qualifier)

    def SetPlaylistUpdateHandler(self, qualifier):
        resultType = qualifier['Result Type']
        PlaylistUpdateCmdString = '{}|1|GetPlaylist\r'.format(self._GroupID)
        res = self.SendAndWait(PlaylistUpdateCmdString, 10, deliRex=self.regex)
        if res:
            self.CurrentPlaylist = res
            if self.CurrentPlaylist != self.LastPlaylist:
                self.LastPlaylist = self.CurrentPlaylist
                self.Playlist.Clear()
                try:
                    Lines = self.CurrentPlaylist.split('\x02')

                    if Lines[-1] in ['\r', ''] or len(Lines[-1].strip()) == 0:
                        del Lines[-1]
                    for Line in Lines:
                        if resultType == 'Filename with Path':
                            self.Playlist.Append(''.join([Line.split(':')[0].strip(), ' : ', Line.split(':')[1].strip()]))
                        else:
                            self.Playlist.Append(''.join([Line.split(':')[0].strip(), ' : ', Line.split('/')[-1].strip().rsplit('.', 1)[0]]))
                    if Lines:
                        self.Playlist.End()
                    else:
                        self.Playlist.Empty()
                except (TypeError, AttributeError, KeyError, IndexError):
                    self.Error(['Playlist provided an invalid/unexpected response'])
                self.SetPlaylistNavigation(None, None)

    def SetReboot(self, value, qualifier):

        RebootCmdString = '{0}|1|reboot\r'.format(self._GroupID)
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetShuffle(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        ShuffleCmdString = '{0}|1|Shuffle|{1}\r'.format(self._GroupID, ValueStateValues[value])
        self.__SetHelper('Shuffle', ShuffleCmdString, value, qualifier)

    def SetShutdown(self, value, qualifier):

        ShutdownCmdString = '{0}|1|shutdown\r'.format(self._GroupID)
        self.__SetHelper('Shutdown', ShutdownCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play': 'Play',
            'Previous': 'PrevClip',
            'Next': 'NextClip',
            'Pause': 'Pause'
        }

        TransportCmdString = '{0}|1|{1}\r'.format(self._GroupID, ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}|1|SetVolume|{1}\r'.format(self._GroupID, value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._GroupID == 0:
            self.Discard('Inappropriate Command ' + command)
        else:
            self.Send(commandstring)

            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.LastPlaylistUpdate = 0
        self.LastPlaylist = ''
        self.CurrentPlaylist = ''

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


class ListNavigation:

    EndofList = '***End of list***'
    EmptyList = '***Not Available***'
    InvalidLines = (EndofList, EmptyList, None, '')
    StartingEntry = 0
    Max = 1

    def __init__(self):
        self.Empty()

    def Empty(self):
        self.List = [self.EmptyList]

    def Clear(self):
        self.List.clear()

    def Append(self, Line):
        if Line not in self.InvalidLines:
            self.List.append(Line)

    def End(self):
        self.List.append(self.EndofList)

    def Navigate(self, Direction, WriteFunction):
        if Direction == 'Page Up':
            self.StartingEntry -= self.Max
        elif Direction == 'Page Down':
            self.StartingEntry += self.Max
        elif Direction == 'Up':
            self.StartingEntry -= 1
        elif Direction == 'Down':
            self.StartingEntry += 1

        if self.StartingEntry + self.Max >= len(self.List):
            self.StartingEntry = len(self.List) - self.Max

        if self.StartingEntry < 0:
            self.StartingEntry = 0

        for Button, Line in enumerate(self.List[self.StartingEntry:self.StartingEntry + self.Max], 1):
            WriteFunction('PlaylistResult',Line, {'Position': Button})
    
