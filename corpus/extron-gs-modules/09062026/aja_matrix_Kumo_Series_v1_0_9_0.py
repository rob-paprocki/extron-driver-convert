from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


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
        self.Models = {
            'Kumo 1616': self.aja_15_1403_1616,
            'Kumo 3232': self.aja_15_1403_3232,
            'Kumo 1604': self.aja_15_1403_1604,
            'Kumo 6464': self.aja_15_1403_6464,
            'Kumo 1616-12G': self.aja_15_1403_1616,
            'Kumo 3232-12G': self.aja_15_1403_3232,
            'Kumo 6464-12G': self.aja_15_1403_6464,
        }

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'InputTieStatus': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'MatrixTieCommand': {'Parameters': ['Input', 'Output'], 'Status': {}},
            'ModelName': {'Status': {}},
            'OutputTieStatus': {'Parameters': ['Output'], 'Status': {}},
            'TakeSalvo': {'Parameters': ['Salvo Name'], 'Status': {}},
        }

        self.OutputStatus = {'Tied': []}
        self.InputArray = []
        self.OutputArray = []

        self.InitMatrix = False

    def CalCRC(self, Data):
        return '{0:02X}'.format(256 - (Data % 256)).encode()

    def SetInitialMatrix(self):
        self.OutputStatus['Tied'] = [('0') for i in range(self.OutputSize)]

    def __SetMatrixStatus(self, output, newInput, tag):

        oldInput = self.OutputStatus[tag][int(output) - 1]

        if oldInput != newInput:  # only process this if there is a new tie
            self.WriteStatus('OutputTieStatus', newInput, {'Output': output})  # setting input to output
            self.WriteStatus('InputTieStatus', 'Untied', {'Input': oldInput, 'Output': output})
            self.WriteStatus('InputTieStatus', 'Tied', {'Input': newInput, 'Output': output})  # setting the new input tie status

            if newInput not in self.InputArray:
                self.InputArray.append(newInput)
            if output not in self.OutputArray:
                self.OutputArray.append(output)

            self.OutputStatus[tag][int(output) - 1] = newInput

    def UpdateInputTieStatus(self, value, qualifier):

        outputValue = qualifier['Output']
        inputValue = qualifier['Input']

        if 1 <= int(outputValue) <= self.OutputSize and 1 <= int(inputValue) <= self.InputSize:
            self.UpdateOutputTieStatus(value, {'Output': outputValue})
        else:
            self.Discard('Invalid Command for UpdateInputTieStatus')

    def SetMatrixTieCommand(self, value, qualifier):

        inputValue = qualifier['Input']
        outputValue = qualifier['Output']

        if 1 <= int(inputValue) <= self.InputSize and 1 <= int(outputValue) <= self.OutputSize:

            inputValue = hex(int(inputValue))[2:].zfill(4)
            outputValue = hex(int(outputValue))[2:].zfill(4)

            buffer = [
                0x4E, 0x30, 0x54, 0x49,
                0x09, ord(outputValue[0]), ord(outputValue[1]), ord(outputValue[2]), ord(outputValue[3]),
                0x09, ord(inputValue[0]), ord(inputValue[1]), ord(inputValue[2]), ord(inputValue[3]),
            ]

            CmdString = b'\x01' + bytes(buffer) + self.CalCRC(sum(buffer)) + b'\x04'

            self.__SetHelper('MatrixTieCommand', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

    def UpdateOutputTieStatus(self, value, qualifier):

        out = qualifier['Output']

        if 1 <= int(out) <= self.OutputSize:
            output = '{0:02X}'.format(int(out))
            buffer = pack('>5B', 0x4E, 0x30, 0x51, 0x49, 0x09)
            checksum = self.CalCRC(289 + 0x09 + 0x30 + 0x30 + int(ord(output[0])) + int(ord(output[1])))
            OutputTieStatusCmdString = b'\x01' + buffer + pack('>B', int(ord(output[0]))) + pack('>B', int(ord(output[1]))) + b'\x0900' + checksum + b'\x04'
            res = self.__UpdateHelper('OutputTieStatus', OutputTieStatusCmdString, value, qualifier)
            if res:
                try:
                    if not self.InitMatrix:
                        self.InitMatrix = True
                        for y in range(1, self.OutputSize + 1):
                            self.WriteStatus('OutputTieStatus', '0', {'Output': str(y)})
                            for z in range(1, self.InputSize + 1):
                                self.WriteStatus('InputTieStatus', 'Untied', {'Input': str(z), 'Output': str(y)})

                    self.__SetMatrixStatus(str(int(res[6:10], 16)), str(int(res[20:24], 16)), 'Tied')
                except (KeyError, IndexError, ValueError):
                    self.Error(['Invalid/Unexpected Response'])
        else:
            self.Discard('Invalid Command for UpdateOutputTieStatus')

    def UpdateModelName(self, value, qualifier):

        ValueStateValues = {
            b'1604': 'Kumo 1604',
            b'1616': 'Kumo 1616',
            b'3232': 'Kumo 3232',
            b'6464': 'Kumo 6464'
        }

        ModelNameCmdString = b'\x01\x4E\x30\x42\x4B\x09\x4E\x39\x45\x04'
        res = self.__UpdateHelper('ModelName', ModelNameCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[12:16]]
                self.WriteStatus('ModelName', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Invalid/Unexpected Response'])

    def SetTakeSalvo(self, value, qualifier):

        if qualifier['Salvo Name']:
            buffer = [0x4E, 0x30, 0x54, 0x53, 0x09]
            for index in qualifier['Salvo Name']:
                buffer.append(ord(index))
            TakeSalvoCmdString = b'\x01' + bytes(buffer) + self.CalCRC(sum(buffer)) + b'\x04'
            self.__SetHelper('TakeSalvo', TakeSalvoCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTakeSalvo')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x04')
            if not res:
                self.Error(['Invalid/Unexpected Response'])
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
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x04')
            if not res:
                return ''
            else:
                return self.__CheckResponseForErrors(command, res)


    def OnConnected(self):
        self.connectionFlag = True
        self.WriteStatus('ConnectionStatus', 'Connected')
        self.counter = 0

        self.SetInitialMatrix()

    def OnDisconnected(self):
        self.WriteStatus('ConnectionStatus', 'Disconnected')
        self.connectionFlag = False

        self.InitMatrix = False


    def aja_15_1403_1604(self):

        self.InputSize = 16
        self.OutputSize = 4

    def aja_15_1403_1616(self):

        self.InputSize = 16
        self.OutputSize = 16

    def aja_15_1403_3232(self):

        self.InputSize = 32
        self.OutputSize = 32

    def aja_15_1403_6464(self):

        self.InputSize = 64
        self.OutputSize = 64

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='HW', CharDelay=0, Mode='RS232', Model=None):
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
