from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import ProgramLog, Wait

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DMX': {'Parameters' : ['Universe', 'Slot'], 'Status': {}},
        }

        self._universe = 0
        self._network_address = 0
        self._physical_address = 0
        self._header = b'Art-Net\x00'
        self._proto_version = 14
        self._seq_number = 1
        self._opcodes = {
            'DMX_Data' : 0x5000
        }
        self._data = bytearray(512)
        
    def __MakePacket(self, opcode, universe):

        return b''.join([self._header,
                         opcode.to_bytes(2, 'little'),
                         self._proto_version.to_bytes(2, 'big'),
                         self.__GetSequenceNumber().to_bytes(1, 'big'),
                         self._physical_address.to_bytes(1, 'big'),
                         universe.to_bytes(1, 'big'),
                         self._network_address.to_bytes(1, 'big'),
                         len(self._data).to_bytes(2, 'big'),
                         self._data])
    
    def __GetSequenceNumber(self):

        res = self._seq_number
        self._seq_number += 1
        if self._seq_number > 255:
            self._seq_number = 1
        return res
    
    def SetDMX(self, value, qualifier):

        if 0 <= qualifier['Universe'] <= 255 and 1 <= qualifier['Slot'] <= 512 and 0 <= value <= 255:
            self._data[qualifier['Slot'] - 1] = value
            DMXCmdString = self.__MakePacket(self._opcodes['DMX_Data'], qualifier['Universe'])
            self.__SetHelper('DMX', DMXCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDMX')

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