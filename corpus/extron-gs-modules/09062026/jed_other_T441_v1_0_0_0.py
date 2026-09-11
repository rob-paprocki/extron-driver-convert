from extronlib.interface import SerialInterface, EthernetClientInterface

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'Attenuation': {'Parameters':['Channel'], 'Status': {}},
            'RampTime': {'Parameters':['Channel'], 'Status': {}},
            }

    def SetAttenuation(self, value, qualifier):

        Channel = qualifier['Channel']
        if -63 <= value <= 0 and 1<= int(Channel) <= 4:
            CmdString = ':S{0}{1:02X}\r\n'.format(Channel, -value)
            self.__SetHelper('Attenuation', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetAttenuation')

    def SetRampTime(self, value, qualifier):

        Channel = qualifier['Channel']
        if 0 <= value <= 255 and 1<= int(Channel) <= 4:
            CmdString = ':T{0}{1:02X}\r\n'.format(Channel,value)
            self.__SetHelper('RampTime', CmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetRampTime')

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