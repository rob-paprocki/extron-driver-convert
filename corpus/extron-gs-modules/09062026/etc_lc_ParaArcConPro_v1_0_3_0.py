from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self._Delimiter = '\r'
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ChannelIntensity': {'Parameters': ['Channel Name', 'Space Name'], 'Status': {}},
            'GroupIntensity': {'Parameters': ['Group Name', 'Space Name'], 'Status': {}},
            'GroupIntensityRamp': {'Parameters': ['Group Name', 'Space Name', 'Fade Time'], 'Status': {}},
            'Macro': {'Parameters': ['Macro Name'], 'Status': {}},
            'Override': {'Parameters': ['Override Name'], 'Status': {}},
            'Preset': {'Parameters': ['Preset Name', 'Space Name'], 'Status': {}},
            'PresetRamp': {'Parameters': ['Preset Name', 'Space Name', 'Fade Time'], 'Status': {}},
            'Sequence': {'Parameters': ['Sequence Name', 'Space Name'], 'Status': {}},
            'Wall': {'Parameters': ['Wall Name', 'Space Name'], 'Status': {}},
        }

        if self.Unidirectional == 'False':  # All return data on Page 6 of serial protocol
            self.AddMatchString(re.compile(b'chan int:(?P<level>[0-9]{1,3}) (?P<name>.+)[\r\n]{1,2}'), self.__MatchChannelIntensity, None)
            self.AddMatchString(re.compile(b'grp int:(?P<level>[0-9]{1,3}) (?P<name>.+)[\r\n]{1,2}'), self.__MatchGroupIntensity, None)
            self.AddMatchString(re.compile(b'macro (?P<status>on|off|running) (?P<name>.+)[\r\n]{1,2}'), self.__MatchMacro, None)
            self.AddMatchString(re.compile(b'ovr (?P<status>enab|disab) (?P<name>.+)[\r\n]{1,2}'), self.__MatchOverride, None)
            self.AddMatchString(re.compile(b'pst (?P<status>act|dact|alt) (?P<name>.+)[\r\n]{1,2}'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'seq (?P<status>start|stop|pause) (?P<name>.+)[\r\n]{1,2}'), self.__MatchSequence, None)
            self.AddMatchString(re.compile(b'wall (?P<status>open|close) (?P<name>.+)[\r\n]{1,2}'), self.__MatchWall, None)

    @property
    def Delimiter(self):
        return self._Delimiter

    @Delimiter.setter
    def Delimiter(self, value):
        
        Delimiters = {
                      'Carriage Return': '\r',
                      'Line Feed': '\n',
                      'Carriage Return + Line Feed': '\r\n'
                      }
        try:
            self._Delimiter = Delimiters[value]
        except KeyError:
            print('Invalid Delimeter selected')

    def SetChannelIntensity(self, value, qualifier):

        ChannelName = qualifier['Channel Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if 0 <= value <= 255 and ChannelName:
            ChannelIntensityCmdString = 'chan int:{0} {1}'.format(value, ChannelName)
            if SpaceName:
                ChannelIntensityCmdString += ', {0}'.format(SpaceName)

            self.__SetHelper('ChannelIntensity', ChannelIntensityCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelIntensity')

    def UpdateChannelIntensity(self, value, qualifier):

        ChannelName = qualifier['Channel Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if ChannelName:
            ChannelIntensityCmdString = 'chan get {0}'.format(ChannelName)
            if SpaceName:
                ChannelIntensityCmdString += ', {0}'.format(SpaceName)
            self.__UpdateHelper('ChannelIntensity', ChannelIntensityCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateChannelIntensity')

    def __MatchChannelIntensity(self, match, tag):

        nameList = match.group('name').decode().split(',')  # ['channel name','space name']
        qualifier = {'Channel Name': nameList[0].strip()}

        try:
            qualifier['Space Name'] = nameList[1].strip()
        except IndexError:
            qualifier['Space Name'] = ''

        value = int(match.group('level').decode())
        self.WriteStatus('ChannelIntensity', value, qualifier)

    def SetGroupIntensity(self, value, qualifier):

        GroupName = qualifier['Group Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if 0 <= value <= 255 and GroupName:
            GroupIntensityCmdString = 'grp int:{0} {1}'.format(value, GroupName)
            if SpaceName:
                GroupIntensityCmdString += ', {0}'.format(SpaceName)
            self.__SetHelper('GroupIntensity', GroupIntensityCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupIntensity')

    def UpdateGroupIntensity(self, value, qualifier):

        GroupName = qualifier['Group Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if GroupName:
            GroupIntensityCmdString = 'grp get {0}'.format(GroupName)
            if SpaceName:
                GroupIntensityCmdString += ', {0}'.format(SpaceName)
            self.__UpdateHelper('GroupIntensity', GroupIntensityCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateGroupIntensity')

    def __MatchGroupIntensity(self, match, tag):

        nameList = match.group('name').decode().split(',')  # ['group name','space name']
        qualifier = {'Group Name': nameList[0].strip()}

        try:
            qualifier['Space Name'] = nameList[1].strip()
        except IndexError:
            qualifier['Space Name'] = ''

        value = int(match.group('level').decode())
        self.WriteStatus('GroupIntensity', value, qualifier)

    def SetGroupIntensityRamp(self, value, qualifier):

        GroupName = qualifier['Group Name']  # Required
        SpaceName = qualifier['Space Name']  # Required
        FadeTime = qualifier['Fade Time']  # Required

        if 0 <= value <= 255 and GroupName and SpaceName and 0 <= FadeTime <= 9.9:
            GroupIntensityRampCmdString = 'grp int:{0} {1}, {2}, {3:.1f}'.format(value, GroupName, SpaceName, FadeTime)
            self.__SetHelper('GroupIntensityRamp', GroupIntensityRampCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupIntensityRamp')

    def SetMacro(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off',
            'Cancel': 'cancel',
        }

        MacroName = qualifier['Macro Name']  # Required
        if MacroName:
            MacroCmdString = 'macro {0} {1}'.format(ValueStateValues[value], MacroName)
            self.__SetHelper('Macro', MacroCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMacro')

    def UpdateMacro(self, value, qualifier):

        MacroName = qualifier['Macro Name']  # Required

        if MacroName:
            MacroCmdString = 'macro get {0}'.format(MacroName)
            self.__UpdateHelper('Macro', MacroCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateMacro')

    def __MatchMacro(self, match, tag):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off',
            'running': 'Running'
        }

        qualifier = {'Macro Name': match.group('name').decode()}
        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('Macro', value, qualifier)

    def SetOverride(self, value, qualifier):

        ValueStateValues = {
            'On': 'enab',
            'Off': 'disab'
        }

        OverrideName = qualifier['Override Name']  # Required
        if OverrideName:
            OverrideCmdString = 'ovr {0} {1}'.format(ValueStateValues[value], OverrideName)
            self.__SetHelper('Override', OverrideCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOverride')

    def UpdateOverride(self, value, qualifier):

        OverrideName = qualifier['Override Name']  # Required

        if OverrideName:
            OverrideCmdString = 'ovr get {0}'.format(OverrideName)
            self.__UpdateHelper('Override', OverrideCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOverride')

    def __MatchOverride(self, match, tag):

        ValueStateValues = {
            'enab': 'On',
            'disab': 'Off'
        }

        qualifier = {'Override Name': match.group('name').decode()}
        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('Override', value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            'Activate': 'act',
            'Deactivate': 'dact',
            'Record': 'rec'
        }

        PresetName = qualifier['Preset Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional
        if PresetName:
            PresetCmdString = 'pst {0} {1}'.format(ValueStateValues[value], PresetName)
            if SpaceName:
                PresetCmdString += ', {0}'.format(SpaceName)
            self.__SetHelper('Preset', PresetCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetName = qualifier['Preset Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional
        if PresetName:
            PresetCmdString = 'pst get {0}'.format(PresetName)
            if SpaceName:
                PresetCmdString += ', {0}'.format(SpaceName)
            self.__UpdateHelper('Preset', PresetCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdatePreset')

    def __MatchPreset(self, match, tag):

        ValueStateValues = {
            'act': 'Activate',
            'dact': 'Deactivate',
            'alt': 'Altered'
        }

        nameList = match.group('name').decode().split(',')  # ['preset name','space name']
        qualifier = {'Preset Name': nameList[0].strip()}
        try:
            qualifier['Space Name'] = nameList[1].strip()
        except IndexError:
            qualifier['Space Name'] = ''

        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('Preset', value, qualifier)

    def SetPresetRamp(self, value, qualifier):

        ValueStateValues = {
            'Activate': 'act',
            'Deactivate': 'dact'
        }

        PresetName = qualifier['Preset Name']  # Required
        SpaceName = qualifier['Space Name']  # Required
        FadeTime = qualifier['Fade Time']  # Required

        if PresetName and SpaceName and 0 <= FadeTime <= 9.9:
            PresetRampCmdString = 'pst {0} {1}, {2}, {3:.1f}'.format(ValueStateValues[value], PresetName, SpaceName, FadeTime)
            self.__SetHelper('PresetRamp', PresetRampCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRamp')

    def SetSequence(self, value, qualifier):

        ValueStateValues = {
            'Start': 'start',
            'Stop': 'stop',
            'Pause': 'pause',
            'Resume': 'resume'
        }

        SequenceName = qualifier['Sequence Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if SequenceName:
            SequenceCmdString = 'seq {0} {1}'.format(ValueStateValues[value], SequenceName)
            if SpaceName and value in ['Start', 'Stop']:
                SequenceCmdString += ', {0}'.format(SpaceName)
            self.__SetHelper('Sequence', SequenceCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSequence')

    def UpdateSequence(self, value, qualifier):

        SequenceName = qualifier['Sequence Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if SequenceName:
            SequenceCmdString = 'seq get {0}'.format(SequenceName)
            if SpaceName:
                SequenceCmdString += ', {0}'.format(SpaceName)
            self.__UpdateHelper('Sequence', SequenceCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSequence')

    def __MatchSequence(self, match, tag):

        ValueStateValues = {
            'start': 'Start',
            'stop': 'Stop',
            'pause': 'Pause'
        }

        nameList = match.group('name').decode().split(',')  # ['sequence name','space name']
        qualifier = {'Sequence Name': nameList[0].strip()}
        try:
            qualifier['Space Name'] = nameList[1].strip()
        except IndexError:
            qualifier['Space Name'] = ''

        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('Sequence', value, qualifier)

    def SetWall(self, value, qualifier):

        ValueStateValues = {
            'Open': 'open',
            'Close': 'close'
        }

        WallName = qualifier['Wall Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if WallName:
            WallCmdString = 'wall {0} {1}'.format(ValueStateValues[value], WallName)
            if SpaceName:
                WallCmdString += ', {0}'.format(SpaceName)
            self.__SetHelper('Wall', WallCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWall')

    def UpdateWall(self, value, qualifier):

        WallName = qualifier['Wall Name']  # Required
        SpaceName = qualifier['Space Name']  # Optional

        if WallName:
            WallCmdString = 'wall get {0}'.format(WallName)
            if SpaceName:
                WallCmdString += ', {0}'.format(SpaceName)
            self.__UpdateHelper('Wall', WallCmdString + self._Delimiter, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateWall')

    def __MatchWall(self, match, tag):

        ValueStateValues = {
            'open': 'Open',
            'close': 'Close'
        }

        nameList = match.group('name').decode().split(',')  # ['wall name','space name']
        qualifier = {'Wall Name': nameList[0].strip()}
        try:
            qualifier['Space Name'] = nameList[1].strip()
        except IndexError:
            qualifier['Space Name'] = ''
        value = ValueStateValues[match.group('status').decode()]
        self.WriteStatus('Wall', value, qualifier)

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

        value = match.group(0).decode().split(':')
        self.Error([value[1]])

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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
