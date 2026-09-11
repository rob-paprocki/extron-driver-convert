from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:    
    def __init__(self):

        self.Debug = False
        self.Models = {}
        self.Commands = {
                 'DMX512Data': {'Parameters' : ['Slot'], 'Status': {}},
                 }
        self._network_address = 0
        self._physical_address = 0
        self._universe = 0
        self._header = b'Art-Net\x00'
        self._proto_version = 14
        self._seq_number = 1
        self._opcodes = {
            'DMX_Data' : 0x5000
            }

        self._data = bytearray(512)  
        NetworkLimits = {
            'min' : 0,
            'max' : 127
            }
            
        PhysicalLimits = {
            'min' : 0,
            'max' : 255
            }
            
        UniverseLimits = {
            'min' : 0,
            'max' : 255
            }

    @property
    def Network(self):
        return self._Network

    @Network.setter
    def Network(self, value):
        if 0 <= int(value) <= 127:
            self._Network= value
        else:
            print('Network Parameter Out of Range')

    @property
    def Physical(self):
        return self._Physical

    @Physical.setter
    def Physical(self, value):
        if 0 <= int(value) <= 255:
            self._Physical= value
        else:
            print('Physical Parameter Out of Range')

    @property
    def Universe(self):
        return self._Universe

    @Universe.setter
    def Universe(self, value):
        if 0 <= int(value) <= 255:
            self._Universe= value
        else:
            print('Univaerse Parameter Out of Range')

    def SetDMX512Data(self, value, qualifier):

        SlotLimits = {
            'min' : 0,
            'max' : 511
            }
            
        LevelLimits = {
            'min' : 0,
            'max' : 255
            }
        
        ok = True
        slot = 0
        try:
            slot = int(qualifier['Slot']) - 1
            level = int(value)
        except (ValueError, KeyError):
            ok = False
        else:
            ok &= SlotLimits['min'] <= slot <= SlotLimits['max']
            ok &= LevelLimits['min'] <= level <= LevelLimits['max']
            
        if ok:
            self._data[slot] = level
        else:
            self.Discard('Invalid Command for SetDMX512Data')
        
        self.__SetHelper('DMX512Data', self.__MakePacket(self._opcodes['DMX_Data']), value, qualifier)    

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
        method = getattr(self, 'Set%s' % command)
        if method is not None and callable(method):
            method(value, qualifier)
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