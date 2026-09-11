from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog
from struct import pack


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoFocus': {'Parameters': ['Device ID'], 'Status': {}},
            'AutoIris': {'Parameters': ['Device ID'], 'Status': {}},
            'Focus': {'Parameters': ['Device ID'], 'Status': {}},
            'Iris': {'Parameters': ['Device ID'], 'Status': {}},
            'PanTilt': {'Parameters': ['PanTiltSpeed', 'Device ID'], 'Status': {}},
            'PresetRecall': {'Parameters': ['Device ID'], 'Status': {}},
            'PresetSave': {'Parameters': ['Device ID'], 'Status': {}},
            'SetFocusSpeed': {'Parameters': ['Device ID'], 'Status': {}},
            'SetZoomSpeed': {'Parameters': ['Device ID'], 'Status': {}},
            'Zoom': {'Parameters': ['Device ID'], 'Status': {}},
        }

    def SetAutoFocus(self, value, qualifier):

        AutoFocusStateValues = {
            'On': 0x01,
            'Off': 0x02,
            'Auto': 0x00,
        }
        if 0 <= int(qualifier['Device ID']) <= 31:
            ckSum = int(qualifier['Device ID']) + AutoFocusStateValues[value] + 0x2B & 255
            AutoFocusCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x2B, 0x00, AutoFocusStateValues[value], ckSum)
            self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoFocus')

    def SetAutoIris(self, value, qualifier):

        AutoIrisStateValues = {
            'On': 0x01,
            'Off': 0x02,
            'Auto': 0x00,
        }
        if 0 <= int(qualifier['Device ID']) <= 31:
            ckSum = int(qualifier['Device ID']) + AutoIrisStateValues[value] + 0x2D & 255
            AutoIrisCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x2D, 0x00, AutoIrisStateValues[value], ckSum)
            self.__SetHelper('AutoIris', AutoIrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAutoIris')

    def SetFocus(self, value, qualifier):

        if 0 <= int(qualifier['Device ID']) <= 31:
            if value == 'Far':
                ckSum = int(qualifier['Device ID']) + 0x80 & 255
                FocusCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x80, 0x00, 0x00, ckSum)
            elif value == 'Near':
                ckSum = int(qualifier['Device ID']) + 0x01 & 255
                FocusCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x01, 0x00, 0x00, 0x00, ckSum)
            elif value == 'Stop':
                ckSum = int(qualifier['Device ID']) & 255
                FocusCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x00, 0x00, 0x00, ckSum)
            if FocusCmdString:
                self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        IrisStateValues = {
            'Open': 0x02,
            'Close': 0x04,
        }
        if 0 <= int(qualifier['Device ID']) <= 31:
            ckSum = int(qualifier['Device ID']) + IrisStateValues[value] & 255
            IrisCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), IrisStateValues[value], 0x00, 0x00, 0x00, ckSum)
            self.__SetHelper('Iris', IrisCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetIris')

    def SetPanTilt(self, value, qualifier):

        PanTiltStateValues = {
            'Up': 0x08,
            'Down': 0x10,
            'Left': 0x04,
            'Right': 0x02,
            'Stop': 0x00,
        }
        if 0 <= int(qualifier['Device ID']) <= 31:
            if qualifier['PanTiltSpeed'] == 'Turbo':
                ckSum = int(qualifier['Device ID']) + PanTiltStateValues[value] + 0xFF & 255
                if value == 'Left' or value == 'Right':
                    PanTiltCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, PanTiltStateValues[value], 0xFF, 0x00, ckSum)
                else:
                    PanTiltCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, PanTiltStateValues[value], 0x00, 0xFF, ckSum)
            elif 0 <= int(qualifier['PanTiltSpeed']) <= 63:
                ckSum = int(qualifier['Device ID']) + PanTiltStateValues[value] + int(qualifier['PanTiltSpeed']) & 255
                if value == 'Left' or value == 'Right':
                    PanTiltCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, PanTiltStateValues[value], int(qualifier['PanTiltSpeed']), 0x00, ckSum)
                else:
                    PanTiltCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, PanTiltStateValues[value], 0x00, int(qualifier['PanTiltSpeed']), ckSum)
            else:
                self.Discard('Invalid Command for SetPanTilt')

            if PanTiltCmdString:
                self.__SetHelper('PanTilt', PanTiltCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPanTilt')

    def SetPresetRecall(self, value, qualifier):

        if 0 <= int(qualifier['Device ID']) <= 31 and 1 <= int(value) <= 32:
            ckSum = int(qualifier['Device ID']) + int(value) + 0x07 & 255
            PresetRecallCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x07, 0x00, int(value), ckSum)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetPresetSave(self, value, qualifier):

        if 0 <= int(qualifier['Device ID']) <= 31 and 1 <= int(value) <= 32:
            ckSum = int(qualifier['Device ID']) + int(value) + 0x03 & 255
            PresetSaveCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x03, 0x00, int(value), ckSum)
            self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSave')

    def SetSetFocusSpeed(self, value, qualifier):

        if 0 <= int(qualifier['Device ID']) <= 31 and 0 <= int(value) <= 3:
            ckSum = int(qualifier['Device ID']) + int(value) + 0x27 & 255
            SetFocusSpeedCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x27, 0x00, int(value), ckSum)
            self.__SetHelper('SetFocusSpeed', SetFocusSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetFocusSpeed')

    def SetSetZoomSpeed(self, value, qualifier):

        if 0 <= int(qualifier['Device ID']) <= 31 and 0 <= int(value) <= 3:
            ckSum = int(qualifier['Device ID']) + int(value) + 0x25 & 255
            SetZoomSpeedCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, 0x25, 0x00, int(value), ckSum)
            self.__SetHelper('SetZoomSpeed', SetZoomSpeedCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetSetZoomSpeed')

    def SetZoom(self, value, qualifier):

        ZoomStateValues = {
            'Wide': 0x40,
            'Tele': 0x20,
            'Stop': 0x00,
        }
        if 0 <= int(qualifier['Device ID']) <= 31:
            ckSum = int(qualifier['Device ID']) + ZoomStateValues[value] & 255
            ZoomCmdString = pack('>BBBBBBB', 0xFF, int(qualifier['Device ID']), 0x00, ZoomStateValues[value], 0x00, 0x00, ckSum)
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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
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
