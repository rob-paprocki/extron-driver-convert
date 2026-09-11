from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack, unpack
from struct import pack
from binascii import unhexlify

class DeviceSerialClass:

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
        self.Models = {
            'pema 4250': self.ashl_25_3722_4,
            'pema 4125': self.ashl_25_3722_4,
            'pema 8125': self.ashl_25_3722_8,
            'pema 8250': self.ashl_25_3722_8,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMuteInput': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMuteOutput': {'Parameters': ['Channel'], 'Status': {}},
            'Heartbeat': {'Status': {}},
            'InputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'MixerFaderLevelControl': {'Parameters': ['Output', 'Input', 'Routing', 'Mute'], 'Status': {}},
            'OutputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'\xF0\x00\x01\\x2A\x0C\x00\x04\x00\x01[\x00-\xFF](?P<inputmute>[\x00-\x7F]{3})[\x00-\xFF](?P<outputmute>[\x00-\x7F]{3})[\x00-\xFF]\xF7'), self.__MatchAudioMuteInput, None)
            self.AddMatchString(re.compile(b'\xF0\x00\x01\\x2A\x0C\x00\x08\x00\x01([\x00-\x07])([\x01-\x3F])\xF7'), self.__MatchInputVolume, None)
            self.AddMatchString(re.compile(b'\xF0\x00\x01\\x2A\x0C\x00\x08\x00\x01([\x40-\x47])([\x01-\x3F])\xF7'), self.__MatchOutputVolume, None)


    def SetAudioMuteInput(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            AudioMuteInputCmdString = b'\xF0\x00\x01\x2A\x06\x00\x15' + pack('>2B', channel - 1, ValueStateValues[value]) + b'\xF7'
            self.__SetHelper('AudioMuteInput', AudioMuteInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteInput')

    def UpdateAudioMuteInput(self, value, qualifier):
        CmdString = b'\xF0\x00\x01\x2A\x0C\x00\x03\x00\x01\xF7'
        self.__UpdateHelper('AudioMuteInput', CmdString, value, qualifier)

    def UpdateAudioMuteOutput(self, value, qualifier):
        CmdString = b'\xF0\x00\x01\x2A\x0C\x00\x03\x00\x01\xF7'
        self.__UpdateHelper('AudioMuteOutput', CmdString, value, qualifier)

    def __MatchAudioMuteInput(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        InputMute_1_7 = '{0:08b}'.format(match.group('inputmute')[0])
        InputMute_8_14 = '{0:08b}'.format(match.group('inputmute')[1])
        OutputMute_1_7 = '{0:08b}'.format(match.group('outputmute')[0])
        OutputMute_8_14 = '{0:08b}'.format(match.group('outputmute')[1])

        self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-1]], {'Channel': '1'})
        self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-2]], {'Channel': '2'})
        self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-3]], {'Channel': '3'})
        self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-4]], {'Channel': '4'})

        self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-1]], {'Channel': '1'})
        self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-2]], {'Channel': '2'})
        self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-3]], {'Channel': '3'})
        self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-4]], {'Channel': '4'})

        if self.InputSize > 4:
            self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-5]], {'Channel': '5'})
            self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-6]], {'Channel': '6'})
            self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_1_7[-7]], {'Channel': '7'})
            self.WriteStatus('AudioMuteInput', ValueStateValues[InputMute_8_14[-1]], {'Channel': '8'})

        if self.OutputSize > 4:
            self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-5]], {'Channel': '5'})
            self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-6]], {'Channel': '6'})
            self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_1_7[-7]], {'Channel': '7'})
            self.WriteStatus('AudioMuteOutput', ValueStateValues[OutputMute_8_14[-1]], {'Channel': '8'})

    def SetAudioMuteOutput(self, value, qualifier):

        ValueStateValues = {
            'On': 1,
            'Off': 0
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.OutputSize:
            AudioMuteOutputCmdString = b'\xF0\x00\x01\x2A\x06\x00\x15' + pack('>2B', channel + 63, ValueStateValues[value]) + b'\xF7'
            self.__SetHelper('AudioMuteOutput', AudioMuteOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteOutput')

    def SetInputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if -50 <= value <= 12 and 1 <= channel <= self.InputSize:
            if value == -50:
                vol_first_byte = 0x3C  # First byte
                vol_second_byte = 0x0C  # Second byte
            else:
                vol_gain_word = (value * 10) + 8192  # Convert dB value to equivalent int value
                vol_first_byte = int(vol_gain_word) >> 7  # First byte
                vol_second_byte = int(vol_gain_word) & 127  # Second byte

            InputVolumeCmdString = b'\xF0\x00\x01\x2A\x06\x00\x0C' + pack('>3B', channel - 1, vol_first_byte, vol_second_byte) + b'\xF7'
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            InputVolumeCmdString = b'\xF0\x00\x01\x2A\x0C\x00\x07\x00\x01' + pack('>B', channel - 1) + b'\xF7'
            self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputVolume')

    def __MatchInputVolume(self, match, tag):

        qualifier = {'Channel': str(match.group(1)[0] + 1)}
        value = match.group(2)[0] - 51
        self.WriteStatus('InputVolume', value, qualifier)

    def SetMixerFaderLevelControl(self, value, qualifier):

        RoutingStates = {
            'Enable': 1,
            'Disable': 0
        }

        MuteStates = {
            'On': 1,
            'Off': 0
        }

        inputValue = int(qualifier['Input'])
        outputValue = int(qualifier['Output'])

        if -50 <= value <= 12 and 1 <= inputValue <= self.InputSize and 1 <= outputValue <= self.OutputSize and qualifier['Routing'] in RoutingStates and qualifier['Mute'] in MuteStates:
            routing = RoutingStates[qualifier['Routing']]
            muting = MuteStates[qualifier['Mute']]
            MixerFaderLevelControlCmdString = b'\xF0\x00\x01\x2A\x06\x00\x12' + pack('>5B', outputValue + 63, inputValue - 1, value + 51, routing, muting) + b'\xF7'
            self.__SetHelper('MixerFaderLevelControl', MixerFaderLevelControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerFaderLevelControl')

    def SetOutputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if -50 <= value <= 12 and 1 <= channel <= self.OutputSize:
            if value == -50:
                vol_first_byte = 0x3C  # First byte
                vol_second_byte = 0x0C  # Second byte
            else:
                vol_gain_word = (value * 10) + 8192  # Convert dB value to equivalent int value
                vol_first_byte = int(vol_gain_word) >> 7  # First byte
                vol_second_byte = int(vol_gain_word) & 127  # Second byte

            OutputVolumeCmdString = b'\xF0\x00\x01\x2A\x06\x00\x0C' + pack('>3B', channel + 63, vol_first_byte, vol_second_byte) + b'\xF7'
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.OutputSize:
            OutputVolumeCmdString = b'\xF0\x00\x01\x2A\x0C\x00\x07\x00\x01' + pack('>B', channel + 63) + b'\xF7'
            self.__UpdateHelper('InputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputVolume')

    def __MatchOutputVolume(self, match, tag):

        qualifier = {'Channel': str(match.group(1)[0] - 63)}
        value = match.group(2)[0] - 51
        self.WriteStatus('OutputVolume', value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 31:
            PresetRecallCmdString = b'\xF0\x00\x01\x2A\x06\x00\x07' + pack('>B', int(value) - 1) + b'\x00\xF7'
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

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

    def ashl_25_3722_4(self):
        self.InputSize = 8
        self.OutputSize = 4

    def ashl_25_3722_8(self):

        self.InputSize = 8
        self.OutputSize = 8

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


class DeviceEthernetClass:

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
        self._MACAddress = b''
        self._deviceUsername = b'admin'
        self._devicePassword = b''
        self.Models = {
            'pema 4250': self.ashl_25_3722_4,
            'pema 4125': self.ashl_25_3722_4,
            'pema 8125': self.ashl_25_3722_8,
            'pema 8250': self.ashl_25_3722_8,
            }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMuteInput': {'Parameters': ['Channel'], 'Status': {}},
            'AudioMuteOutput': {'Parameters': ['Channel'], 'Status': {}},
            'InputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'MixerMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputVolume': {'Parameters': ['Channel'], 'Status': {}},
            'PowerStatus': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }

        self.SetHeader = b'\xAA\xAA\xAA\xAA'
        self.UpdateHeader = b'\x8F\x8F\x8F\x8F'

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x02\x03\x01([\x00-\x07])([\x00-\x01])\xFF'), self.__MatchAudioMuteInput, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x02\x03\x00([\x00-\x07])([\x00-\x01])\xFF'), self.__MatchAudioMuteOutput, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x81\x06\x01([\x00-\x07])\x17([\x00-\xFF])([\x00-\xFF])[\x00-\x01]\xFF'), self.__MatchInputVolume, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x81\x06\x00([\x00-\x07])\x17([\x00-\xFF])([\x00-\xFF])[\x00-\x01]\xFF'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'[\x8F]{4}[\x00-\xFF]{6}\x01[\x00-\xFF][\x00]{2}\x06\x01([\x00-\x01])\xFF'), self.__MatchPowerStatus, None)

    @property
    def MACAddress(self):
        return self._MACAddress

    @MACAddress.setter
    def MACAddress(self, value):
        self._MACAddress = b''
        res = re.search('([a-fA-F0-9]{2}-?){6}', value)
        temp_list = res.group().split('-')
        for mc in temp_list:
            self._MACAddress += unhexlify(mc)

    @property
    def deviceUsername(self):
        return self._deviceUsername

    @deviceUsername.setter
    def deviceUsername(self, value):
        self._deviceUsername = b''
        for user in value.ljust(8, '\x00'):
            self._deviceUsername += pack('B', ord(user))

    @property
    def devicePassword(self):
        return self._devicePassword

    @devicePassword.setter
    def devicePassword(self, value):
        self._devicePassword = b''
        for pw in value.ljust(8, '\x00'):
            self._devicePassword += pack('B', ord(pw))

    def SetAudioMuteInput(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            AudioMuteInputCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>6B', 0x02, 0x03, 0x01, channel - 1, ValueStateValues[value], 0xFF)
            self.__SetHelper('AudioMuteInput', AudioMuteInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteInput')

    def UpdateAudioMuteInput(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            AudioMuteInputCmdString = self.UpdateHeader + self._MACAddress + b'\x00\x00\x00\x00' + pack('>5B', 0x02, 0x02, 0x01, channel - 1, 0xFF)
            self.__UpdateHelper('AudioMuteInput', AudioMuteInputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMuteInput')

    def __MatchAudioMuteInput(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {'Channel': str(match.group(1)[0] + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMuteInput', value, qualifier)

    def SetAudioMuteOutput(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.OutputSize:
            AudioMuteOutputCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>6B', 0x02, 0x03, 0x00, channel - 1, ValueStateValues[value], 0xFF)
            self.__SetHelper('AudioMuteOutput', AudioMuteOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMuteOutput')

    def UpdateAudioMuteOutput(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.OutputSize:
            AudioMuteOutputCmdString = self.UpdateHeader + self._MACAddress + b'\x00\x00\x00\x00' + pack('>5B', 0x02, 0x02, 0x00, channel - 1, 0xFF)
            self.__UpdateHelper('AudioMuteOutput', AudioMuteOutputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioMuteOutput')

    def __MatchAudioMuteOutput(self, match, tag):

        ValueStateValues = {
            '\x01': 'On',
            '\x00': 'Off'
        }

        qualifier = {'Channel': str(match.group(1)[0] + 1)}
        value = ValueStateValues[match.group(2).decode()]
        self.WriteStatus('AudioMuteOutput', value, qualifier)

    def SetInputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if -50 <= value <= 12 and 1 <= channel <= self.InputSize:
            vol_gain_word = (value * 10) + 8192  # Convert dB value to equivalent int value
            vol_first_byte = round(vol_gain_word / 256)  # First 16 bit
            vol_second_byte = vol_gain_word & 127  # Second 16 bit
            InputVolumeCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>9B', 0x81, 0x06, 0x01, channel - 1, 0x17, vol_first_byte, vol_second_byte, 0x00, 0xFF)
            self.__SetHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputVolume')

    def UpdateInputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.InputSize:
            InputVolumeCmdString = self.UpdateHeader + self._MACAddress + b'\x00\x00\x00\x00' + pack('>6B', 0x81, 0x03, 0x01, channel - 1, 0x17, 0xFF)
            self.__UpdateHelper('InputVolume', InputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateInputVolume')

    def __MatchInputVolume(self, match, tag):

        qualifier = {'Channel': str(match.group(1)[0] + 1)}
        temp_val1 = match.group(2)[0]  # MSB byte
        temp_val2 = match.group(3)[0]  # LSB byte
        value = int((((temp_val1 * 256) + temp_val2) - 8192) / 10)
        self.WriteStatus('InputVolume', value, qualifier)

    def SetMixerMute(self, value, qualifier):

        inputValue = int(qualifier['Input'])
        outputValue = int(qualifier['Output'])
        if value in ['On', 'Off'] and 1 <= inputValue <= self.InputSize and 1 <= outputValue <= self.OutputSize:
            # byteValue is the binary position of the channel to be muted / unmuted
            binaryValues = {
                1: 1,
                2: 2,
                3: 4,
                4: 8,
                5: 16,
                6: 32,
                7: 64,
                8: 128
            }

            if value == 'On':
                unmuteBytes = 0
                muteBytes = binaryValues[inputValue]
            else:
                muteBytes = 0
                unmuteBytes = binaryValues[inputValue]
            MixerMuteCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00\x81\x0B\x00' + \
                                 pack('B', outputValue - 1) + pack('>10B', 0x74, 0x00, 0x00, 0x00, muteBytes, 0x00, 0x00, 0x00, unmuteBytes, 0xFF)
            self.__SetHelper('MixerMute', MixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMixerMute')

    def SetOutputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if -50 <= value <= 12 and 1 <= channel <= self.OutputSize:
            vol_gain_word = (value * 10) + 8192  # Convert dB value to equivalent int value
            vol_first_byte = round(vol_gain_word / 256)  # First 16 bit
            vol_second_byte = vol_gain_word & 127  # Second 16 bit
            OutputVolumeCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>9B', 0x81, 0x06, 0x00, channel - 1, 0x17, vol_first_byte, vol_second_byte, 0x00, 0xFF)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 1 <= channel <= self.OutputSize:
            OutputVolumeCmdString = self.UpdateHeader + self._MACAddress + b'\x00\x00\x00\x00' + pack('>6B', 0x81, 0x03, 0x00, channel - 1, 0x17, 0xFF)
            self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateOutputVolume')

    def __MatchOutputVolume(self, match, tag):

        qualifier = {'Channel': str(match.group(1)[0] + 1)}
        temp_val1 = match.group(2)[0]  # MSB byte
        temp_val2 = match.group(3)[0]  # LSB byte
        value = int((((temp_val1 * 256) + temp_val2) - 8192) / 10)
        self.WriteStatus('OutputVolume', value, qualifier)

    def UpdatePowerStatus(self, value, qualifier):

        PowerStatusCmdString = self.UpdateHeader + self._MACAddress + b'\x00\x00\x00\x00' + pack('>3B', 0x06, 0x00, 0xFF)
        self.__UpdateHelper('PowerStatus', PowerStatusCmdString, value, qualifier)

    def __MatchPowerStatus(self, match, tag):

        ValueStateValues = {
            0: 'On',
            1: 'Standby'
        }

        value = ValueStateValues[match.group(1)[0]]
        self.WriteStatus('PowerStatus', value, None)

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 31:
            PresetRecallCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>5B', 0x32, 0x02, int(value) - 1, 0x00, 0xFF)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 31:
            PresetSaveCmdString = self.SetHeader + self._MACAddress + self._deviceUsername + self._devicePassword + b'\x00\x00\x00\x00' + pack('>5B', 0x31, 0x02, int(value) - 1, 0x00, 0xFF)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

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

    def ashl_25_3722_4(self):
        self.InputSize = 8
        self.OutputSize = 4

    def ashl_25_3722_8(self):

        self.InputSize = 8
        self.OutputSize = 8

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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            self.__matchStringDict[regex_string] = {'callback': callback, 'para':arg}

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

class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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

class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self) 
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

class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self) 
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
