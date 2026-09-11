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
            'AUXLevel': {'Parameters': ['Input Channel', 'AUX Channel'], 'Status': {}},
            'AUXMute': {'Parameters': ['Input Channel', 'AUX Channel'], 'Status': {}},
            'FaderLevel': {'Parameters': ['Channel'], 'Status': {}},
            'FaderMute': {'Parameters': ['Channel'], 'Status': {}},
            'Firmware': {'Status': {}},
            'InputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Channel'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Channel'], 'Status': {}},
            'Preset': {'Parameters': ['Scene', 'Action'], 'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(rb'(?:OK|Notify|OKm) (?:set|get) MIXER:Current/InCh/ToMix/Level ([0-9]{1,2}) ([0-9]{1,2}) (-?\d{1,5})[\s\S]*?\n'), self.__MatchAUXLevel, None)
            self.AddMatchString(re.compile(rb'(?:OK|Notify) (?:set|get) MIXER:Current/InCh/ToMix/On ([0-9]{1,2}) ([0-9]{1,2}) (0|1)[\s\S]*?\n'), self.__MatchAUXMute, None)
            self.AddMatchString(re.compile(rb'(?:OK|Notify|OKm) (?:set|get) MIXER:Current/(Mono|St)/Fader/Level (0|1) 0 (-?\d{1,5})[\s\S]*?\n'), self.__MatchFaderLevel, None)
            self.AddMatchString(re.compile(rb'(?:OK|Notify) (?:set|get) MIXER:Current/(Mono|St)/Fader/On (0|1) 0 (0|1)[\s\S]*?\n'), self.__MatchFaderMute, None)
            self.AddMatchString(re.compile(rb'OK devinfo version (V[.\d]+)\n'), self.__MatchFirmware, None)
            self.AddMatchString(re.compile(rb'(?:OK|NOTIFY|OKm) (?:set|get) MIXER:Current/InCh/Fader/Level ([0-9]{1,2}) 0 (-?\d{1,5}).*?\n'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(rb'(?:OK|NOTIFY|OKm) (?:set|get) MIXER:Current/Mix/Fader/Level ([0-9]{1,2}) 0 (-?\d{1,5}).*?\n'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'(?:OK|NOTIFY) (?:set|get) MIXER:Current/InCh/Fader/On ([0-9]{1,2}) 0 ([01]).*?\n'), self.__MatchInputMute, None)
            self.AddMatchString(re.compile(b'(?:OK|NOTIFY) (?:set|get) MIXER:Current/Mix/Fader/On ([0-9]{1,2}) 0 ([01]).*?\n'), self.__MatchOutputMute, None)
            self.AddMatchString(re.compile(b'(ERROR get InvalidArgument|ERROR unknown UnknownCommand)'), self.__MatchError, None)

    def SetAUXLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -138.00,
            'Max': 10.00
        }

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= input_channel <= 40 and 1 <= aux_channel <= 20:
            AUXLevelCmdString = 'set MIXER:Current/InCh/ToMix/Level {0} {1} {2}\n'.format(input_channel - 1, aux_channel - 1, int(value * 100))
            self.__SetHelper('AUXLevel', AUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAUXLevel')

    def UpdateAUXLevel(self, value, qualifier):

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])
        if 1 <= input_channel <= 40 and 1 <= aux_channel <= 20:
            AUXLevelCmdString = 'get MIXER:Current/InCh/ToMix/Level {0} {1}\n'.format(input_channel - 1, aux_channel - 1)
            self.__UpdateHelper('AUXLevel', AUXLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAUXLevel')

    def __MatchAUXLevel(self, match, tag):

        qualifier = {}
        qualifier['Input Channel'] = str(int(match.group(1).decode()) + 1)
        qualifier['AUX Channel'] = str(int(match.group(2).decode()) + 1)
        value = int(match.group(3).decode()) / 100
        if -138 <= value <= 10:
            self.WriteStatus('AUXLevel', value, qualifier)
        else:
            self.Error(['AUX Level: Invalid/unexpected response'])

    def SetAUXMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])
        if 1 <= input_channel <= 40 and 1 <= aux_channel <= 20:
            AUXMuteCmdString = 'set MIXER:Current/InCh/ToMix/On {0} {1} {2}\n'.format(input_channel - 1, aux_channel - 1, ValueStateValues[value])
            self.__SetHelper('AUXMute', AUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAUXMute')

    def UpdateAUXMute(self, value, qualifier):

        input_channel = int(qualifier['Input Channel'])
        aux_channel = int(qualifier['AUX Channel'])
        if 1 <= input_channel <= 40 and 1 <= aux_channel <= 20:
            AUXMuteCmdString = 'get MIXER:Current/InCh/ToMix/On {0} {1}\n'.format(input_channel - 1, aux_channel - 1)
            self.__UpdateHelper('AUXMute', AUXMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAUXMute')

    def __MatchAUXMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {}
        qualifier['Input Channel'] = str(int(match.group(1).decode()) + 1)
        qualifier['AUX Channel'] = str(int(match.group(2).decode()) + 1)
        value = ValueStateValues[match.group(3).decode()]
        self.WriteStatus('AUXMute', value, qualifier)

    def SetFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
        }

        ValueConstraints = {
            'Min': -138.00,
            'Max': 10.00
        }

        channel_val = qualifier['Channel']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and channel_val in ['Mono', 'Stereo L', 'Stereo R']:
            if 'Mono' in channel_val:
                FaderLevelCmdString = 'set MIXER:Current/Mono/Fader/Level 0 0 {0}\n'.format(int(value * 100))
            else:
                FaderLevelCmdString = 'set MIXER:Current/St/Fader/Level {0} 0 {1}\n'.format(
                    ChannelStates[channel_val], int(value * 100))
            self.__SetHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderLevel')

    def UpdateFaderLevel(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
        }

        channel_val = qualifier['Channel']
        if 'Mono' in channel_val:
            FaderLevelCmdString = 'get MIXER:Current/Mono/Fader/Level 0 0\n'
            self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        elif channel_val in ChannelStates:
            FaderLevelCmdString = 'get MIXER:Current/St/Fader/Level {0} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FaderLevel', FaderLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFaderLevel')

    def __MatchFaderLevel(self, match, tag):

        ChannelStates = {
            '0': 'Stereo L',
            '1': 'Stereo R',
        }

        value = int(match.group(3).decode()) / 100
        if -138 <= value <= 10:
            if match.group(1).decode() == 'Mono':
                self.WriteStatus('FaderLevel', value, {'Channel': 'Mono'})
            else:
                self.WriteStatus('FaderLevel', value, {'Channel': ChannelStates[match.group(2).decode()]})
        else:
            self.Error(['Fader Level: Invalid/unexpected response'])

    def SetFaderMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        channel_val = qualifier['Channel']
        if channel_val in ['Mono', 'Stereo L', 'Stereo R']:
            if 'Mono' in channel_val:
                FaderMuteCmdString = 'set MIXER:Current/Mono/Fader/On 0 0 {0}\n'.format(ValueStateValues[value])
            else:
                FaderMuteCmdString = 'set MIXER:Current/St/Fader/On {0} 0 {1}\n'.format(ChannelStates[channel_val], ValueStateValues[value])
            self.__SetHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFaderMute')

    def UpdateFaderMute(self, value, qualifier):

        ChannelStates = {
            'Stereo L': '0',
            'Stereo R': '1',
        }

        channel_val = qualifier['Channel']
        if 'Mono' in channel_val:
            FaderMuteCmdString = 'get MIXER:Current/Mono/Fader/On 0 0\n'
            self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        elif channel_val in ChannelStates:
            FaderMuteCmdString = 'get MIXER:Current/St/Fader/On {0} 0\n'.format(ChannelStates[channel_val])
            self.__UpdateHelper('FaderMute', FaderMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateFaderMute')

    def __MatchFaderMute(self, match, tag):

        ChannelStates = {
            '0': 'Stereo L',
            '1': 'Stereo R',
        }
        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        value = ValueStateValues[match.group(3).decode()]
        if match.group(1).decode() == 'Mono':
            self.WriteStatus('FaderMute', value, {'Channel': 'Mono'})
        else:
            self.WriteStatus('FaderMute', value, {'Channel': ChannelStates[match.group(2).decode()]})

    def UpdateFirmware(self, value, qualifier):

        FirmwareCmdString = 'devinfo version\n'
        self.__UpdateHelper('Firmware', FirmwareCmdString, value, qualifier)

    def __MatchFirmware(self, match, tag):

        self.WriteStatus('Firmware', match.group(1).decode(), None)

    def SetInputLevel(self, value, qualifier):

        if -138.00 <= value <= 10 and 1 <= int(qualifier['Channel']) <= 40:
            InputLevelCmdString = 'set MIXER:Current/InCh/Fader/Level {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, int(value * 100))
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 40:
            InputLevelCmdString = 'get MIXER:Current/InCh/Fader/Level {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2)) / 100
        if -138 <= value <= 10:
            self.WriteStatus('InputLevel', value, qualifier)
        else:
            self.Error(['Input Level: Invalid/unexpected response'])

    def SetInputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Channel']) <= 40:
            InputMuteCmdString = 'set MIXER:Current/InCh/Fader/On {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 40:
            InputMuteCmdString = 'get MIXER:Current/InCh/Fader/On {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def __MatchInputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('InputMute', value, qualifier)

    def SetOutputLevel(self, value, qualifier):

        if -138 <= value <= 10 and 1 <= int(qualifier['Channel']) <= 20:
            OutputLevelCmdString = 'set MIXER:Current/Mix/Fader/Level {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, int(value * 100))
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 20:
            OutputLevelCmdString = 'get MIXER:Current/Mix/Fader/Level {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        qualifier = {'Channel': str(int(match.group(1).decode()) + 1)}
        value = int(match.group(2).decode()) / 100
        self.WriteStatus('OutputLevel', value, qualifier)

    def SetOutputMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        if 1 <= int(qualifier['Channel']) <= 20:
            CmdString = 'set MIXER:Current/Mix/Fader/On {0} 0 {1}\n'.format(int(qualifier['Channel']) - 1, ValueStateValues[value])
            self.__SetHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        if 1 <= int(qualifier['Channel']) <= 20:
            CmdString = 'get MIXER:Current/Mix/Fader/On {0} 0\n'.format(int(qualifier['Channel']) - 1)
            self.__UpdateHelper('OutputMute', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def __MatchOutputMute(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        qualifier = {'Channel': str(int(match.group(1).decode()) + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('OutputMute', value, qualifier)

    def SetPreset(self, value, qualifier):

        if qualifier['Action'] in ['Recall', 'Store'] and qualifier['Scene'] in ['A', 'B'] and 0 <= int(value) <= 99:
            CmdString = 'ss{0}_ex scene_{1} {2}\n'.format(qualifier['Action'].lower(), qualifier['Scene'].lower(), value)
            self.__SetHelper('Preset', CmdString, value, qualifier)

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
        self.Error([match.group(0).decode()])

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
                    except BaseException:
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
                    except BaseException:
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
        except BaseException:
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
            except BaseException:
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
