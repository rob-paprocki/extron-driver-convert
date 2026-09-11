from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
            'AudioMute': {'Parameters': ['Channel'], 'Status': {}},
            'Bass': {'Parameters': ['Channel'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'Group': {'Parameters': ['Channel'], 'Status': {}},
            'InputGain': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Channel'], 'Status': {}},
            'PresetSave': {'Parameters': ['Channel'], 'Status': {}},
            'Treble': {'Parameters': ['Channel'], 'Status': {}},
            'Volume': {'Parameters': ['Channel'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Amt(1|2|3|4| All)\*(0|1)\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Chn(1|2|3|4) Bas([0-9]{1,2})\r\n'), self.__MatchBass, None)
            self.AddMatchString(re.compile(b'Exe(0|1|2)\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Tie Grp(A|B)\*(0|1)\r\n'), self.__MatchGroup, None)
            self.AddMatchString(re.compile(b'Chn(1|2|3|4) Gain\+?(\-?[0-9]{1,2})\r\n'), self.__MatchInputGain, None)
            self.AddMatchString(re.compile(b'Chn(1|2|3|4) Trb([0-9]{1,2})\r\n'), self.__MatchTreble, None)
            self.AddMatchString(re.compile(b'Vol(1|2|3|4)\*([\d]+)\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'Chn(1|2|3|4) Vol([\d]+)\r\n'), self.__MatchVolume, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': '1',
            'Off': '0'
        }

        channel = qualifier['Channel']
        if 1 <= int(channel) <= 4:
            AudioMuteCmdString = '{0}*{1}Z'.format(channel, AudioMuteState[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteState = {
            '0': 'Off',
            '1': 'On'
        }

        channel = qualifier['Channel']
        CommandString = '{0}Z'.format(channel)
        res = self.__UpdateHelper('AudioMute', CommandString, value, qualifier)
        if res:
            try:
                value = AudioMuteState[res[0:-2]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, ValueError):
                self.Error(['Audio Mute : Invalid/Unexpected Response'])

    def __MatchAudioMute(self, match, qualifier):

        AudioMuteState = {
            '0': 'Off',
            '1': 'On'
        }

        channelnum = match.group(1).decode()
        value = AudioMuteState[match.group(2).decode()]
        if channelnum == ' All':
            self.WriteStatus('AudioMute', value, {'Channel': '1'})
            self.WriteStatus('AudioMute', value, {'Channel': '2'})
            self.WriteStatus('AudioMute', value, {'Channel': '3'})
            self.WriteStatus('AudioMute', value, {'Channel': '4'})
        else:
            self.WriteStatus('AudioMute', value, {'Channel': match.group(1).decode()})

    def SetBass(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(channel) <= 4:
            BassCmdString = '{0}*{1}>'.format(channel, int(value / 2 + 7))
            self.__SetHelper('Bass', BassCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBass')

    def UpdateBass(self, value, qualifier):

        channel = qualifier['Channel']
        BassCmdString = '{0}>'.format(channel)
        res = self.__UpdateHelper('Bass', BassCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-2])
                value = (value - 7) * 2
                self.WriteStatus('Bass', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Bass: Invalid/Unexpected Response'])

    def __MatchBass(self, match, qualifier):

        value = int(match.group(2).decode())
        value = (value - 7) * 2
        self.WriteStatus('Bass', value, {'Channel': match.group(1).decode()})

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2'
        }

        ExecutiveModeStateCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeStateCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        ExecutiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeState[res[0:-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode : Invalid/Unexpected Response'])

    def __MatchExecutiveMode(self, match, qualifier):

        ExecutiveModeState = {
            '0': 'Off',
            '1': 'Mode 1',
            '2': 'Mode 2'
        }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetGlobalAudioMute(self, value, qualifier):

        GlobalAudioMuteState = {
            'On': '1',
            'Off': '0'
        }

        GlobalAudioMuteCmdString = '{0}*Z'.format(GlobalAudioMuteState[value])
        self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)

    def SetInputGain(self, value, qualifier):

        ValueConstraints = {
            'Min': -12,
            'Max': 12
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(channel) <= 4:
            if value >= 0:
                InputGainCmdString = '{0}*{1}G'.format(channel, value)
            elif value < 0:
                InputGainCmdString = '{0}*{1}g'.format(channel, abs(value))
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        channel = qualifier['Channel']
        InputGainCmdString = 'V{0}G'.format(channel)
        res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
        if res:
            try:
                if res[0] == '-':
                    value = int(res[0:-2])
                else:
                    value = int(res[1:-2])
                self.WriteStatus('InputGain', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Input Gain: Invalid/Unexpected Response'])

    def __MatchInputGain(self, match, qualifier):

        value = int(match.group(2).decode())
        self.WriteStatus('InputGain', value, {'Channel': match.group(1).decode()})

    def SetPresetRecall(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(value) <= 3 and 1 <= int(channel) <= 4:
            PresetRecallCmdString = '{0}*{1}.'.format(channel, value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        channel = qualifier['Channel']
        if 1 <= int(value) <= 3 and 1 <= int(channel) <= 4:
            PresetSaveCmdString = '{0}*{1},'.format(channel, value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetGroup(self, value, qualifier):

        TieState = {
            'On': 1,
            'Off': 0
        }

        Group = {
            '1 and 2': 'A',
            '3 and 4': 'B'
        }

        group = Group[qualifier['Channel']]
        CommandString = '{0}*{1}*4#'.format(group, TieState[value])
        self.__SetHelper('Group', CommandString, value, qualifier)

    def UpdateGroup(self, value, qualifier):

        TieState = {
            '0': 'Off',
            '1': 'On'
        }

        CommandString = '4#'
        res = self.__UpdateHelper('Group', CommandString, value, qualifier)
        if res:
            try:
                ResSplit = res.split(' ')
                GroupATieStatus = TieState[ResSplit[0][-1]]
                GroupBTieStatus = TieState[ResSplit[1][-3]]
                self.WriteStatus('Group', GroupATieStatus, {'Channel': '1 and 2'})
                self.WriteStatus('Group', GroupBTieStatus, {'Channel': '3 and 4'})
            except (KeyError, IndexError):
                self.Error(['Group : Invalid/Unexpected Response'])

    def __MatchGroup(self, match, qualifier):

        TieState = {
            '0': 'Off',
            '1': 'On'
        }

        GroupState = {
            'A': '1 and 2',
            'B': '3 and 4'
        }

        value = TieState[match.group(2).decode()]
        self.WriteStatus('Group', value, {'Channel': GroupState[match.group(1).decode()]})

    def SetTreble(self, value, qualifier):

        ValueConstraints = {
            'Min': -14,
            'Max': 14
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(channel) <= 4:
            TrebleCmdString = '{0}*{1}<'.format(channel, int(value / 2 + 7))
            self.__SetHelper('Treble', TrebleCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTreble')

    def UpdateTreble(self, value, qualifier):

        channel = qualifier['Channel']
        TrebleCmdString = '{0}<'.format(channel)
        res = self.__UpdateHelper('Treble', TrebleCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-2])
                value = (value - 7) * 2
                self.WriteStatus('Treble', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Treble : Invalid/Unexpected Response'])

    def __MatchTreble(self, match, qualifier):

        value = int(match.group(2).decode())
        value = (value - 7) * 2
        self.WriteStatus('Treble', value, {'Channel': match.group(1).decode()})

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        channel = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = '{0}*{1}V'.format(channel, value + 100)
            self.__SetHelper('Volume', VolumeCmdString, value + 100, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        channel = qualifier['Channel']
        VolumeCmdString = '{0}V'.format(channel)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-2])
                value = value - 100
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume : Invalid/Unexpected Response'])

    def __MatchVolume(self, match, qualifier):

        value = int(match.group(2).decode())
        value = value - 100
        self.WriteStatus('Volume', value, {'Channel': match.group(1).decode()})

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': "Invalid channel number (too large)",
            'E10': "Invalid command",
            'E13': "Invalid setting at this time",
            'E23': "Firmware update failure"
        }

        if response:
            if response[0:3] in DEVICE_ERROR_CODES:
                ErrorString = sourceCmdName + ' ' + DEVICE_ERROR_CODES[response[0:3]]
                self.Error([ErrorString])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r\n')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res.decode())

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
