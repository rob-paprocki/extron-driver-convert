from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from functools import reduce
from operator import xor


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
        self._MonitorID = b'\x01'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoAdjustVGA': {'Status': {}},
            'AutoSignalDetect': {'Status': {}},
            'InputSource': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureFormat': {'Status': {}},
            'Power': {'Status': {}},
            'UserInputControl': {'Parameters': ['Device'], 'Status': {}},
            'Volume': {'Status': {}},
        }

        self.ErrorRegex = re.compile(b''.join([b'\x21', self.MonitorID,
                                               b'\x00\x00\x04\x01\x00([\x00\x03\x04])[\x00-\xFF]']))
        self.UpdateRex = {
            'AutoSignalDetect': b''.join([b'\x21', self.MonitorID,
                                          b'\x00\x00\x04\x01\xAF(\x00|\x01)[\x00-\xFF]']),
            'InputSource': b''.join([b'\x21', self.MonitorID,
                                     b'\x00\x00\x05\x01\xAD\xFD([\x06\x08\x09\x0A\x0B\x0D\x0F])[\x00-\xFF]']),
            'PictureFormat': b''.join([b'\x21', self.MonitorID,
                                       b'\x00\x00\x04\x01\x3B([\x00\x01\x02\x03\x04\x05])[\x00-\xFF]']),
            'Power': b''.join([b'\x21', self.MonitorID,
                               b'\x00\x00\x04\x01\x19(\x01|\x02)[\x00-\xFF]']),
            'UserInputControl': b''.join([b'\x21', self.MonitorID,
                                          b'\x00\x00\x04\x01\x1D([\x00\x01\x02\x03])[\x00-\xFF]']),
            'Volume': b''.join([b'\x21', self.MonitorID,
                                b'\x00\x00\x04\x01\x45([\x00-\x3E])[\x00-\xFF]']),
        }
        self.UpdateRegex = {k: re.compile(v) for k, v in self.UpdateRex.items()}

    @property
    def MonitorID(self):
        return self._MonitorID

    @MonitorID.setter
    def MonitorID(self, value):
        if 1 <= int(value) <= 255:
            self._MonitorID = int(value).to_bytes(1, 'big')
        else:
            self.Error('MonitorID should be a value between 1 and 255.')

    def SetAutoAdjustVGA(self, value, qualifier):

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x05\x01\x70\x40\x00'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        AutoAdjustVGACmdString = b''.join([body, crc])
        self.__SetHelper('AutoAdjustVGA', AutoAdjustVGACmdString, value, qualifier)

    def SetAutoSignalDetect(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\xAF', ValueStateValues[value]])
        crc = reduce(xor, body).to_bytes(1, 'big')
        AutoSignalDetectCmdString = b''.join([body, crc])
        self.__SetHelper('AutoSignalDetect', AutoSignalDetectCmdString, value, qualifier)

    def UpdateAutoSignalDetect(self, value, qualifier):

        ValueStateValues = {
            1: 'On',
            0: 'Off'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\xAF'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        AutoSignalDetectCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('AutoSignalDetect', AutoSignalDetectCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('AutoSignalDetect', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Auto Signal Detect: Invalid/unexpected response'])

    def SetInputSource(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\x05\x00',
            'DVI-D': b'\x09\x01',
            'HDMI 1': b'\x09\x00',
            'HDMI 2': b'\x05\x01',
            'DisplayPort': b'\x07\x01',
            'Component': b'\x03\x00'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x07\x01\xAC', ValueStateValues[value], b'\x01\x00'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        InputSourceCmdString = b''.join([body, crc])
        self.__SetHelper('InputSource', InputSourceCmdString, value, qualifier)

    def UpdateInputSource(self, value, qualifier):

        ValueStateValues = {
            0x08: 'VGA',
            0x0B: 'DVI-D',
            0x0A: 'HDMI 1',
            0x09: 'HDMI 2',
            0x0D: 'DisplayPort',
            0x06: 'Component',
            0x0F: 'USB'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\xAD'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        InputSourceCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('InputSource', InputSourceCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[8]]
                self.WriteStatus('InputSource', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input Source: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\xDB', int(value).to_bytes(1, 'big')])
        crc = reduce(xor, body).to_bytes(1, 'big')
        KeypadCmdString = b''.join([body, crc])
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xA1',
            'Up': b'\xA6',
            'Down': b'\xA7',
            'Left': b'\xA8',
            'Right': b'\xA9',
            'OK': b'\xB1',
            'Return': b'\xB2'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\xDB', ValueStateValues[value]])
        crc = reduce(xor, body).to_bytes(1, 'big')
        MenuNavigationCmdString = b''.join([body, crc])
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureFormat(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x00',
            'Custom': b'\x01',
            'Unscaled': b'\x02',
            'Wide Screen': b'\x03',
            '16:9': b'\x04',
            'Auto': b'\x05'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x3A', ValueStateValues[value]])
        crc = reduce(xor, body).to_bytes(1, 'big')
        PictureFormatCmdString = b''.join([body, crc])
        self.__SetHelper('PictureFormat', PictureFormatCmdString, value, qualifier)

    def UpdatePictureFormat(self, value, qualifier):

        ValueStateValues = {
            0: '4:3',
            1: 'Custom',
            2: 'Unscaled',
            3: 'Wide Screen',
            4: '16:9',
            5: 'Auto'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x3B'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        PictureFormatCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('PictureFormat', PictureFormatCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('PictureFormat', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Picture Format: Invalid/unexpected response'])

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x01'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x18', ValueStateValues[value]])
        crc = reduce(xor, body).to_bytes(1, 'big')
        PowerCmdString = b''.join([body, crc])
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x19'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        PowerCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[7]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetUserInputControl(self, value, qualifier):

        ValueStateValues = {
            'Locked': 0,
            'Unlocked': 1
        }

        device = qualifier['Device']
        if device == 'Local Keyboard':
            UserInputControl = self.ReadStatus('UserInputControl', {'Device': 'Remote Control'})
            if UserInputControl:
                UserInputControl = ValueStateValues[UserInputControl] | ValueStateValues[value] << 1
            else:
                self.Discard('Invalid Command for SetUserInputControl')
                return
        elif device == 'Remote Control':
            UserInputControl = self.ReadStatus('UserInputControl', {'Device': 'Local Keyboard'})
            if UserInputControl:
                UserInputControl = ValueStateValues[UserInputControl] << 1 | ValueStateValues[value]
            else:
                self.Discard('Invalid Command for SetUserInputControl')
                return
        else:
            self.Discard('Invalid Command for SetUserInputControl')
            return

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x1C', bytes([UserInputControl])])
        crc = reduce(xor, body).to_bytes(1, 'big')
        UserInputControlCmdString = b''.join([body, crc])
        self.__SetHelper('UserInputControl', UserInputControlCmdString, value, qualifier)

    def UpdateUserInputControl(self, value, qualifier):

        ValueStateValues = {
            0: 'Locked',
            1: 'Unlocked'
        }

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x1D'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        UserInputControlCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('UserInputControl', UserInputControlCmdString, value, qualifier)
        if res:
            try:
                value = res[7]
                self.WriteStatus('UserInputControl', ValueStateValues[value >> 1], {'Device': 'Local Keyboard'})
                self.WriteStatus('UserInputControl', ValueStateValues[value & 1], {'Device': 'Remote Control'})
            except (KeyError, IndexError):
                self.Error(['User Input Control: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 60
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x04\x01\x44', bytes([value])])
            crc = reduce(xor, body).to_bytes(1, 'big')
            VolumeCmdString = b''.join([body, crc])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        body = b''.join([b'\xA6', self.MonitorID, b'\x00\x00\x00\x03\x01\x45'])
        crc = reduce(xor, body).to_bytes(1, 'big')
        VolumeCmdString = b''.join([body, crc])
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = res[7]
                self.WriteStatus('Volume', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {b'\x00\x03': "Error: Command Not Acknowledged.",
                              b'\x00\x04': "Error: Command Not Available Or Checksum Error."}
        if len(response) > 7:
            if response[6:8] in DEVICE_ERROR_CODES:
                self.Error([DEVICE_ERROR_CODES[response[6:8]]])
                response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.ErrorRegex)
            if not res:
                self.Error(['Invalid/unexpected response'  + command])
            else:
                res = self.__CheckResponseForErrors(command, res)

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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.UpdateRegex[command])
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
