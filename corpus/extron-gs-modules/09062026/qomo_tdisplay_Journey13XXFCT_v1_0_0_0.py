from extronlib.interface import SerialInterface, EthernetClientInterface
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'Aspect': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'BacklightMode': { 'Status': {}},
            'Freeze': { 'Status': {}},
            'Home': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'Screenshot': { 'Status': {}},
            'Volume': { 'Status': {}},
        }

    def SetAspect(self, value, qualifier):
        self.__SetHelper('Aspect', b'\x55\x00\x4C\x00\xA1', value, qualifier)

    def SetAutoImage(self, value, qualifier):
        self.__SetHelper('AutoImage', b'\x55\x00\x58\x00\xAD', value, qualifier)

    def SetBacklightMode(self, value, qualifier):
        self.__SetHelper('BacklightMode', b'\x55\x00\x88\x00\xDD', value, qualifier)

    def SetFreeze(self, value, qualifier):
        self.__SetHelper('Freeze', b'\x55\x00\xA4\x01\xFA', value, qualifier)

    def SetHome(self, value, qualifier):
        self.__SetHelper('Home', b'\x55\x00\x91\x00\xE6', value, qualifier)

    def SetInput(self, value, qualifier):

        ValueStateValues = {
            'DTV'       : b'\x55\x00\x80\x01\xD6',
            'ATV'       : b'\x55\x00\x80\x02\xD7',
            'YPbPr'     : b'\x55\x00\x80\x04\xD9',
            'YPbPr 2'   : b'\x55\x00\x80\x10\xE5',
            'VGA'       : b'\x55\x00\x80\x05\xDA',
            'Front HDMI': b'\x55\x00\x80\x08\xDD',
            'HDMI 1'    : b'\x55\x00\x80\x09\xDE',
            'HDMI 2'    : b'\x55\x00\x80\x11\xE6',
            'OPS'       : b'\x55\x00\x80\x0B\xE0',
            'AV 1'      : b'\x55\x00\x80\x0C\xE1',
            'AV 2'      : b'\x55\x00\x80\x0D\xE2',
            'USB'       : b'\x55\x00\x80\x0F\xE4'
        }

        InputCmdString = ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        ValueStateValues = {
            'Up'   : b'\x55\x00\x00\x01\x56',
            'Down' : b'\x55\x00\x00\x02\x57',
            'Left' : b'\x55\x00\x00\x03\x58',
            'Right': b'\x55\x00\x00\x04\x59',
            'Ok'   : b'\x55\x00\x00\x00\x55',
            'Menu' : b'\x55\x00\x14\x00\x69',
            'Exit' : b'\x55\x00\x16\x00\x6B'
        }

        MenuNavigationCmdString = ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetMute(self, value, qualifier):
        self.__SetHelper('Mute', b'\x55\x00\x1A\x00\x6F', value, qualifier)

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On' : b'\x55\x00\xA0\x01\xF6',
            'Off': b'\x55\x00\xA0\x02\xF7\x55\x00\x00\x04\x59\x55\x00\x00\x04\x59\x55\x00\x00\x00\x55' # BASED ON NOTE
        }

        PowerCmdString = ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetScreenshot(self, value, qualifier):
        self.__SetHelper('Screenshot', b'\x55\x00\x8A\x00\xDF', value, qualifier)

    def SetVolume(self, value, qualifier):

        ValueStateValues = {
            'Up'  : b'\x55\x00\x0C\x00\x61',
            'Down': b'\x55\x00\x0E\x00\x63'
        }

        VolumeCmdString = ValueStateValues[value]
        self.__SetHelper('Volume', VolumeCmdString, value, qualifier)

    def __SetHelper(self, command, commandstring, value, qualifier):        self.Debug = True
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

