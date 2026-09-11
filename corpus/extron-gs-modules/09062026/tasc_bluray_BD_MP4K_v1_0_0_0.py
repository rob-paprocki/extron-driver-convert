from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DiskTray': { 'Status': {}},
            'Menu': { 'Status': {}},
            'Mute': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Transport': { 'Status': {}},
        }

    def SetDiskTray(self, value, qualifier):

        ValueStateValues = {
            'Open': 'OP',
            'Close': 'CL',
        }

        if value in ValueStateValues:
            DiskTrayCmdString = '!7OPC{}\r'.format(ValueStateValues[value])
            self.__SetHelper('DiskTray', DiskTrayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDiskTray')

    def SetMenu(self, value, qualifier):

        ValueStateValues = {
            'Setup Menu': 'SMN',
            'Top/Disc Menu': 'TMN',
            'Popup Menu': 'PMN',
            'Enter': 'ENT',
            'Return': 'RET',
            'Home': 'HOM',
            'Up': 'OSD3',
            'Down': 'OSD4',
            'Left': 'OSD1',
            'Right': 'OSD2',
            'Option Menu': 'OMN',
        }

        if value in ValueStateValues:
            MenuCmdString = '!7{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Menu', MenuCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenu')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On': '00',
            'Off': '01',
        }

        if value in ValueStateValues:
            MuteCmdString = '!7MUT{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '01',
            'Off': '00',
        }

        if value in ValueStateValues:
            PowerCmdString = '!7PWR{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPowerOff(self, value, qualifier):

        ValueStateValues = {
            'Off': '00',
        }

        if value in ValueStateValues:
            PowerOffCmdString = '!7PWR{}\r'.format(ValueStateValues[value])
            self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPowerOff')

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop': 'STP',
            'Play': 'PLY',
            'Play Pause': 'PAS',
            'Fast Forward': 'SCNFf',
            'Rewind': 'SCNRf',
            'Track Skip Next': 'SKPNX',
            'Track Skip Previous': 'SKPPV',
        }

        if value in ValueStateValues:
            TransportCmdString = '!7{}\r'.format(ValueStateValues[value])
            self.__SetHelper('Transport', TransportCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTransport')

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

    def __init__(self, Host, Port, Baud=57600, Data=8, Parity='None', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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