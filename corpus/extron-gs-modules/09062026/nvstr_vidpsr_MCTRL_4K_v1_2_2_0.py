from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from functools import reduce
from operator import add
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
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoBrightness': {'Status': {}},
            'Blackout': {'Status': {}},
            'Brightness': {'Status': {}},
            'Input': {'Status': {}},
            'LightSensorStatus': {'Status': {}},
            'RelayControl': {'Parameters': ['RJ45 Port', 'Relay'], 'Status': {}},
            'TemperatureStatus': {'Parameters': ['RJ45 Port', 'Board Address'], 'Status': {}},
            'TestPattern': {'Status': {}},
        }

        self.SetRegex = re.compile(b'\xAA\x55[\x00-\x04]')
        self.AutoBrightnessRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x01\x00[\x7D-\xFF][\x00-\xFF]{2}')
        self.BlackoutRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x01\x00[\x00-\xFF][\x00-\xFF]{2}')
        self.BrightnessRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x01\x00\x00\x00\x00\x00\x01\x00\x00\x02\x01\x00[\x00-\xFF][\x00-\xFF]{2}')
        self.InputRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x00\x00\x00\x00\x00\x00\x23\x00\x00\x02\x01\x00[\x01\x05\x58\x5A\x5F\x61][\x00-\xFF]{2}')
        self.LightSensorRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x02\x00\x00\x00\x00\x00\x00\x00\x00\x06\x05\x00\x01\x02[\x00-\xFF]{5}')
        self.RelayControlRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x02\x00\x00\x00\x00\x00\x10\x00\x00\x05\x08\x00[\x00-\x01]{8}[\x00-\xFF]{2}')
        self.TemperatureRegex = re.compile(b'\xAA\x55\x00[\x00-\xFF]\x00\xFE\x01\x00[\x00-\xFF]{3}\x00\x00\x00\x00\x0A\x02\x00\x80[\x00-\xFF][\x00-\xFF]{2}')

    @staticmethod
    def calc_checkout(input_list):
        chk = reduce(add, input_list[2:]) + 0x5555
        checkout = [(chk & 0xFF), (chk & 0xFF00) >> 8]

        return checkout

    def SetAutoBrightness(self, value, qualifier):

        States = {
            'Enable': b'\x55\xAA\x00\x5B\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x0A\x01\x00\x7D\x37\x57',
            'Disable': b'\x55\xAA\x00\x5B\xFE\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x0A\x01\x00\xFF\xB9\x57',
        }

        if value in States:
            self.__SetHelper('AutoBrightness', States[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoBrightness')

    def UpdateAutoBrightness(self, value, qualifier):

        States = {
            0x7D: 'Enable',
            0xFF: 'Disable',
        }

        CmdString = b'\x55\xAA\x00\x5B\xFE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x01\x00\xB9\x56'
        res = self.__UpdateHelper('AutoBrightness', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('AutoBrightness', States[res[-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Brightness: Invalid/unexpected response'])

    def SetBlackout(self, value, qualifier):

        States = {
            'Enable': b'\x55\xAA\x00\x00\xFE\xFF\x01\xFF\xFF\xFF\x01\x00\x00\x01\x00\x02\x01\x00\xFF\x54\x5B',
            'Disable': b'\x55\xAA\x00\x00\xFE\xFF\x01\xFF\xFF\xFF\x01\x00\x00\x01\x00\x02\x01\x00\x00\x55\x5A',
        }

        if value in States:
            self.__SetHelper('Blackout', States[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetBlackout')

    def UpdateBlackout(self, value, qualifier):

        States = {
            0xFF: 'Enable',
            0x00: 'Disable',
        }

        CmdString = b'\x55\xAA\x00\x00\xFE\x00\x01\x00\x00\x00\x00\x00\x00\x01\x00\x02\x01\x00\x58\x56'
        res = self.__UpdateHelper('Blackout', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Blackout', States[res[-3]], qualifier)
            except (KeyError, IndexError):
                self.Error(['Blackout: Invalid/unexpected response'])

    def SetBrightness(self, value, qualifier):

        cmd = [
            0x55, 0xAA,                         # Head
            0x00,                               # ACK
            0x00,                               # Serial
            0xFE,                               # Source
            0x00,                               # Destination
            0x01,                               # Card Type
            0xFF,                               # Port
            0xFF, 0xFF,                         # Board Address
            0x01,                               # WR
            0x00,                               # Reserved
            0x01, 0x00, 0x00, 0x02,             # Register Address
            0x01, 0x00,                         # Data len
            value                               # Data
        ]                                       # + Checksum appended separately

        cmd = cmd + self.calc_checkout(cmd)
        CmdString = pack('B' * len(cmd), *cmd)

        if 0 <= value <= 255:
            self.__SetHelper('Brightness', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def UpdateBrightness(self, value, qualifier):

        cmd = [
            0x55, 0xAA,                         # Head
            0x00,                               # ACK
            0x00,                               # Serial
            0xFE,                               # Source
            0x00,                               # Destination
            0x01,                               # Card Type
            0x00,                               # Port
            0x00, 0x00,                         # Board Address
            0x00,                               # WR
            0x00,                               # Reserved
            0x01, 0x00, 0x00, 0x02,             # Register Address
            0x01, 0x00,                         # Data len
        ]                                       # + Checksum appended separately

        cmd = cmd + self.calc_checkout(cmd)
        CmdString = pack('B' * len(cmd), *cmd)

        res = self.__UpdateHelper('Brightness', CmdString, value, qualifier)
        if res:
            try:
                self.WriteStatus('Brightness', res[-3], qualifier)
            except (ValueError, IndexError):
                self.Error(['Brightness: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        States = {
            'DVI': 0x58,
            'Dual DVI': 0x61,
            'HDMI': 0x05,
            '3G-SDI': 0x01,
            'DisplayPort': 0x5F,
            'HDMI 1.4': 0x5A,
        }

        if value in States:
            cmd = [
                0x55, 0xAA,                         # Head
                0x00,                               # ACK
                0x00,                               # Serial
                0xFE,                               # Source
                0xFF,                               # Destination
                0x00,                               # Card Type
                0x00,                               # Port
                0x00, 0x00,                         # Board Address
                0x01,                               # WR
                0x00,                               # Reserved
                0x23, 0x00, 0x00, 0x02,             # Register Address
                0x01, 0x00,                         # Data len
                States[value]                       # Data
            ]                                       # + Checksum appended separately
            cmd = cmd + self.calc_checkout(cmd)
            InputCmdString = pack('B' * len(cmd), *cmd)

            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def UpdateInput(self, value, qualifier):

        cmd = [
            0x55, 0xAA,                         # Head
            0x00,                               # ACK
            0x00,                               # Serial
            0xFE,                               # Source
            0x00,                               # Destination
            0x00,                               # Card Type
            0x00,                               # Port
            0x00, 0x00,                         # Board Address
            0x00,                               # WR
            0x00,                               # Reserved
            0x23, 0x00, 0x00, 0x02,             # Register Address
            0x01, 0x00,                         # Data len
        ]                                       # + Checksum appended separately

        cmd = cmd + self.calc_checkout(cmd)
        InputCmdString = pack('B' * len(cmd), *cmd)

        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                ValueStateValues = {
                    0x58: 'DVI',
                    0x61: 'Dual DVI',
                    0x05: 'HDMI',
                    0x01: '3G-SDI',
                    0x5F: 'DisplayPort',
                    0x5A: 'HDMI 1.4',
                }

                value = ValueStateValues[res[-3]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def UpdateLightSensorStatus(self, value, qualifier):

        DataRefreshCommand = b'\x55\xAA\x00\x15\xFE\x00\x02\x00\x00\x00\x01\x00\x00\x00\x00\x06\x0B\x00\x00\x00\x00\x00\x55\xAA\x01\x02\x80\xFF\x81\x7E\x59'
        RequestCommand = b'\x55\xAA\x00\x15\xFE\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x06\x05\x00\x75\x56'
        res = self.__UpdateHelper('LightSensorStatus', DataRefreshCommand + RequestCommand, value, qualifier)

        if res:
            try:
                value = res[-4] + 256 * res[-5]

                if res[-5] >> 7:
                    value = (value - 0x8000) * 2
                    self.WriteStatus('LightSensorStatus', value, qualifier)
                else:
                    self.Error(['Light Sensor Status: Invalid sensor data'])

            except (ValueError, IndexError):
                self.Error(['Light Sensor Status: Invalid/unexpected response'])

    def SetRelayControl(self, value, qualifier):

        Data = {
            'On': 0x00,
            'Off': 0x01,
        }

        RelayOffset = {
            '1': 0x10,
            '2': 0x11,
            '3': 0x12,
            '4': 0x13,
            '5': 0x14,
            '6': 0x15,
            '7': 0x16,
            '8': 0x17,
        }

        RJ45_Port = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            '5': 0x04,
            '6': 0x05,
            '7': 0x06,
            '8': 0x07,
        }

        if value in Data and qualifier['RJ45 Port'] in RJ45_Port and qualifier['Relay'] in RelayOffset:
            cmd = [
                0x55, 0xAA,                         # Head
                0x00,                               # ACK
                0x00,                               # Serial
                0xFE,                               # Source
                0x00,                               # Destination
                0x02,                               # Card Type
                RJ45_Port[qualifier['RJ45 Port']],  # Port
                0x00, 0x00,                         # Board Address
                0x01,                               # WR
                0x00,                               # Reserved
                RelayOffset[qualifier['Relay']],    # Register Address
                0x00, 0x00, 0x05,                   # Register Address
                0x01, 0x00,                         # Data len
                Data[value]                         # Data
            ]                                       # + Checksum appended separately

            cmd = cmd + self.calc_checkout(cmd)
            CmdString = pack('B' * len(cmd), *cmd)

            self.__SetHelper('RelayControl', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRelayControl')

    def UpdateRelayControl(self, value, qualifier):

        States = {
            0: 'On',
            1: 'Off',
        }

        Port = qualifier['RJ45 Port']

        RJ45_Port = {
            '1': 0x00,
            '2': 0x01,
            '3': 0x02,
            '4': 0x03,
            '5': 0x04,
            '6': 0x05,
            '7': 0x06,
            '8': 0x07,
        }

        if Port in RJ45_Port and 1 <= int(qualifier['Relay']) <= 8:
            cmd = [
                0x55, 0xAA,                         # Head
                0x00,                               # ACK
                0x00,                               # Serial
                0xFE,                               # Source
                0x00,                               # Destination
                0x02,                               # Card Type
                RJ45_Port[Port],                    # Port
                0x00, 0x00,                         # Board Address
                0x00,                               # WR
                0x00,                               # Reserved
                0x10, 0x00, 0x00, 0x05,             # Register Address
                0x08, 0x00,                         # Data len
            ]                                       # + Checksum appended separately

            cmd = cmd + self.calc_checkout(cmd)
            CmdString = pack('B' * len(cmd), *cmd)

            res = self.__UpdateHelper('RelayControl', CmdString, value, qualifier)
            if res:
                try:
                    self.WriteStatus('RelayControl', States[res[-10]], {'Relay': '1', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-9]], {'Relay': '2', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-8]], {'Relay': '3', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-7]], {'Relay': '4', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-6]], {'Relay': '5', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-5]], {'Relay': '6', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-4]], {'Relay': '7', 'RJ45 Port': Port})
                    self.WriteStatus('RelayControl', States[res[-3]], {'Relay': '8', 'RJ45 Port': Port})
                except (KeyError, IndexError):
                    self.Error(['Relay Control: Invalid/unexpected response'])

        else:
            self.Discard('Invalid Command for UpdateRelayControl')

    def UpdateTemperatureStatus(self, value, qualifier):

        Port = int(qualifier['RJ45 Port']) - 1
        Addr = int(qualifier['Board Address']) - 1

        cmd = [
            0x55, 0xAA,                         # Head
            0x00,                               # ACK
            0x00,                               # Serial
            0xFE,                               # Source
            0x00,                               # Destination
            0x01,                               # Card Type
            Port,                               # Port
            Addr, 0x00,                         # Board Address
            0x00,                               # WR
            0x00,                               # Reserved
            0x00, 0x00, 0x00, 0x0A,             # Register Address
            0x02, 0x00,                         # Data len
        ]                                       # + Checksum appended separately

        cmd = cmd + self.calc_checkout(cmd)
        CmdString = pack('B' * len(cmd), *cmd)

        res = self.__UpdateHelper('TemperatureStatus', CmdString, value, qualifier)
        if res:
            try:
                value = int(res[-3] / 2)
                self.WriteStatus('TemperatureStatus', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Temperature Status: Invalid/unexpected response'])

    def SetTestPattern(self, value, qualifier):

        States = {
            'Red': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x02\xD9\x59',
            'Green': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x03\xDA\x59',
            'Blue': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x04\xDB\x59',
            'White': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x05\xDC\x59',
            'Horizontal': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x06\xDD\x59',
            'Vertical': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x07\xDE\x59',
            'Incline': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x08\xDF\x59',
            'Grayscale': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x09\xE0\x59',
            'Aging': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x0A\xE1\x59',
            'Normal Video': b'\x55\xAA\x00\x80\xFE\x00\x01\xFF\xFF\xFF\x01\x00\x01\x01\x00\x02\x01\x00\x00\xD7\x59',
        }

        if value in States:
            self.__SetHelper('TestPattern', States[value], value, qualifier)
        else:
            self.Discard('Invalid Command for SetTestPattern')

    def __CheckResponseForErrors(self, sourceCmdName, response):

        Errors = {
            0x01: 'Command failed due to timeout',
            0x02: 'Command failed due to check error on request data package',
            0x03: 'Command failed due to check error on acknowledge data package',
            0x04: 'Command failed due to invalid command',
        }

        if response[-1] in Errors:
            ErrorMessage = '{}: {}'.format(sourceCmdName, Errors[response[2]])
            self.Error([ErrorMessage])
            response = ''

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.SetRegex)
            if not res:
                self.Error(['{}: Invalid/unexpected response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

    def __UpdateHelper(self, command, commandstring, value, qualifier):

        Regex = {
            'AutoBrightness': self.AutoBrightnessRegex,
            'Blackout': self.BlackoutRegex,
            'Brightness': self.BrightnessRegex,
            'Input': self.InputRegex,
            'LightSensorStatus': self.LightSensorRegex,
            'RelayControl': self.RelayControlRegex,
            'TemperatureStatus': self.TemperatureRegex,
        }[command]

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=Regex)
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