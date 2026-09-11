from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack

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

        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoConfigVGA': {'Status': {}},
            'ButtonLock': {'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'ScreenControl': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 249
        elif 1 <= int(value) <= 30:
            self._DeviceID = int(value)

    def SetAutoConfigVGA(self, value, qualifier):

        AutoConfigVGACmdString = pack('>5B', 0xFA, self._DeviceID, 0x05, 0x00, 0x00)
        self.__SetHelper('AutoConfigVGA', AutoConfigVGACmdString, value, qualifier)

    def SetButtonLock(self, value, qualifier):

        ButtonLockState = {
            'On': 0x01,
            'Off': 0x00
        }

        ButtonLockCmdString = pack('>5B', 0xFA, self._DeviceID, 0x04, ButtonLockState[value], 0x00)
        self.__SetHelper('ButtonLock', ButtonLockCmdString, value, qualifier)

    def UpdateButtonLock(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def UpdateDeviceStatus(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': 0x01,
            'DVI': 0x00
        }

        InputCmdString = pack('>5B', 0xFA, self._DeviceID, 0x03, InputState[value], 0x00)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):
        self.UpdatePower(value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('>5B', 0xFA, self._DeviceID, 0x02, PowerState[value], 0x00)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        PowerState = {
            4: 'On',
            0: 'Off'
        }

        ButtonLockState = {
            8: 'On',
            0: 'Off'
        }

        DeviceStatusState = {
            128: 'System Failure',
            0: 'Normal'
        }

        InputState = {
            16: 'VGA',
            0: 'DVI'
        }

        PowerCmdString = pack('>5B', 0xFA, self._DeviceID, 0x14, 0x00, 0x00)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                PowerValue = PowerState[res[3] & 0x04]
                self.WriteStatus('Power', PowerValue, qualifier)
            except (KeyError, IndexError):
                print('Power: Invalid/Unexpected Response for UpdatePower')

            try:
                ButtonLockValue = ButtonLockState[res[3] & 0x08]
                self.WriteStatus('ButtonLock', ButtonLockValue, qualifier)
            except (KeyError, IndexError):
                print('Button Lock: Invalid/Unexpected Response')

            try:
                StatusValue = DeviceStatusState[res[3] & 0x80]
                self.WriteStatus('DeviceStatus', StatusValue, qualifier)
            except (KeyError, IndexError):
                print('Device Status: Invalid/Unexpected Response')

            try:
                InputValue = InputState[res[3] & 0x10]
                self.WriteStatus('Input', InputValue, qualifier)
            except (KeyError, IndexError):
                print('Input: Invalid/Unexpected Response')

    def SetScreenControl(self, value, qualifier):

        ScreenControlState = {
            'Up': 0x01,
            'Down': 0x00
        }

        ScreenControlCmdString = pack('>5B', 0xFA, self._DeviceID, 0x01, ScreenControlState[value], 0x00)
        self.__SetHelper('ScreenControl', ScreenControlCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=5)
            if not res:
                print('Invalid/Unexpected Response')
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == 249:
            print('Inappropriate Command ', command)
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
                return b''
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
                    except BaseException:                        break
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
