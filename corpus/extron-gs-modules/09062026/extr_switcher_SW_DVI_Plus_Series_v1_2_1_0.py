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
            'SW2 DVI A Plus': self.extr_2_11_SW2A,
            'SW2 DVI Plus': self.extr_2_11_SW2,
            'SW4 DVI A Plus': self.extr_2_11_SW4A,
            'SW4 DVI Plus': self.extr_2_11_SW4,
            'SW6 DVI A Plus': self.extr_2_11_SW6A,
            'SW6 DVI Plus': self.extr_2_11_SW6,
            'SW8 DVI Plus': self.extr_2_11_SW8,
            'SW8 DVI A Plus': self.extr_2_11_SW8A,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoSwitchMode': {'Status': {}},
            'AutoSwitchModeStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Parameters': ['Type'], 'Status': {}},
            'IRSensor': {'Status': {}},
            'InputSignalStatus': {'Parameters': ['Input'], 'Status': {}},
            'VideoMute': {'Status': {}},
        }

        self.InputSignalStatusRegex = re.compile('Sig([ 01]+)\r\n')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1Z',
            'Off': '0Z'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def UpdateAudioMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AudioMuteCmdString = 'Z'
        res = self.__UpdateHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('AudioMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AudioMute: Invalid/unexpected response'])

    def SetAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            'On': '1#',
            'Off': '0#'
        }

        AutoSwitchModeCmdString = ValueStateValues[value]
        self.__SetHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)

    def UpdateAutoSwitchMode(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AutoSwitchModeCmdString = '72#'
        res = self.__UpdateHelper('AutoSwitchMode', AutoSwitchModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoSwitchMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoSwitchMode: Invalid/unexpected response'])

    def UpdateAutoSwitchModeStatus(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        AutoSwitchCmdString = '72#'
        res = self.__UpdateHelper('AutoSwitchModeStatus', AutoSwitchCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[3]]
                self.WriteStatus('AutoSwitchModeStatus', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['AutoSwitchModeStatus: Invalid/unexpected response'])

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
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['ExecutiveMode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        if 0 <= int(value) <= self.InputSize:
            if self.ModelType == 'Non Audio':
                InputCmdString = '{}!'.format(value)
            else:
                typeVal = {
                    'Video': '&',
                    'Audio': '$',
                    'Audio/Video': '!'
                }[qualifier['Type']]
                InputCmdString = '{0}{1}'.format(value, typeVal)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        InputCmdString = 'I'
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            if self.ModelType == 'Non Audio':
                try:
                    value = res[1]
                    self.WriteStatus('Input', value, None)
                except(KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])
            else:
                try:
                    Input = self.AudioVideoPattern.match(res)
                    Video = Input.group(1)
                    Audio = Input.group(2)
                    if Video == Audio:
                        AVInput = Video
                    else:
                        AVInput = '0'
                    self.WriteStatus('Input', Audio, {'Type': 'Audio'})
                    self.WriteStatus('Input', Video, {'Type': 'Video'})
                    self.WriteStatus('Input', AVInput, {'Type': 'Audio/Video'})
                except (KeyError, IndexError):
                    self.Error(['Input: Invalid/unexpected response'])

    def SetIRSensor(self, value, qualifier):

        ValueStateValues = {
            'On': '0*65#',
            'Off': '1*65#'
        }

        IRSensorCmdString = ValueStateValues[value]
        self.__SetHelper('IRSensor', IRSensorCmdString, value, qualifier)

    def UpdateIRSensor(self, value, qualifier):

        ValueStateValues = {
            '0': 'On',
            '1': 'Off'
        }

        IRSensorCmdString = '65#'
        res = self.__UpdateHelper('IRSensor', IRSensorCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('IRSensor', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['IRSensor: Invalid/unexpected response'])

    def UpdateInputSignalStatus(self, value, qualifier):

        InputSignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active'
        }

        InputSignalStatusQueryCmdString = '0LS'
        res = self.__UpdateHelper('InputSignalStatus', InputSignalStatusQueryCmdString, value, qualifier)
        if res:
            try:
                index, valueList = 0, re.search(self.InputSignalStatusRegex, res).group(1).split()
                for value in valueList:
                    self.WriteStatus('InputSignalStatus', InputSignalStatusStateNames[value], {'Input': str(index + 1)})
                    index += 1
            except KeyError:
                self.Error(['InputSignalStatus: Invalid/unexpected response'])

    def __MatchInputSignalStatus(self, match, tag):

        InputSignalStatusStateNames = {
            '0': 'Not Active',
            '1': 'Active'
        }

        valueList = match.group(1).decode().split()

        index = 0
        for value in valueList:
            self.WriteStatus('InputSignalStatus', InputSignalStatusStateNames[value], {'Input': str(index + 1)})
            index += 1

    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On': '1B',
            'Off': '0B'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def UpdateVideoMute(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        VideoMuteCmdString = 'B'
        res = self.__UpdateHelper('VideoMute', VideoMuteCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('VideoMute', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['VideoMute: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        ResponseError = {
            'E01': 'Invalid Input',
            'E06': 'Invalid Input Selection',
            'E10': 'Invalid Command',
            'E11': 'Invalid preset number',
            'E12': 'Invalid port number',
            'E13': 'Invalid Value',
            'E14': 'Command not available for this configuration',
            'E17': 'System timed out',
            'E22': 'Busy',
            'E24': 'Privilege violation',
            'E25': 'Device not present',
            'E26': 'Maximum number of connections exceeded',
            'E27': 'Invalid event number',
            'E28': 'Bad filename or file not found',
            'E30': 'Hardware failure (followed by a colon [:] and a descriptor number)',
            'E31': 'Attempt to break port pass-through when it has not been set',
            'E32': 'Incorrect V-chip password'
        }

        RegError = re.compile('E(\d+)')
        Match = RegError.match(response)
        if Match:
            Result = Match.group()
            if Result in ResponseError:
                self.Error([ResponseError[Result]])
                return ''
        else:
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

    def extr_2_11_SW2(self):

        self.InputSize = 2
        self.ModelType = 'Non Audio'

    def extr_2_11_SW2A(self):

        self.InputSize = 2
        self.ModelType = 'Audio'
        self.AudioVideoPattern = re.compile('V([0-2]) A([0-2])')

    def extr_2_11_SW4(self):

        self.InputSize = 4
        self.ModelType = 'Non Audio'

    def extr_2_11_SW4A(self):

        self.InputSize = 4
        self.ModelType = 'Audio'
        self.AudioVideoPattern = re.compile('V([0-4]) A([0-4])')

    def extr_2_11_SW6(self):

        self.InputSize = 6
        self.ModelType = 'Non Audio'

    def extr_2_11_SW6A(self):

        self.InputSize = 6
        self.ModelType = 'Audio'
        self.AudioVideoPattern = re.compile('V([0-6]) A([0-6])')

    def extr_2_11_SW8(self):

        self.InputSize = 8
        self.ModelType = 'Non Audio'

    def extr_2_11_SW8A(self):

        self.InputSize = 8
        self.ModelType = 'Audio'
        self.AudioVideoPattern = re.compile('V([0-8]) A([0-8])')

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
