from extronlib.interface import SerialInterface, EthernetClientInterface
import re


class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._DeviceID = 1
        self.Models = {}
        self.Commands = {
            'DisplayCommand': {'Parameters': ['Effect', 'Color', 'Speed'], 'Status': {}},
        }

    @property
    def DeviceID(self):
        return self._DeviceID

    @DeviceID.setter
    def DeviceID(self, value):
        if value == 'Broadcast':
            self._DeviceID = '00'
        elif 1 <= int(value) <= 255:
            self._DeviceID = '{0:02X}'.format(int(value))
        else:
            self.Error(['Device ID should be a value between 1 to 255 or Broadcast.'])

    def SetDisplayCommand(self, value, qualifier):

        ColorStates = {
            'Red': '\x1C1',
            'Green': '\x1C2',
            'Amber': '\x1C3',
            'Dim Red': '\x1C4',
            'Dim Green': '\x1C5',
            'Brown': '\x1C6',
            'Orange': '\x1C7',
            'Yellow': '\x1C8',
            'Color Mix': '\x1CB',
            'Autocolor': '\x1CC'
        }

        EffectStates = {
            'Rotate': 'a',
            'Hold': 'b',
            'Flash': 'c',
            'Roll Up': 'e',
            'Roll Down': 'f',
            'Roll Left': 'g',
            'Roll Right': 'h',
            'Wipe Up': 'i',
            'Wipe Down': 'j',
            'Wipe Left': 'k',
            'Wipe Right': 'l',
            'Scroll': 'm',
            'Automode': 'o',
            'Compressed Rotate': 't',
            'Twinkle': 'n0',
            'Sparkle': 'n1',
            'Snow': 'n2',
            'Interlock': 'n3'
        }

        SpeedStates = {
            'Slowest': '\x15',
            'Slow': '\x16',
            'Fast': '\x17',
            'Faster': '\x18',
            'Fastest': '\x19'
        }

        Effect = EffectStates.get(qualifier['Effect'])
        Color = ColorStates.get(qualifier['Color'])
        Speed = SpeedStates.get(qualifier['Speed'])

        if Effect and Color and Speed and value:
            DisplayCommandCmdString = '\x00\x00\x00\x00\x00\x01a{0}\x02AA\x1B\x20{1}{2}{3}{4}\x04'.format(self._DeviceID, Effect, Color, Speed, value)
            self.__SetHelper('DisplayCommand', DisplayCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDisplayCommand')

    def __CheckResponseForErrors(self, sourceCmdName, response):
        pass

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
            raise AttributeError(command, 'does not support Set.')


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
