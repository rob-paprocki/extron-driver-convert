from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Mute': {'Parameters': ['Instance'], 'Status': {}},
            'SerialUDPInputEvent': {'Parameters': ['Instance'], 'Status': {}},
            'Video': {'Parameters': ['Instance'], 'Status': {}},
            'Volume': {'Parameters': ['Instance'], 'Status': {}},
        }

    def SetMute(self, value, qualifier):

        ValueStates = ['Mute', 'Unmute']
        Instance = qualifier['Instance']

        if 1 <= int(Instance) <= 255 and value in ValueStates:
            MuteCmdString = ''.join([value, ' ', Instance])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Error(['Invalid command for SetMute'])

    def SetSerialUDPInputEvent(self, value, qualifier):

        ValueStateValues = {
            'Transition to New State': 'Transition',
            'Return to prior State': 'Return',
            'Remain on current State': 'Remain'
        }

        Instance = qualifier['Instance']
        if 1 <= int(Instance) <= 255:
            SerialUDPInputEventCmdString = ''.join([ValueStateValues[value], ' ', Instance])
            self.__SetHelper('SerialUDPInputEvent', SerialUDPInputEventCmdString, value, qualifier)
        else:
            self.Error(['Invalid command for SerialUDPInputEvent'])

    def SetVideo(self, value, qualifier):

        ValueStates = ['Play', 'Pause', 'Stop', 'Loop']

        Instance = qualifier['Instance']
        VideoCmdString = ''.join([value, ' ', Instance])
        self.__SetHelper('Video', VideoCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStates = ['Increment', 'Decrement']
        Instance = qualifier['Instance']

        if 1 <= int(Instance) <= 255 and value in ValueStates:
            VolumeCmdString = ''.join([value, ' ', Instance])
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Error(['Invalid command for Volume'])

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model=None):
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

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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
