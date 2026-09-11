from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'AudioOnly': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioCmdString = b'\x55\x00\x4C\x00\xA1'
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioOnly(self, value, qualifier):

        AudioOnlyCmdString = b'\x55\x00\x97\x00\xEC'
        self.__SetHelper('AudioOnly', AudioOnlyCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'YPbPr':    b'\x55\x00\x80\x04\xD9',
            'VGA':      b'\x55\x00\x80\x05\xDA',
            'HDMI 1':   b'\x55\x00\x80\x08\xDD',
            'HDMI 2':   b'\x55\x00\x80\x09\xDE',
            'HDMI 3':   b'\x55\x00\x80\x11\xE6',
            'DP':       b'\x55\x00\x80\x15\xEA',
            'OPS':      b'\x55\x00\x80\x0B\xE0',
            'AV':       b'\x55\x00\x80\x0C\xE1',
            'USB':      b'\x55\x00\x80\x0F\xE4'
        }

        if value in ValueStateValues:
            InputCmdString = ValueStateValues[value]
            self.__SetHelper('Input', InputCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetInput')

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up':                       b'\x55\x00\x00\x01\x56',
            'Down':                     b'\x55\x00\x00\x02\x57',
            'Left':                     b'\x55\x00\x00\x03\x58',
            'Right':                    b'\x55\x00\x00\x04\x59',
            'OK':                       b'\x55\x00\x00\x00\x55',
            'Menu':                     b'\x55\x00\x14\x00\x69',
            'Exit':                     b'\x55\x00\x16\x00\x6B',
            'Info':                     b'\x55\x00\x18\x00\x6D',
            'Return':                   b'\x55\x00\x0A\x00\x5F',
            'Home':                     b'\x55\x00\x91\x00\xE6',
            'Factory Settings/Menu':    b'\x55\x00\x82\x00\xD7'
        }

        if value in ValueStateValues:
            MenuNavigationCmdString = ValueStateValues[value]
            self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuNavigation')

    def SetMute(self, value, qualifier):

        MuteCmdString = b'\x55\x00\x1A\x00\x6F'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On':   b'\x55\x00\x8E\x00\xE3',
            'Off':  b'\x55\x00\x8D\x00\xE2'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up':   b'\x55\x00\x0C\x00\x61',
            'Down': b'\x55\x00\x0E\x00\x63'
        }

        if value in ValueStateValues:
            VolumeCmdString = ValueStateValues[value]
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')

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