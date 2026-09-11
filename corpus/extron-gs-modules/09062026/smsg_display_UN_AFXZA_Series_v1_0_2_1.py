from extronlib.interface import SerialInterface, EthernetClientInterface
import re
from struct import pack

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}


        self.Commands = {
            'AspectRatio': { 'Status': {}},
            'AudioMute': { 'Status': {}},
            'Channel': { 'Status': {}},
            'Input': { 'Status': {}},
            'MenuNavigation': { 'Status': {}},
            'Power': { 'Status': {}},
            'Volume': { 'Status': {}},
            }

    def SetAspectRatio(self, value, qualifier):

        AspectRatioStateValues = {
            '16:9'          : b'\x08\x22\x0B\x0A\x01\x00\xC0',
            'Zoom 1'        : b'\x08\x22\x0B\x0A\x01\x01\xBF',
            'Zoom 2'        : b'\x08\x22\x0B\x0A\x01\x02\xBE',
            'Wide Fit'      : b'\x08\x22\x0B\x0A\x01\x03\xBD',
            '4:3'           : b'\x08\x22\x0B\x0A\x01\x04\xBC',
            'Screen Fit'    : b'\x08\x22\x0B\x0A\x01\x05\xBB',
            'Smart View 1'  : b'\x08\x22\x0B\x0A\x01\x06\xBA',
            'Smart View 2'  : b'\x08\x22\x0B\x0A\x01\x07\xB9',
            }
        AspectRatioCmdString = AspectRatioStateValues[value]
        self.__SetHelper('AspectRatio', AspectRatioCmdString, value, qualifier)

    def SetAudioMute(self, value, qualifier):

        AudioMuteCmdString = b'\x08\x22\x02\x00\x00\x00\xD4'
        self.__SetHelper('AudioMute', AudioMuteCmdString, value, qualifier)

    def SetChannel(self, value, qualifier):

        ChannelStateValues = {
            'Up'          : b'\x08\x22\x03\x00\x01\x00\xD2',
            'Down'        : b'\x08\x22\x03\x00\x02\x00\xD1',
            }
        ChannelCmdString = ChannelStateValues[value]
        self.__SetHelper('Channel', ChannelCmdString, value, qualifier)

    def SetInput(self, value, qualifier):

        InputStateValues = {
            'TV'        : b'\x08\x22\x0A\x00\x00\x00\xCC',
            'AV'        : b'\x08\x22\x0A\x00\x01\x00\xCB',
            'AV 1'      : b'\x08\x22\x0A\x00\x01\x00\xCB',
            'AV 2'      : b'\x08\x22\x0A\x00\x01\x01\xCA',
            'Component' : b'\x08\x22\x0A\x00\x03\x00\xC9',
            'HDMI1'     : b'\x08\x22\x0A\x00\x05\x00\xC7',
            'HDMI2'     : b'\x08\x22\x0A\x00\x05\x01\xC6',
            'HDMI3'     : b'\x08\x22\x0A\x00\x05\x02\xC5',
            'HDMI4'     : b'\x08\x22\x0A\x00\x05\x03\xC4',
            }
        InputCmdString = InputStateValues[value]
        self.__SetHelper('Input', InputCmdString, value, qualifier)

    def SetMenuNavigation(self, value, qualifier):

        MenuNavigationStateValues = {
            'Up'    : b'\x08\x22\x0D\x00\x00\x60\x69',
            'Down'  : b'\x08\x22\x0D\x00\x00\x61\x68',
            'Left'  : b'\x08\x22\x0D\x00\x00\x65\x64',
            'Right' : b'\x08\x22\x0D\x00\x00\x62\x67',
            'Menu'  : b'\x08\x22\x0D\x00\x00\x1A\xAF',
            'Enter' : b'\x08\x22\x0D\x00\x00\x68\x61',
            'Exit'  : b'\x08\x22\x0D\x00\x00\x2D\x9C',
            }
        MenuNavigationCmdString = MenuNavigationStateValues[value]
        self.__SetHelper('MenuNavigation', MenuNavigationCmdString, value, qualifier)

    def SetPower(self, value, qualifier):

        PowerStateValues = {
            'On'  : b'\x08\x22\x00\x00\x00\x02\xD4',
            'Off' : b'\x08\x22\x00\x00\x00\x01\xD5',
            }
        PowerCmdString = PowerStateValues[value]
        self.__SetHelper('Power', PowerCmdString, value, qualifier)

    def SetVolume(self, value, qualifier):

        VolumeConstraints = {
            'Min' : 0,
            'Max' : 100
        }
        if VolumeConstraints['Min'] <= value <= VolumeConstraints['Max']:
            checksum = 213 - value;
            VolumeCmdString = b'\x08\x22\x01\x00\x00' + value.to_bytes(1, byteorder='big') + checksum.to_bytes(1, byteorder='big')
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

