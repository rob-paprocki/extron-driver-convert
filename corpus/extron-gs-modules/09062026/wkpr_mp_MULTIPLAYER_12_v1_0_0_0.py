from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mode': {'Status': {}},
            'Mute': {'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Sleep': {'Status': {}},
            'Standby': {'Status': {}},
            'Transport': {'Status': {}},
            'Tuner': {'Status': {}},
            'Volume': {'Status': {}}
        }        

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Menu': b'\x19',
            'Up': b'\x1E',
            'Down': b'\x1F',
            'Left': b'\x22',
            'Right': b'\x26',
            'Enter': b'\x1C'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMode(self, value, qualifier):

        ValueStateValues = {
            'Internet Radio': b'\x3F',
            'Music Player': b'\x40',
            'DAB': b'\x41',
            'FM': b'\x42',
            'Aux In': b'\x43'
        }

        ModeCmdString = ValueStateValues[value]
        self.__SetHelper('Mode', ModeCmdString, value, qualifier)

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x2E'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPresetRecall(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x02',
            '2': b'\x03',
            '3': b'\x04',
            '4': b'\x05',
            '5': b'\x06',
            '6': b'\x33',
            '7': b'\x34',
            '8': b'\x35',
            '9': b'\x36',
            '10': b'\x37'
        }

        PresetRecallCmdString = ValueStateValues[value]
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        ValueStateValues = {
            '1': b'\x07',
            '2': b'\x0A',
            '3': b'\x0B',
            '4': b'\x0E',
            '5': b'\x0F',
            '6': b'\x3A',
            '7': b'\x3B',
            '8': b'\x3C',
            '9': b'\x3D',
            '10': b'\x3E'
        }

        PresetSaveCmdString = ValueStateValues[value]
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetSleep(self, value, qualifier):

        SleepCmdString = b'\x18'
        self.__SetHelper('Sleep', SleepCmdString, value, qualifier)

    def SetStandby(self, value, qualifier):

        StandbyCmdString = b'\x01'
        self.__SetHelper('Standby', StandbyCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Play/Stop': b'\x2B',
            'Rewind': b'\x30',
            'Previous': b'\x2F',
            'Fast Forward': b'\x31',
            'Next': b'\x32',
            'Repeat': b'\x27',
            'Shuffle': b'\x2A'
        }

        TransportCmdString = ValueStateValues[value]
        self.__SetHelper('Transport', TransportCmdString, value, qualifier)

    def SetTuner(self, value, qualifier):

        ValueStateValues = {
            'Scan': b'\x1C',
            'Tunning Up': b'\x1E',
            'Tunning Down': b'\x1F',
            'Auto Scan Up': b'\x20',
            'Auto Scan Down': b'\x21'
        }

        TunerCmdString = ValueStateValues[value]
        self.__SetHelper('Tuner', TunerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x2D',
            'Down': b'\x2C'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

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
