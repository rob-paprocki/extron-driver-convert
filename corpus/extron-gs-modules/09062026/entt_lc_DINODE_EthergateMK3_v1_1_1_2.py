from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:    
    def __init__(self):
        self.Debug = False
        self.Models = {}
        self.Commands = {                 
                 'SendDMX512Data': {'Parameters' : ['Slot'], 'Status': {}},
                 } 

        self._universe = 1
        self._network_address = 0
        self._physical_address = 0       

        self._header = b'Art-Net\x00'
        self._proto_version = 14
        self._seq_number = 1
        self._opcodes = {
            'DMX_Data' : 0x5000
            }      
        self._data = bytearray(512)   

    @property
    def Universe(self):
        return self._Universe

    @Universe.setter
    def Universe(self, value):
        self._Universe = value   
            
    def SetSendDMX512Data(self, value, qualifier):    
        ok = True
        slot = 0
        try:
            slot = int(qualifier['Slot']) - 1
            level = int(value)
        except (ValueError, KeyError):
            ok = False
        else:
            ok &= 0 <= slot <= 511
            ok &= 0 <= level <= 255
            
        if ok:
            self._data[slot] = level            
            self.__SetHelper('SendDMX512Data', self.__MakePacket(self._opcodes['DMX_Data']), value, qualifier)   
        else:
            self.Discard('Incorrect Command or Qualifier value')        

    def __MakePacket(self, opcode):
        return b''.join([ self._header,
                          opcode.to_bytes(2, 'little'),
                          self._proto_version.to_bytes(2, 'big'),
                          self.__GetSequenceNumber().to_bytes(1, 'big'),
                          self._physical_address.to_bytes(1, 'big'),
                          self._universe.to_bytes(1, 'big'),
                          self._network_address.to_bytes(1, 'big'),
                          len(self._data).to_bytes(2, 'big'),
                          self._data])
    
    def __GetSequenceNumber(self):
        res = self._seq_number
        self._seq_number += 1
        if self._seq_number > 255:
            self._seq_number = 1
        return res

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