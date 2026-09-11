from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'AutoImage': { 'Status': {}},
            'ChannelTV': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Mute': { 'Status': {}},
            'PictureMode': { 'Status': {}},
            'Power': { 'Status': {}},
            'SoundMode': { 'Status': {}},
            'Volume': { 'Status': {}},
        }


        self.Header = b'\x08\x22'


    def GetCommandString(self, value):

        string = self.Header + value
        checksum = sum(string)
        checksum = checksum ^ 0xFFFF
        checksum = checksum + 1
        checksum = checksum & 0xFF
        return string + pack('B', checksum)

    def SetAspectRatio(self, value, qualifier):

        
        ValueStateValues = {
            '16:9'       : b'\x00', 
            'Zoom 1'     : b'\x01', 
            'Zoom 2'     : b'\x02', 
            'Wide Fit'   : b'\x03', 
            '4:3'        : b'\x04', 
            'Screen Fit' : b'\x05'
        }

        AspectRatioCmdString = b'\x0B\x0A\x01' + ValueStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)
    def SetAutoImage(self, value, qualifier):

        
        AutoImageCmdString = b'\x0B\x0B\x00\x00'
        self.__SetHelper('AutoImage', AutoImageCmdString, value, qualifier)
    def SetChannelTV(self, value, qualifier):

        
        ValueStateValues = {
            'Up'   : b'\x01', 
            'Down' : b'\x02'
        }

        ChannelCmdString = ValueStateValues[value].join([b'\x03\x00', b'\x00'])
        self.__SetHelper('ChannelTV', ChannelCmdString, value, qualifier)
    def SetInput(self, value, qualifier):

        
        ValueStateValues = {
            'TV'        : b'\x00\x00', 
            'AV'        : b'\x01\x00', 
            'Component' : b'\x03\x00', 
            'HDMI 1'    : b'\x05\x00', 
            'HDMI 2'    : b'\x05\x01'
        }

        InputCmdString = b'\x0A\x00' + ValueStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)
    def SetMenuNavigation(self, value, qualifier):

        
        ValueStateValues = {
            'Up'    : b'\x60', 
            'Down'  : b'\x61', 
            'Left'  : b'\x65', 
            'Right' : b'\x98', 
            'Menu'  : b'\x1A', 
            'Enter' : b'\x68', 
            'Exit'  : b'\x2D'
        }

        MenuNavigationCmdString = b'\x0D\x00\x00' + ValueStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)
    def SetMute(self, value, qualifier):

        
        MuteCmdString = b'\x02\x00\x00\x00'
        self.__SetHelper('Mute', MuteCmdString, value, qualifier)
    def SetPictureMode(self, value, qualifier):

        
        ValueStateValues = {
            'Dynamic (Entertain)'   : b'\x00', 
            'Standard'  		    : b'\x01', 
            'Movie'     			: b'\x02', 
            'Natural'   			: b'\x03', 
            'CAL-NIGHT' 			: b'\x04', 
            'CAL-DAY'   			: b'\x05', 
            'BD Wise'   			: b'\x06'
        }

        PictureModeCmdString = b'\x0B\x00\x00' + ValueStateValues[value]
        self.__SetHelper('PictureMode', PictureModeCmdString, value, qualifier)
    def SetPower(self, value, qualifier):

        
        ValueStateValues = {
            'On'  : b'\x02', 
            'Off' : b'\x01'
        }

        PowerCmdString = b'\x00\x00\x00' + ValueStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)
    def SetSoundMode(self, value, qualifier):

        
        ValueStateValues = {
            'Standard'    : b'\x00', 
            'Music'       : b'\x01', 
            'Movie'       : b'\x02', 
            'Clear Voice' : b'\x03'
        }

        SoundModeCmdString = b'\x0C\x00\x00' + ValueStateValues[value]
        self.__SetHelper('SoundMode', SoundModeCmdString, value, qualifier)
    def SetVolume(self, value, qualifier):

        
        ValueConstraints = {
            'Min' : 0,
            'Max' : 100
        }

        if ValueConstraints['Min'] <= value <= ValueConstraints['Max']:
            VolumeCmdString = b'\x01\x00\x00' + pack('B', value)
            self.__SetHelper('Volume', VolumeCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetVolume')
            
    def __SetHelper(self, command, commandstring, value, qualifier):
        self.Debug = True
        
        commandstring = self.GetCommandString(commandstring)

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

