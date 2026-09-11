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

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ClearPlaylist': {'Status': {}},
            'Clip': {'Parameters': ['Output'], 'Status': {}},
            'ContactClosureInput': {'Parameters': ['Input'], 'Status': {}},
            'ContactClosureInputTrigger': {'Status': {}},
            'CreatePlaylist': {'Status': {}},
            'DeletePlaylist': {'Status': {}},
            'LoadPlaylist': {'Parameters': ['Output'], 'Status': {}},
            'OutputRelay': {'Parameters': ['Output'], 'Status': {}},
            'OutputResolution': {'Parameters': ['Output'], 'Status': {}},
            'PlaylistList': {'Parameters': ['Position'], 'Status': {}},
            'PlaylistListNavigation': {'Parameters': ['Step'], 'Status': {}},
            'PlaylistListUpdate': {'Status': {}},
            'PresentationLoop': {'Parameters': ['Output'], 'Status': {}},
            'Reboot': {'Status': {}},
            'RemainingHardDriveSpace': {'Status': {}},
            'Transport': {'Parameters': ['Output'], 'Status': {}},
            'VideoMode': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
            'Volume': {'Parameters': ['Output'], 'Status': {}}
        }

        self.PlaylistList = []
        self.PlaylistListStartIndex = 0

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'(Playlist [.\S\s]*)Playlist\r'), self.__MatchPlaylistListUpdate, None)
            self.AddMatchString(re.compile(b'AudioMute (1|2) (0|1)\r'), self.__MatchAudioMute, 'Valid')
            self.AddMatchString(re.compile(b'AudioMute\r'), self.__MatchAudioMute, 'Invalid')
            self.AddMatchString(re.compile(b'inputstate "1(\+|\-)" "2(\+|\-)" "3(\+|\-)" "4(\+|\-)"\r'), self.__MatchContactClosureInput, None)
            self.AddMatchString(re.compile(b'outputstate "([1-4])(\+|\-)"\r'), self.__MatchOutputRelay, None)
            self.AddMatchString(re.compile(b'LoopMode (ON|OFF)\r'), self.__MatchPresentationLoop, '1')
            self.AddMatchString(re.compile(b'LoopMode (ON|OFF) (ON|OFF)\r'), self.__MatchPresentationLoop, '2')
            self.AddMatchString(re.compile(b'StateEx (1|2) "playstate" "(playing|paused|stopped)"\r'), self.__MatchTransport, 'Valid')
            self.AddMatchString(re.compile(b'StateEx\r'), self.__MatchTransport, 'Invalid')
            self.AddMatchString(re.compile(b'AudioVolume (1|2) ([+-]\d{1,3}) (?:[+-]\d{1,3})\r'), self.__MatchVolume, 'Valid')
            self.AddMatchString(re.compile(b'AudioVolume\r'), self.__MatchVolume, 'Invalid')
            self.AddMatchString(re.compile(b'VideoMode (1_channel|2_channel|2_channel_locked)\r'), self.__MatchVideoMode, None)
            self.AddMatchString(re.compile(b'diskinfo (\d*) (\d*)\r'), self.__MatchRemainingHardDriveSpace, None)
            self.AddMatchString(re.compile(b'OutputResolution (1|2) ([\d\.]*) ([\d\.]*) (i|p) ([\d\.]*)\r'), self.__MatchOutputResolution, None)
            self.AddMatchString(re.compile(b'ERROR\r'), self.__MatchError, None)

        self.PlaylistNames = re.compile(b'Playlist "(.*)"')
        self.VideoMode = 'Single Channel'

    @property
    def VideoMode(self):
        return self._VideoMode

    @VideoMode.setter
    def VideoMode(self, value):
        if 'Dual Channel' in value:
            self._VideoMode = 'Dual Channel'
        elif value == 'Single Channel':
            self._VideoMode = value
        else:
            print('Invalid VideoMode')

    def __PlaylistListPositionHandler(self):

        index = self.PlaylistListStartIndex

        position = 1
        while (index < len(self.PlaylistList)):
            self.WriteStatus('PlaylistList', self.PlaylistList[index], {'Position': str(position)})
            position += 1
            index += 1
        else:

            while (position <= 10):
                self.WriteStatus('PlaylistList', '', {'Position': str(position)})
                position += 1

    def SetClearPlaylist(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        if self.PlaylistList:
            try:
                if self.PlaylistList[(self.PlaylistListStartIndex - 1) + int(ValueStateValues[value])] != '***End of List***':
                    ClearPlaylistCmdString = 'ClearPlaylist "{0}"\r'.format(self.PlaylistList[(self.PlaylistListStartIndex - 1) + int(ValueStateValues[value])])
                    self.__SetHelper('ClearPlaylist', ClearPlaylistCmdString, value, qualifier)
                else:
                    print('Inappropriate Command')
            except(IndexError):
                print('Playlist Selection Out of Range.')
        else:
            print('Inappropriate Command for SetClearPlaylist')

    def SetCreatePlaylist(self, value, qualifier):

        if value[-9:] == '.espl.xml':
            CreatePlaylistString = 'CreatePlaylist "{0}"\r'.format(value)
        else:
            CreatePlaylistString = 'CreatePlaylist "{0}.espl.xml"\r'.format(value)

        self.__SetHelper('CreatePlaylist', CreatePlaylistString, value, qualifier)
        self.SetPlaylistListUpdate(None, None)

    def SetDeletePlaylist(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        if self.PlaylistList:
            try:
                if self.PlaylistList[(self.PlaylistListStartIndex - 1) + int(ValueStateValues[value])] != '***End of List***':
                    DeletePlaylistCmdString = 'DeletePlaylist "{0}"\r'.format(self.PlaylistList[(self.PlaylistListStartIndex - 1) + int(ValueStateValues[value])])
                    self.__SetHelper('DeletePlaylist', DeletePlaylistCmdString, value, qualifier)
                    self.SetPlaylistListUpdate(None, None)
                else:
                    print('Inappropriate Command')
            except(IndexError):
                print('Playlist Selection Out of Range.')
        else:
            print('Inappropriate Command for SetDeletePlaylist')

    def SetLoadPlaylist(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }

        OutputStates = {
            '1': '1',
            '2': '2',
        }

        try:
            val = self.PlaylistList[(self.PlaylistListStartIndex - 1) + int(ValueStateValues[value])]
            if val and val != '***End of List***':
                LoadPlaylistCmdString = 'LoadPlaylist {0} "{1}"\r'.format(OutputStates[qualifier['Output']], val)
                self.__SetHelper('LoadPlaylist', LoadPlaylistCmdString, value, qualifier)
            else:
                print('Inappropriate Command')
        except(IndexError):
            print('Playlist Selection Out of Range.')

    def UpdatePlaylistList(self, value, qualifier):
        self.SetPlaylistListUpdate(value, qualifier)

    def SetPlaylistListNavigation(self, value, qualifier):

        StepStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10'
        }
        step = int(StepStates[qualifier['Step']])
        if self.PlaylistList:

            if value == 'Up':

                if self.PlaylistListStartIndex - step >= 0:
                    self.PlaylistListStartIndex -= step
                else:
                    self.PlaylistListStartIndex = 0
            if value == 'Down':

                if self.PlaylistListStartIndex + step <= len(self.PlaylistList) - 1:
                    self.PlaylistListStartIndex += step
                else:
                    self.PlaylistListStartIndex = len(self.PlaylistList) - 1
                    if self.PlaylistListStartIndex < 0:
                        self.PlaylistListStartIndex = 0

            self.__PlaylistListPositionHandler()
        else:
            print('Inappropriate Command for SetPlaylistListNavigation')

    def SetPlaylistListUpdate(self, value, qualifier):
        if not self.PlaylistList:
            self.PlaylistList.append("***End of List***")
        PlaylistListUpdateCmdString = 'ListAllPlaylists\r'
        self.__SetHelper('PlaylistListUpdate', PlaylistListUpdateCmdString, value, qualifier)
        self.__PlaylistListPositionHandler()

    def __MatchPlaylistListUpdate(self, match, tag):
        self.PlaylistList.clear()
        PlaylistIter = re.finditer(self.PlaylistNames, match.group(1))
        for name in PlaylistIter:
            self.PlaylistList.append(name.group(1).decode())
        self.PlaylistList.append("***End of List***")
        self.__PlaylistListPositionHandler()

    def SetClip(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'Next': 'Next {0}\r',
            'Previous': 'Previous {0}\r'
        }

        ClipCmdString = ValueStateValues[value].format(OutputStates[qualifier['Output']])
        self.__SetHelper('Clip', ClipCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        AudioMuteCmdString = 'SetAudioMute {0} {1}\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        AudioMuteCmdString = 'GetAudioMute {0}\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        OutputStates = {
            '1': '1',
            '2': '2',
        }

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        mode = self._VideoMode
        if mode == 'Single Channel' and tag == 'Invalid':
            qualifier = {}
            qualifier['Output'] = '2'
            value = 'Invalid Output'
            self.WriteStatus('AudioMute', value, qualifier)
        elif match.group(0).decode() != 'AudioMute\r':
            qualifier = {}
            qualifier['Output'] = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('AudioMute', value, qualifier)

    def UpdateContactClosureInput(self, value, qualifier):

        ContactClosureInputCmdString = 'GetInput\r'
        self.__UpdateHelper('ContactClosureInput', ContactClosureInputCmdString, value, qualifier)

    def __MatchContactClosureInput(self, match, tag):

        ValueStateValues = {
            '+': '+',
            '-': '-'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('ContactClosureInput', value, {'Input': '1'})

        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('ContactClosureInput', value, {'Input': '2'})

        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('ContactClosureInput', value, {'Input': '3'})

        value = ValueStateValues[match.group(4).decode()]
        self.WriteStatus('ContactClosureInput', value, {'Input': '4'})

    def SetContactClosureInputTrigger(self, value, qualifier):

        ValueStateValues = {
            'On': 'SetInputTrigger On\r',
            'Off': 'SetInputTrigger Off\r'
        }

        ContactClosureInputTriggerCmdString = ValueStateValues[value]
        self.__SetHelper('ContactClosureInputTrigger', ContactClosureInputTriggerCmdString, value, qualifier)

    def SetOutputRelay(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '+': '+',
            '-': '-'
        }

        OutputRelayCmdString = 'Setoutput {0}{1}\r'.format(OutputStates[qualifier['Output']], ValueStateValues[value])
        self.__SetHelper('Output', OutputRelayCmdString, value, qualifier)

    def UpdateOutputRelay(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        OutputCmdString = 'GetOutput {0}\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputRelay', OutputCmdString, value, qualifier)

    def __MatchOutputRelay(self, match, tag):

        OutputStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4'
        }

        ValueStateValues = {
            '+': '+',
            '-': '-'
        }

        qualifier = {}
        qualifier['Output'] = OutputStates[match.group(1).decode()]
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputRelay', value, qualifier)

    def UpdateOutputResolution(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }
        OutputResolutionCmdString = 'GetOutputResolution {0}\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('OutputResolution', OutputResolutionCmdString, value, qualifier)

    def __MatchOutputResolution(self, match, tag):

        OutputStateValues = {
            '1': '1',
            '2': '2'
        }

        qualifier = {}
        qualifier = {'Output': OutputStateValues[match.group(1).decode()]}
        HorizontalResolution = match.group(2).decode()
        VerticalResolution = match.group(3).decode()
        ScanType = match.group(4).decode()
        FrameRate = match.group(5).decode()

        value = HorizontalResolution + "x" + VerticalResolution + ScanType + ", at " + FrameRate + "fps"
        self.WriteStatus('OutputResolution', value, qualifier)

    def SetPresentationLoop(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': 'Loopon {0}\r',
            'Off': 'Loopoff {0}\r'
        }

        PresentationLoopCmdString = ValueStateValues[value].format(OutputStates[qualifier['Output']])
        self.__SetHelper('PresentationLoop', PresentationLoopCmdString, value, qualifier)

    def UpdatePresentationLoop(self, value, qualifier):

        PresentationLoopCmdString = 'GetLoopMode\r'
        self.__UpdateHelper('PresentationLoop', PresentationLoopCmdString, value, qualifier)

    def __MatchPresentationLoop(self, match, tag):

        ValueStateValues = {
            'ON': 'On',
            'OFF': 'Off'
        }

        if tag == '1':
            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('PresentationLoop', value, {'Output': '1'})
            self.WriteStatus('PresentationLoop', 'Invalid Output', {'Output': '2'})
        else:
            value = ValueStateValues[match.group(1).decode()]
            self.WriteStatus('PresentationLoop', value, {'Output': '1'})

            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('PresentationLoop', value, {'Output': '2'})

    def SetReboot(self, value, qualifier):

        RebootCmdString = 'Reboot\r'
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def UpdateRemainingHardDriveSpace(self, value, qualifier):

        RemainingHardDriveSpaceCmdString = 'GetDiskInfo\r'
        self.__UpdateHelper('RemainingHardDriveSpace', RemainingHardDriveSpaceCmdString, value, qualifier)

    def __MatchRemainingHardDriveSpace(self, match, tag):

        TotalSpace = match.group(1).decode()
        FreeSpace = match.group(2).decode()
        value = FreeSpace + "KB remaining out of total space " + TotalSpace + "KB"
        self.WriteStatus('RemainingHardDriveSpace', value, None)

    def SetTransport(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'Play': 'Play {0}\r',
            'Pause': 'Pause {0}\r',
            'Stop': 'Stop {0}\r',
            'Fast Forward 3x': 'Play {0} 3\r',
            'Fast Forward 5x': 'Play {0} 5\r',
            'Fast Forward 10x': 'Play {0} 10\r',
            'Fast Forward 15x': 'Play {0} 15\r',
            'Fast Forward 20x': 'Play {0} 20\r',
            'Fast Forward 25x': 'Play {0} 25\r',
            'Rewind 3x': 'Play {0} -3\r',
            'Rewind 5x': 'Play {0} -5\r',
            'Rewind 10x': 'Play {0} -10\r',
            'Rewind 15x': 'Play {0} -15\r',
            'Rewind 20x': 'Play {0} -20\r',
            'Rewind 25x': 'Play {0} -25\r'
        }

        TransportCmdString = ValueStateValues[value].format(OutputStates[qualifier['Output']])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def UpdateTransport(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        TransportCmdString = 'GetStateEx {0} Playstate\r'.format(qualifier['Output'])
        self.__UpdateHelper('Transport', TransportCmdString, value, qualifier)

    def __MatchTransport(self, match, tag):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'playing': 'Play',
            'paused': 'Pause',
            'stopped': 'Stop',
        }

        mode = self._VideoMode
        if mode == 'Single Channel' and tag == 'Invalid':
            qualifier = {}
            qualifier['Output'] = '2'
            value = 'Invalid Output'
            self.WriteStatus('Transport', value, qualifier)
        elif match.group(0).decode() != 'StateEx\r':
            qualifier = {}
            qualifier['Output'] = OutputStates[match.group(1).decode()]
            value = ValueStateValues[match.group(2).decode()]
            self.WriteStatus('Transport', value, qualifier)

    def SetVideoMode(self, value, qualifier):
        ValueStateValues = {
            'Single Channel': '1_channel',
            'Dual Channel': '2_channel',
            'Dual Channel Locked': '2_channel_locked'
        }

        VideoModeCmdString = 'SetVideoMode {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('VideoMode', VideoModeCmdString, value, qualifier)

    def UpdateVideoMode(self, value, qualifier):
        VideoModeCmdString = 'GetVideoMode\r'
        self.__UpdateHelper('VideoMode', VideoModeCmdString, value, qualifier)

    def __MatchVideoMode(self, match, tag):
        ValueStateValues = {
            '1_channel': 'Single Channel',
            '2_channel': 'Dual Channel',
            '2_channel_locked': 'Dual Channel Locked'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('VideoMode', value, None)
        self.VideoMode = value

    def SetVideoMute(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueStateValues = {
            'On': 'VideoOff {0}\r',
            'Off': 'VideoOn {0}\r'
        }

        VideoMuteCmdString = ValueStateValues[value].format(OutputStates[qualifier['Output']])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        ValueConstraints = {
            'Min': -144,
            'Max': 0
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'SetAudioVolume {0} {1}\r'.format(OutputStates[qualifier['Output']], value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Inappropriate Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        VolumeCmdString = 'GetAudioVolume {0}\r'.format(OutputStates[qualifier['Output']])
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        OutputStates = {
            '1': '1',
            '2': '2'
        }

        mode = self._VideoMode
        if mode == 'Single Channel' and tag == 'Invalid':
            qualifier = {}
            qualifier['Output'] = '2'
            value = -144
            self.WriteStatus('Volume', value, qualifier)
        elif match.group(0).decode() != 'AudioVolume\r':
            qualifier = {}
            qualifier['Output'] = OutputStates[match.group(1).decode()]
            value = int(match.group(2).decode())
            self.WriteStatus('Volume', value, qualifier)

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
        value = match.group(0).decode()
        print(value[:-1])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.PlaylistListStartIndex = 0
        self.PlaylistList = []

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
