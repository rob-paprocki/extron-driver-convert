from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}
        self._DisplayID = 1

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'Input': {'Status': {}},
            'Menu': {'Status': {}},
            'Power': {'Status': {}},
            'Reset': {'Status': {}},
            'Volume': {'Status': {}}
        }

    @property
    def DisplayID(self):
        return self._DisplayID

    @DisplayID.setter
    def DisplayID(self, value):
        if value == 'Broadcast':
            self._DisplayID = 0
        elif 1 <= int(ID) <= 255:
            self._DisplayID = int(ID)

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = pack('>BBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x14, 0x00, 0x03)
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        AudioMuteCmdString = pack('>BBBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x13, 0x01, ValueStateValues[value], 0x03)
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': 0x00,
            'DVI': 0x01,
            'YPbPr': 0x02,
            'HDMI 1': 0x03,
            'HDMI 2': 0x04,
            'AV': 0x05,
            'USB 1': 0x06,
            'USB 2': 0x07
        }

        InputCmdString = pack('>BBBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x02, 0x01, ValueStateValues[value], 0x03)
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenu(self, value, qualifier):

        MenuCmdString = pack('>BBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x31, 0x00, 0x03)
        self.__SetHelper('Menu', MenuCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        PowerCmdString = pack('>BBBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x01, 0x01, ValueStateValues[value], 0x03)
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetReset(self, value, qualifier):

        ResetCmdString = pack('>BBBBBBB', 0x02, self._DisplayID, 0x00, 0xFF, 0x00, 0x00, 0x03)
        self.__SetHelper('Reset', ResetCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = pack('>BBBBBBBB', 0x02, self._DisplayID, 0x00, 0x00, 0x12, 0x01, value, 0x03)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        return response

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        if self.Unidirectional == 'True' or self._DisplayID == 0:
            self.Send(commandstring)
        else:
            res = self.SendAndWait(commandstring, self.DefaultResponseTimeout, deliTag='0x03')
            if not res:
                print('No Response')
                print('Invalid/unexpected response')
            else:
                res = self.__CheckResponseForErrors(command, res)

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
