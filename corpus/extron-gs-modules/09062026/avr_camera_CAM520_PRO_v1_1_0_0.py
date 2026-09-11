from extronlib.interface import SerialInterface, EthernetClientInterface
from struct import pack


class DeviceSerialClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'TrackingMode': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 8:
            value = 0x80 + int(value)
            self._DeviceID = bytes([value])
        else:
            self.Error(['Device ID Out of Range'])

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Stop': b'\x03\x03'
        }

        if 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 24 and value in ValueStateValues:
            PanTiltCmdString = self.DeviceID + b'\x01\x06\x01' + bytes([qualifier['Pan Speed'], qualifier['Tilt Speed']]) + ValueStateValues[value] + b'\xFF'
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        if value in ValueStateValues:
            PowerCmdString = self.DeviceID + ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Recall': b'\x01\x04\x3F\x02',
            'Save': b'\x01\x04\x3F\x01'
        }

        if 1 <= int(value) <= 128 and qualifier['Action'] in ActionStates:
            PresetCmdString = self.DeviceID + ActionStates[qualifier['Action']] + bytes([int(value) - 1]) + b'\xFF'
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x7D\x02\x00\xFF',
            'Off': b'\x01\x04\x7D\x03\x00\xFF'
        }

        if value in ValueStateValues:
            TrackingModeCmdString = self.DeviceID + ValueStateValues[value]
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def SetZoom(self, value, qualifier):

        if 0 <= qualifier['Speed'] <= 7 and value in ['Tele', 'Wide', 'Stop']:
            ValueStateValues = {
                'Tele': 0x20 + qualifier['Speed'],
                'Wide': 0x30 + qualifier['Speed'],
                'Stop': 0x00
            }

            ZoomCmdString = self.DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')

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
        self._DeviceID = b'\x81'
        self.Models = {}

        self.Commands = {
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'TrackingMode': {'Status': {}},
            'Zoom': {'Parameters': ['Speed'], 'Status': {}},
        }


    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 8:
            value = 0x80 + int(value)
            self._DeviceID = bytes([value])
        else:
            self.Error(['Device ID Out of Range'])

    def SetHeader(self, commandstring):
        return b'\x01\x00\x00' + pack('B', len(commandstring)) + b'\x00\x00\x00\x01' + commandstring

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Stop': b'\x03\x03'
        }

        if 1 <= qualifier['Pan Speed'] <= 24 and 1 <= qualifier['Tilt Speed'] <= 24 and value in ValueStateValues:
            PanTiltCmdString = self.SetHeader(self.DeviceID + b'\x01\x06\x01' + bytes([qualifier['Pan Speed'], qualifier['Tilt Speed']]) + ValueStateValues[value] + b'\xFF')
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x00\x02\xFF',
            'Off': b'\x01\x04\x00\x03\xFF'
        }

        if value in ValueStateValues:
            PowerCmdString = self.SetHeader(self.DeviceID + ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Recall': b'\x01\x04\x3F\x02',
            'Save': b'\x01\x04\x3F\x01'
        }

        if 1 <= int(value) <= 128 and qualifier['Action'] in ActionStates:
            PresetCmdString = self.SetHeader(self.DeviceID + ActionStates[qualifier['Action']] + bytes([int(value) - 1]) + b'\xFF')
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x01\x04\x7D\x02\x00\xFF',
            'Off': b'\x01\x04\x7D\x03\x00\xFF'
        }

        if value in ValueStateValues:
            TrackingModeCmdString = self.SetHeader(self.DeviceID + ValueStateValues[value])
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def SetZoom(self, value, qualifier):

        if 0 <= qualifier['Speed'] <= 7 and value in ['Tele', 'Wide', 'Stop']:
            ValueStateValues = {
                'Tele': 0x20 + qualifier['Speed'],
                'Wide': 0x30 + qualifier['Speed'],
                'Stop': 0x00
            }

            ZoomCmdString = self.SetHeader(self.DeviceID + b'\x01\x04\x07' + bytes([ValueStateValues[value]]) + b'\xFF')
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetZoom')


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(b'\x02\x00\x00\x01\x00\x00\x00\x00\x01')
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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
