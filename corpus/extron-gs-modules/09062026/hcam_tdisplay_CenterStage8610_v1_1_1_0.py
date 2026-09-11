from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x99\x23\x1F\x01\xE0\xAA'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up': b'\x99\x23\x19\x01\xE6\xAA',
            'Down': b'\x99\x23\x1A\x01\xE5\xAA'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'ATV': b'\x99\x23\x07\x01\xF8\xAA',
            'AV': b'\x99\x23\x08\x01\xF7\xAA',
            'YPbPr': b'\x99\x23\x0A\x01\xF5\xAA',
            'VGA': b'\x99\x23\x0B\x01\xF4\xAA',
            'HDMI 1': b'\x99\x23\x0E\x01\xF1\xAA',
            'HDMI 2': b'\x99\x23\x0F\x01\xF0\xAA',
            'HDMI 3': b'\x99\x23\x10\x01\xEF\xAA',
            'USB': b'\x99\x23\x27\x01\xD8\xAA'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x99\x23\x22\x01\xDD\xAA',
            'Down': b'\x99\x23\x23\x01\xDC\xAA',
            'Left': b'\x99\x23\x24\x01\xDB\xAA',
            'Right': b'\x99\x23\x25\x01\xDA\xAA',
            'Enter': b'\x99\x23\x26\x01\xD9\xAA',
            'Menu': b'\x99\x23\x12\x01\xED\xAA',
            'Home': b'\x99\x23\x00\x01\xFF\xAA',
            'Exit': b'\x99\x23\x14\x01\xEB\xAA'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x99\x23\x02\x01\xFD\xAA'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x99\x23\x04\x01\xFB\xAA'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x99\x23\x80\x01\x7F\xAA',
            'Off': b'\x99\x23\x01\x01\xFE\xAA'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeState = {
            'Up': b'\x99\x23\x17\x01\xE8\xAA',
            'Down': b'\x99\x23\x18\x01\xE7\xAA'
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
