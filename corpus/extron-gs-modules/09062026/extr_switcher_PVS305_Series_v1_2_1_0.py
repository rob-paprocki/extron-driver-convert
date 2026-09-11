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
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'PassThroughMode': {'Status': {}},
            'StandbyPowerSaveMode': {'Status': {}},
            'VoiceLiftAuxInput': {'Status': {}},
            'OutputVolume': {'Status': {}},
        }


        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'In(\d) Aud=\+?(-?[0-9]{1,2})\r\n'), self.__MatchAudioGainAttenuation, None)
            self.AddMatchString(re.compile(b'Amt([0-3])\r\n'), self.__MatchAudioMute, None)
            self.AddMatchString(re.compile(b'Exe([01])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'Aud([0-5])\r\n'), self.__MatchAudioInput, None)
            self.AddMatchString(re.compile(b'Vid([0-5])\r\n'), self.__MatchVideoInput, None)
            self.AddMatchString(re.compile(b'Chn([0-5])\r\n'), self.__MatchAudioVideoInput, None)
            self.AddMatchString(re.compile(b'Vid([0-5]) Aud([0-5]) Vol\d+\r\n'), self.__MatchInput, None)
            self.AddMatchString(re.compile(b'Frq=([01])\*([01])\*([01])\*([01])\r\n'), self.__MatchInputSignalStatus, None)
            self.AddMatchString(re.compile(b'Cpn([01])\r\n'), self.__MatchPassThroughMode, None)
            self.AddMatchString(re.compile(b'Psav\*([0-3])\r\n'), self.__MatchStandbyPowerSaveMode, None)
            self.AddMatchString(re.compile(b'Mix([01])\r\n'), self.__MatchVoiceLiftAuxInput, None)
            self.AddMatchString(re.compile(b'Vol([0-9]{3})\r\n'), self.__MatchOutputVolume, None)
            self.AddMatchString(re.compile(b'E(01|06|10|13|14)\r\n'), self.__MatchError, None)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Overall Mute On': '1Z',
            'Overall Mute Off': '0Z',
            'Input Muted-Voicelift Input Unmuted': '3Z',
            'VoiceLift Input Muted-Input Unmuted': '2Z',
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        AudioMuteCmdString = 'Z'
        self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def __MatchAudioMute(self, match, tag):

        AudioMuteState = {
            '1': 'Overall Mute On',
            '0': 'Overall Mute Off',
            '3': 'Input Muted-Voicelift Input Unmuted',
            '2': 'VoiceLift Input Muted-Input Unmuted'
        }

        value = AudioMuteState[match.group(1).decode()]
        self.WriteStatus('AudioMute', value, None)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'On': '1X',
            'Off': '0X',
        }

        ExecutiveModeCmdString = ExecutiveModeState[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeCmdString = 'X'
        self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeState = {
            '1': 'On',
            '0': 'Off',
        }

        value = ExecutiveModeState[match.group(1).decode()]
        self.WriteStatus('ExecutiveMode', value, None)

    def SetInput(self, value, qualifier):

        TieTypeState = {
            'Video': '&',
            'Audio': '$',
            'Audio/Video': '!'
        }

        inputType = qualifier['Type']
        if 0 <= int(value) <= 5 and inputType in TieTypeState:
            InputCmdString = '{0}{1}'.format(value, TieTypeState[inputType])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'i'
        self.__UpdateHelper('Input', InputCmdString, value, qualifier)

    def __MatchInput(self, match, qualifier):

        VideoInput = match.group(1).decode()
        AudioInput = match.group(2).decode()

        if AudioInput == VideoInput:
            AVInput = VideoInput
        else:
            AVInput = '0'

        self.WriteStatus('Input', VideoInput, {'Type': 'Video'})
        self.WriteStatus('Input', AudioInput, {'Type': 'Audio'})
        self.WriteStatus('Input', AVInput, {'Type': 'Audio/Video'})

    def __MatchVideoInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Video'})
        self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

    def __MatchAudioInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Audio'})
        self.WriteStatus('Input', '0', {'Type': 'Audio/Video'})

    def __MatchAudioVideoInput(self, match, qualifier):

        value = match.group(1).decode()
        self.WriteStatus('Input', value, {'Type': 'Audio/Video'})
        self.WriteStatus('Input', value, {'Type': 'Video'})
        self.WriteStatus('Input', value, {'Type': 'Audio'})

    def SetAudioGainAttenuation(self, value, qualifier):

        channel = int(qualifier['Input'])
        if -18 <= value <= 24 and 1 <= channel <= 7:
            if value >= 0:
                AudioGainAttenuationCmdString = '{0}*{1}G'.format(channel, value)
            elif value < 0:
                AudioGainAttenuationCmdString = '{0}*{1}g'.format(channel, value)
            else:
                self.Discard('Invalid Command for SetAudioGainAttenuation')
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        channel = int(qualifier['Input'])
        if 1 <= channel <= 7:
            AudioGainAttenuationCmdString = '{0}*G'.format(channel)
            self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def __MatchAudioGainAttenuation(self, match, tag):

        value = int(match.group(2).decode())
        self.WriteStatus('AudioGainAttenuation', value, {'Input': match.group(1).decode()})

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusCmdString = 'LS'
        self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusState = {
            '1': 'Active',
            '0': 'Not Active',
        }

        value1 = InputSignalStatusState[match.group(1).decode()]
        value2 = InputSignalStatusState[match.group(2).decode()]
        value3 = InputSignalStatusState[match.group(3).decode()]
        value4 = InputSignalStatusState[match.group(4).decode()]

        self.WriteStatus('InputSignalStatus', value1, {'Input': '1'})
        self.WriteStatus('InputSignalStatus', value2, {'Input': '2'})
        self.WriteStatus('InputSignalStatus', value3, {'Input': '3'})
        self.WriteStatus('InputSignalStatus', value4, {'Input': '4'})

    def SetPassThroughMode(self, value, qualifier):

        PassThroughModeState = {
            'Configure Pass-through Mode': '\x1B1CD\r',
            'Terminate Pass-through Mode': '\x1B0CD\r',
        }

        PassThroughModeCmdString = PassThroughModeState[value]
        self.__SetHelper('PassThroughMode', PassThroughModeCmdString, value, qualifier)

    def UpdatePassThroughMode(self, value, qualifier):

        PassThroughModeCmdString = '\x1BCD\r'
        self.__UpdateHelper('PassThroughMode', PassThroughModeCmdString, value, qualifier)

    def __MatchPassThroughMode(self, match, tag):

        PassThroughModeState = {
            '1': 'Configure Pass-through Mode',
            '0': 'Terminate Pass-through Mode',
        }

        value = PassThroughModeState[match.group(1).decode()]
        self.WriteStatus('PassThroughMode', value, None)

    def SetStandbyPowerSaveMode(self, value, qualifier):

        StandbyPowerSaveModeState = {
            'Disable Power Save': '\x1B0PSAV\r',
            'Start Auto Power Save Timer': '\x1B1PSAV\r',
            'Force Auto Power Save': '\x1B2PSAV\r',
            'Force Standby Power Mode On': '\x1B3PSAV\r',
        }

        StandbyPowerCmdString = StandbyPowerSaveModeState[value]
        self.__SetHelper('StandbyPowerSaveMode', StandbyPowerCmdString, value, qualifier)

    def UpdateStandbyPowerSaveMode(self, value, qualifier):

        StandbyPowerSaveModeCmdString = '\x1BPSAV\r'
        self.__UpdateHelper('StandbyPowerSaveMode', StandbyPowerSaveModeCmdString, value, qualifier)

    def __MatchStandbyPowerSaveMode(self, match, tag):

        StandbyPowerSaveModeState = {
            '0': 'Disable Power Save',
            '1': 'Start Auto Power Save Timer',
            '2': 'Force Auto Power Save',
            '3': 'Force Standby Power Mode On',
        }

        value = StandbyPowerSaveModeState[match.group(1).decode()]
        self.WriteStatus('StandbyPowerSaveMode', value, None)

    def SetVoiceLiftAuxInput(self, value, qualifier):

        VoiceLiftAuxInputState = {
            'On': '1M',
            'Off': '0M',
        }

        VoiceLiftAuxInputCmdString = VoiceLiftAuxInputState[value]
        self.__SetHelper('VoiceLiftAuxInput', VoiceLiftAuxInputCmdString, value, qualifier)

    def UpdateVoiceLiftAuxInput(self, value, qualifier):

        VoiceLiftAuxInputCmdString = 'M'
        self.__UpdateHelper('VoiceLiftAuxInput', VoiceLiftAuxInputCmdString, value, qualifier)

    def __MatchVoiceLiftAuxInput(self, match, tag):

        VoiceLiftAuxInputState = {
            '1': 'On',
            '0': 'Off'
        }

        value = VoiceLiftAuxInputState[match.group(1).decode()]
        self.WriteStatus('VoiceLiftAuxInput', value, None)

    def SetOutputVolume(self, value, qualifier):

        if 0 <= value <= 100:
            OutputVolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputVolume')

    def UpdateOutputVolume(self, value, qualifier):

        OutputVolumeCmdString = 'V'
        self.__UpdateHelper('OutputVolume', OutputVolumeCmdString, value, qualifier)

    def __MatchOutputVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('OutputVolume', value, None)

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

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (too large)',
            '06': 'Invalid channel change',
            '10': 'Invalid command',
            '13': 'Invalid value (too large)',
            '14': 'Invalid command for this configuration',
        }

        value = match.group(1).decode()
        if value in DEVICE_ERROR_CODES:
            self.Error([DEVICE_ERROR_CODES[value]])
        else:
            self.Error(['Unrecognize error code: ' + match.group(0).decode()])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.lastSignalStatusUpdate = 0

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
