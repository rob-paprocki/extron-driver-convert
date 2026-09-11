from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AudioMode': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Capture': {'Status': {}},
            'Channel': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Model': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'Whiteboard': {'Status': {}},
            'WiFi': {'Status': {}},
        }

       
    def SetAudioMode(self, value, qualifier):

        AudioModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x34\xCF'
        self.__SetHelper('AudioMode', AudioModeCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetCapture(self, value, qualifier):

        CaptureCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1F\xCF'
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1A\xCF',
            'Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x19\xCF'
        }

        ChannelCmdString = ValueStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        EcoModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x16\xCF'
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HD 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0A\xCF',
            'HD 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0B\xCF',
            'YPbPr': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x10\xCF',
            'OPS Computer': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0C\xCF',
            'PC 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0D\xCF',
            'PC 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x0E\xCF',
            'Video 1': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x11\xCF',
            'Video 2': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x12\xCF'
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
            '9': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x29\xCF',
        }

        KeypadCmdString = ValueStateValues[value]
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'OK': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2B\xCF',
            'Source': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x06\xCF',
            'Cursor Right': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2D\xCF',
            'Cursor Left': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2C\xCF',
            'Cursor Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2E\xCF',
            'Cursor Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x2F\xCF',
            'Menu': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1B\xCF',
            'Page Up': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x13\xCF',
            'Page Down': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x14\xCF',
            'Back': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1D\xCF',
            'Home': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1C\xCF',
            'Search': b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1E\xCF',
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetModel(self, value, qualifier):

        ModelCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x31\xCF'
        self.__SetHelper('Model', ModelCmdString, value, qualifier)

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

    def SetWhiteboard(self, value, qualifier):

        WhiteboardCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x07\xCF'
        self.__SetHelper('Whiteboard', WhiteboardCmdString, value, qualifier)

    def SetWiFi(self, value, qualifier):

        WiFiCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x04\xCF'
        self.__SetHelper('WiFi', WiFiCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=19200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
