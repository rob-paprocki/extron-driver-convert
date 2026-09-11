from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'DMXBufferLevel': {'Parameters': ['Channel'], 'Status': {}},
            'Fade': {'Status': {}},
            'PresetRecall': {'Parameters': ['Page', 'Show'], 'Status': {}},
            'StartSelectShow': {'Parameters': ['Show'], 'Status': {}},
            'StopAllActions': {'Status': {}},
        }


    def SetDMXBufferLevel(self, value, qualifier):

        channel = int(qualifier['Channel'])
        if 0 <= value <= 100 and 1 <= channel <= 255:
            DMXBufferLevelCmdString = b'X4' + pack('>H', channel - 1) + pack('>B', int(value * 2.55)) + b'X4' + pack('>H', channel - 1) + pack('>B', int(value * 2.55)) + b'X4' + pack('>H', channel - 1) + pack('>B', int(value * 2.55))
            self.__SetHelper('DMXBufferLevel', DMXBufferLevelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetDMXBufferLevel')

    def SetFade(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 65535
        }

        if 0 <= value <= 65535:
            FadeCmdString = b'F01' + pack('>H', value)
            self.__SetHelper('Fade', FadeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFade')

    def SetPresetRecall(self, value, qualifier):

        PageStates = {
            '0': b'\x00',
            '1': b'\x01'
        }

        page = qualifier['Page']
        show = qualifier['Show']
        if page in PageStates and 65 <= ord(show) <= 90:
            PresetRecallCmdString = b'L' + PageStates[page] + pack('>BH', ord(show), int(value))
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPresetRecall')

    def SetStartSelectShow(self, value, qualifier):

        show_id = qualifier['Show']
        if 65 <= ord(show_id) <= 90:
            StartSelectShowCmdString = b'H1H' + bytes(show_id, 'utf-8') + b'H0'
            self.__SetHelper('StartSelectShow', StartSelectShowCmdString, value, qualifier)
        else:
            print('Invalid Command for SetStartSelectShow')

    def SetStopAllActions(self, value, qualifier):

        StopAllActionsCmdString = b'H1'
        self.__SetHelper('StopAllActions', StopAllActionsCmdString, value, qualifier)

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


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
