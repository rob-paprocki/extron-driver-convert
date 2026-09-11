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
            'AntennaStrength': {'Status': {}},
            'ArtistName': {'Status': {}},
            'CategoryName': {'Status': {}},
            'ChangeDisplay': {'Status': {}},
            'ChannelName': {'Status': {}},
            'ChannelNumber': {'Status': {}},
            'ChannelSelect': {'Status': {}},
            'Jump': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PresetSelect': {'Status': {}},
            'RadioID': {'Status': {}},
            'SongTitle': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Current Signal Quality is:\n\r\x20(Good Signal|Marginal Signal|Weak Signal|No Signal)\n\r'), self.__MatchAntennaStrength, None)
            self.AddMatchString(re.compile(b'Current Channel Artist Name:\n\r\x20([^\\\\*]{1,16})\n\r\x20Current Channel Song Title:\n\r\x20([^\\\\*]{1,16})\n\r'), self.__MatchArtistName, None)
            self.AddMatchString(re.compile(b'Current Channel Number is:\x20\x20([^\\\\*]{1,3})\n\rCurrent Channel Name is:\n\r([^\\\\*]{1,16})\n\rCurrent Category Name is:\n\r([^\\\\*]{1,16})\n\r'), self.__MatchChannelNumber, None)
            self.AddMatchString(re.compile(b'The RADIO ID is:\n\r([^\\\\*]{8})\n\r'), self.__MatchRadioID, None)

    def UpdateAntennaStrength(self, value, qualifier):

        AntennaStrengthCmdString = 'GetAntennaStrength\r'
        self.__UpdateHelper('AntennaStrength', AntennaStrengthCmdString, value, qualifier)

    def __MatchAntennaStrength(self, match, tag):

        ValueStateValues = {
            'Good Signal': 'Good Signal',
            'Marginal Signal': 'Marginal Signal',
            'Weak Signal': 'Weak Signal',
            'No Signal': 'No Signal'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('AntennaStrength', value, None)

    def UpdateArtistName(self, value, qualifier):

        ArtistNameCmdString = 'GetSongInformation\r'
        self.__UpdateHelper('ArtistName', ArtistNameCmdString, value, qualifier)

    def __MatchArtistName(self, match, tag):

        escapedCharacters = {
            '\a': 'a',
            '\b': 'b',
            '\f': 'f',
            '\n': 'n',
            '\r': 'r',
            '\t': 't',
            '\o': 'o',
            '\'': "'",
            '\"': '"',
        }
        Artist = match.group(1).decode()
        Title = match.group(2).decode()

        for character in escapedCharacters.keys():
            if character in match.group(1).decode():
                Artist = match.group(1).decode().replace(character, escapedCharacters[character])
            if character in match.group(2).decode():
                Title = match.group(2).decode().replace(character, escapedCharacters[character])

        self.WriteStatus('ArtistName', Artist, None)
        self.WriteStatus('SongTitle', Title, None)

    def UpdateCategoryName(self, value, qualifier):

        CategoryNameCmdString = 'GetChannelInformation\r'
        self.__UpdateHelper('CategoryName', CategoryNameCmdString, value, qualifier)

    def SetChangeDisplay(self, value, qualifier):

        ChangeDisplayCmdString = 'ChangeDisplay\r'
        self.__SetHelper('ChangeDisplay', ChangeDisplayCmdString, value, qualifier)

    def SetChannelSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            ChannelSelectCmdString = 'ChannelSelect {0:03d}\r'.format(int(value))
            self.__SetHelper('ChannelSelect', ChannelSelectCmdString, value, qualifier)

    def UpdateChannelName(self, value, qualifier):

        ChannelNameCmdString = 'GetChannelInformation\r'
        self.__UpdateHelper('ChannelName', ChannelNameCmdString, value, qualifier)

    def UpdateChannelNumber(self, value, qualifier):

        ChannelNumberCmdString = 'GetChannelInformation\r'
        self.__UpdateHelper('ChannelNumber', ChannelNumberCmdString, value, qualifier)

    def __MatchChannelNumber(self, match, tag):

        escapedCharacters = {
            '\a': 'a',
            '\b': 'b',
            '\f': 'f',
            '\n': 'n',
            '\r': 'r',
            '\t': 't',
            '\o': 'o',
            '\'': "'",
            '\"': '"',
        }

        ChanNumber = match.group(1).decode()
        ChanName = match.group(2).decode()
        CatName = match.group(3).decode()

        for character in escapedCharacters.keys():
            if character in match.group(1).decode():
                ChanNumber = match.group(1).decode().replace(character, escapedCharacters[character])
            if character in match.group(2).decode():
                ChanName = match.group(2).decode().replace(character, escapedCharacters[character])
            if character in match.group(3).decode():
                CatName = match.group(3).decode().replace(character, escapedCharacters[character])

        self.WriteStatus('ChannelNumber', ChanNumber, None)
        self.WriteStatus('ChannelName', ChanName, None)
        self.WriteStatus('CategoryName', CatName, None)

    def SetJump(self, value, qualifier):

        JumpCmdString = 'Jump\r'
        self.__SetHelper('Jump', JumpCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 'Menu\r',
            'Up': 'SelectUp 01\r',
            'Down': 'SelectDown 01\r ',
            'Left': 'CategoryLeft 01\r',
            'Right': 'CategoryRight 01\r',
            'Enter': 'Enter\r'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'Mute\r',
            'Off': 'Unmute\r'
        }

        MuteCmdString = ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPresetSelect(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 20
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetSelectCmdString = 'PresetSelect {0:02d}\r'.format(int(value))
            self.__SetHelper('PresetSelect', PresetSelectCmdString, value, qualifier)

    def UpdateRadioID(self, value, qualifier):

        RadioIDCmdString = 'GetHardwareID\r'
        self.__UpdateHelper('RadioID', RadioIDCmdString, value, qualifier)

    def __MatchRadioID(self, match, tag):

        escapedCharacters = {
            '\a': 'a',
            '\b': 'b',
            '\f': 'f',
            '\n': 'n',
            '\r': 'r',
            '\t': 't',
            '\o': 'o',
            '\'': "'",
            '\"': '"',
        }

        value = match.group(1).decode()

        for character in escapedCharacters.keys():
            if character in match.group(1).decode():
                value = match.group(1).decode().replace(character, escapedCharacters[character])

        self.WriteStatus('RadioID', value, None)

    def UpdateSongTitle(self, value, qualifier):

        SongTitleCmdString = 'GetSongInformation\r'
        self.__UpdateHelper('SongTitle', SongTitleCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
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
