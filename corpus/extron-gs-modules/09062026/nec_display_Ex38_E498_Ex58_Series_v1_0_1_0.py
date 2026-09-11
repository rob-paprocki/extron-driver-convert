from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = 0x41
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'TVChannelCommand': {'Status': {}},
            'TVChannelStep': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = 0x2A
        elif 1 <= int(value) <= 100:
            self._DeviceID = 0x40 + int(value)
        else:
           print('Invalid Device ID parameter.')

    def __calculate_checksum(self, command_string):

        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, op_code_page, op_code, value):

        header = b'\x010' + bytes([self._DeviceID]) + b'0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'

        return header + message + checksum + delimiter

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'01',
            'Full': b'02',
            'Zoom': b'04',
            '1:1': b'07'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.__build_setstring(b'02', b'70', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.__build_setstring(b'00', b'1E', b'01')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA (RGB)': b'01',
            'VGA (YPbPr)': b'0C',
            'Video': b'05',
            'Tuner': b'09',
            'HDMI 1': b'11',
            'HDMI 2': b'12',
            'HDMI 3': b'82',
            'Media Player': b'87'
        }

        if value in ValueStateValues:
            InputCmdString = self.__build_setstring(b'00', b'60', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'1',
            'Off': b'4'
        }

        if value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A0C\x02C203D6000', ValueStateValues[value], b'\x03'])
            PowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetTVChannelCommand(self, value, qualifier):

        channel_string = value

        if channel_string:
            try:
                channels = channel_string.split('.')
                if len(channels) == 2:
                    major = int(channels[0])
                    minor = int(channels[1])

                    if (0 <= major <= 65535) and (0 <= minor <= 65535):
                        major = '{0:04X}'.format(major).encode()
                        minor = '{0:04X}'.format(minor).encode()

                        temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A12\x02C22D0000', major, minor, b'\x03'])
                        TVChannelCommandCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
                        self.__SetHelper('TVChannelCommand', TVChannelCommandCmdString, value, qualifier)
                        return
            except ValueError:
                pass

        self.Discard('Invalid Command for SetTVChannelCommand')

    def SetTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'33',
            'Down': b'32'
        }

        if value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A0C\x02C21000', ValueStateValues[value], b'03', b'\x03'])
            TVChannelStepCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('TVChannelStep', TVChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTVChannelStep')

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'17',
            'Down': b'16'
        }

        if value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A0C\x02C21000', ValueStateValues[value], b'03', b'\x03'])
            VolumeStepCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolumeStep')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

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