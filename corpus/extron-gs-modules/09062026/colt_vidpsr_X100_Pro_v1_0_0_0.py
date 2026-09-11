from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._Sender = b'\x00\x00'
        self.Models = {}

        self.Commands = {
            'Brightness': { 'Status': {}},
            'Input': {'Parameters':['Layer','Output Board Slot Number','Input Card Model','Interface Number'], 'Status': {}},
            'PresetRecall': { 'Status': {}},
            'Screen': { 'Status': {}},
        }

    @property
    def Sender(self):
        return self._Sender

    @Sender.setter
    def Sender(self, value):
        if value == 'All':
            self._Sender = b'\xFF\xFF'
        elif 1 <= int(value) <= 15:
            self._Sender = pack('>h', int(value) - 1)
        else:
            self.Error(['Invalid Sender Parameter range.'])

    def SetBrightness(self, value, qualifier):

        if 0 <= value <= 100:
            brightness = pack('<h', value * 100)
            BrightnessCmdString = b'\x50\x10\x00\x13\x00\x00\x00' + self._Sender + b'\x00\x00\x00\x00\x00\x00\x00\x00' + brightness
            self.__SetHelper('Brightness', BrightnessCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetBrightness')

    def SetInput(self, value, qualifier):

        LayerStates = {
            'Main'  : b'\x00',
            'PIP 1' : b'\x01',
            'PIP 2' : b'\x02'
        }

        InputCardModelStates = {
            'DVI x 4'           : b'\x10',
            'HDMI x 4'          : b'\x11',
            '2 IN 1'            : b'\x12',
            '3G-SDI'            : b'\x16',
            'HDMI 2.0'          : b'\x1E',
            'DisplayPort 1.2'   : b'\x1F',
            'VGA x 4'           : b'\x20',
            'VGA x 2, CVBS x 2' : b'\x21',
            'CVBS x 4'          : b'\x22',
            'Mixed Input'       : b'\x18'
        }

        ValueStateValues = {
            'DVI'               : b'\x10',
            'HDMI 1.4'          : b'\x11',
            'HDMI 2.0'          : b'\x20',
            'DisplayPort 1.4'   : b'\x21',
            '12G-SDI'           : b'\x22',
            '3G-SDI'            : b'\x12',
            'VGA'               : b'\x13',
            'CVBS'              : b'\x14'
        }

        outputBoardSlotNumber = int(qualifier['Output Board Slot Number'])
        interfaceNumber = int(qualifier['Interface Number'])
        if qualifier['Layer'] in LayerStates and 1 <= outputBoardSlotNumber <= 32 and qualifier['Input Card Model'] in InputCardModelStates and 1 <= interfaceNumber <= 10 and value in ValueStateValues:
            InputCmdString = b'\x20\x10\x00\x18\x00\x00\x00' + self._Sender + b'\x00\x00\x00\x00\x00\x00\x00\x00' + LayerStates[qualifier['Layer']] + pack('h', 15 + outputBoardSlotNumber) + InputCardModelStates[qualifier['Input Card Model']] + b'\x00' + ValueStateValues[value] + pack('B', interfaceNumber - 1)
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetPresetRecall(self, value, qualifier):

        if 1 <= int(value) <= 128:
            PresetRecallCmdString = b'\x07\x10\x03\x13\x00\x00\x00' + self._Sender + b'\x00\x00\x00\x00\x00\x00\x00\x00' + pack('h', int(value) - 1)
            self.__SetHelper('PresetRecall', PresetRecallCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPresetRecall')

    def SetScreen(self, value, qualifier):

        ValueStateValues = {
            'Wakeup'   : b'\x01',
            'Blackout' : b'\x00'
        }

        if value in ValueStateValues:
            ScreenCmdString = b'\x10\x10\x00\x12\x00\x00\x00' + self._Sender + b'\x00\x00\x00\x00\x00\x00\x00\x00' + ValueStateValues[value]
            self.__SetHelper('Screen', ScreenCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScreen')

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

    def __init__(self, Host, Port, Baud=115200, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
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
        portInfo = 'IP Address/Host: {0}:{1}'.format(self.IPAddress, self.IPPort)
        print('Module: {}'.format(__name__), portInfo, 'Error Message: {}'.format(message[0]), sep='\r\n')
  
    def Discard(self, message):
        self.Error([message])