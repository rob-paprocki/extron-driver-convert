from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }



    def __CommandBuilder(self, value):

        cks = 0x2A
        for i in value:
            cks += i
        checksum = (255 - cks) + 1
        return b''.join([b'\x08\x22', bytes(value), bytes([checksum])])

    def SetAspectRatio(self, value, qualifier):


        ValueStateValues = {
            '4:3'       : 0x04,
            '16:9'      : 0x00,
            'Zoom 1'    : 0x01,
            'Zoom 2'    : 0x02,
            'Wide Fit'  : 0x03,
            'Screen Fit': 0x05
        }

        if value in ValueStateValues:
            self.__SetHelper('AspectRatio', self.__CommandBuilder([0x0B, 0x0A, 0x01, ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetAspectRatio')
    def SetChannel(self, value, qualifier):


        ValueStateValues = {
            'Up'  : 0x01,
            'Down': 0x02
        }

        if value in ValueStateValues:
            self.__SetHelper('Channel',
                                 self.__CommandBuilder([0x03, 0x00, ValueStateValues[value],0x00]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannel')
    def SetInput(self, value, qualifier):


        ValueStateValues = {
            'TV'     : [0x00, 0x00],
            'HDMI 1' : [0x05, 0x00],
            'HDMI 2' : [0x05, 0x01],
            'HDMI 3' : [0x05, 0x02],
            'HDMI 4' : [0x05, 0x03]
        }

        if value in ValueStateValues:
            self.__SetHelper('Input',
                                 self.__CommandBuilder([0x0A,0x00, ValueStateValues[value][0], ValueStateValues[value][1]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')
    def SetMute(self, value, qualifier):


        self.__SetHelper('Mute', self.__CommandBuilder([0x02, 0x00, 0x00,0x00]), value, qualifier)
        
    def SetPower(self, value, qualifier):


        ValueStateValues = {
            'On' : 0x02,
            'Off': 0x01
        }

        if value in ValueStateValues:
            self.__SetHelper('Power', self.__CommandBuilder([0x00, 0x00,0x00, ValueStateValues[value]]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')
    def SetVolume(self, value, qualifier):


        if 0 <= value <= 100:
            self.__SetHelper('Volume', self.__CommandBuilder([0x01, 0x00,0x00, value]), value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True




        self.Send(commandstring)

    def __MatchError(self, match, tag):
        self.counter = 0



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

