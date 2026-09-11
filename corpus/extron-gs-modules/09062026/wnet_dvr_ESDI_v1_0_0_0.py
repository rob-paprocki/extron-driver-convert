from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.Debug = False
        self.Models = {}
        self.DeviceID = 1

        self.Commands = {
            'KeyCode': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'MultiPicture': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = int(value)

    def SetKeyCode(self, value, qualifier):

        States = {

            '0': 0x00,
            '1': 0x01,
            '2': 0x02,
            '3': 0x03,
            '4': 0x04,
            '5': 0x05,
            '6': 0x06,
            '7': 0x07,
            '8': 0x08,
            '9': 0x09,

            'Up': 0x0A,
            'Down': 0x0B,
            'Left': 0x0C,
            'Right': 0x0D,
            'Cancel': 0x0E,
            'Enter': 0x0F,
            'Record': 0x10,
            'Multi-Picture': 0x11,
            'Playback': 0x12,
            'Function': 0x13,
            'Previous Section': 0x14,
            'Next Section': 0x15,
            'Play': 0x16,
            'Fast Forward': 0x17,
            'Information': 0x18,

            '4 Picture A': 0x19,
            '4 Picture B': 0x1A,
            '4 Picture C': 0x1B,
            '4 Picture D': 0x1C,
            '8 Picture A': 0x1D,
            '8 Picture B': 0x1E,
            'Single Picture 1': 0x81,
            'Single Picture 2': 0x82,
            'Single Picture 3': 0x83,
            'Single Picture 4': 0x84,
            'Single Picture 5': 0x85,
            'Single Picture 6': 0x86,
            'Single Picture 7': 0x87,
            'Single Picture 8': 0x88,
            'Single Picture 9': 0x89,
            'Single Picture 10': 0x8A,
            'Single Picture 11': 0x8B,
            'Single Picture 12': 0x8C,
            'Single Picture 13': 0x8D,
            'Single Picture 14': 0x8E,
            'Single Picture 15': 0x8F,
            'Single Picture 16': 0x90,

        }

        CmdString = bytes([0x80, self._DeviceID, States[value], 0x01])
        self.__SetHelper('KeyCode', CmdString, value, qualifier)
        
    def SetMenuNavigation(self, value, qualifier):
        self.SetKeyCode(value, qualifier)
        
    def SetMultiPicture(self, value, qualifier):
        self.SetKeyCode(value, qualifier)

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
