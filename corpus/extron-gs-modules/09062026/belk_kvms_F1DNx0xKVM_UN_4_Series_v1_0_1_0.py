from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {
            'F1DN116KVM-UN-4': self.belk_32_6435_16,
            'F1DN102KVM-UNN4': self.belk_32_6435_2,
            'F1DN102KVM-UN-4': self.belk_32_6435_2,
            'F1DN202KVM-UNN4': self.belk_32_6435_2,
            'F1DN202KVM-UN-4': self.belk_32_6435_2,
            'F1DN204KVM-UN-4': self.belk_32_6435_4,
            'F1DN104KVM-UNN4': self.belk_32_6435_4,
            'F1DN204KVM-UNN4': self.belk_32_6435_4,
            'F1DN108KVM-UN-4': self.belk_32_6435_8,
            'F1DN208KVM-UN-4': self.belk_32_6435_8,
        }

        self.Commands = {
            'Channel': { 'Status': {}}
        }

    def SetChannel(self, value, qualifier):

        if value in self.ChannelStateValues:
            ChannelCmdString = '#AFP_ALIVE {}\r'.format(self.ChannelStateValues[value])
            self.__SetHelper('Channel', ChannelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')

    def __SetHelper(self, command, commandstring, value, qualifier):

        self.Debug = True

        self.Send(commandstring)

    def belk_32_6435_16(self):

        self.ChannelStateValues = {
            '1'  : 'FE',
            '2'  : 'FD',
            '3'  : 'FB',
            '4'  : 'F7',
            '5'  : 'EF',
            '6'  : 'DF',
            '7'  : 'BF',
            '8'  : '7F',
            '9'  : 'FF',
            '10' : 'FDFF',
            '11' : 'FBFF',
            '12' : 'F7FF',
            '13' : 'EFFF',
            '14' : 'DFFF',
            '15' : 'BFFF',
            '16' : '7FFF'
        }

    def belk_32_6435_2(self):

        self.ChannelStateValues = {
            '1' : 'FE',
            '2' : 'FD'
        }

    def belk_32_6435_4(self):

        self.ChannelStateValues = {
            '1' : 'FE',
            '2' : 'FD',
            '3' : 'FB',
            '4' : 'F7'
        }


    def belk_32_6435_8(self):

        self.ChannelStateValues = {
            '1' : 'FE',
            '2' : 'FD',
            '3' : 'FB',
            '4' : 'F7',
            '5' : 'EF',
            '6' : 'DF',
            '7' : 'BF',
            '8' : '7F'
        }

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