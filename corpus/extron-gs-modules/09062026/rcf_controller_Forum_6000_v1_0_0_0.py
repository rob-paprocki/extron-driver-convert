from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
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
            'ConsoleSpeakerOperation': {'Parameters': ['Line', 'Mic'], 'Status': {}},
            'ConsoleSpeakerVolume': {'Parameters': ['Line', 'Mic'], 'Status': {}},
            'ConsoleState': {'Parameters': ['Line', 'Mic'], 'Status': {}},
            'ConsoleType': {'Parameters': ['Line', 'Mic'], 'Status': {}},
            'DeviceStatus': {'Status': {}},
            'Heartbeat': {'Status': {}},
        }

        self.Regex = re.compile(b'\x02\x02(.*)\x02\x03')
        self.GetStatusConsolePollingList = []

    def AddChecksum(self, Data):

        Low = [
            0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
            0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
            0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
            0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41,
            0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81,
            0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0,
            0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
            0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40,
            0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
            0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
            0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01,
            0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
            0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
            0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0,
            0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01,
            0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81, 0x40, 0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41,
            0x00, 0xC1, 0x81, 0x40, 0x01, 0xC0, 0x80, 0x41, 0x01, 0xC0, 0x80, 0x41, 0x00, 0xC1, 0x81,
            0x40
        ]

        High = [
            0x00, 0xC0, 0xC1, 0x01, 0xC3, 0x03, 0x02, 0xC2, 0xC6, 0x06, 0x07, 0xC7, 0x05, 0xC5, 0xC4,
            0x04, 0xCC, 0x0C, 0x0D, 0xCD, 0x0F, 0xCF, 0xCE, 0x0E, 0x0A, 0xCA, 0xCB, 0x0B, 0xC9, 0x09,
            0x08, 0xC8, 0xD8, 0x18, 0x19, 0xD9, 0x1B, 0xDB, 0xDA, 0x1A, 0x1E, 0xDE, 0xDF, 0x1F, 0xDD,
            0x1D, 0x1C, 0xDC, 0x14, 0xD4, 0xD5, 0x15, 0xD7, 0x17, 0x16, 0xD6, 0xD2, 0x12, 0x13, 0xD3,
            0x11, 0xD1, 0xD0, 0x10, 0xF0, 0x30, 0x31, 0xF1, 0x33, 0xF3, 0xF2, 0x32, 0x36, 0xF6, 0xF7,
            0x37, 0xF5, 0x35, 0x34, 0xF4, 0x3C, 0xFC, 0xFD, 0x3D, 0xFF, 0x3F, 0x3E, 0xFE, 0xFA, 0x3A,
            0x3B, 0xFB, 0x39, 0xF9, 0xF8, 0x38, 0x28, 0xE8, 0xE9, 0x29, 0xEB, 0x2B, 0x2A, 0xEA, 0xEE,
            0x2E, 0x2F, 0xEF, 0x2D, 0xED, 0xEC, 0x2C, 0xE4, 0x24, 0x25, 0xE5, 0x27, 0xE7, 0xE6, 0x26,
            0x22, 0xE2, 0xE3, 0x23, 0xE1, 0x21, 0x20, 0xE0, 0xA0, 0x60, 0x61, 0xA1, 0x63, 0xA3, 0xA2,
            0x62, 0x66, 0xA6, 0xA7, 0x67, 0xA5, 0x65, 0x64, 0xA4, 0x6C, 0xAC, 0xAD, 0x6D, 0xAF, 0x6F,
            0x6E, 0xAE, 0xAA, 0x6A, 0x6B, 0xAB, 0x69, 0xA9, 0xA8, 0x68, 0x78, 0xB8, 0xB9, 0x79, 0xBB,
            0x7B, 0x7A, 0xBA, 0xBE, 0x7E, 0x7F, 0xBF, 0x7D, 0xBD, 0xBC, 0x7C, 0xB4, 0x74, 0x75, 0xB5,
            0x77, 0xB7, 0xB6, 0x76, 0x72, 0xB2, 0xB3, 0x73, 0xB1, 0x71, 0x70, 0xB0, 0x50, 0x90, 0x91,
            0x51, 0x93, 0x53, 0x52, 0x92, 0x96, 0x56, 0x57, 0x97, 0x55, 0x95, 0x94, 0x54, 0x9C, 0x5C,
            0x5D, 0x9D, 0x5F, 0x9F, 0x9E, 0x5E, 0x5A, 0x9A, 0x9B, 0x5B, 0x99, 0x59, 0x58, 0x98, 0x88,
            0x48, 0x49, 0x89, 0x4B, 0x8B, 0x8A, 0x4A, 0x4E, 0x8E, 0x8F, 0x4F, 0x8D, 0x4D, 0x4C, 0x8C,
            0x44, 0x84, 0x85, 0x45, 0x87, 0x47, 0x46, 0x86, 0x82, 0x42, 0x43, 0x83, 0x41, 0x81, 0x80,
            0x40
        ]

        crc = 0xFFFF

        def UpdateCRC16(inchar, crc):
            Index = (crc ^ inchar) & 0x00FF
            Lo = (crc >> 8) ^ (Low[Index])
            Hi = High[Index]
            return Hi << 8 | Lo

        for i in Data:
            crc = UpdateCRC16(i, crc)

        CRCH = int(crc % 256)
        CRCL = int(crc / 256)

        return b'\x02\x02' + bytes(Data) + bytes([CRCH, CRCL]) + b'\x02\x03'

    def UpdateGetStatusConsole(self, value, qualifier):

        CmdStringDict = {
            '0': b'\x02\x02\x01\x01\x21\x00\x48\x48\x02\x03',
            '1': b'\x02\x02\x01\x01\x21\x01\x89\x88\x02\x03',
            '2': b'\x02\x02\x01\x01\x21\x02\xC9\x89\x02\x03',
            '3': b'\x02\x02\x01\x01\x21\x03\x08\x49\x02\x03',
            '4': b'\x02\x02\x01\x01\x21\x04\x49\x8B\x02\x03',
            '5': b'\x02\x02\x01\x01\x21\x05\x88\x4B\x02\x03'
        }

        for Line in self.GetStatusConsolePollingList:

            res = self.__UpdateHelper('ConsoleSpeakerOperation', CmdStringDict[Line], None, None)

            if res:
                res = res[5:-4]
                numConsoles = int(len(res) / 2)
                for i in range(1, numConsoles + 1):
                    qualifier = {'Line': Line, 'Mic': str(i)}
                    Byte0 = format(res[2 * i - 2], '0>8b')
                    Byte1 = format(res[2 * i - 1], '0>8b')
                    try:
                        ConsoleType = {
                            '11': 'Delegate',
                            '10': 'Interpreter',
                            '00': 'President',
                            '01': 'Reserved'
                        }[Byte0[0:2]]

                        self.WriteStatus('ConsoleType', ConsoleType, qualifier)

                    except(KeyError, IndexError):
                        self.Error(['Invalid response for Console Type'])
                    try:
                        ConsoleState = {
                            '000': 'Inactive',
                            '001': 'Active',
                            '010': 'Priority',
                            '011': 'Reset',
                            '100': 'Local Mute'
                        }[Byte0[2:5]]

                        self.WriteStatus('ConsoleState', ConsoleState, qualifier)

                    except(KeyError, IndexError):
                        self.Error(['Invalid response for Console State'])
                    try:
                        ConsoleSpearkerOperation = {
                            '000': 'Inactive',
                            '001': 'Recording',
                            '010': 'Active'
                        }[Byte1[0:3]]

                        self.WriteStatus('ConsoleSpeakerOperation', ConsoleSpearkerOperation, qualifier)

                    except(KeyError, IndexError):
                        self.Error(['Invalid response for Console Operation'])
                    try:
                        Volume = int(Byte1[2:], 2)
                        if 0 <= Volume <= 16:
                            self.WriteStatus('ConsoleSpeakerVolume', Volume, qualifier)

                    except(KeyError, ValueError):
                        self.Error(['Invalid response for Console Volume'])

    def UpdateConsoleSpeakerOperation(self, value, qualifier):

        Line = qualifier['Line']  # '0' to '5'
        if Line not in self.GetStatusConsolePollingList:
            self.GetStatusConsolePollingList.append(Line)

        self.UpdateGetStatusConsole(None, None)

    def SetConsoleSpeakerVolume(self, value, qualifier):

        Data0 = int(qualifier['Mic']) + int(qualifier['Line']) << 5

        Data1 = {
            'Inactive': int('00000000', 2),
            'Active': int('00100000', 2),
            'Priority': int('01000000', 2),
            'Reset': int('01100000', 2),
            'Local Mute': int('10000000', 2)
        }[self.ReadStatus('ConsoleState', qualifier)]

        Data2 = {
            'Inactive': int('00000000', 2),
            'Recording': int('00100000', 2),
            'Active': int('01000000', 2)
        }[self.ReadStatus('ConsoleSpeakerOperation', qualifier)]

        Data3 = int(value)

        Data = [
            0x01,          # Serial
            0x03,          # Length
            0x31,          # Cmd
            Data1,
            Data2,
            Data3,
        ]

        if 0 <= value <= 16:
            self.__SetHelper('ConsoleSpeakerVolume', self.AddChecksum(Data), value, qualifier)
        else:
            self.Discard('Invalid Command for SetConsoleSpeakerVolume')

    def UpdateConsoleSpeakerVolume(self, value, qualifier):

        Line = qualifier['Line']  # '0' to '5'
        if Line not in self.GetStatusConsolePollingList:
            self.GetStatusConsolePollingList.append(Line)

        self.UpdateGetStatusConsole(None, None)

    def SetConsoleState(self, value, qualifier):

        Data0 = int(qualifier['Mic']) + int(qualifier['Line']) << 5

        Data1 = {
            'Inactive': int('00000000', 2),
            'Active': int('00100000', 2),
            'Priority': int('01000000', 2),
            'Reset': int('01100000', 2),
            'Local Mute': int('10000000', 2)
        }[value]

        Data2 = {
            'Inactive': int('00000000', 2),
            'Recording': int('00100000', 2),
            'Active': int('01000000', 2)
        }[self.ReadStatus('ConsoleSpeakerOperation', qualifier)]

        Volume = int(self.ReadStatus('ConsoleSpeakerVolume', qualifier))
        Data3 = Volume

        Data = [
            0x01,          # Serial
            0x03,          # Length
            0x31,          # Cmd
            Data1,
            Data2,
            Data3,
        ]

        if 0 <= Volume <= 16:
            self.__SetHelper('ConsoleState', self.AddChecksum(Data), value, qualifier)
        else:
            self.Discard('Invalid Command for SetConsoleState')

    def UpdateConsoleState(self, value, qualifier):

        Line = qualifier['Line']  # '0' to '5'
        if Line not in self.GetStatusConsolePollingList:
            self.GetStatusConsolePollingList.append(Line)

        self.UpdateGetStatusConsole(None, None)

    def UpdateConsoleType(self, value, qualifier):

        Line = qualifier['Line']  # '0' to '5'
        if Line not in self.GetStatusConsolePollingList:
            self.GetStatusConsolePollingList.append(Line)

        self.UpdateGetStatusConsole(None, None)

    def UpdateDeviceStatus(self, value, qualifier):

        res = self.__UpdateHelper('DeviceStatus', b'\x02\x02\x01\x00\x03\x60\x01\x02\x03', value, qualifier)
        if res:
            try:

                Byte10 = format(res[6], '0>8b') + format(res[5], '0>8b')
                DeviceStatus = {
                    '0000000000000001': 'CHRM Init Error',
                    '0000000000000010': 'DEL Init Error',
                    '0000000000000100': 'Console Error',
                    '0000000000001000': 'Interpreter Error',
                    '0000000000010000': '12V Power Fault',
                    '0000000000100000': '24V Power Fault',
                    '0000000001000000': 'Ext 24V Power Fault',
                    '0000000010000000': 'L1 & L2 Fuse Fault',
                    '0000000100000000': 'L3 & L4 Fuse Fault',
                    '0000001000000000': 'L5 & L6 Fuse Fault',
                    '0000000000000000': 'No Error'
                }[Byte10]

                self.WriteStatus('DeviceStatus', DeviceStatus, qualifier)
            except (KeyError, IndexError):
                self.Error(['Device Status: Invalid/unexpected response'])

    def UpdateHeartbeat(self, value, qualifier):

        self.__UpdateHelper('Heartbeat', b'\x02\x02\x01\x00\x01\xE1\xc0\x02\x03', value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        return response

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.Regex)
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

class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS485', Model=None):
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