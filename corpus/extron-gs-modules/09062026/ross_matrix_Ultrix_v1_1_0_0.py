from extronlib.interface import SerialInterface, EthernetClientInterface
import re
class DeviceClass:


    
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'MatrixTieCommand': {'Parameters':['Input','Output','Tie Type'], 'Status': {}},
            }






    def CalcChecksum(self,buffer):
        sum = 0
        for i in buffer:
            sum += (256 - i)
        return bytes([sum%255])

    def SetMatrixTieCommand(self, value, qualifier):


        Input  = int(qualifier['Input'])
        Output = int(qualifier['Output'])
        Tie    = qualifier['Tie Type']

        if 1 <= Input <= 16 and 1 <= Output <= 16:

            if Tie in [ 'Video' , 'Audio/Video' ]:

                buffer = [ 0x02 , 0x00 , 0x00 , Output , Input , 0x05 ]
                CmdString = b'\x10\x02' + bytes(buffer) + self.CalcChecksum(buffer) + b'\x10\x03'

                self.__SetHelper('MatrixTieCommand', CmdString, value, qualifier)

            if Tie in [ 'Audio' , 'Audio/Video' ]:

                bufferL = [ 0x02 , 0x01 , 0x00 , Output , Input , 0x05 ]
                CmdStringL = b'\x10\x02' + bytes(bufferL) + self.CalcChecksum(bufferL) + b'\x10\x03'

                bufferR = [ 0x02 , 0x02 , 0x00 , Output , Input, 0x05 ]
                CmdStringR = b'\x10\x02' + bytes(bufferR) + self.CalcChecksum(bufferR) + b'\x10\x03'

                self.__SetHelper('MatrixTieCommand', CmdStringL + CmdStringR , value, qualifier)
        else:
            self.Discard('Invalid Command for SetMatrixTieCommand')

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

    def __init__(self, Host, Port, Baud=9600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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

