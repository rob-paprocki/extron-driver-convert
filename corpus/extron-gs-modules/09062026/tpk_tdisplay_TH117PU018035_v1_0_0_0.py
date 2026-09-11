from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Brightness': {'Status': {}},
            'Contrast': {'Status': {}},
            'ExecutiveMode': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}},
        }


    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x06\x02\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'Off': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x06\x03\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x02\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            BrightnessCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x47\x02\x01\x00\x00\x00\x00\x00', bytes([value]), b'\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'])
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetContrast(self, value, qualifier):

        if 0 <= value <= 100:
            ContrastCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x48\x02\x01\x00\x00\x00\x00\x00', bytes([value]), b'\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'])
            self.__SetHelper('Contrast', ContrastCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetContrast')

    def SetExecutiveMode(self, value, qualifier):

        ValueStateValues = {
            'Lock Power': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'Lock OSD': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x00\x03\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'Unlock Power': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x00\x02\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'Unlock OSD': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x01\x01\x01\x00\x00\x00\x00\x00\x04\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'
        }

        ExecutiveModeCmdString = ValueStateValues[value]
        self.__SetHelper('ExecutiveMode', ExecutiveModeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'VGA': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x49\x10\x01\x00\x00\x00\x00\x00\x01\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'DVI': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x49\x10\x01\x00\x00\x00\x00\x00\x03\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x00\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC',
            'Off': b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x00\x02\x01\x00\x00\x00\x00\x00\x04\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        if 0 <= value <= 100:
            VolumeCmdString = b''.join([b'\xBE\xEF\x03\x19\x00\x00\x00\x01\x06\x01\x01\x00\x00\x00\x00\x00', bytes([value]), b'\x00\x00\x00\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC\xCC'])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True

        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0

        ######################################################
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send Control Commands
    def Set(self, command, value, qualifier=None):
        method = getattr(self, 'Set%s' % command, None)
        if method is not None and callable(method):
            method(value, qualifier)
        else:
            raise AttributeError(command, 'does not support Set.')


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
