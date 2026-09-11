from extronlib.interface import SerialInterface, EthernetClientInterface
import re


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
            'SW2 VGA Ars': self.extr_2_23_sw2_VGA_Ars,
            'SW2 VGArs': self.extr_2_23_sw2_VGArs,
            'SW4 VGA Ars': self.extr_2_23_sw4_VGA_Ars,
            'SW4 VGArs': self.extr_2_23_sw4_VGArs,
            'SW6 VGA Ars': self.extr_2_23_sw6_VGA_Ars,
            'SW6 VGArs': self.extr_2_23_sw6_VGArs,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'Off': '0',
            'On': '1'
        }

        AudioMuteCmdString = '{0}Z'.format(AudioMuteState[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'On': '2',
            'Off': '1'
        }

        AutoSwitchModeCmdString = '{0}#'.format(ValueStateValues[value])
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeState = {
            'Off': '0',
            'On': '1'
        }

        ExecutiveModeCmdString = '{0}X'.format(ExecutiveModeState[value])
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ExecutiveModeStateNames = {
            '0': 'Off',
            '1': 'On'
        }

        executiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', executiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ExecutiveModeStateNames[res.strip()]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        if self.model == 'VGA Ars':
            SwitchType = qualifier['Type']
            SwitchTypeNames = {
                'Audio': '$',
                'Video': '&',
                'Audio Video': '!'
            }

            if 0 <= int(value) <= self.InputSize:
                InputCmdString = '{0}{1}'.format(value, SwitchTypeNames[SwitchType])
                if SwitchType == 'Audio Video':
                    self.__SetHelper('Input', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')

        elif self.model == 'VGArs':
            if 0 <= int(value) <= self.InputSize:
                InputCmdString = '{0}&'.format(value)
                self.__SetHelper('Video', InputCmdString, value, qualifier)
            else:
                self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        if self.model == 'VGA Ars':
            SwitchingModeStateNames = {
                '1': 'Off',
                '2': 'On'
            }

            VideoMuteStateNames = {
                '0': 'Off',
                '1': 'On'
            }

            AudioMuteStateNames = {
                '0': 'Off',
                '1': 'On'
            }

            InputCmdString = 'I'
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    videoInputValue = res[1:2]
                    audioInputValue = res[4:5]

                    if videoInputValue == audioInputValue:
                        AVInputValue = videoInputValue
                    else:
                        AVInputValue = '0'

                    self.WriteStatus('Input', audioInputValue, {'Type': 'Audio'})
                    self.WriteStatus('Input', videoInputValue, {'Type': 'Video'})
                    self.WriteStatus('Input', AVInputValue, {'Type': 'Audio Video'})

                except (ValueError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])

                try:
                    switchModeValue = res[7:8]
                    self.WriteStatus('AutoSwitchMode', SwitchingModeStateNames[switchModeValue], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Switch Mode: Invalid/unexpected response'])

                try:
                    videoMuteValue = res[12:13]
                    self.WriteStatus('VideoMute', VideoMuteStateNames[videoMuteValue], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])

                try:
                    audioMuteValue = res[17:18]
                    self.WriteStatus('AudioMute', AudioMuteStateNames[audioMuteValue], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Audio Mute: Invalid/unexpected response'])
        elif self.model == 'VGArs':
            SwitchingModeStateNames = {
                '1': 'Off',
                '2': 'On'
            }

            VideoMuteStateNames = {
                '0': 'Off',
                '1': 'On'
            }

            InputCmdString = 'I'
            res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
            if res:
                try:
                    InputValue = res[1:2]
                    self.WriteStatus('Input', InputValue, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])

                try:
                    switchModeValue = res[7:8]
                    self.WriteStatus('AutoSwitchMode', SwitchingModeStateNames[switchModeValue], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Auto Switch Mode: Invalid/unexpected response'])

                try:
                    videoMuteValue = res[12:13]
                    self.WriteStatus('VideoMute', VideoMuteStateNames[videoMuteValue], qualifier)
                except (KeyError, IndexError):
                    self.Error(['Video Mute: Invalid/unexpected response'])

    def UpdateInputSignalStatus(self, value, qualifier):

        SignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active'
        }

        signalStatusCmdString = '0S'
        res = self.__UpdateHelper('InputSignalStatus', signalStatusCmdString, value, qualifier)
        if res:
            try:
                res = res[4::2].strip()
                for i in range(self.InputSize):
                    qualifier = {'Input': str(i + 1)}
                    value = SignalStatusStateNames[res[i]]
                    self.WriteStatus('InputSignalStatus', value, qualifier)

            except (KeyError, IndexError):
                self.Error(['Input Signal Status: Invalid/unexpected response'])

    def SetVideoMute(self, value, qualifier):

        VideoMuteState = {
            'Off': '0',
            'On': '1'
        }

        VideoMuteCmdString = '{0}B'.format(VideoMuteState[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):
        self.UpdateInput(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number (out of range)',
            'E06': 'Ivalid input channel change (auto switch mode active)',
            'E09': 'Invalid parameter',
            'E10': 'Invalid command',
            'E13': 'Invalid value',
            'E14': 'Command not available for this configuration'
        }

        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    errorString = '{0} {1} {2}'.format(sourceCmdName, k, v)
                    self.Error([errorString])
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

    def extr_2_23_sw2_VGA_Ars(self):
        self.model = 'VGA Ars'
        self.InputSize = 2

    def extr_2_23_sw2_VGArs(self):
        self.model = 'VGArs'
        self.InputSize = 2

    def extr_2_23_sw4_VGA_Ars(self):
        self.model = 'VGA Ars'
        self.InputSize = 4

    def extr_2_23_sw4_VGArs(self):
        self.model = 'VGArs'
        self.InputSize = 4

    def extr_2_23_sw6_VGA_Ars(self):
        self.model = 'VGA Ars'
        self.InputSize = 6

    def extr_2_23_sw6_VGArs(self):
        self.model = 'VGArs'
        self.InputSize = 6

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
