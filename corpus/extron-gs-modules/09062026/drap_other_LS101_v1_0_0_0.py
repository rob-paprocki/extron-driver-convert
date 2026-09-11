from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ScreenControl': {'Parameters': ['Device ID', 'Channel'], 'Status': {}},
        }

    def SetScreenControl(self, value, qualifier):

        device_id = int(qualifier['Device ID'])
        channel = int(qualifier['Channel'])

        ValueStateValues = {
            'Up': 0xDD,
            'Down': 0xEE,
            'Stop': 0xCC
        }

        if all(1 <= x <= 255 for x in {device_id, channel}):
            ScreenControlCmdString = pack('>5B', device_id, channel, 0x00, 0x0A, ValueStateValues[value])
            checksum = (device_id ^ channel ^ 0x00 ^ 0x0A ^ ValueStateValues[value]).to_bytes(1, 'big')
            ScreenControlCmdString = b'\x9A' + ScreenControlCmdString + checksum
            self.__SetHelper('ScreenControl', ScreenControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenControl')

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
            raise AttributeError(command, 'does not support Set.')


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
