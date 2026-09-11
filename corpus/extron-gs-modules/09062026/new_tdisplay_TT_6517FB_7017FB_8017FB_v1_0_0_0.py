from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoImage': {'Status': {}},
            'Capture': {'Status': {}},
            'ChildLock': {'Status': {}},
            'ChildLockMode': {'Status': {}},
            'EcoMode': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Keypad': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mute': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
            'Whiteboard': {'Status': {}},
            'WiFi': {'Status': {}},
        }


    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x20\xCF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetCapture(self, value, qualifier):

        CaptureCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x1F\xCF'
        self.__SetHelper('Capture', CaptureCmdString, value, qualifier)

    def SetChildLock(self, value, qualifier):

        ChildLockCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x57\xCF'
        self.__SetHelper('ChildLock', ChildLockCmdString, value, qualifier)

    def SetChildLockMode(self, value, qualifier):

        ChildLockModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x58\xCF'
        self.__SetHelper('ChildLockMode', ChildLockModeCmdString, value, qualifier)

    def SetEcoMode(self, value, qualifier):

        ValueStateValues = {
            'Standard': b'\x00',
            'Eco': b'\x01',
            'Auto': b'\x02'
        }

        EcoModeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x06' + ValueStateValues[value] + b'\xCF'
        self.__SetHelper('EcoMode', EcoModeCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x3B\xCF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI 1': b'\x0A',
            'HDMI 2': b'\x0B',
            'HDMI 3': b'\x0C',
            'HDMI 4': b'\x51',
            'DisplayPort': b'\x56',
            'VGA': b'\x0D',
            'AV': b'\x11',
            'OPS': b'\x38'
        }

        InputCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01' + ValueStateValues[value] + b'\xCF'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '0': b'\x2A',
            '1': b'\x21',
            '2': b'\x22',
            '3': b'\x23',
            '4': b'\x24',
            '5': b'\x25',
            '6': b'\x26',
            '7': b'\x27',
            '8': b'\x28',
            '9': b'\x29'
        }

        KeypadCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01' + ValueStateValues[value] + b'\xCF'
        self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x2E',
            'Down': b'\x2F',
            'Left': b'\x2C',
            'Right': b'\x2D',
            'Enter': b'\x2B',
            'Menu': b'\x1B',
            'Page Up': b'\x13',
            'Page Down': b'\x14',
            'Home': b'\x1C',
            'Return': b'\x1D'
        }

        MenuNavigationCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01' + ValueStateValues[value] + b'\xCF'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01\x02\xCF'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x00',
            'Off': b'\x01'
        }

        PowerCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x01' + ValueStateValues[value] + b'\xCF'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x7F\x08\x99\xA2\xB3\xC4\x02\xFF\x05' + value.to_bytes(1, 'big') + b'\xCF'
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
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
