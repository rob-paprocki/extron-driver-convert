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
            'InputLevel': {'Parameters': ['Input'], 'Status': {}},
            'MasterLevel': {'Status': {}},
            'MuteInput': {'Parameters': ['Input'], 'Status': {}},
            'MuteMaster': {'Status': {}},
            'MuteOutput': {'Parameters': ['Output'], 'Status': {}},
            'OutputLevel': {'Parameters': ['Output'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
        }


    def SetInputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -110,
            'Max': 24
        }
        input_ = int(qualifier['Input'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= input_ <= 8:
            InputLevelCmdString = 'SG {0} {1}\r'.format(input_ + 1, value)
            self.__SetHelper('InputLevel', InputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetInputLevel')

    def UpdateInputLevel(self, value, qualifier):

        input_ = int(qualifier['Input'])
        if 1 <= input_ <= 8:
            InputLevelCmdString = 'GG {0}\r'.format(input_ + 1)
            res = self.__UpdateHelper('InputLevel', InputLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[0:-1])
                    if value & 0x1:
                        if (value - 1) > -110:
                            value = value - 1
                        else:
                            value = -110
                    self.WriteStatus('InputLevel', value, qualifier)
                except (IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateInputLevel')

    def SetMasterLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -110,
            'Max': 24
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            MasterLevelCmdString = 'SG 1 {0}\r'.format(value)
            self.__SetHelper('MasterLevel', MasterLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMasterLevel')

    def UpdateMasterLevel(self, value, qualifier):

        MasterLevelCmdString = 'GG 1\r'
        res = self.__UpdateHelper('MasterLevel', MasterLevelCmdString, value, qualifier)
        if res:
            try:
                value = int(res[0:-1])
                if value & 0x1:
                    if (value - 1) > -110:
                        value = value - 1
                    else:
                        value = -110
                self.WriteStatus('MasterLevel', value, qualifier)
            except (IndexError, ValueError):
                print('Invalid/unexpected response for UpdateMasterLevel')

    def SetMuteInput(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        input_ = int(qualifier['Input'])
        if 1 <= input_ <= 8:
            MuteInputCmdString = 'SM {0} {1}\r'.format(input_ + 1, ValueStateValues[value])
            self.__SetHelper('MuteInput', MuteInputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMuteInput')

    def UpdateMuteInput(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        input_ = int(qualifier['Input'])
        if 1 <= input_ <= 8:
            MuteInputCmdString = 'GM {0}\r'.format(input_ + 1)
            res = self.__UpdateHelper('MuteInput', MuteInputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('MuteInput', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateMuteInput')
        else:
            print('Invalid Command for UpdateMuteInput')

    def SetMuteMaster(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }

        MuteMasterCmdString = 'SM 1 {0}\r'.format(ValueStateValues[value])
        self.__SetHelper('MuteMaster', MuteMasterCmdString, value, qualifier)

    def UpdateMuteMaster(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }

        MuteMasterCmdString = 'GM 1\r'
        res = self.__UpdateHelper('MuteMaster', MuteMasterCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[0]]
                self.WriteStatus('MuteMaster', value, qualifier)
            except (KeyError, IndexError):
                print('Invalid/unexpected response for UpdateMuteMaster')

    def SetMuteOutput(self, value, qualifier):

        ValueStateValues = {
            'On': '1',
            'Off': '0'
        }
        output = int(qualifier['Output'])
        if 1 <= output <= 8:
            MuteOutputCmdString = 'SM {0} {1}\r'.format(output + 9, ValueStateValues[value])
            self.__SetHelper('MuteOutput', MuteOutputCmdString, value, qualifier)
        else:
            print('Invalid Command for SetMuteOutput')

    def UpdateMuteOutput(self, value, qualifier):

        ValueStateValues = {
            '1': 'On',
            '0': 'Off'
        }
        output = int(qualifier['Output'])
        if 1 <= output <= 8:
            MuteOutputCmdString = 'GM {0}\r'.format(output + 1)
            res = self.__UpdateHelper('MuteOutput', MuteOutputCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res[0]]
                    self.WriteStatus('MuteOutput', value, qualifier)
                except (KeyError, IndexError):
                    print('Invalid/unexpected response for UpdateMuteOutput')
        else:
            print('Invalid Command for UpdateMuteOutput')

    def SetOutputLevel(self, value, qualifier):

        ValueConstraints = {
            'Min': -98,
            'Max': 24
        }
        output = int(qualifier['Output'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= output <= 8:
            OutputLevelCmdString = 'SG {0} {1}\r'.format(output + 9, value)
            self.__SetHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetOutputLevel')

    def UpdateOutputLevel(self, value, qualifier):

        output = int(qualifier['Output'])
        if 1 <= output <= 8:
            OutputLevelCmdString = 'GG {0}\r'.format(output + 9)
            res = self.__UpdateHelper('OutputLevel', OutputLevelCmdString, value, qualifier)
            if res:
                try:
                    value = int(res[0:-1])
                    if value & 0x1:
                        if (value - 1) > -98:
                            value = value - 1
                        else:
                            value = -98
                    self.WriteStatus('OutputLevel', value, qualifier)
                except (KeyError, IndexError, ValueError):
                    print('Invalid/unexpected response for UpdateOutputLevel')
        else:
            print('Invalid Command for UpdateOutputLevel')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = 'GP {0}\r'.format(value)
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = 'SP {0}\r'.format(value)
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response == 'ERR\n':
            print('An error occurred')
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n').decode()
            if not res:
                print('No Response')
            else:
                res = self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):        
            
        if self.Unidirectional == 'True':
            print('Inappropriate Command ', command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='\n').decode()
            if res:
                return self.__CheckResponseForErrors(command + ':' + commandstring.strip(), res)

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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=30304, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()
