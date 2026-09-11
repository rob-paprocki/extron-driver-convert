from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack
from struct import unpack


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
        self._SourceAddress = b'\x80\x80\x80'
        self._SrcDstNodeType = [255]

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'GroupMotorControl': {'Parameters': ['Group Address'], 'Status': {}},
            'Lock': {'Parameters': ['Destination Address'], 'Status': {}},
            'MotorControl': {'Parameters': ['Destination Address'], 'Status': {}},
            'MotorPosition': {'Parameters': ['Destination Address'], 'Status': {}},
        }

    @property
    def SourceAddress(self):
        return self._SourceAddress

    @SourceAddress.setter
    def SourceAddress(self, value):
        if len(value.encode(encoding='iso-8859-1')) == 3:
            self._SourceAddress = value.encode(encoding='iso-8859-1')
        else:
            self.Error(['Source Address value should be a length of 3 bytes.'])

    @property
    def SrcDstNodeType(self):
        return self._SrcDstNodeType

    @SrcDstNodeType.setter
    def SrcDstNodeType(self, value):
        if len(value.encode(encoding='iso-8859-1')) == 1:
            node = value.encode(encoding='iso-8859-1')
            self._SrcDstNodeType = [0x00]
            self._SrcDstNodeType[0] = 255 - node[0]
        else:
            self.Error(['Src/Dst Node Type should be a length of 1 byte.'])

    def chkSum(self, cmdBytes):
        total = 0
        for x in cmdBytes:
            total = total + x
        return total.to_bytes(2, 'big')

    def SetGroupMotorControl(self, value, qualifier):

        group = qualifier['Group Address']
        if len(group.encode(encoding='iso-8859-1')) == 3:
            group = group.encode(encoding='iso-8859-1')
            GroupAddr = [0x00, 0x00, 0x00]
            GroupAddr[0] = group[2]
            GroupAddr[1] = group[1]
            GroupAddr[2] = group[0]

            ValueStateValues = {
                'Up': [0xFC, 0xF0, self._SrcDstNodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFE, 0xFF, 0xFF, 0xFF],
                'Down': [0xFC, 0xF0, self._SrcDstNodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF],
                'Stop': [0xFD, 0xF3, self._SrcDstNodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFF]
            }

            byteString = ValueStateValues[value]
            MotorControlCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                MotorControlCmdString += pack('>B', val)
            MotorControlCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('GroupMotorControl', MotorControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupMotorControl')

    def UpdateMotorPosition(self, value, qualifier):

        destination = qualifier['Destination Address']
        if len(destination.encode(encoding='iso-8859-1')) == 3:
            destination = destination.encode(encoding='iso-8859-1')
            DestAddr = [0x00, 0x00, 0x00]
            DestAddr[0] = 255 - destination[2]
            DestAddr[1] = 255 - destination[1]
            DestAddr[2] = 255 - destination[0]

            sum = self.chkSum([0xF3, 0xF4, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2]])
            MotorPositionCmdString = pack('>BBBBBBBBBBB', 0xF3, 0xF4, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], sum[0], sum[1])
            res = self.__UpdateHelper('MotorPosition', MotorPositionCmdString, value, qualifier)
            if res:
                try:
                    value = pack('>BB', res[10], res[9])
                    value = 65535 - unpack('>H', value)[0]
                    self.WriteStatus('MotorPosition', value, qualifier)
                except (KeyError, IndexError):
                    self.Error(['Invalid/unexpected response'])
        else:
            self.Discard('Invalid Command for UpdateMotorPosition')

    def SetLock(self, value, qualifier):

        destination = qualifier['Destination Address']
        if len(destination.encode(encoding='iso-8859-1')) == 3:
            destination = destination.encode(encoding='iso-8859-1')
            DestAddr = [0x00, 0x00, 0x00]
            DestAddr[0] = 255 - destination[2]
            DestAddr[1] = 255 - destination[1]
            DestAddr[2] = 255 - destination[0]

            ValueStateValues = {
                'Lock Up': [0xA4, 0xF1, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFE, 0xFF, 0xFE],
                'Lock Down': [0xA4, 0xF1, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFD, 0xFF, 0xFE],
                'Lock Position': [0xA4, 0xF1, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF, 0xFF, 0xFE],
                'Unlock': [0xA4, 0xF1, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFA, 0xFF, 0xFE]
            }

            byteString = ValueStateValues[value]
            LockCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                LockCmdString += pack('>B', val)
            LockCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('Lock', LockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLock')

    def SetMotorControl(self, value, qualifier):

        destination = qualifier['Destination Address']
        if len(destination.encode(encoding='iso-8859-1')) == 3:
            destination = destination.encode(encoding='iso-8859-1')
            DestAddr = [0x00, 0x00, 0x00]
            DestAddr[0] = 255 - destination[2]
            DestAddr[1] = 255 - destination[1]
            DestAddr[2] = 255 - destination[0]

            ValueStateValues = {
                'Up': [0xFC, 0xF0, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFE, 0xFF, 0xFF, 0xFF],
                'Down': [0xFC, 0xF0, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF, 0xFF, 0xFF, 0xFF],
                'Stop': [0xFD, 0xF3, self._SrcDstNodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF]
            }

            byteString = ValueStateValues[value]
            MotorControlCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                MotorControlCmdString += pack('>B', val)
            MotorControlCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('MotorControl', MotorControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotorControl')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\r')
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        if self.initializationChk:
            self.OnConnected()
            self.initializationChk = False

        self.counter = self.counter + 1
        if self.counter > self.connectionCounter and self.connectionFlag:
            self.OnDisconnected()

        if self.Unidirectional == 'True':
            self.Discard('Inappropriate Command ' + command)
            return ''
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliLen=16)
            if not res:
                return ''
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

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
