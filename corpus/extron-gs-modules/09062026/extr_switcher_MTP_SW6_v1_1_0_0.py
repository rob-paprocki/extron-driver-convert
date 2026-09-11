from extronlib.interface import SerialInterface, EthernetClientInterface


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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Parameters': ['Input'], 'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'RS232Insert': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAudioGainAttenuation(self, value, qualifier):

        AudioGainAttenuationConstraints = {
            'Min': -18,
            'Max': 24
        }
        ChannelConstraints = {
            'Min': 1,
            'Max': 6
        }
        channel = qualifier['Input']

        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max'] and AudioGainAttenuationConstraints['Min'] <= value <= AudioGainAttenuationConstraints['Max']:
            if value >= 0:
                AudioGainAttenuationCmdString = '{0}*{1}G'.format(channel, value)
            elif value < 0:
                AudioGainAttenuationCmdString = '{0}*{1}g'.format(channel, -value)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        ChannelConstraints = {
            'Min': 1,
            'Max': 6
        }
        channel = qualifier['Input']

        if ChannelConstraints['Min'] <= int(channel) <= ChannelConstraints['Max']:
            AudioGainAttenuationCmdString = '{0}G'.format(channel)
            res = self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('AudioGainAttenuation', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Gain Attenuation: Invalid/Unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateAudioGainAttenuation')

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1'
        }
        AudioMuteCmdString = '{0}Z'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdateHandler(value, qualifier, 'AudioMute')

    def SetAutoSwitchMode(self, value, qualifier):

        AutoSwitchModeStates = {
            'Off': '1',
            'On': '2'
        }
        AutoSwitchModeCmdString = '{0}#'.format(AutoSwitchModeStates[value])
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):
        self.UpdateHandler(value, qualifier, 'AutoSwitchMode')

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'On': '1'
        }
        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):
        self.UpdateHandler(value, qualifier, 'ExecutiveMode')

    def UpdateHandler(self, value, qualifier, command):

        AutoSwitchModeStateNames = {
            '1': 'Off',
            '2': 'On'
        }
        AudioMuteStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        ExecutiveModeStateNames = {
            '0': 'Off',
            '1': 'On'
        }
        CmdString = 'i'
        res = self.__UpdateHelper(command, CmdString, value, qualifier)
        if res:
            try:
                videoInputValue = res[1:2]
                self.WriteStatus('Input', videoInputValue, {'Type': 'Video'})

                audioInputValue = res[4:5]
                self.WriteStatus('Input', audioInputValue, {'Type': 'Audio'})

                if videoInputValue == audioInputValue:
                    AVInputValue = videoInputValue
                else:
                    AVInputValue = '0'

                self.WriteStatus('Input', AVInputValue, {'Type': 'Audio/Video'})
            except IndexError:
                self.Error(['Input: Invalid/Unexpected response'])

            try:
                switchModeValue = res[7:8]
                self.WriteStatus('AutoSwitchMode', AutoSwitchModeStateNames[switchModeValue], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Switch Mode: Invalid/Unexpected response'])

            try:
                audioMuteValue = res[17:18]
                self.WriteStatus('AudioMute', AudioMuteStateNames[audioMuteValue], qualifier)
            except (KeyError, IndexError):
                self.Error(['Audio Mute: Invalid/Unexpected response'])

            try:
                executiveValue = res[22:23]
                self.WriteStatus('ExecutiveMode', ExecutiveModeStateNames[executiveValue], qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/Unexpected response'])

    def SetInput(self, value, qualifier):

        SwitchType = qualifier['Type']
        InputConstraints = {
            'Min': 1,
            'Max': 6
        }
        SwitchTypeNames = {
            'Audio': '$',
            'Video': '&',
            'Audio/Video': '!'
        }
        if InputConstraints['Min'] <= int(value) <= InputConstraints['Max']:
            InputCmdString = '{0}{1}'.format(value, SwitchTypeNames[SwitchType])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):
        self.UpdateHandler(value, qualifier, 'Input')

    def SetRS232Insert(self, value, qualifier):

        RS232Insert = {
            'Off': '0',
            'On': '1'
        }
        RS232InsertCmdString = 'w1*{0}Lrpt|'.format(RS232Insert[value])
        self.__SetHelper('RS232Insert', RS232InsertCmdString, value, qualifier)

    def UpdateRS232Insert(self, value, qualifier):

        RS232InsertStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        RS232InsertCmdString = 'w1Lrpt|'
        res = self.__UpdateHelper('RS232Insert', RS232InsertCmdString, value, qualifier).strip()
        if res:
            try:
                value = RS232InsertStateNames[res]
                self.WriteStatus('RS232Insert', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['RS232 Insert: Invalid/Unexpected response'])

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }

        if value < VolumeConstraints['Min'] or value > VolumeConstraints['Max']:
            self.Discard('Invalid Command for SetVolume')
        else:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[3:6])
                self.WriteStatus('Volume', value, qualifier)

            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/Unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E10': 'Invalid command',
            'E11': 'Invalid preset number',
            'E13': 'Invalid parameter',
            'E14': 'Command not available for this configuration',
        }
        if response:
            error_code = DEVICE_ERROR_CODES.get(response[:-2])
            if error_code:
                self.Error(['{0}: {1}'.format(sourceCmdName, error_code)])
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
