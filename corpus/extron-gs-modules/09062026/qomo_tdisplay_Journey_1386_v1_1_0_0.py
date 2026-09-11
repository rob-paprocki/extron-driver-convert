from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '16:9': b'\x55\x54\x53\x50\x64\x31\x31\x21',
            '4:3': b'\x55\x54\x53\x50\x64\x21\x21\x21',
            'Figure': b'\x55\x54\x53\x50\x64\x30\x21\x21',
            'Full View': b'\x55\x54\x53\x50\x64\x31\x21\x21',
            'Subtitle': b'\x55\x54\x53\x50\x64\x32\x21\x21',
            'Movie': b'\x55\x54\x53\x50\x64\x33\x21\x21'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up': b'\x55\x54\x53\x50\x3E\x21\x21\x21',
            'Down': b'\x55\x54\x53\x50\x3C\x21\x21\x21'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'DTV/ATV': b'\x55\x54\x53\x50\x73\x21\x21\x21',
            'Video 1': b'\x55\x54\x53\x50\x73\x30\x30\x21',
            'Video 2': b'\x55\x54\x53\x50\x73\x30\x31\x21',
            'Component': b'\x55\x54\x53\x50\x73\x30\x32\x21',
            'HDMI 1': b'\x55\x54\x53\x50\x73\x30\x33\x21',
            'HDMI 2': b'\x55\x54\x53\x50\x73\x30\x34\x21',
            'PC 1': b'\x55\x54\x53\x50\x73\x30\x35\x21',
            'PC 2': b'\x55\x54\x53\x50\x73\x30\x36\x21',
            'S Terminal': b'\x55\x54\x53\x50\x73\x30\x37\x21',
            'Built in HDMI': b'\x55\x54\x53\x50\x73\x30\x38\x21',
            'External HDMI': b'\x55\x54\x53\x50\x73\x30\x39\x21'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x55\x54\x53\x50\x55\x21\x21\x21',
            'Down': b'\x55\x54\x53\x50\x44\x21\x21\x21',
            'Left': b'\x55\x54\x53\x50\x4C\x21\x21\x21',
            'Right': b'\x55\x54\x53\x50\x52\x21\x21\x21',
            'Ok': b'\x55\x54\x53\x50\x4F\x21\x21\x21',
            'Menu': b'\x55\x54\x53\x50\x6D\x21\x21\x21',
            'Back': b'\x55\x54\x53\x50\x45\x21\x21\x21',
            'Home': b'\x55\x54\x53\x50\x48\x21\x21\x21'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x55\x54\x53\x50\x4D\x21\x21\x21'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeState = {
            'Standard': b'\x55\x54\x53\x50\x70\x35\x21\x21',
            'Bright': b'\x55\x54\x53\x50\x70\x21\x21\x21',
            'Soft': b'\x55\x54\x53\x50\x70\x30\x21\x21',
            'Customized': b'\x55\x54\x53\x50\x70\x31\x21\x21'
        }

        PictureModeCmdString = PictureModeState[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x55\x54\x53\x50\x4E\x21\x21\x21',
            'Off': b'\x55\x54\x53\x50\x46\x21\x21\x21'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeState = {
            'Up': b'\x55\x54\x53\x50\x2B\x21\x21\x21',
            'Down': b'\x55\x54\x53\x50\x2D\x21\x21\x21'
        }

        VolumeCmdString = VolumeState[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
