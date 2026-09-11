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
            'AudioMute': {'Status': {}},
            'DecoderStatus': {'Parameters': ['Input'], 'Status': {}},
            'Input': {'Status': {}},
            'MultimediaMenu': {'Status': {}},
            'Power': {'Status': {}},
            'PresetRecall': {'Parameters': ['Mode'], 'Status': {}},
            'SetupMenu': {'Status': {}},
            'SetupMenuCall': {'Status': {}},
            'SurroundModeChannelInput': {'Parameters': ['Input'], 'Status': {}},
            'SurroundModeStereoInput': {'Parameters': ['Input'], 'Status': {}},
            'Tuner': {'Status': {}},
            'Volume': {'Status': {}},
            'Zone2AudioMute': {'Status': {}},
            'Zone2Input': {'Status': {}},
            'Zone2Power': {'Status': {}},
            'Zone2Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'P1S([1-9c-e])V([-+]\d{2})M([01])D[0-9]\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'P1D([1-9c-e])([0-9])\n'), self.__MatchDecoderStatus, None)
            self.AddMatchString(re.compile(b'P1P([01])\n'), self.__MatchPower, None)
            self.AddMatchString(re.compile(b'P1MM([1-9c-e])([0-8])\n'), self.__MatchSurroundModeChannelInput, None)
            self.AddMatchString(re.compile(b'P1MS([1-9c-e])([0-9a])\n'), self.__MatchSurroundModeStereoInput, None)
            self.AddMatchString(re.compile(b'P2S([1-9c-e])V([-+]\d{2})M([01])\n'), self.__MatchZone2AudioMute, None)
            self.AddMatchString(re.compile(b'P2P([01])\n'), self.__MatchZone2Power, None)
            self.AddMatchString(re.compile(b'(Parameter Out-of-range|Invalid Command|Main Off|Zone2 Off|Unit Off)\n'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'P1M1\n',
            'Off': 'P1M0\n'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'P1?\n'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        InputStateValues = {
            '1': 'BDP',
            '2': 'CD',
            '3': 'TV',
            '4': 'SAT',
            '5': 'Game',
            '6': 'AUX',
            '7': 'Media',
            '8': 'AM/FM',
            '9': 'iPod',
            'c': 'Current Main Zone Source',
            'd': 'USB',
            'e': 'Internet Radio'
        }

        input_ = InputStateValues[match.group(1).decode()]
        amute = AudioMuteStateValues[match.group(3).decode()]
        vol = int(match.group(2).decode())

        self.WriteStatus('AudioMute', amute, None)
        self.WriteStatus('Volume', vol, None)
        self.WriteStatus('Input', input_, None)

    def UpdateDecoderStatus(self, value, qualifier):

        DecoderStatusCmdString = 'P1D?\n'
        self.__UpdateHelper('DecoderStatus', DecoderStatusCmdString, value, qualifier)

    def __MatchDecoderStatus(self, match, tag):

        InputStates = {
            '1': 'BDP',
            '2': 'CD',
            '3': 'TV',
            '4': 'SAT',
            '5': 'Game',
            '6': 'AUX',
            '7': 'Media',
            '8': 'AM/FM',
            '9': 'iPod',
            'c': 'Current Main Zone Source',
            'd': 'USB',
            'e': 'Internet Radio'
        }

        ValueStateValues = {
            '0': 'No Signal',
            '1': '1-Channel',
            '2': '2-Channel',
            '3': 'Dolby Digital Surround',
            '4': 'Multi Channel PCM',
            '5': 'Dolby Digital',
            '6': 'Dolby Digital Surround EX',
            '7': 'DTS 5.1',
            '8': 'DTS-ES',
            '9': '7.1-Channel'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('DecoderStatus', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'BDP': 'P1S1\n',
            'CD': 'P1S2\n',
            'TV': 'P1S3\n',
            'SAT': 'P1S4\n',
            'Game': 'P1S5\n',
            'AUX': 'P1S6\n',
            'Media': 'P1S7\n',
            'AM/FM': 'P1S8\n',
            'iPod': 'P1S9\n',
            'Current Main Zone Source': 'P1Sc\n',
            'USB': 'P1Sd\n',
            'Internet Radio': 'P1Se\n',
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def SetMultimediaMenu(self, value, qualifier):

        ValueStateValues = {
            'Up': 'P1Gu\n',
            'Down': 'P1Gd\n',
            'Left': 'P1Gl\n',
            'Right': 'P1Gr\n',
            'Select': 'P1GS\n',
            '0': 'P1G0\n',
            '1': 'P1G1\n',
            '2': 'P1G2\n',
            '3': 'P1G3\n',
            '4': 'P1G4\n',
            '5': 'P1G5\n',
            '6': 'P1G6\n',
            '7': 'P1G7\n',
            '8': 'P1G8\n',
            '9': 'P1G9\n',
            'Page Up': 'P1GU\n',
            'Page Down': 'P1GD\n',
            'Menu': 'P1GM\n',
            'Play/Pause': 'P1GP\n',
            'Rewind': 'P1GR\n',
            'Fast Forward': 'P1GF\n',
            'Next': 'P1Gn\n',
            'Previous': 'P1Gp\n',
            'Preset Scan': 'P1Gs\n',
            'Green': 'P1Gg\n',
            'Blue': 'P1Gb\n'
        }

        MultimediaMenuCmdString = ValueStateValues[value]
        self.__SetHelper('MultimediaMenu', MultimediaMenuCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'P1P1\n',
            'Off': 'P1P0\n'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerCmdString = 'P1P?\n'
        self.__UpdateHelper('Power', PowerCmdString, value, qualifier)

    def __MatchPower(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Power', value, None)

    def SetPresetRecall(self, value, qualifier):

        ModeStates = {
            'AM': 'A',
            'FM': 'F'
        }

        mode = qualifier['Mode']
        if mode in ['AM', 'FM'] and 1 <= int(value) <= 30:
            PresetRecallCmdString = 'T{0}P{1:02d}'.format(ModeStates[mode], int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetSetupMenu(self, value, qualifier):

        ValueStateValues = {
            'Up': 'P1Uu\n',
            'Down': 'P1Ud\n',
            'Left': 'P1Ul\n',
            'Right': 'P1Ur\n',
            'Select': 'P1Us\n',
            '0': 'P1U0\n',
            '1': 'P1U1\n',
            '2': 'P1U2\n',
            '3': 'P1U3\n',
            '4': 'P1U4\n',
            '5': 'P1U5\n',
            '6': 'P1U6\n',
            '7': 'P1U7\n',
            '8': 'P1U8\n',
            '9': 'P1U9\n'
        }

        SetupMenuCmdString = ValueStateValues[value]
        self.__SetHelper('SetupMenu', SetupMenuCmdString, value, qualifier)

    def SetSetupMenuCall(self, value, qualifier):

        ValueStateValues = {
            'Open': 'P1Uo\n',
            'Quit': 'P1Uq\n'
        }

        SetupMenuCallCmdString = ValueStateValues[value]
        self.__SetHelper('SetupMenuCall', SetupMenuCallCmdString, value, qualifier)

    def SetSurroundModeChannelInput(self, value, qualifier):

        InputStates = {
            'BDP': '1',
            'CD': '2',
            'TV': '3',
            'SAT': '4',
            'Game': '5',
            'AUX': '6',
            'Media': '7',
            'AM/FM': '8',
            'iPod': '9',
            'USB': 'd',
            'Internet Radio': 'e',
            'Current Main Zone Source': 'c'
        }

        ValueStateValues = {
            'None': '0',
            'PLIIx Movie': '1',
            'PLIIx Music': '2',
            'Dolby Digital EX': '3',
            'Dolby Virtual Speaker Wide': '4',
            'Dolby Virtual Speaker Reference': '5',
            'Neo:6 Cinema': '6',
            'Neo:6 Music': '7',
            'Last Used': '8'
        }

        input_ = qualifier['Input']
        if input_ in InputStates:
            SurroundModeChannelInputCmdString = 'P1MM{0}{1}\n'.format(InputStates[input_], ValueStateValues[value])
            self.__SetHelper('SurroundModeChannelInput', SurroundModeChannelInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurroundModeChannelInput')

    def UpdateSurroundModeChannelInput(self, value, qualifier):

        InputStates = {
            'BDP': '1',
            'CD': '2',
            'TV': '3',
            'SAT': '4',
            'Game': '5',
            'AUX': '6',
            'Media': '7',
            'AM/FM': '8',
            'iPod': '9',
            'Current Main Zone Source': 'c',
            'USB': 'd',
            'Internet Radio': 'e'
        }

        input_ = qualifier['Input']
        if input_ in InputStates:
            SurroundModeChannelInputCmdString = 'P1MM?\n'
            self.__UpdateHelper('SurroundModeChannelInput', SurroundModeChannelInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSurroundModeChannelInput')

    def __MatchSurroundModeChannelInput(self, match, tag):

        InputStates = {
            '1': 'BDP',
            '2': 'CD',
            '3': 'TV',
            '4': 'SAT',
            '5': 'Game',
            '6': 'AUX',
            '7': 'Media',
            '8': 'AM/FM',
            '9': 'iPod',
            'c': 'Current Main Zone Source',
            'd': 'USB',
            'e': 'Internet Radio'
        }

        ValueStateValues = {
            '0': 'None',
            '1': 'PLIIx Movie',
            '2': 'PLIIx Music',
            '3': 'Dolby Digital EX',
            '4': 'Dolby Virtual Speaker Wide',
            '5': 'Dolby Virtual Speaker Reference',
            '6': 'Neo:6 Cinema',
            '7': 'Neo:6 Music',
            '8': 'Last Used'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SurroundModeChannelInput', value, qualifier)

    def SetSurroundModeStereoInput(self, value, qualifier):

        InputStates = {
            'BDP': '1',
            'CD': '2',
            'TV': '3',
            'SAT': '4',
            'Game': '5',
            'AUX': '6',
            'Media': '7',
            'AM/FM': '8',
            'iPod': '9',
            'Current Main Zone Source': 'c',
            'USB': 'd',
            'Internet Radio': 'e'
        }

        ValueStateValues = {
            'Stereo': '0',
            'AnthemLogic Music': '1',
            'AnthemLogic Cinema': '2',
            'PLIIx Movie': '3',
            'PLIIx Music': '4',
            'Neo:6 Cinema': '6',
            'Neo:6 Music': '5',
            'Dolby Virtual Speaker Wide': '7',
            'Dolby Virtual Speaker Reference': '8',
            'All Channel Stereo': '9',
            'Last Used': 'a'
        }

        input_ = qualifier['Input']
        if input_ in InputStates:
            SurroundModeStereoInputCmdString = 'P1MS{0}{1}\n'.format(InputStates[input_], ValueStateValues[value])
            self.__SetHelper('SurroundModeStereoInput', SurroundModeStereoInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSurroundModeStereoInput')

    def UpdateSurroundModeStereoInput(self, value, qualifier):

        InputStates = {
            'BDP': '1',
            'CD': '2',
            'TV': '3',
            'SAT': '4',
            'Game': '5',
            'AUX': '6',
            'Media': '7',
            'AM/FM': '8',
            'iPod': '9',
            'Current Main Zone Source': 'c',
            'USB': 'd',
            'Internet Radio': 'e'
        }

        input_ = qualifier['Input']
        if input_ in InputStates:
            SurroundModeStereoInputCmdString = 'P1MS?\n'
            self.__UpdateHelper('SurroundModeStereoInput', SurroundModeStereoInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateSurroundModeStereoInput')

    def __MatchSurroundModeStereoInput(self, match, tag):

        InputStates = {
            '1': 'BDP',
            '2': 'CD',
            '3': 'TV',
            '4': 'SAT',
            '5': 'Game',
            '6': 'AUX',
            '7': 'Media',
            '8': 'AM/FM',
            '9': 'iPod',
            'c': 'Current Main Zone Source',
            'd': 'USB',
            'e': 'Internet Radio'
        }

        ValueStateValues = {
            '0': 'Stereo',
            '1': 'AnthemLogic Music',
            '2': 'AnthemLogic Cinema',
            '3': 'PLIIx Movie',
            '4': 'PLIIx Music',
            '6': 'Neo:6 Cinema',
            '5': 'Neo:6 Music',
            '7': 'Dolby Virtual Speaker Wide',
            '8': 'Dolby Virtual Speaker Reference',
            '9': 'All Channel Stereo',
            'a': 'Last Used'
        }

        qualifier = {'Input': InputStates[match.group(1).decode()]}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('SurroundModeStereoInput', value, qualifier)

    def SetTuner(self, value, qualifier):

        ValueStateValues = {
            'Up': 'T+\n',
            'Down': 'T-\n'
        }

        TunerCmdString = ValueStateValues[value]
        self.__SetHelper('Tuner', TunerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -90,
            'Max': 26
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = 'P1V{0}\n'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        self.UpdateAudioMute(value, qualifier)

    def SetZone2AudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'P2M1\n',
            'Off': 'P2M0\n'
        }

        Zone2AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def UpdateZone2AudioMute(self, value, qualifier):

        Zone2AudioMuteCmdString = 'P2?\n'
        self.__UpdateHelper('Zone2AudioMute', Zone2AudioMuteCmdString, value, qualifier)

    def __MatchZone2AudioMute(self, match, tag):

        InputStateValues = {
            '1': 'BDP',
            '2': 'CD',
            '3': 'TV',
            '4': 'SAT',
            '5': 'Game',
            '6': 'AUX',
            '7': 'Media',
            '8': 'AM/FM',
            '9': 'iPod',
            'c': 'Current Main Zone Source',
            'd': 'USB',
            'e': 'Internet Radio'
        }

        AudioMuteStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        vol = int(match.group(2).decode())
        amute = AudioMuteStateValues[match.group(3).decode()]
        input_ = InputStateValues[match.group(1).decode()]

        self.WriteStatus('Zone2Volume', vol, None)
        self.WriteStatus('Zone2Input', input_, None)
        self.WriteStatus('Zone2AudioMute', amute, None)

    def SetZone2Input(self, value, qualifier):

        ValueStateValues = {
            'BDP': 'P2S1\n',
            'CD': 'P2S2\n',
            'TV': 'P2S3\n',
            'SAT': 'P2S4\n',
            'Game': 'P2S5\n',
            'AUX': 'P2S6\n',
            'Media': 'P2S7\n',
            'AM/FM': 'P2S8\n',
            'iPod': 'P2S9\n',
            'USB': 'P2Sd\n',
            'Internet Radio': 'P2Se\n',
            'Current Main Zone Source': 'P2Sc\n'
        }

        Zone2InputCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Input', Zone2InputCmdString, value, qualifier)

    def UpdateZone2Input(self, value, qualifier):

        self.UpdateZone2AudioMute(value, qualifier)

    def SetZone2Power(self, value, qualifier):

        ValueStateValues = {
            'On': 'P2P1\n',
            'Off': 'P2P0\n'
        }

        Zone2PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def UpdateZone2Power(self, value, qualifier):

        Zone2PowerCmdString = 'P2P?\n'
        self.__UpdateHelper('Zone2Power', Zone2PowerCmdString, value, qualifier)

    def __MatchZone2Power(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(1).decode()]
        self.WriteStatus('Zone2Power', value, None)

    def SetZone2Volume(self, value, qualifier):

        ValueConstraints = {
            'Min': -90,
            'Max': 26
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            Zone2VolumeCmdString = 'P2V{0}\n'.format(value)
            self.__SetHelper('Zone2Volume', Zone2VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZone2Volume')

    def UpdateZone2Volume(self, value, qualifier):
        self.UpdateZone2AudioMute(value, qualifier)

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
        self.Error(['Error: {0}'.format(match.group(1).decode())])

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            print(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command)
        if method is not None and callable(method):
            method(None, qualifier)
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
        # Handle incoming data
        self.__receiveBuffer += data
        index = 0  # Start of possible good data

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
