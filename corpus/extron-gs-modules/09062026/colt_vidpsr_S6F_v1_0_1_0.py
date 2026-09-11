from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack


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
        self._DeviceID = 0
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Blank': {'Status': {}},
            'Brightness': {'Status': {}},
            'ColorTemperature': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'SwitchInputManually': {'Status': {}},
            'TestPattern': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        try:
            if 0 <= int(value) <= 65535:
                self._DeviceID = pack('>H', int(value))
            else:
                self.Error(['Invalid Device ID Parameter.'])
        except ValueError:
            self.Error(['Device ID Parameter is the wrong type.'])

    def SetBlank(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00',
            'Off': b'\x01'
        }

        if value in ValueStateValues:
            BlankCmdString = b'\x11\x00\x11\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('Blank', BlankCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlank')

    def UpdateBlank(self, value, qualifier):

        BlankStates = {
            0x00: 'On',
            0x01: 'Off'
        }

        FreezeStates = {
            0x01: 'On',
            0x00: 'Off'
        }

        InputStates = {
            0x01: 'DVI',
            0x10: 'HDMI'
        }

        SwitchInputManuallyStates = {
            0x01: 'Enable',
            0x00: 'Disable'
        }

        BlankCmdString = b'\x01\x00\x11\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x01\x00\x16'
        res = self.__UpdateHelper('Blank', BlankCmdString, value, qualifier)
        if res:
            try:
                value = BlankStates[res[231]]
                self.WriteStatus('Blank', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Blank: Invalid/unexpected response'])

            try:
                value = int(unpack('<f', res[23:27])[0] * 100)
                self.WriteStatus('Brightness', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

            try:
                value = int(unpack('<h', res[39:41])[0])
                self.WriteStatus('ColorTemperature', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Color Temperature: Invalid/unexpected response'])

            try:
                value = FreezeStates[res[230]]
                self.WriteStatus('Freeze', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Freeze: Invalid/unexpected response'])

            try:
                value = InputStates[res[88]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

            try:
                value = int(unpack('<i', res[19:23])[0]) & 0x01  # bit 0
                value = SwitchInputManuallyStates[value]
                self.WriteStatus('SwitchInputManually', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Switch Input Manually: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            valueFloat = value / 100
            BrightnessCmdString = b'\x21\x00\x14\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + pack('<f', valueFloat)
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetColorTemperature(self, value, qualifier):

        if 2000 <= value <= 10000:
            ColorTemperatureCmdString = b'\x22\x00\x12\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + pack('<h', value)
            self.__SetHelper('ColorTemperature', ColorTemperatureCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetColorTemperature')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        if value in ValueStateValues:
            FreezeCmdString = b'\x12\x00\x11\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DVI': b'\x01',
            'HDMI': b'\x10'
        }

        if value in ValueStateValues:
            InputCmdString = b'\x33\x00\x12\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetSwitchInputManually(self, value, qualifier):

        ValueStateValues = {
            'Enable': b'\x01',
            'Disable': b'\x00'
        }

        if value in ValueStateValues:
            SwitchInputManuallyCmdString = b'\x8B\x00\x11\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('SwitchInputManually', SwitchInputManuallyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSwitchInputManually')

    def SetTestPattern(self, value, qualifier):

        ValueStateValues = {
            'Normal': 0,
            'Red': 1,
            'Green': 2,
            'Blue': 3,
            'White': 4,
            'Vertical Line': 5,
            'Horizontal Line': 6,
            'Left Diagonal': 7,
            'Right Diagonal': 9,
            'Gradient of Red': 10,
            'Gradient of Green': 11,
            'Gradient of Blue': 12,
            'Gradient of White': 13,
            'Black': 14
        }

        if value in ValueStateValues:
            TestPatternCmdString = b'\x32\x00\x17\x00\x00\x00' + self._DeviceID + b'\xFF\x00\x00\x00\x00\x00\x00\x00' + pack('b', ValueStateValues[value]) + b'\x00\x00\x00\x00\x00\x00'
            self.__SetHelper('TestPattern', TestPatternCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.Unidirectional == 'True' or self._DeviceID == b'\xFF\xFF':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            if self.initializationChk:
                self.OnConnected()
                self.initializationChk = False

            self.counter = self.counter + 1
            if self.counter > self.connectionCounter and self.connectionFlag:
                self.OnDisconnected()

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=260)
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
            raise KeyError('Invalid command for SubscribeStatus ' + command)

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
            except BaseException:
                return None
        else:
            raise KeyError('Invalid command for ReadStatus: ' + command)


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

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])
