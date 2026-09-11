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
        self._DeviceID = '1'

        self.Models = {
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Colorspace': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'FileTransport': {'Parameters': ['File'], 'Status': {}},
            'OutputFormat': {'Status': {}},
            'RelayOutput': {'Parameters': ['Relay Type'], 'Status': {}},
            'Transport': {'Status': {}},
            'VideoMute': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'All':
            self._DeviceID = '127'
        elif 0 <= int(value) <= 126:
            self._DeviceID = value

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        AudioMuteCmdString = '{0}@{1}AD\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetColorspace(self, value, qualifier):

        ValueStateValues = {
            'YPbPr': '1',
            'RGsB': '0'
        }

        ColorspaceCmdString = '{0}@{1}VC\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Colorspace', ColorspaceCmdString, value, qualifier)

    def UpdateColorspace(self, value, qualifier):

        ValueStateValues = {
            '1': 'YPbPr',
            '0': 'RGsB'
        }

        ColorspaceCmdString = '{0}@VC\r'.format(self._DeviceID)
        res = self.__UpdateHelper('Colorspace', ColorspaceCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('Colorspace', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateColorspace')

    def UpdateDeviceStatus(self, value, qualifier):

        ValueStateValues = {
            '4': 'Playing',
            '1': 'Stopped',
            '0': 'Error',
            '5': 'Stilled',
            '6': 'Paused'
        }

        DeviceStatusCmdString = '{0}@?P\r'.format(self._DeviceID)
        res = self.__UpdateHelper('DeviceStatus', DeviceStatusCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = ValueStateValues[res[2:3]]
                self.WriteStatus('DeviceStatus', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateDeviceStatus')

    def SetFileTransport(self, value, qualifier):

        FileConstraints = {
            'Min': 0,
            'Max': 99999
        }

        ValueStateValues = {
            'Search': 'SE',
            'Play File': 'PL',
            'Loop File': 'LP',
            'Play Next': 'PN',
            'Loop Next': 'LN'
        }
        if FileConstraints['Min'] <= int(qualifier['File']) <= FileConstraints['Max']:
            FileTransportCmdString = '{0}@{1}{2}\r'.format(self._DeviceID, qualifier['File'], ValueStateValues[value])
            self.__SetHelper('FileTransport', FileTransportCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFileTransport')

    def SetOutputFormat(self, value, qualifier):

        OutputResolutionStates = {
            '1080i29': '1080i29',
            '720p59': '720p59',
            '480p': '480p',
            '480i': '480i',
            '1080i25': '1080i25',
            '720p50': '720p50',
            '576p': '576p',
            '576i': '576i'
        }

        OutputFormatCmdString = '{0}@{1}VO\r'.format(self._DeviceID, OutputResolutionStates[value])
        self.__SetHelper('OutputFormat', OutputFormatCmdString, value, qualifier)

    def UpdateOutputFormat(self, value, qualifier):

        OutputResolutionStates = {
            '1080i29': '1080i29',
            '720p59': '720p59',
            '480p': '480p',
            '480i': '480i',
            '1080i25': '1080i25',
            '720p50': '720p50',
            '576p': '576p',
            '576i': '576i'
        }

        OutputFormatCmdString = '{0}@VO\r'.format(self._DeviceID)
        res = self.__UpdateHelper('OutputFormat', OutputFormatCmdString, value, qualifier)
        if res:
            res = res.decode()
            try:
                value = OutputResolutionStates[res[0:-1]]
                self.WriteStatus('OutputFormat', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateOutputFormat')

    def SetRelayOutput(self, value, qualifier):

        RelayTypeStates = {
            'Play': 'P',
            'Fault': 'F'
        }

        ValueStateValues = {
            'On': '1',
            'Off': '0',
            'Auto': 'X'
        }

        RelayOutputCmdString = '{0}@{1}{2}RL\r'.format(self._DeviceID, ValueStateValues[value], RelayTypeStates[qualifier['Relay Type']])
        self.__SetHelper('RelayOutput', RelayOutputCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop': 'RJ',
            'Loop': 'LP',
            'Still': 'ST',
            'Pause': 'PA',
            'Play': 'PL'
        }

        TransportCmdString = '{0}@{1}\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '0',
            'Off': '1'
        }

        VideoMuteCmdString = '{0}@{1}VD\r'.format(self._DeviceID, ValueStateValues[value])
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            'E01\r': "Hardware Error.",
            'E04\r': "Feature Not Available.",
            'E06\r': "Invalid Argument.",
            'E12\r': "Search Error."
        }

        if response:
            error_code = DEVICE_ERROR_CODES.get(response)
            if error_code:
                print('{0} {1}'.format(sourceCmdName, error_code))
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.Unidirectional == 'True' or self._DeviceID == '127':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == '127':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\r')
            if not res:
                return ''
            else:
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
