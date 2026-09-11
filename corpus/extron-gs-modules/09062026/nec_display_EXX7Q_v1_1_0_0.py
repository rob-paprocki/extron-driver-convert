from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog, Timer
from binascii import hexlify

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = 0x41

        self.Models = {
            'E557Q': self.nec_10_4134_Others,
            'E327': self.nec_10_4134_E327,
            'E437Q': self.nec_10_4134_Others,
            'E507Q': self.nec_10_4134_Others,
            'E657Q': self.nec_10_4134_Others,
            }

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'ClosedCaption': {'Status': {}},
            'DigitalClosedCaption': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'PictureMode': {'Status': {}},
            'Power': {'Status': {}},
            'TVChannelCommand': {'Status': {}},
            'TVChannelStep': {'Status': {}},
            'Volume': {'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):

        if value == 'Broadcast':
            self._DeviceID = 0x2A
        elif 1 <= int(value) <= 100:
            self._DeviceID = 0x40 + int(value)

    def __calculate_checksum(self, command_string):

        checksum = 0
        for byte in command_string[1:]:
            checksum ^= byte
        return bytes([checksum])

    def __build_setstring(self, op_code_page, op_code, value):

        header = b'\x010' + bytes([self._DeviceID]) + b'0E0A'
        message = b'\x02' + op_code_page + op_code + b'00' + value + b'\x03'
        checksum = self.__calculate_checksum(header + message)
        delimiter = b'\r'
        return header + message + checksum + delimiter

    def keep_alive(self):
        command_string = b'\x010\x2A0A06\x0201D6\x03'
        checksum = self.__calculate_checksum(command_string)
        self.Send(command_string + checksum + b'\r')

    def SetAspectRatio(self, value, qualifier):

        ValueStateValues = {
            'Normal': b'01',
            'Full': b'02',
            'Wide': b'03',
            'Zoom': b'04',
            'Cinema': b'0A',
            'Auto': b'0B'
        }

        if value in ValueStateValues:
            AspectRatioCmdString = self.__build_setstring(b'02', b'70', ValueStateValues[value])
            self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')

    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'01',
            'Off': b'02'
        }

        if value in ValueStateValues:
            AudioMuteCmdString = self.__build_setstring(b'00', b'8D', ValueStateValues[value])
            self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAudioMute')

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = self.__build_setstring(b'00', b'1E', b'01')
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'01',
            'CC1': b'02',
            'CC2': b'03',
            'CC3': b'04',
            'CC4': b'05',
            'TT1': b'06',
            'TT2': b'07',
            'TT3': b'08',
            'TT4': b'09'
        }

        if value in ValueStateValues:
            ClosedCaptionCmdString = self.__build_setstring(b'10', b'84', ValueStateValues[value])
            self.__SetHelper('ClosedCaption', ClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetClosedCaption')

    def SetDigitalClosedCaption(self, value, qualifier):

        ValueStateValues = {
            'Off': b'01',
            'CS1': b'02',
            'CS2': b'03',
            'CS3': b'04',
            'CS4': b'05',
            'CS5': b'06',
            'CS6': b'07'
        }

        if value in ValueStateValues:
            DigitalClosedCaptionCmdString = self.__build_setstring(b'10', b'A1', ValueStateValues[value])
            self.__SetHelper('DigitalClosedCaption', DigitalClosedCaptionCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDigitalClosedCaption')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'On': b'02',
            'Off': b'01'
        }

        if value in ValueStateValues:
            ExecutiveModeCmdString = self.__build_setstring(b'00', b'FB', ValueStateValues[value])
            self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetExecutiveMode')

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'01',
            'Video': b'05',
            'Component': b'0C',
            'HDMI 1': b'11',
            'HDMI 2': b'12',
            'HDMI 3': b'82',
            'USB': b'87',
            'Tuner': b'09'
        }

        if value in ValueStateValues:
            InputCmdString = self.__build_setstring(b'00', b'60', ValueStateValues[value])
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPictureMode(self, value, qualifier):

        if value in self.SetPictureMode_ValueStateValues:
            PictureModeCmdString = self.__build_setstring(b'02', b'1A', self.SetPictureMode_ValueStateValues[value])
            self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPictureMode')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'1',
            'Off': b'4'
        }

        if value in ValueStateValues:
            temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A0C\x02C203D6000', ValueStateValues[value], b'\x03'])
            PowerCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetTVChannelCommand(self, value, qualifier):

        channel_string = value

        if channel_string:
            try:
                channels = channel_string.split('.')
                if len(channels) == 2:
                    major = int(channels[0])
                    minor = int(channels[1])

                    if (0 <= major <= 65535) and (0 <= minor <= 65535):
                        major = '{0:04X}'.format(major).encode()
                        minor = '{0:04X}'.format(minor).encode()

                        temp = b''.join([b'\x010', bytes([self._DeviceID]), b'0A12\x02C22D0000', major, minor, b'\x03'])
                        TVChannelCommandCmdString = b''.join([temp, self.__calculate_checksum(temp), b'\r'])
                        self.__SetHelper('TVChannelCommand', TVChannelCommandCmdString, value, qualifier)
                        return
            except ValueError:
                pass

        self.Discard('Invalid Command for SetTVChannelCommand')

    def SetTVChannelStep(self, value, qualifier):

        ValueStateValues = {
            'Up': b'01',
            'Down': b'02'
        }

        if value in ValueStateValues:
            TVChannelStepCmdString = self.__build_setstring(b'00', b'8B', ValueStateValues[value])
            self.__SetHelper('TVChannelStep', TVChannelStepCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTVChannelStep')

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = self.__build_setstring(b'00', b'62', hexlify(value.to_bytes(1, 'big')).upper())
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        self.Send(commandstring)

    def nec_10_4134_Others(self):

        self.SetPictureMode_ValueStateValues = {
            'Standard': b'04',
            'Theater': b'05',
            'Custom': b'08',
            'Dynamic': b'17',
            'Energy Saving': b'18',
            'Game': b'19',
            'HDR Dynamic': b'1A',
            'HDR Video': b'1B'
        }

    def nec_10_4134_E327(self):

        self.SetPictureMode_ValueStateValues = {
            'Standard': b'04',
            'Theater': b'05',
            'Custom': b'08',
            'Dynamic': b'17',
            'Energy Saving': b'18',
            'Game': b'19'
        }

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
