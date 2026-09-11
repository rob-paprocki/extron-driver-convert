from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = '01'
        self.Models = {}

        self.Commands = {
            'ABTElectriscreenMaskControl': {'Parameters': ['Type'], 'Status': {}},
            'CineCurveVistaScopeMaskControl': {'Parameters': ['Type'], 'Status': {}},
            'DoorCloseOpen': {'Status': {}},
            'EMSNMaskControl': {'Parameters': ['Type'], 'Status': {}},
            'FourwayMaskControl': {'Parameters': ['Type'], 'Status': {}},
            'Home': {'Status': {}},
            'Preset': {'Status': {}},
            'ProgramPreset': {'Status': {}},
            'ScreenControl': {'Status': {}},
            'UltimateFourwayDirectorsChoiceMaskControl': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 4:
            self._DeviceID = '0' + value        

    def SetABTElectriscreenMaskControl(self, value, qualifier):

        TypeStates = {
            'Horizontal': 'B',
            'Vertical': 'B'
        }
        type_ = qualifier['Type']

        ValueStateValues = {
            'Up': 'U',
            'Down': 'D'
        }

        if type_ in TypeStates and value in ValueStateValues:
            ABTElectriscreenMaskControlCmdString = self._DeviceID + ValueStateValues[value] + TypeStates[type_] + '\r'
            self.__SetHelper('ABTElectriscreenMaskControl', ABTElectriscreenMaskControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetABTElectriscreenMaskControl')

    def SetCineCurveVistaScopeMaskControl(self, value, qualifier):

        TypeStates = {
            'Left': 'A',
            'Right': 'B'
        }
        type_ = qualifier['Type']

        ValueStateValues = {
            'Open': 'U',
            'Close': 'D'
        }

        if type_ in TypeStates and value in ValueStateValues:
            CineCurveVistaScopeMaskControlCmdString = self._DeviceID + ValueStateValues[value] + TypeStates[type_] + '\r'
            self.__SetHelper('CineCurveVistaScopeMaskControl', CineCurveVistaScopeMaskControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCineCurveVistaScopeMaskControl')

    def SetDoorCloseOpen(self, value, qualifier):

        DoorCloseOpenCmdString = self._DeviceID + 'DC\r'
        self.__SetHelper('DoorCloseOpen', DoorCloseOpenCmdString, value, qualifier)

    def SetEMSNMaskControl(self, value, qualifier):

        TypeStates = {
            'Top': 'A',
            'Bottom': 'B'
        }
        type_ = qualifier['Type']

        ValueStateValues = {
            'Up': 'U',
            'Down': 'D'
        }

        if type_ in TypeStates and value in ValueStateValues:
            EMSNMaskControlCmdString = self._DeviceID + ValueStateValues[value] + TypeStates[type_] + '\r'
            self.__SetHelper('EMSNMaskControl', EMSNMaskControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetEMSNMaskControl')

    def SetFourwayMaskControl(self, value, qualifier):

        TypeStates = {
            'Top': 'A',
            'Bottom': 'B',
            'Side': 'C'
        }
        type_ = qualifier['Type']

        ValueStateValues = {
            'Up': 'U',
            'Down': 'D'
        }

        if type_ in TypeStates and value in ValueStateValues:
            FourwayMaskControlCmdString = self._DeviceID + ValueStateValues[value] + TypeStates[type_] + '\r'
            self.__SetHelper('FourwayMaskControl', FourwayMaskControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetFourwayMaskControl')

    def SetHome(self, value, qualifier):

        HomeCmdString = self._DeviceID + 'M0\r'
        self.__SetHelper('Home', HomeCmdString, value, qualifier)

    def SetPreset(self, value, qualifier):

        ValueStateValues = {
            '1 (16:9)': '1',
            '2 (4:3)': '2',
            '3 (1.85)': '3',
            '4 (2.35)': '4',
            '5 (user 1)': '5',
            '6 (user 2)': '6',
            '7 (user 3)': '7',
            '8 (user 4)': '8',
            '9 (user 5)': '9'
        }

        if value in ValueStateValues:
            PresetCmdString = self._DeviceID + 'M' + ValueStateValues[value] + '\r'
            self.__SetHelper('Preset', PresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPreset')

    def SetProgramPreset(self, value, qualifier):

        if 1 <= int(value) <= 9:
            ProgramPresetCmdString = self._DeviceID + 'P' + value + '\r'
            self.__SetHelper('ProgramPreset', ProgramPresetCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetProgramPreset')

    def SetScreenControl(self, value, qualifier):

        ValueStateValues = {
            'Up': 'U',
            'Down': 'D'
        }

        if value in ValueStateValues:
            ScreenControlCmdString = self._DeviceID + ValueStateValues[value] + 'A\r'
            self.__SetHelper('ScreenControl', ScreenControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreenControl')

    def SetUltimateFourwayDirectorsChoiceMaskControl(self, value, qualifier):

        ValueStateValues = {
            'Top Mask Up': 'UA',
            'Top Mask Down': 'DA',
            'Bottom Mask Up': 'UB',
            'Bottom Mask Down': 'DB',
            'Left Mask In': 'DC',
            'Left Mask Out': 'UC',
            'Right Mask In': 'UD',
            'Right Mask Out': 'DD'
        }

        if value in ValueStateValues:
            UltimateFourwayDirectorsChoiceMaskControlCmdString = self._DeviceID + ValueStateValues[value] + '\r'
            self.__SetHelper('UltimateFourwayDirectorsChoiceMaskControl', UltimateFourwayDirectorsChoiceMaskControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetUltimateFourwayDirectorsChoiceMaskControl')

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
