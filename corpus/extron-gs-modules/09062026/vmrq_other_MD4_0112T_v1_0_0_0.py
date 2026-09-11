from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self._SystemID = 1
        self.Models = {}

        self.Commands = {
            'Clear': { 'Status': {}},
            'TextCommand': {'Parameters':['Color'], 'Status': {}},
        }

    @property
    def SystemID(self):
        return self._SystemID

    @SystemID.setter
    def SystemID(self, value):
        if value == 'Broadcast':
            self._SystemID = '0'
        elif 1 <= int(value) <= 247:
            self._SystemID = int(value)
        else:
            self.Error(['Invalid System ID Parameter.'])

    def SetClear(self, value, qualifier):

        ClearCmdString = '<ID {0}><CLR>\r'.format(self._SystemID)
        self.__SetHelper('Clear', ClearCmdString, value, qualifier)
        
    def SetTextCommand(self, value, qualifier):

        ColorStates = {
            'Red'   : '<RED>',
            'Green' : '<GRN>',
            'Amber' : '<AMB>'
        }

        textString = value
        if qualifier['Color'] in ColorStates and textString:
            TextCommandCmdString = '<ID {0}><CLR>{1}<T>{2}</T>\r'.format(self._SystemID, ColorStates[qualifier['Color']], textString)
            self.__SetHelper('TextCommand', TextCommandCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetTextCommand')

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

    def __init__(self, Host, Port, Baud=38400, Data=8, Parity='Odd', Stop=1, FlowControl='Off', CharDelay=0, Mode='RS232', Model =None):
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