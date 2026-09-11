from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.DeviceID = '1'

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'Focus': {'Status': {}},
            'Iris': {'Status': {}},
            'Pan': {'Parameters': ['Pan Speed'], 'Status': {}},
            'PresetRecall': {'Status': {}},
            'PresetSave': {'Status': {}},
            'Tilt': {'Parameters': ['Tilt Speed'], 'Status': {}},
            'Zoom': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if 1 <= int(value) <= 64:
            self._DeviceID = (value.zfill(2)).encode()
        else:
            print('DeviceID is out of range')


    def SetFocus(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 22
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempVal = str(value).zfill(2)
            FocusCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCN:20214B1:2022\x30' + bytes(tempVal[0], 'utf-8') + b'\x38\x3A\x32\x30\x32\x32' + bytes(tempVal[1], 'utf-8') + b'\x30\x31\x03'
            self.__SetHelper('Focus', FocusCmdString, value, qualifier)
        else:
            print('Invalid Command for SetFocus')

    def SetIris(self, value, qualifier):

        ValueStateValues = {
            'Open': b'8',
            'Close': b'9'
        }

        IrisCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCF:00219F0:0022A' + ValueStateValues[value] + b'0\x03'
        self.__SetHelper('Iris', IrisCmdString, value, qualifier)

    def SetPan(self, value, qualifier):

        panspeed = qualifier['Pan Speed']

        ValueStateValues = {
            'Left': b'368',
            'Right': b'36C',
            'Stop': b'364'
        }

        if 0 <= int(panspeed) <= 7:
            PanCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCF:2021' + ValueStateValues[value] + b'\x3A2022' + bytes(panspeed, 'utf-8') + b'0' + b'\x30\x03'
            self.__SetHelper('Pan', PanCmdString, value, qualifier)
        else:
            print('Invalid Command for SetPan')

    def SetPresetRecall(self, value, qualifier):

        PresetRecallCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCF:00219F0:0022' + bytes(hex((int(value) - 1))[2:].zfill(2), 'utf-8').upper() + b'0\x03'
        self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)

    def SetPresetSave(self, value, qualifier):

        PresetSaveCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCF:00219F0:0022' + bytes(hex(int(value) + 99)[2:], 'utf-8').upper() + b'0\x03'
        self.__SetHelper('PresetSave', PresetSaveCmdString, value, qualifier)

    def SetTilt(self, value, qualifier):

        tiltspeed = qualifier['Tilt Speed']

        ValueStateValues = {
            'Up': b'36A',
            'Down': b'36E',
            'Stop': b'364'
        }

        if 0 <= int(tiltspeed) <= 7:
            TiltCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCF:2021' + ValueStateValues[value] + b'\x3A20220' + bytes(tiltspeed, 'utf-8') + b'\x30\x03'
            self.__SetHelper('Tilt', TiltCmdString, value, qualifier)
        else:
            print('Invalid Command for SetTilt')

    def SetZoom(self, value, qualifier):

        ValueConstraints = {
            'Min': 1,
            'Max': 22
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            tempVal = str(value).zfill(2)
            ZoomCmdString = b'\x02AD' + self._DeviceID + b'\x3BGCN:20214B0:2022\x30' + bytes(tempVal[0], 'utf-8') + b'\x38\x3A\x32\x30\x32\x32' + bytes(tempVal[1], 'utf-8') + b'\x30\x31\x03'
            self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)
        else:
            print('Invalid Command for SetZoom')

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
