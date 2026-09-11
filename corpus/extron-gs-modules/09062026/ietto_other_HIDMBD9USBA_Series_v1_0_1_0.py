from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Keyboard': {'Status': {}},
        }

    def SetKeyboard(self, value, qualifier):

        ValueStateValues = {
            'Delete': b'\x7F',
            'Backspace': b'\x08',
            'Tab': b'\x09',
            'Linefeed': b'\x0A',
            'Return': b'\x0D',
            'Escape': b'\x1B',
            'Space': b'\x20',
            '^A': b'\x01',
            '^B': b'\x02',
            '^C': b'\x03',
            '^D': b'\x04',
            '^E': b'\x05',
            '^F': b'\x06',
            '^G': b'\x07',
            '^K': b'\x0B',
            '^L': b'\x0C',
            '^N': b'\x0E',
            '^O': b'\x0F',
            '^P': b'\x10',
            '^Q': b'\x11',
            '^R': b'\x12',
            '^S': b'\x13',
            '^T': b'\x14',
            '^U': b'\x15',
            '^V': b'\x16',
            '^W': b'\x17',
            '^X': b'\x18',
            '^Y': b'\x19',
            '^Z': b'\x1A',
            '^\\': b'\x1C',
            '^]': b'\x1D',
            '^^': b'\x1E',
            '^_': b'\x1F',
            'F1': b'\xB5',
            'F2': b'\xB6',
            'F3': b'\xB7',
            'F4': b'\xB8',
            'F5': b'\xB9',
            'F6': b'\xBA',
            'F7': b'\xBB',
            'F8': b'\xBC',
            'F9': b'\xBD',
            'F10': b'\xBE',
            'F11': b'\xBF',
            'F12': b'\xC0',
            'Insert': b'\xC1',
            'Home': b'\xC2',
            'Page Up': b'\xC3',
            'Page Down': b'\xC6',
            'End': b'\xC5',
            'Right Arrow': b'\xC7',
            'Left Arrow': b'\xC8',
            'Down Arrow': b'\xC9',
            'Up Arrow': b'\xCA',
            'Control Alt Delete': b'\x8F\x05\xC4'
        }
        try:
            if len(value) > 1:
                KeyboardCmdString = ValueStateValues[value]
            elif ord(value) < 128:
                KeyboardCmdString = value
            self.__SetHelper('Keyboard', KeyboardCmdString, value, qualifier)
        except (KeyError, ValueError):
            print('Invalid Command for SetKeyboard')

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
