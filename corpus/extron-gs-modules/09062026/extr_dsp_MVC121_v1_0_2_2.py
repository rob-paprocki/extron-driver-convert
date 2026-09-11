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
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'FixedOutputMute': {'Parameters': ['Fixed output'], 'Status': {}},
            'LineLevel': {'Parameters': ['Input'], 'Status': {}},
            'LineMute': {'Parameters': ['Input'], 'Status': {}},
            'MicMute': {'Parameters': ['Input'], 'Status': {}},
            'MicInputLevel': {'Parameters': ['Input'], 'Status': {}},
            'MicLineMix': {'Parameters': ['Input'], 'Status': {}},
            'MixpointMute': {'Parameters': ['Mixpoint'], 'Status': {}},
            'VariableOutputMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.VerboseDisabled = True

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'Exe([0-2])\r\n'), self.__MatchExecutiveMode, None)
            self.AddMatchString(re.compile(b'DsM(6000[2-3])\*([0-1])\r\n'), self.__MatchFixedOutputMute, None)
            self.AddMatchString(re.compile(b'DsG(3000[0-1])\*(-{0,1}\d{1,3})\r\n'), self.__MatchLineLevel, None)
            self.AddMatchString(re.compile(b'DsM(3000[0-1])\*([0-1])\r\n'), self.__MatchLineMute, None)
            self.AddMatchString(re.compile(b'DsG(4000[0-1])\*(-{0,1}\d{1,3})\r\n'), self.__MatchMicInputLevel, None)
            self.AddMatchString(re.compile(b'DsM(4000[0-1])\*([0-1])\r\n'), self.__MatchMicMute, None)
            self.AddMatchString(re.compile(b'In([1-3]) Aud(-{0,1}\d{1,2})\r\n'), self.__MatchMicLineMix, None)
            self.AddMatchString(re.compile(b'DsM(20[0-2]{3})\*([0-1])\r\n'), self.__MatchMixpointMute, None)
            self.AddMatchString(re.compile(b'Amt([0-1])\r\n'), self.__MatchVariableOutputMute, None)
            self.AddMatchString(re.compile(b'Vol([0-9]{1,3})\r\n'), self.__MatchVolume, None)
            self.AddMatchString(re.compile(b'e:[0-9A-F]{4}.\*\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'i:.\*\r'), self.__MatchError, None)
            self.AddMatchString(re.compile(b'Vrb3\r\n'), self.__MatchVerboseMode, None)

    def __MatchVerboseMode(self, match, qualifier):
        self.OnConnected()
        self.VerboseDisabled = False

    def SetExecutiveMode(self, value, qualifier):

        ExecutiveModeValues = {
            'Off': '0',
            'Mode 1': '1',
            'Mode 2': '2',
        }

        self.__SetHelper('ExecutiveMode', '{0}X'.format(ExecutiveModeValues[value]), value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        self.__UpdateHelper('ExecutiveMode', 'X', value, qualifier)

    def __MatchExecutiveMode(self, match, tag):

        ExecutiveModeStateNames = {
            b'0': 'Off',
            b'1': 'Mode 1',
            b'2': 'Mode 2',
        }

        self.WriteStatus('ExecutiveMode', ExecutiveModeStateNames[match.group(1)], None)

    def SetFixedOutputMute(self, value, qualifier):

        FixedOutputState = qualifier['Fixed output']
        FixedOutputStateValues = {
            'Left channel output': '60002',
            'Right channel output': '60003'
        }

        FixedOutputMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('FixedOutputMute', '\x1bM{0}*{1}AU\x0D'.format(FixedOutputStateValues[FixedOutputState],
                                                                        FixedOutputMuteStateValues[value]), value, qualifier)

    def UpdateFixedOutputMute(self, value, qualifier):

        FixedOutputStateValues = {
            'Left channel output': '60002',
            'Right channel output': '60003'
        }

        FixedOutputMuteCmdString = '\x1bM{0}AU\x0D'.format(FixedOutputStateValues[qualifier['Fixed output']])
        self.__UpdateHelper('FixedOutputMute', FixedOutputMuteCmdString, value, qualifier)

    def __MatchFixedOutputMute(self, match, tag):

        FixedOutputStateValues = {
            b'60002': 'Left channel output',
            b'60003': 'Right channel output',
        }

        FixedOutputMuteStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('FixedOutputMute', FixedOutputMuteStateValues[match.group(2)],
                         {'Fixed output': FixedOutputStateValues[match.group(1)]})

    def SetLineLevel(self, value, qualifier):

        LineLevelState = qualifier['Input']
        LineLevelStateValues = {
            'Line input 3 left': '30000',
            'Line input 3 right': '30001'
        }

        if value < -18.0 or value > 24.0:
            self.Discard('Invalid Command for SetLineLevel')
        else:

            self.__SetHelper('LineLevel', '\x1bG{0}*{1}AU\x0D'.format(LineLevelStateValues[LineLevelState],
                                                                      int(value * 10)), value, qualifier)

    def UpdateLineLevel(self, value, qualifier):

        LineLevelStateValues = {
            'Line input 3 left': '30000',
            'Line input 3 right': '30001'
        }

        LineLevelCmdString = '\x1bG{0}AU\x0D'.format(LineLevelStateValues[qualifier['Input']])
        self.__UpdateHelper('LineLevel', LineLevelCmdString, value, qualifier)

    def __MatchLineLevel(self, match, tag):

        LineLevelStateValues = {
            b'30000': 'Line input 3 left',
            b'30001': 'Line input 3 right',
        }

        value = float(match.group(2)) / 10
        value = int(value * 10) / 10.0

        self.WriteStatus('LineLevel', value, {'Input': LineLevelStateValues[match.group(1)]})

    def SetLineMute(self, value, qualifier):

        InputSelectState = qualifier['Input']
        InputSelectStateValues = {
            'Line input 3 left': '30000',
            'Line input 3 right': '30001',
        }

        LineMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('LineMute', '\x1bM{0}*{1}AU\x0D'.format(InputSelectStateValues[InputSelectState], LineMuteStateValues[value]), value, qualifier)

    def UpdateLineMute(self, value, qualifier):

        InputSelectStateValues = {
            'Line input 3 left': '30000',
            'Line input 3 right': '30001',
        }

        LineMuteCmdString = '\x1bM{0}AU\x0D'.format(InputSelectStateValues[qualifier['Input']])
        self.__UpdateHelper('LineMute', LineMuteCmdString, value, qualifier)

    def __MatchLineMute(self, match, tag):

        InputSelectStateValues = {
            b'30000': 'Line input 3 left',
            b'30001': 'Line input 3 right',
        }

        LineMuteStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('LineMute', LineMuteStateValues[match.group(2)], {'Input': InputSelectStateValues[match.group(1)]})

    def SetMicInputLevel(self, value, qualifier):

        InputSelectState = qualifier['Input']
        InputSelectStateValues = {
            'Mic/Line Input 1': '40000',
            'Mic/Line Input 2': '40001',
        }

        if value < -18.0 or value > 60.0:
            self.Discard('Invalid Command for SetMicInputLevel')
        else:
            self.__SetHelper('MicInputLevel', '\x1bG{0}*{1}AU\x0D'.format(InputSelectStateValues[InputSelectState], int(value * 10)), value, qualifier)

    def UpdateMicInputLevel(self, value, qualifier):

        InputSelectStateValues = {
            'Mic/Line Input 1': '40000',
            'Mic/Line Input 2': '40001',
        }

        MicInputSelectionCmdString = '\x1bG{0}AU\x0D'.format(InputSelectStateValues[qualifier['Input']])
        self.__UpdateHelper('MicInputLevel', MicInputSelectionCmdString, value, qualifier)

    def __MatchMicInputLevel(self, match, tag):

        InputSelectStateValues = {
            b'40000': 'Mic/Line Input 1',
            b'40001': 'Mic/Line Input 2',
        }

        self.WriteStatus('MicInputLevel', float((int(match.group(2).decode()) / 10)),
                         {'Input': InputSelectStateValues[match.group(1)]})

    def SetMicMute(self, value, qualifier):

        MicInputState = qualifier['Input']
        MicInputStateValues = {
            'Mic Input 1': '40000',
            'Mic Input 2': '40001',
        }

        MicMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        self.__SetHelper('MicMute', '\x1bM{0}*{1}AU\x0D'.format(MicInputStateValues[MicInputState],
                                                                MicMuteStateValues[value]), value, qualifier)

    def UpdateMicMute(self, value, qualifier):

        MicInputStateValues = {
            'Mic Input 1': '40000',
            'Mic Input 2': '40001',
        }

        MicMuteCmdString = '\x1bM{0}AU\x0D'.format(MicInputStateValues[qualifier['Input']])
        self.__UpdateHelper('MicMute', MicMuteCmdString, value, qualifier)

    def __MatchMicMute(self, match, tag):

        MicInputStateValues = {
            b'40000': 'Mic Input 1',
            b'40001': 'Mic Input 2',
        }

        MicMuteStateValues = {
            b'1': 'On',
            b'0': 'Off',
        }

        self.WriteStatus('MicMute', MicMuteStateValues[match.group(2)], {'Input': MicInputStateValues[match.group(1)]})

    def SetMicLineMix(self, value, qualifier):

        MicLineMixState = qualifier['Input']
        MicLineMixValues = {
            'Mic 1 Mix-Point': '1',
            'Mic 2 Mix-Point': '2',
            'Line 3 Mix-Point': '3',
        }

        if value < -24 or value > 12:
            self.Discard('Invalid Command for SetMicLineMix')
        else:
            self.__SetHelper('MicLineMix', '{0}*{1}G'.format(MicLineMixValues[MicLineMixState], value), value, qualifier)

    def UpdateMicLineMix(self, value, qualifier):

        MicLineMixValues = {
            'Mic 1 Mix-Point': '1',
            'Mic 2 Mix-Point': '2',
            'Line 3 Mix-Point': '3',
        }

        MicLineMixCmdString = '{0}G'.format(MicLineMixValues[qualifier['Input']])
        self.__UpdateHelper('MicLineMix', MicLineMixCmdString, value, qualifier)

    def __MatchMicLineMix(self, match, tag):

        MicLineMixValues = {
            b'1': 'Mic 1 Mix-Point',
            b'2': 'Mic 2 Mix-Point',
            b'3': 'Line 3 Mix-Point',
        }

        self.WriteStatus('MicLineMix', int(match.group(2)), {'Input': MicLineMixValues[match.group(1)]})

    def SetMixpointMute(self, value, qualifier):

        MicInputState = qualifier['Mixpoint']
        MicInputStateValues = {
            'Input 1 to left output': '20000',
            'Input 2 to left output': '20100',
            'Input 3 to left output': '20200',
            'Input 1 to right output': '20001',
            'Input 2 to right output': '20101',
            'Input 3 to right output': '20201',
        }

        MixpointMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        MixpointMuteCmdString = MixpointMuteStateValues[value]
        self.__SetHelper('MixpointMute', '\x1bM{0}*{1}AU\x0D'.format(MicInputStateValues[MicInputState],
                                                                     MixpointMuteStateValues[value]), value, qualifier)

    def UpdateMixpointMute(self, value, qualifier):

        MicInputStateValues = {
            'Input 1 to left output': '20000',
            'Input 2 to left output': '20100',
            'Input 3 to left output': '20200',
            'Input 1 to right output': '20001',
            'Input 2 to right output': '20101',
            'Input 3 to right output': '20201',
        }

        MixpointMuteCmdString = '\x1bM{0}AU\x0D'.format(MicInputStateValues[qualifier['Mixpoint']])
        self.__UpdateHelper('MixpointMute', MixpointMuteCmdString, value, qualifier)

    def __MatchMixpointMute(self, match, tag):

        MicInputStateValues = {
            b'20000': 'Input 1 to left output',
            b'20100': 'Input 2 to left output',
            b'20200': 'Input 3 to left output',
            b'20001': 'Input 1 to right output',
            b'20101': 'Input 2 to right output',
            b'20201': 'Input 3 to right output'
        }

        MixpointMuteStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        self.WriteStatus('MixpointMute', MixpointMuteStateValues[match.group(2)],
                         {'Mixpoint': MicInputStateValues[match.group(1)]})

    def SetVariableOutputMute(self, value, qualifier):

        VariableOutputMuteStateValues = {
            'On': '1',
            'Off': '0'
        }

        VariableOutputMuteCmdString = VariableOutputMuteStateValues[value]
        self.__SetHelper('VariableOutputMute', '{0}Z'.format(VariableOutputMuteStateValues[value]), value, qualifier)

    def UpdateVariableOutputMute(self, value, qualifier):

        VariableOutputMuteCmdString = 'Z'
        self.__UpdateHelper('VariableOutputMute', VariableOutputMuteCmdString, value, qualifier)

    def __MatchVariableOutputMute(self, match, tag):

        VariableOutputMuteStateValues = {
            b'1': 'On',
            b'0': 'Off'
        }

        value = VariableOutputMuteStateValues[match.group(1)]
        self.WriteStatus('VariableOutputMute', value, None)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100,
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            VolumeCmdString = '{0}V'.format(value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        VolumeCmdString = 'V'
        self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)

    def __MatchVolume(self, match, tag):

        value = int(match.group(1).decode())
        self.WriteStatus('Volume', value, None)

    def __SetHelper(self, command, commandstring, value, qualifier):
        if self.VerboseDisabled:
            @Wait(1)
            def SendVerbose():
                self.Send('w3cv\r\n')
                self.Send(commandstring)
        else:
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

            if self.VerboseDisabled:
                @Wait(1)
                def SendVerbose():
                    self.Send('w3cv\r\n')
                    self.Send(commandstring)
            else:
                self.Send(commandstring)

    def __MatchError(self, match, tag):
        value = match.group(0).decode().split(':')
        self.Error([value[1]])

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False
        self.VerboseDisabled = True

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


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
