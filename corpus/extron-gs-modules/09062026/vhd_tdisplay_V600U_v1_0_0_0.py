from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        
        self._DeviceID = b'\x81'

        self.Commands = {
            'AutoFocus': {'Status': {}},
            'Focus': {'Parameters': ['Focus Speed'], 'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'RecallPreset': {'Status': {}},
            'SavePreset': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
    
        if self.ConnectionType == 'Ethernet':
            self._DeviceID = b'\x81'
        else:
            if 1 <= int(value) <= 7:
                self._DeviceID = pack('B', 0x80 + int(value))

    def SetAutoFocus(self, value, qualifier):

        ValueStateValues = {
            'Auto': b'\x02',
            'Manual': b'\x03'
        }

        AutoFocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x38', ValueStateValues[value], b'\xFF'])
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        FocusSpeedConstraints = {
            'Min': 0,
            'Max': 7
        }

        ValueStateValues = {
            'Near': 0x30,
            'Far': 0x20,
            'Stop': 0x00
        }

        focus_spd = int(qualifier['Focus Speed'])
        if FocusSpeedConstraints['Min'] <= focus_spd <= FocusSpeedConstraints['Max']:
            if value == 'Stop':
                focus_spd = 0x00
            else:
                focus_spd += ValueStateValues[value]
            FocusCmdString = b''.join([self._DeviceID, b'\x01\x04\x08', pack('B', focus_spd), b'\xFF'])
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        PanSpeedConstraints = {
            'Min': 1,
            'Max': 24
        }

        TiltSpeedConstraints = {
            'Min': 1,
            'Max': 20
        }

        ValueStateValues = {
            'Up': b'\x03\x01',
            'Down': b'\x03\x02',
            'Left': b'\x01\x03',
            'Right': b'\x02\x03',
            'Up Left': b'\x01\x01',
            'Up Right': b'\x02\x01',
            'Down Left': b'\x01\x02',
            'Down Right': b'\x02\x02',
            'Stop': b'\x03\x03',
            'Home': b''.join([self._DeviceID, b'\x01\x06\x04\xFF'])
        }

        pan_spd = int(qualifier['Pan Speed'])
        tilt_spd = int(qualifier['Tilt Speed'])
        if (PanSpeedConstraints['Min'] <= pan_spd <= PanSpeedConstraints['Max'] and
                TiltSpeedConstraints['Min'] <= tilt_spd <= TiltSpeedConstraints['Max']):
            if value == 'Home':
                PanTiltCmdString = ValueStateValues[value]
            else:
                PanTiltCmdString = b''.join([b'\x81\x01\x06\x01', pack('BB', pan_spd, tilt_spd),
                                             ValueStateValues[value], b'\xFF'])
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetRecallPreset(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            RecallPresetCmdString = b''.join([b'\x81\x01\x04\x3F\x02', pack('B', int(value)), b'\xFF'])
            self.__SetHelper('RecallPreset', RecallPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRecallPreset')

    def SetSavePreset(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max']:
            SavePresetCmdString = b''.join([b'\x81\x01\x04\x3F\x01', pack('B', int(value)), b'\xFF'])
            self.__SetHelper('SavePreset', SavePresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSavePreset')

    def SetZoom(self, value, qualifier):

        ZoomSpeedConstraints = {
            'Min': 0,
            'Max': 7
        }

        ValueStateValues = {
            'Tele': 0x20,
            'Wide': 0x30,
            'Stop': 0x00
        }

        zoom_spd = int(qualifier['Zoom Speed'])
        if ZoomSpeedConstraints['Min'] <= zoom_spd <= ZoomSpeedConstraints['Max']:
            if value == 'Stop':
                zoom_spd = ValueStateValues[value]
            else:
                zoom_spd += ValueStateValues[value]
            ZoomCmdString = b''.join([b'\x81\x01\x04\x07', pack('B', zoom_spd), b'\xFF'])
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
