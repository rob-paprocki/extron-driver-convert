from extronlib.interface import SerialInterface, EthernetClientInterface
import re
import struct
import math

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'VirtualPaneluS': {'Parameters':['Handle','MethodID'], 'Status': {}},
            'VirtualPaneldB': {'Parameters':['Handle','MethodID'], 'Status': {}},
            'VirtualPanelDiscrete': {'Parameters':['Handle','MethodID'], 'Status': {}},
            'VirtualPanelFrequency': {'Parameters':['Handle','MethodID'], 'Status': {}},
            'VirtualPanelMute': {'Parameters':['Handle','MethodID'], 'Status': {}},
            }

    def MethodIDConversion(self,MethodID):
        
        if re.findall(re.compile('0x([0-9]|[A-F]|[a-f]){8}'), MethodID) != []:
            Handle = MethodID[2:] 
            OUTPUT = b''
            OUTPUT = struct.pack('BBBB',int((Handle[0] + Handle[1]),16), int((Handle[2] + Handle[3]),16),int((Handle[4] + Handle[5]),16),int((Handle[6] + Handle[7]),16))
            return OUTPUT
        else:
            self.Discard('Invalid Command')

    def HandleConversion(self,Handle):
        
        if re.findall(re.compile('0x([0-9]|[A-F]|[a-f]){8}'),Handle) != []:
            Handle = Handle[2:] 
            OUTPUT = b''
            OUTPUT = struct.pack('BBBB',int((Handle[0] + Handle[1]),16), int((Handle[2] + Handle[3]),16),int((Handle[4] + Handle[5]),16),int((Handle[6] + Handle[7]),16))
            return OUTPUT
        else:
            self.Discard('Invalid Command')

    def escape(self,m):

        M = b''
        Escaped = {
            0x02: b'\x1B\x82', 
            0x03: b'\x1B\x83', 
            0x06: b'\x1B\x86', 
            0x15: b'\x1B\x95', 
            0x1b: b'\x1B\x9B'
            }
        for byte in m:
            if byte in Escaped:
                M += Escaped[byte]
            else:
                M += byte.to_bytes(1, byteorder='big')
        return M

    def CheckSum(self,Body):

        checksum = 0
        for byte in Body:
            checksum = checksum ^ byte
        OUTPUT = struct.pack('B',checksum)
        return OUTPUT

    def ValueConversion(self,ValueType,Value):

        OUTPUT = b''
        if ValueType == 'dB':
            Value = int(Value*256)
            OUTPUT = struct.pack('>h',Value)
        elif ValueType == 'Hz':
            Value = int((10000*math.log(Value))/math.log(10))
            OUTPUT = struct.pack('>H',Value)
        elif ValueType == 'uS':
            OUTPUT = struct.pack('>I', Value)
        elif ValueType == 'Discrete':
            OUTPUT = struct.pack('BB',0,Value)
        return OUTPUT

    def PacketGenerationWMI(self,Handle, MethodID, Value, ValueType):

        HexHandle = self.HandleConversion(Handle)
        MessageValue = self.ValueConversion(ValueType, Value)
        HexMethodID = self.MethodIDConversion(MethodID)
        Body =  b'\x84' + HexHandle + HexMethodID + MessageValue
        CS = self.CheckSum(Body)
        m = Body + CS
        return b'\x02' + self.escape(m) + b'\x03'
    def SetVirtualPaneluS(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 4000000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VirtualPaneluSCmdString = self.PacketGenerationWMI(qualifier['Handle'], qualifier['MethodID'], value, 'uS')
            self.__SetHelper('VirtualPaneluS', VirtualPaneluSCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualPaneluS')

    def SetVirtualPaneldB(self, value, qualifier):

        ValueConstraints = {
            'Min' : -128,
            'Max' : 127
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VirtualPaneldBCmdString = self.PacketGenerationWMI(qualifier['Handle'], qualifier['MethodID'], value, 'dB')
            self.__SetHelper('VirtualPaneldB', VirtualPaneldBCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualPaneldB')

    def SetVirtualPanelDiscrete(self, value, qualifier):

        ValueConstraints = {
            'Min' : 0,
            'Max' : 255
            }
        
        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VirtualPanelDiscreteCmdString = self.PacketGenerationWMI(qualifier['Handle'], qualifier['MethodID'], value, 'Discrete')
            self.__SetHelper('VirtualPanelDiscrete', VirtualPanelDiscreteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualPanelDiscrete')
    def SetVirtualPanelFrequency(self, value, qualifier):

        ValueConstraints = {
            'Min' : 1,
            'Max' : 3500000
            }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VirtualPanelFrequencyCmdString = self.PacketGenerationWMI(qualifier['Handle'], qualifier['MethodID'], value, 'Hz')
            self.__SetHelper('VirtualPanelFrequency', VirtualPanelFrequencyCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVirtualPanelFrequency')

    def SetVirtualPanelMute(self, value, qualifier):

        ValueStateValues = {
            'On' : 1, 
            'Off' : 0
        }

        VirtualPanelDiscreteCmdString = self.PacketGenerationWMI(qualifier['Handle'], qualifier['MethodID'], ValueStateValues[value], 'Discrete')
        self.__SetHelper('VirtualPanelMute', VirtualPanelDiscreteCmdString, value, qualifier)

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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