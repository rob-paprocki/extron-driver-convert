from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack


class DeviceClass:

    def __init__(self):

        self._DeviceID = 1
        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AutoImage': {'Status': {}},
            'AVMute': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'LaserPowerMode': {'Status': {}},
            'LensShift': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PIPInput': {'Status': {}},
            'PIPMode': {'Status': {}},
            'PIPPosition': {'Status': {}},
            'PIPSize': {'Status': {}},
            'Power': {'Status': {}},
            'Saturation': {'Status': {}},
            'Sharpness': {'Status': {}},
            'Tint': {'Status': {}},
            'Zoom': {'Status': {}}
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        self._DeviceID = value

    def CalCRC(self, Data):
        Crc = 0
        for i in range(0, len(Data)):
            Crc = Crc + Data[i]
        return (Crc % 256)

    def escaped(self, Data):
        d = 0
        List = []
        Escaped = {
            0x80: [0x80, 0x00],
            0xFE: [0x80, 0x7E],
            0xFF: [0x80, 0x7F]
        }
        for d in Data:
            if d in Escaped:
                List.append(Escaped[d][0])
                List.append(Escaped[d][1])
            else:
                List.append(d)
        return List

    def conversion(self, List):
        cmdStr = b''
        for i in range(len(List)):
            cmdStr += pack('>B', List[i])
        return cmdStr

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            '4:3': 0x00,
            '16:10': 0x01,
            'Native': 0x02,
            'Auto': 0x03
        }

        temp = [self._DeviceID, 0x20, 0x0B, 0xC0, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        AspectRatioCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        temp = [self._DeviceID, 0x20, 0x16]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        AutoImageCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetAVMute(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        temp = [self._DeviceID, 0x20, 0xA9, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        AVMuteCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('AVMute', AVMuteCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = [self._DeviceID, 0x20, 0x02, value]
            temp.append(self.CalCRC(temp))
            list = self.escaped(temp)
            BrightnessCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetContrast(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = [self._DeviceID, 0x20, 0x01, value]
            temp.append(self.CalCRC(temp))
            list = self.escaped(temp)
            ContrastCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'In': 0x01,
            'Out': 0x00
        }

        temp = [self._DeviceID, 0xF4, 0x83, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        FocusCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        temp = [self._DeviceID, 0x20, 0xAC, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        FreezeCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 0x00,
            'VGA': 0x01,
            'DVI': 0x02,
            'BNC': 0x03,
            'CVBS': 0x04
        }

        temp = [self._DeviceID, 0x33, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        InputCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLaserPowerMode(self, value, qualifier):

        ValueStateValues = {
            'Economic': 0x02,
            'Normal': 0x01,
            'Power': 0x06
        }

        temp = [self._DeviceID, 0x20, 0x98, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        LaserPowerModeCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('LaserPowerMode', LaserPowerModeCmdString, value, qualifier)

    def SetLensShift(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x00,
            'Down': 0x01,
            'Left': 0x02,
            'Right': 0x03
        }

        if value == 'Center':
            temp = [self._DeviceID, 0xF4, 0x88]
        else:
            temp = [self._DeviceID, 0xF4, 0x81, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        LensShiftCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('LensShift', LensShiftCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': 0x04,
            'Down': 0x05,
            'Left': 0x07,
            'Right': 0x06,
            'Menu': 0x0A,
            'Enter': 0x0B
        }

        temp = [self._DeviceID, 0x30, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        MenuNavigationCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Presentation': 0x00,
            'Video': 0x01,
            'Dicom': 0x02,
            'Bright': 0x03
        }

        temp = [self._DeviceID, 0x20, 0x15, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PictureModeCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPIPInput(self, value, qualifier):

        ValueStateValues = {
            'HDMI': 0x00,
            'VGA': 0x01,
            'DVI': 0x02,
            'BNC': 0x03,
            'CVBS': 0x04
        }

        temp = [self._DeviceID, 0xA0, 0x02, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PIPInputCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('PIPInput', PIPInputCmdString, value, qualifier)

    def SetPIPMode(self, value, qualifier):

        ValueStateValues = {
            'On': 0x01,
            'Off': 0x00
        }

        temp = [self._DeviceID, 0xA0, 0x01, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PIPModeCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('PIPMode', PIPModeCmdString, value, qualifier)

    def SetPIPPosition(self, value, qualifier):

        ValueStateValues = {
            'Top Left': 0x00,
            'Top Right': 0x01,
            'Bottom Left': 0x02,
            'Bottom Right': 0x03
        }

        temp = [self._DeviceID, 0xA0, 0x04, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PIPPositionCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('PIPPosition', PIPPositionCmdString, value, qualifier)

    def SetPIPSize(self, value, qualifier):

        ValueStateValues = {
            'Small': 0x00,
            'Medium': 0x01,
            'Large': 0x02
        }

        temp = [self._DeviceID, 0xA0, 0x03, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PIPSizeCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('PIPSize', PIPSizeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': 0x03,
            'Off': 0x00
        }

        temp = [self._DeviceID, 0x58, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        PowerCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetSaturation(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = [self._DeviceID, 0x20, 0x03, value]
            temp.append(self.CalCRC(temp))
            list = self.escaped(temp)
            SaturationCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Saturation', SaturationCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetSharpness(self, value, qualifier):

        ValueConstraints = {
            'Min': -7,
            'Max': 7
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = [self._DeviceID, 0x20, 0x05, value + 7]
            temp.append(self.CalCRC(temp))
            list = self.escaped(temp)
            SharpnessCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Sharpness', SharpnessCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetTint(self, value, qualifier):

        ValueConstraints = {
            'Min': 0,
            'Max': 255
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            temp = [self._DeviceID, 0x20, 0x04, value]
            temp.append(self.CalCRC(temp))
            list = self.escaped(temp)
            TintCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
            self.__SetHelper('Tint', TintCmdString, value, qualifier)
        else:
            print('Invalid Command')

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'In': 0x00,
            'Out': 0x01
        }

        temp = [self._DeviceID, 0xF4, 0x82, ValueStateValues[value]]
        temp.append(self.CalCRC(temp))
        list = self.escaped(temp)
        ZoomCmdString = b'\xFE' + self.conversion(list) + b'\xFF'
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)


    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

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
