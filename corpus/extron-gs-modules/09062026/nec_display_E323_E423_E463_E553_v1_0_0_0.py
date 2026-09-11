from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'AutoImage': {'Status': {}},
            'Channel': {'Status': {}},
            'ClosedCaptionAnalog': {'Status': {}},
            'ClosedCaptionDigital': {'Status': {}},
            'Input': {'Status': {}},
            'KeyLock': {'Status': {}},
            'Power': {'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioState = {
            '4:3': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x31\x03\x00\x0D',
            'Auto': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x32\x03\x03\x0D',
            '16:9': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x33\x03\x02\x0D',
            'Zoom': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x34\x03\x05\x0D',
            'Cinema': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x32\x37\x30\x30\x30\x30\x42\x03\x73\x0D'
        }

        AspectRatioCmdString = AspectRatioState[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteState = {
            'On': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x31\x03\x09\x0D',
            'Off': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x44\x30\x30\x30\x32\x03\x0A\x0D'
        }

        AudioMuteCmdString = AudioMuteState[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetAutoImage(self, value, qualifier):

        AutoImageCmdString = b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x31\x45\x30\x30\x30\x31\x03\x01\x0D'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelState = {
            'Up': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x31\x03\x0F\x0D',
            'Down': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x38\x42\x30\x30\x30\x32\x03\x0C\x0D'
        }

        ChannelCmdString = ChannelState[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetClosedCaptionAnalog(self, value, qualifier):

        ClosedCaptionAnalogState = {
            'CC1': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x32\x03\x0B\x0D',
            'CC2': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x33\x03\x0A\x0D',
            'CC3': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x34\x03\x0D\x0D',
            'CC4': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x35\x03\x0C\x0D',
            'Text 1': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x36\x03\x0F\x0D',
            'Text 2': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x37\x03\x0E\x0D',
            'Text 3': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x38\x03\x01\x0D',
            'Text 4': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x39\x03\x00\x0D',
            'Off': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x38\x34\x30\x30\x30\x31\x03\x08\x0D'
        }

        ClosedCaptionAnalogCmdString = ClosedCaptionAnalogState[value]
        self.__SetHelper('ClosedCaptionAnalog', ClosedCaptionAnalogCmdString, value, qualifier)

    def SetClosedCaptionDigital(self, value, qualifier):

        ClosedCaptionDigitalState = {
            'Service 1': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x32\x03\x77\x0D',
            'Service 2': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x33\x03\x76\x0D',
            'Service 3': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x34\x03\x71\x0D',
            'Service 4': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x35\x03\x70\x0D',
            'Service 5': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x36\x03\x73\x0D',
            'Service 6': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x37\x03\x72\x0D',
            'Off': b'\x01\x30\x31\x30\x45\x30\x41\x02\x31\x30\x41\x31\x30\x30\x30\x31\x03\x74\x0D'
        }

        ClosedCaptionDigitalCmdString = ClosedCaptionDigitalState[value]
        self.__SetHelper('ClosedCaptionDigital', ClosedCaptionDigitalCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputState = {
            'VGA': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x31\x03\x73\x0D',
            'HDMI 1': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x31\x03\x72\x0D',
            'HDMI 2': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x32\x03\x71\x0D',
            'HDMI 3': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x33\x03\x70\x0D',
            'Composite': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x35\x03\x77\x0D',
            'TV': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x41\x03\x73\x0D',
            'Component': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x30\x43\x03\x01\x0D',
            'USB': b'\x01\x30\x31\x30\x45\x30\x41\x02\x30\x30\x36\x30\x30\x30\x31\x34\x03\x07\x0D'
        }

        InputCmdString = InputState[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetKeyLock(self, value, qualifier):

        KeyLockState = {
            'All Buttons': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x32\x03\x72\x0D',
            'Control Buttons': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x31\x03\x71\x0D',
            'Unlock': b'\x01\x30\x41\x30\x45\x30\x41\x02\x30\x30\x46\x42\x30\x30\x30\x30\x03\x70\x0D'
        }

        KeyLockCmdString = KeyLockState[value]
        self.__SetHelper('KeyLock', KeyLockCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerState = {
            'On': b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x31\x03\x73\x0D',
            'Off': b'\x01\x30\x41\x30\x41\x30\x43\x02\x43\x32\x30\x33\x44\x36\x30\x30\x30\x34\x03\x76\x0D'
        }

        PowerCmdString = PowerState[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

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
