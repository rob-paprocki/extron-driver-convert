from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:

    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AudioMute': {'Status': {}},
            'Freeze': {'Status': {}},
            'Input': {'Status': {}},
            'Power': {'Status': {}},
            'VideoMute': {'Status': {}},
            'Volume': {'Status': {}},
        }

       
    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x30'
        }

        AudioMuteCmdString = b'\x38\x30\x31\x73\x36\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetFreeze(self, value, qualifier):

        FreezeCmdString = b'\x38\x30\x31\x73\x21\x30\x30\x33\x0D'
        self.__SetHelper('Freeze', FreezeCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'AV 1': b'\x30\x30\x33',
            'Component': b'\x30\x30\x34',
            'VGA': b'\x30\x30\x30',
            'HDMI 1': b'\x30\x30\x31',
            'HDMI 2': b'\x30\x30\x32',
            'HDMI 3': b'\x30\x32\x31',
            'HDMI 4': b'\x30\x32\x32',
            'HDMI 5': b'\x30\x32\x33',
            'Android': b'\x31\x30\x31',
            'Optional': b'\x31\x30\x32',
            'Source': b'\x32\x30\x31'
        }

        InputCmdString = b'\x38\x30\x31\x73\x22' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': b'\x31',
            'Off': b'\x32'
        }

        PowerCmdString = b'\x38\x30\x31\x73\x21\x30\x30' + ValueStateValues[value] + b'\x0D'
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVideoMute(self, value, qualifier):

        VideoMuteCmdString = b'\x38\x30\x31\x73\x21\x30\x30\x30\x0D'
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up': b'\x33',
            'Down': b'\x32'
        }

        VolumeCmdString = b'\x38\x30\x31\x73\x35' + ValueStateValues[value] + b'\x30\x30\x0D'
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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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
