from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Page': {'Status': {}},
            'PCPower': {'Status': {}},
            'Power': {'Status': {}},
            'RemoteKeys': {'Status': {}},
            'TVChannel': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\xAA\xBB\xCC\x08\x00\x00\x08\xDD\xEE\xFF',
            '4:3': b'\xAA\xBB\xCC\x08\x01\x00\x09\xDD\xEE\xFF',
            'Point to Point': b'\xAA\xBB\xCC\x08\x07\x00\x0F\xDD\xEE\xFF'
        }

        AspectRatioCmdString = ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'\xAA\xBB\xCC\x02\x01\x00\x03\xDD\xEE\xFF',
            'CVBS': b'\xAA\xBB\xCC\x02\x02\x00\x04\xDD\xEE\xFF',
            'VGA 1': b'\xAA\xBB\xCC\x02\x03\x00\x05\xDD\xEE\xFF',
            'VGA 2': b'\xAA\xBB\xCC\x02\x04\x00\x06\xDD\xEE\xFF',
            'VGA 3': b'\xAA\xBB\xCC\x02\x0B\x00\x0D\xDD\xEE\xFF',
            'HDMI 1': b'\xAA\xBB\xCC\x02\x06\x00\x08\xDD\xEE\xFF',
            'HDMI 2': b'\xAA\xBB\xCC\x02\x07\x00\x09\xDD\xEE\xFF',
            'HDMI 3': b'\xAA\xBB\xCC\x02\x05\x00\x07\xDD\xEE\xFF',
            'PC': b'\xAA\xBB\xCC\x02\x08\x00\x0A\xDD\xEE\xFF',
            'Android': b'\xAA\xBB\xCC\x02\x0A\x00\x0C\xDD\xEE\xFF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\xAA\xBB\xCC\x07\x1B\x00\x22\xDD\xEE\xFF',
            '1': b'\xAA\xBB\xCC\x07\x00\x00\x07\xDD\xEE\xFF',
            '2': b'\xAA\xBB\xCC\x07\x10\x00\x17\xDD\xEE\xFF',
            '3': b'\xAA\xBB\xCC\x07\x11\x00\x18\xDD\xEE\xFF',
            '4': b'\xAA\xBB\xCC\x07\x13\x00\x1A\xDD\xEE\xFF',
            '5': b'\xAA\xBB\xCC\x07\x14\x00\x1B\xDD\xEE\xFF',
            '6': b'\xAA\xBB\xCC\x07\x15\x00\x1C\xDD\xEE\xFF',
            '7': b'\xAA\xBB\xCC\x07\x17\x00\x1E\xDD\xEE\xFF',
            '8': b'\xAA\xBB\xCC\x07\x18\x00\x1F\xDD\xEE\xFF',
            '9': b'\xAA\xBB\xCC\x07\x19\x00\x20\xDD\xEE\xFF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Home': b'\xAA\xBB\xCC\x07\x48\x00\x4F\xDD\xEE\xFF',
            'Menu': b'\xAA\xBB\xCC\x07\x0D\x00\x14\xDD\xEE\xFF',
            'Up': b'\xAA\xBB\xCC\x07\x47\x00\x4E\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x4D\x00\x54\xDD\xEE\xFF',
            'Left': b'\xAA\xBB\xCC\x07\x49\x00\x50\xDD\xEE\xFF',
            'Right': b'\xAA\xBB\xCC\x07\x4B\x00\x52\xDD\xEE\xFF',
            'Enter': b'\xAA\xBB\xCC\x07\x4A\x00\x51\xDD\xEE\xFF',
            'Back': b'\xAA\xBB\xCC\x07\x0A\x00\x11\xDD\xEE\xFF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPage(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\xAA\xBB\xCC\x07\x42\x00\x49\xDD\xEE\xFF',
            'Down': b'\xAA\xBB\xCC\x07\x0F\x00\x16\xDD\xEE\xFF'
        }

        PageCmdString = ValueStateValues[value]
        self.__SetHelper('Page', PageCmdString, value, qualifier)

    def SetPCPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x09\x01\x00\x0A\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x09\x00\x00\x09\xDD\xEE\xFF'
        }

        PCPowerCmdString = ValueStateValues[value]
        self.__SetHelper('PCPower', PCPowerCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xAA\xBB\xCC\x01\x00\x00\x01\xDD\xEE\xFF',
            'Off': b'\xAA\xBB\xCC\x01\x01\x00\x02\xDD\xEE\xFF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetRemoteKeys(self, value, qualifier):

        ValueStateValues = {
            'F1': b'\xAA\xBB\xCC\x07\x45\x00\x4C\xDD\xEE\xFF',
            'F2': b'\xAA\xBB\xCC\x07\x12\x00\x19\xDD\xEE\xFF',
            'F3': b'\xAA\xBB\xCC\x07\x51\x00\x58\xDD\xEE\xFF',
            'F4': b'\xAA\xBB\xCC\x07\x5B\x00\x62\xDD\xEE\xFF',
            'F5': b'\xAA\xBB\xCC\x07\x44\x00\x4B\xDD\xEE\xFF',
            'F6': b'\xAA\xBB\xCC\x07\x50\x00\x57\xDD\xEE\xFF',
            'F7': b'\xAA\xBB\xCC\x07\x43\x00\x4A\xDD\xEE\xFF',
            'F8': b'\xAA\xBB\xCC\x07\x1A\x00\x21\xDD\xEE\xFF',
            'F9': b'\xAA\xBB\xCC\x07\x04\x00\x0B\xDD\xEE\xFF',
            'F10': b'\xAA\xBB\xCC\x07\x59\x00\x60\xDD\xEE\xFF',
            'F11': b'\xAA\xBB\xCC\x07\x57\x00\x5E\xDD\xEE\xFF',
            'F12': b'\xAA\xBB\xCC\x07\x08\x00\x0F\xDD\xEE\xFF',
            'Red': b'\xAA\xBB\xCC\x07\x5C\x00\x63\xDD\xEE\xFF',
            'Green': b'\xAA\xBB\xCC\x07\x5D\x00\x64\xDD\xEE\xFF',
            'Yellow': b'\xAA\xBB\xCC\x07\x5E\x00\x65\xDD\xEE\xFF',
            'Blue': b'\xAA\xBB\xCC\x07\x5F\x00\x66\xDD\xEE\xFF',
            'WIN': b'\xAA\xBB\xCC\x07\x0B\x00\x12\xDD\xEE\xFF',
            'Space': b'\xAA\xBB\xCC\x07\x46\x00\x4D\xDD\xEE\xFF',
            'Alt+Tab': b'\xAA\xBB\xCC\x07\x1D\x00\x24\xDD\xEE\xFF',
            'Alt+F4': b'\xAA\xBB\xCC\x07\x1F\x00\x26\xDD\xEE\xFF',
            'Display': b'\xAA\xBB\xCC\x07\x1C\x00\x23\xDD\xEE\xFF',
            'Refresh': b'\xAA\xBB\xCC\x07\x4C\x00\x53\xDD\xEE\xFF',
            'Delete': b'\xAA\xBB\xCC\x07\x40\x00\x47\xDD\xEE\xFF',
            'Energy': b'\xAA\xBB\xCC\x07\x4E\x00\x55\xDD\xEE\xFF',
            'Point': b'\xAA\xBB\xCC\x07\x06\x00\x0D\xDD\xEE\xFF'
        }

        RemoteKeysCmdString = ValueStateValues[value]
        self.__SetHelper('RemoteKeys', RemoteKeysCmdString, value, qualifier)

    def SetTVChannel(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 99
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            chksum = (value + 0x05) & 0xFF
            TVChannelCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x05, 0x00, value, chksum, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('TVChannel', TVChannelCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTVChannel')

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            chksum = (value + 0x03) & 0xFF
            VolumeCmdString = pack('>10B', 0xAA, 0xBB, 0xCC, 0x03, 0x00, value, chksum, 0xDD, 0xEE, 0xFF)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

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
