from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Unidirectional = False
        self.DefaultResponseTimeout = 0.3

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'Channel': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x02KEY:030\x03'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up': b'\x02KEY:010\x03',
            'Down': b'\x02KEY:011\x03'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x02KEY:035\x03'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'TV': b'\x02KEY:102\x03',
            'Video': b'\x02KEY:103\x03',
            'VGA 1': b'\x02KEY:105\x03',
            'VGA 2': b'\x02KEY:107\x03',
            'VGA 3': b'\x02KEY:108\x03',
            'HDMI 1': b'\x02KEY:111\x03',
            'HDMI 2': b'\x02KEY:112\x03',
            'HDMI 3': b'\x02KEY:113\x03'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        KeypadState = {
            '1': b'\x02KEY:001\x03',
            '2': b'\x02KEY:002\x03',
            '3': b'\x02KEY:003\x03',
            '4': b'\x02KEY:004\x03',
            '5': b'\x02KEY:005\x03',
            '6': b'\x02KEY:006\x03',
            '7': b'\x02KEY:007\x03',
            '8': b'\x02KEY:008\x03',
            '9': b'\x02KEY:009\x03',
            '0': b'\x02KEY:000\x03'
        }

        KeypadCmdString = KeypadState[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationState = {
            'Up': b'\x02KEY:017\x03',
            'Down': b'\x02KEY:018\x03',
            'Left': b'\x02KEY:019\x03',
            'Right': b'\x02KEY:020\x03',
            'Enter': b'\x02KEY:015\x03',
            'Menu': b'\x02KEY:014\x03',
            'Return': b'\x02KEY:016\x03'
        }

        MenuNavigationCmdString = MenuNavigationState[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x02KEY:023\x03'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        PictureModeCmdString = b'\x02KEY:025\x03'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x02KEY:021\x03',
            'Off': b'\x02KEY:048\x03'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeState = {
            'Up': b'\x02KEY:012\x03',
            'Down': b'\x02KEY:013\x03'
        }

        VolumeCmdString = VolumeState[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __CheckResponseForErrors(self, sourceCmdName, response):

        if response[1:3] in b'ER':
            self.Error(['Invalid command'])
            response = ''
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True':
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag=b'\x03')
            if not res:
                self.Error(['{0}: Invalid/Unexpected Response'.format(command)])
            else:
                res = self.__CheckResponseForErrors(command, res)

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
