from extronlib.interface import EthernetClientInterface
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DimmerControl': {'Parameters': ['Panel Number', 'Dim Number', 'Dimmer Name'], 'Status': {}},
            'RelayControl': {'Parameters': ['Panel Number', 'Relay Name'], 'Status': {}},
            'RemoteControl': {'Parameters': ['Panel Number', 'Remote Name'], 'Status': {}},
        }

    def SetDimmerControl(self, value, qualifier):

        DimNumberStates = {
            '1': b'\x06',
            '2': b'\x07',
            '3': b'\x08'
        }
        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if 1 <= int(qualifier['Panel Number']) <= 254:
            panel = pack('>B', int(qualifier['Panel Number']))
            if 1 <= len(qualifier['Dimmer Name']) <= 8 and ValueConstraints['Min'] <= value <= ValueConstraints['Max'] and 1 <= int(qualifier['Dim Number']) <= 3:
                DimmerControlCmdStringTemp = b'\xAA\x1B' + panel + b'\x00\x00\x0E' + '{0: <8}'.format(qualifier['Dimmer Name']).encode() + b'01' + \
                    DimNumberStates[qualifier['Dim Number']] + b'\x00\x04\x01\x08\x00\x00\x00\x00\x00\x00\x00' + pack('>B', value)
                checksum = 0
                for i in DimmerControlCmdStringTemp:
                    checksum = checksum ^ i
                DimmerControlCmdString = DimmerControlCmdStringTemp + pack('>B', checksum)
                self.__SetHelper('DimmerControl', DimmerControlCmdString, value, qualifier)
            else:
                print('Invalid Command for SetDimmerControl')
        else:
            print('Invalid Command for SetDimmerControl')

    def SetRelayControl(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x03',
            'Off': b'\x02'
        }

        if 1 <= int(qualifier['Panel Number']) <= 254:
            panel = pack('>B', int(qualifier['Panel Number']))
            if 1 <= len(qualifier['Relay Name']) <= 8:
                RelayControlCmdStringTemp = b'\xAA\x0E' + panel + b'\x00\x00\x03' + '{0: <8}'.format(qualifier['Relay Name']).encode() + ValueStateValues[value]
                checksum = 0
                for i in RelayControlCmdStringTemp:
                    checksum = checksum ^ i
                RelayControlCmdString = RelayControlCmdStringTemp + pack('>B', checksum)
                self.__SetHelper('RelayControl', RelayControlCmdString, value, qualifier)
            else:
                print('Invalid Command for SetRelayControl')
        else:
            print('Invalid Command for SetRelayControl')

    def SetRemoteControl(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x03',
            'Off': b'\x02'
        }

        if qualifier['Panel Number'] == 'Broadcast' or 1 <= int(qualifier['Panel Number']) <= 254:
            if qualifier['Panel Number'] == 'Broadcast':
                panel = b'\xFF'
            elif 1 <= int(qualifier['Panel Number']) <= 254:
                panel = pack('>B', int(qualifier['Panel Number']))
            if 1 <= len(qualifier['Remote Name']) <= 8:
                RemoteControlCmdStringTemp = b'\xAA\x0E' + panel + b'\x00\x00\x02' + '{0: <8}'.format(qualifier['Remote Name']).encode() + ValueStateValues[value]
                checksum = 0
                for i in RemoteControlCmdStringTemp:
                    checksum = checksum ^ i
                RemoteControlCmdString = RemoteControlCmdStringTemp + pack('>B', checksum)
                self.__SetHelper('RemoteControl', RemoteControlCmdString, value, qualifier)
            else:
                print('Invalid Command for SetRemoteControl')
        else:
            print('Invalid Command for SetRemoteControl')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

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
