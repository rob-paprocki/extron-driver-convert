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
            'AutoConfig': {'Parameters': ['Device ID'], 'Status': {}},
            'ButtonLock': {'Parameters': ['Device ID'], 'Status': {}},
            'DeviceStatus': {'Parameters': ['Device ID'], 'Status': {}},
            'Input': {'Parameters': ['Device ID'], 'Status': {}},
            'Position': {'Parameters': ['Device ID'], 'Status': {}},
            'Power': {'Parameters': ['Device ID'], 'Status': {}},
        }

    def GetHeader(self, ID):
        if ID == 'Broadcast':
            return b'\xFA\xF9'
        elif 1 <= int(ID) <= 30:
            return b'\xFA' + bytes([int(ID)])
        else:
            self.Error(['Invalid Device ID qualifier'])
            return ''

    def SetAutoConfig(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        if Header:
            self.__SetHelper('AutoConfig', Header + b'\x05\x00\x00', value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoConfig')

    def SetButtonLock(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        Value = {
            'On': b'\x04\x01\x00',
            'Off': b'\x04\x00\x00'
        }[value]

        if Header:
            self.__SetHelper('ButtonLock', Header + Value, value, qualifier)
        else:
            self.Discard('Invalid Command for SetButtonLock')

    def SetInput(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        Value = {
            'DVI A': b'\x03\x01\x00',
            'DVI 1': b'\x03\x00\x00',
            'DVI 2': b'\x03\x03\x00',
        }[value]

        if Header:
            self.__SetHelper('Input', Header + Value, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPosition(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        Value = {
            'Up': b'\x01\x01\x00',
            'Down': b'\x01\x00\x00'
        }[value]

        if Header:
            self.__SetHelper('Position', Header + Value, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPosition')

    def SetPower(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        Value = {
            'On': b'\x02\x01\x00',
            'Off': b'\x02\x00\x00'
        }[value]

        if Header:
            self.__SetHelper('Power', Header + Value, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def UpdatePower(self, value, qualifier):

        Header = self.GetHeader(qualifier['Device ID'])

        if Header:
            res = self.__UpdateHelper('Power', Header + b'\x14\x00\x00', value, qualifier)
            if res:

                try:
                    if res[3] & (1 << 0):
                        self.WriteStatus('DeviceStatus', 'System Failure', qualifier)
                    else:
                        self.WriteStatus('DeviceStatus', 'Normal', qualifier)
                except IndexError:
                    self.Error(['Invalid Response for Device Status'])

                try:
                    if res[3] & (1 << 1):
                        self.WriteStatus('Power', 'On', qualifier)
                    else:
                        self.WriteStatus('Power', 'Off', qualifier)
                except IndexError:
                    self.Error(['Invalid Response for Power'])

                try:
                    if res[3] & (1 << 5):
                        self.WriteStatus('Position', 'Down', qualifier)
                    else:
                        self.WriteStatus('Position', 'Up', qualifier)
                except IndexError:
                    self.Error(['Invalid Response for Position'])

                try:
                    if res[3] & (1 << 6):
                        self.WriteStatus('Input', 'DVI 1', qualifier)
                    elif res[3] & (1 << 7):
                        self.WriteStatus('Input', 'DVI 2', qualifier)
                    else:
                        self.WriteStatus('Input', 'DVI A', qualifier)
                except IndexError:
                    self.Error(['Invalid Response for Input'])

                try:
                    if res[4] & (1 << 5):
                        self.WriteStatus('ButtonLock', 'On', qualifier)
                    else:
                        self.WriteStatus('ButtonLock', 'Off', qualifier)
                except IndexError:
                    self.Error(['Invalid Response for Button Lock'])

        else:
            self.Discard('Invalid Command for UpdatePower')

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdatePosition(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateButtonLock(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=5)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or qualifier['Device ID'] == 'Broadcast':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=5)
            if not res:
                return ''
            else:
                return res

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS422', Model=None):
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
