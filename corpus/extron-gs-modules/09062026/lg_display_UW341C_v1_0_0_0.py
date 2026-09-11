from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'Backlight': {'Status': {}},
            'ExecutiveMode': {'Parameters': ['Button'], 'Status': {}},
            'Input': {'Status': {}},
            'Mute': {'Status': {}},
            'OnScreenDisplay': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Volume': {'Status': {}}
        }


    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': b'\x01',
            '16:9': b'\x02',
            'Zoom': b'\x04',
            'Zoom 2': b'\x05',
            'Original': b'\x06',
            '14:9': b'\x07',
            'Just Scan': b'\x09',
            'Full Wide': b'\x0B',
            'Cinema Zoom 1': b'\x10',
            'Cinema Zoom 2': b'\x11',
            'Cinema Zoom 3': b'\x12',
            'Cinema Zoom 4': b'\x13',
            'Cinema Zoom 5': b'\x14',
            'Cinema Zoom 6': b'\x15',
            'Cinema Zoom 7': b'\x16',
            'Cinema Zoom 8': b'\x17',
            'Cinema Zoom 9': b'\x18',
            'Cinema Zoom 10': b'\x19',
            'Cinema Zoom 11': b'\x1A',
            'Cinema Zoom 12': b'\x1B',
            'Cinema Zoom 13': b'\x1C',
            'Cinema Zoom 14': b'\x1D',
            'Cinema Zoom 15': b'\x1E',
            'Cinema Zoom 16': b'\x1F'
        }
        AspectRatioCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x71\x01' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetBacklight(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            BacklightCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x46' + value.to_bytes(1, 'big')
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            print('Invalid Command for SetBacklight')

    def SetExecutiveMode(self, value, qualifier):

        ButtonStates = {
            'Power': b'\x66',
            'Volume': b'\x67',
            'Channel': b'\x68',
            'Input': b'\x69',
            'All Except Power, Volume,'
            ' Channel and Input': b'\x6A',
            'All': b'\x6B',
            'All Except Power': b'\x6C'
        }
        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        Button = qualifier['Button']
        if Button in ButtonStates:
            ExecutiveModeCmdString = ButtonStates[Button].join([b'\x01\x00\xA0\x00\xD3\x8D', ValueStateValues[value]])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetExecutiveMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV': b'\x02\x00\x00',
            'PC': b'\x03\x00\x00',
            'HDMI 1': b'\x04\x00\x00',
            'HDMI 2': b'\x04\x00\x01',
            'HDMI 3': b'\x04\x00\x02',
            'Component': b'\x05\x00\x00'
        }
        InputCmdString = b'\x01\x00\xA0\x00\xD3\x8D' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        MuteCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x72\x01' + ValueStateValues[value]
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetOnScreenDisplay(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01',
            'Off': b'\x00'
        }
        OnScreenDisplayCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x47' + ValueStateValues[value]
        self.__SetHelper('OnScreenDisplay', OnScreenDisplayCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Vivid': b'\x00',
            'Standard': b'\x01',
            'Eco': b'\x02',
            'Cinema': b'\x03',
            'Sport': b'\x04',
            'Game': b'\x05'
        }
        PictureModeCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x71\x00' + ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x01\x00\xA0\x00\xD3\x8D\x72\x00' + value.to_bytes(1, 'big')
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
