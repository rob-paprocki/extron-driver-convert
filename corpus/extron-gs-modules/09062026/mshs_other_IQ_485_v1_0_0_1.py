from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Commands = {
            'MotorControl': {'Parameters': ['Zone Select', 'Group Select', 'Node Select'], 'Status': {}},
            'PresetSelect': {'Parameters': ['Zone Select', 'Group Select', 'Node Select'], 'Status': {}},
        }
      
    def SetMotorControl(self, value, qualifier):

        ValueStateValues = {
            'Up': 'UP',
            'Down': 'DN',
            'Stop': 'ST'
        }

        zone = int(qualifier['Zone Select'])
        group = int(qualifier['Group Select'])
        node = int(qualifier['Node Select'])

        if 0 <= zone <= 255 and 0 <= group <= 255 and 0 <= node <= 255:
            MotorControlCmdString = '#{0}.{1}.{2}.A={3}\r'.format(zone, group, node, ValueStateValues[value])
            self.__SetHelper('MotorControl', MotorControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotorControl')

    def SetPresetSelect(self, value, qualifier):

        ValueStateValues = {
            '1': 'G1',
            '2': 'G2',
            '3': 'G3'
        }

        zone = int(qualifier['Zone Select'])
        group = int(qualifier['Group Select'])
        node = int(qualifier['Node Select'])

        if 0 <= zone <= 255 and 0 <= group <= 255 and 0 <= node <= 255:
            PresetSelectCmdString = '#{0}.{1}.{2}.A={3}\r'.format(zone, group, node, ValueStateValues[value])
            self.__SetHelper('PresetSelect', PresetSelectCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetSelect')

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
