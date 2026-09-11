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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioGainAttenuation': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'HDCPInputAuthorization': {'Parameters': ['Input'], 'Status': {}},
            'HDCPInputStatus': {'Parameters': ['Input'], 'Status': {}},
            'Input': {'Status': {}},
            'InputAudioSelection': {'Parameters': ['Input'], 'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VGAInputVideoFormat': {'Status': {}},
        }


    def SetAudioGainAttenuation(self, value, qualifier):

        if -18 <= value <= 10:
            if value < 0:
                AudioGainAttenuationCmdString = '{0}g'.format(abs(value))
            else:
                AudioGainAttenuationCmdString = '{0}G'.format(value)
            self.__SetHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioGainAttenuation')

    def UpdateAudioGainAttenuation(self, value, qualifier):

        AudioGainAttenuationCmdString = 'G'
        res = self.__UpdateHelper('AudioGainAttenuation', AudioGainAttenuationCmdString, value, qualifier)
        if res:
            try:
                value = int(res)
            except (ValueError, IndexError):
                self.Error(['Audio Gain Attenuation: Invalid/unexpected response'])
            else:
                self.WriteStatus('AudioGainAttenuation', value, qualifier)

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'Off': 'W0AUSW\r',
            'Highest Active Input': 'W1AUSW\r',
            'Lowest Active Input': 'W2AUSW\r'
        }

        AutoSwitchModeCmdString = ValueStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            '0': 'Off',
            '1': 'Highest Active Input',
            '2': 'Lowest Active Input'
        }

        AutoSwitchModeCmdString = 'WAUSW\r'
        res = self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
            except (KeyError, IndexError):
                self.Error(['Auto Switch Mode: Invalid/unexpected response'])
            else:
                self.WriteStatus('AutoSwitchMode', value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1X',
            'Off': '0X'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        ExecutiveModeCmdString = 'X'
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])
            else:
                self.WriteStatus('ExecutiveMode', value, qualifier)

    def SetHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        input = int(qualifier['Input'])
        if 2 <= input <= 3:
            HDCPInputAuthorizationCmdString = 'WE{0}*{1}HDCP\r'.format(input, ValueStateValues[value])
            self.__SetHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetHDCPInputAuthorization')

    def UpdateHDCPInputAuthorization(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        input = int(qualifier['Input'])
        if 2 <= input <= 3:
            HDCPInputAuthorizationCmdString = 'WE{0}HDCP\r'.format(input)
            res = self.__UpdateHelper('HDCPInputAuthorization', HDCPInputAuthorizationCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                except (KeyError, IndexError):
                    self.Error(['HDCP Input Authorization: Invalid/unexpected response'])
                else:
                    self.WriteStatus('HDCPInputAuthorization', value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def UpdateHDCPInputStatus(self, value, qualifier):

        ValueStateValues = {
            '0': 'No source device detected',
            '1': 'Source detected with HDCP',
            '2': 'Source detected but no HDCP is present'
        }

        input = int(qualifier['Input'])
        if 2 <= input <= 3:
            HDCPInputStatusCmdString = 'WI{0}HDCP\r'.format(input)
            res = self.__UpdateHelper('HDCPInputStatus', HDCPInputStatusCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                except (KeyError, IndexError):
                    self.Error(['HDCP Input Status: Invalid/unexpected response'])
                else:
                    self.WriteStatus('HDCPInputStatus', value, qualifier)
        else:
            self.Discard('Invalid Command for UpdateHDCPInputStatus')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            '1': '1!',
            '2': '2!',
            '3': '3!'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        InputCmdString = '!'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = res[0]
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])
            else:
                self.WriteStatus('Input', value, qualifier)

    def SetInputAudioSelection(self, value, qualifier):

        ValueStateValues = {
            'Auto': '0',
            'Digital Embedded': '1',
            'Analog': '2'
        }

        input = int(qualifier['Input'])
        if 1 <= input <= 3:
            InputAudioSelectionCmdString = 'WI{0}*{1}AFMT\r'.format(input, ValueStateValues[value])
            self.__SetHelper('InputAudioSelection', InputAudioSelectionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputAudioSelection')

    def UpdateInputAudioSelection(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto',
            '1': 'Digital Embedded',
            '2': 'Analog'
        }
        input = int(qualifier['Input'])
        if 1 <= input <= 3:
            InputAudioSelectionCmdString = 'WI{0}AFMT\r'.format(input)
            res = self.__UpdateHelper('InputAudioSelection', InputAudioSelectionCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                except (KeyError, IndexError):
                    self.Error(['Input Audio Selection: Invalid/unexpected response'])
                else:
                    self.WriteStatus('InputAudioSelection', value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def UpdateInputSignalStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'Active',
            '0': 'Not Active'
        }

        InputSignalStatusCmdString = '5S\r'
        res = self.__UpdateHelper('InputSignalStatus', InputSignalStatusCmdString, value, qualifier)
        if res:
            try:
                for i in range(3):
                    self.WriteStatus('InputSignalStatus', ValueStateValues[res[4:7][i]], {'Input': str(i + 1)})
            except (KeyError, IndexError):
                self.Error(['Input Signal Status: Invalid/unexpected response'])

    def SetVGAInputVideoFormat(self, value, qualifier):

        ValueStateValues = {
            'Auto Detect': '1*0\\',
            'RGB': '1*1\\',
            'YUV': '1*2\\'
        }

        VGAInputVideoFormatCmdString = ValueStateValues[value]
        self.__SetHelper('VGAInputVideoFormat', VGAInputVideoFormatCmdString, value, qualifier)

    def UpdateVGAInputVideoFormat(self, value, qualifier):

        ValueStateValues = {
            '0': 'Auto Detect',
            '1': 'RGB',
            '2': 'YUV'
        }

        VGAInputVideoFormatCmdString = '1\\'
        res = self.__UpdateHelper('VGAInputVideoFormat', VGAInputVideoFormatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
            except (KeyError, IndexError):
                self.Error(['VGA Input Video Format: Invalid/unexpected response'])
            else:
                self.WriteStatus('VGAInputVideoFormat', value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01': 'Invalid input number',
            'E06': 'Invalid switch attempt in this mode',
            'E10': 'Invalid command',
            'E13': 'Invalid parameter',
            'E14': 'Not valid for this configuration',
            'E17': 'Invalid command for signal type',
            'E22': 'Busy',
        }
        if response:
            for k, v in DEVICE_ERROR_CODES.items():
                if k in response:
                    self.Error(['{0} {1} {2}'.format(sourceCmdName, k, v)])
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

        self.lastInputSignalStatusUpdate = 0

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
