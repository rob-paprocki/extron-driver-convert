from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Commands = {
            'Level': {'Parameters': ['Address'], 'Status': {}},
            'Scene': {'Parameters': ['Address'], 'Status': {}},
        }

    def SetLevel(self, value, qualifier):

        AddressConstraints = {
            'Min': 0,
            'Max': 63
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 254
        }

        addrVal = int(qualifier['Address'])
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and AddressConstraints['Min'] <= addrVal <= AddressConstraints['Max']:
            addr_Val = (0 << 8) + (addrVal << 1) + 0
            checksum = 3 ^ 0 ^ addr_Val ^ value
            LevelCmdString = pack('5B', 3, 0, addr_Val, value, checksum)
            self.__SetHelper('Level', LevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLevel')

    def SetScene(self, value, qualifier):

        AddressConstraints = {
            'Min': 0,
            'Max': 63
        }

        ValueStateValues = {  # 0x10-0x1F
            '0': 16,
            '1': 17,
            '2': 18,
            '3': 19,
            '4': 20,
            '5': 21,
            '6': 22,
            '7': 23,
            '8': 24,
            '9': 25,
            '10': 26,
            '12': 27,
            '13': 29,
            '14': 30,
            '15': 31
        }

        addrVal = int(qualifier['Address'])
        if AddressConstraints['Min'] <= addrVal <= AddressConstraints['Max']:
            addr_Val = (0 << 8) + (addrVal << 1) + 0
            checksum = 3 ^ 0 ^ addr_Val ^ ValueStateValues[value]
            SceneCmdString = pack('5B', 3, 0, addr_Val, ValueStateValues[value], checksum)
            self.__SetHelper('Scene', SceneCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScene')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
