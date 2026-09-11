from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }


    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1A\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x19\xCF'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'ATV': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x08\xCF',
            'HDMI 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF',
            'HDMI 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF',
            'HDMI 3': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0C\xCF',
            'HDMI 4 (OPS)': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x38\xCF',
            'PC': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF',
            'DTV': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0F\xCF',
            'Component': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x10\xCF',
            'Video': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x11\xCF'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2A\xCF',
            '1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x21\xCF',
            '2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x22\xCF',
            '3': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x23\xCF',
            '4': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x24\xCF',
            '5': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x25\xCF',
            '6': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x26\xCF',
            '7': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x27\xCF',
            '8': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x28\xCF',
            '9': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x29\xCF'
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1B\xCF',
            'Home Page': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1C\xCF',
            'Return': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1D\xCF',
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x13\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x14\xCF',
            'Enter': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2B\xCF',
            'Up Arrow': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2E\xCF',
            'Down Arrow': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2F\xCF',
            'Left Arrow': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2C\xCF',
            'Right Arrow': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2D\xCF'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x02\xCF'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x00\xCF',
            'Off': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x01\xCF'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x18\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x17\xCF'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)


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
