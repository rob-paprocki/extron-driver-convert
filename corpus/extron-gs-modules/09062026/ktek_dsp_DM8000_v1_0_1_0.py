from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, findall, search

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
            'InputGain': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'InputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'InputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'MixerInputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'MixerInputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'OutputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'PhantomPower': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'StandardMixerOutputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'StandardMixerOutputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'USBInputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'USBInputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'USBOutputLevel': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'USBOutputMute': {'Parameters': ['Instance Tag', 'Channel'], 'Status': {}},
            'VerboseMode': {'Status': {}}
        }
        self.findDigit = compile('OK \"value\":(-*\d+)\.*\d*')

        if self.Unidirectional == 'False':
            self.UpdateRegex = compile(b'(\+OK|-ERR).+\r\n')

    def SetVerbose(self, value, qualifier):
        self.Send('SESSION set verbose true\r')

    def UpdateVerboseMode(self, value, qualifier):

        res = self.__UpdateHelper('VerboseMode', 'SESSION get verbose\r', value, qualifier)
        if res:
            if 'false' in res:
                self.SetVerbose(None, None)
                self.WriteStatus('VerboseMode', 'Off', None)
            elif 'true' in res:
                self.WriteStatus('VerboseMode', 'On', None)
        else:
            print('Invalid/unexpected response for VerboseMode')

    def SetInputGain(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        InputGainState = {
            '0': '0',
            '6': '6',
            '12': '12',
            '18': '18',
            '24': '24',
            '30': '30',
            '36': '36',
            '42': '42',
            '48': '48',
            '54': '54',
            '60': '60',
            '66': '66'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            InputGainCmdString = '{0} set gain {1} {2}\n'.format(tag, channel, InputGainState[value])
            self.__SetHelper('InputGain', InputGainCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputGain')

    def UpdateInputGain(self, value, qualifier):

        InputGainState = {
            '0': '0',
            '6': '6',
            '12': '12',
            '18': '18',
            '24': '24',
            '30': '30',
            '36': '36',
            '42': '42',
            '48': '48',
            '54': '54',
            '60': '60',
            '66': '66'
        }

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            InputGainCmdString = '{0} get gain {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('InputGain', InputGainCmdString, value, qualifier)
            if res:
                result = findall('OK \"value\":(\d+)\.*\d*', res)
                if result:
                    value = InputGainState[result[0]]
                    self.WriteStatus('InputGain', value, qualifier)
                else:
                    print('Input Gain: Invalid/Unexpected Response for InputGain')
        else:
            print('Invalid Command for UpdateInputGain')

    def SetInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            InputLevelCmdString = '{0} set inputlevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            InputLevelCmdString = '{0} get inputlevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('InputLevel', value, qualifier)
                else:
                    print('Input Level: Invalid/Unexpected Response for InputLevel')
        else:
            print('Invalid Command for UpdateInputLevel')

    def SetInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        InputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            InputMuteCmdString = '{0} set inputMute {1} {2}\n'.format(tag, channel, InputMuteState[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            InputMuteCmdString = '{0} get inputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('InputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('InputMute', 'Off', qualifier)
                else:
                    print('Input Mute: Invalid/Unexpected Response for InputMute')
        else:
            print('Invalid Command for UpdateInputMute')

    def SetMixerInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 32 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MixerInputLevelCmdString = '{0} set inputLevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('MixerInputLevel', MixerInputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMixerInputLevel')

    def UpdateMixerInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 32:
            MixerInputLevelCmdString = '{0} get inputLevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('MixerInputLevel', MixerInputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('MixerInputLevel', value, qualifier)
                else:
                    print('Mixer Input Level: Invalid/Unexpected Response for MixerInputLevel')
        else:
            print('Invalid Command for UpdateMixerInputLevel')

    def SetMixerInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        MixerInputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 32:
            MixerInputMuteCmdString = '{0} set inputMute {1} {2}\n'.format(tag, channel, MixerInputMuteState[value])
            self.__SetHelper('MixerInputMute', MixerInputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMixerInputMute')

    def UpdateMixerInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 32:
            MixerInputMuteCmdString = '{0} get inputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('MixerInputMute', MixerInputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('MixerInputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('MixerInputMute', 'Off', qualifier)
                else:
                    print('Mixer Input Mute: Invalid/Unexpected Response for MixerInputMute')
        else:
            print('Invalid Command for UpdateMixerInputMute')

    def SetOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 6 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            OutputLevelCmdString = '{0} set outputLevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 6:
            OutputLevelCmdString = '{0} get outputLevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('OutputLevel', value, qualifier)
                else:
                    print('Output Level: Invalid/Unexpected Response for OutputLevel')
        else:
            print('Invalid Command for UpdateOutputLevel')

    def SetOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        OutputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 6:
            OutputMuteCmdString = '{0} set outputMute {1} {2}\n'.format(tag, channel, OutputMuteState[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 6:
            OutputMuteCmdString = '{0} get outputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('OutputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('OutputMute', 'Off', qualifier)
                else:
                    print('Output Mute: Invalid/Unexpected Response for OutputMute')
        else:
            print('Invalid Command for UpdateOutputMute')

    def SetPhantomPower(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        PhantomPowerState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            PhantomPowerCmdString = '{0} set phantomPower {1} {2}\n'.format(tag, channel, PhantomPowerState[value])
            self.__SetHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPhantomPower')

    def UpdatePhantomPower(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 10:
            PhantomPowerCmdString = '{0} get phantomPower {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('PhantomPower', PhantomPowerCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('PhantomPower', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('PhantomPower', 'Off', qualifier)
            else:
                print('Phantom Power: Invalid/Unexpected Response for PhantomPower')
        else:
            print('Invalid Command for UpdatePhantomPower')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetRecallCmdString = 'DEVICE recallPreset {0}\r'.format(int(value) + 1000)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetSaveCmdString = 'DEVICE savePreset {0}\r'.format(int(value) + 1000)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetSave')

    def SetStandardMixerOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 24 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            StandardMixerOutputLevelCmdString = '{0} set outputLevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('StandardMixerOutputLevel', StandardMixerOutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStandardMixerOutputLevel')

    def UpdateStandardMixerOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 24:
            StandardMixerOutputLevelCmdString = '{0} get outputLevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('StandardMixerOutputLevel', StandardMixerOutputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('StandardMixerOutputLevel', value, qualifier)
                else:
                    print('Standard Mixer Output Level: Invalid/Unexpected Response for StandardMixerOutputLevel')
        else:
            print('Invalid Command for UpdateStandardMixerOutputLevel')

    def SetStandardMixerOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        StandardMixerOutputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 24:
            StandardMixerOutputMuteCmdString = '{0} set outputMute {1} {2}\n'.format(tag, channel, StandardMixerOutputMuteState[value])
            self.__SetHelper('StandardMixerOutputMute', StandardMixerOutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStandardMixerOutputMute')

    def UpdateStandardMixerOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 24:
            StandardMixerOutputMuteCmdString = '{0} get outputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('StandardMixerOutputMute', StandardMixerOutputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('StandardMixerOutputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('StandardMixerOutputMute', 'Off', qualifier)
                else:
                    print('Standard Mixer Output Mute: Invalid/Unexpected Response for StandardMixerOutputMute')
        else:
            print('Invalid Command for UpdateStandardMixerOutputMute')

    def SetUSBInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 12
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            USBInputLevelCmdString = '{0} set inputLevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('USBInputLevel', USBInputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetUSBInputLevel')

    def UpdateUSBInputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBInputLevelCmdString = '{0} get inputLevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('USBInputLevel', USBInputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('USBInputLevel', value, qualifier)
                else:
                    print('USB Input Level: Invalid/Unexpected Response for USBInputLevel')
        else:
            print('Invalid Command for UpdateUSBInputLevel')

    def SetUSBInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        USBInputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBInputMuteCmdString = '{0} set inputMute {1} {2}\n'.format(tag, channel, USBInputMuteState[value])
            self.__SetHelper('USBInputMute', USBInputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetUSBInputMute')

    def UpdateUSBInputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBInputMuteCmdString = '{0} get inputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('USBInputMute', USBInputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('USBInputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('USBInputMute', 'Off', qualifier)
                else:
                    print('USB Input Mute: Invalid/Unexpected Response for USBInputMute')
        else:
            print('Invalid Command for UpdateUSBInputMute')

    def SetUSBOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        ValueConstraints = {
            'Min': -100,
            'Max': 0
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2 and ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            USBOutputLevelCmdString = '{0} set outputLevel {1} {2}\n'.format(tag, channel, value)
            self.__SetHelper('USBOutputLevel', USBOutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetUSBOutputLevel')

    def UpdateUSBOutputLevel(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBOutputLevelCmdString = '{0} get outputLevel {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('USBOutputLevel', USBOutputLevelCmdString, value, qualifier)
            if res:
                result = findall(self.findDigit, res)
                if result:
                    value = int(result[0])
                    self.WriteStatus('USBOutputLevel', value, qualifier)
                else:
                    print('USB Output Level: Invalid/Unexpected Response for USBOutputLevel')
        else:
            print('Invalid Command for UpdateUSBOutputLevel')

    def SetUSBOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        USBOutputMuteState = {
            'On': 'true',
            'Off': 'false'
        }

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBOutputMuteCmdString = '{0} set outputMute {1} {2}\n'.format(tag, channel, USBOutputMuteState[value])
            self.__SetHelper('USBOutputMute', USBOutputMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetUSBOutputMute')

    def UpdateUSBOutputMute(self, value, qualifier):

        tag = qualifier['Instance Tag']
        channel = qualifier['Channel']
        if ' ' in tag:
            tag = '\"' + tag + '\"'

        if '/' not in tag and '&' not in tag and 1 <= int(channel) <= 2:
            USBOutputMuteCmdString = '{0} get outputMute {1}\n'.format(tag, channel)
            res = self.__UpdateHelper('USBOutputMute', USBOutputMuteCmdString, value, qualifier)
            if res:
                if 'true' in res:
                    self.WriteStatus('USBOutputMute', 'On', qualifier)
                elif 'false' in res:
                    self.WriteStatus('USBOutputMute', 'Off', qualifier)
                else:
                    print('USB Output Mute: Invalid/Unexpected Response for USBOutputMute')
        else:
            print('Invalid Command for UpdateUSBOutputMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if '+OK' in response:
            return response
        elif '-ERR' in response:
            print('{0} {1}'.format(sourceCmdName, response))
            return ''
        else:
            return ''

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex)
            if not res:
                return ''
            else:
                res = res.decode()
                return self.__CheckResponseForErrors(command, res)

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
                    except BaseException:
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
        except BaseException:
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
                result = search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
