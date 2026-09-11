from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Backlight': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '1:1': b'\x8C0',
            'Fill Screen': b'\x8C1',
            'Fill to Aspect Ratio': b'\x8C2',
            '4:3': b'\x8C9',
            '16:9': b'\x8CA',
            '16:10': b'\x8CB',
            '2.35:1': b'\x8CC',
            '2:1': b'\x8CD'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = ValueStateValues[value]
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x80M0',
            'Off': b'\x80M1'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = ValueStateValues[value]
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetBacklight(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xE11',
            'Off': b'\xE10'
        }

        if value in ValueStateValues:
            BacklightCmdString = ValueStateValues[value]
            self.__SetHelper('Backlight', BacklightCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBacklight')

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xC61',
            'Off': b'\xC60'
        }

        if value in ValueStateValues:
            FreezeCmdString = ValueStateValues[value]
            self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFreeze')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'ARGB': b'\x98\x41\x31',
            'Composite': b'\x98\x42\x31',
            'S-Video': b'\x98\x43\x31',
            'SD-Component': b'\x98\x44\x31',
            'HDSDI': b'\x98\x45\x31',
            'DVI': b'\x98\x46\x31',
            'HD Component': b'\x98\x47\x31',
            'HDMI': b'\x98\x48\x31',
            'DisplayPort': b'\x98\x50\x31',
            'Composite 2': b'\x98\x42\x32',
            'HDSDI 2': b'\x98\x45\x32'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\xF7',
            'Down': b'\xFA',
            'Up': b'\xFB',
            'Right': b'\xFC',
            'Left': b'\xFD'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xC81',
            'Off': b'\xC80'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 30:
            VolumeCmdString = '\x80A{:02X}'.format(value).encode(encoding='iso-8859-1')
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command + 'does not support Set.')


class SerialClass(SerialInterface, DeviceClass):

    def __init__(self, Host, Port, Baud=2400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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