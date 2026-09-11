from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'VolumeStep': {'Status': {}},
        }

    def CheckSumCalc(self, commandstring):
        command = b'\x08\x22' + commandstring
        checksum = sum(command)
        checksum = checksum ^ 0xFFFF
        checksum = checksum + 1
        checksum = checksum & 0xFF
        return command + pack('B', checksum)

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '16:9': b'\x00',
            '4:3': b'\x04',
            'Fit to Screen': b'\x05',
            'Zoom': b'\x01'
        }

        AspectRatioCmdString = b'\x0B\x0A\x01' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x02\x00\x00\x00'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'TV': b'\x00\x00',
            'AV': b'\x01\x00',
            'Component': b'\x03\x00',
            'HDMI 1': b'\x05\x00',
            'HDMI 2': b'\x05\x01',
            'HDMI 3': b'\x05\x02'
        }

        InputCmdString = b'\x0A\x00' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x1A',
            'Up': b'\x60',
            'Down': b'\x61',
            'Right': b'\x62',
            'Left': b'\x65',
            'Enter': b'\x68',
            'Return': b'\x58',
            'Exit': b'\x2D'
        }

        MenuNavigationCmdString = b'\x0D\x00\x00' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Dynamic': b'\x00',
            'Standard': b'\x01',
            'Natural': b'\x03',
            'Movie': b'\x02'
        }

        PictureModeCmdString = b'\x0B\x00\x00' + ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x02',
            'Off': b'\x01'
        }

        PowerCmdString = b'\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolumeStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x01\x00',
            'Down': b'\x02\x00'
        }

        VolumeStepCmdString = b'\x01\x00' + ValueStateValues[value]
        self.__SetHelper('VolumeStep', VolumeStepCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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


class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='TCP', ServicePort=0, Model=None):
        EthernetClientInterface.__init__(self, Hostname, IPPort, Protocol, ServicePort)
        self.ConnectionType = 'Ethernet'
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