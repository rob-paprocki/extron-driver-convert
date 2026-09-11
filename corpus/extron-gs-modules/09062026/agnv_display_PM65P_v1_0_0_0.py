from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack, unpack
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
        self._DeviceID = 1
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

        if self.Unidirectional == 'False':
            self.AspectRatioRegex = re.compile(b'(\x21[\x00-\xFE]\x00\x00\x04\x01\x3B([\x00-\x05])[\x00-\xFF])|(\x21[\x00-\xFE]\x00\x00\x04\x01\x00[\x03\x04][\x00-\xFF])')
            self.ExecutiveModeRegex = re.compile(b'(\x21[\x00-\xFE]\x00\x00\x04\x01\x1D([\x00-\x03])[\x00-\xFF])|(\x21[\x00-\xFE]\x00\x00\x04\x01\x00[\x03\x04][\x00-\xFF])')
            self.InputRegex = re.compile(b'(\x21[\x00-\xFE]\x00\x00\x05\x01\xAD[\x01-\x03\xFD\xFE]([\x01\x02\x06\x08\x09\x0A\x0B\x0D\x0E\x0F\x10\xFF])[\x00-\xFF])|(\x21[\x00-\xFE]\x00\x00\x04\x01\x00[\x03\x04][\x00-\xFF])')
            self.PowerRegex = re.compile(b'(\x21[\x00-\xFE]\x00\x00\x04\x01\x19([\x01\x02])[\x00-\xFF])|(\x21[\x00-\xFE]\x00\x00\x04\x01\x00[\x03\x04][\x00-\xFF])')
            self.VolumeRegex = re.compile(b'(\x21[\x00-\xFE]\x00\x00\x04\x01\x45([\x00-\x3C])[\x00-\xFF])|(\x21[\x00-\xFE]\x00\x00\x04\x01\x00[\x03\x04][\x00-\xFF])')

            self.updateRegex = {
                'AspectRatio': self.AspectRatioRegex,
                'ExecutiveMode': self.ExecutiveModeRegex,
                'Input': self.InputRegex,
                'Power': self.PowerRegex,
                'Volume': self.VolumeRegex
            }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0
        else:
            if 1 <= int(value) <= 255:
                self._DeviceID = int(value)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': 0,
            'Custom': 1,
            'Unscaled': 2,
            'Wide Screen': 3,
            'Movie Expand 16:9': 4,
            'Auto': 5
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x3A ^ ValueStateValues[value]
        AspectRatioCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x3A,
                                    ValueStateValues[value], checksum)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def UpdateAspectRatio(self, value, qualifier):

        ValueStateValues = {
            0: '4:3',
            1: 'Custom',
            2: 'Unscaled',
            3: 'Wide Screen',
            4: 'Movie Expand 16:9',
            5: 'Auto'
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x3B
        AspectRatioCmdString = pack('9B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x3B, checksum)
        res = self.__UpdateHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('AspectRatio', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Aspect Ratio: Invalid/unexpected response'])

    def SetAutoImage(self, value, qualifier):

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x05 ^ 0x01 ^ 0x70 ^ 0x40 ^ 0x00
        AutoImageCmdString = pack('11B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x05, 0x01, 0x70, 0x40, 0x00, checksum)
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Local Keyboard': 1,
            'Remote Control': 2,
            'Local Keyboard & Remote Control': 0,
            'Off': 3
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x1C ^ ValueStateValues[value]
        ExecutiveModeCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x1C, ValueStateValues[value], checksum)
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def UpdateExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            1: 'Local Keyboard',
            2: 'Remote Control',
            0: 'Local Keyboard & Remote Control',
            3: 'Off'
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x1D
        ExecutiveModeCmdString = pack('9B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x1D, checksum)
        res = self.__UpdateHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('ExecutiveMode', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Executive Mode: Invalid/unexpected response'])

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Video': [0x01, 0x00],
            'Component': [0x03, 0x00],
            'VGA': [0x05, 0x00],
            'HDMI 1': [0x09, 0x00],
            'HDMI 2': [0x05, 0x01],
            'DisplayPort': [0x07, 0x01],
            'DVI-D': [0x09, 0x01],
            'Card OPS': [0x08, 0x00],
            'USB': [0x08, 0x01],
            'Network': [0x0A, 0x00]
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x07 ^ 0x01 ^ 0xAC ^ ValueStateValues[value][0] ^ ValueStateValues[value][1] ^ 0x00 ^ 0x00
        InputCmdString = pack('13B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x07, 0x01, 0xAC, ValueStateValues[value][0], ValueStateValues[value][1], 0x00, 0x00, checksum)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def UpdateInput(self, value, qualifier):

        ValueStateValues = {
            1: 'Video',
            6: 'Component',
            8: 'VGA',
            10: 'HDMI 1',
            9: 'HDMI 2',
            13: 'DisplayPort',
            11: 'DVI-D',
            14: 'Card OPS',
            15: 'USB',
            16: 'Network',
            255: 'Unknown'
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0xAD
        InputCmdString = pack('9B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0xAD, checksum)
        res = self.__UpdateHelper('Input', InputCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Input', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Input: Invalid/unexpected response'])

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 0,
            '1': 1,
            '2': 2,
            '3': 3,
            '4': 4,
            '5': 5,
            '6': 6,
            '7': 7,
            '8': 8,
            '9': 9
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xFD ^ ValueStateValues[value]
        KeypadCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xFD, ValueStateValues[value],
                               checksum)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0xA1,
            'Up': 0xA6,
            'Down': 0xA7,
            'Left': 0xA8,
            'Right': 0xA9,
            'Ok': 0xB1,
            'Return': 0xB2,
            'Info': 0xD2
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xFD ^ ValueStateValues[value]
        MenuNavigationCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xFD,
                                       ValueStateValues[value], checksum)
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0xFD ^ 0xA5
        MuteCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0xFD, 0xA5, checksum)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 2,
            'Off': 1
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x18 ^ ValueStateValues[value]
        PowerCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x18, ValueStateValues[value],
                              checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def UpdatePower(self, value, qualifier):

        ValueStateValues = {
            2: 'On',
            1: 'Off'
        }

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x19
        PowerCmdString = pack('9B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x19, checksum)
        res = self.__UpdateHelper('Power', PowerCmdString, value, qualifier)
        if res:
            try:
                value = ValueStateValues[res[-2]]
                self.WriteStatus('Power', value, qualifier)
            except (KeyError, IndexError):
                self.Error(['Power: Invalid/unexpected response'])

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 60:
            checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x04 ^ 0x01 ^ 0x44 ^ value
            VolumeCmdString = pack('10B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x04, 0x01, 0x44, value, checksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def UpdateVolume(self, value, qualifier):

        checksum = 0xA6 ^ self.DeviceID ^ 0x00 ^ 0x00 ^ 0x00 ^ 0x03 ^ 0x01 ^ 0x45
        VolumeCmdString = pack('9B', 0xA6, self.DeviceID, 0x00, 0x00, 0x00, 0x03, 0x01, 0x45, checksum)
        res = self.__UpdateHelper('Volume', VolumeCmdString, value, qualifier)
        if res:
            try:
                value = int(res[-2])
                self.WriteStatus('Volume', value, qualifier)
            except (ValueError, IndexError):
                self.Error(['Volume: Invalid/unexpected response'])

    def __CheckResponseForErrors(self, sourceCmdName, response):

        DEVICE_ERROR_CODES = {
            3: 'NACK - Not Acknowledged.',
            4: 'NAV - Checksum Error.'
        }

        if response[7] in DEVICE_ERROR_CODES and response[6] == 0 and len(response) == 9:
            self.Error('Error: ' + DEVICE_ERROR_CODES[response[-2]])
            response = ''
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

            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliRex=self.updateRegex[command])
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
                    except:
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
            raise KeyError('Invalid command for ReadStatus: ' + command)


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0,
                 Mode='RS232', Model=None):
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