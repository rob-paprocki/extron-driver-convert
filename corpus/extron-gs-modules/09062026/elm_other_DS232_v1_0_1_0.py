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
            'Clear': {'Status': {}},
            'Dimmer': {'Parameters': ['Level'], 'Status': {}},
            'SceneRecall': {'Status': {}},
            'SceneSave': {'Status': {}},
        }

    def SetClear(self, value, qualifier):

        ClearCmdString = 'CG\r\n'
        self.__SetHelper('Clear', ClearCmdString, value, qualifier)

    def SetDimmer(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 512
        }

        level = qualifier['Level']

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            DimmerCmdString = 'D{0}@{1}G\r\n'.format(level, value)
            self.__SetHelper('Dimmer', DimmerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDimmer')

    def UpdateDimmer(self, value, qualifier):

        CmdString = b'M=B\r\n'
        res = self.__UpdateHelper('Dimmer', CmdString, value, qualifier)
        if res:
            try:
                level = 1
                for value in res[:-1]:
                    self.WriteStatus('Dimmer', value, {'Level': level})
                    level += 1
            except (ValueError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetSceneRecall(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            SceneRecallCmdString = 'S{0}G\r\n'.format(value)
            self.__SetHelper('SceneRecall', SceneRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneRecall')

    def SetSceneSave(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 100
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            SceneSaveCmdString = 'S{0}VG\r\n'.format(value)
            self.__SetHelper('SceneSave', SceneSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneSave')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            0x01: 'String Error',
            0x02: 'RS232 Port Error: Parity error',
            0x04: 'RS232 Port Error: Unexpected data error',
            0x08: 'RS232 Port Error: Overrun error, excessive data was received and could not process',
            0x10: 'RS232 Port Error: An error has occurred on the RS232 port since last power, reset, or clear',
            0x20: 'DMX Port Error: An error has occurred on the DMX port since last power or reset',
            0x40: 'Last Scene Read or Save Error',
            0x80: 'Scene Save Error has occurred'
        }

        if response[-1] in DEVICE_ERROR_CODES:
            errorstring = sourceCmdName + ' Error: ' + DEVICE_ERROR_CODES[response[-1]]
            self.Error([errorstring])
        elif response[-1] != 0x00:
            errorstring = sourceCmdName + ' Multiple Errors'
            self.Error([errorstring])

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=513)
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)

    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.Send('M=L\r\n')

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
