from extronlib.interface import SerialInterface, EthernetClientInterface
import re

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
        self.Models = {
            'MIMO88': self.eclr_15_831_88,
            'MIMO1616': self.eclr_15_831_1616,
            'MIMO1212SG': self.eclr_15_831_1212,
            'MIMO88SG': self.eclr_15_831_88,
        }

        self.Commands = {
            'Connect': {'Status': {}},
            'ConnectionStatus': {'Status': {}},
            'CrosspointLevel': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'CrosspointMute': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'GeneralPurposeInput': {'Parameters': ['Input'], 'Status': {}},
            'GeneralPurposeOutput': {'Parameters': ['Output'], 'Status': {}},
            'InputLevel': {'Parameters': ['Input'], 'Status': {}},
            'Mute': {'Parameters': ['Type', 'Number'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'Preset': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AddMatchString(re.compile(b'DATA XLEVEL (\d{1,2}) (\d{1,2}) (\d{1,3})'), self.__MatchCrosspointLevel, None)
            self.AddMatchString(re.compile(b'DATA XMUTE (\d{1,2}) (\d{1,2}) (YES|NO)'), self.__MatchCrosspointMute, None)
            self.AddMatchString(re.compile(b'DATA GPI (\d{1,2}) (\d{1,3})'), self.__MatchGeneralPurposeInput, None)
            self.AddMatchString(re.compile(b'DATA GPO (\d{1,2}) (1|0)'), self.__MatchGeneralPurposeOutput, None)
            self.AddMatchString(re.compile(b'DATA ILEVEL (\d{1,2}) (\d{1,3})'), self.__MatchInputLevel, None)
            self.AddMatchString(re.compile(b'DATA (I|O)MUTE (\d{1,2}) (YES|NO)'), self.__MatchMute, None)
            self.AddMatchString(re.compile(b'DATA OLEVEL (\d{1,2}) (\d{1,3})'), self.__MatchOutputLevel, None)
            self.AddMatchString(re.compile(b'DATA PRESET (\d{1,3})'), self.__MatchPreset, None)
            self.AddMatchString(re.compile(b'ERROR (\d{1,2})'), self.__MatchError, None)

    def SetConnect(self, value, qualifier):

        self.Send('SYSTEM CONNECT\n')

    def SetCrosspointLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        inputVal = int(qualifier['Input'])
        output = int(qualifier['Output'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']) and (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            CrosspointLevelCmdString = 'SET XLEVEL {0} {1} {2}\n'.format(inputVal, output, value)
            self.__SetHelper('CrosspointLevel', CrosspointLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointLevel')

    def UpdateCrosspointLevel(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        output = int(qualifier['Output'])
        if (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']) and (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            CrosspointLevelCmdString = 'GET XLEVEL {0} {1}\n'.format(inputVal, output)
            self.__UpdateHelper('CrosspointLevel', CrosspointLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateCrosspointLevel')

    def __MatchCrosspointLevel(self, match, tag):

        if (self.InputConstraints['Min'] <= int(match.group(1).decode()) <= self.InputConstraints['Max']) \
                and (self.OutputConstraints['Min'] <= int(match.group(2).decode()) <= self.OutputConstraints['Max']) \
                and (0 <= int(match.group(3).decode()) <= 100):
            self.WriteStatus('CrosspointLevel', int(match.group(3).decode()), {'Input': match.group(1).decode(), 'Output': match.group(2).decode()})

    def SetCrosspointMute(self, value, qualifier):

        ValueStateValues = {
            'On': 'YES',
            'Off': 'NO'
        }

        inputVal = int(qualifier['Input'])
        output = int(qualifier['Output'])
        if (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']) and (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            CrosspointMuteCmdString = 'SET XMUTE {0} {1} {2}\n'.format(inputVal, output, ValueStateValues[value])
            self.__SetHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetCrosspointMute')

    def UpdateCrosspointMute(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        output = int(qualifier['Output'])
        if (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']) and (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            CrosspointMuteCmdString = 'GET XMUTE {0} {1}\n'.format(inputVal, output)
            self.__UpdateHelper('CrosspointMute', CrosspointMuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateCrosspointMute')

    def __MatchCrosspointMute(self, match, tag):

        ValueStateValues = {
            'YES': 'On',
            'NO': 'Off'
        }
        if (self.InputConstraints['Min'] <= int(match.group(1).decode()) <= self.InputConstraints['Max']) \
                and (self.OutputConstraints['Min'] <= int(match.group(2).decode()) <= self.OutputConstraints['Max']):
            self.WriteStatus('CrosspointMute', ValueStateValues[match.group(3).decode()], {'Input': match.group(1).decode(), 'Output': match.group(2).decode()})

    def UpdateGeneralPurposeInput(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']):
            GeneralPurposeInputCmdString = 'GET GPI {0}\n'.format(inputVal)
            self.__UpdateHelper('GeneralPurposeInput', GeneralPurposeInputCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateGeneralPurposeInput')

    def __MatchGeneralPurposeInput(self, match, tag):

        if (self.InputConstraints['Min'] <= int(match.group(1).decode()) <= self.InputConstraints['Max']) and (0 <= int(match.group(2).decode()) <= 100):
            self.WriteStatus('GeneralPurposeInput', int(match.group(2).decode()), {'Input': match.group(1).decode()})

    def SetGeneralPurposeOutput(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        output = int(qualifier['Output'])
        if (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            GeneralPurposeOutputCmdString = 'SET GPO {0} {1}\n'.format(output, ValueStateValues[value])
            self.__SetHelper('GeneralPurposeOutput', GeneralPurposeOutputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetGeneralPurposeOutput')

    def UpdateGeneralPurposeOutput(self, value, qualifier):

        output = int(qualifier['Output'])
        if (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            GeneralPurposeOutputCmdString = 'GET GPO {0}\n'.format(output)
            self.__UpdateHelper('GeneralPurposeOutput', GeneralPurposeOutputCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateGeneralPurposeOutput')

    def __MatchGeneralPurposeOutput(self, match, tag):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        if (self.OutputConstraints['Min'] <= int(match.group(1).decode()) <= self.OutputConstraints['Max']):
            self.WriteStatus('GeneralPurposeOutput', ValueStateValues[match.group(2).decode()], {'Output': match.group(1).decode()})

    def SetInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        inputVal = int(qualifier['Input'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']):
            InputLevelCmdString = 'SET ILEVEL {0} {1}\n'.format(inputVal, value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        inputVal = int(qualifier['Input'])
        if (self.InputConstraints['Min'] <= inputVal <= self.InputConstraints['Max']):
            InputLevelCmdString = 'GET ILEVEL {0}\n'.format(inputVal)
            self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateInputLevel')

    def __MatchInputLevel(self, match, tag):

        if (self.InputConstraints['Min'] <= int(match.group(1).decode()) <= self.InputConstraints['Max']) and 0 <= int(match.group(2).decode()) <= 100:
            self.WriteStatus('InputLevel', int(match.group(2).decode()), {'Input': match.group(1).decode()})

    def SetMute(self, value, qualifier):

        TypeStates = {
            'Input': 'I',
            'Output': 'O'
        }

        ValueStateValues = {
            'On': 'YES',
            'Off': 'NO'
        }

        typeVal = qualifier['Type']
        number = int(qualifier['Number'])
        if (typeVal in TypeStates) and (self.InputConstraints['Min'] <= number <= self.InputConstraints['Max']):
            MuteCmdString = 'SET {0}MUTE {1} {2}\n'.format(TypeStates[typeVal], number, ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMute')

    def UpdateMute(self, value, qualifier):

        TypeStates = {
            'Input': 'I',
            'Output': 'O'
        }

        typeVal = qualifier['Type']
        number = int(qualifier['Number'])
        if (typeVal in TypeStates) and (self.InputConstraints['Min'] <= number <= self.InputConstraints['Max']):
            MuteCmdString = 'GET {0}MUTE {1}\n'.format(TypeStates[typeVal], number)
            self.__UpdateHelper('Mute', MuteCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateMute')

    def __MatchMute(self, match, tag):

        TypeStates = {
            'I': 'Input',
            'O': 'Output'
        }

        ValueStateValues = {
            'YES': 'On',
            'NO': 'Off'
        }

        if (self.InputConstraints['Min'] <= int(match.group(2).decode()) <= self.InputConstraints['Max']):
            self.WriteStatus('Mute', ValueStateValues[match.group(3).decode()], {'Type': TypeStates[match.group(1).decode()], 'Number': match.group(2).decode()})

    def SetOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        output = int(qualifier['Output'])
        if (ValueConstraints['Min'] <= value <= ValueConstraints['Max']) and (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            OutputLevelCmdString = 'SET OLEVEL {0} {1}\n'.format(output, value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        output = int(qualifier['Output'])
        if (self.OutputConstraints['Min'] <= output <= self.OutputConstraints['Max']):
            OutputLevelCmdString = 'GET OLEVEL {0}\n'.format(output)
            self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for UpdateOutputLevel')

    def __MatchOutputLevel(self, match, tag):

        if (self.OutputConstraints['Min'] <= int(match.group(1).decode()) <= self.OutputConstraints['Max'])\
                and (0 <= int(match.group(2).decode()) <= 100):
            self.WriteStatus('OutputLevel', int(match.group(2).decode()), {'Output': match.group(1).decode()})

    def SetPreset(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            PresetCmdString = 'SET PRESET {0}\n'.format(value)
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPreset')

    def UpdatePreset(self, value, qualifier):

        PresetCmdString = 'GET PRESET\n'
        self.__UpdateHelper('Preset', PresetCmdString, value, qualifier)

    def __MatchPreset(self, match, tag):

        if 0 <= int(match.group(1).decode()) <= 100:
            self.WriteStatus('Preset', match.group(1).decode(), None)

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

            self.Send(commandstring)

    def __MatchError(self, match, tag):

        ERROR_CODES = {
                       '0': 'No Error',
                       '1': 'Invalid Field TYPE',
                       '2': 'Invalid Field PARAM1',
                       '3': 'Invalid Field PARAM2',
                       '4': 'Invalid Field PARAM3',
                       '5': 'Invalid Field PARAM4',
                       '6': 'Timeout waiting for PONG',
                       '7': 'CONNECT received while connected',
                       '8': 'DICONNECT received while unconnected',
                       '9': 'Invalid client IP (client IP different from CONNECT message)',
                       '10': 'Message too long (More than 80 characters',
                       '11': 'Unsupported Preset Number',
                       '12': 'Unsupported Message',
                       '13': 'Unsupported Input Channel Number',
                       '14': 'Unsupported Output Channel Number',
                       '15': 'Unsupported GPI number',
                       '16': 'Unsupported GPO number',
                       '17': 'Invalid Level Value',
                       '18': 'Invalid Rate Value',
                       '19': 'Invalid GPO Value',
            }
        value = ERROR_CODES[match.group(1).decode()]
        print(value)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetConnect(None, None)

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

    def eclr_15_831_88(self):

        self.InputConstraints = {
            'Min': 1,
            'Max': 8
        }
        self.OutputConstraints = {
            'Min': 1,
            'Max': 8
        }

    def eclr_15_831_1212(self):

        self.InputConstraints = {
            'Min': 1,
            'Max': 12
        }
        self.OutputConstraints = {
            'Min': 1,
            'Max': 12
        }

    def eclr_15_831_1616(self):

        self.InputConstraints = {
            'Min': 1,
            'Max': 16
        }
        self.OutputConstraints = {
            'Min': 1,
            'Max': 16
        }

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
                result = re.search(regexString, self._ReceiveBuffer)
                if result:
                    self._compile_list[regexString]['callback'](result, self._compile_list[regexString]['para'])
                    self._ReceiveBuffer = self._ReceiveBuffer.replace(result.group(0), b'')
                else:
                    break
        return True


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
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
