from extronlib.interface import SerialInterface, EthernetClientInterface
from re import findall, match


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {
            'MVX 88 VGA A': self.extr_15_99_88_VGA_A,
            'MVX 84 VGA A': self.extr_15_99_84_VGA_A,
            'MVX 48 VGA A': self.extr_15_99_48_VGA_A,
            'MVX 44 VGA A': self.extr_15_99_44_VGA_A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainandAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Parameters': ['Output'], 'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'GlobalAudioMute': {'Status': {}},
            'GlobalVideoMute': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output', 'Tie Type'], 'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output', 'Tie Type'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'VideoMute': {'Parameters': ['Output'], 'Status': {}},
        }

        self.inTieStatInit = 1
        self.OutputStatus = {'Audio': [], 'Video': []}

    def SetAudioGainandAttenuation(self, value, qualifier):

        ValueConstraints = {
            'Min': -18,
            'Max': 10
        }
        driverInput = qualifier['Input']
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 0 < int(driverInput) <= self.InputSize:
            if value < 0:
                AudioGainandAttenuationCmdString = '{0}*{1}g'.format(driverInput, abs(value))
            else:
                AudioGainandAttenuationCmdString = '{0}*{1}G'.format(driverInput, value)
            self.__SetHelper('AudioGainandAttenuation', AudioGainandAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainandAttenuation')

    def UpdateAudioGainandAttenuation(self, value, qualifier):

        driverInput = qualifier['Input']
        if 0 < int(driverInput) <= self.InputSize:
            AudioGainandAttenuationCmdString = '{0}g'.format(driverInput)
            res = self.__UpdateHelper('AudioGainandAttenuation', AudioGainandAttenuationCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('AudioGainandAttenuation', value, qualifier)
                except (KeyError, ValueError):
                    self.Error(['Audio Gain and Attenuation: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioGainandAttenuation')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        output = qualifier['Output']
        if 0 < int(output) <= self.OutputSize:
            AudioMuteCmdString = '{0}*{1}z'.format(output, ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        output = qualifier['Output']
        if 0 < int(output) <= self.OutputSize:
            AudioMuteCmdString = '{0}z'.format(output)
            res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('AudioMute', value, qualifier)
                except (KeyError, ValueError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioMute')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1x',
            'Off': '0x'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecutiveModeCmdString = 'x'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetGlobalAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*z',
            'Off': '0*z'
        }

        GlobalAudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('GlobalAudioMute', GlobalAudioMuteCmdString, value, qualifier)

    def SetGlobalVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1*b',
            'Off': '0*b'
        }

        GlobalVideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('GlobalVideoMute', GlobalVideoMuteCmdString, value, qualifier)

    def UpdateInputTieStatus(self, value, qualifier):

        self.UpdateOutputTieStatus(value, qualifier)

    def SetMatrixTieCommand(self, value, qualifier):

        TieTypeStates = {
            'Audio': '$',
            'Video': '%',
            'Audio/Video': '!'
        }
        driverInput = qualifier['Input']
        output = qualifier['Output']
        tie = TieTypeStates[qualifier['Tie Type']]
        if 0 <= int(driverInput) <= self.InputSize and 0 < int(output) <= self.OutputSize:
            MatrixTieCommandCmdString = '{0}*{1}{2}'.format(driverInput, output, tie)
            self.__SetHelper('MatrixTieCommand', MatrixTieCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def __SetMatrixStatus(self, output, newInput, tag):

        oldInput = self.OutputStatus[tag][int(output) - 1]
        opTag = 'Audio' if tag == 'Video' else 'Video'

        if oldInput != newInput:
            self.WriteStatus('OutputTieStatus', newInput, {'Output': output, 'Tie Type': tag})

            opInVal = self.ReadStatus('OutputTieStatus', {'Output': output, 'Tie Type': opTag})  # get opposite input

            prevInputTieStatus = self.ReadStatus('InputTieStatus', {'Input': oldInput, 'Output': output})
            if prevInputTieStatus == 'Audio/Video':
                self.WriteStatus('InputTieStatus', opTag, {'Input': oldInput, 'Output': output})
            else:
                self.WriteStatus('InputTieStatus', 'Untied', {'Input': oldInput, 'Output': output})

            if opInVal == newInput:
                self.WriteStatus('OutputTieStatus', newInput, {'Output': output, 'Tie Type': 'Audio/Video'})
                self.WriteStatus('InputTieStatus', 'Audio/Video', {'Input': newInput, 'Output': output})
            else:
                self.WriteStatus('OutputTieStatus', '0', {'Output': output, 'Tie Type': 'Audio/Video'})
                self.WriteStatus('InputTieStatus', tag, {'Input': newInput, 'Output': output})

            self.OutputStatus[tag][int(output) - 1] = newInput

    def UpdateOutputTieStatus(self, value, qualifier):

        if self.inTieStatInit == 1:
            for input_ in range(1, self.InputSize + 1):
                for output_ in range(1, self.InputSize + 1):
                    self.WriteStatus('InputTieStatus', 'Untied', {'Input': str(input_), 'Output': str(output_)})
            self.inTieStatInit = 0

        command = 'OutputTieStatus' if 'Tie Type' in qualifier else 'InputTieStatus'
        res = self.__UpdateHelper(command, '\x1B0VC\r', value, qualifier)
        if res:
            try:
                response = res.split('Vid')
                if response:
                    vid = findall('\d+', response[0])
                    aud = findall('\d+', response[1])
                    output = 1
                    for inputNum in vid:
                        self.__SetMatrixStatus(str(output), str(int(inputNum)), 'Video')
                        output += 1

                    output = 1
                    for inputNum in aud:
                        self.__SetMatrixStatus(str(output), str(int(inputNum)), 'Audio')
                        output += 1
            except (ValueError, IndexError):
                self.Error(['{}: Invalid/unexpected response'.format(command)])

    def SetPresetRecall(self, value, qualifier):

        if 0 < int(value) <= 16:
            PresetRecallCmdString = '{0}.'.format(value)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        if 0 < int(value) <= 16:
            PresetSaveCmdString = '{0},'.format(value)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        output = qualifier['Output']
        if 0 < int(output) <= self.OutputSize:
            VideoMuteCmdString = '{0}*{1}b'.format(output, ValueStateValues[value])
            self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVideoMute')

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        output = qualifier['Output']
        if 0 < int(output) <= self.OutputSize:
            VideoMuteCmdString = '{0}b'.format(output)
            res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('VideoMute', value, qualifier)
                except (KeyError, ValueError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateVideoMute')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            '01': 'Invalid input channel number (out of range)',
            '10': 'Invalid command',
            '11': 'Invalid preset number (out of range)',
            '12': 'Invalid output number (out of range)',
            '13': 'Invalid value (out of range)',
            '14': 'Invalid command for this configuration'
        }
        if response:
            err = match('E(\d+)\r\n', response)
            if err:
                self.Error(['Error {0}: {1}'.format(sourceCmdName, DEVICE_ERROR_CODES[err.group(1)])])
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
        self.inTieStatInit = 1
        self.OutputStatus['Video'] = ['Initial' for i in range(0, self.OutputSize)]
        self.OutputStatus['Audio'] = ['Initial' for i in range(0, self.OutputSize)]

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def extr_15_99_44_VGA_A(self):

        self.InputSize = 4
        self.OutputSize = 4

    def extr_15_99_48_VGA_A(self):

        self.InputSize = 4
        self.OutputSize = 8

    def extr_15_99_84_VGA_A(self):

        self.InputSize = 8
        self.OutputSize = 4

    def extr_15_99_88_VGA_A(self):

        self.InputSize = 8
        self.OutputSize = 8

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
