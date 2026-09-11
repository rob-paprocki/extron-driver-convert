from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '16:9': b'\x08\x22\x0B\x0A\x01\x00\xC0',
            'Zoom 1': b'\x08\x22\x0B\x0A\x01\x01\xBF',
            'Zoom 2': b'\x08\x22\x0B\x0A\x01\x02\xBE',
            '4:3': b'\x08\x22\x0B\x0A\x01\x04\xBC'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up': b'\x08\x22\x03\x00\x01\x00\xD2',
            'Down': b'\x08\x22\x03\x00\x02\x00\xD1'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'TV': b'\x08\x22\x0A\x00\x00\x00\xCC',
            'AV': b'\x08\x22\x0A\x00\x00\x00\xCB',
            'Component': b'\x08\x22\x0A\x00\x03\x00\xC9',
            'HDMI 1': b'\x08\x22\x0A\x00\x05\x00\xC7',
            'HDMI 2': b'\x08\x22\x0A\x00\x05\x01\xC6',
            'HDMI 3': b'\x08\x22\x0A\x00\x05\x02\xC5',
            'HDMI 4': b'\x08\x22\x0A\x00\x05\x03\xC4'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x08\x22\x0D\x00\x00\x60\x69',
            'Down': b'\x08\x22\x0D\x00\x00\x61\x68',
            'Left': b'\x08\x22\x0D\x00\x00\x65\x64',
            'Right': b'\x08\x22\x0D\x00\x00\x62\x67',
            'Menu': b'\x08\x22\x0D\x00\x00\x1A\xAF',
            'Enter': b'\x08\x22\x0D\x00\x00\x68\x61',
            'Exit': b'\x08\x22\x0D\x00\x00\x2D\x9C'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x08\x22\x02\x00\x00\x00\xD4'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x08\x22\x00\x00\x00\x02\xD4',
            'Off': b'\x08\x22\x00\x00\x00\x01\xD5'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min': 0,
            'Max': 100
        }

        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            cks = 256 - 43 - value
            VolumeCmdString = b'\x08\x22\x01\x00\x00' + value.to_bytes(1, 'big') + cks.to_bytes(1, 'big')
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
