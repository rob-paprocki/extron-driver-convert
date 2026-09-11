from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'DiscTray': { 'Status': {}},
            'Keypad': { 'Status': {}},
            'MenuControl': { 'Status': {}},
            'Mute': { 'Status': {}},
            'OSD': { 'Status': {}},
            'Power': { 'Status': {}},
            'PowerOff': { 'Status': {}},
            'Scan': {'Parameters': ['Speed'], 'Status': {}},
            'Subtitle': { 'Status': {}},
            'Transport': { 'Status': {}},
        }

    def SetDiscTray(self, value, qualifier):

        ValueStateValues = {
            'Open':  '!7OPCOP\r',
            'Close': '!7OPCCL\r',
        }

        if value in ValueStateValues:
            DiscTrayCmdString = ValueStateValues[value]
            self.__SetHelper('DiscTray', DiscTrayCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetDiscTray')

    def SetKeypad(self, value, qualifier):

        ValueStateValues = {
            '1': '!7NUM1\r',
            '2': '!7NUM2\r',
            '3': '!7NUM3\r',
            '4': '!7NUM4\r',
            '5': '!7NUM5\r',
            '6': '!7NUM6\r',
            '7': '!7NUM7\r',
            '8': '!7NUM8\r',
            '9': '!7NUM9\r',
            '0': '!7NUM0\r',
        }

        if value in ValueStateValues:
            KeypadCmdString = ValueStateValues[value]
            self.__SetHelper('Keypad', KeypadCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetKeypad')

    def SetMenuControl(self, value, qualifier):

        ValueStateValues = {
            'Setup Menu':    '!7SMN\r',
            'Top Menu':      '!7TMN\r',
            'Option Menu':   '!7OMN\r',
            'Pop Up Menu':   '!7PMN\r',
            'Display/Info':  '!7DSP\r',
            'Return':        '!7RET\r',
            'Enter':         '!7ENT\r',
            'Home':          '!7HOM\r',
            'Left':          '!7OSD1\r',
            'Right':         '!7OSD2\r',
            'Up':            '!7OSD3\r',
            'Down':          '!7OSD4\r',
        }

        if value in ValueStateValues:
            MenuControlCmdString = ValueStateValues[value]
            self.__SetHelper('MenuControl', MenuControlCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMenuControl')

    def SetMute(self, value, qualifier):

        ValueStateValues = {
            'On':  '!7MUT00\r',
            'Off': '!7MUT01\r',
        }

        if value in ValueStateValues:
            MuteCmdString = ValueStateValues[value]
            self.__SetHelper('Mute', MuteCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetMute')

    def SetOSD(self, value, qualifier):

        ValueStateValues = {
            'On':  '!7OSD00\r',
            'Off': '!7OSD01\r',
        }

        if value in ValueStateValues:
            OSDCmdString = ValueStateValues[value]
            self.__SetHelper('OSD', OSDCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetOSD')

    def SetPower(self, value, qualifier):

        ValueStateValues = {
            'On': '!7PWR01\r',
            'Off': '!7PWR00\r'
        }

        if value in ValueStateValues:
            PowerCmdString = ValueStateValues[value]
            self.__SetHelper('Power', PowerCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetPower')

    def SetPowerOff(self, value, qualifier):

        PowerOffCmdString = '!7PWR00\r'
        self.__SetHelper('PowerOff', PowerOffCmdString, value, qualifier)

    def SetScan(self, value, qualifier):

        SpeedStates = {
            'Fast': 'f',
            'Slow': 's',
        }

        ValueStateValues = {
            'Forward': 'F',
            'Reverse': 'R',
        }

        if value in ValueStateValues and qualifier['Speed'] in SpeedStates:
            ScanCmdString = '!7SCN{0}{1}\r'.format(ValueStateValues[value], SpeedStates[qualifier['Speed']])
            self.__SetHelper('Scan', ScanCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetScan')

    def SetSubtitle(self, value, qualifier):

        SubtitleCmdString = '!7SBT1\r'
        self.__SetHelper('Subtitle', SubtitleCmdString, value, qualifier)

    def SetTransport(self, value, qualifier):

        ValueStateValues = {
            'Stop':                  '!7STP\r',
            'Play':                  '!7PLY\r',
            'Pause':                 '!7PAS\r',
            'Chapter Jump Next':     '!7SKPNX\r',
            'Chapter Jump Previous': '!7SKPPV\r',
            'Title Jump Next':       '!7GSKNX\r',
            'Title Jump Previous':   '!7GSKPV\r',
        }

        if value in ValueStateValues:
            TransportCmdString = ValueStateValues[value]
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