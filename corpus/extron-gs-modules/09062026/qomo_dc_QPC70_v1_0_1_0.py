from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from extronlib.system import Wait, ProgramLog


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AutoFocus': {'Status': {}},
            'Brightness': {'Status': {}},
            'Focus': {'Status': {}},
            'Freeze': {'Status': {}},
            'ImageRecall': {'Status': {}},
            'ImageRotate': {'Status': {}},
            'ImageSave': {'Status': {}},
            'Input': {'Status': {}},
            'Light': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Mirror': {'Status': {}},
            'PictureMode': {'Status': {}},
            'PositiveNegative': {'Status': {}},
            'Power': {'Status': {}},
            'Resolution': {'Status': {}},
            'Split': {'Status': {}},
            'Volume': {'Status': {}},
            'Zoom': {'Status': {}},
        }

    def SetAutoFocus(self, value, qualifier):

        AutoFocusCmdString = '\x48\x02\x18\x03\x54'
        self.__SetHelper('AutoFocus', AutoFocusCmdString, value, qualifier)

    def SetBrightness(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x04\x17\x14\x00\x02\x54',
            'Down': '\x48\x04\x17\x14\x00\x03\x54'
        }

        BrightnessCmdString = ValueStateValues[value]
        self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)

    def SetFocus(self, value, qualifier):

        ValueStateValues = {
            'Near': '\x48\x04\x17\x08\x00\x03\x54',
            'Far': '\x48\x04\x17\x08\x00\x02\x54'
        }

        FocusCmdString = ValueStateValues[value]
        self.__SetHelper('Focus', FocusCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        ValueStateValues = {
            'On': '\x48\x04\x16\x0C\x00\x01\x54',
            'Off': '\x48\x04\x16\x0C\x00\x00\x54'
        }

        FreezeCmdString = ValueStateValues[value]
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetImageRecall(self, value, qualifier):

        ImageRecallCmdString = '\x48\x02\x28\x07\x54'
        self.__SetHelper('ImageRecall', ImageRecallCmdString, value, qualifier)

    def SetImageRotate(self, value, qualifier):

        ValueStateValues = {
            'Rotate': '\x48\x04\x17\x0A\x00\x01\x54',
            'Exit': '\x48\x04\x16\x0A\x00\x00\x54'
        }

        ImageRotateCmdString = ValueStateValues[value]
        self.__SetHelper('ImageRotate', ImageRotateCmdString, value, qualifier)

    def SetImageSave(self, value, qualifier):

        ImageSaveCmdString = '\x48\x02\x28\x04\x54'
        self.__SetHelper('ImageSave', ImageSaveCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'PC1': '\x48\x04\x16\x13\x00\x01\x54',
            'HDMI': '\x48\x04\x16\x13\x00\x02\x54',
            'CCD': '\x48\x04\x16\x13\x00\x00\x54'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetLight(self, value, qualifier):

        ValueStateValues = {
            'Arm Light': '\x48\x04\x16\x09\x00\x01\x54',
            'All Off': '\x48\x04\x16\x09\x00\x00\x54'
        }

        LightCmdString = ValueStateValues[value]
        self.__SetHelper('Light', LightCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x02\x28\x08\x54',
            'Down': '\x48\x02\x28\x09\x54',
            'Left': '\x48\x02\x28\x0a\x54',
            'Right': '\x48\x02\x28\x0b\x54'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMirror(self, value, qualifier):

        ValueStateValues = {
            'On': '\x48\x04\x16\x0B\x00\x01\x54',
            'Off': '\x48\x04\x16\x1B\x00\x00\x54',
        }

        MirrorCmdString = ValueStateValues[value]
        self.__SetHelper('Mirror', MirrorCmdString, value, qualifier)

    def SetPictureMode(self, value, qualifier):

        ValueStateValues = {
            'Image': '\x48\x04\x16\x11\x00\x00\x54',
            'Text': '\x48\x04\x16\x11\x00\x01\x54',
            'Color': '\x48\x04\x16\x10\x00\x00\x54',
            'B&W': '\x48\x04\x16\x10\x00\x01\x54',
        }

        PictureModeCmdString = ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)

    def SetPositiveNegative(self, value, qualifier):

        ValueStateValues = {
            'Positive': '\x48\x04\x16\x0F\x00\x00\x54',
            'Negative': '\x48\x04\x16\x0F\x00\x01\x54'
        }

        PositiveNegativeCmdString = ValueStateValues[value]
        self.__SetHelper('PositiveNegative', PositiveNegativeCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '\x48\x02\x28\x01\x54',
            'Off': '\x48\x02\x18\x02\x54'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetResolution(self, value, qualifier):

        ValueStateValues = {
            '1080P': '\x48\x04\x16\x12\x00\x10\x54',
            '720P': '\x48\x04\x16\x12\x00\x04\x54',
            'WXGA': '\x48\x04\x16\x12\x00\xAC\x54',
            'XGA': '\x48\x04\x16\x12\x00\x98\x54',
            'SXGA': '\x48\x04\x16\x12\x00\xA8\x54'
        }

        ResolutionCmdString = ValueStateValues[value]
        self.__SetHelper('Resolution', ResolutionCmdString, value, qualifier)

    def SetSplit(self, value, qualifier):

        ValueStateValues = {
            'On': '\x48\x04\x16\x0D\x00\x01\x54',
            'Off': '\x48\x04\x16\x0D\x00\x00\x54',
        }

        SplitCmdString = ValueStateValues[value]
        self.__SetHelper('Split', SplitCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': '\x48\x04\x17\x15\x00\x02\x54',
            'Down': '\x48\x04\x17\x15\x00\x03\x54'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def SetZoom(self, value, qualifier):

        ValueStateValues = {
            'Tele': '\x48\x04\x17\x07\x00\x04\x54',
            'Wide': '\x48\x04\x17\x07\x00\x05\x54',
            'Stop': '\x48\x04\x17\x07\x00\x06\x54'
        }

        ZoomCmdString = ValueStateValues[value]
        self.__SetHelper('Zoom', ZoomCmdString, value, qualifier)

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
