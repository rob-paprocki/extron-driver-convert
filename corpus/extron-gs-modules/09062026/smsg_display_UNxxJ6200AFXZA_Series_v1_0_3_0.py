from extronlib.interface import EthernetClientInterface, EthernetServerInterface, SerialInterface, IRInterface, RelayInterface
import time
from struct import pack

class DeviceClass:

    def __init__(self):
        self.Unidirectional = 'False'
        self.connectionCounter = 15

        # Do not change this the variables values below
        self.DefaultResponseTimeout = 0.3
        self._compile_list = {}
        self.Subscription = {}
        self.ReceiveData = self.__ReceiveData
        self._ReceiveBuffer = b''
        self.counter = 0
        self.connectionFlag = True
        self.initializationChk = True
        self.Models = {}

        self.Commands = {
            'ConnectionStatus': {'Status': {}},
            'AspectRatio': {'Status': {}},
            'AudioMute': {'Status': {}},
            'ChannelDirectCommand': {'Status': {}},
            'ChannelTV': {'Status': {}},
            'Input': {'Status': {}},
            'MenuNavigation': {'Status': {}},
            'Power': {'Status': {}},
            'Volume': {'Status': {}}
        }
       
    def SetAspectRatio(self, value, qualifier):
        ValueStateValues = {
            '16:9': b'\x00\xC0',
            'Zoom 1': b'\x01\xBF',
            'Zoom 2': b'\x02\xBE',
            'Wide Fit': b'\x03\xBD',
            '4:3': b'\x04\xBC',
            'Screen Fit': b'\x05\xBB'
        }

        AspectRatioCmdString = b'\x08\x22\x0B\x0A\x01' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):
        AudioMuteCmdString = b'\x08\x22\x02\x00\x00\x00\xD4'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannelTV(self, value, qualifier):
        ValueStateValues = {
            'Up': b'\x01\x00\xD2',
            'Down': b'\x02\x00\xD1'
        }

        ChannelTVCmdString = b'\x08\x22\x03\x00' + ValueStateValues[value]
        self.__SetHelper('ChannelTV', ChannelTVCmdString, value, qualifier)

    def SetChannelDirectCommand(self, value, qualifier):

        if value != '':
            temp = ~(0x08 + 0x22 + 0x04 + int(value)) & 0xFF
            checksum = pack('B', temp + 1)
            channel = pack('>H', int(value))
            ChannelDirectCmdString = b'\x08\x22\x04\x00' + channel + checksum
            self.__SetHelper('ChannelDirectCommand', ChannelDirectCmdString, value, qualifier)

    def SetInput(self, value, qualifier):
        ValueStateValues = {
            'TV': b'\x00\x00\xCC',
            'AV': b'\x01\x00\xCB',
            'Component': b'\x03\x00\xC9',
            'HDMI 1': b'\x05\x00\xC7',
            'HDMI 2': b'\x05\x01\xC6'
        }

        InputCmdString = b'\x08\x22\x0A\x00' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):
        ValueStateValues = {
            'Up': b'\x60\x69',
            'Down': b'\x61\x68',
            'Left': b'\x65\x64',
            'Right': b'\x62\x67',
            'Menu': b'\x1A\xAF',
            'Enter': b'\x68\x61',
            'Exit': b'\x2D\x9C'
        }

        MenuNavigationCmdString = b'\x08\x22\x0D\x00\x00' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):
        ValueStateValues = {
            'On': b'\x02\xD4',
            'Off': b'\x01\xD5'
        }

        PowerCmdString = b'\x08\x22\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):
        ValueConstraints = {
            'Min': 0,
            'Max': 100
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            chksum = 0x08 + 0x22 + 0x01 + 0x00 + 0x00 + value
            chksum = 256 - chksum
            VolumeCmdString = pack('>7B', 0x08, 0x22, 0x01, 0x00, 0x00, value, chksum)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            print('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier, queryDisallowTime=0):
        self.Send(commandstring)


    ######################################################    
    # RECOMMENDED not to modify the code below this point
    ######################################################

    # Send  Control Commands
    def Set(self, command, value, qualifier=None):
        try:
            getattr(self, 'Set%s' % command)(value, qualifier)
        except AttributeError:
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
