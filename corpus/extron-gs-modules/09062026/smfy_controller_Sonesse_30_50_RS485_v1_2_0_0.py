from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._NodeType = [255]
        self._SourceAddress = b'\x80\x80\x80'
        self.Models = {}


        self.Commands = {
            'GroupMotorControl': {'Parameters':['Group Address'], 'Status': {}},
            'Lock': {'Parameters':['Destination Address'], 'Status': {}},
            'MotorControl': {'Parameters':['Destination Address'], 'Status': {}},
        }

    @property
    def NodeType(self):
        return self._NodeType

    @NodeType.setter
    def NodeType(self, value):
        if len(value.encode(encoding = 'iso-8859-1')) == 1:
            node = value.encode(encoding = 'iso-8859-1')
            self._NodeType = [0x00]
            self._NodeType[0] = 255 - node[0]
        else:
            print('Missing Node Type Parameter.')

    @property
    def SourceAddress(self):
        return self._SourceAddress

    @SourceAddress.setter
    def SourceAddress(self, value):
        if len(value.encode(encoding = 'iso-8859-1')) == 3:
            self._SourceAddress = value.encode(encoding = 'iso-8859-1')
        else:
            print('Missing Source Address Parameter.')

    def chkSum(self, cmdBytes):
        total = 0
        for x in cmdBytes:
            total = total + x
        return total.to_bytes(2, 'big')

    def SetGroupMotorControl(self, value, qualifier):

        group = qualifier['Group Address']
        if len(group.encode(encoding = 'iso-8859-1')) == 3:
            group = group.encode(encoding = 'iso-8859-1')
            GroupAddr = [0x00,0x00,0x00]
            GroupAddr[0] = group[2]
            GroupAddr[1] = group[1]
            GroupAddr[2] = group[0]

            ValueStateValues = {
	            'Up'   : [0xFC, 0xF0, self._NodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFE, 0xFF, 0xFF, 0xFF], 
	            'Down' : [0xFC, 0xF0, self._NodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF], 
	            'Stop' : [0xFD, 0xF3, self._NodeType[0], GroupAddr[0], GroupAddr[1], GroupAddr[2], 0xFF, 0xFF, 0xFF, 0xFF]
            }

            byteString = ValueStateValues[value]
            MotorControlCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                MotorControlCmdString += pack('>B', val)
            MotorControlCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('GroupMotorControl', MotorControlCmdString, value, qualifier)
        else:
             self.Discard('Invalid Command for SetGroupMotorControl')

    def SetLock(self, value, qualifier):

        destination = qualifier['Destination Address']
        if len(destination.encode(encoding = 'iso-8859-1')) == 3:
            destination = destination.encode(encoding = 'iso-8859-1')
            DestAddr = [0x00,0x00,0x00]
            DestAddr[0] = 255 - destination[2]
            DestAddr[1] = 255 - destination[1]
            DestAddr[2] = 255 - destination[0]

            ValueStateValues = {
	            'Lock Up'       : [0xA4, 0xF1, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFE, 0xFF, 0xFE], 
	            'Lock Down'     : [0xA4, 0xF1, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFD, 0xFF, 0xFE], 
	            'Lock Position' : [0xA4, 0xF1, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF, 0xFF, 0xFE], 
	            'Unlock'        : [0xA4, 0xF1, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFA, 0xFF, 0xFE]
            }

            byteString = ValueStateValues[value]
            LockCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                LockCmdString += pack('>B', val)
            LockCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('Lock', LockCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetLock')	     

    def SetMotorControl(self, value, qualifier):

        destination = qualifier['Destination Address']
        if len(destination.encode(encoding = 'iso-8859-1')) == 3:
            destination = destination.encode(encoding = 'iso-8859-1')
            DestAddr = [0x00,0x00,0x00]
            DestAddr[0] = 255 - destination[2]
            DestAddr[1] = 255 - destination[1]
            DestAddr[2] = 255 - destination[0]

            ValueStateValues = {
	            'Up'   : [0xFC, 0xF0, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFE, 0xFF, 0xFF, 0xFF], 
	            'Down' : [0xFC, 0xF0, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF, 0xFF, 0xFF, 0xFF], 
	            'Stop' : [0xFD, 0xF3, self._NodeType[0], self._SourceAddress[0], self._SourceAddress[1], self._SourceAddress[2], DestAddr[0], DestAddr[1], DestAddr[2], 0xFF]
            }
            
            byteString = ValueStateValues[value]
            MotorControlCmdString = bytes()
            checkSum = self.chkSum(byteString)
            for val in byteString:
                MotorControlCmdString += pack('>B', val)
            MotorControlCmdString += pack('>BB', checkSum[0], checkSum[1])
            self.__SetHelper('MotorControl', MotorControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMotorControl')

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

    def __init__(self, Host, Port, Baud=4800, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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