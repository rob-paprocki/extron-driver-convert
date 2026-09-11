from extronlib.interface import SerialInterface, EthernetClientInterface
from extronlib.system import Wait, ProgramLog
import re

class DeviceClass:
    def __init__(self):

        self.Debug = False
        self.Models = {}

        self.Commands = {
            'ChannelLevel': {'Parameters': ['Channel Number'], 'Status': {}},
            'Cue': {'Parameters': ['Action'], 'Status': {}},
            'Go': { 'Status': {}},
            'GroupLevel': {'Parameters': ['Group Number'], 'Status': {}},
        }

    def SetChannelLevel(self, value, qualifier):

        ChannelNo = qualifier['Channel Number']
        if 0 <= ChannelNo <= 16384 and 0 <= value <= 100:
            if ChannelNo == 0:
                ChannelLevelCmdString = 'Channel * At {}\r\n'.format(value)
            else:
                ChannelLevelCmdString = 'Channel {} At {}\r\n'.format(ChannelNo, value)

            self.__SetHelper('ChannelLevel', ChannelLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetChannelLevel')

    def SetCue(self, value, qualifier):

        ActionStates = {
            'Recall': 'Cue',
            'Record': 'Record Cue',
            'Update': 'Update Cue'
        }

        CueAction = qualifier['Action']
        if CueAction in ActionStates and 0 <= value <= 99999:
            CueCmdString = '{} {}\r\n'.format(ActionStates[CueAction], value)
            self.__SetHelper('Cue', CueCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetCue')

    def SetGo(self, value, qualifier):

        GoCmdString = 'Go\r\n'
        self.__SetHelper('Go', GoCmdString, value, qualifier)

    def SetGroupLevel(self, value, qualifier):

        group = qualifier['Group Number']

        if 1 <= group <= 99999 and 0 <= value <= 100:
            GroupLevelCmdString = 'Group {} At {}\r\n'.format(group, value)
            self.__SetHelper('GroupLevel', GroupLevelCmdString, value, qualifier)
        else:
            self.Discard('Invalid Command for SetGroupLevel')

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

class EthernetClass(EthernetClientInterface, DeviceClass):

    def __init__(self, Hostname, IPPort, Protocol='UDP', ServicePort=0, Model=None):
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