from extronlib.interface import EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Subscription = {}
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GroupLevel': {'Parameters': ['Group'], 'Status': {}},
            'GroupMute': {'Parameters': ['Group'], 'Status': {}},
            'InputMute': {'Parameters': ['Name'], 'Status': {}},
            'InputSource': {'Parameters': ['Name'], 'Status': {}},
            'MatrixMixerLevel': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixMixerMute': {'Parameters': ['Type', 'Channel'], 'Status': {}},
            'MatrixMixerState': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Name'], 'Status': {}},
            'OutputMute': {'Parameters': ['Name'], 'Status': {}},
            'ParameterRecall': { 'Status': {}},
        }

        self.set_regex = re.compile(b'\x06|\x15(?:01|02|03|99)')
        self.get_regex = re.compile(b'.+\r|\x15(?:01|02|03|99)')
        self.pattern = re.compile('GA.+=(.*);?\r')

    def parse(self, response):
        data = self.pattern.search(response)
        if data:
            return data.group(1).strip().strip(';')
        return response

    def SetGroupLevel(self, value, qualifier):
        group = qualifier['Group']

        if 1 <= int(group) <= 64 and -60 <= value <= 0:
            scaled = int((value + 60) * 2)
            GroupLevelCmdString = 'SG {:x},{:x}\r'.format(int(group), scaled)
            self.__SetHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLevel')

    def UpdateGroupLevel(self, value, qualifier):

        group = qualifier['Group']

        if 1 <= int(group) <= 64:
            GroupLevelCmdString = 'GG {:x}\r'.format(int(group))
            res = self.__UpdateHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
            if res:
                try:
                    res = res.strip(';\r')
                    value = int(res.split(',')[-1], 16)
                    value = float('{:.1f}'.format(value / 2 - 60))
                    self.WriteStatus('GroupLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Group Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGroupLevel')

    def SetGroupMute(self, value, qualifier):

        group = qualifier['Group']

        ValueStateValues = {
            'On':   'M',
            'Off':  'U'
        }

        if 1 <= int(group) <= 64 and value in ValueStateValues:
            GroupMuteCmdString = 'SN {:x},{}\r'.format(int(group), ValueStateValues[value])
            self.__SetHelper('GroupMute', GroupMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMute')

    def UpdateGroupMute(self, value, qualifier):

        group = qualifier['Group']

        ValueStateValues = {
            'M': 'On',
            'U': 'Off'
        }

        if 1 <= int(group) <= 64:
            GroupMuteCmdString = 'GN {:x}\r'.format(int(group))
            res = self.__UpdateHelper('GroupMute', GroupMuteCmdString, value, qualifier)
            if res:
                try:
                    res = res.strip(';\r').split(',')[-1]
                    value = ValueStateValues[res]
                    self.WriteStatus('GroupMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Group Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateGroupMute')

    def SetInputMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            InputMuteCmdString = 'SA"{}">2={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('InputMute', InputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputMute')

    def UpdateInputMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            InputMuteCmdString = 'GA"{}">2\r'.format(name)
            res = self.parse(self.__UpdateHelper('InputMute', InputMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('InputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputMute')

    def SetInputSource(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'Analog':   'F',
            'Digital':  'O'
        }

        if name and value in ValueStateValues:
            InputSourceCmdString = 'SA"{}">3={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInputSource')

    def UpdateInputSource(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'F': 'Analog',
            'O': 'Digital'
        }

        if name:
            InputSourceCmdString = 'GA"{}">3\r'.format(name)
            res = self.parse(self.__UpdateHelper('InputSource', InputSourceCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('InputSource', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Input Source: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateInputSource')

    def SetMatrixMixerLevel(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']
        value = float('{:.1f}'.format(value))
        if 1 <= int(input_) <= 4 and 1 <= int(output) <= 4 and -60.5 <= value <= 0:
            index2 = ((int(input_) - 1) * 4) + int(output)
            MatrixMixerLevelCmdString = 'SA"Matrix 1">2>{}={:.1f}\r'.format(index2, value)
            self.__SetHelper('MatrixMixerLevel', MatrixMixerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerLevel')

    def UpdateMatrixMixerLevel(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        if 1 <= int(input_) <= 4 and 1 <= int(output) <= 4:
            index2 = ((int(input_) - 1) * 4) + int(output)
            MatrixMixerLevelCmdString = 'GA"Matrix 1">2>{}\r'.format(index2)
            res = self.parse(self.__UpdateHelper('MatrixMixerLevel', MatrixMixerLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('MatrixMixerLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Matrix Mixer Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerLevel')

    def SetMatrixMixerMute(self, value, qualifier):

        TypeStates = {
            'Input':    '3',
            'Output':   '4'
        }
        type_ = qualifier['Type']
        channel = qualifier['Channel']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }
        if type_ in TypeStates and 1 <= int(channel) <= 4 and value in ValueStateValues:
            MatrixMixerMuteCmdString = 'SA"Matrix 1">{}>{}={}\r'.format(TypeStates[type_], channel, ValueStateValues[value])
            self.__SetHelper('MatrixMixerMute', MatrixMixerMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerMute')

    def UpdateMatrixMixerMute(self, value, qualifier):

        TypeStates = {
            'Input':    '3',
            'Output':   '4'
        }
        type_ = qualifier['Type']
        channel = qualifier['Channel']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if type_ in TypeStates and 1 <= int(channel) <= 4:
            MatrixMixerMuteCmdString = 'GA"Matrix 1">{}>{}\r'.format(TypeStates[type_], channel)
            res = self.parse(self.__UpdateHelper('MatrixMixerMute', MatrixMixerMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('MatrixMixerMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Matrix Mixer Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerMute')

    def SetMatrixMixerState(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if 1 <= int(input_) <= 4 and 1 <= int(output) <= 4 and value in ValueStateValues:
            index2 = ((int(input_) - 1) * 4) + int(output)
            MatrixMixerStateCmdString = 'SA"Matrix 1">1>{}={}\r'.format(index2, ValueStateValues[value])
            self.__SetHelper('MatrixMixerState', MatrixMixerStateCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixMixerState')

    def UpdateMatrixMixerState(self, value, qualifier):

        input_ = qualifier['Input']
        output = qualifier['Output']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if 1 <= int(input_) <= 4 and 1 <= int(output) <= 4:
            index2 = ((int(input_) - 1) * 4) + int(output)
            MatrixMixerStateCmdString = 'GA"Matrix 1">1>{}\r'.format(index2)
            res = self.parse(self.__UpdateHelper('MatrixMixerState', MatrixMixerStateCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('MatrixMixerState', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Matrix Mixer State: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMatrixMixerState')

    def SetOutputLevel(self, value, qualifier):

        name = qualifier['Name']
        value = float('{:.1f}'.format(value))

        if name and -60.5 <= value <= 0:
            OutputLevelCmdString = 'SA"{}">1={:.1f}\r'.format(name, value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        name = qualifier['Name']

        if name:
            OutputLevelCmdString = 'GA"{}">1\r'.format(name)
            res = self.parse(self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier))
            if res:
                try:
                    value = float('{:.1f}'.format(float(res)))
                    if value == -999:
                        value = -60.5
                    self.WriteStatus('OutputLevel', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Output Level: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputLevel')

    def SetOutputMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'On':   'O',
            'Off':  'F'
        }

        if name and value in ValueStateValues:
            OutputMuteCmdString = 'SA"{}">2={}\r'.format(name, ValueStateValues[value])
            self.__SetHelper('OutputMute', OutputMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOutputMute')

    def UpdateOutputMute(self, value, qualifier):

        name = qualifier['Name']

        ValueStateValues = {
            'O': 'On',
            'F': 'Off'
        }

        if name:
            OutputMuteCmdString = 'GA"{}">2\r'.format(name)
            res = self.parse(self.__UpdateHelper('OutputMute', OutputMuteCmdString, value, qualifier))
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('OutputMute', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Output Mute: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateOutputMute')

    def SetParameterRecall(self, value, qualifier):

        if 1 <= int(value) <= 255:
            ParameterRecallCmdString = 'SS {:x}\r'.format(int(value))
            self.__SetHelper('ParameterRecall', ParameterRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetParameterRecall')

    def UpdateParameterRecall(self, value, qualifier):

        ParameterRecallCmdString = 'GS\r'
        res = self.__UpdateHelper('ParameterRecall', ParameterRecallCmdString, value, qualifier)
        if res:
            try:
                res = res.strip(';\r')
                value = int(res.split()[-1], 16)

                if 0 <= value <= 255:
                    value = str(value)

                    if value == '0':
                        value = 'None'
                    self.WriteStatus('ParameterRecall', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Parameter Recall: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        error_map = {
            '\x1501': 'Invalid Module Name (no match found for module name - or duplicate name)',
            '\x1502': 'Illegal Index (index value or quantity incorrect for specific module)',
            '\x1503': 'Value is out-of-range (value is not permitted for the specified parameter)',
            '\x1599': 'Unknown error'
        }

        if response and response in error_map:
            self.Error(['An error occurred: {}: {}.'.format(sourceCmdName, error_map[response])])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or command in {'GroupLevel', 'GroupMute', 'ParameterRecall'}:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.set_regex)
            if res:
                res = self.__CheckResponseForErrors(command, res.decode())

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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.get_regex)
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
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command + 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
        if Command:
            if command not in self.Subscription:
                self.Subscription[command] = {'method':{}}

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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

    # This method is to check the command with new status have a callback method then trigger the callback
    def NewStatus(self, command, value, qualifier):
        if command in self.Subscription :
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
        Command = self.Commands.get(command, None)
        if Command:
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
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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
