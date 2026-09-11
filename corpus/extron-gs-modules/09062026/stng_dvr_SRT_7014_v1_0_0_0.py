from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Channel': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteEmulation': {'Status': {}},
            'Transports': {'Status': {}},
            'Volume': {'Status': {}},
        }

        self.Header = b'\xA5\x07\x00\x30\x08\x7F\x02'

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x49,
            'Down': 0x4A
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        ChannelCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': 0x1B,
            '1': 0x15,
            '2': 0x16,
            '3': 0x17,
            '4': 0x54,
            '5': 0x55,
            '6': 0x56,
            '7': 0x57,
            '8': 0x18,
            '9': 0x19
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        KeypadCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': 0x09,
            'Up': 0x4B,
            'Down': 0x0C,
            'Left': 0x0F,
            'Right': 0x0E,
            'Okay': 0x0D,
            'Exit': 0x0A
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        MenuNavigationCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('MenuNavigation',
                         MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        Checksum = (0x40 - 0x09) & 0xFF
        MuteCmdString = self.Header + b'\x40\x00' + pack('B', Checksum)
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        Checksum = (0x00 - 0x09) & 0xFF
        PowerCmdString = self.Header + b'\x00\x00' + pack('B', Checksum)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRemoteEmulation(self, value, qualifier):

        ValueStateValues = {
            'Text': 0x03,
            'Subtitle': 0x42,
            'Sleep': 0x06,
            'Freeze': 0x07,
            'TV/Radio': 0x41,
            'Audio': 0x04,
            'Zoom': 0x44,
            'Recall': 0x47,
            'Red': 0x51,
            'Blue': 0x14,
            'Green': 0x52,
            'Yellow': 0x53,
            'V. Format': 0x1A,
            'Wide': 0x58
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        RemoteEmulationCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('RemoteEmulation',
                         RemoteEmulationCmdString, value, qualifier)

    def SetTransports(self, value, qualifier):

        ValueStateValues = {
            'Play': 0x4D,
            'Pause': 0x10,
            'Stop': 0x4E,
            'Slow': 0x50,
            'Record': 0x13,
            'Rewind': 0x4F,
            'Fast Forward': 0x11,
            'Advance': 0x12
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        TransportsCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('Transports', TransportsCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x0B,
            'Down': 0x48
        }

        Checksum = (ValueStateValues[value] - 0x09) & 0xFF
        VolumeCmdString = self.Header + \
            pack('B', ValueStateValues[value]) + b'\x00' + pack('B', Checksum)
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(
            self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'Host Alias: {0}, Port: {1}'.format(
            self.Host.DeviceAlias, self.Port)
        print('Module: {}'.format(__name__), portInfo,
              'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])


class SerialOverEthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(
            self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()

    def Error(self, message):
        portInfo = 'IP Address/Host: {0}:{1}'.format(
            self.Hostname, self.IPPort)
        print('Module: {}'.format(__name__), portInfo,
              'Error Message: {}'.format(message[0]), sep='\r\n')

    def Discard(self, message):
        self.Error([message])

    def Disconnect(self):
        EthernetClientInterface.Disconnect(self)
        self.OnDisconnected()
