from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AudioMute': { 'Status': {}},
            'Input': { 'Status': {}},
            'Power': { 'Status': {}},
            'VideoMute': { 'Status': {}},
        }


    def SetAudioMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x12\x00\x00\x00\x14',
            'Off' : b'\x02\x13\x00\x00\x00\x15'
        }

        AudioMuteCmdString = ValueStateValues[value]
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'Computer'  : b'\x02\x03\x00\x00\x02\x01\x01\x09',
            'HDMI 1'    : b'\x02\x03\x00\x00\x02\x01\xA1\xA9',
            'HDMI 2'    : b'\x02\x03\x00\x00\x02\x01\xA2\xAA',
            'Video'     : b'\x02\x03\x00\x00\x02\x01\x06\x0E',
            'USB-A'     : b'\x02\x03\x00\x00\x02\x01\x1F\x27',
            'LAN'       : b'\x02\x03\x00\x00\x02\x01\x20\x28',
            'USB-B'     : b'\x02\x03\x00\x00\x02\x01\x22\x2A'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x00\x00\x00\x00\x02',
            'Off' : b'\x02\x01\x00\x00\x00\x03'
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def SetVideoMute(self, value, qualifier):

        ValueStateValues = {
            'On'  : b'\x02\x10\x00\x00\x00\x12',
            'Off' : b'\x02\x11\x00\x00\x00\x13'
        }

        VideoMuteCmdString = ValueStateValues[value]
        self.__SetHelper('VideoMute', VideoMuteCmdString, value, qualifier)
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

