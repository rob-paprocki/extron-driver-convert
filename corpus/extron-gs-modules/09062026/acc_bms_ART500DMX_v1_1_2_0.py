from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack


class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'SceneOperation': {'Parameters': ['Selection', 'Page'], 'Status': {}},
        }

    def SetSceneOperation(self, value, qualifier):

        SelectionStates = {
            'Play': 1,
            'Stop': 2,
            'Pause': 3,
            'Release': 4,
            'Reset': 5,
        }[qualifier['Selection']]

        PageStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            'I': '8',
            'J': '9'
        }[qualifier['Page']]

        if 1 <= int(value) <= 50:
            scene = 50 * int(PageStates) + int(value)
            SceneOperationCmdString = pack('>4B', SelectionStates, scene % 256, scene // 256, 255)
            self.__SetHelper('SceneOperation', SceneOperationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneOperation')

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


class DeviceEthernetClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'SceneOperation': {'Parameters': ['Selection', 'Page', 'Dimmer', 'Speed', 'R', 'G', 'B'], 'Status': {}},
            'SceneTrigger': {'Parameters': ['Page'], 'Status': {}},
        }

    def SetSceneOperation(self, value, qualifier):

        SelectionStates = {
            'Stop': '0',
            'Play': '1',
            'Release': '2',
            'Pause': '3',
            'Reset': '4',
            'Dimmer Set': '5',
            'Speed Set': '6',
            'Color Set': '7',
            'Black Out Off': '8',
            'Black Out On': '9'
        }[qualifier['Selection']]

        PageStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            'I': '8',
            'J': '9'
        }[qualifier['Page']]

        dimmer = qualifier['Dimmer']
        speed = qualifier['Speed']
        red = qualifier['R']
        green = qualifier['G']
        blue = qualifier['B']
        if int(value) in range(1, 51) and dimmer in range(201) and speed in range(601) and red in range(256) and green in range(256) and blue in range(256):
            scene = 50 * int(PageStates) + int(value)
            SceneOperationCmdString = pack('8s2h2B2h6B', b'Stick_3A', 109, scene, 0, int(SelectionStates), dimmer, speed, 0, 0, red, green, blue, 0)
            self.__SetHelper('SceneOperation', SceneOperationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSceneOperation')

    def SetSceneTrigger(self, value, qualifier):

        PageStates = {
            'A': '0',
            'B': '1',
            'C': '2',
            'D': '3',
            'E': '4',
            'F': '5',
            'G': '6',
            'H': '7',
            'I': '8',
            'J': '9'
        }[qualifier['Page']]

        scene = 50 * int(PageStates) + int(value)
        SceneOperationCmdString = pack('8s2h2B2h6B', b'Stick_3A', 109, scene, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0)
        self.__SetHelper('SceneOperation', SceneOperationCmdString, value, qualifier)

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


class SerialClass(SerialInterface, DeviceSerialClass):

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=2, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay, Mode)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class SerialOverEthernetClass(EthernetClientInterface, DeviceSerialClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Serial'
        DeviceSerialClass.__init__(self)
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


class EthernetClass(EthernetClientInterface, DeviceEthernetClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
        DeviceEthernetClass.__init__(self)
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
