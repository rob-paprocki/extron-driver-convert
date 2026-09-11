from extronlib.interface import SerialInterface, EthernetClientInterface
from re import compile, search


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
            'DimmerLevel': {'Parameters': ['Group Number', 'Ramp Rate'], 'Status': {}},
            'DimmerLevelStatus': {'Parameters': ['Group Number'], 'Status': {}},
            'PresetScene': {'Status': {}},
            'Relay': {'Parameters': ['Group Number'], 'Status': {}},
        }

        self.DimmerLevel_rex = compile(b'100|[1-9][0-9]|\d')
        self.PresetScene_rex = compile(b'1[0-6]|\d')
        self.Relay_rex = compile(b'on|off')

    def SetDimmerLevel(self, value, qualifier):

        groupNum = int(qualifier['Group Number'])
        rampRate = qualifier['Ramp Rate']
        if value in range(101) and groupNum in range(1, 17) and rampRate in range(43201):
            DimmerLevelCmdString = 'set,group,{},level,{},ramp,{}\r\n'.format(groupNum, value, rampRate)
            self.__SetHelper('DimmerLevel', DimmerLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmerLevel')

    def UpdateDimmerLevelStatus(self, value, qualifier):

        groupNum = int(qualifier['Group Number'])
        if groupNum in range(1, 17):
            DimmerLevelStatusCmdString = 'get,group,{},level\r\n'.format(groupNum)
            res = self.__UpdateHelper('DimmerLevelStatus', DimmerLevelStatusCmdString, value, qualifier)
            if res:
                try:
                    value = int(res)
                    self.WriteStatus('DimmerLevelStatus', value, qualifier)
                except (ValueError, IndexError):
                    self.Error(['Dimmer Level Status: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateDimmerLevelStatus')

    def SetPresetScene(self, value, qualifier):

        if int(value) in range(1, 17):
            PresetSceneCmdString = 'set,preset,{}\r\n'.format(value)
            self.__SetHelper('PresetScene', PresetSceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetScene')

    def UpdatePresetScene(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12',
            '13': '13',
            '14': '14',
            '15': '15',
            '16': '16',
            '0': 'No Active Preset'
        }

        PresetSceneCmdString = 'get,preset\r\n'
        res = self.__UpdateHelper('PresetScene', PresetSceneCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res]
                self.WriteStatus('PresetScene', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Preset Scene: Invalid/unexpected response'])

    def SetRelay(self, value, qualifier):

        ValueStateValues = {
            'On': 'on',
            'Off': 'off'
        }

        groupNum = int(qualifier['Group Number'])
        if groupNum in range(1, 17):
            RelayCmdString = 'set,group,{},state,{}\r\n'.format(groupNum, ValueStateValues[value])
            self.__SetHelper('Relay', RelayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelay')

    def UpdateRelay(self, value, qualifier):

        ValueStateValues = {
            'on': 'On',
            'off': 'Off'
        }

        groupNum = int(qualifier['Group Number'])
        if groupNum in range(1, 17):
            RelayCmdString = 'get,group,{},state\r\n'.format(groupNum)
            res = self.__UpdateHelper('Relay', RelayCmdString, value, qualifier)
            if res:
                try:
                    value = ValueStateValues[res]
                    self.WriteStatus('Relay', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Relay: Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateRelay')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        regex_dict = {
            "DimmerLevelStatus": self.DimmerLevel_rex,
            "PresetScene": self.PresetScene_rex,
            "Relay": self.Relay_rex
        }
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
                
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=regex_dict[command])
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
            raise AttributeError(command, 'does not support Set.')

    # Send Update Commands
    def Update(self, command, qualifier=None):
        method = getattr(self, 'Update%s' % command, None)
        if method is not None and callable(method):
            method(None, qualifier)
        else:
            raise AttributeError(command, 'does not support Update.')

    # This method is to tie an specific command with a parameter to a call back method
    # when its value is updated. It sets how often the command will be query, if the command
    # have the update method.
    # If the command doesn't have the update feature then that command is only used for feedback
    def SubscribeStatus(self, command, qualifier, callback):
        Command = self.Commands.get(command, None)
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
            raise KeyError('Invalid command for SubscribeStatus ', command)

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
            raise KeyError('Invalid command for ReadStatus: ', command)


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
