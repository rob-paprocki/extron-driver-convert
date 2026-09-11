from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:

    def __init__(self):

        self.Unidirectional = 'False'
        self.connectionCounter = 15
        self.DefaultResponseTimeout = 0.3
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'CameraSelect': {'Status': {}},
            'HomeCamera': {'Status': {}},
            'MoveCamera': {'Status': {}},
            'Power': {'Status': {}},
            'Preset': {'Status': {}},
            'Preview': {'Status': {}},
            'Program': {'Status': {}},
            'Rescan': {'Status': {}},
            'ResetVideo': {'Status': {}},
            'SaveConfig': {'Status': {}},
            'Store': {'Status': {}},
            'SystemMode': {'Status': {}},
            'Take': {'Status': {}},
            'Zoom': {'Parameters': ['Zoom Speed'], 'Status': {}}
        }               

    def SetCameraSelect(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        if 1 <= int(value) <= 6:
            CameraSelectCmdString = 'Camera {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('CameraSelect', CameraSelectCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetHomeCamera(self, value, qualifier):

        HomeCameraCmdString = 'Home\r'
        self.__SetHelper('HomeCamera', HomeCameraCmdString, value, qualifier)

    def SetMoveCamera(self, value, qualifier):

        ValueStateValues = {
            'Up': 'Up',
            'Down': 'Down',
            'Left': 'Left',
            'Right': 'Right',
            'Stop': 'Stop'
        }
        if value in ValueStateValues:
            MoveCameraCmdString = 'Move {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('MoveCamera', MoveCameraCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 'On',
            'Off': 'Off'
        }

        if value in ValueStateValues:
            PowerCmdString = 'Power {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            '8': '8',
            '9': '9',
            '10': '10',
            '11': '11',
            '12': '12'
        }

        if 1 <= int(value) <= 12:
            PresetCmdString = 'Prset {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetPreview(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        if 1 <= int(value) <= 6:
            PreviewCmdString = 'PrevIn {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Preview', PreviewCmdString, value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def SetProgram(self, value, qualifier):

        ValueStateValues = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6'
        }

        if 1 <= int(value) <= 6:
            ProgramCmdString = 'ProgIn {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('Program', ProgramCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetRescan(self, value, qualifier):

        RescanCmdString = 'Rescan\r'
        self.__SetHelper('Rescan', RescanCmdString, value, qualifier)

    def SetResetVideo(self, value, qualifier):

        ResetVideoCmdString = 'ResetVideo\r'
        self.__SetHelper('ResetVideo', ResetVideoCmdString, value, qualifier)

    def SetSaveConfig(self, value, qualifier):

        SaveConfigCmdString = 'SaveConfig\r'
        self.__SetHelper('SaveConfig', SaveConfigCmdString, value, qualifier)

    def SetStore(self, value, qualifier):

        if 1 <= int(value) <= 138:
            StoreCmdString = 'Store {0}\r'.format(value)
            self.__SetHelper('Store', StoreCmdString, value, qualifier)
        else:
            self.Dicard('Invalid Command')

    def SetSystemMode(self, value, qualifier):

        ValueStateValues = {
            'Auto': 'Auto',
            'Manual': 'Manual'
        }

        if value in ValueStateValues:
            SystemModeCmdString = 'SysMode {0}\r'.format(ValueStateValues[value])
            self.__SetHelper('SystemMode', SystemModeCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetTake(self, value, qualifier):

        TakeCmdString = 'Take\r'
        self.__SetHelper('Take', TakeCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ZoomSpeedStates = {
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
            '5': '5',
            '6': '6',
            '7': '7',
            'Default': ''
        }

        ValueStateValues = {
            'In': 'In',
            'Out': 'Out',
            'Stop': 'Stop'
        }

        if qualifier['Zoom Speed'] in ZoomSpeedStates and value in ValueStateValues:

            if qualifier['Zoom Speed'] == 'Default':
                ZoomCmdString = 'Zoom {0}\r'.format(ValueStateValues[value])
            else:
                ZoomCmdString = 'Zoom {0}, {1}\r'.format(ValueStateValues[value], ZoomSpeedStates[qualifier['Zoom Speed']])

            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Model=None):
        SerialInterface.__init__(self, Host, Port, Baud, Data, Parity, Stop, FlowControl, CharDelay)
        self.ConnectionType = 'Serial'
        DeviceClass.__init__(self)
        # Check if Model belongs to a subclass
        if len(self.Models) > 0:
            if Model not in self.Models:
                print('Model mismatch')
            else:
                self.Models[Model]()


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
