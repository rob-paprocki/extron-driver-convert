from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = 0x81
        self.Models = {}

        self.Commands = {
            'Focus': {'Status': {}},
            'PanTilt': {'Parameters': ['Pan Speed', 'Tilt Speed'], 'Status': {}},
            'Preset': {'Parameters': ['Action'], 'Status': {}},
            'PresetFraming': {'Status': {}},
            'Reboot': {'Status': {}},
            'TrackingMode': {'Status': {}},
            'WhiteBalance': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 7:
            self._DeviceID = 0x80 + int(value)
        else:
            print('Invalid Device ID Parameter.')

    def SetHeader(self, commandstring, type):
        if self.ConnectionType == 'Serial':
            return commandstring
        else:  # Not deleting type check to support status if Aver fix the firmware
            if type == 'Set':
                return b''.join([b'\x01\x00\x00', pack('B', len(commandstring)), b'\x00\x00\x00\x01', commandstring])
            else:
                return b''.join([b'\x01\x10\x00', pack('B', len(commandstring)), b'\x00\x00\x00\x01', commandstring])

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Manual': 0x03,
            'Auto': 0x02,
        }

        if value in ValueStateValues:
            FocusCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x38, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetPanTilt(self, value, qualifier):

        ValueStateValues = {
            'Stop': 0x0303,
            'Up': 0x0301,
            'Down': 0x0302,
            'Left': 0x0103,
            'Right': 0x0203,
            'Up Left': 0x0101,
            'Up Right': 0x0201,
            'Down Left': 0x0102,
            'Down Right': 0x0202,
        }

        pan_speed = qualifier['Pan Speed']
        tilt_speed = qualifier['Tilt Speed']
        if 0 <= pan_speed <= 15 and 0 <= tilt_speed <= 15 and value in ValueStateValues:
            if value == 'Stop':
                PanTiltCmdString = self.SetHeader(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, 0x00, 0x00, ValueStateValues[value], 0xFF), 'Set')
            else:
                PanTiltCmdString = self.SetHeader(pack('>6BHB', self._DeviceID, 0x01, 0x06, 0x01, pan_speed, tilt_speed, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPreset(self, value, qualifier):

        ActionStates = {
            'Save': 0x01,
            'Recall': 0x02
        }

        ValueConstraints = {
            'Min': 0,
            'Max': 127
        }

        action_val = qualifier['Action']
        if ValueConstraints['Min'] <= int(value) <= ValueConstraints['Max'] and action_val in ActionStates:
            PresetCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x3F, ActionStates[action_val], int(value), 0xFF), 'Set')
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetPresetFraming(self, value, qualifier):

        PresetFramingCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x7D, 0x06, 0x00, 0xFF), 'Set')
        self.__SetHelper('PresetFraming', PresetFramingCmdString, value, qualifier)

    def SetReboot(self, value, qualifier):

        RebootCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x00, 0x00, 0xFF), 'Set')
        self.__SetHelper('Reboot', RebootCmdString, value, qualifier)

    def SetTrackingMode(self, value, qualifier):

        ValueStateValues = {
            'Disable': 0x01,
            'Auto Framing': 0x02,
            'Manual Framing': 0x03
        }

        if value in ValueStateValues:
            TrackingModeCmdString = self.SetHeader(pack('7B', self._DeviceID, 0x01, 0x04, 0x7D, ValueStateValues[value], 0x00, 0xFF), 'Set')
            self.__SetHelper('TrackingMode', TrackingModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTrackingMode')

    def SetWhiteBalance(self, value, qualifier):

        ValueStateValues = {
            'Manual': 0x05,
            'Auto': 0x00,
        }

        if value in ValueStateValues:
            WhiteBalanceCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x35, ValueStateValues[value], 0xFF), 'Set')
            self.__SetHelper('WhiteBalance', WhiteBalanceCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetWhiteBalance')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Stop': 0x00,
            'Tele': 0x20,
            'Wide': 0x30
        }

        if value in ValueStateValues:
            ZoomCmdString = self.SetHeader(pack('6B', self._DeviceID, 0x01, 0x04, 0x07, ValueStateValues[value], 0xFF), 'Set')
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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